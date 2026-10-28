#!/usr/bin/env python3
"""Generate the erx_* fixtures (coverage atlas rows 1, 8, 106: several generated dependency flaws, only the one reachable
from a manifest-EXPORTED component counts).
usage: gen_erx.py <variant: activity_handler | legacy_receiver | decoy_unexported> <out.apk>
Three bundled libs (net.alpha.yamlkit / org.beta.imgcodec / io.gamma.netcfg), one flaw (ANS- const + HCTF-DEP id) each.
javac --release 8 (android.* stubs on the classpath only) -> dex2jar d2j-jar2dex -> `apktool b` (text manifest compiled
by apktool's bundled aapt2 + framework). The oracle (oracle.sh) reads the binary manifest with `aapt dump xmltree` and RUNS
every exported component's entry methods on the JVM; the flaws they hit are printed."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d27.erx"
LIBS = {"net.alpha.yamlkit": ("Loader", "ANS-4c1e9a07b3d258f6", "HCTF-DEP-YAML-0031"),
        "org.beta.imgcodec": ("Decoder", "ANS-a83f0d5c9e1b6274", "HCTF-DEP-IMG-0112"),
        "io.gamma.netcfg": ("TrustAll", "ANS-27d9b4e6f0a15c83", "HCTF-DEP-TLS-0007")}
STUBS = {
    "android/os/Bundle": "package android.os; public class Bundle {}",
    "android/content/Intent": "package android.content; public class Intent {}",
    "android/content/Context": "package android.content; public class Context {}",
    "android/app/Activity": "package android.app; public class Activity extends android.content.Context {"
                            " protected void onCreate(android.os.Bundle b) {} protected void onNewIntent(android.content.Intent i) {} }",
    "android/app/Service": "package android.app; public abstract class Service extends android.content.Context {"
                           " public int onStartCommand(android.content.Intent i, int f, int id) { return 0; }"
                           " public abstract android.os.IBinder onBind(android.content.Intent i); }",
    "android/os/IBinder": "package android.os; public interface IBinder {}",
    "android/content/BroadcastReceiver": "package android.content; public abstract class BroadcastReceiver {"
                                         " public abstract void onReceive(Context c, Intent i); }",
    "android/os/Handler": "package android.os; public class Handler { public boolean post(Runnable r) { r.run(); return true; } }",
}
P = f"package {PKG};\n"
files = {f"{PKG}.Trace": P + "public final class Trace { public static final java.util.List<String> LOG = new java.util.ArrayList<>();"
                              " public static void hit(String v) { LOG.add(v); } }"}
for pkg, (cls, tok, fid) in LIBS.items():
    files[f"{pkg}.{cls}"] = f"""package {pkg};
public final class {cls} {{
  static String advisory() {{ return "{fid}"; }}
  static String flaw() {{ return "{tok}"; }}
  public static String process(String in) {{
    {PKG}.Trace.hit(flaw() + " " + advisory());
    return in == null ? "" : in.trim();
  }}
}}
"""
A, B, C = (f"{p}.{c[0]}" for p, c in LIBS.items())
files[f"{PKG}.MainActivity"] = P + """public class MainActivity extends android.app.Activity {
  public String shown;
  protected void onCreate(android.os.Bundle b) { shown = "welcome"; }
}"""
tsdk, manifest_extra = "33", ""
if variant == "activity_handler":
    # exported deep-link activity -> Handler.post(Runnable) -> alpha flaw; non-exported service -> beta; gamma dead
    files[f"{PKG}.LinkActivity"] = P + f"""public class LinkActivity extends android.app.Activity {{
  protected void onNewIntent(android.content.Intent i) {{
    new android.os.Handler().post(new Runnable() {{ public void run() {{ {A}.process(" deep "); }} }});
  }}
}}"""
    files[f"{PKG}.SyncService"] = P + f"""public class SyncService extends android.app.Service {{
  public int onStartCommand(android.content.Intent i, int f, int id) {{ {B}.process("sync"); return 2; }}
  public android.os.IBinder onBind(android.content.Intent i) {{ return null; }}
}}"""
    comps = """        <activity android:name=".LinkActivity" android:exported="true">
            <intent-filter><action android:name="android.intent.action.VIEW"/><category android:name="android.intent.category.DEFAULT"/><category android:name="android.intent.category.BROWSABLE"/><data android:scheme="erx27" android:host="open"/></intent-filter>
        </activity>
        <service android:name=".SyncService" android:exported="false"/>"""
else:
    # legacy (targetSdk 30) receiver with an intent-filter and no exported attr -> implicitly exported -> Thread -> beta;
    # non-exported activity -> alpha; exported service behind a signature permission -> gamma
    files[f"{PKG}.AdminActivity"] = P + f"""public class AdminActivity extends android.app.Activity {{
  protected void onCreate(android.os.Bundle b) {{ {A}.process("admin"); }}
}}"""
    files[f"{PKG}.Worker"] = P + f"""final class Worker implements Runnable {{ public void run() {{ {B}.process("push"); }} }}"""
    files[f"{PKG}.PushReceiver"] = P + """public class PushReceiver extends android.content.BroadcastReceiver {
  public void onReceive(android.content.Context c, android.content.Intent i) { Thread t = new Thread(new Worker()); t.start();
    try { t.join(); } catch (InterruptedException e) { } }
}"""
    files[f"{PKG}.PrivService"] = P + f"""public class PrivService extends android.app.Service {{
  public android.os.IBinder onBind(android.content.Intent i) {{ {C}.process("priv"); return null; }}
}}"""
    tsdk = "30" if variant == "legacy_receiver" else "33"
    rexp = "" if variant == "legacy_receiver" else ' android:exported="false"'
    manifest_extra = f'    <permission android:name="{PKG}.PRIV" android:protectionLevel="signature"/>\n'
    comps = f"""        <activity android:name=".AdminActivity" android:exported="false"/>
        <receiver android:name=".PushReceiver"{rexp}>
            <intent-filter><action android:name="{PKG}.PUSH"/></intent-filter>
        </receiver>
        <service android:name=".PrivService" android:exported="true" android:permission="{PKG}.PRIV"/>"""
manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{PKG}">
{manifest_extra}    <application android:allowBackup="false" android:label="erx">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter>
        </activity>
{comps}
    </application>
</manifest>
"""
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
for root, d in ((tmp / "stub", STUBS), (tmp / "src", {k.replace(".", "/"): v for k, v in files.items()})):
    for k, v in d.items():
        (root / f"{k}.java").parent.mkdir(parents=True, exist_ok=True)
        (root / f"{k}.java").write_text(v)
(tmp / "stubc").mkdir(); (tmp / "cls").mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(tmp / "stubc"), *map(str, (tmp / "stub").rglob("*.java"))], check=True)
subprocess.run(["javac", "--release", "8", "-cp", str(tmp / "stubc"), "-d", str(tmp / "cls"),
                *map(str, (tmp / "src").rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", tmp / "cls")
bd = tmp / "b"
bd.mkdir()
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(bd / "classes.dex"), str(tmp / "app.zip")],
               check=True)
(bd / "AndroidManifest.xml").write_text(manifest)
(bd / "apktool.yml").write_text(f"version: 3.0.3\napkFileName: erx.apk\nsdkInfo:\n  minSdkVersion: 23\n  targetSdkVersion: {tsdk}\n"
                                "versionInfo:\n  versionCode: 1\n  versionName: 1.0\nusesFramework:\n  ids:\n  - 1\n")
subprocess.run(["apktool", "b", "-f", "-o", str(out), str(bd)], check=True)
shutil.rmtree(tmp, ignore_errors=True)
print(out)
