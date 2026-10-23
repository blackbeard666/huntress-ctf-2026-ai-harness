"""Independent JOSE fixture writer (not lib/warmups_codecs): PyJWT for alg none, jwcrypto for HS256 / nested,
stdlib zlib (wbits -15) + json for the zip:DEF token. Usage: jwt_gen.py <form> <plain>"""
import base64
import json
import sys
import zlib

form, plain = sys.argv[1], sys.argv[2]
if form == "none":
    import jwt   # PyJWT
    print(jwt.encode({"sub": "warmup", "msg": plain}, None, algorithm="none"))
elif form in ("hs256-nested", "seg"):
    from jwcrypto import jwk, jwt as jjwt
    key = jwk.JWK(kty="oct", k=base64.urlsafe_b64encode(b"huntress-warmup-key-0123456789abc").decode().rstrip("="))
    claims = {"iss": "huntress", "data": {"note": plain}, "iat": 1760000000}
    t = jjwt.JWT(header={"alg": "HS256", "typ": "JWT"}, claims=claims)
    t.make_signed_token(key)
    tok = t.serialize()
    print(tok.split(".")[1] if form == "seg" else tok)
elif form == "def":
    e = lambda b: base64.urlsafe_b64encode(b).decode().rstrip("=")
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    body = c.compress(json.dumps({"msg": plain}).encode()) + c.flush()
    print(e(json.dumps({"alg": "none", "zip": "DEF"}).encode()) + "." + e(body) + ".")
