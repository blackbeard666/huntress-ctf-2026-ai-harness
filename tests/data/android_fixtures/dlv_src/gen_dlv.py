#!/usr/bin/env python3
"""Generate the dlv_* fixtures (coverage atlas row 112: deeplink-input-validation-eval).
usage: gen_dlv.py <variant: endswith_host | parseuri_regex | decoy_nearmiss> <out.apk>
App classes + android.* framework stubs (android.net.Uri over java.net.URI: getHost as given, getPath decoded,
getQueryParameter first match %XX-decoded with "+" -> " " (API 16+), Uri.decode keeps "+"; Intent.parseUri for `intent:...#Intent;...;end`) are compiled
with javac --release 8; app classes only -> d2j-jar2dex. The manifest (exported LinkActivity, VIEW/BROWSABLE
intent-filter, <data scheme="huntress28" host="vault" path="/unlock"/>) is compiled by apktool's bundled aapt2 link.
 endswith_host:  onCreate: host = getData().getHost(); requires host.endsWith("huntress.local") (the manifest host
                 "vault" fails it) and getPath() == "/unlock"; Log.d the ENC[k] ^ host.charAt(k % len) token.
 parseuri_regex: onCreate: next = getData().getQueryParameter("next"); Intent.parseUri(next, URI_INTENT_SCHEME)
                 .getStringExtra("code") must matches("vault-77(31)") and getLastPathSegment() == "unlock"; Log.d the
                 ENC[k] ^ code.charAt(k % len) token.
 decoy_nearmiss: endswith_host whose token is a 15-hex near miss.
The oracle (Probe, not shipped) is a CALLER run on the host JVM: it delivers the deep link the validator accepts
(huntress28://huntress.local/unlock, or huntress28://vault/unlock?next=<urlencoded intent:#Intent;S.code=vault-7731;end>)
to LinkActivity.onCreate and prints what it logs."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"endswith_host": "ANS-5d0c8e3a71f94b26", "parseuri_regex": "ANS-e7a2193fc04d6b58",
          "decoy_nearmiss": "ANS-91c3f6e0a2b5d47"}
PKG = "com.huntress.mobile.d28.links"
STUBS = {
    "android/net/Uri.java": """package android.net;
public class Uri {
  final java.net.URI u;
  Uri(java.net.URI u) { this.u = u; }
  public static Uri parse(String s) { return new Uri(java.net.URI.create(s)); }
  public static String decode(String s) { try { return java.net.URLDecoder.decode(s.replace("+", "%2B"), "UTF-8"); }
    catch (Exception e) { return s; } }
  public String getScheme() { return u.getScheme(); }
  public String getHost() { return u.getHost(); }
  public String getPath() { return u.getPath(); }
  public String getLastPathSegment() { String p = u.getPath(); return p == null ? null : p.substring(p.lastIndexOf('/') + 1); }
  public String getQueryParameter(String k) { String q = u.getRawQuery(); if (q == null) return null;
    for (String kv : q.split("&")) { int e = kv.indexOf('='); String n = e < 0 ? kv : kv.substring(0, e);
      if (decode(n).equals(k)) try { return e < 0 ? "" : java.net.URLDecoder.decode(kv.substring(e + 1), "UTF-8"); }
      catch (Exception x) { return null; } } return null; }
  public String toString() { return u.toString(); }
}""",
    "android/content/Context.java": "package android.content;\npublic class Context { }",
    "android/content/Intent.java": """package android.content;
public class Intent {
  public static final int URI_INTENT_SCHEME = 1;
  String action; android.net.Uri data; public final java.util.HashMap<String, String> x = new java.util.HashMap<String, String>();
  public Intent() { }
  public Intent setData(android.net.Uri d) { data = d; return this; }
  public android.net.Uri getData() { return data; }
  public String getStringExtra(String k) { return x.get(k); }
  public static Intent parseUri(String s, int flags) throws java.net.URISyntaxException {
    Intent it = new Intent(); int i = s.lastIndexOf("#Intent;");
    if (i < 0) { it.data = android.net.Uri.parse(s); return it; }
    String scheme = null, d = s.substring(0, i);
    for (String part : s.substring(i + 8).split(";")) {
      if (part.equals("end")) break; int e = part.indexOf('='); if (e < 0) continue;
      String k = part.substring(0, e), v = android.net.Uri.decode(part.substring(e + 1));
      if (k.startsWith("S.")) it.x.put(k.substring(2), v); else if (k.equals("action")) it.action = v;
      else if (k.equals("scheme")) scheme = v; }
    if (d.startsWith("intent:")) d = d.substring(7);
    if (d.length() > 0) it.data = android.net.Uri.parse((scheme == null ? "" : scheme + ":") + d);
    return it; }
}""",
    "android/util/Log.java": """package android.util;
public final class Log { public static int d(String t, String m) { System.out.println(t + ": " + m); return 0; } }""",
    "android/app/Activity.java": """package android.app;
public class Activity extends android.content.Context {
  public android.content.Intent intent;
  public android.content.Intent getIntent() { return intent; }
  public void finish() { }
  protected void onCreate(android.os.Bundle b) { } }""",
    "android/os/Bundle.java": "package android.os;\npublic class Bundle { }",
}
HOST = """package %(pkg)s;
public class LinkActivity extends android.app.Activity {
  static final byte[] ENC = {%(enc)s};
  @Override protected void onCreate(android.os.Bundle b) {
    super.onCreate(b);
    android.net.Uri u = getIntent().getData();
    if (u == null) { finish(); return; }
    String host = u.getHost();
    if (host == null || !host.endsWith("huntress.local")) { android.util.Log.d("link", "rejected host"); finish(); return; }
    if (!"/unlock".equals(u.getPath())) { finish(); return; }
    StringBuilder sb = new StringBuilder();
    for (int k = 0; k < ENC.length; k++) sb.append((char) ((ENC[k] ^ host.charAt(k %% host.length())) & 0xFF));
    android.util.Log.d("vault", sb.toString());
  }
}"""
REGEX = """package %(pkg)s;
public class LinkActivity extends android.app.Activity {
  static final byte[] ENC = {%(enc)s};
  @Override protected void onCreate(android.os.Bundle b) {
    super.onCreate(b);
    android.net.Uri u = getIntent().getData();
    if (u == null || !"unlock".equals(u.getLastPathSegment())) { finish(); return; }
    String next = u.getQueryParameter("next");
    if (next == null) { finish(); return; }
    String code;
    try { code = android.content.Intent.parseUri(next, android.content.Intent.URI_INTENT_SCHEME).getStringExtra("code"); }
    catch (java.net.URISyntaxException e) { finish(); return; }
    if (code == null || !code.matches("vault-77(31)")) { android.util.Log.d("link", "rejected code"); finish(); return; }
    StringBuilder sb = new StringBuilder();
    for (int k = 0; k < ENC.length; k++) sb.append((char) ((ENC[k] ^ code.charAt(k %% code.length())) & 0xFF));
    android.util.Log.d("vault", sb.toString());
  }
}"""
PROBE = """package %(pkg)s;
public final class Probe { public static void main(String[] a) throws Exception {
  LinkActivity act = new LinkActivity();
  act.intent = new android.content.Intent().setData(android.net.Uri.parse(%(link)s));
  act.onCreate(null);
} }"""
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%(pkg)s">
  <application android:label="Links">
    <activity android:name=".LinkActivity" android:exported="true">
      <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <data android:scheme="huntress28" android:host="vault" android:path="/unlock"/>
      </intent-filter>
    </activity>
  </application>
</manifest>"""
pdir = PKG.replace(".", "/")
plain = TOKENS[variant].encode()
if variant == "parseuri_regex":
    key, body = b"vault-7731", REGEX
    link = ('"huntress28://vault/unlock?next=" + java.net.URLEncoder.encode('
            '"intent:#Intent;S.code=vault-7731;end", "UTF-8")')
else:
    key, body, link = b"huntress.local", HOST, '"huntress28://huntress.local/unlock"'
enc = [b ^ key[i % len(key)] for i, b in enumerate(plain)]
enc = [e - 256 if e > 127 else e for e in enc]
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
files = {f"{pdir}/LinkActivity.java": body, f"{pdir}/Probe.java": PROBE, **STUBS}
for rel, b in files.items():
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(b % {"pkg": PKG, "enc": ", ".join(map(str, enc)), "link": link} if "%(" in b else b)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shown = subprocess.run(["java", "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
for junk in ("android", f"{pdir}/Probe.class"):
    p = cls / junk
    shutil.rmtree(p) if p.is_dir() else p.unlink()
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2", "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "AndroidManifest.xml").write_text(MAN % {"pkg": PKG})
(tmp / "aapt2").chmod(0o755)
subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I", str(tmp / "android-framework.jar"),
                "-o", str(tmp / "base.apk")], check=True)
with zipfile.ZipFile(tmp / "base.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(f"host-JVM caller sees={shown!r}")
