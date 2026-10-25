#!/usr/bin/env python3
"""Generate the dxr_* fixtures (coverage atlas row 96: dex-eval-java-random-lcg -- an answer COMPUTED from a seeded
java.util.Random / SplittableRandom / Collections.shuffle / UUID.nameUUIDFromBytes inside the app's dex).
usage: gen_dxr.py <variant: random_mix | splittable_uuid | decoy_unseeded> <out.zip>
Writes Java sources, compiles with javac --release 8, converts with dex2jar's d2j-jar2dex, zips classes.dex + the
manifest of a stock fixture into an APK with zipfile, and wraps that APK in a one-set deep_eval_bench bundle (.zip).
The oracle (oracle.sh) runs the SAME compiled classes on the JVM (the real java.util implementations)."""
import io, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
P = "package com.huntress.mobile.d26.rnd;\n"

RANDOM_MIX = P + """
import java.util.*;
public final class Rng {
  static final long SEED = 0x2026102AL;
  public static String code() {
    Random r = new Random(SEED);
    byte[] b = new byte[7];
    r.nextBytes(b);
    long acc = r.nextLong();
    acc ^= ((long) r.nextInt()) << 16;
    acc += r.nextInt(1000) * 7919L;          // rejection-loop bound
    acc ^= r.nextInt(64);                    // power-of-two bound
    acc += r.nextInt(0x7FFFFFF1);            // non-power-of-two bound near 2^31
    if (r.nextBoolean()) acc = Long.rotateLeft(acc, 13);
    acc += (long) (r.nextDouble() * 1e9);
    for (byte x : b) acc = acc * 31 + (x & 0xff);
    Integer[] deck = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    List<Integer> l = Arrays.asList(deck);
    Collections.shuffle(l, r);
    for (int i = 0; i < l.size(); i++) acc = acc * 11 + l.get(i);
    r.setSeed(acc);
    acc ^= r.nextLong();
    return "ANS-" + String.format("%016X", acc);
  }
}
"""
SPLIT_UUID = P + """
import java.util.*;
public final class Rng {
  public static String code() {
    SplittableRandom s = new SplittableRandom(0xC0FFEE1234L);
    long acc = s.nextLong();
    acc ^= s.nextInt();
    acc += s.nextInt(37);
    acc += s.nextInt(1 << 20);
    if (s.nextBoolean()) acc = ~acc;
    UUID u = UUID.nameUUIDFromBytes(("huntress-" + Long.toHexString(acc)).getBytes());
    acc ^= u.getMostSignificantBits() ^ Long.rotateLeft(u.getLeastSignificantBits(), 5);
    ArrayList<Integer> l = new ArrayList<>();
    for (int i = 0; i < 12; i++) l.add(i * 3);
    Collections.shuffle(l, new Random(acc));
    for (int i = 0; i < l.size(); i++) acc = acc * 13 + l.get(i);
    return "ANS-" + String.format("%016x", acc);
  }
}
"""
if variant == "random_mix":
    src = RANDOM_MIX
elif variant == "splittable_uuid":
    src = SPLIT_UUID
elif variant == "decoy_unseeded":  # same mixer, but the Random is unseeded: no deterministic answer exists
    src = RANDOM_MIX.replace("new Random(SEED)", "new Random()")
else:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
sd, cls = tmp / "src/com/huntress/mobile/d26/rnd", tmp / "cls"
sd.mkdir(parents=True)
(sd / "Rng.java").write_text(src)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), str(sd / "Rng.java")], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
apk = io.BytesIO()
with zipfile.ZipFile(apk, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "compute", "hint": "the app derives it"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as z:
    z.writestr("set01.apk", apk.getvalue())
shutil.rmtree(tmp)
print(out)
