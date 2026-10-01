# Oura 数据拉取与分析

只用 Python 标准库（3.10+），无需安装依赖。

## 1. 授权（一次性）

Oura 已于 2025 年 12 月停用 Personal Access Token，现在只能用 OAuth2。

1. 打开 https://cloud.ouraring.com/oauth/applications ，新建一个应用
   - Redirect URI 填：`http://localhost:8765/callback`
2. 记下 Client ID 和 Client Secret，然后：

```bash
export OURA_CLIENT_ID=xxx
export OURA_CLIENT_SECRET=xxx
python3 oura_fetch.py login          # 自动打开浏览器授权，token 存到 ~/.oura_token.json
# 在远程机器上用：python3 oura_fetch.py login --paste（把跳转后的完整 URL 粘回来）
```

token 过期后会用 refresh_token 自动续期。

## 2. 拉数据

```bash
python3 oura_fetch.py fetch --days 180            # 睡眠/准备度/活动/压力/血氧/运动/标签等
python3 oura_fetch.py fetch --days 180 --heartrate-days 30   # 另外拉 5 分钟粒度心率（数据量大）
```

数据保存在 `oura_data/`（已被 .gitignore 排除，不会提交）。

## 3. 分析

```bash
python3 oura_analyze.py --data oura_data --out oura_report
```

生成 `oura_report/report.md`（可读报告）和 `summary.json`（结构化数字），内容包括：

- 近 30 天 vs 之前的各项均值对比
- 睡眠时长分布、上床/起床时间波动、社交时差
- 各指标趋势（每 30 天变化）
- 一周规律、上床时间分段对比
- 当天行为（步数、久坐、压力、运动）与当晚睡眠/HRV 的相关性
- 标签（如饮酒、咖啡因）当晚对比
- 近 90 天 HRV 骤降、静息心率升高、体温偏高的异常夜晚
- 最好/最差的夜晚及其前一天的情况
