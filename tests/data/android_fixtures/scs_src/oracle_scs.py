"""Independent DECODER for the stacked-v1-codec fixtures: reads the puzzle JSON from stdin (`unzip -p <apk>
assets/huntress_puzzle.json`) and undoes the variant's stack step by step (stdlib only, no lib.android)."""
import base64, json, re, sys

variant, p = sys.argv[1], json.load(sys.stdin)
d, key = p["data"], p["key"]
if variant == "b85_add2i_rev":
    b = base64.b85decode(d)
    out = bytes((x + key + 2 * i) & 255 for i, x in enumerate(b))[::-1]
elif variant == "hex_xorkeyi_b64":
    b = bytes.fromhex(d)
    out = base64.b64decode(bytes(x ^ ((key ^ i) & 255) for i, x in enumerate(b)))
elif variant == "b32_swap_keystr_rev":
    b = base64.b32decode(d + "=" * (-len(d) % 8))
    b = bytes(b[i ^ 1] if (i ^ 1) < len(b) else b[i] for i in range(len(b)))
    ks = str(key).encode()
    out = bytes(x ^ ks[i % len(ks)] for i, x in enumerate(b))[::-1]
elif variant == "decoy_layered_nearmiss":
    b = base64.b64decode(d)
    out = bytes(x ^ ((key + i) & 255) for i, x in enumerate(b))[::-1]
print(out.decode("latin-1"), "VALID" if re.fullmatch(r"ANS-[0-9A-F]{16}", out.decode("latin-1")) else "NOT-A-TOKEN")
