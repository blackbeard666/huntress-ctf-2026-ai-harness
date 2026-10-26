#!/usr/bin/env python3
"""Generate the splitread_* fixtures (coverage atlas rows 58, 102: v2-split-asset-read). A `.apks` bundle (stored zip
of base.apk + split_feature_a.apk + split_feature_b.apk, split manifests `split="feature_x"` hasCode=false). The base
puzzle is v2 `codec: analysis`; Release.code(Context) computes the token from a split's asset bytes:
  zip_two_splits  Assets.readSplit(ctx, name): for p in getApplicationInfo().splitSourceDirs: ZipFile(p).getEntry(
                  "assets/"+name), null -> close + next; read 16 B via InputStream.read(buf, off, len) loop, else throw
                  FileNotFoundException; Util folds ByteBuffer.wrap(b).order(BIG_ENDIAN).getLong() x2. Only
                  feature_b holds the entry (feature_a ships a different asset).
  ctx_split       createContextForSplit("feature_b").getAssets().open(name) -> DataInputStream.readLong x2, plus the
                  base Context's getAssets().open("huntress_salt.bin") that only feature_a ships (base then splits);
                  bundle order = splits first, base last.
  decoy_missing   zip_two_splits layout but neither split ships the named entry -> FileNotFoundException, no token.
usage: gen_split.py <variant> <out.apks>
Build: javac --release 8 (app + android.* stubs) -> dex2jar d2j-jar2dex; manifests by apktool's aapt2 link
-I android-framework.jar; python zipfile adds assets/classes.dex to each inner APK; `zip -0 -j` makes the bundle.
ORACLE (independent of lib.android): `aapt2 dump xmltree` reads each member's split name; the host JVM runs
Release.code() on stubs backed by the members extracted with `unzip`: splitSourceDirs = their real paths (bundle
order), java.util.zip.ZipFile / AssetManager.open over those real files."""
import random, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
ROOT = Path(__file__).resolve().parents[4]
PKG = {"zip_two_splits": "com.huntress.arena.split1", "ctx_split": "com.huntress.arena.split2",
       "decoy_missing": "com.huntress.arena.split3"}[variant]
rnd = random.Random(variant)
STUBS = {
    "android/content/pm/ApplicationInfo.java": """package android.content.pm;
public class ApplicationInfo { public String sourceDir; public String[] splitSourceDirs; public String[] splitNames; public int flags; }""",
    "android/content/pm/PackageManager.java": """package android.content.pm;
public class PackageManager { public static class NameNotFoundException extends Exception { } }""",
    "android/content/res/AssetManager.java": """package android.content.res;
public class AssetManager { final String[] order; public AssetManager(String[] o) { order = o; }
  public java.io.InputStream open(String n) throws java.io.IOException {
    for (String p : order) { java.util.zip.ZipFile z = new java.util.zip.ZipFile(p);
      java.util.zip.ZipEntry e = z.getEntry("assets/" + n);
      if (e != null) return z.getInputStream(e); z.close(); }
    throw new java.io.FileNotFoundException(n); } }""",
    "android/content/Context.java": """package android.content;
import android.content.pm.*;
public class Context { final String own;
  public Context() { this(null); } Context(String s) { own = s; }
  static String[] list(String k) { String v = System.getProperty(k, ""); return v.isEmpty() ? new String[0] : v.split(","); }
  public ApplicationInfo getApplicationInfo() { ApplicationInfo a = new ApplicationInfo();
    a.sourceDir = System.getProperty("ctx.base"); a.splitSourceDirs = list("ctx.splits"); a.splitNames = list("ctx.names"); return a; }
  public Context createContextForSplit(String n) throws PackageManager.NameNotFoundException {
    for (String s : list("ctx.names")) if (s.equals(n)) return new Context(n); throw new PackageManager.NameNotFoundException(); }
  public android.content.res.AssetManager getAssets() { String[] p = list("ctx.splits"), nm = list("ctx.names");
    java.util.ArrayList<String> o = new java.util.ArrayList<>();
    for (int i = 0; i < p.length; i++) if (nm[i].equals(own)) o.add(p[i]);
    o.add(System.getProperty("ctx.base"));
    for (int i = 0; i < p.length; i++) if (!nm[i].equals(own)) o.add(p[i]);
    return new android.content.res.AssetManager(o.toArray(new String[0])); } }""",
}
READ = """    static byte[] readSplit(Context ctx, String name) throws IOException {
        String[] dirs = ctx.getApplicationInfo().splitSourceDirs;
        if (dirs != null) for (String p : dirs) {
            ZipFile z = new ZipFile(p);
            ZipEntry e = z.getEntry("assets/" + name);
            if (e == null) { z.close(); continue; }
            byte[] buf = new byte[16];
            int off = 0;
            InputStream in = z.getInputStream(e);
            while (off < buf.length) { int r = in.read(buf, off, buf.length - off); if (r < 0) break; off += r; }
            in.close();
            z.close();
            return buf;
        }
        throw new FileNotFoundException(name);
    }
"""
SEED = rnd.getrandbits(63)
BODY = {
    "zip_two_splits": """        byte[] b = Assets.readSplit(ctx, "huntress_feature.bin");
        ByteBuffer bb = ByteBuffer.wrap(b).order(ByteOrder.BIG_ENDIAN);
        long h = Util.mergeFeatureHi(SEED, bb.getLong());
        h = Util.mergeFeatureLo(h, bb.getLong());""",
    "ctx_split": """        DataInputStream d = new DataInputStream(ctx.createContextForSplit("feature_b").getAssets().open("huntress_feature.bin"));
        long h = Util.mergeFeatureHi(SEED, d.readLong());
        h = Util.mergeFeatureLo(h, d.readLong());
        d.close();
        DataInputStream s = new DataInputStream(ctx.getAssets().open("huntress_salt.bin"));
        h = Util.mergeFeatureLo(h, s.readInt());""",
}
BODY["decoy_missing"] = BODY["zip_two_splits"]
APP = {
    "Assets.java": "package %(pkg)s;\nimport android.content.Context;\nimport java.io.*;\nimport java.util.zip.*;\n"
                   "final class Assets {\n" + READ + "}\n",
    "Util.java": """package %(pkg)s;
final class Util {
    static long mergeFeatureHi(long h, long v) { h ^= v; h *= 0x100000001b3L; return h ^ (h >>> 29); }
    static long mergeFeatureLo(long h, long v) { h += v * 0x9E3779B97F4A7C15L; return Long.rotateLeft(h, 17) ^ (h >>> 31); }
}
""",
    "Release.java": """package %(pkg)s;
import android.content.Context;
import java.io.*;
import java.nio.*;
public final class Release {
    static final long SEED = %(seed)dL;
    static String hex(long v) {
        char[] H = "0123456789ABCDEF".toCharArray();
        StringBuilder sb = new StringBuilder();
        for (int i = 60; i >= 0; i -= 4) sb.append(H[(int) ((v >>> i) & 15)]);
        return sb.toString();
    }
    public static String code(Context ctx) throws Exception {
%(body)s
        return "ANS-" + hex(h);
    }
}
""",
    "Probe.java": "package %(pkg)s;\npublic class Probe { public static void main(String[] a) throws Exception {"
                  " System.out.println(Release.code(new android.content.Context())); } }\n",
}
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%(pkg)s"%(split)s>
  <application android:hasCode="%(code)s"/>
</manifest>"""

tmp = Path(tempfile.mkdtemp())
src, cls = tmp / "src", tmp / "cls"
pdir = PKG.replace(".", "/")
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)
files = dict(STUBS)
for n, body in APP.items():
    files[f"{pdir}/{n}"] = body % {"pkg": PKG, "seed": SEED, "body": BODY[variant]}
for rel, body in files.items():
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(body)
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
app = tmp / "app"
shutil.copytree(cls, app)
shutil.rmtree(app / "android")
(app / pdir / "Probe.class").unlink()
shutil.make_archive(str(tmp / "app"), "zip", app)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
feat = bytes(rnd.getrandbits(8) for _ in range(16))
salt = bytes(rnd.getrandbits(8) for _ in range(4))
name = "huntress_feature.bin" if variant != "decoy_missing" else "huntress_feature.bln"
members = {  # member -> (split name, assets)
    "base.apk": (None, {"huntress_puzzle.json": b'{"schema":"huntress.mobile.puzzle.v2","day":26,"codec":"analysis",'
                                                b'"build":"split-' + variant.encode() + b'"}'}),
    "split_feature_a.apk": ("feature_a", {"huntress_other.bin": bytes(16), "huntress_salt.bin": salt}),
    "split_feature_b.apk": ("feature_b", {name: feat}),
}
for m, (split, assets) in members.items():
    (tmp / "AndroidManifest.xml").write_text(MAN % {"pkg": PKG, "split": f' split="{split}"' if split else "",
                                                    "code": "false" if split else "true"})
    subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                    str(tmp / "android-framework.jar"), "-o", str(tmp / ("raw_" + m))], check=True)
    with zipfile.ZipFile(tmp / ("raw_" + m)) as zin, zipfile.ZipFile(tmp / m, "w", zipfile.ZIP_DEFLATED) as z:
        for i in zin.infolist():
            z.writestr(i, zin.read(i))
        if split is None:
            z.write(tmp / "classes.dex", "classes.dex")
        for n, b in assets.items():
            z.writestr("assets/" + n, b)
order = ["base.apk", "split_feature_a.apk", "split_feature_b.apk"]
if variant == "ctx_split":
    order = order[1:] + order[:1]
out.unlink(missing_ok=True)
subprocess.run(["zip", "-q", "-0", "-j", "-X", str(out), *[str(tmp / m) for m in order]], check=True)

# --- oracle: unzip the bundle, aapt2 xmltree split names, host JVM on the extracted members ---
ex = tmp / "ex"
subprocess.run(["unzip", "-q", "-o", str(out), "-d", str(ex)], check=True)
names = subprocess.run(["unzip", "-Z1", str(out)], check=True, capture_output=True, text=True).stdout.split()
splits, snames, base = [], [], None
for m in names:
    x = subprocess.run([str(tmp / "aapt2"), "dump", "xmltree", "--file", "AndroidManifest.xml", str(ex / m)],
                       check=True, capture_output=True, text=True).stdout
    s = re.search(r'A: split="([^"]+)"', x)
    if s:
        splits.append(str(ex / m))
        snames.append(s[1])
    else:
        base = str(ex / m)
shown = subprocess.run(["java", f"-Dctx.base={base}", f"-Dctx.splits={','.join(splits)}", f"-Dctx.names={','.join(snames)}",
                        "-cp", str(cls), f"{PKG}.Probe"], capture_output=True, text=True)
shutil.rmtree(tmp)
print(f"order={names} splits={snames} oracle={shown.stdout.strip() or shown.stderr.strip().splitlines()[0]}")
