#!/usr/bin/env python3
"""Generate the ads_* fixtures (anti-debug STATE MACHINES whose clean terminal state emits the answer; coverage atlas
rows 41, 79, 89). usage: gen_ads.py <variant: int_switch | string_state | decoy_trap> <out.apk> [--debugged]
A Java state machine (int field / String state, reassigned inside a loop, transitions on Debug.isDebuggerConnected,
ApplicationInfo.flags & FLAG_DEBUGGABLE, /proc/self/status TracerPid, System.nanoTime deltas, Settings.Secure
adb_enabled) folds every transition into a key; the terminal state xors ENC with it. The token's ENC bytes are computed
by stage 1 (the host JVM runs the machine on CLEAN android.* stubs and prints the key), stage 2 recompiles with ENC and
the JVM prints the terminal output (the oracle). --debugged prints what the same machine shows on DEBUGGED stubs (the
trap value a scanner must demote). App classes only -> dex2jar d2j-jar2dex -> zipfile."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
debugged = "--debugged" in sys.argv
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"int_switch": "ANS-7c21e9a05fd384b6", "string_state": "ANS-a3f0d81b6c5e2947",
          "decoy_trap": "ANS-5e8d1b0c4a7f93"}  # decoy: clean path emits a 14-hex near-miss
TRAP = "ANS-d3adb33fc0ffee11"
PKG = "com.huntress.mobile.d21.adsm"
STUBS = {
    "android/os/Debug.java": """package android.os;
public class Debug { public static boolean isDebuggerConnected() { return %(dbg)s; }
  public static boolean waitingForDebugger() { return %(dbg)s; } }""",
    "android/os/Bundle.java": "package android.os;\npublic class Bundle { }",
    "android/util/Log.java": """package android.util;
public class Log { public static int i(String t, String m) { System.out.println(m); return 0; } }""",
    "android/content/ContentResolver.java": "package android.content;\npublic class ContentResolver { }",
    "android/provider/Settings.java": """package android.provider;
public class Settings { public static class Secure {
  public static int getInt(android.content.ContentResolver c, String k, int d) { return %(adb)s; } } }""",
    "android/content/pm/ApplicationInfo.java": """package android.content.pm;
public class ApplicationInfo { public static final int FLAG_DEBUGGABLE = 2; public int flags = %(flags)s; }""",
    "android/content/Context.java": """package android.content;
public class Context { public android.content.pm.ApplicationInfo getApplicationInfo() { return new android.content.pm.ApplicationInfo(); }
  public ContentResolver getContentResolver() { return new ContentResolver(); } }""",
    "android/app/Activity.java": """package android.app;
public class Activity extends android.content.Context { protected void onCreate(android.os.Bundle b) { } }""",
}
TRACER = """
  static int tracer() {
    try {
      java.io.BufferedReader r = new java.io.BufferedReader(new java.io.FileReader("/proc/self/status"));
      String l; int v = 0;
      while ((l = r.readLine()) != null) if (l.startsWith("TracerPid:")) v = Integer.parseInt(l.substring(10).trim());
      r.close();
      return v;
    } catch (Exception e) { return 0; }
  }"""
GATE = {
    "int_switch": """package %(pkg)s;
import android.app.Activity;
import android.os.Debug;
public class Gate extends Activity {
  static final byte[] ENC = {%(enc)s};
  static final byte[] TRAP = {%(trap)s};
  int state;
  long key;
  public Gate() { state = 0x11; key = 0x5DEECE66DL; }
""" + TRACER + """
  public String debuggerGate() {
    StringBuilder sb = new StringBuilder();
    long t0 = 0;
    while (true) {
      switch (state) {
        case 0x11: key = key * 31 + 7; state = Debug.isDebuggerConnected() ? 0x66 : 0x22; break;
        case 0x22: key ^= 0x1F2E3D4CL; state = (getApplicationInfo().flags & 2) != 0 ? 0x66 : 0x33; break;
        case 0x33: key = key * 17 + tracer(); state = tracer() != 0 ? 0x66 : 0x44; t0 = System.nanoTime(); break;
        case 0x44: key += 0x2545F491L; state = System.nanoTime() - t0 > 2000000000L ? 0x66 : 0x55; break;
        case 0x55:
          for (int i = 0; i < ENC.length; i++) sb.append((char) ((ENC[i] ^ (key >>> ((i %% 8) * 8))) & 0xFF));
          return "proof=" + sb;
        case 0x66:
          for (int i = 0; i < TRAP.length; i++) sb.append((char) ((TRAP[i] ^ 0x5A) & 0xFF));
          return "proof=" + sb;
        default: return null;
      }
    }
  }
  public long probeKey() {
    while (true) {
      switch (state) {
        case 0x11: key = key * 31 + 7; state = Debug.isDebuggerConnected() ? 0x66 : 0x22; break;
        case 0x22: key ^= 0x1F2E3D4CL; state = (getApplicationInfo().flags & 2) != 0 ? 0x66 : 0x33; break;
        case 0x33: key = key * 17 + tracer(); state = tracer() != 0 ? 0x66 : 0x44; break;
        case 0x44: key += 0x2545F491L; state = 0x55; break;
        default: return key;
      }
    }
  }
}""",
    "string_state": """package %(pkg)s;
import android.app.Activity;
import android.os.Bundle;
import android.os.Debug;
import android.provider.Settings;
import android.util.Log;
public class Gate extends Activity {
  static final byte[] ENC = {%(enc)s};
  static final byte[] TRAP = {%(trap)s};
  static String state;
  static int key;
  static { state = "BOOT"; key = 0x1337; }
  @Override protected void onCreate(Bundle b) {
    super.onCreate(b);
    key = key * 7 + 3;
    walk();
  }
""" + TRACER + """
  void walk() {
    String outv = null;
    while (!state.equals("DONE")) {
      if (state.equals("BOOT")) { key = key * 31 + 0x41; state = Debug.waitingForDebugger() ? "HONEY" : "ADB"; }
      else if (state.equals("ADB")) {
        int adb = Settings.Secure.getInt(getContentResolver(), "adb_enabled", 0);
        key ^= 0x5A5A00 + adb; state = adb != 0 ? "HONEY" : "TRACE";
      }
      else if (state.equals("TRACE")) { int tp = tracer(); key = key * 13 + tp; state = tp != 0 ? "HONEY" : "EMIT"; }
      else if (state.equals("EMIT")) {
        char[] c = new char[ENC.length];
        for (int i = 0; i < c.length; i++) c[i] = (char) ((ENC[i] ^ (key >>> ((i %% 4) * 8)) ^ i) & 0xFF);
        outv = new String(c); state = "DONE";
      }
      else if (state.equals("HONEY")) {
        char[] c = new char[TRAP.length];
        for (int i = 0; i < c.length; i++) c[i] = (char) ((TRAP[i] ^ 0x5A) & 0xFF);
        outv = new String(c); state = "DONE";
      }
      else state = "DONE";
    }
    Log.i("gate", "proof=" + outv);
  }
  public int probeKey() { onCreate(null); return key; }
}""",
}
GATE["decoy_trap"] = GATE["int_switch"]
PROBE = """package %(pkg)s;
public final class Probe { public static void main(String[] a) { %(body)s } }"""
pdir = PKG.replace(".", "/")


def build(enc, trap, body, dbg):
    tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
    src, cls = tmp / "src", tmp / "cls"
    sub = {"dbg": "true" if dbg else "false", "adb": "1" if dbg else "0", "flags": "0x38c8be46" if dbg else "0x38c8be44"}
    files = {k: v % sub if "%(" in v else v for k, v in STUBS.items()}
    files[f"{pdir}/Gate.java"] = GATE[variant] % {"pkg": PKG, "enc": ", ".join(map(str, enc)),
                                                 "trap": ", ".join(map(str, trap))}
    files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG, "body": body}
    for rel, b in files.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_text(b)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    run = subprocess.run(["java", "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
    return tmp, cls, run


trap = [(b ^ 0x5A) - 256 * ((b ^ 0x5A) > 127) for b in TRAP.encode()]
tmp, _, k = build([], trap, "System.out.println(new Gate().probeKey());", False)  # clean-stub key
shutil.rmtree(tmp)
k = int(k.splitlines()[-1])
plain = TOKENS[variant].encode()
if variant == "string_state":
    enc = [((p ^ ((k & 0xFFFFFFFF) >> ((i % 4) * 8)) ^ i) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(plain)]
    show = "new Gate().onCreate(null);"
else:
    enc = [((p ^ ((k & 0xFFFFFFFFFFFFFFFF) >> ((i % 8) * 8))) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(plain)]
    show = "System.out.println(new Gate().debuggerGate());"
# oracle: the JVM prints the machine's terminal output on CLEAN stubs (or DEBUGGED stubs with --debugged)
tmp, cls, shown = build(enc, trap, show, debugged)
if debugged:
    shutil.rmtree(tmp)
    print(f"key={k} debugged-JVM terminal={shown!r}")
    sys.exit(0)
for junk in ("android", f"{pdir}/Probe.class"):
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
print(f"key={k} clean-JVM terminal={shown!r}")
