#!/usr/bin/env python3
"""Generate the shellprobe_* fixtures (coverage atlas row 95: root checks that shell out -- Runtime.exec(String |
String[]) and new ProcessBuilder(..).start() of `which su`, `su -c id`, `getprop ro.*`, `getenforce`, `id`, `mount` --
and fold the process OUTPUT + exit codes into the key that decodes the answer).
usage: gen_shellprobe.py <variant: exec_readline | pb_scanner | decoy_rooted> <out.apk>
Plain Java (javac --release 8), no android.* stubs needed. The ORACLE is the host JVM running the very same classes
with PATH = a fake toybox dir whose shell scripts print what a retail Pixel 6 / Android 14 prints (getprop release-keys
/ 0 / 1 / green, getenforce Enforcing, id uid=10234(u0_a234).., `which su` silent exit 1, toybox `mount` lines with no
rw /system / magisk) and that has NO `su` (so the JVM's own exec throws IOException "Cannot run program"). Stage 1
prints Sig.key() on that device, the token is xor'd with it here, stage 2 prints Vault.reveal() (the oracle).
decoy_rooted: exec_readline's code with ENC keyed on a ROOTED persona (which su -> /system/xbin/su, test-keys,
ro.debuggable 1, Permissive, su -c id -> uid=0(root)), so the clean device decodes garbage (no token).
App classes -> dex2jar d2j-jar2dex -> zipfile (manifest borrowed from skc_decoy_cbc_wrong_key.apk)."""
import os, shutil, stat, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"exec_readline": "ANS-4f1c9e07b2a6d385", "pb_scanner": "ANS-a83d05e6c1f94b72", "decoy_rooted": "ANS-6e2b91d4f07c3a58"}
PKG = "com.huntress.mobile.shellprobe"
pdir = PKG.replace(".", "/")
MOUNT_CLEAN = """/dev/block/dm-6 on / type ext4 (ro,seclabel,relatime)
/dev/block/dm-7 on /system_ext type ext4 (ro,seclabel,relatime)
/dev/block/dm-8 on /product type ext4 (ro,seclabel,relatime)
/dev/block/dm-9 on /vendor type ext4 (ro,seclabel,relatime)
tmpfs on /dev type tmpfs (rw,seclabel,nosuid,relatime,mode=755)
/dev/block/dm-48 on /data type f2fs (rw,lazytime,seclabel,nosuid,nodev,noatime)
"""
PERSONA = {
    "clean": {
        "getprop": 'case "$1" in ro.build.tags) echo release-keys;; ro.debuggable) echo 0;; ro.secure) echo 1;;'
                   ' ro.boot.verifiedbootstate) echo green;; *) echo;; esac',
        "getenforce": "echo Enforcing",
        "id": 'if [ "$1" = -u ]; then echo 10234; else echo "uid=10234(u0_a234) gid=10234(u0_a234) groups=10234(u0_a234),'
              '3003(inet),9997(everybody),20234(u0_a234_cache),50234(all_a234) context=u:r:untrusted_app:s0:c234,c256,'
              'c512,c768"; fi',
        "which": 'case "$1" in su|magisk|busybox) exit 1;; *) echo "/system/bin/$1";; esac',
        "mount": "printf '%s' '" + MOUNT_CLEAN + "'",  # printf: a dash builtin (no cat on this PATH)
    },
    "rooted": {
        "getprop": 'case "$1" in ro.build.tags) echo test-keys;; ro.debuggable) echo 1;; ro.secure) echo 0;;'
                   ' ro.boot.verifiedbootstate) echo orange;; *) echo;; esac',
        "getenforce": "echo Permissive",
        "id": 'if [ "$1" = -u ]; then echo 0; else echo "uid=0(root) gid=0(root) context=u:r:magisk:s0"; fi',
        "which": 'case "$1" in su|magisk|busybox) echo "/system/xbin/$1";; *) echo "/system/bin/$1";; esac',
        "mount": "printf '%s' '" + MOUNT_CLEAN + "magisk on /system type tmpfs (rw,seclabel,relatime)\n'",
        "su": 'shift; exec sh -c "$1"',
    },
}
SHELL = """package %(pkg)s;
import java.io.*;
import java.util.*;
public final class Shell {
  static String run(String cmd) {
    try {
      Process p = Runtime.getRuntime().exec(cmd);
      BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
      StringBuilder sb = new StringBuilder();
      String l;
      while ((l = r.readLine()) != null) sb.append(l.trim()).append(';');
      r.close();
      return sb.append(p.waitFor()).toString();
    } catch (IOException e) { return "ioe"; } catch (InterruptedException e) { return "int"; }
  }
  static String runv(String[] argv) {
    try {
      Process p = Runtime.getRuntime().exec(argv);
      BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
      String l = r.readLine();
      return (l == null ? "-" : l) + "#" + p.waitFor();
    } catch (Exception e) { return "ioe"; }
  }
  static String pb(String... argv) {
    try {
      ProcessBuilder b = new ProcessBuilder(argv);
      b.redirectErrorStream(true);
      Process p = b.start();
      Scanner s = new Scanner(p.getInputStream()).useDelimiter("\\\\A");
      String o = s.hasNext() ? s.next() : "";
      s.close();
      p.waitFor();
      return o.trim() + "#" + p.exitValue();
    } catch (Exception e) { return "ioe"; }
  }
}"""
SIG = {
    "exec_readline": """package %(pkg)s;
public final class Sig {
  static String vector() {
    StringBuilder v = new StringBuilder();
    v.append(Shell.run("which su")).append('/');
    v.append(Shell.run("getprop ro.build.tags")).append('/');
    v.append(Shell.run("getprop ro.debuggable")).append('/');
    v.append(Shell.run("getprop ro.secure")).append('/');
    v.append(Shell.run("getenforce")).append('/');
    v.append(Shell.runv(new String[]{"su", "-c", "id"})).append('/');
    String id = Shell.run("id");
    v.append(id.startsWith("uid=0(") ? "root" : id.substring(0, id.indexOf(' ')));
    return v.toString();
  }
  public static int key() { return vector().hashCode() ^ 0x5A17C0DE; }
}""",
    "pb_scanner": """package %(pkg)s;
public final class Sig {
  static int mountScore() {
    String m = Shell.pb("mount");
    int n = 1;
    for (int i = 0; i < m.length(); i++) if (m.charAt(i) == '\\n') n++;
    int bad = m.contains(" on /system ") && m.contains("(rw") ? 3 : 0;
    if (m.contains("magisk")) bad += 5;
    return n * 16 + bad;
  }
  static String vector() {
    return Shell.pb("sh", "-c", "getprop ro.boot.verifiedbootstate") + "|" + Shell.pb("id", "-u") + "|" + mountScore()
        + "|" + Shell.pb("su") + "|" + Shell.pb("which", "magisk") + "|" + Shell.pb("getenforce");
  }
  public static int key() { int h = vector().hashCode(); return (h * 0x9E3779B1) ^ (h >>> 11); }
}""",
}
SIG["decoy_rooted"] = SIG["exec_readline"]
VAULT = """package %(pkg)s;
public final class Vault {
  static final byte[] ENC = {%(enc)s};
  static String x(byte[] b, int k) {
    char[] c = new char[b.length];
    for (int i = 0; i < c.length; i++) c[i] = (char) ((b[i] ^ (k >>> ((i %% 4) * 8)) ^ (i * 13)) & 0xFF);
    return new String(c);
  }
  public static String reveal() { return x(ENC, Sig.key()); }
}"""
PROBE = """package %(pkg)s;
public final class Probe { public static void main(String[] a) { %(body)s } }"""


def enc_of(plain, k):
    return [((p ^ (k >> ((i % 4) * 8)) ^ (i * 13)) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(plain)]


def fakebin(tmp, persona):
    d = tmp / f"bin-{persona}"
    d.mkdir()
    for name, body in PERSONA[persona].items():
        (d / name).write_text("#!/bin/sh\n" + body + "\n")
        (d / name).chmod(stat.S_IRWXU)
    (d / "sh").symlink_to("/bin/sh")
    return d


def build(persona, enc, body):
    tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
    src, cls = tmp / "src", tmp / "cls"
    files = {f"{pdir}/Shell.java": SHELL % {"pkg": PKG}, f"{pdir}/Sig.java": SIG[variant] % {"pkg": PKG},
             f"{pdir}/Vault.java": VAULT % {"pkg": PKG, "enc": ", ".join(map(str, enc))},
             f"{pdir}/Probe.java": PROBE % {"pkg": PKG, "body": body}}
    for rel, b in files.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_text(b)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    java = shutil.which("java")
    run = subprocess.run([java, "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True,
                         env={"PATH": str(fakebin(tmp, persona)), "HOME": str(tmp)}).stdout.strip()
    return tmp, cls, run


tmp, _, k = build("rooted" if variant == "decoy_rooted" else "clean", [],
                  "System.out.println(Sig.vector()); System.out.println(Sig.key());")
shutil.rmtree(tmp)
vec, k = k.splitlines()[0], int(k.splitlines()[-1])
enc = enc_of(TOKENS[variant].encode(), k)
# oracle: the JVM on the CLEAN persona prints what a clean device shows
tmp, cls, shown = build("clean", enc, "System.out.println(Sig.vector()); System.out.println(Vault.reveal());")
(cls / f"{pdir}/Probe.class").unlink()
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(f"keyed-vector={vec!r} key={k} clean-JVM vector+reveal()={shown!r}")
