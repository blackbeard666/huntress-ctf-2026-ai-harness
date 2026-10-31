#!/usr/bin/env python3
"""Generate the ckx_* fixtures (coverage atlas: v2-checksum-intrinsics-crc32-adler). A v2 `Release.code(Context)` stores
ctx in a static and a separate token() folds 'integrity checks' over the APK's OWN bytes into the answer:
  dex_cert    ZipFile(getPackageCodePath()).getInputStream(classes.dex) -> CRC32.update(byte[],off,len) loop / getValue
              (unsigned 32-bit in a long) and MessageDigest SHA-256 of getPackageInfo(GET_SIGNATURES).signatures[0]
              .toByteArray() (the DER cert of META-INF/*.RSA), folded big-endian by hand + ByteBuffer.wrap(d, 8, 8).getLong
  asset_adler getAssets().open("seed.bin") read loop -> Checksum ck = new Adler32() (invoke-interface update(int) /
              update(byte[],off,len) / getValue), MD5 digest folded big-endian, SHA-1 of signingInfo
              getApkContentsSigners()[0] -> ByteBuffer.wrap(..).order(LITTLE_ENDIAN).getLong, Arrays.hashCode(byte[]),
              String.hashCode, CRC32 update(int)
  decoy_pin   dex_cert behind a cert pin that is a near-miss of the real SHA-256: the clean install returns "tampered"
usage: gen_ckx.py <variant> <out.apk>
Build: javac --release 8 (app + android.* stubs) -> d2j-jar2dex; manifest by apktool's aapt2 link; zipfile adds assets +
classes.dex; keytool RSA + apksigner v1+v2.
ORACLE (independent of lib.android): the host JVM runs Release.code() with the REAL java.util.zip.CRC32 / Adler32 /
ZipFile, java.security.MessageDigest and java.nio.ByteBuffer, on stubs answering from the SIGNED APK itself: assets and
getPackageCodePath via java.util.zip.ZipFile on the signed apk, the signer DER from
`openssl pkcs7 -print_certs | openssl x509 -outform DER` on META-INF/*.RSA, the package from `aapt dump badging`."""
import re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = {"dex_cert": "com.huntress.arena.ckx1", "asset_adler": "com.huntress.arena.ckx2",
       "decoy_pin": "com.huntress.arena.ckx3"}[variant]
STUBS = {
    "android/content/res/AssetManager.java": """package android.content.res;
public class AssetManager { public java.io.InputStream open(String n) throws java.io.IOException {
  java.util.zip.ZipFile z = new java.util.zip.ZipFile(System.getProperty("ctx.apk"));
  java.util.zip.ZipEntry e = z.getEntry("assets/" + n);
  if (e == null) throw new java.io.FileNotFoundException(n);
  return z.getInputStream(e); } }""",
    "android/content/pm/Signature.java": """package android.content.pm;
public class Signature { private final byte[] b; public Signature(byte[] b) { this.b = b; }
  public byte[] toByteArray() { return b.clone(); }
  public int hashCode() { return java.util.Arrays.hashCode(b); } }""",
    "android/content/pm/SigningInfo.java": """package android.content.pm;
public class SigningInfo { public Signature[] getApkContentsSigners() { return Stub.sigs(); } }""",
    "android/content/pm/Stub.java": """package android.content.pm;
public class Stub {
  public static Signature[] sigs() {
    try { return new Signature[] { new Signature(java.nio.file.Files.readAllBytes(java.nio.file.Paths.get(System.getProperty("ctx.cert")))) }; }
    catch (java.io.IOException e) { throw new RuntimeException(e); } } }""",
    "android/content/pm/PackageInfo.java": """package android.content.pm;
public class PackageInfo { public Signature[] signatures; public SigningInfo signingInfo; }""",
    "android/content/pm/PackageManager.java": """package android.content.pm;
public class PackageManager {
  public static final int GET_SIGNATURES = 64, GET_SIGNING_CERTIFICATES = 0x08000000;
  public static class NameNotFoundException extends Exception { public NameNotFoundException(String s) { super(s); } }
  public PackageInfo getPackageInfo(String p, int f) throws NameNotFoundException {
    if (!p.equals(System.getProperty("ctx.pkg"))) throw new NameNotFoundException(p);
    PackageInfo i = new PackageInfo();
    if ((f & GET_SIGNATURES) != 0) i.signatures = Stub.sigs();
    if ((f & GET_SIGNING_CERTIFICATES) != 0) i.signingInfo = new SigningInfo();
    return i; } }""",
    "android/content/Context.java": """package android.content;
public class Context {
  public android.content.pm.PackageManager getPackageManager() { return new android.content.pm.PackageManager(); }
  public String getPackageName() { return System.getProperty("ctx.pkg"); }
  public String getPackageCodePath() { return System.getProperty("ctx.apk"); }
  public android.content.res.AssetManager getAssets() { return new android.content.res.AssetManager(); } }""",
}
DEX_CERT = """    ZipFile z = new ZipFile(ctx.getPackageCodePath());
    InputStream in = z.getInputStream(z.getEntry("classes.dex"));
    CRC32 crc = new CRC32();
    byte[] buf = new byte[1024];
    int n;
    while ((n = in.read(buf)) > 0) crc.update(buf, 0, n);
    in.close();
    z.close();
    PackageInfo pi = ctx.getPackageManager().getPackageInfo(ctx.getPackageName(), PackageManager.GET_SIGNATURES);
    byte[] d = MessageDigest.getInstance("SHA-256").digest(pi.signatures[0].toByteArray());
%(gate)s    long h = 0;
    for (int i = 0; i < 8; i++) h = (h << 8) | (d[i] & 0xff);
    h ^= crc.getValue() << 13;
    h ^= ByteBuffer.wrap(d, 8, 8).getLong() >>> 7;
    return hex(h);
"""
GATE = """    StringBuilder sb = new StringBuilder();
    for (byte x : d) sb.append(String.format("%%02x", x & 0xff));
    if (!sb.toString().equals("%s")) return "tampered";
"""
ASSET_ADLER = """    InputStream in = ctx.getAssets().open("seed.bin");
    byte[] s = new byte[256];
    int n = 0, x;
    while ((x = in.read()) != -1 && n < s.length) s[n++] = (byte) x;
    in.close();
    Checksum ck = new Adler32();
    for (int i = 0; i < 4; i++) ck.update(s[i]);
    ck.update(s, 4, n - 4);
    CRC32 c2 = new CRC32();
    for (int i = 0; i < n; i += 3) c2.update(s[i] ^ 0x5a);
    MessageDigest md = MessageDigest.getInstance("MD5");
    md.update(s, 0, n);
    byte[] m = md.digest();
    long hi = 0;
    for (int i = 0; i < 4; i++) hi = (hi << 8) | (m[i] & 0xff);
    PackageInfo pi = ctx.getPackageManager().getPackageInfo(ctx.getPackageName(), PackageManager.GET_SIGNING_CERTIFICATES);
    byte[] cd = MessageDigest.getInstance("SHA-1").digest(pi.signingInfo.getApkContentsSigners()[0].toByteArray());
    long le = ByteBuffer.wrap(cd).order(ByteOrder.LITTLE_ENDIAN).getLong();
    long h = (ck.getValue() << 32) | (hi ^ c2.getValue());
    h ^= le;
    h += (long) Arrays.hashCode(s) * 31 + ctx.getPackageName().hashCode();
    return hex(h);
"""
APP = """package %(pkg)s;
import android.content.Context;
import android.content.pm.*;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.zip.*;
public final class Release {
  static Context ctx;
  static String hex(long h) { String s = Long.toHexString(h); while (s.length() < 16) s = "0" + s; return "ANS-" + s; }
  public static String code(Context c) { ctx = c; return token(); }
  static String token() {
    try {
%(body)s    } catch (Exception e) { return "error"; }
  }
}"""
PROBE = """package %(pkg)s;
public class Probe { public static void main(String[] a) { System.out.println(Release.code(new android.content.Context())); } }"""
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%(pkg)s"
  android:versionCode="3" android:versionName="1.3">
  <application android:label="arena"/>
</manifest>"""


def build(tmp, src, cls, body):
    pdir = PKG.replace(".", "/")
    files = dict(STUBS)
    files[f"{pdir}/Release.java"] = APP % {"pkg": PKG, "body": body}
    files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG}
    for rel, b in files.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_text(b)
    if cls.exists():
        shutil.rmtree(cls)
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    app = tmp / "app"
    if app.exists():
        shutil.rmtree(app)
    shutil.copytree(cls, app)
    for junk in ("android", f"{pdir}/Probe.class"):
        p = app / junk
        shutil.rmtree(p) if p.is_dir() else p.unlink()
    shutil.make_archive(str(tmp / "app"), "zip", app)
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
                   check=True, capture_output=True)


tmp = Path(tempfile.mkdtemp())
src, cls = tmp / "src", tmp / "cls"
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)
(tmp / "AndroidManifest.xml").write_text(MAN % {"pkg": PKG})
subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                str(tmp / "android-framework.jar"), "-o", str(tmp / "base.apk")], check=True)
subprocess.run(["keytool", "-genkeypair", "-keystore", str(tmp / "k.jks"), "-storepass", "android", "-keypass", "android",
                "-alias", "k", "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000",
                "-dname", f"CN=Arena {variant}, O=Huntress Fixtures, C=US"], check=True, capture_output=True)
subprocess.run(["keytool", "-exportcert", "-keystore", str(tmp / "k.jks"), "-storepass", "android", "-alias", "k",
                "-file", str(tmp / "pre.der")], check=True, capture_output=True)
if variant == "decoy_pin":  # pin = the real cert SHA-256 (openssl dgst on keytool's export) with its last digit bumped
    real = subprocess.run(["openssl", "dgst", "-sha256", "-r", str(tmp / "pre.der")], check=True, capture_output=True,
                          text=True).stdout.split()[0]
    pin = real[:-1] + "0123456789abcdef"[("0123456789abcdef".index(real[-1]) + 1) % 16]
    body = DEX_CERT % {"gate": GATE % pin}
else:
    body = DEX_CERT % {"gate": ""} if variant == "dex_cert" else ASSET_ADLER
build(tmp, src, cls, body)
assets = {"seed.bin": bytes((i * 73 + 41) & 0xFF for i in range(200))} if variant == "asset_adler" else {}
with zipfile.ZipFile(tmp / "base.apk") as zin, zipfile.ZipFile(tmp / "unsigned.apk", "w", zipfile.ZIP_DEFLATED) as z:
    for n in zin.namelist():
        z.writestr(n, zin.read(n))
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
    for n, b in assets.items():
        z.writestr("assets/" + n, b)
subprocess.run(["apksigner", "sign", "--ks", str(tmp / "k.jks"), "--ks-pass", "pass:android", "--min-sdk-version", "21",
                "--v1-signing-enabled", "true", "--v2-signing-enabled", "true", "--out", str(out), str(tmp / "unsigned.apk")],
               check=True)
# --- oracle: openssl cert DER + aapt badging + the host JVM (real CRC32 / Adler32 / MessageDigest) on the signed APK ---
rsa = next(n for n in zipfile.ZipFile(out).namelist() if re.fullmatch(r"META-INF/[^/]+\.(?:RSA|DSA|EC)", n))
(tmp / "sig.p7").write_bytes(zipfile.ZipFile(out).read(rsa))
pem = subprocess.run(["openssl", "pkcs7", "-inform", "DER", "-in", str(tmp / "sig.p7"), "-print_certs"], check=True,
                     capture_output=True).stdout
subprocess.run(["openssl", "x509", "-outform", "DER", "-out", str(tmp / "cert.der")], input=pem, check=True)
badging = subprocess.run(["aapt", "dump", "badging", str(out)], capture_output=True, text=True).stdout
pkg = re.search(r"package: name='([^']+)'", badging)[1]
shown = subprocess.run(["java", f"-Dctx.apk={out}", f"-Dctx.cert={tmp / 'cert.der'}", f"-Dctx.pkg={pkg}",
                        "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
shutil.rmtree(tmp)
print(f"pkg={pkg} oracle={shown}")
