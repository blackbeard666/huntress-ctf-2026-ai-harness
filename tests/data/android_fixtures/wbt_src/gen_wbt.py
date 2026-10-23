#!/usr/bin/env python3
"""White-box / table-driven cipher fixtures (coverage atlas: whitebox-table-cipher-eval).

  gen_wbt.py tbox_aes   out.apk  # AES-128 decrypt as a T-table walk (Td0..Td3 int[256], Td4 byte[256], round keys
                                 #  folded into int[44]); ciphertext in assets/wb.bin, read by an InputStream caller
  gen_wbt.py sbox_chain out.apk  # 4 chained byte[256] S-boxes + position xor, static byte[] CT, caller needs a Context
  gen_wbt.py sbox_asset out.apk  # sbox_chain tables, ciphertext as hex text in assets/blob.txt (read by a caller)
  gen_wbt.py decoy      out.apk  # sbox_chain layout, plaintext is a near-miss (14 hex digits)

Java source -> javac --release 8 -> dex2jar d2j-jar2dex -> zipfile. The oracle is the host JVM running the shipped
decrypt (Probe) and, for tbox_aes, `openssl enc -d -aes-128-ecb -nopad` on the asset bytes."""
import os, random, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

from Crypto.Cipher import AES  # pycryptodome: only to produce the ciphertext (the writer)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
variant, out = sys.argv[1], Path(sys.argv[2])
PKG = "com.huntress.wb"
TOK = {"tbox_aes": "ANS-5e0b7a93c1d26f48", "sbox_chain": "ANS-b3d91f0e6a2c4875", "sbox_asset": "ANS-90d7e2c41b5f3a68", "decoy": "ANS-4f1c2d9e7b30a5x8"}[variant]


def sbox():
    p, q = [0] * 256, [0] * 256
    inv = lambda a: 0 if a == 0 else pow_gf(a, 254)  # noqa: E731
    for x in range(256):
        b = inv(x)
        s = b
        for k in range(1, 5):
            s ^= ((b << k) | (b >> (8 - k))) & 0xFF
        p[x] = s ^ 0x63
    for x in range(256):
        q[p[x]] = x
    return p, q


def mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = ((a << 1) ^ (0x11B if a & 0x80 else 0)) & 0xFF
        b >>= 1
    return r


def pow_gf(a, e):
    r = 1
    while e:
        if e & 1:
            r = mul(r, a)
        a = mul(a, a)
        e >>= 1
    return r


def jb(v):
    return ", ".join(str((x ^ 0x80) - 0x80) for x in v)


def ji(v):
    return ", ".join(str(x - (1 << 32) if x >> 31 else x) for x in v)


def aes_java(key):
    S, IS = sbox()
    td = []
    for sh in (24, 16, 8, 0):
        t = []
        for x in range(256):
            s = IS[x]
            w = (mul(s, 14) << 24) | (mul(s, 9) << 16) | (mul(s, 13) << 8) | mul(s, 11)
            t.append(((w >> (24 - sh)) | (w << (8 + sh))) & 0xFFFFFFFF if sh != 24 else w)
        td.append(t)
    # Td1 = ror8(Td0) etc.: recompute explicitly
    ror = lambda w, n: ((w >> n) | (w << (32 - n))) & 0xFFFFFFFF  # noqa: E731
    td = [td[0], [ror(w, 8) for w in td[0]], [ror(w, 16) for w in td[0]], [ror(w, 24) for w in td[0]]]
    rc, w = 1, [int.from_bytes(key[4 * i:4 * i + 4], "big") for i in range(4)]
    for i in range(4, 44):
        t = w[i - 1]
        if i % 4 == 0:
            t = ((S[(t >> 16) & 255] << 24) | (S[(t >> 8) & 255] << 16) | (S[t & 255] << 8) | S[t >> 24]) ^ (rc << 24)
            rc = mul(rc, 2)
        w.append(w[i - 4] ^ t)
    # equivalent inverse cipher key schedule: reverse rounds, InvMixColumns on rounds 1..9
    dk = []
    for r in range(10, -1, -1):
        for c in range(4):
            x = w[4 * r + c]
            if 0 < r < 10:
                x = td[0][S[x >> 24]] ^ td[1][S[(x >> 16) & 255]] ^ td[2][S[(x >> 8) & 255]] ^ td[3][S[x & 255]]
            dk.append(x)
    return f"""package {PKG};
public final class WhiteBox {{
    static final int[] Td0 = {{ {ji(td[0])} }};
    static final int[] Td1 = {{ {ji(td[1])} }};
    static final int[] Td2 = {{ {ji(td[2])} }};
    static final int[] Td3 = {{ {ji(td[3])} }};
    static final byte[] Td4 = {{ {jb(IS)} }};
    static final int[] RK = {{ {ji(dk)} }};
    static int w(byte[] b, int o) {{ return ((b[o] & 0xff) << 24) | ((b[o + 1] & 0xff) << 16) | ((b[o + 2] & 0xff) << 8) | (b[o + 3] & 0xff); }}
    static void put(byte[] b, int o, int v) {{ b[o] = (byte) (v >>> 24); b[o + 1] = (byte) (v >>> 16); b[o + 2] = (byte) (v >>> 8); b[o + 3] = (byte) v; }}
    static int last(int a, int b, int c, int d, int k) {{
        return ((Td4[a >>> 24] & 0xff) << 24 | (Td4[(b >>> 16) & 0xff] & 0xff) << 16 | (Td4[(c >>> 8) & 0xff] & 0xff) << 8 | (Td4[d & 0xff] & 0xff)) ^ k;
    }}
    public static byte[] decrypt(byte[] in) {{
        byte[] out = new byte[in.length];
        for (int o = 0; o + 16 <= in.length; o += 16) {{
            int s0 = w(in, o) ^ RK[0], s1 = w(in, o + 4) ^ RK[1], s2 = w(in, o + 8) ^ RK[2], s3 = w(in, o + 12) ^ RK[3];
            int k = 4;
            for (int r = 1; r < 10; r++) {{
                int t0 = Td0[s0 >>> 24] ^ Td1[(s3 >>> 16) & 0xff] ^ Td2[(s2 >>> 8) & 0xff] ^ Td3[s1 & 0xff] ^ RK[k];
                int t1 = Td0[s1 >>> 24] ^ Td1[(s0 >>> 16) & 0xff] ^ Td2[(s3 >>> 8) & 0xff] ^ Td3[s2 & 0xff] ^ RK[k + 1];
                int t2 = Td0[s2 >>> 24] ^ Td1[(s1 >>> 16) & 0xff] ^ Td2[(s0 >>> 8) & 0xff] ^ Td3[s3 & 0xff] ^ RK[k + 2];
                int t3 = Td0[s3 >>> 24] ^ Td1[(s2 >>> 16) & 0xff] ^ Td2[(s1 >>> 8) & 0xff] ^ Td3[s0 & 0xff] ^ RK[k + 3];
                s0 = t0; s1 = t1; s2 = t2; s3 = t3; k += 4;
            }}
            put(out, o, last(s0, s3, s2, s1, RK[40]));
            put(out, o + 4, last(s1, s0, s3, s2, RK[41]));
            put(out, o + 8, last(s2, s1, s0, s3, RK[42]));
            put(out, o + 12, last(s3, s2, s1, s0, RK[43]));
        }}
        return out;
    }}
    public static String reveal(java.io.InputStream asset) throws java.io.IOException {{
        byte[] buf = new byte[asset.available()];
        asset.read(buf);
        byte[] p = decrypt(buf);
        int n = p.length - p[p.length - 1];
        return new String(p, 0, n, "UTF-8");
    }}
}}
"""


def chain_java(plain, asset=None):
    rnd = random.Random(0x5B0C)
    boxes = []
    for _ in range(4):
        p = list(range(256))
        rnd.shuffle(p)
        boxes.append(p)
    keys = [rnd.randrange(256) for _ in range(4)]
    # forward (what the build server ran): c = F4(F3(F2(F1(p ^ k1 ^ i) ^ k2) ^ k3) ^ k4) -> app ships the inverses
    ct = []
    for i, x in enumerate(plain):
        v = x
        for r in range(4):
            v = boxes[r][(v ^ keys[r] ^ (i if r == 0 else 0)) & 0xFF]
        ct.append(v)
    inv = []
    for p in boxes:
        q = [0] * 256
        for a, b in enumerate(p):
            q[b] = a
        inv.append(q)
    if asset is not None:
        asset["assets/blob.txt"] = bytes(ct).hex().encode() + b"\n"
        ct = [0]
    return f"""package {PKG};
public final class WhiteBox {{
    static final byte[] I1 = {{ {jb(inv[0])} }};
    static final byte[] I2 = {{ {jb(inv[1])} }};
    static final byte[] I3 = {{ {jb(inv[2])} }};
    static final byte[] I4 = {{ {jb(inv[3])} }};
    static final byte[] CT = {{ {jb(ct)} }};
    public static byte[] decrypt(byte[] c) {{
        byte[] o = new byte[c.length];
        for (int i = 0; i < c.length; i++) {{
            int v = I4[c[i] & 0xff] & 0xff ^ {keys[3]};
            v = I3[v] & 0xff ^ {keys[2]};
            v = I2[v] & 0xff ^ {keys[1]};
            v = (I1[v] & 0xff) ^ {keys[0]} ^ (i & 0xff);
            o[i] = (byte) v;
        }}
        return o;
    }}
    public static void show(Object ctx) {{
        String s = new String(decrypt(CT));
        ctx.notifyAll();
        System.out.println(s);
    }}
}}
"""


PROBE = """package %s;
public final class Probe { public static void main(String[] a) throws Exception { %s } }
"""
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src" / PKG.replace(".", "/"), tmp / "cls"
src.mkdir(parents=True)
cls.mkdir()
assets = {}
if variant == "tbox_aes":
    key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    pt = TOK.encode() + bytes([12]) * 12
    assets["assets/wb.bin"] = AES.new(key, AES.MODE_ECB).encrypt(pt)
    (tmp / "wb.bin").write_bytes(assets["assets/wb.bin"])
    (src / "WhiteBox.java").write_text(aes_java(key))
    body = f'System.out.println(WhiteBox.reveal(new java.io.FileInputStream("{tmp / "wb.bin"}")));'
elif variant == "sbox_asset":
    (src / "WhiteBox.java").write_text(chain_java(TOK.encode(), assets))
    (tmp / "blob.txt").write_bytes(assets["assets/blob.txt"])
    body = (f'byte[] h = java.nio.file.Files.readAllBytes(java.nio.file.Paths.get("{tmp / "blob.txt"}"));'
            ' byte[] c = new byte[(h.length - 1) / 2];'
            ' for (int i = 0; i < c.length; i++) c[i] = (byte) Integer.parseInt(new String(h, 2 * i, 2), 16);'
            ' System.out.println(new String(WhiteBox.decrypt(c)));')
else:
    (src / "WhiteBox.java").write_text(chain_java(TOK.encode()))
    body = "System.out.println(new String(WhiteBox.decrypt(WhiteBox.CT)));"
(src / "Probe.java").write_text(PROBE % (PKG, body))
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.glob("*.java"))], check=True)
shown = subprocess.run(["java", "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout
if variant == "tbox_aes":
    ossl = subprocess.run(["openssl", "enc", "-d", "-aes-128-ecb", "-nopad", "-K", key.hex(), "-in", str(tmp / "wb.bin")],
                          check=True, capture_output=True).stdout
    print(f"openssl-d={ossl[:20]!r}")
(cls / PKG.replace(".", "/") / "Probe.class").unlink()
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
    for k, v in assets.items():
        z.writestr(k, v)
shutil.rmtree(tmp)
print(f"JVM decrypt={shown.strip()!r}")
