#!/usr/bin/env python3
"""Generate the selfint_* fixtures (coverage atlas: analysis-self-integrity-stubs, rows 49 / 99). A v2-chain
`Release.code(Context)` folds the APK's OWN integrity facts into a 64-bit seed: signatures[0] (GET_SIGNATURES |
GET_SIGNING_CERTIFICATES / signingInfo.getApkContentsSigners) -> toByteArray -> MessageDigest SHA-256 / SHA-1 / MD5 ->
ByteBuffer.wrap(d).getLong() / order(LITTLE_ENDIAN).getLong(8) / `v = v*31 + b`; Signature.hashCode; ZipFile(
getApplicationInfo().sourceDir) / JarFile(getPackageCodePath()) getEntry(classes.dex | asset).getCrc / getSize and a
CRC32 / MD5 over getInputStream(entry) (the shipped dex bytes); Adler32 over the puzzle asset; getInstallerPackageName.
usage: gen_selfint.py <variant: sig_bb | fold_le | decoy_pin> <out.apk>
Build: javac --release 8 (app + android.* stubs) -> d2j-jar2dex; manifest by apktool's aapt2 link; zipfile adds assets
+ classes.dex; keytool RSA + apksigner v1+v2.
ORACLE (independent of lib.android): the host JVM runs Release.code() with stubs answering from the SIGNED APK:
sourceDir / getPackageCodePath = the signed apk path read by the real java.util.zip.ZipFile / java.util.jar.JarFile,
real java.nio.ByteBuffer / MessageDigest / CRC32 / Adler32, the signer DER from `openssl pkcs7 -print_certs |
openssl x509 -outform DER` on META-INF/*.RSA, installer com.android.vending."""
import re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = {"sig_bb": "com.huntress.arena.si1", "fold_le": "com.huntress.arena.si2", "decoy_pin": "com.huntress.arena.si3"}[variant]
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
    "android/content/pm/ApplicationInfo.java": """package android.content.pm;
public class ApplicationInfo { public String sourceDir = System.getProperty("ctx.apk"); public int flags = 0x38c8be44; }""",
    "android/content/pm/PackageManager.java": """package android.content.pm;
public class PackageManager {
  public static final int GET_SIGNATURES = 64, GET_SIGNING_CERTIFICATES = 0x08000000;
  public static class NameNotFoundException extends Exception { public NameNotFoundException(String s) { super(s); } }
  public String getInstallerPackageName(String p) { return p.equals(System.getProperty("ctx.pkg")) ? "com.android.vending" : null; }
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
  public android.content.res.AssetManager getAssets() { return new android.content.res.AssetManager(); }
  public android.content.pm.ApplicationInfo getApplicationInfo() { return new android.content.pm.ApplicationInfo(); } }""",
}
SIG_BB = """      String pkg = c.getPackageName();
      PackageManager pm = c.getPackageManager();
      PackageInfo pi = pm.getPackageInfo(pkg, PackageManager.GET_SIGNATURES | PackageManager.GET_SIGNING_CERTIFICATES);
      Signature s = pi.signatures[0];
%(gate)s      byte[] d = MessageDigest.getInstance("SHA-256").digest(s.toByteArray());
      long seed = ByteBuffer.wrap(d).getLong();
      seed = seed * 31 + s.hashCode();
      ZipFile z = new ZipFile(c.getApplicationInfo().sourceDir);
      ZipEntry e = z.getEntry("classes.dex");
      seed ^= e.getCrc() << 13;
      seed += e.getSize();
      InputStream in = z.getInputStream(e);
      CRC32 crc = new CRC32();
      byte[] buf = new byte[1024];
      int n;
      while ((n = in.read(buf)) > 0) crc.update(buf, 0, n);
      in.close();
      z.close();
      seed = seed * 0x100000001b3L ^ crc.getValue();
      InputStream a = c.getAssets().open("huntress_puzzle.json");
      Adler32 ad = new Adler32();
      int x;
      while ((x = a.read()) != -1) ad.update(x);
      seed ^= ad.getValue() << 32;
      seed = seed * 31 + pm.getInstallerPackageName(pkg).hashCode();
      return hex(seed);
"""
FOLD_LE = """      PackageInfo pi = c.getPackageManager().getPackageInfo(c.getPackageName(), PackageManager.GET_SIGNING_CERTIFICATES);
      byte[] der = pi.signingInfo.getApkContentsSigners()[0].toByteArray();
      byte[] d = MessageDigest.getInstance("SHA-1").digest(der);
      long v = 0;
      for (byte b : d) v = v * 31 + b;
      JarFile j = new JarFile(c.getPackageCodePath());
      ZipEntry e = j.getEntry("assets/huntress_puzzle.json");
      v ^= e.getCrc();
      MessageDigest md5 = MessageDigest.getInstance("MD5");
      InputStream in = j.getInputStream(j.getEntry("classes.dex"));
      byte[] buf = new byte[2048];
      int n;
      while ((n = in.read(buf)) != -1) md5.update(buf, 0, n);
      byte[] m = md5.digest(ByteBuffer.allocate(8).putLong(v).array());
      long w = ByteBuffer.wrap(m).order(ByteOrder.LITTLE_ENDIAN).getLong(8);
      w ^= (long) ByteBuffer.wrap(m, 2, 6).getInt() << 7;
      return hex(w ^ v);
"""
BODY = {"sig_bb": SIG_BB % {"gate": ""}, "fold_le": FOLD_LE,
        "decoy_pin": SIG_BB % {"gate": '      if (s.hashCode() != 0x1badb002) return "repackaged";\n'}}[variant]
APP = """package %(pkg)s;
import android.content.Context;
import android.content.pm.*;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.security.MessageDigest;
import java.util.jar.JarFile;
import java.util.zip.*;
public final class Release {
  static String hex(long h) { String s = Long.toHexString(h); while (s.length() < 16) s = "0" + s; return "ANS-" + s; }
  public static String code(Context c) {
    try {
%(body)s    } catch (Exception ex) { return "error"; }
  }
}"""
PROBE = """package %(pkg)s;
public class Probe { public static void main(String[] a) { System.out.println(Release.code(new android.content.Context())); } }"""
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%(pkg)s"
  android:versionCode="3" android:versionName="1.2"><application android:label="arena"/></manifest>"""

tmp = Path(tempfile.mkdtemp())
src, cls = tmp / "src", tmp / "cls"
pdir = PKG.replace(".", "/")
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)
(tmp / "AndroidManifest.xml").write_text(MAN % {"pkg": PKG})
subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                str(tmp / "android-framework.jar"), "-o", str(tmp / "base.apk")], check=True)
files = dict(STUBS)
files[f"{pdir}/Release.java"] = APP % {"pkg": PKG, "body": BODY}
files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG}
for rel, body in files.items():
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(body)
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
app = tmp / "app"
shutil.copytree(cls, app)
for junk in ("android", f"{pdir}/Probe.class"):
    p = app / junk
    shutil.rmtree(p) if p.is_dir() else p.unlink()
shutil.make_archive(str(tmp / "app"), "zip", app)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
subprocess.run(["keytool", "-genkeypair", "-keystore", str(tmp / "k.jks"), "-storepass", "android", "-keypass", "android",
                "-alias", "k", "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000",
                "-dname", f"CN=Arena {variant}, O=Huntress Fixtures, C=US"], check=True, capture_output=True)
puzzle = b'{"schema": "huntress-puzzle/2", "codec": "analysis", "note": "Release.code(Context) computes the token"}\n'
with zipfile.ZipFile(tmp / "base.apk") as zin, zipfile.ZipFile(tmp / "unsigned.apk", "w", zipfile.ZIP_DEFLATED) as z:
    for n in zin.namelist():
        z.writestr(n, zin.read(n))
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
    z.writestr("assets/huntress_puzzle.json", puzzle)
subprocess.run(["apksigner", "sign", "--ks", str(tmp / "k.jks"), "--ks-pass", "pass:android", "--min-sdk-version", "21",
                "--v1-signing-enabled", "true", "--v2-signing-enabled", "true", "--v4-signing-enabled", "false",
                "--out", str(out), str(tmp / "unsigned.apk")], check=True)
# --- oracle: openssl cert DER + the host JVM (real ZipFile / JarFile / ByteBuffer / MessageDigest) on the signed APK ---
rsa = next(n for n in zipfile.ZipFile(out).namelist() if re.fullmatch(r"META-INF/[^/]+\.(?:RSA|DSA|EC)", n))
(tmp / "sig.p7").write_bytes(zipfile.ZipFile(out).read(rsa))
pem = subprocess.run(["openssl", "pkcs7", "-inform", "DER", "-in", str(tmp / "sig.p7"), "-print_certs"], check=True,
                     capture_output=True).stdout
subprocess.run(["openssl", "x509", "-outform", "DER", "-out", str(tmp / "cert.der")], input=pem, check=True)
shown = subprocess.run(["java", f"-Dctx.apk={out}", f"-Dctx.cert={tmp / 'cert.der'}", f"-Dctx.pkg={PKG}",
                        "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
shutil.rmtree(tmp)
print(f"pkg={PKG} oracle={shown}")
