"""Day 14 prep, stream S4 (binary lane): lib.binary.hcfg_scan -- the HCFG config blob in every storage encoding
(raw/base64 as on D2-D13, plus hex variants, base64url, base32, base85/ascii85, UTF-16LE/BE, reversed, single-byte
xor'd, zlib/gzip/raw deflate), crc-gated against decoys, offset law per encoding, the kill switch, and its fallback
wiring in the newest binary solver (challenges/day13/binary-crystal-clear/solver/solve.py). Offline: no GM/Homebase.

Fixtures: tests/data/hcfg_fixtures/ (make.py regenerates them byte-identically; expected values come from the generator).

Run:  source bin/env.sh && python3 tests/test_day14_s4.py      (exit 0 = all pass)
"""
import importlib.util
import json
import os
import random
import sys
import tempfile
import time
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import binary as B  # noqa: E402

FIX = ROOT / "tests" / "data" / "hcfg_fixtures"
_spec = importlib.util.spec_from_file_location("hcfg_make", FIX / "make.py")
make = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(make)
EXPECTED = json.loads((FIX / "expected.json").read_text())
LEGACY = {"raw", "base64", "base64url", "hex"}   # what the D13 solver's native scan already decodes
NEW_ENC = {e["encoding"] for e in EXPECTED if e["valid"]} - LEGACY


def first_valid(hits):
    return next((h for h in hits if h.valid), None)


def check(e, h, where):
    got = h and (h.offset, h.encoding, h.key, h.version, h.crc, h.config)
    want = (e["offset"], e["encoding"], e["key"], e["version"], e["crc"], e["config"])
    assert got == want, (where, e["file"], got and got[:5], want[:5])


# 1) generator is deterministic: the committed fixtures are exactly what make.py builds
with tempfile.TemporaryDirectory() as d:
    make.main(d)
    for f in sorted(FIX.iterdir()):
        if f.suffix in (".bin", ".json"):
            assert (Path(d) / f.name).read_bytes() == f.read_bytes(), f"stale fixture {f.name}: re-run make.py"
    assert len(list(Path(d).iterdir())) == len([f for f in FIX.iterdir() if f.suffix in (".bin", ".json")])
print(f"ok  fixtures: {len(EXPECTED)} files regenerate byte-identically from make.py")

# 2) every encoding found at the generator's offset with the generator's header/config; offset law flag
for e in EXPECTED:
    hits = B.hcfg_scan((FIX / e["file"]).read_bytes())
    if not e["valid"]:
        assert first_valid(hits) is None, (e["file"], hits)
        continue
    h = first_valid(hits)
    check(e, h, "scan")
    assert h.speculative == (e["encoding"] not in ("raw", "base64")), (e["file"], h.speculative)
    assert h.crc_ok and h.plain == json.dumps(e["config"], separators=(",", ":")).encode()
    assert h.as_solver()["crc"] == e["crc"] and h.as_solver()["offset"] == e["offset"]
    for dec in e.get("decoys", []):   # decoys are reported, but never as the valid blob
        assert any((x.offset, x.encoding, x.valid) == (dec["offset"], dec["encoding"], False) for x in hits), dec
print(f"ok  hcfg_scan: {sum(e['valid'] for e in EXPECTED)} encodings at the generator's offsets "
      f"({len(NEW_ENC)} new: {', '.join(sorted(NEW_ENC))}); decoys crc-rejected")

# 3) decoy semantics: a bare "HCFG" string (n=0) is never crc_ok; truncated + wrong magic never valid
hits = B.hcfg_scan((FIX / "decoy_none.bin").read_bytes())
assert hits and not any(h.valid for h in hits) and not any(h.crc_ok for h in hits), hits
assert B.hcfg_find((FIX / "decoy_none.bin").read_bytes()) is None
print("ok  decoys: assert-string magic, truncated blob, wrong magic -> no valid hit (hcfg_find None)")

# 4) placement robustness: every encoding re-embedded at fresh offsets (odd too, except 2-aligned UTF-16), seeds 1-4
n = 0
for seed in range(1, 5):
    r = random.Random(seed)
    for i, (name, (enc, fn)) in enumerate(make.ENCODINGS.items()):
        cfg, key = make.config(50 + i), r.randrange(1, 256)
        data = make.container(seed * 100 + i) + make.container(seed * 100 + i + 1)
        stored = fn(make.blob(cfg, key))
        off = r.randrange(600, 3000) & (~1 if enc.startswith("utf16") else ~0)
        data[off - 1:off] = b"\0"
        data[off:off + len(stored)] = stored
        data[off + len(stored):off + len(stored) + 2] = b"\0\0"
        h = B.hcfg_find(bytes(data))
        assert h and (h.offset, h.encoding, h.key, h.config) == (off, enc, key, cfg), (seed, name, h, off)
        n += 1
print(f"ok  placement: {n} re-embeds (4 seeds x {len(make.ENCODINGS)} encodings) found at the right offset")

# 5) kill switch: ext=False keeps only the D13 solver's encodings (raw, base64/url, plain hex)
for e in EXPECTED:
    h = first_valid(B.hcfg_scan((FIX / e["file"]).read_bytes(), ext=False))
    if e["valid"] and e["encoding"] in LEGACY:
        check(e, h, "ext=False")
    else:
        assert h is None, (e["file"], h)
print("ok  ext=False (HCTF_HCFG_SCAN_EXT=0): raw/base64/base64url/hex only, every new encoding ignored")

# 6) bounded runtime: 4 MB of binary-looking filler (worst case: no blob -> every pass), a blob near the end, deadline
big = bytearray()
k = 0
while len(big) < (4 << 20):
    big += make.container(k)
    k += 1
big = bytes(big)
t = time.time()
assert B.hcfg_scan(big) == []
t_none = time.time() - t
e = next(x for x in EXPECTED if x["file"] == "zlib6.bin")
blobbed = big[:-4096] + (FIX / "zlib6.bin").read_bytes()
t = time.time()
h = B.hcfg_find(blobbed)
t_hit = time.time() - t
assert h and h.offset == len(big) - 4096 + e["offset"] and h.encoding == "zlib", h
t = time.time()
B.hcfg_scan(big, deadline=time.time() - 1)
t_late = time.time() - t
# full no-blob scan: ~0.6 s alone, 1.3-1.5 s with the other suites running in parallel (2026-10-17) -> 2.5 s cap
assert t_none < 2.5 and t_hit < 1.0 and t_late < 0.2, (t_none, t_hit, t_late)
print(f"ok  runtime on 4 MB: no blob {t_none * 1000:.0f} ms (all passes), zlib blob at the end {t_hit * 1000:.0f} ms, "
      f"expired deadline {t_late * 1000:.0f} ms")

# 7) solver wiring (D13 = newest binary solver, raced first): native_hcfg / jar path fall back to hcfg_scan; flag off
#    = the D13 behaviour (hcfg_scan never called)
SOLVER = ROOT / "challenges" / "day13" / "binary-crystal-clear" / "solver" / "solve.py"
_s = importlib.util.spec_from_file_location("d13_binary_solver", SOLVER)
S = importlib.util.module_from_spec(_s)
_s.loader.exec_module(S)
for e in EXPECTED:
    if not e["valid"]:
        continue
    data = (FIX / e["file"]).read_bytes()
    h = S.native_hcfg(data)
    assert h and (h["offset"], h["key"], h["version"], h["crc"], h["config"]) == (
        e["offset"], e["key"], e["version"], e["crc"], e["config"]), (e["file"], h)
    if e["encoding"] in NEW_ENC:
        assert h.get("encoding") == e["encoding"], (e["file"], h)
jar_like = b"\xca\xfe\xba\xbe" + (FIX / "base32.bin").read_bytes()   # jar path: a bare class file
h = S.jar_hcfg(jar_like)
assert h and h["config"] == next(x for x in EXPECTED if x["file"] == "base32.bin")["config"], h
calls = []
orig = B.hcfg_find
B.hcfg_find = lambda *a, **kw: calls.append(1) or orig(*a, **kw)
try:
    os.environ["HCTF_HCFG_SCAN_EXT"] = "0"
    assert S.hcfg_ext((FIX / "zlib6.bin").read_bytes()) is None
    off_zlib = S.native_hcfg((FIX / "zlib6.bin").read_bytes())
    assert off_zlib is None or "encoding" not in off_zlib, off_zlib
    assert calls == [], calls
    del os.environ["HCTF_HCFG_SCAN_EXT"]
    assert S.native_hcfg((FIX / "zlib6.bin").read_bytes())["encoding"] == "zlib" and calls
finally:
    B.hcfg_find = orig
    os.environ.pop("HCTF_HCFG_SCAN_EXT", None)
print("ok  D13 solver: native_hcfg + jar_hcfg fall back to hcfg_scan for every new encoding; "
      "HCTF_HCFG_SCAN_EXT=0 never calls it")

# 8) real artifacts (main copies with Day 13 data): hcfg_find agrees with the D13 solver on every member
EV = ROOT / "challenges" / "day13" / "binary-crystal-clear" / "single_solve" / "artifacts" / "latest" / "evidence.zip"
if EV.exists():
    agree = 0
    for item in S.unzip(EV.read_bytes(), lazy=False):
        name, b = item[0], item[1]
        b = b() if callable(b) else b
        if not S.is_binary(b) or S.is_jar(b) or len(b) > (8 << 20):
            continue
        want = S.native_hcfg(b)
        h = B.hcfg_find(b)
        assert (h and (h.offset, h.key, h.crc)) == (want and (want["offset"], want["key"], want["crc"])), (name, h)
        assert h is None or not h.speculative, (name, h)   # D2-D13 are all raw/base64: GM-confirmed offsets
        agree += 1
    print(f"ok  real Day 13 evidence.zip: hcfg_find == D13 solver on {agree} native members (raw/base64, confirmed)")
else:
    print("skip real-artifact parity: no Day 13 evidence.zip in this copy")

print("\nALL DAY-14 S4 CHECKS PASSED")
