"""Self-check: lib.codec.label_expansion reproduces every GM-verified label in cases.json (decoys -> None), < 1 ms each.
Run:  python3 tests/data/script_fixtures/expansion_regime/check.py   (exit 0 = all pass)"""
import json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib import codec  # noqa: E402

doc = json.loads((Path(__file__).parent / "cases.json").read_text())
t0, bad = time.time(), []
for c in doc["cases"]:
    got = codec.label_expansion(c["join_stmt"], None, c["contract"], c["echo_delayed"])
    if got != c["expected"]:
        bad.append((c["case"], c["answer_id"] if "answer_id" in c else "-", c["join_stmt"][:60], c["expected"], got))
assert codec.label_regime("batch_control", {"run_for_time": False}) == "legacy"
assert codec.label_regime("vbs_control", {"started_at": "2026-10-20"}) == "legacy"
assert codec.label_regime("batch_expansion", {"started_at": "2026-10-16T13:00:19.360Z"}) == "statement"
assert codec.label_regime("batch_expansion", {"run_for_time": True, "started_at": "2026-10-15T13:00:00Z"}) == "legacy"
for b in bad[:20]:
    print("FAIL", *b)
print(f"{'FAIL' if bad else 'ok'}  label_expansion {len(doc['cases']) - len(bad)}/{len(doc['cases'])} "
      f"in {time.time() - t0:.3f}s")
sys.exit(1 if bad else 0)
