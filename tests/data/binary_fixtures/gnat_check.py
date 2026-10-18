"""Offline check: gnat_*.{bin,json} fixtures + gnat_real_members.json rows through lib.binary.gnat_facts / gnat_field.
usage (repo root): python3 tests/data/binary_fixtures/gnat_check.py"""
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib import binary as B

here = pathlib.Path(__file__).parent
cases = [(fj.stem, fj.with_suffix(".bin"), json.loads(fj.read_text())) for fj in sorted(here.glob("gnat_*.json"))
         if fj.stem != "gnat_real_members"]
cases += [(pathlib.Path(r["path"]).name, ROOT / r["path"], r)
          for r in json.loads((here / "gnat_real_members.json").read_text())["rows"]]
bad = 0
for name, path, f in cases:
    if not path.exists():
        print(f"skip {name}: bytes not cached")
        continue
    data = path.read_bytes()
    t = time.time()
    got = B.gnat_facts(data)
    ms = (time.time() - t) * 1e3
    want = f["expected_facts"]
    if want is None:
        diff = {} if got is None and B.gnat_field(data, "gnat_version") == "none" else {"facts": got}
    else:
        diff = {k: (got.get(k) if got else None, v) for k, v in want.items() if got is None or got.get(k) != v}
    if ms > 1000:
        diff["ms"] = ms
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{name}: ({ms:.0f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
