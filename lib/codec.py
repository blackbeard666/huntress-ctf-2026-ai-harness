"""Codec helper for the script-analysis fixtures' self-describing payloads.

The script-analysis generator hides each fixture's plan behind a declared codec, written next to the payload:
    Const Codec_<id> = "<rep>|<transform>|<key>"            (VBS; also bash `readonly`, Python `CODEC_<id> = ...`)
    rem HUNTRESS-CODEC:<rep>|<transform>                       (Batch: the parameter is part of the transform name)
and the payload as `Material_<id>` / `MATERIAL_<id>` / `rem HUNTRESS-MATERIAL:`. The rep says how the bytes are WRITTEN
(base64, hex pairs, decimal list...), the transform how they were scrambled (named for the ENCODE side, the key is hex).

This is a TOOL for the worker and its solver, not a solver: `decode()` turns (material, rep, transform, key) into the
plaintext, `find_codecs()` lists every declared codec in a source text, `plan_kv()` splits `k=v|k=v`. Anything it does
not know returns None (never raises) -- a new rep/transform is the worker's job; propose it under `## Proposed lib
additions` in NOTES.md and the post-run ratchet adds it here.

Every name is tagged with the day it was FIRST seen (`REPS` / `TRANSFORMS`), so a from-scratch replay of day N can load
only what days < N taught: `HCTF_CODEC_MAX_DAY=<N-1>` (unset = everything).
Validation: the right reading yields a plan starting `v=` (or JSON `{`); ambiguous parameters (rotation amount, rolling
xor flavour, reversal order) are tried in a small fixed order and the first valid plaintext wins.
"""
import base64
import binascii
import os
import re
import time

# name -> first day seen in the GM's script-analysis evidence
REPS = {
    "base64_literal": 3, "decimal_bytes": 3, "hex_pairs": 3, "plain_fragments": 3, "reversed_text": 3,
    "split_fragments": 3,
    "base64_chunks": 4, "decimal_comma": 4, "decimal_dash": 4, "decimal_pipe": 4, "hex_colon": 4, "hex_compact": 4,
    "hex_dash": 4, "reversed_decimal": 4, "reversed_hex": 4,
    "decimal_csv": 5, "decimal_dot": 5, "hex_escape": 5, "hex_literal": 5, "integer_list": 5, "integer_tuple": 5,
    "reversed_integer_list": 5, "urlsafe_base64": 5,
    "decimal_colon": 6, "decimal_space": 6, "octal_space": 6, "percent_hex": 6,
    "json_numbers": 7, "unicode_escapes": 7, "reversed_base64": 7, "xor_hex": 7,
    "hex_base64": 8,
    # compressed / wider-alphabet reps (prebuild gzip-zlib-codec-rep, 10-16): tagged 16 so no earlier-day replay sees them
    "gzip_base64": 16, "zlib_base64": 16, "deflate_base64": 16, "gzip_hex": 16, "zlib_hex": 16, "base32": 16,
    "base85": 16, "ascii85": 16,
}
TRANSFORMS = {
    "identity": 3, "reverse": 3, "add_7": 3, "xor_5a": 3, "rotate_left": 3, "reverse_xor": 3,
    "add_modulo_256": 4, "subtract_modulo_256": 4, "repeating_key_xor": 4, "reverse_bytes": 4,
    "reverse_then_xor": 4, "rolling_xor": 4, "single_byte_xor": 4,
    # layer transforms (gzip-zlib-codec-rep): the _fallback tries them only after every earlier pair found no plan
    "rot13": 16, "atbash": 16, "rc4": 16, "gzip": 16, "zlib": 16, "deflate": 16,
}
_LAYER_TRANSFORMS = ("rot13", "atbash", "rc4", "gzip", "zlib", "deflate")
_TRANSFORM_ALIAS = {"rot_13": "rot13", "rot-13": "rot13", "caesar_13": "rot13", "arc4": "rc4", "arcfour": "rc4",
                    "rc4_key": "rc4", "gunzip": "gzip", "gzip_compress": "gzip", "zlib_compress": "zlib",
                    "inflate": "deflate", "raw_deflate": "deflate", "deflate_raw": "deflate"}


def _max_day():
    try:
        return int(os.environ.get("HCTF_CODEC_MAX_DAY", "0")) or 99
    except ValueError:
        return 99


def known(rep=None, transform=None):
    """True if every given name is in the vocabulary visible to this run."""
    md = _max_day()
    return ((rep is None or REPS.get(rep, 99) <= md) and
            (transform is None or _base_transform(transform)[0] in TRANSFORMS and
             TRANSFORMS.get(_base_transform(transform)[0], 99) <= md))


def _base_transform(t):
    """'xor_5a' -> ('xor_5a', 0x5a); 'add_7' -> ('add_7', 7). Parameterised names carry their own key."""
    t = _TRANSFORM_ALIAS.get((t or "").lower(), t)
    m = re.fullmatch(r"(xor|add|sub|subtract|rotate_left|rol)_([0-9a-fA-F]{1,2})", t or "")
    if m:
        return t, m.group(2) if m.group(1) == "xor" else f"{int(m.group(2)):02x}"   # add_7 = decimal 7
    return t, None


# ------------------------------------------------------------------------------------------------ helpers

def b64(text):
    """Standard or urlsafe base64, whitespace/quotes stripped, padding repaired. bytes or None."""
    s = re.sub(r"[^A-Za-z0-9+/=_-]", "", text or "")
    s = s.rstrip("=")
    s += "=" * (-len(s) % 4)
    for alt in (None, b"-_"):
        try:
            return base64.b64decode(s, altchars=alt, validate=True) if alt is None else base64.b64decode(s, altchars=alt)
        except (binascii.Error, ValueError):
            continue
    return None


def int_array(text, radix=None):
    """Integers from any separator-joined list. radix: 10/16/8, or None = per token (`0x..` hex, else decimal).
    READ THE RADIX FROM THE CODE (`parseInt(x, 16)`, `CInt("&H" & x)`, `int(x, 8)`) when it is not explicit."""
    toks = re.findall(r"0[xX][0-9a-fA-F]+|&[hH][0-9a-fA-F]+|[0-9a-fA-F]+", text or "")
    out = []
    for t in toks:
        if t[:2] in ("0x", "0X"):
            out.append(int(t, 16))
        elif t[:2] in ("&h", "&H"):
            out.append(int(t[2:], 16))
        elif radix:
            out.append(int(t, radix))
        elif t.isdigit():
            out.append(int(t))
        else:
            return None
    return out


def hex_bytes(text):
    """Hex digits in any wrapping (pairs, colon/dash/space separated, `0x`, `\\x`, `%`) -> bytes or None."""
    s = re.sub(r"0[xX]|\\x|%|&[hH]", " ", text or "")
    toks = re.findall(r"[0-9a-fA-F]+", s)
    if not toks:
        return None
    if all(len(t) <= 2 for t in toks) and len(toks) > 1:
        return bytes(int(t, 16) for t in toks)
    s = "".join(toks)
    if len(s) % 2:
        return None
    try:
        return bytes.fromhex(s)
    except ValueError:
        return None


def key_bytes(key):
    """Codec key field -> bytes. Hex ('0b', 'b8b3fe'), or a comma list of hex bytes ('b8,b3,fe')."""
    if key is None:
        return b""
    k = str(key).strip()
    if not k:
        return b""
    if "," in k:
        try:
            return bytes(int(x, 16) for x in k.split(",") if x.strip())
        except ValueError:
            return b""
    try:
        return bytes.fromhex(k if len(k) % 2 == 0 else "0" + k)
    except ValueError:
        return b""


def looks_like_plan(b):
    """The right decode yields `v=N|...` (or a JSON object)."""
    if not b:
        return False
    try:
        t = b.decode("utf-8")
    except UnicodeDecodeError:
        return False
    t = t.lstrip("﻿ \r\n\t")
    if t.startswith("{") and t.rstrip().endswith("}"):
        # a JSON plan must PARSE: a wrong rolling-xor/rotation guess can start with '{' and end with '}' by chance
        # (Day 7 Node json_numbers under a renamed rep decoded to '{Jr^hYuAx...}' and was accepted)
        import json
        try:
            return isinstance(json.loads(t), dict)
        except ValueError:
            return False
    return t.startswith("v=") or "|steps=" in t[:80]


def plan_kv(text):
    """'v=1|steps=a,b|url=..' -> dict (first '=' splits; later duplicates keep the first)."""
    out = {}
    for part in (text or "").strip().split("|"):
        if "=" in part:
            k, v = part.split("=", 1)
            out.setdefault(k.strip(), v)
    return out


# ------------------------------------------------------------------------------------------------ reps

def _rep_candidates(rep, material):
    """All plausible byte readings of the written material for this rep (most likely first)."""
    m = material or ""
    c = []
    if rep.startswith(("gzip", "zlib", "deflate")):   # D16 names: the compressed stream written as base64 / hex
        c += [_inflate(x) for x in (hex_bytes(m) if "hex" in rep else b64(m),) if x]
    elif rep in ("base32", "base85", "ascii85"):
        c += _layer_readings(m, rep)
    elif rep.startswith(("hex_base64", "hex_b64")):   # D8 v=3 `HB64`: hex digits of a base64 text (GM label hex_base64)
        h = hex_bytes(m)
        c += [b64(h.decode("latin-1")) if h else None, h]
    elif "base64" in rep:
        c.append(b64(m))
        c.append(b64(m[::-1]))
    elif rep.startswith("reversed_hex"):
        h = hex_bytes(m)
        c += [h[::-1] if h else None, hex_bytes(re.sub(r"[^0-9a-fA-F]", "", m)[::-1])]
    elif "hex" in rep:
        c.append(hex_bytes(m))
    elif rep.endswith("escapes"):   # Node `unicode_escapes` (D7): '\\u0076\\u003d..' -- any backslash count
        esc = re.findall(r"\\+u([0-9a-fA-F]{4})|\\+x([0-9a-fA-F]{2})", m)
        v = [int(a or b, 16) for a, b in esc]
        c.append(bytes(v) if v and all(x < 256 for x in v) else None)
    elif rep.startswith("octal"):
        a = int_array(m, 8)
        c.append(bytes(a) if a and all(0 <= x < 256 for x in a) else None)
    elif rep.startswith(("reversed_decimal", "reversed_integer")):
        a = int_array(m, 10)
        c.append(bytes(a[::-1]) if a and all(0 <= x < 256 for x in a) else None)
        c.append(bytes(a) if a and all(0 <= x < 256 for x in a) else None)
    elif rep.startswith(("decimal", "integer", "json_num")):   # json_numbers (Node, D7) = '[118,61,49,..]'
        a = int_array(m, 10) or int_array(m)
        c.append(bytes(a) if a and all(0 <= x < 256 for x in a) else None)
    elif rep == "reversed_text":
        c += [m[::-1].encode("latin-1", "replace"), m.encode("latin-1", "replace"), b64(m[::-1]), b64(m)]
    else:  # plain_fragments / split_fragments / unknown text-ish reps: the text itself, or a base64 of it
        c += [m.encode("latin-1", "replace"), b64(m), hex_bytes(m)]
    seen, out = set(), []
    for x in c:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


# ------------------------------------------------------------------------------------------------ transforms

def _xor(b, k):
    return bytes(x ^ k[i % len(k)] for i, x in enumerate(b)) if k else b


def _rolling(b, k0, flavour):
    out, prev = bytearray(), k0
    for x in b:
        p = x ^ prev
        out.append(p)
        prev = x if flavour == "cipher" else p
    return bytes(out)


def _transform_candidates(transform, key, data):
    t, inline = _base_transform(transform)
    k = key_bytes(inline if inline is not None else key)
    k1 = k[0] if k else None
    rev = data[::-1]
    if t == "identity":
        yield data
    elif t in ("reverse", "reverse_bytes"):
        yield rev
    elif t.startswith("xor_") or t == "single_byte_xor" or t == "repeating_key_xor":
        yield _xor(data, k)
        yield _xor(rev, k)
    elif t.startswith("add_"):
        yield bytes((x - k1) % 256 for x in data) if k1 is not None else data
    elif t.startswith(("sub_", "subtract_")):
        yield bytes((x + k1) % 256 for x in data) if k1 is not None else data
    elif t in ("reverse_then_xor", "reverse_xor"):
        kk = k or b"\x5a"           # batch `reverse_xor` carries no key field (0x5a family seen with it)
        yield _xor(rev, kk)
        yield _xor(data, kk)[::-1]
        if not k:
            for g in range(1, 256):
                yield _xor(rev, bytes([g]))
    elif t == "rolling_xor":
        for start in ([k1] if k1 is not None else range(256)):
            yield _rolling(data, start, "cipher")
            yield _rolling(data, start, "plain")
    elif t == "rot13":
        yield data.translate(_ROT13)
    elif t == "atbash":
        yield data.translate(_ATBASH)
    elif t == "rc4":   # stated key: hex bytes, else the key text itself
        for kk in dict.fromkeys(x for x in (k, str(key or "").strip().encode("latin-1", "ignore")) if x):
            yield _rc4(data, kk)
    elif t in ("gzip", "zlib", "deflate"):
        z = _inflate(data)
        if z:
            yield z
    elif t in ("rotate_left", "rol"):
        amounts = [int(inline, 16) % 8] if inline else ([k1 % 8] if k1 else list(range(1, 8)))
        for n in amounts:
            yield bytes(((x >> n) | (x << (8 - n))) & 0xFF for x in data)   # undo a left rotation


_UP, _LO = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ", b"abcdefghijklmnopqrstuvwxyz"
_ROT13 = bytes.maketrans(_UP + _LO, _UP[13:] + _UP[:13] + _LO[13:] + _LO[:13])
_ATBASH = bytes.maketrans(_UP + _LO, _UP[::-1] + _LO[::-1])
_ROT13_S = str.maketrans(_UP.decode() + _LO.decode(), (_UP[13:] + _UP[:13] + _LO[13:] + _LO[:13]).decode())
_B32_TEXT = re.compile(r"[A-Z2-7]{8,}=*|[a-z2-7]{8,}=*")


def _rc4(b, k):
    if not k or len(b) > (1 << 16):
        return b""
    S, j = list(range(256)), 0
    for i in range(256):
        j = (j + S[i] + k[i % len(k)]) & 255
        S[i], S[j] = S[j], S[i]
    out, i, j = bytearray(), 0, 0
    for x in b:
        i = (i + 1) & 255
        j = (j + S[i]) & 255
        S[i], S[j] = S[j], S[i]
        out.append(x ^ S[(S[i] + S[j]) & 255])
    return bytes(out)


def _inflate(b, raw=True):
    """gzip (H4sI) / zlib (eJ, eF..) / bz2 / xz by magic, raw deflate too when `raw`: the COMPLETE stream's bytes, else
    None. A truncated stream (no end marker) is None, never a partial plan. Output bounded to 256 KiB."""
    import bz2
    import lzma
    import zlib
    if not b or len(b) < 8:
        return None
    try:
        if b[:3] == b"BZh":
            d = bz2.BZ2Decompressor()
        elif b[:6] == b"\xfd7zXZ\x00":
            d = lzma.LZMADecompressor()
        else:
            if b[:2] == b"\x1f\x8b":
                w = 31
            elif b[0] & 0x0F == 8 and b[0] >> 4 <= 7 and ((b[0] << 8) | b[1]) % 31 == 0:
                w = 15
            elif raw:
                w = -15
            else:
                return None
            d = zlib.decompressobj(w)
        out = d.decompress(b, 1 << 18)
        return out if out and d.eof else None
    except (zlib.error, OSError, EOFError, ValueError, lzma.LZMAError):
        return None


def _layer_readings(material, rep):
    """Second-pass readings: base32 ([A-Z2-7]=), base85 / Ascii85 (<~..~>), base64 of a ROT13'd text, then every
    generic reading -- each followed by its inflated stream when it is gzip / zlib / raw deflate. Unvalidated."""
    m0 = re.sub(r"\s+", "", material or "").strip("\"'")   # '`' is a base85 digit
    out = []
    for m in dict.fromkeys((m0, m0[::-1])):
        if _B32_TEXT.fullmatch(m):
            s = m.upper().rstrip("=")
            try:
                out.append(base64.b32decode(s + "=" * (-len(s) % 8)))
            except (binascii.Error, ValueError):
                pass
        a = m[2:-2] if m.startswith("<~") and m.endswith("~>") else m
        for f in (base64.b85decode, base64.a85decode):
            try:
                out.append(f(a))
            except (binascii.Error, ValueError):
                pass
        if re.fullmatch(r"[A-Za-z0-9+/=_-]{8,}", m):
            out.append(b64(m.translate(_ROT13_S)))
    out += _generic_readings(material or "", rep or "")
    seen, res = set(), []
    for b in out:
        for x in (b, _inflate(b)):
            if x and x not in seen:
                seen.add(x)
                res.append(x)
    return res


def _spec(rep, transform, key):
    """Normalise short codec specs (D7 bash): `rep|` (empty transform) = identity; `xor_hex|cd` (the rep names the xor
    and the 2nd field is the KEY, not a transform) = repeating_key_xor with that key."""
    t = (transform or "").strip()
    if not t:
        return "identity", key
    if "xor" in rep and t not in TRANSFORMS and _base_transform(t)[1] is None and \
            re.fullmatch(r"[0-9a-fA-F]{1,2}(?:,?[0-9a-fA-F]{2})*", t):
        return "repeating_key_xor", t
    return t, key


def decode(material, rep, transform, key=None):
    """Plaintext (str) of a declared codec, or None. Tries the rep's plausible readings x the transform's plausible
    parameters and returns the first that looks like a plan (`v=` / JSON). Unknown names fall through to
    `_fallback()` (a name-agnostic reading of the literal itself); None if that finds no plan either."""
    if not material or not rep:
        return None
    transform, key = _spec(rep, transform, key)
    if known(rep, transform):
        for data in _rep_candidates(rep, material):
            for out in _transform_candidates(transform, key, data):
                if looks_like_plan(out):
                    return out.decode("utf-8").lstrip("\ufeff")
    return _fallback(material, rep, transform, key)


FALLBACK = os.environ.get("HCTF_CODEC_FALLBACK", "1") != "0"   # 0: names only (strict replay of what day N knew)


def _generic_readings(material, rep):
    """Byte readings of a literal read from its own FORM, not the rep name: \\uXXXX/\\xXX escapes, an int array
    (decimal, or hex when the rep says hex), compact hex, base64 -- each also from the reversed TEXT, and reversed
    bytes. Day 7 TT renamed reps mid-day (`unicode_escapes`, `json_numbers`, `reversed_base64|`, `xor_hex|cd`): every
    one was readable from the material itself, but cost a ~100s generalize because decode() keyed on the name."""
    out = []
    for m in (material, material[::-1]):
        esc = re.findall(r"\\+u([0-9a-fA-F]{4})|\\+x([0-9a-fA-F]{2})", m)
        if esc:
            v = [int(a or b, 16) for a, b in esc]
            if all(x < 256 for x in v):
                out.append(bytes(v))
        if re.fullmatch(r"\s*[\[(]?[\s0-9a-fA-FxX,;:|.-]+[\])]?\s*", m) and re.search(r"[\s,;:|.-]", m.strip()):
            for radix in ((8, 10, 16) if "oct" in rep else (16, 10, 8) if "hex" in rep else (10, 16, 8)):
                try:
                    a = int_array(m, radix)
                except ValueError:       # '3d' is not radix 10: that reading just doesn't apply
                    continue
                if a and all(0 <= x < 256 for x in a):
                    out.append(bytes(a))
        for f in (hex_bytes, b64):
            try:
                b = f(m)
            except (ValueError, TypeError):
                b = None
            if b:
                out.append(b)
    seen, uniq = set(), []
    for b in out + [b[::-1] for b in out]:
        if b not in seen:
            seen.add(b)
            uniq.append(b)
    return uniq


def _fallback(material, rep, transform, key):
    """Name-agnostic decode: generic readings x (the declared transform if known, then every known transform), with
    the declared key or any hex-looking spec field as the key. Only a plan-shaped plaintext is accepted, so a wrong
    guess returns None rather than garbage. Never raises."""
    if not FALLBACK:
        return None
    try:
        trs = [transform] if known(transform=transform) else []
        trs += [t for t in TRANSFORMS if t not in trs and known(transform=t)]
        keys = [k for k in dict.fromkeys([key, transform]) if k and re.fullmatch(r"[0-9a-fA-F]{1,8}|(?:[0-9a-fA-F]{2},)+[0-9a-fA-F]{2}", k)] or [key]
        readings = (_rep_candidates(rep, material) if known(rep) else []) + _generic_readings(material, rep or "")
        for data in readings:
            if not data:
                continue
            for t in trs:
                for k in keys:
                    for out in _transform_candidates(t, k, data):
                        if looks_like_plan(out):
                            return out.decode("utf-8").lstrip("\ufeff")
        return _fallback_layers(material, rep, transform, trs, keys, readings)
    except Exception:  # noqa: BLE001 - a tool for the solver: unknown -> None, never an exception
        return None


def _fallback_layers(material, rep, transform, trs, keys, tried, budget=0.15):
    """Second _fallback pass (gzip-zlib-codec-rep): base32 / base85 / gzip / zlib / deflate readings x (the layer
    transforms rot13 / atbash / rc4 / inflate, then the earlier ones), each output also inflated when it carries a
    gzip / zlib / bz2 / xz magic (plan -> gzip -> rc4). Runs only after the first pass found nothing, so every earlier
    result is unchanged; pairs the first pass already tried skip straight to the inflate check. Bounded by `budget`."""
    import time
    end = time.time() + budget
    lay = [t for t in _LAYER_TRANSFORMS if known(transform=t)]
    trs2 = list(dict.fromkeys(([transform] if transform in trs else []) + lay + trs))
    tried = set(tried)
    for data in _layer_readings(material, rep or ""):
        for t in trs2:
            old = data in tried and t not in lay
            for k in keys:
                for out in _transform_candidates(t, k, data):
                    if not old and looks_like_plan(out):
                        return out.decode("utf-8").lstrip("\ufeff")
                    z = _inflate(out, raw=False)
                    if z and looks_like_plan(z):
                        return z.decode("utf-8").lstrip("\ufeff")
            if time.time() > end:
                return None
    return None


# ------------------------------------------------------------------------------------------------ source scanning

_CODEC_RE = re.compile(r"""(?:Codec|CODEC)_(?P<id>[0-9A-Za-z]+)\s*=\s*["'](?P<spec>[^"']*)["']""")
_BATCH_CODEC_RE = re.compile(r"HUNTRESS-CODEC:\s*(?P<spec>\S+)")
_BATCH_MAT_RE = re.compile(r"HUNTRESS-MATERIAL:\s*(?P<mat>\S+)")
# D8 cross-language v=3 fixtures (.php, .wsf/.hta markup inside .js/.vbs): `HUNTRESS_ANALYSIS_V1:<TAG>-<data>` comment +
# the same data in a `descriptor_<id>` literal; identity transform. FRAG = dot-separated hex fragments.
_ANALYSIS_RE = re.compile(r"""HUNTRESS_ANALYSIS_V\d+:(?P<tag>[A-Za-z0-9_]+)-(?P<mat>[^\s"'<]+)""")
_ANALYSIS_TAG_REP = {"B64": "base64_literal", "HEX": "hex_compact", "HB64": "hex_base64", "FRAG": "hex_compact"}


def material_text(src, ident):
    """The written payload for `Material_<ident>` / `MATERIAL_<ident>`: every string literal (or the int tuple/array)
    of its assignment(s), joined in order -- one literal, `& _` / `+` continuation, adjacent quoted strings, later
    `+=` / `&=` appends. Returns the raw text (rep decoding is decode()'s job) or None."""
    pat = re.compile(r"(?:Material|MATERIAL)_" + re.escape(ident) + r"(?:_[0-9A-Za-z]+)?\b")   # also split `_a`/`_b` parts
    pieces = []
    for m in pat.finditer(src):
        rest = src[m.end():]
        a = re.match(r"\s*(\+=|&=|=|\.=)?\s*", rest)
        if not a or not a.group(1):
            continue                                   # a use, not an assignment
        body = rest[a.end():]
        if body[:1] in "([{" and not body.startswith(("('", '("')):
            close = {"(": ")", "[": "]", "{": "}"}[body[0]]
            end = body.find(close)
            pieces.append(body[1:end] if end > 0 else body[1:400])
            continue
        # string literal(s) until the statement ends (newline not preceded by a continuation)
        stmt, depth = [], 0
        for line in body.splitlines():
            stmt.append(line)
            depth += line.count("(") - line.count(")")       # parenthesised adjacent literals: ("..." \n "...")
            if depth <= 0 and not re.search(r"(&\s*_|\+|\\|,)\s*$", line.rstrip()):
                break
        text = "\n".join(stmt)
        lits = re.findall(r'"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\'', text)
        joined = "".join(a or b for a, b in lits)
        if joined:
            pieces.append(joined)
    return "".join(pieces) or None


def find_codecs(src, _depth=0):
    """Every declared codec in a source text: [{id, rep, transform, key, material, plain}] (plain = decode() or None).
    Batch `HUNTRESS-CODEC:` has no id -- its material is the `HUNTRESS-MATERIAL:` line.
    `src` may also be raw bytes (or latin-1 text) of a container carrier: see _carrier_codecs, tried only when the
    text itself declares nothing."""
    raw = None
    if isinstance(src, (bytes, bytearray)):
        raw = bytes(src)
        src = raw.decode("utf-8", "ignore")
    out = _find_codecs_text(src)
    if _depth < 2 and not any(c.get("plain") for c in out):
        out = out + _carrier_codecs(src, raw, _depth)
    if _depth < 2 and not any(c.get("plain") for c in out):
        out = out + _bat_codecs(src)
    if _depth < 2 and not any(c.get("plain") for c in out):
        out = out + _ps_codecs(src, _depth)
    if _depth < 2 and not any(c.get("plain") for c in out):
        out = out + _xslt_codecs(src)
    elif _depth < 2 and _XSL_HOST.search((src or "")[:1 << 16]):
        # an XML-escaped `"a" &amp; _ "b"` reads as the plan-shaped first piece only: the full plan goes first
        x = [c for c in _xslt_codecs(src) if any(c["plain"] != p and c["plain"].startswith(p)
                                                 for p in (o.get("plain") for o in out) if p)]
        out = x + out
    if _depth < 2 and not any(c.get("plain") for c in out):
        out = out + _chain_codecs(src, _depth)
    return out


def _find_codecs_text(src):
    out = []
    for m in _CODEC_RE.finditer(src or ""):
        parts = m.group("spec").split("|")
        rep, tr, key = (parts + ["", "", ""])[:3]
        mat = material_text(src, m.group("id"))
        out.append({"id": m.group("id"), "rep": rep, "transform": tr, "key": key, "material": mat,
                    "plain": decode(mat, rep, tr, key)})
    bc, bm = _BATCH_CODEC_RE.search(src or ""), _BATCH_MAT_RE.search(src or "")
    if bc:
        parts = bc.group("spec").split("|")
        rep, tr, key = (parts + ["", "", ""])[:3]
        mat = bm.group("mat") if bm else None
        out.append({"id": "batch", "rep": rep, "transform": tr, "key": key, "material": mat,
                    "plain": decode(mat, rep, tr, key)})
    am = _ANALYSIS_RE.search(src or "")
    if am:
        rep = _ANALYSIS_TAG_REP.get(am.group("tag").upper(), am.group("tag").lower())
        dm = re.search(r"descriptor_(\w+)", src)
        # a tag the reps don't name (B32, GZ64, XOR, ROT, A85, URL, UTF16...): peel its layers BEFORE the name-agnostic
        # _fallback, whose transform guesses can turn UTF-16 NULs into a plan-shaped 'v==33||ll..' (known tags unchanged)
        known_tag = am.group("tag").upper() in _ANALYSIS_TAG_REP
        plain = decode(am.group("mat"), rep, "identity") if known_tag else peel_plan(am.group("mat"), am.group("tag"))
        if plain is None:
            plain = peel_plan(am.group("mat"), am.group("tag")) if known_tag else decode(am.group("mat"), rep, "identity")
            for lit in ([] if plain else _descriptor_literals(src)):
                plain = peel_plan(lit, am.group("tag"))
                if plain:
                    break
            if plain is None:                    # wrapped marker material, then the wider descriptor syntax set
                cont = [("", v) for v in _marker_continued(src, am)]
                plain = _peel_ext(cont + _descriptor_literals_ext(src), am.group("tag"),
                                  tried=_descriptor_literals(src) + [am.group("mat")])[1]
        out.append({"id": dm.group(1) if dm else "analysis", "rep": rep, "transform": "identity", "key": "",
                    "material": am.group("mat"), "plain": plain})
    elif not out:
        for ident, lit in _descriptor_literals(src or "", with_id=True):    # descriptor literal, no marker line
            plain = peel_plan(lit)
            if plain:
                out.append({"id": ident, "rep": "descriptor", "transform": "identity", "key": "", "material": lit,
                            "plain": plain})
                break
        if not out:
            lits = _descriptor_literals_ext(src or "")
            ident, plain = _peel_ext(lits, tried=_descriptor_literals(src or ""))
            if plain:
                out.append({"id": ident, "rep": "descriptor", "transform": "identity", "key": "",
                            "material": dict(lits).get(ident), "plain": plain})
    return out


# ------------------------------------------------------------------------------------------------ v=3 layer peel
# The v=3 cross-language marker `HUNTRESS_ANALYSIS_V1:<TAG>-<material>` names its layers in TAG (B64, HEX, HB64, FRAG
# so far). A new tag must not silently yield no plan: peel_plan() reads the material through lib.decode's layer
# expander (hex/b32/b64/b64url/b85/a85/gzip/zlib/bz2/lzma/url/reverse/rot) plus UTF-16 text, raw deflate and
# single-byte / tag-keyed XOR, breadth-first to `depth` layers, accepting only a plan (looks_like_plan).

_DESC_RE = re.compile(r"""descriptor_(?P<id>\w+)\s*(?::=|:|=)?\s*((?:"[^"]*"|'[^']*'|\s*[.+&]\s*|\s*_\s*\n)+)""")


def _descriptor_literals(src, with_id=False):
    """The joined string literal(s) of each `descriptor_<id> = "..." [+ "..."]` assignment."""
    out = []
    for m in _DESC_RE.finditer(src or ""):
        lit = "".join(a or b for a, b in re.findall(r'"([^"]*)"|\'([^\']*)\'', m.group(2)))
        if lit:
            out.append((m.group("id"), lit) if with_id else lit)
    return out



# Descriptor syntax beyond `descriptor_x = "..."` (target descriptor-syntax-generic): any case / `-` separator, typed or
# non-`=` binders (Tcl `set x {..}`, R `<-`, Go `:=` / `var x string =`, Rust/Kotlin/TS `: &str =`, YAML `x: |`, JSON
# `"x": "..."`), multi-line literal forms (triple quotes, here-strings, heredocs, Lua long strings, braces, backticks,
# YAML block scalars) and XML elements (`<descriptor_x>..</..>`, `<string name="descriptor_x">`, plist <key>). Only
# consulted after _descriptor_literals found no plan, so every earlier reading is unchanged.
_XDESC_RE = re.compile(r"""descriptor[_-](?P<id>[\w-]+)["']?""", re.I)
_XBIND_RE = re.compile(r"""[ \t]*(?::[ \t]*&?(?:'static[ \t]+)?[\w.\[\]<>]+[ \t]*(?==))?(?:[ \t]+-?[A-Za-z_][\w.\[\]]*[ \t]*(?==))?"""
                       r"""[ \t]*(?P<op><<-|<-|:=|=>|->|=|:|,)?[ \t]*""")
_XML_DESC_RES = (
    re.compile(r"<(?P<tag>descriptor[\w-]*)\b(?P<attrs>[^>]*)>(?P<body>.*?)</(?P=tag)\s*>", re.I | re.S),
    re.compile(r"""<(?P<tag>[\w:-]+)\b[^>]*?\b(?:name|id|key)\s*=\s*["']descriptor[_-](?P<id>[\w-]+)["'][^>]*>(?P<body>.*?)</(?P=tag)\s*>""",
               re.I | re.S),
    re.compile(r"<key>\s*descriptor[_-](?P<id>[\w-]+)\s*</key>\s*<(?P<tag>\w+)>(?P<body>.*?)</(?P=tag)>", re.I | re.S),
)


def _read_literal(src, i, op):
    """(text, end) of the literal starting at src[i] in any common quoting form, or (None, i)."""
    lim = 1 << 16
    t = src[i:i + 3]
    if t in ('"""', "'''"):
        j = src.find(t, i + 3, i + lim)
        return (src[i + 3:j], j + 3) if j > 0 else (None, i)
    m = re.match(r"""@(["'])[ \t]*\r?\n""", src[i:i + 4])            # PowerShell here-string @" .. "@
    if m:
        e = re.compile(r"\n[ \t]*" + m.group(1) + "@").search(src, i, i + lim)
        return (src[i + m.end():e.start()], e.end()) if e else (None, i)
    m = re.match(r"""<<[-~]?[ \t]*(["']?)([A-Za-z_]\w*)\1[^\n]*\n""", src[i:i + 80])     # heredoc
    if m:
        e = re.compile(r"\n[ \t]*" + re.escape(m.group(2)) + r"\b").search(src, i + m.end() - 1, i + lim)
        return (src[i + m.end():e.start()], e.end()) if e else (None, i)
    m = re.match(r"\[(=*)\[", src[i:i + 12])                          # Lua long string [[ .. ]] / [==[ .. ]==]
    if m:
        j = src.find("]" + m.group(1) + "]", i, i + lim)
        return (src[i + m.end():j], j + len(m.group(0))) if j > 0 else (None, i)
    c = src[i:i + 1]
    if c in "\"'`":
        j = i + 1
        while j < len(src) and j < i + lim:
            if src[j] == "\\" and c != "`":
                j += 2
                continue
            if src[j] == c:
                return src[i + 1:j], j + 1
            j += 1
        return None, i
    if c == "{":                                                     # Tcl braces (nesting)
        depth, j = 0, i
        while j < len(src) and j < i + lim:
            depth += {"{": 1, "}": -1}.get(src[j], 0)
            if depth == 0:
                return src[i + 1:j], j + 1
            j += 1
        return None, i
    m = re.match(r"[|>][-+]?\d?[ \t]*(?:#[^\n]*)?\r?\n", src[i:i + 40])   # YAML block scalar
    if m and op == ":":
        ls = src.rfind("\n", 0, i) + 1
        base = len(src[ls:i]) - len(src[ls:i].lstrip(" \t"))
        body, j = [], i + m.end()
        for line in src[j:j + lim].split("\n"):
            if line.strip() and len(line) - len(line.lstrip(" \t")) <= base:
                break
            body.append(line)
            j += len(line) + 1
        return "\n".join(body), j
    if op in ("=", ":", ":="):                                       # YAML / INI / env plain scalar
        m = re.match(r"[^\s#;,\"'<>(){}\[\]]{8,}", src[i:i + lim])
        if m:
            return m.group(0), i + m.end()
    return None, i


def _descriptor_literals_ext(src, limit=24):
    """(id, literal) of descriptor assignments in the wider syntax set above; concatenated pieces joined."""
    out = []
    for m in _XDESC_RE.finditer(src or ""):
        if len(out) >= limit:
            break
        b = _XBIND_RE.match(src, m.end())
        i, op = b.end(), b.group("op")
        if src.startswith("{", i) and m.group(0).lower().startswith("descriptor") and \
                not re.search(r"\bset\s*$", src[max(0, m.start() - 12):m.start()], re.I) and op is None:
            continue                                                 # `descriptor_x {` that is not a Tcl `set`
        lit, end = _read_literal(src, i, op)
        if lit is None:
            continue
        pieces = [lit]
        while len(pieces) < 64:                                      # "a" + "b" / . / .. / & / ~ / ||, `& _` lines
            c = re.match(r"""\s*(?:\+|\.\.?|&|~|\|\||<>)\s*(?:_[ \t]*\r?\n\s*)?(?=["'`])""", src[end:end + 200])
            if not c:
                break
            nxt, e2 = _read_literal(src, end + c.end(), None)
            if nxt is None:
                break
            pieces.append(nxt)
            end = e2
        out.append((m.group("id"), "".join(pieces)))
    for rx in _XML_DESC_RES:
        for m in rx.finditer(src or ""):
            if len(out) >= 2 * limit:
                break
            body = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", m.group("body"), flags=re.S)
            if "<" in body:
                continue
            ident = m.groupdict().get("id") or (re.search(r"""\b(?:id|name|key)\s*=\s*["']([\w-]+)""", m.group("attrs") or "")
                                                or re.match(r"descriptor[_-]?(.*)", m.group("tag"), re.I)).group(1)
            out.append((ident, body))
    return out


def _peel_ext(lits, tag="", tried=(), budget=1.5):
    """First plan among the wider literals (whitespace-joined first: wrapped base64/hex/base32 lines), or (None, None)."""
    import time
    end, seen = time.time() + budget, set(tried)
    for ident, lit in lits:
        for cand in (re.sub(r"\s+", "", lit), lit.strip()):
            if not cand or cand in seen or time.time() > end:
                continue
            seen.add(cand)
            plain = peel_plan(cand, tag, budget=min(0.4, max(0.05, end - time.time())))
            if plain:
                return ident, plain
    return None, None


_MARK_CONT_RE = re.compile(r"""^[ \t]*(?:#|//|--|;+|'|REM\b|::|\*|%|!)?[ \t]*([A-Za-z0-9+/=_\-.%~:]+)[ \t]*\r?$""")


def _marker_continued(src, am):
    """The v=3 marker material with its wrapped continuation lines appended (block comments / =begin / <# #> / YAML
    folded lines): following lines holding one material-charset token after an optional comment leader."""
    parts, pos = [am.group("mat")], am.end()
    rest = src[pos:pos + (1 << 16)]
    if rest[:1] not in ("\r", "\n"):
        return []
    variants = []
    for line in rest.lstrip("\r").split("\n")[1:65]:
        if re.match(r"\s*(?:=\w+|\"\"\"|'''|#>|\*/|-->|\]\])\s*$", line):
            break
        m = _MARK_CONT_RE.match(line)
        if not m or not m.group(1):
            break
        parts.append(m.group(1))
        variants.append("".join(parts))
    return variants[::-1][:4]

def _utf16(b):
    """UTF-16 text (BOM'd, or LE/BE with every other byte NUL) re-encoded as UTF-8, else None."""
    if len(b) < 4 or len(b) % 2:
        return None
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        enc = "utf-16"
    elif b[1::2].count(0) >= 0.9 * (len(b) // 2):
        enc = "utf-16-le"
    elif b[0::2].count(0) >= 0.9 * (len(b) // 2):
        enc = "utf-16-be"
    else:
        return None
    try:
        return b.decode(enc).lstrip("\ufeff").encode("utf-8")
    except UnicodeDecodeError:
        return None


def _peel_children(b, tag):
    from lib import decode as _d
    import zlib
    rot_all = "ROT" in tag
    for name, out in _d._candidates(b):
        if name.startswith("rot") and not (rot_all or name == "rot13"):
            continue
        yield out
    u = _utf16(b)
    if u:
        yield u
    if _d._printable(b) is None:
        try:
            yield zlib.decompressobj(-15).decompress(b, 1 << 20)
        except zlib.error:
            pass
        m = re.search(r"XOR_?([0-9A-Fa-f]{2,16})", tag)
        if m and len(m.group(1)) % 2 == 0:
            k = bytes.fromhex(m.group(1))
            yield bytes(c ^ k[i % len(k)] for i, c in enumerate(b))
        for k in range(1, 256):
            x = bytes(c ^ k for c in b)
            if x[:2] == b"v=" or x[:1] == b"{" or _d._printable(x):
                yield x


def peel_plan(material, tag="", depth=4, max_nodes=3000, budget=0.5):
    """The plan (str) under up to `depth` generic layers of a v=3 marker/descriptor material, or None. Bounded by
    `max_nodes` and `budget` seconds; never raises."""
    import time
    try:
        mat = (material or "").strip().strip("\"'")
        if not mat:
            return None
        tag = (tag or "").upper()
        end = time.time() + budget
        frontier = [mat.encode()]
        if "." in mat:
            frontier.append(mat.replace(".", "").encode())          # FRAG-style dot-split fragments
        seen, n = set(frontier), 0
        for level in range(depth + 1):
            nxt = []
            for b in frontier:
                if looks_like_plan(b):
                    return b.decode("utf-8").lstrip("\ufeff")
                if level == depth:
                    continue
                for out in _peel_children(b, tag):
                    n += 1
                    if n > max_nodes or time.time() > end:
                        return None
                    if out and out not in seen and len(out) < (1 << 20):
                        if looks_like_plan(out):
                            return out.decode("utf-8").lstrip("\ufeff")
                        seen.add(out)
                        nxt.append(out)
            frontier = nxt
    except Exception:  # noqa: BLE001 - unknown -> None, never an exception
        return None
    return None


# ------------------------------------------------------------------------------------------------ XSLT msxsl:script host
# Target xslt-msxsl-route (msxsl.exe / `wmic /format:evil.xsl`, Squiblytwo; sibling of the D9 SCT and D14 MSBuild hosts):
# an <xsl:stylesheet> carrying <msxsl:script language="JScript|VBScript"> (any prefix bound to
# urn:schemas-microsoft-com:xslt, e.g. <ms:script>). Without CDATA the body is XML-escaped (`&quot;`, VBS `&amp; _`,
# `&#NN;` char refs), which hides the descriptor from the text readings. _xslt_codecs() never applies the transform: it
# reads (1) each script body unescaped and folded per language= (JScript String.fromCharCode, VBS Chr/ChrW), (2) the
# whole document flattened (CDATA unwrapped, the rest unescaped: comment marker + descriptor), (3) XPath string
# literals / concat() of <xsl:variable|param name="descriptor_x" select=..>. Only consulted when nothing else produced
# a plan, and only on an XSLT host, so every earlier reading is unchanged. Pure regex + html.unescape, never raises.
_XSL_HOST = re.compile(r"<[\w.-]*:?(?:stylesheet|transform)\b|urn:schemas-microsoft-com:xslt", re.I)
_XSL_SCRIPT = re.compile(r"<(?P<tag>[\w.-]+:script)\b(?P<attrs>[^>]*)>(?P<body>.*?)</(?P=tag)\s*>", re.I | re.S)
_XSL_VAR = re.compile(r"<[\w.-]+:(?:variable|param|with-param)\b(?P<attrs>[^>]*)>", re.I)
_XSL_CDATA = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.S)


def _xml_flat(s):
    """XML text with CDATA sections unwrapped and everything outside them entity-unescaped."""
    import html
    out, pos = [], 0
    for m in _XSL_CDATA.finditer(s):
        out.append(html.unescape(s[pos:m.start()]))
        out.append(m.group(1))
        pos = m.end()
    out.append(html.unescape(s[pos:]))
    return "".join(out)


def _xsl_fold(body, lang):
    """Constant char-code builders of the script's language rewritten as quoted literals."""
    def q(codes):
        try:
            return '"' + "".join(chr(int(c, 0)) for c in codes).replace('"', "") + '"'
        except (ValueError, OverflowError):
            return None
    if "vb" in lang:
        body = re.sub(r"&[ \t]*_[ \t]*\r?\n\s*", "& ", body)                # `& _` continuation lines joined
        rx = re.compile(r"(?:ChrW?\s*\(\s*(?:&H[0-9A-Fa-f]+|\d+)\s*\)\s*&?\s*)+", re.I)
        sub = lambda m: q([c.replace("&H", "0x").replace("&h", "0x") for c in   # noqa: E731
                           re.findall(r"\(\s*(&H[0-9A-Fa-f]+|\d+)", m.group(0), re.I)]) or m.group(0)
    else:
        rx = re.compile(r"String\.fromCharCode\s*\(\s*([0-9xXa-fA-F,\s]+)\)")
        sub = lambda m: q([c for c in re.split(r"[\s,]+", m.group(1)) if c]) or m.group(0)   # noqa: E731
    return rx.sub(sub, body[:1 << 18])


def _xpath_literal(expr):
    """The string of an XPath `'lit'` / `"lit"` / concat(lit, ...) select expression, else None."""
    e = expr.strip()
    m = re.fullmatch(r"concat\s*\((.*)\)", e, re.S)
    lits = re.findall(r"""'([^']*)'|"([^"]*)\"""", m.group(1) if m else e)
    if not lits or (not m and len(lits) > 1):
        return None
    return "".join(a or b for a, b in lits)


def _xslt_codecs(src):
    try:
        if not src or not _XSL_HOST.search(src[:1 << 16]):
            return []
        texts = []
        for m in _XSL_SCRIPT.finditer(src):
            if len(texts) >= 16:
                break
            lm = re.search(r"""\blanguage\s*=\s*["']([^"']*)""", m.group("attrs"), re.I)
            lang = (lm.group(1) if lm else "jscript").lower()
            body = _xml_flat(m.group("body"))
            texts.append(("msxsl_" + re.sub(r"\W", "", lang), _xsl_fold(body, lang)))
        flat = _xml_flat(src)
        syn = []
        for m in _XSL_VAR.finditer(flat if "&" in src else src):
            a = m.group("attrs")
            nm = re.search(r"""\bname\s*=\s*["'](descriptor[_-][\w-]+)["']""", a, re.I)
            sel = re.search(r"""\bselect\s*=\s*(?:"([^"]*)"|'([^']*)')""", a, re.S)
            lit = _xpath_literal(sel.group(1) if sel.group(1) is not None else sel.group(2)) if nm and sel else None
            if lit:
                syn.append('%s = "%s"\n' % (nm.group(1).replace("-", "_"), lit.replace('"', "")))
        texts.append(("xslt", flat + "\n" + "".join(syn)))
        for ident, text in texts:
            for c in _find_codecs_text(text):
                if c.get("plain"):
                    c = dict(c, id=c.get("id") or ident)
                    return [c]
    except Exception:  # noqa: BLE001 - unknown -> None, never an exception
        return []
    return []


# ------------------------------------------------------------------------------------------------ PowerShell layer peel
# Target ps-layer-peel: the Invoke-Obfuscation family hides the descriptor / marker behind constant PowerShell string
# expressions: backtick ticks, `'a'+'b'`, `"{1}{0}" -f ..`, `[char]N` / `[char[]](..)` / `-join`, `[string]::Join`,
# `'..'[-1..-N]` reversal, `.Replace()` / `-replace`, `$env:comspec[4,15,25]` style env-index tables, and the payload
# layers `-EncodedCommand <UTF-16LE b64>`, `[Text.Encoding]::X.GetString([Convert]::FromBase64String(..))` and
# Deflate/GzipStream over FromBase64String. _ps_codecs() folds the constants statically (never runs anything), then
# reads the folded text and every decoded payload through the normal text readings. Consulted by find_codecs() only
# when nothing else produced a plan, so every earlier reading is unchanged. Bounded, pure python, never raises.
_PS_HINT = re.compile(r"""-f\s*['"(]|\[char\b|\[char\[\]\]|-join\b|::join\(|frombase64string|\s[-/]e(?:c|nc\w*)\s+['"]?[A-Za-z0-9+/]{16}|"""
                      r"""\$env:|\$pshome\b|\$shellid\b|invoke-expression|-[ci]?replace\b""", re.I)
_PS_S = r"'(?:[^']|'')*'"
_PS_SG = r"('(?:[^']|'')*')"
_PS_ENV = {"comspec": r"C:\WINDOWS\system32\cmd.exe", "pshome": r"C:\Windows\System32\WindowsPowerShell\v1.0",
           "shellid": "Microsoft.PowerShell", "verbosepreference": "SilentlyContinue", "public": r"C:\Users\Public",
           "windir": r"C:\WINDOWS", "systemroot": r"C:\WINDOWS", "programdata": r"C:\ProgramData"}
_PS_DQ_ESC = {"0": "\0", "a": "\a", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v"}


def _ps_q(s):
    return "'" + s.replace("'", "''") + "'"


def _ps_u(lit):
    return lit[1:-1].replace("''", "'")


def _ps_list(body):
    """'a','b' (single-quoted literals, comma separated) -> [str], else None."""
    if not re.fullmatch(r"\s*" + _PS_S + r"(?:\s*,\s*" + _PS_S + r")*\s*", body):
        return None
    return [_ps_u(a) for a in re.findall(_PS_S, body)]


def _ps_nums(body):
    toks = [t for t in re.split(r"[\s,]+", body.strip()) if t]
    try:
        return [int(t, 0) for t in toks] if toks else None
    except ValueError:
        return None


def _ps_tokens(src):
    """Normalise quoting: constant double-quoted strings (no `$`) -> single-quoted with backtick escapes applied; ticks
    outside strings dropped; comments kept verbatim."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c == "#" or src.startswith("<#", i):
            j = src.find("#>", i + 2) + 2 if c == "<" else src.find("\n", i)
            j = n if j < (2 if c == "<" else 0) else j
            out.append(src[i:j])
            i = j
        elif c == "'":
            m = re.compile(_PS_S).match(src, i)
            if not m:
                out.append(src[i:])
                break
            out.append(m.group(0))
            i = m.end()
        elif c == '"':
            j, buf, const = i + 1, [], True
            while j < n:
                d = src[j]
                if d == "`" and j + 1 < n:
                    buf.append(_PS_DQ_ESC.get(src[j + 1], src[j + 1]))
                    j += 2
                    continue
                if d == '"':
                    if src.startswith('""', j):
                        buf.append('"')
                        j += 2
                        continue
                    break
                if d == "$":
                    const = False
                buf.append(d)
                j += 1
            out.append(_ps_q("".join(buf)) if const else src[i:j + 1])
            i = j + 1
        elif c == "`" and i + 1 < n and src[i + 1] not in "\r\n":
            i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _ps_format(fmt, args):
    def sub(m):
        if m.group(0) in ("{{", "}}"):
            return m.group(0)[0]
        k = int(m.group(1))
        if k >= len(args):
            raise IndexError
        return args[k]
    return re.sub(r"\{\{|\}\}|\{(\d+)\}", sub, fmt)


def _ps_fold_once(t):
    S, SG = _PS_S, _PS_SG
    NUMS = r"((?:\s*(?:0x[0-9a-fA-F]+|\d+)\s*,)*\s*(?:0x[0-9a-fA-F]+|\d+)\s*)"
    rules = []

    def env(m):
        return _ps_q(_PS_ENV[m.group(1).lower()])
    rules.append((r"\$(?:env:)?(comspec|pshome|shellid|public|windir|systemroot|programdata)\b(?![\w:])", env, re.I))
    rules.append((r"\(?\s*\$(verbosepreference)\b(?:\.tostring\(\s*\))?\s*\)?(?=\s*\[)|\[string\]\s*\$(verbosepreference)\b",
                  lambda m: _ps_q(_PS_ENV["verbosepreference"]), re.I))

    def ch(m):
        v = int(m.group(1), 0)
        return _ps_q(chr(v)) if v < 0x110000 else m.group(0)
    rules.append((r"\[char\]\s*\(?\s*(0x[0-9a-fA-F]+|\d+)\s*\)?", ch, re.I))
    rules.append((r"\[char\[\]\]\s*@?\(" + NUMS + r"\)", lambda m: "(" + ",".join(_ps_q(chr(v)) for v in _ps_nums(m.group(1))) + ")", re.I))
    rules.append((r"\(?\s*@?\(" + NUMS + r"\)\s*\|\s*(?:%|foreach-object|foreach)\s*\{\s*\[char\]\s*\$_\s*\}\s*\)?",
                  lambda m: "(" + ",".join(_ps_q(chr(v)) for v in _ps_nums(m.group(1))) + ")", re.I))
    rules.append((r"\[char\[\]\]\s*" + SG, lambda m: "(" + ",".join(_ps_q(c) for c in _ps_u(m.group(1))) + ")", re.I))
    rules.append((SG + r"\.tochararray\(\s*\)", lambda m: "(" + ",".join(_ps_q(c) for c in _ps_u(m.group(1))) + ")", re.I))

    def idx(m):
        s, body = _ps_u(m.group(1)), m.group(2)
        r = re.fullmatch(r"\s*(-?\d+)\s*\.\.\s*-?\s*\(?\s*(-?\d+|" + S + r"\.length)\s*\)?\s*", body, re.I)
        if r:
            a = int(r.group(1))
            b = -len(s) if r.group(2).lower().endswith(".length") else int(r.group(2))
            if body.replace(" ", "").split("..")[1].startswith("-") and b > 0:
                b = -b
            step = 1 if b >= a else -1
            ks = range(a, b + step, step)
        else:
            ks = _ps_nums(body.replace("-", " -").replace(" -", "-")) if re.fullmatch(r"[\s\d,\-x]+", body) else None
            if ks is None:
                try:
                    ks = [int(k) for k in body.split(",")]
                except ValueError:
                    return m.group(0)
        got = [s[k] for k in ks if -len(s) <= k < len(s)]
        if len(got) != len(list(ks)):
            return m.group(0)
        return _ps_q(got[0]) if len(got) == 1 and "," not in body and ".." not in body else "(" + ",".join(_ps_q(c) for c in got) + ")"
    rules.append((SG + r"\s*\[([^\[\]]{1,80})\]", idx, re.I))

    def rtl(m):
        return "(" + ",".join(_ps_q(c) for c in _ps_u(m.group(1))[::-1]) + ")"
    rules.append((r"\[regex\]::matches\(\s*" + SG + r"\s*,\s*'\.'\s*,\s*'righttoleft'\s*\)\s*\|\s*(?:%|foreach-object|foreach)"
                  r"\s*\{\s*\$_(?:\.value)?\s*\}", rtl, re.I))
    rules.append((r"(?<![\w\]\)\.\$])\(\s*" + SG + r"\s*\)", lambda m: m.group(1), 0))

    def fmt(m, lead=""):
        args = _ps_list(m.group(m.lastindex))
        if args is None:
            return m.group(0)
        try:
            return lead + _ps_q(_ps_format(_ps_u(m.group(m.lastindex - 1)), args))
        except (IndexError, ValueError):
            return m.group(0)
    rules.append((r"(?<![\w\]\)\.\$])\(\s*" + SG + r"\s*-f\s*((?:" + S + r"\s*,\s*)*" + S + r")\s*\)", fmt, re.I))
    rules.append((r"(?<=[=;(\n])(\s*)" + SG + r"\s*-f\s*((?:" + S + r"\s*,\s*)*" + S + r")(?=\s*[;)\n]|\s*$)",
                  lambda m: fmt(m, m.group(1)), re.I))

    def join_bin(m):
        items = _ps_list(m.group(1))
        return m.group(0) if items is None else _ps_q(_ps_u(m.group(2)).join(items))
    rules.append((r"\(\s*((?:" + S + r"\s*,\s*)*" + S + r")\s*\)\s*-join\s*" + SG, join_bin, re.I))

    def join_un(m):
        items = _ps_list(m.group(1))
        return m.group(0) if items is None else _ps_q("".join(items))
    rules.append((r"-join\s*\(\s*((?:" + S + r"\s*,\s*)*" + S + r")\s*\)", join_un, re.I))
    rules.append((r"\[string\]::join\(\s*" + SG + r"\s*,\s*\(?\s*((?:" + S + r"\s*,\s*)*" + S + r")\s*\)?\s*\)",
                  lambda m: (lambda it: m.group(0) if it is None else _ps_q(_ps_u(m.group(1)).join(it)))(_ps_list(m.group(2))), re.I))
    rules.append((SG + r"\.replace\(\s*" + SG + r"\s*,\s*" + SG + r"\s*\)",
                  lambda m: _ps_q(_ps_u(m.group(1)).replace(_ps_u(m.group(2)), _ps_u(m.group(3)))), re.I))

    def rx(m):
        a, pat, rep = _ps_u(m.group(1)), _ps_u(m.group(3)), _ps_u(m.group(4))
        if "$" in rep or t[max(0, m.start() - 8):m.start()].rstrip().endswith("+"):     # `+` binds tighter
            return m.group(0)
        try:
            return _ps_q(re.sub(pat, lambda _: rep, a, flags=0 if m.group(2).lower() == "c" else re.I))
        except re.error:
            return m.group(0)
    rules.append((SG + r"\s*-([ci]?)replace\s*" + SG + r"\s*,\s*" + SG + r"(?!\s*[\[\.+])", rx, re.I))
    def cat(m):
        before = t[max(0, m.start() - 8):m.start()].rstrip()
        if re.search(r"(?:[,.\w\]\)'*]|-f)$", before, re.I):          # `-f`, `,`, `*`, member access bind tighter
            return m.group(0)
        return _ps_q(_ps_u(m.group(1)) + _ps_u(m.group(2)))
    rules.append((SG + r"\s*\+\s*" + SG + r"(?!\s*(?:[\[\.,*]|-f\b))", cat, re.I))

    def b64s(m):
        try:
            raw = base64.b64decode(re.sub(r"\s", "", _ps_u(m.group(2))), validate=False)
            enc = {"unicode": "utf-16-le", "bigendianunicode": "utf-16-be", "utf8": "utf-8", "ascii": "latin-1",
                   "default": "latin-1", "utf32": "utf-32-le"}.get(m.group(1).lower(), "utf-8")
            return _ps_q(raw.decode(enc))
        except (ValueError, UnicodeDecodeError):
            return m.group(0)
    rules.append((r"\[(?:system\.)?text\.encoding\]::(\w+)\.getstring\(\s*\[(?:system\.)?convert\]::frombase64string\(\s*"
                  + SG + r"\s*\)\s*\)", b64s, re.I))
    for pat, fn, fl in rules:
        t2 = re.sub(pat, fn, t, flags=fl)
        if t2 != t:
            return t2
    return t


def _ps_simplify(src, budget=0.4):
    import time
    end = time.time() + budget
    t = _ps_tokens(src)
    for _ in range(400):
        if time.time() > end:
            break
        t2 = _ps_fold_once(t)
        if t2 == t:
            break
        t = t2
    return t


_PS_ENC_RE = re.compile(r"""(?:^|\s)[-/](e[a-z]*)\s+['"]?([A-Za-z0-9+/]{16,}={0,2})""", re.I)
_PS_B64ARG_RE = re.compile(r"frombase64string\(\s*'((?:[^']|'')*)'\s*\)", re.I)


def _ps_inflate(b):
    """Raw deflate that must reach its end-of-stream block (a truncated stream is no payload)."""
    import zlib
    d = zlib.decompressobj(-15)
    out = d.decompress(b, 1 << 22)
    if not d.eof:
        raise ValueError("truncated deflate")
    return out


def _ps_payloads(t):
    """Decoded payload texts in a folded PowerShell text: -EncodedCommand (UTF-16LE) and FromBase64String layers
    (Deflate/Gzip when the statement names the stream, else UTF-16LE / UTF-8 text)."""
    import gzip
    import zlib
    out = []
    for m in _PS_ENC_RE.finditer(t):
        if "encodedcommand".startswith(m.group(1).lower()) or m.group(1).lower() == "ec":
            try:
                out.append(base64.b64decode(m.group(2)).decode("utf-16-le"))
            except (ValueError, UnicodeDecodeError):
                pass
    for m in _PS_B64ARG_RE.finditer(t):
        try:
            raw = base64.b64decode(re.sub(r"\s", "", m.group(1).replace("''", "'")))
        except ValueError:
            continue
        stmt = t[max(0, m.start() - 400):m.end() + 400].lower()
        cands = []
        if "deflatestream" in stmt:
            cands.append(_ps_inflate)
        if "gzipstream" in stmt or raw[:2] == b"\x1f\x8b":
            cands.append(lambda b: gzip.decompress(b))
        if "zlibstream" in stmt or raw[:1] == b"\x78":
            cands.append(lambda b: zlib.decompress(b))
        cands.append(lambda b: b)
        for f in cands:
            try:
                b = f(raw)
            except (zlib.error, OSError, EOFError, ValueError):
                continue
            u = _utf16(b)
            try:
                out.append((u or b).decode("utf-8").lstrip("\ufeff"))
                break
            except UnicodeDecodeError:
                continue
    return out


def _ps_codecs(src, depth=0, budget=0.6):
    """find_codecs entries read from the folded PowerShell text and its decoded payload layers (up to 4 deep)."""
    import time
    try:
        if not src or len(src) > (1 << 18) or not _PS_HINT.search(src):
            return []
        end, frontier, seen = time.time() + budget, [src], {src}
        for level in range(4):
            nxt = []
            for text in frontier:
                if time.time() > end:
                    return []
                folded = _ps_simplify(text, budget=min(0.3, max(0.05, end - time.time())))
                for cand in ([folded] if level == 0 else [text, folded]):
                    if looks_like_plan(cand.strip().encode("utf-8", "ignore")):
                        return [{"id": "ps-layer", "rep": "powershell", "transform": "identity", "key": "",
                                 "material": None, "plain": cand.strip().lstrip("\ufeff")}]
                    for c in (_find_codecs_text(cand) if cand != src else []):
                        if c.get("plain"):
                            return [dict(c, id=f"{c['id']}@ps{level}")]
                for p in _ps_payloads(folded):
                    if p and p not in seen and len(seen) < 64:
                        seen.add(p)
                        nxt.append(p)
            frontier = nxt
            if not frontier:
                break
    except Exception:  # noqa: BLE001 - unknown -> nothing, never an exception
        return []
    return []


# ------------------------------------------------------------------------------------------------ batch DOSfuscation
# Target batch-substring-emulation: a .bat/.cmd that spells its plan through cmd's own expansion (Invoke-DOSfuscation
# style) instead of a HUNTRESS-MATERIAL line -- %VAR:~n,m% / !VAR:~n,m! substrings (negative n/m), %VAR:old=new% and
# %VAR:*old=new% substitution, ^ carets, setlocal EnableDelayedExpansion / cmd /V:ON !VAR!, `call set` second percent
# pass, `for /l` and `for %%G in (..)` loops. A straight-line pass (goto/exit/if are not followed: an `if` runs its
# command) records every set value and echo line; the first plan-shaped one (or one peel_plan reads) is the plain.
# Bounded by a step count; never raises. The per-day solver's batchplan.py stays the control-flow-exact reading.
_BAT_HINT = re.compile(r"(?im)^[\s@(]*(?:s\^?e\^?t|c\^?a\^?l\^?l|f\^?o\^?r)\b[^\n]*[%!]|^[\s@]*cmd(?:\.exe)?\b[^\n]*/v")
_BAT_LABEL = re.compile(r"^\s*:[^:]")


class _Bat:
    def __init__(self, delayed, max_steps=20000):
        self.env, self.delayed, self.steps, self.max_steps = {}, delayed, 0, max_steps
        self.seen = []                                   # set values and echo lines, in execution order

    def var(self, body):
        m = re.match(r"^([^:]+):~\s*(-?\d+)\s*(?:,\s*(-?\d+))?\s*$", body)
        if m:
            v = self.env.get(m.group(1).lower())
            if v is None:
                return None
            a = int(m.group(2))
            a = max(len(v) + a, 0) if a < 0 else min(a, len(v))
            if m.group(3) is None:
                return v[a:]
            b = int(m.group(3))
            return v[a:a + b] if b >= 0 else v[a:max(len(v) + b, a)]
        m = re.match(r"^([^:]+):(\*?)([^=]*)=(.*)$", body, re.S)
        if m:
            v = self.env.get(m.group(1).lower())
            if v is None or not m.group(3):
                return v
            if m.group(2):
                i = v.lower().find(m.group(3).lower())
                return v if i < 0 else m.group(4) + v[i + len(m.group(3)):]
            return re.sub(re.escape(m.group(3)), lambda _: m.group(4), v, flags=re.I)
        return self.env.get(body.lower())

    def percent(self, s, batch_file=True):
        out, i, n = [], 0, len(s)
        while i < n:
            c = s[i]
            if c != "%":
                out.append(c); i += 1; continue
            if batch_file and s.startswith("%%", i):
                out.append("%"); i += 2; continue
            m = re.match(r"%(?:~[a-zA-Z]*)?[0-9*]", s[i:]) if batch_file else None
            if m:                                        # %1 / %~dp0 / %*: no arguments
                i += len(m.group(0)); continue
            j = s.find("%", i + 1)
            if j < 0:
                if not batch_file:
                    out.append(c)
                i += 1; continue
            v = self.var(s[i + 1:j]) if j > i + 1 else None
            if v is None:
                if batch_file:
                    i = j + 1
                else:
                    out.append(s[i:j]); i = j
                continue
            out.append(v); i = j + 1
        return "".join(out)

    def delayed_exp(self, s):
        if not self.delayed or "!" not in s:
            return s
        out, i, n = [], 0, len(s)
        while i < n:
            c = s[i]
            if c == "^":                                 # a line holding '!' loses one more level of carets
                if i + 1 < n:
                    out.append(s[i + 1])
                i += 2; continue
            if c != "!":
                out.append(c); i += 1; continue
            j = s.find("!", i + 1)
            if j < 0:
                i += 1; continue
            out.append(self.var(s[i + 1:j]) or "")
            i = j + 1
        return "".join(out)

    @staticmethod
    def split_ops(s):
        """Unquoted, unescaped & && || | -> [(cmd, op_before)]; carets outside quotes consumed (escaped char kept)."""
        parts, cur, op, q, i, n, depth = [], [], None, False, 0, len(s), 0
        while i < n:
            c = s[i]
            if c == '"':
                q = not q; cur.append(c); i += 1; continue
            if not q and c == "^":
                if i + 1 < n:
                    cur.append(s[i + 1])
                i += 2; continue
            if not q:
                depth += (c == "(") - (c == ")")
            if not q and depth <= 0 and c in "&|":
                dbl = i + 1 < n and s[i + 1] == c
                parts.append(("".join(cur), op))
                op, cur = c * 2 if dbl else c, []
                i += 2 if dbl else 1; continue
            cur.append(c); i += 1
        parts.append(("".join(cur), op))
        return parts

    def line(self, s, batch_file=True, depth=0):
        s = self.percent(s, batch_file)
        for cmd, op in self.split_ops(s):
            if op != "|":                                # right side of a pipe: output only
                self.cmd(cmd.strip(), batch_file, depth)

    def _set(self, rest):
        rest = rest.strip()
        if re.match(r"(?i)/p\b", rest):
            return
        if re.match(r"(?i)/a\b", rest):                  # only `set /a n=<int>` (loop bounds / offsets)
            m = re.match(r'(?i)/a\s*"?\s*([^\s="]+)\s*=\s*(-?\d+)\s*"?\s*$', rest)
            if m:
                self.env[m.group(1).lower()] = str(int(m.group(2)))
            return
        if rest.startswith('"'):
            end = rest.rfind('"')
            rest = rest[1:end] if end > 0 else rest[1:]
        if "=" not in rest:
            return
        name, val = rest.split("=", 1)
        name = name.strip().lower()
        if not name:
            return
        if val:
            self.env[name] = val
            self.seen.append(val)
        else:
            self.env.pop(name, None)

    def cmd(self, c, batch_file, depth):
        self.steps += 1
        if not c or depth > 6 or self.steps > self.max_steps:
            return
        while c.startswith("(") and c.endswith(")"):
            c = c[1:-1].strip()
        c = c.lstrip("@( ").rstrip(") ") if c.count("(") != c.count(")") else c.lstrip("@ ")
        if not c:
            return
        low = c.lower()
        word = re.match(r"[^\s(.:;,/\\\[\]+=]*", low).group(0)
        if word == "rem" or low.startswith("::"):
            return
        if word == "setlocal":
            if re.search(r"enabledelayedexpansion", low):
                self.delayed = True
            return
        if word == "echo":
            body = c[5:] if len(c) > 4 else ""
            if low.strip() not in ("echo off", "echo on", "echo"):
                self.seen.append(self.delayed_exp(body).rstrip())
            return
        if word == "for":                                # its body expands !vars! per iteration
            return self._for(c, batch_file, depth)
        c = self.delayed_exp(c)
        if word == "set":
            self._set(c[3:])
        elif word == "call":
            rest = c[4:].strip()
            if rest and not rest.startswith(":"):
                self.line(rest, batch_file, depth + 1)
        elif word == "if":
            m = re.match(r'(?i)if\s+(?:/i\s+)?(?:not\s+)?(?:(?:defined|exist|errorlevel|cmdextversion)\s+\S+|'
                         r'"[^"]*"\s*(?:==|equ|neq|lss|leq|gtr|geq)\s*"[^"]*"|\S+?\s*==\s*\S+)\s*(.*)$', c, re.S)
            if m:
                body = re.split(r"\)\s*else\s*\(?", m.group(1), maxsplit=1, flags=re.I)[0]
                self.cmd(body.strip(), batch_file, depth + 1)
        elif word in ("cmd", "cmd.exe") or re.match(r"[^\s]*\\cmd(?:\.exe)?$", word):
            m = re.search(r'(?i)/[ck]\s+(.*)$', c, re.S)
            if m:
                inner = m.group(1).strip()
                if inner.startswith('"') and inner.endswith('"'):
                    inner = inner[1:-1]
                child = _Bat(self.delayed or bool(re.search(r"(?i)/v(?::?on)?\b", c[:m.start()])),
                             self.max_steps - self.steps)
                child.env = dict(self.env)
                child.line(inner, batch_file=False, depth=depth + 1)
                self.steps += child.steps
                self.seen.extend(child.seen)

    def _for(self, c, batch_file, depth):
        m = re.match(r'(?i)for\s+(/l\s+|/f\s+(?:"[^"]*"\s+)?)?%%?([A-Za-z])\s+in\s*\((.*?)\)\s*do\s+(.*)$', c, re.S)
        if not m:
            return
        flag, letter, lst, body = (m.group(1) or "").strip().lower(), m.group(2), m.group(3), m.group(4)
        if flag.startswith("/l"):
            nums = [int(x) for x in re.findall(r"-?\d+", lst)][:3]
            if len(nums) != 3 or nums[1] == 0:
                return
            a, st, e = nums
            items = [str(x) for x in range(a, e + (1 if st > 0 else -1), st)][:8192]
        elif flag.startswith("/f"):
            lm = re.match(r'\s*"(.*)"\s*$', lst, re.S)        # only a literal string, first token
            if not lm:
                return
            items = (lm.group(1).split() or [""])[:1]
        else:
            items = [t for t in re.split(r'[\s,;=]+', lst) if t][:4096]
        pat = re.compile(r"%~?" + re.escape(letter))
        for it in items:
            if self.steps > self.max_steps:
                return
            self.cmd(pat.sub(lambda _: it, body).strip(), batch_file, depth + 1)


def _bat_run(src, max_steps=20000):
    """Straight-line emulation of a batch source -> the _Bat (its `seen` set values / echo lines)."""
    text = (src or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(?<!\^)\^\n", "", text)              # caret line continuation
    b = _Bat(False, max_steps)
    for ln in text.split("\n")[:5000]:
        if b.steps > max_steps:
            break
        s = ln.strip()
        if not s or s.startswith("::") or _BAT_LABEL.match(s):
            continue
        b.line(s)
    return b


def _bat_codecs(src, budget=0.4):
    """find_codecs fallback for DOSfuscated batch: the plan a set/echo spells once cmd's expansions are applied."""
    import time
    try:
        if not src or not _BAT_HINT.search(src):
            return []
        b = _bat_run(src)
        seen, end = [], time.time() + budget
        for v in reversed(b.seen):                       # later values are the assembled ones
            v = v.strip()
            if v and v not in seen:
                seen.append(v)
        for v in seen:
            if looks_like_plan(v.encode("utf-8", "ignore")):
                return [{"id": "batch_emu", "rep": "batch_expansion", "transform": "identity", "key": "",
                         "material": v, "plain": v}]
        for v in seen[:24]:
            tok = re.fullmatch(r"[A-Za-z0-9+/=_\-:%.]{24,}", v)
            if tok and time.time() < end:
                plain = peel_plan(v, budget=min(0.2, max(0.02, end - time.time())))
                if plain:
                    return [{"id": "batch_emu", "rep": "batch_expansion", "transform": "identity", "key": "",
                             "material": v, "plain": plain}]
    except Exception:  # noqa: BLE001 - unknown -> nothing, never an exception
        return []
    return []


# ------------------------------------------------------------------------------------------------ container carriers
# Target container-carrier-extract: the script rides inside a container (OOXML zip -> vbaProject.bin, OLE .doc/.xls,
# LNK StringData, OneNote FileDataStoreObject, gzip, pyc constants, UTF-16LE .reg/.ps1). find_codecs() falls back to
# this only when the text itself yields no plan: from raw bytes (find_codecs(bytes)), latin-1 text, or -- when the
# caller decoded utf-8 'ignore'/'replace' -- whatever survived (UTF-16LE runs keep their NULs). Each member text goes
# through the text readings, then a bounded peel of its long material-charset tokens. Pure python, bounded, never raises.
# CHM content (LZX-compressed section) is NOT decompressed: only its uncompressed bytes/UTF-16 runs are scanned.
_ONE_FDSO = bytes.fromhex("e716e3bd65261145a4c48d4d0b7a9eac")      # {BDE316E7-2665-4511-A4C4-8D4D0B7A9EAC}
_MAGICS = (b"PK\x03\x04", b"\xd0\xcf\x11\xe0", b"\x1f\x8b", b"L\x00\x00\x00\x01\x14\x02\x00",
           bytes.fromhex("e4525c7b8cd8a74daeb15378d02996d3"), b"ITSF")
_U16_RUN = re.compile(rb"(?:[\t\n\r\x20-\x7e]\x00){12,}")
_U16_RUN_S = re.compile(r"(?:[\t\n\r\x20-\x7e]\x00){12,}")
_MAT_TOKEN = re.compile(r"[A-Za-z0-9+/=_\-:%.]{24,}")


def _ovba_decompress(b, i):
    """MS-OVBA CompressedContainer at b[i] (signature 0x01) -> bytes, or None if it is not one."""
    if i >= len(b) or b[i] != 1:
        return None
    out, i = bytearray(), i + 1
    while i + 2 <= len(b) and len(out) < (1 << 22):
        hdr = b[i] | b[i + 1] << 8
        if (hdr >> 12) & 7 != 3:
            return bytes(out) if out else None
        chunk, i = b[i + 2:i + (hdr & 0xFFF) + 3], i + (hdr & 0xFFF) + 3
        if not hdr >> 15:
            out += chunk[:4096]
            continue
        start, j = len(out), 0
        while j < len(chunk):
            fb, j = chunk[j], j + 1
            for bit in range(8):
                if j >= len(chunk):
                    break
                if not fb >> bit & 1:
                    out.append(chunk[j])
                    j += 1
                    continue
                if j + 1 >= len(chunk):
                    return None
                tok, j = chunk[j] | chunk[j + 1] << 8, j + 2
                bc = max((len(out) - start - 1).bit_length(), 4)
                ln, off = (tok & (0xFFFF >> bc)) + 3, (tok >> (16 - bc)) + 1
                if off > len(out) - start:
                    return None
                for _ in range(ln):
                    out.append(out[-off])
    return bytes(out) if out else None


def _vba_sources(s):
    """VBA module source(s) in an OLE module stream: the compressed container after the p-code (validated by
    `Attribute VB_`), tried from the last candidate signature backwards."""
    cands = [m.start() for m in re.finditer(rb"\x01[\x00-\xff][\xb0-\xbf]", s)][-48:]
    for i in reversed(cands):
        src = _ovba_decompress(s, i)
        if src and b"Attribute VB_" in src[:400]:
            return src
    return None


def _carrier_blobs(b, name="", depth=0, budget=None):
    """(member name, bytes) of every stream inside a container, recursively (zip / OLE+VBA / gzip / OneNote)."""
    import io
    import time
    import zlib
    budget = budget if budget is not None else time.time() + 0.8
    if depth > 3 or time.time() > budget or len(b) < 8:
        return
    yield name, b
    try:
        if b[:4] == b"PK\x03\x04":
            import zipfile
            z = zipfile.ZipFile(io.BytesIO(b))
            for zi in z.infolist()[:200]:
                if zi.is_dir() or zi.flag_bits & 1 or zi.file_size > (8 << 20):
                    continue
                try:
                    yield from _carrier_blobs(z.read(zi), f"{name}/{zi.filename}", depth + 1, budget)
                except Exception:  # noqa: BLE001 - one bad member, keep walking
                    continue
        elif b[:4] == b"\xd0\xcf\x11\xe0":
            import olefile
            ole = olefile.OleFileIO(io.BytesIO(b))
            for ent in ole.listdir()[:300]:
                if ole.get_size("/".join(ent)) > (8 << 20):
                    continue
                s = ole.openstream(ent).read()
                if len(ent) >= 2 and ent[-1].lower() not in ("dir", "_vba_project") and \
                        not ent[-1].startswith("__SRP_") and ole.exists("/".join(ent[:-1] + ["dir"])):
                    src = _vba_sources(s)
                    if src:
                        yield f"{name}:{'/'.join(ent)}", src
                        continue
                yield from _carrier_blobs(s, f"{name}:{'/'.join(ent)}", depth + 1, budget)
        elif b[:2] == b"\x1f\x8b":
            yield from _carrier_blobs(zlib.decompressobj(31).decompress(b, 1 << 22), name + "|gunzip", depth + 1, budget)
        else:
            i = b.find(_ONE_FDSO)
            while 0 <= i and i + 36 <= len(b):
                n = int.from_bytes(b[i + 16:i + 24], "little")
                if 0 < n <= len(b) - i - 36:
                    yield from _carrier_blobs(b[i + 36:i + 36 + n], f"{name}#one@{i}", depth + 1, budget)
                i = b.find(_ONE_FDSO, i + 16)
    except Exception:  # noqa: BLE001 - truncated / impostor container: keep what was yielded
        return


def _carrier_texts(src, raw):
    """(member, text) candidates for a carrier: decoded member streams plus their UTF-16LE runs."""
    if raw is None and src:
        try:
            raw = src.encode("latin-1") if max(src) < "Ā" else src.encode("utf-8", "surrogateescape")
        except (UnicodeEncodeError, ValueError):
            raw = None
    out = []
    if raw and (raw[:4] in (m[:4] for m in _MAGICS) or raw[:16] in _MAGICS or b"\x00" in raw[:1 << 16]):
        for name, b in _carrier_blobs(raw):
            u = _utf16(b) if b[:2] in (b"\xff\xfe", b"\xfe\xff") else None
            if name and b[:4] not in (m[:4] for m in _MAGICS):
                out.append((name, (u or b).decode("utf-8", "ignore")))
            out.extend((name + "~u16", r.decode("utf-16-le")) for r in _U16_RUN.findall(b)[:64])
    elif src and "\x00" in src:                      # lossy utf-8 decode of a carrier: the UTF-16LE runs survive
        out.extend(("~u16", r.encode("latin-1").decode("utf-16-le")) for r in _U16_RUN_S.findall(src)[:64])
    if src and "\x00" in src and not out:
        out.append(("", src))
    return out


def _carrier_codecs(src, raw, depth=0):
    import time
    try:
        texts = _carrier_texts(src, raw)
        end = time.time() + 0.6
        for name, text in texts:
            for c in _find_codecs_text(text):
                if c.get("plain"):
                    return [dict(c, id=f"{c['id']}@{name}" if name else c["id"])]
        seen = set()
        for name, text in texts + ([("", src)] if src and "\x00" in src else []):
            for tok in _MAT_TOKEN.findall(text)[:48]:
                if tok in seen or time.time() > end:
                    continue
                seen.add(tok)
                plain = peel_plan(tok, budget=min(0.15, max(0.02, end - time.time())))
                if plain:
                    return [{"id": f"carrier@{name}", "rep": "carrier", "transform": "identity", "key": "",
                             "material": tok, "plain": plain}]
    except Exception:  # noqa: BLE001 - unknown -> nothing, never an exception
        return []
    return []


# ------------------------------------------------------------------------------------------------ encode (inverse)
# For synthetic "family" regression cases (hctf/family.py): re-encode a fixture's plaintext under ANOTHER known
# rep x transform, so a solver that decodes codecs by name/table instead of through decode() fails offline instead of
# on the next timed variant (rehearsal Day 7 replay: a second TT generalize for one more member of the same codec family).
# The written FORMAT of a rep is copied from a real material `sample` of that rep (separators, 0x prefix, case,
# brackets); every result is verified by decode() and None is returned if it doesn't round-trip.

def _encode_transform(p, transform, key):
    t, inline = _base_transform(transform)
    k = key_bytes(inline if inline is not None else key)
    k1 = k[0] if k else None
    if t == "identity":
        return p
    if t in ("reverse", "reverse_bytes"):
        return p[::-1]
    if t.startswith("xor_") or t in ("single_byte_xor", "repeating_key_xor"):
        return _xor(p, k) if k else None
    if t.startswith("add_"):
        return bytes((x + k1) % 256 for x in p) if k1 is not None else None
    if t.startswith(("sub_", "subtract_")):
        return bytes((x - k1) % 256 for x in p) if k1 is not None else None
    if t in ("reverse_then_xor", "reverse_xor"):
        return _xor(p, k or b"\x5a")[::-1]
    if t == "rolling_xor":
        if k1 is None:
            return None
        out, prev = bytearray(), k1
        for x in p:
            c = x ^ prev
            out.append(c)
            prev = c
        return bytes(out)
    if t in ("rotate_left", "rol"):
        n = int(inline, 16) % 8 if inline else (k1 % 8 if k1 else 0)
        return bytes(((x << n) | (x >> (8 - n))) & 0xFF for x in p) if n else None
    return None


def _format_like(data, rep, sample):
    """Write `data` the way `sample` (a real material of `rep`) is written."""
    if rep.startswith(("hex_base64", "hex_b64")):   # hex digits of the base64 text (D8 v=3 HB64), case like the sample
        s = base64.b64encode(data).hex()
        return s.upper() if sample and re.search(r"[A-F]", sample) and not re.search(r"[a-f]", sample) else s
    if "base64" in rep:
        s = base64.b64encode(data).decode()
        if "urlsafe" in rep or (sample and re.search(r"[-_]", sample) and not re.search(r"[+/]", sample)):
            s = base64.urlsafe_b64encode(data).decode()
        if sample and not sample.rstrip().endswith("=") and not rep.startswith("reversed"):
            s = s.rstrip("=")
        return s[::-1] if rep.startswith("reversed") else s
    if rep == "percent_hex":
        return "".join(f"%{b:02x}" for b in data)
    if not sample:
        return None
    if rep.startswith("octal"):
        tok, radix = re.compile(r"[0-7]+"), 8
    elif "hex" in rep:
        tok, radix = re.compile(r"(?:0[xX]|\\x|&[hH])?[0-9a-fA-F]{2}"), 16
    elif rep.startswith(("decimal", "integer", "json_num", "reversed_decimal", "reversed_integer")):
        tok, radix = re.compile(r"\d+"), 10
    else:
        return None
    toks = list(tok.finditer(sample))
    if len(toks) < 2:
        return None
    pre, sep, suf = sample[:toks[0].start()], sample[toks[0].end():toks[1].start()], sample[toks[-1].end():]
    t0 = toks[0].group(0)
    prefix = re.match(r"0[xX]|\\x|&[hH]", t0)
    prefix = prefix.group(0) if prefix else ""
    upper = any(c in "ABCDEF" for m in toks for c in m.group(0)[len(prefix):])
    width = len(t0) - len(prefix) if (radix != 10 or t0.startswith("0")) else 0
    vals = list(data[::-1] if rep.startswith(("reversed_decimal", "reversed_integer", "reversed_hex")) else data)
    if radix == 16:
        body = [f"{v:0{max(2, width)}{'X' if upper else 'x'}}" for v in vals]
    elif radix == 8:
        body = [f"{v:0{width}o}" for v in vals]
    else:
        body = [f"{v:0{width}d}" if width else str(v) for v in vals]
    return pre + sep.join(prefix + b for b in body) + suf


def encode(plain, rep, transform, key=None, sample=None):
    """Material text that decode(material, rep, transform, key) turns back into `plain` (bytes or str), or None.
    `sample` = a real material written in `rep` (its format is copied). Only known names; result verified."""
    if isinstance(plain, str):
        plain = plain.encode("utf-8")
    if not known(rep, None):
        return None
    t, k = _spec(rep, transform, key)
    if not known(None, t):
        return None
    data = _encode_transform(plain, t, k)
    if data is None:
        return None
    mat = _format_like(data, rep, sample)
    if not mat:
        return None
    try:
        back = decode(mat, rep, transform, key)
    except Exception:  # noqa: BLE001
        back = None
    return mat if back == plain.decode("utf-8", "replace").lstrip("﻿") else None


# ------------------------------------------------------------------------------------------------ decode call chains
# Target php-eval-chain: `@eval(gzinflate(base64_decode(str_rot13('..'))))` onions (PHP webshells) and the same shape in
# Ruby (`eval(Zlib::Inflate.inflate('..'.unpack1('m')))`, `[".."].pack('H*')`), Python (`exec(zlib.decompress(
# base64.b64decode(b'..')))`, `codecs.decode(x,'rot13')`, `[::-1]`) and Perl (`eval uncompress decode_base64 '..'`,
# `pack('H*', ..)`, `scalar reverse`). A tiny expression parser (calls, paren-less known calls, method/postfix chains,
# literal concatenation, `$var`/name assignments) evaluates each NAMED decoder innermost-first; wrappers it does not
# know (eval/exec/assert/print...) pass their first argument through. A decoded layer that is code again is re-read
# (up to 4 levels); the result must be a plan (looks_like_plan, else peel_plan). Only consulted when nothing else
# produced a plan, so every earlier reading is unchanged. Bounded (budget seconds, node count), never raises.
_CH_B64 = {"base64_decode", "b64decode", "standard_b64decode", "urlsafe_b64decode", "decode64", "decode_base64",
           "urlsafe_decode64", "strict_decode64", "decodebase64", "frombase64string", "atob", "a2b_base64",
           "decodebytes", "decodestring", "base64decode", "mime_base64_decode"}
_CH_INFL = {"gzinflate", "gzuncompress", "gzdecode", "zlib_decode", "inflate", "decompress", "uncompress",
            "memgunzip", "gunzip", "inflateraw", "inflatesync", "gunzipsync", "inflaterawsync", "unzip",
            "zlib_decompress", "bz2_decompress", "bzdecompress", "lzma_decompress", "memgunzip_s"}
_CH_HEX = {"hex2bin", "unhexlify", "fromhex", "a2b_hex", "hex_decode", "hexdecode", "b16decode"}
_CH_URL = {"urldecode", "rawurldecode", "unquote", "unquote_plus", "unquote_to_bytes", "decodeuricomponent",
           "unescape", "decode_www_form_component", "uri_unescape", "url_decode"}
_CH_ALL = (_CH_B64 | _CH_INFL | _CH_HEX | _CH_URL |
           {"str_rot13", "rot13", "strrev", "reverse", "convert_uudecode", "a2b_uu", "uudecode", "b32decode",
            "base32_decode", "b85decode", "a85decode", "quoted_printable_decode", "pack", "unpack", "unpack1",
            "decode", "tr", "eval", "assert", "exec", "create_function", "instance_eval", "class_eval",
            "module_eval", "preg_replace", "system", "compile"})
_CH_START = re.compile(r"(?<![\w$>.:\\])[@\\]*(?:[A-Za-z_][\w]*(?:(?:::|\.|->|\\)[A-Za-z_]\w*)*)(?=\s*[(\s'\"$\[])")
_CH_QOP = re.compile(r"(qq|q|%[qQ]|%)\s*([{(\[<|/!])")
_CH_PAIR = {"{": "}", "(": ")", "[": "]", "<": ">"}
_CH_LIT_PLAN = re.compile(r"""(["'])((?:v=\d+\||\{)[^\n]{8,}?)\1|\b(?:qq?|%[qQ]?)\s*\{((?:v=\d+\||\{)[^\n]{8,}?)\}""")
_CH_DQ_ESC = {"n": "\n", "r": "\r", "t": "\t", "0": "\0", "e": "\x1b", "f": "\f", "v": "\v", "a": "\a", "b": "\b"}


def _ch_unescape(body, q):
    if "\\" not in body:
        return body
    if q == "'":
        return re.sub(r"\\([\\'])", r"\1", body)

    def sub(m):
        s = m.group(1)
        if s[0] in "xX":
            return chr(int(s[1:], 16))
        if s[0] == "u":
            return chr(int(s[1:].strip("{}"), 16))
        if s[0] in "01234567":
            return chr(int(s, 8) & 0xFF)
        return _CH_DQ_ESC.get(s, s)
    return re.sub(r"\\(x[0-9a-fA-F]{1,2}|u\{[0-9a-fA-F]{1,6}\}|u[0-9a-fA-F]{4}|[0-7]{1,3}|.)", sub, body, flags=re.S)


def _ch_uu(b):
    out = bytearray()
    for line in b.split(b"\n"):
        line = line.rstrip(b"\r")
        if not line or line.startswith((b"begin ", b"end")):
            continue
        try:
            out += binascii.a2b_uu(line)
        except binascii.Error:
            try:                                         # lenient: trailing garbage on a short final line
                n = (line[0] - 32) & 63
                out += binascii.a2b_uu(line[:1 + (n + 2) // 3 * 4])
            except (binascii.Error, IndexError):
                return None
    return bytes(out) or None


class _Chain:
    def __init__(self, src, end, depth=0):
        self.s, self.end, self.depth, self.nodes = src, end, depth, 0

    # -- lexing helpers
    def ws(self, i):
        s = self.s
        while i < len(s):
            if s[i] in " \t\r\n":
                i += 1
            elif s.startswith("\\\n", i):
                i += 2
            else:
                break
        return i

    def literal(self, i):
        """(text, j) for a quoted literal at i (b/r/u prefixes, PHP/Python/Ruby/Perl quoting), else None."""
        s = self.s
        pm = _CH_QOP.match(s, i)
        if pm:                                            # Perl q{..} / qq{..}, Ruby %q{..} / %Q{..}
            close = _CH_PAIR.get(pm.group(2), pm.group(2))
            j = s.find(close, pm.end())
            if j < 0:
                return None
            body = s[pm.end():j]
            return (body if pm.group(1).lower() in ("q", "%q") else _ch_unescape(body, '"')), j + 1
        m = re.compile(r"""[bBrRuUfF]{0,2}(\"\"\"|'''|"|')""").match(s, i)
        if not m:
            return None
        q, raw = m.group(1), "r" in m.group(0).lower()
        j, body = m.end(), []
        while j < len(s):
            if s.startswith(q, j):
                t = "".join(body)
                return (t if raw else _ch_unescape(t, q[0] if len(q) == 1 or q[0] == "'" else '"')), j + len(q)
            if s[j] == "\\" and j + 1 < len(s):
                body.append(s[j:j + 2])
                j += 2
                continue
            body.append(s[j])
            j += 1
        return None

    # -- expression parser: returns (value, j); value = bytes | list | ("name", qualified) | None
    def expr(self, i, lvl=0):
        self.nodes += 1
        if lvl > 40 or self.nodes > 4000 or time.time() > self.end:
            raise ValueError("budget")
        v, i = self.postfix(*self.primary(i, lvl), lvl)
        while True:
            j = self.ws(i)
            m = re.compile(r"\.\.|\.(?![\w(])|\+(?!\+)").match(self.s, j)
            if not m and j < len(self.s) and self.s[j] in "'\"" and isinstance(v, bytes):
                m2 = self.literal(j)                       # Python implicit 'a' 'b' concatenation
                if m2:
                    v, i = v + m2[0].encode("latin-1", "ignore"), m2[1]
                    continue
            if not m:
                return v, i
            w, k = self.postfix(*self.primary(self.ws(m.end()), lvl + 1), lvl + 1)
            if not (isinstance(v, bytes) and isinstance(w, bytes)):
                return v, i
            v, i = v + w, k

    def primary(self, i, lvl):
        s = self.s
        i = self.ws(i)
        while i < len(s) and s[i] in "@\\":
            i += 1
        if i >= len(s):
            return None, i
        lit = self.literal(i)
        if lit:
            return lit[0].encode("latin-1", "ignore") if max(map(ord, lit[0] or "\0")) < 256 \
                else lit[0].encode("utf-8"), lit[1]
        if s[i] == "(":
            v, j = self.expr(i + 1, lvl + 1)
            j = self.ws(j)
            return v, (j + 1 if j < len(s) and s[j] == ")" else j)
        if s[i] == "[":
            items, j = self.args(i + 1, "]", lvl)
            return items, j
        m = re.compile(r"\$?[A-Za-z_]\w*(?:(?:::|\.|->|\\)[A-Za-z_]\w*)*").match(s, i)
        if not m:
            return None, i
        name, j = m.group(0), m.end()
        parts = re.split(r"::|\.|->|\\", name)
        head = self.var(parts[0], i)
        if head is not None:                              # `x.decode('hex')`: a value with method calls
            v = head
            for p in parts[1:-1]:
                v = self.apply(p, [v])
            if len(parts) == 1:
                return v, j
            k = self.ws(j)
            if k < len(s) and s[k] == "(":
                a, j = self.args(k + 1, ")", lvl)
                return self.apply(parts[-1], [v] + a), j
            return self.apply(parts[-1], [v]), j
        k = self.ws(j)
        last = parts[-1].lower()
        if k < len(s) and s[k] == "(":
            a, j = self.args(k + 1, ")", lvl)
            return self.apply(last, a, name), j
        if last in _CH_ALL and k > j and k < len(s) and (s[k] in "'\"$@[(" or s[k].isalpha()):
            v, j = self.expr(k, lvl + 1)                  # Ruby/Perl paren-less call `decode64 x` / `scalar reverse`
            return self.apply(last, [v], name), j
        if last in ("scalar", "my", "our", "local", "return", "print", "echo", "puts", "do", "eval"):
            return self.expr(k, lvl + 1)
        return ("name", name), j

    def args(self, i, close, lvl):
        out, s = [], self.s
        i = self.ws(i)
        if i < len(s) and s[i] == close:
            return out, i + 1
        while i < len(s):
            v, i = self.expr(i, lvl + 1)
            out.append(v)
            i = self.ws(i)
            if i < len(s) and s[i] == ",":
                i = self.ws(i + 1)
                if i < len(s) and s[i] == close:
                    return out, i + 1
                continue
            if i < len(s) and s[i] == close:
                return out, i + 1
            if i < len(s) and s[i] == ":" and close == "]":   # slice [::-1]
                m = re.compile(r"[\s:]*(-?\d*)\s*\]").match(s, i)
                if m:
                    out = [("slice", s[i:m.end()])] if not out or out == [None] else out + [("slice", s[i:m.end()])]
                    return out, m.end()
            if i < len(s) and s[i] == ":":
                m = re.compile(r":\s*:\s*-1\s*\]").match(s, i)
                if m:
                    return out + [("slice", "::-1")], m.end()
            return out, i
        return out, i

    def postfix(self, v, i, lvl):
        s = self.s
        while True:
            j = self.ws(i)
            if s.startswith("[", j):
                m = re.compile(r"\[\s*:\s*:\s*-1\s*\]|\[\s*(-?\d+)\s*\]").match(s, j)
                if not m:
                    return v, i
                if m.group(1) is None:
                    v = v[::-1] if isinstance(v, (bytes, list)) else v
                elif isinstance(v, list):
                    try:
                        v = v[int(m.group(1))]
                    except IndexError:
                        v = None
                i = m.end()
                continue
            m = re.compile(r"(?:\.|->|&\.)\s*([A-Za-z_]\w*[!?]?)").match(s, j)
            if not m or (isinstance(v, bytes) and s[j] == "." and j > i):
                return v, i
            name, k = m.group(1).rstrip("!?"), self.ws(m.end())
            if k < len(s) and s[k] == "(":
                a, i = self.args(k + 1, ")", lvl)
            else:
                a, i = [], m.end()
            v = self.apply(name, [v] + a)

    def var(self, name, at):
        """The value last assigned to `name` before offset `at` (`$x = ..;`, `x = ..`, `my $x = ..`), else None."""
        if name.lower() in _CH_ALL or self.depth > 3:
            return None
        bare = name.lstrip("$")
        pat = re.compile(r"(?:^|[;\n{(])\s*(?:(?:my|our|local|var|let|const)\s+)?\$?" + re.escape(bare) +
                         r"\s*(?:\.=|=)(?![=~>])")
        hit = None
        for m in pat.finditer(self.s, 0, at):
            hit = m
        if not hit:
            return None
        sub = _Chain(self.s, self.end, self.depth + 1)
        sub.nodes = self.nodes
        try:
            v, _ = sub.expr(hit.end())
        except ValueError:
            return None
        self.nodes = sub.nodes
        return v if isinstance(v, (bytes, list)) else None

    # -- evaluation
    def apply(self, name, a, qual=""):
        n = (name or "").lower()
        qual = (qual or "").lower()
        v = next((x for x in a if isinstance(x, (bytes, list))), None)
        sargs = [x.decode("latin-1") for x in a[1:] if isinstance(x, bytes)] if a else []
        if n == "pack":
            fmt = next((x for x in a if isinstance(x, bytes) and re.fullmatch(rb"[A-Za-z]\*?\d*", x)), None)
            data = next((x for x in (a[1:] if a and a[0] is fmt else a) if x is not fmt), None)
            if isinstance(data, list):                    # Ruby ["..."].pack('H*')
                data = data[0] if data and isinstance(data[0], bytes) else None
            if fmt is None and len(a) >= 2 and isinstance(a[0], list):
                data, fmt = (a[0][0] if a[0] and isinstance(a[0][0], bytes) else None), a[1]
            f = (fmt or b"").decode("latin-1")[:1]
            if not isinstance(data, bytes):
                return None
            return hex_bytes(data.decode("latin-1")) if f == "H" else (b64(data.decode("latin-1")) if f == "m"
                                                                      else _ch_uu(data) if f == "u" else None)
        if n in ("unpack", "unpack1"):
            fmt = next((x for x in a[1:] if isinstance(x, bytes)), None) if len(a) > 1 else None
            data = a[0] if a else None
            if isinstance(fmt, bytes) and isinstance(data, bytes) and re.fullmatch(rb"[A-Za-z]\*?\d*", data) \
                    and not re.fullmatch(rb"[A-Za-z]\*?\d*", fmt):
                fmt, data = data, fmt                     # Perl unpack('u', $x)
            if not isinstance(data, bytes) or not isinstance(fmt, bytes):
                return None
            f = fmt.decode("latin-1")[:1]
            r = b64(data.decode("latin-1")) if f == "m" else _ch_uu(data) if f == "u" else None
            return r if n == "unpack1" or r is None else [r]
        if isinstance(v, list):
            v = v[0] if v and isinstance(v[0], bytes) else None
        if not isinstance(v, bytes):
            return None if n in _CH_ALL else v
        t = v.decode("latin-1")
        if n == "decode" and sargs:                       # Python codecs.decode(x, 'rot13') / x.decode('base64')
            c = sargs[0].lower().replace("-", "_")
            n = {"rot13": "rot13", "rot_13": "rot13", "base64": "b64decode", "base_64": "b64decode",
                 "hex": "unhexlify", "zlib": "decompress", "zip": "decompress", "bz2": "decompress",
                 "uu": "a2b_uu", "quopri": "quoted_printable_decode"}.get(c, "identity")
        if n in _CH_B64:
            return b64(t)
        if n in _CH_INFL or (n == "new" and "gzip" in qual):
            return _inflate(v)
        if n in _CH_HEX:
            return hex_bytes(t)
        if n in _CH_URL:
            from urllib.parse import unquote_to_bytes
            return unquote_to_bytes(t.replace("+", " ") if n in ("urldecode", "unquote_plus",
                                                                  "decode_www_form_component") else t)
        if n in ("str_rot13", "rot13"):
            return t.translate(_ROT13_S).encode("latin-1")
        if n == "tr" and len(sargs) >= 2 and sargs[0].replace(" ", "") in ("A-Za-z", "a-zA-Z") and \
                sargs[1].replace(" ", "") in ("N-ZA-Mn-za-m", "n-za-mN-ZA-M"):
            return t.translate(_ROT13_S).encode("latin-1")
        if n in ("strrev", "reverse"):
            return v[::-1]
        if n in ("convert_uudecode", "a2b_uu", "uudecode"):
            return _ch_uu(v)
        if n in ("b32decode", "base32_decode"):
            s = re.sub(r"\s+", "", t).upper().rstrip("=")
            try:
                return base64.b32decode(s + "=" * (-len(s) % 8))
            except (binascii.Error, ValueError):
                return None
        if n in ("b85decode", "a85decode"):
            try:
                return (base64.b85decode if n == "b85decode" else base64.a85decode)(t.strip())
            except (binascii.Error, ValueError):
                return None
        if n == "quoted_printable_decode":
            import quopri
            return quopri.decodestring(v)
        if n == "create_function":                        # PHP create_function('$a', $code): the body
            return next((x for x in reversed(a) if isinstance(x, bytes)), None)
        return v                                          # eval/exec/assert/print/str()/bytes()/.decode()...


def _chain_codecs(src, depth=0, budget=0.4):
    """find_codecs entries read from decode call chains (see the section comment)."""
    _t = time
    try:
        if not src or len(src) > (1 << 18):
            return []
        end = _t.time() + budget
        starts, last = [], -1
        for m in _CH_START.finditer(src):
            nm = re.split(r"::|\.|->|\\", m.group(0).lstrip("@\\"))[-1].lower()
            if nm in _CH_ALL and m.start() >= last:
                starts.append(m.start())
                if len(starts) >= 48:
                    break
        seen = set()
        for st in starts:
            if _t.time() > end:
                break
            ch = _Chain(src, end, 0)
            try:
                v, j = ch.expr(st)
            except (ValueError, RecursionError):
                continue
            if isinstance(v, list):
                v = v[0] if v and isinstance(v[0], bytes) else None
            if not isinstance(v, bytes) or v in seen or len(v) > (1 << 20):
                continue
            seen.add(v)
            for b in (v, _utf16(v) if b"\x00" in v else None):
                if not b:
                    continue
                b = b.encode("utf-8") if isinstance(b, str) else b
                txt = b.decode("utf-8", "ignore")
                whole = txt.lstrip("\ufeff").strip()
                plain = whole if looks_like_plan(b) and whole[:2] in ("v=", "{") else None
                for lm in ([] if plain else _CH_LIT_PLAN.finditer(txt[:1 << 16])):
                    lit = lm.group(2) or lm.group(3)
                    if looks_like_plan(lit.encode("utf-8")):    # final layer `$plan = 'v=3|..';` / `q{..}`
                        plain = lit
                        break
                if plain or looks_like_plan(b):
                    return [{"id": "callchain", "rep": "callchain", "transform": "identity", "key": "",
                             "material": src[st:j][:400], "plain": plain or whole}]
                if depth < 4 and txt != src:                       # the decoded layer is code again
                    inner = find_codecs(txt, 1) if depth == 0 else []
                    inner = [c for c in inner if c.get("plain")] or _chain_codecs(txt, depth + 1,
                                                                               max(0.05, end - _t.time()))
                    if inner:
                        return [dict(inner[0], id=f"{inner[0]['id']}@chain{depth}")]
                if re.fullmatch(r"[\x20-\x7e\s]{16,}", txt):
                    p = peel_plan(txt.strip(), budget=min(0.15, max(0.02, end - _t.time())))
                    if p:
                        return [{"id": "callchain", "rep": "callchain", "transform": "identity", "key": "",
                                 "material": src[st:j][:400], "plain": p}]
    except Exception:  # noqa: BLE001 - unknown -> nothing, never an exception
        return []
    return []
