"""Fixture READER (independent of lib/warmups_codecs): the libraries' own verifying loaders.
usage: printf %s TOKEN | PYTHONPATH=tools/pylib-signing python3 -I signed_cookie_oracle.py <form>
prints the decoded JSON (compact) or None when the library rejects the token."""
import hashlib
import json
import sys

form, tok = sys.argv[1], sys.stdin.read().strip()
try:
    if form.startswith("django"):
        from django.conf import settings
        settings.configure(SECRET_KEY="fixture-django-key")
        from django.core import signing
        obj = signing.loads(tok)
    else:
        from itsdangerous import URLSafeSerializer, URLSafeTimedSerializer
        if form == "flask":
            obj = URLSafeTimedSerializer("fixture-flask-key", salt="cookie-session",
                                         signer_kwargs={"key_derivation": "hmac", "digest_method": hashlib.sha1}).loads(tok)
        elif form == "its-dict":
            obj = URLSafeTimedSerializer("fixture-its-key").loads(tok)
        elif form == "its":
            obj = URLSafeSerializer("fixture-its-key").loads(tok)
        else:   # payload-only fragment: itsdangerous' own payload loader (handles the leading-dot zlib form)
            obj = URLSafeSerializer("x").load_payload(tok.encode())
    print(json.dumps(obj, separators=(",", ":"), ensure_ascii=False))
except Exception as e:   # noqa: BLE001
    print("None", type(e).__name__, file=sys.stdout)
