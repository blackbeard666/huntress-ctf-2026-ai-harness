"""Forward ENCODERS for the stacked-v1-codec fixtures (stdlib only, independent of lib.android).
usage: python3 gen_scs.py <variant> <out.apk>   -- writes assets/huntress_puzzle.json under the variant's stack."""
import base64, hashlib, json, sys, zipfile

variant, out = sys.argv[1], sys.argv[2]
tok = ("ANS-" + hashlib.sha256(variant.encode()).hexdigest()[:16].upper()).encode()
if variant == "b85_add2i_rev":  # decode: b85 -> plain = b + (key+2i) -> reverse
    key = 77
    r = tok[::-1]
    data = base64.b85encode(bytes((x - (key + 2 * i)) & 255 for i, x in enumerate(r))).decode()
elif variant == "hex_xorkeyi_b64":  # decode: hex -> b ^ (key^i) -> base64 (inner)
    key = 99
    inner = base64.b64encode(tok)
    data = bytes(x ^ ((key ^ i) & 255) for i, x in enumerate(inner)).hex()
elif variant == "b32_swap_keystr_rev":  # decode: base32 -> swap byte pairs -> b ^ str(key)[i%n] -> reverse
    key = 4721
    ks = str(key).encode()
    r = bytes(x ^ ks[i % len(ks)] for i, x in enumerate(tok[::-1]))
    data = base64.b32encode(bytes(r[i ^ 1] if (i ^ 1) < len(r) else r[i] for i in range(len(r)))).decode().rstrip("=")
elif variant == "decoy_layered_nearmiss":  # D30 `layered` shape, the token's last char is 'G' (not hex)
    key = 12
    bad = tok[:-1] + b"G"
    data = base64.b64encode(bytes(x ^ ((key + i) & 255) for i, x in enumerate(bad[::-1]))).decode()
else:
    raise SystemExit("unknown variant")
puz = {"schema": "huntress.mobile.puzzle.v1", "day": 31, "codec": "composed", "data": data, "key": key}
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", b"\x03\x00\x08\x00" + b"\x00" * 4)
    z.writestr("assets/huntress_puzzle.json", json.dumps(puz, separators=(",", ":")))
print(json.dumps(puz))
