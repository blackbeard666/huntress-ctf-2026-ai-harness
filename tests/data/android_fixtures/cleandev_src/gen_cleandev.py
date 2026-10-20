#!/usr/bin/env python3
"""Generate the cleandev_* fixtures (coverage atlas rows 41, 47, 48: root / emulator / debugger / Frida checks whose
RESULTS key the answer, so only a clean-device evaluation recovers it).
usage: gen_cleandev.py <variant: score_xor | pm_proc_socket | decoy_trap> <out.apk>
Java app + android.* framework stubs are compiled with javac; the stubs model a clean retail Pixel (Build.TAGS
release-keys, no debugger, PackageManager throws NameNotFound) and the rest is the host JVM itself (File.exists on
/system/xbin/su, /proc/self/status TracerPid, /proc/self/maps, a refused 127.0.0.1:27042, Class.forName).
Stage 1 runs Guard.key() on the JVM to get the check-derived key, the token is xor'd with that key stream here, stage
2 recompiles Vault with the bytes and the JVM prints Vault.reveal() (the oracle). App classes only -> d2j-jar2dex ->
zipfile. decoy_trap: bytes keyed for a ROOTED device (stub TAGS test-keys), so the clean path yields garbage."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"score_xor": "ANS-4f0b9c27e1d385a6", "pm_proc_socket": "flag{ANS-b81e6d0f3a52c947}",
          "decoy_trap": "ANS-0d7e35b9a4c1f862"}
PKG = "com.huntress.mobile.d19.envq"
STUBS = {
    "android/os/Build.java": """package android.os;
public class Build {
  static String p(String v) { return v; }
  public static final String TAGS = p("%(tags)s");
  public static final String FINGERPRINT = p("google/oriole/oriole:14/UQ1A.240205.004/11269751:user/%(tags)s");
  public static final String MODEL = p("Pixel 6"), HARDWARE = p("oriole"), PRODUCT = p("oriole"), BRAND = p("google");
}""",
    "android/os/Debug.java": """package android.os;
public class Debug { public static boolean isDebuggerConnected() { return false; }
  public static boolean waitingForDebugger() { return false; } }""",
    "android/content/pm/ApplicationInfo.java": """package android.content.pm;
public class ApplicationInfo { public static final int FLAG_DEBUGGABLE = 2; public int flags = 0x38c8be44; }""",
    "android/content/pm/PackageInfo.java": "package android.content.pm;\npublic class PackageInfo { }",
    "android/content/pm/PackageManager.java": """package android.content.pm;
public class PackageManager {
  public static class NameNotFoundException extends Exception { public NameNotFoundException(String s) { super(s); } }
  public PackageInfo getPackageInfo(String p, int f) throws NameNotFoundException { throw new NameNotFoundException(p); }
}""",
    "android/content/Context.java": """package android.content;
public class Context { public android.content.pm.PackageManager getPackageManager() { return new android.content.pm.PackageManager(); }
  public android.content.pm.ApplicationInfo getApplicationInfo() { return new android.content.pm.ApplicationInfo(); } }""",
    "android/app/Activity.java": "package android.app;\npublic class Activity extends android.content.Context { }",
}
GUARD = {
    "score_xor": """package %(pkg)s;
import java.io.File;
import android.os.Build;
import android.os.Debug;
public final class Guard {
  static final String[] PATHS = {"/system/xbin/su", "/system/bin/su", "/sbin/magisk", "/system/xbin/busybox",
      "/data/local/tmp/frida-server", "/system/app/Superuser.apk"};
  static boolean emulator() {
    return Build.FINGERPRINT.startsWith("generic") || Build.FINGERPRINT.contains("vbox") || Build.MODEL.contains("sdk")
        || Build.MODEL.contains("Emulator") || Build.HARDWARE.contains("goldfish") || Build.HARDWARE.contains("ranchu")
        || Build.PRODUCT.contains("sdk") || System.getProperty("ro.kernel.qemu") != null;
  }
  public static int key() {
    int s = 0x5A17;
    for (String p : PATHS) s = s * 31 + (new File(p).exists() ? 3 : 11);
    s ^= Build.TAGS.hashCode();
    s = s * 7 + (emulator() ? 0x1D : 0x2B);
    if (Debug.isDebuggerConnected() || Debug.waitingForDebugger()) s = ~s;
    return s;
  }
}""",
    "pm_proc_socket": """package %(pkg)s;
import java.io.BufferedReader;
import java.io.FileReader;
import java.net.Socket;
import android.app.Activity;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
public class Guard extends Activity {
  boolean pkg(String p) {
    try { getPackageManager().getPackageInfo(p, 0); return true; }
    catch (PackageManager.NameNotFoundException e) { return false; }
  }
  static int tracer() {
    try {
      BufferedReader r = new BufferedReader(new FileReader("/proc/self/status"));
      String l;
      int v = -1;
      while ((l = r.readLine()) != null) if (l.startsWith("TracerPid:")) v = Integer.parseInt(l.substring(10).trim());
      r.close();
      return v;
    } catch (Exception e) { return -2; }
  }
  static boolean hooked() {
    try {
      BufferedReader r = new BufferedReader(new FileReader("/proc/self/maps"));
      String l;
      boolean h = false;
      while ((l = r.readLine()) != null) if (l.contains("frida") || l.contains("XposedBridge")) h = true;
      r.close();
      return h;
    } catch (Exception e) { return true; }
  }
  static boolean fridaPort() {
    try { Socket s = new Socket("127.0.0.1", 27042); s.close(); return true; }
    catch (Exception e) { return false; }
  }
  static boolean xposed() {
    try { Class.forName("de.robv.android.xposed.XposedBridge"); return true; }
    catch (ClassNotFoundException e) { return false; }
  }
  public int key() {
    int k = 0x2F;
    k = k * 13 + (pkg("com.topjohnwu.magisk") ? 5 : 9);
    k = k * 13 + (pkg("de.robv.android.xposed.installer") ? 5 : 9);
    k = k * 13 + ((getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0 ? 5 : 9);
    k = k * 13 + tracer() + 4;
    k = k * 13 + (hooked() ? 5 : 9);
    k = k * 13 + (fridaPort() ? 5 : 9);
    k = k * 13 + (xposed() ? 5 : 9);
    return k;
  }
}""",
}
GUARD["decoy_trap"] = GUARD["score_xor"]
VAULT_STATIC = """package %(pkg)s;
public final class Vault {
  static final byte[] ENC = {%(enc)s};
  public static String reveal() {
    int k = Guard.key();
    char[] c = new char[ENC.length];
    for (int i = 0; i < c.length; i++) c[i] = (char) ((ENC[i] ^ (k >>> ((i %% 4) * 8)) ^ i) & 0xFF);
    return new String(c);
  }
}"""
VAULT_ACT = """package %(pkg)s;
public final class Vault extends Guard {
  static final byte[] ENC = {%(enc)s};
  public String reveal() {
    int k = key();
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < ENC.length; i++) sb.append((char) ((ENC[i] - i * 3 ^ k >> (i %% 3)) & 0xFF));
    return sb.toString();
  }
}"""
PROBE = """package %(pkg)s;
public final class Probe { public static void main(String[] a) {
  %(body)s } }"""
act = variant == "pm_proc_socket"
pdir = PKG.replace(".", "/")


def build(tags, enc, body):
    tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
    src, cls = tmp / "src", tmp / "cls"
    files = {k: v % {"tags": tags} if "%(" in v else v for k, v in STUBS.items()}
    files[f"{pdir}/Guard.java"] = GUARD[variant] % {"pkg": PKG}
    files[f"{pdir}/Vault.java"] = (VAULT_ACT if act else VAULT_STATIC) % {"pkg": PKG, "enc": ", ".join(map(str, enc))}
    files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG, "body": body}
    for rel, b in files.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_text(b)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    run = subprocess.run(["java", "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
    return tmp, cls, run


key_tags = "test-keys" if variant == "decoy_trap" else "release-keys"
tmp, _, k = build(key_tags, [], "System.out.println(" + ("new Vault().key()" if act else "Guard.key()") + ");")
shutil.rmtree(tmp)
k = int(k)
plain = TOKENS[variant].encode()
if act:  # inverse of ((e - 3i) ^ (k >> (i%3))) & 0xFF == p
    enc = [(((p ^ (k >> (i % 3))) & 0xFF) + 3 * i + 128) % 256 - 128 for i, p in enumerate(plain)]
else:
    enc = [((p ^ (k >> ((i % 4) * 8)) ^ i) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(plain)]
# oracle: the JVM on the CLEAN stubs (release-keys) prints what a clean device shows
tmp, cls, shown = build("release-keys", enc, "System.out.println(" + ("new Vault().reveal()" if act else "Vault.reveal()") + ");")
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
print(f"key={k} clean-JVM reveal()={shown!r}")
