"""Fixture WRITER for the signed-cookie family: real itsdangerous 2.2 / Django 6.1 signers (tools/pylib-signing).
usage: PYTHONPATH=tools/pylib-signing python3 -I signed_cookie_gen.py <form> <plain>
forms: flask (URLSafeTimedSerializer, salt cookie-session, {"msg": plain}), its (URLSafeSerializer, bare JSON string),
its-dict (URLSafeTimedSerializer, {"user", "flag": plain}), its-frag (payload part 0 only of a URLSafeTimedSerializer token), django (signing.dumps compress=True, {"m": plain}),
django-plain (signing.dumps, bare JSON string)."""
import hashlib
import sys

form, plain = sys.argv[1], sys.argv[2]
if form.startswith("django"):
    from django.conf import settings
    settings.configure(SECRET_KEY="fixture-django-key")
    from django.core import signing
    if form == "django":
        print(signing.dumps({"m": plain}, compress=True))
    else:
        print(signing.dumps(plain))
else:
    from itsdangerous import URLSafeSerializer, URLSafeTimedSerializer
    if form == "flask":
        s = URLSafeTimedSerializer("fixture-flask-key", salt="cookie-session",
                                   signer_kwargs={"key_derivation": "hmac", "digest_method": hashlib.sha1})
        print(s.dumps({"msg": plain}))
    elif form == "its":
        print(URLSafeSerializer("fixture-its-key").dumps(plain))
    elif form == "its-dict":   # URLSafeTimedSerializer, short dict -> uncompressed 'eyJ..' + timestamp
        print(URLSafeTimedSerializer("fixture-its-key").dumps({"user": "guest", "flag": plain}))
    elif form == "its-frag":
        tok = URLSafeTimedSerializer("fixture-its-key").dumps(plain)
        print(tok[:tok.index(".", 1)])   # '.eJ..' (deflated) or 'eyJ..' payload part only
