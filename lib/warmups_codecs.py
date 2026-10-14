"""Warmups lane codec library: every day's line codec as an exact ENCODER + decoder, plus a broad try-list of classical
encoders for identifying an unknown day's codec from its Single Solve.

Warmups (D1-D14): each Single is one sentence -- "Nice work decoding this warmup! To solve, submit this exact answer to
the Game Master: <slug>" -- under ONE codec that changes daily; Mastery day N = 5N-2 sets of N numbered lines, line k
under day k's codec, the sentence cut mid-word (reference/techniques/warmups.md). The encoders below reproduce the GM's
bytes exactly (all 819 lines of D13 auto-mastery-d1a77831: lowercase hex/%xx, space-separated 8-bit binary, decimal,
3-digit octal, decimal `&#NN;`, quoted lowercase `\\u00xx`, padded base32, unpadded base64url, ...), so
hctf/today_probe.py can re-encode yesterday's verified Mastery sentence with TODAY's codec on a new last line and test
the solver BEFORE the Mastery clock (D12/D13: the first Mastery attempt failed on exactly that mix).

  DAYS        [(day, name, enc, dec, free)] -- free = no alphabet signature (told apart only by how English it reads)
  CANDIDATES  [(name, enc, dec|None)] -- DAYS first, then format variants, classical ciphers and chained pairs
  infer(plain, blob, hints=())  -> (name, enc) | None: the encoder E with E(plain) == blob.strip() (or dec(blob) == plain)
  plaintext(blob, slug)         -> the decoded sentence (decode_chunk -> peel -> candidate decoders -> template)

Also registers SPECULATIVE keyless free-text decoders with lib.decode.register_free (day=None): lib.decode's joint
free-line assignment tries them only for a blob with more free lines than the confirmed free codecs cover AND more lines
than the newest confirmed codec's day -- never on D1-D13 bytes. Pure stdlib.
"""
import base64
import codecs
import html
import itertools
import json
import quopri
import os
import re
import string
import urllib.parse

SENTENCE = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {slug}"
SLUG = re.compile(r"[a-z]+(?:-[a-z]+)+-\d{2,}")


def _u(s):
    return s.encode("utf-8")


def _t(b):
    return b.decode("utf-8") if isinstance(b, (bytes, bytearray)) else b


# ------------------------------------------------------------------------------------------------ day codecs (exact)
def rot(s, n):
    return "".join(chr((ord(c) - 97 + n) % 26 + 97) if "a" <= c <= "z" else
                   chr((ord(c) - 65 + n) % 26 + 65) if "A" <= c <= "Z" else c for c in s)


def atbash(s):
    return "".join(chr(219 - ord(c)) if "a" <= c <= "z" else chr(155 - ord(c)) if "A" <= c <= "Z" else c for c in s)


def _b64pad(t):
    t = re.sub(r"\s+", "", t)
    return t + "=" * (-len(t) % 4)


def _toks(t):
    return [x for x in re.split(r"[\s,]+", t.strip()) if x]


DAYS = [
    (1, "base64", lambda s: base64.b64encode(_u(s)).decode(), lambda t: _t(base64.b64decode(_b64pad(t), validate=True)),
     False),
    (2, "rot13", lambda s: rot(s, 13), lambda t: rot(t, 13), True),
    (3, "hex", lambda s: _u(s).hex(), lambda t: _t(bytes.fromhex(re.sub(r"\s+", "", t))), False),
    (4, "binary8", lambda s: " ".join(f"{b:08b}" for b in _u(s)),
     lambda t: _t(bytes(int(x, 2) for x in _toks(t))), False),
    (5, "decimal", lambda s: " ".join(str(b) for b in _u(s)), lambda t: _t(bytes(int(x) for x in _toks(t))), False),
    (6, "octal3", lambda s: " ".join(f"{b:03o}" for b in _u(s)), lambda t: _t(bytes(int(x, 8) for x in _toks(t))),
     False),
    (7, "url%xx", lambda s: "".join(f"%{b:02x}" for b in _u(s)), lambda t: _t(urllib.parse.unquote_to_bytes(t.strip())),
     False),
    (8, "html&#n;", lambda s: "".join(f"&#{ord(c)};" for c in s), lambda t: html.unescape(t.strip()), False),
    (9, "json\\u", lambda s: '"' + "".join(f"\\u{ord(c):04x}" for c in s) + '"',
     lambda t: json.loads(t.strip() if t.strip().startswith('"') else '"' + t.strip() + '"'), False),
    (10, "base32", lambda s: base64.b32encode(_u(s)).decode(), lambda t: _t(base64.b32decode(re.sub(r"\s+", "", t))),
     False),
    (11, "base64url-nopad", lambda s: base64.urlsafe_b64encode(_u(s)).decode().rstrip("="),
     lambda t: _t(base64.urlsafe_b64decode(_b64pad(t.strip().rstrip("=")))), False),
    (12, "reverse", lambda s: s[::-1], lambda t: t[::-1], True),
    (13, "atbash", atbash, atbash, True),
    (14, "caesar+7", lambda s: rot(s, 7), lambda t: rot(t, -7), True),
]

try:   # fair runs (HCTF_CODEC_MAX_DAY=<N-1>, as lib/codec.py): only codecs GM-confirmed before day N
    _MAXD = int(os.environ.get("HCTF_CODEC_MAX_DAY", "0")) or 99
except ValueError:
    _MAXD = 99
DAYS = [d for d in DAYS if d[0] <= _MAXD]


def day_codec(day):
    """(name, enc, dec, free) of a known day's line codec, or None."""
    for d, name, enc, dec, free in DAYS:
        if d == day:
            return name, enc, dec, free
    return None


def safe(fn, x):
    """fn(x), or None when it raises / returns something unprintable."""
    try:
        out = fn(x)
    except Exception:  # noqa: BLE001 - a codec that doesn't apply
        return None
    if not isinstance(out, str):
        return None
    return out if all(c.isprintable() or c in "\t\r\n" for c in out) else None


# ------------------------------------------------------------------------------------------ classical / format family
_MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....", "I": "..",
    "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--..", "0": "-----",
    "1": ".----", "2": "..---", "3": "...--", "4": "....-", "5": ".....", "6": "-....", "7": "--...", "8": "---..",
    "9": "----.", "!": "-.-.--", ":": "---...", ",": "--..--", ".": ".-.-.-", "-": "-....-", "?": "..--..",
    "'": ".----.", "/": "-..-.", "(": "-.--.", ")": "-.--.-", "&": ".-...", ";": "-.-.-.", "=": "-...-", "+": ".-.-.",
    '"': ".-..-.", "@": ".--.-.", "_": "..--.-",
}
_UNMORSE = {v: k for k, v in _MORSE.items()}


def morse_enc(s, word="/"):
    return f" {word} ".join(" ".join(_MORSE.get(c.upper(), "") for c in w if c.upper() in _MORSE)
                            for w in s.split(" "))


def morse_dec(t):
    words = re.split(r"\s*/\s*|\s{3,}", t.strip())
    return " ".join("".join(_UNMORSE.get(x, "") for x in w.split()) for w in words).lower()


_NATO = ("Alfa Bravo Charlie Delta Echo Foxtrot Golf Hotel India Juliett Kilo Lima Mike November Oscar Papa Quebec "
         "Romeo Sierra Tango Uniform Victor Whiskey Xray Yankee Zulu").split()
_NATO_DIG = "Zero One Two Three Four Five Six Seven Eight Nine".split()


def nato_enc(s, sep=" ", word=" / "):
    out = []
    for w in s.split(" "):
        out.append(sep.join(_NATO[ord(c.lower()) - 97] if c.isascii() and c.isalpha() else
                            _NATO_DIG[int(c)] if c.isdigit() else c for c in w))
    return word.join(out)


def nato_dec(t):
    m = {w.lower(): chr(97 + i) for i, w in enumerate(_NATO)}
    m.update({"alpha": "a", "juliet": "j", "x-ray": "x"})
    m.update({w.lower(): str(i) for i, w in enumerate(_NATO_DIG)})
    words = re.split(r"\s*/\s*", t.strip())
    return " ".join("".join(m.get(x.lower(), x) for x in w.split()) for w in words)


def a1z26_enc(s, sep="-"):
    """Letters -> 1..26 joined by `sep` inside a word, words by a space; other characters kept."""
    out = []
    for w in s.split(" "):
        parts, cur = [], []
        for c in w:
            if c.isascii() and c.isalpha():
                cur.append(str(ord(c.lower()) - 96))
            else:
                if cur:
                    parts.append(sep.join(cur))
                    cur = []
                parts.append(c)
        if cur:
            parts.append(sep.join(cur))
        out.append("".join(parts))
    return " ".join(out)


def a1z26_dec(t, sep="-"):
    return re.sub(r"\d{1,2}(?:" + re.escape(sep) + r"\d{1,2})*",
                  lambda m: "".join(chr(96 + int(x)) if 1 <= int(x) <= 26 else x for x in m.group(0).split(sep)), t)


def rot47(s):
    return "".join(chr(33 + (ord(c) - 33 + 47) % 94) if 33 <= ord(c) <= 126 else c for c in s)


_ROWS = ("`1234567890-=", "qwertyuiop[]\\", "asdfghjkl;'", "zxcvbnm,./")


def qwerty_shift(s, d):
    """Each key -> its neighbour d keys to the right (d=-1: left) on a US QWERTY row; case kept, others unchanged."""
    m = {}
    for row in _ROWS:
        for i, c in enumerate(row):
            j = i + d
            if 0 <= j < len(row):
                m[c] = row[j]
    out = []
    for c in s:
        lo = c.lower()
        if lo in m:
            v = m[lo]
            out.append(v.upper() if c.isupper() and v.isalpha() else v)
        else:
            out.append(c)
    return "".join(out)


def rail_enc(s, n):
    rails = [[] for _ in range(n)]
    r, step = 0, 1
    for c in s:
        rails[r].append(c)
        if n > 1:
            if r == 0:
                step = 1
            elif r == n - 1:
                step = -1
            r += step
    return "".join("".join(x) for x in rails)


def rail_dec(t, n):
    pattern = list(range(n)) + list(range(n - 2, 0, -1)) if n > 1 else [0]
    idx = [pattern[i % len(pattern)] for i in range(len(t))]
    counts = [idx.count(r) for r in range(n)]
    pos, rails = 0, []
    for c in counts:
        rails.append(list(t[pos:pos + c]))
        pos += c
    return "".join(rails[r].pop(0) for r in idx)


_AFFINE_A = (3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25)


def affine(s, a, b):
    return "".join(chr((a * (ord(c) - 97) + b) % 26 + 97) if "a" <= c <= "z" else
                   chr((a * (ord(c) - 65) + b) % 26 + 65) if "A" <= c <= "Z" else c for c in s)


def affine_inv(t, a, b):
    ai = pow(a, -1, 26)
    return "".join(chr(ai * (ord(c) - 97 - b) % 26 + 97) if "a" <= c <= "z" else
                   chr(ai * (ord(c) - 65 - b) % 26 + 65) if "A" <= c <= "Z" else c for c in t)


def vigenere(s, key, sign=1):
    """Letters only advance the key (classic tableau); case kept."""
    k = [ord(c) - 97 for c in key.lower() if c.isalpha()]
    if not k:
        return s
    out, i = [], 0
    for c in s:
        if "a" <= c <= "z" or "A" <= c <= "Z":
            base = 97 if c.islower() else 65
            out.append(chr((ord(c) - base + sign * k[i % len(k)]) % 26 + base))
            i += 1
        else:
            out.append(c)
    return "".join(out)


_B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58_enc(s):
    b = _u(s)
    n = int.from_bytes(b, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = _B58[r] + out
    return "1" * (len(b) - len(b.lstrip(b"\0"))) + out


def b58_dec(t):
    n = 0
    for c in t.strip():
        n = n * 58 + _B58.index(c)
    return _t(n.to_bytes((n.bit_length() + 7) // 8, "big"))


# basE91 (Joachim Henke): 13/14-bit groups -> 2 chars of a 91-char alphabet (printable ASCII minus space - \ ').
# Strict decoder: whitespace is dropped, any other non-alphabet character rejects the line.
_B91 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&()*+,./:;<=>?@[]^_`{|}~\""
_UNB91 = {c: i for i, c in enumerate(_B91)}


def b91_enc(s):
    b = n = 0
    out = []
    for byte in _u(s):
        b |= byte << n
        n += 8
        if n > 13:
            v = b & 8191
            if v > 88:
                b >>= 13
                n -= 13
            else:
                v = b & 16383
                b >>= 14
                n -= 14
            out += [_B91[v % 91], _B91[v // 91]]
    if n:
        out.append(_B91[b % 91])
        if n > 7 or b > 90:
            out.append(_B91[b // 91])
    return "".join(out)


def b91_dec(t):
    b = n = 0
    v = -1
    out = bytearray()
    for c in re.sub(r"\s+", "", t):
        d = _UNB91[c]
        if v < 0:
            v = d
            continue
        v += d * 91
        b |= v << n
        n += 13 if (v & 8191) > 88 else 14
        while n > 7:
            out.append(b & 255)
            b >>= 8
            n -= 8
        v = -1
    if v >= 0:
        out.append((b | v << n) & 255)
    return _t(bytes(out))


def b36_enc(s):
    n, out = int.from_bytes(_u(s), "big"), ""
    while n:
        n, r = divmod(n, 36)
        out = "0123456789abcdefghijklmnopqrstuvwxyz"[r] + out
    return out


def b36_dec(t):
    n = int(t.strip(), 36)
    return _t(n.to_bytes((n.bit_length() + 7) // 8, "big"))


# base62 big-integer text (CyberChef "To Base62" / GMP / pybase62): bytes as one big-endian integer in radix 62, no
# padding, leading zero bytes dropped. Alphabet 0-9A-Za-z, or the "inverted" 0-9a-zA-Z. Strict: any non-alphabet
# character (space, punctuation, '=') rejects the line.
_B62 = string.digits + string.ascii_uppercase + string.ascii_lowercase
_B62_INV = string.digits + string.ascii_lowercase + string.ascii_uppercase


def b62_enc(s, alpha=_B62):
    n, out = int.from_bytes(_u(s), "big"), ""
    while n:
        n, r = divmod(n, 62)
        out = alpha[r] + out
    return out


def b62_dec(t, alpha=_B62):
    t = t.strip()
    if not t or len(t) > 4096:
        raise ValueError("not base62")
    n = 0
    for c in t:
        n = n * 62 + alpha.index(c)
    return _t(n.to_bytes((n.bit_length() + 7) // 8, "big"))


# Punycode (RFC 3492, punycode.js / Python "punycode" codec): basic code points kept in order, then '-' and the
# lowercase base-36 deltas of the rest -- an ASCII line comes out as itself + '-'. IDNA (RFC 5891 ToASCII): each
# non-ASCII label becomes "xn--" + punycode, ASCII labels stay. Variants: whole line, per space-separated word, forced
# "xn--" per word, IDNA per word. Strict: a label must re-encode to itself and decode to printable text.
_PUNY_EXT = re.compile(r"[A-Za-z0-9]*")


def puny_enc(s):
    return s.encode("punycode").decode("ascii")


def _puny1(lbl):
    if not lbl or not lbl.isascii() or len(lbl) > 4096:
        raise ValueError("not punycode")
    basic, _sep, ext = lbl.rpartition("-")
    if not _PUNY_EXT.fullmatch(ext):
        raise ValueError("not punycode")
    out = lbl.encode("ascii").decode("punycode")
    if not out.isprintable() or puny_enc(out) != basic + _sep + ext.lower():
        raise ValueError("not punycode")
    return out


def puny_dec(t):
    return _puny1(t.strip())


def puny_words_dec(t):
    toks = t.strip().split(" ")
    if not all("-" in w for w in toks):
        raise ValueError("not punycode words")
    return " ".join(_puny1(w) for w in toks)


def idna_enc(s, force=False):
    if force:
        return " ".join("xn--" + puny_enc(w) for w in s.split(" "))
    return " ".join(".".join(lb if lb.isascii() else "xn--" + puny_enc(lb) for lb in w.split(".")) for w in s.split(" "))


def idna_dec(t, force=False):
    """xn-- labels (space-separated words, each optionally dot-separated labels) decoded; force = every word xn--."""
    toks, out, hit = t.strip().split(" "), [], False
    for w in toks:
        if force and not w.lower().startswith("xn--"):
            raise ValueError("not xn-- words")
        labels = w.split(".") if not force else [w]
        dec = []
        for lbl in labels:
            if lbl[:4].lower() == "xn--":
                dec.append(_puny1(lbl[4:]))
                hit = True
            else:
                dec.append(lbl)
        out.append(".".join(dec))
    if not hit:
        raise ValueError("no xn-- label")
    return " ".join(out)


# Baconian cipher (CyberChef "Bacon Cipher Encode" semantics): letter -> 5-bit group, "24" = Bacon's own alphabet
# (I=J, U=V), "26" = one code per letter. groups = letters only, groups space-joined; keep = groups run together, every
# other character kept in place (cc: CyberChef also turns a kept 0/1 digit into A/B). Lossy (case, I/J, U/V): the
# decoder returns lowercase letters.
_BACON24 = "abcdefghiklmnopqrstuwxyz"
_BACON_TR = {"AB": "AB", "ab": "ab", "BA": "BA", "01": "01", "10": "10"}


def bacon_enc(s, alpha=26, tr="AB", keep=False, cc=False):
    sym = _BACON_TR[tr]
    out = []
    for c in s:
        lc = c.lower()
        if "a" <= lc <= "z":
            n = ord(lc) - 97 if alpha == 26 else _BACON24.index({"j": "i", "v": "u"}.get(lc, lc))
            out.append("".join(sym[int(b)] for b in f"{n:05b}"))
        elif keep:
            out.append(sym[int(c)] if cc and c in "01" else c)
    return "".join(out) if keep else " ".join(out)


def bacon_dec(t, alpha=26, tr="AB", keep=False):
    """Inverse of bacon_enc; None for anything that isn't cleanly that layout (decoy text, wrong symbols, stray bits)."""
    sym = _BACON_TR[tr]
    t = t.strip()
    top = 26 if alpha == 26 else 24

    def run(bits):
        if len(bits) % 5:
            return None
        out = ""
        for i in range(0, len(bits), 5):
            n = int("".join(str(sym.index(b)) for b in bits[i:i + 5]), 2)
            if n >= top:
                return None
            out += chr(97 + n) if alpha == 26 else _BACON24[n]
        return out

    if not keep:
        if not re.fullmatch(f"[{sym}]{{5}}(?:[ \\t]*[{sym}]{{5}})*", t):
            return None
        return run(re.sub(r"\s+", "", t))
    nbits = sum(c in sym for c in t)
    if nbits < 10 or nbits < 0.6 * len(re.sub(r"\s", "", t)) or any(c.isalpha() and c not in sym for c in t):
        return None
    out = []
    for m in re.finditer(f"[{sym}]+|[^{sym}]+", t):
        g = m.group(0)
        if g[0] not in sym:
            out.append(g)
        elif len(g) < 5:   # a slug digit run ("-10") kept verbatim, or turned into A/B by CyberChef
            out.append("".join(str(sym.index(b)) for b in g) if sym.isalpha() else g)
        else:
            d = run(g)
            if d is None:
                return None
            out.append(d)
    return "".join(out)


# uuencode / xxencode: lines of <length char><4 chars per 3 bytes>, 45 bytes a line, optional `begin NNN name` ... `end`
# frame. uu = chr(32 + v) (0 as space or backtick), xx = the 64-char alphabet below. The decoder takes framed or bare
# bodies and rejects a line whose characters or length don't fit its length char.
_UU = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_"
_XX = "+-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_UNUU = {**{c: i for i, c in enumerate(_UU)}, "`": 0}
_UNXX = {c: i for i, c in enumerate(_XX)}


def uu_enc(s, alpha=_UU, zero="`", frame=None, end="`"):
    """Body lines (alpha[0] -> `zero`); frame="644 name" wraps it in begin/end with an `end` length-0 line."""
    a = alpha.replace(alpha[0], zero, 1) if zero else alpha
    b = _u(s)
    lines = []
    for i in range(0, len(b), 45):
        chunk = b[i:i + 45]
        n = int.from_bytes(chunk + b"\0" * (-len(chunk) % 3), "big")
        k = (len(chunk) + 2) // 3 * 4
        lines.append(a[len(chunk)] + "".join(a[(n >> (6 * (k - 1 - j))) & 63] for j in range(k)))
    if frame:
        lines = [f"begin {frame}"] + lines + [a[0] if end is None else end, "end"]
    return "\n".join(lines)


def uu_dec(t, table=_UNUU):
    out = bytearray()
    lines = [ln.strip("\r\n") for ln in t.strip().splitlines()]
    if lines and re.fullmatch(r"begin(-base64)? [0-7]{3,4} .*", lines[0].strip()):
        lines = lines[1:]
    for ln in lines:
        if ln.strip() == "end":
            break
        if not ln.strip():
            continue
        if table is not _UNUU:
            ln = ln.strip()
        n = table.get(ln[0])
        if n is None:
            return None
        if n == 0:
            break
        body = ln[1:]
        k = (n + 2) // 3 * 4
        if table is _UNUU:
            body = body.ljust(k)                    # space-zero encoders lose trailing spaces to strip()
        if not k <= len(body) <= k + 1:             # +1: some encoders append a checksum char
            return None
        try:
            v = 0
            for c in body[:k]:
                v = v << 6 | table[c]
        except KeyError:
            return None
        out += v.to_bytes(k // 4 * 3, "big")[:n]
    return _t(bytes(out)) if out else None


def xx_dec(t):
    return uu_dec(t, _UNXX)


# Polybius square (5x5, I/J merged, row then column, 1-based) and tap code (the same idea on the "prison" grid that
# merges C/K instead, each coordinate knocked as a run of dots). Letters only: the decoder returns lowercase letters,
# words split where the input had "/" or "|" (or each space-separated token is a whole word), never past a stray symbol.
_POLY = "abcdefghiklmnopqrstuvwxyz"
_TAP = "abcdefghijlmnopqrstuvwxyz"


def _sq_pos(c, grid):
    c = c.lower()
    c = {"j": "i"}.get(c, c) if grid is _POLY else {"k": "c"}.get(c, c)
    i = grid.find(c)
    return None if i < 0 or not c.isalpha() else divmod(i, 5)


def polybius_enc(s, sep=" ", word=None, grid=_POLY):
    words = [[f"{r + 1}{c + 1}" for r, c in filter(None, (_sq_pos(ch, grid) for ch in w))] for w in s.split()]
    words = [w for w in words if w]
    if word is None:
        return sep.join(x for w in words for x in w)
    return word.join(sep.join(w) for w in words)


def _sq_word(digits, grid):
    if not digits or len(digits) % 2:
        return None
    return "".join(grid[(int(digits[i]) - 1) * 5 + int(digits[i + 1]) - 1] for i in range(0, len(digits), 2))


def polybius_dec(t, grid=_POLY):
    t = t.strip()
    if len(t) > 20000 or not re.fullmatch(r"[1-5][1-5\s/|,.-]*", t) or sum(c.isdigit() for c in t) < 4:
        return None
    if re.search(r"[/|]", t):
        words = re.split(r"[/|]", t)
    elif re.search(r"\S\s{2,}\S", t):
        words = re.split(r"\s{2,}", t)
    else:
        toks = re.split(r"[\s,.-]+", t)
        words = [t] if all(len(x) == 2 for x in toks) else toks
    out = [_sq_word(re.sub(r"[\s,.-]", "", w), grid) for w in words if w.strip()]
    return None if not out or None in out else " ".join(out)


def tap_enc(s, tap=".", gap=" ", letter="  ", word=" / "):
    return word.join(letter.join(f"{tap * (r + 1)}{gap}{tap * (c + 1)}" for r, c in filter(None, (_sq_pos(ch, _TAP)
                                                                                                    for ch in w)))
                     for w in s.split() if any(_sq_pos(ch, _TAP) for ch in w))


def tap_dec(t):
    t = t.strip()
    if len(t) > 50000 or not re.fullmatch(r"[.*•·xX][.*•·xX\s/|]*", t) or len(set(re.sub(r"[\s/|]", "", t))) != 1:
        return None
    out = []
    for w in re.split(r"[/|]", t):
        runs = [len(r) for r in re.findall(r"[.*•·xX]+", w)]
        if not runs:
            continue
        if len(runs) % 2 or max(runs) > 5:
            return None
        out.append("".join(_TAP[(runs[i] - 1) * 5 + runs[i + 1] - 1] for i in range(0, len(runs), 2)))
    return " ".join(out) or None


_BR_LET = dict(zip(string.ascii_lowercase, "⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚⠅⠇⠍⠝⠕⠏⠟⠗⠎⠞⠥⠧⠺⠭⠽⠵"))
_BR_PUN = {",": "⠂", ";": "⠆", ":": "⠒", ".": "⠲", "!": "⠖", "?": "⠦", "'": "⠄", "-": "⠤", "/": "⠌", "(": "⠶",
           ")": "⠶", '"': "⠴"}
_UNBR_LET = {v: k for k, v in _BR_LET.items()}
_UNBR_PUN = {v: k for k, v in _BR_PUN.items() if k not in ')"'} | {"⠴": '"'}
_BR_DIG = dict(zip("1234567890", "⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚"))
_BR_ASCII = " A1B'K2L@CIF/MSP\"E3H9O6R^DJG>NTQ,*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)="  # North American Braille ASCII


def braille_enc(s, space=" "):
    """Grade 1 (uncontracted) Unicode Braille: ⠠ capital per letter, ⠼ number sign before a digit run, ⠰ letter sign
    when a-j follows digits."""
    out, num = [], False
    for c in s:
        if c.isdigit() and c in _BR_DIG:
            out.append(("" if num else "⠼") + _BR_DIG[c])
            num = True
            continue
        if num and c.lower() in "abcdefghij":
            out.append("⠰")
        num = num and c in ".,"
        if c.lower() in _BR_LET:
            out.append(("⠠" if c.isupper() else "") + _BR_LET[c.lower()])
        elif c == " ":
            out.append(space)
        else:
            out.append(_BR_PUN.get(c, c))
    return "".join(out)


def braille_dec(t):
    """Grade 1 Unicode Braille (U+2800 block, 6-dot cells) -> text; ⠀ or ASCII whitespace = space. None when the text
    isn't Braille or holds a cell outside the uncontracted letter/digit/punctuation set (contractions, 8-dot cells)."""
    t = t.strip()
    if not t or len(t) > 50000 or not all("\u2800" <= c <= "\u283f" or c in " \t\r\n" for c in t):
        return None
    out, num, cap, caps, letter, paren = [], False, False, False, False, False
    i = 0
    while i < len(t):
        c = t[i]
        i += 1
        if c in " \t\r\n\u2800":
            out.append(" " if c == "\u2800" else c)
            num = caps = False
            continue
        if c == "⠠":
            if i < len(t) and t[i] == "⠠":
                caps, i = True, i + 1
            else:
                cap = True
            continue
        if c == "⠼":
            num = True
            continue
        if c == "⠰":
            num, letter = False, True
            continue
        if num and c in _BR_DIG.values() and not letter:
            out.append("1234567890"["⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚".index(c)])
            continue
        if num and c in "⠲⠂":
            out.append("." if c == "⠲" else ",")
            continue
        num = letter = False
        if c in _UNBR_LET:
            ch = _UNBR_LET[c]
            out.append(ch.upper() if cap or caps else ch)
            cap = False
        elif c == "⠶":
            out.append(")" if paren else "(")
            paren = not paren
        elif c in _UNBR_PUN:
            out.append(_UNBR_PUN[c])
            caps = caps and c == "⠤"
        else:
            return None
    return "".join(out) or None


def braille_ascii_enc(s):
    """CyberChef "To Braille": each char through the North American Braille ASCII table (digits = lower cells)."""
    return "".join(chr(0x2800 + _BR_ASCII.index(c.upper())) if c.upper() in _BR_ASCII else c for c in s)


def braille_ascii_dec(t):
    t = t.strip()
    if not t or len(t) > 50000 or not all("\u2800" <= c <= "\u283f" or c in " \t\r\n" for c in t):
        return None
    return "".join(_BR_ASCII[ord(c) - 0x2800] if "\u2800" <= c <= "\u283f" else c for c in t).lower()


def wordrev(s):
    return " ".join(w[::-1] for w in s.split(" "))


def wordorder(s):
    return " ".join(reversed(s.split(" ")))


def _xor(s, k):
    return bytes(b ^ k for b in _u(s))


def _cands():
    """[(name, enc, dec|None)] in try order: the confirmed day codecs, cheap format variants, classical ciphers."""
    out = [(name, enc, dec) for _d, name, enc, dec, _f in DAYS]
    out += [
        ("plain", lambda s: s, lambda t: t),
        ("hex-upper", lambda s: _u(s).hex().upper(), DAYS[2][3]),
        ("hex-spaced", lambda s: " ".join(f"{b:02x}" for b in _u(s)), DAYS[2][3]),
        ("hex-spaced-upper", lambda s: " ".join(f"{b:02X}" for b in _u(s)), DAYS[2][3]),
        ("hex-0x", lambda s: " ".join(f"0x{b:02x}" for b in _u(s)),
         lambda t: _t(bytes(int(x, 16) for x in _toks(t)))),
        ("hex-colon", lambda s: ":".join(f"{b:02x}" for b in _u(s)), lambda t: _t(bytes.fromhex(t.replace(":", "")))),
        ("binary8-nospace", lambda s: "".join(f"{b:08b}" for b in _u(s)),
         lambda t: _t(int(t.strip(), 2).to_bytes(len(t.strip()) // 8, "big"))),
        ("binary7", lambda s: " ".join(f"{b:07b}" for b in _u(s)), DAYS[3][3]),
        ("decimal-comma", lambda s: ",".join(str(b) for b in _u(s)), DAYS[4][3]),
        ("decimal-comma-space", lambda s: ", ".join(str(b) for b in _u(s)), DAYS[4][3]),
        ("decimal3", lambda s: " ".join(f"{b:03d}" for b in _u(s)), DAYS[4][3]),
        ("octal", lambda s: " ".join(f"{b:o}" for b in _u(s)), DAYS[5][3]),
        ("octal-backslash", lambda s: "".join(f"\\{b:03o}" for b in _u(s)),
         lambda t: _t(bytes(int(x, 8) for x in re.findall(r"\\([0-7]{1,3})", t)))),
        ("url%XX", lambda s: "".join(f"%{b:02X}" for b in _u(s)), DAYS[6][3]),
        ("url-quote", lambda s: urllib.parse.quote(s), lambda t: urllib.parse.unquote(t)),
        ("url-quote-plus", lambda s: urllib.parse.quote_plus(s), lambda t: urllib.parse.unquote_plus(t)),
        ("html&#xh;", lambda s: "".join(f"&#x{ord(c):x};" for c in s), DAYS[7][3]),
        ("html&#xH;", lambda s: "".join(f"&#x{ord(c):X};" for c in s), DAYS[7][3]),
        ("html&#n;-alnum", lambda s: "".join(f"&#{ord(c)};" if c.isalnum() else html.escape(c) for c in s), DAYS[7][3]),
        ("json\\u-bare", lambda s: "".join(f"\\u{ord(c):04x}" for c in s), DAYS[8][3]),
        ("json\\U", lambda s: '"' + "".join(f"\\u{ord(c):04X}" for c in s) + '"', DAYS[8][3]),
        ("escape\\x", lambda s: "".join(f"\\x{b:02x}" for b in _u(s)),
         lambda t: _t(bytes(int(x, 16) for x in re.findall(r"\\x([0-9a-fA-F]{2})", t)))),
        ("escape\\x-quoted", lambda s: '"' + "".join(f"\\x{b:02x}" for b in _u(s)) + '"',
         lambda t: _t(bytes(int(x, 16) for x in re.findall(r"\\x([0-9a-fA-F]{2})", t)))),
        ("base32-nopad", lambda s: base64.b32encode(_u(s)).decode().rstrip("="),
         lambda t: _t(base64.b32decode(t.strip() + "=" * (-len(t.strip()) % 8)))),
        ("base32-lower", lambda s: base64.b32encode(_u(s)).decode().lower(),
         lambda t: _t(base64.b32decode(t.strip().upper()))),
        ("base32hex", lambda s: base64.b32hexencode(_u(s)).decode(), lambda t: _t(base64.b32hexdecode(t.strip()))),
        ("base64-nopad", lambda s: base64.b64encode(_u(s)).decode().rstrip("="), DAYS[0][3]),
        ("base64url", lambda s: base64.urlsafe_b64encode(_u(s)).decode(), DAYS[10][3]),
        ("base85", lambda s: base64.b85encode(_u(s)).decode(), lambda t: _t(base64.b85decode(t.strip()))),
        ("ascii85", lambda s: base64.a85encode(_u(s)).decode(), lambda t: _t(base64.a85decode(t.strip()))),
        ("ascii85-adobe", lambda s: base64.a85encode(_u(s), adobe=True).decode(),
         lambda t: _t(base64.a85decode(t.strip(), adobe=True))),
        ("base91", b91_enc, b91_dec),
        ("base58", b58_enc, b58_dec),
        ("base36", b36_enc, b36_dec),
        ("base62", b62_enc, b62_dec),
        ("base62-inv", lambda s: b62_enc(s, _B62_INV), lambda t: b62_dec(t, _B62_INV)),
        ("punycode-words", lambda s: " ".join(puny_enc(w) for w in s.split(" ")), puny_words_dec),
        ("punycode", puny_enc, puny_dec),
        ("xn--words", lambda s: idna_enc(s, force=True), lambda t: idna_dec(t, force=True)),
        ("idna-words", idna_enc, idna_dec),
        ("quoted-printable", lambda s: quopri.encodestring(_u(s)).decode(), lambda t: _t(quopri.decodestring(_u(t)))),
        ("quoted-printable-all", lambda s: "".join(f"={b:02X}" for b in _u(s)),
         lambda t: _t(quopri.decodestring(_u(t)))),
        ("uu", lambda s: codecs.encode(_u(s), "uu").decode(), uu_dec),
        ("uu-bare", uu_enc, uu_dec),
        ("uu-bare-space", lambda s: uu_enc(s, zero=" "), uu_dec),
        ("uu-begin644", lambda s: uu_enc(s, frame="644 data"), uu_dec),
        ("xx-bare", lambda s: uu_enc(s, _XX, zero=None), xx_dec),
        ("xx-begin644", lambda s: uu_enc(s, _XX, zero=None, frame="644 data", end=None), xx_dec),
        ("rot47", rot47, rot47),
        ("swapcase", lambda s: s.swapcase(), lambda t: t.swapcase()),
        ("upper", lambda s: s.upper(), None),
        ("wordrev", wordrev, wordrev),
        ("wordorder", wordorder, wordorder),
        ("qwerty-right", lambda s: qwerty_shift(s, 1), lambda t: qwerty_shift(t, -1)),
        ("qwerty-left", lambda s: qwerty_shift(s, -1), lambda t: qwerty_shift(t, 1)),
        ("morse", morse_enc, morse_dec),
        ("morse-3space", lambda s: morse_enc(s, word=" "), morse_dec),
        ("nato", nato_enc, nato_dec),
        ("a1z26", a1z26_enc, a1z26_dec),
        ("a1z26-comma", lambda s: a1z26_enc(s, sep=","), lambda t: a1z26_dec(t, sep=",")),
        ("polybius", lambda s: polybius_enc(s, sep=""), polybius_dec),
        ("polybius-spaced", polybius_enc, polybius_dec),
        ("polybius-words", lambda s: polybius_enc(s, word=" / "), polybius_dec),
        ("polybius-wordruns", lambda s: polybius_enc(s, sep="", word=" "), polybius_dec),
        ("polybius-comma", lambda s: polybius_enc(s, sep=","), polybius_dec),
        ("tapcode-digits", lambda s: polybius_enc(s, grid=_TAP), lambda t: polybius_dec(t, _TAP)),
        ("tapcode", tap_enc, tap_dec),
        ("tapcode-nowords", lambda s: tap_enc(s, word="  "), tap_dec),
        ("tapcode-knock", lambda s: tap_enc(s, tap="x"), tap_dec),
        ("braille", braille_enc, braille_dec),
        ("braille-blank", lambda s: braille_enc(s, space="\u2800"), braille_dec),
        ("braille-ascii", braille_ascii_enc, braille_ascii_dec),
    ]
    out += [(f"bacon{a}-{tr}{('-keep', '-keep-cc')[cc] if k else ''}",
             (lambda a, tr, k, cc: lambda s: bacon_enc(s, a, tr, k, cc))(a, tr, k, cc),
             (lambda a, tr, k: lambda t: bacon_dec(t, a, tr, k))(a, tr, k))
            for a in (26, 24) for tr in _BACON_TR for k in (False, True) for cc in (False, True)
            if not (cc and (not k or tr[0] in "01"))]
    out += [(f"caesar{n}", (lambda n: lambda s: rot(s, n))(n), (lambda n: lambda t: rot(t, -n))(n))
            for n in range(1, 26) if n != 13]
    out += [(f"rail{n}", (lambda n: lambda s: rail_enc(s, n))(n), (lambda n: lambda t: rail_dec(t, n))(n))
            for n in range(2, 7)]
    out += [(f"affine{a},{b}", (lambda a, b: lambda s: affine(s, a, b))(a, b),
             (lambda a, b: lambda t: affine_inv(t, a, b))(a, b)) for a in _AFFINE_A for b in range(26)]
    out += [(f"xor{k:#04x}-hex", (lambda k: lambda s: _xor(s, k).hex())(k),
             (lambda k: lambda t: bytes(b ^ k for b in bytes.fromhex(t.strip())).decode())(k)) for k in range(1, 256)]
    out += [(f"xor{k:#04x}-base64", (lambda k: lambda s: base64.b64encode(_xor(s, k)).decode())(k),
             (lambda k: lambda t: bytes(b ^ k for b in base64.b64decode(_b64pad(t))).decode())(k)) for k in range(1, 256)]
    # chained pairs of confirmed codecs, inner first ("base64 of the reversed text", "hex of rot13", ...)
    for (_d1, n1, e1, d1, _f1), (_d2, n2, e2, d2, _f2) in itertools.product(DAYS, DAYS):
        if n1 != n2:
            out.append((f"{n2}({n1})", (lambda e1, e2: lambda s: e2(e1(s)))(e1, e2),
                        (lambda d1, d2: lambda t: d1(d2(t)))(d1, d2)))
    return out


CANDIDATES = _cands()


def _hint_keys(hints):
    """Vigenère keys from the challenge title / prompt words (and the words run together)."""
    keys = []
    for h in hints or ():
        words = re.findall(r"[A-Za-z]{3,}", str(h))
        for w in words + ["".join(words)]:
            w = w.lower()
            if w and w not in keys:
                keys.append(w)
    return keys[:40]


def _hint_cands(hints):
    out = []
    for k in _hint_keys(hints):
        out.append((f"vigenere:{k}", (lambda k: lambda s: vigenere(s, k))(k), (lambda k: lambda t: vigenere(t, k, -1))(k)))
        out.append((f"beaufort:{k}", (lambda k: lambda s: vigenere(atbash(s), k))(k), None))
    return out


def _fit_affine(plain, blob):
    """(a, b) when the blob is plain under one affine letter map (case kept, everything else unchanged), else None."""
    if len(plain) != len(blob):
        return None
    pairs = set()
    for p, c in zip(plain, blob):
        if p.isascii() and p.isalpha():
            if not (c.isascii() and c.isalpha()) or p.isupper() != c.isupper():
                return None
            pairs.add((ord(p.lower()) - 97, ord(c.lower()) - 97))
        elif p != c:
            return None
    for a in (1,) + _AFFINE_A:
        for b in range(26):
            if all((a * x + b) % 26 == y for x, y in pairs):
                return a, b
    return None


def _fit_subst(plain, blob):
    """A consistent one-to-one character map plain -> blob (same length), else None. Letters the sentence never shows
    are unknown: enc passes them through (fine for re-encoding the same sentence's fragments)."""
    if len(plain) != len(blob):
        return None
    m, back = {}, {}
    for p, c in zip(plain, blob):
        if m.setdefault(p, c) != c or back.setdefault(c, p) != p:
            return None
    if all(k == v for k, v in m.items()):
        return None
    return m


def infer(plain, blob, hints=()):
    """Today's codec from the Single: (name, enc) of the first encoder E with E(plain) == blob.strip() (exact GM bytes),
    else of the first decoder D with D(blob) == plain, else a fitted affine / learned substitution map. None = no
    candidate explains the blob (the today-probe then reports "unidentified" and builds no case)."""
    if not plain or blob is None:
        return None
    blob = _t(blob)
    want = blob.strip()
    p = plain.strip()
    cands = CANDIDATES + _hint_cands(hints)
    for name, enc, _dec in cands:
        try:
            if enc(p).strip() == want:
                return name, enc
        except Exception:  # noqa: BLE001
            continue
    for name, enc, dec in cands:
        if dec is not None and safe(dec, want) == p:
            return name, enc
    ab = _fit_affine(p, want)
    if ab:
        a, b = ab
        return f"affine{a},{b}", lambda s: affine(s, a, b)
    sub = _fit_subst(p, want)
    if sub:
        return "subst", lambda s: "".join(sub.get(c, c) for c in s)
    return None


def plaintext(blob, slug, deadline=None):
    """The Single's decoded sentence holding `slug`: lib.decode.decode_chunk -> peel -> every candidate decoder -> the
    fixed warmups sentence (identical D1-D13, so an unknown codec can still be fitted against it)."""
    from lib import decode
    text = _t(blob)
    if not slug:
        return None
    try:
        d = decode.decode_chunk(text.strip())
    except Exception:  # noqa: BLE001
        d = None
    if d and slug in d:
        return d.strip()
    try:
        out, _steps = decode.peel(_u(text), lambda t: slug in t, max_nodes=4000, deadline=deadline)
    except Exception:  # noqa: BLE001
        out = None
    if out and slug in out:
        return out.strip()
    for _name, _enc, dec in CANDIDATES:
        if dec is not None:
            got = safe(dec, text.strip())
            if got and slug in got:
                return got.strip()
    return SENTENCE.format(slug=slug)


def infer_case(case_dir, hints=()):
    """(name, enc, plain) for a Single Solve regression case (contract + artifacts + expected), else None."""
    from pathlib import Path
    case = Path(case_dir)
    try:
        contract = json.loads((case / "contract.json").read_text())
        expected = json.loads((case / "expected.json").read_text())
    except (OSError, ValueError):
        return None
    slug = next((v for v in expected.values() if isinstance(v, str) and SLUG.fullmatch(v)), None)
    q = (contract.get("questions") or [{}])[0]
    art = case / "artifacts" / str(q.get("artifact") or "blob.txt")
    if not art.exists():
        files = [f for f in (case / "artifacts").glob("*") if f.is_file()]
        if len(files) != 1:
            return None
        art = files[0]
    blob = art.read_bytes().decode("utf-8", "replace")
    plain = plaintext(blob, slug)
    if not plain:
        return None
    hints = tuple(hints) + tuple(str(contract.get(k) or "") for k in ("name", "prompt"))
    got = infer(plain, blob, hints)
    if not got:
        return None
    return got[0], got[1], plain


# --------------------------------------------------------------------- speculative free-text decoders for lib.decode
def _top(p, outs, k=3):
    from lib.decode import _bigram
    seen = []
    for o in outs:
        if o and o != p and o not in seen:
            seen.append(o)
    return sorted(seen, key=_bigram, reverse=True)[:k]


SPECULATIVE_FREE = (
    ("rot47", lambda p: [rot47(p)]),
    ("swapcase", lambda p: [p.swapcase()]),
    ("wordrev", lambda p: [wordrev(p)]),
    ("qwerty", lambda p: _top(p, [qwerty_shift(p, 1), qwerty_shift(p, -1)], 2)),
    ("rail", lambda p: _top(p, [rail_dec(p, n) for n in range(2, 7)])),
    ("affine", lambda p: _top(p, [affine_inv(p, a, b) for a in _AFFINE_A for b in range(26)])),
    ("punycode", lambda p: [p[:len(p) - len(p.lstrip())] + puny_dec(p)]),
    ("braille", lambda p: [b for b in (braille_dec(p),) if b]),
)


def register_speculative():
    """Hand the keyless free-text decoders to lib.decode's joint free-line assignment as day=None (speculative)
    entries: only for a blob that has more lines than any confirmed codec day and a free line the confirmed codecs
    can't cover. Idempotent."""
    from lib import decode
    for name, fn in SPECULATIVE_FREE:
        decode.register_free(name, None, fn)


if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]:
        print(f, (infer_case(f) or ("unidentified",))[0])
