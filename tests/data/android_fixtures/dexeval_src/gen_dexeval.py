#!/usr/bin/env python3
"""Generate the dexeval_* fixtures (coverage atlas rows 35/43/45: an answer COMPUTED by simple dex bytecode -- char
arrays, xor/add loops, StringBuilder, switch-flattened control flow, Base64 + Integer.parseInt).
usage: gen_dexeval.py <variant: xor_switch | b64_parse | decoy_nearmiss> <out.apk>
Writes Java sources, compiles with javac --release 8, converts with dex2jar's d2j-jar2dex, zips classes.dex + the
manifest of a stock fixture with zipfile. The oracle (oracle.sh) runs the SAME compiled classes on the JVM."""
import base64, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
P = "package com.huntress.mobile.d19.q4e;\n"


def masked(plain, seed):
    out, k = [], seed
    for ch in plain:
        out.append(ord(ch) ^ (k & 0xFF))
        k = (k * 31 + 7) & 0xFFFFFFFF
    return ", ".join(str(x) for x in out)


VAULT = P + """
public final class Vault {
  private static final char[] E = {%s};
  static String unmask(char[] e, int seed) {
    StringBuilder sb = new StringBuilder();
    int k = seed, i = 0, state = 0;
    while (true) {
      switch (state) {
        case 0: state = i >= e.length ? 3 : 1; break;
        case 1: sb.append((char) (e[i] ^ (k & 0xff))); state = 2; break;
        case 2: k = k * 31 + 7; i++; state = 0; break;
        case 3: return sb.toString();
        default: state = 0;
      }
    }
  }
  public static String token() { return unmask(E, 0x5d); }
}
"""
if variant == "xor_switch":
    files = {"Vault": VAULT % masked("token=ANS-6d0e94b1c7a3f258", 0x5D)}
elif variant == "decoy_nearmiss":  # same flattened decoder, the computed value has only 15 hex digits
    files = {"Vault": VAULT % masked("token=ANS-6d0e94b1c7a3f25", 0x5D)}
elif variant == "b64_parse":
    plain = b"ANS-a41f07c3e98d2b56"
    enc = base64.b64encode(bytes((b + 3 + i % 5) & 0xFF for i, b in enumerate(plain))).decode()
    files = {"Cfg": P + """
public class Cfg {
  static final String P = "%s";
  static final String D = "3";
  public String proof(String host) {
    byte[] raw = java.util.Base64.getDecoder().decode(P);
    int d = Integer.parseInt(D);
    byte[] out = new byte[raw.length];
    for (int i = 0; i < raw.length; i++) out[i] = (byte) (raw[i] - d - (i %% 5));
    String s = new String(out, java.nio.charset.StandardCharsets.UTF_8);
    StringBuilder sb = new StringBuilder("https://");
    sb.append(host).append("/evidence?proof=");
    for (int i = 0; i < s.length(); i++) sb.append(s.charAt(i));
    return sb.toString();
  }
}
""" % enc}
else:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
for name, body in files.items():
    (src / "com/huntress/mobile/d19/q4e").mkdir(parents=True, exist_ok=True)
    (src / f"com/huntress/mobile/d19/q4e/{name}.java").write_text(body)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "compute", "hint": "the app derives it"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
