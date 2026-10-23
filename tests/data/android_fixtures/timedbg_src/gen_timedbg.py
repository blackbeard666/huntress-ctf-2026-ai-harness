#!/usr/bin/env python3
"""Generate the timedbg_* fixtures (coverage atlas rows 41, 50, 88: timing anti-debug + debug-flag probes whose RESULTS
key the answer, so only a clean-device evaluation with a fast monotonic clock recovers it).
usage: gen_timedbg.py <variant: clock_xor | settings_props | decoy_slow> <out.apk>
Java app + android.* / dalvik.* framework stubs are compiled with javac; the stubs model a clean retail Pixel
(SystemClock / Debug.threadCpuTimeNanos backed by the host JVM's real clocks, no debugger, VMDebug off, adb and
developer options 0, SystemProperties ro.debuggable=0 ro.secure=1 service.adb.root=0). Stage 1 runs Guard.key(ctx) on
the JVM to get the check-derived key, the token is xor'd with that key stream here, stage 2 recompiles Vault with the
bytes and the JVM prints Vault.reveal(ctx) (the oracle). App classes only -> d2j-jar2dex -> zipfile.
settings_props ships a DEBUG build (BuildConfig.DEBUG = Boolean.parseBoolean("true")) but the token is keyed for the
release path (stub BuildConfig.DEBUG false in both JVM stages). decoy_slow: bytes keyed for a DEBUGGED device (the
stage-1 SystemClock stub jumps 5 s per read, so the timing check fails), the clean path yields garbage."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"clock_xor": "ANS-7c3e19a05bd2f846", "settings_props": "ANS-e2a95d1704c8b63f", "decoy_slow": "ANS-91b4f07e3c6a2d58"}
PKG = "com.huntress.mobile.d21.timedbg"
STUBS = {
    "android/os/SystemClock.java": """package android.os;
public final class SystemClock {
  static long skew = 0;
  static long n() { skew += %(skew)sL; return System.nanoTime() + skew; }
  public static long elapsedRealtime() { return n() / 1000000L; }
  public static long uptimeMillis() { return n() / 1000000L; }
  public static long elapsedRealtimeNanos() { return n(); }
}""",
    "android/os/Debug.java": """package android.os;
public class Debug { public static boolean isDebuggerConnected() { return false; }
  public static long threadCpuTimeNanos() {
    return java.lang.management.ManagementFactory.getThreadMXBean().getCurrentThreadCpuTime(); } }""",
    "android/os/SystemProperties.java": """package android.os;
public class SystemProperties {
  public static String get(String k) { return get(k, ""); }
  public static String get(String k, String d) {
    return k.equals("ro.debuggable") ? "0" : k.equals("ro.secure") ? "1" : k.equals("service.adb.root") ? "0" : d; }
  public static int getInt(String k, int d) { String v = get(k); return v.isEmpty() ? d : Integer.parseInt(v); }
}""",
    "dalvik/system/VMDebug.java": """package dalvik.system;
public class VMDebug { public static boolean isDebuggingEnabled() { return false; } }""",
    "android/content/ContentResolver.java": "package android.content;\npublic class ContentResolver { }",
    "android/content/Context.java": """package android.content;
public class Context { public ContentResolver getContentResolver() { return new ContentResolver(); } }""",
    "android/provider/Settings.java": """package android.provider;
public final class Settings {
  public static final class Global {
    public static final String ADB_ENABLED = "adb_enabled";
    public static final String DEVELOPMENT_SETTINGS_ENABLED = "development_settings_enabled";
    public static int getInt(android.content.ContentResolver r, String n, int d) { return 0; } }
  public static final class Secure {
    public static int getInt(android.content.ContentResolver r, String n, int d) { return 0; } }
}""",
}
GUARD = {
    "clock_xor": """package %(pkg)s;
import android.content.Context;
import android.os.Debug;
import android.os.SystemClock;
import dalvik.system.VMDebug;
public final class Guard {
  static int work(int n) { int s = 7; for (int i = 0; i < n; i++) s = s * 31 + i; return s; }
  static boolean fast() {
    long a = SystemClock.elapsedRealtime(), b = SystemClock.uptimeMillis(), c = SystemClock.elapsedRealtimeNanos();
    long d = System.nanoTime(), e = System.currentTimeMillis(), f = Debug.threadCpuTimeNanos();
    int w = work(64);
    try { Thread.sleep(1); } catch (InterruptedException x) { return false; }
    long a2 = SystemClock.elapsedRealtime(), b2 = SystemClock.uptimeMillis(), c2 = SystemClock.elapsedRealtimeNanos();
    long d2 = System.nanoTime(), e2 = System.currentTimeMillis(), f2 = Debug.threadCpuTimeNanos();
    return w != 0 && a2 - a < 500 && b2 - b < 500 && c2 - c < 500000000L && d2 - d < 500000000L && e2 - e < 500
        && f2 - f < 500000000L;
  }
  public static int key(Context ctx) {
    int k = 0x6B1D;
    k = k * 31 + (fast() ? 0x11 : 0x2F);
    k = k * 31 + (Debug.isDebuggerConnected() || VMDebug.isDebuggingEnabled() ? 3 : 5);
    return k;
  }
}""",
    "settings_props": """package %(pkg)s;
import android.content.Context;
import android.os.SystemProperties;
import android.provider.Settings;
public final class Guard {
  static String prop(String k) {
    try {
      Class<?> c = Class.forName("android.os.SystemProperties");
      java.lang.reflect.Method m = c.getMethod("get", String.class);
      return (String) m.invoke(null, k);
    } catch (Exception e) { return "?"; }
  }
  public static int key(Context ctx) {
    int k = 0x1F3;
    k = k * 31 + Settings.Global.getInt(ctx.getContentResolver(), Settings.Global.ADB_ENABLED, 7);
    k = k * 31 + Settings.Secure.getInt(ctx.getContentResolver(), Settings.Global.DEVELOPMENT_SETTINGS_ENABLED, 7);
    k = k * 31 + (SystemProperties.get("ro.debuggable").equals("1") ? 3 : 5);
    k = k * 31 + prop("ro.secure").hashCode();
    k = k * 31 + SystemProperties.getInt("service.adb.root", 9);
    if (BuildConfig.DEBUG) k ^= 0x5A5A;
    return k;
  }
}""",
}
GUARD["decoy_slow"] = GUARD["clock_xor"]
BUILDCONFIG = """package %(pkg)s;
public final class BuildConfig { public static final boolean DEBUG = Boolean.parseBoolean("%(dbg)s"); }"""
VAULT = """package %(pkg)s;
public final class Vault {
  static final byte[] ENC = {%(enc)s};
  public static String reveal(android.content.Context ctx) {
    int k = Guard.key(ctx);
    char[] c = new char[ENC.length];
    for (int i = 0; i < c.length; i++) c[i] = (char) ((ENC[i] ^ (k >>> ((i %% 4) * 8)) ^ (i * 5)) & 0xFF);
    return new String(c);
  }
}"""
PROBE = """package %(pkg)s;
public final class Probe { public static void main(String[] a) {
  System.out.println(%(body)s); } }"""
pdir = PKG.replace(".", "/")


def build(skew, dbg, enc, body):
    tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
    src, cls = tmp / "src", tmp / "cls"
    files = {k: v % {"skew": skew} if "%(" in v else v for k, v in STUBS.items()}
    files[f"{pdir}/Guard.java"] = GUARD[variant] % {"pkg": PKG}
    files[f"{pdir}/BuildConfig.java"] = BUILDCONFIG % {"pkg": PKG, "dbg": dbg}
    files[f"{pdir}/Vault.java"] = VAULT % {"pkg": PKG, "enc": ", ".join(map(str, enc))}
    files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG, "body": body}
    for rel, b in files.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_text(b)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True,
                   capture_output=True)
    run = subprocess.run(["java", "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
    return tmp, cls, run


ctx = "new android.content.Context()"
tmp, _, k = build(5_000_000_000 if variant == "decoy_slow" else 0, "false", [], f"Guard.key({ctx})")
shutil.rmtree(tmp)
k = int(k)
enc = [((p ^ (k >> ((i % 4) * 8)) ^ (i * 5)) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(TOKENS[variant].encode())]
# oracle: the JVM on the CLEAN release stubs (real fast clocks, DEBUG false) prints what a clean device shows
tmp, cls, shown = build(0, "false", enc, f"Vault.reveal({ctx})")
if variant == "settings_props":  # ship the DEBUG build's BuildConfig (parseBoolean("true")): the release path is the answer
    tmp2, cls2, _ = build(0, "true", enc, "0")
    shutil.copy(cls2 / pdir / "BuildConfig.class", cls / pdir / "BuildConfig.class")
    shutil.rmtree(tmp2)
for junk in ("android", "dalvik", f"{pdir}/Probe.class"):
    p = cls / junk
    shutil.rmtree(p) if p.is_dir() else p.unlink()
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(f"key={k} clean-JVM reveal()={shown!r}")
