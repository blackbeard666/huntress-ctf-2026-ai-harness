#!/usr/bin/env python3
"""Generate the rootsig_* fixtures (coverage atlas rows 47, 94: multi-signal root detection whose WHOLE clean vector
keys the answer; forcing the aggregate check / every probe to 'not rooted' gives a decoy, not the answer).
usage: gen_rootsig.py <variant: mask_bool | map_score | bitset_enum | decoy_rooted> <out.apk>
Java app + android.* framework stubs (a clean retail Pixel: Build.TAGS release-keys, ro.secure 1, ro.debuggable 0,
ro.boot.selinux enforcing, PackageManager throws NameNotFound) compiled with javac; the rest is the host JVM itself
(File.exists on su paths, /proc/mounts, Runtime.exec of a missing /system/xbin/which). Stage 1 runs Sig.key() on the
JVM to get the vector-derived key, the token is xor'd with it here, stage 2 recompiles Vault with the bytes and the
JVM prints Vault.reveal() (the oracle). App classes only -> d2j-jar2dex -> zipfile.
decoy_rooted: bitset_enum keyed on the ROOTED stubs (test-keys, ro.debuggable 1, permissive), so the clean vector
(and the all-false forced vector) decode to garbage."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"mask_bool": "ANS-7c3e19a0d45b82f6", "map_score": "ANS-e2a95d0c7b16f348",
          "bitset_enum": "ANS-19f4b6c0e8d27a53", "decoy_rooted": "ANS-5b08e3d1f6a49c27"}
TRAP = "ANS-0000dead0000beef"  # map_score: what a forced all-clear vector (score 0) shows
PKG = "com.huntress.mobile.d22.rootsig"
STUBS = {
    "android/os/Build.java": """package android.os;
public class Build { static String p(String v) { return v; }
  public static final String TAGS = p("%(tags)s"), MODEL = p("Pixel 6"); }""",
    "android/os/SystemProperties.java": """package android.os;
public class SystemProperties { public static String get(String k) {
  if (k.equals("ro.secure")) return "%(secure)s";
  if (k.equals("ro.debuggable")) return "%(dbg)s";
  if (k.equals("ro.boot.selinux")) return "%(selinux)s";
  return ""; } }""",
    "android/content/pm/PackageInfo.java": "package android.content.pm;\npublic class PackageInfo { }",
    "android/content/pm/PackageManager.java": """package android.content.pm;
public class PackageManager {
  public static class NameNotFoundException extends Exception { public NameNotFoundException(String s) { super(s); } }
  public PackageInfo getPackageInfo(String p, int f) throws NameNotFoundException { throw new NameNotFoundException(p); }
}""",
    "android/content/Context.java": """package android.content;
public class Context { public android.content.pm.PackageManager getPackageManager() { return new android.content.pm.PackageManager(); } }""",
}
PROBES = """
  static boolean suBinary() {
    String[] ps = {"/system/xbin/su", "/system/bin/su", "/sbin/su", "/su/bin/su", "/data/local/xbin/su"};
    for (String p : ps) if (new File(p).exists()) return true;
    return false;
  }
  static boolean testKeys() { String t = Build.TAGS; return t != null && t.contains("test-keys"); }
  static boolean magiskPkg(Context c) {
    try { c.getPackageManager().getPackageInfo("com.topjohnwu.magisk", 0); return true; }
    catch (PackageManager.NameNotFoundException e) { return false; }
  }
  static boolean debuggable() { return "1".equals(SystemProperties.get("ro.debuggable")); }
  static boolean secure() { return "1".equals(SystemProperties.get("ro.secure")); }
  static boolean selinuxEnforcing() { return "enforcing".equals(SystemProperties.get("ro.boot.selinux")); }
  static boolean whichSu() {
    try { Process p = Runtime.getRuntime().exec(new String[]{"/system/xbin/which", "su"}); return p.waitFor() == 0; }
    catch (Exception e) { return false; }
  }
  static boolean systemRw() {
    try {
      BufferedReader r = new BufferedReader(new FileReader("/proc/mounts"));
      String l; boolean rw = false;
      while ((l = r.readLine()) != null) if (l.contains(" /system ") && l.contains(" rw,")) rw = true;
      r.close();
      return rw;
    } catch (Exception e) { return false; }
  }
"""
HEAD = """package %(pkg)s;
import java.io.*;
import java.util.*;
import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.SystemProperties;
"""
SIG = {
    "mask_bool": HEAD + """public final class Sig {""" + PROBES + """
  static int mask(Context c) {
    boolean[] s = new boolean[8];
    s[0] = suBinary(); s[1] = testKeys(); s[2] = magiskPkg(c); s[3] = debuggable();
    s[4] = secure(); s[5] = whichSu(); s[6] = systemRw(); s[7] = selinuxEnforcing();
    int m = 0;
    for (int i = 0; i < s.length; i++) m |= (s[i] ? 1 : 0) << i;
    return m;
  }
  static boolean isRooted(Context c) { return (mask(c) & 0x6F) != 0; }
  public static int key(Context c) { int m = mask(c); return (m * 0x9E3779B1) ^ (m << 13) ^ 0x2F6B3C1D; }
}""",
    "map_score": HEAD + """public final class Sig {""" + PROBES + """
  static final int[] W = {7, 11, 5, 3, 13, 2, 17, 19};
  static Map<String, Boolean> signals(Context c) {
    Map<String, Boolean> m = new LinkedHashMap<String, Boolean>();
    m.put("su", Boolean.valueOf(suBinary()));
    m.put("tags", Boolean.valueOf(testKeys()));
    m.put("magisk", Boolean.valueOf(magiskPkg(c)));
    m.put("debuggable", Boolean.valueOf(debuggable()));
    m.put("secure", Boolean.valueOf(secure()));
    m.put("which", Boolean.valueOf(whichSu()));
    m.put("rw", Boolean.valueOf(systemRw()));
    m.put("selinux", Boolean.valueOf(selinuxEnforcing()));
    return m;
  }
  public static int score(Context c) {
    int sc = 0, i = 0;
    for (Map.Entry<String, Boolean> e : signals(c).entrySet()) { if (e.getValue().booleanValue()) sc += W[i]; i++; }
    return sc;
  }
  public static int key(Context c) {
    Map<String, Boolean> m = signals(c);
    StringBuilder sb = new StringBuilder();
    for (String k : m.keySet()) sb.append(k.charAt(0)).append(m.get(k).booleanValue() ? '1' : '0');
    return sb.toString().hashCode() * 31 + score(c);
  }
}""",
    "bitset_enum": HEAD + """public final class Sig {""" + PROBES + """
  enum Signal { SU, TAGS, MAGISK, DEBUGGABLE, SECURE, WHICH, RW, SELINUX }
  static EnumSet<Signal> hits(Context c) {
    EnumSet<Signal> h = EnumSet.noneOf(Signal.class);
    if (suBinary()) h.add(Signal.SU);
    if (testKeys()) h.add(Signal.TAGS);
    if (magiskPkg(c)) h.add(Signal.MAGISK);
    if (debuggable()) h.add(Signal.DEBUGGABLE);
    if (secure()) h.add(Signal.SECURE);
    if (whichSu()) h.add(Signal.WHICH);
    if (systemRw()) h.add(Signal.RW);
    if (selinuxEnforcing()) h.add(Signal.SELINUX);
    return h;
  }
  public static int key(Context c) {
    EnumSet<Signal> h = hits(c);
    BitSet bs = new BitSet(16);
    int[] w = new int[8];
    for (Signal s : Signal.values()) { if (h.contains(s)) bs.set(s.ordinal() * 2 + 1); w[s.ordinal()] = h.contains(s) ? 3 : 1; }
    int k = bs.cardinality() * 0x1000193;
    for (int i = 0; i < 16; i++) k = k * 31 + (bs.get(i) ? i + 1 : 0);
    for (int x : w) k = (k << 3) ^ x;
    return k;
  }
}""",
}
SIG["decoy_rooted"] = SIG["bitset_enum"]
VAULT = """package %(pkg)s;
import android.content.Context;
public final class Vault {
  static final byte[] ENC = {%(enc)s};
  static final byte[] TRAP = {%(trap)s};
  static String x(byte[] b, int k) {
    char[] c = new char[b.length];
    for (int i = 0; i < c.length; i++) c[i] = (char) ((b[i] ^ (k >>> ((i %% 4) * 8)) ^ (i * 7)) & 0xFF);
    return new String(c);
  }
  public static String reveal(Context ctx) {
    %(gate)s
    return x(ENC, Sig.key(ctx));
  }
}"""
GATE = {"mask_bool": "if (Sig.isRooted(ctx)) return \"blocked\";",
        "map_score": "if (Sig.score(ctx) == 0) return x(TRAP, 0x5EC0DE);",
        "bitset_enum": "", "decoy_rooted": ""}
PROBE = """package %(pkg)s;
public final class Probe { public static void main(String[] a) { android.content.Context c = new android.content.Context();
  %(body)s } }"""
pdir = PKG.replace(".", "/")


def enc_of(plain, k):
    return [((p ^ (k >> ((i % 4) * 8)) ^ (i * 7)) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(plain)]


def build(rooted, enc, trap, body):
    tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
    src, cls = tmp / "src", tmp / "cls"
    sub = {"tags": "test-keys", "secure": "0", "dbg": "1", "selinux": "permissive"} if rooted else \
        {"tags": "release-keys", "secure": "1", "dbg": "0", "selinux": "enforcing"}
    files = {k: v % sub if "%(" in v else v for k, v in STUBS.items()}
    files[f"{pdir}/Sig.java"] = SIG[variant] % {"pkg": PKG}
    files[f"{pdir}/Vault.java"] = VAULT % {"pkg": PKG, "enc": ", ".join(map(str, enc)), "trap": ", ".join(map(str, trap)),
                                           "gate": GATE[variant]}
    files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG, "body": body}
    for rel, b in files.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_text(b)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    run = subprocess.run(["java", "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
    return tmp, cls, run


trap = enc_of(TRAP.encode(), 0x5EC0DE)
tmp, _, k = build(variant == "decoy_rooted", [], trap, "System.out.println(Sig.key(c));")
shutil.rmtree(tmp)
k = int(k)
enc = enc_of(TOKENS[variant].encode(), k)
# oracle: the JVM on the CLEAN stubs prints what a clean device shows
tmp, cls, shown = build(False, enc, trap, "System.out.println(Vault.reveal(c));")
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
