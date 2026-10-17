"""Regenerate cases.json: GM-verified batch `expansion` labels paired with the join statement they label.

Reader (independent of lib.codec.label_expansion): the D16 solver's own batch interpreter
(challenges/day16/.../solver/batchplan.py: Batch(text).run() trace -> the last executed `set` of the echoed variable
whose right-hand side carries % or !). Label = the GM's expected.json answer for that member's `*-expansion` id.
Run:  python3 tests/data/script_fixtures/expansion_regime/gen.py   (offline; reads only solver/cases/)
"""
import importlib.util, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
SOLVER = ROOT / "challenges/day16/scripting-same-same-but-different/solver"
sys.path.insert(0, str(SOLVER))
spec = importlib.util.spec_from_file_location("d16solve", SOLVER / "solve.py")
S = importlib.util.module_from_spec(spec)
sys.argv = ["x"]
spec.loader.exec_module(S)
BP = S.BP


def join_of(data):
    text = data.decode("utf-8", "ignore").lstrip("﻿")
    b = BP.Batch(text).run()
    target = None
    for lno, _ in b.trace:
        mm = re.match(r"(?i)echo.\s*[!%]([^!%]+)[!%]", b.lines[lno].strip())
        if mm:
            target = mm.group(1).lower()
    if not target:
        return None
    echo_delayed = any(re.match(r"(?i)echo.\s*!%s!" % re.escape(target), b.lines[l].strip()) for l, _ in b.trace)
    for lno, _ in reversed(b.trace):
        raw = b.lines[lno].strip()
        if re.search(r'(?i)set\s+"?%s=' % re.escape(target), raw) and re.search(r"[%!]", raw.split("=", 1)[1]):
            return raw, echo_delayed
    return None


# decoys: not a join statement (no `=`, or no %/! on the right-hand side, or not text) -> label_expansion None
DECOYS = [{"case": "decoy", "decoy": True, "join_stmt": j, "echo_delayed": True, "contract": c, "expected": None}
          for j, c in (('echo(!cfg!)', {"run_for_time": False}), ('set "cfg=v=3|steps=a,b"', {}),
                       ('rem HUNTRESS-MATERIAL:7633d', {"started_at": "2026-10-16T13:00:00Z"}), ('', None),
                       ('\x00\xff=\x01', {"run_for_time": True}))]
out, seen = [], set()
for cdir in sorted(ROOT.glob("challenges/day*/scripting-*/solver/cases/*/")):
    try:
        contract = json.loads((cdir / "contract.json").read_text())
        exp = json.loads((cdir / "expected.json").read_text())
    except Exception:
        continue
    exp = exp.get("answers", exp)
    qs = {q["id"]: q for q in contract.get("questions") or [] if isinstance(q, dict) and q.get("id")}
    S.CONTRACT.clear(); S.CONTRACT.update(contract); S._INDEX.clear()
    for aid, label in exp.items():
        if not re.search(r"(^|\.)batch-[a-z]+-expansion$", aid) or aid not in qs:
            continue
        try:
            got = join_of(S.find_member(str(cdir / "artifacts"), qs[aid].get("artifact") or ""))
        except Exception as e:  # noqa: BLE001
            print("skip", cdir.name, aid, repr(e)[:80], file=sys.stderr)
            continue
        if not got or (contract.get("attempt_id") or cdir.name, aid) in seen:  # cases are copied forward day to day: keep the first copy
            continue
        seen.add((contract.get("attempt_id") or cdir.name, aid))
        out.append({"case": "%s/%s" % (cdir.parts[-5], cdir.name), "answer_id": aid, "join_stmt": got[0],
                    "echo_delayed": got[1],
                    "contract": {k: contract[k] for k in ("run_for_time", "started_at") if k in contract},
                    "expected": label})
doc = {"_doc": __doc__.strip().splitlines()[0],
       "generator_cmd": "GM-generated evidence (challenges/day*/scripting-*/solver/cases/*/artifacts); join line read by "
                        "python3 tests/data/script_fixtures/expansion_regime/gen.py (D16 batchplan.Batch trace)",
       "oracle_cmd": "GM expected.json answers (judged CORRECT by the Game Master) for each *-expansion answer_id",
       "cases": out + DECOYS}
(Path(__file__).parent / "cases.json").write_text(json.dumps(doc, indent=1) + "\n")
print(len(out), "cases")
