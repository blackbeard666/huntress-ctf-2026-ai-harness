#!/usr/bin/env python3
"""Generate the dbgv2_* fixtures (coverage atlas target v2-debugger-gate-state-loop, rows 41/79/88/100): the D23 v2
mixer chain with the d21 anti-debug mechanic as CODE -- DebuggerGate.debuggerGate(Context, long) is an
`int state = S0; while (state != DONE) switch (state)` machine (iteration cap 64) whose transitions read
Debug.isDebuggerConnected(), Debug.waitingForDebugger(), ctx.getApplicationInfo().flags & FLAG_DEBUGGABLE,
/proc/self/status TracerPid (BufferedReader(FileReader)) and a SystemClock.elapsedRealtime() delta; every probe that
says 'debugged' jumps to the trap state, which still emits a full ANS token (the honeypot).
  gate      no manifest (zipfile-built APK)
  manifest  the APK carries an aapt2-linked AndroidManifest with android:debuggable="true" (the D21 shape): the
            intended flow is still the NON-debugged path, so the expected value is the clean one
  decoy     the gate chain, but the hex loop emits 15 nibbles (ANS-<15 hex>: a near-miss, no valid token anywhere)
usage: gen_dbgv2.py <variant> <out.apk> [--debugged]
Build: javac --release 8 (app + android.* stubs) -> dex2jar d2j-jar2dex -> zipfile (+ assets/huntress_puzzle.json, v2
codec analysis, no data). Oracle: the host JVM runs Release.code(new Context()) on CLEAN stubs (Debug false, flags 0,
real /proc/self/status, SystemClock = System.nanoTime) and prints 'oracle=<value>'; --debugged prints the trap value."""
import shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
debugged = "--debugged" in sys.argv
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d21.dbgv2" + variant
STUBS = {
    "android/os/Debug.java": """package android.os;
public class Debug { public static boolean isDebuggerConnected() { return %(dbg)s; }
  public static boolean waitingForDebugger() { return %(dbg)s; } }""",
    "android/os/SystemClock.java": """package android.os;
public class SystemClock { public static long elapsedRealtime() { return System.nanoTime() / 1000000L + %(skew)s; } }""",
    "android/content/pm/ApplicationInfo.java": """package android.content.pm;
public class ApplicationInfo { public static final int FLAG_DEBUGGABLE = 2; public int flags = %(flags)s; }""",
    "android/content/Context.java": """package android.content;
public class Context { public android.content.pm.ApplicationInfo getApplicationInfo() {
  return new android.content.pm.ApplicationInfo(); } }""",
}
MIX = """package %(pkg)s;
public final class Mix {
    static long f1(int j) { return Util.sealHook30(j); }
    static long f1(long j) {
        long j2 = (j ^ (-2307042702180851644L)) * 333607066048539835L;
        long j3 = (j2 << 3) | (j2 >>> 61);
        long j4 = (((j3 << 31) | (j3 >>> 33)) * (-886256348880561723L)) ^ (-2607315507995602435L);
        return (j4 << 44) | (j4 >>> 20);
    }
}"""
PROBE = """package %(pkg)s;
public final class Probe {
    static int s2(int i, int i2, int i3, int i4) {
        int i5 = 0;
        while (((((i5 ^ i3) * i) + i2) & 4095) != i4) { i5++; if (i5 >= 4096) return -1; }
        return i5;
    }
    static int s3(int i, int i2, int i3, int i4) {
        int i5 = (i %% 11) + 1; int i6 = 12 - i5; int i7 = 0;
        do {
            int i8 = (i7 ^ i3) & 4095;
            if (((((i8 >>> i6) | (i8 << i5)) + i2) & 4095) == i4) return i7;
            i7++;
        } while (i7 < 4096);
        return -1;
    }
}"""
UTIL = """package %(pkg)s;
public final class Util {
    static long finTrampoline2d(long j) {
        long j2 = (j ^ (j >>> 10)) * (-4565261069424997581L);
        return ((((((j2 << 23) | (j2 >>> 41)) + 799274663451203256L) ^ 3900367236340418941L) ^ (-2044953418663047449L)) ^ 1775288625161603791L) + 4847595846291780659L;
    }
    static long mixTrampoline79(long j) {
        long j2 = j ^ (j >>> 28);
        long j3 = ((((j2 ^ (j2 >>> 30)) ^ (-5342125323041540572L)) + 2183413890471151166L) ^ 5116065488051834350L) * (-1402156385267666889L);
        long j4 = (j3 << 41) | (j3 >>> 23);
        return (j4 << 10) | (j4 >>> 54);
    }
    static long scanSignal61(long j) {
        int a = Probe.s3(3572, 943, 1370, 293);
        int b = Probe.s3(1990, 2605, 1464, 1995);
        int c = Probe.s2(3849, 3120, 2439, 2906);
        long v = (((j ^ (((0 ^ (((long) a) * (-3409818179106685223L))) ^ (((long) b) * (-8371994457828002933L))) ^ (((long) c) * (-3055453405719099057L)))) * (-8474999941664858633L)) + (((long) (((a ^ b) ^ c) & 7)) * 579319999994391256L)) * (-1580869134723234487L) * 3504449675974248957L;
        return (v << 23) | (v >>> 41);
    }
    static long sealHook30(long j) {
        long j2 = (j ^ (-6346643076729912359L)) * (-301087911024711665L);
        return ((j2 << 55) | (j2 >>> 9)) * 2575955574811816977L;
    }
}"""
HOOK = """package %(pkg)s;
public final class HookScan {
    static long mixPatcheb(long j) {
        long j2 = (j ^ 5006709854372244345L) * 1958157885234814829L;
        long j3 = (j2 << 30) | (j2 >>> 34);
        return (j3 ^ (j3 >>> 20)) - 7619862862749198346L;
    }
}"""
GATE = """package %(pkg)s;
import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.os.Debug;
import android.os.SystemClock;
public final class DebuggerGate {
    static int tracerPid() {
        try {
            java.io.BufferedReader r = new java.io.BufferedReader(new java.io.FileReader("/proc/self/status"));
            String l;
            int t = 0;
            while ((l = r.readLine()) != null) if (l.startsWith("TracerPid:")) t = Integer.parseInt(l.substring(10).trim());
            r.close();
            return t;
        } catch (Exception e) {
            return 0;
        }
    }
    static long debuggerGate(Context ctx, long v) {
        int state = 0x21;
        int guard = 0;
        long t0 = 0L;
        while (state != 0x7E) {
            if (++guard > 64) return Util.sealHook30(v);
            switch (state) {
                case 0x21: t0 = SystemClock.elapsedRealtime(); v = Util.mixTrampoline79(v);
                    state = Debug.isDebuggerConnected() ? 0x66 : 0x34; break;
                case 0x34: v ^= 0x1F3D5B7997B5D3F1L; state = Debug.waitingForDebugger() ? 0x66 : 0x47; break;
                case 0x47: state = (ctx.getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0 ? 0x66 : 0x52;
                    break;
                case 0x52: v = Util.scanSignal61(v); state = tracerPid() != 0 ? 0x66 : 0x5D; break;
                case 0x5D: state = SystemClock.elapsedRealtime() - t0 > 2000L ? 0x66 : 0x6A; break;
                case 0x6A: v = HookScan.mixPatcheb(v); state = 0x7E; break;
                case 0x66: v = Util.sealHook30(v) ^ 0x0DEB0661L; state = 0x7E; break;
                default: state = 0x66; break;
            }
        }
        return v;
    }
}"""
RELEASE = """package %(pkg)s;
import android.content.Context;
public final class Release {
    public static String code(Context context) {
        long v = DebuggerGate.debuggerGate(context, -6466867484639169990L);
        v = Util.finTrampoline2d(Mix.f1(v)) ^ (-7148765225602638926L);
        StringBuilder sb = new StringBuilder();
        sb.append("ANS-");
        int i = %(top)s;
        do { sb.append("0123456789ABCDEF".charAt(((int) (v >>> i)) & 15)); i -= 4; } while (i >= 0);
        return sb.toString();
    }
}"""
ORACLE = """package %(pkg)s;
public final class Oracle {
    public static void main(String[] a) { System.out.println("oracle=" + Release.code(new android.content.Context())); }
}"""
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%s" android:versionCode="1"
  android:versionName="1.0"><application android:label="Debug Me If You Can" android:debuggable="true"/></manifest>"""

subs = {"pkg": PKG, "top": 56 if variant == "decoy" else 60, "dbg": "true" if debugged else "false",
        "flags": 2 if debugged else 0, "skew": "3000L" if debugged else "0L"}
tmp = Path(tempfile.mkdtemp())
try:
    src, pdir = tmp / "src", tmp / "src" / PKG.replace(".", "/")
    pdir.mkdir(parents=True)
    for rel, body in STUBS.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_text(body % subs)
    for n, t in (("Mix", MIX), ("Probe", PROBE), ("Util", UTIL), ("HookScan", HOOK), ("DebuggerGate", GATE),
                 ("Release", RELEASE), ("Oracle", ORACLE)):
        (pdir / f"{n}.java").write_text(t % subs)
    cls = tmp / "cls"
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    print(subprocess.run(["java", "-cp", str(cls), PKG + ".Oracle"], check=True, capture_output=True,
                         text=True).stdout.strip())
    if debugged:
        sys.exit(0)
    with zipfile.ZipFile(tmp / "app.zip", "w") as z:  # app classes only (Oracle + android.* stubs stay out of the dex)
        for f in (cls / PKG.replace(".", "/")).glob("*.class"):
            if f.name != "Oracle.class":
                z.write(f, f.relative_to(cls).as_posix())
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"),
                    str(tmp / "app.zip")], check=True, capture_output=True)
    base = {}
    if variant == "manifest":
        subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                        "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
        (tmp / "aapt2").chmod(0o755)
        (tmp / "AndroidManifest.xml").write_text(MAN % PKG)
        subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                        str(tmp / "android-framework.jar"), "-o", str(tmp / "base.apk")], check=True)
        with zipfile.ZipFile(tmp / "base.apk") as zin:
            base = {n: zin.read(n) for n in zin.namelist()}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in base.items():
            z.writestr(n, b)
        z.writestr("assets/huntress_puzzle.json", '{"schema":"huntress.mobile.puzzle.v2","day":21,"codec":"analysis",'
                   '"build":"dbg%s"}' % variant)
        z.write(tmp / "classes.dex", "classes.dex")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
