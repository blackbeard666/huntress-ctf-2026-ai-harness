"""X.509 certificate fields, GM-verified (the rest stay speculative in prebuilt/x509.py)."""


def sha256_fingerprint(data, ctx):
    """D29 "Trust Issues": SHA-256 of the WHOLE certificate DER (PEM -> first CERTIFICATE block base64-decoded),
    lowercase hex, no colons (openssl x509 -fingerprint -sha256 digits) -- single b466fdbf.., TT 01851d3a.., 13/13
    Mastery sets (nested evidence-NN.zip). Promoted from prebuilt x509.sha256_fingerprint with identical results: not a
    certificate -> "none"."""
    from .prebuilt.x509 import sha256_fingerprint as f
    return f(data, ctx or {})
