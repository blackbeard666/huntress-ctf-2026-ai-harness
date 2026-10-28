#!/usr/bin/env python3
"""Generate the jvmcf_* fixtures (coverage atlas row 108: a dependency shipped as JVM bytecode, not dex).
usage: gen_jvmcf.py <variant: aar_format_chain | jar_indy_chain | class_const | decoy_runtime> <out.apk>
Writes Java sources, compiles with javac (--release 8 -> StringBuilder/String.format; default 21 -> invokedynamic
makeConcatWithConstants), packs the classes with `jar` (and `zip` for the .aar), then builds the APK with `zip`.
No ANS-<16 hex> literal exists for the *_chain variants: the token is computed by a 2+ method long chain."""
import os, shutil, subprocess, sys, tempfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
SRC = {
    "aar_format_chain": ("com/vendor/mathkit", ["--release", "8"], {
        "Mix.java": """package com.vendor.mathkit;
public final class Mix {
  static final long K1 = 0x5DEECE66DL;
  static long seed() { return K1 * 0x9E3779B97F4A7C15L ^ (K1 >>> 7); }
  static long mix(long x) { x ^= x >>> 33; x *= 0xff51afd7ed558ccdL; x ^= x >>> 33; return x + Fold.step(4); }
  public static String token() { return "ANS-" + String.format("%016x", mix(seed())); }
}
""",
        "Fold.java": """package com.vendor.mathkit;
final class Fold {
  static long step(int n) {
    long a = 0;
    for (int i = 0; i < n; i++) {
      switch (i) { case 0: a += 0x1111; break; case 1: a <<= 12; break; case 2: a |= 0x7L << 60; break;
                   default: a ^= 0xABCDEFL; }
    }
    return a;
  }
}
"""}),
    "jar_indy_chain": ("org/legacy/codec", [], {
        "Keys.java": """package org.legacy.codec;
public final class Keys {
  static long a() { long v = 0xC0FFEE1234L; return Long.rotateLeft(v, 21) - 0x55AA55AA55AAL; }
  static int b(int k) { return (k * 31 + 7) ^ 0x2F; }
  static long chain() { return a() ^ ((long) b(1009) << 40) ^ (a() >>> 3); }
  public static String token() { return "ANS-" + Long.toHexString(chain() | 0x8000000000000000L); }
}
"""}),
    "class_const": ("net/oldlib/xml", ["--release", "8"], {
        "Build.java": """package net.oldlib.xml;
public final class Build {
  public static final String LIB_VERSION = "2.4.1";
  public static final String ADVISORY = "ANS-3f9a0c7e51b2d846";
  public static String version() { return LIB_VERSION; }
}
"""}),
    # near-miss: token computed from a RUNTIME value, a 15-hex const, and an ANS- prefixed 17-hex composition
    "decoy_runtime": ("org/legacy/codec", [], {
        "Keys.java": """package org.legacy.codec;
public final class Keys {
  static final String NEAR = "ANS-3f9a0c7e51b2d84";
  static long a() { return System.nanoTime() ^ 0xC0FFEE1234L; }
  public static String token() { return "ANS-" + Long.toHexString(a()); }
  public static String wide() { return "ANS-" + String.format("%017x", 0x1234567890ABCDEFL); }
}
"""}),
}
if variant not in SRC:
    sys.exit("variant?")
pkg, jflags, files = SRC[variant]
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
try:
    src = tmp / "src" / pkg
    src.mkdir(parents=True)
    for n, s in files.items():
        (src / n).write_text(s)
    cls = tmp / "cls"
    subprocess.check_call(["javac", *jflags, "-d", str(cls), *[str(src / n) for n in files]])
    apk = tmp / "apk"
    (apk / "assets").mkdir(parents=True)
    (apk / "AndroidManifest.xml").write_bytes(b"")  # placeholder entry; the row-108 reader ignores the manifest
    if variant == "aar_format_chain":
        aar = tmp / "aar"
        aar.mkdir()
        subprocess.check_call(["jar", "cf", str(aar / "classes.jar"), "-C", str(cls), "."])
        (aar / "AndroidManifest.xml").write_text('<manifest package="com.vendor.mathkit"/>\n')
        subprocess.check_call(["zip", "-qr", str(apk / "assets" / "vendor-mathkit.aar"), "."], cwd=aar)
    else:
        subprocess.check_call(["jar", "cf", str(apk / "assets" / "legacy.jar"), "-C", str(cls), "."])
    out.unlink(missing_ok=True)
    subprocess.check_call(["zip", "-qr", str(out), "."], cwd=apk)
finally:
    shutil.rmtree(tmp)
