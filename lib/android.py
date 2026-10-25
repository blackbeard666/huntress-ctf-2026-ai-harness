"""Android/APK analysis helpers for the mobile lane.

Before this, each mobile solver was a copy-pasted *JSON reader*: it pulled assets/huntress_puzzle.json and
regex'd the answer, never touching the dex/manifest/resources — so it broke the instant the answer moved,
with zero obfuscation. This module is the robust fallback chain:

    extract_answer(apk):  puzzle-json decode  ->  raw scan of every zip entry  ->  dex strings  ->  nested zip/dex  ->
                          apktool (manifest/resources/smali)  ->  jadx (decompiled sources)

plus manifest_facts() for the exported-component / deep-link / allowBackup questions the lane actually asks.
Tools (apktool, jadx) are on PATH via bin/env.sh; each stage is best-effort with a timeout and degrades
gracefully if a tool is missing. Static only — we never install/run the APK.
"""
import base64
import binascii
import bz2
import codecs
import hashlib
import hmac
import io
import itertools
import json
import lzma
import math
import re
import struct
import unicodedata
import subprocess
import time
import xml.etree.ElementTree as ET
import zipfile
import zlib
from functools import lru_cache
from pathlib import Path

ANS_RE_T = re.compile(r"ANS-[0-9A-Fa-f]{16}")
ANS_RE_B = re.compile(rb"ANS-[0-9A-Fa-f]{16}")
_ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


# --- codec decode (the primary puzzle-json path, kept identical to the per-day solvers) ----------
def _key_bytes(key):
    if key is None:
        return b"\x00"
    if isinstance(key, int):
        return bytes([key & 0xFF])
    if isinstance(key, (bytes, bytearray)):  # a derived key (identity_key_scan: digest bytes)
        return bytes(key) or b"\x00"
    s = str(key)
    if re.fullmatch(r"\d+", s):
        return bytes([int(s) & 0xFF])
    return s.encode("utf-8") or b"\x00"


def decode_payload(codec, data, key=None, accept=ANS_RE_T.search):
    """Decode a huntress_puzzle.json payload by its declared codec: plain/split, xor (base64 + repeating key), base64,
    base32, hex, rot13, reverse, caesar (every char's code point shifted by key). When the declared reading doesn't yield
    an answer (`accept`, default: an `ANS-<16 hex>` code) -- an unknown or renamed codec -- `decode_any()` searches the
    known primitives instead; if that finds nothing either, the declared reading (unknown codec: data unchanged) is
    returned as before."""
    out = _decode_declared(codec, data, key)
    if accept is None or (out and accept(out)):
        return out
    return decode_any(data, key, accept) or out


def _decode_declared(codec, data, key=None):
    codec = (codec or "plain").strip().lower()
    try:
        if codec in ("plain", "", "none", "raw", "identity", "split"):
            return data if isinstance(data, str) else str(data)
        if codec == "xor":
            raw = base64.b64decode(data)
            k = _key_bytes(key)
            return bytes(b ^ k[i % len(k)] for i, b in enumerate(raw)).decode("utf-8", "replace")
        if codec in ("base64", "b64"):
            return base64.b64decode(data).decode("utf-8", "replace")
        if codec in ("base32", "b32"):
            return base64.b32decode(data).decode("utf-8", "replace")
        if codec in ("hex", "base16"):
            return binascii.unhexlify(str(data).strip()).decode("utf-8", "replace")
        if codec in ("rot13", "rot-13"):
            return codecs.decode(data, "rot13")
        if codec in ("reverse", "reversed"):
            return data[::-1]
        if codec in ("caesar", "shift", "char_shift"):
            # Day 7 (webview-bridge): EVERY character's code point shifted by `key` (']'->'S', '7'->'-'), not just
            # letters -- lib.ciphers.caesar_all can't express it. Decode = subtract the key.
            k = int(key)
            return "".join(chr((ord(c) - k) % 0x110000) for c in str(data))
    except Exception:  # noqa: BLE001 - a wrong codec guess should just miss, not crash
        return ""
    return data


def _b64ish(b, alt=False):
    t = re.sub(rb"\s", b"", b)
    if not t or not re.fullmatch(rb"[A-Za-z0-9_\-]+={0,2}" if alt else rb"[A-Za-z0-9+/]+={0,2}", t):
        return None
    t += b"=" * (-len(t) % 4)
    return base64.urlsafe_b64decode(t) if alt else base64.b64decode(t)


def _readings(b):
    """Byte -> byte primitives a puzzle codec is built from (decode direction)."""
    yield b[::-1]
    for fn in (_b64ish, lambda x: _b64ish(x, True),
               lambda x: base64.b32decode(re.sub(rb"\s", b"", x)) if re.fullmatch(rb"[A-Z2-7]+=*", re.sub(rb"\s", b"", x) or b"-") else None,
               lambda x: binascii.unhexlify(re.sub(rb"[\s:,\-]", b"", x)) if re.fullmatch(rb"(?:[0-9a-fA-F]{2}[\s:,\-]*)+", x.strip() or b"-") else None,
               lambda x: bytes(int(t) for t in re.split(rb"[\s,;]+", x.strip())) if re.fullmatch(rb"\d+(?:[\s,;]+\d+)+", x.strip()) and all(int(t) < 256 for t in re.split(rb"[\s,;]+", x.strip())) else None,
               lambda x: base64.b85decode(x)):
        try:
            r = fn(b)
        except Exception:  # noqa: BLE001 - not this encoding
            r = None
        if r:
            yield r
    t = b.decode("latin-1")
    yield codecs.decode(t, "rot13").encode("latin-1")


def _keyed(b, key):
    """Keyed primitives (xor / add / sub mod 256 / code-point shift) for every reading of the key."""
    keys = []
    for k in (_key_bytes(key), str(key).encode() if key is not None and not isinstance(key, (bytes, bytearray)) else None):
        if k and k not in keys:
            keys.append(k)
    for k in keys:
        yield bytes(x ^ k[i % len(k)] for i, x in enumerate(b))
        if len(k) == 1:
            yield bytes((x - k[0]) % 256 for x in b)
            yield bytes((x + k[0]) % 256 for x in b)
    try:
        n = int(str(key), 0)
    except (TypeError, ValueError):
        return
    t = b.decode("utf-8", "replace")
    for d in (-n, n):
        try:
            yield "".join(chr((ord(c) + d) % 0x110000) for c in t).encode("utf-8")
        except (ValueError, UnicodeEncodeError):
            pass


_CHAIN_MAX_IN = 16384  # extended passes (2-3) only for puzzle-sized payloads, never a whole APK (day 10 fallback)
_UNZ_MAX = 1 << 20     # decompressed-output cap per step


def _atbash(t):
    return "".join(chr(219 - ord(c)) if "a" <= c <= "z" else chr(155 - ord(c)) if "A" <= c <= "Z" else c for c in t)


def _rot47(t):
    return "".join(chr(33 + (ord(c) - 33 + 47) % 94) if 33 <= ord(c) <= 126 else c for c in t)


def _vigenere(t, key, every=False):
    """Vigenere decrypt by the key's letters (case kept, non-letters pass); the key advances on letters only (CyberChef
    / textbook) or, `every`, on every character."""
    ks = [ord(c) - 65 for c in str(key).upper() if "A" <= c <= "Z"]
    if not ks:
        return None
    out, j = [], 0
    for c in t:
        if "a" <= c <= "z" or "A" <= c <= "Z":
            base = 97 if c >= "a" else 65
            out.append(chr((ord(c) - base - ks[j % len(ks)]) % 26 + base))
            j += 1
        else:
            out.append(c)
            j += every
    return "".join(out)


def _rail_fence(t, rails):
    """Decode a zig-zag rail-fence ciphertext written with `rails` rails."""
    n = len(t)
    if rails < 2 or rails >= n:
        return None
    cyc = 2 * rails - 2
    rows = [min(i % cyc, cyc - i % cyc) for i in range(n)]
    order = sorted(range(n), key=lambda i: rows[i])  # stable: positions per rail, left to right
    out = [""] * n
    for c, i in zip(t, order):
        out[i] = c
    return "".join(out)


def _unz(b):
    if b[:2] == b"\x1f\x8b":
        d = zlib.decompressobj(31)
    elif b[:1] == b"x":
        d = zlib.decompressobj()
    elif b[:3] == b"BZh":
        d = bz2.BZ2Decompressor()
    elif b[:5] == b"\xfd7zXZ":
        d = lzma.LZMADecompressor()
    else:
        return None
    return d.decompress(b, _UNZ_MAX)


def _readings2(b):
    """Pass-2 primitives (Row 36): atbash, rot47, rail-fence 2-6, binary/octal char codes, a85, zlib/gzip/bz2/xz."""
    t = b.decode("latin-1")
    yield _atbash(t).encode("latin-1")
    yield _rot47(t).encode("latin-1")
    if 3 <= len(t) <= 4096:
        for n in range(2, 7):
            r = _rail_fence(t, n)
            if r:
                yield r.encode("latin-1")
    s = re.sub(rb"\s", b"", b)
    for fn in (lambda: int(s, 2).to_bytes(len(s) // 8, "big") if re.fullmatch(rb"(?:[01]{8})+", s) else None,
               lambda: bytes(int(x, 8) for x in b.split()) if re.fullmatch(rb"[0-7]{3}(?:\s+[0-7]{3})+", b.strip()) else None,
               lambda: base64.a85decode(b.strip(), adobe=b.strip().startswith(b"<~")),
               lambda: _unz(b)):
        try:
            r = fn()
        except Exception:  # noqa: BLE001 - not this encoding
            r = None
        if r:
            yield r


def _keyed2(b, key):
    """Pass-2 keyed primitives: Vigenere by a string key, rail-fence by an integer key."""
    t = b.decode("latin-1")
    for every in (False, True):
        r = _vigenere(t, key, every)
        if r:
            yield r.encode("latin-1")
    try:
        n = int(str(key), 0)
    except (TypeError, ValueError):
        return
    if 6 < n < len(t):
        r = _rail_fence(t, n)
        if r:
            yield r.encode("latin-1")


def _bfs(start, key, accept, depth, cap, extended=False, end=None):
    seen, frontier = {start}, [start]
    for _ in range(depth):
        nxt = []
        for b in frontier:
            if end is not None and time.time() > end:
                return None
            for r in (*_readings(b), *(_keyed(b, key) if key is not None else ()),
                      *(_readings2(b) if extended else ()),
                      *(_keyed2(b, key) if extended and key is not None else ())):
                if not r or r in seen:
                    continue
                seen.add(r)
                t = r.decode("utf-8", "replace")
                if accept(t):
                    return t
                nxt.append(r)
                if len(seen) > cap:
                    return None
        frontier = nxt
    return None


def decode_any(data, key=None, accept=ANS_RE_T.search, depth=3, cap=4000, chain=True, chain_s=0.35):
    """Name-agnostic decode: breadth-first over the primitives puzzle codecs are composed of (reverse, base64/urlsafe/
    base32/hex/decimal/base85, rot13, xor/add/sub/code-point shift by `key`), up to `depth` steps, returning the first
    reading that satisfies `accept` (default: contains an ANS-<16 hex> code). The answer shape is the oracle, so a new
    or renamed codec name never matters (Day 7 `caesar` was such a name). None if nothing within the budget matches.
    When that finds nothing and `chain` (payloads <= 16 KB): a second pass adds atbash / rot47 / Vigenere (string key) /
    rail-fence / binary / octal / a85 / zlib-gzip-bz2-xz, then lib.decode.peel (rot-N, url, single-byte xor, longer
    chains) runs until `chain_s` seconds. Pass 1 is unchanged, so every answer it found before is still found first."""
    start = data.encode("utf-8", "replace") if isinstance(data, str) else bytes(data or b"")
    hit = _bfs(start, key, accept, depth, cap)
    if hit is not None or not chain or not start or len(start) > _CHAIN_MAX_IN:
        return hit
    end = time.time() + chain_s
    try:
        hit = _bfs(start, key, accept, depth, cap, extended=True, end=end)
        if hit is None and time.time() < end:
            from lib.decode import peel
            hit = peel(start, lambda t: bool(accept(t)), max_nodes=20000, deadline=end)[0]
    except Exception:  # noqa: BLE001 - a search miss, never a crash
        hit = None
    return hit


def _split_assemblies(parts, order):
    parts = [str(p) for p in parts]
    n = len(parts)
    outs = []
    if order and sorted(int(o) for o in order) == list(range(n)):
        o = [int(x) for x in order]
        slots = [None] * n
        for i, pos in enumerate(o):
            slots[pos] = parts[i]
        outs.append("".join(slots))
        outs.append("".join(parts[x] for x in o))
    outs.append("".join(parts))
    outs.append("".join(reversed(parts)))
    return outs


_PERM_KEYS = re.compile(r"order|perm|index|indices|pos|map|slot|shuffle|seq|idx|key", re.I)


def _int_list(v):
    if isinstance(v, str) and re.fullmatch(r"\s*\d+(?:\s*[,; ]\s*\d+){3,}\s*", v):
        v = re.split(r"[,; ]+", v.strip())
    if not isinstance(v, list) or len(v) < 4 or len(v) > 4096:
        return None
    if not all((isinstance(x, int) and not isinstance(x, bool) and 0 <= x < 1 << 20)
               or (isinstance(x, str) and x.strip().isdigit() and len(x.strip()) < 7) for x in v):
        return None
    return [int(x) for x in v]


def permutation_candidates(p):
    """Permutation codecs keyed by an int list (D17 `indexed`, D5/D10 `split`, any `perm*`/`shuffle*`): for every
    int-list field of the puzzle dict (order/perm/index/positions/map/slots/... -- any name) the data string (or its
    `parts` list) is reassembled by scatter (r[o[i]] = d[i]) and gather (r[i] = d[o[i]]), 0- and 1-based; scatter of o
    is gather of o's inverse, so both directions cover the inverse. Gather also runs on a non-permutation index list
    into a longer table. Each reading is kept as is, and when none carries an ANS token, decode_any() runs on them
    (a permuted base64/hex/xor layer). Candidates fully matching ^ANS-<16 hex>$ come first. [] when absent."""
    out = []
    try:
        if not isinstance(p, dict):
            return out
        seqs = []
        for k in ("parts", "data", "payload", "chars", "pieces", "chunks"):
            v = p.get(k)
            if isinstance(v, list) and v and all(isinstance(x, (str, int)) for x in v):
                seqs.append([str(x) for x in v])
            elif isinstance(v, str) and len(v) >= 4:
                seqs.append(v)
        lists = []
        for k, v in p.items():
            o = _int_list(v)
            if o is not None and all(o != x for _, x in lists):
                lists.append((0 if _PERM_KEYS.search(str(k)) else 1, o))
        lists = [o for _, o in sorted(lists, key=lambda t: t[0])][:8]
        for seq in seqs:
            n = len(seq)
            for o in lists:
                for base in (0, 1):
                    oo = [x - base for x in o]
                    if min(oo) < 0:
                        continue
                    if len(oo) == n and sorted(oo) == list(range(n)):
                        slots = [""] * n
                        for i, pos in enumerate(oo):
                            slots[pos] = seq[i]
                        out.append("".join(slots))
                    if max(oo) < n:
                        out.append("".join(seq[x] for x in oo))
        out = list(dict.fromkeys(c for c in out if c))
        if out and not any(ANS_RE_T.search(c) for c in out):
            key = p.get("key")
            for c in out[:8]:
                d = decode_any(c, key, depth=2, chain=False)
                if d:
                    out.append(d)
        out.sort(key=lambda c: not re.fullmatch(r"ANS-[0-9A-Fa-f]{16}", c.strip()))
    except Exception:  # noqa: BLE001 - a decoy / malformed puzzle just yields nothing
        return []
    return out


_ANS_FULL = re.compile(r"ANS-[0-9A-Fa-f]{16}")
_TP_HINTS = (("affine", r"strid|step|slot|affine|skip|hop|modul|decimat|mult"), ("rail", r"rail|zig|fence|wave"),
             ("columnar", r"colum|\bcols?\b|grid|matrix|width|transpos|table|interleav|even|odd|weave"),
             ("chunk", r"chunk|block|revers|flip|segment|mirror|piece"))


@lru_cache(maxsize=8)
def _tp_orders(n):
    """(family, params, read order) of the keyless transposition families on n slots (cipher[j] = plain[o[j]]):
    affine/stride slot maps (k*i+o mod n: rotation, reversal, D17's 3+7i), rail-fence 2-10, columnar width 2-10
    (natural / reversed column order, every column order up to width 5; width 2 = even/odd interleave), chunk-reverse
    k=2-10 and chunk-order reversal. Each order is also composed with a whole-string reversal."""
    from itertools import permutations
    from math import gcd
    base = []
    for k in range(1, n):
        if gcd(k, n) == 1:
            for o in range(n):
                base.append(("affine", (k, o), [(k * i + o) % n for i in range(n)]))
    for r in range(2, min(n, 11)):
        cyc = 2 * r - 2
        rows = [min(i % cyc, cyc - i % cyc) for i in range(n)]
        base.append(("rail", (r,), sorted(range(n), key=lambda i: rows[i])))
    for w in range(2, min(n, 11)):
        cols = list(range(w))
        for cord in (permutations(cols) if w <= 5 else (cols, cols[::-1])):
            base.append(("columnar", (w,), [r * w + c for c in cord for r in range((n + w - 1) // w) if r * w + c < n]))
    for k in range(2, min(n, 11)):
        chunks = [list(range(s, min(s + k, n))) for s in range(0, n, k)]
        base.append(("chunk", (k,), [i for ch in chunks for i in reversed(ch)]))
        base.append(("chunk", (k,), [i for ch in reversed(chunks) for i in ch]))
    out = []
    for fam, prm, o in base:
        out.append((fam, prm, tuple(o)))
        out.append((fam, prm, tuple(o[::-1])))
    return tuple(out)


def transposition_candidates(s, p=None):
    """Keyless transposition codecs (Row 36) on a bare `data` string with no index list: when s is a shuffled
    ANS-<16 hex> (one each of N, S, -, at least one A, the rest hex; 20 chars), every permutation of the keyless
    families in _tp_orders() is applied both ways (gather r[j] = s[o[j]], scatter r[o[j]] = s[j]) and only readings
    fully matching ^ANS-<16 hex>$ are kept. Ties (the 4-char prefix leaves ~15% ambiguous) narrow by the puzzle dict p:
    first the family named by its codec/field names (stride/rail/columnar/chunk ...), then its small int fields as
    the family parameter (rails=8, width=5, step=7). Returns [token] only when exactly one distinct token survives,
    else [] (a decode, never a guess list)."""
    try:
        if not isinstance(s, str):
            return []
        s = s.strip()
        n = len(s)
        if n != 20 or ANS_RE_T.search(s) or any(s.count(c) != 1 for c in "NS-") or "A" not in s:
            return []
        if not re.fullmatch(r"[0-9A-Fa-f]*", re.sub(r"[NS-]", "", s)):
            return []
        hits = {}
        for fam, prm, o in _tp_orders(n):
            r = [""] * n
            for j, x in enumerate(o):
                r[x] = s[j]
            for v in ("".join(s[x] for x in o), "".join(r)):
                if _ANS_FULL.fullmatch(v):
                    hits.setdefault(v, set()).add((fam, prm))
        if len(hits) > 1 and isinstance(p, dict):
            text = " ".join([str(p.get("codec") or "")] + [str(k) for k in p])
            fams = {f for f, rx in _TP_HINTS if re.search(rx, text, re.I)}
            ints = {v for k, v in p.items() if isinstance(v, int) and not isinstance(v, bool) and 1 < v < n
                    and k not in ("day", "version", "schema", "len", "length")}
            for keep in (lambda t: t[0] in fams, lambda t: bool(ints & set(t[1]))):
                sub = {v: {t for t in ts if keep(t)} for v, ts in hits.items()}
                sub = {v: ts for v, ts in sub.items() if ts}
                if sub:
                    hits = sub
                if len(hits) == 1:
                    break
        return list(hits) if len(hits) == 1 else []
    except Exception:  # noqa: BLE001 - malformed input just yields nothing
        return []


def _puzzle_obj_candidates(p):
    """Decoded candidate strings of one parsed huntress_puzzle.json object (declared codec, split parts, int-list
    permutation fields, keyless transposition)."""
    data, codec, key = p.get("data", p.get("payload", "")), p.get("codec"), p.get("key")
    if (codec or "").lower() == "split" or "parts" in p:
        got = _split_assemblies(p.get("parts", []), p.get("order"))
    else:
        got = [decode_payload(codec, data, key)]
    if not any(c and ANS_RE_T.search(c) for c in got):  # indexed/perm*/shuffle*/unknown: int-list fields
        got = permutation_candidates(p) + got
    if not any(c and ANS_RE_T.search(c) for c in got):  # keyless stride/rail/columnar/chunk transposition
        for s in [data] + [c for c in got if isinstance(c, str)][:8]:
            t = transposition_candidates(s, p)
            if t:
                got = t + got
                break
    return got


# --- position / rolling-key xor keystreams (coverage atlas row 70; D18 TT `decryptByte`) -------------------------------
# A per-byte helper whose key varies with the index: c^(k+s*i), c^k^i, (c-k-s*i), c^key[i%n] (key from the JSON or a dex
# string), cipher/plain-feedback chaining (IV = key), an LCG keystream (any 2^n LCG's low byte solved from the known
# bytes; Java Random / glibc / MSVC / JSON-given a,c,m seeded from JSON / dex numbers), each optionally under a
# fixed or index-driven bit rotation. Every family's parameters are solved from the known plaintext "ANS-" and the whole
# reading must then be `ANS-<16 hex>` (trailing whitespace allowed), so a stray solve can't produce a token.
_RXK_P = b"ANS-"
_RXK_FULL = re.compile(rb"ANS-[0-9A-Fa-f]{16}\s{0,4}")
_RXK_MIN, _RXK_MAX = 20, 24
_RXK_POOL = re.compile(rb"([\x01-\x40])([\x20-\x7e]{1,64})\x00")
_RXK_ARR = re.compile(rb"\x00\x03([\x01\x02])\x00(.{4})", re.S)
_RXK_LCG = ((1103515245, 12345, 1 << 31), (214013, 2531011, 1 << 32), (1664525, 1013904223, 1 << 32),
            (0x5DEECE66D, 0xB, 1 << 48), (6364136223846793005, 1442695040888963407, 1 << 64))
_RXK_BUDGET_S = 0.3


def _rxk_ok(p):
    return _RXK_FULL.fullmatch(bytes(p)) is not None


def _rxk_rot(x, r):
    r &= 7
    return ((x >> r) | (x << (8 - r))) & 0xFF


def _rxk_free(c, q):
    """Keyless families (parameters solved from target prefix `q`): yield intermediate byte lists."""
    n = len(c)
    k = c[0] ^ q[0]
    s = ((c[1] ^ q[1]) - k) & 0xFF
    yield [c[i] ^ ((k + s * i) & 0xFF) for i in range(n)]  # c ^ (k + s*i): k+i, k-i, k*i, k*(i+1)
    for o in (0, 1):
        k = c[0] ^ q[0] ^ o
        yield [c[i] ^ k ^ ((i + o) & 0xFF) for i in range(n)]  # c ^ k ^ i
    k = (c[0] - q[0]) & 0xFF
    s = (c[1] - q[1] - k) & 0xFF
    yield [(c[i] - k - s * i) & 0xFF for i in range(n)]  # c = p + k + s*i
    k = (c[0] + q[0]) & 0xFF
    s = (c[1] + q[1] - k) & 0xFF
    yield [(k + s * i - c[i]) & 0xFF for i in range(n)]  # c = k + s*i - p
    for sub in (False, True):  # feedback chaining: prev = previous cipher / plain byte, prev[-1] = IV
        for fb_plain in (False, True):
            prv0 = q[0] if fb_plain else c[0]
            k = ((c[1] - q[1] - prv0) if sub else (c[1] ^ q[1] ^ prv0)) & 0xFF
            iv = ((c[0] - q[0] - k) if sub else (c[0] ^ q[0] ^ k)) & 0xFF
            out, prv = [], iv
            for x in c:
                y = ((x - k - prv) if sub else (x ^ k ^ prv)) & 0xFF
                out.append(y)
                prv = y if fb_plain else x
            yield out
    ks = [c[i] ^ q[i] for i in range(4)]
    kd = [(c[i] - q[i]) & 0xFF for i in range(4)]
    for kk, sub in ((ks, False), (kd, True)):  # low byte of any power-of-two LCG: x' = a*x + b (mod 256)
        d0, d1 = (kk[1] - kk[0]) & 0xFF, (kk[2] - kk[1]) & 0xFF
        for a in range(256):
            if (a * d0 - d1) & 0xFF:
                continue
            b = (kk[1] - a * kk[0]) & 0xFF
            if (a * kk[2] + b) & 0xFF != kk[3]:
                continue
            x, out = kk[0], []
            for v in c:
                out.append(((v - x) if sub else (v ^ x)) & 0xFF)
                x = (a * x + b) & 0xFF
            yield out


def _rxk_keyed(c, q, keys):
    """c ^ key[i % n] (also ^ i, and c - key[i % n]) for every candidate key whose bytes fit the known prefix."""
    n = len(c)
    kx = [c[i] ^ q[i] for i in range(4)]
    kxi = [kx[i] ^ i for i in range(4)]
    kd = [(c[i] - q[i]) & 0xFF for i in range(4)]
    for key in keys:
        m = len(key)
        for want, mode in ((kx, 0), (kxi, 1), (kd, 2)):
            if all(key[i % m] == want[i] for i in range(4)):
                if mode == 0:
                    yield [c[i] ^ key[i % m] for i in range(n)]
                elif mode == 1:
                    yield [c[i] ^ key[i % m] ^ (i & 0xFF) for i in range(n)]
                else:
                    yield [(c[i] - key[i % m]) & 0xFF for i in range(n)]


def _rxk_java(seed, n):
    """Java Random(seed) byte streams: nextInt(256), nextInt() & 0xff, nextBytes."""
    m = (1 << 48) - 1
    s0 = (seed ^ 0x5DEECE66D) & m
    a, b, s, c = [], [], s0, []
    for _ in range(n):
        s = (s * 0x5DEECE66D + 0xB) & m
        a.append((s >> 40) & 0xFF)
        b.append((s >> 16) & 0xFF)
    s = s0
    while len(c) < n:
        s = (s * 0x5DEECE66D + 0xB) & m
        r = s >> 16
        c += [(r >> sh) & 0xFF for sh in (0, 8, 16, 24)]
    return a, b, c[:n]


def _rxk_streams(seeds, lcgs, n):
    for seed in seeds:
        yield from _rxk_java(seed, n)
        for a, b, m in lcgs:
            for before in (True, False):
                x, outs = seed % m, ([], [], [], [])
                for _ in range(n):
                    if before:
                        x = (a * x + b) % m
                    outs[0].append(x & 0xFF)
                    outs[1].append((x >> 16) & 0xFF)
                    outs[2].append((x >> 24) & 0xFF)
                    outs[3].append((x >> (m.bit_length() - 9)) & 0xFF)
                    if not before:
                        x = (a * x + b) % m
                yield from outs


def _rxk_seeded(c, q, streams):
    kx = [c[i] ^ q[i] for i in range(4)]
    kd = [(c[i] - q[i]) & 0xFF for i in range(4)]
    for ks in streams:
        if ks[:4] == kx:
            yield [x ^ k for x, k in zip(c, ks)]
        elif ks[:4] == kd:
            yield [(x - k) & 0xFF for x, k in zip(c, ks)]


def rolling_xor_solve(c, keys=(), seeds=(), lcgs=()):
    """ANS tokens from one ciphertext (byte values) under a position / rolling-key keystream; [] when none fits."""
    c = [int(v) & 0xFF for v in c]
    if not _RXK_MIN <= len(c) <= _RXK_MAX:
        return []
    n, hits = len(c), []
    streams = list(_rxk_streams(seeds, list(_RXK_LCG) + list(lcgs), n)) if seeds else []
    # (pre-rotation of the cipher, target prefix, post-rotation): plain, rotr then families, families then rotr, and
    # an index-driven rotation (rotr by (r + i) % 8)
    plans = [(None, 0, 0)]
    for r in range(1, 8):
        plans += [(("f", r), 0, 0), (None, r, r)]
    plans += [(("i", r), 0, 0) for r in range(8)]
    for pre, qr, post in plans:
        cc = c if pre is None else [_rxk_rot(x, pre[1] if pre[0] == "f" else pre[1] + i) for i, x in enumerate(c)]
        q = [((v << qr) | (v >> (8 - qr))) & 0xFF if qr else v for v in _RXK_P]
        for out in (*_rxk_free(cc, q), *_rxk_keyed(cc, q, keys), *_rxk_seeded(cc, q, streams)):
            p = [_rxk_rot(x, post) for x in out] if post else out
            if p[:4] == list(_RXK_P) and _rxk_ok(p):
                hits.append(bytes(p).decode("latin-1").strip())
    return list(dict.fromkeys(hits))


def _rxk_readings(v):
    """Byte-value readings of one JSON value (raw / base64 / hex / int list) of ciphertext size."""
    out = []
    if isinstance(v, list):
        if all(isinstance(x, int) and not isinstance(x, bool) for x in v):
            out.append([x & 0xFFFF for x in v])
        return [r for r in out if _RXK_MIN <= len(r) <= _RXK_MAX]
    if not isinstance(v, str) or len(v) > 4 * _RXK_MAX:
        return []
    out.append([ord(ch) & 0xFFFF for ch in v])
    t = re.sub(r"\s", "", v)
    for fn in (lambda: base64.b64decode(t + "=" * (-len(t) % 4), validate=True),
               lambda: base64.urlsafe_b64decode(t + "=" * (-len(t) % 4)) if re.fullmatch(r"[A-Za-z0-9_\-]+=*", t) else None,
               lambda: binascii.unhexlify(re.sub(r"[:\-,]", "", t)),
               lambda: [int(x, 0) for x in re.split(r"[\s,;]+", v.strip())] if re.fullmatch(r"\s*(?:0[xX])?[0-9A-Fa-f]+(?:[\s,;]+(?:0[xX])?[0-9A-Fa-f]+)+\s*", v) else None):
        try:
            r = fn()
        except Exception:  # noqa: BLE001 - not this encoding
            r = None
        if r:
            out.append(list(r))
    return [r for r in out if _RXK_MIN <= len(r) <= _RXK_MAX]


def _rxk_walk(o, strs, ints, lists, depth=0):
    if depth > 4:
        return
    if isinstance(o, dict):
        for v in o.values():
            _rxk_walk(v, strs, ints, lists, depth + 1)
    elif isinstance(o, list):
        if o and all(isinstance(x, int) and not isinstance(x, bool) for x in o):
            lists.append(o)
        else:
            for v in o[:64]:
                _rxk_walk(v, strs, ints, lists, depth + 1)
    elif isinstance(o, bool):
        return
    elif isinstance(o, int):
        ints.append(o)
    elif isinstance(o, str) and len(o) <= 256:
        strs.append(o)


def _rxk_int(s):
    try:
        return int(s.strip(), 0) if re.fullmatch(r"\s*-?(?:0[xX][0-9A-Fa-f]+|\d+)\s*", s) else None
    except ValueError:
        return None


def rolling_xor_scan(apk, puzzle_objs=None):
    """ANS tokens from puzzle-JSON values and dex byte/char arrays (fill-array-data, 20-24 elements) under a position /
    rolling-key keystream (rolling_xor_solve). Keys: JSON key-ish values (int / str / list) and dex string-pool
    entries; seeds: JSON ints / numeric strings / Java hashCode of JSON strings, dex numeric strings; LCG constants
    a/c/m from JSON when present. [] when absent; never raises; bounded to ~0.3 s."""
    hits, deadline = [], time.time() + _RXK_BUDGET_S
    try:
        strs, ints, lists, cts, dstrs = [], [], [], [], []
        with zipfile.ZipFile(apk) as z:
            objs = puzzle_objs
            if objs is None:
                objs = []
                for info in z.infolist():
                    if info.filename.endswith("huntress_puzzle.json") and info.file_size < 1 << 20:
                        try:
                            objs.append(json.loads(z.read(info)))
                        except ValueError:
                            continue
            for info in z.infolist():
                if info.file_size <= 32 << 20 and re.fullmatch(r"classes\d*\.dex", Path(info.filename).name):
                    d = z.read(info)
                    if d[:4] != b"dex\n":
                        continue
                    for m in _RXK_POOL.finditer(d, 0x70):
                        if m.group(1)[0] == len(m.group(2)) and len(dstrs) < 4000:
                            dstrs.append(m.group(2).decode())
                    for m in _RXK_ARR.finditer(d):
                        w, cnt = m.group(1)[0], int.from_bytes(m.group(2), "little")
                        if _RXK_MIN <= cnt <= _RXK_MAX and m.end() + w * cnt <= len(d):
                            raw = d[m.end():m.end() + w * cnt]
                            cts.append(list(raw) if w == 1 else [int.from_bytes(raw[j:j + 2], "little")
                                                                  for j in range(0, len(raw), 2)])
                            if len(cts) >= 256:
                                break
        lcg = {}
        for o in objs:
            _rxk_walk(o, strs, ints, lists)
            if isinstance(o, dict):
                for k, v in o.items():
                    kk = str(k).lower()
                    iv = v if isinstance(v, int) and not isinstance(v, bool) else (_rxk_int(v) if isinstance(v, str) else None)
                    if iv is None:
                        continue
                    for name, al in (("a", ("a", "mul", "mult", "multiplier")), ("c", ("c", "inc", "increment", "add")),
                                     ("m", ("m", "mod", "modulus"))):
                        if kk in al:
                            lcg[name] = iv
                    if kk in ("bits", "n") and 8 <= iv <= 64:
                        lcg.setdefault("m", 1 << iv)
        cts = [r for v in strs + lists for r in _rxk_readings(v)] + cts
        keys = []
        for v in ints:
            keys.append(bytes([v & 0xFF]))
        for v in strs + dstrs:
            if 1 <= len(v) <= 64:
                keys.append(v.encode("utf-8", "replace"))
                if re.fullmatch(r"(?:[0-9A-Fa-f]{2})+", v):
                    keys.append(bytes.fromhex(v))
        for v in lists:
            if 1 <= len(v) <= 64:
                keys.append(bytes(x & 0xFF for x in v))
        keys = list(dict.fromkeys(keys))
        seeds = ints + [x for x in map(_rxk_int, strs + dstrs) if x is not None]
        hs = [_java_hash(s) for s in strs if s and len(s) <= 64]
        seeds += hs + [h - (1 << 32) for h in hs if h >> 31]
        seeds = list(dict.fromkeys(x for x in seeds if isinstance(x, int)))[:64]
        lcgs = [(lcg["a"], lcg.get("c", 0), lcg.get("m", 1 << 32))] if "a" in lcg and lcg.get("m", 1) > 1 else []
        for c in cts:
            if time.time() > deadline:
                break
            hits += rolling_xor_solve(c, keys, seeds, lcgs)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- puzzle data in a custom base-n alphabet carried in the dex / assets (coverage atlas rows 35, 36) ------------------
# Obfuscation days ship a shuffled base64/base32/base58 table: every dex string-pool or asset string of length 32 / 58 /
# 64 / 65 with all-unique printable chars is a candidate alphabet; the puzzle data (and other base-n-shaped strings) is
# translated to the standard table and decoded (alphabet as given and reversed), then the alphabet is also tried as a
# substitution key (data chars mapped alphabet <-> sorted / standard). Only ANS tokens are kept.
_CA_STD = {32: "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567",
           58: "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz",
           64: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"}
_CA_MAX_ALPHA, _CA_MAX_DATA, _CA_MAX_ENTRY, _CA_MAX_DEX, _CA_DEADLINE_S = 48, 12, 1 << 20, 32 << 20, 0.8
_CA_TOK = re.compile(rb"[^\s\"',;:=<>(){}\[\]\x00-\x1f\x7f-\xff]{16,}")


def _ca_is_alpha(s):
    return isinstance(s, str) and len(s) in (32, 58, 64, 65) and s.isascii() and s.isprintable() \
        and " " not in s and len(set(s)) == len(s)


def _ca_json_strings(o, out, depth=0):
    if isinstance(o, str):
        out.append(o)
    elif depth < 4 and isinstance(o, dict):
        for v in o.values():
            _ca_json_strings(v, out, depth + 1)
    elif depth < 4 and isinstance(o, list):
        for v in o[:256]:
            _ca_json_strings(v, out, depth + 1)


def _ca_dex_alphas(d):
    """String-pool entries of one dex whose MUTF-8 length is 32/58/64/65 and that read as an alphabet."""
    out = []
    if len(d) < 0x70 or not d.startswith(b"dex\n"):
        return out
    n, off = struct.unpack_from("<II", d, 0x38)
    if off + 4 * n > len(d):
        return out
    for so in struct.unpack_from(f"<{n}I", d, off):
        if so < len(d) and d[so] in (32, 58, 64, 65):
            s = d[so + 1:so + 1 + d[so]]
            if d[so + 1 + d[so]:so + 2 + d[so]] == b"\x00":
                t = s.decode("latin-1")
                if _ca_is_alpha(t):
                    out.append(t)
    return out


def _ca_b58(data, alpha):
    n = 0
    for c in data:
        n = n * 58 + alpha.index(c)
    lead = len(data) - len(data.lstrip(alpha[0]))
    return b"\x00" * lead + n.to_bytes((n.bit_length() + 7) // 8, "big")


def _ca_decode(data, alpha):
    """Byte readings of `data` under one custom alphabet (base-n table, then substitution key)."""
    out, L = [], len(alpha)
    body = data.rstrip("=") if "=" not in alpha else data
    if L == 65:  # 64 symbols + its own pad char
        tab, pad = alpha[:64], alpha[64]
        body = data.rstrip(pad)
    else:
        tab, pad = alpha, "="
    if body and set(body) <= set(tab):
        try:
            if len(tab) == 64:
                s = body.translate(str.maketrans(tab, _CA_STD[64]))
                out.append(base64.b64decode(s + "=" * (-len(s) % 4)))
            elif len(tab) == 32:
                s = body.translate(str.maketrans(tab, _CA_STD[32]))
                out.append(base64.b32decode(s + "=" * (-len(s) % 8)))
            elif len(tab) == 58 and len(body) <= 4096:
                out.append(_ca_b58(body, tab))
        except (ValueError, binascii.Error):
            pass
    for key, ref in ((alpha, "".join(sorted(alpha))), (tab, _CA_STD.get(len(tab), ""))):  # substitution key
        if len(ref) == len(key) and ref != key:
            for a, b in ((key, ref), (ref, key)):
                out.append(data.translate(str.maketrans(a, b)).encode("utf-8", "replace"))
    return out


def custom_alphabet_scan(apk, puzzle_objs=None):
    """ANS tokens from puzzle `data` (and other base-n-shaped strings) written in a custom base64/base32/base58 alphabet
    carried in the dex string pool, an asset or the puzzle json itself. Each candidate alphabet (as given and reversed)
    maps the data to the standard table before decoding, then serves as a substitution key; a decoded reading is checked
    for a literal token, then one decompression step. [] when absent; never raises."""
    hits, alphas, datas = [], [], []
    end = time.time() + _CA_DEADLINE_S
    try:
        with zipfile.ZipFile(apk) as z:
            objs = list(puzzle_objs or [])
            if puzzle_objs is None:
                for i in z.infolist():
                    if i.filename.endswith("huntress_puzzle.json") and i.file_size <= _CA_MAX_ENTRY:
                        try:
                            objs.append(json.loads(z.read(i)))
                        except ValueError:
                            continue
            strs = []
            for p in objs:
                _ca_json_strings(p, strs)
                if isinstance(p, dict):
                    v = p.get("data", p.get("payload"))
                    if isinstance(v, str):
                        datas.append(v)
            for i in z.infolist():
                name = i.filename
                if re.fullmatch(r"classes\d*\.dex", Path(name).name) and i.file_size <= _CA_MAX_DEX:
                    alphas += _ca_dex_alphas(z.read(i))
                elif (name.startswith(("assets/", "res/raw/")) and i.file_size <= _CA_MAX_ENTRY
                      and not name.endswith("huntress_puzzle.json")):
                    b = z.read(i)
                    try:
                        _ca_json_strings(json.loads(b), strs)
                    except ValueError:
                        pass
                    strs += [m.decode("latin-1") for m in _CA_TOK.findall(b)[:512]]
            for s in strs:
                (alphas if _ca_is_alpha(s) else datas).append(s)
    except (OSError, zipfile.BadZipFile, RuntimeError, struct.error):
        return []
    alphas = list(dict.fromkeys(alphas))[:_CA_MAX_ALPHA]
    datas = [d.strip() for d in dict.fromkeys(datas) if 8 <= len(d.strip()) <= 16384][:_CA_MAX_DATA]
    if not alphas or not datas:
        return []
    try:
        for a in alphas:
            for alpha in (a, a[::-1]):
                for d in datas:
                    if time.time() > end:
                        return list(dict.fromkeys(hits))
                    for b in _ca_decode(d, alpha):
                        t = b.decode("latin-1")
                        found = ANS_RE_T.findall(t)
                        if not found:
                            try:
                                u = _unz(b)
                            except (OSError, ValueError, EOFError, zlib.error, lzma.LZMAError):
                                u = None
                            found = ANS_RE_T.findall(u.decode("latin-1")) if u else []
                        hits += found
            if hits:
                break
    except Exception:  # noqa: BLE001 - a malformed alphabet / payload is a miss, never a crash
        pass
    return list(dict.fromkeys(hits))


# --- puzzle field that names a zip entry (coverage atlas row 42; D20 codec `dynamic`, data=`assets/payload.dex`) ---------
# A puzzle field (data / path / module / entry / payload / file, then any other string value) equal to -- or ending at a
# `/` boundary in -- an existing entry name (also with `assets/` added / stripped, `file:///android_asset/` mapped to
# `assets/`, `<entry>:<dotted.Class>` cut at the colon) is a pointer: that entry's bytes run the candidate chain (literal
# ASCII / UTF-16LE tokens, dex string pool, nested zip/jar/apk incl. multi-dex + its own puzzle, ELF printable runs,
# payload_unwrap'd wrappers, a text / JSON body), depth <= 3, each entry read once. Host-dex `<entry>:<Class>` strings
# are pointers too. The pointer string itself is never a candidate.
_PEF_KEYS = ("data", "path", "module", "entry", "payload", "file")
_PEF_ASSET_URL = "file:///android_asset/"
_PEF_BUDGET_S, _PEF_MAX_ENTRY, _PEF_MAX_STRS, _PEF_DECODE_CAP = 1.0, 32 << 20, 64, 24
_PEF_RUN = re.compile(rb"[\x21-\x7e]{16,4096}")


def _pef_strings(p, depth=0):
    """String values of a parsed puzzle object, pointer-named keys first."""
    out = []
    if depth > 4:
        return out
    if isinstance(p, dict):
        for k in sorted(p, key=lambda k: str(k).lower() not in _PEF_KEYS):
            out += _pef_strings(p[k], depth + 1)
    elif isinstance(p, list):
        for v in p[:256]:
            out += _pef_strings(v, depth + 1)
    elif isinstance(p, str) and 0 < len(p) <= 512:
        out.append(p)
    return out[:_PEF_MAX_STRS]


def _pef_resolve(s, names):
    """The entry name pointer string `s` names among `names` (a set), or None."""
    s = s.strip()
    m = _MC_PTR.fullmatch(s)
    if m:
        s = m.group(1)
    if s.startswith(_PEF_ASSET_URL):
        s = "assets/" + s[len(_PEF_ASSET_URL):]
    s = s.lstrip("/")
    if not s or s.endswith("/"):
        return None
    for c in (s, "assets/" + s, s[7:] if s.startswith("assets/") else None):
        if c and c in names:
            return c
    tails = [n for n in names if s.endswith("/" + n)]
    return max(tails, key=len) if tails else None


def _pef_tokens(b):
    return [m.decode() for m in ANS_RE_B.findall(b)] + [m.decode("utf-16-le") for m in ANS_RE_U16.findall(b)]


def _pef_decode(strs, deadline):
    """Tokens of encoded-looking strings run through decode_any (bounded)."""
    out = []
    for s in strs[:_PEF_DECODE_CAP]:
        if time.time() > deadline:
            break
        try:
            r = decode_any(s, accept=ANS_RE_T.search, depth=2, cap=600, chain=False)
        except Exception:  # noqa: BLE001
            continue
        if r:
            out += ANS_RE_T.findall(r)
    return out


def _pef_blob(b, depth, deadline, seen):
    """ANS tokens of one pointed-to payload (bytes): literal, then by format; [] when none."""
    hits = _pef_tokens(b)
    if depth <= 0 or time.time() > deadline:
        return hits
    kind, inner = (_unwrap_nested(b) or (None, b))
    if kind is None and b[:4] == b"\x7fELF":
        kind = "elf"
    if kind == "dex":
        strs = _cdx_pool(inner, 0, ()) if len(inner) >= 0x70 else []
        hits += [m for s in strs for m in ANS_RE_T.findall(s)]
        if not hits:
            hits += _pef_decode([s for s in strs if _CDX_ENCODED.fullmatch(s)], deadline)
        if not hits and inner is not b:
            hits += _pef_tokens(inner)
        return hits
    if kind == "zip":
        try:
            bio = io.BytesIO(inner)
            hits += [m for c in _puzzle_candidates(bio, depth - 1, seen, top=False) for m in ANS_RE_T.findall(c)]
            with zipfile.ZipFile(bio) as z:
                for i in z.infolist():
                    if i.is_dir() or i.file_size > _PEF_MAX_ENTRY or time.time() > deadline:
                        continue
                    hits += _pef_blob(z.read(i), depth - 1, deadline, seen)
        except Exception:  # noqa: BLE001 - truncated / impostor inner archive
            pass
        return hits
    if kind == "elf":
        if not hits:
            hits += _pef_decode([r.decode() for r in _PEF_RUN.findall(b)], deadline)
        return hits
    if hits:
        return hits
    try:
        got = payload_unwrap(b, min(deadline, time.time() + 0.4))
    except Exception:  # noqa: BLE001
        got = None
    if got:
        return _pef_blob(got[1], depth - 1, deadline, seen)
    try:
        t = b.decode("utf-8").strip()
    except UnicodeDecodeError:
        return hits
    if t[:1] in "{[":
        try:
            o = json.loads(t)
            for p in (o if isinstance(o, list) else [o]):
                if isinstance(p, dict):
                    hits += [m for c in _puzzle_obj_candidates(p) if isinstance(c, str) for m in ANS_RE_T.findall(c)]
        except Exception:  # noqa: BLE001
            pass
    if not hits and 16 <= len(t) <= 1 << 16:
        hits += _pef_decode([t], deadline)
    return hits


def _pef_follow(z, strs, depth, deadline, seen):
    """(tokens, pointer strings) for the pointers among `strs` into zip `z`; each entry is read once per chain."""
    names = {i.filename for i in z.infolist() if not i.is_dir()}
    hits, ptrs = [], []
    for s in strs:
        n = _pef_resolve(s, names)
        if n is None:
            continue
        ptrs.append(s)
        try:
            info = z.getinfo(n)
            if info.file_size > _PEF_MAX_ENTRY:
                continue
            b = z.read(info)
        except Exception:  # noqa: BLE001
            continue
        key = (n, len(b), hash(b[:4096]))
        if key in seen:
            continue
        seen.add(key)
        hits += _pef_blob(b, depth, deadline, seen)
    return list(dict.fromkeys(hits)), ptrs


def puzzle_pointer_candidates(apk, depth=3):
    """ANS tokens reached through puzzle fields (or host-dex `<entry>:<Class>` strings) that name a zip entry of `apk`.
    [] when no field is a pointer / the pointed-to entry holds no token; never raises."""
    try:
        with zipfile.ZipFile(apk) as z:
            objs = []
            for i in z.infolist():
                if i.filename.endswith("huntress_puzzle.json"):
                    try:
                        objs.append(json.loads(z.read(i)))
                    except ValueError:
                        continue
            hits, _ = _pef_follow(z, [s for p in objs for s in _pef_strings(p)], depth,
                                  time.time() + _PEF_BUDGET_S, set())
            return list(dict.fromkeys(hits))
    except Exception:  # noqa: BLE001
        return []


def _pef_host_ptrs(z):
    """`<entry>:<dotted.Class>` strings of the top-level classes*.dex."""
    out = []
    for i in z.infolist():
        if re.fullmatch(r"classes\d*\.dex", i.filename) and i.file_size <= _PEF_MAX_ENTRY:
            try:
                for m in re.finditer(_MC_PTR.pattern.encode(), z.read(i)):
                    v = m.group(0)  # a 1-byte uleb string length the regex swallowed (`4assets/...`) is not the name
                    out.append((v[1:] if v[0] == len(v) - 1 else v).decode())
            except Exception:  # noqa: BLE001
                continue
    return list(dict.fromkeys(out))[:_PEF_MAX_STRS]


def puzzle_candidates(apk):
    """Decoded candidate strings from assets/*huntress_puzzle.json (the primary, fast path). A field that names a zip
    entry (D20 `dynamic`: data=`assets/payload.dex`; see puzzle_pointer_candidates) yields that entry's tokens first,
    never the pointer string itself."""
    return _puzzle_candidates(apk)


def _puzzle_candidates(apk, depth=3, seen=None, top=True):
    out, names, objs, ptrs = [], [], [], []
    seen = set() if seen is None else seen
    try:
        with zipfile.ZipFile(apk) as z:
            # every central record in archive order (a duplicated name is read per record, the first -- the one Android
            # installs -- first; z.read(name) would only ever return the last, a decoy shadowing the real puzzle)
            names = [i for i in z.infolist() if i.filename.endswith("huntress_puzzle.json")]
            deadline = time.time() + _PEF_BUDGET_S
            for n in names:
                try:
                    p = json.loads(z.read(n))
                except ValueError:
                    continue
                objs.append(p)
                got = []
                if depth > 0:  # a field naming an entry: that entry's candidate chain first
                    try:
                        got, ptr = _pef_follow(z, _pef_strings(p), depth, deadline, seen)
                    except Exception:  # noqa: BLE001
                        got, ptr = [], []
                    out, ptrs = out + got, ptrs + ptr
                if any(ANS_RE_T.search(c) for c in got):
                    continue
                try:
                    out += _puzzle_obj_candidates(p)
                except Exception:  # noqa: BLE001 - e.g. a list-valued `data` under an unknown codec
                    continue
            if names and depth > 0 and not any(c and ANS_RE_T.search(c) for c in out):  # host dex `<entry>:<Class>`
                try:
                    got, ptr = _pef_follow(z, _pef_host_ptrs(z), depth, deadline, seen)
                except Exception:  # noqa: BLE001
                    got, ptr = [], []
                out, ptrs = got + out, ptrs + ptr
    except (OSError, zipfile.BadZipFile):
        pass
    out = [c for c in out if c and c not in ptrs]
    if not top:
        return out
    if names and not any(ANS_RE_T.search(c) for c in out) \
            and any(isinstance(p, dict) and str(p.get("codec", "")).lower() == "analysis" for p in objs):
        # D23 "Hook Line and Signal": `codec: analysis` and no data -- Release.code() computes the token (decoy literal)
        out += dex_eval_scan(apk, deep=True)
        if not any(ANS_RE_T.search(c) for c in out):  # v2: the chain reads assets / resources / PackageInfo via its Context
            out += context_chain_scan(apk)
    if names and not any(ANS_RE_T.search(c) for c in out):  # unknown codec / xor mismatch: a per-index rolling keystream
        out += rolling_xor_scan(apk, [p for p in objs if isinstance(p, dict)])
    if names and not any(ANS_RE_T.search(c) for c in out):  # unknown codec: a custom base-n alphabet from dex / assets
        out += custom_alphabet_scan(apk)
    if names and not any(ANS_RE_T.search(c) for c in out):  # undecodable payload: maybe AES/DES under a static key
        out += static_key_cipher_scan(apk)
        if not any(ANS_RE_T.search(c) for c in out):  # ... or keyed by the app's identity (package / case / secret)
            out += identity_key_scan(apk)
    return out


# --- fallback scans (dex / resources / decompiled code) ------------------------------------------
def raw_entry_scan(apk):
    """Every zip entry's bytes, scanned for a literal ANS token (plaintext-anywhere fallback; several tokens beside Play
    Integrity / SafetyNet verdict blobs: integrity_verdict_scan()'s clean-verdict tokens first). When no ASCII token
    exists anywhere, falls back to zip_structure_scan() (duplicate-name / local-only / mismatched records, gap and
    post-EOCD bytes, comments, extra fields), then string_pool_scan() (UTF-16LE tokens + decoded AXML/resources.arsc pool strings), then
    proto_manifest_scan() (AAB / proto-format manifest values, then the bundle's base module re-laid as an APK), then
    signing_block_scan() (non-signature APK Signing Block pairs: Walle / VasDolly channel values), then
    hermes_string_scan() (decoded strings of a React Native Hermes bytecode bundle), then
    local_store_scan() (SQLite db cells / shared_prefs values / adb backup .ab members), then
    il2cpp_literal_scan() (decoded C# string literals of a Unity IL2CPP global-metadata.dat), then
    webview_asset_scan() (decoded JS literals / char-code arrays of assets/**/*.html|js|json), then
    java_serial_scan() (string / field values of a Java serialization stream: raw, dex byte[], base64 / hex text), then
    jwt_scan() (header / claim values of a JWT / JWE shipped in dex / assets / arsc / .so), then
    protobuf_asset_scan() (field values of a schema-less protobuf message in any entry or base64 / hex run), then
    compact_dex_scan() (decoded pool strings of a CompactDex / vdex / OAT payload)."""
    hits, arsc, verdicts = [], False, False
    try:
        with zipfile.ZipFile(apk) as z:
            for n in z.namelist():
                try:
                    b = z.read(n)
                    got = [m.decode() for m in ANS_RE_B.findall(b)]
                except (OSError, RuntimeError):
                    continue
                hits += got
                arsc = arsc or (n == "resources.arsc" and bool(got))
                verdicts = verdicts or bool(got) and _IVS_HINT.search(b) is not None
    except (OSError, zipfile.BadZipFile):
        pass
    if arsc:  # ANS-shaped strings.xml values: the ones the code reads by R id / getIdentifier go first
        hits = list(dict.fromkeys(resource_id_scan(apk) + hits))
    if verdicts and len(set(hits)) > 1:  # several tokens beside Play Integrity verdicts: the clean verdict's go first
        hits = list(dict.fromkeys(integrity_verdict_scan(apk) + hits))
    if not hits:
        hits = zip_structure_scan(apk)
    if not hits:
        hits = string_pool_scan(apk)
    if not hits:
        hits = proto_manifest_scan(apk)
    if not hits:
        hits = signing_block_scan(apk)
    if not hits:
        hits = hermes_string_scan(apk)
    if not hits:
        hits = local_store_scan(apk)
    if not hits:
        hits = il2cpp_literal_scan(apk)
    if not hits:
        hits = webview_asset_scan(apk)
    if not hits:
        hits = java_serial_scan(apk)
    if not hits:
        hits = jwt_scan(apk)
    if not hits:
        hits = protobuf_asset_scan(apk)
    if not hits:
        hits = compact_dex_scan(apk)
    return hits


# --- compact / optimised dex payloads: cdex001, vdex, OAT (coverage atlas row 86) -----------------------------------
# androguard and the classes*.dex scans only read a top-level standard dex. An optimised payload keeps the same string
# pool in another shell: CompactDex (`cdex001\0`, 0x88-byte header; string_data_off relative to the data section --
# data_off, or a vdex's shared data section), a vdex (`vdex0NN\0`: 006-011 dex section after the checksums, 019 a
# DexSectionHeader then cdex main sections + one shared data block, 021+ a section table) or an OAT ELF (`oatdata`
# symbol, dex files embedded after the oat header). Embedded dex / cdex are found by 4-aligned header magic (validated by
# header_size / endian tag / string_ids bounds), the data base is chosen by how many pool strings decode as exact MUTF-8,
# and each string is read for a token, then through decode_any when it looks encoded.
_CDX_MAX_ENTRY, _CDX_MAX_DEX, _CDX_MAX_STRINGS, _CDX_DECODE_BUDGET, _CDX_DEADLINE_S = 64 << 20, 64, 300_000, 300, 1.0
_CDX_MAGIC = re.compile(rb"dex\n0[0-9]{2}\x00|cdex0[0-9]{2}\x00")
_CDX_ENCODED = re.compile(r"[\x21-\x7e]{16,4096}")


def _cdx_mutf8(d, p):
    """(string, ok) of the MUTF-8 string_data_item at d[p]: uleb128 utf16 length, bytes, NUL. ok = length agrees."""
    n, q = _uleb(d, p)
    e = d.find(b"\x00", q, q + 3 * n + 1)
    if e < 0:
        return None, False
    try:
        s = d[q:e].replace(b"\xc0\x80", b"\x00").decode("utf-8", "surrogatepass")
        s = s.encode("utf-16-le", "surrogatepass").decode("utf-16-le", "replace")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return None, False
    return s, len(s.encode("utf-16-le")) // 2 == n


def _cdx_pool(d, base, shared):
    """Pool strings of the dex / cdex whose header sits at d[base]; [] when its string_ids do not resolve."""
    n, ids = struct.unpack_from("<II", d, base + 0x38)
    if not n or n > _CDX_MAX_STRINGS or base + ids + 4 * n > len(d):
        return []
    offs = struct.unpack_from(f"<{n}I", d, base + ids)
    cands = [base]
    if d[base:base + 4] == b"cdex":
        data_off = struct.unpack_from("<I", d, base + 0x6C)[0]
        cands = [base + data_off, base] + [x for s in shared for x in (s, s + data_off)]
    best, score = None, 0
    step = max(1, n // 32)
    for b0 in dict.fromkeys(c for c in cands if 0 <= c < len(d)):
        ok = 0
        for o in offs[::step]:
            try:
                ok += _cdx_mutf8(d, b0 + o)[1] if b0 + o < len(d) else 0
            except (IndexError, ValueError):
                pass
        if ok > score:
            best, score = b0, ok
    if best is None or score * 2 < len(offs[::step]):
        return []
    out = []
    for o in offs:
        try:
            s, ok = _cdx_mutf8(d, best + o) if best + o < len(d) else (None, False)
        except (IndexError, ValueError):
            continue
        if s is not None:
            out.append(s)
    return out


def _cdx_dexes(d):
    """(header offset, shared-data base candidates) of every dex / cdex embedded in a vdex / OAT / cdex blob."""
    hits = []
    for m in _CDX_MAGIC.finditer(d):
        o = m.start()
        if o & 3 or o + 0x70 > len(d):
            continue
        hsz, tag = struct.unpack_from("<II", d, o + 0x24)
        if tag != 0x12345678 or hsz not in (0x70, 0x88) and not (0x70 <= hsz <= 0x200):
            continue
        hits.append(o)
        if len(hits) >= _CDX_MAX_DEX:
            break
    shared = []
    if d[:4] == b"vdex" and d[4:7].isdigit() and 19 <= int(d[4:7]) < 21 and len(d) >= 0x1C:
        nd = struct.unpack_from("<I", d, 12)[0]
        sec = 0x1C + 4 * min(nd, 4096)
        if sec + 12 <= len(d):
            shared.append(sec + 12 + struct.unpack_from("<I", d, sec)[0])
    if hits:  # generic: the block right after the last embedded dex's own file_size
        last = hits[-1]
        shared.append(last + ((struct.unpack_from("<I", d, last + 0x20)[0] + 3) & ~3))
    return [(o, shared) for o in hits]


def compact_dex_strings(blob):
    """Pool strings of every dex / CompactDex inside one cdex / vdex / OAT ELF payload (bytes). [] for anything else
    (a plain zip / .so / renamed impostor without a valid embedded header); never raises."""
    try:
        d = bytes(blob)
        if not (d[:4] in (b"cdex", b"vdex") or (d[:4] == b"\x7fELF" and b"oatdata\x00" in d and b"oat\n" in d)):
            return []
        out = []
        for o, shared in _cdx_dexes(d):
            try:
                out += _cdx_pool(d, o, shared)
            except (struct.error, IndexError, ValueError):
                continue
        return out
    except Exception:  # noqa: BLE001 - truncated / hostile payload: nothing here
        return []


def compact_dex_scan(apk):
    """ANS tokens from the string pools of CompactDex / vdex / OAT payloads in any zip entry (assets/oat/*.vdex|odex,
    a renamed .cdex, ...): literal tokens first, then decode_any over encoded-looking pool strings. [] when absent."""
    hits, enc = [], []
    t0 = time.time()
    try:
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if info.is_dir() or info.file_size > _CDX_MAX_ENTRY or info.file_size < 0x70:
                    continue
                try:
                    with z.open(info) as f:
                        head = f.read(4)
                    if head not in (b"cdex", b"vdex", b"\x7fELF"):
                        continue
                    b = z.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError, NotImplementedError):
                    continue
                for s in compact_dex_strings(b):
                    got = ANS_RE_T.findall(s)
                    hits += got
                    if not got and _CDX_ENCODED.fullmatch(s.strip()):
                        enc.append(s.strip())
                if time.time() - t0 > _CDX_DEADLINE_S:
                    break
            if hits:
                return list(dict.fromkeys(hits))
            for s in dict.fromkeys(sorted(enc, key=len, reverse=True)[:_CDX_DECODE_BUDGET]):
                if time.time() - t0 > _CDX_DEADLINE_S * 1.5:
                    break
                d = decode_any(s, depth=2, cap=200, chain=False)
                if d:
                    hits += ANS_RE_T.findall(d)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- ZIP-level structure anomalies (coverage atlas row 62) -----------------------------------------------------------
# A pure-Python walk of the local file headers, independent of the central directory zipfile trusts: duplicated names
# (Android's libziparchive installs the FIRST record, zipfile.read(name) returns the LAST -- a decoy shadowing the real
# puzzle json), records whose local name / size differ from the central one, local-only entries (prepended or hidden
# in a gap, no central record), bytes between entries / after the EOCD, the archive and per-entry comments and
# non-standard extra fields. Each such blob is read for a literal token, as a puzzle json object, then via decode_any.
_ZSA_MAX_FILE, _ZSA_MAX_BLOB, _ZSA_DEADLINE_S, _ZSA_DECODE_BUDGET = 64 << 20, 4 << 20, 1.0, 48
# zip64, AV, PKWARE unix/NTFS/OpenVMS, strong encryption, Info-ZIP UT / ux / Ux / unix, jar 0xcafe, zipalign 0xd935,
# WinZip AES, Info-ZIP unicode path / comment
_ZSA_STD_EXTRA = frozenset((0x0001, 0x0007, 0x000A, 0x000C, 0x000D, 0x0014, 0x0015, 0x0016, 0x0017, 0x5455, 0x5855,
                            0x7855, 0x7875, 0xCAFE, 0xD935, 0x9901, 0x7075, 0x6375))
_ZSA_TEXT = re.compile(rb"[\x20-\x7e\t\r\n]{16,}")


def _zsa_local(b, off):
    """(name bytes, flags, method, local csize, data start, extra bytes) of the local header at b[off:], or None."""
    if b[off:off + 4] != b"PK\x03\x04" or off + 30 > len(b):
        return None
    flags, method = struct.unpack_from("<HH", b, off + 6)
    csize, = struct.unpack_from("<I", b, off + 18)
    nlen, xlen = struct.unpack_from("<HH", b, off + 26)
    ds = off + 30 + nlen + xlen
    if ds > len(b):
        return None
    return b[off + 30:off + 30 + nlen], flags, method, csize, ds, b[off + 30 + nlen:ds]


def _zsa_inflate(raw, method):
    if method == 0:
        return raw[:_ZSA_MAX_BLOB]
    if method == 8:
        try:
            return zlib.decompressobj(-15).decompress(raw, _ZSA_MAX_BLOB)
        except zlib.error:
            return b""
    return b""


def _zsa_extras(x):
    """Payloads of the non-standard extra-field records in `x`; a malformed tail that is not zero padding is a blob."""
    out, i = [], 0
    while i + 4 <= len(x):
        hid, n = struct.unpack_from("<HH", x, i)
        if i + 4 + n > len(x):
            break
        if hid not in _ZSA_STD_EXTRA and x[i + 4:i + 4 + n].strip(b"\x00"):
            out.append(x[i + 4:i + 4 + n])
        i += 4 + n
    if x[i:].strip(b"\x00"):
        out.append(x[i:])
    return out


def _zsa_blob(name, b, hits, state, depth):
    """Tokens of one anomalous blob: literal ASCII / UTF-16LE, an inner zip, a puzzle json object, then decode_any."""
    if not b:
        return
    found = [m.decode() for m in ANS_RE_B.findall(b)] + [m.decode("utf-16-le") for m in ANS_RE_U16.findall(b)]
    if not found and b[:4] == b"PK\x03\x04" and depth > 0:
        bio = io.BytesIO(b)
        found = [m.group(0) for c in puzzle_candidates(bio) for m in ANS_RE_T.finditer(c)]
        found = found or raw_entry_scan(bio) or zip_structure_scan(bio, depth - 1)
    if not found and b.lstrip()[:1] == b"{":
        try:
            p = json.loads(b)
        except ValueError:
            p = None
        if isinstance(p, dict):
            found = [m.group(0) for c in _puzzle_obj_candidates(p) if isinstance(c, str) for m in ANS_RE_T.finditer(c)]
    if not found:
        runs = [b.strip()] if _ZSA_TEXT.fullmatch(b.strip() or b"-") else _ZSA_TEXT.findall(b[:1 << 20])[:16]
        for r in runs:
            if state["budget"] <= 0 or time.time() > state["end"]:
                break
            state["budget"] -= 1
            d = decode_any(r.strip()[:_CHAIN_MAX_IN], chain_s=0.1)
            if d:
                found += ANS_RE_T.findall(d)
                break
    hits += found


def zip_structure_scan(apk, depth=2):
    """ANS tokens hidden in ZIP-level anomalies the central-directory readers skip or resolve differently: every record
    of a duplicated name (first first: Android's pick), local records whose name / size / extra differ from the
    central record, local-only entries (prepended or in a gap), gap bytes between entries, bytes after the EOCD, the
    archive / entry comments and non-standard extra fields (the v2 APK Signing Block is left to signing_block_scan).
    [] when the archive has none of these; never raises."""
    hits, state = [], {"budget": _ZSA_DECODE_BUDGET, "end": time.time() + _ZSA_DEADLINE_S}
    try:
        with zipfile.ZipFile(apk) as z:
            fp = z.fp
            fp.seek(0, 2)
            if fp.tell() > _ZSA_MAX_FILE:
                return []
            fp.seek(0)
            b = fp.read()
            infos, cd, comment = z.infolist(), z.start_dir, z.comment
        counts = {}
        for i in infos:
            counts[i.filename] = counts.get(i.filename, 0) + 1
        covered, side = [], []
        for i in infos:  # central records, archive order
            loc = _zsa_local(b, i.header_offset)
            if loc is None:
                continue
            lname, flags, method, lcsize, ds, lx = loc
            end = ds + i.compress_size
            if flags & 8:
                end += 16 if b[end:end + 4] == b"PK\x07\x08" else 12
            covered.append((i.header_offset, max(end, ds + (lcsize if not flags & 8 else 0))))
            cname = i.orig_filename.encode("utf-8" if i.flag_bits & 0x800 else "cp437", "replace")
            odd = counts[i.filename] > 1 or lname != cname or (not flags & 8 and lcsize != i.compress_size)
            if odd and not flags & 1:
                for n in dict.fromkeys((i.compress_size, lcsize if not flags & 8 else i.compress_size)):
                    _zsa_blob(i.filename, _zsa_inflate(b[ds:ds + n], method), hits, state, depth)
            side += [(i.filename, x) for x in _zsa_extras(lx) + _zsa_extras(i.extra)]
            if i.comment:
                side.append((i.filename, i.comment))
        sig_lo = cd
        if cd >= 32 and b[cd - 16:cd] == b"APK Sig Block 42":
            size, = struct.unpack_from("<Q", b, cd - 24)
            if 24 <= size <= cd - 8:
                sig_lo = cd - size - 8
        e = b.rfind(b"PK\x05\x06", cd)
        eocd_end = e + 22 + struct.unpack_from("<H", b, e + 20)[0] if 0 <= e <= len(b) - 22 else len(b)
        covered += [(sig_lo, eocd_end)]
        gaps, pos = [], 0
        for lo, hi in sorted(covered):
            if lo > pos:
                gaps.append((pos, lo))
            pos = max(pos, hi)
        if pos < len(b):
            gaps.append((pos, len(b)))
        for lo, hi in gaps:  # local-only records first, then the leftover gap bytes (prepended / trailing data)
            rest, k = bytearray(b[lo:hi]), lo
            while True:
                k = b.find(b"PK\x03\x04", k, hi)
                if k < 0:
                    break
                loc = _zsa_local(b, k)
                if loc is None or loc[1] & 1:
                    k += 4
                    continue
                lname, flags, method, lcsize, ds, lx = loc
                if flags & 8 and not lcsize:  # size only in the descriptor: run to the next signature in the gap
                    nxt = min([j for j in (b.find(s, ds, hi) for s in (b"PK\x07\x08", b"PK\x03\x04", b"PK\x01\x02"))
                               if j >= 0] or [hi])
                    lcsize = nxt - ds
                dend = min(ds + lcsize, hi)
                _zsa_blob(lname.decode("utf-8", "replace"), _zsa_inflate(b[ds:dend], method), hits, state, depth)
                side += [("", x) for x in _zsa_extras(lx)]
                rest[k - lo:dend - lo] = bytes(dend - k)
                k = max(dend, k + 4)
            rest = bytes(rest).strip(b"\x00")
            if rest:
                side.append(("", rest[:_ZSA_MAX_BLOB]))
        if comment:
            side.append(("", comment))
        for name, x in side:
            _zsa_blob(name, x, hits, state, depth)
    except Exception:  # noqa: BLE001 - truncated / impostor archive: no answer here, never raise
        pass
    return list(dict.fromkeys(hits))


# --- UTF-16 string pools: binary AXML manifest / layouts and resources.arsc (coverage atlas rows 22, 60, 61) ----------
ANS_RE_U16 = re.compile(rb"A\x00N\x00S\x00-\x00(?:[0-9A-Fa-f]\x00){16}")
_POOL_HDR = b"\x01\x00\x1c\x00"  # RES_STRING_POOL_TYPE, headerSize 0x1c
_POOL_MAX_ENTRY = 32 << 20
_POOL_MAX_STRINGS = 200_000
_POOL_DECODE_BUDGET = 400  # pool strings run through decode_any (each is bounded by its cap)
_POOL_ENCODED = re.compile(r"[\x21-\x7e]{16,4096}")


def _pool_len(b, i, utf8):
    """(length, next offset) of a ResStringPool length prefix (u8 pair with 0x80 flag / u16 pair with 0x8000 flag)."""
    if utf8:
        n = b[i]
        return ((n & 0x7F) << 8 | b[i + 1], i + 2) if n & 0x80 else (n, i + 1)
    n = int.from_bytes(b[i:i + 2], "little")
    if n & 0x8000:
        return (n & 0x7FFF) << 16 | int.from_bytes(b[i + 2:i + 4], "little"), i + 4
    return n, i + 2


def _pool_strings(b):
    """Every string of every ResStringPool chunk in an AXML / resources.arsc blob (UTF-8 and UTF-16 pools). Locates
    pool headers by signature, so it walks the manifest, compiled layouts, and all arsc packages alike; a malformed
    chunk is skipped, never raised."""
    out = []
    at = b.find(_POOL_HDR)
    while at >= 0 and len(out) < _POOL_MAX_STRINGS:
        try:
            size, count, _styles, flags, s_start = (int.from_bytes(b[at + o:at + o + 4], "little") for o in (4, 8, 12, 16, 20))
            end = at + size
            if 0x1c <= s_start <= size <= len(b) - at and count <= (size - 0x1c) // 4:
                utf8 = bool(flags & 0x100)
                base = at + s_start
                for k in range(min(count, _POOL_MAX_STRINGS - len(out))):
                    i = base + int.from_bytes(b[at + 0x1c + 4 * k:at + 0x20 + 4 * k], "little")
                    if i >= end:
                        continue
                    if utf8:
                        _, i = _pool_len(b, i, True)       # UTF-16 length, then the UTF-8 byte length
                        n, i = _pool_len(b, i, True)
                        out.append(b[i:min(i + n, end)].decode("utf-8", "replace"))
                    else:
                        n, i = _pool_len(b, i, False)
                        out.append(b[i:min(i + 2 * n, end)].decode("utf-16-le", "replace"))
        except (IndexError, ValueError):
            pass
        at = b.find(_POOL_HDR, at + 4)
    return out


def string_pool_scan(apk):
    """ANS tokens the ASCII scans miss: (1) a UTF-16LE `ANS-<16 hex>` in any zip entry (AXML manifest <meta-data
    android:value>, a UTF-16 arsc pool, a UTF-16 asset), then (2) the string pools of AndroidManifest.xml, res/*.xml
    and resources.arsc parsed and each pool string read directly and, when it looks encoded (printable, >= 16 chars),
    through decode_any (an encoded value in strings.xml). [] when absent; never raises."""
    hits = []
    try:
        with zipfile.ZipFile(apk) as z:
            pools = []
            for info in z.infolist():
                if info.is_dir() or info.file_size > _POOL_MAX_ENTRY:
                    continue
                try:
                    b = z.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError):
                    continue
                hits += [m.decode("utf-16-le") for m in ANS_RE_U16.findall(b)]
                n = info.filename
                if n == "AndroidManifest.xml" or n == "resources.arsc" or (n.startswith("res/") and n.endswith(".xml")):
                    if b[:2] in (b"\x03\x00", b"\x02\x00"):  # RES_XML_TYPE / RES_TABLE_TYPE
                        pools.append(b)
            if hits:
                return list(dict.fromkeys(hits))
            budget = _POOL_DECODE_BUDGET
            for b in pools:
                if b[:2] == b"\x02\x00" and not hits:  # resources.arsc: values the code reads by R id first
                    hits += resource_id_scan(apk)
                for s in _pool_strings(b):
                    m = ANS_RE_T.search(s)
                    if m:
                        hits.append(m.group(0))
                        continue
                    if budget > 0 and _POOL_ENCODED.fullmatch(s.strip()):
                        budget -= 1
                        d = decode_any(s.strip(), depth=2, cap=200, chain=False)
                        if d:
                            hits += ANS_RE_T.findall(d)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- resources.arsc entries reached through R.<type>.<name> id constants in dex code (coverage atlas rows 22, 61) ----
# string_pool_scan sees every arsc string but not WHICH one the app reads; a challenge that plants several ANS-shaped
# strings.xml values is disambiguated by the id the code loads (`const vX, 0x7fTTEEEE` / `const/high16` before
# getString / getText / getStringArray) or by the name it passes to Resources.getIdentifier(name, "string", pkg).
_RID_MAX_ARSC, _RID_MAX_DEX, _RID_DEADLINE_S, _RID_MAX_UNITS = 32 << 20, 32 << 20, 1.0, 4_000_000
_RID_PRIO = re.compile(r"proof|challenge|answer|flag|secret|token|verify|check", re.I)


def _rid_value(dt, data, gpool):
    """Res_value -> python value (string pool / int / bool / float / ref kept as ('ref', id))."""
    if dt == 0x03:
        return gpool[data] if data < len(gpool) else None
    if dt == 0x01 or dt == 0x02:
        return ("ref", data)
    if dt == 0x12:
        return bool(data)
    if dt in (0x10, 0x11):
        return data - (1 << 32) if dt == 0x10 and data & 0x80000000 else data
    if dt == 0x04:
        return struct.unpack("<f", struct.pack("<I", data))[0]
    return None if dt == 0 else ("raw", dt, data)


def _rid_config(b, o):
    """Short qualifier of a ResTable_config: '' (default) or 'fr', 'en-rUS', ... (language/country only)."""
    try:
        lang, country = b[o + 8:o + 10], b[o + 10:o + 12]
        q = "".join(chr(c) for c in lang if c) if lang[:1] < b"\x80" else lang.hex()
        if country[:1] != b"\0":
            q += "-r" + "".join(chr(c) for c in country if c)
        return q
    except IndexError:
        return ""


def resource_table(apk_or_bytes):
    """resources.arsc parsed (package / type / entry tables): {res id: {"type", "name", "values": [(config, value)]}}.
    Values are str / int / bool / float; a reference stays ("ref", id) and bag (array / plurals) entries are lists of
    their item values. Handles FLAG_SPARSE / FLAG_OFFSET16 type chunks and compact entries. {} when absent / malformed."""
    out = {}
    try:
        b = apk_or_bytes
        if not isinstance(b, (bytes, bytearray)):
            with zipfile.ZipFile(apk_or_bytes) as z:
                if z.getinfo("resources.arsc").file_size > _RID_MAX_ARSC:
                    return {}
                b = z.read("resources.arsc")
        if b[:4] != b"\x02\x00\x0c\x00":
            return {}
        u16 = lambda o: struct.unpack_from("<H", b, o)[0]  # noqa: E731
        u32 = lambda o: struct.unpack_from("<I", b, o)[0]  # noqa: E731
        end, gpool, at = min(u32(4), len(b)), [], 12
        while at + 8 <= end:
            typ, hsz, size = u16(at), u16(at + 2), u32(at + 4)
            if size < 8 or at + size > end:
                break
            if typ == 0x0001 and not gpool:
                gpool = _pool_strings(b[at:at + size])
            elif typ == 0x0200:
                pid = u32(at + 8)
                tpool = _pool_strings(b[at + u32(at + 268):at + size]) if u32(at + 268) else []
                kpool = _pool_strings(b[at + u32(at + 276):at + size]) if u32(at + 276) else []
                c = at + hsz
                while c + 8 <= at + size:
                    ct, ch, cs = u16(c), u16(c + 2), u32(c + 4)
                    if cs < 8 or c + cs > at + size:
                        break
                    if ct == 0x0201:
                        tid, flags, cnt, est = b[c + 8], b[c + 9], u32(c + 12), u32(c + 16)
                        cfg = _rid_config(b, c + 20)
                        tname = tpool[tid - 1] if 0 < tid <= len(tpool) else str(tid)
                        if flags & 0x01:  # FLAG_SPARSE: (u16 idx, u16 offset/4)
                            offs = [(u16(c + ch + 4 * k), 4 * u16(c + ch + 4 * k + 2)) for k in range(min(cnt, 65536))]
                        elif flags & 0x02:  # FLAG_OFFSET16
                            offs = [(k, 4 * u16(c + ch + 2 * k)) for k in range(min(cnt, 65536))
                                    if u16(c + ch + 2 * k) != 0xFFFF]
                        else:
                            offs = [(k, u32(c + ch + 4 * k)) for k in range(min(cnt, 65536)) if u32(c + ch + 4 * k) != 0xFFFFFFFF]
                        for idx, off in offs:
                            e = c + est + off
                            if e + 8 > c + cs:
                                continue
                            esz, efl = u16(e), u16(e + 2)
                            if efl & 0x0008:  # FLAG_COMPACT: key u16 in the size slot, dataType in the flags high byte
                                key, val = esz, _rid_value(efl >> 8, u32(e + 4), gpool)
                            elif efl & 0x0001:  # bag: parent, count, then (name, Res_value) items
                                key, n = u32(e + 4), u32(e + 12)
                                val, m = [], e + esz
                                for _ in range(min(n, 4096)):
                                    if m + 12 > c + cs:
                                        break
                                    val.append(_rid_value(b[m + 7], u32(m + 8), gpool))
                                    m += 12
                            else:
                                key, val = u32(e + 4), _rid_value(b[e + esz + 3], u32(e + esz + 4), gpool)
                            rid = (pid & 0xFF) << 24 | tid << 16 | idx
                            ent = out.setdefault(rid, {"type": tname, "name": kpool[key] if key < len(kpool) else None,
                                                       "values": []})
                            ent["values"].append((cfg, val))
                    c += cs
            at += size
    except Exception:  # noqa: BLE001 - truncated / impostor table: what was parsed so far
        pass
    return out


def _rid_resolve(tab, v, depth=0):
    if isinstance(v, tuple) and v[:1] == ("ref",) and depth < 8 and v[1] in tab:
        vals = tab[v[1]]["values"]
        return _rid_resolve(tab, next((x for c, x in vals if not c), vals[0][1]), depth + 1) if vals else None
    if isinstance(v, list):
        return [_rid_resolve(tab, x, depth + 1) for x in v]
    return v


def resource_id_refs(apk):
    """Which arsc entries the code reads: every `const`/`const/high16` 0xPPTTEEEE (PP = an arsc package id) in a dex
    method, and every Resources.getIdentifier(name, type, pkg) whose const-string name/type match an arsc entry.
    [{"id", "type", "name", "values": [(config, value)], "method", "via"}] ordered proof/ChallengeActivity-style
    methods first, then dex order. [] when absent; never raises."""
    refs, deadline, units = [], time.time() + _RID_DEADLINE_S, [0]
    try:
        tab = resource_table(apk)
        if not tab:
            return []
        pkgs = {rid >> 24 for rid in tab}
        by_name = {}
        for rid, e in tab.items():
            by_name.setdefault((e["type"], e["name"]), rid)
        with zipfile.ZipFile(apk) as z:
            dexes = [n for n in z.namelist() if re.fullmatch(r"classes\d*\.dex", n) and z.getinfo(n).file_size <= _RID_MAX_DEX]
            for dn in dexes:
                d = z.read(dn)
                if d[:4] != b"dex\n" or len(d) < 0x70:
                    continue
                tabs = _dnc_tables(d)
                if not tabs:
                    continue
                sget, _tdesc, mref = tabs
                for mi, _fl, code in _dnc_methods(d):
                    if not code or code + 16 > len(d) or time.time() > deadline:
                        continue
                    n_ins = struct.unpack_from("<I", d, code + 12)[0]
                    if n_ins > 1 << 18 or units[0] + n_ins > _RID_MAX_UNITS:
                        continue
                    units[0] += n_ins
                    ins = d[code + 16:code + 16 + 2 * n_ins]
                    me = mref(mi) or (None, None, (), None)
                    where = f"{me[0]}->{me[1]}"
                    ids, strs, ident, pc = [], [], False, 0
                    while pc < n_ins:
                        p = 2 * pc
                        if p + 2 > len(ins):
                            break
                        op, a8 = ins[p], ins[p + 1]
                        if op == 0 and a8 in (1, 2, 3):
                            if p + 8 > len(ins):
                                break
                            if a8 == 1:
                                pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
                            elif a8 == 2:
                                pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
                            else:
                                w, n = struct.unpack_from("<HI", ins, p + 2)
                                pc += 4 + (w * n + 1) // 2
                            continue
                        if p + 2 * _DOP_W[op] > len(ins):
                            break
                        if op == 0x14:  # const vAA, #+BBBBBBBB
                            ids.append(struct.unpack_from("<I", ins, p + 2)[0])
                        elif op == 0x15:  # const/high16 vAA, #+BBBB0000
                            ids.append(struct.unpack_from("<H", ins, p + 2)[0] << 16)
                        elif op in (0x1A, 0x1B):  # const-string(/jumbo)
                            s = sget(struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0])
                            if s is not None:
                                strs.append(s)
                        elif 0x6E <= op <= 0x72 or 0x74 <= op <= 0x78:
                            m = mref(struct.unpack_from("<H", ins, p + 2)[0])
                            if m and m[1] == "getIdentifier":
                                ident = True
                        pc += _DOP_W[op]
                    for rid in ids:
                        if rid >> 24 in pkgs and rid in tab:
                            refs.append((rid, where, "const"))
                    if ident:
                        types = [s for s in strs if s in {t for t, _ in by_name}] or ["string"]
                        for s in strs:
                            for t in types:
                                if (t, s) in by_name:
                                    refs.append((by_name[(t, s)], where, "getIdentifier"))
    except Exception:  # noqa: BLE001 - truncated / impostor APK: what was found so far
        pass
    out, seen = [], set()
    for rid, where, via in sorted(refs, key=lambda r: 0 if _RID_PRIO.search(r[1] or "") else 1):
        if (rid, where) in seen:
            continue
        seen.add((rid, where))
        e = tab[rid]
        out.append({"id": f"0x{rid:08x}", "type": e["type"], "name": e["name"],
                    "values": [(c, _rid_resolve(tab, v)) for c, v in e["values"]], "method": where, "via": via})
    return out


def _rid_flat(v):
    if isinstance(v, list):
        for x in v:
            yield from _rid_flat(x)
    elif isinstance(v, str):
        yield v


def resource_id_scan(apk):
    """ANS tokens of the arsc values the CODE reads (resource_id_refs order: proof/ChallengeActivity methods first), each
    value read directly and, when it looks encoded, through decode_any -- the decoy-aware pick among several arsc
    ANS-shaped strings. [] when absent; never raises."""
    hits, budget = [], _POOL_DECODE_BUDGET
    try:
        for r in resource_id_refs(apk):
            for _cfg, v in r["values"]:
                for s in _rid_flat(v):
                    m = ANS_RE_T.findall(s)
                    if m:
                        hits += m
                    elif budget > 0 and _POOL_ENCODED.fullmatch(s.strip()):
                        budget -= 1
                        dec = decode_any(s.strip(), depth=2, cap=200, chain=False)
                        if dec:
                            hits += ANS_RE_T.findall(dec)
    except Exception:  # noqa: BLE001
        pass
    return list(dict.fromkeys(hits))


# --- React Native Hermes bytecode string table (coverage atlas row 54) ------------------------------------------------
_HBC_MAGIC = b"\xc6\x1f\xbc\x03\xc1\x03\x19\x1f"
_HBC_MAX_ENTRY = 32 << 20
_HBC_MAX_STRINGS = 500_000
_HBC_DECODE_BUDGET = 400
_HBC_HEX = re.compile(r"(?:[0-9a-fA-F]{2}){16,}")
_HBC_B32 = re.compile(r"[A-Z2-7]{16,}=*")
_HBC_B64 = re.compile(r"(?=.*\d|.*[+/=])(?=.*[a-z])(?=.*[A-Z])(?:[A-Za-z0-9+/]{4})+(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?")


def _hbc_rank(r):
    """Decode order for Hermes string runs: strict hex / base32 / base64 shapes, then url-safe alphabets, then the rest
    (a real bundle has tens of thousands of identifier-like strings ahead of one encoded payload)."""
    if _HBC_HEX.fullmatch(r) or _HBC_B32.fullmatch(r) or _HBC_B64.fullmatch(r):
        return 0
    return 1 if re.fullmatch(r"[A-Za-z0-9_=-]{20,}", r) and re.search(r"\d", r) else 2


def _a4(i):
    return (i + 3) & ~3


def hermes_strings(b):
    """Every string of a Hermes bytecode (.hbc / index.android.bundle) blob: header -> function headers -> string
    kinds -> identifier hashes -> small string table (u32 isUTF16:1 offset:23 length:8; length 255 = index into the
    overflow table of {offset u32, length u32}) -> string storage (Latin-1 or UTF-16LE). [] when not HBC / truncated."""
    try:
        if b[:8] != _HBC_MAGIC or len(b) < 128:
            return []
        version = struct.unpack_from("<I", b, 8)[0]
        if not 40 <= version <= 255:
            return []
        fn_count, kind_count, ident_count, count, ovf_count, storage_size = struct.unpack_from("<6I", b, 40)
        if count > _HBC_MAX_STRINGS or max(fn_count, kind_count, ident_count, ovf_count) > _HBC_MAX_STRINGS:
            return []
        i = 128 + fn_count * (12 if version >= 97 else 16)   # header is 97..113 bytes, padded to 32 in every version
        i = _a4(_a4(i) + 4 * kind_count)
        i = _a4(i + 4 * ident_count)
        small, i = i, _a4(i + 4 * count)
        ovf, i = i, _a4(i + 8 * ovf_count)
        if i + storage_size > len(b):
            return []
        storage = b[i:i + storage_size]
        out = []
        for k in range(count):
            e = struct.unpack_from("<I", b, small + 4 * k)[0]
            utf16, off, n = e & 1, (e >> 1) & 0x7FFFFF, e >> 24
            if n == 0xFF:
                if off >= ovf_count:
                    continue
                off, n = struct.unpack_from("<II", b, ovf + 8 * off)
            raw = storage[off:off + (2 * n if utf16 else n)]
            out.append(raw.decode("utf-16-le", "replace") if utf16 else raw.decode("latin-1"))
        return out
    except (struct.error, IndexError, ValueError):
        return []


def hermes_string_scan(apk, deadline_s=1.0):
    """ANS tokens from the string table of every Hermes bytecode zip entry (assets/index.android.bundle or a renamed
    one, found by HBC magic): a literal token in any string (incl. UTF-16 ones), then printable runs (>= 16 chars,
    base64/hex-looking first) through decode_any. [] when absent; never raises."""
    hits, runs = [], []
    try:
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if info.is_dir() or info.file_size > _HBC_MAX_ENTRY or info.file_size < 128:
                    continue
                try:
                    with z.open(info) as f:
                        if f.read(8) != _HBC_MAGIC:
                            continue
                    b = z.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError):
                    continue
                for s in hermes_strings(b):
                    m = ANS_RE_T.findall(s)
                    if m:
                        hits += m
                    elif not hits:
                        runs += _POOL_ENCODED.findall(s)
        if hits:
            return list(dict.fromkeys(hits))
        runs = sorted(dict.fromkeys(runs), key=_hbc_rank)
        end = time.monotonic() + deadline_s
        for r in runs[:_HBC_DECODE_BUDGET]:
            if time.monotonic() > end:
                break
            d = decode_any(r, depth=2, cap=200, chain=False)
            if d:
                hits += ANS_RE_T.findall(d)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


def dex_strings(apk):
    """ANS tokens from the UTF-8 string pool of every classes*.dex (handles multidex, renamed code). When no literal
    token exists, falls back to cert_pin_scan() (a token encoded as a `sha256/<b64>` pin / NSC <pin>), then
    split_native_assembly() (an `ANS-` prefix + hex fragments split across dex and .so), then
    dex_array_scan() (a <clinit> byte/char array xor'd with a class constant), then rolling_xor_scan() (a puzzle value /
    dex byte array under a per-index rolling keystream), then clean_device_scan() (the value a root / emulator /
    debugger / Frida check lets through, evaluated on a clean Pixel), then root_signal_facts()'s clean tokens (a
    multi-signal vector in a mask / score / boolean[] / BitSet / EnumSet / Map keys the token), then
    exception_flow_scan() (the clean-device run with throw / catch handlers live), then dex_gated_branch_scan() (an encoded
    const-string behind a Java root / emulator / signature check), then native_export_scan() (a token computed by a .so export: xor constants, then unicorn emulation), then
    renamed_chain_scan(), then reflection_scan() (a static field / method reached via Class.forName + getDeclaredField/
    Method with encoded names), then method_handle_scan() (invoke-custom lambdas / MethodHandle invokeExact / Proxy
    handlers / desugared lambda classes), then jni_callback_scan() (a Java method a .so calls back by name via
    FindClass / GetStaticMethodID, run with the native's NewStringUTF literals), then dex_eval_scan() (a token computed by simple Dalvik bytecode, run by a tiny
    evaluator), then bytecode_vm_scan() (a custom bytecode program run by an in-dex switch VM, larger step budget),
    then flattened_cfg_scan() (a while/switch(state) flattened method: long run + static unflattening),
    then anti_debug_state_scan() (an anti-debug state machine's clean terminal value; 'debugged'-only values demoted),
    then coroutine_state_scan() (a Kotlin invokeSuspend state machine resumed in label order, L$0/I$0 spills),
    then decrypt_call_scan() (a decrypt helper run with its call sites' constant args), then
    string_obfuscator_scan() (StringFog / obfuscapk / Allatori call sites decoded by signature), then dex_slack_scan() (bytes appended past the header file_size / map_list slack / orphan strings),
    then binder_transact_scan() (a bound service's onTransact / Messenger handleMessage case, run per transaction code
    with the Parcel / Bundle reads answering the constants the case compares against),
    then biometric_auth_scan() (an AuthenticationCallback.onAuthenticationSucceeded run with a null and an identity
    CryptoObject, a createConfirmDeviceCredentialIntent caller's onActivityResult(RESULT_OK); failure-only values demoted),
    then digest_answer_scan() (`"ANS-"` + hex prefix of a MessageDigest / Mac over the method's inputs:
    candidates), then ans_compose_scan() (`"ANS-"` + numeric constants of the same method: candidates, not one answer).
    then whitebox_table_scan() (a white-box / T-table / S-box chain decrypt walk evaluated over static / asset arrays).
    A fallback hit that an anti-debug state machine only reaches when 'debugged' is demoted behind its clean value."""
    hits = []
    try:
        with zipfile.ZipFile(apk) as z:
            for n in z.namelist():
                if re.fullmatch(r"classes\d*\.dex", Path(n).name):
                    hits += [m.decode() for m in ANS_RE_B.findall(z.read(n))]
    except (OSError, zipfile.BadZipFile):
        pass
    if hits:  # a literal that sits in a shadowed class copy (host vs payload dex, row 84) goes behind the running copy's
        sh = classloader_shadow_facts(apk)
        dem = set(sh.get("demoted") or ())
        if dem & set(hits):
            hits = list(dict.fromkeys(sh["live"] + [h for h in hits if h not in dem] + [h for h in hits if h in dem]))
    literal = bool(hits)
    if not hits:
        hits = cert_pin_scan(apk)
    if not hits:
        hits = _eav_anchor(apk, split_native_assembly(apk))
    if not hits:
        hits = dex_array_scan(apk)
    if not hits:
        hits = rolling_xor_scan(apk)
    if not hits:
        hits = clean_device_scan(apk)
    if not hits:
        hits = root_signal_facts(apk)["clean"]
    if not hits:
        hits = exception_flow_scan(apk)
    if not hits:
        hits = dex_gated_branch_scan(apk)
    if not hits:
        hits = native_export_scan(apk)
    if not hits:
        hits = renamed_chain_scan(apk)
    if not hits:
        hits = reflection_scan(apk)
    if not hits:
        hits = method_handle_scan(apk)
    if not hits:
        hits = jni_callback_scan(apk)
    if not hits:
        hits = dex_eval_scan(apk)
    if not hits:
        hits = bytecode_vm_scan(apk)
    if not hits:
        hits = flattened_cfg_scan(apk)
    if not hits:
        hits = anti_debug_state_scan(apk)
    if not hits:
        hits = coroutine_state_scan(apk)
    if not hits:
        hits = decrypt_call_scan(apk)
    if not hits:
        hits = string_obfuscator_scan(apk)
    if not hits:
        hits = dex_slack_scan(apk)
    if not hits:
        hits = binder_transact_scan(apk)
    if not hits:
        hits = biometric_auth_scan(apk)
    if not hits:
        hits = _eav_anchor(apk, digest_answer_scan(apk))
    if not hits:
        hits = _eav_anchor(apk, ans_compose_scan(apk))
    if not hits:
        hits = whitebox_table_scan(apk)
    if hits and not literal:  # a static decode that is an anti-debug machine's honeypot goes behind its clean value
        rows = anti_debug_state_facts(apk)
        trap = {r["value"] for r in rows if not r["clean"]}
        if trap & set(hits):
            hits = list(dict.fromkeys([r["value"] for r in rows if r["clean"]] + [h for h in hits if h not in trap]
                                      + [h for h in hits if h in trap]))
    hits = [h for h in hits if not _eav_alphabet(h)]
    if len(hits) > 1 and not literal:  # row 98: the value the entry path computes leads its dead look-alikes
        ev = set(entry_evaluated_values(apk)) & set(hits)
        if ev:
            hits = [h for h in hits if h in ev] + [h for h in hits if h not in ev]
    return hits


# --- answer split across dex const-strings and .so .rodata (coverage atlas row 38) ------------------------------------
_HEXFRAG = re.compile(r"[0-9A-Fa-f]{4,16}")
_ANCHOR = re.compile(r"ANS-[0-9A-Fa-f]{0,15}")
_SPLIT_MAX_DEX = 32 << 20
_SPLIT_MAX_UNITS = 1_500_000  # code units decoded across all methods (keeps a 20 MB dex well under 1 s)
# Dalvik instruction width in 16-bit code units, by opcode (unused opcodes = 1).
_DOP_W = bytearray([1] * 256)
for _lo, _hi, _w in ((0x02, 0x02, 2), (0x03, 0x03, 3), (0x05, 0x05, 2), (0x06, 0x06, 3), (0x08, 0x08, 2),
                     (0x09, 0x09, 3), (0x13, 0x13, 2), (0x14, 0x14, 3), (0x15, 0x16, 2), (0x17, 0x17, 3),
                     (0x18, 0x18, 5), (0x19, 0x1a, 2), (0x1b, 0x1b, 3), (0x1c, 0x1c, 2), (0x1f, 0x20, 2),
                     (0x22, 0x23, 2), (0x24, 0x26, 3), (0x29, 0x29, 2), (0x2a, 0x2c, 3), (0x2d, 0x3d, 2),
                     (0x44, 0x6d, 2), (0x6e, 0x72, 3), (0x74, 0x78, 3), (0x90, 0xaf, 2), (0xd0, 0xe2, 2),
                     (0xfa, 0xfb, 4), (0xfc, 0xfd, 3), (0xfe, 0xff, 2)):
    for _o in range(_lo, _hi + 1):
        _DOP_W[_o] = _w


def _uleb(b, i):
    r = s = 0
    while True:
        x = b[i]
        i += 1
        r |= (x & 0x7F) << s
        if x < 0x80:
            return r, i
        s += 7
        if s > 35:
            raise ValueError("uleb")


def _dex_class_strings(d, budget):
    """[(class_idx, [[str, ...] per method in code order] + [static-value strings])] for one dex; strings that are hex
    fragments or `ANS-` anchors only. Methods whose bytecode cannot reference such a string are skipped cheaply."""
    import struct
    if d[:4] != b"dex\n" or len(d) < 0x70:
        return []
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_str, o_str, n_cls, o_cls = u32(0x38), u32(0x3C), u32(0x60), u32(0x64)
    if n_str > 1 << 22 or n_cls > 1 << 20 or o_str + 4 * n_str > len(d) or o_cls + 32 * n_cls > len(d):
        return []
    keep = {}
    for i in range(n_str):
        off = u32(o_str + 4 * i)
        _, j = _uleb(d, off)
        if d[j:j + 1] in (b"", b"\0") or not (0x30 <= d[j] <= 0x41 or 0x61 <= d[j] <= 0x66):
            continue  # first char can't start a hex fragment or "ANS-"
        e = d.find(b"\0", j, j + 20)
        if e < 0:
            continue
        t = d[j:e].decode("ascii", "replace")
        if _HEXFRAG.fullmatch(t) or _ANCHOR.fullmatch(t):
            keep[i] = t
    if not keep:
        return []
    out = []
    for c in range(n_cls):
        base = o_cls + 32 * c
        cdata, sval = u32(base + 24), u32(base + 28)
        meths = []
        if cdata and budget[0] > 0:
            i = cdata
            sf, i = _uleb(d, i)
            inf, i = _uleb(d, i)
            dm, i = _uleb(d, i)
            vm, i = _uleb(d, i)
            for _ in range(2 * (sf + inf)):
                _, i = _uleb(d, i)
            for _ in range(dm + vm):
                _, i = _uleb(d, i)
                _, i = _uleb(d, i)
                code, i = _uleb(d, i)
                if not code or code + 16 > len(d):
                    continue
                n_ins = u32(code + 12)
                ins = d[code + 16:code + 16 + 2 * n_ins]
                if b"\x1a" not in ins and b"\x1b" not in ins:
                    continue
                budget[0] -= n_ins
                if budget[0] < 0:
                    break
                got, pc = [], 0
                while pc < n_ins:
                    p = 2 * pc
                    op = ins[p]
                    if op == 0x1A or op == 0x1B:
                        si = struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0]
                        if si in keep:
                            got.append(keep[si])
                    elif op == 0 and ins[p + 1] in (1, 2, 3):  # switch / fill-array payloads
                        if ins[p + 1] == 1:
                            pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
                        elif ins[p + 1] == 2:
                            pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
                        else:
                            w, n = struct.unpack_from("<HI", ins, p + 2)
                            pc += 4 + (w * n + 1) // 2
                        continue
                    pc += _DOP_W[op]
                if got:
                    meths.append(got)
        if sval and sval < len(d):  # static final String constants (encoded_array of the class)
            try:
                n, i = _uleb(d, sval)
                vals = []
                for _ in range(min(n, 4096)):
                    t = d[i]
                    i += 1
                    vt, arg = t & 0x1F, t >> 5
                    if vt == 0x17:
                        vals.append(keep.get(int.from_bytes(d[i:i + arg + 1], "little")))
                    elif vt in (0x1C, 0x1D):
                        break  # nested array/annotation: stop rather than mis-parse
                    if vt not in (0x1E, 0x1F):
                        i += arg + 1
                vals = [v for v in vals if v]
                if vals:
                    meths.append(vals)
            except (IndexError, ValueError):
                pass
        if meths:
            out.append(meths)
    return out


def _so_rodata_seqs(b):
    """Hex fragments / anchors of one ELF .so: (.rodata strings by address, exported .rodata objects by symbol name)."""
    from elftools.elf.elffile import ELFFile
    elf = ELFFile(io.BytesIO(b))
    seqs = []
    for idx, sec in enumerate(elf.iter_sections()):
        if not (sec.name == ".rodata" or sec.name.startswith(".rodata.")) or sec["sh_type"] == "SHT_NOBITS":
            continue
        data, addr = sec.data(), sec["sh_addr"]
        seqs.append([t for t in (m.group(0).decode() for m in re.finditer(rb"[\x20-\x7e]{4,}", data))
                     if _HEXFRAG.fullmatch(t) or _ANCHOR.fullmatch(t)])
        syms = []
        for st in elf.iter_sections():
            if st["sh_type"] not in ("SHT_DYNSYM", "SHT_SYMTAB"):
                continue
            for s in st.iter_symbols():
                if s["st_info"]["type"] == "STT_OBJECT" and s["st_shndx"] == idx and s["st_size"]:
                    off = s["st_value"] - addr
                    t = data[off:off + min(s["st_size"], 32)].split(b"\0")[0].decode("latin-1")
                    if 0 <= off < len(data) and (_HEXFRAG.fullmatch(t) or _ANCHOR.fullmatch(t)):
                        syms.append((s.name, t))
        if syms:  # numbered siblings first (k_part1, k_part2 / secret_0, secret_1), then every export by name
            syms = sorted(dict(syms).items(), key=lambda kv: [int(x) if x.isdigit() else x
                                                              for x in re.split(r"(\d+)", kv[0])])
            stems = {}
            for name, t in syms:
                stems.setdefault(re.sub(r"\d+", "#", name), []).append(t)
            seqs[:0] = [v for k, v in stems.items() if "#" in k and len(v) > 1] + [[t for _, t in syms]]
    return seqs


def _windows(seq, need, maxlen=4):
    """Contiguous runs of hex fragments in `seq` whose total length is exactly `need` (need 0 -> the empty run)."""
    if need == 0:
        yield ""
        return
    for i in range(len(seq)):
        acc = ""
        for t in seq[i:i + maxlen]:
            if not _HEXFRAG.fullmatch(t):
                break
            acc += t
            if len(acc) >= need:
                if len(acc) == need:
                    yield acc
                break


def split_native_assembly(apk, cap=64):
    """Rebuild an answer split between the dex and native code: an `ANS-` prefix (alone or with some hex) plus 4-16 hex
    fragments from classes*.dex const-strings (code order per method, then the class's other methods / static values)
    and from lib/*/*.so .rodata (exported objects by symbol name, then strings by address). Candidates whose
    concatenation is `ANS-` + exactly 16 hex, most code-like order first: the anchor's own method alone, then that
    method + a native run, then the class's other dex fragments (+ native). Needs an anchor; [] when absent; never raises."""
    out = []
    try:
        dex_classes, so_seqs = [], []
        budget = [_SPLIT_MAX_UNITS]
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if info.file_size > _SPLIT_MAX_DEX:
                    continue
                n = info.filename
                try:
                    if re.fullmatch(r"classes\d*\.dex", Path(n).name):
                        dex_classes += _dex_class_strings(z.read(info), budget)
                    elif n.startswith("lib/") and n.endswith(".so") and len(so_seqs) < 16:
                        so_seqs += _so_rodata_seqs(z.read(info))
                except Exception:  # noqa: BLE001 - a malformed dex / .so contributes nothing
                    continue
        native = [s for s in so_seqs if s]

        def add(c):
            if ANS_RE_T.fullmatch(c) and c not in out and not _eav_alphabet(c):
                out.append(c)

        for meths in dex_classes:
            flat = [t for m in meths for t in m]
            for m in meths:
                for a, t in enumerate(m):
                    if not _ANCHOR.fullmatch(t):
                        continue
                    tail = [x for x in m[a + 1:] if _HEXFRAG.fullmatch(x)]
                    heads = [t]
                    for x in tail[:4]:
                        heads.append(heads[-1] + x)
                    for h in heads:
                        if len(h) == 20:
                            add(h)
                    for h in heads:
                        for seq in native:
                            for w in _windows(seq, 20 - len(h)):
                                add(h + w)
                    for w in _windows([x for x in flat if x not in m], 20 - len(t)):
                        add(t + w)
                    for seq in native + [flat]:
                        for w1 in _windows([x for x in flat if x not in m], 20 - len(t) - 8):
                            for w2 in _windows(seq, 8):
                                add(t + w1 + w2)
                    if len(out) >= cap:
                        return out[:cap]
        if not out:  # anchor on the native side: native run after it, then dex fragments in code order
            dflat = [t for meths in dex_classes for m in meths for t in m if _HEXFRAG.fullmatch(t)]
            for seq in native:
                for a, t in enumerate(seq):
                    if _ANCHOR.fullmatch(t):
                        rest = seq[a + 1:]
                        for k in range(0, 5):
                            h = t + "".join(rest[:k])
                            if k and not _HEXFRAG.fullmatch(rest[k - 1] if k <= len(rest) else ""):
                                break
                            if len(h) > 20:
                                break
                            for s2 in (dflat, seq):
                                for w in _windows(s2, 20 - len(h)):
                                    add(h + w)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return out[:cap]


# --- string-encryption helper: xor'd byte/char arrays built in <clinit> (coverage atlas rows 35, 46) -----------------
_DXA_MAX_DEX, _DXA_UNITS, _DXA_BUDGET_S = 32 << 20, 1_000_000, 0.6
_DXA_MAX_ARRS, _DXA_MAX_KEYS, _DXA_MAX_LEN, _DXA_DEEP = 256, 48, 4096, 64
_DXA_OPS = frozenset((0x26, 0xD7, 0xDF))  # fill-array-data, xor-int/lit16, xor-int/lit8 (plain xor-int is in every hashCode)
_DXA_APUT = bytes(range(0x4B, 0x52))


def _dxa_hot(ins):
    """A method worth walking: fill-array-data / xor-literal ops, or new-array followed by a long aput run."""
    ops = ins[0::2]
    return not _DXA_OPS.isdisjoint(ops) or (0x23 in ops and sum(ops.count(x) for x in _DXA_APUT) >= 16)


def _s16(v):
    return v - 0x10000 if v & 0x8000 else v


def _dex_array_classes(d, budget, deadline):
    """[(arrays, int_keys, str_keys)] per class of one dex: element lists from fill-array-data payloads and from
    new-array + aput-with-constants runs, plus the class's int literals (const*, xor/add lits, static values) and
    short const-strings. Only methods whose code holds an array / xor opcode are walked."""
    if d[:4] != b"dex\n" or len(d) < 0x70:
        return []
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_str, o_str, n_cls, o_cls = u32(0x38), u32(0x3C), u32(0x60), u32(0x64)
    if n_str > 1 << 22 or n_cls > 1 << 20 or o_str + 4 * n_str > len(d) or o_cls + 32 * n_cls > len(d):
        return []

    def sget(si):
        if si >= n_str:
            return None
        _, j = _uleb(d, u32(o_str + 4 * si))
        e = d.find(b"\0", j, j + 66)
        return d[j:e].decode("utf-8", "replace") if e > j else None

    out = []
    for c in range(n_cls):
        if budget[0] <= 0 or time.time() > deadline:
            break
        base = o_cls + 32 * c
        cdata, sval = u32(base + 24), u32(base + 28)
        arrs, ikeys, skeys = [], [], []
        if cdata:
            i = cdata
            sf, i = _uleb(d, i)
            inf, i = _uleb(d, i)
            dm, i = _uleb(d, i)
            vm, i = _uleb(d, i)
            for _ in range(2 * (sf + inf)):
                _, i = _uleb(d, i)
            codes = []
            for _ in range(dm + vm):
                _, i = _uleb(d, i)
                _, i = _uleb(d, i)
                code, i = _uleb(d, i)
                if code and code + 16 <= len(d):
                    n_ins = u32(code + 12)
                    codes.append((n_ins, d[code + 16:code + 16 + 2 * n_ins]))
            if not any(_dxa_hot(ins) for _, ins in codes):
                codes = []  # no array / xor op in the class: its constants can't be a decrypt key here
            for n_ins, ins in codes:
                budget[0] -= n_ins
                if budget[0] < 0:
                    break
                regs, built, pc = {}, {}, 0
                while pc < n_ins:
                    p = 2 * pc
                    op = ins[p]
                    if op == 0x12:  # const/4 vA, #+B
                        regs[ins[p + 1] & 0xF] = ((ins[p + 1] >> 4) ^ 8) - 8
                    elif op in (0x13, 0x15, 0x14):  # const/16, const/high16, const
                        v = struct.unpack_from("<H", ins, p + 2)[0]
                        v = _s16(v) if op == 0x13 else (v << 16 if op == 0x15 else struct.unpack_from("<i", ins, p + 2)[0])
                        regs[ins[p + 1]] = v
                        ikeys.append(v)
                    elif op in (0x1A, 0x1B):
                        s = sget(struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0])
                        if s and len(s) <= 64:
                            skeys.append(s)
                    elif op == 0x23:  # new-array vA, vB, type
                        a = ins[p + 1] & 0xF
                        if built.get(a):
                            arrs.append(built[a])
                        built[a] = {}
                        regs.pop(a, None)
                    elif 0x4B <= op <= 0x51:  # aput* vAA(value), vBB(array), vCC(index)
                        va, arr, ix = ins[p + 1], ins[p + 2], ins[p + 3]
                        if arr in built and va in regs and ix in regs and 0 <= regs[ix] < _DXA_MAX_LEN:
                            built[arr][regs[ix]] = regs[va]
                    elif op == 0x26:  # fill-array-data vAA, +BBBBBBBB -> payload (ident 0x0300, width, size, data)
                        q = 2 * (pc + struct.unpack_from("<i", ins, p + 2)[0])
                        if 0 <= q and q + 8 <= len(ins) and ins[q:q + 2] == b"\x00\x03":
                            w, n = struct.unpack_from("<HI", ins, q + 2)
                            if w in (1, 2, 4, 8) and 0 < n <= _DXA_MAX_LEN and q + 8 + w * n <= len(ins):
                                raw = ins[q + 8:q + 8 + w * n]
                                arrs.append(list(raw) if w == 1 else
                                            [int.from_bytes(raw[k:k + w], "little") for k in range(0, w * n, w)])
                    elif 0xD0 <= op <= 0xD7:  # binop/lit16
                        ikeys.append(_s16(struct.unpack_from("<H", ins, p + 2)[0]))
                    elif 0xD8 <= op <= 0xE2:  # binop/lit8
                        ikeys.append((ins[p + 3] ^ 0x80) - 0x80)
                    elif op == 0 and ins[p + 1] in (1, 2, 3):  # switch / fill-array payloads
                        if ins[p + 1] == 1:
                            pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
                        elif ins[p + 1] == 2:
                            pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
                        else:
                            w, n = struct.unpack_from("<HI", ins, p + 2)
                            pc += 4 + (w * n + 1) // 2
                        continue
                    elif op not in (0x01, 0x02, 0x03, 0x07, 0x08, 0x09, 0x0D):  # other writes clobber vAA / vA
                        regs.pop(ins[p + 1], None)
                        regs.pop(ins[p + 1] & 0xF, None)
                    pc += _DOP_W[op]
                for b in built.values():
                    if b and sorted(b) == list(range(len(b))):
                        arrs.append([b[k] for k in range(len(b))])
        if sval and sval < len(d) and (arrs or ikeys):  # static final int/char/byte/String constants
            try:
                n, i = _uleb(d, sval)
                for _ in range(min(n, 4096)):
                    t = d[i]
                    i += 1
                    vt, arg = t & 0x1F, t >> 5
                    if vt in (0x00, 0x02, 0x03, 0x04):
                        ikeys.append(int.from_bytes(d[i:i + arg + 1], "little", signed=vt != 0x03))
                    elif vt == 0x17:
                        s = sget(int.from_bytes(d[i:i + arg + 1], "little"))
                        if s and len(s) <= 64:
                            skeys.append(s)
                    elif vt in (0x1C, 0x1D):
                        break
                    if vt not in (0x1E, 0x1F):
                        i += arg + 1
            except (IndexError, ValueError):
                pass
        if arrs or ikeys:
            out.append((arrs, ikeys, skeys))
    return out


def _dxa_try(vals, key):
    """ANS token from element list `vals` under one key (int, str or element list): xor (repeating), xor/add/sub with
    the key + index, then -- for byte-sized data -- decode_any's codec chains (base64-of-xor and friends)."""
    kl = [key] if isinstance(key, int) else ([ord(ch) for ch in key] if isinstance(key, str) else list(key))
    if not kl:
        return None
    n = len(kl)
    outs = [[v ^ kl[i % n] for i, v in enumerate(vals)]]
    if n == 1:
        k = kl[0]
        outs += [[v - k for v in vals], [v + k for v in vals], [v ^ ((k + i) & 0xFF) for i, v in enumerate(vals)],
                 [v ^ (k ^ i) & 0xFF for i, v in enumerate(vals)]]
    else:
        outs += [[v - kl[i % n] for i, v in enumerate(vals)]]
    for o in outs:
        if all(0 <= x < 0x110000 for x in o):
            m = ANS_RE_T.search("".join(map(chr, o)))
        else:
            m = ANS_RE_T.search(bytes(x & 0xFF for x in o).decode("latin-1"))
        if m:
            return m.group(0)
    return None


def dex_array_scan(apk):
    """ANS tokens hidden by a string-encryption helper: a byte/char/int array built in <clinit> (fill-array-data payload
    or new-array + aput constants) decoded with a constant key from the same class (const / xor-int/lit literal, static
    final value, const-string, or a short sibling array), else from any class. Tries the array as-is, xor / add / sub
    (plain, repeating, key+index), and decode_any for codec layers. Static only (no code runs); [] when absent; never
    raises; bounded to ~0.6 s."""
    hits = []
    deadline = time.time() + _DXA_BUDGET_S
    try:
        classes, budget = [], [_DXA_UNITS]
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if info.file_size <= _DXA_MAX_DEX and re.fullmatch(r"classes\d*\.dex", Path(info.filename).name):
                    try:
                        classes += _dex_array_classes(z.read(info), budget, deadline)
                    except Exception:  # noqa: BLE001 - a malformed dex contributes nothing
                        continue
        glob_i, glob_s = [], []
        for _, ik, sk in classes:
            glob_i += ik
            glob_s += sk
        deep = [_DXA_DEEP]
        for arrs, ik, sk in classes:
            data = [a for a in arrs if len(a) >= 20][:_DXA_MAX_ARRS]
            if not data:
                continue
            short = [a for a in arrs if 0 < len(a) <= 32]
            keys = list(dict.fromkeys([0] + [k for k in ik if -0x10000 < k < 0x10000] + sk))
            keys += [a for a in short] + [k for k in dict.fromkeys(glob_i + glob_s)
                                          if k not in keys and (not isinstance(k, int) or -0x10000 < k < 0x10000)]
            keys = keys[:_DXA_MAX_KEYS + len(short)]
            for vals in data:
                for key in keys:
                    if time.time() > deadline:
                        return list(dict.fromkeys(hits))
                    t = _dxa_try(vals, key)
                    if t:
                        hits.append(t)
                        break
                else:
                    if all(0 <= v < 256 for v in vals):
                        raw = bytes(vals)
                        for key in [k for k in keys if not isinstance(k, list)][:8]:
                            if deep[0] <= 0 or time.time() > deadline:
                                break
                            deep[0] -= 1
                            t = decode_any(raw, key if key else None, depth=2, cap=400, chain=False)
                            m = t and ANS_RE_T.search(t)
                            if m:
                                hits.append(m.group(0))
                                break
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- root / emulator / debugger / signature check in Java gating a constant (coverage atlas rows 47-49) ---------------
_DGB_MARK = re.compile(r"(?i)(?:^|/)su$|magisk|supersu|superuser|test-keys|rootbeer|busybox|goldfish|ranchu|ro\.kernel\.qemu"
                       r"|qemu_pipe|genymotion|sdk_gphone|frida|27042|xposed|tracerpid|/proc/self/(?:maps|status)"
                       r"|^(?:isDebuggerConnected|getPackageInfo|getInstallerPackageName|getInstallingPackageName"
                       r"|getApkContentsSigners|hasSigningCertificateHistory|signatures|signingInfo|TAGS|HARDWARE)$")
_DGB_PRE = re.compile(rb"(?i)magisk|test-keys|goldfish|ranchu|qemu|frida|xposed|tracerpid|/su\0|rootbeer|busybox"
                      rb"|isDebuggerConnected|getPackageInfo|getInstall\w*PackageName|signingInfo|getApkContentsSigners")
_DGB_PAYLOAD = re.compile(r"[\x21-\x7e]{12,4096}")
_DGB_MAX_DEX, _DGB_UNITS, _DGB_BUDGET_S, _DGB_PAYLOADS, _DGB_KEYS = 32 << 20, 1_000_000, 0.7, 48, 24


def _dgb_methods(d, budget, deadline):
    """Per-method facts of one dex whose pool holds an anti-root / anti-emulator / signature marker:
    {method_idx: (marked, [string idx], [int literal], {invoked method idx})}, plus the string reader. ({}, None) else."""
    if d[:4] != b"dex\n" or len(d) < 0x70 or not _DGB_PRE.search(d):
        return {}, None
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_str, o_str, n_fld, o_fld, n_mth, o_mth, n_cls, o_cls = (u32(o) for o in (0x38, 0x3C, 0x50, 0x54, 0x58, 0x5C, 0x60, 0x64))
    if (n_str > 1 << 22 or n_cls > 1 << 20 or o_str + 4 * n_str > len(d) or o_cls + 32 * n_cls > len(d)
            or o_fld + 8 * n_fld > len(d) or o_mth + 8 * n_mth > len(d)):
        return {}, None

    @lru_cache(maxsize=None)
    def sget(si):
        if si >= n_str:
            return None
        _, j = _uleb(d, u32(o_str + 4 * si))
        e = d.find(b"\0", j, j + 4100)
        return d[j:e].decode("utf-8", "replace") if e >= j else None

    mark_s = {i for i in range(n_str) if _DGB_PRE.search(d, u32(o_str + 4 * i) + 1, u32(o_str + 4 * i) + 80)
              or (d[u32(o_str + 4 * i) + 1:u32(o_str + 4 * i) + 5] in (b"su\0", b"TAGS", b"HARD", b"sign"))}
    mark_s = {i for i in mark_s if _DGB_MARK.search(sget(i) or "")}
    mark_m = {i for i in range(n_mth) if u32(o_mth + 8 * i + 4) in mark_s}
    mark_f = {i for i in range(n_fld) if u32(o_fld + 8 * i + 4) in mark_s}
    out = {}
    for c in range(n_cls):
        cdata = u32(o_cls + 32 * c + 24)
        if not cdata:
            continue
        i = cdata
        sf, i = _uleb(d, i)
        inf, i = _uleb(d, i)
        dm, i = _uleb(d, i)
        vm, i = _uleb(d, i)
        for _ in range(2 * (sf + inf)):
            _, i = _uleb(d, i)
        for cnt in (dm, vm):
            midx = 0
            for _ in range(cnt):
                dlt, i = _uleb(d, i)
                midx += dlt
                _, i = _uleb(d, i)
                code, i = _uleb(d, i)
                if not code or code + 16 > len(d):
                    continue
                n_ins = u32(code + 12)
                budget[0] -= n_ins
                if budget[0] < 0 or time.time() > deadline:
                    return out, sget
                ins = d[code + 16:code + 16 + 2 * n_ins]
                marked, strs, ints, calls, pc = False, [], [], set(), 0
                while pc < n_ins and 2 * pc + 1 < len(ins):
                    p = 2 * pc
                    op = ins[p]
                    if op in (0x1A, 0x1B):
                        si = struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0]
                        strs.append(si)
                        marked |= si in mark_s
                    elif op == 0x12:
                        ints.append(((ins[p + 1] >> 4) ^ 8) - 8)
                    elif op in (0x13, 0x14) or 0xD0 <= op <= 0xD7:
                        ints.append(struct.unpack_from("<i", ins, p + 2)[0] if op == 0x14 else _s16(struct.unpack_from("<H", ins, p + 2)[0]))
                    elif 0xD8 <= op <= 0xE2:
                        ints.append((ins[p + 3] ^ 0x80) - 0x80)
                    elif 0x6E <= op <= 0x72 or 0x74 <= op <= 0x78:
                        mi = struct.unpack_from("<H", ins, p + 2)[0]
                        calls.add(mi)
                        marked |= mi in mark_m
                    elif 0x52 <= op <= 0x6D:  # iget*/iput*/sget*/sput* field@CCCC
                        marked |= struct.unpack_from("<H", ins, p + 2)[0] in mark_f
                    elif op == 0 and ins[p + 1] in (1, 2, 3):  # switch / fill-array payloads
                        if ins[p + 1] == 1:
                            pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
                        elif ins[p + 1] == 2:
                            pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
                        else:
                            w, n = struct.unpack_from("<HI", ins, p + 2)
                            pc += 4 + (w * n + 1) // 2
                        continue
                    pc += _DOP_W[op]
                out[midx] = (marked, strs, ints, calls)
    return out, sget


def dex_gated_branch_scan(apk):
    """ANS tokens behind a Java root / emulator / debugger / signature gate: methods that reference a check marker (su /
    magisk / test-keys / goldfish / ranchu / frida / TracerPid / /proc/self/maps / isDebuggerConnected / getPackageInfo
    signatures / installer ...), their callers (the method holding `if (isRooted()) ... else <secret>`) and those
    callers' callees (the decode helper). Their encoded const-strings are run through decode_any keyless, then with
    the small int literals and short strings of the same method set as keys (xor / add / sub, base64-of-xor ...).
    Static only; both branches are read and the ANS shape is the oracle. [] when absent; never raises; ~0.7 s bound."""
    hits = []
    deadline = time.time() + _DGB_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [i for i in z.infolist()
                     if i.file_size <= _DGB_MAX_DEX and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
            budget = [_DGB_UNITS]
            for info in dexes:
                meths, sget = _dgb_methods(z.read(info), budget, deadline)
                gated = {m for m, f in meths.items() if f[0]}
                if not gated:
                    continue
                callers = {m for m, f in meths.items() if f[3] & gated} - gated
                helpers = {c for m in callers for c in meths[m][3] if c in meths} - gated - callers
                payloads, keys = [], []
                for group in (callers, gated, helpers):
                    for m in sorted(group):
                        _, strs, ints, _ = meths[m]
                        for si in strs:
                            s = sget(si)
                            if not s:
                                continue
                            m_ans = ANS_RE_T.search(s)
                            if m_ans:
                                hits.append(m_ans.group(0))
                            elif _DGB_PAYLOAD.fullmatch(s) and not _DGB_MARK.search(s) and s not in payloads:
                                payloads.append(s)
                            elif 0 < len(s) <= 32 and s not in keys:
                                keys.append(s)
                        keys += [k for k in ints if 1 < abs(k) < 0x10000 and k not in keys and k not in (16, 0xFF)]
                payloads.sort(key=lambda s: -len(s))
                ikeys = [k for k in keys if isinstance(k, int)][:_DGB_KEYS]
                skeys = [k for k in keys if isinstance(k, str)][:_DGB_KEYS // 2]
                for s in payloads[:_DGB_PAYLOADS]:
                    for key in (None, *ikeys, *skeys):
                        if time.time() > deadline:
                            return list(dict.fromkeys(hits))
                        t = decode_any(s, key, depth=3 if key is None else 2, cap=600, chain=False)
                        m_ans = t and ANS_RE_T.search(t)
                        if m_ans:
                            hits.append(m_ans.group(0))
                            break
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))

# --- opaque predicates: constant-fold if-* over consts / classic opaque forms, drop dead blocks (coverage atlas row 72) --
_OPQ_BIN = ("add", "sub", "mul", "div", "rem", "and", "or", "xor", "shl", "shr", "ushr")
_OPQ_LIT = ("add", "rsub", "mul", "div", "rem", "and", "or", "xor", "shl", "shr", "ushr")
_OPQ_CMP = (lambda a, b: a == b, lambda a, b: a != b, lambda a, b: a < b,
            lambda a, b: a >= b, lambda a, b: a > b, lambda a, b: a <= b)
_OPQ_S1 = (0, 1, -1, 2, -2, 3, -3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 31, 64, 100, 127, 128, 255, 256,
           1000, 4095, 65535, 65536, 123457, 0x7FFFFFFF, -0x80000000, 0x7FFFFFFE, -0x7FFFFFFF, 0x55555555, 0x3039,
           0xDEADBEEF - (1 << 32), 46341, -46341, 0x10001, 2 ** 31 - 19, 2 ** 40 + 7, -(2 ** 63), 2 ** 63 - 1)
_OPQ_MAX_NODES, _OPQ_MAX_COMBOS = 48, 900


def _opq_wrap(v, w):
    v &= (1 << w) - 1
    return v - (1 << w) if v >> (w - 1) else v


def _opq_eval(e, env):
    """expr tree -> int under Java int/long semantics (raises ZeroDivisionError on /0, KeyError never: vars in env)."""
    k = e[0]
    if k == "k":
        return e[1]
    if k == "x":
        return env[e[1]]
    if k == "u":
        a = _opq_eval(e[2], env)
        f = e[1]
        return (_opq_wrap(-a, e[3]) if f == "neg" else _opq_wrap(~a, e[3]) if f == "not"
                else _opq_wrap(a, 32) if f == "l2i" else _opq_wrap(a, 8) if f == "i2b"
                else a & 0xFFFF if f == "i2c" else _opq_wrap(a, 16) if f == "i2s" else a)
    if k == "cmp":
        a, b = _opq_eval(e[1], env), _opq_eval(e[2], env)
        return (a > b) - (a < b)
    f, w = e[1], e[4]
    a, b = _opq_eval(e[2], env), _opq_eval(e[3], env)
    if f in ("div", "rem"):
        q = abs(a) // abs(b)
        q = q if (a < 0) == (b < 0) else -q
        return _opq_wrap(q if f == "div" else a - q * b, w)
    if f in ("shl", "shr", "ushr"):
        s = b & (w - 1)
        a = _opq_wrap(a, w)
        return _opq_wrap(a << s if f == "shl" else a >> s if f == "shr" else (a & ((1 << w) - 1)) >> s, w)
    return _opq_wrap(a + b if f == "add" else a - b if f == "sub" else b - a if f == "rsub" else a * b if f == "mul"
                     else a & b if f == "and" else a | b if f == "or" else a ^ b, w)


def _opq_vars(e, out, n=0):
    """Collect variable occurrences into `out` (list); returns the node count (tree size)."""
    n += 1
    if e[0] == "x":
        out.append(e[1])
    elif e[0] in ("u",):
        n = _opq_vars(e[2], out, n)
    elif e[0] == "cmp":
        n = _opq_vars(e[2], out, _opq_vars(e[1], out, n))
    elif e[0] == "b":
        n = _opq_vars(e[3], out, _opq_vars(e[2], out, n))
    return n


def _opq_fold(cmp, lhs, rhs):
    """True / False when `lhs <cmp> rhs` has one outcome for every input, else None. Constant operands fold exactly;
    otherwise only a classic opaque shape (some input used twice -- x*(x+1)%2, x*x%4, x|~x, 7*y*y-1 vs x*x) is
    sampled, so a plain `input == secret` gate is never folded."""
    occ = []
    if _opq_vars(lhs, occ) + _opq_vars(rhs, occ) > _OPQ_MAX_NODES:
        return None
    names = list(dict.fromkeys(occ))
    if names and (len(names) > 3 or len(occ) == len(names)):
        return None
    pool = _OPQ_S1 if len(names) <= 1 else _OPQ_S1[:30] if len(names) == 2 else _OPQ_S1[:9]
    seen = set()
    try:
        for combo in (itertools.product(pool, repeat=len(names)) if names else [()]):
            env = dict(zip(names, combo))
            seen.add(bool(cmp(_opq_eval(lhs, env), _opq_eval(rhs, env))))
            if len(seen) > 1:
                return None
    except (ZeroDivisionError, RecursionError, KeyError, TypeError):
        return None
    return seen.pop() if seen else None


def _opq_dead(ins, n_ins):
    """Dead code-unit offsets of one method: the blocks reachable only through an if-* whose condition folds to a
    constant (const operands or an opaque predicate). Empty set when nothing folds, so callers behave as before."""
    pcs, targets, pc = [], set(), 0
    while pc < n_ins and 2 * pc + 1 < len(ins):
        p = 2 * pc
        op, b1 = ins[p], ins[p + 1]
        if op == 0 and b1 in (1, 2, 3):
            if 2 * pc + 4 > len(ins):
                break
            if b1 == 1:
                pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
            elif b1 == 2:
                pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
            else:
                w, n = struct.unpack_from("<HI", ins, p + 2)
                pc += 4 + (w * n + 1) // 2
            continue
        w = _DOP_W[op]
        if 2 * pc + 2 * w > len(ins):
            break
        pcs.append((pc, op, b1, w))
        if 0x32 <= op <= 0x3D:
            targets.add(pc + struct.unpack_from("<h", ins, p + 2)[0])
        elif 0x28 <= op <= 0x2A:
            targets.add(pc + (_s16(b1 << 8) >> 8 if op == 0x28 else struct.unpack_from(
                "<h" if op == 0x29 else "<i", ins, p + 2)[0]))
        pc += w
    if not any(0x32 <= op <= 0x3D for _, op, _, _ in pcs):
        return set()
    reg, folds, blk = {}, {}, [0]
    rd = lambda r, pc: reg.get(r) or ("x", ("in", r, blk[0]))  # noqa: E731 - an input read in this block
    for pc, op, b1, w in pcs:
        p = 2 * pc
        a4, b4 = b1 & 0xF, b1 >> 4
        if pc in targets:
            reg, blk[0] = {}, pc
        h = lambda k: struct.unpack_from("<h", ins, p + 2 * k)[0]  # noqa: E731
        H = lambda k: struct.unpack_from("<H", ins, p + 2 * k)[0]  # noqa: E731
        if op == 0x12:
            reg[a4] = ("k", b4 - 16 if b4 & 8 else b4)
        elif op in (0x13, 0x16):
            reg[b1] = ("k", h(1))
        elif op in (0x14, 0x17):
            reg[b1] = ("k", struct.unpack_from("<i", ins, p + 2)[0])
        elif op == 0x15:
            reg[b1] = ("k", _opq_wrap(H(1) << 16, 32))
        elif op == 0x18:
            reg[b1] = ("k", struct.unpack_from("<q", ins, p + 2)[0])
        elif op == 0x19:
            reg[b1] = ("k", _opq_wrap(H(1) << 48, 64))
        elif op in (0x01, 0x04, 0x07):
            reg[a4] = rd(b4, pc)
        elif op in (0x02, 0x05, 0x08):
            reg[b1] = rd(H(1), pc)
        elif op in (0x03, 0x06, 0x09):
            reg[H(1)] = rd(H(2), pc)
        elif op in (0x7B, 0x7C, 0x7D, 0x7E, 0x81, 0x84, 0x8D, 0x8E, 0x8F):
            f = {0x7B: "neg", 0x7C: "not", 0x7D: "neg", 0x7E: "not", 0x81: "i2l", 0x84: "l2i", 0x8D: "i2b",
                 0x8E: "i2c", 0x8F: "i2s"}[op]
            reg[a4] = ("u", f, rd(b4, pc), 64 if op in (0x7D, 0x7E) else 32)
        elif 0x90 <= op <= 0xA5:
            i = op - 0x90 if op <= 0x9A else op - 0x9B
            reg[b1] = ("b", _OPQ_BIN[i], rd(ins[p + 2], pc), rd(ins[p + 3], pc), 32 if op <= 0x9A else 64)
        elif 0xB0 <= op <= 0xC5:
            i = op - 0xB0 if op <= 0xBA else op - 0xBB
            reg[a4] = ("b", _OPQ_BIN[i], rd(a4, pc), rd(b4, pc), 32 if op <= 0xBA else 64)
        elif 0xD0 <= op <= 0xE2:
            dst, src, lit, i = ((a4, b4, h(1), op - 0xD0) if op <= 0xD7 else
                                (b1, ins[p + 2], ins[p + 3] - 256 if ins[p + 3] & 0x80 else ins[p + 3], op - 0xD8))
            reg[dst] = ("b", _OPQ_LIT[i], rd(src, pc), ("k", lit), 32)
        elif op == 0x31:
            reg[b1] = ("cmp", rd(ins[p + 2], pc), rd(ins[p + 3], pc))
        elif 0x32 <= op <= 0x37:
            r = _opq_fold(_OPQ_CMP[op - 0x32], rd(a4, pc), rd(b4, pc))
            if r is not None:
                folds[pc] = r
        elif 0x38 <= op <= 0x3D:
            r = _opq_fold(_OPQ_CMP[op - 0x38], rd(b1, pc), ("k", 0))
            if r is not None:
                folds[pc] = r
        elif (0x0A <= op <= 0x0D or 0x1A <= op <= 0x1C or op == 0x22 or 0x2D <= op <= 0x31 or 0x44 <= op <= 0x4A
              or 0x60 <= op <= 0x66 or 0x90 <= op <= 0xAF):
            reg[b1] = ("x", (pc, b1))
        elif op in (0x20, 0x21, 0x23) or 0x52 <= op <= 0x58 or 0x7B <= op <= 0x8F or 0xA6 <= op - 0x10 <= 0xBF:
            reg[a4] = ("x", (pc, a4))
    if not folds:
        return set()
    order = [pc for pc, _, _, _ in pcs]
    nxt = dict(zip(order, order[1:]))
    info = {pc: (op, b1) for pc, op, b1, _ in pcs}

    def reach(use_folds):
        seen, todo = set(), [0]
        while todo:
            pc = todo.pop()
            if pc in seen or pc not in info:
                continue
            seen.add(pc)
            op, b1 = info[pc]
            p = 2 * pc
            if 0x0E <= op <= 0x11 or op == 0x27:
                continue
            if 0x28 <= op <= 0x2A:
                todo.append(pc + (_s16(b1 << 8) >> 8 if op == 0x28 else struct.unpack_from(
                    "<h" if op == 0x29 else "<i", ins, p + 2)[0]))
                continue
            if op in (0x2B, 0x2C):
                q = 2 * (pc + struct.unpack_from("<i", ins, p + 2)[0])
                try:
                    n = struct.unpack_from("<H", ins, q + 2)[0]
                    base = q + 8 if op == 0x2B else q + 4 + 4 * n
                    todo += [pc + struct.unpack_from("<i", ins, base + 4 * k)[0] for k in range(n)]
                except struct.error:
                    pass
            if 0x32 <= op <= 0x3D:
                f = folds.get(pc) if use_folds else None
                if f is not False:
                    todo.append(pc + struct.unpack_from("<h", ins, p + 2)[0])
                if f is True:
                    continue
            if pc in nxt:
                todo.append(nxt[pc])
        return seen

    return reach(False) - reach(True)



# --- decoy insertion: several ANS- candidates, the request builder picks one after `proof=` (coverage atlas row 67) ---
_PF_PRE = re.compile(rb"(?i)proof[=:]|evidence\?")
_PF_MARK = re.compile(r"(?i)(?:proof|evidence)\W{0,2}$")
_PF_SB = "Ljava/lang/StringBuilder;"
_PF_MAX_DEX, _PF_UNITS, _PF_BUDGET_S, _PF_DEPTH = 32 << 20, 1_000_000, 0.8, 5


def _pf_static_values(d, off, n_fields):
    """encoded_array at static_values_off -> [str | None] (strings by index, other constants None; stops on
    array / annotation values, whose layout we do not need)."""
    out = []
    try:
        size, i = _uleb(d, off)
        for _ in range(min(size, n_fields)):
            t = d[i]
            i += 1
            vt, arg = t & 0x1F, t >> 5
            if vt in (0x1C, 0x1D):
                break
            if vt in (0x1E, 0x1F):
                out.append(None)
                continue
            v = int.from_bytes(d[i:i + arg + 1], "little")
            i += arg + 1
            out.append(("sidx", v) if vt == 0x17 else None)
    except IndexError:
        pass
    return out


def _pf_proto(d, o_pro, pi, n_pro, tget):
    """proto_id -> full descriptor `(Ljava/lang/Object;I)Ljava/lang/String;` ("" when unreadable)."""
    try:
        if pi >= n_pro:
            return ""
        _, rti, po = struct.unpack_from("<III", d, o_pro + 12 * pi)
        ps = []
        if po and po + 4 <= len(d):
            n = struct.unpack_from("<I", d, po)[0]
            ps = [tget(struct.unpack_from("<H", d, po + 4 + 2 * k)[0]) or "?" for k in range(min(n, 255))]
        return "(" + "".join(ps) + ")" + (tget(rti) or "?")
    except struct.error:
        return ""


def _pf_dex(d, budget, deadline, facts):
    """One dex's request-builder facts into `facts` (keys by descriptor, so they join across classesN.dex):
    facts['ret'][mkey] / facts['put'][fkey] / facts['init'][fkey] -> [source], facts['sb'] -> [(class, method, [source])],
    a source being ('str', s) | ('field', fkey) | ('call', mkey) | ('cat', (sources...)) | None."""
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    u16 = lambda o: struct.unpack_from("<H", d, o)[0]  # noqa: E731
    n_str, o_str, n_typ, o_typ, n_pro, o_pro, n_fld, o_fld, n_mth, o_mth, n_cls, o_cls = (
        u32(o) for o in range(0x38, 0x68, 4))
    if (n_str > 1 << 22 or n_cls > 1 << 20 or o_str + 4 * n_str > len(d) or o_cls + 32 * n_cls > len(d)
            or o_typ + 4 * n_typ > len(d) or o_pro + 12 * n_pro > len(d)
            or o_fld + 8 * n_fld > len(d) or o_mth + 8 * n_mth > len(d)):
        return

    @lru_cache(maxsize=None)
    def sget(si):
        if si >= n_str:
            return None
        _, j = _uleb(d, u32(o_str + 4 * si))
        e = d.find(b"\0", j, j + 65536)
        return d[j:e].decode("utf-8", "replace") if e >= j else None

    tget = lru_cache(maxsize=None)(lambda ti: sget(u32(o_typ + 4 * ti)) if ti < n_typ else None)
    # keys carry the FULL descriptor (row 68: R8 overloads `a` across field types / param types sharing a shorty)
    fkey = lru_cache(maxsize=None)(lambda fi: (tget(u16(o_fld + 8 * fi)), sget(u32(o_fld + 8 * fi + 4)),
                                               tget(u16(o_fld + 8 * fi + 2)) or "") if fi < n_fld else None)

    @lru_cache(maxsize=None)
    def mkey(mi):
        if mi >= n_mth:
            return None
        pi = u16(o_mth + 8 * mi + 2)
        return (tget(u16(o_mth + 8 * mi)), sget(u32(o_mth + 8 * mi + 4)),
                sget(u32(o_pro + 12 * pi)) if pi < n_pro else None, _pf_proto(d, o_pro, pi, n_pro, tget))

    for c in range(n_cls):
        cdata, sv_off = u32(o_cls + 32 * c + 24), u32(o_cls + 32 * c + 28)
        if not cdata:
            continue
        i = cdata
        sf, i = _uleb(d, i)
        inf, i = _uleb(d, i)
        dm, i = _uleb(d, i)
        vm, i = _uleb(d, i)
        sfields, fidx = [], 0
        for k in range(sf + inf):
            dlt, i = _uleb(d, i)
            _, i = _uleb(d, i)
            fidx = (0 if k == sf else fidx) + dlt
            if k < sf:
                sfields.append(fidx)
        if sv_off and sv_off < len(d):
            for fi, v in zip(sfields, _pf_static_values(d, sv_off, len(sfields))):
                if v:
                    facts["init"].setdefault(fkey(fi), []).append(("str", sget(v[1])))
        cname = tget(u16(o_cls + 32 * c))
        for cnt in (dm, vm):
            midx = 0
            for _ in range(cnt):
                dlt, i = _uleb(d, i)
                midx += dlt
                _, i = _uleb(d, i)
                code, i = _uleb(d, i)
                if not code or code + 16 > len(d):
                    continue
                n_ins = u32(code + 12)
                budget[0] -= n_ins
                if budget[0] < 0 or time.time() > deadline:
                    return
                _pf_walk(d[code + 16:code + 16 + 2 * n_ins], n_ins, cname, mkey(midx), sget, fkey, mkey, facts)


def _pf_walk(ins, n_ins, cname, me, sget, fkey, mkey, facts):
    """Linear register-source tracking over one method (branches merge by last write -- good enough for a
    builder chain). Records returns, field puts and every StringBuilder's ordered append sources."""
    reg, sbs, last, pc = {}, {}, None, 0
    edges = facts["edges"].setdefault(me, []) if "edges" in facts else None  # renamed_chain_scan's call graph
    dead = _opq_dead(ins, n_ins)  # row 72: blocks behind an opaque / constant if-* never run
    while pc < n_ins and 2 * pc + 1 < len(ins):
        p = 2 * pc
        op, b1 = ins[p], ins[p + 1]
        a4 = b1 & 0xF
        if pc in dead:
            if op in (0x1A, 0x1B) and "dead" in facts:
                facts["dead"].add(sget(struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0]))
            pc += _DOP_W[op]
            continue
        if op == 0 and b1 in (1, 2, 3):  # switch / fill-array payloads
            if b1 == 1:
                pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
            elif b1 == 2:
                pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
            else:
                w, n = struct.unpack_from("<HI", ins, p + 2)
                pc += 4 + (w * n + 1) // 2
            continue
        w = _DOP_W[op]
        if 2 * pc + 2 * w > len(ins):
            break
        res, last = last, None
        if op in (0x1A, 0x1B):
            reg[b1] = ("str", sget(struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0]))
            if "live" in facts:
                facts["live"].add(reg[b1][1])
            if edges is not None:
                edges.append(reg[b1])
        elif op == 0x62:  # sget-object
            reg[b1] = ("field", fkey(struct.unpack_from("<H", ins, p + 2)[0]))
            if edges is not None:
                edges.append(reg[b1])
        elif op == 0x54:  # iget-object
            reg[a4] = ("field", fkey(struct.unpack_from("<H", ins, p + 2)[0]))
            if edges is not None:
                edges.append(reg[a4])
        elif op in (0x69, 0x5B):  # sput-object / iput-object
            src = reg.get(b1 if op == 0x69 else a4)
            facts["put"].setdefault(fkey(struct.unpack_from("<H", ins, p + 2)[0]), []).append(src)
        elif op == 0x07:
            reg[a4] = reg.get(b1 >> 4)
        elif op == 0x08:
            reg[b1] = reg.get(struct.unpack_from("<H", ins, p + 2)[0])
        elif op == 0x09:
            reg[struct.unpack_from("<H", ins, p + 2)[0]] = reg.get(struct.unpack_from("<H", ins, p + 4)[0])
        elif op == 0x0C:
            reg[b1] = res
        elif op == 0x11:
            facts["ret"].setdefault(me, []).append(reg.get(b1))
        elif op == 0x22:  # new-instance
            reg[b1] = ("sb", pc)
        elif 0x6E <= op <= 0x72 or 0x74 <= op <= 0x78:
            m = mkey(struct.unpack_from("<H", ins, p + 2)[0])
            if edges is not None and m:
                edges.append(("call", m))
            if op <= 0x72:
                cnt, g = b1 >> 4, b1 & 0xF
                regs = [ins[p + 4] & 0xF, ins[p + 4] >> 4, ins[p + 5] & 0xF, ins[p + 5] >> 4, g][:cnt]
            else:
                first = struct.unpack_from("<H", ins, p + 4)[0]
                regs = list(range(first, first + b1))
            recv = reg.get(regs[0]) if regs else None
            if m and m[0] == _PF_SB and recv and recv[0] == "sb":
                parts = sbs.setdefault(recv[1], [])
                if m[1] in ("append", "<init>") and len(regs) == 2 and m[2] in ("LL", "VL"):
                    parts.append(reg.get(regs[1]))
                last = recv if m[1] == "append" else ("cat", tuple(parts)) if m[1] == "toString" else None
            elif m and m[0] == "Ljava/lang/String;" and m[1] in ("intern", "trim", "toString") and recv:
                last = recv
            elif m and m[0] == "Ljava/lang/String;" and m[1] == "<init>" and len(regs) == 2 and recv:
                reg[regs[0]] = reg.get(regs[1])
            else:
                last = ("call", m) if m else None
        elif (0x0A <= op <= 0x0D or 0x01 <= op <= 0x06 or 0x12 <= op <= 0x19 or op == 0x1C or 0x44 <= op <= 0x4A
              or 0x60 <= op <= 0x66 or 0x90 <= op <= 0xAF or 0xD8 <= op <= 0xE2):
            reg[b1] = None
        elif op == 0x23 or 0x52 <= op <= 0x58 or 0x7B <= op <= 0x8F or 0xB0 <= op <= 0xD7:
            reg[a4] = None
        pc += w
    for parts in sbs.values():
        if any(s and s[0] == "str" and s[1] and _PF_MARK.search(s[1]) for s in parts):
            facts["sb"].append((cname, me, parts))


def _pf_resolve(src, facts, depth=_PF_DEPTH, seen=frozenset()):
    """A source -> its string value (const-string / static-field initializer / <clinit> put / getter return /
    StringBuilder concatenation), or None."""
    if not src or depth < 0 or src in seen:
        return None
    seen = seen | {src}
    kind, v = src
    if kind == "str":
        return v
    if kind == "cat":
        out = [_pf_resolve(s, facts, depth - 1, seen) for s in v]
        return "".join(out) if out and None not in out else None
    pool = (facts["put"].get(v, []) + facts["init"].get(v, [])) if kind == "field" else facts["ret"].get(v, [])
    vals = [r for r in (_pf_resolve(s, facts, depth - 1, seen) for s in pool) if r is not None]
    return next((r for r in reversed(vals) if ANS_RE_T.search(r)), vals[-1] if vals else None)


def _pf_targets(facts):
    """[(class, method, value)] for each builder: the source appended right after a `proof=` / `evidence?` literal."""
    out = []
    for cname, me, parts in facts["sb"]:
        for k, s in enumerate(parts[:-1]):
            if not (s and s[0] == "str" and s[1] and _PF_MARK.search(s[1])):
                continue
            nxt = parts[k + 1]
            if nxt and nxt[0] == "str" and nxt[1] and _PF_MARK.search(nxt[1]):
                continue  # "evidence?" then "proof=": the value follows the last marker
            out.append((cname, me, _pf_resolve(nxt, facts)))
    out.sort(key=lambda t: not re.search(r"(?i)challenge", t[0] or ""))
    return out


def proof_flow_candidates(apk):
    """Decoy insertion (row 67): the asset / dex / .so offer several ANS- values and the app's request builder picks one
    (`...evidence?...proof=` + X). Walks every StringBuilder chain holding a `proof=` / `evidence?` literal, resolves the
    value appended after it (const-string, sget -> <clinit> sput / static initializer, renamed getter -> its return,
    nested builder) and returns every ANS candidate of the APK as {"value", "source", "reached_by_proof"}, the
    proof-reached ones first (ChallengeActivity first). [] when absent; never raises; ~0.8 s bound."""
    reached, rest = [], []
    deadline = time.time() + _PF_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            facts = {"ret": {}, "put": {}, "init": {}, "sb": [], "dead": set(), "live": set()}
            budget, pool_tok = [_PF_UNITS], []
            for info in z.infolist():
                if info.file_size > _PF_MAX_DEX or info.is_dir():
                    continue
                b = z.read(info)
                is_dex = b[:4] == b"dex\n" and len(b) >= 0x70
                for m in ANS_RE_B.finditer(b):
                    pool_tok.append((m.group(0).decode(), ("dex:" if is_dex else "entry:") + info.filename))
                if is_dex and re.fullmatch(r"classes\d*\.dex", Path(info.filename).name) and _PF_PRE.search(b):
                    _pf_dex(b, budget, deadline, facts)
            targets = _pf_targets(facts)
            for cname, me, val in targets:
                m = val and ANS_RE_T.search(val)
                if not m and val and time.time() < deadline:
                    t = decode_any(val, depth=2, cap=400, chain=False)
                    m = t and ANS_RE_T.search(t)
                if m:
                    reached.append({"value": m.group(0), "source": f"proof:{cname}->{me and me[1]}",
                                    "reached_by_proof": True})
            if not reached and any(v is None for _, _, v in targets):
                # row 78: the builder appends a reflective / virtual call nobody resolved -> the ONE literal reachable
                # from the entry activity whose look-alike twins are all unreachable
                wired = list(dict.fromkeys(c["value"] for c in entry_reachable_candidates(apk)
                                           if c["reachable"] and c["twins"] and not c["twins_reached"]))
                if len(wired) == 1:
                    reached.append({"value": wired[0], "source": "proof:entry-reachable-twin", "reached_by_proof": True})
            seen = {c["value"] for c in reached}
            dead = {m.group(0) for s in facts["dead"] - facts["live"] if s for m in ANS_RE_T.finditer(s)}
            for tok, where in pool_tok:
                if tok not in seen:
                    seen.add(tok)
                    rest.append({"value": tok, "source": where, "reached_by_proof": False, "dead_only": tok in dead})
            rest.sort(key=lambda c: c["dead_only"])  # row 72: decoys only behind an opaque predicate rank last
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list({c["value"]: c for c in reached}.values()) + rest


def proof_flow_scan(apk):
    """Only the ANS values the request builder appends after `proof=` (see proof_flow_candidates). [] when absent."""
    return [c["value"] for c in proof_flow_candidates(apk) if c["reached_by_proof"]]


# --- identifier collisions: case / homoglyph / zero-width twins and descriptor-only overloads (coverage atlas row 68) ---
_IDC_ZW = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u200e\u200f\u2060\u2061\u2062\u2063\u2064\ufeff\u00ad\u180e"))
_IDC_CONF = str.maketrans("\u0430\u0435\u043e\u0440\u0441\u0443\u0445\u0456\u0458\u0455\u04cf\u0410\u0412\u0415"
                          "\u041a\u041c\u041d\u041e\u0420\u0421\u0422\u0425\u0391\u0392\u0395\u0396\u0397\u0399"
                          "\u039a\u039c\u039d\u039f\u03a1\u03a4\u03a5\u03a7\u03bf\u03b9\u0131\u2010\u2011",
                          "aeopcyxijslABEKMHOPCTXABEZHIKMNOPTYXoii--")
_IDC_MAX_DEX = 32 << 20


def _idc_forms(n):
    """name -> {form: normalized} for casefold / NFKC / zero-width-stripped / confusable skeleton."""
    zw = n.translate(_IDC_ZW)
    nf = unicodedata.normalize("NFKC", n)
    skel = unicodedata.normalize("NFKC", zw).translate(_IDC_CONF).casefold().replace("l", "1").replace("0", "o")
    return {"casefold": n.casefold(), "nfkc": nf, "zero_width": zw, "skeleton": skel}


def _idc_groups(names, kind, where, out):
    names = sorted(set(n for n in names if n))
    for form in ("casefold", "nfkc", "zero_width", "skeleton"):
        bucket = {}
        for n in names:
            bucket.setdefault(_idc_forms(n)[form], []).append(n)
        for k, grp in bucket.items():
            if len(grp) > 1:
                out.append({"kind": kind, "form": form, "where": where, "names": grp})


def identifier_collisions(apk):
    """Row 68 ("Name Collapse"): names the decompiled tree silently merges. From every classesN.dex (never the jadx /
    apktool tree -- a case-insensitive FS overwrites `a.java` with `A.java`):
      "classes":   class descriptors equal after casefold / NFKC / zero-width strip / confusable skeleton,
      "members":   fields / methods of one class colliding the same way,
      "overloads": one class + one raw name carried by several descriptors (R8 `a:I` + `a:Ljava/lang/String;`,
                   `a(Ljava/lang/Object;)` + `a(Ljava/lang/String;)`) -- resolve each invoke / sget by FULL descriptor.
    -> {"classes": [...], "members": [...], "overloads": [...]} (lists of dicts); empty lists when absent; never raises."""
    out = {"classes": [], "members": [], "overloads": []}
    try:
        with zipfile.ZipFile(apk) as z:
            descs, members = set(), {}
            for n in z.namelist():
                if not re.fullmatch(r"classes\d*\.dex", Path(n).name) or z.getinfo(n).file_size > _IDC_MAX_DEX:
                    continue
                d = z.read(n)
                if d[:4] != b"dex\n" or len(d) < 0x70:
                    continue
                u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
                u16 = lambda o: struct.unpack_from("<H", d, o)[0]  # noqa: E731
                n_str, o_str, n_typ, o_typ, n_pro, o_pro, n_fld, o_fld, n_mth, o_mth, n_cls, o_cls = (
                    u32(o) for o in range(0x38, 0x68, 4))
                if (n_str > 1 << 22 or o_str + 4 * n_str > len(d) or o_typ + 4 * n_typ > len(d)
                        or o_pro + 12 * n_pro > len(d) or o_fld + 8 * n_fld > len(d) or o_mth + 8 * n_mth > len(d)
                        or o_cls + 32 * n_cls > len(d)):
                    continue

                @lru_cache(maxsize=None)
                def sget(si, d=d, n_str=n_str, o_str=o_str):
                    if si >= n_str:
                        return None
                    _, j = _uleb(d, struct.unpack_from("<I", d, o_str + 4 * si)[0])
                    e = d.find(b"\0", j, j + 65536)
                    return d[j:e].decode("utf-8", "replace") if e >= j else None

                tget = lru_cache(maxsize=None)(lambda ti: sget(u32(o_typ + 4 * ti)) if ti < n_typ else None)
                for c in range(n_cls):
                    descs.add(tget(u16(o_cls + 32 * c)))
                for fi in range(n_fld):
                    o = o_fld + 8 * fi
                    members.setdefault(tget(u16(o)), set()).add(("field", sget(u32(o + 4)), tget(u16(o + 2)) or ""))
                for mi in range(n_mth):
                    o = o_mth + 8 * mi
                    members.setdefault(tget(u16(o)), set()).add(
                        ("method", sget(u32(o + 4)), _pf_proto(d, o_pro, u16(o + 2), n_pro, tget)))
            descs.discard(None)
            _idc_groups(descs, "class", "", out["classes"])
            for cls in sorted(c for c in members if c in descs):
                ms = members[cls]
                _idc_groups([m[1] for m in ms], "member", cls, out["members"])
                by = {}
                for kind, name, desc in ms:
                    by.setdefault((kind, name), []).append(desc)
                for (kind, name), ds in sorted(by.items(), key=lambda t: (t[0][0], t[0][1] or "")):
                    if len(ds) > 1:
                        out["overloads"].append({"class": cls, "kind": kind, "name": name, "descriptors": sorted(ds)})
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        pass
    return out


# --- R8-renamed class chain: the answer moved from the asset into 1-2 letter classes (coverage atlas row 45) ----------
_RC_FOLLOW = re.compile(r"(?i)follow\s+([\w.$/]+)\s*(?:->|=>|\u2192)\s*([\w.$/]+)")
_RC_IGNORE = re.compile(r"(?i)ignore\s+(?:the\s+)?field\s+([\w.$/]+)")
_RC_DEPTH, _RC_BUDGET_S, _RC_DECODE_S, _RC_HINT_MAX = 6, 0.8, 0.4, 4 << 20


def _rc_simple(desc):
    return re.split(r"[/$.]", (desc or "").strip("L;"))[-1]


def _rc_match(desc, name):
    """Hint name ('b', 'a.b', 'com.x.b') vs a class descriptor 'Lcom/x/b;'."""
    d = (desc or "").strip("L;").replace("/", ".").replace("$", ".")
    n = name.replace("/", ".").replace("$", ".")
    return d == n or d.endswith("." + n)


def _rc_hints(texts):
    """`follow X -> Y` / `ignore field Z` hint strings -> ({X: Y}, [Z]) (Z may be `cls.field`)."""
    follow, ignore = {}, []
    for t in texts:
        for m in _RC_FOLLOW.finditer(t):
            follow[m.group(1)] = m.group(2)
        ignore += [z for z in _RC_IGNORE.findall(t) if z not in ignore]
    return follow, ignore


def _rc_ignored(fk, ignore):
    if not fk:
        return False
    for z in ignore:
        cls, _, fld = z.rpartition(".")
        if fk[1] == fld and (not cls or _rc_match(fk[0], cls)):
            return True
    return False


# --- restore original names: ProGuard/R8 mapping.txt, kotlin.Metadata d2, dex SourceFile (coverage atlas row 45) -------
_PGM_FILE = re.compile(r"(?i)(?:^|/)(?:mapping[\w.-]*\.txt|[\w.-]*\.map|seeds\.txt|proguard[\w.-]*\.txt|r8[\w.-]*\.txt)$")
_PGM_CLS = re.compile(r"^([\w.$-]+) -> ([\w.$-]+):\s*$")
_PGM_MEM = re.compile(r"^\s+(?:\d+:\d+:)?[\w.$\[\]<>]+ ([\w$<>-]+)(?:\([^)]*\))?(?::\d+(?::\d+)?)? -> ([\w$<>-]+)\s*$")
_PGM_MAX_FILE, _PGM_MAX_LINES, _PGM_MAX_CLS = 8 << 20, 400_000, 1 << 16


def _pgm_parse(text, names):
    """ProGuard mapping text (`orig.Cls -> a.b:` + indented `type member -> x`) into names (see original_names)."""
    cur = None
    for k, line in enumerate(text.splitlines()):
        if k >= _PGM_MAX_LINES:
            break
        if not line or line.lstrip().startswith("#"):
            continue
        m = _PGM_CLS.match(line)
        if m:
            cur = m.group(2)
            names["classes"][m.group(1)] = cur
            names["src"].setdefault(cur, "mapping")
            continue
        m = cur and _PGM_MEM.match(line)
        if m:
            names["members"].setdefault(cur, {}).setdefault(m.group(1), m.group(2))


def _pgm_skip(d, i, depth=0):
    """Index past one encoded_value (dex annotation grammar); raises on garbage (callers catch)."""
    t = d[i]
    vt, va = t & 0x1F, t >> 5
    i += 1
    if vt == 0x1C:
        n, i = _uleb(d, i)
        for _ in range(min(n, 4096)):
            i = _pgm_skip(d, i, depth + 1)
        return i
    if vt == 0x1D:
        return _pgm_skip_ann(d, i, depth + 1)
    if vt in (0x1E, 0x1F):
        return i
    if depth > 8 or vt not in (0, 2, 3, 4, 6, 0x10, 0x11, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B):
        raise ValueError("encoded_value")
    return i + va + 1


def _pgm_skip_ann(d, i, depth):
    _, i = _uleb(d, i)
    n, i = _uleb(d, i)
    for _ in range(min(n, 256)):
        _, i = _uleb(d, i)
        i = _pgm_skip(d, i, depth)
    return i


def _pgm_d2(d, ann_off, tdesc, sget):
    """The string array `d2` of a class's kotlin.Metadata annotation ([] when absent)."""
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    cls_set = u32(ann_off)
    if not cls_set or cls_set + 4 > len(d):
        return []
    for k in range(min(u32(cls_set), 64)):
        i = u32(cls_set + 4 + 4 * k) + 1  # annotation_item: visibility byte, then encoded_annotation
        ti, i = _uleb(d, i)
        if tdesc(ti) != "Lkotlin/Metadata;":
            continue
        n, i = _uleb(d, i)
        for _ in range(min(n, 32)):
            ni, i = _uleb(d, i)
            if sget(ni) == "d2" and d[i] & 0x1F == 0x1C:
                cnt, j = _uleb(d, i + 1)
                out = []
                for _ in range(min(cnt, 4096)):
                    if d[j] & 0x1F != 0x17:
                        j = _pgm_skip(d, j)
                        continue
                    w = (d[j] >> 5) + 1
                    out.append(sget(int.from_bytes(d[j + 1:j + 1 + w], "little")) or "")
                    j += 1 + w
                return out
            i = _pgm_skip(d, i)
    return []


def _pgm_dex(d, names):
    """dex class_defs: SourceFile stem (javac/kotlinc `Foo.java`/`Foo.kt` kept by -keepattributes SourceFile) and the
    first `L...;` entry of kotlin.Metadata d2 as the original name of each renamed class."""
    tabs = _dnc_tables(d)
    if not tabs:
        return
    sget, tdesc, _ = tabs
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_cls, o_cls = u32(0x60), u32(0x64)
    if n_cls > _PGM_MAX_CLS or o_cls + 32 * n_cls > len(d):
        return
    by_src = {}
    for c in range(n_cls):
        desc = tdesc(u32(o_cls + 32 * c))
        if not desc or not desc.startswith("L"):
            continue
        dotted = desc[1:-1].replace("/", ".")
        ann = u32(o_cls + 32 * c + 20)
        if ann and ann + 16 <= len(d):
            try:
                for s in _pgm_d2(d, ann, tdesc, sget):
                    if re.fullmatch(r"L[\w/$]+;", s):
                        if s != desc:
                            names["classes"].setdefault(s[1:-1].replace("/", "."), dotted)
                            names["src"].setdefault(dotted, "kotlin.Metadata")
                        break
            except (IndexError, ValueError, struct.error):
                pass
        si = u32(o_cls + 32 * c + 16)
        sf = sget(si) if si != 0xFFFFFFFF else None
        stem = re.fullmatch(r"([A-Za-z_$][\w$]*)\.(?:java|kt)", sf or "")
        if stem and "$" not in dotted and stem.group(1) not in ("SourceFile", _rc_simple(desc)):
            by_src.setdefault(stem.group(1), []).append(dotted)
    for stem, cls in by_src.items():
        if len(cls) == 1:  # one top-level class per source file; several = ambiguous, skip
            names["classes"].setdefault(stem, cls[0])
            names["src"].setdefault(cls[0], "SourceFile")


def _pgm_names(z, dex_blobs=None):
    names = {"classes": {}, "members": {}, "src": {}}
    for info in z.infolist():
        if not info.is_dir() and info.file_size <= _PGM_MAX_FILE and _PGM_FILE.search(info.filename):
            _pgm_parse(z.read(info).decode("utf-8", "replace"), names)
    if dex_blobs is None:
        dex_blobs = [z.read(n) for n in z.namelist() if re.fullmatch(r"classes\d*\.dex", Path(n).name)
                     and z.getinfo(n).file_size <= _PF_MAX_DEX]
    for b in dex_blobs:
        if b[:4] == b"dex\n" and len(b) >= 0x70:
            _pgm_dex(b, names)
    return names


def original_names(apk):
    """Renamed -> original facts of an R8/ProGuard-shrunk APK, from a shipped mapping (assets/mapping.txt, *.map,
    seeds.txt: `orig.Cls -> a:` + indented `type orig -> b`), kotlin.Metadata d2 and dex SourceFile.
    -> {"classes": {original: renamed}, "renamed": {renamed: original}, "members": {renamed_cls: {orig: renamed}},
    "src": {renamed: "mapping"|"kotlin.Metadata"|"SourceFile"}}; empty dicts when absent; never raises."""
    names = {"classes": {}, "members": {}, "src": {}}
    try:
        with zipfile.ZipFile(apk) as z:
            names = _pgm_names(z)
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        pass
    names["renamed"] = {}
    for o, r in names["classes"].items():
        names["renamed"].setdefault(r, o)
    return names


def _pgm_lookup(names, n):
    """Original class name (full `com.x.Foo` or simple `Foo`) -> renamed dotted name, or None."""
    n = n.replace("/", ".")
    if n in names["classes"]:
        return names["classes"][n]
    hits = {r for o, r in names["classes"].items() if o.replace("$", ".").rsplit(".", 1)[-1] == n.rsplit(".", 1)[-1]
            and (o.endswith("." + n) or "." not in n)}
    return hits.pop() if len(hits) == 1 else None


def _pgm_translate(follow, ignore, names, known):
    """Rewrite `follow X -> Y` / `ignore field C.f` hints that use original names into the renamed classes/members.
    A name already matching a dex class (`known` descriptors) is left as is."""
    if not names["classes"]:
        return follow, ignore

    def cls(n):
        if any(_rc_match(k, n) for k in known):
            return n
        return _pgm_lookup(names, n) or n
    follow = dict(follow, **{cls(x): cls(y) for x, y in follow.items()})
    extra = []
    for zf in ignore:
        c, _, f = zf.rpartition(".")
        if not c:
            continue
        rc = cls(c)
        if rc != c:
            extra.append(rc + "." + names["members"].get(rc, {}).get(f, f))
    return follow, ignore + [e for e in extra if e not in ignore]


def renamed_chain_candidates(apk, hints=None):
    """R8-renamed chain (row 45): index the dex's field values (static initialisers, <clinit>/<init> puts of consts)
    and method returns, walk invoke / sget / iget edges from ChallengeActivity.onCreate (depth <= 6) through the
    renamed classes and collect every value reached, each fed to decode_any. Hint strings in the dex / assets (or
    `hints`, e.g. the contract text) of the form `follow X -> Y` put class Y's values first and `ignore field Z` drops
    field Z (and any value equal to it); hints naming ORIGINAL classes/fields are first mapped to the renamed ones
    (shipped ProGuard mapping, kotlin.Metadata d2, dex SourceFile; see original_names). -> [{"value", "source", "tier"}] best first; [] when absent; never raises."""
    out, dropped = [], set()
    deadline = time.time() + _RC_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            facts = {"ret": {}, "put": {}, "init": {}, "sb": [], "edges": {}}
            budget, texts = [_PF_UNITS], [hints] if isinstance(hints, str) else list(hints or [])
            for info in z.infolist():
                if info.is_dir() or info.file_size > _PF_MAX_DEX:
                    continue
                if re.fullmatch(r"classes\d*\.dex", Path(info.filename).name):
                    b = z.read(info)
                    if b[:4] == b"dex\n" and len(b) >= 0x70:
                        texts += [m.decode("utf-8", "replace") for m in
                                  re.findall(rb"(?i)(?:follow|ignore)[^\x00]{2,200}", b)]
                        _pf_dex(b, budget, deadline, facts)
                elif info.file_size <= _RC_HINT_MAX and not info.filename.endswith((".so", ".png", ".jpg", ".arsc")):
                    b = z.read(info)
                    texts += [m.decode("utf-8", "replace") for m in
                              re.findall(rb"(?i)(?:follow|ignore)[^\x00\"\n]{2,200}", b)]
            follow, ignore = _rc_hints(texts)
            edges = facts["edges"]
            if follow or ignore:  # hints naming original classes: restore through mapping / Metadata / SourceFile
                known = {k[0] for k in list(edges) + list(facts["put"]) + list(facts["init"]) + list(facts["ret"]) if k}
                follow, ignore = _pgm_translate(follow, ignore, _pgm_names(z), known)

            def field_vals(fk):
                if _rc_ignored(fk, ignore):
                    return []
                return [_pf_resolve(s, facts) for s in facts["put"].get(fk, []) + facts["init"].get(fk, [])]

            def ret_vals(mk):
                return [_pf_resolve(s, facts) for s in facts["ret"].get(mk, [])]

            for fk in set(facts["put"]) | set(facts["init"]):
                if _rc_ignored(fk, ignore):
                    dropped.update(v for s in facts["put"].get(fk, []) + facts["init"].get(fk, [])
                                   for v in [_pf_resolve(s, facts)] if v)
            found = []  # (tier, value, source)
            # tier 0: the follow target's own fields / returns
            for tgt in follow.values():
                for fk in sorted(k for k in set(facts["put"]) | set(facts["init"]) if k and _rc_match(k[0], tgt)):
                    found += [(0, v, f"follow:{_rc_simple(fk[0])}.{fk[1]}") for v in field_vals(fk)]
                for mk in sorted(k for k in facts["ret"] if k and _rc_match(k[0], tgt)):
                    found += [(0, v, f"follow:{_rc_simple(mk[0])}.{mk[1]}()") for v in ret_vals(mk)]
            # tier 1/2: BFS from ChallengeActivity.onCreate over the call graph
            acts = [k for k in edges if k and re.search(r"ChallengeActivity", k[0] or "")]
            start = [k for k in acts if k[1] == "onCreate"] or acts
            seen, frontier = set(start), list(start)
            for depth in range(_RC_DEPTH + 1):
                nxt = []
                for mk in frontier:
                    found += [(1, v, f"ret:{_rc_simple(mk[0])}.{mk[1]}()") for v in ret_vals(mk)]
                    for e in edges.get(mk, []):
                        if not e:
                            continue
                        if e[0] == "field":
                            found += [(1, v, f"field:{_rc_simple(e[1] and e[1][0])}.{e[1] and e[1][1]}")
                                      for v in field_vals(e[1])]
                        elif e[0] == "str":
                            found.append((2, e[1], f"const:{_rc_simple(mk[0])}.{mk[1]}"))
                        elif e[0] == "call" and e[1] in edges and e[1] not in seen and depth < _RC_DEPTH:
                            seen.add(e[1])
                            nxt.append(e[1])
                frontier = nxt
            dl2 = time.time() + _RC_DECODE_S
            for tier, v, src in sorted(found, key=lambda t: t[0]):
                if not v or v in dropped:
                    continue
                m = ANS_RE_T.search(v)
                if not m and time.time() < dl2 and len(v) >= 8:
                    t = decode_any(v, depth=2, cap=400, chain=False)
                    m = t and ANS_RE_T.search(t)
                if m and m.group(0) not in dropped:
                    out.append({"value": m.group(0), "source": src, "tier": tier})
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    uniq = {}
    for c in out:
        uniq.setdefault(c["value"], c)
    return list(uniq.values())


def mapping_restore_scan(apk, hints=None):
    """renamed_chain_scan() for an APK whose renamed classes can be named back (original_names(): shipped mapping.txt /
    kotlin.Metadata d2 / SourceFile), so `follow <orig> -> <orig>` / `ignore field <Orig>.<field>` hints resolve.
    [] when no original names are recoverable; never raises."""
    if not original_names(apk)["classes"]:
        return []
    return renamed_chain_scan(apk, hints)


def renamed_chain_scan(apk, hints=None):
    """ANS values reached from ChallengeActivity.onCreate through R8-renamed classes, hint-ranked
    (see renamed_chain_candidates). [] when absent."""
    return [c["value"] for c in renamed_chain_candidates(apk, hints)]

# --- JNI secret computed inside a .so export, not a literal (coverage atlas rows 37, 39, 40) --------------------------
_NSO_MAX_SO, _NSO_MAX_BYTES, _NSO_MAX_FUNCS, _NSO_FUNC_CAP = 8, 32 << 20, 48, 16384
_NSO_BUDGET_S, _NSO_DECODE_S, _NSO_FN_US, _NSO_FN_INSNS = 1.2, 0.3, 150_000, 2_000_000
_NSO_PROBE_S = 0.6  # the clean-device probe pass (row 66), on top of the plain emulation
_NSO_DATA = re.compile(r"\.(rodata|data)(\.|$)|\.data\.rel\.ro")
_NSO_JNI = {6: "FindClass", 167: "NewStringUTF", 169: "GetStringUTFChars", 215: "RegisterNatives"}
_NSO_ALLOC = {"malloc", "_Znwm", "_Znam", "_Znwj", "_Znaj", "calloc", "realloc", "strdup"}
# e_machine -> (unicorn arch/mode names, capstone arch/mode names, arg regs, return reg, ret insn, reloc types)
_NSO_ARCH = {
    "EM_X86_64": (("UC_ARCH_X86", "UC_MODE_64"), ("CS_ARCH_X86", "CS_MODE_64"),
                  ("RDI", "RSI", "RDX", "RCX", "R8", "R9"), "RAX", b"\xc3", {8: "rel", 6: "sym", 7: "sym", 1: "sym"}),
    "EM_AARCH64": (("UC_ARCH_ARM64", "UC_MODE_ARM"), ("CS_ARCH_ARM64", "CS_MODE_ARM"),
                   ("X0", "X1", "X2", "X3", "X4", "X5"), "X0", b"\xc0\x03\x5f\xd6",
                   {1027: "rel", 1025: "sym", 1026: "sym", 257: "sym"}),
    # 32-bit ABIs (row 40: armeabi-v7a Thumb / x86): REL relocations (addend in place); x86 passes args on the stack
    "EM_ARM": (("UC_ARCH_ARM", "UC_MODE_ARM"), ("CS_ARCH_ARM", "CS_MODE_ARM"),
               ("R0", "R1", "R2", "R3"), "R0", b"\x1e\xff\x2f\xe1", {23: "rel", 21: "sym", 22: "sym", 2: "abs"}),
    "EM_386": (("UC_ARCH_X86", "UC_MODE_32"), ("CS_ARCH_X86", "CS_MODE_32"),
               (), "EAX", b"\xc3", {8: "rel", 6: "sym", 7: "sym", 1: "abs"}),
}


# Clean-device libc answers for the unicorn runner's probe pass (row 66: anti-debug inside the JNI export): ptrace /
# prctl succeed, fork's child never runs, /proc/<self>/status says TracerPid 0, /proc/<self>/maps has no frida/xposed,
# su / frida / emulator paths are absent, kill / raise / exit end the run as a trap path, clocks step 1 us per call,
# pthread_create runs its start routine inline once (until it returns, sleeps or exits).
_NSO_PROBE_IMPORTS = {"ptrace", "prctl", "fork", "vfork", "fopen", "fopen64", "open", "open64", "__open_2", "openat",
                      "__openat_2", "access", "faccessat", "stat", "lstat", "stat64", "lstat64", "__xstat", "__lxstat",
                      "fstatat", "newfstatat", "pthread_create", "kill", "raise", "tgkill", "getppid",
                      "clock_gettime", "gettimeofday", "time", "__system_property_get", "__system_property_find",
                      "__system_property_read", "__system_property_read_callback", "popen", "opendir", "dlopen"}
_NSO_PROBE_STATUS = (b"Name:\tarena\nUmask:\t0077\nState:\tS (sleeping)\nTgid:\t4242\nNgid:\t0\nPid:\t4242\n"
                     b"PPid:\t600\nTracerPid:\t0\nUid:\t10123\t10123\t10123\t10123\nGid:\t10123\t10123\t10123\t10123\n"
                     b"FDSize:\t128\nThreads:\t17\nSigQ:\t0/31424\n")
_NSO_PROBE_MAPS = (b"12c00000-2ac00000 rw-p 00000000 00:00 0                          [anon:dalvik-main space]\n"
                   b"70000000-70100000 r-xp 00000000 fd:00 1201                       /system/lib64/libc.so\n"
                   b"70100000-70200000 r-xp 00000000 fd:00 1202                       /system/lib64/libart.so\n"
                   b"7ffff0000000-7ffff0021000 rw-p 00000000 00:00 0                  [stack]\n")
_NSO_PROBE_PROC = re.compile(rb"/proc/(?:self|thread-self|\d+)(?:/task/(?:self|\d+))?/(\w+)$")
# rows 66 / 95: a stock, locked, unrooted phone's system properties (unset ones read ""), its mount table (no magisk /
# tmpfs-on-/system / overlay) and what popen'd probe commands print there (`which su` / `ls /data/adb`: nothing)
_NSO_PROBE_PROPS = {b"ro.build.tags": b"release-keys", b"ro.debuggable": b"0", b"ro.secure": b"1",
                    b"ro.build.type": b"user", b"ro.boot.verifiedbootstate": b"green", b"ro.boot.flash.locked": b"1",
                    b"ro.boot.vbmeta.device_state": b"locked", b"ro.boot.veritymode": b"enforcing",
                    b"ro.boot.warranty_bit": b"0", b"ro.warranty_bit": b"0", b"ro.adb.secure": b"1",
                    b"ro.hardware": b"qcom", b"ro.board.platform": b"kona", b"ro.product.board": b"kona",
                    b"ro.boot.hardware": b"qcom", b"ro.product.model": b"Pixel 5", b"ro.product.brand": b"google",
                    b"ro.product.manufacturer": b"Google", b"ro.product.device": b"redfin",
                    b"ro.product.name": b"redfin", b"ro.build.product": b"redfin",
                    b"ro.build.fingerprint": b"google/redfin/redfin:13/TQ3A.230805.001/10316531:user/release-keys",
                    b"ro.build.characteristics": b"nosdcard", b"ro.build.version.sdk": b"33",
                    b"ro.build.version.release": b"13", b"ro.zygote": b"zygote64_32", b"ro.crypto.state": b"encrypted",
                    b"init.svc.adbd": b"stopped", b"sys.usb.config": b"mtp", b"persist.sys.usb.config": b"mtp",
                    b"service.adb.root": b"0", b"ro.allow.mock.location": b"0", b"selinux.status": b"1"}
_NSO_PROBE_MOUNTS = (b"/dev/block/dm-6 / ext4 ro,seclabel,relatime 0 0\n"
                     b"tmpfs /dev tmpfs rw,seclabel,nosuid,relatime,mode=755 0 0\n"
                     b"proc /proc proc rw,relatime,gid=3009,hidepid=invisible 0 0\n"
                     b"sysfs /sys sysfs rw,seclabel,relatime 0 0\n"
                     b"/dev/block/dm-7 /system_ext ext4 ro,seclabel,relatime 0 0\n"
                     b"/dev/block/dm-8 /product ext4 ro,seclabel,relatime 0 0\n"
                     b"/dev/block/dm-9 /vendor ext4 ro,seclabel,relatime 0 0\n"
                     b"tmpfs /apex tmpfs rw,seclabel,nosuid,nodev,noexec,relatime,mode=755 0 0\n"
                     b"/dev/block/dm-40 /data f2fs rw,lazytime,seclabel,nosuid,nodev,noatime 0 0\n")
_NSO_PROBE_MOUNTINFO = b"".join(b"%d 1 253:%d / %s %s - %s %s %s\n" % (20 + i, i, f[1], f[3].split(b",")[0], f[2], f[0],
                                                                         f[3])
                                for i, f in enumerate(ln.split() for ln in _NSO_PROBE_MOUNTS.splitlines()))
# Raw syscalls issued inline (`syscall` / `svc #0`) to dodge Frida's libc hooks: number -> the libc probe answering it
# from the same clean-device model (failures become -errno: ENOENT for absent paths, EBADF for unknown fds, ENOSYS).
_NSO_SYSCALLS = {"EM_X86_64": {0: "read", 3: "close", 17: "pread64", 39: "getpid", 62: "kill", 60: "exit", 89: "readlink",
                               101: "ptrace", 102: "getuid", 104: "getgid", 107: "geteuid", 110: "getppid", 157: "prctl",
                               186: "gettid", 200: "tgkill", 228: "clock_gettime", 231: "exit", 234: "tgkill",
                               257: "openat", 262: "newfstatat", 267: "readlinkat", 269: "faccessat", 2: "open",
                               4: "stat", 6: "lstat", 21: "access", 439: "faccessat2"},
                 "EM_AARCH64": {63: "read", 57: "close", 67: "pread64", 172: "getpid", 129: "kill", 93: "exit",
                                117: "ptrace", 174: "getuid", 176: "getgid", 175: "geteuid", 173: "getppid",
                                167: "prctl", 178: "gettid", 130: "tgkill", 113: "clock_gettime", 94: "exit",
                                131: "tgkill", 56: "openat", 79: "newfstatat", 78: "readlinkat", 48: "faccessat",
                                439: "faccessat2"}}


def _nso_has_svc(elf):
    """True when a .text section holds an inline `syscall` (x86_64) / 4-aligned `svc #0` (arm64)."""
    pat = {"EM_X86_64": b"\x0f\x05", "EM_AARCH64": b"\x01\x00\x00\xd4"}.get(elf.arch)
    for name, addr, data in elf.sections() if pat else ():
        if not name.startswith(".text"):
            continue
        j = data.find(pat)
        while j >= 0:
            if elf.arch == "EM_X86_64" or (addr + j) % 4 == 0:
                return True
            j = data.find(pat, j + 1)
    return False


_NSO_PROBE_SAVE = {"EM_X86_64": ("RBX", "RBP", "R12", "R13", "R14", "R15", "RSP"),
                   "EM_386": ("EBX", "ESI", "EDI", "EBP", "ESP"),
                   "EM_AARCH64": tuple(f"X{i}" for i in range(19, 29)) + ("FP", "LR", "SP"),
                   "EM_ARM": ("R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "SP", "LR")}


def _nso_probe_file(path):
    """Contents a clean device shows for a probed path; None = absent (su, frida, emulator, any non-/proc path)."""
    if path == b"/proc/mounts":
        return _NSO_PROBE_MOUNTS
    m = _NSO_PROBE_PROC.match(path)
    if not m:
        return None
    leaf = m.group(1)
    return (_NSO_PROBE_STATUS if leaf == b"status" else _NSO_PROBE_MAPS if leaf in (b"maps", b"smaps") else
            _NSO_PROBE_MOUNTS if leaf == b"mounts" else _NSO_PROBE_MOUNTINFO if leaf == b"mountinfo" else
            b"com.huntress.arena\0" if leaf == b"cmdline" else
            b"4242 (huntress.arena) S 600 600 0 0 -1 4194624 0 0 0 0 0 0 0 0 20 0 17 0\n" if leaf == b"stat" else b"")


def _nso_probe_popen(cmd):
    """What a popen'd probe command prints on a clean device: getprop [name], mount / cat <mounts>, id; else nothing
    (`which su`, `ls /data/adb`, `pm list packages | grep magisk`, ...)."""
    w = cmd.split(b"|")[0].split()
    if not w:
        return b""
    if w[0].endswith(b"getprop"):
        if len(w) > 1:
            return _NSO_PROBE_PROPS.get(w[1], b"") + b"\n"
        return b"".join(b"[%s]: [%s]\n" % kv for kv in sorted(_NSO_PROBE_PROPS.items()))
    if w[0].endswith(b"mount"):
        return _NSO_PROBE_MOUNTS
    if w[0].endswith(b"cat") and len(w) > 1:
        return _nso_probe_file(w[1]) or b""
    if w[0].endswith(b"id"):
        return b"uid=10123(u0_a123) gid=10123(u0_a123) groups=10123(u0_a123),3003(inet) context=u:r:untrusted_app:s0\n"
    return b""


def _nso_strtol(b, base=10):
    """(value, chars consumed) of a C strtol over bytes `b` (base 0 = auto)."""
    i = len(b) - len(b.lstrip(b" \t\n\r\f\v"))
    neg = b[i:i + 1] == b"-"
    i += b[i:i + 1] in (b"-", b"+")
    if base in (0, 16) and b[i:i + 2].lower() == b"0x":
        base, i = 16, i + 2
    elif base == 0:
        base = 8 if b[i:i + 1] == b"0" else 10
    j, v = i, 0
    while j < len(b) and j - i < 40:
        d = b[j] - 48 if 48 <= b[j] <= 57 else (b[j] | 32) - 87 if 97 <= (b[j] | 32) <= 122 else 99
        if d >= base:
            break
        v, j = v * base + d, j + 1
    return (-v if neg else v), (j if j > i else 0)

class _NsoElf:
    """Struct-level ELF view: header + PT_LOAD via pyelftools, section headers / symbols / RELA / RELR unpacked with
    struct (pyelftools' per-symbol parsing costs ~1 s on a libc-sized .so)."""

    def __init__(self, b):
        from elftools.elf.elffile import ELFFile
        elf = ELFFile(io.BytesIO(b))
        h, self.b, self.arch = elf.header, b, elf["e_machine"]
        self.e, self.is64 = "<" if elf.little_endian else ">", elf.elfclass == 64
        self.segs = [(s["p_vaddr"], s["p_offset"], s["p_filesz"], s["p_memsz"]) for s in elf.iter_segments()
                     if s["p_type"] == "PT_LOAD"]
        self.dyn = next(((s["p_vaddr"], s["p_filesz"]) for s in elf.iter_segments() if s["p_type"] == "PT_DYNAMIC"),
                        None)
        shf = self.e + ("IIQQQQIIQQ" if self.is64 else "IIIIIIIIII")
        self.secs = []  # [name, type, addr, offset, size, link]
        for i in range(min(h["e_shnum"], 512)):
            name, typ, _, addr, off, size, link = struct.unpack_from(shf, b, h["e_shoff"] + i * h["e_shentsize"])[:7]
            self.secs.append([name, typ, addr, off, size, link])
        if h["e_shstrndx"] < len(self.secs):
            stro = self.secs[h["e_shstrndx"]][3]
            for sec in self.secs:
                sec[0] = self.cstr(stro + sec[0]).decode("latin-1")
        self.syms = {}  # symtab section index -> [(name, value, size, type, shndx)]
        for i, (_, typ, _, off, size, link) in enumerate(self.secs):
            if typ not in (2, 11) or link >= len(self.secs):  # SHT_SYMTAB, SHT_DYNSYM
                continue
            stro, out = self.secs[link][3], []
            for t in struct.iter_unpack(self.e + ("IBBHQQ" if self.is64 else "IIIBBH"),
                                        b[off:off + min(size, 60000 * (24 if self.is64 else 16))]):
                nm, val, sz, info, shndx = (t[0], t[4], t[5], t[1], t[3]) if self.is64 else (t[0], t[1], t[2], t[3], t[5])
                out.append((self.cstr(stro + nm).decode("latin-1") if nm else "", val, sz, info & 0xF, shndx))
            self.syms[i] = out

    def cstr(self, off, n=256):
        return self.b[off:off + n].split(b"\0")[0]

    def at(self, va, n):
        """File bytes at virtual address `va`, capped to its segment; b"" when not file-backed."""
        for v, o, fs, _ in self.segs:
            if v <= va < v + fs:
                return self.b[o + va - v:o + min(va - v + n, fs)]
        return b""

    def sections(self, data_only=False):
        for name, typ, addr, off, size, _ in self.secs:
            if typ != 8 and (not data_only or _NSO_DATA.match(name)):  # SHT_NOBITS has no bytes
                yield name, addr, self.b[off:off + size]


def _nso_exports(elf):
    """Defined FUNC symbols (dynsym, then symtab when not stripped): JNI_OnLoad, Java_*, huntress_*, then the rest."""
    seen = {}
    for i in sorted(elf.syms, key=lambda i: elf.secs[i][1] != 11):
        for name, val, size, typ, shndx in elf.syms[i]:
            if typ == 2 and shndx and name and val:  # STT_FUNC, defined
                seen.setdefault(name, (val, size, elf.secs[i][1] == 11))
    rank = lambda n: (0 if n == "JNI_OnLoad" else 1 if n.startswith("Java_") else 2 if "huntress" in n.lower()
                      else 3 if seen[n][2] else 4)
    return [(n, *seen[n][:2]) for n in sorted(seen, key=lambda n: (rank(n), seen[n][0]))
            if not n.startswith(("_init", "_fini", "__", "frame_dummy", "register_tm", "deregister_tm"))]


def _nso_xor_keys(elf, arch, funcs, deadline):
    """Byte constants feeding the exports' xor/eor (x86 `xor r, imm`; ARM `eor r, r, #imm` or `mov r, #imm` < 256),
    plus multi-byte xor immediates as repeating keys."""
    import capstone
    keys = []
    a, m = _NSO_ARCH[arch][1]
    for name, va, size in funcs[:_NSO_MAX_FUNCS]:
        if time.time() > deadline:
            break
        thumb = arch == "EM_ARM" and va & 1  # the Thumb bit is ARM-only; an x86 function may start at an odd address
        md = capstone.Cs(getattr(capstone, a), getattr(capstone, m) | (capstone.CS_MODE_THUMB if thumb else 0))
        va -= 1 if thumb else 0
        for ins in md.disasm(elf.at(va, min(size or 512, _NSO_FUNC_CAP)), va):
            mn, ops = ins.mnemonic, ins.op_str
            mi = re.search(r"#?(-?0x[0-9a-f]+|-?\d+)\s*$", ops)
            if not mi or not (mn.startswith(("xor", "eor")) or (arch in ("EM_ARM", "EM_AARCH64") and mn.startswith("mov"))):
                continue
            v = int(mi.group(1), 0)
            if mn.startswith("mov") and not 0 < v < 256:
                continue
            v &= 0xFFFFFFFF
            k = bytes([v]) if v < 256 else v.to_bytes(4, "little").rstrip(b"\0")
            if k and k != b"\0" and k not in keys:
                keys.append(k)
    return keys[:32]


def _nso_static(elf, keys, deadline):
    """xor each data section (whole, for a single-byte key) and each data blob (symbol object / NUL-delimited run,
    any key; plus decode_any over the object blobs) with the export's key constants."""
    hits, blobs = [], []
    for _, _, d in elf.sections(data_only=True):
        for k in keys:
            if len(k) == 1:
                hits += ANS_RE_B.findall(d.translate(bytes(x ^ k[0] for x in range(256))))
        blobs += [m.group(0) for m in re.finditer(rb"[^\0]{8,512}", d)][:400]
    for syms in elf.syms.values():
        for _, val, size, typ, shndx in syms:
            if typ == 1 and shndx and 8 <= size <= 512 and val:  # STT_OBJECT
                b = elf.at(val, size)
                if b and b not in blobs:
                    blobs.insert(0, b)
    multi = [k for k in keys if len(k) > 1]
    for b in blobs[:2000] if multi else ():
        for k in multi:
            hits += ANS_RE_B.findall(bytes(x ^ k[j % len(k)] for j, x in enumerate(b)))
    end = min(deadline, time.time() + _NSO_DECODE_S)  # decode_any (b64/hex/rot/add/sub/...) on the first blobs only
    for b in blobs[:16]:
        for k in keys[:8]:
            if not hits and time.time() < end:
                r = decode_any(b, key=k[0] if len(k) == 1 else k.decode("latin-1"), depth=2, cap=200, chain=False)
                hits += [h.encode() for h in ANS_RE_T.findall(r or "")]
    return [h.decode() for h in hits]


_NSO_REG_WORDS = 1 << 18
_NSO_REG_NAME = re.compile(rb"[A-Za-z_$][\w$]{0,127}")
_NSO_REG_SIG = re.compile(rb"\((?:\[*(?:[ZBCSIJFD]|L[^;()]+;))*\)\[*(?:[ZBCSIJFDV]|L[^;()]+;)")


def _nso_registered(elf, dex=b""):
    """RegisterNatives tables without running JNI_OnLoad (row 39): every pointer-aligned {char* name, char* sig,
    void* fn} triple in .data.rel.ro / .data (pointers from R_*_RELATIVE RELA / RELR relocations, else the in-place
    word) whose name is a Java identifier, sig a JNI method descriptor and fn inside .text. Names that are also dex
    strings (the `native` method's name) rank first. [(name, fn va)]; [] when none (x86_64 / arm64 LE only)."""
    if not elf.is64 or elf.e != "<" or elf.arch not in ("EM_X86_64", "EM_AARCH64"):
        return []
    rel_t = 8 if elf.arch == "EM_X86_64" else 1027
    ptr = {}
    for _, typ, _, off, ssz, _ in elf.secs:
        if typ == 4:  # SHT_RELA: R_*_RELATIVE -> addend
            for r_off, info, add in struct.iter_unpack("<QQq", elf.b[off:off + min(ssz, 24 * _NSO_REG_WORDS) // 24 * 24]):
                if info & 0xFFFFFFFF == rel_t:
                    ptr[r_off] = add
        elif typ == 19:  # SHT_RELR: the in-place word is the target
            where = 0
            for (e,) in struct.iter_unpack("<Q", elf.b[off:off + (min(ssz, 8 * _NSO_REG_WORDS) & ~7)]):
                for o in ([e] if not e & 1 else [where + 8 * j for j in range(63) if e >> (j + 1) & 1]):
                    ptr.setdefault(o, int.from_bytes(elf.at(o, 8).ljust(8, b"\0"), "little"))
                where = e + 8 if not e & 1 else where + 63 * 8
    text = [(addr, addr + len(d)) for name, addr, d in elf.sections() if name == ".text"]
    out, words = [], 0
    for name, addr, d in elf.sections():
        if name not in (".data.rel.ro", ".data", ".data.rel.ro.local", ".data.rel"):
            continue
        for i in range((-addr) % 8, len(d) - 23, 8):
            words += 1
            if words > _NSO_REG_WORDS:
                break
            va = addr + i
            p = [ptr.get(va + 8 * k) or int.from_bytes(d[i + 8 * k:i + 8 * k + 8], "little") for k in range(3)]
            if not all(p) or not any(lo <= p[2] < hi for lo, hi in text):
                continue
            nm, sig = elf.at(p[0], 130).split(b"\0")[0], elf.at(p[1], 512).split(b"\0")[0]
            if _NSO_REG_NAME.fullmatch(nm) and _NSO_REG_SIG.fullmatch(sig):
                out.append((nm.decode(), p[2]))
    rank = {n: bool(dex) and bytes([len(n)]) + n.encode() + b"\0" in dex for n, _ in out}
    return sorted(dict.fromkeys(out), key=lambda t: not rank[t[0]])


_NSO_REF_FUNCS, _NSO_REF_TARGETS, _NSO_REF_S = 24, 96, 0.35
_NSO_RIP = re.compile(r"\[rip ([+-]) (0x[0-9a-f]+|\d+)\]")
_NSO_IMM = re.compile(r"#?(0x[0-9a-f]+|\d+)$")


def _nso_refs(elf, arch, funcs, deadline, extra=()):
    """What a Java_* / huntress_* export can return (rows 37, 65 -- D16's gated nativeEvidence returned &arena_value
    only for len 65536, so emulating it with len 0 misses): disassemble each export (and the local functions it calls,
    one level) for its rip-relative lea/mov targets (x86_64) and adrp+add / adrp+ldr pairs (arm64), read the C string
    / sized object at each target in a data section, and match it raw, xor'd with the function's own immediates, and
    through decode_any. Tokens in export order; [] when none."""
    import capstone
    if arch not in ("EM_X86_64", "EM_AARCH64"):
        return []
    a, m = _NSO_ARCH[arch][1]
    md = capstone.Cs(getattr(capstone, a), getattr(capstone, m))
    text = [(addr, addr + len(d)) for name, addr, d in elf.sections() if name == ".text"]
    datas = [(addr, addr + len(d)) for name, addr, d in elf.sections(data_only=True)]
    objs = {val: size for syms in elf.syms.values() for _, val, size, typ, shndx in syms
            if typ == 1 and shndx and 0 < size <= 4096}
    sizes = {va: size for _, va, size in funcs}
    end = min(deadline, time.time() + _NSO_REF_S)
    queue = [va for n, va, _ in funcs if n.startswith("Java_") or "huntress" in n.lower()][:_NSO_REF_FUNCS]
    starts = sorted({va for _, va, _ in funcs} | {va for _, va in extra} | {hi for _, hi in text})
    extra_va = {va for _, va in extra}
    for _, va in extra:  # RegisterNatives targets (stripped, unsized): up to the next known start, past early rets
        if va not in sizes and any(lo <= va < hi for lo, hi in text):
            sizes[va] = min(next((s for s in starts if s > va), va + 0x400) - va, 0x400)
            queue.append(va)
    seen, hits = set(), []
    while queue and time.time() < end and len(seen) < _NSO_REF_FUNCS:
        va = queue.pop(0)
        if va in seen:
            continue
        seen.add(va)
        targets, keys, pages, callees, lens = [], [], {}, [], []
        for ins in md.disasm(elf.at(va, min(sizes.get(va) or 1024, _NSO_FUNC_CAP)), va):
            mn, ops = ins.mnemonic, ins.op_str
            if arch == "EM_X86_64":
                r = _NSO_RIP.search(ops)
                if r:
                    targets.append(ins.address + ins.size + int(r.group(2), 0) * (1 if r.group(1) == "+" else -1))
            elif mn == "adrp":
                reg, _, page = ops.partition(", ")
                pages[reg] = int(page.lstrip("#"), 0)
            elif mn in ("add", "ldr", "ldrb", "ldrsb") and ops.count(",") >= 1:
                p = [x.strip(" []!") for x in ops.split(",")]
                base = p[1] if len(p) > 1 else ""
                if base in pages:
                    off = int(p[2].lstrip("#"), 0) if len(p) > 2 and p[2].lstrip("#")[:1].isdigit() else 0
                    targets.append(pages[base] + off)
            if mn.startswith(("call", "bl", "jmp", "b")) and not mn.startswith(("blr", "br")):
                t = _NSO_IMM.search(ops)
                if t and any(lo <= int(t.group(1), 0) < hi for lo, hi in text):
                    callees.append(int(t.group(1), 0))
            mi = _NSO_IMM.search(ops)
            if mi and mn.startswith(("xor", "eor", "mov", "cmp", "sub", "add")):
                v = int(mi.group(1), 0) & 0xFFFFFFFF
                if mn.startswith("cmp") and 8 <= v <= 512 and va in extra_va:
                    lens.append(v)  # loop bound: the length of an unsized (stripped) blob whose xor holds a NUL
                k = bytes([v]) if 0 < v < 256 else v.to_bytes(4, "little").rstrip(b"\0") if mn.startswith(("xor", "eor")) else b""
                if k and k not in keys:
                    keys.append(k)
            if mn in ("ret", "retq") and not sizes.get(va):
                break
        queue += [c for c in callees if c not in seen]
        for t in list(dict.fromkeys(targets))[:_NSO_REF_TARGETS]:
            if not any(lo <= t < hi for lo, hi in datas) or time.time() > end:
                continue
            raw = elf.at(t, objs.get(t, 512))
            blobs = [raw[:objs[t]]] if t in objs else []
            blobs += [b for b in (raw.split(b"\0")[0],) if len(b) >= 8 and b not in blobs]
            blobs += [raw[:n] for n in dict.fromkeys(lens) if t not in objs and len(raw) >= n and raw[:n] not in blobs]
            for b in blobs:
                found = ANS_RE_B.findall(b)
                for k in keys[:16]:
                    found = found or ANS_RE_B.findall(bytes(x ^ k[j % len(k)] for j, x in enumerate(b)))
                for k in [None] + keys[:6]:
                    if found or time.time() > end:
                        break
                    r = decode_any(b, key=None if k is None else k[0] if len(k) == 1 else k.decode("latin-1"),
                                   depth=2, cap=300, chain=False)
                    found = [h.encode() for h in ANS_RE_T.findall(r or "")]
                hits += [h.decode() for h in found]
    return hits


_NSO_STK_FUNCS, _NSO_STK_S = 64, 0.3
_NSO_STK_X86 = re.compile(r"(byte|word|dword|qword) ptr \[(rbp|rsp|ebp|esp)(?: ([+-]) (0x[0-9a-f]+|\d+))?\], (\w+)$")
_NSO_STK_A64 = re.compile(r"([wx]\w+), (?:([wx]\w+), )?\[(sp|x29)(?:, #(-?0x[0-9a-f]+|-?\d+))?\]$")
_NSO_STK_W = {"byte": 1, "word": 2, "dword": 4, "qword": 8}
_NSO_STK_HEAD = b"ANS-"


def _nso_stack_runs(md, arch, code, va):
    """Immediate stores into one stack frame, ordered by offset: x86_64 `mov byte/word/dword/qword [rbp/rsp +- off],
    imm` and `movabs/mov reg, imm; mov [..], reg`; arm64 `mov/movz/movk/movn w|x, #imm` then `strb/strh/str/stur/stp
    reg, [sp|x29, #off]` (wzr/xzr = 0). Later stores to an offset win. Yields each contiguous byte run (>= 8)."""
    regs, mem = {}, {}

    def put(base, off, val, n):
        for j in range(n):
            mem[(base, off + j)] = (val >> (8 * j)) & 0xFF

    for ins in md.disasm(code, va):
        mn, ops = ins.mnemonic, ins.op_str
        if arch == "EM_X86_64":
            if mn in ("mov", "movabs"):
                r = _NSO_STK_X86.match(ops)
                if r:
                    src, n = r.group(5), _NSO_STK_W[r.group(1)]
                    v = int(src, 0) if src[:1].isdigit() else regs.get(src[-2:])
                    if v is not None:
                        off = int(r.group(4) or "0", 0) * (-1 if r.group(3) == "-" else 1)
                        put(r.group(2)[-2:], off, v, n)
                    continue
                d, _, s = ops.partition(", ")
                if s[:1].isdigit() and "[" not in d:
                    regs[d[-2:]] = int(s, 0)  # rax/eax/ax share the low bytes
                    continue
            if mn.startswith(("call", "j", "ret")):
                regs.clear()
            elif ops and "[" not in ops.split(",")[0]:
                regs.pop(ops.split(",")[0][-2:], None)
        else:
            p = [x.strip() for x in ops.split(",")]
            reg = lambda x: "x" + x[1:] if x[:1] in "wx" else x
            if mn in ("mov", "movz", "movk", "movn") and len(p) >= 2 and p[1].startswith("#"):
                try:
                    v = int(p[1][1:], 0)
                except ValueError:
                    continue
                sh = int(p[2].split("#")[-1], 0) if len(p) > 2 and "lsl" in p[2] else 0
                if mn == "movk":
                    old = regs.get(reg(p[0]), 0)
                    regs[reg(p[0])] = (old & ~(0xFFFF << sh)) | (v << sh)
                else:
                    v <<= sh
                    regs[reg(p[0])] = ~v if mn == "movn" else v
                continue
            r = _NSO_STK_A64.match(ops) if mn in ("str", "stur", "strb", "sturb", "strh", "sturh", "stp", "stnp") else None
            if r:
                n = 1 if mn.endswith("b") else 2 if mn.endswith("h") else 8 if r.group(1)[0] == "x" else 4
                off = int(r.group(4) or "0", 0)
                for j, src in enumerate((r.group(1), r.group(2)) if mn.startswith(("stp", "stnp")) else (r.group(1),)):
                    v = 0 if src and src[1:] == "zr" else regs.get(reg(src or ""))
                    if v is not None:
                        put(r.group(3), off + j * n, v, n)
                continue
            if mn.startswith(("bl", "ret", "b.", "cb", "tb")) or mn == "b":
                regs.clear()
            elif p and p[0][:1] in "wx":
                regs.pop(reg(p[0]), None)
    for base in {b for b, _ in mem}:
        offs = sorted(o for b, o in mem if b == base)
        run, prev = bytearray(), None
        for o in offs + [None]:
            if o is None or (prev is not None and o != prev + 1):
                if len(run) >= 8:
                    yield bytes(run)
                run = bytearray()
            if o is not None:
                run.append(mem[(base, o)])
                prev = o


def _nso_stack_decode(b, keys):
    """ANS tokens in a stack byte run: raw; known-plaintext anchored ("ANS-" at each start) xor / add / sub with an
    affine per-index key k + m*i, and a 4-byte repeating xor key; then decode_any with the function's imm8 keys."""
    hits = [h.decode() for h in ANS_RE_B.findall(b)]
    for s in (b, b[::-1]):
        for i in range(len(s) - 19):
            c = s[i:i + 20]
            for op, inv in ((lambda x, k: x ^ k, lambda x, p: x ^ p), (lambda x, k: x - k, lambda x, p: x - p),
                            (lambda x, k: x + k, lambda x, p: p - x)):
                k0, k1 = inv(c[0], 0x41) & 0xFF, inv(c[1], 0x4E) & 0xFF
                m = (k1 - k0) & 0xFF
                t = bytes(op(x, (k0 + m * j) & 0xFF) & 0xFF for j, x in enumerate(c))
                if t[:4] == _NSO_STK_HEAD and ANS_RE_B.fullmatch(t):
                    hits.append(t.decode())
            k = bytes(x ^ y for x, y in zip(c[:4], _NSO_STK_HEAD))
            t = bytes(x ^ k[j % 4] for j, x in enumerate(c))
            if ANS_RE_B.fullmatch(t):
                hits.append(t.decode())
    if not hits and len(b) >= 16:
        for k in [None] + keys[:4]:
            r = decode_any(b, key=k, depth=2, cap=150, chain=False)
            hits += ANS_RE_T.findall(r or "")
            if hits:
                break
    return hits


def _nso_stack(elf, arch, funcs, deadline):
    """Row 40 stack strings: the answer (encoded) is assembled on the stack by immediate stores in an export (or a
    local function it calls) and never sits in a data section -- strings / the section sweeps miss it, and a checker
    that compares enc(input) to it never materialises the plaintext for emulation. Each run of stores, ordered by
    stack offset, goes through _nso_stack_decode. x86_64 / arm64; tokens in function order; [] when none."""
    import capstone
    if arch not in ("EM_X86_64", "EM_AARCH64"):
        return []
    a, m = _NSO_ARCH[arch][1]
    md = capstone.Cs(getattr(capstone, a), getattr(capstone, m))
    text = [(addr, addr + len(d)) for name, addr, d in elf.sections() if name == ".text"]
    starts = sorted({va for _, va, _ in funcs} | {hi for _, hi in text})
    sizes = {va: size for _, va, size in funcs}
    queue = [va for _, va, _ in funcs[:_NSO_MAX_FUNCS]]
    end, seen, hits = min(deadline, time.time() + _NSO_STK_S), set(), []
    while queue and time.time() < end and len(seen) < _NSO_STK_FUNCS:
        va = queue.pop(0)
        if va in seen:
            continue
        seen.add(va)
        size = sizes.get(va) or min(next((s for s in starts if s > va), va + 0x800) - va, 0x800)
        code = elf.at(va, min(size, _NSO_FUNC_CAP))
        keys = []
        for ins in md.disasm(code, va):
            mn, ops = ins.mnemonic, ins.op_str
            t = _NSO_IMM.search(ops)
            if t and mn.startswith(("call", "bl", "jmp", "b")) and not mn.startswith(("blr", "br")):
                c = int(t.group(1), 0)
                if any(lo <= c < hi for lo, hi in text) and c not in seen:
                    queue.append(c)
            elif t and mn.startswith(("xor", "eor", "add", "sub")) and 0 < int(t.group(1), 0) < 256:
                k = int(t.group(1), 0)
                keys += [k] if k not in keys else []
        for run in _nso_stack_runs(md, arch, code, va):
            if time.time() > end:
                break
            hits += _nso_stack_decode(run, keys)
    return hits


_NSO_MAX_CTORS = 64


def _nso_ctors(elf, word, W):
    """Load-time constructors in the dynamic loader's order: DT_INIT, then the DT_INIT_ARRAY / SHT_INIT_ARRAY words
    (`word(va)` reads them after relocation), then any `datadiv_decode<N>` symbol (OLLVM string decryption) not
    already listed. Image-relative addresses; [] when the .so has none."""
    out, arrs = [], []
    if elf.dyn:
        dyn, tags = elf.at(elf.dyn[0], min(elf.dyn[1], 0x4000)), {}
        for i in range(0, len(dyn) - 2 * W + 1, 2 * W):
            t, v = int.from_bytes(dyn[i:i + W], "little"), int.from_bytes(dyn[i + W:i + 2 * W], "little")
            if t == 0:
                break
            tags.setdefault(t, v)
        if tags.get(12):  # DT_INIT
            out.append(tags[12])
        if 25 in tags:  # DT_INIT_ARRAY / DT_INIT_ARRAYSZ
            arrs.append((tags[25], tags.get(27, 0)))
    arrs += [(addr, sz) for _, typ, addr, _, sz, _ in elf.secs if typ == 14 and addr]  # SHT_INIT_ARRAY
    for addr, sz in arrs:
        for j in range(min(sz // W, _NSO_MAX_CTORS)):
            v = int.from_bytes(word(addr + j * W)[:W].ljust(W, b"\0"), "little")
            if v not in (0, (1 << 8 * W) - 1):
                out.append(v)
    for syms in elf.syms.values():
        out += [val for name, val, _, typ, shndx in syms if typ == 2 and shndx and val and "datadiv_decode" in name]
    return list(dict.fromkeys(out))


def _nso_emulate(elf, arch, funcs, deadline, gate=None, probes=False):
    """Run the exports in unicorn: JNI_OnLoad (fake JavaVM; RegisterNatives' fn pointers are queued), Java_* and the
    registered natives with a fake JNIEnv (NewStringUTF strings are captured), every other export with no args (its
    char* return is read). Imports: malloc/calloc/new bump-allocate, mem/str copies are done, the rest return 0.
    The memory touched (image, heap, stack) and every string handed to a stub is scanned for the token.
    probes=True (row 66: anti-debug inside the export): libc answers as on a clean, untraced device (_NSO_PROBE_*:
    fake /proc/self/status|maps FILEs / fds read by fgets / read / getline / fread, str/mem compares and strtol done,
    pthread_create runs the routine inline), SetByteArrayRegion buffers are captured, and a run that reaches kill /
    raise / exit / abort is a trap path whose strings are dropped."""
    import unicorn as U
    spec = _NSO_ARCH[arch]
    if spec[0] is None:
        return []
    ua, um = spec[0]
    rc, pfx = {"EM_X86_64": (U.x86_const, "UC_X86_REG_"), "EM_386": (U.x86_const, "UC_X86_REG_"),
               "EM_AARCH64": (U.arm64_const, "UC_ARM64_REG_"), "EM_ARM": (U.arm_const, "UC_ARM_REG_")}[arch]
    argr = [getattr(rc, pfx + r) for r in spec[2]]
    retr = getattr(rc, pfx + spec[3])
    BASE, STUB, JNI, HEAP, STACK, TLS = 0x10000000, 0x60000000, 0x61000000, 0x62000000, 0x63000000, 0x64000000
    RET = STUB + 0xF000
    if elf.e != "<" or elf.is64 != (arch in ("EM_X86_64", "EM_AARCH64")):
        return []
    W = 8 if elf.is64 else 4  # pointer width: JNI tables, relocated words, JNINativeMethod entries (3 * W)
    MASK = (1 << 8 * W) - 1
    top = max(v + ms for v, _, _, ms in elf.segs)
    size = (top + 0xFFFF) & ~0xFFFF
    if size > 64 << 20:
        return []
    uc = U.Uc(getattr(U, ua), getattr(U, um))
    uc.mem_map(BASE, size)
    for v, o, fs, _ in elf.segs:
        uc.mem_write(BASE + v, elf.b[o:o + fs])
    for a, n in ((STUB, 0x10000), (JNI, 0x10000), (HEAP, 1 << 20), (STACK, 1 << 20), (TLS, 0x10000)):
        uc.mem_map(a, n)
    uc.mem_write(STUB, spec[4] * (0x10000 // len(spec[4])))
    uc.mem_write(JNI, (JNI + 0x100).to_bytes(W, "little"))
    uc.mem_write(JNI + 0x100, b"".join((STUB + 16 * i).to_bytes(W, "little") for i in range(300)))
    VM = JNI + 0x2000
    uc.mem_write(VM, (VM + 0x100).to_bytes(W, "little"))
    uc.mem_write(VM + 0x100, b"".join((STUB + 16 * (300 + i)).to_bytes(W, "little") for i in range(16)))
    uc.mem_write(TLS, (TLS + 0x8000).to_bytes(W, "little"))
    if arch == "EM_X86_64":
        uc.reg_write(rc.UC_X86_REG_FS_BASE, TLS)
    elif arch == "EM_AARCH64":
        uc.reg_write(rc.UC_ARM64_REG_TPIDR_EL0, TLS)
    elif arch == "EM_386":  # bionic's canary is %gs:0x14 with gs = 0 here: a zero page answers it
        uc.mem_map(0, 0x10000)
    else:
        try:  # VFP / NEON on (vectorised Thumb-2 loops), else the first vld1 faults
            uc.reg_write(rc.UC_ARM_REG_C1_C0_2, uc.reg_read(rc.UC_ARM_REG_C1_C0_2) | 0xF00000)
            uc.reg_write(rc.UC_ARM_REG_FPEXC, 0x40000000)
        except Exception:  # noqa: BLE001
            pass
    imports = {}  # import name -> stub slot

    def put(o, v):
        if BASE <= o <= BASE + size - W:
            uc.mem_write(o, (v & MASK).to_bytes(W, "little"))

    for _, typ, _, off, ssz, link in elf.secs:
        if typ == 19:  # SHT_RELR: even word = address, odd word = bitmap of the next 63 words
            where = 0
            for (e,) in struct.iter_unpack("<" + "IQ"[W // 8], elf.b[off:off + (min(ssz, W << 17) & -W)]):
                for o in ([e] if not e & 1 else [where + W * j for j in range(8 * W - 1) if e >> (j + 1) & 1]):
                    if o <= size - W:
                        put(BASE + o, BASE + int.from_bytes(uc.mem_read(BASE + o, W), "little"))
                where = e + W if not e & 1 else where + (8 * W - 1) * W
        if typ not in (4, 9):  # SHT_RELA, SHT_REL (32-bit ABIs: the addend is the word in place)
            continue
        syms = elf.syms.get(link, [])
        fmt = "<" + ("QQq" if W == 8 else "IIi" if typ == 4 else "II")
        n = struct.calcsize(fmt)
        for r in struct.iter_unpack(fmt, elf.b[off:off + min(ssz, n * 200_000) // n * n]):
            r_off, info = r[:2]
            inplace = int.from_bytes(elf.at(r_off, W).ljust(W, b"\0"), "little") if len(r) == 2 else 0
            add = r[2] if len(r) == 3 else inplace
            kind, si = (spec[5].get(info & 0xFFFFFFFF), info >> 32) if W == 8 else (spec[5].get(info & 0xFF), info >> 8)
            if kind == "rel":
                put(BASE + r_off, BASE + add)
            elif kind in ("sym", "abs") and si < len(syms):
                name, val, _, _, shndx = syms[si]
                add = add if kind == "abs" or len(r) == 3 else 0  # REL GLOB_DAT / JUMP_SLOT ignore the word in place
                if shndx and val:
                    put(BASE + r_off, BASE + val + add)
                else:
                    if name not in imports and len(imports) < 3000:
                        imports[name] = len(imports)
                    put(BASE + r_off, STUB + 16 * (400 + imports[name]) if name in imports else RET)
    slot_name = {v: k for k, v in imports.items()}
    strs, natives, heap = [], [], [HEAP + 0x100]
    files, threads, pst = {}, [], {"fd": 64, "t": 0, "trap": False}  # probes: open handles, inline threads, state
    props = {}  # probes: __system_property_find handle -> name
    save = [getattr(rc, pfx + r) for r in _NSO_PROBE_SAVE[arch]]
    pcr = getattr(rc, pfx + {"EM_X86_64": "RIP", "EM_386": "EIP", "EM_AARCH64": "PC", "EM_ARM": "PC"}[arch])
    spr = save[-2 if arch == "EM_ARM" else -1]

    def rd(p, n=256):
        try:
            return bytes(uc.mem_read(p, n))
        except U.UcError:
            try:
                return bytes(uc.mem_read(p, 16))
            except U.UcError:
                return b""

    def cstr(p):
        return rd(p).split(b"\0")[0] if p > 0x1000 else b""

    def alloc(n):
        p, heap[0] = heap[0], (heap[0] + max(16, min(n, 1 << 18)) + 15) & ~15
        if heap[0] >= HEAP + (1 << 20):
            heap[0] = HEAP + 0x100
        return p

    def thread_end():  # back to pthread_create's caller as if it returned 0 (the routine returned / slept / exited)
        for r, v in zip(save, threads.pop()):
            uc.reg_write(r, v)
        return 0

    def probe(n, a):
        """Clean-device answer of libc import `n`; None = not a probe (the plain stubs handle it)."""
        if n in ("ptrace", "prctl", "signal", "sigaction", "pthread_join", "pthread_detach", "close", "fclose",
                 "closedir", "waitpid", "pclose"):
            if n in ("close", "fclose", "pclose"):
                files.pop(a[0], None)
            return 0
        if n in ("__system_property_get", "__system_property_find"):  # rows 66 / 95: stock-device properties
            name = cstr(a[0])
            if n == "__system_property_find":
                if name not in _NSO_PROBE_PROPS:
                    return 0
                h = alloc(16)
                props[h] = name
                return h
            v = _NSO_PROBE_PROPS.get(name, b"")[:91]
            if a[1]:
                uc.mem_write(a[1], v + b"\0")
            return len(v)
        if n in ("__system_property_read", "__system_property_read_callback"):
            name = props.get(a[0])
            if name is None:
                return 0
            v = _NSO_PROBE_PROPS[name][:91]
            if n == "__system_property_read":
                if a[1]:
                    uc.mem_write(a[1], name + b"\0")
                if a[2]:
                    uc.mem_write(a[2], v + b"\0")
                return len(v)
            if not a[1]:
                return 0
            pn, pv = alloc(len(name) + 1), alloc(len(v) + 1)
            uc.mem_write(pn, name + b"\0")
            uc.mem_write(pv, v + b"\0")
            # tail call callback(cookie, name, value, serial): it returns straight to read_callback's caller
            if argr:
                for r, x in zip(argr, (a[2], pn, pv, 1)):
                    uc.reg_write(r, x)
            else:
                uc.mem_write(uc.reg_read(rc.UC_X86_REG_ESP) + 4, struct.pack("<4I", a[2] & MASK, pn, pv, 1))
            uc.reg_write(pcr, a[1])
            return a[2]  # arg 0 doubles as the return register on ARM
        if n == "popen":  # rows 66 / 95: `which su` / getprop / mount read back through fgets / fread
            h = alloc(64)
            files[h] = [_nso_probe_popen(cstr(a[0])), 0]
            return h
        if n in ("fork", "vfork", "clone"):
            return 4243  # parent side: the watchdog child never runs
        if n in ("getpid", "gettid"):
            return 4242
        if n == "getppid":
            return 600  # zygote
        if n in ("getuid", "geteuid", "getgid"):
            return 10123
        if n in ("__errno", "__errno_location"):
            return TLS + 0x100
        if n in ("clock_gettime", "gettimeofday", "time"):
            pst["t"] += 1000
            sec, ns = 1000 + pst["t"] // 10 ** 9, pst["t"] % 10 ** 9
            dst = a[1] if n == "clock_gettime" else a[0]
            if n == "time":
                sec += 1_700_000_000
            if dst and n != "time":
                uc.mem_write(dst, ((sec & MASK).to_bytes(W, "little") +
                                   (ns if n == "clock_gettime" else ns // 1000).to_bytes(W, "little")))
            elif dst:
                uc.mem_write(dst, (sec & MASK).to_bytes(W, "little"))
            return sec if n == "time" else 0
        if n in ("kill", "raise", "tgkill", "abort", "exit", "_exit", "_Exit", "pthread_exit", "sleep", "usleep",
                 "nanosleep"):
            if threads:  # inside an inline thread: its run ends here
                return thread_end()
            if "sleep" in n:
                return 0
            pst["trap"] = True
            uc.emu_stop()
            return 0
        if n == "pthread_create":
            if len(threads) >= 4 or not a[2]:
                return 0
            threads.append([uc.reg_read(r) for r in save])
            if a[0]:
                uc.mem_write(a[0], (0x7000 + len(threads)).to_bytes(W, "little"))
            sp = uc.reg_read(spr) - 0x200 & ~15
            if arch == "EM_X86_64":
                sp -= 8
                uc.mem_write(sp, (STUB + 16 * 399).to_bytes(8, "little"))
            elif arch == "EM_386":
                sp -= 12
                uc.mem_write(sp, struct.pack("<II", STUB + 16 * 399, a[3] & MASK))
            else:
                uc.reg_write(save[-1 if arch == "EM_ARM" else -2], STUB + 16 * 399)
            uc.reg_write(spr, sp)
            if argr:
                uc.reg_write(argr[0], a[3])
            uc.reg_write(pcr, a[2])
            return a[3]  # the routine's first argument (arg 0 doubles as the return register on ARM)
        if n in ("fopen", "fopen64", "open", "open64", "__open_2", "__open", "openat", "__openat_2", "opendir"):
            data = _nso_probe_file(cstr(a[1] if "openat" in n else a[0])) if n != "opendir" else None
            if data is None:
                return -1 if "open" in n and n not in ("opendir", "fopen", "fopen64") else 0  # opendir: NULL
            if n.startswith("fopen"):
                h = alloc(64)
            else:
                h, pst["fd"] = pst["fd"], pst["fd"] + 1
            files[h] = [data, 0]
            return h
        if n in ("access", "faccessat", "stat", "lstat", "stat64", "lstat64", "__xstat", "__lxstat", "fstatat",
                 "newfstatat", "__xstat64", "__lxstat64"):
            path = cstr(a[1] if n in ("faccessat", "fstatat", "newfstatat", "__xstat", "__lxstat", "__xstat64",
                                      "__lxstat64") else a[0])
            return 0 if _NSO_PROBE_PROC.match(path) or path == b"/proc/mounts" else -1
        if n in ("read", "__read_chk", "pread", "pread64", "fread", "fread_unlocked", "fgets", "__fgets_chk",
                 "fgets_unlocked", "getline", "__getline", "getdelim", "fgetc", "getc", "feof"):
            h = next((x for x in ((a[0],) if n in ("read", "__read_chk", "pread", "pread64", "fgetc", "getc", "feof")
                                  else (a[3], a[2]) if n in ("fread", "fread_unlocked", "getdelim") else
                                  (a[2], a[3])) if x in files), None)
            if h is None:
                return None
            data, pos = files[h]
            rest = data[pos:]
            if n == "feof":
                return int(not rest)
            if n in ("fgetc", "getc"):
                files[h][1] += 1 if rest else 0
                return rest[0] if rest else -1
            if n.startswith(("read", "__read", "pread")):
                chunk = rest[:min(a[2], 1 << 16)]
            elif n.startswith("fread"):
                chunk = rest[:min(a[1] * a[2], 1 << 16)]
            else:
                lim = (min(a[1], 4096) - 1) if "fgets" in n else 4096
                nl = rest.find(b"\n" if n != "getdelim" else bytes([a[2] & 0xFF]))
                chunk = rest[:min(lim, nl + 1 if nl >= 0 else len(rest))]
                if not chunk:
                    return 0 if "fgets" in n else -1
            files[h][1] += len(chunk)
            if n.startswith(("getline", "__getline", "getdelim")):
                buf = alloc(len(chunk) + 16)
                uc.mem_write(buf, chunk + b"\0")
                uc.mem_write(a[0], buf.to_bytes(W, "little"))
                uc.mem_write(a[1], (len(chunk) + 16).to_bytes(W, "little"))
                return len(chunk)
            uc.mem_write(a[1] if n.startswith(("read", "__read", "pread")) else a[0],
                         chunk + (b"\0" if "fgets" in n else b""))
            return a[0] if "fgets" in n else len(chunk) // (a[1] or 1) if n.startswith("fread") else len(chunk)
        if n in ("strstr", "strcasestr", "memmem"):
            hay = rd(a[0], min(a[1], 1 << 16)) if n == "memmem" else rd(a[0], 1 << 16).split(b"\0")[0]
            nee = rd(a[2], min(a[3], 256)) if n == "memmem" else cstr(a[1])
            j = hay.lower().find(nee.lower()) if n == "strcasestr" else hay.find(nee)
            return a[0] + j if j >= 0 else 0
        if n in ("strcmp", "strncmp", "strcasecmp", "strncasecmp", "memcmp", "bcmp"):
            m = a[2] if "n" in n[3:] or n in ("memcmp", "bcmp") else 4096
            x, y = rd(a[0], min(m, 4096)), rd(a[1], min(m, 4096))
            if not n.endswith(("memcmp", "bcmp")):
                x, y = x.split(b"\0")[0] + b"\0", y.split(b"\0")[0] + b"\0"
                x, y = x[:m], y[:m]
            if "case" in n:
                x, y = x.lower(), y.lower()
            return 0 if x == y else -1 if x < y else 1
        if n in ("strchr", "strrchr"):
            b = rd(a[0], 4096).split(b"\0")[0] + b"\0"
            j = (b.find if n == "strchr" else b.rfind)(bytes([a[1] & 0xFF]))
            return a[0] + j if j >= 0 else 0
        if n in ("atoi", "atol", "atoll") or re.fullmatch(r"(__isoc23_)?strto(u?ll?|u?l|imax|umax)", n):
            v, used = _nso_strtol(rd(a[0], 64).split(b"\0")[0], a[2] if n.startswith(("strto", "__isoc23")) else 10)
            if n.startswith(("strto", "__isoc23")) and a[1]:
                uc.mem_write(a[1], (a[0] + used).to_bytes(W, "little"))
            return v
        return None

    def hook(uc, addr, size, _):
        if addr == RET:
            uc.emu_stop()
            return
        if argr:
            a = [uc.reg_read(r) for r in argr] + [0] * (6 - len(argr))
        else:  # i386 cdecl: [esp] = return address, then the args
            a = list(struct.unpack("<6I", rd(uc.reg_read(rc.UC_X86_REG_ESP) + 4, 24).ljust(24, b"\0")))
        for x in a[:4]:
            s = cstr(x)
            if len(s) >= 4:
                strs.append(s)
        i, ret = (addr - STUB) // 16, 0
        if probes and i == 399 and threads:  # an inline thread's routine returned
            ret = thread_end()
        elif probes and i == 208:  # SetByteArrayRegion(env, array, start, len, buf): the export's byte[] result
            strs.append(rd(a[4], min(a[3], 4096)))
        elif i < 300:
            if i == 6:
                ret = 1
            elif i == 167:
                ret = a[1]
            elif i == 169:
                ret = alloc(16)
            elif i == 215:
                for j in range(min(a[3], 64)):
                    e = rd(a[2] + 3 * W * j, 3 * W)
                    if len(e) == 3 * W:
                        natives.append(int.from_bytes(e[2 * W:], "little"))
        elif i < 316:
            if i - 300 in (4, 6, 7):
                uc.mem_write(a[1], JNI.to_bytes(W, "little"))
        elif i - 400 in slot_name:
            n = slot_name[i - 400]
            pr = probe(n, a) if probes else None
            if pr is not None:
                ret = pr
            elif n in _NSO_ALLOC:
                ret = alloc(a[0] * a[1] if n == "calloc" else len(cstr(a[0])) + 1 if n == "strdup" else a[1]
                            if n == "realloc" else a[0])
                if n in ("realloc", "strdup") and a[0]:
                    uc.mem_write(ret, rd(a[0], min(a[1], 1 << 16)) if n == "realloc" else cstr(a[0]))
            elif n == "strlen":
                ret = len(rd(a[0], 4096).split(b"\0")[0])
            elif n in ("memcpy", "memmove", "__memcpy_chk", "__memmove_chk"):
                uc.mem_write(a[0], rd(a[1], min(a[2], 1 << 16))[:a[2]])
                ret = a[0]
            elif n in ("memset", "__memset_chk"):
                uc.mem_write(a[0], bytes([a[1] & 0xFF]) * min(a[2], 1 << 16))
                ret = a[0]
            elif n in ("strcpy", "__strcpy_chk", "strcat", "__strcat_chk"):
                d = a[0] + (len(cstr(a[0])) if "cat" in n else 0)
                uc.mem_write(d, cstr(a[1]) + b"\0")
                ret = a[0]
            elif n in ("__stack_chk_fail", "abort", "exit", "_exit", "__cxa_throw"):
                uc.emu_stop()
        uc.reg_write(retr, ret & MASK)

    uc.hook_add(U.UC_HOOK_CODE, hook, begin=STUB, end=STUB + 0xFFFF)
    sysno = _NSO_SYSCALLS.get(arch) if probes else None
    if sysno:  # inline syscall / svc #0 probes (Frida libc-hook bypass) answer from the same clean-device model
        sregs = [getattr(rc, pfx + r) for r in (("RDI", "RSI", "RDX", "R10", "R8", "R9") if arch == "EM_X86_64" else
                                                 ("X0", "X1", "X2", "X3", "X4", "X5"))]
        nrr = getattr(rc, pfx + ("RAX" if arch == "EM_X86_64" else "X8"))

        def syscall(uc, *x):
            if arch == "EM_AARCH64" and x[0] != 2:  # not EXCP_SWI (brk / udf): this run ends
                uc.emu_stop()
                return
            n, a = sysno.get(uc.reg_read(nrr)), [uc.reg_read(r) for r in sregs]
            try:
                if n in ("readlinkat", "readlink"):  # nothing links anywhere but our own exe / std fds
                    path = cstr(a[1] if n == "readlinkat" else a[0])
                    t = (b"/system/bin/app_process64" if re.fullmatch(rb"/proc/(self|\d+)/exe", path) else
                         b"/dev/null" if re.fullmatch(rb"/proc/(self|\d+)/fd/[012]", path) else None)
                    buf, cap = a[2:4] if n == "readlinkat" else a[1:3]
                    if t is not None and buf:
                        uc.mem_write(buf, t[:cap])
                    r = -2 if t is None else min(len(t), cap)
                else:
                    r = probe(n, a) if n else None
                    if r is None:
                        r = -9 if n in ("read", "pread64") else -38  # EBADF / ENOSYS
                    elif r == -1 and n != "ptrace":
                        r = -2  # ENOENT: su / frida / emulator paths are absent
            except Exception:  # noqa: BLE001 - a bad pointer: EFAULT
                r = -14
            uc.reg_write(retr, r & MASK)

        if arch == "EM_X86_64":
            uc.hook_add(U.UC_HOOK_INSN, syscall, None, 1, 0, U.x86_const.UC_X86_INS_SYSCALL)
        else:
            uc.hook_add(U.UC_HOOK_INTR, syscall)

    def call(va, args):
        if time.time() > deadline:
            return
        mark, pst["trap"] = len(strs), False
        threads.clear()
        sp = STACK + (1 << 20) - 0x1000
        for r, v in zip(argr, list(args) + [0] * 6):
            uc.reg_write(r, v)
        if arch == "EM_X86_64":
            sp -= 8
            uc.mem_write(sp, RET.to_bytes(8, "little"))
            uc.reg_write(rc.UC_X86_REG_RSP, sp)
        elif arch == "EM_386":
            sp -= 28
            uc.mem_write(sp, struct.pack("<7I", RET, *[v & MASK for v in (list(args) + [0] * 6)[:6]]))
            uc.reg_write(rc.UC_X86_REG_ESP, sp)
        elif arch == "EM_ARM":  # a Thumb target keeps its odd address: unicorn starts it in Thumb state
            uc.reg_write(rc.UC_ARM_REG_SP, sp)
            uc.reg_write(rc.UC_ARM_REG_LR, RET)
        else:
            uc.reg_write(rc.UC_ARM64_REG_SP, sp)
            uc.reg_write(rc.UC_ARM64_REG_LR, RET)
        try:
            uc.emu_start(va, RET, timeout=_NSO_FN_US, count=_NSO_FN_INSNS)
        except Exception:  # noqa: BLE001 - a fault (or a hook error) ends this export's run only
            pass
        if probes and pst["trap"]:  # kill / raise / exit reached: the debugged side, not the answer
            del strs[mark:]
            return
        s = cstr(uc.reg_read(retr))
        if s:
            strs.append(s)

    if gate is not None:  # jni_gate_scan: the caller drives the probing through call()
        return gate(call, strs, lambda: uc.reg_read(retr), (BASE, JNI, VM), natives)
    hits, ran = [], set()
    try:  # rows 46/66: load-time constructors (OLLVM .datadiv_decode*) decrypt .data before any export runs
        ctors = _nso_ctors(elf, lambda a: rd(BASE + a, W), W)
    except Exception:  # noqa: BLE001
        ctors = []
    for va in ctors[:_NSO_MAX_CTORS]:
        v = va - BASE if va >= BASE else va
        if 0 < v < size and v not in ran:
            ran.add(v)
            call(BASE + v, ())
    hits += [m.decode() for s in strs for m in ANS_RE_B.findall(s)]
    strs.clear()
    for name, va, _ in funcs[:_NSO_MAX_FUNCS]:
        if va in ran:  # a constructor run twice re-encrypts an xor'd global
            continue
        if name == "JNI_OnLoad":
            call(BASE + va, (VM, 0))
            for fn in list(dict.fromkeys(natives))[:32]:
                call(BASE + fn if fn < BASE else fn, (JNI, 0))
        else:
            call(BASE + va, (JNI, 0) if name.startswith("Java_") else ())
        hits += [m.decode() for s in strs for m in ANS_RE_B.findall(s)]
        strs.clear()
    for a, n in ((HEAP, heap[0] - HEAP), (STACK + (1 << 20) - 0x10000, 0x10000), (BASE, size)):
        hits += [m.decode() for m in ANS_RE_B.findall(rd(a, n))]
    return hits


# Anti-debug / root / instrumentation gates (rows 41, 47, 48, 66): the import's return value on a clean device
# (untraced, no su, no frida). fopen/open of a /proc path succeeds when clean (the gate then reads it).
_NGB_CLEAN = {"ptrace": 0, "fopen": 0, "fopen64": 0, "open": -1, "open64": -1, "openat": -1, "opendir": 0, "popen": 0,
              "access": -1, "faccessat": -1, "stat": -1, "lstat": -1, "stat64": -1, "lstat64": -1, "strstr": 0,
              "strcasestr": 0, "memmem": 0, "dlopen": 0, "__system_property_find": 0}
_NGB_PATH2 = {"openat", "faccessat"}  # path is the 2nd argument
_NGB_FUNCS, _NGB_INSNS, _NGB_S = 24, 6000, 0.25
_NGB_X86_JCC = {"je": "eq", "jz": "eq", "jne": "ne", "jnz": "ne", "js": "mi", "jns": "pl", "jl": "lt", "jge": "ge",
                "jle": "le", "jg": "gt", "jb": "lo", "jae": "hs", "jbe": "ls", "ja": "hi"}


def _ngb_reg(n):
    """Canonical 64-bit register name (eax/ax/al -> rax, r12d -> r12, w3 -> x3)."""
    m = re.fullmatch(r"(r\d+)[dwb]?", n) or re.fullmatch(r"e?([abcd])[xlh]", n) or re.fullmatch(r"[er]?(si|di|bp|sp)l?", n)
    if m:
        g = m.group(1)
        return g if g.startswith("r") else "r" + g + ("x" if len(g) == 1 else "")
    return "x" + n[1:] if re.fullmatch(r"w\d+", n) else n


def _ngb_cond(cc, a, b, w):
    """Does condition `cc` hold after `cmp a, b` (width w bits)? None when unknown."""
    m = (1 << w) - 1
    sa, sb = [((v & m) ^ (1 << w - 1)) - (1 << w - 1) for v in (a, b)]
    ua, ub = a & m, b & m
    r = {"eq": ua == ub, "ne": ua != ub, "lt": sa < sb, "ge": sa >= sb, "le": sa <= sb, "gt": sa > sb,
         "mi": (sa - sb) & m >> (w - 1) & 1 == 1, "pl": (sa - sb) & m >> (w - 1) & 1 == 0, "lo": ua < ub, "hs": ua >= ub,
         "ls": ua <= ub, "hi": ua > ub, "cc": ua < ub, "cs": ua >= ub}
    return r.get(cc)


def _ngb_imports(elf):
    """GOT slot va -> imported name (JUMP_SLOT / GLOB_DAT RELA entries against .dynsym)."""
    want = {"EM_X86_64": (7, 6), "EM_AARCH64": (1026, 1025)}.get(elf.arch, ())
    got = {}
    for _, typ, _, off, ssz, link in elf.secs:
        syms = elf.syms.get(link)
        if typ != 4 or not syms:
            continue
        for r_off, info, _ in struct.iter_unpack("<QQq", elf.b[off:off + min(ssz, 24 << 16) // 24 * 24]):
            if info & 0xFFFFFFFF in want and info >> 32 < len(syms):
                got[r_off] = syms[info >> 32][0].split("@")[0]
    return got


def _ngb_walk(elf, md, arch, va, size, got, ctx, depth):
    """Walk one function from `va`, following ONLY the clean side of every gate branch (a conditional branch on the
    register holding a gate import's result, evaluated with _NGB_CLEAN) and both sides of every other branch.
    Appends data refs / immediates seen to ctx['refs'] / ctx['keys']; ctx['gates'] counts resolved gate branches."""
    lo, hi = va, va + (size or 0x1000)
    work, seen, plt = [va], set(), ctx["plt"]
    while work and ctx["n"] < _NGB_INSNS and time.time() < ctx["end"]:
        a = work.pop(0)
        if a in seen or not lo <= a < hi:
            continue
        alias, flags, pages, argref, chain = set(), None, {}, {}, {}
        for ins in md.disasm(elf.at(a, hi - a), a):
            if ins.address in seen:
                break
            seen.add(ins.address)
            ctx["n"] += 1
            mn, ops = ins.mnemonic, ins.op_str
            p = [x.strip(" []!") for x in ops.split(",")] if ops else []
            dst = _ngb_reg(p[0].split()[-1]) if p and p[0] else ""
            tgt = None
            if arch == "EM_X86_64":
                r = _NSO_RIP.search(ops)
                if r:
                    tgt = ins.address + ins.size + int(r.group(2), 0) * (1 if r.group(1) == "+" else -1)
            elif mn == "adrp":
                pages[dst] = int(p[1].lstrip("#"), 0)
            elif mn in ("add", "ldr", "ldrb") and len(p) >= 2 and _ngb_reg(p[1]) in pages:
                off = int(p[2].lstrip("#"), 0) if len(p) > 2 and p[2].lstrip("#")[:1].isdigit() else 0
                tgt = pages[_ngb_reg(p[1])] + off
                if mn == "add":
                    pages[dst] = tgt
            if tgt is not None:
                if mn == "add" and _ngb_reg(p[1]) == dst and dst in chain:  # adrp; add #lo; add #field: one ref
                    ctx["refs"][chain[dst]] = tgt
                else:
                    ctx["refs"].append(tgt)
                chain.pop(dst, None)
                if mn == "add":
                    chain[dst] = len(ctx["refs"]) - 1
                if mn in ("lea", "add") or arch == "EM_X86_64" and mn == "mov" and "ptr" not in p[0]:
                    argref[dst] = tgt
            mi = _NSO_IMM.search(ops)
            if mi and mn.startswith(("xor", "eor", "mov")) and 0 < int(mi.group(1), 0) < 256:
                k = bytes([int(mi.group(1), 0)])
                if k not in ctx["keys"]:
                    ctx["keys"].append(k)
            t = _NSO_IMM.search(ops)
            t = int(t.group(1), 0) if t and mn.startswith(("call", "bl", "j", "b", "cb", "tb")) else None
            if mn in ("call", "bl"):
                slot = tgt if mn == "call" and "ptr" in ops else plt.get(t) if t is not None else None
                name = got.get(slot) if slot is not None else None
                if name in _NGB_CLEAN:
                    path = argref.get("rsi" if name in _NGB_PATH2 else "rdi") if arch == "EM_X86_64" else \
                        argref.get("x1" if name in _NGB_PATH2 else "x0")
                    s = b"" if path is None else elf.at(path, 64).split(b"\0")[0]
                    clean = 3 if name.startswith(("fopen", "open")) and s.startswith(b"/proc/") else _NGB_CLEAN[name]
                    alias, flags = {"rax" if arch == "EM_X86_64" else "x0"}, None
                    ctx["clean"] = clean
                    continue
                if t is not None and depth < 2 and ctx["text"][0] <= t < ctx["text"][1] and t not in plt:
                    ctx["callees"].append(t)
                alias, flags = set(), None
                argref.clear()
                continue
            if alias:
                c = ctx["clean"]
                taken = None
                if mn in ("test", "cmp", "cmn") and len(p) == 2:
                    r0 = _ngb_reg(p[0])
                    w = 32 if re.match(r"e|w|r\d+d", p[0]) else 64
                    if r0 in alias and mn == "test" and _ngb_reg(p[1]) == r0:
                        flags = (c, 0, w)
                    elif r0 in alias and _NSO_IMM.search(p[1]) and mn in ("cmp", "cmn"):
                        v = int(p[1].lstrip("#"), 0)
                        flags = (c, -v if mn == "cmn" else v, w)
                    else:
                        alias = set()
                    continue
                cc = _NGB_X86_JCC.get(mn) if arch == "EM_X86_64" else mn[2:] if mn.startswith("b.") else None
                if cc and flags and t is not None:
                    taken = _ngb_cond(cc, *flags)
                elif mn in ("cbz", "cbnz") and _ngb_reg(p[0]) in alias and t is not None:
                    taken = (c == 0) == (mn == "cbz")
                elif mn in ("tbz", "tbnz") and _ngb_reg(p[0]) in alias and t is not None:
                    bit = (c >> int(p[1].lstrip("#"), 0)) & 1
                    taken = bit == (mn == "tbnz")
                elif mn == "mov" and len(p) == 2 and _ngb_reg(p[1]) in alias:
                    alias.add(dst)
                    continue
                elif dst in alias and not mn.startswith(("j", "b", "st", "push")):
                    alias.discard(dst)
                if taken is not None:
                    ctx["gates"] += 1
                    alias, flags = set(), None
                    if taken:
                        work.append(t)
                        break
                    continue
            if mn.startswith(("ret", "hlt", "ud2", "br", "blr")) or mn == "jmp" and t is None:
                break
            if t is not None and (mn.startswith(("j", "cb", "tb")) or mn == "b" or mn.startswith("b.")):
                work.append(t)
                if mn in ("jmp", "b"):
                    break


def native_gate_branch_scan(apk):
    """ANS token on the clean ('not debugged / not rooted') path of a native anti-debug / root / emulator gate (rows
    41, 47, 48, 66), static only: in each Java_* / huntress_* export of the x86_64 / arm64 lib/*/*.so, calls to
    ptrace / fopen / open / access / stat / strstr / ... (PLT stub or -fno-plt GOT slot -> .rela.plt / .rela.dyn
    name) are followed by the first conditional branch on their result (test/cmp/cmn + jcc/b.cond, cbz/cbnz,
    tbz/tbnz); the branch is evaluated with the import's clean return value (_NGB_CLEAN) and only that side is walked
    (other branches: both), local callees one level down too. The data refs on the clean path are matched raw, xor'd
    with the path's byte immediates and through decode_any. Tokens only when >= 1 gate branch was resolved; [] when
    absent; never raises."""
    import capstone
    hits = []
    end = time.time() + _NGB_S
    try:
        with zipfile.ZipFile(apk) as z:
            sos = [i for i in z.infolist() if i.filename.startswith("lib/") and i.filename.endswith(".so")
                   and 0 < i.file_size <= _NSO_MAX_BYTES][:_NSO_MAX_SO]
            sos.sort(key=lambda i: ("x86_64" not in i.filename, "arm64" not in i.filename))
            for info in sos:
                if time.time() > end:
                    break
                try:
                    b = z.read(info)
                    if b[:4] != b"\x7fELF":
                        continue
                    elf = _NsoElf(b)
                    if elf.arch not in ("EM_X86_64", "EM_AARCH64") or not elf.is64 or elf.e != "<":
                        continue
                    hits += _ngb_elf(elf, capstone, end)
                except Exception:  # noqa: BLE001 - a malformed .so contributes nothing
                    continue
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        pass
    return list(dict.fromkeys(hits))


def _ngb_elf(elf, capstone, end):
    arch = elf.arch
    a, m = _NSO_ARCH[arch][1]
    md = capstone.Cs(getattr(capstone, a), getattr(capstone, m))
    got = _ngb_imports(elf)
    if not any(n in _NGB_CLEAN for n in got.values()):
        return []
    plt = {}  # PLT stub va -> GOT slot va
    for name, addr, d in elf.sections():
        if not name.startswith(".plt"):
            continue
        page = {}
        for ins in md.disasm(d[:0x10000], addr):
            r = _NSO_RIP.search(ins.op_str) if arch == "EM_X86_64" else None
            if r and ins.mnemonic.endswith("jmp"):
                plt[addr + (ins.address - addr) // 16 * 16] = ins.address + ins.size + int(r.group(2), 0) * (
                    1 if r.group(1) == "+" else -1)
            elif ins.mnemonic == "adrp":
                page = {"at": ins.address, "v": int(ins.op_str.split("#")[-1], 0)}
            elif ins.mnemonic == "ldr" and page and "x16" in ins.op_str:
                o = re.search(r"#(0x[0-9a-f]+|\d+)\]", ins.op_str)
                plt[page["at"]] = page["v"] + (int(o.group(1), 0) if o else 0)
                page = {}
    text = next(((ad, ad + len(d)) for n, ad, d in elf.sections() if n == ".text"), (0, 0))
    datas = [(ad, ad + len(d)) for _, ad, d in elf.sections(data_only=True)]
    objs = {val: size for syms in elf.syms.values() for _, val, size, typ, shndx in syms
            if typ == 1 and shndx and 0 < size <= 4096}
    funcs = _nso_exports(elf)
    sizes = {va: size for _, va, size in funcs}
    hits = []
    for name, va, size in [f for f in funcs if f[0].startswith("Java_") or "huntress" in f[0].lower()][:_NGB_FUNCS]:
        if time.time() > end:
            break
        ctx = {"refs": [], "keys": [], "gates": 0, "callees": [], "plt": plt, "text": text, "n": 0, "end": end,
               "clean": 0}
        _ngb_walk(elf, md, arch, va, size, got, ctx, 0)
        if not ctx["gates"]:
            continue
        done = {va}
        while ctx["callees"]:
            c = ctx["callees"].pop(0)
            if c not in done and len(done) < 8:
                done.add(c)
                _ngb_walk(elf, md, arch, c, sizes.get(c) or 0x400, got, ctx, 1)
        for t in list(dict.fromkeys(ctx["refs"]))[:_NSO_REF_TARGETS]:
            if not any(lo <= t < hi for lo, hi in datas) or time.time() > end:
                continue
            raw = elf.at(t, objs.get(t, 512))
            blobs = [raw[:objs[t]]] if t in objs else []
            blobs += [x for x in (raw.split(b"\0")[0],) if len(x) >= 8 and x not in blobs]
            for x in blobs:
                found = ANS_RE_B.findall(x)
                for k in ctx["keys"][:16]:
                    found = found or ANS_RE_B.findall(x.translate(bytes(i ^ k[0] for i in range(256))))
                for k in [None] + ctx["keys"][:6]:
                    if found or time.time() > end:
                        break
                    r = decode_any(x, key=None if k is None else k[0], depth=2, cap=300, chain=False)
                    found = [h.encode() for h in ANS_RE_T.findall(r or "")]
                hits += [h.decode() for h in found]
    return hits


# --- native code loaded later: System.load(<asset .so extracted to filesDir>) (coverage atlas: native-payload-system-
# load). An ELF stored under assets/ / res/raw (plain, inside a nested jar/apk/zip, or wrapped: payload_unwrap peels
# base64/hex/zlib/xz/bz2 and derives xor/add/rolling keys from the ELF ident) is re-homed as lib/<abi>/ of an in-memory
# APK (with the host classes*.dex for RegisterNatives) and run through native_export_scan's own chain. ---
_ANL_MAX_ELF, _ANL_MAX_ENTRIES, _ANL_BUDGET_S = 4, 512, 0.6
_ANL_ABI = {62: "x86_64", 183: "arm64-v8a", 40: "armeabi-v7a", 3: "x86"}
_ANL_SKIP = re.compile(r"classes\d*\.dex|AndroidManifest\.xml|resources\.arsc|META-INF/.*|lib/.*|(?!res/raw/)res/.*")


def _anl_elves(z, deadline, depth=1):
    """ELF images (bytes) among the non-lib/ entries of zip `z`: plain, one nested zip/jar/apk level down, or wrapped
    (payload_unwrap kind 'elf')."""
    out = []
    for info in z.infolist()[:_ANL_MAX_ENTRIES]:
        if len(out) >= _ANL_MAX_ELF or time.time() > deadline:
            break
        n = info.filename
        if info.is_dir() or _ANL_SKIP.fullmatch(n) or n.endswith(".json") \
                or not (0x40 <= info.file_size <= _NSO_MAX_BYTES):
            continue
        try:
            with z.open(info) as f:
                head = f.read(16)
            if head.startswith(_ACD_MEDIA):
                continue
            if head[:4] == b"\x7fELF":
                out.append(z.read(info))
            elif head[:4] == b"PK\x03\x04":
                if depth > 0:
                    with zipfile.ZipFile(io.BytesIO(z.read(info))) as inner:
                        out += _anl_elves(inner, deadline, depth - 1)[:_ANL_MAX_ELF - len(out)]
            elif not _pku_kind(head):
                got = payload_unwrap(z.read(info), min(deadline, time.time() + _PKU_BUDGET_S))
                if got and got[0] == "elf":
                    out.append(got[1])
        except Exception:  # noqa: BLE001 - a truncated / impostor entry contributes nothing
            continue
    return out


def asset_native_candidates(apk):
    """ANS tokens computed by an ELF the app ships outside lib/<abi>/ and loads with System.load after extracting it
    (assets/, res/raw, a nested payload jar/apk, xor / add / zlib / base64 wrapped): each image is placed at
    lib/<abi by e_machine>/libasset<i>.so of an in-memory zip next to the host classes*.dex, then native_export_scan
    runs on it (rodata xor sweep, Java_* / RegisterNatives / no-arg exports, .init_array decrypt, unicorn emulation,
    multi-ABI consensus, gate scan). [] when absent; never raises."""
    try:
        with zipfile.ZipFile(apk) as z:
            elves = _anl_elves(z, time.time() + _ANL_BUDGET_S)
            if not elves:
                return []
            bio = io.BytesIO()
            with zipfile.ZipFile(bio, "w", zipfile.ZIP_STORED) as w:
                for i, b in enumerate(elves):
                    abi = _ANL_ABI.get(int.from_bytes(b[18:20], "little" if b[5] == 1 else "big"), "unknown")
                    w.writestr(f"lib/{abi}/libasset{i}.so", b)
                for n in z.namelist():
                    if re.fullmatch(r"classes\d*\.dex", n):
                        w.writestr(n, z.read(n))
        return native_export_scan(bio, _assets=False)
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        return []


def native_export_scan(apk, _assets=True):
    """ANS tokens computed by native code (no literal in the .so): for each lib/*/*.so (pyelftools) the exported funcs
    (JNI_OnLoad, Java_*, huntress_*, the rest) are disassembled (capstone) for their xor/eor byte constants, and every
    .rodata/.data blob is xor'd / decode_any'd with them; when that finds nothing, the exports are emulated in unicorn
    (x86_64 / arm64 / armeabi-v7a ARM+Thumb / x86; fake JNIEnv/JavaVM, RegisterNatives followed), after the load-time
    constructors (DT_INIT, .init_array, OLLVM `.datadiv_decode*`: rows 46/66) have decrypted .data. Multi-ABI (row 40):
    emulation goes on through the other lib/<abi>/ dirs until one token is confirmed by >= 2 ABIs; tokens rank by
    the number of ABIs that produced them, then by an assets/ entry quoting them. With no lib/ hit, an ELF shipped in
    assets / res/raw / a nested jar (plain or wrapped) and loaded via System.load goes through the same chain
    (asset_native_candidates). Bounded (~1.2 s per pass); [] when absent; never raises."""
    hits, abis = [], {}  # token -> {lib/<abi> dirs that produced it}

    def note(new, abi):
        hits.extend(new)
        for t in new:
            abis.setdefault(t, set()).add(abi)

    deadline = time.time() + _NSO_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            sos = [i for i in z.infolist() if i.filename.startswith("lib/") and i.filename.endswith(".so")
                   and 0 < i.file_size <= _NSO_MAX_BYTES][:_NSO_MAX_SO]
            sos.sort(key=lambda i: ("x86_64" not in i.filename, "arm64" not in i.filename))
            if sos:  # cold imports (pyelftools / capstone / unicorn: ~0.7 s on a slow disk) are not the work budget
                import capstone  # noqa: F401
                import elftools.elf.elffile  # noqa: F401
                import unicorn  # noqa: F401
                deadline = time.time() + _NSO_BUDGET_S
            elves, dex = [], None
            for info in sos:
                abi = info.filename.rsplit("/", 2)[-2] if info.filename.count("/") >= 2 else ""
                try:
                    b = z.read(info)
                    if b[:4] != b"\x7fELF":
                        continue
                    elf = _NsoElf(b)
                    arch = elf.arch
                    if arch not in _NSO_ARCH:
                        continue
                    funcs = _nso_exports(elf)
                    reg = []
                    if not any(n.startswith("Java_") for n, _, _ in funcs):  # row 39: dynamic registration only
                        try:
                            if dex is None:
                                dex = b"".join(z.read(n) for n in z.namelist()
                                               if re.fullmatch(r"classes\d*\.dex", n))[:64 << 20]
                            reg = _nso_registered(elf, dex)
                        except Exception:  # noqa: BLE001
                            reg = []
                    try:  # the export-referenced candidates rank first; the section-wide sweep follows
                        note(_nso_refs(elf, arch, funcs, deadline, reg), abi)
                    except Exception:  # noqa: BLE001
                        pass
                    try:  # row 40: stack strings built by immediate stores
                        note(_nso_stack(elf, arch, funcs, deadline), abi)
                    except Exception:  # noqa: BLE001
                        pass
                    note(_nso_static(elf, _nso_xor_keys(elf, arch, funcs, deadline), deadline), abi)
                    elves.append((elf, arch, funcs, abi))
                except Exception:  # noqa: BLE001 - a malformed .so contributes nothing
                    continue
            for elf, arch, funcs, abi in elves:
                done = {a for v in abis.values() for a in v}
                if time.time() > deadline or (hits and (any(len(v) >= 2 for v in abis.values())
                                                        or all(e[3] in done for e in elves))):
                    break  # one ABI only (every day so far): the first hits end it, as before
                if abi in done:
                    continue
                try:
                    new = _nso_emulate(elf, arch, funcs, deadline)
                    if not new and (_NSO_PROBE_IMPORTS & {y[0].split("@")[0] for i, ys in elf.syms.items()
                                                             if elf.secs[i][1] == 11 for y in ys if not y[4]}
                                    or _nso_has_svc(elf)):  # raw syscall probes: no libc import to see
                        # row 66: the export folds its anti-debug probes (ptrace / TracerPid / su / fork) into the
                        # value: rerun with libc answering as a clean device (own budget: the plain pass may spend all)
                        new = _nso_emulate(elf, arch, funcs, max(deadline, time.time() + _NSO_PROBE_S), probes=True)
                    note(new, abi)
                except Exception:  # noqa: BLE001
                    continue
            hits = list(dict.fromkeys(hits))
            if len(hits) > 1:  # consensus across ABIs, then an asset quoting the token
                quoted = b"".join(z.read(i)[:1 << 20] for i in z.infolist()[:256]
                                  if i.filename.startswith("assets/") and 0 < i.file_size <= 4 << 20)
                hits.sort(key=lambda t: (-len(abis.get(t, ())), t.encode() not in quoted))
            if hits and sos:  # rows 41/47/48/66: a token on the clean side of an anti-debug / root gate ranks first
                gated = native_gate_branch_scan(apk)
                hits = gated + [t for t in hits if t not in gated]
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    if not hits and _assets:  # nothing from lib/<abi>/: an ELF in assets loaded via System.load (asset_native_candidates)
        hits = asset_native_candidates(apk)
    return list(dict.fromkeys(hits))


_GATE_INPUTS = (0, 1, 0x7F, 0x80, 0xFF, 0x100, 0x7FFF, 0x8000, 0xFFFF, 0x10000, 0x10001, 0x7FFFFFFF, -1, -0x8000,
                -0x10000)
_GATE_MAX_FN = 0x400      # Java_* exports probed (an `int` gate sits in the export or a small helper it calls)
_GATE_MAX_CHECK = 0x100   # other exports: small int checkers only
_GATE_BUDGET_S = 1.0
_GATE_X86_R16 = re.compile(r"^(ax|bx|cx|dx|si|di|bp|r\d+w)$")
_GATE_X86_R8 = re.compile(r"^(al|bl|cl|dl|sil|dil|bpl|r\d+b)$")


def _gate_order(v):
    return (v < 0, abs(v))


def _gate_narrowing(elf, arch, va, size):
    """[u8/s8/u16/s16 found, strongest first] or ["u32"] from the gate's code (the export up to its first conditional
    branch + the helpers it calls directly): x86 movzx/movsx of
    a 16/8-bit register, cwde/cbw, 16-bit cmp/test, and/test with 0xffff/0xff/0x8000/0x80; arm64 uxth/sxth/uxtb/sxtb
    (also as operand extends), tst/and with #0xffff/#0xff/#0x8000/#0x80."""
    import capstone
    a, m = _NSO_ARCH[arch][1]
    md = capstone.Cs(getattr(capstone, a), getattr(capstone, m))
    seen, todo, tags = set(), [(va, min(size or _GATE_MAX_CHECK, _GATE_MAX_FN))], []
    while todo and len(seen) < 6:
        start, n = todo.pop(0)
        if start in seen:
            continue
        seen.add(start)
        for ins in md.disasm(elf.at(start, n), start):
            mn, ops = ins.mnemonic, [o.strip() for o in ins.op_str.split(",")]
            if mn in ("call", "bl") and ops[0].startswith(("0x", "#0x")):
                t = int(ops[0].lstrip("#"), 16)
                if elf.at(t, 1) and not any(t == s[2] for s in elf.secs if s[0] in (".plt", ".plt.sec")):
                    todo.append((t, _GATE_MAX_CHECK))
            if mn in ("ret", "retq") and start != va and ins.address > start:
                break
            imm = ops[-1].lstrip("#") if ops else ""
            if mn in ("uxth", "sxth", "uxtb", "sxtb"):
                tags.append({"uxth": "u16", "sxth": "s16", "uxtb": "u8", "sxtb": "s8"}[mn])
            elif arch == "EM_AARCH64" and any(x in ins.op_str for x in ("uxth", "sxth", "uxtb", "sxtb")):
                tags.append(next(t for x, t in (("uxth", "u16"), ("sxth", "s16"), ("uxtb", "u8"), ("sxtb", "s8"))
                                 if x in ins.op_str))
            elif mn in ("movzx", "movsx") and len(ops) == 2:
                w = "16" if _GATE_X86_R16.match(ops[1]) or ops[1].startswith("word") else \
                    "8" if _GATE_X86_R8.match(ops[1]) or ops[1].startswith("byte") else ""
                if w:
                    tags.append(("u" if mn == "movzx" else "s") + w)
            elif mn in ("cwde", "cwd", "cwtl"):
                tags.append("s16")
            elif mn in ("cbw",):
                tags.append("s8")
            elif mn in ("cmp", "test") and ops and _GATE_X86_R16.match(ops[0]):
                tags.append("u16")
            elif mn in ("and", "ands", "tst", "test") and imm in ("0xffff", "0xff", "0x8000", "0x80"):
                tags.append({"0xffff": "u16", "0xff": "u8", "0x8000": "s16", "0x80": "s8"}[imm])
            elif mn in ("shr", "sar") and ops and _GATE_X86_R16.match(ops[0]):  # shr $0xf, %dx: the int16 sign bit
                tags.append("s16" if imm == "0xf" else "u16")
            elif mn in ("tbz", "tbnz") and imm in ("0xf", "0x7", "15", "7"):
                tags.append("s16" if imm in ("0xf", "15") else "s8")
            elif mn in ("ubfx", "sbfx") and len(ops) == 4 and ops[2].lstrip("#") in ("0", "0x0") and \
                    ops[3].lstrip("#") in ("16", "0x10", "8", "0x8"):
                tags.append(mn[0] + ("16" if ops[3].lstrip("#") in ("16", "0x10") else "8"))
            if start == va and (mn.startswith(("b.", "cbz", "cbnz", "tbz", "tbnz")) or
                                (mn.startswith("j") and mn != "jmp")):
                break  # the export's gate ends at its first conditional branch (the payload after it is not the gate)
    return [t for t in ("s16", "u16", "s8", "u8") if t in tags] or ["u32"]


def jni_gate_scan(apk):
    """Bypass input of a JNI type/length-narrowing gate (row 65; D16 nativeEvidence(len) passed only for 65536): every
    Java_* export (<= 0x400 bytes), every RegisterNatives target and every small (< 0x100) other export of the x86_64 /
    arm64 lib/*/*.so is run in unicorn (fake JNIEnv, as native_export_scan) over the boundary ints _GATE_INPUTS, then,
    if none passes, over (a, b) pairs of them. The commonest outcome (NewStringUTF strings, else the int return) is
    the denial; every other outcome passes. Returns [{"export", "input", "arg2", "narrowing", "narrowings" (all the
    narrowing ops seen, for a two-arg gate), "returns", "answer"}],
    smallest passing input first per export (non-negative ascending, then negative); arg2 None when one int arg
    sufficed; `answer` = the ANS token in / decode_any of what it returned (None if none). [] when absent; never raises."""
    out = []
    deadline = time.time() + _GATE_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            sos = [i for i in z.infolist() if i.filename.startswith("lib/") and i.filename.endswith(".so")
                   and 0 < i.file_size <= _NSO_MAX_BYTES][:_NSO_MAX_SO]
            sos.sort(key=lambda i: ("x86_64" not in i.filename, "arm64" not in i.filename))
            if sos:
                import capstone  # noqa: F401
                import elftools.elf.elffile  # noqa: F401
                import unicorn  # noqa: F401
                deadline = time.time() + _GATE_BUDGET_S
            done = set()
            for info in sos:
                if time.time() > deadline:
                    break
                try:
                    b = z.read(info)
                    if b[:4] != b"\x7fELF":
                        continue
                    elf = _NsoElf(b)
                    if elf.arch not in ("EM_X86_64", "EM_AARCH64"):
                        continue
                    funcs = _nso_exports(elf)
                    for r in _nso_emulate(elf, elf.arch, funcs, deadline, gate=_gate_probe(elf, funcs, deadline)):
                        if r["export"] not in done:  # one ABI's answer per export
                            out.append(r)
                    done.update(r["export"] for r in out)
                except Exception:  # noqa: BLE001 - a malformed .so contributes nothing
                    continue
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        pass
    return out


def _gate_probe(elf, funcs, deadline):
    def probe(call, strs, ret, bases, natives):
        BASE, JNI, VM = bases
        targets = []
        for name, va, size in funcs[:_NSO_MAX_FUNCS]:
            if name == "JNI_OnLoad":
                call(BASE + va, (VM, 0))
                strs.clear()
                targets += [(f"native@{(fn - BASE if fn >= BASE else fn):#x}", fn - BASE if fn >= BASE else fn, 0, True)
                            for fn in list(dict.fromkeys(natives))[:16]]
            elif name.startswith("Java_") and 0 < size <= _GATE_MAX_FN:
                targets.append((name, va, size, True))
            elif 0 < size < _GATE_MAX_CHECK:
                targets.append((name, va, size, False))
        res = []
        for name, va, size, jni in targets[:24]:
            def run(a, b):
                strs.clear()
                call(BASE + va, ((JNI, 0) if jni else ()) + (a & 0xFFFFFFFF, b & 0xFFFFFFFF))
                r = ret()
                o = tuple(strs) if strs else r & 0xFFFFFFFF
                strs.clear()
                return o
            for pairs in ([(a, 0) for a in _GATE_INPUTS],
                          [(a, b) for a in _GATE_INPUTS for b in _GATE_INPUTS if b]):
                if time.time() > deadline:
                    return res
                outs = {p: run(*p) for p in pairs}
                if len(pairs) > len(_GATE_INPUTS):
                    outs.update({(a, 0): o for (a, b), o in one.items()})
                vals = list(outs.values())
                deny = max(vals, key=lambda o: (vals.count(o), o == outs[(0, 0)]))
                if 2 * vals.count(deny) <= len(vals):  # a lookup (notes[i % n]), not a gate
                    break
                ok = sorted((p for p, o in outs.items() if o != deny),
                            key=lambda p: (_gate_order(p[0]), _gate_order(p[1])))
                if ok and len(ok) < len(outs):
                    a, b = ok[0]
                    o = outs[ok[0]]
                    txt = "\n".join(dict.fromkeys(t.decode("latin-1") for t in o if t.isascii() and bytes(
                        t).decode().isprintable())) if isinstance(o, tuple) else str(o)
                    m = ANS_RE_T.search(txt)
                    if not m:
                        for s in (o if isinstance(o, tuple) else ()):
                            m = ANS_RE_T.search(str(decode_any(s, depth=2, chain=False) or ""))
                            if m:
                                break
                    ans = m.group(0) if m else None
                    nw = _gate_narrowing(elf, elf.arch, va, size)
                    res.append({"export": name, "input": a, "arg2": b if len(pairs) > len(_GATE_INPUTS) else None,
                                "narrowing": nw[0], "narrowings": nw, "returns": txt[:200],
                                "answer": ans})
                    break
                one = outs
        return res
    return probe


# --- Java side of the JNI boundary: dex `native` methods and the constants each call site passes (row 65) ------------
_DNC_MAX_DEX = 32 << 20
_DNC_MAX_UNITS = 2_000_000  # code units decoded across all methods
_DNC_BUDGET_S = 1.0
_DNC_NOWRITE = frozenset([0x00, 0x0E, 0x0F, 0x10, 0x11, 0x1D, 0x1E, 0x1F, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C]
                         + list(range(0x32, 0x3E)) + list(range(0x4B, 0x52)) + list(range(0x59, 0x60))
                         + list(range(0x67, 0x79)) + [0xFA, 0xFB, 0xFC, 0xFD])
_DNC_NIBDST = frozenset([0x01, 0x04, 0x07, 0x12, 0x20, 0x21, 0x23] + list(range(0x52, 0x59)) + list(range(0x7B, 0x90))
                        + list(range(0xB0, 0xD8)))
_DNC_IFOP = {0x32: "==", 0x33: "!=", 0x34: "<", 0x35: ">=", 0x36: ">", 0x37: "<="}
_DNC_NEG = {"==": "!=", "!=": "==", "<": ">=", ">=": "<", ">": "<=", "<=": ">"}
_DNC_SWAP = {"==": "==", "!=": "!=", "<": ">", ">=": "<=", ">": "<", "<=": ">="}


def _dnc_tables(d):
    """(sget, tdesc, mref) for one dex: string by idx, type descriptor by idx, method_id idx -> (class, name, params, ret)."""
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_str, o_str, n_typ, o_typ = u32(0x38), u32(0x3C), u32(0x40), u32(0x44)
    n_pro, o_pro, n_met, o_met = u32(0x48), u32(0x4C), u32(0x58), u32(0x5C)
    if (n_str > 1 << 22 or o_str + 4 * n_str > len(d) or o_typ + 4 * n_typ > len(d) or o_pro + 12 * n_pro > len(d)
            or o_met + 8 * n_met > len(d)):
        return None

    @lru_cache(maxsize=None)
    def sget(si):
        if si >= n_str:
            return None
        n, j = _uleb(d, u32(o_str + 4 * si))
        e = d.find(b"\0", j, j + 4 * n + 1)
        return d[j:e].decode("utf-8", "replace") if e >= j else None

    def tdesc(ti):
        return sget(u32(o_typ + 4 * ti)) if ti < n_typ else None

    @lru_cache(maxsize=None)
    def mref(mi):
        if mi >= n_met:
            return None
        ci, pi, ni = struct.unpack_from("<HHI", d, o_met + 8 * mi)
        if pi >= n_pro:
            return None
        _, rt, poff = struct.unpack_from("<III", d, o_pro + 12 * pi)
        ps = []
        if poff and poff + 4 <= len(d):
            ps = [tdesc(struct.unpack_from("<H", d, poff + 4 + 2 * k)[0]) for k in range(min(u32(poff), 255))]
        return tdesc(ci), sget(ni), tuple(ps), tdesc(rt)
    return sget, tdesc, mref


def _dnc_methods(d):
    """[(method_idx, access_flags, code_off)] of every encoded method in one dex's class_data."""
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_cls, o_cls = u32(0x60), u32(0x64)
    if n_cls > 1 << 20 or o_cls + 32 * n_cls > len(d):
        return []
    out = []
    for c in range(n_cls):
        cdata = u32(o_cls + 32 * c + 24)
        if not cdata or cdata >= len(d):
            continue
        try:
            i = cdata
            sf, i = _uleb(d, i)
            inf, i = _uleb(d, i)
            dm, i = _uleb(d, i)
            vm, i = _uleb(d, i)
            for _ in range(2 * (sf + inf)):
                _, i = _uleb(d, i)
            for n in (dm, vm):
                mi = 0
                for _ in range(n):
                    diff, i = _uleb(d, i)
                    fl, i = _uleb(d, i)
                    code, i = _uleb(d, i)
                    mi += diff
                    out.append((mi, fl, code))
        except (IndexError, ValueError):
            continue
    return out


def _dnc_val(v):
    if v is None:
        return None
    k, x = v[0], v[1]
    if k == "int":
        return x
    if k == "str":
        return x
    if k == "bytes":
        return {"bytes_of": x, "length": len(x.encode())}
    if k == "len":
        return {"length_of": x[0], "value": x[1]}
    return None


def _dnc_walk(ins, n_ins, sget, mref, natives):
    """Linear register walk of one method: [(native key, args, static, length checks seen before the call)]."""
    regs, pend, checks, calls, pc = {}, None, [], [], 0
    while pc < n_ins:
        p = 2 * pc
        op = ins[p]
        a8 = ins[p + 1]
        if op == 0 and a8 in (1, 2, 3):  # switch / fill-array payloads
            if a8 == 1:
                pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
            elif a8 == 2:
                pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
            else:
                w, n = struct.unpack_from("<HI", ins, p + 2)
                pc += 4 + (w * n + 1) // 2
            continue
        if p + 2 * _DOP_W[op] > len(ins):
            break
        res = None
        if op == 0x12:  # const/4
            regs[a8 & 0xF] = ("int", ((a8 >> 4) ^ 8) - 8)
        elif op in (0x13, 0x15, 0x16, 0x19):  # const/16, const/high16, const-wide/16, const-wide/high16
            v = _s16(struct.unpack_from("<H", ins, p + 2)[0])
            regs[a8] = ("int", v << 16 if op == 0x15 else v << 48 if op == 0x19 else v)
        elif op in (0x14, 0x17):  # const, const-wide/32
            regs[a8] = ("int", struct.unpack_from("<i", ins, p + 2)[0])
        elif op == 0x18:  # const-wide
            regs[a8] = ("int", struct.unpack_from("<q", ins, p + 2)[0])
        elif op in (0x1A, 0x1B):  # const-string(/jumbo)
            s = sget(struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0])
            regs[a8] = ("str", s) if s is not None else None
        elif op in (0x01, 0x04, 0x07):  # move vA, vB
            regs[a8 & 0xF] = regs.get(a8 >> 4)
        elif op in (0x02, 0x05, 0x08):  # move/from16 vAA, vBBBB
            regs[a8] = regs.get(struct.unpack_from("<H", ins, p + 2)[0])
        elif op in (0x0A, 0x0B, 0x0C):  # move-result*
            regs[a8] = pend
        elif op == 0x21:  # array-length vA, vB
            src = regs.get(a8 >> 4)
            regs[a8 & 0xF] = ("len", (src[1], len(src[1].encode()))) if src and src[0] == "bytes" else None
        elif op in _DNC_IFOP or 0x38 <= op <= 0x3D:  # length checks: if-cmp vA, vB / if-cmpz vAA
            if op in _DNC_IFOP:
                x, y, cmp = regs.get(a8 & 0xF), regs.get(a8 >> 4), _DNC_IFOP[op]
            else:
                x, y, cmp = regs.get(a8), ("int", 0), _DNC_IFOP[op - 6]
            if y and y[0] == "len":
                x, y, cmp = y, x, _DNC_SWAP[cmp]
            if x and x[0] == "len" and y and y[0] == "int":
                # the branch skips the call when `cmp` holds: the fall-through (the call) needs the negation
                checks.append({"length_of": x[1][0], "branch_if": f"len {cmp} {y[1]}", "requires": f"len {_DNC_NEG[cmp]} {y[1]}",
                               "value": y[1]})
        elif 0x6E <= op <= 0x78 and op != 0x73:  # invoke-kind 35c / 3rc
            mi = struct.unpack_from("<H", ins, p + 2)[0]
            if op <= 0x72:
                cnt, g = a8 >> 4, a8 & 0xF
                fe = struct.unpack_from("<H", ins, p + 4)[0]
                rl = [fe & 0xF, (fe >> 4) & 0xF, (fe >> 8) & 0xF, (fe >> 12) & 0xF, g][:cnt]
            else:
                c0 = struct.unpack_from("<H", ins, p + 4)[0]
                rl = list(range(c0, c0 + a8))
            m = mref(mi)
            static = op in (0x71, 0x77)
            if m:
                cls, name, params, _ = m
                r0 = regs.get(rl[0]) if rl else None
                if cls == "Ljava/lang/String;" and r0 and r0[0] == "str":
                    if name == "length" and not params:
                        res = ("len", (r0[1], len(r0[1])))
                    elif name == "getBytes":
                        res = ("bytes", r0[1])
                    elif name in ("trim", "toString", "intern"):
                        res = r0
                key = (cls, name, params)
                if key in natives:
                    k, args = (0 if static else 1), []
                    for t in params:
                        args.append(_dnc_val(regs.get(rl[k])) if k < len(rl) else None)
                        k += 2 if t in ("J", "D") else 1
                    calls.append((key, args, static, list(checks)))
        elif op in _DNC_NIBDST:
            regs.pop(a8 & 0xF, None)
        elif op not in _DNC_NOWRITE:
            regs.pop(a8, None)
        if op in (0x16, 0x17, 0x18, 0x19, 0x0B, 0x04, 0x05):
            regs.pop((a8 & 0xF if op == 0x04 else a8) + 1, None)
        pend = res
        pc += _DOP_W[op]
    return calls


def dex_native_calls(apk):
    """Java side of the JNI boundary (coverage atlas row 65): every `native` method declared in the classes*.dex
    (class, name, param descriptors, return, static) and, for each invoke of it, the constants the caller loads into the
    argument registers (const/const-wide ints, const-string, "s".getBytes() -> {bytes_of, length}, "s".length()) plus the
    String.length()/byte[].length checks seen before the call in that method. [] when none; never raises.
    Answers 'which length/type crosses the boundary' and feeds call-site ints to jni_gate_scan-style bypass questions."""
    out, deadline, budget = {}, time.time() + _DNC_BUDGET_S, [_DNC_MAX_UNITS]
    try:
        z = zipfile.ZipFile(apk)
        dexes = [n for n in z.namelist() if re.fullmatch(r"classes\d*\.dex", Path(n).name)
                 and z.getinfo(n).file_size <= _DNC_MAX_DEX]
        loaded = []
        for n in dexes:
            d = z.read(n)
            if d[:4] != b"dex\n" or len(d) < 0x70:
                continue
            tabs = _dnc_tables(d)
            if not tabs:
                continue
            meths = _dnc_methods(d)
            loaded.append((d, tabs, meths))
            for mi, fl, _ in meths:
                if fl & 0x100:  # ACC_NATIVE
                    m = tabs[2](mi)
                    if m and m[1]:
                        out.setdefault((m[0], m[1], m[2]), {
                            "method": f"{m[0]}->{m[1]}({''.join(m[2])}){m[3]}", "class": m[0], "name": m[1],
                            "params": list(m[2]), "returns": m[3], "static": bool(fl & 0x8), "calls": []})
        if not out:
            return []
        names = {k[1] for k in out}
        for d, (sget, _, mref), meths in loaded:
            n_met, o_met = struct.unpack_from("<II", d, 0x58)
            hot = [struct.pack("<H", mi) for mi, (_, _, ni) in enumerate(struct.iter_unpack("<HHI", d[o_met:o_met + 8 * n_met]))
                   if sget(ni) in names and (mref(mi) or ())[:3] in out]
            for mi, fl, code in meths if hot else ():
                if not code or code + 16 > len(d) or time.time() > deadline:
                    continue
                n_ins = struct.unpack_from("<I", d, code + 12)[0]
                budget[0] -= n_ins
                if budget[0] < 0:
                    break
                ins = d[code + 16:code + 16 + 2 * n_ins]
                if not any(h in ins for h in hot):
                    continue
                try:
                    calls = _dnc_walk(ins, n_ins, sget, mref, out)
                except (IndexError, ValueError, struct.error):
                    continue
                if calls:
                    m = mref(mi)
                    caller = f"{m[0]}->{m[1]}({''.join(m[2])}){m[3]}" if m else str(mi)
                    for key, args, static, checks in calls:
                        out[key]["calls"].append({"caller": caller, "args": args, "length_checks": checks})
    except Exception:  # noqa: BLE001 -- decoy / truncated input: report what was parsed
        pass
    return sorted(out.values(), key=lambda r: r["method"])


_NEST_MAGICS = (b"PK\x03\x04", b"dex\n")
_NEST_MAX_ENTRY = 32 << 20


def _unwrap_nested(b):
    """An entry's bytes as an inner container: a zip/jar/apk or a dex, as-is or under a single-byte xor key (an asset
    dex for DexClassLoader is often xor'd). Returns (kind, bytes) with kind 'zip'/'dex', or None."""
    if len(b) < 8:
        return None
    for magic, kind in zip(_NEST_MAGICS, ("zip", "dex")):
        k = b[0] ^ magic[0]
        if bytes(x ^ k for x in b[:4]) == magic:
            return kind, (b if not k else bytes(x ^ k for x in b))
    return None


def nested_scan(apk, depth=3, _top=True):
    """ANS tokens from containers nested inside the APK (XAPK/APKS base.apk + splits, an asset .jar/.apk/.zip, an asset
    dex for DexClassLoader, plain or single-byte-xor'd), recursing up to `depth` levels. Inside each inner zip it runs
    puzzle_candidates -> raw_entry_scan -> dex_strings (so an inner huntress_puzzle.json codec is decoded); an inner
    dex is scanned for the token directly. The outer APK's own classes*.dex are skipped (dex_strings covers them).
    [] when nothing nested yields a token; never raises."""
    hits = []
    if depth <= 0:
        return hits
    try:
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if info.is_dir() or info.file_size > _NEST_MAX_ENTRY:
                    continue
                if _top and re.fullmatch(r"classes\d*\.dex", info.filename):
                    continue
                try:
                    with z.open(info) as f:
                        head = f.read(8)
                    got = _unwrap_nested(head)
                    if not got:
                        continue
                    got = _unwrap_nested(z.read(info))
                except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError):
                    continue
                if not got:
                    continue
                kind, inner = got
                if kind == "dex":
                    hits += [m.decode() for m in ANS_RE_B.findall(inner)]
                    continue
                bio = io.BytesIO(inner)
                hits += [m.group(0) for c in puzzle_candidates(bio) for m in ANS_RE_T.finditer(c)]
                hits += raw_entry_scan(bio) + dex_strings(bio) + nested_scan(bio, depth - 1, False)
    except Exception:  # noqa: BLE001 - truncated / impostor container: no answer here, never raise
        pass
    if not hits:
        hits = asset_cipher_dex_scan(apk, depth)
    if not hits:
        hits = payload_unwrap_scan(apk, depth)
    return list(dict.fromkeys(hits))


# --- encrypted asset dex / jar for a DexClassLoader (coverage atlas rows 42, 44; MASVS-RESILIENCE D15-D17) -----------
_ACD_LOADERS = re.compile(rb"(?:InMemory|Base|Path|Delegate_?Last)?DexClassLoader|PathClassLoader|InMemoryDexClassLoader")
_ACD_SKIP = re.compile(r"classes\d*\.dex|AndroidManifest\.xml|resources\.arsc|META-INF/.*|lib/.*|(?!res/raw/)res/.*")
_ACD_MEDIA = (b"\x89PNG", b"\xff\xd8\xff", b"GIF8", b"RIFF", b"OggS", b"ID3", b"wOF", b"\x00\x01\x00\x00", b"OTTO", b"fLaC")
_ACD_MAX_PAYLOADS, _ACD_MAX_KEYS, _ACD_BUDGET_S, _ACD_HEAD = 4, 160, 0.9, 64
_ACD_DEX_FIX = b"\x70\x00\x00\x00\x78\x56\x34\x12"  # header_size 0x70 + ENDIAN_CONSTANT at 0x24


def _acd_entropy(b):
    import math
    if not b:
        return 0.0
    n = len(b)
    return -sum(c / n * math.log2(c / n) for c in (b.count(bytes([i])) for i in range(256)) if c)


def _acd_head_kind(p):
    """'dex' / 'zip' / 'z' (zlib / gzip wrapper) for a plaintext prefix, else None. A dex needs its magic AND the fixed
    header_size / endian words, so a stray 4-byte match is not enough."""
    if p[:4] == b"dex\n" and (len(p) < 0x2C or p[0x24:0x2C] == _ACD_DEX_FIX):
        return "dex"
    if p[:4] == b"PK\x03\x04":
        return "zip"
    if p[:3] == b"\x1f\x8b\x08" or (len(p) > 1 and p[0] == 0x78 and (p[0] << 8 | p[1]) % 31 == 0):
        return "z"
    return None


def _acd_unz(p):
    """A zlib / gzip wrapped plaintext inflated (<= 32 MB) when it holds a dex / zip, else None."""
    try:
        d = zlib.decompressobj(47)
        head = d.decompress(p, 64)
        if _acd_head_kind(head) not in ("dex", "zip"):
            return None
        out = head + d.decompress(d.unconsumed_tail, _NEST_MAX_ENTRY)
        return out
    except (zlib.error, ValueError):
        return None


def _acd_byte_arrays(d):
    """byte[] literals of a dex (fill-array-data payloads, element width 1, 4..64 bytes): key / IV candidates."""
    out = []
    for m in re.finditer(rb"\x00\x03\x01\x00(.{4})", d, re.S):
        n = int.from_bytes(m.group(1), "little")
        if 4 <= n <= 64:
            out.append(d[m.end():m.end() + n])
            if len(out) >= 32:
                break
    return out


def _acd_xor_derived(ct):
    """Repeating-xor keys (1..8 bytes) recovered from a dex's known header bytes: magic "dex\\n03?\\0" at 0, verified at
    0x24..0x2B (header_size + endian tag)."""
    out = []
    if len(ct) < 0x2C:
        return out
    for ver in b"56789":
        magic = b"dex\n03" + bytes([ver]) + b"\0"
        for n in range(1, 9):
            k = bytes(ct[i] ^ magic[i] for i in range(n))
            if all(ct[0x24 + i] ^ k[(0x24 + i) % n] == _ACD_DEX_FIX[i] for i in range(8)) and k not in out:
                out.append(k)
    return out


def _acd_payloads(z, loader):
    """Asset / res/raw entries that could be an encrypted dex or jar: no plain container magic, not media, and (when no
    dex references a class loader) high-entropy. Base64 / hex text assets contribute their decoded bytes."""
    out = []
    for info in z.infolist():
        n = info.filename
        if info.is_dir() or _ACD_SKIP.fullmatch(n) or not (0x40 <= info.file_size <= _NEST_MAX_ENTRY):
            continue
        with z.open(info) as f:
            head = f.read(4096)
        if head.startswith(_ACD_MEDIA) or _unwrap_nested(head[:8]) or n.endswith(".json"):
            continue
        b = z.read(info)
        blobs = [r for r in _skc_blobs(b.strip()) if len(r) >= 0x40] if re.fullmatch(rb"[A-Za-z0-9+/=_\-\s]+", head) else []
        for c in blobs or [b]:
            if loader or _acd_entropy(c[:4096]) >= 7.0:
                out.append(c)
        if len(out) >= _ACD_MAX_PAYLOADS:
            break
    return out[:_ACD_MAX_PAYLOADS]


def _acd_keys(z, dexes):
    """(key bytes, iv bytes) candidates: dex key-like constants (via _skc_keys), dex byte[] literals, the manifest package
    name (raw / hashed) and the signer cert / dex integrity digests."""
    strs, arrays, pk = [], [], []
    for d in dexes:
        strs += _skc_dex_strs(d)
        arrays += _acd_byte_arrays(d)
    try:
        m = z.read("AndroidManifest.xml")
        if m[:2] == b"\x03\x00":
            pk = [t for t in _pool_strings(m)[:400] if _IDK_PKG.fullmatch(t) and not t.startswith(_IDK_SYS)][:1]
    except KeyError:
        pass
    strs = list(dict.fromkeys(pk + sorted(dict.fromkeys(strs), key=_skc_rank)))[:40]
    raw = list(arrays) + [s.encode("utf-8", "replace") for s in strs]
    keys = list(arrays) + [k for s in strs for k in _skc_keys(s)]
    ivs = [a for a in arrays if len(a) in (12, 16)] + [k for k in keys if len(k) in (12, 16)]
    return (list(dict.fromkeys(keys))[:_ACD_MAX_KEYS], list(dict.fromkeys(raw))[:_ACD_MAX_KEYS],
            list(dict.fromkeys(ivs))[:8])


def _acd_decrypts(ct, keys, raw, ivs, deadline):
    """Yield (name, fn) decryptors fn(bytes) -> plaintext whose output prefix looks like a dex / zip / zlib stream."""
    from Crypto.Cipher import AES, ARC4

    def ok(fn):
        try:
            return _acd_head_kind(fn(ct[:_ACD_HEAD])) is not None
        except (ValueError, KeyError, IndexError):
            return False

    def xor(k):
        return lambda c: bytes(x ^ k[i % len(k)] for i, x in enumerate(c))

    for k in _acd_xor_derived(ct):
        yield "xor-derived", xor(k)
    for k in raw + [k for k in keys if k not in raw]:
        if time.time() > deadline:
            return
        if not k:
            continue
        if len(k) > 1 and ok(xor(k)):
            yield "xor", xor(k)
        if ok(lambda c, k=k: ARC4.new(k).decrypt(c)):
            yield "rc4", lambda c, k=k: ARC4.new(k).decrypt(c)
    for k in keys:
        if time.time() > deadline:
            return
        if len(k) not in (16, 24, 32):
            continue
        ecb = AES.new(k, AES.MODE_ECB)

        def cbc(iv, off=0, ecb=ecb):
            def fn(c):
                body = c[off:len(c) - (len(c) - off) % 16]
                return _xor_int(ecb.decrypt(body), iv + body[:-16]) if body else b""
            return fn
        cands = [("ecb", lambda c, ecb=ecb: ecb.decrypt(c[:len(c) - len(c) % 16]))]
        cands += [("cbc", cbc(iv)) for iv in [bytes(16)] + [v for v in ivs if len(v) == 16]]
        cands.append(("cbc-ivprefix", cbc(ct[:16], 16)))
        for nc in [bytes(12), ct[:12]] + [v[:12] for v in ivs]:
            off = 12 if nc == ct[:12] else 0
            cands.append(("gcm", lambda c, k=k, nc=nc, off=off: AES.new(
                k, AES.MODE_CTR, nonce=b"", initial_value=nc + b"\0\0\0\2").decrypt(c[off:])))
        for iv in [bytes(16), ct[:16]] + [v for v in ivs if len(v) == 16]:
            off = 16 if iv == ct[:16] else 0
            cands.append(("ctr", lambda c, k=k, iv=iv, off=off: AES.new(
                k, AES.MODE_CTR, nonce=b"", initial_value=iv).decrypt(c[off:])))
        for name, fn in cands:
            if ok(fn):
                yield name, fn
        # CBC with an unknown IV: block 2 on is exact, so a dex shows its 0x24 header words (or at 0x34 behind an IV prefix)
        p = cbc(bytes(16))(ct[:0x50])
        for off in (0, 16):
            if p[0x24 + off:0x2C + off] == _ACD_DEX_FIX:
                yield "cbc-anyiv", (lambda c, off=off, f=cbc(bytes(16)): b"dex\n035\0" + bytes(8) + f(c)[16 + off:])


def asset_cipher_dex_scan(apk, depth=2):
    """ANS tokens from an ENCRYPTED asset dex / jar loaded at runtime (DexClassLoader / InMemoryDexClassLoader /
    PathClassLoader; rows 42, 44). Gate: a dex names a class loader, or an asset is high-entropy (>= 7 bits/byte).
    Ciphers: repeating-key xor (key recovered from the dex header, or a candidate key), RC4, AES ECB / CBC (zero / key /
    byte[] / prefix IV, or any IV for a dex) / CTR / GCM (zero / prefix / byte[] nonce, tag ignored), keys from dex
    constants, dex byte[] literals, the package name and the integrity digests (integrity_facts); a zlib / gzip layer
    after decryption is inflated. Output accepted only as dex (magic + header words) or a zip that opens; then the token
    is scanned in it and dex_strings (renamed_chain_scan / dex_eval_scan ...) + puzzle / raw / nested scans recurse on
    it. [] when absent; never raises."""
    hits = []
    if depth <= 0:
        return hits
    deadline = time.time() + _ACD_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist()
                     if re.fullmatch(r"classes\d*\.dex", i.filename) and i.file_size <= _NEST_MAX_ENTRY]
            loader = any(_ACD_LOADERS.search(d) for d in dexes)
            payloads = _acd_payloads(z, loader)
            if not payloads:
                return hits
            keys, raw, ivs = _acd_keys(z, dexes)
        if loader:
            facts = [v for _, v in integrity_facts(apk) if len(v) >= 16]
            keys += [k for v in facts for k in (v, v[:16]) if len(k) in (16, 24, 32) and k not in keys]
            raw += [v for v in facts if v not in raw]
        payloads = [(c, c) for c in payloads]
        payloads += [(c, u) for c, _ in payloads if _acd_head_kind(c[:4]) == "z" for u in [_acd_unz(c)] if u]
        for ct, plain in payloads:
            found = [("plain", plain)] if plain is not ct else []
            for name, fn in ([] if found else _acd_decrypts(ct, keys, raw, ivs, deadline)):
                p = fn(ct)
                if _acd_head_kind(p[:_ACD_HEAD]) == "z":
                    p = _acd_unz(p)
                if p and _acd_head_kind(p[:_ACD_HEAD]) in ("dex", "zip"):
                    found.append((name, p))
                    break
            for _, p in found:
                if p[:4] == b"dex\n":
                    hits += [m.decode() for m in ANS_RE_B.findall(p)]
                    bio = io.BytesIO()
                    with zipfile.ZipFile(bio, "w") as w:
                        w.writestr("classes.dex", p)
                    if not hits:
                        hits += dex_strings(bio)
                    continue
                try:
                    zipfile.ZipFile(io.BytesIO(p)).close()
                except zipfile.BadZipFile:
                    continue
                bio = io.BytesIO(p)
                hits += [m.group(0) for c in puzzle_candidates(bio) for m in ANS_RE_T.finditer(c)]
                hits += raw_entry_scan(bio) + dex_strings(bio) + nested_scan(bio, depth - 1, False)
            if hits:
                break
            if found and depth >= 2:  # a stage decrypted but held nothing: its constants may unlock the next stage
                hits += multi_stage_scan(apk)
                break
    except Exception:  # noqa: BLE001 - truncated / impostor APK or payload: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- multi-stage loader (coverage atlas row 85): the stage-1 dex decrypted from an asset names ANOTHER entry (outer APK
# or a nested jar/zip) + its key (const-string / fill-array-data byte[]) and decrypts it into stage 2, up to depth 4. ---
_MS_DEPTH, _MS_BUDGET_S, _MS_BYTES, _MS_MAX_TRIES = 4, 0.9, 48 << 20, 8


def _ms_pool(z, label=""):
    """[(label, name, bytes)] entries of a zip that could hold a wrapped next stage (same gate as _acd_payloads: no plain
    container magic, not media / .json / code / resources, 0x40..32 MB); base64 / hex text contributes its decoded bytes."""
    out = []
    for info in z.infolist():
        n = info.filename
        if info.is_dir() or _ACD_SKIP.fullmatch(n) or n.endswith(".json") or not (0x40 <= info.file_size <= _NEST_MAX_ENTRY):
            continue
        with z.open(info) as f:
            head = f.read(64)
        if head.startswith(_ACD_MEDIA) or _unwrap_nested(head[:8]) or head[:4] == b"\x7fELF":
            continue
        b = z.read(info)
        blobs = [r for r in _skc_blobs(b.strip()) if len(r) >= 0x40] if re.fullmatch(rb"[A-Za-z0-9+/=_\-\s]+", head) else []
        out += [(label + n, n, c) for c in blobs or [b]]
    return out


def _ms_tokens(p):
    return [m.decode() for m in ANS_RE_B.findall(p)] + \
        [m.decode("utf-16-le") for m in re.findall(rb"A\0N\0S\0-\0(?:[0-9A-Fa-f]\0){16}", p)]


def _ms_walk(z, pool, dexes, depth, deadline, path, used, budget):
    """[(token, stage path)] below one stage: keys from this stage's dexes (_acd_keys), entries this stage names (basename
    in its dex bytes) tried first, then the rest of the pool; each decrypt (_acd_decrypts, or payload_unwrap for entries
    of a nested container) accepted as dex / zip and recursed; a leaf dex / zip goes through dex_strings."""
    out = []
    if depth <= 0 or time.time() > deadline:
        return out
    keys, raw, ivs = _acd_keys(z, dexes)
    blob = b"".join(dexes)
    cands = [c for c in pool if c[0] not in used]
    cands.sort(key=lambda c: c[1].rsplit("/", 1)[-1].encode() not in blob)
    for label, name, ct in cands[:_MS_MAX_TRIES]:
        if time.time() > deadline or budget[0] <= 0:
            break
        got = None
        for cname, fn in _acd_decrypts(ct, keys, raw, ivs, deadline):
            p = fn(ct)
            if _acd_head_kind(p[:_ACD_HEAD]) == "z":
                p = _acd_unz(p)
            if p and _acd_head_kind(p[:_ACD_HEAD]) in ("dex", "zip"):
                got = (cname, p)
                break
        if not got and "!" in label:  # keyless known-plaintext unwrap (outer entries: payload_unwrap_scan owns them)
            u = payload_unwrap(ct, min(deadline, time.time() + 0.3))
            if u and u[0] in ("dex", "zip"):
                got = ("+".join(w if isinstance(w, str) else w[0] for w in u[2]) or "plain", u[1])
        if not got:
            continue
        budget[0] -= len(got[1])
        p, step, seen = got[1], path + ("%s:%s" % (label, got[0]),), used | {label}
        toks = _ms_tokens(p)
        if toks:
            return [(t, step) for t in dict.fromkeys(toks)]
        if p[:4] == b"dex\n":
            out = _ms_walk(z, pool, [p], depth - 1, deadline, step, seen, budget)
            if not out:  # leaf stage: the token may be computed / encoded inside it
                bio = io.BytesIO()
                with zipfile.ZipFile(bio, "w") as w:
                    w.writestr("classes.dex", p)
                out = [(t, step) for t in dex_strings(bio)]
        else:
            try:
                zi = zipfile.ZipFile(io.BytesIO(p))
                inner = [zi.read(i) for i in zi.infolist() if re.fullmatch(r"classes\d*\.dex", i.filename)
                         and i.file_size <= _NEST_MAX_ENTRY]
                bio = io.BytesIO(p)
                out = [(m.group(0), step) for c in puzzle_candidates(bio) for m in ANS_RE_T.finditer(c)]
                out += [(t, step) for d in inner for t in _ms_tokens(d)]
                if not out:
                    out = _ms_walk(z, pool + _ms_pool(zi, label + "!"), inner or dexes, depth - 1, deadline, step, seen,
                                   budget)
                if not out:
                    out = [(t, step) for t in raw_entry_scan(bio) + dex_strings(bio)]
            except (zipfile.BadZipFile, OSError, EOFError, ValueError, KeyError):
                out = []
        if out:
            return out
    return out


def multi_stage_candidates(apk, depth=_MS_DEPTH):
    """[(token, stage path)] for a MULTI-STAGE loader (row 85): the outer classes*.dex hold the key of an encrypted asset
    stage 1 (dex / jar), whose own constants (const-string, fill-array-data byte[]) hold the key -- and usually the name --
    of stage 2 in the outer APK or inside the stage-1 jar, recursing to `depth` stages under a 0.9 s / 48 MB budget.
    Ciphers / key forms as asset_cipher_dex_scan; the path reads e.g. ('classes.dex', 'assets/s1.bin:cbc-ivprefix',
    'assets/core.dat:rc4'). [] when absent; never raises."""
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist()
                     if re.fullmatch(r"classes\d*\.dex", i.filename) and i.file_size <= _NEST_MAX_ENTRY]
            pool = _ms_pool(z)
            if not dexes or not pool:
                return []
            got = _ms_walk(z, pool, dexes, depth, time.time() + _MS_BUDGET_S, ("classes.dex",), frozenset(), [_MS_BYTES])
    except Exception:  # noqa: BLE001 - truncated / impostor APK or payload: no answer here
        return []
    return list(dict.fromkeys(got))


def multi_stage_scan(apk, depth=_MS_DEPTH):
    """ANS tokens of multi_stage_candidates (stage paths dropped). [] when absent; never raises."""
    return list(dict.fromkeys(t for t, _ in multi_stage_candidates(apk, depth)))


# --- wrapped secondary payload: recover the wrapper from the expected file magic (coverage atlas: payload-magic-known-
# plaintext-unwrap). An asset dex / jar / so / db with no known magic is peeled through text / compressor / reverse layers,
# then a byte-wise cipher is derived from known plaintext (the format's fixed header / trailer bytes) and verified. ---
_PKU_MAX_PAYLOADS, _PKU_MAX_NODES, _PKU_BUDGET_S, _PKU_MAX_PERIOD = 8, 12, 0.8, 16
_PKU_MAGICS = (b"dex\n", b"cdex", b"PK\x03\x04", b"\x7fELF", b"SQLite format 3\x00")
_PKU_TEXT = re.compile(rb"[A-Za-z0-9+/=_\-\s]+")
# mode: (key byte from (cipher, plain, index), plain from (cipher, key, index)); rolling modes depend on the index
_PKU_MODES = (("xor", lambda c, p, i: c ^ p, lambda c, k, i: c ^ k),
              ("add", lambda c, p, i: (c - p) & 255, lambda c, k, i: (c - k) & 255),
              ("sub", lambda c, p, i: (p - c) & 255, lambda c, k, i: (c + k) & 255),
              ("xor-k+i", lambda c, p, i: ((c ^ p) - i) & 255, lambda c, k, i: c ^ ((k + i) & 255)),
              ("xor-k^i", lambda c, p, i: c ^ p ^ (i & 255), lambda c, k, i: c ^ k ^ (i & 255)),
              ("add-k+i", lambda c, p, i: (c - p - i) & 255, lambda c, k, i: (c - k - i) & 255))
_PKU_ROLLING_MAX_PERIOD = 2


def _pku_templates(n):
    """(kind, strong {offset: byte}, weak [(offset, byte)]) known plaintext of each target format for an n-byte file.
    Strong bytes must agree with one periodic key; weak ones (usual-but-not-fixed fields) only fill key bytes left open."""
    def at(off, bs):
        return {off + i: b for i, b in enumerate(bs)}

    out = []
    tail = {**at(0x24, b"\x70\x00\x00\x00"), **at(0x28, b"\x78\x56\x34\x12")}
    weak = [*at(0x20, n.to_bytes(4, "little")).items(), *at(0x2C, bytes(8)).items(), *at(0x3C, b"\x70\0\0\0").items()]
    for v in (b"035", b"036", b"037", b"038", b"039", b"040", b"041"):
        out.append(("dex", {**at(0, b"dex\n" + v + b"\0"), **tail}, weak))
    out.append(("cdex", {**at(0, b"cdex001\0"), **at(0x28, b"\x78\x56\x34\x12")}, weak))
    if n > 0x40:
        eocd = {**at(0, b"PK\x03\x04"), **at(n - 22, b"PK\x05\x06\0\0\0\0"), **at(n - 2, b"\0\0")}
        out.append(("zip", eocd, [*at(4, b"\x14\x00").items(), *at(6, b"\x00\x00").items()]))
    for cls, ehsz in ((2, 64), (1, 52)):
        hdr = {**at(0, b"\x7fELF" + bytes([cls, 1, 1]) + bytes(9)), **at(0x14, b"\x01\0\0\0")}
        out.append(("elf", hdr, [*at(0x10, b"\x03\x00").items(), *at(0x34 if cls == 2 else 0x28, bytes([ehsz, 0])).items()]))
    out.append(("sqlite", at(0, b"SQLite format 3\x00"), [*at(0x12, b"\x01\x01\x00\x40\x20\x20").items()]))
    return out


def _pku_keys(c, strong, weak, derive, max_p):
    """Periodic keys (period 1..max_p, smallest first) consistent with every strong known byte, open bytes filled
    from the weak ones; only fully-determined keys are yielded."""
    n = len(c)
    pos = [(o, b) for o, b in strong.items() if o < n]
    wk = [(o, b) for o, b in weak if o < n]
    for p in range(1, max_p + 1):
        key, ok = {}, True
        for o, b in pos:
            k = derive(c[o], b, o)
            if key.setdefault(o % p, k) != k:
                ok = False
                break
        if not ok:
            continue
        for o, b in wk:
            key.setdefault(o % p, derive(c[o], b, o))
        if len(key) == p:
            yield bytes(key[j] for j in range(p))


def _pku_apply(c, key, plain, rolling):
    """Whole-buffer decrypt with a periodic key: one 256-byte translate table per residue class (mod lcm(p, 256) for
    an index-dependent mode)."""
    import math
    p = len(key)
    L = p * 256 // math.gcd(p, 256) if rolling else p
    out = bytearray(len(c))
    for j in range(min(L, len(c))):
        k, i = key[j % p], j & 255
        out[j::L] = c[j::L].translate(bytes(plain(x, k, i) for x in range(256)))
    return bytes(out)


def _pku_verify(kind, v):
    """Plaintext `v` really is `kind`: dex = magic + header words + file_size within len + adler32 over [12:file_size]
    (returns the dex trimmed to file_size); zip = central directory opens; elf = ident + e_ehsize; sqlite = header."""
    try:
        if kind == "dex":
            fs = int.from_bytes(v[0x20:0x24], "little")
            if v[:4] == b"dex\n" and v[0x24:0x2C] == _ACD_DEX_FIX and 0x70 <= fs <= len(v) \
                    and zlib.adler32(v[12:fs]) == int.from_bytes(v[8:12], "little"):
                return v[:fs]
        elif kind == "cdex":
            fs = int.from_bytes(v[0x20:0x24], "little")
            if v[:8] == b"cdex001\0" and v[0x28:0x2C] == b"\x78\x56\x34\x12" and fs <= len(v):
                return v
        elif kind == "zip":
            with zipfile.ZipFile(io.BytesIO(v)) as z:
                if z.namelist():
                    return v
        elif kind == "elf":
            cls = v[4]
            eh = int.from_bytes(v[0x34:0x36] if cls == 2 else v[0x28:0x2A], "little")
            if v[:4] == b"\x7fELF" and v[5] in (1, 2) and eh == (64 if cls == 2 else 52):
                return v
        elif kind == "sqlite":
            ps = int.from_bytes(v[16:18], "big")
            if v[:16] == _LS_SQLITE and v[21:24] == b"\x40\x20\x20" and (ps == 1 or (ps >= 512 and not ps & (ps - 1))):
                return v
    except (zipfile.BadZipFile, zipfile.LargeZipFile, ValueError, IndexError, EOFError, OSError, RuntimeError):
        pass
    return None


def _pku_kind(v):
    for m, kind in zip(_PKU_MAGICS, ("dex", "cdex", "zip", "elf", "sqlite")):
        if v.startswith(m):
            return kind
    return None


def _pku_layers(b):
    """(name, bytes) for one layer peeled off `b`: reversed bytes, base64 / hex text decoded, gzip / zlib / xz / lzma /
    bz2 inflated."""
    out = [("reversed", b[::-1])]
    s = b.strip()
    if _PKU_TEXT.fullmatch(s[:4096]):
        t = re.sub(rb"\s+", b"", s)
        if re.fullmatch(rb"(?:[0-9a-fA-F]{2})+", t):
            out.append(("hex", bytes.fromhex(t.decode())))
        else:
            for alt in (b"+/", b"-_"):
                try:
                    out.append(("base64", base64.b64decode(t + b"=" * (-len(t) % 4), altchars=alt, validate=True)))
                    break
                except ValueError:
                    continue
    try:
        if b[:3] == b"\x1f\x8b\x08" or (b[0] == 0x78 and (b[0] << 8 | b[1]) % 31 == 0):
            out.append(("zlib", zlib.decompressobj(47).decompress(b, _NEST_MAX_ENTRY)))
        elif b[:6] == b"\xfd7zXZ\x00" or b[:3] == b"\x5d\x00\x00":
            out.append(("lzma", lzma.LZMADecompressor().decompress(b, _NEST_MAX_ENTRY)))
        elif b[:3] == b"BZh":
            out.append(("bz2", bz2.BZ2Decompressor().decompress(b, _NEST_MAX_ENTRY)))
    except (zlib.error, lzma.LZMAError, OSError, ValueError, EOFError):
        pass
    return [(n, v) for n, v in out if len(v) >= 0x40]


def payload_unwrap(b, deadline=None):
    """(kind, plaintext, wrapper) for a wrapped secondary payload, or None. Breadth-first over layers (reversed,
    base64 / hex text, gzip / zlib / xz / bz2, depth <= 3); at each node a known magic is verified as-is, else a
    byte-wise key is derived from the format's known plaintext (dex 035..041 header words, cdex, zip local header +
    EOCD, ELF ident, SQLite header): xor / add / sub with a 1..16-byte periodic key, or rolling xor (k+i) / (k^i) /
    add (k+i), period by consistency; each candidate is decrypted only when its header is consistent and accepted only
    after a full format check (dex file_size + adler32, zip central directory, ELF e_ehsize, SQLite header)."""
    deadline = deadline or time.time() + _PKU_BUDGET_S
    queue, seen = [(b, 0, ())], set()
    while queue and len(seen) < _PKU_MAX_NODES and time.time() < deadline:
        v, d, path = queue.pop(0)
        h = hash(v[:256] + v[-64:]) ^ len(v)
        if h in seen or len(v) < 0x40:
            continue
        seen.add(h)
        kind = _pku_kind(v)
        if kind:
            got = _pku_verify(kind, v)
            if got:
                return kind, got, path
        else:
            head = v[:0x50]
            for kind, strong, weak in _pku_templates(len(v)):
                for name, derive, plain in _PKU_MODES:
                    rolling = "i" in name
                    for key in _pku_keys(v, strong, weak, derive, _PKU_ROLLING_MAX_PERIOD if rolling else _PKU_MAX_PERIOD):
                        if not key.strip(b"\0") and name in ("xor", "add", "sub"):
                            continue
                        if _pku_kind(_pku_apply(head, key, plain, rolling)) != kind:
                            continue
                        got = _pku_verify(kind, _pku_apply(v, key, plain, rolling))
                        if got:
                            return kind, got, path + ((name, key.hex()),)
                if time.time() > deadline:
                    return None
        if d < 3:
            queue += [(u, d + 1, path + (lname,)) for lname, u in _pku_layers(v)]
    return None


def _pku_hits(kind, p, depth):
    """ANS tokens in a recovered payload: the bytes (ASCII / UTF-16LE) first, then the lane scans on it (a dex via
    dex_strings, a zip via puzzle / raw / dex / nested scans, a db via local_store_scan)."""
    hits = [m.decode() for m in ANS_RE_B.findall(p)]
    hits += [m.decode("utf-16-le") for m in re.findall(rb"A\0N\0S\0-\0(?:[0-9A-Fa-f]\0){16}", p)]
    if hits:
        return hits
    bio = io.BytesIO()
    if kind == "zip":
        bio = io.BytesIO(p)
        hits += [m.group(0) for c in puzzle_candidates(bio) for m in ANS_RE_T.finditer(c)]
        return hits + raw_entry_scan(bio) + dex_strings(bio) + nested_scan(bio, depth - 1, False)
    with zipfile.ZipFile(bio, "w") as w:
        w.writestr({"dex": "classes.dex", "sqlite": "assets/payload.db"}.get(kind, "assets/payload.bin"), p)
    if kind == "dex":
        return dex_strings(bio)
    if kind == "sqlite":
        return local_store_scan(bio)
    return []


def payload_unwrap_scan(apk, depth=2):
    """ANS tokens from a WRAPPED secondary payload in assets / res/raw (an asset dex / jar / so / db xor'd, added,
    rolling-keyed, reversed, base64 / hex text, compressed -- payload_unwrap); the recovered bytes recurse through the
    lane scans. Entries with a plain container magic, media and .json are skipped (nested / puzzle scans own them).
    [] when absent; never raises."""
    hits = []
    if depth <= 0:
        return hits
    deadline = time.time() + _PKU_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            names = []
            for info in z.infolist():
                n = info.filename
                if info.is_dir() or _ACD_SKIP.fullmatch(n) or n.endswith(".json") \
                        or not (0x40 <= info.file_size <= _NEST_MAX_ENTRY):
                    continue
                with z.open(info) as f:
                    head = f.read(16)
                if head.startswith(_ACD_MEDIA) or _pku_kind(head):
                    continue
                names.append(info)
                if len(names) >= _PKU_MAX_PAYLOADS:
                    break
            for info in names:
                if time.time() > deadline:
                    break
                got = payload_unwrap(z.read(info), deadline)
                if got:
                    hits += _pku_hits(got[0], got[1], depth)
    except Exception:  # noqa: BLE001 - truncated / impostor APK or payload: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- local app stores shipped in the APK: SQLite db / shared_prefs xml / adb backup .ab (coverage atlas rows 16-18) ---
_LS_SQLITE = b"SQLite format 3\x00"
_LS_AB = b"ANDROID BACKUP\n"
_LS_MAX_ENTRY = 32 << 20
_LS_MAX_ROWS, _LS_MAX_CELLS, _LS_DECODE_BUDGET = 2000, 20_000, 300
_LS_KEYCOL = re.compile(r"^(key|xor_?key|secret|pass(word)?|seed)$", re.I)


def _ls_sqlite_rows(b, deadline):
    """Every table's rows of an in-memory SQLite image as [{column: value}] (WAL header flags reset so deserialize
    reads it; a progress handler stops the query at `deadline`)."""
    import sqlite3
    b = bytearray(b)
    if b[18:20] == b"\x02\x02":  # WAL mode: an in-memory image has no -wal/-shm, read it as a rollback-journal db
        b[18:20] = b"\x01\x01"
    con = sqlite3.connect(":memory:")
    rows = []
    try:
        con.deserialize(bytes(b))
        con.set_progress_handler(lambda: 1 if time.time() > deadline else 0, 2000)
        tabs = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for t in tabs:
            if len(rows) >= _LS_MAX_ROWS:
                break
            try:
                cur = con.execute('SELECT * FROM "%s" LIMIT %d' % (t.replace('"', '""'), _LS_MAX_ROWS - len(rows)))
                cols = [d[0] for d in cur.description or ()]
                rows += [dict(zip(cols, r)) for r in cur]
            except sqlite3.Error:
                continue
    except Exception:  # noqa: BLE001 - not a readable db image
        pass
    finally:
        con.close()
    return rows


def _ls_prefs(b):
    """A SharedPreferences xml (<map><string name=..>v</string><int name=.. value=../>...) as one {name: value} row."""
    try:
        root = ET.fromstring(b)
    except (ET.ParseError, ValueError):
        return []
    if root.tag != "map":
        return []
    row = {}
    for el in root:
        v = el.text if el.tag == "string" else el.get("value")
        if el.tag == "set":
            v = " ".join(s.text or "" for s in el)
        if el.get("name") is not None and v is not None:
            row[el.get("name")] = v
    return [row] if row else []


def _ls_ab_members(b):
    """(name, bytes) of every file in an unencrypted adb backup: 'ANDROID BACKUP' / version / compressed / 'none'
    header lines, then a (zlib-deflated) tar. Encrypted backups (AES-256 + password) yield nothing."""
    import tarfile
    parts = b.split(b"\n", 4)
    if len(parts) < 5 or parts[3].strip() != b"none":
        return []
    body = parts[4]
    if parts[2].strip() == b"1":
        d = zlib.decompressobj()
        body = d.decompress(body, _LS_MAX_ENTRY)
    out = []
    try:
        with tarfile.open(fileobj=io.BytesIO(body), mode="r:") as tf:
            for m in tf:
                if m.isfile() and m.size <= _LS_MAX_ENTRY:
                    f = tf.extractfile(m)
                    if f is not None:
                        out.append((m.name, f.read()))
    except Exception:  # noqa: BLE001 - truncated tar: keep the members read so far
        pass
    return out


def _ls_rows(name, b, deadline, depth=2):
    """Rows ({column: value}) found in one entry: a SQLite db, a shared_prefs map, or (recursively) a .ab's members;
    any other .ab member contributes its text as a single-cell row."""
    if b.startswith(_LS_SQLITE):
        return _ls_sqlite_rows(b, deadline)
    if b.startswith(_LS_AB):
        rows = []
        if depth > 0:
            for n, mb in _ls_ab_members(b):
                rows += _ls_rows(n, mb, deadline, depth - 1) or ([{n: mb}] if len(mb) <= _CHAIN_MAX_IN else [])
        return rows
    if b"<map" in b[:512] and (b.lstrip().startswith(b"<?xml") or b.lstrip().startswith(b"<map")):
        return _ls_prefs(b)
    return []


# SQLCipher-encrypted db (coverage atlas row 76): (kdf iterations, hmac/kdf digest, page size, reserved bytes) of the
# v4 / v3 / v2 defaults. Page 1 starts with the 16-byte KDF salt; each page is AES-256-CBC over [salt..page - reserve)
# with the IV in the first 16 reserved bytes (then the HMAC).
_SQLC_PROFILES = ((256000, "sha512", 4096, 80), (64000, "sha1", 1024, 48), (4000, "sha1", 1024, 48))
_SQLC_NAME = re.compile(r"\.(db|sqlite3?|sqlcipher|dat|bin|enc)$|(^|/)databases/", re.I)
_SQLC_MAX_DBS, _SQLC_MAX_PW, _SQLC_BUDGET = 4, 20, 0.9
_SQLC_RAWKEY = re.compile(r"x'([0-9a-fA-F]{64})(?:[0-9a-fA-F]{32})?'")


def _sqlc_passwords(z, dexes):
    """Passphrase candidates for an encrypted db: printable dex string-pool entries and resources.arsc strings (4-64
    chars, not a type / path / message), key-like first (_skc_rank), at most _SQLC_MAX_PW."""
    strs = []
    for d in dexes:
        if d[:4] == b"dex\n":
            for m in _SKC_POOL.finditer(d, 0x70):
                if m.group(1)[0] == len(m.group(2)):
                    t = m.group(2).decode()
                    if not _SKC_BAD.search(t) and "sqlcipher" not in t.lower():
                        strs.append(t)
    try:
        strs += [t for t in _pool_strings(z.read("resources.arsc")) if 4 <= len(t) <= 64 and t.isprintable()]
    except (KeyError, OSError, zipfile.BadZipFile, RuntimeError, ValueError):
        pass
    return sorted(dict.fromkeys(strs), key=_skc_rank)[:_SQLC_MAX_PW]


def _sqlc_decrypt(b, passwords, deadline):
    """A plain `SQLite format 3` image of SQLCipher db bytes `b` under the first (password, v4/v3/v2 profile) whose
    page-1 header decrypts to sane values (page size, file format 1/2, 64/32/32 payload fractions); None when none does.
    A passphrase `x'<64 hex>'` is the raw key (no KDF)."""
    from Crypto.Cipher import AES
    salt = b[:16]
    for pw in passwords:
        raw = _SQLC_RAWKEY.fullmatch(pw)
        for iters, dg, ps, rs in _SQLC_PROFILES:
            if time.time() > deadline:
                return None
            if len(b) < ps or len(b) % ps:
                continue
            key = bytes.fromhex(raw.group(1)) if raw else hashlib.pbkdf2_hmac(dg, pw.encode(), salt, iters, 32)
            p1 = AES.new(key, AES.MODE_CBC, b[ps - rs:ps - rs + 16]).decrypt(b[16:32])
            if int.from_bytes(p1[:2], "big") != ps or p1[2:4] not in (b"\1\1", b"\2\2") or p1[5:8] != b"\x40\x20\x20":
                continue
            out = bytearray()
            for o in range(0, len(b), ps):
                pg = b[o:o + ps]
                body = AES.new(key, AES.MODE_CBC, pg[ps - rs:ps - rs + 16]).decrypt(pg[16 if o == 0 else 0:ps - rs])
                out += (_LS_SQLITE if o == 0 else b"") + body + bytes(rs)
            out[20] = max(out[20], rs)  # the btree never reads the IV/HMAC tail (v3-compat dbs may record a larger one)
            return bytes(out)
    return None


def _sqlc_rows(z, enc, deadline):
    """Rows of every encrypted-db candidate `enc` [(name, bytes)] when the app ships SQLCipher (`sqlcipher` in a dex /
    an entry name such as lib/*/libsqlcipher.so) and a dex / arsc string opens it."""
    dexes = [z.read(n) for n in z.namelist() if re.fullmatch(r"classes\d*\.dex", Path(n).name)]
    if not (any("sqlcipher" in n.lower() for n in z.namelist()) or any(b"sqlcipher" in d for d in dexes)):
        return []
    pws, rows = _sqlc_passwords(z, dexes), []
    for _name, b in enc:
        img = _sqlc_decrypt(b, pws, deadline)
        if img:
            rows += _ls_sqlite_rows(img, deadline + 0.3)
    return rows


def local_store_scan(apk):
    """ANS tokens stored the way an app keeps local data, shipped inside the APK (or handed out alone): a SQLite db
    (`SQLite format 3\\0` magic, any entry name; every table's cells), a SharedPreferences xml (<string>/value= of a
    <map>), an unencrypted adb backup `.ab` (zlib -> tar -> those again), a SQLCipher v2/v3/v4 db (no magic, app ships
    sqlcipher; passphrase = a dex / arsc string, _sqlc_rows) when no plain store exists. Each cell is read directly, then through
    decode_payload when its row looks like a puzzle record ({codec, data|payload, key}), then decode_any with the
    row's key-ish column as the key. [] when absent; never raises."""
    hits, rows, enc = [], [], []
    deadline = time.time() + 1.0
    try:
        try:
            with zipfile.ZipFile(apk) as z:
                for info in z.infolist():
                    if info.is_dir() or info.file_size > _LS_MAX_ENTRY or time.time() > deadline:
                        continue
                    try:
                        with z.open(info) as f:
                            head = f.read(16)
                        if not (head.startswith((_LS_SQLITE, _LS_AB)) or head.lstrip().startswith((b"<?xml", b"<map"))):
                            if (_SQLC_NAME.search(info.filename) and info.file_size >= 1024 and not info.file_size % 1024
                                    and len(enc) < _SQLC_MAX_DBS and not info.filename.endswith(".dex")):
                                enc.append((info.filename, z.read(info)))
                            continue
                        rows += _ls_rows(info.filename, z.read(info), deadline)
                    except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError):
                        continue
                if enc and not rows:  # no plain store: try SQLCipher-encrypted dbs (row 76)
                    try:
                        rows += _sqlc_rows(z, enc, time.time() + _SQLC_BUDGET)
                    except Exception:  # noqa: BLE001 - impostor / truncated db: no rows
                        pass
                    deadline = max(deadline, time.time() + 0.3)
        except zipfile.BadZipFile:  # a bare .db / .ab / prefs xml delivered on its own
            if hasattr(apk, "seek"):
                apk.seek(0)
                b = apk.read(_LS_MAX_ENTRY)
            else:
                with Path(apk).open("rb") as f:
                    b = f.read(_LS_MAX_ENTRY)
            rows += _ls_rows("", b, deadline)
        budget, cells = _LS_DECODE_BUDGET, 0
        for row in rows:
            lk = {str(k).lower(): v for k, v in row.items()}
            key = next((v for k, v in row.items() if _LS_KEYCOL.match(str(k)) and v not in (None, "")), None)
            data = lk.get("data", lk.get("payload"))
            if isinstance(data, str) and "codec" in lk:
                d = decode_payload(lk.get("codec"), data, key)
                if d and ANS_RE_T.search(d):
                    hits += ANS_RE_T.findall(d)
                    continue
            for v in row.values():
                cells += 1
                if cells > _LS_MAX_CELLS or time.time() > deadline:
                    break
                if isinstance(v, (bytes, bytearray, memoryview)):
                    v = bytes(v).decode("utf-8", "replace")
                if not isinstance(v, str):
                    continue
                m = ANS_RE_T.findall(v)
                if m:
                    hits += m
                    continue
                s = v.strip()
                if budget > 0 and 16 <= len(s) <= _CHAIN_MAX_IN:
                    budget -= 1
                    d = decode_any(s, key, chain=True, chain_s=0.05)
                    if d:
                        hits += ANS_RE_T.findall(d)
    except Exception:  # noqa: BLE001 - truncated / impostor store: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- Unity IL2CPP global-metadata.dat string literals (coverage atlas row 56) ------------------------------------------
_IL2_MAGIC = b"\xaf\x1b\xb1\xfa"  # 0xFAB11BAF little-endian
_IL2_MAX_ENTRY = 64 << 20
_IL2_MAX_LITS, _IL2_DECODE_BUDGET = 200_000, 400
_IL2_RUN = re.compile(rb"[\x20-\x7e]{16,4096}")


def _il2_unxor(b):
    """The metadata bytes, plain or under a single-byte xor (a cheap 'encrypted metadata' trick), or None."""
    if len(b) < 32:
        return None
    k = b[0] ^ _IL2_MAGIC[0]
    if bytes(x ^ k for x in b[:4]) != _IL2_MAGIC:
        return None
    return b if not k else bytes(x ^ k for x in b)


def il2cpp_literals(b):
    """C# string literals (`ldstr` constants) of a Unity IL2CPP global-metadata.dat: header magic 0xFAB11BAF + version,
    then the stringLiteral table ({uint32 length, int32 dataIndex}, or dataIndex only) indexing stringLiteralData.
    Header layout v16-v31 = (offset, size) pairs at 8 / 16; v38+ = (offset, size, count) sections at 8 / 20. When
    neither layout validates (unknown version), printable runs of the file stand in. [] when not IL2CPP metadata."""
    b = _il2_unxor(b)
    if b is None:
        return []
    n = len(b)
    ver = struct.unpack_from("<i", b, 4)[0]
    if not 16 <= ver <= 64:
        return []
    for step in ((12, 8) if ver >= 38 else (8, 12)):
        if 8 + 2 * step > n:
            continue
        lo, ls = struct.unpack_from("<ii", b, 8)
        do, ds = struct.unpack_from("<ii", b, 8 + step)
        cnt = struct.unpack_from("<i", b, 16)[0] if step == 12 else 0
        if not (0 < lo and 0 <= ls and lo + ls <= n and 0 < do and 0 <= ds and do + ds <= n):
            continue
        es = ls // cnt if cnt > 0 and ls % cnt == 0 else 8
        if es not in (4, 8) or ls % es or ls // es > _IL2_MAX_LITS:
            continue
        rows = [struct.unpack_from("<Ii" if es == 8 else "<i", b, lo + i * es) for i in range(ls // es)]
        if es == 4:  # dataIndex only: each literal runs to the next one's start
            idx = [r[0] for r in rows] + [ds]
            rows = [(idx[i + 1] - idx[i], idx[i]) for i in range(len(rows))]
        if not all(0 <= di and 0 <= ln and di + ln <= ds for ln, di in rows):
            continue
        return [b[do + di:do + di + ln].decode("utf-8", "replace") for ln, di in rows]
    return [m.group(0).decode("latin-1") for m in _IL2_RUN.finditer(b[:_IL2_MAX_ENTRY])]


def il2cpp_literal_scan(apk):
    """ANS tokens among the C# string literals of a Unity IL2CPP build (any entry starting with the global-metadata.dat
    magic, usually assets/bin/Data/Managed/Metadata/global-metadata.dat; a bare metadata file works too). Each literal
    is read directly, as a huntress_puzzle-style json ({codec, data|payload, key}), then through decode_any -- unkeyed,
    then keyed by a short neighbouring literal (a `const string key` sits next to its ciphertext in source order).
    [] when absent; never raises."""
    hits, lits = [], []
    deadline = time.time() + 1.0
    try:
        try:
            with zipfile.ZipFile(apk) as z:
                for info in z.infolist():
                    if info.is_dir() or info.file_size > _IL2_MAX_ENTRY or time.time() > deadline:
                        continue
                    try:
                        with z.open(info) as f:
                            if _il2_unxor(f.read(32)) is None:
                                continue
                        lits += il2cpp_literals(z.read(info))
                    except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError):
                        continue
        except zipfile.BadZipFile:  # a bare global-metadata.dat handed out on its own
            if hasattr(apk, "seek"):
                apk.seek(0)
                b = apk.read(_IL2_MAX_ENTRY)
            else:
                with Path(apk).open("rb") as f:
                    b = f.read(_IL2_MAX_ENTRY)
            lits = il2cpp_literals(b)
        for s in lits:
            hits += ANS_RE_T.findall(s)
        if hits:
            return list(dict.fromkeys(hits))
        budget = _IL2_DECODE_BUDGET
        for i, s in enumerate(lits):
            t = s.strip()
            if budget <= 0 or time.time() > deadline:
                break
            if t.startswith("{") and "codec" in t:
                try:
                    p = json.loads(t)
                    d = decode_payload(p.get("codec"), p.get("data", p.get("payload", "")), p.get("key"))
                    if d and ANS_RE_T.search(d):
                        hits += ANS_RE_T.findall(d)
                        continue
                except (ValueError, AttributeError, TypeError):
                    pass
            if not 16 <= len(t) <= _CHAIN_MAX_IN:
                continue
            budget -= 1
            d = decode_any(t, chain=True, chain_s=0.03)
            for j in (i - 1, i + 1):
                if d or not 0 <= j < len(lits) or not 1 <= len(lits[j].strip()) <= 32 or time.time() > deadline:
                    continue
                budget -= 1
                d = decode_any(t, lits[j].strip(), chain=True, chain_s=0.03)
            if d:
                hits += ANS_RE_T.findall(d)
    except Exception:  # noqa: BLE001 - truncated / impostor metadata: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- WebView / hybrid-app assets: html / js / json under assets/ (coverage atlas rows 13, 14, 57) ----------------------
_WV_EXT = re.compile(r"(?i)^assets/.*\.(?:html?|m?js|json|xhtml)$")
_WV_MAX_ENTRY = 4 << 20
_WV_MAX_TOTAL = 24 << 20
_WV_DECODE_BUDGET = 300
_WV_LIT = re.compile(r"""(["'`])((?:[^"'`\\\n]|\\.|(?!\1)["'`]){1,16384}?)\1""", re.S)
_WV_CONCAT = re.compile(r"""(?:(["'])(?:[^"'\\\n]|\\.)*?\1\s*\+\s*)+(["'])(?:[^"'\\\n]|\\.)*?\2""")
_WV_NUM = r"(?:0[xX][0-9a-fA-F]+|\d+)"
_WV_FCC = re.compile(r"fromCharCode\s*(?:\.apply\s*\(\s*\w*\s*,|\(\s*\.\.\.|\()\s*\[?\s*(" + _WV_NUM + r"(?:\s*,\s*" + _WV_NUM + r")*)")
_WV_ARR = re.compile(r"\[\s*(" + _WV_NUM + r"(?:\s*,\s*" + _WV_NUM + r"){7,4095})\s*,?\s*\]")
_WV_XKEY = re.compile(r"\^\s*(?:(" + _WV_NUM + r")\b|(?:\w+\.)?(\w+)\s*(?:\.charCodeAt|\[))")
_WV_ESC = re.compile(r"\\(?:x([0-9a-fA-F]{2})|u\{([0-9a-fA-F]{1,6})\}|u([0-9a-fA-F]{4})|([0-7]{1,3})|(.))", re.S)
_WV_SIMPLE = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}


def _wv_unescape(s):
    def sub(m):
        h = m.group(1) or m.group(2) or m.group(3)
        if h:
            return chr(min(int(h, 16), 0x10FFFF))
        if m.group(4):
            return chr(int(m.group(4), 8) & 0xFF)
        c = m.group(5)
        return "" if c == "\n" else _WV_SIMPLE.get(c, c)
    return _WV_ESC.sub(sub, s)


def _wv_nums(s):
    return [int(t, 0) for t in re.findall(_WV_NUM, s)]


def _wv_candidates(text):
    """(strings, keys) from one html/js/json asset: unescaped string literals (adjacent `"a" + "b"` concatenations
    joined), String.fromCharCode lists, numeric/hex byte arrays; keys = short literals and `^ <int>` / `^ name[...]`
    xor operands (a named key resolves to that variable's literal)."""
    lits, cands, keys = [], [], []
    for m in _WV_CONCAT.finditer(text):
        parts = [_wv_unescape(p.group(2)) for p in _WV_LIT.finditer(m.group(0))]
        cands.append("".join(parts))
    for m in _WV_LIT.finditer(text):
        if m.group(1) == "`" and "${" in m.group(2):
            continue
        lits.append(_wv_unescape(m.group(2)))
    for m in _WV_FCC.finditer(text):
        try:
            cands.append("".join(chr(n) for n in _wv_nums(m.group(1))))
        except (ValueError, OverflowError):
            pass
    for m in _WV_ARR.finditer(text):
        ns = _wv_nums(m.group(1))
        if all(n < 256 for n in ns):
            cands.append(bytes(ns))
        elif all(n < 0x110000 for n in ns):
            cands.append("".join(chr(n) for n in ns))
    named = {}
    for m in re.finditer(r"""\b(\w+)\s*[:=]\s*(["'`])((?:[^"'`\\\n]|\\.){1,64}?)\2""", text):
        named[m.group(1)] = _wv_unescape(m.group(3))
    for m in _WV_XKEY.finditer(text):
        k = int(m.group(1), 0) if m.group(1) else named.get(m.group(2))
        if k is not None and k not in keys:
            keys.append(k)
    keys += [s for s in lits if 1 <= len(s) <= 32 and s.strip() == s and s not in keys][:24]
    cands = cands + [s for s in lits if len(s) >= 16]
    return lits + cands, cands, keys


def webview_asset_scan(apk):
    """ANS tokens hidden in a WebView / Cordova / Capacitor / Flutter app's web assets (assets/**/*.html|js|json,
    incl. assets/www, assets/public, flutter_assets). Pure regex, no JS engine: each asset's string literals (JS
    escapes \\xHH / \\uHHHH / \\u{..} / octal undone, `"a"+"b"` joined), String.fromCharCode lists and numeric/hex byte
    arrays are scanned for a literal token, then run through decode_any -- unkeyed, then keyed by the file's `^ <int>`
    / `^ key[...]` xor operands and short literals. huntress_puzzle.json is puzzle_candidates' job and skipped.
    [] when absent; never raises."""
    hits, files = [], []
    deadline = time.time() + 0.9
    try:
        with zipfile.ZipFile(apk) as z:
            total = 0
            for info in z.infolist():
                n = info.filename
                if (info.is_dir() or not _WV_EXT.match(n) or n.endswith("huntress_puzzle.json")
                        or info.file_size > _WV_MAX_ENTRY or total + info.file_size > _WV_MAX_TOTAL):
                    continue
                try:
                    files.append(z.read(info).decode("utf-8", "replace"))
                    total += info.file_size
                except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError, NotImplementedError):
                    continue
        parsed = []
        for t in files:
            if time.time() > deadline:
                break
            strs, cands, keys = _wv_candidates(t)
            for s in strs:
                if isinstance(s, str):
                    hits += ANS_RE_T.findall(s)
            parsed.append((cands, keys))
        if hits:
            return list(dict.fromkeys(hits))
        budget = _WV_DECODE_BUDGET
        for cands, keys in parsed:
            for c in cands:
                if budget <= 0 or time.time() > deadline:
                    break
                b = c.encode("utf-8", "surrogatepass") if isinstance(c, str) else c
                if not 8 <= len(b) <= _CHAIN_MAX_IN:
                    continue
                budget -= 1
                d = decode_any(b, chain=True, chain_s=0.03)
                for k in keys:
                    if d or budget <= 0 or time.time() > deadline:
                        break
                    if k == c:
                        continue
                    budget -= 1
                    d = decode_any(b, k, depth=2, chain=False)
                if d:
                    hits += ANS_RE_T.findall(d)
    except Exception:  # noqa: BLE001 - not a zip / malformed asset: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- static-key AES/DES/3DES (coverage atlas row 33: SecretKeySpec + const key, ciphertext in an asset / the json) -----
_SKC_KEYISH = re.compile(r"key|secret|pass|pwd|seed", re.I)
_SKC_IVISH = re.compile(r"\biv\b|^iv|nonce|vector|^iv_|_iv$", re.I)
_SKC_MAX_STRS, _SKC_MAX_CTS, _SKC_MAX_IVS, _SKC_CT_CAP, _SKC_MAX_POOL = 32, 8, 8, 4096, 20_000
_SKC_BAD = re.compile(r"[\s/;()<>\[\]]|^L.*;$|^\W*$")


def _skc_blobs(s):
    """Bytes a text field can stand for: base64 / urlsafe / hex (the raw text never; it is not ciphertext)."""
    b = s.encode("latin-1", "replace") if isinstance(s, str) else s
    out = []
    for fn in (_b64ish, lambda x: _b64ish(x, True),
               lambda x: binascii.unhexlify(x.strip()) if re.fullmatch(rb"(?:[0-9a-fA-F]{2})+", x.strip()) else None):
        try:
            r = fn(b)
        except Exception:  # noqa: BLE001 - not this encoding
            r = None
        if r and r not in out:
            out.append(r)
    return out


def _skc_keys(s):
    """Key bytes a constant string can stand for: raw / hex / base64 of a valid length, sha256 (16/32), md5, sha1[:16],
    and Arrays.copyOf(s.getBytes(), 16)."""
    import hashlib
    sb = s.encode("utf-8", "replace")
    out = [sb] + [r for r in _skc_blobs(sb) if len(r) in (8, 16, 24, 32)]
    h = hashlib.sha256(sb).digest()
    out += [h[:16], h, hashlib.md5(sb).digest(), hashlib.sha1(sb).digest()[:16]]
    if len(sb) not in (8, 16, 24, 32) and 4 <= len(sb) < 32:
        out.append(sb[:16].ljust(16, b"\0"))
    return [k for k in dict.fromkeys(out) if len(k) in (8, 16, 24, 32)]


_SKC_POOL = re.compile(rb"([\x04-\x40])([\x21-\x7e]{4,64})\0")
_SKC_HEXK = re.compile(r"[0-9a-fA-F]{32}|[0-9a-fA-F]{48}|[0-9a-fA-F]{64}")
_SKC_MIX = re.compile(r"\d.*[A-Za-z]|[A-Za-z].*\d")
_SKC_PUNCT = re.compile(r"[^A-Za-z0-9_$]")
_SKC_WORD = re.compile(r"[a-z][A-Za-z]*|[A-Z][A-Za-z]*|[A-Z_]+|[a-z_]+|<.*>|\$.*|[\w$]+(?:\.[\w$]+)+")


def _skc_dex_strs(d):
    """Printable string-pool entries of one dex that could be a key constant (4-64 chars, not a type/path/message): one
    C-speed regex over the dex for `uleb len, chars, NUL` records whose length byte matches (a stray hit is only one more
    candidate key)."""
    if d[:4] != b"dex\n" or len(d) < 0x70:
        return []
    out = []
    for m in _SKC_POOL.finditer(d, 0x70):
        if m.group(1)[0] == len(m.group(2)):
            t = m.group(2).decode()
            if not _SKC_BAD.search(t) and (len(t) in (8, 16, 24, 32, 48, 64) or not _SKC_WORD.fullmatch(t)):
                out.append(t)
                if len(out) >= _SKC_MAX_POOL:
                    break
    return out


def _skc_rank(t):
    n = len(t)
    sc = 2 * (n in (8, 16, 24, 32)) + 3 * (n in (32, 48, 64) and bool(_SKC_HEXK.fullmatch(t)))
    sc += bool(_SKC_MIX.search(t)) + bool(_SKC_PUNCT.search(t)) - 3 * bool(_SKC_WORD.fullmatch(t))
    return -sc


def _xor_int(a, b):
    n = min(len(a), len(b))
    return (int.from_bytes(a[:n], "big") ^ int.from_bytes(b[:n], "big")).to_bytes(n, "big")


def static_key_cipher_scan(apk, seeds=None, raw_keys=()):
    """ANS tokens from a payload encrypted with a hardcoded key: ciphertext = a base64/hex field of any asset json
    (`data` / `payload` / ... first) or an asset file (base64/hex text or raw bytes) or a long base64/hex dex string;
    keys = json key-ish fields, then dex string-pool constants ranked key-like (<= 32 strings), each as raw / hex / b64 /
    sha256 / md5 / sha1 bytes. Tries AES (16/24/32), DES (8), 3DES (16/24) in ECB, CBC (IV zero / json iv / key /
    ct prefix), CTR and GCM (tag ignored; nonce json / zero / ct prefix). The answer regex is the oracle. [] when absent;
    never raises. `seeds` (identity_key_scan): try only these key strings instead of the json / dex constants; `raw_keys`
    (integrity_key_scan): key bytes tried first, as they are."""
    from Crypto.Cipher import AES, DES, DES3
    hits, cts, jkeys, ivs, dstrs = [], [], [], [], []
    try:
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                n = info.filename
                if info.is_dir() or info.file_size > _NEST_MAX_ENTRY:
                    continue
                if re.fullmatch(r"classes\d*\.dex", n):
                    dstrs += _skc_dex_strs(z.read(info))
                    continue
                if not n.startswith(("assets/", "res/raw/")) or info.file_size > 1 << 20:
                    continue
                b = z.read(info)
                if n.endswith(".json"):
                    try:
                        stack, pri, rest = [(None, json.loads(b))], [], []
                    except ValueError:
                        stack, pri, rest = [], [], []
                    while stack:
                        k, v = stack.pop()
                        if isinstance(v, dict):
                            stack += list(v.items())[::-1]
                        elif isinstance(v, list):
                            stack += [(k, x) for x in v[::-1]]
                        elif isinstance(v, str) and v:
                            k = str(k or "")
                            if _SKC_IVISH.search(k):
                                ivs += [v.encode()] + _skc_blobs(v)
                            elif _SKC_KEYISH.search(k):
                                jkeys.append(v)
                            elif len(v) >= 12:
                                (pri if re.search(r"data|payload|cipher|ct|enc|blob|value", k, re.I) else rest).append(v)
                    cts += [r for v in pri + rest for r in _skc_blobs(v) if len(r) >= 8]
                elif b and info.file_size <= 64 << 10:
                    cts += _skc_blobs(b) or ([b] if len(b) >= 16 else [])
        cts += [r for t in dstrs if len(t) >= 24 for r in _skc_blobs(t) if len(r) >= 16]
        cts = [c[:_SKC_CT_CAP] for c in dict.fromkeys(cts)][:_SKC_MAX_CTS]
        if not cts:
            return []
        strs = list(dict.fromkeys(jkeys + sorted(dict.fromkeys(dstrs), key=_skc_rank)))[:_SKC_MAX_STRS] if seeds is None else list(seeds)
        keys = list(dict.fromkeys([k for k in raw_keys if len(k) in (8, 16, 24, 32)] + [k for s in strs for k in _skc_keys(s)]))
        jivs = list(dict.fromkeys(v for v in ivs if len(v) >= 12))[:4]  # CTR / GCM: json IVs only (a cipher each)
        ivs = list(dict.fromkeys(ivs + [k for k in keys if len(k) in (8, 12, 16)]))[:_SKC_MAX_IVS]

        def hit(p):
            for m in ANS_RE_B.findall(p):
                t = m.decode()
                if t not in hits:
                    hits.append(t)

        for k in keys:
            ciphers = []
            if len(k) in (16, 24, 32):
                ciphers.append((AES, 16))
            if len(k) == 8:
                ciphers.append((DES, 8))
            if len(k) in (16, 24):
                try:
                    DES3.adjust_key_parity(k)
                    ciphers.append((DES3, 8))
                except ValueError:
                    pass
            for mod, bs in ciphers:
                ecb = mod.new(k, mod.MODE_ECB)
                for ct in cts:
                    body = ct[:len(ct) - len(ct) % bs]
                    if len(body) >= bs:
                        d = ecb.decrypt(body)
                        hit(d)  # ECB
                        tail = _xor_int(d[bs:], body[:-bs])
                        hit(tail)  # CBC from block 2 on (any IV); also IV = the ct prefix
                        for iv in [bytes(bs)] + [v[:bs] for v in ivs if len(v) >= bs]:
                            hit(_xor_int(d[:bs], iv) + tail)
                    if mod is not AES:
                        continue
                    ct = ct[:1024]
                    for iv, c in [(bytes(16), ct), (ct[:16], ct[16:])] + [(v[:16], ct) for v in jivs if len(v) >= 16]:
                        if c:
                            hit(AES.new(k, AES.MODE_CTR, nonce=b"", initial_value=iv).decrypt(c))
                    for nc, c in [(bytes(12), ct), (ct[:12], ct[12:])] + [(v[:12], ct) for v in jivs]:
                        if c:  # GCM keystream = CTR from nonce || 2 (96-bit nonce); tag left unverified
                            hit(AES.new(k, AES.MODE_CTR, nonce=b"", initial_value=nc + b"\0\0\0\2").decrypt(c))
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return hits


# --- identity-derived keys (coverage atlas rows 32, 33): key = client secret / case ref / package / day, raw or hashed --
_IDK_DEX = re.compile(rb"SECRET-[0-9A-Za-z_\-]{6,64}|MOB-\d{1,3}-[0-9A-Fa-f]{6,16}|[a-z]\w*(?:\.\w+){2,8}\.v[0-9a-f]{12}")
_IDK_PKG = re.compile(r"[a-z]\w*(?:\.[A-Za-z_]\w*){2,8}")
_IDK_SYS = ("android.", "androidx.", "com.android.", "com.google.", "java.", "kotlin.")
_IDK_MAX_SEEDS, _IDK_MAX_PAYLOADS, _IDK_BUDGET_S = 12, 6, 0.8


def _idk_seeds(z):
    """Identity strings an app could derive its key from, most specific first: client secret (SECRET-...), case ref
    (MOB-NN-<hex>), package name (dex / manifest string pool) with its v<12hex> suffix, then the day number (puzzle json
    `day`, package dNN, case ref NN) -- plus the payload strings of the asset jsons."""
    found, pkgs, days, payloads = [], [], [], []
    for info in z.infolist():
        n = info.filename
        if info.is_dir() or info.file_size > _NEST_MAX_ENTRY:
            continue
        if re.fullmatch(r"classes\d*\.dex", n):
            found += [m.decode() for m in _IDK_DEX.findall(z.read(info))]
        elif n == "AndroidManifest.xml":
            b = z.read(info)
            if b[:2] == b"\x03\x00":
                pkgs += [t for t in _pool_strings(b)[:400] if _IDK_PKG.fullmatch(t) and not t.startswith(_IDK_SYS)][:2]
        elif n.startswith("assets/") and n.endswith(".json") and info.file_size <= 1 << 20:
            try:
                stack = [(None, json.loads(z.read(info)))]
            except ValueError:
                continue
            while stack:
                k, v = stack.pop()
                if isinstance(v, dict):
                    stack += list(v.items())[::-1]
                elif isinstance(v, list):
                    stack += [(k, x) for x in v[::-1]]
                elif str(k).lower() == "day" and isinstance(v, (int, str)) and str(v).isdigit():
                    days.append(int(v))
                elif isinstance(v, str) and len(v) >= 12:
                    payloads.append(v)
    seeds = [s for s in found if s.startswith("SECRET-")] + [s for s in found if s.startswith("MOB-")]
    for p in [s for s in found if "." in s] + pkgs:
        seeds += [p, p.rsplit(".", 1)[-1]] + ([p[-12:]] if re.search(r"\.v[0-9a-f]{12}$", p) else [])
        m = re.search(r"\.d(\d{1,2})\.", p)
        days += [int(m.group(1))] if m else []
    days += [int(s.split("-")[1]) for s in found if s.startswith("MOB-")]
    seeds = list(dict.fromkeys(seeds))[:_IDK_MAX_SEEDS]
    seeds += list(dict.fromkeys(x for d in days for x in (str(d), "%02d" % d)))[:2]
    return seeds, list(dict.fromkeys(payloads))[:_IDK_MAX_PAYLOADS]


def identity_key_scan(apk):
    """ANS tokens from a payload keyed by the app's own identity (rows 32-33: "predictable crypto"): each seed of
    _idk_seeds() raw, and its md5 / sha1 / sha256 as digest bytes and as hex text, as the decode_any key (xor / add / shift
    after base64 / hex ...) of every asset-json payload, then as AES/DES keys via static_key_cipher_scan(seeds=...). [] when
    absent; never raises."""
    import hashlib
    hits = []
    try:
        with zipfile.ZipFile(apk) as z:
            seeds, payloads = _idk_seeds(z)
        if not seeds:
            return []
        keys, texts = [], []
        for s in seeds:
            sb = s.encode()
            keys.append(s)
            for h in (hashlib.md5(sb), hashlib.sha1(sb), hashlib.sha256(sb)):
                keys += [h.digest(), h.hexdigest()]
                texts += [h.hexdigest()[:32], h.hexdigest()[:16]]
        end = time.time() + _IDK_BUDGET_S
        for data in payloads:
            for k in keys:
                if time.time() > end:
                    break
                d = decode_any(data, key=k, depth=2, cap=300, chain=False)
                if d:
                    hits += [t for t in ANS_RE_T.findall(d) if t not in hits]
            if hits:
                return hits
        hits += static_key_cipher_scan(apk, seeds=list(dict.fromkeys(seeds + texts)))
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- signing certificate facts (coverage atlas rows 9 / 49 / 59: app-links fingerprint, integrity check, cert fields) ---
_SIG_V1 = re.compile(r"META-INF/[^/]+\.(RSA|DSA|EC)$", re.I)
_SIG_BLOCK_IDS = {0x7109871A: "v2", 0xF05368C0: "v3", 0x1B93AD61: "v3.1"}
_SIG_MAX_CERTS, _SIG_BUDGET_S = 8, 0.8
_SIG_DN_SHORT = {"common_name": "CN", "organization_name": "O", "organizational_unit_name": "OU", "country_name": "C",
                 "locality_name": "L", "state_or_province_name": "ST", "email_address": "EMAILADDRESS",
                 "street_address": "STREET", "domain_component": "DC", "serial_number": "SERIALNUMBER"}


def _sig_lp(b, i):
    """One uint32-length-prefixed item of the APK Signing Block at b[i:] -> (item, next offset); raises on overrun."""
    n = struct.unpack_from("<I", b, i)[0]
    if i + 4 + n > len(b):
        raise ValueError("lp overrun")
    return b[i + 4:i + 4 + n], i + 4 + n


def _sig_block_certs(z):
    """DER certificates of the v2 / v3 / v3.1 signers in the APK Signing Block ("APK Sig Block 42" just before the
    central directory), read through the ZipFile's own file handle. [(scheme, der)]; raises on a malformed block."""
    fp, cd = z.fp, z.start_dir
    if cd < 32:
        return []
    fp.seek(cd - 24)
    tail = fp.read(24)
    if tail[8:] != b"APK Sig Block 42":
        return []
    size = struct.unpack_from("<Q", tail)[0]
    if not 24 <= size <= min(cd - 8, 8 << 20):
        return []
    fp.seek(cd - size - 8)
    blk = fp.read(size + 8)
    out, i, end = [], 8, len(blk) - 24
    while i + 12 <= end:
        n, pid = struct.unpack_from("<QI", blk, i)
        if n < 4 or i + 8 + n > end:
            break
        scheme = _SIG_BLOCK_IDS.get(pid)
        if scheme:
            seq, _ = _sig_lp(blk[i + 12:i + 8 + n], 0)
            j = 0
            while j < len(seq) and len(out) < _SIG_MAX_CERTS:
                signer, j = _sig_lp(seq, j)
                sd, _ = _sig_lp(signer, 0)
                _digests, k = _sig_lp(sd, 0)
                certs, _ = _sig_lp(sd, k)
                c = 0
                while c < len(certs) and len(out) < _SIG_MAX_CERTS:
                    der, c = _sig_lp(certs, c)
                    out.append((scheme, der))
        i += 8 + n
    return out


# Non-signature id-value pairs of the block (coverage atlas rows 59 / 62): Walle 0x71777777 / VasDolly 0x881155ff channel
# ids and any custom id. The signature, padding, source-stamp and Play metadata pairs are skipped.
_SIG_BLOCK_SKIP = frozenset((0x7109871A, 0xF05368C0, 0x1B93AD61, 0x42726577, 0x6DFF800D, 0x504B4453, 0x2146444E))
_SIG_PAIR_MAX, _SIG_PAIR_DECODE_MAX = 64, 64 << 10
_SIG_PAIR_TEXT = re.compile(r"[\x20-\x7e\t\r\n]{8,}")


def signing_block_pairs(apk):
    """[(id, value bytes)] of the APK Signing Block's pairs other than v2 / v3 / v3.1 signatures, padding, source stamp
    and Play dependency / frosting metadata, walked from the EOCD central-directory offset back to "APK Sig Block 42".
    [] when absent; never raises."""
    out = []
    try:
        with zipfile.ZipFile(apk) as z:
            fp, cd = z.fp, z.start_dir
            if cd < 32:
                return []
            fp.seek(cd - 24)
            tail = fp.read(24)
            if tail[8:] != b"APK Sig Block 42":
                return []
            size = struct.unpack_from("<Q", tail)[0]
            if not 24 <= size <= min(cd - 8, 32 << 20):
                return []
            fp.seek(cd - size - 8)
            blk = fp.read(size + 8)
        i, end = 8, len(blk) - 24
        while i + 12 <= end and len(out) < _SIG_PAIR_MAX:
            n, pid = struct.unpack_from("<QI", blk, i)
            if n < 4 or i + 8 + n > end:
                break
            if pid not in _SIG_BLOCK_SKIP:
                out.append((pid, blk[i + 12:i + 8 + n]))
            i += 8 + n
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        return out
    return out


def signing_block_scan(apk):
    """ANS tokens in the APK Signing Block's non-signature pairs (signing_block_pairs): a literal ASCII / UTF-16LE token
    in the value, else each printable value -- or each string leaf of a JSON value (Walle's {"channel": ...}) --
    through decode_any. [] when absent; never raises."""
    hits = []
    try:
        pairs = signing_block_pairs(apk)
        for _pid, v in pairs:
            hits += [m.decode() for m in ANS_RE_B.findall(v)] + [m.decode("utf-16-le") for m in ANS_RE_U16.findall(v)]
        if hits:
            return list(dict.fromkeys(hits))
        end = time.time() + _SIG_BUDGET_S
        for _pid, v in pairs:
            if len(v) > _SIG_PAIR_DECODE_MAX:
                continue
            t = v.decode("utf-16-le", "replace") if v[1:16:2] == bytes(len(v[1:16:2])) and len(v) >= 16 else \
                v.decode("latin-1")
            try:
                j = json.loads(t)
                leaves, stack = [], [j]
                while stack and len(leaves) < 64:
                    x = stack.pop()
                    if isinstance(x, dict):
                        stack += list(x.values())
                    elif isinstance(x, list):
                        stack += x
                    elif isinstance(x, str):
                        leaves.append(x)
            except ValueError:
                leaves = [t]
            for s in leaves:
                for r in _SIG_PAIR_TEXT.findall(s)[:16]:
                    if time.time() > end:
                        return list(dict.fromkeys(hits))
                    d = decode_any(r.strip(), depth=2, cap=600, chain=False)
                    hits += ANS_RE_T.findall(d or "")
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


def signing_certs(apk):
    """Signer certificates of an APK, v1 (META-INF/*.RSA|DSA|EC PKCS#7) and v2/v3 (APK Signing Block), deduplicated:
    [{"scheme", "subject", "issuer" ("C=US, O=..., CN=..." as apksigner prints them), "subject_fields" / "issuer_fields"
    ({attr: value}), "serial" (hex), "not_before", "not_after", "sha256" / "sha1" / "md5" (lower hex of the DER),
    "sha256_colon" (assetlinks.json / apksigner style "AB:CD:..."), "der" (bytes)}]. [] when absent; never raises."""
    import hashlib
    from asn1crypto import cms, x509
    ders = []
    try:
        with zipfile.ZipFile(apk) as z:
            try:
                ders += _sig_block_certs(z)
            except (ValueError, struct.error, OSError):
                pass
            for info in z.infolist():
                if _SIG_V1.match(info.filename) and info.file_size <= 1 << 20 and len(ders) < 2 * _SIG_MAX_CERTS:
                    try:
                        sd = cms.ContentInfo.load(z.read(info))["content"]
                        ders += [("v1", c.chosen.dump()) for c in (sd["certificates"] or [])
                                 if c.name == "certificate"][:_SIG_MAX_CERTS]
                    except Exception:  # noqa: BLE001 - impostor / truncated PKCS#7
                        continue
    except Exception:  # noqa: BLE001 - not a zip
        return []
    out, seen = [], {}
    for scheme, der in ders:
        if der in seen:
            seen[der]["scheme"] += "+" + scheme if scheme not in seen[der]["scheme"].split("+") else ""
            continue
        try:
            c = x509.Certificate.load(der)
            tbs = c["tbs_certificate"]

            def dn(name):
                fields = {}
                for rdn in name.chosen:
                    for atv in rdn:
                        v, t = atv["value"].native, str(atv["type"].native)
                        fields[_SIG_DN_SHORT.get(t, t)] = v if isinstance(v, str) else str(v)
                return fields
            subj, iss = dn(tbs["subject"]), dn(tbs["issuer"])
            h = hashlib.sha256(der).hexdigest()
            rec = {"scheme": scheme, "subject": ", ".join(f"{k}={v}" for k, v in list(subj.items())[::-1]),
                   "issuer": ", ".join(f"{k}={v}" for k, v in list(iss.items())[::-1]), "subject_fields": subj,
                   "issuer_fields": iss, "serial": "%x" % tbs["serial_number"].native,
                   "not_before": str(tbs["validity"]["not_before"].native),
                   "not_after": str(tbs["validity"]["not_after"].native),
                   "sha256": h, "sha1": hashlib.sha1(der).hexdigest(), "md5": hashlib.md5(der).hexdigest(),
                   "sha256_colon": ":".join(h[i:i + 2] for i in range(0, 64, 2)).upper(), "der": der}
        except Exception:  # noqa: BLE001 - not a certificate
            continue
        seen[der] = rec
        out.append(rec)
    return out


def signing_cert_scan(apk):
    """ANS tokens hidden in / keyed by the APK's signing certificate (rows 9 / 49 / 59): every subject / issuer DN value
    and the serial (hex / decimal) of each v1 / v2 / v3 signer cert, plain or through decode_any; then each asset-json
    payload decoded with the cert digest (sha256 / sha1 / md5 as bytes, lower / upper / colon hex) as the decode_any key,
    and those digest strings as AES/DES key seeds (static_key_cipher_scan). [] when absent; never raises."""
    hits = []
    try:
        certs = signing_certs(apk)
        if not certs:
            return []
        end = time.time() + _SIG_BUDGET_S
        for c in certs:
            vals = list(c["subject_fields"].values()) + list(c["issuer_fields"].values())
            vals += [c["serial"], str(int(c["serial"], 16))]
            for v in dict.fromkeys(vals):
                if time.time() > end:
                    break
                hits += [t for t in ANS_RE_T.findall(v) if t not in hits]
                if not hits and len(v) >= 12:
                    d = decode_any(v, depth=2, cap=600, chain=False)
                    hits += [t for t in ANS_RE_T.findall(d or "") if t not in hits]
        if hits:
            return hits
        with zipfile.ZipFile(apk) as z:
            payloads = _idk_seeds(z)[1]
        keys, seeds = [], []
        for c in certs:
            for h in ("sha256", "sha1", "md5"):
                keys += [bytes.fromhex(c[h]), c[h], c[h].upper()]
            keys.append(c["sha256_colon"])
            seeds += [c["sha256"], c["sha256"].upper(), c["sha256_colon"], c["sha1"], c["md5"]]
        for data in payloads:
            if ANS_RE_T.search(decode_any(data, depth=2, cap=300, chain=False) or ""):
                continue    # keyless reading already answers: the puzzle path's, not a cert-keyed payload
            for k in keys:
                if time.time() > end:
                    break
                d = decode_any(data, key=k, depth=2, cap=300, chain=False)
                hits += [t for t in ANS_RE_T.findall(d or "") if t not in hits]
            if hits:
                return hits
        if payloads:
            hits += static_key_cipher_scan(apk, seeds=list(dict.fromkeys(seeds)))
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- integrity-derived keys (coverage atlas rows 49 / 33: anti-tamper key = cert digest / dex header / entry CRC32) ----
_IKD_CRC = re.compile(r"classes\d*\.dex|AndroidManifest\.xml|resources\.arsc|lib/[^/]+/[^/]+\.so")
_IKD_MAX_FACTS, _IKD_BUDGET_S = 16, 0.8


def _java_hash(s):
    """String.hashCode() (over UTF-16 code units) as an unsigned 32-bit int."""
    h, b = 0, s.encode("utf-16-be")
    for i in range(0, len(b), 2):
        h = (31 * h + (b[i] << 8 | b[i + 1])) & 0xFFFFFFFF
    return h


def integrity_facts(apk):
    """The APK's own integrity values an anti-tamper check could key on, as (label, bytes): signer cert sha256 / sha1 /
    md5 of the DER (raw sha256 / sha1 of META-INF/*.RSA|DSA|EC when no cert parses), each dex's header adler32 checksum
    (file order, LE) and sha1 signature plus the sha256 / md5 of the whole dex, the zip CRC32 (big-endian) of
    classes*.dex / manifest / resources.arsc / .so entries, and the package name's Java hashCode (BE). [] when absent;
    never raises."""
    import hashlib
    facts = []
    try:
        certs = signing_certs(apk)
        for c in certs[:2]:
            facts += [("cert_" + h, bytes.fromhex(c[h])) for h in ("sha256", "sha1", "md5")]
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                n = info.filename
                if info.is_dir() or info.file_size > _NEST_MAX_ENTRY:
                    continue
                if not certs and _SIG_V1.match(n) and info.file_size <= 1 << 20:
                    b = z.read(info)
                    facts += [("v1_sha256", hashlib.sha256(b).digest()), ("v1_sha1", hashlib.sha1(b).digest())]
                if re.fullmatch(r"classes\d*\.dex", n):
                    d = z.read(info)
                    if d[:4] == b"dex\n" and len(d) >= 0x70:
                        facts += [("dex_adler32", d[8:12]), ("dex_sha1", d[12:32]),
                                  ("dex_sha256", hashlib.sha256(d).digest()), ("dex_md5", hashlib.md5(d).digest())]
                if _IKD_CRC.fullmatch(n):
                    facts.append(("crc32:" + n, struct.pack(">I", info.CRC)))
                if n == "AndroidManifest.xml" and info.file_size <= 4 << 20:
                    b = z.read(info)
                    if b[:2] == b"\x03\x00":
                        pk = [t for t in _pool_strings(b)[:400] if _IDK_PKG.fullmatch(t) and not t.startswith(_IDK_SYS)]
                        facts += [("pkg_hashcode", struct.pack(">I", _java_hash(t))) for t in pk[:1]]
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        pass
    return list(dict.fromkeys(facts))[:_IKD_MAX_FACTS]


def _ikd_forms(v):
    """Key forms of one integrity value: bytes, first 16 bytes, lower / upper hex text; a 4-byte value also LE / BE swapped,
    unsigned / signed decimal and unpadded hex (Integer.toHexString / Long.toString of the CRC)."""
    h = v.hex()
    out = [v, h.encode(), h.upper().encode()] + ([v[:16], h[:32].encode(), h[:16].encode()] if len(v) > 16 else [])
    if len(v) == 4:
        u = int.from_bytes(v, "big")
        out += [v[::-1], b"%d" % u, b"%d" % (u - (1 << 32) if u >> 31 else u), b"%x" % u, b"%X" % u,
                b"%x" % int.from_bytes(v, "little"), b"%d" % int.from_bytes(v, "little")]
    return list(dict.fromkeys(out))


def integrity_key_scan(apk):
    """ANS tokens from a payload keyed by the APK's own integrity data (rows 49 / 33: anti-tamper decryption): every
    integrity_facts() value in each _ikd_forms() shape as the decode_any key (xor / add ... after base64 / hex) of every
    asset-json payload, then as AES/DES keys (raw bytes, first 16 bytes, hex text) via static_key_cipher_scan. Payloads
    that already decode keyless are skipped (the puzzle path owns them). [] when absent; never raises."""
    hits = []
    try:
        facts = integrity_facts(apk)
        if not facts:
            return []
        with zipfile.ZipFile(apk) as z:
            payloads = _idk_seeds(z)[1]
        keys = list(dict.fromkeys(k for _, v in facts for k in _ikd_forms(v)))
        end = time.time() + _IKD_BUDGET_S
        for data in payloads:
            if ANS_RE_T.search(decode_any(data, depth=2, cap=300, chain=False) or ""):
                continue
            for k in keys:
                if time.time() > end:
                    break
                d = decode_any(data, key=k, depth=2, cap=300, chain=False)
                hits += [t for t in ANS_RE_T.findall(d or "") if t not in hits]
            if hits:
                return hits
        raw = [x for _, v in facts for x in (v[:16], v[:32], v[:24])]
        seeds = [x.decode() for _, v in facts for x in _ikd_forms(v) if x.isascii() and len(x) >= 8]
        hits += static_key_cipher_scan(apk, seeds=list(dict.fromkeys(seeds)), raw_keys=list(dict.fromkeys(raw)))
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- in-dex integrity keys (coverage atlas: dex-bytecode-integrity-gate) ---------------------------------------------
# An anti-tamper gate reads its own classes.dex (getPackageCodePath + ZipFile) and keys the answer on a digest of it:
# Adler32 / CRC32 / SHA-1 / MD5 / SHA-256 of the whole dex, the recomputed header checksum / signature, or of one
# method's own code_item (header + insns, or insns only). Every such digest (_ikd_forms shapes) is tried as an xor / add
# / sub key by an "ANS-" known-plaintext prefix lookup (O(1) per key) and as an AES key (ECB / CBC IV 0 / CBC IV-prefix /
# CTR IV-prefix / GCM nonce-prefix, first block only) over asset payloads, dex base64 / hex literals and dex byte arrays.
_DBI_MAX_DEX, _DBI_MAX_METHODS, _DBI_BUDGET_S = 32 << 20, 4000, 0.8
_DBI_MAX_READINGS, _DBI_MAX_ASSET = 96, 64 << 10
_DBI_LIT = re.compile(rb"(?<![A-Za-z0-9+/=_-])(?:[A-Za-z0-9+/_-]{4}){5,96}(?:[A-Za-z0-9+/_-]{2}==|[A-Za-z0-9+/_-]{3}=)?"
                      rb"(?![A-Za-z0-9+/=_-])")
_DBI_LIB = ("Landroid/", "Landroidx/", "Lkotlin/", "Lkotlinx/", "Lcom/google/", "Ljava/", "Lj$/", "Lorg/intellij/")
_DBI_ANS = re.compile(rb"ANS-[0-9A-Fa-f]{16}")


def _dbi_code_items(d, cap):
    """[(code_item bytes, insns bytes)] of one dex's methods with code, app classes before library ones; [] when not a
    dex."""
    if d[:4] != b"dex\n" or len(d) < 0x70:
        return []
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_str, o_str, n_typ, o_typ, n_cls, o_cls = u32(0x38), u32(0x3C), u32(0x40), u32(0x44), u32(0x60), u32(0x64)
    if n_cls > 1 << 20 or o_cls + 32 * n_cls > len(d) or o_typ + 4 * n_typ > len(d) or o_str + 4 * n_str > len(d):
        return []

    def tname(ti):
        try:
            si = u32(o_typ + 4 * ti)
            _, p = _uleb(d, u32(o_str + 4 * si))
            return d[p:d.index(b"\0", p)].decode("utf-8", "replace")
        except (IndexError, ValueError, struct.error):
            return ""
    order = sorted(range(n_cls), key=lambda c: tname(u32(o_cls + 32 * c)).startswith(_DBI_LIB))
    out = []
    for c in order:
        cd = u32(o_cls + 32 * c + 24)
        if not cd or cd >= len(d):
            continue
        try:
            sf, i = _uleb(d, cd)
            inf, i = _uleb(d, i)
            dm, i = _uleb(d, i)
            vm, i = _uleb(d, i)
            for _ in range(sf + inf):
                i = _uleb(d, _uleb(d, i)[1])[1]
            for _ in range(dm + vm):
                _, i = _uleb(d, i)
                _, i = _uleb(d, i)
                co, i = _uleb(d, i)
                if co and co + 16 <= len(d):
                    n = u32(co + 12)
                    if co + 16 + 2 * n <= len(d):
                        out.append((d[co:co + 16 + 2 * n], d[co + 16:co + 16 + 2 * n]))
                if len(out) >= cap:
                    return out
        except (IndexError, ValueError, struct.error):
            continue
    return out


def _dbi_digests(b):
    return [struct.pack(">I", zlib.crc32(b)), struct.pack(">I", zlib.adler32(b)), hashlib.md5(b).digest(),
            hashlib.sha1(b).digest(), hashlib.sha256(b).digest()]


def _dbi_readings(s):
    """Byte readings of one payload (str or bytes): as-is, base64 (std / url), hex -- each >= 20 bytes."""
    b = s.encode("latin-1", "ignore") if isinstance(s, str) else bytes(s)
    out = [b]
    t = b.strip()
    if re.fullmatch(rb"(?:[0-9A-Fa-f]{2}){10,}", t):
        out.append(bytes.fromhex(t.decode()))
    elif re.fullmatch(rb"[A-Za-z0-9+/_-]{20,}={0,2}", t):
        for alt in (False, True):
            try:
                out.append(base64.b64decode(t + b"=" * (-len(t) % 4), altchars=b"-_" if alt else None, validate=True))
            except (binascii.Error, ValueError):
                pass
    return [x for x in dict.fromkeys(out) if 20 <= len(x) <= 4096]


def _dbi_payloads(z):
    """(asset payload strings / raw asset blobs, dex blobs) of one APK zip."""
    pays, dexes = [], []
    for info in z.infolist():
        n = info.filename
        if info.is_dir():
            continue
        if re.fullmatch(r"classes\d*\.dex", n) and info.file_size <= _DBI_MAX_DEX:
            dexes.append(z.read(info))
        elif n.startswith("assets/") and info.file_size <= _DBI_MAX_ASSET:
            b = z.read(info)
            try:
                stack = [json.loads(b)] if n.endswith(".json") else []
            except ValueError:
                stack = []
            if not stack:
                pays += [b] + [m.group(0) for m in itertools.islice(_DBI_LIT.finditer(b), 16)]
            while stack:
                v = stack.pop()
                if isinstance(v, dict):
                    stack += list(v.values())
                elif isinstance(v, list):
                    stack += v
                elif isinstance(v, str) and len(v) >= 20:
                    pays.append(v)
    return pays, dexes


def _dbi_try(readings, keys, deadline):
    """ANS tokens of readings under keys: xor / sub / add by prefix lookup, then AES first-block probes."""
    from Crypto.Cipher import AES
    want = b"ANS-"
    tabs = ({}, {}, {})  # key prefix needed for: p = c ^ k, p = c - k, p = c + k
    for r in readings:
        tabs[0].setdefault(bytes(c ^ p for c, p in zip(r, want)), []).append(r)
        tabs[1].setdefault(bytes((c - p) & 0xFF for c, p in zip(r, want)), []).append(r)
        tabs[2].setdefault(bytes((p - c) & 0xFF for c, p in zip(r, want)), []).append(r)
    ops = (lambda c, k: c ^ k, lambda c, k: (c - k) & 0xFF, lambda c, k: (c + k) & 0xFF)
    blk = [r for r in readings if len(r) >= 16]
    hits = []
    for k in keys:
        if time.time() > deadline:
            break
        for tab, op in zip(tabs, ops):
            for r in tab.get(bytes(k[i % len(k)] for i in range(4)), ()):
                m = _DBI_ANS.search(bytes(op(c, k[i % len(k)]) for i, c in enumerate(r[:64])))
                hits += [m.group(0).decode()] if m else []
        if len(k) not in (16, 24, 32) or not blk:
            continue
        ecb = AES.new(k, AES.MODE_ECB)
        x = lambda u, v: bytes(i ^ j for i, j in zip(u, v))  # noqa: E731
        for r in blk:
            tries = []
            if len(r) % 16 == 0 and ecb.decrypt(r[:16])[:4] == want:
                tries += [lambda r=r: AES.new(k, AES.MODE_ECB).decrypt(r),
                          lambda r=r: AES.new(k, AES.MODE_CBC, iv=bytes(16)).decrypt(r)]
            if len(r) >= 32 and len(r) % 16 == 0 and x(ecb.decrypt(r[16:32]), r)[:4] == want:
                tries.append(lambda r=r: AES.new(k, AES.MODE_CBC, iv=r[:16]).decrypt(r[16:]))
            if len(r) >= 36 and x(ecb.encrypt(r[:16]), r[16:20]) == want:
                tries.append(lambda r=r: AES.new(k, AES.MODE_CTR, nonce=b"", initial_value=r[:16]).decrypt(r[16:]))
            if len(r) >= 32 and x(ecb.encrypt(r[:12] + b"\0\0\0\2"), r[12:16]) == want:
                tries.append(lambda r=r: AES.new(k, AES.MODE_GCM, nonce=r[:12]).decrypt(r[12:]))
            for f in tries:
                m = _DBI_ANS.search(f())
                if m:
                    hits.append(m.group(0).decode())
                    break
    return hits


def dex_integrity_gate_scan(apk):
    """ANS tokens keyed by a digest of the APK's own dex bytes (anti-tamper gate reading classes.dex via
    getPackageCodePath + ZipFile): CRC32 / Adler32 / MD5 / SHA-1 / SHA-256 of each whole dex, of dex[12:] / dex[32:]
    (recomputed header checksum / signature), the stored header fields, and of every method's code_item (16-byte header
    + insns, and insns alone; app classes first) -- each in _ikd_forms() shapes as xor / add / sub key (repeating) and AES
    key over asset payloads (json strings, raw blobs), dex base64 / hex literals and dex byte arrays, confirmed by the
    "ANS-" known plaintext. Static only; [] when absent; never raises; bounded to ~0.8 s."""
    hits = []
    deadline = time.time() + _DBI_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            pays, dexes = _dbi_payloads(z)
        if not dexes:
            return []
        for d in dexes:
            pays += [m.group(0) for m in itertools.islice(_DBI_LIT.finditer(d), 64)]
            try:
                for arrs, _, _ in _dex_array_classes(d, [_DXA_UNITS], deadline):
                    pays += [bytes(v & 0xFF for v in a) for a in arrs if 20 <= len(a) <= 4096][:16]
            except Exception:  # noqa: BLE001 - malformed dex: no arrays
                pass
        readings = list(dict.fromkeys(r for p in pays for r in _dbi_readings(p)))[:_DBI_MAX_READINGS]
        readings = [r for r in readings if not _DBI_ANS.search(r)]  # plain tokens belong to the other scans
        if not readings:
            return []
        seen = set()

        def run(vals):
            keys = [k for v in vals for k in _ikd_forms(v) if k not in seen]
            seen.update(keys)
            return _dbi_try(readings, list(dict.fromkeys(keys)), deadline)
        for d in dexes:
            if d[:4] == b"dex\n" and len(d) >= 0x70:
                hits += run([d[8:12], d[12:32]] + _dbi_digests(d) + _dbi_digests(d[12:]) + _dbi_digests(d[32:]))
        for d in dexes:
            if hits or time.time() > deadline:
                break
            for ci, ins in _dbi_code_items(d, _DBI_MAX_METHODS):
                hits += run(_dbi_digests(ci) + _dbi_digests(ins))
                if hits or time.time() > deadline:
                    break
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- v1 (JAR) signature verification: MANIFEST.MF / .SF digests vs the actual bytes (coverage atlas rows 49, 59) ------
# An anti-tamper story ships a v1-signed APK, then patches one entry (or adds one) after signing: its digest no longer
# matches MANIFEST.MF (or it is not listed at all), and that entry is where the real answer hides. Pure Python: sections
# split on blank lines, 72-byte continuation lines (leading space) joined, every "<alg>-Digest" recomputed; the .SF's
# "<alg>-Digest-Manifest" / "-Main-Attributes" and per-section digests are checked against MANIFEST.MF's raw bytes.
_V1_ALG = {"SHA": "sha1", "SHA1": "sha1", "SHA224": "sha224", "SHA256": "sha256", "SHA384": "sha384",
           "SHA512": "sha512", "MD5": "md5"}
_V1_EOL = re.compile(rb"\r\n|\r|\n")
_V1_SIGFILE = re.compile(r"META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC)|SIG-[^/]*)$", re.I)
_V1_MAX_MF, _V1_MAX_ENTRY, _V1_BUDGET_S = 8 << 20, 32 << 20, 1.0


def _v1_sections(b):
    """[(raw section bytes incl. its terminating blank line, {attr: value})] of a manifest / .SF; continuation lines
    (leading space) are joined, attribute names keep their case (look them up case-insensitively)."""
    out, lines, start, pos = [], [], 0, 0
    while pos < len(b):
        m = _V1_EOL.search(b, pos)
        line, nxt = (b[pos:], len(b)) if m is None else (b[pos:m.start()], m.end())
        if line:
            if line[:1] == b" " and lines:
                lines[-1] += line[1:]
            else:
                lines.append(line)
        elif lines:
            out.append((b[start:nxt], lines))
            lines, start = [], nxt
        else:
            start = nxt
        pos = nxt
    if lines:
        out.append((b[start:], lines))
    res = []
    for raw, ls in out:
        attrs = {}
        for ln in ls:
            k, sep, v = ln.decode("utf-8", "replace").partition(":")
            if sep:
                attrs.setdefault(k.strip(), v.strip())
        res.append((raw, attrs))
    return res


def _v1_digests(attrs, suffix="-Digest"):
    """[(hashlib name, expected digest bytes)] of every '<alg><suffix>' attribute of one section."""
    out = []
    for k, v in attrs.items():
        if k.lower().endswith(suffix.lower()):
            alg = _V1_ALG.get(k[:-len(suffix)].upper().replace("-", ""))
            try:
                d = base64.b64decode(v, validate=True)
            except (binascii.Error, ValueError):
                continue
            if alg:
                out.append((alg, d))
    return out


def _v1_check(data, digs):
    import hashlib
    return all(hashlib.new(a, data).digest() == d for a, d in digs)


def v1_manifest_verify(apk):
    """JAR (v1) signature integrity of an APK, recomputed in pure Python. None when it is not a zip or has no
    META-INF/MANIFEST.MF; else {"listed": n Name: sections, "modified": [entries whose bytes no longer match their
    MANIFEST.MF digest], "unlisted": [non-signature entries absent from MANIFEST.MF], "missing": [listed, not in the
    zip], "unverified": [too large / unreadable], "sf": {"META-INF/X.SF": {"manifest_ok", "main_ok" (True / False /
    None = attribute absent), "section_mismatch": [names whose MANIFEST.MF section digest differs], "unlisted": [Name:
    sections of MANIFEST.MF the .SF lacks]}}, "tampered": modified + unlisted (modified first; "which file was
    modified"), "v1_certs" / "v2v3_certs": [signer cert sha256], "cert_mismatch": True when both schemes have certs and
    no v1 cert is a v2/v3 cert}. Never raises."""
    try:
        with zipfile.ZipFile(apk) as z:
            infos = z.infolist()
            mf_info = [i for i in infos if i.filename.upper() == "META-INF/MANIFEST.MF"]
            if not mf_info or mf_info[0].file_size > _V1_MAX_MF:
                return None
            mf = z.read(mf_info[0])
            secs = _v1_sections(mf)
            listed = {}
            for raw, attrs in secs[1:]:
                n = next((v for k, v in attrs.items() if k.lower() == "name"), None)
                if n is not None:
                    listed.setdefault(n, (raw, _v1_digests(attrs)))
            res = {"listed": len(listed), "modified": [], "unlisted": [], "missing": [], "unverified": [], "sf": {}}
            names, end = set(), time.time() + _V1_BUDGET_S
            for info in infos:
                n = info.filename
                if info.is_dir() or _V1_SIGFILE.fullmatch(n):
                    continue
                names.add(n)
                if n not in listed:
                    res["unlisted"] += [n] if n not in res["unlisted"] else []
                    continue
                digs = listed[n][1]
                if not digs or info.file_size > _V1_MAX_ENTRY or time.time() > end:
                    res["unverified"] += [n] if n not in res["unverified"] else []
                    continue
                try:
                    ok = _v1_check(z.read(info), digs)
                except (OSError, RuntimeError, zipfile.BadZipFile, zlib.error, NotImplementedError):
                    res["unverified"] += [n] if n not in res["unverified"] else []
                    continue
                if not ok and n not in res["modified"]:
                    res["modified"].append(n)
            res["missing"] = [n for n in listed if n not in names]
            main_raw = secs[0][0] if secs and not any(k.lower() == "name" for k in secs[0][1]) else b""
            for info in infos:
                if not re.fullmatch(r"META-INF/[^/]+\.SF", info.filename, re.I) or info.file_size > _V1_MAX_MF:
                    continue
                sf = _v1_sections(z.read(info))
                if not sf:
                    continue
                main = sf[0][1]
                dm = _v1_digests(main, "-Digest-Manifest")
                dma = _v1_digests(main, "-Digest-Manifest-Main-Attributes")
                rec = {"manifest_ok": _v1_check(mf, dm) if dm else None,
                       "main_ok": _v1_check(main_raw, dma) if dma and main_raw else None,
                       "section_mismatch": [], "unlisted": []}
                sf_names = set()
                for _raw, attrs in sf[1:]:
                    n = next((v for k, v in attrs.items() if k.lower() == "name"), None)
                    if n is None:
                        continue
                    sf_names.add(n)
                    digs = _v1_digests(attrs)
                    if n in listed and digs and not _v1_check(listed[n][0], digs):
                        rec["section_mismatch"].append(n)
                rec["unlisted"] = [n for n in listed if n not in sf_names] if rec["manifest_ok"] is not True else []
                res["sf"][info.filename] = rec
    except Exception:  # noqa: BLE001 - not a zip / truncated / impostor manifest
        return None
    sf_bad = [n for r in res["sf"].values() for n in r["section_mismatch"] + r["unlisted"]]
    res["tampered"] = list(dict.fromkeys(res["modified"] + [n for n in sf_bad if n in names] + res["unlisted"]))
    try:
        certs = signing_certs(apk)
    except Exception:  # noqa: BLE001
        certs = []
    res["v1_certs"] = [c["sha256"] for c in certs if "v1" in c["scheme"].split("+")]
    res["v2v3_certs"] = [c["sha256"] for c in certs if set(c["scheme"].split("+")) - {"v1"}]
    res["cert_mismatch"] = bool(res["v1_certs"] and res["v2v3_certs"]
                                and not set(res["v1_certs"]) & set(res["v2v3_certs"]))
    return res


def v1_tamper_scan(apk):
    """ANS tokens of the entries a v1 anti-tamper check would flag (v1_manifest_verify): bytes changed after signing
    first, then .SF-section mismatches, then entries added after signing (only when MANIFEST.MF lists most of the zip --
    a stub manifest is not a signature). Each entry is read like a zip anomaly blob (literal ASCII / UTF-16LE token,
    nested zip, puzzle json object, decode_any over its printable runs). [] when nothing is tampered; never raises."""
    hits = []
    try:
        r = v1_manifest_verify(apk)
        if not r or not r["listed"]:
            return []
        targets = [n for n in r["tampered"] if n not in r["unlisted"]]
        if len(r["unlisted"]) <= max(2, r["listed"] // 2):
            targets += r["unlisted"]
        if not targets:
            return []
        state = {"budget": _ZSA_DECODE_BUDGET, "end": time.time() + _ZSA_DEADLINE_S}
        with zipfile.ZipFile(apk) as z:
            by_name = {}
            for info in z.infolist():
                by_name.setdefault(info.filename, []).append(info)
            for n in targets[:32]:
                for info in by_name.get(n, [])[:4]:
                    if info.file_size > _ZSA_MAX_BLOB:
                        continue
                    try:
                        b = z.read(info)
                    except (OSError, RuntimeError, zipfile.BadZipFile, zlib.error, NotImplementedError):
                        continue
                    found = []
                    _zsa_blob(n, b, found, state, 1)
                    hits += [t for t in found if t not in hits]
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return hits


def _run(cmd, timeout=90):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None


@lru_cache(maxsize=16)
def jadx_sources_text(apk, timeout=120):
    """Decompile with jadx and return all decompiled source text (cached). Empty string if jadx fails."""
    out = Path(apk).resolve().parent / (".android-work/" + Path(apk).stem + "-jadx")
    out.mkdir(parents=True, exist_ok=True)
    if not any(out.rglob("*.java")):
        _run(["jadx", "-d", str(out), "--no-res", str(apk)], timeout=timeout)
    buf = []
    for j in out.rglob("*.java"):
        try:
            buf.append(j.read_text(errors="replace"))
        except OSError:
            continue
    return "\n".join(buf)


@lru_cache(maxsize=16)
def apktool_dir(apk, timeout=120):
    """Decode with apktool (manifest + resources + smali) and return the output dir, or None."""
    out = Path(apk).resolve().parent / (".android-work/" + Path(apk).stem + "-apktool")
    if not (out / "AndroidManifest.xml").exists():
        r = _run(["apktool", "d", "-f", "-o", str(out), str(apk)], timeout=timeout)
        if r is None or not (out / "AndroidManifest.xml").exists():
            return None
    return out


# --- certificate pinning: OkHttp `sha256/<b64>` pins in dex + NSC <pin-set> (coverage atlas rows 27, 28) ---------------
_PIN_DEX = re.compile(rb"(sha(?:256|1))/([A-Za-z0-9+/]{27,86}={0,2})")
_PIN_POOL = re.compile(rb"([\x04-\x7f])([\x21-\x7e]{4,127})\0")
_PIN_HOST = re.compile(r"(?:\*{1,2}\.)?[a-z0-9](?:[a-z0-9-]{0,62}\.)+[a-z][a-z0-9-]{1,62}", re.I)
_PIN_URL = re.compile(r"https?://([^/:?#\s]+)")
_PIN_NOTHOST = frozenset(("com", "org", "net", "io", "android", "androidx", "java", "javax", "kotlin", "kotlinx",
                          "okhttp3", "okio", "dalvik", "retrofit2", "sun", "libcore", "junit", "me", "de", "ch"))
_PIN_MAX_ENTRY = 32 << 20


def _pin_b64(v):
    """Raw digest bytes of a pin's base64 (std or url-safe, padding optional); None when not base64."""
    v = v.strip()
    try:
        return base64.b64decode(v + "=" * (-len(v) % 4), altchars=b"-_" if ("-" in v or "_" in v) else None,
                                validate=True)
    except (binascii.Error, ValueError):
        return None


def _pin_rec(algo, b64, source, hosts=()):
    raw = _pin_b64(b64)
    return {"pin": f"{algo.lower().replace('-', '')}/{b64}", "algo": algo.lower().replace("-", ""), "b64": b64,
            "hex": raw.hex() if raw is not None else None, "len": len(raw) if raw is not None else None,
            "source": source, "hosts": list(hosts)}


def _axml_events(b):
    """(kind, name, attrs, text) events of a binary AXML: ("start", tag, {attr: value}, None), ("end", tag, None, None),
    ("text", None, None, cdata). Attribute values are the raw string (or the typed int as str / "true"/"false")."""
    pool = None
    i = 8 if b[:2] == b"\x03\x00" else len(b)
    while i + 8 <= len(b):
        typ, hsz, size = struct.unpack_from("<HHI", b, i)
        if size < 8 or i + size > len(b):
            break
        if typ == 0x0001 and pool is None:
            pool = _pool_strings(b[i:i + size])
        elif pool is not None and typ in (0x0102, 0x0103, 0x0104):
            s = lambda k: pool[k] if 0 <= k < len(pool) else None  # noqa: E731
            e = i + hsz
            if typ == 0x0102:
                _ns, name, astart, asize, acount = struct.unpack_from("<IIHHH", b, e)
                attrs = {}
                for k in range(min(acount, 256)):
                    a = e + astart + k * max(asize, 20)
                    _ans, an, raw, _sz, _r0, dtype, data = struct.unpack_from("<IIIHBBI", b, a)
                    if raw != 0xFFFFFFFF:
                        v = s(raw)
                    elif dtype == 0x12:
                        v = "true" if data else "false"
                    elif dtype == 0x03:
                        v = s(data)
                    else:
                        v = str(data)
                    attrs[s(an) or str(an)] = v
                yield "start", s(name), attrs, None
            elif typ == 0x0103:
                yield "end", s(struct.unpack_from("<II", b, e)[1]), None, None
            else:
                yield "text", None, None, s(struct.unpack_from("<I", b, e)[0])
        i += size


def _xml_events(b):
    """Same events from a plaintext (uncompiled) XML file."""
    def walk(el):
        yield "start", el.tag.split("}")[-1], {k.split("}")[-1]: v for k, v in el.attrib.items()}, None
        if (el.text or "").strip():
            yield "text", None, None, el.text
        for c in el:
            yield from walk(c)
        yield "end", el.tag.split("}")[-1], None, None
    yield from walk(ET.fromstring(b))


def _nsc_parse(name, b):
    """Network-security-config facts of one res/xml file: [{"file", "kind" (domain-config / base-config /
    debug-overrides), "domains" [{"host", "includeSubdomains"}], "pins", "expiration", "cleartextTrafficPermitted",
    "trust_anchors"}]; [] when the file is not an NSC."""
    ev = _axml_events(b) if b[:2] == b"\x03\x00" else _xml_events(b) if b.lstrip()[:1] == b"<" else ()
    out, stack, cur, last = [], [], [], None
    for kind, tag, attrs, text in ev:
        if kind == "start":
            stack.append(tag)
            last = (tag, attrs)
            if tag in ("domain-config", "base-config", "debug-overrides"):
                cur.append({"file": name, "kind": tag, "domains": [], "pins": [], "expiration": None,
                            "cleartextTrafficPermitted": attrs.get("cleartextTrafficPermitted"), "trust_anchors": []})
                out.append(cur[-1])
            elif cur and tag == "pin-set":
                cur[-1]["expiration"] = attrs.get("expiration")
            elif cur and tag == "certificates":
                cur[-1]["trust_anchors"].append(attrs.get("src"))
        elif kind == "end":
            if stack:
                stack.pop()
            if tag in ("domain-config", "base-config", "debug-overrides") and cur:
                cur.pop()
            last = None
        elif kind == "text" and cur and last and (text or "").strip():
            tag, attrs = last
            if tag == "domain":
                cur[-1]["domains"].append({"host": text.strip(), "includeSubdomains": attrs.get("includeSubdomains")})
            elif tag == "pin":
                cur[-1]["pins"].append(_pin_rec(attrs.get("digest") or "SHA-256", text.strip(), name,
                                                [d["host"] for d in cur[-1]["domains"]]))
    return out


def cert_pins(apk):
    """Certificate-pinning facts of an APK (rows 27, 28): {"pins": [{"pin" ("sha256/<b64>"), "algo", "b64", "hex" (digest
    bytes, lower hex), "len", "source" (dex / res/xml file), "hosts"}], "hosts": pinned / referenced hostnames,
    "nsc": per-<domain-config> records of every res/xml network-security-config (domains, includeSubdomains, pins,
    pin-set expiration, cleartextTrafficPermitted, trust anchors)}. Dex pins come from OkHttp CertificatePinner-style
    `sha256/<b64>` / `sha1/<b64>` constants; dex hosts are string-pool hostnames / URL hosts of a dex that holds a pin.
    Empty lists when absent; never raises."""
    facts = {"pins": [], "hosts": [], "nsc": []}
    try:
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                n = info.filename
                if info.is_dir() or info.file_size > _PIN_MAX_ENTRY:
                    continue
                is_dex = bool(re.fullmatch(r"classes\d*\.dex", Path(n).name))
                if not (is_dex or (n.startswith("res/") and n.endswith(".xml"))):
                    continue
                try:
                    b = z.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError):
                    continue
                if is_dex:
                    pins = list(dict.fromkeys((m.group(1).decode(), m.group(2).decode()) for m in _PIN_DEX.finditer(b)))
                    if not pins:
                        continue
                    hosts = []
                    for m in _PIN_POOL.finditer(b, 0x70):
                        if m.group(1)[0] != len(m.group(2)):
                            continue
                        t = m.group(2).decode()
                        u = _PIN_URL.match(t)
                        h = u.group(1) if u else t
                        if _PIN_HOST.fullmatch(h) and h.lstrip("*.").split(".")[0].lower() not in _PIN_NOTHOST:
                            hosts.append(h)
                    hosts = list(dict.fromkeys(hosts))
                    facts["pins"] += [_pin_rec(a, v, n, hosts) for a, v in pins]
                    facts["hosts"] += hosts
                elif b"pin" in b or b"domain" in b or b[:2] == b"\x03\x00":
                    try:
                        recs = _nsc_parse(n, b)
                    except Exception:  # noqa: BLE001 - malformed AXML: skip the file
                        continue
                    facts["nsc"] += recs
                    for r in recs:
                        facts["pins"] += r["pins"]
                        facts["hosts"] += [d["host"] for d in r["domains"]]
    except Exception:  # noqa: BLE001 - not a zip
        pass
    facts["hosts"] = list(dict.fromkeys(facts["hosts"]))
    return facts


def cert_pin_scan(apk):
    """ANS tokens encoded as a certificate pin (rows 27, 28): each dex `sha256/<b64>` / NSC <pin> value's digest bytes
    scanned for a literal token, then the b64 text through decode_any; pinned hostnames scanned too. [] when absent."""
    hits = []
    try:
        f = cert_pins(apk)
        for p in f["pins"]:
            raw = _pin_b64(p["b64"]) or b""
            hits += [t.decode() for t in ANS_RE_B.findall(raw)]
            if not hits:
                d = decode_any(p["b64"], depth=2, cap=300, chain=False)
                hits += ANS_RE_T.findall(d or "")
        for h in f["hosts"]:
            hits += ANS_RE_T.findall(h)
    except Exception:  # noqa: BLE001
        pass
    return list(dict.fromkeys(hits))


def decompiled_scan(apk):
    """ANS tokens from apktool resources/smali and jadx sources (for an answer that lives in code)."""
    hits = []
    d = apktool_dir(apk)
    if d:
        for f in list(d.rglob("*.xml")) + list(d.rglob("*.smali")):
            try:
                hits += ANS_RE_T.findall(f.read_text(errors="replace"))
            except OSError:
                continue
    hits += ANS_RE_T.findall(jadx_sources_text(apk))
    return hits


def extract_answer(apk):
    """Robust answer recovery for a mobile challenge. Tries fast paths first, escalating to decompilation:
    puzzle json -> raw zip-entry scan -> dex strings -> nested containers -> static-key AES/DES -> apktool/jadx decompiled scan. Returns the first
    ANS-<16 hex> found (via the decoders + a direct token scan), or None. Order favours speed; the later
    stages cover an answer that was moved into the dex/resources/code (even with renaming). After the puzzle path, entries
    a v1 anti-tamper check flags (v1_tamper_scan: changed / added after signing) go first; [] on an intact APK.
    classloader_shadow_scan runs before them: [] unless a class is defined in both host and payload dex."""
    for cand in puzzle_candidates(apk):
        m = ANS_RE_T.search(cand)
        if m:
            return m.group(0)
    for stage in (classloader_shadow_scan, pinned_payload_scan, v1_tamper_scan, raw_entry_scan, dex_strings, nested_scan, static_key_cipher_scan, identity_key_scan,
                  signing_cert_scan, integrity_key_scan, dex_integrity_gate_scan, xamarin_assembly_scan, decompiled_scan):
        hits = [h for h in stage(apk) if not _eav_alphabet(h)]
        if hits:
            return hits[0]
    return None


# --- AAB / proto-format manifests (coverage atlas row 58) ------------------------------------------------------------
# An Android App Bundle keeps each module's manifest as an aapt2 protobuf XmlNode (<module>/manifest/AndroidManifest.xml;
# a `aapt2 link --proto-format` module zip keeps it at the top level), which neither aapt nor the AXML pool parser reads,
# and its code / assets under base/dex/ and base/assets/, where the APK-layout scans (assets/ prefix, top-level
# classes*.dex) do not look. Minimal wire-format decoder over the aapt2 Resources.proto field numbers, no generated code:
#   XmlNode{1 element, 2 text}  XmlElement{2 namespace_uri, 3 name, 4 attribute, 5 child}
#   XmlAttribute{1 namespace_uri, 2 name, 3 value, 5 resource_id, 6 compiled_item}
#   Item{1 ref Reference{3 name}, 2 str String{1 value}, 3 raw_str RawString{1 value}, 7 prim Primitive}
_PXM_MAX, _PXM_DEPTH, _PXM_NODES, _PXM_DECODE_BUDGET = 8 << 20, 64, 200_000, 200
_PXM_PATH = re.compile(r"(?:[^/]+/manifest/)?AndroidManifest\.xml")
_AAB_MAX_BASE = 64 << 20


def _pb_fields(b):
    """(field number, wire type, value) of one protobuf message; LEN values are bytes. ValueError on malformed input."""
    i, n, out = 0, len(b), []
    while i < n:
        key, i = _pb_varint(b, i)
        fn, wt = key >> 3, key & 7
        if fn == 0:
            raise ValueError("field 0")
        if wt == 0:
            v, i = _pb_varint(b, i)
        elif wt == 2:
            ln, i = _pb_varint(b, i)
            if i + ln > n:
                raise ValueError("truncated")
            v, i = b[i:i + ln], i + ln
        elif wt == 1:
            v, i = b[i:i + 8], i + 8
        elif wt == 5:
            v, i = b[i:i + 4], i + 4
        else:
            raise ValueError("wire type")
        if i > n:
            raise ValueError("truncated")
        out.append((fn, wt, v))
    return out


def _pb_varint(b, i):
    r = s = 0
    while True:
        if i >= len(b) or s > 63:
            raise ValueError("varint")
        c = b[i]
        i += 1
        r |= (c & 0x7F) << s
        s += 7
        if not c & 0x80:
            return r, i


def _pxm_item(b):
    """Display string of a compiled Item (when the attribute's raw value field is empty)."""
    for fn, wt, v in _pb_fields(b):
        if wt != 2:
            continue
        sub = _pb_fields(v)
        if fn == 1:  # Reference: name, else 0x7f... id
            name = next((x for f, w, x in sub if f == 3 and w == 2), b"")
            rid = next((x for f, w, x in sub if f == 2 and w == 0), 0)
            return "@" + name.decode("utf-8", "replace") if name else (f"@0x{rid:08x}" if rid else "")
        if fn in (2, 3):  # String / RawString
            return next((x for f, w, x in sub if f == 1 and w == 2), b"").decode("utf-8", "replace")
        if fn == 7:  # Primitive: the first scalar
            for f, w, x in sub:
                if f == 8:
                    return "true" if x else "false"
                if w == 0:
                    return str(x - (1 << 32) if f == 6 and x >= 1 << 31 else x)
    return ""


def _pxm_element(b, depth, budget):
    if depth > _PXM_DEPTH:
        raise ValueError("depth")
    budget[0] -= 1
    if budget[0] < 0:
        raise ValueError("nodes")
    el = {"tag": "", "ns": "", "attrs": {}, "children": [], "text": ""}
    for fn, wt, v in _pb_fields(b):
        if wt != 2:
            continue
        if fn == 3:
            el["tag"] = v.decode("utf-8", "replace")
        elif fn == 2:
            el["ns"] = v.decode("utf-8", "replace")
        elif fn == 4:
            ns = name = val = b""
            item = None
            for f, w, x in _pb_fields(v):
                if w == 2 and f == 1:
                    ns = x
                elif w == 2 and f == 2:
                    name = x
                elif w == 2 and f == 3:
                    val = x
                elif w == 2 and f == 6:
                    item = x
            sval = val.decode("utf-8", "replace") if val else (_pxm_item(item) if item else "")
            key = name.decode("utf-8", "replace")
            el["attrs"][("android:" if ns.decode("utf-8", "replace") == _ANDROID_NS[1:-1] else "") + key] = sval
        elif fn == 5:
            node = _pxm_node(v, depth + 1, budget)
            if node is None:
                continue
            if isinstance(node, str):
                el["text"] += node
            else:
                el["children"].append(node)
    return el


def _pxm_node(b, depth, budget):
    """An XmlNode: its element dict, its text (str), or None when empty."""
    el = txt = None
    for fn, wt, v in _pb_fields(b):
        if wt == 2 and fn == 1:
            el = _pxm_element(v, depth, budget)
        elif wt == 2 and fn == 2:
            txt = v.decode("utf-8", "replace")
    return el if el is not None else txt


def proto_xml_tree(data):
    """Root element of an aapt2 protobuf XmlNode (AAB / --proto-format manifest or res xml) as nested dicts
    {"tag", "ns", "attrs" {"android:name": value, ...}, "children" [...], "text"}; None for AXML / text XML / any
    non-proto or malformed input. Never raises."""
    try:
        b = bytes(data)
        if not b or len(b) > _PXM_MAX or b[0] != 0x0A:  # XmlNode.element (field 1, LEN); AXML starts 03 00
            return None
        root = _pxm_node(b, 0, [_PXM_NODES])
        if not isinstance(root, dict) or not re.fullmatch(r"[A-Za-z_][\w.:-]{0,127}", root["tag"]):
            return None
        return root
    except Exception:  # noqa: BLE001 - not a proto XmlNode
        return None


def _pxm_walk(el, parent=None):
    yield el, parent
    for c in el["children"]:
        yield from _pxm_walk(c, el)


def _proto_manifests(z):
    """[(module, root)] of every protobuf manifest in an open zip: base first, then feature modules, then a top-level one."""
    out = []
    for info in z.infolist():
        n = info.filename
        if info.is_dir() or info.file_size > _PXM_MAX or not _PXM_PATH.fullmatch(n):
            continue
        try:
            with z.open(info) as f:
                if f.read(1) != b"\x0a":
                    continue
            root = proto_xml_tree(z.read(info))
        except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError):
            continue
        if root is not None and root["tag"] == "manifest":
            out.append((n.split("/")[0] if "/" in n else "", root))
    out.sort(key=lambda t: (t[0] != "base", t[0] == "", t[0]))
    return out


def proto_manifest_facts(apk):
    """manifest_facts()-shaped dict from an AAB's / proto-format module's protobuf manifest (base module first):
    package, versionCode/versionName, allowBackup, debuggable, permissions, components (type, name, exported,
    intent_filters, deep_link_schemes, deep_link_hosts, meta_data) plus "meta_data" [{"name", "value", "resource",
    "parent", "module"}] across every module and "modules" [names]. {} when the archive has no protobuf manifest."""
    try:
        with zipfile.ZipFile(apk) as z:
            mans = _proto_manifests(z)
    except Exception:  # noqa: BLE001
        return {}
    if not mans:
        return {}
    A = "android:"
    module, root = mans[0]
    app = next((c for c in root["children"] if c["tag"] == "application"), None)
    facts = {
        "package": root["attrs"].get("package"),
        "versionCode": root["attrs"].get(A + "versionCode"),
        "versionName": root["attrs"].get(A + "versionName"),
        "permissions": sorted({c["attrs"].get(A + "name") for c in root["children"]
                               if c["tag"] in ("uses-permission", "uses-permission-sdk-23") and c["attrs"].get(A + "name")}),
        "allowBackup": app["attrs"].get(A + "allowBackup") if app else None,
        "debuggable": app["attrs"].get(A + "debuggable") if app else None,
        "components": [], "meta_data": [], "modules": [m for m, _ in mans], "format": "proto",
    }
    for mod, r in mans:
        for el, parent in _pxm_walk(r):
            if el["tag"] == "meta-data":
                facts["meta_data"].append({"name": el["attrs"].get(A + "name"), "value": el["attrs"].get(A + "value"),
                                           "resource": el["attrs"].get(A + "resource"),
                                           "parent": (parent or {}).get("attrs", {}).get(A + "name") or (parent or {}).get("tag"),
                                           "module": mod})
        rapp = next((c for c in r["children"] if c["tag"] == "application"), None)
        for c in (rapp["children"] if rapp else []):
            if c["tag"] not in ("activity", "activity-alias", "service", "receiver", "provider"):
                continue
            filters = [f for f in c["children"] if f["tag"] == "intent-filter"]
            datas = [d for f in filters for d in f["children"] if d["tag"] == "data"]
            exported = c["attrs"].get(A + "exported")
            facts["components"].append({
                "type": c["tag"], "name": c["attrs"].get(A + "name"), "module": mod,
                "exported": (exported == "true") if exported is not None else bool(filters),
                "exported_explicit": exported, "intent_filters": len(filters),
                "deep_link_schemes": sorted({d["attrs"][A + "scheme"] for d in datas if d["attrs"].get(A + "scheme")}),
                "deep_link_hosts": sorted({d["attrs"][A + "host"] for d in datas if d["attrs"].get(A + "host")}),
                "meta_data": {m["attrs"].get(A + "name"): m["attrs"].get(A + "value", m["attrs"].get(A + "resource"))
                              for m in c["children"] if m["tag"] == "meta-data"},
            })
    return facts


def aab_base_apk(apk):
    """An AAB's base module re-laid as APK bytes (base/dex/classesN.dex -> classesN.dex, base/assets|res|lib/ -> same,
    base/root/* -> *, resources.pb kept), so the APK-layout scans can read it. None when not a bundle. Never raises."""
    try:
        with zipfile.ZipFile(apk) as z:
            infos = [i for i in z.infolist() if i.filename.startswith("base/") and not i.is_dir()]
            if not any(i.filename == "base/manifest/AndroidManifest.xml" for i in infos) or \
                    sum(i.file_size for i in infos) > _AAB_MAX_BASE:
                return None
            bio = io.BytesIO()
            with zipfile.ZipFile(bio, "w", zipfile.ZIP_STORED) as out:
                seen = set()
                for i in infos:
                    rel = i.filename[5:]
                    if rel.startswith("manifest/"):
                        continue
                    rel = rel[4:] if rel.startswith(("dex/", "root/")) else rel
                    if rel and rel not in seen:
                        seen.add(rel)
                        out.writestr(rel, z.read(i))
            return bio.getvalue()
    except Exception:  # noqa: BLE001 - truncated / impostor bundle
        return None


def proto_manifest_scan(apk):
    """ANS tokens from an AAB / proto-format module: every protobuf manifest's attribute values and text (meta-data
    android:value / resource first), read directly and, when encoded-looking, through decode_any; then the bundle's
    base module re-laid as an APK (aab_base_apk) through puzzle_candidates -> raw_entry_scan -> dex_strings ->
    nested_scan -> static_key_cipher_scan. [] when absent; never raises."""
    hits = []
    try:
        with zipfile.ZipFile(apk) as z:
            mans = _proto_manifests(z)
        vals = []
        for _, root in mans:
            for el, _p in _pxm_walk(root):
                vs = list(el["attrs"].values()) + ([el["text"]] if el["text"].strip() else [])
                vals.extend((el["tag"] != "meta-data", v) for v in vs if v)
        vals = [v for _, v in sorted(vals, key=lambda t: t[0])]
        budget = _PXM_DECODE_BUDGET
        for s in dict.fromkeys(vals):
            m = ANS_RE_T.findall(s)
            if m:
                hits += m
                continue
            if budget > 0 and _POOL_ENCODED.fullmatch(s.strip()):
                budget -= 1
                d = decode_any(s.strip(), depth=3, cap=400, chain=False)
                if d:
                    hits += ANS_RE_T.findall(d)
        if not hits and mans:
            base = aab_base_apk(apk)
            if base:
                bio = io.BytesIO(base)
                hits += [m.group(0) for c in puzzle_candidates(bio) for m in ANS_RE_T.finditer(c)]
                for stage in (raw_entry_scan, dex_strings, nested_scan, static_key_cipher_scan):
                    if hits:
                        break
                    hits += stage(bio)
    except Exception:  # noqa: BLE001 - truncated / impostor bundle: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- manifest facts (for exported-component / deep-link / allowBackup style questions) ------------
def manifest_facts(apk):
    """Parse AndroidManifest.xml via apktool's decoded (text) manifest. Returns a dict with package,
    allowBackup, debuggable, permissions, and per-component exported/intent-filter/deep-link data.
    Empty dict if apktool is unavailable. An AAB / proto-format module (protobuf manifest apktool cannot decode)
    is read by proto_manifest_facts() instead."""
    pf = proto_manifest_facts(apk)
    if pf:
        return pf
    d = apktool_dir(apk)
    if not d:
        return {}
    try:
        root = ET.parse(d / "AndroidManifest.xml").getroot()
    except (OSError, ET.ParseError):
        return {}
    app = root.find("application")
    facts = {
        "package": root.get("package"),
        "permissions": sorted(e.get(_ANDROID_NS + "name") for e in root.findall("uses-permission")
                              if e.get(_ANDROID_NS + "name")),
        "allowBackup": (app.get(_ANDROID_NS + "allowBackup") if app is not None else None),
        "debuggable": (app.get(_ANDROID_NS + "debuggable") if app is not None else None),
        "components": [],
    }
    for tag in ("activity", "activity-alias", "service", "receiver", "provider"):
        for c in (app.findall(tag) if app is not None else []):
            filters = c.findall("intent-filter")
            schemes = sorted({dd.get(_ANDROID_NS + "scheme") for f in filters for dd in f.findall("data")
                              if dd.get(_ANDROID_NS + "scheme")})
            exported = c.get(_ANDROID_NS + "exported")
            facts["components"].append({
                "type": tag,
                "name": c.get(_ANDROID_NS + "name"),
                # Android default: exported=true when an intent-filter is present and not set explicitly.
                "exported": (exported == "true") if exported is not None else bool(filters),
                "exported_explicit": exported,
                "intent_filters": len(filters),
                "deep_link_schemes": schemes,
            })
    return facts


# --- tiny Dalvik evaluator: an answer computed by simple bytecode (coverage atlas rows 35, 43, 45) ---------------------
# char/byte arrays, xor/add loops, StringBuilder chains, switch-flattened state machines and string-encryption helpers,
# run statically over ONE method at a time (plus its in-dex callees and the <clinit>s it reads). Unknown invokes abort.
_DXE_MAX_DEX, _DXE_STEPS, _DXE_BUDGET_S, _DXE_DEPTH, _DXE_MAX_ARR = 32 << 20, 50_000, 0.8, 6, 1 << 16
_DXE_DEEP_STEPS, _DXE_DEEP_BUDGET_S = 2_000_000, 2.0   # dex_eval_scan(deep=True): D23 computed-code (`analysis`) apps
_DXE_HOT = frozenset((0x23, 0x24, 0x26, 0x2B, 0x2C, 0x8E, 0x97, 0xB7, 0xD7, 0xDF))
_DXE_LIB = re.compile(r"L(?:androidx|android|kotlinx?|java|javax|dalvik|okhttp3|okio|retrofit2|org/jetbrains|org/intellij"
                      r"|com/google|com/squareup|com/facebook|io/reactivex)/")
# exception control flow (coverage atlas row 90; only _ExcVM): ops that throw -- `throw`, array-length / aget / aput /
# iget / iput / instance invoke on null, a bad array index, int/long div/rem by zero -- and java.lang's exception tree
_DXX_DIV = frozenset((0x93, 0x94, 0x9E, 0x9F, 0xB3, 0xB4, 0xBE, 0xBF, 0xD3, 0xD4, 0xDB, 0xDC))
_DXX_OPS = frozenset((0x21, 0x27, 0x6E, 0x6F, 0x70, 0x72, 0x74, 0x75, 0x76, 0x78, *range(0x44, 0x60), *_DXX_DIV))
_DXX_TREE = {f"L{c};": f"L{q};" for c, q in (
    ("java/lang/Exception", "java/lang/Throwable"), ("java/lang/Error", "java/lang/Throwable"),
    ("java/lang/RuntimeException", "java/lang/Exception"), ("java/lang/SecurityException", "java/lang/RuntimeException"),
    ("java/lang/IllegalStateException", "java/lang/RuntimeException"),
    ("java/lang/IllegalArgumentException", "java/lang/RuntimeException"),
    ("java/lang/NumberFormatException", "java/lang/IllegalArgumentException"),
    ("java/lang/ArithmeticException", "java/lang/RuntimeException"),
    ("java/lang/NullPointerException", "java/lang/RuntimeException"),
    ("java/lang/ClassCastException", "java/lang/RuntimeException"),
    ("java/lang/UnsupportedOperationException", "java/lang/RuntimeException"),
    ("java/lang/IndexOutOfBoundsException", "java/lang/RuntimeException"),
    ("java/lang/ArrayIndexOutOfBoundsException", "java/lang/IndexOutOfBoundsException"),
    ("java/lang/StringIndexOutOfBoundsException", "java/lang/IndexOutOfBoundsException"),
    ("java/lang/NegativeArraySizeException", "java/lang/RuntimeException"),
    ("java/util/NoSuchElementException", "java/lang/RuntimeException"),
    ("java/util/ConcurrentModificationException", "java/lang/RuntimeException"),
    ("java/lang/ReflectiveOperationException", "java/lang/Exception"),
    ("java/lang/ClassNotFoundException", "java/lang/ReflectiveOperationException"),
    ("java/lang/NoSuchMethodException", "java/lang/ReflectiveOperationException"),
    ("java/lang/NoSuchFieldException", "java/lang/ReflectiveOperationException"),
    ("java/lang/IllegalAccessException", "java/lang/ReflectiveOperationException"),
    ("java/lang/InstantiationException", "java/lang/ReflectiveOperationException"),
    ("java/lang/reflect/InvocationTargetException", "java/lang/ReflectiveOperationException"),
    ("java/lang/CloneNotSupportedException", "java/lang/Exception"),
    ("java/lang/InterruptedException", "java/lang/Exception"),
    ("java/util/concurrent/TimeoutException", "java/lang/Exception"),
    ("java/security/GeneralSecurityException", "java/lang/Exception"),
    ("java/security/NoSuchAlgorithmException", "java/security/GeneralSecurityException"),
    ("java/io/IOException", "java/lang/Exception"), ("java/io/FileNotFoundException", "java/io/IOException"),
    ("java/io/EOFException", "java/io/IOException"), ("java/net/SocketException", "java/io/IOException"),
    ("java/net/ConnectException", "java/net/SocketException"),
    ("android/util/AndroidException", "java/lang/Exception"),
    ("android/content/pm/PackageManager$NameNotFoundException", "android/util/AndroidException"),
    ("android/system/ErrnoException", "java/lang/Exception"), ("java/lang/AssertionError", "java/lang/Error"),
    ("java/lang/LinkageError", "java/lang/Error"), ("java/lang/NoClassDefFoundError", "java/lang/LinkageError"),
    ("java/lang/UnsatisfiedLinkError", "java/lang/LinkageError"),
    ("java/lang/VirtualMachineError", "java/lang/Error"), ("java/lang/StackOverflowError", "java/lang/VirtualMachineError"),
    ("java/lang/OutOfMemoryError", "java/lang/VirtualMachineError"),
    ("kotlin/KotlinNullPointerException", "java/lang/NullPointerException"),
    ("kotlin/UninitializedPropertyAccessException", "java/lang/RuntimeException"))}


class _DxAbort(Exception):
    pass


class _DxArr(list):
    __slots__ = ("t",)


class _DxSB:
    __slots__ = ("s",)

    def __init__(self, s=""):
        self.s = list(s)


class _DxThrow(_DxAbort):
    """A Java exception thrown by a modelled call; `types` = its class and supertypes (descriptors)."""

    def __init__(self, *types):
        super().__init__(types[0])
        self.types = (*types, "Ljava/lang/Exception;", "Ljava/lang/Throwable;")

    obj = None  # the thrown object (_DxExc: a `throw` / VM fault of exception_flow_scan's VM); None = framework-raised


class _DxExc(_DxThrow):
    """An exception object thrown inside the evaluator (`throw vX`, div by zero, null receiver, bad index)."""

    def __init__(self, obj, types):
        _DxAbort.__init__(self, types[0])
        self.obj, self.types = obj, types


class _DxObj:
    __slots__ = ("t", "f")

    def __init__(self, t):
        self.t, self.f = t, {}


class _DxB64:
    __slots__ = ("url",)

    def __init__(self, url):
        self.url = url


_DXE_UNK = object()  # opaque value (unknown parameter, const-class, ...): any use aborts


def _dxe_w32(v):
    return ((v + 0x80000000) & 0xFFFFFFFF) - 0x80000000


def _dxe_w64(v):
    return ((v + (1 << 63)) & ((1 << 64) - 1)) - (1 << 63)


def _dxe_binop(k, a, b, wide):
    if not isinstance(a, int) or not isinstance(b, int):
        raise _DxAbort
    m = 63 if wide else 31
    if k == 0:
        r = a + b
    elif k == 1:
        r = a - b
    elif k == 2:
        r = a * b
    elif k in (3, 4):
        if b == 0:
            raise _DxAbort
        q = abs(a) // abs(b) * (1 if (a < 0) == (b < 0) else -1)
        r = q if k == 3 else a - b * q
    elif k == 5:
        r = a & b
    elif k == 6:
        r = a | b
    elif k == 7:
        r = a ^ b
    elif k == 8:
        r = a << (b & m)
    elif k == 9:
        r = a >> (b & m)
    elif k == 10:
        r = (a & ((1 << (m + 1)) - 1)) >> (b & m)
    else:
        raise _DxAbort
    return _dxe_w64(r) if wide else _dxe_w32(r)


def _dxe_str(x):
    if isinstance(x, str):
        return x
    if isinstance(x, _DxSB):
        return "".join(x.s)
    if x is None:
        return "null"
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        return str(x)
    raise _DxAbort


def _dxe_bytes(a):
    if not isinstance(a, list):
        raise _DxAbort
    return bytes(v & 0xFF for v in a)


def _dxe_barr(b):
    r = _DxArr((x ^ 0x80) - 0x80 for x in b)
    r.t = "B"
    return r


def _dxe_carr(s):
    r = _DxArr(ord(ch) for ch in s)
    r.t = "C"
    return r


def _dxe_cs(x):
    n = (x if isinstance(x, str) else "utf-8").lower().replace("_", "-")
    return "latin-1" if n in ("iso-8859-1", "us-ascii", "ascii", "latin1") else "utf-8"


def _dxe_b64d(x, url=False):
    s = x if isinstance(x, str) else _dxe_bytes(x).decode("latin-1")
    s = re.sub(r"[\s=]", "", s)
    try:
        return _dxe_barr(base64.b64decode(s + "=" * (-len(s) % 4), b"-_" if url or "-" in s or "_" in s else None))
    except (binascii.Error, ValueError):
        raise _DxAbort from None


def _dxe_parse(s, radix=10):
    if not isinstance(s, str) or not isinstance(radix, int) or not 2 <= radix <= 36 or not re.fullmatch(r"[+-]?\w+", s):
        raise _DxAbort
    try:
        return int(s, radix)
    except ValueError:
        raise _DxAbort from None


def _dxe_hash(s):
    h = 0
    for ch in s:
        h = (31 * h + ord(ch)) & 0xFFFFFFFF
    return _dxe_w32(h)


def _dxe_sb_append(a):
    sb, v = a[0], a[1]
    if not isinstance(sb, _DxSB):
        raise _DxAbort
    sb.s.extend(v)
    return sb


def _dxe_intrinsics():
    S, SB = "Ljava/lang/String;", "Ljava/lang/StringBuilder;"
    t = {}
    for sb in (SB, "Ljava/lang/StringBuffer;"):
        t[sb + "-><init>()V"] = t[sb + "-><init>(I)V"] = lambda a: _DxSB()
        t[sb + "-><init>(Ljava/lang/String;)V"] = t[sb + "-><init>(Ljava/lang/CharSequence;)V"] = \
            lambda a: _DxSB(_dxe_str(a[1]))
        for p, conv in (("C", lambda v: chr(v & 0xFFFF)), ("I", str), ("J", str), ("Z", lambda v: "true" if v else "false"),
                        (S, _dxe_str), ("Ljava/lang/Object;", _dxe_str), ("Ljava/lang/CharSequence;", _dxe_str),
                        ("[C", lambda v: "".join(map(chr, v)))):
            t[f"{sb}->append({p}){sb}"] = (lambda c: lambda a: _dxe_sb_append((a[0], c(a[1]))))(conv)
        t[sb + "->toString()" + S] = lambda a: "".join(a[0].s)
        t[sb + "->length()I"] = lambda a: len(a[0].s)
        t[sb + "->charAt(I)C"] = lambda a: ord(a[0].s[a[1]])
        t[f"{sb}->reverse(){sb}"] = lambda a: (a[0].s.reverse(), a[0])[1]
        t[sb + "->setCharAt(IC)V"] = lambda a: a[0].s.__setitem__(a[1], chr(a[2] & 0xFFFF))
        t[f"{sb}->insert(IC){sb}"] = lambda a: (a[0].s.insert(a[1], chr(a[2] & 0xFFFF)), a[0])[1]
        t[f"{sb}->insert(I{S}){sb}"] = lambda a: (a[0].s.__setitem__(slice(a[1], a[1]), _dxe_str(a[2])), a[0])[1]
        t[f"{sb}->deleteCharAt(I){sb}"] = lambda a: (a[0].s.pop(a[1]), a[0])[1]
    t[S + "-><init>([C)V"] = lambda a: "".join(chr(v & 0xFFFF) for v in a[1])
    t[S + "-><init>([CII)V"] = lambda a: "".join(chr(v & 0xFFFF) for v in a[1][a[2]:a[2] + a[3]])
    t[S + "-><init>([B)V"] = lambda a: _dxe_bytes(a[1]).decode("utf-8", "replace")
    t[S + "-><init>([BII)V"] = lambda a: _dxe_bytes(a[1][a[2]:a[2] + a[3]]).decode("utf-8", "replace")
    t[S + "-><init>([BLjava/lang/String;)V"] = t[S + "-><init>([BLjava/nio/charset/Charset;)V"] = \
        lambda a: _dxe_bytes(a[1]).decode(_dxe_cs(a[2]), "replace")
    t[S + "-><init>(Ljava/lang/String;)V"] = t[S + "-><init>(Ljava/lang/StringBuilder;)V"] = lambda a: _dxe_str(a[1])
    t[S + "->charAt(I)C"] = lambda a: ord(a[0][a[1]])
    t[S + "->length()I"] = lambda a: len(a[0])
    t[S + "->isEmpty()Z"] = lambda a: int(not a[0])
    t[S + "->hashCode()I"] = lambda a: _dxe_hash(a[0])
    t[S + "->getBytes()[B"] = lambda a: _dxe_barr(a[0].encode("utf-8", "replace"))
    t[S + "->getBytes(Ljava/lang/String;)[B"] = t[S + "->getBytes(Ljava/nio/charset/Charset;)[B"] = \
        lambda a: _dxe_barr(a[0].encode(_dxe_cs(a[1]), "replace"))
    t[S + "->toCharArray()[C"] = lambda a: _dxe_carr(a[0])
    t[f"{S}->substring(I){S}"] = lambda a: a[0][a[1]:]
    t[f"{S}->substring(II){S}"] = lambda a: a[0][a[1]:a[2]]
    t[f"{S}->concat({S}){S}"] = lambda a: a[0] + _dxe_str(a[1])
    t[f"{S}->trim(){S}"] = lambda a: a[0].strip(" \t\r\n\0")
    t[f"{S}->intern(){S}"] = t[f"{S}->toString(){S}"] = lambda a: a[0]
    t[f"{S}->toUpperCase(){S}"] = lambda a: a[0].upper()
    t[f"{S}->toLowerCase(){S}"] = lambda a: a[0].lower()
    t[S + "->equals(Ljava/lang/Object;)Z"] = lambda a: int(a[0] == a[1])
    t[f"{S}->indexOf(I)I"] = lambda a: a[0].find(chr(a[1] & 0xFFFF))
    t[f"{S}->indexOf({S})I"] = lambda a: a[0].find(_dxe_str(a[1]))
    for p, conv in (("C", lambda v: chr(v & 0xFFFF)), ("I", str), ("J", str), ("Z", lambda v: "true" if v else "false"),
                    ("Ljava/lang/Object;", _dxe_str), ("[C", lambda v: "".join(map(chr, v)))):
        t[f"{S}->valueOf({p}){S}"] = (lambda c: lambda a: c(a[0]))(conv)
    t[f"{S}->copyValueOf([C){S}"] = lambda a: "".join(map(chr, a[0]))
    for box, prim in (("Ljava/lang/Integer;", "I"), ("Ljava/lang/Long;", "J"), ("Ljava/lang/Character;", "C"),
                      ("Ljava/lang/Byte;", "B"), ("Ljava/lang/Short;", "S"), ("Ljava/lang/Boolean;", "Z")):
        t[f"{box}->valueOf({prim}){box}"] = lambda a: a[0]
    for box, prim, w in (("Ljava/lang/Integer;", "I", _dxe_w32), ("Ljava/lang/Long;", "J", _dxe_w64)):
        t[f"{box}->intValue()I"] = t[f"{box}->longValue()J"] = lambda a: a[0]
        nm = "Int" if prim == "I" else "Long"
        t[f"{box}->parse{nm}({S}){prim}"] = (lambda w: lambda a: w(_dxe_parse(a[0])))(w)
        t[f"{box}->parse{nm}({S}I){prim}"] = (lambda w: lambda a: w(_dxe_parse(a[0], a[1])))(w)
        t[f"{box}->valueOf({S}){box}"] = (lambda w: lambda a: w(_dxe_parse(a[0])))(w)
        mask = 0xFFFFFFFF if prim == "I" else (1 << 64) - 1
        t[f"{box}->toHexString({prim}){S}"] = (lambda m: lambda a: format(a[0] & m, "x"))(mask)
        t[f"{box}->toString({prim}){S}"] = lambda a: str(a[0])
    t["Ljava/lang/Integer;->toString(II)" + S] = \
        lambda a: (lambda v, r: ("-" if v < 0 else "") + (lambda f: f(f, abs(v), r))(
            lambda f, n, r: "0123456789abcdefghijklmnopqrstuvwxyz"[n] if n < r else f(f, n // r, r) +
            "0123456789abcdefghijklmnopqrstuvwxyz"[n % r]))(a[0], a[1] if 2 <= a[1] <= 36 else 10)
    t["Ljava/lang/Character;->charValue()C"] = lambda a: a[0]
    t["Ljava/lang/Character;->toString(C)" + S] = lambda a: chr(a[0] & 0xFFFF)
    t["Ljava/lang/Object;-><init>()V"] = lambda a: None
    t["Ljava/lang/Math;->abs(I)I"] = lambda a: _dxe_w32(abs(a[0]))
    t["Ljava/lang/Math;->max(II)I"] = lambda a: max(a[0], a[1])
    t["Ljava/lang/Math;->min(II)I"] = lambda a: min(a[0], a[1])
    t["Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V"] = \
        lambda a: a[2].__setitem__(slice(a[3], a[3] + a[4]), a[0][a[1]:a[1] + a[4]]) \
        if 0 <= a[4] and a[1] + a[4] <= len(a[0]) and a[3] + a[4] <= len(a[2]) else (_ for _ in ()).throw(_DxAbort)
    for p in ("B", "C", "I"):
        def cp(a, p=p, rng=False):
            r = _DxArr(a[0][a[1]:a[2]] if rng else (list(a[0][:a[1]]) + [0] * max(0, a[1] - len(a[0]))))
            r.t = p
            return r
        t[f"Ljava/util/Arrays;->copyOf([{p}I)[{p}"] = cp
        t[f"Ljava/util/Arrays;->copyOfRange([{p}II)[{p}"] = (lambda p: lambda a: cp(a, p, True))(p)
    t["Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B"] = lambda a: _dxe_barr(a[0].encode(_dxe_cs(a[1])))
    t["Ljava/nio/charset/Charset;->forName(Ljava/lang/String;)Ljava/nio/charset/Charset;"] = lambda a: _dxe_str(a[0])
    ab = "Landroid/util/Base64;"
    t[ab + "->decode(Ljava/lang/String;I)[B"] = t[ab + "->decode([BI)[B"] = lambda a: _dxe_b64d(a[0], bool(a[1] & 8))
    t[ab + "->encodeToString([BI)" + S] = lambda a: base64.b64encode(_dxe_bytes(a[0])).decode()
    t[ab + "->encode([BI)[B"] = lambda a: _dxe_barr(base64.b64encode(_dxe_bytes(a[0])))
    jb = "Ljava/util/Base64;"
    for g, url in (("getDecoder", False), ("getUrlDecoder", True), ("getMimeDecoder", False)):
        t[f"{jb}->{g}()Ljava/util/Base64$Decoder;"] = (lambda u: lambda a: _DxB64(u))(url)
    t[f"{jb}->getEncoder()Ljava/util/Base64$Encoder;"] = lambda a: _DxB64(False)
    t["Ljava/util/Base64$Decoder;->decode(Ljava/lang/String;)[B"] = t["Ljava/util/Base64$Decoder;->decode([B)[B"] = \
        lambda a: _dxe_b64d(a[1], a[0].url)
    t["Ljava/util/Base64$Encoder;->encodeToString([B)" + S] = lambda a: base64.b64encode(_dxe_bytes(a[1])).decode()
    t["Ljava/util/Base64$Encoder;->encode([B)[B"] = lambda a: _dxe_barr(base64.b64encode(_dxe_bytes(a[1])))
    for lv in "vdiwe":
        t[f"Landroid/util/Log;->{lv}({S}{S})I"] = lambda a: 0
    for k, v in _dxe_intr_numeric().items():  # new keys only, except the width-keeping Long.valueOf(J)
        if k == "Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;" or k not in t:
            t[k] = v
    return t


# --- java.lang / kotlin numeric intrinsics a mixer chain may call (coverage atlas row 96: dex-eval-long-intrinsics) --
# Long / Integer bit ops (rotate, reverse, bitCount, nlz/ntz, highest/lowestOneBit, signum), unsigned div / rem /
# compare / toString / parse, Math floor / exact / multiplyHigh, String.format (%d %x %X %o %s %c %b %n, flags 0 - +
# width; Long-boxed negatives format as 64-bit two's complement), Long / Arrays hashCode, CRC32 / Adler32 /
# MessageDigest / BigInteger(1, d).toString(16), kotlin ULong / UInt helpers. Exact Java semantics: two's complement
# wrap, ArithmeticException (div by zero, *Exact overflow) and bad input abort the method. Added with setdefault, so
# every pre-existing intrinsic keeps its behaviour.
class _DxJ(int):
    """A boxed java.lang.Long (Long.valueOf(J)): an int that remembers it is 64-bit for String.format("%x")."""
    __slots__ = ()


_DXE_NEW = frozenset(("Ljava/util/zip/CRC32;", "Ljava/util/zip/Adler32;", "Ljava/math/BigInteger;"))
_DXE_DIG = "0123456789abcdefghijklmnopqrstuvwxyz"
_DXE_MD = {"md5": "md5", "sha-1": "sha1", "sha1": "sha1", "sha-256": "sha256", "sha256": "sha256", "sha-512": "sha512",
           "sha-384": "sha384", "sha-224": "sha224", "sha512": "sha512"}


def _dxe_radix(v, r):
    if not isinstance(v, int) or not isinstance(r, int):
        raise _DxAbort
    r = r if 2 <= r <= 36 else 10
    s, n = [], abs(v)
    while True:
        s.append(_DXE_DIG[n % r])
        n //= r
        if not n:
            break
    return ("-" if v < 0 else "") + "".join(reversed(s))


def _dxe_ints(*xs):
    if not all(isinstance(x, int) for x in xs):
        raise _DxAbort
    return xs


def _dxe_exact(v, bits):
    if not -(1 << (bits - 1)) <= v < 1 << (bits - 1):
        raise _DxAbort  # ArithmeticException: integer overflow
    return v


def _dxe_fdiv(a, b, w):
    _dxe_ints(a, b)
    if b == 0:
        raise _DxAbort
    return w(a // b)


def _dxe_fmod(a, b, w):
    _dxe_ints(a, b)
    if b == 0:
        raise _DxAbort
    return w(a % b)


def _dxe_udivrem(a, b, bits, rem, w):
    _dxe_ints(a, b)
    m = (1 << bits) - 1
    if not b & m:
        raise _DxAbort
    return w((a & m) % (b & m) if rem else (a & m) // (b & m))


def _dxe_parse_u(s, radix, bits):
    v = _dxe_parse(s, radix)
    if v < 0 or v >> bits or s.startswith("-"):
        raise _DxAbort  # NumberFormatException
    return _dxe_w64(v) if bits == 64 else _dxe_w32(v)


def _dxe_rev(v, bits, unit):
    m = (1 << bits) - 1
    v &= m
    if unit == 1:
        r = int(format(v, f"0{bits}b")[::-1], 2)
    else:
        r = int.from_bytes(v.to_bytes(bits // 8, "big"), "little")
    return _dxe_w64(r) if bits == 64 else _dxe_w32(r)


def _dxe_ffmt(f, args):  # noqa: C901 - one java.util.Formatter subset
    """java.lang.String.format(f, args...) for integral / string / char / boolean conversions; aborts on the rest."""
    if not isinstance(f, str) or not isinstance(args, list):
        raise _DxAbort
    out, k, pos = [], 0, 0
    for m in re.finditer(r"%(?:(\d+)\$)?([-#+ 0,(]*)(\d+)?(?:\.(\d+))?([a-zA-Z%])", f):
        out.append(f[pos:m.start()])
        pos = m.end()
        idx, flags, width, prec, c = m.groups()
        if c == "%":
            out.append("%")
            continue
        if c == "n":
            out.append("\n")
            continue
        if idx:
            i = int(idx) - 1
        else:
            i, k = k, k + 1
        if not 0 <= i < len(args):
            raise _DxAbort  # MissingFormatArgumentException
        v = args[i]
        if isinstance(v, _DxObj) and v.t == "Ljava/math/BigInteger;" and isinstance(v.f.get("v"), int):
            v, big = v.f["v"], True
        else:
            big = False
        cl = c.lower()
        if cl == "s":
            s = _dxe_str(v)
            s = s[:int(prec)] if prec else s
        elif cl == "b":
            if isinstance(v, int):
                raise _DxAbort  # a boxed Boolean and an Integer look alike here
            s = "false" if v is None else "true"
        elif cl == "c":
            if not isinstance(v, int) or isinstance(v, bool):
                raise _DxAbort
            s = chr(v & 0xFFFF)
        elif cl in ("d", "x", "o"):
            if not isinstance(v, int) or isinstance(v, bool) or prec is not None or (cl == "d" and c == "D"):
                raise _DxAbort  # IllegalFormatConversion / IllegalFormatPrecision
            if cl == "d":
                s = str(abs(v))
                if "," in flags:
                    s = f"{abs(v):,}"
                sign = "-" if v < 0 else "+" if "+" in flags else " " if " " in flags else ""
            else:
                if v < 0 and not big:
                    v &= (1 << 64) - 1 if isinstance(v, _DxJ) else 0xFFFFFFFF
                sign = "-" if v < 0 else ""
                s = format(abs(v), cl)
                if "#" in flags:
                    s = ("0x" if cl == "x" else "0") + s
            if "0" in flags and width:
                s = s.rjust(int(width) - len(sign), "0")
            s = sign + s
        else:
            raise _DxAbort  # %f %e %h %t ...: not modelled
        if c.isupper():
            s = s.upper()
        if width:
            s = s.ljust(int(width)) if "-" in flags else s.rjust(int(width))
        out.append(s)
    out.append(f[pos:])
    return "".join(out)


def _dxe_ahash(a, el=lambda x: x):
    if a is None:
        return 0
    if not isinstance(a, list):
        raise _DxAbort
    h = 1
    for x in a:
        h = (31 * h + el(x)) & 0xFFFFFFFF
    return _dxe_w32(h)


def _dxe_lhash(v):
    return _dxe_w32((v ^ ((v & ((1 << 64) - 1)) >> 32)) & 0xFFFFFFFF)


def _dxe_bi_init(a, v):
    o = a[0]
    if not isinstance(o, _DxObj):
        raise _DxAbort
    o.f["v"] = v
    return None


def _dxe_bi(v):
    o = _DxObj("Ljava/math/BigInteger;")
    o.f["v"] = v
    return o


def _dxe_biv(o):
    if not isinstance(o, _DxObj) or not isinstance(o.f.get("v"), int):
        raise _DxAbort
    return o.f["v"]


def _dxe_bi_mag(sig, mag):
    b = _dxe_bytes(mag)
    v = int.from_bytes(b, "big")
    if sig not in (-1, 0, 1) or (sig == 0 and v):
        raise _DxAbort  # NumberFormatException
    return sig * v


def _dxe_chk(a, fn, init):
    o = a[0]
    if not isinstance(o, _DxObj):
        raise _DxAbort
    v = o.f.get("v", init)
    if len(a) == 2 and isinstance(a[1], int):
        b = bytes([a[1] & 0xFF])
    else:
        b = _dxe_bytes(a[1])
        if len(a) == 4:
            _dxe_ints(a[2], a[3])
            if a[2] < 0 or a[3] < 0 or a[2] + a[3] > len(b):
                raise _DxAbort
            b = b[a[2]:a[2] + a[3]]
    o.f["v"] = fn(b, v)
    return None


def _dxe_md_get(a):
    alg = _DXE_MD.get(_dxe_str(a[0]).lower())
    if alg is None:
        raise _DxAbort
    m = _DxObj("Ljava/security/MessageDigest;")
    m.f["md"] = hashlib.new(alg)
    return m


def _dxe_md(a, op):
    o = a[0]
    if not isinstance(o, _DxObj) or "md" not in o.f:
        raise _DxAbort
    md = o.f["md"]
    if op == "update":
        b = bytes([a[1] & 0xFF]) if isinstance(a[1], int) else _dxe_bytes(a[1])
        if len(a) == 4:
            _dxe_ints(a[2], a[3])
            b = b[a[2]:a[2] + a[3]]
        md.update(b)
        return None
    if op == "digest" and len(a) > 1:
        md.update(_dxe_bytes(a[1]))
    o.f["md"] = hashlib.new(md.name)
    return None if op == "reset" else _dxe_barr(md.digest())


def _dxe_intr_numeric():
    S, L, I, M = "Ljava/lang/String;", "Ljava/lang/Long;", "Ljava/lang/Integer;", "Ljava/lang/Math;"
    t = {}
    for box, p, bits, w in ((L, "J", 64, _dxe_w64), (I, "I", 32, _dxe_w32)):
        m = (1 << bits) - 1
        t[f"{box}->rotateLeft({p}I){p}"] = (lambda m, b, w: lambda a: w(
            (((a[0] & m) << (a[1] % b)) | ((a[0] & m) >> ((b - a[1] % b) % b))) & m))(m, bits, w)
        t[f"{box}->rotateRight({p}I){p}"] = (lambda m, b, w: lambda a: w(
            (((a[0] & m) >> (a[1] % b)) | ((a[0] & m) << ((b - a[1] % b) % b))) & m))(m, bits, w)
        t[f"{box}->reverse({p}){p}"] = (lambda b: lambda a: _dxe_rev(_dxe_ints(a[0])[0], b, 1))(bits)
        t[f"{box}->reverseBytes({p}){p}"] = (lambda b: lambda a: _dxe_rev(_dxe_ints(a[0])[0], b, 8))(bits)
        t[f"{box}->bitCount({p})I"] = (lambda m: lambda a: bin(a[0] & m).count("1"))(m)
        t[f"{box}->numberOfLeadingZeros({p})I"] = (lambda m, b: lambda a: b - (a[0] & m).bit_length())(m, bits)
        t[f"{box}->numberOfTrailingZeros({p})I"] = (lambda m, b: lambda a: (
            ((a[0] & m) & -(a[0] & m)).bit_length() - 1 if a[0] & m else b))(m, bits)
        t[f"{box}->highestOneBit({p}){p}"] = (lambda m, w: lambda a: w(
            1 << ((a[0] & m).bit_length() - 1) if a[0] & m else 0))(m, w)
        t[f"{box}->lowestOneBit({p}){p}"] = (lambda m, w: lambda a: w((a[0] & m) & -(a[0] & m)))(m, w)
        t[f"{box}->signum({p})I"] = lambda a: (a[0] > 0) - (a[0] < 0)
        t[f"{box}->compare({p}{p})I"] = lambda a: (a[0] > a[1]) - (a[0] < a[1])
        t[f"{box}->compareUnsigned({p}{p})I"] = (lambda m: lambda a: ((a[0] & m) > (a[1] & m)) -
                                                ((a[0] & m) < (a[1] & m)))(m)
        t[f"{box}->divideUnsigned({p}{p}){p}"] = (lambda b, w: lambda a: _dxe_udivrem(a[0], a[1], b, False, w))(bits, w)
        t[f"{box}->remainderUnsigned({p}{p}){p}"] = (lambda b, w: lambda a: _dxe_udivrem(a[0], a[1], b, True, w))(bits,
                                                                                                                 w)
        t[f"{box}->toUnsignedString({p}){S}"] = (lambda m: lambda a: str(_dxe_ints(a[0])[0] & m))(m)
        t[f"{box}->toUnsignedString({p}I){S}"] = (lambda m: lambda a: _dxe_radix(_dxe_ints(a[0])[0] & m, a[1]))(m)
        t[f"{box}->toString({p}I){S}"] = lambda a: _dxe_radix(a[0], a[1])
        t[f"{box}->toBinaryString({p}){S}"] = (lambda m: lambda a: format(_dxe_ints(a[0])[0] & m, "b"))(m)
        t[f"{box}->toOctalString({p}){S}"] = (lambda m: lambda a: format(_dxe_ints(a[0])[0] & m, "o"))(m)
        nm = "Long" if p == "J" else "Int"
        t[f"{box}->parseUnsigned{nm}({S}){p}"] = (lambda b: lambda a: _dxe_parse_u(a[0], 10, b))(bits)
        t[f"{box}->parseUnsigned{nm}({S}I){p}"] = (lambda b: lambda a: _dxe_parse_u(a[0], a[1], b))(bits)
        for op, fn in (("sum", lambda x, y: x + y), ("max", max), ("min", min)):
            t[f"{box}->{op}({p}{p}){p}"] = (lambda fn, w: lambda a: w(fn(*_dxe_ints(a[0], a[1]))))(fn, w)
    t[f"{L}->hashCode(J)I"] = lambda a: _dxe_lhash(_dxe_ints(a[0])[0])
    t[f"{L}->hashCode()I"] = lambda a: _dxe_lhash(_dxe_ints(a[0])[0])
    t[f"{I}->hashCode(I)I"] = t[f"{I}->hashCode()I"] = lambda a: _dxe_ints(a[0])[0]
    t[f"{L}->valueOf(J){L}"] = lambda a: _DxJ(_dxe_ints(a[0])[0])
    t[f"{I}->toUnsignedLong(I)J"] = lambda a: _dxe_ints(a[0])[0] & 0xFFFFFFFF
    t["Ljava/lang/Byte;->toUnsignedInt(B)I"] = t["Ljava/lang/Byte;->toUnsignedLong(B)J"] = lambda a: a[0] & 0xFF
    t["Ljava/lang/Short;->toUnsignedInt(S)I"] = lambda a: a[0] & 0xFFFF
    for mc in (M, "Ljava/lang/StrictMath;"):
        for p, bits, w in (("J", 64, _dxe_w64), ("I", 32, _dxe_w32)):
            t[f"{mc}->abs({p}){p}"] = (lambda w: lambda a: w(abs(a[0])))(w)
            t[f"{mc}->max({p}{p}){p}"] = lambda a: max(a[0], a[1])
            t[f"{mc}->min({p}{p}){p}"] = lambda a: min(a[0], a[1])
            t[f"{mc}->floorDiv({p}{p}){p}"] = (lambda w: lambda a: _dxe_fdiv(a[0], a[1], w))(w)
            t[f"{mc}->floorMod({p}{p}){p}"] = (lambda w: lambda a: _dxe_fmod(a[0], a[1], w))(w)
            for op, fn in (("addExact", lambda x, y: x + y), ("subtractExact", lambda x, y: x - y),
                           ("multiplyExact", lambda x, y: x * y)):
                t[f"{mc}->{op}({p}{p}){p}"] = (lambda fn, b: lambda a: _dxe_exact(fn(*_dxe_ints(a[0], a[1])), b))(fn, bits)
            t[f"{mc}->negateExact({p}){p}"] = (lambda b: lambda a: _dxe_exact(-_dxe_ints(a[0])[0], b))(bits)
            t[f"{mc}->incrementExact({p}){p}"] = (lambda b: lambda a: _dxe_exact(_dxe_ints(a[0])[0] + 1, b))(bits)
            t[f"{mc}->decrementExact({p}){p}"] = (lambda b: lambda a: _dxe_exact(_dxe_ints(a[0])[0] - 1, b))(bits)
        t[f"{mc}->floorDiv(JI)J"] = lambda a: _dxe_fdiv(a[0], a[1], _dxe_w64)
        t[f"{mc}->floorMod(JI)I"] = lambda a: _dxe_fmod(a[0], a[1], _dxe_w32)
        t[f"{mc}->multiplyExact(JI)J"] = lambda a: _dxe_exact(a[0] * a[1], 64)
        t[f"{mc}->toIntExact(J)I"] = lambda a: _dxe_exact(_dxe_ints(a[0])[0], 32)
        t[f"{mc}->multiplyHigh(JJ)J"] = lambda a: _dxe_w64((a[0] * a[1]) >> 64)
        t[f"{mc}->unsignedMultiplyHigh(JJ)J"] = lambda a: _dxe_w64(
            ((a[0] & (1 << 64) - 1) * (a[1] & (1 << 64) - 1)) >> 64)
        t[f"{mc}->multiplyFull(II)J"] = lambda a: a[0] * a[1]
    # String.format / Locale / Arrays
    t[f"{S}->format({S}[Ljava/lang/Object;){S}"] = lambda a: _dxe_ffmt(a[0], a[1])
    t[f"{S}->format(Ljava/util/Locale;{S}[Ljava/lang/Object;){S}"] = lambda a: _dxe_ffmt(a[1], a[2])
    t[f"{S}->formatted([Ljava/lang/Object;){S}"] = lambda a: _dxe_ffmt(a[0], a[1])
    t[f"{S}->toUpperCase(Ljava/util/Locale;){S}"] = lambda a: a[0].upper()
    t[f"{S}->toLowerCase(Ljava/util/Locale;){S}"] = lambda a: a[0].lower()
    t[f"{S}->replace(CC){S}"] = lambda a: a[0].replace(chr(a[1] & 0xFFFF), chr(a[2] & 0xFFFF))
    t[f"{S}->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;){S}"] = \
        lambda a: a[0].replace(_dxe_str(a[1]), _dxe_str(a[2]))
    t[f"{S}->repeat(I){S}"] = lambda a: a[0] * a[1] if 0 <= a[1] <= _DXE_MAX_ARR else (_ for _ in ()).throw(_DxAbort)
    t["Ljava/util/Locale;->getDefault()Ljava/util/Locale;"] = lambda a: "en-US"
    t["Ljava/util/Arrays;->copyOf([Ljava/lang/Object;I)[Ljava/lang/Object;"] = \
        lambda a: _DxArr(list(a[0][:a[1]]) + [None] * max(0, a[1] - len(a[0])))
    for p in "BCSI":
        t[f"Ljava/util/Arrays;->hashCode([{p})I"] = lambda a: _dxe_ahash(a[0])
    t["Ljava/util/Arrays;->hashCode([J)I"] = lambda a: _dxe_ahash(a[0], _dxe_lhash)
    t["Ljava/util/Arrays;->hashCode([Z)I"] = lambda a: _dxe_ahash(a[0], lambda x: 1231 if x else 1237)
    # checksums / digests / BigInteger
    for cls, fn, init in (("Ljava/util/zip/CRC32;", zlib.crc32, 0), ("Ljava/util/zip/Adler32;", zlib.adler32, 1)):
        t[cls + "-><init>()V"] = t[cls + "->reset()V"] = (lambda i: lambda a: a[0].f.__setitem__("v", i))(init)
        for sig in ("I", "[B", "[BII"):
            t[f"{cls}->update({sig})V"] = (lambda fn, i: lambda a: _dxe_chk(a, fn, i))(fn, init)
        t[cls + "->getValue()J"] = (lambda i: lambda a: a[0].f.get("v", i))(init)
    md = "Ljava/security/MessageDigest;"
    t[f"{md}->getInstance({S}){md}"] = _dxe_md_get
    for sig in ("[B", "[BII", "B"):
        t[f"{md}->update({sig})V"] = lambda a: _dxe_md(a, "update")
    t[f"{md}->digest()[B"] = t[f"{md}->digest([B)[B"] = lambda a: _dxe_md(a, "digest")
    t[f"{md}->reset()V"] = lambda a: _dxe_md(a, "reset")
    bi = "Ljava/math/BigInteger;"
    t[bi + "-><init>(I[B)V"] = lambda a: _dxe_bi_init(a, _dxe_bi_mag(a[1], a[2]))
    t[bi + "-><init>([B)V"] = lambda a: _dxe_bi_init(a, int.from_bytes(_dxe_bytes(a[1]), "big", signed=True)
                                                     if a[1] else (_ for _ in ()).throw(_DxAbort))
    t[f"{bi}-><init>({S})V"] = lambda a: _dxe_bi_init(a, _dxe_parse(a[1]))
    t[f"{bi}-><init>({S}I)V"] = lambda a: _dxe_bi_init(a, _dxe_parse(a[1], a[2]))
    t[f"{bi}->valueOf(J){bi}"] = lambda a: _dxe_bi(_dxe_ints(a[0])[0])
    t[f"{bi}->toString(I){S}"] = lambda a: _dxe_radix(_dxe_biv(a[0]), a[1])
    t[f"{bi}->toString(){S}"] = lambda a: str(_dxe_biv(a[0]))
    t[f"{bi}->longValue()J"] = lambda a: _dxe_w64(_dxe_biv(a[0]))
    t[f"{bi}->intValue()I"] = lambda a: _dxe_w32(_dxe_biv(a[0]))
    t[f"{bi}->signum()I"] = lambda a: (_dxe_biv(a[0]) > 0) - (_dxe_biv(a[0]) < 0)
    # kotlin unsigned / text helpers (inline ULong ops compile to these static calls)
    t["Lkotlin/ULong;->constructor-impl(J)J"] = t["Lkotlin/UInt;->constructor-impl(I)I"] = lambda a: a[0]
    t["Lkotlin/ULong;->toString-impl(J)" + S] = lambda a: str(a[0] & (1 << 64) - 1)
    t["Lkotlin/UInt;->toString-impl(I)" + S] = lambda a: str(a[0] & 0xFFFFFFFF)
    uk = "Lkotlin/UnsignedKt;"
    t[uk + "->ulongRemainder-eb3DHEI(JJ)J"] = lambda a: _dxe_udivrem(a[0], a[1], 64, True, _dxe_w64)
    t[uk + "->ulongDivide-eb3DHEI(JJ)J"] = lambda a: _dxe_udivrem(a[0], a[1], 64, False, _dxe_w64)
    t[uk + "->uintRemainder-J1ME1BU(II)I"] = lambda a: _dxe_udivrem(a[0], a[1], 32, True, _dxe_w32)
    t[uk + "->uintDivide-J1ME1BU(II)I"] = lambda a: _dxe_udivrem(a[0], a[1], 32, False, _dxe_w32)
    t[uk + "->ulongCompare(JJ)I"] = t[f"{L}->compareUnsigned(JJ)I"]
    t[uk + "->uintCompare(II)I"] = t[f"{I}->compareUnsigned(II)I"]
    t[uk + "->ulongToString(J)" + S] = t["Lkotlin/ULong;->toString-impl(J)" + S]
    t[f"{uk}->ulongToString(JI){S}"] = lambda a: _dxe_radix(a[0] & (1 << 64) - 1, a[1])
    t[f"Lkotlin/text/UStringsKt;->toString-JSWoG40(JI){S}"] = t[f"{uk}->ulongToString(JI){S}"]
    t[f"Lkotlin/text/UStringsKt;->toString-V7xB4Y4(II){S}"] = lambda a: _dxe_radix(a[0] & 0xFFFFFFFF, a[1])
    t["Lkotlin/text/CharsKt;->checkRadix(I)I"] = lambda a: a[0] if 2 <= a[0] <= 36 else (_ for _ in ()).throw(_DxAbort)
    t[f"Lkotlin/text/StringsKt;->padStart({S}IC){S}"] = lambda a: _dxe_str(a[0]).rjust(a[1], chr(a[2] & 0xFFFF)) \
        if a[1] >= 0 else (_ for _ in ()).throw(_DxAbort)
    t[f"Lkotlin/text/StringsKt;->padEnd({S}IC){S}"] = lambda a: _dxe_str(a[0]).ljust(a[1], chr(a[2] & 0xFFFF)) \
        if a[1] >= 0 else (_ for _ in ()).throw(_DxAbort)
    return t


_DXE_INTR = _dxe_intrinsics()


# --- float / double with exact Java semantics (coverage atlas row 96: SensorMap / mixSensor*, `score > 0.5f`) --------
# A register keeps the IEEE bit pattern as a signed int, like Dalvik (const/high16, const-wide/high16, fill-array-data
# and encoded static values already load bits); every float op computes in double and rounds through struct '<f'
# (exact for + - * / % of float32 operands), conversions saturate (NaN -> 0), cmpl / cmpg bias NaN to -1 / +1.
_FX_F32_INF = 2.0 ** 128 - 2.0 ** 103  # |x| >= this rounds to +-Infinity in float32 (ties-to-even past FLT_MAX)


def _fx_int(v):
    if v.__class__ is not int:
        raise _DxAbort
    return v


def _fx_f(v):
    """float32 bits -> python float."""
    return struct.unpack("<f", struct.pack("<I", _fx_int(v) & 0xFFFFFFFF))[0]


def _fx_d(v):
    """float64 bits -> python float."""
    return struct.unpack("<d", struct.pack("<Q", _fx_int(v) & 0xFFFFFFFFFFFFFFFF))[0]


def _fx_F(x):
    """python float -> float32 bits (round to nearest even, overflow to Infinity, canonical NaN)."""
    if x != x:
        return 0x7FC00000
    if abs(x) >= _FX_F32_INF:
        x = math.copysign(math.inf, x)
    return struct.unpack("<i", struct.pack("<f", x))[0]


def _fx_D(x):
    return 0x7FF8000000000000 if x != x else struct.unpack("<q", struct.pack("<d", x))[0]


def _fx_i2f(v):
    """int/long -> float32 bits, rounded once (float(long) would round to double first)."""
    n = abs(v)
    s = n.bit_length() - 24
    if s > 0:
        q, rem, h = n >> s, n & ((1 << s) - 1), 1 << (s - 1)
        n = (q + (rem > h or rem == h and q & 1)) << s
    return _fx_F(float(-n if v < 0 else n))


def _fx_trunc(x, bits):
    """f2i / d2l: NaN -> 0, saturate at the int/long bounds, else truncate toward zero."""
    if x != x:
        return 0
    lo, hi = -(1 << (bits - 1)), (1 << (bits - 1)) - 1
    return hi if x >= hi else lo if x <= lo else int(x)


def _fx_arith(k, x, y):
    """Java add / sub / mul / div / rem (k 0..4) on doubles: IEEE results where Python would raise."""
    if k == 0:
        return x + y
    if k == 1:
        return x - y
    if k == 2:
        return x * y
    if k == 3:
        if y == 0:
            return math.nan if x != x or x == 0 else math.copysign(math.inf, x) * math.copysign(1.0, y)
        return x / y
    if k == 4:
        if x != x or y != y or math.isinf(x) or y == 0:
            return math.nan
        return x if math.isinf(y) else math.fmod(x, y)
    raise _DxAbort


def _fx_binop(k, a, b, wide):
    if wide:
        return _fx_D(_fx_arith(k, _fx_d(a), _fx_d(b)))
    return _fx_F(_fx_arith(k, _fx_f(a), _fx_f(b)))


def _fx_unop(op, v):
    """neg-float .. double-to-float (0x7F-0x8C minus the int/long ones): (value, wide result)."""
    if op == 0x7F:
        return _dxe_w32(v ^ 0x80000000), False
    if op == 0x80:
        return _dxe_w64(v ^ (1 << 63)), True
    if op in (0x82, 0x85):
        return _fx_i2f(v), False
    if op in (0x83, 0x86):
        return _fx_D(float(v)), True
    if op in (0x87, 0x88):
        return _fx_trunc(_fx_f(v), 32 if op == 0x87 else 64), op == 0x88
    if op in (0x8A, 0x8B):
        return _fx_trunc(_fx_d(v), 32 if op == 0x8A else 64), op == 0x8B
    if op == 0x89:
        return _fx_D(_fx_f(v)), True
    if op == 0x8C:
        return _fx_F(_fx_d(v)), False
    raise _DxAbort


def _fx_cmp(op, a, b):
    """cmpl-float / cmpg-float / cmpl-double / cmpg-double (0x2D-0x30)."""
    cv = _fx_d if op >= 0x2F else _fx_f
    x, y = cv(a), cv(b)
    if x != x or y != y:
        return -1 if op in (0x2D, 0x2F) else 1
    return (x > y) - (x < y)


def _fx_minmax(x, y, mx):
    if x != x or y != y:
        return math.nan
    if x == y == 0:  # Math.min(0.0, -0.0) = -0.0, Math.max(-0.0, 0.0) = 0.0
        return x if (math.copysign(1.0, x) > 0) == mx else y
    return max(x, y) if mx else min(x, y)


def _fx_pow(x, y):
    if y == 0:
        return 1.0
    if x != x or y != y or abs(x) == 1 and math.isinf(y):
        return math.nan
    odd = not math.isinf(y) and y == int(y) and int(y) & 1
    if x == 0 and y < 0:
        return -math.inf if odd and math.copysign(1.0, x) < 0 else math.inf
    try:
        return math.pow(x, y)
    except OverflowError:
        return -math.inf if x < 0 and odd else math.inf
    except ValueError:
        return math.nan


def _fx_integral(x, fn):
    """Math.floor / ceil / rint: NaN, +-Infinity and +-0.0 pass through; a zero result keeps the argument's sign."""
    if x != x or math.isinf(x) or x == 0:
        return x
    return math.copysign(float(fn(x)), x)


def _fx_round(x, bits):
    """Math.round: floor(x + 1/2) computed exactly, NaN -> 0, saturating."""
    if x != x or math.isinf(x):
        return _fx_trunc(x, bits)
    r = math.floor(x)
    r += x - r >= 0.5
    return max(-(1 << (bits - 1)), min((1 << (bits - 1)) - 1, r))


def _fx_jstr(x, single):
    """Float.toString / Double.toString: shortest round-trip digits, plain in [1e-3, 1e7), else d.dddE<n>."""
    if x != x:
        return "NaN"
    if math.isinf(x):
        return "Infinity" if x > 0 else "-Infinity"
    if x == 0:
        return "-0.0" if math.copysign(1.0, x) < 0 else "0.0"
    for p in range(1, 18):
        s = "%.*e" % (p - 1, x)
        if (_fx_F(float(s)) == _fx_F(x)) if single else float(s) == x:
            break
    mant, e = s.lstrip("-").split("e")
    e, dg = int(e), mant.replace(".", "").rstrip("0") or "0"
    if 1e-3 <= abs(x) < 1e7:
        out = dg[:e + 1].ljust(e + 1, "0") + "." + (dg[e + 1:] or "0") if e >= 0 else "0." + "0" * (-e - 1) + dg
    else:
        out = dg[0] + "." + (dg[1:] or "0") + "E" + str(e)
    return ("-" if x < 0 else "") + out


def _fx_parse(s, single):
    """Float.parseFloat / Double.parseDouble (decimal forms; a hex float or junk aborts like NumberFormatException).
    parseFloat rounds the exact decimal straight to float32 (decimal -> double -> float could double-round)."""
    from fractions import Fraction
    s = _dxe_str(s).strip("".join(map(chr, range(33))))
    if s[-1:] in ("f", "F", "d", "D"):
        s = s[:-1]
    m = re.fullmatch(r"([+-]?)(?:(NaN)|(Infinity)|((?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?))", s)
    if not m:
        raise _DxAbort
    if not m.group(4):
        x = math.nan if m.group(2) else math.copysign(math.inf, -1.0 if m.group(1) == "-" else 1.0)
        return _fx_F(x) if single else _fx_D(x)
    if not single:
        return _fx_D(float(s))
    fr = abs(Fraction(m.group(4)))
    try:
        b = _fx_F(float(fr)) & 0x7FFFFFFF
    except OverflowError:
        b = 0x7F800000
    best = None
    for c in (b - 1, b, b + 1):
        if 0 <= c <= 0x7F800000:
            key = (abs((Fraction(_fx_f(c)) if c < 0x7F800000 else Fraction(2 ** 128)) - fr), c & 1)
            best = min(best or (key, c), (key, c))
    return _dxe_w32(best[1] | (0x80000000 if m.group(1) == "-" else 0))


def _dxe_intr_float():
    F, D, S, f, d = "Ljava/lang/Float;", "Ljava/lang/Double;", "Ljava/lang/String;", _fx_f, _fx_d
    t = {}
    t[F + "->floatToRawIntBits(F)I"] = t[F + "->intBitsToFloat(I)F"] = lambda a: _dxe_w32(_fx_int(a[0]))
    t[F + "->floatToIntBits(F)I"] = lambda a: 0x7FC00000 if f(a[0]) != f(a[0]) else _dxe_w32(a[0])
    t[D + "->doubleToRawLongBits(D)J"] = t[D + "->longBitsToDouble(J)D"] = lambda a: _dxe_w64(_fx_int(a[0]))
    t[D + "->doubleToLongBits(D)J"] = lambda a: 0x7FF8000000000000 if d(a[0]) != d(a[0]) else _dxe_w64(a[0])
    for box, P, cv, back, canon, w, single in ((F, "F", f, _fx_F, 0x7FC00000, _dxe_w32, True),
                                              (D, "D", d, _fx_D, 0x7FF8000000000000, _dxe_w64, False)):
        def cmp(a, cv=cv, canon=canon, w=w):  # Java's own: < / >, then the canonical bits (-0.0 < 0.0, NaN last)
            x, y = cv(a[0]), cv(a[1])
            if x < y or x > y:
                return -1 if x < y else 1
            bx, by = (canon if v != v else w(r) for v, r in ((x, a[0]), (y, a[1])))
            return (bx > by) - (bx < by)
        t[f"{box}->compare({P}{P})I"] = cmp
        t[f"{box}->isNaN({P})Z"] = lambda a, cv=cv: int(cv(a[0]) != cv(a[0]))
        t[f"{box}->isInfinite({P})Z"] = lambda a, cv=cv: int(math.isinf(cv(a[0])))
        t[f"{box}->isFinite({P})Z"] = lambda a, cv=cv: int(math.isfinite(cv(a[0])))
        t[f"{box}->sum({P}{P}){P}"] = lambda a, cv=cv, back=back: back(cv(a[0]) + cv(a[1]))
        t[f"{box}->max({P}{P}){P}"] = lambda a, cv=cv, back=back: back(_fx_minmax(cv(a[0]), cv(a[1]), True))
        t[f"{box}->min({P}{P}){P}"] = lambda a, cv=cv, back=back: back(_fx_minmax(cv(a[0]), cv(a[1]), False))
        t[f"{box}->toString({P}){S}"] = t[f"{S}->valueOf({P}){S}"] = \
            lambda a, cv=cv, single=single: _fx_jstr(cv(a[0]), single)
        for sb in ("Ljava/lang/StringBuilder;", "Ljava/lang/StringBuffer;"):
            t[f"{sb}->append({P}){sb}"] = \
                lambda a, cv=cv, single=single: _dxe_sb_append((a[0], _fx_jstr(cv(a[1]), single)))
        t[f"{box}->parse{'Float' if single else 'Double'}({S}){P}"] = lambda a, single=single: _fx_parse(a[0], single)
    for m in ("Ljava/lang/Math;", "Ljava/lang/StrictMath;"):
        t[f"{m}->abs(F)F"] = lambda a: _dxe_w32(_fx_int(a[0]) & 0x7FFFFFFF)
        t[f"{m}->abs(D)D"] = lambda a: _fx_int(a[0]) & 0x7FFFFFFFFFFFFFFF
        t[f"{m}->abs(I)I"] = lambda a: _dxe_w32(abs(_fx_int(a[0])))
        t[f"{m}->abs(J)J"] = lambda a: _dxe_w64(abs(_fx_int(a[0])))
        for P, cv, back in (("F", f, _fx_F), ("D", d, _fx_D)):
            t[f"{m}->max({P}{P}){P}"] = lambda a, cv=cv, back=back: back(_fx_minmax(cv(a[0]), cv(a[1]), True))
            t[f"{m}->min({P}{P}){P}"] = lambda a, cv=cv, back=back: back(_fx_minmax(cv(a[0]), cv(a[1]), False))
            t[f"{m}->signum({P}){P}"] = lambda a, cv=cv, back=back: back(
                (lambda x: x if x != x or x == 0 else math.copysign(1.0, x))(cv(a[0])))
        for P in ("I", "J"):
            t[f"{m}->max({P}{P}){P}"] = lambda a: max(_fx_int(a[0]), _fx_int(a[1]))
            t[f"{m}->min({P}{P}){P}"] = lambda a: min(_fx_int(a[0]), _fx_int(a[1]))
        t[f"{m}->sqrt(D)D"] = lambda a: _fx_D((lambda x: math.nan if x < 0 else math.sqrt(x))(d(a[0])))
        t[f"{m}->floor(D)D"] = lambda a: _fx_D(_fx_integral(d(a[0]), math.floor))
        t[f"{m}->ceil(D)D"] = lambda a: _fx_D(_fx_integral(d(a[0]), math.ceil))
        t[f"{m}->rint(D)D"] = lambda a: _fx_D(_fx_integral(d(a[0]), round))
        t[f"{m}->pow(DD)D"] = lambda a: _fx_D(_fx_pow(d(a[0]), d(a[1])))
        t[f"{m}->round(F)I"] = lambda a: _fx_round(f(a[0]), 32)
        t[f"{m}->round(D)J"] = lambda a: _fx_round(d(a[0]), 64)
    return t


for _k, _v in _dxe_intr_float().items():
    _DXE_INTR.setdefault(_k, _v)
_DXE_SFIELDS = {"Ljava/nio/charset/StandardCharsets;->UTF_8": "utf-8", "Ljava/nio/charset/StandardCharsets;->US_ASCII":
                "us-ascii", "Ljava/nio/charset/StandardCharsets;->ISO_8859_1": "iso-8859-1",
                **{f"Ljava/util/Locale;->{k}": "en-US" for k in ("US", "ROOT", "ENGLISH", "UK")}}


class _DxDex:
    """Index of one dex for the evaluator: method/field/type refs as strings, code items by method ref, <clinit>s and
    static values by class."""

    def __init__(self, d):
        u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
        self.d = d
        (n_str, o_str, n_typ, o_typ, n_pro, o_pro, n_fld, o_fld, n_met, o_met, n_cls, o_cls) = \
            struct.unpack_from("<12I", d, 0x38)
        if n_str > 1 << 22 or n_met > 1 << 20 or n_cls > 1 << 20 or o_cls + 32 * n_cls > len(d) \
                or o_met + 8 * n_met > len(d) or o_fld + 8 * n_fld > len(d) or o_typ + 4 * n_typ > len(d):
            raise ValueError("dex")
        self.n_str, self.o_str, self.o_typ, self.n_typ = n_str, o_str, o_typ, n_typ
        self.o_pro, self.o_fld, self.o_met, self.n_fld, self.n_met = o_pro, o_fld, o_met, n_fld, n_met
        self._s, self._m, self._f = {}, {}, {}
        self.code, self.clinit, self.svals, self.sfields = {}, {}, {}, {}
        self.order, self.coff = [], {}
        for c in range(n_cls):
            base = o_cls + 32 * c
            ct = self.typ(u32(base))
            cdata, sval = u32(base + 24), u32(base + 28)
            if not cdata:
                continue
            i = cdata
            sf, i = _uleb(d, i)
            inf, i = _uleb(d, i)
            dm, i = _uleb(d, i)
            vm, i = _uleb(d, i)
            fi, sfl = 0, []
            for _ in range(sf):
                x, i = _uleb(d, i)
                fi += x
                _, i = _uleb(d, i)
                sfl.append(fi)
            for _ in range(inf):
                _, i = _uleb(d, i)
                _, i = _uleb(d, i)
            self.sfields[ct] = (sfl, sval)
            for cnt in (dm, vm):
                mi = 0
                for _ in range(cnt):
                    x, i = _uleb(d, i)
                    mi += x
                    acc, i = _uleb(d, i)
                    code, i = _uleb(d, i)
                    if code and code + 16 <= len(d) and mi < n_met:
                        nreg, nin = struct.unpack_from("<HH", d, code)
                        n_ins = u32(code + 12)
                        ref = self.mref(mi)
                        self.code[ref] = (nreg, nin, d[code + 16:code + 16 + 2 * n_ins], acc)
                        self.coff[ref] = code
                        if ref.endswith("-><clinit>()V"):
                            self.clinit[ct] = ref
                        elif not _DXE_LIB.match(ct):
                            self.order.append(ref)

    def s(self, i):
        r = self._s.get(i)
        if r is None and i < self.n_str:
            _, j = _uleb(self.d, struct.unpack_from("<I", self.d, self.o_str + 4 * i)[0])
            e = self.d.find(b"\0", j)
            raw = self.d[j:e]
            try:
                r = raw.decode("utf-8")
            except UnicodeDecodeError:  # MUTF-8: surrogate pairs / embedded NUL as 2-3 byte sequences
                try:
                    r = raw.replace(b"\xc0\x80", b"\0").decode("utf-8", "surrogatepass").encode(
                        "utf-16", "surrogatepass").decode("utf-16", "replace")
                except UnicodeError:
                    r = raw.decode("utf-8", "replace")
            self._s[i] = r
        return r

    def typ(self, i):
        return self.s(struct.unpack_from("<I", self.d, self.o_typ + 4 * i)[0]) if i < self.n_typ else "?"

    def mref(self, mi):
        r = self._m.get(mi)
        if r is None:
            c, p, n = struct.unpack_from("<HHI", self.d, self.o_met + 8 * mi)
            so, rt, po = struct.unpack_from("<III", self.d, self.o_pro + 12 * p)
            ps = ""
            if po:
                k = struct.unpack_from("<I", self.d, po)[0]
                ps = "".join(self.typ(t) for t in struct.unpack_from(f"<{min(k, 255)}H", self.d, po + 4))
            r = self._m[mi] = f"{self.typ(c)}->{self.s(n)}({ps}){self.typ(rt)}"
        return r

    def fref(self, fi):
        r = self._f.get(fi)
        if r is None:
            c, t, n = struct.unpack_from("<HHI", self.d, self.o_fld + 8 * fi)
            r = self._f[fi] = (self.typ(c), f"{self.typ(c)}->{self.s(n)}", self.typ(t))
        return r


def _dxe_enum_call(ref, raw):
    """java.lang.Enum / array members an in-dex enum inherits (coverage atlas row 89): Enum.<init>(name, ordinal) tags
    the _DxObj, ordinal() / name() / toString() / compareTo() / equals() read it back, values()'s `[LE;->clone()`
    copies $VALUES -- enough for an enum <clinit>, javac's `<Outer>$1.$SwitchMap$<pkg>$<Enum>` / kotlinc's
    `<Outer>$WhenMappings.$EnumSwitchMapping$N` <clinit> and the `aget map[e.ordinal()]` before a packed-switch.
    _DXE_UNK when the call is none of these (the caller aborts)."""
    name = ref[ref.find("->") + 2:ref.find("(")]
    o = raw[0] if raw else None
    if ref == "Ljava/lang/Enum;-><init>(Ljava/lang/String;I)V":
        if not isinstance(o, _DxObj) or len(raw) < 3 or not isinstance(raw[2], int):
            return _DXE_UNK
        o.f["$name"], o.f["$ordinal"] = raw[1], raw[2]
        return None
    if ref.startswith("[") and name == "clone" and isinstance(o, _DxArr) and len(raw) == 1:
        c = _DxArr(o)
        c.t = getattr(o, "t", "")
        return c
    if not isinstance(o, _DxObj) or "$ordinal" not in o.f:
        return _DXE_UNK
    if name == "ordinal" and len(raw) == 1:
        return o.f["$ordinal"]
    if name in ("name", "toString") and len(raw) == 1 and ref.endswith(")Ljava/lang/String;"):
        return o.f["$name"]
    if name == "compareTo" and len(raw) == 2 and isinstance(raw[1], _DxObj) and "$ordinal" in raw[1].f:
        return o.f["$ordinal"] - raw[1].f["$ordinal"]
    if name == "equals" and len(raw) == 2:
        return int(o is raw[1])
    if name == "hashCode" and len(raw) == 1:
        return id(o) & 0x7FFFFFFF
    return _DXE_UNK


def _dxe_params(ref):
    """Parameter descriptors of a method ref string."""
    p = ref[ref.index("(") + 1:ref.index(")")]
    return re.findall(r"\[*(?:L[^;]+;|[ZBSCIJFD])", p)


class _DxVM:
    max_steps = _DXE_STEPS
    inst_of = False  # instance-of: exact in-dex class match (only _KcoVM turns it on)
    trace = None  # switch keys taken, in order (only _AdsVM records them)
    exc = False  # model `throw` + runtime faults through the try/catch tables (only _ExcVM turns it on)

    def __init__(self, dx, deadline):
        self.dx, self.deadline, self.statics, self.inited, self.seen = dx, deadline, {}, set(), []
        self.steps = 0

    def note(self, v):
        if isinstance(v, str) and len(v) >= 8:
            self.seen.append(v)
        return v

    def init_class(self, ct):
        if ct in self.inited:
            return
        self.inited.add(ct)
        sfl, sval = self.dx.sfields.get(ct, ((), 0))
        d = self.dx.d
        for fi in sfl:
            t = self.dx.fref(fi)[2]
            self.statics[self.dx.fref(fi)[1]] = 0 if t in "ZBSCIJFD" else None
        if sval:
            try:
                n, i = _uleb(d, sval)
                for k in range(min(n, len(sfl))):
                    t = d[i]
                    i += 1
                    vt, arg = t & 0x1F, t >> 5
                    raw = d[i:i + arg + 1]
                    v = None
                    if vt in (0x00, 0x02, 0x04, 0x06):
                        v = int.from_bytes(raw, "little", signed=True)
                    elif vt == 0x03:
                        v = int.from_bytes(raw, "little")
                    elif vt in (0x10, 0x11):  # float / double: bytes are the high end of the bit pattern
                        v = int.from_bytes(raw, "little") << 8 * ((4 if vt == 0x10 else 8) - len(raw))
                        v = _dxe_w32(v) if vt == 0x10 else _dxe_w64(v)
                    elif vt == 0x17:
                        v = self.dx.s(int.from_bytes(raw, "little"))
                    elif vt == 0x1F:
                        v = arg
                    elif vt in (0x1C, 0x1D):
                        break
                    if vt not in (0x1E, 0x1F):
                        i += arg + 1
                    if v is not None:
                        self.statics[self.dx.fref(sfl[k])[1]] = v
            except (IndexError, ValueError):
                pass
        ref = self.dx.clinit.get(ct)
        if ref:
            saved, self.steps = self.steps, 0
            try:
                self.run(ref, [], 1)
            except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError):
                pass
            self.steps = saved

    def const_class(self, t):
        return _DXE_UNK

    def new_instance(self, t):
        if t in _DXE_NEW:  # CRC32 / Adler32 / BigInteger: state lives in .f, filled by their _DXE_INTR <init>
            return _DxObj(t)
        raise _DxAbort

    def dyn(self, op, ins, p, r, depth):
        raise _DxAbort  # invoke-polymorphic / invoke-custom: only method_handle_scan's VM runs them

    def invoke(self, ref, raw, depth):
        intr = _DXE_INTR.get(ref)
        if intr is not None or ref in self.dx.code:
            ps = _dxe_params(ref)
            static = len(raw) == sum(2 if p in "JD" else 1 for p in ps)
            args, i = [], 0
            if not static:
                args.append(raw[0])
                i = 1
            for p in ps:
                args.append(raw[i] if i < len(raw) else None)
                i += 2 if p in "JD" else 1
            if intr is not None:
                if any(a is _DXE_UNK for a in args):
                    raise _DxAbort
                return self.note(intr(args))
            if depth >= _DXE_DEPTH:
                raise _DxAbort
            self.init_class(ref.split("->")[0])
            return self.note(self.run(ref, raw, depth + 1))
        v = _dxe_enum_call(ref, raw)
        if v is _DXE_UNK:
            raise _DxAbort
        return self.note(v)

    def handler(self, ref, pc, types):
        """Catch-handler address (code units) covering `pc` in `ref` for an exception of `types`; None when uncaught."""
        d, code = self.dx.d, self.dx.coff.get(ref)
        if code is None:
            return None
        n_try, n_ins = struct.unpack_from("<H", d, code + 6)[0], struct.unpack_from("<I", d, code + 12)[0]
        tb = code + 16 + 2 * n_ins + 2 * (n_ins & 1)
        lb = tb + 8 * n_try
        for k in range(min(n_try, 4096)):
            start, cnt, hoff = struct.unpack_from("<IHH", d, tb + 8 * k)
            if not start <= pc < start + cnt:
                continue
            i, size = lb + hoff, 0
            sh = 0
            while True:
                b = d[i]
                i += 1
                size |= (b & 0x7F) << sh
                sh += 7
                if b < 0x80:
                    break
            if b & 0x40:
                size -= 1 << sh
            for _ in range(abs(size)):
                ti, i = _uleb(d, i)
                addr, i = _uleb(d, i)
                if self.dx.typ(ti) in types:
                    return addr
            if size <= 0:
                return _uleb(d, i)[0]
            return None
        return None

    def exc_types(self, t):
        """`t` and its supertypes, in-dex superclasses first, then java.lang's tree; () when `t` is not a Throwable (an
        unknown framework *Exception / *Error type hangs under Exception / Error)."""
        sup = _dxx_supers(self.dx)
        out = [t]
        for _ in range(24):
            q = sup.get(t) or _DXX_TREE.get(t)
            if q is None and t not in ("Ljava/lang/Throwable;", "Ljava/lang/Object;"):
                q = "Ljava/lang/Error;" if t.endswith("Error;") else "Ljava/lang/Exception;" if t.endswith(
                    "Exception;") else None
            if q is None or q in out:
                break
            out.append(t := q)
        return tuple(out) if out[-1] == "Ljava/lang/Throwable;" else ()

    def exc_new(self, t, msg=None):
        o = _DxObj(t)
        if msg is not None:
            o.f["$msg"] = msg
        return _DxExc(o, self.exc_types(t))

    def fault(self, op, ins, p, r):
        """The exception op at `p` throws with these registers (an _DxExc), or None when it runs normally."""
        b1 = ins[p + 1]
        A, B = b1 & 0xF, b1 >> 4
        npe = "Ljava/lang/NullPointerException;"
        null = lambda v: v is None or v.__class__ is int and v == 0  # noqa: E731 - `const/4 vX, 0` is also null
        if op == 0x27:
            v = r[b1]
            if null(v):
                return self.exc_new(npe)
            if isinstance(v, _DxThrow):  # rethrow of a framework exception bound by move-exception
                return v
            ts = self.exc_types(v.t) if isinstance(v, _DxObj) else ()
            if not ts:
                raise _DxAbort
            return _DxExc(v, ts)
        if op == 0x21 or 0x52 <= op <= 0x5F:
            return self.exc_new(npe) if null(r[B]) else None
        if 0x44 <= op <= 0x51:
            a_, ix = r[ins[p + 2]], r[ins[p + 3]]
            if null(a_):
                return self.exc_new(npe)
            if isinstance(a_, list) and isinstance(ix, int) and not 0 <= ix < len(a_):
                return self.exc_new("Ljava/lang/ArrayIndexOutOfBoundsException;",
                                    f"length={len(a_)}; index={ix}")
            return None
        if op in _DXX_DIV:
            dv = (r[ins[p + 3]] if op < 0xB0 else r[B] if op < 0xD0 else struct.unpack_from("<h", ins, p + 2)[0]
                  if op < 0xD8 else (ins[p + 3] ^ 0x80) - 0x80)
            return self.exc_new("Ljava/lang/ArithmeticException;", "divide by zero") if dv == 0 else None
        cnt = B if op <= 0x72 else b1
        if cnt:
            rcv = r[struct.unpack_from("<H", ins, p + 4)[0] & (0xF if op <= 0x72 else 0xFFFF)]
            if null(rcv):
                return self.exc_new(npe)
        return None

    def run(self, ref, raw_args, depth=0):  # noqa: C901 - one dispatch loop
        nreg, nin, ins, _ = self.dx.code[ref]
        n_ins = len(ins) // 2
        r = [None] * nreg
        r[nreg - nin:nreg - nin + len(raw_args)] = raw_args[:nin]
        h16 = lambda p: struct.unpack_from("<h", ins, p)[0]  # noqa: E731
        u16 = lambda p: struct.unpack_from("<H", ins, p)[0]  # noqa: E731
        dx, last, pc, exc = self.dx, None, 0, self.exc
        while True:
            self.steps += 1
            if self.steps > self.max_steps or (self.steps & 1023 == 0 and time.time() > self.deadline):
                raise _DxAbort
            if pc >= n_ins:
                raise _DxAbort
            p = 2 * pc
            op, b1 = ins[p], ins[p + 1]
            A, B = b1 & 0xF, b1 >> 4
            w = _DOP_W[op]
            if exc and op in _DXX_OPS:
                e = self.fault(op, ins, p, r)
                if e is not None:
                    h = self.handler(ref, pc, e.types)
                    if h is None:
                        raise e
                    last, pc = e, h
                    continue
            if op == 0x00:
                if b1:
                    raise _DxAbort  # fell into a payload
            elif op in (0x01, 0x04, 0x07):
                r[A] = r[B]
                if op == 0x04:
                    r[A + 1] = r[B + 1]
            elif op in (0x02, 0x05, 0x08):
                s = u16(p + 2)
                r[b1] = r[s]
                if op == 0x05:
                    r[b1 + 1] = r[s + 1]
            elif op in (0x03, 0x06, 0x09):
                a_, s = u16(p + 2), u16(p + 4)
                r[a_] = r[s]
                if op == 0x06:
                    r[a_ + 1] = r[s + 1]
            elif op in (0x0A, 0x0C):
                r[b1] = last
            elif op == 0x0B:
                r[b1], r[b1 + 1] = last, None
            elif op == 0x0E:
                return None
            elif op in (0x0F, 0x10, 0x11):
                return r[b1]
            elif op == 0x12:
                r[A] = (B ^ 8) - 8
            elif op == 0x13:
                r[b1] = h16(p + 2)
            elif op == 0x14:
                r[b1] = struct.unpack_from("<i", ins, p + 2)[0]
            elif op == 0x15:
                r[b1] = _dxe_w32(u16(p + 2) << 16)
            elif op == 0x16:
                r[b1], r[b1 + 1] = h16(p + 2), None
            elif op == 0x17:
                r[b1], r[b1 + 1] = struct.unpack_from("<i", ins, p + 2)[0], None
            elif op == 0x18:
                r[b1], r[b1 + 1] = struct.unpack_from("<q", ins, p + 2)[0], None
            elif op == 0x19:
                r[b1], r[b1 + 1] = _dxe_w64(h16(p + 2) << 48), None
            elif op == 0x1A:
                r[b1] = dx.s(u16(p + 2))
            elif op == 0x1B:
                r[b1] = dx.s(struct.unpack_from("<I", ins, p + 2)[0])
            elif op == 0x1C:
                r[b1] = self.const_class(dx.typ(u16(p + 2)))
            elif op in (0x1D, 0x1E, 0x1F):
                pass
            elif op == 0x21:
                if not isinstance(r[B], list):
                    raise _DxAbort
                r[A] = len(r[B])
            elif op == 0x22:
                t = dx.typ(u16(p + 2))
                if t in ("Ljava/lang/StringBuilder;", "Ljava/lang/StringBuffer;"):
                    r[b1] = _DxSB()
                elif t == "Ljava/lang/String;" or t in ("Ljava/util/Base64$Decoder;",):
                    r[b1] = _DxObj(t)
                elif t in dx.sfields:
                    self.init_class(t)
                    r[b1] = _DxObj(t)
                else:
                    r[b1] = self.new_instance(t)
            elif op == 0x23:
                n, t = r[B], dx.typ(u16(p + 2))
                if not isinstance(n, int) or not 0 <= n <= _DXE_MAX_ARR:
                    raise _DxAbort
                a_ = _DxArr([0] * n if len(t) == 2 and t[1] in "ZBSCIJFD" else [None] * n)
                a_.t = t[1:]
                r[A] = a_
            elif op in (0x24, 0x25):
                t, cnt = dx.typ(u16(p + 2)), (B if op == 0x24 else b1)
                if op == 0x24:
                    g = u16(p + 4)
                    regs = [g & 0xF, (g >> 4) & 0xF, (g >> 8) & 0xF, g >> 12, A][:cnt]
                else:
                    regs = range(u16(p + 4), u16(p + 4) + cnt)
                last = _DxArr(r[x] for x in regs)
                last.t = t[1:]
            elif op == 0x26:
                q = 2 * (pc + struct.unpack_from("<i", ins, p + 2)[0])
                a_ = r[b1]
                if not isinstance(a_, _DxArr) or q < 0 or ins[q:q + 2] != b"\x00\x03":
                    raise _DxAbort
                ew, n = struct.unpack_from("<HI", ins, q + 2)
                if ew not in (1, 2, 4, 8) or n > len(a_) or q + 8 + ew * n > len(ins):
                    raise _DxAbort
                sg = a_.t != "C"
                for k in range(n):
                    a_[k] = int.from_bytes(ins[q + 8 + ew * k:q + 8 + ew * (k + 1)], "little", signed=sg)
            elif op == 0x0D and isinstance(last, _DxThrow):  # only reached via handler(): base VM never throws
                r[b1] = last if last.obj is None else last.obj
            elif op == 0x20 and self.inst_of:
                v = r[B]
                r[A] = int(isinstance(v, _DxObj) and v.t == dx.typ(u16(p + 2)))
            elif op == 0x27 or op == 0x0D or op == 0x20:
                raise _DxAbort
            elif op in (0x28, 0x29, 0x2A):
                off = (b1 ^ 0x80) - 0x80 if op == 0x28 else (h16(p + 2) if op == 0x29 else
                                                              struct.unpack_from("<i", ins, p + 2)[0])
                if off == 0 and op != 0x2A:
                    raise _DxAbort
                pc += off
                continue
            elif op in (0x2B, 0x2C):
                q = 2 * (pc + struct.unpack_from("<i", ins, p + 2)[0])
                v = r[b1]
                if not isinstance(v, int) or q < 0 or q + 4 > len(ins):
                    raise _DxAbort
                if self.trace is not None and len(self.trace) < 256:
                    self.trace.append(v)
                n = u16(q + 2)
                if op == 0x2B and ins[q:q + 2] == b"\x00\x01":
                    k0 = struct.unpack_from("<i", ins, q + 4)[0]
                    if 0 <= v - k0 < n:
                        pc += struct.unpack_from("<i", ins, q + 8 + 4 * (v - k0))[0]
                        continue
                elif op == 0x2C and ins[q:q + 2] == b"\x00\x02":
                    keys = struct.unpack_from(f"<{n}i", ins, q + 4)
                    if v in keys:
                        pc += struct.unpack_from("<i", ins, q + 4 + 4 * n + 4 * keys.index(v))[0]
                        continue
                else:
                    raise _DxAbort
            elif 0x2D <= op <= 0x30:
                r[b1] = _fx_cmp(op, r[ins[p + 2]], r[ins[p + 3]])
            elif op == 0x31:
                x, y = r[ins[p + 2]], r[ins[p + 3]]
                if not isinstance(x, int) or not isinstance(y, int):
                    raise _DxAbort
                r[b1] = (x > y) - (x < y)
            elif 0x32 <= op <= 0x3D:
                if op <= 0x37:
                    x, y, off = r[A], r[B], h16(p + 2)
                else:
                    x, y, off = r[b1], 0, h16(p + 2)
                    if not isinstance(x, int):
                        x = 0 if x is None else 1
                if x is _DXE_UNK or y is _DXE_UNK:
                    raise _DxAbort
                k = (op - 0x32) % 6
                if k == 0:
                    c = x is y if not isinstance(x, int) else x == y
                elif k == 1:
                    c = x is not y if not isinstance(x, int) else x != y
                else:
                    if not isinstance(x, int) or not isinstance(y, int):
                        raise _DxAbort
                    c = (x < y, x >= y, x > y, x <= y)[k - 2]
                if c:
                    if off == 0:
                        raise _DxAbort
                    pc += off
                    continue
            elif 0x44 <= op <= 0x51:
                a_, ix = r[ins[p + 2]], r[ins[p + 3]]
                if not isinstance(a_, list) or not isinstance(ix, int) or not 0 <= ix < len(a_):
                    raise _DxAbort
                if op <= 0x4A:
                    r[b1] = a_[ix]
                    if op == 0x45:
                        r[b1 + 1] = None
                else:
                    v = r[b1]
                    if op in (0x4B, 0x4C, 0x4E, 0x4F, 0x50, 0x51) and not isinstance(v, int):
                        raise _DxAbort
                    a_[ix] = ((v + 0x80) & 0xFF) - 0x80 if op == 0x4F else (
                        v & 0xFFFF if op == 0x50 else (((v + 0x8000) & 0xFFFF) - 0x8000 if op == 0x51 else v))
            elif 0x52 <= op <= 0x5F:
                o, f = r[B], dx.fref(u16(p + 2))
                if not isinstance(o, _DxObj):
                    raise _DxAbort
                if op <= 0x58:
                    r[A] = o.f.get(f[1], 0 if f[2] in "ZBSCIJFD" else None)
                else:
                    o.f[f[1]] = r[A]
            elif 0x60 <= op <= 0x6D:
                ct, fk, ft = dx.fref(u16(p + 2))
                if fk not in self.statics:
                    if ct in dx.sfields:
                        self.init_class(ct)
                    elif fk in _DXE_SFIELDS:
                        self.statics[fk] = _DXE_SFIELDS[fk]
                if op <= 0x66:
                    if fk not in self.statics:
                        raise _DxAbort
                    r[b1] = self.statics[fk]
                    if op == 0x61:
                        r[b1 + 1] = None
                else:
                    self.statics[fk] = r[b1]
            elif 0x6E <= op <= 0x78 and op != 0x73:
                ref2 = dx.mref(u16(p + 2))
                if op <= 0x72:
                    g = u16(p + 4)
                    regs = [g & 0xF, (g >> 4) & 0xF, (g >> 8) & 0xF, g >> 12, A][:B]
                else:
                    regs = range(u16(p + 4), u16(p + 4) + b1)
                raw = [r[x] for x in regs]
                if ref2.endswith("-><init>" + ref2[ref2.index("("):]) and ref2.startswith(
                        ("Ljava/lang/String;", "Ljava/lang/StringBuilder;", "Ljava/lang/StringBuffer;")):
                    new = self.invoke(ref2, raw, depth)
                    old = raw[0]
                    for k in range(nreg):
                        if r[k] is old:
                            r[k] = new
                    last = None
                else:
                    try:
                        last = self.invoke(ref2, raw, depth)
                    except _DxThrow as e:  # raised by a modelled framework call (clean_device_scan's VM only)
                        h = self.handler(ref, pc, e.types)
                        if h is None:
                            raise
                        last, pc = e, h
                        continue
            elif 0x7B <= op <= 0x8F:
                v = r[B]
                if not isinstance(v, int):
                    raise _DxAbort
                if op == 0x7B:
                    r[A] = _dxe_w32(-v)
                elif op == 0x7C:
                    r[A] = ~v
                elif op == 0x7D:
                    r[A], r[A + 1] = _dxe_w64(-v), None
                elif op == 0x7E:
                    r[A], r[A + 1] = ~v, None
                elif op == 0x81:
                    r[A], r[A + 1] = v, None
                elif op == 0x84:
                    r[A] = _dxe_w32(v)
                elif op == 0x8D:
                    r[A] = ((v + 0x80) & 0xFF) - 0x80
                elif op == 0x8E:
                    r[A] = v & 0xFFFF
                elif op == 0x8F:
                    r[A] = ((v + 0x8000) & 0xFFFF) - 0x8000
                else:
                    r[A], wide = _fx_unop(op, v)
                    if wide:
                        r[A + 1] = None
            elif 0x90 <= op <= 0xA5:
                k, wide = (op - 0x90, False) if op <= 0x9A else (op - 0x9B, True)
                r[b1] = _dxe_binop(k, r[ins[p + 2]], r[ins[p + 3]], wide)
                if wide:
                    r[b1 + 1] = None
            elif 0xB0 <= op <= 0xC5:
                k, wide = (op - 0xB0, False) if op <= 0xBA else (op - 0xBB, True)
                r[A] = _dxe_binop(k, r[A], r[B], wide)
                if wide:
                    r[A + 1] = None
            elif 0xD0 <= op <= 0xD7:
                k = op - 0xD0
                lit = h16(p + 2)
                r[A] = _dxe_binop(1, lit, r[B], False) if k == 1 else _dxe_binop(k, r[B], lit, False)
            elif 0xD8 <= op <= 0xE2:
                k, s, lit = op - 0xD8, r[ins[p + 2]], (ins[p + 3] ^ 0x80) - 0x80
                r[b1] = _dxe_binop(1, lit, s, False) if k == 1 else _dxe_binop(k, s, lit, False)
            elif 0xA6 <= op <= 0xAF:
                wide = op >= 0xAB
                r[b1] = _fx_binop(op - (0xAB if wide else 0xA6), r[ins[p + 2]], r[ins[p + 3]], wide)
                if wide:
                    r[b1 + 1] = None
            elif 0xC6 <= op <= 0xCF:
                wide = op >= 0xCB
                r[A] = _fx_binop(op - (0xCB if wide else 0xC6), r[A], r[B], wide)
                if wide:
                    r[A + 1] = None
            elif 0xFA <= op <= 0xFD:
                last = self.dyn(op, ins, p, r, depth)
            else:
                raise _DxAbort  # odex ops
            pc += w


def _dxe_default(p):
    return 0 if p in ("Z", "B", "S", "C", "I", "J") else ("" if p == "Ljava/lang/String;" else _DXE_UNK)


class _DxeDeepVM(_DxVM):
    max_steps = _DXE_DEEP_STEPS
    natives = None  # ref -> callable(int) -> int | None: the app's own JNI exports (D23 set5 `jni_secret` bridge)

    def invoke(self, ref, raw, depth):
        if ref in self.dx.code and _dxp_pure(self.dx, ref):  # pure static long/int fn: memoised compiled closures
            ct = ref.split("->")[0]
            memo = self.dx.__dict__.setdefault("_dxp_memo", {})
            key = (ref, *raw)
            v = memo.get(key, _DXE_UNK)
            if v is not _DXE_UNK:
                return v
            if depth >= _DXE_DEPTH:
                raise _DxAbort
            self.init_class(ct)
            v = _dxp_run(self, ref, raw, depth + 1)
            if len(memo) < _DXP_MEMO_MAX:
                memo[key] = v
            return v
        if ref not in self.dx.code and ref not in _DXE_INTR:
            v = self.kotlin(ref, raw, depth)
            if v is not _DXE_UNK:
                return v
        elif depth > 0 and ref in self.dx.code and len(self.dx.code[ref][2]) <= 16 and (
                "->access$" in ref or self.dx.code[ref][3] & 0x1000):
            depth -= 1  # a kotlinc synthetic accessor / bridge forwards one call: it costs no frame of _DXE_DEPTH
        fn = None if self.natives is None or ref in self.dx.code or ref in _DXE_INTR else self.natives(ref)
        if fn is None:
            return super().invoke(ref, raw, depth)
        v = fn(raw)
        if v is None:
            raise _DxAbort
        return self.note(v)

    def init_class(self, ct):
        if not self.inited:  # first class of a run: the Locale constants a kotlinc `uppercase()` / `lowercase()` reads
            for k in _KOBJ_LOCALES:
                self.statics.setdefault(k, _DxObj("Ljava/util/Locale;"))
        super().init_class(ct)

    def new_instance(self, t):
        if t in _dxx_supers(self.dx):  # an in-dex class with no statics: Release$Companion, $$ExternalSyntheticLambda0
            self.init_class(t)
            return _DxObj(t)
        return super().new_instance(t)

    def kotlin(self, ref, raw, depth):
        """A Kotlin-compiled chain's out-of-dex call (coverage atlas row 96): Intrinsics.check* -> no-op, areEqual;
        inline-class box-impl / unbox-impl (ULong / UInt / UShort / UByte); Number.xxxValue() on a boxed primitive;
        an interface / abstract / inherited call (Function1.invoke on a d8 lambda, a `when` over a sealed class)
        dispatched on the receiver's in-dex class. _DXE_UNK when none applies (the caller's own path decides)."""
        ct, rest = ref.split("->", 1)
        name = rest[:rest.find("(")]
        o = raw[0] if raw else None
        if ct == "Lkotlin/jvm/internal/Intrinsics;":
            if name.startswith("check") and ref.endswith(")V"):
                return None
            if name == "areEqual" and len(raw) == 2 and all(isinstance(x, (int, str)) or x is None for x in raw):
                return int(raw[0] == raw[1])
            return _DXE_UNK
        if ct in _KOBJ_INLINE:
            if name == "box-impl" and len(raw) in (1, 2) and isinstance(o, int):
                b = _DxObj(ct)
                b.f["$v"] = o
                return b
            if name == "unbox-impl" and len(raw) == 1 and isinstance(o, _DxObj) and o.t == ct and "$v" in o.f:
                return o.f["$v"]
            return _DXE_UNK
        if ct == "Ljava/lang/Number;" and len(raw) == 1 and isinstance(o, int) and not isinstance(o, bool):
            w = {"longValue": _dxe_w64, "intValue": _dxe_w32, "shortValue": lambda x: ((x + 0x8000) & 0xFFFF) - 0x8000,
                 "byteValue": lambda x: ((x + 0x80) & 0xFF) - 0x80}.get(name)
            return _DXE_UNK if w is None else w(o)
        if isinstance(o, _DxObj) and o.t != ct:
            sup, t = _dxx_supers(self.dx), o.t
            for _ in range(8):
                if t is None or t not in sup:
                    break
                if f"{t}->{rest}" in self.dx.code:
                    return self.invoke(f"{t}->{rest}", raw, depth)
                t = sup.get(t)
        return _DXE_UNK


# Kotlin `object` / companion / inline-class chains (coverage atlas row 96): the boxes kotlinc emits for value classes
# and the Locale constants of `uppercase()` / `lowercase()`; _DxeDeepVM.kotlin() runs them.
_KOBJ_INLINE = frozenset(("Lkotlin/ULong;", "Lkotlin/UInt;", "Lkotlin/UShort;", "Lkotlin/UByte;"))
_KOBJ_LOCALES = ("Ljava/util/Locale;->ROOT", "Ljava/util/Locale;->US", "Ljava/util/Locale;->ENGLISH")


# --- pure static fns of a v2 chain, compiled once to per-instruction closures and memoised (coverage atlas:
# dex-eval-pure-static-memo, rows 96/97). A static method with only int/long params + result whose body is moves /
# consts / int+long ALU / cmp / if / goto / switch / returns and invoke-static of other such methods (or a
# Long/Integer/Math intrinsic) touches no statics, arrays or objects: its value is a function of its args, so the deep
# VM keys it by (ref, args) across every String method it runs, and executes it from a pre-decoded closure table
# instead of re-decoding each code unit (Probe.s1/s2/s3's <=4096-step inverse searches dominate a D23 Mastery set).
# Same semantics as _DxVM.run: anything the interpreter aborts on raises _DxAbort here; steps count toward max_steps.
_DXP_MEMO_MAX = 1 << 16
_DXP_OPS = frozenset([*range(0x01, 0x0C), 0x0F, 0x10, *range(0x12, 0x1A), 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x31,
                      *range(0x32, 0x3E), 0x7B, 0x7C, 0x7D, 0x7E, 0x81, 0x84, 0x8D, 0x8E, 0x8F, *range(0x90, 0xA6),
                      *range(0xB0, 0xC6), *range(0xD0, 0xE3), 0x71, 0x77])
_DXP_INTR_OK = ("Ljava/lang/Long;->", "Ljava/lang/Integer;->", "Ljava/lang/Math;->")


def _dxp_prim(ref):
    ps = _dxe_params(ref)
    return all(p in "ZBSCIJ" for p in ps) and ref[ref.rindex(")") + 1:] in ("Z", "B", "S", "C", "I", "J")


def _dxp_walk(ins):
    """[(pc, op, b1)] of real instructions (switch / array payloads skipped); None when the stream is malformed."""
    out, pc, n = [], 0, len(ins) // 2
    while pc < n:
        p = 2 * pc
        op, b1 = ins[p], ins[p + 1]
        if op == 0 and b1 in (1, 2, 3):
            if p + 8 > len(ins):
                return None
            sz = struct.unpack_from("<H", ins, p + 2)[0]
            w = (sz * 2 + 4 if b1 == 1 else sz * 4 + 2 if b1 == 2 else
                 (sz * struct.unpack_from("<I", ins, p + 4)[0] + 1) // 2 + 4)
        else:
            out.append((pc, op, b1))
            w = _DOP_W[op]
        pc += w
    return out if pc == n else None


def _dxp_pure(dx, ref):
    """True when `ref` is a static primitive-only method of the pure kind above (cached on the _DxDex)."""
    cache = dx.__dict__.setdefault("_dxp_pure", {})
    if ref in cache:
        return cache[ref]
    cache[ref] = True  # provisional: a recursive cycle of otherwise-pure methods stays pure
    ok = False
    try:
        nreg, nin, ins, acc = dx.code[ref]
        walk = _dxp_walk(ins) if acc & 0x8 and nin <= nreg and _dxp_prim(ref) and len(ins) <= 1 << 16 else None
        if walk is not None:
            ok = True
            for pc, op, b1 in walk:
                if op not in _DXP_OPS or op == 0 and b1:
                    ok = False
                elif op in (0x71, 0x77):
                    r2 = dx.mref(struct.unpack_from("<H", ins, 2 * pc + 2)[0])
                    ok = (_dxp_pure(dx, r2) if r2 in dx.code else
                          r2 in _DXE_INTR and r2.startswith(_DXP_INTR_OK) and _dxp_prim(r2))
                if not ok:
                    break
    except Exception:  # noqa: BLE001 - malformed code item: interpret it instead
        ok = False
    cache[ref] = ok
    return ok


def _dxp_abort(r):
    raise _DxAbort


def _dxp_compile(dx, ref):  # noqa: C901 - one table of instruction closures
    """(closures by pc, nreg, nin) of a pure method. Each closure takes the register list (regs + [ret, last, vm,
    depth]) and returns the next pc, -1 on return."""
    comp = dx.__dict__.setdefault("_dxp_comp", {})
    if ref in comp:
        return comp[ref]
    nreg, nin, ins, _ = dx.code[ref]
    n = len(ins) // 2
    R, L, VM, DP = nreg, nreg + 1, nreg + 2, nreg + 3
    code = [_dxp_abort] * (n + 1)
    h16 = lambda p: struct.unpack_from("<h", ins, p)[0]  # noqa: E731
    u16 = lambda p: struct.unpack_from("<H", ins, p)[0]  # noqa: E731
    w32, w64, binop = _dxe_w32, _dxe_w64, _dxe_binop

    def br(t):
        return t if 0 <= t < n else n

    for pc, op, b1 in _dxp_walk(ins):
        p, A, B, nx = 2 * pc, b1 & 0xF, b1 >> 4, br(pc + _DOP_W[op])
        f = None
        if op in (0x01, 0x04, 0x07):
            if op == 0x04:
                def f(r, A=A, B=B, nx=nx):
                    r[A], r[A + 1] = r[B], r[B + 1]
                    return nx
            else:
                def f(r, A=A, B=B, nx=nx):
                    r[A] = r[B]
                    return nx
        elif op in (0x02, 0x05, 0x08, 0x03, 0x06, 0x09):
            a_, s_ = (b1, u16(p + 2)) if op in (0x02, 0x05, 0x08) else (u16(p + 2), u16(p + 4))
            if op in (0x05, 0x06):
                def f(r, a_=a_, s_=s_, nx=nx):
                    r[a_], r[a_ + 1] = r[s_], r[s_ + 1]
                    return nx
            else:
                def f(r, a_=a_, s_=s_, nx=nx):
                    r[a_] = r[s_]
                    return nx
        elif op in (0x0A, 0x0B):
            if op == 0x0B:
                def f(r, a_=b1, nx=nx):
                    r[a_], r[a_ + 1] = r[L], None
                    return nx
            else:
                def f(r, a_=b1, nx=nx):
                    r[a_] = r[L]
                    return nx
        elif op in (0x0F, 0x10):
            def f(r, a_=b1):
                r[R] = r[a_]
                return -1
        elif 0x12 <= op <= 0x19:
            wide = op >= 0x16
            a_ = A if op == 0x12 else b1
            v = ((B ^ 8) - 8 if op == 0x12 else h16(p + 2) if op in (0x13, 0x16) else
                 struct.unpack_from("<i", ins, p + 2)[0] if op in (0x14, 0x17) else w32(u16(p + 2) << 16)
                 if op == 0x15 else struct.unpack_from("<q", ins, p + 2)[0] if op == 0x18 else w64(h16(p + 2) << 48))
            if wide:
                def f(r, a_=a_, v=v, nx=nx):
                    r[a_], r[a_ + 1] = v, None
                    return nx
            else:
                def f(r, a_=a_, v=v, nx=nx):
                    r[a_] = v
                    return nx
        elif op in (0x28, 0x29, 0x2A):
            off = (b1 ^ 0x80) - 0x80 if op == 0x28 else h16(p + 2) if op == 0x29 else \
                struct.unpack_from("<i", ins, p + 2)[0]
            if off or op == 0x2A:
                f = (lambda r, t=br(pc + off): t)
        elif op in (0x2B, 0x2C):
            q = 2 * (pc + struct.unpack_from("<i", ins, p + 2)[0])
            if 0 <= q and q + 4 <= len(ins):
                cnt, tab = u16(q + 2), None
                if op == 0x2B and ins[q:q + 2] == b"\x00\x01":
                    k0 = struct.unpack_from("<i", ins, q + 4)[0]
                    tab = {k0 + k: br(pc + struct.unpack_from("<i", ins, q + 8 + 4 * k)[0]) for k in range(cnt)}
                elif op == 0x2C and ins[q:q + 2] == b"\x00\x02":
                    keys = struct.unpack_from(f"<{cnt}i", ins, q + 4)
                    tab = {}
                    for k, kv in enumerate(keys):
                        tab.setdefault(kv, br(pc + struct.unpack_from("<i", ins, q + 4 + 4 * cnt + 4 * k)[0]))
                if tab is not None:
                    def f(r, a_=b1, tab=tab, nx=nx):
                        v = r[a_]
                        if v.__class__ is not int:
                            raise _DxAbort
                        return tab.get(v, nx)
        elif op == 0x31:
            def f(r, a_=b1, x_=ins[p + 2], y_=ins[p + 3], nx=nx):
                x, y = r[x_], r[y_]
                if x.__class__ is not int or y.__class__ is not int:
                    raise _DxAbort
                r[a_] = (x > y) - (x < y)
                return nx
        elif 0x32 <= op <= 0x3D:
            off, k, z = h16(p + 2), (op - 0x32) % 6, op >= 0x38
            if off:
                t = br(pc + off)
                cmp = (int.__eq__, int.__ne__, int.__lt__, int.__ge__, int.__gt__, int.__le__)[k]

                def f(r, xa=(b1 if z else A), yb=B, z=z, cmp=cmp, t=t, nx=nx):
                    x = r[xa]
                    y = 0 if z else r[yb]
                    if x.__class__ is not int:
                        if not z:
                            raise _DxAbort
                        x = 0 if x is None else 1
                    if y.__class__ is not int:
                        raise _DxAbort
                    return t if cmp(x, y) else nx
        elif 0x7B <= op <= 0x8F:
            g = {0x7B: lambda v: w32(-v), 0x7C: lambda v: ~v, 0x7D: lambda v: w64(-v), 0x7E: lambda v: ~v,
                 0x81: lambda v: v, 0x84: w32, 0x8D: lambda v: ((v + 0x80) & 0xFF) - 0x80, 0x8E: lambda v: v & 0xFFFF,
                 0x8F: lambda v: ((v + 0x8000) & 0xFFFF) - 0x8000}[op]
            if op in (0x7D, 0x7E, 0x81):
                def f(r, A=A, B=B, g=g, nx=nx):
                    v = r[B]
                    if v.__class__ is not int:
                        raise _DxAbort
                    r[A], r[A + 1] = g(v), None
                    return nx
            else:
                def f(r, A=A, B=B, g=g, nx=nx):
                    v = r[B]
                    if v.__class__ is not int:
                        raise _DxAbort
                    r[A] = g(v)
                    return nx
        elif 0x90 <= op <= 0xA5 or 0xB0 <= op <= 0xC5:
            lo = 0x90 if op <= 0xA5 else 0xB0
            k, wide = (op - lo, False) if op <= lo + 0xA else (op - lo - 0xB, True)
            d_, x_, y_ = (b1, ins[p + 2], ins[p + 3]) if lo == 0x90 else (A, A, B)
            if wide:
                def f(r, k=k, d_=d_, x_=x_, y_=y_, nx=nx):
                    r[d_], r[d_ + 1] = binop(k, r[x_], r[y_], True), None
                    return nx
            else:
                def f(r, k=k, d_=d_, x_=x_, y_=y_, nx=nx):
                    r[d_] = binop(k, r[x_], r[y_], False)
                    return nx
        elif 0xD0 <= op <= 0xE2:
            if op <= 0xD7:
                k, d_, s_, lit = op - 0xD0, A, B, h16(p + 2)
            else:
                k, d_, s_, lit = op - 0xD8, b1, ins[p + 2], (ins[p + 3] ^ 0x80) - 0x80
            if k == 1:
                def f(r, d_=d_, s_=s_, lit=lit, nx=nx):
                    r[d_] = binop(1, lit, r[s_], False)
                    return nx
            else:
                def f(r, k=k, d_=d_, s_=s_, lit=lit, nx=nx):
                    r[d_] = binop(k, r[s_], lit, False)
                    return nx
        elif op in (0x71, 0x77):
            ref2 = dx.mref(u16(p + 2))
            if op == 0x71:
                g_ = u16(p + 4)
                regs = tuple([g_ & 0xF, (g_ >> 4) & 0xF, (g_ >> 8) & 0xF, g_ >> 12, A][:B])
            else:
                regs = tuple(range(u16(p + 4), u16(p + 4) + b1))

            def f(r, ref2=ref2, regs=regs, nx=nx):
                r[L] = r[VM].invoke(ref2, [r[x] for x in regs], r[DP])
                return nx
        if f is not None:
            code[pc] = f
    comp[ref] = (code, nreg, nin)
    return comp[ref]


def _dxp_run(vm, ref, raw, depth):
    """Run a pure method's compiled closures on `vm` (its steps / deadline budget); the returned int."""
    code, nreg, nin = _dxp_compile(vm.dx, ref)
    r = [None] * (nreg + 4)
    r[nreg - nin:nreg - nin + len(raw)] = raw[:nin]
    r[nreg + 2], r[nreg + 3] = vm, depth
    pc, k, now, dl = 0, 0, time.time, vm.deadline
    while pc >= 0:
        pc = code[pc](r)
        k += 1
        if not k & 1023 and (vm.steps + k > vm.max_steps or now() > dl):
            raise _DxAbort
    vm.steps += k
    if vm.steps > vm.max_steps:
        raise _DxAbort
    return r[nreg]


# --- JNI bridge: an app `native` method (static or instance; int / long / boolean / String args; int-like, long or
# String return) run as its Java_* export -- short or overloaded `__<sig>` JNI name, else a RegisterNatives table entry
# -- under unicorn (coverage atlas rows 37, 96: D23 Mastery `NativeLibrarySecrets.nativeShare(long)` inside
# Release.token()). JNIEnv* -> a function table whose slots trap: NewStringUTF records the C string (the jstring
# return), GetStringUTFChars hands a String arg back as C bytes, FindClass / Get*MethodID return dummy handles, the
# rest 0. R_*_RELATIVE applied; libc imports -> a small shim (strlen / mem* / str* / malloc / [s|sn]printf), others
# return 0. x86_64, then arm64-v8a, armeabi-v7a (ARM / Thumb), x86. 200k insns per call; the artifact is never dlopened.
_NLB_STEPS, _NLB_MAX_SO = 200_000, 8 << 20
_NLB_ABI = {"EM_X86_64": ("UC_ARCH_X86", "UC_MODE_64", "x86_const", "UC_X86_REG_", ("RDI", "RSI", "RDX", "RCX", "R8", "R9"),
                          "RAX", "RSP", "RIP", 8, b"\xc3\xc3\xc3\xc3"),
            "EM_AARCH64": ("UC_ARCH_ARM64", "UC_MODE_ARM", "arm64_const", "UC_ARM64_REG_",
                           ("X0", "X1", "X2", "X3", "X4", "X5", "X6", "X7"), "X0", "SP", "PC", 8, b"\xc0\x03\x5f\xd6"),
            "EM_ARM": ("UC_ARCH_ARM", "UC_MODE_ARM", "arm_const", "UC_ARM_REG_", ("R0", "R1", "R2", "R3"), "R0", "SP",
                       "PC", 4, b"\x1e\xff\x2f\xe1"),
            "EM_386": ("UC_ARCH_X86", "UC_MODE_32", "x86_const", "UC_X86_REG_", (), "EAX", "ESP", "EIP", 4,
                       b"\xc3\xc3\xc3\xc3")}
_NLB_ABI_ORDER = ("x86_64", "arm64-v8a", "armeabi-v7a", "x86")
_NLB_REF = re.compile(r"L([^;]+);->([^(]+)\(((?:[ZBCSIJ]|Ljava/lang/String;)*)\)([ZBCSIJ]|Ljava/lang/String;)")
_NLB_JNI_HANDLE = {6: 0x50000040, 21: 0x50000050, 31: 0x50000040, 33: 0x50000060, 113: 0x50000070}  # FindClass ...
_NLB_JNI_SLOTS, _NLB_MAX_IMPORTS = 0x140, 0x200
_NLB_FMT = re.compile(rb"%([-+ #0]*)(\d*|\*)(?:\.(\d*|\*))?(hh|h|ll|l|z|j|t|q)?([diouxXcsp%])")


def _nlb_mangle(s):
    out = []
    for ch in s:
        if ch.isalnum() and ch.isascii():
            out.append(ch)
        else:
            out.append({"/": "_", "_": "_1", ";": "_2", "[": "_3"}.get(ch, "_0%04x" % ord(ch)))
    return "".join(out)


def _nlb_relocs(elf):
    """(relative [(off, addend | None)], imports [(off, sym name)]) from the .so's RELA / REL sections."""
    rel_t = {"EM_X86_64": 8, "EM_AARCH64": 1027, "EM_ARM": 23, "EM_386": 8}[elf.arch]
    sym_t = {"EM_X86_64": (6, 7, 1), "EM_AARCH64": (1025, 1026, 257), "EM_ARM": (21, 22, 2),
             "EM_386": (6, 7, 1)}[elf.arch]
    rel, imp = [], []
    for _, typ, _, off, size, link in elf.secs:
        if typ not in (4, 9):  # SHT_RELA, SHT_REL
            continue
        fmt = ("<QQq" if typ == 4 else "<QQ") if elf.is64 else ("<IIi" if typ == 4 else "<II")
        n = struct.calcsize(fmt)
        names = elf.syms.get(link, [])
        for t in struct.iter_unpack(fmt, elf.b[off:off + min(size, n * 65536) // n * n]):
            info = t[1]
            rt, si = (info & 0xFFFFFFFF, info >> 32) if elf.is64 else (info & 0xFF, info >> 8)
            if rt == rel_t:
                rel.append((t[0], t[2] if len(t) > 2 else None))
            elif rt in sym_t and si < len(names) and names[si][0] and not names[si][4]:
                imp.append((t[0], names[si][0]))
    return rel, imp


def _nlb_call(elf, va, args, ret):
    """Run the JNI function at `va` with `args` = [(kind, value)] (kind 'w' 32-bit word, 'q' 64-bit, 's' str) after
    (env, jclass/jobject); `ret` = the Java return descriptor. The masked value / str, or None (fault, trap, budget)."""
    import unicorn as U
    ua, um, cm, rp, aregs, retr, spr, pcr, W, ret_insn = _NLB_ABI[elf.arch]
    C = getattr(U, cm)
    R = lambda n: getattr(C, rp + n)
    thumb = elf.arch == "EM_ARM" and va & 1
    uc, page = U.Uc(getattr(U, ua), getattr(U, um)), 0x1000
    base, top = 0x10000000, 0
    for v, o, fs, ms in elf.segs:
        top = max(top, (v + ms + page - 1) & ~(page - 1))
    if not 0 < top <= 64 << 20:
        return None
    uc.mem_map(base, top, U.UC_PROT_ALL)
    for v, o, fs, ms in elf.segs:
        uc.mem_write(base + v, elf.b[o:o + fs])
    mask = (1 << (8 * W)) - 1
    pk = (lambda x: struct.pack("<Q", x & mask)) if W == 8 else (lambda x: struct.pack("<I", x & mask))
    rel, imp = _nlb_relocs(elf)
    for off, add in rel[:65536]:
        if add is None:
            add = int.from_bytes(elf.at(off, W).ljust(W, b"\0"), "little")
        try:
            uc.mem_write(base + off, pk(base + add))
        except U.UcError:
            pass
    stack, env, stop = 0x70000000, 0x60000000, 0x50000000
    table, trap, heap0, tls = env + 0x100, env + 0x2000, env + 0x10000, env + 0xF8000
    uc.mem_map(stack, 0x20000)
    uc.mem_map(env, 0x100000)
    uc.mem_map(stop, page)
    uc.mem_write(env, pk(table))
    uc.mem_write(table, b"".join(pk(trap + 4 * i) for i in range(_NLB_JNI_SLOTS)))
    uc.mem_write(trap, ret_insn * (_NLB_JNI_SLOTS + _NLB_MAX_IMPORTS))
    lib, heap = {}, [heap0]
    for off, name in imp:
        if name not in lib and len(lib) < _NLB_MAX_IMPORTS:
            lib[name] = len(lib)
        if name in lib:
            try:  # a data import (stack guard, environ) reads the stub's bytes: constant, never written
                uc.mem_write(base + off, pk(trap + 4 * (_NLB_JNI_SLOTS + lib[name])))
            except U.UcError:
                pass
    libn = {v: k for k, v in lib.items()}
    strs, hnd = {}, [0x51000000]

    def new_str(b):
        hnd[0] += 16
        strs[hnd[0]] = bytes(b)
        return hnd[0]

    def alloc(n):
        p = heap[0]
        heap[0] = (p + max(int(n), 1) + 15) & ~15
        if heap[0] > tls - 0x100:
            raise _DxAbort
        return p

    def cstr(p, cap=4096):
        out = bytearray()
        while len(out) < cap:
            c = bytes(uc.mem_read(p + len(out), 64))
            k = c.find(b"\0")
            out += c if k < 0 else c[:k]
            if k >= 0:
                break
        return bytes(out[:cap])

    def sp_word(i):  # the i-th stack word above the return address / at sp
        sp = uc.reg_read(R(spr)) + (W if elf.arch in ("EM_X86_64", "EM_386") else 0)
        return int.from_bytes(uc.mem_read(sp + W * i, W), "little")

    def arg(i):  # i-th word-sized call argument at a trap
        if i < len(aregs):
            return uc.reg_read(R(aregs[i])) & mask
        return sp_word(i - len(aregs))

    def sprintf(fmt, k):
        out, pos = bytearray(), 0
        for m in _NLB_FMT.finditer(fmt):
            out += fmt[pos:m.start()]
            pos = m.end()
            flags, width, prec, ln, cv = m.groups()
            if cv == b"%":
                out += b"%"
                continue
            if width == b"*":
                width, k = str(_dxe_w32(arg(k))).encode(), k + 1
            if prec == b"*":
                prec, k = str(_dxe_w32(arg(k))).encode(), k + 1
            if cv == b"s":
                v = cstr(arg(k))
                k += 1
                if prec:
                    v = v[:int(prec)]
                out += v.rjust(int(width or 0)) if b"-" not in flags else v.ljust(int(width or 0))
                continue
            wide = ln in (b"ll", b"q", b"j") or (W == 8 and ln in (b"l", b"z", b"t")) or cv == b"p"
            if wide and W == 4:
                if elf.arch == "EM_ARM" and k % 2:
                    k += 1
                v, k = arg(k) | arg(k + 1) << 32, k + 2
            else:
                v, k = arg(k), k + 1
            bits = 64 if wide else 32
            v &= (1 << bits) - 1
            if ln == b"hh":
                v, bits = v & 0xFF, 8
            elif ln == b"h":
                v, bits = v & 0xFFFF, 16
            if cv == b"c":
                out += bytes([v & 0xFF])
                continue
            f = "%" + flags.decode() + width.decode() + ("." + prec.decode() if prec is not None else "")
            if cv in b"di":
                out += (f + "d").encode() % (v - (1 << bits) if v >> (bits - 1) else v)
            else:
                out += (f + ("x" if cv == b"p" else cv.decode())).encode() % v
        return bytes(out + fmt[pos:])

    def libc(name):
        a = arg
        if name in ("strlen", "__strlen_chk"):
            return len(cstr(a(0), 1 << 16))
        if name in ("memcpy", "memmove", "__memcpy_chk", "__memmove_chk"):
            uc.mem_write(a(0), bytes(uc.mem_read(a(1), a(2) & 0xFFFFF)))
            return a(0)
        if name in ("memset", "__memset_chk"):
            uc.mem_write(a(0), bytes([a(1) & 0xFF]) * (a(2) & 0xFFFFF))
            return a(0)
        if name in ("malloc", "_Znwm", "_Znam", "_Znwj", "_Znaj"):
            return alloc(a(0) & 0xFFFFF)
        if name == "calloc":
            return alloc((a(0) * a(1)) & 0xFFFFF)
        if name in ("strcpy", "__strcpy_chk", "stpcpy"):
            s = cstr(a(1))
            uc.mem_write(a(0), s + b"\0")
            return a(0) + (len(s) if name == "stpcpy" else 0)
        if name in ("strcat", "__strcat_chk"):
            d = a(0)
            uc.mem_write(d + len(cstr(d)), cstr(a(1)) + b"\0")
            return d
        if name in ("strncpy", "__strncpy_chk"):
            n = a(2) & 0xFFFFF
            uc.mem_write(a(0), cstr(a(1), n).ljust(n, b"\0"))
            return a(0)
        if name in ("strcmp", "strncmp", "memcmp"):
            n = a(2) & 0xFFFFF if name != "strcmp" else 1 << 16
            x, y = (bytes(uc.mem_read(a(0), n)), bytes(uc.mem_read(a(1), n))) if name == "memcmp" else \
                (cstr(a(0), n), cstr(a(1), n))
            return (x > y) - (x < y)
        if name in ("sprintf", "snprintf", "__sprintf_chk", "__snprintf_chk"):
            fi = {"sprintf": 1, "snprintf": 2, "__sprintf_chk": 3, "__snprintf_chk": 4}[name]
            s = sprintf(cstr(a(fi)), fi + 1)
            if name in ("snprintf", "__snprintf_chk"):
                n = a(1) & 0xFFFFF
                if n:
                    uc.mem_write(a(0), s[:n - 1] + b"\0")
            else:
                uc.mem_write(a(0), s + b"\0")
            return len(s)
        if name in ("abort", "__stack_chk_fail", "exit", "_exit", "raise", "kill", "__assert2", "__assert_fail"):
            raise _DxAbort
        if name in ("free", "__cxa_finalize", "__cxa_atexit", "_ZdlPv", "_ZdaPv"):
            return 0
        if name in ("__stack_chk_guard", "environ", "__sF", "stderr", "stdout"):
            return 0
        return 0

    def jni(i):
        if i == 167:  # NewStringUTF(env, const char*)
            return new_str(cstr(arg(1)))
        if i in (164, 168):  # GetStringLength / GetStringUTFLength
            return len(strs.get(arg(1), b""))
        if i == 169:  # GetStringUTFChars(env, jstring, isCopy)
            b = strs.get(arg(1))
            if b is None:
                return 0
            p = alloc(len(b) + 1)
            uc.mem_write(p, b + b"\0")
            return p
        if i == 4:  # GetVersion
            return 0x10006
        return _NLB_JNI_HANDLE.get(i, 0)

    def on_trap(_uc, addr, _size, _ud):
        i = (addr - trap) // 4
        try:
            v = jni(i) if i < _NLB_JNI_SLOTS else libc(libn.get(i - _NLB_JNI_SLOTS, ""))
        except (_DxAbort, U.UcError):
            _uc.emu_stop()
            return
        uc.reg_write(R(retr), v & mask)

    uc.hook_add(U.UC_HOOK_CODE, on_trap, begin=trap, end=trap + 4 * (_NLB_JNI_SLOTS + _NLB_MAX_IMPORTS))
    if elf.arch == "EM_X86_64":
        uc.reg_write(C.UC_X86_REG_FS_BASE, tls)
    elif elf.arch == "EM_AARCH64":
        uc.reg_write(C.UC_ARM64_REG_TPIDR_EL0, tls)
    # the word list: env, jclass / jobject, then the Java args (ARM32: a long sits in an even register pair / slot)
    words, this = [env, 0x50000010 if args and args[0][0] == "this" else 0x50000020], args[:1] == [("this", None)]
    for kind, v in args[1:] if this else args:
        if kind == "s":
            words.append(new_str(v.encode("utf-8", "surrogatepass")))
        elif kind == "q" and W == 4:
            if elf.arch == "EM_ARM" and len(words) % 2:
                words.append(0)
            words += [v & 0xFFFFFFFF, (v >> 32) & 0xFFFFFFFF]
        else:
            words.append(v & (0xFFFFFFFF if kind == "w" else mask))
    s = stack + 0x18000
    spill = words[len(aregs):]
    s -= W * len(spill) + 16
    s &= ~15
    uc.mem_write(s, b"".join(pk(w) for w in spill))
    for n, w in zip(aregs, words):
        uc.reg_write(R(n), w & mask)
    if elf.arch in ("EM_X86_64", "EM_386"):
        s -= W
        uc.mem_write(s, pk(stop))
    else:
        uc.reg_write(C.UC_ARM64_REG_LR if elf.arch == "EM_AARCH64" else C.UC_ARM_REG_LR, stop)
    uc.reg_write(R(spr), s)
    uc.emu_start((base + va) | (1 if thumb else 0) if elf.arch == "EM_ARM" else base + va, stop, count=_NLB_STEPS)
    if uc.reg_read(R(pcr)) & ~1 != stop:
        return None
    lo = uc.reg_read(R(retr)) & mask
    if ret == "Ljava/lang/String;":
        b = strs.get(lo)
        return None if b is None else b.decode("utf-8", "replace")
    if ret == "J":
        if W == 4:
            hi = uc.reg_read(C.UC_X86_REG_EDX if elf.arch == "EM_386" else C.UC_ARM_REG_R1)
            lo |= (hi & 0xFFFFFFFF) << 32
        return _dxe_w64(lo)
    lo &= 0xFFFFFFFF
    return {"Z": lambda x: int(x & 0xFF != 0), "B": lambda x: ((x + 0x80) & 0xFF) - 0x80,
            "S": lambda x: ((x + 0x8000) & 0xFFFF) - 0x8000, "C": lambda x: x & 0xFFFF}.get(ret, _dxe_w32)(lo)


def _nlb_resolver(z):
    """ref -> callable(raw registers) for app `native` methods whose Java_<mangled>[__<sig>] export (or a
    RegisterNatives {name, sig, fn} entry) sits in lib/<abi>/*.so; the first ABI the bridge can run wins. None when
    the APK ships no runnable .so. The callable returns None when it cannot answer (the VM aborts that chain)."""
    sos = {}
    for i in z.infolist():
        m = re.fullmatch(r"lib/([^/]+)/[^/]+\.so", i.filename)
        if m and m.group(1) in _NLB_ABI_ORDER and 0 < i.file_size <= _NLB_MAX_SO:
            sos.setdefault(m.group(1), []).append(i)
    if not sos:
        return None
    dex = b"".join(z.read(i) for i in z.infolist() if re.fullmatch(r"classes\d*\.dex", i.filename)
                   and i.file_size <= _DXE_MAX_DEX)
    elves = []
    for abi in _NLB_ABI_ORDER:
        for i in sos.get(abi, []):
            try:
                elf = _NsoElf(z.read(i))
            except Exception:  # noqa: BLE001 - truncated / impostor .so
                continue
            if elf.arch not in _NLB_ABI or elf.e != "<" or elf.is64 != (elf.arch in ("EM_X86_64", "EM_AARCH64")):
                continue
            ex = {n: va for n, va, _ in _nso_exports(elf) if n.startswith("Java_")}
            try:
                reg = {} if ex else dict(reversed(_nso_registered(elf, dex)))
            except Exception:  # noqa: BLE001
                reg = {}
            if ex or reg:
                elves.append((elf, ex, reg))
    if not elves:
        return None
    cache = {}

    def resolve(ref):
        if ref in cache:
            return cache[ref]
        cache[ref] = None
        m = _NLB_REF.fullmatch(ref)
        if not m:
            return None
        short = "Java_%s_%s" % (_nlb_mangle(m.group(1)), _nlb_mangle(m.group(2)))
        hit = next(((elf, ex[n]) for elf, ex, _ in elves for n in (short, short + "__" + _nlb_mangle(m.group(3)))
                    if n in ex), None) or next(((elf, reg[m.group(2)]) for elf, _, reg in elves if m.group(2) in reg),
                                               None)
        if hit is None:
            return None
        ps, rt = _dxe_params(ref), m.group(4)
        nslots = sum(2 if p == "J" else 1 for p in ps)

        def fn(raw, elf=hit[0], va=hit[1]):
            if len(raw) not in (nslots, nslots + 1):
                return None
            i, args = len(raw) - nslots, []
            if i:
                args.append(("this", None))
            for p in ps:
                v = raw[i]
                if p == "Ljava/lang/String;":
                    if not isinstance(v, str):
                        return None
                    args.append(("s", v))
                elif isinstance(v, int) and not isinstance(v, bool) or isinstance(v, bool):
                    args.append(("q" if p == "J" else "w", int(v)))
                else:
                    return None
                i += 2 if p == "J" else 1
            try:
                return _nlb_call(elf, va, args, rt)
            except Exception:  # noqa: BLE001 - unmapped access / bad opcode / trap: cannot answer
                return None
        cache[ref] = fn
        return fn
    return resolve


def dex_eval_scan(apk, deep=False):
    """ANS tokens computed by simple Dalvik bytecode: each app method (static String-returning ones and any method with
    an array / xor / switch / int-to-char op) is evaluated by a tiny static interpreter -- const / move / arrays /
    fill-array-data / int+long arithmetic / if / goto / packed+sparse switch, in-dex calls and the <clinit>s it reads,
    plus String / StringBuilder / Integer.parseInt / Base64 intrinsics; String params get "", int params 0; an
    unknown invoke aborts that method; float / double ops follow exact Java semantics (_fx_*). Every string it builds or returns is regex'd. Covers string-
    encryption helpers and switch-flattened control flow without a device. [] when absent; never raises; ~0.8 s.
    deep=True (D23 `codec: analysis`, a puzzle with no data): only the String-returning methods, 2M steps each, return
    values first -- `Release.code(Context)` = a chain of 64-bit mixers fed by 4096-iteration probe solvers, far past
    the 50k cap; the dex also carries a literal decoy token (ANS-0123456789ABCDEF) that dex_strings stops on."""
    if deep:
        return _dex_eval_deep(apk)
    hits = []
    deadline = time.time() + _DXE_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            todo = []
            for ref in dx.order:
                nreg, nin, ins, acc = dx.code[ref]
                ps = _dxe_params(ref)
                if len(ps) > 4 or nin > nreg:
                    continue
                hot = not _DXE_HOT.isdisjoint(ins[0::2])
                if hot or ref.endswith(")Ljava/lang/String;"):
                    todo.append((not hot, ref, ps, acc))
            todo.sort(key=lambda x: x[0])
            for _, ref, ps, acc in todo:
                if time.time() > deadline:
                    break
                vm = _DxVM(dx, deadline)
                raw = [] if acc & 0x8 else [_DxObj(ref.split("->")[0])]
                for p in ps:
                    raw += [_dxe_default(p)] + ([None] if p in "JD" else [])
                try:
                    vm.init_class(ref.split("->")[0])
                    vm.note(vm.run(ref, raw))
                except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError,
                        RecursionError, struct.error):
                    pass
                for s in vm.seen + [v for v in vm.statics.values() if isinstance(v, str)]:
                    hits += ANS_RE_T.findall(s)
                    if not ANS_RE_T.search(s) and re.fullmatch(r"[A-Za-z0-9+/=_-]{24,}", s or ""):
                        t = decode_any(s.encode(), depth=1, cap=40, chain=False)
                        hits += ANS_RE_T.findall(t or "")
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


def _dex_eval_deep(apk, entry_only=False):
    """dex_eval_scan(deep=True): returned ANS tokens of every static String-returning app method under _DxeDeepVM.
    entry_only=True: only the methods _eav_reached() reaches from ChallengeActivity / MainActivity ([] without one)."""
    rets, seen = [], []
    deadline = time.time() + _DXE_DEEP_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
            try:
                natives = _nlb_resolver(z)
            except Exception:  # noqa: BLE001 - no runnable JNI bridge
                natives = None
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            live = _eav_reached(dx, deadline) if entry_only else None
            if entry_only and not live:
                continue
            try:
                vmc = _DxeRflVM if _dxe_reflective(dx) else _DxeDeepVM
            except (IndexError, struct.error):
                vmc = _DxeDeepVM
            for ref in dx.order:
                nreg, nin, _ins, acc = dx.code[ref]
                ps = _dxe_params(ref)
                if not ref.endswith(")Ljava/lang/String;") or not acc & 0x8 or len(ps) > 4 or nin > nreg \
                        or _DXE_LIB.match(ref) or (live is not None and ref not in live):
                    continue
                if time.time() > deadline:
                    break
                vm = vmc(dx, deadline)
                vm.natives = natives
                raw = []
                for q in ps:
                    raw += [_dxe_default(q)] + ([None] if q in "JD" else [])
                try:
                    vm.init_class(ref.split("->")[0])
                    r = vm.run(ref, raw)
                except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError,
                        RecursionError, struct.error):
                    continue
                if isinstance(r, str):
                    rets += ANS_RE_T.findall(r)
                seen += [m for s in vm.seen if isinstance(s, str) for m in ANS_RE_T.findall(s)]
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(rets + seen))




# --- white-box / table-driven cipher: evaluate the table walk (coverage atlas: whitebox-table-cipher-eval) -----------
_WBT_STEPS, _WBT_BUDGET_S, _WBT_MIN_SCORE, _WBT_MAX_IN, _WBT_MAX_RUNS = 400_000, 0.8, 8, 4096, 48
_WBT_AGET = frozenset(range(0x44, 0x4B))
_WBT_XOR = frozenset((0x97, 0xA2, 0xB7, 0xC2, 0xD7, 0xDF))


class _WbtVM(_DxVM):
    max_steps = _WBT_STEPS  # 10-16 rounds of aget/xor over every block of the input


def _wbt_score(ins):
    """aget + xor op count of one method (a T-box / S-box walk is dense in both)."""
    ops = ins[0::2]
    return sum(1 for o in ops if o in _WBT_AGET) + sum(1 for o in ops if o in _WBT_XOR)


def _wbt_bytes(v):
    if isinstance(v, str):
        return v.encode("utf-8", "replace")
    if isinstance(v, list) and v and all(isinstance(x, int) for x in v):
        t = getattr(v, "t", "B")
        if t == "C":
            return "".join(chr(x & 0xFFFF) for x in v).encode("utf-8", "replace")
        if t == "I":
            return b"".join((x & 0xFFFFFFFF).to_bytes(4, "big") for x in v) + bytes(x & 0xFF for x in v)
        return bytes(x & 0xFF for x in v)
    return b""


def _wbt_inputs(z):
    """Small asset blobs a table cipher may read (raw, plus a clean base64 / hex text reading)."""
    out = []
    for i in z.infolist():
        if not i.filename.startswith(("assets/", "res/raw/")) or not 16 <= i.file_size <= _WBT_MAX_IN:
            continue
        b = z.read(i)
        out.append(b)
        t = b.strip()
        if re.fullmatch(rb"(?:[0-9a-fA-F]{2}){16,}", t):
            out.append(bytes.fromhex(t.decode()))
        elif re.fullmatch(rb"[A-Za-z0-9+/_-]{16,}={0,2}", t):
            try:
                out.append(base64.b64decode(t.replace(b"-", b"+").replace(b"_", b"/") + b"=" * (-len(t) % 4)))
            except ValueError:
                pass
    return out


def whitebox_table_scan(apk):
    """ANS tokens a white-box / table-driven cipher decrypts (lookup-table AES with the round keys folded into int[]
    T-tables, Tyi / T-box byte tables, chained byte S-boxes): the key is never recovered -- the table walk itself is
    evaluated. Methods dense in aget + xor (own ops plus their in-dex callees') that take an array are run by the Dalvik
    evaluator with a larger step budget, their <clinit> tables preloaded, the array parameter bound to each static
    byte/int/char array of the app (non-256-long first) and each small asset blob, int params 0 / length. The returned
    (or in-place / output-param) array is regex'd. [] when absent; never raises; ~0.8 s."""
    hits = []
    deadline = time.time() + _WBT_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
            blobs = _wbt_inputs(z)
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            own = {ref: _wbt_score(dx.code[ref][2]) for ref in dx.order}
            cands = []
            for ref in dx.order:
                ps = _dxe_params(ref)
                if not any(p in ("[B", "[I", "[C") for p in ps) or len(ps) > 5:
                    continue
                ins = dx.code[ref][2]
                callee = 0
                for k in range(0, len(ins) - 4, 2):  # invoke-* of in-dex methods (operand alignment is approximate)
                    if 0x6E <= ins[k] <= 0x78 and ins[k] != 0x73:
                        mi = struct.unpack_from("<H", ins, k + 2)[0]
                        if mi < dx.n_met:
                            callee = max(callee, own.get(dx.mref(mi), 0))
                sc = own[ref] + callee
                if sc >= _WBT_MIN_SCORE:
                    cands.append((-sc, ref, ps))
            if not cands:
                continue
            cands.sort()
            pool = _WbtVM(dx, deadline)
            for ct in dict.fromkeys(r.split("->")[0] for r in dx.order):
                if time.time() > deadline:
                    break
                pool.init_class(ct)
            arrs = [v for v in pool.statics.values() if isinstance(v, list) and 16 <= len(v) <= _WBT_MAX_IN
                    and getattr(v, "t", "") in ("B", "I", "C") and all(isinstance(x, int) for x in v)]
            arrs.sort(key=lambda v: len(v) == 256)
            inputs = [(list(v), v.t) for v in arrs] + [([(x ^ 0x80) - 0x80 for x in b], "B") for b in blobs]
            runs = 0
            for _, ref, ps in cands[:8]:
                ai = next(k for k, p in enumerate(ps) if p in ("[B", "[I", "[C"))
                for vals, t in inputs:
                    if time.time() > deadline or runs >= _WBT_MAX_RUNS:
                        break
                    if ps[ai] != "[" + t and not (ps[ai] == "[B" and t == "B"):
                        continue
                    runs += 1
                    vm = _WbtVM(dx, deadline)
                    vm.statics, vm.inited = dict(pool.statics), set(pool.inited)
                    arr = _DxArr(vals)
                    arr.t = t
                    acc = dx.code[ref][3]
                    raw = [] if acc & 0x8 else [_DxObj(ref.split("->")[0])]
                    outs = [arr]
                    for k, p in enumerate(ps):
                        if k == ai:
                            raw.append(arr)
                        elif p in ("[B", "[I", "[C"):  # an output buffer the walk writes into
                            o = _DxArr([0] * len(vals))
                            o.t = p[1]
                            raw.append(o)
                            outs.append(o)
                        elif p in "JD":
                            raw += [0, None]
                        else:
                            raw.append(len(vals) if p == "I" and k == ai + 2 else _dxe_default(p))
                    try:
                        if not acc & 0x8 and ref.split("->")[0] + "-><init>()V" in dx.code:
                            vm.run(ref.split("->")[0] + "-><init>()V", raw[:1])
                        outs.append(vm.note(vm.run(ref, raw)))
                    except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError,
                            RecursionError, struct.error):
                        pass
                    for v in outs + vm.seen:
                        b = _wbt_bytes(v)
                        hits += [m.decode() for m in ANS_RE_B.findall(b)]
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))

_SWM_FIELD = re.compile(r"->(?:\$SwitchMap\$(.+)|\$EnumSwitchMapping\$\d+)$")


def switchmap_table(apk):
    """Enum switch maps of every dex (coverage atlas row 89): javac's `<Outer>$1.$SwitchMap$<pkg>$<Enum>` and kotlinc's
    `<Outer>$WhenMappings.$EnumSwitchMapping$N` int[]s, filled by their <clinit> from the enum's own <clinit>
    (Enum.<init>(name, ordinal) + $VALUES) and run by the dex_eval_scan interpreter. -> {"<map class>-><field>":
    {"enum": "L<pkg>/<Enum>;" | None, "cases": {"<CONST>" (or the ordinal when the enum is unknown): case key}}} --
    the packed-switch key each constant takes. {} when absent; never raises."""
    out = {}
    deadline = time.time() + 1.0
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            for ct, (sfl, _) in dx.sfields.items():
                maps = [(dx.fref(fi)[1], m) for fi in sfl for m in [_SWM_FIELD.search(dx.fref(fi)[1])] if m
                        and dx.fref(fi)[2] == "[I"]
                if not maps or time.time() > deadline:
                    continue
                vm = _DxVM(dx, deadline)
                try:
                    vm.init_class(ct)
                except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError,
                        RecursionError, struct.error):
                    continue
                enums = {}  # enum class -> {ordinal: name}, from the constants its <clinit> built
                for fk, v in vm.statics.items():
                    if isinstance(v, _DxObj) and "$ordinal" in v.f and fk.startswith(v.t + "->"):
                        enums.setdefault(v.t, {})[v.f["$ordinal"]] = v.f["$name"]
                for fk, m in maps:
                    arr = vm.statics.get(fk)
                    if not isinstance(arr, list) or not all(isinstance(x, int) for x in arr):
                        continue
                    if m.group(1):
                        e = [t for t in enums if t[1:-1].replace("/", "$") == m.group(1)]
                    else:
                        e = [t for t in enums if len(enums[t]) == len(arr)]
                    names = enums[e[0]] if len(e) == 1 else {}
                    out[fk] = {"enum": e[0] if len(e) == 1 else None,
                               "cases": {names.get(o, o): k for o, k in enumerate(arr) if k}}
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no table
        pass
    return out

# --- secondary-dex module contract (D20 TT `moduleContract`, coverage atlas) -------------------------------------------
# The host dex names a payload as `<entry>:<dotted class>` (`assets/payload.dex:com.huntress.arena.payload.Module`) and
# a contract member (`moduleContract`, an interface it calls through, a field such as ANSWER / CONTRACT). When the payload
# holds more than one ANS- candidate the member the host names decides: every static field (static_values + <clinit>
# sputs) and String-returning method of the payload is evaluated by the dex_eval_scan interpreter and ranked
#   host-named member > field/method named ANSWER / CONTRACT > host-interface method it implements > the rest.
_MC_PTR = re.compile(r"([\w./-]+\.(?:dex|jar|zip|apk|bin|dat)):([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)+)")
_MC_ID = re.compile(r"[A-Za-z_$][\w$]{1,63}")
_MC_NAMED = frozenset(("answer", "contract"))
_MC_GENERIC = frozenset(("toString", "<init>", "<clinit>", "valueOf", "values", "hashCode", "name", "get", "run",
                         "call", "apply", "invoke", "getClass", "length", "append", "INSTANCE", "TAG", "Companion"))
_MC_BUDGET_S, _MC_MAX_STR = 0.9, 200_000


def _mc_payloads(z, names):
    """[(entry, dex bytes)] of every non-top-level-classes dex: a bare dex entry or a jar/zip's classes*.dex (plain or
    single-byte xor'd, via _unwrap_nested), pointer-named entries first."""
    out = []
    infos = sorted((i for i in z.infolist() if 8 <= i.file_size <= _NEST_MAX_ENTRY
                    and not re.fullmatch(r"classes\d*\.dex", i.filename)), key=lambda i: i.filename not in names)
    for i in infos[:64]:
        try:
            u = _unwrap_nested(z.read(i))
            if u and u[0] == "dex":
                out.append((i.filename, u[1]))
            elif u:
                with zipfile.ZipFile(io.BytesIO(u[1])) as zin:
                    out += [(i.filename, zin.read(j)) for j in zin.infolist() if j.file_size <= _NEST_MAX_ENTRY
                            and re.fullmatch(r"classes\d*\.dex", j.filename)]
        except Exception:  # noqa: BLE001 - impostor entry
            continue
    return out


def _mc_ifaces(d, ct_want):
    """class descriptor -> [interface descriptors] for the classes in ct_want (class_def interfaces_off type_list)."""
    out = {}
    n_typ, o_typ = struct.unpack_from("<II", d, 0x40)
    n_cls, o_cls = struct.unpack_from("<II", d, 0x60)
    dx = _DxDex.__new__(_DxDex)
    dx.d, dx._s, dx.n_str, dx.o_str, dx.n_typ, dx.o_typ = d, {}, *struct.unpack_from("<II", d, 0x38), n_typ, o_typ
    for c in range(min(n_cls, 1 << 16)):
        ci, _, _, ioff = struct.unpack_from("<IIII", d, o_cls + 32 * c)
        ct = dx.typ(ci)
        if ct in ct_want and ioff and ioff + 4 <= len(d):
            k = struct.unpack_from("<I", d, ioff)[0]
            out[ct] = [dx.typ(t) for t in struct.unpack_from(f"<{min(k, 64)}H", d, ioff + 4)]
    return out


def module_contract_candidates(apk):
    """[(rank, member, ANS token)] for the host-named secondary-dex module, best first (rank 0 host-named member,
    1 ANSWER/CONTRACT, 2 host-interface method, 3 other member). [] when there is no payload dex; never raises."""
    res = []
    deadline = time.time() + _MC_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            hosts = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", i.filename)]
            hstr, hmeth, ptrs = set(), {}, []
            for d in hosts:
                if d[:4] != b"dex\n" or len(d) < 0x70:
                    continue
                try:
                    hx = _DxDex(d)
                    for k in range(min(hx.n_str, _MC_MAX_STR)):
                        s = hx.s(k)
                        if _MC_ID.fullmatch(s):
                            hstr.add(s)
                        ptrs += [(m.group(1), "L" + m.group(2).replace(".", "/") + ";") for m in _MC_PTR.finditer(s)]
                        if "." in s and _MC_ID.fullmatch(s.replace(".", "_").replace("$", "_")):
                            ptrs.append(("", "L" + s.replace(".", "/") + ";"))  # bare dotted name (loadClass arg)
                    for mi in range(min(hx.n_met, 1 << 18)):
                        ref = hx.mref(mi)
                        hmeth.setdefault(ref.split("->")[0], set()).add(ref.split("->")[1].split("(")[0])
                except Exception:  # noqa: BLE001 - malformed host dex
                    continue
            names = {e for e, _ in ptrs if e}
            pays = _mc_payloads(z, names)
        want_cls = {c for _, c in ptrs}
        for entry, d in pays:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001
                continue
            classes = [c for c in dx.sfields if not _DXE_LIB.match(c)]
            named = [c for c in classes if c in want_cls]
            ifs = _mc_ifaces(d, set(classes))
            for ct in named + [c for c in classes if c not in named]:
                if time.time() > deadline:
                    break
                imeth = set().union(*(hmeth.get(t, set()) for t in ifs.get(ct, ())))
                vm = _DxVM(dx, deadline)
                vals = []
                try:
                    vm.init_class(ct)
                except Exception:  # noqa: BLE001
                    pass
                for fi in dx.sfields[ct][0]:
                    fk = dx.fref(fi)[1]
                    vals.append((fk.split("->")[1], vm.statics.get(fk)))
                obj = None
                for ref in [r for r in dx.code if r.startswith(ct + "->") and r.endswith(")Ljava/lang/String;")]:
                    nm = ref.split("->")[1].split("(")[0]
                    ps = _dxe_params(ref)
                    if len(ps) > 4 or time.time() > deadline:
                        continue
                    raw = []
                    try:
                        if not dx.code[ref][3] & 0x8:
                            if obj is None:
                                obj = _DxObj(ct)
                                if f"{ct}-><init>()V" in dx.code:
                                    vm.run(f"{ct}-><init>()V", [obj], 1)
                            raw = [obj]
                        for p in ps:
                            raw += [_dxe_default(p)] + ([None] if p in "JD" else [])
                        vm.steps = 0
                        vals.append((nm, vm.run(ref, raw)))
                    except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError,
                            RecursionError, struct.error):
                        pass
                base = 0 if ct in named else 4
                for nm, v in vals:
                    if not isinstance(v, str):
                        continue
                    rank = (0 if nm in hstr and nm not in _MC_GENERIC else 1 if nm.lower() in _MC_NAMED
                            else 2 if nm in imeth and nm not in _MC_GENERIC else 3)
                    res += [(base + rank, f"{entry}:{ct}->{nm}", t) for t in ANS_RE_T.findall(v)]
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    res.sort(key=lambda r: r[0])
    return res


def module_contract_scan(apk):
    """ANS tokens of the host-named secondary-dex module's members, best-ranked first ([] when absent)."""
    return list(dict.fromkeys(t for _, _, t in module_contract_candidates(apk)))


def module_contract_answer(apk):
    """The single best module-contract value (rank of the host-named member), or None."""
    c = module_contract_candidates(apk)
    return c[0][2] if c else None


# --- pinned-digest payload selection ('challenge-signed' module, coverage atlas row 83) ---------------------------------
# The APK ships N candidate payloads (assets/payload_a.dex, payload_b.dex, modules/*.bin, a decoy jar) and the host pins
# the one it loads: a digest constant in the host dex (64/40/32/128/8 hex, colon hex, base64 / base64url, `sha256/`
# prefixed), a sidecar entry (*.sha256 / *.sig / *.digest, a JSON `sha256` / `digest` / `signature` field), or a detached
# RSA (PKCS#1 v1.5 / PSS) / Ed25519 / ECDSA signature + a shipped public key. Every non-META entry is digested (sha256 /
# sha1 / md5 / sha512 / crc32 / adler32 of the bytes and of an inner xor'd dex / jar classes.dex, plus a dex header's
# adler32 + sha1 signature fields); a payload whose MANIFEST.MF digest no longer matches (v1_manifest_verify "modified")
# is a tampered decoy and never selected. Only pin- or signature-selected payloads are scanned; the rest are demoted.
_PPS_SKIP = re.compile(r"classes\d*\.dex|AndroidManifest\.xml|resources\.arsc|META-INF/.*|.*/$", re.I)
_PPS_SIDE = re.compile(r"(?i).*\.(?:sig|sign|signature|sha\d*|md5|digest|hash|sum|crc|checksum|pin|json|txt|properties"
                       r"|xml|cfg|conf|ini|ya?ml|pem|pub|der|key|crt|cer)$")
_PPS_HEX = re.compile(rb"(?<![0-9A-Fa-f])(?:[0-9A-Fa-f]{2}:){15,63}[0-9A-Fa-f]{2}|(?<![0-9A-Za-z])[0-9A-Fa-f]{8,128}"
                      rb"(?![0-9A-Za-z])")
_PPS_B64 = re.compile(rb"[A-Za-z0-9+/_-]{11,172}={0,2}")
_PPS_PEM = re.compile(rb"-----BEGIN ((?:RSA |EC )?PUBLIC KEY|CERTIFICATE)-----[\sA-Za-z0-9+/=]+-----END \1-----")
_PPS_MAX_ENTRY, _PPS_MAX_SIDE, _PPS_MAX_PAY, _PPS_BUDGET_S = 32 << 20, 1 << 16, 32, 1.2


def _pps_digests(b):
    """{digest bytes: label} of a payload's bytes (+ an unwrapped inner dex / jar classes.dex) and dex header fields."""
    out = {}
    blobs = [("", b)]
    try:
        u = _unwrap_nested(b)
        if u and u[1] is not b:
            blobs.append((u[0] + ":", u[1]))
        if u and u[0] == "zip":
            with zipfile.ZipFile(io.BytesIO(u[1])) as zin:
                blobs += [(j.filename + ":", zin.read(j)) for j in zin.infolist()[:8]
                          if j.file_size <= _PPS_MAX_ENTRY and re.fullmatch(r"classes\d*\.dex", j.filename)]
    except Exception:  # noqa: BLE001 - impostor container
        pass
    for pre, x in blobs:
        for a in ("sha256", "sha1", "md5", "sha512"):
            out.setdefault(hashlib.new(a, x).digest(), pre + a)
        c, ad = zlib.crc32(x), zlib.adler32(x)
        out.setdefault(struct.pack(">I", c), pre + "crc32")
        out.setdefault(struct.pack(">I", ad), pre + "adler32")
        if x[:4] == b"dex\n" and len(x) >= 0x70:
            out.setdefault(x[8:12][::-1], pre + "dex_checksum")
            out.setdefault(x[12:32], pre + "dex_signature")
    return out


def _pps_pins(blob, strs=()):
    """Digest-sized byte strings a text / binary blob (or a host dex's string list) can pin: hex / colon hex, base64,
    base64url, decimal crc ints, and the raw bytes of a 16/20/32/64-byte binary blob."""
    pins = set()
    texts = list(strs) + ([blob] if blob else [])
    if blob and len(blob) in (4, 16, 20, 32, 64):
        pins.add(bytes(blob))
    for t in texts:
        if isinstance(t, str):
            t = t.encode("utf-8", "replace")
        for m in _PPS_HEX.finditer(t):
            h = m.group(0).replace(b":", b"")
            if len(h) in (8, 32, 40, 64, 128):
                pins.add(bytes.fromhex(h.decode()))
        for m in _PPS_B64.finditer(t):
            s = m.group(0).rstrip(b"=")
            if len(s) not in (6, 22, 27, 43, 86):
                continue
            try:
                pins.add(base64.b64decode(s.replace(b"-", b"+").replace(b"_", b"/") + b"=" * (-len(s) % 4)))
            except Exception:  # noqa: BLE001
                pass
        for m in re.finditer(rb"(?<![\w.])-?\d{6,10}(?![\w.])", t):
            v = int(m.group(0)) & 0xFFFFFFFF
            pins.add(struct.pack(">I", v))
    return pins


def _pps_sigs(z, side, deadline):
    """[(public key, signature bytes)] candidates: shipped PEM / DER public keys or certs x raw / base64 / hex
    signature blobs of a plausible size (64 Ed25519 / ECDSA DER / RSA modulus)."""
    try:
        from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_der_public_key
        from cryptography import x509
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except Exception:  # noqa: BLE001
        return [], []
    keys, sigs = [], []
    for name, b in side:
        for m in _PPS_PEM.finditer(b):
            try:
                pem = m.group(0)
                keys.append(x509.load_pem_x509_certificate(pem).public_key() if b"CERTIFICATE" in m.group(1)
                            else load_pem_public_key(pem))
            except Exception:  # noqa: BLE001
                pass
        if re.search(r"(?i)\.(?:der|pub|key)$", name) and not _PPS_PEM.search(b):
            try:
                keys.append(load_der_public_key(b) if len(b) != 32 else Ed25519PublicKey.from_public_bytes(b))
            except Exception:  # noqa: BLE001
                pass
        if re.search(r"(?i)\.(?:sig|sign|signature)$", name) or name.lower().endswith(".json"):
            cand = [b] if not name.lower().endswith(".json") else []
            for m in _PPS_B64.finditer(b) if len(b) < 4096 else ():
                s = m.group(0)
                try:
                    if len(s) >= 80:
                        cand.append(base64.b64decode(s.replace(b"-", b"+").replace(b"_", b"/") + b"=" * (-len(s) % 4)))
                except Exception:  # noqa: BLE001
                    pass
            for m in re.finditer(rb"[0-9A-Fa-f]{128,1024}", b):
                if len(m.group(0)) % 2 == 0:
                    cand.append(bytes.fromhex(m.group(0).decode()))
            sigs += [c for c in cand if 64 <= len(c) <= 1024]
    return keys[:4], list(dict.fromkeys(sigs))[:8]


def _pps_verify(key, sig, data):
    """True when sig is a valid RSA PKCS#1 v1.5 / PSS (sha256 / sha1 / sha512), Ed25519 or ECDSA signature of data."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa
    try:
        if isinstance(key, ed25519.Ed25519PublicKey):
            key.verify(sig, data)
            return True
        for h in (hashes.SHA256(), hashes.SHA1(), hashes.SHA512()):
            try:
                if isinstance(key, rsa.RSAPublicKey):
                    for pad in (padding.PKCS1v15(), padding.PSS(padding.MGF1(h), padding.PSS.AUTO)):
                        try:
                            key.verify(sig, data, pad, h)
                            return True
                        except Exception:  # noqa: BLE001
                            continue
                elif isinstance(key, ec.EllipticCurvePublicKey):
                    key.verify(sig, data, ec.ECDSA(h))
                    return True
            except Exception:  # noqa: BLE001
                continue
    except Exception:  # noqa: BLE001
        pass
    return False


def _pps_tokens(name, b):
    """ANS tokens of one payload: a direct scan, then raw_entry_scan + dex_strings on it re-laid as a one-entry APK."""
    hits = [m.group(0).decode() for m in ANS_RE_B.finditer(b)]
    try:
        u = _unwrap_nested(b)
        bio = io.BytesIO()
        if u and u[0] == "zip":
            bio = io.BytesIO(u[1])
        else:
            with zipfile.ZipFile(bio, "w") as zo:
                zo.writestr("classes.dex" if u else "assets/" + name.rsplit("/", 1)[-1], u[1] if u else b)
        hits += raw_entry_scan(bio) + dex_strings(bio)
    except Exception:  # noqa: BLE001
        pass
    return list(dict.fromkeys(hits))


def pinned_payload_candidates(apk):
    """[{"entry", "rank", "why", "tokens"}] for every candidate payload entry, selected first: rank 0 signature-verified,
    1 digest pin matched (host dex / sidecar), 2 unpinned (demoted, not scanned), 3 pinned but its MANIFEST.MF digest
    no longer matches (tampered decoy). [] when there is no payload or no pin / signature at all; never raises."""
    deadline = time.time() + _PPS_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            infos = [i for i in z.infolist() if not _PPS_SKIP.fullmatch(i.filename) and 8 <= i.file_size <= _PPS_MAX_ENTRY]
            side = [(i.filename, z.read(i)) for i in infos if _PPS_SIDE.fullmatch(i.filename)
                    and i.file_size <= _PPS_MAX_SIDE]
            side_names = {n for n, _ in side}
            pays = [i for i in infos if i.filename not in side_names and not i.filename.startswith("lib/")
                    and not re.search(r"(?i)\.(?:png|jpe?g|webp|gif|ogg|mp3|ttf|otf|kotlin_builtins|kotlin_module)$",
                                      i.filename)][:_PPS_MAX_PAY]
            if len(pays) < 1 or (not side and not any(re.fullmatch(r"classes\d*\.dex", i.filename)
                                                      for i in z.infolist())):
                return []
            hstr = []
            for i in z.infolist():
                if re.fullmatch(r"classes\d*\.dex", i.filename) and i.file_size <= _PPS_MAX_ENTRY:
                    try:
                        hx = _DxDex(z.read(i))
                        hstr += [hx.s(k) for k in range(min(hx.n_str, 200_000))]
                    except Exception:  # noqa: BLE001 - malformed host dex
                        continue
            pins = _pps_pins(b"", [s for s in hstr if len(s) <= 256])
            for n, b in side:
                pins |= _pps_pins(b)
            keys, sigs = _pps_sigs(z, side, deadline)
            pay_bytes = [(i.filename, z.read(i)) for i in pays]
        mod = set()
        try:
            v = v1_manifest_verify(apk)
            mod = set((v or {}).get("modified") or ())
        except Exception:  # noqa: BLE001
            pass
        out = []
        for name, b in pay_bytes:
            digs = _pps_digests(b)
            why = [digs[p] for p in pins if p in digs]
            signed = any(_pps_verify(k, s, b) for k in keys for s in sigs) if keys and sigs \
                and time.time() < deadline else False
            rank = 0 if signed else 1 if why else 2
            if rank < 2 and name in mod:
                rank = 3
            out.append({"entry": name, "rank": rank, "why": (["signature"] if signed else []) + why, "tokens": []})
        if not any(c["rank"] < 2 for c in out):
            return []
        for c in out:
            if c["rank"] < 2 and time.time() < deadline + 0.5:
                c["tokens"] = _pps_tokens(c["entry"], dict(pay_bytes)[c["entry"]])
        out.sort(key=lambda c: c["rank"])
        return out
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        return []


def pinned_payload_scan(apk):
    """ANS tokens of the pin / signature-selected payload(s) only (signature first), [] when none is selected."""
    return list(dict.fromkeys(t for c in pinned_payload_candidates(apk) if c["rank"] < 2 for t in c["tokens"]))


def pinned_payload_answer(apk):
    """The first token of the best-selected payload, or None."""
    h = pinned_payload_scan(apk)
    return h[0] if h else None



# --- virtualised method: custom bytecode program + in-dex VM interpreter (coverage atlas row 81) -----------------------
# A method `while (pc < code.length) switch (code[pc++]) {push / xor / add / rol / load / store / emit-char / loop ...}`
# run over a [B/[I/[C program (fill-array-data literal) or a base64 / hex const-string. dex_eval_scan gives up when the
# program spins past its 50k-step budget or the caller makes an unknown framework call; here each VM-shaped method (a
# packed/sparse-switch dispatching on an array element) is re-run by the same interpreter with a larger step budget:
# first via its in-dex no-arg callers, then directly with every program literal of its own / its callers' classes.
_VMB_STEPS, _VMB_BUDGET_S, _VMB_MAX_ARGS = 1_500_000, 1.2, 24
_VMB_HEX = re.compile(r"(?:[0-9A-Fa-f]{2}){8,}")
_VMB_B64 = re.compile(r"[A-Za-z0-9+/_-]{12,}={0,2}")


class _VmbVM(_DxVM):
    max_steps = _VMB_STEPS


def _vmb_literals(dx, refs):
    """(array literals {width: [element lists]}, const-strings) of the given methods' code items."""
    arrs, strs = {1: [], 2: [], 4: []}, []
    for ref in refs:
        ins = dx.code[ref][2]
        for op, o in _dga_ops(ins):
            if op in (0x1A, 0x1B):
                strs.append(dx.s(struct.unpack_from("<H" if op == 0x1A else "<I", ins, o + 2)[0]))
            elif op == 0x26:
                q = o + 2 * struct.unpack_from("<i", ins, o + 2)[0]
                if 0 <= q and ins[q:q + 2] == b"\x00\x03":
                    ew, n = struct.unpack_from("<HI", ins, q + 2)
                    if ew in arrs and 4 <= n <= _DXE_MAX_ARR and q + 8 + ew * n <= len(ins):
                        arrs[ew].append([int.from_bytes(ins[q + 8 + ew * k:q + 8 + ew * (k + 1)], "little",
                                                        signed=ew != 2) for k in range(n)])
    return arrs, list(dict.fromkeys(x for x in strs if isinstance(x, str)))


def _vmb_args(p, arrs, strs):
    """Candidate values for one VM parameter descriptor."""
    out = []
    if p == "Ljava/lang/String;":
        out = [x for x in strs if _VMB_B64.fullmatch(x) or _VMB_HEX.fullmatch(x)]
    elif p in ("[B", "[I", "[C"):
        ew = {"[B": 1, "[I": 4, "[C": 2}[p]
        for el in arrs[ew] + ([list(_dxe_barr(b)) for b in (_vmb_bytes(x) for x in strs) if b] if ew == 1 else []):
            a = _DxArr(el)
            a.t = p[1]
            out.append(a)
    return out


def _vmb_bytes(x):
    try:
        if _VMB_HEX.fullmatch(x):
            return bytes.fromhex(x)
        if _VMB_B64.fullmatch(x):
            return base64.b64decode(x.replace("-", "+").replace("_", "/") + "=" * (-len(x) % 4), validate=True)
    except (ValueError, binascii.Error):
        pass
    return None


def bytecode_vm_scan(apk):
    """ANS tokens emitted by a virtualised method: a custom bytecode program (byte/int/char[] fill-array-data literal or
    base64 / hex const-string) run by an in-dex VM (loop + packed/sparse-switch on program[pc]). Each VM-shaped app
    method is re-run by the dex_eval_scan interpreter with a 1.5M-step budget -- through its in-dex callers (params
    defaulted), then directly with each program literal of its class and its callers' classes as the argument (the
    instance built by its no-arg <init>). Every string it builds or returns is regex'd. [] when absent; never raises."""
    hits = []
    deadline = time.time() + _VMB_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            vms = []
            for ref in dx.order:
                if _DXE_LIB.match(ref):
                    continue
                ops = set(dx.code[ref][2][0::2])
                if not ops.isdisjoint((0x2B, 0x2C)) and not ops.isdisjoint(range(0x44, 0x4B)) \
                        and len(_dxe_params(ref)) <= 3:
                    vms.append(ref)
            if not vms:
                continue
            want, callers = set(vms), {v: [] for v in vms}
            for ref in dx.order:
                for op, o in _dga_ops(dx.code[ref][2]):
                    if 0x6E <= op <= 0x72 or 0x74 <= op <= 0x78:
                        t = dx.mref(struct.unpack_from("<H", dx.code[ref][2], o + 2)[0])
                        if t in want and ref not in callers[t]:
                            callers[t].append(ref)
            runs = []
            for v in vms:
                runs += [(c, None) for c in callers[v] if len(_dxe_params(c)) <= 4]
            for v in vms:
                cls = {v.split("->")[0]} | {c.split("->")[0] for c in callers[v]}
                arrs, strs = _vmb_literals(dx, [r for r in dx.order if r.split("->")[0] in cls])
                ps = _dxe_params(v)
                slots = [i for i, p in enumerate(ps) if p in ("Ljava/lang/String;", "[B", "[I", "[C")]
                if len(slots) == 1:
                    runs += [(v, (slots[0], a)) for a in _vmb_args(ps[slots[0]], arrs, strs)[:_VMB_MAX_ARGS]]
            for ref, fill in runs:
                if time.time() > deadline:
                    break
                vm = _VmbVM(dx, deadline)
                ct = ref.split("->")[0]
                acc = dx.code[ref][3]
                try:
                    vm.init_class(ct)
                    raw = []
                    if not acc & 0x8:
                        obj = _DxObj(ct)
                        if f"{ct}-><init>()V" in dx.code:
                            vm.run(f"{ct}-><init>()V", [obj], 1)
                        raw = [obj]
                    for i, p in enumerate(_dxe_params(ref)):
                        raw += [fill[1] if fill and fill[0] == i else _dxe_default(p)] + ([None] if p in "JD" else [])
                    vm.steps = 0
                    vm.note(vm.run(ref, raw))
                except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError,
                        RecursionError, struct.error):
                    pass
                for s_ in vm.seen + [x for x in vm.statics.values() if isinstance(x, str)]:
                    hits += ANS_RE_T.findall(s_)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))

# --- root / emulator / debugger / Frida checks evaluated as a clean physical device (coverage atlas rows 41, 47, 48) --
# The evaluator above with a 'clean Pixel' environment: su / magisk / busybox / frida / xposed / qemu paths do not exist,
# Build.* is a Pixel 6 release build, no debugger / tracer / adb, ro.kernel.qemu unset, /proc/self/{status,maps} are
# clean, Frida's ports refuse, root / hook packages and classes are absent (NameNotFound / ClassNotFound reach the
# method's own catch handler). Each method touching those APIs / strings, and its in-dex callers, runs on that path.
_ENV_FP = "google/oriole/oriole:14/UQ1A.240205.004/11269751:user/release-keys"
_ENV_STATICS = {f"Landroid/os/Build;->{k}": v for k, v in (
    ("TAGS", "release-keys"), ("FINGERPRINT", _ENV_FP), ("MODEL", "Pixel 6"), ("MANUFACTURER", "Google"),
    ("BRAND", "google"), ("DEVICE", "oriole"), ("PRODUCT", "oriole"), ("HARDWARE", "oriole"), ("BOARD", "oriole"),
    ("BOOTLOADER", "slider-1.3-11180583"), ("HOST", "abfarm-release-2004-0050"), ("USER", "android-build"),
    ("TYPE", "user"), ("ID", "UQ1A.240205.004"), ("DISPLAY", "UQ1A.240205.004"), ("SERIAL", "unknown"),
    ("RADIO", "g5123b-130914-240205-B-11405587"), ("SUPPORTED_ABIS", None), ("CPU_ABI", "arm64-v8a"))}
_ENV_STATICS.update({"Landroid/os/Build$VERSION;->SDK_INT": 34, "Landroid/os/Build$VERSION;->RELEASE": "14",
                     "Landroid/os/Build$VERSION;->INCREMENTAL": "11269751", "Landroid/os/Build$VERSION;->CODENAME": "REL"})
_ENV_ABSENT = re.compile(r"(?i)(?:^|/)(?:su|busybox|daemonsu|sugote\w*|supolicy)$|magisk|supersu|superuser|frida|xposed"
                         r"|lsposed|substrate|/data/adb|/sbin/|qemu|goldfish|ranchu|genyd|genymotion|nox|bluestacks"
                         r"|/system/(?:xbin|sd/xbin|bin/failsafe)/|/data/local/(?:tmp/|bin/|xbin/)|/su/|kinguser|rootcloak"
                         r"|/dev/socket/(?:qemud|baseband)|vbox|andy|/system/app/super")
_ENV_PKG = re.compile(r"(?i)magisk|supersu|superuser|chainfire|koushikdutta|kingroot|kinguser|xposed|lsposed|edxp"
                      r"|saurik|substrate|rootcloak|devadvance|zachspong|ramdroid|frida|luckypatcher|chelpus|root"
                      r"|zygisk|riru|shamiko|kernelsu|apatch")
# probe args built at runtime (rows 47, 48, 94): the stubs see the evaluated string, normalised (// collapsed, trailing
# / stripped, casefolded) before lookup; an unknown path under the root-tool trees is absent on a clean device.
_ENV_ROOTTREE = re.compile(r"/(?:system|sbin|su|data/local|data/adb|cache)/.")
_ENV_FILES = {
    "/proc/self/status": "Name:\tapp\nUmask:\t0077\nState:\tS (sleeping)\nTgid:\t12345\nNgid:\t0\nPid:\t12345\n"
                         "PPid:\t678\nTracerPid:\t0\nUid:\t10234\t10234\t10234\t10234\nGid:\t10234\t10234\t10234\t10234\n"
                         "FDSize:\t128\nThreads:\t17\nSeccomp:\t2\n",
    "/proc/self/maps": "5d1c2a3000-5d1c2a5000 r--p 00000000 fd:05 1234 /system/bin/app_process64\n"
                       "7a1b200000-7a1b2d0000 r--p 00000000 fd:05 2345 /apex/com.android.runtime/lib64/bionic/libc.so\n"
                       "7a1c000000-7a1c400000 r--p 00000000 fd:21 3456 /data/app/~~x==/base.apk\n"
                       "7ffd5000000-7ffd5021000 rw-p 00000000 00:00 0 [stack]\n"}
# instrumentation false positives (rows 48, 91): the rest of a stock ART process's maps -- libart / libandroid_runtime /
# boot oat, dalvik heaps, the JIT's r-xp memfd (an exec anon mapping that is NOT an injected agent), the app's oat; and
# /proc/net/tcp{,6} with ephemeral :443 sockets only (no :69A2 / :69A3 local port; one peer IP hex holds a bare "69A2").
_ENV_FILES["/proc/self/maps"] += (
    "70a1e000-70c4a000 rw-p 00000000 00:00 0 [anon:dalvik-/system/framework/boot.art]\n"
    "7a1d100000-7a1d900000 r--p 00000000 fd:05 4567 /apex/com.android.art/lib64/libart.so\n"
    "7a1d900000-7a1dc80000 r-xp 00800000 fd:05 4567 /apex/com.android.art/lib64/libart.so\n"
    "7a1e000000-7a1e0c0000 r-xp 00000000 fd:05 5678 /system/lib64/libandroid_runtime.so\n"
    "7a1e400000-7a1e480000 r-xp 00000000 fd:05 6789 /system/lib64/libandroid.so\n"
    "7a1e800000-7a1e900000 r-xp 00000000 fd:05 7890 /system/framework/arm64/boot-framework.oat\n"
    "7a1f000000-7a1f040000 rw-p 00000000 00:00 0 [anon:dalvik-LinearAlloc]\n"
    "7a1f100000-7a1f500000 rw-p 00000000 00:00 0 [anon:dalvik-main space (region space)]\n"
    "7a1f600000-7a1f800000 r-xp 00000000 00:01 8901 /memfd:jit-cache (deleted)\n"
    "7a1f800000-7a1fa00000 r--p 00000000 00:01 8901 /memfd:jit-cache (deleted)\n"
    "7a20000000-7a20020000 r--p 00000000 fd:21 3457 /data/app/~~x==/oat/arm64/base.odex\n"
    "7a20100000-7a20140000 r-xp 00000000 fd:05 9012 /system/lib64/libgui.so\n"
    "7a20200000-7a20210000 r--s 00000000 00:16 9123 /dev/__properties__/u:object_r:default_prop:s0\n"
    "7a20300000-7a20400000 r-xp 00000000 fd:05 9234 /apex/com.android.runtime/bin/linker64\n"
    "7ffd5100000-7ffd5102000 r-xp 00000000 00:00 0 [vdso]\n")
_ENV_FILES["/proc/12345/maps"] = _ENV_FILES["/proc/self/maps"]
_ENV_FILES["/proc/net/tcp"] = _ENV_FILES["/proc/self/net/tcp"] = (
    "  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode\n"
    "   0: 172AB10A:A3F2 2E0E7A8E:01BB 01 00000000:00000000 00:00000000 00000000 10234        0 48213 1 0 20 4 30 10 -1\n"
    "   1: 172AB10A:C81E 69A2FB8E:01BB 01 00000000:00000000 00:00000000 00000000 10234        0 48290 1 0 21 4 30 10 -1\n"
    "   2: 172AB10A:D0A4 C1E8D9AC:01BB 06 00000000:00000000 03:00000F2A 00000000     0        0 0 3 0\n")
_ENV_FILES["/proc/net/tcp6"] = _ENV_FILES["/proc/self/net/tcp6"] = (
    "  sl  local_address                         remote_address                        st tx_queue rx_queue tr "
    "tm->when retrnsmt   uid  timeout inode\n"
    "   0: 0000000000000000FFFF0000172AB10A:B1C6 0000000000000000FFFF00004E0F7A8E:01BB 01 00000000:00000000 "
    "00:00000000 00000000 10234        0 48311 1 0 20 4 30 10 -1\n")
# PackageManager.getInstalledPackages / getInstalledApplications: a stock Pixel's apps + a few Play installs (no frida
# server / Xposed / LSPosed / Magisk managers); near misses by design: com.google.android.gm(s), android.ext.shared
_ENV_INSTALLED = ("android", "com.android.systemui", "com.android.settings", "com.android.phone", "com.android.vending",
                  "com.google.android.gms", "com.google.android.gsf", "com.google.android.gm",
                  "com.google.android.apps.maps", "com.google.android.youtube", "com.android.chrome",
                  "com.google.android.apps.messaging", "com.google.android.dialer", "com.google.android.apps.photos",
                  "com.google.android.inputmethod.latin", "com.android.providers.downloads", "android.ext.shared",
                  "com.google.android.webview", "com.whatsapp", "com.spotify.music")
_ENV_FILES["/proc/" + "12345/status"] = _ENV_FILES["/proc/self/status"]
_ENV_PORTS = frozenset((27042, 27043, 27047, 23946, 5555, 5037))
_ENV_NEW = frozenset(("Ljava/io/File;", "Ljava/io/FileReader;", "Ljava/io/FileInputStream;", "Ljava/io/InputStreamReader;",
                      "Ljava/io/BufferedReader;", "Ljava/net/Socket;", "Ljava/net/InetSocketAddress;", "Ljava/util/Scanner;",
                      "Ljava/lang/ProcessBuilder;"))
_ENV_MARK = re.compile(r"(?i)Landroid/os/(?:Build|Debug)|isDebuggerConnected|waitingForDebugger|getPackageInfo"
                       r"|getApplicationInfo|Ljava/net/Socket;|Ljava/io/File;-><init>|getProperty|forName|Runtime;->exec|ProcessBuilder;-><init>"
                       r"|Settings\$(?:Secure|Global)|Landroid/os/SystemClock;|Ljava/lang/System;->(?:nanoTime|currentTimeMillis)"
                       r"|Ldalvik/system/VMDebug;|Landroid/os/SystemProperties;|getStackTrace|getAllStackTraces"
                       r"|Ljava/lang/reflect/Modifier;->isNative|ClassLoader;->loadClass|Landroid/system/Os;->readlink"
                       r"|Ljava/lang/System;->getenv|getInstalled(?:Packages|Applications)"
                       r"|Landroid/telephony/TelephonyManager;|Landroid/hardware/SensorManager;|Landroid/os/BatteryManager;"
                       r"|Ljava/net/NetworkInterface;->getNetworkInterfaces"
                       r"|getInstallerPackageName|getInstallSourceInfo|getPackageCodePath|getPackageResourcePath"
                       r"|Landroid/content/pm/(?:Signature|SigningInfo);|Ljava/util/(?:zip/ZipFile|jar/JarFile);-><init>")
# timing anti-debug + debug-flag probes (rows 50, 88): every clock read advances a monotonic counter by 1 ms, so a
# `t1 - t0 < threshold` check passes; Thread.sleep is a no-op; hidden SystemProperties (direct or via reflection) and
# VMDebug answer as a user build with adb off. BuildConfig.DEBUG keeps its encoded value AND is re-run as false.
_ENV_CLOCK = re.compile(r"Ljava/lang/System;->(?:nanoTime|currentTimeMillis)\(|Landroid/os/SystemClock;->"
                        r"(?:elapsedRealtime|uptimeMillis|currentThreadTime)|Landroid/os/Debug;->threadCpuTimeNanos\(")
_ENV_PROPS = {"ro.debuggable": "0", "ro.secure": "1", "service.adb.root": "0", "ro.adb.secure": "1",
              "ro.build.tags": "release-keys", "ro.build.type": "user", "ro.build.fingerprint": _ENV_FP,
              "ro.product.model": "Pixel 6", "ro.hardware": "oriole", "ro.boot.verifiedbootstate": "green",
              "ro.boot.flash.locked": "1", "ro.kernel.qemu": "", "ro.boot.qemu": "", "ro.kernel.android.qemud": "",
              "init.svc.adbd": "stopped", "sys.usb.config": "mtp", "persist.sys.usb.config": "mtp"}
_ENV_BCDBG = re.compile(r"/BuildConfig;->DEBUG$")
_ENV_STEPS, _ENV_BUDGET_S, _ENV_MAX_RUNS = 100_000, 0.8, 96
_ENV_NNF = ("Landroid/content/pm/PackageManager$NameNotFoundException;", "Landroid/util/AndroidException;")
_ENV_IOE = ("Ljava/io/IOException;",)
_ENV_UNSET = object()
# hook-framework introspection (row 91): Frida / Xposed / Substrate checks that read the VM's own stack, its threads,
# /proc/self/task/*/comm, /proc/self/fd links, reflection modifiers or env vars see a stock ART process: frames are
# VMStack / Thread, the evaluator's own call chain, then one ActivityThread -> ZygoteInit tail (no XposedBridge / MS$2);
# threads are ART's daemons + binders (no gum-js-loop / gmain / pool-frida); fds point at /dev/null, apks and sockets.
_HK_TAIL = ("android.os.Handler.dispatchMessage", "android.os.Looper.loop", "android.app.ActivityThread.main",
            "java.lang.reflect.Method.invoke", "com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run",
            "com.android.internal.os.ZygoteInit.main")
_HK_THREADS = ("main", "Signal Catcher", "perfetto_hprof_listener", "Jit thread pool", "HeapTaskDaemon",
               "ReferenceQueueDaemon", "FinalizerDaemon", "FinalizerWatchdogDaemon", "Binder:12345_1", "Binder:12345_2",
               "Binder:12345_3", "Profile Saver", "RenderThread")
_HK_TASKS = {12345 + i: n[:15] for i, n in enumerate(("app",) + _HK_THREADS[1:])}
_HK_FDS = {0: "/dev/null", 1: "/dev/null", 2: "/dev/null", 3: "/apex/com.android.art/javalib/core-oj.jar",
           4: "/apex/com.android.art/javalib/core-libart.jar", 5: "/system/framework/framework.jar", 6: "/dev/binder",
           7: "anon_inode:[eventfd]", 8: "anon_inode:[eventpoll]", 9: "socket:[48213]", 10: "pipe:[48214]",
           11: "pipe:[48214]", 12: "/dev/ashmem", 13: "/data/app/~~x==/base.apk", 14: "/dev/hwbinder"}
_HK_DIRS = {"/proc/self/task": [str(t) for t in _HK_TASKS], "/proc/self/fd": [str(f) for f in _HK_FDS]}
for _t, _n in _HK_TASKS.items():
    _ENV_FILES[f"/proc/self/task/{_t}/comm"] = _n + "\n"
    _ENV_FILES[f"/proc/self/task/{_t}/status"] = f"Name:\t{_n}\nState:\tS (sleeping)\nTracerPid:\t0\n"
_HK_NEW = frozenset(("Ljava/lang/Throwable;", "Ljava/lang/Exception;", "Ljava/lang/RuntimeException;"))
# emulator checks beyond Build fields (row 48): a retail phone on T-Mobile -- IMEI-shaped device id, GSM, SIM ready, 24
# vendor sensors (no Goldfish / AOSP), battery 63 % / 28.5 C / unplugged / discharging, arm64 /proc/cpuinfo without
# Goldfish / hypervisor, wlan0 + rmnet + lo interfaces (no 10.0.2.15 / eth0); qemu pipes / sockets are _ENV_ABSENT.
_EMU_TEL = {"getDeviceId": "352099001761481", "getImei": "352099001761481", "getMeid": None,
            "getSubscriberId": "310260417291538", "getLine1Number": "+12065550147", "getVoiceMailNumber": "+18056377243",
            "getSimSerialNumber": "8901260417291538470", "getNetworkOperatorName": "T-Mobile",
            "getSimOperatorName": "T-Mobile", "getNetworkOperator": "310260", "getSimOperator": "310260",
            "getNetworkCountryIso": "us", "getSimCountryIso": "us", "getPhoneType": 1, "getSimState": 5,
            "getNetworkType": 13, "getDataNetworkType": 13, "getCallState": 0, "getDataState": 2,
            "isNetworkRoaming": 0, "hasIccCard": 1, "getPhoneCount": 2, "getActiveModemCount": 2,
            "getDeviceSoftwareVersion": "01", "getMmsUserAgent": "pixel6", "isVoiceCapable": 1, "isSmsCapable": 1}
_EMU_SENSORS = tuple((t, n, v) for t, n, v in (
    (1, "LSM6DSR Accelerometer", "STMicro"), (2, "MMC56X3X Magnetometer", "memsic"), (4, "LSM6DSR Gyroscope", "STMicro"),
    (5, "TMD3702V Ambient Light Sensor", "AMS"), (6, "ICP10101 Pressure Sensor", "TDK-Invensense"),
    (8, "TMD3702V Proximity Sensor", "AMS"), (9, "Gravity Sensor", "Google"), (10, "Linear Acceleration Sensor", "Google"),
    (11, "Rotation Vector Sensor", "Google"), (14, "MMC56X3X Magnetometer Uncalibrated", "memsic"),
    (15, "Game Rotation Vector Sensor", "Google"), (16, "LSM6DSR Gyroscope Uncalibrated", "STMicro"),
    (17, "Significant Motion Detector", "Google"), (18, "Step Detector", "Google"), (19, "Step Counter", "Google"),
    (20, "Geomagnetic Rotation Vector Sensor", "Google"), (22, "Tilt Detector", "Google"),
    (25, "Pick Up Gesture", "Google"), (27, "Device Orientation", "Google"),
    (35, "LSM6DSR Accelerometer Uncalibrated", "STMicro"), (30, "Motion Detect", "Google"),
    (65536, "Double Twist", "Google"), (65537, "Double Tap", "Google"), (65538, "Device Temperature", "Google")))
_EMU_BATTERY = {"level": 63, "scale": 100, "temperature": 285, "voltage": 3871, "status": 3, "plugged": 0, "health": 2,
                "icon-small": 17303637, "present": 1, "technology": "Li-ion", "battery_low": 0}
_EMU_BATPROP = {1: 2_904_000, 2: -352_000, 3: -341_000, 4: 63, 5: 0, 6: 3}  # BatteryManager.BATTERY_PROPERTY_*
_EMU_IFACES = (("wlan0", ("192.168.1.23", "fe80::8a3b:2dff:fe14:9c07%wlan0")), ("rmnet_data1", ("10.177.42.9",)),
               ("dummy0", ()), ("lo", ("127.0.0.1", "::1%1")))
_EMU_SVC = {"phone": "Landroid/telephony/TelephonyManager;", "sensor": "Landroid/hardware/SensorManager;",
            "batterymanager": "Landroid/os/BatteryManager;"}
_EMU_LIST = frozenset(("Ljava/util/List;", "Ljava/util/ArrayList;", "Ljava/util/Collection;", "Ljava/lang/Iterable;",
                       "Ljava/util/Iterator;", "Ljava/util/Enumeration;"))
_ENV_FILES["/proc/cpuinfo"] = "".join(
    f"processor\t: {i}\nBogoMIPS\t: 49.15\nFeatures\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics fphp asimdhp"
    f" cpuid asimdrdm lrcpc dcpop asimddp\nCPU implementer\t: 0x41\nCPU architecture: 8\nCPU variant\t: "
    f"{'0x1' if i > 3 else '0x2'}\nCPU part\t: {'0xd05' if i < 4 else '0xd41' if i < 6 else '0xd44'}\nCPU revision\t: 0\n\n"
    for i in range(8)) + "Hardware\t: Tensor\n"
_ENV_FILES["/proc/version"] = ("Linux version 5.10.157-android13-4-00001-g5c7ff5dc7aac-ab10381520 (build-user@build-host) "
                               "(Android (8508608, based on r450784e) clang version 14.0.7) #1 SMP PREEMPT Tue Jun 27 "
                               "14:13:03 UTC 2023\n")
# shell probes (row 95): Runtime.exec(String | String[]) and ProcessBuilder(..).start() run on the clean Pixel's
# toybox. su / magisk / busybox and absent paths throw IOException ("Cannot run program"); `which su` prints nothing
# and exits 1; getprop / getenforce / id / whoami / mount / cat / ls / uname / echo / sh -c "<one command>" print what
# the retail phone prints (exit 0); any other command aborts the run. The mount table has no rw /system, magisk, tmpfs
# over /system or overlay; File("/proc/mounts" | "/proc/self/mountinfo") reads give the same table.
_ENV_MOUNTS = (("/dev/block/dm-6", "/", "ext4", "ro,seclabel,relatime"),
               ("/dev/block/dm-7", "/system_ext", "ext4", "ro,seclabel,relatime"),
               ("/dev/block/dm-8", "/product", "ext4", "ro,seclabel,relatime"),
               ("/dev/block/dm-9", "/vendor", "ext4", "ro,seclabel,relatime"),
               ("tmpfs", "/dev", "tmpfs", "rw,seclabel,nosuid,relatime,mode=755"),
               ("/dev/block/dm-48", "/data", "f2fs", "rw,lazytime,seclabel,nosuid,nodev,noatime"))
_ENV_FILES["/proc/mounts"] = _ENV_FILES["/proc/self/mounts"] = "".join(f"{d} {m} {t} {o} 0 0\n" for d, m, t, o in _ENV_MOUNTS)
_ENV_FILES["/proc/self/mountinfo"] = "".join(f"{20 + i} {19 if i else 1} 253:{6 + i} / {m} {o.split(',seclabel')[0]} "
                                             f"shared:{i + 1} - {t} {d} {o}\n" for i, (d, m, t, o) in enumerate(_ENV_MOUNTS))
_ENV_ID = "uid=10234(u0_a234) gid=10234(u0_a234) groups=10234(u0_a234),3003(inet),9997(everybody),20234(u0_a234_cache)," \
          "50234(all_a234) context=u:r:untrusted_app:s0:c234,c256,c512,c768"
_ENV_TOYBOX = frozenset(("sh", "getprop", "getenforce", "id", "whoami", "mount", "cat", "ls", "uname", "echo", "which",
                         "toybox", "test", "ps", "pm", "settings", "grep", "stat", "df", "env", "setprop", "logcat"))
_ENV_SH_PROBES = frozenset(("getprop", "getenforce", "which", "mount", "/system/bin/getprop", "/system/bin/sh"))
_ENV_SH_META = re.compile(r"[|;&<>$`()*?\[\]'\"\\]")


def _env_shell(argv):
    """(stdout text, exit code) of one command line on the clean Pixel; _DxThrow(IOException) when the program does
    not exist; _DxAbort for a command the model does not know."""
    if not argv or not all(isinstance(x, str) for x in argv):
        raise _DxAbort
    prog, args = argv[0].strip(), [x.strip() for x in argv[1:]]
    base = prog.rsplit("/", 1)[-1]
    if "/" in prog and not (_env_norm(prog).rsplit("/", 1)[0] == "/system/bin" and base in _ENV_TOYBOX):
        if _env_absent(prog):
            raise _DxThrow(*_ENV_IOE)
        raise _DxAbort
    if base not in _ENV_TOYBOX:
        if _ENV_ABSENT.search(base) or _ENV_PKG.search(base):
            raise _DxThrow(*_ENV_IOE)
        raise _DxAbort
    if base == "toybox" and args:
        return _env_shell(args)
    if base == "sh" and len(args) == 2 and args[0] == "-c" and not _ENV_SH_META.search(args[1]):
        return _env_shell(args[1].split())
    if base == "which" and len(args) == 1:
        t = args[0].rsplit("/", 1)[-1]
        if t in _ENV_TOYBOX and "/" not in args[0]:
            return f"/system/bin/{t}\n", 0
        if _ENV_ABSENT.search(args[0]) or _ENV_PKG.search(t):
            return "", 1
        raise _DxAbort
    if base == "getprop":
        if not args:
            return "".join(f"[{k}]: [{v}]\n" for k, v in sorted(_ENV_PROPS.items())), 0
        if len(args) <= 2 and (args[0] in _ENV_PROPS or _ENV_ABSENT.search(args[0])):
            v = _ENV_PROPS.get(args[0], "")
            return (v or (args[1] if len(args) > 1 else "")) + "\n", 0
        raise _DxAbort
    if base == "getenforce" and not args:
        return "Enforcing\n", 0
    if base == "id" and not args:
        return _ENV_ID + "\n", 0
    if base == "id" and args in (["-u"], ["-g"]):
        return "10234\n", 0
    if base == "whoami" and not args or base == "id" and args in (["-un"], ["-nu"], ["-u", "-n"], ["-n", "-u"]):
        return "u0_a234\n", 0
    if base == "mount" and not args:
        return "".join(f"{d} on {m} type {t} ({o})\n" for d, m, t, o in _ENV_MOUNTS), 0
    if base == "uname" and len(args) == 1 and args[0] in ("-r", "-m", "-s"):
        return {"-r": "5.10.157-android13-4-00001-g5c7ff5dc7aac-ab10381520\n", "-m": "aarch64\n",
                "-s": "Linux\n"}[args[0]], 0
    if base == "echo" and not _ENV_SH_META.search(" ".join(args)):
        return " ".join(args) + "\n", 0
    if base in ("cat", "ls") and len(args) == 1 and not args[0].startswith("-"):
        if _env_absent(args[0]):
            return "", 1
        f = _env_file(args[0])
        if base == "cat" and f is not None:
            return f, 0
        if base == "ls" and f is not None:
            return args[0] + "\n", 0
    if base == "test" and len(args) == 2 and args[0] in ("-e", "-f", "-x", "-d") and _env_absent(args[1]):
        return "", 1
    raise _DxAbort


def _env_argv(v):
    """The argv of an exec / ProcessBuilder command: a String (StringTokenizer split), a String[] or a List."""
    if isinstance(v, str):
        return v.split()
    if isinstance(v, _DxObj):
        v = v.f.get("rs", v.f.get("sl"))
    if isinstance(v, list) and v and all(isinstance(x, str) for x in v):
        return list(v)
    raise _DxAbort


def _env_path(v):
    if isinstance(v, _DxObj) and v.t == "Ljava/io/File;":
        v = v.f.get("p")
    if not isinstance(v, str):
        raise _DxAbort
    return v


def _env_norm(p):
    """A probe path as the kernel resolves it, casefolded for lookup: // collapsed, trailing / stripped."""
    q = re.sub(r"/{2,}", "/", p.strip())
    return (q.rstrip("/") or q).casefold()


def _env_absent(p):
    """True when a clean retail device has no such file: a root / emulator / hook marker, or an unknown path under
    /system, /sbin, /su, /data/local, /data/adb, /cache (both on the raw and the normalised path)."""
    n = _env_norm(p)
    return bool(_ENV_ABSENT.search(p) or _ENV_ABSENT.search(n)) or n not in _ENV_FILES and bool(_ENV_ROOTTREE.match(n))


def _env_file(p):
    """The clean device's content of a modelled file (exact, then normalised path), else None."""
    v = _ENV_FILES.get(p)
    return v if v is not None else _ENV_FILES.get(_env_norm(p))


# anti-tamper / repackaging probes (coverage atlas rows 49, 50): the untampered Play install of THIS apk. Installer
# (getInstallerPackageName / InstallSourceInfo installing + initiating) is com.android.vending; getPackageInfo(own pkg,
# GET_SIGNATURES | GET_SIGNING_CERTIFICATES).signatures / signingInfo hold the APK's real signer DER (toByteArray,
# hashCode = Arrays.hashCode, toCharsString); ApplicationInfo.flags carries FLAG_DEBUGGABLE only when the manifest sets
# it; sourceDir / publicSourceDir / getPackageCodePath = /data/app/<pkg>-1/base.apk, and ZipFile / JarFile of that path
# reads the real central directory (getEntry(n).getCrc / getSize / getCompressedSize); MessageDigest / CRC32 / Adler32
# hash the bytes, so a digest-keyed answer comes out of the true values.
_ENV_TAMPER_NEW = frozenset(("Ljava/util/zip/ZipFile;", "Ljava/util/jar/JarFile;", "Ljava/util/zip/CRC32;",
                             "Ljava/util/zip/Adler32;"))
_ENV_SIG = "Landroid/content/pm/Signature;"
_ENV_MD = {"md5": "md5", "sha1": "sha1", "sha-1": "sha1", "sha": "sha1", "sha-256": "sha256", "sha256": "sha256",
           "sha-512": "sha512", "sha512": "sha512", "sha-384": "sha384", "sha384": "sha384", "sha-224": "sha224"}


def _env_apk_facts(apk):
    """{"pkg", "dbg" (manifest android:debuggable), "certs" (signer DERs), "ent" ({name: (crc, size, csize)}), "path"}
    of the APK for the clean-device tamper probes; None when it is not a readable zip."""
    try:
        with zipfile.ZipFile(apk) as z:
            ent = {i.filename: (i.CRC, i.file_size, i.compress_size) for i in z.infolist()[:4096]}
            pkg, dbg = None, False
            try:
                b = z.read("AndroidManifest.xml") if z.getinfo("AndroidManifest.xml").file_size < 1 << 22 else b""
                for kind, tag, attrs, _ in (_axml_events(b) if b[:2] == b"\x03\x00" else ()):
                    if kind == "start" and attrs and tag in ("manifest", "application"):
                        at = {k.split(":")[-1]: v for k, v in attrs.items()}
                        if tag == "manifest":
                            pkg = at.get("package") if isinstance(at.get("package"), str) else pkg
                        else:
                            dbg = str(at.get("debuggable")).lower() in ("true", "-1", "1")
                            break
            except Exception:  # noqa: BLE001 - unreadable manifest: package unknown, not debuggable
                pass
    except Exception:  # noqa: BLE001 - not a zip
        return None
    certs = [c["der"] for c in signing_certs(apk)]
    return {"pkg": pkg, "dbg": dbg, "certs": certs, "ent": ent,
            "path": f"/data/app/{pkg or 'app'}-1/base.apk"}


# (probe, resolved argument, stub answer) of the last clean_device_scan() call, for the worker to audit
CLEAN_DEVICE_PROBES = []


class _EnvVM(_DxVM):
    """_DxVM on a clean physical Pixel: framework probes used by root / emulator / debugger / Frida checks answer the
    way an unrooted, untraced retail device would; any other unknown call still aborts."""
    max_steps = _ENV_STEPS
    apk = None  # _env_apk_facts() of the scanned APK (tamper probes); None = not modelled

    def __init__(self, dx, deadline, release=False):
        super().__init__(dx, deadline)
        self.statics.update(_ENV_STATICS)
        self.ns, self.release, self.stack = 1_700_000_000_000_000_000, release, []
        self.probe_log = []

    def log_probe(self, kind, arg, answer):
        if len(self.probe_log) < 256:
            self.probe_log.append((kind, arg, answer))
        return answer

    def run(self, ref, raw_args, depth=0):
        self.stack.append(ref)
        try:
            return super().run(ref, raw_args, depth)
        finally:
            self.stack.pop()

    def init_class(self, ct):
        super().init_class(ct)
        if self.release and ct.endswith("/BuildConfig;") and f"{ct}->DEBUG" in self.statics:
            self.statics[f"{ct}->DEBUG"] = 0

    def process(self, kind, argv):
        """A java.lang.Process running argv on the clean Pixel (_env_shell); IOException when the program is absent."""
        try:
            out, rc = _env_shell(argv)
        except _DxThrow:
            self.log_probe(kind, " ".join(argv), "IOException")
            raise
        p = _DxObj("Ljava/lang/Process;")
        p.f.update(out=self.log_probe(kind, " ".join(argv), out), rc=rc)
        return p

    @staticmethod
    def read1(lines):
        """Reader.read() / InputStream.read() over a line-split stream: one char code, -1 at the end."""
        if not lines:
            return -1
        if not lines[0]:
            lines.pop(0)
            return 10
        c, lines[0] = lines[0][0], lines[0][1:]
        return ord(c)

    def prop(self, name, a):
        k = a[0] if a and isinstance(a[0], str) else None
        if k is None or k not in _ENV_PROPS and not _ENV_ABSENT.search(k):
            raise _DxAbort
        v = _ENV_PROPS.get(k, "")
        d = a[1] if len(a) > 1 else None
        if name == "get":
            return v if v or d is None else d
        if name in ("getInt", "getLong"):
            return int(v) if re.fullmatch(r"-?\d{1,18}", v) else d if isinstance(d, int) else _ENV_UNSET
        if name == "getBoolean":
            return int(v in ("1", "y", "yes", "on", "true")) if v else d if isinstance(d, int) else _ENV_UNSET
        raise _DxAbort

    def const_class(self, t):
        return self.klass(t) if t in self.dx.sfields else super().const_class(t)

    def new_instance(self, t):
        if t in _ENV_NEW or t in _HK_NEW or t in ("Landroid/content/IntentFilter;", "Ljava/util/ArrayList;") or (
                self.apk is not None and t in _ENV_TAMPER_NEW):
            return _DxObj(t)
        return super().new_instance(t)

    def invoke(self, ref, raw, depth):
        ref = _env_resolve(self.dx, ref)
        if ref not in self.dx.code:
            v = self.env(ref, raw)
            if v is not _ENV_UNSET:
                return self.note(v)
        return super().invoke(ref, raw, depth)

    def env(self, ref, raw):  # noqa: C901 - one table of framework models
        cls, rest = ref.split("->", 1)
        name, sig = rest.split("(", 1)
        a = raw[1:] if raw and isinstance(raw[0], _DxObj) and name != "<init>" else raw
        o = raw[0] if raw and isinstance(raw[0], _DxObj) else None
        v = self.tamper(cls, name, sig, a, o) if self.apk is not None else _ENV_UNSET
        if v is _ENV_UNSET:
            v = self.hook(cls, name, sig, raw, a, o)
        if v is _ENV_UNSET:
            v = self.emu(cls, name, sig, a, o)
        if v is not _ENV_UNSET:
            return v
        if cls == "Ljava/lang/String;" and name in ("contains", "startsWith", "endsWith", "equalsIgnoreCase") and raw:
            x, y = _dxe_str(raw[0]), _dxe_str(raw[1])
            if name == "startsWith" and len(raw) > 2:
                return int(isinstance(raw[2], int) and x.startswith(y, raw[2]))
            return int({"contains": y in x, "startsWith": x.startswith(y), "endsWith": x.endswith(y),
                        "equalsIgnoreCase": x.lower() == y.lower()}[name])
        if cls in ("Landroid/os/Debug;", "Ldalvik/system/VMDebug;") and name in (
                "isDebuggerConnected", "waitingForDebugger", "isDebuggingEnabled"):
            return self.log_probe(name, "", 0)
        if _ENV_CLOCK.match(ref):
            self.ns += 1_000_000
            return self.ns if "Nanos" in ref or "nanoTime" in ref else self.ns // 1_000_000
        if name == "sleep" and cls in ("Ljava/lang/Thread;", "Landroid/os/SystemClock;"):
            return None
        if cls == "Landroid/os/SystemProperties;":
            v = self.prop(name, raw)
            if v is _ENV_UNSET:
                raise _DxAbort
            return v
        if cls == "Ljava/lang/Boolean;" and name == "parseBoolean" and raw and isinstance(raw[0], str):
            return int(raw[0].lower() == "true")
        if cls == "Ljava/lang/System;" and name in ("getProperty", "getenv"):
            return raw[1] if len(raw) > 1 else None
        if cls == "Ljava/lang/Class;" and name == "forName" and raw and raw[0] == "android.os.SystemProperties":
            c = _DxObj(cls)
            c.f["n"] = raw[0]
            return c
        if o is not None and o.t == "Ljava/lang/Class;" and o.f.get("n") == "android.os.SystemProperties":
            if name in ("getMethod", "getDeclaredMethod") and a and isinstance(a[0], str):
                m = _DxObj("Ljava/lang/reflect/Method;")
                m.f["n"] = a[0]
                return m
            raise _DxAbort
        if o is not None and o.t == "Ljava/lang/reflect/Method;" and "n" in o.f:
            if name == "setAccessible":
                return None
            if name == "invoke" and len(a) > 1 and isinstance(a[1], list) and o.f["n"] == "get":
                v = self.prop("get", list(a[1]))
                if v is not _ENV_UNSET:
                    return v
            raise _DxAbort
        if cls == "Ljava/lang/Class;" and name == "forName" and raw and isinstance(raw[0], str):
            if _ENV_PKG.search(raw[0]):
                self.log_probe("Class.forName", raw[0], "ClassNotFoundException")
                raise _DxThrow("Ljava/lang/ClassNotFoundException;", "Ljava/lang/ReflectiveOperationException;")
            raise _DxAbort
        if cls == "Ljava/lang/Runtime;":
            if name == "getRuntime":
                return _DxObj(cls)
            if name == "exec" and a:
                try:
                    return self.process("Runtime.exec", _env_argv(a[0]))
                except _DxThrow:
                    raise
                except _DxAbort:  # an unmodelled command naming su / which / magisk / busybox: not on this device
                    if not re.search(r"(?:^|/|\b)su\b|which|magisk|busybox", " ".join(
                            x for x in (a[0] if isinstance(a[0], list) else [a[0]]) if isinstance(x, str))):
                        raise
                self.log_probe("Runtime.exec", a[0], "IOException")
                raise _DxThrow(*_ENV_IOE)
            raise _DxAbort
        if cls == "Ljava/lang/ProcessBuilder;" and o is not None:
            if name in ("<init>", "command") and len(raw) > 1:
                o.f["argv"] = _env_argv(raw[1])
                return None if name == "<init>" else o
            if name in ("redirectErrorStream", "directory") and len(raw) > 1:
                return o
            if name == "start" and "argv" in o.f:
                return self.process("ProcessBuilder.start", o.f["argv"])
            raise _DxAbort
        if o is not None and o.t == "Ljava/lang/Process;":
            if name in ("waitFor", "exitValue"):
                return 1 if sig.startswith("JLjava/util/concurrent/TimeUnit;") else o.f["rc"]
            if name in ("getInputStream", "getErrorStream"):
                k = "so" if name == "getInputStream" else "se"
                if k not in o.f:
                    o.f[k] = _DxObj("Ljava/io/InputStream;")
                    o.f[k].f["L"] = o.f["out"].splitlines() if k == "so" else []
                return o.f[k]
            if name in ("destroy", "destroyForcibly", "isAlive"):
                return 0 if name == "isAlive" else None if name == "destroy" else o
            raise _DxAbort
        if cls in ("Lkotlin/io/TextStreamsKt;", "Lkotlin/io/ByteStreamsKt;") and name in ("readText", "readBytes") \
                and a and isinstance(a[0], _DxObj) and "L" in a[0].f:
            txt = "".join(x + "\n" for x in a[0].f["L"])
            del a[0].f["L"][:]
            return txt if name == "readText" else _DxArr((b ^ 0x80) - 0x80 for b in txt.encode())
        if o is not None and o.t == "Ljava/io/File;" or cls == "Ljava/io/File;":
            if name == "<init>" and o is not None:
                parts = [_env_path(x) for x in raw[1:3]]
                o.f["p"] = "/".join(p.rstrip("/") for p in parts[:-1]) + ("/" if len(parts) > 1 else "") + parts[-1]
                return None
            if o is not None and name in ("exists", "canRead", "canExecute", "canWrite", "isFile", "isDirectory", "length"):
                p = _env_path(o)
                if _env_absent(p):
                    return self.log_probe("File." + name, p, 0)
                f = _env_file(p)
                if f is not None:
                    return self.log_probe("File." + name, p, len(f) if name == "length" else int(name in (
                        "exists", "canRead", "isFile")))
            if o is not None and name in ("getPath", "getAbsolutePath", "toString"):
                return _env_path(o)
            raise _DxAbort
        if cls in ("Ljava/io/FileReader;", "Ljava/io/FileInputStream;") and name == "<init>" and o is not None:
            p = _env_path(raw[1] if len(raw) > 1 else None)
            if _env_absent(p):
                self.log_probe(cls[1:-1].rsplit("/", 1)[-1], p, "FileNotFoundException")
                raise _DxThrow("Ljava/io/FileNotFoundException;", *_ENV_IOE)
            f = _env_file(p)
            if f is None:
                raise _DxAbort
            o.f["L"] = self.log_probe(cls[1:-1].rsplit("/", 1)[-1], p, f).splitlines()
            return None
        if cls in ("Ljava/io/InputStreamReader;", "Ljava/io/BufferedReader;", "Ljava/util/Scanner;") and o is not None:
            if name == "<init>":
                src = raw[1] if len(raw) > 1 else None
                if not isinstance(src, _DxObj) or "L" not in src.f:
                    raise _DxAbort
                o.f["L"] = src.f["L"]
                return None
            lines = o.f.get("L")
            if lines is None:
                raise _DxAbort
            if name in ("readLine", "nextLine"):
                if name == "nextLine" and not lines:
                    raise _DxThrow("Ljava/util/NoSuchElementException;", "Ljava/lang/RuntimeException;")
                return lines.pop(0) if lines else None
            if name == "useDelimiter" and len(raw) > 1 and raw[1] in ("\\A", "\\Z"):
                o.f["all"] = 1
                return o
            if name == "next" and o.f.get("all"):
                if not lines:
                    raise _DxThrow("Ljava/util/NoSuchElementException;", "Ljava/lang/RuntimeException;")
                txt = "".join(x + "\n" for x in lines)
                del lines[:]
                return txt
            if name in ("ready", "hasNext"):
                return int(bool(lines))
            if name == "read" and sig.startswith(")"):
                return self.read1(lines)
            if name == "hasNextLine":
                return int(bool(lines))
            if name == "close":
                return None
            raise _DxAbort
        if cls in ("Ljava/io/FileReader;", "Ljava/io/FileInputStream;") and name == "close":
            return None
        if cls == "Ljava/io/InputStream;" and o is not None and "L" in o.f:
            if name == "close":
                return None
            if name == "read" and sig.startswith(")"):
                return self.read1(o.f["L"])
            if name == "available":
                return len("".join(x + "\n" for x in o.f["L"]).encode())
            raise _DxAbort
        if cls in ("Ljava/net/Socket;", "Ljava/net/InetSocketAddress;"):
            if name == "<init>" and o is not None:
                port = next((x for x in raw[2:] if isinstance(x, int)), None)
                if cls == "Ljava/net/InetSocketAddress;":
                    o.f["port"] = port
                elif port is not None:
                    if port in _ENV_PORTS:
                        raise _DxThrow("Ljava/net/ConnectException;", "Ljava/net/SocketException;", *_ENV_IOE)
                    raise _DxAbort
                return None
            if name == "connect" and len(raw) > 1 and isinstance(raw[1], _DxObj):
                if raw[1].f.get("port") in _ENV_PORTS:
                    raise _DxThrow("Ljava/net/ConnectException;", "Ljava/net/SocketException;", *_ENV_IOE)
                raise _DxAbort
            if name in ("close", "setSoTimeout"):
                return None
            raise _DxAbort
        if name == "getPackageManager" and sig.endswith(")Landroid/content/pm/PackageManager;"):
            return _DxObj("Landroid/content/pm/PackageManager;")
        if name == "getContentResolver" and sig.endswith(")Landroid/content/ContentResolver;"):
            return _DxObj("Landroid/content/ContentResolver;")
        if name == "getApplicationInfo" and sig.endswith(")Landroid/content/pm/ApplicationInfo;"):
            if a and isinstance(a[0], str) and _ENV_PKG.search(a[0].strip()):
                self.log_probe(name, a[0], "NameNotFoundException")
                raise _DxThrow(*_ENV_NNF)
            if a:
                raise _DxAbort
            return self.app_info()
        if name == "getPackageInfo" and cls.startswith("Landroid/content/pm/") or name == "getLaunchIntentForPackage":
            if a and isinstance(a[0], str) and _ENV_PKG.search(a[0].strip()):
                if name == "getLaunchIntentForPackage":
                    return self.log_probe(name, a[0], None)
                self.log_probe(name, a[0], "NameNotFoundException")
                raise _DxThrow(*_ENV_NNF)
            raise _DxAbort
        if name in ("getInstallerPackageName",) and cls.startswith("Landroid/content/pm/"):
            return "com.android.vending"
        if cls in ("Landroid/provider/Settings$Secure;", "Landroid/provider/Settings$Global;") and len(raw) > 1:
            if isinstance(raw[1], str) and re.search(r"adb|development_settings|mock_location|debug_app|wait_for_debugger",
                                                     raw[1]):
                return 0 if name in ("getInt", "getLong") else None  # adb / developer options off
            raise _DxAbort
        return _ENV_UNSET

    def app_info(self):
        ai = _DxObj("Landroid/content/pm/ApplicationInfo;")
        ai.f["Landroid/content/pm/ApplicationInfo;->flags"] = 0x38C8BE44  # FLAG_DEBUGGABLE (0x2) clear
        if self.apk is not None:
            A = "Landroid/content/pm/ApplicationInfo;->"
            ai.f[A + "flags"] |= 2 if self.apk["dbg"] else 0
            ai.f[A + "sourceDir"] = ai.f[A + "publicSourceDir"] = self.apk["path"]
            if self.apk["pkg"]:
                ai.f[A + "packageName"] = ai.f[A + "processName"] = self.apk["pkg"]
                ai.f[A + "dataDir"] = f"/data/user/0/{self.apk['pkg']}"
        return ai

    def sigs(self):
        out = _DxArr()
        out.t = _ENV_SIG
        for der in self.apk["certs"]:
            x = _DxObj(_ENV_SIG)
            x.f["der"] = der
            out.append(x)
        return out

    def tamper(self, cls, name, sig, a, o):  # noqa: C901 - one table of anti-tamper probe models
        """Installer / signature / debuggable / APK-path / dex-CRC probes of the untampered install (rows 49, 50);
        _ENV_UNSET otherwise."""
        import hashlib
        import zlib
        t = o.t if o is not None else None
        ap, pkg = self.apk, self.apk["pkg"]
        own = bool(a) and isinstance(a[0], str) and pkg is not None and a[0].strip() == pkg
        if name == "getPackageName" and sig == ")Ljava/lang/String;" and pkg and (cls in self.dx.sfields or cls in (
                "Landroid/content/Context;", "Landroid/content/ContextWrapper;", "Landroid/app/Activity;",
                "Landroid/app/Application;", "Landroid/app/Service;")):
            return pkg
        if name in ("getPackageCodePath", "getPackageResourcePath") and sig == ")Ljava/lang/String;":
            return self.log_probe(name, "", ap["path"])
        if cls.startswith("Landroid/content/pm/") and t != _ENV_SIG:
            if name == "getInstallerPackageName" and own:
                return self.log_probe(name, a[0], "com.android.vending")
            if name == "getInstallSourceInfo" and own:
                return _DxObj("Landroid/content/pm/InstallSourceInfo;")
            if t == "Landroid/content/pm/InstallSourceInfo;":
                if name in ("getInstallingPackageName", "getInitiatingPackageName", "getUpdateOwnerPackageName"):
                    return self.log_probe(name, "", "com.android.vending")
                if name in ("getOriginatingPackageName", "getInstallingPackageSigningInfo"):
                    return None
                if name == "getPackageSource":
                    return 2  # PACKAGE_SOURCE_STORE
                raise _DxAbort
            if name == "getPackageInfo" and own:
                pi = _DxObj("Landroid/content/pm/PackageInfo;")
                P = "Landroid/content/pm/PackageInfo;->"
                flags = a[1] if len(a) > 1 and isinstance(a[1], int) else 0
                pi.f[P + "packageName"], pi.f[P + "applicationInfo"] = pkg, self.app_info()
                if flags & 0x40:  # GET_SIGNATURES
                    pi.f[P + "signatures"] = self.sigs()
                if flags & 0x8000000:  # GET_SIGNING_CERTIFICATES
                    pi.f[P + "signingInfo"] = _DxObj("Landroid/content/pm/SigningInfo;")
                self.log_probe(name, a[0], f"PackageInfo(flags={flags:#x})")
                return pi
            if name == "getApplicationInfo" and own:
                return self.app_info()
            if t == "Landroid/content/pm/SigningInfo;":
                if name in ("getApkContentsSigners", "getSigningCertificateHistory"):
                    return self.sigs()
                if name in ("hasMultipleSigners", "hasPastSigningCertificates"):
                    return int(name == "hasMultipleSigners" and len(ap["certs"]) > 1)
                raise _DxAbort
        if t == _ENV_SIG and "der" in o.f:
            der = o.f["der"]
            if name == "toByteArray":
                return _dxe_barr(der)
            if name == "hashCode":
                h = 1
                for x in der:
                    h = (31 * h + ((x ^ 0x80) - 0x80)) & 0xFFFFFFFF
                return _dxe_w32(h)
            if name in ("toCharsString", "toString"):
                return der.hex() if name == "toCharsString" else f"android.content.pm.Signature@{id(o) & 0xFFFFFFF:x}"
            if name == "equals":
                return int(isinstance(a[0], _DxObj) and a[0].f.get("der") == der) if a else 0
            raise _DxAbort
        if t in ("Ljava/util/zip/ZipFile;", "Ljava/util/jar/JarFile;"):
            if name == "<init>":
                p = a[1] if len(a) > 1 else None
                p = p.f.get("p") if isinstance(p, _DxObj) else p
                if p != ap["path"]:
                    raise _DxAbort
                o.f["zip"] = True
                return self.log_probe("ZipFile", p, "base.apk")
            if not o.f.get("zip"):
                raise _DxAbort
            if name in ("getEntry", "getJarEntry") and a and isinstance(a[0], str):
                e = ap["ent"].get(a[0])
                if e is None:
                    return None
                z = _DxObj("Ljava/util/zip/ZipEntry;")
                z.f.update(zn=a[0], ze=e)
                return z
            if name == "close":
                return None
            if name == "size":
                return len(ap["ent"])
            raise _DxAbort
        if t in ("Ljava/util/zip/ZipEntry;", "Ljava/util/jar/JarEntry;") and "ze" in o.f:
            v = {"getCrc": o.f["ze"][0], "getSize": o.f["ze"][1], "getCompressedSize": o.f["ze"][2],
                 "getName": o.f["zn"], "toString": o.f["zn"], "isDirectory": int(o.f["zn"].endswith("/"))}
            if name not in v:
                raise _DxAbort
            return self.log_probe(f"ZipEntry.{name}", o.f["zn"], v[name])
        if t in ("Ljava/util/zip/CRC32;", "Ljava/util/zip/Adler32;"):
            fn, v = (zlib.crc32, o.f.get("v", 0)) if t.endswith("CRC32;") else (zlib.adler32, o.f.get("v", 1))
            if name in ("<init>", "reset"):
                o.f["v"] = 0 if fn is zlib.crc32 else 1
                return None
            if name == "update" and a:
                b = bytes([a[0] & 0xFF]) if isinstance(a[0], int) else _dxe_bytes(a[0])
                if len(a) == 3 and isinstance(a[1], int) and isinstance(a[2], int):
                    b = b[a[1]:a[1] + a[2]]
                o.f["v"] = fn(b, v)
                return None
            if name == "getValue":
                return v
            raise _DxAbort
        if cls == "Ljava/security/MessageDigest;" and name == "getInstance" and a and isinstance(a[0], str):
            alg = _ENV_MD.get(a[0].lower())
            if alg is None:
                raise _DxAbort
            m = _DxObj(cls)
            m.f["md"] = hashlib.new(alg)
            return m
        if t == "Ljava/security/MessageDigest;" and "md" in o.f:
            md = o.f["md"]
            if name == "update" and a:
                b = bytes([a[0] & 0xFF]) if isinstance(a[0], int) else _dxe_bytes(a[0])
                if len(a) == 3 and isinstance(a[1], int) and isinstance(a[2], int):
                    b = b[a[1]:a[1] + a[2]]
                md.update(b)
                return None
            if name == "digest":
                if a:
                    md.update(_dxe_bytes(a[0]))
                o.f["md"] = hashlib.new(md.name)  # digest() resets the engine
                return _dxe_barr(md.digest())
            if name == "reset":
                o.f["md"] = hashlib.new(md.name)
                return None
            raise _DxAbort
        if cls == "Ljava/security/MessageDigest;" and name == "isEqual" and len(a) == 2:
            return int(_dxe_bytes(a[0]) == _dxe_bytes(a[1]))
        return _ENV_UNSET

    def emu(self, cls, name, sig, a, o):  # noqa: C901 - one table of retail-phone models
        """Telephony / sensor / battery / network-interface probes on a retail phone (row 48); _ENV_UNSET otherwise."""
        t = o.t if o is not None else None
        if name == "getSystemService" and a and isinstance(a[0], str) and sig.startswith("Ljava/lang/String;)"):
            if a[0] not in _EMU_SVC:
                raise _DxAbort
            return _DxObj(_EMU_SVC[a[0]])
        if t == "Landroid/telephony/TelephonyManager;" or cls == "Landroid/telephony/TelephonyManager;" and o:
            if name not in _EMU_TEL:
                raise _DxAbort
            return _EMU_TEL[name]
        if t == "Landroid/hardware/SensorManager;":
            if name in ("getSensorList", "getDefaultSensor", "getDynamicSensorList") and a and isinstance(a[0], int):
                ss = [] if name == "getDynamicSensorList" else [s for s in _EMU_SENSORS if a[0] == -1 or s[0] == a[0]]
                objs = []
                for st, sn, sv in ss:
                    x = _DxObj("Landroid/hardware/Sensor;")
                    x.f.update(st=st, sn=sn, sv=sv)
                    objs.append(x)
                if name == "getDefaultSensor":
                    return objs[0] if objs else None
                lst = _DxObj("Ljava/util/List;")
                lst.f["sl"] = objs
                return lst
            raise _DxAbort
        if t == "Landroid/hardware/Sensor;" and "st" in o.f:
            v = {"getName": o.f["sn"], "getVendor": o.f["sv"], "getType": o.f["st"], "getVersion": 1, "getPower": 0.0,
                 "getMaximumRange": 100.0, "getResolution": 0.01, "getMinDelay": 5000, "isWakeUpSensor": 0,
                 "toString": f'{{Sensor name="{o.f["sn"]}", vendor="{o.f["sv"]}", version=1, type={o.f["st"]}}}'}
            if name not in v:
                raise _DxAbort
            return v[name]
        if t in _EMU_LIST and o is not None and "sl" in o.f:
            sl = o.f["sl"]
            if name in ("size", "isEmpty"):
                return len(sl) if name == "size" else int(not sl)
            if name == "get" and a and isinstance(a[0], int):
                if not 0 <= a[0] < len(sl):
                    raise _DxThrow("Ljava/lang/IndexOutOfBoundsException;", "Ljava/lang/RuntimeException;")
                return sl[a[0]]
            if name == "iterator":
                it = _DxObj("Ljava/util/Iterator;")
                it.f["sl"] = list(sl)
                return it
            if name in ("hasNext", "hasMoreElements"):
                return int(bool(sl))
            if name in ("next", "nextElement"):
                if not sl:
                    raise _DxThrow("Ljava/util/NoSuchElementException;", "Ljava/lang/RuntimeException;")
                return sl.pop(0)
            raise _DxAbort
        if cls == "Ljava/util/Collections;" and name == "list" and a and isinstance(a[0], _DxObj) and "sl" in a[0].f:
            lst = _DxObj("Ljava/util/ArrayList;")
            lst.f["sl"] = list(a[0].f["sl"])
            return lst
        if t == "Landroid/content/IntentFilter;" and name in ("<init>", "addAction"):
            act = a[1] if name == "<init>" and len(a) > 1 else a[0] if name == "addAction" and a else None
            if isinstance(act, str):
                o.f["act"] = act
            return None
        if name == "registerReceiver" and len(a) > 1 and isinstance(a[1], _DxObj) and a[1].t == "Landroid/content/IntentFilter;":
            if a[1].f.get("act") != "android.intent.action.BATTERY_CHANGED" or a[0] not in (None, 0):
                raise _DxAbort  # a live receiver / other broadcast: nothing sticky to hand back
            it = _DxObj("Landroid/content/Intent;")
            it.f["bat"] = True
            return it
        if t == "Landroid/content/Intent;" and o.f.get("bat"):
            k = a[0] if a and isinstance(a[0], str) else None
            if name == "getAction":
                return "android.intent.action.BATTERY_CHANGED"
            if name in ("getIntExtra", "getBooleanExtra", "getStringExtra") and k is not None:
                v = _EMU_BATTERY.get(k)
                if v is None or isinstance(v, str) != (name == "getStringExtra"):
                    return a[1] if len(a) > 1 else None
                return v
            raise _DxAbort
        if t == "Landroid/os/BatteryManager;":
            if name in ("getIntProperty", "getLongProperty") and a and isinstance(a[0], int):
                return _EMU_BATPROP.get(a[0], -2 ** 31 if name == "getIntProperty" else -2 ** 63)
            if name == "isCharging":
                return 0
            raise _DxAbort
        if cls == "Ljava/net/NetworkInterface;" and name in ("getNetworkInterfaces", "getByName"):
            nis = []
            for n, addrs in _EMU_IFACES:
                ni = _DxObj(cls)
                ni.f.update(nn=n, na=addrs)
                nis.append(ni)
            if name == "getByName":
                return next((x for x in nis if a and x.f["nn"] == a[0]), None)
            e = _DxObj("Ljava/util/Enumeration;")
            e.f["sl"] = nis
            return e
        if t == "Ljava/net/NetworkInterface;" and "nn" in o.f:
            n = o.f["nn"]
            if name in ("getName", "getDisplayName", "toString"):
                return n if name != "toString" else f"name:{n} ({n})"
            if name in ("isUp", "isLoopback", "isVirtual", "isPointToPoint"):
                return int({"isUp": n != "dummy0", "isLoopback": n == "lo"}.get(name, False))
            if name in ("getInetAddresses", "getInterfaceAddresses"):
                e = _DxObj("Ljava/util/Enumeration;" if name == "getInetAddresses" else "Ljava/util/List;")
                e.f["sl"] = []
                for ad in o.f["na"]:
                    x = _DxObj("Ljava/net/InetAddress;")
                    x.f["ha"] = ad
                    e.f["sl"].append(x)
                return e
            raise _DxAbort
        if t in ("Ljava/net/InetAddress;", "Ljava/net/Inet4Address;", "Ljava/net/Inet6Address;") and "ha" in o.f:
            h = o.f["ha"]
            if name in ("getHostAddress", "toString"):
                return h if name == "getHostAddress" else "/" + h
            if name in ("isLoopbackAddress", "isSiteLocalAddress", "isLinkLocalAddress"):
                return int({"isLoopbackAddress": h in ("127.0.0.1", "::1%1"), "isLinkLocalAddress": h.startswith("fe80"),
                            "isSiteLocalAddress": h.startswith(("192.168.", "10."))}[name])
            raise _DxAbort
        return _ENV_UNSET

    def frames(self, top=()):
        """StackTraceElement[] of the current call chain as stock ART reports it (innermost first); a daemon thread's
        (top None) is just its run loop."""
        names = ["java.lang.Object.wait", "java.lang.Thread.run"] if top is None else list(top) + [
            r.split("(", 1)[0].replace("->", ".")[1:].replace("/", ".").replace(";.", ".")
            for r in reversed(self.stack)] + list(_HK_TAIL)
        out = _DxArr()
        out.t = "Ljava/lang/StackTraceElement;"
        for n in names:
            e = _DxObj("Ljava/lang/StackTraceElement;")
            e.f["c"], e.f["m"] = n.rsplit(".", 1)
            e.f["nat"] = n in ("java.lang.reflect.Method.invoke", "dalvik.system.VMStack.getThreadStackTrace")
            out.append(e)
        return out

    def klass(self, desc):
        c = _DxObj("Ljava/lang/Class;")
        c.f["d"] = desc
        return c

    def hook(self, cls, name, sig, raw, a, o):  # noqa: C901 - one table of introspection models
        """Hook-framework introspection probes on a stock device (row 91); _ENV_UNSET when not one of them."""
        t = o.t if o is not None else None
        if cls == "Ljava/lang/Thread;" and name == "currentThread":
            th = _DxObj(cls)
            th.f["n"] = "main"
            return th
        if t == "Ljava/lang/Thread;" and "n" in o.f:
            if name == "getName":
                return o.f["n"]
            if name == "getStackTrace":
                if o.f["n"] == "main":
                    return self.frames(("dalvik.system.VMStack.getThreadStackTrace", "java.lang.Thread.getStackTrace"))
                return self.frames(None)
            raise _DxAbort
        if name in ("getInstalledPackages", "getInstalledApplications") and cls.startswith("Landroid/content/pm/"):
            own = (self.apk or {}).get("pkg")
            objs = []
            for pk in _ENV_INSTALLED + ((own,) if own and own not in _ENV_INSTALLED else ()):
                ai = _DxObj("Landroid/content/pm/ApplicationInfo;")
                ai.f.update({"Landroid/content/pm/ApplicationInfo;->packageName": pk,
                             "Landroid/content/pm/ApplicationInfo;->processName": pk,
                             "Landroid/content/pm/ApplicationInfo;->flags": 0x38C8BE44 if pk == own else 0x30C8BE45})
                if name == "getInstalledPackages":
                    pi = _DxObj("Landroid/content/pm/PackageInfo;")
                    pi.f.update({"Landroid/content/pm/PackageInfo;->packageName": pk,
                                 "Landroid/content/pm/PackageInfo;->applicationInfo": ai,
                                 "Landroid/content/pm/PackageInfo;->versionName": "1.0"})
                    ai = pi
                objs.append(ai)
            lst = _DxObj("Ljava/util/List;")
            lst.f["sl"] = objs
            self.log_probe(name, "", f"{len(objs)} packages, no frida / xposed / lsposed / magisk manager")
            return lst
        if cls == "Ljava/lang/Thread;" and name == "getAllStackTraces":
            self.log_probe("Thread.getAllStackTraces", "", f"{len(_HK_THREADS)} ART threads, no gum-js-loop / gmain")
            m = _DxObj("Ljava/util/Map;")
            m.f["hk"] = []
            for n in _HK_THREADS:
                th = _DxObj(cls)
                th.f["n"] = n
                m.f["hk"].append((th, self.frames(("dalvik.system.VMStack.getThreadStackTrace",
                                                    "java.lang.Thread.getStackTrace") if n == "main" else None)))
            return m
        if t in _HK_NEW:
            if name == "<init>":
                o.f["st"] = self.frames(())
                return None
            if name == "getStackTrace" and "st" in o.f:
                return o.f["st"]
            raise _DxAbort
        if o is not None and "hk" in o.f and t in ("Ljava/util/Map;", "Ljava/util/Set;", "Ljava/util/Collection;",
                                                   "Ljava/util/Iterator;", "Ljava/util/Map$Entry;"):
            hk = o.f["hk"]
            if name in ("keySet", "values", "entrySet"):
                c = _DxObj("Ljava/util/Set;")
                if name == "entrySet":
                    c.f["hk"] = []
                    for k, v in hk:
                        e = _DxObj("Ljava/util/Map$Entry;")
                        e.f["hk"] = (k, v)
                        c.f["hk"].append(e)
                else:
                    c.f["hk"] = [kv[name == "values"] for kv in hk]
                return c
            if t == "Ljava/util/Map$Entry;" and name in ("getKey", "getValue"):
                return hk[name == "getValue"]
            if name == "get" and t == "Ljava/util/Map;" and a:
                return next((v for k, v in hk if k is a[0]), None)
            if name == "iterator":
                it = _DxObj("Ljava/util/Iterator;")
                it.f["hk"] = list(hk)
                return it
            if name == "hasNext":
                return int(bool(hk))
            if name == "next":
                if not hk:
                    raise _DxAbort
                return hk.pop(0)
            if name in ("size", "isEmpty"):
                return len(hk) if name == "size" else int(not hk)
            raise _DxAbort
        if t == "Ljava/lang/StackTraceElement;":
            c, m = o.f["c"], o.f["m"]
            if name in ("getClassName", "getMethodName"):
                return c if name == "getClassName" else m
            if name == "isNativeMethod":
                return int(o.f["nat"])
            if name == "toString":
                return f"{c}.{m}({'Native Method' if o.f['nat'] else 'Unknown Source'})"
            raise _DxAbort
        if t == "Ljava/io/File;" or cls == "Ljava/io/File;" and o is not None:
            p = o.f.get("p")
            if isinstance(p, str) and p.rstrip("/") in _HK_DIRS:
                p = p.rstrip("/")
                if name in ("exists", "isDirectory", "canRead"):
                    return 1
                if name == "isFile":
                    return 0
                if name in ("list", "listFiles"):
                    out = _DxArr()
                    for n in _HK_DIRS[p]:
                        if name == "list":
                            out.append(n)
                        else:
                            f = _DxObj("Ljava/io/File;")
                            f.f["p"] = f"{p}/{n}"
                            out.append(f)
                    out.t = "Ljava/lang/String;" if name == "list" else "Ljava/io/File;"
                    return out
            if isinstance(p, str) and name == "getName" and re.match(r"/proc/self/(?:task|fd)/", p):
                return p.rsplit("/", 1)[1]
            if isinstance(p, str) and name in ("getCanonicalPath", "getCanonicalFile") and p.startswith("/proc/self/fd/"):
                tgt = _HK_FDS.get(int(p[14:])) if p[14:].isdigit() else None
                if tgt is None:
                    raise _DxThrow(*_ENV_IOE)
                if name == "getCanonicalPath":
                    return tgt
                f = _DxObj("Ljava/io/File;")
                f.f["p"] = tgt
                return f
            return _ENV_UNSET
        if cls == "Landroid/system/Os;" and name == "readlink" and raw and isinstance(raw[0], str):
            m = re.fullmatch(r"/proc/self/fd/(\d+)", raw[0])
            if not m or int(m.group(1)) not in _HK_FDS:
                raise _DxThrow("Landroid/system/ErrnoException;")
            return self.log_probe("Os.readlink", raw[0], _HK_FDS[int(m.group(1))])
        if cls == "Ljava/lang/System;" and name == "getenv" and raw and isinstance(raw[0], str):
            return None  # LD_PRELOAD / CLASSPATH / ... unset in a zygote-forked app
        if t == "Ljava/lang/Class;" and "d" in o.f:
            d = o.f["d"]
            if name == "getName":
                return d[1:-1].replace("/", ".")
            if name == "getDeclaredMethods":
                out = _DxArr()
                out.t = "Ljava/lang/reflect/Method;"
                for r in self.dx.code:
                    if r.startswith(d + "->") and "-><init>(" not in r and "-><clinit>(" not in r:
                        m = _DxObj("Ljava/lang/reflect/Method;")
                        m.f["m"] = r
                        out.append(m)
                return out
            if name in ("getDeclaredMethod", "getMethod") and a and isinstance(a[0], str):
                r = next((r for r in self.dx.code if r.startswith(f"{d}->{a[0]}(")), None)
                if r is None:
                    raise _DxThrow("Ljava/lang/NoSuchMethodException;", "Ljava/lang/ReflectiveOperationException;")
                m = _DxObj("Ljava/lang/reflect/Method;")
                m.f["m"] = r
                return m
            if name == "getClassLoader":
                return _DxObj("Ljava/lang/ClassLoader;")
            raise _DxAbort
        if t == "Ljava/lang/reflect/Method;" and "m" in o.f:
            if name == "getModifiers":
                return self.dx.code[o.f["m"]][3] & 0x0DFF  # has dex code: never ACC_NATIVE unless hooked
            if name == "getName":
                return o.f["m"].split("->", 1)[1].split("(", 1)[0]
            raise _DxAbort
        if cls == "Ljava/lang/reflect/Modifier;" and name.startswith("is") and raw and isinstance(raw[0], int):
            bit = {"isNative": 0x100, "isStatic": 0x8, "isPublic": 0x1, "isPrivate": 0x2, "isProtected": 0x4,
                   "isFinal": 0x10, "isSynchronized": 0x20, "isAbstract": 0x400}.get(name)
            if bit is None:
                raise _DxAbort
            return int(bool(raw[0] & bit))
        if name == "getClass" and sig == ")Ljava/lang/Class;" and o is not None and o.t in self.dx.sfields:
            return self.klass(o.t)
        if name == "getClassLoader" and sig.endswith(")Ljava/lang/ClassLoader;") or (
                cls == "Ljava/lang/ClassLoader;" and name == "getSystemClassLoader"):
            return _DxObj("Ljava/lang/ClassLoader;")
        if name in ("loadClass", "forName") and (t == "Ljava/lang/ClassLoader;" or cls == "Ljava/lang/Class;") and a \
                and isinstance(a[0], str) and (name == "loadClass" or a[0] != "android.os.SystemProperties"):
            if _ENV_PKG.search(a[0]):
                self.log_probe("ClassLoader." + name, a[0], "ClassNotFoundException")
                raise _DxThrow("Ljava/lang/ClassNotFoundException;", "Ljava/lang/ReflectiveOperationException;")
            d = "L" + a[0].replace(".", "/") + ";"
            if d in self.dx.sfields:
                return self.klass(d)
            raise _DxAbort
        return _ENV_UNSET


def _dxx_supers(dx):
    """{class descriptor: superclass descriptor} of every class_def in the dex (cached on it)."""
    sup = getattr(dx, "supers", None)
    if sup is None:
        u32 = lambda o: struct.unpack_from("<I", dx.d, o)[0]  # noqa: E731
        n_cls, o_cls = u32(0x60), u32(0x64)
        sup = dx.supers = {dx.typ(u32(o_cls + 32 * c)): dx.typ(u32(o_cls + 32 * c + 8)) for c in range(n_cls)}
    return sup


def _env_resolve(dx, ref):
    """An invoke ref re-pointed at the in-dex superclass that defines it (inherited app methods); else unchanged."""
    if ref in dx.code:
        return ref
    sup = _dxx_supers(dx)
    cls, rest = ref.split("->", 1)
    for _ in range(8):
        cls = sup.get(cls)
        if cls is None:
            break
        if f"{cls}->{rest}" in dx.code:
            return f"{cls}->{rest}"
    return ref


def _env_scan_ins(dx, ins):
    """(touches an environment probe, {in-dex callee refs}) of one method's code."""
    marked, calls, pc, n = False, set(), 0, len(ins) // 2
    while pc < n:
        p = 2 * pc
        op = ins[p]
        if op in (0x1A, 0x1B):
            s = dx.s(struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0]) or ""
            marked |= bool(len(s) < 200 and (_ENV_ABSENT.search(s) or s in _ENV_FILES or "TracerPid" in s
                                             or s in ("ro.kernel.qemu", "test-keys", "ro.debuggable", "ro.secure",
                                                      "service.adb.root", "adb_enabled", "development_settings_enabled",
                                                      "/proc/self/task", "/proc/self/fd", "gum-js-loop", "gmain",
                                                      "LD_PRELOAD", "CLASSPATH", "/proc/cpuinfo", "/proc/version",
                                                      "android.intent.action.BATTERY_CHANGED"))
                                             or s[:48].split(" ", 1)[0] in _ENV_SH_PROBES)
        elif 0x60 <= op <= 0x6D:
            f = dx.fref(struct.unpack_from("<H", ins, p + 2)[0])[1]
            marked |= f.startswith("Landroid/os/Build") or bool(_ENV_BCDBG.search(f))
        elif 0x6E <= op <= 0x78 and op != 0x73:
            m = _env_resolve(dx, dx.mref(struct.unpack_from("<H", ins, p + 2)[0]))
            if m in dx.code:
                calls.add(m)
            else:
                marked |= bool(_ENV_MARK.search(m))
        elif op == 0 and ins[p + 1] in (1, 2, 3):
            if ins[p + 1] == 1:
                pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
            elif ins[p + 1] == 2:
                pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
            else:
                w, k = struct.unpack_from("<HI", ins, p + 2)
                pc += 4 + (w * k + 1) // 2
            continue
        pc += _DOP_W[op]
    return marked, calls


def clean_device_scan(apk):
    """ANS tokens a root / emulator / debugger / Frida check lets through on a clean device: every app method whose
    code touches an environment probe (File.exists on su / magisk / busybox / frida paths, Build.TAGS / FINGERPRINT /
    HARDWARE / MODEL / PRODUCT, Debug.isDebuggerConnected, ApplicationInfo.flags, System.getProperty("ro.kernel.qemu"),
    /proc/self/status TracerPid, /proc/self/maps, Socket :27042, PackageManager.getPackageInfo(magisk / xposed),
    Class.forName(XposedBridge), Runtime.exec("su"), timing deltas of SystemClock / nanoTime / currentTimeMillis /
    threadCpuTimeNanos (1 ms per read, Thread.sleep a no-op), Settings adb_enabled / development_settings_enabled,
    SystemProperties ro.debuggable / ro.secure / service.adb.root (direct or reflective), VMDebug.isDebuggingEnabled,
    BuildConfig.DEBUG (encoded value, then re-run as the release build's false)), plus its in-dex callers two levels
    up, is run by the Dalvik
    evaluator with those probes answering as an unrooted retail Pixel (catch handlers taken for NameNotFound /
    ClassNotFound / ConnectException). Only the clean path runs, so a value keyed on the check results (a score folded
    into an xor key) comes out right and a trap behind `if (rooted)` stays unread. [] when absent; never raises; ~0.8 s."""
    hits, facts_apk = [], None
    del CLEAN_DEVICE_PROBES[:]
    deadline = time.time() + _ENV_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline or not _DGB_PRE.search(d) and not re.search(
                    rb"Landroid/os/(?:Build|Debug|SystemClock|SystemProperties);|/proc/self/|Ljava/net/Socket;|VMDebug;"
                    rb"|nanoTime|currentTimeMillis|adb_enabled|development_settings_enabled|BuildConfig;"
                    rb"|getStackTrace|getAllStackTraces|isNative|loadClass|TelephonyManager;|SensorManager;"
                    rb"|BatteryManager;|BATTERY_CHANGED|NetworkInterface;|/proc/cpuinfo|Ljava/lang/(?:Runtime|Process\w*);"
                    rb"|getInstallerPackageName|getInstallSourceInfo|getPackageCodePath|Landroid/content/pm/Signature;", d) and b"\x0egetPackageInfo\0" not in d and not (
                    b"\x0eLjava/io/File;\0" in d and b"\x06exists\0" in d):  # probe args built at runtime
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            facts = {ref: _env_scan_ins(dx, dx.code[ref][2]) for ref in dx.order}
            marked = {r for r, f in facts.items() if f[0]}
            if not marked:
                continue
            if facts_apk is None and re.search(rb"getInstall|getPackageCodePath|getPackageResourcePath|ApplicationInfo;"
                                               rb"|Landroid/content/pm/(?:Signature|SigningInfo);|getPackageInfo", d):
                facts_apk = _env_apk_facts(apk) or {"pkg": None, "dbg": False, "certs": [], "ent": {},
                                                     "path": "/data/app/app-1/base.apk"}
            todo, layer = list(marked), marked
            for _ in range(2):
                layer = {r for r, f in facts.items() if f[1] & layer} - set(todo)
                todo += sorted(layer)
            for ref in todo[:_ENV_MAX_RUNS]:
                if time.time() > deadline:
                    break
                nreg, nin, _, acc = dx.code[ref]
                ps = _dxe_params(ref)
                if len(ps) > 4 or nin > nreg:
                    continue
                for release in (False, True):
                    vm = _EnvVM(dx, deadline, release)
                    vm.apk = facts_apk
                    raw = [] if acc & 0x8 else [_DxObj(ref.split("->")[0])]
                    for p in ps:
                        raw += [_DxObj(p) if p in ("Landroid/content/Context;", "Landroid/app/Activity;",
                                                   "Landroid/app/Application;") else _dxe_default(p)] + (
                            [None] if p in "JD" else [])
                    try:
                        vm.init_class(ref.split("->")[0])
                        vm.note(vm.run(ref, raw))
                    except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError,
                            RecursionError, struct.error):
                        pass
                    for s in vm.seen + [v for v in vm.statics.values() if isinstance(v, str)]:
                        hits += ANS_RE_T.findall(s)
                    CLEAN_DEVICE_PROBES.extend(x for x in vm.probe_log if x not in CLEAN_DEVICE_PROBES)
                    if release or not any(v for k, v in vm.statics.items() if _ENV_BCDBG.search(k)):
                        break  # a DEBUG build's BuildConfig.DEBUG read true: the release (false) path runs too
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- the Context a v2 chain is handed, answering from the APK itself (coverage atlas: analysis-android-api-stubs) -------
# D23 `Release.code(Context)` stores ctx in a static: the next chains read Android state through it. _CtxVM is the deep
# evaluator on the clean retail Pixel (_EnvVM's Build / root / emulator / hook / installer / signature tables) plus a
# Context backed by the APK's own bytes: getAssets().open(name) -> the zip entry (InputStream read / available /
# readAllBytes / readers), org.json JSONObject / JSONArray over those bytes, getResources() / getString(id) /
# getIdentifier via resources.arsc, getPackageName / PackageInfo (signer certs, versionCode / versionName from the
# manifest, fixed install times), getApplicationInfo().flags (manifest debuggable bit), SharedPreferences (unset key ->
# the default; put + apply / commit read back), Settings.Secure ANDROID_ID = a fixed 16-hex id, System.getProperty =
# ART's values. Every stub hit lands in CONTEXT_STUB_HITS (kind, argument, answer) for the worker to audit.
_CTX_TYPES = frozenset(("Landroid/content/Context;", "Landroid/content/ContextWrapper;", "Landroid/app/Activity;",
                        "Landroid/app/Application;", "Landroid/app/Service;", "Landroid/view/ContextThemeWrapper;",
                        "Landroidx/appcompat/app/AppCompatActivity;", "Landroidx/fragment/app/FragmentActivity;",
                        "Landroidx/activity/ComponentActivity;", "Landroidx/core/app/ComponentActivity;"))
_CTX_ANDROID_ID = "3f8a1c5e7b2d9046"
_CTX_INSTALL_MS = 1_707_177_600_000  # firstInstallTime / lastUpdateTime (2024-02-06, the build date of _ENV_FP)
_CTX_SYSPROPS = {"java.vm.name": "Dalvik", "java.vm.version": "2.1.0", "java.vm.vendor": "The Android Project",
                 "java.vendor": "The Android Project", "java.vendor.url": "http://www.android.com/", "java.version": "0",
                 "java.specification.version": "0.9", "java.vm.specification.version": "0.9", "java.home": "/system",
                 "java.class.path": ".", "java.library.path": "/system/lib64:/system_ext/lib64", "os.name": "Linux",
                 "os.arch": "aarch64", "os.version": "5.10.198-android13-4-00050-g12f3388846c3-ab11920634",
                 "file.separator": "/", "path.separator": ":", "line.separator": "\n", "file.encoding": "UTF-8",
                 "user.dir": "/", "user.home": "", "user.name": "", "user.language": "en", "user.region": "US",
                 "http.agent": "Dalvik/2.1.0 (Linux; U; Android 14; Pixel 6 Build/UQ1A.240205.004)",
                 "android.icu.library.version": "72.1", "android.icu.unicode.version": "15.0"}
_CTX_MAX_ASSET, _CTX_BUDGET_S, _CTX_MAX_RUNS = 4 << 20, 1.5, 64
_CTX_JSON = ("Lorg/json/JSONObject;", "Lorg/json/JSONArray;")
_CTX_JEX = ("Lorg/json/JSONException;",)
_CTX_RNF = ("Landroid/content/res/Resources$NotFoundException;", "Ljava/lang/RuntimeException;")
_CTX_PREF = ("Landroid/content/SharedPreferences;", "Landroid/content/SharedPreferences$Editor;")
_CTX_BYTEORDER = {"Ljava/nio/ByteOrder;->LITTLE_ENDIAN": "LITTLE_ENDIAN", "Ljava/nio/ByteOrder;->BIG_ENDIAN": "BIG_ENDIAN"}
# (kind, argument, stub answer) of the last context_chain_scan() call
CONTEXT_STUB_HITS = []


def _ctx_facts(apk):
    """_env_apk_facts plus the manifest versionCode / versionName; None when the APK is not a readable zip."""
    f = _env_apk_facts(apk)
    if f is None:
        return None
    f.update(vc=1, vn=None)
    try:
        with zipfile.ZipFile(apk) as z:
            b = z.read("AndroidManifest.xml") if z.getinfo("AndroidManifest.xml").file_size < 1 << 22 else b""
        for kind, tag, attrs, _ in (_axml_events(b) if b[:2] == b"\x03\x00" else ()):
            if kind == "start" and tag == "manifest" and attrs:
                at = {k.split(":")[-1]: v for k, v in attrs.items()}
                vc = at.get("versionCode")
                f["vc"] = vc if isinstance(vc, int) and not isinstance(vc, bool) else int(vc) if str(vc).isdigit() else 1
                f["vn"] = at.get("versionName") if isinstance(at.get("versionName"), str) else None
                break
    except Exception:  # noqa: BLE001 - unreadable manifest: versionCode 1, no versionName
        pass
    return f


def _ctx_jstr(v):
    """org.json's coercion of a value to String (getString / optString)."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, str)):
        return str(v)
    if isinstance(v, float):
        return repr(v)  # Double.toString: 5.0, 0.25
    raise _DxAbort


def _ctx_jnum(v, w):
    """org.json's coercion to int / long (getInt / getLong): numbers truncate, numeric strings parse; else None."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return w(int(v))
    if isinstance(v, str):
        try:
            return w(int(float(v))) if re.fullmatch(r"\s*-?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?\s*", v) else None
        except (ValueError, OverflowError):
            return None
    return None


# --- X.509 / attestation through CertificateFactory / KeyStore APIs (coverage atlas: analysis-keystore-cert-api-stubs,
# rows 87, 93). A v2 chain reads a SHIPPED cert: getResources().openRawResource(R.raw.x) / getAssets().open("a.der" |
# ".pem") / new ByteArrayInputStream(bytes) -> CertificateFactory.getInstance("X.509").generateCertificate(in) /
# generateCertificates (DER, PEM blocks, concatenated, PKCS#7 .p7b) -> X509Certificate getEncoded / getExtensionValue
# (the OCTET STRING-wrapped extnValue, e.g. 1.3.6.1.4.1.11129.2.1.17 KeyDescription) / getSerialNumber (BigInteger:
# longValue truncates) / getNotBefore|NotAfter().getTime() / getSubject|IssuerX500Principal().getName() (RFC 2253) /
# getPublicKey().getEncoded() (SPKI) / getSignature / getTBSCertificate / getSigAlgName|OID / getVersion /
# getBasicConstraints / getKeyUsage; KeyStore.getInstance("AndroidKeyStore").load(null).getCertificateChain(alias) =
# the certs of the shipped assets|res/raw entry named <alias>.* in order (null when none). Values come from asn1crypto
# over the APK's own bytes; byte[] results are Java signed-byte arrays.
_X5_TYPES = frozenset(("Ljava/security/cert/CertificateFactory;", "Ljava/security/cert/Certificate;",
                       "Ljava/security/cert/X509Certificate;", "Ljava/security/KeyStore;",
                       "Ljavax/security/auth/x500/X500Principal;", "Ljava/security/PublicKey;", "Ljava/security/Key;",
                       "Ljava/util/Date;"))
_X5_CEX = ("Ljava/security/cert/CertificateException;", "Ljava/security/GeneralSecurityException;")
_X5_KEX = ("Ljava/security/KeyStoreException;", "Ljava/security/GeneralSecurityException;")
_X5_PEM = re.compile(rb"-----BEGIN (?:X509 |TRUSTED )?CERTIFICATE-----\s*([A-Za-z0-9+/=\s]+?)-----END[^\n]*\n?")
_X5_PEM7 = re.compile(rb"-----BEGIN PKCS7-----\s*([A-Za-z0-9+/=\s]+?)-----END[^\n]*")
_X5_KW = {"2.5.4.3": "CN", "2.5.4.6": "C", "2.5.4.7": "L", "2.5.4.8": "ST", "2.5.4.10": "O", "2.5.4.11": "OU",
          "2.5.4.9": "STREET", "0.9.2342.19200300.100.1.25": "DC", "0.9.2342.19200300.100.1.1": "UID"}
_X5_SIGKEY = {"rsa": "RSA", "rsassa_pkcs1v15": "RSA", "ecdsa": "ECDSA", "dsa": "DSA", "ed25519": "Ed25519",
              "rsassa_pss": "RSASSA-PSS"}


def _x5_der_len(b, i=0):
    """End offset of the DER SEQUENCE at b[i], or None."""
    t = _ka_tlv(b, i, len(b)) if i < len(b) and b[i] == 0x30 else None
    return t[4] if t else None


def _x5_load(der):
    """asn1crypto Certificate over one DER cert with its fields parsed (raises ValueError on a malformed cert)."""
    from asn1crypto import x509 as _ax
    try:
        c = _ax.Certificate.load(der, strict=True)
        c["tbs_certificate"]["serial_number"].native  # noqa: B018 - force the lazy parse of what the getters read
        c["tbs_certificate"]["subject"].contents  # noqa: B018
        c["tbs_certificate"]["subject_public_key_info"].dump()
        c.not_valid_before  # noqa: B018
    except Exception as e:  # noqa: BLE001 - any asn1crypto parse error = CertificateException
        raise ValueError(e) from None
    return c


def _x5_read(b, pos, many):
    """Java X509Factory over a stream's bytes from pos: [(der, ...)] certs and the new position; ValueError when none.
    One cert for generateCertificate (DER or the next PEM block), every DER / PEM / PKCS#7 cert for generateCertificates."""
    out, i = [], pos
    while i < len(b) and (many or not out):
        while i < len(b) and b[i] in b" \t\r\n":
            i += 1
        if i >= len(b):
            break
        if b[i] == 0x30:
            e = _x5_der_len(b, i)
            if e is None:
                raise ValueError("truncated DER")
            der = bytes(b[i:e])
            if many and not out and e == len(b) and b"\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x07\x02" in der[:24]:
                from asn1crypto import cms as _cms
                try:
                    sd = _cms.ContentInfo.load(der)["content"]
                    return [c.chosen.dump() for c in sd["certificates"]], e
                except Exception as x:  # noqa: BLE001 - not a SignedData
                    raise ValueError(x) from None
            out.append(der)
            i = e
            continue
        m = _X5_PEM.search(b, i)
        m7 = _X5_PEM7.search(b, i) if many and not out else None
        if m7 and (not m or m7.start() < m.start()):
            return _x5_read(base64.b64decode(re.sub(rb"\s", b"", m7.group(1))), 0, True)[0], m7.end()
        if not m or (b[i:m.start()].strip() and not b[i:m.start()].isascii()):
            break
        out.append(base64.b64decode(re.sub(rb"\s", b"", m.group(1))))
        i = m.end()
    if not out:
        raise ValueError("no certificate")
    return out, i


def _x5_rfc2253(name):
    """X500Principal.getName() (RFC 2253): RDNs last-first, keyword=value with ,=+<>#;"\\ escaped, unknown types as
    OID=#hex of the value's DER."""
    rdns = []
    for rdn in reversed(list(name.chosen)):
        avas = []
        for ava in rdn:
            oid = ava["type"].dotted
            kw = _X5_KW.get(oid)
            v = ava["value"]
            if kw is None:
                avas.append(f"{oid}=#{v.dump().hex()}")
                continue
            s = v.native if isinstance(v.native, str) else str(v.native)
            s = "".join("\\" + ch if ch in ',=+<>#;"\\' else ch for ch in s)
            if s.startswith(" "):
                s = "\\" + s
            if s.endswith(" ") and not s.endswith("\\ "):
                s = s[:-1] + "\\ "
            avas.append(f"{kw}={s}")
        rdns.append("+".join(avas))
    return ",".join(rdns)


class _CtxVM(_DxeDeepVM, _EnvVM):
    """_DxeDeepVM on the clean Pixel (_EnvVM) holding a Context whose assets / resources / package facts are the APK's."""

    def __init__(self, dx, deadline, facts, z, prefs):
        _EnvVM.__init__(self, dx, deadline)
        self.apk, self.z, self.prefs, self.tab = facts, z, prefs, None
        self.statics.update(_CTX_BYTEORDER)

    def new_instance(self, t):
        if t in _CTX_JSON or t == "Ljava/io/ByteArrayInputStream;":
            return _DxObj(t)
        return super().new_instance(t)

    def env(self, ref, raw):
        v = self.ctx(ref, raw)
        return super().env(ref, raw) if v is _ENV_UNSET else v

    def res_table(self):
        if self.tab is None:
            try:
                self.tab = resource_table(self.z.read("resources.arsc")) if "resources.arsc" in self.z.NameToInfo \
                    and self.z.getinfo("resources.arsc").file_size <= _RID_MAX_ARSC else {}
            except Exception:  # noqa: BLE001 - unreadable table: no resources
                self.tab = {}
        return self.tab

    def res(self, rid):
        e = self.res_table().get(rid) if isinstance(rid, int) else None
        if not e or not e["values"]:
            self.log_probe("Resources.get", rid, "NotFoundException")
            raise _DxThrow(*_CTX_RNF)
        return _rid_resolve(self.tab, next((x for c, x in e["values"] if not c), e["values"][0][1]))

    def stream(self, kind, arg, data):
        s = _DxObj("Ljava/io/InputStream;")
        s.f.update(B=data, pos=0)
        self.log_probe(kind, arg, f"{len(data)} bytes")
        return s

    def json(self, t, v):
        o = _DxObj(t)
        o.f["J"] = v
        return o

    def bbuf(self, cls, name, sig, o, a):  # noqa: C901 - java.nio.ByteBuffer's heap-buffer accessors
        """ByteBuffer.wrap / allocate over a byte[] (shared, Java's position / limit / order), relative and absolute
        get / put of byte .. long, array / position / remaining / flip / rewind; ByteOrder.nativeOrder (aarch64 LE)."""
        if cls == "Ljava/nio/ByteOrder;" and o is None:
            if name == "nativeOrder":
                return "LITTLE_ENDIAN"
            raise _DxAbort
        if o is None or "bb" not in o.f:
            if name == "wrap" and a and isinstance(a[0], list):
                off, n = (a[1], a[2]) if len(a) >= 3 else (0, len(a[0]))
                if not (isinstance(off, int) and isinstance(n, int) and 0 <= off and 0 <= n and off + n <= len(a[0])):
                    raise _DxAbort
                arr = a[0]
            elif name in ("allocate", "allocateDirect") and a and isinstance(a[0], int) and 0 <= a[0] <= 1 << 20:
                arr, off, n = _dxe_barr(bytes(a[0])), 0, a[0]
            else:
                raise _DxAbort
            bb = _DxObj("Ljava/nio/ByteBuffer;")
            bb.f.update(bb=arr, pos=off, lim=off + n, le=False)
            return bb
        f = o.f
        arr, pos, lim = f["bb"], f["pos"], f["lim"]
        bo = "little" if f["le"] else "big"
        if name == "order":
            if sig.startswith(")"):
                return "LITTLE_ENDIAN" if f["le"] else "BIG_ENDIAN"
            if not a or a[0] not in ("LITTLE_ENDIAN", "BIG_ENDIAN"):
                raise _DxAbort
            f["le"] = a[0] == "LITTLE_ENDIAN"
            return o
        simple = {"array": arr, "position": pos, "limit": lim, "capacity": len(arr), "remaining": lim - pos,
                  "hasRemaining": int(lim > pos), "arrayOffset": 0, "hasArray": 1, "isDirect": 0, "isReadOnly": 0}
        if name in simple and sig.startswith(")"):
            return simple[name]
        if name in ("rewind", "flip", "clear") and sig.startswith(")"):
            f["lim"] = pos if name == "flip" else len(arr) if name == "clear" else lim
            f["pos"] = 0
            return o
        if name in ("position", "limit") and a and isinstance(a[0], int):
            if not 0 <= a[0] <= (lim if name == "position" else len(arr)):
                raise _DxAbort
            f["pos" if name == "position" else "lim"] = a[0]
            f["pos"] = min(f["pos"], f["lim"])
            return o
        width = {"": 1, "Short": 2, "Char": 2, "Int": 4, "Long": 8}
        kind = name[3:] if name[:3] in ("get", "put") else None
        if kind not in width:
            raise _DxAbort
        w, args = width[kind], [x for x in a if x is not None]
        if name == "get" and sig.startswith("[") or sig.startswith("Ljava/nio/"):
            raise _DxAbort
        if name == "put" and sig.startswith("[B"):  # bulk put(byte[] [, off, len])
            src = args[0] if args and isinstance(args[0], list) else None
            if src is None:
                raise _DxAbort
            s0, sn = (args[1], args[2]) if len(args) >= 3 else (0, len(src))
            if not (0 <= s0 and 0 <= sn and s0 + sn <= len(src)) or pos + sn > lim:
                raise _DxAbort
            arr[pos:pos + sn] = [(x & 0xFF ^ 0x80) - 0x80 for x in src[s0:s0 + sn]]
            f["pos"] = pos + sn
            return o
        absolute = sig.startswith("I)") if name.startswith("get") else sig[:2] in ("IB", "IS", "IC", "II", "IJ")
        i = args.pop(0) if absolute else pos
        if not isinstance(i, int) or i < 0 or i + w > lim:
            raise _DxAbort
        if not absolute:
            f["pos"] = pos + w
        if name.startswith("get"):
            return int.from_bytes(bytes(x & 0xFF for x in arr[i:i + w]), bo, signed=kind != "Char")
        if not args or not isinstance(args[0], int):
            raise _DxAbort
        arr[i:i + w] = [(x ^ 0x80) - 0x80 for x in (args[0] & ((1 << 8 * w) - 1)).to_bytes(w, bo)]
        return o

    def cert_obj(self, der):
        try:
            c = _x5_load(der)
        except ValueError:
            raise _DxThrow(*_X5_CEX) from None
        x = _DxObj("Ljava/security/cert/X509Certificate;")
        x.f.update(X=der, c=c)
        return x

    def shipped_chain(self, alias):
        """Certs of the assets / res/raw entry whose file stem is `alias` (AndroidKeyStore's provisioned chain)."""
        for n in sorted(self.z.NameToInfo):
            if n.startswith(("assets/", "res/raw/")) and n.rsplit("/", 1)[-1].split(".", 1)[0] == alias \
                    and self.z.getinfo(n).file_size <= _CTX_MAX_ASSET:
                try:
                    return n, _x5_read(self.z.read(n), 0, True)[0]
                except ValueError:
                    continue
        return None, []

    def x509(self, cls, name, sig, o, a):  # noqa: C901 - CertificateFactory / X509Certificate / KeyStore / Date models
        f = o.f if o is not None else {}
        if cls == "Ljava/security/cert/CertificateFactory;" and name == "getInstance" and o is None:
            if not a or not isinstance(a[0], str) or a[0].upper().replace(".", "") != "X509":
                raise _DxThrow(*_X5_CEX)
            self.log_probe("CertificateFactory.getInstance", a[0], "X.509")
            return _DxObj(cls)
        if o is not None and o.t == "Ljava/security/cert/CertificateFactory;":
            if name not in ("generateCertificate", "generateCertificates") or not a or not isinstance(a[0], _DxObj) \
                    or "B" not in a[0].f:
                raise _DxAbort
            s = a[0]
            try:
                ders, s.f["pos"] = _x5_read(s.f["B"], s.f["pos"], name == "generateCertificates")
            except (ValueError, binascii.Error):
                raise _DxThrow(*_X5_CEX) from None
            certs = [self.cert_obj(d) for d in ders[:64]]
            self.log_probe("CertificateFactory." + name, f"{len(s.f['B'])} bytes", f"{len(certs)} cert(s)")
            if name == "generateCertificate":
                return certs[0]
            lst = _DxObj("Ljava/util/Collection;")
            lst.f["sl"] = certs
            return lst
        if cls == "Ljava/security/KeyStore;" and o is None:
            if name == "getInstance" and a and a[0] == "AndroidKeyStore":
                self.log_probe("KeyStore.getInstance", a[0], "AndroidKeyStore")
                return _DxObj(cls)
            if name == "getDefaultType":
                return "BKS"
            raise _DxThrow(*_X5_KEX)
        if o is not None and o.t == "Ljava/security/KeyStore;":
            if name == "load":
                if any(x not in (None, 0) for x in a):  # load(null) / load(null, null): a const/4 0 register is null
                    raise _DxAbort
                f["ld"] = True
                return None
            if not f.get("ld"):
                raise _DxThrow(*_X5_KEX)
            if name in ("getCertificateChain", "getCertificate", "containsAlias", "isCertificateEntry") and a \
                    and isinstance(a[0], str):
                n, ders = self.shipped_chain(a[0])
                self.log_probe("KeyStore." + name, a[0], f"{n}: {len(ders)} cert(s)" if n else "null")
                if name == "containsAlias":
                    return int(bool(ders))
                if name == "isCertificateEntry":
                    return 0
                if not ders:
                    return None
                certs = [self.cert_obj(d) for d in ders[:16]]
                if name == "getCertificate":
                    return certs[0]
                r = _DxArr(certs)
                r.t = "Ljava/security/cert/Certificate;"
                return r
            raise _DxAbort
        if o is not None and "X" in f:
            c, der = f["c"], f["X"]
            tbs = c["tbs_certificate"]
            if name in ("getEncoded", "getTBSCertificate", "getSignature"):
                return _dxe_barr(der if name == "getEncoded" else tbs.dump() if name == "getTBSCertificate"
                                 else c["signature_value"].contents[1:])
            if name == "getExtensionValue" and a and isinstance(a[0], str):
                for e in tbs["extensions"] or ():
                    if e["extn_id"].dotted == a[0]:
                        v = e["extn_value"].contents
                        ln = len(v)
                        hdr = bytes([ln]) if ln < 0x80 else bytes([0x80 | (ln.bit_length() + 7) // 8]) + ln.to_bytes(
                            (ln.bit_length() + 7) // 8, "big")
                        self.log_probe("X509Certificate.getExtensionValue", a[0], f"{len(v)} bytes")
                        return _dxe_barr(b"\x04" + hdr + v)
                return self.log_probe("X509Certificate.getExtensionValue", a[0], None)
            if name == "getSerialNumber":
                return _dxe_bi(tbs["serial_number"].native)
            if name in ("getNotBefore", "getNotAfter"):
                dt = c.not_valid_before if name == "getNotBefore" else c.not_valid_after
                d = _DxObj("Ljava/util/Date;")
                d.f["ms"] = int(dt.timestamp() * 1000)
                return d
            if name in ("getSubjectX500Principal", "getIssuerX500Principal"):
                p = _DxObj("Ljavax/security/auth/x500/X500Principal;")
                p.f["N"] = tbs["subject" if name.startswith("getSubject") else "issuer"]
                return p
            if name == "getPublicKey":
                k = _DxObj("Ljava/security/PublicKey;")
                k.f["K"] = tbs["subject_public_key_info"]
                return k
            if name == "getVersion":
                return tbs["version"].native and int(tbs["version"].native[1:]) or 1
            if name == "getType":
                return "X.509"
            if name == "getSigAlgOID":
                return c["signature_algorithm"]["algorithm"].dotted
            if name == "getSigAlgName":
                sa = c["signature_algorithm"]
                ka = _X5_SIGKEY.get(sa.signature_algo)
                if ka is None:
                    raise _DxAbort
                return ka if ka in ("Ed25519", "RSASSA-PSS") else f"{sa.hash_algo.upper()}with{ka}"
            if name == "getBasicConstraints":
                bc = c.basic_constraints_value
                if bc is None or not bc["ca"].native:
                    return -1
                pl = bc["path_len_constraint"].native
                return 0x7FFFFFFF if pl is None else pl
            if name == "getKeyUsage":
                ku = c.key_usage_value
                if ku is None:
                    return None
                bits = ["digital_signature", "non_repudiation", "key_encipherment", "data_encipherment",
                        "key_agreement", "key_cert_sign", "crl_sign", "encipher_only", "decipher_only"]
                r = _DxArr(int(b in ku.native) for b in bits)
                r.t = "Z"
                return r
            raise _DxAbort
        if o is not None and "N" in f:
            if name == "getName" and (not a or a[0] == "RFC2253"):
                return _x5_rfc2253(f["N"])
            if name == "getEncoded":
                return _dxe_barr(f["N"].dump())
            if name in ("toString", "hashCode", "equals"):
                raise _DxAbort
            raise _DxAbort
        if o is not None and "K" in f:
            k = f["K"]
            if name == "getEncoded":
                return _dxe_barr(k.dump())
            if name == "getFormat":
                return "X.509"
            if name == "getAlgorithm":
                return {"rsa": "RSA", "ec": "EC", "dsa": "DSA", "ed25519": "Ed25519"}.get(k.algorithm) or (
                    _ for _ in ()).throw(_DxAbort)
            raise _DxAbort
        if o is not None and "ms" in f:
            ms = f["ms"]
            if name == "getTime":
                return ms
            b = a[0].f.get("ms") if a and isinstance(a[0], _DxObj) else None
            if b is not None and name in ("before", "after", "compareTo", "equals"):
                return {"before": int(ms < b), "after": int(ms > b), "equals": int(ms == b),
                        "compareTo": (ms > b) - (ms < b)}[name]
            raise _DxAbort
        return _ENV_UNSET

    def ctx(self, ref, raw):  # noqa: C901 - one table of Context-backed models
        cls, rest = ref.split("->", 1)
        name, sig = rest.split("(", 1)
        o = raw[0] if raw and isinstance(raw[0], _DxObj) else None
        t = o.t if o is not None else None
        a = raw[1:] if o is not None else raw
        pkg = self.apk["pkg"]
        if t in _CTX_JSON or cls in _CTX_JSON:
            return self.json_call(cls, name, sig, o, a)
        if t == "Ljava/nio/ByteBuffer;" or cls in ("Ljava/nio/ByteBuffer;", "Ljava/nio/ByteOrder;"):
            return self.bbuf(cls, name, sig, o, a)
        if (t in _X5_TYPES or cls in _X5_TYPES) and (o is None or o.t != "Ljava/util/Date;" or "ms" in o.f):
            v = self.x509(cls, name, sig, o, a)
            if v is not _ENV_UNSET:
                return v
        if cls == "Ljava/io/ByteArrayInputStream;" and name == "<init>" and o is not None and a \
                and isinstance(a[0], list):
            off, n = (a[1], a[2]) if len(a) >= 3 else (0, len(a[0]))
            if not (isinstance(off, int) and isinstance(n, int) and 0 <= off and 0 <= n and off + n <= len(a[0])):
                raise _DxAbort
            o.f.update(B=_dxe_bytes(a[0][off:off + n]), pos=0)
            return None
        if t in ("Ljava/util/zip/ZipFile;", "Ljava/util/jar/JarFile;") and o.f.get("zip") and name == "getInputStream" \
                and a and isinstance(a[0], _DxObj) and "zn" in a[0].f:  # the shipped entry bytes (own dex / asset)
            i = self.z.NameToInfo.get(a[0].f["zn"])
            if i is None or i.file_size > _CTX_MAX_ASSET:
                raise _DxAbort
            return self.stream("ZipFile.getInputStream", i.filename, self.z.read(i))
        if o is not None and "B" in o.f:  # an asset stream
            b, pos = o.f["B"], o.f["pos"]
            if name == "read" and sig.startswith(")"):
                o.f["pos"] = min(pos + 1, len(b))
                return b[pos] if pos < len(b) else -1
            if name == "read" and a and isinstance(a[0], list):
                off, n = (a[1], a[2]) if len(a) >= 3 and isinstance(a[1], int) and isinstance(a[2], int) else (0, len(a[0]))
                if off < 0 or n < 0 or off + n > len(a[0]):
                    raise _DxAbort
                if n == 0:
                    return 0
                if pos >= len(b):
                    return -1
                chunk = b[pos:pos + n]
                a[0][off:off + len(chunk)] = [(x ^ 0x80) - 0x80 for x in chunk]
                o.f["pos"] = pos + len(chunk)
                return len(chunk)
            if name in ("readAllBytes", "readBytes") or name == "readNBytes" and sig.startswith("I)"):
                n = len(b) - pos if name != "readNBytes" else max(0, a[0])
                o.f["pos"] = min(len(b), pos + n)
                return _dxe_barr(b[pos:pos + n])
            if name == "available":
                return len(b) - pos
            if name == "skip" and a and isinstance(a[0], int):
                n = max(0, min(a[0], len(b) - pos))
                o.f["pos"] = pos + n
                return n
            if name in ("close", "mark", "reset"):
                return None
            raise _DxAbort
        if name == "<init>" and o is not None and cls in ("Ljava/io/InputStreamReader;", "Ljava/io/BufferedReader;",
                                                         "Ljava/util/Scanner;", "Ljava/io/BufferedInputStream;",
                                                         "Ljava/io/DataInputStream;"):
            src = a[0] if a else None
            if isinstance(src, _DxObj) and "B" in src.f:
                if cls in ("Ljava/io/BufferedInputStream;", "Ljava/io/DataInputStream;"):
                    o.f.update(B=src.f["B"][src.f["pos"]:], pos=0)
                else:
                    o.f["L"] = src.f["B"][src.f["pos"]:].decode("utf-8", "replace").splitlines()
                src.f["pos"] = len(src.f["B"])
                return None
            return _ENV_UNSET
        if cls == "Lkotlin/io/ByteStreamsKt;" and name == "readBytes" and a and isinstance(a[0], _DxObj) and "B" in a[0].f:
            s = a[0]
            out, s.f["pos"] = s.f["B"][s.f["pos"]:], len(s.f["B"])
            return _dxe_barr(out)
        if t in _CTX_PREF or cls in _CTX_PREF:
            return self.pref_call(name, sig, o, a)
        if cls == "Ljava/lang/String;" and name == "<init>" and sig in (
                "[BIILjava/lang/String;)V", "[BIILjava/nio/charset/Charset;)V") and len(a) == 4 and isinstance(a[0], list):
            off, n = a[1], a[2]
            if not (isinstance(off, int) and isinstance(n, int) and 0 <= off and 0 <= n and off + n <= len(a[0])):
                raise _DxAbort
            return _dxe_bytes(a[0][off:off + n]).decode(_dxe_cs(a[3]), "replace")
        if name == "getAssets" and sig == ")Landroid/content/res/AssetManager;":
            return _DxObj("Landroid/content/res/AssetManager;")
        if t == "Landroid/content/res/AssetManager;" or cls == "Landroid/content/res/AssetManager;":
            if name in ("open", "openFd", "openNonAssetFd") and a and isinstance(a[0], str) and name == "open":
                n = "assets/" + a[0].lstrip("/")
                i = self.z.NameToInfo.get(n)
                if i is None or i.file_size > _CTX_MAX_ASSET:
                    self.log_probe("AssetManager.open", a[0], "FileNotFoundException")
                    raise _DxThrow("Ljava/io/FileNotFoundException;", *_ENV_IOE)
                return self.stream("AssetManager.open", a[0], self.z.read(i))
            if name == "list" and a and isinstance(a[0], str):
                d = ("assets/" + a[0].strip("/") + "/").replace("assets//", "assets/")
                names = sorted({n[len(d):].split("/", 1)[0] for n in self.z.NameToInfo if n.startswith(d) and n != d})
                r = _DxArr(names)
                r.t = "Ljava/lang/String;"
                return self.log_probe("AssetManager.list", a[0], r)
            if name == "close":
                return None
            raise _DxAbort
        if name == "getResources" and sig == ")Landroid/content/res/Resources;":
            return _DxObj("Landroid/content/res/Resources;")
        if name in ("getApplicationContext", "getBaseContext") and sig == ")Landroid/content/Context;":
            return o if o is not None and (t in _CTX_TYPES or t in _dxx_supers(self.dx)) else _DxObj(
                "Landroid/content/Context;")
        if name in ("getString", "getText") and sig in ("I)Ljava/lang/String;", "I)Ljava/lang/CharSequence;") and a:
            v = self.res(a[0])
            if not isinstance(v, str):
                raise _DxAbort
            return self.log_probe("Resources." + name, f"{a[0]:#x}", v)
        if t == "Landroid/content/res/Resources;" or cls == "Landroid/content/res/Resources;":
            if name == "openRawResource" and a and isinstance(a[0], int):
                v = self.res(a[0])
                i = self.z.NameToInfo.get(v) if isinstance(v, str) else None
                if i is None or i.file_size > _CTX_MAX_ASSET:
                    self.log_probe("Resources.openRawResource", f"{a[0]:#x}", "NotFoundException")
                    raise _DxThrow(*_CTX_RNF)
                return self.stream("Resources.openRawResource", f"{a[0]:#x}", self.z.read(i))
            if name == "getIdentifier" and len(a) >= 2 and all(isinstance(x, str) or x is None for x in a[:3]):
                n, ty = a[0], a[1]
                m = re.fullmatch(r"(?:[\w.]+:)?(\w+)/(\w+)", n)
                if m:
                    ty, n = m[1], m[2]
                rid = next((k for k, e in sorted(self.res_table().items()) if e["name"] == n and e["type"] == ty), 0)
                return self.log_probe("Resources.getIdentifier", f"{ty}/{n}", rid)
            if name in ("getInteger", "getBoolean") and a:
                v = self.res(a[0])
                if not isinstance(v, (int, bool)):
                    raise _DxAbort
                return self.log_probe("Resources." + name, f"{a[0]:#x}", int(v))
            if name in ("getStringArray", "getTextArray") and a:
                v = self.res(a[0])
                if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
                    raise _DxAbort
                r = _DxArr(v)
                r.t = "Ljava/lang/String;"
                return self.log_probe("Resources." + name, f"{a[0]:#x}", r)
            if name in ("getResourceEntryName", "getResourceName", "getResourceTypeName") and a:
                e = self.res_table().get(a[0])
                if e is None:
                    raise _DxThrow(*_CTX_RNF)
                return {"getResourceEntryName": e["name"], "getResourceTypeName": e["type"],
                        "getResourceName": f"{pkg}:{e['type']}/{e['name']}"}[name]
            raise _DxAbort
        if name == "getPackageName" and sig == ")Ljava/lang/String;" and pkg and o is not None:
            return self.log_probe("getPackageName", "", pkg)
        if name == "getSharedPreferences" and sig == "Ljava/lang/String;I)Landroid/content/SharedPreferences;" and a:
            return self.pref_file(_dxe_str(a[0]))
        if name == "getDefaultSharedPreferences" and cls == "Landroid/preference/PreferenceManager;" \
                or cls == "Landroidx/preference/PreferenceManager;" and name == "getDefaultSharedPreferences":
            return self.pref_file(f"{pkg}_preferences")
        if name == "getPackageInfo" and cls.startswith("Landroid/content/pm/") and pkg and a \
                and isinstance(a[0], str) and a[0].strip() == pkg:
            pi = _EnvVM.env(self, ref, raw)
            P = "Landroid/content/pm/PackageInfo;->"
            pi.f.update({P + "versionCode": _dxe_w32(self.apk["vc"]), P + "versionName": self.apk["vn"],
                         P + "firstInstallTime": _CTX_INSTALL_MS, P + "lastUpdateTime": _CTX_INSTALL_MS})
            return pi
        if t == "Landroid/content/pm/PackageInfo;" and name == "getLongVersionCode":
            return self.apk["vc"]
        if cls in ("Landroid/provider/Settings$Secure;", "Landroid/provider/Settings$System;") and name == "getString" \
                and len(raw) > 1 and raw[1] == "android_id":
            return self.log_probe("Settings.Secure", "android_id", _CTX_ANDROID_ID)
        if cls == "Ljava/lang/System;" and name == "getProperty" and raw and isinstance(raw[0], str) \
                and raw[0] in _CTX_SYSPROPS:
            v = _CTX_SYSPROPS[raw[0]]
            if raw[0] == "java.io.tmpdir" and pkg:
                v = f"/data/user/0/{pkg}/cache"
            return self.log_probe("System.getProperty", raw[0], v)
        if cls == "Ljava/lang/System;" and name == "lineSeparator":
            return "\n"
        return _ENV_UNSET

    def pref_file(self, n):
        p = _DxObj("Landroid/content/SharedPreferences;")
        p.f.update(P=self.prefs.setdefault(n, {}), n=n)
        return p

    def pref_call(self, name, sig, o, a):
        if o is None or "P" not in o.f:
            raise _DxAbort
        P = o.f["P"]
        if o.t == "Landroid/content/SharedPreferences;":
            if name.startswith("get") and name != "getAll" and a and isinstance(a[0], str):
                v = P.get(a[0], a[1] if len(a) > 1 else None)
                self.log_probe("SharedPreferences." + name, f"{o.f['n']}:{a[0]}", v if a[0] in P else f"default {v!r}")
                return v
            if name == "contains" and a:
                return int(a[0] in P)
            if name == "edit":
                e = _DxObj("Landroid/content/SharedPreferences$Editor;")
                e.f.update(P=P, W={}, n=o.f["n"])
                return e
            raise _DxAbort
        W = o.f["W"]
        if name.startswith("put") and a and isinstance(a[0], str):
            W[a[0]] = a[1] if len(a) > 1 else None
            return o
        if name == "remove" and a:
            W[a[0]] = _ENV_UNSET
            return o
        if name == "clear":
            P.clear()
            return o
        if name in ("apply", "commit"):
            for k, v in W.items():
                P.pop(k, None) if v is _ENV_UNSET else P.__setitem__(k, v)
            W.clear()
            return None if name == "apply" else 1
        raise _DxAbort

    def json_call(self, cls, name, sig, o, a):  # noqa: C901 - org.json's accessors
        if name == "<init>":
            if o is None or not a or not isinstance(a[0], str):
                raise _DxAbort
            try:
                v = json.loads(a[0])
            except ValueError:
                raise _DxThrow(*_CTX_JEX) from None
            if not isinstance(v, dict if o.t == "Lorg/json/JSONObject;" else list):
                raise _DxThrow(*_CTX_JEX)
            o.f["J"] = v
            self.log_probe("org.json." + o.t[10:-1], a[0][:64], f"{len(v)} keys")
            return None
        if o is None or "J" not in o.f:
            raise _DxAbort
        J = o.f["J"]
        if name in ("length", "size"):
            return len(J)
        if name == "toString" and not a:
            return json.dumps(J, separators=(",", ":"))
        if name in ("has", "isNull") and a:
            x = J.get(a[0], None) if isinstance(J, dict) else (J[a[0]] if 0 <= a[0] < len(J) else None)
            return int(a[0] in J if name == "has" else x is None)
        if not a:
            raise _DxAbort
        k = a[0]
        try:
            v, miss = (J[k], False) if isinstance(J, dict) and isinstance(k, str) or isinstance(J, list) and isinstance(
                k, int) and 0 <= k < len(J) else (None, True)
        except (KeyError, TypeError):
            v, miss = None, True
        opt = name.startswith("opt")
        base = name[3:] if opt else name[3:] if name.startswith("get") else None
        if base is None:
            raise _DxAbort
        dflt = a[1] if opt and len(a) > 1 else None
        if base == "String":
            if miss or v is None:
                if opt:
                    return dflt if len(a) > 1 else ""
                raise _DxThrow(*_CTX_JEX)
            return _ctx_jstr(v)
        if base in ("Int", "Long"):
            w = _dxe_w32 if base == "Int" else _dxe_w64
            n = None if miss else _ctx_jnum(v, w)
            if n is None:
                if opt:
                    return dflt if isinstance(dflt, int) else 0
                raise _DxThrow(*_CTX_JEX)
            return n
        if base == "Boolean":
            b = v if isinstance(v, bool) else {"true": True, "false": False}.get(v.lower()) if isinstance(v, str) else None
            if b is None or miss:
                if opt:
                    return dflt if isinstance(dflt, int) else 0
                raise _DxThrow(*_CTX_JEX)
            return int(b)
        if base in ("JSONObject", "JSONArray"):
            want = dict if base == "JSONObject" else list
            if miss or not isinstance(v, want):
                if opt:
                    return None
                raise _DxThrow(*_CTX_JEX)
            return self.json("Lorg/json/" + base + ";", v)
        raise _DxAbort


def context_chain_scan(apk):
    """ANS tokens of app methods handed a Context (D23-style `Release.code(Context)` and its v2 successors), run by the
    deep evaluator on a clean retail Pixel whose Context answers from the APK's own bytes: assets (AssetManager.open ->
    zip entry, InputStream read / available / readAllBytes, readers), org.json JSONObject / JSONArray accessors,
    resources.arsc strings by id / getIdentifier, package name, PackageInfo (signer cert, versionCode / versionName,
    install times), ApplicationInfo.flags (manifest debuggable), ZipFile(sourceDir).getInputStream (the shipped dex /
    asset bytes), ByteBuffer wrap / getLong / order, SharedPreferences (defaults; put + apply read back),
    Settings.Secure ANDROID_ID (a fixed 16-hex id), System.getProperty (ART's values), plus clean_device_scan's root /
    emulator / hook / installer / tamper / Build / clock tables. Returned values first, then strings the run built.
    CONTEXT_STUB_HITS logs every stub answer. [] when absent; never raises; < 1.5 s."""
    rets, seen = [], []
    del CONTEXT_STUB_HITS[:]
    deadline = time.time() + _CTX_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
            dexes = [d for d in dexes if d[:4] == b"dex\n" and len(d) >= 0x70 and b"Landroid/content/Context;" in d]
            if not dexes:
                return []
            facts = _ctx_facts(apk) or {"pkg": None, "dbg": False, "certs": [], "ent": {}, "vc": 1, "vn": None,
                                        "path": "/data/app/app-1/base.apk"}
            prefs, runs = {}, 0
            for d in dexes:
                if time.time() > deadline:
                    break
                try:
                    dx = _DxDex(d)
                except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                    continue
                todo = []
                for ref in dx.order:
                    nreg, nin, _ins, acc = dx.code[ref]
                    ps = _dxe_params(ref)
                    if not any(p in _CTX_TYPES for p in ps) or len(ps) > 4 or nin > nreg or _DXE_LIB.match(ref):
                        continue
                    todo.append((not ref.endswith(")Ljava/lang/String;"), not acc & 0x8, ref, ps, acc))
                todo.sort(key=lambda x: x[:2])
                for _, _, ref, ps, acc in todo:
                    if time.time() > deadline or runs >= _CTX_MAX_RUNS:
                        break
                    runs += 1
                    vm = _CtxVM(dx, deadline, facts, z, prefs)
                    raw = [] if acc & 0x8 else [_DxObj(ref.split("->")[0])]
                    for p in ps:
                        raw += [_DxObj(p) if p in _CTX_TYPES else _dxe_default(p)] + ([None] if p in "JD" else [])
                    r = None
                    try:
                        vm.init_class(ref.split("->")[0])
                        r = vm.run(ref, raw)
                    except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError,
                            RecursionError, struct.error, UnicodeError):
                        pass
                    if isinstance(r, str):
                        rets += ANS_RE_T.findall(r)
                    seen += [m for s in vm.seen if isinstance(s, str) for m in ANS_RE_T.findall(s)]
                    CONTEXT_STUB_HITS.extend(x for x in vm.probe_log if x not in CONTEXT_STUB_HITS)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(rets + seen))


# --- exception-driven control flow: a probe throws, the catch handler picks the path (coverage atlas row 90) ----------
# _EnvVM (clean Pixel) with the dex try_item / encoded_catch_handler tables live: `throw vX` and runtime faults (div /
# rem by zero, null receiver, array index out of range, Integer.parseInt on a non-number, the stubbed probes'
# NameNotFound / ClassNotFound / FileNotFound) go to the first covering handler whose type is a supertype of the thrown
# class (in-dex hierarchy + java.lang's tree), catch-alls (`finally`) included, unwinding through in-dex callers;
# move-exception binds the thrown object (getMessage / getCause / toString modelled). A trap in the handler of a throw
# that only fires when debugged / rooted stays unread.
_DXX_STEPS, _DXX_BUDGET_S, _DXX_MAX_RUNS = 100_000, 0.8, 96
_DXX_PARSE = re.compile(r"Ljava/lang/(?:Integer|Long|Short|Byte);->(?:parse\w+|valueOf|decode)\(Ljava/lang/String;")


class _ExcVM(_EnvVM):
    """_EnvVM whose throws and runtime faults reach the method's catch handlers (see exception_flow_scan)."""
    max_steps = _DXX_STEPS
    exc = True

    def new_instance(self, t):
        if t not in self.dx.sfields and self.exc_types(t):
            return _DxObj(t)
        return super().new_instance(t)

    def invoke(self, ref, raw, depth):
        o = raw[0] if raw else None
        if isinstance(o, _DxObj) and _env_resolve(self.dx, ref) not in self.dx.code and self.exc_types(o.t):
            name, a = ref.split("->", 1)[1].split("(", 1)[0], raw[1:]
            if name == "<init>":
                for x in a[:2]:
                    if isinstance(x, str) and "$msg" not in o.f:
                        o.f["$msg"] = x
                    elif isinstance(x, (_DxObj, _DxThrow)):
                        o.f["$cause"] = x
                return super().invoke(ref, raw, depth) if o.t in _HK_NEW else None
            if name in ("getMessage", "getLocalizedMessage"):
                return self.note(o.f.get("$msg"))
            if name == "getCause":
                return o.f.get("$cause")
            if name == "toString":
                m = o.f.get("$msg")
                return self.note(o.t[1:-1].replace("/", ".") + (f": {m}" if m is not None else ""))
            if name in ("initCause", "fillInStackTrace"):
                if name == "initCause" and a:
                    o.f["$cause"] = a[0]
                return o
            if name in ("printStackTrace", "addSuppressed", "setStackTrace"):
                return None
        if _DXX_PARSE.match(ref):
            try:
                return super().invoke(ref, raw, depth)
            except _DxAbort:
                if raw and isinstance(raw[0], str):
                    raise self.exc_new("Ljava/lang/NumberFormatException;", f'For input string: "{raw[0]}"') from None
                raise
        return super().invoke(ref, raw, depth)


def _dxx_marked(dx, ref):
    """A method with a try block (tries_size > 0) or a `throw` op."""
    code = dx.coff.get(ref)
    if code is None:
        return False
    if struct.unpack_from("<H", dx.d, code + 6)[0]:
        return True
    ins, pc = dx.code[ref][2], 0
    n = len(ins) // 2
    while pc < n:
        p = 2 * pc
        op = ins[p]
        if op == 0x27:
            return True
        if op == 0 and ins[p + 1] in (1, 2, 3):
            if ins[p + 1] == 1:
                pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
            elif ins[p + 1] == 2:
                pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
            else:
                w, k = struct.unpack_from("<HI", ins, p + 2)
                pc += 4 + (w * k + 1) // 2
            continue
        pc += _DOP_W[op]
    return False


def exception_flow_scan(apk):
    """ANS tokens of anti-debug / anti-tamper code that uses try/catch as control flow (row 90): every app method with
    a try block or a `throw`, plus its in-dex callers two levels up, runs on the clean-device evaluator (_EnvVM probes)
    with exceptions modelled -- `throw` (custom SecurityException subclasses included), ArithmeticException on div /
    rem by zero, NullPointerException on a null receiver, ArrayIndexOutOfBounds, NumberFormatException from parseInt,
    the probes' NameNotFound / ClassNotFound / FileNotFound -- each dispatched through the dex's try_item /
    encoded_catch_handler tables to the first handler whose type is a supertype (in-dex class hierarchy + java.lang
    exception tree, catch-all `finally` handlers, nested tries, unwinding through in-dex callees). So a value built
    only inside a handler comes out, and a decoy in the handler of a debugged-path throw stays unread.
    [] when absent; never raises; ~0.8 s."""
    hits = []
    deadline = time.time() + _DXX_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
                marked = [r for r in dx.order if _dxx_marked(dx, r)]
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            if not marked:
                continue
            facts = {ref: _env_scan_ins(dx, dx.code[ref][2])[1] for ref in dx.order}
            todo, layer = list(marked), set(marked)
            for _ in range(2):
                layer = {r for r, c in facts.items() if c & layer} - set(todo)
                todo += sorted(layer)
            for ref in todo[:_DXX_MAX_RUNS]:
                if time.time() > deadline:
                    break
                nreg, nin, _, acc = dx.code[ref]
                ps = _dxe_params(ref)
                if len(ps) > 4 or nin > nreg:
                    continue
                for release in (False, True):
                    vm = _ExcVM(dx, deadline, release)
                    raw = [] if acc & 0x8 else [_DxObj(ref.split("->")[0])]
                    for p in ps:
                        raw += [_DxObj(p) if p in ("Landroid/content/Context;", "Landroid/app/Activity;",
                                                   "Landroid/app/Application;") else _dxe_default(p)] + (
                            [None] if p in "JD" else [])
                    try:
                        vm.init_class(ref.split("->")[0])
                        vm.note(vm.run(ref, raw))
                    except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError,
                            RecursionError, struct.error):
                        pass
                    for s in vm.seen + [v for v in vm.statics.values() if isinstance(v, str)]:
                        hits += ANS_RE_T.findall(s)
                    if release or not any(v for k, v in vm.statics.items() if _ENV_BCDBG.search(k)):
                        break
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- control-flow flattening: while (true) { switch (state) } dispatchers (coverage atlas row 79) ----------------------
# Each app method holding a packed/sparse-switch inside a loop is run by the evaluator with a 200k-step budget, its
# params seeded by 0/"" and by the constants each call site passes; an invoke the evaluator cannot model (println, a
# framework sink) records its String / char / char[] args as emitted output instead of aborting. When that run yields
# no token (an opaque predicate on an unknown value, a float op), a static unflattener follows the case order from the
# initial state (each case ends `const state; goto head`) and concatenates the cases' const-strings / char args /
# char[] writes in that order.
_FCF_STEPS, _FCF_BUDGET_S, _FCF_MAX_SEEDS, _FCF_VISITS, _FCF_WALK = 200_000, 0.9, 8, 512, 4000
_FCF_CATCH = (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError, RecursionError,
              struct.error)


class _FcfVM(_DxVM):
    """_DxVM with the flattening step budget; unknown out-of-dex invokes emit their args and return an opaque value."""
    max_steps = _FCF_STEPS

    def __init__(self, dx, deadline):
        super().__init__(dx, deadline)
        self.out = []

    def invoke(self, ref, raw, depth):
        try:
            return super().invoke(ref, raw, depth)
        except _DxAbort:
            if ref in self.dx.code or ref in _DXE_INTR:
                raise
        ps = _dxe_params(ref)
        i = len(raw) - sum(2 if p in "JD" else 1 for p in ps)
        if i < 0:
            raise _DxAbort
        for p in ps:
            self.out.append(_fcf_text(p, raw[i]))
            i += 2 if p in "JD" else 1
        return None if ref.endswith(")V") else _DXE_UNK


def _fcf_text(p, v):
    """What a sink call prints for one (descriptor, value) arg; "" when not text."""
    if p == "C" and isinstance(v, int):
        return chr(v & 0xFFFF)
    if isinstance(v, str):
        return v
    if isinstance(v, _DxSB):
        return "".join(v.s)
    if p == "[C" and isinstance(v, list) and all(isinstance(c, int) for c in v):
        return "".join(chr(c & 0xFFFF) for c in v)
    return ""


def _fcf_insns(ins):
    """{pc: (op, b1, width)} of one code item, payload pseudo-instructions skipped."""
    out, pc, n = {}, 0, len(ins) // 2
    while pc < n:
        p = 2 * pc
        op, b1, w = ins[p], ins[p + 1], _DOP_W[ins[p]]
        if op == 0x00 and b1 and p + 8 <= len(ins):
            k = struct.unpack_from("<H", ins, p + 2)[0]
            w = 4 + 2 * k if b1 == 1 else (2 + 4 * k if b1 == 2 else (
                4 + (k * struct.unpack_from("<I", ins, p + 4)[0] + 1) // 2 if b1 == 3 else 1))
        out[pc] = (op, b1, max(w, 1))
        pc += max(w, 1)
    return out


def _fcf_flat(ins, at):
    """True for a switch in a loop: a packed/sparse-switch plus a backward goto / if."""
    if not any(v[0] in (0x2B, 0x2C) for v in at.values()):
        return False
    for pc, (op, b1, w) in at.items():
        p = 2 * pc
        off = ((b1 ^ 0x80) - 0x80 if op == 0x28 else struct.unpack_from("<h", ins, p + 2)[0] if op == 0x29 or
               0x32 <= op <= 0x3D else struct.unpack_from("<i", ins, p + 2)[0] if op == 0x2A else 0)
        if off < 0:
            return True
    return False


def _fcf_table(ins, pc, op):
    """{case key: target pc} of the switch at `pc`."""
    q = 2 * (pc + struct.unpack_from("<i", ins, 2 * pc + 2)[0])
    if q < 0 or q + 4 > len(ins):
        return {}
    n = struct.unpack_from("<H", ins, q + 2)[0]
    if op == 0x2B and ins[q:q + 2] == b"\x00\x01":
        k0 = struct.unpack_from("<i", ins, q + 4)[0]
        return {k0 + j: pc + t for j, t in enumerate(struct.unpack_from(f"<{n}i", ins, q + 8))}
    if op == 0x2C and ins[q:q + 2] == b"\x00\x02":
        keys = struct.unpack_from(f"<{n}i", ins, q + 4)
        return dict(zip(keys, (pc + t for t in struct.unpack_from(f"<{n}i", ins, q + 4 + 4 * n))))
    return {}


def _fcf_walk(dx, ins, at, pc, r, stop, pieces, arr):
    """Const-tracking walk from `pc` (gotos followed, known-const ifs evaluated, unknown ifs fall through) until the
    switch at `stop`: the register map there, or None at a return / throw / budget. Sink args go to `pieces`, const
    char[] writes to `arr`."""
    h16 = lambda p: struct.unpack_from("<h", ins, p)[0]  # noqa: E731
    u16 = lambda p: struct.unpack_from("<H", ins, p)[0]  # noqa: E731
    for _ in range(_FCF_WALK):
        if pc == stop:
            return r
        if pc not in at:
            return None
        op, b1, w = at[pc]
        p, A, B = 2 * pc, b1 & 0xF, b1 >> 4
        if op in (0x0E, 0x0F, 0x10, 0x11, 0x27) or op in (0x2B, 0x2C) or (op == 0x00 and b1):
            return None
        if op in (0x28, 0x29, 0x2A):
            pc += (b1 ^ 0x80) - 0x80 if op == 0x28 else (h16(p + 2) if op == 0x29 else
                                                          struct.unpack_from("<i", ins, p + 2)[0])
            continue
        if 0x32 <= op <= 0x3D:
            x, y = (r.get(A), r.get(B)) if op <= 0x37 else (r.get(b1), 0)
            if isinstance(x, int) and isinstance(y, int):
                k = (op - 0x32) % 6
                if (x == y, x != y, x < y, x >= y, x > y, x <= y)[k]:
                    pc += h16(p + 2)
                    continue
            pc += w
            continue
        if op == 0x12:
            r[A] = (B ^ 8) - 8
        elif op == 0x13:
            r[b1] = h16(p + 2)
        elif op == 0x14:
            r[b1] = struct.unpack_from("<i", ins, p + 2)[0]
        elif op == 0x15:
            r[b1] = _dxe_w32(u16(p + 2) << 16)
        elif op == 0x1A:
            r[b1] = dx.s(u16(p + 2))
        elif op == 0x1B:
            r[b1] = dx.s(struct.unpack_from("<I", ins, p + 2)[0])
        elif op in (0x01, 0x07):
            r[A] = r.get(B)
        elif op in (0x02, 0x08):
            r[b1] = r.get(u16(p + 2))
        elif op in (0x03, 0x09):
            r[u16(p + 2)] = r.get(u16(p + 4))
        elif op == 0x50:
            v, ix = r.get(b1), r.get(ins[p + 3])
            if isinstance(v, int) and isinstance(ix, int) and 0 <= ix < 4096:
                arr[ix] = chr(v & 0xFFFF)
        elif 0x6E <= op <= 0x78 and op != 0x73:
            ref2 = dx.mref(u16(p + 2))
            if op <= 0x72:
                g = u16(p + 4)
                regs = [g & 0xF, (g >> 4) & 0xF, (g >> 8) & 0xF, g >> 12, A][:B]
            else:
                regs = list(range(u16(p + 4), u16(p + 4) + b1))
            ps = _dxe_params(ref2)
            i = len(regs) - sum(2 if t in "JD" else 1 for t in ps)
            for t in ps:
                if 0 <= i < len(regs):
                    pieces.append(_fcf_text(t, r.get(regs[i])))
                i += 2 if t in "JD" else 1
        elif op in (0x90, 0x91, 0x92, 0x95, 0x96, 0x97, 0xB0, 0xB1, 0xB2, 0xB5, 0xB6, 0xB7) or 0xD0 <= op <= 0xE2:
            try:
                if op >= 0xD0:
                    k, s, lit = ((op - 0xD0, r.get(B), h16(p + 2)) if op <= 0xD7 else
                                 (op - 0xD8, r.get(ins[p + 2]), (ins[p + 3] ^ 0x80) - 0x80))
                    v = _dxe_binop(1, lit, s, False) if k == 1 else _dxe_binop(k, s, lit, False)
                    dst = A if op <= 0xD7 else b1
                elif op >= 0xB0:
                    v, dst = _dxe_binop(op - 0xB0, r.get(A), r.get(B), False), A
                else:
                    v, dst = _dxe_binop(op - 0x90, r.get(ins[p + 2]), r.get(ins[p + 3]), False), b1
                r[dst] = v
            except _DxAbort:
                r.pop(A if 0xB0 <= op <= 0xD7 else b1, None)
        elif op not in (0x00, 0x1D, 0x1E, 0x1F, 0x24, 0x25, 0x26) and not 0x67 <= op <= 0x6D \
                and not 0x59 <= op <= 0x5F and not 0x4B <= op <= 0x51:
            r.pop(A, None)  # any other op writes vA (4-bit form) or vAA: forget both readings of the destination
            r.pop(b1, None)
            r.pop(b1 + 1, None)
        pc += w
    return None


def _fcf_static(dx, ins, at, seed):
    """Static unflattening: from the state the entry walk carries into each dispatcher switch, follow case -> next
    state (the const the case leaves in the switch register) and join what the cases emit, in that order."""
    out = []
    for spc in [pc for pc, v in at.items() if v[0] in (0x2B, 0x2C)][:4]:
        sreg, tab = at[spc][1], _fcf_table(ins, spc, at[spc][0])
        if len(tab) < 3:
            continue
        pieces, arr = [], {}
        r = _fcf_walk(dx, ins, at, 0, dict(seed), spc, pieces, arr)
        for _ in range(_FCF_VISITS):
            st = r.get(sreg) if r is not None else None
            if not isinstance(st, int) or st not in tab:
                break
            r = _fcf_walk(dx, ins, at, tab[st], r, spc, pieces, arr)
        out += ["".join(pieces), "".join(arr[k] for k in sorted(arr))]
    return out


def flattened_cfg_scan(apk):
    """ANS tokens assembled by a control-flow-flattened method (`while (true) { switch (state) { ... state = K; } }`):
    the dex evaluator runs it with a 200k-step budget and the int state seeded by 0 and by each call site's constants
    (unknown sink calls such as println emit their String / char args); else a static unflattener follows the case
    order from the initial state and joins the cases' const-strings / chars. [] when absent; never raises; < 1 s."""
    hits = []
    deadline = time.time() + _FCF_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            flat = {}
            for ref in dx.order:
                ins = dx.code[ref][2]
                if b"\x2b" in ins[0::2] or b"\x2c" in ins[0::2]:
                    try:
                        at = _fcf_insns(ins)
                        if _fcf_flat(ins, at):
                            flat[ref] = at
                    except struct.error:
                        pass
            helpers = {ref: (_dxe_params(ref), bool(dx.code[ref][3] & 0x8)) for ref in flat if _dxe_params(ref)}
            sites = {}
            if helpers:
                for ref, raw in _dcs_sites(dx, helpers, _DxVM(dx, deadline), deadline, partial=True):
                    if raw not in sites.setdefault(ref, []) and len(sites[ref]) < _FCF_MAX_SEEDS:
                        sites[ref].append(raw)
            for ref, at in flat.items():
                nreg, nin, ins, acc = dx.code[ref]
                ps, ct = _dxe_params(ref), ref.split("->")[0]
                if len(ps) > 6 or nin > nreg:
                    continue
                base = [] if acc & 0x8 else [_DxObj(ct)]
                for p in ps:
                    base += [_dxe_default(p)] + ([None] if p in "JD" else [])
                raws = [[v if isinstance(v, (int, str)) else b for v, b in zip(raw, base)]
                        for raw in sites.get(ref, []) if len(raw) == len(base)] + [base]
                for raw in raws:
                    if time.time() > deadline:
                        break
                    vm = _FcfVM(dx, deadline)
                    try:
                        vm.init_class(ct)
                        vm.note(vm.run(ref, list(raw)))
                    except _FCF_CATCH:
                        pass
                    texts = vm.seen + ["".join(vm.out)] + [v for v in vm.statics.values() if isinstance(v, str)]
                    if not any(ANS_RE_T.search(t) for t in texts):
                        seed = {nreg - nin + i: v for i, v in enumerate(raw) if isinstance(v, int)}
                        try:
                            texts += _fcf_static(dx, ins, at, seed)
                        except _FCF_CATCH:
                            pass
                    found = [m for t in texts for m in ANS_RE_T.findall(t)]
                    hits += found
                    if found:
                        break
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- anti-debug state machines: the clean terminal state emits the answer (coverage atlas rows 41, 79, 89) ------------
# An app method holding a loop that re-assigns a state (switch dispatcher, a field written >= 3 times, String.equals
# chain) and reaching a debugger / tracer / timing / adb probe within two calls is run by ONE evaluator that is both the
# flattening VM (sink args emitted) and the clean-device VM (probe table), after <clinit> / <init>()V / onCreate set the
# initial state. A second run answers the probes as DEBUGGED (debugger attached, FLAG_DEBUGGABLE, TracerPid != 0,
# adb_enabled, 3 s timing deltas): tokens only that run reaches are the decoy / honeypot branch and are demoted.
_ADS_BUDGET_S, _ADS_MAX_RUNS = 0.75, 48
_ADS_TIME = re.compile(r"Ljava/lang/System;->(?:nanoTime|currentTimeMillis)|Landroid/os/SystemClock;->"
                       r"(?:elapsedRealtime|uptimeMillis|currentThreadTimeMillis)|Landroid/os/Debug;->threadCpuTimeNanos")
_ADS_ENTRY = ("onCreate(Landroid/os/Bundle;)V", "onResume()V", "onStart()V")


class _AdsVM(_FcfVM, _EnvVM):
    """Flattening VM x clean-device VM in one env (MRO: sink emission -> probe table -> dex evaluator); `dbg` flips the
    debugger-facing probes so the honeypot branch can be told apart. Monotonic clocks advance 50 us per read (3 s
    when debugged)."""

    def __init__(self, dx, deadline, dbg=False):
        super().__init__(dx, deadline)
        self.dbg, self.trace, self.ns = dbg, [], 1_700_000_000_000_000_000

    def env(self, ref, raw):
        if _ADS_TIME.match(ref):
            self.ns += 3_000_000_000 if self.dbg else 50_000
            return self.ns if "Nanos" in ref or "nanoTime" in ref else self.ns // 1_000_000
        v = super().env(ref, raw)
        if not self.dbg:
            return v
        cls, rest = ref.split("->", 1)
        name = rest.split("(")[0]
        if cls in ("Landroid/os/Debug;", "Ldalvik/system/VMDebug;") and name in (
                "isDebuggerConnected", "waitingForDebugger", "isDebuggingEnabled"):
            return 1
        if isinstance(v, _DxObj) and v.t == "Landroid/content/pm/ApplicationInfo;":
            v.f["Landroid/content/pm/ApplicationInfo;->flags"] |= 2
        if cls.startswith("Landroid/provider/Settings$") and v == 0 and name in ("getInt", "getLong"):
            return 1
        if name == "<init>" and raw and isinstance(raw[0], _DxObj) and isinstance(raw[0].f.get("L"), list):
            raw[0].f["L"] = ["TracerPid:\t4242" if ln.startswith("TracerPid:") else ln for ln in raw[0].f["L"]]
        return v


def _ads_shape(dx, ins):
    """(state loop, touches a timing / env probe, {in-dex callees}) of one method's code."""
    marked, calls = _env_scan_ins(dx, ins)
    at = _fcf_insns(ins)
    loop, switch, eq, puts, timing = False, False, 0, {}, False
    for pc, (op, b1, w) in at.items():
        p = 2 * pc
        if op in (0x28, 0x29, 0x2A, *range(0x32, 0x3E)):
            off = ((b1 ^ 0x80) - 0x80 if op == 0x28 else struct.unpack_from("<i", ins, p + 2)[0] if op == 0x2A else
                   struct.unpack_from("<h", ins, p + 2)[0])
            loop |= off < 0
        elif op in (0x2B, 0x2C):
            switch = True
        elif 0x59 <= op <= 0x5F or 0x67 <= op <= 0x6D:
            k = struct.unpack_from("<H", ins, p + 2)[0]
            puts[k] = puts.get(k, 0) + 1
        elif 0x6E <= op <= 0x78 and op != 0x73:
            m = dx.mref(struct.unpack_from("<H", ins, p + 2)[0])
            eq += m == "Ljava/lang/String;->equals(Ljava/lang/Object;)Z"
            timing |= bool(_ADS_TIME.match(m))
    return loop and (switch or eq >= 2 or max(puts.values(), default=0) >= 3), marked or timing, calls


def _ads_run(dx, ref, deadline, dbg):
    """One evaluation of `ref` (after <clinit>, <init>()V and the class's onCreate) -> (texts, switch-key path)."""
    nreg, nin, _, acc = dx.code[ref]
    ct, ps = ref.split("->")[0], _dxe_params(ref)
    vm = _AdsVM(dx, deadline, dbg)
    obj = _DxObj(ct)
    texts = []
    try:
        vm.init_class(ct)
        pre = [f"{ct}-><init>()V"] + [f"{ct}->{e}" for e in _ADS_ENTRY if not ref.endswith("->" + e)]
        for r0 in pre if not acc & 0x8 else []:
            if r0 in dx.code:
                vm.steps = 0
                try:
                    vm.run(r0, [obj] + [None] * (dx.code[r0][1] - 1))
                except _FCF_CATCH:
                    pass
        vm.trace, vm.steps = [], 0
        raw = [] if acc & 0x8 else [obj]
        for p in ps:
            raw += [_DxObj(p) if p in ("Landroid/content/Context;", "Landroid/app/Activity;") else _dxe_default(p)] + (
                [None] if p in "JD" else [])
        res = vm.run(ref, raw)
        texts.append(_dxe_str(res) if isinstance(res, _DxSB) else res)
    except _FCF_CATCH:
        pass
    texts += vm.seen + ["".join(vm.out)] + [v for v in vm.statics.values() if isinstance(v, str)]
    texts += [_dxe_str(v) if isinstance(v, _DxSB) else v for v in obj.f.values()]
    return [t for t in texts if isinstance(t, str)], vm.trace


def anti_debug_state_facts(apk):
    """[{"value", "method", "path", "clean"}] of an anti-debug state machine's terminal values: clean-path tokens first
    (path = switch keys taken), then tokens reached only when a probe says 'debugged' (clean False: decoy / trap /
    honeypot). [] when absent; never raises; < 0.8 s."""
    rows, seen = [], set()
    deadline = time.time() + _ADS_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline or not re.search(
                    rb"Landroid/os/(?:Debug|SystemClock);|TracerPid|ApplicationInfo;|nanoTime|Settings\$|adb_enabled", d):
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            facts = {}
            for ref in dx.order:
                if _DXE_LIB.match(ref.split("->")[0]):
                    continue
                try:
                    facts[ref] = _ads_shape(dx, dx.code[ref][2])
                except (struct.error, IndexError, KeyError):
                    pass
            probed = {r for r, f in facts.items() if f[1]}
            for _ in range(2):
                probed |= {r for r, f in facts.items() if f[2] & probed}
            sms = [r for r, f in facts.items() if f[0] and (f[1] or f[2] & probed)]
            entries = sms + sorted({r for r, f in facts.items() if f[2] & set(sms)} - set(sms))
            clean, trap = [], []
            for ref in entries[:_ADS_MAX_RUNS]:
                if time.time() > deadline:
                    break
                if len(_dxe_params(ref)) > 4 or dx.code[ref][1] > dx.code[ref][0]:
                    continue
                for dbg, sink in ((False, clean), (True, trap)):
                    texts, path = _ads_run(dx, ref, deadline, dbg)
                    sink += [(m, ref, path) for t in texts for m in ANS_RE_T.findall(t)]
            good = {m for m, _, _ in clean}
            for (m, ref, path), ok in [(c, True) for c in clean] + [(t, False) for t in trap if t[0] not in good]:
                if (m, ok) not in seen:
                    seen.add((m, ok))
                    rows.append({"value": m, "method": ref, "path": path[:64], "clean": ok})
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return sorted(rows, key=lambda r: not r["clean"])


def anti_debug_state_scan(apk):
    """ANS tokens a clean-room anti-debug state machine emits on its CLEAN terminal state (int / String state re-assigned
    in a loop or switch dispatcher, transitions on Debug.isDebuggerConnected / waitingForDebugger, ApplicationInfo.flags
    & FLAG_DEBUGGABLE, TracerPid, timing deltas, Settings adb_enabled), run from the state <clinit> / <init> / onCreate
    set. Values only a 'debugged' probe answer reaches (honeypots) are left out -- anti_debug_state_facts lists them,
    demoted. [] when absent; never raises; < 0.8 s."""
    return [r["value"] for r in anti_debug_state_facts(apk) if r["clean"]]


# --- Kotlin coroutine state machines: invokeSuspend resumed in label order (coverage atlas, mobile kotlin row) --------
_KCO_REF = "->invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;"
_KCO_CONT = "Lkotlin/coroutines/Continuation;"
_KCO_RESUMES, _KCO_BUDGET_S, _KCO_MAX_SM = 64, 0.6, 256


class _KcoVM(_DxVM):
    """_DxVM for a compiled `suspend` block: COROUTINE_SUSPENDED is one sentinel object, every out-of-dex call taking a
    Continuation (delay, withContext, ...) suspends, kotlin runtime plumbing (throwOnFailure, Intrinsics checks, super
    constructors) is a no-op, android.util.Log args are noted, and instance-of matches the exact in-dex class."""
    inst_of = True

    def __init__(self, dx, deadline, susp):
        super().__init__(dx, deadline)
        self.susp = susp
        self.statics["Lkotlin/coroutines/intrinsics/CoroutineSingletons;->COROUTINE_SUSPENDED"] = susp
        self.statics["Lkotlin/Unit;->INSTANCE"] = _DxObj("Lkotlin/Unit;")

    def new_instance(self, t):
        return _DxObj(t)

    def invoke(self, ref, raw, depth):
        ct, name = ref.split("->")[0], ref.split("->")[1].split("(")[0]
        if name == "getCOROUTINE_SUSPENDED" and ct.startswith("Lkotlin/"):
            return self.susp
        ext = ref not in self.dx.code or ct.startswith(("Lkotlin/", "Lkotlinx/"))
        if ext and ref not in _DXE_INTR:
            if _KCO_CONT in _dxe_params(ref):
                return self.susp
            if ct.startswith("Landroid/util/Log;"):
                for v in raw:
                    self.note(_fcf_text("Ljava/lang/String;", v) if isinstance(v, _DxSB) else v)
                return 0
            if name == "<init>" or ref.endswith(")V") or ct.startswith("Lkotlin/jvm/internal/Intrinsics;"):
                return raw[0] if name.startswith("check") and raw else None
        return super().invoke(ref, raw, depth)


def coroutine_state_scan(apk):
    """ANS tokens built across the suspension points of a Kotlin coroutine: every class with
    invokeSuspend(Object) (SuspendLambda of a launch {} block, or the ContinuationImpl of a named `suspend fun` that
    re-enters the outer method with label | MIN_VALUE) is resumed on ONE object until it stops returning
    COROUTINE_SUSPENDED, so the `switch (label)` cases run in label order with the values spilled in L$n / I$n / J$n
    fields carried between them. Tokens come from the final value, spilled strings and Log args. [] when absent;
    never raises; < 1 s."""
    hits = []
    deadline = time.time() + _KCO_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or b"invokeSuspend" not in d or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            sms = [r for r in dx.order if r.endswith(_KCO_REF)][:_KCO_MAX_SM]
            for ref in sms:
                if time.time() > deadline:
                    break
                susp = _DxObj("Lkotlin/coroutines/intrinsics/CoroutineSingletons;")
                vm = _KcoVM(dx, deadline, susp)
                ct = ref.split("->")[0]
                obj, res, texts = _DxObj(ct), None, []
                try:
                    vm.init_class(ct)
                    for _ in range(_KCO_RESUMES):
                        vm.steps = 0
                        res = vm.run(ref, [obj, vm.statics["Lkotlin/Unit;->INSTANCE"]])
                        texts += [_dxe_str(v) if isinstance(v, _DxSB) else v for v in obj.f.values()]
                        if res is not susp:
                            break
                except _FCF_CATCH:
                    pass
                texts += vm.seen + [_dxe_str(res) if isinstance(res, _DxSB) else res]
                hits += [m for t in texts if isinstance(t, str) for m in ANS_RE_T.findall(t)]
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- bound Service / AIDL / Messenger: transaction code -> reply value (coverage atlas: binder-ontransact-code-map) ------
# Binder.onTransact(int code, Parcel data, Parcel reply, int flags) (an AIDL `I*$Stub` or a hand-written Binder) and
# Handler.handleMessage(Message) (a Messenger service switching on msg.what) are run once per case key with a stub
# Parcel / Bundle: reads answer the constants the case compares them against (String.equals / TextUtils.equals wants,
# else the code's own int / string literals), writes to `reply`, Bundle.put*, Message.obj and Messenger.send are kept.
_BND_ENTRY = ("->onTransact(ILandroid/os/Parcel;Landroid/os/Parcel;I)Z", "->handleMessage(Landroid/os/Message;)V",
              "->handleMessage(Landroid/os/Message;)Z")
_BND_PRE = re.compile(rb"onTransact\0|handleMessage\0")
_BND_EQ = frozenset(("Ljava/lang/String;->equals(Ljava/lang/Object;)Z", "Ljava/lang/String;->equalsIgnoreCase(Ljava/lang/String;)Z",
                     "Ljava/lang/String;->contentEquals(Ljava/lang/CharSequence;)Z",
                     "Ljava/util/Objects;->equals(Ljava/lang/Object;Ljava/lang/Object;)Z",
                     "Landroid/text/TextUtils;->equals(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Z"))
_BND_NOOP = ("Landroid/os/Binder;", "Landroid/os/Handler;", "Landroid/app/Service;", "Ljava/lang/Object;",
             "Landroid/os/Messenger;", "Landroid/os/Bundle;", "Landroid/os/Message;", "Landroid/os/Parcel;")
_BND_NAMED = re.compile(r"->(?:TRANSACTION|MSG|CODE|WHAT|TX|CMD|OP)_?(\w+)$")
_BND_PREF = re.compile(r"(?i)secret|flag|answer|token|reveal|unlock|key|vault|ans\b")
_BND_BUDGET_S, _BND_MAX_ENTRY, _BND_MAX_CODES, _BND_MAX_RUNS = 0.8, 24, 40, 48
_BND_ITF = 0x5F4E5446  # IBinder.INTERFACE_TRANSACTION ('_NTF')


class _BndStr(str):
    """A string a Parcel / Bundle read returned; `k` is the read's index in this run."""
    k = -1


class _BndVM(_DxVM):
    """_DxVM for one binder transaction: Parcel / Bundle / Message / Messenger modelled, app virtual calls resolved on
    the receiver's runtime class (an abstract Stub's onTransact reaching the concrete Impl), framework constructors and
    super.onTransact no-ops; the reads made, the equality wants on them and the reply values are recorded."""

    def __init__(self, dx, deadline, answers):
        super().__init__(dx, deadline)
        self.answers, self.reads, self.wants, self.out, self.desc, self.lits = answers, [], {}, [], [], set()

    def new_instance(self, t):
        return _DxObj(t)

    def read(self, kind, dflt=None):
        k = len(self.reads)
        self.reads.append((k, kind))
        v = self.answers.get(k, dflt if dflt is not None else ("" if kind == "S" else 0))
        if kind == "S" and isinstance(v, str):
            v = _BndStr(v)
            v.k = k
        return v

    def keep(self, v):
        v = _dxe_str(v) if isinstance(v, _DxSB) else v
        if isinstance(v, str):
            self.out.append(str(v))
        elif isinstance(v, int) and not isinstance(v, bool):
            self.out.append(str(v))
        elif isinstance(v, list) and v and all(isinstance(c, int) for c in v):
            self.out.append(bytes(c & 0xFF for c in v).decode("latin-1"))
        elif isinstance(v, _DxObj) and v.t == "Landroid/os/Bundle;":
            for x in v.f.get("$m", {}).values():
                self.keep(x)
        elif isinstance(v, _DxObj) and v.t == "Landroid/os/Message;":
            self.keep(v.f.get("Landroid/os/Message;->obj"))
            self.keep(v.f.get("$data"))

    def invoke(self, ref, raw, depth):  # noqa: C901 - one framework model
        ct, rest = ref.split("->", 1)
        name = rest[:rest.index("(")]
        ps = _dxe_params(ref)
        inst = len(raw) == sum(2 if p in "JD" else 1 for p in ps) + 1
        o = raw[0] if raw else None
        if inst and isinstance(o, _DxObj) and o.t != ct and not _DXE_LIB.match(o.t):
            r2 = _env_resolve(self.dx, f"{o.t}->{rest}")
            if r2 in self.dx.code:
                ref, ct = r2, r2.split("->")[0]
        if ref in self.dx.code:
            self.lits.add(ref)
        if ref in _BND_EQ:
            a, b = raw[0], raw[1] if len(raw) > 1 else None
            for x, y in ((a, b), (b, a)):
                if isinstance(x, _BndStr) and isinstance(y, str) and not isinstance(y, _BndStr):
                    self.wants[x.k] = str(y)
            if not isinstance(a, str) or not isinstance(b, str):
                return int(a is b)
            return int(a.lower() == b.lower() if name == "equalsIgnoreCase" else a == b)
        if ct == "Landroid/os/Parcel;":
            if name == "obtain":
                p = _DxObj(ct)
                p.f["$role"] = "reply"
                return p
            role = o.f.get("$role") if isinstance(o, _DxObj) else None
            if name == "enforceInterface":
                self.desc.append(raw[1] if len(raw) > 1 else None)
                return None
            if name.startswith("read") and role == "data":
                kind = {"readString": "S", "readInt": "I", "readLong": "J", "readByte": "I"}.get(name)
                if kind is None:
                    raise _DxAbort
                return self.read(kind)
            if name.startswith("write") and role == "reply":
                for v in raw[1:]:
                    self.keep(v)
                return None
            if name in ("recycle", "readException", "setDataPosition", "writeNoException", "dataPosition"):
                return 0 if name == "dataPosition" else None
            raise _DxAbort
        if ct == "Landroid/os/Message;":
            if name == "obtain":
                m = _DxObj(ct)
                vals = raw[1:] if ps and ps[0] == "Landroid/os/Handler;" else raw
                for k_, v in zip(("what", "arg1", "arg2"), [v for v, p in zip(vals, ps[1:] if ps and ps[0] ==
                                                           "Landroid/os/Handler;" else ps) if p == "I"]):
                    m.f["Landroid/os/Message;->" + k_] = v
                if ps and ps[-1] == "Ljava/lang/Object;":
                    m.f["Landroid/os/Message;->obj"] = raw[-1]
                return m
            if name in ("getData", "peekData") and isinstance(o, _DxObj):
                b = o.f.get("$data")
                if b is None and name == "getData":
                    b = o.f["$data"] = _DxObj("Landroid/os/Bundle;")
                return b
            if name == "setData" and isinstance(o, _DxObj):
                o.f["$data"] = raw[1]
                return None
            if name in ("recycle", "sendToTarget"):
                self.keep(o)
                return None
        if ct == "Landroid/os/Bundle;" and isinstance(o, _DxObj):
            m = o.f.setdefault("$m", {})
            if name.startswith("put") and len(raw) >= 3:
                m[raw[1]] = raw[2]
                return None
            if name in ("getString", "getInt", "getCharSequence", "getLong") and len(raw) >= 2:
                if raw[1] in m:
                    return m[raw[1]]
                return self.read("I" if name in ("getInt", "getLong") else "S",
                                 raw[2] if len(raw) > 2 and not isinstance(raw[2], _DxObj) else None)
            if name in ("containsKey", "isEmpty"):
                return int(raw[1] in m) if name == "containsKey" else int(not m)
        if ct == "Landroid/os/Messenger;" and name == "send":
            self.keep(raw[1] if len(raw) > 1 else None)
            return None
        if ct == "Landroid/os/Binder;" and name in ("getCallingUid", "getCallingPid"):
            return 10123 if name == "getCallingUid" else 4321
        if ct == "Landroid/os/Process;" and name in ("myUid", "myPid"):
            return 10123 if name == "myUid" else 4321
        if ct == "Landroid/util/Log;":
            for v in raw:
                self.note(_dxe_str(v) if isinstance(v, _DxSB) else v)
            return 0
        if ref not in self.dx.code and ref not in _DXE_INTR and (ct.startswith(_BND_NOOP) or ct in self.dx.sfields
                                                                  or _dxx_supers(self.dx).get(ct)):
            if name in ("<init>", "attachInterface", "handleMessage", "onCreate", "onDestroy", "removeMessages"):
                return None
            if name in ("onTransact", "sendMessage", "sendEmptyMessage", "post", "asBinder", "getBinder"):
                return 0 if ref.endswith(")Z") else None
        return super().invoke(ref, raw, depth)


def _bnd_literals(dx, refs):
    """(int literals, const-strings) of the given methods' code items, in order (the candidate read answers)."""
    ints, strs = [], []
    for ref in refs:
        ins = dx.code[ref][2]
        for op, o in _dga_ops(ins):
            b1 = ins[o + 1]
            if op == 0x12:
                ints.append(((b1 >> 4) ^ 8) - 8)
            elif op == 0x13 or 0xD0 <= op <= 0xD7:
                ints.append(struct.unpack_from("<h", ins, o + 2)[0])
            elif op == 0x14:
                ints.append(struct.unpack_from("<i", ins, o + 2)[0])
            elif 0xD8 <= op <= 0xE2:
                ints.append((ins[o + 3] ^ 0x80) - 0x80)
            elif op in (0x1A, 0x1B):
                strs.append(dx.s(struct.unpack_from("<H" if op == 0x1A else "<I", ins, o + 2)[0]))
    return (list(dict.fromkeys(i for i in ints if i not in (0, 1, -1)))[:24],
            list(dict.fromkeys(s for s in strs if isinstance(s, str) and 0 < len(s) <= 128))[:24])


def _bnd_codes(ins):
    """Case keys of every packed / sparse switch of `ins`."""
    at = _fcf_insns(ins)
    keys = []
    for pc, (op, _, _) in at.items():
        if op in (0x2B, 0x2C):
            keys += sorted(_fcf_table(ins, pc, op))
    return list(dict.fromkeys(keys))


def _bnd_run(dx, ref, recv, code, answers, deadline):
    vm = _BndVM(dx, deadline, answers)
    is_tx = ref.endswith(_BND_ENTRY[0])
    try:
        vm.init_class(recv.t)
        if is_tx:
            data, reply = _DxObj("Landroid/os/Parcel;"), _DxObj("Landroid/os/Parcel;")
            data.f["$role"], reply.f["$role"] = "data", "reply"
            vm.run(ref, [recv, code, data, reply, 0])
        else:
            msg = _DxObj("Landroid/os/Message;")
            msg.f.update({"Landroid/os/Message;->what": code, "Landroid/os/Message;->arg1": 0,
                          "Landroid/os/Message;->arg2": 0, "Landroid/os/Message;->replyTo": _DxObj(
                              "Landroid/os/Messenger;"), "$data": _DxObj("Landroid/os/Bundle;")})
            vm.run(ref, [recv, msg])
    except _FCF_CATCH:
        pass
    return vm


def _bnd_solve(dx, ref, recv, code, deadline, runs, run=None):
    """The run of one case whose reads answer the case's comparisons (wants, then literal candidates, 2 levels)."""
    best = None
    run = run or _bnd_run

    def solve(ans, depth):
        nonlocal best
        vm = None
        for _ in range(6):
            if runs[0] <= 0 or time.time() > deadline:
                return vm
            runs[0] -= 1
            vm = run(dx, ref, recv, code, ans, deadline)
            if best is None or len(vm.out) > len(best.out):
                best = vm
            if any(ANS_RE_T.search(s) for s in vm.out + vm.seen):
                return vm
            new = {k: v for k, v in vm.wants.items() if ans.get(k) != v}
            if not new:
                break
            ans = {**ans, **new}
        free = [(k, kind) for k, kind in vm.reads if k not in ans]
        if depth >= 2 or not free:
            return vm
        k, kind = free[0]
        ints, strs = _bnd_literals(dx, [ref] + sorted(vm.lits))
        for c in (strs if kind == "S" else ints):
            r = solve({**ans, k: c}, depth + 1)
            if r is not None and any(ANS_RE_T.search(s) for s in r.out + r.seen):
                return r
        return vm

    vm = solve({}, 0)
    return vm if vm is not None and any(ANS_RE_T.search(s) for s in vm.out + vm.seen) else best


def binder_transact_facts(apk):
    """[{"class", "entry": "onTransact" | "handleMessage", "code", "name", "descriptor", "values", "tokens"}] per case of
    every in-dex Binder.onTransact / Handler.handleMessage (receiver: the class or its in-dex subclasses, e.g. an
    abstract AIDL Stub's Impl), the case's reads answered with the constants it compares against; `name` is the
    TRANSACTION_* / MSG_* static naming that code. [] when absent; never raises; < 1 s."""
    rows = []
    deadline = time.time() + _BND_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or not _BND_PRE.search(d) or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            sup = _dxx_supers(dx)
            entries = [r for r in dx.order if r.endswith(_BND_ENTRY)][:_BND_MAX_ENTRY]
            for ref in entries:
                ct = ref.split("->")[0]
                subs = [c for c in sup if c != ct and (sup.get(c) == ct or sup.get(sup.get(c)) == ct)]
                names = {}
                nvm = _DxVM(dx, deadline)
                for c in [ct] + subs + [ct.split("$")[0] + ";"]:
                    try:
                        nvm.init_class(c)
                    except _FCF_CATCH:
                        pass
                for k, v in nvm.statics.items():
                    m = _BND_NAMED.search(k)
                    if m and isinstance(v, int):
                        names.setdefault(v, m.group(1))
                codes = _bnd_codes(dx.code[ref][2])
                codes = list(dict.fromkeys(codes + sorted(names) + [1]))[:_BND_MAX_CODES]
                runs = [_BND_MAX_RUNS * 4]
                for code in codes:
                    if time.time() > deadline:
                        break
                    vm = None
                    for rc in subs[:4] + [ct]:
                        per = [min(runs[0], _BND_MAX_RUNS)]
                        before = per[0]
                        vm = _bnd_solve(dx, ref, _DxObj(rc), code, deadline, per)
                        runs[0] -= before - per[0]
                        if vm is not None and (vm.out or vm.seen):
                            break
                    if vm is None or not (vm.out or vm.desc):
                        continue
                    toks = list(dict.fromkeys(m for s in vm.out + vm.seen for m in ANS_RE_T.findall(s)))
                    rows.append({"class": ct, "entry": "onTransact" if "onTransact" in ref else "handleMessage",
                                 "code": code, "name": names.get(code, "INTERFACE" if code == _BND_ITF else None),
                                 "descriptor": next((x for x in vm.desc if isinstance(x, str)), None),
                                 "values": list(dict.fromkeys(vm.out))[:16], "tokens": toks})
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return rows


def binder_transact_scan(apk):
    """ANS tokens a bound service hands back per transaction code / msg.what (binder_transact_facts), the code a
    TRANSACTION_* / MSG_* name calls secret / flag / token / reveal first. [] when absent; never raises; < 1 s."""
    rows = binder_transact_facts(apk)
    rows.sort(key=lambda r: not (r["name"] and _BND_PREF.search(r["name"])))
    return list(dict.fromkeys(t for r in rows for t in r["tokens"]))


# --- broadcast receiver: (action, extras) -> emitted value (coverage atlas: broadcast-receiver-action-map) -------------
# Every in-dex BroadcastReceiver.onReceive(Context, Intent) is run once per action it can receive: the manifest
# <receiver>'s intent-filter actions, IntentFilter(action) / addAction strings of dynamic registerReceiver calls and the
# action-like const-strings of onReceive itself. The delivered Intent's getAction returns that action; its extras (and
# getExtras Bundle reads) answer the constants the code compares them against (_bnd_solve). setResultData /
# setResult / setResultExtras, Log, Toast, sendBroadcast extras and SharedPreferences.put* are kept; receivers sharing
# an action run in priority order with getResultData chaining the previous receiver's result (ordered broadcast).
_BRC_ENTRY = "->onReceive(Landroid/content/Context;Landroid/content/Intent;)V"
_BRC_PRE = re.compile(rb"onReceive\0")
_BRC_ACT = re.compile(r"[A-Za-z_][\w$]*(?:\.[\w$]+)+")
_BRC_IF = ("Landroid/content/IntentFilter;-><init>(Ljava/lang/String;", "Landroid/content/IntentFilter;->addAction(")
_BRC_BR = ("Landroid/content/BroadcastReceiver;", "Landroid/content/BroadcastReceiver$PendingResult;")
_BRC_CTX = ("Landroid/content/Context;", "Landroid/content/ContextWrapper;", "Landroid/app/Application;",
            "Landroid/app/Activity;", "Landroid/app/Service;")
_BRC_STR = {"startsWith": str.startswith, "endsWith": str.endswith, "contains": lambda x, y: y in x}
_BRC_BUDGET_S, _BRC_MAX_RECV, _BRC_MAX_ACT, _BRC_MAX_RUNS = 0.8, 24, 12, 48


class _BrcVM(_BndVM):
    """_BndVM for one delivered broadcast: the Intent / Bundle / Context / SharedPreferences / BroadcastReceiver result
    API modelled; extra reads go through read() so equality wants answer them."""

    def __init__(self, dx, deadline, answers, action, prev=None, pkg=None):
        super().__init__(dx, deadline, answers)
        self.action, self.prev, self.pkg, self.result = action, prev, pkg, prev

    def keep(self, v):
        if isinstance(v, _DxObj) and v.t == "Landroid/content/Intent;":
            for x in v.f.get("$m", {}).values():
                self.keep(x)
            return
        super().keep(v)

    def invoke(self, ref, raw, depth):  # noqa: C901 - one framework model
        ct, rest = ref.split("->", 1)
        name = rest[:rest.index("(")]
        o = raw[0] if raw else None
        a = raw[1:]
        own = ref not in self.dx.code and ref not in _DXE_INTR
        if isinstance(o, _DxObj) and o.t == "Landroid/content/Intent;":
            if o.f.get("$in"):
                if name == "getAction":
                    return self.action
                if name in ("getStringExtra", "getCharSequenceExtra", "getDataString"):
                    return self.read("S")
                if name in ("getIntExtra", "getBooleanExtra", "getShortExtra", "getByteExtra", "getCharExtra"):
                    return self.read("I", a[1] if len(a) > 1 and isinstance(a[1], int) and a[1] not in (0, -1) else None)
                if name == "getLongExtra":
                    return self.read("I")
                if name == "hasExtra":
                    return 1
                if name == "getExtras":
                    b = o.f.get("$b")
                    if b is None:
                        b = o.f["$b"] = _DxObj("Landroid/os/Bundle;")
                    return b
                if name in ("getPackage", "getType", "getScheme"):
                    return None
                raise _DxAbort
            m = o.f.setdefault("$m", {})
            if name == "<init>":
                if a and isinstance(a[0], str):
                    o.f["act"] = a[0]
                return None
            if name in ("putExtra", "putExtras") and a:
                if name == "putExtra" and len(a) >= 2:
                    m[a[0]] = a[1]
                elif isinstance(a[0], _DxObj):
                    m.update(a[0].f.get("$m", {}))
                return o
            if name == "setAction" and a:
                o.f["act"] = a[0]
                return o
            if name in ("setPackage", "setClass", "setClassName", "setComponent", "addFlags", "setFlags", "setData"):
                return o
            if name in ("getStringExtra", "getIntExtra") and a:
                return m.get(a[0], a[1] if len(a) > 1 else None)
            if name == "getAction":
                return o.f.get("act")
            raise _DxAbort
        if ct in ("Landroid/content/SharedPreferences;", "Landroid/content/SharedPreferences$Editor;"):
            if name == "edit":
                return _DxObj("Landroid/content/SharedPreferences$Editor;")
            if name.startswith("put") and len(a) >= 2:
                self.keep(a[1])
                return o
            if name in ("apply", "remove", "clear"):
                return None if name == "apply" else o
            if name == "commit":
                return 1
            if name.startswith("get") and len(a) >= 2:
                return a[1]
            raise _DxAbort
        if ct == "Landroid/util/Log;":
            for v in a:
                self.keep(v)
            return 0
        if ct == "Ljava/lang/String;" and isinstance(o, str) and ref not in _DXE_INTR and a and isinstance(a[0], str):
            if name in _BRC_STR:
                return int(_BRC_STR[name](o, a[0]))
        if ct == "Landroid/widget/Toast;":
            if name == "makeText":
                if len(a) > 1:
                    self.keep(a[1])
                return _DxObj(ct)
            return None
        if own and name in ("sendBroadcast", "sendOrderedBroadcast", "sendStickyBroadcast", "startService",
                            "startActivity", "startForegroundService") and a and isinstance(a[0], _DxObj):
            self.keep(a[0])
            return None
        if own and name == "getSharedPreferences":
            return _DxObj("Landroid/content/SharedPreferences;")
        if own and name in ("getApplicationContext", "getBaseContext"):
            return _DxObj("Landroid/content/Context;")
        if own and name == "getPackageName" and self.pkg:
            return self.pkg
        if own and (ct.startswith(_BRC_BR) or ct in _BRC_CTX or _dxx_supers(self.dx).get(ct)):
            if name in ("setResultData", "setResult", "setResultExtras"):
                for v in a:
                    if v is not None and not isinstance(v, int):
                        self.keep(v)
                vs = [v for v in a if isinstance(v, (str, _DxSB))]
                if vs:
                    self.result = _dxe_str(vs[0]) if isinstance(vs[0], _DxSB) else str(vs[0])
                return None
            if name == "getResultData":
                return self.read("S", self.prev) if self.prev else self.read("S")
            if name == "getResultExtras":
                return _DxObj("Landroid/os/Bundle;")
            if name in ("getResultCode", "isOrderedBroadcast", "isInitialStickyBroadcast"):
                return -1 if name == "getResultCode" else int(name == "isOrderedBroadcast")
            if name == "goAsync":
                return _DxObj("Landroid/content/BroadcastReceiver$PendingResult;")
            if name in ("setResultCode", "abortBroadcast", "clearAbortBroadcast", "finish", "<init>", "onReceive",
                        "setOrderedHint", "unregisterReceiver", "registerReceiver"):
                return None
        return super().invoke(ref, raw, depth)


def _brc_manifest(z):
    """({receiver class descriptor: {"actions", "exported", "permission", "priority"}}, package) of the manifest."""
    out, pkg = {}, None
    try:
        b = z.read("AndroidManifest.xml")
        ev = _axml_events(b) if b[:2] == b"\x03\x00" else _xml_events(b)
        cur, prio = None, 0
        for kind, tag, attrs, _ in ev:
            if kind == "start" and tag == "manifest":
                pkg = attrs.get("package")
            elif kind == "start" and tag == "receiver":
                n = attrs.get("name") or ""
                n = (pkg or "") + n if n.startswith(".") else n if "." in n else f"{pkg}.{n}"
                cur = out.setdefault("L" + n.replace(".", "/") + ";", {
                    "actions": [], "exported": attrs.get("exported"), "permission": attrs.get("permission"),
                    "priority": 0})
            elif kind == "end" and tag == "receiver":
                cur = None
            elif kind == "start" and tag == "intent-filter" and cur is not None:
                try:
                    prio = int(attrs.get("priority") or 0)
                except ValueError:
                    prio = 0
                prio = prio - (1 << 32) if prio >= 1 << 31 else prio
                cur["priority"] = max(cur["priority"], prio)
                if cur["exported"] is None:
                    cur["exported"] = "true"
            elif kind == "start" and tag == "action" and cur is not None and attrs.get("name"):
                cur["actions"].append(attrs["name"])
    except Exception:  # noqa: BLE001 - no / unreadable manifest: dex-side actions only
        pass
    return out, pkg


def _brc_dyn_actions(dx, budget=400):
    """Action strings handed to IntentFilter(String) / addAction anywhere in the dex (dynamic registerReceiver)."""
    acts = []
    for ref in dx.order[:budget]:
        ins = dx.code[ref][2]
        last = None
        for op, o in _dga_ops(ins):
            if op in (0x1A, 0x1B):
                last = dx.s(struct.unpack_from("<H" if op == 0x1A else "<I", ins, o + 2)[0])
            elif 0x6E <= op <= 0x72 or 0x74 <= op <= 0x78:
                try:
                    r = dx.mref(struct.unpack_from("<H", ins, o + 2)[0])
                except Exception:  # noqa: BLE001
                    continue
                if isinstance(r, str) and r.startswith(_BRC_IF) and isinstance(last, str):
                    acts.append(last)
    return list(dict.fromkeys(acts))


def broadcast_receiver_facts(apk):
    """[{"class", "action", "exported", "permission", "priority", "result", "values", "tokens"}] per (receiver, action)
    of every in-dex BroadcastReceiver.onReceive, run with a delivered Intent of that action whose extras answer the
    code's comparisons; receivers sharing an action chain getResultData in priority order. [] when absent; never
    raises; < 1 s."""
    rows = []
    deadline = time.time() + _BRC_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            man, pkg = _brc_manifest(z)
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or not _BRC_PRE.search(d) or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            entries = [r for r in dx.order if r.endswith(_BRC_ENTRY)][:_BRC_MAX_RECV]
            if not entries:
                continue
            dyn = _brc_dyn_actions(dx)
            plan = {}
            for ref in entries:
                ct = ref.split("->")[0]
                meta = man.get(ct, {})
                own = [s for s in _bnd_literals(dx, [ref])[1] if _BRC_ACT.fullmatch(s) and s.split(".")[-1].isupper()]
                acts = list(dict.fromkeys(meta.get("actions", []) + own + dyn))[:_BRC_MAX_ACT] or [None]
                for act in acts:
                    plan.setdefault(act, []).append((ref, ct, meta))
            runs = [_BRC_MAX_RUNS * 4]
            for act, recvs in plan.items():
                prev = None
                for ref, ct, meta in sorted(recvs, key=lambda t: -t[2].get("priority", 0)):
                    if time.time() > deadline or runs[0] <= 0:
                        break

                    tried = []

                    def run(dx_, ref_, recv, action, ans, dl, prev_=prev, tried_=tried):
                        vm = _BrcVM(dx_, dl, ans, action, prev_, pkg)
                        tried_.append((len(ans), vm))
                        it = _DxObj("Landroid/content/Intent;")
                        it.f["$in"] = True
                        try:
                            vm.init_class(recv.t)
                            vm.run(ref_, [recv, _DxObj("Landroid/content/Context;"), it])
                        except _FCF_CATCH:
                            pass
                        return vm

                    per = [min(runs[0], _BRC_MAX_RUNS)]
                    before = per[0]
                    vm = _bnd_solve(dx, ref, _DxObj(ct), act, deadline, per, run=run)
                    runs[0] -= before - per[0]
                    if vm is None:
                        continue
                    if not any(ANS_RE_T.search(t) for t in vm.out + vm.seen):
                        # no token: the run whose reads were answered most (the guarded path, not the bail-out)
                        vm = max(((n, v.steps, -k, v) for k, (n, v) in enumerate(tried) if v.out), default=(0, 0, 0, vm))[3]
                    prev = vm.result if vm.result is not None else prev
                    if not vm.out:
                        continue
                    toks = list(dict.fromkeys(m for s in vm.out + vm.seen for m in ANS_RE_T.findall(s)))
                    rows.append({"class": ct, "action": act, "exported": meta.get("exported"),
                                 "permission": meta.get("permission"), "priority": meta.get("priority", 0),
                                 "result": vm.result, "values": list(dict.fromkeys(vm.out))[:16], "tokens": toks})
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return rows


def broadcast_receiver_scan(apk):
    """ANS tokens a broadcast receiver emits per action (broadcast_receiver_facts), result-data tokens first.
    [] when absent; never raises; < 1 s."""
    rows = broadcast_receiver_facts(apk)
    rows.sort(key=lambda r: not (r["result"] and ANS_RE_T.search(r["result"])))
    return list(dict.fromkeys(t for r in rows for t in r["tokens"]))


# --- biometric / local-auth success callback holds the secret (coverage atlas row 92, MASVS-AUTH) --------------------
# Every in-dex onAuthenticationSucceeded(AuthenticationResult) of a BiometricPrompt / FingerprintManager(Compat)
# AuthenticationCallback subclass is run twice: with a result whose getCryptoObject() is null (the event-bound bypass a
# hook forces) and with a CryptoObject whose Cipher / Mac is an identity stub (doFinal / update return their input).
# onActivityResult of a class reaching KeyguardManager.createConfirmDeviceCredentialIntent runs with resultCode -1
# (RESULT_OK) per requestCode literal. Values only reached on onAuthenticationFailed / onAuthenticationError /
# a non-OK result are kept but demoted. Key-spec flags: setUserAuthenticationRequired(false), and a spec that never
# calls setInvalidatedByBiometricEnrollment (or calls it with false).
_BIO_CB = ("Landroidx/biometric/BiometricPrompt$AuthenticationCallback;",
           "Landroid/hardware/biometrics/BiometricPrompt$AuthenticationCallback;",
           "Landroid/hardware/fingerprint/FingerprintManager$AuthenticationCallback;",
           "Landroidx/core/hardware/fingerprint/FingerprintManagerCompat$AuthenticationCallback;",
           "Landroid/support/v4/hardware/fingerprint/FingerprintManagerCompat$AuthenticationCallback;")
_BIO_OK = re.compile(r"->onAuthenticationSucceeded\(L[\w/$]*AuthenticationResult;\)V$")
_BIO_BAD = ("->onAuthenticationFailed()V", "->onAuthenticationError(ILjava/lang/CharSequence;)V")
_BIO_KG = "->onActivityResult(IILandroid/content/Intent;)V"
_BIO_PRE = re.compile(rb"onAuthenticationSucceeded\0|createConfirmDeviceCredentialIntent\0")
_BIO_UAR = "Landroid/security/keystore/KeyGenParameterSpec$Builder;->setUserAuthenticationRequired(Z)"
_BIO_INV = "Landroid/security/keystore/KeyGenParameterSpec$Builder;->setInvalidatedByBiometricEnrollment(Z)"
_BIO_STUB = ("Ljavax/crypto/Cipher;", "Ljavax/crypto/Mac;")
_BIO_BUDGET_S, _BIO_MAX_ENTRY, _BIO_MAX_RQ, _BIO_MAX_RUNS = 0.8, 16, 6, 32


class _BioVM(_BrcVM):
    """_BrcVM for one auth callback: AuthenticationResult.getCryptoObject() -> `crypto` (None or a CryptoObject whose
    Cipher / Mac doFinal / update are the identity), KeyguardManager / Activity / TextView modelled, super callbacks
    no-ops."""

    def __init__(self, dx, deadline, answers, crypto):
        super().__init__(dx, deadline, answers, None)
        self.crypto = crypto

    def invoke(self, ref, raw, depth):  # noqa: C901 - one framework model
        ct, rest = ref.split("->", 1)
        name = rest[:rest.index("(")]
        o = raw[0] if raw else None
        a = raw[1:]
        own = ref not in self.dx.code and ref not in _DXE_INTR
        if not own:
            return super().invoke(ref, raw, depth)
        if ct.endswith("$AuthenticationResult;"):
            if name == "getCryptoObject":
                return self.crypto
            if name == "getAuthenticationType":
                return 2
            raise _DxAbort
        if ct.endswith("$CryptoObject;"):
            if name == "getCipher":
                return _DxObj(_BIO_STUB[0]) if self.crypto is not None else None
            if name == "getMac":
                return _DxObj(_BIO_STUB[1]) if self.crypto is not None else None
            if name in ("getSignature", "getIdentityCredential", "getPresentationSession", "getOperationHandle"):
                return None if name != "getOperationHandle" else 0
            if name == "<init>":
                return None
            raise _DxAbort
        if ct in _BIO_STUB and isinstance(o, _DxObj):
            if name in ("doFinal", "update"):
                if not a:
                    return _DxArr([])
                v = a[0]
                if not isinstance(v, list):
                    raise _DxAbort
                if len(a) >= 3 and isinstance(a[1], int) and isinstance(a[2], int):
                    v = v[a[1]:a[1] + a[2]]
                c = _DxArr(v)
                c.t = getattr(v, "t", "B")
                return c
            if name in ("init", "updateAAD"):
                return None
            if name in ("getIV", "getBlockSize", "getMacLength"):
                return _DxArr([0] * 16) if name == "getIV" else 16
            raise _DxAbort
        if name.startswith("onAuthentication") or name in ("onActivityResult", "onCreate", "startActivityForResult",
                                                            "authenticate", "cancel", "finish", "setResult"):
            return None
        if ct == "Landroid/app/KeyguardManager;":
            if name == "createConfirmDeviceCredentialIntent":
                return _DxObj("Landroid/content/Intent;")
            if name in ("isKeyguardSecure", "isDeviceSecure", "isKeyguardLocked", "isDeviceLocked"):
                return 1
            raise _DxAbort
        if name == "getSystemService":
            return _DxObj("Landroid/app/KeyguardManager;") if a and a[0] == "keyguard" else _DxObj("Ljava/lang/Object;")
        if name in ("findViewById", "requireViewById"):
            return _DxObj("Landroid/widget/TextView;")
        if name in ("setText", "append", "setTitle", "setSubtitle", "setMessage") and a:
            self.keep(a[0])
            return None
        if name in ("setVisibility", "setEnabled", "setTextColor"):
            return None
        return super().invoke(ref, raw, depth)


def _bio_kind(dx, ct):
    """The framework AuthenticationCallback `ct` extends (up to 4 in-dex levels), or None."""
    sup = _dxx_supers(dx)
    for _ in range(4):
        ct = sup.get(ct)
        if ct is None:
            return None
        if ct in _BIO_CB:
            return ("androidx." if ct.startswith("Landroidx/") else "") + ct.split("/")[-1].split("$")[0]
    return None


def _bio_flags(dx):
    """{"user_auth_required_false", "invalidated_by_enrollment": True / False / None (never called)} of the dex's
    KeyGenParameterSpec.Builder calls; the boolean is the const/4 last written to the argument register."""
    out = {"user_auth_required_false": False, "user_auth_required": False, "invalidated_by_enrollment": None}
    for ref in dx.order[:2000]:
        ins = dx.code[ref][2]
        regs = {}
        for op, o in _dga_ops(ins):
            b1 = ins[o + 1]
            if op == 0x12:
                regs[b1 & 0xF] = ((b1 >> 4) ^ 8) - 8
            elif op in (0x6E, 0x74):
                try:
                    r = dx.mref(struct.unpack_from("<H", ins, o + 2)[0])
                except Exception:  # noqa: BLE001
                    continue
                if not isinstance(r, str) or not r.startswith((_BIO_UAR, _BIO_INV)):
                    continue
                g = struct.unpack_from("<H", ins, o + 4)[0]
                arg = regs.get((g >> 4) & 0xF) if op == 0x6E else regs.get(g + 1)
                if r.startswith(_BIO_UAR):
                    out["user_auth_required"] = True
                    out["user_auth_required_false"] |= arg == 0
                else:
                    out["invalidated_by_enrollment"] = (out["invalidated_by_enrollment"] is not False) and arg != 0
            elif op not in (0x0E, 0x0F, 0x10, 0x11) and 0x01 <= op <= 0xE2 and op not in range(0x32, 0x3E):
                regs.pop(b1 & 0xF, None)
                regs.pop(b1, None)
    out["invalidated_missing"] = out["user_auth_required"] and not out["invalidated_by_enrollment"]
    return out


def biometric_auth_facts(apk):
    """{"rows": [{"class", "kind", "entry", "mode", "primary", "values", "tokens"}], "flags": {...}} -- every in-dex
    BiometricPrompt / FingerprintManager(Compat) AuthenticationCallback run per mode: "crypto_null" (getCryptoObject()
    null: event-bound bypass) / "crypto_stub" (CryptoObject over an identity Cipher / Mac) on onAuthenticationSucceeded,
    "failed" / "error" (primary False) on the failure callbacks; onActivityResult of a createConfirmDeviceCredentialIntent
    caller run as "result_ok" (resultCode -1, per requestCode literal) and "result_canceled" (primary False). flags:
    _bio_flags of the dex (setUserAuthenticationRequired(false), setInvalidatedByBiometricEnrollment missing / false).
    {"rows": [], "flags": {}} when absent; never raises; < 1 s."""
    rows, flags = [], {}
    deadline = time.time() + _BIO_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline:
                continue
            if not _BIO_PRE.search(d) and b"setUserAuthenticationRequired\0" not in d:
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            if b"setUserAuthenticationRequired\0" in d or b"setInvalidatedByBiometricEnrollment\0" in d:
                for k, v in _bio_flags(dx).items():
                    flags[k] = flags.get(k) or v
            if not _BIO_PRE.search(d):
                continue
            kg = b"createConfirmDeviceCredentialIntent\0" in d
            plan = []
            for ref in dx.order:
                ct = ref.split("->")[0]
                if _DXE_LIB.match(ct):
                    continue
                if _BIO_OK.search(ref):
                    kind = _bio_kind(dx, ct) or "callback"
                    plan += [(ref, ct, kind, "crypto_null", None), (ref, ct, kind, "crypto_stub", None)]
                elif ref.endswith(_BIO_BAD) and _bio_kind(dx, ct):
                    plan.append((ref, ct, _bio_kind(dx, ct), "failed" if "Failed" in ref else "error", None))
                elif kg and ref.endswith(_BIO_KG):
                    rqs = (_bnd_literals(dx, [ref])[0] + [0])[:_BIO_MAX_RQ]
                    plan += [(ref, ct, "keyguard", m, rq) for m in ("result_ok", "result_canceled") for rq in rqs]
            runs = [_BIO_MAX_RUNS * 4]
            for ref, ct, kind, mode, rq in plan[:_BIO_MAX_ENTRY * 4]:
                if time.time() > deadline or runs[0] <= 0:
                    break

                def run(dx_, ref_, recv, mode_, ans, dl, rq_=rq):
                    crypto = _DxObj("Landroidx/biometric/BiometricPrompt$CryptoObject;") if mode_ == "crypto_stub" else None
                    vm = _BioVM(dx_, dl, ans, crypto)
                    ps = _dxe_params(ref_)
                    if mode_.startswith("crypto"):
                        args = [_DxObj("L" + ps[0][1:-1] + ";" if ps else "LAuthenticationResult;")]
                    elif mode_ == "error":
                        args = [7, "Too many attempts. Try again later."]
                    elif mode_.startswith("result"):
                        it = _DxObj("Landroid/content/Intent;")
                        it.f["$in"] = True
                        args = [rq_, -1 if mode_ == "result_ok" else 0, it]
                    else:
                        args = []
                    try:
                        vm.init_class(recv.t)
                        vm.run(ref_, [recv] + args)
                    except _FCF_CATCH:
                        pass
                    return vm

                per = [min(runs[0], _BIO_MAX_RUNS)]
                before = per[0]
                vm = _bnd_solve(dx, ref, _DxObj(ct), mode, deadline, per, run=run)
                runs[0] -= before - per[0]
                if vm is None or not (vm.out or vm.seen):
                    continue
                toks = list(dict.fromkeys(m for s in vm.out + vm.seen for m in ANS_RE_T.findall(s)))
                rows.append({"class": ct, "kind": kind, "entry": ref.split("->")[1].split("(")[0], "mode": mode,
                             "request_code": rq, "primary": mode in ("crypto_null", "crypto_stub", "result_ok"),
                             "values": list(dict.fromkeys(vm.out))[:16], "tokens": toks})
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return {"rows": rows, "flags": flags}


def biometric_auth_scan(apk):
    """ANS tokens an auth success callback yields (biometric_auth_facts): null-CryptoObject and identity-CryptoObject
    success runs and RESULT_OK onActivityResult first, failure / error / cancelled-only tokens demoted behind them.
    [] when absent; never raises; < 1 s."""
    rows = biometric_auth_facts(apk)["rows"]
    good = [t for r in rows if r["primary"] for t in r["tokens"]]
    bad = [t for r in rows if not r["primary"] for t in r["tokens"]]
    return list(dict.fromkeys(good + [t for t in bad if t not in good]))


# --- decrypt helper evaluated with each call site's constant arguments (coverage atlas rows 35, 70) --------------------
_DCS_NAME = re.compile(r"decr|deobf|decod|unmask|unxor|xor|reveal|unscr", re.I)
_DCS_XOR = frozenset((0x97, 0xA2, 0xB7, 0xC2, 0xDF, 0xD7))
_DCS_RET = (")Ljava/lang/String;", ")[B", ")[C")
_DCS_BUDGET_S, _DCS_MAX_FALLBACK = 0.8, 600


def _dcs_helpers(dx):
    """In-dex methods with params that look like string decrypters: String/[B/[C return, a decrypt-ish name, or a short
    (renamed) name with xor in the body."""
    out = {}
    for ref, (nreg, nin, ins, acc) in dx.code.items():
        ct, rest = ref.split("->", 1)
        name = rest[:rest.index("(")]
        ps = _dxe_params(ref)
        if _DXE_LIB.match(ct) or not ps or len(ps) > 4 or nin > nreg or name.startswith("<"):
            continue
        xor = not _DCS_XOR.isdisjoint(ins[0::2])
        if ref.endswith(_DCS_RET) or _DCS_NAME.search(name) or (len(name) <= 2 and xor):
            out[ref] = (ps, bool(acc & 0x8))
    return out


def _dcs_copy(v):
    if isinstance(v, _DxArr):
        c = _DxArr(v)
        c.t = getattr(v, "t", "B")
        return c
    return v


def _dcs_sites(dx, helpers, svm, deadline, partial=False):
    """Linear constant tracking over every app method: (helper ref, raw register args) for each call whose parameter
    registers hold constants (const / const-string / new-array + fill-array-data / aput / filled-new-array / sget of a
    <clinit>-initialised static / the result of a nested helper call). partial: also calls where only some int args
    are constant (the missing ones None)."""
    sites = []
    for ref, (nreg, nin, ins, acc) in dx.code.items():
        if time.time() > deadline:
            break
        if _DXE_LIB.match(ref.split("->")[0]):
            continue
        n_ins, pc, r, last = len(ins) // 2, 0, {}, None
        u16 = lambda p: struct.unpack_from("<H", ins, p)[0]  # noqa: E731
        while pc < n_ins:
            p = 2 * pc
            op, b1 = ins[p], ins[p + 1]
            A, B, w = b1 & 0xF, b1 >> 4, _DOP_W[op]
            if op == 0x00 and b1:  # payload pseudo-instruction: skip it whole
                if b1 == 1:
                    w = 4 + 2 * u16(p + 2)
                elif b1 == 2:
                    w = 2 + 4 * u16(p + 2)
                elif b1 == 3:
                    w = 4 + (u16(p + 2) * struct.unpack_from("<I", ins, p + 4)[0] + 1) // 2
            nl = None
            if op in (0x01, 0x04, 0x07):
                r[A] = r.get(B)
            elif op in (0x02, 0x05, 0x08):
                r[b1] = r.get(u16(p + 2))
            elif op in (0x03, 0x06, 0x09):
                r[u16(p + 2)] = r.get(u16(p + 4))
            elif op in (0x0A, 0x0B, 0x0C):
                r[b1] = last
            elif op == 0x12:
                r[A] = (B ^ 8) - 8
            elif op in (0x13, 0x16):
                r[b1] = struct.unpack_from("<h", ins, p + 2)[0]
            elif op in (0x14, 0x17):
                r[b1] = struct.unpack_from("<i", ins, p + 2)[0]
            elif op == 0x15:
                r[b1] = _dxe_w32(u16(p + 2) << 16)
            elif op == 0x18:
                r[b1] = struct.unpack_from("<q", ins, p + 2)[0]
            elif op == 0x19:
                r[b1] = _dxe_w64(struct.unpack_from("<h", ins, p + 2)[0] << 48)
            elif op == 0x1A:
                r[b1] = dx.s(u16(p + 2))
            elif op == 0x1B:
                r[b1] = dx.s(struct.unpack_from("<I", ins, p + 2)[0])
            elif op == 0x23:
                n, t = r.get(B), dx.typ(u16(p + 2))
                if isinstance(n, int) and 0 <= n <= _DXE_MAX_ARR and len(t) == 2:
                    a_ = _DxArr([0] * n)
                    a_.t = t[1:]
                    r[A] = a_
                else:
                    r[A] = None
            elif op in (0x24, 0x25):
                cnt = B if op == 0x24 else b1
                g = u16(p + 4)
                regs = [g & 0xF, (g >> 4) & 0xF, (g >> 8) & 0xF, g >> 12, A][:cnt] if op == 0x24 else range(g, g + cnt)
                vals = [r.get(x) for x in regs]
                if all(isinstance(v, (int, str)) for v in vals):
                    nl = _DxArr(vals)
                    nl.t = dx.typ(u16(p + 2))[1:]
            elif op == 0x26:
                q = 2 * (pc + struct.unpack_from("<i", ins, p + 2)[0])
                a_ = r.get(b1)
                if isinstance(a_, _DxArr) and 0 <= q and ins[q:q + 2] == b"\x00\x03":
                    ew, n = struct.unpack_from("<HI", ins, q + 2)
                    if ew in (1, 2, 4, 8) and n <= len(a_) and q + 8 + ew * n <= len(ins):
                        sg = a_.t != "C"
                        for k in range(n):
                            a_[k] = int.from_bytes(ins[q + 8 + ew * k:q + 8 + ew * (k + 1)], "little", signed=sg)
            elif 0x44 <= op <= 0x4A:
                a_, ix = r.get(ins[p + 2]), r.get(ins[p + 3])
                r[b1] = a_[ix] if isinstance(a_, list) and isinstance(ix, int) and 0 <= ix < len(a_) else None
            elif 0x4B <= op <= 0x51:
                a_, ix, v = r.get(ins[p + 2]), r.get(ins[p + 3]), r.get(b1)
                if isinstance(a_, list) and isinstance(ix, int) and 0 <= ix < len(a_):
                    a_[ix] = v
            elif 0x60 <= op <= 0x66:
                ct, fk, _ = dx.fref(u16(p + 2))
                if fk not in svm.statics and ct in dx.sfields:
                    svm.init_class(ct)
                r[b1] = svm.statics.get(fk, _DXE_SFIELDS.get(fk))
            elif 0x6E <= op <= 0x78 and op != 0x73:
                ref2 = dx.mref(u16(p + 2))
                if op <= 0x72:
                    g = u16(p + 4)
                    regs = [g & 0xF, (g >> 4) & 0xF, (g >> 8) & 0xF, g >> 12, A][:B]
                else:
                    regs = range(u16(p + 4), u16(p + 4) + b1)
                h = helpers.get(ref2)
                if h is not None:
                    raw = [r.get(x) for x in regs]
                    ps, static = h
                    if not static and raw:
                        raw[0] = _DxObj(ref2.split("->")[0])
                    i, ok = (0 if static else 1), True
                    for pt in ps:
                        v = raw[i] if i < len(raw) else None
                        ok = ok and (isinstance(v, int) if pt in "ZBSCIJ" else v is not None)
                        i += 2 if pt in "JD" else 1
                    if ok or (partial and any(isinstance(v, int) for v in raw)):
                        nl = (ref2, raw)
                        sites.append(nl)
            elif op not in (0x0E, 0x0F, 0x10, 0x11, 0x1D, 0x1E, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C) \
                    and not 0x32 <= op <= 0x3D and not 0x67 <= op <= 0x6D and not 0x59 <= op <= 0x5F:
                # any other op writes vA (4-bit form) or vAA: forget both readings of the destination
                r.pop(A, None)
                r.pop(b1, None)
                r.pop(b1 + 1, None)
            last = nl
            pc += max(w, 1)
    return sites


def decrypt_call_candidates(apk):
    """Decrypted strings of every in-dex decrypt helper (String/[B/[C return, decrypt/deobf/decode/xor name, or a
    renamed 1-2 letter method with xor in its body) run by the dex_eval_scan interpreter with the CONSTANT arguments of
    each of its call sites (`a("<cipher>", 0x4d)`, `decode(new byte[]{..}, Codec.K)`, nested helper(helper(..)) calls),
    then -- as a fallback -- run over every const-string / array literal of the dex (other params from the call
    sites, else 0). Returns the decoded strings (ANS-bearing first); [] when absent; never raises; < 1 s."""
    out = []
    deadline = time.time() + _DCS_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
                helpers = _dcs_helpers(dx)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            if not helpers:
                continue
            svm = _DxVM(dx, deadline)
            sites = _dcs_sites(dx, helpers, svm, deadline - _DCS_BUDGET_S / 3)

            def call(ref, raw, src=None):
                vm = _DxVM(dx, deadline)
                vm.statics, vm.inited = dict(svm.statics), set(svm.inited)
                res = None
                try:
                    res = vm.invoke(ref, [_dcs_copy(v) for v in raw], 0)
                except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError,
                        RecursionError, struct.error):
                    pass
                vals = vm.seen + ([res] if res is not None else [])
                for v in vals:
                    if isinstance(v, list) and v and all(isinstance(x, int) for x in v):
                        v = (_dxe_bytes(v).decode("utf-8", "replace") if getattr(v, "t", "B") in "BZ"
                             else "".join(chr(x & 0xFFFF) for x in v))
                    if isinstance(v, str) and v and (src is None or src not in v):  # fallback: echoed input = no decrypt
                        out.append(v)
                return res

            done = {}
            for site in sites:  # nested helper(helper(..)) args resolve from earlier sites, in call order
                if time.time() > deadline:
                    break
                ref, raw = site
                raw = [done.get(id(v), v) if isinstance(v, tuple) else v for v in raw]
                if any(isinstance(v, tuple) or v is None for v in raw[1:]) and any(isinstance(v, tuple) for v in site[1]):
                    continue
                done[id(site)] = call(ref, raw)
            if any(ANS_RE_T.search(s) for s in out):
                continue
            # fallback: every helper over every const-string / array literal of the dex
            ints = {}
            for ref, raw in sites:
                ints.setdefault(ref, raw)
            lits = [dx.s(i) for i in range(min(dx.n_str, 20000))]
            lits = [s for s in lits if s and 8 <= len(s) <= 512 and not re.fullmatch(r"\[*L[\w/$]+;|[\w$<>]+", s)]
            lits = lits[:_DCS_MAX_FALLBACK]
            for ref, (ps, static) in helpers.items():
                kinds = [k for k, pt in enumerate(ps) if pt in ("Ljava/lang/String;", "[B", "[C",
                                                                 "Ljava/lang/CharSequence;")]
                if not kinds or time.time() > deadline:
                    continue
                k0 = kinds[0]
                for s in lits:
                    if time.time() > deadline:
                        break
                    v = s if ps[k0] in ("Ljava/lang/String;", "Ljava/lang/CharSequence;") else (
                        _dxe_barr(s.encode("utf-8", "replace")) if ps[k0] == "[B" else _dxe_carr(s))
                    tmpl = ints.get(ref)
                    raw = [] if static else [_DxObj(ref.split("->")[0])]
                    for k, pt in enumerate(ps):
                        dflt = _dxe_default(pt)
                        if tmpl is not None:
                            j = (0 if static else 1) + sum(2 if q in "JD" else 1 for q in ps[:k])
                            if j < len(tmpl) and tmpl[j] is not None and not isinstance(tmpl[j], tuple):
                                dflt = tmpl[j]
                        raw += [v if k == k0 else dflt] + ([None] if pt in "JD" else [])
                    if any(x is _DXE_UNK for x in raw):
                        continue
                    call(ref, raw, s)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    out = list(dict.fromkeys(out))
    return sorted(out, key=lambda s: not ANS_RE_T.search(s))


def decrypt_call_scan(apk):
    """ANS tokens among decrypt_call_candidates(apk) (plus one decode_any layer on base64-ish results). [] when
    absent; never raises."""
    hits = []
    for s in decrypt_call_candidates(apk):
        hits += ANS_RE_T.findall(s)
        if not hits and re.fullmatch(r"[A-Za-z0-9+/=_-]{24,}", s):
            hits += ANS_RE_T.findall(decode_any(s.encode(), depth=1, cap=40, chain=False) or "")
    return list(dict.fromkeys(hits))

# --- known open-source string obfuscators, decoded statically by signature (coverage atlas row 71) --------------------
# StringFog (com/github/megatronking/stringfog): call sites `StringFog.decrypt("<b64>", "<key>")` (v1-3: xor of
#   base64(data) with the key's UTF-8 bytes; the Base64 / AES impls take the same pair) or `decrypt(byte[] data,
#   byte[] key)` (v4+: fill-array-data pair, plain xor).
# obfuscapk EncryptStrings: `DecryptString.decryptString("<hex>")`, AES-ECB/PKCS5 under a const key in the dex (the
#   32-char secret as raw bytes -> AES-256, or 32 hex -> AES-128).
# Allatori-style: a (String)String helper (ALLATORIxDEMO or renamed) xor'ing chars with 1-2 literals, alternating from
#   the END of the string. Paranoid's getString(long) keystream is not modelled.
_SOB_BUDGET_S, _SOB_MAX_DEX, _SOB_MAX_SITES, _SOB_MAX_KEYS = 0.8, 32 << 20, 2000, 64
_SOB_SIGS = {"(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;": "ss", "([B[B)Ljava/lang/String;": "bb",
             "(Ljava/lang/String;)Ljava/lang/String;": "s"}


def _sob_text(b):
    try:
        t = b.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        return None
    return t if t and t.isprintable() else None


def _sob_unpad(b):
    n = b[-1] if b else 0
    return b[:-n] if 0 < n <= 16 and b.endswith(bytes([n]) * n) else None


def _sob_xor(d, k):
    return bytes(c ^ k[i % len(k)] for i, c in enumerate(d)) if k else None


def _sob_sites(dx, deadline):
    """[(callee ref, [arg values])] for every invoke of a String-decrypt-shaped method with constant args (const-string
    -> str, new-array + fill-array-data -> bytes), plus {callee ref: [int literals of its own code]}."""
    sites, lits = [], {}
    for me, (nreg, nin, ins, acc) in dx.code.items():
        if time.time() > deadline or len(sites) > _SOB_MAX_SITES:
            break
        n_ins, reg, pc, own = len(ins) // 2, {}, 0, []
        while pc < n_ins:
            p = 2 * pc
            op, b1 = ins[p], ins[p + 1]
            if op == 0 and b1 in (1, 2, 3):
                if b1 == 1:
                    pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
                elif b1 == 2:
                    pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
                else:
                    w, n = struct.unpack_from("<HI", ins, p + 2)
                    pc += 4 + (w * n + 1) // 2
                continue
            w = _DOP_W[op]
            if p + 2 * w > len(ins):
                break
            if op in (0x1A, 0x1B):
                reg[b1] = dx.s(struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0])
            elif op == 0x12:
                v = b1 >> 4
                reg[b1 & 0xF] = v - 16 if v > 7 else v
                own.append(reg[b1 & 0xF])
            elif op in (0x13, 0x14):
                reg[b1] = struct.unpack_from("<h" if op == 0x13 else "<i", ins, p + 2)[0]
                own.append(reg[b1])
            elif op == 0xD7 or 0xD0 <= op <= 0xE2:  # binop/lit16, binop/lit8: keep the literal
                own.append(struct.unpack_from("<h", ins, p + 2)[0] if op <= 0xD7 else struct.unpack_from("<b", ins, p + 3)[0])
                reg.pop(b1 & 0xF if op <= 0xD7 else b1, None)
            elif op == 0x26:  # fill-array-data vAA, payload
                off = 2 * (pc + struct.unpack_from("<i", ins, p + 2)[0])
                if 0 <= off and off + 8 <= len(ins) and ins[off:off + 2] == b"\x00\x03":
                    ew, n = struct.unpack_from("<HI", ins, off + 2)
                    if ew == 1 and off + 8 + n <= len(ins):
                        reg[b1] = bytes(ins[off + 8:off + 8 + n])
            elif op in (0x6E, 0x6F, 0x70, 0x71, 0x72, 0x74, 0x75, 0x76, 0x77, 0x78):
                ref = dx.mref(struct.unpack_from("<H", ins, p + 2)[0])
                sig = ref[ref.index("("):]
                if sig in _SOB_SIGS:
                    if op < 0x74:
                        g = struct.unpack_from("<H", ins, p + 4)[0]
                        rs = [g & 0xF, g >> 4 & 0xF, g >> 8 & 0xF, g >> 12, b1 & 0xF][:b1 >> 4]
                    else:
                        f = struct.unpack_from("<H", ins, p + 4)[0]
                        rs = list(range(f, f + b1))
                    if op not in (0x71, 0x77):
                        rs = rs[1:]  # receiver
                    args = [reg.get(r) for r in rs]
                    if args and all(isinstance(a, (str, bytes)) for a in args):
                        sites.append((ref, args))
            elif op in (0x0C, 0x0A, 0x0B, 0x22, 0x23, 0x1F, 0x01, 0x07, 0x08) or 0x44 <= op <= 0x4A or 0x52 <= op <= 0x58 \
                    or 0x60 <= op <= 0x66 or 0x7B <= op <= 0xCF:
                reg.pop(b1 if op in (0x0C, 0x0A, 0x0B, 0x22, 0x08) or 0x44 <= op <= 0x4A or 0x60 <= op <= 0x66
                        or 0x90 <= op <= 0xAF else b1 & 0xF, None)
            pc += w
        lits[me] = own
    return sites, lits


def string_obfuscator_candidates(apk):
    """Strings decoded from the call sites of known open-source Android string obfuscators (StringFog xor / base64 /
    AES pairs, obfuscapk EncryptStrings AES-ECB hex, Allatori-style alternating char xor) found by their dex
    signatures; ANS-bearing ones first. [] when absent; never raises."""
    out = []
    deadline = time.time() + _SOB_BUDGET_S
    try:
        from Crypto.Cipher import AES
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _SOB_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            fog = re.search(rb"(?i)stringfog", d) is not None
            sites, lits = _sob_sites(dx, deadline)
            keys = None
            for ref, args in sites:
                if time.time() > deadline:
                    break
                cls, _, rest = ref.partition("->")
                name, kind = rest[:rest.index("(")], _SOB_SIGS[rest[rest.index("("):]]
                got = []
                if kind in ("ss", "bb") and (fog or re.search(r"(?i)fog|decrypt", ref)):
                    data, key = args
                    kb = key.encode("utf-8") if isinstance(key, str) else key
                    raws = [data] if isinstance(data, bytes) else []
                    if isinstance(data, str) and re.fullmatch(r"[A-Za-z0-9+/=_-]{4,}", data):
                        try:
                            raws.append(base64.b64decode(data + "=" * (-len(data) % 4), altchars=b"-_"
                                                         if re.search("[-_]", data) else None))
                        except (binascii.Error, ValueError):
                            pass
                    for raw in raws:
                        got += [_sob_xor(raw, kb), raw]
                        if len(kb) in (16, 24, 32) and raw and len(raw) % 16 == 0:
                            for c in (AES.new(kb, AES.MODE_ECB), AES.new(kb, AES.MODE_CBC, kb[:16]),
                                      AES.new(kb, AES.MODE_CBC, bytes(16))):
                                got.append(_sob_unpad(c.decrypt(raw)))
                elif kind == "s" and isinstance(args[0], str):
                    s = args[0]
                    if re.fullmatch(r"(?:[0-9A-Fa-f]{32})+", s) and (fog or "decryptstring" in ref.lower()
                                                                     or "decryptstring" in cls.lower()):
                        if keys is None:
                            ks = [dx.s(i) for i in range(min(dx.n_str, 50000))]
                            keys = [k.encode() for k in ks if len(k) in (16, 24, 32) and k.isprintable()]
                            keys += [bytes.fromhex(k) for k in ks if re.fullmatch(r"[0-9A-Fa-f]{32}|[0-9A-Fa-f]{64}", k)]
                            keys = list(dict.fromkeys(keys))[:_SOB_MAX_KEYS]
                        ct = bytes.fromhex(s)
                        for k in keys:
                            got.append(_sob_unpad(AES.new(k, AES.MODE_ECB).decrypt(ct)))
                    elif fog and re.fullmatch(r"[A-Za-z0-9+/=]{4,}", s):  # StringFog Base64 impl
                        try:
                            got.append(base64.b64decode(s + "=" * (-len(s) % 4)))
                        except (binascii.Error, ValueError):
                            pass
                    if ref in lits and (name.startswith("ALLATORI") or not _DXE_LIB.match(cls)):
                        ks = list(dict.fromkeys(v & 0xFFFF for v in lits[ref] if v and -0x8000 <= v <= 0xFFFF))[:12]
                        cs = [ord(c) for c in s]
                        for k1 in ks:
                            for k2 in ks:  # Allatori: last char ^ k1, the one before ^ k2, alternating from the end
                                t = "".join(chr((c ^ (k1 if (len(cs) - 1 - i) % 2 == 0 else k2)) & 0xFFFF)
                                            for i, c in enumerate(cs))
                                if t.isascii() and t.isprintable():
                                    out.append(t)
                for g in got:
                    t = _sob_text(g) if isinstance(g, bytes) else None
                    if t:
                        out.append(t)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    out = list(dict.fromkeys(out))
    return sorted(out, key=lambda s: not ANS_RE_T.search(s))


def string_obfuscator_scan(apk):
    """ANS tokens among string_obfuscator_candidates(apk). [] when absent; never raises."""
    return list(dict.fromkeys(m for s in string_obfuscator_candidates(apk) for m in ANS_RE_T.findall(s)))


# --- reflection with encoded names: Class.forName / getDeclaredField / getDeclaredMethod (coverage atlas row 43) -------
_RFL_PRE = re.compile(rb"getDeclaredField|getDeclaredMethod|getField\0|getMethod\0")
_RFL_TYPES = frozenset(("Ljava/lang/Class;", "Ljava/lang/reflect/Field;", "Ljava/lang/reflect/Method;",
                        "Ljava/lang/reflect/AccessibleObject;", "Ljava/lang/ClassLoader;"))
_RFL_BUDGET_S = 0.8
_RFL_NOOP = re.compile(r"Lkotlin/jvm/internal/Intrinsics;->check\w*\(|L[\w/]+;->setAccessible\(Z\)V$")


class _RflCls:
    __slots__ = ("t",)

    def __init__(self, t):
        self.t = t


class _RflMem:
    __slots__ = ("t", "name", "n")

    def __init__(self, t, name, n=None):
        self.t, self.name, self.n = t, name, n


def _rfl_desc(name):
    if not isinstance(name, str) or not 0 < len(name) < 256:
        raise _DxAbort
    return name if name.startswith("L") and name.endswith(";") else "L" + name.replace(".", "/") + ";"


class _RflVM(_DxVM):
    """_DxVM plus the java.lang.reflect calls an obfuscator emits: names are whatever the interpreter computed, resolved
    against this dex's classes / fields / methods. Values read through Field.get / returned by Method.invoke mark the
    start of the strings that count (`mark`), so decoy fields nobody reflects on are never reported."""

    def __init__(self, dx, deadline):
        super().__init__(dx, deadline)
        self.mark = None

    def const_class(self, t):
        return _RflCls(t)

    def _cls(self, v):
        if not isinstance(v, _RflCls) or v.t not in self.dx.sfields:
            raise _DxAbort
        return v.t

    def _pick(self):
        if self.mark is None:
            self.mark = len(self.seen)

    def invoke(self, ref, raw, depth):
        cls, _, rest = ref.partition("->")
        if _RFL_NOOP.match(ref):
            return None
        if ref == "Ljava/lang/StringBuilder;->reverse()Ljava/lang/StringBuilder;" and isinstance(raw[0], _DxSB):
            raw[0].s.reverse()
            return raw[0]
        if cls not in _RFL_TYPES and rest != "getClass()Ljava/lang/Class;":
            return super().invoke(ref, raw, depth)
        name = rest[:rest.index("(")]
        if name == "forName" and cls == "Ljava/lang/Class;":
            return _RflCls(_rfl_desc(raw[0]))
        if name == "loadClass" and len(raw) >= 2:
            return _RflCls(_rfl_desc(raw[1]))
        if name == "getClassLoader":
            return "Ljava/lang/ClassLoader;"
        if name == "getClass" and isinstance(raw[0], (_DxObj, _RflCls)):
            return _RflCls(raw[0].t if isinstance(raw[0], _DxObj) else "Ljava/lang/Class;")
        if name == "getName" and isinstance(raw[0], _RflCls):
            return raw[0].t[1:-1].replace("/", ".")
        if name in ("getDeclaredField", "getField"):
            ct, fn = self._cls(raw[0]), raw[1]
            if not isinstance(fn, str) or f"{ct}->{fn}" not in self._fields(ct):
                raise _DxAbort
            return _RflMem(ct, fn)
        if name in ("getDeclaredMethod", "getMethod"):
            ct, mn = self._cls(raw[0]), raw[1]
            n = len(raw[2]) if len(raw) > 2 and isinstance(raw[2], list) else None
            if not isinstance(mn, str) or not self._methods(ct, mn, n):
                raise _DxAbort
            return _RflMem(ct, mn, n)
        o = raw[0]
        if not isinstance(o, _RflMem):
            raise _DxAbort
        if cls == "Ljava/lang/reflect/Field;" and name.startswith("get") and len(raw) == 2:
            fk = f"{o.t}->{o.name}"
            self.init_class(o.t)
            if self._fields(o.t)[fk]:
                if fk not in self.statics:
                    raise _DxAbort
                v = self.statics[fk]
            elif isinstance(raw[1], _DxObj):
                v = raw[1].f.get(fk)
            else:
                raise _DxAbort
            self._pick()
            return self.note(v)
        if cls == "Ljava/lang/reflect/Method;" and name == "invoke" and len(raw) == 3:
            args = raw[2] if isinstance(raw[2], list) else []
            for mref in self._methods(o.t, o.name, len(args)):
                acc = self.dx.code[mref][3]
                call = [] if acc & 0x8 else [raw[1]]
                for p, a in zip(_dxe_params(mref), args):
                    call += [a] + ([None] if p in "JD" else [])
                if depth >= _DXE_DEPTH:
                    raise _DxAbort
                self._pick()
                self.init_class(o.t)
                return self.note(self.run(mref, call, depth + 1))
        raise _DxAbort

    def _fields(self, ct):
        """{field key: is_static} of class ct (static from class_data, instance fields from the field_id table)."""
        idx = getattr(self, "_fidx", None)
        if idx is None:
            idx = self._fidx = {}
            for fi in range(min(self.dx.n_fld, 1 << 18)):
                c, fk, _ = self.dx.fref(fi)
                idx.setdefault(c, {})[fk] = False
            for c, (sfl, _) in self.dx.sfields.items():
                for fi in sfl:
                    idx.setdefault(c, {})[self.dx.fref(fi)[1]] = True
        return idx.get(ct, {})

    def _methods(self, ct, mn, n):
        pre = f"{ct}->{mn}("
        return [m for m in self.dx.code if m.startswith(pre) and (n is None or len(_dxe_params(m)) == n)]


def _rfl_callers(dx):
    """App methods whose code invokes a reflection lookup (getDeclaredField/Method, getField/Method)."""
    want = set()
    for mi in range(dx.n_met):
        c, _, n = struct.unpack_from("<HHI", dx.d, dx.o_met + 8 * mi)
        if dx.typ(c) == "Ljava/lang/Class;" and dx.s(n) in ("getDeclaredField", "getDeclaredMethod", "getField",
                                                             "getMethod"):
            want.add(mi)
    out = []
    for ref in dx.order:
        ins = dx.code[ref][2]
        pc, n_ins = 0, len(ins) // 2
        while pc < n_ins:
            op, b1 = ins[2 * pc], ins[2 * pc + 1]
            if op == 0 and b1 in (1, 2, 3) and 2 * pc + 8 <= len(ins):
                ew, k = struct.unpack_from("<HI", ins, 2 * pc + 2)
                n = struct.unpack_from("<H", ins, 2 * pc + 2)[0]
                pc += (4 + 2 * n) if b1 == 1 else ((2 + 4 * n) if b1 == 2 else (4 + (ew * k + 1) // 2))
                continue
            if (0x6E <= op <= 0x72 or 0x74 <= op <= 0x78) and 2 * pc + 4 <= len(ins) \
                    and struct.unpack_from("<H", ins, 2 * pc + 2)[0] in want:
                out.append(ref)
                break
            pc += _DOP_W[op]
    return out


# --- a v2 chain whose mixers are reached by reflection (coverage atlas: analysis-chain-obfuscation-hardening) --------
# Class.forName(x("..Mix")).getDeclaredMethod(x("f1"), Long.TYPE).invoke(null, Long.valueOf(v)) -> ((Long) r).longValue():
# _dex_eval_deep runs the chain under _DxeDeepVM + _RflVM when the dex has a getDeclaredMethod / getMethod ref. Boxing is
# the identity in the evaluator (Long.valueOf / longValue / check-cast pass the int through); the Class[] of the lookup
# picks the exact overload (Long.TYPE -> J). Flattened / string-switch / opaque-predicate / tiny-VM chains need nothing
# extra: the deep VM runs them concretely (fixtures obfv2_*).
_DXE_PRIM_TYPES = {f"Ljava/lang/{b};->TYPE": p for b, p in (("Long", "J"), ("Integer", "I"), ("Short", "S"),
                   ("Byte", "B"), ("Character", "C"), ("Boolean", "Z"), ("Double", "D"), ("Float", "F"),
                   ("Void", "V"))}


class _DxeRflMethod(_RflMem):
    __slots__ = ("ps",)


class _DxeRflVM(_DxeDeepVM, _RflVM):
    def __init__(self, dx, deadline):
        super().__init__(dx, deadline)
        for k, p in _DXE_PRIM_TYPES.items():
            self.statics[k] = _RflCls(p)

    def invoke(self, ref, raw, depth):
        cls, _, rest = ref.partition("->")
        name = rest[:rest.find("(")]
        if cls == "Ljava/lang/Class;" and name in ("getDeclaredMethod", "getMethod") and len(raw) == 3 \
                and isinstance(raw[2], list) and all(isinstance(c, _RflCls) for c in raw[2]):
            ct, mn = self._cls(raw[0]), raw[1]
            ps = [c.t for c in raw[2]]
            if not isinstance(mn, str) or not [m for m in self._methods(ct, mn, len(ps)) if _dxe_params(m) == ps]:
                raise _DxAbort
            m = _DxeRflMethod(ct, mn, len(ps))
            m.ps = ps
            return m
        if cls == "Ljava/lang/reflect/Method;" and name == "invoke" and len(raw) == 3 \
                and isinstance(raw[0], _DxeRflMethod):
            o, args = raw[0], raw[2] if isinstance(raw[2], list) else []
            for mref in self._methods(o.t, o.name, len(args)):
                if _dxe_params(mref) != o.ps:
                    continue
                call = [] if self.dx.code[mref][3] & 0x8 else [raw[1]]
                for p, a in zip(o.ps, args):
                    call += [a] + ([None] if p in "JD" else [])
                if depth >= _DXE_DEPTH:
                    raise _DxAbort
                self.init_class(o.t)
                return self.note(self.invoke(mref, call, depth))
            raise _DxAbort
        return super().invoke(ref, raw, depth)


def _dxe_reflective(dx):
    """True when the dex references Class.getDeclaredMethod / getMethod (a reflected mixer chain)."""
    for mi in range(dx.n_met):
        c, _, n = struct.unpack_from("<HHI", dx.d, dx.o_met + 8 * mi)
        if dx.typ(c) == "Ljava/lang/Class;" and dx.s(n) in ("getDeclaredMethod", "getMethod"):
            return True
    return False


def reflection_scan(apk):
    """ANS tokens reached through reflection with encoded names: every app method that calls Class.getDeclaredField /
    getDeclaredMethod (or getField / getMethod) is run by the dex_eval_scan interpreter, with Class.forName /
    ClassLoader.loadClass / const-class / getClass resolving to this dex's classes, Field.get reading the class's static
    (static_values + <clinit>) or instance value and Method.invoke running the named method. The class / member names
    may be const-strings or computed (xor char arrays, Base64, StringBuilder.reverse, ...). Only strings produced from
    the first reflective read on are reported -- the fields nobody reflects on (decoys) are not. [] when absent; never
    raises; < 1 s."""
    hits = []
    deadline = time.time() + _RFL_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or not _RFL_PRE.search(d) or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
                callers = _rfl_callers(dx)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            for ref in callers:
                if time.time() > deadline:
                    break
                nreg, nin, ins, acc = dx.code[ref]
                ps = _dxe_params(ref)
                if len(ps) > 4 or nin > nreg:
                    continue
                vm = _RflVM(dx, deadline)
                raw = [] if acc & 0x8 else [_DxObj(ref.split("->")[0])]
                for p in ps:
                    raw += [_dxe_default(p)] + ([None] if p in "JD" else [])
                try:
                    vm.init_class(ref.split("->")[0])
                    vm.note(vm.run(ref, raw))
                except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError,
                        RecursionError, struct.error):
                    pass
                if vm.mark is None:
                    continue
                for s in vm.seen[vm.mark:]:
                    hits += ANS_RE_T.findall(s)
                    if not ANS_RE_T.search(s) and re.fullmatch(r"[A-Za-z0-9+/=_-]{24,}", s or ""):
                        hits += ANS_RE_T.findall(decode_any(s.encode(), depth=1, cap=40, chain=False) or "")
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- reflective dispatch table keyed by a runtime string (coverage atlas row 77) --------------------------------------
# key -> handler maps (HashMap.put(const, Class | Method | handler object | class-name string) in <clinit>/<init>),
# javac/D8 string switches (hashCode -> sparse-switch -> equals) and class-name arrays indexed by an int. Every key
# the table knows is run through the dispatcher; the key the app SUPPLIES (puzzle json route/key/entry/dispatch field,
# manifest deep-link path segment / pool string, const arg at the dispatcher's call site) picks the answer.
_DSP_MAPS = frozenset(("Ljava/util/HashMap;", "Ljava/util/LinkedHashMap;", "Ljava/util/TreeMap;", "Ljava/util/Hashtable;",
                       "Ljava/util/concurrent/ConcurrentHashMap;", "Landroid/util/ArrayMap;",
                       "Landroidx/collection/ArrayMap;"))
_DSP_MAP_IF = _DSP_MAPS | {"Ljava/util/Map;", "Ljava/util/AbstractMap;", "Ljava/util/SortedMap;", "Ljava/util/NavigableMap;"}
_DSP_PRE = re.compile(rb"Ljava/util/Map;|Ljava/util/(?:Linked)?HashMap;|hashCode\0|forName\0")
_DSP_FIELDS = frozenset(("route", "key", "entry", "dispatch", "handler", "action", "command", "cmd", "target", "path",
                         "screen", "mode", "op", "name", "id", "index", "slot"))
_DSP_BUDGET_S, _DSP_MAX_KEYS, _DSP_MAX_DISP = 0.9, 48, 24
_DSP_RET = (")Ljava/lang/String;", ")Ljava/lang/Object;", ")Ljava/lang/CharSequence;")


class _DspMap(dict):
    pass


class _DspVM(_RflVM):
    """_RflVM plus java.util maps, Class/Constructor.newInstance and virtual/interface dispatch on in-dex receivers
    (handler objects, D8 synthetic lambda classes)."""

    def new_instance(self, t):
        if t in _DSP_MAPS:
            return _DspMap()
        raise _DxAbort

    def invoke(self, ref, raw, depth):
        cls, _, rest = ref.partition("->")
        name = rest[:rest.index("(")]
        o = raw[0] if raw else None
        if isinstance(o, _DspMap) and cls in _DSP_MAP_IF:
            k = raw[1] if len(raw) > 1 else None
            if name == "<init>":
                return None
            if name in ("size", "isEmpty"):
                return len(o) if name == "size" else int(not o)
            if not isinstance(k, (str, int)) or isinstance(k, bool):
                raise _DxAbort
            if name in ("put", "putIfAbsent"):
                prev = o.get(k)
                if name == "put" or prev is None:
                    o[k] = raw[2]
                return prev
            if name in ("get", "remove"):
                return o.get(k) if name == "get" else o.pop(k, None)
            if name == "getOrDefault":
                return o.get(k, raw[2])
            if name == "containsKey":
                return int(k in o)
            raise _DxAbort
        if name == "<init>" and ref not in self.dx.code and ref not in _DXE_INTR and isinstance(o, _DxObj) \
                and o.t in self.dx.sfields:
            return None  # java.lang.Object / framework superclass constructor of an in-dex object
        if name in ("getDeclaredConstructor", "getConstructor") and isinstance(o, _RflCls):
            return o
        if name == "newInstance" and cls in ("Ljava/lang/Class;", "Ljava/lang/reflect/Constructor;"):
            t = self._cls(o)
            self.init_class(t)
            obj, ctor = _DxObj(t), f"{t}-><init>()V"
            if ctor in self.dx.code:
                if depth >= _DXE_DEPTH:
                    raise _DxAbort
                self.run(ctor, [obj], depth + 1)
            return obj
        if isinstance(o, _DxObj) and ref not in self.dx.code and ref not in _DXE_INTR:
            m = f"{o.t}->{rest}"
            if m in self.dx.code:
                if depth >= _DXE_DEPTH:
                    raise _DxAbort
                return self.note(self.run(m, raw, depth + 1))
        return super().invoke(ref, raw, depth)


def _dsp_walk(ins):
    """(pc, op, b1) over a code item's instructions, skipping switch / array payloads."""
    pc, n_ins = 0, len(ins) // 2
    while pc < n_ins:
        op, b1 = ins[2 * pc], ins[2 * pc + 1]
        if op == 0 and b1 in (1, 2, 3) and 2 * pc + 8 <= len(ins):
            n = struct.unpack_from("<H", ins, 2 * pc + 2)[0]
            ew, k = struct.unpack_from("<HI", ins, 2 * pc + 2)
            pc += (4 + 2 * n) if b1 == 1 else ((2 + 4 * n) if b1 == 2 else (4 + (ew * k + 1) // 2))
            continue
        yield pc, op, b1
        pc += _DOP_W[op]


def _dsp_dispatchers(dx):
    """{method ref: (key param type, const-strings in its body)} -- app methods taking one String / int key that look
    a handler up: Map.get/getOrDefault, String.hashCode (string switch) or Class.forName."""
    want = set()
    for mi in range(dx.n_met):
        r = dx.mref(mi)
        c, _, rest = r.partition("->")
        if (c in _DSP_MAP_IF and rest.startswith(("get(", "getOrDefault("))) or r in (
                "Ljava/lang/String;->hashCode()I",) or (c == "Ljava/lang/Class;" and rest.startswith("forName(")):
            want.add(mi)
    out = {}
    for ref in dx.order:
        ps = _dxe_params(ref)
        if len(ps) != 1 or ps[0] not in ("Ljava/lang/String;", "I") or not ref.endswith(_DSP_RET):
            continue
        ins, hit, consts = dx.code[ref][2], False, []
        for pc, op, b1 in _dsp_walk(ins):
            if (0x6E <= op <= 0x72 or 0x74 <= op <= 0x78) and 2 * pc + 4 <= len(ins):
                hit = hit or struct.unpack_from("<H", ins, 2 * pc + 2)[0] in want
            elif op == 0x1A and 2 * pc + 4 <= len(ins):
                consts.append(dx.s(struct.unpack_from("<H", ins, 2 * pc + 2)[0]))
            elif op == 0x1B and 2 * pc + 6 <= len(ins):
                consts.append(dx.s(struct.unpack_from("<I", ins, 2 * pc + 2)[0]))
        if hit:
            out[ref] = (ps[0], consts)
        if len(out) >= _DSP_MAX_DISP:
            break
    return out


def _dsp_call_args(dx, disp):
    """Const String / int arguments the app passes at each dispatcher call site, in code order."""
    out = []
    for ref in dx.order:
        ins, regs = dx.code[ref][2], {}
        for pc, op, b1 in _dsp_walk(ins):
            p = 2 * pc
            if op == 0x1A and p + 4 <= len(ins):
                regs[b1] = dx.s(struct.unpack_from("<H", ins, p + 2)[0])
            elif op == 0x12:
                regs[b1 & 0xF] = ((b1 >> 4) ^ 8) - 8
            elif op == 0x13 and p + 4 <= len(ins):
                regs[b1] = struct.unpack_from("<h", ins, p + 2)[0]
            elif (0x6E <= op <= 0x72 or 0x74 <= op <= 0x78) and p + 6 <= len(ins):
                callee = dx.mref(struct.unpack_from("<H", ins, p + 2)[0])
                if callee in disp:
                    g = struct.unpack_from("<H", ins, p + 4)[0]
                    rr = [g & 0xF, (g >> 4) & 0xF, (g >> 8) & 0xF, g >> 12, b1 & 0xF][:b1 >> 4] if op <= 0x72 \
                        else list(range(g, g + b1))
                    if rr and rr[-1] in regs:
                        out.append(regs[rr[-1]])
    return out


def _dsp_expand(v, out):
    if isinstance(v, bool) or v is None:
        return
    if isinstance(v, int):
        out.append(v)
        return
    if not isinstance(v, str) or not 0 < len(v) <= 200:
        return
    out.append(v)
    if v.lstrip("-").isdigit():
        out.append(int(v))
    if "/" in v or "?" in v:
        path, _, q = v.partition("?")
        segs = [x for x in path.split("/") if x and ":" not in x]
        out += segs[::-1]
        for kv in q.split("&"):
            out += [x for x in kv.split("=") if x]


def _dsp_supplied(z):
    """Keys the app supplies, best first: puzzle-json route/key/entry/dispatch fields, manifest path segments, other
    manifest pool strings (meta-data values, hosts)."""
    fields, man = [], []

    def walk(o, depth=0, hot=False):
        if depth > 6:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                h = hot or str(k).lower() in _DSP_FIELDS
                if isinstance(v, (dict, list)):
                    walk(v, depth + 1, h)
                elif h:
                    _dsp_expand(v, fields)
        elif isinstance(o, list):
            for v in o[:64]:
                walk(v, depth + 1, hot)

    for i in z.infolist():
        if i.filename.startswith("assets/") and i.filename.endswith(".json") and i.file_size <= 1 << 20:
            try:
                walk(json.loads(z.read(i).decode("utf-8", "replace")))
            except ValueError:
                pass
    try:
        pool = _pool_strings(z.read("AndroidManifest.xml"))
    except KeyError:
        pool = []
    for v in pool:
        if v.startswith("/") or "://" in v:
            _dsp_expand(v, man)
    for v in pool:
        _dsp_expand(v, man)
    return fields, [v for v in man if isinstance(v, str)]


def _dsp_run(dx, ref, key, deadline):
    """(completed, strings produced by the dispatcher for this key) -- the dispatcher's class/instance setup is not
    counted."""
    vm = _DspVM(dx, deadline)
    ct = ref.split("->")[0]
    acc = dx.code[ref][3]
    raw = []
    try:
        vm.init_class(ct)
        if not acc & 0x8:
            obj = _DxObj(ct)
            if f"{ct}-><init>()V" in dx.code:
                vm.run(f"{ct}-><init>()V", [obj], 1)
            raw = [obj]
        mark = len(vm.seen)
        vm.note(vm.run(ref, raw + [key]))
        ok = True
    except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError, RecursionError,
            struct.error):
        ok, mark = False, len(vm.seen)
    table = set()
    for v in list(vm.statics.values()) + (list(raw[0].f.values()) if raw else []):
        if isinstance(v, _DspMap):
            table |= {k for k in v if isinstance(k, str)}
    return ok, vm.seen[mark:], table


def _dsp_tokens(strs):
    out = []
    for s in strs:
        if not isinstance(s, str):
            continue
        out += ANS_RE_T.findall(s)
        if not ANS_RE_T.search(s) and re.fullmatch(r"[A-Za-z0-9+/=_-]{24,}", s):
            out += ANS_RE_T.findall(decode_any(s.encode(), depth=1, cap=40, chain=False) or "")
    return out


def dispatch_key_table(apk):
    """[{dispatcher, key, supplied (rank in the app's supplied keys or None), tokens}] for every key a reflective
    dispatch table knows. Never raises; < 1 s."""
    rows = []
    deadline = time.time() + _DSP_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
            fields, man = _dsp_supplied(z) if any(_DSP_PRE.search(d) for d in dexes) else ([], [])
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or not _DSP_PRE.search(d) or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
                disp = _dsp_dispatchers(dx)
                calls = _dsp_call_args(dx, disp) if disp else []
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            for ref, (pt, consts) in disp.items():
                if time.time() > deadline:
                    break
                ct = ref.split("->")[0]
                if pt == "I":  # int index: only the puzzle json / call-site constants, never manifest version ints
                    sup = list(dict.fromkeys(k for k in fields + calls if isinstance(k, int)))
                    keys = sup + list(range(16))
                else:
                    sup = list(dict.fromkeys(k for k in fields + man + calls if isinstance(k, str)))
                    table = _dsp_run(dx, ref, "", deadline)[2] | {c for c in consts if 0 < len(c) <= 64}
                    keys = [k for k in sup if k in table] + sorted(table)
                done = set()
                for k in keys:
                    if k in done or len(done) >= _DSP_MAX_KEYS or time.time() > deadline:
                        continue
                    done.add(k)
                    ok, strs, _ = _dsp_run(dx, ref, k, deadline)
                    if ok:
                        rows.append({"dispatcher": ref, "class": ct, "key": k,
                                     "supplied": sup.index(k) if k in sup else None,
                                     "tokens": list(dict.fromkeys(_dsp_tokens(strs)))})
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return rows


def dispatch_key_candidates(apk):
    """ANS tokens of a reflective dispatch table: the handler selected by the key the app supplies first, every other
    handler's tokens after it (demoted). [] when absent; never raises; < 1 s."""
    rows = dispatch_key_table(apk)
    rows.sort(key=lambda r: (r["supplied"] is None, r["supplied"] or 0))
    return list(dict.fromkeys(t for r in rows for t in r["tokens"]))


def dispatch_key_scan(apk):
    """ANS tokens of ONLY the dispatch-table handler the app's supplied key selects (puzzle json route/key/entry/dispatch
    field > manifest deep-link path segment / meta-data string > const arg at the call site). A selected handler that
    yields no valid token -> [] (its siblings are decoys); no supplied key resolves -> []. Never raises; < 1 s."""
    rows = [r for r in dispatch_key_table(apk) if r["supplied"] is not None]
    if not rows:
        return []
    best = min(r["supplied"] for r in rows)
    return list(dict.fromkeys(t for r in rows if r["supplied"] == best for t in r["tokens"]))


# --- dynamic dispatch without Class.forName: invoke-custom lambdas, MethodHandles, Proxy (coverage atlas row 80) -----
# dex 038+ call_site_ids -> bootstrap (LambdaMetafactory / StringConcatFactory) -> implementation method_handle;
# invoke-polymorphic MethodHandle.invoke/invokeExact on Lookup.findStatic/findVirtual/findGetter handles resolved by
# name + MethodType; Proxy.newProxyInstance interface calls routed into InvocationHandler.invoke with a Method whose
# getName() is the called name; D8/Kotlin desugared `$$Lambda$` / `$ExternalSyntheticLambda` classes via _DspVM.
_PMH_PRE = re.compile(rb"LambdaMetafactory|StringConcatFactory|Ljava/lang/invoke/MethodHandles|newProxyInstance\0"
                      rb"|\$\$Lambda|ExternalSyntheticLambda|\$\$ExternalSynthetic")
_PMH_CALLS = re.compile(r"^Ljava/lang/invoke/MethodHandles(?:\$Lookup)?;->|^Ljava/lang/reflect/Proxy;->newProxyInstance\("
                        r"|^L[\w/$]*(?:\$\$Lambda|ExternalSyntheticLambda)[\w$]*;-><init>\(")
_PMH_LAMBDA = re.compile(r"\$\$Lambda|ExternalSyntheticLambda|\$\$ExternalSynthetic")
_PMH_BUDGET_S = 0.8
_PMH_PRIM = {"Ljava/lang/%s;->TYPE" % k: v for k, v in (("Integer", "I"), ("Long", "J"), ("Boolean", "Z"), ("Byte", "B"),
             ("Character", "C"), ("Short", "S"), ("Float", "F"), ("Double", "D"), ("Void", "V"))}
_PMH_INVOKE = "(Ljava/lang/Object;Ljava/lang/reflect/Method;[Ljava/lang/Object;)Ljava/lang/Object;"


class _PmhMH:
    """A resolved method handle: kind (method_handle_item type: 1/3 getters, 4 static, 5/7/8 instance), target ref,
    bound leading args (captured lambda values / bindTo), sam = interface method name a lambda answers to."""
    __slots__ = ("kind", "ref", "bound", "sam", "concat")

    def __init__(self, kind, ref, bound=(), sam=None, concat=None):
        self.kind, self.ref, self.bound, self.sam, self.concat = kind, ref, list(bound), sam, concat


class _PmhLookup:
    pass


class _PmhType:
    __slots__ = ("desc",)

    def __init__(self, desc):
        self.desc = desc


class _PmhProxy:
    __slots__ = ("h",)

    def __init__(self, h):
        self.h = h


class _PmhMethod(_RflMem):
    pass


def _pmh_value(d, i):
    """One encoded_value -> ((type, value), next offset); ints little-endian, arrays recursed."""
    b = d[i]
    t, arg = b & 0x1F, b >> 5
    i += 1
    if t == 0x1C:
        n, i = _uleb(d, i)
        out = []
        for _ in range(min(n, 64)):
            v, i = _pmh_value(d, i)
            out.append(v)
        return (t, out), i
    if t in (0x1E, 0x1F):
        return (t, arg), i
    if t == 0x1D:
        raise ValueError("annotation")
    return (t, int.from_bytes(d[i:i + arg + 1], "little")), i + arg + 1


def _pmh_sections(dx):
    """(call_site offsets, method_handle (kind, member id) list) from the dex map_list (types 0x0007 / 0x0008)."""
    d, cs, mh = dx.d, [], []
    mo = struct.unpack_from("<I", d, 0x34)[0]
    n = struct.unpack_from("<I", d, mo)[0]
    for k in range(min(n, 64)):
        t, _, size, off = struct.unpack_from("<HHII", d, mo + 4 + 12 * k)
        if t == 0x0007:
            cs = list(struct.unpack_from(f"<{min(size, 1 << 16)}I", d, off))
        elif t == 0x0008:
            mh = [struct.unpack_from("<HHH", d, off + 8 * j)[::2] for j in range(min(size, 1 << 16))]
    return cs, mh


def _pmh_proto(dx, pi):
    so, rt, po = struct.unpack_from("<III", dx.d, dx.o_pro + 12 * pi)
    ps = ""
    if po:
        k = struct.unpack_from("<I", dx.d, po)[0]
        ps = "".join(dx.typ(t) for t in struct.unpack_from(f"<{min(k, 255)}H", dx.d, po + 4))
    return f"({ps}){dx.typ(rt)}"


class _PmhVM(_DspVM):
    """_DspVM plus invoke-custom / invoke-polymorphic, java.lang.invoke lookups and java.lang.reflect.Proxy. The first
    dynamic dispatch sets `mark` so only values produced through it count."""

    def __init__(self, dx, deadline, sec):
        super().__init__(dx, deadline)
        self.cs, self.mh = sec
        self.statics.update((k, _RflCls(v)) for k, v in _PMH_PRIM.items())

    def _handle(self, idx):
        kind, mid = self.mh[idx]
        ref = self.dx.fref(mid)[1] if kind <= 3 else self.dx.mref(mid)
        return _PmhMH(kind, ref)

    def call_mh(self, h, args, depth):
        """Invoke a resolved handle with (bound + call) args, longs/doubles as one value each."""
        if not isinstance(h, _PmhMH):
            raise _DxAbort
        args = h.bound + list(args)
        self._pick()
        if h.concat is not None:
            it = iter(args)
            return self.note("".join(_dxe_str(next(it)) if c == "\1" else c for c in h.concat))
        if h.kind <= 3:
            ct = h.ref.split("->")[0]
            self.init_class(ct)
            if h.kind == 1 and h.ref in self.statics:
                return self.note(self.statics[h.ref])
            if h.kind == 3 and args and isinstance(args[0], _DxObj):
                return self.note(args[0].f.get(h.ref))
            raise _DxAbort
        ref = h.ref
        if h.kind in (5, 8) and args and isinstance(args[0], _DxObj) and ref not in self.dx.code:
            ref = f"{args[0].t}->{ref.split('->', 1)[1]}"
        if h.kind == 6:
            raise _DxAbort
        raw = [] if h.kind == 4 else [args.pop(0) if args else None]
        for p, a in zip(_dxe_params(ref), args):
            raw += [a] + ([None] if p in "JD" else [])
        return self.invoke(ref, raw, depth)

    def dyn(self, op, ins, p, r, depth):
        u16 = lambda o: struct.unpack_from("<H", ins, o)[0]  # noqa: E731
        b1 = ins[p + 1]
        if op in (0xFA, 0xFC):
            g = u16(p + 4)
            regs = [g & 0xF, (g >> 4) & 0xF, (g >> 8) & 0xF, g >> 12, b1 & 0xF][:b1 >> 4]
        else:
            regs = list(range(u16(p + 4), u16(p + 4) + b1))
        if op >= 0xFC:  # invoke-custom: build the call site's object
            idx = u16(p + 2)
            if idx >= len(self.cs):
                raise _DxAbort
            n, i = _uleb(self.dx.d, self.cs[idx])
            items = []
            for _ in range(min(n, 16)):
                v, i = _pmh_value(self.dx.d, i)
                items.append(v)
            boot = self._handle(items[0][1]).ref if items and items[0][0] == 0x16 else ""
            name = self.dx.s(items[1][1]) if len(items) > 1 and items[1][0] == 0x17 else None
            ptypes = _dxe_params("x" + _pmh_proto(self.dx, items[2][1])) if len(items) > 2 else []
            vals, k = [], 0
            for t in ptypes:
                vals.append(r[regs[k]] if k < len(regs) else None)
                k += 2 if t in "JD" else 1
            if "LambdaMetafactory;->" in boot:
                impl = next((v for t, v in items[3:] if t == 0x16), None)
                if impl is None:
                    raise _DxAbort
                h = self._handle(impl)
                h.bound, h.sam = vals, name
                return h
            if "StringConcatFactory;->makeConcatWithConstants" in boot and len(items) > 3 and items[3][0] == 0x17:
                return self.call_mh(_PmhMH(4, "", concat=self.dx.s(items[3][1])), vals, depth)
            raise _DxAbort
        ref = self.dx.mref(u16(p + 2))  # invoke-polymorphic MethodHandle.invoke / invokeExact (proto at p + 6)
        ptypes = _dxe_params("x" + _pmh_proto(self.dx, u16(p + 6)))
        vals, k = [], 1
        for t in ptypes:
            vals.append(r[regs[k]] if k < len(regs) else None)
            k += 2 if t in "JD" else 1
        if not ref.startswith("Ljava/lang/invoke/MethodHandle;->"):
            raise _DxAbort
        return self.call_mh(r[regs[0]], vals, depth)

    def _desc(self, mt):
        return mt.desc if isinstance(mt, _PmhType) else None

    def invoke(self, ref, raw, depth):
        cls, _, rest = ref.partition("->")
        name = rest[:rest.index("(")]
        o = raw[0] if raw else None
        if cls in ("Ljava/lang/invoke/MethodHandles;",) and name in ("lookup", "publicLookup", "privateLookupIn"):
            return _PmhLookup()
        if cls == "Ljava/lang/invoke/MethodType;" and name == "methodType":
            ts = []
            for a in raw:
                if isinstance(a, list):
                    ts += a
                elif a is not None:
                    ts.append(a)
            if not ts or not all(isinstance(a, _RflCls) for a in ts):
                raise _DxAbort
            return _PmhType("(" + "".join(a.t for a in ts[1:]) + ")" + ts[0].t)
        if isinstance(o, _PmhLookup) and cls == "Ljava/lang/invoke/MethodHandles$Lookup;":
            ct, mn = self._cls(raw[1]) if name != "findConstructor" else None, raw[2] if len(raw) > 2 else None
            if name in ("findStatic", "findVirtual", "findSpecial") and isinstance(mn, str):
                desc = self._desc(raw[3])
                ms = [m for m in self._methods(ct, mn, None) if desc is None or m.endswith(desc)]
                if not ms and desc is not None:  # findVirtual on an interface / superclass: match name + descriptor
                    ms = [m for m in self.dx.code if m.endswith(f"->{mn}{desc}")]
                if len(ms) != 1:
                    raise _DxAbort
                return _PmhMH(4 if name == "findStatic" else 5, ms[0])
            if name in ("findGetter", "findStaticGetter") and isinstance(mn, str):
                if f"{ct}->{mn}" not in self._fields(ct):
                    raise _DxAbort
                return _PmhMH(1 if name == "findStaticGetter" else 3, f"{ct}->{mn}")
            if name == "unreflect" and isinstance(raw[1], _RflMem):
                ms = self._methods(raw[1].t, raw[1].name, raw[1].n)
                if len(ms) != 1:
                    raise _DxAbort
                return _PmhMH(4 if self.dx.code[ms[0]][3] & 0x8 else 5, ms[0])
            raise _DxAbort
        if isinstance(o, _PmhMH) and cls == "Ljava/lang/invoke/MethodHandle;":
            if name == "bindTo":
                return _PmhMH(o.kind, o.ref, o.bound + [raw[1]], o.sam, o.concat)
            if name == "invokeWithArguments":
                a = raw[1] if len(raw) > 1 else []
                return self.call_mh(o, list(a) if isinstance(a, list) else [a], depth)
            if name in ("invoke", "invokeExact"):
                return self.call_mh(o, raw[1:], depth)
            if name == "type":
                return _PmhType(None)
            raise _DxAbort
        if cls == "Ljava/lang/reflect/Proxy;" and name == "newProxyInstance" and len(raw) == 3:
            if raw[2] is None or raw[2] is _DXE_UNK:
                raise _DxAbort
            return _PmhProxy(raw[2])
        if isinstance(o, _PmhMethod) and cls == "Ljava/lang/reflect/Method;":
            if name == "getName":
                return o.name
            if name == "getDeclaringClass":
                return _RflCls(o.t)
            raise _DxAbort
        if isinstance(o, _PmhProxy) and name not in ("<init>",):
            args, i = [], 1
            for p in _dxe_params(ref):
                args.append(raw[i] if i < len(raw) else None)
                i += 2 if p in "JD" else 1
            m = _PmhMethod(cls, name, len(args))
            self._pick()
            return self.note(self._call_obj(o.h, "invoke" + _PMH_INVOKE, [o, m, _DxArr(args) if args else None],
                                            depth))
        if isinstance(o, _PmhMH) and o.sam is not None:
            if name != o.sam:
                raise _DxAbort
            args, i = [], 1
            for p in _dxe_params(ref):
                args.append(raw[i] if i < len(raw) else None)
                i += 2 if p in "JD" else 1
            return self.note(self.call_mh(o, args, depth))
        if isinstance(o, _DxObj) and _PMH_LAMBDA.search(o.t) and name != "<init>":
            self._pick()
        return super().invoke(ref, raw, depth)

    def _call_obj(self, h, sig, args, depth):
        """Call interface method `sig` (name + descriptor) on a handler: an in-dex object or a lambda handle."""
        if isinstance(h, _PmhMH):
            return self.call_mh(h, args, depth)
        if not isinstance(h, _DxObj):
            raise _DxAbort
        ref = f"{h.t}->{sig}"
        if ref not in self.dx.code or depth >= _DXE_DEPTH:
            raise _DxAbort
        raw = [h]
        for p, a in zip(_dxe_params(ref), args):
            raw += [a] + ([None] if p in "JD" else [])
        return self.run(ref, raw, depth + 1)


def _pmh_callers(dx):
    """App methods that use invoke-custom / invoke-polymorphic, MethodHandles lookups, Proxy.newProxyInstance or
    instantiate a desugared lambda class."""
    out = []
    for ref in dx.order:
        for pc, op, b1 in _dsp_walk(dx.code[ref][2]):
            if 0xFA <= op <= 0xFD:
                out.append(ref)
                break
            if (0x6E <= op <= 0x72 or 0x74 <= op <= 0x78) and 2 * pc + 4 <= len(dx.code[ref][2]) \
                    and _PMH_CALLS.match(dx.mref(struct.unpack_from("<H", dx.code[ref][2], 2 * pc + 2)[0])):
                out.append(ref)
                break
    return out


def method_handle_scan(apk):
    """ANS tokens reached through dynamic dispatch that never names a class by string: dex 038+ invoke-custom call
    sites (call_site_ids -> LambdaMetafactory -> implementation method handle, captured args bound; StringConcatFactory
    recipes), invoke-polymorphic MethodHandle.invoke/invokeExact on MethodHandles.Lookup.findStatic / findVirtual /
    findGetter handles resolved by name + MethodType, Proxy.newProxyInstance interface calls routed into the
    InvocationHandler.invoke with a Method whose getName() is the called name, and D8/Kotlin desugared lambda classes.
    Each app method using one of these is run by the dex_eval_scan interpreter; only values produced from the first
    dynamic dispatch on are reported. [] when absent; never raises; < 1 s."""
    hits = []
    deadline = time.time() + _PMH_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or not _PMH_PRE.search(d) or time.time() > deadline:
                continue
            try:
                dx = _DxDex(d)
                sec = _pmh_sections(dx)
                callers = _pmh_callers(dx)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            for ref in callers:
                if time.time() > deadline:
                    break
                nreg, nin, ins, acc = dx.code[ref]
                ps = _dxe_params(ref)
                if len(ps) > 4 or nin > nreg:
                    continue
                vm = _PmhVM(dx, deadline, sec)
                raw = [] if acc & 0x8 else [_DxObj(ref.split("->")[0])]
                for p in ps:
                    raw += [_dxe_default(p)] + ([None] if p in "JD" else [])
                try:
                    vm.init_class(ref.split("->")[0])
                    vm.note(vm.run(ref, raw))
                except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError,
                        RecursionError, StopIteration, struct.error):
                    pass
                if vm.mark is None:
                    continue
                for s in vm.seen[vm.mark:]:
                    hits += ANS_RE_T.findall(s)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- answer composed in code: "ANS-" prefix + numeric constants (coverage atlas row 69) -------------------------------
_ACS_PRE = re.compile(rb"ANS(?:-|_|-?%0?(?:16|8)[xX])?[%0-9xX]{0,10}\x00")
_ACS_BUDGET_S, _ACS_MAX_METHOD, _ACS_MAX = 0.8, 64, 256
_ACS_LOPS = {0x9B: "add", 0xBB: "add", 0x9C: "sub", 0xBC: "sub", 0xA2: "xor", 0xC2: "xor"}
_M32, _M64 = 0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF


def _acs_prefix_ids(d, n_str, o_str):
    """String ids whose value is an `ANS` / `ANS-` prefix (optionally fused with a %016X / %08X format), found by
    regex on the raw dex and mapped back through the string_ids table."""
    offs = {}
    for m in _ACS_PRE.finditer(d):
        s = m.group(0)[:-1]
        if m.start() >= 1 and d[m.start() - 1] == len(s) and not re.search(rb"[0-9A-Fa-f]{16}", s):
            offs[m.start() - 1] = s.decode("ascii", "replace")
    if not offs:
        return {}
    ids = struct.unpack_from(f"<{n_str}I", d, o_str)
    return {i: offs[o] for i, o in enumerate(ids) if o in offs}


def _acs_method(dx, ins, pre_ids):
    """(prefix, longs, ints, long_ops, case_hints) of one method holding an ANS prefix const-string, else None."""
    d_ins, n = ins, len(ins) // 2
    pre, longs, ints, lops, hints = None, [], [], set(), set()
    pc = 0
    while pc < n:
        o = 2 * pc
        op, b1 = d_ins[o], d_ins[o + 1]
        if op == 0 and b1 in (1, 2, 3) and o + 8 <= len(d_ins):  # switch / fill-array payloads
            ew, k = struct.unpack_from("<HI", d_ins, o + 2)
            c = struct.unpack_from("<H", d_ins, o + 2)[0]
            pc += (4 + 2 * c) if b1 == 1 else ((2 + 4 * c) if b1 == 2 else (4 + (ew * k + 1) // 2))
            continue
        w = _DOP_W[op]
        if o + 2 * w > len(d_ins):
            break
        if op in (0x1A, 0x1B):
            si = struct.unpack_from("<H" if op == 0x1A else "<I", d_ins, o + 2)[0]
            if si in pre_ids:
                pre = pre or pre_ids[si]
            else:
                s = dx.s(si) or ""
                if len(s) <= 32:
                    if re.search(r"%0?\d*x", s):
                        hints.add("lower")
                    if re.search(r"%0?\d*X", s):
                        hints.add("upper")
        elif op == 0x14:
            ints.append(struct.unpack_from("<i", d_ins, o + 2)[0])
        elif op == 0x15:
            ints.append(_s16(struct.unpack_from("<H", d_ins, o + 2)[0]) << 16)
        elif op in (0x17, 0x18, 0x19):
            v = (struct.unpack_from("<i", d_ins, o + 2)[0] if op == 0x17 else
                 struct.unpack_from("<q", d_ins, o + 2)[0] if op == 0x18 else
                 _s16(struct.unpack_from("<H", d_ins, o + 2)[0]) << 48)
            if abs(v) >= 1 << 32 or (op == 0x17 and v < -(1 << 24)):  # masks / counters are not answers
                longs.append(v)
        elif op == 0x26:
            t = o + 2 * struct.unpack_from("<i", d_ins, o + 2)[0]
            if 0 <= t and t + 8 <= len(d_ins) and d_ins[t:t + 2] == b"\x00\x03":
                ew, k = struct.unpack_from("<HI", d_ins, t + 2)
                if ew in (4, 8) and k <= 64 and t + 8 + ew * k <= len(d_ins):
                    vals = struct.unpack_from(f"<{k}{'i' if ew == 4 else 'q'}", d_ins, t + 8)
                    (ints if ew == 4 else longs).extend(vals)
        elif op in _ACS_LOPS:
            lops.add(_ACS_LOPS[op])
        elif 0x6E <= op <= 0x72 or 0x74 <= op <= 0x78:
            ref = dx.mref(struct.unpack_from("<H", d_ins, o + 2)[0])
            if "->toHexString(" in ref:
                hints.add("lower")
            elif "->toUpperCase(" in ref:
                hints.add("UPPER")
        pc += w
    if pre is None:
        return None
    if re.search(r"%0?\d*x", pre):
        hints.add("lower")
    if re.search(r"%0?\d*X", pre):
        hints.add("upper")
    return pre, longs, ints, lops, hints


def _acs_hex(longs, ints, lops):
    """16-hex readings of one method's numbers, most direct first."""
    out = [format(v & _M64, "016X") for v in longs]
    if 2 <= len(longs) <= 8:
        f = {"xor": lambda a, b: a ^ b, "add": lambda a, b: a + b, "sub": lambda a, b: a - b}
        for name in sorted(lops):
            for i in range(len(longs)):
                for j in range(len(longs)):
                    if i != j and (j > i or name == "sub"):
                        out.append(format(f[name](longs[i], longs[j]) & _M64, "016X"))
    pairs = [(i, i + 1) for i in range(len(ints) - 1)]
    if len(ints) <= 8:
        pairs += [(i, j) for i in range(len(ints)) for j in range(i + 2, len(ints))]
        pairs += [(i + 1, i) for i in range(len(ints) - 1)]
    out += [f"{ints[i] & _M32:08X}{ints[j] & _M32:08X}" for i, j in pairs]
    for i in range(len(ints)):  # Integer.toHexString(a) + toHexString(b) + ... (unpadded) reaching exactly 16 digits
        s = ""
        for j in range(i, min(len(ints), i + 6)):
            s += format(ints[j] & _M32, "X")
            if len(s) >= 16:
                if len(s) == 16 and j - i >= 2:
                    out.append(s)
                break
    return list(dict.fromkeys(out))


def ans_compose_scan(apk):
    """ANS tokens composed in code from an `ANS-` / `ANS` prefix const-string plus numeric constants in the SAME method
    (coverage atlas row 69): `"ANS-" + String.format("%016X", long)`, `Long.toHexString(c)` (zero-padded), a hi/lo int
    pair (`%08X%08X` / `((long) hi << 32) | lo`), `Integer.toHexString(a) + Integer.toHexString(b)`, fill-array-data
    long[] / int[] elements, and xor / add / sub of two long constants when the method has that op. Case follows the
    code (toHexString / %x -> lower, %X / toUpperCase -> upper; both when it gives no sign). These are CANDIDATES for
    proof_flow ranking -- several per method -- never one to submit blind. [] when absent; never raises; < 1 s."""
    hits, dead = [], []
    deadline = time.time() + _ACS_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or b"ANS" not in d or time.time() > deadline:
                continue
            try:
                n_str, o_str = struct.unpack_from("<2I", d, 0x38)
                if n_str > 1 << 22 or o_str + 4 * n_str > len(d):
                    continue
                pre_ids = _acs_prefix_ids(d, n_str, o_str)
                if not pre_ids:
                    continue
                dx = _DxDex(d)
            except (ValueError, struct.error, IndexError):
                continue
            pats = re.compile(b"|".join(re.escape(struct.pack("<H" if i < 1 << 16 else "<I", i)) for i in pre_ids))
            live = _eav_reached(dx, deadline)
            for ref, (_, _, ins, _) in dx.code.items():
                if time.time() > deadline or len(hits) + len(dead) >= _ACS_MAX:
                    break
                if not pats.search(ins) or _eav_table_walk(dx, ins):
                    continue
                try:
                    r = _acs_method(dx, ins, pre_ids)
                except (struct.error, IndexError, ValueError):
                    continue
                if not r:
                    continue
                pre, longs, ints, lops, hints = r
                hx = _acs_hex(longs, ints, lops)[:_ACS_MAX_METHOD]
                if "UPPER" in hints or hints == {"upper"}:
                    cases = ("upper",)
                elif hints == {"lower"}:
                    cases = ("lower",)
                else:
                    cases = ("upper", "lower")
                for c in cases:
                    (hits if live is None or ref in live else dead).extend(
                        f"ANS-{h if c == 'upper' else h.lower()}" for h in hx)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return [h for h in dict.fromkeys(hits + dead) if not _eav_alphabet(h)][:_ACS_MAX]


# --- digest / HMAC-derived answers (coverage atlas rows 33, 69: "ANS-" + hex prefix of MessageDigest / Mac output) ----
_DGA_BUDGET_S, _DGA_MAX_IN, _DGA_MAX_HASH, _DGA_MAX = 0.3, 14, 2400, 1024
_DGA_ALGO = re.compile(r"(?i)(?:Hmac)?(?:MD5|SHA-?1|SHA-?(?:224|256|384|512))")
_DGA_JUNK = re.compile(r"(?i)ANS[-_]?|%0?\d*[xX]|UTF-?8|US-ASCII|ISO-8859-1|UTF-16(?:LE|BE)?|0|")
_DGA_HL = {"MD5": "md5", "SHA1": "sha1", "SHA224": "sha224", "SHA256": "sha256", "SHA384": "sha384", "SHA512": "sha512"}
_DGA_SEPS = ("", ":", "|", "-", "_", "/")


def _dga_sstr(dx, cache):
    """{field ref: str} of the String static fields with a const value (encoded static_values or <clinit> sput)."""
    if cache:
        return cache
    for ct, (sfl, sval) in dx.sfields.items():
        if sval and sfl:
            for fi, v in zip(sfl, _pf_static_values(dx.d, sval, len(sfl))):
                if v and fi < dx.n_fld:
                    cache[dx.fref(fi)[1]] = dx.s(v[1])
    for ct, ref in dx.clinit.items():
        last, ins = {}, dx.code[ref][2]
        for op, o in _dga_ops(ins):
            if op in (0x1A, 0x1B):
                last[ins[o + 1]] = dx.s(struct.unpack_from("<H" if op == 0x1A else "<I", ins, o + 2)[0])
            elif op == 0x69 and ins[o + 1] in last:
                fi = struct.unpack_from("<H", ins, o + 2)[0]
                if fi < dx.n_fld:
                    cache[dx.fref(fi)[1]] = last[ins[o + 1]]
    cache.setdefault(None, None)
    return cache


def _dga_ops(ins):
    """(opcode, byte offset) of each Dalvik instruction of a code item (switch / fill-array payloads skipped)."""
    pc, n = 0, len(ins) // 2
    while pc < n:
        o = 2 * pc
        op, b1 = ins[o], ins[o + 1]
        if op == 0 and b1 in (1, 2, 3) and o + 8 <= len(ins):
            ew, k = struct.unpack_from("<HI", ins, o + 2)
            c = ew
            pc += (4 + 2 * c) if b1 == 1 else ((2 + 4 * c) if b1 == 2 else (4 + (ew * k + 1) // 2))
            continue
        w = _DOP_W[op]
        if o + 2 * w > len(ins):
            return
        yield op, o
        pc += w


def _dga_method(dx, ins, sstr, depth=0):
    """(strings in code order, invoked method refs) of one code item; const-strings of in-dex callees (one level) and
    String static fields read by sget-object are inlined where they occur."""
    strs, refs = [], []
    for op, o in _dga_ops(ins):
        if op in (0x1A, 0x1B):
            strs.append(dx.s(struct.unpack_from("<H" if op == 0x1A else "<I", ins, o + 2)[0]))
        elif op == 0x62:
            fi = struct.unpack_from("<H", ins, o + 2)[0]
            v = fi < dx.n_fld and _dga_sstr(dx, sstr).get(dx.fref(fi)[1])
            if v:
                strs.append(v)
        elif 0x6E <= op <= 0x78 and op != 0x73:
            mi = struct.unpack_from("<H", ins, o + 2)[0]
            if mi < dx.n_met:
                ref = dx.mref(mi)
                refs.append(ref)
                if depth == 0 and ref in dx.code and len(dx.code[ref][2]) <= 4096 and "Ljava/" not in ref[:7]:
                    s2, r2 = _dga_method(dx, dx.code[ref][2], sstr, 1)
                    strs += s2
                    refs += r2
    return strs, refs


def _dga_hex(dg, upper):
    """first / last 16 hex of a digest (%02x and BigInteger(1, d).toString(16) readings)."""
    h = dg.hex()
    hs = [h, h.lstrip("0")]
    out = []
    for x in hs:
        if len(x) >= 16:
            out += [x[:16], x[-16:]]
    return [x.upper() if upper else x for x in out]


def digest_answer_candidates(apk):
    """ANS tokens computed as a hex prefix / suffix of a MessageDigest / Mac result (coverage atlas rows 33, 69): every
    method that holds an `ANS` prefix const-string (or calls one that does) and calls MessageDigest.getInstance /
    Mac.getInstance has its algorithm names and app-visible inputs collected -- its own const-strings (+ in-dex callees,
    String static fields), the package name / case id when it calls getPackageName, the signer cert (DER, sha256 hex)
    when it reads signatures -- and MD5/SHA-x digests of each input, the in-order concatenation, ordered pairs with a
    few separators and HMACs keyed by each string are computed (<= ~2.4k hashes). Returns {"value", "source"} in rank
    order (all-in-order concat and singles first). CANDIDATES for proof_flow / GM, never one answer. [] when absent;
    never raises; ~0.3 s."""
    import hashlib
    import hmac
    out = []
    deadline = time.time() + _DGA_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
            dexes = [d for d in dexes if d[:4] == b"dex\n" and len(d) >= 0x70 and b"ANS" in d
                     and (b"Ljava/security/MessageDigest;" in d or b"Ljavax/crypto/Mac;" in d)]
            if not dexes:
                return []
            seeds, _ = _idk_seeds(z)
        certs = None
        for d in dexes:
            try:
                dx = _DxDex(d)
            except (ValueError, struct.error, IndexError):
                continue
            sstr, nhash = {}, 0
            for ref in list(dx.order):
                if time.time() > deadline or nhash >= _DGA_MAX_HASH:
                    break
                ins = dx.code[ref][2]
                try:
                    strs, refs = _dga_method(dx, ins, sstr)
                except (struct.error, IndexError, ValueError):
                    continue
                jrefs = " ".join(refs)
                if not any(s.startswith("ANS") for s in strs) or \
                        ("MessageDigest;->getInstance" not in jrefs and "Mac;->getInstance" not in jrefs):
                    continue
                algos = list(dict.fromkeys(_DGA_ALGO.fullmatch(s).group(0) for s in strs if _DGA_ALGO.fullmatch(s)))
                mac = "Mac;->getInstance" in jrefs
                names = list(dict.fromkeys(re.sub(r"(?i)^hmac|-", "", a).upper() for a in algos))
                names = [n for n in names if n in _DGA_HL] or ["SHA256", "SHA1", "MD5", "SHA512"]
                upper = not (any(re.fullmatch(r"%0?\d*x", s) for s in strs) and "toUpperCase" not in jrefs
                             and not any(re.fullmatch(r"%0?\d*X", s) for s in strs))
                ins_s = [s for s in dict.fromkeys(strs) if not _DGA_ALGO.fullmatch(s) and not _DGA_JUNK.fullmatch(s)
                         and len(s) <= 512]
                if "getPackageName" in jrefs or "getApplicationId" in jrefs:
                    ins_s += [s for s in seeds if s not in ins_s]
                ins_s = ins_s[:_DGA_MAX_IN]
                msgs = [(s, s.encode("utf-8", "surrogatepass")) for s in ins_s]
                if "Signature;->toByteArray" in jrefs or "signingInfo" in jrefs or "getApkContentsSigners" in jrefs:
                    if certs is None:
                        certs = signing_certs(apk)
                    for c in certs[:2]:
                        msgs += [("cert.der", c["der"]), ("cert.sha256", c["sha256"].encode()),
                                 ("cert.SHA256", c["sha256"].upper().encode())]
                if not msgs:
                    continue
                combos = []
                strs_only = [m for m in msgs if not m[0].startswith("cert.")]
                if len(strs_only) > 1:
                    combos.append(("concat", b"".join(m[1] for m in strs_only)))
                combos += msgs
                combos += [(f"{a[0]}{sep}{b[0]}", a[1] + sep.encode() + b[1]) for sep in _DGA_SEPS
                           for a in msgs for b in msgs if a is not b]
                keys = [m for m in strs_only] if mac or len(strs_only) > 1 else []
                for nm in names:
                    hl = _DGA_HL[nm]
                    jobs = []
                    if mac:
                        jobs += [(f"Hmac{nm}[{k[0]}]({m[0]})", lambda k=k, m=m: hmac.new(k[1], m[1], hl).digest())
                                 for k in keys for m in combos[:1 + len(msgs)] if k is not m]
                    jobs += [(f"{nm}({c[0]})", lambda c=c: hashlib.new(hl, c[1]).digest()) for c in combos]
                    if not mac:
                        jobs += [(f"Hmac{nm}[{k[0]}]({m[0]})", lambda k=k, m=m: hmac.new(k[1], m[1], hl).digest())
                                 for k in keys for m in combos[:1 + len(msgs)] if k is not m]
                    for src, fn in jobs:
                        if nhash >= _DGA_MAX_HASH or time.time() > deadline:
                            break
                        nhash += 1
                        out += [{"value": f"ANS-{h}", "source": f"{ref}: {src}"} for h in _dga_hex(fn(), upper)]
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    seen, res = set(), []
    for c in out:
        if c["value"] not in seen:
            seen.add(c["value"])
            res.append(c)
    return res[:_DGA_MAX]


def digest_answer_scan(apk):
    """ANS values of digest_answer_candidates (rank order); [] when absent."""
    return [c["value"] for c in digest_answer_candidates(apk)]


# --- data hidden in a dex outside its declared structure (coverage atlas rows 51, 62) --------------------------------
_DSL_MAX_DEX, _DSL_BUDGET_S, _DSL_MAX_BLOB, _DSL_MAX_ORPHANS = 32 << 20, 0.6, 1 << 20, 256
_DSL_MAGIC = re.compile(rb"dex\n0[0-9]{2}\0")
_DSL_UNIT = {0x0001: 4, 0x0002: 4, 0x0003: 12, 0x0004: 8, 0x0005: 8, 0x0006: 32, 0x0007: 4, 0x0008: 8}
_DSL_INVOKE = frozenset([*range(0x6E, 0x73), *range(0x74, 0x79), 0xFA, 0xFB])


def _dsl_str(d, off):
    _, j = _uleb(d, off)
    e = d.find(b"\0", j)
    return j, (e if e >= 0 else len(d))


def _dsl_insns(ins, n_ins):
    """(const-string idxs, invoked method idxs) of one code item."""
    strs, calls, pc = [], [], 0
    while pc < n_ins:
        p = 2 * pc
        op = ins[p]
        if op == 0x1A or op == 0x1B:
            strs.append(struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0])
        elif op in _DSL_INVOKE:
            calls.append(struct.unpack_from("<H", ins, p + 2)[0])
        elif op == 0 and ins[p + 1] in (1, 2, 3):  # switch / fill-array payloads
            if ins[p + 1] == 1:
                pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
            elif ins[p + 1] == 2:
                pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
            else:
                w, n = struct.unpack_from("<HI", ins, p + 2)
                pc += 4 + (w * n + 1) // 2
            continue
        pc += _DOP_W[op]
    return strs, calls


def dex_slack_facts_one(d, deadline=None):
    """Structure facts of one dex blob (pure Python): {"version", "file_size", "real_size", "adler_ok", "sha1_ok",
    "appended" (bytes past header file_size), "gaps" [(off, bytes)] (non-zero bytes inside file_size not covered by any
    map_list item: between fixed-size sections / string_data items, or after the last item), "orphans" [str] (string_ids
    no code const-string / type / proto / field / method / source-file uses -- static values, annotations, planted
    strings), "decoy_likely" [str] (strings const-loaded only by never-invoked private methods or by a duplicate
    class_def), "dup_classes" [descriptor]}. None when not a dex; never raises."""
    deadline = deadline or time.time() + _DSL_BUDGET_S
    if len(d) < 0x70 or not _DSL_MAGIC.fullmatch(d[:8]):
        return None
    import hashlib
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    fsz = u32(0x20)
    body = d[:min(fsz, len(d))]
    f = {"version": d[4:7].decode(), "file_size": fsz, "real_size": len(d),
         "adler_ok": zlib.adler32(body[12:]) == u32(8), "sha1_ok": hashlib.sha1(body[32:]).digest() == d[12:32],
         "appended": d[fsz:] if 0x70 <= fsz < len(d) else b"", "gaps": [], "orphans": [], "decoy_likely": [],
         "dup_classes": []}
    try:
        (n_str, o_str, n_typ, o_typ, n_pro, o_pro, n_fld, o_fld, n_met, o_met, n_cls, o_cls) = \
            struct.unpack_from("<12I", d, 0x38)
        if n_str > 1 << 22 or n_met > 1 << 20 or n_cls > 1 << 20 or o_str + 4 * n_str > len(d) \
                or o_typ + 4 * n_typ > len(d) or o_pro + 12 * n_pro > len(d) or o_fld + 8 * n_fld > len(d) \
                or o_met + 8 * n_met > len(d) or o_cls + 32 * n_cls > len(d):
            return f
        soff = list(struct.unpack_from(f"<{n_str}I", d, o_str))
        # map_list coverage -> slack between / after items
        mo = u32(0x34)
        items = []
        if mo and mo + 4 <= len(d):
            n = u32(mo)
            if n <= 64 and mo + 4 + 12 * n <= len(d):
                items = sorted((o, t, s) for t, _, s, o in (struct.unpack_from("<HHII", d, mo + 4 + 12 * k)
                                                              for k in range(n)))
        lim = min(fsz, len(d))
        for k, (o, t, s) in enumerate(items):
            nxt = items[k + 1][0] if k + 1 < len(items) else lim
            if t == 0:
                end = 0x70
            elif t == 0x1000:
                end = o + 4 + 12 * u32(o)
            elif t in _DSL_UNIT:
                end = o + s * _DSL_UNIT[t]
            elif t == 0x2002:
                spans = sorted(so for so in soff if o <= so < nxt)
                end = o
                for so in spans:
                    if so - end > 3 and d[end:so].strip(b"\0"):
                        f["gaps"].append((end, d[end:so]))
                    end = max(end, _dsl_str(d, so)[1] + 1)
            else:
                continue  # variable-size item: extent unknown, assume it runs to the next item
            if nxt - end > 3 and d[end:nxt].strip(b"\0"):
                f["gaps"].append((end, d[end:nxt]))
        # string references: names / types / code
        named = set(struct.unpack_from(f"<{n_typ}I", d, o_typ))
        named |= {u32(o_pro + 12 * k) for k in range(n_pro)}
        named |= {u32(o_fld + 8 * k + 4) for k in range(n_fld)}
        mids = [struct.unpack_from("<HHI", d, o_met + 8 * k) for k in range(n_met)]
        named |= {m[2] for m in mids}
        meths, seen_cls = [], set()
        for c in range(n_cls):
            if time.time() > deadline:
                return f
            base = o_cls + 32 * c
            cidx, src, cdata = u32(base), u32(base + 16), u32(base + 24)
            named.add(src)
            shadow = cidx in seen_cls
            if shadow and cidx < n_typ:
                j, e = _dsl_str(d, soff[u32(o_typ + 4 * cidx)])
                f["dup_classes"].append(d[j:e].decode("utf-8", "replace"))
            seen_cls.add(cidx)
            if not cdata or cdata >= len(d):
                continue
            i = cdata
            sf, i = _uleb(d, i)
            inf, i = _uleb(d, i)
            dm, i = _uleb(d, i)
            vm, i = _uleb(d, i)
            for _ in range(2 * (sf + inf)):
                _, i = _uleb(d, i)
            for direct, cnt in ((True, dm), (False, vm)):
                mi = 0
                for _ in range(cnt):
                    x, i = _uleb(d, i)
                    mi += x
                    acc, i = _uleb(d, i)
                    code, i = _uleb(d, i)
                    if not code or code + 16 > len(d) or mi >= n_met:
                        continue
                    n_ins = u32(code + 12)
                    strs, calls = _dsl_insns(d[code + 16:code + 16 + 2 * n_ins], n_ins)
                    meths.append((mi, acc, direct, shadow, strs, calls))
        invoked = {(mids[m][1], mids[m][2]) for *_, calls in meths for m in calls if m < n_met}
        loaded = {s for *_, strs, _ in meths for s in strs}
        live, dead = set(), set()
        for mi, acc, direct, shadow, strs, _ in meths:
            _, pr, nm = mids[mi]
            j, e = _dsl_str(d, soff[nm]) if nm < n_str else (0, 0)
            name = d[j:e]
            unused = direct and acc & 0x2 and name not in (b"<init>", b"<clinit>") and (pr, nm) not in invoked and nm not in loaded
            (dead if shadow or unused else live).update(strs)
        for k, so in enumerate(soff):
            if k in named or k in live:
                continue
            j, e = _dsl_str(d, so)
            (f["decoy_likely"] if k in dead else f["orphans"]).append(d[j:e].decode("utf-8", "replace"))
    except (struct.error, IndexError, ValueError):
        pass
    return f


def _dsl_blob_hits(b, depth, deadline):
    """ANS tokens inside a slack blob: literal, a nested zip / dex (plain or 1-byte xor), or a decode_any chain."""
    b = b.strip(b"\0")[:_DSL_MAX_BLOB]
    if not b:
        return []
    hits = [m.decode() for m in ANS_RE_B.findall(b)]
    if hits:
        return hits
    k = b.find(b"PK\x03\x04")
    got = _unwrap_nested(b[k:] if k > 0 else b)
    if got and depth > 0:
        kind, inner = got
        if kind == "dex":
            return [m.decode() for m in ANS_RE_B.findall(inner)] or _dsl_dex_hits(inner, depth - 1, deadline)
        bio = io.BytesIO(inner)
        return [m.group(0) for c in puzzle_candidates(bio) for m in ANS_RE_T.finditer(c)] + raw_entry_scan(bio) + \
            dex_strings(bio)
    if time.time() < deadline:
        r = decode_any(b, chain=len(b) <= 4096, chain_s=min(0.2, max(0.0, deadline - time.time())))
        if r:
            return ANS_RE_T.findall(r)
    return []


def _dsl_dex_hits(d, depth, deadline):
    f = dex_slack_facts_one(d, deadline)
    if not f:
        return []
    hits = []
    for b in [f["appended"]] + [g for _, g in f["gaps"]]:
        hits += _dsl_blob_hits(b, depth, deadline)
    for s in f["orphans"][:_DSL_MAX_ORPHANS]:
        if hits or time.time() > deadline:
            break
        if len(s) < 8 or len(s) > 4096 or s.startswith(("L", "[", "(")) and s.endswith((";", "V")):
            continue
        r = ANS_RE_T.search(s) or decode_any(s, chain=False, cap=600)
        if r:
            hits += ANS_RE_T.findall(r if isinstance(r, str) else r.group(0))
    return hits


def dex_slack_facts(apk):
    """[{"name", **dex_slack_facts_one}] for every classes*.dex / dex-magic entry of the APK (header file_size vs real
    length, adler32/sha1 checks, magic version 035-041, map_list slack, orphan and decoy-likely strings, duplicate
    class_defs). Decoy-likely strings (const-loaded only by never-invoked private methods / shadowed duplicate classes)
    are for proof_flow ranking, never answers on their own. [] when absent; never raises."""
    out = []
    deadline = time.time() + _DSL_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if info.is_dir() or info.file_size > _DSL_MAX_DEX or info.file_size < 0x70:
                    continue
                if not re.fullmatch(r"classes\d*\.dex", Path(info.filename).name):
                    with z.open(info) as fh:
                        if not _DSL_MAGIC.fullmatch(fh.read(8)):
                            continue
                f = dex_slack_facts_one(z.read(info), deadline)
                if f:
                    out.append({"name": info.filename, **f})
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no facts
        pass
    return out


def dex_slack_scan(apk, depth=2):
    """ANS tokens hidden in a dex outside its declared structure (rows 51, 62): bytes appended past the header
    file_size, non-zero slack inside file_size not covered by any map_list item, and orphan string_ids no code loads
    (an unused static final String / annotation value / planted string). Blobs go through a literal scan, a nested
    zip / dex unwrap (puzzle_candidates / raw_entry_scan / dex_strings inside), then decode_any; orphan strings through
    decode_any. Strings loaded only by never-invoked methods / duplicate class_defs are decoy-likely and NOT returned
    (see dex_slack_facts). [] when absent; never raises; < 1 s."""
    hits = []
    deadline = time.time() + _DSL_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if info.is_dir() or info.file_size > _DSL_MAX_DEX or info.file_size < 0x70 or time.time() > deadline:
                    continue
                if not re.fullmatch(r"classes\d*\.dex", Path(info.filename).name):
                    if not info.filename.startswith(("assets/", "res/raw/")):
                        continue
                    with z.open(info) as fh:
                        if not _DSL_MAGIC.fullmatch(fh.read(8)):
                            continue
                hits += _dsl_dex_hits(z.read(info), depth, deadline)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(h for h in hits if ANS_RE_T.fullmatch(h)))


# --- Java serialization streams (coverage atlas row 73) --------------------------------------------------------------
# An ObjectOutputStream blob (magic AC ED 00 05) in an asset / res/raw entry, a dex byte[] literal (fill-array-data
# keeps it verbatim inside classes.dex) or wrapped as base64 ("rO0AB...") / hex ("aced0005...") text anywhere. Minimal
# pure-Python ObjectInputStream grammar (TC_OBJECT / CLASSDESC / PROXYCLASSDESC / STRING / LONGSTRING / ARRAY / ENUM /
# CLASS / REFERENCE / BLOCKDATA[LONG] / RESET / EXCEPTION, field descriptors, primitive values, class hierarchies,
# writeObject annotations) emitting every string and field (name, value); a truncated or non-default stream keeps what
# parsed and falls back to a scan of TC_STRING records (0x74 + u16 len). Values go through a literal scan then
# decode_any (keyed by a key/secret/seed-named field when one exists).
_JSR_MAGIC = b"\xac\xed\x00\x05"
_JSR_B64 = re.compile(rb"rO0AB[A-Za-z0-9+/_\-]{12,}={0,2}")
_JSR_HEX = re.compile(rb"(?i)aced0005(?:[0-9a-f]{2}){8,}")
_JSR_MAX_ENTRY, _JSR_MAX_BLOBS, _JSR_MAX_ITEMS, _JSR_DEPTH = 32 << 20, 32, 20_000, 64
_JSR_BUDGET_S, _JSR_DECODE_BUDGET = 1.0, 200
_JSR_PRIM = {"B": (">b", 1), "C": (">H", 2), "D": (">d", 8), "F": (">f", 4), "I": (">i", 4), "J": (">q", 8),
             "S": (">h", 2), "Z": ("?", 1)}
_JSR_KEYISH = re.compile(r"(?i)key|secret|pass|seed|salt")


class _JsrStop(Exception):
    pass


class _JsrReader:
    """Recursive-descent ObjectInputStream reader. `out` collects (name, value) pairs: field values by
    "Class.field", other strings / block data by kind. Raises _JsrStop at the first malformed / unsupported byte."""

    def __init__(self, b, i):
        self.b, self.i, self.h, self.out, self.n = b, i, [], [], 0

    def take(self, k):
        if k < 0 or self.i + k > len(self.b):
            raise _JsrStop("eof")
        v = self.b[self.i:self.i + k]
        self.i += k
        return v

    def u(self, fmt, k):
        return struct.unpack(fmt, self.take(k))[0]

    def utf(self, wide=False):
        n = self.u(">Q", 8) if wide else self.u(">H", 2)
        if n > len(self.b):
            raise _JsrStop("len")
        return self.take(n).decode("utf-8", "replace")

    def emit(self, name, v):
        self.n += 1
        if self.n > _JSR_MAX_ITEMS:
            raise _JsrStop("items")
        self.out.append((name, v))

    def handle(self, v):
        self.h.append(v)
        return len(self.h) - 1

    def content(self, d=0, name="value"):
        if d > _JSR_DEPTH:
            raise _JsrStop("depth")
        tc = self.u("B", 1)
        if tc == 0x70:  # TC_NULL
            return None
        if tc == 0x71:  # TC_REFERENCE
            k = self.u(">I", 4) - 0x7E0000
            if not 0 <= k < len(self.h):
                raise _JsrStop("ref")
            return self.h[k]
        if tc in (0x74, 0x7C):  # TC_STRING / TC_LONGSTRING
            s = self.utf(tc == 0x7C)
            self.handle(s)
            self.emit(name, s)
            return s
        if tc in (0x72, 0x7D):
            self.i -= 1
            return self.classdesc(d)
        if tc == 0x73:  # TC_OBJECT
            return self.obj(d)
        if tc == 0x75:  # TC_ARRAY
            return self.array(d, name)
        if tc == 0x76:  # TC_CLASS
            cd = self.classdesc(d + 1)
            self.handle(cd)
            return cd
        if tc == 0x7E:  # TC_ENUM
            cd = self.classdesc(d + 1)
            k = self.handle(None)
            v = self.content(d + 1, (cd or {}).get("name", "enum"))
            self.h[k] = v
            return v
        if tc in (0x77, 0x7A):  # TC_BLOCKDATA / TC_BLOCKDATALONG
            blk = self.take(self.u("B", 1) if tc == 0x77 else self.u(">I", 4))
            self.emit("blockdata", blk)
            return blk
        if tc == 0x79:  # TC_RESET
            self.h = []
            return None
        if tc == 0x7B:  # TC_EXCEPTION
            self.h = []
            v = self.content(d + 1, "exception")
            self.h = []
            return v
        raise _JsrStop(f"tc {tc:#x}")

    def annotation(self, d):
        while True:
            if self.i < len(self.b) and self.b[self.i] == 0x78:  # TC_ENDBLOCKDATA
                self.i += 1
                return
            self.content(d + 1, "annotation")

    def classdesc(self, d):
        tc = self.u("B", 1)
        if tc == 0x70:
            return None
        if tc == 0x71:
            self.i -= 1
            v = self.content(d)
            if v is not None and not isinstance(v, dict):
                raise _JsrStop("ref not a class")
            return v
        if tc == 0x7D:  # TC_PROXYCLASSDESC
            cd = {"name": "$Proxy", "flags": 0x02, "fields": [], "super": None}
            self.handle(cd)
            for _ in range(min(self.u(">I", 4), 256)):
                self.emit("interface", self.utf())
            self.annotation(d)
            cd["super"] = self.classdesc(d + 1)
            return cd
        if tc != 0x72:
            raise _JsrStop("classdesc")
        cd = {"name": self.utf(), "fields": [], "super": None}
        self.take(8)  # serialVersionUID
        self.handle(cd)
        cd["flags"] = self.u("B", 1)
        for _ in range(self.u(">H", 2)):
            t = chr(self.u("B", 1))
            fname = self.utf()
            if t in "[L":
                self.content(d + 1, "classname")
            elif t not in _JSR_PRIM:
                raise _JsrStop("field type")
            cd["fields"].append((t, fname))
        self.annotation(d)
        cd["super"] = self.classdesc(d + 1)
        return cd

    def value(self, t, d, name):
        if t in _JSR_PRIM:
            fmt, k = _JSR_PRIM[t]
            v = self.u(fmt, k)
            return chr(v) if t == "C" else v
        return self.content(d + 1, name)

    def obj(self, d):
        cd = self.classdesc(d + 1)
        o = {"class": (cd or {}).get("name")}
        self.handle(o)
        chain = []
        while cd is not None and len(chain) < 64:
            chain.append(cd)
            cd = cd.get("super")
        for c in reversed(chain):
            fl = c.get("flags", 0)
            if fl & 0x04:  # externalizable: only the block-data (protocol 2) form is readable
                if not fl & 0x08:
                    raise _JsrStop("externalizable v1")
                self.annotation(d)
                continue
            for t, fname in c["fields"]:
                key = f"{c['name']}.{fname}"
                v = self.value(t, d, key)
                o[fname] = v
                if t in _JSR_PRIM:
                    self.emit(key, v)
            if fl & 0x01:  # SC_WRITE_METHOD: custom writeObject data follows
                self.annotation(d)
        return o

    def array(self, d, name):
        cd = self.classdesc(d + 1)
        cname = (cd or {}).get("name") or "[L"
        k = self.handle(None)
        n = self.u(">i", 4)
        if n < 0 or n > len(self.b):
            raise _JsrStop("array len")
        t = cname[1:2]
        if t == "B":
            v = self.take(n)
        elif t in _JSR_PRIM:
            fmt, w = _JSR_PRIM[t]
            raw = self.take(n * w)
            v = [struct.unpack_from(fmt, raw, j * w)[0] for j in range(n)]
            if t == "C":
                v = "".join(map(chr, v))
        else:
            v = [self.content(d + 1, name) for _ in range(n)]
        self.h[k] = v
        if t in _JSR_PRIM:
            self.emit(name, v)
        return v


def _jsr_strings_fallback(b, start):
    """(name, value) of every plausible TC_STRING record (0x74 + u16 len + printable UTF-8) from `start`."""
    out, i = [], b.find(b"\x74", start)
    while 0 <= i < len(b) - 3 and len(out) < _JSR_MAX_ITEMS:
        n = int.from_bytes(b[i + 1:i + 3], "big")
        s = b[i + 3:i + 3 + n]
        if n >= 4 and len(s) == n:
            try:
                t = s.decode("utf-8")
            except UnicodeDecodeError:
                t = ""
            if t.isprintable():
                out.append(("string", t))
                i = b.find(b"\x74", i + 3 + n)
                continue
        i = b.find(b"\x74", i + 1)
    return out


def java_serial_parse(b, start=0):
    """[(name, value)] of a Java serialization stream at b[start:] (magic AC ED 00 05): every string, block-data
    chunk, primitive / primitive-array value, field values keyed "Class.field". Consecutive top-level objects are read
    until the data ends; a malformed / truncated / unsupported tail keeps what parsed and appends the TC_STRING scan of
    the rest. [] when the magic is absent; never raises."""
    try:
        b = bytes(b)
        if b[start:start + 4] != _JSR_MAGIC:
            return []
        r, done = _JsrReader(b, start + 4), 0
        try:
            while r.i < len(b):
                r.content()
                done += 1
            return r.out
        except _JsrStop:  # after a complete top-level object the tail is the host's bytes (a dex past its byte[])
            return r.out if done else r.out + _jsr_strings_fallback(b, r.i)
        except RecursionError:
            return r.out
    except Exception:  # noqa: BLE001 - impostor bytes: nothing
        return []


def _jsr_blobs(b):
    """Serialization streams inside one entry's bytes: raw magic occurrences (an asset, a dex byte[] literal),
    base64 "rO0AB..." and hex "aced0005..." runs (also a whole entry of base64 text with line breaks)."""
    out = []
    i = b.find(_JSR_MAGIC)
    while i >= 0 and len(out) < _JSR_MAX_BLOBS:
        out.append((b, i))
        i = b.find(_JSR_MAGIC, i + 4)
    if b"rO0AB" in b:
        cands = [m.group(0) for m in _JSR_B64.finditer(b)]
        if b.lstrip()[:5] == b"rO0AB":
            cands.insert(0, re.sub(rb"\s+", b"", b))
        for m in cands[:_JSR_MAX_BLOBS]:
            for alt in (False, True):
                try:
                    s = m.translate(bytes.maketrans(b"-_", b"+/")) if alt else m
                    raw = base64.b64decode(s + b"=" * (-len(s) % 4))
                except (binascii.Error, ValueError):
                    continue
                if raw[:4] == _JSR_MAGIC:
                    out.append((raw, 0))
                    break
    for m in list(_JSR_HEX.finditer(b))[:_JSR_MAX_BLOBS]:
        out.append((bytes.fromhex(m.group(0).decode()), 0))
    seen, uniq = set(), []
    for blob, off in out:
        if (id(blob), off) in seen or (off == 0 and blob in seen):
            continue
        seen.update(((id(blob), off), blob) if off == 0 else ((id(blob), off),))
        uniq.append((blob, off))
    return uniq[:_JSR_MAX_BLOBS * 2]


def java_serial_records(apk):
    """[{"entry", "offset", "items": [(name, value)]}] for every Java serialization stream in the APK's entries
    (assets / res/raw / dex byte[] literals / base64- or hex-wrapped text). [] when absent; never raises."""
    recs = []
    deadline = time.time() + _JSR_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if info.is_dir() or info.file_size > _JSR_MAX_ENTRY or time.time() > deadline:
                    continue
                try:
                    b = z.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile, zlib.error):
                    continue
                if _JSR_MAGIC not in b and b"rO0AB" not in b and not re.search(rb"(?i)aced0005", b):
                    continue
                for blob, off in _jsr_blobs(b):
                    items = java_serial_parse(blob, off)
                    if items:
                        recs.append({"entry": info.filename, "offset": off, "items": items})
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        pass
    return recs


def java_serial_scan(apk):
    """ANS tokens carried by a Java serialization stream (row 73): every string / char[] / byte[] / block-data value
    and "field=value" of java_serial_records(), read literally, then through decode_any (keyed by a key/secret/seed/
    salt-named field's value when present). [] when absent; never raises; < 1 s."""
    hits = []
    deadline = time.time() + _JSR_BUDGET_S
    try:
        for rec in java_serial_records(apk):
            vals, keys = [], []
            for name, v in rec["items"]:
                if isinstance(v, list) and v and all(isinstance(x, int) and 0 <= x < 256 for x in v):
                    v = bytes(v)
                if not isinstance(v, (str, bytes)) or not v:
                    continue
                vals.append(v)
                if _JSR_KEYISH.search(str(name).rsplit(".", 1)[-1]) and len(v) <= 64:
                    keys.append(v)
            for v in vals:
                hits += ANS_RE_T.findall(v if isinstance(v, str) else v.decode("latin-1"))
            if hits:
                continue
            budget = _JSR_DECODE_BUDGET
            for v in vals:
                if hits or budget <= 0 or time.time() > deadline:
                    break
                if not 8 <= len(v) <= 4096:
                    continue
                for k in [None, *keys[:4]]:
                    budget -= 1
                    r = decode_any(v, key=k, chain=False, cap=600)
                    if r:
                        hits += ANS_RE_T.findall(r)
                        break
    except Exception:  # noqa: BLE001 - never raise past the scan
        pass
    return list(dict.fromkeys(hits))


# --- JWT / JWE bearer tokens shipped in the app (coverage atlas row 74, MASVS-AUTH) ----------------------------------
# A hardcoded `eyJ...` token in a dex const-string, an asset / res/raw config, a resources.arsc string (UTF-8 or
# UTF-16) or .so rodata. Header + payload are base64url JSON: the answer may be a claim value (or the header's kid),
# read literally then through decode_any. Facts for the worker: alg "none" / empty signature, and which app string
# (dex / asset / arsc / .so, raw or its b64 / hex bytes, <= 2000) signs an HS256/384/512 token. JWE (5 parts): header
# only. Pure Python hmac / hashlib; every value is a candidate the GM judges.
_JWT_RE = re.compile(rb"eyJ[A-Za-z0-9_-]{4,16384}(?:\.[A-Za-z0-9_-]{0,65536}){2,4}")
_JWT_RE16 = re.compile(rb"e\x00y\x00J\x00(?:[A-Za-z0-9_.-]\x00){16,32768}")
_JWT_MAX_ENTRY, _JWT_MAX_TOKENS, _JWT_MAX_KEYS, _JWT_BUDGET_S, _JWT_DECODE_BUDGET = 32 << 20, 64, 2000, 1.0, 64
_JWT_HS = {"HS256": hashlib.sha256, "HS384": hashlib.sha384, "HS512": hashlib.sha512}
_JWT_DEXSTR = re.compile(rb"([\x01-\x7f])([\x20-\x7e]{1,127})\x00")
_JWT_CSTR = re.compile(rb"[\x20-\x7e]{4,256}(?=\x00)")
_JWT_QUOTED = re.compile(rb"[\"'`]([\x20-\x7e]{1,256}?)[\"'`]")
_JWT_PIECE = re.compile(rb"[^\s\"'`=:,;{}<>\[\]()]{4,256}")
_JWT_B64K = re.compile(r"[A-Za-z0-9+/_-]{16,}={0,2}")
_JWT_HEXK = re.compile(r"(?:[0-9a-fA-F]{2}){16,}")


def _jwt_b64(s):
    try:
        return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
    except (binascii.Error, ValueError):
        return None


def _jwt_obj(s):
    raw = _jwt_b64(s)
    try:
        return json.loads(raw.decode("utf-8")) if raw else None
    except (UnicodeDecodeError, ValueError):
        return None


def _jwt_parse(tok, entry):
    """One JWS (3 parts) / JWE (5 parts) record, or None when the header is not a JOSE JSON object."""
    parts = tok.split(".")
    for n in (3, 5) if len(parts) not in (3, 5) else (len(parts),):
        if len(parts) < n:
            continue
        ps = parts[:n]
        hdr = _jwt_obj(ps[0])
        if not isinstance(hdr, dict) or not ({"alg", "typ", "enc", "kid", "cty"} & set(hdr)):
            continue
        alg = str(hdr.get("alg", ""))
        rec = {"entry": entry, "token": ".".join(ps), "kind": "jwe" if n == 5 else "jws", "header": hdr,
               "payload": None, "alg": alg, "alg_none": alg.lower() == "none", "key": None}
        if n == 3:
            body = _jwt_b64(ps[1])
            rec["payload"] = _jwt_obj(ps[1])
            if rec["payload"] is None and body:
                rec["payload"] = body.decode("latin-1")
            rec["signature_empty"] = ps[2] == ""
        return rec
    return None


def _jwt_key_strs(name, b, out):
    """Candidate HMAC secrets from one entry's bytes (dex pool records, quoted / delimited text, NUL-terminated
    rodata, arsc pool strings), appended to `out` (a dict used as an ordered set)."""
    if b[:4] == b"dex\n":
        for m in _JWT_DEXSTR.finditer(b, 0x70):
            if m.group(1)[0] == len(m.group(2)):
                out.setdefault(m.group(2), None)
    elif name == "resources.arsc" or name.endswith(".xml") and b[:2] == b"\x03\x00":
        for s in _pool_strings(b)[:20000]:
            if 1 <= len(s) <= 256:
                out.setdefault(s.encode("utf-8", "ignore"), None)
    elif b[:4] == b"\x7fELF":
        for m in _JWT_CSTR.finditer(b):
            out.setdefault(m.group(0), None)
    else:
        head = b[:4096]
        if sum(32 <= c < 127 or c in (9, 10, 13) for c in head) < 0.9 * len(head):
            return
        for line in b.splitlines()[:20000]:
            s = line.strip()
            if 1 <= len(s) <= 256:
                out.setdefault(s, None)
            for m in _JWT_QUOTED.finditer(s):
                out.setdefault(m.group(1), None)
            for m in _JWT_PIECE.finditer(s):
                out.setdefault(m.group(0), None)


def _jwt_key_variants(k):
    """(label prefix, key bytes): the string itself, then its hex / base64(url) decoding when it has that shape."""
    yield "", k
    try:
        t = k.decode("ascii")
    except UnicodeDecodeError:
        return
    if _JWT_HEXK.fullmatch(t):
        yield "hex:", bytes.fromhex(t)
    if _JWT_B64K.fullmatch(t):
        raw = _jwt_b64(t.rstrip("=").translate(str.maketrans("+/", "-_")))
        if raw:
            yield "b64:", raw


def jwt_tokens(apk):
    """[{"entry", "token", "kind": jws|jwe, "header", "payload" (claims dict / text; None for JWE), "alg", "alg_none",
    "signature_empty", "key"}] for every JWT / JWE in the APK's entries (ASCII and UTF-16LE). "key" = the app string
    whose HMAC verifies an HS256/384/512 signature (str, or "hex:" / "b64:" + the string when its decoded bytes sign),
    tried over <= 2000 dex / asset / arsc / .so strings. [] when absent; never raises; < 1 s."""
    recs, seen = [], set()
    deadline = time.time() + _JWT_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            infos = [i for i in z.infolist() if not i.is_dir() and i.file_size <= _JWT_MAX_ENTRY]
            for info in infos:
                if len(recs) >= _JWT_MAX_TOKENS or time.time() > deadline:
                    break
                try:
                    b = z.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile, zlib.error):
                    continue
                toks = [m.group(0).decode() for m in _JWT_RE.finditer(b)] if b"eyJ" in b else []
                if b"e\x00y\x00J\x00" in b:
                    toks += [m.group(0).decode("utf-16-le") for m in _JWT_RE16.finditer(b)]
                for t in toks:
                    rec = _jwt_parse(t, info.filename)
                    if rec and rec["token"] not in seen and len(recs) < _JWT_MAX_TOKENS:
                        seen.add(rec["token"])
                        recs.append(rec)
            jwe = [r for r in recs if r["kind"] == "jwe" and r["alg"] in _JWE_KW and r["header"].get("enc") in _JWE_ENC]
            hs = [r for r in recs if r["kind"] == "jws" and r["alg"].upper() in _JWT_HS and not r["signature_empty"]]
            if not hs and not jwe:
                _jws_x5c(recs)
                return recs
            keys = {b"": None}
            for info in infos:
                if len(keys) > 4 * _JWT_MAX_KEYS or time.time() > deadline:
                    break
                try:
                    _jwt_key_strs(info.filename, z.read(info), keys)
                except (OSError, RuntimeError, zipfile.BadZipFile, zlib.error):
                    continue
        _jwe_open(jwe, keys, recs, seen, deadline)
        hs = [r for r in recs if r["kind"] == "jws" and r["alg"].upper() in _JWT_HS and not r["signature_empty"]]
        for r in hs:
            head, _, sig = r["token"].rpartition(".")
            want, fn = _jwt_b64(sig), _JWT_HS[r["alg"].upper()]
            if not want:
                continue
            for k in itertools.islice(keys, _JWT_MAX_KEYS):
                if r["key"] is not None or time.time() > deadline:
                    break
                for label, kb in _jwt_key_variants(k):
                    if hmac.compare_digest(hmac.new(kb, head.encode(), fn).digest(), want):
                        r["key"] = label + k.decode("utf-8", "replace")
                        break
        _jws_x5c(recs)
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        pass
    return recs


# --- JWE decryption + attestation (Play Integrity / SafetyNet) tokens (coverage atlas row 87, MASVS-RESILIENCE) -----
# A Play Integrity token is a JWE (A256KW + A256GCM) around an ES256 JWS; the app may ship the base64 decryption key
# (and verification key) beside it, so a JWE header alone hides the claims. _jwe_open tries every app string (raw, hex,
# base64 -- only when its length fits the alg) as the key-wrap key (RFC 3394, A128/192/256KW) or direct CEK, opens
# A*GCM / A*CBC-HS* (RFC 7518 5.2, AAD = protected header), inflates zip=DEF, and appends the inner JWS / claims as a
# record (entry "<entry>#jwe"; "jwe_key" on the JWE / "opened_by" on the inner record = the key label). _jws_x5c verifies an RS/PS/ES JWS against its x5c leaf
# ("x5c_verified", "x5c_chain_ok", "x5c_subject"). attestation_claims() reports the attestation verdict claims and
# compares the cert digest / package claims with the APK's own signer and package.
_JWE_KW = {"A128KW": 16, "A192KW": 24, "A256KW": 32, "dir": 0}
_JWE_ENC = {"A128GCM": 16, "A192GCM": 24, "A256GCM": 32, "A128CBC-HS256": 32, "A192CBC-HS384": 48, "A256CBC-HS512": 64}
_JWE_MAX_TRIES, _JWE_MAX_OUT = 4000, 1 << 20


def _jwe_unwrap(kek, w):
    """RFC 3394 AES key unwrap; None when the integrity check value does not match."""
    from Crypto.Cipher import AES
    n = len(w) // 8 - 1
    if len(w) % 8 or n < 2:
        return None
    a, r, ecb = w[:8], [w[8 * i + 8:8 * i + 16] for i in range(n)], AES.new(kek, AES.MODE_ECB)
    for j in range(5, -1, -1):
        for i in range(n, 0, -1):
            b = ecb.decrypt((int.from_bytes(a, "big") ^ (n * j + i)).to_bytes(8, "big") + r[i - 1])
            a, r[i - 1] = b[:8], b[8:]
    return b"".join(r) if a == b"\xa6" * 8 else None


def _jwe_decrypt(parts, hdr, kb):
    """Plaintext of a compact JWE under key bytes `kb`, or None (wrong key / length / tag)."""
    from Crypto.Cipher import AES
    alg, enc = hdr.get("alg"), hdr.get("enc")
    need = _JWE_ENC[enc]
    if alg == "dir":
        cek = kb if len(kb) == need else None
    else:
        ek = _jwt_b64(parts[1])
        cek = _jwe_unwrap(kb, ek) if len(kb) == _JWE_KW[alg] and ek else None
    if not cek or len(cek) != need:
        return None
    iv, ct, tag, aad = _jwt_b64(parts[2]), _jwt_b64(parts[3]), _jwt_b64(parts[4]), parts[0].encode()
    if iv is None or ct is None or not tag:
        return None
    try:
        if enc.endswith("GCM"):
            g = AES.new(cek, AES.MODE_GCM, nonce=iv)
            g.update(aad)
            pt = g.decrypt_and_verify(ct, tag)
        else:
            h = need // 2
            mac = hmac.new(cek[:h], aad + iv + ct + (len(aad) * 8).to_bytes(8, "big"),
                           {16: hashlib.sha256, 24: hashlib.sha384, 32: hashlib.sha512}[h]).digest()[:h]
            if len(iv) != 16 or not hmac.compare_digest(mac, tag) or not ct or len(ct) % 16:
                return None
            pt = AES.new(cek[h:], AES.MODE_CBC, iv=iv).decrypt(ct)
            if not 1 <= pt[-1] <= 16 or pt[-pt[-1]:] != bytes([pt[-1]]) * pt[-1]:
                return None
            pt = pt[:-pt[-1]]
        if hdr.get("zip") == "DEF":
            d = zlib.decompressobj(-15)
            pt = d.decompress(pt, _JWE_MAX_OUT)
    except (ValueError, KeyError, zlib.error):
        return None
    return pt


def _jwe_open(jwe, keys, recs, seen, deadline):
    """Decrypt each JWE record with the app's candidate key strings; inner JWS / JWE tokens become new records (one
    more level), a JSON / text plaintext becomes the JWE record's payload."""
    queue, depth = list(jwe), {id(r): 0 for r in jwe}
    while queue:
        r = queue.pop(0)
        parts, hdr = r["token"].split("."), r["header"]
        want = _JWE_ENC[hdr["enc"]] if hdr["alg"] == "dir" else _JWE_KW[hdr["alg"]]
        tries = 0
        for k in keys:
            if r.get("jwe_key") is not None or tries > _JWE_MAX_TRIES or time.time() > deadline:
                break
            for label, kb in _jwt_key_variants(k):
                if len(kb) != want:
                    continue
                tries += 1
                pt = _jwe_decrypt(parts, hdr, kb)
                if pt is None:
                    continue
                r["jwe_key"], r["plaintext"] = label + k.decode("utf-8", "replace"), pt.decode("latin-1")
                inner = [m.group(0).decode() for m in _JWT_RE.finditer(pt)]
                for t in inner:
                    sub = _jwt_parse(t, r["entry"] + "#jwe")
                    if sub and sub["token"] not in seen and len(recs) < _JWT_MAX_TOKENS:
                        seen.add(sub["token"])
                        sub["opened_by"] = r["jwe_key"]
                        recs.append(sub)
                        if sub["kind"] == "jwe" and depth[id(r)] < 1 and sub["alg"] in _JWE_KW \
                                and sub["header"].get("enc") in _JWE_ENC:
                            depth[id(sub)] = depth[id(r)] + 1
                            queue.append(sub)
                if not inner:
                    try:
                        r["payload"] = json.loads(pt.decode("utf-8"))
                    except (UnicodeDecodeError, ValueError):
                        r["payload"] = pt.decode("latin-1")
                break


def _jws_x5c(recs):
    """x5c_verified / x5c_chain_ok / x5c_subject on every RS* / PS* / ES* JWS whose header embeds a cert chain."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec, padding, utils
    for r in recs:
        x5c, alg = r["header"].get("x5c"), r["alg"]
        if r["kind"] != "jws" or not isinstance(x5c, list) or not x5c or alg[:2] not in ("RS", "PS", "ES"):
            continue
        r["x5c_verified"] = r["x5c_chain_ok"] = False
        try:
            certs = [x509.load_der_x509_certificate(base64.b64decode(c)) for c in x5c[:8]]
            r["x5c_subject"] = certs[0].subject.rfc4514_string()
            h = {"256": hashes.SHA256, "384": hashes.SHA384, "512": hashes.SHA512}[alg[2:]]()
            head, _, sig = r["token"].rpartition(".")
            sig, pub = _jwt_b64(sig) or b"", certs[0].public_key()
            if alg[:2] == "ES":
                n = len(sig) // 2
                sig = utils.encode_dss_signature(int.from_bytes(sig[:n], "big"), int.from_bytes(sig[n:], "big"))
                pub.verify(sig, head.encode(), ec.ECDSA(h))
            elif alg[:2] == "PS":
                pub.verify(sig, head.encode(), padding.PSS(padding.MGF1(h), h.digest_size), h)
            else:
                pub.verify(sig, head.encode(), padding.PKCS1v15(), h)
            r["x5c_verified"] = True
            for a, b in zip(certs, certs[1:]):
                a.verify_directly_issued_by(b)
            r["x5c_chain_ok"] = True
        except Exception:  # noqa: BLE001 - bad cert / signature / unsupported key
            continue


_ATT_KEYS = ("nonce", "apkPackageName", "apkDigestSha256", "apkCertificateDigestSha256", "ctsProfileMatch",
             "basicIntegrity", "evaluationType", "advice", "timestampMs", "requestPackageName", "timestampMillis",
             "requestHash", "packageName", "certificateSha256Digest", "versionCode", "appRecognitionVerdict",
             "deviceRecognitionVerdict", "appLicensingVerdict", "playProtectVerdict", "appsDetected")


def _att_walk(o, out, depth=0):
    if depth > 6 or not isinstance(o, dict):
        return
    for k, v in o.items():
        if k in _ATT_KEYS and k not in out:
            out[k] = v
        if isinstance(v, dict):
            _att_walk(v, out, depth + 1)


def attestation_claims(apk):
    """Play Integrity / SafetyNet attestation tokens shipped in the APK (row 87): [{"entry", "alg", "claims" (the
    verdict claims: nonce, apkPackageName / packageName, apkCertificateDigestSha256 / certificateSha256Digest,
    ctsProfileMatch, basicIntegrity, appRecognitionVerdict, deviceRecognitionVerdict ... found at any depth, e.g. under
    tokenPayloadExternal / requestDetails / appIntegrity), "nonce_bytes" (base64(url) decoded nonce), "cert_match"
    (a digest claim equals the APK signer's sha256; None when no signer / no claim), "package_match", "x5c_verified",
    "jwe_key"}] over jwt_tokens() (JWE opened with an app-shipped key). [] when absent; never raises."""
    out = []
    try:
        recs = [r for r in jwt_tokens(apk) if isinstance(r.get("payload"), dict)]
        rows = []
        for r in recs:
            c = {}
            _att_walk(r["payload"], c)
            if c:
                rows.append((r, c))
        if not rows:
            return []
        signers = {x["sha256"] for x in signing_certs(apk)}
        pkg = None
        with zipfile.ZipFile(apk) as z:
            if "AndroidManifest.xml" in z.namelist():
                b = z.read("AndroidManifest.xml")
                if b[:2] == b"\x03\x00":
                    pkg = next((t for t in _pool_strings(b)[:400] if _IDK_PKG.fullmatch(t) and not t.startswith(_IDK_SYS)), None)
        for r, c in rows:
            nb = None
            if isinstance(c.get("nonce"), str):
                nb = _jwt_b64(c["nonce"].rstrip("=").translate(str.maketrans("+/", "-_")))
            digs = c.get("apkCertificateDigestSha256") or c.get("certificateSha256Digest")
            digs = [digs] if isinstance(digs, str) else digs if isinstance(digs, list) else []
            hexes = set()
            for d in digs:
                d = str(d)
                if re.fullmatch(r"(?:[0-9a-fA-F]{2}:?){32}", d):
                    hexes.add(d.replace(":", "").lower())
                else:
                    raw = _jwt_b64(d.rstrip("=").translate(str.maketrans("+/", "-_")))
                    if raw and len(raw) == 32:
                        hexes.add(raw.hex())
            claim_pkg = c.get("apkPackageName") or c.get("packageName") or c.get("requestPackageName")
            out.append({"entry": r["entry"], "alg": r["alg"], "claims": c, "nonce_bytes": nb,
                        "cert_match": bool(hexes & signers) if hexes and signers else None,
                        "package_match": (claim_pkg == pkg) if claim_pkg and pkg else None,
                        "x5c_verified": r.get("x5c_verified"), "jwe_key": r.get("jwe_key") or r.get("opened_by")})
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        pass
    return out


# --- Play Integrity / SafetyNet verdict selection (coverage atlas row 87: play-integrity-verdict-select) -------------
# Several verdict blobs (plain JSON assets, JWS strings inside them, or tokens jwt_tokens() decodes / opens) may each be
# tied to an ANS value; the app's branch takes the strongest CLEAN one. A verdict root is a dict carrying requestDetails
# / appIntegrity / deviceIntegrity / accountDetails / tokenPayloadExternal or a legacy SafetyNet ctsProfileMatch /
# basicIntegrity; its "owner" is the largest enclosing subtree holding no other root, and the ANS strings in it (plain,
# else decode_any) are the root's value. Clean = PLAY_RECOGNIZED (when present), MEETS_DEVICE / MEETS_STRONG_INTEGRITY
# (when present), LICENSED (when present), ctsProfileMatch / basicIntegrity true (when present), cert digest = APK
# signer, package = manifest package, nonce = a host-side value (a dex / JSON string, its sha256) when any root's nonce
# matches one. Everything else is a decoy.
_IVS_ROOT = {"requestDetails", "appIntegrity", "deviceIntegrity", "accountDetails", "tokenPayloadExternal",
             "ctsProfileMatch", "basicIntegrity", "appRecognitionVerdict", "deviceRecognitionVerdict",
             "appLicensingVerdict"}
_IVS_MAX_ENTRY, _IVS_MAX_NODES, _IVS_MAX_HOST = 4 << 20, 50000, 20000
_IVS_HINT = re.compile(rb"RecognitionVerdict|ctsProfileMatch|tokenPayloadExternal|eyJ")
_IVS_JWS = re.compile(r"eyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*")


def _ivs_expand(o, budget, depth=0):
    """The JSON tree with every JWS string replaced by its decoded claims dict (unverified)."""
    budget[0] -= 1
    if depth > 14 or budget[0] < 0:
        return None
    if isinstance(o, dict):
        return {str(k): _ivs_expand(v, budget, depth + 1) for k, v in list(o.items())[:2000]}
    if isinstance(o, list):
        return [_ivs_expand(v, budget, depth + 1) for v in o[:2000]]
    if isinstance(o, str) and len(o) < 65536 and _IVS_JWS.fullmatch(o.strip()):
        rec = _jwt_parse(o.strip(), "")
        if rec and isinstance(rec.get("payload"), dict):
            budget[1].add(rec["token"])
            return {"_jws": _ivs_expand(rec["payload"], budget, depth + 1)}
    return o


def _ivs_roots(o, anc, out):
    if isinstance(o, dict):
        if _IVS_ROOT & set(o):
            out.append((o, list(anc)))
            return
        for v in o.values():
            _ivs_roots(v, anc + [o], out)
    elif isinstance(o, list):
        for v in o:
            _ivs_roots(v, anc + [o], out)


def _ivs_strings(o, out, depth=0, skip=()):
    """String leaves of a JSON tree (dict nodes whose id is in `skip` left out)."""
    if depth > 16 or len(out) > 4000:
        return
    if isinstance(o, dict):
        if id(o) in skip:
            return
        for v in o.values():
            _ivs_strings(v, out, depth + 1, skip)
    elif isinstance(o, list):
        for v in o:
            _ivs_strings(v, out, depth + 1, skip)
    elif isinstance(o, str):
        out.append(o)


def _ivs_bool(v):
    if isinstance(v, bool):
        return v
    return {"true": True, "false": False}.get(str(v).strip().lower()) if v is not None else None


def _ivs_digests(c):
    digs = c.get("apkCertificateDigestSha256") or c.get("certificateSha256Digest")
    digs = [digs] if isinstance(digs, str) else digs if isinstance(digs, list) else []
    hexes = set()
    for d in digs:
        d = str(d)
        if re.fullmatch(r"(?:[0-9a-fA-F]{2}:?){32}", d):
            hexes.add(d.replace(":", "").lower())
        else:
            raw = _jwt_b64(d.rstrip("=").translate(str.maketrans("+/", "-_")))
            if raw and len(raw) == 32:
                hexes.add(raw.hex())
    return hexes


def _ivs_judge(c):
    """(fails, score, verdict summary) of one claims dict, before the cert / package / nonce comparisons."""
    fails, score = [], 0
    app = c.get("appRecognitionVerdict")
    dev = c.get("deviceRecognitionVerdict")
    devs = {dev} if isinstance(dev, str) else {str(x) for x in dev} if isinstance(dev, list) else set()
    lic = c.get("appLicensingVerdict")
    cts, basic = _ivs_bool(c.get("ctsProfileMatch")), _ivs_bool(c.get("basicIntegrity"))
    if app is not None:
        if app == "PLAY_RECOGNIZED":
            score += 2
        else:
            fails.append("app:%s" % app)
    if dev is not None:
        if "MEETS_STRONG_INTEGRITY" in devs:
            score += 4
        elif "MEETS_DEVICE_INTEGRITY" in devs:
            score += 3
        else:
            fails.append("device:%s" % (",".join(sorted(devs)) or "none"))
    if lic is not None:
        if lic == "LICENSED":
            score += 1
        else:
            fails.append("licensing:%s" % lic)
    if "ctsProfileMatch" in c:
        score += 2 if cts else 0
        if not cts:
            fails.append("ctsProfileMatch:false")
    if "basicIntegrity" in c:
        score += 1 if basic else 0
        if not basic:
            fails.append("basicIntegrity:false")
    et = str(c.get("evaluationType") or "")
    if "HARDWARE_BACKED" in et:
        score += 1
    if not (app == "PLAY_RECOGNIZED" or devs & {"MEETS_DEVICE_INTEGRITY", "MEETS_STRONG_INTEGRITY"} or cts):
        fails.append("no-positive-verdict")
    return fails, score, {"app": app, "device": sorted(devs), "licensing": lic, "ctsProfileMatch": cts,
                          "basicIntegrity": basic, "evaluationType": et or None}


def _ivs_jwe_strs(tr):
    out = []
    _ivs_strings(tr, out)
    return [s for s in out if s.count(".") == 4]


def integrity_verdict_candidates(apk):
    """Every Play Integrity / SafetyNet verdict blob in the APK, ranked strongest clean first (row 87):
    [{"entry", "verdict" (app / device / licensing / ctsProfileMatch / basicIntegrity / evaluationType), "claims",
    "cert_match", "package_match", "nonce_match" (True / False / None = not comparable), "fails" ([] = clean),
    "clean", "score", "tokens" (ANS values tied to the blob)}]. [] when absent; never raises."""
    rows = []
    try:
        deadline = time.time() + 1.2
        trees, host, dex_has_jwt, used = [], [], False, set()
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if info.is_dir() or info.file_size > _IVS_MAX_ENTRY or time.time() > deadline:
                    continue
                n = info.filename
                isdex = re.fullmatch(r"classes\d*\.dex", n) is not None
                if not (isdex or n.endswith((".json", ".txt", ".jwt", ".jws")) or n.startswith(("assets/", "res/raw/"))):
                    continue
                try:
                    b = z.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile, zlib.error):
                    continue
                if isdex:
                    dex_has_jwt |= b"eyJ" in b
                    for m in _JWT_DEXSTR.finditer(b, 0x70):
                        if len(host) < _IVS_MAX_HOST and m.group(1)[0] == len(m.group(2)):
                            host.append(m.group(2).decode("ascii", "replace"))
                    continue
                for enc in ("utf-8-sig", "utf-16"):
                    try:
                        t = b.decode(enc).strip()
                        if t[:1] in "{[":
                            budget = [_IVS_MAX_NODES, used]
                            trees.append((n, _ivs_expand(json.loads(t), budget)))
                            break
                    except (UnicodeDecodeError, ValueError, RecursionError):
                        continue
                else:
                    dex_has_jwt |= b"eyJ" in b
            pkg = None
            if "AndroidManifest.xml" in z.namelist():
                b = z.read("AndroidManifest.xml")
                if b[:2] == b"\x03\x00":
                    pkg = next((t for t in _pool_strings(b)[:400] if _IDK_PKG.fullmatch(t) and not t.startswith(_IDK_SYS)), None)
        if dex_has_jwt or any("eyJ" in s for _, tr in trees for s in _ivs_jwe_strs(tr)):
            for r in jwt_tokens(apk):
                if isinstance(r.get("payload"), dict) and r["token"] not in used:
                    trees.append((r["entry"] + "#" + r["kind"], {"_jws": r["payload"]}))
        found = []
        for n, tr in trees:
            rs = []
            _ivs_roots(tr, [], rs)
            cnt = {}
            for root, anc in rs:
                for a in anc:
                    cnt[id(a)] = cnt.get(id(a), 0) + 1
            for root, anc in rs:
                owner = root
                for a in reversed(anc):
                    if cnt[id(a)] != 1:
                        break
                    owner = a
                found.append((n, root, owner))
            outside = []
            _ivs_strings(tr, outside, skip={id(root) for root, _ in rs})
            host += outside[:_IVS_MAX_HOST]
        if not found:
            return []
        hset = set(host)
        hdig = {hashlib.sha256(s.encode("utf-8", "ignore")).digest() for s in hset if s}
        hhex = {d.hex() for d in hdig}
        signers = {x["sha256"] for x in signing_certs(apk)}
        for n, root, owner in found:
            c = {}
            _att_walk(root, c)
            fails, score, verdict = _ivs_judge(c)
            hexes = _ivs_digests(c)
            cert = bool(hexes & signers) if hexes and signers else None
            claim_pkg = c.get("apkPackageName") or c.get("packageName") or c.get("requestPackageName")
            pmatch = (claim_pkg == pkg) if claim_pkg and pkg else None
            nonce, nmatch = c.get("nonce"), None
            if isinstance(nonce, str) and nonce.strip() and hset:
                nonce = nonce.strip()
                nb = _jwt_b64(nonce.rstrip("=").translate(str.maketrans("+/", "-_")))
                nmatch = nonce in hset or nonce.lower() in hhex or nb is not None and (
                    nb in hdig or nb.decode("latin-1") in hset)
            strs = []
            _ivs_strings(owner, strs)
            toks = [t for s in strs for t in ANS_RE_T.findall(s)]
            if not toks:
                for s in strs[:32]:
                    if 16 <= len(s) <= 1024 and time.time() < deadline + 0.4:
                        toks += ANS_RE_T.findall(decode_any(s, depth=2, cap=600, chain=False) or "")
            if cert is False:
                fails.append("cert-mismatch")
            if pmatch is False:
                fails.append("package-mismatch")
            score += 2 * (cert is True) + 2 * (nmatch is True) + (pmatch is True)
            rows.append({"entry": n, "verdict": verdict, "claims": c, "cert_match": cert, "package_match": pmatch,
                         "nonce_match": nmatch, "fails": fails, "score": score, "tokens": list(dict.fromkeys(toks))})
        if any(r["nonce_match"] is True for r in rows):
            for r in rows:
                if r["nonce_match"] is not True:
                    r["fails"].append("nonce-mismatch" if r["nonce_match"] is False else "nonce-unmatched")
        for r in rows:
            r["clean"] = not r["fails"]
        rows.sort(key=lambda r: (not r["clean"], -r["score"]))
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        return []
    return rows


def integrity_verdict_scan(apk):
    """ANS values tied to the clean Play Integrity / SafetyNet verdict blobs, strongest first (row 87); decoy verdicts
    (UNRECOGNIZED_VERSION / UNEVALUATED, MEETS_BASIC / VIRTUAL only, UNLICENSED, cts false, foreign cert digest, wrong
    nonce) contribute nothing. [] when absent; never raises."""
    out = []
    for r in integrity_verdict_candidates(apk):
        if r.get("clean"):
            out += [t for t in r["tokens"] if t not in out]
    return out


def _jwt_values(o, out, depth=0):
    if depth > 8 or len(out) > 256:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            out.append(str(k))
            _jwt_values(v, out, depth + 1)
    elif isinstance(o, list):
        for v in o:
            _jwt_values(v, out, depth + 1)
    elif o is not None:
        out.append(str(o))


def jwt_scan(apk):
    """ANS tokens carried by a JWT / JWE shipped in the APK (row 74): header + claim values of jwt_tokens() read
    literally, then each string claim through decode_any (keyed by the verified HMAC secret when one signs it).
    [] when absent; never raises; < 1 s."""
    hits = []
    deadline = time.time() + _JWT_BUDGET_S
    try:
        recs = jwt_tokens(apk)
        vals = []
        for r in recs:
            vs = []
            _jwt_values(r["header"], vs)
            _jwt_values(r["payload"], vs)
            vals.append((r, vs))
            for v in vs:
                hits += ANS_RE_T.findall(v)
        if hits:
            return list(dict.fromkeys(hits))
        budget = _JWT_DECODE_BUDGET
        for r, vs in vals:
            key = r["key"].split(":", 1)[-1] if r["key"] and r["key"][:4] in ("hex:", "b64:") else r["key"]
            for v in vs:
                if budget <= 0 or time.time() > deadline:
                    break
                if not 8 <= len(v) <= 4096:
                    continue
                for k in (None, key) if key else (None,):
                    budget -= 1
                    got = decode_any(v, key=k, chain=False, cap=600)
                    if got:
                        hits += ANS_RE_T.findall(got)
                        break
    except Exception:  # noqa: BLE001 - never raise past the scan
        pass
    return list(dict.fromkeys(hits))


# --- schema-less protobuf assets (coverage atlas row 75) -------------------------------------------------------------
# An app keeps its config / state as a serialized protobuf message (assets/*.pb|bin, res/raw/, or a base64 / hex text
# blob of one) read through GeneratedMessageLite, so the token sits in a LEN field of a message nobody has the .proto
# for. Generic wire walk over the aapt2 reader's _pb_fields: a blob counts only when it is consumed exactly (no
# trailing bytes, sane field numbers, wire types 0/1/2/5), each LEN value is tried as a nested message first (depth
# <= 8), and is ALSO kept as a UTF-8 string when it reads as text, else as bytes. Leaves go to the ANS regex, the
# concatenation of a message's sibling strings (split token), then decode_any keyed by a sibling string (xor key field).
_PBA_MAX_ENTRY, _PBA_DEPTH, _PBA_LEAVES, _PBA_BUDGET_S, _PBA_DECODE_BUDGET = 4 << 20, 8, 4096, 1.0, 64
_PBA_SKIP = re.compile(r"(?:classes\d*\.dex|resources\.arsc|AndroidManifest\.xml|META-INF/.*|.*\.(?:so|png|jpe?g|webp|"
                       r"gif|ogg|mp3|ttf|otf|kotlin_builtins|kotlin_module|version|properties))$", re.I)
_PBA_TEXT = re.compile(r"[^\x00-\x08\x0b\x0c\x0e-\x1f\x7f]*")
_PBA_BLOB = re.compile(rb"[A-Za-z0-9+/_\-]{16,}={0,2}|(?:[0-9a-fA-F]{2}){8,}")


def _pba_msg(b):
    """Fields of `b` when it is one complete, plausible protobuf message; else None."""
    if not b or len(b) > _PBA_MAX_ENTRY:
        return None
    try:
        fs = _pb_fields(b)
    except (ValueError, IndexError):
        return None
    if not fs or any(fn > 0x1FFFFFFF or (fn > 4096 and len(fs) < 4) for fn, _, _ in fs):
        return None
    return fs


def _pba_text(v):
    try:
        s = v.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if s and _PBA_TEXT.fullmatch(s) and sum(c.isprintable() or c.isspace() for c in s) == len(s) else None


def _pba_walk(fs, path, depth, out, groups):
    sibs = []
    for fn, wt, v in fs:
        p = f"{path}.{fn}" if path else str(fn)
        if len(out) >= _PBA_LEAVES:
            return
        if wt != 2:
            out.append((p, v if isinstance(v, int) else int.from_bytes(v, "little")))
            continue
        s = _pba_text(v)
        sub = _pba_msg(v) if depth < _PBA_DEPTH and len(v) >= 2 else None
        if sub is not None and not (s is not None and len(sub) == 1 and sub[0][1] != 2):
            _pba_walk(sub, p, depth + 1, out, groups)
        if s is not None:
            out.append((p, s))
            sibs.append(s)
        elif sub is None:
            out.append((p, bytes(v)))
    if len(sibs) >= 2:
        groups.append(sibs)


def protobuf_fields(data):
    """Schema-less decode of one serialized protobuf message: [(field path "1.3.2", value)] where value is a str (LEN
    field that reads as UTF-8 text), bytes (other LEN leaves) or int (varint / fixed32 / fixed64, little-endian). LEN
    fields that parse as a complete nested message are walked (depth <= 8) and, when also text, kept as the string.
    None unless `data` is consumed exactly as wire format. Never raises."""
    try:
        fs = _pba_msg(bytes(data))
        if fs is None:
            return None
        out = []
        _pba_walk(fs, "", 1, out, [])
        return out
    except Exception:  # noqa: BLE001 - not a protobuf message
        return None


def _pba_blobs(name, b):
    """(label, candidate message bytes) of an entry: the bytes themselves, then base64 / hex text runs inside it."""
    yield name, b
    for m in _PBA_BLOB.finditer(b[:1 << 20]):
        t = m.group(0)
        for fn in (lambda x: binascii.unhexlify(x) if re.fullmatch(rb"(?:[0-9a-fA-F]{2})+", x) else None,
                   _b64ish, lambda x: _b64ish(x, True)):
            try:
                r = fn(t)
            except (binascii.Error, ValueError):
                r = None
            if r and len(r) >= 4:
                yield f"{name}@{m.start()}", r


def protobuf_asset_scan(apk):
    """ANS tokens inside schema-less protobuf messages shipped in the APK (row 75): every non-code entry (assets/,
    res/raw/, any path), and every base64 / hex run inside one, that parses completely as wire format (two or more
    fields, or one LEN field) is walked by protobuf_fields; string / bytes leaves are read for a literal token, then a
    message's sibling strings joined (split token), then each leaf through decode_any (unkeyed, then keyed by each
    sibling string). [] when absent; never raises; < 1 s."""
    hits, leaves, seen = [], [], set()
    deadline = time.time() + _PBA_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if time.time() > deadline:
                    break
                if info.is_dir() or info.file_size > _PBA_MAX_ENTRY or _PBA_SKIP.fullmatch(info.filename):
                    continue
                try:
                    b = z.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile, zlib.error, NotImplementedError):
                    continue
                for label, blob in _pba_blobs(info.filename, b):
                    if time.time() > deadline:
                        break
                    if blob in seen:
                        continue
                    seen.add(blob)
                    fs = _pba_msg(blob)
                    if fs is None or (len(fs) < 2 and fs[0][1] != 2):
                        continue
                    out, groups = [], []
                    _pba_walk(fs, "", 1, out, groups)
                    if not any(isinstance(v, (str, bytes)) for _, v in out):
                        continue
                    leaves.append((label, out, groups))
        for _label, out, groups in leaves:
            for _p, v in out:
                if isinstance(v, (str, bytes)):
                    t = v if isinstance(v, str) else v.decode("latin-1")
                    hits += [x for x in ANS_RE_T.findall(t) if x not in hits]
            for g in groups:
                hits += [x for x in ANS_RE_T.findall("".join(g)) if x not in hits]
        if hits:
            return hits
        budget = _PBA_DECODE_BUDGET
        for _label, out, groups in leaves:
            strs = [v for _, v in out if isinstance(v, str) and 4 <= len(v) <= 256]
            keys = list(dict.fromkeys(s for s in strs if len(s) <= 64))[:6]
            for _p, v in out:
                if budget <= 0 or time.time() > deadline:
                    break
                if isinstance(v, int) or not 8 <= len(v) <= 4096:
                    continue
                for k in [None] + [x for x in keys if x != v]:
                    if budget <= 0 or time.time() > deadline:
                        break
                    budget -= 1
                    got = decode_any(v, key=k, depth=2 if k else 3, cap=400, chain=False)
                    if got:
                        hits += [x for x in ANS_RE_T.findall(got) if x not in hits]
                        break
                if hits:
                    return hits
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return hits


# --- entry-reachable call graph over generated look-alike classes (coverage atlas row 78) -----------------------------
# N structurally equivalent classes/methods each hold an ANS- literal; only one is wired from the entry activity
# (direct call, reflective Class.forName/getDeclaredMethod, const-class, Proxy handler or virtual dispatch to the one
# concrete subclass that is instantiated). Rapid-type-analysis reachability from ChallengeActivity / MainActivity / the
# manifest's activities; unreachable twins are decoys.
_ERC_PRE = re.compile(rb"ANS-")
_ERC_BUDGET_S, _ERC_MAX_DEX, _ERC_UNITS = 0.9, 32 << 20, 1_500_000
_ERC_ENTRY = re.compile(r"(?i)/(?:challenge|main)activity;$")
_ERC_REFL = re.compile(r"^Ljava/lang/(?:Class;->(?:forName|getDeclaredMethods?|getMethods?|newInstance|getDeclaredConstructor"
                       r"|getConstructor)|ClassLoader;->loadClass|reflect/Proxy;->newProxyInstance)\(")
_ERC_CB = frozenset(("run", "call", "invoke", "apply", "accept", "get", "onClick", "handleMessage", "onReceive",
                     "doInBackground", "onPostExecute", "compare", "test", "onCreate", "onStart", "onResume"))


def _erc_ops(dx, ins):
    """One method body -> (opcode tuple, [(virtual?, ref)], [str], {type}, {field class})."""
    ops, calls, strs, types, fcls = [], [], [], set(), set()
    pc, n = 0, len(ins) // 2
    while pc < n:
        p = 2 * pc
        op, b1 = ins[p], ins[p + 1]
        if op == 0 and b1 in (1, 2, 3) and p + 8 <= len(ins):
            k = struct.unpack_from("<H", ins, p + 2)[0]
            if b1 == 3:
                w, cnt = struct.unpack_from("<HI", ins, p + 2)
                pc += 4 + (w * cnt + 1) // 2
            else:
                pc += (4 + 2 * k) if b1 == 1 else (2 + 4 * k)
            continue
        w = _DOP_W[op]
        if p + 2 * w > len(ins):
            break
        ops.append(op)
        if op in (0x1A, 0x1B):
            strs.append(dx.s(struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0]))
        elif op in (0x1C, 0x22):
            types.add(dx.typ(struct.unpack_from("<H", ins, p + 2)[0]))
        elif 0x52 <= op <= 0x6D:
            fi = struct.unpack_from("<H", ins, p + 2)[0]
            if fi < dx.n_fld:
                fcls.add(dx.fref(fi)[0])
        elif 0x6E <= op <= 0x72 or 0x74 <= op <= 0x78:
            mi = struct.unpack_from("<H", ins, p + 2)[0]
            if mi < dx.n_met:
                calls.append((op in (0x6E, 0x72, 0x74, 0x78), dx.mref(mi)))
        pc += w
    return tuple(ops), calls, strs, types, fcls


def _erc_names(s):
    """A reflective string's readings: as-is, reversed, Base64."""
    out = {s, s[::-1]}
    if re.fullmatch(r"[A-Za-z0-9+/]{4,}={0,2}", s) and len(s) % 4 == 0:
        try:
            out.add(base64.b64decode(s).decode())
        except (ValueError, UnicodeDecodeError):
            pass
    return out


class _ErcVM(_RflVM):
    """_RflVM that records which classes / methods the reflective lookups resolved to."""

    def __init__(self, dx, deadline, rec):
        super().__init__(dx, deadline)
        self.rec = rec

    def _cls(self, v):
        t = super()._cls(v)
        self.rec.add(("cls", t))
        return t

    def _methods(self, ct, mn, n):
        r = super()._methods(ct, mn, n)
        self.rec.update(("m", m) for m in r)
        return r


def _erc_manifest(z):
    try:
        b = z.read("AndroidManifest.xml")
    except KeyError:
        return set()
    out = set()
    try:
        for kind, tag, attrs, _ in (_axml_events(b) if b[:2] == b"\x03\x00" else ()):
            if kind == "start" and tag in ("activity", "activity-alias") and attrs:
                for k, v in attrs.items():
                    if k.split(":")[-1] in ("name", "targetActivity") and isinstance(v, str) and v:
                        out.add(v.lstrip(".").replace(".", "/") + ";")
    except Exception:  # noqa: BLE001 - a broken manifest just means name-based entries
        pass
    return out


def _erc_dex(d, deadline, manifest, budget):
    """One dex -> candidate dicts {value, method, reachable, twins} (twins = structurally equivalent methods)."""
    dx = _DxDex(d)
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_cls, o_cls = u32(0x60), u32(0x64)
    sup = {}
    for c in range(n_cls):
        base = o_cls + 32 * c
        ifs, io = [], u32(base + 12)
        if io and io + 4 <= len(d):
            k = min(u32(io), 64)
            ifs = [dx.typ(t) for t in struct.unpack_from(f"<{k}H", d, io + 4)] if io + 4 + 2 * k <= len(d) else []
        sc = u32(base + 8)
        sup[dx.typ(u32(base))] = ([dx.typ(sc)] if sc != 0xFFFFFFFF else []) + ifs
    by_cls, info = {}, {}
    for ref, (_, _, ins, _) in dx.code.items():
        budget[0] -= len(ins) // 2
        if budget[0] < 0 or time.time() > deadline:
            return []
        by_cls.setdefault(ref.split("->")[0], []).append(ref)
        info[ref] = _erc_ops(dx, ins)

    @lru_cache(maxsize=None)
    def supers(t):
        seen, todo = set(), [t]
        while todo and len(seen) < 256:
            x = todo.pop()
            if x not in seen:
                seen.add(x)
                todo += sup.get(x, [])
        return frozenset(seen)

    def resolve(t, sig):
        x = t
        for _ in range(32):
            if f"{x}->{sig}" in dx.code:
                return f"{x}->{sig}"
            s = sup.get(x)
            if not s:
                return None
            x = s[0]
        return None

    reached, inst, vsites, work = set(), set(), set(), []

    def reach(ref):
        if ref and ref in dx.code and ref not in reached:
            reached.add(ref)
            work.append(ref)

    def instantiate(t):
        if t in inst or t not in sup:
            return
        inst.add(t)
        reach(dx.clinit.get(t))
        for c, sig in list(vsites):
            if c in supers(t):
                reach(resolve(t, sig))
        if any(s not in sup and s != "Ljava/lang/Object;" for s in supers(t)):
            for ref in by_cls.get(t, ()):  # framework callback overrides (Runnable.run, OnClickListener, ...)
                if ref.split("->")[1].split("(")[0] in _ERC_CB:
                    reach(ref)

    entries = [t for t in sup if _ERC_ENTRY.search(t) or any(t.endswith("/" + m) or t == "L" + m for m in manifest)]
    for t in entries:
        instantiate(t)
        for ref in by_cls.get(t, ()):
            reach(ref)
    while work:
        if time.time() > deadline:
            return []
        ref = work.pop()
        ct = ref.split("->")[0]
        _, calls, strs, types, fcls = info[ref]
        reach(dx.clinit.get(ct))
        for t in types:
            instantiate(t)
        for t in fcls:
            reach(dx.clinit.get(t))
        refl = False
        for virt, m in calls:
            c, sig = m.split("->", 1)
            if _ERC_REFL.match(m):
                refl = True
            if sig == "invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;":
                refl = True
            if virt:
                if (c, sig) not in vsites:
                    vsites.add((c, sig))
                    for t in list(inst):
                        if c in supers(t):
                            reach(resolve(t, sig))
            else:
                reach(m)
                reach(dx.clinit.get(c))
        if "Ljava/lang/reflect/Proxy;->newProxyInstance" in " ".join(m for _, m in calls):
            vsites.add(("Ljava/lang/reflect/InvocationHandler;",
                        "invoke(Ljava/lang/Object;Ljava/lang/reflect/Method;[Ljava/lang/Object;)Ljava/lang/Object;"))
            for t in list(inst):
                inst.discard(t)
                instantiate(t)
        if refl:
            rec = set()
            names = {x for s in strs if s for x in _erc_names(s)}
            for x in names:
                t = "L" + x.replace(".", "/") + ";"
                if t in sup:
                    rec.add(("cls", t))
            try:
                nreg, nin, _, acc = dx.code[ref]
                ps = _dxe_params(ref)
                if len(ps) <= 4 and nin <= nreg:
                    vm = _ErcVM(dx, min(deadline, time.time() + 0.15), rec)
                    raw = [] if acc & 0x8 else [_DxObj(ct)]
                    for p in ps:
                        raw += [_dxe_default(p)] + ([None] if p in "JD" else [])
                    vm.init_class(ct)
                    vm.run(ref, raw)
            except Exception:  # noqa: BLE001 - the VM is a best-effort resolver; string readings stay
                pass
            for kind, v in rec:
                if kind == "m":
                    reach(v)
                    continue
                instantiate(v)
                ms = [r for r in by_cls.get(v, ()) if r.split("->")[1].split("(")[0] in names]
                for r in ms or by_cls.get(v, ()):
                    reach(r)

    def tokens(ref):
        _, _, strs, _, fcls = info[ref]
        out = [m for s in strs if s for m in ANS_RE_T.findall(s)]
        if not out and ref.endswith(")Ljava/lang/String;") and time.time() < deadline:
            try:
                nreg, nin, _, acc = dx.code[ref]
                if not _dxe_params(ref) and nin <= nreg:
                    vm = _DxVM(dx, min(deadline, time.time() + 0.05))
                    vm.init_class(ref.split("->")[0])
                    v = vm.run(ref, [] if acc & 0x8 else [_DxObj(ref.split("->")[0])])
                    out = ANS_RE_T.findall(v) if isinstance(v, str) else []
            except Exception:  # noqa: BLE001
                pass
        return out

    groups = {}
    for ref in dx.code:
        if not _DXE_LIB.match(ref) and len(info[ref][0]) >= 2:
            groups.setdefault(info[ref][0], []).append(ref)
    out = []
    for ref in dx.code:
        if _DXE_LIB.match(ref):
            continue
        toks = tokens(ref) if ref in reached or ANS_RE_T.search(" ".join(s for s in info[ref][2] if s)) else []
        twins = [r for r in groups.get(info[ref][0], ()) if r != ref and r.split("->")[0] != ref.split("->")[0]]
        for tok in toks:
            out.append({"value": tok, "method": ref, "reachable": ref in reached, "twins": len(twins),
                        "twins_reached": sum(r in reached for r in twins)})
    return out


def entry_reachable_candidates(apk):
    """Every ANS literal (or zero-arg String method's computed value) of the APK's dexes as {value, method, reachable,
    twins, twins_reached}: `reachable` = its method is reached from the entry activities by rapid type analysis (direct
    / static calls, virtual dispatch to instantiated subclasses, const-class, Class.forName / getDeclaredMethod names
    as literals, reversed, Base64 or computed by the reflection interpreter, Proxy handlers, <clinit>s). Reachable ones
    first, the sole reached member of a twin group (same opcode sequence across look-alike classes) leading. [] when
    absent; never raises; ~0.9 s bound."""
    out = []
    deadline = time.time() + _ERC_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            manifest = _erc_manifest(z)
            budget = [_ERC_UNITS]
            for i in z.infolist():
                if i.file_size > _ERC_MAX_DEX or not re.fullmatch(r"classes\d*\.dex", Path(i.filename).name):
                    continue
                d = z.read(i)
                if d[:4] == b"dex\n" and len(d) >= 0x70 and _ERC_PRE.search(d) and time.time() < deadline:
                    try:
                        out += _erc_dex(d, deadline, manifest, budget)
                    except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                        continue
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        return []
    out.sort(key=lambda c: (not c["reachable"], not (c["twins"] and c["twins_reached"] == 0)))
    return out


def entry_reachable_scan(apk):
    """Only the ANS values whose method is reachable from the entry activities (see entry_reachable_candidates);
    unreachable look-alike twins are decoys. [] when absent."""
    return list(dict.fromkeys(c["value"] for c in entry_reachable_candidates(apk) if c["reachable"]))


# --- entry-anchored candidate veto (coverage atlas row 98) ------------------------------------------------------------
# D23 v2: Release.code() builds "ANS-" + "0123456789ABCDEF".charAt(x >>> i & 15) over a mixer chain, next to unreferenced
# look-alike mixers (sealTrampolineNN / sealHookNN / K* longs). The shape-only composers (split_native_assembly,
# digest_answer_scan, ans_compose_scan) turn that into ANS-0123456789ABCDEF (the harness placeholder too) and several
# ANS-shaped decoys. Veto: never the hex alphabet; a value the entry method actually computes (proof_flow_scan / the
# deep evaluator over entry-reachable static String methods) replaces every shape-only candidate; compose candidates of
# methods unreachable from the entry activities (callers all dead included) go last.
_EAV_ALPHA = frozenset(("0123456789ABCDEF", "FEDCBA9876543210"))
_EAV_BUDGET_S, _EAV_UNITS = 0.4, 2_000_000


def _eav_alphabet(c):
    """True for ANS-<the hex digit table> (a lookup-table const, never a token)."""
    return isinstance(c, str) and c[4:].upper() in _EAV_ALPHA


def _eav_table_walk(dx, ins):
    """True when a method spells its hex through the "0123456789ABCDEF" table AND calls in-dex code: its numeric
    constants are mixer inputs, not the printed value (D23 Release.code), so composing "ANS-" + a constant is a decoy."""
    if b"0123456789" not in dx.d and b"0123456789abcdef" not in dx.d:
        return False
    try:
        _, calls, strs, _, _ = _erc_ops(dx, ins)
    except Exception:  # noqa: BLE001
        return False
    return any(s and s.upper() in _EAV_ALPHA for s in strs) and any(m in dx.code for _, m in calls)


def _eav_reached(dx, deadline=None):
    """App method refs reached from ChallengeActivity / MainActivity (by class name) over static and virtual call edges
    -- a virtual / unresolved call reaches every app method with that name+signature, a new-instance / const-class every
    method of that class, a touched class its <clinit> -- over-approximate so a live method is never called dead. None
    (= no verdict, demote nothing) without an entry class, on reflection / MethodHandle / Proxy use, or out of budget."""
    try:
        entries = [r for r in dx.code if _ERC_ENTRY.search(r.split("->")[0])]
        if not entries:
            return None
        deadline = min(deadline or 1e18, time.time() + _EAV_BUDGET_S)
        by_sig, by_cls = {}, {}
        for r in dx.code:
            c, sig = r.split("->", 1)
            by_sig.setdefault(sig, []).append(r)
            by_cls.setdefault(c, []).append(r)
        reached, work, units = set(), list(entries), 0
        while work:
            ref = work.pop()
            if ref in reached or ref not in dx.code:
                continue
            reached.add(ref)
            ins = dx.code[ref][2]
            units += len(ins) // 2
            if units > _EAV_UNITS or time.time() > deadline:
                return None
            _, calls, _, types, fcls = _erc_ops(dx, ins)
            nxt = [dx.clinit.get(ref.split("->")[0])]
            for virt, m in calls:
                if _ERC_REFL.match(m) or "Ljava/lang/invoke/" in m or "Ljava/lang/reflect/Proxy;" in m:
                    return None
                c, sig = m.split("->", 1)
                nxt.append(dx.clinit.get(c))
                nxt += by_sig.get(sig, ()) if virt or m not in dx.code else (m,)
            for t in types:
                nxt += by_cls.get(t, ())
            nxt += [dx.clinit.get(t) for t in fcls]
            work += [r for r in nxt if r and r not in reached]
        return reached
    except Exception:  # noqa: BLE001 - a malformed dex gives no verdict
        return None


def entry_evaluated_values(apk):
    """ANS values the entry path itself produces: proof_flow_scan() (the request builder's `proof=` value), else the deep
    evaluator's returns of static String methods reachable from ChallengeActivity / MainActivity. Hex-alphabet never.
    [] when absent; never raises."""
    try:
        vals = proof_flow_scan(apk) or _dex_eval_deep(apk, entry_only=True)
    except Exception:  # noqa: BLE001
        vals = []
    return [v for v in dict.fromkeys(vals) if not _eav_alphabet(v)]


def _eav_anchor(apk, hits):
    """Shape-only candidates -> the entry-evaluated value(s) when the entry path computes one (those already among the
    hits first), else the hits minus the hex alphabet."""
    hits = [h for h in hits or () if not _eav_alphabet(h)]
    if not hits:
        return hits
    ev = entry_evaluated_values(apk)
    if not ev:
        return hits
    return list(dict.fromkeys([h for h in hits if h in ev] + ev))


# --- native code calling back into Java by name: FindClass / GetStaticMethodID (coverage atlas row 82) ----------------
# A Java_* / JNI_OnLoad / RegisterNatives body does FindClass("com/x/K") + Get[Static]MethodID(k, "q", "(...)L...;")
# + NewStringUTF("<literal>") + Call[Static]ObjectMethod(k, m, arg): the answer is what the NAMED Java method computes
# from the native's literal args (dex_eval_scan runs it with "" args and gets nothing). Strings are collected from the
# function bodies in code order (x86_64 `lea r, [rip+d]`, arm64 `adrp`+`add` / `adr`), classified by shape (class
# path / descriptor / identifier / literal), paired by proximity, and the dex method is run by the _DxVM with the
# literal args (every ordering, bounded); the literals' own tokens are returned too.
_JCB_CLASS = re.compile(r"[A-Za-z_$][\w$]*(?:/[A-Za-z_$][\w$]*)+")
_JCB_SIG = re.compile(r"\((?:\[*(?:[ZBSCIJFD]|L[\w$/]+;))*\)\[*(?:[ZBSCIJFDV]|L[\w$/]+;)")
_JCB_NAME = re.compile(r"[A-Za-z_$][\w$]*")
_JCB_MAX_SO, _JCB_FUNCS, _JCB_FN_BYTES, _JCB_BUDGET_S, _JCB_TRIES = 8, 48, 8192, 1.0, 24
_JCB_RIP = re.compile(r"\[rip ([+-]) (0x[0-9a-f]+|\d+)\]")


def _jcb_str(elf, va):
    s = elf.at(va, 256).split(b"\0")[0]
    if 1 <= len(s) < 256 and all(0x20 <= c < 0x7F for c in s):
        return s.decode()
    return None


def _jcb_refs(elf, md, va, size):
    """Printable C strings a function body addresses, in code order."""
    out, pages = [], {}
    code = elf.at(va, min(size or _JCB_FN_BYTES, _JCB_FN_BYTES))
    for ins in md.disasm(code, va):
        mn, ops, tgt = ins.mnemonic, ins.op_str, None
        if mn == "lea":
            m = _JCB_RIP.search(ops)
            if m:
                d = int(m.group(2), 0)
                tgt = ins.address + ins.size + (d if m.group(1) == "+" else -d)
        elif mn in ("adrp", "adr"):
            r, _, imm = ops.partition(", #")
            try:
                if mn == "adrp":
                    pages[r] = int(imm, 0)
                else:
                    tgt = int(imm, 0)
            except ValueError:
                pass
        elif mn == "add" and ops.count(", ") == 2:
            rd, rn, imm = ops.split(", ")
            if rn in pages and imm.startswith("#"):
                try:
                    tgt = pages[rn] + int(imm[1:], 0)
                except ValueError:
                    pass
        elif mn in ("ret", "retq") and out and size == 0:
            break
        if tgt is not None:
            s = _jcb_str(elf, tgt)
            if s is not None and (not out or out[-1] != s):
                out.append(s)
    return out


def _jcb_pair(refs):
    """[(class, name, sig, literals)] from one function's ordered strings."""
    kind = ["c" if _JCB_CLASS.fullmatch(s) else "s" if _JCB_SIG.fullmatch(s) else "n" if _JCB_NAME.fullmatch(s) else "l"
            for s in refs]
    used, out = set(), []
    for i, k in enumerate(kind):
        if k != "s":
            continue
        names = sorted((j for j, kj in enumerate(kind) if kj == "n" and j not in used), key=lambda j: (abs(j - i), j > i))
        cls = [j for j in range(i - 1, -1, -1) if kind[j] == "c"] or [j for j, kj in enumerate(kind) if kj == "c"]
        if names and cls:
            used.update((i, names[0]))
            out.append([refs[cls[0]], refs[names[0]], refs[i]])
    lits = [s for j, s in enumerate(refs) if j not in used and kind[j] in ("l", "n")]
    return [(c, n, s, lits) for c, n, s in out]


def jni_callbacks(apk):
    """Native -> Java callbacks named in each x86_64 / arm64 lib/*/*.so: [{"so", "class", "name", "sig", "args"}]
    (args = the function's other string literals, the NewStringUTF candidates). [] when none; never raises."""
    out, deadline = [], time.time() + _JCB_BUDGET_S
    try:
        import capstone
        with zipfile.ZipFile(apk) as z:
            sos = [i for i in z.infolist() if i.filename.startswith("lib/") and i.filename.endswith(".so")
                   and i.file_size <= _NSO_MAX_BYTES][:_JCB_MAX_SO]
            dex = b"".join(z.read(i) for i in z.infolist() if re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)
                           and i.file_size <= _DXE_MAX_DEX)
            for info in sos:
                if time.time() > deadline:
                    break
                try:
                    elf = _NsoElf(z.read(info))
                    if not elf.is64 or elf.arch not in ("EM_X86_64", "EM_AARCH64"):
                        continue
                    _, (ca, cm), *_ = _NSO_ARCH[elf.arch]
                    md = capstone.Cs(getattr(capstone, ca), getattr(capstone, cm))
                    funcs = [(n, va, sz) for n, va, sz in _nso_exports(elf)
                             if n == "JNI_OnLoad" or n.startswith("Java_") or "huntress" in n.lower()][:_JCB_FUNCS]
                    funcs += [(n, va, 0) for n, va in _nso_registered(elf, dex)][:16]
                    found = []
                    for _, va, sz in funcs:
                        if time.time() > deadline:
                            break
                        found += _jcb_pair(_jcb_refs(elf, md, va, sz))
                    if not found:  # stripped helpers: .rodata strings in address order as one body
                        refs = [s.decode() for name, _, b in elf.sections(True) if name.startswith(".rodata")
                                for s in re.findall(rb"[\x20-\x7e]{1,255}(?=\0)", b)]
                        found = _jcb_pair(refs[:4096])
                    for c, n, s, lits in found:
                        out.append({"so": info.filename, "class": c, "name": n, "sig": s, "args": lits[:8]})
                except Exception:  # noqa: BLE001 - a malformed .so contributes nothing
                    continue
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        pass
    return out


def jni_callback_scan(apk):
    """ANS tokens from native -> Java callbacks (row 82): each jni_callbacks() target `L<class>;-><name><sig>` is
    resolved in the dex and run by the dex_eval_scan interpreter with the native's string literals as its String args
    (every ordering, <= 24 tries; other params 0); then any token in the literals themselves. [] when absent."""
    hits = []
    try:
        cbs = jni_callbacks(apk)
        if not cbs:
            return []
        deadline = time.time() + _JCB_BUDGET_S
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70:
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001
                continue
            for cb in cbs:
                ct = f"L{cb['class']};"
                ref = f"{ct}->{cb['name']}{cb['sig']}"
                if ref not in dx.code:
                    continue
                acc, ps = dx.code[ref][3], _dxe_params(ref)
                ns = sum(p == "Ljava/lang/String;" for p in ps)
                tries = list(itertools.islice(itertools.permutations(cb["args"], ns), _JCB_TRIES)) if ns else [()]
                for args in tries:
                    if time.time() > deadline:
                        break
                    it, raw = iter(args), [] if acc & 0x8 else [_DxObj(ct)]
                    for p in ps:
                        raw += [next(it) if p == "Ljava/lang/String;" else _dxe_default(p)] + ([None] if p in "JD" else [])
                    vm = _DxVM(dx, deadline)
                    try:
                        vm.init_class(ct)
                        ret = vm.run(ref, raw)
                    except Exception:  # noqa: BLE001 - unknown op / call: this ordering gives nothing
                        continue
                    found = ANS_RE_T.findall(ret) if isinstance(ret, str) else []
                    if not found and isinstance(ret, str) and re.fullmatch(r"[A-Za-z0-9+/=_-]{24,}", ret):
                        found = ANS_RE_T.findall(decode_any(ret.encode(), depth=1, cap=40, chain=False) or "")
                    hits += found
        for cb in cbs:
            for s in cb["args"]:
                hits += ANS_RE_T.findall(s)
    except Exception:  # noqa: BLE001
        pass
    return list(dict.fromkeys(hits))


# --- class-loader shadowing: same descriptor in host and payload dex (coverage atlas row 84) --------------------------
# A class defined in classes*.dex AND in an asset dex / jar: which copy runs is decided by delegation order. Android's
# DexClassLoader / PathClassLoader / InMemoryDexClassLoader are parent-first (the host / boot copy wins; among host
# multidex the first classes{,2,3..}.dex wins) unless the app defines a ClassLoader subclass overriding loadClass
# (child-first), builds a DelegateLastClassLoader, or passes a null parent (const/4 vX, 0 -> boot parent: the payload
# copy wins). findClass alone does not change the order (ClassLoader.loadClass still asks the parent first).
_CLS_FW = frozenset(("Ldalvik/system/DexClassLoader;", "Ldalvik/system/PathClassLoader;", "Ljava/lang/ClassLoader;",
                     "Ldalvik/system/InMemoryDexClassLoader;", "Ldalvik/system/BaseDexClassLoader;",
                     "Ldalvik/system/DelegateLastClassLoader;", "Ljava/net/URLClassLoader;",
                     "Ljava/security/SecureClassLoader;"))
_CLS_MAX_PAYLOADS, _CLS_MAX_UNITS, _CLS_DECODE_BUDGET = 16, 1_500_000, 60
_CLS_PAYLOAD_NAME = re.compile(r"(?i)(?:^assets/|^res/raw/|\.(?:dex|jar|apk|zip|bin|dat)$)")


def _cls_dex_index(d, budget):
    """{descriptor: {"super", "strs" (const-string + static String values), "loadClass" (defines it)}} plus
    [(constructed loader descriptor, parent register was null)] for one dex. {} / [] on a malformed dex."""
    import struct
    if d[:4] != b"dex\n" or len(d) < 0x70:
        return {}, []
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_str, o_str, n_typ, o_typ = u32(0x38), u32(0x3C), u32(0x40), u32(0x44)
    n_pro, o_pro, n_met, o_met, n_cls, o_cls = u32(0x48), u32(0x4C), u32(0x58), u32(0x5C), u32(0x60), u32(0x64)
    if (n_str > 1 << 22 or n_cls > 1 << 20 or o_str + 4 * n_str > len(d) or o_typ + 4 * n_typ > len(d)
            or o_pro + 12 * n_pro > len(d) or o_met + 8 * n_met > len(d) or o_cls + 32 * n_cls > len(d)):
        return {}, []
    scache = {}

    def sget(i):
        if i not in scache:
            if i >= n_str:
                return ""
            _, j = _uleb(d, u32(o_str + 4 * i))
            e = d.find(b"\0", j)
            scache[i] = d[j:e if e >= 0 else len(d)].decode("utf-8", "replace")
        return scache[i]

    tget = lambda t: sget(u32(o_typ + 4 * t)) if t < n_typ else ""  # noqa: E731

    def mref(mi):
        if mi >= n_met:
            return "", "", ""
        c, p = struct.unpack_from("<HH", d, o_met + 8 * mi)
        last = ""
        if p < n_pro:
            po = u32(o_pro + 12 * p + 8)
            if po and po + 4 <= len(d):
                n = u32(po)
                if 0 < n < 256 and po + 4 + 2 * n <= len(d):
                    last = tget(struct.unpack_from("<H", d, po + 4 + 2 * (n - 1))[0])
        return tget(c), sget(u32(o_met + 8 * mi + 4)), last

    classes, ctors = {}, []
    for c in range(n_cls):
        base = o_cls + 32 * c
        desc, sup = tget(u32(base)), u32(base + 8)
        rec = classes.setdefault(desc, {"super": tget(sup) if sup != 0xFFFFFFFF else "", "strs": [], "loadClass": False})
        cdata, sval = u32(base + 24), u32(base + 28)
        if cdata and cdata < len(d):
            i = cdata
            sf, i = _uleb(d, i)
            inf, i = _uleb(d, i)
            dm, i = _uleb(d, i)
            vm, i = _uleb(d, i)
            for _ in range(2 * (sf + inf)):
                _, i = _uleb(d, i)
            mi = 0
            for k in range(dm + vm):
                if k == dm:
                    mi = 0
                diff, i = _uleb(d, i)
                mi += diff
                _, i = _uleb(d, i)
                code, i = _uleb(d, i)
                if k >= dm and mref(mi)[1] == "loadClass":
                    rec["loadClass"] = True
                if not code or code + 16 > len(d) or budget[0] <= 0:
                    continue
                n_ins = u32(code + 12)
                budget[0] -= n_ins
                ins = d[code + 16:code + 16 + 2 * n_ins]
                regs, pc = {}, 0
                while pc < n_ins and 2 * pc + 1 < len(ins):
                    p = 2 * pc
                    op, a = ins[p], ins[p + 1]
                    if op == 0 and a in (1, 2, 3):  # switch / fill-array payloads
                        if a == 1:
                            pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
                        elif a == 2:
                            pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
                        else:
                            w, n = struct.unpack_from("<HI", ins, p + 2)
                            pc += 4 + (w * n + 1) // 2
                        continue
                    w = _DOP_W[op]
                    if p + 2 * w > len(ins):
                        break
                    if op == 0x12:
                        regs[a & 0xF] = (a >> 4) == 0
                    elif op == 0x13:
                        regs[a] = struct.unpack_from("<h", ins, p + 2)[0] == 0
                    elif op == 0x07:
                        regs[a & 0xF] = regs.get(a >> 4, False)
                    elif op == 0x08:
                        regs[a] = regs.get(struct.unpack_from("<H", ins, p + 2)[0], False)
                    elif op in (0x1A, 0x1B):
                        regs[a] = False
                        rec["strs"].append(sget(struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0]))
                    elif op in (0x0C, 0x14, 0x15, 0x1C, 0x22, 0x46, 0x62):
                        regs[a] = False
                    elif op in (0x23, 0x54):
                        regs[a & 0xF] = False
                    elif op in (0x70, 0x76):  # invoke-direct(/range): a class-loader <init> and its parent register
                        cdesc, name, last = mref(struct.unpack_from("<H", ins, p + 2)[0])
                        if name == "<init>" and last == "Ljava/lang/ClassLoader;":
                            if op == 0x70:
                                g = struct.unpack_from("<H", ins, p + 4)[0]
                                rl = [g & 0xF, (g >> 4) & 0xF, (g >> 8) & 0xF, g >> 12, a & 0xF][:a >> 4]
                            else:
                                rl = [struct.unpack_from("<H", ins, p + 4)[0] + a - 1] if a else []
                            if rl:
                                ctors.append((cdesc, desc, bool(regs.get(rl[-1], False))))
                    pc += w
        if sval and sval < len(d):  # static final String constants (encoded_array of the class)
            try:
                n, i = _uleb(d, sval)
                for _ in range(min(n, 4096)):
                    t = d[i]
                    i += 1
                    vt, arg = t & 0x1F, t >> 5
                    if vt == 0x17:
                        rec["strs"].append(sget(int.from_bytes(d[i:i + arg + 1], "little")))
                    elif vt in (0x1C, 0x1D):
                        break
                    if vt not in (0x1E, 0x1F):
                        i += arg + 1
            except (IndexError, ValueError):
                pass
    return classes, ctors


def _cls_payloads(z):
    """[(label, dex bytes)] of every dex reachable outside the top-level classes*.dex: an asset / res/raw / *.dex|jar|apk
    entry that is a dex or a zip (plain or single-byte xor'd); a zip contributes its classes*.dex."""
    out = []
    for info in z.infolist():
        n = info.filename
        if (info.is_dir() or re.fullmatch(r"classes\d*\.dex", n) or n.startswith("META-INF/")
                or not _CLS_PAYLOAD_NAME.search(n) or not (0x70 <= info.file_size <= _NEST_MAX_ENTRY)):
            continue
        with z.open(info) as f:
            if _unwrap_nested(f.read(8)) is None:
                continue
        got = _unwrap_nested(z.read(info))
        if got is None:
            continue
        kind, b = got
        if kind == "dex":
            out.append((n, b))
        else:
            try:
                with zipfile.ZipFile(io.BytesIO(b)) as iz:
                    for m in sorted((m for m in iz.namelist() if re.fullmatch(r"classes\d*\.dex", m)),
                                    key=lambda m: int(m[7:-4] or 1)):
                        out.append((f"{n}!{m}", iz.read(m)))
            except (zipfile.BadZipFile, OSError, ValueError, KeyError):
                pass
        if len(out) >= _CLS_MAX_PAYLOADS:
            break
    return out[:_CLS_MAX_PAYLOADS]


def _cls_tokens(strs, decode):
    toks = []
    for s in strs:
        toks += ANS_RE_T.findall(s)
    if not toks and decode:
        for s in [s for s in dict.fromkeys(strs) if 16 <= len(s) <= 4096][:_CLS_DECODE_BUDGET]:
            r = decode_any(s, depth=2, chain=False)
            if r:
                toks += ANS_RE_T.findall(r)
    return list(dict.fromkeys(toks))


def classloader_shadow_facts(apk):
    """{} unless a class descriptor is defined more than once across classes*.dex and payload dexes. Otherwise
    {"mode": "parent-first" | "child-first", "evidence": [...], "shadowed": [{"class", "winner", "losers"}],
     "live": ANS tokens of the winning copies, "demoted": ANS tokens only the shadowed copies hold}."""
    try:
        with zipfile.ZipFile(apk) as z:
            payloads = _cls_payloads(z)
            if not payloads:
                return {}
            hosts = sorted((n for n in z.namelist() if re.fullmatch(r"classes\d*\.dex", n)),
                           key=lambda n: int(n[7:-4] or 1))
            host_b = [(n, z.read(n)) for n in hosts]
    except (OSError, zipfile.BadZipFile, ValueError, KeyError, RuntimeError):
        return {}
    try:
        budget, idx, ctors = [_CLS_MAX_UNITS], [], []
        for side, blobs in (("host", host_b), ("payload", payloads)):
            for label, b in blobs:
                cl, ct = _cls_dex_index(b, budget)
                idx.append((side, label, cl))
                if side == "host":
                    ctors += ct
        defs = {}
        for side, label, cl in idx:
            for desc in cl:
                defs.setdefault(desc, []).append((side, label))
        dup = {k: v for k, v in defs.items() if len(v) > 1 and any(s == "host" for s, _ in v)}
        if not dup:
            return {}
        hcls = {}
        for side, _, cl in idx:
            if side == "host":
                for k, v in cl.items():
                    hcls.setdefault(k, v)

        def is_loader(desc, seen=0):
            while desc and seen < 32:
                if desc in _CLS_FW:
                    return True
                desc, seen = hcls.get(desc, {}).get("super", ""), seen + 1
            return False

        evidence = []
        for k, v in hcls.items():
            if v["loadClass"] and k not in _CLS_FW and is_loader(v["super"]):
                evidence.append(f"{k} overrides loadClass (child-first)")
        for cdesc, site, null in ctors:
            if cdesc == "Ldalvik/system/DelegateLastClassLoader;":
                evidence.append(f"{site} builds DelegateLastClassLoader (child-first)")
            elif null and is_loader(cdesc):
                evidence.append(f"{site} builds {cdesc} with a null parent (boot parent)")
        mode = "child-first" if evidence else "parent-first"
        where = {(s, l): cl for s, l, cl in idx}
        shadowed, live, dead = [], [], []
        for desc, copies in dup.items():
            host_c = [c for c in copies if c[0] == "host"]
            pay_c = [c for c in copies if c[0] == "payload"]
            win = pay_c[0] if (mode == "child-first" and pay_c) else host_c[0]
            losers = [c for c in copies if c != win]
            shadowed.append({"class": desc, "winner": win[1], "losers": [c[1] for c in losers]})
            live += _cls_tokens(where[win][desc]["strs"], True)
            for c in losers:
                dead += _cls_tokens(where[c][desc]["strs"], False)
        live = list(dict.fromkeys(live))
        return {"mode": mode, "evidence": evidence, "shadowed": shadowed, "live": live,
                "demoted": [t for t in dict.fromkeys(dead) if t not in live]}
    except Exception:  # noqa: BLE001 - a malformed dex is "no facts", never a crash
        return {}


def classloader_shadow_scan(apk):
    """ANS tokens of the class copies that actually run when a descriptor is shadowed (classloader_shadow_facts); []."""
    return list(classloader_shadow_facts(apk).get("live") or [])


# --- Xamarin / .NET for Android managed assemblies (coverage atlas row 55) -------------------------------------------
# C# string literals live in each DLL's #US heap (UTF-16), which no dex / AXML scan reads. The DLLs ship as
#   assemblies/*.dll                        raw PE, or XALZ: "XALZ" u32 descriptor index, u32 uncompressed size, lz4 block
#   assemblies/assemblies[.<abi>].blob      store v1 "XABA": u32 version, local count, global count, store id; then
#                                           24-byte descriptors {data off, size, debug off, size, config off, size}
#   lib/<abi>/libassemblies.<abi>.blob.so   .NET 8+: ELF whose `payload` section is a store v2 "XABA": u32 version,
#                                           entry count, index count, index bytes; index; 28-byte descriptors
#                                           {mapping index, data off, size, debug off, size, config off, size}
#   lib/<abi>/lib_<Name>.dll.so             per-assembly ELF wrapper, `payload` section = PE or XALZ
# Each descriptor region (store-relative) is a PE or an XALZ; a store whose table does not parse falls back to a magic
# scan (XALZ sized by the next magic, MZ to the next magic). Pure Python + lz4.block; no pyxamstore.
_XAM_MAX_ENTRY, _XAM_MAX_DLL, _XAM_MAX_DLLS, _XAM_DECODE_BUDGET = 64 << 20, 64 << 20, 512, 120
_XAM_NAME = re.compile(r"(?i)(?:^|/)(?:assemblies/.*\.(?:dll|blob)|lib/[^/]+/lib(?:assemblies\.[^/]*\.blob|_[^/]*\.dll)\.so)$")
_XAM_FW = re.compile(r"(?i)^(?:system|microsoft|mono|xamarin|java\.interop|netstandard|mscorlib|_microsoft)[._]")


def _xam_lz4(b, size):
    """lz4 block -> exactly `size` bytes: lz4.block when `b` is the exact block, else a bounded pure-Python decoder that
    stops once `size` bytes are out (tolerates trailing padding). None on malformed input."""
    try:
        import lz4.block
        out = lz4.block.decompress(bytes(b), uncompressed_size=size)
        if len(out) == size:
            return out
    except Exception:  # noqa: BLE001 - trailing bytes / not lz4 / lz4 missing: the pure decoder below
        pass
    if size > (4 << 20):
        return None
    out, i, n = bytearray(), 0, len(b)
    try:
        while i < n and len(out) < size:
            tok = b[i]
            i += 1
            ln = tok >> 4
            if ln == 15:
                while True:
                    c = b[i]
                    i += 1
                    ln += c
                    if c != 255:
                        break
            out += b[i:i + ln]
            i += ln
            if len(out) >= size or i >= n:
                break
            off = b[i] | b[i + 1] << 8
            i += 2
            if not off or off > len(out):
                return None
            ml = tok & 15
            if ml == 15:
                while True:
                    c = b[i]
                    i += 1
                    ml += c
                    if c != 255:
                        break
            ml += 4
            st = len(out) - off
            for k in range(ml):
                out.append(out[st + k])
    except IndexError:
        return None
    return bytes(out[:size]) if len(out) >= size else None


def _xam_elf_payload(b):
    """Contents of the `payload` section of a little-endian ELF32/64 (the .NET 8+ assembly wrapper); None otherwise."""
    if b[:4] != b"\x7fELF" or len(b) < 64 or b[5] != 1:
        return None
    is64 = b[4] == 2
    if is64:
        shoff, = struct.unpack_from("<Q", b, 0x28)
        shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 0x3A)
    else:
        shoff, = struct.unpack_from("<I", b, 0x20)
        shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 0x2E)
    if not shnum or shnum > 4096 or shstrndx >= shnum or shentsize < (64 if is64 else 40) or \
            shoff + shnum * shentsize > len(b):
        return None

    def sec(k):
        o = shoff + k * shentsize
        if is64:
            name, typ, _, _, off, size = struct.unpack_from("<IIQQQQ", b, o)
        else:
            name, typ, _, _, off, size = struct.unpack_from("<IIIIII", b, o)
        return name, typ, off, size
    _, _, stro, strs = sec(shstrndx)
    for k in range(shnum):
        name, typ, off, size = sec(k)
        end = b.find(b"\0", stro + name, stro + strs)
        if b[stro + name:end] == b"payload" and typ != 8 and off + size <= len(b):  # SHT_NOBITS has no bytes
            return b[off:off + size]
    return None


def _xam_regions(b):
    """[(off, size)] of a XABA store's descriptor table (v1 or v2 layout) when every region fits and starts with a PE
    or XALZ magic; [] when the table does not parse."""
    if b[:4] != b"XABA" or len(b) < 20:
        return []
    ver, c1, c2, c3 = struct.unpack_from("<IIII", b, 4)
    tables = []
    if ver & 0xFF == 1:  # v1: local count, global count, store id; 24-byte descriptors right after the header
        tables.append([struct.unpack_from("<II", b, 20 + 24 * k) for k in range(c1) if 20 + 24 * k + 8 <= len(b)])
    for base in dict.fromkeys(x for x in (20 + c3, 20 + 8 * c2, 20 + 12 * c2, 20 + 9 * c2, 20 + 13 * c2)
                              if x < len(b)):  # v2: entry count, index count, index bytes; 28-byte descriptors
        tables.append([struct.unpack_from("<II", b, base + 28 * k + 4) for k in range(c1)
                       if base + 28 * k + 12 <= len(b)])
    for t in tables:
        if t and len(t) <= _XAM_MAX_DLLS and all(o + s <= len(b) and s >= 12 and
                                                  b[o:o + 4] in (b"XALZ", b"MZ\x90\0") for o, s in t):
            return t
    return []


def _xam_unwrap(name, b, out, depth=0):
    """Append (name, PE bytes) for every assembly inside one entry: PE, XALZ, XABA store or ELF `payload` wrapper."""
    if depth > 3 or len(out) >= _XAM_MAX_DLLS or len(b) < 12:
        return
    if b[:2] == b"MZ":
        out.append((name, bytes(b)))
    elif b[:4] == b"XALZ":
        size, = struct.unpack_from("<I", b, 8)
        if 64 <= size <= _XAM_MAX_DLL:
            d = _xam_lz4(b[12:], size)
            if d and d[:2] == b"MZ":
                out.append((name, d))
    elif b[:4] == b"\x7fELF":
        p = _xam_elf_payload(b)
        if p:
            _xam_unwrap(name, p, out, depth + 1)
    elif b[:4] == b"XABA":
        regs = _xam_regions(b)
        if not regs:  # unknown table layout: every XALZ / MZ magic up to the next one
            marks = sorted({m.start() for m in re.finditer(rb"XALZ|MZ\x90\0", b[20:])})
            regs = [(20 + p, (marks[k + 1] if k + 1 < len(marks) else len(b) - 20) - p) for k, p in enumerate(marks)]
        for k, (o, s) in enumerate(regs):
            _xam_unwrap(f"{name}#{k}", b[o:o + s], out, depth + 1)


def xamarin_assemblies(apk):
    """[(name, PE bytes)] of every managed assembly of a Xamarin / .NET for Android APK (assemblies/*.dll raw or XALZ,
    assemblies*.blob XABA stores, lib/<abi>/libassemblies.*.blob.so and lib_*.dll.so ELF payloads); a bare
    store / XALZ / ELF / PE file works too. [] when absent; never raises."""
    out = []
    try:
        try:
            with zipfile.ZipFile(apk) as z:
                for info in z.infolist():
                    if info.is_dir() or info.file_size > _XAM_MAX_ENTRY or len(out) >= _XAM_MAX_DLLS:
                        continue
                    try:
                        with z.open(info) as f:
                            head = f.read(4)
                        if head in (b"XALZ", b"XABA") or (_XAM_NAME.search(info.filename) and
                                                          (head[:2] == b"MZ" or head == b"\x7fELF")):
                            _xam_unwrap(info.filename, z.read(info), out)
                    except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError, struct.error):
                        continue
        except zipfile.BadZipFile:
            if hasattr(apk, "seek"):
                apk.seek(0)
                b = apk.read(_XAM_MAX_ENTRY)
            elif isinstance(apk, (bytes, bytearray)):
                b = bytes(apk)
            else:
                with Path(apk).open("rb") as f:
                    b = f.read(_XAM_MAX_ENTRY)
            _xam_unwrap(getattr(apk, "name", "blob"), b, out)
    except Exception:  # noqa: BLE001 - truncated / impostor store
        pass
    return out


def _xam_cint(b, i):
    """ECMA-335 compressed unsigned int at b[i] -> (value, next index)."""
    c = b[i]
    if c < 0x80:
        return c, i + 1
    if c < 0xC0:
        return (c & 0x3F) << 8 | b[i + 1], i + 2
    return (c & 0x1F) << 24 | b[i + 1] << 16 | b[i + 2] << 8 | b[i + 3], i + 4


def dotnet_user_strings(pe):
    """Every string of a .NET assembly's #US heap (the C# literals, UTF-16), located via the BSJB metadata root.
    [] for a non-.NET / malformed PE; never raises."""
    out = []
    try:
        b = bytes(pe)
        root = b.find(b"BSJB")
        while root >= 0:
            vlen, = struct.unpack_from("<I", b, root + 12)
            p = root + 16 + vlen
            nstreams, = struct.unpack_from("<H", b, p + 2)
            p += 4
            if vlen > 255 or nstreams > 16:
                root = b.find(b"BSJB", root + 4)
                continue
            for _ in range(nstreams):
                off, size = struct.unpack_from("<II", b, p)
                e = b.find(b"\0", p + 8, p + 8 + 32)
                if e < 0:
                    break
                nm = b[p + 8:e]
                p = (e + 4) & ~3
                if nm != b"#US":
                    continue
                h = b[root + off:root + off + size]
                i = 1
                while i < len(h):
                    n, i = _xam_cint(h, i)
                    if n > 1:
                        out.append(h[i:i + n - 1].decode("utf-16-le", "replace"))
                    i += n
                return out
            return out
    except (struct.error, IndexError):
        pass
    return out


def xamarin_assembly_scan(apk):
    """ANS tokens from a Xamarin / .NET for Android APK's managed assemblies (xamarin_assemblies): each DLL's #US
    literals (dotnet_user_strings) read directly, plus a literal ASCII / UTF-16 pass over the whole DLL (embedded
    resources, #Strings); then app (non-framework) literals as a huntress_puzzle-style json and through decode_any,
    unkeyed and keyed by a short neighbouring literal. [] when absent; never raises."""
    hits, app_lits = [], []
    deadline = time.time() + 1.5
    try:
        for name, dll in xamarin_assemblies(apk):
            lits = dotnet_user_strings(dll)
            for s in lits:
                hits += ANS_RE_T.findall(s)
            hits += [m.decode() for m in ANS_RE_B.findall(dll)] + [m.decode("utf-16-le") for m in ANS_RE_U16.findall(dll)]
            if not _XAM_FW.match(Path(name.split("#")[0]).name):
                app_lits += [lits]
        if hits:
            return list(dict.fromkeys(hits))
        budget = _XAM_DECODE_BUDGET
        for lits in app_lits:
            for i, s in enumerate(lits):
                t = s.strip()
                if budget <= 0 or time.time() > deadline:
                    break
                if t.startswith("{") and "codec" in t:
                    try:
                        p = json.loads(t)
                        d = decode_payload(p.get("codec"), p.get("data", p.get("payload", "")), p.get("key"))
                        if d and ANS_RE_T.search(d):
                            hits += ANS_RE_T.findall(d)
                            continue
                    except (ValueError, AttributeError, TypeError):
                        pass
                if not 16 <= len(t) <= _CHAIN_MAX_IN:
                    continue
                budget -= 1
                d = decode_any(t, chain=True, chain_s=0.03)
                for j in (i - 1, i + 1):
                    if d or not 0 <= j < len(lits) or not 1 <= len(lits[j].strip()) <= 32 or time.time() > deadline:
                        continue
                    budget -= 1
                    d = decode_any(t, lits[j].strip(), chain=True, chain_s=0.03)
                if d:
                    hits += ANS_RE_T.findall(d)
    except Exception:  # noqa: BLE001
        pass
    return list(dict.fromkeys(hits))


# --- Flutter / Dart AOT snapshot strings in libapp.so; debug kernel_blob.bin (coverage atlas row 52) ----------------
# A release Flutter app keeps its Dart code and every string literal in lib/<abi>/libapp.so, an ELF exporting
# _kDart{Vm,Isolate}Snapshot{Data,Instructions}. Each snapshot starts with magic 0xdcdcf5f5 (LE), int64 length, int64
# kind (3 = FullAOT), a 32-char version hash (identifies the Dart SDK) and a NUL-terminated features string. Strings
# appear either in the cluster stream (unsigned varint (len << 1) | two_byte, last byte >= 0x80, then Latin-1 or UTF-16LE
# bytes) or as heap objects (tags word, Smi length = 2 * len as u32 (compressed pointers) / u64, then the bytes). No
# blutter (arm64-only, builds the SDK): strings are carved by length prefix with a raw printable / UTF-16LE fallback.
# A debug build ships assets/flutter_assets/kernel_blob.bin (kernel magic 0x90abcdef) holding the Dart source as text.
_DART_MAGIC = (b"\xf5\xf5\xdc\xdc", b"\xdc\xdc\xf5\xf5")
_DART_SYMS = ("_kDartVmSnapshotData", "_kDartVmSnapshotInstructions", "_kDartIsolateSnapshotData",
              "_kDartIsolateSnapshotInstructions")
_DART_KINDS = {0: "Full", 1: "FullCore", 2: "FullJIT", 3: "FullAOT"}
_DART_MAX_ENTRY = 64 << 20
_DART_RUN_A = re.compile(rb"[\x20-\x7e]{4,}")
_DART_RUN_U = re.compile(rb"(?:[\x20-\x7e]\x00){4,}")
_DART_LIT = re.compile(r"""'([^'\\]{1,4096})'|"([^"\\]{1,4096})\"""")
_DART_DECODE_BUDGET, _DART_BUDGET_S = 300, 0.8


def _dart_elf_syms(b):
    """{name: (file offset, size)} of the _kDart* dynsym exports of an ELF32/64 LE .so (struct only); {} otherwise."""
    out = {}
    try:
        if b[:4] != b"\x7fELF" or b[5] != 1:
            return out
        is64 = b[4] == 2
        if is64:
            shoff, shentsize, shnum = struct.unpack_from("<Q", b, 0x28)[0], *struct.unpack_from("<HH", b, 0x3A)
        else:
            shoff, shentsize, shnum = struct.unpack_from("<I", b, 0x20)[0], *struct.unpack_from("<HH", b, 0x2E)
        if not shoff or shnum > 4096 or shoff + shnum * shentsize > len(b):
            return out
        secs = []
        for i in range(shnum):
            o = shoff + i * shentsize
            if is64:
                _, typ, _, addr, off, size, link = struct.unpack_from("<IIQQQQI", b, o)
            else:
                _, typ, _, addr, off, size, link = struct.unpack_from("<IIIIIII", b, o)
            secs.append((typ, addr, off, size, link))
        for typ, _, off, size, link in secs:
            if typ != 11 or link >= len(secs):   # SHT_DYNSYM
                continue
            stro, strsz = secs[link][2], secs[link][3]
            ent = 24 if is64 else 16
            for k in range(min(size // ent, 100_000)):
                o = off + k * ent
                if is64:
                    nm, _, _, shndx, val, sz = struct.unpack_from("<IBBHQQ", b, o)
                else:
                    nm, val, sz, _, _, shndx = struct.unpack_from("<IIIBBH", b, o)
                if not nm or nm >= strsz or not 0 < shndx < len(secs):
                    continue
                name = b[stro + nm:b.index(b"\0", stro + nm)].decode("latin-1")
                if name in _DART_SYMS:
                    s = secs[shndx]
                    fo = s[2] + val - s[1]
                    if 0 <= fo < len(b):
                        out[name] = (fo, min(sz or len(b) - fo, len(b) - fo))
    except (struct.error, IndexError, ValueError):
        return {}
    return out


def dart_snapshot_info(b):
    """Header of every Dart snapshot in a libapp.so (bytes): [{symbol, offset, size, kind, version_hash, features}].
    The version hash names the Dart SDK the app was built with (blutter / reFlutter key their builds on it). [] when
    the .so exports no _kDart* symbol and carries no snapshot magic; never raises."""
    out = []
    try:
        syms = _dart_elf_syms(b) or {"?": (b.find(m), 0) for m in _DART_MAGIC if b.find(m) >= 0}
        for name, (off, size) in sorted(syms.items(), key=lambda kv: kv[1][0]):
            h = b[off:off + 52]
            if h[:4] not in _DART_MAGIC or len(h) < 52:
                out.append({"symbol": name, "offset": off, "size": size, "kind": None})
                continue
            ln, kind = struct.unpack_from("<qq", h, 4)
            feat = b[off + 52:off + 52 + 1024].split(b"\0")[0].decode("latin-1")
            out.append({"symbol": name, "offset": off, "size": size or ln + 4, "kind": _DART_KINDS.get(kind, kind),
                        "version_hash": h[20:52].decode("latin-1"), "features": feat})
    except Exception:  # noqa: BLE001
        pass
    return out


def _dart_prefixed(b, s, n, two):
    """True when the bytes before offset s encode a Dart string length n: cluster varint (len << 1 | two_byte, 7 bits
    per byte, last byte | 0x80) or a heap Smi (2 * len) as u32 / u64 (64-bit layout) or followed by a u32 hash (32-bit)."""
    v, enc = (n << 1) | two, bytearray()
    while v > 0x7F:
        enc.append(v & 0x7F)
        v >>= 7
    enc.append(v | 0x80)
    smi = (2 * n).to_bytes(8, "little")
    return (b[s - len(enc):s] == enc or b[s - 4:s] == smi[:4] or b[s - 8:s] == smi or b[s - 8:s - 4] == smi[:4]) \
        and s >= 4


def dart_strings(b):
    """Ordered strings of a Dart snapshot / kernel region: each printable Latin-1 run (>= 4) and UTF-16LE run, cut to
    its length prefix when one is found (so a following object header never glues on), stripped."""
    found = []
    for rx, two in ((_DART_RUN_A, 0), (_DART_RUN_U, 1)):
        for m in rx.finditer(b):
            s, raw = m.start(), m.group(0)
            n = len(raw) // (2 if two else 1)
            for cut in range(n, 3, -1):   # longest prefixed cut; a run with no length prefix stays whole
                if _dart_prefixed(b, s, cut, two):
                    n = cut
                    break
                if n - cut >= 8:
                    break
            t = (raw[:2 * n].decode("utf-16-le") if two else raw[:n].decode("latin-1")).strip()
            if len(t) >= 4:
                found.append((s, t))
    found.sort()
    return [t for _, t in found]


def _dart_regions(apk):
    """(label, bytes) of every Dart snapshot region (libapp.so _kDart* exports, or the whole .so when it carries the
    magic but no symbols) and every kernel_blob.bin / *snapshot_data file under flutter_assets."""
    out = []
    with zipfile.ZipFile(apk) as z:
        for info in z.infolist():
            n = info.filename
            if info.is_dir() or info.file_size > _DART_MAX_ENTRY:
                continue
            base = n.rsplit("/", 1)[-1]
            if n.endswith(".so") and n.startswith("lib/"):
                with z.open(info) as f:
                    if f.read(4) != b"\x7fELF":
                        continue
                b = z.read(info)
                syms = _dart_elf_syms(b)
                if syms:
                    out += [(f"{n}:{k}", b[o:o + sz]) for k, (o, sz) in sorted(syms.items(), key=lambda kv: kv[1][0])
                            if "Data" in k]
                elif any(m in b for m in _DART_MAGIC) and (base == "libapp.so" or b"_kDartIsolateSnapshot" in b):
                    out.append((n, b))
            elif base in ("kernel_blob.bin", "isolate_snapshot_data", "vm_snapshot_data") or (
                    "flutter_assets/" in n and base.endswith((".dill", ".bin"))):
                out.append((n, z.read(info)))
    return out


def dart_snapshot_scan(apk):
    """ANS tokens from a Flutter app's Dart code: libapp.so snapshot strings (Latin-1 + UTF-16 objects) and a debug
    build's kernel_blob.bin source. A literal token first; then an `ANS-` anchor string joined with the hex-fragment
    strings stored next to it (parts.join / interpolation of consts); then quoted literals / encoded runs through
    decode_any. [] when the APK is not Flutter or nothing matches; never raises."""
    hits, cands = [], []
    try:
        seqs = []
        for _, b in _dart_regions(apk):
            strs = dart_strings(b)
            seqs.append(strs)
            for t in strs:
                hits += ANS_RE_T.findall(t)
        if hits:
            return list(dict.fromkeys(hits))
        for strs in seqs:
            toks = []
            for t in strs:   # kernel source text: each string literal is its own token
                lits = [a or c for a, c in _DART_LIT.findall(t)]
                toks += [x.strip() for x in lits] if lits else [t]
            for a, t in enumerate(toks):
                if not _ANCHOR.fullmatch(t):
                    continue
                need = 20 - len(t)
                for seq in (toks[a + 1:a + 9], toks[max(0, a - 8):a][::-1]):
                    for w in _windows(seq, need):
                        if ANS_RE_T.fullmatch(t + w) and t + w not in hits:
                            hits.append(t + w)
                    if hits:
                        break
            for t in toks:
                for lit in [t] + _POOL_ENCODED.findall(t):
                    if 16 <= len(lit) <= _CHAIN_MAX_IN:
                        cands.append(lit)
        if hits:
            return hits
        end = time.monotonic() + _DART_BUDGET_S
        for r in sorted(dict.fromkeys(cands), key=_hbc_rank)[:_DART_DECODE_BUDGET]:
            if time.monotonic() > end:
                break
            d = decode_any(r, depth=2, cap=200, chain=False)
            if d:
                hits += ANS_RE_T.findall(d)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- multi-signal root detection: the whole clean vector keys the answer (coverage atlas rows 47, 94) -----------------
# N probe methods (su paths, Build.TAGS test-keys, magisk / superuser packages, ro.debuggable / ro.secure, a rw /system
# in /proc/mounts, `which su`, SELinux enforcing) each answer a boolean / int; a combiner folds them into a mask
# (or-int / shl-int), a weighted score, a fragment string, or a boolean[] / int[] / BitSet / EnumSet / Map<String,
# Boolean>, and that keys the xor / hash yielding the token. _RsgVM is _EnvVM (clean retail Pixel) plus java.util
# collections (HashMap bucket order, LinkedHashMap / Tree* / EnumSet / EnumMap orders, BitSet) and the extra probes;
# its forced mode answers 0 (false) from every probe method -- the "patch every check to pass" bypass -- whose value is
# reported separately, demoted: a clean ro.secure=1 / SELinux-enforcing bit makes that vector differ from the real one.
_RSG_BUDGET_S, _RSG_MAX_RUNS, _RSG_LAYERS = 0.75, 96, 4
_RSG_PROPS = {"ro.boot.selinux": "enforcing", "ro.build.selinux": "1", "ro.boot.veritymode": "enforcing",
              "ro.boot.vbmeta.device_state": "locked", "ro.boot.warranty_bit": "0", "ro.warranty_bit": "0",
              "ro.build.version.sdk": "34", "ro.boot.mode": "normal", "ro.bootmode": "unknown", "ro.boot.selinux_mode": ""}
_RSG_FILES = {"/proc/mounts": "/dev/block/dm-6 / ext4 ro,seclabel,relatime 0 0\n"
                              "/dev/block/dm-7 /system_ext ext4 ro,seclabel,relatime 0 0\n"
                              "/dev/block/dm-8 /product ext4 ro,seclabel,relatime 0 0\n"
                              "/dev/block/dm-9 /vendor ext4 ro,seclabel,relatime 0 0\n"
                              "tmpfs /dev tmpfs rw,seclabel,nosuid,relatime,mode=755 0 0\n"
                              "/dev/block/dm-48 /data f2fs rw,lazytime,seclabel,nosuid,nodev,noatime 0 0\n",
              "/sys/fs/selinux/enforce": "1"}
_RSG_FILES["/proc/self/mounts"] = _RSG_FILES["/proc/self/mountinfo"] = _RSG_FILES["/proc/mounts"]
_RSG_MAPS = frozenset(("Ljava/util/HashMap;", "Ljava/util/LinkedHashMap;", "Ljava/util/TreeMap;", "Ljava/util/Hashtable;",
                       "Ljava/util/concurrent/ConcurrentHashMap;", "Ljava/util/EnumMap;", "Landroid/util/ArrayMap;"))
_RSG_SEQS = frozenset(("Ljava/util/ArrayList;", "Ljava/util/LinkedList;", "Ljava/util/HashSet;", "Ljava/util/LinkedHashSet;",
                       "Ljava/util/TreeSet;", "Ljava/util/Vector;", "Ljava/util/ArrayDeque;", "Landroid/util/ArraySet;"))
_RSG_PRE = re.compile(rb"Landroid/os/(?:Build|Debug|SystemProperties);|/proc/(?:self/)?mount|selinux|test-keys|ro\.secure"
                      rb"|ro\.debuggable|getPackageInfo|Runtime;|ProcessBuilder;|/su\x00|magisk|superuser|busybox|Ljava/io/File;")


def _rsg_hash(k):
    """Java hashCode of a String / boxed int key; None for anything else (identity hash: order not knowable)."""
    if isinstance(k, str):
        return _dxe_hash(k) & 0xFFFFFFFF
    if isinstance(k, int):
        return k & 0xFFFFFFFF
    return None


def _rsg_order(t, keys):
    """Iteration order Java gives `keys` (insertion order) in a container of type t."""
    if t in ("Ljava/util/TreeMap;", "Ljava/util/TreeSet;"):
        return sorted(keys)
    if t in ("Ljava/util/EnumSet;", "Ljava/util/EnumMap;"):
        return sorted(keys, key=lambda e: e.f["$ordinal"])
    if t in ("Ljava/util/HashMap;", "Ljava/util/HashSet;", "Ljava/util/concurrent/ConcurrentHashMap;"):
        hs = [_rsg_hash(k) for k in keys]
        if None in hs:
            raise _DxAbort
        cap = 16
        while len(keys) > cap * 3 // 4:
            cap *= 2
        idx = [(h ^ (h >> 16)) & (cap - 1) for h in hs]
        return [k for _, _, k in sorted(zip(idx, range(len(keys)), keys), key=lambda x: x[:2])]
    if t in ("Ljava/util/Hashtable;", "Landroid/util/ArrayMap;", "Landroid/util/ArraySet;"):
        raise _DxAbort
    return list(keys)


class _RsgVM(_EnvVM):
    """_EnvVM with java.util collections, the SELinux / mount probes, and (forced=True) every probe method answering
    0; `vector` records what each probe method returned (see root_signal_facts)."""

    def __init__(self, dx, deadline, probes, forced=False):
        super().__init__(dx, deadline)
        self.probes, self.forced, self.vector = probes, forced, {}
        self.statics.update({"Ljava/lang/Boolean;->TRUE": 1, "Ljava/lang/Boolean;->FALSE": 0})

    def new_instance(self, t):
        if t in _RSG_MAPS or t in _RSG_SEQS or t == "Ljava/util/BitSet;":
            return _DxObj(t)
        return super().new_instance(t)

    def invoke(self, ref, raw, depth):
        r = _env_resolve(self.dx, ref)
        if r in self.probes:
            if self.forced:
                self.vector[r] = 0
                return 0
            v = super().invoke(ref, raw, depth)
            self.vector.setdefault(r, v)
            return v
        return super().invoke(ref, raw, depth)

    def prop(self, name, a):
        k = a[0] if a and isinstance(a[0], str) else None
        if k in _RSG_PROPS:
            v, d = _RSG_PROPS[k], a[1] if len(a) > 1 else None
            if name == "get":
                return v if v or d is None else d
            if name in ("getInt", "getLong", "getBoolean"):
                return (int(v) if v.isdigit() else int(v == "true")) if v else d if isinstance(d, int) else 0
            raise _DxAbort
        return super().prop(name, a)

    def env(self, ref, raw):
        cls, rest = ref.split("->", 1)
        name = rest[:rest.index("(")]
        v = self.coll(cls, name, raw, rest)
        if v is not _ENV_UNSET:
            return v
        o = raw[0] if raw and isinstance(raw[0], _DxObj) else None
        if cls in ("Ljava/io/FileReader;", "Ljava/io/FileInputStream;") and name == "<init>" and o is not None:
            p = _env_path(raw[1] if len(raw) > 1 else None)
            if p in _RSG_FILES:
                o.f["L"] = _RSG_FILES[p].splitlines()
                return None
        if o is not None and o.t == "Ljava/io/File;" and name in ("exists", "canRead", "isFile", "length"):
            p = _env_path(o)
            if p in _RSG_FILES:
                return len(_RSG_FILES[p]) if name == "length" else 1
        return super().env(ref, raw)

    def _box(self, t, items, **kw):
        c = _DxObj(t)
        c.f["rs"] = list(items)
        c.f.update(kw)
        return c

    def coll(self, cls, name, raw, rest=""):  # noqa: C901 - one table of java.util models
        if cls == "Ljava/lang/Boolean;" and name == "booleanValue" and raw and isinstance(raw[0], int):
            return raw[0]
        if cls == "Ljava/util/EnumSet;" and name in ("noneOf", "allOf", "of", "copyOf"):
            if name == "copyOf" and raw and isinstance(raw[0], _DxObj) and "rs" in raw[0].f:
                return self._box(cls, dict.fromkeys(raw[0].f["rs"]), set=1)
            if name == "noneOf":
                return self._box(cls, (), set=1)
            if name == "allOf" and raw and isinstance(raw[0], _DxObj) and "d" in raw[0].f:
                self.init_class(raw[0].f["d"])
                vals = self.statics.get(raw[0].f["d"] + "->$VALUES")
                if isinstance(vals, list):
                    return self._box(cls, vals, set=1)
            if name == "of" and raw:
                its = raw[-1] if isinstance(raw[-1], list) else []
                return self._box(cls, dict.fromkeys([x for x in raw if isinstance(x, _DxObj)] + list(its)), set=1)
            raise _DxAbort
        o = raw[0] if raw and isinstance(raw[0], _DxObj) else None
        if o is None:
            return _ENV_UNSET
        f, a = o.f, raw[1:]
        if name == "<init>" and o.t == cls and (cls in _RSG_MAPS or cls in _RSG_SEQS or cls == "Ljava/util/BitSet;"):
            src = a[0] if a and isinstance(a[0], _DxObj) else None
            if cls == "Ljava/util/BitSet;":
                f["bits"] = 0
            elif cls in _RSG_MAPS:
                f["rm"] = dict(src.f["rm"]) if src is not None and "rm" in src.f else {}
            else:
                f["set"] = int("Set" in cls)
                f["rs"] = list(dict.fromkeys(src.f["rs"]) if f["set"] else src.f["rs"]) if src is not None and \
                    "rs" in src.f else []
            return None
        if "rm" in f:
            m = f["rm"]
            if name in ("put", "putIfAbsent") and len(a) == 2:
                old = m.get(a[0])
                if name == "put" or a[0] not in m:
                    m[a[0]] = a[1]
                return old
            if name in ("get", "getOrDefault", "containsKey", "remove") and a:
                if name == "containsKey":
                    return int(a[0] in m)
                return m.pop(a[0], None) if name == "remove" else m.get(a[0], a[1] if len(a) > 1 else None)
            if name in ("size", "isEmpty"):
                return len(m) if name == "size" else int(not m)
            if name == "containsValue" and a:
                return int(a[0] in m.values())
            if name in ("keySet", "values", "entrySet"):
                ks = _rsg_order(o.t, list(m))
                if name == "keySet":
                    return self._box("Ljava/util/Set;", ks, set=1)
                if name == "values":
                    return self._box("Ljava/util/Collection;", [m[k] for k in ks])
                es = []
                for k in ks:
                    e = _DxObj("Ljava/util/Map$Entry;")
                    e.f.update(ek=k, ev=m[k], em=m)
                    es.append(e)
                return self._box("Ljava/util/Set;", es, set=1)
            raise _DxAbort
        if "ek" in f:
            if name in ("getKey", "getValue"):
                return f["ek"] if name == "getKey" else f["ev"]
            if name == "setValue" and a:
                old, f["ev"] = f["ev"], a[0]
                f["em"][f["ek"]] = a[0]
                return old
            raise _DxAbort
        if "it" in f:
            if name == "hasNext":
                return int(bool(f["it"]))
            if name == "next":
                if not f["it"]:
                    raise _DxThrow("Ljava/util/NoSuchElementException;", "Ljava/lang/RuntimeException;")
                return f["it"].pop(0)
            raise _DxAbort
        if "rs" in f:
            s = f["rs"]
            if name == "add" and len(a) == 1:
                if f.get("set") and a[0] in s:
                    return 0
                s.append(a[0])
                return 1
            if name == "add" and len(a) == 2 and isinstance(a[0], int):
                s.insert(a[0], a[1])
                return None
            if name == "addAll" and a and isinstance(a[0], _DxObj) and "rs" in a[0].f:
                n = len(s)
                s.extend(x for x in a[0].f["rs"] if not (f.get("set") and x in s))
                return int(len(s) > n)
            if name in ("get", "set") and a and isinstance(a[0], int) and not f.get("set"):
                if not 0 <= a[0] < len(s):
                    raise _DxThrow("Ljava/lang/IndexOutOfBoundsException;", "Ljava/lang/RuntimeException;")
                old = s[a[0]]
                if name == "set":
                    s[a[0]] = a[1]
                return old
            if name in ("size", "isEmpty"):
                return len(s) if name == "size" else int(not s)
            if name in ("contains", "indexOf") and a:
                return int(a[0] in s) if name == "contains" else s.index(a[0]) if a[0] in s else -1
            if name == "remove" and a and (f.get("set") or not isinstance(a[0], int)):
                if a[0] in s:
                    s.remove(a[0])
                    return 1
                return 0
            if name in ("iterator", "toArray"):
                items = _rsg_order(o.t, s) if f.get("set") else list(s)
                if name == "toArray":
                    return _DxArr(items)
                it = _DxObj("Ljava/util/Iterator;")
                it.f["it"] = items
                return it
            raise _DxAbort
        if "bits" in f:
            b = f["bits"]
            if name in ("set", "clear", "flip") and a and isinstance(a[0], int):
                if a[0] < 0 or len(a) > 1 and isinstance(a[1], int) and name != "set" and a[1] < a[0]:
                    raise _DxThrow("Ljava/lang/IndexOutOfBoundsException;", "Ljava/lang/RuntimeException;")
                if name == "set" and "(IZ)" in rest:
                    on, mask = a[1], 1 << a[0]
                else:
                    hi = a[1] if len(a) > 1 and isinstance(a[1], int) else a[0] + 1
                    on, mask = name == "set", ((1 << hi) - 1) ^ ((1 << a[0]) - 1)
                f["bits"] = b ^ mask if name == "flip" else b | mask if on else b & ~mask
                return None
            if name == "clear" and not a:
                f["bits"] = 0
                return None
            if name == "get" and len(a) == 1 and isinstance(a[0], int):
                return (b >> a[0]) & 1
            if name in ("cardinality", "length", "isEmpty", "hashCode", "size"):
                h = 1234
                for i, w in enumerate(_rsg_words(b)):
                    h ^= (w & ((1 << 64) - 1)) * (i + 1)
                h &= (1 << 64) - 1
                return {"cardinality": bin(b).count("1"), "length": b.bit_length(), "isEmpty": int(not b),
                        "hashCode": _dxe_w32((h >> 32) ^ h), "size": max(64, -(-b.bit_length() // 64) * 64)}[name]
            if name == "nextSetBit" and a and isinstance(a[0], int):
                x = b >> a[0]
                return -1 if not x else a[0] + (x & -x).bit_length() - 1
            if name in ("toLongArray", "toByteArray"):
                if name == "toLongArray":
                    return _DxArr(_rsg_words(b))
                n = -(-b.bit_length() // 8)
                return _DxArr(((b >> (8 * i)) & 0xFF ^ 0x80) - 0x80 for i in range(n))
            if name in ("or", "and", "xor", "andNot") and a and isinstance(a[0], _DxObj) and "bits" in a[0].f:
                y = a[0].f["bits"]
                f["bits"] = {"or": b | y, "and": b & y, "xor": b ^ y, "andNot": b & ~y}[name]
                return None
            raise _DxAbort
        return _ENV_UNSET


def _rsg_words(b):
    out = []
    while b:
        w = b & ((1 << 64) - 1)
        out.append(w - (1 << 64) if w >> 63 else w)
        b >>= 64
    return out


def root_signal_facts(apk):
    """Multi-signal root detection (see the section comment): {"clean": [ANS tokens the probes-as-clean-Pixel path
    shows], "forced": [ANS tokens of the all-probes-patched-to-false path, a DECOY unless also clean], "vector":
    {probe method: clean return value}}. Empty lists when absent; never raises; < 0.8 s."""
    out = {"clean": [], "forced": [], "vector": {}}
    deadline = time.time() + _RSG_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [z.read(i) for i in z.infolist() if i.file_size <= _DXE_MAX_DEX
                     and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
        for d in dexes:
            if d[:4] != b"dex\n" or len(d) < 0x70 or time.time() > deadline or not _RSG_PRE.search(d):
                continue
            try:
                dx = _DxDex(d)
            except Exception:  # noqa: BLE001 - malformed dex contributes nothing
                continue
            facts = {ref: _env_scan_ins(dx, dx.code[ref][2]) for ref in dx.order}
            for ref in dx.order:  # the probes _env_scan_ins does not know: SELinux, /proc/mounts
                if not facts[ref][0] and any(s in _RSG_FILES or s in _RSG_PROPS for s in _rsg_consts(dx, ref)):
                    facts[ref] = (True, facts[ref][1])
            probes = {r for r, fc in facts.items() if fc[0] and r.endswith((")Z", ")I", ")Ljava/lang/Boolean;"))}
            if not probes:
                continue
            layers, seen = [{r for r, fc in facts.items() if fc[0]}], set()
            seen |= layers[0]
            for _ in range(_RSG_LAYERS):
                nxt = {r for r, fc in facts.items() if fc[1] & layers[-1]} - seen
                if not nxt:
                    break
                seen |= nxt
                layers.append(nxt)
            todo = [r for layer in reversed(layers) for r in sorted(layer)][:_RSG_MAX_RUNS]
            for forced in (False, True):
                stop = deadline if forced else time.time() + (deadline - time.time()) * 0.6
                key = "forced" if forced else "clean"
                for ref in todo:
                    if time.time() > stop:
                        break
                    nreg, nin, _, acc = dx.code[ref]
                    ps = _dxe_params(ref)
                    if len(ps) > 4 or nin > nreg or forced and ref in probes:
                        continue
                    vm = _RsgVM(dx, stop, probes, forced)
                    raw = [] if acc & 0x8 else [_DxObj(ref.split("->")[0])]
                    for p in ps:
                        raw += [_DxObj(p) if p in ("Landroid/content/Context;", "Landroid/app/Activity;",
                                                   "Landroid/app/Application;") else _dxe_default(p)] + (
                            [None] if p in "JD" else [])
                    try:
                        vm.init_class(ref.split("->")[0])
                        vm.note(vm.run(ref, raw))
                    except (_DxAbort, IndexError, KeyError, TypeError, ValueError, AttributeError, OverflowError,
                            RecursionError, struct.error):
                        pass
                    for s in vm.seen + [v for v in vm.statics.values() if isinstance(v, str)]:
                        out[key] += ANS_RE_T.findall(s)
                    if not forced:
                        for r, v in vm.vector.items():
                            if isinstance(v, int):
                                out["vector"].setdefault(r, v)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    out["clean"] = list(dict.fromkeys(out["clean"]))
    out["forced"] = [t for t in dict.fromkeys(out["forced"]) if t not in out["clean"]]
    return out


def _rsg_consts(dx, ref):
    """const-string literals of one method."""
    ins, pc, n, out = dx.code[ref][2], 0, len(dx.code[ref][2]) // 2, []
    while pc < n:
        p = 2 * pc
        op = ins[p]
        if op in (0x1A, 0x1B):
            out.append(dx.s(struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0]) or "")
        elif op == 0 and ins[p + 1] in (1, 2, 3):
            if ins[p + 1] == 1:
                pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
            elif ins[p + 1] == 2:
                pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
            else:
                w, k = struct.unpack_from("<HI", ins, p + 2)
                pc += 4 + (w * k + 1) // 2
            continue
        pc += _DOP_W[op]
    return out


def root_signal_scan(apk):
    """ANS tokens of a multi-signal root check evaluated on the CLEAN vector (root_signal_facts), first; then, labelled
    and demoted, any different token the forced all-probes-false path shows ("forced-success DECOY: ANS-..."), which a
    solver must not submit as the clean answer. [] when absent; never raises; < 0.8 s."""
    f = root_signal_facts(apk)
    return f["clean"] + [f"forced-success DECOY (not the clean vector): {t}" for t in f["forced"]]


# --- Android hardware key attestation: KeyDescription / RootOfTrust (coverage atlas row 93) --------------------------
# An attestation leaf cert carries extension 1.3.6.1.4.1.11129.2.1.17 = KeyDescription SEQUENCE {attestationVersion,
# attestationSecurityLevel ENUM, keyMint/keymasterVersion, keyMint/keymasterSecurityLevel ENUM, attestationChallenge
# OCTET STRING, uniqueId OCTET STRING, softwareEnforced AuthorizationList, teeEnforced AuthorizationList}; each
# AuthorizationList is a SEQUENCE of EXPLICIT [tag] fields, [704] rootOfTrust = SEQUENCE {verifiedBootKey OCTET STRING,
# deviceLocked BOOLEAN, verifiedBootState ENUM(0 Verified, 1 SelfSigned, 2 Unverified, 3 Failed), verifiedBootHash
# OCTET STRING (v3+)}, [705] osVersion, [706] osPatchLevel, [709] attestationApplicationId = OCTET STRING(DER SEQUENCE
# {SET OF {packageName OCTET STRING, version INTEGER}, SET OF signatureDigest OCTET STRING}). The OID is located in
# raw DER, PEM blocks and base64 / hex text of every entry (puzzle JSON fields, dex constants), parsed by a minimal
# pure-python TLV walker (no asn1crypto schema: a hand-rolled / truncated extension still yields what parses).
_KA_OID = b"\x06\x0a\x2b\x06\x01\x04\x01\xd6\x79\x02\x01\x11"
_KA_PEM = re.compile(rb"-----BEGIN (?:TRUSTED )?CERTIFICATE-----([A-Za-z0-9+/=\s\\rn]{40,}?)-----END", re.S)
_KA_B64 = re.compile(rb"[A-Za-z0-9+/_-]{120,}={0,2}")
_KA_HEX = re.compile(rb"(?:[0-9a-fA-F]{2}){100,}")
_KA_STATE = {0: "Verified", 1: "SelfSigned", 2: "Unverified", 3: "Failed"}
_KA_LEVEL = {0: "Software", 1: "TrustedEnvironment", 2: "StrongBox"}
_KA_TAGS = {1: "purpose", 2: "algorithm", 3: "keySize", 5: "digest", 6: "padding", 10: "ecCurve",
            200: "rsaPublicExponent", 203: "mgfDigest", 303: "rollbackResistance", 305: "earlyBootOnly",
            400: "activeDateTime", 401: "originationExpireDateTime", 402: "usageExpireDateTime",
            405: "usageCountLimit", 503: "noAuthRequired", 504: "userAuthType", 505: "authTimeout",
            506: "allowWhileOnBody", 507: "trustedUserPresenceRequired", 508: "trustedConfirmationRequired",
            509: "unlockedDeviceRequired", 600: "allApplications", 601: "applicationId", 701: "creationDateTime",
            702: "origin", 703: "rollbackResistant", 704: "rootOfTrust", 705: "osVersion", 706: "osPatchLevel",
            709: "attestationApplicationId", 710: "attestationIdBrand", 711: "attestationIdDevice",
            712: "attestationIdProduct", 713: "attestationIdSerial", 714: "attestationIdImei",
            715: "attestationIdMeid", 716: "attestationIdManufacturer", 717: "attestationIdModel",
            718: "vendorPatchLevel", 719: "bootPatchLevel", 720: "deviceUniqueAttestation",
            723: "attestationIdSecondImei", 724: "moduleHash"}
_KA_MAX_ENTRY, _KA_MAX_HITS, _KA_BUDGET_S = 8 << 20, 32, 1.2
_KA_STATE_DEX = re.compile(rb"(?i)\b(?:verified_?boot_?state|self_?signed|unverified|(?:^|[^a-z])verified|"
                           rb"device_?locked|root_?of_?trust)\b")


def _ka_tlv(d, i, end):
    """(cls, constructed, tag, content_start, content_end) of the DER element at i, or None."""
    if i + 2 > end:
        return None
    b0 = d[i]
    cls, cons, tag, i = b0 >> 6, bool(b0 & 0x20), b0 & 0x1F, i + 1
    if tag == 0x1F:
        tag = 0
        for _ in range(4):
            if i >= end:
                return None
            tag, i = (tag << 7) | (d[i] & 0x7F), i + 1
            if not d[i - 1] & 0x80:
                break
        else:
            return None
    if i >= end:
        return None
    ln, i = d[i], i + 1
    if ln & 0x80:
        n = ln & 0x7F
        if not 1 <= n <= 4 or i + n > end:
            return None
        ln, i = int.from_bytes(d[i:i + n], "big"), i + n
    if i + ln > end:
        return None
    return cls, cons, tag, i, i + ln


def _ka_children(d, s, e):
    out, i = [], s
    while i < e and len(out) < 256:
        t = _ka_tlv(d, i, e)
        if t is None:
            break
        out.append(t)
        i = t[4]
    return out


def _ka_int(d, t):
    return int.from_bytes(d[t[3]:t[4]], "big", signed=True) if t and t[3] < t[4] <= t[3] + 16 else None


def _ka_value(d, t, depth=0):
    """Python value of a universal element (INTEGER/ENUM/BOOLEAN -> int/bool, OCTET STRING -> bytes, SET/SEQUENCE ->
    list)."""
    cls, cons, tag, s, e = t
    if cls == 0 and tag in (2, 10):
        return _ka_int(d, t)
    if cls == 0 and tag == 1:
        return bool(d[s]) if e > s else None
    if cls == 0 and tag == 5:
        return None
    if cons and depth < 4:
        return [_ka_value(d, c, depth + 1) for c in _ka_children(d, s, e)]
    return bytes(d[s:e])


def _ka_appid(b):
    """AttestationApplicationId DER -> {"packages": [[name, version]], "signature_digests": [hex]}."""
    out = {"packages": [], "signature_digests": []}
    t = _ka_tlv(b, 0, len(b))
    if not t or t[2] != 16:
        return out
    kids = _ka_children(b, t[3], t[4])
    if kids:
        for p in _ka_children(b, kids[0][3], kids[0][4]):
            f = _ka_children(b, p[3], p[4])
            if f:
                out["packages"].append([b[f[0][3]:f[0][4]].decode("utf-8", "replace"),
                                        _ka_int(b, f[1]) if len(f) > 1 else None])
    if len(kids) > 1:
        out["signature_digests"] = [b[c[3]:c[4]].hex() for c in _ka_children(b, kids[1][3], kids[1][4])]
    return out


def _ka_authlist(d, t):
    out = {}
    if not t or not t[1]:
        return out
    for c in _ka_children(d, t[3], t[4]):
        if c[0] != 2:
            continue
        name = _KA_TAGS.get(c[2], f"tag{c[2]}")
        inner = _ka_children(d, c[3], c[4])
        if not inner:
            out[name] = True
            continue
        if c[2] == 704:
            f = _ka_children(d, inner[0][3], inner[0][4])
            vals = [_ka_value(d, x) for x in f]
            rot = {"verifiedBootKey": vals[0].hex() if vals and isinstance(vals[0], bytes) else None,
                   "deviceLocked": vals[1] if len(vals) > 1 else None,
                   "verifiedBootState": vals[2] if len(vals) > 2 else None,
                   "verifiedBootHash": vals[3].hex() if len(vals) > 3 and isinstance(vals[3], bytes) else None}
            rot["verifiedBootStateName"] = _KA_STATE.get(rot["verifiedBootState"])
            rot["clean"] = rot["verifiedBootState"] == 0 and rot["deviceLocked"] is True
            out[name] = rot
        elif c[2] == 709:
            v = _ka_value(d, inner[0])
            out[name] = _ka_appid(v) if isinstance(v, bytes) else v
            if isinstance(v, bytes):
                out[name]["raw"] = v.hex()
        else:
            v = _ka_value(d, inner[0])
            out[name] = v.decode("latin-1") if isinstance(v, bytes) and v.isascii() and v.isprintable() else (
                v.hex() if isinstance(v, bytes) else v)
    return out


def _ka_desc(d, s, e):
    """KeyDescription SEQUENCE content [s, e) -> dict, or None."""
    f = _ka_children(d, s, e)
    if len(f) < 6 or f[4][2] != 4:
        return None
    lv = lambda t: _KA_LEVEL.get(_ka_int(d, t), _ka_int(d, t))  # noqa: E731
    sw = _ka_authlist(d, f[6]) if len(f) > 6 else {}
    hw = _ka_authlist(d, f[7]) if len(f) > 7 else {}
    rot = hw.get("rootOfTrust") or sw.get("rootOfTrust")
    ch = bytes(d[f[4][3]:f[4][4]])
    uid = bytes(d[f[5][3]:f[5][4]]) if f[5][2] == 4 else b""
    return {"attestationVersion": _ka_int(d, f[0]), "attestationSecurityLevel": lv(f[1]),
            "keymasterVersion": _ka_int(d, f[2]), "keymasterSecurityLevel": lv(f[3]),
            "attestationChallenge": ch.hex(), "challenge_text": ch.decode("latin-1"), "uniqueId": uid.hex(),
            "softwareEnforced": sw, "teeEnforced": hw, "rootOfTrust": rot,
            "verifiedBootState": rot and rot.get("verifiedBootStateName"),
            "deviceLocked": rot and rot.get("deviceLocked"), "clean": bool(rot and rot.get("clean")),
            "osVersion": hw.get("osVersion", sw.get("osVersion")),
            "osPatchLevel": hw.get("osPatchLevel", sw.get("osPatchLevel")),
            "attestationApplicationId": sw.get("attestationApplicationId") or hw.get("attestationApplicationId")}


def _ka_blob_descs(b, out, seen, depth=0):
    """Every KeyDescription in a blob: raw DER at each OID hit, then PEM / base64 / hex text decoded (2 levels)."""
    i = b.find(_KA_OID)
    while i >= 0 and len(out) < _KA_MAX_HITS:
        j = i + len(_KA_OID)
        t = _ka_tlv(b, j, len(b))
        if t and t[0] == 0 and t[2] == 1:  # critical BOOLEAN
            t = _ka_tlv(b, t[4], len(b))
        if t and t[0] == 0 and t[2] == 4:
            s = _ka_tlv(b, t[3], t[4])
            if s and s[2] == 16 and bytes(b[s[3]:s[4]]) not in seen:
                seen.add(bytes(b[s[3]:s[4]]))
                try:
                    r = _ka_desc(b, s[3], s[4])
                except (IndexError, ValueError, TypeError, AttributeError):
                    r = None
                if r:
                    out.append(r)
        i = b.find(_KA_OID, j)
    if depth >= 2:
        return
    cands = []
    for m in _KA_PEM.finditer(b):
        cands.append(re.sub(rb"\\[rn]|\s", b"", m.group(1)))
    if b"\x2b\x06\x01\x04\x01\xd6\x79" not in b or depth:
        cands += [m.group(0) for m in _KA_B64.finditer(b)][:64]
    for c in cands:
        if len(out) >= _KA_MAX_HITS:
            return
        for alt in (False, True):
            try:
                raw = base64.b64decode(c + b"=" * (-len(c) % 4), altchars=b"-_" if alt else None, validate=False)
            except (binascii.Error, ValueError):
                continue
            if b"\x2b\x06\x01\x04\x01\xd6\x79" in raw or b"CERTIFICATE" in raw:
                _ka_blob_descs(raw, out, seen, depth + 1)
                break
    for m in list(_KA_HEX.finditer(b))[:64]:
        raw = bytes.fromhex(m.group(0).decode())
        if b"\x2b\x06\x01\x04\x01\xd6\x79" in raw:
            _ka_blob_descs(raw, out, seen, depth + 1)


def _ka_tokens(r):
    """ANS tokens in a KeyDescription's octet strings: ASCII, ASCII-hex text, then decode_any on printable strings."""
    vals = [r["attestationChallenge"], r["uniqueId"]]
    for al in (r["softwareEnforced"], r["teeEnforced"]):
        for k, v in al.items():
            if isinstance(v, str):
                vals += [v.encode("latin-1", "replace").hex()] + ([v] if re.fullmatch(r"(?:[0-9a-f]{2})+", v) else [])
            elif k == "rootOfTrust" and isinstance(v, dict):
                vals += [v.get("verifiedBootKey") or "", v.get("verifiedBootHash") or ""]
            elif k == "attestationApplicationId" and isinstance(v, dict):
                vals += [p[0].encode("utf-8", "replace").hex() for p in v.get("packages", [])]
                vals += v.get("signature_digests", [])
    toks = []
    for h in vals:
        try:
            raw = bytes.fromhex(h or "")
        except ValueError:
            continue
        txt = raw.decode("latin-1")
        toks += ANS_RE_T.findall(txt)
        for m in re.finditer(r"(?:[0-9a-fA-F]{2}){20,}", txt):
            toks += ANS_RE_T.findall(bytes.fromhex(m.group(0)).decode("latin-1"))
        if not toks:
            for s in re.findall(r"[\x21-\x7e]{16,512}", txt)[:4]:
                toks += ANS_RE_T.findall(decode_any(s, depth=2, cap=600, chain=False) or "")
    return list(dict.fromkeys(toks))


def key_attestation_scan(apk):
    """Android hardware key attestation certs shipped in the APK (row 93): [{"entry", "attestationVersion",
    "attestationSecurityLevel" / "keymasterSecurityLevel" (Software / TrustedEnvironment / StrongBox),
    "attestationChallenge" (hex) / "challenge_text", "uniqueId", "softwareEnforced" / "teeEnforced" (AuthorizationList
    {field name: value}), "rootOfTrust" {verifiedBootKey, deviceLocked, verifiedBootState (int) +
    verifiedBootStateName (Verified / SelfSigned / Unverified / Failed), verifiedBootHash, clean}, "verifiedBootState",
    "deviceLocked", "clean" (Verified + locked), "osVersion", "osPatchLevel", "attestationApplicationId" {packages
    [[name, version]], signature_digests [hex]}, "sig_match" (an app-id digest equals the APK signer's sha256; None
    when no signer / digest), "dex_boot_markers" (boot-state strings the dex compares), "tokens" (ANS-...)}].
    Searches raw DER, PEM and base64 / hex text of every entry (assets, res/raw, META-INF, puzzle JSON, dex).
    [] when absent; never raises; < 1.2 s."""
    out = []
    try:
        deadline = time.time() + _KA_BUDGET_S
        markers = set()
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if time.time() > deadline or len(out) >= _KA_MAX_HITS:
                    break
                if info.is_dir() or info.file_size > _KA_MAX_ENTRY:
                    continue
                try:
                    b = z.read(info)
                except Exception:  # noqa: BLE001 - corrupt / encrypted entry
                    continue
                if info.filename.endswith(".dex"):
                    markers.update(m.group(0).decode("latin-1").strip() for m in _KA_STATE_DEX.finditer(b))
                found = []
                _ka_blob_descs(b, found, set())
                for r in found:
                    r["entry"] = info.filename
                out += found
        if out:
            signers = {x["sha256"] for x in signing_certs(apk)}
            for r in out:
                dig = set((r.get("attestationApplicationId") or {}).get("signature_digests") or []) \
                    if isinstance(r.get("attestationApplicationId"), dict) else set()
                r["sig_match"] = bool(dig & signers) if dig and signers else None
                r["dex_boot_markers"] = sorted(markers)[:16]
                r["tokens"] = _ka_tokens(r)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        return out
    return out


def key_attestation_tokens(apk):
    """ANS tokens from key_attestation_scan, clean (Verified + locked) attestations first. [] when absent."""
    recs = key_attestation_scan(apk)
    recs.sort(key=lambda r: not r.get("clean"))
    return list(dict.fromkeys(t for r in recs for t in r.get("tokens", [])))
