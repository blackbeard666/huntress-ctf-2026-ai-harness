"""Writer for the layoutq_* fixtures (question-prose header layouts, lib.binary.layout_from_question / layout_field):
synthetic overlays built with stdlib struct + hashlib after an ELF-ish / junk prefix, each paired with its question
text. Expected values come from layoutq_oracle.sh (od / dd / sha256sum), not from lib.binary.
usage (repo root): python3 tests/data/binary_fixtures/layoutq_gen.py"""
import hashlib, json, pathlib, random, struct

D = pathlib.Path(__file__).parent
R = random.Random(2026)
TAIL = " Locate the unique CRC32-valid HCFG record: bytes 0..3 are ASCII HCFG, byte 4 is version, byte 5 is the XOR key."


def hcfg(n):
    body = json.dumps({"campaign": "LQ-%03d" % n, "domain": "n%d.example.invalid" % n}).encode()
    return b"HCFG" + bytes([1, 0x5A]) + struct.pack("<HI", len(body), 0) + bytes(c ^ 0x5A for c in body)


def junk(n):
    return b"\x7fELF\x02\x01\x01" + bytes(R.randrange(256) for _ in range(n - 7))


def put(name, data, question, oracle, decoy=False, note=""):
    (D / (name + ".bin")).write_bytes(data)
    (D / (name + ".json")).write_text(json.dumps({"entry": "layout_from_question+layout_field", "question": question,
                                                  "oracle_args": oracle, "decoy": decoy, "note": note}, indent=1) + "\n")


# 1. D20 RS20 layout verbatim (GM-confirmed shape): +8 u32le hcfg len, +12 u16le scratch len, +16..+47 sha(scratch)
h, s = hcfg(1), bytes(R.randrange(256) for _ in range(37))
hdr = b"RS20" + b"\x01\0\0\0" + struct.pack("<IH", len(h), len(s)) + b"\0\0" + hashlib.sha256(s).digest()
put("layoutq_rs20_d20", junk(3000) + b"RS20 decoy string in rodata" + junk(500) + hdr + h + s,
    "In delivery 1: evidence.zip, Use all d20-- members in ZIP central-directory order. Find the final RS20 overlay. "
    "Read HCFG resource length u32le at +8 and scratch length u16le at +12; bytes +16..+47 are the scratch SHA-256, the "
    "HCFG resource starts at +48, and scratch follows it. Verify exact end bounds and scratch SHA-256, then use the HCFG "
    "resource at offset 0." + TAIL, "RS20 m hcfg_resource_length:8:u32le scratch_length:12:u16le scratch_sha256:16:32 "
    "hcfg_resource:48:hcfg_resource_length scratch:after:scratch_length", note="D20 question text verbatim")

# 2. permuted fields + renamed magic + extra padding: sha first, lengths after it, body at +56
h, s = hcfg(2), bytes(R.randrange(256) for _ in range(90))
hdr = b"QX21" + b"\x02\0\0\0" + hashlib.sha256(s).digest() + struct.pack("<HxxI", len(s), len(h)) + b"\xcc" * 8
put("layoutq_permuted_qx21", junk(4096) + hdr + h + s,
    "Find the final QX21 overlay. Bytes +8..+39 are the scratch SHA-256, read scratch length u16le at +40 and HCFG "
    "resource length u32le at +44; the HCFG resource starts at +56, and scratch follows it. Verify exact end bounds and "
    "scratch SHA-256." + TAIL, "QX21 m scratch_sha256:8:32 scratch_length:40:u16le hcfg_resource_length:44:u32le "
    "hcfg_resource:56:hcfg_resource_length scratch:after:scratch_length", note="permuted + padding")

# 3. big-endian ints, k bytes, u8 count, body / trailer via 'immediately after'
h, tr = hcfg(3), b"TRAILER!" * 3
hdr = b"BE77" + bytes([3, 0x41, 0x99, 2]) + struct.pack(">IH", len(h), len(tr)) + b"\0\0" + hashlib.sha256(h).digest()
put("layoutq_bigendian_be77", junk(2222) + hdr + h + tr,
    "Find the last BE77 trailer. Read k1 at +5, k2 at +6, entry count u8 at +7, payload length u32be at +8, footer "
    "length u16be at +12, and the 32-byte payload SHA-256 at +16. The payload bytes begin at +48 and the footer is "
    "immediately after the payload. Verify exact end bounds." + TAIL,
    "BE77 m k1:5:u8 k2:6:u8 entry_count:7:u8 payload_length:8:u32be footer_length:12:u16be payload_sha256:16:32 "
    "payload:48:payload_length footer:after:footer_length", note="BE ints, 'immediately after'")

# 4. u64le lengths, offsets relative to the file (header at file start, magic renamed)
h = hcfg(4)
pad = b"\0" * 7
hdr = b"HX64v2\0\0" + struct.pack("<QQ", len(h), 7) + hashlib.md5(h).digest()
body_at = len(hdr) + 64
data = hdr + b"\xee" * 64 + h + pad
put("layoutq_u64_filerel_hx64", data,
    "The container begins with magic HX64; offsets are relative to the file. Read config length u64le at +8 and pad "
    "length u64le at +16; the 16-byte config MD5 at +24. The config starts at +%d, and the pad follows it. Verify exact "
    "end bounds." % body_at + TAIL,
    "HX64 f config_length:8:u64le pad_length:16:u64le config_md5:24:16 config:%d:config_length pad:after:pad_length"
    % body_at, note="u64le + relative to the file")

# 5. D19 PK19 header (k1/k2, packed length, stored unpacked sha), packed body to EOF
pk = bytes(R.randrange(256) for _ in range(211))
hdr = b"PK19" + bytes([1, 0x37, 0x6b, 0]) + struct.pack("<I", len(pk)) + hashlib.sha256(b"unpacked").digest()
put("layoutq_pk19_d19", junk(5000) + hdr + pk,
    "In delivery 1: evidence.zip, Use all d19-- members in ZIP central-directory order. Find the final PK19 overlay. "
    "Read k1 at +5, k2 at +6, packed length u32le at +8, the 32-byte unpacked SHA-256 at +12, and packed bytes at +44. "
    "For each packed byte compute ror8(byte XOR k2,3) XOR k1; verify the unpacked SHA-256 and use the HCFG record at "
    "unpacked offset 0." + TAIL, "PK19 m version:4:u8 k1:5:u8 k2:6:u8 packed_length:8:u32le unpacked_sha256:12:32 "
    "packed:44:packed_length", note="D19 question text verbatim")

# 6. DECOY: renamed impostor magic (RS2O) -- the question's RS20 is absent -> every id "none"
h, s = hcfg(6), b"s" * 20
hdr = b"RS2O" + b"\x01\0\0\0" + struct.pack("<IH", len(h), len(s)) + b"\0\0" + hashlib.sha256(s).digest()
put("layoutq_decoy_impostor", junk(3000) + hdr + h + s,
    "Find the final RS20 overlay. Read HCFG resource length u32le at +8 and scratch length u16le at +12; bytes +16..+47 "
    "are the scratch SHA-256, the HCFG resource starts at +48, and scratch follows it. Verify exact end bounds and "
    "scratch SHA-256." + TAIL, "RS20 m hcfg_resource_length:8:u32le scratch_length:12:u16le", decoy=True,
    note="impostor magic RS2O: RS20 absent")

# 7. DECOY: truncated RS20 (length field runs past EOF, bad scratch hash) -> bodies "none", end bounds false
h = hcfg(7)
hdr = b"RS20" + b"\x01\0\0\0" + struct.pack("<IH", len(h) + 900, 64) + b"\0\0" + b"\x11" * 32
put("layoutq_decoy_truncated", junk(3000) + hdr + h,
    "Find the final RS20 overlay. Read HCFG resource length u32le at +8 and scratch length u16le at +12; bytes +16..+47 "
    "are the scratch SHA-256, the HCFG resource starts at +48, and scratch follows it. Verify exact end bounds and "
    "scratch SHA-256." + TAIL, "RS20 m hcfg_resource_length:8:u32le scratch_length:12:u16le scratch_sha256:16:32 "
    "hcfg_resource:48:hcfg_resource_length", decoy=True, note="truncated: declared resource runs past EOF")
