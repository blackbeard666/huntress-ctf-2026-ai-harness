#!/usr/bin/env python3
"""PostToolUse hook for harness Single Solve workers: at 10 and 30 minutes without completion,
push the worker to split into alternative directions (ilio-style). No-op elsewhere."""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

if os.environ.get("HCTF_STAGE") != "single" or not os.environ.get("HCTF_CHAL"):
    sys.exit(0)

from hctf import cli, paths  # noqa: E402

cid = os.environ["HCTF_CHAL"]
start = float(os.environ.get("HCTF_WORKER_START", time.time()))
minutes = (time.time() - start) / 60
mdir = paths.mode_dir(cid)
for mark in (30, 10):
    flag = mdir / f".nudge{mark}-{int(start)}"
    if minutes >= mark and not flag.exists() and not cli.is_complete(cid):
        flag.write_text("")
        msg = (f"HARNESS: {int(minutes)} min and the Single Solve is not complete yet. Update notes.md, then split "
               "with the explore-alternatives skill: spawn 2-3 subagents on genuinely different directions "
               "(each with one bounded question), keep your own lane moving, merge their findings. Only you submit.")
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}))
        break
sys.exit(0)
