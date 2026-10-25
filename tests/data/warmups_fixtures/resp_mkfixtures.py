"""Offline generator for tests/data/warmups_fixtures/resp-*.json.
Writer: redis-py's own RESP command packer (redis.Connection.pack_command, no socket opened) or a printf literal;
oracle: hiredis.Reader (the C reference parser) -- never lib.warmups_codecs.
pip install --target tools/pylib-redis redis hiredis. Run: python3 -I tests/data/warmups_fixtures/resp_mkfixtures.py"""
import json
import os
import sys

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(D, "..", "..", "..", "tools", "pylib-redis"))
import hiredis  # noqa: E402
import redis  # noqa: E402

GEN = ("python3 -I -c \"import sys; sys.path.insert(0,'tools/pylib-redis'); import redis; plain=sys.argv[1]; "
       "sys.stdout.buffer.write(b''.join(redis.Connection().pack_command(*{expr})))\" \"$plain\"{post}")
ORACLE = ("python3 -I -c \"import sys; sys.path.insert(0,'tools/pylib-redis'); import hiredis\n"
          "d=sys.stdin.buffer.read(){pre}\n"
          "r=hiredis.Reader(); r.feed(d); v=r.gets()\n"
          "assert v is not False and not r.has_data(), 'not one complete RESP value'\n"
          "w=lambda v: b''.join(map(w,v)) if isinstance(v,list) else (v if isinstance(v,bytes) else b'')\n"
          "j=' ' if {words} else ''\n"
          "print(j.join(x.decode() for x in v) if isinstance(v,list) and {words} else w(v).decode(), end='')\"")


def oracle(enc, lf=False, words=False):
    """The same reader as ORACLE (hiredis over the WHOLE text), in-process."""
    try:
        d = enc.encode("utf-8")
        if lf:
            d = d.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        r = hiredis.Reader()
        r.feed(d)
        v = r.gets()
        assert v is not False and not r.has_data(), "not one complete RESP value"
        if isinstance(v, Exception):
            raise v

        def w(v):
            return b"".join(map(w, v)) if isinstance(v, list) else (v if isinstance(v, bytes) else b"")
        if words and isinstance(v, list):
            return " ".join(x.decode() for x in v)
        return w(v).decode()
    except Exception as e:  # noqa: BLE001
        return f"<error: {type(e).__name__}: {e}>"


def P(slug):
    return f"Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {slug}"


def pack(args):
    return b"".join(redis.Connection().pack_command(*args)).decode("utf-8")


def emit(name, plain, enc, expr=None, lf=False, words=False, decoy=False, gen=None, note=None):
    opl = oracle(enc, lf, words)
    pre = ".replace(b'\\r\\n',b'\\n').replace(b'\\n',b'\\r\\n')   # LF -> CRLF for the strict C reader" if lf else ""
    fx = {"codec": "resp", "plain": None if decoy else plain, "encoded": enc,
          "generator_cmd": gen or GEN.format(expr=expr, post=" | sed 's/\\r$//'" if lf else ""),
          "oracle_cmd": ORACLE.format(pre=pre, words=words), "oracle_plain": opl}
    if decoy:
        fx.update(decoy=True, expected="none", oracle_note=note)
    else:
        assert opl == plain, (name, opl, plain)
        fx["expected"] = "match"
    with open(os.path.join(D, name + ".json"), "w") as f:
        f.write(json.dumps(fx, ensure_ascii=False, indent=1) + "\n")


p = P("cobalt-wren-44")   # array of 1-char bulk strings, CRLF
emit("resp-chars-crlf-cobalt", p, pack(list(p)), "list(plain)")
p = P("jade-otter-17")    # same, bare LF line ends
emit("resp-chars-lf-jade", p, pack(list(p)).replace("\r\n", "\n"), "list(plain)", lf=True)
p = P("amber-finch-63")   # one bulk string per word (spaces dropped -> words re-joined with ' ')
emit("resp-words-amber", p, pack(p.split(" ")), "plain.split(' ')", words=True)
p = P("maple-heron-29")   # same, LF
emit("resp-words-lf-maple", p, pack(p.split(" ")).replace("\r\n", "\n"), "plain.split(' ')", lf=True, words=True)
p = "Café crème, naïve résumé — submit this exact answer to the Game Master: clover-lynx-85"
emit("resp-chars-utf8-clover", p, pack(list(p)), "list(plain)")   # $len counts UTF-8 bytes
p = P("jade-gecko-52")    # RESP3 verbatim string (txt: prefix stripped by hiredis)
v = f"={len(p.encode()) + 4}\r\ntxt:{p}\r\n"
emit("resp3-verbatim-jade", p, v, gen=f"printf '={len(p.encode()) + 4}\\r\\ntxt:%s\\r\\n' \"$plain\"")

emit("resp-decoy-overrun", None, "*2\r\n$5\r\nhello\r\n$9\r\nworld\r\n", decoy=True,
     gen="printf '*2\\r\\n$5\\r\\nhello\\r\\n$9\\r\\nworld\\r\\n'   # $9 claims more bytes than follow",
     note="bulk length overruns the buffer")
emit("resp-decoy-markdown", None, "* bring snacks\n* bring 3 chairs\n* meet at 10:30", decoy=True,
     gen="printf '* bring snacks\\n* bring 3 chairs\\n* meet at 10:30'   # markdown bullets, no RESP",
     note="'*' not followed by a count")
emit("resp-decoy-count-short", None, "*3\r\n$5\r\nhello\r\n$5\r\nworld\r\n", decoy=True,
     gen="printf '*3\\r\\n$5\\r\\nhello\\r\\n$5\\r\\nworld\\r\\n'   # array promises 3, has 2",
     note="array count larger than the elements present")
