#!/usr/bin/env python3
"""Generate the swm_* fixtures (enum state machines compiled through javac's `$SwitchMap$` synthetic class; coverage
atlas row 89). usage: gen_swm.py <variant: enum_loop | enum_fields | decoy_nearmiss> <out.apk>
`switch (phase)` on an enum compiles to `Gate$1.$SwitchMap$<pkg>$Phase[phase.ordinal()]` -> packed-switch on the
case numbers 1..n (in switch order, NOT the declaration order), so the evaluator must run Phase.<clinit>
(new-instance + Enum.<init>(name, ordinal) + $VALUES), Gate$1.<clinit> (values().length, ordinal(), aput under a
NoSuchFieldError catch) and resolve the aget before the switch. Every transition folds into a key; the terminal state
xors ENC with it. Stage 1: the host JVM prints the key; stage 2 recompiles with ENC and the JVM prints the terminal
output (the oracle). App classes only -> dex2jar d2j-jar2dex -> zipfile."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"enum_loop": "ANS-4be81c07d93fa265", "enum_fields": "ANS-0d6e93a1f2c754b8",
          "decoy_nearmiss": "ANS-9c3e71b0a5d248"}  # decoy: the terminal state emits a 14-hex near-miss
PKG = "com.huntress.mobile.d22.swm"
pdir = PKG.replace(".", "/")
SRC = {
    "enum_loop": {
        "Phase.java": """package %(pkg)s;
public enum Phase { TRAP, EMIT, MIX, BOOT, CHECK, DONE }""",
        "Gate.java": """package %(pkg)s;
public final class Gate {
  static final byte[] ENC = {%(enc)s};
  static Phase phase = Phase.BOOT;
  static long key = 0x2B7E1516L;
  public static String run() {
    String outv = null;
    int guard = 0;
    while (outv == null && guard++ < 64) {
      switch (phase) {
        case BOOT:  key = key * 31 + phase.ordinal(); phase = Phase.CHECK; break;
        case CHECK: key ^= 0x5A5A1234L; phase = Phase.MIX; break;
        case MIX:   key = key * 17 + 0x1F; phase = (key & 1) == 0 ? Phase.EMIT : Phase.EMIT; break;
        case TRAP:  outv = "trap"; break;
        case EMIT: {
          char[] c = new char[ENC.length];
          for (int i = 0; i < c.length; i++) c[i] = (char) ((ENC[i] ^ (key >>> ((i %% 8) * 8))) & 0xFF);
          outv = "proof=" + new String(c); phase = Phase.DONE; break;
        }
        default: outv = "none";
      }
    }
    return outv;
  }
  public static long probeKey() {
    while (true) {
      switch (phase) {
        case BOOT:  key = key * 31 + phase.ordinal(); phase = Phase.CHECK; break;
        case CHECK: key ^= 0x5A5A1234L; phase = Phase.MIX; break;
        case MIX:   key = key * 17 + 0x1F; phase = Phase.EMIT; break;
        default: return key;
      }
    }
  }
}""",
    },
    "enum_fields": {
        "Op.java": """package %(pkg)s;
public enum Op {
  HALT(0), ROTL(7), XOR(0x3C), ADD(0x55), MUL(13);
  final int k;
  Op(int k) { this.k = k; }
}""",
        "Mode.java": """package %(pkg)s;
public enum Mode { SLOW, FAST, OFF }""",
        "Gate.java": """package %(pkg)s;
public final class Gate {
  static final byte[] ENC = {%(enc)s};
  static final Op[] PROG = {Op.XOR, Op.MUL, Op.ROTL, Op.ADD, Op.XOR, Op.HALT};
  static Mode mode = Mode.FAST;
  static int acc;
  static void step(Op op) {
    switch (op) {
      case ADD:  acc += op.k + op.ordinal(); break;
      case XOR:  acc ^= op.k << 8; break;
      case MUL:  acc *= op.k; break;
      case ROTL: acc = (acc << op.k) | (acc >>> (32 - op.k)); break;
      case HALT: break;
    }
  }
  static int fold() {
    acc = 0x13579BDF;
    for (int i = 0; i < PROG.length; i++) step(PROG[i]);
    switch (mode) {
      case OFF:  return 0;
      case FAST: return acc ^ 0x0BADF00D;
      case SLOW: return acc;
    }
    return -1;
  }
  public static String proof() {
    int k = fold();
    char[] c = new char[ENC.length];
    for (int i = 0; i < c.length; i++) c[i] = (char) ((ENC[i] ^ (k >>> ((i %% 4) * 8)) ^ i) & 0xFF);
    return "proof=" + new String(c);
  }
  public static long probeKey() { return fold() & 0xFFFFFFFFL; }
}""",
    },
}
SRC["decoy_nearmiss"] = SRC["enum_loop"]
PROBE = """package %(pkg)s;
public final class Probe { public static void main(String[] a) { %(body)s } }"""


def build(enc, body):
    tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
    src, cls = tmp / "src", tmp / "cls"
    files = {f"{pdir}/{k}": v % {"pkg": PKG, "enc": ", ".join(map(str, enc))} for k, v in SRC[variant].items()}
    files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG, "body": body}
    for rel, b in files.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_text(b)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    run = subprocess.run(["java", "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
    return tmp, cls, run


tmp, _, k = build([], "System.out.println(Gate.probeKey());")
shutil.rmtree(tmp)
k = int(k.splitlines()[-1])
plain = TOKENS[variant].encode()
if variant == "enum_fields":
    enc = [((p ^ (k >> ((i % 4) * 8)) ^ i) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(plain)]
    show = "System.out.println(Gate.proof());"
else:
    enc = [((p ^ ((k & 0xFFFFFFFFFFFFFFFF) >> ((i % 8) * 8))) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(plain)]
    show = "System.out.println(Gate.run());"
tmp, cls, shown = build(enc, show)  # oracle: the host JVM's own enum switch output
os.unlink(cls / pdir / "Probe.class")
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(f"key={k} JVM terminal={shown!r}")
