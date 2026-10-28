"""Self-check: every multilang_drop case (12 never-shipped pool languages + underscore language labels, D28 layout) is
answered end-to-end by lib.codec: v3_plan(source) -> plan_answer (semantic ids) / pf_route + pf_answer (per-file ids).
Decoys must answer nothing. Expected values come from gen.py's coreutils oracle, never from lib.codec.
Run:  python3 tests/data/script_fixtures/multilang_drop/check.py   (exit 0 = all pass)"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))
from lib import codec  # noqa: E402

doc = json.loads((HERE / "cases.json").read_text())
bad, n, t0, worst = [], 0, time.time(), 0.0
for c in doc["cases"]:
    src = (HERE / "cases" / c["file"]).read_bytes()
    t1 = time.time()
    plan = codec.v3_plan(src)
    worst = max(worst, time.time() - t1)
    for qq in c["questions"]:
        q, exp = qq["q"], qq["expected"]
        n += 1
        if plan is None:
            got = None
        elif c["grammar"] == "per_file":
            r = codec.pf_route(q["id"], q)
            got = codec.pf_answer(r[2], plan, q, r[0]) if r else None
        else:
            got = codec.plan_answer(q["id"], plan, q)
        if got != exp:
            bad.append((c["file"], c["tag"], q["id"], exp, got))
for b in bad[:25]:
    print("FAIL", *b)
print(f"{'FAIL' if bad else 'ok'}  multilang_drop {n - len(bad)}/{n} answers over {len(doc['cases'])} files "
      f"in {time.time() - t0:.2f}s (slowest v3_plan {worst * 1000:.0f} ms)")
sys.exit(1 if bad else 0)
