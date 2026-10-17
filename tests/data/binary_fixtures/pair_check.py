"""Offline check: every pair_*.{bin,json} fixture through lib.binary.zip_cd_sha256 + pair_route + pair_member_facts.
usage (repo root): python3 tests/data/binary_fixtures/pair_check.py"""
import io, json, pathlib, sys, time, zipfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("pair_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t = time.time()
    shas = B.zip_cd_sha256(data)
    errs = [] if [s for _, s in shas or []] == f["expected_sha256"] else [f"sha256 order {shas}"]
    z = zipfile.ZipFile(io.BytesIO(data))
    members = [(zi.filename, z.read(zi)) for zi in z.infolist()]
    for field, want in f["routes"].items():
        r = B.pair_route(field, members)
        if want is None:
            if r is not None:
                errs.append(f"{field}: routed {r} (want none)")
            continue
        if r is None or members[r[0]][0].rsplit("/", 1)[-1] != want["member"]:
            errs.append(f"{field}: route {r} (want {want['member']})")
            continue
        fx = B.pair_member_facts(members[r[0]][1]) or {}
        got = fx.get(r[1], "none")
        if got != want["value"]:
            errs.append(f"{field}: {got!r} != {want['value']!r}")
    bad += bool(errs)
    print(("ok  " if not errs else "BAD ") + f"{fj.stem}: {len(f['routes'])} routes ({(time.time() - t) * 1e3:.1f} ms)")
    for e in errs:
        print("     ", e)
sys.exit(1 if bad else 0)
