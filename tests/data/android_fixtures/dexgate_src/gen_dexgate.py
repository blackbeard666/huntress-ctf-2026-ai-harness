#!/usr/bin/env python3
"""Generate the dexgate_* fixtures (coverage atlas rows 47-49: a root / emulator / signature check in Java gating a
constant). usage: gen_dexgate.py <variant: root_b64xor | emu_hex_sub | decoy_nearmiss> <out.apk>
Writes Java sources, compiles with javac, converts with dex2jar's d2j-jar2dex, zips classes.dex (+ the manifest of a
stock fixture) with zipfile. The ANS token is never a literal in the dex: it is encoded here, in the generator."""
import base64, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"root_b64xor": "flag:ANS-7c41e09b2d5fa386", "emu_hex_sub": "ANS-e2a95d0c7b3418f6",
          "decoy_nearmiss": "flag:ANS-7c41e09b2d5fa38"}  # decoy: 15 hex digits
plain = TOKENS[variant].encode()
pkg = "com/huntress/mobile/d16/g5a1c"
stub = """package android.os;
public class Build { public static String TAGS = "release-keys"; public static String HARDWARE = "qcom";
  public static String FINGERPRINT = "x"; }
"""
if variant in ("root_b64xor", "decoy_nearmiss"):
    enc = base64.b64encode(bytes(b ^ 0x37 for b in plain)).decode()
    check = """package com.huntress.mobile.d16.g5a1c;
import java.io.File;
public final class RootCheck {
  static final String[] PATHS = {"/system/xbin/su", "/system/bin/su", "/sbin/magisk", "/data/adb/magisk"};
  public static boolean isRooted() {
    String t = android.os.Build.TAGS;
    if (t != null && t.contains("test-keys")) return true;
    for (String p : PATHS) if (new File(p).exists()) return true;
    return false;
  }
}
"""
    main = """package com.huntress.mobile.d16.g5a1c;
public final class Vault {
  static String x(String s, int k) {
    byte[] b = java.util.Base64.getDecoder().decode(s);
    for (int i = 0; i < b.length; i++) b[i] = (byte) (b[i] ^ k);
    return new String(b);
  }
  public static String reveal() {
    if (RootCheck.isRooted()) return "Device integrity check failed";
    return x("%s", 0x37);
  }
}
""" % enc
else:
    enc = bytes((b + 0x0B) & 0xFF for b in plain).hex()
    check = """package com.huntress.mobile.d16.g5a1c;
import java.io.BufferedReader;
import java.io.FileReader;
public final class EnvProbe {
  public static boolean hostile() {
    String h = android.os.Build.HARDWARE;
    if (h.contains("goldfish") || h.contains("ranchu")) return true;
    try (BufferedReader r = new BufferedReader(new FileReader("/proc/self/status"))) {
      String l;
      while ((l = r.readLine()) != null)
        if (l.startsWith("TracerPid:") && !l.substring(10).trim().equals("0")) return true;
    } catch (Exception e) { }
    try (BufferedReader r = new BufferedReader(new FileReader("/proc/self/maps"))) {
      String l;
      while ((l = r.readLine()) != null) if (l.contains("frida")) return true;
    } catch (Exception e) { }
    return false;
  }
}
"""
    main = """package com.huntress.mobile.d16.g5a1c;
public final class Vault {
  static String unhex(String s) {
    byte[] b = new byte[s.length() / 2];
    for (int i = 0; i < b.length; i++) b[i] = (byte) (Integer.parseInt(s.substring(2 * i, 2 * i + 2), 16) - 11);
    return new String(b);
  }
  public static String reveal() {
    if (!EnvProbe.hostile()) return unhex("%s");
    return "emulator detected";
  }
}
""" % enc
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
for rel, body in (("android/os/Build.java", stub), (f"{pkg}/RootCheck.java" if "RootCheck" in check else f"{pkg}/EnvProbe.java", check),
                  (f"{pkg}/Vault.java", main)):
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(body)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.rmtree(cls / "android")  # framework stub: provided by the device, not packaged
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")], check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out, enc)
