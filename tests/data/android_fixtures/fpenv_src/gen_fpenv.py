#!/usr/bin/env python3
"""Generate the fpenv_* fixtures (coverage atlas rows 48, 91: instrumentation detection that must separate REAL hook
signals from benign near-misses -- the false positives a clean process shows -- and whose verdicts key the answer).
usage: gen_fpenv.py <variant: maps_tcp | pkgs_classes | decoy_flagged> <out.apk>
maps_tcp: /proc/self/maps lines scored (frida / gadget / xposed / substrate substrings are candidates; only an agent .so /
  XposedBridge.jar path or a non-JIT /memfd exec mapping is real), /proc/net/tcp local port parsed (a bare "69A2" in a peer
  address is a false positive, only local :69A2 / :69A3 is real), Debug.isDebuggerConnected.
pkgs_classes: PackageManager.getInstalledPackages(0) + getInstalledApplications(0) package names vs hook-manager list,
  ClassLoader.loadClass(XposedBridge) / Class.forName(com.saurik.substrate.MS) CNFE, maps scored again (weighted).
Java app + android.* stubs compiled with javac; stage 1 runs Guard.key(ctx) on the host JVM (a real, uninstrumented Linux
process in a fresh `unshare -rn` network namespace: its own /proc/self/maps and an empty /proc/net/tcp, CNFE for hook classes, stub PackageManager with a stock list) to get the
verdict-derived key, the token is xor'd with that key stream, stage 2 recompiles Vault and the JVM prints Vault.reveal(ctx)
(the oracle). App classes only -> d2j-jar2dex -> zipfile. decoy_flagged: maps_tcp's app, bytes keyed for a process where
the naive substring verdicts fire (stage-1 Guard built with NAIVE=true: every candidate line counts as real), so the clean
path yields garbage."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"maps_tcp": "ANS-8c1e5a07d3f92b64", "pkgs_classes": "ANS-e47b02c9a58d16f3", "decoy_flagged": "ANS-1a9d6e3f0c5b7284"}
PKG = "com.huntress.mobile.d23.fpenv"
STUBS = {
    "android/os/Debug.java": "package android.os;\npublic final class Debug { public static boolean isDebuggerConnected() "
                             "{ return false; } }",
    "android/content/pm/ApplicationInfo.java": "package android.content.pm;\npublic class ApplicationInfo "
                                               "{ public String packageName; public int flags; }",
    "android/content/pm/PackageInfo.java": "package android.content.pm;\npublic class PackageInfo "
                                           "{ public String packageName; public ApplicationInfo applicationInfo; }",
    "android/content/pm/PackageManager.java": """package android.content.pm;
import java.util.*;
public class PackageManager {
  static final String[] STOCK = {"android", "com.android.systemui", "com.android.vending", "com.google.android.gms"};
  public List<PackageInfo> getInstalledPackages(int f) {
    List<PackageInfo> l = new ArrayList<>();
    for (String s : STOCK) { PackageInfo p = new PackageInfo(); p.packageName = s; l.add(p); }
    return l;
  }
  public List<ApplicationInfo> getInstalledApplications(int f) {
    List<ApplicationInfo> l = new ArrayList<>();
    for (String s : STOCK) { ApplicationInfo a = new ApplicationInfo(); a.packageName = s; l.add(a); }
    return l;
  }
}""",
    "android/content/Context.java": """package android.content;
public class Context {
  public ClassLoader getClassLoader() { return Context.class.getClassLoader(); }
  public android.content.pm.PackageManager getPackageManager() { return new android.content.pm.PackageManager(); }
}""",
}
COMMON = """
  static final boolean NAIVE = %(naive)s;
  static int fp;
  static int mapsScore() {
    int real = 0;
    try {
      BufferedReader r = new BufferedReader(new FileReader("/proc/self/maps"));
      String l;
      while ((l = r.readLine()) != null) {
        String s = l.toLowerCase();
        boolean cand = s.contains("frida") || s.contains("gadget") || s.contains("xposed") || s.contains("substrate")
            || s.contains("/memfd:") && s.contains(" r-xp ") || s.contains("[anon:dalvik-") || s.contains("libart.so");
        if (!cand) continue;
        boolean isReal = s.contains("frida-agent") || s.contains("frida-gadget") || s.endsWith("/libgadget.so")
            || s.contains("xposedbridge.jar") || s.contains("libsubstrate")
            || s.contains("/memfd:") && s.contains(" r-xp ") && !s.contains("jit-cache");
        if (isReal || NAIVE) real++; else fp++;
      }
      r.close();
    } catch (Exception e) { }
    return NAIVE ? real + 1 : real;  // the host JVM has no ART: NAIVE stands for the libart / dalvik lines it would flag
  }
"""
GUARD = {
    "maps_tcp": """package %(pkg)s;
import android.content.Context;
import android.os.Debug;
import java.io.BufferedReader;
import java.io.FileReader;
public final class Guard {""" + COMMON + """
  static boolean tcp() {
    try {
      BufferedReader r = new BufferedReader(new FileReader("/proc/net/tcp"));
      String l = r.readLine();
      boolean hit = false;
      while ((l = r.readLine()) != null) {
        l = l.trim();
        int a = l.indexOf(": ");
        if (a < 0) continue;
        String lp = l.substring(a + 11, a + 15).toUpperCase();
        if (lp.equals("69A2") || lp.equals("69A3")) hit = true;
        else if (l.toUpperCase().contains("69A2")) { if (NAIVE) hit = true; else fp++; }
      }
      r.close();
      return !hit;
    } catch (Exception e) { return true; }
  }
  public static int key(Context ctx) {
    int k = 0x3A97;
    k = k * 31 + (mapsScore() == 0 ? 0x15 : 0x4D);
    k = k * 31 + (tcp() ? 0x0F : 0x33);
    k = k * 31 + (Debug.isDebuggerConnected() ? 0x59 : 0x07);
    return k;
  }
}""",
    "pkgs_classes": """package %(pkg)s;
import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.List;
public final class Guard {""" + COMMON + """
  static final String[] MGRS = {"re.frida.server", "de.robv.android.xposed.installer", "org.lsposed.manager",
                                "com.topjohnwu.magisk", "io.github.lsposed.manager", "org.meowcat.edxposed.manager"};
  static boolean bad(String p) {
    if (p == null) return false;
    for (String m : MGRS) if (p.equals(m)) return true;
    return NAIVE && (p.startsWith("com.google.android.gm") || p.contains("android.ext"));
  }
  static int pkgs(Context ctx) {
    int n = 0;
    List<PackageInfo> ps = ctx.getPackageManager().getInstalledPackages(0);
    for (PackageInfo p : ps) if (bad(p.packageName)) n++;
    List<ApplicationInfo> as = ctx.getPackageManager().getInstalledApplications(0);
    for (int i = 0; i < as.size(); i++) if (bad(as.get(i).packageName)) n += 2;
    return n;
  }
  static int classes(Context ctx) {
    int found = 0;
    try { ctx.getClassLoader().loadClass("de.robv.android.xposed.XposedBridge"); found++; }
    catch (ClassNotFoundException e) { }
    try { Class.forName("com.saurik.substrate.MS"); found += 2; }
    catch (ClassNotFoundException e) { }
    return found;
  }
  public static int key(Context ctx) {
    int score = 4 * pkgs(ctx) + 3 * classes(ctx) + 5 * mapsScore();
    int k = 0x61C5;
    k = k * 31 + (score == 0 ? 0x2B : 0x71 + score);
    return k;
  }
}""",
}
GUARD["decoy_flagged"] = GUARD["maps_tcp"]
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


def build(naive, enc, body):
    tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
    src, cls = tmp / "src", tmp / "cls"
    files = dict(STUBS)
    files[f"{pdir}/Guard.java"] = GUARD[variant] % {"pkg": PKG, "naive": naive}
    files[f"{pdir}/Vault.java"] = VAULT % {"pkg": PKG, "enc": ", ".join(map(str, enc))}
    files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG, "body": body}
    for rel, b in files.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_text(b)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True,
                   capture_output=True)
    # unshare -rn: a fresh network namespace, so /proc/net/tcp is a clean process's (the build host may run :27043)
    run = subprocess.run(["unshare", "-rn", "java", "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
    return tmp, cls, run


ctx = "new android.content.Context()"
tmp, _, k = build("true" if variant == "decoy_flagged" else "false", [], f"Guard.key({ctx})")
shutil.rmtree(tmp)
k = int(k)
enc = [((p ^ (k >> ((i % 4) * 8)) ^ (i * 5)) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(TOKENS[variant].encode())]
# oracle: the JVM on the CLEAN guard (NAIVE=false, a real uninstrumented host process) prints what a clean device shows
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
