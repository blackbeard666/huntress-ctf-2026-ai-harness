"""Play Integrity / SafetyNet verdict-select fixtures (integrity_verdict_scan). Writers: keytool (signer), json +
jwcrypto (RS256 JWS), python zipfile, apksigner sign. Run: PYTHONPATH=tools/pylib python3 gen.py <outdir>"""
import base64, hashlib, json, os, subprocess, sys, tempfile, zipfile
from jwcrypto import jwk, jws

out = sys.argv[1]
tmp = tempfile.mkdtemp()
ks = os.path.join(tmp, "k.jks")
subprocess.run(["keytool", "-genkeypair", "-keystore", ks, "-storepass", "android", "-keypass", "android", "-alias",
                "k", "-keyalg", "RSA", "-keysize", "2048", "-validity", "9000", "-dname", "CN=Verdict Fixture, O=HCTF"],
               check=True, capture_output=True)
der = subprocess.run(["keytool", "-exportcert", "-keystore", ks, "-storepass", "android", "-alias", "k"],
                     check=True, capture_output=True).stdout
CERT = base64.b64encode(hashlib.sha256(der).digest()).decode().rstrip("=")
FOREIGN = base64.b64encode(hashlib.sha256(b"other-signer").digest()).decode().rstrip("=")
PKG = "com.hctf.verdict"
NONCE = base64.urlsafe_b64encode(hashlib.sha256(b"session-7731-host").digest()).decode().rstrip("=")
BAD_NONCE = base64.urlsafe_b64encode(hashlib.sha256(b"session-0000-replay").digest()).decode().rstrip("=")


def pi(app, dev, lic, cert=CERT, nonce=NONCE):
    return {"requestDetails": {"requestPackageName": PKG, "nonce": nonce, "timestampMillis": "1761200000000"},
            "appIntegrity": {"appRecognitionVerdict": app, "packageName": PKG, "certificateSha256Digest": [cert],
                             "versionCode": "42"},
            "deviceIntegrity": {"deviceRecognitionVerdict": dev},
            "accountDetails": {"appLicensingVerdict": lic}}


def apk(name, files):
    raw = os.path.join(tmp, name + ".unsigned")
    with zipfile.ZipFile(raw, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in files.items():
            z.writestr(n, b)
    subprocess.run(["apksigner", "sign", "--ks", ks, "--ks-pass", "pass:android", "--min-sdk-version", "24",
                    "--v1-signing-enabled", "true", "--v4-signing-enabled", "false", "--out", os.path.join(out, name + ".apk"), raw],
                   check=True, capture_output=True)


def plain(name, clean_ok):
    rows = [
        {"label": "stale", "payload": pi("UNRECOGNIZED_VERSION", ["MEETS_DEVICE_INTEGRITY"], "LICENSED"),
         "unlock": "ANS-0d1e2f3a4b5c6d7e"},
        {"label": "emulator", "payload": pi("PLAY_RECOGNIZED", ["MEETS_BASIC_INTEGRITY", "MEETS_VIRTUAL_INTEGRITY"],
                                            "LICENSED"), "unlock": "ANS-1a2b3c4d5e6f7081"},
        {"label": "resigned", "payload": pi("PLAY_RECOGNIZED", ["MEETS_DEVICE_INTEGRITY"], "LICENSED", cert=FOREIGN),
         "unlock": "ANS-2b3c4d5e6f708192"},
        {"label": "replay", "payload": pi("PLAY_RECOGNIZED", ["MEETS_BASIC_INTEGRITY", "MEETS_DEVICE_INTEGRITY"],
                                          "LICENSED", nonce=BAD_NONCE), "unlock": "ANS-3c4d5e6f708192a3"},
        {"label": "unlicensed", "payload": pi("PLAY_RECOGNIZED", ["MEETS_STRONG_INTEGRITY"], "UNLICENSED"),
         "unlock": "ANS-4d5e6f708192a3b4"},
    ]
    if clean_ok:
        rows.insert(2, {"label": "clean", "payload": pi("PLAY_RECOGNIZED", ["MEETS_BASIC_INTEGRITY",
                        "MEETS_DEVICE_INTEGRITY", "MEETS_STRONG_INTEGRITY"], "LICENSED"),
                        "unlock": "ANS-9e4b7c21d03f5a68"})
    apk(name, {"assets/integrity/request.json": json.dumps({"package": PKG, "nonce": NONCE}),
               "assets/integrity/verdicts.json": json.dumps({"responses": rows}, indent=1)})


def legacy(name):
    key = jwk.JWK.generate(kty="RSA", size=2048)

    def tok(claims):
        s = jws.JWS(json.dumps(claims).encode())
        s.add_signature(key, alg="RS256", protected=json.dumps({"alg": "RS256", "typ": "JWT"}))
        return s.serialize(compact=True)
    snonce = base64.b64encode(hashlib.sha256(b"challenge-5fd0-host").digest()).decode()
    base = {"timestampMs": 1761200000000, "apkPackageName": PKG, "apkCertificateDigestSha256": [CERT]}
    atts = [
        {"jws": tok(dict(base, nonce=snonce, ctsProfileMatch=False, basicIntegrity=True, evaluationType="BASIC",
                         advice="RESTORE_TO_FACTORY_ROM")), "reward": "ANS-5e6f708192a3b4c5"},
        {"jws": tok(dict(base, nonce=snonce, ctsProfileMatch=True, basicIntegrity=True,
                         evaluationType="BASIC,HARDWARE_BACKED")), "reward": "ANS-c71f2a9e04b85d36"},
        {"jws": tok({"tokenPayloadExternal": pi("UNEVALUATED", [], "UNEVALUATED", nonce=snonce)}),
         "reward": "ANS-6f708192a3b4c5d6"},
    ]
    apk(name, {"res/raw/session.json": json.dumps({"challenge": "challenge-5fd0-host"}),
               "res/raw/attest.json": json.dumps({"attempts": atts})})


plain("ivs_plain_multi", True)
plain("ivs_decoy_no_clean", False)
legacy("ivs_safetynet_jws")
