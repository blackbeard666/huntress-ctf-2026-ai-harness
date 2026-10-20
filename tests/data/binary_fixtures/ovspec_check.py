"""Offline check: every ovspec_*.{bin,json} fixture through lib.binary.overlay_spec(question) +
overlay_spec_unpack(data, spec): (offset, size) and the HCFG JSON at unpacked offset 0 must match; decoys -> None.
usage (repo root): python3 tests/data/binary_fixtures/ovspec_check.py"""
import json, pathlib, struct, sys, time, zlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("ovspec_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    r = B.overlay_unpack(data, B.overlay_spec(f["question"]))
    ms = (time.time() - t) * 1e3
    got = "none"
    if r:
        u = r[3]
        k, n, crc = u[5], *struct.unpack_from("<HI", u, 6)
        p = bytes(b ^ k for b in u[12:12 + n])
        got = json.loads(p) if zlib.crc32(p) == crc else "crc-bad"
    exp = f["expected_config"]
    ok = (got == exp or isinstance(got, dict) and isinstance(exp, dict) and all(got.get(k) == v for k, v in exp.items())) and ms < 1000 and (
        r is None if f.get("decoy") else (r[0], r[1], r[4]) == (f["expected_offset"], f["expected_size"], True))
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms -> {r and (r[0], r[1], r[4])} {str(got)[:60]}")
sys.exit(1 if bad else 0)
