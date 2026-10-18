"""Offline check: every qrule_*.{bin,json} contract fixture through lib.binary's contract-rule helpers
(contract_accepted / contract_rules / qrule_pick / qrule_enforce / contract_diff).
usage (repo root): python3 tests/data/binary_fixtures/qrule_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

here = pathlib.Path(__file__).parent
bad = 0
for fj in sorted(here.glob("qrule_*.json")):
    f = json.loads(fj.read_text())
    c = (here / f["contract"]).read_bytes()
    t = time.time()
    qs = {q["id"]: q for q in json.loads(c)["questions"]}
    errs = []
    if B.contract_accepted(c) != f["expected_accepted"]:
        errs.append(("accepted", B.contract_accepted(c)))
    rules = {k: [list(p) for p in v] for k, v in B.contract_rules(c).items()}
    if rules != f["expected_rules"]:
        errs.append(("rules", rules))
    for qid, holds, want in f["expected_pick"]:
        got = B.qrule_pick(B.qrule_rules(qs[qid]), holds)
        if got != want:
            errs.append(("pick", qid, holds, got))
    for qid, val, want in f["expected_enforce"]:
        got = B.qrule_enforce(qs[qid], val)
        if got != want:
            errs.append(("enforce", qid, val, got))
    if f["baseline"]:
        d = B.contract_diff((here / f["baseline"]).read_bytes(), c)
        got = {k: (v if k.startswith("_") else v["changed"]) for k, v in d.items()}
        if got != f["expected_diff"]:
            errs.append(("diff", got))
        for line in B.contract_revision_lines((here / f["baseline"]).read_bytes(), c):
            print("     ", line[:160])
    bad += bool(errs)
    print(("ok  " if not errs else "BAD ") + f"{fj.stem}: {len(rules)} rule ids, {len(f['expected_enforce'])} enforce "
          f"({(time.time() - t) * 1e3:.1f} ms)" + ("".join(f"\n     {e}" for e in errs)))
sys.exit(1 if bad else 0)
