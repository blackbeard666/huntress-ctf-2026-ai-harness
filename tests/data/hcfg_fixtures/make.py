#!/usr/bin/env python3
"""Generate the HCFG storage-encoding fixtures for lib.binary.hcfg_scan (tests/test_day14_s4.py). Stdlib only.

Each fixture = a small ELF-looking container (ELF64 header + seeded filler: code-ish bytes, C strings, zero padding)
with one synthesized HCFG blob stored in ONE encoding at a known file offset. The blob layout follows the real lane
artifacts (verified against challenges/day12 + day13 evidence.zip members):
    b'HCFG' | u8 version | u8 xor_key | u16 len (LE) | u32 crc32(plain JSON) (LE) | plain JSON ^ xor_key
Expected values (offset, encoding, key, version, crc, config) come from THIS generator, never from the scanner.
Offset law: raw -> the 'H' of the magic; every other encoding -> first byte of the stored encoded form (see
lib/binary.py OFFSET LAW). Decoy fixtures (bad crc, truncated, wrong magic) carry "valid": false entries.

Run:  python3 tests/data/hcfg_fixtures/make.py [outdir]     (default: this directory; deterministic output)
"""
import base64
import json
import random
import struct
import sys
import zlib
from pathlib import Path

SIZE = 4096


def config(i):
    tag = f"BR14-{i:03d}"
    return {"campaign": tag, "domain": f"node-{i:03d}.day14.example.invalid", "ipv4": f"198.51.100.{10 + i}",
            "url": f"https://node-{i:03d}.day14.example.invalid/api/{tag}", "mutex": f"Global\\HuntressBR14_{i:03d}",
            "service": f"HuntressLab-Day14-{i:03d}"}


def blob(cfg, key, ver=1, crc_delta=0, magic=b"HCFG"):
    plain = json.dumps(cfg, separators=(",", ":")).encode()
    body = bytes(b ^ key for b in plain)
    return magic + struct.pack("<BBHI", ver, key, len(plain), (zlib.crc32(plain) + crc_delta) & 0xFFFFFFFF) + body


def container(seed):
    """ELF64 x86-64 header + filler that looks like a binary (code bytes, strings, zero runs)."""
    r = random.Random(seed)
    hdr = b"\x7fELF\x02\x01\x01" + bytes(9) + struct.pack("<HHIQQQIHHHHHH", 2, 62, 1, 0x401000, 64, 0, 0, 64, 56, 0,
                                                            64, 0, 0)
    out = bytearray(hdr)
    words = [b"main", b"config", b"decode", b"runtime", b"GLIBC_2.34", b".rodata", b"error: %s\n", b"init"]
    while len(out) < SIZE:
        k = r.random()
        if k < 0.5:
            out += bytes(r.choice((0x48, 0x89, 0x8b, 0xe8, 0xc3, 0x55, 0x5d, 0x0f, 0x1f, 0x44)) if r.random() < .6
                         else r.randrange(256) for _ in range(r.randrange(8, 48)))
        elif k < 0.8:
            out += r.choice(words) + b"\0"
        else:
            out += bytes(r.randrange(4, 32))
    return out[:SIZE]


def wide(s, be=False):
    return b"".join((b"\0" + bytes([c])) if be else (bytes([c]) + b"\0") for c in s)


def xor(b, k):
    return bytes(c ^ k for c in b)


def deflate(b, wbits, level=6, strategy=zlib.Z_DEFAULT_STRATEGY):
    c = zlib.compressobj(level, zlib.DEFLATED, wbits, 8, strategy)
    return c.compress(b) + c.flush()


def hexsep(b, sep, pre=""):
    return sep.join(f"{pre}{c:02x}" for c in b).encode()


# name -> (encoding expected from the scanner, stored bytes builder(blob) -> bytes, lead bytes before the stored form)
ENCODINGS = {
    "raw": ("raw", lambda b: b),
    "base64": ("base64", base64.b64encode),
    "base64_mime": ("base64", lambda b: base64.encodebytes(b).rstrip(b"\n")),   # 76-col newline-wrapped
    "base64url": ("base64url", lambda b: base64.urlsafe_b64encode(b).rstrip(b"=")),
    "hex_lower": ("hex", lambda b: b.hex().encode()),
    "hex_upper": ("hex", lambda b: b.hex().upper().encode()),
    "hex_space": ("hex-sep", lambda b: hexsep(b, " ")),
    "hex_colon": ("hex-sep", lambda b: hexsep(b, ":")),
    "hex_escape": ("hex-sep", lambda b: hexsep(b, "", "\\x")),
    "hex_carray": ("hex-sep", lambda b: hexsep(b, ", ", "0x")),
    "base32": ("base32", base64.b32encode),
    "base32_lower": ("base32", lambda b: base64.b32encode(b).lower().rstrip(b"=")),
    "base85": ("base85", base64.b85encode),
    "ascii85": ("ascii85", base64.a85encode),
    "ascii85_adobe": ("ascii85", lambda b: base64.a85encode(b, adobe=True)),
    "utf16le_raw": ("utf16le-raw", lambda b: wide(b)),
    "utf16be_raw": ("utf16be-raw", lambda b: wide(b, True)),
    "utf16le_base64": ("utf16le-base64", lambda b: wide(base64.b64encode(b))),
    "utf16be_base64": ("utf16be-base64", lambda b: wide(base64.b64encode(b), True)),
    "utf16le_hex": ("utf16le-hex", lambda b: wide(b.hex().encode())),
    "utf16le_base32": ("utf16le-base32", lambda b: wide(base64.b32encode(b))),
    "reversed_raw": ("reversed-raw", lambda b: b[::-1]),
    "reversed_base64": ("reversed-base64", lambda b: base64.b64encode(b)[::-1]),
    "xor_base64": ("xor-base64", lambda b: xor(base64.b64encode(b), 0x5A)),
    "xor_raw": ("xor-raw", lambda b: xor(b, 0xC3)),
    "zlib6": ("zlib", lambda b: deflate(b, 15)),
    "zlib9": ("zlib", lambda b: deflate(b, 15, 9)),
    "zlib1": ("zlib", lambda b: deflate(b, 15, 1)),
    "gzip": ("gzip", lambda b: deflate(b, 31)),
    "zlib_inside": ("zlib", lambda b: deflate(b"RSRC" + bytes(range(256)) * 2 + b, 15)),   # blob 516 B into the stream
    "deflate_raw": ("deflate", lambda b: deflate(b, -15)),
    "deflate_fixed": ("deflate", lambda b: deflate(b, -15, 6, zlib.Z_FIXED)),
}


def build():
    """{filename: bytes}, expected list -- deterministic."""
    files, expected = {}, []
    for i, (name, (enc, fn)) in enumerate(ENCODINGS.items()):
        r = random.Random(1000 + i)
        cfg, key = config(i), r.randrange(1, 256)
        data = container(i)
        stored = fn(blob(cfg, key))
        off = r.randrange(512, 1024)
        if enc.startswith("utf16"):
            off &= ~1   # wide strings are 2-byte aligned (the scanner's LE/BE tie-break relies on it)
        lead = b"\0" if enc.startswith(("utf16", "base", "hex", "ascii", "reversed-base")) else b""
        data[off - len(lead):off] = lead               # text sits NUL-delimited, like a C/rodata string literal
        data[off:off + len(stored)] = stored
        data[off + len(stored):off + len(stored) + 2] = b"\0\0"
        fname = f"{name}.bin"
        files[fname] = bytes(data)
        plain = json.dumps(cfg, separators=(",", ":")).encode()
        expected.append({"file": fname, "valid": True, "encoding": enc, "offset": off, "key": key, "version": 1,
                         "crc": zlib.crc32(plain), "config": cfg})
    # decoys: the scanner must not take these as THE blob
    n = len(ENCODINGS)
    cfg = config(n)
    good = blob(cfg, 0x81)
    plain = json.dumps(cfg, separators=(",", ":")).encode()
    d = container(n)   # bad-crc raw decoy BEFORE the real base64 blob (D9 Nim shape)
    d[600:600 + len(good)] = blob(config(n + 1), 0x81, crc_delta=1)
    real = base64.b64encode(good)
    d[1400:1400 + len(real)] = real
    files["decoy_badcrc_then_base64.bin"] = bytes(d)
    expected.append({"file": "decoy_badcrc_then_base64.bin", "valid": True, "encoding": "base64", "offset": 1400,
                     "key": 0x81, "version": 1, "crc": zlib.crc32(plain), "config": cfg,
                     "decoys": [{"offset": 600, "encoding": "raw"}]})
    d = container(n + 2)   # magic text only (assert message), truncated raw blob, wrong magic -> nothing valid
    d[500:540] = b'assert b[0 .. 3] == "HCFG"\0'.ljust(40, b"\0")
    t = blob(cfg, 0x42)
    d[800:800 + 60] = t[:60]
    d[1500:1500 + len(t)] = blob(cfg, 0x42, magic=b"HCFX")
    files["decoy_none.bin"] = bytes(d)
    expected.append({"file": "decoy_none.bin", "valid": False})
    d = container(n + 3)   # bad-crc zlib stream decoy before a real hex-sep blob
    z = deflate(blob(cfg, 0x33, crc_delta=7), 15)
    d[520:520 + len(z)] = z
    h = hexsep(good, " ")
    d[1100:1100 + len(h)] = h
    files["decoy_zlib_then_hexsep.bin"] = bytes(d)
    expected.append({"file": "decoy_zlib_then_hexsep.bin", "valid": True, "encoding": "hex-sep", "offset": 1100,
                     "key": 0x81, "version": 1, "crc": zlib.crc32(plain), "config": cfg,
                     "decoys": [{"offset": 520, "encoding": "zlib"}]})
    return files, expected


def main(out=None):
    out = Path(out or Path(__file__).resolve().parent)
    files, expected = build()
    for name, b in files.items():
        (out / name).write_bytes(b)
    (out / "expected.json").write_text(json.dumps(expected, indent=1) + "\n")
    return out


if __name__ == "__main__":
    print(main(sys.argv[1] if len(sys.argv) > 1 else None))
