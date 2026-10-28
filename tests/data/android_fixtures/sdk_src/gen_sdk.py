#!/usr/bin/env python3
"""Generate the sdk_* fixtures (coverage atlas row 111: sdk-int-platform-gate).
usage: gen_sdk.py <variant: target30 | target31 | decoy31 | nosdk> <out.apk>
One app class, com.huntress.mobile.d29.platform.Gate.code(Context): reads ctx.getApplicationInfo().targetSdkVersion
and Build.VERSION.SDK_INT (sget: the real android.jar's SDK_INT is not a compile-time constant) against
Build.VERSION_CODES.S / TIRAMISU (javac inlines those as const), and picks the legacy (targetSdk < 31: implicit export
of an intent-filter component without android:exported) or the modern branch; each branch XORs its own ENC array with
a key built from the branch name + Build.VERSION.RELEASE + the API bucket. No ANS literal ships.
 target30: <uses-sdk minSdkVersion=24 targetSdkVersion=30>; legacy branch decodes TOKENS[target30].
 target31: same code, targetSdkVersion=31; modern branch decodes TOKENS[target31] (legacy branch -> TOKENS[target30]).
 nosdk:    no <uses-sdk> at all: Android's defaults (minSdk 1, targetSdk = minSdk) -> legacy branch; Gate.code also
           requires Build.VERSION.CODENAME == "REL" (a preview build would take the modern branch).
 decoy31:  targetSdkVersion=31, but only the legacy (not taken) branch holds a valid token; the modern one is a 15-hex
           near miss -> no ANS token on the pinned device.
App + android.* stubs compile with javac --release 8; app classes only -> dex2jar d2j-jar2dex. Manifest (with an
intent-filter activity lacking android:exported) -> apktool-bundled aapt2 link -I android-framework.jar.
The oracle is independent: `aapt dump badging` of the BUILT APK gives targetSdkVersion; Probe (host JVM, not shipped)
runs Gate.code with ApplicationInfo.targetSdkVersion = that value and SDK_INT = 34 / RELEASE = "14" (the pinned
emulator profile) and prints the result."""
import os, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
ROOT = Path(__file__).resolve().parents[4]
TOKENS = {"target30": "ANS-3b9e07c4d1a2f685", "target31": "ANS-c60d2e9b7f41a538", "near": "ANS-8a1f4c0e9d3b7e2"}
PKG = "com.huntress.mobile.d29.platform"
STUBS = {
    "android/os/Build.java": """package android.os;
public class Build {
  public static class VERSION {
    public static final int SDK_INT = Integer.getInteger("sdk", 34);
    public static final String RELEASE = System.getProperty("release", "14");
    public static final String CODENAME = System.getProperty("codename", "REL");
  }
  public static class VERSION_CODES {
    public static final int R = 30; public static final int S = 31; public static final int TIRAMISU = 33;
  }
}""",
    "android/content/pm/ApplicationInfo.java": """package android.content.pm;
public class ApplicationInfo { public int targetSdkVersion; public int minSdkVersion; public int flags; }""",
    "android/content/Context.java": """package android.content;
public class Context { public android.content.pm.ApplicationInfo ai = new android.content.pm.ApplicationInfo();
  public android.content.pm.ApplicationInfo getApplicationInfo() { return ai; } }""",
}
GATE = """package %(pkg)s;
import android.os.Build;
public final class Gate {
  static final byte[] LEGACY = {%(legacy)s};
  static final byte[] MODERN = {%(modern)s};
  static String mix(byte[] enc, String key) {
    StringBuilder sb = new StringBuilder();
    for (int k = 0; k < enc.length; k++) sb.append((char) ((enc[k] ^ key.charAt(k %% key.length())) & 0xFF));
    return sb.toString();
  }
  public static String code(android.content.Context ctx) {
    int target = ctx.getApplicationInfo().targetSdkVersion;
    boolean implicitExport = target < Build.VERSION_CODES.S && "REL".equals(Build.VERSION.CODENAME);
    String bucket = Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU ? "t+" : "pre-t";
    if (implicitExport) return mix(LEGACY, "legacy/" + Build.VERSION.RELEASE + "/" + bucket);
    return mix(MODERN, "modern/" + Build.VERSION.RELEASE + "/" + bucket + "/" + target);
  }
}"""
PROBE = """package %(pkg)s;
public final class Probe { public static void main(String[] a) {
  android.content.Context c = new android.content.Context();
  c.ai.targetSdkVersion = Integer.parseInt(a[0]);
  System.out.println(Gate.code(c));
} }"""
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%(pkg)s">
%(usesdk)s  <application android:label="Platform">
    <activity android:name=".LegacyActivity">
      <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
      </intent-filter>
    </activity>
  </application>
</manifest>"""
target = 30 if variant == "target30" else 1 if variant == "nosdk" else 31
usesdk = "" if variant == "nosdk" else f'  <uses-sdk android:minSdkVersion="24" android:targetSdkVersion="{target}"/>\n'
release, bucket = "14", "t+"  # pinned emulator: API 34, RELEASE "14"


def enc(tok, key):
    e = [b ^ key[i % len(key)] for i, b in enumerate(tok.encode())]
    return ", ".join(str(x - 256 if x > 127 else x) for x in e)


legacy = enc(TOKENS["target30"], f"legacy/{release}/{bucket}".encode())
modern = enc(TOKENS["near" if variant == "decoy31" else "target31"], f"modern/{release}/{bucket}/{target}".encode())
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
pdir = PKG.replace(".", "/")
for rel, b in {f"{pdir}/Gate.java": GATE, f"{pdir}/Probe.java": PROBE, **STUBS}.items():
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(b % {"pkg": PKG, "legacy": legacy, "modern": modern} if "%(" in b else b)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "AndroidManifest.xml").write_text(MAN % {"pkg": PKG, "usesdk": usesdk})
(tmp / "aapt2").chmod(0o755)
subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                str(tmp / "android-framework.jar"), "-o", str(tmp / "base.apk")], check=True)
probe_cp = str(tmp / "probe")
shutil.copytree(cls, probe_cp)
for junk in ("android", f"{pdir}/Probe.class"):
    p = cls / junk
    shutil.rmtree(p) if p.is_dir() else p.unlink()
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
with zipfile.ZipFile(tmp / "base.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
# oracle: targetSdk as aapt reads it from the built APK, then the host-JVM caller with the pinned SDK_INT / RELEASE
badging = subprocess.run(["aapt", "dump", "badging", str(out)], capture_output=True, text=True).stdout
m = re.search(r"targetSdkVersion:'(\d+)'", badging)
tsdk = m.group(1) if m else "1"  # aapt prints no targetSdkVersion line without <uses-sdk>: platform default 1
shown = subprocess.run(["java", "-Dsdk=34", "-Drelease=14", "-Dcodename=REL", "-cp", probe_cp, f"{PKG}.Probe", tsdk],
                       check=True, capture_output=True, text=True).stdout.strip()
shutil.rmtree(tmp)
print(f"aapt targetSdkVersion={tsdk} host-JVM Gate.code={shown!r}")
