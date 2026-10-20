"""Attestation-token fixtures (row 87), written with jwcrypto + cryptography + zipfile (independent of lib.android).
usage: PYTHONPATH=tools/pylib python3 gen.py <outdir>"""
import base64, datetime, json, sys, zipfile, zlib
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import NameOID
from jwcrypto import jwe, jwk, jws

out = sys.argv[1]


def cert(subject, key, issuer=None, ikey=None):
    now = datetime.datetime(2026, 1, 1)
    n = lambda cn: x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    b = (x509.CertificateBuilder().subject_name(n(subject)).issuer_name(n(issuer or subject))
         .public_key(key.public_key()).serial_number(x509.random_serial_number())
         .not_valid_before(now).not_valid_after(now + datetime.timedelta(days=3650)))
    return b.sign(ikey or key, hashes.SHA256())


def der64(c):
    return base64.b64encode(c.public_bytes(serialization.Encoding.DER)).decode()


def sign(payload, key, alg, chain):
    s = jws.JWS(json.dumps(payload).encode())
    s.add_signature(jwk.JWK.from_pyca(key), alg=alg, protected=json.dumps({"alg": alg, "x5c": chain}))
    return s.serialize(compact=True)


def seal(inner, key_bytes, alg, enc, zipdef=False):
    hdr = {"alg": alg, "enc": enc}
    if zipdef:
        hdr["zip"] = "DEF"
    e = jwe.JWE(inner.encode(), json.dumps(hdr))
    e.add_recipient(jwk.JWK(kty="oct", k=base64.urlsafe_b64encode(key_bytes).rstrip(b"=").decode()))
    return e.serialize(compact=True)


def apk(name, files):
    with zipfile.ZipFile(f"{out}/{name}.apk", "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in files.items():
            z.writestr(n, b)


# 1. Play Integrity: JWE(A256KW, A256GCM) around an ES256 JWS; nonce = base64url(answer); key = base64 in an asset
eck = ec.generate_private_key(ec.SECP256R1())
pi_payload = lambda ans: {
    "requestDetails": {"requestPackageName": "com.huntress.attest", "timestampMillis": "1792000000000",
                       "nonce": base64.urlsafe_b64encode(ans.encode()).decode()},
    "appIntegrity": {"appRecognitionVerdict": "PLAY_RECOGNIZED", "packageName": "com.huntress.attest",
                     "certificateSha256Digest": ["6a6a1474b5cbbb2b1aa57e0bc3"], "versionCode": "42"},
    "deviceIntegrity": {"deviceRecognitionVerdict": ["MEETS_DEVICE_INTEGRITY"]},
    "accountDetails": {"appLicensingVerdict": "LICENSED"}}
k1 = bytes(range(0x40, 0x60))
t1 = seal(sign({"tokenPayloadExternal": pi_payload("ANS-3f9c21d07ab4e586")}, eck, "ES256",
               [der64(cert("Play Integrity Test", eck))]), k1, "A256KW", "A256GCM")
apk("att_play_integrity_jwe", {
    "assets/attestation.json": json.dumps({"integrityToken": t1}),
    "assets/config.properties": "integrity.decryption_key=%s\nintegrity.verification_key=MFkwEwYHKoZIzj0CAQ\n"
                                % base64.b64encode(k1).decode()})

# 2. SafetyNet: JWE(dir, A128CBC-HS256, zip=DEF) around an RS256 JWS with a 2-cert x5c chain; key = hex in res/raw
ca = rsa.generate_private_key(public_exponent=65537, key_size=2048)
leaf = rsa.generate_private_key(public_exponent=65537, key_size=2048)
chain = [der64(cert("attest.android.com", leaf, "GTS CA 1O1", ca)), der64(cert("GTS CA 1O1", ca))]
sn = {"nonce": base64.b64encode(b"ANS-b71e04c9d25a8f30|1792000000").decode(), "timestampMs": 1792000000000,
      "apkPackageName": "com.huntress.safetynet", "apkDigestSha256": "x9U0r7yWm5w2wqA9E8b3m1fGmJm2y0R6tS4nV1kL0aQ=",
      "apkCertificateDigestSha256": ["2rS0a8m0bM2y7JzWm4q8bS1vV6X7u0aT2e4nK9cL1oQ="], "ctsProfileMatch": True,
      "basicIntegrity": True, "evaluationType": "BASIC,HARDWARE_BACKED"}
k2 = bytes.fromhex("8c1f03a95d7e2b46c0d18e7f5a3b9264e1c7084d2fa65b3910de7c48a2f6b51e")
t2 = seal(sign(sn, leaf, "RS256", chain), k2, "dir", "A128CBC-HS256", zipdef=True)
apk("att_safetynet_dir_cbc", {
    "res/raw/attest_response.txt": "jwsResult: " + t2 + "\n",
    "res/raw/keys.txt": "# do not ship\nCEK=" + k2.hex() + "\n"})

# 3. DECOY: layout of 1, but the shipped key is one byte off (near miss) -> the token cannot be opened
k3 = bytes(range(0x40, 0x60))
t3 = seal(sign({"tokenPayloadExternal": pi_payload("ANS-d4a07c6e19b2f358")}, eck, "ES256",
               [der64(cert("Play Integrity Test", eck))]), k3, "A256KW", "A256GCM")
apk("att_decoy_wrong_key", {
    "assets/attestation.json": json.dumps({"integrityToken": t3}),
    "assets/config.properties": "integrity.decryption_key=%s\n" % base64.b64encode(k3[:-1] + b"\x00").decode()})
