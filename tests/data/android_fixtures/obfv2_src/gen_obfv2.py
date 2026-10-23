#!/usr/bin/env python3
"""Generate the obfv2_* fixtures (coverage atlas: analysis-chain-obfuscation-hardening, rows 72/77/79/81/96): the D23
'Hook Line and Signal' TT v2 chain (Release.code -> HookScan.mixPatcheb(Util.scanSignal61(Util.mixTrampoline79(SEED)))
-> Mix.f1 -> Util.finTrampoline2d ^ K -> "ANS-" + 16 nibbles of "0123456789ABCDEF"; Probe.s2/s3 4096-step inverse
searches) rewritten with ONE obfuscating transform per variant:
  flat     token() as a while(true){switch(state)} int dispatcher + code() as a string-switch (hashCode/equals) dispatcher
  reflect  every mixer reached via Class.forName / getDeclaredMethod(name, Long.TYPE) with xor'd names, Method.invoke on
           a boxed Long, unboxed with ((Long) r).longValue()
  opaque   opaque predicates over non-final statics ((x*x+x)&1 == 0, 7*y*y != 1 mod 7...) guard the real mixer, the
           never-taken branch runs a decoy mixer (sealHook30) that yields a different ANS
  vm       a tiny bytecode VM (byte[] program, long[] constant pool, switch over opcodes) runs the whole mix
  decoy    the flat chain, but the hex loop emits 15 nibbles (ANS-<15 hex>: a near-miss, no valid token anywhere)
usage: gen_obfv2.py <variant> <out.apk>
Build: javac --release 8 (app + android.content.Context stub) -> dex2jar d2j-jar2dex -> zipfile (+ assets/
huntress_puzzle.json, codec: analysis, no data). Oracle: the host JVM runs Release.code(null) on the javac classes and
prints the token (printed to stdout as 'oracle=<value>')."""
import shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d23.obf" + variant
CTX = "package android.content;\npublic class Context { }"

MIX = """package %(pkg)s;
public final class Mix {
    static long f1(int j) { return Util.sealHook30(j); }
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
FLAT = """package %(pkg)s;
import android.content.Context;
public final class Release {
    static Context ctx;
    static final String[] PLAN = {"f1", "fin", "seal"};
    public static String code(Context context) {
        ctx = context;
        long v = token();
        for (String op : PLAN) {
            switch (op) {
                case "f1": v = Mix.f1(v); break;
                case "fin": v = Util.finTrampoline2d(v) ^ (-7148765225602638926L); break;
                case "seal": return hex(v, %(top)s);
                default: v = Util.sealHook30(v); break;
            }
        }
        return null;
    }
    public static long token() {
        long v = -6466867484639169990L;
        int state = 0x3A;
        while (true) {
            switch (state) {
                case 0x3A: v = Util.mixTrampoline79(v); state = 0x71; break;
                case 0x71: v = Util.scanSignal61(v); state = 0x05; break;
                case 0x05: v = HookScan.mixPatcheb(v); state = 0x6C; break;
                case 0x13: v = Util.sealHook30(v); state = 0x6C; break;
                case 0x6C: return v;
                default: state = 0x13; break;
            }
        }
    }
""" + HEX + "\n}"
REFLECT = """package %(pkg)s;
import android.content.Context;
import java.lang.reflect.Method;
public final class Release {
    static Context ctx;
    static final int KEY = 0x2B;
    static final byte[] N_MIX = {%(n_mix)s};
    static final byte[] N_UTIL = {%(n_util)s};
    static final byte[] N_HOOK = {%(n_hook)s};
    static final byte[] M_F1 = {%(m_f1)s};
    static final byte[] M_FIN = {%(m_fin)s};
    static final byte[] M_M79 = {%(m_m79)s};
    static final byte[] M_S61 = {%(m_s61)s};
    static final byte[] M_PEB = {%(m_peb)s};
    static String x(byte[] b) {
        char[] c = new char[b.length];
        for (int i = 0; i < b.length; i++) c[i] = (char) ((b[i] ^ KEY ^ i) & 0xFF);
        return new String(c);
    }
    static long call(byte[] cls, byte[] name, long v) {
        try {
            Method m = Class.forName(x(cls)).getDeclaredMethod(x(name), Long.TYPE);
            m.setAccessible(true);
            Object r = m.invoke(null, Long.valueOf(v));
            return ((Long) r).longValue();
        } catch (Exception e) {
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
OPAQUE = """package %(pkg)s;
import android.content.Context;
public final class Release {
    static Context ctx;
    static int gx = 0x1D3;
    static int gy = 0x2C9;
    public static String code(Context context) {
        ctx = context;
        long v = token();
        if (((gx * gx + gx) & 1) == 0) v = Mix.f1(v); else v = Util.sealHook30(v);
        if ((7 * gy * gy) %% 7 != 1) v = Util.finTrampoline2d(v) ^ (-7148765225602638926L);
        else v = Util.sealHook30(v) ^ 0x5A5A5A5AL;
        return hex(v, 60);
    }
    public static long token() {
        long v = Util.mixTrampoline79(-6466867484639169990L);
        if ((gy * (gy + 1) * (gy + 2)) %% 3 == 0) v = Util.scanSignal61(v); else v = Util.sealHook30(v);
        if (((gx | 1) & 1) == 0) return Util.sealHook30(v);
        return HookScan.mixPatcheb(v);
    }
""" + HEX + "\n}"
VM = """package %(pkg)s;
import android.content.Context;
public final class Release {
    static Context ctx;
    static final long[] POOL = {-2307042702180851644L, 333607066048539835L, -886256348880561723L,
        -2607315507995602435L, -7148765225602638926L, -6466867484639169990L};
    // op: 0 x^=POOL[a]  1 x*=POOL[a]  2 x=rotl(x,a)  3 call fn a  4 x=POOL[a]  5 halt
    static final byte[] PROG = {4, 5, 3, 0, 3, 1, 3, 2, 0, 0, 1, 1, 2, 3, 2, 31, 1, 2, 0, 3, 2, 44, 3, 3, 0, 4, 5, 0};
    static long run(byte[] p) {
        long x = 0L;
        int pc = 0;
        while (true) {
            int op = p[pc], a = p[pc + 1];
            pc += 2;
            switch (op) {
                case 0: x ^= POOL[a]; break;
                case 1: x *= POOL[a]; break;
                case 2: x = (x << a) | (x >>> (64 - a)); break;
                case 3:
                    switch (a) {
                        case 0: x = Util.mixTrampoline79(x); break;
                        case 1: x = Util.scanSignal61(x); break;
                        case 2: x = HookScan.mixPatcheb(x); break;
                        case 3: x = Util.finTrampoline2d(x); break;
                        default: x = Util.sealHook30(x); break;
                    }
                    break;
                case 4: x = POOL[a]; break;
                case 5: return x;
                default: return -1L;
            }
        }
    }
    public static String code(Context context) {
        ctx = context;
        return hex(run(PROG), 60);
    }
    public static long token() {
        return HookScan.mixPatcheb(Util.scanSignal61(Util.mixTrampoline79(-6466867484639169990L)));
    }
""" + HEX + "\n}"
ORACLE = """package %(pkg)s;
public final class Oracle {
    public static void main(String[] a) { System.out.println("oracle=" + Release.code(null)); }
}"""


def xb(s, key=0x2B):
    return ", ".join(str(((ord(c) ^ key ^ i) + 128) % 256 - 128) for i, c in enumerate(s))


rel = {"flat": FLAT, "decoy": FLAT, "reflect": REFLECT, "opaque": OPAQUE, "vm": VM}[variant]
subs = {"pkg": PKG, "top": 56 if variant == "decoy" else 60,
        "n_mix": xb(PKG + ".Mix"), "n_util": xb(PKG + ".Util"), "n_hook": xb(PKG + ".HookScan"),
        "m_f1": xb("f1"), "m_fin": xb("finTrampoline2d"), "m_m79": xb("mixTrampoline79"),
        "m_s61": xb("scanSignal61"), "m_peb": xb("mixPatcheb")}
tmp = Path(tempfile.mkdtemp())
try:
    src, pdir = tmp / "src", tmp / "src" / PKG.replace(".", "/")
    pdir.mkdir(parents=True)
    (tmp / "src/android/content").mkdir(parents=True)
    (tmp / "src/android/content/Context.java").write_text(CTX)
    for n, t in (("Mix", MIX), ("Probe", PROBE), ("Util", UTIL), ("HookScan", HOOK), ("Release", rel),
                 ("Oracle", ORACLE)):
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
                   '"build":"obf%s"}' % variant)
        z.write(tmp / "classes.dex", "classes.dex")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
