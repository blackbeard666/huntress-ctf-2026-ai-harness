"""Offline check: langof_*.{bin,json} fixtures + langof_real_members.json rows through lib.binary.language_of.
usage (repo root): python3 tests/data/binary_fixtures/langof_check.py"""
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib import binary as B

here = pathlib.Path(__file__).parent
cases = [(fj.stem, fj.with_suffix(".bin"), json.loads(fj.read_text())) for fj in sorted(here.glob("langof_*.json"))
         if fj.stem != "langof_real_members"]
cases += [(pathlib.Path(r["path"]).name, ROOT / r["path"], r)
          for r in json.loads((here / "langof_real_members.json").read_text())["rows"]]
bad = 0
for name, path, f in cases:
    if not path.exists():
        print(f"skip {name}: bytes not cached")
        continue
    data = path.read_bytes()
    t = time.time()
    got = B.language_of(data)
    ms = (time.time() - t) * 1e3
    diff = {}
    if f["expected_language"] is None:
        if got is not None or B.language_field(data) != "none":
            diff["language"] = (got and got["language"], None)
    else:
        for k in ("language", "toolchain", "source_language", "ambiguous_with"):
            want = f.get("expected_" + k)
            if want is not None and (got or {}).get(k) != want:
                diff[k] = ((got or {}).get(k), want)
    if ms > 1000:
        diff["ms"] = round(ms)
    bad += bool(diff)
    print(("ok  " if not diff else "BAD ") + f"{name}: {got and got['language']}/{got and got['toolchain']} "
          f"({ms:.0f} ms) {diff or ''}")
sys.exit(1 if bad else 0)
