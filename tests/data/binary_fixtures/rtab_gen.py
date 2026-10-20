"""Writer for the rtab_* fixtures (multi-entry resource-table overlays, lib.binary.resource_table_field): a gcc-built
stripped ELF + an appended table (magic, count, N fixed-size entries {name / type, offset, size, digest}, data) built
with stdlib struct/hashlib/zlib. Expected values come from rtab_oracle.sh (od / dd / sha256sum / md5sum / gzip), not
from lib.binary. usage (repo root): python3 tests/data/binary_fixtures/rtab_gen.py"""
import hashlib, json, pathlib, random, struct, subprocess, tempfile, zlib

D = pathlib.Path(__file__).parent
R = random.Random(2126)


def elf():
    with tempfile.TemporaryDirectory() as t:
        c = pathlib.Path(t) / "r.c"
        c.write_text('#include <stdio.h>\nint main(void){puts("resource table host");return 0;}\n')
        subprocess.run(["gcc", "-O2", "-s", "-o", t + "/r", str(c)], check=True)
        return (pathlib.Path(t) / "r").read_bytes()


def hcfg(n, good=True):
    body = json.dumps({"campaign": "RT-%03d" % n, "c2": "rt%d.example.invalid" % n}).encode()
    crc = zlib.crc32(body) ^ (0 if good else 0x1337)
    return b"HCFG" + bytes([1, 0x33]) + struct.pack("<HI", len(body), crc) + bytes(c ^ 0x33 for c in body)


def rnd(n):
    return bytes(R.randrange(256) for _ in range(n))


ICON = b"\x89PNG\r\n\x1a\n" + rnd(40)


def put(name, data, oracle, decoy=False, note=""):
    (D / (name + ".bin")).write_bytes(data)
    (D / (name + ".json")).write_text(json.dumps({"entry": "resource_table_field", "oracle_args": oracle,
                                                  "decoy": decoy, "note": note}, indent=1) + "\n")


E = elf()
# 1. RT21: +4 u8 version, +6 u16le count, entries at +8, 52 bytes {name[8] NUL-padded, type u32le, offset u32le
#    (relative to the overlay), size u32le, sha256[32]}; entry 0 = decoy HCFG with a wrong sha256
res = [(b"HCFG", 1, hcfg(1), False), (b"HCFG", 1, hcfg(2), True), (b"scratch", 7, rnd(29), True),
       (b"icon", 3, ICON, True)]
hdr = 8 + 52 * len(res)
tab, blob = b"", b""
for nm, ty, body, ok in res:
    dg = hashlib.sha256(body).digest() if ok else hashlib.sha256(body + b"x").digest()
    tab += nm.ljust(8, b"\0") + struct.pack("<III", ty, hdr + len(blob), len(body)) + dg
    blob += body
put("rtab_rt21_nul8_sha256", E + b"RT21" + bytes([1, 0]) + struct.pack("<H", len(res)) + tab + blob,
    "RT21 overlay 6:u16le 8 52 name:0:nul8 type:8:u32le offset:12:u32le size:16:u32le sha256:20:32",
    note="4 entries; decoy HCFG first (bad sha256), selected = index 1")

# 2. RX22: +4 u32le count, entries at +12 (pad +8), 24 bytes {u8 length + name (11 bytes), offset u32le relative to
#    the FILE, size u32le, crc32 u32le}; decoy HCFG entry's table crc verifies but its HCFG record crc does not
o = len(E)
res = [(b"scratch", rnd(17)), (b"HCFG", hcfg(3, good=False)), (b"HCFG", hcfg(4))]
hdr = 12 + 24 * len(res)
tab, blob = b"", b""
for nm, body in res:
    tab += (bytes([len(nm)]) + nm).ljust(12, b"\0") + struct.pack("<III", o + hdr + len(blob), len(body),
                                                                  zlib.crc32(body))
    blob += body
put("rtab_rx22_pascal_crc_filerel", E + b"RX22" + struct.pack("<I", len(res)) + b"\0" * 4 + tab + blob,
    "RX22 file 4:u32le 12 24 name:0:pascal offset:12:u32le size:16:u32le crc32:20:u32le",
    note="3 entries, file-relative offsets, pascal names; HCFG#1 has a bad record crc -> selected = index 2")

# 3. RQ23: 5 entries, +5 u8 count, entries at +8, 32 bytes {name[8], size u32le, offset u32le, md5[16]}, size BEFORE
#    offset, data in a different order than the table
res = [(b"icon", ICON), (b"strings", rnd(33)), (b"HCFG", hcfg(5, good=False)), (b"scratch", rnd(64)),
       (b"HCFG", hcfg(6))]
hdr = 8 + 32 * len(res)
order = [3, 0, 4, 1, 2]
pos, blob = {}, b""
for i in order:
    pos[i] = hdr + len(blob)
    blob += res[i][1]
tab = b"".join(nm.ljust(8, b"\0") + struct.pack("<II", len(b), pos[i]) +
               (hashlib.md5(b).digest() if i != 2 else hashlib.md5(b"x").digest()) for i, (nm, b) in enumerate(res))
put("rtab_rq23_md5_sizefirst", E + b"RQ23" + bytes([2, len(res), 0, 0]) + tab + blob,
    "RQ23 overlay 5:u8 8 32 name:0:nul8 size:8:u32le offset:12:u32le md5:16:16",
    note="5 entries, size before offset, data out of table order; decoy HCFG idx 2 (bad md5 AND bad record crc)")

# 4. decoy: RT21 header + table whose every digest is wrong (no entry verifies) -> no table
res = [(b"HCFG", hcfg(7)), (b"scratch", rnd(20))]
hdr = 8 + 52 * len(res)
tab, blob = b"", b""
for nm, body in res:
    tab += nm.ljust(8, b"\0") + struct.pack("<III", 1, hdr + len(blob), len(body)) + hashlib.sha256(b"z" + body).digest()
    blob += body
put("rtab_decoy_badhash", E + b"RT21" + bytes([1, 0]) + struct.pack("<H", 2) + tab + blob, "none", decoy=True,
    note="every stored sha256 wrong: not a verified table -> every field 'none'")

# 5. decoy: plain ELF, a 'RT21' string in a trailing comment, no table
put("rtab_decoy_plain", E + b"RT21 resource table not present\n", "none", decoy=True, note="no table")
