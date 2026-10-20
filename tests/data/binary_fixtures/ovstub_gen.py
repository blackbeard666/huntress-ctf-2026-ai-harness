"""Generate the ovstub_* fixtures (offline): gcc-built stub hosts (ovstub_host.c) + a D19-layout overlay written here
with stdlib only (struct/hashlib/zlib); the packed bytes = the inverse of the stub's per-byte decode table.
usage (repo root): python3 tests/data/binary_fixtures/ovstub_gen.py"""
import hashlib, json, pathlib, struct, subprocess, sys, tempfile, zlib

HERE = pathlib.Path(__file__).resolve().parent
rol8 = lambda x, r: ((x << r) | (x >> (8 - r))) & 255
ror8 = lambda x, r: ((x >> r) | (x << (8 - r))) & 255
CASES = {   # name: (magic, k1, k2, C expression for the host, Python decode(p, k1, k2), cflags, config, corrupt_hash)
    "ovstub_o2_xor_add_rol": ("PK19", 0x5a, 0xc3, "rol8((uint8_t)((p ^ k2) + 0x3d), 5) ^ k1",
                              lambda p, k1, k2: rol8(((p ^ k2) + 0x3d) & 255, 5) ^ k1, "-O2",
                              {"campaign": "OS19-STB", "domain": "stub.example.net", "mutex": "Global\\ovstub-a",
                               "url": "https://stub.example.net/a"}, False),
    "ovstub_o1_sub_ror_mutmagic": ("QX27", 0x91, 0x2e, "ror8((uint8_t)(p - k1), 2) ^ 0xa7 ^ k2",
                                   lambda p, k1, k2: ror8((p - k1) & 255, 2) ^ 0xa7 ^ k2, "-O1",
                                   {"campaign": "QX27-MUT", "domain": "mut.example.org", "mutex": "Local\\qx27",
                                    "url": "http://mut.example.org/b"}, False),
    "ovstub_nostub_family": ("PK19", 0x11, 0x6b, None,
                             lambda p, k1, k2: (ror8((p + k1) & 255, 5) + k2) & 255, "-O2 -DNOSTUB",
                             {"campaign": "NS19-FAM", "domain": "fam.example.com", "mutex": "nostub-mutex",
                              "url": "https://fam.example.com/c"}, False),
    "ovstub_decoy_badhash": ("PK19", 0x5a, 0xc3, "rol8((uint8_t)((p ^ k2) + 0x3d), 5) ^ k1",
                             lambda p, k1, k2: rol8(((p ^ k2) + 0x3d) & 255, 5) ^ k1, "-O2",
                             {"campaign": "DECOY", "domain": "decoy.example.net", "mutex": "decoy",
                              "url": "https://decoy.example.net/"}, True),
}


def hcfg(cfg, key=0x4d, ver=1):
    plain = json.dumps(cfg, separators=(",", ":")).encode()
    return b"HCFG" + struct.pack("<BBHI", ver, key, len(plain), zlib.crc32(plain)) + bytes(b ^ key for b in plain)


for name, (magic, k1, k2, cx, dec, cflags, cfg, bad) in CASES.items():
    with tempfile.TemporaryDirectory() as td:
        exe = pathlib.Path(td) / "host"
        m = struct.unpack("<I", magic.encode())[0]
        cmd = ["gcc", *cflags.split(), "-s", f"-DMAGIC={m:#x}u", f"-DXFORM={cx or 'p'}", "-o", str(exe),
               str(HERE / "ovstub_host.c")]
        subprocess.run(cmd, check=True)
        host = exe.read_bytes()
    out = hcfg(cfg)
    table = [dec(p, k1, k2) for p in range(256)]
    assert sorted(table) == list(range(256)), name
    inv = {u: p for p, u in enumerate(table)}
    pk = bytes(inv[u] for u in out)
    sha = hashlib.sha256(out).digest()
    if bad:
        sha = bytes([sha[0] ^ 1]) + sha[1:]
    blob = host + magic.encode() + bytes([1, k1, k2, 0]) + struct.pack("<I", len(pk)) + sha + pk
    (HERE / f"{name}.bin").write_bytes(blob)
    print(name, len(host), len(blob))
