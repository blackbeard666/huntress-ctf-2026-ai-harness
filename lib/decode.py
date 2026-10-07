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
import math
import re
import urllib.parse
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


# Numbered mixed-encoding chunks ("NN<TAB>payload" per line, each line its own encoding, split mid-word), from
# Day 6 "Eight Is Enough" Mastery (GM-confirmed 28/28 sets): decode each chunk by its own strict format, join in
# index order WITHOUT trimming chunk spaces. decode_chunked() returns None when the text is not chunked.
_CHUNK = re.compile(r"^(\d+)(?:\t|[:.)|\]] )(.*)$")
_NUMS = re.compile(r"^\d{1,3}(?:[\s,]+\d{1,3})*$")
_BINS = re.compile(r"^[01]{8}(?:[\s,]*[01]{8})*$")
_HEXS = re.compile(r"^(?:[0-9a-fA-F]{2})+$")
_B64S = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
_B32S = re.compile(r"^[A-Z2-7]+=*$")
# English letter frequencies (%), for picking a rot-N shift on short chunks
_FREQ = dict(zip("abcdefghijklmnopqrstuvwxyz",
                 (8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, 0.15, 0.77, 4.0, 2.4, 6.7, 7.5, 1.9, 0.095,
                  6.0, 6.3, 9.1, 2.8, 0.98, 2.4, 0.15, 2.0, 0.074)))


def _ascii(b):
    """Printable ASCII text (plus \\t\\r\\n) or None."""
    if b and all(32 <= c < 127 or c in (9, 10, 13) for c in b):
        return b.decode()
    return None


def _wordy(s):
    return sum(c.isalnum() or c in " .,!?:;'-_\n" for c in s) / max(len(s), 1)


def _rot(s, n):
    return "".join(chr((ord(c) - 97 + n) % 26 + 97) if "a" <= c <= "z" else
                   chr((ord(c) - 65 + n) % 26 + 65) if "A" <= c <= "Z" else c for c in s)


def _eng(s):
    letters = [c for c in s.lower() if "a" <= c <= "z"]
    return sum(math.log(_FREQ[c]) for c in letters) / max(len(letters), 1)


def decode_chunk(p):
    """Decode one chunk payload by its own format; strict formats first, rot-N last."""
    t = p.strip()
    cands = []  # (decoded_text, priority)
    if re.fullmatch(r"(?:%[0-9A-Fa-f]{2}|[^%\s])+", t) and len(re.findall(r"%[0-9A-Fa-f]{2}", t)) * 3 >= len(t) // 2:
        # URL percent-encoding (warmups Day 7 "Percent Chance": line 7 = '%2d%69%73...'), mostly %XX by length
        cands.append((_ascii(urllib.parse.unquote_to_bytes(t)), 0))
    if _BINS.match(t):
        bits = re.sub(r"[\s,]", "", t)
        cands.append((_ascii(int(bits, 2).to_bytes(len(bits) // 8, "big")), 0))
    if _NUMS.match(t):
        toks = re.split(r"[\s,]+", t)
        padded = any(len(x) == 3 and x[0] == "0" for x in toks)
        if all(re.fullmatch(r"[0-7]+", x) for x in toks) and max(int(x, 8) for x in toks) < 256:
            cands.append((_ascii(bytes(int(x, 8) for x in toks)), 1 if padded else 2))
        if max(int(x) for x in toks) < 256:
            cands.append((_ascii(bytes(int(x) for x in toks)), 3 if padded else 1))
    if _HEXS.match(t):
        cands.append((_ascii(binascii.unhexlify(t)), 4))
    if _B32S.match(t) and len(t) % 8 == 0:
        try:
            cands.append((_ascii(base64.b32decode(t)), 5))
        except Exception:
            pass
    if _B64S.match(t) and len(t) % 4 == 0:
        try:
            cands.append((_ascii(base64.b64decode(t, validate=True)), 6))
        except Exception:
            pass
    good = [(s, pr) for s, pr in cands if s is not None and _wordy(s) >= 0.85]
    if good:
        return min(good, key=lambda x: (-round(_wordy(x[0]), 2), x[1]))[0]
    # free text: plain or rot-N (pick the shift that reads most like English); keep spacing exactly
    if re.search(r"[A-Za-z]", p):
        return max((_rot(p, n) for n in range(26)), key=lambda s: (_eng(s), s == _rot(p, 13)))
    return p


def decode_chunked(text):
    rows = []
    for ln in text.splitlines():
        m = _CHUNK.match(ln.rstrip("\r\n"))
        if m:
            rows.append((int(m.group(1)), m.group(2)))
        elif ln.strip():
            return None
    if len(rows) < 2:
        return None
    rows.sort(key=lambda r: r[0])
    return "".join(decode_chunk(p) for _, p in rows)
