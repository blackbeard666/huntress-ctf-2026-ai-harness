"""X.509 certificate fields (prebuilt, SPECULATIVE). fmt `x509`, alias `cert`.

Input = one certificate member: DER (SEQUENCE 30 82 ..), or PEM text ('-----BEGIN CERTIFICATE-----' / 'X509 CERTIFICATE'
/ 'TRUSTED CERTIFICATE'; the FIRST block of a bundle), or a degenerate PKCS#7 bundle (.p7b/.p7c, DER or PEM 'PKCS7')
-> its first certificate. Parsed with asn1crypto (the same DER walker as the pe.py Authenticode signer fields).
Spellings follow the openssl / Windows certutil views and pe.py's signer_* fields:
  *_cn                 the LAST CN attribute's value as stored (openssl -nameopt shows the most specific one last)
  serial_hex           lowercase hex of the unsigned big-endian serial, even length, no 0x / colons (openssl -serial)
  not_before/after_utc ISO-8601 UTC 'YYYY-MM-DDTHH:MM:SSZ' of the Validity UTCTime/GeneralizedTime (both are UTC by RFC 5280)
  sha1/sha256/md5_fingerprint  lowercase hex digest of the WHOLE certificate DER, no colons (openssl -fingerprint digits)
  san_dns_names        SubjectAltName dNSName entries in stored order (JSON list); no SAN extension -> "none"
Not a certificate (wrong magic / truncated / a key or CSR) -> "none"."""
import base64
import hashlib
import re

FIELDS = {
    ("x509", "subject_cn"): "subject_cn",
    ("x509", "subject_common_name"): "subject_cn",
    ("x509", "issuer_cn"): "issuer_cn",
    ("x509", "issuer_common_name"): "issuer_cn",
    ("x509", "subject_dn"): "subject_dn",
    ("x509", "subject"): "subject_dn",
    ("x509", "issuer_dn"): "issuer_dn",
    ("x509", "issuer"): "issuer_dn",
    ("x509", "subject_o"): "subject_o",
    ("x509", "subject_organization"): "subject_o",
    ("x509", "issuer_o"): "issuer_o",
    ("x509", "issuer_organization"): "issuer_o",
    ("x509", "serial_hex"): "serial_hex",
    ("x509", "serial_number_hex"): "serial_hex",
    ("x509", "serial"): "serial_hex",
    ("x509", "serial_number"): "serial_hex",
    ("x509", "tbs_serial_number_hex"): "serial_hex",
    ("x509", "serial_number_decimal"): "serial_decimal",
    ("x509", "serial_decimal"): "serial_decimal",
    ("x509", "not_before"): "not_before_utc",
    ("x509", "not_before_utc"): "not_before_utc",
    ("x509", "validity_not_before"): "not_before_utc",
    ("x509", "validity_not_before_utc"): "not_before_utc",
    ("x509", "valid_from"): "not_before_utc",
    ("x509", "valid_from_utc"): "not_before_utc",
    ("x509", "not_after"): "not_after_utc",
    ("x509", "not_after_utc"): "not_after_utc",
    ("x509", "validity_not_after"): "not_after_utc",
    ("x509", "validity_not_after_utc"): "not_after_utc",
    ("x509", "valid_to"): "not_after_utc",
    ("x509", "valid_to_utc"): "not_after_utc",
    ("x509", "valid_until"): "not_after_utc",
    ("x509", "expiry_utc"): "not_after_utc",
    ("x509", "fingerprint_sha256"): "sha256_fingerprint",
    ("x509", "sha256_thumbprint"): "sha256_fingerprint",
    ("x509", "thumbprint_sha256"): "sha256_fingerprint",
    ("x509", "sha256"): "sha256_fingerprint",
    ("x509", "der_sha256"): "sha256_fingerprint",
    ("x509", "sha1_fingerprint"): "sha1_fingerprint",
    ("x509", "fingerprint_sha1"): "sha1_fingerprint",
    ("x509", "thumbprint"): "sha1_fingerprint",
    ("x509", "sha1_thumbprint"): "sha1_fingerprint",
    ("x509", "thumbprint_sha1"): "sha1_fingerprint",
    ("x509", "sha1"): "sha1_fingerprint",
    ("x509", "der_sha1"): "sha1_fingerprint",
    ("x509", "md5_fingerprint"): "md5_fingerprint",
    ("x509", "fingerprint_md5"): "md5_fingerprint",
    ("x509", "san_dns_names"): "san_dns_names",
    ("x509", "subject_alt_name_dns_names"): "san_dns_names",
    ("x509", "subject_alternative_name_dns_names"): "san_dns_names",
    ("x509", "dns_names"): "san_dns_names",
    ("x509", "san_dns"): "san_dns_names",
    ("x509", "san_names"): "san_dns_names",
    ("x509", "version"): "version",
    ("x509", "tbs_version"): "version",
    ("x509", "signature_algorithm"): "signature_algorithm",
    ("x509", "signature_algorithm_oid"): "signature_algorithm_oid",
    ("x509", "public_key_algorithm"): "public_key_algorithm",
    ("x509", "key_size_bits"): "key_size_bits",
    ("x509", "public_key_size_bits"): "key_size_bits",
    ("x509", "key_size"): "key_size_bits",
    ("x509", "is_self_signed"): "is_self_signed",
    ("x509", "self_signed"): "is_self_signed",
    ("x509", "is_ca"): "is_ca",
    ("x509", "basic_constraints_ca"): "is_ca",
    ("x509", "subject_key_identifier_hex"): "subject_key_identifier",
    ("x509", "subject_key_identifier"): "subject_key_identifier",
    ("x509", "authority_key_identifier_hex"): "authority_key_identifier",
    ("x509", "authority_key_identifier"): "authority_key_identifier",
    ("x509", "extended_key_usage"): "extended_key_usage",
    ("x509", "ext_key_usage"): "extended_key_usage",
    ("x509", "extended_key_usage_oids"): "extended_key_usage_oids",
    ("cert", "subject_cn"): "subject_cn",
    ("cert", "subject_common_name"): "subject_cn",
    ("cert", "issuer_cn"): "issuer_cn",
    ("cert", "issuer_common_name"): "issuer_cn",
    ("cert", "subject_dn"): "subject_dn",
    ("cert", "subject"): "subject_dn",
    ("cert", "issuer_dn"): "issuer_dn",
    ("cert", "issuer"): "issuer_dn",
    ("cert", "subject_o"): "subject_o",
    ("cert", "subject_organization"): "subject_o",
    ("cert", "issuer_o"): "issuer_o",
    ("cert", "issuer_organization"): "issuer_o",
    ("cert", "serial_hex"): "serial_hex",
    ("cert", "serial_number_hex"): "serial_hex",
    ("cert", "serial"): "serial_hex",
    ("cert", "serial_number"): "serial_hex",
    ("cert", "tbs_serial_number_hex"): "serial_hex",
    ("cert", "serial_number_decimal"): "serial_decimal",
    ("cert", "serial_decimal"): "serial_decimal",
    ("cert", "not_before"): "not_before_utc",
    ("cert", "not_before_utc"): "not_before_utc",
    ("cert", "validity_not_before"): "not_before_utc",
    ("cert", "validity_not_before_utc"): "not_before_utc",
    ("cert", "valid_from"): "not_before_utc",
    ("cert", "valid_from_utc"): "not_before_utc",
    ("cert", "not_after"): "not_after_utc",
    ("cert", "not_after_utc"): "not_after_utc",
    ("cert", "validity_not_after"): "not_after_utc",
    ("cert", "validity_not_after_utc"): "not_after_utc",
    ("cert", "valid_to"): "not_after_utc",
    ("cert", "valid_to_utc"): "not_after_utc",
    ("cert", "valid_until"): "not_after_utc",
    ("cert", "expiry_utc"): "not_after_utc",
    ("cert", "sha256_fingerprint"): "sha256_fingerprint",
    ("cert", "fingerprint_sha256"): "sha256_fingerprint",
    ("cert", "sha256_thumbprint"): "sha256_fingerprint",
    ("cert", "thumbprint_sha256"): "sha256_fingerprint",
    ("cert", "sha256"): "sha256_fingerprint",
    ("cert", "der_sha256"): "sha256_fingerprint",
    ("cert", "sha1_fingerprint"): "sha1_fingerprint",
    ("cert", "fingerprint_sha1"): "sha1_fingerprint",
    ("cert", "thumbprint"): "sha1_fingerprint",
    ("cert", "sha1_thumbprint"): "sha1_fingerprint",
    ("cert", "thumbprint_sha1"): "sha1_fingerprint",
    ("cert", "sha1"): "sha1_fingerprint",
    ("cert", "der_sha1"): "sha1_fingerprint",
    ("cert", "md5_fingerprint"): "md5_fingerprint",
    ("cert", "fingerprint_md5"): "md5_fingerprint",
    ("cert", "san_dns_names"): "san_dns_names",
    ("cert", "subject_alt_name_dns_names"): "san_dns_names",
    ("cert", "subject_alternative_name_dns_names"): "san_dns_names",
    ("cert", "dns_names"): "san_dns_names",
    ("cert", "san_dns"): "san_dns_names",
    ("cert", "san_names"): "san_dns_names",
    ("cert", "version"): "version",
    ("cert", "tbs_version"): "version",
    ("cert", "signature_algorithm"): "signature_algorithm",
    ("cert", "signature_algorithm_oid"): "signature_algorithm_oid",
    ("cert", "public_key_algorithm"): "public_key_algorithm",
    ("cert", "key_size_bits"): "key_size_bits",
    ("cert", "public_key_size_bits"): "key_size_bits",
    ("cert", "key_size"): "key_size_bits",
    ("cert", "is_self_signed"): "is_self_signed",
    ("cert", "self_signed"): "is_self_signed",
    ("cert", "is_ca"): "is_ca",
    ("cert", "basic_constraints_ca"): "is_ca",
    ("cert", "subject_key_identifier_hex"): "subject_key_identifier",
    ("cert", "subject_key_identifier"): "subject_key_identifier",
    ("cert", "authority_key_identifier_hex"): "authority_key_identifier",
    ("cert", "authority_key_identifier"): "authority_key_identifier",
    ("cert", "extended_key_usage"): "extended_key_usage",
    ("cert", "ext_key_usage"): "extended_key_usage",
    ("cert", "extended_key_usage_oids"): "extended_key_usage_oids",
}

_PEM = re.compile(rb"-----BEGIN (X509 CERTIFICATE|TRUSTED CERTIFICATE|CERTIFICATE|PKCS7)-----(.*?)-----END \1-----", re.S)


def _from_p7(der):
    from asn1crypto import cms
    ci = cms.ContentInfo.load(der, strict=False)
    if ci["content_type"].native != "signed_data":
        return None
    for c in ci["content"]["certificates"] or []:
        if c.name == "certificate":
            return c.chosen
    return None


def _cert(data):
    """asn1crypto x509.Certificate of the member; "none" (not a certificate) or None (no data)."""
    if data is None:
        return None
    try:
        b = bytes(data)
        m = _PEM.search(b[:1 << 20])
        p7 = False
        if m:
            b = base64.b64decode(re.sub(rb"[^A-Za-z0-9+/=]", b"", m.group(2)))
            p7 = m.group(1) == b"PKCS7"
        if len(b) < 64 or b[0] != 0x30:
            return "none"
        from asn1crypto import x509
        c = None
        if not p7:
            c = x509.Certificate.load(b, strict=False)
            tbs = c["tbs_certificate"]
            if not isinstance(tbs["serial_number"].native, int) or tbs["validity"]["not_after"].native is None:
                c = None
        if c is None:
            c = _from_p7(b)
        if c is None:
            return "none"
        c["tbs_certificate"]["subject"].native    # force-parse: a truncated / non-cert SEQUENCE raises here
        return c
    except Exception:
        return "none"


def _name_attr(name, attr):
    vals = []
    for rdn in name.chosen:
        for atv in rdn:
            if atv["type"].native == attr:
                vals.append(str(atv["value"].native).strip())
    return vals[-1] if vals else "none"


def _get(data, fn):
    c = _cert(data)
    if c is None or c == "none":
        return c
    try:
        return fn(c)
    except Exception:
        return None


def subject_cn(data, ctx):
    return _get(data, lambda c: _name_attr(c.subject, "common_name"))


def issuer_cn(data, ctx):
    return _get(data, lambda c: _name_attr(c.issuer, "common_name"))


def subject_o(data, ctx):
    return _get(data, lambda c: _name_attr(c.subject, "organization_name"))


def issuer_o(data, ctx):
    return _get(data, lambda c: _name_attr(c.issuer, "organization_name"))


def _dn(name):
    """RFC 4514 string (most specific RDN first, e.g. 'CN=x,O=y,C=US'), as `openssl x509 -nameopt RFC2253`."""
    return name.human_friendly and _rfc4514(name)


_SHORT = {"common_name": "CN", "country_name": "C", "locality_name": "L", "state_or_province_name": "ST",
          "organization_name": "O", "organizational_unit_name": "OU", "domain_component": "DC", "user_id": "UID",
          "street_address": "STREET", "email_address": "emailAddress", "serial_number": "serialNumber"}


def _rfc4514(name):
    out = []
    for rdn in reversed(list(name.chosen)):
        parts = []
        for atv in rdn:
            t = atv["type"]
            k = _SHORT.get(t.native) or t.dotted
            v = str(atv["value"].native)
            v = re.sub(r'([,+"\\<>;])', r"\\\1", v)
            v = re.sub(r"^([ #])", r"\\\1", v)
            v = re.sub(r" $", r"\\ ", v)
            parts.append(f"{k}={v}")
        out.append("+".join(parts))
    return ",".join(out) if out else "none"


def subject_dn(data, ctx):
    return _get(data, lambda c: _dn(c.subject))


def issuer_dn(data, ctx):
    return _get(data, lambda c: _dn(c.issuer))


def _serial(c):
    n = c.serial_number
    if n < 0:
        return None
    h = "%x" % n
    return "0" * (len(h) % 2) + h


def serial_hex(data, ctx):
    return _get(data, _serial)


def serial_decimal(data, ctx):
    return _get(data, lambda c: str(c.serial_number))


def _utc(dt):
    import datetime
    if dt.tzinfo is not None:
        dt = dt.astimezone(datetime.timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def not_before_utc(data, ctx):
    return _get(data, lambda c: _utc(c["tbs_certificate"]["validity"]["not_before"].native))


def not_after_utc(data, ctx):
    return _get(data, lambda c: _utc(c["tbs_certificate"]["validity"]["not_after"].native))


def sha256_fingerprint(data, ctx):
    return _get(data, lambda c: hashlib.sha256(c.dump()).hexdigest())


def sha1_fingerprint(data, ctx):
    return _get(data, lambda c: hashlib.sha1(c.dump()).hexdigest())


def md5_fingerprint(data, ctx):
    return _get(data, lambda c: hashlib.md5(c.dump()).hexdigest())


def _san(c):
    ext = c.subject_alt_name_value
    if ext is None:
        return "none"
    return [str(g.native) for g in ext if g.name == "dns_name"] or "none"


def san_dns_names(data, ctx):
    return _get(data, _san)


def version(data, ctx):
    """X.509 version as displayed (stored INTEGER + 1: v3 -> 3)."""
    return _get(data, lambda c: int(c["tbs_certificate"]["version"].native[1:]))


def signature_algorithm(data, ctx):
    """openssl-style name of the outer signatureAlgorithm (e.g. sha256WithRSAEncryption, ecdsa-with-SHA256)."""
    _OSSL = {"1.2.840.113549.1.1.5": "sha1WithRSAEncryption", "1.2.840.113549.1.1.11": "sha256WithRSAEncryption",
             "1.2.840.113549.1.1.12": "sha384WithRSAEncryption", "1.2.840.113549.1.1.13": "sha512WithRSAEncryption",
             "1.2.840.113549.1.1.4": "md5WithRSAEncryption", "1.2.840.113549.1.1.10": "rsassaPss",
             "1.2.840.10045.4.3.2": "ecdsa-with-SHA256", "1.2.840.10045.4.3.3": "ecdsa-with-SHA384",
             "1.2.840.10045.4.3.4": "ecdsa-with-SHA512", "1.2.840.10045.4.1": "ecdsa-with-SHA1",
             "1.3.101.112": "ED25519", "1.3.101.113": "ED448"}
    return _get(data, lambda c: _OSSL.get(c["signature_algorithm"]["algorithm"].dotted,
                                          c["signature_algorithm"]["algorithm"].dotted))


def signature_algorithm_oid(data, ctx):
    return _get(data, lambda c: c["signature_algorithm"]["algorithm"].dotted)


def public_key_algorithm(data, ctx):
    """asn1crypto's algorithm name: rsa / ec / dsa / ed25519 / ed448."""
    return _get(data, lambda c: c.public_key.algorithm)


def key_size_bits(data, ctx):
    return _get(data, lambda c: c.public_key.bit_size)


def is_self_signed(data, ctx):
    """subject == issuer (asn1crypto self_issued; the signature is not verified)."""
    return _get(data, lambda c: c.self_issued)


def is_ca(data, ctx):
    """basicConstraints cA flag; no basicConstraints extension -> false."""
    return _get(data, lambda c: bool(c.ca))


def subject_key_identifier(data, ctx):
    """keyIdentifier bytes as lowercase hex, no colons; absent -> none."""
    return _get(data, lambda c: c.key_identifier.hex() if c.key_identifier else "none")


def authority_key_identifier(data, ctx):
    return _get(data, lambda c: c.authority_key_identifier.hex() if c.authority_key_identifier else "none")


def extended_key_usage(data, ctx):
    """EKU purposes as asn1crypto names in stored order (server_auth, client_auth, code_signing, ...); absent -> none."""
    return _get(data, lambda c: [p.native for p in c.extended_key_usage_value]
                if c.extended_key_usage_value is not None else "none")


def extended_key_usage_oids(data, ctx):
    return _get(data, lambda c: [p.dotted for p in c.extended_key_usage_value]
                if c.extended_key_usage_value is not None else "none")
