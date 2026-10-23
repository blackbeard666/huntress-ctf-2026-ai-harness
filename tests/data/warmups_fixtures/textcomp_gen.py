"""Offline fixture GENERATOR for the text-compression family (independent of lib/warmups_codecs.py).
usage: python3 -I textcomp_gen.py <rle-cf|rle-ca|lz77|lzw|lzw-clear|huffman> "<plain>"
huffman uses the PyPI `dahuffman` library (PYTHONPATH=tools/pylibs) for the code table."""
import itertools
import re
import sys

mode, s = sys.argv[1], sys.argv[2]
if mode == "rle-cf":
    print("".join(f"{len(list(g))}{k}" for k, g in itertools.groupby(s)))
elif mode == "rle-ca":
    print(re.sub(r"(.)\1*", lambda m: m[1] + str(len(m[0])), s, flags=re.S))
elif mode == "lz77":   # textbook LZ77, search buffer 64, (distance, length, next) with the literal quoted
    toks, p = [], 0
    while p < len(s):
        best = (0, 0)
        for start in range(max(0, p - 64), p):
            n = 0
            while p + n < len(s) - 1 and s[start + n] == s[p + n]:
                n += 1
            if n > best[1] or (n == best[1] and n and p - start < best[0]):
                best = (p - start, n)
        toks.append(f"({best[0]}, {best[1]}, '{s[p + best[1]]}')")
        p += best[1] + 1
    print(" ".join(toks))
elif mode in ("lzw", "lzw-clear"):   # Rosetta-Code style LZW compress, dict of 256 single chars
    size = 258 if mode == "lzw-clear" else 256
    table = {chr(i): i for i in range(256)}
    w, res = "", ([256] if mode == "lzw-clear" else [])
    for c in s:
        if w + c in table:
            w = w + c
        else:
            res.append(table[w])
            table[w + c] = size
            size += 1
            w = c
    if w:
        res.append(table[w])
    if mode == "lzw-clear":
        res.append(257)
    print(res)
elif mode == "huffman":
    from dahuffman import HuffmanCodec
    tbl = HuffmanCodec.from_data(s).get_code_table()
    codes = {k: format(v, f"0{n}b") for k, (n, v) in tbl.items() if isinstance(k, str)}
    print(repr(codes))
    print("".join(codes[c] for c in s))
