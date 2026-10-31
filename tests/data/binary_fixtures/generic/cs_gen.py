"""Writer for the cross-group-campaign-correlation fixtures (stdlib zipfile/struct/zlib/json only; no lib.binary).
Members carry a raw `HCFG`/`HGRF` record (u8 ver, u8 xor, u16le len, u32le crc32 of the plain JSON, xor'd JSON)."""
import json, struct, sys, zipfile, zlib


def rec(magic, cfg, key):
    p = json.dumps(cfg, separators=(",", ":")).encode()
    return magic + struct.pack("<BBHI", 1, key, len(p), zlib.crc32(p)) + bytes(x ^ key for x in p)


def cfg(c, d, m):
    return {"campaign": c, "domain": d, "url": f"https://{d}/api/{c}", "mutex": m, "host_model": "analysis"}


ELF = b"\x7fELF\x02\x01\x01" + b"\0" * 57 + b"code" * 64
PE = b"MZ" + b"\0" * 126 + b"stub" * 32
NEKO = b"NEKO" + b"\0" * 60 + b"bytecode" * 16
members = [
    ("d01--sample.elf", ELF + rec(b"HCFG", cfg("BR01-111", "node-1.day01.example.invalid", "Global\\M01"), 0x21)),
    ("d02--sample.elf", ELF + rec(b"HCFG", cfg("BR01-111", "node-1.day01.example.invalid", "Global\\M02"), 0x33)),
    ("d03--sample-loader.elf", ELF + b"no config here"),
    ("d03--sample-plugin.elf", ELF + rec(b"HCFG", cfg("BR03-333", "node-3.day03.example.invalid", "Global\\M03"), 0x5a)),
    ("d04--sample-family-a.elf", ELF + rec(b"HCFG", cfg("BR04-444", "node-4.day04.example.invalid", "Global\\M04"), 0x11)),
    ("d04--sample-family-b.elf", ELF + rec(b"HCFG", cfg("BR04-444", "node-4.day04.example.invalid", "Global\\M04"), 0x12)),
    ("d04--sample-false-friend.elf", ELF + rec(b"HCFG", cfg("FF04-999", "ff.day04.example.invalid", "Global\\F04"), 0x13)),
    ("d05--sample-config.n", NEKO + rec(b"HGRF", {"campaign_id": "DAY05-000", "this_role": "config",
                                                  "config": cfg("BR05-555", "node-5.day05.example.invalid",
                                                                "Global\\M05")}, 0x6b)),
]
out = sys.argv[1]
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for n, b in members:
        z.writestr(n, b)
with zipfile.ZipFile(sys.argv[2], "w", zipfile.ZIP_DEFLATED) as z:   # decoy: ONE day only, no cross-group set
    for n, b in members[:1]:
        z.writestr(n, b)
