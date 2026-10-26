#!/usr/bin/env python3
"""PostToolUse hook for harness Single Solve workers: (1) deliver unread harness inbox messages (hctf/inbox.py: reuse-race
banking, late dry-run notes) as "HARNESS UPDATE" context; (2) at 10 and 30 minutes without completion, push the worker
to split into alternative directions (ilio-style). No-op elsewhere."""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

STAGE = os.environ.get("HCTF_STAGE")
# generalize workers get inbox messages too (coordinator hints, hctf/coordinator.py); the timed nudges stay single-only.
# live workers too: a parallel live answer is narrowed to the runner's unresolved fields mid-run (rehearsal replay D26)
if STAGE not in ("single", "generalize", "live") or not os.environ.get("HCTF_CHAL"):
    sys.exit(0)

msgs = []
if os.environ.get("HCTF_INBOX", "1") != "0" and os.environ.get("HCTF_CHAL_DIR"):
    try:
        from hctf import inbox  # stdlib-only module: cheap on every tool call
        for m in inbox.unread(os.environ["HCTF_CHAL_DIR"], os.environ.get("HCTF_WORKER_START", "0")):
            if STAGE == "live" and (not str(m.get("key") or "").startswith("live")
                                    or float(m.get("ts") or 0) < float(os.environ.get("HCTF_WORKER_START") or 0)):
                # answer-first shares the single's inbox (its solver-writer notes are not for a live answer), and an
                # earlier attempt's narrowing note in the same mode dir is not about this worker's attempt
                continue
            msgs.append("HARNESS UPDATE (GM facts, authoritative): " + m.get("text", ""))
    except Exception:  # noqa: BLE001 - a hook must never break the worker
        pass

start = float(os.environ.get("HCTF_WORKER_START", time.time()))
minutes = (time.time() - start) / 60
if STAGE == "single" and minutes >= 10:   # the cli import (~0.2 s) only once a nudge can actually fire
    from hctf import cli, paths  # noqa: E402
    cid = os.environ["HCTF_CHAL"]
    mdir = paths.mode_dir(cid)
    for mark in (30, 10):
        flag = mdir / f".nudge{mark}-{int(start)}"
        if minutes >= mark and not flag.exists() and not cli.is_complete(cid):
            flag.write_text("")
            msgs.append(f"HARNESS: {int(minutes)} min and the Single Solve is not complete yet. Update notes.md, then "
                        "split with the explore-alternatives skill: spawn 2-3 subagents on genuinely different "
                        "directions (each with one bounded question), keep your own lane moving, merge their findings. "
                        "Only you submit.")
            break
if msgs:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "\n\n".join(msgs)}}))
sys.exit(0)
