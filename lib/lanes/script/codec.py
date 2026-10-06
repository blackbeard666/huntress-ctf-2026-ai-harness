"""ONE shared codec engine for every script-analysis fixture (days 1-6, any language).

Every fixture hides a plan (k=v|... text, or a JSON object) as   carrier(transform(plan_bytes, key)).
  carrier   : how the bytes are written in source  (base64 / urlsafe / reversed text / hex compact|sep|\\x|%|0x /
              decimal any-separator / octal / int-array literal)
  transform : identity, reverse, single-byte xor, repeating-key xor, rolling xor (prev cipher | prev plain),
              counter xor (c ^ (k+i)),
              add/sub mod 256 (any shift), rotate left/right 1..7, and each of them applied to the reversed bytes
  key       : hex '1b', comma hex '55,51,74,dd,3a' (any separator), embedded in the transform name ('xor_5a', 'add_7'),
              int arrays in the code, OR derived from known plaintext (the plan always starts 'v=' or '{').

The self-describing `Codec_<id>='carrier|transform|key'` (any language) is only a HINT tried first; correctness comes
from the validator (the output must parse as a plan). So a wrong/missing/misleading codec (batch 'plain_fragments' is
really base64) still decodes, and so does a language whose code we never parse (JScript keeps its codec in code).
Nothing is executed.
"""
import base64
import binascii
import json
import re

PLAN_PREFIXES = (b"v=1|steps=", b"v=2|steps=", b"v=3|steps=", b'{"steps":[', b'{"steps": [')
PROBE_CHARS = (ord("v"), ord("{"))


# ---------------------------------------------------------------------------------------------------------- keys
def key_bytes(key):
    """'1b' / '55,51,74,dd,3a' / '13:37:c4' / '0x1b' / '27' -> list of byte lists to try (hex reading first)."""
    key = (key or "").strip()
    if not key:
        return []
    out = []
    if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", key):
        out.append(list(bytes.fromhex(key)))
    parts = [x for x in re.split(r"[\s,:;\-|]+", key) if x]
    if parts and all(re.fullmatch(r"(?:0x)?[0-9a-fA-F]{1,2}", x) for x in parts):
        out.append([int(x, 16) for x in parts])
    if parts and all(re.fullmatch(r"\d{1,3}", x) and int(x) < 256 for x in parts):
        out.append([int(x) for x in parts])
    return [k for i, k in enumerate(out) if k and k not in out[:i]]


def name_keys(transform):
    """Keys embedded in a transform name: xor_5a -> [0x5a], add_7 -> [7], rot3 -> [3]."""
    m = re.search(r"(?:xor|add|sub|rot\w*)[_-]?(0x[0-9a-f]+|[0-9a-f]{2}|\d+)$", transform or "", re.I)
    if not m:
        return []
    t = m.group(1)
    cands = []
    if re.fullmatch(r"\d+", t):
        cands.append(int(t))
    if re.fullmatch(r"(?:0x)?[0-9a-f]+", t, re.I):
        cands.append(int(t, 16))
    return [[c & 255] for c in cands]


def code_keys(text):
    """Integer arrays / lists anywhere in the code ([41,178,35], @(0x1b,..), (..), Array(..), bash (0x55 0x51)):
    candidate repeating keys. Short ones only (keys, not material)."""
    keys = []
    for m in re.finditer(r"[\[(]\s*((?:(?:0x[0-9a-fA-F]+|&H[0-9a-fA-F]+|16#[0-9a-fA-F]+|\d+)\s*[,\s]\s*){1,31}"
                         r"(?:0x[0-9a-fA-F]+|&H[0-9a-fA-F]+|16#[0-9a-fA-F]+|\d+))\s*[\])]", text):
        vals = []
        for t in re.split(r"[,\s]+", m.group(1).strip()):
            t = t.strip()
            if not t:
                continue
            v = int(t[2:], 16) if t[:2].lower() in ("0x", "&h") else int(t[3:], 16) if t.startswith("16#") else int(t)
            vals.append(v)
        if 2 <= len(vals) <= 32 and all(0 <= v < 256 for v in vals) and vals not in keys:
            keys.append(vals)
    return keys


# ------------------------------------------------------------------------------------------------------ carriers
B64 = re.compile(r"^[A-Za-z0-9+/=\s_-]+$")


def _b64(s):
    s = re.sub(r"\s+", "", s)
    if not s or len(s) < 8:
        return []
    outs = []
    for alt in (None, b"-_"):
        try:
            t = s.replace("-", "+").replace("_", "/") if alt else s
            outs.append(base64.b64decode(t + "=" * (-len(t) % 4), validate=True))
        except (binascii.Error, ValueError):
            pass
    return outs


def carriers(material):
    """All plausible byte readings of a material string (or an int list), most specific first.
    Yields (carrier_name, bytes)."""
    if isinstance(material, (list, tuple)):
        if all(isinstance(x, int) and 0 <= x < 256 for x in material):
            yield "integer_list", bytes(material)
        return
    s = material.strip()
    if not s:
        return
    # escaped hex: \x41 / %41 / 0x41 ... (+ separators)
    esc = list(re.finditer(r"(?:\\x|%|0x)([0-9a-fA-F]{2})", s))
    if esc and sum(len(m.group(0)) for m in esc) >= len(re.sub(r"[\s,;:|]", "", s)) * 0.9:
        yield "hex_escape", bytes(int(m.group(1), 16) for m in esc)
    toks = [t for t in re.split(r"[^0-9A-Za-z]+", s) if t]
    # separated tokens
    if len(toks) >= 4:
        if all(re.fullmatch(r"\d{1,3}", t) for t in toks):
            if all(int(t) < 256 for t in toks):
                yield "decimal", bytes(int(t) for t in toks)
            if all(re.fullmatch(r"[0-7]{1,3}", t) and int(t, 8) < 256 for t in toks):
                yield "octal", bytes(int(t, 8) for t in toks)
        if all(re.fullmatch(r"[0-9a-fA-F]{1,2}", t) for t in toks):
            yield "hex_sep", bytes(int(t, 16) for t in toks)
    compact = re.sub(r"[\s]", "", s)
    if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", compact):
        yield "hex_compact", bytes.fromhex(compact)
    hexsep = re.sub(r"[\s:,;|.\-]", "", s)
    if hexsep != compact and re.fullmatch(r"(?:[0-9a-fA-F]{2})+", hexsep) and len(toks) >= 4 \
            and all(len(t) == 2 for t in toks):
        yield "hex_sep", bytes.fromhex(hexsep)
    if B64.match(s):
        for b in _b64(s):
            yield "base64", b
        for b in _b64(s[::-1]):
            yield "reversed_base64", b


# ---------------------------------------------------------------------------------------------------- transforms
def _xor(b, k):
    n = len(k)
    return bytes(c ^ k[i % n] for i, c in enumerate(b))


def _shift(b, d):
    return bytes((c + d) & 255 for c in b)


def _roll_cipher(b, seed):
    out, prev = bytearray(), seed
    for c in b:
        out.append(c ^ prev)
        prev = c
    return bytes(out)


def _roll_plain(b, seed):
    out, prev = bytearray(), seed
    for c in b:
        p = c ^ prev
        out.append(p)
        prev = p
    return bytes(out)


def _rotr(b, n):
    return bytes(((c >> n) | (c << (8 - n))) & 255 for c in b)


def transforms(b, keys=()):
    """Yield (transform_name, key_repr, plaintext_candidate) for every transform family over b and reversed b.
    Single-byte families take their key from known plaintext ('v' / '{'), so no key is needed."""
    for rev, data in (("", b), ("reverse_", b[::-1])):
        if not data:
            continue
        yield rev + "identity", "", data
        for p in PROBE_CHARS:
            k = data[0] ^ p
            yield rev + "single_byte_xor", "%02x" % k, _xor(data, [k])
            d = (p - data[0]) & 255
            yield rev + "shift_modulo_256", "%02x" % d, _shift(data, d)
            yield rev + "rolling_xor", "%02x" % k, _roll_cipher(data, k)
            yield rev + "rolling_xor_plain", "%02x" % k, _roll_plain(data, k)
            yield rev + "counter_xor", "%02x" % k, bytes(c ^ ((k + i) & 255) for i, c in enumerate(data))
        for n in range(1, 8):
            yield rev + "rotate", str(n), _rotr(data, n)
        for k in keys:
            if len(k) > 1:
                yield rev + "repeating_key_xor", ",".join("%02x" % x for x in k), _xor(data, k)
                yield rev + "repeating_key_xor_then_reverse", ",".join("%02x" % x for x in k), _xor(data[::-1], k)[::-1]
        # repeating xor with a key derived from a known plan prefix (no key anywhere in the file)
        for pre in PLAN_PREFIXES:
            if not data or (data[0] ^ pre[0]) is None:
                continue
            for n in range(2, min(len(pre), 9) + 1):
                k = [data[i] ^ pre[i] for i in range(n)]
                yield rev + "repeating_key_xor", ",".join("%02x" % x for x in k), _xor(data, k)


# ------------------------------------------------------------------------------------------------------- plan
def parse_plan(raw):
    """bytes -> plan dict or None.  'v=N|k=v|..' (needs steps) or a JSON object (JS plan / PS descriptor)."""
    if not raw or raw[0] not in PROBE_CHARS:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if any(ord(ch) < 9 or 13 < ord(ch) < 32 for ch in text):
        return None
    if text.startswith("v="):
        plan = {}
        for part in text.strip().split("|"):
            k, eq, v = part.partition("=")
            if not eq:
                return None
            plan.setdefault(k.strip(), v)
        if "steps" not in plan:
            return None
        plan["steps"] = [x for x in plan["steps"].split(",") if x]
        return plan
    try:
        obj = json.loads(text)
    except ValueError:
        return None
    if not isinstance(obj, dict):
        return None
    if "values" in obj and isinstance(obj["values"], dict):  # JS plan {steps, adapter, values, stageCount}
        flat = dict(obj["values"])
        flat.update({k: v for k, v in obj.items() if k != "values"})
        obj = flat
    if "stageCount" in obj:
        obj.setdefault("stage_count", obj["stageCount"])
    obj.setdefault("__json__", True)
    return obj


def decode(material, codec=None, keys=()):
    """material (str / int list) + optional 'carrier|transform|key' hint -> (plan, how) or (None, None).
    Hinted key first, then every carrier x transform x key; first output that parses as a plan wins."""
    hint_keys = []
    if codec:
        parts = (codec.split("|") + ["", "", ""])[:3]
        hint_keys = key_bytes(parts[2]) + name_keys(parts[1])
    allkeys = hint_keys + [k for k in keys if k not in hint_keys]
    for cname, b in carriers(material):
        for tname, krepr, out in transforms(b, allkeys):
            plan = parse_plan(out)
            if plan is not None:
                return plan, {"carrier": cname, "transform": tname, "key": krepr, "plain": out.decode("utf-8")}
    return None, None
