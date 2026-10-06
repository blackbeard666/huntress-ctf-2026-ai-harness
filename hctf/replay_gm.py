#!/usr/bin/env python3
"""Replay Game Master: re-run an already-solved day FROM SCRATCH and measure it, without the real GM's help.

The real GM won't judge a solved Single Solve again (submit -> already_solved), but Time Trial / Mastery can be re-run
for real (each start is a fresh variant; the scoreboard keeps the original solve). This local server sits in front of
the real GM (point HUNTRESS_GAME_MASTER_URL at it) and:
  * replayed Single Solves: serves the SAVED start contract + artifact bytes and judges submits against the saved
    GM-confirmed answers with GM semantics (any wrong value -> incorrect; all right -> accepted/remaining, then CORRECT);
  * replayed challenges (all modes): status reports `start_required` until solved in THIS session, so the harness
    doesn't skip them as already solved;
  * everything else (list, Time Trial / Mastery start/artifact/download/submit, ...) is proxied to the real GM with the
    caller's Authorization header. A proxied CORRECT marks that mode solved for this session.
Every judged event is appended to --events (JSONL, wall-clock ts) for timing.

Keep --src outside what workers can read (it holds the answers): workers run sandboxed, add it to HCTF_SANDBOX_HIDE.

  python3 hctf/replay_gm.py --port 18765 --events .run/replay/events.jsonl \\
      --replay warmups-day-06=.run/replay-src/warmups-eight-is-enough/single_solve ...
"""
import argparse
import glob
import hashlib
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = "https://2026.huntress.ctf.games"
CAP_RE = re.compile(r"(?:/download/|[?&]capability=)([0-9a-f]{64})")
STATE = {"single": {}, "solved": set(), "replayed": set(), "events": None, "lock": threading.Lock()}


def load_single(base, src):
    start = json.load(open(os.path.join(src, "start.json")))
    att = start.get("attempt_id")
    conf = json.load(open(os.path.join(src, "confirmed.json")))
    truth = conf.get(att) or max(conf.values(), key=len)
    if set(truth) != set(start.get("answer_ids") or []):
        raise SystemExit(f"{base}: confirmed answers don't cover every answer_id ({len(truth)}/{len(start.get('answer_ids') or [])})")
    files = {}
    manifest = sorted(glob.glob(os.path.join(src, "artifacts", "2*", "manifest.json")))[-1]
    for f in json.load(open(manifest))["files"]:
        path = os.path.join(os.path.dirname(manifest), f["name"])
        files[f["sha256"]] = (f["name"], path)
    caps = {}
    for cap in CAP_RE.findall(json.dumps(start)):
        sha = start.get("sha256")  # single-file contracts carry one sha256
        caps[cap] = files.get(sha) or next(iter(files.values()))
    STATE["single"][base] = {"start": start, "truth": truth, "caps": caps, "conf": {}}
    STATE["replayed"].update({base, f"{base}/time_trial", f"{base}/mastery"})


def event(**kw):
    kw["ts"] = time.time()
    with STATE["lock"], open(STATE["events"], "a") as f:
        f.write(json.dumps(kw) + "\n")


def judge(base, answers):
    s = STATE["single"][base]
    if base in STATE["solved"]:
        return {"result": "already_solved", "name": s["start"].get("name")}
    wrong = [a for a, v in answers.items() if s["truth"].get(a) != str(v)]
    if wrong:
        event(challenge=base, op="submit", result="incorrect", n=len(answers), wrong=len(wrong))
        return {"result": "incorrect", "name": s["start"].get("name")}
    s["conf"].update({a: str(v) for a, v in answers.items()})
    remaining = len(s["truth"]) - len(s["conf"])
    if remaining:
        event(challenge=base, op="submit", result="accepted", n=len(answers), remaining=remaining)
        return {"result": "accepted", "remaining": remaining, "accepted_ids": sorted(answers), "name": s["start"].get("name")}
    STATE["solved"].add(base)
    event(challenge=base, op="submit", result="CORRECT", n=len(answers))
    return {"result": "CORRECT", "flag": hashlib.md5(f"replay-{base}".encode()).hexdigest(), "name": s["start"].get("name")}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json", extra=None):
        raw = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(raw)

    def _proxy(self, method, query, payload):
        url = UPSTREAM + ("?" + query if query else "")
        headers = {k: v for k, v in self.headers.items() if k.lower() in ("authorization", "content-type")}
        req = urllib.request.Request(url, data=payload, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers or {}), e.read()

    def _relay(self, status, headers, raw):
        extra = {k: v for k, v in headers.items() if k.lower() in ("content-disposition", "retry-after")}
        self._send(status, raw, headers.get("Content-Type") or headers.get("content-type") or "application/json", extra)

    def do_GET(self):
        q = urllib.parse.urlparse(self.path).query
        p = dict(urllib.parse.parse_qsl(q))
        op, cid = p.get("op"), p.get("challenge")
        if op == "download":
            for s in STATE["single"].values():
                if p.get("capability") in s["caps"]:
                    name, path = s["caps"][p["capability"]]
                    return self._send(200, open(path, "rb").read(), "application/octet-stream",
                                      {"Content-Disposition": f'attachment; filename="{name}"'})
        if op == "status" and cid in STATE["single"] and cid not in STATE["solved"]:
            st = {k: v for k, v in STATE["single"][cid]["start"].items() if k not in ("attempt_id", "download", "deadline")}
            return self._send(409, {"error": "start_required", **st})
        if op == "status" and cid in STATE["single"]:
            return self._send(200, {"result": "CORRECT", **STATE["single"][cid]["start"]})
        status, headers, raw = self._proxy("GET", q, None)
        if op == "status" and cid in STATE["replayed"] and cid not in STATE["solved"]:
            try:
                body = json.loads(raw)
                if str(body.get("result", "")).upper() == "CORRECT":  # solved before this replay: hide it
                    body = {k: v for k, v in body.items() if k not in ("result", "flag")}
                    return self._send(409, {"error": "start_required", **body})
            except ValueError:
                pass
        self._relay(status, headers, raw)

    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        try:
            body = json.loads(raw or b"{}")
        except ValueError:
            body = {}
        op, cid = body.get("op"), body.get("challenge")
        if cid in STATE["single"]:
            if op in ("start", "retry"):
                event(challenge=cid, op="start")
                return self._send(200, STATE["single"][cid]["start"])
            if op == "submit":
                return self._send(200, judge(cid, body.get("answers") or {}))
        q = urllib.parse.urlparse(self.path).query
        status, headers, out = self._proxy("POST", q, raw)
        if cid in STATE["replayed"] and op in ("start", "submit"):
            try:
                res = json.loads(out)
            except ValueError:
                res = {}
            event(challenge=cid, op=op, http=status, result=res.get("result") or res.get("error"))
            if op == "submit" and str(res.get("result", "")).upper() == "CORRECT":
                STATE["solved"].add(cid)
        self._relay(status, headers, out)


def main():
    global UPSTREAM
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=18765)
    ap.add_argument("--events", required=True)
    ap.add_argument("--upstream", default=UPSTREAM)
    ap.add_argument("--replay", action="append", default=[], help="<single_solve id>=<saved single_solve dir>")
    a = ap.parse_args()
    UPSTREAM = a.upstream
    STATE["events"] = a.events
    os.makedirs(os.path.dirname(os.path.abspath(a.events)), exist_ok=True)
    for spec in a.replay:
        base, src = spec.split("=", 1)
        load_single(base, src)
    print(f"replay GM on 127.0.0.1:{a.port} -> {UPSTREAM}; replaying {sorted(STATE['single'])}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()


if __name__ == "__main__":
    main()
