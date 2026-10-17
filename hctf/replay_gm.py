#!/usr/bin/env python3
"""Replay Game Master: re-run an already-solved day FROM SCRATCH and measure it, without the real GM's help -- and a
FAULT-INJECTING stand-in for the timed runner (tests/test_fault_replay.py, preflight).

The real GM won't judge a solved Single Solve again (submit -> already_solved), but Time Trial / Mastery can be re-run
for real (each start is a fresh variant; the scoreboard keeps the original solve). This local server sits in front of
the real GM (point HUNTRESS_GAME_MASTER_URL at it) and:
  * replayed Single Solves (--replay): serves the SAVED start contract + artifact bytes and judges submits against the
    saved GM-confirmed answers with GM semantics (any wrong value -> incorrect; all right -> accepted/remaining, then
    CORRECT);
  * replayed challenges (all modes): status reports `start_required` until solved in THIS session, so the harness
    doesn't skip them as already solved;
  * LOCAL timed modes (--timed <cid>=<case dir>[,<case dir>...]): start/retry/status/submit/download served from saved
    regression cases (contract.json + expected.json + the artifact file(s)) with the REAL GM's untimed regular-pool
    semantics -- start reconnects to the live attempt, retry advances to the next case (a fresh variant) until the pool
    (--pool N) is spent (retry_variants_unavailable), a submit with any wrong value is `incorrect` and banks nothing,
    an all-right subset is `accepted` with accepted_ids + remaining, remaining 0 is CORRECT, a start after the pass
    hands back the FINISHED CORRECT body (no answer_ids), Mastery needs the Time Trial passed in this session
    (409 prerequisite_required; --no-prereq disables). Nothing reaches the real GM for these ids.
  * everything else is proxied to the real GM with the caller's Authorization header. A proxied CORRECT marks that
    mode solved for this session.
Faults (the harness failures of D8/D14/D15/D16/alt-D16, replayable offline before every drop):
  --fault-429 RATE        this fraction of submits -> 429 rate_limited, unjudged (never counts as incorrect)
  --fault-cut N           every Nth submit reply is cut off mid-body (client sees http.client.IncompleteRead) AFTER
                          the GM judged it (D15 script Mastery)
  --fault-latency S       every submit reply waits S seconds (a slow GM: D16 bisect, 5 s probes under load)
  --fault-start-503 N     the first N timed starts/retries -> 503 training_rotation_invalid (D8 regular pool)
  --fault-prereq-flap N   the first N Mastery starts -> 409 prerequisite_required although the TT passed (rehearsal D16)
  --fault-dl-stall S      the first download of every attempt waits S seconds (a stalled delivery)
  --pool N                fresh variants per timed mode (D14 warmups: 1 -> the untimed fallback)
Every judged event is appended to --events (JSONL, wall-clock ts) for timing.

Keep --src outside what workers can read (it holds the answers): workers run sandboxed, add it to HCTF_SANDBOX_HIDE.

  python3 hctf/replay_gm.py --port 18765 --events .run/replay/events.jsonl \\
      --replay warmups-day-06=.run/replay-src/warmups-eight-is-enough/single_solve ...
  python3 hctf/replay_gm.py --port 18777 --events /tmp/ev.jsonl --fault-cut 3 \\
      --timed fault-lane-day-99/time_trial=.run/fault/cases/tt-a,.run/fault/cases/tt-b
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
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = "https://2026.huntress.ctf.games"
CAP_RE = re.compile(r"(?:/download/|[?&]capability=)([0-9a-f]{64})")
STATE = {"single": {}, "solved": set(), "replayed": set(), "events": None, "lock": threading.RLock()}
# --fault-429 RATE: answer this fraction of submits with the GM's 429 {"error":"rate_limited"} WITHOUT judging (or
# forwarding) them -- rehearses the harness's unjudged-submit handling (a 429 must never count as incorrect).
FAULT = {"rate": 0.0, "rng": None, "cut": 0, "latency": 0.0, "start_503": 0, "prereq_flap": 0, "dl_stall": 0.0,
         "n_submit": 0}
# --timed: {cid: {"cases": [dir...], "i": next case index, "att": live attempt dict | None, "solved": bool,
#                 "fresh": variants left, "prereq": cid of the mode that must pass first | None}}
TIMED = {}
POOL = 32
NO_PREREQ = False


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


def load_timed(cid, dirs):
    """Register a locally served timed mode: each case dir holds contract.json (questions, answer_ids, name, prompt,
    ...), expected.json (the GM-verified answers) and the artifact file(s) (every other regular file, or artifacts/)."""
    cases = []
    for d in dirs:
        c = json.load(open(os.path.join(d, "contract.json")))
        exp = json.load(open(os.path.join(d, "expected.json")))
        files = sorted(p for p in glob.glob(os.path.join(d, "*")) + glob.glob(os.path.join(d, "artifacts", "*"))
                       if os.path.isfile(p) and os.path.basename(p) not in ("contract.json", "expected.json")
                       and not os.path.basename(p).startswith("."))
        if not files:
            raise SystemExit(f"{cid}: case {d} has no artifact file")
        ids = c.get("answer_ids") or list(exp)
        truth = {a: str(exp[a]) for a in ids if a in exp}
        if len(truth) != len(ids):
            raise SystemExit(f"{cid}: case {d}: expected.json covers {len(truth)}/{len(ids)} answer ids")
        cases.append({"dir": d, "contract": c, "truth": truth, "files": files})
    mode = cid.rsplit("/", 1)[-1]
    base = re.sub(r"/(time_trial|mastery)$", "", cid)
    prereq = None if (NO_PREREQ or mode != "mastery") else f"{base}/time_trial"
    TIMED[cid] = {"cases": cases, "i": 0, "att": None, "solved": False, "fresh": POOL, "prereq": prereq,
                  "n_start": 0, "n_prereq_flap": 0}
    STATE["replayed"].add(cid)


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


# ------------------------------------------------------------------------------------------------ local timed modes
def _pool_fields(t):
    return {"unique_attempts_remaining": t["fresh"], "hall_of_fame_eligible": False, "run_for_time": False,
            "ranked_attempts_remaining": t["fresh"], "regular_variants_remaining": t["fresh"],
            "training_variants_remaining": t["fresh"], "variant_fresh": True}


def _timed_body(cid, t, att):
    c = att["case"]["contract"]
    body = {k: c.get(k) for k in ("mode", "name", "prompt", "guidance", "questions") if k in c}
    body.setdefault("mode", cid.rsplit("/", 1)[-1])
    body.setdefault("name", cid)
    body.update(attempt_id=att["id"], started_at=att["started_at"], answer_ids=list(att["truth"]), deadline=None,
                remaining=len(att["truth"]) - len(att["banked"]), **_pool_fields(t))
    caps = list(att["caps"])
    body["download"] = f"/?op=download&capability={caps[0]}"
    body["sha256"] = att["caps"][caps[0]][1]
    if len(caps) > 1:
        body["artifacts"] = [{"name": att["caps"][x][2], "download": f"/?op=download&capability={x}",
                              "sha256": att["caps"][x][1]} for x in caps]
    return body


def _finished_body(cid, t):
    att = t["att"]
    return {"result": "CORRECT", "attempt_id": att["id"] if att else None, "mode": cid.rsplit("/", 1)[-1],
            "deadline": None, "flag": hashlib.md5(f"replay-{cid}".encode()).hexdigest(), **_pool_fields(t),
            "solved_by": {"name": "replay", "at": att.get("solved_at") if att else None}}


def _new_attempt(cid, t, reuse_last=False):
    """A fresh attempt on the next case (a fresh variant, one off the pool) -- or, `reuse_last` (the untimed practice
    continuation after the pool is spent), a new attempt on the LAST artifact again: empty bank, nothing off the pool."""
    if reuse_last and t["i"]:
        case = t["cases"][(t["i"] - 1) % len(t["cases"])]
    else:
        case = t["cases"][t["i"] % len(t["cases"])]
        t["i"] += 1
        t["fresh"] = max(0, t["fresh"] - 1)
    caps = {}
    for p in case["files"]:
        data = open(p, "rb").read()
        cap = hashlib.sha256(f"{cid}|{t['i']}|{p}".encode()).hexdigest()
        caps[cap] = (p, hashlib.sha256(data).hexdigest(), os.path.basename(p))
    att = {"id": str(uuid.uuid4()), "case": case, "truth": dict(case["truth"]), "banked": {}, "caps": caps,
           "started_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z", "done": False,
           "dl_stalled": False}
    t["att"] = att
    event(challenge=cid, op="start", attempt=att["id"], case=os.path.basename(case["dir"]), fresh_left=t["fresh"])
    return att


def timed_start(cid, op):
    """start / retry / practice on a locally served timed mode -> (http status, body)."""
    t = TIMED[cid]
    t["n_start"] += 1
    if FAULT["start_503"] > 0:
        FAULT["start_503"] -= 1
        event(challenge=cid, op=op, result="fault_503")
        return 503, {"error": "training_rotation_invalid"}
    if t["prereq"] and not TIMED.get(t["prereq"], {}).get("solved") and t["prereq"] not in STATE["solved"]:
        c = t["cases"][0]["contract"]
        return 409, {"error": "prerequisite_required", "mode": cid.rsplit("/", 1)[-1],
                     "questions": c.get("questions"), "name": c.get("name")}
    if t["prereq"] and FAULT["prereq_flap"] > 0:
        FAULT["prereq_flap"] -= 1
        event(challenge=cid, op=op, result="fault_prereq_flap")
        return 409, {"error": "prerequisite_required", "mode": cid.rsplit("/", 1)[-1]}
    att = t["att"]
    if att and not att["done"] and op in ("start", "retry", "practice"):
        if op == "start" or not att["done"]:
            # start reconnects to the live attempt; a retry on a LIVE attempt resumes it too (GM: retry advances only
            # after the current attempt ends)
            return 200, _timed_body(cid, t, att)
    if att and att["done"] and op == "start":
        return 200, _finished_body(cid, t)      # the latest attempt is finished: `start` hands it back (no answer_ids)
    if att is None and op == "practice":
        return 409, {"error": "start_required"}
    if (att is not None or op in ("retry", "practice")) and t["fresh"] <= 0:
        if op == "practice" and att is not None:
            # the untimed practice continuation: a new attempt on the last artifact (variant_fresh false)
            body = _timed_body(cid, t, _new_attempt(cid, t, reuse_last=True))
            return 200, {**body, "practice": True, "variant_fresh": False}
        return 409, {"error": "retry_variants_unavailable", **_pool_fields(t)}
    return 200, _timed_body(cid, t, _new_attempt(cid, t))


def timed_submit(cid, answers):
    t = TIMED[cid]
    att = t["att"]
    if att is None:
        return 409, {"error": "start_required"}
    if att["done"]:
        return 200, {"result": "already_solved", "attempt_id": att["id"], **_pool_fields(t)}
    unknown = [a for a in answers if a not in att["truth"]]
    if unknown:
        return 400, {"error": "unknown_answer_id", "answer_ids": unknown[:5]}
    wrong = [a for a, v in answers.items() if att["truth"][a] != str(v).strip()]
    if wrong:
        event(challenge=cid, op="submit", result="incorrect", n=len(answers), wrong=len(wrong))
        return 200, {"result": "incorrect", "attempt_id": att["id"],
                     "remaining": len(att["truth"]) - len(att["banked"]), **_pool_fields(t)}
    new = [a for a in answers if a not in att["banked"]]
    att["banked"].update({a: str(v).strip() for a, v in answers.items()})
    remaining = len(att["truth"]) - len(att["banked"])
    if remaining:
        event(challenge=cid, op="submit", result="accepted", n=len(answers), remaining=remaining, new=len(new))
        return 200, {"result": "accepted", "remaining": remaining, "accepted_ids": sorted(new),
                     "attempt_id": att["id"], **_pool_fields(t)}
    att["done"], t["solved"] = True, True
    att["solved_at"] = datetime.now(timezone.utc).isoformat()
    STATE["solved"].add(cid)
    event(challenge=cid, op="submit", result="CORRECT", n=len(answers), attempt=att["id"])
    return 200, {"result": "CORRECT", "attempt_id": att["id"], "remaining": 0, "accepted_ids": sorted(new),
                 "flag": hashlib.md5(f"replay-{cid}".encode()).hexdigest(), **_pool_fields(t)}


def timed_status(cid):
    t = TIMED[cid]
    att = t["att"]
    if t["solved"] and att and att["done"]:
        return 200, _finished_body(cid, t)
    if att is None:
        c = t["cases"][0]["contract"]
        return 409, {"error": "start_required", "mode": cid.rsplit("/", 1)[-1], "questions": c.get("questions"),
                     "name": c.get("name"), **_pool_fields(t)}
    b = _timed_body(cid, t, att)
    b["result"] = "in_progress"
    return 200, b


def timed_download(cap):
    for cid, t in TIMED.items():
        att = t["att"]
        if att and cap in att["caps"]:
            path, _sha, name = att["caps"][cap]
            if FAULT["dl_stall"] and not att["dl_stalled"]:
                att["dl_stalled"] = True
                event(challenge=cid, op="download", result="fault_dl_stall", seconds=FAULT["dl_stall"])
                time.sleep(FAULT["dl_stall"])
            return name, open(path, "rb").read()
    return None


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json", extra=None, cut=False):
        raw = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw) + (1000 if cut else 0)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        if cut:
            self.send_header("Connection", "close")
        self.end_headers()
        if cut:
            # the reply is cut off mid-body: the client's read() ends short of Content-Length (IncompleteRead)
            self.wfile.write(raw[: max(1, len(raw) // 2)])
            self.wfile.flush()
            self.close_connection = True
            try:
                self.connection.shutdown(1)
            except OSError:
                pass
            return
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
            got = timed_download(p.get("capability", ""))
            if got:
                name, data = got
                return self._send(200, data, "application/octet-stream",
                                  {"Content-Disposition": f'attachment; filename="{name}"'})
            if TIMED and not STATE["single"]:
                return self._send(404, {"error": "unknown_capability"})
        if op == "status" and cid in TIMED:
            return self._send(*timed_status(cid))
        if op == "status" and cid in STATE["single"] and cid not in STATE["solved"]:
            st = {k: v for k, v in STATE["single"][cid]["start"].items() if k not in ("attempt_id", "download", "deadline")}
            return self._send(409, {"error": "start_required", **st})
        if op == "status" and cid in STATE["single"]:
            return self._send(200, {"result": "CORRECT", **STATE["single"][cid]["start"]})
        if op == "list" and TIMED and not STATE["single"] and UPSTREAM == "":
            return self._send(200, {"challenges": []})
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
        if op == "_fault":      # test control: change the fault knobs of a running stand-in ({"op": "_fault", "latency": 0})
            FAULT.update({k: v for k, v in body.items() if k in FAULT and k not in ("rng", "n_submit")})
            return self._send(200, {"ok": True, **{k: v for k, v in FAULT.items() if k != "rng"}})
        if op == "submit" and FAULT["rate"] and FAULT["rng"].random() < FAULT["rate"]:
            event(challenge=cid, op="submit", result="fault_429", n=len(body.get("answers") or {}))
            return self._send(429, {"error": "rate_limited"}, extra={"Retry-After": "1"})
        if cid in STATE["single"]:
            if op in ("start", "retry"):
                event(challenge=cid, op="start")
                return self._send(200, STATE["single"][cid]["start"])
            if op == "submit":
                return self._send(200, judge(cid, body.get("answers") or {}))
        if cid in TIMED:
            with STATE["lock"]:
                if op in ("start", "retry", "practice"):
                    st, out = timed_start(cid, op)
                    return self._send(st, out)
                if op == "submit":
                    FAULT["n_submit"] += 1
                    cut = FAULT["cut"] and FAULT["n_submit"] % FAULT["cut"] == 0
                    st, out = timed_submit(cid, body.get("answers") or {})
            if op == "submit":
                if FAULT["latency"]:
                    time.sleep(FAULT["latency"])
                if cut:
                    event(challenge=cid, op="submit", result="fault_cut", judged=out.get("result"))
                return self._send(st, out, cut=bool(cut))
            return self._send(400, {"error": "unknown_op"})
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
    global UPSTREAM, POOL, NO_PREREQ
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=18765)
    ap.add_argument("--events", required=True)
    ap.add_argument("--upstream", default=UPSTREAM, help="the real GM for everything not served locally ('' = none)")
    ap.add_argument("--replay", action="append", default=[], help="<single_solve id>=<saved single_solve dir>")
    ap.add_argument("--timed", action="append", default=[],
                    help="<time_trial|mastery id>=<case dir>[,<case dir>...] served locally (see module doc)")
    ap.add_argument("--pool", type=int, default=32, help="fresh variants per local timed mode (default 32)")
    ap.add_argument("--no-prereq", action="store_true", help="local Mastery does not require the Time Trial first")
    ap.add_argument("--fault-429", type=float, default=0.0, help="fraction of submits answered 429 rate_limited, unjudged")
    ap.add_argument("--fault-cut", type=int, default=0, help="every Nth submit reply is cut off mid-body (judged)")
    ap.add_argument("--fault-latency", type=float, default=0.0, help="seconds every submit reply waits")
    ap.add_argument("--fault-start-503", type=int, default=0, help="first N timed starts -> 503 training_rotation_invalid")
    ap.add_argument("--fault-prereq-flap", type=int, default=0, help="first N Mastery starts -> 409 prerequisite_required")
    ap.add_argument("--fault-dl-stall", type=float, default=0.0, help="first download of each attempt waits S seconds")
    ap.add_argument("--seed", type=int, default=15)
    a = ap.parse_args()
    import random
    FAULT.update(rate=a.fault_429, rng=random.Random(a.seed), cut=a.fault_cut, latency=a.fault_latency,
                 start_503=a.fault_start_503, prereq_flap=a.fault_prereq_flap, dl_stall=a.fault_dl_stall)
    UPSTREAM = a.upstream
    POOL, NO_PREREQ = a.pool, a.no_prereq
    STATE["events"] = a.events
    os.makedirs(os.path.dirname(os.path.abspath(a.events)), exist_ok=True)
    for spec in a.replay:
        base, src = spec.split("=", 1)
        load_single(base, src)
    for spec in a.timed:
        cid, dirs = spec.split("=", 1)
        load_timed(cid, [d for d in dirs.split(",") if d])
    print(f"replay GM on 127.0.0.1:{a.port} -> {UPSTREAM or '(no upstream)'}; replaying {sorted(STATE['single'])}; "
          f"local timed {sorted(TIMED)}; faults {({k: v for k, v in FAULT.items() if k not in ('rng', 'n_submit') and v})}",
          flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()


if __name__ == "__main__":
    main()
