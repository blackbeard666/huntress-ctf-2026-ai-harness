#!/usr/bin/env python3
"""Minimal Game Master client. Standard library only, so it runs unchanged anywhere
(locally via the pairing token, or on Homebase against the inside proxy).

Default transport is the public GM at https://2026.huntress.ctf.games with a per-identity
pairing token (Authorization: Bearer ...). Set HUNTRESS_GAME_MASTER_URL to the inside proxy
(http://10.0.0.219/huntress-ctf-proxy) to talk to the GM from inside the CTF network instead;
there, identity comes from the network path and no token is needed.

Every command prints exactly one JSON envelope on stdout:
  {"http": <status or 0>, "body": <parsed JSON or null>, "text": <raw text if not JSON>,
   "saved": [{"path", "bytes", "sha256"}]}

Usage:
  gm.py openapi
  gm.py list [--day N] [--lane L] [--all] [--search S]
  gm.py status ID
  gm.py start ID
  gm.py retry ID
  gm.py submit ID ANSWERS_JSON
  gm.py artifact ID OUTDIR [--delivery N]
  gm.py download CAPABILITY OUTDIR
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Public GM (pairing-token) by default; override with the inside proxy URL when running in-network.
# Note: the inside proxy 404s if a trailing slash is added before the query string, so never append one.
GM = os.environ.get("HUNTRESS_GAME_MASTER_URL", "https://2026.huntress.ctf.games")
TIMEOUT = int(os.environ.get("HCTF_GM_TIMEOUT", "30"))          # start/submit (POST)
GET_TIMEOUT = int(os.environ.get("HCTF_GM_GET_TIMEOUT", "15"))  # status/list/artifact/download (idempotent, retried once)


def _token():
    """Pairing token for the public GM: env first, then the project-local secret.
    Returns None inside the CTF network (the inside proxy authenticates by network path)."""
    tok = os.environ.get("HUNTRESS_GM_TOKEN")
    if tok:
        return tok.strip()
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "secrets", "gm_pairing_token")
    try:
        with open(path) as f:
            return f.read().strip() or None
    except OSError:
        return None


def _refusal(raw):
    """A 429/503 whose JSON body names a non-rate-limit error is a deterministic GM verdict (Day 8: 503
    training_rotation_invalid), not load: backing off 2/4/8/16 s on it only delays the caller (~40 s per local start)."""
    if b"rate_limited" in (raw or b""):
        return False
    try:
        return bool(json.loads(raw).get("error"))
    except (ValueError, AttributeError):
        return False


def _request(method, params=None, payload=None):
    url = GM + ("?" + urllib.parse.urlencode(params) if params else "")
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    tok = _token()
    if tok:
        headers["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    # Short read timeout + one retry for idempotent GETs: a hung call once stalled a worker 65.7 s (60 s timeout).
    # POSTs (start/submit) get a longer timeout and no blind retry -- the GM may have processed them.
    timeout, net_retries = (GET_TIMEOUT, 1) if method == "GET" else (TIMEOUT, 0)
    for attempt in range(RATE_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            raw = e.read()
            if e.code in (429, 503) and attempt < RATE_RETRIES and not _refusal(raw):
                wait = _retry_after(e.headers, attempt)
                # rate-limited: back off, don't fail the caller -- but SAY so (Day 7: 9.5-18 s single submits with no
                # trace of why; the envelope's retries/slept + this line make 429 backoff visible in log.jsonl)
                STATS["retries"] += 1
                STATS["slept"] += wait
                print(f"gm.py: HTTP {e.code} on {method} {(params or payload or {}).get('op', '')}; retry "
                      f"{attempt + 1}/{RATE_RETRIES} in {wait:g}s", file=sys.stderr)
                time.sleep(wait)
                continue
            return e.code, dict(e.headers or {}), raw
        except (urllib.error.URLError, OSError) as e:
            if net_retries > 0:
                net_retries -= 1
                continue
            return 0, {}, json.dumps({"error": "unreachable", "detail": str(e)}).encode()


RATE_RETRIES = int(os.environ.get("HCTF_GM_RATE_RETRIES", os.environ.get("HCTF_RATE_RETRIES", "4")))
STATS = {"retries": 0, "slept": 0.0}  # this process's 429/503 backoff, reported in every envelope


def _retry_after(headers, attempt):
    """Seconds to wait after a 429/503: the server's Retry-After if given, else 2, 4, 8, 16s."""
    try:
        return min(30.0, float((headers or {}).get("Retry-After")))
    except (TypeError, ValueError):
        return 2.0 * (2 ** attempt)


def _envelope(status, headers, raw, saved=None):
    out = {"http": status, "body": None, "text": None, "saved": saved or []}
    ctype = (headers.get("Content-Type") or headers.get("content-type") or "").lower()
    if not saved:
        try:
            out["body"] = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            out["text"] = raw[:4000].decode("utf-8", "replace")
    out["content_type"] = ctype
    return out


def _filename(headers, fallback):
    cd = headers.get("Content-Disposition") or headers.get("content-disposition") or ""
    m = re.search(r"filename\*?=(?:UTF-8'')?\"?([^\";]+)", cd)
    name = urllib.parse.unquote(m.group(1)) if m else fallback
    return os.path.basename(name) or fallback


def _save_bytes(outdir, name, raw):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    with open(path, "wb") as f:
        f.write(raw)
    return {"path": path, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def _is_json(headers, raw):
    ctype = (headers.get("Content-Type") or headers.get("content-type") or "").lower()
    if "json" not in ctype:
        return False
    try:
        json.loads(raw.decode("utf-8"))
        return True
    except (UnicodeDecodeError, ValueError):
        return False


def cmd_artifact(cid, outdir, delivery=None):
    params = {"op": "artifact", "challenge": cid}
    if delivery is not None:
        params["delivery"] = delivery
    status, headers, raw = _request("GET", params)
    if status != 200 or _is_json(headers, raw):
        # JSON means metadata (download capabilities, errors), not file bytes: follow capability links.
        env = _envelope(status, headers, raw)
        caps = set(re.findall(r"\b[0-9a-f]{64}\b", json.dumps(env["body"]))) if env["body"] else set()
        for cap in sorted(caps):
            env["saved"] += cmd_download(cap, outdir)["saved"]
        return env
    saved = [_save_bytes(outdir, _filename(headers, "artifact.bin"), raw)]
    return _envelope(status, headers, raw, saved)


def cmd_download(cap, outdir, name=None):
    status, headers, raw = _request("GET", {"op": "download", "capability": cap})
    if status != 200 or _is_json(headers, raw):
        return _envelope(status, headers, raw)
    fname = name or _filename(headers, cap[:16] + ".bin")
    return _envelope(status, headers, raw, [_save_bytes(outdir, fname, raw)])


def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("openapi")
    pl = sub.add_parser("list")
    pl.add_argument("--day")
    pl.add_argument("--lane")
    pl.add_argument("--all", action="store_true")
    pl.add_argument("--search")
    for name in ("status", "start", "retry"):
        sub.add_parser(name).add_argument("id")
    ps = sub.add_parser("submit")
    ps.add_argument("id")
    ps.add_argument("answers")
    pa = sub.add_parser("artifact")
    pa.add_argument("id")
    pa.add_argument("outdir")
    pa.add_argument("--delivery", type=int)
    pd = sub.add_parser("download")
    pd.add_argument("capability")
    pd.add_argument("outdir")
    pd.add_argument("--name")
    a = p.parse_args(argv)
    t0 = time.time()

    if a.cmd == "openapi":
        env = _envelope(*_request("GET", {"op": "openapi"}))
    elif a.cmd == "list":
        params = {"op": "list"}
        if a.day is not None:
            params["day"] = a.day
        if a.lane:
            params["lane"] = a.lane
        if a.all:
            params["all"] = "true"
        if a.search:
            params["search"] = a.search
        env = _envelope(*_request("GET", params))
    elif a.cmd == "status":
        env = _envelope(*_request("GET", {"op": "status", "challenge": a.id}))
    elif a.cmd in ("start", "retry"):
        env = _envelope(*_request("POST", payload={"op": a.cmd, "challenge": a.id}))
    elif a.cmd == "submit":
        answers = json.loads(a.answers)
        env = _envelope(*_request("POST", payload={"op": "submit", "challenge": a.id, "answers": answers}))
    elif a.cmd == "artifact":
        env = cmd_artifact(a.id, a.outdir, a.delivery)
    else:
        env = cmd_download(a.capability, a.outdir, a.name)
    env["elapsed"] = round(time.time() - t0, 3)          # request time incl. any 429 backoff (not process startup)
    env["retries"], env["slept"] = STATS["retries"], round(STATS["slept"], 2)
    json.dump(env, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if env["http"] else 5


if __name__ == "__main__":
    sys.exit(main())
