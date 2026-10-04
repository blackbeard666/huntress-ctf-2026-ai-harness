#!/usr/bin/env python3
"""One-shot timed attempt: the whole start -> download -> solve -> submit path in one process.

Runs LOCALLY against the public GM (pairing token) by default — direct HTTPS is fast enough for the
~6s Time Trial windows, so no VM/SSH is needed. Still runs unchanged ON Homebase against the inside
proxy (set HUNTRESS_GAME_MASTER_URL) as a fallback. The solver must already be correct
(built/generalised offline); this just executes the clock-critical path as fast as possible.

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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

GM = os.environ.get("HUNTRESS_GAME_MASTER_URL", "https://2026.huntress.ctf.games")
HW = Path(__file__).resolve().parent.parent          # project root locally; ~/hw on Homebase
CAP_RE = re.compile(r"(?:/download/|[?&]capability=)([0-9a-f]{64})")  # Homebase proxy or public GM


def _token():
    """Pairing token for the public GM: env first, then the project-local secret (None in-network)."""
    tok = os.environ.get("HUNTRESS_GM_TOKEN")
    if tok:
        return tok.strip()
    try:
        with open(HW / "secrets" / "gm_pairing_token") as f:
            return f.read().strip() or None
    except OSError:
        return None


def _auth(headers=None):
    headers = dict(headers or {})
    tok = _token()
    if tok:
        headers["Authorization"] = "Bearer " + tok
    return headers


def _post(payload, timeout=20):
    req = urllib.request.Request(GM, data=json.dumps(payload).encode(),
                                 headers=_auth({"Content-Type": "application/json"}), method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _get_bytes(cap, timeout=20):
    req = urllib.request.Request(f"{GM}?op=download&capability={cap}", headers=_auth())
    with urllib.request.urlopen(req, timeout=timeout) as r:
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
    t_started = time.time()

    # download artifacts into a temp dir next to the GM
    adir = HW / ".run" / "tmp-timed" / re.sub(r"[^A-Za-z0-9]+", "_", a.cid)
    adir.mkdir(parents=True, exist_ok=True)
    for f in adir.glob("*"):
        f.unlink()
    # Download every per-set delivery CONCURRENTLY: over the public GM each call is ~0.2s RTT, so a
    # many-file Mastery bundle must fetch in parallel or the ~6-10s window expires before the solver runs.
    plan = _plan(body)

    def _fetch(item):
        name, cap = item
        (adir / name).write_bytes(_get_bytes(cap))

    if plan:
        with ThreadPoolExecutor(max_workers=min(8, len(plan))) as ex:
            for _ in ex.map(_fetch, plan):  # propagate any download exception
                pass
    t_downloaded = time.time()

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
    t_solved = time.time()
    out["phases"] = {"start": round(t_started - t0, 2), "download": round(t_downloaded - t_started, 2),
                     "solve": round(t_solved - t_downloaded, 2)}
    if missing:
        out["result"] = "solver_incomplete"
        out["missing"] = missing
        print(json.dumps(out))
        return

    # FAST PATH: submit EVERY answer in one request. A public-GM submit round-trip is ~0.2-several s, so N
    # sequential per-set POSTs can blow a ~6-10s Mastery window (set 1 banks, set 2 expires). One POST covering
    # all sets fits even a tight window when the solver is complete+correct.
    def setkey(aid):
        m = re.match(r"(set|slot)[._-]?\d+", aid)
        return m.group(0) if m else "_"
    full = _post({"op": "submit", "challenge": a.cid, "answers": answers})
    out["phases"]["submit"] = round(time.time() - t_solved, 2)
    fk = str(full.get("result", "")).lower()
    out["full_result"] = fk
    if fk in ("correct", "accepted") and not full.get("remaining"):
        out["result"] = "correct"
        out["elapsed"] = round(time.time() - t0, 2)
        print(json.dumps(out))
        return

    # Not fully correct: break down per set to learn which set failed (clock permitting), so the offline
    # generalize worker gets granular feedback on the next cycle.
    groups = {}
    for aid, v in answers.items():
        groups.setdefault(setkey(aid), {})[aid] = v
    per_set, final = {}, fk or "incorrect"
    for key, grp in groups.items():
        res = _post({"op": "submit", "challenge": a.cid, "answers": grp})
        rk = str(res.get("result", "")).lower()
        per_set[key] = {"result": rk, "remaining": res.get("remaining")}
        if rk == "expired":
            final = "expired"
            break
        if rk not in ("correct", "accepted"):
            final = "incorrect"
    out["result"] = "correct" if all(v["result"] in ("correct", "accepted") for v in per_set.values()) and per_set else final
    out["per_set"] = per_set
    out["bad_sets"] = [k for k, v in per_set.items() if v["result"] not in ("correct", "accepted")]
    out["elapsed"] = round(time.time() - t0, 2)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
