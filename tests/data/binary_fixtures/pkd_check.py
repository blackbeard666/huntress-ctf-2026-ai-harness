"""Offline check of the packer decompressors: every pkd_*.{bin,json} fixture through lib.binary --
packer_hcfg(stream) for bare/decoy streams and overlay_spec(question) + overlay_spec_unpack for RS20 overlays.
Positives must yield the crc-valid HCFG JSON (and the overlay offset/size); decoys -> no valid HCFG / None.
usage (repo root): python3 tests/data/binary_fixtures/pkd_check.py"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import binary as B

bad = 0
for fj in sorted(pathlib.Path(__file__).parent.glob("pkd_*.json")):
    f = json.loads(fj.read_text())
    data = fj.with_suffix(".bin").read_bytes()
    t, res = time.time(), []
    if "stream_offset" in f:
        o = f["stream_offset"]
        r = B.packer_hcfg(data[o:o + f["stream_length"]])
        res.append((r[2].config, r[0]) if r else ("none", None))
    if "question" in f:
        r = B.overlay_spec_unpack(data, B.overlay_spec(f["question"]))
        h = B.hcfg_find(r[3]) if r else None
        res.append((h.config if h else "none", r and (r[0], r[1], r[4])))
    ms = (time.time() - t) * 1e3
    ok = ms < 1000 and all(c == f["expected_config"] for c, _ in res)
    if not f.get("decoy"):
        ok = ok and all(x == (f["expected_offset"], f["expected_size"], True) for c, x in res if isinstance(x, tuple))
        ok = ok and all(x == f["encoding"] for c, x in res if isinstance(x, str))
    bad += not ok
    print(("ok  " if ok else "BAD ") + f"{fj.stem}: {ms:.1f} ms -> {[(str(c)[:40], x) for c, x in res]}")
sys.exit(1 if bad else 0)
