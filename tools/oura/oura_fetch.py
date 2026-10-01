#!/usr/bin/env python3
"""Download your own data from the Oura API v2 into local JSON files.

Oura retired Personal Access Tokens in Dec 2025, so this uses OAuth2:

  1. Register an app at https://cloud.ouraring.com/oauth/applications
     Redirect URI: http://localhost:8765/callback
  2. export OURA_CLIENT_ID=... OURA_CLIENT_SECRET=...
  3. python3 oura_fetch.py login          # opens the consent page, saves the token
  4. python3 oura_fetch.py fetch --days 180

If you already have an access token, skip login and set OURA_ACCESS_TOKEN.
Only the standard library is used.
"""
import argparse
import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

API = "https://api.ouraring.com"
AUTHORIZE_URL = "https://cloud.ouraring.com/oauth/authorize"
TOKEN_URL = API + "/oauth/token"
DEFAULT_REDIRECT = "http://localhost:8765/callback"
DEFAULT_SCOPES = "email personal daily heartrate workout tag session spo2"
TOKEN_FILE = Path(os.environ.get("OURA_TOKEN_FILE", Path.home() / ".oura_token.json"))

# Date-ranged collections (start_date / end_date).
DAILY_ENDPOINTS = [
    "daily_sleep", "sleep", "daily_readiness", "daily_activity",
    "daily_stress", "daily_resilience", "daily_spo2",
    "daily_cardiovascular_age", "vO2_max", "workout", "session",
    "sleep_time", "enhanced_tag", "tag", "rest_mode_period",
]
SINGLE_ENDPOINTS = ["personal_info", "ring_configuration"]


# --------------------------------------------------------------------------- auth

def _post_form(url, fields):
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _save_token(tok):
    tok["obtained_at"] = int(time.time())
    TOKEN_FILE.write_text(json.dumps(tok, indent=2))
    os.chmod(TOKEN_FILE, 0o600)


def _client_creds():
    cid, csec = os.environ.get("OURA_CLIENT_ID"), os.environ.get("OURA_CLIENT_SECRET")
    if not cid or not csec:
        sys.exit("Set OURA_CLIENT_ID and OURA_CLIENT_SECRET (from your Oura OAuth app).")
    return cid, csec


def _capture_code(redirect_uri, state):
    """Run a one-shot local server that catches the OAuth redirect."""
    parsed = urllib.parse.urlparse(redirect_uri)
    result = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result.update({k: v[0] for k, v in qs.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Oura authorization received. You can close this tab.".encode())

        def log_message(self, *args):
            pass

    server = HTTPServer((parsed.hostname or "localhost", parsed.port or 80), Handler)
    server.timeout = 300
    server.handle_request()
    if result.get("state") != state:
        sys.exit("OAuth state mismatch; aborting.")
    if "code" not in result:
        sys.exit(f"Authorization failed: {result}")
    return result["code"]


def cmd_login(args):
    cid, csec = _client_creds()
    state = secrets.token_urlsafe(16)
    url = AUTHORIZE_URL + "?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": cid, "redirect_uri": args.redirect_uri,
        "scope": args.scopes, "state": state,
    })
    print("Open this URL and approve access:\n\n  " + url + "\n")
    if args.paste:
        raw = input("After approving, paste the full URL you were redirected to (or just the code): ").strip()
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(raw).query)
        if qs.get("state", [state])[0] != state:
            sys.exit("OAuth state mismatch; aborting.")
        code = qs["code"][0] if "code" in qs else raw
    else:
        webbrowser.open(url)
        print(f"Waiting for the redirect on {args.redirect_uri} ...")
        code = _capture_code(args.redirect_uri, state)
    tok = _post_form(TOKEN_URL, {
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": args.redirect_uri, "client_id": cid, "client_secret": csec,
    })
    _save_token(tok)
    print(f"Token saved to {TOKEN_FILE}")


def _refresh(tok):
    cid, csec = _client_creds()
    new = _post_form(TOKEN_URL, {
        "grant_type": "refresh_token", "refresh_token": tok["refresh_token"],
        "client_id": cid, "client_secret": csec,
    })
    _save_token(new)
    return new


def access_token(force_refresh=False):
    if os.environ.get("OURA_ACCESS_TOKEN") and not force_refresh:
        return os.environ["OURA_ACCESS_TOKEN"]
    if not TOKEN_FILE.exists():
        sys.exit("No token. Run `oura_fetch.py login` or set OURA_ACCESS_TOKEN.")
    tok = json.loads(TOKEN_FILE.read_text())
    expires_at = tok.get("obtained_at", 0) + tok.get("expires_in", 0) - 60
    if (force_refresh or time.time() > expires_at) and tok.get("refresh_token"):
        tok = _refresh(tok)
    return tok["access_token"]


# --------------------------------------------------------------------------- fetch

class NotAvailable(Exception):
    pass


def _get(path, params, token):
    url = f"{API}/v2/usercollection/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = int(e.headers.get("Retry-After", 2 ** attempt * 5))
                print(f"  rate limited, sleeping {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            if e.code == 401:
                raise PermissionError("401")
            if e.code in (400, 403, 404, 426):
                # Missing scope, endpoint not on this account/ring, or app needs update.
                raise NotAvailable(f"HTTP {e.code}: {e.read()[:200]!r}")
            raise
    raise RuntimeError(f"Gave up on {path} after repeated rate limiting")


def fetch_collection(path, params, token):
    items, next_token = [], None
    while True:
        p = dict(params)
        if next_token:
            p["next_token"] = next_token
        page = _get(path, p, token)
        items.extend(page.get("data", []))
        next_token = page.get("next_token")
        if not next_token:
            return items


def cmd_fetch(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    end = date.today() + timedelta(days=1)  # end_date is exclusive for some collections
    start = date.today() - timedelta(days=args.days)
    token = access_token()

    def run(fn):
        nonlocal token
        try:
            return fn(token)
        except PermissionError:
            token = access_token(force_refresh=True)
            return fn(token)

    summary = {}
    for ep in SINGLE_ENDPOINTS:
        try:
            data = run(lambda t: _get(ep, {}, t))
            (out / f"{ep}.json").write_text(json.dumps(data, indent=1))
            summary[ep] = "ok"
        except NotAvailable as e:
            summary[ep] = f"skipped ({e})"

    for ep in DAILY_ENDPOINTS:
        try:
            rows = run(lambda t: fetch_collection(
                ep, {"start_date": start.isoformat(), "end_date": end.isoformat()}, t))
            (out / f"{ep}.json").write_text(json.dumps(rows, indent=1))
            summary[ep] = f"{len(rows)} records"
        except NotAvailable as e:
            summary[ep] = f"skipped ({e})"

    if args.heartrate_days:
        # Heart rate is 5-minute samples; the API caps each request at 30 days.
        rows, hr_end = [], datetime.now(timezone.utc)
        hr_start = hr_end - timedelta(days=args.heartrate_days)
        cursor = hr_start
        try:
            while cursor < hr_end:
                chunk_end = min(cursor + timedelta(days=30), hr_end)
                rows += run(lambda t: fetch_collection("heartrate", {
                    "start_datetime": cursor.isoformat(timespec="seconds"),
                    "end_datetime": chunk_end.isoformat(timespec="seconds")}, t))
                cursor = chunk_end
            (out / "heartrate.json").write_text(json.dumps(rows))
            summary["heartrate"] = f"{len(rows)} samples"
        except NotAvailable as e:
            summary["heartrate"] = f"skipped ({e})"

    (out / "_fetch_meta.json").write_text(json.dumps({
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "start_date": start.isoformat(), "end_date": end.isoformat(), "summary": summary,
    }, indent=2))
    width = max(map(len, summary))
    for k, v in summary.items():
        print(f"  {k:<{width}}  {v}")
    print(f"\nSaved to {out.resolve()}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    lg = sub.add_parser("login", help="OAuth2 sign-in; stores the token in ~/.oura_token.json")
    lg.add_argument("--redirect-uri", default=os.environ.get("OURA_REDIRECT_URI", DEFAULT_REDIRECT))
    lg.add_argument("--scopes", default=os.environ.get("OURA_SCOPES", DEFAULT_SCOPES))
    lg.add_argument("--paste", action="store_true",
                    help="Don't run a local server; paste the redirect URL instead (for remote machines)")
    lg.set_defaults(func=cmd_login)

    ft = sub.add_parser("fetch", help="Download data to JSON files")
    ft.add_argument("--days", type=int, default=180)
    ft.add_argument("--heartrate-days", type=int, default=0,
                    help="Also pull 5-minute heart-rate samples for this many days (large)")
    ft.add_argument("--out", default="oura_data")
    ft.set_defaults(func=cmd_fetch)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
