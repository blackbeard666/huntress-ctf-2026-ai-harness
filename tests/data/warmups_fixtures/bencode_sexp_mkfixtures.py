"""Offline generator for tests/data/warmups_fixtures/{bencode,sexp}-*.json.
bencode: writer AND reader = bencode.py 4.1.0 (pip install --target tools/pylib-bencode bencode.py).
sexp: writer = nettle's sexp-conv 3.10.2 (apt-get download nettle-bin; dpkg -x into tools/nettle-bin) fed an
advanced-syntax sexp of quoted strings; reader = sexp-conv -s advanced -> sexpdata 1.0.2 (pip install --target
tools/pylib-sexpdata sexpdata). Never lib.warmups_codecs. Run: python3 -I tests/data/warmups_fixtures/bencode_sexp_mkfixtures.py"""
import base64
import json
import os
import subprocess
import sys

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(D, "..", "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "pylib-bencode"))
sys.path.insert(0, os.path.join(ROOT, "tools", "pylib-sexpdata"))
import bencode as B  # noqa: E402
import sexpdata as SD  # noqa: E402

SEXPCONV = os.path.join(ROOT, "tools", "nettle-bin", "usr", "bin", "sexp-conv")

B_GEN = ("python3 -I -c \"import sys; sys.path.insert(0,'tools/pylib-bencode'); import bencode as B; plain=sys.argv[1]; "
         "sys.stdout.buffer.write(B.encode({expr}))\" \"$plain\"")
B_ORACLE = ("python3 -I -c \"import sys; sys.path.insert(0,'tools/pylib-bencode'); import bencode as B\n"
            "def w(v):\n"
            " if isinstance(v,(str,bytes)): return v if isinstance(v,str) else v.decode()\n"
            " if isinstance(v,list): return ''.join(w(x) for x in v) if any(not isinstance(x,int) for x in v) else ''.join(map(chr,v))\n"
            " if isinstance(v,dict): return ''.join(w(v[k]) for k in sorted(v))\n"
            " return ''\n"
            "print(w(B.decode(sys.stdin.buffer.read().strip())), end='')\"")
S_GEN = ("python3 -I -c \"import sys, json; plain=sys.argv[1]; print({expr})\" \"$plain\" | "
         "tools/nettle-bin/usr/bin/sexp-conv -s {syntax}")
S_ORACLE = ("tools/nettle-bin/usr/bin/sexp-conv -s advanced -w 0 | python3 -I -c \"import sys; "
            "sys.path.insert(0,'tools/pylib-sexpdata'); import sexpdata as S\n"
            "def w(v, nohead={nohead}):\n"
            " if isinstance(v,list): return ''.join(w(x) for x in v[(1 if nohead and len(v)>1 and isinstance(v[0],S.Symbol) else 0):] if not isinstance(x,S.Brackets))\n"
            " return str(v)\n"
            "print(w(S.loads(sys.stdin.read(), nil=None, true=None, false=None)), end='')\"")


def P(slug):
    return f"Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {slug}"


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def b_oracle(enc):
    def w(v):
        if isinstance(v, (str, bytes)):
            return v if isinstance(v, str) else v.decode()
        if isinstance(v, list):
            return "".join(w(x) for x in v) if any(not isinstance(x, int) for x in v) else "".join(map(chr, v))
        if isinstance(v, dict):
            return "".join(w(v[k]) for k in sorted(v))
        return ""
    try:
        return w(B.decode(enc.encode("utf-8").strip()))
    except Exception as e:  # noqa: BLE001
        return f"<error: {type(e).__name__}: {e}>"


def s_oracle(enc, nohead=False):
    r = subprocess.run([SEXPCONV, "-s", "advanced", "-w", "0"], input=enc.encode("utf-8"), capture_output=True)
    if r.returncode:
        return f"<error: sexp-conv: {r.stderr.decode(errors='replace').strip()}>"

    def w(v):
        if isinstance(v, list):
            st = 1 if nohead and len(v) > 1 and isinstance(v[0], SD.Symbol) else 0
            return "".join(w(x) for x in v[st:] if not isinstance(x, SD.Brackets))
        return str(v)
    try:
        return w(SD.loads(r.stdout.decode("utf-8"), nil=None, true=None, false=None))
    except Exception as e:  # noqa: BLE001
        return f"<error: {type(e).__name__}: {e}>"


def s_write(adv, syntax):
    return subprocess.run([SEXPCONV, "-s", syntax], input=adv.encode("utf-8"), capture_output=True,
                          check=True).stdout.decode("utf-8").strip()


def emit(name, codec, plain, enc, gen, oracle_cmd, opl, decoy=False, note=None):
    fx = {"codec": codec, "plain": None if decoy else plain, "encoded": enc, "generator_cmd": gen,
          "oracle_cmd": oracle_cmd, "oracle_plain": opl}
    if decoy:
        assert opl.startswith("<error") or opl != plain, (name, opl)
        fx.update(decoy=True, expected="none", oracle_note=note)
    else:
        assert opl == plain, (name, opl, plain)
        fx["expected"] = "match"
    with open(os.path.join(D, name + ".json"), "w") as f:
        f.write(json.dumps(fx, ensure_ascii=False, indent=1) + "\n")


def bfx(name, plain, expr, value):
    enc = B.encode(value).decode("utf-8")
    emit(name, "bencode", plain, enc, B_GEN.format(expr=expr), B_ORACLE, b_oracle(enc))


def sfx(name, plain, expr, adv, syntax, nohead=False):
    enc = s_write(adv, syntax)
    emit(name, "sexp", plain, enc, S_GEN.format(expr=expr, syntax=syntax), S_ORACLE.format(nohead=nohead),
         s_oracle(enc, nohead))


p = P("cobalt-ibis-41")
bfx("bencode-list1-cobalt", p, "list(plain)", list(p))
p = P("jade-marten-73")
bfx("bencode-string-jade", p, "plain", p)
p = P("amber-quail-26")
bfx("bencode-dict-index-amber", p, "{f'{i:04d}': c for i, c in enumerate(plain)}", {f"{i:04d}": c for i, c in enumerate(p)})
p = "Café crème, naïve résumé — submit this exact answer to the Game Master: maple-yak-58 ✓"
words = [w + " " for w in p.split(" ")[:-1]] + [p.split(" ")[-1]]
bfx("bencode-nested-utf8-maple", p, "{'msg': [[w, i] for i, w in enumerate(words incl. trailing space)], 'n': 17}",
    {"msg": [[w, i] for i, w in enumerate(words)], "n": 17})
p = P("clover-mink-39")
bfx("bencode-charcodes-clover", p, "[ord(c) for c in plain]", [ord(c) for c in p])

p = P("clover-tapir-64")
adv = "(" + " ".join(q(c) for c in p) + ")"
sfx("sexp-canonical-clover", p, "'(' + ' '.join(json.dumps(c) for c in plain) + ')'", adv, "canonical")
p = P("amber-gibbon-15")
adv = "(" + " ".join(q(c) for c in p) + ")"
sfx("sexp-transport-amber", p, "'(' + ' '.join(json.dumps(c) for c in plain) + ')'", adv, "transport")
p = P("jade-lemur-82")
adv = "(msg [text/plain] " + " ".join(q(w + " ") for w in p.split(" ")[:-1]) + " " + q(p.split(" ")[-1]) + ")"
sfx("sexp-hint-words-jade", p, "'(msg [text/plain] ' + ' '.join(json.dumps(w) for w in words incl. trailing space) + ')'",
    adv, "canonical", nohead=True)
p = P("maple-civet-90")
w = p.split(" ")
adv = "(answer (part " + " ".join(q(x + " ") for x in w[:8]) + ") (part " + " ".join(q(x + " ") for x in w[8:-1]) \
      + ") (slug " + q(w[-1]) + "))"
sfx("sexp-nested-transport-maple", p, "(answer (part words0-7) (part words8..) (slug last)) incl. trailing spaces",
    adv, "transport", nohead=True)

# decoys
p = P("cobalt-ibis-41")
enc = B.encode(list(p)).decode()[:-1]
emit("bencode-decoy-unterminated", "bencode", None, enc, B_GEN.format(expr="list(plain)") + " | head -c -1",
     B_ORACLE, b_oracle(enc), decoy=True, note="list missing its final 'e'")
enc = "Meet at 10:30, bring 2:00 snacks and i3e chairs!"
emit("bencode-decoy-prose", "bencode", None, enc, f"printf '{enc}'   # prose with colons/digits/i3e, not bencode",
     B_ORACLE, b_oracle(enc), decoy=True, note="not bencode at all")
p = P("jade-lemur-82")
canon = s_write("(" + " ".join(q(c) for c in p) + ")", "canonical").encode()
enc = "{" + base64.b64encode(canon[:-1]).decode() + "}"
emit("sexp-decoy-transport-truncated", "sexp", None, enc,
     S_GEN.format(expr="'(' + ' '.join(json.dumps(c) for c in plain) + ')'", syntax="canonical")
     + " | head -c -1 | base64 -w0 | sed 's/.*/{&}/'", S_ORACLE.format(nohead=False), s_oracle(enc), decoy=True,
     note="transport form whose canonical sexp lost its closing ')'")
enc = "(3:Nic5:e wo)"
emit("sexp-decoy-length-overrun", "sexp", None, enc, "printf '(3:Nic5:e wo)'   # atom length overruns the list",
     S_ORACLE.format(nohead=False), s_oracle(enc), decoy=True, note="verbatim atom length overrun")
