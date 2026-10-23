#!/usr/bin/env python3
"""Generate the tamper_* fixtures (coverage atlas rows 49, 50: anti-tamper / repackaging probes whose RESULTS key the
answer -- installer package, signer cert bytes / Signature.hashCode, ApplicationInfo.flags FLAG_DEBUGGABLE, the CRC of
classes.dex read back through ZipFile(getPackageCodePath() / ApplicationInfo.sourceDir)).
usage: gen_tamper.py <variant: sig_crc | install_signing | decoy_gate> <out.apk>
App + android.* stubs compile with javac --release 8; app classes only -> d2j-jar2dex -> classes.dex; the manifest is
linked to binary AXML by apktool's bundled aapt2 (-I android-framework.jar); zip -> apksigner v1+v2 with a fresh
keytool RSA key. ORACLE (independent of lib.android): the signer cert DER is pulled from META-INF/*.RSA by
`openssl pkcs7 -print_certs | openssl x509 -outform DER`, the debuggable bit from `aapt dump badging`, and the host JVM
runs Guard.reveal() on stubs that hand those back (installer com.android.vending; getPackageCodePath / sourceDir = the
signed APK's host path, so the real java.util.zip.ZipFile reads the classes.dex CRC). The token is COMPUTED (sha-256 /
crc32 of the probe results), never stored. decoy_gate: the token is only built on a tampered device (installer not
Play, or debuggable) -- the clean path returns "verified"."""
import re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d22.tamper"
STUBS = {
    "android/content/pm/Signature.java": """package android.content.pm;
public class Signature { private final byte[] b; public Signature(byte[] b) { this.b = b; }
  public byte[] toByteArray() { return b.clone(); }
  public int hashCode() { return java.util.Arrays.hashCode(b); } }""",
    "android/content/pm/SigningInfo.java": """package android.content.pm;
public class SigningInfo { public Signature[] getApkContentsSigners() { return Stub.sigs(); } }""",
    "android/content/pm/Stub.java": """package android.content.pm;
public class Stub {
  public static Signature[] sigs() {
    try { return new Signature[] { new Signature(java.nio.file.Files.readAllBytes(java.nio.file.Paths.get(System.getProperty("tamper.cert")))) }; }
    catch (java.io.IOException e) { throw new RuntimeException(e); } } }""",
    "android/content/pm/InstallSourceInfo.java": """package android.content.pm;
public class InstallSourceInfo { public String getInstallingPackageName() { return "com.android.vending"; }
  public String getInitiatingPackageName() { return "com.android.vending"; } }""",
    "android/content/pm/PackageInfo.java": """package android.content.pm;
public class PackageInfo { public Signature[] signatures; public SigningInfo signingInfo; }""",
    "android/content/pm/ApplicationInfo.java": """package android.content.pm;
public class ApplicationInfo { public static final int FLAG_DEBUGGABLE = 2;
  public int flags = 0x38c8be44 | (Boolean.getBoolean("tamper.dbg") ? 2 : 0);
  public String sourceDir = System.getProperty("tamper.apk"); }""",
    "android/content/pm/PackageManager.java": """package android.content.pm;
public class PackageManager {
  public static final int GET_SIGNATURES = 64, GET_SIGNING_CERTIFICATES = 0x08000000;
  public static class NameNotFoundException extends Exception { public NameNotFoundException(String s) { super(s); } }
  public String getInstallerPackageName(String p) { return "com.android.vending"; }
  public InstallSourceInfo getInstallSourceInfo(String p) throws NameNotFoundException { return new InstallSourceInfo(); }
  public PackageInfo getPackageInfo(String p, int f) throws NameNotFoundException {
    PackageInfo i = new PackageInfo();
    if ((f & GET_SIGNATURES) != 0) i.signatures = Stub.sigs();
    if ((f & GET_SIGNING_CERTIFICATES) != 0) i.signingInfo = new SigningInfo();
    return i; } }""",
    "android/content/Context.java": """package android.content;
public class Context { public android.content.pm.PackageManager getPackageManager() { return new android.content.pm.PackageManager(); }
  public String getPackageName() { return "%(pkg)s"; }
  public String getPackageCodePath() { return System.getProperty("tamper.apk"); }
  public android.content.pm.ApplicationInfo getApplicationInfo() { return new android.content.pm.ApplicationInfo(); } }""",
    "android/app/Activity.java": "package android.app;\npublic class Activity extends android.content.Context { }",
}
HEX = """    StringBuilder sb = new StringBuilder("ANS-");
    for (int i = 0; i < 8; i++) sb.append(Integer.toHexString((h[i] & 0xff) | 0x100).substring(1));
    return sb.toString();"""
SIG_CRC = """    PackageManager pm = getPackageManager();
    String me = getPackageName();
    String inst = pm.getInstallerPackageName(me);
    PackageInfo pi = pm.getPackageInfo(me, PackageManager.GET_SIGNATURES);
    Signature s = pi.signatures[0];
    boolean dbg = (getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0;
    %(gate)s
    MessageDigest md = MessageDigest.getInstance("SHA-256");
    md.update(s.toByteArray());
    md.update(inst.getBytes());
    ZipFile zf = new ZipFile(getPackageCodePath());
    long crc = zf.getEntry("classes.dex").getCrc();
    zf.close();
    md.update(Long.toString(crc).getBytes());
    md.update(Integer.toString(s.hashCode()).getBytes());
    md.update((byte) (dbg ? 1 : 0));
    byte[] h = md.digest();
""" + HEX
INSTALL_SIGNING = """    PackageManager pm = getPackageManager();
    String me = getPackageName();
    InstallSourceInfo isi = pm.getInstallSourceInfo(me);
    Signature[] ss = pm.getPackageInfo(me, PackageManager.GET_SIGNING_CERTIFICATES).signingInfo.getApkContentsSigners();
    ApplicationInfo ai = getApplicationInfo();
    CRC32 c = new CRC32();
    c.update(ss[0].toByteArray());
    c.update(isi.getInstallingPackageName().getBytes());
    c.update(isi.getInitiatingPackageName().getBytes());
    ZipFile zf = new ZipFile(ai.sourceDir);
    long dc = zf.getEntry("classes.dex").getCrc();
    zf.close();
    long v = (c.getValue() << 32) ^ dc ^ ((long) (ai.flags & ApplicationInfo.FLAG_DEBUGGABLE) << 40) ^ ((long) ss[0].hashCode() << 8);
    byte[] h = new byte[8];
    for (int i = 0; i < 8; i++) h[i] = (byte) (v >>> (56 - 8 * i));
""" + HEX
BODY = {"sig_crc": SIG_CRC % {"gate": ""}, "install_signing": INSTALL_SIGNING,
        "decoy_gate": SIG_CRC % {"gate": 'if ("com.android.vending".equals(inst) && !dbg) return "verified";'}}
DEBUGGABLE = {"sig_crc": False, "install_signing": True, "decoy_gate": False}
GUARD = """package %(pkg)s;
import android.app.Activity;
import android.content.pm.*;
import java.security.MessageDigest;
import java.util.zip.CRC32;
import java.util.zip.ZipFile;
public class Guard extends Activity {
  public String reveal() {
    try {
%(body)s
    } catch (Exception e) { return "tampered"; }
  }
}"""
PROBE = """package %(pkg)s;
public class Probe { public static void main(String[] a) { System.out.println(new Guard().reveal()); } }"""
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%(pkg)s">
  <application android:label="tamper"%(dbg)s>
    <activity android:name=".Guard" android:exported="true"/>
  </application>
</manifest>"""

tmp = Path(tempfile.mkdtemp())
src, cls = tmp / "src", tmp / "cls"
pdir = PKG.replace(".", "/")
files = dict(STUBS)
files[f"{pdir}/Guard.java"] = GUARD % {"pkg": PKG, "body": BODY[variant]}
files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG}
for rel, body in files.items():
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(body.replace("%(pkg)s", PKG))
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
app = tmp / "app"
shutil.copytree(cls, app)
shutil.rmtree(app / "android")
(app / pdir / "Probe.class").unlink()
shutil.make_archive(str(tmp / "app"), "zip", app)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)
(tmp / "AndroidManifest.xml").write_text(MAN % {"pkg": PKG, "dbg": ' android:debuggable="true"' if DEBUGGABLE[variant] else ""})
subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                str(tmp / "android-framework.jar"), "-o", str(tmp / "base.apk")], check=True)
with zipfile.ZipFile(tmp / "base.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(tmp / "unsigned.apk", "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
subprocess.run(["keytool", "-genkeypair", "-keystore", str(tmp / "k.jks"), "-storepass", "android", "-keypass", "android",
                "-alias", "k", "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000",
                "-dname", f"CN=Tamper {variant}, O=Huntress Fixtures, C=US"], check=True, capture_output=True)
subprocess.run(["apksigner", "sign", "--ks", str(tmp / "k.jks"), "--ks-pass", "pass:android", "--v1-signing-enabled",
                "true", "--v2-signing-enabled", "true", "--out", str(out), str(tmp / "unsigned.apk")], check=True)
# --- oracle: openssl cert DER + aapt badging + the host JVM's real ZipFile on the signed APK ---
rsa = next(n for n in zipfile.ZipFile(out).namelist() if re.fullmatch(r"META-INF/[^/]+\.(?:RSA|DSA|EC)", n))
(tmp / "sig.p7").write_bytes(zipfile.ZipFile(out).read(rsa))
pem = subprocess.run(["openssl", "pkcs7", "-inform", "DER", "-in", str(tmp / "sig.p7"), "-print_certs"], check=True,
                     capture_output=True).stdout
subprocess.run(["openssl", "x509", "-outform", "DER", "-out", str(tmp / "cert.der")], input=pem, check=True)
badging = subprocess.run(["aapt", "dump", "badging", str(out)], capture_output=True, text=True).stdout
dbg = "application-debuggable" in badging
shown = subprocess.run(["java", f"-Dtamper.apk={out}", f"-Dtamper.cert={tmp / 'cert.der'}", f"-Dtamper.dbg={str(dbg).lower()}",
                        "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
shutil.rmtree(tmp)
print(f"debuggable={dbg} oracle={shown}")
