#!/usr/bin/env python3
"""Generate the pmc_* fixtures (coverage atlas: v2-boolean-gate-manifest-facts). A D27-v2-style `Release.code(Context)`
whose answer passes the `(ZI)I` gate `exportedReachability(boolean z, int i) = z ? i+1 : -1` fed by REAL manifest facts:
getActivityInfo(new ComponentName(ctx, X.class), 0).exported / PackageInfo(GET_ACTIVITIES|GET_RECEIVERS|GET_SERVICES)
.activities[k].exported / .permission / .services[0] / .receivers[0], ApplicationInfo.targetSdkVersion / minSdkVersion,
then int-to-byte / int-to-short / int-to-char narrowing into a long mixer -> "ANS-" + 16 hex. The gate's false side
returns "LOCKED" (no token).
usage: gen_pmc.py <variant: getinfo | pkginfo | decoy_nonexported> <out.apk>
Build: javac --release 8 (app + android.* stubs) -> d2j-jar2dex; binary manifest by apktool's aapt2 link
(-I android-framework.jar); zipfile adds classes.dex; keytool RSA + apksigner v1+v2.
ORACLE (independent of lib.android): `aapt dump xmltree` of the SIGNED APK gives each component's name / exported attr /
intent-filter presence / permission and uses-sdk; exported = attr, else "has an intent-filter" (the platform default
below targetSdk 31). Those facts feed android.* stubs on the host JVM, which runs Release.code() and prints the answer."""
import re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = {"getinfo": "com.huntress.arena.pmc1", "pkginfo": "com.huntress.arena.pmc2",
       "decoy_nonexported": "com.huntress.arena.pmc3"}[variant]
STUBS = {
    "android/content/Context.java": """package android.content;
public class Context { public android.content.pm.PackageManager getPackageManager() { return new android.content.pm.PackageManager(); }
  public String getPackageName() { return System.getProperty("pm.pkg"); }
  public android.content.pm.ApplicationInfo getApplicationInfo() { return android.content.pm.PackageManager.app(); } }""",
    "android/content/ComponentName.java": """package android.content;
public class ComponentName { String p, c;
  public ComponentName(Context x, Class<?> k) { p = x.getPackageName(); c = k.getName(); }
  public ComponentName(String a, String b) { p = a; c = b; }
  public String getPackageName() { return p; } public String getClassName() { return c; } }""",
    "android/content/pm/PackageItemInfo.java": "package android.content.pm;\npublic class PackageItemInfo { public String name, packageName; }",
    "android/content/pm/ComponentInfo.java": """package android.content.pm;
public class ComponentInfo extends PackageItemInfo { public boolean exported, enabled = true; public String processName;
  public ApplicationInfo applicationInfo; }""",
    "android/content/pm/ActivityInfo.java": """package android.content.pm;
public class ActivityInfo extends ComponentInfo { public String permission, targetActivity; }""",
    "android/content/pm/ServiceInfo.java": """package android.content.pm;
public class ServiceInfo extends ComponentInfo { public String permission; }""",
    "android/content/pm/ApplicationInfo.java": """package android.content.pm;
public class ApplicationInfo { public int targetSdkVersion, minSdkVersion, flags; }""",
    "android/content/pm/PackageInfo.java": """package android.content.pm;
public class PackageInfo { public String packageName; public ActivityInfo[] activities, receivers; public ServiceInfo[] services; }""",
    # facts file lines: type|fqcn|exported(0/1)|permission-or-empty ; written by the oracle from `aapt dump xmltree`
    "android/content/pm/PackageManager.java": """package android.content.pm;
public class PackageManager { public static final int GET_ACTIVITIES = 1, GET_RECEIVERS = 2, GET_SERVICES = 4;
  public static class NameNotFoundException extends Exception { }
  static java.util.List<String[]> facts() { try { java.util.List<String[]> r = new java.util.ArrayList<>();
    for (String l : java.nio.file.Files.readAllLines(java.nio.file.Paths.get(System.getProperty("pm.facts"))))
      if (!l.isEmpty()) r.add(l.split("\\\\|", -1)); return r; } catch (java.io.IOException e) { throw new RuntimeException(e); } }
  public static ApplicationInfo app() { ApplicationInfo a = new ApplicationInfo();
    a.targetSdkVersion = Integer.getInteger("pm.tsdk"); a.minSdkVersion = Integer.getInteger("pm.msdk"); return a; }
  static <T extends ComponentInfo> T fill(T o, String[] f) { o.name = f[1]; o.packageName = System.getProperty("pm.pkg");
    o.exported = f[2].equals("1"); o.applicationInfo = app();
    if (o instanceof ActivityInfo) ((ActivityInfo) o).permission = f[3].isEmpty() ? null : f[3];
    if (o instanceof ServiceInfo) ((ServiceInfo) o).permission = f[3].isEmpty() ? null : f[3]; return o; }
  public ActivityInfo getActivityInfo(android.content.ComponentName cn, int fl) throws NameNotFoundException {
    for (String[] f : facts()) if (f[0].equals("activity") && f[1].equals(cn.getClassName())) return fill(new ActivityInfo(), f);
    throw new NameNotFoundException(); }
  public PackageInfo getPackageInfo(String p, int fl) throws NameNotFoundException {
    PackageInfo pi = new PackageInfo(); pi.packageName = p;
    java.util.List<ActivityInfo> a = new java.util.ArrayList<>(), r = new java.util.ArrayList<>();
    java.util.List<ServiceInfo> s = new java.util.ArrayList<>();
    for (String[] f : facts()) { if (f[0].equals("activity")) a.add(fill(new ActivityInfo(), f));
      if (f[0].equals("receiver")) r.add(fill(new ActivityInfo(), f)); if (f[0].equals("service")) s.add(fill(new ServiceInfo(), f)); }
    if ((fl & 1) != 0 && !a.isEmpty()) pi.activities = a.toArray(new ActivityInfo[0]);
    if ((fl & 2) != 0 && !r.isEmpty()) pi.receivers = r.toArray(new ActivityInfo[0]);
    if ((fl & 4) != 0 && !s.isEmpty()) pi.services = s.toArray(new ServiceInfo[0]); return pi; } }""",
}
HEX = """  static String hex(long v) { String h = "0123456789abcdef"; StringBuilder sb = new StringBuilder("ANS-");
    for (int k = 60; k >= 0; k -= 4) sb.append(h.charAt((int) (v >>> k) & 15)); return sb.toString(); }
  public static int exportedReachability(boolean z, int i) { return z ? i + 1 : -1; }
"""
GETINFO = """  public static String code(Context ctx) throws Exception {
    PackageManager pm = ctx.getPackageManager();
    ActivityInfo ai = pm.getActivityInfo(new ComponentName(ctx, %(target)s.class), 0);
    int g = exportedReachability(ai.exported, 0x29);
    if (g < 0) return "LOCKED";
    ApplicationInfo app = ctx.getApplicationInfo();
    byte b = (byte) (g * 0x37 + app.targetSdkVersion);
    short s = (short) (app.minSdkVersion * 0x1F3D + b * 0x301);
    char c = (char) (g ^ 0xBEEF ^ (ai.permission == null ? 0x55AA : ai.permission.length()));
    long v = 0x5D3A91C0E7F24B68L;
    v = v * 1000003L + b; v ^= ((long) s << 21); v = v * 31 + c; v ^= v >>> 29;
    return hex(v);
  }
"""
PKGINFO = """  public static String code(Context ctx) throws Exception {
    PackageManager pm = ctx.getPackageManager();
    PackageInfo pi = pm.getPackageInfo(ctx.getPackageName(),
        PackageManager.GET_ACTIVITIES | PackageManager.GET_RECEIVERS | PackageManager.GET_SERVICES);
    int g = -1, n = 0, p = 0;
    for (int k = 0; k < pi.activities.length; k++) {
      ActivityInfo x = pi.activities[k];
      if (x.name.endsWith(".ChallengeActivity")) g = exportedReachability(x.exported, k);
      if (x.exported) n++;
      if (x.permission != null) p += x.permission.length();
    }
    int sv = exportedReachability(pi.services[0].exported, 7);
    int rv = exportedReachability(pi.receivers[0].exported, 3);
    if (g < 0) return "LOCKED";
    int sdk = pi.activities[0].applicationInfo.targetSdkVersion;
    byte b = (byte) (g * 0x5B + n * 0x11 + sdk);
    short s = (short) (p * 0x2F1 - sv * 0x777);
    char c = (char) (rv * 0x3C3C + 0xF00D);
    long v = 0x1C9E4F7A30B58D26L;
    v = (v ^ b) * 0x100000001B3L; v += ((long) s << 17) ^ c; v ^= v >>> 31; v *= 0x9E3779B1L;
    return hex(v);
  }
"""
APP = "package %(pkg)s;\nimport android.content.*;\nimport android.content.pm.*;\npublic class Release {\n%(body)s}\n"
PROBE = "package %(pkg)s;\npublic class Probe { public static void main(String[] a) throws Exception {" \
        " System.out.println(Release.code(new android.content.Context())); } }"
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%(pkg)s"
  android:versionCode="3" android:versionName="1.0.%(v)s">
  <uses-sdk android:minSdkVersion="23" android:targetSdkVersion="30"/>
  <application android:label="arena">
    <activity android:name=".MainActivity" android:exported="true">
      <intent-filter><action android:name="android.intent.action.MAIN"/>
        <category android:name="android.intent.category.LAUNCHER"/></intent-filter>
    </activity>
    <activity android:name=".AdminActivity" android:exported="false" android:permission="com.huntress.arena.ADMIN"/>
    <activity android:name=".ChallengeActivity">
      <intent-filter><action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/><category android:name="android.intent.category.BROWSABLE"/>
        <data android:scheme="huntress27" android:host="dependency-surface" android:path="/unlock"/></intent-filter>
    </activity>
    <service android:name=".SyncService" android:exported="false"/>
    <receiver android:name=".BootReceiver" android:exported="true"/>
  </application>
</manifest>"""

tmp = Path(tempfile.mkdtemp())
src, cls = tmp / "src", tmp / "cls"
pdir = PKG.replace(".", "/")
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)
(tmp / "AndroidManifest.xml").write_text(MAN % {"pkg": PKG, "v": variant})
subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                str(tmp / "android-framework.jar"), "-o", str(tmp / "base.apk")], check=True)
body = HEX + (PKGINFO if variant == "pkginfo" else
              GETINFO % {"target": "AdminActivity" if variant == "decoy_nonexported" else "ChallengeActivity"})
files = dict(STUBS)
files[f"{pdir}/Release.java"] = APP % {"pkg": PKG, "body": body}
files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG}
for c in ("MainActivity", "AdminActivity", "ChallengeActivity", "SyncService", "BootReceiver"):
    files[f"{pdir}/{c}.java"] = f"package {PKG};\npublic class {c} {{ }}\n"
for rel, b in files.items():
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(b)
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
with zipfile.ZipFile(tmp / "base.apk") as zin, zipfile.ZipFile(tmp / "unsigned.apk", "w", zipfile.ZIP_DEFLATED) as z:
    for n in zin.namelist():
        z.writestr(n, zin.read(n))
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
subprocess.run(["apksigner", "sign", "--ks", str(tmp / "k.jks"), "--ks-pass", "pass:android", "--min-sdk-version", "23",
                "--v1-signing-enabled", "true", "--v2-signing-enabled", "true", "--out", str(out), str(tmp / "unsigned.apk")],
               check=True)

# --- oracle: aapt dump xmltree of the signed APK -> component facts -> host JVM runs Release.code() on the stubs ---
tree = subprocess.run(["aapt", "dump", "xmltree", str(out), "AndroidManifest.xml"], check=True, capture_output=True,
                      text=True).stdout
comps, sdk, cur = [], {}, None
for line in tree.splitlines():
    ind = len(line) - len(line.lstrip())
    m = re.match(r"\s*E: ([\w-]+)", line)
    if m:
        if cur is not None and ind <= cur["ind"]:
            cur = None
        if m[1] in ("activity", "service", "receiver"):
            cur = {"ind": ind, "type": m[1], "name": None, "exp": None, "perm": "", "filters": 0}
            comps.append(cur)
        elif m[1] == "intent-filter" and cur is not None:
            cur["filters"] += 1
        continue
    a = re.match(r"\s*A: android:(\w+)\(0x[0-9a-f]+\)=(?:\(type 0x[0-9a-f]+\)(0x[0-9a-f]+)|\"([^\"]*)\")", line)
    if not a:
        continue
    k, iv, sv = a[1], a[2], a[3]
    if k in ("minSdkVersion", "targetSdkVersion"):
        sdk[k] = int(iv, 16) if iv else int(sv)
    elif cur is not None and ind > cur["ind"] and k in ("name", "exported", "permission"):
        if k == "name" and cur["name"] is None:
            cur["name"] = sv
        elif k == "exported":
            cur["exp"] = int(iv, 16) != 0
        elif k == "permission":
            cur["perm"] = sv
facts = tmp / "facts.txt"
for c in comps:  # the platform's PackageParser expands a relative ".Name" against the package
    c["name"] = PKG + c["name"] if c["name"].startswith(".") else c["name"]
facts.write_text("".join(f"{c['type']}|{c['name']}|{int(c['exp'] if c['exp'] is not None else c['filters'] > 0)}|"
                         f"{c['perm']}\n" for c in comps))
assert sdk.get("targetSdkVersion") == 30 and len(comps) == 5, (sdk, comps)
shown = subprocess.run(["java", f"-Dpm.facts={facts}", f"-Dpm.pkg={PKG}", f"-Dpm.tsdk={sdk['targetSdkVersion']}",
                        f"-Dpm.msdk={sdk['minSdkVersion']}", "-cp", str(cls), f"{PKG}.Probe"], check=True,
                       capture_output=True, text=True).stdout.strip()
print(facts.read_text(), end="")
print("ORACLE", shown)
shutil.rmtree(tmp)
