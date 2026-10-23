#!/usr/bin/env python3
"""Generate the brc_* fixtures (coverage atlas: broadcast-receiver-action-map).
usage: gen_brc.py <variant: dynamic_extra | ordered_chain | decoy_nearmiss> <out.apk>
App classes + android.* framework stubs (Intent with a working extras map, BroadcastReceiver with result data,
SharedPreferences backed by a static map, Log) are compiled with javac --release 8; app classes only -> d2j-jar2dex.
The manifest is compiled to binary AXML by apktool's bundled aapt2 link (-I apktool's prebuilt android-framework.jar).
 dynamic_extra:  MainActivity.onCreate registerReceiver(new VaultReceiver(), new IntentFilter(ACTION_UNLOCK)); no
                 manifest receiver. onReceive: getStringExtra("pin") equals "open-sesame" and getIntExtra("level", 0)
                 == 3 -> setResultData(xor-decoded token), else "denied".
 ordered_chain:  manifest <receiver>s StageOne (priority 100) / StageTwo (priority 10) on one action. StageOne needs
                 extra who == "alpha" and setResultData("k=43"); StageTwo parses getResultData() for the xor key and
                 puts the decoded token into SharedPreferences "vault"/"token".
 decoy_nearmiss: dynamic_extra whose token is a 15-hex near miss.
The oracle (Probe, not shipped) is a SENDER run on the host JVM: it delivers the intent with the right extras to the
receivers in priority order, copying result data between them as the ordered-broadcast dispatcher does."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"dynamic_extra": "ANS-3c9e1a7f05b2d846", "ordered_chain": "ANS-a41f7c0e98d3b265", "decoy_nearmiss": "ANS-7e2b04c9d1f6a38"}
PKG = "com.huntress.mobile.d24.bcast"
STUBS = {
    "android/content/Context.java": """package android.content;
public class Context {
  public SharedPreferences getSharedPreferences(String n, int mode) { return new SharedPreferences(); }
  public Intent registerReceiver(BroadcastReceiver r, IntentFilter f) { return null; }
  public void sendBroadcast(Intent i) { }
}""",
    "android/content/Intent.java": """package android.content;
public class Intent {
  String action; public final java.util.HashMap<String, Object> x = new java.util.HashMap<String, Object>();
  public Intent(String a) { action = a; }
  public String getAction() { return action; }
  public Intent putExtra(String k, String v) { x.put(k, v); return this; }
  public Intent putExtra(String k, int v) { x.put(k, v); return this; }
  public String getStringExtra(String k) { return (String) x.get(k); }
  public int getIntExtra(String k, int d) { Object o = x.get(k); return o == null ? d : (Integer) o; }
}""",
    "android/content/IntentFilter.java": """package android.content;
public class IntentFilter { public final java.util.ArrayList<String> a = new java.util.ArrayList<String>();
  public IntentFilter(String s) { a.add(s); } public void addAction(String s) { a.add(s); } }""",
    "android/content/BroadcastReceiver.java": """package android.content;
public abstract class BroadcastReceiver {
  String data;
  public abstract void onReceive(Context c, Intent i);
  public final void setResultData(String d) { data = d; }
  public final String getResultData() { return data; }
}""",
    "android/content/SharedPreferences.java": """package android.content;
public class SharedPreferences {
  public static final java.util.HashMap<String, String> STORE = new java.util.HashMap<String, String>();
  public Editor edit() { return new Editor(); }
  public static class Editor { public Editor putString(String k, String v) { STORE.put(k, v); return this; }
    public void apply() { } }
}""",
    "android/util/Log.java": """package android.util;
public final class Log { public static int d(String t, String m) { System.err.println(t + ": " + m); return 0; } }""",
    "android/app/Activity.java": """package android.app;
public class Activity extends android.content.Context { protected void onCreate(android.os.Bundle b) { } }""",
    "android/os/Bundle.java": "package android.os;\npublic class Bundle { }",
}
DYN = """package %(pkg)s;
public class MainActivity extends android.app.Activity {
  static final String ACTION_UNLOCK = "com.huntress.mobile.d24.action.UNLOCK";
  @Override protected void onCreate(android.os.Bundle b) {
    super.onCreate(b);
    registerReceiver(new VaultReceiver(), new android.content.IntentFilter(ACTION_UNLOCK));
  }
}"""
VAULT = """package %(pkg)s;
public class VaultReceiver extends android.content.BroadcastReceiver {
  static final byte[] ENC = {%(enc)s};
  @Override public void onReceive(android.content.Context c, android.content.Intent i) {
    String pin = i.getStringExtra("pin");
    int level = i.getIntExtra("level", 0);
    if (pin == null || !pin.equals("open-sesame") || level != 3) { setResultData("denied"); return; }
    StringBuilder sb = new StringBuilder();
    for (int k = 0; k < ENC.length; k++) sb.append((char) ((ENC[k] ^ (level * 0x11 + k)) & 0xFF));
    setResultData(sb.toString());
  }
}"""
STAGE1 = """package %(pkg)s;
public class StageOne extends android.content.BroadcastReceiver {
  @Override public void onReceive(android.content.Context c, android.content.Intent i) {
    if (!"alpha".equals(i.getStringExtra("who"))) { setResultData("nobody"); return; }
    setResultData("k=" + 43);
  }
}"""
STAGE2 = """package %(pkg)s;
public class StageTwo extends android.content.BroadcastReceiver {
  static final byte[] ENC = {%(enc)s};
  @Override public void onReceive(android.content.Context c, android.content.Intent i) {
    String r = getResultData();
    if (r == null || !r.startsWith("k=")) return;
    int key = Integer.parseInt(r.substring(2));
    char[] o = new char[ENC.length];
    for (int k = 0; k < ENC.length; k++) o[k] = (char) ((ENC[k] ^ key) & 0xFF);
    c.getSharedPreferences("vault", 0).edit().putString("token", new String(o)).apply();
  }
}"""
PROBE_DYN = """package %(pkg)s;
public final class Probe { public static void main(String[] a) {
  VaultReceiver r = new VaultReceiver();
  r.onReceive(new android.content.Context(), new android.content.Intent(MainActivity.ACTION_UNLOCK).putExtra("pin", "open-sesame").putExtra("level", 3));
  System.out.println(r.getResultData());
} }"""
PROBE_CHAIN = """package %(pkg)s;
public final class Probe { public static void main(String[] a) {
  android.content.Intent it = new android.content.Intent("com.huntress.mobile.d24.action.CHAIN").putExtra("who", "alpha");
  android.content.Context c = new android.content.Context();
  StageOne s1 = new StageOne(); s1.onReceive(c, it);
  StageTwo s2 = new StageTwo(); s2.setResultData(s1.getResultData()); s2.onReceive(c, it);
  System.out.println(android.content.SharedPreferences.STORE.get("token"));
} }"""
MAN_DYN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%(pkg)s">
  <application android:label="Bcast"><activity android:name=".MainActivity" android:exported="true"/></application>
</manifest>"""
MAN_CHAIN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%(pkg)s">
  <permission android:name="com.huntress.mobile.d24.permission.VAULT" android:protectionLevel="signature"/>
  <application android:label="Bcast">
    <receiver android:name=".StageTwo" android:exported="true" android:permission="com.huntress.mobile.d24.permission.VAULT">
      <intent-filter android:priority="10"><action android:name="com.huntress.mobile.d24.action.CHAIN"/></intent-filter>
    </receiver>
    <receiver android:name=".StageOne" android:exported="true">
      <intent-filter android:priority="100"><action android:name="com.huntress.mobile.d24.action.CHAIN"/>
        <action android:name="com.huntress.mobile.d24.action.PING"/></intent-filter>
    </receiver>
  </application>
</manifest>"""
pdir = PKG.replace(".", "/")
plain = TOKENS[variant].encode()
if variant == "ordered_chain":
    enc = [b ^ 43 for b in plain]
    files = {f"{pdir}/StageOne.java": STAGE1, f"{pdir}/StageTwo.java": STAGE2, f"{pdir}/Probe.java": PROBE_CHAIN}
    man = MAN_CHAIN
else:
    enc = [(b ^ (3 * 0x11 + i)) & 0xFF for i, b in enumerate(plain)]
    files = {f"{pdir}/MainActivity.java": DYN, f"{pdir}/VaultReceiver.java": VAULT, f"{pdir}/Probe.java": PROBE_DYN}
    man = MAN_DYN
enc = [e - 256 if e > 127 else e for e in enc]
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
files.update(STUBS)
for rel, b in files.items():
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(b % {"pkg": PKG, "enc": ", ".join(map(str, enc))} if "%(" in b else b)
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
(tmp / "AndroidManifest.xml").write_text(man % {"pkg": PKG})
(tmp / "aapt2").chmod(0o755)
subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I", str(tmp / "android-framework.jar"),
                "-o", str(tmp / "base.apk")], check=True)
with zipfile.ZipFile(tmp / "base.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(f"host-JVM sender sees={shown!r}")
