"""Day-independent LANE solvers: deterministic, no-LLM solvers for a whole lane (every day's generator variation seen so
far), run FIRST by merged reuse (hctf/solvers.reuse_plan). Each lives in lib/lanes/<name>/solve.py with the standard solver
CLI (--contract --artifacts -> JSON {answer_id: value}) and stdlib-only deps so it also runs on Homebase.
Validated offline on every saved case of days 1-6 (warmups 49/49 cases, mobile 27/27, script-analysis 19134/19134 fields, binary 2494/2494, metadata 58/58 (generic tier alone too); .run/review3/ prototypes)."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANES = {"warmups": "warmups", "mobile-android": "mobile", "script-analysis": "script",
         "binary-reverse-engineering": "binary", "metadata-forensics": "metadata"}


def solver_dir(lane):
    """lib/lanes/<name> for a lane (index.json lane name), or None."""
    name = LANES.get(lane)
    d = HERE / name if name else None
    return d if d and (d / "solve.py").exists() else None


def wrapper_source(lane):
    """A challenge solver/solve.py that delegates to the lane solver (same depth rules as every solver: project root is
    parents[4]; on Homebase lib/ is synced, so the wrapper works there too)."""
    return f'''#!/usr/bin/env python3
"""Delegates to the day-independent lane solver lib/lanes/{LANES[lane]}/solve.py (seeded by merged reuse)."""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
runpy.run_path(str(ROOT / "lib" / "lanes" / "{LANES[lane]}" / "solve.py"), run_name="__main__")
'''
