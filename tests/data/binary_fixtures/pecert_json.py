"""Wrap pecert_oracle.py output into the fixture json: python3 pecert_json.py <file.bin> <decoy 0|1> < oracle.json"""
import json, struct, sys, zlib
p, decoy = sys.argv[1], sys.argv[2] == "1"
facts = json.load(sys.stdin)
data = open(p, "rb").read()
h = int(facts["hcfg_offset"]) if facts["hcfg_offset"] != "none" else None
cfg = None
if h is not None:   # stdlib header parse: magic, ver u8, key u8, len u16le, crc u32le, body
    _, _, n, crc = struct.unpack_from("<BBHI", data, h + 4)
    body = data[h + 12:h + 12 + n]
    assert zlib.crc32(body) == crc
    cfg = json.loads(body)
name = p.rsplit("/", 1)[-1]
print(json.dumps({"family": "pe_certificate", "encoding": "raw" if h is not None else "none", "expected_offset": h,
                  "expected_config": cfg, "decoy": decoy, "expected_facts": facts,
                  "generator_cmd": "bash pecert_gen.sh   # zig cc -target x86_64-windows-gnu (MinGW PE32+) of pecert_src.c; "
                  "openssl req -x509 + openssl cms -sign -outform DER (detached PKCS#7 SignedData); pecert_asm.py = "
                  "pefile writer (Security dir VirtualAddress = FILE offset, CheckSum = generate_checksum or stale 0x1234)",
                  "oracle_cmd": f".venv/bin/python pecert_oracle.py {name}   # pefile get_overlay_data_start_offset / "
                  "DATA_DIRECTORY[SECURITY] / generate_checksum+verify_checksum, openssl asn1parse (DER len), struct "
                  "WIN_CERTIFICATE walk; config = stdlib struct+crc32+json of the blob",
                  "note": "lib.binary.pe_cert_field(data, key) per expected_facts key; hcfg_scan raw hit at "
                  "expected_offset (decoy: no cert fields; badptr: no HCFG at all)"}, indent=1))
