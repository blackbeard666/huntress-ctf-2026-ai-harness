"""Forward ENCODERS for the declared-pipeline fixtures (stdlib only, independent of lib.android).
usage: python3 gen_dpl.py <variant> <out.apk>  -- writes assets/huntress_puzzle.json declaring its own layers."""
import base64, hashlib, json, sys, zipfile

variant, out = sys.argv[1], sys.argv[2]
tok = ("ANS-" + hashlib.sha256(variant.encode()).hexdigest()[:16].upper()).encode()
if variant == "three_step":  # declared decode order: hex -> sub (7+3i) -> reverse
    r = tok[::-1]
    data = bytes((x + 7 + 3 * i) & 255 for i, x in enumerate(r)).hex()
    puz = {"codec": "layered", "layers": ["hex", {"op": "sub", "key": 7, "step": 3}, "reverse"], "data": data}
elif variant == "encoder_order":  # listed as the ENCODER applied them: reverse, xor key2 cycled "k3y", base32; key=caesar
    c = bytes(65 + (x - 65 + 5) % 26 if 65 <= x <= 90 else x for x in tok)  # caesar +5 on capitals
    r = c[::-1]
    ks = b"k3y"
    x = bytes(b ^ ks[i % 3] for i, b in enumerate(r))
    data = base64.b32encode(x).decode()
    puz = {"codec": "pipeline", "key": 5, "key2": "k3y", "steps": ["caesar", "reverse", "xor", "base32"], "data": data}
elif variant in ("onion", "decoy_onion_nearmiss"):  # base64 -> JSON{layered xor 12+i} -> base64 -> JSON{split/order}
    t = tok if variant == "onion" else tok[:-1] + b"Z"
    s = t.decode()
    parts = [s[11:], s[:4], s[4:11]]
    core = {"codec": "split", "data": "", "parts": parts, "order": [2, 0, 1]}
    cj = json.dumps(core).encode()
    mid_data = base64.b64encode(bytes(x ^ ((12 + i) & 255) for i, x in enumerate(base64.b64encode(cj)))).decode()
    mid = {"codec": "layered", "pipeline": ["base64", {"xor": 12, "step": 1}, "base64"], "data": mid_data}
    puz = {"codec": "base64", "data": base64.b64encode(json.dumps(mid).encode()).decode()}
else:
    raise SystemExit("unknown variant")
puz = {"schema": "huntress.mobile.puzzle.v1", "day": 31, **puz}
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", b"\x03\x00\x08\x00" + b"\x00" * 4)
    z.writestr("assets/huntress_puzzle.json", json.dumps(puz, separators=(",", ":")))
print(json.dumps(puz))
