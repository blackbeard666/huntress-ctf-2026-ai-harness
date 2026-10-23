"""Offline fixture ORACLE (reader) for the text-compression family, independent of lib/warmups_codecs.py.
usage: printf %s "$encoded" | python3 -I textcomp_oracle.py <rle-cf|rle-ca|lz77|lzw|lzw-clear|huffman>"""
import ast
import re
import sys

mode, t = sys.argv[1], sys.stdin.read().strip()
if mode == "rle-cf":
    print(re.sub(r"(\d)(.)", lambda m: m[2] * int(m[1]), t, flags=re.S))
elif mode == "rle-ca":
    print(re.sub(r"(.)(\d)", lambda m: m[1] * int(m[2]), t, flags=re.S))
elif mode == "lz77":
    out = []
    for d, n, c in ast.literal_eval("[" + t.replace(") (", "), (") + "]"):
        assert d <= len(out)
        for _ in range(n):
            out.append(out[-d])
        out.append(c)
    print("".join(out))
elif mode in ("lzw", "lzw-clear"):
    codes = ast.literal_eval(t)
    if mode == "lzw-clear":
        assert codes[0] == 256 and codes[-1] == 257
        codes = codes[1:-1]
    nxt = 258 if mode == "lzw-clear" else 256
    d = {i: chr(i) for i in range(256)}
    w = d[codes[0]]
    out = [w]
    for k in codes[1:]:
        e = d[k] if k in d else w + w[0]
        out.append(e)
        d[nxt] = w + e[0]
        nxt += 1
        w = e
    print("".join(out))
elif mode == "huffman":
    tline, bits = t.split("\n", 1)
    inv = {v: k for k, v in ast.literal_eval(tline).items()}
    assert len(inv) > 1
    out, cur = [], ""
    for b in bits.strip():
        cur += b
        if cur in inv:
            out.append(inv[cur])
            cur = ""
    assert not cur
    print("".join(out))
