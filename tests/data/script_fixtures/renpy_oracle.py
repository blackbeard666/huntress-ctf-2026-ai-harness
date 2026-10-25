"""Independent oracle for the renpy_* fixtures: stdlib pickle.loads (with a find_class stub that records class names) on
the RPA index, pickletools.genops for the .rpyc string literals; finds the descriptor hex and prints the decoded plan,
or 'none'. Usage: python3 -I renpy_oracle.py <fixture.json>"""
import base64
import json
import pickle
import pickletools
import re
import struct
import sys
import zlib


def rpyc_strings(b):
    if b[:10] != b"RENPY RPC2":
        return []
    slot, start, ln = struct.unpack_from("<III", b, 10)
    d = zlib.decompress(b[start:start + ln])
    return [a for op, a, _ in pickletools.genops(d) if isinstance(a, str) and op.name.endswith("UNICODE")]


def texts(b):
    m = re.match(rb"RPA-(3\.0|2\.0) ([0-9a-f]{16})(?: ([0-9a-f]{8}))?\n", b)
    if m:
        off, key = int(m.group(2), 16), int(m.group(3) or b"0", 16)
        for name, ents in pickle.loads(zlib.decompress(b[off:])).items():
            o, ln, pre = ents[0]
            data = pre + b[o ^ key:(o ^ key) + (ln ^ key) - len(pre)]
            yield from (rpyc_strings(data) if name.endswith(".rpyc") else [data.decode("utf-8", "ignore")])
    yield from rpyc_strings(b)


fx = json.load(open(sys.argv[1]))
found = "none"
for t in texts(base64.b64decode(fx["material"])):
    for h in re.findall(r"[0-9a-f]{40,}", t):
        p = bytes.fromhex(h).decode()
        if p.startswith("v=3|"):
            found = p
print(found)
