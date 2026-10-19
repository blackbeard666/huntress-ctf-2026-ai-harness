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
  gm.py arena start|stop|status|retry ID [--run-for-time]   (the browser arena's /arena/api: web live targets)
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


# Keep-alive HTTP(S) connections, used when gm.py runs IN-PROCESS (hctf: remote._gm_local -> run()): no interpreter
# start + no TLS handshake per call (D9: every orchestrator GM call was a fresh `python3 gm.py` + TLS to the public GM).
# A one-shot CLI process keeps urllib. GETs that hit a dropped kept-alive socket are resent once on a fresh one; a POST
# only ever goes out on a socket used within POOL_IDLE_MAX s or a fresh one, and is never resent.
POOL = os.environ.get("HCTF_GM_KEEPALIVE", "0") == "1"
POOL_IDLE_MAX = float(os.environ.get("HCTF_GM_POOL_IDLE_MAX", "3"))
_POOL_Q = __import__("queue").LifoQueue()


GZIP = os.environ.get("HCTF_GM_GZIP", "1") != "0"


def _gz(headers, params):
    """Ask for gzip on API replies (2026-10-17: the GM honors it -- script Mastery status 3.3 MB -> 117 KB on the wire,
    10.6 s -> 5.6 s from WSL); never on artifact bytes (download/artifact: saved as-is, sha-checked)."""
    if GZIP and str((params or {}).get("op", "")) not in ("download", "artifact"):
        return {**(headers or {}), "Accept-Encoding": "gzip"}
    return headers or {}


def _gunzip(raw, enc):
    if raw and str(enc or "").lower() == "gzip":
        import gzip
        try:
            return gzip.decompress(raw)
        except (OSError, EOFError):
            return raw
    return raw


def _conn(fresh=False):
    import http.client
    import queue
    u = urllib.parse.urlsplit(GM)
    while not fresh and not _POOL_Q.empty():
        try:
            c = _POOL_Q.get_nowait()
        except queue.Empty:
            break
        if time.time() - c._hctf_used <= POOL_IDLE_MAX:
            return c, True
        c.close()
    cls = http.client.HTTPSConnection if u.scheme == "https" else http.client.HTTPConnection
    c = cls(u.hostname, u.port, timeout=TIMEOUT)
    c._hctf_used = time.time()
    return c, False


def _pooled(method, params, data, headers, timeout):
    """-> (status, headers dict, body) over a kept-alive connection; raises OSError/HTTPException on transport failure."""
    import http.client
    path = (urllib.parse.urlsplit(GM).path or "/") + ("?" + urllib.parse.urlencode(params) if params else "")
    for attempt in range(2 if method == "GET" else 1):
        c, reused = _conn(fresh=attempt > 0)
        c.timeout = timeout
        if c.sock is not None:
            c.sock.settimeout(timeout)
        try:
            c.request(method, path, body=data, headers=_gz(headers, params))
            r = c.getresponse()
            raw = _gunzip(r.read(), r.getheader("Content-Encoding"))
        except (http.client.HTTPException, OSError):
            c.close()
            if method == "GET" and reused and attempt == 0:
                continue          # stale kept-alive socket: one resend of an idempotent GET on a fresh socket
            raise
        c._hctf_used = time.time()
        if r.getheader("Connection", "").lower() != "close":
            _POOL_Q.put(c)
        else:
            c.close()
        return r.status, dict(r.getheaders()), raw


def warm_pool(n=4):
    """Open + TLS-handshake n kept-alive connections now (before a clock / a drop)."""
    if not POOL:
        return 0
    from concurrent.futures import ThreadPoolExecutor
    def one(_):
        c, _r = _conn(fresh=True)
        try:
            c.connect()
            c._hctf_used = time.time()
            _POOL_Q.put(c)
            return 1
        except OSError:
            return 0
    with ThreadPoolExecutor(max_workers=n) as ex:
        return sum(ex.map(one, range(n)))


def _request(method, params=None, payload=None):
    if POOL:
        return _request_pooled(method, params, payload)
    url = GM + ("?" + urllib.parse.urlencode(params) if params else "")
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    tok = _token()
    if tok:
        headers["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(url, data=data, method=method, headers=_gz(headers, params))
    # Short read timeout + one retry for idempotent GETs: a hung call once stalled a worker 65.7 s (60 s timeout).
    # POSTs (start/submit) get a longer timeout and no blind retry -- the GM may have processed them.
    timeout, net_retries = (GET_TIMEOUT, 1) if method == "GET" else (TIMEOUT, 0)
    for attempt in range(RATE_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, dict(r.headers), _gunzip(r.read(), r.headers.get("Content-Encoding"))
        except urllib.error.HTTPError as e:
            raw = _gunzip(e.read(), (e.headers or {}).get("Content-Encoding"))
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


def _request_pooled(method, params=None, payload=None):
    """_request over the keep-alive pool, with the same 429/503 backoff and network-retry rules."""
    data, headers = None, {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    tok = _token()
    if tok:
        headers["Authorization"] = "Bearer " + tok
    timeout, net_retries = (GET_TIMEOUT, 1) if method == "GET" else (TIMEOUT, 0)
    for attempt in range(RATE_RETRIES + 1):
        try:
            status, hdrs, raw = _pooled(method, params, data, headers, timeout)
        except OSError as e:
            if net_retries > 0:
                net_retries -= 1
                continue
            return 0, {}, json.dumps({"error": "unreachable", "detail": str(e)}).encode()
        except Exception as e:  # noqa: BLE001 - http.client.HTTPException etc.
            if net_retries > 0:
                net_retries -= 1
                continue
            return 0, {}, json.dumps({"error": "unreachable", "detail": repr(e)}).encode()
        if status in (429, 503) and attempt < RATE_RETRIES and not _refusal(raw):
            wait = _retry_after(hdrs, attempt)
            STATS["retries"] += 1
            STATS["slept"] += wait
            print(f"gm.py: HTTP {status} on {method} {(params or payload or {}).get('op', '')}; retry "
                  f"{attempt + 1}/{RATE_RETRIES} in {wait:g}s", file=sys.stderr)
            time.sleep(wait)
            continue
        return status, hdrs, raw


RATE_RETRIES = int(os.environ.get("HCTF_GM_RATE_RETRIES", os.environ.get("HCTF_RATE_RETRIES", "8")))


class _Stats(__import__("threading").local):
    """This call's 429/503 backoff, reported in its envelope (per thread: run() is called in-process by many chains)."""
    def __init__(self):
        super().__init__()
        self.d = {"retries": 0, "slept": 0.0}

    def __getitem__(self, k):
        return self.d[k]

    def __setitem__(self, k, v):
        self.d[k] = v

    def update(self, *a, **kw):
        self.d.update(*a, **kw)

    def get(self, k, default=None):
        return self.d.get(k, default)


STATS = _Stats()


# Without Retry-After the backoff is 2, 4, 4, 4 ... s (cap HCTF_GM_BACKOFF_CAP): Day 8 singles slept 2/4/8/16 s and the
# limit had cleared mid-wait (warmups: cleared between 15 and 32 s, slept 30). More, shorter retries keep ~30 s total.
BACKOFF_CAP = float(os.environ.get("HCTF_GM_BACKOFF_CAP", "4"))


def _retry_after(headers, attempt):
    """Seconds to wait after a 429/503: the server's Retry-After if given, else 2, 4, 4, ... s (capped)."""
    try:
        return min(30.0, float((headers or {}).get("Retry-After")))
    except (TypeError, ValueError):
        return min(BACKOFF_CAP, 2.0 * (2 ** attempt))


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


# The browser arena's endpoint (GET /arena serves the page): same bearer, JSON {op, challenge[, run_for_time]}. Web live
# targets only (2026-10-19): its `start` revived a `cleaned` web attempt (the public API's start/retry kept handing back
# the dead attempt) and it has `stop` ("Stopping containers") that the public OpenAPI lacks. Always the PUBLIC origin
# (the inside proxy serves the API only) unless HCTF_ARENA_URL says otherwise (tests / a replay stand-in).
ARENA_PATH = "/arena/api"
ARENA_UA = "Mozilla/5.0 (X11; Linux x86_64) hctf-arena"


def arena_url():
    if os.environ.get("HCTF_ARENA_URL"):
        return os.environ["HCTF_ARENA_URL"]
    base = GM if any(h in GM for h in ("127.0.0.1", "localhost")) else "https://2026.huntress.ctf.games"
    return base.rstrip("/") + ARENA_PATH


def cmd_arena(op, cid, run_for_time=None, token=None, timeout=None):
    """POST {op, challenge} to the arena endpoint -> the usual envelope (the token never enters it)."""
    payload = {"op": op, "challenge": cid}
    if run_for_time is not None:
        payload["run_for_time"] = bool(run_for_time)
    headers = {"Content-Type": "application/json", "User-Agent": ARENA_UA}
    tok = token or _token()
    if tok:
        headers["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(arena_url(), data=json.dumps(payload).encode(), method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout or TIMEOUT) as r:
            return _envelope(r.status, dict(r.headers), r.read())
    except urllib.error.HTTPError as e:
        return _envelope(e.code, dict(e.headers or {}), e.read())
    except (urllib.error.URLError, OSError) as e:
        return _envelope(0, {}, json.dumps({"error": "unreachable", "detail": str(e)}).encode())


def main(argv=None):
    p = _parser()
    a = p.parse_args(argv)
    env = _dispatch(a)
    json.dump(env, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if env["http"] else 5


def _parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("openapi")
    pl = sub.add_parser("list")
    pl.add_argument("--day")
    pl.add_argument("--lane")
    pl.add_argument("--all", action="store_true")
    pl.add_argument("--search")
    for name in ("status", "start", "retry", "practice"):
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
    par = sub.add_parser("arena")
    par.add_argument("op", choices=["start", "stop", "status", "retry"])
    par.add_argument("id")
    par.add_argument("--run-for-time", action="store_true")
    return p


def run(argv):
    """In-process entry (hctf remote._gm_local): the same envelope main() prints, returned instead."""
    return _dispatch(_parser().parse_args([str(x) for x in argv]))


def _dispatch(a):
    STATS["retries"], STATS["slept"] = 0, 0.0
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
    elif a.cmd in ("start", "retry", "practice"):   # practice: legacy-route untimed continuation after exhaustion
        env = _envelope(*_request("POST", payload={"op": a.cmd, "challenge": a.id}))
    elif a.cmd == "submit":
        answers = json.loads(a.answers)
        env = _envelope(*_request("POST", payload={"op": "submit", "challenge": a.id, "answers": answers}))
    elif a.cmd == "artifact":
        env = cmd_artifact(a.id, a.outdir, a.delivery)
    elif a.cmd == "arena":
        env = cmd_arena(a.op, a.id, run_for_time=True if a.run_for_time else (False if a.op in ("start", "retry") else None))
    else:
        env = cmd_download(a.capability, a.outdir, a.name)
    env["elapsed"] = round(time.time() - t0, 3)          # request time incl. any 429 backoff (not process startup)
    env["retries"], env["slept"] = STATS["retries"], round(STATS["slept"], 2)
    return env


if __name__ == "__main__":
    sys.exit(main())
