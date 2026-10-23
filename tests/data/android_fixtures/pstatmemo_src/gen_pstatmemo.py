#!/usr/bin/env python3
"""Generate the pstatmemo_* fixtures (coverage atlas rows 96/97, target dex-eval-pure-static-memo): a D23-style puzzle
v2 `analysis` APK whose `Release.code()` = "ANS-" + 16 nibbles of a 64-bit mixer chain fed by several Probe.s1/s2/s3
<=4096-step inverse searches (pure static int/long fns, some called twice: from code() and proof()).
usage: gen_pstatmemo.py <variant: probe6 | wide_switch | decoy_runtime> <out.apk>
Writes Java sources, compiles with javac --release 8, converts with dex2jar's d2j-jar2dex, zips classes.dex + the
manifest of a stock fixture + the v2 puzzle json with zipfile. The oracle (oracle.sh) runs the SAME classes on the JVM."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com/huntress/mobile/d24/psm"
P = "package com.huntress.mobile.d24.psm;\n"
PROBE = """
public final class Probe {
  public static int s1(int a, int b, int c, int d) {
    int i = 0;
    while ((((i ^ c) * a + b) & 4095) != d) { i++; if (i >= 4096) return -1; }
    return i;
  }
  public static int s2(int a, int b, int c, int d) {
    int r = (a % 11) + 1;
    for (int i = 0; i < 4096; i++) {
      int x = ((i << r) | (i >>> (32 - r))) ^ c;
      if (((x + b) & 4095) == d) return i;
    }
    return -1;
  }
  public static int s3(int a, int b, int c, int d) {
    for (int i = 0; i < 4096; i++) {
      if (gate(i * a, b, c) == d) return i;
    }
    return -1;
  }
  static int gate(int x, int y, int z) { return Math.abs((x ^ y ^ z) % 4093); }
}
"""
MIX = {
    "probe6": """
public final class Mix {
  public static long f1(long v) { v ^= v >>> 33; v *= 0xFF51AFD7ED558CCDL; v ^= v >>> 33; v *= 0xC4CEB9FE1A85EC53L; return v ^ (v >>> 33); }
  public static long f2(long v, int k) { return (v << (k & 63)) | (v >>> (64 - (k & 63))); }
  public static long fold(int n) { long v = 0x9E3779B97F4A7C15L; for (int k = 2; k <= n; k++) v = f1(v + k); return v; }
}
""",
    "wide_switch": """
public final class Mix {
  public static long f1(long v) {
    for (int r = 0; r < 4; r++) {
      switch ((int) (v & 7)) {
        case 0: v = v * 0x100000001B3L + 7; break;
        case 1: v ^= v << 13; break;
        case 3: v ^= v >>> 7; break;
        case 5: v = ~v + 0x5DEECE66DL; break;
        case 1000: v -= 1; break;
        default: v ^= v << 17;
      }
      v = Math.max((int) v, 3) ^ (v * 31);
    }
    return v;
  }
  public static long f2(long v, int k) { return (v << (k & 63)) | (v >>> (64 - (k & 63))); }
  public static long fold(int n) { long v = 0x2545F4914F6CDD1DL; for (int k = 2; k <= n; k++) v = f1(v ^ ((long) k << 40)); return v; }
}
""",
}
MIX["decoy_runtime"] = MIX["probe6"]
TOKEN = {
    "probe6": """
  static long token() {
    long t = Mix.fold(9);
    t ^= (long) Probe.s1(37, 11, 1234, 3000) * 0x9E3779B97F4A7C15L;
    t = Mix.f2(t, Probe.s2(17, 5, 777, 4000) & 63) ^ Probe.s3(97, 23, 41, 4000);
    t ^= (long) Probe.s1(53, 7, 99, 4090) << 20;
    t += Probe.s2(29, 3, 4095, 17);
    return Mix.f1(t ^ Probe.s3(13, 1, 2, 4092));
  }
""",
    "wide_switch": """
  static long token() {
    long t = Mix.fold(12);
    for (int k = 0; k < 3; k++) t = Mix.f1(t + Probe.s1(41 + 2 * k, 13, 2000 + k, 4093 - k));
    t ^= (long) Probe.s3(101, 9, 8, 4091) << 33;
    return Mix.f2(t, Probe.s2(23, 19, 5, 4094)) ^ Probe.s1(61, 0, 0, 4095);
  }
""",
    # near-miss: the same chain, but one input is the clock -> nothing static to evaluate
    "decoy_runtime": """
  static long token() {
    long t = Mix.fold(9) ^ System.nanoTime();
    t ^= (long) Probe.s1(37, 11, 1234, 3000) * 0x9E3779B97F4A7C15L;
    return Mix.f1(t ^ Probe.s3(13, 1, 2, 4092));
  }
""",
}
RELEASE = """
public final class Release {
  static final String HEX = "0123456789ABCDEF";
%s
  public static String code() {
    long v = Mix.f1(token()) ^ 0x5A5A00FF13572468L;
    StringBuilder sb = new StringBuilder("ANS-");
    for (int i = 60; i >= 0; i -= 4) sb.append(HEX.charAt((int) ((v >>> i) & 15)));
    return sb.toString();
  }
  public static String proof() { return Long.toHexString(token()); }
}
"""
if variant not in TOKEN:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src" / PKG, tmp / "cls"
src.mkdir(parents=True)
(src / "Probe.java").write_text(P + PROBE)
(src / "Mix.java").write_text(P + MIX[variant])
(src / "Release.java").write_text(P + RELEASE % TOKEN[variant])
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.glob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json",
               '{"schema":"huntress.mobile.puzzle.v2","day":24,"codec":"analysis","build":"psm-%s"}' % variant)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
