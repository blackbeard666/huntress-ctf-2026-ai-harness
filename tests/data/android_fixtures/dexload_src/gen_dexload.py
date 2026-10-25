#!/usr/bin/env python3
"""Generate the dexload_* fixtures (coverage atlas rows 42, 100, 101: a v2 chain calling into a SECOND dex). A static
`Release.code(Context)` reads assets/payload.dex, hands it to a class loader and reflects into
com.huntress.arena.payload.Module; the answer is computed inside the payload (its <clinit> + static methods).
usage: gen_dexload.py <variant: file_cls | inmem_xor | decoy_name> <out.apk>
  file_cls   getAssets().open -> FileOutputStream copy into getCodeCacheDir(), setReadOnly, new DexClassLoader(path,
             odir, null, Release.class.getClassLoader()) -> loadClass -> getMethod("mix", long.class).invoke(null,
             Long.valueOf(seed)) -> unbox, plus getField("SALT").getLong(null)
  inmem_xor  asset bytes xor'd with an 8-byte key; read through a ByteArrayOutputStream loop, unxored, then
             new InMemoryDexClassLoader(ByteBuffer.wrap(b), c.getClassLoader()) -> getDeclaredMethod("mix", long.class,
             int.class).invoke(null, Long, Integer); Module calls a second payload class (Tab)
  decoy_name file_cls host whose loadClass names a class the payload does not define -> ClassNotFoundException ->
             "none"; neither dex carries a token literal (expected null)
Build: javac --release 8 (host + android.* / dalvik.* stubs; payload separately) -> d2j-jar2dex (host classes.dex and
payload.dex) -> python zipfile (classes.dex, assets/payload.dex, assets/huntress_puzzle.json codec=analysis).
ORACLE (independent of lib.android): the host JVM runs Release.code(new Context()) with stubs whose AssetManager reads
the BUILT APK via java.util.zip.ZipFile, getCodeCacheDir() is a real temp dir, and DexClassLoader /
InMemoryDexClassLoader are URLClassLoaders over the javac'd payload jar that first check the bytes they were handed
(file at `path` / ByteBuffer) are byte-identical to the d2j payload.dex (sha-256) -- so the host's copy / unxor
really ran. The JVM's printed value is `expected`."""
import hashlib, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
ROOT = Path(__file__).resolve().parents[4]
PKG = {"file_cls": "com.huntress.arena.dl1", "inmem_xor": "com.huntress.arena.dl2", "decoy_name": "com.huntress.arena.dl3"}[variant]
XKEY = b"arena-20"
STUBS = {
    "android/content/res/AssetManager.java": """package android.content.res;
public class AssetManager { public java.io.InputStream open(String n) throws java.io.IOException {
  java.util.zip.ZipFile z = new java.util.zip.ZipFile(System.getProperty("ctx.apk"));
  java.util.zip.ZipEntry e = z.getEntry("assets/" + n);
  if (e == null) throw new java.io.FileNotFoundException(n);
  return z.getInputStream(e); } }""",
    "android/content/Context.java": """package android.content;
public class Context { public android.content.res.AssetManager getAssets() { return new android.content.res.AssetManager(); }
  public java.io.File getCodeCacheDir() { return new java.io.File(System.getProperty("ctx.dir")); }
  public ClassLoader getClassLoader() { return Context.class.getClassLoader(); } }""",
    "dalvik/system/Chk.java": """package dalvik.system;
public class Chk { static java.net.URL[] jar(byte[] b) {
  try { byte[] h = java.security.MessageDigest.getInstance("SHA-256").digest(b);
    StringBuilder s = new StringBuilder(); for (byte x : h) s.append(String.format("%02x", x));
    if (!s.toString().equals(System.getProperty("ctx.dexsha"))) throw new IllegalStateException("payload bytes differ");
    return new java.net.URL[] { new java.io.File(System.getProperty("ctx.pjar")).toURI().toURL() };
  } catch (java.security.NoSuchAlgorithmException | java.net.MalformedURLException e) { throw new RuntimeException(e); } } }""",
    "dalvik/system/DexClassLoader.java": """package dalvik.system;
public class DexClassLoader extends java.net.URLClassLoader {
  public DexClassLoader(String path, String odir, String lib, ClassLoader parent) throws java.io.IOException {
    super(Chk.jar(java.nio.file.Files.readAllBytes(java.nio.file.Paths.get(path))), parent);
    if (new java.io.File(path).canWrite()) throw new SecurityException("Writable dex file is not allowed"); } }""",
    "dalvik/system/InMemoryDexClassLoader.java": """package dalvik.system;
public class InMemoryDexClassLoader extends java.net.URLClassLoader {
  static byte[] all(java.nio.ByteBuffer b) { byte[] o = new byte[b.remaining()]; b.duplicate().get(o); return o; }
  public InMemoryDexClassLoader(java.nio.ByteBuffer b, ClassLoader parent) { super(Chk.jar(all(b)), parent); } }""",
}
PAYLOAD = {
    "com/huntress/arena/payload/Module.java": """package com.huntress.arena.payload;
public final class Module {
  public static long SALT = 0x51ed270b27f3a1c9L;
  static final int[] ROT;
  static { ROT = new int[8]; for (int i = 0; i < 8; i++) ROT[i] = (i * 7 + 5) %% 31 + 1; SALT ^= Tab.T[3]; }
  public static long mix(long v) { long h = v ^ SALT; for (int i = 0; i < 8; i++) { h = Long.rotateLeft(h, ROT[i]) * 0x9e3779b97f4a7c15L; h ^= h >>> 31; } return h; }
  public static long mix(long v, int r) { long h = mix(v); for (int i = 0; i < r; i++) h = h * 6364136223846793005L + Tab.T[i & 7]; return h ^ %(salt)dL; }
}""",
    "com/huntress/arena/payload/Tab.java": """package com.huntress.arena.payload;
final class Tab { static final long[] T = new long[8];
  static { long x = 0x2545f4914f6cdd1dL; for (int i = 0; i < 8; i++) { x ^= x << 13; x ^= x >>> 7; x ^= x << 17; T[i] = x; } } }""",
}
HEX = """  static String hex(long h) { String s = Long.toHexString(h); while (s.length() < 16) s = "0" + s; return "ANS-" + s; }
"""
FILE_CHAIN = """    try {
      File dir = c.getCodeCacheDir();
      File f = new File(dir, "payload.dex");
      InputStream in = c.getAssets().open("payload.dex");
      FileOutputStream o = new FileOutputStream(f);
      byte[] buf = new byte[1024];
      int n;
      while ((n = in.read(buf)) > 0) o.write(buf, 0, n);
      o.close();
      in.close();
      f.setReadOnly();
      DexClassLoader dl = new DexClassLoader(f.getAbsolutePath(), dir.getAbsolutePath(), null, Release.class.getClassLoader());
      Class<?> k = dl.loadClass("%(cls)s");
      long seed = 0x6a09e667f3bcc908L ^ "%(pkg)s".hashCode();
      long v = ((Long) k.getMethod("mix", long.class).invoke(null, Long.valueOf(seed))).longValue();
      long s = k.getField("SALT").getLong(null);
      return hex(v ^ Long.rotateRight(s, 11));
    } catch (Exception e) { return "none"; }
"""
INMEM_CHAIN = """    try {
      InputStream in = c.getAssets().open("payload.dex");
      ByteArrayOutputStream bo = new ByteArrayOutputStream();
      byte[] buf = new byte[512];
      int n;
      while ((n = in.read(buf)) != -1) bo.write(buf, 0, n);
      in.close();
      byte[] b = bo.toByteArray();
      byte[] key = "%(key)s".getBytes("UTF-8");
      for (int i = 0; i < b.length; i++) b[i] = (byte) (b[i] ^ key[i %% key.length]);
      InMemoryDexClassLoader dl = new InMemoryDexClassLoader(ByteBuffer.wrap(b), c.getClassLoader());
      Class<?> k = dl.loadClass("com.huntress.arena.payload.Module");
      Method m = k.getDeclaredMethod("mix", long.class, int.class);
      Object r = m.invoke(null, Long.valueOf(0x3c6ef372fe94f82bL), Integer.valueOf(13));
      return hex(((Long) r).longValue());
    } catch (Exception e) { return "none"; }
"""
CHAIN = {"file_cls": FILE_CHAIN % {"cls": "com.huntress.arena.payload.Module", "pkg": PKG},
         "inmem_xor": INMEM_CHAIN % {"key": XKEY.decode()},
         "decoy_name": FILE_CHAIN % {"cls": "com.huntress.arena.payload.Modul", "pkg": PKG}}[variant]
APP = """package %(pkg)s;
import android.content.Context;
import dalvik.system.*;
import java.io.*;
import java.lang.reflect.Method;
import java.nio.ByteBuffer;
public final class Release {
""" % {"pkg": PKG} + HEX + """  public static String code(Context c) {
""" + CHAIN + "  }\n}\n"
PROBE = """package %(pkg)s;
public class Probe { public static void main(String[] a) { System.out.println(Release.code(new android.content.Context())); } }"""

tmp = Path(tempfile.mkdtemp())
pdir = PKG.replace(".", "/")
psrc, pcls, hsrc, hcls = tmp / "psrc", tmp / "pcls", tmp / "hsrc", tmp / "hcls"
for rel, body in PAYLOAD.items():
    (psrc / rel).parent.mkdir(parents=True, exist_ok=True)
    (psrc / rel).write_text(body % {"salt": int.from_bytes(hashlib.sha256(variant.encode()).digest()[:4], "big")})
subprocess.run(["javac", "--release", "8", "-d", str(pcls), *map(str, psrc.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "payload"), "zip", pcls)
files = dict(STUBS)
files[f"{pdir}/Release.java"] = APP
files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG}
for rel, body in files.items():
    (hsrc / rel).parent.mkdir(parents=True, exist_ok=True)
    (hsrc / rel).write_text(body)
subprocess.run(["javac", "--release", "8", "-d", str(hcls), *map(str, hsrc.rglob("*.java"))], check=True)
app = tmp / "app"
shutil.copytree(hcls, app)
for junk in ("android", "dalvik", f"{pdir}/Probe.class"):
    p = app / junk
    shutil.rmtree(p) if p.is_dir() else p.unlink()
shutil.make_archive(str(tmp / "app"), "zip", app)
d2j = str(ROOT / "tools/dex2jar/d2j-jar2dex.sh")
subprocess.run([d2j, "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")], check=True, capture_output=True)
subprocess.run([d2j, "-f", "-o", str(tmp / "payload.dex"), str(tmp / "payload.zip")], check=True, capture_output=True)
pdex = (tmp / "payload.dex").read_bytes()
asset = bytes(x ^ XKEY[i % len(XKEY)] for i, x in enumerate(pdex)) if variant == "inmem_xor" else pdex
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
    z.writestr("assets/payload.dex", asset)
    z.writestr("assets/huntress_puzzle.json", '{"schema":"huntress.mobile.puzzle.v1","day":20,"codec":"analysis"}')
# --- oracle: the host JVM runs Release.code() against the built APK, the payload loaded from its javac'd jar ---
(tmp / "cc").mkdir()
shown = subprocess.run(["java", f"-Dctx.apk={out}", f"-Dctx.dir={tmp / 'cc'}", f"-Dctx.pjar={tmp / 'payload.zip'}",
                        f"-Dctx.dexsha={hashlib.sha256(pdex).hexdigest()}", "-cp", str(hcls), f"{PKG}.Probe"],
                       check=True, capture_output=True, text=True).stdout.strip()
shutil.rmtree(tmp)
print(f"variant={variant} oracle={shown}")
