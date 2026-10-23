"""Fixture generator for key_attestation_scan (row 93). Writer: pyasn1 (KeyDescription / RootOfTrust /
AttestationApplicationId DER) + cryptography x509 builder (cert with the 1.3.6.1.4.1.11129.2.1.17 extension) + `zip`.
Usage: gen_ka.py <variant> <out.apk>"""
import base64, datetime, json, os, subprocess, sys, tempfile
from pyasn1.type import univ, namedtype, tag
from pyasn1.codec.der import encoder
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


def expl(n, v):
    return univ.Any(encoder.encode(v), tagSet=univ.Any.tagSet.tagExplicitly(
        tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, n)))


def authlist(items):
    return seq(*[expl(n, v) for n, v in items])


def seq(*vals):
    s = univ.SequenceOf(componentType=univ.Any())
    for i, v in enumerate(vals):
        s[i] = v if isinstance(v, univ.Any) else univ.Any(encoder.encode(v))
    return s


def setof(*vals):
    s = univ.SetOf(componentType=univ.Any())
    for i, v in enumerate(vals):
        s[i] = univ.Any(encoder.encode(v))
    return s


def key_description(challenge, boot_state=0, locked=True, boot_hash=b"\x11" * 32, pkg=b"com.huntress.attest"):
    rot = seq(univ.OctetString(b"\xa5" * 32), univ.Boolean(locked), univ.Enumerated(boot_state),
              univ.OctetString(boot_hash))
    appid = seq(setof(seq(univ.OctetString(pkg), univ.Integer(7))), setof(univ.OctetString(bytes(range(32)))))
    sw = authlist([(701, univ.Integer(1760000000000)), (709, univ.OctetString(encoder.encode(appid)))])
    hw = authlist([(1, setof(univ.Integer(2))), (2, univ.Integer(3)), (3, univ.Integer(256)),
                   (704, rot), (705, univ.Integer(140000)), (706, univ.Integer(202609))])
    kd = seq(univ.Integer(200), univ.Enumerated(1), univ.Integer(200), univ.Enumerated(1),
             univ.OctetString(challenge), univ.OctetString(b""), sw, hw)
    return encoder.encode(kd)


def cert(cn, ext_der=None, issuer_key=None, issuer_cn=None):
    k = ec.generate_private_key(ec.SECP256R1())
    b = (x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)]))
         .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, issuer_cn or cn)]))
         .public_key(k.public_key()).serial_number(x509.random_serial_number())
         .not_valid_before(datetime.datetime(2026, 1, 1)).not_valid_after(datetime.datetime(2036, 1, 1)))
    if ext_der:
        b = b.add_extension(x509.UnrecognizedExtension(x509.ObjectIdentifier("1.3.6.1.4.1.11129.2.1.17"), ext_der),
                            critical=False)
    return b.sign(issuer_key or k, hashes.SHA256()), k


def main(variant, out):
    tok = {"pem_challenge": "ANS-3f9a0c71d2e48b56", "puzzle_b64_boothash": "ANS-a1c0ffee5d2b7e94",
           "raw_der_hexchallenge": "ANS-07be41d9c3f2a688"}.get(variant)
    root, rk = cert("Huntress Attestation Root")
    d = tempfile.mkdtemp()
    files = {}
    if variant == "pem_challenge":
        leaf, _ = cert("Android Keystore Key", key_description(tok.encode()), rk, "Huntress Attestation Root")
        files["assets/attestation_chain.pem"] = b"".join(c.public_bytes(serialization.Encoding.PEM) for c in (leaf, root))
    elif variant == "puzzle_b64_boothash":
        leaf, _ = cert("Android Keystore Key", key_description(b"nonce-8842", boot_state=0,
                       boot_hash=tok.encode() + b"\x00" * 12), rk, "Huntress Attestation Root")
        files["assets/huntress_puzzle.json"] = json.dumps({"codec": "attestation", "chain": [
            base64.b64encode(leaf.public_bytes(serialization.Encoding.DER)).decode(),
            base64.b64encode(root.public_bytes(serialization.Encoding.DER)).decode()]}).encode()
    elif variant == "raw_der_hexchallenge":
        leaf, _ = cert("Android Keystore Key", key_description(tok.encode().hex().encode(), boot_state=2, locked=False),
                       rk, "Huntress Attestation Root")
        files["res/raw/attest.der"] = leaf.public_bytes(serialization.Encoding.DER)
    elif variant == "decoy_nearmiss":
        # attestation challenge is a near-miss (non-hex char); a plain cert (no attestation ext) carries a real token
        leaf, _ = cert("Android Keystore Key", key_description(b"ANS-0123456789abcdeZ"), rk, "Huntress Attestation Root")
        other, _ = cert("ANS-5555aaaa5555aaaa")
        files["assets/attestation_chain.pem"] = b"".join(c.public_bytes(serialization.Encoding.PEM) for c in (leaf, root))
        files["res/raw/server.der"] = other.public_bytes(serialization.Encoding.DER)
    files["AndroidManifest.xml"] = b"\x03\x00\x08\x00" + b"\x00" * 60
    files["classes.dex"] = b"dex\n035\x00" + b"\x00" * 104 + b"verifiedBootState\x00SELF_SIGNED\x00"
    for n, b in files.items():
        os.makedirs(os.path.join(d, os.path.dirname(n)), exist_ok=True)
        open(os.path.join(d, n), "wb").write(b)
    out = os.path.abspath(out)
    if os.path.exists(out):
        os.remove(out)
    subprocess.run(["zip", "-qrX", out] + sorted(files), cwd=d, check=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
