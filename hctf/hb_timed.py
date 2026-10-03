#!/usr/bin/env python3
"""Runs ON Homebase: one-shot timed attempt entirely adjacent to the Game Master.

Day-2 Time Trial windows are ~6 seconds, so the whole start -> download -> solve -> submit path must run
where GM latency is sub-millisecond (Homebase), not orchestrated over SSH from WSL. The solver must already
be correct (built/generalised offline); this just executes the clock-critical path as fast as possible.

Usage:  python3 hb_timed.py <challenge-id> <solver_dir_rel_to_HW> [--op start|retry]
Prints one JSON line: {result, remaining, deadline, elapsed, submitted, detail}.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

GM = os.environ.get("HUNTRESS_GAME_MASTER_URL", "http://10.0.0.219/huntress-ctf-proxy")
HW = Path(__file__).resolve().parent.parent          # ~/hw
CAP_RE = re.compile(r"/download/([0-9a-f]{64})")


def _post(payload, timeout=20):
    req = urllib.request.Request(GM, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _get_bytes(cap, timeout=20):
    with urllib.request.urlopen(f"{GM}?op=download&capability={cap}", timeout=timeout) as r:
        return r.read()


def _deadline_left(body):
    d = (body or {}).get("deadline")
    if not d:
        return None
    import datetime as dt
    end = dt.datetime.fromisoformat(d.replace("Z", "+00:00"))
    return (end - dt.datetime.now(dt.timezone.utc)).total_seconds()


def _plan(body):
    """(filename, capability) per unique deliverable, named by the questions' container names (see cli._planned_downloads)."""
    caps = []
    arts = body.get("artifacts")
    src = arts if isinstance(arts, list) and arts else (body.get("downloads") or
          ([body["download"]] if body.get("download") else []))
    for x in src:
        s = x.get("download", "") if isinstance(x, dict) else str(x)
        m = CAP_RE.search(s)
        if m and m.group(1) not in caps:
            caps.append(m.group(1))
    containers = []
    for q in body.get("questions") or []:
        a = q.get("artifact")
        if a:
            n = os.path.basename(a.split("->")[0].strip())
            if n and n not in containers:
                containers.append(n)
    return [(containers[i] if i < len(containers) else f"artifact-{i}.bin", c) for i, c in enumerate(caps)]


def _normalize(v, q):
    norm = (q or {}).get("normalization")
    if norm == "exact":
        return v
    v = v.strip()
    return v.lower() if norm == "case_insensitive" else v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cid")
    ap.add_argument("solver_dir")           # relative to HW, e.g. challenges/day02/warmups-half-a-turn/solver
    ap.add_argument("--op", default="start", choices=["start", "retry"])
    a = ap.parse_args()
    t0 = time.time()
    out = {"cid": a.cid, "submitted": {}}

    body = _post({"op": a.op, "challenge": a.cid})
    # fresh clock if this attempt is already expired / past its deadline
    left = _deadline_left(body)
    if body.get("result") == "expired" or (left is not None and left <= 0.5):
        body = _post({"op": "retry", "challenge": a.cid})
        left = _deadline_left(body)
    out["deadline"] = body.get("deadline")
    out["attempt_id"] = body.get("attempt_id")
    ids = body.get("answer_ids") or []
    qmap = {aid: (body["questions"][i] if i < len(body.get("questions", [])) else {}) for i, aid in enumerate(ids)}
    if body.get("error") or not ids:
        out["result"] = body.get("error") or "no_answer_ids"
        out["detail"] = body
        print(json.dumps(out))
        return

    # download artifacts into a temp dir next to the GM
    adir = HW / ".tmp-timed" / re.sub(r"[^A-Za-z0-9]+", "_", a.cid)
    adir.mkdir(parents=True, exist_ok=True)
    for f in adir.glob("*"):
        f.unlink()
    for name, cap in _plan(body):
        (adir / name).write_bytes(_get_bytes(cap))

    # run the solver (already correct, offline-built); lib on PYTHONPATH
    contract = adir / "contract.json"
    contract.write_text(json.dumps(body))
    env = dict(os.environ, PYTHONPATH=str(HW))
    solve = HW / a.solver_dir / "solve.py"
    r = subprocess.run([sys.executable, str(solve), "--contract", str(contract), "--artifacts", str(adir)],
                       capture_output=True, text=True, timeout=max(2, (left or 30) - 1.5), env=env)
    try:
        answers = {k: _normalize(str(v), qmap.get(k, {})) for k, v in json.loads(r.stdout.strip().splitlines()[-1]).items()}
    except Exception:
        out["result"] = "solver_error"
        out["detail"] = r.stderr[-800:]
        print(json.dumps(out))
        return

    missing = [i for i in ids if i not in answers]
    out["submitted"] = answers
    if missing:
        out["result"] = "solver_incomplete"
        out["missing"] = missing
        print(json.dumps(out))
        return

    # one submit with everything, to spend the least time on the clock
    res = _post({"op": "submit", "challenge": a.cid, "answers": answers})
    out["result"] = str(res.get("result", "")).lower() or "unknown"
    out["remaining"] = res.get("remaining")
    out["elapsed"] = round(time.time() - t0, 2)
    out["detail"] = {k: res.get(k) for k in ("result", "remaining", "status", "flag") if k in res}
    print(json.dumps(out))


if __name__ == "__main__":
    main()
