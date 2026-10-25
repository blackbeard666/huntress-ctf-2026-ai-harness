"""Generate the fpx_* fixtures (coverage atlas row 96: float/double arithmetic in a computed-token chain, exact Java
semantics). usage: gen_fpx.py <variant: sensor_gate | battery_score | decoy_nan_gate> <out.apk>
SensorMap.mixSensorCode() folds accelerometer floats / battery-temperature doubles into a long through float+double
arithmetic (2addr and 3-reg forms, rem, neg), i2f/l2f/f2i/d2l saturation + NaN->0, cmpl/cmpg NaN bias, Math / StrictMath
/ Float / Double intrinsics, then prints "ANS-" + 16 hex. Oracle: the host JVM runs Probe (javac classes) and prints the
string; App classes only -> dex2jar d2j-jar2dex -> zipfile (manifest borrowed from skc_decoy_cbc_wrong_key.apk)."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d24.sensor"
HEX = """
  static String hex(long k) {
    StringBuilder sb = new StringBuilder();
    for (int i = 60; i >= 0; i -= 4) sb.append("0123456789abcdef".charAt((int) (k >>> i) & 15));
    return sb.toString();
  }"""
BODY = {
    "sensor_gate": """
  static final float[] ACC = {0.12f, 9.79f, -0.33f, 0.05f, 9.81f, -0.29f, 0.11f, 9.80665f, -0.31f, 0.07f, 9.78f, -0.35f};
  static float gain = 1.5f;
  static double tempRaw = 312.0;
  static long mixSensorAccel(float[] a) {
    float sx = 0, sy = 0, sz = 0;
    for (int i = 0; i + 2 < a.length; i += 3) { sx += a[i]; sy += a[i + 1]; sz += a[i + 2]; }
    float n = a.length / 3;
    float mx = sx / n, my = sy / n, mz = sz / n;
    double mag = Math.sqrt(mx * mx + my * my + mz * mz);
    float score = (float) (mag / 9.80665) * gain;
    float nan = (mz - mz) * Float.POSITIVE_INFINITY;
    long k = 0x9E3779B97F4A7C15L;
    k ^= Float.floatToIntBits(mx) & 0xFFFFFFFFL; k *= 0x100000001B3L;
    k ^= Double.doubleToLongBits(mag); k = Long.rotateLeft(k, 17);
    if (score > 0.5f) k += 0x1234567L; else k -= 0x7654321L;
    if (!(nan > 0.5f)) k ^= 0x55L;
    if (nan < 0.5f) k ^= 0xAA00L; else k ^= 0x3300L;
    if (nan >= 0.5) k ^= 0x110000L; else k ^= 0x770000L;
    if (nan <= 0.5) k ^= 0x2200000L; else k ^= 0x9900000L;
    k += (int) (mx * 1e12f);
    k += (long) nan + (int) (-sy * 1e30f) + (long) (sy * 1e30f);
    k ^= Math.round(mz * 1000f) * 0x10001L;
    k ^= Math.round(-2.5f) + Math.round(2.5) + Math.round(-0.5);
    double t = tempRaw / 10.0;
    k += (long) (Math.floor(t * 3.7) * 1000) + (long) Math.ceil(-t);
    k ^= (long) (Math.pow(score, 3) * 1e9);
    k = k * 31 + Float.compare(-0f * mx, 0f) + Float.compare(nan, Float.POSITIVE_INFINITY);
    k ^= (long) (mx % 0.03f * 1e9f) << 20;
    k ^= Double.doubleToLongBits(-(double) my);
    k += Float.floatToIntBits(-score) + Float.floatToIntBits(nan);
    return k;
  }
  public static String mixSensorCode() { return "ANS-" + hex(mixSensorAccel(ACC)); }""",
    "battery_score": """
  static final double[] TEMPS = {31.2, 33.75, 36.1, 29.9, 41.05};
  static long big = 0x1000001000000001L;
  static long mixSensorBattery(double[] tt) {
    double acc = 0;
    for (double v : tt) { acc += v; acc *= 1.0001; acc -= v / 7; }
    double avg = acc / tt.length;
    long k = Double.doubleToRawLongBits(avg);
    float f = (float) big;
    k ^= Float.floatToRawIntBits(f);
    k += (long) (float) (big + 0x7FFL) - (big + 0x7FFL);
    k ^= Float.floatToIntBits((float) 1e300) * 3L + Float.floatToIntBits((float) -1e-300);
    k ^= (long) (Float.parseFloat("1.00000017881393432617187499") * 1e9f);
    k += Float.floatToIntBits(Float.parseFloat(" 0.1f ")) + Double.doubleToLongBits(Double.parseDouble("2.5e-3"));
    k ^= Double.doubleToLongBits(Math.min(-0.0, 0.0 * avg)) ^ Double.doubleToLongBits(Math.max(-0.0 * avg, 0.0));
    k += Float.floatToIntBits(Float.intBitsToFloat(0x40490FDB) * 2f);
    k ^= Double.doubleToLongBits(StrictMath.abs(-avg)) >>> 3;
    k += Double.doubleToLongBits(Math.rint(2.5) + Math.rint(-3.5) + Math.ceil(-0.4) + Math.floor(-0.4));
    k ^= Double.doubleToLongBits(Math.pow(-avg, 3) % 97.0);
    String s = "t=" + (float) avg + "/" + avg + "/" + (1e7f * (float) avg) + "/" + (avg / 1e6);
    k = k * 1000003L + s.hashCode();
    double z = avg - avg;
    k += Double.doubleToLongBits(1.0 / z) ^ Double.doubleToLongBits(-1.0 / -z) ^ Double.doubleToLongBits(z % 0.0);
    float q = (float) avg;
    q %= 3.3f; q /= 0.7f; q -= 1.25f; q *= -q;
    k ^= Float.floatToIntBits(q);
    int i = (int) avg; i *= 12345;
    k += (float) i > 1e5f ? (long) ((float) i / 3f) : -1L;
    k += (long) (double) Long.MIN_VALUE + (long) Double.NaN + (int) Float.NEGATIVE_INFINITY;
    return k;
  }
  public static String mixSensorCode() { return "ANS-" + hex(mixSensorBattery(TEMPS)); }""",
    # decoy: the score is NaN (an empty sample window: 0/0) and `score > 0.5f` compiles to cmpl-float, so the token
    # branch is dead; the live branch emits a 15-hex near-miss. An evaluator with the wrong NaN bias reaches the token.
    "decoy_nan_gate": """
  static final float[] ACC = {};
  static long mixSensorAccel(float[] a) {
    float s = 0;
    for (float v : a) s += v;
    float score = s / a.length;
    long k = 0x7F4A7C159E3779B9L ^ Float.floatToRawIntBits(score);
    return score > 0.5f ? k : k >>> 4;
  }
  public static String mixSensorCode() {
    float s = 0;
    for (float v : ACC) s += v;
    float score = s / ACC.length;
    String h = hex(mixSensorAccel(ACC));
    return score > 0.5f ? "ANS-" + h : "ANS-" + h.substring(1);
  }""",
}
PROBE = """package %s;
public class Probe { public static void main(String[] a) { System.out.println(SensorMap.mixSensorCode()); } }""" % PKG

tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
pdir = tmp / "src" / PKG.replace(".", "/")
pdir.mkdir(parents=True)
(pdir / "SensorMap.java").write_text(f"package {PKG};\npublic class SensorMap {{{BODY[variant]}\n{HEX}\n}}\n")
(pdir / "Probe.java").write_text(PROBE)
cls = tmp / "cls"
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, pdir.glob("*.java"))], check=True)
shown = subprocess.run(["java", "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
(cls / PKG.replace(".", "/") / "Probe.class").unlink()
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(f"JVM mixSensorCode()={shown!r}")
