"""Independent oracle for pkd_* fixtures (no lib.binary): slices the stream at the recorded offset (bare / decoy) or
reads the RS20 header (overlay: key +5, len +8, sha256 +12, data +44), decompresses with a DIFFERENT implementation --
aPLib: pip `aplib` (snemes); LZNT1: dissect.util.compression.lznt1; LZ4 block: python-lz4 lz4.block.decompress;
raw LZMA: `xz -d --format=raw --lzma1=lc=3,lp=0,pb=2,dict=64KiB` -- and prints offset, sha_ok, HCFG crc_ok, JSON.
usage (repo root): python3 tests/data/binary_fixtures/pkd_oracle.py pkd_aplib_bare"""
import hashlib, json, pathlib, struct, subprocess, sys, zlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools" / "pk"))
import aplib, lz4.block
from dissect.util.compression import lznt1

R = {"aplib": lambda b: aplib.decompress(b), "lznt1": lznt1.decompress,
     "lz4block": lambda b: lz4.block.decompress(b, uncompressed_size=1 << 16),
     "lzma-raw": lambda b: subprocess.run(["xz", "-dq", "--format=raw", "--lzma1=lc=3,lp=0,pb=2,dict=64KiB", "-c"],
                                          input=b, capture_output=True).stdout}

name = sys.argv[1]
meta = json.loads((HERE / f"{name}.json").read_text())
data = (HERE / f"{name}.bin").read_bytes()
fmt = meta["encoding"]
if "stream_offset" in meta:
    o = meta["stream_offset"]
    out, sha_ok = R[fmt](data[o:o + meta["stream_length"]]), None
else:
    o = data.rfind(b"RS20")
    k, n = data[o + 5], struct.unpack_from("<I", data, o + 8)[0]
    out = R[fmt](bytes(b ^ k for b in data[o + 44:o + 44 + n]))
    sha_ok = hashlib.sha256(out).digest() == data[o + 12:o + 44]
k, n, crc = out[5], *struct.unpack_from("<HI", out, 6)
p = bytes(b ^ k for b in out[12:12 + n])
print(o, "sha_ok=%s" % sha_ok, out[:4].decode("latin-1"), "crc_ok=%s" % (zlib.crc32(p) == crc), p.decode())
