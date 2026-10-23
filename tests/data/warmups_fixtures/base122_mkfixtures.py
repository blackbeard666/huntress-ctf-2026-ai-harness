"""Base-122 fixtures from an INDEPENDENT writer/reader: PyPI base122==2026.10.18 (Bart Broere's port of kevinAlbs'
encode.js / decode.js; `pip install --no-deps --target tools/pip-base122 base122==2026.10.18`), run in a separate
python3 -I process. Never lib.warmups_codecs. Run from the repo root:
    python3 tests/data/warmups_fixtures/base122_mkfixtures.py"""
import json, os, subprocess
ROOT = os.getcwd(); LIB = ROOT + "/tools/pip-base122"; OUT = ROOT + "/tests/data/warmups_fixtures/"
SENT = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "
GEN = ("printf %s \"$plain\" | python3 -I -c \"import sys;sys.path.insert(0,'tools/pip-base122');import base122;"
       "sys.stdout.buffer.write(base122.b122encode(sys.stdin.buffer.read()))\"  # PyPI base122==2026.10.18 b122encode "
       "(port of kevinAlbs/Base122 encode.js)")
ORC = ("printf %s \"$encoded\" | python3 -I -c \"import sys;sys.path.insert(0,'tools/pip-base122');import base122;"
       "print(base122.b122decode([ord(c) for c in sys.stdin.buffer.read().decode('utf-8')]).decode('utf-8'))\"  "
       "# PyPI base122==2026.10.18 b122decode (kevinAlbs decode.js port; takes code points, like charCodeAt)")


def py(code, data):
    return subprocess.run(["python3", "-I", "-c", f"import sys;sys.path.insert(0,{LIB!r});import base122;" + code],
                          input=data, capture_output=True)


def enc(p):
    return py("sys.stdout.buffer.write(base122.b122encode(sys.stdin.buffer.read()))", p.encode()).stdout.decode()


def oracle(e):
    r = py("sys.stdout.buffer.write(base122.b122decode([ord(c) for c in sys.stdin.buffer.read().decode('utf-8')]))",
           e.encode())
    if r.returncode:
        return None, "reference decode raises " + r.stderr.decode().strip().splitlines()[-1][:160]
    try:
        return r.stdout.decode("utf-8"), None
    except UnicodeDecodeError as x:
        return None, f"reference decode -> bytes {r.stdout[:12].hex()}..., not UTF-8 text ({x.reason} at {x.start})"


def write(name, plain, encoded, decoy=False, note="", **extra):
    got, err = oracle(encoded)
    fx = {"codec": "base122", "plain": plain, "encoded": encoded, **extra}
    if decoy:
        fx.update(decoy=True, expected="none", generator_cmd=note, oracle_cmd=ORC + f"  -> rejects: {err}",
                  oracle_plain=got)
        assert got is None or not got.isprintable(), (name, got)
    else:
        fx.update(expected="match", generator_cmd=GEN + note, oracle_cmd=ORC, oracle_plain=got)
        assert got == plain, (name, got)
    json.dump(fx, open(OUT + name + ".json", "w"), indent=1, ensure_ascii=False)
    print(name, fx["expected"], len(encoded.encode()), "bytes")


single = enc(SENT + "maple-otter-41")
write("base122-maple", SENT + "maple-otter-41", single)
write("base122-cobalt", SENT + "cobalt-heron-27", enc(SENT + "cobalt-heron-27"))
write("base122-fragment-amber", "amber-fox-17", enc("amber-fox-17"),
      note="  -- Mastery-style fragment: an illegal-index pair (U+04AB) mid-line and a shortened (sss=7) last char U+07DC")
raw = enc(SENT + "jade-lynx-58").encode()
open(OUT + "base122-raw-jade.bin", "wb").write(raw)
write("base122-raw-jade", SENT + "jade-lynx-58", enc(SENT + "jade-lynx-58"), encoded_file="base122-raw-jade.bin",
      encoded_latin1=raw.decode("latin-1"),
      note=" > base122-raw-jade.bin  -- raw UTF-8 bytes artifact; encoded_latin1 = the same bytes read as Latin-1 "
           "(mojibake a bytes->text reader produces)")
write("base122-decoy-misaligned", None, single[1:], decoy=True,
      note="base122-maple's encoded with its first char dropped (every 7-bit group shifted): decodes to non-UTF-8 bytes")
b2048 = json.load(open(OUT + "base2048-clover.json"))["encoded"]
write("base122-decoy-base2048", None, b2048, decoy=True,
      note="base2048-clover.json's encoded (qntm npm base2048): another dense U+0080..U+0FFF packing, not base122")
