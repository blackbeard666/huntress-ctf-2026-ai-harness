#!/usr/bin/env python3
"""Generate the sigobj_* fixtures (coverage atlas rows 94/96: puzzle v2 `codec: analysis` where the "multiple signals"
are OBJECTS -- interface / abstract `Check` implementations collected in Arrays.asList / ArrayList / HashMap /
LinkedHashMap and iterated, virtual + interface dispatch (inherited, overridden and default methods), iget/iput of
int / long / boolean / object fields, StringBuilder.reverse/insert/setCharAt, String.format("%02x"), Integer.valueOf).
usage: gen_sigobj.py <variant: list_iface | map_order | decoy_runtime> <out.apk>
Writes Java sources, compiles with javac --release 8 (a stub android.content.Context is compiled but NOT dexed),
converts with dex2jar's d2j-jar2dex, zips classes.dex + a stock manifest + assets/huntress_puzzle.json with zipfile.
The oracle (oracle_sigobj.sh) runs the SAME dex (d2j-dex2jar back to classes) on the JVM."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
P = "package com.huntress.mobile.d25.sig;\nimport java.util.*;\n"
COMMON = {
    "Check.java": """
public interface Check {
  int weight();
  long read();
  default long mix(long x) { return Long.rotateLeft(x * 0x9E3779B97F4A7C15L, weight() & 31) ^ read(); }
  default String tag() { return getClass().getSimpleName(); }
}
""",
    "Signal.java": """
public abstract class Signal implements Check {
  protected final int w;
  protected long salt;
  protected boolean clean;
  protected String label;
  protected Signal(int w, long salt, String label) { this.w = w; this.salt = salt; this.label = label; this.clean = true; }
  public int weight() { return w; }
  public long read() { return clean ? salt ^ label.hashCode() : 0L; }
}
""",
    "BoardCheck.java": """
public class BoardCheck extends Signal {
  public BoardCheck() { super(3, 0x51A7C0DE1234L, "ro.product.board"); }
  @Override public long read() { return super.read() * 7 + w; }
}
""",
    "SensorMap.java": """
public class SensorMap extends Signal {
  private final int[] axes = {9, 81, 27};
  public SensorMap() { super(5, 0x0BADC0FFEE77L, "sensor.map"); }
  @Override public long read() { long s = 0; for (int a : axes) s = s * 131 + a; return s ^ salt; }
}
""",
    "GyroMap.java": """
public final class GyroMap extends SensorMap {
  public GyroMap() { super(); salt = 0x7F00FF00AA55L; }
  @Override public int weight() { return super.weight() + 6; }
}
""",
    "PathProbe.java": """
public class PathProbe implements Check {
  private final String path;
  private boolean seen;
  public PathProbe(String path) { this.path = path; }
  public int weight() { return path.length(); }
  public long read() { seen = !seen; return seen ? (long) path.hashCode() << 17 : -1L; }
  @Override public long mix(long x) { return x + read() * 31; }
}
""",
}
SRC = {
    "list_iface": """
public final class Release {
  public static String code(android.content.Context ctx) {
    List<Check> checks = Arrays.asList(new BoardCheck(), new SensorMap(), new GyroMap(), new PathProbe("/sys/fs/selinux"));
    long score = 0x2545F4914F6CDD1DL;
    for (Check c : checks) {
      score += c.weight() * c.read();
      score = c.mix(score);
    }
    ArrayList<Check> more = new ArrayList<>();
    more.add(new PathProbe("/proc/self/maps"));
    more.add(0, new BoardCheck());
    Iterator<Check> it = more.iterator();
    while (it.hasNext()) { Check c = it.next(); score ^= c.mix(score >>> 7) + c.tag().length(); }
    return "ANS-" + String.format("%016X", score);
  }
}
""",
    "map_order": """
public final class Release {
  public static String code(android.content.Context ctx) {
    HashMap<String, Check> map = new HashMap<>();
    map.put("zeta", new PathProbe("/system/xbin/su"));
    map.put("board", new BoardCheck());
    map.put("gyro", new GyroMap());
    map.put("alpha", new SensorMap());
    map.put("mid", new PathProbe("/data/local/tmp"));
    LinkedHashMap<String, Integer> order = new LinkedHashMap<>();
    long acc = 0xC0FFEE1234567L;
    Iterator<Map.Entry<String, Check>> ei = map.entrySet().iterator();  // bounded loops: jadx keeps the casts
    int n = 0;
    while (ei.hasNext() && n++ < 64) {
      Map.Entry<String, Check> e = (Map.Entry<String, Check>) ei.next();
      Check c = (Check) e.getValue();
      acc = Long.rotateLeft(acc, 9) ^ (e.getKey().hashCode() * 0x100000001B3L) ^ c.mix(acc);
      order.put(e.getKey(), Integer.valueOf(c.weight()));
    }
    int k = 1;
    Iterator<String> ki = order.keySet().iterator();
    while (ki.hasNext() && k != 0x7FFFFFFF) { String key = (String) ki.next(); Integer v = (Integer) order.get(key); k = k * 37 + v.intValue() + key.charAt(0); }
    acc ^= ((long) k << 32) | (k & 0xFFFFFFFFL);
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < 8; i++) sb.append(String.format("%02x", (int) (acc >>> (8 * i)) & 0xFF));
    sb.reverse();
    sb.setCharAt(0, Character.toUpperCase(sb.charAt(0)));
    sb.insert(0, "ANS-");
    String s = sb.toString();
    return s.substring(0, 4) + s.substring(4).toLowerCase();
  }
}
""",
    # DECOY: list_iface's chain, but one signal is the wall clock -> no deterministic token exists
    "decoy_runtime": """
public final class Release {
  public static String code(android.content.Context ctx) {
    List<Check> checks = Arrays.asList(new BoardCheck(), new SensorMap(), new PathProbe("/sys/fs/selinux"));
    long score = System.nanoTime();
    for (Check c : checks) { score += c.weight() * c.read(); score = c.mix(score); }
    return "ANS-" + String.format("%016X", score);
  }
}
""",
}
if variant not in SRC:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
pk = src / "com/huntress/mobile/d25/sig"
pk.mkdir(parents=True)
(src / "android/content").mkdir(parents=True)
(src / "android/content/Context.java").write_text("package android.content;\npublic abstract class Context {}\n")
for n, body in {**COMMON, "Release.java": SRC[variant]}.items():
    (pk / n).write_text(P + body)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.rmtree(cls / "android")  # framework stub: not part of the app dex
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json",
               '{"schema": "huntress.puzzle.v2", "codec": "analysis", "build": "sig-objects", '
               '"hint": "every signal object contributes"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
