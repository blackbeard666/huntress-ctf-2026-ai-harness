"""Offline check: every sfx_*.json fixture through lib.binary.appended_archive_facts(data, password); each expected key
must match (expected archive_offset "none" = decoy: facts None and every field "none"), < 1 s per call.
usage (repo root): python3 tests/data/binary_fixtures/sfx_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("sfx_*.json")):
    f = json.loads(fj.read_text())
    data = (fj.parent / f["bin"]).read_bytes()
    t = time.time()
    got = B.appended_archive_facts(data, f.get("password"))
    ms = (time.time() - t) * 1e3
    exp = f["expected"]
    if exp.get("archive_offset") == "none":
        diff = {} if got is None and B.appended_archive_field(data, "archive_offset") == "none" else {"got": got}
    else:
        diff = {k: ((got or {}).get(k), v) for k, v in exp.items() if (got or {}).get(k) != v}
        fld = B.appended_archive_field(data, "archive_offset", f.get("password"))
        if fld != str(exp["archive_offset"]):
            diff["field"] = fld
    ok = not diff and ms < 1000
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms {diff or ''}")
for junk in (b"", b"garbage", b"\x7fELF\x02" + b"\0" * 60, b"PK\x05\x06" + b"\xff" * 18, b"hsqs" + b"\xff" * 92):
    assert B.appended_archive_field(junk, "archive_offset") == "none", junk
sys.exit(1 if bad else 0)
