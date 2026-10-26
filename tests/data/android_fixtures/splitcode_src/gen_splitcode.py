#!/usr/bin/env python3
"""Generate the splitcode_* fixtures (coverage atlas rows 42, 101, 103: split-feature-dex-code). A `.apks` bundle
(stored zip of base.apk + split_arena_feature.apk; the split manifest is `split="arena_feature"` isFeatureSplit with
hasCode=true and its OWN classes.dex). The base puzzle is v2 `codec: analysis`; Release.code(Context) calls
SplitCompat.install(ctx), checks SplitInstallManagerFactory.create(ctx).getInstalledModules().contains("arena_feature"),
then continues the token chain inside the split's code. The split also ships a duplicate `Util` (same descriptor,
different body): the base copy wins (parent-first / shared loader).
  shared      base manifest without isolatedSplits: a plain static invoke FeatureMix.mix(h) into the split dex (one
              shared PathClassLoader) + ctx.getClassLoader().loadClass("..Tail").getDeclaredMethod("tail", long, int)
              .invoke(null, h, 7).
  isolated    base manifest isolatedSplits="true": ClassLoader cl = ctx.createContextForSplit("arena_feature")
              .getClassLoader(); Class.forName("..FeatureMix", true, cl).getDeclaredMethod("mix", long).invoke(null, h)
              + cl.loadClass("..Tail")...; the split code calls back into the base Util (parent = base loader).
  decoy_cnf   isolated layout but the base asks for "..FeatureMixer" (absent) -> ClassNotFoundException, no token.
usage: gen_splitcode.py <variant> <out.apks>
Build: javac --release 8 (base app + feature classes + android.* / Play Core stubs; the split's duplicate Util
compiled on its own) -> dex2jar d2j-jar2dex (one dex per APK); manifests by apktool's aapt2 link -I android-framework.jar;
python zipfile adds classes.dex; `zip -0 -j -X` makes the bundle.
ORACLE (independent of lib.android): unzip the bundle, `aapt2 dump xmltree` reads split names + isolatedSplits, each
member's classes.dex goes BACK through dex2jar d2j-dex2jar into a jar, and the host JVM runs Release.code() with the
base jar on the classpath and the split jar either on the same classpath AFTER the base (shared loader: base wins) or
behind a URLClassLoader whose parent is the base loader (isolatedSplits)."""
import random, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
ROOT = Path(__file__).resolve().parents[4]
PKG = {"shared": "com.huntress.arena.splitcode1", "isolated": "com.huntress.arena.splitcode2",
       "decoy_cnf": "com.huntress.arena.splitcode3"}[variant]
ISO = variant != "shared"
rnd = random.Random("splitcode-" + variant)
STUBS = {
    "android/content/pm/PackageManager.java": """package android.content.pm;
public class PackageManager { public static class NameNotFoundException extends Exception { } }""",
    "android/content/Context.java": """package android.content;
public class Context { final String own;
  public Context() { this(null); } Context(String s) { own = s; }
  static java.util.List<String> names() { String v = System.getProperty("ctx.names", ""); return java.util.Arrays.asList(v.isEmpty() ? new String[0] : v.split(",")); }
  public Context createContextForSplit(String n) throws android.content.pm.PackageManager.NameNotFoundException {
    if (names().contains(n)) return new Context(n); throw new android.content.pm.PackageManager.NameNotFoundException(); }
  public ClassLoader getClassLoader() {
    ClassLoader base = Context.class.getClassLoader();
    if (own == null || !Boolean.getBoolean("ctx.iso")) return base;
    try { return new java.net.URLClassLoader(new java.net.URL[] { new java.io.File(System.getProperty("ctx.jar." + own)).toURI().toURL() }, base); }
    catch (java.io.IOException e) { throw new RuntimeException(e); } } }""",
    "com/google/android/play/core/splitcompat/SplitCompat.java": """package com.google.android.play.core.splitcompat;
public class SplitCompat { public static boolean install(android.content.Context c) { return true; } }""",
    "com/google/android/play/core/splitinstall/SplitInstallManager.java": """package com.google.android.play.core.splitinstall;
public interface SplitInstallManager { java.util.Set<String> getInstalledModules(); }""",
    "com/google/android/play/core/splitinstall/SplitInstallManagerFactory.java": """package com.google.android.play.core.splitinstall;
public class SplitInstallManagerFactory { public static SplitInstallManager create(android.content.Context c) {
  return new SplitInstallManager() { public java.util.Set<String> getInstalledModules() {
    String v = System.getProperty("ctx.names", "");
    return new java.util.HashSet<String>(java.util.Arrays.asList(v.isEmpty() ? new String[0] : v.split(","))); } }; } }""",
}
SEED, K1, K2 = rnd.getrandbits(63), rnd.getrandbits(62), rnd.getrandbits(31)
BASE = {
    "Util.java": """package %(pkg)s;
public final class Util {
    public static long fold(long h, long v) { h ^= v; h *= 0x100000001b3L; return h ^ (h >>> 29); }
}
""",
    "Release.java": """package %(pkg)s;
import android.content.Context;
import java.lang.reflect.Method;
import java.util.Set;
import com.google.android.play.core.splitcompat.SplitCompat;
import com.google.android.play.core.splitinstall.SplitInstallManagerFactory;
public final class Release {
    static final long SEED = %(seed)dL;
    static String hex(long v) {
        char[] H = "0123456789ABCDEF".toCharArray();
        StringBuilder sb = new StringBuilder();
        for (int i = 60; i >= 0; i -= 4) sb.append(H[(int) ((v >>> i) & 15)]);
        return sb.toString();
    }
    public static String code(Context ctx) throws Exception {
        if (!SplitCompat.install(ctx)) throw new IllegalStateException("splitcompat");
        Set<String> mods = SplitInstallManagerFactory.create(ctx).getInstalledModules();
        if (!mods.contains("arena_feature")) throw new IllegalStateException("feature not installed");
        long h = Util.fold(SEED, 0x5157L);
%(body)s
        return "ANS-" + hex(h);
    }
}
""",
    "Probe.java": "package %(pkg)s;\npublic class Probe { public static void main(String[] a) throws Exception {"
                  " System.out.println(Release.code(new android.content.Context())); } }\n",
}
BODY = {
    "shared": """        h = %(pkg)s.feature.FeatureMix.mix(h);
        Class<?> t = ctx.getClassLoader().loadClass("%(pkg)s.feature.Tail");
        h = (Long) t.getDeclaredMethod("tail", long.class, int.class).invoke(null, h, 7);""",
    "isolated": """        ClassLoader cl = ctx.createContextForSplit("arena_feature").getClassLoader();
        Class<?> c = Class.forName("%(pkg)s.feature.FeatureMix", true, cl);
        Method m = c.getDeclaredMethod("mix", long.class);
        h = (Long) m.invoke(null, h);
        Class<?> t = cl.loadClass("%(pkg)s.feature.Tail");
        h = (Long) t.getDeclaredMethod("tail", long.class, int.class).invoke(null, h, 7);""",
}
BODY["decoy_cnf"] = BODY["isolated"].replace("feature.FeatureMix\"", "feature.FeatureMixer\"")
FEAT = {
    "feature/FeatureMix.java": """package %(pkg)s.feature;
public final class FeatureMix {
    static final long K = %(k1)dL;
    static long round(long h) { h += K * 0x9E3779B97F4A7C15L; return Long.rotateLeft(h, 17) ^ (h >>> 31); }
    public static long mix(long h) { return %(pkg)s.Util.fold(round(h), K ^ 0x2545F4914F6CDD1DL); }
}
""",
    "feature/Tail.java": """package %(pkg)s.feature;
public final class Tail {
    public static long tail(long h, int n) { for (int i = 0; i < n; i++) h = %(pkg)s.Util.fold(h, %(k2)d + i); return h; }
}
""",
    "Util.java": """package %(pkg)s;
public final class Util {
    public static long fold(long h, long v) { return h + v; }
}
""",  # the split's shadowed duplicate: never runs (base copy wins)
}
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%(pkg)s"%(extra)s>
  <application android:hasCode="true"/>
</manifest>"""

tmp = Path(tempfile.mkdtemp())
pdir = PKG.replace(".", "/")
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)
fmt = {"pkg": PKG, "seed": SEED, "k1": K1, "k2": K2}
fmt["body"] = BODY[variant] % fmt


def build(files, srcdir, outdir, cp=None):
    for rel, body in files.items():
        (srcdir / rel).parent.mkdir(parents=True, exist_ok=True)
        (srcdir / rel).write_text(body % fmt if "%(" in body else body)
    subprocess.run(["javac", "--release", "8", "-nowarn", "-d", str(outdir), *(["-cp", str(cp)] if cp else []),
                    *map(str, srcdir.rglob("*.java"))], check=True)


FEAT_UTIL = FEAT.pop("Util.java")
build({**STUBS, **{f"{pdir}/{n}": b for n, b in {**BASE, **FEAT}.items()}}, tmp / "src", tmp / "cls")
build({f"{pdir}/Util.java": FEAT_UTIL}, tmp / "dsrc", tmp / "dcls")
shutil.copytree(tmp / "cls", tmp / "app")
shutil.rmtree(tmp / "app/android")
shutil.rmtree(tmp / "app/com/google")
shutil.rmtree(tmp / "app" / pdir / "feature")
(tmp / "app" / pdir / "Probe.class").unlink()
shutil.copytree(tmp / "cls" / pdir / "feature", tmp / "feat" / pdir / "feature")
shutil.copy(tmp / "dcls" / pdir / "Util.class", tmp / "feat" / pdir / "Util.class")
for k in ("app", "feat"):
    shutil.make_archive(str(tmp / k), "zip", tmp / k)
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / f"{k}.dex"), str(tmp / f"{k}.zip")],
                   check=True, capture_output=True)
members = {"base.apk": (None, "app.dex"), "split_arena_feature.apk": ("arena_feature", "feat.dex")}
for m, (split, dex) in members.items():
    extra = f' split="{split}" android:isFeatureSplit="true"' if split else (' android:isolatedSplits="true"' if ISO else "")
    (tmp / "AndroidManifest.xml").write_text(MAN % {"pkg": PKG, "extra": extra})
    subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                    str(tmp / "android-framework.jar"), "-o", str(tmp / ("raw_" + m))], check=True)
    with zipfile.ZipFile(tmp / ("raw_" + m)) as zin, zipfile.ZipFile(tmp / m, "w", zipfile.ZIP_DEFLATED) as z:
        for i in zin.infolist():
            z.writestr(i, zin.read(i))
        z.write(tmp / dex, "classes.dex")
        if split is None:
            z.writestr("assets/huntress_puzzle.json", b'{"schema":"huntress.mobile.puzzle.v2","day":27,'
                                                      b'"codec":"analysis","build":"splitcode-' + variant.encode() + b'"}')
out.unlink(missing_ok=True)
subprocess.run(["zip", "-q", "-0", "-j", "-X", str(out), *[str(tmp / m) for m in members]], check=True)

# --- oracle: unzip the bundle, aapt2 xmltree, dex -> jar via d2j-dex2jar, host JVM with real class loaders ---
ex, jars = tmp / "ex", tmp / "jars"
jars.mkdir()
subprocess.run(["unzip", "-q", "-o", str(out), "-d", str(ex)], check=True)
base_jar, split_jars, iso = None, {}, False
for m in subprocess.run(["unzip", "-Z1", str(out)], check=True, capture_output=True, text=True).stdout.split():
    x = subprocess.run([str(tmp / "aapt2"), "dump", "xmltree", "--file", "AndroidManifest.xml", str(ex / m)],
                       check=True, capture_output=True, text=True).stdout
    subprocess.run(["unzip", "-q", "-o", str(ex / m), "classes.dex", "-d", str(ex / (m + ".d"))], check=True)
    jar = jars / (m + ".jar")
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-dex2jar.sh"), "-f", "-o", str(jar), str(ex / (m + ".d/classes.dex"))],
                   check=True, capture_output=True)
    s = re.search(r'A: split="([^"]+)"', x) or re.search(r'A: http://schemas.android.com/apk/res/android:split[^=]*="([^"]+)"', x)
    if s:
        split_jars[s[1]] = jar
    else:
        base_jar = jar
        iso = bool(re.search(r"isolatedSplits\(0x[0-9a-f]+\)=(?:true|\(type 0x12\)0xffffffff)", x))
cp = [str(tmp / "cls_stubs"), str(base_jar)] + ([] if iso else [str(j) for j in split_jars.values()])
shutil.copytree(tmp / "cls", tmp / "cls_stubs")
for f in (tmp / "cls_stubs" / pdir).rglob("*.class"):
    if f.name != "Probe.class":
        f.unlink()
shown = subprocess.run(["java", f"-Dctx.iso={str(iso).lower()}", f"-Dctx.names={','.join(split_jars)}",
                        *[f"-Dctx.jar.{n}={j}" for n, j in split_jars.items()], "-cp", ":".join(cp), f"{PKG}.Probe"],
                       capture_output=True, text=True)
print(f"iso={iso} splits={list(split_jars)} oracle={shown.stdout.strip() or next((ln for ln in shown.stderr.splitlines() if 'Exception' in ln), shown.stderr.strip())}")
shutil.rmtree(tmp)
