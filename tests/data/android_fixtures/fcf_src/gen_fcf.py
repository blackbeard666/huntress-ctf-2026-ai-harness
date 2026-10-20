#!/usr/bin/env python3
"""Generate the fcf_* fixtures (coverage atlas row 79: control-flow flattening, `while (true) { switch (state) }`).
usage: gen_fcf.py <variant: param_seed | sink_static | decoy_nearmiss> <out.apk>
  param_seed:     static String F.build(int seed) -- sparse-switch state machine appending chars / strings to a
                  StringBuilder, state updated by xor arithmetic, one case burns a 16000-iteration junk loop (> 50k
                  Dalvik steps); the seed only comes from the call site show(): out.println(build(0x2a)).
  sink_static:    void G.show(PrintStream out) -- packed-switch dispatcher whose cases print the token pieces straight
                  to `out` (String / char) behind an opaque predicate on out.hashCode(): only static unflattening
                  (case order from the initial state) recovers the text.
  decoy_nearmiss: param_seed layout, token one hex digit short.
Writes Java sources, compiles with javac --release 8, converts with dex2jar's d2j-jar2dex, zips classes.dex + the
manifest of a stock fixture with zipfile. The oracle (oracle.sh) runs the SAME dex (dex2jar'd back) on the JVM."""
import os, random, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
P = "package com.huntress.mobile.d20.fcf;\n"
rng = random.Random(variant)


def jstr(s):
    return "".join(c if 0x20 <= ord(c) < 0x7F and c not in '"\\' else "\\u%04x" % ord(c) for c in s)


def chunks(tok):
    out, i = [], 0
    while i < len(tok):
        n = rng.choice((1, 1, 2, 3))
        out.append(tok[i:i + n])
        i += n
    return out


if variant in ("param_seed", "decoy_nearmiss"):
    tok = "ANS-7c3e91f0a2d845b6" if variant == "param_seed" else "ANS-7c3e91f0a2d845b"
    parts = chunks(tok)
    keys = rng.sample(range(100, 4000), len(parts) + 2)  # +junk-loop state, +final state
    seq = keys[:len(parts)]
    junk_at = len(parts) // 2
    seq.insert(junk_at, keys[len(parts)])
    final = keys[len(parts) + 1]
    order = seq + [final]
    k = 0x5A
    cases, pi = [], 0
    for i, st in enumerate(order[:-1]):
        nxt = order[i + 1]
        if i == junk_at:
            body = "for (int i = 0; i < 16000; i++) acc = acc * 31 + i; state = (state ^ %d) + (acc & 0);" % (st ^ nxt)
        else:
            p = parts[pi]
            pi += 1
            app = "sb.append('%s');" % jstr(p) if len(p) == 1 else 'sb.append("%s");' % jstr(p)
            body = app + " state = state ^ %d;" % (st ^ nxt)
        cases.append("        case %d: %s break;" % (st, body))
    rng.shuffle(cases)
    cases.append("        case %d: return sb.toString();" % final)
    files = {"F": P + """
public final class F {
  static String build(int seed) {
    StringBuilder sb = new StringBuilder();
    int state = seed ^ %d, acc = 0;
    while (true) {
      switch (state) {
%s
        default: return "nope";
      }
    }
  }
  public void show(java.io.PrintStream out) {
    out.println(build(%d));
  }
}
""" % (k, "\n".join(cases), order[0] ^ k)}
elif variant == "sink_static":
    tok = "flag ANS-e05b9d1c74a3f826 ok"
    parts = chunks(tok)
    n = len(parts)
    perm = list(range(n + 1))
    rng.shuffle(perm)  # perm[i] = case key of step i; the last key exits
    cases = []
    for i, p in enumerate(parts):
        pr = "out.print('%s');" % jstr(p) if len(p) == 1 else 'out.print("%s");' % jstr(p)
        cases.append("        case %d: %s if (out.hashCode() == 0x1337) junk += 3; s = %d; break;"
                     % (perm[i], pr, perm[i + 1]))
    cases.append("        case %d: out.println(); return;" % perm[n])
    cases.sort(key=lambda c: int(c.split()[1].rstrip(":")))
    files = {"G": P + """
public final class G {
  public void show(java.io.PrintStream out) {
    int s = %d, junk = 0;
    while (true) {
      switch (s) {
%s
        default: return;
      }
    }
  }
}
""" % (perm[0], "\n".join(cases))}
else:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
for name, body in files.items():
    (src / "com/huntress/mobile/d20/fcf").mkdir(parents=True, exist_ok=True)
    (src / f"com/huntress/mobile/d20/fcf/{name}.java").write_text(body)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "flattened", "hint": "follow the state machine"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
