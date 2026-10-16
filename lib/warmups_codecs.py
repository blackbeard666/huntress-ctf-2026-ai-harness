"""Warmups lane codec library: every day's line codec as an exact ENCODER + decoder, plus a broad try-list of classical
encoders for identifying an unknown day's codec from its Single Solve.

Warmups (D1-D15): each Single is one sentence -- "Nice work decoding this warmup! To solve, submit this exact answer to
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
import collections
import html
import itertools
import json
import quopri
import os
import re
import string
import unicodedata
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
    (15, "rot47", lambda s: rot47(s), lambda t: rot47(t), True),   # D15 "Room Forty-Seven": punctuation spins too
    # D16 "Dot Com" ("Sixteen little symbols ... Dot dot dot"): Morse of the UTF-8 HEX digits, one space between symbols
    (16, "morse-hex", lambda s: " ".join(_MORSE[c.upper()] for c in _u(s).hex()),
     lambda t: _t(bytes.fromhex(morse_dec(t).replace(" ", ""))), False),
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


# Morse in any 2-symbol alphabet: glyphs (•/—, ·/−, ./_, 1/0, x/o ...) or symbol words (dit/dah, "di-dah-dit",
# CyberChef "DotDash"/"dash dot", beep/boop), with any gap separators (space, /, |, \, comma, newline).
_MORSE_GAP = set(" \t\r\n/|\\,;:")
_MORSE_DOT = {".", "·", "•", "∙", "⋅", "*", "dit", "dot", "short"}
_MORSE_DASH = {"-", "−", "–", "—", "‒", "_", "dah", "dash", "long"}
_MORSE_WORDS = re.compile(r"(dash|dah|da|dot|dit|di|beep|boop|bip|bop|blip|bleep|long|short)", re.I)


def morse_alt_enc(s, dot=".", dash="-", intra="", letter=" ", word=" / ", ditdah=False):
    def one(c):
        code = _MORSE.get(c.upper(), "")
        if ditdah:   # "di-dah-dit": a non-final dot is "di"
            return intra.join(("dit" if i == len(code) - 1 else "di") if x == "." else "dah" for i, x in enumerate(code))
        return intra.join(dot if x == "." else dash for x in code)
    return word.join(letter.join(one(c) for c in w if c.upper() in _MORSE) for w in s.split(" "))


def _morse_tokens(t):
    """(symbols, gaps) with gaps[i] between symbols[i] and [i+1], or None: symbol words when the text is only
    symbol words + gap punctuation, else glyphs = every non-gap character."""
    parts = _MORSE_WORDS.split(t)
    if len(parts) > 3 and all(re.fullmatch(r"[\s\-/|\\,;:]*", g) for g in parts[::2]):
        return [{"di": "dit", "da": "dah"}.get(p.lower(), p.lower()) for p in parts[1::2]], parts[2:-1:2]
    syms, gaps, gap = [], [], None
    for c in t:
        if c in _MORSE_GAP:
            gap = (gap or "") + c
        else:
            if syms:
                gaps.append(gap or "")
            syms.append(c)
            gap = None
    return syms, gaps


def morse_alt_dec(t):
    """Morse under any 2-symbol alphabet and any gap separators -> lowercase text, else None. Gap classes ranked by
    frequency: in-letter (most common; "" for glyphs), letter gap (next), anything rarer = word gap. A symbol pair
    with no known dot/dash reading (1/0, beep/boop, x/o) is decoded both ways; the reading with fewer invalid codes,
    then the more English-looking letters, wins."""
    t = t.strip()
    if len(t) < 5:
        return None
    syms, gaps = _morse_tokens(t)
    alpha = sorted(set(syms))
    if len(alpha) != 2 or len(syms) < 6:
        return None
    ranked = [g for g, _n in collections.Counter(gaps).most_common()]
    if len(ranked) < 2:
        return None
    if "" in ranked:
        ranked.remove("")
        ranked.insert(0, "")
    intra, lgap = ranked[0], ranked[1]
    if not re.fullmatch(r"[ \-]?", intra):   # in-letter joins: adjacent, "-" (di-dah) or one space (dash dot)
        return None
    words, cur, code = [], [], [syms[0]]
    for s, g in zip(syms[1:] + [None], gaps + [None]):
        if g == intra:
            code.append(s)
            continue
        cur.append(code)
        if g is not None and g != lgap:
            words.append(cur)
            cur = []
        code = [s]
    words.append(cur)
    a, b = alpha
    if a in _MORSE_DOT or b in _MORSE_DASH:
        orders = [a]
    elif b in _MORSE_DOT or a in _MORSE_DASH:
        orders = [b]
    else:
        orders = [a, b]
    best = None
    for dot in orders:
        bad, out = 0, []
        for w in words:
            ls = []
            for c in w:
                x = _UNMORSE.get("".join("." if s == dot else "-" for s in c))
                bad += x is None
                ls.append(x or "")
            out.append("".join(ls))
        txt = " ".join(out).lower()
        n = sum(len(w) for w in words)
        letters = [c for c in txt if c.isalpha()]
        score = (-bad, sum(c in "etaoinshrdlu" for c in letters) / max(1, len(letters)))
        if n >= 3 and bad * 20 <= n and (best is None or score > best[0]):
            best = (score, txt)
    return best[1] if best else None


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


# ROT8000 (rot8000.com / CyberChef "ROT8000"): rotate by half the BMP's valid code points -- no controls, spaces or
# surrogates -- so it is its own inverse; printable ASCII lands on CJK ideographs U+7C21.. and ASCII spaces stay.
_R8K_RANGES = ((33, 127), (161, 5760), (5761, 8192), (8203, 8232), (8234, 8239), (8240, 8287), (8288, 12288),
               (12289, 55296), (57344, 65536))
_R8K_VALID = [c for a, b in _R8K_RANGES for c in range(a, b)]
_R8K_HALF = len(_R8K_VALID) // 2
_R8K_INDEX = {c: i for i, c in enumerate(_R8K_VALID)}


def rot8000(s):
    v, h, idx = _R8K_VALID, _R8K_HALF, _R8K_INDEX
    return "".join(chr(v[(idx[ord(c)] + h) % (2 * h)]) if ord(c) in idx else c for c in s)


def rot8000_dec(t):
    """Undo ROT8000. None unless >= 4 non-whitespace chars, under 10% of them ASCII and >= 90% rotating back into
    printable ASCII (genuine CJK / Braille / other-script text rotates elsewhere)."""
    if not isinstance(t, str) or len(t) > 200000:
        return None
    t = t.strip()
    chars = [c for c in t if not c.isspace()]
    if len(chars) < 4 or sum(c.isascii() for c in chars) > 0.1 * len(chars):
        return None
    out = rot8000(t)
    body = [c for c in out if not c.isspace()]
    if sum(33 <= ord(c) <= 126 for c in body) < 0.9 * len(body):
        return None
    return out


# ROT18 = ROT13 letters + ROT5 digits (tr 'A-Za-z0-9' 'N-ZA-Mn-za-m5-90-4'); ROT5 = digits alone; CyberChef "ROT13"
# with "Rotate numbers" turns digits by amount % 10 (amount 13 -> digits +3, not +5).
def rotnum(s, n=13, d=5):
    return "".join(chr((ord(c) - 48 + d) % 10 + 48) if "0" <= c <= "9" else c for c in rot(s, n))


def _rotnum_ok(t):
    """Prose with digits only as standalone numbers (slug -NN): a digit inside a word is hex/base64/leet, and a line
    without digits is plain rot-N (the confirmed codecs' job)."""
    if not isinstance(t, str) or len(t) > 50000:
        return False
    toks = re.findall(r"[A-Za-z0-9]+", t)
    digits = sum(c.isdigit() for c in t)
    return (digits and any(c.isascii() and c.isalpha() for c in t)
            and not any(re.search(r"[A-Za-z]", w) and re.search(r"\d", w) for w in toks))


def rotnum_dec(t, n=13, d=5):
    return rotnum(t, -n, -d) if _rotnum_ok(t) else None


def rotnum_free(p):
    """Speculative free-line candidates: ROT18, ROT5 alone, CyberChef ROT13+numbers (digits -3), then the best letter
    shift by bigrams with digits back by 5 / by the shift % 10 (a 3-letter Mastery fragment can't pick its shift)."""
    if not _rotnum_ok(p):
        return []
    from lib.decode import _bigram
    n = max(range(26), key=lambda k: (_bigram(rot(p, -k)), k == 13))
    return list(dict.fromkeys(rotnum(p, -a, -d) for a, d in ((13, 5), (0, 5), (13, 3), (n, 5), (n, n % 10)) if d))


_ROWS =("`1234567890-=", "qwertyuiop[]\\", "asdfghjkl;'", "zxcvbnm,./")


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


# "Typed on the wrong keyboard": the same physical keys read under another layout (XKB us / us(dvorak) / us(colemak)
# / fr). Each layout = (unshifted, shifted) over the 47 ANSI keys in US order TLDE AE01-12, AD01-12 BKSL, AC01-11,
# AB01-10; "\0" = a dead key (no char typed: that key is left out of the map).
_KBD = {
    "qwerty": ("`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./",
               "~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:\"ZXCVBNM<>?"),
    "dvorak": ("`1234567890[]',.pyfgcrl/=\\aoeuidhtns-;qjkxbmwvz",
               "~!@#$%^&*(){}\"<>PYFGCRL?+|AOEUIDHTNS_:QJKXBMWVZ"),
    "colemak": ("`1234567890-=qwfpgjluy;[]\\arstdhneio'zxcvbkm,./",
                "~!@#$%^&*()_+QWFPGJLUY:{}|ARSTDHNEIO\"ZXCVBKM<>?"),
    "azerty": ("²&é\"'(-è_çà)=azertyuiop\0$*qsdfghjklmùwxcvbn,;:!",
               "~1234567890°+AZERTYUIOP\0£µQSDFGHJKLM%WXCVBN?./§"),
}


def _kbd_map(src, dst):
    m = {}
    for a, b in zip(_KBD[src][0] + _KBD[src][1], _KBD[dst][0] + _KBD[dst][1]):
        if a != "\0" and b != "\0":
            m.setdefault(a, b)
    return m


_KBD_MAPS = {(a, b): _kbd_map(a, b) for a in _KBD for b in _KBD if a != b}


def kbd_swap(s, src, dst):
    """Text typed by a `src` typist on a machine set to `dst` (case rides the shift level; unmapped chars unchanged)."""
    m = _KBD_MAPS[(src, dst)]
    return "".join(m.get(c, c) for c in s)


_KBD_WORD = re.compile(r"[\"'(]*(?:[A-Za-z]+(?:'[a-z]+)?|[a-z]+(?:-[a-z]+)*-\d+|\d+)[.,!?:;)\"']*")
_KBD_KNOWN = set(re.findall(r"[a-z]+", SENTENCE.lower())) - {"slug"} | set(
    "a an and are as at be but by for from have he i if in is it not of on or she that the they this was we with you"
    .split())


def _kbd_score(s):
    """Letter-bigram English score, plus the share of known words (the fixed warmups sentence: AZERTY keeps most
    letters, 'Nice zork'), minus the share a wrong layout breaks: punctuation / digits inside a word, a capital after
    a lowercase letter ('zqr;up/', 'maoy.pS'). A slug 'amber-falcon-42' is a clean word."""
    from lib.decode import _bigram
    words = s.split()
    n = max(len(words), 1)
    junk = sum(not _KBD_WORD.fullmatch(w) or bool(re.search(r"[a-z][A-Z]", w)) for w in words)
    known = sum(w.strip("\"'(.,!?:;)").lower() in _KBD_KNOWN for w in words)
    return _bigram(s) + 2.0 * known / n - 3.0 * junk / n


def kbd_dec(t, src, dst):
    """Undo kbd_swap(., src, dst). None unless the text reads as layout-garbled: the swap back must change it and read
    clearly more English than the input -- plain prose / base64 / hex are not keyboard text."""
    if not isinstance(t, str) or not t.strip() or len(t) > 50000:
        return None
    from lib.decode import _bigram
    out = kbd_swap(t, dst, src)
    if out == t or _bigram(out) < -6.6:
        return None
    sc = _kbd_score(out)
    return out if sc >= -5.8 and sc - _kbd_score(t) >= 0.7 else None


_KBD_PAIRS = [(a, b) for a in _KBD for b in _KBD if a != b and "qwerty" in (a, b)]


def kbd_free(p):
    """Mastery free line: every QWERTY<->layout reading that passes kbd_dec, best English first."""
    lead = p[:len(p) - len(p.lstrip())]
    outs = dict.fromkeys(lead + o for o in (kbd_dec(p.strip(), a, b) for a, b in _KBD_PAIRS) if o)
    return sorted(outs, key=_kbd_score, reverse=True)[:2]


def _rail_rows(L, n, offset=0):
    """Rail index of each of L positions: zig-zag over n rails, phase shifted by `offset` (CyberChef Rail Fence
    Cipher: row = n-1-|cycle/2 - (pos+offset) % cycle|, cycle = 2n-2; offset 0 = the classic fence from the top)."""
    if n < 2:
        return [0] * L
    cyc = 2 * n - 2
    return [n - 1 - abs(n - 1 - (i + offset) % cyc) for i in range(L)]


def rail_enc(s, n, offset=0):
    rows = _rail_rows(len(s), n, offset)
    return "".join(s[i] for i in sorted(range(len(s)), key=rows.__getitem__))


def rail_dec(t, n, offset=0):
    rows = _rail_rows(len(t), n, offset)
    out = [""] * len(t)
    for c, i in zip(t, sorted(range(len(t)), key=rows.__getitem__)):
        out[i] = c
    return "".join(out)


_RAIL_MAX = 20   # rails 2-20, every offset 0..2n-3 (361 fences)


def rail_keys(L, nmax=_RAIL_MAX):
    """[(n, offset)] rail fences that differ on a length-L text (n < L), classic offset-0 fences first."""
    keys = [(n, 0) for n in range(2, min(nmax, L - 1) + 1)]
    return keys + [(n, o) for n in range(2, min(nmax, L - 1) + 1) for o in range(1, 2 * n - 2)]


_SLUG_PIECE = re.compile(r"[a-z]*(?:-[a-z]+)*(?:-\d*)?|\d+")
_SLUG_TAIL = re.compile(r"[a-z0-9-]*\s*$")


def _crib_piece(c):
    """How many crib characters reading c confirms: len(c) when it is the whole sentence or a crib substring, len(head)
    for a crib tail + the start of a slug, 1 for a hyphenated slug-shaped piece (words-words-NN); 0 = not a piece."""
    if c.startswith(_CRIB) and SLUG.fullmatch(c[len(_CRIB):].strip()):
        return len(c)
    if len(c) >= 4 and c in _CRIB:
        return len(c)
    m = _SLUG_TAIL.search(c)
    head, tail = c[:m.start()], m.group().rstrip()
    if not _SLUG_PIECE.fullmatch(tail):
        return 0
    if head:
        return len(head) if len(head) >= 2 and _CRIB.endswith(head) and (not tail or tail[0].isalpha()) else 0
    return int(len(tail) >= 4 and "-" in tail.strip("-") and "--" not in tail)


def rail_free(p):
    """Rail fence (rails 2-20 x every offset) of a free line. A transposition keeps the letter multiset, so a line that
    is an anagram of the sentence (or of a piece of it) is cheap to brute-force: readings that ARE the sentence / a
    contiguous piece of it win (most crib characters confirmed, then bigram), at most 3; otherwise the 3 best by bigram
    over offset-0 rails 2-6 as before. Leading spaces may be ciphertext (a rail starting with one): the raw line and its
    stripped form are both tried."""
    from lib.decode import _bigram
    lead = p[:len(p) - len(p.lstrip())]
    hits, seen = [], set()
    for pre, t in ((lead, p[len(lead):].rstrip("\r\n")), ("", p.rstrip("\r\n")))[:2 if lead else 1]:
        if len(t) < 3:
            continue
        seen.add(t)
        for n, o in rail_keys(len(t)):
            c = rail_dec(t, n, o)
            if c in seen:
                continue
            seen.add(c)
            k = _crib_piece(c)
            if k:
                hits.append((k, _bigram(c), pre + c))
    if hits:
        return [c for _k, _b, c in sorted(hits, reverse=True)[:3]]
    return _top(p, [rail_dec(p, n) for n in range(2, 7)])


def rail_solve(blob):
    """(name, sentence, enc) when the blob is the warmups sentence under a rail fence of 2-20 rails at any offset: the
    multiset must equal the crib's plus a slug's (anagram cue), then the one fence that reads crib + slug wins."""
    try:
        t = _t(blob).strip("\r\n")   # spaces are ciphertext: a rail may start or end with one
        if len(t) <= len(_CRIB) + 4:
            return None
        rest = collections.Counter(t)
        rest.subtract(_CRIB)
        if min(rest.values()) < 0 or any(not (ch.islower() or ch.isdigit() or ch == "-") for ch, v in rest.items() if v):
            return None
        for n, o in rail_keys(len(t)):
            c = rail_dec(t, n, o)
            if c.startswith(_CRIB) and SLUG.fullmatch(c[len(_CRIB):]):
                return (f"rail{n}" + (f"-off{o}" if o else ""), c,
                        (lambda n, o: lambda s: rail_enc(s, n, o))(n, o))
    except Exception:  # noqa: BLE001
        pass
    return None


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


# ------------------------------------------------- polyalphabetic family, keyed: solved by the fixed-sentence crib
# c = p + k (vigenere / gronsfeld / trithemius), c = k - p (beaufort), c = p - k (variant beaufort); autokey = primer
# then the plaintext letters themselves (pycipher Autokey). Letters-only key advance (pycipher/CyberChef) or `every`
# char advances it; case and non-letters kept.
_POLY_MODES = ("vigenere", "beaufort", "variant")


def _poly_enc1(x, k, mode):
    return (x + k) % 26 if mode == "vigenere" else (k - x) % 26 if mode == "beaufort" else (x - k) % 26


def _poly_dec1(y, k, mode):
    return (y - k) % 26 if mode == "vigenere" else (k - y) % 26 if mode == "beaufort" else (y + k) % 26


def _key_ints(key):
    return [int(c) if c.isdigit() else ord(c.lower()) - 97 for c in str(key) if c.isdigit() or c.isalpha()] \
        if not isinstance(key, (list, tuple)) else list(key)


def poly(s, key, mode="vigenere", auto=False, every=False, decode=False):
    """Polyalphabetic en/decoder. key: letters, Gronsfeld digits, or a list of shifts (autokey: the primer; autokey is
    letters-only)."""
    ks = _key_ints(key)
    if not ks:
        return s
    out, i = [], 0
    for j, c in enumerate(s):
        if c.isascii() and c.isalpha():
            base = 97 if c.islower() else 65
            n = j if every else i
            k = ks[n] if auto else ks[n % len(ks)]
            x = ord(c) - base
            y = _poly_dec1(x, k, mode) if decode else _poly_enc1(x, k, mode)
            if auto:
                ks.append(y if decode else x)
            out.append(chr(y + base))
            i += 1
        else:
            out.append(c)
    return "".join(out)


def trithemius(s, start=0, decode=False):
    return poly(s, [(start + i) % 26 for i in range(26)], decode=decode)


def _crib_stream(plain, ct, mode, every):
    """[(pos, key)] the cipher letters imply against the crib, or None when a non-letter / case-class doesn't line up."""
    out, i = [], 0
    for j, (p, c) in enumerate(zip(plain, ct)):
        pa, ca = p.isascii() and p.isalpha(), c.isascii() and c.isalpha()
        if pa != ca or (not pa and p != c):
            return None
        if pa:
            x, y = ord(p.lower()) - 97, ord(c.lower()) - 97
            k = (y - x) % 26 if mode == "vigenere" else (y + x) % 26 if mode == "beaufort" else (x - y) % 26
            out.append((j if every else i, k, x))
            i += 1
    return out


def _crib_fit(stream, min_letters=8):
    """(kind, key) for the shortest explanation of a crib key stream: ('auto', primer) / ('prog', start) /
    ('key', shifts with smallest period), else None. Needs >= 2 key cycles of evidence."""
    n = len(stream)
    if n < min_letters:
        return None
    xs = {pos: x for pos, _k, x in stream}
    # progressive (Trithemius): k = start + position
    st = {(k - pos) % 26 for pos, k, _x in stream}
    if len(st) == 1:
        return "prog", st.pop()
    for per in range(1, n // 2):
        key = {}
        if all(key.setdefault(pos % per, k) == k for pos, k, _x in stream) and len(key) == per:
            if per == 1 and key[0] == 0:
                return None
            return "key", [key[i] for i in range(per)]
    # autokey: k[pos] == plaintext letter at pos - L (letters-only positions), >= 6 such checks
    if any(i not in xs for i in range(n)):
        return None
    for L in range(1, n - 5):
        if all(xs[pos - L] == k for pos, k, _x in stream if pos >= L):
            return "auto", L
    return None


def _hint_fit(stream, hints, min_letters=8):
    """('hint', (word, phase)) when the crib key stream is a title/prompt key read from some phase (periodic, so a
    running key = the prompt's letters fits too): keys longer than half the crib that _crib_fit can't see."""
    if len(stream) < min_letters:
        return None
    for w in _hint_keys(hints):
        ks = [ord(c) - 97 for c in w]
        n = len(ks)
        for ph in range(n):
            if all(ks[(pos + ph) % n] == k for pos, k, _x in stream):
                return "hint", (w, ph)
    return None


def crib_key(plain, ct, min_letters=8, hints=()):
    """[(name, (key, mode, auto, every))] for every polyalphabetic family that maps crib `plain` onto the cipher text
    `ct` (aligned at position 0, compared over the shorter length); poly(t, *spec, decode=True) decodes the WHOLE ct.
    hints (title / prompt): a key too long for the crib's period search is matched against their words / letters."""
    m = min(len(plain), len(ct))
    found = []
    for every in (False, True):
        for mode in _POLY_MODES:
            st = _crib_stream(plain[:m], ct[:m], mode, every)
            if not st:
                continue
            fit = _crib_fit(st, min_letters) or (_hint_fit(st, hints, min_letters) if hints else None)
            if not fit:
                continue
            kind, v = fit
            tag = "-every" if every else ""
            if kind == "key":
                ks = "".join(chr(97 + k) for k in v)
                name = (f"gronsfeld:{''.join(map(str, v))}" if mode == "vigenere" and max(v) < 10 and len(v) > 1
                        else f"{mode}:{ks}") + tag
                found.append((name, (v, mode, False, every)))
            elif kind == "hint":
                w, ph = v
                ks = [ord(c) - 97 for c in w[ph:] + w[:ph]]
                found.append((f"{mode}:{w}" + (f"@{ph}" if ph else "") + tag, (ks, mode, False, every)))
            elif kind == "prog":
                if mode == "vigenere":
                    found.append((f"trithemius:{v}{tag}", ([(v + i) % 26 for i in range(26)], mode, False, every)))
            elif not every:   # autokey: primer = first L key values (pre-plaintext region)
                ks = {pos: k for pos, k, _x in st}
                primer = [ks[i] for i in range(v)]
                found.append((f"autokey-{mode}:{''.join(chr(97 + k) for k in primer)}", (primer, mode, True, False)))
    return found


_CRIB = SENTENCE.split("{slug}")[0]


def crib_solve(blob, hints=()):
    """(name, sentence, enc) when the blob is the warmups sentence under a polyalphabetic cipher (key derived from the fixed
    87-char prefix, slug decoded with it; a key longer than the prefix can show is matched against the hints), else
    None."""
    t = _t(blob).strip()
    if len(t) <= len(_CRIB):
        return None
    for name, (key, mode, auto, every) in crib_key(_CRIB, t, min_letters=20, hints=hints):
        try:
            got = poly(t, key, mode, auto, every, decode=True)
        except Exception:  # noqa: BLE001
            continue
        if got[:len(_CRIB)].lower() == _CRIB.lower() and SLUG.fullmatch(got[len(_CRIB):].lower()):
            enc = (lambda key, mode, auto, every, up: lambda x: (lambda y: y.upper() if up else y)(
                poly(x, key, mode, auto, every)))(key, mode, auto, every, not any(c.islower() for c in t))
            return name, _CRIB + got[len(_CRIB):].lower(), enc
    return None


def crib_fragment(p):
    """Mastery free-text fragment (raw, spacing intact) under a polyalphabetic cipher, key restarting per fragment:
    try the fixed sentence at every offset as the crib -> decoded fragments, best first. [] when nothing fits."""
    out = []
    s = p
    for off in range(len(_CRIB)):
        crib = _CRIB[off:]
        m = min(len(crib), len(s))
        if sum(c.isalpha() for c in s[:m]) < 8:
            break
        for _name, (key, mode, auto, every) in crib_key(crib, s, min_letters=8):
            try:
                got = poly(s, key, mode, auto, every, decode=True)
            except Exception:  # noqa: BLE001
                continue
            if got[:m].lower() == crib[:m].lower():
                got = got[:m] + got[m:].lower() if s[m:] and not any(c.islower() for c in s) else got
                if got not in out:
                    out.append(got)
        if out:
            return out
    return out


# keyword / simple substitution: the crib shows 21 of 26 plain letters, so the map is learned from the blob alone; only
# f j q y z (slug-only) stay unseen and are resolved by elimination + the slug word lists (lib.slug)
_LC = string.ascii_lowercase


def keyword_alpha(key):
    """Keyword cipher alphabet: the key's letters (first occurrence each) then the rest of a-z in order."""
    out = []
    for c in (key or "").lower() + _LC:
        if c in _LC and c not in out:
            out.append(c)
    return "".join(out)


def keyword_enc(s, key):
    a = keyword_alpha(key)
    return s.translate(str.maketrans(_LC + _LC.upper(), a + a.upper()))


def keyword_dec(t, key):
    a = keyword_alpha(key)
    return t.translate(str.maketrans(a + a.upper(), _LC + _LC.upper()))


def _subst_map(plain, ct):
    """{cipher letter: plain letter} (lowercase) when ct[:len(plain)] is plain under ONE 1:1 letter map (non-letters
    unchanged, case free), else None."""
    m, back = {}, {}
    for p, c in zip(plain, ct):
        pa, ca = p.isascii() and p.isalpha(), c.isascii() and c.isalpha()
        if pa != ca or (not pa and p != c):
            return None
        if pa:
            p, c = p.lower(), c.lower()
            if m.setdefault(c, p) != p or back.setdefault(p, c) != c:
                return None
    return m


_SUBST_POOL = [None]


def _subst_word_fits(cw, m, free, words, prefix=False):
    """Words (from `words`) cipher word `cw` can decode to under the partial map `m`: known letters must agree, unknown
    cipher letters go 1:1 onto `free` plain letters. -> [(word, {cipher: plain} additions)]."""
    out = []
    n = len(cw)
    for w in words:
        if (len(w) < n) if prefix else (len(w) != n):
            continue
        add, ok = {}, True
        for c, x in zip(cw, w):
            y = m.get(c)
            if y is None:
                y = add.get(c)
                if y is None:
                    if x not in free or x in add.values():
                        ok = False
                        break
                    add[c] = y = x
            if y != x:
                ok = False
                break
        if ok:
            out.append((w[:n], add))
    return out


def _subst_tail(m, tail, whole=True):
    """Decode `tail` (the slug part) under cipher->plain map `m`; cipher letters the crib never showed are resolved by
    elimination: each slug word must be a generator / English word (lib.slug) under one global 1:1 completion of the
    map. Ties: generator words first, then keyword-alphabet order (the leftover a-z stays in order). whole=False: the
    last word may be cut. None = no consistent reading."""
    from lib import slug as S
    low = tail.lower()
    if not any(c in _LC and c not in m for c in low):
        return "".join(m.get(c, c) for c in low)
    free = set(_LC) - set(m.values())
    vocab = S.vocab()
    if _SUBST_POOL[0] is None:
        _SUBST_POOL[0] = sorted(vocab) + sorted(w for w in S.english() if w not in vocab and w.isascii() and w.isalpha())
    pool = _SUBST_POOL[0]
    spans = [(x.start(), x.end()) for x in re.finditer(r"[a-z]+", low)]
    cut = not whole and spans and spans[-1][1] == len(low)
    fits = []
    for k, (a, b) in enumerate(spans):
        f = _subst_word_fits(low[a:b], m, free, pool, prefix=cut and k == len(spans) - 1)
        if not f:
            return None
        fits.append(f[:400])
    best, budget = [None, None], [20000]

    def walk(k, mm, sc):
        budget[0] -= 1
        if budget[0] < 0:
            return
        if k == len(fits):
            new = [(c, p) for c, p in mm.items() if c not in m]
            mono = sum((a < b) == (x < y) for (a, x), (b, y) in itertools.combinations(sorted(new), 2))
            key = (sc, mono)
            if best[1] is None or key > best[1]:
                best[0], best[1] = dict(mm), key
            return
        used = set(mm.values())
        for w, add in fits[k]:
            add = {c: p for c, p in add.items() if c not in mm}
            if any(mm.get(c, p) != p for c, p in add.items()) or len(set(add.values())) < len(add) \
                    or used & set(add.values()):
                continue
            mm2 = dict(mm, **add)
            if all(mm2.get(c) == ch for c, ch in zip(low[spans[k][0]:spans[k][1]], w)):
                walk(k + 1, mm2, sc + (w in vocab or (cut and k == len(fits) - 1 and any(v.startswith(w) for v in vocab))))
    walk(0, dict(m), 0)
    if best[0] is None:
        return None
    return "".join(best[0].get(c, c) for c in low)


def subst_solve(blob):
    """(name, sentence, enc) when the blob is the warmups sentence under one simple / keyword substitution (map learned
    from the fixed 87-char prefix, unseen slug letters resolved by elimination + slug words), else None."""
    t = _t(blob).strip()
    if len(t) <= len(_CRIB):
        return None
    m = _subst_map(_CRIB, t)
    if not m or all(k == v for k, v in m.items()):
        return None
    tail = _subst_tail(m, t[len(_CRIB):])
    if not tail or not SLUG.fullmatch(tail):
        return None
    plain = _CRIB + tail
    enc_map = {p: c for c, p in m.items()}
    enc_map.update({p: c for p, c in zip(tail, t[len(_CRIB):].lower()) if p in _LC})
    up = not any(c.islower() for c in t)

    def enc(x):
        y = "".join((enc_map.get(c.lower(), c.lower()).upper() if c.isupper() else enc_map.get(c, c)) for c in x)
        return y.upper() if up else y
    return "subst", plain, enc


def subst_fragment(p, k=3):
    """Mastery free-text fragment under a simple / keyword substitution: fit the fixed sentence at every offset as the
    crib (>= 10 letters, one consistent non-identity 1:1 map) -> decoded fragments, longest-crib fits first."""
    out = []
    for off in range(len(_CRIB)):
        crib = _CRIB[off:]
        n = min(len(crib), len(p))
        if sum(c.isalpha() for c in p[:n]) < 10:
            break
        m = _subst_map(crib[:n], p)
        if not m or all(a == b for a, b in m.items()):
            continue
        got = crib[:n]
        if len(p) > n:
            tail = _subst_tail(m, p[n:], whole=False)
            if tail is None:
                continue
            got += tail
        if not any(c.islower() for c in p):
            got = got.upper()
        if got not in out:
            out.append(got)
        if len(out) >= k:
            break
    return out


_B58 ="123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


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


# base45 (RFC 9285, EU DCC / CyberChef "To Base45" / chepy to_base45): each byte pair -> 3 chars (n = c + d*45 + e*2025,
# little-endian digits), a trailing odd byte -> 2 chars. Alphabet 0-9A-Z plus " $%*+-./:" -- space is a DIGIT, so the
# line is not stripped beyond its newline. Strict: a char outside the alphabet, length % 3 == 1 or a triple > 65535
# (a chunk > 255 for a pair) rejects the line.
_B45 = string.digits + string.ascii_uppercase + " $%*+-./:"
_UNB45 = {c: i for i, c in enumerate(_B45)}


def b45_enc(s):
    b, out = _u(s), []
    for i in range(0, len(b) - 1, 2):
        n = b[i] << 8 | b[i + 1]
        out += [_B45[n % 45], _B45[n // 45 % 45], _B45[n // 2025]]
    if len(b) % 2:
        out += [_B45[b[-1] % 45], _B45[b[-1] // 45]]
    return "".join(out)


def b45_dec(t):
    t = t.strip("\r\n")
    if not t or len(t) % 3 == 1 or len(t) > 8192:
        raise ValueError("not base45")
    v = [_UNB45[c] for c in t]
    out = bytearray()
    for i in range(0, len(v), 3):
        ch = v[i:i + 3]
        n = sum(d * 45 ** k for k, d in enumerate(ch))
        if n > (0xFFFF if len(ch) == 3 else 0xFF):
            raise ValueError("base45 chunk out of range")
        out += n.to_bytes(len(ch) - 1, "big")
    return _t(bytes(out))


def b45_free(p):
    """Speculative free-line base45: only an all-alphabet line that decodes to printable text."""
    got = safe(b45_dec, p)
    return [got] if got and got.strip() and any(c.isalpha() for c in got) else []


# Z85 (ZeroMQ RFC 32): big-endian 4-byte frames -> 5 base-85 digits over its own alphabet. Strict ZeroMQ (pyzmq,
# `basenc --z85`) needs len%4 == 0; CyberChef "To Base85"/Z85 truncates a partial last frame ascii85-style ("z85"),
# others NUL-pad it to a full frame ("z85-pad": the decoder drops <= 3 trailing NULs). Overflowing frames reject.
_Z85 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#"
_UNZ85 = {c: i for i, c in enumerate(_Z85)}


def z85_enc(s, pad=False):
    b = _u(s)
    n = -len(b) % 4
    b += b"\0" * n
    out = []
    for i in range(0, len(b), 4):
        v = int.from_bytes(b[i:i + 4], "big")
        out += [_Z85[v // 85 ** k % 85] for k in (4, 3, 2, 1, 0)]
    return "".join(out if pad or not n else out[:-n])


def z85_dec(t):
    t = re.sub(r"[\r\n]+", "", t.strip())
    if not t or len(t) % 5 == 1 or len(t) > 16384:
        raise ValueError("not z85")
    n = -len(t) % 5
    out = bytearray()
    for i in range(0, len(t) + n, 5):
        v = 0
        for c in (t[i:i + 5] + "#" * n)[:5]:
            v = v * 85 + _UNZ85[c]
        if v > 0xFFFFFFFF:
            raise ValueError("z85 frame out of range")
        out += v.to_bytes(4, "big")
    if n:
        del out[-n:]
    else:
        k = len(out) - len(out.rstrip(b"\0"))
        if k > 3:
            raise ValueError("z85 NUL run")
        del out[len(out) - k:]
    return _t(bytes(out))


def z85_free(p):
    """Speculative free-line Z85: only an all-alphabet line that decodes to printable text."""
    got = safe(z85_dec, p)
    return [got] if got and got.strip() and any(c.isalpha() for c in got) else []


# base100 /"base💯" (AdamNiederer/base100, pybase100): each UTF-8 byte b -> one emoji U+1F3F7 + b (U+1F3F7..U+1F4F6;
# on the wire F0 9F (b+55)//64+143 (b+55)%64+128). Strict: after stripping surrounding whitespace every char must be
# in the 256-emoji block (any other char, incl. ZWJ / VS16 / a space between emoji, rejects the line).
_B100 = 0x1F3F7


def b100_enc(s):
    return "".join(chr(_B100 + b) for b in _u(s))


def b100_dec(t):
    t = t.strip()
    if not t or len(t) > 16384 or not all(_B100 <= ord(c) < _B100 + 256 for c in t):
        raise ValueError("not base100")
    return _t(bytes(ord(c) - _B100 for c in t))


def b100_free(p):
    """Speculative free-line base100: only an all-block line of >= 2 emoji that decodes to printable text."""
    got = safe(b100_dec, p) if len(p.strip()) >= 2 else None
    return [p[:len(p) - len(p.lstrip())] + got] if got and got.strip() else []


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


# Upside-down ("flip") text: each char -> its 180°-rotated look-alike, usually read back to front. Two encoder tables
# (upsidedown 0.4 on PyPI = fileformat.info map, reverses; chepy to_upside_down, lossy B->q R->ɹ, no reverse by
# default); the decoder takes the union of both plus common web alternates.
_UD_TABLE = dict(zip("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"&',.;?^_()[]{}<>",
                     "ɐqɔpǝɟƃɥᴉɾʞꞁɯuodbɹsʇnʌʍxʎzⱯᗺƆᗡƎᖵ⅁HIᒋ⋊ꞀWNOԀꝹᴚS⊥∩ɅMX⅄Z0ІᘔƐᔭ59Ɫ86¡„⅋,'˙؛¿ᵥ‾)(][}{><"))
_UD_CHEPY = dict(zip("abcdefghijklmnpqrtuvwyABCEFGKLMPRTUVWY1234579!&',?/()[]<>",
                     "ɐqɔpǝɟƃɥᴉɾʞlɯudbɹʇnʌʍʎ∀qƆƎſפʞ˥WԀɹ┴∩ΛM⅄ƖᄅƐㄣϛㄥ6¡⅋,'¿\\)(][><"))
# flipped look-alike -> original; ASCII images swap pairwise (b/q d/p n/u M/W 6/9 ,/' brackets), lowercase wins on
# chepy's lossy images (q, ɹ, ʞ)
_UNUD = {"ı": "i", "ן": "l", "ʅ": "l", "Ⅎ": "F", "߃": "F", "∀": "A", "ᗄ": "A", "ꓭ": "B", "𐐒": "B", "Ↄ": "C", "Ͻ": "C",
         "ᗜ": "D", "ꓷ": "D", "ꓨ": "G", "ſ": "F", "ꓘ": "K", "ᒣ": "L", "⅂": "L", "ꓶ": "L", "Ό": "Q", "ꓤ": "R", "ꓕ": "T",
         "ꓵ": "U", "Ⴖ": "U", "Λ": "V", "ꓥ": "V", "Ϻ": "W", "ʁ": "R", "⇂": "1", "↊": "2", "↋": "3", "߈": "4", "ㄐ": "4",
         "¸": ","}
for _tbl in (_UD_CHEPY, _UD_TABLE):
    for _k, _v in _tbl.items():
        _UNUD[_v] = _k
_UNUD.update({"ɹ": "r", "ʞ": "k", "q": "b", "W": "M", "M": "W", "/": "/", "\\": "\\"})
_UD_MARKS = {c for c in _UNUD if not c.isascii()}
_UD_ASCII_LOW = set("bdlnopqsuxz")   # the only ASCII lowercase letters a flipped English line can show


def upside_enc(s, table=_UD_TABLE, rev=True):
    out = "".join(table.get(c, c) for c in s)
    return out[::-1] if rev else out


def upside_dec(t, rev=True):
    """Upside-down text -> plain (rev: read it back to front too). None unless >= 3 flip-only non-ASCII marks making
    >= 20% of the non-space chars, every non-ASCII char is a known flip image and no ASCII lowercase letter outside
    the flip-image set (b d l n o p q s u x z) shows -- plain English, CJK, Braille or ROT8000 stay None."""
    if not isinstance(t, str):
        return None
    t = t.strip()
    if not t or len(t) > 50000:
        return None
    body = [c for c in t if not c.isspace()]
    marks = sum(c in _UD_MARKS for c in body)
    if marks < 3 or marks < 0.2 * len(body):
        return None
    for c in body:
        if c.isascii() and c.islower() and c not in _UD_ASCII_LOW:
            return None
        if not c.isascii() and c not in _UD_MARKS:
            return None
    out = "".join(_UNUD.get(c, c) for c in t)
    return out[::-1] if rev else out


def upside_free(p):
    """Mastery free line: both readings (flipped back to front / in place), better English first."""
    lead = p[:len(p) - len(p.lstrip())]
    return _top(p, [lead + b for b in (upside_dec(p), upside_dec(p, rev=False)) if b], 2)


# "Fancy text" letter styles: Fullwidth Forms (U+FF01-FF5E = ASCII + 0xFEE0, space -> U+3000 as ICU
# Halfwidth-Fullwidth), Mathematical Alphanumeric Symbols (13 Latin A-Za-z runs + 5 digit runs; reserved slots live
# in Letterlike Symbols U+21xx), small capitals (no small-capital X exists: x stays ASCII), circled / squared letters.
_MATH_LATIN = {"bold": 0x1D400, "italic": 0x1D434, "bold-italic": 0x1D468, "script": 0x1D49C, "bold-script": 0x1D4D0,
               "fraktur": 0x1D504, "double-struck": 0x1D538, "bold-fraktur": 0x1D56C, "sans": 0x1D5A0,
               "sans-bold": 0x1D5D4, "sans-italic": 0x1D608, "sans-bold-italic": 0x1D63C, "monospace": 0x1D670}
_MATH_DIGITS = {"bold": 0x1D7CE, "double-struck": 0x1D7D8, "sans": 0x1D7E2, "sans-bold": 0x1D7EC, "monospace": 0x1D7F6}
_MATH_HOLES = {"italic": dict(h="ℎ"), "script": dict(B="ℬ", E="ℰ", F="ℱ", H="ℋ", I="ℐ", L="ℒ", M="ℳ", R="ℛ", e="ℯ",
                                                       g="ℊ", o="ℴ"),
               "fraktur": dict(C="ℭ", H="ℌ", I="ℑ", R="ℜ", Z="ℨ"),
               "double-struck": dict(C="ℂ", H="ℍ", N="ℕ", P="ℙ", Q="ℚ", R="ℝ", Z="ℤ")}
_SMALLCAPS = dict(zip("abcdefghijklmnopqrstuvwyz", "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘꞯʀꜱᴛᴜᴠᴡʏᴢ"))
_SMALLCAPS_WEB = _SMALLCAPS | {"f": "ғ", "q": "ǫ", "s": "s"}   # lingojam-style generators: Cyrillic ghe-stroke f
_DING_DIGITS = "⓿❶❷❸❹❺❻❼❽❾"   # black-bubble digits: NEGATIVE CIRCLED DIGIT ZERO + DINGBAT NEGATIVE CIRCLED DIGIT 1-9


def _style_table(style):
    """ASCII char -> its look-alike in one style (chars the style lacks are absent: they pass through)."""
    if style == "fullwidth":
        return {chr(c): chr(c + 0xFEE0) for c in range(0x21, 0x7F)} | {" ": "\u3000"}
    if style == "smallcaps":
        return dict(_SMALLCAPS)
    if style == "smallcaps-web":
        return dict(_SMALLCAPS_WEB)
    if style == "parenthesized":   # (a) U+249C, (A) U+1F110, (1)-(9) U+2474; no parenthesized zero
        return ({chr(65 + i): chr(0x1F110 + i) for i in range(26)} | {chr(97 + i): chr(0x249C + i) for i in range(26)}
                | {str(i): chr(0x2473 + i) for i in range(1, 10)})
    if style == "regional":        # REGIONAL INDICATOR SYMBOL LETTER A-Z (capitals only; pairs render as flags)
        return {chr(65 + i): chr(0x1F1E6 + i) for i in range(26)}
    if style == "bubble-black":    # NEGATIVE CIRCLED LATIN CAPITAL LETTER + dingbat negative circled digits
        return {chr(65 + i): chr(0x1F150 + i) for i in range(26)} | dict(zip(string.digits, _DING_DIGITS))
    if style == "circled":
        return ({chr(65 + i): chr(0x24B6 + i) for i in range(26)} | {chr(97 + i): chr(0x24D0 + i) for i in range(26)}
                | {str(i): chr(0x245F + i) for i in range(1, 10)} | {"0": "⓪"})
    if style in ("squared", "negative-circled", "negative-squared"):
        base = {"squared": 0x1F130, "negative-circled": 0x1F150, "negative-squared": 0x1F170}[style]
        return {chr(65 + i): chr(base + i) for i in range(26)}
    base = _MATH_LATIN[style]
    out = {c: chr(base + i) for i, c in enumerate(string.ascii_uppercase + string.ascii_lowercase)}
    out.update(_MATH_HOLES.get(style, {}))
    if style in _MATH_DIGITS:
        out.update({str(i): chr(_MATH_DIGITS[style] + i) for i in range(10)})
    return out


_STYLES = ("fullwidth", *_MATH_LATIN, "smallcaps", "smallcaps-web", "circled", "squared", "negative-circled",
           "negative-squared", "parenthesized", "regional", "bubble-black")
_UNSTYLE = {}
for _st in _STYLES:
    for _k, _v in _style_table(_st).items():
        if _k != _v:
            _UNSTYLE.setdefault(_v, _k.lower() if _st.startswith("smallcaps") else _k)
_UNSTYLE.update({"ǫ": "q", "\u3000": " ", "ᴩ": "p", "ᑫ": "q"})   # web generators: ǫ/ᴩ small Q/P, tiny-text ᑫ
# every other compatibility look-alike NFKC folds to one ASCII letter/digit (superscripts ᵃ, subscripts ₐ, ⅰ, ℹ, ...),
# to a parenthesized one ((a) -> a) or to a 2-digit number (circled 10-20); ᶦ -> ɪ chains through small capitals
for _lo, _hi in ((0xAA, 0xBA), (0x2B0, 0x2E4), (0x1D2C, 0x1DBF), (0x2070, 0x209C), (0x2100, 0x218F),
                 (0x2460, 0x24FF), (0x2C7C, 0x2C7D), (0xFF01, 0xFF5E), (0x1D400, 0x1D7FF), (0x1F100, 0x1F1FF)):
    for _cp in range(_lo, _hi + 1):
        _n = unicodedata.normalize("NFKC", chr(_cp))
        _m = re.fullmatch(r"\(?([A-Za-z0-9]|[12][0-9])\)?", _n)
        if _m and _n != chr(_cp) and (_n[0] == "(") == (_n[-1] == ")"):
            _UNSTYLE.setdefault(chr(_cp), _m[1])
        elif _n in _UNSTYLE and _n != chr(_cp):
            _UNSTYLE.setdefault(chr(_cp), _UNSTYLE[_n])
for _base in (0x2776, 0x2780, 0x278A):   # dingbat (negative) circled (sans-serif) digits 1-10
    _UNSTYLE.update({chr(_base + d): str(d + 1) for d in range(10)})
_UNSTYLE.update({chr(0x24EB + d): str(d + 11) for d in range(10)} | {chr(0x24F5 + d): str(d + 1) for d in range(10)}
                | {"🄋": "0", "🄌": "0", "⓿": "0", "ғ": "f"})
_UNSTYLE_SKIP = "\ufe0e\ufe0f\u200b\u200c\u200d"   # emoji/text presentation selectors, zero-width joiners


def unistyle_enc(s, style="fullwidth", upper=False, space=None):
    """Plain -> one letter style (upper: fold to capitals first; smallcaps upper=True styles capitals too).
    space: replacement for " " (fullwidth default U+3000; pass " " to keep ASCII spaces)."""
    tbl = _style_table(style)
    if space is not None:
        tbl[" "] = space
    if style.startswith("smallcaps"):
        s = s.lower() if upper else s
    elif upper:
        s = s.upper()
    return "".join(tbl.get(c, c) for c in s)


def unistyle_dec(t):
    """Styled Unicode letters (any mix of the styles above) -> ASCII; small capitals read back lowercase. None unless
    >= 2 styled chars making >= 50% of the non-space chars and every other char is ASCII -- CJK prose with fullwidth
    punctuation, IPA, math Greek, upside-down or plain text stay None."""
    if not isinstance(t, str):
        return None
    t = t.strip()
    if not t or len(t) > 50000:
        return None
    body = [c for c in t if not c.isspace() and c not in _UNSTYLE_SKIP]
    marks = sum(c in _UNSTYLE for c in body)
    if marks < 2 or marks < 0.5 * len(body):
        return None
    if any(not c.isascii() and c not in _UNSTYLE for c in body):
        return None
    return "".join(_UNSTYLE.get(c, c) for c in t if c not in _UNSTYLE_SKIP)


# Zero-width steganography: invisible format characters carry the text between (or instead of) visible cover text,
# which is ignored. Writers: plain bits (2 symbols, 8-bit groups); Aysan's fingerprint (1=U+200B 0=U+200C, U+200D
# between chars, every symbol joined by U+FEFF); Steganographr (unpadded bits 0=U+200B 1=U+200C, U+2060 between chars,
# U+FEFF-wrapped); npm/pip zwsp-steg (fixed width: base 5 x 7 over U+200B-200F, base 3 x 11 over U+200B-200D); npm
# zero-width-lib (code point in unpadded base 5 over U+200E U+200F U+200C U+200D U+FEFF, U+200B between chars, after the
# cover's first char); 330k (base 4 x 8 over U+200C U+200D U+202C U+FEFF). The decoder is keyless over symbol roles:
# wrapper / joiner stripped, then every separator choice x digit order (<= 5 digits: all) x width, ranked by English.
_ZW = ("​‌‍‎‏‪‫‬‭‮⁠⁡⁢⁣⁤⁦⁧⁨"
       "⁩᠎﻿")
_ZWSET = frozenset(_ZW)
_ZWSP_STEG = "​‌‍‎‏"   # zwsp-steg MODE_FULL digit order (MODE_ZWSP: the first 3)
_ZWLIB = "‎‏‌‍﻿"       # zero-width-lib quinary digit order (U+200B separates chars)
_ZW_KNOWN = (_ZWSP_STEG, _ZWLIB, "‌‍‬﻿")


def zw_bits_enc(s, zero="​", one="‌", width=8, sep="", join="", wrap="", cover=""):
    """UTF-8 bytes as bits (width 0 = unpadded) on two zero-width symbols; `sep` between bytes, `join` between every
    symbol (separators too), `wrap` around the payload, which goes after the first char of `cover`."""
    tr = str.maketrans("01", zero + one)
    body = sep.join((format(b, f"0{width}b") if width else format(b, "b")).translate(tr) for b in _u(s))
    body = wrap + (join.join(body) if join else body) + wrap
    return cover[:1] + body + cover[1:]


def zw_base_enc(s, alpha, width=0, sep="", cover=""):
    """Each code point in base len(alpha) on zero-width digit symbols: zero-padded to `width` (zwsp-steg) or unpadded
    with `sep` between chars (zero-width-lib); the payload goes after the first char of `cover`."""
    k, out = len(alpha), []
    for c in s:
        n, d = ord(c), []
        while True:
            n, r = divmod(n, k)
            d.append(alpha[r])
            if not n:
                break
        out.append(alpha[0] * (width - len(d)) + "".join(reversed(d)))
    body = sep.join(out)
    return cover[:1] + body + cover[1:]


def _zw_bodies(seq):
    """The symbol run as is, minus a wrapper symbol seen only at its ends (Steganographr U+FEFF, a stray BOM), and minus
    a joiner symbol on every odd position (Aysan U+FEFF)."""
    out = [seq]
    for s in set(seq):
        core = seq.strip(s)
        if core and s not in core:
            out.append(core)
    for b in list(out):
        if len(b) >= 3 and len(b) % 2 and len(set(b[1::2])) == 1 and b[1] not in b[0::2]:
            out.append(b[0::2])
    return [b for b in dict.fromkeys(out) if len(b) >= 8]


def _zw_orders(digits):
    """Digit-value maps for a set of symbols: every order up to 5 symbols, else the known writers' orders + sorted."""
    if len(digits) < 2:
        return []
    if len(digits) <= 5:
        perms = itertools.permutations(digits)
    else:
        ds = set(digits)
        perms = [p for p in (tuple(x for x in a if x in ds) for a in _ZW_KNOWN) if set(p) == ds]
        perms += [tuple(digits), tuple(digits)[::-1]]
    return [{c: i for i, c in enumerate(p)} for p in perms]


def _zw_read(groups, val, k):
    """Text of the digit groups (UTF-8 when every value is a byte), or None at the first impossible value."""
    ns = []
    for g in groups:
        n = 0
        for c in g:
            n = n * k + val[c]
        if n > 0x10FFFF or (n < 32 and n not in (9, 10, 13)) or n == 127:
            return None
        ns.append(n)
    if max(ns) < 256:
        try:
            return bytes(ns).decode("utf-8")
        except UnicodeDecodeError:
            pass
    return "".join(map(chr, ns))


def _zw_scan(body, found):
    syms = sorted(set(body))
    k = len(syms)
    if k > 7:
        return
    for val in _zw_orders(syms):   # fixed-width groups, no separator
        w0 = next(w for w in range(1, 9) if k ** w >= 128)
        for w in range(w0, min(len(body), 21) + 1):
            if len(body) % w == 0:
                txt = _zw_read([body[i:i + w] for i in range(0, len(body), w)], val, k)
                if txt:
                    found.setdefault(txt, 0 if (k, w) == (2, 8) else 1)
    for sep in syms:               # one symbol between chars, the others are digits (padded or not)
        toks = body.strip(sep).split(sep)
        if len(toks) < 2 or not all(toks):
            continue
        digits = [c for c in syms if c != sep]
        for val in _zw_orders(digits):
            txt = _zw_read(toks, val, len(digits))
            if txt:
                found.setdefault(txt, 1)


_ZW_MEMO = {}


def zw_cands(t, k=3):
    """Keyless readings of the zero-width payload hidden in t, most English first; [] when t holds < 8 zero-width
    symbols (emoji ZWJ sequences / Persian ZWNJ use one symbol and never read). Never raises."""
    try:
        if not isinstance(t, str) or len(t) > 200000:
            return []
        seq = "".join(c for c in t if c in _ZWSET)
        if len(seq) < 8:
            return []
        if seq not in _ZW_MEMO:
            from lib.decode import _bigram
            found = {}
            for body in _zw_bodies(seq):
                _zw_scan(body, found)
            good = [x for x in found if all(c.isprintable() or c in "\t\r\n" for c in x)]
            if len(_ZW_MEMO) > 256:
                _ZW_MEMO.clear()
            _ZW_MEMO[seq] = sorted(good, key=lambda x: (x.isascii(), _bigram(x), -found[x]), reverse=True)
        return _ZW_MEMO[seq][:k]
    except Exception:  # noqa: BLE001 - malformed input reads as nothing
        return []


def zw_dec(t):
    """The best zero-width reading of t, or None."""
    got = zw_cands(t, 1)
    return got[0] if got else None


def zw_fit(plain, blob):
    """(name, enc) re-encoding `plain` to exactly the zero-width blob, its symbol roles (bit values, separator, joiner,
    wrapper / base-k digit order) learned from it; a cover text is kept when the payload sits after its first char."""
    blob = blob.strip()
    want = "".join(c for c in blob if c in _ZWSET)
    cover = "".join(c for c in blob if c not in _ZWSET)
    if len(want) < 8 or not plain or blob not in (want, cover[:1] + want + cover[1:]):
        return None
    syms = sorted(set(want))
    if len(syms) > 6:
        return None
    for zero, one in itertools.permutations(syms, 2):
        rest = [c for c in syms if c not in (zero, one)]
        for sep, join, wrap in itertools.product([""] + rest, repeat=3):
            if len({x for x in (sep, join, wrap) if x}) != len([x for x in (sep, join, wrap) if x]):
                continue
            for width in (8, 7, 0):
                kw = dict(zero=zero, one=one, width=width, sep=sep, join=join, wrap=wrap)
                if zw_bits_enc(plain, **kw) == want:
                    kw["cover"] = cover
                    return f"zw-bits{width or ''}-fit", lambda s, kw=kw: zw_bits_enc(s, **kw)
    for sep in [""] + syms:
        digits = [c for c in syms if c != sep]
        for val in _zw_orders(digits):
            alpha = "".join(sorted(val, key=val.get))
            width = 0 if sep else len(want) // len(plain)
            if zw_base_enc(plain, alpha, width, sep) == want:
                return (f"zw-base{len(alpha)}-fit",
                        lambda s, a=alpha, w=width, sp=sep: zw_base_enc(s, a, w, sp, cover))
    return None


def col_order(key):
    """Column read order for a columnar key: a word (stable alphabetical rank, ties left to right -- pycipher ColTrans /
    secretpy ColumnarTransposition), an int n (identity order = scytale with n columns) or an explicit index tuple."""
    if isinstance(key, int):
        return list(range(key))
    if isinstance(key, str):
        k = key.lower()
        return sorted(range(len(k)), key=lambda i: (k[i], i))
    return list(key)


def col_enc(s, key, pad=None):
    """Columnar transposition: write row-wise under len(key) columns, read whole columns in key order. Every character
    is kept (spaces, punctuation); pad fills the last row (online tools' 'X')."""
    order = col_order(key)
    m = len(order)
    if pad and len(s) % m:
        s += pad * (m - len(s) % m)
    return "".join(s[c::m] for c in order)


def col_dec(t, key, pad=None):
    """Inverse of col_enc (ragged last row: the leftmost len % m columns are one longer). pad strips its fill."""
    order = col_order(key)
    m, n = len(order), len(t)
    if not m:
        return t
    rows, extra = divmod(n, m)
    out, pos = [""] * n, 0
    for c in order:
        ln = rows + (c < extra)
        out[c::m] = t[pos:pos + ln]
        pos += ln
    s = "".join(out)
    if pad and n % m == 0:
        k = len(s) - len(s.rstrip(pad))
        s = s[:n - k] if k < m else s
    return s


def col_letters_enc(s, key):
    """pycipher ColTrans form: non-letters dropped, upper-cased, then columnar."""
    return col_enc(re.sub(r"[^A-Z]", "", s.upper()), key)


_COL_PERM_MAX = 5   # every column order up to 5 columns (152 orders); 6-8 columns: identity + reversed + hint words


def col_keys(hints=()):
    """[(tier, order)] keys for keyless solving, most plausible first: hint words <= 8 letters (tier 0), identity =
    scytale 2-8 (1), reversed 6-8 and every other permutation of 2-5 columns (2)."""
    keys = {}
    for h in hints or ():
        for w in re.findall(r"[A-Za-z]{2,}", str(h)):
            if len(w) <= 8:
                keys.setdefault(tuple(col_order(w)), 0)
    for m in range(2, 9):
        keys.setdefault(tuple(range(m)), 1)
        keys.setdefault(tuple(range(m))[::-1], 2)
    for m in range(2, _COL_PERM_MAX + 1):
        for p in itertools.permutations(range(m)):
            keys.setdefault(p, 2)
    return [(tier, k) for k, tier in keys.items()]


def col_solve(t, hints=()):
    """Best columnar / scytale reading of t (either direction: column-read and its inverse row-read), or None when no
    order reads clearly more English than t itself (decoys: prose, base64, hex, other ciphers). A wrong order of the
    same width often yields a near-tie ROTATION of the answer ('ce work ... iN'), so among readings within 0.3 of the
    best bigram score the most plausible key wins (hint word, then scytale, column-read before row-read). Never
    raises."""
    try:
        from lib.decode import _bigram
        if not isinstance(t, str):
            t = _t(t)
        t = t.strip("\r\n")   # spaces are ciphertext: a column may start or end with one
        if len(t) < 6 or not re.search(r"[A-Za-z]{2}", t) or "\n" in t:
            return None
        seen, scored = {t}, []
        for tier, k in col_keys(hints):
            if len(k) >= len(t):
                continue
            for d, cand in enumerate((col_dec(t, k), col_enc(t, k))):
                if cand not in seen:
                    seen.add(cand)
                    scored.append((_bigram(cand), 2 * tier + d, cand))
        if not scored:
            return None
        top = max(sc for sc, _r, _c in scored)
        if top < -6.3 or top < _bigram(t) + 0.6:
            return None
        return min((r, -sc, c) for sc, r, c in scored if sc >= top - (1.0 if r < 2 else 0.3))[2]
    except Exception:  # noqa: BLE001
        return None


def wordrev(s):
    return " ".join(w[::-1] for w in s.split(" "))


def wordorder(s):
    return " ".join(reversed(s.split(" ")))


# Pig Latin: leading consonant cluster -> end + "ay", a vowel-initial word + `vowel`. Two reference implementations:
#   bsd   -- bsdgames `pig`: ASCII letter runs, y stops the cluster (even first), "qu" moves as one unit, case kept by
#            position (Nice -> Icenay), an ALL-CAPS word gets WAY/AY; everything else passes through
#   ws    -- PyPI piglatin 1.0.6 translate(): whitespace words minus \W pre/post, case-sensitive "aeiou", y a vowel
#            after the first letter, raw letters moved and a hyphen before the suffix (Nice -> ice-Nay, exact -> exact-ay)
_PIG_VARIANTS = {
    "piglatin": dict(vowel="way"),
    "piglatin-yay": dict(vowel="yay", y=False, qu=False),
    "piglatin-ay": dict(vowel="ay", y=False, qu=False),
    "piglatin-hay": dict(vowel="hay", y=False, qu=False),
    "piglatin-raw": dict(vowel="way", case="move"),
    "piglatin-raw-yay": dict(vowel="yay", case="move", y=False, qu=False),
    "piglatin-raw-ay": dict(vowel="ay", case="move", y=False, qu=False),
    "piglatin-lower": dict(vowel="way", case="lower"),
    "piglatin-lower-yay": dict(vowel="yay", case="lower", y=False, qu=False),
    "piglatin-hyphen": dict(vowel="ay", sep="-", case="move", y=False, qu=False, ci=False),
    "piglatin-hyphen-way": dict(vowel="way", sep="-", case="move", y=False, qu=False, ci=False),
    "piglatin-hyphen-yay": dict(vowel="yay", sep="-", case="move", y=False, qu=False, ci=False),
}
_PIG_WS = re.compile(r"^(?P<pre>[\W]*)(?P<word>.+?)(?P<post>[\W]*)$")


def _pig_word(w, vowel="way", sep="", case="keep", qu=True, y=True, ci=True):
    """One word to Pig Latin. y=True: y stops the cluster even as the first letter (bsd), else only after it."""
    if case == "lower":
        w = w.lower()
    vs = "aeiouAEIOU" if ci else "aeiou"
    ys = "yY" if ci else "y"
    allup = case == "keep" and w.isupper()
    if w[0] in vs:
        return w + sep + (vowel.upper() if allup else vowel)
    i = 0
    while i < len(w) and not (w[i] in vs or (w[i] in ys and (i or y))):
        i += 2 if qu and w[i] in "qQ" and w[i + 1:i + 2] in ("u", "U") else 1
    if i >= len(w):
        i = 0                                            # no vowel at all: the word stays, + "ay"
    rest, clus = w[i:], w[:i]
    if case == "keep" and not allup and w[0].isupper() and clus:
        clus, rest = clus[0].lower() + clus[1:], rest[0].upper() + rest[1:]
    return rest + sep + clus + ("AY" if allup else "ay")


def _pig_sub(s, fn, sep):
    """Apply fn to every word: ASCII letter runs (sep ''), or the piglatin package's whitespace words minus \\W edges."""
    if not sep:
        return re.sub(r"[A-Za-z]+", lambda m: fn(m.group()), s)
    out = []
    for tok in re.findall(r"\S+|\s+", s):
        m = _PIG_WS.match(tok) if tok.strip() and re.search(r"[A-Za-z]", tok) else None
        out.append(m.group("pre") + fn(m.group("word")) + m.group("post") if m else tok)
    return "".join(out)


def pig_enc(s, **kw):
    return _pig_sub(s, lambda w: _pig_word(w, **kw), kw.get("sep", ""))


_pig_known = None


def _pig_score(w):
    """Word plausibility: GM sentence / slug-generator words in it, then English ones, no inner capital (nIce), bigrams."""
    global _pig_known
    if _pig_known is None:
        _pig_known = (set(_SENT_WORDS), {"a", "i"})
        try:
            from lib import slug as _slug
            _pig_known = (_pig_known[0] | _slug.vocab(), _pig_known[1] | _slug.english())
        except Exception:  # noqa: BLE001 - no reference lists: bigrams alone
            pass
    from lib.decode import _bigram
    runs = re.findall(r"[a-z]+", w.lower())   # stone/tones, squid/quids: a GM word outranks any English one
    return (sum(x in _pig_known[0] for x in runs), sum(x in _pig_known[1] for x in runs),
            not re.search(r"[a-z][A-Z]|^[A-Z].*[A-Z][a-z]", w), _bigram(w), -len(w))


def _pig_unword(w, kw):
    """The most plausible original of one Pig Latin word under variant kw (it must re-encode to exactly w), else None."""
    vowel, sep = kw.get("vowel", "way"), kw.get("sep", "")
    low = w.lower()
    if not low.endswith("ay"):
        return None
    cands = []
    if low.endswith(sep + vowel) and len(w) > len(sep + vowel):
        cands.append(w[:-len(sep + vowel)])
    body = w[:-2]
    if sep:
        if sep in body:
            rest, clus = body.rsplit(sep, 1)
            cands.append(clus + rest)
    else:
        for k in range(0, min(len(body), 6) + 1):
            cands.append(body[len(body) - k:] + body[:len(body) - k])
    seen = []
    for c in cands:
        if not c:
            continue
        for v in (c, c[0].upper() + c[1:].lower() if c[0].islower() and any(x.isupper() for x in c[1:]) else c,
                  c.lower(), c.upper(), c.capitalize()):
            if v not in seen and _pig_word(v, **kw) == w:
                seen.append(v)
    return max(seen, key=_pig_score) if seen else None


def pig_dec(t, **kw):
    """Undo Pig Latin variant kw. None unless EVERY word re-encodes exactly (plain prose / base64 / hex -> None)."""
    if not isinstance(t, str) or not re.search(r"[A-Za-z]", t) or len(t) > 20000:
        return None
    bad = []

    def one(w):
        got = _pig_unword(w, kw)
        if got is None:
            bad.append(w)
        return got or w
    out = _pig_sub(t, one, kw.get("sep", ""))
    return None if bad else out


def pig_free(p):
    """Speculative free-line candidates: every Pig Latin variant that decodes the whole fragment, best English first."""
    if not re.search(r"[aA][yY]\W*(?:\s|$)", p):
        return []
    return _top(p, [pig_dec(p, **kw) for kw in _PIG_VARIANTS.values()])


_LEET = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"}
_UNLEET = {"4": "a", "3": "e", "0": "o", "5": "s", "7": "t"}
_SENT_WORDS = set(re.findall(r"[a-z]+", SENTENCE.lower())) - {"slug"}


def leet_enc(s, il=False):
    """CyberChef "To Leet Speak": a e i o s t -> 4 3 1 0 5 7 (il=True also l -> 1); digits are left as they are."""
    m = dict(_LEET, l="1") if il else _LEET
    return "".join(m.get(c.lower(), c) for c in s)


def _unleet_word(w):
    w = "".join(_UNLEET.get(c, c) for c in w)
    n = w.count("1")
    if not n:
        return w
    if n > 4:
        return w.replace("1", "i")
    from lib.decode import _bigram
    parts = w.split("1")
    outs = ["".join(p + c for p, c in zip(parts, ch + ("",))) for ch in itertools.product("il", repeat=n)]
    # 1 = i or l: a word of the GM sentence, else the more English reading (no 'lll' / 'ii' runs), ties -> i
    return max(outs, key=lambda o: (o.lower() in _SENT_WORDS, _bigram(o) - len(re.findall(r"(.)\1\1|ii", o)),
                                    o.count("i")))


def leet_dec(t):
    """Undo 1337 substitution (4 3 1 0 5 7 -> a e i/l o s t, 1 picked per word by bigram score). A slug's trailing
    -NN number is kept. None unless the text reads as leet: >= 1 letter+digit word, no 2/6/8/9 inside one (hex,
    base64), and more leet digits than surviving a/e/i/o/s/t letters."""
    if not isinstance(t, str) or not t.strip() or len(t) > 50000:
        return None
    toks = list(re.finditer(r"[A-Za-z0-9]+", t))
    keep = {m.start() for m in toks if m.group().isdigit() and m.start() and t[m.start() - 1] == "-"
            and not t[m.end():m.end() + 1].isalnum() and t[m.end():m.end() + 1] != "-"}
    mixed = [m.group() for m in toks if re.search(r"[A-Za-z]", m.group()) and re.search(r"\d", m.group())]
    if not mixed or any(re.search(r"[2689]", w) for w in mixed):
        return None
    digits = sum(len(re.findall(r"[013457]", m.group())) for m in toks if m.start() not in keep)
    if digits <= len(re.findall(r"[aeiostAEIOST]", t)):
        return None
    out, last = [], 0
    for m in toks:
        out += [t[last:m.start()], m.group() if m.start() in keep else _unleet_word(m.group())]
        last = m.end()
    return "".join(out) + t[last:]


_KEYPAD = ("2abc", "3def", "4ghi", "5jkl", "6mno", "7pqrs", "8tuv", "9wxyz")
_KEY_OF = {c: k[0] for k in _KEYPAD for c in k[1:]}
_KEY_LET = {k[0]: k[1:] for k in _KEYPAD}
_T9_WORDS = {}


def multitap_enc(s, sep=" ", word=" 0 "):
    """Phone multi-tap: each letter = its key pressed N times (h=44 e=33 l=555), a digit one press past its letters
    (2222 -> 2, 00 -> 0); other chars pass through as tokens."""
    def tap(c):
        if c in _KEY_OF:
            return _KEY_OF[c] * (_KEY_LET[_KEY_OF[c]].index(c) + 1)
        return c * (len(_KEY_LET[c]) + 1) if c in _KEY_LET else "00" if c == "0" else c
    return word.join(sep.join(tap(c) for c in w.lower()) for w in s.split())


def multitap_dec(t):
    """Undo multi-tap (lowercase out). Word gaps: a lone 0, / or |, else 2+ spaces. A run one longer than the key's
    letters is the key's digit (2222 -> 2); punctuation and digit tokens with 0/1 or mixed keys stay literal. None
    unless >= 3 letter runs make up >= 60% of the tokens and no ASCII letter appears."""
    if not isinstance(t, str) or not t.strip() or len(t) > 50000 or re.search(r"[A-Za-z]", t):
        return None
    t = t.strip()
    words = (re.split(r"\s*(?:(?<!\S)0(?!\S)|[/|])\s*", t) if re.search(r"(?<!\S)0(?!\S)|[/|]", t)
             else re.split(r"\s{2,}", t))
    out, runs, toks = [], 0, 0
    for w in words:
        cur = []
        for tok in w.split():
            toks += 1
            m = re.fullmatch(r"([^\d\s]*)(([2-9])\3*)([^\d\s]*)", tok)
            if not m:
                cur.append("0" if tok == "00" else tok)
                continue
            n, let = len(m.group(2)), _KEY_LET[m.group(3)]
            if n > len(let) + 1:
                return None
            cur.append(m.group(1) + (let[n - 1] if n <= len(let) else m.group(3)) + m.group(4))
            runs += 1
        if cur:
            out.append("".join(cur))
    return " ".join(out) if runs >= 3 and runs >= 0.6 * toks else None


def t9_enc(s, space=" "):
    """T9 / one-press-per-letter keypad digits (hello -> 43556); spaces -> `space`, other chars pass through."""
    return "".join(_KEY_OF.get(c, space if c == " " else c) for c in s.lower())


def _t9_index():
    if not _T9_WORDS:
        from lib import slug
        from lib.decode import _bigram
        idx = {}
        for w in slug.english():
            idx.setdefault("".join(_KEY_OF.get(c, "?") for c in w), []).append(w)
        idx = {k: v[0] if len(v) == 1 else max(sorted(v), key=_bigram) for k, v in idx.items()}
        for w in SENTENCE.lower().split() + sorted(slug.vocab()):   # template + GM slug words win a tie
            w = re.sub(r"[^a-z]", "", w)
            if w:
                idx["".join(_KEY_OF[c] for c in w)] = w
        _T9_WORDS.update(idx)
    return _T9_WORDS


def t9_dec(t):
    """Undo T9 digits with the shipped English list (+ slug vocab and the warmups sentence words on ties). Word gaps
    are whitespace, or 0 when there is none; a slug's trailing -NN and groups holding 0/1 stay literal. None unless
    >= 3 multi-digit groups averaging >= 2.5 digits (not Polybius pairs), >= 80% of them resolve to words, <= 15% hold
    0/1 (decimal/octal codes), and they aren't all single-key runs (multi-tap)."""
    if not isinstance(t, str) or not t.strip() or len(t) > 50000 or re.search(r"[A-Za-z]", t):
        return None
    t = t.strip()
    if not re.search(r"\s", t):
        t = re.sub(r"0", " ", t)
    idx = _t9_index()
    keep = {m.start(1) for m in re.finditer(r"(?:[2-9]+-)+(\d{2,})(?![\d-])", t)}
    out, groups, hits, lits = [], 0, 0, 0
    for m in re.finditer(r"\d+|\D+", t):
        g = m.group()
        if not g.isdigit() or m.start() in keep:
            out.append(g)
            continue
        if re.search(r"[01]", g):
            lits += 1
            out.append(g)
            continue
        groups += 1
        w = idx.get(g)
        hits += bool(w)
        out.append(w or g)
    multi = [g for g in re.findall(r"[2-9]+", t) if len(g) > 1]
    if len(multi) < 3 or hits < 0.8 * groups or lits > 0.15 * (groups + lits) \
            or sum(map(len, multi)) < 2.5 * len(multi) or all(len(set(g)) == 1 for g in multi):
        return None
    return "".join(out)


# Unicode code-point notation (sibling of D9 \uXXXX): U+XXXX (CyberChef "Escape Unicode Characters" U+, run together
# or spaced), JS escape() %uXXXX (UTF-16, astral = surrogate pair), Python \U0000XXXX, ES6 \u{XX}, and CSS escapes
# (cssesc escapeEverything: \HEX with an optional one-space terminator, punctuation as \c). Whole fragment only.
_UCP_TOK = re.compile(r"[Uu]\+([0-9A-Fa-f]{4,6})|%[uU]([0-9A-Fa-f]{4})|\\U([0-9A-Fa-f]{8})|\\u\{([0-9A-Fa-f]{1,6})\}"
                      r"|\\u([0-9A-Fa-f]{4})")
_UCP_FULL = re.compile(r"(?:(?:" + _UCP_TOK.pattern + r")|[\s,;])+")
_CSS_TOK = re.compile(r"\\([0-9A-Fa-f]{1,6})(?:\r\n|[ \t\n\r\f])?|\\([^0-9A-Fa-f\r\n\f])")
_CSS_FULL = re.compile(r"(?:" + _CSS_TOK.pattern + r")+")


def _ucp_str(vals):
    """Code points (UTF-16 surrogate halves paired) -> printable text, else None."""
    if any(v > 0x10FFFF for v in vals):
        return None
    try:
        s = "".join(map(chr, vals)).encode("utf-16-le", "surrogatepass").decode("utf-16-le")
    except UnicodeError:
        return None
    return s if s and all(c.isprintable() or c in "\t\n" for c in s) else None


def ucp_enc(s, fmt="U+{:04X}", sep="", utf16=False):
    if utf16:
        b = s.encode("utf-16-be", "surrogatepass")
        return sep.join(fmt.format(int.from_bytes(b[i:i + 2], "big")) for i in range(0, len(b), 2))
    return sep.join(fmt.format(ord(c)) for c in s)


def css_enc(s, spaced=False):
    """cssesc(s, {escapeEverything: true}): \\c for printable ASCII punctuation/space, \\HEX for the rest (every next
    output char is a backslash, so no terminator space). spaced=True: browser CSS.escape's lowercase '\\4e \\69 ' form."""
    if spaced:
        return "".join(f"\\{ord(c):x} " for c in s)
    return "".join("\\" + c if 0x20 <= ord(c) <= 0x7E and re.match(r"[ -,./:-@\[-^`{-~]", c) else f"\\{ord(c):X}"
                   for c in s)


def ucp_dec(t):
    """Unicode code-point notation -> text, None unless the WHOLE fragment (one pair of quotes allowed) is code-point
    tokens + separators. Whitespace between tokens is a separator when it sits between every pair or a token encodes
    whitespace; otherwise it is the literal word space. CSS escapes must read back ASCII (octal '\\150' never does)."""
    if not isinstance(t, str):
        return None
    t = t.strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        t = t[1:-1]
    if not t or len(t) > 200000:
        return None
    if _UCP_FULL.fullmatch(t):
        toks = list(_UCP_TOK.finditer(t))
        if not toks:
            return None
        vals = [int(next(g for g in m.groups() if g), 16) for m in toks]
        gaps = [t[a.end():b.start()] for a, b in zip(toks, toks[1:])]
        keep = not any(chr(v).isspace() for v in vals) and any(gaps) and not all(gaps)
        out = []
        for i, v in enumerate(vals):
            out.append(v)
            if keep and i < len(gaps) and re.search(r"\s", gaps[i]):
                out.append(32)
        return _ucp_str(out)
    if _CSS_FULL.fullmatch(t):
        toks = list(_CSS_TOK.finditer(t))
        if sum(bool(m.group(1)) for m in toks) < 2:
            return None
        s = _ucp_str([int(m.group(1), 16) if m.group(1) else ord(m.group(2)) for m in toks])
        return s if s and s.isascii() else None
    return None


def ucp_free(p):
    d = ucp_dec(p)
    return [p[:len(p) - len(p.lstrip())] + d] if d else []


def _xor(s, k):
    return bytes(b ^ k for b in _u(s))


def _poly_cands(k):
    """Exact keyed polyalphabetic (name, enc, dec) entries for one key word: Beaufort c = k - p, variant c = p - k,
    autokey (pycipher: primer then plaintext), key advancing on every character."""
    out = []
    for mode, auto, every in (("beaufort", False, False), ("variant", False, False), ("vigenere", True, False),
                              ("beaufort", True, False), ("variant", True, False), ("vigenere", False, True),
                              ("beaufort", False, True)):
        name = f"{'autokey-' if auto else ''}{mode}:{k}{'-every' if every else ''}"
        out.append((name, (lambda m, a, e: lambda s: poly(s, k, m, a, e))(mode, auto, every),
                    (lambda m, a, e: lambda t: poly(t, k, m, a, e, decode=True))(mode, auto, every)))
    return out


# Playfair, keyed by a title/prompt word: 5x5 keyword square (J -> I), X inserted between a doubled pair, X pad on an odd
# tail (secretpy / practicalcryptography rule); "pyc" = pycipher's quirk (2nd of a doubled pair REPLACED by X, no
# insert). Layouts: one letter stream (lower / UPPER, bare, pairs or 5-groups) or each letter run alone (non-letters
# and digits kept in place, so the slug survives). The decoder reads any layout and strips the fillers.
_PF_PUN = ("playfair", "wheatstone", "monarchy", "lyon", "keyword", "huntress")


def pf_square(key):
    sq = ""
    for c in re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(key)).lower()).replace("j", "i") + _POLY:
        if c not in sq:
            sq += c
    return sq


def _pf_pairs(letters, pyc=False):
    """Digraphs of a lowercase letter string (j already i): X between a doubled pair (pyc: 2nd replaced), X pad."""
    out, i = [], 0
    while i < len(letters):
        a = letters[i]
        b = letters[i + 1] if i + 1 < len(letters) else "x"
        if a == b:
            if pyc:
                out.append(a + "x")
                i += 2
            else:
                out.append(a + ("q" if a == "x" else "x"))
                i += 1
            continue
        out.append(a + b)
        i += 2
    return out


def _pf_crypt(pair, sq, d):
    (ra, ca), (rb, cb) = divmod(sq.index(pair[0]), 5), divmod(sq.index(pair[1]), 5)
    if ra == rb:
        return sq[ra * 5 + (ca + d) % 5] + sq[rb * 5 + (cb + d) % 5]
    if ca == cb:
        return sq[(ra + d) % 5 * 5 + ca] + sq[(rb + d) % 5 * 5 + cb]
    return sq[ra * 5 + cb] + sq[rb * 5 + ca]


def _pf_letters(s):
    return re.sub(r"[^a-z]", "", s.lower()).replace("j", "i")


def playfair_enc(s, key, layout="stream", upper=False, pyc=False):
    sq = pf_square(key)
    f = (lambda x: x.upper()) if upper else (lambda x: x)
    if layout == "words":
        return re.sub(r"[A-Za-z]+", lambda m: f("".join(_pf_crypt(p, sq, 1) for p in _pf_pairs(_pf_letters(m[0]), pyc))),
                      s)
    ct = [_pf_crypt(p, sq, 1) for p in _pf_pairs(_pf_letters(s), pyc)]
    if layout == "pairs":
        return f(" ".join(ct))
    ct = "".join(ct)
    return f(" ".join(ct[i:i + 5] for i in range(0, len(ct), 5)) if layout == "groups5" else ct)


def _pf_strip(p):
    """Drop the X fillers of a deciphered digraph run: X (or Q after X) between equal letters at an odd index, odd pad."""
    out = []
    for i, c in enumerate(p):
        if i % 2 and 0 < i < len(p) - 1 and p[i - 1] == p[i + 1] and c == ("q" if p[i - 1] == "x" else "x"):
            continue
        out.append(c)
    if len(out) > 1 and out[-1] == ("q" if out[-2] == "x" else "x"):
        out.pop()   # the odd-length pad (a real final X is indistinguishable: Playfair is lossy there)
    return "".join(out)


def _pf_run(letters, sq):
    """Deciphered + filler-stripped lowercase run, or None when it can't be Playfair ciphertext (odd, J, aa digraph)."""
    if len(letters) % 2 or "j" in letters:
        return None
    pairs = [letters[i:i + 2] for i in range(0, len(letters), 2)]
    if any(a == b for a, b in pairs):
        return None
    return _pf_strip("".join(_pf_crypt(p, sq, -1) for p in pairs))


def playfair_dec(t, key):
    """Lowercase plaintext of a Playfair blob under `key`, any layout: per-word when every letter run is even and the
    blob keeps punctuation/digits, else one stream (spacing ignored). None when it can't be Playfair ciphertext."""
    t = _t(t).strip()
    if not t or not t.isascii():
        return None
    sq = pf_square(key)
    runs = re.findall(r"[A-Za-z]+", t)
    if runs and re.search(r"[^A-Za-z\s]", t) and all(len(r) % 2 == 0 for r in runs):
        outs = [_pf_run(r.lower(), sq) for r in runs]
        if all(o is not None for o in outs):
            it = iter(outs)
            return re.sub(r"[A-Za-z]+", lambda _m: next(it), t)
    if re.search(r"[^A-Za-z\s]", t):
        return None
    return _pf_run(re.sub(r"\s+", "", t).lower(), sq)


def _pf_cands(k, dec=True):
    """(name, enc, dec) for every Playfair layout under key k; the decoder (layout-agnostic) rides the first only."""
    out = []
    for layout, upper, pyc in (("stream", True, False), ("stream", False, False), ("stream", True, True),
                               ("groups5", True, False), ("pairs", True, False), ("words", False, False),
                               ("words", True, False)):
        name = f"playfair{'-pyc' if pyc else ''}-{layout}{'-upper' if upper else ''}:{k}"
        out.append((name, (lambda layout, upper, pyc: lambda s: playfair_enc(s, k, layout, upper, pyc))(layout, upper, pyc),
                    (lambda t: playfair_dec(t, k)) if dec and not out else None))
    return out


def playfair_solve(blob, hints=()):
    """(name, sentence, enc) when the blob is the warmups sentence under Playfair keyed by a title/prompt word (or a
    pun key) in a layout that keeps the slug (per-word: hyphens + digits stay); the sentence re-encodes to the exact
    blob. None otherwise (a letter stream loses the slug's digits: infer() then matches it by encoder)."""
    t = _t(blob).strip()
    crib = _pf_letters(_CRIB)
    for k in list(_hint_keys(hints)) + list(_PF_PUN):
        got = playfair_dec(t, k)
        if not got or not _pf_letters(got).startswith(crib):
            continue
        tail = got.split(":")[-1].strip().lower() if ":" in got else ""
        if not SLUG.fullmatch(tail):
            continue
        sent = _CRIB + tail
        for name, enc, _d in _pf_cands(k, dec=False):
            if safe(enc, sent) == t:
                return name, sent, enc
    return None


_PUN_KEYS = ("key", "lemon", "vigenere", "beaufort", "autokey", "bellaso", "blaise", "cipher", "secret", "huntress")


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
        # keyword substitution, keyboard order (any other key: _hint_cands keyword:<word>, crib map: subst_solve)
        ("keyword:qwerty", lambda s: keyword_enc(s, "qwertyuiopasdfghjklzxcvbnm"),
         lambda t: keyword_dec(t, "qwertyuiopasdfghjklzxcvbnm")),
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
        ("base45", b45_enc, b45_dec),
        ("z85", z85_enc, z85_dec),
        ("z85-pad", lambda s: z85_enc(s, pad=True), z85_dec),
        ("base100", b100_enc, b100_dec),
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
        ("rot8000", rot8000, rot8000_dec),
        ("rot18", rotnum, rotnum_dec),
        ("rot5", lambda s: rotnum(s, 0), lambda t: rotnum_dec(t, 0)),
        ("swapcase", lambda s: s.swapcase(), lambda t: t.swapcase()),
        ("upper", lambda s: s.upper(), None),
        ("wordrev", wordrev, wordrev),
        ("wordorder", wordorder, wordorder),
        ("qwerty-right", lambda s: qwerty_shift(s, 1), lambda t: qwerty_shift(t, -1)),
        ("qwerty-left", lambda s: qwerty_shift(s, -1), lambda t: qwerty_shift(t, 1)),
        *[(f"kbd:{a}>{b}", (lambda a, b: lambda s: kbd_swap(s, a, b))(a, b),
           (lambda a, b: lambda t: kbd_dec(t, a, b))(a, b)) for a, b in _KBD_PAIRS],
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
        ("upsidedown", upside_enc, upside_dec),
        ("upsidedown-noreverse", lambda s: upside_enc(s, rev=False), lambda t: upside_dec(t, rev=False)),
        ("upsidedown-chepy", lambda s: upside_enc(s, _UD_CHEPY, rev=False), lambda t: upside_dec(t, rev=False)),
        ("upsidedown-chepy-rev", lambda s: upside_enc(s, _UD_CHEPY), upside_dec),
        ("leet", leet_enc, leet_dec),
        ("leet-il", lambda s: leet_enc(s, il=True), leet_dec),
        ("multitap", multitap_enc, multitap_dec),
        ("multitap-slash", lambda s: multitap_enc(s, word=" / "), multitap_dec),
        ("multitap-2space", lambda s: multitap_enc(s, word="  "), multitap_dec),
        ("t9", t9_enc, t9_dec),
        ("t9-0", lambda s: t9_enc(s, space="0"), t9_dec),
        ("fullwidth", unistyle_enc, unistyle_dec),
        ("fullwidth-space", lambda s: unistyle_enc(s, space=" "), unistyle_dec),
        ("smallcaps", lambda s: unistyle_enc(s, "smallcaps"), unistyle_dec),
        ("smallcaps-all", lambda s: unistyle_enc(s, "smallcaps", upper=True), unistyle_dec),
        ("circled", lambda s: unistyle_enc(s, "circled"), unistyle_dec),
        ("smallcaps-web", lambda s: unistyle_enc(s, "smallcaps-web"), unistyle_dec),
        ("parenthesized", lambda s: unistyle_enc(s, "parenthesized"), unistyle_dec),
        ("regional", lambda s: unistyle_enc(s, "regional", upper=True), unistyle_dec),
        ("regional-zwsp", lambda s: "\u200b".join(unistyle_enc(s, "regional", upper=True)), unistyle_dec),
        ("bubble-black", lambda s: unistyle_enc(s, "bubble-black", upper=True), unistyle_dec),
        ("zw-bits8", zw_bits_enc, zw_dec),
        ("zw-bits8-inv", lambda s: zw_bits_enc(s, "‌", "​"), zw_dec),
        ("zw-fingerprint", lambda s: zw_bits_enc(s, "‌", "​", sep="‍", join="﻿"), zw_dec),
        ("zw-steganographr", lambda s: zw_bits_enc(s, width=0, sep="⁠", wrap="﻿"), zw_dec),
        ("zwsp-steg", lambda s: zw_base_enc(s, _ZWSP_STEG, 7), zw_dec),
        ("zwsp-steg-zwsp", lambda s: zw_base_enc(s, _ZWSP_STEG[:3], 11), zw_dec),
        ("zero-width-lib", lambda s: zw_base_enc(s, _ZWLIB, sep="​"), zw_dec),
        ("ucp-U+", ucp_enc, ucp_dec),
        ("ucp-U+-spaced", lambda s: ucp_enc(s, sep=" "), ucp_dec),
        ("ucp-u+-lower", lambda s: ucp_enc(s, "U+{:04x}"), ucp_dec),
        ("ucp-%u", lambda s: ucp_enc(s, "%u{:04X}", utf16=True), ucp_dec),
        ("ucp-%u-lower", lambda s: ucp_enc(s, "%u{:04x}", utf16=True), ucp_dec),
        ("ucp-\\U8", lambda s: ucp_enc(s, "\\U{:08x}"), ucp_dec),
        ("ucp-\\U8-upper", lambda s: ucp_enc(s, "\\U{:08X}"), ucp_dec),
        ("ucp-\\u{}", lambda s: ucp_enc(s, "\\u{{{:x}}}"), ucp_dec),
        ("css-escape", css_enc, ucp_dec),
        ("css-escape-spaced", lambda s: css_enc(s, spaced=True), ucp_dec),
        ("css-escape6", lambda s: ucp_enc(s, "\\{:06x}"), ucp_dec),
    ]
    out += [(name, (lambda kw: lambda s: pig_enc(s, **kw))(kw), (lambda kw: lambda t: pig_dec(t, **kw))(kw))
            for name, kw in _PIG_VARIANTS.items()]
    out += [(f"math-{st}", (lambda st: lambda s: unistyle_enc(s, st))(st), unistyle_dec) for st in _MATH_LATIN]
    out += [(st, (lambda st: lambda s: unistyle_enc(s, st, upper=True))(st), unistyle_dec)
            for st in ("squared", "negative-circled", "negative-squared")]
    out += [(f"bacon{a}-{tr}{('-keep', '-keep-cc')[cc] if k else ''}",
             (lambda a, tr, k, cc: lambda s: bacon_enc(s, a, tr, k, cc))(a, tr, k, cc),
             (lambda a, tr, k: lambda t: bacon_dec(t, a, tr, k))(a, tr, k))
            for a in (26, 24) for tr in _BACON_TR for k in (False, True) for cc in (False, True)
            if not (cc and (not k or tr[0] in "01"))]
    # columnar / scytale transposition, keyless: identity order = scytale with n columns (col-read and row-read)
    out += [(f"scytale{n}", (lambda n: lambda s: col_enc(s, n))(n), (lambda n: lambda t: col_dec(t, n))(n))
            for n in range(2, 9)]
    out += [(f"scytale-rows{n}", (lambda n: lambda s: col_dec(s, n))(n), (lambda n: lambda t: col_enc(t, n))(n))
            for n in range(2, 9)]
    # keyed polyalphabetic, key = a pun on the codec's name (any other key: the crib -> crib_solve, or _hint_cands)
    for k in _PF_PUN:
        out += _pf_cands(k)
    for k in _PUN_KEYS:
        out.append((f"vigenere:{k}", (lambda k: lambda s: vigenere(s, k))(k), (lambda k: lambda t: vigenere(t, k, -1))(k)))
        out += _poly_cands(k)
    out += [(f"caesar{n}", (lambda n: lambda s: rot(s, n))(n), (lambda n: lambda t: rot(t, -n))(n))
            for n in range(1, 26) if n != 13]
    # CyberChef ROT13 op, "Rotate numbers" on: digits turn by amount % 10 (amount 5 = the rot18 digit step on caesar5)
    out += [(f"rot{n}-num", (lambda n: lambda s: rotnum(s, n, n))(n), (lambda n: lambda t: rotnum_dec(t, n, n))(n))
            for n in range(1, 26) if n % 10]
    out += [(f"rail{n}", (lambda n: lambda s: rail_enc(s, n))(n), (lambda n: lambda t: rail_dec(t, n))(n))
            for n in range(2, 7)]
    # rail fence 7-20 rails, and 2-20 rails at every offset (CyberChef Rail Fence Cipher "Offset")
    out += [(f"rail{n}" + (f"-off{o}" if o else ""), (lambda n, o: lambda s: rail_enc(s, n, o))(n, o),
             (lambda n, o: lambda t: rail_dec(t, n, o))(n, o)) for n, o in rail_keys(10 ** 6) if n > 6 or o]
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
    """Vigenère keys from the challenge title / prompt words (and the words run together, and every letter of the hint
    = a running key). Accents folded first: a 'Vigenère' pun title must key 'vigenere', not 'vigen'."""
    keys = []
    for h in hints or ():
        h = unicodedata.normalize("NFKD", str(h)).encode("ascii", "ignore").decode()
        words = re.findall(r"[A-Za-z]{3,}", h)
        for w in words + ["".join(words), "".join(re.findall(r"[A-Za-z]", h))]:
            w = w.lower()
            if w and w not in keys:
                keys.append(w)
    return keys[:40]



def _hint_cands(hints):
    out = []
    for k in _hint_keys(hints):
        out.append((f"vigenere:{k}", (lambda k: lambda s: vigenere(s, k))(k), (lambda k: lambda t: vigenere(t, k, -1))(k)))
        out.append((f"keyword:{k}", (lambda k: lambda s: keyword_enc(s, k))(k),
                    (lambda k: lambda t: keyword_dec(t, k))(k)))
        out += _poly_cands(k)
        out += _pf_cands(k)
        if len(k) <= 8:   # columnar transposition keyed by a title/prompt word
            out.append((f"columnar:{k}", (lambda k: lambda s: col_enc(s, k))(k), (lambda k: lambda t: col_dec(t, k))(k)))
            out.append((f"columnar-x:{k}", (lambda k: lambda s: col_enc(s, k, "x"))(k),
                        (lambda k: lambda t: col_dec(t, k, "x"))(k)))
            out.append((f"columnar-letters:{k}", (lambda k: lambda s: col_letters_enc(s, k))(k), None))
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
    zf = zw_fit(p, want)
    if zf:
        return zf
    for name, enc, dec in cands:
        if dec is not None and safe(dec, want) == p:
            return name, enc
    ab = _fit_affine(p, want)
    if ab:
        a, b = ab
        return f"affine{a},{b}", lambda s: affine(s, a, b)
    cs = crib_solve(want, hints) if p.startswith(_CRIB) else None
    if cs and cs[1] == p:
        return cs[0], cs[2]
    pf = playfair_solve(want, hints) if p.startswith(_CRIB) else None
    if pf and pf[1] == p:
        return pf[0], pf[2]
    ss = subst_solve(want) if p.startswith(_CRIB) else None
    if ss and ss[1] == p:
        return ss[0], ss[2]
    sub = _fit_subst(p, want)
    if sub:
        return "subst", lambda s: "".join(sub.get(c, c) for c in s)
    return None


def plaintext(blob, slug, deadline=None, hints=()):
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
    rs = rail_solve(text)   # strict (crib + slug, anagram-gated): before the loose `slug in` decoders below
    if rs and slug in rs[1]:
        return rs[1]
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
    cs = crib_solve(text, hints)
    if cs and slug in cs[1]:
        return cs[1]
    pf = playfair_solve(text, hints)
    if pf and slug in pf[1]:
        return pf[1]
    ss = subst_solve(text)
    if ss and slug in ss[1]:
        return ss[1]
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
    hints = tuple(hints) + tuple(str(contract.get(k) or "") for k in ("name", "prompt"))
    plain = plaintext(blob, slug, hints=hints)
    if not plain:
        return None
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
    ("rot8000", lambda p: [b for b in (rot8000_dec(p),) if b]),
    ("swapcase", lambda p: [p.swapcase()]),
    ("rot18", rotnum_free),
    ("wordrev", lambda p: [wordrev(p)]),
    ("piglatin", pig_free),
    ("qwerty", lambda p: _top(p, [qwerty_shift(p, 1), qwerty_shift(p, -1)], 2)),
    ("keyboard", kbd_free),
    ("rail", rail_free),
    ("affine", lambda p: _top(p, [affine_inv(p, a, b) for a in _AFFINE_A for b in range(26)])),
    ("columnar", lambda p: [b for b in (col_solve(p),) if b]),
    ("punycode", lambda p: [p[:len(p) - len(p.lstrip())] + puny_dec(p)]),
    ("braille", lambda p: [b for b in (braille_dec(p),) if b]),
    ("base45", b45_free),
    ("z85", z85_free),
    ("base100", b100_free),
    ("upsidedown", upside_free),
    ("leet", lambda p: [b for b in (leet_dec(p),) if b]),
    ("multitap", lambda p: [b for b in (multitap_dec(p),) if b]),
    ("t9", lambda p: [b for b in (t9_dec(p),) if b]),
    ("unistyle", lambda p: [p[:len(p) - len(p.lstrip())] + b for b in (unistyle_dec(p),) if b]),
    ("codepoint", ucp_free),
    ("zerowidth", zw_cands),
    ("polyalpha", crib_fragment),
    ("subst", subst_fragment),
)


def register_speculative():
    """Hand the keyless free-text decoders to lib.decode's joint free-line assignment as day=None (speculative)
    entries: only for a blob that has more lines than any confirmed codec day and a free line the confirmed codecs
    can't cover. Idempotent."""
    from lib import decode
    confirmed = {n for n, d, _f in decode._FREE if d is not None}
    for name, fn in SPECULATIVE_FREE:
        if name not in confirmed:   # rot47 = GM-confirmed D15: keep its day so it isn't demoted to speculative
            decode.register_free(name, None, fn)


if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]:
        print(f, (infer_case(f) or ("unidentified",))[0])
