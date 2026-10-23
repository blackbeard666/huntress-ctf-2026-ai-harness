#!/usr/bin/env python3
"""Generate the eav_* fixtures (entry-anchored candidate veto, coverage atlas row 98).
usage: gen_eav.py <variant: live_mixer | runtime_decoy> <out.apk> [--oracle]
D23 v2 shape: ChallengeActivity -> Release.code(Context) = "ANS-" + "0123456789ABCDEF".charAt(x >>> i & 15) over a 64-bit
mixer chain; beside it unreferenced look-alike mixers (sealTrampolineNN / sealHookNN / K* longs) and a dead
Ghost.code() (same builder, other seed) whose only caller Ghost.relay() is itself dead. runtime_decoy: the same builder
fed by System.currentTimeMillis() (no static token) and no Ghost. javac --release 8 (app + android.* compile stubs) ->
dex2jar d2j-jar2dex (app classes only) -> zipfile. --oracle: run Release.code(null) / Ghost.code() on the host JVM."""
import subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
ROOT = Path(__file__).resolve().parents[4]
PKG = "com.huntress.mobile.d23.veto"
seed = "new java.util.Random().nextLong()" if variant == "runtime_decoy" else "-6466867484639169990L"
APP = {
    "ChallengeActivity.java": """package %(p)s;
public class ChallengeActivity extends android.app.Activity {
  protected void onCreate(android.os.Bundle b) { super.onCreate(b); android.util.Log.i("ev", Release.code(this)); } }""",
    "Release.java": """package %(p)s;
public final class Release {
  static long KSeal = 2211886173333885659L;
  public static long token() { return Util.mixA(Util.mixB(%(seed)s)); }
  public static String code(android.content.Context c) {
    long v = Util.fin(token()) ^ -7148765225602638926L;
    StringBuilder sb = new StringBuilder(); sb.append("ANS-");
    int i = 60; do { sb.append("0123456789ABCDEF".charAt(((int) (v >>> i)) & 15)); i -= 4; } while (i >= 0);
    return sb.toString(); } }""",
    "Util.java": """package %(p)s;
public final class Util {
  static final long KPatchea = -7001372155309101779L;
  static long mixA(long j) { long a = (j ^ 5006709854372244345L) * 1958157885234814829L; a = (a << 30) | (a >>> 34);
    return (a ^ (a >>> 20)) - 7619862862749198346L; }
  static long mixB(long j) { long a = j ^ (j >>> 28); a = ((a ^ (a >>> 30)) + 2183413890471151166L) * -1402156385267666889L;
    return (a << 41) | (a >>> 23); }
  static long fin(long j) { long a = (j ^ (j >>> 10)) * -4565261069424997581L; return ((a << 23) | (a >>> 41)) + 4847595846291780659L; }
  static long sealHook30(long j) { long a = (j ^ -6346643076729912359L) * -301087911024711665L; return ((a << 55) | (a >>> 9)) * 2575955574811816977L; } }""",
    "TrampolineMap.java": """package %(p)s;
public final class TrampolineMap {
  static final long KHook59 = 4319040364164822500L;
  static long sealTrampolinec7(long j) { long a = (j ^ 4319040364164822500L) * 3279936631865730991L;
    return ((a << 38) | (a >>> 26)) * 2549406440646763139L; } }""",
}
if variant != "runtime_decoy":
    APP["Ghost.java"] = """package %(p)s;
public final class Ghost {
  public static String code() {
    long v = TrampolineMap.sealTrampolinec7(Util.sealHook30(8403552673466330925L));
    StringBuilder sb = new StringBuilder(); sb.append("ANS-");
    int i = 60; do { sb.append("0123456789ABCDEF".charAt(((int) (v >>> i)) & 15)); i -= 4; } while (i >= 0);
    return sb.toString(); }
  static String relay() { return Ghost.code(); } }"""
STUBS = {
    "android/app/Activity.java": "package android.app;\npublic class Activity extends android.content.Context {\n"
                                 "  protected void onCreate(android.os.Bundle b) { } }",
    "android/content/Context.java": "package android.content;\npublic class Context { }",
    "android/os/Bundle.java": "package android.os;\npublic class Bundle { }",
    "android/util/Log.java": "package android.util;\npublic class Log { public static int i(String t, String m) "
                             "{ System.out.println(m); return 0; } }",
}
ORACLE = """package %(p)s;
public class Oracle { public static void main(String[] a) { System.out.println("live=" + Release.code(null));
  try { System.out.println("ghost=" + Class.forName("%(p)s.Ghost").getMethod("code").invoke(null)); }
  catch (Exception e) { System.out.println("ghost=-"); } } }"""

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    src, cls = tmp / "src", tmp / "cls"
    pdir = src / PKG.replace(".", "/")
    pdir.mkdir(parents=True)
    for n, body in APP.items():
        (pdir / n).write_text(body % {"p": PKG, "seed": seed})
    if "--oracle" in sys.argv:
        (pdir / "Oracle.java").write_text(ORACLE % {"p": PKG})
    for n, body in STUBS.items():
        (src / n).parent.mkdir(parents=True, exist_ok=True)
        (src / n).write_text(body)
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    if "--oracle" in sys.argv:
        subprocess.run(["java", "-cp", str(cls), PKG + ".Oracle"], check=True)
        sys.exit(0)
    with zipfile.ZipFile(tmp / "app.zip", "w") as z:
        for f in cls.rglob("*.class"):
            if not f.relative_to(cls).as_posix().startswith("android/"):
                z.write(f, f.relative_to(cls).as_posix())
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"),
                    str(tmp / "app.zip")], check=True, capture_output=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(tmp / "classes.dex", "classes.dex")
print(out)
