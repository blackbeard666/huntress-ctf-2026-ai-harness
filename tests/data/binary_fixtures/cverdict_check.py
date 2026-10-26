"""Offline check: every cverdict_*.{bin,json} fixture (+ companion cverdict_*_exe.elf) through
lib.binary.crash_verdict_field; decoys (expected_facts null) must give None. Also checks the oracle's first-ranked
rule tags (minus PossibleStackCorruption, which needs gdb's unwinder) against other_tags.
usage (repo root): python3 tests/data/binary_fixtures/cverdict_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("cverdict_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    exe = (fj.parent / f["companion"]).read_bytes() if f.get("companion") else None
    t = time.time()
    if f["expected_facts"] is None:
        got = B.crash_verdict_facts(data, exe)
        ok = got is None
        want = None
    else:
        want = dict(f["expected_facts"])
        got = {k: B.crash_verdict_field(data, k, exe) for k in want}
        if "oracle_other_tags" in f:
            want["other_tags"] = json.dumps([x for x in f["oracle_other_tags"] if x != "PossibleStackCorruption"],
                                            separators=(",", ":"))
            got["other_tags"] = B.crash_verdict_field(data, "other_tags", exe)
        ok = got == want
    ms = (time.time() - t) * 1e3
    hit = next((h for h in B.hcfg_scan(data) if h.valid), None)
    ok = ok and hit is None
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms" + ("" if hit is None else f" unexpected hcfg {hit}"))
    if not ok and want is not None and got is not None:
        for k in want:
            if got.get(k) != want[k]:
                print(f"     {k}: got {got.get(k)!r}\n     {' ' * len(k)}  want {want[k]!r}")
    elif not ok:
        print(f"     got {got!r} want {want!r}")
sys.exit(1 if bad else 0)
