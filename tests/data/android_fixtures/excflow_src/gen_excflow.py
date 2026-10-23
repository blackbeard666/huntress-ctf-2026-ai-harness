#!/usr/bin/env python3
"""Generate the excflow_* fixtures (coverage atlas row 90: anti-debug / anti-tamper code using try/catch as control
flow -- a probe throws, the catch handler picks the path).
usage: gen_excflow.py <variant: handler_only | stub_nested | decoy_debug> <out.apk>
Java app + android.* stubs (a clean retail device: Debug false, PackageManager throws NameNotFound) are compiled with
javac --release 8; the token is xor'd with the key the JVM itself computes on those stubs (stage 1), then the JVM
prints Vault/Shield.reveal() (stage 2 = the oracle). App classes only -> dex2jar d2j-jar2dex -> zipfile.
  handler_only: Guard.key() folds which handler each probe level reaches (custom TamperException extends
                SecurityException, ArithmeticException 7/0, ArrayIndexOutOfBounds, NPE on a null String receiver,
                NumberFormatException from parseInt, finally catch-alls); the token is decoded ONLY inside
                reveal()'s catch (SecurityException) keyed on the thrown message's hashCode.
  stub_nested:  NameNotFound caught and rethrown as IllegalStateException through a nested try/finally one frame up,
                FileNotFound (/system/xbin/su), ClassNotFound (XposedBridge); decode only in an NPE handler.
  decoy_debug:  the ANS token sits in the handler of a throw that only fires when Debug.isDebuggerConnected();
                the clean path returns a near-miss -> expected none."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"handler_only": "ANS-7c2e91f04ab3d658", "stub_nested": "ANS-e5039bd7a1c46f28",
          "decoy_debug": "ANS-3a9f0c61d7e2b854"}
PKG = "com.huntress.mobile.d21.exc"
STUBS = {
    "android/os/Debug.java": """package android.os;
public class Debug { public static boolean isDebuggerConnected() { return %(dbg)s; } }""",
    "android/content/pm/PackageInfo.java": "package android.content.pm;\npublic class PackageInfo { }",
    "android/content/pm/PackageManager.java": """package android.content.pm;
public class PackageManager {
  public static class NameNotFoundException extends Exception { public NameNotFoundException(String s) { super(s); } }
  public PackageInfo getPackageInfo(String p, int f) throws NameNotFoundException { throw new NameNotFoundException(p); }
}""",
    "android/content/Context.java": """package android.content;
public class Context { public android.content.pm.PackageManager getPackageManager() { return new android.content.pm.PackageManager(); } }""",
    "android/app/Activity.java": "package android.app;\npublic class Activity extends android.content.Context { }",
}
TAMPER = """package %(pkg)s;
public class TamperException extends SecurityException { public TamperException(String m) { super(m); } }"""
APP = {
    "handler_only": {"Guard.java": """package %(pkg)s;
public final class Guard {
  static final int[] T = {3, 1, 4, 1, 5};
  static String lbl = "probe";
  static void probe(int lvl) {
    if (lvl == 0) throw new TamperException("sig-mismatch");
    if (lvl == 1) { int z = T[1] - 1; T[0] = 7 / z; }
    if (lvl == 2) T[lvl + 7] = 1;
    if (lvl == 3) { String s = lvl > 2 ? null : lbl; T[1] = s.length(); }
    if (lvl == 4) T[2] = Integer.parseInt("x" + lvl);
  }
  public static int key() {
    int k = 0x31;
    for (int i = 0; i < 6; i++) {
      try { probe(i); k = k * 3 + 1; }
      catch (TamperException e) { k = k * 5 + e.getMessage().length(); }
      catch (ArithmeticException e) { k = k * 7 + 2; }
      catch (IndexOutOfBoundsException e) { k = k * 11 + 3; }
      catch (IllegalArgumentException e) { k = k * 13 + 4; }
      catch (RuntimeException e) { k = k * 17 + 5; }
      finally { k ^= i << 4; }
    }
    return k;
  }
}""", "Vault.java": """package %(pkg)s;
public final class Vault {
  static final byte[] ENC = {%(enc)s};
  static void attest(int k) { if (k != 0) throw new TamperException("clean:" + (k & 0xff)); }
  public static int mkey() {
    try { attest(Guard.key()); return 0; } catch (SecurityException e) { return e.getMessage().hashCode(); }
  }
  public static String reveal() {
    int k = Guard.key();
    try {
      attest(k);
      return "attest-ok";
    } catch (SecurityException e) {
      int m = e.getMessage().hashCode();
      char[] c = new char[ENC.length];
      for (int i = 0; i < c.length; i++) c[i] = (char) ((ENC[i] ^ (m >>> ((i %% 4) * 8)) ^ i) & 0xFF);
      return new String(c);
    }
  }
}"""},
    "stub_nested": {"Shield.java": """package %(pkg)s;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import android.app.Activity;
import android.content.pm.PackageManager;
public class Shield extends Activity {
  static final byte[] ENC = {%(enc)s};
  void attest() {
    try { getPackageManager().getPackageInfo("com.topjohnwu.magisk", 0); }
    catch (PackageManager.NameNotFoundException e) { throw new IllegalStateException("no-root"); }
  }
  public int probes() {
    int k = 0x6b;
    try {
      try { attest(); k += 1; }
      finally { k = k * 3; }
    } catch (IllegalStateException t) { k = k * 5 + t.getMessage().length(); }
    try { new FileInputStream("/system/xbin/su").close(); k += 50; }
    catch (FileNotFoundException e) { k ^= 0x55; }
    catch (IOException e) { k ^= 1; }
    try { Class.forName("de.robv.android.xposed.XposedBridge"); k += 100; }
    catch (ClassNotFoundException e) { k += 7; }
    return k;
  }
  public String reveal() {
    int k = probes();
    StringBuilder sb = new StringBuilder();
    try {
      Object o = k > 0 ? null : this;
      sb.append(o.hashCode());
      return sb.toString();
    } catch (NullPointerException e) {
      for (int i = 0; i < ENC.length; i++) sb.append((char) ((ENC[i] - i * 3 ^ k >> (i %% 3)) & 0xFF));
      return sb.toString();
    }
  }
}"""},
    "decoy_debug": {"Vault.java": """package %(pkg)s;
import android.os.Debug;
public final class Vault {
  static final byte[] ENC = {%(enc)s};
  static void probe() { if (Debug.isDebuggerConnected()) throw new TamperException("dbg"); }
  public static int mkey() { return 0x5d; }
  public static String reveal() {
    try {
      probe();
      return "ANS-" + "cleanpath" + "-nohex";
    } catch (TamperException e) {
      char[] c = new char[ENC.length];
      for (int i = 0; i < c.length; i++) c[i] = (char) ((ENC[i] ^ 0x5d ^ i) & 0xFF);
      return new String(c);
    }
  }
}"""},
}
PROBE = """package %(pkg)s;
public final class Probe { public static void main(String[] a) { System.out.println(%(body)s); } }"""
pdir = PKG.replace(".", "/")
act = variant == "stub_nested"


def build(enc, body, dbg="false"):
    tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
    src, cls = tmp / "src", tmp / "cls"
    files = {k: v % {"dbg": dbg} if "%(" in v else v for k, v in STUBS.items()}
    files[f"{pdir}/TamperException.java"] = TAMPER % {"pkg": PKG}
    for n, b in APP[variant].items():
        files[f"{pdir}/{n}"] = b % {"pkg": PKG, "enc": ", ".join(map(str, enc))}
    files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG, "body": body}
    for rel, b in files.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_text(b)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    run = subprocess.run(["java", "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
    return tmp, cls, run


tmp, _, k = build([], "new Shield().probes()" if act else "Vault.mkey()")
shutil.rmtree(tmp)
k = int(k)
plain = TOKENS[variant].encode()
if act:  # inverse of ((e - 3i) ^ (k >> (i%3))) & 0xFF == p
    enc = [(((p ^ (k >> (i % 3))) & 0xFF) + 3 * i + 128) % 256 - 128 for i, p in enumerate(plain)]
elif variant == "decoy_debug":  # the trap handler's fixed 0x5d key
    enc = [((p ^ 0x5D ^ i) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(plain)]
else:
    enc = [((p ^ (k >> ((i % 4) * 8)) ^ i) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(plain)]
body = "new Shield().reveal()" if act else "Vault.reveal()"
if variant == "decoy_debug":
    tmp, _, dbg_shown = build(enc, body, dbg="true")
    shutil.rmtree(tmp)
    print(f"debugger-attached JVM reveal()={dbg_shown!r} (the trap)")
tmp, cls, shown = build(enc, body)  # oracle: the JVM on the clean stubs
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
