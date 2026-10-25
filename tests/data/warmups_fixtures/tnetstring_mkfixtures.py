"""Offline generator for tests/data/warmups_fixtures/tnetstring-*.json.
Writer AND oracle: the reference tnetstring3 library (rfk's tnetstring, py3 port; pip install --target
tools/pylib-tnet tnetstring3) -- never lib.warmups_codecs. Run: python3 -I tests/data/warmups_fixtures/tnetstring_mkfixtures.py"""
import json
import os
import sys

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(D, "..", "..", "..", "tools", "pylib-tnet"))
import tnetstring as T  # noqa: E402

GEN = "python3 -I -c \"import sys; sys.path.insert(0,'tools/pylib-tnet'); import tnetstring as T; plain=sys.argv[1]; " \
      "sys.stdout.buffer.write(T.dumps({expr}))\" \"$plain\""
ORACLE = ("python3 -I -c \"import sys; sys.path.insert(0,'tools/pylib-tnet'); import tnetstring as T\n"
          "def w(v):\n"
          " if isinstance(v,bytes): return v.decode()\n"
          " if isinstance(v,list): return ''.join(w(x) for x in v) if any(not isinstance(x,int) for x in v) else ''.join(map(chr,v))\n"
          " if isinstance(v,dict): return ''.join(w(v[k]) for k in sorted(v, key=int))\n"
          " return ''\n"
          "d=sys.stdin.buffer.read().strip(); v,r=T.pop(d)\n"
          "assert not r.strip(), 'trailing bytes'\n"
          "print(w(v), end='')\"")


def oracle(enc):
    """The same reader as ORACLE (tnetstring3.pop over the WHOLE text), run in-process."""
    def w(v):
        if isinstance(v, bytes):
            return v.decode()
        if isinstance(v, list):
            return "".join(w(x) for x in v) if any(not isinstance(x, int) for x in v) else "".join(map(chr, v))
        if isinstance(v, dict):
            return "".join(w(v[k]) for k in sorted(v, key=int))
        return ""
    try:
        v, r = T.pop(enc.encode("utf-8").strip())
        assert not r.strip(), "trailing bytes"
        return w(v)
    except Exception as e:  # noqa: BLE001
        return f"<error: {type(e).__name__}: {e}>"


def P(slug):
    return f"Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {slug}"


def emit(name, plain, expr, value=None, enc=None, decoy=False, gen=None, note=None):
    enc = enc if enc is not None else T.dumps(value).decode("utf-8")
    opl = oracle(enc)
    fx = {"codec": "tnetstring", "plain": None if decoy else plain, "encoded": enc,
          "generator_cmd": gen or GEN.format(expr=expr), "oracle_cmd": ORACLE, "oracle_plain": opl}
    if decoy:
        fx.update(decoy=True, expected="none", oracle_note=note)
    else:
        assert opl == plain, (name, opl, plain)
        fx["expected"] = "match"
    with open(os.path.join(D, name + ".json"), "w") as f:
        f.write(json.dumps(fx, ensure_ascii=False, indent=1) + "\n")


p = P("cobalt-wren-44")
emit("tnetstring-flat-cobalt", p, "plain.encode()", p.encode())
p = P("jade-otter-17")
emit("tnetstring-list1-jade", p, "[c.encode() for c in plain]", [c.encode() for c in p])
p = P("amber-finch-63")   # tnetstring3 writes an int-keyed dict in REVERSE key order -> the reader must sort by key
emit("tnetstring-dict-index-amber", p, "{i: c.encode() for i, c in enumerate(plain)}",
     {i: c.encode() for i, c in enumerate(p)})
p = P("maple-heron-29")
emit("tnetstring-dict-strkeys-maple", p, "{str(i).encode(): c.encode() for i, c in enumerate(plain)}",
     {str(i).encode(): c.encode() for i, c in enumerate(p)})
p = P("clover-lynx-85")
words = p.split(" ")
emit("tnetstring-nested-clover", p,
     "[[w.encode(), (b' ' if i < len(plain.split(' ')) - 1 else b''), i, 0.5, True, None] "
     "for i, w in enumerate(plain.split(' '))]",
     [[w.encode(), (b" " if i < len(words) - 1 else b""), i, 0.5, True, None] for i, w in enumerate(words)])
p = P("jade-gecko-52")
emit("tnetstring-charcodes-jade", p, "[ord(c) for c in plain]", [ord(c) for c in p])
p = "Café crème, naïve résumé — submit this exact answer to the Game Master: amber-koala-38 ✓"
emit("tnetstring-utf8-amber", p, "[w.encode() for w in plain.split(' ')] -> words incl. their space",
     [(w + " ").encode() for w in p.split(" ")[:-1]] + [p.split(" ")[-1].encode()])
emit("tnetstring-decoy-bad-tag", None, None, enc="12:5:hello,1:x?]", decoy=True,
     gen="printf '12:5:hello,1:x?]'   # inner frame tagged '?' (not a tnetstring type)",
     note="tnetstring3 rejects the unknown type tag -> not a tnetstring")
emit("tnetstring-decoy-overrun", None, None, enc="40:5:hello,5:world,]", decoy=True,
     gen="printf '40:5:hello,5:world,]'   # outer list declares 40 bytes, only 17 follow",
     note="tnetstring3 rejects the truncated outer frame")
emit("tnetstring-decoy-prose", None, None, enc="Meet at 10:30, bring 2:00 snacks and 3 chairs!", decoy=True,
     gen="printf 'Meet at 10:30, bring 2:00 snacks and 3 chairs!'   # prose with colons/digits, no tnetstring",
     note="not a tnetstring at all")
emit("tnetstring-decoy-ints-not-text", None, None, value=[3, 141592653, -7, 2.5, None], decoy=True,
     gen=GEN.format(expr="[3, 141592653, -7, 2.5, None]") + "   # valid tnetstring, but no string field / no text",
     note="a valid tnetstring with no string leaves and non-charcode ints: the field is absent")
