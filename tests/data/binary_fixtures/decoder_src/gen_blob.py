# usage: gen_blob.py <form> <key> <arg>  -> C initializer for the stored HCFG blob (stdlib zlib/json; independent of lib.binary)
import sys, json, zlib, struct
form, key, arg = sys.argv[1], int(sys.argv[2], 0), int(sys.argv[3], 0)
plain = json.dumps({"c2": "decoder.hctf.example", "port": 8443, "id": "dec-" + form}, separators=(",", ":")).encode()
blob = b"HCFG" + struct.pack("<BBHI", 1, key, len(plain), zlib.crc32(plain)) + bytes(b ^ key for b in plain)
if form == "add":   stored = bytes((b + arg) % 256 for b in blob)
elif form == "rol": stored = bytes(((b << arg) | (b >> (8 - arg))) & 255 for b in blob)
elif form == "roll": stored = bytes(b ^ ((arg + j) & 255) for j, b in enumerate(blob))
else: stored = blob
print("#define BLOB_LEN %d" % len(stored)); print("#define BODY_LEN %d" % len(plain))
print("const unsigned char hcfg_blob[BLOB_LEN] = {" + ",".join(str(b) for b in stored) + "};")
