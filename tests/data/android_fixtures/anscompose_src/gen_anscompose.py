#!/usr/bin/env python3
"""Generate the anscompose_* fixtures (coverage atlas row 69: an answer COMPOSED in code from an "ANS-" const-string
plus numeric constants -- String.format("%08X%08X", hi, lo), Long.toHexString(a ^ b), Integer.toHexString(a) +
Integer.toHexString(b); no ANS-<16 hex> literal anywhere in the APK).
usage: gen_anscompose.py <variant: hilo_format | long_xor | tohex_ints | decoy_runtime> <out.apk>
Writes Java sources, compiles with javac --release 8, converts with dex2jar's d2j-jar2dex, zips classes.dex + the
manifest of a stock fixture with zipfile. The oracle (oracle.sh) runs the SAME compiled classes on the JVM."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
P = "package com.huntress.mobile.d20.c69;\n"
SRC = {
    "hilo_format": """
public final class Proof {
  static int seen;
  public static String token() {
    int hi = 0x9C41E07B;
    int lo = 0x2D5AF386;
    seen++;
    return "ANS-" + String.format("%08X%08X", hi, lo);
  }
}
""",
    "long_xor": """
public final class Proof {
  public static String token() {
    long a = 0xB3E1904C5A27D6F8L;
    long b = 0x1F2E3D4C5B6A7988L;
    StringBuilder sb = new StringBuilder("ANS-");
    sb.append(Long.toHexString(a ^ b));
    return sb.toString();
  }
}
""",
    "tohex_ints": """
public final class Proof {
  public static String token() {
    int a = 0xE4A7130F;
    int b = 0x6B92C5D1;
    return "ANS-" + Integer.toHexString(a) + Integer.toHexString(b);
  }
}
""",
    # near-miss: the ANS- prefix is composed with a RUNTIME value; the only 64-bit constant sits in another method
    "decoy_runtime": """
public final class Proof {
  public static long salt() { return 0x7A3C51E09D84B26FL; }
  public static String token() {
    long v = new java.security.SecureRandom().nextLong();
    return "ANS-" + String.format("%016X", v);
  }
}
""",
}
if variant not in SRC:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
(src / "com/huntress/mobile/d20/c69").mkdir(parents=True)
(src / "com/huntress/mobile/d20/c69/Proof.java").write_text(P + SRC[variant])
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "compose", "hint": "the app builds it from numbers"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
