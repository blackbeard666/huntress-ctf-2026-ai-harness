"""Independent hand-written DECODERS (stdlib; reads the puzzle JSON on stdin) for the declared-pipeline fixtures."""
import base64, json, re, sys

variant, p = sys.argv[1], json.load(sys.stdin)
if variant == "three_step":
    b = bytes.fromhex(p["data"])
    out = bytes((x - 7 - 3 * i) & 255 for i, x in enumerate(b))[::-1].decode()
elif variant == "encoder_order":
    x = base64.b32decode(p["data"])
    r = bytes(b ^ b"k3y"[i % 3] for i, b in enumerate(x))[::-1]
    out = "".join(chr(65 + (c - 65 - 5) % 26) if 65 <= c <= 90 else chr(c) for c in r)
else:
    mid = json.loads(base64.b64decode(p["data"]))
    a = base64.b64decode(mid["data"])
    core = json.loads(base64.b64decode(bytes(x ^ ((12 + i) & 255) for i, x in enumerate(a))))
    slots = [None] * 3
    for i, pos in enumerate(core["order"]):
        slots[pos] = core["parts"][i]
    out = "".join(slots)
print(out if re.fullmatch(r"ANS-[0-9A-F]{16}", out) else "NOT-A-TOKEN:" + out)
