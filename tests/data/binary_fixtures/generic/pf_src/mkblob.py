"""Independent HCFG writer (stdlib zlib.crc32): python3 mkblob.py <campaign> <key-hex> > blob.h"""
import json, struct, sys, zlib
camp, key = sys.argv[1], int(sys.argv[2], 16)
cfg = json.dumps({"campaign": camp, "domain": "node-%s.day31.example.invalid" % camp[-3:].lower(),
                  "mutex": "Global\\HuntressPF_" + camp[-3:]}, separators=(",", ":")).encode()
rec = b"HCFG" + struct.pack("<BBHI", 1, key, len(cfg), zlib.crc32(cfg)) + bytes(c ^ key for c in cfg)
print("__attribute__((used)) static const unsigned char hcfg_blob[%d] = {%s};" % (len(rec), ",".join(map(str, rec))))
