"""Generate pkd_* fixtures: an HCFG record compressed by an INDEPENDENT writer per format, either bare (inside a
filler 'binary') or wrapped in an RS20 overlay (key u8 at +5, packed length u32le at +8, sha256(unpacked) at +12,
packed bytes at +44, packed = compressed ^ key). Writers: aPLib -> pkd_aplib_pack.py (own packer, spec-derived);
LZNT1 -> pip `lznt1` (compress); LZ4 block -> python-lz4 lz4.block.compress(store_size=False); raw LZMA ->
`xz --format=raw --lzma1=lc=3,lp=0,pb=2,dict=64KiB`. usage (repo root): python3 tests/data/binary_fixtures/pkd_gen.py"""
import hashlib, json, pathlib, random, struct, subprocess, sys, zlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools" / "pk"))
sys.path.insert(0, str(HERE))
import lznt1, lz4.block, pkd_aplib_pack


def hcfg(cfg, key):
    p = json.dumps(cfg, separators=(",", ":")).encode()
    return b"HCFG" + struct.pack("<BBHI", 1, key, len(p), zlib.crc32(p)) + bytes(b ^ key for b in p)


def xz_raw(b):
    return subprocess.run(["xz", "--format=raw", "--lzma1=lc=3,lp=0,pb=2,dict=64KiB", "-c"], input=b,
                          capture_output=True, check=True).stdout


W = {"aplib": pkd_aplib_pack.pack, "aplib-ap32": pkd_aplib_pack.pack_ap32, "lznt1": lznt1.compress,
     "lz4block": lambda b: lz4.block.compress(b, store_size=False), "lzma-raw": xz_raw}
Q = {"aplib": "aPLib-decompress", "lznt1": "LZNT1-decompress", "lz4block": "LZ4-block-decompress",
     "lzma-raw": "raw LZMA-decompress (lc=3, lp=0, pb=2, 64 KiB dictionary)"}


def filler(n, seed):
    r = random.Random(seed)
    return b"\x7fELF\x02\x01\x01" + bytes(r.choice(b"\0\0\0\x48\x89\xe5\xc3\x90abc") for _ in range(n - 7))


def overlay(comp, unpacked, key):
    pk = bytes(b ^ key for b in comp)
    return b"RS20" + bytes([2, key, 0, 0]) + struct.pack("<I", len(pk)) + hashlib.sha256(unpacked).digest() + pk


CFGS = {
    "aplib": {"c2": "198.51.100.40:443", "campaign": "ap-squeeze", "mutex": "Global\\APL_0001",
              "flag": "flag{ap_l1b_d3p4ck}", "pad": "ABABABABABABABABABABABAB0000000000"},
    "lznt1": {"c2": "203.0.113.91:8080", "campaign": "nt-chunks", "sleep": 30, "flag": "flag{lznt1_rtl_buf}",
              "pad": "xyzxyzxyzxyzxyzxyzxyzxyzxyz"},
    "lz4block": {"c2": "192.0.2.77:53", "campaign": "lz4-blk", "flag": "flag{lz4_n0_fr4m3}",
                 "pad": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"},
    "lzma-raw": {"c2": "198.51.100.3:4444", "campaign": "raw-lzma1", "flag": "flag{lzm4_r4w_lc3}",
                 "pad": "qwerqwerqwerqwerqwerqwer"},
}


def emit(name, data, meta):
    (HERE / f"{name}.bin").write_bytes(data)
    meta.setdefault("generator_cmd", f"python3 tests/data/binary_fixtures/pkd_gen.py   # writer: {meta.pop('writer')}")
    meta.setdefault("oracle_cmd", f"python3 tests/data/binary_fixtures/pkd_oracle.py {name}")
    (HERE / f"{name}.json").write_text(json.dumps(meta, indent=1) + "\n")


WRITER = {"aplib": "pkd_aplib_pack.pack (own spec-derived packer)", "aplib-ap32": "pkd_aplib_pack.pack_ap32",
          "lznt1": "pip lznt1.compress", "lz4block": "python-lz4 lz4.block.compress(store_size=False)",
          "lzma-raw": "xz --format=raw --lzma1=lc=3,lp=0,pb=2,dict=64KiB"}
for i, (fmt, cfg) in enumerate(CFGS.items()):
    rec = hcfg(cfg, 0x30 + i)
    # 1. bare stream inside a filler binary (packer_hcfg on the stream bytes)
    wfmt = "aplib-ap32" if fmt == "aplib" else fmt
    comp = W[wfmt](rec)
    pre = filler(1024 + 64 * i, i)
    emit(f"pkd_{fmt}_bare", pre + comp + b"\0" * 16,
         {"entry": "packer_hcfg", "encoding": fmt, "stream_offset": len(pre), "stream_length": len(comp),
          "expected_offset": 0, "expected_config": cfg, "decoy": False, "writer": WRITER[wfmt]})
    # 2. RS20 overlay: xor key + sha256(unpacked), question-driven unpack
    key = 0x5A + i
    comp = W[fmt](rec)
    pre = filler(2048, 100 + i)
    q = (f"Find the final RS20 overlay. Read the key u8 at +5, packed length u32le at +8, the 32-byte unpacked SHA-256 "
         f"at +12, and packed bytes at +44. For each packed byte compute byte XOR key; then {Q[fmt]}, verify the "
         f"unpacked SHA-256 and use the HCFG record at unpacked offset 0.")
    data = pre + overlay(comp, rec, key)
    emit(f"pkd_{fmt}_overlay", data,
         {"entry": "overlay_spec+overlay_spec_unpack", "encoding": fmt, "question": q, "expected_offset": len(pre),
          "expected_size": len(data) - len(pre), "expected_config": cfg, "decoy": False, "writer": WRITER[fmt]})
    # 3. decoy: the compressed record with its header crc corrupted (decodes, but no crc-valid HCFG) inside the
    #    overlay with a WRONG sha256 -> both entries must answer "none"
    bad = rec[:8] + struct.pack("<I", 0xDEADBEEF) + rec[12:]
    comp = W[fmt](bad)
    ov = bytearray(overlay(comp, bad, key))
    ov[12:44] = hashlib.sha256(b"not the payload").digest()
    emit(f"pkd_{fmt}_decoy", pre + comp + bytes(ov),
         {"entry": "packer_hcfg+overlay_spec_unpack", "encoding": fmt, "question": q, "stream_offset": len(pre),
          "stream_length": len(comp), "expected_offset": None, "expected_config": "none", "decoy": True,
          "writer": WRITER[fmt], "detail": "HCFG crc forced to 0xdeadbeef + overlay sha256 of other bytes"})
print("ok")
