#!/usr/bin/env python3
"""Generate the hookintro_* fixtures (coverage atlas row 91: Frida / Xposed / Substrate detection by introspection whose
RESULTS key the answer, so only a clean-device evaluation recovers it).
usage: gen_hookintro.py <variant: stack_threads | proc_task_fd | decoy_hooked> <out.apk>
stack_threads: Thread.currentThread().getStackTrace() + new Throwable().getStackTrace() scanned for XposedBridge /
  com.saurik.substrate / a second ZygoteInit, Thread.getAllStackTraces().keySet() names (gum-js-loop / gmain /
  pool-frida), Modifier.isNative over Vault.class.getDeclaredMethods() and Class.forName(Guard).getDeclaredMethod,
  ctx.getClassLoader().loadClass(XposedBridge) + Class.forName(com.saurik.substrate.MS$2) caught as CNFE.
proc_task_fd: File("/proc/self/task").listFiles() + each task's comm read, File("/proc/self/fd").listFiles() +
  android.system.Os.readlink (linjector / frida), System.getenv LD_PRELOAD / CLASSPATH.
Java app + android.* stubs compiled with javac; stage 1 runs Guard.key(ctx) on the host JVM (a real, unhooked process:
its own stack, threads, /proc/self/task comms and fd links, CNFE for hook classes) to get the check-derived key, the
token is xor'd with that key stream, stage 2 recompiles Vault with the bytes and the JVM prints Vault.reveal(ctx) (the
oracle). App classes only -> d2j-jar2dex -> zipfile. decoy_hooked: proc_task_fd's app, bytes keyed for a FRIDA-injected
process (the stage-1 Os.readlink stub reports fd 3 -> frida-agent-64.so), so the clean path yields garbage."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"stack_threads": "ANS-3d8f0b61e2a47c95", "proc_task_fd": "ANS-a6e14c0f97b3d258", "decoy_hooked": "ANS-5f2c7e90d14b8a36"}
PKG = "com.huntress.mobile.d22.hookintro"
STUBS = {
    "android/content/Context.java": """package android.content;
public class Context { public ClassLoader getClassLoader() { return Context.class.getClassLoader(); } }""",
    "android/system/ErrnoException.java": """package android.system;
public class ErrnoException extends Exception { public ErrnoException(String s) { super(s); } }""",
    "android/system/Os.java": """package android.system;
public final class Os {
  public static String readlink(String p) throws ErrnoException {
    if (%(hooked)s && p.endsWith("/fd/3")) return "/memfd:frida-agent-64.so (deleted)";
    try { return java.nio.file.Files.readSymbolicLink(java.nio.file.Paths.get(p)).toString(); }
    catch (Exception e) { throw new ErrnoException(p); }
  }
}""",
}
GUARD = {
    "stack_threads": """package %(pkg)s;
import android.content.Context;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
public final class Guard {
  static boolean frames(StackTraceElement[] st) {
    int zyg = 0;
    for (StackTraceElement e : st) {
      String c = e.getClassName();
      if (c.contains("de.robv.android.xposed") || c.contains("com.saurik.substrate") || c.contains("LSPHooker")) return false;
      if (c.contains("MS$") && e.getMethodName().equals("invoked")) return false;
      if (c.equals("com.android.internal.os.ZygoteInit")) zyg++;
    }
    return zyg <= 1;
  }
  static boolean threads() {
    for (Thread t : Thread.getAllStackTraces().keySet()) {
      String n = t.getName();
      if (n.equals("gum-js-loop") || n.equals("gmain") || n.startsWith("pool-frida") || n.contains("frida")) return false;
    }
    return true;
  }
  static boolean natives() {
    for (Method m : Vault.class.getDeclaredMethods()) if (Modifier.isNative(m.getModifiers())) return false;
    try {
      Method f = Class.forName("%(pkg)s.Guard").getDeclaredMethod("threads");
      return !Modifier.isNative(f.getModifiers());
    } catch (Exception e) { return false; }
  }
  static boolean classes(Context ctx) {
    int found = 0;
    try { ctx.getClassLoader().loadClass("de.robv.android.xposed.XposedBridge"); found++; }
    catch (ClassNotFoundException e) { }
    try { Class.forName("com.saurik.substrate.MS$2"); found += 2; }
    catch (ClassNotFoundException e) { }
    return found == 0;
  }
  public static int key(Context ctx) {
    int k = 0x2C71;
    k = k * 31 + (frames(Thread.currentThread().getStackTrace()) ? 0x11 : 0x2F);
    k = k * 31 + (frames(new Throwable().getStackTrace()) ? 0x13 : 0x3B);
    k = k * 31 + (threads() ? 5 : 9);
    k = k * 31 + (natives() ? 0x21 : 0x47);
    k = k * 31 + (classes(ctx) ? 0x0D : 0x6B);
    return k;
  }
}""",
    "proc_task_fd": """package %(pkg)s;
import android.content.Context;
import android.system.Os;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
public final class Guard {
  static boolean tasks() {
    File[] ts = new File("/proc/self/task").listFiles();
    if (ts == null) return true;
    for (File t : ts) {
      try {
        BufferedReader r = new BufferedReader(new FileReader(new File(t, "comm")));
        String n = r.readLine();
        r.close();
        if (n != null && (n.contains("gum-js-loop") || n.contains("gmain") || n.contains("gdbus")
            || n.startsWith("pool-frida"))) return false;
      } catch (Exception e) { }
    }
    return true;
  }
  static boolean fds() {
    File[] fs = new File("/proc/self/fd").listFiles();
    if (fs == null) return true;
    for (File f : fs) {
      try {
        String l = Os.readlink(f.getAbsolutePath());
        if (l.contains("linjector") || l.contains("frida")) return false;
      } catch (Exception e) { }
    }
    return true;
  }
  static boolean env() {
    String p = System.getenv("LD_PRELOAD"), c = System.getenv("CLASSPATH");
    return (p == null || !p.contains("frida")) && (c == null || !c.toLowerCase().contains("xposed"));
  }
  public static int key(Context ctx) {
    int k = 0x5E03;
    k = k * 31 + (tasks() ? 0x17 : 0x29);
    k = k * 31 + (fds() ? 0x0B : 0x61);
    k = k * 31 + (env() ? 3 : 7);
    return k;
  }
}""",
}
GUARD["decoy_hooked"] = GUARD["proc_task_fd"]
VAULT = """package %(pkg)s;
public final class Vault {
  static final byte[] ENC = {%(enc)s};
  public static String reveal(android.content.Context ctx) {
    int k = Guard.key(ctx);
    char[] c = new char[ENC.length];
    for (int i = 0; i < c.length; i++) c[i] = (char) ((ENC[i] ^ (k >>> ((i %% 4) * 8)) ^ (i * 7)) & 0xFF);
    return new String(c);
  }
}"""
PROBE = """package %(pkg)s;
public final class Probe { public static void main(String[] a) {
  System.out.println(%(body)s); } }"""
pdir = PKG.replace(".", "/")


def build(hooked, enc, body):
    tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
    src, cls = tmp / "src", tmp / "cls"
    files = {k: v % {"hooked": hooked} if "%(" in v else v for k, v in STUBS.items()}
    files[f"{pdir}/Guard.java"] = GUARD[variant] % {"pkg": PKG}
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
tmp, _, k = build("true" if variant == "decoy_hooked" else "false", [], f"Guard.key({ctx})")
shutil.rmtree(tmp)
k = int(k)
enc = [((p ^ (k >> ((i % 4) * 8)) ^ (i * 7)) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(TOKENS[variant].encode())]
# oracle: the JVM on the CLEAN stubs (a real unhooked host process) prints what a clean device shows
tmp, cls, shown = build("false", enc, f"Vault.reveal({ctx})")
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
