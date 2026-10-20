"""Independent reader: opens each fixture's token with jwcrypto using the key text shipped in the APK (zipfile +
regex, no lib.android), verifies the inner JWS with its x5c leaf and prints any ANS token in the (base64-decoded)
claims, or "none".  usage: PYTHONPATH=tools/pylib python3 oracle.py <apk>"""
import base64, json, re, sys, zipfile
from cryptography import x509
from jwcrypto import jwe, jwk, jws

z = zipfile.ZipFile(sys.argv[1])
blob = b"\n".join(z.read(n) for n in z.namelist())
tok = re.search(rb"eyJ[\w-]+(?:\.[\w-]*){4}", blob).group(0).decode()
cands = re.findall(rb"(?:key|CEK)=([A-Za-z0-9+/=]+)", blob)
found = "none"
for c in cands:
    c = c.decode()
    try:
        kb = bytes.fromhex(c) if re.fullmatch(r"[0-9a-f]{64}", c) else base64.b64decode(c)
    except ValueError:
        continue
    e = jwe.JWE()
    e.deserialize(tok)
    try:
        e.decrypt(jwk.JWK(kty="oct", k=base64.urlsafe_b64encode(kb).rstrip(b"=").decode()))
    except Exception:
        continue
    inner = e.payload.decode()
    s = jws.JWS()
    s.deserialize(inner)
    leaf = x509.load_der_x509_certificate(base64.b64decode(json.loads(base64.urlsafe_b64decode(
        inner.split(".")[0] + "==").decode())["x5c"][0]))
    s.verify(jwk.JWK.from_pyca(leaf.public_key()))
    claims = json.loads(s.payload)
    print("claims:", json.dumps(claims)[:300], file=sys.stderr)
    blobtxt = json.dumps(claims)
    for v in re.findall(r"[A-Za-z0-9+/_-]{16,}={0,2}", blobtxt):
        try:
            d = base64.urlsafe_b64decode(v.translate(str.maketrans("+/", "-_")) + "=" * (-len(v) % 4))
        except Exception:
            continue
        m = re.search(rb"ANS-[0-9a-f]{16}", d)
        if m:
            found = m.group(0).decode()
print(found)
