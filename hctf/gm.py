#!/usr/bin/env python3
"""Minimal Game Master client. Standard library only, so it runs unchanged on Homebase,
the only place the GM is reachable (the VPN can't reach it, and sshd forbids tunnels).

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
import urllib.error
import urllib.parse
import urllib.request

# Exact URL: the proxy 404s if a trailing slash is added before the query string.
GM = os.environ.get("HUNTRESS_GAME_MASTER_URL", "http://10.0.0.219/huntress-ctf-proxy")
TIMEOUT = 60


def _request(method, params=None, payload=None):
    url = GM + ("?" + urllib.parse.urlencode(params) if params else "")
    data = headers = None
    if payload is not None:
        data = json.dumps(payload).encode()
        headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read()
    except (urllib.error.URLError, OSError) as e:
        return 0, {}, json.dumps({"error": "unreachable", "detail": str(e)}).encode()


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
    json.dump(env, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if env["http"] else 5


if __name__ == "__main__":
    sys.exit(main())
