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
import unicodedata

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


# Target plan-key-passthrough: v=3 plans carry keys no question asked yet (`verdict` since D16, `language`). An answer
# id names its plan key in its tail (`set1.php-stager-next-language` -> next_language): the longest hyphen-suffix that
# is a plan key (or an alias of one) wins, so `-next-language` never reads `language`. Values go out plan-verbatim,
# shaped only by the answer_format: ordered_tokens '>'-joins a comma list, integer is base-10, enum must be one of the
# accepted_values (else None). None = this plan cannot answer the id (the per-day solver keeps its own reading).
PLAN_KEY_ALIASES = {"campaign": "campaign_id", "obfuscation": "obfuscation_profile", "file_path": "file_path",
                    "upload_url": "upload_url"}
# multi-word keys seen in v=3 plans: an id ending in one the plan lacks is unanswerable here (None), never read as the
# shorter key under it (`-next-language` must not answer `language`, `-upload-url` must not answer `url`)
PLAN_KNOWN_KEYS = {"next_language", "host_profile", "stage_profile", "obfuscation_profile", "stage_count",
                   "campaign_id", "file_path", "upload_url", "host_id"}


def plan_key_for(answer_id, plan):
    """The plan key an answer id asks for (longest suffix match, hyphens -> underscores, aliases), or None."""
    keys = {str(k).lower(): k for k in (plan or {})}
    parts = re.split(r"[-_]+", str(answer_id or "").rsplit(".", 1)[-1].lower())
    for i in range(len(parts)):
        suf = "_".join(p for p in parts[i:] if p)
        for cand in (suf, PLAN_KEY_ALIASES.get(suf), suf + "_id"):
            if cand and cand in keys:
                return keys[cand]
        if "_" in suf and (suf in PLAN_KNOWN_KEYS or PLAN_KEY_ALIASES.get(suf) in PLAN_KNOWN_KEYS):
            return None
    return None


def _plan_dict(plan):
    if isinstance(plan, dict):
        return plan
    if isinstance(plan, (bytes, bytearray)):
        plan = bytes(plan).decode("utf-8", "replace")
    t = str(plan or "").lstrip("﻿ \r\n\t")
    if t.startswith("{"):
        import json
        try:
            d = json.loads(t)
            return d if isinstance(d, dict) else {}
        except ValueError:
            return {}
    return plan_kv(t)


def plan_answer(answer_id, plan, q=None):
    """Answer `answer_id` straight from a decoded plan (dict, `k=v|..` text or JSON text) under the question's
    answer_format, or None when the plan has no such key / the value does not fit the format. Never raises."""
    try:
        plan = _plan_dict(plan)
        key = plan_key_for(answer_id, plan)
        if key is None or plan.get(key) is None:
            return None
        val = plan[key]
        fmt = (q or {}).get("answer_format") or {}
        kind = str(fmt.get("kind") or "").lower()
        if isinstance(val, (list, tuple)):
            val = ",".join(str(x) for x in val)
        val = str(val).strip()
        if kind == "ordered_tokens":
            toks = [t.strip() for t in re.split(r"[,>]", val) if t.strip()]
            return ">".join(toks) if toks else None
        if kind == "integer":
            return str(int(val)) if re.fullmatch(r"[+-]?\d+", val) else None
        if kind == "enum":
            acc = [str(a) for a in fmt.get("accepted_values") or []]
            if not acc:
                return val
            return val if val in acc else next((a for a in acc if a.lower() == val.lower()), None)
        return val
    except Exception:  # noqa: BLE001
        return None


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
    if re.sub(r"[^a-z]", "", rep.lower()) in ("cmdline", "commandline"):   # cmdline-canon (no plan reading)
        got = _cl_decode(material, rep, transform)
        if got is not None:
            return got
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

_CODEC_RE = re.compile(r"""(?:Codec|CODEC)_(?P<id>[0-9A-Za-z]+)(?:\s+(?i:As)\s+[A-Za-z_][\w.]*)?\s*=\s*["'](?P<spec>[^"']*)["']""")
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
        a = re.match(r"(?:\s+(?i:As)\s+[A-Za-z_][\w.]*)?\s*(\+=|&=|=|\.=)?\s*", rest)   # VBA `Const X As String =`
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


# Unix scripting-language material templates (prebuild ruby-perl-pack-reps, 10-16): a v=1 `Codec_<id>` whose material
# is WRITTEN through the language's own byte syntax instead of one plain literal -- Ruby `["..."].pack("H*")`,
# `"..".unpack1("m0")`, `[118, 61].pack("C*")`, `%w[76 3d].map(&:hex).pack("C*")`, `"\u{76 3d}"`; Perl
# `pack("H*", "..")`, `pack("C*", qw(..))`, `MIME::Base64::decode("..")`, `"\x{76}"`; Tcl `set Material_x [binary
# decode hex|base64 ".."]`, `binary format c* {..}`, `set Codec_x {..}`; Lua `"\118\061"`, `string.char(..)`.
# material_text() joins every literal (format `H*` / `m0` included) or misses the statement (Tcl `set`); here the
# assignment is read by its shape + the named template: the inner literal under the declared rep, then the bytes the
# template evaluates to (also with the template ops chained in either order) under the declared transform. Only
# consulted when the plain material reading found no plan, so every earlier result is unchanged. Bounded, never raises.
_TPL_CODEC_RES = (re.compile(r"""\bset\s+(?:Codec|CODEC)_(?P<id>[0-9A-Za-z]+)\s+(?:"(?P<q>[^"]*)"|\{(?P<b>[^{}]*)\})"""),
                  re.compile(r"""(?:Codec|CODEC)_(?P<id>[0-9A-Za-z]+)['"]?\s*=>\s*(?:"(?P<q>[^"]*)"|'(?P<b>[^']*)')"""))
_TPL_FMT = re.compile(r"[A-Za-z][*\d]{0,3}")
_TPL_WORDS = re.compile(r"(?:%[wWiI]|\bqw)\s*([\[({</|!])")
_TPL_ESC_PERL = re.compile(r"\\(x\{[0-9a-fA-F\s]{1,8}\}|x[0-9a-fA-F]{1,2}|u\{[0-9a-fA-F\s]{1,64}\}|u[0-9a-fA-F]{4}|"
                           r"[0-7]{1,3}|.)", re.S)
_TPL_ESC_LUA = re.compile(r"\\(x[0-9a-fA-F]{2}|u\{[0-9a-fA-F]{1,6}\}|\d{1,3}|.)", re.S)


def _tpl_unescape(body, lua=False):
    """Double-quoted literal body -> its bytes: Ruby/Perl/Tcl (`\\u{76 3d}`, `\\x{76}`, `\\xHH`, octal `\\166`) or Lua
    (decimal `\\118`, `\\xHH`, `\\u{..}`). None when an escape is out of range."""
    def sub(m):
        s = m.group(1)
        if s[0] in "xu" and len(s) > 1 and (s[1] == "{" or s[0] == "x" or len(s) == 5):
            return "".join(chr(int(h, 16)) for h in s[1:].strip("{}").split())
        if s[0].isdigit():
            v = int(s, 10 if lua else 8)
            if v > 255:
                raise ValueError(s)
            return chr(v)
        return _CH_DQ_ESC.get(s, s)
    try:
        t = (_TPL_ESC_LUA if lua else _TPL_ESC_PERL).sub(sub, body)
        return t.encode("latin-1") if max(map(ord, t or "\0")) < 256 else t.encode("utf-8")
    except (ValueError, OverflowError):
        return None


def _tpl_stmts(src, ident, limit=8):
    """RHS text of each `Material_<id> = ..` / `=> ..` / `.= ..` / `<< ..` / Tcl `set Material_<id> ..` statement."""
    pat = re.compile(r"(\bset\s+|\bappend\s+)?[$@]?(?:Material|MATERIAL)_" + re.escape(ident) + r"(?:_[0-9A-Za-z]+)?\b")
    out = []
    for m in pat.finditer(src):
        a = re.compile(r"[ \t]+" if m.group(1) else r"['\"]?\s*(\+=|\.=|<<|=>|=(?![=~]))\s*").match(src, m.end())
        if not a:
            continue
        i, depth, q, prev = a.end(), 0, None, ""
        while i < len(src) and i - a.end() < 65536:
            c = src[i]
            if q:
                if c == "\\":
                    i += 1
                elif c == q:
                    q = None
            elif c in "\"'":
                q = c
            elif c in "([{":
                depth += 1
            elif c in ")]}":
                depth -= 1
                if depth < 0:
                    break
            elif depth <= 0 and (c == ";" or c == "\n" and prev not in "\\+.,&(|"):
                break
            if not c.isspace():
                prev = c
            i += 1
        out.append(src[a.end():i])
        if len(out) >= limit:
            break
    return out


def _tpl_parse(stmt, tcl):
    """(literals [(quote, body)], words, bare text outside literals) of one RHS."""
    lits, words, bare, i, s = [], [], [], 0, stmt
    while i < len(s):
        c = s[i]
        w = _TPL_WORDS.match(s, i)
        if w:
            close = _CH_PAIR.get(w.group(1), w.group(1))
            j = s.find(close, w.end())
            j = len(s) if j < 0 else j
            words += s[w.end():j].split()
            i = j + 1
            continue
        if c in "\"'" or (tcl and c == "{"):
            close = "}" if c == "{" else c
            j, body = i + 1, []
            while j < len(s) and s[j] != close:
                if s[j] == "\\" and j + 1 < len(s) and c != "{":
                    body.append(s[j:j + 2])
                    j += 2
                    continue
                body.append(s[j])
                j += 1
            lits.append((c, "".join(body)))
            i = j + 1
            bare.append(" ")
            continue
        bare.append(c)
        i += 1
    return lits, words, "".join(bare)


def _tpl_ops(stmt):
    """Decoding ops the statement names, in source order: 'hex' / 'hexlo' / 'b64' / 'bytes'."""
    ops = []
    pats = ((r"""\bunpack1?\s*\(?\s*["']m0?\*?["']|\bdecode64\b|\bstrict_decode64\b|\bdecode_base64\b|"""
             r"""MIME::Base64::decode\b|\bb64decode\b|\bbase64_decode\b|binary\s+decode\s+base64\b|\bfrom_base64\b""",
             "b64"),
            (r"""\bpack\s*\(?\s*["']H\*?\d*["']|binary\s+(?:decode\s+hex|format\s+H\*?\d*)\b|\bhex2bin\b|"""
             r"""\bunhexlify\b|\bfrom_hex\b""", "hex"),
            (r"""\bpack\s*\(?\s*["']h\*?\d*["']|binary\s+format\s+h\*?\d*\b""", "hexlo"),
            (r"""\bpack\s*\(?\s*["'][CcUW]\*?\d*["']|binary\s+format\s+[cC]\*?\d*\b|\bstring\.char\b|\bchr\b|"""
             r"""\.chr\b|&:chr\b""", "bytes"))
    for p, op in pats:
        ops += [(m.start(), op) for m in re.finditer(p, stmt)]
    return [op for _, op in sorted(ops)]


def _tpl_apply(op, text):
    if op == "b64":
        return b64(text)
    h = hex_bytes(text) if re.fullmatch(r"[\s0-9a-fA-F]+", text or "") else None
    if h and op == "hexlo":
        return bytes(((x & 15) << 4) | (x >> 4) for x in h)
    return h


def _tpl_numbers(words, lits, bare, stmt):
    """Byte list of a pack('C*') / string.char / binary format c* template, radix read from the code (`hex`, `16`)."""
    toks = list(words)
    for q, body in lits:
        if re.fullmatch(r"[\s,0-9a-fA-FxX]+", body) and re.search(r"[\s,]", body.strip()):
            toks += re.split(r"[\s,]+", body.strip())
    b = re.sub(r"\bto_i\s*\(\s*16\s*\)|\bunpack1\b|[\w.]*[A-Za-z_][\w.]*\d\w*", " ", bare)
    toks += re.findall(r"(?<![\w.])(?:0[xX][0-9a-fA-F]+|\d+)(?![\w.])", b)
    toks = [t for t in toks if t]
    if not toks:
        return []
    hexy = bool(re.search(r"\bhex\b|&:hex|to_i\s*\(\s*16|\b16\b|scan\s*%x", stmt)) or \
        any(re.search(r"[a-fA-F]", t) and not t.lower().startswith("0x") for t in toks)
    out = []
    for radix in ((16, 10) if hexy else (10, 16)):
        try:
            v = [int(t, 16) if t.lower().startswith("0x") else int(t, radix) for t in toks]
        except ValueError:
            continue
        if all(0 <= x < 256 for x in v):
            out.append(bytes(v))
        elif "U*" in stmt and all(0 <= x < 0x110000 for x in v):
            out.append("".join(map(chr, v)).encode("utf-8"))
    return out


def _tpl_decode(src, ident, rep, tr, key, budget=0.8):
    """(plain, statement) for a template-written material (see the section comment), else (None, None)."""
    try:
        end = time.time() + budget
        stmts = _tpl_stmts(src, ident)
        if not stmts:
            return None, None
        blobs = []
        parts = [[], [], [], []]                       # raw text / perl-unescaped / lua-unescaped / evaluated bytes
        for st in stmts:
            tcl = bool(re.match(r"\s*\[", st)) or "binary " in st or bool(re.search(r"\bset\s+(?:Material|MATERIAL)_"
                                                                                  + re.escape(ident), src))
            lits, words, bare = _tpl_parse(st, tcl)
            fmt = bool(re.search(r"\b(?:un)?pack1?\b|binary\s+format", st))
            body = [(q, b) for q, b in lits if not (fmt and _TPL_FMT.fullmatch(b))]
            raw = "".join(b for _, b in body) + " ".join(words)
            perl = b"".join((_tpl_unescape(b) or b"") if q == '"' else b.encode("latin-1", "ignore") for q, b in body)
            lua = b"".join((_tpl_unescape(b, True) or b"") if q == '"' else b.encode("latin-1", "ignore")
                           for q, b in body)
            ops = _tpl_ops(st)
            ev = []
            for seq in dict.fromkeys((tuple(ops), tuple(reversed(ops)))):
                for start in (perl, lua):
                    cur = [start] if seq[:1] != ("bytes",) else _tpl_numbers(words, lits, bare, st)
                    for op in seq:
                        if op == "bytes":
                            continue
                        cur = [x for x in (_tpl_apply(op, c.decode("latin-1")) for c in cur) if x]
                    ev += cur
                    for op in seq[:1]:                     # a single op of a two-op chain
                        if op != "bytes" and len(seq) > 1:
                            x = _tpl_apply(op, start.decode("latin-1"))
                            ev += [x] if x else []
            for k, v in enumerate((raw.encode("latin-1", "ignore"), perl, lua, b"".join(ev[:1]))):
                parts[k].append(v)
            blobs += ev[1:4]
        texts = [b"".join(p) for p in parts[:3]]
        blobs = [b"".join(parts[3])] + blobs + texts[1:]
        # the inner literal under the declared rep, then the evaluated bytes under the declared transform; names
        # only first (cheap), then decode() with its name-agnostic fallback
        cands = list(dict.fromkeys([(t.decode("latin-1"), rep) for t in texts if t] +
                                   [(b.hex(), "hex_compact") for b in blobs if b]))
        for full in (False, True):
            for m, r in cands:
                if time.time() > end:
                    return None, None
                t2, k2 = _spec(r, tr, key)
                if full:
                    p = decode(m, r, tr, key)
                elif known(r, t2):
                    p = next((o.decode("utf-8").lstrip("\ufeff") for d in _rep_candidates(r, m)
                              for o in _transform_candidates(t2, k2, d) if looks_like_plan(o)), None)
                else:
                    continue
                if p:
                    return p, stmts[0]
    except Exception:  # noqa: BLE001 - unknown -> None, never an exception
        pass
    return None, None


# JScript.Encode / VBScript.Encode (screnc: .jse/.vbe, `language="VBScript.Encode"` in WSF/HTA/SCT/ASP hosts):
# `#@~^<len b64>==<body><checksum b64>==^#~@`. Each body char < 0x80 advances a position i; tab and 0x20-0x7F (bar
# `<` `>` `@`) go through one of 3 permutation tables picked by _WSH_SLOT[i % 64]; `@&` `@#` `@*` `@!` `@$` are \n \r
# > < @. _WSH_ENC[s] lists the slot-s ciphertext of each _WSH_PLAIN char. find_codecs() reads the decoded source
# (blocks substituted in place) when the text carries the marker. Length/checksum are not enforced (lenient).
_WSH_PLAIN = "\t" + "".join(chr(c) for c in range(32, 128) if c not in (60, 62, 64))
_WSH_ENC = (
    '7~ZE:yY\'vcbMQSR &Tq+f*X\x7f{01lIx_)$/93o!u(BFJ\\H6K}]jPi#\tpet,wD?m|C8^[nWL4r%VshUG25.dO;-Aaz"`kN=g',
    'i,er[fuLEv*C3B cJZ8y2Wl+FRO=p{Qz~;GAwV_&xndtg}h5"U:`jqoI\\]\'Y%|#m(19\x7f6T4bN0^s\tKa$MkD!7SXH.P-)?/',
    'dP"Ja^][B`#e_~ORz!F &c*vG%,)i\'gbAZf2sMCq9|SH1rnpI?Kj.\x7f(5}$-T7{=l4mN+0otkL3V:xWw;D/YE\\h6Xy\tu8UQ',
)
_WSH_SLOT = "0120121221210212021200122102122100212120200120210212001220012021"
_WSH_DEC = tuple({e: p for e, p in zip(enc, _WSH_PLAIN)} for enc in _WSH_ENC)
_WSH_ESC = {"&": "\n", "#": "\r", "*": ">", "!": "<", "$": "@"}
_WSH_RE = re.compile(r"#@~\^[A-Za-z0-9+/]{6}==(.*?)[A-Za-z0-9+/]{6}==\^#~@", re.S)


def wsh_decode_block(body):
    """Plain text of one screnc body (between the `#@~^XXXXXX==` header and the `XXXXXX==^#~@` trailer)."""
    out, i, k = [], 0, 0
    while k < len(body):
        c = body[k]
        k += 1
        if c == "@" and k < len(body) and body[k] in _WSH_ESC:
            c = _WSH_ESC[body[k]]
            k += 1
        elif c < "\x80" and c not in "<>@":
            c = _WSH_DEC[int(_WSH_SLOT[i & 63])].get(c, c)
        if c < "\x80":
            i += 1
        out.append(c)
    return "".join(out)


def wsh_decode(src):
    """`src` with every `#@~^..^#~@` encoded block replaced by its plain script, or None when it carries none."""
    try:
        if not isinstance(src, str) or "#@~^" not in src:
            return None
        dec = _WSH_RE.sub(lambda m: wsh_decode_block(m.group(1)), src)
        return dec if dec != src else None
    except Exception:  # noqa: BLE001
        return None


# ------------------------------------------------------------------------------------------------ Dockerfile / Makefile
# Target dockerfile-makefile-route: build hosts read as the build tool would, never run (`make -n` / `docker build`).
# Logical lines join `\`-newline continuations (Dockerfile `# escape=` honoured, comment lines inside an instruction
# dropped; a Makefile `#` comment ending in `\` continues). Variables: Dockerfile `ARG X=..`, `ENV X=.. Y=..`, legacy
# `ENV X value`; Makefile `X (=|:=|::=|:::=|?=|+=|!=) ..` (override/export prefixes) and `define X .. endef`, all with
# `$(X)`/`${X}`/`$X` expanded. Payloads: `echo`/`printf` arguments of RUN / TAB-recipe / `$(shell ..)` / `!=` pipelines
# (`| base64 -d | sh`, `xxd -r -p`, gunzip ...) and RUN heredoc bodies. Each candidate is peeled name-agnostically
# (peel_plan); descriptor variables first, then the continued `#` marker, echo payloads, other variables. Only
# consulted when nothing earlier yielded a plan.
_BH_DOCKER = re.compile(r"(?im)^[ \t]*(?:FROM|ARG|ENV|RUN|LABEL)[ \t]+\S")
_BH_MAKE = re.compile(r"(?m)^\t[^\n]*\S|^(?:override[ \t]+|export[ \t]+)*[A-Za-z_][\w.-]*[ \t]*(?:::?=|:::=|\?=|\+=|!=)"
                      r"|^define[ \t]+\w")
_BH_APPEND = re.compile(r"(?im)^[ \t]*(?:(?:override|export)[ \t]+)*(descriptor[_-][\w.-]*)[ \t]*"
                        r"(?:\+=|:{0,3}=[ \t]*\$[({]\1[)}])")
_BH_MK_ASSIGN = re.compile(r"(?:(?:override|export|private)[ \t]+)*(?P<name>[A-Za-z_][\w.-]*)[ \t]*"
                           r"(?P<op>:::=|::=|:=|\?=|\+=|!=|=)[ \t]*(?P<val>.*)\Z", re.S)
_BH_ENV_PAIR = re.compile(r"""(?P<name>[A-Za-z_]\w*)=(?P<val>"(?:[^"\\]|\\.)*"|'[^']*'|(?:[^\s"'\\]|\\.)*)""")
_BH_VAR = re.compile(r"\$(?:\((?P<p>[A-Za-z_][\w.-]*)\)|\{(?P<b>[A-Za-z_][\w.-]*)(?::?[-+](?P<d>[^}]*))?\}|(?P<s>[A-Za-z_]\w*))")
_BH_ECHO = re.compile(r"""(?:^|[\s;&|(`"'\[,])(?:/(?:usr/)?bin/)?(?P<cmd>echo|printf)\b(?P<args>(?:\\.|"[^"]*"|'[^']*'|[^|;&<>)`\n])*)""")
_BH_HEREDOC = re.compile(r"""<<-?[ \t]*(["']?)(?P<tag>[A-Za-z_]\w*)\1[^\n]*\n(?P<body>.*?)\n[ \t]*(?P=tag)[ \t]*(?:\n|$)""", re.S)


def _bh_lines(src, docker):
    """Logical lines: `\\`-newline continuations joined (continuation-line indentation kept as one space)."""
    esc = "\\"
    if docker:
        m = re.match(r"(?:[ \t]*#[ \t]*\w+[ \t]*=[^\n]*\n)*?[ \t]*#[ \t]*escape[ \t]*=[ \t]*([\\`])", src, re.I)
        esc = m.group(1) if m else "\\"
    out, cur = [], None
    for ln in src.split("\n"):
        ln = ln.rstrip("\r")
        if cur is not None:
            if docker and re.match(r"[ \t]*#", ln):                  # comment inside a continued instruction
                continue
            ln = (" " if ln[:1] in " \t" else "") + ln.strip(" \t")
            cur += ln
        else:
            cur = ln
        if cur.endswith(esc) and not cur.endswith(esc * 2):
            cur = cur[:-1]
            continue
        out.append(cur)
        cur = None
    if cur is not None:
        out.append(cur)
    return out


def _bh_expand(s, env, depth=0):
    """`$(X)` / `${X}` / `${X:-d}` / `$X` from `env` (unknown -> ''), `$$` -> `$`, `$(shell ..)` left for the caller."""
    if "$" not in s or depth > 4:
        return s

    def rep(m):
        n = m.group("p") or m.group("b") or m.group("s")
        if n in env:
            return _bh_expand(env[n], env, depth + 1)
        if m.group("s"):
            return m.group(0)                                        # bare `$X`: a shell variable, keep
        return m.group("d") or ""
    s = s.replace("$$", "\0")
    return _BH_VAR.sub(rep, s).replace("\0", "$")


def _bh_shell_calls(s):
    """Bodies of `$(shell ..)` calls (balanced parentheses)."""
    out, i = [], 0
    while len(out) < 16:
        i = s.find("$(shell", i)
        if i < 0:
            break
        d, j = 0, i + 1
        while j < len(s):
            d += {"(": 1, ")": -1}.get(s[j], 0)
            if d == 0:
                break
            j += 1
        out.append(s[i + 7:j])
        i = j
    return out


def _bh_echo_args(cmd):
    """Joined arguments of each echo/printf in a shell command (quotes, option flags, `%s` formats dropped)."""
    out = []
    for m in _BH_ECHO.finditer(cmd):
        a = m.group("args").strip()
        a = re.sub(r"^(?:-[neE]+[ \t]+)+", "", a)
        if m.group("cmd") == "printf":
            a = re.sub(r"""^(["']?)%[bs](?:\\n)?\1[ \t]+""", "", a)
        a = re.sub(r"""["'\\]""", "", a)
        out.append(a)
    return out


def _bh_payloads(cmd, env):
    cmd = _bh_expand(cmd, env)
    return [a for a in _bh_echo_args(cmd)] + [m.group("body") for m in _BH_HEREDOC.finditer(cmd)]


def _build_host_codecs(src, budget=0.6):
    """find_codecs entries read from a Dockerfile / Makefile build host (see the section comment)."""
    try:
        if not src or len(src) > (1 << 20):
            return []
        docker = bool(_BH_DOCKER.search(src))
        make = bool(_BH_MAKE.search(src))
        if not (docker or make):
            return []
        end = time.time() + budget
        env, order, run_cmds, marks = {}, [], [], []
        lines = _bh_lines(src, docker and not make)
        k = 0
        while k < len(lines):
            ln = lines[k]
            k += 1
            st = ln.strip()
            if st.startswith("#"):
                if _ANALYSIS_RE.search(st):
                    marks.append(re.sub(r"\s+", "", st))
                continue
            if ln.startswith("\t"):                                  # make recipe line
                run_cmds.append(ln[1:].lstrip("@-+ \t"))
                continue
            dm = re.match(r"(?i)(ARG|ENV|LABEL)[ \t]+(.*)\Z", st, re.S) if docker else None
            if dm:
                body = dm.group(2)
                pairs = list(_BH_ENV_PAIR.finditer(body))
                if not pairs and dm.group(1).upper() != "ARG":       # legacy `ENV X value`
                    lm = re.match(r"([A-Za-z_]\w*)[ \t]+(.+)", body, re.S)
                    pairs = [(lm.group(1), lm.group(2).strip())] if lm else []
                else:
                    pairs = [(p.group("name"), p.group("val")) for p in pairs]
                for n, v in pairs:
                    if v[:1] in "\"'" and v[-1:] == v[:1] and len(v) > 1:
                        v = v[1:-1].replace("\\" + '"', '"') if v[0] == '"' else v[1:-1]
                    env[n] = _bh_expand(v, env)
                    order.append(n)
                continue
            rm = re.match(r"(?i)(RUN|CMD|ENTRYPOINT)[ \t]+(.*)\Z", st, re.S) if docker else None
            if rm:
                cmd = rm.group(2)
                hm = re.search(r"<<-?[ \t]*([\"']?)([A-Za-z_]\w*)\1", cmd)
                if hm:                                               # RUN <<EOF heredoc: body up to the tag line
                    body = []
                    while k < len(lines) and lines[k].strip() != hm.group(2):
                        body.append(lines[k])
                        k += 1
                    k += 1
                    cmd = cmd + "\n" + "\n".join(body) + "\n" + hm.group(2) + "\n"
                    run_cmds.extend(body)
                run_cmds.append(cmd)
                continue
            if make:
                fm = re.match(r"(?:(?:override|export)[ \t]+)*define[ \t]+([A-Za-z_][\w.-]*)", st)
                if fm:
                    body = []
                    while k < len(lines) and not re.match(r"[ \t]*endef\b", lines[k]):
                        body.append(lines[k])
                        k += 1
                    k += 1
                    env[fm.group(1)] = "\n".join(body)
                    order.append(fm.group(1))
                    continue
                am = _BH_MK_ASSIGN.match(st)
                if am and not re.match(r"[^=]*:[ \t]*[^=:]", st[:am.start("op")]):
                    n, op, v = am.group("name"), am.group("op"), re.sub(r"(?<!\\)[ \t]*#.*$", "", am.group("val"))
                    for sc in _bh_shell_calls(v):
                        run_cmds.append(sc)
                    if op == "!=":
                        run_cmds.append(v)
                        v = ""
                    elif op == "?=" and n in env:
                        continue
                    if op == "+=" and n in env:
                        v = env[n] + " " + v
                    elif op in (":=", "::=", ":::="):
                        v = _bh_expand(v, env)
                    env[n] = v
                    order.append(n)
        cands, seen = [], set()

        def add(ident, lit):
            if lit and lit.strip() and (ident, lit) not in seen:
                seen.add((ident, lit))
                cands.append((ident, lit))
        names = list(dict.fromkeys(order))
        for n in names:
            if re.match(r"(?i)descriptor[_-]", n):
                add(re.sub(r"(?i)^descriptor[_-]", "", n), _bh_expand(env[n], env))
        for c in run_cmds:
            if re.search(r"(?i)\bdescriptor[_-]", c):
                for a in _bh_payloads(c, env):
                    add("run", a)
        for mk in marks:
            am = _ANALYSIS_RE.search(mk)
            plain = peel_plan(am.group("mat"), am.group("tag"), budget=min(0.3, max(0.05, end - time.time())))
            if plain:
                dm = re.search(r"(?i)descriptor[_-](\w+)", src)
                return [{"id": dm.group(1) if dm else "analysis", "rep": "descriptor", "transform": "identity",
                         "key": "", "material": am.group("mat"), "plain": plain}]
        for c in run_cmds:
            for a in _bh_payloads(c, env):
                add("run", a)
        for n in names:
            add(n, _bh_expand(env[n], env))
        ident, plain = _peel_ext(cands, budget=max(0.05, end - time.time()))
        if plain:
            return [{"id": ident, "rep": "descriptor", "transform": "identity", "key": "",
                     "material": dict(cands).get(ident), "plain": plain}]
    except Exception:  # noqa: BLE001 - unknown host -> nothing, never an exception
        return []
    return []


def find_codecs(src, _depth=0):
    """Every declared codec in a source text: [{id, rep, transform, key, material, plain}] (plain = decode() or None).
    Batch `HUNTRESS-CODEC:` has no id -- its material is the `HUNTRESS-MATERIAL:` line.
    `src` may also be raw bytes (or latin-1 text) of a container carrier: see _carrier_codecs, tried only when the
    text itself declares nothing."""
    raw = None
    if isinstance(src, (bytes, bytearray)):
        raw = bytes(src)
        src = raw.decode("utf-8", "ignore")
    src = wsh_decode(src) or src                         # JScript.Encode / VBScript.Encode blocks: read the plain
    out = _find_codecs_text(src)
    if _depth < 2 and not any(c.get("plain") for c in out):
        out = out + _carrier_codecs(src, raw, _depth)
    if _depth < 2 and not any(c.get("plain") for c in out):
        out = out + _bat_codecs(src)
    if _depth < 2 and not any(c.get("plain") for c in out):
        out = out + _ps_codecs(src, _depth)
    if _depth < 2 and not any(c.get("plain") for c in out):
        out = out + _ps_v3_codecs(src)
    elif _depth < 2 and _PSV3_VAR.search((src or "")[:1 << 20]):
        # a PS `"a" +` backtick-continued / `'it''s'` descriptor reads lossy elsewhere: the full plan goes first
        x = [c for c in _ps_v3_codecs(src) if any(_psv3_lossy(c["plain"], o.get("plain")) for o in out)]
        out = x + out
    if _depth < 2 and not any(c.get("plain") for c in out):
        out = out + _xslt_codecs(src)
    elif _depth < 2 and _XSL_HOST.search((src or "")[:1 << 16]):
        # an XML-escaped `"a" &amp; _ "b"` reads as the plan-shaped first piece only: the full plan goes first
        x = [c for c in _xslt_codecs(src) if any(c["plain"] != p and c["plain"].startswith(p)
                                                 for p in (o.get("plain") for o in out) if p)]
        out = x + out
    if _depth < 2 and not any(c.get("plain") for c in out):
        out = out + _chain_codecs(src, _depth)
    if _depth < 2 and not any(c.get("plain") for c in out):
        out = out + _build_host_codecs(src)
    elif _depth < 2 and _BH_APPEND.search((src or "")[:1 << 20]):
        # a Makefile `descriptor_x += ..` / `:= $(descriptor_x)..` append reads as its first piece only: full plan first
        x = [c for c in _build_host_codecs(src) if any(c["plain"] != p and c["plain"].startswith(p)
                                                       for p in (o.get("plain") for o in out) if p)]
        out = x + out
    if _depth < 2 and not any(c.get("plain") for c in out):
        out = out + _saas_host_codecs(src, raw, _depth)     # SaaS / add-in host: JSON-escaped script, zip / CRX package
    if _depth < 1 and not any(c.get("plain") for c in out):
        norm = normalize(raw if raw is not None else src)     # whole-leaf UTF-16 / gzip / base64: rescan the source
        if norm:
            out = out + [dict(c, id=f"{c['id']}@leaf") for c in find_codecs(norm, _depth + 1) if c.get("plain")]
    if _depth < 1 and not any(c.get("plain") for c in out):
        out = out + _reg_inf_codecs(normalize(raw if raw is not None else src) or src, _depth)
    if _depth < 1 and not any(c.get("plain") for c in out):
        mat, plain = _split_array_plain(src, budget=0.5)          # split chunk-list carrier without the SPLIT marker
        if plain:
            out = out + [{"id": "split", "rep": "split_array", "transform": "identity", "key": "", "material": mat,
                          "plain": plain}]
    if _depth < 1 and not any(c.get("plain") for c in out):
        out = out + _proc_codecs(src, raw, _depth)   # process-telemetry log: codecs inside escaped command lines
    return out


def _find_codecs_text(src):
    out = []
    for m in _CODEC_RE.finditer(src or ""):
        parts = m.group("spec").split("|")
        rep, tr, key = (parts + ["", "", ""])[:3]
        mat = material_text(src, m.group("id"))
        out.append({"id": m.group("id"), "rep": rep, "transform": tr, "key": key, "material": mat,
                    "plain": decode(mat, rep, tr, key)})
    seen = {c["id"] for c in out}
    for rx in _TPL_CODEC_RES:                         # Tcl `set Codec_x {..}`, Perl `CODEC_X => '..'`
        for m in rx.finditer(src or ""):
            if m.group("id") not in seen:
                seen.add(m.group("id"))
                rep, tr, key = ((m.group("q") or m.group("b") or "").split("|") + ["", "", ""])[:3]
                mat = material_text(src, m.group("id"))
                out.append({"id": m.group("id"), "rep": rep, "transform": tr, "key": key, "material": mat,
                            "plain": decode(mat, rep, tr, key)})
    tpl_end = time.time() + 1.0
    for c in out:                                     # material written through a pack/unpack/escape template
        if c["plain"] is None and c["rep"] and time.time() < tpl_end:
            p, st = _tpl_decode(src, c["id"], c["rep"], c["transform"], c["key"], max(0.05, tpl_end - time.time()))
            if p:
                c["plain"], c["material"] = p, st
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
                plain = _peel_ext(cont + _ahk_literals(src) + _descriptor_literals_ext(src), am.group("tag"),
                                  tried=_descriptor_literals(src) + [am.group("mat")])[1]
        out.append({"id": dm.group(1) if dm else "analysis", "rep": rep, "transform": "identity", "key": "",
                    "material": am.group("mat"), "plain": plain})
    elif not out:
        if _SPLIT_MARK_RE.search(src or ""):                     # D18 bare SPLIT marker + literal-array material
            mat, plain = _split_array_plain(src)
            if plain:
                out.append({"id": "analysis", "rep": "split_array", "transform": "identity", "key": "",
                            "material": mat, "plain": plain})
        for ident, lit in ([] if out else _ahk_literals(src)):   # AHK v1 continuation section / `.=` appends
            plain = _peel_ext([(ident, lit)])[1]
            if plain:
                out.append({"id": ident, "rep": "descriptor", "transform": "identity", "key": "", "material": lit,
                            "plain": plain})
                break
        for ident, lit in ([] if out else _descriptor_literals(src or "", with_id=True)):  # descriptor literal, no marker line
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


# YAML value shapes (target yaml-ci-host-route: GitHub Actions / GitLab CI / Ansible hosts) the quoting forms below miss:
# `!!binary` / `!tag` / `&anchor` properties, `*alias`, `[..]` flow sequences, a value on the deeper-indented lines
# below its key (block sequence items joined, a mapping's default/value/data child, a lone scalar), `|2-` indicators,
# plain scalars folded over deeper-indented lines, and `- name: descriptor_x` + sibling `value:`. Pure regex/indent
# reading (no PyYAML in-window); every shape here used to read as None, so earlier readings are unchanged.
_YAML_PROPS = re.compile(r"(?:(?:!!?[\w:/.-]*|!<[^>\s]*>|&[\w-]+)(?:[ \t]+|(?=[ \t]*(?:#[^\n]*)?\r?\n)))+")
_YAML_SUB_KEYS = ("default", "value", "data", "content", "payload", "text", "body", "stdin", "src")
_YAML_KEY = re.compile(r"""[ \t]*(?:-[ \t]+)?(["']?)([\w.-]+)\1[ \t]*:(?:[ \t]+|(?=\r?$))""")
_YAML_PLAIN_CONT = re.compile(r"\n( +)([A-Za-z0-9+/=_\-.%~]+)[ \t]*(?=\r?\n|$)")
_YAML_JINJA = re.compile(r"""\s*\{\{-?\s*(["'])(.*?)\1\s*(?:\|\s*\w+(?:\([^)]*\))?\s*)*-?\}\}\s*""", re.S)
_YAML_FLOW_ITEM = re.compile(r""""([^"]*)"|'([^']*)'|([^,\s\[\]"']+)""")


def _yaml_indent(src, i):
    ls = src.rfind("\n", 0, i) + 1
    line = src[ls:i]
    return len(line) - len(line.lstrip(" \t"))


def _yaml_children(src, j, base, lim=1 << 16):
    """[(indent, line, offset)] of the non-blank, non-comment lines from src[j] on that sit deeper than `base`."""
    out, stop = [], j + lim
    while j < len(src) and j < stop and len(out) < 512:
        e = src.find("\n", j)
        e = len(src) if e < 0 else e
        line = src[j:e].rstrip("\r")
        s = line.strip()
        if s and not s.startswith("#"):
            ind = len(line) - len(line.lstrip(" \t"))
            if ind <= base:
                break
            out.append((ind, line, j))
        j = e + 1
    return out


def _yaml_node(src, i, depth=0):
    """(text, end) of a YAML value at src[i] in one of the shapes above, or (None, i)."""
    if depth > 2 or i >= len(src):
        return None, i
    p = _YAML_PROPS.match(src, i)
    if p and p.end() > i:
        return _read_literal(src, p.end(), ":", depth + 1)
    m = re.match(r"\*([\w-]+)", src[i:i + 80])
    if m:                                                            # alias -> the anchored value
        a = re.search(r"(?<![\w*-])&" + re.escape(m.group(1)) + r"(?=[ \t\r\n])", src)
        return (_read_literal(src, a.start(), ":", depth + 1)[0] if a else None), i + m.end()
    if src.startswith("[", i):                                       # flow sequence ["ab", 'cd', ef]
        j = src.find("]", i, i + (1 << 16))
        if j < 0:
            return None, i
        text = "".join(a or b or c for a, b, c in _YAML_FLOW_ITEM.findall(src[i + 1:j]))
        return (text or None), j + 1
    m = re.match(r"[ \t]*(?:#[^\n]*)?\r?\n", src[i:i + 4096])
    if not m:
        return None, i
    kids = _yaml_children(src, i + m.end(), _yaml_indent(src, i))
    if not kids:
        return None, i
    ind0 = kids[0][0]
    top = [k for k in kids if k[0] == ind0]
    end = kids[-1][2] + len(kids[-1][1])
    if top[0][1].lstrip().startswith("- "):                          # block sequence: scalar items joined
        parts = []
        for ind, line, off in top:
            body = line.lstrip()
            if not body.startswith("- ") or _YAML_KEY.match(body[2:]):
                return None, i
            t, _ = _read_literal(src, off + ind + 2, ":", depth + 1)
            parts.append(body[2:].strip() if t is None else t)
        return "".join(parts), end
    keyed = [(km, off + ind) for ind, line, off in top for km in [_YAML_KEY.match(line.lstrip())] if km]
    if keyed:                                                        # nested mapping: default/value/data, else longest
        vals = []
        for km, off in keyed:
            t, _ = _read_literal(src, off + km.end(), ":", depth + 1)
            if t:
                vals.append((km.group(2).lower() in _YAML_SUB_KEYS, len(t), t))
        return (max(vals)[2] if vals else None), end
    t, e = _read_literal(src, top[0][2] + ind0, ":", depth + 1)      # lone scalar on the next line
    return t, (e if t is not None else i)


def _yaml_sibling_value(src, start):
    """`- name: descriptor_x` (k8s env / Actions inputs list): the sibling `value:` / `default:` literal, else None."""
    ls = src.rfind("\n", 0, start) + 1
    m = re.match(r"""([ \t]*(?:-[ \t]+)?)(?:name|key|id|variable)[ \t]*:[ \t]*["']?$""", src[ls:start])
    if not m:
        return None
    col, j = len(m.group(1)), src.find("\n", start)
    for ind, line, off in _yaml_children(src, j + 1 if j >= 0 else len(src), col - 1)[:32]:
        km = _YAML_KEY.match(line) if ind == col else None
        if km and km.group(2).lower() in _YAML_SUB_KEYS:
            return _read_literal(src, off + km.end(), ":")[0]
    return None


def _read_literal(src, i, op, _depth=0):
    """(text, end) of the literal starting at src[i] in any common quoting form, or (None, i)."""
    lim = 1 << 16
    if op == ":":
        r = _yaml_node(src, i, _depth)
        if r[0] is not None:
            return r
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
    m = re.match(r"[|>](?:[-+]?\d?|\d[-+])[ \t]*(?:#[^\n]*)?\r?\n", src[i:i + 40])   # YAML block scalar
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
            text, j = m.group(0), i + m.end()
            # Makefile / Dockerfile / shell `\`-newline continuation: `X := aaaa\` + `bbbb\` + `cccc` (joined)
            while text.endswith("\\") and len(text) < lim:
                c = re.match(r"\r?\n[ \t]*([^\s#;,\"'<>(){}\[\]]+)", src[j:j + lim])
                if not c:
                    break
                text, j = text[:-1] + c.group(1), j + c.end()
            if op == ":" and not text.endswith("\\"):                 # YAML plain scalar folded over deeper lines
                base = _yaml_indent(src, i)
                while len(text) < lim:
                    c = _YAML_PLAIN_CONT.match(src, j)
                    if not c or len(c.group(1)) <= base:
                        break
                    text, j = text + c.group(2), c.end()
            return text, j
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
        if lit is None and op is None:
            lit = _yaml_sibling_value(src, m.start())
            if lit:
                out.append((m.group("id"), lit))
            continue
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
        jm = _YAML_JINJA.fullmatch(out[-1][1])                       # Ansible "{{ 'blob' | b64decode }}"
        if jm:
            out.append((m.group("id"), jm.group(2)))
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


# AutoHotkey v1 legacy descriptor forms (target ahk-compiled-exe-extract): a continuation section
# `descriptor_x =` / `:= "` + `(Join..` lines `)` (`)"` closes the quoted form) and `descriptor_x .= ".."` / `.= text`
# appends. Only ids that use one of these AHK constructs are returned (whole value accumulated in source order), so a
# plain `descriptor_x = ..` keeps its earlier reading.
_AHK_ASSIGN_RE = re.compile(r"""^[ \t]*(?:global[ \t]+|static[ \t]+|local[ \t]+)?descriptor_(?P<id>\w+)[ \t]*(?P<op>\.=|:=|=)"""
                            r"""[ \t]*(?P<rest>[^\r\n]*)""", re.M)
_AHK_CONT_OPEN_RE = re.compile(r"""\r?\n[ \t]*\((?P<opts>[^\r\n)]*)\r?\n""")


def _ahk_value(rest, op):
    """Value of a one-line AHK v1 assignment: `:=`/`.=` take quoted pieces joined by ` . `; legacy `=` the raw text."""
    rest = re.sub(r"""[ \t]+;.*$""", "", rest).strip()
    if op == "=" or (op == ".=" and rest[:1] not in "\"'"):
        return rest or None
    pieces = re.findall(r'"((?:[^"]|"")*)"', rest)
    return "".join(x.replace('""', '"') for x in pieces) if pieces else None


def _ahk_literals(src, limit=16):
    """(id, value) of descriptors written with an AHK continuation section or `.=` appends; [] otherwise."""
    if not src or "descriptor_" not in src:
        return []
    vals, special = {}, set()
    for m in _AHK_ASSIGN_RE.finditer(src[:1 << 20]):
        ident, op, rest = m.group("id"), m.group("op"), m.group("rest").strip()
        val = None
        if rest in ("", '"') and op in ("=", ":="):
            c = _AHK_CONT_OPEN_RE.match(src, m.end())
            if c:
                body, j = [], c.end()
                for line in src[j:j + (1 << 16)].split("\n"):
                    if re.match(r"[ \t]*\)", line):
                        break
                    body.append(line.rstrip("\r"))
                else:
                    continue
                opts = c.group("opts")
                jm = re.search(r"\bjoin(\S*)", opts, re.I)
                lines = [ln.strip() for ln in body]                  # LTrim/RTrim: indentation never part of a blob
                sep = (jm.group(1).replace("`s", " ").replace("`n", "\n").replace("`t", "\t") if jm else "\n")
                val = sep.join(lines)
                special.add(ident)
        elif rest:
            val = _ahk_value(rest, op)
        if val is None:
            continue
        if op == ".=":
            special.add(ident)
            vals[ident] = vals.get(ident, "") + val
        else:
            vals[ident] = val
    return [(k, v) for k, v in vals.items() if k in special and v][:limit]


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

# D18 Google Apps Script v=3 fixtures: a bare `// HUNTRESS_ANALYSIS_V1:SPLIT` marker (no `-<material>`) and the material
# as an array of string-literal chunks, `const X = ["<TAG>-chunk", "chunk", ..].join("")` (TAG = B64/HEX/HB64/FRAG),
# plus an untagged copy. The same split carrier in the other host syntaxes reads through three name-agnostic shapes:
#  - separator runs: quoted literals (r/b/u/@/$ prefixes, Lua [[..]]) joined by `,` `;` `+` `&` `..` `.` whitespace or a
#    line continuation (`_` / backtick / `\`) -- JS/AHK/Python `[..]`, tuples, PS `@(..)` / `"a","b"`, Lua `{..}`, Perl
#    `(..)`, VBS `Array(..)`, AutoIt `[..]`, AppleScript `{..}`, implicit/explicit concatenation;
#  - word lists: Perl `qw(..)`, Ruby `%w[..]`;
#  - line runs: consecutive lines holding one value each -- `x += "c"` / `push @a, "c"` / `table.insert(t, "c")` /
#    `$a[1] = "c"` / `set end of L to "c"`, batch `set c1=..` / `set "c1=.."` / `set x=%x%..`, XML `<Chunk>..</Chunk>`
#    and `<Chunk Include=".." />` (MSBuild).
# A joined run is peeled from its first chunk and from every `<TAG>-` chunk (tag stripped, and kept); only a plan counts.
_SPLIT_MARK_RE = re.compile(r"HUNTRESS_ANALYSIS_V\d+:SPLIT\b")
_SPLIT_LIT = re.compile(r"""(?<![\w"'`])[rRbBuU@$]{0,2}(?:"([^"\r\n]*)"|'([^'\r\n]*)'|`([^`$\r\n]*)`)|\[\[([^\]\r\n]*)\]\]""")
_SPLIT_SEP = re.compile(r"""(?:\s|[,;+&.]|_[ \t]*\r?\n|`[ \t]*\r?\n|\\[ \t]*\r?\n)*""")
_SPLIT_VAL = re.compile(r"[A-Za-z0-9+/=_\-.%~:]+")
_SPLIT_TAG = re.compile(r"([A-Za-z0-9_]{1,12})-(.+)$", re.S)
_SPLIT_WORDS = re.compile(r"(?:\bqw|%[wW])\s*([\[({</|!])")
_SPLIT_CLOSE = {"[": "]", "(": ")", "{": "}", "<": ">"}
_SPLIT_BAT = re.compile(r"""^[ \t]*@?set[ \t]+"?(?P<n>[^=\s"/][^=\s"]*)=(?P<v>[^"\r\n]*?)"?[ \t]*$""", re.I)
_SPLIT_XML = re.compile(r"<(?P<t>[A-Za-z_][\w.:-]*)\b[^<>]*>(?P<v>[^<>\r\n]+)</(?P=t)\s*>")


def _split_runs(src):
    """Joined chunk lists (list of value lists) of a source, in the three shapes above."""
    runs, cur, prev = [], [], None
    for m in _SPLIT_LIT.finditer(src):                                   # separator runs
        v = next((g for g in m.groups() if g is not None), "")
        if prev is not None and (m.start() - prev > 400 or not _SPLIT_SEP.fullmatch(src, prev, m.start())):
            if len(cur) > 1:
                runs.append(cur)
            cur = []
        cur.append(v)
        prev = m.end()
    if len(cur) > 1:
        runs.append(cur)
    for m in _SPLIT_WORDS.finditer(src):                                 # qw(..) / %w[..]
        close = _SPLIT_CLOSE.get(m.group(1), m.group(1))
        j = src.find(close, m.end())
        if 0 < j - m.end() < (1 << 16):
            runs.append(src[m.end():j].split())
    cur = []                                                              # one value per line
    for line in src.splitlines() + [""]:
        v = None
        bm = _SPLIT_BAT.match(line)
        if bm:
            v = re.sub(r"%" + re.escape(bm.group("n")) + r"%|!" + re.escape(bm.group("n")) + "!", "", bm.group("v"))
            v = None if re.search(r"%[A-Za-z_][\w.$#@-]*%|![A-Za-z_][\w.$#@-]*!", v) else v   # `set p=%c1%%c2%`: the join
        else:
            xm = list(_SPLIT_XML.finditer(line))
            lm = list(_SPLIT_LIT.finditer(line))
            if len(xm) == 1:
                v = xm[0].group("v").strip()
            elif len(lm) == 1:
                v = next((g for g in lm[0].groups() if g is not None), "")
        if v and _SPLIT_VAL.fullmatch(v):
            cur.append(v)
        else:
            if len(cur) > 1:
                runs.append(cur)
            cur = []
    return runs


def _split_array_plain(src, budget=0.8):
    """(material, plan) of the first chunk run that joins to `[<TAG>-]<material>` and peels to a plan, else
    (None, None). Bounded by `budget` seconds; never raises."""
    try:
        end, seen = time.time() + budget, set()
        for run in _split_runs((src or "")[:1 << 20]):
            run = [v.strip() for v in run if v.strip()]
            starts = [0] + [i for i, v in enumerate(run) if i and _SPLIT_TAG.match(v)]
            for i in starts[:6]:
                j = "".join(run[i:])
                if len(j) < 16 or not _SPLIT_VAL.fullmatch(j):
                    continue
                tm = _SPLIT_TAG.match(j)
                for tag, mat in ([(tm.group(1), tm.group(2))] if tm else []) + [("", j)]:
                    if mat in seen or time.time() > end:
                        continue
                    seen.add(mat)
                    plain = peel_plan(mat, tag, budget=min(0.25, max(0.02, end - time.time())))
                    if plain:
                        return mat, plain
    except Exception:  # noqa: BLE001 - a decoy / truncated carrier reads as nothing
        return None, None
    return None, None


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


# Whole-leaf encodings (prebuild source-encoding-normalize, 10-16): the zip member itself is UTF-16 (BOM'd or not,
# .reg / PS `-Encoding Unicode` saves), UTF-32, gzip'd, or one base64 blob of the source (optionally gzip'd / UTF-16
# under it). find_codecs() rescans normalize(src) only when every other reading of the text found no plan.
_LEAF_B64 = re.compile(r"[A-Za-z0-9+/\-_]+={0,2}")


def _leaf_text(b):
    """Source text of a leaf's bytes when they read as a printable script (UTF-8, UTF-16/32 by BOM or NUL
    interleave), else None."""
    if b[:4] in (b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff"):
        try:
            t = b.decode("utf-32")
        except UnicodeDecodeError:
            return None
    else:
        u = _utf16(b[:len(b) & ~1]) if b"\x00" in b[:256] or b[:2] in (b"\xff\xfe", b"\xfe\xff") else None
        try:
            t = (u or b).decode("utf-8")
        except UnicodeDecodeError:
            return None
    t = t.lstrip("\ufeff")
    if not t.strip() or sum(c.isprintable() or c in "\r\n\t" for c in t) < 0.95 * len(t):
        return None
    return t


def normalize(data, depth=3):
    """The source text under a whole-leaf encoding: BOM / UTF-16 / UTF-32 sniff, gzip / zlib / bz2 / xz, one base64
    (or base64url) blob, peeled up to `depth` layers. `data` is bytes or (lossy-decoded) text. None when the leaf is
    plain text already or reads as nothing printable -- never raises."""
    try:
        if isinstance(data, str):
            if not data:
                return None
            b = data.encode("latin-1") if max(data) < "\u0100" else data.encode("utf-8", "surrogateescape")
        else:
            b = bytes(data or b"")
        start, cur = b, b
        for _ in range(depth):
            if len(cur) < 8:
                break
            nxt = None
            if cur[:2] in (b"\xff\xfe", b"\xfe\xff", b"\xef\xbb") or b"\x00" in cur[:256]:
                t = _leaf_text(cur)
                nxt = t.encode("utf-8") if t is not None else None
            if nxt is None and (cur[:2] == b"\x1f\x8b" or cur[:3] == b"BZh" or cur[:6] == b"\xfd7zXZ\x00"
                                or (cur[0] & 0x0F == 8 and ((cur[0] << 8) | cur[1]) % 31 == 0)):
                nxt = _inflate(cur, raw=False)
            if nxt is None:
                s = re.sub(rb"\s+", b"", cur).decode("latin-1")
                if len(s) >= 24 and len(s) <= (1 << 20) and _LEAF_B64.fullmatch(s):
                    s = s.replace("-", "+").replace("_", "/").rstrip("=")
                    try:
                        nxt = base64.b64decode(s + "=" * (-len(s) % 4), validate=True)
                    except (binascii.Error, ValueError):
                        nxt = None
            if not nxt or nxt == cur:
                break
            cur = nxt
        if cur is start:
            return None
        t = _leaf_text(cur)
        return t if t is not None and t != data else None
    except Exception:  # noqa: BLE001 - a decoy / truncated leaf reads as nothing
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


# ------------------------------------------------------------------------------------------------ .reg / .inf hosts
# Target reg-inf-host-route (persistence hosts; builds on source-encoding-normalize): a regedit export (UTF-16LE + BOM
# for `Version 5.00`, ANSI for REGEDIT4) hides values as `"name"=hex(2):`/`hex(7):`/`hex:` comma-hex (UTF-16LE text,
# NUL-terminated / NUL-separated) wrapped with `,\` line continuations; an INF (CMSTP / setupapi) spells its values as
# %var% references into [Strings] and its registry writes as `root,subkey,name,flags,value` AddReg lines
# (RunPreSetupCommands / UnRegisterOCXSection name the command sections). _reg_inf_host() rewrites the host as plain
# text -- every hex value decoded to `"name"="text"`, every %var% substituted, every AddReg line as `"name"="value"` --
# and _reg_inf_codecs() rescans it, then peels each decoded value name-agnostically. Only consulted when nothing else
# produced a plan, so every earlier reading is unchanged. Bounded, regex + bytes only, never raises.
_REG_HDR = re.compile(r"^.{0,4}?(?:Windows Registry Editor Version [\d.]+|REGEDIT4)[ \t]*\r?$", re.M | re.I)
_REG_HEXVAL = re.compile(r"""^[ \t]*(?P<name>@|"(?:[^"\\\r\n]|\\.)*")[ \t]*=[ \t]*hex(?:\((?P<t>[0-9a-fA-F]{1,8})\))?:"""
                         r"""(?P<body>(?:[0-9a-fA-F]{2}|[ \t,]|\\[ \t]*\r?\n)*)""", re.M)
_INF_HINT = re.compile(r"^[ \t]*\[(?:version|strings|defaultinstall[\w.]*)\][ \t]*\r?$", re.M | re.I)
_INF_SECT = re.compile(r"^[ \t]*\[([^\]\r\n]+)\][ \t]*\r?$", re.M)
_INF_VAR = re.compile(r"%([^%\s,\"]{1,64})%|%%")
_INF_ROOTS = {"hkcr", "hkcu", "hklm", "hku", "hkr", "hkey_classes_root", "hkey_current_user", "hkey_local_machine",
              "hkey_users"}


def _reg_bytes_text(b, wide):
    """Strings of a registry value's bytes (UTF-16LE when `wide` or NUL-interleaved, else latin-1), NUL-split."""
    if wide or (len(b) >= 4 and b[1::2].count(0) >= 0.8 * (len(b) // 2)):
        t = b[:len(b) & ~1].decode("utf-16-le", "replace")
    else:
        t = b.decode("latin-1")
    return [s for s in t.lstrip("﻿").split("\x00") if s.strip()]


def _inf_split(line):
    """INF fields: comma-separated, `"..."` quoted with `""` as a literal quote, `;` comments outside quotes."""
    out, cur, q, i, quoted = [], [], False, 0, False
    while i < len(line):
        c = line[i]
        if q:
            if c == '"' and line[i + 1:i + 2] == '"':
                cur.append('"')
                i += 1
            elif c == '"':
                q = False
            else:
                cur.append(c)
        elif c == '"':
            q = quoted = True
        elif c == ",":
            out.append("".join(cur) if quoted else "".join(cur).strip())
            cur, quoted = [], False
        elif c == ";":
            break
        else:
            cur.append(c)
        i += 1
    out.append("".join(cur) if quoted else "".join(cur).strip())
    return out


def _reg_inf_host(src):
    """(rewritten text, [(name, value)]) for a .reg / .inf host, else None."""
    if not src or len(src) > (1 << 21):
        return None
    vals, extra = [], []
    if _REG_HDR.search(src[:4096]) or (re.match(r"\W{0,6}\[HKEY_", src) and "=hex" in src):
        ansi = bool(re.search(r"^.{0,4}?REGEDIT4", src[:256], re.I | re.M))

        def sub(m):
            t = (m.group("t") or "3").lower().lstrip("0") or "0"
            if t in ("4", "5", "b"):                          # dword / big-endian / qword: no text
                return m.group(0)
            b = bytes.fromhex("".join(re.findall(r"[0-9a-fA-F]{2}", m.group("body")))[:1 << 18])
            parts = _reg_bytes_text(b, not ansi and t in ("1", "2", "6", "7"))
            if t in ("3", "0") and parts and sum(ch.isprintable() for ch in "".join(parts)) < 0.9 * len("".join(parts)):
                return m.group(0)                             # binary blob, not text
            name = m.group("name").strip('"')
            vals.extend((name, p) for p in parts[:32])
            nl = "\r\n" if "\r\n" in m.group(0) else "\n"
            return nl.join('"%s"="%s"' % (name, p) for p in parts[:32]) + nl if parts else m.group(0)
        out = _REG_HEXVAL.sub(sub, src)
        return (out, vals) if vals else None
    if not _INF_HINT.search(src):
        return None
    txt = re.sub(r"\\[ \t]*\r?\n[ \t]*", "", src)            # INF `\` line continuation
    secs, last = {}, None
    for m in _INF_SECT.finditer(txt):
        if last is not None:
            secs.setdefault(last[0].strip().lower(), []).append(txt[last[1]:m.start()])
        last = (m.group(1), m.end())
    if last is not None:
        secs.setdefault(last[0].strip().lower(), []).append(txt[last[1]:])
    strings = {}
    for body in secs.get("strings", []) + [b for k, v in secs.items() if k.startswith("strings.") for b in v]:
        for ln in body.splitlines()[:4096]:
            k, eq, v = ln.partition("=")
            k = k.strip().strip('"')
            if eq and k and not k.startswith(";"):
                f = _inf_split(v.strip())
                strings.setdefault(k.lower(), f[0] if len(f) == 1 else v.strip())
    if not strings and "addreg" not in txt.lower():
        return None

    def subst(s):
        for _ in range(4):
            n = _INF_VAR.sub(lambda m: "%" if m.group(0) == "%%" else strings.get(m.group(1).lower(), m.group(0)), s)
            if n == s:
                break
            s = n
        return s
    out = subst(txt)
    for k, v in strings.items():
        vals.append((k, subst(v)))
    for ln in out.splitlines()[:8192]:                         # AddReg: root,subkey,name,flags,value[,value..]
        f = _inf_split(ln)
        if len(f) >= 5 and f[0].strip().lower() in _INF_ROOTS:
            try:
                flags = int(f[3] or "0", 0)
            except ValueError:
                flags = 0
            if flags & 1:                                      # FLG_ADDREG_BINVALUETYPE: hex byte fields
                try:
                    parts = _reg_bytes_text(bytes(int(x, 16) for x in f[4:] if x), False)
                except ValueError:
                    parts = []
            else:
                parts = [x for x in f[4:] if x]
            vals.extend((f[2], p) for p in parts[:32])
            extra.extend('"%s"="%s"' % (f[2], p) for p in parts[:32])
    return out + "\n" + "\n".join(extra) + "\n", vals


def _reg_inf_codecs(src, depth=0):
    """Codecs of a .reg / .inf host read as text (see _reg_inf_host): the rewritten host rescanned, then each decoded
    value peeled on its own. [] when `src` is not such a host or nothing reads as a plan."""
    try:
        host = _reg_inf_host(src)
        if not host:
            return []
        text, vals = host
        out = [dict(c, id=f"{c['id']}@host") for c in find_codecs(text, depth + 1) if c.get("plain")]
        if out:
            return out
        end = time.time() + 0.8
        for name, v in sorted(vals[:128], key=lambda nv: "descriptor" not in nv[0].lower()):
            if time.time() > end:
                break
            v = v.strip()
            if len(v) < 8:
                continue
            p = peel_plan(v, budget=max(0.05, min(0.3, end - time.time())))
            if p:
                return [{"id": f"host:{name}", "rep": "reg_value", "transform": "identity", "key": "", "material": v,
                         "plain": p}]
    except Exception:  # noqa: BLE001 - a decoy / truncated host reads as nothing
        return []
    return []


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


# ------------------------------------------------------------------------------------------------ PowerShell v=3 route
# Target ps-v3-polyglot-route: a polyglot-PowerShell day (.ps1/.psm1/.psd1/.ps1xml) writes the v=3 descriptor in PS
# syntax: `[string]$script:descriptor_x = "..."`, `${descriptor_x}`, `Set-Variable -Name descriptor_x -Value '..'`,
# here-strings `@' .. '@` / `@" .. "@`, `'a' + 'b'` / backtick-continued pieces, `-join @('a','b')`, `''` / `""` /
# backtick escapes, a .psd1 hashtable key `Descriptor = '..'` and a .ps1xml `<Name>descriptor_x</Name><Value>..`.
# find_codecs() consults _ps_v3_codecs() when nothing else produced a plan, and puts its plan first only when an
# earlier reading of the SAME literal is demonstrably lossy (a truncated first piece, or a `''`/`""` escape dropped).
# is_v3() / v3_plan() let a solver route v=3 before the v=1 `$encodedMaterial` / `$nativeTypes` JSON path.
_PSV3_VAR = re.compile(r"""(?:\[[\w.\[\]]+\]\s*)*\$\{?(?:(?:script|global|local|private|using|env):)?(?P<n>descriptor[_-]?[\w-]*)\}?"""
                       r"""[ \t]*=(?!=)[ \t]*""", re.I)
_PSV3_SETVAR = re.compile(r"""\b(?:Set|New)-Variable\s+(?:-Name\s+)?['"]?(?P<n>descriptor[_-]?[\w-]*)['"]?\s+"""
                          r"""(?:-Value\s+)?""", re.I)
_PSV3_KEY = re.compile(r"""(?:^|[;{(])[ \t]*['"]?(?P<n>descriptor[_-]?[\w-]*)['"]?[ \t]*=(?!=)[ \t]*""", re.I | re.M)
_PSV3_XML = re.compile(r"""<Name>\s*(?P<n>descriptor[_-]?[\w-]*)\s*</Name>\s*<Value>(?P<v>.*?)</Value>""", re.I | re.S)
_PSV3_NOTPS = re.compile(r"""<\?php|^\s*my\s+[$@%]|^\s*use\s+strict\b""", re.I | re.M)
_PSV3_MARK = re.compile(r"HUNTRESS_ANALYSIS_V\d+:[A-Za-z0-9_]+-")


def _psv3_str(s, i):
    """(value, end) of the PowerShell string literal at s[i] ('..', "..", @'..'@, @"..."@), else (None, i)."""
    n = len(s)
    if s.startswith(("@'", '@"'), i):
        q = s[i + 1]
        j = s.find("\n", i + 2)
        if j < 0 or s[i + 2:j].strip():
            return None, i
        m = re.compile(r"\r?\n" + q + "@").search(s, j)
        if not m:
            return None, i
        body = s[j + 1:m.start()]
        return (body if q == "'" else _psv3_dq(body, here=True)), m.end()
    if i < n and s[i] in "'‘’":
        out, j = [], i + 1
        while j < n:
            c = s[j]
            if c in "'‘’":
                if j + 1 < n and s[j + 1] in "'‘’":
                    out.append(c)
                    j += 2
                    continue
                return "".join(out), j + 1
            out.append(c)
            j += 1
        return None, i
    if i < n and s[i] in '"“”':
        j = i + 1
        while j < n:
            c = s[j]
            if c == "`":
                j += 2
                continue
            if c in '"“”':
                if j + 1 < n and s[j + 1] in '"“”':
                    j += 2
                    continue
                return _psv3_dq(s[i + 1:j]), j + 1
            j += 1
        return None, i
    return None, i


def _psv3_dq(body, here=False):
    """Expandable-string body: backtick escapes and `""` (no variable expansion: a constant descriptor has none)."""
    out, j, n = [], 0, len(body)
    while j < n:
        c = body[j]
        if c == "`" and j + 1 < n:
            d = body[j + 1]
            out.append(_PS_DQ_ESC.get(d, "" if d in "\r\n" else d))
            j += 2
        elif not here and c in '"“”' and j + 1 < n and body[j + 1] in '"“”':
            out.append(c)
            j += 2
        else:
            out.append(c)
            j += 1
    return "".join(out)


def _psv3_ws(s, i, nl):
    """Skip blanks (newlines too when `nl`), backtick line continuations and `<# #>` comments."""
    n = len(s)
    while i < n:
        if s[i] in " \t" or (nl and s[i] in "\r\n"):
            i += 1
        elif s[i] == "`" and s[i + 1:i + 2] in ("\n", "\r"):
            i += 2
        elif s.startswith("<#", i):
            e = s.find("#>", i + 2)
            if e < 0:
                return n
            i = e + 2
        else:
            return i
    return i


def _psv3_expr(s, i, depth=0):
    """(value, end) of a constant PowerShell string expression at s[i]: literals joined by `+`, `-join @(..)`,
    `(..)`, `@('a','b') -join ''`, `[string]::Concat(..)` / `[string]::Join('', ..)`; else (None, i)."""
    if depth > 6:
        return None, i
    parts, j = [], _psv3_ws(s, i, False)
    while True:
        j0 = j
        mj = re.compile(r"-join\s*", re.I).match(s, j)
        if not parts and mj:
            v, j = _psv3_group(s, mj.end(), depth)
        elif not parts and re.match(r"\[string\]::(?:concat|join)\s*\(", s[j:j + 24], re.I):
            k = s.index("(", j)
            isjoin = s[j:k].lower().rstrip().endswith("join")
            items, j = _psv3_items(s, k + 1, ")", depth)
            v = None if items is None or (isjoin and len(items) < 1) else \
                (items[0].join(items[1:]) if isjoin else "".join(items))
        elif s.startswith(("@(", "("), j):
            v, j = _psv3_group(s, j, depth)
            mj = re.compile(r"\s*-join\s*", re.I).match(s, j)
            if v is not None and mj:
                sep, j2 = _psv3_str(s, mj.end())
                if sep is not None:
                    v, j = v, j2                                # `@('a','b') -join ''`: separator already ''
        else:
            v, j = _psv3_str(s, j)
        if v is None:
            j = j0
            break
        parts.append(v)
        k = _psv3_ws(s, j, False)
        if s.startswith("+", k):
            j = _psv3_ws(s, k + 1, True)
            continue
        j = k
        break
    return ("".join(parts), j) if parts else (None, i)


def _psv3_items(s, i, close, depth):
    """Comma/newline separated constant expressions up to `close`: (list, end) or (None, i)."""
    items, j = [], i
    while True:
        j = _psv3_ws(s, j, True)
        if s.startswith(close, j):
            return items, j + 1
        if items and s.startswith((",", ";"), j):
            j += 1
            continue
        if s.startswith("@(", j) and _psv3_expr(s, j, depth + 1)[0] is None:  # nested array: flatten
            sub, j2 = _psv3_items(s, j + 2, ")", depth + 1)
            if sub is None:
                return None, i
            items += sub
            j = j2
            continue
        v, j2 = _psv3_expr(s, j, depth + 1)
        if v is None:
            return None, i
        items.append(v)
        j = j2


def _psv3_group(s, i, depth):
    """`@(..)` / `(..)` of constant strings -> their concatenation (the `-join` reading), or a bare literal."""
    if s.startswith("@(", i):
        items, j = _psv3_items(s, i + 2, ")", depth)
    elif s.startswith("(", i):
        items, j = _psv3_items(s, i + 1, ")", depth)
    else:
        v, j = _psv3_str(s, i)
        return v, j
    return ("".join(items) if items is not None else None), j


def _ps_descriptor_literals(src, limit=24):
    """(id, literal) of every PowerShell-syntax descriptor assignment (see the block comment above)."""
    out = []
    if not src or "descriptor" not in src.lower() or _PSV3_NOTPS.search(src[:1 << 16]):
        return out
    texts = [src]
    if "<Value>" in src or "&lt;" in src or "<ScriptBlock>" in src:
        import html
        texts.append(html.unescape(re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", src, flags=re.S)))
        for m in _PSV3_XML.finditer(src):
            out.append((m.group("n"), html.unescape(m.group("v").strip())))
    hashtable = "@{" in src
    for t in texts:
        for rx in (_PSV3_VAR, _PSV3_SETVAR) + ((_PSV3_KEY,) if hashtable else ()):
            for m in rx.finditer(t):
                if rx is _PSV3_KEY and "@{" not in t[:m.start()]:
                    continue
                v, _ = _psv3_expr(t, m.end())
                if v:
                    out.append((m.group("n"), v))
                if len(out) >= limit:
                    break
    seen, res = set(), []
    for n, v in out:
        ident = re.sub(r"(?i)^descriptor[_-]?", "", n) or "descriptor"
        if (ident, v) not in seen:
            seen.add((ident, v))
            res.append((ident, v))
    return res


def _ps_v3_codecs(src, budget=1.0):
    """Codec entries for PowerShell-syntax descriptors whose literal peels to a plan (marker TAG as the layer hint)."""
    try:
        lits = _ps_descriptor_literals(src)
        if not lits:
            return []
        am = _ANALYSIS_RE.search(src)
        end, out = time.time() + budget, []
        for ident, lit in lits:
            if time.time() > end:
                break
            plain = None
            for cand in (lit, re.sub(r"\s+", "", lit), lit.strip()):
                plain = peel_plan(cand, am.group("tag") if am else "",
                                  budget=min(0.4, max(0.05, end - time.time()))) if cand else None
                if plain:
                    break
            if plain:
                out.append({"id": ident, "rep": "descriptor", "transform": "identity", "key": "", "material": lit,
                            "plain": plain})
        return out
    except Exception:
        return []


def _psv3_lossy(full, part):
    """`part` is a lossy reading of the plan `full`: its truncated first piece, or `full` with quotes dropped."""
    if not full or not part or full == part:
        return False
    if full.startswith(part):
        return True
    sq = lambda t: re.sub(r"['\"‘’“”]", "", t)
    return sq(full) == sq(part)


def v3_plan(src):
    """The v=3 plan text of a source (str or bytes, UTF-16/BOM'd sources too), else None. Never raises."""
    try:
        if isinstance(src, (bytes, bytearray)):
            b = bytes(src)
            u = _utf16(b[:1 << 22]) if (b[:2] in (b"\xff\xfe", b"\xfe\xff") or b[1:64:2].count(0) > 20
                                         or b[0:64:2].count(0) > 20) else None
            src = (u or b).decode("utf-8", "ignore").lstrip("﻿")
        for c in find_codecs(src or ""):
            p = c.get("plain")
            if p and (p.lstrip().startswith("v=3") or re.match(r'\s*\{\s*"v"\s*:\s*"?3\b', p)):
                return p
    except Exception:
        return None
    return None


def is_v3(src):
    """True when a source is a v=3 polyglot (HUNTRESS_ANALYSIS marker, or a descriptor peeling to a `v=3` plan): route
    it to the v=3 reader before the v=1 `$encodedMaterial` / `$nativeTypes` JSON path. Never raises."""
    try:
        if isinstance(src, (bytes, bytearray)):
            b = bytes(src)
            if _PSV3_MARK.search(b.decode("latin-1")) or _PSV3_MARK.search(b.replace(b"\x00", b"").decode("latin-1")):
                return True
        elif _PSV3_MARK.search(src or ""):
            return True
        return v3_plan(src) is not None
    except Exception:
        return False


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
           bytes.fromhex("e4525c7b8cd8a74daeb15378d02996d3"), b"ITSF",
           b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d", b"\x0a\x0d\x0d\x0a")
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


def _vba_dir_offsets(d):
    """{module stream name (lower): MODULEOFFSET} from a VBA `dir` stream (MS-OVBA 2.3.4.2 records), or {}."""
    d, out, name, i = _ovba_decompress(d, 0) or b"", {}, None, 0
    while i + 6 <= len(d) and len(out) < 4096:
        rid, size = int.from_bytes(d[i:i + 2], "little"), int.from_bytes(d[i + 2:i + 6], "little")
        size = 6 if rid == 0x0009 else size                     # PROJECTVERSION: Size says 4, 6 bytes follow
        body, i = d[i + 6:i + 6 + size], i + 6 + size
        if rid == 0x001A:                                       # MODULESTREAMNAME (MBCS; 0x0032 unicode follows)
            name = body.decode("latin-1").lower()
        elif rid == 0x0031 and name is not None and size == 4:  # MODULEOFFSET of the source in that stream
            out[name] = int.from_bytes(body, "little")
    return out


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
            offs = {}                                           # VBA storages: dir-stream module offsets
            for ent in ole.listdir()[:300]:
                if ent[-1].lower() == "dir" and ole.get_size("/".join(ent)) < (1 << 20):
                    offs.update({"/".join(ent[:-1] + [k]).lower(): v
                                 for k, v in _vba_dir_offsets(ole.openstream(ent).read()).items()})
            for ent in ole.listdir()[:300]:
                if ole.get_size("/".join(ent)) > (8 << 20):
                    continue
                s = ole.openstream(ent).read()
                if len(ent) >= 2 and ent[-1].lower() not in ("dir", "_vba_project") and \
                        not ent[-1].startswith("__SRP_") and ole.exists("/".join(ent[:-1] + ["dir"])):
                    off = offs.get("/".join(ent).lower())
                    src = (_ovba_decompress(s, off) if off is not None else None) or _vba_sources(s)
                    if src:
                        yield f"{name}:{'/'.join(ent)}", src
                        continue
                yield from _carrier_blobs(s, f"{name}:{'/'.join(ent)}", depth + 1, budget)
        elif b[:2] == b"MZ" and depth == 0:                    # compiled AHK (Ahk2Exe) / any PE: RT_RCDATA members
            import pefile
            pe = pefile.PE(data=b, fast_load=True)
            pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]])
            for t in getattr(getattr(pe, "DIRECTORY_ENTRY_RESOURCE", None), "entries", [])[:64]:
                if t.id != 10 or not hasattr(t, "directory"):
                    continue
                for n in t.directory.entries[:64]:
                    for lang in getattr(getattr(n, "directory", None), "entries", [])[:8]:
                        d = lang.data.struct
                        if 0 < d.Size <= (8 << 20) and time.time() < budget:
                            data = pe.get_data(d.OffsetToData, d.Size)
                            data = data[3:] if data[:3] == b"\xef\xbb\xbf" else data
                            yield from _carrier_blobs(data, f"{name}#rcdata:{n.name or n.id}", depth + 1, budget)
        elif b[:4] in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d",
                       b"\x0a\x0d\x0d\x0a"):             # pcap / pcapng: reassembled HTTP bodies (the fetched stage)
            for o in http_objects(b, budget=max(0.05, budget - time.time())):
                if o["body"]:
                    yield from _carrier_blobs(o["body"], f"{name}#http:{o['uri'] or o['direction']}", depth + 1,
                                              budget)
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
        for name, text in texts if depth < 1 else ():   # a fetched HTTP body is a whole script: every reading
            if "#http:" in name and not name.endswith("~u16") and time.time() < end:
                for c in find_codecs(text, depth + 1):
                    if c.get("plain"):
                        return [dict(c, id=f"{c['id']}@{name}")]
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


# ------------------------------------------------------------------------------------------------ SaaS / add-in hosts
# D18 opened SaaS script hosts (Apps Script google_docs_sidebar). Siblings ship the same plan inside a host container:
# a JSON document whose string holds the script (Office Scripts .osts `body`, Apps Script project `files[].source`,
# Power Automate / Logic Apps definitions, VS Code package.json), or a zip / CRX package whose manifest names the script
# members (appsscript.json, Chrome MV3 manifest.json, Office add-in manifest.xml, VSIX). saas_host() unwraps the
# container into script texts; _saas_host_codecs() runs the normal readers over each.

_SAAS_STR = re.compile(r'"((?:[^"\\\r\n]|\\.){48,})"')
_SAAS_REF = re.compile(r'"(?:service_worker|main|browser|scripts|js|file|path|scriptFile)"\s*:\s*(\[[^\]]{0,2000}\]|"[^"]{1,300}")'
                       r'|(?:DefaultValue|src|href)\s*=\s*"([^"]{1,300})"')
_SAAS_PROFILES = (
    ("office_script", re.compile(r"ExcelScript\.Workbook|\"noCodeMetadata\"|\.osts$")),
    ("apps_script", re.compile(r"appsscript\.json|\.gs$|\"SERVER_JS\"|\b(?:DocumentApp|SpreadsheetApp|GmailApp|"
                               r"HtmlService|ScriptApp|CardService)\.|function do(?:Get|Post)\s*\(")),
    ("office_addin", re.compile(r"<OfficeApp\b|Office\.onReady|Office\.initialize")),
    ("browser_extension", re.compile(r"\"manifest_version\"|\"service_worker\"|\"content_scripts\"|^Cr24|\.crx$")),
    ("power_automate", re.compile(r"Microsoft\.Logic|\"definition\"\s*:\s*\{|\"triggers\"\s*:|\"actions\"\s*:")),
    ("vscode_extension", re.compile(r"\"activationEvents\"|\"engines\"\s*:\s*\{\s*\"vscode\"|extension\.vsixmanifest")),
    ("salesforce_apex", re.compile(r"\.cls$|@AuraEnabled|\b(?:public|global)\s+(?:with sharing\s+)?class\s+\w+")),
)


def _saas_json_strings(text, limit=24):
    """Code-bearing JSON string values of `text`, longest first: a full parse when it is JSON, else every long quoted
    literal json-unescaped (JSONC / truncated / JSON embedded in another file)."""
    import json
    vals = []
    s = (text or "").lstrip("﻿ \t\r\n")
    if s[:1] in "{[" and len(s) < (4 << 20):
        try:
            stack, n = [json.loads(s)], 0
            while stack and n < 20000:
                v, n = stack.pop(), n + 1
                if isinstance(v, dict):
                    stack.extend(v.values())
                elif isinstance(v, list):
                    stack.extend(v)
                elif isinstance(v, str) and len(v) >= 48:
                    vals.append(v)
        except (ValueError, RecursionError):
            vals = []
    if not vals:
        for m in _SAAS_STR.finditer((text or "")[:4 << 20]):
            if "\\" in m.group(1):
                try:
                    vals.append(json.loads('"' + m.group(1) + '"'))
                except ValueError:
                    continue
    vals = [v for v in dict.fromkeys(vals) if "\n" in v or "(" in v or "=" in v]
    return sorted(vals, key=len, reverse=True)[:limit]


def _saas_zip(raw):
    """The zip inside a package: a plain zip / VSIX / .xpi, or a Chrome CRX2/CRX3 (`Cr24` header then the zip)."""
    if raw[:4] == b"PK\x03\x04":
        return raw
    if raw[:4] == b"Cr24" and len(raw) > 16:
        ver = int.from_bytes(raw[4:8], "little")
        off = 12 + int.from_bytes(raw[8:12], "little") if ver == 3 else \
            16 + int.from_bytes(raw[8:12], "little") + int.from_bytes(raw[12:16], "little")
        if raw[off:off + 4] != b"PK\x03\x04":
            off = raw.find(b"PK\x03\x04", 12, 1 << 16)
        return raw[off:] if off > 0 else None
    return None


def saas_host(name, src):
    """Unwrap a cloud/SaaS/add-in script host. `src` = bytes or text of the file (`name` its file name, may be "").
    -> {"profile": guess or None, "scripts": [(member, text)]} -- manifest-referenced members first; [] when it is
    not a host container. Never raises."""
    import io
    import time
    out = {"profile": None, "scripts": []}
    try:
        end = time.time() + 0.4
        raw = bytes(src) if isinstance(src, (bytes, bytearray)) else None
        if raw is None and src:
            try:
                raw = src.encode("latin-1") if max(src) < "Ā" else None
            except (UnicodeEncodeError, ValueError):
                raw = None
        text = src if isinstance(src, str) else (raw or b"").decode("utf-8", "ignore")
        z = _saas_zip(raw) if raw else None
        scripts, sig = [], [name or "", text[:1 << 16] if z is None else "Cr24" if raw[:4] == b"Cr24" else ""]
        if z is not None:
            import zipfile
            zf = zipfile.ZipFile(io.BytesIO(z))
            mem = {}
            for zi in zf.infolist()[:200]:
                if zi.is_dir() or zi.flag_bits & 1 or zi.file_size > (4 << 20) or time.time() > end:
                    continue
                try:
                    mem[zi.filename] = zf.read(zi).decode("utf-8", "ignore").lstrip("﻿")
                except Exception:  # noqa: BLE001 - one bad member, keep walking
                    continue
            refs = set()
            for fn, t in mem.items():
                base = fn.rsplit("/", 1)[-1].lower()
                if base in ("manifest.json", "appsscript.json", "package.json", "manifest.xml",
                            "extension.vsixmanifest") or base.endswith((".html", ".htm", ".xml")):
                    sig.append(fn + "\n" + t[:1 << 14])
                    for m in _SAAS_REF.finditer(t[:1 << 18]):
                        for r in re.findall(r'[^"\[\],\s]+', m.group(1) or m.group(2) or ""):
                            refs.add(r.split("?")[0].rstrip("/").rsplit("/", 1)[-1].lower())
                elif base.endswith((".gs", ".osts", ".cls", ".trigger")):
                    sig.append(fn)
            order = sorted(mem, key=lambda fn: (fn.rsplit("/", 1)[-1].lower() not in refs,
                                                not fn.lower().endswith((".gs", ".js", ".ts", ".osts", ".cls",
                                                                         ".html", ".htm", ".json")), fn))
            for fn in order:
                scripts.append((fn, mem[fn]))
                if fn.lower().endswith((".json", ".osts")):
                    scripts.extend((f"{fn}#str", v) for v in _saas_json_strings(mem[fn], 8))
        elif text.lstrip("﻿ \t\r\n")[:1] in "{[" or "\\n" in text[:1 << 16]:
            scripts = [("#str", v) for v in _saas_json_strings(text)]
        for pool in (sig, [t[:1 << 14] for _, t in scripts[:6]]):     # the container's own signals win
            out["profile"] = next((p for p, rx in _SAAS_PROFILES if any(rx.search(s) for s in pool)), None)
            if out["profile"]:
                break
        out["scripts"] = scripts
    except Exception:  # noqa: BLE001 - truncated / impostor container: what was read so far
        pass
    return out


def _saas_host_codecs(src, raw, depth=0, name=""):
    import time
    try:
        host = saas_host(name, raw if raw is not None else src)
        end = time.time() + 0.8
        for member, text in host["scripts"]:
            if time.time() > end:
                break
            for c in find_codecs(text, depth + 1):
                if c.get("plain"):
                    tag = f"saas:{host['profile'] or 'host'}:{member}"
                    return [dict(c, id=f"{c['id']}@{tag}")]
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
# Target python-onion-regex-fold adds Python's module indirection (`__import__('zlib').decompress(..)`,
# `getattr(__import__('base64'),'b85decode')(..)`) and pyobfuscate-style `_ = lambda __: ..(__[::-1]); exec((_)(b'..'))`
# (the body is evaluated with the parameter bound). `marshal.loads` stops the fold: the code object is not unmarshalled,
# only a plan string constant whose marshal length field matches it exactly is reported (rep "marshal").
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


_CH_LAMBDA = r"(?:^|[;\n])[ \t]*{}[ \t]*=[ \t]*lambda[ \t]*([A-Za-z_]\w*)?[ \t]*:"
_CH_IMPORT = ("__import__", "import_module")


class _Chain:
    def __init__(self, src, end, depth=0, env=None):
        self.s, self.end, self.depth, self.nodes = src, end, depth, 0
        self.env, self.marshal = env or {}, None

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
            if last in _CH_IMPORT and a and isinstance(a[0], bytes):   # Python __import__('zlib')
                return ("mod", a[0].decode("latin-1")), j
            if last == "getattr" and len(a) >= 2 and isinstance(a[1], bytes) and isinstance(a[0], tuple):
                return ("fn", f"{a[0][1]}.{a[1].decode('latin-1')}"), j
            return self.call(("name", name), a, i), j
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
            if s.startswith("(", j) and isinstance(v, tuple) and v[0] in ("name", "fn"):
                a, i = self.args(j + 1, ")", lvl)         # `(_)(b'..')`, `getattr(m, 'f')(..)`
                v = self.call(v, a, j)
                continue
            m = re.compile(r"(?:\.|->|&\.)\s*([A-Za-z_]\w*[!?]?)").match(s, j)
            if not m or (isinstance(v, bytes) and s[j] == "." and j > i):
                return v, i
            name, k = m.group(1).rstrip("!?"), self.ws(m.end())
            if k < len(s) and s[k] == "(":
                a, i = self.args(k + 1, ")", lvl)
            else:
                a, i = [], m.end()
            if isinstance(v, tuple) and v[0] == "mod":    # __import__('base64').b64decode(..)
                q = f"{v[1]}.{name}"
                v = self.apply(name, a, q) if k < len(s) and s[k] == "(" else ("fn", q)
                continue
            v = self.apply(name, [v] + a)

    def call(self, f, a, at):
        """Call a function value: a Python `NAME = lambda P: BODY` bound before `at` (BODY evaluated with P = the first
        argument), else the named decoder."""
        name = f[1]
        if f[0] == "name" and name.lower() not in _CH_ALL and self.depth <= 3 and re.fullmatch(r"\w+", name):
            hit = None
            for hit in re.finditer(_CH_LAMBDA.format(re.escape(name)), self.s[:at]):
                pass
            if hit:
                sub = _Chain(self.s, self.end, self.depth + 1, {hit.group(1): a[0]} if hit.group(1) and a else {})
                sub.nodes = self.nodes
                v, _ = sub.expr(hit.end())
                self.nodes, self.marshal = sub.nodes, sub.marshal or self.marshal
                return v
        return self.apply(name.rsplit(".", 1)[-1], a, name)

    def var(self, name, at):
        """The value last assigned to `name` before offset `at` (`$x = ..;`, `x = ..`, `my $x = ..`), else None."""
        if name in self.env:
            return self.env[name]
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
        if n == "loads" and "marshal" in qual:           # code object: stop here, keep the blob (report only)
            self.marshal = v
            return None
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


def _marshal_plan(blob):
    """A plan string constant inside a marshal'd code object (`exec(marshal.loads(..))`), read without unmarshalling:
    the literal must sit right after a str/bytes type byte whose length field matches it exactly. Else None."""
    for m in re.finditer(rb"v=\d+\||\{", blob[:1 << 20]):
        st = m.start()
        for hdr, n in ((b"zZ", 1), (b"aAust", 4)):
            if st > n and blob[st - n - 1] & 0x7F in hdr:
                ln = int.from_bytes(blob[st - n:st], "little")
                run = blob[st:st + ln]
                if 8 <= ln == len(run) and looks_like_plan(run):
                    return run.decode("utf-8", "replace")
    return None


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
            if v is None and ch.marshal:                  # marshal.loads(..): report the code object's plan constant
                p = _marshal_plan(ch.marshal)
                if p:
                    return [{"id": "callchain", "rep": "marshal", "transform": "identity", "key": "",
                             "material": src[st:j][:400], "plain": p}]
                continue
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


# ------------------------------------------------------------------------------------------------ equivalence
# Sibling-outlier / semantic-equivalence questions (prebuild equivalence-outlier-compare, 10-16): D8 "doesn't match its
# siblings", D15/D16 "prove which are truly equivalent, expose the variant that quietly changed the plot". D16 polyglot
# families (9 languages x {benign_utility, downloader, launcher, staged_chain}, GM-verified fields): role / attack /
# adapter agree across the family, steps / stage_count / stage_profile / obfuscation rotate through 4 obfuscation
# profiles (the "scrambling"), and exactly one member (php) changes next_language. So the plot outlier is the
# minority on a field that is otherwise near-unanimous, never a field whose values spread across the family.
EQ_KEEP = ("role", "steps", "adapter", "attack", "stage_count", "stage_profile", "next_language", "scenario",
           "nativetypes", "native_types")
EQ_DROP = ("campaign", "campaign_id", "host", "host_id", "url", "file_path", "path", "upload_url", "next_stage",
           "codec", "rep", "transform", "key", "material", "v", "id", "ids", "obfuscation", "obfuscation_profile",
           "host_profile", "wallet", "mutex", "user_agent", "file", "note", "note_name", "extension", "dest")


def _eq_field(k):
    k = re.sub(r"[^0-9a-z]+", "_", str(k).strip().lower()).strip("_")
    return {"campaign": "campaign_id", "host": "host_id", "nativetypes": "native_types"}.get(k, k)


def _eq_value(field, v):
    """Comparison form of one plan value: steps as an ordered tuple, T1059.xxx as T1059 (the interpreter sub-id is the
    host language, not the plot), everything else stripped and case-folded."""
    if v is None:
        return None
    if field == "steps":
        parts = v if isinstance(v, (list, tuple)) else re.split(r"[>,|;\s]+", str(v))
        return tuple(str(p).strip().lower() for p in parts if str(p).strip()) or None
    if isinstance(v, (list, tuple)):
        return tuple(sorted(str(x).strip().casefold() for x in v))
    s = str(v).strip()
    if field == "attack":
        s = re.sub(r"^(T1059)\.\d{3}$", r"\1", s.upper())
    return s.casefold() or None


def _eq_dict(plan):
    """A decoded plan as a dict: dict as is, 'k=v|..' or JSON text / bytes parsed; None otherwise."""
    if isinstance(plan, (bytes, bytearray)):
        plan = bytes(plan).decode("utf-8", "replace")
    if isinstance(plan, str):
        s = plan.strip()
        if s[:1] == "{":
            import json
            plan = json.loads(s)
        else:
            plan = plan_kv(s)
    return plan if isinstance(plan, dict) else None


def plan_canonical(plan, keep=EQ_KEEP, drop=EQ_DROP):
    """{field: comparison value} of one decoded plan (dict, 'k=v|..' text or JSON text); identity fields dropped.
    `keep` None = every field not in `drop`. None when the plan is unreadable or has no comparable field."""
    try:
        plan = _eq_dict(plan)
        if not plan:
            return None
        kset = {_eq_field(k) for k in keep} if keep else None
        dset = {_eq_field(k) for k in drop or ()}
        out = {}
        for k, v in plan.items():
            f = _eq_field(k)
            if f in dset or (kset is not None and f not in kset) or isinstance(v, dict):
                continue
            cv = _eq_value(f, v)
            if cv is not None:
                out.setdefault(f, cv)
        return out or None
    except Exception:  # noqa: BLE001 - a decoy plan compares as nothing
        return None


def equivalence(plans, keep=EQ_KEEP, drop=EQ_DROP, unanimity=2 / 3):
    """{member: decoded plan} -> equivalence report, or None (< 2 comparable plans).
      classes        members grouped by identical canonical plan (largest first, then by name), class_count, singletons
      majority       {field: value} for every field one value holds in >= `unanimity` of the members that carry it
      outliers       members that differ from such a near-unanimous field (the variant that "changed the plot"),
                     diffs {member: {field: its raw value}}, diff_fields (sorted union)
      plot_classes   classes over the near-unanimous fields only (scrambling fields that spread are ignored),
                     plot_class_count, equivalent (the members agreeing with every majority value)
    Field values in diffs / majority are the member's original text (exact_text answers)."""
    try:
        canon, raw = {}, {}
        for m, p in (plans or {}).items():
            c = plan_canonical(p, keep, drop)
            if c:
                canon[m] = c
                raw[m] = {_eq_field(k): v for k, v in _eq_dict(p).items()}
        if len(canon) < 2:
            return None

        def group(fields):
            g = {}
            for m in sorted(canon):
                g.setdefault(tuple((f, canon[m].get(f)) for f in fields), []).append(m)
            return sorted(g.values(), key=lambda ms: (-len(ms), ms[0]))

        fields = sorted({f for c in canon.values() for f in c})
        classes = group(fields)
        majority, diffs = {}, {}
        for f in fields:
            vals = [(m, canon[m][f]) for m in sorted(canon) if f in canon[m]]
            if len(vals) < 2:
                continue
            counts = {}
            for _, v in vals:
                counts[v] = counts.get(v, 0) + 1
            top, n = max(counts.items(), key=lambda kv: kv[1])
            if n < len(vals) and n >= unanimity * len(vals) and n > len(vals) - n:
                for m, v in vals:
                    if v != top:
                        diffs.setdefault(m, {})[f] = raw[m].get(f)
            if n >= unanimity * len(vals) and n > len(vals) - n:
                maj_m = next(m for m, v in vals if v == top)
                majority[f] = raw[maj_m].get(f)
        plot = group(sorted(majority))
        return {"classes": classes, "class_count": len(classes), "singletons": [c[0] for c in classes if len(c) == 1],
                "majority": majority, "outliers": sorted(diffs), "diffs": diffs,
                "diff_fields": sorted({f for d in diffs.values() for f in d}),
                "plot_classes": plot, "plot_class_count": len(plot),
                "equivalent": sorted(m for m in canon if m not in diffs)}
    except Exception:  # noqa: BLE001
        return None


def equivalence_answer(report, kind, accepted_values=None, what="outlier"):
    """One GM answer from an equivalence() report. kind enum -> the outlier member (matched to accepted_values by name
    or stem), integer -> class count (what='plot' -> plot classes), exact_text -> the differing field (what='field')
    or the outlier's value on it (what='value'). "none" when the family has no outlier; None when unanswerable."""
    try:
        if not report:
            return None
        if kind == "integer":
            return str(report["plot_class_count"] if what == "plot" else report["class_count"])
        outs = report["outliers"]
        if not outs:
            return "none"
        if kind == "enum" or what == "outlier":
            m = outs[0] if len(outs) == 1 else None
            if m is None:
                return None
            stem = lambda s: re.sub(r"\.[A-Za-z0-9_]+$", "", str(s).rsplit("/", 1)[-1]).lower()
            for a in accepted_values or ():
                if stem(a) == stem(m) or stem(a) in stem(m).split("-") or stem(m) in stem(a):
                    return a
            return None if accepted_values else m
        f = report["diff_fields"]
        if len(f) != 1:
            return None
        if what == "field":
            return f[0]
        vals = {str(d[f[0]]) for d in report["diffs"].values() if f[0] in d}
        return vals.pop() if len(vals) == 1 else None
    except Exception:  # noqa: BLE001
        return None


# --- GM label regimes (prebuild batch-expansion-regime-lib) ----------------------------------------------------------
# Some GM labels flipped meaning mid-event. Each entry says when a contract is in the newer regime: `untimed` = an
# explicit run_for_time:false contract is in it, `since` = any contract whose started_at date is >= this is in it.
#   batch_expansion: old regime (D3-D14, timed D15) labels the handoff -- echo(!var!) makes any non-FOR join `delayed`;
#     statement regime (D15 untimed TT 0df5072d / Mastery 7fbfc526, D16 single 89161077 / TT a719c002 / Mastery
#     81bb44e6, all GM-verified) labels the join statement alone.
#   batch_control / vbs_control: no flip observed yet; set `untimed` / `since` here if they flip next.
LABEL_REGIMES = {
    "batch_expansion": {"untimed": True, "since": "2026-10-16"},
    "batch_control": {"untimed": False, "since": None},
    "vbs_control": {"untimed": False, "since": None},
}


def label_regime(field, contract=None):
    """'statement' when `contract` falls in `field`'s newer GM labelling regime (LABEL_REGIMES), else 'legacy'."""
    try:
        rule = LABEL_REGIMES.get(field) or {}
        c = contract if isinstance(contract, dict) else {}
        if rule.get("untimed") and c.get("run_for_time") is False:
            return "statement"
        since = rule.get("since")
        if since and str(c.get("started_at") or "")[:10] >= since:
            return "statement"
    except Exception:  # noqa: BLE001
        pass
    return "legacy"


def batch_join_pool(join_stmt):
    """Fragment-variable pool of a batch join line: `%%h%%G%%` / `%%h0%%` -> 'h', `%%FrAg0%%` -> 'frag'; None if absent."""
    s = str(join_stmt or "")
    m = re.search(r"%%([A-Za-z_]+?)%%G%%", s) or re.search(r"%%([A-Za-z_]+?)\d%%", s)
    return m.group(1).lower() if m else None


def label_expansion(join_stmt, pool=None, contract=None, echo_delayed=True):
    """GM `expansion` label for a batch join statement (`set "x=..."`, `call set ...`, `for ... do call set ...`).

    pool = the fragment-variable prefix (None: read it off the line); echo_delayed = the handoff is echo(!var!) (old
    regime only). Tables (all GM-verified):
      legacy:    FOR join -> call_double on the h pool, else for_indirect; bare `call set` over %%h..%% -> call_double;
                 echo(!var!) handoff -> delayed; other `call set` -> call_double; !a!!b! -> delayed; else percent.
      statement: FOR join -> for_indirect (any pool); bare `call set` over %%h..%% -> call_double; !a!!b! -> delayed;
                 anything else (other pools' call set, plain %a%%b%) -> percent.
    None when the line is not a join (no `=`, no %/! on the right-hand side)."""
    try:
        raw = str(join_stmt or "").strip()
        if "=" not in raw:
            return None
        rhs = raw.split("=", 1)[1]
        if not re.search(r"[%!]", rhs):
            return None
        pool = (pool or batch_join_pool(raw) or "").lower() or None
        stmt = label_regime("batch_expansion", contract) == "statement"
        if re.match(r"(?i)(?:@?\s*)for\s", raw) or re.search(r"(?i)\bdo\s+call\s+set\b", raw):
            return "for_indirect" if stmt or pool != "h" else "call_double"
        call_set = re.search(r"(?i)\bcall\s+set\b", raw)
        if call_set and "%%" in rhs and pool == "h":
            return "call_double"
        if stmt:
            return "delayed" if re.search(r"![^!\s]+!", rhs) else "percent"
        if echo_delayed:
            return "delayed"
        if call_set:
            return "call_double"
        return "delayed" if re.search(r"![^!\s]+!", rhs) else "percent"
    except Exception:  # noqa: BLE001
        return None


# --- network evidence reconcile (prebuild network-evidence-reconcile) ------------------------------------------------
# D17 "Fetch Quest": the decoded plans say where each member would fetch from, the network evidence says where the
# requests went; the answer is the indicator on only one side. Both sides are refanged + canonicalised for matching
# only (canon_host / canon_url); every reported value is the original spelling (exact_text answers are verbatim).
_RC_DEFANG = ((r"(?i)\bh(?:xx|\*\*|XX)p(s?)\b", r"http\1"), (r"(?i)\bfxp\b", "ftp"),
              (r"\s*(?:\[\s*(?:\.|dot)\s*\]|\(\s*(?:\.|dot)\s*\)|\{\s*(?:\.|dot)\s*\}|<\s*dot\s*>)\s*", "."),
              (r"\s*\[\s*:\s*\]\s*", ":"), (r"\[\s*:?//\s*\]", "://"), (r"\[\s*/\s*\]", "/"),
              (r"\s*(?:\[\s*@\s*\]|\(\s*at\s*\)|\[\s*at\s*\])\s*", "@"), (r"\\\.", "."), (r"\\/", "/"))
_RC_URL = re.compile(r"(?i)\b(?:https?|ftp|wss?)://[^\s\"'<>`|,;)\]}]+")
_RC_HOST = re.compile(r"(?i)^(?=.{1,253}$)(?:[a-z0-9_\-\u0080-￿]{1,63}\.)+(?:[a-z\u0080-￿][a-z\-\u0080-￿]"
                      r"{1,62}|xn--[a-z0-9\-]{1,59})$|^xn--[a-z0-9\-]+(?:\.[a-z0-9\-]+)+$")
_RC_IP = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$|^[0-9a-f:]*:[0-9a-f:.]+$", re.I)
_RC_FILE_EXT = re.compile(r"(?i)\.(?:ps1|psm1|js|jse|vbs|vbe|bat|cmd|py|sh|exe|dll|dat|bin|txt|zip|hta|wsf|php|lua|pl|rb|"
                          r"ts|ahk|au3|mof|scpt|applescript|proj|xml|json|ini|log|tmp|lnk|docm|xlsm)$")
_RC_HOST_FIELDS = re.compile(r"(?i)(?:^|_)(?:host(?:name)?|domain|server|c2|sni|server_name|callback|beacon|"
                             r"query|qry_name|destination(?:_?hostname)?|fqdn)$")
_RC_PLAN_URL_FIELDS = ("url", "upload_url", "next_stage", "download_url", "fetch_url", "stage_url", "c2_url")


def refang(s):
    """'hxxps://a[.]b[.]c/x' -> 'https://a.b.c/x' (also (.), {.}, [dot], [:], [://], [@]); other text unchanged."""
    s = str(s or "").strip().strip("\"'`<>")
    for pat, rep in _RC_DEFANG:
        s = re.sub(pat, rep, s)
    return s


def _rc_idna(host):
    # IDNA mapping: fullwidth / compatibility forms fold (NFKC), and the ideographic / fullwidth / halfwidth stops
    # U+3002 U+FF0E U+FF61 separate labels like '.'
    host = re.sub("[\u3002\uff0e\uff61]", ".", unicodedata.normalize("NFKC", host)).lower()
    out = []
    for lab in host.split("."):
        if lab and any(ord(c) > 127 for c in lab):
            try:
                lab = "xn--" + lab.encode("punycode").decode("ascii")
            except Exception:  # noqa: BLE001
                pass
        out.append(lab)
    return ".".join(out).rstrip(".")


def _rc_split(s):
    """(scheme, host, port, rest) of a refanged URL or bare host[/path]; host lowercased + IDNA, no userinfo."""
    s = refang(s)
    m = re.match(r"(?i)^([a-z][a-z0-9+.\-]*)://(.*)$", s)
    scheme, body = (m.group(1).lower(), m.group(2)) if m else ("", s)
    cut = re.search(r"[/?#]", body)
    auth, rest = (body[:cut.start()], body[cut.start():]) if cut else (body, "")
    auth = auth.rsplit("@", 1)[-1]
    port = None
    if auth.startswith("["):
        host, _, tail = auth[1:].partition("]")
        if tail.startswith(":") and tail[1:].isdigit():
            port = int(tail[1:])
    else:
        host, sep, p = auth.rpartition(":")
        if not sep or not p.isdigit() or ":" in host:
            host = auth
        else:
            port = int(p)
    host = _rc_idna(host.strip().rstrip(".").lower())
    return scheme, host, port, rest


def canon_host(s):
    """Matching form of a host / URL's host: refanged, lowercased, IDNA punycode, no port / userinfo / trailing dot.
    None when there is no plausible host (a bare word without a dot, a file name)."""
    try:
        _, host, _, _ = _rc_split(s)
        if not host or not (_RC_HOST.match(host) or _RC_IP.match(host) or host == "localhost"):
            return None
        return host
    except Exception:  # noqa: BLE001
        return None


def canon_url(s):
    """Scheme-less matching form 'host[:port]/path?query' of a URL: refanged, host canonical, default port, fragment
    and trailing '/' dropped, unreserved %XX decoded, path case kept. A TLS-observed https request and the declared
    http URL of the same resource compare equal. None when it is not a URL with a host."""
    try:
        scheme, host, port, rest = _rc_split(s)
        if not canon_host(host):
            return None
        rest = rest.split("#", 1)[0]
        rest = re.sub(r"%([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)) if re.match(
            r"[A-Za-z0-9\-._~]", chr(int(m.group(1), 16))) else "%" + m.group(1).upper(), rest)
        path, q, query = rest.partition("?")
        path = re.sub(r"/{2,}", "/", path).rstrip("/")
        dflt = {"http": 80, "https": 443, "ws": 80, "wss": 443, "ftp": 21}
        if ":" in host:   # IPv6 literal: keep the brackets so a port stays unambiguous
            host = f"[{host}]"
        hp = host if port is None or port in (80, 443) or port == dflt.get(scheme) else f"{host}:{port}"
        return hp + path + (q + query if query else "")
    except Exception:  # noqa: BLE001
        return None


def _rc_field(k):
    return re.sub(r"[^0-9a-z]+", "_", str(k).strip().lower()).strip("_")


def _rc_dict(plan):
    if isinstance(plan, (bytes, bytearray)):
        plan = bytes(plan).decode("utf-8", "replace")
    if isinstance(plan, dict):
        return plan
    s = str(plan or "").strip()
    if s[:1] == "{":
        try:
            import json
            d = json.loads(s)
            return d if isinstance(d, dict) else {}
        except ValueError:
            return {}
    out = {}
    for part in re.split(r"[|\r\n]+", s):
        if "=" in part:
            k, v = part.split("=", 1)
            out.setdefault(k.strip(), v.strip())
    return out


def declared_fetches(plans):
    """{member: decoded plan (dict / 'k=v|..' / JSON text)} -> [{member, field, value, url, host, stage}]: every plan
    value that is a URL (any field) or a dotted host (host/domain/server/c2 fields), plus non-URL next_stage names
    (`stage`, matched against observed URL basenames). `value` is the plan's original spelling."""
    out = []
    for m in sorted(plans or {}):
        try:
            d = _rc_dict(plans[m])
        except Exception:  # noqa: BLE001
            continue
        for k, v in d.items():
            if not isinstance(v, (str, int, float)) or isinstance(v, bool):
                continue
            f, v = _rc_field(k), str(v).strip()
            if not v:
                continue
            r = refang(v)
            if _RC_URL.fullmatch(r) and canon_url(r):
                out.append({"member": m, "field": f, "value": v, "url": canon_url(r), "host": canon_host(r),
                            "stage": None})
            elif _RC_HOST_FIELDS.search(f) and "." in r and not _RC_FILE_EXT.search(r) and canon_host(r):
                out.append({"member": m, "field": f, "value": v, "url": None, "host": canon_host(r), "stage": None})
            elif f in _RC_PLAN_URL_FIELDS and re.fullmatch(r"[\w.\-]{1,128}", r):
                out.append({"member": m, "field": f, "value": v, "url": None, "host": None,
                            "stage": r.rsplit("/", 1)[-1].lower()})
    return out


# --- declared fetch call sites (download cradles) read from the CODE -------------------------------------------------
# D17 "the source code says where it would fetch from": when a plan has no url (or disagrees), the declared side comes
# from the call sites. Regex only (no ast / eval): string assignments build a small symbol table, the call's argument
# is rebuilt from literals joined by + & . .. , -f / .format / % / sprintf, join() and char-code arrays.
_FS_URL = re.compile(r"(?i)\b(?:https?|ftp)://[^\s\"'<>`|]+")
_FS_LIT = re.compile(r'''(?P<p>[rRbBuUfF]{0,2})(?:"(?P<d>(?:[^"\\\n]|\\.|"")*)"|'(?P<s>(?:[^'\\\n]|\\.|'')*)'|`(?P<t>(?:[^`\\]|\\.)*)`)''', re.S)
_FS_IDENT = re.compile(r"[$@%]?\{?[A-Za-z_][\w]*(?:::[A-Za-z_]\w*)*\}?%?")
_FS_WRAP = re.compile(r"(?i)^(?:new\s+)?(?:URI(?:\.parse|\.join)?|URL|(?:urllib\.request\.|urllib2\.)?Request|str|String|"
                      r"CStr|tostring|URI::HTTPS?\.build|quoted\s+form\s+of|\[(?:string|uri|system\.uri)\])\s*"
                      r"(?:\((?P<a>.*)\)|(?P<b>[^()].*))$", re.S)
_FS_CHR = re.compile(r"(?i)^(?:chrw?|chr\$|\[char\]|string\.char|String\.fromCharCode|pack\s*\(\s*['\"][CU]\*?['\"]\s*,)"
                     r"\s*\(?\s*(?P<n>[\dxa-fA-FhH&,\s]+?)\s*\)?\s*\)?$")
_FS_NUM = re.compile(r"\s*(0x[0-9a-fA-F]+|&[hH][0-9a-fA-F]+|\d+)\s*")
_FS_ASSIGN = re.compile(r"""^\s*(?:<\?php\s+)?(?:(?:export|local|my|our|var|let|const|Dim|Set|Global|Local|Private|Public|static|"""
                        r"""readonly|declare(?:\s+-\w+)?|\$global:|\$script:)\s+)*(?P<n>[$@]?[A-Za-z_]\w*)"""
                        r"""(?:\s*:\s*[\w.\[\]<>|&' ]+?)?\s*(?P<op>:=|\+=|\.=|&=|\.\.=|<-|=(?![=~>]))\s*(?P<v>.+?)\s*;?\s*$""")
_FS_AS_SET = re.compile(r"(?i)^\s*set\s+(?P<n>\w+)\s+to\s+(?P<v>.+?)\s*$")
_FS_BAT_SET = re.compile(r'''(?i)^\s*@?set\s+(?:/[a-z]\s+)?(?:"(?P<n1>[^="]+)=(?P<v1>[^"]*)"|(?P<n2>[^="\s]+)=(?P<v2>.*))$''')
_FS_COMMENT = re.compile(r"(?i)^\s*(?:#(?![!{@])|//|::|rem\b|'|;|--(?!\w)|<!--|\*|/\*)")
_FS_ECHO = re.compile(r"(?i)^\s*@?(?:echo|write-host|write-output|print|puts|console\.log|msgbox|wscript\.echo)\b")
_FS_VERB = re.compile(r"(?i)^(GET|POST|PUT|HEAD|DELETE|PATCH|OPTIONS)$")
_FS_CMD_STOP = re.compile(r"""[;|\n)]|&&|(?<![\w"'])&(?!\w)""")
# (api, regex for the call head, kind): kind 'call' = parenthesised / VB-style args, 'open' = XMLHTTP-style
# .open(method, url), 'cmd' = command line (tokens until ; | && newline)
_FS_HEAD = r"(?im)(?:^|(?<=[\s(;|&\"'`{\[,=]))"
_FS_SITES = (
    ("Invoke-WebRequest", re.compile(_FS_HEAD + r"(?:Invoke-WebRequest|iwr)(?=\s)"), "cmd"),
    ("Invoke-RestMethod", re.compile(_FS_HEAD + r"(?:Invoke-RestMethod|irm)(?=\s)"), "cmd"),
    ("Start-BitsTransfer", re.compile(_FS_HEAD + r"Start-BitsTransfer(?=\s)"), "cmd"),
    ("certutil", re.compile(_FS_HEAD + r"certutil(?:\.exe)?(?=\s[^\n]*-urlcache)"), "cmd"),
    ("bitsadmin", re.compile(_FS_HEAD + r"bitsadmin(?:\.exe)?(?=\s[^\n]*/(?:transfer|addfile))"), "cmd"),
    ("curl", re.compile(_FS_HEAD + r"(?:/usr/bin/)?curl(?:\.exe)?(?=\s)"), "cmd"),
    ("wget", re.compile(_FS_HEAD + r"(?:/usr/bin/|busybox\s+)?wget(?:\.exe)?(?=\s)"), "cmd"),
    ("mshta", re.compile(_FS_HEAD + r"mshta(?:\.exe)?(?=\s+[\"']?(?:https?|ftp)://|\s+[\"']?[$%(])"), "cmd"),
    ("regsvr32", re.compile(_FS_HEAD + r"regsvr32(?:\.exe)?(?=\s[^\n]*/i:)"), "cmd"),
    ("WebClient", re.compile(r"(?i)\.(Download(?:String|File|Data)(?:Async|TaskAsync)?|Upload(?:String|File|Data|Values)"
                             r"(?:Async|TaskAsync)?|OpenRead(?:Async)?)\s*\("), "call"),
    ("HttpClient", re.compile(r"(?i)\.((?:Get(?:String|ByteArray|Stream)?|Post|Put|Send)Async)\s*\("), "call"),
    ("WebRequest", re.compile(r"(?i)\[(?:System\.)?Net\.(?:Http)?WebRequest\]::Create\s*\("), "call"),
    ("XMLHTTP.open", re.compile(r"(?i)\.open\s*(?=[(\s])"), "open"),
    ("fetch", re.compile(r"(?<![\w.$])fetch\s*\("), "call"),
    ("http.get", re.compile(r"\b(https?)\.(get|request)\s*\("), "call"),
    ("axios", re.compile(r"\baxios(?:\.(get|post|put|delete|head|patch|request))?\s*\("), "call"),
    ("urllib.urlopen", re.compile(r"(?<![\w$])(?:urllib2?\.(?:request\.)?|request\.)?(urlopen|urlretrieve)\s*\("), "call"),
    ("requests", re.compile(r"\b(?:requests|httpx|session|s)\.(get|post|put|head|delete|patch|request)\s*\("), "call"),
    ("Net::HTTP", re.compile(r"\bNet::HTTP\.(get_response|get|post_form|post|start)\s*[(\s]"), "call"),
    ("URI.open", re.compile(r"(?<![\w.])(?:URI\.|Kernel\.)?open\s*\(\s*(?=[\"']?(?:https?|ftp)://|URI|[\"'][^\"']*#\{)"), "call"),
    ("LWP", re.compile(r"(?<![\w>$.])(get|getstore|getprint|mirror|head)\s*\(\s*(?=[\"'$])"), "call"),
    ("LWP", re.compile(r"->\s*(get|post|put|head|mirror|request)\s*\(\s*(?=[\"'$])"), "call"),
    ("file_get_contents", re.compile(r"(?i)\b(file_get_contents|fopen|readfile|file|copy|curl_init)\s*\(\s*(?=[\"'$])"), "call"),
    ("curl_setopt", re.compile(r"(?i)\bcurl_setopt\s*\(\s*\$\w+\s*,\s*CURLOPT_URL\s*,"), "call"),
    ("socket.http", re.compile(r"\b(?:http|socket\.http|https)\.request\s*\(?\s*(?=[\"'\w{])"), "call"),
    ("ngx.location.capture", re.compile(r"\bngx\.location\.capture\s*\("), "call"),
    ("Download", re.compile(r"(?i)(?<![\w.])(?:Download|UrlDownloadToFile)\s*(?:\(|,)"), "call"),
    ("InetGet", re.compile(r"(?i)(?<![\w.])(InetGet|InetRead|_INetGetSource)\s*\("), "call"),
)
_FS_UNESC = re.compile(r"\\(x[0-9a-fA-F]{2}|u\{[0-9a-fA-F]{1,6}\}|u[0-9a-fA-F]{4}|[0-7]{1,3}|.)|`([0abefnrtv`\"'$])", re.S)


def _fs_unescape(s, ps=True):
    def one(m):
        e, b = m.group(1), m.group(2)
        if b is not None:
            return {"0": "\0", "a": "\a", "b": "\b", "e": "\x1b", "f": "\f", "n": "\n", "r": "\r", "t": "\t",
                    "v": "\v"}.get(b, b) if ps else m.group(0)
        if e[0] == "x":
            return chr(int(e[1:], 16))
        if e[0] == "u" and len(e) > 1:
            return chr(int(e.strip("u{}"), 16))
        if e[0] in "01234567":
            return chr(int(e, 8) & 0xFF)
        return {"n": "\n", "r": "\r", "t": "\t", "0": "\0"}.get(e, e)
    return _FS_UNESC.sub(one, s)


def _fs_split(expr, seps):
    """Split at top level (outside quotes / brackets) on the regex `seps`; [] when brackets don't balance."""
    out, depth, i, last, q = [], 0, 0, 0, None
    n = len(expr)
    while i < n:
        c = expr[i]
        if q:
            if c == "\\" and q != "'":
                i += 2
                continue
            if c == q:
                q = None
        elif c in "\"'`":
            q = c
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
            if depth < 0:
                return []
        elif depth == 0:
            m = seps.match(expr, i)
            if m and m.end() > i:
                out.append(expr[last:i])
                i = last = m.end()
                continue
        i += 1
    out.append(expr[last:])
    return out


_FS_CONCAT = re.compile(r"\s*\.\.\s*|\s*\+\s*|\s+&\s+|&(?=[\"'$\w(])|\s+\.\s+|(?<=[\"')\w])\.(?=[\"'$])")
_FS_COMMA = re.compile(r"\s*,\s*")


def _fs_ints(s):
    parts = [p for p in re.split(r"[\s,]+", s.strip()) if p]
    if not parts:
        return None
    try:
        vals = [int(p, 16) if p[:2].lower() == "0x" else int(p[2:], 16) if p[:2].lower() == "&h" else int(p)
                for p in parts]
    except ValueError:
        return None
    return "".join(chr(v) for v in vals) if all(0 < v < 0x110000 for v in vals) else None


def _fs_lookup(name, env):
    k = name.strip("${}%@!")
    k = k[7:] if k.lower().startswith(("global:", "script:")) else k
    return env.get(k, env.get(k.lower()))


def _fs_interp(body, env, kind):
    """Substitute $x / ${x} / #{x} / %x% (and {x} for f-strings) when x is known; None when a reference is unknown."""
    pats = {"f": r"\{([A-Za-z_]\w*)\}", "t": r"\$\{\s*([A-Za-z_]\w*)\s*\}",
            "d": r"\$\(\s*\$?([A-Za-z_]\w*)\s*\)|\$\{([A-Za-z_]\w*)\}|#\{\s*@?([A-Za-z_]\w*)\s*\}|"
                 r"\$([A-Za-z_]\w*)(?![\w(])|%([A-Za-z_]\w*)%"}[kind]
    bad = []

    def one(m):
        v = _fs_lookup(next(g for g in m.groups() if g), env)
        if v is None:
            bad.append(m.group(0))
            return m.group(0)
        return v
    s = re.sub(pats, one, body)
    return None if bad else s


def _fs_eval(expr, env, depth=0):
    """String value of a literal-only expression, or None."""
    try:
        e = expr.strip().rstrip(";").strip()
        if not e or depth > 8 or len(e) > 8000:
            return None
        while e[0] == "(" and e[-1] == ")" and _fs_split(e[1:-1], re.compile(r"(?!)")) != []:
            e = e[1:-1].strip()
            if not e:
                return None
        e = re.sub(r"(?i)^\[(?:string|uri|system\.uri)\]\s*", "", e)
        m = _FS_LIT.fullmatch(e)
        if m:
            p = m.group("p").lower()
            if m.group("s") is not None:
                body = m.group("s").replace("''", "'") if "\\" not in m.group("s") else _fs_unescape(m.group("s"), False)
                return _fs_interp(body, env, "f") if "f" in p else body
            if m.group("t") is not None:
                return _fs_interp(_fs_unescape(m.group("t"), False), env, "t")
            body = m.group("d").replace('""', '"')
            body = body if "r" in p else _fs_unescape(body, ps="`" in body)
            if "f" in p:
                return _fs_interp(body, env, "f")
            return _fs_interp(body, env, "d") if re.search(r"[$#%]", body) else body
        if re.fullmatch(r"\d+", e):
            return e
        if _FS_IDENT.fullmatch(e):
            return _fs_lookup(e, env)
        m = _FS_CHR.match(e)
        if m:
            return _fs_ints(m.group("n").rstrip(")"))
        # -f format / .format / % / sprintf / string.format
        ps = _fs_split(e, re.compile(r"(?i)\s+-f\s+"))
        if len(ps) == 2:
            fmt = _fs_eval(ps[0], env, depth + 1)
            args = [_fs_eval(a, env, depth + 1) for a in _fs_split(ps[1].strip().lstrip("@"), _FS_COMMA)]
            if fmt is not None and None not in args:
                return re.sub(r"\{(\d+)(?:[:,][^}]*)?\}", lambda m: args[int(m.group(1))] if int(m.group(1)) < len(args)
                              else m.group(0), fmt)
            return None
        m = re.fullmatch(r"(?s)(.+?)\.format\s*\((.*)\)", e)
        if m and _FS_LIT.fullmatch(m.group(1).strip()):
            fmt = _fs_eval(m.group(1), env, depth + 1)
            args = [_fs_eval(a, env, depth + 1) for a in _fs_split(m.group(2), _FS_COMMA)]
            if fmt is not None and None not in args:
                it = iter(args)
                return re.sub(r"\{(\d*)\}", lambda mm: args[int(mm.group(1))] if mm.group(1) else next(it, ""), fmt)
            return None
        m = (re.fullmatch(r"(?is)(?:s?printf|string\.format|String\.Format)\s*\((.*)\)", e))
        pm = None if m else _fs_split(e, re.compile(r"\s*%\s*"))
        if m or (pm and len(pm) == 2 and _FS_LIT.fullmatch(pm[0].strip())):
            parts = _fs_split(m.group(1), _FS_COMMA) if m else [pm[0]] + _fs_split(pm[1].strip().strip("()"), _FS_COMMA)
            vals = [_fs_eval(a, env, depth + 1) for a in parts]
            if not parts or None in vals:
                return None
            it = iter(vals[1:])
            return re.sub(r"%[-\d.]*[sd]|\{(\d+)\}", lambda mm: (vals[1:][int(mm.group(1))] if mm.group(1) else
                                                                next(it, "")), vals[0])
        # join forms over arrays of literals / char codes
        m = (re.fullmatch(r"(?is)(?:\[char\[\]\]\s*)?@?\((?P<a>.*)\)\s*-join\s*(?P<s>.*)", e)
             or re.fullmatch(r"(?is)-join\s*(?:\[char\[\]\]\s*)?@?\((?P<a>.*)\)(?P<s>)", e)
             or re.fullmatch(r"(?is)(?P<s>[\"'][^\"']*[\"'])\.join\s*\(\s*(?:map\s*\(\s*chr\s*,\s*)?[\[(](?P<a>.*)[\])]\s*\)?\s*\)", e)
             or re.fullmatch(r"(?is)\[(?P<a>.*)\](?:\.map\s*\([^)]*fromCharCode[^)]*\)\s*)?\.join\s*\(\s*(?P<s>[^)]*)\)", e)
             or re.fullmatch(r"(?is)(?:join|implode)\s*\(\s*(?P<s>[\"'][^\"']*[\"'])\s*,\s*(?:array\s*\(|\[|\(|\{)?(?P<a>.*?)[\])}]?\s*\)", e)
             or re.fullmatch(r"(?is)table\.concat\s*\(\s*\{(?P<a>.*)\}\s*(?:,\s*(?P<s>.+))?\)", e))
        if m:
            sep = _fs_eval(m.group("s"), env, depth + 1) if (m.group("s") or "").strip() else ""
            items = _fs_split(m.group("a"), _FS_COMMA)
            if sep is None or not items:
                return None
            codes = re.search(r"(?i)char|chr|fromCharCode", e) and all(re.fullmatch(r"\s*(?:0x[0-9a-f]+|\d+)\s*", i, re.I)
                                                                       for i in items)
            if codes:
                return _fs_ints(",".join(items))
            vals = [_fs_eval(i, env, depth + 1) for i in items]
            return None if None in vals else sep.join(vals)
        m = re.fullmatch(r"(?is)bytes\s*\(\s*\[(?P<a>[\d\s,xa-fA-F]+)\]\s*\)\.decode\s*\([^)]*\)", e)
        if m:
            return _fs_ints(m.group("a"))
        m = _FS_WRAP.match(e)
        if m and (m.group("a") or m.group("b")):
            inner = m.group("a") if m.group("a") is not None else m.group("b")
            first = _fs_split(inner, _FS_COMMA)
            return _fs_eval(first[0], env, depth + 1) if first else None
        parts = _fs_split(e, _FS_CONCAT)
        if len(parts) < 2:
            parts = [p for p in _fs_split(e, re.compile(r"\s+")) if p]   # adjacent literals ("a" "b")
            if len(parts) < 2 or not all(_FS_LIT.fullmatch(p) for p in parts):
                return None
        vals = [_fs_eval(p, env, depth + 1) for p in parts]
        return None if None in vals else "".join(vals)
    except Exception:  # noqa: BLE001
        return None


def _fs_flat(src):
    """Join line continuations (PS `, VB _, batch ^, shell \\) keeping every offset, so line numbers stay true."""
    return re.sub(r"(?:(?<=\s)_|`|\^|\\)(\r?\n)", lambda m: " " * len(m.group(0)), src)


def _fs_env(flat):
    env = {}
    for ln in flat.splitlines()[:20000]:
        if len(env) > 4000:
            break
        for st in (_fs_split(ln, re.compile(r"\s*;\s*")) or [ln])[:16]:
            m = _FS_BAT_SET.match(st)
            if m:
                n, v = (m.group("n1"), m.group("v1")) if m.group("n1") else (m.group("n2"), m.group("v2"))
                v = re.sub(r"\s*&\s*rem\b.*$", "", v, flags=re.I).replace("^", "")
                v = re.sub(r"%(\w+)%|!(\w+)!", lambda mm: _fs_lookup(mm.group(1) or mm.group(2), env) or mm.group(0), v)
                env[n.strip()] = env[n.strip().lower()] = v
                continue
            m = _FS_AS_SET.match(st)
            if m:
                n, op, rhs = m.group("n"), "=", m.group("v")
            else:
                m = _FS_ASSIGN.match(st)
                if not m:
                    continue
                n, op, rhs = m.group("n"), m.group("op"), m.group("v")
            rhs = re.sub(r"\s+(?:#|//|--|;)\s[^\"'`]*$", "", rhs)
            if op == "=" and not re.match(r"""\s*[\"'`(\[$@%\w-]""", rhs):
                continue
            v = _fs_eval(rhs, env)
            if v is None and op == "=" and n[0] not in "$@" and re.fullmatch(r"[\w.:/?&=%~+-]+", rhs) and \
                    _FS_URL.fullmatch(rhs):
                v = rhs                                    # bash / AHK v1 legacy bare value
            key = n.lstrip("$@")
            if v is None:
                env.pop(key, None)
                env.pop(key.lower(), None)
                continue
            if op != "=" and op not in (":=", "<-"):
                old = _fs_lookup(key, env)
                if old is None:
                    continue
                v = old + v
            env[key] = env[key.lower()] = v[:4096]
    return env


def _fs_args(text, i):
    """Argument list text after a call head ending at offset i: balanced (...) or the rest of the logical line."""
    j = i
    while j < len(text) and text[j] in " \t":
        j += 1
    if text[i - 1:i] == "(":
        j = i - 1
    if j < len(text) and text[j] == "(":
        depth, q, k = 0, None, j
        while k < len(text) and k - j < 4000:
            c = text[k]
            if q:
                if c == "\\" and q != "'":
                    k += 1
                elif c == q:
                    q = None
            elif c in "\"'`":
                q = c
            elif c in "([{":
                depth += 1
            elif c in ")]}":
                depth -= 1
                if depth == 0:
                    return text[j + 1:k]
            elif c == "\n" and depth == 0:
                break
            k += 1
        return None
    end = text.find("\n", j)
    return text[j:end if end >= 0 else len(text)].strip()


def _fs_url_of(val):
    m = _FS_URL.search(val or "")
    return m.group(0).rstrip(".,") if m else None


def _fs_cmd(api, rest, env):
    """(url, method) from a command line's tokens."""
    cut = _fs_split(rest, _FS_CMD_STOP)
    rest = cut[0] if cut else rest
    toks = [t for t in _fs_split(rest, re.compile(r"\s+")) if t]
    url, method, prev = None, "GET", ""
    for t in toks[:64]:
        low = t.lower()
        if api == "regsvr32" and low.startswith("/i:"):
            t = t[3:]
        v = _fs_eval(t, env)
        if v is None and not re.match(r"""[\"'`($@%{]""", t):
            v = re.sub(r"%(\w+)%|!(\w+)!|\$\{?(\w+)\}?", lambda m: _fs_lookup(next(g for g in m.groups() if g), env)
                       or "\0", t)
            v = None if "\0" in v else v
        if prev in ("-x", "--request", "-method", "--method") and v and _FS_VERB.match(v):
            method = v.upper()
        elif low in ("-d", "--data", "--data-binary", "--data-raw", "--data-urlencode", "-f", "--form",
                     "--post-data", "--post-file", "/upload") and api in ("curl", "wget", "bitsadmin") and \
                not (api == "curl" and low == "-f"):
            method = "POST"
        elif low in ("-t", "--upload-file") and api == "curl":
            method = "PUT"
        elif low in ("-i", "--head") and api == "curl":
            method = "HEAD"
        elif low.startswith("--method="):
            method = t.split("=", 1)[1].upper()
        elif prev == "-transfertype" and v and v.lower() == "upload":
            method = "POST"
        if url is None and v and _fs_url_of(v) and (v.strip().lower().startswith(("http", "ftp")) or
                                                    api in ("regsvr32", "mshta")):
            url = _fs_url_of(v)
        prev = low
    return url, method


def fetch_sites(src, name=""):
    """Download-cradle call sites in a script's CODE -> [{api, url, method, line, echo}] in source order. `url` is the
    target rebuilt from the file's own literals (concat / format / join / char codes / variables assigned literals)
    or None when it comes from runtime data (e.g. the decoded plan); `echo` marks a site on an echo/print line (the
    command is only displayed). Comment lines are skipped. [] for a script with no cradle / unreadable input."""
    try:
        if isinstance(src, (bytes, bytearray)):
            b = bytes(src)
            src = (b.decode("utf-16", "replace") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else
                   b.decode("utf-8-sig", "replace"))
        text = _fs_flat(str(src or "")[:2_000_000])
        env = _fs_env(text)
        lines = text.split("\n")
        starts = [0]
        for ln in lines:
            starts.append(starts[-1] + len(ln) + 1)
        out, seen = [], set()
        import bisect
        for api, rx, kind in _FS_SITES:
            for m in rx.finditer(text):
                lno = bisect.bisect_right(starts, m.start())
                line = lines[lno - 1]
                if _FS_COMMENT.match(line) or (lno, m.start()) in seen:
                    continue
                args = _fs_args(text, m.end())
                if args is None:
                    continue
                url, method, sub = None, "GET", (m.group(1) if m.groups() else "") or ""
                if kind == "cmd":
                    url, method = _fs_cmd(api, args, env)
                else:
                    if kind == "call" and not text[m.end() - 1:m.end()] in "(," and api not in ("Net::HTTP", "socket.http"):
                        args = args.strip()
                    items = _fs_split(args, _FS_COMMA) or [args]
                    if kind == "open":
                        verb = _fs_eval(items[0], env) if items else None
                        if not verb or not _FS_VERB.match(verb.strip()) or len(items) < 2:
                            continue
                        method, items = verb.strip().upper(), items[1:2]
                    elif api == "requests" and sub == "request" or api == "LWP" and sub == "request":
                        verb = _fs_eval(items[0], env) if items else None
                        method, items = ((verb or "GET").upper(), items[1:2]) if verb and _FS_VERB.match(verb) else \
                            (method, items)
                    elif re.match(r"(?i)upload|post|put", sub):
                        method = "PUT" if sub.lower().startswith("put") else "POST"
                    for it in items[:4]:
                        it2 = re.sub(r"^\s*(?:url|uri)\s*[:=]>?\s*", "", it)
                        v = _fs_eval(it2, env)
                        if v is None and _FS_URL.fullmatch(it2.strip()):
                            v = it2.strip()                     # AHK v1 / AutoIt legacy bare argument
                        elif v is None and re.fullmatch(r"\s*%\w+%\s*", it2):
                            v = _fs_lookup(it2.strip(), env)
                        if v is None and it2.strip()[:1] == "{":
                            mm = re.search(r"""\burl\s*[:=]\s*(.+?)\s*(?:,\s*\w+\s*[:=]|\}$)""", it2.strip(), re.S)
                            v = _fs_eval(mm.group(1), env) if mm else None
                        if v is not None and _fs_url_of(v):
                            url = _fs_url_of(v)
                            break
                        if v is not None and api == "ngx.location.capture":
                            url = None
                            break
                    mm = re.search(r"""(?i)\bmethod\s*[:=]\s*['"]?(?:ngx\.HTTP_)?(GET|POST|PUT|HEAD|DELETE|PATCH)""", args)
                    if mm:
                        method = mm.group(1).upper()
                    if api == "URI.open" and url is None:
                        continue
                if api in ("file_get_contents", "LWP", "socket.http") and url is None:
                    continue                                    # local-file reads / plain gets
                seen.add((lno, m.start()))
                out.append({"api": api, "url": url, "method": method, "line": lno,
                            "echo": bool(_FS_ECHO.match(line))})
        out.sort(key=lambda d: d["line"])
        return out
    except Exception:  # noqa: BLE001
        return []


# --- fetch API / LOLBin -> ATT&CK + adapter label (prebuild lolbin-download-attack-table, 10-18) ---------------------
# GM history: a plan's own attack= always wins; this table only fills ids for members with no plan value. Candidates
# are ordered (first = primary). `adapter` is the canonical tool/API name (plans spell it e.g. adapter=bitsadmin.exe).
_FA_DOWNLOAD = ("T1105",)
_FA_UPLOAD = ("T1041", "T1567", "T1105")
FETCH_ATTACK = {
    # api (fetch_sites name): (adapter label, ids)
    "certutil": ("certutil.exe", ("T1105",)),
    "bitsadmin": ("bitsadmin.exe", ("T1197", "T1105")),
    "Start-BitsTransfer": ("Start-BitsTransfer", ("T1197", "T1105")),
    "mshta": ("mshta.exe", ("T1218.005", "T1105")),
    "regsvr32": ("regsvr32.exe", ("T1218.010", "T1105")),
    "rundll32": ("rundll32.exe", ("T1218.011", "T1105")),
    "msiexec": ("msiexec.exe", ("T1218.007", "T1105")),
    "curl": ("curl", _FA_DOWNLOAD), "wget": ("wget", _FA_DOWNLOAD),
    "Invoke-WebRequest": ("Invoke-WebRequest", _FA_DOWNLOAD), "Invoke-RestMethod": ("Invoke-RestMethod", _FA_DOWNLOAD),
    "WebClient": ("Net.WebClient", _FA_DOWNLOAD), "HttpClient": ("Net.Http.HttpClient", _FA_DOWNLOAD),
    "WebRequest": ("Net.WebRequest", _FA_DOWNLOAD), "XMLHTTP.open": ("MSXML2.XMLHTTP", _FA_DOWNLOAD),
    "fetch": ("fetch", _FA_DOWNLOAD), "http.get": ("http.get", _FA_DOWNLOAD), "axios": ("axios", _FA_DOWNLOAD),
    "urllib.urlopen": ("urllib.request", _FA_DOWNLOAD), "requests": ("requests", _FA_DOWNLOAD),
    "Net::HTTP": ("Net::HTTP", _FA_DOWNLOAD), "URI.open": ("open-uri", _FA_DOWNLOAD), "LWP": ("LWP", _FA_DOWNLOAD),
    "file_get_contents": ("file_get_contents", _FA_DOWNLOAD), "curl_setopt": ("php-curl", _FA_DOWNLOAD),
    "socket.http": ("socket.http", _FA_DOWNLOAD), "Download": ("UrlDownloadToFile", _FA_DOWNLOAD),
    "InetGet": ("InetGet", _FA_DOWNLOAD),
}
_FA_DECODE = re.compile(r"(?i)(?:^|\s)[-/]decode(?:hex)?\b")
_FA_UPVERB = re.compile(r"(?i)\.Upload(?:String|File|Data|Values)|-transfertype\s+upload|/upload\b|--upload-file|"
                        r"(?-i:(?:^|\s)-T\s)|-InFile\b")
_FA_EXTRA = (   # LOLBin proxies fetch_sites does not list (it stays unchanged): (api, call head)
    ("rundll32", re.compile(_FS_HEAD + r"rundll32(?:\.exe)?(?=\s[^\n]*(?:https?|ftp)://|\s[^\n]*javascript:)")),
    ("msiexec", re.compile(_FS_HEAD + r"msiexec(?:\.exe)?(?=\s[^\n]*(?:/i|/package)\b[^\n]*(?:https?|ftp)://)")),
)


def _fa_plan_attack(plan):
    try:
        d = _eq_dict(plan) if plan is not None else None
    except Exception:  # noqa: BLE001
        return None
    v = next((d[k] for k in d if str(k).strip().lower() in ("attack", "technique", "mitre", "attack_id")), None) if d \
        else None
    v = str(v).strip() if v is not None else ""
    return v or None


def fetch_attack(api, line="", method="GET", plan=None):
    """Ordered ATT&CK candidates for one fetch call site: fetch_sites' `api` (or a LOLBin name), its source line
    (certutil -decode adds T1140; upload verbs give T1041/T1567 first) and method. A plan's attack= wins and is
    returned alone. [] for an unknown api."""
    pa = _fa_plan_attack(plan)
    if pa:
        return [pa]
    key = next((k for k in FETCH_ATTACK if k.lower() == str(api or "").strip().lower().removesuffix(".exe")), None)
    if key is None:
        return []
    ids = list(FETCH_ATTACK[key][1])
    line = str(line or "")
    upload = bool(_FA_UPVERB.search(line)) or (str(method or "").upper() in ("POST", "PUT") and
                                               ids[0] == "T1105")
    if upload:      # exfil ids lead; a proxy LOLBin keeps its own id first
        ids = list(_FA_UPLOAD) if ids[0] == "T1105" else ids[:1] + list(_FA_UPLOAD)
    if key == "certutil" and _FA_DECODE.search(line):
        ids.insert(ids.index("T1105") + 1 if "T1105" in ids else len(ids), "T1140")
    out = []
    for i in ids:
        if i not in out:
            out.append(i)
    return out


def fetch_adapter(api):
    """Canonical adapter label for a fetch_sites api name (certutil -> 'certutil.exe'); None when unknown."""
    key = next((k for k in FETCH_ATTACK if k.lower() == str(api or "").strip().lower().removesuffix(".exe")), None)
    return FETCH_ATTACK[key][0] if key else None


def fetch_attack_sites(src, name="", plan=None):
    """fetch_sites(src) plus rundll32 / msiexec /i URL proxies, each site with `adapter` and ordered `attack`
    candidates (plan attack= wins). [] for unreadable input or no cradle."""
    try:
        sites = fetch_sites(src, name)
        if isinstance(src, (bytes, bytearray)):
            b = bytes(src)
            src = (b.decode("utf-16", "replace") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else
                   b.decode("utf-8-sig", "replace"))
        text = _fs_flat(str(src or "")[:2_000_000])
        lines = text.split("\n")
        env, starts = None, None
        have = {(d["line"], d["api"]) for d in sites}
        import bisect
        for api, rx in _FA_EXTRA:
            for m in rx.finditer(text):
                if starts is None:
                    starts = [0]
                    for ln in lines:
                        starts.append(starts[-1] + len(ln) + 1)
                lno = bisect.bisect_right(starts, m.start())
                line = lines[lno - 1]
                if _FS_COMMENT.match(line) or (lno, api) in have:
                    continue
                env = _fs_env(text) if env is None else env
                args = _fs_args(text, m.end()) or ""
                url, method = _fs_cmd("mshta" if api == "rundll32" else api, args, env)
                if url is None:
                    url = _fs_url_of(args)
                have.add((lno, api))
                sites.append({"api": api, "url": url, "method": method, "line": lno,
                              "echo": bool(_FS_ECHO.match(line))})
        sites.sort(key=lambda d: d["line"])
        decode = any(re.search(r"(?i)\bcertutil(?:\.exe)?\s", ln) and _FA_DECODE.search(ln) and
                     not _FS_COMMENT.match(ln) for ln in lines)    # download + separate `certutil -decode` step
        for d in sites:
            line = lines[d["line"] - 1] if 0 < d["line"] <= len(lines) else ""
            if d["api"] == "certutil" and decode:
                line += " -decode"
            d["adapter"] = fetch_adapter(d["api"])
            d["attack"] = fetch_attack(d["api"], line, d.get("method"), plan)
        return sites
    except Exception:  # noqa: BLE001
        return []


def fetch_attack_answer(src, plan=None, name=""):
    """Primary ATT&CK id for a member's fetch behaviour: plan attack= first, else the first non-echo site's top
    candidate. None when there is neither."""
    pa = _fa_plan_attack(plan)
    if pa:
        return pa
    for d in fetch_attack_sites(src, name):
        if not d.get("echo") and d.get("attack"):
            return d["attack"][0]
    return None


def _rc_obs_dict(d):
    """One network_indicators()-style record {kind, host, url, uri, ip, port, ...} -> (url value, host value)."""
    low = {_rc_field(k): v for k, v in d.items() if isinstance(v, (str, int))}
    url = low.get("url") or low.get("request_url") or low.get("full_uri")
    host = next((low[k] for k in ("host", "http_host", "hostname", "server_name", "sni", "query", "qry_name",
                                  "dns_qry_name", "queryname", "destinationhostname", "domain") if low.get(k)), None)
    uri = low.get("uri") or low.get("path") or low.get("request_uri")
    if not url and host and uri and str(uri).startswith("/"):
        url = f"http://{host}{uri}"
    if not host and low.get("ip") and not url:
        host = low.get("ip")
    return (str(url) if url else None), (str(host) if host else None)


# --- network evidence -> fetch indicators (pcap / pcapng / HAR / Zeek / Sysmon / proxy & DNS logs) --------------------
_NI_METHODS = r"GET|POST|PUT|HEAD|DELETE|OPTIONS|PATCH|CONNECT|TRACE|PROPFIND"
_NI_REQ = re.compile(rb"(?:^|\n)(" + _NI_METHODS.encode() + rb") (\S{1,4096}) HTTP/\d(?:\.\d)?\r?\n")
_NI_MAX_FLOW = 1 << 18
_NI_BIN_MAGIC = (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d", b"\x0a\x0d\x0d\x0a",
                 b"ElfF")


def _ni_ip(b):
    try:
        import ipaddress
        return str(ipaddress.ip_address(bytes(b)))
    except Exception:  # noqa: BLE001
        return None


def _ni_l3(link, pkt):
    """Link-layer frame -> (ip version, ip packet bytes) or None. Ethernet(+VLAN), NULL/LOOP, raw IP, SLL, SLL2."""
    import struct
    link &= 0xFFFF
    if link == 1:
        if len(pkt) < 14:
            return None
        et, off = struct.unpack(">H", pkt[12:14])[0], 14
        while et in (0x8100, 0x88A8, 0x9100) and len(pkt) >= off + 4:
            et, off = struct.unpack(">H", pkt[off + 2:off + 4])[0], off + 4
        body = pkt[off:]
    elif link in (0, 108):
        if len(pkt) < 4:
            return None
        af = struct.unpack(">I" if link == 108 else "<I", pkt[:4])[0]
        if link == 0 and af > 0xFFFF:
            af = struct.unpack(">I", pkt[:4])[0]
        et, body = (0x0800 if af == 2 else 0x86DD if af in (10, 24, 28, 30) else 0), pkt[4:]
    elif link in (101, 12, 14, 228, 229):
        body = pkt
        et = 0x0800 if body[:1] and body[0] >> 4 == 4 else 0x86DD if body[:1] and body[0] >> 4 == 6 else 0
    elif link == 113:
        if len(pkt) < 16:
            return None
        et, body = struct.unpack(">H", pkt[14:16])[0], pkt[16:]
    elif link == 276:
        if len(pkt) < 20:
            return None
        et, body = struct.unpack(">H", pkt[:2])[0], pkt[20:]
    else:
        return None
    return (4, body) if et == 0x0800 else (6, body) if et == 0x86DD else None


def _ni_l4(ver, ip):
    """IP packet -> (proto, src ip, dst ip, l4 bytes) or None (non-first fragments skipped)."""
    import struct
    if ver == 4:
        if len(ip) < 20 or ip[0] >> 4 != 4:
            return None
        ihl, tot = (ip[0] & 15) * 4, struct.unpack(">H", ip[2:4])[0]
        if struct.unpack(">H", ip[6:8])[0] & 0x1FFF:
            return None
        end = tot if ihl <= tot <= len(ip) else len(ip)
        return ip[9], _ni_ip(ip[12:16]), _ni_ip(ip[16:20]), ip[ihl:end]
    if len(ip) < 40 or ip[0] >> 4 != 6:
        return None
    nh, off, plen = ip[6], 40, struct.unpack(">H", ip[4:6])[0]
    end = 40 + plen if 0 < plen and 40 + plen <= len(ip) else len(ip)
    for _ in range(8):
        if nh not in (0, 43, 60, 44) or len(ip) < off + 8:
            break
        if nh == 44:
            if struct.unpack(">H", ip[off + 2:off + 4])[0] & 0xFFF8:
                return None
            nh, off = ip[off], off + 8
        else:
            nh, off = ip[off], off + (ip[off + 1] + 1) * 8
    return nh, _ni_ip(ip[8:24]), _ni_ip(ip[24:40]), ip[off:end]


def _ni_frames(data):
    """pcap / pcapng bytes -> iterator of (linktype, frame bytes). Truncated tails end the walk quietly."""
    import struct
    m = data[:4]
    if m in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d"):
        e = "<" if m[0] in (0xD4, 0x4D) else ">"
        if len(data) < 24:
            return
        link, off = struct.unpack(e + "I", data[20:24])[0], 24
        while off + 16 <= len(data):
            incl = struct.unpack(e + "I", data[off + 8:off + 12])[0]
            if incl > 0x40000:
                return
            yield link, data[off + 16:off + 16 + incl]
            off += 16 + incl
        return
    if m != b"\x0a\x0d\x0d\x0a":
        return
    off, e, links = 0, "<", []
    while off + 12 <= len(data):
        bt = data[off:off + 4]
        if bt == b"\x0a\x0d\x0d\x0a":
            e = "<" if data[off + 8:off + 12] == b"\x4d\x3c\x2b\x1a" else ">"
            links = []
        btype, blen = struct.unpack(e + "II", data[off:off + 8])
        if blen < 12 or blen % 4 or off + blen > len(data):
            return
        body = data[off + 8:off + blen - 4]
        if btype == 1 and len(body) >= 2:
            links.append(struct.unpack(e + "H", body[:2])[0])
        elif btype == 6 and len(body) >= 20:
            iface, _, _, cap = struct.unpack(e + "IIII", body[:16])
            if iface < len(links):
                yield links[iface], body[20:20 + cap]
        elif btype == 3 and links:
            orig = struct.unpack(e + "I", body[:4])[0]
            yield links[0], body[4:4 + min(orig, len(body) - 4)]
        elif btype == 2 and len(body) >= 20:
            iface, cap = struct.unpack(e + "H", body[:2])[0], struct.unpack(e + "I", body[12:16])[0]
            if iface < len(links):
                yield links[iface], body[20:20 + cap]
        off += blen


def _ni_dns_name(msg, off):
    labels, jumps, end = [], 0, None
    while off < len(msg) and jumps < 32:
        n = msg[off]
        if n == 0:
            off += 1
            break
        if n & 0xC0 == 0xC0:
            if off + 1 >= len(msg):
                return None, len(msg)
            if end is None:
                end = off + 2
            off, jumps = ((n & 0x3F) << 8) | msg[off + 1], jumps + 1
            continue
        labels.append(msg[off + 1:off + 1 + n].decode("latin-1"))
        off += 1 + n
    return ".".join(labels), (end if end is not None else off)


def _ni_dns(msg):
    """DNS message -> [(qname, [answers: A/AAAA ip or CNAME name])]."""
    import struct
    if len(msg) < 12:
        return []
    flags, qd, an = struct.unpack(">HHH", msg[2:8])
    if qd == 0 or qd > 16 or flags & 0x7800:
        return []
    off, qs = 12, []
    for _ in range(qd):
        name, off = _ni_dns_name(msg, off)
        if not name or off + 4 > len(msg):
            return qs and [(q, []) for q in qs]
        qs.append(name)
        off += 4
    ans = []
    for _ in range(min(an, 64) if flags & 0x8000 else 0):
        _, off = _ni_dns_name(msg, off)
        if off + 10 > len(msg):
            break
        typ, _, _, rdl = struct.unpack(">HHIH", msg[off:off + 10])
        rd = msg[off + 10:off + 10 + rdl]
        if typ in (1, 28) and len(rd) in (4, 16):
            ans.append(_ni_ip(rd))
        elif typ == 5:
            ans.append(_ni_dns_name(msg, off + 10)[0])
        off += 10 + rdl
    return [(q, [a for a in ans if a] if i == 0 else []) for i, q in enumerate(qs)]


def _ni_sni(st):
    """TLS byte stream (client side) -> ClientHello server_name, or None."""
    import struct
    hs, off = b"", 0
    while off + 5 <= len(st) and st[off] == 0x16 and st[off + 1] == 3 and len(hs) < 1 << 16:
        n = struct.unpack(">H", st[off + 3:off + 5])[0]
        hs += st[off + 5:off + 5 + n]
        off += 5 + n
    if len(hs) < 42 or hs[0] != 1:
        return None
    p = 4 + 2 + 32
    p += 1 + hs[p]
    p += 2 + struct.unpack(">H", hs[p:p + 2])[0]
    p += 1 + hs[p]
    end = min(len(hs), p + 2 + struct.unpack(">H", hs[p:p + 2])[0])
    p += 2
    while p + 4 <= end:
        t, n = struct.unpack(">HH", hs[p:p + 4])
        if t == 0 and n >= 5:
            ln = struct.unpack(">H", hs[p + 7:p + 9])[0]
            return hs[p + 9:p + 9 + ln].decode("ascii", "replace") or None
        p += 4 + n
    return None


def _ni_http(st, dst, dport, src):
    out, skip = [], 0
    for mm in _NI_REQ.finditer(st):
        if mm.start() < skip:
            continue
        hend = st.find(b"\r\n\r\n", mm.end() - 2)
        hend = st.find(b"\n\n", mm.end() - 1) if hend < 0 else hend
        head = st[mm.end():hend if hend >= 0 else len(st)].decode("latin-1")
        hdr = {}
        for ln in head.splitlines():
            k, sep, v = ln.partition(":")
            if sep:
                hdr.setdefault(k.strip().lower(), v.strip())
        meth, tgt = mm.group(1).decode(), mm.group(2).decode("latin-1")
        host = hdr.get("host") or (f"{dst}:{dport}" if dport != 80 else dst)
        if meth == "CONNECT":
            url, host = None, tgt
        elif re.match(r"(?i)^[a-z][a-z0-9+.\-]*://", tgt):
            url = tgt
        else:
            url = f"http://{host}{tgt if tgt.startswith('/') else '/' + tgt}"
        out.append({"kind": "http", "host": host, "url": url, "ip": dst, "port": dport, "method": meth,
                    "user_agent": hdr.get("user-agent"), "src": src})
        try:
            skip = (hend if hend >= 0 else len(st)) + int(hdr.get("content-length") or 0)
        except ValueError:
            skip = hend
    return out


def _ni_capture(data):
    """pcap / pcapng -> records (TCP SYN conn, HTTP requests, TLS SNI, DNS questions with answers)."""
    out, flows, order, reqs, resps = [], {}, [], {}, {}
    for n, (link, fr) in enumerate(_ni_frames(data)):
        if n > 200000:
            break
        l3 = _ni_l3(link, fr)
        l4 = l3 and _ni_l4(*l3)
        if not l4:
            continue
        proto, s, d, seg = l4
        if proto == 6 and len(seg) >= 20:
            sp, dp = int.from_bytes(seg[0:2], "big"), int.from_bytes(seg[2:4], "big")
            seq, hl, fl = int.from_bytes(seg[4:8], "big"), (seg[12] >> 4) * 4, seg[13]
            if fl & 0x02 and not fl & 0x10:
                out.append({"kind": "conn", "host": None, "url": None, "ip": d, "port": dp, "method": None,
                            "user_agent": None, "src": s})
            pay = seg[hl:]
            k = (s, sp, d, dp)
            if pay:
                if k not in flows:
                    flows[k] = []
                    order.append(k)
                if sum(len(x[1]) for x in flows[k]) < _NI_MAX_FLOW:
                    flows[k].append((seq, bytes(pay)))
        elif proto == 17 and len(seg) >= 8:
            sp, dp = int.from_bytes(seg[0:2], "big"), int.from_bytes(seg[2:4], "big")
            if {sp, dp} & {53, 5353, 5355}:
                srv, cli = (d, s) if dp in (53, 5353, 5355) else (s, d)
                for q, ans in _ni_dns(seg[8:]):
                    out.append({"kind": "dns", "host": q, "url": None, "ip": next((a for a in ans if _ni_ip_ok(a)),
                                None), "port": 53, "method": None, "user_agent": None, "src": cli,
                                "answers": ans, "server": srv})
    for k in order:
        segs, st, cur = sorted(flows[k]), b"", None
        for seq, p in segs:
            if cur is None or seq >= cur:
                st += p
                cur = seq + len(p)
            elif seq + len(p) > cur:
                st += p[cur - seq:]
                cur = seq + len(p)
        s, sp, d, dp = k
        if 53 in (sp, dp):
            off = 0
            while off + 2 <= len(st):
                n = int.from_bytes(st[off:off + 2], "big")
                for q, ans in _ni_dns(st[off + 2:off + 2 + n]):
                    out.append({"kind": "dns", "host": q, "url": None, "ip": next((a for a in ans if _ni_ip_ok(a)),
                                None), "port": 53, "method": None, "user_agent": None,
                                "src": s if dp == 53 else d, "answers": ans})
                off += 2 + n
        elif st[:1] == b"\x16":
            sni = _ni_sni(st)
            if sni:
                out.append({"kind": "tls", "host": sni, "url": None, "ip": d, "port": dp, "method": None,
                            "user_agent": None, "src": s})
        elif st[:5] == b"HTTP/":
            resps[k] = _ni_http_resp(st)
        else:
            reqs[k] = _ni_http(st, d, dp, s)
            out += reqs[k]
    for (s, sp, d, dp), rs in resps.items():   # server -> client stream answers the reverse flow's requests in order
        for rq, (status, loc) in zip(reqs.get((d, dp, s, sp)) or (), rs):
            rq["status"] = status
            loc = _rd_join(rq.get("url"), loc, status)
            if loc:
                rq["location"] = loc
    return out


def _ni_http_resp(st):
    """Server -> client HTTP byte stream -> [(status, Location or None)] in order (bodies skipped by Content-Length)."""
    out, skip = [], 0
    for mm in re.finditer(rb"(?:^|\n)HTTP/\d(?:\.\d)? (\d{3})[^\r\n]*\r?\n", st):
        if mm.start() < skip or len(out) >= 4096:
            continue
        hend = st.find(b"\r\n\r\n", mm.end() - 2)
        hend = st.find(b"\n\n", mm.end() - 1) if hend < 0 else hend
        hdr = {}
        for ln in st[mm.end():hend if hend >= 0 else len(st)].decode("latin-1").splitlines():
            k, sep, v = ln.partition(":")
            if sep:
                hdr.setdefault(k.strip().lower(), v.strip())
        if mm.group(1)[:1] != b"1":   # 1xx interim responses answer no request of their own
            out.append((int(mm.group(1)), hdr.get("location") or None))
        try:
            skip = (hend if hend >= 0 else len(st)) + int(hdr.get("content-length") or 0)
        except ValueError:
            skip = hend
    return out


# --- pcap HTTP objects (Wireshark "Export Objects > HTTP"): reassembled bodies -> name / size / hashes / next stage -----
_HO_MAX_FLOW = 8 << 20
_HO_START = re.compile(rb"(?:^|(?<=\n))(?:(?P<m>" + _NI_METHODS.encode() + rb") (?P<t>\S{1,4096}) HTTP/\d(?:\.\d)?|"
                       rb"HTTP/\d(?:\.\d)? (?P<s>\d{3})[^\r\n]*)\r?\n")


def _ho_streams(data):
    """pcap / pcapng -> {(src, sport, dst, dport): payload} TCP streams, segments ordered by relative seq
    (retransmits / overlaps trimmed, wrap-safe), first-seen flow order."""
    flows, order = {}, []
    for n, (link, fr) in enumerate(_ni_frames(data)):
        if n > 200000:
            break
        l3 = _ni_l3(link, fr)
        l4 = l3 and _ni_l4(*l3)
        if not l4 or l4[0] != 6 or len(l4[3]) < 20:
            continue
        _, s, d, seg = l4
        pay = seg[(seg[12] >> 4) * 4:]
        if not pay:
            continue
        k = (s, int.from_bytes(seg[0:2], "big"), d, int.from_bytes(seg[2:4], "big"))
        if k not in flows:
            flows[k] = [0, []]
            order.append(k)
        f = flows[k]
        if f[0] < _HO_MAX_FLOW:
            f[1].append((int.from_bytes(seg[4:8], "big"), bytes(pay)))
            f[0] += len(pay)
    out = {}
    for k in order:
        segs = flows[k][1]
        base = segs[0][0]
        rel = sorted((((q - base + (1 << 31)) & 0xFFFFFFFF) - (1 << 31), -len(p), p) for q, p in segs)
        st, cur = bytearray(), None
        for q, _, p in rel:
            if cur is None or q >= cur:
                st += p
                cur = q + len(p)
            elif q + len(p) > cur:
                st += p[cur - q:]
                cur = q + len(p)
        out[k] = bytes(st)
    return out


def _ho_dechunk(st, i):
    """chunked transfer-coding at st[i:] -> (body, next offset, complete)."""
    out = bytearray()
    while i < len(st):
        e = st.find(b"\n", i)
        if e < 0:
            break
        try:
            n = int(st[i:e].split(b";")[0].strip(), 16)
        except ValueError:
            return bytes(out), i, False
        i = e + 1
        if n == 0:
            while True:                                  # trailer fields up to the blank line
                e = st.find(b"\n", i)
                if e < 0:
                    return bytes(out), len(st), True
                ln, i = st[i:e].strip(), e + 1
                if not ln:
                    return bytes(out), i, True
        out += st[i:i + n]
        if i + n > len(st):
            return bytes(out), len(st), False
        i += n
        i += 2 if st[i:i + 2] == b"\r\n" else 1 if st[i:i + 1] == b"\n" else 0
    return bytes(out), len(st), False


def _ho_messages(st, methods=None, limit=1024):
    """HTTP/1.x stream -> [(method, target, status, headers, body as transferred (de-chunked), complete)].
    `methods` (the paired request methods, in order) keeps a HEAD response from eating the next message."""
    out, i, mi = [], 0, 0
    while len(out) < limit:
        m = _HO_START.search(st, i)
        if not m:
            break
        hend, sep = st.find(b"\r\n\r\n", m.end() - 2), 4
        if hend < 0:
            hend, sep = st.find(b"\n\n", m.end() - 1), 2
        if hend < 0:
            hend, sep = len(st), 0
        hdr = {}
        for ln in st[m.end():hend].decode("latin-1").splitlines():
            k, c, v = ln.partition(":")
            if c:
                hdr.setdefault(k.strip().lower(), v.strip())
        b0, status = min(hend + sep, len(st)), int(m.group("s")) if m.group("s") else None
        meth = m.group("m").decode() if m.group("m") else None
        if status is not None and status >= 200 and methods is not None:
            meth, mi = (methods[mi] if mi < len(methods) else None), mi + 1
        cl = (hdr.get("content-length") or "").split(",")[0].strip()
        if (status is not None and (status < 200 or status in (204, 304))) or (status and meth == "HEAD"):
            body, nxt, ok = b"", b0, True
        elif "chunked" in (hdr.get("transfer-encoding") or "").lower():
            body, nxt, ok = _ho_dechunk(st, b0)
        elif cl.isdigit():
            body = st[b0:b0 + int(cl)]
            nxt, ok = b0 + len(body), len(body) == int(cl)
        elif status is not None:                         # no length: body runs to connection close
            body, nxt, ok = st[b0:], len(st), True
        else:
            body, nxt, ok = b"", b0, True
        out.append((None if status is not None else meth, m.group("t").decode("latin-1") if m.group("t") else None,
                    status, hdr, body, ok))
        i = max(nxt, m.end())
    return out


def _ho_content_decode(body, enc):
    """Content-Encoding (gzip / x-gzip / deflate / br / zstd, stacked codings undone last-first) -> bytes or None."""
    import zlib
    for c in reversed([x.strip().lower() for x in (enc or "").split(",") if x.strip()]):
        try:
            if c in ("gzip", "x-gzip"):
                body = zlib.decompressobj(31).decompress(body, 1 << 26)
            elif c == "deflate":
                try:
                    body = zlib.decompressobj(15).decompress(body, 1 << 26)
                except zlib.error:
                    body = zlib.decompressobj(-15).decompress(body, 1 << 26)
            elif c == "br":
                import brotli
                body = brotli.decompress(body)
            elif c in ("zstd", "x-zstd"):
                import zstandard
                body = zstandard.ZstdDecompressor().decompressobj().decompress(body)
            elif c not in ("identity", ""):
                return None
        except Exception:  # noqa: BLE001 - truncated / mislabelled coding
            return None
    return body


def http_objects(data, plans=False, budget=0.8):
    """pcap / pcapng bytes -> HTTP objects in capture order, like Wireshark "Export Objects > HTTP" (TCP reassembled
    by seq, de-chunked, Content-Encoding undone): [{direction: response|request, method, uri, url, host, status,
    content_type, content_encoding, file_name (Content-Disposition, else last URI path segment), size, md5, sha1,
    sha256 (of the decoded body), wire_size / wire_sha256 (as transferred, de-chunked), complete, src, dst, port,
    body}]. Responses pair with the reverse flow's requests in order; request bodies (POST/PUT uploads) are objects
    too. plans=True adds `plain` / `codec` for a body that is itself a staged script (find_codecs on the body: the
    fetched next stage). [] for anything that is not a capture."""
    import hashlib
    import time
    from urllib.parse import unquote
    try:
        data = bytes(data or b"")
        if data[:4] not in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d",
                            b"\x0a\x0d\x0d\x0a"):
            return []
        end = time.time() + budget
        streams = _ho_streams(data)
        reqs, out = {}, []
        for k, st in streams.items():
            m = _HO_START.search(st)
            if m and m.group("m"):
                reqs[k] = _ho_messages(st)
        for k, st in streams.items():
            if time.time() > end:
                break
            s, sp, d, dp = k
            if k in reqs:
                rq_list, rs_list, cli, srv, port = reqs[k], [], s, d, dp
                rq_list = [r for r in rq_list if r[4]]
                pairs = [(r, None) for r in rq_list]
            else:
                m = _HO_START.search(st)
                if not m or not m.group("s"):
                    continue
                rq_list = reqs.get((d, dp, s, sp)) or []
                rs_list = _ho_messages(st, [r[0] for r in rq_list])
                cli, srv, port = d, s, sp
                pairs, j = [], 0
                for r in rs_list:
                    if r[2] >= 200:
                        pairs.append((rq_list[j] if j < len(rq_list) else None, r))
                        j += 1
            for rq, rs in pairs:
                msg = rs or rq
                hdr, wire = msg[3], msg[4]
                body = _ho_content_decode(wire, hdr.get("content-encoding"))
                tgt = rq[1] if rq else None
                host = (rq[3].get("host") if rq else None) or (f"{srv}:{port}" if port != 80 else srv)
                if tgt and re.match(r"(?i)^[a-z][a-z0-9+.\-]*://", tgt):
                    url = tgt
                    uri = "/" + tgt.split("://", 1)[1].partition("/")[2]
                else:
                    uri = tgt
                    url = f"http://{host}{tgt if tgt.startswith('/') else '/' + tgt}" if tgt else None
                path = unquote((uri or "").split("?", 1)[0].split("#", 1)[0])
                name = _rc_cd_name(hdr.get("content-disposition")) or (path.rsplit("/", 1)[-1] or None)
                b = body if body is not None else wire
                o = {"direction": "response" if rs else "request", "method": rq[0] if rq else None, "uri": uri,
                     "url": url, "host": host, "status": rs[2] if rs else None,
                     "content_type": (hdr.get("content-type") or "").split(";")[0].strip().lower() or None,
                     "content_encoding": hdr.get("content-encoding"), "file_name": name, "size": len(b),
                     "md5": hashlib.md5(b).hexdigest(), "sha1": hashlib.sha1(b).hexdigest(),
                     "sha256": hashlib.sha256(b).hexdigest(), "wire_size": len(wire),
                     "wire_sha256": hashlib.sha256(wire).hexdigest(), "complete": bool(msg[5] and body is not None),
                     "src": cli, "dst": srv, "port": port, "body": b}
                if plans and b and time.time() < end:
                    for c in find_codecs(b, 1):
                        if c.get("plain"):
                            o["plain"], o["codec"] = c["plain"], {x: c.get(x) for x in ("id", "rep", "transform")}
                            break
                out.append(o)
        return out
    except Exception:  # noqa: BLE001 - impostor / truncated capture: nothing, never an exception
        return []


def _ni_ip_ok(a):
    return bool(a) and bool(re.fullmatch(r"[0-9.]+|[0-9a-fA-F:]*:[0-9a-fA-F:.]*", a))


def _ni_rec(kind, host=None, url=None, ip=None, port=None, method=None, ua=None, src=None, **kw):
    try:
        port = int(port) if port not in (None, "", "-") else None
    except (TypeError, ValueError):
        port = None
    r = {"kind": kind, "host": host or None, "url": url or None, "ip": ip or None, "port": port,
         "method": method or None, "user_agent": ua or None, "src": src or None}
    r.update({k: v for k, v in kw.items() if v})
    return r


def _ni_zeek(row):
    g = lambda *ks: next((row[k] for k in ks if row.get(k) not in (None, "", "-", "(empty)")), None)  # noqa: E731
    ip, port, src = g("id.resp_h", "id_resp_h"), g("id.resp_p", "id_resp_p"), g("id.orig_h", "id_orig_h")
    if g("uri", "method"):
        host, uri = g("host") or ip, g("uri") or "/"
        url = uri if re.match(r"(?i)^https?://", uri) else f"http://{host}{uri}" if host else None
        fn = g("resp_filenames", "orig_filenames")
        fn = ",".join(fn) if isinstance(fn, list) else fn
        return _ni_rec("http", host, url, ip, port, g("method"), g("user_agent"), src, filename=fn,
                       status=g("status_code"), location=_rd_join(url, g("location", "redirect_location",
                                                                         "redirect_url"), g("status_code")))
    if g("query"):
        ans = g("answers")
        ans = ans if isinstance(ans, list) else [a for a in str(ans or "").split(",") if a]
        return _ni_rec("dns", g("query"), None, next((a for a in ans if _ni_ip_ok(a)), None), 53, src=src,
                       answers=ans)
    if g("server_name"):
        return _ni_rec("tls", g("server_name"), None, ip, port, src=src)
    if ip:
        return _ni_rec("conn", None, None, ip, port, src=src)
    return None


def _ni_csv_split(ln, sep):
    if sep == "\t":
        return ln.split("\t")
    return [(q.replace('""', '"') if q is not None and q != "" or a == "" else a).strip()
            for q, a in re.findall(r'(?:^|' + re.escape(sep) + r')\s*(?:"((?:[^"]|"")*)"|([^' + re.escape(sep) +
                                    r']*))', ln)]


def _ni_sysmon(xml):
    out = []
    for ev in re.findall(r"(?s)<Event[\s>].*?</Event>", xml)[:50000]:
        mm = re.search(r"<EventID[^>]*>\s*(\d+)\s*<", ev)
        if not mm or mm.group(1) not in ("3", "22"):
            continue
        import html
        d = {k: html.unescape(v) for k, v in re.findall(r"<Data Name=['\"](\w+)['\"]\s*>([^<]*)</Data>", ev)}
        img = d.get("Image")
        if mm.group(1) == "3":
            out.append(_ni_rec("conn", d.get("DestinationHostname") if d.get("DestinationHostname") not in ("-", "")
                               else None, None, d.get("DestinationIp"), d.get("DestinationPort"), src=d.get("SourceIp"),
                               image=img))
        elif d.get("QueryName"):
            ans = [a.strip() for a in re.sub(r"type:\s*\d+\s*", "", d.get("QueryResults") or "").split(";")
                   if a.strip() and a.strip() != "-"]
            ans = [a[7:] if a.startswith("::ffff:") else a for a in ans]
            out.append(_ni_rec("dns", d["QueryName"], None, next((a for a in ans if _ni_ip_ok(a)), None), 53,
                               answers=ans, image=img))
    return out


def _ni_sysmon_json(rows):
    """Sysmon EID 3 / 22 exported as JSON (flat {EventID, Image, DestinationIp ..}, {System:{EventID}, EventData:{..}},
    xmltodict {Event:{EventData:{Data:[{@Name, #text}]}}}, winlogbeat winlog.event_data, EvtxECmd Payload) -> records;
    None when no row is Sysmon-shaped."""
    def walk(x, d, depth=0):
        if depth > 8:
            return
        if isinstance(x, dict):
            nm = next((x[k] for k in ("@Name", "Name", "name", "@name") if isinstance(x.get(k), str)), None)
            vv = next((x[k] for k in ("#text", "text", "value", "Value", "$") if k in x), None)
            if nm and isinstance(vv, (str, int)):
                d.setdefault(nm, str(vv))
            for k, v in x.items():
                if isinstance(v, str) and k.lower() == "message" and re.search(r"(?m)^\s*(?:Image|QueryName):", v):
                    for mk, mv in re.findall(r"(?m)^\s*(\w+):[ \t]*(.*?)\s*$", v[:65536]):
                        d.setdefault(mk, mv)   # Get-WinEvent | ConvertTo-Json: rendered 'Key: value' lines
                if isinstance(v, (str, int)) and not isinstance(v, bool):
                    d.setdefault(k, str(v))
                    if k.lower() in ("eventid", "event_id", "id", "eventcode"):
                        d.setdefault("EventID", str(v))
                elif k.lower() == "payload" and isinstance(v, str) and v.lstrip()[:1] == "{":
                    try:
                        import json
                        walk(json.loads(v), d, depth + 1)
                    except ValueError:
                        pass
                else:
                    walk(v, d, depth + 1)
        elif isinstance(x, list):
            for v in x[:256]:
                walk(v, d, depth + 1)
    out, hit = [], False
    for row in rows[:50000]:
        d = {}
        walk(row, d)
        low = {re.sub(r"[^a-z]", "", k.lower()): v for k, v in d.items()}
        low = {k: v for k, v in low.items() if v not in ("", "-")} | {k: low[k] for k in ("eventid",) if k in low}
        eid = str(low.get("eventid") or "").strip()
        if not (low.get("destinationip") or low.get("queryname")) or \
                not (eid in ("3", "22") or (not eid and "image" in low)):
            continue
        hit = True
        img = low.get("image")
        if (eid == "3" or not eid) and low.get("destinationip"):
            out.append(_ni_rec("conn", low.get("destinationhostname"), None, low.get("destinationip"),
                               low.get("destinationport"), src=low.get("sourceip"), image=img))
        elif low.get("queryname"):
            ans = [a.strip() for a in re.sub(r"type:\s*\d+\s*", "", low.get("queryresults") or "").split(";")
                   if a.strip() and a.strip() != "-"]
            ans = [a[7:] if a.startswith("::ffff:") else a for a in ans]
            out.append(_ni_rec("dns", low["queryname"], None, next((a for a in ans if _ni_ip_ok(a)), None), 53,
                               answers=ans, image=img))
    return out if hit else None


def _ni_w3c_split(ln):
    return [a if a else q for q, a in re.findall(r'"([^"]*)"|(\S+)', ln)]


def _ni_text(s):
    import json
    st = s.lstrip("﻿").strip()
    if st[:1] in "[{":
        try:
            j = json.loads(st)
            if isinstance(j, dict) and isinstance(j.get("log"), dict):
                out = []
                for e in j["log"].get("entries") or ():
                    rq = (e or {}).get("request") or {}
                    u = rq.get("url")
                    if not u:
                        continue
                    ua = next((h.get("value") for h in rq.get("headers") or () if isinstance(h, dict)
                               and str(h.get("name", "")).lower() == "user-agent"), None)
                    sp = _rc_split(u)
                    rs = (e.get("response") or {}) if isinstance(e.get("response"), dict) else {}
                    cd = next((h.get("value") for h in (rs.get("headers") or ())
                               if isinstance(h, dict) and str(h.get("name", "")).lower() == "content-disposition"), None)
                    loc = rs.get("redirectURL") or next((h.get("value") for h in (rs.get("headers") or ())
                                                         if isinstance(h, dict)
                                                         and str(h.get("name", "")).lower() == "location"), None)
                    out.append(_ni_rec("http", sp[1], u, e.get("serverIPAddress"), sp[2], rq.get("method"), ua,
                                       filename=_rc_cd_name(cd), status=rs.get("status"),
                                       location=_rd_join(u, loc, rs.get("status"))))
                return out
            rows = j if isinstance(j, list) else [j]
            if len(rows) == 1 and isinstance(rows[0], dict):   # {"Events": [...]} / {"records": [...]} wrappers
                inner = next((v for v in rows[0].values() if isinstance(v, list) and v and isinstance(v[0], dict)),
                             None)
                rows = inner if inner and not _ni_zeek(rows[0]) else rows
            sj = _ni_sysmon_json([x for x in rows if isinstance(x, dict)])
            if sj is not None:
                return sj
            return [r for r in (_ni_zeek(x) for x in rows if isinstance(x, dict)) if r]
        except ValueError:
            pass
        if st[:1] == "{":
            rows = []
            for ln in st.splitlines()[:200000]:
                try:
                    x = json.loads(ln)
                except ValueError:
                    continue
                if isinstance(x, dict):
                    rows.append(x)
            if rows:
                sj = _ni_sysmon_json(rows)
                return sj if sj is not None else [r for r in map(_ni_zeek, rows) if r]
    if re.search(r"<EventID[^>]*>\s*(?:3|22)\s*<", s):
        return _ni_sysmon(s)
    lines = s.splitlines()[:200000]
    out, fields, w3c = [], None, None
    for ln in lines:
        if ln.startswith("#fields"):
            fields = ln.split("\t")[1:]
        elif ln.startswith("#Fields:"):
            w3c = ln[8:].split()
        elif fields and ln and not ln.startswith("#"):
            r = _ni_zeek(dict(zip(fields, ln.split("\t"))))
            if r:
                out.append(r)
        elif w3c and ln and not ln.startswith("#"):
            d = {k.lower(): v for k, v in zip(w3c, _ni_w3c_split(ln)) if v != "-"}
            host = d.get("cs-host") or d.get("r-host") or d.get("cs-uri-host") or d.get("s-ip")
            stem, q = d.get("cs-uri-stem") or d.get("cs-uri-path"), d.get("cs-uri-query")
            full = d.get("cs-uri") or d.get("cs-url")
            if full and re.match(r"(?i)^[a-z][\w+.\-]*://", full):
                sp = _rc_split(full)
                out.append(_ni_rec("http", sp[1], full, d.get("r-ip") or d.get("s-ip"), sp[2],
                                   d.get("cs-method"), (d.get("cs(user-agent)") or "").replace("+", " "),
                                   d.get("c-ip")))
            elif host and stem:
                out.append(_ni_rec("http", host, f"http://{host}{stem}" + (f"?{q}" if q and q != "-" else ""),
                                   d.get("s-ip"), d.get("s-port"), d.get("cs-method"),
                                   (d.get("cs(user-agent)") or "").replace("+", " "), d.get("c-ip")))
    if fields or w3c:
        return out
    if lines and re.search(r"(?i)[,\t;](?:\"?)(?:url|uri|request_?url|host|hostname|query|domain|dest\w*|"
                           r"server_?name|sni)(?:\"?)(?:[,\t;]|$)", lines[0]):
        sep = "\t" if "\t" in lines[0] else ";" if lines[0].count(";") > lines[0].count(",") else ","
        hdr = [_rc_field(h) for h in _ni_csv_split(lines[0], sep)]
        for ln in lines[1:]:
            if not ln.strip():
                continue
            d = {k: v for k, v in zip(hdr, _ni_csv_split(ln, sep)) if v not in ("", "-")}
            u, h = _rc_obs_dict(d)
            ip = d.get("dest_ip") or d.get("destination_ip") or d.get("dst_ip") or d.get("ip")
            port = d.get("dest_port") or d.get("destination_port") or d.get("dst_port") or d.get("port")
            kind = "http" if u else "dns" if (d.get("query") or d.get("qry_name")) else "tls" \
                if (d.get("sni") or d.get("server_name")) else "conn" if not h or h == ip else "http"
            if u or h or ip:
                out.append(_ni_rec(kind, h if h != ip else None, u, ip, port, d.get("method"),
                                   d.get("user_agent") or d.get("useragent"), d.get("src_ip") or d.get("client_ip")))
        return out
    for ln in lines:
        mm = re.match(r"^\s*\d{9,}(?:\.\d+)?\s+\d+\s+(\S+)\s+[A-Z_]+/\d{3}\s+\d+\s+([A-Z]+)\s+(\S+)"
                      r"(?:\s+\S+\s+[A-Z_]+/(\S+))?", ln)
        if mm:   # squid native access.log: ts elapsed client code/status bytes METHOD URL [ident hier/peer type]
            meth, tgt = mm.group(2), mm.group(3)
            sp = _rc_split(tgt if "://" in tgt else "https://" + tgt)
            out.append(_ni_rec("http", sp[1], tgt if "://" in tgt else None,
                               mm.group(4) if mm.group(4) and _ni_ip_ok(mm.group(4)) else None, sp[2], meth,
                               src=mm.group(1)))
            continue
        mm = re.search(r"\bquery(?:\[(\w+)\])?:\s+([\w.\-]+)\s+(?:IN\s+\w+|from\s+(\S+))", ln)
        if mm:   # BIND query log / dnsmasq
            out.append(_ni_rec("dns", mm.group(2), None, None, 53, src=mm.group(3)))
            continue
        mm = re.match(r'^(?:(\S+) )?(\S+) \S+ \S+ \[[^\]]+\] "(' + _NI_METHODS + r') (\S+) [^"]*" \d{3} \S+'
                      r'(?: "[^"]*" "([^"]*)")?', ln)
        if mm and "://" in mm.group(4):   # proxy in combined log format with absolute targets
            sp = _rc_split(mm.group(4))
            out.append(_ni_rec("http", sp[1], mm.group(4), None, sp[2], mm.group(3), mm.group(5), mm.group(2)))
        elif mm and mm.group(3) == "CONNECT" and re.fullmatch(r"[\w.\-\[\]:]+:\d{1,5}", mm.group(4)):
            sp = _rc_split("https://" + mm.group(4))   # proxy tunnel: host:port, no URL
            out.append(_ni_rec("tls", sp[1], None, None, sp[2], "CONNECT", mm.group(5), mm.group(2)))
        elif mm and mm.group(1) and mm.group(4).startswith("/"):   # vhost_combined: vhost[:port] client - - [..]
            vh = re.fullmatch(r"([\w.\-]+|\[[0-9a-fA-F:.]+\])(?::(\d{1,5}))?", mm.group(1))
            if vh and "." in vh.group(1) or vh and vh.group(1)[:1] == "[":
                hp = vh.group(1) + (f":{vh.group(2)}" if vh.group(2) and vh.group(2) not in ("80", "443") else "")
                url = ("https" if vh.group(2) == "443" else "http") + f"://{hp}{mm.group(4)}"
                out.append(_ni_rec("http", vh.group(1), url, None, vh.group(2), mm.group(3), mm.group(5),
                                   mm.group(2)))
    if not out:
        for u in _RC_URL.findall(refang(s)):
            u = u.rstrip(".,")
            out.append(_ni_rec("http", _rc_split(u)[1], u))
        for h in re.findall(r"(?im)^\s*host:\s*(\S+)", s):
            out.append(_ni_rec("http", h))
    return out


def _ni_evtx(data):
    try:
        from Evtx.Evtx import FileHeader
        fh, xs, t0 = FileHeader(data, 0), [], time.time()
        for ch in fh.chunks():
            for rec in ch.records():
                x = rec.xml()
                if "<EventID" in x and re.search(r"<EventID[^>]*>\s*(?:3|22)\s*<", x):
                    xs.append(x)
            if time.time() - t0 > 3:
                break
        return _ni_sysmon("\n".join(xs))
    except Exception:  # noqa: BLE001
        return []


def network_indicators(data, name=""):
    """Network evidence -> [{kind: http|dns|tls|conn, host, url, ip, port, method, user_agent, src, ...}] (deduped,
    first-seen order; dns records add `answers`, Sysmon records `image`). Sniffed by magic/shape, not by `name`:
    pcap (D4C3B2A1/A1B2C3D4, ns variants) / pcapng (0A0D0D0A): TCP SYN dst ip:port, reassembled HTTP request lines
    + Host (absolute proxy targets kept), TLS ClientHello SNI, DNS (UDP/TCP 53) qname + A/AAAA/CNAME answers;
    EVTX / Sysmon XML (EID 3 DestinationIp/Port/Hostname, EID 22 QueryName/QueryResults); HAR; Zeek TSV/JSON
    (http/dns/ssl/conn); W3C #Fields; CSV/TSV with url/host/query columns; squid / BIND / dnsmasq / combined proxy
    lines; else free-text URLs and Host: headers. [] when nothing network-shaped is in it. Feed the list straight
    into observed_fetches() / reconcile()."""
    try:
        if isinstance(data, (bytearray, memoryview)):
            data = bytes(data)
        if isinstance(data, bytes):
            data = data[:1 << 26]
            if data[:4] in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d",
                            b"\x0a\x0d\x0d\x0a"):
                recs = _ni_capture(data)
            elif data[:8] == b"ElfFile\x00":
                recs = _ni_evtx(data)
            else:
                if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
                    txt = data.decode("utf-16", "replace")
                elif len(data) > 4 and data[1:4:2] == b"\x00\x00" and data[0]:
                    txt = data.decode("utf-16-le", "replace")
                else:
                    txt = data.decode("utf-8", "replace")
                if txt.count("�") > max(16, len(txt) // 20):
                    return []
                recs = _ni_text(txt)
        elif isinstance(data, str):
            recs = _ni_text(data)
        else:
            return []
        out, seen = [], {}
        for r in recs:
            if not r or not (r.get("host") or r.get("url") or r.get("ip")):
                continue
            key = (r["kind"], r.get("host"), r.get("url"), r.get("method")) if r["kind"] in ("dns", "http", "tls") \
                else (r["kind"], r.get("ip"), r.get("port"), r.get("host"))
            if key in seen:
                old = seen[key]
                for a in r.get("answers") or ():
                    if a not in old.setdefault("answers", []):
                        old["answers"].append(a)
                if not old.get("ip") and r.get("ip"):
                    old["ip"] = r["ip"]
                if not old.get("location") and r.get("location"):
                    old["location"], old["status"] = r["location"], r.get("status")
                continue
            seen[key] = r
            out.append(r)
        return out
    except Exception:  # noqa: BLE001
        return []


def observed_fetches(observed):
    """Network evidence -> [{value, url, host, kind}]. Accepts network_indicators() output (list of dicts), a list
    of URL / host strings, HAR JSON (log.entries[].request.url), Zeek TSV (#fields; host+uri / query / server_name),
    or free text (every URL, then 'Host:' headers). Original spelling kept in `value`."""
    recs = []
    try:
        if isinstance(observed, (bytes, bytearray)) and bytes(observed[:4]) in _NI_BIN_MAGIC:
            observed = network_indicators(observed)   # pcap / pcapng / EVTX: binary evidence, records out
        if isinstance(observed, (bytes, bytearray)):
            observed = bytes(observed[:1 << 24]).decode("utf-8", "replace")
        if isinstance(observed, str) and re.search(r"<EventID[^>]*>\s*(?:3|22)\s*<", observed[:1 << 20]):
            observed = network_indicators(observed)   # Sysmon network-connect / DNS-query XML
        if isinstance(observed, str) and _of_log_shaped(observed):
            observed = network_indicators(observed) or observed   # Sysmon JSON / W3C / squid / combined logs
        if isinstance(observed, str):
            s = observed.lstrip("﻿").strip()
            if s[:1] in "[{":
                try:
                    import json
                    j = json.loads(s)
                    if isinstance(j, dict) and isinstance(j.get("log"), dict):
                        j = [e.get("request") or {} for e in j["log"].get("entries") or () if isinstance(e, dict)]
                    observed = j if isinstance(j, list) else [j]
                except ValueError:
                    pass
        if isinstance(observed, str):
            lines = observed.splitlines()
            fields = None
            for ln in lines:
                if ln.startswith("#fields"):
                    fields = ln.split("\t")[1:]
                elif fields and ln and not ln.startswith("#"):
                    row = dict(zip(fields, ln.split("\t")))
                    row = {k: v for k, v in row.items() if v not in ("-", "(empty)", "")}
                    recs.append((_rc_obs_dict(row), "zeek"))
            if fields is None:
                for u in _RC_URL.findall(refang(observed)):
                    if not u.startswith("http://schemas.microsoft.com/win/2004/08/events/"):   # Event xmlns
                        recs.append(((u.rstrip(".,"), None), "url"))
                for h in re.findall(r"(?im)^\s*host:\s*(\S+)", observed):
                    recs.append(((None, h), "host"))
        if isinstance(observed, (list, tuple)) and observed and all(isinstance(x, dict) and "kind" not in x
                                                                    for x in observed[:64]):
            sj = _ni_sysmon_json(list(observed))   # parsed Sysmon JSON export rows
            observed = sj if sj is not None else observed
        if isinstance(observed, (list, tuple, set)):
            # a bare TCP-connect record to an IP some DNS answer / HTTP / TLS record already names adds no host
            named = {str(a) for x in observed if isinstance(x, dict) and x.get("kind") in ("dns", "http", "tls")
                     for a in list(x.get("answers") or ()) + [x.get("ip")] if a}
            for x in observed:
                if isinstance(x, dict) and x.get("kind") == "conn" and not x.get("host") and str(x.get("ip")) in named:
                    continue
                if isinstance(x, dict):
                    recs.append((_rc_obs_dict(x), str(x.get("kind") or "rec"), x.get("image")))
                elif isinstance(x, str):
                    r = refang(x)
                    recs.append(((x, None) if _RC_URL.fullmatch(r) else (None, x), "str"))
    except Exception:  # noqa: BLE001
        pass
    out = []
    for (u, h), kind, *img in recs:
        cu = canon_url(u) if u else None
        ch = canon_host(u) if cu else canon_host(h) if h else None
        if cu or ch:
            out.append({"value": u if cu else h, "url": cu, "host": ch, "kind": kind})
            if img and img[0]:
                out[-1]["image"] = str(img[0])   # Sysmon Image: the process that fetched
    return out


def _of_log_shaped(s):
    """Text that network_indicators() reads as a log, not prose: Sysmon JSON (EventID 3 / 22 with DestinationIp /
    QueryName), a W3C '#Fields:' header, or >= half of the first lines in squid native / (vhost_)combined shape."""
    head = s[:1 << 16]
    st = head.lstrip("\ufeff").lstrip()
    if st[:1] in "[{" and re.search(r"(?:DestinationIp|QueryName)\b", head) and \
            re.search(r'(?i)"(?:EventID|event_id|Id|EventCode)"\s*:\s*"?(?:3|22)\b', head):
        return True
    if re.search(r"(?m)^#Fields:", head):
        return True
    lines = [ln for ln in head.splitlines()[:40] if ln.strip() and not ln.startswith("#")]
    if not lines:
        return False
    pat = re.compile(r'^\s*\d{9,}(?:\.\d+)?\s+\d+\s+\S+\s+[A-Z_]+/\d{3}\s+\d+\s+[A-Z]+\s+\S+|'
                     r'^(?:\S+ )?\S+ \S+ \S+ \[[^\]]+\] "(?:' + _NI_METHODS + r') \S+ [^"]*" \d{3} ')
    return sum(1 for ln in lines if pat.match(ln)) * 2 >= len(lines)


def fetch_processes(observed):
    """Network evidence -> {observed value: process image} for Sysmon EID 3 / 22 records (first image seen per value),
    so an 'only one side' answer can name the process that fetched. {} when the evidence carries no Image."""
    out = {}
    for x in observed_fetches(observed):
        if x.get("image"):
            out.setdefault(x["value"], x["image"])
    return out


# Target process-telemetry-windows (D18 'native telemetry keeps its own record of events'): process start / end
# records from Sysmon EID 1 / 5 and Security 4688 / 4689, read from EVTX, exported XML, JSON (flat, xmltodict,
# winlogbeat / ECS, EvtxECmd Payload, Get-WinEvent Message) or Splunk-style key=value / rendered 'Key: value' text.
_PE_EIDS = {"1": "start", "4688": "start", "5": "end", "4689": "end"}
_PE_ECS = ("process", "user", "event", "host", "agent", "ecs", "winlog", "log", "@timestamp", "_source")
_PE_DATA = ("eventdata", "event_data", "system", "userdata", "payload", "data", "eventdatafields", "properties")
_PE_HINT = re.compile(r"(?im)<EventID[^>]*>\s*(?:1|5|4688|4689)\s*<|\bEvent(?:ID|Code|_id)\W{0,4}(?:1|5|4688|4689)\b|"
                      r"\bevent\.code\W{0,4}(?:1|5|4688|4689)\b|process\.(?:pid|command_line|entity_id)|"
                      r"\"command_line\"|New[ _]Process[ _](?:ID|Name)|Creator[ _]Process[ _]ID|NewProcessId\b|"
                      r"ParentProcess(?:Guid|Id)\b|ProcessGuid\b|^\s*Process Create:|ProcessName\b")


def _pe_int(v):
    s = str(v if v is not None else "").strip()
    try:
        return int(s, 16) if re.fullmatch(r"0[xX][0-9a-fA-F]+", s) else int(s) if re.fullmatch(r"\d+", s) else None
    except ValueError:
        return None


def _pe_norm(k):
    return re.sub(r"[^a-z]", "", str(k).lower())


def _pe_build(d, flat):
    """One record from `d` (event-data names, letters-only lowercase keys) + `flat` (dotted ECS paths), else None."""
    g = lambda *ks: next((d[k] for k in ks if d.get(k) not in (None, "", "-")), None)  # noqa: E731
    f = lambda *ks: next((flat[k] for k in ks if flat.get(k) not in (None, "", "-")), None)  # noqa: E731
    eid = str(g("eventid", "eventcode", "id") or f("winlog.event_id", "event.code") or "").strip()
    if eid not in _PE_EIDS:
        eid = "4688" if g("newprocessid") else "1" if g("parentprocessguid", "parentprocessid") else ""
    sec = eid in ("4688", "4689")
    if eid == "4688":
        pid, ppid = g("newprocessid"), g("processid", "creatorprocessid")
        image, pimage = g("newprocessname"), g("parentprocessname", "creatorprocessname")
        cmd = g("commandline", "processcommandline")
    elif eid == "4689":
        pid, ppid, image, pimage, cmd = g("processid"), None, g("processname"), None, None
    else:
        pid, ppid, image, pimage = g("processid"), g("parentprocessid"), g("image"), g("parentimage")
        cmd = g("commandline")
    ev = _PE_EIDS.get(eid)
    if not ev:
        typ = " ".join(str(x) for x in (f("event.type"), f("event.action")) if x).lower()
        ev = "start" if re.search(r"start|creat|exec|spawn", typ) else "end" if re.search(r"end|stop|termin|exit",
                                                                                          typ) else None
        ev = ev or ("start" if not typ and f("process.pid") and f("process.parent.pid") else None)
    if not ev:
        return None
    pid = pid if pid is not None else f("process.pid")
    if ppid is None and ev == "start":
        ppid = f("process.parent.pid", "process.ppid")
    if pid is None and not image:
        return None
    user = g("user") if not sec else None
    if sec and not user:
        un = g("subjectusername", "accountname")
        dom = g("subjectdomainname", "accountdomain")
        user = f"{dom}\\{un}" if un and dom else un
    hashes = g("hashes") or ",".join(f"{k.split('.')[-1].upper()}={v}" for k, v in flat.items()
                                     if k.startswith("process.hash.") and v not in (None, "")) or None
    return {"ts": g("utctime", "systemtime", "timecreated", "time") or f("@timestamp", "event.created", "timestamp"),
            "pid": _pe_int(pid), "ppid": _pe_int(ppid), "pid_raw": None if pid is None else str(pid),
            "ppid_raw": None if ppid is None else str(ppid),
            "image": image or f("process.executable"), "cmdline": cmd or f("process.command_line"),
            "parent_image": pimage or f("process.parent.executable"),
            "parent_cmdline": g("parentcommandline") or f("process.parent.command_line"),
            "guid": g("processguid") or f("process.entity_id"),
            "parent_guid": g("parentprocessguid") or f("process.parent.entity_id"),
            "user": user or f("user.name"), "integrity": g("integritylevel", "mandatorylabel"),
            "hashes": hashes, "event": ev, "eid": int(eid) if eid else None,
            "src": "security" if sec else "sysmon" if eid else "ecs", **_pe_creator(g, sec)}


def _pe_creator(g, sec):
    """Explicit real-creator fields on a non-4688 record (CreatorProcessId / CreatorProcessGuid / RealParent..):
    {creator_pid, creator_pid_raw, creator_guid, creator_image}, only the keys present ({} for ordinary records)."""
    if sec:
        return {}
    out = {}
    c = g("creatorprocessid", "realparentprocessid", "actualparentprocessid", "trueparentprocessid",
          "callerprocessid", "creatorpid")
    if c is not None and _pe_int(c) is not None:
        out["creator_pid"], out["creator_pid_raw"] = _pe_int(c), str(c)
    c = g("creatorprocessguid", "realparentprocessguid", "actualparentprocessguid")
    if c:
        out["creator_guid"] = c
    c = g("creatorprocessname", "creatorimage", "realparentimage", "actualparentimage", "realparentprocessname")
    if c:
        out["creator_image"] = c
    return out


def _pe_xml(xml):
    import html
    out = []
    for e in re.findall(r"(?s)<Event[\s>].*?</Event>", xml)[:50000]:
        mm = re.search(r"<EventID[^>]*>\s*(\d+)\s*<", e)
        if not mm or mm.group(1) not in _PE_EIDS:
            continue
        d = {_pe_norm(k): html.unescape(a or b) for k, a, b in
             re.findall(r"<Data Name=['\"](\w+)['\"]\s*(?:/>()|>([^<]*)</Data>)", e)}
        d["eventid"] = mm.group(1)
        t = re.search(r"<TimeCreated[^>]*SystemTime=['\"]([^'\"]+)", e)
        if t:
            d["systemtime"] = t.group(1)
        r = _pe_build(d, {})
        if r:
            out.append(r)
    return out


def _pe_json_row(row):
    if isinstance(row.get("_source"), dict):
        row = row["_source"]
    d, flat = {}, {}

    def walk(x, path, keep, depth=0):
        if depth > 10:
            return
        if isinstance(x, dict):
            nm = next((x[k] for k in ("@Name", "Name", "name", "@name") if isinstance(x.get(k), str)), None)
            vv = next((x[k] for k in ("#text", "text", "value", "Value", "$") if k in x), None)
            if nm and isinstance(vv, (str, int)) and not isinstance(vv, bool):
                d.setdefault(_pe_norm(nm), str(vv))
            for k, v in x.items():
                p = f"{path}.{k}" if path else str(k)
                if k in ("#text", "$") and isinstance(v, (str, int)) and path:
                    flat.setdefault(path.lower(), v)
                    if keep:
                        d.setdefault(_pe_norm(path.split(".")[-1]), str(v))
                    continue
                kp = keep or not path and str(k).split(".")[0].lower() not in _PE_ECS or k.lower() in _PE_DATA
                if isinstance(v, str) and k.lower() == "message" and re.search(
                        r"(?m)^\s*(?:Image|CommandLine|New Process ID|Process ID|ProcessId):", v):
                    for mk, mv in re.findall(r"(?m)^\s*([A-Za-z][\w ]*?):[ \t]*(.*?)\s*$", v[:65536]):
                        if mv:
                            d.setdefault(_pe_norm(mk), mv)
                if k.lower() == "payload" and isinstance(v, str) and v.lstrip()[:1] == "{":
                    try:   # EvtxECmd: the event XML as a JSON string
                        import json
                        walk(json.loads(v), p, True, depth + 1)
                    except ValueError:
                        pass
                elif isinstance(v, (str, int)) and not isinstance(v, bool):
                    flat.setdefault(p.lower(), v)
                    if kp:
                        d.setdefault(_pe_norm(k), str(v))
                elif isinstance(v, (dict, list)):
                    walk(v, p, kp, depth + 1)
        elif isinstance(x, list):
            for v in x[:256]:
                walk(v, path, keep, depth + 1)
    walk(row, "", False)
    return _pe_build(d, flat)


def _pe_kv(text):
    """Splunk-style `k=v` / `k="v"` events and rendered 'Key: value' blocks: a new record at each EventCode/EventID."""
    recs, cur = [], {}
    kv = re.compile(r"""(?<![\w.])([A-Za-z_][\w.]*)=(?:"((?:[^"\\]|\\.)*)"|'([^']*)'|(\S+))""")
    for ln in text.splitlines()[:200000]:
        pairs = [(k, a if a or b or c else "", b, c) for k, a, b, c in kv.findall(ln)]
        dt = None if pairs else \
            re.match(r"^\s*(\d{1,4}[/-]\d{1,2}[/-]\d{1,4}[ T]\d{1,2}:\d{2}:\d{2}(?:\.\d+)?(?: ?[AP]M)?)\s*$", ln)
        if dt:                          # Splunk classic WinEventLog header line: a new event starts here
            if cur.get("eventid"):
                recs.append(cur)
            cur = {"time": dt.group(1)}
            continue
        rend = None if pairs else re.match(r"^\s*([A-Za-z][\w ]*?):[ \t]+(\S.*?)\s*$", ln)
        items = [(k, (a.replace('\\"', '"') if a else b or c)) for k, a, b, c in pairs] if pairs else \
            [(rend.group(1), rend.group(2))] if rend else []
        if pairs and cur.get("eventid") and any(_pe_norm(k) in ("eventcode", "eventid") for k, *_ in pairs):
            recs.append(cur)    # one k=v event per line: `_time=.. host=..` before EventCode belong to this one
            cur = {}
        for k, v in items:
            nk = _pe_norm(k)
            if nk in ("eventcode", "eventid") and cur.get("eventid"):
                recs.append(cur)
                cur = {}
            if nk in ("eventcode", "eventid"):
                nk = "eventid"
            cur.setdefault(nk, v)
    if cur:
        recs.append(cur)
    out = []
    for d in recs:
        r = _pe_build(d, {}) if d.get("eventid") in _PE_EIDS else None
        if r:
            out.append(r)
    return out


def _pe_evtx(data, budget=2.0):
    try:
        from Evtx.Evtx import FileHeader
        fh, xs, t0 = FileHeader(data, 0), [], time.time()
        for ch in fh.chunks():
            for rec in ch.records():
                try:
                    x = rec.xml()
                except Exception:  # noqa: BLE001 - one damaged record
                    continue
                if re.search(r"<EventID[^>]*>\s*(?:1|5|4688|4689)\s*<", x):
                    xs.append(x)
            if time.time() - t0 > budget:
                break
        return _pe_xml("\n".join(xs))
    except Exception:  # noqa: BLE001
        return []


# Target process-telemetry-linux-text: the same record shape from Linux-side process telemetry -- auditd (SYSCALL
# execve + EXECVE argv (hex-encoded when quoted args would break) + PROCTITLE (hex, NUL-joined) grouped by
# msg=audit(ts:serial)), `ps -ef` / `ps -eo pid,ppid,cmd` / `ps auxf` (`\_` forest indentation = parent), `pstree -p`
# / `pstree -ap`, osquery process_events / processes JSON and Procmon CSV `Process Create` / `Process Start` rows.
# (Sysmon-for-Linux XML is the Windows EID 1 / 5 shape and reads through _pe_xml.)
_PL_HINT = re.compile(r"(?im)\btype=(?:SYSCALL|EXECVE|PROCTITLE|130[09]|1327)\s+(?:msg=)?audit\(|"
                      r"^\s*(?:(?:UID|USER)\s+)?PID\s+(?:PPID|%CPU)\s|^\s*PID\s+PPID\b|"
                      r"\w\(\d+(?:,\w+)?\)(?:---|-\+-|───|─┬─)|^\s*\S+?,\d+(?:\s|$)|"
                      r"\"parent\"\s*:\s*\"?-?\d+|\"Process (?:Create|Start)\"\s*,")
_PL_AU_TYPES = {"1300": "SYSCALL", "1309": "EXECVE", "1327": "PROCTITLE", "1307": "CWD", "1302": "PATH"}
_PL_EXEC_NR = {"59", "322", "11", "358", "221", "281", "execve", "execveat"}


def _pl_rec(**kw):
    pid, ppid = kw.pop("pid", None), kw.pop("ppid", None)
    r = {"ts": None, "pid": _pe_int(pid), "ppid": _pe_int(ppid), "pid_raw": None if pid is None else str(pid),
         "ppid_raw": None if ppid is None else str(ppid), "image": None, "cmdline": None, "parent_image": None,
         "parent_cmdline": None, "guid": None, "parent_guid": None, "user": None, "integrity": None, "hashes": None,
         "event": "start", "eid": None, "src": None}
    r.update(kw)
    return r


def _pl_auval(v, interp):
    """auditd field value: "quoted" -> as is; raw-mode unquoted even-length hex -> its bytes (NULs -> spaces)."""
    if v[:1] == '"' and v[-1:] == '"' and len(v) >= 2:
        return v[1:-1]
    if not interp and re.fullmatch(r"(?:[0-9A-Fa-f]{2})+", v or ""):
        return bytes.fromhex(v).decode("utf-8", "replace")
    return None if v == "(null)" else v


def _pl_auditd(txt):
    kv = re.compile(r"""([\w\[\]]+)=("[^"]*"|'[^']*'|\S+)""")
    grp, order = {}, []
    for ln in txt.splitlines()[:400000]:
        m = re.search(r"\btype=(\w+)\s+(?:msg=)?audit\(([^)]*)\)\s*:?\s*(.*)", ln.split("\x1d")[0])
        if not m:
            continue
        typ = _PL_AU_TYPES.get(m.group(1), m.group(1).upper())
        if typ not in ("SYSCALL", "EXECVE", "PROCTITLE", "CWD", "PATH"):
            continue
        stamp = m.group(2)
        g = grp.get(stamp)
        if g is None:
            g = grp[stamp] = {"interp": bool(re.search(r"[/ ]", stamp)) or ") : " in ln}
            order.append(stamp)
        f = {}
        for k, v in kv.findall(m.group(3)):
            f.setdefault(k, v)
        if typ == "PATH" and f.get("item") not in (None, "0"):
            continue
        g.setdefault(typ, f)
    out = []
    for stamp in order[:100000]:
        g, ip = grp[stamp], grp[stamp]["interp"]
        sc, ex = g.get("SYSCALL") or {}, g.get("EXECVE")
        if not ex and str(sc.get("syscall", "")).lower() not in _PL_EXEC_NR:
            continue
        if sc.get("success") == "no":
            continue
        args = []
        if ex:
            n = _pe_int(ex.get("argc")) or 0
            for i in range(min(n or 4096, 4096)):
                if f"a{i}" in ex:
                    args.append(_pl_auval(ex[f"a{i}"], ip) or "")
                elif f"a{i}[0]" in ex:   # long argument: a2_len=N a2[0]=hex a2[1]=hex ...
                    parts, j = [], 0
                    while f"a{i}[{j}]" in ex:
                        parts.append(ex[f"a{i}[{j}]"].strip('"'))
                        j += 1
                    s = "".join(parts)
                    args.append(bytes.fromhex(s).decode("utf-8", "replace")
                                if not ip and re.fullmatch(r"(?:[0-9A-Fa-f]{2})+", s) else s)
                elif not n:
                    break
        cmd = " ".join(args) if args else None
        pt = (g.get("PROCTITLE") or {}).get("proctitle")
        if not cmd and pt:
            cmd = pt.strip('"') if pt[:1] == '"' or ip else \
                bytes.fromhex(pt).replace(b"\x00", b" ").decode("utf-8", "replace").strip() \
                if re.fullmatch(r"(?:[0-9A-Fa-f]{2})+", pt) else pt
        image = _pl_auval(sc["exe"], ip) if sc.get("exe") else None
        if not image and g.get("PATH", {}).get("name"):
            image = _pl_auval(g["PATH"]["name"], ip)
        ts = stamp.rsplit(":", 1)[0]
        cwd = _pl_auval(g["CWD"]["cwd"], ip) if g.get("CWD", {}).get("cwd") else None
        out.append(_pl_rec(pid=sc.get("pid"), ppid=sc.get("ppid"), ts=ts, image=image or (args[0] if args else None),
                           cmdline=cmd, user=sc.get("UID", "").strip('"') or sc.get("uid"), src="auditd",
                           args=args, cwd=cwd, serial=stamp.rsplit(":", 1)[-1], auid=sc.get("auid"),
                           comm=_pl_auval(sc["comm"], ip) if sc.get("comm") else None))
    return out


def _pl_ps(txt):
    lines = txt.splitlines()[:400000]
    hi = next((i for i, ln in enumerate(lines[:2000]) if re.match(r"^\s*(?:[A-Z%]+\s+)*PID\s+(?:[A-Z%]+\s+)*"
                                                                 r"(?:CMD|COMMAND|ARGS|COMM)\s*$", ln)), None)
    if hi is None:
        return []
    cols = lines[hi].split()
    n, last = len(cols), cols[-1]
    ix = {c: i for i, c in enumerate(cols)}
    row = re.compile(r"^(\s*\S+(?:\s+\S+){%d})(.*)$" % (n - 2)) if n >= 2 else None
    out, stack = [], []
    for ln in lines[hi + 1:]:
        if not ln.strip():
            continue
        m = row.match(ln) if row else None
        if not m:
            if out and re.match(r"^\s*(?:[A-Z%]+\s+)*PID\s", ln):
                continue
            break
        fs, rest = m.group(1).split(), m.group(2)
        if _pe_int(fs[ix["PID"]]) is None:
            break
        fm = re.match(r"^(\s*(?:[|│]\s*)*)\\_\s?", rest)
        cmd = rest[fm.end():].strip() if fm else rest.strip()
        ind = len(m.group(1)) + fm.end() if fm else -1
        while stack and stack[-1][0] >= ind:
            stack.pop()
        ppid = fs[ix["PPID"]] if "PPID" in ix else (stack[-1][1] if stack and fm else None)
        stack.append((ind, fs[ix["PID"]]))
        user = fs[ix["UID"]] if "UID" in ix else fs[ix["USER"]] if "USER" in ix else None
        tok = cmd.split()[0] if cmd.split() else None
        ts = fs[ix[k]] if (k := next((k for k in ("STIME", "START", "STARTED") if k in ix), None)) else None
        out.append(_pl_rec(pid=fs[ix["PID"]], ppid=ppid, ts=ts, image=tok if last != "COMM" else cmd,
                           cmdline=cmd if last != "COMM" else None, user=user, src="ps"))
    return out


_PL_TREE_NODE = re.compile(r"(\{[^{}()\n]*\}|[^\s()|`+\-─┬┴├└│{}][^\s()]*?)\((\d+)(?:,([\w.\-]+))?\)")


def _pl_pstree(txt):
    out, branch = [], {}
    lines = txt.splitlines()[:200000]
    if not any(_PL_TREE_NODE.search(ln) for ln in lines[:50]):
        return _pl_pstree_a(lines)
    for ln in lines:
        prev, pend = None, 0
        for m in _PL_TREE_NODE.finditer(ln):
            gap = ln[pend:m.start()]
            if prev is not None and re.search(r"[-─+┬]", gap):
                parent = prev
            else:
                bc = max(ln.rfind(c, 0, m.start()) for c in "|`├└│")
                parent = branch.get(bc) if bc >= 0 else None
                if prev is not None and parent is None:
                    break
            if prev is None and gap.strip() and not re.fullmatch(r"[\s|`\-─├└│+┬]*", gap):
                break
            nm = m.group(1)
            out.append(_pl_rec(pid=m.group(2), ppid=parent, image=nm, user=m.group(3), src="pstree"))
            nxt = ln[m.end():m.end() + 3]
            for c in ("+", "┬"):
                if c in nxt:
                    branch[m.end() + nxt.index(c)] = m.group(2)
            prev, pend = m.group(2), m.end()
    return out


def _pl_pstree_a(lines):
    """`pstree -ap`: one `name,pid args` per line, indentation = depth."""
    out, stack = [], []
    for ln in lines:
        m = re.match(r"^([\s|`│├└\-─]*)(\{?[^\s,(){}]+\}?),(\d+)(?:,[\w.\-]+)?(?:\s+(.*))?$", ln)
        if not m:
            continue
        ind = len(m.group(1))
        while stack and stack[-1][0] >= ind:
            stack.pop()
        out.append(_pl_rec(pid=m.group(3), ppid=stack[-1][1] if stack else None, image=m.group(2),
                           cmdline=(m.group(2) + " " + m.group(4)) if m.group(4) else m.group(2), src="pstree"))
        stack.append((ind, m.group(3)))
    return out if len(out) >= 2 else []


def _pl_osq_row(x):
    c = x.get("columns") if isinstance(x.get("columns"), dict) else x
    if not isinstance(c, dict) or "pid" not in c or not ({"parent", "ppid"} & set(c)) or \
            not ({"cmdline", "path", "name"} & set(c)):
        return None
    act = str(x.get("action") or "added").lower()
    ts = c.get("time") or x.get("unixTime") or x.get("calendarTime")
    return _pl_rec(pid=c.get("pid"), ppid=c.get("parent", c.get("ppid")), ts=None if ts is None else str(ts),
                   image=c.get("path") or c.get("name"), cmdline=c.get("cmdline") or None,
                   user=c.get("username") or (None if c.get("uid") is None else str(c.get("uid"))),
                   event="end" if act == "removed" else "start", src="osquery", cwd=c.get("cwd"))


def _pl_osquery(txt):
    import json
    try:
        j = json.loads(txt)
        rows = j if isinstance(j, list) else [j]
    except ValueError:
        rows = []
        for ln in txt.splitlines()[:200000]:
            try:
                rows.append(json.loads(ln))
            except ValueError:
                continue
    flat = []
    for x in rows[:200000]:
        if isinstance(x, dict) and isinstance(x.get("snapshot"), list):
            flat += [dict(y, unixTime=x.get("unixTime")) for y in x["snapshot"] if isinstance(y, dict)]
        elif isinstance(x, dict) and isinstance(x.get("diffResults"), dict):
            for a in ("added", "removed"):
                flat += [{"columns": y, "action": a} for y in x["diffResults"].get(a) or [] if isinstance(y, dict)]
        elif isinstance(x, dict):
            flat.append(x)
    return [r for r in (_pl_osq_row(x) for x in flat) if r]


_PL_CSV_FIELD = re.compile(r'\s*(?:"((?:[^"]|"")*)"|([^,]*))\s*(,|$)')


def _pl_csv_split(ln):
    out, pos = [], 0
    while pos <= len(ln):
        m = _PL_CSV_FIELD.match(ln, pos)
        if not m:
            return out
        out.append(m.group(1).replace('""', '"') if m.group(1) is not None else m.group(2))
        if not m.group(3):
            break
        pos = m.end()
    return out


def _pl_procmon(txt):
    lines = txt.lstrip("﻿").splitlines()[:400000]
    hdr = _pl_csv_split(lines[0]) if lines else []
    ix = {_pe_norm(h): i for i, h in enumerate(hdr)}
    if not {"operation", "pid", "detail"} <= set(ix):
        return []
    col = lambda r, k: r[ix[k]] if k in ix and ix[k] < len(r) else None  # noqa: E731
    creates, starts, ends = [], {}, []
    for ln in lines[1:]:
        r = _pl_csv_split(ln)
        op, det = (col(r, "operation") or "").strip(), col(r, "detail") or ""
        ts = col(r, "timeofday") or col(r, "datetime") or col(r, "time")
        if op == "Process Create":
            m = re.match(r"\s*PID:\s*(\d+),\s*Command line:\s?(.*)$", det, re.S)
            if m:
                creates.append(_pl_rec(pid=m.group(1), ppid=col(r, "pid"), ts=ts, image=col(r, "path"),
                                       cmdline=m.group(2) or None, parent_image=col(r, "imagepath") or
                                       col(r, "processname"), user=None, src="procmon"))
        elif op == "Process Start":
            m = re.match(r"\s*Parent PID:\s*(\d+)(?:,\s*Command line:\s?(.*?))?(?:,\s*Current directory:.*)?$",
                         det, re.S)
            if m:
                starts.setdefault(col(r, "pid"), _pl_rec(
                    pid=col(r, "pid"), ppid=m.group(1), ts=ts, image=col(r, "imagepath") or col(r, "processname"),
                    cmdline=m.group(2) or col(r, "commandline") or None, user=col(r, "user"), src="procmon"))
        elif op == "Process Exit":
            ends.append(_pl_rec(pid=col(r, "pid"), ts=ts, image=col(r, "imagepath") or col(r, "processname"),
                                event="end", src="procmon"))
    seen = {r["pid_raw"] for r in creates}
    return creates + [r for k, r in starts.items() if k not in seen] + ends


def _pl_events(txt):
    """Linux-side / Procmon process telemetry text -> process_events() records (+ src auditd|ps|pstree|osquery|
    procmon; auditd adds args / cwd / serial / auid / comm). [] when nothing reads."""
    head = txt[:1 << 20]
    if not _PL_HINT.search(head):
        return []
    out = []
    if re.search(r"\btype=(?:SYSCALL|EXECVE|PROCTITLE|130[09]|1327)\s+(?:msg=)?audit\(", head):
        out = _pl_auditd(txt)
    if not out and head.lstrip()[:1] in "[{":
        out = _pl_osquery(txt)
    if not out and re.search(r"\"?Operation\"?\s*,", head[:4096]):
        out = _pl_procmon(txt)
    if not out and re.search(r"(?m)^\s*(?:[A-Z%]+\s+)*PID\s", head):
        out = _pl_ps(txt)
    if not out:
        out = _pl_pstree(txt)
    by = {}
    for r in out:   # parent image / command line from the latest earlier start of the parent pid
        if r["event"] == "start" and r["ppid"] is not None and r["ppid"] in by:
            p = by[r["ppid"]]
            r["parent_image"] = r["parent_image"] or p["image"]
            r["parent_cmdline"] = r["parent_cmdline"] or p["cmdline"]
        if r["event"] == "start" and r["pid"] is not None:
            by[r["pid"]] = r
    return out


def process_events(data, name=""):
    """Process telemetry -> [{ts, pid, ppid, pid_raw, ppid_raw, image, cmdline, parent_image, parent_cmdline, guid,
    parent_guid, user, integrity, hashes, event: start|end, eid, src: sysmon|security|ecs}] in record order.
    Sysmon EID 1 (ProcessId / ParentProcessId / ProcessGuid / ParentProcessGuid / Image / ParentImage / CommandLine /
    ParentCommandLine / User / IntegrityLevel / Hashes / UtcTime), EID 5 (terminate); Security 4688 (NewProcessId =
    the new pid, ProcessId = the CREATOR pid, both hex; NewProcessName, ParentProcessName, CommandLine,
    MandatoryLabel) and 4689 (ProcessId, ProcessName). Inputs: EVTX bytes, exported XML, JSON / NDJSON (flat,
    xmltodict, winlogbeat winlog.event_data, ECS process.pid / process.parent.pid / process.entity_id, EvtxECmd
    Payload, Get-WinEvent Message), Splunk k=v or rendered 'Key: value' text. Hex pids ('0x1a2c') -> int in pid /
    ppid, the original spelling kept in pid_raw / ppid_raw (answer with that). [] when nothing process-shaped."""
    try:
        if isinstance(data, (bytearray, memoryview)):
            data = bytes(data)
        if isinstance(data, bytes):
            data = data[:1 << 26]
            if data[:8] == b"ElfFile\x00":
                return _pe_evtx(data)
            if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
                txt = data.decode("utf-16", "replace")
            elif len(data) > 4 and data[1:4:2] == b"\x00\x00" and data[0]:
                txt = data.decode("utf-16-le", "replace")
            else:
                txt = data.decode("utf-8", "replace")
        elif isinstance(data, str):
            txt = data
        else:
            return []
        st = txt.lstrip("﻿").strip()
        return _pe_text(st) or _pl_events(st)
    except Exception:  # noqa: BLE001 - impostor / truncated log: nothing, never an exception
        return []


def _pe_text(st):
    try:
        if not _PE_HINT.search(st[:1 << 20]):
            return []
        if re.search(r"<EventID[^>]*>", st[:1 << 20]):
            return _pe_xml(st)
        if st[:1] in "[{":
            import json
            try:
                j = json.loads(st)
                rows = j if isinstance(j, list) else [j]
                if len(rows) == 1 and isinstance(rows[0], dict) and not _pe_json_row(rows[0]):
                    inner = next((v for v in rows[0].values() if isinstance(v, list) and v and isinstance(v[0], dict)),
                                 None)
                    if inner is None and isinstance((rows[0].get("hits") or {}).get("hits"), list):
                        inner = rows[0]["hits"]["hits"]
                    rows = inner or rows
            except ValueError:
                rows = []
                for ln in st.splitlines()[:200000]:
                    try:
                        x = json.loads(ln)
                    except ValueError:
                        continue
                    rows.append(x)
            return [r for r in (_pe_json_row(x) for x in rows[:50000] if isinstance(x, dict)) if r]
        return _pe_kv(st)
    except Exception:  # noqa: BLE001 - impostor / truncated log: nothing, never an exception
        return []


def process_tree(events, pid=None):
    """Observed process tree from process_events() records (or the raw log). With `pid` (int or '0x..'): the legacy
    ancestry list [record, parent, ...]. Without: {nodes: {key: node}, edges: [(parent_key, child_key)], roots,
    orphans, leaves, children: {key: [child keys]}, parent: {key: parent_key|None}, depth: {key: int, root = 0},
    max_depth, chains: {leaf: [root..leaf]}, order: [keys by start]}. Key = ProcessGuid (braces stripped, lower) when
    present, else (pid, start ts) so pid reuse never merges two processes. Parent = the ParentProcessGuid node, else
    the node with pid == ppid (4688: the CREATOR ProcessId) alive at the child's start (started before, not ended
    before). Orphan ('Orphan Process') = a parent reference that resolves to nothing: node['orphan'] = 'missing'
    (pid/guid never seen) | 'exited' (that pid/guid had exited before the child started). An empty tree on junk."""
    try:
        if isinstance(events, (bytes, bytearray, memoryview, str)):
            events = process_events(events)
        if pid is not None:
            starts = [e for e in events if e.get("event") == "start"]
            want, out, seen = _pe_int(pid) if not isinstance(pid, int) else pid, [], set()
            while want is not None and want not in seen and len(out) < 64:
                seen.add(want)
                r = next((e for e in reversed(starts) if e.get("pid") == want), None)
                if not r:
                    break
                out.append(r)
                want = r.get("ppid")
            return out
        return _pt_build(list(events or [])[:200000])
    except Exception:  # noqa: BLE001
        return [] if pid is not None else {}


def _pt_ts(v):
    """Event time -> epoch seconds (ISO 8601 with 7-digit fractions / Z / offset, 'M/D/YYYY h:mm:ss PM', epoch)."""
    import datetime as _dt
    s = str(v or "").strip()
    if not s:
        return None
    if re.fullmatch(r"\d{9,13}(?:\.\d+)?", s):
        f = float(s)
        return f / 1000 if f > 1e11 else f
    m = re.match(r"(\d{4})-(\d\d)-(\d\d)[T ](\d\d):(\d\d):(\d\d)(?:[.,](\d+))?\s*(Z|[+-]\d\d:?\d\d)?", s)
    try:
        if m:
            y, mo, d, h, mi, se, fr, tz = m.groups()
            t = _dt.datetime(int(y), int(mo), int(d), int(h), int(mi), int(se), int((fr or "0")[:6].ljust(6, "0")),
                             tzinfo=_dt.timezone.utc).timestamp()
            if tz and tz != "Z":
                z = tz.replace(":", "")
                t -= (1 if z[0] == "+" else -1) * (int(z[1:3]) * 3600 + int(z[3:5]) * 60)
            return t
        m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})[ T](\d{1,2}):(\d\d):(\d\d)(?:\.(\d+))?\s*([AaPp][Mm])?", s)
        if m:
            mo, d, y, h, mi, se, fr, ap = m.groups()
            h = int(h) % 12 + (12 if ap and ap.upper() == "PM" else 0) if ap else int(h)
            return _dt.datetime(int(y), int(mo), int(d), h, int(mi), int(se), int((fr or "0")[:6].ljust(6, "0")),
                                tzinfo=_dt.timezone.utc).timestamp()
    except ValueError:
        return None
    return None


def _pt_guid(g):
    s = str(g or "").strip().strip("{}").lower()
    return s if s and s.strip("0-") else None


def _pt_build(events):
    evs = [e for e in events if isinstance(e, dict) and e.get("event") in ("start", "end")]
    tss = [_pt_ts(e.get("ts")) for e in evs]
    timed = bool(evs) and all(t is not None for t in tss)
    order = sorted(range(len(evs)), key=lambda i: (tss[i], i) if timed else (i,))
    nodes, by_guid, by_pid, keys, ended_guid = {}, {}, {}, [], {}
    for i in order:
        e, t = evs[i], (tss[i] if timed else i)
        g = _pt_guid(e.get("guid"))
        if e["event"] == "end":
            n = nodes.get(by_guid.get(g)) if g else None
            if n is None and e.get("pid") is not None:
                n = next((nodes[k] for k in reversed(by_pid.get(e["pid"], [])) if nodes[k]["end"] is None), None)
            if n is not None and n["end"] is None:
                n["end"] = t
            elif g:
                ended_guid[g] = t
            continue
        key = g if g and g not in by_guid else (e.get("pid"), e.get("ts") if e.get("ts") is not None else i)
        while key in nodes:
            key = (key, i)
        nodes[key] = {"key": key, "pid": e.get("pid"), "pid_raw": e.get("pid_raw"), "ppid": e.get("ppid"),
                      "ppid_raw": e.get("ppid_raw"), "image": e.get("image"), "cmdline": e.get("cmdline"),
                      "parent_image": e.get("parent_image"), "guid": g, "parent_guid": _pt_guid(e.get("parent_guid")),
                      "user": e.get("user"), "ts": e.get("ts"), "start": t, "end": None, "parent": None,
                      "orphan": None, "rec": e}
        keys.append(key)
        if g:
            by_guid.setdefault(g, key)
        if e.get("pid") is not None:
            by_pid.setdefault(e["pid"], []).append(key)
    children = {k: [] for k in keys}
    edges = []
    for k in keys:
        n = nodes[k]
        par, why = None, None
        pg = n["parent_guid"]
        if pg:
            pk = by_guid.get(pg)
            if pk is not None and pk != k and nodes[pk]["start"] <= n["start"]:
                par = pk
            else:
                why = "exited" if pg in ended_guid and ended_guid[pg] <= n["start"] else "missing"
        if par is None and not (pg and why) and n["ppid"] is not None:
            cands = [c for c in by_pid.get(n["ppid"], []) if c != k and nodes[c]["start"] <= n["start"]]
            alive = [c for c in cands if nodes[c]["end"] is None or nodes[c]["end"] >= n["start"]]
            if alive:
                par = alive[-1]
            else:
                why = "exited" if cands else "missing"
        n["parent"], n["orphan"] = par, (why if par is None else None)
        if par is not None:
            children[par].append(k)
            edges.append((par, k))
    parent = {k: nodes[k]["parent"] for k in keys}
    depth, chains = {}, {}
    for k in keys:
        ch, seen, c = [], set(), k
        while c is not None and c not in seen and len(ch) < 512:
            seen.add(c)
            ch.append(c)
            c = parent[c]
        depth[k] = len(ch) - 1
        if not children[k]:
            chains[k] = ch[::-1]
    roots = [k for k in keys if parent[k] is None]
    return {"nodes": nodes, "edges": edges, "roots": roots, "orphans": [k for k in keys if nodes[k]["orphan"]],
            "leaves": [k for k in keys if not children[k]], "children": children, "parent": parent, "depth": depth,
            "max_depth": max(depth.values()) if depth else 0, "chains": chains, "order": keys}


def process_chain(tree, node):
    """[root .. node] keys for any node (key, pid, guid or image basename resolving to one node)."""
    try:
        ks = _pt_find(tree, node)
        if len(ks) != 1:
            return []
        ch, c = [], ks[0]
        while c is not None and c not in ch and len(ch) < 512:
            ch.append(c)
            c = tree["parent"].get(c)
        return ch[::-1]
    except Exception:  # noqa: BLE001
        return []


def _pt_base(img):
    return re.split(r"[\\/]", str(img or "").rstrip("\\/"))[-1]


def _pt_find(tree, what):
    """Node keys matching `what`: a node key, guid, pid (int / '0x..' / decimal text), image basename or full path
    (case-insensitive); several matches in start order."""
    nodes = tree.get("nodes") or {}
    if what in nodes:
        return [what]
    if isinstance(what, dict) and what.get("key") in nodes:
        return [what["key"]]
    s = str(what if what is not None else "").strip()
    if not s:
        return []
    order = tree.get("order") or list(nodes)
    g = _pt_guid(s)
    hit = [k for k in order if g and nodes[k]["guid"] == g]
    if hit:
        return hit
    p = what if isinstance(what, int) else _pe_int(s)
    if p is not None:
        hit = [k for k in order if nodes[k]["pid"] == p]
        if hit:
            return hit
    low = s.lower()
    hit = [k for k in order if str(nodes[k]["image"] or "").lower() == low]
    return hit or [k for k in order if _pt_base(nodes[k]["image"]).lower() == _pt_base(s).lower()]


def _pt_repr(n, accepted=None):
    """A node in the answer's spelling: the accepted value it matches (basename / path / pid / guid, case-insensitive)
    or, with no accepted list, its image basename as logged (pid_raw when the image is unknown)."""
    if accepted:
        forms = {str(n.get("image") or "").lower(), _pt_base(n.get("image")).lower(), str(n.get("guid") or ""),
                 str(n.get("pid_raw") or "").lower(), str(n.get("pid") if n.get("pid") is not None else "")}
        if n.get("pid") is not None:
            forms.add(hex(n["pid"]))
        forms.discard("")
        for a in accepted:
            al = str(a).strip().lower()
            if al in forms or _pt_guid(al) in forms or (_pe_int(al) is not None and _pe_int(al) == n.get("pid")):
                return a
        return None
    return _pt_base(n.get("image")) or n.get("pid_raw") or (str(n["pid"]) if n.get("pid") is not None else None)


def process_tree_answer(tree, kind, accepted_values=None, what=None):
    """Answer a process-tree question. kind: root | leaf | parent(-of) | children(-of) | child-count | depth |
    max-depth | count | orphan | orphan-parent | chain | ancestor(s). `what` names the node (pid, guid, image
    basename or path; case-insensitive). Images compared case-insensitively, answered in the log's spelling (or the
    matching accepted value). One value -> str, several -> list in start order; chain -> [root..node]. 'none' when
    the field is absent (parent of a root, children of a leaf, no orphan), None when it cannot answer (unknown /
    ambiguous node, empty tree)."""
    try:
        if isinstance(tree, (bytes, bytearray, memoryview, str)) or isinstance(tree, list):
            tree = process_tree(tree)
        nodes = (tree or {}).get("nodes")
        if not nodes:
            return None
        acc = [a for a in (accepted_values or []) if str(a).strip()] or None
        kd = re.sub(r"[^a-z]", "", str(kind or "").lower()).replace("of", "") if kind else ""
        kd = {"parents": "parent", "child": "children", "kids": "children", "roots": "root", "leaves": "leaf",
              "leafs": "leaf", "orphans": "orphan", "ancestors": "chain", "ancestor": "chain", "ancestry": "chain",
              "lineage": "chain", "depthtree": "maxdepth", "treedepth": "maxdepth", "numchildren": "childcount",
              "childrencount": "childcount", "orphanparents": "orphanparent"}.get(kd, kd)

        def rep(keys):
            vals = []
            for k in keys:
                v = _pt_repr(nodes[k], acc)
                if v is not None and v not in vals:
                    vals.append(v)
            return vals

        def one(vals, absent="none"):
            return absent if not vals else vals[0] if len(vals) == 1 else vals

        def target():   # same image twice: answerable only when every match gives the same answer (below)
            return _pt_find(tree, what)
        if kd in ("root", "leaf", "orphan"):
            base = tree["roots"] if kd == "root" else tree["leaves"] if kd == "leaf" else tree["orphans"]
            if what is not None and kd == "root":
                ch = {process_chain(tree, k)[0] for k in target() if process_chain(tree, k)}
                base = [k for k in tree["order"] if k in ch]
            if kd == "orphan" and len(base) > 1 and not acc:
                ex = [k for k in base if nodes[k]["orphan"] == "exited"]
                base = ex or base
            return one(rep(base))
        if kd == "orphanparent":
            return one([v for v in dict.fromkeys(_pt_base(nodes[k]["parent_image"]) or nodes[k]["ppid_raw"]
                                                 for k in tree["orphans"]) if v])
        if kd == "count":
            w = str(what or "").lower()
            if not w or w in ("nodes", "processes", "process", "all"):
                return str(len(nodes))
            if w in ("roots", "orphans", "leaves", "edges"):
                return str(len(tree[w]))
            return str(len(_pt_find(tree, what)))
        if kd == "maxdepth" or (kd == "depth" and what is None):
            return str(tree["max_depth"])
        ks = target()
        if not ks:
            return None
        res = []
        for k in ks:
            if kd == "parent":
                p = tree["parent"][k]
                r = tuple(rep([p])) if p is not None else ("none",)
            elif kd == "children":
                r = tuple(rep(tree["children"][k])) or ("none",)
            elif kd == "childcount":
                r = (str(len(tree["children"][k])),)
            elif kd == "depth":
                r = (str(tree["depth"][k]),)
            elif kd == "chain":
                r = tuple(rep(process_chain(tree, k)))
            else:
                return None
            if r not in res:
                res.append(r)
        if len(res) != 1:
            return None
        r = list(res[0])
        if kd == "chain":
            return r
        return r[0] if len(r) == 1 else r
    except Exception:  # noqa: BLE001
        return None


def _proc_codecs(src, raw, _depth):
    """Codecs inside process-telemetry command lines (Sysmon 1 / 4688 XML, JSON, k=v): the log escapes the script's
    quotes (`&quot;`, `\\"`), so the descriptor only reads after process_events() unescapes each command line."""
    if not (_PE_HINT.search((src or "")[:1 << 20]) or _PL_HINT.search((src or "")[:1 << 20])):
        return []
    out, seen, t0 = [], set(), time.time()
    for e in process_events(raw if raw is not None else src):
        for c in (e.get("cmdline"), e.get("parent_cmdline")):
            if not c or len(c) < 16 or c in seen or time.time() - t0 > 1.0:
                continue
            seen.add(c)
            out += [dict(x, id=f"{x.get('id')}@proc") for x in find_codecs(c, _depth + 1) if x.get("plain")]
        if out:
            break
    return out


_RC_KINDS = ("ips", "user_agents", "file_names", "ports")
_RC_UA_FIELDS = re.compile(r"(?i)(?:^|_)(?:user_?agent|ua|agent)$")
_RC_PORT_FIELDS = re.compile(r"(?i)(?:^|_)(?:port|[lr]port|dst_?port|dest_?port|c2_?port)$")
_RC_IP_FIELDS = re.compile(r"(?i)(?:^|_)(?:ip|ipv[46]|addr(?:ess)?|dst|dest|c2|server|host|callback)(?:_ip|_addr)?$")
_RC_NAME_FIELDS = re.compile(r"(?i)^(?:file_?path|path|file|file_?name|filename|drop(?:_path|_file)?|"
                             r"dest(?:ination)?(?:_path)?|payload|stage|next_stage|dropper|"
                             r"(?:out|output|save|write|target|staging|stage|dropped|local)_?(?:path|file|name))$")
_RC_DFLT_PORT = {"http": 80, "https": 443, "ws": 80, "wss": 443, "ftp": 21}


def _rc_ip(v):
    """'10.0.0.5' / '[2001:db8::1]' / '::ffff:1.2.3.4' / '1.2.3.4:8080' / defanged '1[.]2[.]3[.]4' -> canonical IP, else None."""
    try:
        import ipaddress
        s = refang(str(v)).strip()
        if s.startswith("[") and "]" in s:
            s = s[1:s.index("]")]
        elif s.count(":") == 1 and "." in s:
            s = s.split(":", 1)[0]
        a = ipaddress.ip_address(s)
        if a.version == 6 and a.ipv4_mapped:
            a = a.ipv4_mapped
        return str(a)
    except Exception:  # noqa: BLE001
        return None


def _rc_cd_name(cd):
    """Content-Disposition value -> filename (filename*=UTF-8''x wins over filename=), else None."""
    if not cd:
        return None
    from urllib.parse import unquote
    m = re.search(r"(?i)filename\*\s*=\s*[\w\-]*'[^']*'([^;\s]+)", str(cd))
    if m:
        return unquote(m.group(1)).strip("\"'")
    m = re.search(r'(?i)filename\s*=\s*(?:"((?:[^"\\]|\\.)*)"|([^;\s]+))', str(cd))
    return (m.group(1) if m.group(1) is not None else m.group(2)).strip() if m else None


def _rc_basename(v, need_ext=True):
    s = str(v or "").strip().strip("\"'").split("?", 1)[0].split("#", 1)[0]
    b = re.split(r"[\\/]", s)[-1].strip()
    if not b or len(b) > 255 or (need_ext and not re.search(r"\.[A-Za-z0-9]{1,8}$", b)):
        return None
    return b


def _rc_url_bits(u):
    """URL -> (ip or None, port or None, basename or None) for the extra indicator kinds."""
    from urllib.parse import unquote
    scheme, host, port, rest = _rc_split(u)
    port = port if port is not None else _RC_DFLT_PORT.get(scheme)
    return _rc_ip(host), port, _rc_basename(unquote(rest.split("?", 1)[0]))


def _rc_kinds_declared(plans):
    """{kind: {canonical: (declared spelling, member)}} for ips / user_agents / file_names / ports."""
    out = {k: {} for k in _RC_KINDS}

    def add(kind, canon, val, m):
        if canon is not None and canon != "":
            out[kind].setdefault(canon, (val, m))
    for m in sorted(plans or {}):
        try:
            d = _rc_dict(plans[m])
        except Exception:  # noqa: BLE001
            continue
        for k, v in d.items():
            try:
                if not isinstance(v, (str, int)) or isinstance(v, bool):
                    continue
                f, v = _rc_field(k), str(v).strip()
                if not v:
                    continue
                r = refang(v)
                if _RC_URL.fullmatch(r):
                    ip, port, base = _rc_url_bits(r)
                    if ip:
                        add("ips", ip, _rc_split(r)[1], m)
                    if port:
                        add("ports", str(port), str(port), m)
                    if base:
                        add("file_names", base.lower(), base, m)
                    continue
                if _RC_UA_FIELDS.search(f):
                    add("user_agents", " ".join(v.split()), v, m)
                    continue
                if _RC_PORT_FIELDS.search(f) and re.fullmatch(r"\d{1,5}", v) and 0 < int(v) < 65536:
                    add("ports", str(int(v)), v, m)
                    continue
                ip = _rc_ip(r)
                if ip and (_RC_IP_FIELDS.search(f) or re.fullmatch(r"[\d.]+|\[?[0-9a-fA-F:.]+\]?", r)):
                    add("ips", ip, v, m)
                    mm = re.fullmatch(r"\[?[^\]]+\]?:(\d{1,5})", r)
                    if mm and ("." in r or r.startswith("[")):
                        add("ports", str(int(mm.group(1))), mm.group(1), m)
                    continue
                if _RC_NAME_FIELDS.match(f) and not re.match(r"(?i)^[a-z][a-z0-9+.\-]*://", r):
                    base = _rc_basename(v)
                    if base:
                        add("file_names", base.lower(), base, m)
            except Exception:  # noqa: BLE001
                continue
    return out


def _rc_kinds_observed(observed):
    """{kind: {canonical: observed spelling}} for ips / user_agents / file_names / ports from the evidence."""
    out = {k: {} for k in _RC_KINDS}
    try:
        recs = observed
        if isinstance(recs, dict):
            import json
            recs = network_indicators(json.dumps(recs)) if isinstance(recs.get("log"), dict) else [recs]
        elif isinstance(recs, (bytes, bytearray, memoryview, str)):
            recs = network_indicators(recs)
        if not isinstance(recs, (list, tuple, set)):
            return out
        for x in list(recs)[:200000]:
            if isinstance(x, str):
                r = refang(x)
                if _RC_URL.fullmatch(r):
                    x = {"kind": "http", "url": x}
                elif _rc_ip(x):
                    x = {"kind": "conn", "ip": x}
                else:
                    continue
            if not isinstance(x, dict):
                continue
            low = {_rc_field(k): v for k, v in x.items()}
            kind = str(low.get("kind") or "")
            ips = [low.get(k) for k in ("ip", "dest_ip", "destination_ip", "destinationip", "dst_ip", "id_resp_h",
                                        "serveripaddress", "server_ip", "s_ip") if low.get(k)]
            ans = low.get("answers") or ()
            ips += list(ans) if isinstance(ans, (list, tuple)) else str(ans).split(",")
            for a in ips:
                c = _rc_ip(a)
                if c:
                    out["ips"].setdefault(c, str(a).strip())
            url = low.get("url") or low.get("request_url") or low.get("full_uri")
            uport = ubase = None
            if url and _RC_URL.fullmatch(refang(str(url))):
                uip, uport, ubase = _rc_url_bits(refang(str(url)))
                if uip:
                    out["ips"].setdefault(uip, _rc_split(str(url))[1])
            elif low.get("uri"):
                ubase = _rc_basename(str(low["uri"]))
            ua = next((low[k] for k in ("user_agent", "useragent", "http_user_agent", "cs_user_agent")
                       if isinstance(low.get(k), str) and low[k].strip() not in ("", "-")), None)
            if ua:
                out["user_agents"].setdefault(" ".join(ua.split()), ua)
            if kind != "dns":
                p = next((low[k] for k in ("port", "dest_port", "destination_port", "destinationport", "dst_port",
                                           "id_resp_p") if low.get(k) not in (None, "", "-")), None) or uport
                if p is not None and re.fullmatch(r"\d{1,5}", str(p).strip()) and 0 < int(p) < 65536:
                    out["ports"].setdefault(str(int(p)), str(int(p)))
            names = [ubase] if ubase else []
            for k in ("filename", "file_name", "resp_filenames", "orig_filenames"):
                v = low.get(k)
                names += list(v) if isinstance(v, (list, tuple)) else str(v).split(",") if v else []
            cd = _rc_cd_name(low.get("content_disposition"))
            if cd:
                names.append(cd)
            for n in names:
                b = _rc_basename(n)
                if b:
                    out["file_names"].setdefault(b.lower(), b)
    except Exception:  # noqa: BLE001
        pass
    return out


# --- redirects + DNS resolution (prebuild http-redirect-dns-resolve) --------------------------------------------------
# "Where the requests actually went" can differ from the declared URL by a 30x Location hop or a CNAME. HAR
# (response.redirectURL / Location header + status), pcap HTTP responses (paired in order with the reverse flow's
# requests) and Zeek http status/location give url -> next url; DNS answers (pcap / Zeek / Sysmon EID 22) give
# host -> [CNAME .., A/AAAA]. reconcile() adds every redirect target as an observed URL (the observed-only value when no
# plan names it) and counts a declared URL as fetched when the evidence only shows a URL-less TLS / TCP connection to
# its host, a CNAME of it, or an IP it resolved to.
def _rd_join(url, loc, status=None):
    """Absolute redirect target of a response (Location resolved against the request URL), else None. A Location on a
    non-3xx status (201 Created, 200 with a stray header) is no redirect."""
    try:
        loc = str(loc or "").strip()
        st = str(status or "").strip()
        if not loc or loc == "-" or (st and st not in ("0", "-") and not re.fullmatch(r"30[0-35-8]", st)):
            return None
        if url and not re.match(r"(?i)^[a-z][a-z0-9+.\-]*://", loc):
            from urllib.parse import urljoin
            loc = urljoin(refang(str(url)), loc)
        return loc
    except Exception:  # noqa: BLE001
        return None


def _rd_records(observed):
    if isinstance(observed, dict):
        import json
        observed = json.dumps(observed) if isinstance(observed.get("log"), dict) else [observed]
    if isinstance(observed, (bytes, bytearray, memoryview, str)):
        return network_indicators(observed)
    return [x for x in observed if isinstance(x, dict)] if isinstance(observed, (list, tuple)) else []


def _rd_maps(observed):
    """-> (hops {canon url: (canon next url, next spelling, url spelling)}, alias {canon host: [CNAME / IP spellings]},
    host spellings {canon host: spelling}, dst {IPs reached by a URL-less TLS / TCP connection},
    reached {canon hosts named by a URL-less TLS / conn record})."""
    hops, alias, spell, dst, reached, named = {}, {}, {}, set(), set(), set()
    try:
        for x in _rd_records(observed)[:200000]:
            low = {_rc_field(k): v for k, v in x.items()}
            kind = str(low.get("kind") or "")
            url = low.get("url") or low.get("request_url") or low.get("full_uri")
            loc = next((low[k] for k in ("location", "redirect_url", "redirecturl", "redirect_location")
                        if isinstance(low.get(k), str)), None)
            nxt = _rd_join(url, loc, low.get("status") or low.get("status_code")) if url else None
            if nxt:
                cu, cn = canon_url(str(url)), canon_url(nxt)
                if cu and cn and cu != cn:
                    hops.setdefault(cu, (cn, nxt, str(url)))
            host = low.get("host") or low.get("query") or low.get("queryname")
            h = canon_host(str(host)) if host else None
            ans = low.get("answers") or ()
            ans = ans if isinstance(ans, (list, tuple)) else str(ans).split(",")
            if kind == "dns":
                for a in ans if h else ():
                    a = str(a).strip().rstrip(".")
                    if a and a not in alias.setdefault(h, []) and (_rc_ip(a) or canon_host(a)):
                        spell.setdefault(h, str(host))
                        alias[h].append(a)
                continue
            ip = _rc_ip(low.get("ip")) if low.get("ip") else None
            if kind == "conn" and not h:
                if ip:
                    dst.add(ip)
                continue
            if ip:
                named.add(ip)
            if kind in ("conn", "tls") or (kind == "http" and not url):
                if h and h != ip:
                    reached.add(h)
            elif kind == "http" and url and ip:   # HAR serverIPAddress / pcap dst: host -> ip
                hu = canon_host(str(url))
                if hu and hu != ip and ip not in alias.setdefault(hu, []):
                    spell.setdefault(hu, _rc_split(str(url))[1])
                    alias[hu].append(ip)
    except Exception:  # noqa: BLE001
        pass
    # a bare TCP connect only stands for a fetch when no URL / SNI-carrying record explains its IP (shared-IP hosts)
    return hops, alias, spell, dst - named, reached


def _rd_resolve(h, alias):
    """canon host -> [CNAME .., IP ..] spellings, following CNAME chains (bounded, loop-safe)."""
    out, todo, seen = [], [h], {h}
    while todo and len(seen) < 64:
        for a in alias.get(todo.pop(0), ()):
            c = _rc_ip(a) or canon_host(a)
            if c and c not in seen:
                seen.add(c)
                out.append(a)
                if not _rc_ip(a):
                    todo.append(c)
    return out


def _rd_chains(hops):
    out = {}
    for cu, (cn, nsp, sp) in hops.items():
        chain, seen = [], {cu}
        while cn and cn not in seen and len(chain) < 16:
            chain.append(nsp)
            seen.add(cn)
            cn, nsp = hops.get(cn, (None, None, None))[:2]
        out[sp] = chain
    return out


def resolve_chain(observed):
    """Network evidence (HAR / pcap / pcapng / Zeek / network_indicators() records) -> {url: [hop, .., final url]}:
    every request URL answered by a 30x redirect, mapped to the Location targets it leads through (relative Locations
    resolved against the request; loops cut). Spellings are the evidence's own. {} when nothing redirects."""
    try:
        return _rd_chains(_rd_maps(observed)[0])
    except Exception:  # noqa: BLE001
        return {}


def resolve_hosts(observed):
    """Network evidence -> {host: [CNAME .., A/AAAA ..]} from DNS answers (CNAME chains followed) and HAR / pcap
    request IPs. {} when nothing resolves."""
    try:
        _, alias, spell, _, _ = _rd_maps(observed)
        return {spell.get(h, h): r for h in alias for r in [_rd_resolve(h, alias)] if r}
    except Exception:  # noqa: BLE001
        return {}


def reconcile(plans, observed):
    """Declared fetch targets (decoded plans of every member) vs observed network evidence -> report, or None when
    either side is empty.
      hosts / urls   {declared_only, observed_only, both}: original spellings (declared side's spelling for `both`),
                     sorted by canonical form. URL level compares only records that carry a URL; DNS/TLS/conn records
                     confirm a host, never a URL.
      one_sided      urls.declared_only + urls.observed_only, or the host-level difference when the URL level is clean
      indicator      the single one-sided value (URL level first, then host level), else None
      members        {member: [declared values]}; member_of {declared value: member}
      unfetched      members with declared URLs none of which was observed (the fetch that never happened);
      unseen_hosts   members none of whose declared hosts shows up anywhere in the evidence
      stages         {stage name: observed URL value} for non-URL next_stage names seen as an observed URL basename
      ips / user_agents / file_names / ports
                     the same {declared_only, observed_only, both} shape for non-URL indicators: plan IP literals /
                     URL IP hosts vs conn/http dst + DNS A/AAAA answers; plan user_agent fields vs HAR / Zeek / W3C /
                     pcap User-Agent; plan file_path / next_stage / URL basenames vs observed URI basenames +
                     Content-Disposition / Zeek *_filenames; plan port fields + URL ports vs dst ports (DNS excluded).
                     Never part of one_sided / indicator (those stay URL / host).
      redirects      resolve_chain(): {request url: [Location hop, .., final url]}; every redirect target joins the
                     observed URLs (a target no plan names is observed-only)
      final_urls     {declared value: final url} for declared URLs that redirect
      resolved       {declared value: [CNAME .., IP ..]} from the evidence's DNS answers / request IPs
      fetched_via    {declared value: 'tls' | 'cname' | 'ip'}: declared URLs (hosts) with no URL-level evidence counted
                     as fetched (seen) through a URL-less TLS / TCP connection to the host, a CNAME of it, or an IP
                     it resolved to
      counts         sizes of every set above (+ <kind>_one_sided)"""
    try:
        dec, obs = declared_fetches(plans), observed_fetches(observed)
        xd, xo, xm = _rc_kinds_declared(plans), _rc_kinds_observed(observed), {}
        hops, alias, _, rd_dst, rd_reached = _rd_maps(observed)
        seen_u = {x["url"] for x in obs if x["url"]}
        for cu, (cn, nsp, _) in hops.items():   # a redirect target is where the request went, logged or not
            if cn not in seen_u:
                seen_u.add(cn)
                obs.append({"value": nsp, "url": cn, "host": canon_host(nsp), "kind": "redirect"})
        if not dec or not obs:
            if not (any(xd[k] for k in _RC_KINDS) and any(xo[k] for k in _RC_KINDS)):
                return None

        def sides(level):
            def spell(x):
                return _rc_split(x["value"])[1] if level == "host" and x["url"] else x["value"]
            d, o = {}, {}
            for x in dec:
                if x[level]:
                    d.setdefault(x[level], spell(x))
            for x in obs:
                if x[level]:
                    o.setdefault(x[level], spell(x))
            return {"declared_only": [d[k] for k in sorted(set(d) - set(o))],
                    "observed_only": [o[k] for k in sorted(set(o) - set(d))],
                    "both": [d[k] for k in sorted(set(d) & set(o))]}, set(d), set(o)

        # a declared URL with no URL-level evidence for its host still counts as fetched when a URL-less TLS / conn
        # record reached its host, a CNAME of it, or an IP it resolved to; a declared host whose CNAME is observed
        # counts as seen. Matching only: the declared spelling is reported, the CNAME / IP adds no observed value.
        url_hosts = {x["host"] for x in obs if x["url"]}
        obs_h = {x["host"] for x in obs if x["host"]}
        via, final, resolved = {}, {}, {}
        for x in dec:
            r = _rd_resolve(x["host"], alias) if x["host"] else []
            if r:
                resolved.setdefault(x["value"], r)
            cr = {_rc_ip(a) or canon_host(a) for a in r}
            if x["url"] and x["url"] not in seen_u and x["host"] not in url_hosts:
                if x["host"] in rd_reached or cr & rd_reached:
                    via[x["value"]] = "cname" if x["host"] not in rd_reached else "tls"
                elif cr & rd_dst:
                    via[x["value"]] = "ip"
                if x["value"] in via:
                    obs.append({"value": x["value"], "url": x["url"], "host": x["host"], "kind": "resolved"})
            elif x["host"] and not x["url"] and x["host"] not in obs_h and cr & obs_h:
                via[x["value"]] = "cname"
                obs.append({"value": x["value"], "url": None, "host": x["host"], "kind": "resolved"})
            if x["url"] in hops:
                cn, last, walked = hops[x["url"]][0], hops[x["url"]][1], {x["url"]}
                while cn in hops and cn not in walked and len(walked) < 17:
                    walked.add(cn)
                    cn, last = hops[cn][:2]
                final[x["value"]] = last
        urls, du, ou = sides("url")
        hosts, dh, oh = sides("host")
        one = urls["declared_only"] + urls["observed_only"]
        if not one:
            one = hosts["declared_only"] + hosts["observed_only"]
        members, member_of, unfetched, unseen = {}, {}, [], []
        for m in sorted({x["member"] for x in dec}):
            xs = [x for x in dec if x["member"] == m and (x["url"] or x["host"])]
            if not xs:
                continue
            members[m] = [x["value"] for x in xs]
            for x in xs:
                member_of.setdefault(x["value"], m)
            us = [x["url"] for x in xs if x["url"]]
            if us and not any(u in ou for u in us):
                unfetched.append(m)
            if not any(x["host"] in oh for x in xs if x["host"]):
                unseen.append(m)
        base = {}
        for x in obs:
            if x["url"]:
                base.setdefault(x["url"].split("?", 1)[0].rsplit("/", 1)[-1].lower(), x["value"])
        stages = {x["value"]: base[x["stage"]] for x in dec if x["stage"] and x["stage"] in base}
        rep = {"hosts": hosts, "urls": urls, "one_sided": one, "indicator": one[0] if len(one) == 1 else None,
               "members": members, "member_of": member_of, "unfetched": unfetched, "unseen_hosts": unseen,
               "stages": stages, "redirects": _rd_chains(hops), "final_urls": final, "resolved": resolved,
               "fetched_via": via}
        for lv in _RC_KINDS:
            d, o = {c: v for c, (v, _) in xd[lv].items()}, xo[lv]
            rep[lv] = {"declared_only": [d[k] for k in sorted(set(d) - set(o))],
                       "observed_only": [o[k] for k in sorted(set(o) - set(d))],
                       "both": [d[k] for k in sorted(set(d) & set(o))]}
            for v, m in xd[lv].values():
                member_of.setdefault(v, m)
        rep["counts"] = {f"{lv}_{k}": len(v) for lv in ("hosts", "urls") + _RC_KINDS for k, v in rep[lv].items()}
        rep["counts"].update(one_sided=len(one), unfetched=len(unfetched), unseen_hosts=len(unseen),
                             declared_members=len(members), redirects=len(rep["redirects"]),
                             final_urls=len(final), fetched_via=len(via))
        rep["counts"].update({f"{lv}_one_sided": len(rep[lv]["declared_only"]) + len(rep[lv]["observed_only"])
                              for lv in _RC_KINDS})
        return rep
    except Exception:  # noqa: BLE001
        return None


def reconcile_answer(report, kind, accepted_values=None, what="indicator"):
    """One GM answer from a reconcile() report.
      exact_text  what='indicator' (the one-sided value), or '<level>.<side>' e.g. 'urls.observed_only' /
                  'hosts.declared_only' (its single value)
      enum        the member whose fetch never happened (what='unfetched' / 'unseen_hosts'), or the member that
                  declared the one-sided indicator; matched to accepted_values by name or stem
      integer     counts[what] (what='indicator' -> one_sided)
      redirects / final_urls / resolved / fetched_via: exact_text the final hop (last CNAME / IP for `resolved`,
                  the via-kind for `fetched_via`) of the single entry, integer the entry count, enum its member
      ips / user_agents / file_names / ports: what='<kind>.<side>' (e.g. 'user_agents.observed_only') or '<kind>'
                  alone (declared_only + observed_only); exact_text its single value, integer its size, enum the
                  member that declared it
    "none" when the requested set is empty; None when unanswerable (no report, or several candidates)."""
    try:
        if not report:
            return None
        lv0 = what.partition(".")[0]
        if lv0 in ("redirects", "final_urls", "resolved", "fetched_via"):
            vals = report.get(lv0) or {}
            if kind == "integer":
                return str(len(vals))
            if not vals:
                return "none" if kind != "enum" else None
            if len(vals) != 1:
                return None
            k0, v = next(iter(vals.items()))
            if kind == "enum":
                m = report["member_of"].get(k0)
                return next((a for a in accepted_values or () if str(a) == m), None if accepted_values else m)
            return (v[-1] if v else None) if isinstance(v, list) else v
        if lv0 in _RC_KINDS:
            lv, _, side = what.partition(".")
            if lv not in report:
                return None
            vals = report[lv][side] if side else report[lv]["declared_only"] + report[lv]["observed_only"]
            if kind == "integer":
                return str(len(vals))
            if not vals:
                return "none" if kind != "enum" else None
            if len(vals) != 1:
                return None
            if kind != "enum":
                return vals[0]
            m = report["member_of"].get(vals[0])
            if not m:
                return None
            stem = lambda s: re.sub(r"\.[A-Za-z0-9_]+$", "", str(s).replace("\\", "/").rsplit("/", 1)[-1]).lower()
            for a in accepted_values or ():
                if str(a) == m or stem(a) == stem(m):
                    return a
            return None if accepted_values else m
        if kind == "integer":
            return str(report["counts"]["one_sided" if what == "indicator" else what])
        if kind == "enum":
            if what in ("unfetched", "unseen_hosts"):
                ms = report[what]
            else:
                ind = report["indicator"]
                ms = [report["member_of"][ind]] if ind in report["member_of"] else []
            if not ms:
                return "none" if what in ("unfetched", "unseen_hosts") else None
            if len(ms) != 1:
                return None
            m = ms[0]
            stem = lambda s: re.sub(r"\.[A-Za-z0-9_]+$", "", str(s).replace("\\", "/").rsplit("/", 1)[-1]).lower()
            for a in accepted_values or ():
                if str(a) == m or stem(a) == stem(m):
                    return a
            return None if accepted_values else m
        if what == "indicator":
            vals = report["one_sided"]
        else:
            lv, _, side = what.partition(".")
            vals = report[lv][side]
        if not vals:
            return "none"
        return vals[0] if len(vals) == 1 else None
    except Exception:  # noqa: BLE001
        return None


# --- download / handoff graph (cross-file) ---------------------------------------------------------------------------
_DG_FILE_FIELDS = re.compile(r"(?i)^(?:file_?path|path|file|drop(?:_path|_file)?|dest(?:ination)?(?:_path)?|"
                             r"(?:out|output|save|write|target|staging|stage|dropped|local)_?(?:path|file))$")
_DG_STEP_FETCH = re.compile(r"(?i)acquire_remote|http_client|download|fetch|web_request|remote_fetch")
_DG_STEP_WRITE = re.compile(r"(?i)write_file|drop_file|save_file|write_disk|write_stage")


def _dg_member(d):
    """One decoded plan dict -> {language, next_language, next_stage, urls:[(field, value)], file_paths, steps, ...}."""
    low = {}
    for k, v in d.items():
        if isinstance(v, (list, tuple)) and k.lower() == "steps":
            v = ",".join(str(x) for x in v)
        if isinstance(v, (str, int, float)) and not isinstance(v, bool) and str(v).strip():
            low.setdefault(_rc_field(k), str(v).strip())
    r = {"language": low.get("language"), "next_language": low.get("next_language"),
         "next_stage": low.get("next_stage"), "urls": [], "file_paths": [], "steps": [],
         "stage_count": int(low["stage_count"]) if re.fullmatch(r"\d{1,4}", low.get("stage_count", "")) else None}
    r["steps"] = [s for s in re.split(r"[\s,;>|]+", low.get("steps", "")) if s]
    for f, v in low.items():
        u = refang(v)
        if f != "next_stage" and _RC_URL.fullmatch(u) and canon_url(u):
            r["urls"].append((f, v))
        elif _DG_FILE_FIELDS.match(f) and re.search(r"[\\/]|\.\w{1,6}$", v) and not _RC_URL.match(u):
            r["file_paths"].append(v)
    return r


def _dg_walk(edges):
    """{src: [dst..]} -> the single linear path from the unique root covering every node, else None."""
    nodes = set(edges) | {d for ds in edges.values() for d in ds}
    if not nodes or any(len(set(ds)) > 1 for ds in edges.values()):
        return None
    has_in = {d for ds in edges.values() for d in ds}
    roots = [n for n in nodes if n not in has_in]
    if len(roots) != 1:
        return None
    out, n = [], roots[0]
    while n is not None and n not in out:
        out.append(n)
        n = (edges.get(n) or [None])[0]
    return out if len(out) == len(nodes) else None


def download_graph(plans):
    """{member: decoded plan (dict / 'k=v|..' / JSON)} -> cross-file download/handoff graph report, or None when no
    plan carries a url / file_path / next_language / next_stage.
      members       {member: {language, next_language, next_stage, urls, hosts, file_paths, steps, stage_count}}
      edges         [{src, dst, kind}] kind: fetch (member->url; upload for upload_url / exfil fields), write
                    (url->file_path, or member->file_path when the member fetches nothing), handoff
                    (member->next_language), stage (member->next_stage)
      chain         languages in order following language -> next_language across files (None unless one linear path)
      member_chain  members in order: next_stage naming a member (name / stem), else the one member whose language is
                    the next_language (None unless one linear path); root / leaf = its ends (falls back to the
                    single member of the chain's first / last language)
      unique        {url, host, file_path: [members holding a value no other member shares]} -- only filled when at
                    least one value IS shared (otherwise "unique" means nothing); shared {kind: [values]}
      counts        members, urls, hosts, file_paths, languages, stages, edges, <kind>_edges, chain_length,
                    member_chain_length, stage_count_sum, stage_count_max"""
    try:
        mem = {}
        for m in sorted(plans or {}):
            try:
                g = _dg_member(_rc_dict(plans[m]))
            except Exception:  # noqa: BLE001
                continue
            if g["urls"] or g["file_paths"] or g["next_language"] or g["next_stage"]:
                g["hosts"] = sorted({canon_host(refang(v)) for _, v in g["urls"]} - {None})
                mem[m] = g
        if not mem:
            return None
        edges = []
        for m, g in mem.items():
            fetch = [v for f, v in g["urls"] if not re.search(r"upload|exfil|post|beacon|callback", f)]
            for f, v in g["urls"]:
                edges.append({"src": m, "dst": v, "kind": "fetch" if v in fetch else "upload"})
            writes = not g["steps"] or any(_DG_STEP_WRITE.search(s) for s in g["steps"])
            for p in g["file_paths"]:
                if writes and len(fetch) == 1:
                    edges.append({"src": fetch[0], "dst": p, "kind": "write"})
                else:
                    edges.append({"src": m, "dst": p, "kind": "write"})
            if g["next_language"]:
                edges.append({"src": m, "dst": g["next_language"], "kind": "handoff"})
            if g["next_stage"]:
                edges.append({"src": m, "dst": g["next_stage"], "kind": "stage"})
        # language chain (case-insensitive, first spelling kept); self-handoffs (same_language) are not chain links
        spell, lang_e = {}, {}
        for g in mem.values():
            a, b = g["language"], g["next_language"]
            for x in (a, b):
                if x:
                    spell.setdefault(x.lower(), x)
            if a and b and a.lower() != b.lower():
                lang_e.setdefault(a.lower(), [])
                if b.lower() not in lang_e[a.lower()]:
                    lang_e[a.lower()].append(b.lower())
        lw = _dg_walk(lang_e)
        chain = [spell[x] for x in lw] if lw else None
        # member chain
        stem = lambda s: re.sub(r"\.[A-Za-z0-9_]+$", "", str(s).replace("\\", "/").rsplit("/", 1)[-1]).lower()
        by_name = {}
        for m in mem:
            for k in (m.lower(), m.replace("\\", "/").rsplit("/", 1)[-1].lower(), stem(m)):
                by_name.setdefault(k, set()).add(m)
        by_lang = {}
        for m, g in mem.items():
            if g["language"]:
                by_lang.setdefault(g["language"].lower(), set()).add(m)
        mem_e = {}
        for m, g in mem.items():
            nxt = None
            ns = (g["next_stage"] or "").replace("\\", "/").rsplit("/", 1)[-1].lower()
            for k in (ns, stem(ns)) if ns else ():
                if len(by_name.get(k, ())) == 1:
                    nxt = next(iter(by_name[k]))
                    break
            nl = (g["next_language"] or "").lower()
            if nxt is None and nl and nl != (g["language"] or "").lower() and len(by_lang.get(nl, ())) == 1:
                nxt = next(iter(by_lang[nl]))
            if nxt and nxt != m:
                mem_e[m] = [nxt]
        mchain = _dg_walk(mem_e)
        if mchain and len(mchain) < 2:
            mchain = None
        root = leaf = None
        if mchain:
            root, leaf = mchain[0], mchain[-1]
        elif chain:
            r0, l0 = by_lang.get(chain[0].lower(), set()), by_lang.get(chain[-1].lower(), set())
            root = next(iter(r0)) if len(r0) == 1 else None
            leaf = next(iter(l0)) if len(l0) == 1 else None
        unique, shared = {}, {}
        for kind, get in (("url", lambda g: [v for _, v in g["urls"]]), ("host", lambda g: g["hosts"]),
                          ("file_path", lambda g: g["file_paths"])):
            key = (lambda v: canon_url(refang(v))) if kind == "url" else (lambda v: str(v).lower())
            hold = {}
            for m, g in mem.items():
                for v in get(g):
                    hold.setdefault(key(v), (v, set()))[1].add(m)
            shared[kind] = sorted(v for v, ms in hold.values() if len(ms) > 1)
            have = [m for m, g in mem.items() if get(g)]
            unique[kind] = (sorted(m for m in have if any(len(hold[key(v)][1]) == 1 for v in get(mem[m])))
                            if shared[kind] else [])
        sc = [g["stage_count"] for g in mem.values() if g["stage_count"] is not None]
        all_urls = {canon_url(refang(v)) for g in mem.values() for _, v in g["urls"]}
        rep = {"members": mem, "edges": edges, "chain": chain, "member_chain": mchain, "root": root, "leaf": leaf,
               "unique": unique, "shared": shared}
        counts = {"members": len(mem), "urls": len(all_urls - {None}),
                  "hosts": len({h for g in mem.values() for h in g["hosts"]}),
                  "file_paths": len({p.lower() for g in mem.values() for p in g["file_paths"]}),
                  "languages": len(spell), "stages": len({g["next_stage"].lower() for g in mem.values()
                                                          if g["next_stage"]}),
                  "edges": len(edges), "chain_length": len(chain or ()), "member_chain_length": len(mchain or ()),
                  "stage_count_sum": sum(sc), "stage_count_max": max(sc) if sc else 0}
        for k in ("fetch", "upload", "write", "handoff", "stage"):
            counts[f"{k}_edges"] = sum(1 for e in edges if e["kind"] == k)
        rep["counts"] = counts
        return rep
    except Exception:  # noqa: BLE001
        return None


def download_graph_answer(report, kind, what="chain", accepted_values=None, sep=">"):
    """One GM answer from a download_graph() report.
      ordered_tokens  what='chain' (languages) / 'member_chain', joined with `sep`
      integer         counts[what] (e.g. 'hosts', 'edges', 'fetch_edges', 'stages', 'chain_length')
      enum            what='root' / 'leaf' (member at the chain's ends), 'unique_url' / 'unique_host' /
                      'unique_file_path' (the one member whose value nobody shares), 'root_language' /
                      'leaf_language'; matched to accepted_values by name, stem or case
      exact_text      '<root|leaf>.<url|host|file_path|next_stage|next_language|language>' (that member's single value)
    None when unanswerable (no report, no single linear chain, several candidates)."""
    try:
        if not report:
            return None
        stem = lambda s: re.sub(r"\.[A-Za-z0-9_]+$", "", str(s).replace("\\", "/").rsplit("/", 1)[-1]).lower()

        def pick(v):
            if v is None:
                return None
            for a in accepted_values or ():
                if str(a) == v or str(a).lower() == str(v).lower() or stem(a) == stem(v):
                    return a
            return None if accepted_values else v
        if kind == "integer":
            return str(report["counts"][what]) if what in report["counts"] else None
        if kind == "ordered_tokens":
            ch = report.get("member_chain" if what == "member_chain" else "chain")
            return sep.join(ch) if ch else None
        if kind == "enum":
            if what in ("root", "leaf"):
                return pick(report[what])
            if what in ("root_language", "leaf_language"):
                ch = report.get("chain")
                return pick(ch[0 if what == "root_language" else -1]) if ch else None
            if what.startswith("unique_"):
                ms = report["unique"].get(what[len("unique_"):]) or []
                return pick(ms[0]) if len(ms) == 1 else None
            return None
        end, _, fld = what.partition(".")
        m = report.get(end) if end in ("root", "leaf") else None
        g = report["members"].get(m) if m else None
        if not g:
            return None
        vals = ([v for _, v in g["urls"]] if fld == "url" else g["hosts"] if fld == "host" else
                g["file_paths"] if fld == "file_path" else [g.get(fld)] if g.get(fld) else [])
        return vals[0] if len(vals) == 1 else None
    except Exception:  # noqa: BLE001
        return None


# --- declared (static) process tree: who the source says spawns whom ------------------------------------------------
# parent = the member's host interpreter (host_profile first, then language, then file extension); plan edges come from
# next_language when the steps dispatch a process / language / script; code edges from the spawn call sites in the
# member's own CODE, with arguments rebuilt by the fetch_sites literal folder (_fs_env / _fs_eval).
PT_LANG_IMAGE = {
    "jscript": "wscript.exe", "vbscript": "wscript.exe", "wsf": "wscript.exe", "jse": "wscript.exe",
    "vbe": "wscript.exe", "wsh": "wscript.exe", "hta": "mshta.exe", "batch": "cmd.exe", "cmd": "cmd.exe",
    "bat": "cmd.exe", "powershell": "powershell.exe", "pwsh": "pwsh.exe", "python": "python.exe",
    "javascript": "node.exe", "node": "node.exe", "nodejs": "node.exe", "typescript": "node.exe", "perl": "perl.exe",
    "ruby": "ruby.exe", "lua": "lua.exe", "php": "php.exe", "auto_hotkey": "AutoHotkey64.exe",
    "autohotkey": "AutoHotkey64.exe", "ahk": "AutoHotkey64.exe", "autoit": "AutoIt3.exe", "au3": "AutoIt3.exe",
    "applescript": "osascript", "msbuild_xml": "MSBuild.exe", "msbuild": "MSBuild.exe", "sct": "regsvr32.exe",
    "scriptlet": "regsvr32.exe", "wmi_mof": "scrcons.exe", "mof": "scrcons.exe", "bash": "bash", "sh": "sh",
    "zsh": "zsh", "tcl": "tclsh", "google_apps_script": "apps_script", "xsl": "msxsl.exe", "xslt": "msxsl.exe",
}
PT_EXT_LANG = {
    "js": "jscript", "jse": "jscript", "vbs": "vbscript", "vbe": "vbscript", "wsf": "wsf", "hta": "hta",
    "bat": "batch", "cmd": "batch", "ps1": "powershell", "psm1": "powershell", "psd1": "powershell", "py": "python",
    "pyw": "python", "mjs": "javascript", "cjs": "javascript", "ts": "typescript", "pl": "perl", "pm": "perl",
    "rb": "ruby", "lua": "lua", "php": "php", "ahk": "auto_hotkey", "au3": "autoit", "applescript": "applescript",
    "scpt": "applescript", "proj": "msbuild_xml", "csproj": "msbuild_xml", "targets": "msbuild_xml", "sct": "sct",
    "mof": "wmi_mof", "sh": "bash", "bash": "bash", "zsh": "zsh", "gs": "google_apps_script", "tcl": "tcl",
    "xsl": "xsl", "exe": None,
}
PT_HOST_IMAGE = (   # host_profile (prefix / pattern) -> the process that hosts the member
    (r"^wsf|^wsh|^wscript", "wscript.exe"), (r"^cscript", "cscript.exe"), (r"^hta|mshta", "mshta.exe"),
    (r"^sct|scriptlet|regsvr32", "regsvr32.exe"), (r"php[_-]?(?:webshell|cgi|fpm)", "php-cgi.exe"),
    (r"perl[_-]?cgi", "perl.exe"), (r"ruby[_-]?rack", "ruby.exe"), (r"openresty|nginx", "nginx.exe"),
    (r"google|apps?_?script|sidebar", "apps_script"), (r"msbuild", "MSBuild.exe"),
    (r"wmi|mof", "scrcons.exe"), (r"office|vba|macro|word|excel", "winword.exe"),
)
_PT_DISPATCH = re.compile(r"(?i)^(?:dispatch_(?:process|language|next_stage|script)|handoff_\w+|launch_\w+|"
                          r"execute_(?:process|stage|file)|spawn_\w+|run_(?:process|stage|file))$")
_PT_EXE = re.compile(r"""(?i)^\s*["']?((?:[A-Za-z]:)?[^\s"'|&;<>]*?([^\\/\s"'|&;<>]+))["']?(?:\s|$)""")
_PT_SITES = (   # (api, regex, kind, source gate) kind: call (first arg = cmdline), se (file + args), cmd (rest of line)
    ("WScript.Shell.Run", re.compile(r"(?i)\.Run\s*\(?"), "call", "wscript.shell"),
    ("WScript.Shell.Exec", re.compile(r"(?i)\.Exec\s*\(?"), "call", "wscript.shell"),
    ("ShellExecute", re.compile(r"(?i)\bShellExecute(?:Wait)?\s*\(?"), "se", ""),
    ("Win32_Process.Create", re.compile(r"(?i)\.Create\s*\("), "call", "win32_process"),
    ("Start-Process", re.compile(r"(?i)(?:^|(?<=[\s;|({]))(?:Start-Process|saps)\b"), "ps", ""),
    ("child_process", re.compile(r"\b(?:spawnSync|spawn|execFileSync|execFile|execSync|exec|fork)\s*\("), "call",
     "child_process"),
    ("subprocess", re.compile(r"\bsubprocess\.(?:run|call|Popen|check_call|check_output|getoutput)\s*\("), "call", ""),
    ("os.system", re.compile(r"\bos\.(?:system|popen|startfile|exec[lv]p?e?|spawn[lv]p?e?)\s*\("), "call", ""),
    ("os.execute", re.compile(r"\b(?:os\.execute|io\.popen)\s*\("), "call", ""),
    ("system", re.compile(r"(?<![\w.$>:])(?:system|exec|shell_exec|passthru|popen|proc_open|spawn|IO\.popen|"
                          r"Open3\.\w+)\s*\(?(?=\s*[\"'(\[$@%])"), "call", ""),
    ("qx", re.compile(r"(?<![\w$@%])(?:qx|%x)\s*([{(\[<|/!])"), "qx", ""),
    ("backticks", re.compile(r"(?<![\w\\])`(?=[^`\n]*\b(?:cmd|powershell|pwsh|cscript|wscript|mshta|python|node|perl|"
                             r"ruby|bash|sh|curl|wget)\b)"), "bt", ""),
    ("Run", re.compile(r"(?im)^\s*(?:\w+\s*:?=\s*)?Run(?:Wait)?\b\s*[,(]?"), "call", ""),
    ("do shell script", re.compile(r"(?i)\bdo\s+shell\s+script\s+"), "call", ""),
    ("MSBuild.Exec", re.compile(r"""(?i)<Exec\b[^>]*?\bCommand\s*=\s*(?=["'])"""), "call", ""),
    ("cmd /c", re.compile(r"(?i)(?:^|(?<=[\s(;&|@]))cmd(?:\.exe)?\s+(?=/[ckCK]\b)"), "cmd", ""),
    ("start", re.compile(r"(?im)^\s*@?start\s+"), "cmd", ""),
    ("schtasks /create", re.compile(r"(?i)\bschtasks(?:\.exe)?\s+(?=/create\b)"), "cmd", ""),
    ("wmic process call create", re.compile(r"(?i)\bwmic(?:\.exe)?\s+(?=process\s+call\s+create\b)"), "cmd", ""),
)
_PT_INTERP_LINE = re.compile(r"(?im)^\s*@?(?:call\s+)?(?P<img>(?:[\w.\\:/-]*[\\/])?(?:powershell|pwsh|cscript|wscript|"
                             r"mshta|rundll32|regsvr32|msbuild|python3?|node|perl|ruby|lua|php|osascript|bash|sh)"
                             r"(?:\.exe)?)\s+(?=\S)")


_PT_SHELLWIN = re.compile(r"(?i)\bShell(?:Windows|BrowserWindow)\b|9BA05972-F6A8-11CF-A442-00A0C90A8F39|"
                          r"C08AFD90-F2A1-11D1-8455-00A0C91F3880")
_PT_PROXY_GATE = re.compile(r"(?i)ExecuteShellCommand|\bsc(?:\.exe)?\s+(?:\\\\\S+\s+)?create\b|New-Service|"
                            r"New-ScheduledTaskAction|CommandLineTemplate")


def pt_image(language=None, host_profile=None, member=""):
    """Host process image for a member: host_profile pattern, else language, else the file extension; None unknown."""
    hp = str(host_profile or "").strip().lower()
    if hp and hp not in ("standalone", "none", "native", "local", "default"):
        for rx, img in PT_HOST_IMAGE:
            if re.search(rx, hp):
                return img
        for tok in re.split(r"[_\-\s]+", hp):
            if tok in PT_LANG_IMAGE and tok not in ("javascript", "jscript", "vbscript", "mixed"):
                return PT_LANG_IMAGE[tok]
    lang = re.sub(r"[^0-9a-z]+", "_", str(language or "").strip().lower()).strip("_")
    if lang in PT_LANG_IMAGE:
        return PT_LANG_IMAGE[lang]
    ext = str(member or "").rsplit(".", 1)[-1].lower() if "." in str(member or "") else ""
    lang = PT_EXT_LANG.get(ext)
    return PT_LANG_IMAGE.get(lang) if lang else None


def _pt_child(cmdline):
    """First program of a command line -> its image (a script path maps to its host interpreter)."""
    m = _PT_EXE.match(cmdline or "")
    if not m:
        return None
    base = m.group(2).strip().rstrip(",)")
    if not base or not re.search(r"[A-Za-z]", base):
        return None
    ext = base.rsplit(".", 1)[-1].lower() if "." in base else ""
    if ext in PT_EXT_LANG and ext != "exe" and PT_EXT_LANG[ext]:
        return PT_LANG_IMAGE.get(PT_EXT_LANG[ext])
    low = base.lower()
    if not ext and low in ("powershell", "pwsh", "cscript", "wscript", "mshta", "cmd", "rundll32", "regsvr32",
                           "msbuild", "schtasks", "wmic", "msiexec", "certutil", "bitsadmin", "python", "node"):
        return low + ".exe"
    return base


def _pt_in_string(line, col):
    """True when column `col` of `line` sits inside a quoted literal (crude, per line)."""
    q = None
    i = 0
    while i < col and i < len(line):
        c = line[i]
        if q:
            if c == "\\" and q != "'":
                i += 1
            elif c == q:
                q = None
        elif c in "\"'":
            q = c
        i += 1
    return q is not None


def _pt_value(expr, env, text):
    """Rebuild one argument: the full folded literal, else the head literal of the variable's first assignment."""
    expr = (expr or "").strip()
    v = _fs_eval(expr, env)
    if v is not None:
        return v, True
    head = re.match(r"[$@%]?\{?([A-Za-z_]\w*)", expr)
    if head:
        am = re.search(r"(?m)(?:^|[\s;(,])[$]?" + re.escape(head.group(1)) + r"\s*(?::=|=)(?!=)\s*", text)
        if am:
            lm = _FS_LIT.match(text, am.end())
            if lm:
                lit = lm.group("d") if lm.group("d") is not None else lm.group("s") if lm.group("s") is not None \
                    else lm.group("t")
                return _fs_unescape(lit or ""), False
    lm = _FS_LIT.match(expr)
    if lm:
        lit = lm.group("d") if lm.group("d") is not None else lm.group("s") if lm.group("s") is not None \
            else lm.group("t")
        return _fs_unescape(lit or ""), False
    return None, False


def _pt_ps_args(args, env, text):
    """Start-Process [-FilePath] X [-ArgumentList] Y -> 'X Y'."""
    toks = _fs_split(args, re.compile(r"\s+")) or []
    named, pos, i = {}, [], 0
    while i < len(toks):
        t = toks[i]
        if t.startswith("-") and re.fullmatch(r"-\w+", t):
            n = t[1:].lower()
            if n in ("wait", "nonewwindow", "passthru", "usenewenvironment") or i + 1 >= len(toks):
                i += 1
                continue
            named[n] = toks[i + 1]
            i += 2
            continue
        pos.append(t)
        i += 1
    fp = next((named[k] for k in named if "filepath".startswith(k) or k in ("path", "fp")), pos[0] if pos else None)
    al = next((named[k] for k in named if "argumentlist".startswith(k) or k == "args"), pos[1] if len(pos) > 1 else None)
    f, ok = _pt_value(fp, env, text) if fp else (None, False)
    if f is None:
        return None, False
    if al:
        if "," in al and al.strip()[:2] != "@(":
            parts = [_pt_value(p, env, text) for p in (_fs_split(al, _FS_COMMA) or [al])]
            a = " ".join(p for p, _ in parts if p is not None)
            ok = ok and all(o for _, o in parts)
        else:
            a, o = _pt_value(re.sub(r"^@\((.*)\)$", r"\1", al.strip(), flags=re.S), env, text)
            ok = ok and o
        return f + (" " + a if a else ""), ok
    return f, ok


def code_spawns(src, name="", parent=None):
    """Process-creation call sites in a script's CODE -> [{api, parent_image, child_image, cmdline, line, folded}] in
    source order. `cmdline` is rebuilt from the file's own literals (None when runtime data); `folded` False when only
    the head literal was recovered. Comment / echo lines and call heads inside string literals are skipped; a
    Win32_Process.Create / wmic / schtasks /tr child is parented to WmiPrvSE.exe / svchost.exe (plus the member ->
    wmic.exe / schtasks.exe edge). [] for unreadable input."""
    try:
        if isinstance(src, (bytes, bytearray)):
            b = bytes(src)
            src = (b.decode("utf-16", "replace") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else
                   b.decode("utf-8-sig", "replace"))
        text = _fs_flat(str(src or "")[:1_000_000])
        low = text.lower()
        if not parent and re.search(r"\brequire\s*\(|\bchild_process\b|^\s*import\s.+\bfrom\s", text, re.M) and \
                str(name or "").lower().endswith((".js", ".mjs", ".cjs", ".ts")):
            parent = "node.exe"
        parent = parent or pt_image(member=name)
        env = _fs_env(text)
        lines = text.split("\n")
        starts = [0]
        for ln in lines:
            starts.append(starts[-1] + len(ln) + 1)
        import bisect
        ext = str(name or "").rsplit(".", 1)[-1].lower()
        out, seen = [], set()

        def add(api, par, cmd, lno, folded, child=None):
            child = child or _pt_child(cmd)
            if not child:
                return
            key = (lno, child.lower(), api)
            if key in seen:
                return
            seen.add(key)
            out.append({"api": api, "parent_image": par, "child_image": child,
                        "cmdline": cmd.strip() if cmd and folded else None, "line": lno, "folded": bool(folded)})

        sites = list(_PT_SITES)
        if ext in ("bat", "cmd") or parent == "cmd.exe":
            sites.append(("direct", _PT_INTERP_LINE, "cmd", ""))
        for api, rx, kind, gate in sites:
            if gate and gate not in low:
                continue
            for m in rx.finditer(text):
                if len(out) > 200:
                    break
                lno = bisect.bisect_right(starts, m.start())
                line = lines[lno - 1]
                col = m.start() - starts[lno - 1]
                if _FS_COMMENT.match(line) or _FS_ECHO.match(line) and kind != "cmd":
                    continue
                if kind not in ("qx", "bt") and _pt_in_string(line, col) and not (
                        kind == "cmd" and ext in ("bat", "cmd")):
                    continue
                if api == "Run" and not (ext in ("ahk", "au3") or "autoit" in low or "#requires autohotkey" in low):
                    continue
                if api == "system" and ext in ("js", "mjs", "cjs", "ts", "ps1", "vbs") and "child_process" not in low:
                    continue
                cmd, folded = None, False
                if kind == "qx":
                    close = {"{": "}", "(": ")", "[": "]", "<": ">"}.get(m.group(1), m.group(1))
                    j = text.find(close, m.end())
                    if j < 0 or "\n" in text[m.end():j]:
                        continue
                    cmd, folded = text[m.end():j], True
                elif kind == "bt":
                    j = text.find("`", m.end())
                    if j < 0:
                        continue
                    cmd, folded = text[m.end():j], True
                elif kind == "cmd":
                    rest = line[col + (m.end() - m.start()):]
                    rest = re.sub(r"%(\w+)%|!(\w+)!", lambda mm: _fs_lookup(mm.group(1) or mm.group(2), env)
                                  or mm.group(0), rest).strip()
                    if api == "direct":
                        cmd, folded = m.group("img") + " " + rest, True
                        add(api, parent, cmd, lno, folded)
                        continue
                    if api == "cmd /c":
                        add(api, parent, "cmd.exe " + rest, lno, True, child="cmd.exe")
                        continue
                    if api == "start":
                        rest = re.sub(r'^(?:"[^"]*"\s+)?(?:/\w+\s+)*', "", rest)
                        add(api, parent, rest, lno, True)
                        continue
                    if api == "schtasks /create":
                        add(api, parent, "schtasks.exe " + rest, lno, True, child="schtasks.exe")
                        tm = re.search(r"""(?i)/tr\s+(?:"((?:[^"\\]|\\.)*)"|'([^']*)'|(\S+))""", rest)
                        if tm:
                            tr = (tm.group(1) or tm.group(2) or tm.group(3) or "").replace('\\"', '"')
                            add("schtasks /tr", "svchost.exe", tr, lno, True)
                        continue
                    if api == "wmic process call create":
                        add(api, parent, "wmic.exe " + rest, lno, True, child="wmic.exe")
                        cm = re.search(r"""(?i)\bcreate\s+(?:"((?:[^"\\]|\\.)*)"|'([^']*)'|(\S+))""", rest)
                        if cm:
                            add("Win32_Process.Create", "WmiPrvSE.exe", cm.group(1) or cm.group(2) or cm.group(3),
                                lno, True)
                        continue
                    continue
                else:
                    args = _fs_args(text, m.end())
                    if args is None:
                        continue
                    if kind == "ps":
                        cmd, folded = _pt_ps_args(args, env, text)
                    else:
                        items = _fs_split(args, _FS_COMMA) or [args]
                        if api == "child_process" and items and items[0].strip()[:1] in "[":
                            items = [items[0].strip()[1:]]
                        if api in ("subprocess", "system", "os.system") and items and items[0].strip()[:1] == "[":
                            inner = items[0].strip()[1:].rsplit("]", 1)[0]
                            parts = [_pt_value(p, env, text) for p in (_fs_split(inner, _FS_COMMA) or [inner])]
                            if parts and parts[0][0] is not None:
                                cmd = " ".join(p for p, _ in parts if p is not None)
                                folded = all(o for _, o in parts)
                        if cmd is None and items:
                            cmd, folded = _pt_value(items[0], env, text)
                        if api == "child_process" and cmd is not None and len(items) > 1 and \
                                items[1].strip()[:1] == "[":
                            inner = items[1].strip()[1:].rsplit("]", 1)[0]
                            parts = [_pt_value(p, env, text) for p in (_fs_split(inner, _FS_COMMA) or [inner])]
                            cmd += "".join(" " + p for p, _ in parts if p is not None)
                            folded = folded and all(o for _, o in parts)
                        if kind == "se" and cmd is not None and len(items) > 1:
                            a, o = _pt_value(items[1], env, text)
                            if a:
                                cmd, folded = cmd + " " + a, folded and o
                if cmd is None:
                    continue
                if api == "child_process" and re.search(r"\bfork\s*\($", text[m.start():m.end()]):
                    add(api, parent, "node.exe " + cmd, lno, folded, child="node.exe")
                    continue
                if api == "Win32_Process.Create":
                    add(api, "WmiPrvSE.exe", cmd, lno, folded)
                    continue
                if api == "ShellExecute" and _PT_SHELLWIN.search(text):
                    add("ShellWindows.ShellExecute", "explorer.exe", cmd, lno, folded)
                    continue
                add(api, parent, cmd, lno, folded)
        if _PT_PROXY_GATE.search(text):
            _pt_proxy_edges(text, lines, starts, add)
        out.sort(key=lambda d: d["line"])
        return out
    except Exception:  # noqa: BLE001
        return []


def declared_spawns(plans_by_member, sources=None):
    """Static process tree from plans + sources -> [{member, parent_image, child_image, cmdline, api, line, source}].
      plan edges   (source 'plan', line None): host image (pt_image(language, host_profile, member)) -> the
                   next_language interpreter when the plan's steps dispatch (dispatch_process / dispatch_language /
                   handoff_script / dispatch_next_stage ...); cmdline = next_stage / file_path when the plan names one;
                   api = the dispatching step
      code edges   (source 'code'): code_spawns(sources[member]) with the member's host image as parent
    plans_by_member {member: plan dict / 'k=v|..' / JSON}; sources {member: text/bytes} (optional; members with a
    source but no plan still get their code edges). [] when nothing declares a spawn."""
    try:
        out = []
        plans_by_member = plans_by_member or {}
        sources = sources or {}
        for m in sorted(set(plans_by_member) | set(sources)):
            d = {}
            if m in plans_by_member:
                try:
                    d = {_rc_field(k): v for k, v in _rc_dict(plans_by_member[m]).items()}
                except Exception:  # noqa: BLE001
                    d = {}
            steps = d.get("steps") or ""
            steps = [str(s) for s in steps] if isinstance(steps, (list, tuple)) else \
                [s for s in re.split(r"[\s,;>|]+", str(steps)) if s]
            parent = pt_image(d.get("language"), d.get("host_profile"), m)
            nl = str(d.get("next_language") or "").strip()
            disp = [s for s in steps if _PT_DISPATCH.match(s)]
            if nl and disp and nl.lower() not in ("none", "null", "n/a"):
                child = pt_image(nl) or nl
                tgt = next((str(d[k]) for k in ("next_stage", "file_path", "path", "drop_path") if d.get(k)), None)
                out.append({"member": m, "parent_image": parent, "child_image": child,
                            "cmdline": f"{child} {tgt}" if tgt else None, "api": disp[-1], "line": None,
                            "source": "plan"})
            if m in sources:
                for s in code_spawns(sources[m], m, parent):
                    out.append({"member": m, "parent_image": s["parent_image"], "child_image": s["child_image"],
                                "cmdline": s["cmdline"], "api": s["api"], "line": s["line"], "source": "code"})
        return out
    except Exception:  # noqa: BLE001
        return []


# --- spawn-API proxy parents: the parent telemetry records for a spawn API is the OS broker, not the caller ----------
PT_SPAWN_PARENTS = (  # (key, api aliases (alnum, lower), code cue, recorded parent images in order, ATT&CK candidates)
    ("wmi_process_create", ("win32processcreate", "wmicprocesscallcreate", "wmic", "invokewmimethod",
                            "invokecimmethod", "win32process", "wmiprocess"),
     r"Win32_Process\b|\bwmic(?:\.exe)?\b[^\n]{0,80}?\bprocess\s+call\s+create|Invoke-(?:Wmi|Cim)Method\b",
     ("WmiPrvSE.exe",), ("T1047",)),
    ("wmi_script_consumer", ("activescripteventconsumer", "scrcons"), r"ActiveScriptEventConsumer\b",
     ("scrcons.exe",), ("T1546.003",)),
    ("wmi_cmdline_consumer", ("commandlineeventconsumer", "commandlinetemplate"), r"CommandLineEventConsumer\b",
     ("WmiPrvSE.exe",), ("T1546.003",)),
    ("wmi_event_subscription", ("eventconsumer", "eventfilter", "filtertoconsumerbinding", "wmievent",
                                "wmisubscription", "wmipersistence"),
     r"__EventFilter\b|__FilterToConsumerBinding\b", ("scrcons.exe", "WmiPrvSE.exe"), ("T1546.003",)),
    ("scheduled_task", ("schtasks", "scheduledtask", "newscheduledtaskaction", "schedulesservice", "itaskservice",
                        "taskscheduler", "schtr"),
     r"\bschtasks(?:\.exe)?\b[^\n]{0,60}?/create\b|\b(?:Register|New)-ScheduledTask(?:Action)?\b|"
     r"\bSchedule\.Service\b|\bITaskService\b", ("svchost.exe", "taskeng.exe"), ("T1053.005",)),
    ("mmc20", ("mmc20", "executeshellcommand", "mmc"),
     r"\bMMC20\.Application\b|49B2791A-B1AE-4C90-9B8E-E860BA07F889|\.ExecuteShellCommand\b",
     ("mmc.exe",), ("T1021.003", "T1559.001")),
    ("shell_windows", ("shellwindows", "shellbrowserwindow"),
     r"\bShell(?:Windows|BrowserWindow)\b|9BA05972-F6A8-11CF-A442-00A0C90A8F39|C08AFD90-F2A1-11D1-8455-00A0C91F3880",
     ("explorer.exe",), ("T1021.003", "T1559.001")),
    ("service", ("sccreate", "newservice", "createservice", "servicecreate", "servicesexe", "binpath"),
     r"\bsc(?:\.exe)?\s+(?:\\\\\S+\s+)?create\b|\bNew-Service\b|\bCreateService[AW]?\b|\bWin32_Service\b[^\n]{0,80}"
     r"\bCreate\b", ("services.exe",), ("T1543.003",)),
    ("winlogon", ("winlogon", "userinit", "winlogonshell"),
     r"\\Winlogon\b[^\n]{0,120}?\b(?:Userinit|Shell)\b", ("userinit.exe", "winlogon.exe"), ("T1547.004",)),
    ("run_key", ("runkey", "currentversionrun", "runonce", "registryrun", "autorun"),
     r"\\CurrentVersion\\+Run(?:Once)?(?:Ex)?\b", ("explorer.exe", "userinit.exe"), ("T1547.001",)),
    ("office_macro", ("macro", "vba", "office", "winword", "excel", "outlook", "powerpnt", "autoopen",
                      "documentopen", "workbookopen"),
     r"\b(?:Auto_?Open|AutoExec|Document_Open|Workbook_Open|Application_Startup|Application_NewMail(?:Ex)?)\b|"
     r"\b(?:Word|Excel|Outlook|PowerPoint)\.Application\b",
     ("WINWORD.EXE", "EXCEL.EXE", "OUTLOOK.EXE", "POWERPNT.EXE"), ("T1204.002",)),
    # LOLBin hosts: only a hosting cue (the script runs INSIDE it), not a plain launch of the binary
    ("mshta", ("mshta", "hta"), r"<HTA:APPLICATION\b|\bmshta(?:\.exe)?\s+(?:vbscript|javascript):",
     ("mshta.exe",), ("T1218.005",)),
    ("regsvr32", ("regsvr32", "sct", "scriptlet", "scrobj"),
     r"<scriptlet\b|\bregsvr32(?:\.exe)?\b[^\n]{0,80}?\bscrobj\.dll\b", ("regsvr32.exe",), ("T1218.010",)),
    ("rundll32", ("rundll32",), r"\brundll32(?:\.exe)?\b[^\n]{0,80}?\b(?:javascript:|RunHTMLApplication\b)",
     ("rundll32.exe",), ("T1218.011",)),
    ("cloud_script", ("appsscript", "googleappsscript", "cloud", "urlfetchapp", "serverless", "lambda"),
     r"\b(?:UrlFetchApp|SpreadsheetApp|DriveApp|GmailApp|ScriptApp|PropertiesService)\.", (), ()),
)
_PT_SPAWN_RX = [(k, re.compile("(?i)" + cue)) for k, _, cue, _, _ in PT_SPAWN_PARENTS]
_PT_OFFICE_HINT = (("excel", "EXCEL.EXE"), ("workbook", "EXCEL.EXE"), ("outlook", "OUTLOOK.EXE"),
                   ("application_newmail", "OUTLOOK.EXE"), ("application_startup", "OUTLOOK.EXE"),
                   ("powerpoint", "POWERPNT.EXE"), ("word", "WINWORD.EXE"), ("document_open", "WINWORD.EXE"))
# PPID spoofing (T1134.004): CreateProcess with a parent handle via STARTUPINFOEX + PROC_THREAD_ATTRIBUTE_PARENT_PROCESS
_PPID_CUES = (
    ("UpdateProcThreadAttribute", r"\bUpdateProcThreadAttribute\b"),
    ("PROC_THREAD_ATTRIBUTE_PARENT_PROCESS", r"\bPROC_THREAD_ATTRIBUTE_PARENT_PROCESS\b|"
                                             r"\bUpdateProcThreadAttribute\b[^\n]{0,160}?\b0x0*20000\b|"
                                             r"(?<![\w.])(?:0x0*20000|131072)\b(?![\w.])"),
    ("InitializeProcThreadAttributeList", r"\bInitializeProcThreadAttributeList\b"),
    ("STARTUPINFOEX", r"\bSTARTUPINFOEX[AW]?\b|\bStartupInfoEx\b|\blpAttributeList\b"),
    ("EXTENDED_STARTUPINFO_PRESENT", r"\bEXTENDED_STARTUPINFO_PRESENT\b|(?<![\w.])(?:0x0*80000|524288)\b(?![\w.])"),
    ("PROCESS_CREATE_PROCESS", r"\bPROCESS_CREATE_PROCESS\b|\bOpenProcess\s*\(\s*(?:0x0*80|128)\s*,"),
    ("OpenProcess", r"\bOpenProcess\b"),
    ("CreateProcess", r"\bCreateProcess(?:AsUser)?[AW]?\b"),
)
_PPID_RX = [(n, re.compile("(?i)" + r)) for n, r in _PPID_CUES]
_PPID_TARGET = re.compile(r"""(?i)(?:\bGet-Process\s+(?:-Name\s+)?|\bGetProcessesByName\s*\(\s*|\bgps\s+|"""
                          r"""\bProcessName\s*(?:-eq|==|=)\s*)["']?([A-Za-z][\w.-]{1,40}?)(?:\.exe)?["')\s|;]|"""
                          r"""["']((?:explorer|svchost|lsass|winlogon|services|spoolsv|sihost|taskhostw|dllhost|"""
                          r"""RuntimeBroker|WmiPrvSE|OUTLOOK|WINWORD|EXCEL)\.exe)["']""")


def _pt_key(s):
    return re.sub(r"[^0-9a-z]+", "", str(s or "").lower())


def spawn_parent_candidates(api):
    """Spawn API / launcher name (code_spawns api, 'wmic process call create', 'Register-ScheduledTask',
    'MMC20.Application', 'sc create', 'Run key', 'macro', 'Apps Script' ...) -> the parent images telemetry records
    for its child, most likely first ([] = no local process: cloud script). None when the API is not a proxy (the
    calling script itself is the parent)."""
    try:
        k = _pt_key(api)
        if not k:
            return None
        for key, names, _cue, parents, _att in PT_SPAWN_PARENTS:
            if k == key.replace("_", "") or any(n in k for n in names):
                if key == "office_macro":
                    hint = next((img for h, img in _PT_OFFICE_HINT if h.replace("_", "") in k), None)
                    return ([hint] if hint else []) + [p for p in parents if p != hint]
                return list(parents)
        return None
    except Exception:  # noqa: BLE001
        return None


def spawn_proxies(src):
    """Proxy-launch cues in a script's code -> [{key, cue, line, parents, attack}] in source order (first hit per
    family): the process the telemetry will record as the parent of what this script launches through WMI, the
    Task Scheduler, DCOM (MMC20 / ShellWindows), the SCM, Run keys, Office macros, LOLBin hosts, or [] parents for
    cloud scripts. Comment lines are skipped. [] when nothing proxies."""
    try:
        if isinstance(src, (bytes, bytearray)):
            b = bytes(src)
            src = (b.decode("utf-16", "replace") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else
                   b.decode("utf-8-sig", "replace"))
        text = _fs_flat(str(src or "")[:1_000_000])
        lines = text.split("\n")
        hits = {}
        for key, rx in _PT_SPAWN_RX:
            for lno, ln in enumerate(lines[:50000], 1):
                if len(ln) > 20000 or _FS_COMMENT.match(ln):
                    continue
                m = rx.search(ln)
                if m:
                    hits[key] = (lno, m.start(), m.group(0).strip())
                    break
        if "wmi_event_subscription" in hits and ("wmi_script_consumer" in hits or "wmi_cmdline_consumer" in hits):
            hits.pop("wmi_event_subscription")
        out = []
        for key, names, _cue, parents, att in PT_SPAWN_PARENTS:
            if key not in hits:
                continue
            lno, col, cue = hits[key]
            ps = list(parents)
            if key == "office_macro":
                hint = next((img for h, img in _PT_OFFICE_HINT if h in cue.lower()), None)
                ps = ([hint] if hint else []) + [p for p in parents if p != hint]
            out.append({"key": key, "cue": cue, "line": lno, "parents": ps, "attack": list(att), "_col": col})
        out.sort(key=lambda d: (d["line"], d.pop("_col")))
        return out
    except Exception:  # noqa: BLE001
        return []


def ppid_spoof(src):
    """PPID-spoofing code cues (T1134.004) -> {cues: [names in source order], spoofed_parent: image | None,
    attack: 'T1134.004' | 'none'}. Spoofing = the parent-process attribute (UpdateProcThreadAttribute +
    PROC_THREAD_ATTRIBUTE_PARENT_PROCESS / 0x00020000) or STARTUPINFOEX + EXTENDED_STARTUPINFO_PRESENT (0x00080000)
    with an OpenProcess(PROCESS_CREATE_PROCESS 0x0080) handle. spoofed_parent = the process whose handle is opened
    (Get-Process explorer / GetProcessesByName("svchost") / a quoted '<name>.exe'). {} for unreadable input."""
    try:
        if isinstance(src, (bytes, bytearray)):
            b = bytes(src)
            src = (b.decode("utf-16", "replace") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else
                   b.decode("utf-8-sig", "replace"))
        text = str(src or "")[:1_000_000]
        code = "\n".join(ln for ln in text.split("\n") if not _FS_COMMENT.match(ln))
        found = []
        for name, rx in _PPID_RX:
            m = rx.search(code)
            if m:
                found.append((m.start(), name))
        names = {n for _, n in found}
        attr = "UpdateProcThreadAttribute" in names and "PROC_THREAD_ATTRIBUTE_PARENT_PROCESS" in names
        ext = "STARTUPINFOEX" in names and "EXTENDED_STARTUPINFO_PRESENT" in names and \
            ("PROCESS_CREATE_PROCESS" in names or "UpdateProcThreadAttribute" in names)
        spoof = (attr or ext) and ("CreateProcess" in names or "STARTUPINFOEX" in names)
        par = None
        if spoof:
            for m in _PPID_TARGET.finditer(code):
                v = m.group(1) or m.group(2)
                if v and v.lower() not in ("id", "name", "handle", "process", "processname"):
                    par = v if v.lower().endswith(".exe") else v + ".exe"
                    break
        return {"cues": [n for _, n in sorted(found)], "spoofed_parent": par,
                "attack": "T1134.004" if spoof else "none"}
    except Exception:  # noqa: BLE001
        return {}


def spawn_parent_answer(src, kind="parent", plan=None, accepted_values=None):
    """Answer 'which process will the telemetry record as the parent' / 'which technique' for a script.
    kind: parent (expected recorded parent: the spoofed parent, else the proxy parents in order) | attack (plan
    attack= wins; else T1134.004 when the code spoofs its PPID, else the proxy family's techniques) | family.
    Candidates in order (a list when several); the matching accepted value when given. 'none' when the code has no
    proxy / spoof cue (or a cloud script runs no local process), None on error."""
    try:
        kd = _pt_key(kind)
        acc = [a for a in (accepted_values or []) if str(a).strip()] or None
        sp = ppid_spoof(src) or {}
        px = spawn_proxies(src)
        if any(a in kd for a in ("attack", "technique", "mitre", "ttp")):
            pa = None
            if plan is not None:
                try:
                    pa = str({_rc_field(k): v for k, v in _rc_dict(plan).items()}.get("attack") or "").strip()
                except Exception:  # noqa: BLE001
                    pa = None
            vals = [pa.upper()] if pa and pa.lower() not in ("none", "null", "n/a") else []
            if sp.get("attack") == "T1134.004":
                vals.append("T1134.004")
            for p in px:
                vals += p["attack"]
        elif "famil" in kd or "key" in kd or "method" in kd:
            vals = [p["key"] for p in px]
        else:
            vals = [sp["spoofed_parent"]] if sp.get("spoofed_parent") else []
            for p in px:
                vals += p["parents"]
        seen = []
        for v in vals:
            if v and v.lower() not in [s.lower() for s in seen]:
                seen.append(v)
        if acc:
            seen = [next(a for a in acc if str(a).strip().lower() == v.lower() or
                         _rcp_base(a) == _rcp_base(v)) for v in seen
                    if any(str(a).strip().lower() == v.lower() or _rcp_base(a) == _rcp_base(v) for a in acc)]
        if not seen:
            return "none"
        return seen[0] if len(seen) == 1 else seen
    except Exception:  # noqa: BLE001
        return None


def _pt_proxy_edges(text, lines, starts, add):
    """Code sites whose child the OS parents to a broker: MMC20 ExecuteShellCommand -> mmc.exe, sc create binPath= /
    New-Service -BinaryPathName -> services.exe, New-ScheduledTaskAction -Execute -> svchost.exe, a WMI
    CommandLineEventConsumer CommandLineTemplate -> WmiPrvSE.exe."""
    import bisect
    env = None
    lit = r"""(?:"((?:[^"\\]|\\.)*)"|'([^']*)'|([^\s;,)}]+))"""
    for api, rx, par in _PT_PROXY_SITES:
        for m in rx.finditer(text):
            lno = bisect.bisect_right(starts, m.start())
            line = lines[lno - 1]
            if _FS_COMMENT.match(line) or _FS_ECHO.match(line):
                continue
            if api == "MMC20.ExecuteShellCommand":
                args = _fs_args(text, m.end())
                items = _fs_split(args or "", _FS_COMMA) or []
                if not items:
                    continue
                env = env if env is not None else _fs_env(text)
                c, ok = _pt_value(items[0], env, text)
                if c is None:
                    continue
                if len(items) > 2:
                    a, o = _pt_value(items[2], env, text)
                    c, ok = (c + " " + a, ok and o) if a else (c, ok)
                add(api, par, c, lno, ok)
                continue
            rest = text[m.end():starts[lno] if lno < len(starts) else len(text)]
            if api == "New-ScheduledTaskAction":
                em = re.search(r"(?i)-Execute\s+" + lit, rest)
                if not em:
                    continue
                am = re.search(r"(?i)-Argument\s+" + lit, rest)
                pick = lambda mm: next(g for g in mm.groups() if g is not None)  # noqa: E731
                c = pick(em).replace('\\"', '"') + (" " + pick(am).replace('\\"', '"') if am else "")
                add(api, par, c, lno, True)
                continue
            lm = re.match(lit, rest)
            if not lm:
                continue
            c = next(g for g in lm.groups() if g is not None)
            c = c.replace('\\"', '"').replace("\\\\", "\\") if lm.group(1) is not None else c
            add(api, par, c, lno, True)


_PT_PROXY_SITES = (
    ("MMC20.ExecuteShellCommand", re.compile(r"(?i)\.ExecuteShellCommand\s*\(?"), "mmc.exe"),
    ("sc create", re.compile(r"(?i)\bsc(?:\.exe)?\s+(?:\\\\\S+\s+)?create\s+\S+[^\n]*?\bbinpath=\s*"), "services.exe"),
    ("New-Service", re.compile(r"(?i)\bNew-Service\b[^\n]*?-BinaryPathName\s+"), "services.exe"),
    ("New-ScheduledTaskAction", re.compile(r"(?i)\bNew-ScheduledTaskAction\b"), "svchost.exe"),
    ("CommandLineEventConsumer", re.compile(r"(?i)\bCommandLineTemplate\s*[=:]\s*"), "WmiPrvSE.exe"),
)


# --- process-tree-reconcile: declared (static) vs observed process tree; PPID spoofing (T1134.004) ---------------------
def _rcp_base(img):
    """Image -> comparable basename: last path part, lower, quotes / trailing '.exe' dropped ('' when unknown)."""
    b = _pt_base(str(img or "").strip().strip("\"'")).lower()
    return b[:-4] if b.endswith(".exe") else b


def _rcp_canon(cmd):
    """Command line -> matching form: first token reduced to its image basename, cmd carets / doubled quotes gone,
    quotes stripped, whitespace collapsed, lower-case ('' when absent)."""
    s = str(cmd or "").strip().replace("^", "").replace('""', '"')
    m = re.match(r'\s*(?:"([^"]+)"|(\S+))(.*)$', s, re.S)
    if not m:
        return ""
    head = _rcp_base(m.group(1) or m.group(2))
    return re.sub(r"\s+", " ", (head + " " + m.group(3).replace('"', "").replace("'", "")).strip().lower())


def _rcp_procs(observed):
    """process_events() starts merged per real process: a Sysmon EID 1 and a Security 4688 record of the same pid +
    image (within 5 s) are one process; the 4688 creator ProcessId then rides along as the creator."""
    evs = observed if isinstance(observed, list) else process_events(observed)
    starts = [e for e in evs if isinstance(e, dict) and e.get("event") == "start"][:50000]
    ends = [e for e in evs if isinstance(e, dict) and e.get("event") == "end"][:50000]
    procs = []
    for i, e in enumerate(starts):
        t = _pt_ts(e.get("ts"))
        hit = None
        for p in procs:
            if p["pid"] is not None and p["pid"] == e.get("pid") and \
                    _rcp_base(p["image"]) == _rcp_base(e.get("image")) and \
                    (p["t"] is None or t is None or abs(p["t"] - t) <= 5) and e.get("src") not in p["srcs"]:
                hit = p
                break
        if hit is None:
            hit = {"pid": e.get("pid"), "pid_raw": e.get("pid_raw"), "image": e.get("image"), "t": t, "i": i,
                   "cmdline": e.get("cmdline"), "guid": _pt_guid(e.get("guid")), "srcs": [], "rec_ppid": None,
                   "rec_ppid_raw": None, "rec_pimage": None, "rec_pguid": None, "creator": None, "creator_raw": None,
                   "creator_guid": None, "creator_image": None, "end": None}
            procs.append(hit)
        hit["srcs"].append(e.get("src"))
        hit["cmdline"] = hit["cmdline"] or e.get("cmdline")
        hit["guid"] = hit["guid"] or _pt_guid(e.get("guid"))
        if e.get("src") == "security" and len(hit["srcs"]) > 1:      # 4688 next to a Sysmon record: the creator
            hit["creator"], hit["creator_raw"] = e.get("ppid"), e.get("ppid_raw")
            hit["creator_image"] = hit["creator_image"] or e.get("parent_image")
            continue
        if e.get("src") != "security" and hit["rec_ppid"] is not None and hit["srcs"][0] == "security":
            hit["creator"], hit["creator_raw"] = hit["rec_ppid"], hit["rec_ppid_raw"]  # 4688 came first
            hit["creator_image"] = hit["creator_image"] or hit["rec_pimage"]
            hit["rec_ppid"] = hit["rec_pimage"] = None
        if hit["rec_ppid"] is None:
            hit["rec_ppid"], hit["rec_ppid_raw"] = e.get("ppid"), e.get("ppid_raw")
            hit["rec_pimage"], hit["rec_pguid"] = e.get("parent_image"), _pt_guid(e.get("parent_guid"))
        if e.get("creator_pid") is not None:
            hit["creator"], hit["creator_raw"] = e["creator_pid"], e.get("creator_pid_raw")
        hit["creator_guid"] = hit["creator_guid"] or _pt_guid(e.get("creator_guid"))
        hit["creator_image"] = hit["creator_image"] or e.get("creator_image")
    for e in ends:
        t, g = _pt_ts(e.get("ts")), _pt_guid(e.get("guid"))
        for p in reversed(procs):
            if p["end"] is None and ((g and p["guid"] == g) or (not g and p["pid"] == e.get("pid"))) and \
                    (t is None or p["t"] is None or p["t"] <= t):
                p["end"] = t
                break
    return procs


def _rcp_resolve(procs, me, pid=None, guid=None):
    """The process a parent reference names at `me`'s start: guid first, else the pid alive then. None unknown."""
    if guid:
        hit = next((p for p in procs if p is not me and p["guid"] == guid), None)
        if hit:
            return hit
    if pid is None:
        return None
    t = me["t"]
    cands = [p for p in procs if p is not me and p["pid"] == pid and
             (t is None or p["t"] is None or p["t"] <= t) and (t is None or p["end"] is None or p["end"] >= t)]
    return cands[-1] if cands else None


def _rcp_proxy_ok(d, rec):
    """A declared row launched through a broker API (its `api` / `proxy_parents`) whose recorded parent is that
    broker (WmiPrvSE.exe for Win32_Process.Create, svchost.exe / taskeng.exe for a task ...) is not a mismatch."""
    src = d.get("src") or {}
    cands = src.get("proxy_parents") or spawn_parent_candidates(src.get("api")) or []
    return _rcp_base(rec) in {_rcp_base(c) for c in cands}


def _rcp_declared(declared):
    """declared_spawns() rows / {child: parent} / (parent, child[, cmdline]) tuples -> [{parent, child, cmdline}]."""
    out = []
    if isinstance(declared, dict):
        declared = [{"parent_image": v, "child_image": k} for k, v in declared.items()]
    for d in list(declared or [])[:5000]:
        if isinstance(d, dict):
            c = d.get("child_image") or d.get("child") or d.get("image")
            p = d.get("parent_image") or d.get("parent")
            cl = d.get("cmdline")
        elif isinstance(d, (list, tuple)) and len(d) >= 2:
            p, c, cl = d[0], d[1], (d[2] if len(d) > 2 else None)
        else:
            continue
        if c:
            out.append({"parent": p, "child": c, "cmdline": cl, "src": d if isinstance(d, dict) else None})
    return out


def reconcile_processes(declared, observed):
    """Declared process tree vs observed telemetry ("the child claiming a parent it never had").
    declared: declared_spawns() rows, {child: parent}, or (parent, child[, cmdline]) tuples (None: telemetry only).
    observed: the raw log (bytes / text; anything process_events() reads) or its record list.
    -> {matched: [{child, declared_parent, recorded_parent, pid, guid, cmdline}],
        parent_mismatch: [{child, declared_parent, recorded_parent, real_parent_if_known, pid, guid, reasons}],
        declared_only (declared spawns that never ran), observed_only (unexpected processes: unmatched and not the
        parent of a matched one), orphans (recorded parent never seen / exited), spoofed (bool), attack}.
    A child is matched by image basename, then canonical cmdline, then recorded parent == declared parent, then time
    order. reasons: 'declared' (recorded parent != declared parent), 'creator' (the real creator -- 4688 ProcessId
    next to a Sysmon EID 1 of the same process, or a CreatorProcessId / CreatorProcessGuid field -- differs from
    the recorded ParentProcessId / ParentImage), 'parent_image' (ParentImage disagrees with the process that
    ParentProcessId / ParentProcessGuid resolves to). Images are answered in the log's spelling (basename).
    {} when the log has no process records."""
    try:
        procs = _rcp_procs(observed)
        if not procs:
            return {}
        img = lambda p: _pt_base(p["image"]) if p and p.get("image") else None  # noqa: E731
        info = []
        for p in procs:
            rp = _rcp_resolve(procs, p, p["rec_ppid"], p["rec_pguid"])
            rec = _pt_base(p["rec_pimage"]) if p["rec_pimage"] else img(rp)
            real, reasons = None, []
            if p["creator"] is not None or p["creator_guid"]:
                cp = _rcp_resolve(procs, p, p["creator"], p["creator_guid"])
                real = img(cp) or (_pt_base(p["creator_image"]) if p["creator_image"] else None)
                if (p["creator"] is not None and p["rec_ppid"] is not None and p["creator"] != p["rec_ppid"]) or \
                        (p["creator_guid"] and p["rec_pguid"] and p["creator_guid"] != p["rec_pguid"]) or \
                        (real and rec and _rcp_base(real) != _rcp_base(rec)):
                    reasons.append("creator")
            elif p["creator_image"]:
                real = _pt_base(p["creator_image"])
                if rec and _rcp_base(real) != _rcp_base(rec):
                    reasons.append("creator")
            if p["rec_pimage"] and rp is not None and rp.get("image") and \
                    _rcp_base(p["rec_pimage"]) != _rcp_base(rp["image"]):
                reasons.append("parent_image")
            orphan = None
            if rp is None and (p["rec_ppid"] is not None or p["rec_pguid"]):
                gone = [q for q in procs if q is not p and ((p["rec_pguid"] and q["guid"] == p["rec_pguid"]) or
                                                             (p["rec_ppid"] is not None and q["pid"] == p["rec_ppid"]))]
                orphan = "exited" if gone else "missing"
            info.append({"p": p, "rp": rp, "rec": rec, "real": real, "reasons": reasons, "orphan": orphan})

        def row(x, dp=None):
            p = x["p"]
            return {"child": img(p) or p["pid_raw"], "declared_parent": _pt_base(dp) if dp else None,
                    "recorded_parent": x["rec"], "real_parent_if_known": x["real"], "pid": p["pid_raw"],
                    "guid": p["guid"], "cmdline": p["cmdline"], "reasons": list(x["reasons"])}

        decl = _rcp_declared(declared)
        used, matched, mism, dec_only = set(), [], [], []
        for d in decl:
            cb, cc, pb = _rcp_base(d["child"]), _rcp_canon(d["cmdline"]), _rcp_base(d["parent"])
            best = None
            for j, x in enumerate(info):
                if j in used or _rcp_base(x["p"]["image"]) != cb:
                    continue
                oc = _rcp_canon(x["p"]["cmdline"])
                sc = (4 if cc and oc == cc else 2 if cc and oc and (cc in oc or oc in cc) else 0) + \
                    (1 if pb and pb in (_rcp_base(x["rec"]), _rcp_base(x["real"])) else 0)
                if best is None or sc > best[0]:
                    best = (sc, j)
            if best is None:
                dec_only.append({"child": _pt_base(d["child"]), "declared_parent": _pt_base(d["parent"]) if d["parent"]
                                 else None, "cmdline": d["cmdline"]})
                continue
            used.add(best[1])
            x = info[best[1]]
            r = row(x, d["parent"])
            matched.append({k: r[k] for k in ("child", "declared_parent", "recorded_parent", "pid", "guid", "cmdline")})
            if pb and x["rec"] and _rcp_base(x["rec"]) != pb and not _rcp_proxy_ok(d, x["rec"]):
                r["reasons"].insert(0, "declared")
            if r["reasons"]:
                mism.append(r)
        for j, x in enumerate(info):
            if j not in used and x["reasons"]:
                mism.append(row(x))
        mism.sort(key=lambda r: next(i for i, x in enumerate(info) if x["p"]["pid_raw"] == r["pid"] and
                                     (img(x["p"]) or x["p"]["pid_raw"]) == r["child"]))
        parents, byp = set(), {id(x["p"]): x for x in info}
        todo = [info[j]["p"] for j in used]
        while todo and len(parents) < 50000:     # every ancestor (recorded or real) of a matched child is expected
            p = todo.pop()
            for q in (byp[id(p)]["rp"], _rcp_resolve(procs, p, p["creator"], p["creator_guid"])):
                if q is not None and id(q) not in parents:
                    parents.add(id(q))
                    todo.append(q)
        obs_only = [row(x) for j, x in enumerate(info) if decl and j not in used and id(x["p"]) not in parents]
        orphans = [dict(row(x), orphan=x["orphan"]) for x in info if x["orphan"]]
        spoof = any(set(r["reasons"]) & {"creator", "declared", "parent_image"} for r in mism)
        return {"matched": matched, "parent_mismatch": mism, "declared_only": dec_only, "observed_only": obs_only,
                "orphans": orphans, "spoofed": spoof, "attack": "T1134.004" if spoof else "none",
                "processes": len(procs)}
    except Exception:  # noqa: BLE001 - impostor / truncated input: nothing, never an exception
        return {}


def reconcile_processes_answer(r, kind, accepted_values=None, what=None, declared=None):
    """Answer a declared-vs-observed question from reconcile_processes() (or the raw log, with `declared`).
    kind: child (spoofed child image) | pid | guid | claimed-parent (recorded / fake parent) | true-parent (real
    creator, else the declared parent) | declared-parent | count (what: mismatch (default) | matched | declared_only
    | observed_only | orphans | processes) | declared-only (never ran) | observed-only (unexpected) | orphan | attack
    (T1134.004 when a parent was spoofed). `what` narrows to one child (image basename / path / pid). Values in the
    log's spelling or the matching accepted value; several -> list. 'none' when the field is absent (no mismatch),
    None when it cannot answer."""
    try:
        if not isinstance(r, dict) or "parent_mismatch" not in r:
            r = reconcile_processes(declared, r)
        if not r:
            return None
        acc = [a for a in (accepted_values or []) if str(a).strip()] or None
        kd = re.sub(r"[^a-z]", "", str(kind or "").lower())
        alias = [("attack", ("attack", "technique", "mitre", "ttp", "attck")),
                 ("count", ("count", "number", "howmany", "total")),
                 ("declaredonly", ("declaredonly", "neverran", "notobserved", "missing", "didnotrun", "notrun")),
                 ("observedonly", ("observedonly", "unexpected", "undeclared", "extra")),
                 ("orphan", ("orphan",)),
                 ("trueparent", ("trueparent", "realparent", "actualparent", "creator", "spawnedby", "realcreator")),
                 ("declaredparent", ("declaredparent", "expectedparent", "staticparent", "intendedparent")),
                 ("claimedparent", ("claimed", "recorded", "fake", "spoofedparent", "reportedparent", "loggedparent",
                                    "fakeparent", "parent")),
                 ("guid", ("guid",)), ("pid", ("pid", "processid", "id")),
                 ("child", ("child", "image", "process", "spoofed", "name"))]
        kd = next((k for k, al in alias if any(a in kd for a in al)), kd)
        if kd == "attack":
            v = r.get("attack") or "none"
            if acc and v != "none":
                return next((a for a in acc if str(a).strip().upper() == v), v)
            return v
        if kd == "count":
            w = re.sub(r"[^a-z]", "", str(what or "mismatch").lower())
            key = next((k for k in ("matched", "declared_only", "observed_only", "orphans", "processes")
                        if k.replace("_", "") in w or (k == "orphans" and "orphan" in w)), "parent_mismatch")
            v = r.get(key)
            return str(v if isinstance(v, int) else len(v or []))
        rows = r.get({"declaredonly": "declared_only", "observedonly": "observed_only", "orphan": "orphans"}
                     .get(kd, "parent_mismatch")) or []
        if what is not None:
            w = str(what).strip()
            wp = _pe_int(w)
            rows = [x for x in rows if _rcp_base(x.get("child")) == _rcp_base(w) or
                    (wp is not None and _pe_int(x.get("pid")) == wp)]
        field = {"pid": "pid", "guid": "guid", "claimedparent": "recorded_parent", "declaredparent": "declared_parent",
                 "trueparent": "real_parent_if_known"}.get(kd, "child")
        vals = []
        for x in rows:
            v = x.get(field)
            if kd == "trueparent" and not v:
                v = x.get("declared_parent")
            if v is None or v == "":
                continue
            if acc:
                vb, vp = _rcp_base(v), _pe_int(v)
                v = next((a for a in acc if _rcp_base(a) == vb or str(a).strip().lower() == str(v).lower() or
                          (vp is not None and _pe_int(str(a).strip()) == vp)), None)
                if v is None:
                    continue
            if v not in vals:
                vals.append(v)
        if not vals:
            return "none" if not rows or kd != "trueparent" else None
        return vals[0] if len(vals) == 1 else vals
    except Exception:  # noqa: BLE001
        return None


# --- cmdline-canon: canonical command lines for matching declared vs observed spawns (process-tree / fetch-site) -------
# split_cmdline(s) follows CommandLineToArgvW (argv[0] up to the closing quote, 2n / 2n+1 backslashes before '"', a '""'
# run inside quotes yields '"' and leaves quote mode -- Wine's shell32 algorithm); posix=True reads sh quoting ('..',
# "..", \x) without shlex. canon_cmdline(s): outer quotes off, %VAR% / $env:VAR / ${env:VAR} via _PS_ENV, cmd carets
# and in-word '""' gone, image -> lower basename without .exe, cmd switches lower-case and the /c /k payload canonised
# recursively, powershell parameters -> full lower names (-enc/-e/-ec -> -command <UTF-16LE text>), system path
# prefixes (any case, / or \, PROGRA~1) -> one spelling, whitespace collapsed. Args keep their case. Never raises;
# None for a non-string / empty line. Reachable from decode(material, rep="cmdline", transform="canon"|"argv"|
# "argv_posix") so declared-codec fixtures exercise it; existing callers (_rcp_canon) are unchanged.
_CL_ENV = re.compile(r"%([A-Za-z_][\w()]*)%|\$\{env:([A-Za-z_]\w*)\}|\$env:([A-Za-z_]\w*)", re.I)
_CL_PATHS = ((r"[a-z]:[\\/]+windows[\\/]+system32[\\/]+", "C:\\Windows\\System32\\"),
             (r"[a-z]:[\\/]+windows[\\/]+syswow64[\\/]+", "C:\\Windows\\SysWOW64\\"),
             (r"[a-z]:[\\/]+windows[\\/]+sysnative[\\/]+", "C:\\Windows\\System32\\"),
             (r"[a-z]:[\\/]+windows(?=[\\/]|$)", "C:\\Windows"),
             (r"[a-z]:[\\/]+(?:program files \(x86\)|progra~2)(?=[\\/]|$)", "C:\\Program Files (x86)"),
             (r"[a-z]:[\\/]+(?:program files|progra~1)(?=[\\/]|$)", "C:\\Program Files"),
             (r"[a-z]:[\\/]+(?:programdata|progra~3)(?=[\\/]|$)", "C:\\ProgramData"),
             (r"[a-z]:[\\/]+users(?=[\\/]|$)", "C:\\Users"))
_CL_PATHS = tuple((re.compile(p, re.I), r) for p, r in _CL_PATHS)
_CL_PS = ("command", "encodedcommand", "executionpolicy", "file", "noprofile", "noninteractive", "nologo", "noexit",
          "windowstyle", "sta", "mta", "version", "inputformat", "outputformat", "configurationname", "workingdirectory",
          "commandwithargs", "settingsfile", "login", "interactive", "help")
_CL_PS_ALIAS = {"e": "encodedcommand", "ec": "encodedcommand", "enc": "encodedcommand", "c": "command",
                "f": "file", "ep": "executionpolicy", "ex": "executionpolicy", "w": "windowstyle", "nop": "noprofile",
                "noni": "noninteractive", "nol": "nologo", "noe": "noexit", "v": "version", "wd": "workingdirectory"}
_CL_PS_VAL = {"executionpolicy", "file", "windowstyle", "version", "inputformat", "outputformat", "configurationname",
              "workingdirectory", "settingsfile"}


def split_cmdline(s, posix=False):
    """Command line -> argv list (Windows CommandLineToArgvW rules, or POSIX sh quoting with posix=True); None for a
    non-string. Pure python, linear, never raises."""
    if not isinstance(s, str):
        return None
    try:
        return _cl_split_posix(s) if posix else _cl_split_win(s)
    except Exception:  # noqa: BLE001
        return None


def _cl_split_win(s):
    out, i, n = [], 0, len(s)
    while i < n and s[i] in " \t":
        i += 1
    if i >= n:
        return out
    if s[i] == '"':                                      # argv[0]: no backslash / doubled-quote processing
        j = s.find('"', i + 1)
        j = n if j < 0 else j
        out.append(s[i + 1:j])
        i = j + 1
    else:
        j = i
        while j < n and s[j] not in " \t":
            j += 1
        out.append(s[i:j])
        i = j
    cur, have, qcount, bs = [], False, 0, 0
    while i < n:
        c = s[i]
        if c in " \t" and not qcount % 2:
            cur.extend("\\" * bs)
            bs = 0
            if have:
                out.append("".join(cur))
                cur, have = [], False
            i += 1
            continue
        if c == "\\":
            bs += 1
            have = True
            i += 1
            continue
        if c == '"':
            cur.extend("\\" * (bs // 2))
            have = True
            if bs % 2:
                cur.append('"')
                bs = 0
                i += 1
                continue
            bs = 0
            qcount += 1
            i += 1
            while i < n and s[i] == '"':                 # Wine shell32: count the run of quotes
                qcount += 1
                if qcount == 3:
                    cur.append('"')
                    qcount = 0
                i += 1
            if qcount == 2:
                qcount = 0
            continue
        cur.extend("\\" * bs)
        bs = 0
        cur.append(c)
        have = True
        i += 1
    cur.extend("\\" * bs)
    if have:
        out.append("".join(cur))
    return out


def _cl_split_posix(s):
    out, cur, have, i, n = [], [], False, 0, len(s)
    while i < n:
        c = s[i]
        if c in " \t\r\n":
            if have:
                out.append("".join(cur))
                cur, have = [], False
        elif c == "'":
            j = s.find("'", i + 1)
            j = n if j < 0 else j
            cur.append(s[i + 1:j])
            have, i = True, j
        elif c == '"':
            i += 1
            while i < n and s[i] != '"':
                if s[i] == "\\" and i + 1 < n and s[i + 1] in '$`"\\\n':
                    i += 1
                    if s[i] != "\n":
                        cur.append(s[i])
                else:
                    cur.append(s[i])
                i += 1
            have = True
        elif c == "\\":
            if i + 1 < n and s[i + 1] != "\n":
                cur.append(s[i + 1])
                have = True
            i += 1
        else:
            cur.append(c)
            have = True
        i += 1
    if have:
        out.append("".join(cur))
    return out


def _cl_env(s):
    def sub(m):
        v = _PS_ENV.get((m.group(1) or m.group(2) or m.group(3) or "").lower())
        return v if v is not None else m.group(0)
    return _CL_ENV.sub(sub, s)


def _cl_cmd_unescape(s):
    """cmd.exe reading: '^x' -> 'x' outside double quotes; '""' glued inside a word dropped (`po""wer`)."""
    s = re.sub(r'(?<=[^\s"])""(?=[^\s"])', "", s)
    out, q, i, n = [], False, 0, len(s)
    while i < n:
        c = s[i]
        if c == '"':
            q = not q
        elif c == "^" and not q:
            if i + 1 < n:
                out.append(s[i + 1])
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _cl_path(a):
    for rx, rep in _CL_PATHS:
        m = rx.match(a)
        if m:
            a = rep + a[m.end():]
            break
    if re.match(r"[A-Za-z]:[\\/]|\\\\", a):
        a = a[:2] + re.sub(r"[\\/]+", r"\\", a[2:])
        a = a[0].upper() + a[1:] if a[1] == ":" else a
    return a


def _cl_quote(a):
    return '"' + a + '"' if not a or re.search(r"\s", a) else a


def _cl_image(a):
    b = re.split(r"[\\/]", a.strip().strip("\"'"))[-1].lower()
    return b[:-4] if b.endswith(".exe") else b


def _cl_tail(s, k):
    """Raw remainder of `s` after its first k Windows-split tokens (for cmd /c and powershell -command)."""
    i, n = 0, len(s)
    for _ in range(k):
        while i < n and s[i] in " \t":
            i += 1
        q = False
        while i < n and (q or s[i] not in " \t"):
            if s[i] == '"':
                q = not q
            i += 1
    return s[i:].strip()


def _cl_ws(s):
    return re.sub(r"\s+", " ", s).strip()


def _cl_ps_param(a):
    if not a or a[0] not in "-/" or len(a) < 2:
        return None
    p = a[1:].lower().rstrip(":")
    if p in _CL_PS_ALIAS:
        return _CL_PS_ALIAS[p]
    hits = [x for x in _CL_PS if x.startswith(p)]
    return hits[0] if len(hits) == 1 or p in _CL_PS else None


def _cl_b64_utf16(v):
    try:
        b = base64.b64decode(re.sub(r"\s+", "", v) + "=" * (-len(re.sub(r"\s+", "", v)) % 4), validate=True)
        if len(b) < 2 or len(b) % 2:
            return None
        t = b.decode("utf-16-le").lstrip("\ufeff")
        return t if t and all(ch.isprintable() or ch in "\r\n\t" for ch in t) else None
    except (binascii.Error, ValueError, UnicodeDecodeError):
        return None


def canon_cmdline(s, _depth=0):
    """Declared / observed command line -> one canonical string (see the block comment above); None when unreadable."""
    try:
        if not isinstance(s, str):
            return None
        s = s.replace("\x00", "").lstrip("\ufeff").strip()
        for q in ('"', "'"):                              # outer quotes around the WHOLE line
            if len(s) > 1 and s[0] == q and s[-1] == q and q not in s[1:-1] and re.search(r"\s", s):
                s = s[1:-1].strip()
        s = _cl_cmd_unescape(_cl_env(s))
        argv = _cl_split_win(s)
        if not argv or not argv[0].strip():
            return None
        img = _cl_image(argv[0])
        out = [img]
        if img == "cmd":
            for k in range(1, len(argv)):
                a = argv[k]
                if re.fullmatch(r"/[A-Za-z](?::\w+)?", a):
                    out.append(a.lower())
                    if a.lower() in ("/c", "/k", "/r"):
                        rest = _cl_tail(s, k + 1)
                        if len(rest) > 1 and rest[0] == '"' and rest[-1] == '"':
                            rest = rest[1:-1]
                        inner = canon_cmdline(rest, _depth + 1) if _depth < 4 and rest else None
                        if inner or rest:
                            out.append(inner or _cl_ws(rest))
                        break
                else:
                    out.append(_cl_quote(_cl_path(a)))
            return _cl_ws(" ".join(out))
        if img in ("powershell", "pwsh", "powershell_ise"):
            k = 1
            while k < len(argv):
                a, p = argv[k], _cl_ps_param(argv[k])
                if p == "encodedcommand" and k + 1 < len(argv):
                    t = _cl_b64_utf16(argv[k + 1])
                    if t is not None:
                        out += ["-command", _cl_ws(t)]
                        k += 2
                        continue
                    out += ["-encodedcommand", argv[k + 1]]
                    k += 2
                    continue
                if p == "command":
                    rest = _cl_tail(s, k + 1)
                    if len(rest) > 1 and rest[0] == '"' and rest[-1] == '"' and '"' not in rest[1:-1]:
                        rest = rest[1:-1]
                    out += ["-command", _cl_ws(rest)] if rest else ["-command"]
                    break
                if p is None and a[:1] not in "-/":              # bare script text = implicit -command
                    out += ["-command", _cl_ws(_cl_tail(s, k))]
                    break
                if p is None:
                    out.append(a)
                    k += 1
                    continue
                out.append("-" + p)
                if p in _CL_PS_VAL and k + 1 < len(argv):
                    v = argv[k + 1]
                    out.append(_cl_quote(_cl_path(v)) if p in ("file", "workingdirectory", "settingsfile")
                               else _cl_quote(v.lower()))
                    k += 1
                k += 1
            return _cl_ws(" ".join(out))
        out += [_cl_quote(_cl_path(a)) for a in argv[1:]]
        return _cl_ws(" ".join(out))
    except Exception:  # noqa: BLE001
        return None


def _cl_decode(material, rep, transform):
    """decode() hook for rep 'cmdline': transform canon -> canon_cmdline, argv / argv_posix -> JSON argv list."""
    import json
    t = re.sub(r"[^a-z]", "", (transform or "").lower())
    if t in ("canon", "canonical", "canonicalize", "normalize"):
        return canon_cmdline(material)
    if t in ("argv", "split", "argvwin", "splitwin", "argvposix", "splitposix"):
        a = split_cmdline(material, posix=t.endswith("posix"))
        return None if a is None else json.dumps(a, ensure_ascii=False)
    return None
