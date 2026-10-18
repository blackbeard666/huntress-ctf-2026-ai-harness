"""Offline check: lang_*.{bin,json} fixtures + lang_real_members.json rows through lib.binary.lang_facts / lang_field.
usage (repo root): python3 tests/data/binary_fixtures/lang_check.py"""
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib import binary as B

here = pathlib.Path(__file__).parent
cases = [(fj.stem, fj.with_suffix(".bin"), json.loads(fj.read_text())) for fj in sorted(here.glob("lang_*.json"))
         if fj.stem != "lang_real_members"]
cases += [(pathlib.Path(r["path"]).name, ROOT / r["path"], r)
          for r in json.loads((here / "lang_real_members.json").read_text())["rows"]]
bad = 0
for name, path, f in cases:
    if not path.exists():
        print(f"skip {name}: bytes not cached")
        continue
    data = path.read_bytes()
    t = time.time()
    got = B.lang_facts(data)
    ms = (time.time() - t) * 1e3
    want = f["expected_facts"]
    if want is None:
        diff = {} if got is None and B.lang_field(data, "has_nim_runtime") == "none" else {"facts": got}
    else:
        diff = {k: (got.get(k), v) for k, v in want.items() if got is None or got.get(k) != v}
        if got is None or got["language"] != f["expected_language"]:
            diff["language"] = (got and got["language"], f["expected_language"])
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{name}: {got and got['language']} ({ms:.0f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
