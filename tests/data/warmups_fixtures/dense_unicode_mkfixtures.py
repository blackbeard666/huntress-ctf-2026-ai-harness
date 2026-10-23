import json, subprocess, sys, os
ROOT = os.getcwd(); NM = ROOT + "/tools/npm-base65536/node_modules"; PY = sys.argv[1]
OUT = ROOT + "/tests/data/warmups_fixtures/"
GEN = ("printf %%s \"$plain\" | tools/node/bin/node --input-type=module -e \"import {encode} from './tools/npm-base65536/node_modules/%s/src/index.js';"
       "import fs from 'fs';process.stdout.write(encode(fs.readFileSync(0)))\"  # qntm reference npm %s@%s encode")
NODE_DEC = ("printf %%s \"$encoded\" | tools/node/bin/node --input-type=module -e \"import {decode} from './tools/npm-base65536/node_modules/%s/src/index.js';"
            "import fs from 'fs';process.stdout.write(Buffer.from(decode(fs.readFileSync(0,'utf8'))).toString())\"  # qntm reference npm %s@%s decode")
PYDEC = {"base65536": "printf %s \"$encoded\" | python3 -I -c \"import sys;sys.path.insert(0,'$PYLIB');import base65536;print(base65536.decode(sys.stdin.read()).decode())\"  # sublee PyPI base65536==0.1.1 (+six) decode, pip install --target $PYLIB"}
VER = {"base65536": "5.0.1", "base32768": "3.0.0", "base2048": "5.0.0"}
for c in VER:
    VER[c] = json.load(open(f"{NM}/{c}/package.json"))["version"]

def enc(c, p):
    js = f"import {{encode}} from '{NM}/{c}/src/index.js';import fs from 'fs';process.stdout.write(encode(fs.readFileSync(0)))"
    return subprocess.run(["node", "--input-type=module", "-e", js], input=p.encode(), capture_output=True, check=True).stdout.decode()

def oracle(c, e):
    if c in PYDEC:
        code = f"import sys;sys.path.insert(0,{PY!r});import {c};sys.stdout.write({c}.decode(sys.stdin.read()).decode())"
        r = subprocess.run(["python3", "-I", "-c", code], input=e.encode(), capture_output=True)
    else:
        js = f"import {{decode}} from '{NM}/{c}/src/index.js';import fs from 'fs';process.stdout.write(Buffer.from(decode(fs.readFileSync(0,'utf8'))).toString('latin1'))"
        r = subprocess.run(["node", "--input-type=module", "-e", js], input=e.encode(), capture_output=True)
        if r.returncode == 0:
            r.stdout = r.stdout.decode().encode("latin1")   # raw bytes back; .decode() below = strict UTF-8 check
    if r.returncode:
        return None, [l for l in r.stderr.decode().splitlines() if 'Error' in l][-1].strip()[:160]
    try:
        return r.stdout.decode("utf-8"), None
    except UnicodeDecodeError:
        return None, "decodes to non-UTF-8 bytes " + r.stdout[:16].hex()

def ocmd(c):
    return PYDEC[c] if c in PYDEC else NODE_DEC % (c, c, VER[c])

S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "
pos = [("base65536", "cobalt", S + "cobalt-heron-17"), ("base65536", "fragment-amber", "amber-"),
       ("base32768", "maple", S + "maple-otter-58"), ("base32768", "fragment-jade", "jade-lynx"),
       ("base2048", "clover", S + "clover-badger-93"), ("base2048", "fragment-ivory", "-ivory-")]
for c, tag, p in pos:
    e = enc(c, p); o, err = oracle(c, e)
    assert o == p, (c, tag, o, err)
    json.dump({"codec": c, "plain": p, "encoded": e, "expected": "match", "generator_cmd": GEN % (c, c, VER[c]),
               "oracle_cmd": ocmd(c), "oracle_plain": o}, open(OUT + f"{c}-{tag}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(c, tag, len(p), len(e))

full = enc("base32768", S + "maple-otter-58")
decoys = [("base65536", "cjk-prose", "我们今天去公园散步吧天气很好",
           "hand-written decoy: plain Chinese prose (U+4E00..U+9EFF, inside the base65536 repertoire) -- decodes to non-text bytes"),
          ("base32768", "truncated-tail", full[:-1],
           "base32768 sentence from the generator above with its final (padding) char dropped -- truncated, padding bits no longer all 1s"),
          ("base2048", "thai-prose", "สวัสดีครับยินดีต้อนรับ",
           "hand-written decoy: Thai prose -- its combining vowel signs (U+0E31/U+0E35/U+0E34/U+0E49) are outside the base2048 repertoire")]
for c, tag, e, how in decoys:
    o, err = oracle(c, e)
    assert o is None or not o.isprintable(), (c, o)
    json.dump({"codec": c, "plain": None, "encoded": e, "decoy": True, "expected": "none", "generator_cmd": how,
               "oracle_cmd": ocmd(c) + f"  -> rejects: {err}", "oracle_plain": None},
              open(OUT + f"{c}-decoy-{tag}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(c, "decoy", tag, err)
