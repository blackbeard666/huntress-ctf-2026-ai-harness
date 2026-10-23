"""APK signer identity (prebuilt, SPECULATIVE): v1 JAR signature + APK Signing Block (v2/v3/v3.1). fmt `apk`.
D21 flavor "distinguish rebuilds from clones": same package + different SIGNER = clone/repack; same signer + new
versionCode = rebuild. The D21 APK carries META-INF/FIXTURE-.SF/.RSA/MANIFEST.MF AND a v2 APK Signing Block.

APK Signing Block (source.android.com/docs/security/features/apksigning/v2): EOCD -> CD offset; the 24 bytes before
the CD are `u64 size_of_block` + magic `APK Sig Block 42`; the block starts at cd_off - size - 8 with the same u64;
pairs = u64 len + u32 id + value. v2 (0x7109871a) / v3 (0xf05368c0) / v3.1 (0x1b93ad61) value = u32-len-prefixed
sequence of u32-len-prefixed signers; signer -> u32-len signed data -> [digests, certificates (u32-len DER each), ...].
v1: META-INF/*.RSA|DSA|EC = PKCS#7 SignedData DER -> certificates [0] (hand DER walk, no asn1crypto for this part).
Spellings (apksigner `verify --print-certs -v` / keytool -printcert):
  signer_cert_sha256/_sha1/_md5   lowercase hex digest of the signer certificate DER (apksigner); `_colon` sibling =
                                  uppercase colon-separated (keytool). Signer = first cert of the highest block scheme
                                  present (v3.1 > v3 > v2, as apksigner reports), else the v1 PKCS#7 first cert.
  signer_public_key_sha256        sha256 of the SubjectPublicKeyInfo DER (apksigner "public key SHA-256 digest")
  signer_subject_dn/_issuer_dn    RFC 4514 (most specific first: CN=..,O=..,C=..), via x509.py; *_cn = last CN
  signer_serial_hex               lowercase unsigned big-endian hex, even length (x509.py serial_hex)
  signer_not_before/after_utc     ISO-8601 'YYYY-MM-DDTHH:MM:SSZ' of the Validity (UTC by RFC 5280)
  signing_block_size              the stored u64 `size of block` (excludes that leading 8-byte field itself);
                                  signing_block_total_size = size + 8 (bytes the block occupies in the file)
  signing_block_ids_hex           pair ids in block order, `0x%08x`; signature_schemes = JSON ["v1","v2","v3","v3.1"]
  v1_signature_file_names         META-INF/<x>.SF/.RSA/.DSA/.EC directly under META-INF, central-directory order
Not a zip -> None; a zip with no signature of the asked kind -> "none" (has_* / *_present -> false)."""
import hashlib
import io
import re
import struct
import zipfile

FIELDS = {
    ("apk", "signature_schemes"): "signature_schemes",
    ("apk", "signing_schemes"): "signature_schemes",
    ("apk", "signature_scheme_versions"): "signature_schemes",
    ("apk", "schemes_present"): "signature_schemes",
    ("apk", "has_v1_signature"): "has_v1",
    ("apk", "v1_signature_present"): "has_v1",
    ("apk", "v1_signed"): "has_v1",
    ("apk", "is_v1_signed"): "has_v1",
    ("apk", "jar_signature_present"): "has_v1",
    ("apk", "has_v2_signature"): "has_v2",
    ("apk", "v2_signature_present"): "has_v2",
    ("apk", "v2_signed"): "has_v2",
    ("apk", "is_v2_signed"): "has_v2",
    ("apk", "has_v3_signature"): "has_v3",
    ("apk", "v3_signature_present"): "has_v3",
    ("apk", "v3_signed"): "has_v3",
    ("apk", "is_v3_signed"): "has_v3",
    ("apk", "has_v31_signature"): "has_v31",
    ("apk", "has_v3_1_signature"): "has_v31",
    ("apk", "v31_signature_present"): "has_v31",
    ("apk", "has_source_stamp"): "has_source_stamp",
    ("apk", "source_stamp_present"): "has_source_stamp",
    ("apk", "signing_block_present"): "block_present",
    ("apk", "apk_signing_block_present"): "block_present",
    ("apk", "has_signing_block"): "block_present",
    ("apk", "has_apk_signing_block"): "block_present",
    ("apk", "signing_block_size"): "block_size",
    ("apk", "apk_signing_block_size"): "block_size",
    ("apk", "signing_block_size_bytes"): "block_size",
    ("apk", "signing_block_total_size"): "block_total_size",
    ("apk", "signing_block_offset"): "block_offset",
    ("apk", "apk_signing_block_offset"): "block_offset",
    ("apk", "signing_block_ids_hex"): "block_ids_hex",
    ("apk", "signing_block_ids"): "block_ids_hex",
    ("apk", "signing_block_pair_ids"): "block_ids_hex",
    ("apk", "signing_block_pair_ids_hex"): "block_ids_hex",
    ("apk", "apk_signing_block_ids_hex"): "block_ids_hex",
    ("apk", "signing_block_id_list"): "block_ids_hex",
    ("apk", "signing_block_pair_count"): "block_pair_count",
    ("apk", "v1_signature_file_names"): "v1_files",
    ("apk", "v1_signature_files"): "v1_files",
    ("apk", "signature_files"): "v1_files",
    ("apk", "signature_file_names"): "v1_files",
    ("apk", "meta_inf_signature_files"): "v1_files",
    ("apk", "v1_signer_name"): "v1_signer_name",
    ("apk", "v1_signer_names"): "v1_signer_names",
    ("apk", "signer_cert_sha256"): "cert_sha256",
    ("apk", "signer_certificate_sha256"): "cert_sha256",
    ("apk", "signer_cert_sha256_digest"): "cert_sha256",
    ("apk", "signer_sha256"): "cert_sha256",
    ("apk", "cert_sha256"): "cert_sha256",
    ("apk", "certificate_sha256"): "cert_sha256",
    ("apk", "signing_cert_sha256"): "cert_sha256",
    ("apk", "signer_cert_sha256_colon"): "cert_sha256_colon",
    ("apk", "signer_cert_sha1"): "cert_sha1",
    ("apk", "signer_certificate_sha1"): "cert_sha1",
    ("apk", "signer_sha1"): "cert_sha1",
    ("apk", "cert_sha1"): "cert_sha1",
    ("apk", "certificate_sha1"): "cert_sha1",
    ("apk", "signing_cert_sha1"): "cert_sha1",
    ("apk", "signer_cert_sha1_colon"): "cert_sha1_colon",
    ("apk", "signer_cert_md5"): "cert_md5",
    ("apk", "signer_certificate_md5"): "cert_md5",
    ("apk", "signer_md5"): "cert_md5",
    ("apk", "cert_md5"): "cert_md5",
    ("apk", "signing_cert_md5"): "cert_md5",
    ("apk", "signer_cert_md5_colon"): "cert_md5_colon",
    ("apk", "v1_signer_cert_sha256"): "v1_cert_sha256",
    ("apk", "v1_cert_sha256"): "v1_cert_sha256",
    ("apk", "v2_signer_cert_sha256"): "v2_cert_sha256",
    ("apk", "v2_cert_sha256"): "v2_cert_sha256",
    ("apk", "v3_signer_cert_sha256"): "v3_cert_sha256",
    ("apk", "v3_cert_sha256"): "v3_cert_sha256",
    ("apk", "signer_subject_dn"): "subject_dn",
    ("apk", "signer_dn"): "subject_dn",
    ("apk", "signer_certificate_dn"): "subject_dn",
    ("apk", "signer_cert_subject_dn"): "subject_dn",
    ("apk", "signer_subject"): "subject_dn",
    ("apk", "signer_issuer_dn"): "issuer_dn",
    ("apk", "signer_cert_issuer_dn"): "issuer_dn",
    ("apk", "signer_issuer"): "issuer_dn",
    ("apk", "signer_subject_cn"): "subject_cn",
    ("apk", "signer_cn"): "subject_cn",
    ("apk", "signer_cert_subject_cn"): "subject_cn",
    ("apk", "signer_common_name"): "subject_cn",
    ("apk", "signer_issuer_cn"): "issuer_cn",
    ("apk", "signer_cert_issuer_cn"): "issuer_cn",
    ("apk", "signer_serial_hex"): "serial_hex",
    ("apk", "signer_serial_number_hex"): "serial_hex",
    ("apk", "signer_cert_serial_hex"): "serial_hex",
    ("apk", "signer_not_before_utc"): "not_before_utc",
    ("apk", "signer_not_before"): "not_before_utc",
    ("apk", "signer_valid_from_utc"): "not_before_utc",
    ("apk", "signer_not_after_utc"): "not_after_utc",
    ("apk", "signer_not_after"): "not_after_utc",
    ("apk", "signer_valid_to_utc"): "not_after_utc",
    ("apk", "not_before_utc"): "not_before_utc",
    ("apk", "not_after_utc"): "not_after_utc",
    ("apk", "signer_public_key_sha256"): "pubkey_sha256",
    ("apk", "signer_public_key_sha1"): "pubkey_sha1",
    ("apk", "signer_public_key_md5"): "pubkey_md5",
    ("apk", "public_key_sha256"): "pubkey_sha256",
    ("apk", "signer_key_algorithm"): "key_algorithm",
    ("apk", "signer_public_key_algorithm"): "key_algorithm",
    ("apk", "key_algorithm"): "key_algorithm",
    ("apk", "signer_key_bits"): "key_bits",
    ("apk", "signer_key_size"): "key_bits",
    ("apk", "signer_key_size_bits"): "key_bits",
    ("apk", "key_size_bits"): "key_bits",
    ("apk", "signer_count"): "signer_count",
    ("apk", "number_of_signers"): "signer_count",
    ("apk", "v2_signer_count"): "v2_signer_count",
    ("apk", "v3_signer_count"): "v3_signer_count",
    ("apk", "v1_v2_cert_match"): "v1_v2_match",
    ("apk", "v1_v2_certs_match"): "v1_v2_match",
    ("apk", "v1_v2_signer_match"): "v1_v2_match",
    ("apk", "v2_v3_cert_match"): "v2_v3_match",
    ("apk", "manifest_mf_created_by"): "mf_created_by",
    ("apk", "manifest_created_by"): "mf_created_by",
    ("apk", "created_by"): "mf_created_by",
    ("apk", "jar_manifest_created_by"): "mf_created_by",
    ("apk", "sf_created_by"): "sf_created_by",
    ("apk", "signature_file_created_by"): "sf_created_by",
    ("apk", "sf_x_android_apk_signed"): "sf_apk_signed",
    ("apk", "x_android_apk_signed"): "sf_apk_signed",
}

_MAGIC = b"APK Sig Block 42"
V2, V3, V31, STAMP = 0x7109871A, 0xF05368C0, 0x1B93AD61, 0x6DFF800D
_SIG = re.compile(r"^META-INF/[^/]+\.(SF|RSA|DSA|EC)$", re.I)
_PKCS7 = re.compile(r"^META-INF/[^/]+\.(RSA|DSA|EC)$", re.I)


# ---------------------------------------------------------------- zip / signing block

def _eocd_cd(b):
    """Central-directory offset from the EOCD (zip64 locator honoured), or None."""
    i = b.rfind(b"PK\x05\x06", max(0, len(b) - 65557))
    if i < 0 or i + 22 > len(b):
        return None
    cd_off, = struct.unpack_from("<I", b, i + 16)
    if cd_off == 0xFFFFFFFF and i >= 20 and b[i - 20:i - 16] == b"PK\x06\x07":
        z64, = struct.unpack_from("<Q", b, i - 12)
        if z64 + 56 <= len(b) and b[z64:z64 + 4] == b"PK\x06\x06":
            cd_off, = struct.unpack_from("<Q", b, z64 + 48)
    return cd_off if cd_off <= i else None


def _block(b):
    """(offset, stored_size, [(id, value_bytes), ...]) of the APK Signing Block, "none" if absent, None if not a zip."""
    cd = _eocd_cd(b)
    if cd is None:
        return None
    if cd < 32 or b[cd - 16:cd] != _MAGIC:
        return "none"
    size, = struct.unpack_from("<Q", b, cd - 24)
    start = cd - size - 8
    if size < 24 or start < 0 or struct.unpack_from("<Q", b, start)[0] != size:
        return "none"
    pairs, p, end = [], start + 8, cd - 24
    while p + 12 <= end:
        ln, = struct.unpack_from("<Q", b, p)
        if ln < 4 or p + 8 + ln > end:
            break
        pid, = struct.unpack_from("<I", b, p + 8)
        pairs.append((pid, b[p + 12:p + 8 + ln]))
        p += 8 + ln
    return start, size, pairs


def _lp(buf, p):
    """One u32-length-prefixed item at p -> (bytes, next_p); raises on overrun."""
    n, = struct.unpack_from("<I", buf, p)
    if p + 4 + n > len(buf):
        raise ValueError("lp overrun")
    return buf[p + 4:p + 4 + n], p + 4 + n


def _seq(buf):
    out, p = [], 0
    while p + 4 <= len(buf):
        item, p = _lp(buf, p)
        out.append(item)
    return out


def _scheme_signers(value):
    """[[cert_der, ...] per signer] of a v2/v3/v3.1 pair value."""
    signers = []
    outer, _ = _lp(value, 0)
    for signer in _seq(outer):
        signed, _ = _lp(signer, 0)
        _digests, p = _lp(signed, 0)
        certs, _ = _lp(signed, p)
        signers.append(_seq(certs))
    return signers


# ---------------------------------------------------------------- v1 (hand DER walk)

def _tlv(b, p):
    """(tag, content_start, content_end) of the DER TLV at p."""
    tag = b[p]
    n = b[p + 1]
    q = p + 2
    if n & 0x80:
        k = n & 0x7F
        if not 0 < k <= 4:
            raise ValueError("der len")
        n = int.from_bytes(b[q:q + k], "big")
        q += k
    if q + n > len(b):
        raise ValueError("der overrun")
    return tag, q, q + n


def _p7_certs(der):
    """Certificate DERs of a PKCS#7 SignedData ContentInfo (certificates [0] IMPLICIT SET OF)."""
    t, s, _e = _tlv(der, 0)
    if t != 0x30:
        return []
    t, s1, e1 = _tlv(der, s)                      # contentType OID
    if t != 0x06 or der[s1:e1] != bytes.fromhex("2a864886f70d010702"):
        return []
    t, s2, _ = _tlv(der, e1)                      # [0] EXPLICIT
    if t != 0xA0:
        return []
    t, sd, sde = _tlv(der, s2)                    # SignedData SEQUENCE
    if t != 0x30:
        return []
    p = sd
    for _ in range(3):                            # version, digestAlgorithms, encapContentInfo
        _, _, p = _tlv(der, p)
    if p >= sde or der[p] != 0xA0:
        return []
    _, cs, ce = _tlv(der, p)
    out = []
    while cs < ce:
        t, s, e = _tlv(der, cs)
        if t == 0x30:
            out.append(der[cs:e])
        cs = e
    return out


# ---------------------------------------------------------------- state

def _state(data):
    """Parsed signing facts of the APK, or None (not a zip)."""
    if data is None:
        return None
    b = bytes(data)
    try:
        z = zipfile.ZipFile(io.BytesIO(b))
        infos = z.infolist()
    except Exception:
        return None
    st = {"z": z, "v1_files": [i.filename for i in infos if _SIG.match(i.filename)], "v1_certs": [], "schemes": {}}
    for i in infos:
        if _PKCS7.match(i.filename) and not st["v1_certs"]:
            try:
                st["v1_certs"] = _p7_certs(z.read(i))
            except Exception:
                pass
    st["v1_sf"] = [n for n in st["v1_files"] if n.upper().endswith(".SF")]
    try:
        blk = _block(b)
    except Exception:
        blk = "none"
    st["block"] = blk if isinstance(blk, tuple) else None
    if st["block"]:
        for pid, val in st["block"][2]:
            if pid in (V2, V3, V31) and pid not in st["schemes"]:
                try:
                    st["schemes"][pid] = _scheme_signers(val)
                except Exception:
                    st["schemes"][pid] = []
    return st


def _signer_der(st):
    for pid in (V31, V3, V2):
        sg = st["schemes"].get(pid)
        if sg and sg[0]:
            return sg[0][0]
    return st["v1_certs"][0] if st["v1_certs"] else None


def _with(data, fn):
    st = _state(data)
    if st is None:
        return None
    try:
        return fn(st)
    except Exception:
        return None


def _cert_fn(data, fn):
    def go(st):
        der = _signer_der(st)
        return "none" if der is None else fn(der)
    return _with(data, go)


def _colon(h):
    return ":".join(h[i:i + 2] for i in range(0, len(h), 2)).upper()


# ---------------------------------------------------------------- fields

def signature_schemes(data, ctx):
    def go(st):
        out = ["v1"] if st["v1_sf"] and st["v1_certs"] else []
        for pid, name in ((V2, "v2"), (V3, "v3"), (V31, "v3.1")):
            if pid in st["schemes"]:
                out.append(name)
        return out or "none"
    return _with(data, go)


def has_v1(data, ctx):
    return _with(data, lambda st: bool(st["v1_sf"] and st["v1_certs"]))


def has_v2(data, ctx):
    return _with(data, lambda st: V2 in st["schemes"])


def has_v3(data, ctx):
    return _with(data, lambda st: V3 in st["schemes"])


def has_v31(data, ctx):
    return _with(data, lambda st: V31 in st["schemes"])


def has_source_stamp(data, ctx):
    return _with(data, lambda st: bool(st["block"]) and any(p == STAMP for p, _ in st["block"][2]))


def block_present(data, ctx):
    return _with(data, lambda st: st["block"] is not None)


def block_size(data, ctx):
    return _with(data, lambda st: st["block"][1] if st["block"] else "none")


def block_total_size(data, ctx):
    return _with(data, lambda st: st["block"][1] + 8 if st["block"] else "none")


def block_offset(data, ctx):
    return _with(data, lambda st: st["block"][0] if st["block"] else "none")


def block_ids_hex(data, ctx):
    return _with(data, lambda st: ["0x%08x" % p for p, _ in st["block"][2]] if st["block"] else "none")


def block_pair_count(data, ctx):
    return _with(data, lambda st: len(st["block"][2]) if st["block"] else "none")


def v1_files(data, ctx):
    return _with(data, lambda st: st["v1_files"] or "none")


def v1_signer_names(data, ctx):
    return _with(data, lambda st: [n[9:-3] for n in st["v1_sf"]] or "none")


def v1_signer_name(data, ctx):
    return _with(data, lambda st: st["v1_sf"][0][9:-3] if st["v1_sf"] else "none")


def cert_sha256(data, ctx):
    return _cert_fn(data, lambda d: hashlib.sha256(d).hexdigest())


def cert_sha1(data, ctx):
    return _cert_fn(data, lambda d: hashlib.sha1(d).hexdigest())


def cert_md5(data, ctx):
    return _cert_fn(data, lambda d: hashlib.md5(d).hexdigest())


def cert_sha256_colon(data, ctx):
    return _cert_fn(data, lambda d: _colon(hashlib.sha256(d).hexdigest()))


def cert_sha1_colon(data, ctx):
    return _cert_fn(data, lambda d: _colon(hashlib.sha1(d).hexdigest()))


def cert_md5_colon(data, ctx):
    return _cert_fn(data, lambda d: _colon(hashlib.md5(d).hexdigest()))


def _scheme_cert_sha256(data, pid):
    def go(st):
        sg = st["schemes"].get(pid)
        return hashlib.sha256(sg[0][0]).hexdigest() if sg and sg[0] else "none"
    return _with(data, go)


def v1_cert_sha256(data, ctx):
    return _with(data, lambda st: hashlib.sha256(st["v1_certs"][0]).hexdigest() if st["v1_certs"] else "none")


def v2_cert_sha256(data, ctx):
    return _scheme_cert_sha256(data, V2)


def v3_cert_sha256(data, ctx):
    return _scheme_cert_sha256(data, V3)


def _x509(name):
    """Delegate a certificate field to the x509.py extractor on the signer cert DER."""
    def fn(der):
        from . import x509
        return getattr(x509, name)(der, {})
    return fn


def subject_dn(data, ctx):
    return _cert_fn(data, _x509("subject_dn"))


def issuer_dn(data, ctx):
    return _cert_fn(data, _x509("issuer_dn"))


def subject_cn(data, ctx):
    return _cert_fn(data, _x509("subject_cn"))


def issuer_cn(data, ctx):
    return _cert_fn(data, _x509("issuer_cn"))


def serial_hex(data, ctx):
    return _cert_fn(data, _x509("serial_hex"))


def not_before_utc(data, ctx):
    return _cert_fn(data, _x509("not_before_utc"))


def not_after_utc(data, ctx):
    return _cert_fn(data, _x509("not_after_utc"))


def _pub(der):
    from asn1crypto import x509
    return x509.Certificate.load(der).public_key


def pubkey_sha256(data, ctx):
    return _cert_fn(data, lambda d: hashlib.sha256(_pub(d).dump()).hexdigest())


def pubkey_sha1(data, ctx):
    return _cert_fn(data, lambda d: hashlib.sha1(_pub(d).dump()).hexdigest())


def pubkey_md5(data, ctx):
    return _cert_fn(data, lambda d: hashlib.md5(_pub(d).dump()).hexdigest())


def key_algorithm(data, ctx):
    return _cert_fn(data, lambda d: _pub(d).algorithm.upper())


def key_bits(data, ctx):
    return _cert_fn(data, lambda d: _pub(d).bit_size)


def _count(st, pid):
    return len(st["schemes"][pid]) if pid in st["schemes"] else "none"


def signer_count(data, ctx):
    def go(st):
        for pid in (V31, V3, V2):
            if pid in st["schemes"]:
                return len(st["schemes"][pid])
        return 1 if st["v1_certs"] else "none"
    return _with(data, go)


def v2_signer_count(data, ctx):
    return _with(data, lambda st: _count(st, V2))


def v3_signer_count(data, ctx):
    return _with(data, lambda st: _count(st, V3))


def _match(st, a, b):
    if a is None or b is None:
        return "none"
    return a == b


def _first(st, pid):
    sg = st["schemes"].get(pid)
    return sg[0][0] if sg and sg[0] else None


def v1_v2_match(data, ctx):
    return _with(data, lambda st: _match(st, st["v1_certs"][0] if st["v1_certs"] else None, _first(st, V2)))


def v2_v3_match(data, ctx):
    return _with(data, lambda st: _match(st, _first(st, V2), _first(st, V3)))


def _header(raw, key):
    """Main-section header value of a JAR manifest / .SF (continuation lines start with one space)."""
    txt = raw.decode("utf-8", "replace").replace("\r\n", "\n").replace("\r", "\n")
    txt = re.sub(r"\n ", "", txt).split("\n\n", 1)[0]
    for line in txt.split("\n"):
        k, sep, v = line.partition(":")
        if sep and k.strip().lower() == key.lower():
            return v.strip()
    return "none"


def mf_created_by(data, ctx):
    def go(st):
        try:
            return _header(st["z"].read("META-INF/MANIFEST.MF"), "Created-By")
        except KeyError:
            return "none"
    return _with(data, go)


def sf_created_by(data, ctx):
    return _with(data, lambda st: _header(st["z"].read(st["v1_sf"][0]), "Created-By") if st["v1_sf"] else "none")


def sf_apk_signed(data, ctx):
    return _with(data, lambda st: _header(st["z"].read(st["v1_sf"][0]), "X-Android-APK-Signed")
                 if st["v1_sf"] else "none")
