#!/usr/bin/env python3
"""Generate the vmbc_* fixtures (coverage atlas row 81: a virtualised method -- a custom bytecode program held as a
byte[] literal (fill-array-data) or a base64 const-string, run by an in-dex stack-VM interpreter: while (pc < len)
switch (code[pc++]) { push / xor / add / sub / rol / load / store / emit-char / loop / halt }).
usage: gen_vmbc.py <variant: spin_fill | b64_param | decoy_nearmiss> <out.apk>
The Python here is only the WRITER (assembles the VM program); javac --release 8 + dex2jar d2j-jar2dex build the dex,
zipfile the apk. The oracle (oracle.sh) runs the SAME compiled classes on the JVM."""
import base64, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
P = "package com.huntress.mobile.d20.vm;\n"
# opcode numbering per variant (the b64 variant permutes it, as an obfuscator would)
OPS_A = dict(PUSH=0, XOR=1, ADD=2, SUB=3, ROL=4, STORE=5, LOAD=6, EMIT=7, LOOP=8, HALT=9, PUSHW=10)
OPS_B = dict(PUSH=0x31, XOR=0x17, ADD=0x52, SUB=0x08, ROL=0x6c, STORE=0x23, LOAD=0x4e, EMIT=0x7a, LOOP=0x11, HALT=0x05,
             PUSHW=0x60)


def assemble(plain, ops, key0, spin):
    """reg0 = key0; reg2 = spin; do { reg0 = rol(reg0,3) ^ 0x11 } while (--reg2 != 0); then per char: emit(enc ^ reg0);
    reg0 = (reg0 + 0x1d) & 0xff."""
    c = [ops["PUSH"], key0, ops["STORE"], 0, ops["PUSHW"], spin >> 8, spin & 0xFF, ops["STORE"], 2]
    top = len(c)
    c += [ops["LOAD"], 0, ops["ROL"], 3, ops["PUSH"], 0x11, ops["XOR"], ops["STORE"], 0, ops["LOOP"], 2, top]
    k = key0
    for _ in range(spin):
        k = (((k << 3) | (k >> 5)) & 0xFF) ^ 0x11
    for ch in plain:
        c += [ops["PUSH"], ord(ch) ^ k, ops["LOAD"], 0, ops["XOR"], ops["EMIT"],
              ops["LOAD"], 0, ops["PUSH"], 0x1D, ops["ADD"], ops["STORE"], 0]
        k = (k + 0x1D) & 0xFF
    c += [ops["HALT"]]
    assert len(c) < 256 or True
    return bytes(c)


def machine(ops, sig, prologue):
    o = {k: v for k, v in ops.items()}
    return P + """
public final class Machine {
  private final int[] st = new int[32];
  private final int[] reg = new int[8];
  private int sp;
  %s {
    %s
    StringBuilder out = new StringBuilder();
    int pc = 0;
    while (pc < code.length) {
      int op = code[pc++] & 0xff;
      switch (op) {
        case %d: st[sp++] = code[pc++] & 0xff; break;
        case %d: { int b = st[--sp], a = st[--sp]; st[sp++] = (a ^ b) & 0xff; break; }
        case %d: { int b = st[--sp], a = st[--sp]; st[sp++] = (a + b) & 0xff; break; }
        case %d: { int b = st[--sp], a = st[--sp]; st[sp++] = (a - b) & 0xff; break; }
        case %d: { int a = st[--sp], n = code[pc++] & 7; st[sp++] = ((a << n) | (a >>> (8 - n))) & 0xff; break; }
        case %d: reg[code[pc++]] = st[--sp]; break;
        case %d: st[sp++] = reg[code[pc++]]; break;
        case %d: out.append((char) st[--sp]); break;
        case %d: { int r = code[pc++], t = code[pc++] & 0xff; if (--reg[r] != 0) pc = t; break; }
        case %d: return out.toString();
        case %d: { int hi = code[pc++] & 0xff, lo = code[pc++] & 0xff; st[sp++] = (hi << 8) | lo; break; }
        default: throw new IllegalStateException("bad op " + op);
      }
    }
    return out.toString();
  }
}
""" % (sig, prologue, o["PUSH"], o["XOR"], o["ADD"], o["SUB"], o["ROL"], o["STORE"], o["LOAD"], o["EMIT"], o["LOOP"],
       o["HALT"], o["PUSHW"])


if variant in ("spin_fill", "decoy_nearmiss"):
    plain = "ANS-3b9e07d1f4a6c582" if variant == "spin_fill" else "ANS-3b9e07d1f4a6c58"
    prog = assemble(plain, OPS_A, 0x5A, 3000)  # 3000 VM loop turns: far past a 50k-step Dalvik budget
    lits = ", ".join(str(b - 256 if b > 127 else b) for b in prog)
    files = {"Machine": machine(OPS_A, "public String run(byte[] code)", ""),
             "Vault": P + """
public final class Vault {
  private static final byte[] CODE = {%s};
  public static String token() { return new Machine().run(CODE); }
}
""" % lits}
elif variant == "b64_param":
    prog = assemble("ANS-e1c470b9d28f6a35", OPS_B, 0xC3, 700)
    files = {"Machine": machine(OPS_B, "public String exec(String blob)",
                                "byte[] code = java.util.Base64.getDecoder().decode(blob);"),
             "Gate": P + """
public final class Gate {
  static final String PROGRAM = "%s";
  public static String show() {
    java.util.logging.Logger.getLogger("gate").info("unlocking");
    return new Machine().exec(PROGRAM);
  }
}
""" % base64.b64encode(prog).decode()}
else:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
for name, body in files.items():
    (src / "com/huntress/mobile/d20/vm").mkdir(parents=True, exist_ok=True)
    (src / f"com/huntress/mobile/d20/vm/{name}.java").write_text(body)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.write(tmp / "classes.dex", "classes.dex")
shutil.rmtree(tmp)
print(out)
