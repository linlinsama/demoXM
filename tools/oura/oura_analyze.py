#!/usr/bin/env python3
"""Analyze Oura data saved by oura_fetch.py; writes report.md + summary.json.

  python3 oura_analyze.py --data oura_data --out oura_report

Standard library only (Python 3.10+).
"""
import argparse
import json
import statistics as st
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


# --------------------------------------------------------------------------- loading

def load(d, name):
    p = d / f"{name}.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    if isinstance(data, dict):
        return data.get("data", data)
    return data


def clock_minutes(iso, evening=False):
    """Local wall-clock minutes. evening=True maps 00:00-11:59 to 24:00-35:59 so bedtimes are linear."""
    if not iso:
        return None
    t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    m = t.hour * 60 + t.minute
    return m + 1440 if evening and m < 720 else m


def hhmm(m):
    if m is None:
        return "-"
    m = int(round(m)) % 1440
    return f"{m // 60:02d}:{m % 60:02d}"


def shift(day, n):
    return (date.fromisoformat(day) + timedelta(days=n)).isoformat()


def build_days(d):
    days = defaultdict(dict)

    for r in load(d, "daily_sleep"):
        x = days[r["day"]]
        x["sleep_score"] = r.get("score")
        for k, v in (r.get("contributors") or {}).items():
            x[f"sleep_c_{k}"] = v

    main, naps = {}, Counter()
    for r in load(d, "sleep"):
        t, day = r.get("type"), r.get("day")
        dur = r.get("total_sleep_duration") or 0
        if t in ("sleep", "late_nap") and dur < 3 * 3600:
            naps[day] += 1
        if t not in ("long_sleep", "sleep"):
            continue
        cur = main.get(day)
        rank = (t == "long_sleep", dur)
        if cur is None or rank > (cur.get("type") == "long_sleep", cur.get("total_sleep_duration") or 0):
            main[day] = r
    for day, r in main.items():
        tst = r.get("total_sleep_duration") or 0
        if tst < 2 * 3600:
            continue
        x = days[day]
        x.update({
            "tst_h": tst / 3600,
            "tib_h": (r.get("time_in_bed") or 0) / 3600,
            "deep_pct": 100 * (r.get("deep_sleep_duration") or 0) / tst,
            "rem_pct": 100 * (r.get("rem_sleep_duration") or 0) / tst,
            "light_pct": 100 * (r.get("light_sleep_duration") or 0) / tst,
            "deep_min": (r.get("deep_sleep_duration") or 0) / 60,
            "rem_min": (r.get("rem_sleep_duration") or 0) / 60,
            "awake_min": (r.get("awake_time") or 0) / 60,
            "efficiency": r.get("efficiency"),
            "latency_min": (r["latency"] / 60) if r.get("latency") is not None else None,
            "hrv": r.get("average_hrv"),
            "lowest_hr": r.get("lowest_heart_rate"),
            "avg_hr": r.get("average_heart_rate"),
            "breath": r.get("average_breath"),
            "restless": r.get("restless_periods"),
            "bedtime": clock_minutes(r.get("bedtime_start"), evening=True),
            "waketime": clock_minutes(r.get("bedtime_end")),
        })
        if x["bedtime"] is not None and x["waketime"] is not None:
            x["midpoint"] = (x["bedtime"] + x["waketime"] + 1440) / 2
    for day, n in naps.items():
        days[day]["naps"] = n

    for r in load(d, "daily_readiness"):
        x = days[r["day"]]
        x["readiness"] = r.get("score")
        x["temp_dev"] = r.get("temperature_deviation")
        for k, v in (r.get("contributors") or {}).items():
            x[f"ready_c_{k}"] = v

    for r in load(d, "daily_activity"):
        x = days[r["day"]]
        x.update({
            "activity_score": r.get("score"),
            "steps": r.get("steps"),
            "active_cal": r.get("active_calories"),
            "high_act_min": (r.get("high_activity_time") or 0) / 60,
            "med_act_min": (r.get("medium_activity_time") or 0) / 60,
            "sedentary_h": (r.get("sedentary_time") or 0) / 3600,
        })

    for r in load(d, "daily_stress"):
        x = days[r["day"]]
        x["stress_high_min"] = (r.get("stress_high") or 0) / 60
        x["recovery_high_min"] = (r.get("recovery_high") or 0) / 60
        x["stress_summary"] = r.get("day_summary")

    for r in load(d, "daily_resilience"):
        days[r["day"]]["resilience"] = r.get("level")

    for r in load(d, "daily_spo2"):
        x = days[r["day"]]
        x["spo2"] = (r.get("spo2_percentage") or {}).get("average")
        x["bdi"] = r.get("breathing_disturbance_index")

    for r in load(d, "daily_cardiovascular_age"):
        days[r["day"]]["vascular_age"] = r.get("vascular_age")

    for r in load(d, "vO2_max"):
        days[r["day"]]["vo2max"] = r.get("vo2_max")

    for r in load(d, "workout"):
        x = days[r["day"]]
        mins = 0
        if r.get("start_datetime") and r.get("end_datetime"):
            mins = (datetime.fromisoformat(r["end_datetime"]) -
                    datetime.fromisoformat(r["start_datetime"])).total_seconds() / 60
        x["workout_n"] = x.get("workout_n", 0) + 1
        x["workout_min"] = x.get("workout_min", 0) + mins
        x.setdefault("workouts", []).append(r.get("activity"))

    for r in load(d, "enhanced_tag"):
        name = r.get("custom_name") or (r.get("tag_type_code") or "").removeprefix("tag_generic_")
        if name and r.get("start_day"):
            days[r["start_day"]].setdefault("tags", set()).add(name)
    for r in load(d, "tag"):
        for name in r.get("tags") or []:
            days[r["day"]].setdefault("tags", set()).add(name)

    return dict(sorted(days.items()))


# --------------------------------------------------------------------------- stats

def vals(rows, key):
    return [r[key] for r in rows if r.get(key) is not None]


def mean(xs):
    xs = [x for x in xs if x is not None]
    return st.fmean(xs) if xs else None


def sd(xs):
    xs = [x for x in xs if x is not None]
    return st.stdev(xs) if len(xs) > 1 else None


def _ranks(xs):
    order = sorted(range(len(xs)), key=xs.__getitem__)
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2
        i = j + 1
    return ranks


def spearman(pairs, min_n=15):
    pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
    if len(pairs) < min_n:
        return None
    xs, ys = zip(*pairs)
    if len(set(xs)) < 3 or len(set(ys)) < 3:
        return None
    return st.correlation(_ranks(list(xs)), _ranks(list(ys))), len(pairs)


def slope_per_30d(days, key):
    pts = [(date.fromisoformat(k).toordinal(), v[key]) for k, v in days.items() if v.get(key) is not None]
    if len(pts) < 14:
        return None
    xs, ys = zip(*pts)
    return st.linear_regression(xs, ys).slope * 30


def fmt(v, nd=1, unit=""):
    if v is None:
        return "-"
    if isinstance(v, float):
        v = round(v, nd)
        if nd == 0:
            v = int(v)
    return f"{v}{unit}"


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


# --------------------------------------------------------------------------- report

METRICS = [
    # key, label, decimals, unit, higher_is_better
    ("sleep_score", "睡眠分", 0, "", True),
    ("readiness", "准备度分", 0, "", True),
    ("activity_score", "活动分", 0, "", True),
    ("tst_h", "实际睡眠时长", 2, "h", True),
    ("efficiency", "睡眠效率", 0, "%", True),
    ("deep_min", "深睡", 0, "min", True),
    ("rem_min", "REM", 0, "min", True),
    ("latency_min", "入睡耗时", 0, "min", False),
    ("awake_min", "夜间清醒", 0, "min", False),
    ("hrv", "夜间平均HRV", 0, "ms", True),
    ("lowest_hr", "最低心率", 0, "bpm", False),
    ("breath", "呼吸频率", 1, "/min", None),
    ("temp_dev", "体温偏差", 2, "°C", None),
    ("steps", "步数", 0, "", True),
    ("high_act_min", "高强度活动", 0, "min", True),
    ("sedentary_h", "久坐", 1, "h", False),
    ("stress_high_min", "高压力时长", 0, "min", False),
    ("recovery_high_min", "高恢复时长", 0, "min", True),
    ("spo2", "血氧", 1, "%", True),
    ("bdi", "呼吸紊乱指数", 0, "", False),
]


def analyze(days, info):
    keys = list(days)
    if not keys:
        raise SystemExit("No data found. Did oura_fetch.py run successfully?")
    last = date.fromisoformat(keys[-1])
    recent_n = 30 if len(keys) >= 60 else 14
    cut = (last - timedelta(days=recent_n)).isoformat()
    recent = [v for k, v in days.items() if k > cut]
    base = [v for k, v in days.items() if k <= cut]
    S, md = {"range": [keys[0], keys[-1]], "days": len(keys), "recent_window_days": recent_n}, []

    md.append(f"# Oura 数据分析报告\n\n数据范围：{keys[0]} → {keys[-1]}（{len(keys)} 天）")
    if info:
        md.append(f"个人信息：年龄 {info.get('age', '-')}，性别 {info.get('biological_sex', '-')}，"
                  f"身高 {info.get('height', '-')}，体重 {info.get('weight', '-')}")
        S["personal_info"] = {k: info.get(k) for k in ("age", "biological_sex", "height", "weight")}

    # 1. headline averages
    rows, S["averages"] = [], {}
    for key, label, nd, unit, better in METRICS:
        r, b = mean(vals(recent, key)), mean(vals(base, key))
        if r is None and b is None:
            continue
        delta, arrow = None, ""
        if r is not None and b is not None:
            delta = r - b
            if better is not None and b and abs(delta) / abs(b) >= 0.03:
                arrow = "↑好转" if (delta > 0) == better else "↓变差"
        S["averages"][key] = {"recent": r, "baseline": b, "delta": delta}
        rows.append([label, fmt(r, nd, unit), fmt(b, nd, unit), fmt(delta, nd), arrow])
    md.append(f"\n## 1. 最近 {recent_n} 天 vs 之前\n\n" +
              table(["指标", f"近{recent_n}天", "之前", "变化", ""], rows))

    # 2. sleep quantity & regularity
    night = [v for v in days.values() if v.get("tst_h") is not None]
    tst = vals(night, "tst_h")
    reg = {
        "nights": len(night),
        "pct_under_6h": 100 * sum(t < 6 for t in tst) / len(tst) if tst else None,
        "pct_under_7h": 100 * sum(t < 7 for t in tst) / len(tst) if tst else None,
        "bedtime_mean": mean(vals(night, "bedtime")), "bedtime_sd_min": sd(vals(night, "bedtime")),
        "waketime_mean": mean(vals(night, "waketime")), "waketime_sd_min": sd(vals(night, "waketime")),
    }
    # Social jetlag: sleep midpoint on Fri/Sat nights vs Sun–Thu nights (sleep 'day' is the wake-up day).
    free = [v["midpoint"] for k, v in days.items() if v.get("midpoint") and date.fromisoformat(k).weekday() in (5, 6)]
    work = [v["midpoint"] for k, v in days.items() if v.get("midpoint") and date.fromisoformat(k).weekday() not in (5, 6)]
    reg["social_jetlag_min"] = (mean(free) - mean(work)) if free and work else None
    S["regularity"] = reg
    md.append("\n## 2. 睡眠量与规律性\n")
    md.append(f"- 有效夜晚：{reg['nights']}；平均睡眠 {fmt(mean(tst), 2)} h（标准差 {fmt(sd(tst), 2)} h）")
    md.append(f"- 睡眠 < 6h 的夜晚：{fmt(reg['pct_under_6h'], 0)}%；< 7h：{fmt(reg['pct_under_7h'], 0)}%")
    md.append(f"- 平均上床 {hhmm(reg['bedtime_mean'])}（波动 ±{fmt(reg['bedtime_sd_min'], 0)} 分钟）；"
              f"平均起床 {hhmm(reg['waketime_mean'])}（波动 ±{fmt(reg['waketime_sd_min'], 0)} 分钟）")
    md.append(f"- 社交时差（周五/六晚 vs 工作日晚 睡眠中点差）：{fmt(reg['social_jetlag_min'], 0)} 分钟")
    naps = sum(v.get("naps", 0) for v in days.values())
    md.append(f"- 白天小睡次数：{naps}")

    # 3. trends
    S["trend_per_30d"] = {}
    rows = []
    for key, label, nd, unit, _ in METRICS:
        full = slope_per_30d(days, key)
        tail = slope_per_30d({k: v for k, v in days.items() if k > (last - timedelta(days=60)).isoformat()}, key)
        if full is None:
            continue
        S["trend_per_30d"][key] = {"all": full, "last60": tail}
        rows.append([label, fmt(full, nd + 1, unit), fmt(tail, nd + 1, unit)])
    md.append("\n## 3. 趋势（线性回归，每 30 天变化量）\n\n" + table(["指标", "全时段", "近60天"], rows))

    # 4. weekday pattern — keyed by the evening the night started.
    by_wd = defaultdict(list)
    for k, v in days.items():
        ev = days.get(shift(k, -1), {})
        by_wd[date.fromisoformat(k).weekday() - 1].append({**v, "ev_steps": ev.get("steps")})
    rows, S["weekday"] = [], {}
    for wd in (0, 1, 2, 3, 4, 5, -1):
        g = by_wd[wd]
        name = WEEKDAYS[wd % 7] + "晚"
        S["weekday"][name] = {k: mean(vals(g, k)) for k in ("tst_h", "sleep_score", "bedtime", "hrv", "ev_steps")}
        w = S["weekday"][name]
        rows.append([name, len(g), fmt(w["tst_h"], 2), fmt(w["sleep_score"], 0), hhmm(w["bedtime"]),
                     fmt(w["hrv"], 0), fmt(w["ev_steps"], 0)])
    md.append("\n## 4. 一周规律（按入睡那天晚上）\n\n" +
              table(["夜晚", "n", "睡眠h", "睡眠分", "上床", "HRV", "当天步数"], rows))

    # 5. bedtime buckets
    buckets = [("23:00 前", None, 23 * 60), ("23:00–24:00", 23 * 60, 24 * 60),
               ("00:00–01:00", 24 * 60, 25 * 60), ("01:00 后", 25 * 60, None)]
    rows, S["bedtime_buckets"] = [], {}
    for name, lo, hi in buckets:
        g = [v for v in night if v.get("bedtime") is not None and
             (lo is None or v["bedtime"] >= lo) and (hi is None or v["bedtime"] < hi)]
        if not g:
            continue
        stats = {k: mean(vals(g, k)) for k in ("sleep_score", "tst_h", "deep_min", "rem_min", "hrv", "lowest_hr")}
        S["bedtime_buckets"][name] = {"n": len(g), **stats}
        rows.append([name, len(g), fmt(stats["sleep_score"], 0), fmt(stats["tst_h"], 2), fmt(stats["deep_min"], 0),
                     fmt(stats["rem_min"], 0), fmt(stats["hrv"], 0), fmt(stats["lowest_hr"], 0)])
    md.append("\n## 5. 上床时间 vs 睡眠质量\n\n" +
              table(["上床时间", "n", "睡眠分", "睡眠h", "深睡min", "REM min", "HRV", "最低心率"], rows))

    # 6. drivers: Spearman correlations, previous-day behaviour -> that night
    def prev(k, key):
        return days.get(shift(k, -1), {}).get(key)

    drivers = [
        ("上床时间（越晚）", lambda k, v: v.get("bedtime")),
        ("当天步数", lambda k, v: prev(k, "steps")),
        ("当天高强度活动", lambda k, v: prev(k, "high_act_min")),
        ("当天久坐时长", lambda k, v: prev(k, "sedentary_h")),
        ("当天高压力时长", lambda k, v: prev(k, "stress_high_min")),
        ("当天运动时长", lambda k, v: prev(k, "workout_min") or (0 if k in days else None)),
    ]
    outcomes = [("sleep_score", "睡眠分"), ("tst_h", "睡眠时长"), ("deep_min", "深睡"), ("rem_min", "REM"),
                ("latency_min", "入睡耗时"), ("hrv", "HRV"), ("lowest_hr", "最低心率")]
    rows, S["drivers"] = [], {}
    for dname, fn in drivers:
        row, S["drivers"][dname] = [dname], {}
        for okey, oname in outcomes:
            res = spearman([(fn(k, v), v.get(okey)) for k, v in days.items()])
            S["drivers"][dname][okey] = res
            row.append("-" if res is None else f"{res[0]:+.2f}")
        rows.append(row)
    md.append("\n## 6. 影响因素（Spearman 相关，当天行为 → 当晚睡眠）\n\n"
              "|r| ≥ 0.2 值得注意，≥ 0.3 较明显。相关 ≠ 因果。\n\n" +
              table(["因素"] + [o[1] for o in outcomes], rows))

    # 7. tags: nights after a tagged day vs other nights
    tag_days = defaultdict(set)
    for k, v in days.items():
        for t in v.get("tags", ()):
            tag_days[t].add(k)
    rows, S["tags"] = [], {}
    for t, tds in sorted(tag_days.items(), key=lambda x: -len(x[1])):
        if len(tds) < 3:
            continue
        after = [v for k, v in night_items(days) if shift(k, -1) in tds]
        other = [v for k, v in night_items(days) if shift(k, -1) not in tds]
        res = {key: (mean(vals(after, key)), mean(vals(other, key))) for key in ("sleep_score", "hrv", "lowest_hr", "deep_min")}
        S["tags"][t] = {"n": len(tds), **res}
        rows.append([t, len(tds)] + [f"{fmt(a, 0)} vs {fmt(b, 0)}" for a, b in res.values()])
    if rows:
        md.append("\n## 7. 标签对比（标签当晚 vs 其他夜晚）\n\n" +
                  table(["标签", "次数", "睡眠分", "HRV", "最低心率", "深睡min"], rows))

    # 8. workouts
    wk = Counter(w for v in days.values() for w in v.get("workouts", []))
    if wk:
        after = [v for k, v in night_items(days) if prev(k, "workout_n")]
        other = [v for k, v in night_items(days) if not prev(k, "workout_n")]
        S["workouts"] = {"types": dict(wk), "after_workout": {k: mean(vals(after, k)) for k in ("hrv", "lowest_hr", "deep_min", "sleep_score")},
                         "no_workout": {k: mean(vals(other, k)) for k in ("hrv", "lowest_hr", "deep_min", "sleep_score")}}
        md.append("\n## 8. 运动\n\n- 类型：" + "，".join(f"{k}×{n}" for k, n in wk.most_common()))
        a, o = S["workouts"]["after_workout"], S["workouts"]["no_workout"]
        md.append(f"- 运动当晚 vs 非运动当晚：HRV {fmt(a['hrv'], 0)} vs {fmt(o['hrv'], 0)}；最低心率 {fmt(a['lowest_hr'], 0)} vs "
                  f"{fmt(o['lowest_hr'], 0)}；深睡 {fmt(a['deep_min'], 0)} vs {fmt(o['deep_min'], 0)} min；"
                  f"睡眠分 {fmt(a['sleep_score'], 0)} vs {fmt(o['sleep_score'], 0)}")

    # 9. warning flags in the last 90 days: HRV drop, raised resting HR, temperature
    flags = []
    for i, (k, v) in enumerate(days.items()):
        if k <= (last - timedelta(days=90)).isoformat():
            continue
        window = [days[x] for x in keys[max(0, i - 28):i]]
        h_base, hr_base = vals(window, "hrv"), vals(window, "lowest_hr")
        sig = []
        if v.get("hrv") is not None and len(h_base) >= 10 and v["hrv"] < 0.75 * st.median(h_base):
            sig.append(f"HRV {v['hrv']}（基线 {st.median(h_base):.0f}）")
        if v.get("lowest_hr") is not None and len(hr_base) >= 10 and v["lowest_hr"] >= st.median(hr_base) + 4:
            sig.append(f"最低心率 {v['lowest_hr']}（基线 {st.median(hr_base):.0f}）")
        if v.get("temp_dev") is not None and v["temp_dev"] >= 0.5:
            sig.append(f"体温 +{v['temp_dev']:.2f}°C")
        if sig:
            flags.append((k, sig, sorted(v.get("tags", ()))))
    S["flags"] = [{"day": k, "signals": s, "tags": t} for k, s, t in flags]
    md.append("\n## 9. 近 90 天异常夜晚\n")
    md.append("\n".join(f"- {k}：{'；'.join(s)}" + (f"  标签：{', '.join(t)}" if t else "")
                        for k, s, t in flags) or "- 无")

    # 10. best & worst nights
    scored = [(k, v) for k, v in days.items() if v.get("sleep_score") is not None and v.get("tst_h")]
    scored.sort(key=lambda kv: kv[1]["sleep_score"])

    def night_row(k, v):
        p = days.get(shift(k, -1), {})
        return [k, v["sleep_score"], fmt(v.get("tst_h"), 2), hhmm(v.get("bedtime")), fmt(v.get("hrv"), 0),
                fmt(p.get("steps"), 0), fmt(p.get("stress_high_min"), 0), ", ".join(p.get("workouts", [])) or "-",
                ", ".join(sorted(set(p.get("tags", ())) | set(v.get("tags", ())))) or "-"]
    hdr = ["日期", "睡眠分", "睡眠h", "上床", "HRV", "前一天步数", "前一天高压力min", "前一天运动", "标签"]
    md.append("\n## 10. 最好 / 最差的夜晚\n\n**最好 5 晚**\n\n" + table(hdr, [night_row(*kv) for kv in scored[::-1][:5]]))
    md.append("\n**最差 5 晚**\n\n" + table(hdr, [night_row(*kv) for kv in scored[:5]]))

    # 11. long-horizon markers
    md.append("\n## 11. 长期指标\n")
    for key, label in (("vascular_age", "心血管年龄"), ("vo2max", "VO2max")):
        series = [(k, v[key]) for k, v in days.items() if v.get(key) is not None]
        if series:
            S[key] = {"first": series[0], "last": series[-1]}
            md.append(f"- {label}：{series[0][0]} {series[0][1]} → {series[-1][0]} {series[-1][1]}")
    res = Counter(v["resilience"] for v in recent if v.get("resilience"))
    if res:
        S["resilience_recent"] = dict(res)
        md.append(f"- 近{recent_n}天韧性分布：" + "，".join(f"{k} {n}天" for k, n in res.most_common()))

    # 12. last 7 days
    rows = []
    for k in keys[-7:]:
        v = days[k]
        rows.append([k, fmt(v.get("sleep_score"), 0), fmt(v.get("readiness"), 0), fmt(v.get("tst_h"), 2),
                     hhmm(v.get("bedtime")), fmt(v.get("hrv"), 0), fmt(v.get("lowest_hr"), 0),
                     fmt(v.get("temp_dev"), 2), fmt(v.get("steps"), 0)])
    md.append("\n## 12. 最近 7 天\n\n" + table(["日期", "睡眠", "准备度", "睡眠h", "上床", "HRV", "最低心率", "体温", "步数"], rows))

    return "\n".join(md) + "\n", S


def night_items(days):
    return [(k, v) for k, v in days.items() if v.get("tst_h") is not None]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default="oura_data")
    ap.add_argument("--out", default="oura_report")
    args = ap.parse_args()
    data, out = Path(args.data), Path(args.out)
    info = load(data, "personal_info") if (data / "personal_info.json").exists() else None
    days = build_days(data)
    report, summary = analyze(days, info if isinstance(info, dict) else None)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text(report)
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1, default=list))
    (out / "days.json").write_text(json.dumps(days, ensure_ascii=False, default=sorted))
    print(report)
    print(f"Written to {out.resolve()}")


if __name__ == "__main__":
    main()
