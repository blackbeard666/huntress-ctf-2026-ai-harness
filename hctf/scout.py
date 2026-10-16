"""Time Trial scouting: spend cheap Time Trial attempts discovering GM label spellings BEFORE Mastery.

Why: the GM is an oracle only for constructs present in the variant you hold, and every Time Trial retry
(after `expired`) hands out a NEW variant. Mastery attempts are team-shared and expensive, so new constructs
(e.g. Day 4's VBS On-Error wrapper -> `error_guard`) should be met and labelled on Time Trial first.

Each round = one normal timed attempt (hb_timed: full submit; on failure, label-first binary search + in-window
label correction), followed by the usual bookkeeping (regression case, GM-verified labels cached to vocab.json).
A round is CLEAN when the solver got everything right with no label the GM had never confirmed before. Stop after
`clean` consecutive clean rounds; return the fields we could not fix so the caller can generalize offline.

Safe after a pass (verified 2026-10-05): the CourseStack scoreboard keeps the solve; only GM `status` (latest
attempt) changes, which cli.gm_solved() handles via its sticky marker. Mastery MAY check its prerequisite against
the latest Time Trial attempt, so callers re-pass Time Trial if the final scout round wasn't correct
(see orchestrate.Chain.scout_stage).
"""
import datetime as dt
import json
import os
import time

from . import cli, timed, workers

RATE_GAP = 8          # seconds between attempts (the GM 429s if hammered)


def _wait_expired(deadline, log, cid):
    if not deadline:
        return
    try:
        end = dt.datetime.fromisoformat(deadline.replace("Z", "+00:00"))
    except ValueError:
        return
    left = (end - dt.datetime.now(dt.timezone.utc)).total_seconds()
    if left > 0:
        log(f"[{cid}] scout: waiting {left + 2:.0f}s for the attempt to expire")
        time.sleep(left + 2)


SCOUT_MIN_ATTEMPTS = int(os.environ.get("HCTF_SCOUT_MIN_ATTEMPTS", "8"))   # keep fresh variants for the real run


def scout(cid, solver_dir, rounds=3, clean=2, log=print):
    """Run up to `rounds` Time Trial attempts. Returns a summary dict:
      rounds: per-round records, clean_streak, last_correct (bool), unresolved: [(aid, solver_value)] still wrong,
      fixed: {aid: label} the GM accepted as corrections, new_labels: {aid: label} newly cached."""
    summary = {"cid": cid, "rounds": [], "clean_streak": 0, "last_correct": False,
               "unresolved": [], "fixed": {}, "new_labels": {}}
    log_path = cli.cdir(cid) / "scout.jsonl"
    deadline = (timed.last_result(cid) or {}).get("deadline")
    for i in range(rounds):
        _wait_expired(deadline, log, cid)
        if i:
            time.sleep(RATE_GAP)
        left = (timed.last_result(cid) or {}).get("attempts_remaining")
        if i and left is not None and left < SCOUT_MIN_ATTEMPTS:
            log(f"[{cid}] scout: only {left} unique attempt(s) left for this mode today -- stopping")
            break
        # op=retry: a NEW variant each round (start on the passed attempt now reports already_passed, never re-rolls)
        res = workers.run_timed_auto(solver_dir, cid, op="retry", log=log)
        timed.process_result(cid, solver_dir, res, log=log)   # case capture + label caching + local record
        r = str(res.get("result", "")).lower()
        deadline = res.get("deadline")
        fixed = res.get("fixed") or {}
        wrong = [tuple(w) for w in (res.get("wrong") or []) if w[0] not in fixed]
        novel = res.get("novel_labels") or {}
        is_clean = r == "correct" and not novel
        rec = {"round": i + 1, "attempt": res.get("attempt_id"), "result": r, "window": res.get("window"),
               "in_window": res.get("in_window"), "routed": res.get("routed"), "novel_labels": novel,
               "fixed": fixed, "unresolved": wrong, "localize_complete": res.get("localize_complete"),
               "clean": is_clean, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
        with open(log_path, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        summary["rounds"].append(rec)
        summary["fixed"].update(fixed)
        summary["new_labels"].update(novel)
        summary["last_correct"] = r == "correct"
        summary["clean_streak"] = summary["clean_streak"] + 1 if is_clean else 0
        # keep only fields still wrong on the most recent variant that showed them (a later fix supersedes)
        seen = {a for a, _ in wrong}
        summary["unresolved"] = wrong + [w for w in summary["unresolved"] if w[0] not in seen and w[0] not in fixed]
        log(f"[{cid}] scout round {i + 1}/{rounds}: {r}"
            + (f", NEW labels {novel}" if novel else "") + (f", fixed in-window {fixed}" if fixed else "")
            + (f", still wrong {[a for a, _ in wrong][:6]}" if wrong else "")
            + (" (clean)" if is_clean else ""))
        if r in ("solver_error", "solver_incomplete", "exec_error"):
            summary["solver_failed"] = {"result": r, "missing": res.get("missing"), "detail": str(res.get("detail"))[:300]}
            break   # the solver itself can't handle this variant: generalize before scouting further
        if summary["clean_streak"] >= clean:
            break
    return summary
