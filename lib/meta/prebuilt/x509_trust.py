"""Certificate corpus: fingerprint every certificate, collapse duplicates, find the trust claim the evidence does not
support (prebuilt, SPECULATIVE). fmt x509, aliases cert / trust / relation. D29 flavor ("Certificates appear in
binaries, packages, mail, captures, and disk images. Fingerprint each one, collapse duplicates, and identify the trust
claim unsupported by evidence.") -- never asked yet, the definitions below are this module's choice.

Input = the member: a corpus zip (cluster-style, labels as relation_variants.py: manifest `id` by path then basename,
else basename without extension; the manifest itself skipped) or ONE file (PEM bundle / PKCS7 / PE / pcap / eml).
An APK/JAR (AndroidManifest.xml or META-INF/MANIFEST.MF) is one member, not a corpus.
Certificates per member, deduped by DER within the member, in found order:
  PEM blocks (CERTIFICATE / X509 / TRUSTED CERTIFICATE / PKCS7, multi-block) | eml/MIME parts (S/MIME p7s/p7m,
  pkix-cert) decoded | zip entries (APK META-INF/*.RSA|DSA|EC, .crt/.cer/.der/.pem/.p7b) | a raw DER carve of every
  `30 8x .. 30 8x .. a0 03 02 01` Certificate in the bytes (DER cert, PKCS7 SignedData certificates [0], PE
  Authenticode dir 4, APK v2 signing block, pcap TLS Certificate handshake, disk image) -- carved spans must re-parse
  to exactly themselves.
Cert label = member label when the member holds one cert, else `<label>#<n>` (1-based, found order).
Trust model (no external roots): issuer candidates = corpus certs whose subject DN == this cert's issuer DN; the
signature is checked with each candidate's key via pycryptodome (Ed25519/Ed448 eddsa, RSA pkcs1_15 / PSS, ECDSA DSS
der, DSA DSS der; hash from the signature algorithm).
  unique_fingerprint_count      distinct DER sha256 over all certs (int)
  duplicate_fingerprint_groups  per DER sha256 with >= 2 cert labels: sorted labels; groups sorted (JSON)
  self_signed_ids               subject == issuer AND the signature verifies with its own key
  issuer_not_present_ids        not self-issued and no corpus subject equals its issuer
  signature_invalid_ids         an issuer candidate exists (self when self-issued) but no candidate key verifies it
  unsupported_trust_claim_ids   issuer_not_present + signature_invalid (sorted); `unsupported_trust_claim` (singular)
                                = the label when exactly one, else the sorted list
  trusted_ids / chain_valid_ids certs whose verified issuer links reach a self-signed root
  chain_order                   the longest verified chain, leaf first -> root (JSON); `chain_order_root_first` reversed
All `*_ids` are sorted cert labels, deduped by fingerprint is NOT applied (each copy keeps its label). No certificate
in the input / not parseable -> "none". One parse per input sha256 (never id())."""
import base64
import hashlib
import io
import json
import re
import struct
import zlib

_F = {
    "unique_fingerprint_count": "unique_fingerprint_count", "unique_certificate_count": "unique_fingerprint_count",
    "unique_cert_count": "unique_fingerprint_count", "distinct_fingerprint_count": "unique_fingerprint_count",
    "unique_sha256_fingerprint_count": "unique_fingerprint_count",
    "certificate_count": "certificate_count", "cert_count": "certificate_count",
    "duplicate_fingerprint_groups": "duplicate_fingerprint_groups",
    "duplicate_certificate_groups": "duplicate_fingerprint_groups", "duplicate_cert_groups": "duplicate_fingerprint_groups",
    "identical_fingerprint_groups": "duplicate_fingerprint_groups",
    "fingerprint_groups": "duplicate_fingerprint_groups", "sha256_fingerprint_groups": "duplicate_fingerprint_groups",
    "duplicate_fingerprint_group_count": "duplicate_fingerprint_group_count",
    "unique_fingerprints": "unique_fingerprints", "sha256_fingerprints": "unique_fingerprints",
    "issuer_not_present_ids": "issuer_not_present_ids", "missing_issuer_ids": "issuer_not_present_ids",
    "issuer_missing_ids": "issuer_not_present_ids", "orphan_cert_ids": "issuer_not_present_ids",
    "unknown_issuer_ids": "issuer_not_present_ids", "issuer_not_found_ids": "issuer_not_present_ids",
    "self_signed_ids": "self_signed_ids", "self_signed_cert_ids": "self_signed_ids", "root_ids": "self_signed_ids",
    "self_signed_count": "self_signed_count",
    "signature_invalid_ids": "signature_invalid_ids", "invalid_signature_ids": "signature_invalid_ids",
    "bad_signature_ids": "signature_invalid_ids", "signature_failure_ids": "signature_invalid_ids",
    "forged_cert_ids": "signature_invalid_ids", "forged_ids": "signature_invalid_ids",
    "unsupported_trust_claim": "unsupported_trust_claim",
    "unsupported_trust_claim_id": "unsupported_trust_claim",
    "unsupported_trust_claim_ids": "unsupported_trust_claim_ids",
    "unsupported_trust_claims": "unsupported_trust_claim_ids",
    "untrusted_ids": "unsupported_trust_claim_ids", "untrusted_cert_ids": "unsupported_trust_claim_ids",
    "trusted_ids": "trusted_ids", "chain_valid_ids": "trusted_ids", "verified_ids": "trusted_ids",
    "chain_order": "chain_order", "certificate_chain_order": "chain_order", "chain": "chain_order",
    "chain_order_leaf_first": "chain_order", "chain_order_root_first": "chain_order_root_first",
}
FIELDS = {
    ("x509", "unique_fingerprint_count"): "trust_value",
    ("x509", "unique_certificate_count"): "trust_value",
    ("x509", "unique_cert_count"): "trust_value",
    ("x509", "distinct_fingerprint_count"): "trust_value",
    ("x509", "unique_sha256_fingerprint_count"): "trust_value",
    ("x509", "certificate_count"): "trust_value",
    ("x509", "cert_count"): "trust_value",
    ("x509", "duplicate_fingerprint_groups"): "trust_value",
    ("x509", "duplicate_certificate_groups"): "trust_value",
    ("x509", "duplicate_cert_groups"): "trust_value",
    ("x509", "identical_fingerprint_groups"): "trust_value",
    ("x509", "fingerprint_groups"): "trust_value",
    ("x509", "sha256_fingerprint_groups"): "trust_value",
    ("x509", "duplicate_fingerprint_group_count"): "trust_value",
    ("x509", "unique_fingerprints"): "trust_value",
    ("x509", "sha256_fingerprints"): "trust_value",
    ("x509", "issuer_not_present_ids"): "trust_value",
    ("x509", "missing_issuer_ids"): "trust_value",
    ("x509", "issuer_missing_ids"): "trust_value",
    ("x509", "orphan_cert_ids"): "trust_value",
    ("x509", "unknown_issuer_ids"): "trust_value",
    ("x509", "issuer_not_found_ids"): "trust_value",
    ("x509", "self_signed_ids"): "trust_value",
    ("x509", "self_signed_cert_ids"): "trust_value",
    ("x509", "root_ids"): "trust_value",
    ("x509", "self_signed_count"): "trust_value",
    ("x509", "signature_invalid_ids"): "trust_value",
    ("x509", "invalid_signature_ids"): "trust_value",
    ("x509", "bad_signature_ids"): "trust_value",
    ("x509", "signature_failure_ids"): "trust_value",
    ("x509", "forged_cert_ids"): "trust_value",
    ("x509", "forged_ids"): "trust_value",
    ("x509", "unsupported_trust_claim"): "trust_value",
    ("x509", "unsupported_trust_claim_id"): "trust_value",
    ("x509", "unsupported_trust_claim_ids"): "trust_value",
    ("x509", "unsupported_trust_claims"): "trust_value",
    ("x509", "untrusted_ids"): "trust_value",
    ("x509", "untrusted_cert_ids"): "trust_value",
    ("x509", "trusted_ids"): "trust_value",
    ("x509", "chain_valid_ids"): "trust_value",
    ("x509", "verified_ids"): "trust_value",
    ("x509", "chain_order"): "trust_value",
    ("x509", "certificate_chain_order"): "trust_value",
    ("x509", "chain"): "trust_value",
    ("x509", "chain_order_leaf_first"): "trust_value",
    ("x509", "chain_order_root_first"): "trust_value",
    ("cert", "unique_fingerprint_count"): "trust_value",
    ("cert", "certificate_count"): "trust_value",
    ("cert", "duplicate_fingerprint_groups"): "trust_value",
    ("cert", "duplicate_certificate_groups"): "trust_value",
    ("cert", "unique_fingerprints"): "trust_value",
    ("cert", "issuer_not_present_ids"): "trust_value",
    ("cert", "missing_issuer_ids"): "trust_value",
    ("cert", "self_signed_ids"): "trust_value",
    ("cert", "signature_invalid_ids"): "trust_value",
    ("cert", "invalid_signature_ids"): "trust_value",
    ("cert", "unsupported_trust_claim"): "trust_value",
    ("cert", "unsupported_trust_claim_ids"): "trust_value",
    ("cert", "trusted_ids"): "trust_value",
    ("cert", "chain_order"): "trust_value",
    ("cert", "chain_order_root_first"): "trust_value",
    ("trust", "unique_fingerprint_count"): "trust_value",
    ("trust", "certificate_count"): "trust_value",
    ("trust", "duplicate_fingerprint_groups"): "trust_value",
    ("trust", "unique_fingerprints"): "trust_value",
    ("trust", "issuer_not_present_ids"): "trust_value",
    ("trust", "missing_issuer_ids"): "trust_value",
    ("trust", "self_signed_ids"): "trust_value",
    ("trust", "signature_invalid_ids"): "trust_value",
    ("trust", "invalid_signature_ids"): "trust_value",
    ("trust", "unsupported_trust_claim"): "trust_value",
    ("trust", "unsupported_trust_claim_ids"): "trust_value",
    ("trust", "unsupported_trust_claims"): "trust_value",
    ("trust", "untrusted_ids"): "trust_value",
    ("trust", "trusted_ids"): "trust_value",
    ("trust", "chain_order"): "trust_value",
    ("trust", "chain_order_root_first"): "trust_value",
    ("relation", "unique_fingerprint_count"): "trust_value",
    ("relation", "duplicate_fingerprint_groups"): "trust_value",
    ("relation", "duplicate_certificate_groups"): "trust_value",
    ("relation", "issuer_not_present_ids"): "trust_value",
    ("relation", "self_signed_ids"): "trust_value",
    ("relation", "signature_invalid_ids"): "trust_value",
    ("relation", "unsupported_trust_claim"): "trust_value",
    ("relation", "unsupported_trust_claim_ids"): "trust_value",
    ("relation", "chain_order"): "trust_value",
}

_PEM = re.compile(rb"-----BEGIN (X509 CERTIFICATE|TRUSTED CERTIFICATE|CERTIFICATE|PKCS7)-----(.*?)-----END \1-----",
                  re.S)
_CARVE = re.compile(rb"\x30[\x81\x82\x83]")
_CACHE = {}   # input sha256 -> analysis dict | None


# --- certificate extraction ----------------------------------------------------------------------------------------
def _der_len(b, i):
    """(content start, total end) of the DER TLV at i, or None."""
    if i + 2 > len(b):
        return None
    ln = b[i + 1]
    if ln < 0x80:
        return i + 2, i + 2 + ln
    n = ln & 0x7F
    if not 1 <= n <= 3 or i + 2 + n > len(b):
        return None
    v = int.from_bytes(b[i + 2:i + 2 + n], "big")
    return i + 2 + n, i + 2 + n + v


def _cert_ok(der):
    """asn1crypto Certificate if `der` is exactly one parseable certificate, else None."""
    try:
        from asn1crypto import x509
        c = x509.Certificate.load(der, strict=True)
        c["tbs_certificate"]["subject"].native   # noqa: B018 - force the parse
        c["tbs_certificate"]["subject_public_key_info"]["algorithm"]["algorithm"].native  # noqa: B018
        c["signature_value"].native  # noqa: B018
        return c
    except Exception:  # noqa: BLE001
        return None


def _carve(b, out):
    for m in _CARVE.finditer(b):
        i = m.start()
        tl = _der_len(b, i)
        if tl is None or tl[1] > len(b) or tl[1] - i < 64:
            continue
        s = tl[0]
        if b[s:s + 1] != b"\x30" or b[s + 1:s + 2] not in (b"\x81", b"\x82", b"\x83"):
            continue
        it = _der_len(b, s)
        if it is None or b[it[0]:it[0] + 4] != b"\xa0\x03\x02\x01" and b[it[0]:it[0] + 1] != b"\x02":
            continue
        der = b[i:tl[1]]
        if _cert_ok(der) is not None:
            out.append(bytes(der))


def _from_p7(der, out):
    try:
        from asn1crypto import cms
        ci = cms.ContentInfo.load(der)
        if ci["content_type"].native != "signed_data":
            return
        for c in ci["content"]["certificates"] or []:
            if c.name == "certificate":
                out.append(c.chosen.dump())
    except Exception:  # noqa: BLE001
        return


def _from_pem(b, out):
    for m in _PEM.finditer(b):
        try:
            der = base64.b64decode(re.sub(rb"[^A-Za-z0-9+/=]", b"", m.group(2)))
        except Exception:  # noqa: BLE001
            continue
        if m.group(1) == b"PKCS7":
            _from_p7(der, out)
        elif m.group(1) == b"TRUSTED CERTIFICATE":
            tl = _der_len(der, 0)          # OpenSSL trusted form: Certificate followed by the aux trust SEQUENCE
            if tl and _cert_ok(der[:tl[1]]) is not None:
                out.append(der[:tl[1]])
        elif _cert_ok(der) is not None:
            out.append(der)


def _from_mime(b, out):
    head = b[:4096]
    if not re.search(rb"(?im)^(content-type|mime-version|from|subject|received):", head):
        return
    try:
        import email
        msg = email.message_from_bytes(b)
        for part in msg.walk():
            if part.is_multipart():
                continue
            ct = (part.get_content_type() or "").lower()
            fn = (part.get_filename() or "").lower()
            if ("pkcs7" in ct or "pkix" in ct or "x509" in ct or "x-x509" in ct
                    or fn.endswith((".p7s", ".p7m", ".p7c", ".p7b", ".crt", ".cer", ".der", ".pem"))):
                payload = part.get_payload(decode=True) or b""
                _from_pem(payload, out)
                _from_p7(payload, out)
                _carve(payload, out)
    except Exception:  # noqa: BLE001
        return


def _from_zip(b, out):
    try:
        import zipfile
        z = zipfile.ZipFile(io.BytesIO(b))
        for zi in z.infolist()[:2000]:
            n = zi.filename.lower()
            if zi.is_dir() or zi.file_size > 4 << 20:
                continue
            if (n.startswith("meta-inf/") and n.endswith((".rsa", ".dsa", ".ec"))) or n.endswith(
                    (".crt", ".cer", ".der", ".pem", ".p7b", ".p7c", ".p7s")):
                try:
                    _member_certs(z.read(zi), out, depth=1)
                except Exception:  # noqa: BLE001
                    continue
    except Exception:  # noqa: BLE001
        return


def _member_certs(b, out=None, depth=0):
    out = [] if out is None else out
    if not b:
        return out
    _from_pem(b, out)
    if depth == 0:
        _from_mime(b, out)
        if b[:2] == b"PK":
            _from_zip(b, out)
    _carve(b, out)
    return out


def _uniq(ders):
    seen, res = set(), []
    for d in ders:
        h = hashlib.sha256(d).hexdigest()
        if h not in seen:
            seen.add(h)
            res.append(d)
    return res


# --- corpus members (relation_variants.py label convention, self-contained) ---------------------------------------
def _raw_read(data, zi):
    off = zi.header_offset
    if data[off:off + 4] != b"PK\x03\x04":
        return None
    nlen, xlen = struct.unpack_from("<HH", data, off + 26)
    start = off + 30 + nlen + xlen
    comp = data[start:start + zi.compress_size]
    if zi.compress_type == 0:
        return bytes(comp)
    if zi.compress_type == 8:
        return zlib.decompressobj(-15).decompress(comp)
    return None


def _members(data, ctx):
    """[(label, bytes)] of a corpus zip, or [(stem, data)] for a single non-corpus file."""
    stem = str((ctx or {}).get("member") or "member").replace("\\", "/").rsplit("/", 1)[-1]
    stem = stem.rsplit(".", 1)[0] if "." in stem.lstrip(".") else stem
    if data[:2] != b"PK":
        return [(stem, data)]
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        infos = [zi for zi in z.infolist() if not zi.is_dir() and not zi.filename.endswith(("/", "\\"))]
    except Exception:  # noqa: BLE001
        return [(stem, data)]
    names = {zi.filename for zi in infos}
    if "AndroidManifest.xml" in names or "META-INF/MANIFEST.MF" in names:
        return [(stem, data)]
    ids, manifests = {}, set()
    for zi in infos:
        base = zi.filename.replace("\\", "/").rsplit("/", 1)[-1].lower()
        if not base.endswith(".json") or not ("manifest" in base or base == "index.json"):
            continue
        try:
            doc = json.loads(z.read(zi).decode("utf-8-sig"))
        except Exception:  # noqa: BLE001
            if "manifest" in base:
                manifests.add(zi.filename)
            continue
        arts = doc if isinstance(doc, list) else next(
            (doc[k] for k in ("artifacts", "members", "files", "entries", "items")
             if isinstance(doc, dict) and isinstance(doc.get(k), list)), None)
        if arts is None or not all(isinstance(a, dict) for a in arts):
            if "manifest" in base:
                manifests.add(zi.filename)
            continue
        manifests.add(zi.filename)
        for a in arts:
            if a.get("id") is None:
                continue
            for k in ("path", "filename", "file", "name", "member", "member_path"):
                if isinstance(a.get(k), str) and a[k]:
                    ids.setdefault(a[k], str(a["id"]))
    out = []
    for zi in infos:
        if zi.filename in manifests:
            continue
        try:
            b = z.read(zi)
        except Exception:  # noqa: BLE001 - bad CRC / encrypted: raw local-header read
            try:
                b = _raw_read(data, zi)
            except Exception:  # noqa: BLE001
                b = None
        if b is None:
            continue
        path = zi.filename.replace("\\", "/")
        base = path.rsplit("/", 1)[-1]
        label = ids.get(zi.filename) or ids.get(path) or ids.get(base)
        if label is None:
            label = base.rsplit(".", 1)[0] if "." in base.lstrip(".") else base
        out.append((label, b))
    return out


# --- signature verification ----------------------------------------------------------------------------------------
_HASH = {"sha1": "SHA1", "sha224": "SHA224", "sha256": "SHA256", "sha384": "SHA384", "sha512": "SHA512", "md5": "MD5"}


def _hobj(name, msg):
    from Crypto.Hash import MD5, SHA1, SHA224, SHA256, SHA384, SHA512
    return {"SHA1": SHA1, "SHA224": SHA224, "SHA256": SHA256, "SHA384": SHA384, "SHA512": SHA512,
            "MD5": MD5}[name].new(msg)


def _verify(child, issuer):
    """True if child's signature verifies with issuer's public key, False if it does not, None if unsupported."""
    try:
        tbs = child["tbs_certificate"].dump()
        sig = child["signature_value"].native
        algo = child["signature_algorithm"]
        sa = algo.signature_algo
        spki = issuer["tbs_certificate"]["subject_public_key_info"]
        kalg = spki["algorithm"]["algorithm"].native
        if sa in ("ed25519", "ed448"):
            from Crypto.PublicKey import ECC
            from Crypto.Signature import eddsa
            key = ECC.import_key(spki.dump())
            try:
                eddsa.new(key, "rfc8032").verify(tbs, sig)
                return True
            except ValueError:
                return False
        hname = _HASH.get(algo.hash_algo)
        if hname is None:
            return None
        h = _hobj(hname, tbs)
        if sa == "rsassa_pkcs1v15" and kalg in ("rsa", "rsassa_pss"):
            from Crypto.PublicKey import RSA
            from Crypto.Signature import pkcs1_15
            try:
                pkcs1_15.new(RSA.import_key(spki.dump())).verify(h, sig)
                return True
            except (ValueError, TypeError):
                return False
        if sa == "rsassa_pss":
            from Crypto.PublicKey import RSA
            from Crypto.Signature import pss
            from Crypto.Signature.pss import MGF1
            params = algo["parameters"]
            mgf_h = params["mask_gen_algorithm"]["parameters"]["algorithm"].native
            slen = params["salt_length"].native
            try:
                pss.new(RSA.import_key(spki.dump()), mask_func=lambda x, y: MGF1(x, y, _hobj(_HASH[mgf_h], b"")),
                        salt_bytes=slen).verify(h, sig)
                return True
            except (ValueError, TypeError, KeyError):
                return False
        if sa in ("ecdsa", "dsa"):
            from Crypto.Signature import DSS
            if kalg == "ec":
                from Crypto.PublicKey import ECC
                key = ECC.import_key(spki.dump())
            elif kalg == "dsa":
                from Crypto.PublicKey import DSA
                key = DSA.import_key(spki.dump())
            else:
                return False
            try:
                DSS.new(key, "fips-186-3", encoding="der").verify(h, sig)
                return True
            except ValueError:
                return False
        return None
    except Exception:  # noqa: BLE001 - mismatched key type / malformed key -> does not verify
        return False


# --- analysis ------------------------------------------------------------------------------------------------------
def _analyze(data, ctx):
    key = hashlib.sha256(data).hexdigest() + "|" + str((ctx or {}).get("member") or "")
    if key in _CACHE:
        return _CACHE[key]
    recs = []   # dicts: label, der, sha, cert, subj, iss
    for label, b in _members(data, ctx):
        ders = _uniq(_member_certs(b))
        for n, der in enumerate(ders, 1):
            c = _cert_ok(der)
            if c is None:
                continue
            tbs = c["tbs_certificate"]
            recs.append({"label": label if len(ders) == 1 else f"{label}#{n}", "der": der,
                         "sha": hashlib.sha256(der).hexdigest(), "cert": c,
                         "subj": tbs["subject"].dump(), "iss": tbs["issuer"].dump()})
    res = None
    if recs:
        by_subj = {}
        for r in recs:
            by_subj.setdefault(r["subj"], []).append(r)
        for r in recs:
            r["self_issued"] = r["subj"] == r["iss"]
            cands = [r] if r["self_issued"] else by_subj.get(r["iss"], [])
            r["issuer_present"] = bool(cands)
            r["parents"] = [p for p in _uniq_recs(sorted(cands, key=lambda x: x["label"])) if _verify(r["cert"], p["cert"]) is True]
            r["self_signed"] = r["self_issued"] and bool(r["parents"])
            r["sig_invalid"] = bool(cands) and not r["parents"]
        res = recs
    if len(_CACHE) > 32:
        _CACHE.clear()
    _CACHE[key] = res
    return res


def _uniq_recs(rs):
    seen, out = set(), []
    for r in rs:
        if r["sha"] not in seen:
            seen.add(r["sha"])
            out.append(r)
    return out


def _trusted(r, memo, stack=()):
    if r["sha"] in memo:
        return memo[r["sha"]]
    if r["self_signed"]:
        memo[r["sha"]] = True
        return True
    if r["sha"] in stack:
        return False
    ok = any(_trusted(p, memo, stack + (r["sha"],)) for p in r["parents"] if p["sha"] != r["sha"])
    memo[r["sha"]] = ok
    return ok


def _chain(r, stack=()):
    """Longest verified chain from r upward (list of recs, r first)."""
    if r["self_signed"] or r["sha"] in stack:
        return [r]
    best = [r]
    for p in r["parents"]:
        if p["sha"] in stack or p["sha"] == r["sha"]:
            continue
        c = [r] + _chain(p, stack + (r["sha"],))
        if len(c) > len(best) or (len(c) == len(best) and [x["label"] for x in c] < [x["label"] for x in best]):
            best = c
    return best


def trust_value(data, ctx):
    ctx = ctx or {}
    if data is None:
        return None
    want = _F.get(ctx.get("field") or "")
    if want is None:
        return None
    recs = _analyze(data, ctx)
    if not recs:
        return "none"
    if want == "certificate_count":
        return len(recs)
    if want == "unique_fingerprint_count":
        return len({r["sha"] for r in recs})
    if want == "unique_fingerprints":
        return sorted({r["sha"] for r in recs})
    if want in ("duplicate_fingerprint_groups", "duplicate_fingerprint_group_count"):
        g = {}
        for r in recs:
            g.setdefault(r["sha"], set()).add(r["label"])
        groups = sorted(sorted(v) for v in g.values() if len(v) >= 2)
        return len(groups) if want.endswith("_count") else groups
    if want == "self_signed_ids":
        return sorted({r["label"] for r in recs if r["self_signed"]})
    if want == "self_signed_count":
        return len({r["label"] for r in recs if r["self_signed"]})
    if want == "issuer_not_present_ids":
        return sorted({r["label"] for r in recs if not r["issuer_present"]})
    if want == "signature_invalid_ids":
        return sorted({r["label"] for r in recs if r["sig_invalid"]})
    if want in ("unsupported_trust_claim", "unsupported_trust_claim_ids"):
        ids = sorted({r["label"] for r in recs if not r["issuer_present"] or r["sig_invalid"]})
        if want == "unsupported_trust_claim":
            return ids[0] if len(ids) == 1 else ("none" if not ids else ids)
        return ids
    if want == "trusted_ids":
        memo = {}
        return sorted({r["label"] for r in recs if _trusted(r, memo)})
    if want in ("chain_order", "chain_order_root_first"):
        best = None
        for r in sorted(recs, key=lambda x: x["label"]):
            c = _chain(r)
            if best is None or len(c) > len(best):
                best = c
        labels = [x["label"] for x in best]
        return labels[::-1] if want == "chain_order_root_first" else labels
    return None
