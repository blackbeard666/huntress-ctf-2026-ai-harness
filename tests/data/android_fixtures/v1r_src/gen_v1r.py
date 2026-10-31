"""v1 codec registry regression (D1-D30 every v1 `huntress_puzzle.json` shape, keys re-rolled) -> v1r_*.{apk,zip,json}.

Writer: python zipfile (APK/apks containers) + javac/d2j-jar2dex (dynamic payload dex) + gcc (native .so).
Oracle: each fixture's `oracle_cmd` is an independent shell pipeline (unzip -p | jq | base64/xxd/rev/python -c, or
strings on the pointed entry) that this generator RUNS and asserts equals the rolled token; expected = the oracle output.
Run:  python3 tests/data/android_fixtures/v1r_src/gen_v1r.py   (from the repo root; deterministic seed)
"""
import base64, json, random, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "tests/data/android_fixtures"
rng = random.Random(0x5131)
TMP = Path(tempfile.mkdtemp())
MANIFEST = b'<?xml version="1.0" encoding="utf-8"?>\n<manifest package="com.huntress.arena" />\n'


def tok():
    return "ANS-" + "".join(rng.choice("0123456789ABCDEF") for _ in range(16))


def pz(day, codec, data, **kw):
    d = {"schema": "huntress.mobile.puzzle.v1", "day": day, "codec": codec, "data": data}
    d.update(kw)
    return json.dumps(d, separators=(",", ":")).encode()


def apk(path, puzzle, extra=()):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("AndroidManifest.xml", MANIFEST)
        z.writestr("assets/huntress_puzzle.json", puzzle)
        for n, b in extra:
            z.writestr(n, b)


J = "unzip -p {f} assets/huntress_puzzle.json | jq -r"
PY = "python3 -I -c"
fixtures = []  # (name, suffix, builder(path)->None, oracle_cmd template with {f}, decoy, why)


def add(name, why, build, oracle, decoy=False, suffix=".apk"):
    fixtures.append((name, suffix, build, oracle, decoy, why))


def xb(b, ks):
    return bytes(x ^ ks(i) for i, x in enumerate(b))


# --- the 15 v1 codecs, keys re-rolled -------------------------------------------------------------------------------
t = tok(); add("v1r_plain", "D1 plain", lambda p, t=t: apk(p, pz(1, "plain", t)), J + " .data")
t = tok(); add("v1r_reverse", "D2/D21 reverse", lambda p, t=t: apk(p, pz(2, "reverse", t[::-1])), J + " .data | rev")
t = tok(); add("v1r_base64", "D3/D9/D13/D22/D27 base64",
               lambda p, t=t: apk(p, pz(3, "base64", base64.b64encode(t.encode()).decode())), J + " .data | base64 -d")
t = tok(); add("v1r_hex_lower", "D12/D25 hex (lowercase)",
               lambda p, t=t: apk(p, pz(12, "hex", t.encode().hex())), J + " .data | xxd -r -p")
t = tok(); add("v1r_hex_upper", "hex, uppercase digits (re-roll of D12)",
               lambda p, t=t: apk(p, pz(25, "hex", t.encode().hex().upper())), J + " .data | xxd -r -p")
k = rng.randrange(1, 256); t = tok()
add("v1r_xor_b64", f"D11/D18/D23 xor = base64 + 1-byte key {k}",
    lambda p, t=t, k=k: apk(p, pz(18, "xor", base64.b64encode(xb(t.encode(), lambda i: k)).decode(), key=k)),
    J + " -c '[.data,.key]' | " + PY + " 'import sys,json,base64;d,k=json.load(sys.stdin);print(bytes(b^k for b in base64.b64decode(d)).decode())'")
k = rng.randrange(2, 30); t = tok()
add("v1r_caesar_plus", f"D7/D14 caesar: code point + key {k}",
    lambda p, t=t, k=k: apk(p, pz(7, "caesar", "".join(chr(ord(c) + k) for c in t), key=k)),
    J + " -r '.data, .key' | " + PY + " 'import sys;d,k=sys.stdin.read().split(chr(10))[:2];print(\"\".join(chr(ord(c)-int(k)) for c in d))'")
k = rng.randrange(2, 30); t = tok()
add("v1r_caesar_negkey", f"caesar with a NEGATIVE declared key -{k} (code point - {k})",
    lambda p, t=t, k=k: apk(p, pz(14, "caesar", "".join(chr(ord(c) - k) for c in t), key=-k)),
    J + " -r '.data, .key' | " + PY + " 'import sys;d,k=sys.stdin.read().split(chr(10))[:2];print(\"\".join(chr(ord(c)-int(k)) for c in d))'")
k = rng.randrange(2, 30); t = tok()
add("v1r_caesar_minus", f"caesar shifted the OTHER way: code point - key {k}, key declared +{k}",
    lambda p, t=t, k=k: apk(p, pz(14, "caesar", "".join(chr(ord(c) - k) for c in t), key=k)),
    J + " -r '.data, .key' | " + PY + " 'import sys;d,k=sys.stdin.read().split(chr(10))[:2];print(\"\".join(chr(ord(c)+int(k)) for c in d))'")


def split_parts(t, n):
    cuts = sorted(rng.sample(range(1, len(t)), n - 1))
    pieces = [t[a:b] for a, b in zip([0] + cuts, cuts + [len(t)])]
    order = list(range(n)); rng.shuffle(order)
    parts = [None] * n
    for i in range(n):
        parts[i] = pieces[order[i]]  # r[order[i]] = parts[i]
    return parts, order


ASM = PY + " 'import sys,json;p=json.load(sys.stdin);r=[None]*len(p[\"order\"])\nfor i,o in enumerate(p[\"order\"]): r[o]=p[\"parts\"][i]\nprint(\"\".join(r))'"
t = tok(); parts, order = split_parts(t, 3)
add("v1r_split3", f"D5/D10/D24 split, re-rolled cuts + order {order}",
    lambda p, t=t, pa=parts, o=order: apk(p, pz(5, "split", "", parts=pa, order=o)), "unzip -p {f} assets/huntress_puzzle.json | " + ASM)
t = tok(); parts, order = split_parts(t, 4)
add("v1r_split4", f"split into 4 parts, order {order}",
    lambda p, t=t, pa=parts, o=order: apk(p, pz(24, "split", "", parts=pa, order=o)), "unzip -p {f} assets/huntress_puzzle.json | " + ASM)

t = tok(); parts, order = split_parts(t, 3)
hole = rng.randrange(3)


def build_apks(p, t=t, pa=parts, o=order, hole=hole):
    base, feat = TMP / "base.apk", TMP / "feature.apk"
    bp = list(pa); bp[hole] = ""
    apk(base, pz(26, "split", "", parts=bp, order=o))
    with zipfile.ZipFile(feat, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("AndroidManifest.xml", b'<?xml version="1.0"?>\n<manifest package="com.huntress.arena" split="arena_feature" />\n')
        z.writestr("assets/huntress_feature.json", json.dumps({"part": pa[hole], "part_index": hole}))
    with zipfile.ZipFile(p, "w", zipfile.ZIP_STORED) as z:
        z.write(base, "base.apk"); z.write(feat, "feature.apk")


add("v1r_split_feature_slot", f"D26 .apks: base split with EMPTY slot {hole}, filled from feature.apk huntress_feature.json",
    build_apks,
    "d=$(mktemp -d); unzip -q -o {f} -d $d; " + PY + " 'import sys,json,zipfile;b=json.loads(zipfile.ZipFile(sys.argv[1]).read(\"assets/huntress_puzzle.json\"));f=json.loads(zipfile.ZipFile(sys.argv[2]).read(\"assets/huntress_feature.json\"));b[\"parts\"][f[\"part_index\"]]=f[\"part\"];r=[None]*3\nfor i,o in enumerate(b[\"order\"]): r[o]=b[\"parts\"][i]\nprint(\"\".join(r))' $d/base.apk $d/feature.apk",
    suffix=".zip")

IDX = PY + " 'import sys,json;p=json.load(sys.stdin);r=[\"\"]*len(p[\"data\"])\nfor i,o in enumerate(p[\"order\"]): r[o]=p[\"data\"][i]\nprint(\"\".join(r))'"
for nm, a, b in (("v1r_indexed_d17", 3, 7), ("v1r_indexed_reroll", rng.choice([1, 5, 9, 11, 13]), rng.choice([3, 9, 11, 13, 17]))):
    t = tok(); order = [(a + b * i) % 20 for i in range(20)]
    add(nm, f"D17 indexed order ({a}+{b}i)%20: data[i] = token[order[i]]",
        lambda p, t=t, o=order: apk(p, pz(17, "indexed", "".join(t[o[i]] for i in range(20)), order=o)),
        "unzip -p {f} assets/huntress_puzzle.json | " + IDX)

t = tok()
add("v1r_reflection", "D19 reflection: data is the plaintext answer", lambda p, t=t: apk(p, pz(19, "reflection", t)), J + " .data")


def build_native(p, t=t):
    src = TMP / "n.c"
    src.write_text('const char arena_value[] = "%s";\nconst char *arena(void){return arena_value;}\n' % t)
    so = TMP / "libarena.so"
    subprocess.run(["gcc", "-shared", "-fPIC", "-O2", "-s", "-o", str(so), str(src)], check=True)
    apk(p, pz(15, "native", t), extra=[("lib/x86_64/libarena.so", so.read_bytes())])


t2 = tok()
add("v1r_native", "D15/D16 native: plaintext in data + .rodata literal in lib/x86_64/libarena.so (gcc)",
    lambda p, t=t2: build_native(p, t), J + " .data")


def build_dynamic(p, t, entry):
    src = TMP / "dyn/com/huntress/arena/payload"; src.mkdir(parents=True, exist_ok=True)
    (src / "Module.java").write_text('package com.huntress.arena.payload;\npublic class Module {\n'
                                     '  public static final String ANSWER = "%s";\n  public static String contract() { return ANSWER; }\n}\n' % t)
    cls = TMP / "dyncls"; shutil.rmtree(cls, ignore_errors=True)
    subprocess.run(["javac", "--release", "8", "-d", str(cls), str(src / "Module.java")], check=True)
    jar = TMP / "dyn.zip"
    shutil.make_archive(str(jar)[:-4], "zip", cls)
    dex = TMP / "payload.dex"
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(dex), str(jar)], check=True, capture_output=True)
    apk(p, pz(20, "dynamic", entry), extra=[(entry, dex.read_bytes())])


t = tok(); entry = "assets/" + rng.choice(["payload", "module", "stage2"]) + ".dex"
add("v1r_dynamic", f"D20 dynamic: data = entry path {entry} (javac + d2j-jar2dex dex holding the token)",
    lambda p, t=t, e=entry: build_dynamic(p, t, e),
    "unzip -p {f} $(unzip -p {f} assets/huntress_puzzle.json | jq -r .data) | strings -a | grep -oE 'ANS-[0-9A-F]{{16}}'")


def frame(t):
    b = b"HA" + bytes([len(t)]) + t.encode()
    c = 0
    for x in b:
        c ^= x
    return (b + bytes([c])).hex()


t = tok()
add("v1r_packet", "D28 packet: hex of HA | u8 len | ascii | xor checksum",
    lambda p, t=t: apk(p, pz(28, "packet", frame(t))),
    J + " .data | xxd -r -p | " + PY + " 'import sys;b=sys.stdin.buffer.read();print(b[3:3+b[2]].decode())'")
k = rng.randrange(1, 200); t = tok()
add("v1r_table", f"D29 table: hex of (b + key + 3i) & 255, key {k}",
    lambda p, t=t, k=k: apk(p, pz(29, "table", bytes((c + k + 3 * i) & 255 for i, c in enumerate(t.encode())).hex(), key=k)),
    J + " -r '.data, .key' | " + PY + " 'import sys;d,k=sys.stdin.read().split(chr(10))[:2];k=int(k);print(bytes((c-(k+3*i))&255 for i,c in enumerate(bytes.fromhex(d))).decode())'")
k = rng.randrange(1, 200); t = tok()
add("v1r_layered", f"D30 layered: base64( (reverse(token))[i] ^ (key+i) ), key {k}",
    lambda p, t=t, k=k: apk(p, pz(30, "layered", base64.b64encode(xb(t.encode()[::-1], lambda i: (k + i) & 255)).decode(), key=k)),
    J + " -r '.data, .key' | " + PY + " 'import sys,base64;d,k=sys.stdin.read().split(chr(10))[:2];k=int(k);print(bytes(c^((k+i)&255) for i,c in enumerate(base64.b64decode(d)))[::-1].decode())'")

# --- stacks of v1 steps (finale may chain any of them) --------------------------------------------------------------
t = tok()
add("v1r_stack_hex_reverse_b64", "stack: base64 -> reverse -> hex (decode: unhex, reverse, b64decode)",
    lambda p, t=t: apk(p, pz(31, "stack", base64.b64encode(t.encode()).decode()[::-1].encode().hex())),
    J + " .data | xxd -r -p | rev | base64 -d")
k = rng.randrange(1, 256); t = tok()
add("v1r_stack_xor_hex", f"stack: 1-byte xor {k} then hex (xor without base64)",
    lambda p, t=t, k=k: apk(p, pz(31, "xorhex", xb(t.encode(), lambda i: k).hex(), key=k)),
    J + " -r '.data, .key' | " + PY + " 'import sys;d,k=sys.stdin.read().split(chr(10))[:2];print(bytes(c^int(k) for c in bytes.fromhex(d)).decode())'")
k = rng.randrange(2, 20); t = tok()
add("v1r_stack_caesar_b64", f"stack: base64 of the caesar(+{k}) text",
    lambda p, t=t, k=k: apk(p, pz(31, "caesar64", base64.b64encode("".join(chr(ord(c) + k) for c in t).encode()).decode(), key=k)),
    J + " -r '.data, .key' | " + PY + " 'import sys,base64;d,k=sys.stdin.read().split(chr(10))[:2];print(\"\".join(chr(ord(c)-int(k)) for c in base64.b64decode(d).decode()))'")
k = rng.randrange(1, 200); t = tok()
add("v1r_stack_table_reverse", f"stack: D29 table then reverse of the hex string, key {k}",
    lambda p, t=t, k=k: apk(p, pz(31, "tablerev", bytes((c + k + 3 * i) & 255 for i, c in enumerate(t.encode())).hex()[::-1], key=k)),
    J + " -r '.data, .key' | " + PY + " 'import sys;d,k=sys.stdin.read().split(chr(10))[:2];k=int(k);print(bytes((c-(k+3*i))&255 for i,c in enumerate(bytes.fromhex(d[::-1]))).decode())'")
k = rng.randrange(1, 200); t = tok()
add("v1r_stack_layered_hex", f"stack: D30 layered but hex outer instead of base64, key {k}",
    lambda p, t=t, k=k: apk(p, pz(31, "layered", xb(t.encode()[::-1], lambda i: (k + i) & 255).hex(), key=k)),
    J + " -r '.data, .key' | " + PY + " 'import sys;d,k=sys.stdin.read().split(chr(10))[:2];k=int(k);print(bytes(c^((k+i)&255) for i,c in enumerate(bytes.fromhex(d)))[::-1].decode())'")
t = tok(); order = [(3 + 7 * i) % 20 for i in range(20)]
add("v1r_stack_indexed_b64", "stack: D17 indexed permutation, then base64 of the permuted text",
    lambda p, t=t, o=order: apk(p, pz(31, "indexed64", base64.b64encode("".join(t[o[i]] for i in range(20)).encode()).decode(), order=o)),
    "unzip -p {f} assets/huntress_puzzle.json | " + PY + " 'import sys,json,base64;p=json.load(sys.stdin);d=base64.b64decode(p[\"data\"]).decode();r=[\"\"]*20\nfor i,o in enumerate(p[\"order\"]): r[o]=d[i]\nprint(\"\".join(r))'")

# --- decoys: same layouts, near-miss tokens (15 hex + non-hex) ------------------------------------------------------
nm = "ANS-" + "".join(rng.choice("0123456789ABCDEF") for _ in range(15)) + "G"
k = rng.randrange(1, 256)
add("v1r_decoy_xor_nearmiss", "DECOY: xor b64 of a 15-hex + 'G' near-miss",
    lambda p, k=k: apk(p, pz(18, "xor", base64.b64encode(xb(nm.encode(), lambda i: k)).decode(), key=k)),
    J + " -c '[.data,.key]' | " + PY + " 'import sys,json,base64,re;d,k=json.load(sys.stdin);s=bytes(b^k for b in base64.b64decode(d)).decode();print(re.findall(\"ANS-[0-9A-Fa-f]{{16}}\",s) or \"none\")'",
    decoy=True)
k = rng.randrange(1, 200)
add("v1r_decoy_layered_nearmiss", "DECOY: D30 layered of a near-miss token",
    lambda p, k=k: apk(p, pz(30, "layered", base64.b64encode(xb(nm.encode()[::-1], lambda i: (k + i) & 255)).decode(), key=k)),
    J + " -r '.data, .key' | " + PY + " 'import sys,base64,re;d,k=sys.stdin.read().split(chr(10))[:2];k=int(k);s=bytes(c^((k+i)&255) for i,c in enumerate(base64.b64decode(d)))[::-1].decode();print(re.findall(\"ANS-[0-9A-Fa-f]{{16}}\",s) or \"none\")'",
    decoy=True)
parts, order = split_parts(nm, 3)
add("v1r_decoy_split_nearmiss", "DECOY: split whose assembly is a near-miss token",
    lambda p, pa=parts, o=order: apk(p, pz(5, "split", "", parts=pa, order=o)),
    "unzip -p {f} assets/huntress_puzzle.json | " + ASM + " | grep -oE 'ANS-[0-9A-Fa-f]{{16}}' || echo none", decoy=True)

only = set(sys.argv[1:])
for name, suf, build, oracle, decoy, why in fixtures:
    if only and name not in only:
        continue
    path = OUT / (name + suf)
    build(path)
    rel = path.relative_to(ROOT)
    cmd = oracle.format(f=rel)
    got = subprocess.run(["bash", "-c", cmd], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if decoy:
        assert "ANS-" not in got or got == "none", (name, got)
        exp = None
    else:
        assert re.fullmatch(r"ANS-[0-9A-F]{16}", got), (name, got)
        exp = got
    fx = {"entry": "puzzle_candidates", "expected": exp, "decoy": decoy, "_why": why,
          "generator_cmd": f"python3 tests/data/android_fixtures/v1r_src/gen_v1r.py {name}  # python zipfile (+gcc .so / javac+d2j-jar2dex dex)",
          "oracle_cmd": cmd}
    (OUT / (name + ".json")).write_text(json.dumps(fx, indent=1) + "\n")
    print(f"{name:32s} {exp}")
shutil.rmtree(TMP, ignore_errors=True)
