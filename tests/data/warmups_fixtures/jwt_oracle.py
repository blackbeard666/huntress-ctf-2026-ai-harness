"""Independent JOSE fixture reader (not lib/warmups_codecs): jwcrypto JWS for PyJWT-made tokens, PyJWT for
jwcrypto-made tokens; zip:DEF payload inflated with zlib wbits -15. Usage: printf %s TOKEN | jwt_oracle.py <form>"""
import base64
import json
import sys
import zlib

form, tok = sys.argv[1], sys.stdin.read().strip()
try:
    if form == "none":
        from jwcrypto import jws
        j = jws.JWS()
        j.deserialize(tok)
        print(json.loads(j.objects["payload"])["msg"])
    elif form == "hs256-nested":
        import jwt   # PyJWT
        print(jwt.decode(tok, b"huntress-warmup-key-0123456789abc", algorithms=["HS256"])["data"]["note"])
    elif form == "seg":
        print(json.loads(base64.urlsafe_b64decode(tok + "=" * (-len(tok) % 4)))["data"]["note"])
    elif form == "def":
        from jwcrypto import jws
        j = jws.JWS()
        j.deserialize(tok)
        assert j.jose_header.get("zip") == "DEF"
        print(json.loads(zlib.decompress(j.objects["payload"], -15))["msg"])
except Exception as ex:   # noqa: BLE001
    print("None", type(ex).__name__)
