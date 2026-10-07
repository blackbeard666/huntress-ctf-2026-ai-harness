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
}
TRANSFORMS = {
    "identity": 3, "reverse": 3, "add_7": 3, "xor_5a": 3, "rotate_left": 3, "reverse_xor": 3,
    "add_modulo_256": 4, "subtract_modulo_256": 4, "repeating_key_xor": 4, "reverse_bytes": 4,
    "reverse_then_xor": 4, "rolling_xor": 4, "single_byte_xor": 4,
}


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
    if "base64" in rep:
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
    elif t in ("rotate_left", "rol"):
        amounts = [int(inline, 16) % 8] if inline else ([k1 % 8] if k1 else list(range(1, 8)))
        for n in amounts:
            yield bytes(((x >> n) | (x << (8 - n))) & 0xFF for x in data)   # undo a left rotation


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
    except Exception:  # noqa: BLE001 - a tool for the solver: unknown -> None, never an exception
        return None
    return None


# ------------------------------------------------------------------------------------------------ source scanning

_CODEC_RE = re.compile(r"""(?:Codec|CODEC)_(?P<id>[0-9A-Za-z]+)\s*=\s*["'](?P<spec>[^"']*)["']""")
_BATCH_CODEC_RE = re.compile(r"HUNTRESS-CODEC:\s*(?P<spec>\S+)")
_BATCH_MAT_RE = re.compile(r"HUNTRESS-MATERIAL:\s*(?P<mat>\S+)")


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


def find_codecs(src):
    """Every declared codec in a source text: [{id, rep, transform, key, material, plain}] (plain = decode() or None).
    Batch `HUNTRESS-CODEC:` has no id -- its material is the `HUNTRESS-MATERIAL:` line."""
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
    return out
