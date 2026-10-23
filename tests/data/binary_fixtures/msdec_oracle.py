"""Independent oracle for msdec_* fixtures (no lib.*): expected_config from the PROGRAM'S OWN stdout (<name>.plain, written
by msdec_gen.sh running `dotnet app.dll` / `java A`) -> base64 -> struct HCFG header + zlib.crc32 + json; expected_offset
= bytes.find of the ciphertext the generator stored (re-enciphered here from that output with the generator's recipe):
UTF-16LE #US chars (C#/VB ldstr), raw FieldRVA bytes (C# byte[]), CONSTANT_Utf8 bytes (javac).
usage: python3 -I msdec_oracle.py DIR [name...]   -> prints {name: {expected_offset, expected_config, crc_ok}}"""
import base64, json, struct, sys, zlib, pathlib

K4, K5 = (0x13, 0x37, 0x42, 0x99), (0x21, 0x4F, 0x0D, 0x6B, 0x17)
RECIPE = {
    "cs_b64xor": lambda t: base64.b64encode(bytes(c ^ K4[i % 4] for i, c in enumerate(t))).decode().encode("utf-16-le"),
    "decoy_cs_badcrc": lambda t: base64.b64encode(bytes(c ^ K4[i % 4] for i, c in enumerate(t))).decode().encode("utf-16-le"),
    "cs_bytes": lambda t: bytes(c ^ ((i * 7 + 0x33) & 255) for i, c in enumerate(t)),
    "vb_chrw": lambda t: bytes(c + 3 for c in t).decode().encode("utf-16-le"),
    "java_xor": lambda t: b"".join(bytes([c ^ K5[i % 5]]) if c ^ K5[i % 5] else b"\xc0\x80" for i, c in enumerate(t)),
}
d = pathlib.Path(sys.argv[1])
out = {}
for name in sys.argv[2:] or RECIPE:
    text = (d / f"msdec_{name}.plain").read_bytes().strip()
    blob = base64.b64decode(text)
    ver, key, n, crc = struct.unpack_from("<BBHI", blob, 4)
    plain = bytes(b ^ key for b in blob[12:12 + n])
    ok = blob[:4] == b"HCFG" and zlib.crc32(plain) == crc
    data = (d / f"msdec_{name}.bin").read_bytes()
    out[name] = {"expected_offset": data.find(RECIPE[name](text)), "expected_config": json.loads(plain) if ok else None,
                 "crc_ok": ok}
print(json.dumps(out, indent=1))
