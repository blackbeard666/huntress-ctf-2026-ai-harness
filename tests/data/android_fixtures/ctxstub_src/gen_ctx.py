#!/usr/bin/env python3
"""Generate the ctxstub_* fixtures (coverage atlas: analysis-android-api-stubs). A D23-style `Release.code(Context)`
(static, stores ctx in a static) whose answer is COMPUTED from what the handed Context returns on a clean retail
install: assets (AssetManager.open + InputStream), org.json JSONObject fields of an asset, resources.arsc strings by
R id and by Resources.getIdentifier, getPackageName, PackageInfo signer cert / versionCode / versionName,
ApplicationInfo.flags debuggable bit, SharedPreferences (unset key -> default, put+apply -> read back), Build.TAGS /
TYPE / FINGERPRINT, Settings.Secure ANDROID_ID length, SystemClock delta.
usage: gen_ctx.py <variant: asset_json | static_ctx | decoy_gate> <out.apk>
Build: javac --release 8 (app + android.* / org.json stubs) -> d2j-jar2dex; resources + manifest by apktool's aapt2
(compile + link -I android-framework.jar --java R); zipfile adds assets + classes.dex; keytool RSA + apksigner v1+v2.
ORACLE (independent of lib.android): the host JVM runs Release.code() on stubs that answer from the SIGNED APK itself:
assets via java.util.zip.ZipFile, the signer DER from `openssl pkcs7 -print_certs | openssl x509 -outform DER` on
META-INF/*.RSA, version + debuggable from `aapt dump badging`, resource ids/values from `aapt2 dump resources`;
retail-Pixel constants for Build (release-keys / user). static_ctx's blob = token ^ sha256(certDER || key || versionName)
with the cert taken from `keytool -exportcert` BEFORE packaging; the JVM output must equal it."""
import hashlib, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = {"asset_json": "com.huntress.arena.ctx1", "static_ctx": "com.huntress.arena.ctx2",
       "decoy_gate": "com.huntress.arena.ctx3"}[variant]
TOKEN2 = "ANS-6d0c4be19a7f2358"
FP = "google/oriole/oriole:14/UQ1A.240205.004/11269751:user/release-keys"
STUBS = {
    "android/content/res/AssetManager.java": """package android.content.res;
public class AssetManager { public java.io.InputStream open(String n) throws java.io.IOException {
  java.util.zip.ZipFile z = new java.util.zip.ZipFile(System.getProperty("ctx.apk"));
  java.util.zip.ZipEntry e = z.getEntry("assets/" + n);
  if (e == null) throw new java.io.FileNotFoundException(n);
  return z.getInputStream(e); } }""",
    "android/content/res/Resources.java": """package android.content.res;
public class Resources { public String getString(int id) { return ResTab.val(id); }
  public int getIdentifier(String n, String t, String p) { return ResTab.id(t + "/" + n); } }""",
    "android/content/res/ResTab.java": """package android.content.res;
public class ResTab { public static String val(int id) { return null; } public static int id(String k) { return 0; } }""",
    "android/content/SharedPreferences.java": """package android.content;
public interface SharedPreferences { int getInt(String k, int d); String getString(String k, String d); Editor edit();
  interface Editor { Editor putInt(String k, int v); void apply(); } }""",
    "android/content/Prefs.java": """package android.content;
public class Prefs implements SharedPreferences { java.util.HashMap<String, Object> m = new java.util.HashMap<>();
  public int getInt(String k, int d) { return m.containsKey(k) ? (Integer) m.get(k) : d; }
  public String getString(String k, String d) { return m.containsKey(k) ? (String) m.get(k) : d; }
  public Editor edit() { final Prefs me = this; return new Editor() {
    public Editor putInt(String k, int v) { me.m.put(k, v); return this; } public void apply() { } }; } }""",
    "android/content/ContentResolver.java": "package android.content;\npublic class ContentResolver { }",
    "android/provider/Settings.java": """package android.provider;
public class Settings { public static class Secure { public static final String ANDROID_ID = "android_id";
  public static String getString(android.content.ContentResolver c, String k) { return "android_id".equals(k) ? "3f8a1c5e7b2d9046" : null; } } }""",
    "android/os/Build.java": """package android.os;
public class Build { static String s(String v) { return v; }
  public static final String TAGS = s("release-keys"), TYPE = s("user"), FINGERPRINT = s("%s"), MODEL = s("Pixel 6"); }""" % FP,
    "android/os/SystemClock.java": """package android.os;
public class SystemClock { static long t = 1000; public static long elapsedRealtime() { return t += 1; } }""",
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
public class PackageInfo { public Signature[] signatures; public SigningInfo signingInfo;
  public int versionCode = Integer.getInteger("ctx.vc"); public String versionName = System.getProperty("ctx.vn"); }""",
    "android/content/pm/ApplicationInfo.java": """package android.content.pm;
public class ApplicationInfo { public static final int FLAG_DEBUGGABLE = 2;
  public int flags = 0x38c8be44 | (Boolean.getBoolean("ctx.dbg") ? 2 : 0); }""",
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
public class Context { static Prefs prefs = new Prefs();
  public android.content.pm.PackageManager getPackageManager() { return new android.content.pm.PackageManager(); }
  public String getPackageName() { return System.getProperty("ctx.pkg"); }
  public android.content.res.AssetManager getAssets() { return new android.content.res.AssetManager(); }
  public android.content.res.Resources getResources() { return new android.content.res.Resources(); }
  public String getString(int id) { return getResources().getString(id); }
  public SharedPreferences getSharedPreferences(String n, int m) { return prefs; }
  public ContentResolver getContentResolver() { return new ContentResolver(); }
  public android.content.pm.ApplicationInfo getApplicationInfo() { return new android.content.pm.ApplicationInfo(); } }""",
    "org/json/JSONException.java": """package org.json;
public class JSONException extends Exception { public JSONException(String s) { super(s); } }""",
    "org/json/JSONObject.java": """package org.json;
public class JSONObject { java.util.HashMap<String, String> m = new java.util.HashMap<>();
  public JSONObject(String s) throws JSONException {
    java.util.regex.Matcher x = java.util.regex.Pattern.compile("\\"(\\\\w+)\\"\\\\s*:\\\\s*(?:\\"([^\\"]*)\\"|(-?\\\\d+))").matcher(s);
    while (x.find()) m.put(x.group(1), x.group(2) != null ? x.group(2) : x.group(3)); }
  public String getString(String k) throws JSONException { if (!m.containsKey(k)) throw new JSONException(k); return m.get(k); }
  public String optString(String k, String d) { return m.containsKey(k) ? m.get(k) : d; }
  public int getInt(String k) throws JSONException { return Integer.parseInt(getString(k)); }
  public long getLong(String k) throws JSONException { return Long.parseLong(getString(k)); } }""",
}
MIX = """  static long mix(long h, long v) { h ^= v; h *= 0x100000001b3L; h ^= h >>> 29; return h; }
  static String hex(long h) { String s = Long.toHexString(h); while (s.length() < 16) s = "0" + s; return "ANS-" + s; }
"""
CHAIN = """    InputStream in = c.getAssets().open("build.json");
    byte[] b = new byte[in.available()];
    int n = in.read(b);
    in.close();
    JSONObject j = new JSONObject(new String(b, 0, n, "UTF-8"));
    long h = 0xcbf29ce484222325L;
    h = mix(h, j.getLong("build"));
    h = mix(h, j.getInt("day"));
    h = mix(h, j.optString("channel", "none").hashCode());
    h = mix(h, j.optString("missing", "dflt").hashCode());
    String pkg = c.getPackageName();
    h = mix(h, pkg.hashCode());
    h = mix(h, c.getResources().getString(R.string.seed).hashCode());
    h = mix(h, c.getString(c.getResources().getIdentifier("salt", "string", pkg)).hashCode());
    PackageInfo pi = c.getPackageManager().getPackageInfo(pkg, PackageManager.GET_SIGNATURES);
    h = mix(h, pi.signatures[0].hashCode());
    h = mix(h, pi.versionCode);
    h = mix(h, pi.versionName.hashCode());
    h = mix(h, c.getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE);
    h = mix(h, Build.TAGS.hashCode());
    h = mix(h, Build.TYPE.hashCode());
    h = mix(h, Build.FINGERPRINT.hashCode());
    SharedPreferences sp = c.getSharedPreferences("arena", 0);
    h = mix(h, sp.getInt("seen", 41));
    sp.edit().putInt("boot", 5).apply();
    h = mix(h, sp.getInt("boot", 0));
    String aid = Settings.Secure.getString(c.getContentResolver(), Settings.Secure.ANDROID_ID);
    h = mix(h, aid == null ? 0 : aid.length());
    long t0 = SystemClock.elapsedRealtime();
    long t1 = SystemClock.elapsedRealtime();
    h = mix(h, t1 - t0 < 100 ? 1 : 0);
"""
RELEASE = {
    "asset_json": """  public static String code(Context c) {
    ctx = c;
    try {
""" + CHAIN + """      return hex(h);
    } catch (Exception e) { return "error"; }
  }
""",
    "decoy_gate": """  public static String code(Context c) {
    ctx = c;
    try {
      if (!Build.TAGS.contains("test-keys") && (c.getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) == 0)
        return "release";
""" + CHAIN + """      return hex(h);
    } catch (Exception e) { return "error"; }
  }
""",
    "static_ctx": """  public static String code(Context c) { ctx = c; return Keys.derive(); }
""",
}
KEYS = """package %(pkg)s;
import android.content.pm.*;
import android.content.res.Resources;
import java.io.InputStream;
import java.security.MessageDigest;
final class Keys {
  static String derive() {
    try {
      Resources r = Release.ctx.getResources();
      String pkg = Release.ctx.getPackageName();
      byte[] k = r.getString(r.getIdentifier("arena_key", "string", pkg)).getBytes("UTF-8");
      InputStream in = Release.ctx.getAssets().open("blob.bin");
      byte[] enc = new byte[64];
      int n = 0, x;
      while ((x = in.read()) != -1) enc[n++] = (byte) x;
      in.close();
      PackageInfo pi = Release.ctx.getPackageManager().getPackageInfo(pkg, PackageManager.GET_SIGNING_CERTIFICATES);
      MessageDigest md = MessageDigest.getInstance("SHA-256");
      md.update(pi.signingInfo.getApkContentsSigners()[0].toByteArray());
      md.update(k);
      md.update(pi.versionName.getBytes());
      byte[] h = md.digest();
      char[] o = new char[n];
      for (int i = 0; i < n; i++) o[i] = (char) ((enc[i] ^ h[i %% 32]) & 0xff);
      return new String(o);
    } catch (Exception e) { return "error"; }
  }
}"""
APP = """package %(pkg)s;
import android.content.*;
import android.content.pm.*;
import android.os.Build;
import android.os.SystemClock;
import android.provider.Settings;
import org.json.JSONObject;
import java.io.InputStream;
public final class Release {
  static Context ctx;
""" + MIX + "%(body)s}"
PROBE = """package %(pkg)s;
public class Probe { public static void main(String[] a) { System.out.println(Release.code(new android.content.Context())); } }"""
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%(pkg)s"
  android:versionCode="%(vc)d" android:versionName="%(vn)s">
  <application android:label="arena"%(dbg)s/>
</manifest>"""
STRINGS = """<resources>
  <string name="seed">%(seed)s</string>
  <string name="salt">pepper-%(vc)d</string>
  <string name="arena_key">k3y-%(pkg)s</string>
</resources>"""
VC, VN, DBG = {"asset_json": (7, "2.4.1", False), "static_ctx": (12, "3.0.0-rc2", True),
               "decoy_gate": (7, "2.4.1", False)}[variant]

tmp = Path(tempfile.mkdtemp())
src, cls = tmp / "src", tmp / "cls"
pdir = PKG.replace(".", "/")
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)
(tmp / "res/values").mkdir(parents=True)
(tmp / "res/values/strings.xml").write_text(STRINGS % {"seed": f"orbit-{variant}", "vc": VC, "pkg": PKG})
(tmp / "AndroidManifest.xml").write_text(MAN % {"pkg": PKG, "vc": VC, "vn": VN,
                                                "dbg": ' android:debuggable="true"' if DBG else ""})
subprocess.run([str(tmp / "aapt2"), "compile", "--dir", str(tmp / "res"), "-o", str(tmp / "res.zip")], check=True)
(tmp / "gen").mkdir()
subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                str(tmp / "android-framework.jar"), "--java", str(tmp / "gen"), "-o", str(tmp / "base.apk"),
                str(tmp / "res.zip")], check=True)
files = dict(STUBS)
files[f"{pdir}/Release.java"] = APP % {"pkg": PKG, "body": RELEASE[variant]}
files[f"{pdir}/Keys.java"] = KEYS % {"pkg": PKG}
files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG}
for rel, body in files.items():
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(body)
(src / pdir / "R.java").write_text((tmp / "gen" / pdir / "R.java").read_text())
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
app = tmp / "app"
shutil.copytree(cls, app)
for junk in ("android", "org", f"{pdir}/Probe.class"):
    p = app / junk
    shutil.rmtree(p) if p.is_dir() else p.unlink()
shutil.make_archive(str(tmp / "app"), "zip", app)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
subprocess.run(["keytool", "-genkeypair", "-keystore", str(tmp / "k.jks"), "-storepass", "android", "-keypass", "android",
                "-alias", "k", "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000",
                "-dname", f"CN=Arena {variant}, O=Huntress Fixtures, C=US"], check=True, capture_output=True)
subprocess.run(["keytool", "-exportcert", "-keystore", str(tmp / "k.jks"), "-storepass", "android", "-alias", "k",
                "-file", str(tmp / "pre.der")], check=True, capture_output=True)
assets = {"build.json": b'{"build": 240517, "day": 24, "channel": "release"}\n'}
if variant == "static_ctx":
    h = hashlib.sha256((tmp / "pre.der").read_bytes() + f"k3y-{PKG}".encode() + VN.encode()).digest()
    assets = {"blob.bin": bytes(c ^ h[i % 32] for i, c in enumerate(TOKEN2.encode()))}
with zipfile.ZipFile(tmp / "base.apk") as zin, zipfile.ZipFile(tmp / "unsigned.apk", "w", zipfile.ZIP_DEFLATED) as z:
    for n in zin.namelist():
        z.writestr(n, zin.read(n))
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
    for n, b in assets.items():
        z.writestr("assets/" + n, b)
subprocess.run(["apksigner", "sign", "--ks", str(tmp / "k.jks"), "--ks-pass", "pass:android", "--min-sdk-version", "21",
                "--v1-signing-enabled", "true", "--v2-signing-enabled", "true", "--out", str(out), str(tmp / "unsigned.apk")],
               check=True)
# --- oracle: openssl cert DER + aapt badging + aapt2 resource dump + the host JVM on the signed APK ---
rsa = next(n for n in zipfile.ZipFile(out).namelist() if re.fullmatch(r"META-INF/[^/]+\.(?:RSA|DSA|EC)", n))
(tmp / "sig.p7").write_bytes(zipfile.ZipFile(out).read(rsa))
pem = subprocess.run(["openssl", "pkcs7", "-inform", "DER", "-in", str(tmp / "sig.p7"), "-print_certs"], check=True,
                     capture_output=True).stdout
subprocess.run(["openssl", "x509", "-outform", "DER", "-out", str(tmp / "cert.der")], input=pem, check=True)
badging = subprocess.run(["aapt", "dump", "badging", str(out)], capture_output=True, text=True).stdout
m = re.search(r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']*)'", badging)
dump = subprocess.run([str(tmp / "aapt2"), "dump", "resources", str(out)], check=True, capture_output=True, text=True).stdout
ids, vals, cur = {}, {}, None
for line in dump.splitlines():
    r = re.match(r"\s*resource (0x[0-9a-f]{8}) (\w+/\w+)", line)
    if r:
        cur = int(r[1], 16)
        ids[r[2]] = cur
        continue
    v = re.match(r'\s*\(\) "(.*)"$', line)
    if v and cur is not None:
        vals[cur] = v[1]
jmap = "".join(f'    I.put("{k}", {i}); ' for k, i in ids.items()) + "".join(f'    V.put({i}, "{s}"); ' for i, s in vals.items())
(src / "android/content/res/ResTab.java").write_text("""package android.content.res;
public class ResTab { static java.util.HashMap<String, Integer> I = new java.util.HashMap<>();
  static java.util.HashMap<Integer, String> V = new java.util.HashMap<>();
  static {%s}
  public static String val(int id) { return V.get(id); }
  public static int id(String k) { return I.containsKey(k) ? I.get(k) : 0; } }""" % jmap)
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shown = subprocess.run(["java", f"-Dctx.apk={out}", f"-Dctx.cert={tmp / 'cert.der'}", f"-Dctx.pkg={m[1]}",
                        f"-Dctx.vc={m[2]}", f"-Dctx.vn={m[3]}", f"-Dctx.dbg={str('application-debuggable' in badging).lower()}",
                        "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
if variant == "static_ctx":
    assert shown == TOKEN2, shown
shutil.rmtree(tmp)
print(f"pkg={m[1]} vc={m[2]} vn={m[3]} res={ids} oracle={shown}")
