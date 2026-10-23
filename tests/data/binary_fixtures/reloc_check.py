"""Offline check: every reloc_*.json fixture through lib.binary.elf_reloc_facts (expected_facts subset) and
hcfg_find (encoding / expected_offset / expected_config; decoys -> no valid blob).
usage (repo root): python3 tests/data/binary_fixtures/reloc_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

here, bad = pathlib.Path(__file__).parent, 0
for fj in sorted(here.glob("reloc_*.json")):
    f = json.loads(fj.read_text())
    data = (here / f["file"]).read_bytes()
    t = time.time()
    got = B.elf_reloc_facts(data)
    h = B.hcfg_find(data)
    ms = (time.time() - t) * 1e3
    want, errs = f["expected_facts"], []
    if want is None:
        if got is not None:
            errs.append(f"facts: got {type(got).__name__}, want None")
    else:
        errs += [f"{k}: got {(got or {}).get(k)!r} want {v!r}" for k, v in want.items() if (got or {}).get(k) != v]
    if f["expected_config"] is None:
        if h is not None:
            errs.append(f"hcfg: got {h.encoding}@{h.offset}, want none")
    elif h is None or (h.config, h.offset, h.encoding) != (f["expected_config"], f["expected_offset"], f["encoding"]):
        errs.append(f"hcfg: got {h and (h.encoding, h.offset, h.config)!r}")
    bad += bool(errs)
    print(("BAD " if errs else "ok  ") + f"{fj.stem}: {ms:.1f} ms")
    for e in errs:
        print("     " + e)
sys.exit(1 if bad else 0)
