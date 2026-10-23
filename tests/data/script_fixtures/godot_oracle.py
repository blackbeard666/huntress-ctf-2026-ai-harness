"""Independent READER for the godot_* fixtures (stdlib only, no lib.*): prints the decoded plan of a fixture file.
.pck: struct-walks the GDPC directory (v1 absolute offsets, v2 file_base-relative) and checks each member's md5;
.tscn/.tres: `script/source` literal via ast.literal_eval of the quoted body (Godot escapes are a subset of Python's);
.gdc: un-XORs the identifier table and reads the STRING constants; then the DESCRIPTOR hex -> bytes.fromhex.
Usage: python3 -I godot_oracle.py <file>"""
import ast
import hashlib
import re
import struct
import sys


def pck(b):
    ver = struct.unpack_from("<I", b, 4)[0]
    pos, base = (84, 0) if ver == 1 else (96, struct.unpack_from("<Q", b, 24)[0])
    n = struct.unpack_from("<I", b, pos)[0]
    pos += 4
    for _ in range(n):
        ln = struct.unpack_from("<I", b, pos)[0]
        path = b[pos + 4:pos + 4 + ln].rstrip(b"\0").decode()
        pos += 4 + ln
        off, size = struct.unpack_from("<QQ", b, pos)
        data = b[base + off:base + off + size]
        assert hashlib.md5(data).digest() == b[pos + 16:pos + 32], path
        pos += 32 + (4 if ver != 1 else 0)
        yield path, data


def source(text):
    m = re.search(r'script/source = ("(?:[^"\\]|\\.)*")', text, re.S)
    return ast.literal_eval('"""%s"""' % m.group(1)[1:-1]) if m else text


def plan(text):
    m = re.search(r'DESCRIPTOR_\w+: String = "([0-9a-f]+)"', text) or re.search(r'"([0-9a-f]{64,})"', text)
    return bytes.fromhex(m.group(1)).decode() if m else None


b = open(sys.argv[1], "rb").read()
if b[:4] == b"GDPC":
    print(next(filter(None, (plan(source(d.decode())) for p, d in pck(b) if p.endswith((".gd", ".tscn")))), None))
elif b[:4] == b"GDSC":                         # Godot 3 v13: 5 x u32 header, identifiers u32 len + XOR 0xb6 bytes
    ni, nc = struct.unpack_from("<II", b, 8)
    pos, ids = 24, []
    for _ in range(ni):
        ln = struct.unpack_from("<I", b, pos)[0]
        ids.append(bytes(c ^ 0xB6 for c in b[pos + 4:pos + 4 + ln]).rstrip(b"\0").decode())
        pos += 4 + ln
    strs = []
    for _ in range(nc):                            # STRING variants: u32 type 4, u32 len, utf-8, pad 4
        t, ln = struct.unpack_from("<II", b, pos)
        assert t == 4
        strs.append(b[pos + 8:pos + 8 + ln].decode())
        pos += 8 + ln + (-ln % 4)
    d = next(i for i in ids if i.startswith("DESCRIPTOR_"))
    print(plan("%s: String = \"%s\"" % (d, max(strs, key=len))))
elif b[:2] == b"GD":                           # GD-prefixed impostor (wrong pack magic): no pack
    print("none")
else:
    print(plan(source(b.decode())))
