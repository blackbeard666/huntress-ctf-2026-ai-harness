#!/usr/bin/env python3
"""Generate the x5ctx_* fixtures (coverage atlas: analysis-keystore-cert-api-stubs, rows 87 / 93). A v2
`Release.code(Context)` whose answer is COMPUTED from a SHIPPED attestation cert read through the platform APIs:
getResources().openRawResource(R.raw.attest) / getAssets().open("attest_chain.pem") -> CertificateFactory.getInstance
("X.509").generateCertificate / generateCertificates -> X509Certificate.getExtensionValue("1.3.6.1.4.1.11129.2.1.17")
(signed bytes), getSerialNumber().longValue() (a 128-bit serial: truncation), getNotBefore/After().getTime(),
getSubject/IssuerX500Principal().getName() (escaped comma, emailAddress -> OID=#hex), getPublicKey().getEncoded(),
getEncoded(), getVersion(), getSigAlgName(), getBasicConstraints(), getSignature(); KeyStore("AndroidKeyStore")
.getCertificateChain(alias); new ByteArrayInputStream(cert.getEncoded()) round trip; MessageDigest over the root.
usage: gen_x5.py <raw_attest | asset_chain | decoy_noext> <out.apk>
Writer: pyasn1 KeyDescription (ka_src/gen_ka.key_description) + python `cryptography` x509 builder; aapt2 (apktool's)
compile/link for res/raw + R ids; javac --release 8 + dex2jar d2j-jar2dex; zipfile adds classes.dex / assets.
ORACLE (independent of lib.android): the host JVM runs Release.code() with the REAL JDK CertificateFactory /
X509Certificate / X500Principal over the bytes read back from the built APK by java.util.zip.ZipFile (res path from
`aapt2 dump resources`); AndroidKeyStore = a JDK KeyStoreSpi provider returning generateCertificates() of the APK
entry assets/<alias>.*."""
import datetime, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "ka_src"))
from gen_ka import key_description  # noqa: E402
from cryptography import x509  # noqa: E402
from cryptography.x509.oid import NameOID  # noqa: E402
from cryptography.hazmat.primitives import hashes, serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import ec, rsa  # noqa: E402

PKG = {"raw_attest": "com.huntress.arena.x5a", "asset_chain": "com.huntress.arena.x5b",
       "decoy_noext": "com.huntress.arena.x5c"}[variant]
OID = "1.3.6.1.4.1.11129.2.1.17"


def name(cn, org=None, email=None):
    at = [x509.NameAttribute(NameOID.COUNTRY_NAME, "US")]
    if org:
        at += [x509.NameAttribute(NameOID.ORGANIZATION_NAME, org), x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Arena+Lab")]
    at.append(x509.NameAttribute(NameOID.COMMON_NAME, cn))
    if email:
        at.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, email))
    return x509.Name(at)


def mk(subj, issuer, pub, key, serial, nb, na, ext=None, ca=None):
    b = (x509.CertificateBuilder().subject_name(subj).issuer_name(issuer).public_key(pub).serial_number(serial)
         .not_valid_before(nb).not_valid_after(na))
    if ca is not None:
        b = b.add_extension(x509.BasicConstraints(ca=True, path_length=ca), critical=True)
    if ext:
        b = b.add_extension(x509.UnrecognizedExtension(x509.ObjectIdentifier(OID), ext), critical=False)
    return b.sign(key, hashes.SHA256())


D = datetime.datetime
root_k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
inter_k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
leaf_k = ec.generate_private_key(ec.SECP256R1())
root_n, inter_n = name("Arena Attestation Root", "Huntress, Inc."), name("Arena StrongBox CA", "Huntress, Inc.")
root = mk(root_n, root_n, root_k.public_key(), root_k, 0x1f2e3d4c5b6a79880123456789abcdef, D(2025, 3, 1), D(2045, 3, 1), ca=None)
inter = mk(inter_n, root_n, inter_k.public_key(), root_k, 0x7a5b3c, D(2025, 6, 1, 12, 30, 15), D(2040, 6, 1), ca=1)
kd = None if variant == "decoy_noext" else key_description(b"arena-%s-nonce" % variant.encode(), pkg=PKG.encode())
leaf = mk(name("Android Keystore Key", email="keys@arena.example"), inter_n, leaf_k.public_key(), inter_k,
          0xF00DFACE00C0FFEE1234, D(2026, 10, 24, 8, 15, 42), D(2036, 10, 24), ext=kd)
der = lambda c: c.public_bytes(serialization.Encoding.DER)  # noqa: E731
pem = lambda c: c.public_bytes(serialization.Encoding.PEM)  # noqa: E731

STUBS = {
    "android/content/res/AssetManager.java": """package android.content.res;
public class AssetManager { public java.io.InputStream open(String n) throws java.io.IOException {
  java.util.zip.ZipFile z = new java.util.zip.ZipFile(System.getProperty("ctx.apk"));
  java.util.zip.ZipEntry e = z.getEntry("assets/" + n);
  if (e == null) throw new java.io.FileNotFoundException(n);
  return z.getInputStream(e); } }""",
    "android/content/res/Resources.java": """package android.content.res;
public class Resources { public java.io.InputStream openRawResource(int id) {
  try { java.util.zip.ZipFile z = new java.util.zip.ZipFile(System.getProperty("ctx.apk"));
    return z.getInputStream(z.getEntry(System.getProperty("ctx.res." + id))); }
  catch (Exception e) { throw new RuntimeException(e); } } }""",
    "android/content/Context.java": """package android.content;
public class Context {
  public android.content.res.AssetManager getAssets() { return new android.content.res.AssetManager(); }
  public android.content.res.Resources getResources() { return new android.content.res.Resources(); } }""",
}
MIX = """  static long mix(long h, long v) { h ^= v; h *= 0x100000001b3L; h ^= h >>> 29; return h; }
  static String hex(long h) { String s = Long.toHexString(h); while (s.length() < 16) s = "0" + s; return "ANS-" + s; }
"""
LEAF = """    byte[] ext = x.getExtensionValue("%s");
    if (ext == null) return "unattested";
    long h = 0xcbf29ce484222325L;
    h = mix(h, ext.length);
    for (int i = 0; i < ext.length; i++) h = mix(h, ext[i]);
    h = mix(h, x.getSerialNumber().longValue());
    h = mix(h, x.getNotBefore().getTime());
    h = mix(h, x.getNotAfter().getTime());
    h = mix(h, x.getSubjectX500Principal().getName().hashCode());
    h = mix(h, x.getIssuerX500Principal().getName().hashCode());
    byte[] pk = x.getPublicKey().getEncoded();
    for (int i = 0; i < pk.length; i++) h = mix(h, pk[i]);
    h = mix(h, x.getEncoded().length);
    h = mix(h, x.getVersion());
    h = mix(h, x.getSigAlgName().hashCode());
    h = mix(h, x.getBasicConstraints());
""" % OID
RELEASE = {
    "raw_attest": """  public static String code(Context c) {
    ctx = c;
    try {
      InputStream in = c.getResources().openRawResource(R.raw.attest);
      CertificateFactory cf = CertificateFactory.getInstance("X.509");
      X509Certificate x = (X509Certificate) cf.generateCertificate(in);
      in.close();
""" + LEAF + """      return hex(h);
    } catch (Exception e) { return "error"; }
  }
""",
    "asset_chain": """  public static String code(Context c) {
    ctx = c;
    try {
      InputStream in = c.getAssets().open("attest_chain.pem");
      CertificateFactory cf = CertificateFactory.getInstance("X.509");
      Collection<? extends Certificate> all = cf.generateCertificates(in);
      long g = all.size();
      for (Certificate ce : all) {
        X509Certificate y = (X509Certificate) ce;
        g = mix(g, y.getSerialNumber().longValue());
        g = mix(g, y.getIssuerX500Principal().getName().hashCode());
        g = mix(g, y.getNotAfter().getTime());
      }
      KeyStore ks = KeyStore.getInstance("AndroidKeyStore");
      ks.load(null);
      Certificate[] ch = ks.getCertificateChain("attest_chain");
      X509Certificate x = (X509Certificate) cf.generateCertificate(new ByteArrayInputStream(ch[0].getEncoded()));
""" + LEAF + """      h = mix(h, g);
      h = mix(h, ch.length);
      X509Certificate mid = (X509Certificate) ch[1];
      h = mix(h, mid.getSignature().length);
      h = mix(h, mid.getBasicConstraints());
      h = mix(h, mid.getNotBefore().getTime());
      MessageDigest md = MessageDigest.getInstance("SHA-256");
      md.update(ch[ch.length - 1].getEncoded());
      byte[] d = md.digest();
      h = mix(h, d[0]);
      h = mix(h, d[31]);
      return hex(h);
    } catch (Exception e) { return "error"; }
  }
""",
}
RELEASE["decoy_noext"] = RELEASE["raw_attest"]
APP = """package %(pkg)s;
import android.content.Context;
import java.io.*;
import java.security.*;
import java.security.cert.*;
import java.util.Collection;
import java.security.cert.Certificate;
public final class Release {
  static Context ctx;
""" + MIX + "%(body)s}"
PROBE = """package %(pkg)s;
import java.security.*;
import java.security.cert.Certificate;
public class Probe {
  public static class AKS extends KeyStoreSpi {
    public Certificate[] engineGetCertificateChain(String a) {
      try { java.util.zip.ZipFile z = new java.util.zip.ZipFile(System.getProperty("ctx.apk"));
        java.util.List<String> ns = new java.util.ArrayList<>();
        for (java.util.Enumeration<? extends java.util.zip.ZipEntry> e = z.entries(); e.hasMoreElements();) {
          String n = e.nextElement().getName();
          if ((n.startsWith("assets/") || n.startsWith("res/raw/")) && n.substring(n.lastIndexOf('/') + 1).split("\\\\.")[0].equals(a)) ns.add(n); }
        if (ns.isEmpty()) return null;
        java.util.Collections.sort(ns);
        return java.security.cert.CertificateFactory.getInstance("X.509")
          .generateCertificates(z.getInputStream(z.getEntry(ns.get(0)))).toArray(new Certificate[0]); }
      catch (Exception e) { throw new RuntimeException(e); } }
    public Certificate engineGetCertificate(String a) { Certificate[] c = engineGetCertificateChain(a); return c == null ? null : c[0]; }
    public Key engineGetKey(String a, char[] p) { return null; }
    public java.util.Date engineGetCreationDate(String a) { return null; }
    public void engineSetKeyEntry(String a, Key k, char[] p, Certificate[] c) { }
    public void engineSetKeyEntry(String a, byte[] k, Certificate[] c) { }
    public void engineSetCertificateEntry(String a, Certificate c) { }
    public void engineDeleteEntry(String a) { }
    public java.util.Enumeration<String> engineAliases() { return java.util.Collections.emptyEnumeration(); }
    public boolean engineContainsAlias(String a) { return engineGetCertificateChain(a) != null; }
    public int engineSize() { return 0; }
    public boolean engineIsKeyEntry(String a) { return false; }
    public boolean engineIsCertificateEntry(String a) { return false; }
    public String engineGetCertificateAlias(Certificate c) { return null; }
    public void engineStore(java.io.OutputStream o, char[] p) { }
    public void engineLoad(java.io.InputStream i, char[] p) { }
  }
  public static void main(String[] a) {
    Security.addProvider(new Provider("AKS", 1.0, "AndroidKeyStore oracle") {{ put("KeyStore.AndroidKeyStore", AKS.class.getName()); }});
    System.out.println(Release.code(new android.content.Context())); } }"""
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%s"
  android:versionCode="3" android:versionName="1.3"><application android:label="arena"/></manifest>"""

tmp = Path(tempfile.mkdtemp())
src, cls = tmp / "src", tmp / "cls"
pdir = PKG.replace(".", "/")
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)
(tmp / "res/raw").mkdir(parents=True)
(tmp / "res/raw/attest.der").write_bytes(der(leaf))
(tmp / "AndroidManifest.xml").write_text(MAN % PKG)
subprocess.run([str(tmp / "aapt2"), "compile", "--dir", str(tmp / "res"), "-o", str(tmp / "res.zip")], check=True)
(tmp / "gen").mkdir()
subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                str(tmp / "android-framework.jar"), "--java", str(tmp / "gen"), "-o", str(tmp / "base.apk"),
                str(tmp / "res.zip")], check=True)
files = dict(STUBS)
files[f"{pdir}/Release.java"] = APP % {"pkg": PKG, "body": RELEASE[variant]}
files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG}
for rel, body in files.items():
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(body)
(src / pdir / "R.java").write_text((tmp / "gen" / pdir / "R.java").read_text())
subprocess.run(["javac", "-nowarn", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
app = tmp / "app"
shutil.copytree(cls, app)
for junk in ("android", *(p.relative_to(app) for p in (app / pdir).glob("Probe*.class"))):
    p = app / junk
    shutil.rmtree(p) if p.is_dir() else p.unlink()
shutil.make_archive(str(tmp / "app"), "zip", app)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
assets = {}
if variant == "asset_chain":
    assets["attest_chain.pem"] = b"# provisioned attestation chain, leaf first\n" + pem(leaf) + pem(inter) + pem(root)
with zipfile.ZipFile(tmp / "base.apk") as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for n in zin.namelist():
        z.writestr(n, zin.read(n))
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
    for n, b in assets.items():
        z.writestr("assets/" + n, b)
# --- oracle: aapt2 dump resources (raw id -> path) + the host JVM's real CertificateFactory on the built APK ---
dump = subprocess.run([str(tmp / "aapt2"), "dump", "resources", str(out)], check=True, capture_output=True, text=True).stdout
props, cur = [], None
for line in dump.splitlines():
    s = line.strip()
    if s.startswith("resource 0x"):
        cur = int(s.split()[1], 16)
    elif s.startswith("() (file) ") and cur is not None:
        props.append(f"-Dctx.res.{cur}={s.split()[2]}")
shown = subprocess.run(["java", f"-Dctx.apk={out}", *props, "-cp", str(cls), f"{PKG}.Probe"], check=True,
                       capture_output=True, text=True).stdout.strip()
shutil.rmtree(tmp)
print(f"props={props} oracle={shown}")
