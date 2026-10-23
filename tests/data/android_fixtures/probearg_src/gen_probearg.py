#!/usr/bin/env python3
"""Generate the probearg_* fixtures (coverage atlas rows 47, 48, 94: root probe ARGUMENTS built at runtime, so the
clean-device stubs must answer on the evaluated, normalised string, not on a dex literal).
usage: gen_probearg.py <variant: frag_xor | decoy_rooted> <out.apk>
Guard (an Activity) builds every probe argument at runtime: "/sys" + "tem/" + a 1-byte-xor'd byte[] (-> /system/bin/su),
a reversed StringBuilder with a doubled slash, a char[] with a trailing slash, an upper-case unknown /SYSTEM/etc path,
an unknown /cache path, and package names from base64 (com.topjohnwu.magisk), a reversed string (lsposed) and a xor'd
mixed-case "Zygisk" package. The dex holds none of those literals. Each answer folds into an int key; Vault xors the
token with it. Stage 1 runs Guard.key() on the host JVM (real File.exists on a host with no /system, /cache, /data/adb;
stub PackageManager throws NameNotFound = a clean device), stage 2 recompiles Vault with the bytes and the JVM prints
reveal() (the oracle). App classes only -> dex2jar d2j-jar2dex -> zipfile. decoy_rooted: the bytes are keyed for a
ROOTED device (Guard.fold of all-true answers), so the clean path shows garbage."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"frag_xor": "flag{ANS-7c3e19a5d04bf268}", "decoy_rooted": "flag{ANS-e5a1037d9c4b62f8}"}
PKG = "com.huntress.mobile.d22.probearg"
STUBS = {
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


def jbytes(s, k):
    return ", ".join(str(((ord(c) ^ k) ^ 0x80) - 0x80) for c in s)


GUARD = """package %(pkg)s;
import java.io.File;
import android.app.Activity;
import android.content.pm.PackageManager;
public class Guard extends Activity {
  static final byte[] P0 = {%(p0)s};
  static final byte[] K0 = {%(k0)s};
  static String x(byte[] b, int k) {
    char[] c = new char[b.length];
    for (int i = 0; i < b.length; i++) c[i] = (char) ((b[i] ^ k) & 0xFF);
    return new String(c);
  }
  static String rev(String s) { return new StringBuilder(s).reverse().toString(); }
  static String b64(String s) { return new String(java.util.Base64.getDecoder().decode(s)); }
  static String[] paths() {
    return new String[] {
      "/sys" + "tem/" + x(P0, 0x5C),
      rev("xobysub/nibx//metsys/"),
      new String(new char[] {'/', 'd', 'a', 't', 'a', '/', 'a', 'd', 'b', '/', 'm', 'o', 'd', 'u', 'l', 'e', 's', '/'}),
      "/SYSTEM/etc/" + rev("nomead_us_dellatsni."),
      "/cache" + "//" + rev("t00r./yrevocer"),
    };
  }
  static String[] pkgs() {
    return new String[] { b64("Y29tLnRvcGpvaG53dS5tYWdpc2s="), rev("reganam.desopsl.buhtig.oi"), x(K0, 0x21) };
  }
  boolean pkg(String p) {
    try { getPackageManager().getPackageInfo(p, 0); return true; }
    catch (PackageManager.NameNotFoundException e) { return false; }
  }
  static int fold(boolean[] r) {
    int s = 0x6B1D;
    for (int i = 0; i < r.length; i++) s = s * 31 + (r[i] ? 3 + i : 11 + 2 * i);
    return s;
  }
  public int key() {
    String[] ps = paths(), ks = pkgs();
    boolean[] r = new boolean[ps.length + ks.length];
    for (int i = 0; i < ps.length; i++) r[i] = new File(ps[i]).exists();
    for (int i = 0; i < ks.length; i++) r[ps.length + i] = pkg(ks[i]);
    return fold(r);
  }
}"""
VAULT = """package %(pkg)s;
public final class Vault extends Guard {
  static final byte[] ENC = {%(enc)s};
  public String reveal() {
    int k = key();
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < ENC.length; i++) sb.append((char) ((ENC[i] ^ (k >>> ((i %% 4) * 8)) ^ i) & 0xFF));
    return sb.toString();
  }
}"""
PROBE = """package %(pkg)s;
public final class Probe { public static void main(String[] a) {
  %(body)s } }"""
pdir = PKG.replace(".", "/")
for p in ("/system", "/cache", "/data/adb", "/sbin/su", "/data/local/tmp"):
    assert not os.path.exists(p), f"host has {p}: the JVM would not model a clean device"


def build(enc, body):
    tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
    src, cls = tmp / "src", tmp / "cls"
    files = dict(STUBS)
    files[f"{pdir}/Guard.java"] = GUARD % {"pkg": PKG, "p0": jbytes("bin/su", 0x5C), "k0": jbytes("dev.Zygisk.next", 0x21)}
    files[f"{pdir}/Vault.java"] = VAULT % {"pkg": PKG, "enc": ", ".join(map(str, enc))}
    files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG, "body": body}
    for rel, b in files.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_text(b)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    run = subprocess.run(["java", "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
    return tmp, cls, run


tmp, _, args = build([], "for (String p : Guard.paths()) System.out.println(p); for (String p : Guard.pkgs()) "
                         "System.out.println(p); boolean[] r = new boolean[8]; java.util.Arrays.fill(r, true); "
                         "System.out.println(new Vault().key()); System.out.println(Guard.fold(r));")
shutil.rmtree(tmp)
*resolved, k_clean, k_rooted = args.splitlines()
k = int(k_rooted if variant == "decoy_rooted" else k_clean)
plain = TOKENS[variant].encode()
enc = [((p ^ (k >> ((i % 4) * 8)) ^ i) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(plain)]
# oracle: the JVM on the clean host prints what a clean device shows
tmp, cls, shown = build(enc, "System.out.println(new Vault().reveal());")
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
print(f"resolved probe args={resolved} key_clean={k_clean} key_rooted={k_rooted} used={k} clean-JVM reveal()={shown!r}")
