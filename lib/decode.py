"""Generic layered decoder for the warmups lane (and any 'peel the encodings' task).

peel(data) does a breadth-first search over decode steps (base64/32/85/a85, hex, binary, gzip/zlib/bz2/xz,
url, rot-N, single-byte xor, reversal, decimal char codes) and returns the first decoded text that an
`accept` predicate recognizes, plus the chain of steps taken. Variant-proof: detects layers, no fixed list.
"""
import base64
import binascii
import bz2
import codecs
import gzip
import io
import lzma
import re
import zlib
import zipfile
from urllib.parse import unquote_to_bytes

_B64 = re.compile(rb"^[A-Za-z0-9+/=\s]+$")
_B64URL = re.compile(rb"^[A-Za-z0-9_\-=\s]+$")
_B32 = re.compile(rb"^[A-Z2-7=\s]+$")
_HEX = re.compile(rb"^(?:[0-9a-fA-F]{2}[\s:]*)+$")
_BIN = re.compile(rb"^[01\s]+$")


def _printable(b):
    try:
        s = b.decode("utf-8")
    except Exception:
        return None
    return s if s and sum(c.isprintable() or c in "\r\n\t" for c in s) / len(s) > 0.95 else None


def _candidates(b):
    s = b.strip()
    for magic, fn in ((b"\x1f\x8b", gzip.decompress), (b"BZh", bz2.decompress),
                      (b"\xfd7zXZ", lzma.decompress), (b"x", zlib.decompress)):
        if b.startswith(magic):
            try:
                yield "z:" + magic.hex(), fn(b)
            except Exception:
                pass
    if b.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                yield "zip", b"\n".join(z.read(n) for n in z.namelist())
        except Exception:
            pass
    compact = re.sub(rb"\s+", b"", s)
    if compact:
        if _BIN.match(s) and len(compact) % 8 == 0:
            yield "bin", int(compact, 2).to_bytes(len(compact) // 8, "big")
        if _HEX.match(s):
            try:
                yield "hex", binascii.unhexlify(re.sub(rb"[\s:]", b"", s))
            except Exception:
                pass
        if _B32.match(s) and len(compact) % 8 == 0:
            try:
                yield "b32", base64.b32decode(compact)
            except Exception:
                pass
        if _B64.match(s):
            try:
                yield "b64", base64.b64decode(compact + b"=" * (-len(compact) % 4), validate=True)
            except Exception:
                pass
        if _B64URL.match(s):
            try:
                yield "b64url", base64.urlsafe_b64decode(compact + b"=" * (-len(compact) % 4))
            except Exception:
                pass
        for name, fn in (("b85", base64.b85decode), ("a85", base64.a85decode)):
            try:
                yield name, fn(compact)
            except Exception:
                pass
    if b"%" in s:
        yield "url", unquote_to_bytes(s)
    t = _printable(b)
    if t is not None:
        # strip a leading per-line index/prefix like "01\t", "1: ", "3 - " (seen in Mastery variants)
        stripped = "\n".join(re.sub(r"^\s*\d+\s*[:.\-\t ]\s*", "", ln) for ln in t.splitlines())
        if stripped != t:
            yield "deprefix", stripped.encode()
        # also try just the longest line (prompts sometimes wrap the payload in chatter)
        longest = max(t.splitlines(), key=len, default="")
        if longest and longest != t.strip():
            yield "longline", longest.encode()
        yield "rev", t[::-1].encode()
        if re.fullmatch(r"[\d\s,]+", t.strip()) and re.search(r"\d", t):
            try:
                yield "dec", bytes(int(x) for x in re.split(r"[\s,]+", t.strip()) if x)
            except Exception:
                pass
        for n in range(1, 26):
            yield f"rot{n}", bytes(((c - 65 + n) % 26 + 65) if 65 <= c <= 90 else
                                   ((c - 97 + n) % 26 + 97) if 97 <= c <= 122 else c for c in t.encode())


def _expand(data):
    yield from _candidates(data)
    if _printable(data) is None:
        for k in range(1, 256):
            x = bytes(c ^ k for c in data)
            if _printable(x):
                yield f"xor{k:#x}", x


def peel(data, accept, max_nodes=60000):
    """BFS; return (accepted_text, [steps]) for the shortest chain whose output `accept(text)` is truthy."""
    if isinstance(data, str):
        data = data.encode()
    seen, frontier, n = {data}, [(data, ())], 0
    while frontier:
        nxt = []
        for cur, path in frontier:
            t = _printable(cur)
            if t is not None and accept(t):
                return t, list(path)
            for name, out in _expand(cur):
                n += 1
                if out and out not in seen and n < max_nodes:
                    seen.add(out)
                    nxt.append((out, path + (name,)))
        frontier = nxt
    return None, []
