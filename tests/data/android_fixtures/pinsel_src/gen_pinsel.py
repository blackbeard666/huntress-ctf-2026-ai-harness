#!/usr/bin/env python3
"""Generate the pinsel_* fixtures ('challenge-signed' secondary module, coverage atlas row 83: N payloads ship, the
pinned digest / detached signature picks the one the host loads).
usage: gen_pinsel.py <variant: host_sha256 | rsa_sig | manifest_b64 | decoy_nearmiss> <out.apk>
Each payload is its own javac --release 8 class (com.huntress.arena.payload.Module.ANSWER) converted with dex2jar's
d2j-jar2dex; digests come from `openssl dgst`, the RSA key / PKCS#1 v1.5 signature from `openssl genpkey` /
`openssl dgst -sign`, the host Loader (holding the pin) is compiled after the digests; zipfile lays out the APK."""
import base64, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))


def dex(tag, body, cls):
    d = tmp / tag
    (d / "src").mkdir(parents=True)
    (d / "src" / f"{cls}.java").write_text(body)
    (d / "cls").mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(d / "cls"), str(d / "src" / f"{cls}.java")], check=True)
    with zipfile.ZipFile(d / "x.jar", "w") as z:
        for f in (d / "cls").rglob("*.class"):
            z.write(f, f.relative_to(d / "cls").as_posix())
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(d / "x.dex"), str(d / "x.jar")],
                   check=True, capture_output=True)
    return (d / "x.dex").read_bytes()


def payload(ans):
    return dex("p" + ans[-4:], """package com.huntress.arena.payload;
public final class Module {
  public static final String ANSWER = "%s";
  public String moduleContract() { return ANSWER; }
}
""" % ans, "Module")


def host(pins):
    return dex("host", """package com.huntress.arena;
public final class Loader {
  static final String[] PINNED = {%s};
  public static boolean accept(String digest) { for (String p : PINNED) if (p.equals(digest)) return true; return false; }
}
""" % ", ".join('"%s"' % p for p in pins), "Loader")


def ossl(*args, data=None):
    return subprocess.run(["openssl", *args], input=data, check=True, capture_output=True).stdout


def sha256(b):
    return ossl("dgst", "-sha256", "-binary", data=b)


files = {}
A, B = "ANS-5a1d93c07e4b28f6", "ANS-c4e82b7f19d0a365"
pa, pb = payload(A), payload(B)
if variant in ("host_sha256", "decoy_nearmiss"):
    pin = sha256(pb).hex()
    if variant == "decoy_nearmiss":
        pin = pin[:-1] + ("0" if pin[-1] != "0" else "1")
    files = {"classes.dex": host(["sha256-of-assets/payload_b.dex", pin]),
             "assets/payload_a.dex": pa, "assets/payload_b.dex": pb}
elif variant == "rsa_sig":
    key = tmp / "k.pem"
    ossl("genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(key))
    (tmp / "m2.bin").write_bytes(pb)
    sig = ossl("dgst", "-sha256", "-sign", str(key), str(tmp / "m2.bin"))
    files = {"classes.dex": host(["module.sig"]), "assets/modules/m1.bin": pa, "assets/modules/m2.bin": pb,
             "assets/modules/module.sig": sig, "assets/modules/module_pub.pem": ossl("pkey", "-in", str(key), "-pubout")}
elif variant == "manifest_b64":
    # both payloads are on the host allowlist (base64 sha256), but payload_a was swapped after signing: MANIFEST.MF
    # still holds the digest of the ORIGINAL payload_a, so only payload_b passes v1 verification
    orig_a = payload("ANS-0000000000000000")
    files = {"classes.dex": host([base64.b64encode(sha256(pa)).decode(), base64.b64encode(sha256(pb)).decode()]),
             "assets/payload_a.dex": pa, "assets/payload_b.dex": pb}
    mf = "Manifest-Version: 1.0\r\nCreated-By: gen_pinsel\r\n\r\n"
    for n, b in (("classes.dex", files["classes.dex"]), ("assets/payload_a.dex", orig_a), ("assets/payload_b.dex", pb)):
        mf += f"Name: {n}\r\nSHA-256-Digest: {base64.b64encode(sha256(b)).decode()}\r\n\r\n"
    files["META-INF/MANIFEST.MF"] = mf.encode()
else:
    sys.exit("variant?")
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    if "META-INF/MANIFEST.MF" in files:
        z.writestr("META-INF/MANIFEST.MF", files.pop("META-INF/MANIFEST.MF"))
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"codec": "signed-module", "data": "load the pinned payload"}')
    for n, b in files.items():
        z.writestr(n, b)
shutil.rmtree(tmp)
print(out)
