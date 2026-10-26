#!/usr/bin/env python3
"""Generate the rflx_* fixtures (coverage atlas rows 43/77/80, v2-reflection-api-breadth): the D23 'Hook Line and Signal'
TT v2 chain (same mixers as obfv2_*: token = HookScan.mixPatcheb(Util.scanSignal61(Util.mixTrampoline79(SEED))) ->
Mix.f1 -> Util.finTrampoline2d ^ K -> "ANS-" + 16 nibbles) reached through reflection APIs beyond
forName + getDeclaredMethod + invoke:
  iter       Class.getDeclaredMethods() / getMethods() scanned for getName().hashCode() == H / .equals(x(..)) /
             .startsWith(x(..)) && getParameterTypes().length == 1 && getParameterTypes()[0] == Long.TYPE (Mix carries
             decoy overloads f1(int), f1(Long) that a name-only match would pick), Method.invoke, unboxed Long;
             InvocationTargetException caught around every invoke
  fieldctor  SEED / K read by getDeclaredField(x(..)) + setAccessible(true) + getLong(null) (SEED a static_values
             constant, K set in <clinit>), the last stage an instance mixer: getDeclaredConstructor().newInstance() +
             getDeclaredMethod("apply", Long.TYPE).invoke(obj, v) on a field set by the constructor; one more term is
             Util.tweak via getDeclaredMethod(x, Integer.TYPE) (an Integer.class overload is the decoy), and the Stage
             class's getSimpleName().hashCode() + getName().length() feed the mix
  mh         MethodHandles.lookup().findStatic(Class.forName(x(..)), x(..), MethodType.methodType(long.class,
             long.class)).invokeExact(v) for every mixer (invoke-polymorphic in the dex)
  decoy      the iter chain, but the hex loop emits 15 nibbles (ANS-<15 hex>: a near-miss, no valid token)
usage: gen_rflx.py <variant> <out.apk>
Build: javac --release 8 (app + android.content.Context stub) -> dex2jar d2j-jar2dex -> zipfile (+ assets/
huntress_puzzle.json, codec: analysis, no data). Oracle: the host JVM runs Release.code(null) on the javac classes and
prints 'oracle=<value>'."""
import shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d23.rflx" + variant
CTX = "package android.content;\npublic class Context { }"

MIX = """package %(pkg)s;
public final class Mix {
    static long f1(int j) { return Util.sealHook30(j); }
    static long f1(Long j) { return Util.sealHook30(j.longValue() ^ 1L); }
    static long f1(long j) {
        long j2 = (j ^ (-2307042702180851644L)) * 333607066048539835L;
        long j3 = (j2 << 3) | (j2 >>> 61);
        long j4 = (((j3 << 31) | (j3 >>> 33)) * (-886256348880561723L)) ^ (-2607315507995602435L);
        return (j4 << 44) | (j4 >>> 20);
    }
}"""
PROBE = """package %(pkg)s;
public final class Probe {
    static int s2(int i, int i2, int i3, int i4) {
        int i5 = 0;
        while (((((i5 ^ i3) * i) + i2) & 4095) != i4) { i5++; if (i5 >= 4096) return -1; }
        return i5;
    }
    static int s3(int i, int i2, int i3, int i4) {
        int i5 = (i %% 11) + 1; int i6 = 12 - i5; int i7 = 0;
        do {
            int i8 = (i7 ^ i3) & 4095;
            if (((((i8 >>> i6) | (i8 << i5)) + i2) & 4095) == i4) return i7;
            i7++;
        } while (i7 < 4096);
        return -1;
    }
}"""
UTIL = """package %(pkg)s;
public final class Util {
    static long finTrampoline2d(long j) {
        long j2 = (j ^ (j >>> 10)) * (-4565261069424997581L);
        return ((((((j2 << 23) | (j2 >>> 41)) + 799274663451203256L) ^ 3900367236340418941L) ^ (-2044953418663047449L)) ^ 1775288625161603791L) + 4847595846291780659L;
    }
    static long mixTrampoline79(long j) {
        long j2 = j ^ (j >>> 28);
        long j3 = ((((j2 ^ (j2 >>> 30)) ^ (-5342125323041540572L)) + 2183413890471151166L) ^ 5116065488051834350L) * (-1402156385267666889L);
        long j4 = (j3 << 41) | (j3 >>> 23);
        return (j4 << 10) | (j4 >>> 54);
    }
    static long scanSignal61(long j) {
        int a = Probe.s3(3572, 943, 1370, 293);
        int b = Probe.s3(1990, 2605, 1464, 1995);
        int c = Probe.s2(3849, 3120, 2439, 2906);
        long v = (((j ^ (((0 ^ (((long) a) * (-3409818179106685223L))) ^ (((long) b) * (-8371994457828002933L))) ^ (((long) c) * (-3055453405719099057L)))) * (-8474999941664858633L)) + (((long) (((a ^ b) ^ c) & 7)) * 579319999994391256L)) * (-1580869134723234487L) * 3504449675974248957L;
        return (v << 23) | (v >>> 41);
    }
    static long tweak(int i) { return ((long) i) * 0x9E3779B97F4A7C15L; }
    static long tweak(Integer i) { return 0x5A5A5A5AL; }
    static long sealHook30(long j) {
        long j2 = (j ^ (-6346643076729912359L)) * (-301087911024711665L);
        return ((j2 << 55) | (j2 >>> 9)) * 2575955574811816977L;
    }
}"""
HOOK = """package %(pkg)s;
public final class HookScan {
    static long mixPatcheb(long j) {
        long j2 = (j ^ 5006709854372244345L) * 1958157885234814829L;
        long j3 = (j2 << 30) | (j2 >>> 34);
        return (j3 ^ (j3 >>> 20)) - 7619862862749198346L;
    }
}"""
HEX = """
    static String hex(long v, int top) {
        StringBuilder sb = new StringBuilder();
        sb.append("ANS-");
        int i = top;
        do { sb.append("0123456789ABCDEF".charAt(((int) (v >>> i)) & 15)); i -= 4; } while (i >= 0);
        return sb.toString();
    }
    public static String proof(Context context) { ctx = context; return Long.toHexString(token()); }"""
HEX = """
    static String x(byte[] b) {
        char[] c = new char[b.length];
        for (int i = 0; i < b.length; i++) c[i] = (char) ((b[i] ^ 0x2B ^ i) & 0xFF);
        return new String(c);
    }
    static String hex(long v, int top) {
        StringBuilder sb = new StringBuilder();
        sb.append("ANS-");
        int i = top;
        do { sb.append("0123456789ABCDEF".charAt(((int) (v >>> i)) & 15)); i -= 4; } while (i >= 0);
        return sb.toString();
    }"""
NAMES = """
    static final byte[] N_MIX = {%(n_mix)s};
    static final byte[] N_UTIL = {%(n_util)s};
    static final byte[] N_HOOK = {%(n_hook)s};
    static final byte[] N_KEYS = {%(n_keys)s};
    static final byte[] N_STAGE = {%(n_stage)s};
    static final byte[] M_F1 = {%(m_f1)s};
    static final byte[] M_FIN = {%(m_fin)s};
    static final byte[] M_M79 = {%(m_m79)s};
    static final byte[] M_S61 = {%(m_s61)s};
    static final byte[] M_PEB = {%(m_peb)s};
    static final byte[] M_TWK = {%(m_twk)s};
    static final byte[] M_APPLY = {%(m_apply)s};
    static final byte[] F_SEED = {%(f_seed)s};
    static final byte[] F_K = {%(f_k)s};"""
ITER = """package %(pkg)s;
import android.content.Context;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
public final class Release {
    static Context ctx;""" + NAMES + """
    static Method pick(Class<?> c, int mode, String key) {
        Method[] ms = mode == 2 ? c.getMethods() : c.getDeclaredMethods();
        for (int i = 0; i < ms.length; i++) {
            Method m = ms[i];
            Class<?>[] p = m.getParameterTypes();
            if (p.length != 1 || p[0] != Long.TYPE) continue;
            String n = m.getName();
            boolean ok = mode == 0 ? n.hashCode() == key.hashCode() : mode == 1 ? n.startsWith(key) : n.equals(key);
            if (ok) return m;
        }
        return null;
    }
    static long call(byte[] cls, byte[] name, int mode, long v) {
        try {
            Method m = pick(Class.forName(x(cls)), mode, x(name));
            m.setAccessible(true);
            Object r = m.invoke(null, Long.valueOf(v));
            return ((Long) r).longValue();
        } catch (InvocationTargetException e) {
            return -1L;
        } catch (Exception e) {
            return 0L;
        }
    }
    public static String code(Context context) {
        ctx = context;
        long v = call(N_UTIL, M_FIN, 0, call(N_MIX, M_F1, 0, token())) ^ (-7148765225602638926L);
        return hex(v, %(top)s);
    }
    public static long token() {
        return call(N_HOOK, M_PEB, 1, call(N_UTIL, M_S61, 0, call(N_UTIL, M_M79, 1, -6466867484639169990L)));
    }
""" + HEX + "\n}"
KEYS = """package %(pkg)s;
final class Keys {
    private static final long SEED = -6466867484639169990L;
    private static long K;
    static { K = -7148765225602638926L ^ 0x1234L; K ^= 0x1234L; }
}"""
STAGE = """package %(pkg)s;
public final class Stage {
    private final long salt;
    public Stage() { salt = 0x0F0F0F0F0F0F0F0FL; }
    long apply(long v) { return Util.finTrampoline2d(Mix.f1(v ^ salt) ^ salt); }
}"""
FIELDCTOR = """package %(pkg)s;
import android.content.Context;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
public final class Release {
    static Context ctx;""" + NAMES + """
    static long fld(byte[] cls, byte[] name) throws Exception {
        Field f = Class.forName(x(cls)).getDeclaredField(x(name));
        f.setAccessible(true);
        return f.getLong(null);
    }
    static long call(byte[] cls, byte[] name, long v) throws Exception {
        Method m = Class.forName(x(cls)).getDeclaredMethod(x(name), Long.TYPE);
        return ((Long) m.invoke(null, Long.valueOf(v))).longValue();
    }
    public static String code(Context context) {
        ctx = context;
        try {
            Class<?> sc = Class.forName(x(N_STAGE));
            Constructor<?> k = sc.getDeclaredConstructor();
            k.setAccessible(true);
            Object st = k.newInstance();
            Method ap = sc.getDeclaredMethod(x(M_APPLY), Long.TYPE);
            ap.setAccessible(true);
            Method tw = Class.forName(x(N_UTIL)).getDeclaredMethod(x(M_TWK), Integer.TYPE);
            long t = ((Long) tw.invoke(null, Integer.valueOf(7))).longValue();
            long h = (long) sc.getSimpleName().hashCode() + sc.getName().length();
            long v = ((Long) ap.invoke(st, Long.valueOf(token()))).longValue() ^ fld(N_KEYS, F_K) ^ t ^ h;
            return hex(v, 60);
        } catch (Exception e) {
            return null;
        }
    }
    public static long token() throws Exception {
        return call(N_HOOK, M_PEB, call(N_UTIL, M_S61, call(N_UTIL, M_M79, fld(N_KEYS, F_SEED))));
    }
""" + HEX + "\n}"
MH = """package %(pkg)s;
import android.content.Context;
import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;
public final class Release {
    static Context ctx;""" + NAMES + """
    static long call(byte[] cls, byte[] name, long v) {
        try {
            MethodHandle h = MethodHandles.lookup().findStatic(Class.forName(x(cls)), x(name),
                MethodType.methodType(long.class, long.class));
            return (long) h.invokeExact(v);
        } catch (Throwable e) {
            return 0L;
        }
    }
    public static String code(Context context) {
        ctx = context;
        long v = call(N_UTIL, M_FIN, call(N_MIX, M_F1, token())) ^ (-7148765225602638926L);
        return hex(v, 60);
    }
    public static long token() {
        return call(N_HOOK, M_PEB, call(N_UTIL, M_S61, call(N_UTIL, M_M79, -6466867484639169990L)));
    }
""" + HEX + "\n}"
ORACLE = """package %(pkg)s;
public final class Oracle {
    public static void main(String[] a) throws Exception { System.out.println("oracle=" + Release.code(null)); }
}"""


def xb(s, key=0x2B):
    return ", ".join(str(((ord(c) ^ key ^ i) + 128) % 256 - 128) for i, c in enumerate(s))


rel = {"iter": ITER, "decoy": ITER, "fieldctor": FIELDCTOR, "mh": MH}[variant]
subs = {"pkg": PKG, "top": 56 if variant == "decoy" else 60,
        "n_mix": xb(PKG + ".Mix"), "n_util": xb(PKG + ".Util"), "n_hook": xb(PKG + ".HookScan"),
        "n_keys": xb(PKG + ".Keys"), "n_stage": xb(PKG + ".Stage"),
        "m_f1": xb("f1"), "m_fin": xb("finTrampoline2d"), "m_m79": xb("mixTrampoline"),
        "m_s61": xb("scanSignal61"), "m_peb": xb("mixPatch"), "m_twk": xb("tweak"), "m_apply": xb("apply"),
        "f_seed": xb("SEED"), "f_k": xb("K")}
if variant != "iter" and variant != "decoy":  # prefix keys (startsWith) only in the iter chain
    subs["m_m79"], subs["m_peb"] = xb("mixTrampoline79"), xb("mixPatcheb")
tmp = Path(tempfile.mkdtemp())
try:
    src, pdir = tmp / "src", tmp / "src" / PKG.replace(".", "/")
    pdir.mkdir(parents=True)
    (tmp / "src/android/content").mkdir(parents=True)
    (tmp / "src/android/content/Context.java").write_text(CTX)
    for n, t in (("Mix", MIX), ("Probe", PROBE), ("Util", UTIL), ("HookScan", HOOK), ("Keys", KEYS),
                 ("Stage", STAGE), ("Release", rel), ("Oracle", ORACLE)):
        (pdir / f"{n}.java").write_text(t % subs)
    cls = tmp / "cls"
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    oracle = subprocess.run(["java", "-cp", str(cls), PKG + ".Oracle"], check=True, capture_output=True,
                            text=True).stdout.strip()
    print(oracle)
    with zipfile.ZipFile(tmp / "app.zip", "w") as z:  # app classes only (Oracle + the Context stub stay out of the dex)
        for f in (cls / PKG.replace(".", "/")).glob("*.class"):
            if f.name != "Oracle.class":
                z.write(f, f.relative_to(cls).as_posix())
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"),
                    str(tmp / "app.zip")], check=True, capture_output=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("assets/huntress_puzzle.json", '{"schema":"huntress.mobile.puzzle.v2","day":23,"codec":"analysis",'
                   '"build":"rflx%s"}' % variant)
        z.write(tmp / "classes.dex", "classes.dex")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
