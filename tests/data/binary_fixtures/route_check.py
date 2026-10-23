"""Offline check: every route_*.{bin,json} fixture through lib.binary.route_member (group = the id's dNN-- members in
central-directory order). usage (repo root): python3 tests/data/binary_fixtures/route_check.py"""
import io, json, pathlib, re, sys, time, zipfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("route_*.json")):
    f = json.loads(fj.read_text())
    z = zipfile.ZipFile(io.BytesIO(fj.with_suffix(".bin").read_bytes()))
    members = [(zi.filename, z.read(zi)) for zi in z.infolist()]
    errs, t = [], time.time()
    for r in f["routes"]:
        day = re.match(r"(d\d+)_", r["id"]).group(1)
        group = [(n, b) for n, b in members if n.startswith(day + "--")]
        i, rest = B.route_member(group, r["id"], r["question"])
        got = group[i][0] if i is not None else None
        if got != r["member"] or rest != r["residual"]:
            errs.append(f"{r['id']} [{r['question'][:50]}]: ({got}, {rest}) != ({r['member']}, {r['residual']}) "
                        f"via {B._route_member(group, r['id'], r['question'])[2]}")
    bad += bool(errs)
    print(("ok  " if not errs else "BAD ") + f"{fj.stem}: {len(f['routes'])} routes ({(time.time() - t) * 1e3:.1f} ms)")
    for e in errs:
        print("     ", e)
sys.exit(1 if bad else 0)
