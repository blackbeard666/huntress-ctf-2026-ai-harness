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
import functools
import html
import itertools
import json
import math
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
    # D17 "Bacon Bits" ("Sixteen guests. Five little a's and b's apiece."): each UTF-8 HEX digit as a 5-symbol Bacon
    # group (a=0, b=1, MSB first), single spaces between groups (byte-exact on the Single + 83/83 Mastery line 17)
    (17, "bacon-hex", lambda s: " ".join(f"{int(c, 16):05b}".replace("0", "a").replace("1", "b") for c in _u(s).hex()),
     lambda t: _t(bytes.fromhex("".join("%x" % int(g.replace("a", "0").replace("b", "1"), 2) for g in t.split()))),
     False),
    # D18 "Off the Rails" ("Three rails. One very zigzag commute."): classic 3-rail fence, offset 0, spaces are ciphertext
    # (byte-exact on the Single, TT 813eb166 and 88/88 Mastery 8adb440d line 18)
    (18, "rail3", lambda s: rail_enc(s, 3), lambda t: rail_dec(t, 3), True),
    # D19 "Little Things" ("Two bytes walk into a bar. The little one goes first."): lowercase hex of BOM fffe + UTF-16LE,
    # no separators (byte-exact on the Single, TT dc4763da and 93/93 Mastery 9ca30408 line 19)
    (19, "utf16le-hex", lambda s: (b"\xff\xfe" + s.encode("utf-16-le")).hex(),
     lambda t: bytes.fromhex(re.sub(r"\s+", "", t)).decode("utf-16"), False),
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


# Plain-text Morse with punctuation (`!` `,` `:` `-` as Morse, ' / ' / '/' / 3-space word gaps), exact per symbol: a
# Mastery fragment cut at a word gap (' / - .... ..' = ' this') misses lib.decode's strict Morse branch and falls to
# lib.ciphers.morse_decode, which drops punctuation (the slug hyphen `-....-`). Case is lost, so morse_free also offers
# the reading re-cased onto the warmups template ("game master:" -> "Game Master:") for the positional/template check.
_MORSE_WGAP = re.compile(r"\s*/\s*|\s{3,}")


def morse_text_dec(t):
    """Morse (dots/dashes only) -> lowercase text keeping a leading/trailing word gap as a space, else None (an
    unknown symbol, other characters, no symbols)."""
    if not isinstance(t, str) or not re.fullmatch(r"[.\-/\s]*[.\-][.\-/\s]*", t) or "\n" in t.strip():
        return None
    words = _MORSE_WGAP.split(t)
    out = []
    for w in words:
        syms = w.split()
        if any(x not in _UNMORSE for x in syms):
            return None
        out.append("".join(_UNMORSE[x] for x in syms))
    return " ".join(out).lower()


_TPL = SENTENCE.split("{slug}")[0]


def _recase(x):
    """Lowercase template text -> the template's own casing (a substring of it, or its tail + the slug), else None."""
    tl = _TPL.lower()
    j = tl.find(x)
    if j >= 0:
        return _TPL[j:j + len(x)]
    for i in range(len(_TPL)):
        if x.startswith(tl[i:]):
            return _TPL[i:] + x[len(_TPL) - i:]
    return None


def morse_free(p):
    """Speculative Mastery-line decoder: plain-text Morse -> [template-cased reading, lowercase reading]."""
    x = morse_text_dec(p)
    if not x:
        return []
    r = _recase(x)
    return [r, x] if r and r != x else [x]


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


# Morse carrying another codec (D16 "Dot Com" = Morse over hex): Morse loses case, so the inner codec is a case-free
# one -- hex digits (GM-confirmed, tried first), decimal / octal char codes, 8-bit binary, base32, A1Z26. Inner
# separators ride as Morse word gaps (' / ', CyberChef '/', 3 spaces) or are dropped (fixed-width codes concatenated).
_MORSE_INNER = {
    "hex": lambda s: _u(s).hex().upper(),
    "decimal": lambda s: " ".join(str(b) for b in _u(s)),
    "octal3": lambda s: " ".join(f"{b:03o}" for b in _u(s)),
    "binary8": lambda s: " ".join(f"{b:08b}" for b in _u(s)),
    "base32": lambda s: base64.b32encode(_u(s)).decode(),
    "base32-nopad": lambda s: base64.b32encode(_u(s)).decode().rstrip("="),
    "a1z26": lambda s: a1z26_enc(s),
}


def morse_over_enc(s, inner, word=" / "):
    """Morse (one space between symbols, `word` between the inner codec's space-separated tokens) of inner(s);
    word="" drops the inner separators (D16 morse-hex shape)."""
    x = _MORSE_INNER[inner](s)
    return word.join(" ".join(_MORSE[c] for c in w) for w in (x.split(" ") if word else [x.replace(" ", "")]))


def _txt(b):
    try:
        s = b.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        return None
    return s if s and all(c.isprintable() or c in "\t\r\n" for c in s) else None


def _dec_concat(d):
    """Unseparated decimal char codes: printable ASCII 32-126 parses uniquely (1xx = 100-126, else 32-99)."""
    out, i = [], 0
    while i < len(d):
        n = 3 if d[i] == "1" else 2
        v = int(d[i:i + n]) if len(d) - i >= n else -1
        if not 32 <= v <= 126:
            return None
        out.append(v)
        i += n
    return bytes(out)


def _morse_inner_reads(x):
    """[(inner, text)] readings of the Morse layer's UPPERCASE text `x` (inner tokens split by single spaces)."""
    flat, toks, out = x.replace(" ", ""), x.split(), []

    def add(name, fn):
        try:
            s = fn()
        except Exception:  # noqa: BLE001 - not this inner codec
            return
        s = _txt(s) if isinstance(s, bytes) else s
        if s:
            out.append((name, s))
    if re.fullmatch(r"(?:[0-9A-F]{2})+", flat) and (len(toks) == 1 or all(len(t) == 2 for t in toks)):
        add("hex", lambda: bytes.fromhex(flat))
    if re.fullmatch(r"[01]+", flat):
        if len(toks) > 1 and len({len(t) for t in toks}) == 1 and len(toks[0]) in (7, 8):
            add("binary8", lambda: bytes(int(t, 2) for t in toks))
        elif len(toks) == 1 and len(flat) % 8 == 0:
            add("binary8", lambda: bytes(int(flat[i:i + 8], 2) for i in range(0, len(flat), 8)))
    if re.fullmatch(r"\d+", flat):
        if len(toks) > 1:
            add("decimal", lambda: bytes(int(t) for t in toks))
            if re.fullmatch(r"[0-7]+", flat):
                add("octal3", lambda: bytes(int(t, 8) for t in toks))
        else:
            if re.fullmatch(r"[0-7]+", flat) and len(flat) % 3 == 0:
                add("octal3", lambda: bytes(int(flat[i:i + 3], 8) for i in range(0, len(flat), 3)))
            add("decimal", lambda: _dec_concat(flat))
    if len(toks) == 1 and re.fullmatch(r"[A-Z2-7]+=*", flat) and len(flat.rstrip("=")) % 8 not in (1, 3, 6):
        add("base32", lambda: base64.b32decode(flat.rstrip("=") + "=" * (-len(flat.rstrip("=")) % 8)))
    nums = [int(n) for n in re.findall(r"\d+", x)]
    if "-" in x and re.fullmatch(r"[\d\- !,.:?']+", x) and sum(1 <= n <= 26 for n in nums) >= 0.8 * len(nums):
        add("a1z26", lambda: a1z26_dec(x))
    return out


def _texty(s):
    return sum(c.isalnum() or c in " .,!?:;'-_\n" for c in s) / max(len(s), 1)


def morse_layer_reads(t):
    """[(inner, text)] for Morse (strict `.-`, else any 2-symbol alphabet) carrying a case-free inner codec, best
    first: hex first (GM-confirmed D16), then by how much the result reads as text. Plain-English Morse -> []."""
    t = t.strip()
    if not t or len(t) > 200000:
        return []
    syms = [x for x in re.split(r"\s*/\s*|\s+", t) if x]
    if syms and all(x in _UNMORSE for x in syms):
        x = morse_dec(t).upper()
    else:
        x = (morse_alt_dec(t) or morse_timing_text(t) or "").upper()
    x = re.sub(r" +", " ", x.strip())
    if not x:
        return []
    reads = [(n, s) for n, s in _morse_inner_reads(x) if _texty(s) >= 0.85]
    if not reads:
        return []
    try:
        from lib.decode import _bigram
    except Exception:  # noqa: BLE001
        def _bigram(_s):
            return 0.0
    return sorted(reads, key=lambda r: (r[0] == "hex", round(_texty(r[1]), 2), _bigram(r[1])), reverse=True)


def morse_layer_dec(t):
    """The text under Morse-over-<case-free codec>, else None."""
    r = morse_layer_reads(t)
    return r[0][1] if r else None


def morse_layer_free(p):
    """Speculative Mastery-line decoder: every inner reading of a Morse line (the slug/template check picks)."""
    return [s for _n, s in morse_layer_reads(p)]



# Morse as on/off timing units (ITU timing / "Morse as binary"): dit = 1 on-unit, dah = 3, in-letter gap = 1 off-unit,
# letter gap = 3, word gap = 7 -- one run of two symbols (`1`/`0`, Wikipedia's `=`/`.`, `#`/space ...). Told from 8-bit
# binary by the run lengths: on-runs only 1/3, off-runs only 1/3/7+ (binary ASCII has 0-runs of 2, 4-6).
_TIMING_ON = "1=#*█■xX"


def morse_timing_enc(s, on="1", off="0", inner=None, cat=False):
    """Morse timing units of s (or of inner(s): inner tokens split by word gaps, run together when cat)."""
    x = _MORSE_INNER[inner](s) if inner else s
    ws = [x.replace(" ", "")] if cat else x.split(" ")
    return (off * 7).join((off * 3).join(off.join(on * (1 if d == "." else 3) for d in _MORSE[c.upper()])
                                         for c in w if c.upper() in _MORSE) for w in ws)


def morse_timing_text(t):
    """Morse timing units -> lowercase text, else None (not exactly two symbols, a run length outside 1/3 on and
    1/3/7+ off, an unknown code)."""
    if not isinstance(t, str) or len(t) > 400000:
        return None
    t = t.strip("\r\n")
    sym = set(t) - set(" \t\r\n")
    if len(sym) == 2:
        t = re.sub(r"\s+", "", t)
    elif len(sym) == 1 and " " in t and "\n" not in t:
        sym |= {" "}
    else:
        return None
    a, b = sorted(sym, key=lambda c: c not in _TIMING_ON)
    for on, off in ((a, b), (b, a)):
        runs = [(m.group()[0] == on, len(m.group())) for m in re.finditer(f"{re.escape(on)}+|{re.escape(off)}+", t)]
        while runs and not runs[0][0]:
            runs.pop(0)
        while runs and not runs[-1][0]:
            runs.pop()
        if sum(r[0] for r in runs) < 6 or any(n not in (1, 3) and (o or n < 7) for o, n in runs):
            continue
        words, cur, code = [], [], ""
        for o, n in runs + [(False, 3)]:
            if o:
                code += "." if n == 1 else "-"
            elif n > 1:
                if code not in _UNMORSE:
                    break
                cur.append(_UNMORSE[code])
                code = ""
                if n >= 7:
                    words.append("".join(cur))
                    cur = []
        else:
            words.append("".join(cur))
            return " ".join(words).lower()
    return None


def morse_timing_free(p):
    """Speculative Mastery-line decoder: plain-text Morse timing units -> [template-cased reading, lowercase]."""
    x = morse_timing_text(p)
    if not x:
        return []
    r = _recase(x)
    return [r, x] if r and r != x else [x]

# Baudot-Murray / ITA2 5-bit telegraph code (sequel to D16 Morse): code = index, written MSB-first (A=00011 E=00001;
# dCode/tape-order writers reverse it: A=11000). LTRS 11111 / FIGS 11011 shift the state; space, LF, CR exist in
# both. Rendered as 5-bit groups (spaced or run together), 5-hole tape (`*`/`.`, `o`/` `, 6-wide with a sprocket
# column) or decimal 0-31. Case-free, so it can also carry hex (FIGS digits + LTRS A-F). US-TTY differs only in
# figures (S=BEL D=$ J=' Z=" H=# V=;). USOS (unshift on space): a receiver drops back to LTRS after every space.
_ITA2_L = ["\x00", "E", "\n", "A", " ", "S", "I", "U", "\r", "D", "R", "J", "N", "F", "C", "K",
           "T", "Z", "L", "W", "H", "Y", "P", "Q", "O", "B", "G", None, "M", "X", "V", None]
_ITA2_F = {"ita2": ["\x00", "3", "\n", "-", " ", "'", "8", "7", "\r", "\x05", "4", "\x07", ",", "!", ":", "(",
                    "5", "+", ")", "2", "£", "6", "0", "1", "9", "?", "&", None, ".", "/", "=", None]}
_ITA2_F["us"] = [{5: "\x07", 9: "$", 11: "'", 17: '"', 20: "#", 30: ";"}.get(i, c) for i, c in enumerate(_ITA2_F["ita2"])]
_BD_LTRS, _BD_FIGS = 31, 27
_BD_PUNCH, _BD_BLANK = set("*oOxX#●■1"), set(".○□0 ")


def baudot_codes(s, table="ita2", init=True, usos=False):
    """Text -> ITA2 code list (uppercased; LTRS first when init, else the line starts in letters unannounced)."""
    figs, state, out = _ITA2_F[table], None if init else "L", []
    for c in s.upper():
        if c in _ITA2_L and c in figs and _ITA2_L.index(c) == figs.index(c):
            out.append(_ITA2_L.index(c))
        elif c in _ITA2_L:
            if state != "L":
                out.append(_BD_LTRS)
                state = "L"
            out.append(_ITA2_L.index(c))
        elif c in figs:
            if state != "F":
                out.append(_BD_FIGS)
                state = "F"
            out.append(figs.index(c))
        else:
            raise ValueError(f"no ITA2 code for {c!r}")
        if usos and c == " ":
            state = "L"
    return out


def baudot_enc(s, fmt="bin", sep=" ", table="ita2", init=True, usos=False, lsb=False, inner=None):
    """ITA2 of s (or of the case-free inner codec's text, e.g. inner="hex"): fmt bin (5-bit groups), tape (`*`/`.`)
    or dec (0-31), `sep` between codes; lsb = tape/dCode bit order (A=11000)."""
    x = _MORSE_INNER[inner](s) if inner else s
    out = []
    for c in baudot_codes(x, table, init, usos):
        b = f"{c:05b}"[::-1] if lsb else f"{c:05b}"
        out.append(str(c) if fmt == "dec" else b.translate(str.maketrans("10", "*.")) if fmt == "tape" else b)
    return sep.join(out)


def _bd_parse(t):
    """[code lists] the blob can be read as (MSB-first and LSB-first), else []."""
    t = t.strip("\r\n\t ")
    if not t or len(t) > 200000:
        return []
    rows = [r.rstrip("\r") for r in t.split("\n")]
    toks = t.split()
    if len(rows) >= 3 and all(r.strip() for r in rows) and max(map(len, rows)) <= 6 \
            and set(t) - set("\r\n") <= _BD_PUNCH | _BD_BLANK | set(".:|"):
        # one tape frame per line, blank may be a space (lines rstripped by editors): pad, drop a sprocket column
        w = max(map(len, rows))
        rows = [r.ljust(w) for r in rows]
        if w == 6:
            sp = [i for i in range(6) if len({r[i] for r in rows}) == 1 and rows[0][i] in ".:|"]
            if not sp:
                return []
            rows = [r[:sp[0]] + r[sp[0] + 1:] for r in rows]
        elif w != 5:
            return []
        bits = ["".join("1" if c in _BD_PUNCH else "0" for c in r) for r in rows]
    elif re.fullmatch(r"\d+(?:[\s,]+\d+)*", t) and not re.fullmatch(r"[01\s]+", t):
        nums = [int(x) for x in re.findall(r"\d+", t)]
        if len(nums) < 4 or max(nums) > 31 or not {_BD_LTRS, _BD_FIGS} & set(nums):
            return []
        return [nums]
    elif len(toks) == 1 and re.fullmatch(r"[01]+", t) and len(t) % 5 == 0:
        bits = [t[i:i + 5] for i in range(0, len(t), 5)]
    elif toks and all(len(x) in (5, 6) for x in toks) and len({len(x) for x in toks}) == 1:
        if len(toks[0]) == 6:   # 6-wide frames: one constant sprocket column
            sp = [i for i in range(6) if len({x[i] for x in toks}) == 1 and toks[0][i] in ".:|"]
            if not sp:
                return []
            toks = [x[:sp[0]] + x[sp[0] + 1:] for x in toks]
        al = set("".join(toks))
        if len(al) > 2:
            return []
        if al <= set("01"):
            bits = toks
        elif al <= _BD_PUNCH | _BD_BLANK:
            bits = ["".join("1" if c in _BD_PUNCH else "0" for c in x) for x in toks]
        else:
            return []
    else:
        return []
    if len(bits) < 4:
        return []
    return [[int(b, 2) for b in bits], [int(b[::-1], 2) for b in bits]]


def _bd_text(codes, table, usos):
    figs, state, out = _ITA2_F[table], "L", []
    for c in codes:
        if c == _BD_LTRS:
            state = "L"
        elif c == _BD_FIGS:
            state = "F"
        else:
            ch = _ITA2_L[c] if state == "L" else figs[c]
            out.append(ch)
            if usos and ch == " ":
                state = "L"
    s = "".join(out).replace("\x00", "").replace("\r\n", "\n").replace("\r", "")
    return s if s.strip() and all(c.isprintable() or c == "\n" for c in s) else None


def baudot_reads(t):
    """[(variant, text)] for an ITA2 blob, best first: a case-free inner codec under it (hex first) when the
    decoded text is just that codec's symbols, else the lowercase English reading. Bacon / binary8 / prose -> []."""
    if not isinstance(t, str):
        return []
    try:
        from lib.decode import _bigram
    except Exception:  # noqa: BLE001
        def _bigram(_s):
            return -4.0
    seen, reads = set(), []
    for codes in _bd_parse(t):
        for table in ("ita2", "us"):
            for usos in (False, True):
                s = _bd_text(codes, table, usos)
                if not s or s in seen:
                    continue
                seen.add(s)
                x = re.sub(r"\s+", " ", s.strip())
                inner = [(f"baudot({n})", v) for n, v in _morse_inner_reads(x) if _texty(v) >= 0.85]
                if inner:
                    reads += [(n, v, 2 + (n == "baudot(hex)"), _bigram(v)) for n, v in inner]
                    continue
                letters = sum(c.isalpha() for c in x)
                if letters >= 0.6 * len(x) and _texty(x) >= 0.9 and _bigram(x) > -6.5:
                    reads.append(("baudot", x.lower(), 1, _bigram(x)))
    reads.sort(key=lambda r: (r[2], r[3]), reverse=True)
    return [(n, v) for n, v, _p, _b in reads]


def baudot_dec(t):
    """The text under an ITA2 blob (plain text lowercase, or in the warmups template's casing when it is that
    sentence; the inner codec's text when it carries one), else None."""
    r = baudot_reads(t)
    return ((r[0][0] == "baudot" and _recase(r[0][1])) or r[0][1]) if r else None


def baudot_free(p):
    """Speculative Mastery-line decoder: every ITA2 reading, plain text also in the template's casing."""
    out = []
    for _n, s in baudot_reads(p):
        r = _recase(s) if _n == "baudot" else None
        for x in (r, s):
            if x and x not in out:
                out.append(x)
    return out


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


# NATO / ICAO words spelling the symbols (D16 "spell the symbols" stack with a word alphabet): words -> chars, then the
# case-free inner layer (hex digits, decimal / octal / binary codes, base32, A1Z26) when the spelled string isn't text.
# Strict: every token of the fragment is an alphabet word (both spellings, Niner/Tree/Fower/Fife, Decimal/Stop) or a
# lone punctuation mark; groups split on '/', '|' or 2+ spaces; CamelCase run-together words are split.
_NATO_WORDS = {w.lower(): chr(97 + i) for i, w in enumerate(_NATO)}
_NATO_WORDS.update({w.lower(): str(i) for i, w in enumerate(_NATO_DIG)})
_NATO_WORDS.update({"alpha": "a", "juliet": "j", "whisky": "w", "x-ray": "x", "x_ray": "x", "niner": "9", "tree": "3",
                    "fower": "4", "fife": "5", "decimal": ".", "stop": ".", "period": ".", "point": ".", "dot": ".",
                    "comma": ",", "dash": "-", "hyphen": "-", "colon": ":", "exclamation": "!", "space": " "})
_NATO_TOK = re.compile(r"x-ray|[a-z]+|[^\sa-z0-9]", re.I)


def nato_layer_enc(s, inner=None, alt=False, sep=" ", word=" / "):
    """NATO words of inner(s) (inner=None: the text itself), `sep` between words, `word` between the inner's
    space-separated tokens. alt=True: Alpha/Juliet spellings and Niner."""
    x = (" ".join(f"{b:02X}" for b in _u(s)) if inner == "hex" else _MORSE_INNER[inner](s)) if inner else s
    names = [("Alpha" if alt and i == 0 else "Juliet" if alt and i == 9 else "X-ray" if alt and i == 23 else w)
             for i, w in enumerate(_NATO)]
    digs = [("Niner" if alt and i == 9 else w) for i, w in enumerate(_NATO_DIG)]

    def sp(c):
        return names[ord(c.lower()) - 97] if c.isascii() and c.isalpha() else digs[int(c)] if c.isdigit() else c
    return word.join(sep.join(sp(c) for c in g) for g in (x.split(" ") if word else [x.replace(" ", "")]))


def _nato_spell(t):
    """The string the NATO words spell (groups joined by one space), or None unless EVERY token is an alphabet word or
    a lone punctuation mark and most tokens are words."""
    t = t.strip()
    if not t or len(t) > 400000:
        return None
    groups, out, nwords, ntok = [g for g in re.split(r"\s*[/|]\s*|\s{2,}|\n", t) if g.strip()], [], 0, 0
    for g in groups:
        if not re.search(r"\s", g.strip()) and re.fullmatch(r"(?:[A-Z][a-z]+|X-[Rr]ay)+", g.strip()):
            g = " ".join(re.findall(r"X-[Rr]ay|[A-Z][a-z]+", g))   # CamelCase run-together
        pos, cs = 0, []
        for m in _NATO_TOK.finditer(g):
            if g[pos:m.start()].strip():
                return None
            pos, tok = m.end(), m.group().lower()
            ntok += 1
            if tok in _NATO_WORDS:
                nwords += 1
                cs.append(_NATO_WORDS[tok])
            elif len(tok) == 1 and not tok.isalnum():
                cs.append(tok)
            else:
                return None
        if g[pos:].strip():
            return None
        out.append("".join(cs))
    if nwords < 3 or nwords < 0.7 * ntok:
        return None
    return re.sub(r" +", " ", " ".join(out)).strip()


def nato_layer_reads(t):
    """[(inner, text)] for a strict NATO fragment, best first: a case-free inner layer (hex first) when the spelled
    string decodes to text, else the spelled text itself when it reads as words ("text")."""
    x = _nato_spell(t)
    if not x:
        return []
    reads = [(n, s) for n, s in _morse_inner_reads(x.upper()) if _texty(s) >= 0.85]
    try:
        from lib.decode import _bigram
    except Exception:  # noqa: BLE001
        def _bigram(_s):
            return 0.0
    reads.sort(key=lambda r: (r[0] == "hex", round(_texty(r[1]), 2), _bigram(r[1])), reverse=True)
    letters = [c for c in x if c.isalpha()]
    if (len(letters) >= 0.5 * len(x.replace(" ", "")) and sum(c in "aeiouy" for c in letters) >= 0.2 * len(letters)
            and not re.fullmatch(r"[0-9a-f ]+", x)):
        reads.append(("text", x))
    return reads


def nato_layer_dec(t, inner=None):
    """The text under NATO words (directly, or over hex / char codes), else None. inner: accept only that reading
    ("text" = the words spell the sentence itself) -- one CANDIDATES entry per shape, so infer()'s decoder pass
    returns the matching encoder."""
    r = [x for x in nato_layer_reads(t) if inner is None or x[0] == inner]
    return r[0][1] if r else None


def nato_layer_free(p):
    """Speculative Mastery-line decoder: every reading of a strict NATO line (the slug/template check picks)."""
    return [s for _n, s in nato_layer_reads(p)]


# Digits / hex spelled as English words ("four e six nine", "zero one zero ...", "seventy-eight, one hundred five"):
# words -> the inner case-free layer (hex / binary / octal / decimal codes). Strict: every token is a digit word
# (zero..nine, niner, oh), a hex letter a-f, a nibble value ten..fifteen, or (numeral reading) an English cardinal word
# (eleven..nineteen, twenty..ninety, hundred, and). Groups split on '/', '|', ',', ';', newlines or 2+ spaces; tokens
# on spaces and hyphens; CamelCase run-together words are split.
_SP_DIG = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
_SP_TEEN = ("ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen")
_SP_TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")
_SP_CHAR = {w: str(i) for i, w in enumerate(_SP_DIG)}
_SP_CHAR.update({"niner": "9", "oh": "0", **{c: c for c in "abcdef"}, **{_SP_TEEN[i]: "abcdef"[i] for i in range(6)}})
_SP_NUM = {**{w: i for i, w in enumerate(_SP_DIG)}, "niner": 9, **{w: 10 + i for i, w in enumerate(_SP_TEEN)},
           **{w: 10 * i for i, w in enumerate(_SP_TENS) if w}, "fourty": 40}


def _sp_num_words(n, conj=False):
    """English cardinal 0-999 ("one hundred five" / conj: "one hundred and five"), tens-units hyphenated."""
    h, r = divmod(n, 100)
    tail = _SP_DIG[r] if r < 10 else _SP_TEEN[r - 10] if r < 20 else \
        _SP_TENS[r // 10] + (f"-{_SP_DIG[r % 10]}" if r % 10 else "")
    if not h:
        return tail
    return f"{_SP_DIG[h]} hundred" + (f"{' and' if conj else ''} {tail}" if r else "")


def spelled_enc(s, inner="hex", sep=" ", word=" / ", title=False, nib=False, num=False, conj=False):
    """English words of inner(s): one word per symbol (`sep` between words, `word` between the inner's tokens; hex is
    spaced per byte; word="" runs the symbols together); nib=True spells hex a-f as ten..fifteen; num=True spells each
    byte as a cardinal number ("seventy-eight", `word` between numbers, conj: "one hundred and five")."""
    if num:
        out = word.join(_sp_num_words(b, conj) for b in _u(s))
    else:
        x = " ".join(f"{b:02x}" for b in _u(s)) if inner == "hex" else _MORSE_INNER[inner](s).lower()

        def sp(c):
            return _SP_DIG[int(c)] if c.isdigit() else _SP_TEEN["abcdef".index(c)] if nib else c
        out = word.join(sep.join(sp(c) for c in g) for g in (x.split(" ") if word else [x.replace(" ", "")]))
    return re.sub(r"[a-z]+", lambda m: m.group().capitalize(), out) if title else out


def _sp_groups(t):
    """[[token, ...] per group] (lowercase), or None unless every token is a spelled-number word."""
    t = t.strip()
    if not t or len(t) > 400000 or re.search(r"[^A-Za-z\s/|,;\-]", t):
        return None
    out = []
    for g in re.split(r"\s*[/|,;]\s*|\s{2,}|\n", t):
        g = g.strip()
        if not g:
            continue
        if not re.search(r"[\s-]", g) and re.fullmatch(r"(?:[A-Z][a-z]*)+", g) and re.search(r"[a-z]", g):
            g = " ".join(re.findall(r"[A-Z][a-z]*", g))   # CamelCase run-together
        toks = [x for x in re.split(r"[\s-]+", g.lower()) if x]
        if not toks or any(x not in _SP_CHAR and x not in _SP_NUM and x not in ("hundred", "and") for x in toks):
            return None
        out.append(toks)
    return out if sum(map(len, out)) >= 4 else None


def _sp_cardinals(toks):
    """Greedy English cardinals 0-999 from a token run -> [int], or None if the run isn't a sequence of numbers."""
    nums, cur, st = [], None, ""   # st: u unit, h N hundred, t tens (unit may follow), d closed
    for x in toks:
        if x in ("and", "hundred"):
            if (x == "and") != (st == "h") or (x == "hundred" and st != "u"):
                return None
            if x == "hundred":
                cur, st = cur * 100, "h"
            continue
        v = _SP_NUM.get(x)
        if v is None:
            return None
        if (st == "h" and v) or (st == "t" and v < 10 and v):
            cur, st = cur + v, "t" if st == "h" and v >= 20 else "d"
            continue
        if cur is not None:
            nums.append(cur)
        cur, st = v, "u" if 1 <= v <= 9 else "t" if v >= 20 else "d"
    if cur is not None:
        nums.append(cur)
    return nums


def spelled_reads(t):
    """[(inner, text)] for a strict spelled-digits fragment, best first: per-symbol words (hex first) over the
    inner case-free layer, and cardinal numbers as char codes ("num")."""
    groups = _sp_groups(t)
    if not groups:
        return []
    reads, flat = [], [x for g in groups for x in g]
    if all(x in _SP_CHAR for x in flat):
        x = " ".join("".join(_SP_CHAR[w] for w in g) for g in groups)
        reads += [(n, s) for n, s in _morse_inner_reads(x.upper()) if _texty(s) >= 0.85]
    if any(_SP_NUM.get(x, 0) >= 10 or x == "hundred" for x in flat):
        nums = []
        for g in groups:
            n = _sp_cardinals(g)
            if n is None:
                nums = None
                break
            nums += n
        if nums and len(nums) >= 2 and all(0 < n < 0x110000 for n in nums):
            s = _txt(bytes(nums)) if max(nums) < 256 else "".join(map(chr, nums))
            if s and _texty(s) >= 0.85:
                reads.append(("num", s))
    try:
        from lib.decode import _bigram
    except Exception:  # noqa: BLE001
        def _bigram(_s):
            return 0.0
    reads.sort(key=lambda r: (r[0] == "hex", round(_texty(r[1]), 2), _bigram(r[1])), reverse=True)
    return reads


def spelled_dec(t, inner=None):
    """The text under spelled digit / number words, else None. inner: accept only that reading (one CANDIDATES entry
    per shape, so infer()'s decoder pass returns the matching encoder)."""
    try:
        r = [x for x in spelled_reads(t) if inner is None or x[0] == inner]
    except Exception:  # noqa: BLE001 - parse defensively
        return None
    return r[0][1] if r else None


def spelled_free(p):
    """Speculative Mastery-line decoder: every reading of a strict spelled-digits line (the slug/template check picks)."""
    try:
        return [s for _n, s in spelled_reads(p)]
    except Exception:  # noqa: BLE001
        return []


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


# Redefence (ACA): the rail fence's zigzag (any offset), but the rails are emitted in a key order instead of top to
# bottom. order[k] = the rail (0 = top) read k-th. Keyless solve: each rail's crib characters pin where its slice can
# start in the ciphertext, so the read order is a short DFS over cumulative slice starts (rails 2-8 x every offset, no
# n! brute). A prompt key ('3-1-2', 'THREE') gives the order directly: _redef_hint_orders.
_REDEF_MAX = 8


def redefence_enc(s, order, offset=0):
    n = len(order)
    rows = _rail_rows(len(s), n, offset)
    rank = {r: k for k, r in enumerate(order)}
    return "".join(s[i] for i in sorted(range(len(s)), key=lambda i: (rank[rows[i]], i)))


def redefence_dec(t, order, offset=0):
    n = len(order)
    if sorted(order) != list(range(n)):
        return None
    rows = _rail_rows(len(t), n, offset)
    rank = {r: k for k, r in enumerate(order)}
    out = [""] * len(t)
    for c, i in zip(t, sorted(range(len(t)), key=lambda i: (rank[rows[i]], i))):
        out[i] = c
    return "".join(out)


def _redef_name(order, o):
    return f"redefence{len(order)}-" + "".join(map(str, order)) + (f"-off{o}" if o else "")


def _redef_orders(t, crib, n, o):
    """Rail read orders (not top-to-bottom) under which t (rails n, offset o) decodes with `crib` as its prefix."""
    L = len(t)
    rows = _rail_rows(L, n, o)
    pos = [[] for _ in range(n)]
    for i, r in enumerate(rows):
        pos[r].append(i)
    starts = []
    for r in range(n):
        ln = len(pos[r])
        need = [(j, crib[i]) for j, i in enumerate(pos[r]) if i < len(crib)]
        starts.append({s for s in range(L - ln + 1) if all(t[s + j] == ch for j, ch in need)})
    out = []

    def dfs(cum, used, acc):
        if len(acc) == n:
            if tuple(acc) != tuple(range(n)):
                out.append(tuple(acc))
            return
        for r in range(n):
            if r not in used and cum in starts[r]:
                used.add(r)
                acc.append(r)
                dfs(cum + len(pos[r]), used, acc)
                acc.pop()
                used.discard(r)
                if len(out) > 8:
                    return
    dfs(0, set(), [])
    return out


def _redef_hint_orders(hints, nmax=_REDEF_MAX):
    """Candidate read orders from the prompt / title: a digit key ('3-1-2', '312', '3,1,2'; 0- or 1-based) or a word
    key (letters ranked alphabetically, ties left to right: 'THREE' -> 4,2,3,0,1). Each key is taken both ways: as the
    rail read sequence and as each rail's read rank."""
    keys = []
    for h in hints or ():
        h = unicodedata.normalize("NFKD", str(h)).encode("ascii", "ignore").decode()
        for m in re.findall(r"\d(?:\s*[-,/ ]\s*\d)+|\b\d{2,8}\b", h):
            d = [int(x) for x in re.findall(r"\d", m)]
            if 2 <= len(d) <= nmax and len(set(d)) == len(d):
                lo = min(d)
                if lo in (0, 1) and sorted(x - lo for x in d) == list(range(len(d))):
                    keys.append(tuple(x - lo for x in d))
        for w in re.findall(r"[A-Za-z]{2,}", h):
            w = w.lower()
            if 2 <= len(w) <= nmax:
                srt = sorted(range(len(w)), key=lambda i: (w[i], i))
                rank = [0] * len(w)
                for k, i in enumerate(srt):
                    rank[i] = k
                keys.append(tuple(rank))
    out = []
    for k in keys:
        inv = [0] * len(k)
        for i, r in enumerate(k):
            inv[r] = i
        for o in (k, tuple(inv)):
            if o not in out and o != tuple(range(len(o))):
                out.append(o)
    return out[:40]


def redefence_solve(blob, hints=()):
    """(name, sentence, enc) when the blob is the warmups sentence under a redefence of 2-8 rails at any offset (rail
    slices emitted in a key order), else None. Anagram gate like rail_solve; hinted orders first, then the crib-pinned
    DFS. Accepts only crib + slug. Never raises."""
    try:
        t = _t(blob).strip("\r\n")
        L = len(t)
        if L <= len(_CRIB) + 4 or L > 400 or "\n" in t:
            return None
        rest = collections.Counter(t)
        rest.subtract(_CRIB)
        if min(rest.values()) < 0 or any(not (ch.islower() or ch.isdigit() or ch == "-") for ch, v in rest.items() if v):
            return None

        def ok(c):   # a mirrored order can equal a plain rail fence (rail3 = redefence3-210-off2): rail_solve's
            return (c and c.startswith(_CRIB) and SLUG.fullmatch(c[len(_CRIB):])
                    and not any(rail_enc(c, m, oo) == t for m, oo in rail_keys(L, _REDEF_MAX)))
        for order in _redef_hint_orders(hints):
            for o in range(2 * len(order) - 2):
                c = redefence_dec(t, order, o)
                if ok(c):
                    return _redef_name(order, o), c, (lambda k, o: lambda s: redefence_enc(s, k, o))(order, o)
        for n in range(2, min(_REDEF_MAX, L - 1) + 1):
            for o in range(2 * n - 2):
                for order in _redef_orders(t, _CRIB, n, o):
                    c = redefence_dec(t, order, o)
                    if ok(c):
                        return _redef_name(order, o), c, (lambda k, o: lambda s: redefence_enc(s, k, o))(order, o)
    except Exception:  # noqa: BLE001
        pass
    return None


def redefence_crib_dec(t):
    r = redefence_solve(t)
    return r[1] if r else None


# Perfect riffle (faro) shuffle, speculative ('deck' / 'shuffle' / 'cards' pun): cut the text in half and interleave,
# repeated k times. Out-shuffle keeps the top card on top (top half first, = rail2 DECODE: one un-shuffle is rail2's
# encoder); in-shuffle deals the second half first. Odd length: the half dealt first is the longer one (ceil). Keyless
# solve walks k = 1 .. order-1 of each shuffle (order <= ~L) undoing one shuffle per step, crib + slug gated.
def riffle_enc(s, k=1, inn=False):
    step = _tp_riffle(len(s), inn)
    for _ in range(k):
        s = "".join(map(s.__getitem__, step))
    return s


def _riffle_undo(t, step):
    out = [""] * len(t)
    for j, i in enumerate(step):
        out[i] = t[j]
    return "".join(out)


def riffle_dec(t, k=1, inn=False):
    step = _tp_riffle(len(t), inn)
    for _ in range(k):
        t = _riffle_undo(t, step)
    return t


def _riffle_walk(t, inn):
    """[(k, reading)] for k = 1 .. order-1: t with k shuffles undone (stops when the cycle closes)."""
    step, out, c = _tp_riffle(len(t), inn), [], t
    for k in range(1, 2 * len(t) + 2):
        c = _riffle_undo(c, step)
        if c == t:
            break
        out.append((k, c))
    return out


def riffle_solve(blob):
    """(name 'riffle-out3' / 'riffle-in1', sentence, enc) when the blob is the warmups sentence under k perfect
    out/in-shuffles (smallest k wins; out before in), else None. Anagram gate like rail_solve. Never raises."""
    try:
        t = _t(blob).strip("\r\n")
        if len(t) <= len(_CRIB) + 4 or len(t) > 2000:
            return None
        rest = collections.Counter(t)
        rest.subtract(_CRIB)
        if min(rest.values()) < 0 or any(not (ch.islower() or ch.isdigit() or ch == "-") for ch, v in rest.items() if v):
            return None
        for inn in (False, True):
            for k, c in _riffle_walk(t, inn):
                if c.startswith(_CRIB) and SLUG.fullmatch(c[len(_CRIB):]):
                    return (f"riffle-{'in' if inn else 'out'}{k}", c,
                            (lambda k, inn: lambda s: riffle_enc(s, k, inn))(k, inn))
    except Exception:  # noqa: BLE001
        pass
    return None


def riffle_crib_dec(t):
    r = riffle_solve(t)
    return r[1] if r else None


def riffle_free(p, k=3):
    """Mastery fragment: a line under k in/out shuffles (k restarting per line) -> readings that are a crib piece
    (_crib_piece), best k by (crib chars confirmed, bigram). Raw and lead-stripped line both tried. Never raises."""
    try:
        from lib.decode import _bigram
        lead = p[:len(p) - len(p.lstrip())]
        hits, seen = {}, set()
        for pre, t in ((lead, p[len(lead):].rstrip("\r\n")), ("", p.rstrip("\r\n")))[:2 if lead else 1]:
            if len(t) < 4 or len(t) > 400:
                continue
            seen.add(t)
            for inn in (False, True):
                for _k, c in _riffle_walk(t, inn):
                    if c in seen:
                        continue
                    seen.add(c)
                    n = _crib_piece(c)
                    if n:
                        hits.setdefault(pre + c, (n, _bigram(c)))
        return [c for c, _s in sorted(hits.items(), key=lambda kv: kv[1], reverse=True)[:k]]
    except Exception:  # noqa: BLE001
        return []


# Bifid / Trifid (Delastelle) over a STANDARD keyless square: Bifid = A-Z sans J (5x5, J->I), Trifid = A-Z + '.'
# (3x3x3, secretpy's default). Each period block writes its row coords, then its col (/ layer) coords, and re-reads them
# as tuples. period 0 = the whole letter run (CyberChef Bifid, secretpy key 0). Layouts: keep = letters ciphered in
# place, case kept, everything else kept (CyberChef; keep-cc = CyberChef's literal lowercase j); upper / lower =
# letter stream only (pycipher / secretpy); groups5 = upper stream in 5-letter groups.
_FRAC = {"bifid": ("ABCDEFGHIKLMNOPQRSTUVWXYZ", 5, 2), "trifid": ("ABCDEFGHIJKLMNOPQRSTUVWXYZ.", 3, 3)}
_FRAC_PERIODS = (0, 5, 6, 7, 8, 9, 10)
_FRAC_LAYOUTS = {"bifid": ("keep", "keep-cc", "upper", "lower", "groups5"), "trifid": ("keep", "upper", "lower")}


def _frac_block(idx, base, n, d):
    if d > 0:
        rows = [[i // base ** (n - 1 - k) % base for i in idx] for k in range(n)]
        flat = [x for r in rows for x in r]
        tup = [flat[j:j + n] for j in range(0, len(flat), n)]
    else:
        flat = [i // base ** (n - 1 - k) % base for i in idx for k in range(n)]
        tup = list(zip(*[flat[k * len(idx):(k + 1) * len(idx)] for k in range(n)]))
    return [sum(x * base ** (n - 1 - k) for k, x in enumerate(t)) for t in tup]


def _frac_run(idx, fam, period, d):
    _ab, base, n = _FRAC[fam]
    p = period or len(idx) or 1
    return [x for i in range(0, len(idx), p) for x in _frac_block(idx[i:i + p], base, n, d)]


def frac_enc(s, fam="bifid", period=0, layout="keep"):
    ab = _FRAC[fam][0]
    s = _u(s).decode() if isinstance(s, bytes) else s
    if layout.startswith("keep"):
        cc = layout == "keep-cc"
        if fam == "bifid":
            s = s.replace("J", "I", 1) if cc else s.replace("J", "I").replace("j", "i")
        pos = [k for k, c in enumerate(s) if c.upper() in ab and not (cc and c == "j")]
        out = _frac_run([ab.index(s[k].upper()) for k in pos], fam, period, 1)
        r = list(s)
        for k, i in zip(pos, out):
            r[k] = ab[i] if s[k].isupper() or not s[k].isalpha() else ab[i].lower()
        return "".join(r)
    letters = [c for c in s.upper().replace("J", "I" if fam == "bifid" else "J") if c in ab and c != "."]
    ct = "".join(ab[i] for i in _frac_run([ab.index(c) for c in letters], fam, period, 1))
    if layout == "lower":
        return ct.lower()
    return " ".join(ct[i:i + 5] for i in range(0, len(ct), 5)) if layout == "groups5" else ct


def frac_dec(t, fam="bifid", period=0):
    """Inverse of frac_enc for one family/period, any layout: in-place letters (case kept), others kept; a 'j' (never
    in a Bifid square) passes through like CyberChef's. None when the text holds no square letter. Never raises."""
    try:
        ab = _FRAC[fam][0]
        t = _t(t)
        pos = [k for k, c in enumerate(t) if c.upper() in ab]
        if not pos:
            return None
        out = _frac_run([ab.index(t[k].upper()) for k in pos], fam, period, -1)
        r = list(t)
        for k, i in zip(pos, out):
            r[k] = ab[i].lower() if t[k].islower() else ab[i]
        return "".join(r)
    except Exception:  # noqa: BLE001
        return None


def _frac_fold(s):
    return re.sub(r"[^a-z]", "", s.lower().replace("j", "i"))


def frac_solve(blob, periods=(0,) + tuple(range(2, 16))):
    """(name 'bifid-p7-keep', reading, enc) when the blob is the warmups sentence under Bifid/Trifid with a standard
    square at some period: the reading's letters (I=J folded) start with the crib's. In-place layouts give the full
    sentence back; a letter stream gives its lowercase letters (digits and spacing are gone). Never raises."""
    try:
        t = _t(blob).strip()
        crib = _frac_fold(SENTENCE.split("{slug}")[0])
        if not t or len(t) > 2000 or len(_frac_fold(t)) < len(crib):
            return None
        for fam in ("bifid", "trifid"):
            for per in periods:
                c = frac_dec(t, fam, per)
                if not c or not _frac_fold(c).startswith(crib):
                    continue
                if re.search(r"[^A-Za-z ]", t) or " " in t and not re.fullmatch(r"[A-Z]{5}( [A-Z]{1,5})*", t):
                    return f"{fam}-p{per}-keep", c, (lambda f, p: lambda s: frac_enc(s, f, p, "keep"))(fam, per)
                lay = "groups5" if " " in t else "lower" if t.islower() else "upper"
                return (f"{fam}-p{per}-{lay}", c.replace(" ", "").lower(),
                        (lambda f, p, ly: lambda s: frac_enc(s, f, p, ly))(fam, per, lay))
    except Exception:  # noqa: BLE001
        pass
    return None


def frac_crib_dec(t):
    r = frac_solve(t)
    return r[1] if r else None


def frac_free(p, k=2):
    """Mastery fragment: a line under Bifid/Trifid (standard square, period full / 2-15, restarting per line), in-place
    layout -> readings that are a crib piece (_crib_piece), best by (crib chars confirmed, bigram). Never raises."""
    try:
        from lib.decode import _bigram
        lead = p[:len(p) - len(p.lstrip())]
        t = p[len(lead):].rstrip("\r\n")
        if len(t) < 4 or len(t) > 400:
            return []
        hits = {}
        for fam in ("bifid", "trifid"):
            for per in (0,) + tuple(range(2, 16)):
                c = frac_dec(t, fam, per)
                if c and c != t:
                    n = _crib_piece(c)
                    if n:
                        hits.setdefault(lead + c, (n, _bigram(c)))
        return [c for c, _s in sorted(hits.items(), key=lambda kv: kv[1], reverse=True)[:k]]
    except Exception:  # noqa: BLE001
        return []


def _frac_cands():
    """(name, enc, dec) for Bifid/Trifid x layout x period; the crib-gated any-period decoder rides the first only."""
    out = []
    for fam, lays in _FRAC_LAYOUTS.items():
        for lay in lays:
            for per in _FRAC_PERIODS:
                out.append((f"{fam}-p{per}-{lay}", (lambda f, p, ly: lambda s: frac_enc(s, f, p, ly))(fam, per, lay),
                            None if out else frac_crib_dec))
    return out


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

# CSS / HTML colour codes: the bytes in RGB triples, one colour token each -- '#4e6963' (CyberChef-style "hex colour"
# strings, Pillow pixel dumps), the short '#RGB' (3 nibbles per token, the hex stream cut in threes), '#RRGGBBAA', or
# 'rgb(78, 105, 99)' / 'rgba(...)' decimal triples; CSS colour NAMES read through their #RRGGBB. The last token is
# padded with 00 (or 20) bytes / a 0 nibble; the decoder concatenates every token's hex digits in order and drops
# <= 2 trailing pad bytes. Strict: the line holds only colour tokens and separators (whitespace , ; |).
_CSSCOL_TOK = re.compile(r"#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![0-9a-zA-Z])"
                      r"|rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*([\d.]+%?)\s*)?\)"
                      r"|([a-zA-Z]{3,20})", re.I)


def _css_names():
    try:
        from PIL import ImageColor
        return ImageColor.colormap
    except Exception:  # noqa: BLE001 - no Pillow: names unsupported
        return {}


def css_hex_enc(s, form="hex", sep=" ", pad=b"\0", upper=False):
    b = _u(s)
    if form == "hex3":
        h = b.hex()
        h += "0" * (-len(h) % 3)
        out = ["#" + h[i:i + 3] for i in range(0, len(h), 3)]
    else:
        b += pad * (-len(b) % 3)
        tri = [b[i:i + 3] for i in range(0, len(b), 3)]
        out = [f"rgb({t[0]}, {t[1]}, {t[2]})" for t in tri] if form == "rgb" else ["#" + t.hex() for t in tri]
    return sep.join(o.upper() if upper and o[0] == "#" else o for o in out)


def css_hex_dec(t):
    t = t.strip()
    if not t or len(t) > 65536:
        raise ValueError("not css colours")
    names, pos, hx, n = None, 0, [], 0
    for m in _CSSCOL_TOK.finditer(t):
        if t[pos:m.start()].strip(" \t\r\n,;|"):
            raise ValueError("stray text between colour tokens")
        pos = m.end()
        if m.group(1):
            hx.append(m.group(1))
        elif m.group(2):
            rgb = [int(m.group(k)) for k in (2, 3, 4)]
            if max(rgb) > 255:
                raise ValueError("rgb component > 255")
            hx.append(bytes(rgb).hex())
        else:
            names = _css_names() if names is None else names
            v = names.get(m.group(6).lower())
            if not v:
                raise ValueError("not a colour name")
            hx.append(v[1:])
        n += 1
    if t[pos:].strip(" \t\r\n,;|") or n < 2:
        raise ValueError("not css colours")
    h = "".join(hx)
    if len(h) % 2:
        if h[-1] != "0":
            raise ValueError("odd nibble pad")
        h = h[:-1]
    b = bytes.fromhex(h)
    k = len(b) - len(b.rstrip(b"\0"))
    if k > 2:
        raise ValueError("css NUL run")
    b = b[:len(b) - k] if k else b[:len(b) - min(2, len(b) - len(b.rstrip(b" ")))]
    return _t(b)


def css_hex_free(p):
    """Speculative free-line CSS colours: only a line of >= 2 colour tokens (not ALL bare names) -> printable text."""
    if not re.search(r"#[0-9a-fA-F]{3}|rgba?\(", p):
        return []
    got = safe(css_hex_dec, p)
    return [p[:len(p) - len(p.lstrip())] + got] if got and got.strip() and any(c.isalpha() for c in got) else []


# I Ching (the "Sixty-Four" pun): each hexagram U+4DC0..U+4DFF = one base64 sextet. King Wen index (cp - 0x4DC0) into
# the std / url alphabet; or the hexagram's own 6-line binary value (lines from its trigram pair: yang=1 or yin=1,
# bottom line MSB or LSB) into the std alphabet. '=' / ☯ padding optional. Trigrams U+2630..U+2637 = octal digits
# (cp - 0x2630 = Unicode's broken-line bits, top line LSB; or the complement): space-separated octal char codes, or a
# run-together blob in 3-digit groups. Strict: every char in the block, the bytes printable UTF-8 text.
_HEX0, _TRI0 = 0x4DC0, 0x2630
# King Wen n -> (lower, upper) trigram as cp - 0x2630 (0 heaven 1 lake 2 fire 3 thunder 4 wind 5 water 6 mountain 7 earth)
_KING_WEN = ((0, 0), (7, 7), (3, 5), (5, 6), (0, 5), (5, 0), (5, 7), (7, 5), (0, 4), (1, 0), (0, 7), (7, 0), (2, 0),
             (0, 2), (6, 7), (7, 3), (3, 1), (4, 6), (1, 7), (7, 4), (3, 2), (2, 6), (7, 6), (3, 7), (3, 0), (0, 6),
             (3, 6), (4, 1), (5, 5), (2, 2), (6, 1), (4, 3), (6, 0), (0, 3), (7, 2), (2, 7), (2, 4), (1, 2), (6, 5),
             (5, 3), (1, 6), (3, 4), (0, 1), (4, 0), (7, 1), (4, 7), (5, 1), (4, 5), (2, 1), (4, 2), (3, 3), (6, 6),
             (6, 4), (1, 3), (2, 3), (6, 2), (4, 4), (1, 1), (5, 4), (1, 5), (1, 4), (6, 3), (2, 5), (5, 2))
_B64STD = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"
_B64URL = _B64STD[:62] + "-_"


def _hexa_lines(n):
    """King Wen index -> 6 yang(1)/yin(0) lines, bottom first."""
    lo, up = _KING_WEN[n]
    return [1 - (t >> b & 1) for t in (lo, up) for b in (2, 1, 0)]


def _hexa_order(yang=1, bottom_msb=True):
    """sextet value -> King Wen index, for one binary-value convention."""
    inv = {}
    for n in range(64):
        bits = [x if yang else 1 - x for x in _hexa_lines(n)]
        inv[int("".join(map(str, bits if bottom_msb else bits[::-1])), 2)] = n
    return [inv[v] for v in range(64)]


_HEXA_ORDERS = {"kingwen": list(range(64))}
_HEXA_ORDERS.update({f"bin-{'yang' if y else 'yin'}-{'bot' if m else 'top'}": _hexa_order(y, m)
                     for y in (1, 0) for m in (True, False)})


def iching_enc(s, order="kingwen", alpha=_B64STD):
    perm = _HEXA_ORDERS[order]
    return "".join(chr(_HEX0 + perm[alpha.index(c)]) for c in base64.b64encode(_u(s)).decode().rstrip("="))


def iching_dec(t, order="kingwen", alpha=_B64STD):
    t = re.sub(r"\s+", "", t).rstrip("=☯")
    if len(t) < 2 or len(t) > 32768 or len(t) % 4 == 1 or not all(_HEX0 <= ord(c) < _HEX0 + 64 for c in t):
        raise ValueError("not hexagrams")
    inv = {n: v for v, n in enumerate(_HEXA_ORDERS[order])}
    b = "".join(alpha[inv[ord(c) - _HEX0]] for c in t)
    out = _t(base64.b64decode(b + "=" * (-len(b) % 4), altchars=alpha[62:].encode(), validate=True))
    if any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in out):
        raise ValueError("hexagram bytes not text")
    return out


def iching_reads(t):
    if not isinstance(t, str):
        return []
    out = []
    for order in _HEXA_ORDERS:
        for alpha in ((_B64STD, _B64URL) if order == "kingwen" else (_B64STD,)):
            x = safe(lambda v: iching_dec(v, order, alpha), t)
            if x and x.strip() and x not in [y for _k, y in out]:
                out.append((order == "kingwen", x))
    big = _tern_bigram()
    return [x for _k, x in sorted(out, key=lambda q: (_texty(q[1]) >= 0.9, q[0], big(q[1])), reverse=True)]


def iching_free(p):
    """Speculative free-line I Ching: an all-hexagram line -> its printable base64 readings, most English first."""
    lead = p[:len(p) - len(p.lstrip())] if isinstance(p, str) else ""
    return [lead + x for x in iching_reads(p)[:3]]


def trigram_enc(s, sep=" ", comp=False):
    return sep.join("".join(chr(_TRI0 + (7 - int(d) if comp else int(d))) for d in f"{b:03o}") for b in _u(s))


def trigram_dec(t, comp=False):
    t = t.strip()
    toks = [x for x in re.split(r"[\s,;|/_-]+", t) if x]
    flat = "".join(toks)
    if len(flat) < 3 or len(flat) > 40000 or not all(_TRI0 <= ord(c) <= _TRI0 + 7 for c in flat):
        raise ValueError("not trigrams")
    dig = lambda g: int("".join(str(7 - (ord(c) - _TRI0) if comp else ord(c) - _TRI0) for c in g), 8)
    if len(toks) == 1:
        if len(flat) % 3:
            raise ValueError("trigram blob not 3-digit groups")
        toks = [flat[i:i + 3] for i in range(0, len(flat), 3)]
    vals = [dig(g) for g in toks]
    if max(vals) > 255 or min(vals) < 9:
        raise ValueError("trigram codes out of byte range")
    out = bytes(vals).decode("utf-8")
    if any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in out):
        raise ValueError("trigram bytes not text")
    return out


def trigram_free(p):
    """Speculative free-line trigrams-as-octal: both polarities, printable readings, most English first."""
    out = [x for x in (safe(trigram_dec, p), safe(lambda v: trigram_dec(v, True), p)) if x and x.strip()]
    big = _tern_bigram()
    lead = p[:len(p) - len(p.lstrip())] if isinstance(p, str) else ""
    return [lead + x for x in sorted(dict.fromkeys(out), key=lambda x: (_texty(x) >= 0.9, big(x)), reverse=True)]


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


# Generic two-symbol fixed-width group carrier (generalizes D17 bacon-hex): any 2 distinct non-space symbols (a/b,
# A/B, 0/1, X/O, an emoji pair, a/A case pattern) as bits, groups of 4-8, both symbol->bit assignments. Values read as
# UTF-8 hex nibbles (all < 16, even count), ASCII/UTF-8 bytes (width 7-8), else Bacon-26/24 letters (width 5).
# Values as alphabet indexes ("Thirty-Two"/"Sixty-Four" a's and b's): width 5 -> base32 A-Z2-7, width 6 -> base64
# (std, then url alphabet), width 3 -> octal digits (3 per byte). A cut Mastery fragment is re-aligned to a whole
# quantum and the trailing partial quantum dropped. Morse (`.`/`-` only) is left to the Morse decoders.
_TS_KIND = {"hex": 3, "ascii": 2, "b32": 2, "b64": 2, "octal": 2, "bacon": 1}
_TS_B32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
_TS_B64 = (string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/",
           string.ascii_uppercase + string.ascii_lowercase + string.digits + "-_")


def twosym_enc(s, pair="ab", width=5, inner="hex", sep=" "):
    if inner == "hex":
        vals = [int(c, 16) for c in _u(s).hex()]
    elif inner in ("b32", "b64", "b64url"):
        txt = (base64.b32encode if inner == "b32" else base64.b64encode)(_u(s)).decode().rstrip("=")
        vals = [(_TS_B32 if inner == "b32" else _TS_B64[inner == "b64url"]).index(c) for c in txt]
    elif inner == "octal":
        vals = [int(c, 8) for c in "".join("%03o" % b for b in _u(s))]
    elif inner == "ascii":
        vals = list(_u(s))
    else:
        alpha = "abcdefghijklmnopqrstuvwxyz" if inner == "bacon26" else _BACON24
        vals = [alpha.index({"j": "i", "v": "u"}.get(c, c) if inner == "bacon24" else c)
                for c in s.lower() if "a" <= c <= "z"]
    return sep.join("".join(pair[int(b)] for b in f"{v:0{width}b}") for v in vals)


def _ts_reads(t, kinds=None):
    """[(key, text)] for every (polarity, width, value-range) reading of a strict two-symbol fragment."""
    t = t.strip().strip("\"'").replace("️", "").replace("︎", "")
    sy = [c for c in t if not c.isspace()]
    syms = sorted(set(sy), key=sy.index)
    if len(syms) != 2 or set(syms) == {".", "-"} or len(sy) < 16 or len(sy) > 20000:
        return []
    if set(syms) == {"0", "1"} or {s.lower() for s in syms} == {"a", "b"}:
        syms.sort(key=lambda c: c.lower())   # natural polarity (0/a = 0) first
    toks = t.split()
    lens = {len(x) for x in toks}
    if len(toks) > 1 and len(lens) == 1 and 3 <= min(lens) <= 8:
        widths = [min(lens)]
    else:
        widths = [w for w in range(4, 9) if all(n % w == 0 for n in lens)]
    try:
        from lib.decode import _bigram
    except Exception:  # noqa: BLE001
        def _bigram(_s):
            return 0.0
    out = []
    for z, o in (syms, syms[::-1]):
        bits = "".join("1" if c == o else "0" for c in sy)
        for w in widths:
            vals = [int(bits[i:i + w], 2) for i in range(0, len(bits), w)]
            reads = []
            if max(vals) < 16 and len(vals) % 2 == 0:
                try:
                    reads.append(("hex", bytes.fromhex("".join("%x" % v for v in vals)).decode("utf-8")))
                except ValueError:
                    pass
            if w >= 7:
                try:
                    reads.append(("ascii", bytes(vals).decode("utf-8")))
                except ValueError:
                    pass
            reads += _ts_index_reads(w, vals)
            if w == 5 and max(vals) < 26:
                b26 = "".join(chr(97 + v) for v in vals)
                b24 = "".join(_BACON24[v] for v in vals) if max(vals) < 24 else None
                reads.append(("bacon", b24 if b24 and _bigram(b24) > _bigram(b26) else b26))
            for kind, x in reads:
                if kinds and kind not in kinds:
                    continue
                if x and not any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in x):
                    out.append(((_texty(x) >= 0.9, _TS_KIND[kind], _bigram(x)), x))
    return sorted(out, key=lambda r: r[0], reverse=True)


def _ts_index_reads(w, vals):
    """Group values as base32 (w=5) / base64 (w=6) alphabet indexes or octal digits (w=3) -> [(kind, utf-8 text)].
    Alignment offsets (a fragment cut mid-quantum) are tried in order until one reads as text."""
    def ok(x):
        return x and _texty(x) >= 0.9 and not any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in x)

    out = []
    if w == 3:
        for off in range(3):
            v = vals[off:len(vals) - (len(vals) - off) % 3]
            bs = [v[i] * 64 + v[i + 1] * 8 + v[i + 2] for i in range(0, len(v), 3)]
            try:
                x = bytes(bs).decode("utf-8") if bs and max(bs) < 256 else ""
            except ValueError:
                continue
            if ok(x):
                return [("octal", x)]
        return out
    if w not in (5, 6):
        return out
    q = 8 if w == 5 else 4                       # chars per whole quantum (5 / 3 bytes)
    for off in range(q):
        for al in ([_TS_B32] if w == 5 else _TS_B64):
            txt = "".join(al[v] for v in vals[off:])
            cut = (0, 1, 0, 1, 0, 0, 1, 0)[len(txt) % 8] if w == 5 else (len(txt) % 4 == 1)   # invalid tail chars
            body = txt[:len(txt) - cut]
            try:
                if w == 5:
                    raw = base64.b32decode(body + "=" * (-len(body) % 8))
                else:
                    raw = base64.b64decode(body + "=" * (-len(body) % 4), altchars=al[62:].encode(), validate=True)
                x = raw.decode("utf-8")
            except ValueError:
                continue
            if ok(x) and ("b32" if w == 5 else "b64", x) not in out:
                out.append(("b32" if w == 5 else "b64", x))
        if out:
            break
    return out


def twosym_free(p, k=3):
    seen = []
    for (ok, _k, _b), x in _ts_reads(p):
        if ok and x not in seen:
            seen.append(x)
    return seen[:k]


def twosym_dec(t):
    r = twosym_free(t, 1)
    return r[0] if r else None


def twosym_index_dec(t):
    """Only the alphabet-index readings (base32 w5 / base64 w6 / octal w3) of a two-symbol fragment, else None."""
    try:
        r = [x for (ok, _k, _b), x in _ts_reads(t, ("b32", "b64", "octal")) if ok]
    except Exception:  # noqa: BLE001
        return None
    return r[0] if r else None


# Kenny code (South Park "Kennyspeak") and other fixed-width THREE-symbol carriers: base-3 digits, Bacon-like.
# Kenny: letter a-z -> 3 symbols of m/p/f (m=0 p=1 f=2, a=mmm .. z=ffp), an upper-case letter capitalizes its first
# symbol (A=Mmm), every other character kept in place. Generic: any 3 distinct symbols (0/1/2, m/p/f, an emoji
# triple) in groups of 3-6 -> a-z letters (width 3, values < 26), UTF-8 hex nibbles (all < 16), ASCII/UTF-8 bytes
# (width 5-6). Unknown symbol order: every assignment is tried, natural order (0/1/2, m/p/f) first.
_TERN_KIND = {"hex": 3, "ascii": 2, "alpha": 1}


def kenny_enc(s, sym="mpf"):
    out = []
    for c in s:
        lc = c.lower()
        if "a" <= lc <= "z":
            n = ord(lc) - 97
            g = sym[n // 9] + sym[n // 3 % 3] + sym[n % 3]
            out.append(g[0].upper() + g[1:] if c.isupper() else g)
        else:
            out.append(c)
    return "".join(out)


def tern_enc(s, sym="012", width=3, inner="alpha", sep=" "):
    if inner == "hex":
        vals = [int(c, 16) for c in _u(s).hex()]
    elif inner in ("b32", "b64", "b64url"):
        txt = (base64.b32encode if inner == "b32" else base64.b64encode)(_u(s)).decode().rstrip("=")
        vals = [(_TS_B32 if inner == "b32" else _TS_B64[inner == "b64url"]).index(c) for c in txt]
    elif inner == "octal":
        vals = [int(c, 8) for c in "".join("%03o" % b for b in _u(s))]
    elif inner == "ascii":
        vals = list(_u(s))
    else:
        vals = [ord(c) - 97 for c in s.lower() if "a" <= c <= "z"]
    return sep.join("".join(sym[v // 3 ** i % 3] for i in range(width - 1, -1, -1)) for v in vals)


def _tern_orders(syms, natural):
    """0/1/2 and m/p/f read in their natural order only; any other symbol triple tries all 6 assignments."""
    nat = [c for c in natural if c in syms]
    if len(nat) == 3:
        return [nat]
    first = sorted(syms)
    return [first] + [list(p) for p in itertools.permutations(first) if list(p) != first]


def _tern_bigram():
    try:
        from lib.decode import _bigram
        return _bigram
    except Exception:  # noqa: BLE001
        return lambda _s: 0.0


def kenny_reads(t):
    """Kenny keep-mode readings: the letters are exactly 3 symbols (any case), runs of them decode 3 at a time, every
    other character stays. [] unless every letter run is a clean multiple of 3 with values < 26."""
    t = t.strip()
    letters = [c.lower() for c in t if c.isalpha()]
    syms = set(letters)
    if len(syms) != 3 or len(letters) < 9 or len(letters) < 0.5 * len(re.sub(r"\s", "", t)) or len(t) > 20000:
        return []
    runs = re.findall(r"[^\W\d_]+|[\W\d_]+", t)
    if any(r[0].isalpha() and len(r) % 3 for r in runs):
        return []
    big = _tern_bigram()
    out = []
    for order in _tern_orders(syms, "mpf"):
        idx = {c: i for i, c in enumerate(order)}
        res = []
        for r in runs:
            if not r[0].isalpha():
                res.append(r)
                continue
            for i in range(0, len(r), 3):
                g = r[i:i + 3]
                n = idx[g[0].lower()] * 9 + idx[g[1].lower()] * 3 + idx[g[2].lower()]
                if n >= 26:
                    break
                res.append(chr(97 + n).upper() if g[0].isupper() else chr(97 + n))
            else:
                continue
            break
        else:
            x = "".join(res)
            out.append(((_texty(x) >= 0.9, big(x)), x))
    return [x for _k, x in sorted(out, key=lambda r: r[0], reverse=True) if _k[0]]


def _tern_group_reads(t):
    """[(key, text)] for every (symbol order, width, value range) reading of a strict 3-symbol group fragment."""
    t = t.strip().strip("\"'").replace("️", "").replace("︎", "")
    sy = [c for c in t if not c.isspace()]
    syms = sorted(set(sy), key=sy.index)
    if len(syms) != 3 or len(sy) < 12 or len(sy) > 20000 or set(syms) <= set(".-/"):
        return []
    toks = t.split()
    lens = {len(x) for x in toks}
    if len(toks) > 1 and len(lens) == 1 and 3 <= min(lens) <= 6:
        widths = [min(lens)]
    else:
        widths = [w for w in range(3, 7) if all(n % w == 0 for n in lens)]
    big = _tern_bigram()
    natural = "012" if set(syms) == set("012") else "mpf" if {c.lower() for c in syms} == set("mpf") else ""
    out = []
    for order in _tern_orders(syms, natural):
        idx = {c: i for i, c in enumerate(order)}
        for w in widths:
            vals = []
            for i in range(0, len(sy), w):
                v = 0
                for c in sy[i:i + w]:
                    v = v * 3 + idx[c]
                vals.append(v)
            reads = []
            if w == 3 and max(vals) < 26:   # letters only: must read as English (a permuted order gives junk)
                x = "".join(chr(97 + v) for v in vals)
                if len(x) >= 8 and big(x) > -7.0:
                    reads.append(("alpha", x))
            if max(vals) < 16 and len(vals) % 2 == 0:
                try:
                    reads.append(("hex", bytes.fromhex("".join("%x" % v for v in vals)).decode("utf-8")))
                except ValueError:
                    pass
            if w >= 5 and max(vals) < 256:
                try:
                    reads.append(("ascii", bytes(vals).decode("utf-8")))
                except ValueError:
                    pass
            for kind, x in reads:
                if x and not any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in x):
                    out.append(((_texty(x) >= 0.9, _TERN_KIND[kind], big(x)), x))
    return sorted(out, key=lambda r: r[0], reverse=True)


def tern_free(p, k=3):
    seen = []
    kr, gr = kenny_reads(p), [x for (ok, _k, _b), x in _tern_group_reads(p) if ok]
    if len({len(x) for x in p.split()}) == 1:   # uniform groups (or one blob): a group reading beats Kenny keep-mode
        kr, gr = gr, kr
    for x in kr + gr:
        if x not in seen:
            seen.append(x)
    return seen[:k]


def tern_dec(t):
    r = tern_free(t, 1)
    return r[0] if r else None


# Char codes / hex nibbles as fixed-width DIGIT groups in a radix between binary and octal (base 3-7): quaternary
# 4-digit bytes (0-3), base-5 3/4-digit, base-6/7 3-digit, 2-digit nibbles (numpy.base_repr / Python int(g, r)).
# Radix = max digit + 1 (a sentence always shows its top digit; a larger radix turns a ternary decoy into letters),
# width = the constant token length (a run-together blob: every width dividing it). Values all < 16 (even count) -> UTF-8 hex nibbles, else 9-255 -> UTF-8 bytes.
# Digit 7+ (octal/decimal) or only 0/1 (binary) -> None.
_RADIX_SEP = re.compile(r"[\s,;|:/_-]+")


def radix_enc(s, r=4, width=4, inner="ascii", sep=" "):
    vals = [int(c, 16) for c in _u(s).hex()] if inner == "hex" else list(_u(s))
    out = []
    for v in vals:
        d = ""
        for _ in range(width):
            v, m = divmod(v, r)
            d = str(m) + d
        out.append(d)
    return sep.join(out)


def _radix_reads(t):
    """[(key, text)] for every width reading (hex nibbles or char codes) of a strict base-3..7 digit-group fragment."""
    if not isinstance(t, str):
        return []
    t = t.strip().strip("\"'[]()")
    toks = [x for x in _RADIX_SEP.split(t) if x]
    flat = "".join(toks)
    if not toks or not flat.isdigit() or not flat.isascii() or len(flat) < 8 or len(flat) > 40000:
        return []
    maxd = int(max(flat))
    if maxd < 2 or maxd > 6:
        return []
    lens = {len(x) for x in toks}
    if len(toks) > 1:
        if len(lens) != 1 or not 2 <= min(lens) <= 6:
            return []
        widths = [min(lens)]
    else:
        widths = [w for w in range(2, 7) if len(flat) % w == 0]
    big = _tern_bigram()
    r = maxd + 1
    out = []
    for w in widths:
        vals = [int(flat[i:i + w], r) for i in range(0, len(flat), w)]
        x = None
        try:
            if max(vals) < 16 and len(vals) % 2 == 0:
                x = bytes.fromhex("".join("%x" % v for v in vals)).decode("utf-8")
            elif max(vals) < 256 and min(vals) >= 9 and r ** w > 122:
                x = bytes(vals).decode("utf-8")
        except ValueError:
            pass
        if x and not any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in x):
            out.append(((_texty(x) >= 0.9, big(x)), x))
    return sorted(out, key=lambda q: q[0], reverse=True)


def radix_free(p, k=3):
    seen = []
    for (ok, _b), x in _radix_reads(p):
        if ok and x not in seen:
            seen.append(x)
    return seen[:k]


def radix_dec(t):
    r = radix_free(t, 1)
    return r[0] if r else None


# Ordered Unicode glyph sets as radix digits: a glyph's index in its run is a digit (dice U+2680-2685 = 0-5, chess
# U+2654-265F = 0-11 or either colour's six, zodiac U+2648-2653, card suits U+2660-2667 / the four filled suits, Mahjong
# U+1F000-1F02B), then the radix_dec rules: fixed-width groups (token length, or every width dividing a blob), values
# < 16 (even count) -> UTF-8 hex nibbles, else 9-255 -> UTF-8 bytes. Dice "1-6" = face - 1 = the same digits (a radix-7
# reading has no zero face). Every glyph of the line must sit in ONE set -> else None.
_GLYPH_SETS = {
    "dice": "".join(chr(0x2680 + i) for i in range(6)),
    "chess": "".join(chr(0x2654 + i) for i in range(12)),
    "chess-white": "".join(chr(0x2654 + i) for i in range(6)),
    "chess-black": "".join(chr(0x265A + i) for i in range(6)),
    "zodiac": "".join(chr(0x2648 + i) for i in range(12)),
    "suits8": "".join(chr(0x2660 + i) for i in range(8)),
    "suits4": "♠♣♥♦",       # filled suits in code-point order
    "suits4-bridge": "♣♦♥♠",  # bridge rank order: clubs < diamonds < hearts < spades
    "mahjong": "".join(chr(0x1F000 + i) for i in range(44)),
}
_GLYPH_SEP = re.compile(r"[\s,;|:/_.-]+")


def glyph_radix_enc(s, kind="dice", width=3, inner="ascii", sep=" "):
    al = _GLYPH_SETS[kind]
    r = len(al)
    vals = [int(c, 16) for c in _u(s).hex()] if inner == "hex" else list(_u(s))
    out = []
    for v in vals:
        d = ""
        for _ in range(width):
            v, m = divmod(v, r)
            d = al[m] + d
        out.append(d)
    return sep.join(out)


def _glyph_text(vals):
    try:
        if max(vals) < 16 and len(vals) % 2 == 0:
            x = bytes.fromhex("".join("%x" % v for v in vals)).decode("utf-8")
        elif max(vals) < 256 and min(vals) >= 9:
            x = bytes(vals).decode("utf-8")
        else:
            return None
    except ValueError:
        return None
    return x if x and not any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in x) else None


def _glyph_reads(t):
    """[(key, text)] for every (glyph set, digit convention, width) reading of an all-one-glyph-set fragment."""
    if not isinstance(t, str) or len(t) > 80000:
        return []
    t = t.strip().strip("\"'[]()").replace("️", "").replace("︎", "")
    toks = [x for x in _GLYPH_SEP.split(t) if x]
    flat = "".join(toks)
    if len(flat) < 4:
        return []
    chars = set(flat)
    lens = {len(x) for x in toks}
    if len(toks) > 1 and len(lens) != 1:
        return []
    big = _tern_bigram()
    out, seen = [], set()
    for kind, al in _GLYPH_SETS.items():
        if not chars <= set(al):
            continue
        digs, r = [al.index(c) for c in flat], len(al)
        for w in ([min(lens)] if len(toks) > 1 else [w for w in range(1, 9) if len(flat) % w == 0]):
            if r ** w < 16 or w > 8:
                continue
            vals = []
            for i in range(0, len(digs), w):
                v = 0
                for d in digs[i:i + w]:
                    v = v * r + d
                vals.append(v)
            x = _glyph_text(vals)
            if x and x not in seen:
                seen.add(x)
                out.append(((_texty(x) >= 0.9, big(x)), x))
    return sorted(out, key=lambda q: q[0], reverse=True)


def glyph_radix_free(p, k=3):
    """Speculative free-line glyph radix: an all-dice / chess / zodiac / suits / Mahjong line -> its English readings."""
    lead = p[:len(p) - len(p.lstrip())] if isinstance(p, str) else ""
    return [lead + x for (ok, _b), x in _glyph_reads(p) if ok][:k]


def glyph_radix_dec(t):
    r = glyph_radix_free(t, 1)
    return r[0].strip() if r else None


# 4-bit binary nibbles carrying hex (the next "sixteen" carrier after D16 morse-hex / D17 bacon-hex): each UTF-8 hex
# digit as a [01]{4} group, two per byte. Groups split by whitespace or , ; | : / _ - (a wider byte gap allowed), or run
# together (len % 8 == 0: the same bits as binary8-nospace). swap: low nibble first (perl unpack "h*", CyberChef ROL 4).
# Told from binary8 by group width: any token that is not exactly 4 bits -> None.
_B4_SEP = re.compile(r"[\s,;|:/_-]+")


def bin4_enc(s, sep=" ", byte=None, swap=False):
    hx = _u(s).hex()
    if swap:
        hx = "".join(hx[i + 1] + hx[i] for i in range(0, len(hx), 2))
    g = [f"{int(c, 16):04b}" for c in hx]
    return sep.join(g) if byte is None else byte.join(sep.join(g[i:i + 2]) for i in range(0, len(g), 2))


def bin4_dec(t, swap=False):
    """The text under 4-bit binary hex nibbles, else None (8-bit groups, odd nibble count, non-UTF-8, control chars)."""
    if not isinstance(t, str):
        return None
    t = t.strip().strip("\"'[]()")
    toks = [x for x in _B4_SEP.split(t) if x]
    if not toks or any(set(x) - {"0", "1"} for x in toks):
        return None
    if len(toks) == 1:
        if len(t) < 8 or len(t) % 8:
            return None
        toks = [t[i:i + 4] for i in range(0, len(t), 4)]
    elif any(len(x) != 4 for x in toks) or len(toks) % 2:
        return None
    hx = "".join("%x" % int(x, 2) for x in toks)
    if swap:
        hx = "".join(hx[i + 1] + hx[i] for i in range(0, len(hx), 2))
    try:
        out = bytes.fromhex(hx).decode("utf-8")
    except ValueError:
        return None
    if any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in out):
        return None
    return out


def bin4_free(p):
    """Mastery free line: the plain-order reading, then the nibble-swapped one, English-looking reads only."""
    return [x for x in (bin4_dec(p), bin4_dec(p, swap=True)) if x and _texty(x) >= 0.9]


# BCD of decimal char codes (CyberChef "To BCD" 8421 / Excess-3 per char code): each decimal digit of a char's code as a
# 4-bit group. Char boundaries: a wider separator (" / ", "|", ",", ";", 2+ spaces, newline), one token per char (8/12/16
# bits run together), or none (a nibble stream: 3-digit zero-padded, packed = padded to whole bytes, or 2/3-digit ASCII
# greedy). Unpacked BCD (one byte per digit, high nibble 0) too. Every nibble must be a digit 0-9 (8421) / 3-12 (XS-3).
_BCD_CHR = re.compile(r"\s*[/|,;]\s*|\s{2,}|\n")


def bcd_enc(s, sep=" ", char=" / ", pad=0, xs3=False):
    """pad: 0 = digits as-is, 3 = zero-pad each code to 3 digits, -1 = packed (pad to an even digit count)."""
    out = []
    for c in s:
        d = str(ord(c))
        d = d.zfill(pad) if pad > 0 else d.zfill(len(d) + len(d) % 2) if pad < 0 else d
        out.append(sep.join(f"{int(x) + 3 * xs3:04b}" for x in d))
    return char.join(out)


def _bcd_digits(bits, xs3):
    if not bits or len(bits) % 4:
        return None
    ds = [int(bits[i:i + 4], 2) - 3 * xs3 for i in range(0, len(bits), 4)]
    return "".join(map(str, ds)) if all(0 <= d <= 9 for d in ds) else None


def _bcd_stream(ds):
    """[decimal digit stream] -> [code lists] under fixed-3, packed (0 -> 4 digits else 2) and ASCII-greedy splits."""
    outs = []
    if len(ds) % 3 == 0:
        outs.append([int(ds[i:i + 3]) for i in range(0, len(ds), 3)])
    for rule in ({"0": 4}, {"1": 3}):
        i, codes = 0, []
        while i < len(ds):
            n = rule.get(ds[i], 2)
            if i + n > len(ds):
                codes = None
                break
            codes.append(int(ds[i:i + n]))
            i += n
        if codes:
            outs.append(codes)
    return outs


def _bcd_text(codes):
    try:
        out = "".join(map(chr, codes))
    except (ValueError, OverflowError):
        return None
    return out if out and all(c.isprintable() or c in "\t\n\r" for c in out) else None


def bcd_reads(t):
    """Text readings of a BCD line (8421 first, then Excess-3), else []."""
    if not isinstance(t, str) or len(t) > 262144:
        return []
    t = t.strip().strip("\"'[]()")
    if not t or set(t) - set("01 \t\r\n/|,;"):
        return []
    reads = []
    for xs3 in (False, True):
        groups = [g for g in _BCD_CHR.split(t) if g.strip()]
        streams = []
        if len(groups) > 1:   # explicit char boundaries
            ds = [_bcd_digits(re.sub(r"\s", "", g), xs3) for g in groups]
            if all(ds):
                streams.append([[int(d) for d in ds]])
        else:
            toks = t.split()
            if len(toks) > 1 and all(len(x) == 8 for x in toks) and not xs3 and all(int(x, 2) <= 9 for x in toks):
                streams.append(_bcd_stream("".join(str(int(x, 2)) for x in toks)))   # unpacked: a byte per digit
            elif len(toks) > 1 and any(len(x) > 4 for x in toks):              # one token per char
                ds = [_bcd_digits(x, xs3) for x in toks]
                if all(ds):
                    streams.append([[int(d) for d in ds]])
            else:
                ds = _bcd_digits("".join(toks), xs3)
                if ds:
                    streams.append(_bcd_stream(ds))
        for cl in streams:
            for codes in cl:
                x = _bcd_text(codes)
                if x and x not in reads:
                    reads.append(x)
    return reads


def bcd_dec(t):
    r = sorted(bcd_reads(t), key=_texty, reverse=True)
    return r[0] if r else None


def bcd_free(p):
    return [x for x in bcd_reads(p) if _texty(x) >= 0.9][:3]


# Address notation: the bytes written as network / ID addresses -- IPv4 dotted quads ('78.105.99.101 32.119.111.114'),
# IPv6 (8 hex groups, leading zeros dropped, the zero-padding run compressed to '::'), MAC (6 bytes: aa:bb:.. / aa-bb-..
# / Cisco aabb.ccdd.eeff) or UUIDs (16 bytes, 8-4-4-4-12, RFC order or the Microsoft GUID mixed-endian bytes_le).
# Addresses are split by whitespace , ; | /; the last one is short or NUL-padded (trailing NULs stripped).
_ADDR_SPLIT = re.compile(r"(?:\s*[,;|/]\s*|\s+)+")
_ADDR_KINDS = ("ipv4", "ipv6", "mac", "uuid", "guid")


def _v6_compress(g):
    """RFC 5952: lowercase, no leading zeros, the longest run of >= 2 zero groups (first on a tie) as '::'."""
    best, run = (0, 0), None
    for i, x in enumerate(g + [1]):
        if x == 0 and run is None:
            run = i
        elif x and run is not None:
            best, run = max(best, (i - run, -run)), None
    h = [f"{x:x}" for x in g]
    if best[0] < 2:
        return ":".join(h)
    a = -best[1]
    return ":".join(h[:a]) + "::" + ":".join(h[a + best[0]:])


def addr_enc(s, kind="ipv4", pad=True, sep=" ", style=":", upper=False, le=False):
    b = _u(s)
    le, kind = le or kind == "guid", "uuid" if kind == "guid" else kind
    n = {"ipv4": 4, "ipv6": 16, "mac": 6, "uuid": 16}[kind]
    if pad:
        b += b"\0" * (-len(b) % n)
    out = []
    for c in (b[i:i + n] for i in range(0, len(b), n)):
        if kind == "ipv4":
            out.append(".".join(map(str, c)))
        elif kind == "ipv6":
            g = [int.from_bytes(c[i:i + 2].ljust(2, b"\0") if len(c) == n else c[i:i + 2], "big")
                 for i in range(0, len(c), 2)]
            out.append(_v6_compress(g) if len(c) == n else ":".join(f"{x:x}" for x in g))
        elif kind == "mac":
            h = c.hex()
            out.append(".".join(h[i:i + 4] for i in range(0, len(h), 4)) if style == "." else
                       style.join(h[i:i + 2] for i in range(0, len(h), 2)))
        else:
            if le and len(c) == n:
                c = c[3::-1] + c[5:3:-1] + c[7:5:-1] + c[8:]
            h = c.hex()
            out.append("-".join(h[a:z] for a, z in ((0, 8), (8, 12), (12, 16), (16, 20), (20, 32)) if h[a:z]))
    out = sep.join(out)
    return out.upper() if upper else out


def _addr_tok(x, kind, last):
    """One address token -> its bytes, else None. Only the last token may be short."""
    if kind == "ipv4":
        if not re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){0,3}", x):
            return None
        v = [int(o) for o in x.split(".")]
        return bytes(v) if max(v) < 256 and (len(v) == 4 or (last and "." in x)) else None
    if kind == "ipv6":
        if not re.fullmatch(r"[0-9a-fA-F:]{2,39}", x) or x.count("::") > 1 or ":::" in x:
            return None
        if "::" in x:
            a, z = (p.split(":") if p else [] for p in x.split("::"))
            if len(a) + len(z) > 6:
                return None
            g = a + ["0"] * (8 - len(a) - len(z)) + z
        else:
            g = x.split(":")
            if len(g) != 8 and not (last and len(g) > 1):
                return None
        if not all(0 < len(h) <= 4 for h in g):
            return None
        return b"".join(int(h, 16).to_bytes(2, "big") for h in g)
    if kind == "mac":
        if re.fullmatch(r"[0-9a-fA-F]{4}(?:\.[0-9a-fA-F]{4}){0,2}", x):
            g = x.split(".")
        elif re.fullmatch(r"[0-9a-fA-F]{2}(?:([:-])[0-9a-fA-F]{2}){0,5}", x) and len({c for c in x if c in ":-"}) <= 1:
            g = re.split(r"[:-]", x)
        else:
            return None
        h = "".join(g)
        return bytes.fromhex(h) if len(h) == 12 or (last and len(g) > 1) else None
    x = re.sub(r"(?i)^urn:uuid:", "", x).strip("{}")
    if re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", x):
        return bytes.fromhex(x.replace("-", ""))
    if last and re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{1,4}){0,3}(?:-[0-9a-fA-F]{1,12})?", x):
        h = x.replace("-", "")
        return bytes.fromhex(h) if len(h) % 2 == 0 else None
    return None


def addr_reads(t, kind=None):
    """[(kind, text)] readings of an address-notation line (every token one kind), else []."""
    if not isinstance(t, str) or len(t) > 262144:
        return []
    toks = [x for x in _ADDR_SPLIT.split(t.strip().strip("\"'[]()")) if x]
    if not toks:
        return []
    reads = []
    for k in (kind,) if kind else _ADDR_KINDS:
        bs = [_addr_tok(x, "uuid" if k == "guid" else k, i == len(toks) - 1) for i, x in enumerate(toks)]
        if not all(b is not None for b in bs):
            continue
        if k == "guid":   # Microsoft GUID text: Data1-3 little-endian
            bs = [b[3::-1] + b[5:3:-1] + b[7:5:-1] + b[8:] if len(b) == 16 else b for b in bs]
        for raw in (b"".join(bs).rstrip(b"\0"), b"".join(b.rstrip(b"\0") for b in bs)):
            try:
                x = raw.decode("utf-8")
            except UnicodeDecodeError:
                continue
            if x and all(c.isprintable() or c in "\t\n\r" for c in x) and (k, x) not in reads:
                reads.append((k, x))
    return reads


def _addr_rank(reads):
    from lib.decode import _bigram
    return sorted(dict.fromkeys(x for _k, x in reads), key=lambda x: (round(_texty(x), 2), _bigram(x)), reverse=True)


def addr_dec(t, kind=None):
    r = _addr_rank(addr_reads(t, kind))
    return r[0] if r else None


def addr_free(p):
    return [x for x in _addr_rank(addr_reads(p)) if _texty(x) >= 0.9][:3]


# Gray-coded binary (reflected binary, g = b ^ b >> 1) per byte: [01]{8} (or 7-bit) groups, or run together (len % 8).
# Plain binary of a Gray line decodes to junk; decode: b = g; g >>= 1; b ^= g until g == 0.
def gray_enc(s, bits=8, sep=" "):
    return sep.join(format(b ^ (b >> 1), f"0{bits}b") for b in _u(s))


def _ungray(g):
    b = g
    while g:
        g >>= 1
        b ^= g
    return b


def gray_reads(t):
    if not isinstance(t, str) or len(t) > 262144:
        return []
    t = t.strip().strip("\"'[]()")
    toks = [x for x in re.split(r"[\s,;|:/_-]+", t) if x]
    if not toks or any(set(x) - {"0", "1"} for x in toks):
        return []
    reads = []
    for bits in (8, 7):
        tk = toks
        if len(toks) == 1:
            if len(t) < bits * 2 or len(t) % bits:
                continue
            tk = [t[i:i + bits] for i in range(0, len(t), bits)]
        elif any(len(x) != bits for x in tk):
            continue
        try:
            out = bytes(_ungray(int(x, 2)) for x in tk).decode("utf-8")
        except ValueError:
            continue
        if out and all(c.isprintable() or c in "\t\n\r" for c in out) and out not in reads:
            reads.append(out)
    return reads


def gray_dec(t):
    """The English-looking Gray reading, else None (plain binary Gray-decodes to junk)."""
    r = gray_free(t)
    return r[0] if r else None


def gray_free(p):
    return [x for x in gray_reads(p) if _texty(x) >= 0.9]


# Binary LSB-first per byte (`basenc --base2lsbf`, Perl unpack "b8"): every [01]{8} group bit-reversed, so ASCII groups
# END in 0 and the MSB-first read is junk; also 7-bit LSB-first groups, and the whole bit stream reversed (`basenc
# --base2msbf | rev` = text reversed + LSB-first). Decode int(g[::-1], 2); whole: reverse the stream, read MSB-first.
def lsb_enc(s, bits=8, sep=" ", whole=False):
    if whole:
        return sep.join(format(b, f"0{bits}b") for b in _u(s))[::-1]
    return sep.join(format(b, f"0{bits}b")[::-1] for b in _u(s))


def _bits_txt(gs):
    try:
        out = bytes(int(x, 2) for x in gs).decode("utf-8")
    except ValueError:
        return None
    return out if out and all(c.isprintable() or c in "\t\n\r" for c in out) else None


def lsb_reads(t):
    """[(mode, text)] for mode in lsb8 / rev8 / lsb7 / rev7 whose reading is printable while the plain MSB-first read
    of the same groups is not text (that is binary8 / binary7)."""
    try:
        if not isinstance(t, str) or len(t) > 262144:
            return []
        t = t.strip().strip("\"'[]()")
        toks = [x for x in re.split(r"[\s,;|:/_-]+", t) if x]
        if not toks or any(set(x) - {"0", "1"} for x in toks):
            return []
        reads = []
        for bits in (8, 7):
            tk = toks
            if len(toks) == 1:
                if len(t) < bits * 2 or len(t) % bits:
                    continue
                tk = [t[i:i + bits] for i in range(0, len(t), bits)]
            elif any(len(x) != bits for x in tk):
                continue
            plain = _bits_txt(tk)
            if plain and _texty(plain) >= 0.9:
                continue
            for mode, gs in ((f"lsb{bits}", tk), (f"rev{bits}", tk[::-1])):
                out = _bits_txt([x[::-1] for x in gs])
                if out and _texty(out) >= 0.9 and all(out != o for _m, o in reads):
                    reads.append((mode, out))
        return reads
    except Exception:   # noqa: BLE001
        return []


def lsb_dec(t, whole=False):
    """The LSB-first (whole=False) / whole-stream-reversed (whole=True) reading, else None."""
    pre = "rev" if whole else "lsb"
    return next((o for m, o in lsb_reads(t) if m.startswith(pre)), None)


def lsb_free(p):
    from lib.decode import _bigram
    return sorted((o for _m, o in lsb_reads(p)), key=_bigram, reverse=True)[:2]


# Roman-numeral char codes (`LXXVIII CV XCIX` = "Nic"): each char's decimal code point as a Roman numeral (1-3999), one
# token per char (space / comma / dash / dot / pipe separated), any case, Unicode numeral forms (U+2160..) via NFKC.
# Words may also be split by " / " or 2+ spaces (each group decoded, joined by a space). Nibble variant: hex nibbles
# 0-15 with "N" / "nulla" for zero (no zero numeral), pairs -> bytes. Canonical numerals first, additive (IIII) lenient.
_ROMAN_OK = re.compile(r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})")
_ROMAN_V = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_enc(s, sep=" ", word=None, lower=False, nib=False):
    def r(n):
        if nib and n == 0:
            return "N"
        if not 0 < n < 4000:
            raise ValueError("no Roman numeral")
        out = ""
        for v, sym in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"),
                       (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
            out += sym * (n // v)
            n %= v
        return out
    def one(w):
        vals = [x for b in _u(w) for x in (b >> 4, b & 15)] if nib else [ord(c) for c in w]
        return sep.join(map(r, vals))
    out = word.join(one(w) for w in s.split(" ")) if word else one(s)
    return out.lower() if lower else out


def _roman_int(tok, lenient):
    """A Roman numeral token -> int (None if not one). Strict = canonical form only; lenient = any IVXLCDM run."""
    u = tok.upper()
    if u in ("N", "NULLA"):
        return 0
    if not u or (tok != u and tok != tok.lower()) or set(u) - set(_ROMAN_V):
        return None
    if _ROMAN_OK.fullmatch(u):
        lenient = True
    elif not lenient:
        return None
    n = 0
    for i, c in enumerate(u):
        v = _ROMAN_V[c]
        n += -v if i + 1 < len(u) and _ROMAN_V[u[i + 1]] > v else v
    return n if n > 0 else None


def _roman_vals(toks):
    for lenient in (False, True):
        vals = [_roman_int(x, lenient) for x in toks]
        if all(v is not None for v in vals):
            return vals
    return None


def _roman_text(vals, nib):
    if nib:
        if len(vals) % 2 or any(v > 15 for v in vals):
            return None
        try:
            return bytes(vals[i] << 4 | vals[i + 1] for i in range(0, len(vals), 2)).decode("utf-8")
        except ValueError:
            return None
    if 0 in vals:
        return None
    try:
        return "".join(map(chr, vals))
    except (ValueError, OverflowError):
        return None


def roman_reads(t):
    """Text readings of a Roman-numeral char-code line (char codes, then hex nibbles), else []."""
    if not isinstance(t, str) or len(t) > 262144:
        return []
    t = unicodedata.normalize("NFKC", t).strip().strip("\"'[]()")
    if not t or set(t.upper()) - set("IVXLCDMNULA \t\r\n,;|/.-_"):
        return []
    groups = [g for g in re.split(r"\s*/\s*|\s{2,}|\n", t) if g.strip()]
    tok_groups = [[x for x in re.split(r"[\s,;|._-]+", g) if x] for g in groups]
    if not tok_groups or not all(tok_groups):
        return []
    vals = [_roman_vals(g) for g in tok_groups]
    if not all(vals):
        return []
    reads = []
    for nib in (False, True):
        for gs in ((vals if len(vals) > 1 else None), [sum(vals, [])]):
            if gs is None:
                continue
            parts = [_roman_text(v, nib) for v in gs]
            if all(p is not None for p in parts):
                x = " ".join(parts)
                if x and all(c.isprintable() or c in "\t\n\r" for c in x) and x not in reads:
                    reads.append(x)
    return reads


def roman_dec(t):
    """The most English-looking reading, else None (a lenient parse of IVXLCDM prose is junk)."""
    r = sorted(roman_free(t), key=_texty, reverse=True)
    return r[0] if r else None


def roman_free(p):
    return [x for x in roman_reads(p) if _texty(x) >= 0.9][:3]


# Chuck Norris unary (CodinGame "Chuck Norris", dCode): the bit stream (7-bit ASCII classic, or 8-bit UTF-8 bytes =
# 4-bit hex nibbles run together) cut into runs; each run -> "0" (run of 1s) or "00" (run of 0s), a space, then the run
# length as that many "0"s, pairs space-separated. inner="hex": the stream carries the UTF-8 hex digits as text.
# Strict: only "0" and single spaces, even token count, every pair head "0"/"00", bit count a multiple of the width,
# clean printable text (a 7-bit reading must also stay ASCII); hex inner only for an even all-hex reading.
_CN_LINE = re.compile(r"0+(?: 0+)*")


def chuck_enc(s, bits=7, inner=None):
    data = _u(_u(s).hex()) if inner == "hex" else _u(s)
    st = "".join(format(b, f"0{bits}b") for b in data)
    return " ".join(("0" if r[0] == "1" else "00") + " " + "0" * len(r) for r in re.findall(r"0+|1+", st))


def chuck_reads(t):
    """[(tag, text)] readings of a Chuck Norris unary line (tag = "7", "8", "7-hex", "8-hex"), else []."""
    if not isinstance(t, str):
        return []
    t = t.strip()
    if len(t) > 262144 or not _CN_LINE.fullmatch(t):
        return []
    toks = t.split(" ")
    if len(toks) % 2 or any(h not in ("0", "00") for h in toks[0::2]):
        return []
    st = "".join(("1" if h == "0" else "0") * len(n) for h, n in zip(toks[0::2], toks[1::2]))
    out = []
    for w in (7, 8):
        if len(st) % w:
            continue
        b = bytes(int(st[i:i + w], 2) for i in range(0, len(st), w))
        x = _txt(b)
        if not x or any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in x):
            continue
        out.append((str(w), x))
        if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", x):
            y = _txt(bytes.fromhex(x))
            if y and not any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in y):
                out.append((f"{w}-hex", y))
    return out


def chuck_dec(t, bits=None, inner=None):
    """The text under Chuck Norris unary, else None. bits/inner pin one reading; unpinned: the hex inner first, then
    the most text-like of the 7-/8-bit readings."""
    r = chuck_reads(t)
    if bits or inner:
        tag = f"{bits or ''}{'-hex' if inner == 'hex' else ''}"
        r = [(g, x) for g, x in r if (g == tag if bits else g.endswith("-hex"))]
    if not r:
        return None
    hexed = [x for g, x in r if g.endswith("-hex")]
    return hexed[0] if hexed else max((x for _g, x in r), key=_texty)


def chuck_free(p):
    """Mastery free line: every English-looking reading, hex inner first."""
    r = chuck_reads(p)
    return [x for _g, x in sorted(r, key=lambda gx: not gx[0].endswith("-hex")) if _texty(x) >= 0.9]


# a-p letter hex: each UTF-8 hex digit as one of the 16 letters a..p (nibble = ord - 97), the middle layer of D17
# (Bacon-26 groups -> a-p -> hex). Standalone (blob, byte pairs split by whitespace or , ; | : / _ -, upper case) or as
# the output of a letter carrier (Bacon-26/24, Polybius, tap code, A1Z26). Strict: only [a-p] in one case, even-length
# tokens, clean UTF-8 that reads more English than the letters themselves (an English a-p word line stays None).
# Carriers that merge two a-p letters (Polybius / Bacon-24: I/J = 8/9, tap code: C/K = 2/10) re-split each merged
# letter by (text-likeness, bigram) fit, greedy left to right (a merged digit pair like 8/9 stays a guess).
_AP = "abcdefghijklmnop"
_AP_TOK = re.compile(r"[a-p]+")


def aphex_enc(s, sep="", upper=False):
    a = "".join(_AP[int(c, 16)] for c in _u(s).hex())
    a = a.upper() if upper else a
    return sep.join(a[i:i + 2] for i in range(0, len(a), 2)) if sep else a


def _ap_text(a):
    try:
        out = bytes(16 * (ord(a[i]) - 97) + ord(a[i + 1]) - 97 for i in range(0, len(a), 2)).decode("utf-8")
    except ValueError:
        return None
    if not out or any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in out):
        return None
    return out


def _ap_fit(x):
    """Merged-letter tie-break: text-likeness, then bigrams less letter/digit seams ("Master2") and stray brackets."""
    from lib.decode import _bigram
    depth = stray = 0
    for c in x:
        if c in "()":
            depth += 1 if c == "(" else -1
            if depth < 0:
                depth, stray = 0, stray + 1
    seams = len(re.findall(r"[A-Za-z][0-9]|[0-9][A-Za-z]", x)) + stray + depth
    return _texty(x), _bigram(x) - 0.5 * seams


def aphex_dec(t, merge=""):
    """The text under a-p letter hex, else None. merge "ij" / "ck": the carrier wrote both letters as the first."""
    if not isinstance(t, str):
        return None
    t = t.strip().strip("\"'[]()")
    if not t or len(t) > 40000 or not (t.islower() or t.isupper()):
        return None
    toks = [x for x in _B4_SEP.split(t.lower()) if x]
    if not toks or any(not _AP_TOK.fullmatch(x) or len(x) % 2 for x in toks):
        return None
    a = "".join(toks)
    from lib.decode import _bigram
    out = _ap_text(a)
    if merge and merge[0] in a:
        a = list(a)
        for k in [k for k, c in enumerate(a) if c == merge[0]] * 2:   # 2nd pass: re-pick with both sides set
            best, prev = None, a[k]
            for c in merge:
                a[k] = c
                x = _ap_text("".join(a))
                if x is not None and (best is None or _ap_fit(x) > best[0]):
                    best = (_ap_fit(x), c, x)
            if best is None:
                a[k] = prev   # neither fits yet: a later merged letter may complete the UTF-8 sequence
                continue
            a[k], out = best[1], best[2]
        out = _ap_text("".join(a))
    if out is None or _texty(out) < 0.85 or _bigram(out) <= _bigram(t):
        return None
    return out


def _ap_a1z26(t, sep):
    t = t.strip()
    if not re.fullmatch(r"\d{1,2}(?:[%s\s/|]+\d{1,2})*" % re.escape(sep), t) or len(t) > 60000:
        return None
    x = a1z26_dec(t, sep)
    return None if re.search(r"\d", x) else x


# carrier name -> (encoder of the a-p letters, decoder back to letters, the letter pair it merges)
_AP_CARRIERS = {
    "bacon26": (lambda a: bacon_enc(a, 26), lambda t: next(filter(None, (bacon_dec(t, 26, tr) for tr in _BACON_TR)), None),
                ""),
    "bacon24": (lambda a: bacon_enc(a, 24), lambda t: next(filter(None, (bacon_dec(t, 24, tr) for tr in _BACON_TR)), None),
                "ij"),
    "polybius": (lambda a: polybius_enc(a, sep=" ", word=" / "), lambda t: polybius_dec(t), "ij"),
    "tapcode": (lambda a: tap_enc(a), lambda t: tap_dec(t), "ck"),
    "a1z26": (lambda a: a1z26_enc(a), lambda t: _ap_a1z26(t, "-"), ""),
    "a1z26-comma": (lambda a: a1z26_enc(a, sep=","), lambda t: _ap_a1z26(t, ","), ""),
}


def aphex_over_enc(s, carrier, sep=" "):
    """a-p letter hex (byte pairs split by `sep`, "" = one run) under a letter carrier."""
    return _AP_CARRIERS[carrier][0](aphex_enc(s, sep))


def aphex_reads(t):
    """Every clean [carrier ->] a-p letter hex reading of t, the most English first (Bacon-24 groups also read as
    Bacon-26 a-o letters: the wrong alphabet shifts j..p and loses on bigrams)."""
    if not isinstance(t, str):
        return []
    outs = []
    for name, (_e, dec, merge) in _AP_CARRIERS.items():
        try:
            a = dec(t)
            x = aphex_dec(a, merge) if a else None
        except (ValueError, IndexError, KeyError, TypeError):
            x = None
        if x and x not in outs:
            outs.append(x)
    return sorted(outs, key=_ap_fit, reverse=True)


def aphex_over_dec(t, carrier=None):
    """The text under [carrier ->] a-p letter hex, else None; carrier None = the best read of any carrier."""
    if carrier is None:
        r = aphex_reads(t)
        return r[0] if r else None
    if not isinstance(t, str):
        return None
    _e, dec, merge = _AP_CARRIERS[carrier]
    try:
        a = dec(t)
        return aphex_dec(a, merge) if a else None
    except (ValueError, IndexError, KeyError, TypeError):
        return None


def aphex_free(p):
    """Mastery free line: a-p letter hex standalone, else its letter-carrier readings (best first)."""
    try:
        x = aphex_dec(p)
        return [x] if x else aphex_reads(p)[:2]
    except (ValueError, IndexError, KeyError, TypeError):
        return []


# Seven-segment display hex: each UTF-8 hex digit as the segments lit to show it (0-9 A b C d E F; segments a..g, a =
# top, clockwise, g = middle). Tokens: masks in hex (0x3f / 3F / \x3f), decimal or binary ([01]{7,8}), or segment-letter
# sets ("abcdef", any order / case); separated by whitespace or , ; | : / _ -, or one run (hex pairs / 7- or 8-bit
# binary). Bit layouts: gfedcba (bit i = segment i, TM1637 / HT16K33), abcdefg (a = bit 6, MAX7219 / luma), the 8-bit
# abcdefg+dp (a = MSB, dp = LSB); the dp bit ignored, active-low (common anode) inverted masks. Alternate glyphs: 7 with
# f, 9 without d, lowercase a / c / e (luma). Strict: every token maps, clean UTF-8 that reads as text.
_S7 = dict(x.split(":") for x in "abcdef:0 bc:1 abdeg:2 abcdg:3 bcfg:4 acdfg:5 acdefg:6 abc:7 abcdefg:8 abcdfg:9 "
           "abcefg:a cdefg:b adef:c bcdeg:d adefg:e aefg:f abcf:7 abcfg:9 abcdeg:a deg:c abdefg:e".split())
_S7_SEG = {v: k for k, v in reversed(list(_S7.items()))}   # nibble -> standard segment string (first listed wins)
_S7_LAYOUTS = (("gfedcba", 0), ("abcdefg", 0), ("abcdefg", 1), ("gfedcba", 1))   # (bit order, dp-at-LSB shift)


def _s7_mask(seg, order="gfedcba", shift=0, inv=False):
    m = sum(1 << (i if order == "gfedcba" else 6 - i) for i, c in enumerate("abcdefg") if c in seg)
    return (m ^ 0x7f if inv else m) << shift


def _s7_maps():
    """[(mask -> nibble, the bits that are segments)] per layout x polarity (the remaining bit is the decimal point)."""
    out = []
    for order, shift in _S7_LAYOUTS:
        for inv in (False, True):
            out.append(({_s7_mask(seg, order, shift, inv): n for seg, n in _S7.items()}, 0x7f << shift))
    return out


_S7_MAPS = _s7_maps()


def seg7_enc(s, fmt="hex", order="gfedcba", shift=0, inv=False, sep=" "):
    """fmt: hex (0x3f) / hexraw (3f) / dec / bin / letters."""
    out = []
    for c in _u(s).hex():
        seg = _S7_SEG[c]
        m = _s7_mask(seg, order, shift, inv)
        out.append({"hex": "0x%02x" % m, "hexraw": "%02x" % m, "dec": str(m), "bin": format(m, "08b" if shift else "07b"),
                    "letters": seg}[fmt])
    return sep.join(out)


def _s7_text(nibs):
    if not nibs or len(nibs) % 2:
        return None
    try:
        out = bytes.fromhex("".join(nibs)).decode("utf-8")
    except ValueError:
        return None
    if not out or any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in out) or _texty(out) < 0.85:
        return None
    return out


def seg7_reads(t):
    """Every clean seven-segment hex reading of t (the most text-like first), else []."""
    if not isinstance(t, str) or len(t) > 60000:
        return []
    t = t.strip().strip("\"'[](){}")
    if not t:
        return []
    reads = []
    letters = [x for x in _B4_SEP.split(t.lower()) if x]
    if len(letters) >= 2 and all(re.fullmatch(r"[a-g]{1,7}", x) and len(set(x)) == len(x) for x in letters):
        x = _s7_text([_S7.get("".join(sorted(x))) for x in letters] if all(
            "".join(sorted(x)) in _S7 for x in letters) else [])
        if x:
            reads.append(x)
    u = re.sub(r"(?i)(?:0x|\\x)(?=[0-9a-f])|0b(?=[01]{7,8}(?![0-9a-f]))", " ", t)
    toks = [x for x in _B4_SEP.split(u) if x]
    if not toks:
        return reads
    vals = []   # candidate integer token lists
    if len(toks) == 1 and len(toks[0]) >= 8:
        r = toks[0]
        if re.fullmatch(r"[0-9a-fA-F]+", r) and not len(r) % 2:
            vals.append([int(r[i:i + 2], 16) for i in range(0, len(r), 2)])
        for b in (7, 8):
            if re.fullmatch(r"[01]+", r) and not len(r) % b:
                vals.append([int(r[i:i + b], 2) for i in range(0, len(r), b)])
    elif len(toks) >= 2:
        if all(re.fullmatch(r"[0-9a-fA-F]{1,2}", x) for x in toks):
            vals.append([int(x, 16) for x in toks])
        if all(re.fullmatch(r"\d{1,3}", x) for x in toks):
            vals.append([int(x) for x in toks])
        if all(re.fullmatch(r"[01]{7,8}", x) for x in toks):
            vals.append([int(x, 2) for x in toks])
    for vs in vals:
        for m, segs in _S7_MAPS:
            nibs = []
            for v in vs:
                n = m.get(v & segs) if v < 0x100 else None   # either state of the decimal point
                if n is None:
                    break
                nibs.append(n)
            else:
                x = _s7_text(nibs)
                if x and x not in reads:
                    reads.append(x)
    return sorted(reads, key=_texty, reverse=True)


def seg7_dec(t):
    try:
        r = seg7_reads(t)
    except (ValueError, IndexError, KeyError, TypeError):
        return None
    return r[0] if r else None


def seg7_free(p):
    try:
        return seg7_reads(p)[:2]
    except (ValueError, IndexError, KeyError, TypeError):
        return []


# Crib-aligned token hex: any <=16-token alphabet (words, emoji, glyphs, colours) standing for the 16 UTF-8 hex digits
# under an UNKNOWN token->nibble map, recovered from the fixed sentence: "Nice work decoding this warmup! ..." = 4e 69 63
# 65 20 ... Tokenize (whitespace / , ; | split; else per glyph = code point + its combining marks / VS / ZWJ / skin tone;
# else per bare code point; else CamelCase words), require <= 16 distinct tokens, an even count, a consistent bijection
# over at least the first 31 crib bytes (extended over the whole template prefix while it stays consistent), fill up to
# 4 unmapped tokens by trying the free digits, fromhex, and accept only text that starts with the crib and ends in a
# slug. Plain nibble order first, then low-nibble-first. Not covered: 2 tokens a byte with <= 256 tokens (the crib holds
# too few distinct bytes to pin the map).
_CT_PREFIX = _CRIB
_CT_HEAD = 31   # len("Nice work decoding this warmup!")
_CT_END = re.compile(r"[a-z]+(?:-[a-z]+)+-\d{2,}\s*$")
_CT_DEMO = "🍎🍌🍒🍇🍉🍓🍑🍍🥝🥥🥑🍆🥕🌽🥦🍄"


def crib_tok_enc(s, alphabet=_CT_DEMO, sep="", swap=False):
    h = _u(s).hex()
    if swap:
        h = "".join(h[i + 1] + h[i] for i in range(0, len(h), 2))
    toks = alphabet.split() if " " in alphabet else list(alphabet)
    return sep.join(toks[int(c, 16)] for c in h)


def _ct_glyphs(t):
    out = []
    for c in t:
        o = ord(c)
        join = out and (unicodedata.combining(c) or 0xFE00 <= o <= 0xFE0F or 0x1F3FB <= o <= 0x1F3FF
                        or o == 0xE0020 or 0xE0061 <= o <= 0xE007F or out[-1].endswith("‍") or o == 0x200D)
        if join:
            out[-1] += c
        else:
            out.append(c)
    return out


def _ct_tokenizations(t):
    """Candidate token lists of t, the most specific first (deduplicated)."""
    outs = []
    if re.search(r"[\s,;|]", t):
        outs.append([x for x in re.split(r"[\s,;|]+", t) if x])
    flat = re.sub(r"[\s,;|]+", "", t)
    outs.append(_ct_glyphs(flat))
    outs.append(list(flat))
    if re.fullmatch(r"(?:[A-Z][a-z]+)+", flat):
        outs.append(re.findall(r"[A-Z][a-z]+", flat))
    seen, res = set(), []
    for o in outs:
        k = tuple(o)
        if o and k not in seen:
            seen.add(k)
            res.append(o)
    return res


def _ct_text(toks, m, swap):
    h = "".join(m[x] for x in toks)
    if swap:
        h = "".join(h[i + 1] + h[i] for i in range(0, len(h), 2))
    try:
        out = bytes.fromhex(h).decode("utf-8")
    except ValueError:
        return None
    if not out.startswith(_CT_PREFIX[:_CT_HEAD]) or not _CT_END.search(out):
        return None
    if any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in out):
        return None
    return out.strip()


def _ct_solve_toks(toks):
    """(token->nibble map, swap, text) for one token list, else None."""
    alpha = set(toks)
    if len(toks) % 2 or len(toks) < 2 * _CT_HEAD + 4 or not 2 <= len(alpha) <= 16:
        return None
    for swap in (False, True):
        ch = _CT_PREFIX.encode().hex()
        if swap:
            ch = "".join(ch[i + 1] + ch[i] for i in range(0, len(ch), 2))
        fwd, back, n = {}, {}, 0
        for tok, d in zip(toks, ch):
            if fwd.get(tok, d) != d or back.get(d, tok) != tok:
                break
            fwd[tok], back[d] = d, tok
            n += 1
        if n < 2 * _CT_HEAD:
            continue
        unk = sorted(alpha - set(fwd), key=toks.index)
        free = [d for d in "0123456789abcdef" if d not in back]
        if len(unk) > 4 or len(unk) > len(free):
            continue
        hits = []
        for perm in itertools.permutations(free, len(unk)):
            m = dict(fwd, **dict(zip(unk, perm)))
            x = _ct_text(toks, m, swap)
            if x is not None:
                hits.append((m, swap, x))
                if len(hits) > 1:
                    break
        if len(hits) == 1:   # an unknown token the slug can't pin to one digit = ambiguous -> no answer
            return hits[0]
    return None


def crib_tok_solve(blob):
    """(name, sentence, enc) for the warmups sentence under crib-aligned token hex, else None; enc re-encodes with the
    recovered alphabet and the blob's own separator."""
    if not isinstance(blob, str):
        return None
    t = blob.strip()
    if not t or len(t) > 60000:
        return None
    for toks in _ct_tokenizations(t):
        try:
            got = _ct_solve_toks(toks)
        except (ValueError, KeyError, TypeError):
            got = None
        if got:
            m, swap, x = got
            inv = {d: k for k, d in m.items()}
            sep = next((s for s in (" ", ", ", ",", "|", ";", "\n") if t == s.join(toks)), "")

            def enc(s, inv=inv, sep=sep, swap=swap):
                h = _u(s).hex()
                if swap:
                    h = "".join(h[i + 1] + h[i] for i in range(0, len(h), 2))
                return sep.join(inv[c] if c in inv else "?" for c in h)
            return f"crib-token-hex{'-swap' if swap else ''}", x, enc
    return None


def crib_tok_dec(t):
    """The sentence under crib-aligned token hex (any <=16-token alphabet), else None."""
    r = crib_tok_solve(t)
    return r[1] if r else None


# DNA bases: each UTF-8 byte as 4 bases, 2 bits a base MSB first (2 bases = one hex nibble), A=00 C=01 G=10 T=11 by
# default; the decoder tries all 24 base->bit orders (ACGT first) and keeps a slug-bearing read, else the most English
# one. Run together or split by whitespace , ; | / : _ -, either case, RNA U for T. Second form: codons (3 bases) via
# the 64-symbol table a-z A-Z 0-9 space . in AAA..TTT order (any of the 24 orders), or the standard genetic code
# amino-acid letters (decode only: 20 letters, no B J O U X Z; reads lowercase). Both codon forms pass non-base
# characters through. Strict: only bases, length a multiple of 4 (3), clean printable text that reads more English
# than the bases (a gene-looking run or an English line stays None).
_DNA_ORDERS = ["ACGT"] + ["".join(p) for p in itertools.permutations("ACGT") if "".join(p) != "ACGT"]
_DNA_SEP = re.compile(r"[\s,;|/:_\-]+")
_CODON64 = string.ascii_lowercase + string.ascii_uppercase + "1234567890 ."
_AMINO = "KNKNTTTTRSRSIIMIQHQHPPPPRRRRLLLLEDEDAAAAGGGGVVVV*Y*YSSSS*CWCLFLF"   # AAA..TTT in ACGT order


def dna_enc(s, order="ACGT", sep="", lower=False, rna=False):
    """4 bases a byte, 2 bits a base MSB first; sep splits the bytes."""
    o = order.replace("T", "U") if rna else order
    o = o.lower() if lower else o
    return sep.join("".join(o[b >> k & 3] for k in (6, 4, 2, 0)) for b in _u(s))


def _dna_bases(t, n):
    """t's bases upper-cased (U -> T) with separators removed, else None (non-base char / length not a multiple of n)."""
    if not isinstance(t, str):
        return None
    t = t.strip().strip("\"'[]()")
    if not t or len(t) > 80000 or not (t.islower() or t.isupper()):
        return None
    a = _DNA_SEP.sub("", t).upper()
    if "U" in a:
        if "T" in a:
            return None
        a = a.replace("U", "T")
    if not a or len(a) % n or a.strip("ACGT"):
        return None
    return a


def _dna_text(a, order):
    v = {c: i for i, c in enumerate(order)}
    try:
        out = bytes(v[a[i]] << 6 | v[a[i + 1]] << 4 | v[a[i + 2]] << 2 | v[a[i + 3]]
                    for i in range(0, len(a), 4)).decode("utf-8")
    except ValueError:
        return None
    if any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in out):
        return None
    return out


def dna_reads(t, order=None):
    """[(order, text)] of every clean base->bit order reading of t: slug-bearing first, then by (text-likeness,
    bigram), ACGT winning ties. order: only that order."""
    a = _dna_bases(t, 4)
    if a is None:
        return []
    from lib.decode import _bigram
    outs = []
    for o in [order] if order else _DNA_ORDERS:
        x = _dna_text(a, o)
        if x and _texty(x) >= 0.85 and len(set(x)) >= 4:
            outs.append((o, x))
    outs.sort(key=lambda r: (bool(SLUG.search(r[1])), _texty(r[1]), _bigram(r[1])), reverse=True)
    return [r for r in outs if _bigram(r[1]) > _bigram(t)]


def dna_dec(t, order=None):
    """The text under 2-bit DNA bases, else None; order None = the best of all 24 orders."""
    r = dna_reads(t, order)
    return r[0][1] if r else None


def _codon_tab(order, table):
    return {"".join(order[i // 16] + order[i // 4 % 4] + order[i % 4]): table[i] for i in range(64)}


def codon_enc(s, order="ACGT", sep="", amino=False):
    """Codon letters (64-symbol table, or the first codon of each amino acid); non-table chars pass through."""
    inv = {}
    for k, c in _codon_tab(order, _AMINO if amino else _CODON64).items():
        inv.setdefault(c.lower() if amino else c, k)
    if amino:
        s = s.lower()
    out, run = [], []
    for c in s:
        if c in inv:
            run.append(inv[c])
        elif amino and c.isalpha():
            raise ValueError("no codon for %r" % c)
        else:
            out += [sep.join(run), c]
            run = []
    return "".join(out + [sep.join(run)])


_CODON_RUN = re.compile(r"[ACGTU]+", re.I)
_CODON_GAP = re.compile(r"(?<=[ACGTU]{3}) (?=[ACGTU]{3})", re.I)


def codon_dec(t, order=None, amino=False):
    """The text under codon letters, else None. order None = the best of all 24 orders (64-symbol table only)."""
    if not isinstance(t, str) or len(t) > 80000:
        return None
    t = t.strip()
    if len(_CODON_RUN.findall(t)) >= 4 and all(len(r) == 3 for r in _CODON_RUN.findall(t)):
        t = re.sub(r" / |  ", " ", _CODON_GAP.sub("", t))   # one codon per token: single spaces split codons only
    runs = [(m.start(), m.end(), _dna_bases(m.group(), 3)) for m in _CODON_RUN.finditer(t)]
    if not runs or any(a is None for _s, _e, a in runs) or sum(e - s for s, e, _a in runs) < 0.6 * len(t):
        return None
    if re.search(r"[A-Za-z]", _CODON_RUN.sub("", t)):
        return None   # stray non-base letters: not a codon line
    from lib.decode import _bigram
    best = None
    for o in ["ACGT"] if amino else [order] if order else _DNA_ORDERS:
        tab = _codon_tab(o, _AMINO if amino else _CODON64)
        pos, out = 0, []
        for s, e, a in runs:
            out += [t[pos:s], "".join(tab[a[i:i + 3]] for i in range(0, len(a), 3))]
            pos = e
        x = "".join(out) + t[pos:]
        x = x.lower() if amino else x
        if amino and "*" in x.rstrip("*"):
            continue
        fit = (bool(SLUG.search(x)), _texty(x), _ap_fit(x)[1])
        if best is None or fit > best[0]:
            best = (fit, x)
    if best is None or best[0][1] < 0.85 or best[0][2] <= max(_bigram(t), -6.5):
        return None   # a codon line must read as English (letter/digit seams count against it)
    return best[1].rstrip("*") if amino else best[1]


def dna_free(p):
    """Mastery free line: 2-bit DNA bytes (best two orders), else the codon-table and amino-acid readings."""
    try:
        r = [x for _o, x in dna_reads(p)[:2]]
        return r or [x for x in (codon_dec(p), codon_dec(p, amino=True)) if x]
    except (ValueError, IndexError, KeyError, TypeError):
        return []


# uuencode / xxencode:lines of <length char><4 chars per 3 bytes>, 45 bytes a line, optional `begin NNN name` ... `end`
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


# Hex carried by digit-capable grids: 6x6 Polybius / 6x6 tap code (A-Z then 0-9, row then column, 1-based -- secretpy
# Polybius with a 36-char alphabet) and Braille (⠼ number sign). The decoders answer only when the grid's output is
# nothing but hex pairs whose bytes are printable text.
_POLY6 = "abcdefghijklmnopqrstuvwxyz0123456789"


def _hex_text(h):
    h = re.sub(r"[\s,:]", "", h or "")
    if len(h) < 4 or len(h) % 2 or not re.fullmatch(r"[0-9a-fA-F]+", h):
        return None
    try:
        s = bytes.fromhex(h).decode("utf-8")
    except ValueError:
        return None
    return s if all(c.isprintable() or c in "\t\r\n" for c in s) else None


def polybius6_enc(s, sep=" ", inner="hex"):
    src = s.encode().hex() if inner == "hex" else s.lower()
    return sep.join(f"{i // 6 + 1}{i % 6 + 1}" for i in (_POLY6.find(c) for c in src) if i >= 0)


def polybius6_dec(t):
    t = t.strip()
    if len(t) > 50000 or not re.fullmatch(r"[1-6][1-6\s,/|.-]*", t):
        return None
    d = re.sub(r"\D", "", t)
    if len(d) < 8 or len(d) % 2:
        return None
    return _hex_text("".join(_POLY6[(int(d[i]) - 1) * 6 + int(d[i + 1]) - 1] for i in range(0, len(d), 2)))


def tap6_enc(s, tap=".", gap=" ", letter="  "):
    return letter.join(f"{tap * (i // 6 + 1)}{gap}{tap * (i % 6 + 1)}" for i in (_POLY6.find(c) for c in
                                                                                 s.encode().hex()))


def tap6_dec(t):
    t = t.strip()
    if len(t) > 100000 or not re.fullmatch(r"[.*•·xX][.*•·xX\s/|]*", t) \
            or len(set(re.sub(r"[\s/|]", "", t))) != 1:
        return None
    runs = [len(r) for r in re.findall(r"[.*•·xX]+", t)]
    if len(runs) < 8 or len(runs) % 2 or max(runs) > 6:
        return None
    return _hex_text("".join(_POLY6[(runs[i] - 1) * 6 + runs[i + 1] - 1] for i in range(0, len(runs), 2)))


_BR_AJ = "⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚"


def braille_pyb_enc(s):
    """pybraille 1.0 convertText: ⠠ per capital, ⠼ re-sent before every digit run, NO letter sign -- so a-f after a
    digit read back as digits 1-6 (lossy for lowercase hex: ⠼⠙⠑ = 45 or 4e)."""
    out, num = [], False
    for c in s:
        if c.isupper():
            out.append("⠠")
            c = c.lower()
        if c in "1234567890":
            out.append("" if num else "⠼")
            num = True
            out.append(_BR_DIG[c])
            continue
        num = num and c in ".,-/$"
        out.append(_BR_LET.get(c) or (" " if c == " " else _BR_PUN.get(c, c)))
    return "".join(out)


def braille_hex_reads(t, k=3):
    """Hex under Grade 1 Braille -> up to k texts (best first). ⠰ / ⠠ present = unambiguous (letter sign or capital
    ends the number run); else pybraille style: inside a ⠼ run the a-f cells are digits up to an unknown switch point,
    resolved by a beam over printable bytes scored by English letter bigrams."""
    from lib.decode import _BIGRAM
    t = t.strip()
    if not t or len(t) > 50000 or not all("\u2800" <= c <= "\u283f" or c in " \t\r\n" for c in t) \
            or not any(c in t for c in _BR_AJ):
        return []
    strict = "⠰" in t or "⠠" in t
    if not strict:
        from lib import slug
        vocab = slug.english() | slug.vocab() | _KBD_KNOWN
    hyps = {("", False): 0.0}   # (hex so far, run switched to letters) -> score
    num = False
    for c in t:
        if c in " \t\r\n\u2800⠠⠰":
            num = False
            continue
        if c == "⠼":
            num = True
            hyps = {(h, False): s for (h, _l), s in hyps.items()}
            continue
        i = _BR_AJ.find(c)
        if i < 0:
            return []
        nxt = {}
        for (h, let), s in hyps.items():
            opts = []
            if num and not let:
                opts.append(("1234567890"[i], False))
            if i < 6 and (not num or not strict):
                opts.append(("abcdef"[i], num))
            for ch, l2 in opts:
                h2, s2 = h + ch, s
                if len(h2) % 2 == 0:
                    b = int(h2[-2:], 16)
                    if not (32 <= b < 127 or b in (9, 10, 13)):
                        continue
                    p = chr(b).lower()
                    q = chr(int(h2[-4:-2], 16)).lower() if len(h2) >= 4 else " "
                    s2 += (math.log(_BIGRAM.get(q + p, 0.00005)) if q.isalpha() and p.isalpha()
                           else 0.0 if p.isalpha() or p == " " else -6.0 if p.isdigit() and q.isalpha()
                           else -2.0 if p.isdigit() or p in ".,!?:;'-\"" else -6.0)
                    if not strict and q.isalpha() and not p.isalpha():   # word ended: English / slug word?
                        w = re.search(r"[a-z]+$", bytes.fromhex(h2[:-2]).decode("latin-1").lower()).group()
                        s2 += 6.0 if w in vocab else -3.0 if len(w) > 2 else 0.0
                if nxt.get((h2, l2), -1e18) < s2:
                    nxt[(h2, l2)] = s2
        hyps = dict(sorted(nxt.items(), key=lambda kv: -kv[1])[:64])
        if not hyps:
            return []
    out = []
    for (h, _l), _s in sorted(hyps.items(), key=lambda kv: -kv[1]):
        x = _hex_text(h)
        if x and x not in out:
            out.append(x)
    return out[:k]


def braille_hex_dec(t):
    r = braille_hex_reads(t, 1)
    return r[0] if r else None


def braille_ascii_hex_dec(t):
    return _hex_text(safe(braille_ascii_dec, t) or "")


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


# Regional-indicator "emoji letters" as the Discord / emoji-text generators write them: REGIONAL INDICATOR SYMBOL
# LETTER A-Z (U+1F1E6-1F1FF, capitals only: case lost) each followed by a space or zero-width char so neighbours don't
# fuse into country flags, words split by a wider gap ("   " or " / "); digits as keycaps (4 U+FE0F U+20E3, also #/*),
# !/?/-/+ as heavy emoji marks, or Discord shortcodes (:regional_indicator_a: :four: :hash:). Read back lowercase,
# re-cased to the warmup sentence when it is (a piece of) it.
_KEYCAP_WORDS = "zero one two three four five six seven eight nine".split()
_RI_SHORT = ({f"regional_indicator_{c}": chr(0x1F1E6 + i) for i, c in enumerate(string.ascii_lowercase)}
             | {w: str(i) for i, w in enumerate(_KEYCAP_WORDS)} | {f"keycap_{i}": str(i) for i in range(10)}
             | {"hash": "#", "asterisk": "*", "keycap_ten": "10", "exclamation": "!", "heavy_exclamation_mark": "!",
                "grey_exclamation": "!", "white_exclamation_mark": "!", "question": "?", "grey_question": "?",
                "white_question_mark": "?", "heavy_minus_sign": "-", "heavy_plus_sign": "+", "bangbang": "!!",
                "interrobang": "!?"})
_RI_EMOJI = {"❗": "!", "❕": "!", "❓": "?", "❔": "?", "➖": "-", "➕": "+", "🔟": "10", "‼": "!!", "⁉": "!?"}
_RI_ZW = "\u200b\u200c\u200d\u2060\ufeff"


def regional_enc(s, gap="", word=" ", keycap=False, short=False):
    """Plain -> regional-indicator letters (upper-cased), `gap` after every symbol inside a word, `word` between words;
    keycap: digits/#/* as keycap emoji; short: Discord :regional_indicator_x: / :four: / :hash: shortcodes."""
    def sym(c):
        if c.isascii() and c.isalpha():
            return f":regional_indicator_{c.lower()}:" if short else chr(0x1F1E6 + ord(c.upper()) - 65)
        if c.isdigit() and c.isascii() and (keycap or short):
            return f":{_KEYCAP_WORDS[int(c)]}:" if short else c + "\ufe0f\u20e3"
        return c
    return word.join(gap.join(sym(c) for c in w) for w in s.split(" "))


def regional_dec(t):
    """Regional-indicator text (any writer above) -> lowercase / sentence-cased text, else None (needs >= 2 RI letters
    making >= 80% of the letters, nothing else non-ASCII)."""
    if not isinstance(t, str) or not t.strip() or len(t) > 50000:
        return None
    t = re.sub(r":([a-z0-9_]+):", lambda m: _RI_SHORT.get(m[1], m[0]), t.strip())
    t = re.sub("([0-9#*])\ufe0f?\u20e3", r"\1", t)
    t = "".join(_RI_EMOJI.get(c, c) for c in t if c not in "\ufe0e\ufe0f")
    ri = sum(0x1F1E6 <= ord(c) <= 0x1F1FF for c in t)
    if ri < 2 or ri < 0.8 * sum(c.isalpha() or 0x1F1E6 <= ord(c) <= 0x1F1FF for c in t):
        return None
    if any(not c.isascii() and not 0x1F1E6 <= ord(c) <= 0x1F1FF and c not in _RI_ZW for c in t):
        return None
    parts = re.split(f"([\\s{_RI_ZW}]+)", t)
    toks, gaps = parts[0::2], parts[1::2]
    if len(toks) >= 3 and all(len(x) <= 2 for x in toks) and sum(len(x) == 1 for x in toks) >= 0.7 * len(toks):
        # letter-spaced: a 1-space / zero-width gap joins, a wider gap (or " / ") is a word break, a newline stays
        unit = max(set(gaps), key=gaps.count)   # the in-word gap: the commonest one
        uws = sum(c.isspace() for c in unit)
        out = [toks[0]]
        for g, x in zip(gaps, toks[1:]):
            ws = [c for c in g if c.isspace()]
            if x == "/" and ws:
                x = " "
            elif out[-1] != " ":
                out.append("" if g == unit else "\n" if "\n" in ws else " " if len(ws) > uws else "")
            out.append(x)
        s = "".join(out)
        s = re.sub(r" +", " ", s)
    else:
        s = "".join(c for c in t if c not in _RI_ZW)
    s = "".join(chr(ord(c) - 0x1F1E6 + 97) if 0x1F1E6 <= ord(c) <= 0x1F1FF else c.lower() for c in s)
    return _recase(s) or s


def regional_free(p):
    """Speculative free-line regional-indicator decoder (keeps the line's leading whitespace)."""
    b = regional_dec(p) if isinstance(p, str) else None
    return [p[:len(p) - len(p.lstrip())] + b] if b else []


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


# ------------------------------------- double columnar / Myszkowski, keyed by title / prompt words (speculative)
# tgt:columnar covers one pass under one key. Here: Myszkowski (repeated key letters = one column group, read row by
# row left to right -- secretpy MyszkowskiTransposition), the same key twice, two different keys (either order, any mix
# of plain columnar and Myszkowski), keys = every word / number of the title + prompt, each hint run together, and the
# case-sensitive (ASCII) ranking when it differs; numbers are also scytale widths. Keyless extra: scytale w twice.
# A pass is a permutation (cipher[j] = plain[P[j]]); two passes compose, the crib is checked on the composed inverse
# before any string is built. Accepts only crib + slug (trailing 'x' pad allowed); 0.5 s cap. Never raises.
def mysz_order(key):
    """Myszkowski column groups: [[cols], ...] in key-rank order, columns of a repeated letter grouped left to right.
    A str key ranks lower-cased letters; an int n = n singleton groups (scytale)."""
    if isinstance(key, int):
        return [[c] for c in range(key)]
    k = key.lower()
    return [[i for i, ch in enumerate(k) if ch == u] for u in sorted(set(k))]


def _dcol_perm(L, groups, m):
    """[plain index] in cipher order for one pass over L chars, m columns, read group by group (row-major inside)."""
    out = []
    for g in groups:
        if len(g) == 1:
            out.extend(range(g[0], L, m))
        else:
            for r in range(0, L, m):
                out.extend(r + c for c in g if r + c < L)
    return out


def mysz_enc(s, key, pad=None):
    groups = mysz_order(key)
    m = sum(len(g) for g in groups)
    if pad and len(s) % m:
        s += pad * (m - len(s) % m)
    return "".join(s[i] for i in _dcol_perm(len(s), groups, m))


def mysz_dec(t, key):
    groups = mysz_order(key)
    out = [""] * len(t)
    for j, i in enumerate(_dcol_perm(len(t), groups, sum(len(g) for g in groups))):
        out[i] = t[j]
    return "".join(out)


def _dcol_pass_enc(s, kind, key, pad=None):
    return mysz_enc(s, key, pad) if kind == "mysz" else col_enc(s, key, pad)


def dcol_enc(s, passes, pad=None):
    """Apply [(kind, key), ...] in order (kind 'col' = stable-rank columnar, 'mysz' = Myszkowski)."""
    for kind, key in passes:
        s = _dcol_pass_enc(s, kind, key, pad)
    return s


def _dcol_keys(hints):
    """[(label, key)] from the hints: words / numbers, each hint run together (and its letters only), case-sensitive
    ranking where it differs; numbers also as an int width. Keys of 2-24 chars, at most 96."""
    out, seen = [], set()

    def add(label, key):
        kk = key
        if (isinstance(kk, int) and 2 <= kk <= 24) or (isinstance(kk, str) and 2 <= len(kk) <= 24):
            sig = (type(kk).__name__, kk if isinstance(kk, int) else kk.lower())
            if sig not in seen:
                seen.add(sig)
                out.append((label, kk))
    for h in hints or ():
        h = unicodedata.normalize("NFKD", str(h)).encode("ascii", "ignore").decode()
        words = re.findall(r"[A-Za-z0-9]+", h)
        for w in words + ["".join(words), "".join(re.findall(r"[A-Za-z]", h))]:
            if not w:
                continue
            add(w.lower(), w)
            if w.isdigit():
                add(w, int(w))
    return out[:96]


def _dcol_variants(L, keys):
    """[(name, kind, key, inv)] distinct single passes: columnar + Myszkowski (+ ASCII-case ranking) of every key;
    inv[i] = cipher index of plain i."""
    out, seen = [], set()
    for label, key in keys:
        forms = [("col", key), ("mysz", key)]
        if isinstance(key, str) and key != key.lower() and key != key.upper():
            forms.append(("col", tuple(sorted(range(len(key)), key=lambda i: (key[i], i)))))
        for kind, k in forms:
            m = len(k) if not isinstance(k, int) else k
            if m >= L:
                continue
            groups = mysz_order(k) if kind == "mysz" else [[c] for c in col_order(k)]
            P = _dcol_perm(L, groups, m)
            sig = tuple(P)
            if sig in seen:
                continue
            seen.add(sig)
            inv = [0] * L
            for j, i in enumerate(P):
                inv[i] = j
            out.append((f"{kind}:{label}" + ("-ascii" if isinstance(k, tuple) else ""), kind, k, inv))
    return out


def dcol_solve(blob, hints=(), budget=0.5):
    """(name, sentence, enc) for the warmups sentence under Myszkowski / double columnar keyed by title / prompt words
    (or scytale w twice), else None."""
    import time
    try:
        t0 = time.monotonic()
        t = _t(blob).strip("\r\n")
        L = len(t)
        if L <= len(_CRIB) + 4 or L > 600 or "\n" in t:
            return None
        rest = collections.Counter(t)
        rest.subtract(_CRIB)
        if min(rest.values()) < 0 or any(not (ch.islower() or ch.isdigit() or ch == "-") for ch, v in rest.items() if v):
            return None
        cr, n = _CRIB, len(_CRIB)
        V = _dcol_variants(L, _dcol_keys(hints))
        W = _dcol_variants(L, [(str(w), w) for w in range(2, min(21, L))])

        def accept(passes):   # passes in encoding order: plain[i] = t[inv_last[...inv_first[i]]]
            idx = passes[0][3]
            for v in passes[1:]:
                idx = [v[3][i] for i in idx]
            c = "".join(t[i] for i in idx)
            tail = c[n:].rstrip("x")
            if not (c.startswith(cr) and SLUG.fullmatch(tail)):
                return None
            ps = [(v[1], v[2]) for v in passes]
            pad = "x" if n + len(tail) < L else None
            c = c[:n + len(tail)]
            if pad and dcol_enc(c, ps, pad) != t:   # the padded encoding must reproduce the blob exactly
                return None
            name = "+".join(v[0] for v in passes) + ("-x" if pad else "")
            return ("dcol:" if len(passes) > 1 else "") + name, c, (lambda ps, pd: lambda s: dcol_enc(s, ps, pd))(ps, pad)

        for v in V:   # one Myszkowski pass (one columnar pass under a hint word = _hint_cands' columnar:<k>)
            if v[1] == "mysz" and all(t[v[3][i]] == cr[i] for i in range(n)):
                got = accept([v])
                if got:
                    return got
        pairs = [(v1, v2) for v1 in V for v2 in V] + [(w, w) for w in W]
        for k, (v1, v2) in enumerate(pairs):
            i1, i2 = v1[3], v2[3]
            if all(t[i2[i1[i]]] == cr[i] for i in range(n)):
                got = accept([v1, v2])
                if got:
                    return got
            if not k & 255 and time.monotonic() - t0 > budget:
                return None
    except Exception:  # noqa: BLE001
        pass
    return None


def dcol_crib_dec(t, hints=()):
    """Decoder view of dcol_solve (the sentence or None)."""
    got = dcol_solve(t, hints)
    return got[1] if got else None


# Keyless transposition sweep (D18 opened the family with rail 3). Every family is a permutation P of positions
# (cipher[j] = plain[P[j]]) built per length L, tried as P and as its inverse, each bare and composed with reversal
# (before or after). Spaces are ciphertext; only CR/LF are stripped.
#   reverse | rail n x offset | redefence (rail rows read in a key order) | columnar 2-5 every order, scytale 2-20
#   (and reversed) | route (spiral cw/ccw from each corner, row/column snake; grid filled by rows or by columns)
#   | skip k (every k-th char, gcd(k, L) = 1) | riffle (in/out perfect shuffle x1-6) | word order / per-word reversal
#   | diagonal zigzag route (JPEG scan, first step right or down, each corner). A box padded to w x h with 'x' / ' ' /
#   '_' / NUL reads the same permutations on the full grid: the pad is stripped from the reading's ends. CyberChef
#   'Caesar Box Cipher' (spaces deleted, then scytale-h) is read against the crib with its spaces removed.
def _tp_word_perm(L, s, each):
    """Positions of a text with spaces at the same places as `s`: words in reverse order (each=False) or each word
    reversed in place (each=True)."""
    spans = [m.span() for m in re.finditer(r"[^ ]+| +", s)]
    if each:
        return [i for a, b in spans for i in range(b - 1, a - 1, -1)]
    return [i for a, b in reversed(spans) for i in range(a, b)]


def _tp_route(L, C, path, corner, colfill):
    """Route read of an R x C grid (filled by rows, or by columns when colfill: then C = rows) over positions < L."""
    R = -(-L // C)
    if colfill:
        R, C = C, -(-L // C)
    idx = (lambda r, c: c * R + r) if colfill else (lambda r, c: r * C + c)
    cells = []
    if path == "spiral":
        top, bot, lef, rig = 0, R - 1, 0, C - 1
        while top <= bot and lef <= rig:
            ring = ([(top, c) for c in range(lef, rig + 1)] + [(r, rig) for r in range(top + 1, bot + 1)]
                    + ([(bot, c) for c in range(rig - 1, lef - 1, -1)] if bot > top else [])
                    + ([(r, lef) for r in range(bot - 1, top, -1)] if rig > lef else []))
            cells += ring
            top, bot, lef, rig = top + 1, bot - 1, lef + 1, rig - 1
    elif path in ("diag", "diagdown"):   # JPEG zigzag over anti-diagonals: first step right (diag) or down
        flip = path == "diagdown"
        cells = sorted(((r, c) for r in range(R) for c in range(C)),
                       key=lambda rc: (rc[0] + rc[1], rc[0] if (rc[0] + rc[1]) % 2 != flip else -rc[0]))
    elif path == "colsnake":
        cells = [(r if c % 2 == 0 else R - 1 - r, c) for c in range(C) for r in range(R)]
    else:   # rowsnake
        cells = [(r, c if r % 2 == 0 else C - 1 - c) for r in range(R) for c in range(C)]
    if corner & 1:
        cells = [(r, C - 1 - c) for r, c in cells]
    if corner & 2:
        cells = [(R - 1 - r, c) for r, c in cells]
    p = [idx(r, c) for r, c in cells]
    return [i for i in p if i < L]


def _tp_spiral_ccw(L, C, corner, colfill):
    """Counter-clockwise spiral = the clockwise one with the grid transposed (any shape): walk an C x R spiral and map
    each cell back."""
    R = -(-L // C)
    if colfill:
        R, C = C, -(-L // C)
    idx = (lambda r, c: c * R + r) if colfill else (lambda r, c: r * C + c)
    top, bot, lef, rig, cells = 0, C - 1, 0, R - 1, []
    while top <= bot and lef <= rig:
        cells += ([(top, c) for c in range(lef, rig + 1)] + [(r, rig) for r in range(top + 1, bot + 1)]
                  + ([(bot, c) for c in range(rig - 1, lef - 1, -1)] if bot > top else [])
                  + ([(r, lef) for r in range(bot - 1, top, -1)] if rig > lef else []))
        top, bot, lef, rig = top + 1, bot - 1, lef + 1, rig - 1
    cells = [(c, r) for r, c in cells]
    if corner & 1:
        cells = [(r, C - 1 - c) for r, c in cells]
    if corner & 2:
        cells = [(R - 1 - r, c) for r, c in cells]
    return [i for i in (idx(r, c) for r, c in cells) if i < L]


def _tp_riffle(L, inn):
    h = (L + (0 if inn else 1)) // 2
    a, b = (range(h, L), range(h)) if inn else (range(h), range(h, L))
    a, b = list(a), list(b)
    return [x for pair in itertools.zip_longest(a, b) for x in pair if x is not None]


_TP_RAIL_REDEF = 5   # redefence: every rail read order for 3-5 rails (offset 0 and every offset)


def _tp_families(L):
    """[(tier, name, P)] for length L, most plausible first; P = None entries skipped. Tier: 0 reverse / rail offset 0
    / scytale / word order, 1 rail offsets / columnar / route, 2 redefence / skip / riffle."""
    out = [(0, "reverse", list(range(L))[::-1])]
    rows_cache = {}
    for n, o in rail_keys(L):
        rows = rows_cache[(n, o)] = _rail_rows(L, n, o)
        out.append((0 if o == 0 else 1, f"rail{n}" + (f"-off{o}" if o else ""),
                    sorted(range(L), key=rows.__getitem__)))
    for m in range(2, min(20, L - 1) + 1):
        out.append((0, f"scytale{m}", [i for c in range(m) for i in range(c, L, m)]))
        out.append((1, f"scytale{m}-revcols", [i for c in reversed(range(m)) for i in range(c, L, m)]))
    for m in range(3, min(_COL_PERM_MAX, L - 1) + 1):
        for order in itertools.permutations(range(m)):
            if order != tuple(range(m)) and order != tuple(range(m))[::-1]:
                out.append((1, "columnar-" + "".join(map(str, order)), [i for c in order for i in range(c, L, m)]))
    for C in range(2, min(20, L - 1) + 1):
        for colfill in (False, True):
            f = "c" if colfill else "r"
            for corner in range(4):
                out.append((1, f"route-spiral-cw{corner}-{f}{C}", _tp_route(L, C, "spiral", corner, colfill)))
                out.append((1, f"route-spiral-ccw{corner}-{f}{C}", _tp_spiral_ccw(L, C, corner, colfill)))
            for corner in range(4):
                out.append((1, f"route-colsnake{corner}-{f}{C}", _tp_route(L, C, "colsnake", corner, colfill)))
                out.append((1, f"route-rowsnake{corner}-{f}{C}", _tp_route(L, C, "rowsnake", corner, colfill)))
    for n in range(3, min(_TP_RAIL_REDEF, L - 1) + 1):
        for o in range(2 * n - 2):
            rows = rows_cache.get((n, o)) or _rail_rows(L, n, o)
            for order in itertools.permutations(range(n)):
                if order != tuple(range(n)):
                    rank = {r: k for k, r in enumerate(order)}
                    out.append((2, f"redefence{n}-" + "".join(map(str, order)) + (f"-off{o}" if o else ""),
                                sorted(range(L), key=lambda i: (rank[rows[i]], i))))
    for k in range(2, L - 1):
        if math.gcd(k, L) == 1:
            out.append((2, f"skip{k}", [(i * k) % L for i in range(L)]))
    for inn in (False, True):
        p = list(range(L))
        step = _tp_riffle(L, inn)
        for times in range(1, 7):
            p = [p[i] for i in step]
            out.append((2, f"riffle-{'in' if inn else 'out'}{times}", p))
    for C in range(2, min(20, L - 1) + 1):   # diagonal zigzag route (JPEG scan) of the w x h box, from each corner
        for colfill in (False, True):
            for corner in range(4):
                for path in ("diag", "diagdown"):
                    out.append((2, f"route-{path}{corner}-{'c' if colfill else 'r'}{C}",
                                _tp_route(L, C, path, corner, colfill)))
    return [(tier, name, P) for tier, name, P in out if P and len(P) == L]


@functools.lru_cache(maxsize=64)
def _tp_keys(L):
    """[(tier, name, P, Q)] deduplicated by P (Q = inverse of P), cached per length."""
    seen, out = set(), []
    for tier, name, P in _tp_families(L):
        k = tuple(P)
        if k in seen or k == tuple(range(L)):
            continue
        seen.add(k)
        Q = [0] * L
        for j, i in enumerate(P):
            Q[i] = j
        out.append((tier, name, P, Q))
    return out


def _tp_apply(s, P):
    return "".join(map(s.__getitem__, P))


def _tp_variants(t, P, Q):
    """(suffix, plain) for every composition: the family's encoder (decode with Q) and its inverse (decode with P),
    each bare, with the ciphertext reversed (+rev-out) and after reversing the plaintext (+rev-in)."""
    tr = t[::-1]
    for sfx, X in (("", Q), ("-inv", P)):
        c = _tp_apply(t, X)
        yield sfx, c
        yield sfx + "+rev-out", _tp_apply(tr, X)
        yield sfx + "+rev-in", c[::-1]


def _tp_word_keys(t):
    return [(0, "wordorder", _tp_word_perm(len(t), t, False)), (0, "wordrev", _tp_word_perm(len(t), t, True))]


def _tp_encoder(name, sfx):
    """Encoder for a solved (family name, composition) on any text: rebuild the family's permutation for len(s)."""
    def enc(s):
        L = len(s)
        if "+rev-in" in sfx:
            s = s[::-1]
        if name in ("wordorder", "wordrev"):   # involutions on the text's own spacing: -inv is the same map
            P = _tp_word_perm(L, s, name == "wordrev")
        else:
            P = next((P for _t, n, P in _tp_families(L) if n == name), None)
            if P is None:
                return None
            if "-inv" in sfx:
                Q = [0] * L
                for j, i in enumerate(P):
                    Q[i] = j
                P = Q
        c = _tp_apply(s, P)
        return c[::-1] if "+rev-out" in sfx else c
    return enc


_TP_HEAD = "Nice work"
_TP_TAIL = re.compile(r" ([a-z]+(?:-[a-z]+)+-\d{2,})$")
_TP_PAD = " x_\x00"   # route / box pad chars: never end the sentence (it starts 'N', ends in slug digits)
_CRIB_NS = _CRIB.replace(" ", "")
_TP_TAIL_NS = re.compile(r"[a-z]+(?:-[a-z]+)+-\d{2,}$")
_CRIB_NS_POS = [i for i, ch in enumerate(_CRIB) if ch != " "]


def _tp_dim(name, L):
    """Grid width a padded box of family `name` fills to (scytale m / columnar key length / route C), else L."""
    if name.startswith("columnar-"):
        return len(name.split("-")[1])
    m = re.search(r"(?:^scytale|-[rc])(\d+)(?:-revcols)?$", name)
    return int(m.group(1)) if m else L


def _tp_box_encoder(name, sfx, c, nosp, L):
    """Encoder for a reading c (pad kept) of a length-L ciphertext: drop spaces (Caesar box), pad like c did up to a
    full box, then the family's permutation."""
    base = _tp_encoder(name, sfx)
    lead = c[:len(c) - len(c.lstrip(_TP_PAD))] if not c.startswith(_TP_HEAD.replace(" ", "")) else ""
    trail = c[len(c.rstrip(_TP_PAD)):]

    def enc(s):
        if nosp:
            s = s.replace(" ", "")
        if lead or trail:
            k = _tp_dim(name, L)
            need = (-len(s)) % k if k < L else L - len(s)
            s = s + trail[:1] * need if trail else lead[:1] * need + s
        return base(s)
    return enc


_TP_RIFFLE_ALIAS = {"rail2": "riffle-out1", "rail2-off1": "riffle-in1"}   # rail2(-off1) inverse = one out/in-shuffle


def transposition_solve(blob, budget=0.5):
    """(name, sentence, enc) when the blob is the warmups sentence under any keyless transposition family above (each
    also inverted and composed with reversal), else None. Cheap reject first: the character multiset must be the
    crib's plus slug characters [a-z0-9-] and pad chars (or, if the template drifted, hold 'Nice work' plus a slug's
    hyphens and digits). Accepts only a reading that STARTS 'Nice work' and ends in a ' words-words-NN' slug once box
    padding (_TP_PAD) is stripped from its ends (rotated rail offsets show the slug too, mid-text); the full crib wins
    over the loose head. A space-free blob (CyberChef Caesar Box deletes spaces) is matched against the space-free
    crib and answered with the template's spaces restored. Never raises; <= `budget` seconds."""
    import time
    try:
        t0 = time.monotonic()
        t = _t(blob).strip("\r\n")
        L = len(t)
        if L < len(_TP_HEAD) + 8 or L > 400 or "\n" in t:
            return None
        nosp = " " not in t
        crib, head = (_CRIB_NS, _TP_HEAD.replace(" ", "")) if nosp else (_CRIB, _TP_HEAD)
        cnt = collections.Counter(t)
        rest = cnt.copy()
        rest.subtract(crib)
        strict = min(rest.values()) >= 0 and all(
            ch.islower() or ch.isdigit() or ch in "-" + _TP_PAD for ch, v in rest.items() if v)
        if not strict:
            h = cnt.copy()
            h.subtract(head)
            if min(h.values()) < 0 or cnt["-"] < 2 or sum(cnt[d] for d in string.digits) < 2:
                return None
        loose = None
        keys = ([] if nosp else [(tier, name, P, None) for tier, name, P in _tp_word_keys(t)]) + _tp_keys(L)
        for tier, name, P, Q in keys:
            if time.monotonic() - t0 > budget:
                break
            if Q is None:
                Q = P   # word permutations are involutions
            for sfx, c in _tp_variants(t, P, Q):
                cc = c.strip(_TP_PAD)
                if not cc.startswith(head):
                    continue
                m = (_TP_TAIL_NS if nosp else _TP_TAIL).search(cc)
                if not m:
                    continue
                nm, sx = name, sfx
                if sx.startswith("-inv") and nm in _TP_RIFFLE_ALIAS:   # same P, deck name: undo = one un-shuffle
                    nm, sx = _TP_RIFFLE_ALIAS[nm], sx[4:]
                if cc.startswith(crib) and SLUG.fullmatch(cc[len(crib):]):
                    return nm + sx, _CRIB + cc[len(crib):], _tp_box_encoder(nm, sx, c, nosp, L)
                loose = loose or (nm + sx, cc, _tp_box_encoder(nm, sx, c, nosp, L))
        return loose
    except Exception:  # noqa: BLE001
        return None


def _ns_piece(c):
    """A space-free reading c (Caesar box line) as the sentence piece it spells, template spaces restored, else None:
    the whole crib + slug, a crib substring (>= 6 chars), or a crib tail + the start of a slug."""
    if c.startswith(_CRIB_NS) and SLUG.fullmatch(c[len(_CRIB_NS):]):
        return _CRIB + c[len(_CRIB_NS):]
    i = _CRIB_NS.find(c) if len(c) >= 6 else -1
    if i >= 0:
        return _CRIB[_CRIB_NS_POS[i]:_CRIB_NS_POS[i + len(c) - 1] + 1]
    m = _SLUG_TAIL.search(c)
    hd, tail = c[:m.start()], m.group()
    if len(hd) >= 3 and _CRIB_NS.endswith(hd) and tail[:1].isalpha() and _SLUG_PIECE.fullmatch(tail):
        return _CRIB[_CRIB_NS_POS[len(_CRIB_NS) - len(hd)]:] + tail
    return None


def transposition_dec(t):
    r = transposition_solve(t)
    return r[1] if r else None


def transposition_free(p, k=3, budget=0.1):
    """Mastery fragment mode: every family's key restarts on each line, so each line (CR/LF stripped, spaces kept;
    a leading space may be ciphertext: raw and stripped both tried) is read under every permutation and kept only when
    it is a contiguous piece of the sentence or a crib tail + slug start (_crib_piece). Best k by (crib chars
    confirmed, family plausibility, bigram). Never raises."""
    import time
    try:
        from lib.decode import _bigram
        t0 = time.monotonic()
        lead = p[:len(p) - len(p.lstrip())]
        hits, seen = {}, set()
        for pre, t in ((lead, p[len(lead):].rstrip("\r\n")), ("", p.rstrip("\r\n")))[:2 if lead else 1]:
            L = len(t)
            if L < 3 or L > 200:
                continue
            seen.add(t)
            nosp = " " not in t and L >= 6
            keys = [(tier, name, P, P) for tier, name, P in _tp_word_keys(t)] + _tp_keys(L)
            for tier, name, P, Q in keys:
                if time.monotonic() - t0 > budget:
                    break
                for sfx, c in _tp_variants(t, P, Q):
                    if c in seen:
                        continue
                    seen.add(c)
                    n = _crib_piece(c)
                    if not n:   # padded box: strip one pad char's run from the ends (longest reading first)
                        cs = next((x for x in sorted({c.strip(ch) for ch in _TP_PAD} - {c}, key=len, reverse=True)
                                   if _crib_piece(x)), None)
                        if cs:
                            n, c = _crib_piece(cs), cs
                    if not n and nosp:
                        c = _ns_piece(c) or c
                        n = _crib_piece(c) if " " in c else 0
                    if n:
                        rank = tier + (1 if sfx else 0)
                        hits.setdefault(pre + c, (n, -rank, _bigram(c)))
        return [c for c, _s in sorted(hits.items(), key=lambda kv: kv[1], reverse=True)[:k]]
    except Exception:  # noqa: BLE001
        return []


def register_transposition(day=None, name="transposition", dec=None):
    """One call to put a (new day's) transposition into lib.decode's joint free-line search: `dec(line)` (the day's
    exact keyed decoder, key restarting per line) is tried first, then the keyless sweep. day=None = speculative."""
    from lib import decode

    def cands(p):
        out = []
        if dec is not None:
            got = safe(dec, p.rstrip("\r\n"))
            if got:
                out.append(got)
        return out + [c for c in transposition_free(p) if c not in out]
    decode.register_free(name, day, cands)
    return cands


# ------------------------------------------------ word-level transposition (speculative, coverage atlas target)
# Whole space-split tokens permuted (rail n x offset / scytale / columnar / route / skip / riffle on the 17 token
# positions, or any keyed shuffle), and/or each word's letters rail-fenced / scytale'd / reversed on their own (the
# slug token anagrammed with the same map, or left intact). Crib-gated: after undoing the inner map every token is a
# crib word (16) or the slug, so the plaintext is the crib in template order; the family is only named for the encoder.
_WTP_WORDS = _CRIB.split()


def _wtp_inner():
    """[(name, enc, dec)] per-word letter maps, identity first."""
    out = [("", lambda w: w, lambda w: w), ("rev", lambda w: w[::-1], lambda w: w[::-1])]
    for n in range(2, 9):
        for o in range(2 * n - 2):
            sfx = f"-off{o}" if o else ""
            out.append((f"rail{n}{sfx}", (lambda n, o: lambda w: rail_enc(w, n, o))(n, o),
                        (lambda n, o: lambda w: rail_dec(w, n, o))(n, o)))
    for m in range(2, 9):
        out.append((f"scytale{m}", (lambda m: lambda w: col_enc(w, m))(m), (lambda m: lambda w: col_dec(w, m))(m)))
    out += [(f"{nm}-inv", d, e) for nm, e, d in out[2:]]
    out += [(f"{nm}+rev", (lambda e: lambda w: e(w)[::-1])(e), (lambda d: lambda w: d(w[::-1]))(d))
            for nm, e, d in out[2:]]
    return out


_WTP_INNER = _wtp_inner()


def _wtp_slug(tok, dec):
    """The slug a token spells: the inner map undone, else the token left intact."""
    got = dec(tok)
    return got if SLUG.fullmatch(got) else tok if SLUG.fullmatch(tok) else None


def _wtp_order(cipher, plain):
    """(name, P) of a positional family with cipher[j] == plain[P[j]] (each family and its inverse, bare and composed
    with reversal), else ("shuffle", explicit P)."""
    L = len(plain)
    if cipher == plain:
        return "", list(range(L))
    if cipher == plain[::-1]:
        return "reverse", list(range(L))[::-1]
    for _tier, name, P, Q in _tp_keys(L):
        for sfx, X in (("", P), ("-inv", Q)):
            if all(cipher[j] == plain[X[j]] for j in range(L)):
                return name + sfx, list(X)
            if all(cipher[L - 1 - j] == plain[X[j]] for j in range(L)):
                return name + sfx + "+rev-out", [X[L - 1 - j] for j in range(L)]
    used, P = set(), []
    for c in cipher:
        i = next(i for i, w in enumerate(plain) if w == c and i not in used)
        used.add(i)
        P.append(i)
    return "shuffle", P


def wordtp_solve(blob):
    """(name, sentence, enc) when the blob is the warmups sentence with its words transposed and/or each word's letters
    transposed (see above), else None. Identity (plain text) and the cases transposition_solve already reads exactly
    (pure word order / per-word reversal keep working there) are still answered. Never raises."""
    try:
        t = _t(blob).strip()
        toks = t.split()
        n = len(_WTP_WORDS) + 1
        if len(toks) != n or "\n" in t:
            return None
        want = collections.Counter(_WTP_WORDS)
        for iname, ienc, idec in _WTP_INNER:
            got, slug = [], None
            for tok in toks:
                w = idec(tok)
                if want[w] and got.count(w) < want[w]:
                    got.append(w)
                elif slug is None and _wtp_slug(tok, idec):
                    slug = _wtp_slug(tok, idec)
                    got.append(slug)
                else:
                    break
            if len(got) != n or slug is None:
                continue
            plain = _WTP_WORDS + [slug]
            keep = slug in toks and ienc(slug) != slug   # slug left intact while the words were anagrammed
            ctoks = [ienc(w) for w in _WTP_WORDS] + [slug if keep else ienc(slug)]
            oname, P = _wtp_order(toks, ctoks)
            name = "word-" + "+".join(x for x in (oname, iname and f"each-{iname}", keep and "slug-intact") if x)

            def enc(s, P=P, oname=oname, ienc=ienc, keep=keep):
                ws = s.split(" ")
                if len(ws) != len(P):
                    if oname == "shuffle":
                        return None
                    Pn = next((X for _t2, nm, X in _tp_families(len(ws)) if nm == oname.split("-inv")[0]
                               .split("+rev-out")[0]), None) if oname != "reverse" else list(range(len(ws)))[::-1]
                    if Pn is None or "-inv" in oname or "+rev-out" in oname:
                        return None
                    P2 = Pn
                else:
                    P2 = P
                cs = [w if keep and SLUG.fullmatch(w) else ienc(w) for w in ws]
                return " ".join(cs[i] for i in P2)
            return name, " ".join(plain), enc
        return None
    except Exception:  # noqa: BLE001
        return None


def _wtp_words(s, fam, n):
    """Whole words of s rail-fenced (n rails) or scytale'd (n columns), single-space joined."""
    ws = s.split(" ")
    L = len(ws)
    P = (sorted(range(L), key=_rail_rows(L, n).__getitem__) if fam == "rail"
         else [i for c in range(n) for i in range(c, L, n)])
    return " ".join(ws[i] for i in P)


def wordtp_dec(t):
    r = wordtp_solve(t)
    return r[1] if r else None


def wordtp_free(p, k=3):
    """Mastery fragment: the line's tokens (>= 2) are a contiguous run of the sentence's words (the run may end in the
    slug or a slug piece) once one inner per-word map is undone, in any order -> that run in template order. Only a
    reading that differs from the line is returned. Never raises."""
    try:
        lead = p[:len(p) - len(p.lstrip())]
        toks = p.strip().split()
        if not 2 <= len(toks) <= len(_WTP_WORDS) + 1:
            return []
        out = []
        for _iname, _ienc, idec in _WTP_INNER:
            ws = [idec(x) for x in toks]
            plain_set = collections.Counter(ws)
            for i in range(len(_WTP_WORDS) + 2 - len(toks)):
                win = _WTP_WORDS[i:i + len(toks)]
                if len(win) == len(toks):
                    if collections.Counter(win) == plain_set:
                        out.append(" ".join(win))
                    continue
                rest = plain_set.copy()
                rest.subtract(win)
                left = [w for w, v in rest.items() if v > 0 for _ in range(v)]
                if min(rest.values()) >= 0 and len(left) == 1:   # crib tail + one slug(-piece) token
                    raw = toks[ws.index(left[0])]
                    sl = left[0] if _SLUG_PIECE.fullmatch(left[0]) else raw if _SLUG_PIECE.fullmatch(raw) else None
                    if sl and re.search(r"[a-z]", sl):
                        out.append(" ".join(win + [sl]))
            if len(out) >= k:
                break
        seen = []
        for o in out:
            if o != p.strip() and lead + o not in seen:
                seen.append(lead + o)
        return seen[:k]
    except Exception:  # noqa: BLE001
        return []


# Skip cipher / decimation (dCode 'Skip Cipher'): read every k-th character from start s, wrapping mod L; a position
# already read moves on to the next unread one, so gcd(k, L) = d > 1 still reads all L: lap r (of d laps, L/d reads
# each) starts at s + r, i.e. cipher[r*m + q] = plain[(s + r + q*k) % L] with m = L/d. gcd 1 = one lap. The
# transposition sweep above covers s = 0, gcd 1 only.
def skip_order(L, k, s=0):
    """Plain positions in cipher order for the skip cipher (k, start s) on a length-L text (dCode next-unread rule)."""
    out, used, pos = [], bytearray(L), s % L if L else 0
    for _ in range(L):
        while used[pos]:
            pos = (pos + 1) % L
        out.append(pos)
        used[pos] = 1
        pos = (pos + k) % L
    return out


def skip_enc(s, k, start=0):
    return "".join(s[i] for i in skip_order(len(s), k, start))


def skip_dec(t, k, start=0):
    out = [""] * len(t)
    for c, i in zip(t, skip_order(len(t), k, start)):
        out[i] = c
    return "".join(out)


def _skip_idx(L, k, s):
    """j -> cipher index holding plain[j] (closed form of skip_order's inverse), or None when k % L == 0."""
    d = math.gcd(k, L)
    m = L // d
    if m < 2:
        return None
    kinv = pow(k // d, -1, m)

    def idx(j):
        r = (j - s) % d
        return r * m + ((j - s - r) // d) * kinv % m
    return idx


_SKIP_HEAD = len(_TP_HEAD)


def _skip_reads(t, kmax=None):
    """(name, reading) for every (k, s) skip whose reading of t starts 'Nice work' (enc direction: plain = skip_dec;
    -inv: plain = skip_enc(t)), the 9-char head checked before the rest is built."""
    L = len(t)
    head = _TP_HEAD
    for k in range(1, min(kmax or L, L)):
        d = math.gcd(k, L)
        m = L // d
        if m < 2:
            continue
        kinv = pow(k // d, -1, m)
        for s in range(L):
            if k == 1 and s == 0:
                continue
            # decode: plain[j] = t[idx(j)]
            if all(t[(((j - s) % d) * m + ((j - s - (j - s) % d) // d) * kinv % m)] == head[j] for j in range(_SKIP_HEAD)):
                yield f"skip{k}-s{s}", skip_dec(t, k, s)
            # inverse direction: plain[j] = t[order[j]], order[r*m + q] = (s + r + q*k) % L
            if all(t[(s + j // m + (j % m) * k) % L] == head[j] for j in range(_SKIP_HEAD)):
                yield f"skip{k}-s{s}-inv", skip_enc(t, k, s)


def skip_solve(blob, budget=0.5):
    """(name, sentence, enc) when the blob is the warmups sentence under a skip cipher (any k, any start, coprime or
    not; also the inverse direction), else None. Gated on the crib's character multiset (+ slug chars [a-z0-9-]);
    accepts a reading that is crib + slug (strict) or 'Nice work' ... ' words-words-NN' (loose). ~L^2 cheap head
    checks (L ~ 110: ~24k). Never raises."""
    import time
    try:
        t0 = time.monotonic()
        t = _t(blob).strip("\r\n")
        L = len(t)
        if L < len(_TP_HEAD) + 8 or L > 400 or "\n" in t:
            return None
        cnt = collections.Counter(t)
        rest = cnt.copy()
        rest.subtract(_CRIB)
        if not (min(rest.values()) >= 0 and all(ch.islower() or ch.isdigit() or ch == "-"
                                                for ch, v in rest.items() if v)):
            h = cnt.copy()
            h.subtract(_TP_HEAD)
            if min(h.values()) < 0 or cnt["-"] < 2 or sum(cnt[x] for x in string.digits) < 2:
                return None
        loose = None
        for name, c in _skip_reads(t):
            if time.monotonic() - t0 > budget:
                break
            k, s = (int(x) for x in re.match(r"skip(\d+)-s(\d+)", name).groups())
            enc = ((lambda k, s: lambda x: skip_dec(x, k, s))(k, s) if name.endswith("-inv")
                   else (lambda k, s: lambda x: skip_enc(x, k, s))(k, s))
            if c.startswith(_CRIB) and SLUG.fullmatch(c[len(_CRIB):]):
                return name, c, enc
            if not loose and _TP_TAIL.search(c):
                loose = (name, c, enc)
        return loose
    except Exception:  # noqa: BLE001
        return None


def skip_dec_any(t):
    r = skip_solve(t)
    return r[1] if r else None


def skip_free(p, k=3, budget=0.1):
    """Mastery fragment mode: a line under skip (k, start) with the key restarting per line; every k x start, both
    directions, kept only when the reading is a contiguous sentence piece (_crib_piece). Best k by (crib chars, bigram).
    Lines over 80 chars are left to skip_solve. Never raises."""
    import time
    try:
        from lib.decode import _bigram
        t0 = time.monotonic()
        t = p.rstrip("\r\n")
        L = len(t)
        if L < 4 or L > 80:
            return []
        hits, seen = {}, {t}
        for kk in range(1, L):
            if time.monotonic() - t0 > budget:
                break
            if L // math.gcd(kk, L) < 2:
                continue
            for s in range(L):
                if kk == 1 and s == 0:
                    continue
                for c in (skip_dec(t, kk, s), skip_enc(t, kk, s)):
                    if c in seen:
                        continue
                    seen.add(c)
                    n = _crib_piece(c)
                    if n:
                        hits[c] = (n, _bigram(c))
        return [c for c, _s in sorted(hits.items(), key=lambda kv: kv[1], reverse=True)[:k]]
    except Exception:  # noqa: BLE001
        return []


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


# DTMF (touch-tone) keypad: 16 symbols, each = one row tone (697/770/852/941 Hz) + one column tone (1209/1336/1477/
# 1633 Hz); `697+1209` -> 1. Text form = frequency pairs (either order, optional Hz, any separator) or the keypad chars
# themselves; inner layer = hex (16 symbols <-> 16 nibbles under three maps) or a digits-only codec (decimal/octal/...).
_DTMF_ROWS = (697, 770, 852, 941)
_DTMF_COLS = (1209, 1336, 1477, 1633)
_DTMF_PAD = ("123A", "456B", "789C", "*0#D")
_DTMF_FREQ = {_DTMF_PAD[r][c]: (_DTMF_ROWS[r], _DTMF_COLS[c]) for r in range(4) for c in range(4)}
_DTMF_SYM = {v: k for k, v in _DTMF_FREQ.items()}
# symbol string indexed by nibble: natural (0-9 A-D, *=E #=F), keypad row-major order, MT8870 decoder code (D=0, 0=10)
_DTMF_NIB = {"hex": "0123456789ABCD*#", "hex-keypad": "123A456B789C*0#D", "hex-mt8870": "D1234567890*#ABC"}


def dtmf_enc(s, inner="hex", keys=False, pair="+", sep=" ", word=" / ", hz=False, hi_first=False):
    """DTMF of inner(s): each symbol -> `lo+hi` tone pair (keys=True: the keypad char), `sep` between symbols, `word`
    between the inner's byte tokens (word="" runs everything together with `sep`)."""
    if inner in _DTMF_NIB:
        toks = ["".join(_DTMF_NIB[inner][int(c, 16)] for c in f"{b:02x}") for b in _u(s)]
    else:
        toks = _MORSE_INNER[inner](s).split(" ")

    def sym(c):
        if keys:
            return c
        lo, hi = _DTMF_FREQ[c]
        u = "Hz" if hz else ""
        return f"{hi}{u}{pair}{lo}{u}" if hi_first else f"{lo}{u}{pair}{hi}{u}"
    return (word or sep).join(sep.join(sym(c) for c in t) for t in toks)


_DTMF_FREQ_OK = re.compile(r"(?:\d{3,4}|[Hh][Zz]|[\s+&/,;|:\-x()\[\]])+")
_DTMF_KEYS_OK = re.compile(r"[0-9A-Da-d*#\s/,;|\-]+")


def _dtmf_items(t):
    """[(symbol, start, end)] of a strict DTMF line (every number a DTMF tone, consecutive row+column pairs; or bare
    keypad chars holding a * or #), else None."""
    if _DTMF_FREQ_OK.fullmatch(t):
        nums = list(re.finditer(r"\d+(?:\s*[Hh][Zz])?", t))
        if len(nums) < 8 or len(nums) % 2:
            return None
        out = []
        for a, b in zip(nums[::2], nums[1::2]):
            x, y = int(re.match(r"\d+", a.group()).group()), int(re.match(r"\d+", b.group()).group())
            c = _DTMF_SYM.get((x, y)) or _DTMF_SYM.get((y, x))
            if c is None:
                return None
            out.append((c, a.start(), b.end()))
        return out
    if _DTMF_KEYS_OK.fullmatch(t) and re.search(r"[*#]", t) and re.search(r"[0-9]", t):
        return [(m.group().upper(), m.start(), m.end()) for m in re.finditer(r"[0-9A-Da-d*#]", t)]
    return None


def _dtmf_groupings(t, items):
    """Symbol groupings: one flat run, and for each separator kind between symbols, the split at every other kind."""
    syms = [c for c, _s, _e in items]
    gaps = [t[a[2]:b[1]] for a, b in zip(items, items[1:])]
    out = [["".join(syms)]]
    kinds = sorted(set(gaps))
    if 2 <= len(kinds) <= 3:
        for base in kinds:
            groups, cur = [], syms[0]
            for g, c in zip(gaps, syms[1:]):
                if g == base:
                    cur += c
                else:
                    groups.append(cur)
                    cur = c
            out.append(groups + [cur])
    elif len(kinds) == 1 and kinds[0].strip(" \t") and len(syms) > 1:
        out.append(syms)
    return out


def dtmf_reads(t):
    """[(inner, text)] for a strict DTMF line (tone pairs or keypad chars), best first: hex under each nibble map,
    digits-only inner codecs (decimal/octal3/binary8). Text-like (>= 85%) readings only."""
    if not isinstance(t, str):
        return []
    t = t.strip()
    if not t or len(t) > 400000:
        return []
    items = _dtmf_items(t)
    if not items:
        return []
    reads = []
    for groups in _dtmf_groupings(t, items):
        flat = "".join(groups)
        if len(groups) == 1 or all(len(g) == 2 for g in groups):
            for name, nib in _DTMF_NIB.items():
                if len(flat) % 2 == 0:
                    s = _txt(bytes.fromhex("".join("%x" % nib.index(c) for c in flat)))
                    if s:
                        reads.append((name, s))
        if flat.isdigit():
            reads += [r for r in _morse_inner_reads(" ".join(groups)) if r[0] != "hex"]
    reads = [r for r in dict.fromkeys(reads) if _texty(r[1]) >= 0.85]
    try:
        from lib.decode import _bigram
    except Exception:  # noqa: BLE001
        def _bigram(_s):
            return 0.0
    return sorted(reads, key=lambda r: (round(_texty(r[1]), 2), _bigram(r[1]), r[0] == "hex"), reverse=True)


def dtmf_dec(t, inner=None):
    """The text under DTMF, else None. inner: accept only that reading (one CANDIDATES entry per shape)."""
    try:
        r = [x for x in dtmf_reads(t) if inner is None or x[0] == inner]
    except Exception:  # noqa: BLE001 - parse defensively
        return None
    return r[0][1] if r else None


def dtmf_free(p):
    """Speculative Mastery-line decoder: every inner reading of a strict DTMF line (the slug/template check picks)."""
    try:
        return [s for _n, s in dtmf_reads(p)]
    except Exception:  # noqa: BLE001
        return []


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


# Whitespace steganography. A blob of only ' ' / '\t' (optionally '\n'-separated) or a cover text whose lines end in
# space/tab runs: one symbol = one bit (space=0 tab=1 or swapped), MSB-first 8-bit bytes / 7-bit ASCII / 4-bit hex
# nibbles; or SNOW / stegsnow (uncompressed, no password): after the FIRST tab of the trailing whitespace, every run of
# n spaces (0-7) ended by a tab or by the end of the line is 3 bits, LSB first; a partial last byte and NUL padding
# drop. Strict: never strip() the line; >= 16 whitespace symbols, both space and tab present, printable text out.
def ws_bits_enc(s, zero=" ", one="\t", width=8, sep=""):
    b = _u(s)
    groups = [f"{c:08b}" for c in b] if width == 8 else [f"{int(c, 16):04b}" for c in b.hex()]
    return sep.join(g.replace("0", "\0").replace("1", one).replace("\0", zero) for g in groups)


def snow_enc(s, cover=""):
    bits = "".join(f"{c:08b}" for c in _u(s))
    bits += "0" * (-len(bits) % 3)
    runs = ["\t"] + [" " * (int(bits[i]) + 2 * int(bits[i + 1]) + 4 * int(bits[i + 2])) + "\t"
                     for i in range(0, len(bits), 3)]
    return cover + "".join(runs)


def _ws_trailing(t):
    """[trailing space/tab run of each line] (a pure-whitespace line counts whole)."""
    out = []
    for ln in t.split("\n"):
        ln = ln.rstrip("\r")
        out.append(ln[len(ln.rstrip(" \t")):])
    return out


def _ws_snow(runs):
    bits, started = [], False
    for r in runs:
        if not started:
            k = r.find("\t")
            if k < 0:
                continue
            started, r = True, r[k + 1:]
        if not r:
            continue
        for g in (r.split("\t")[:-1] if r.endswith("\t") else r.split("\t")):
            n = len(g)
            if n > 7 or g.strip(" "):
                return None
            bits += [n & 1, n >> 1 & 1, n >> 2 & 1]
    out = bytes(int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits) - 7, 8)).rstrip(b"\0")
    return out.decode("utf-8") if out else None


def _ws_bit_reads(sy, widths):
    out = []
    for one in ("\t", " "):
        bits = "".join("1" if c == one else "0" for c in sy)
        for w in widths:
            if len(bits) % w:
                continue
            vals = [int(bits[i:i + w], 2) for i in range(0, len(bits), w)]
            try:
                out.append(bytes(vals).decode("utf-8") if w > 4 else
                           bytes.fromhex("".join("%x" % v for v in vals)).decode("utf-8"))
            except ValueError:
                pass
    return out


def ws_cands(t, k=3):
    """Keyless readings of the whitespace payload in t (pure space/tab blob or cover text + trailing runs), most
    English first; [] for ordinary text (markdown two-space breaks, indentation). Never raises."""
    try:
        if not isinstance(t, str) or len(t) > 200000 or "\t" not in t or " " not in t:
            return []
        reads = []
        pure = not t.strip(" \t\r\n")
        runs = _ws_trailing(t) if not pure else [ln.rstrip("\r") for ln in t.split("\n")]
        sy = "".join(runs)
        if len(sy) < 16 or "\t" not in sy or " " not in sy:
            return []
        snow = safe(_ws_snow, runs)
        if snow:
            reads.append(snow)
        toks = [r for r in runs if r]
        lens = {len(r) for r in toks}
        widths = [min(lens)] if len(toks) > 1 and len(lens) == 1 and min(lens) in (4, 7, 8) else [8, 7, 4]
        reads += _ws_bit_reads(sy, widths)
        from lib.decode import _bigram
        good = []
        for x in reads:
            if (x and x not in good and _texty(x) >= 0.9 and any(c.isalpha() for c in x)
                    and not any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in x)):
                good.append(x)
        return sorted(good, key=_bigram, reverse=True)[:k]
    except Exception:  # noqa: BLE001 - malformed input reads as nothing
        return []


def ws_dec(t):
    """The best whitespace-stego reading of t, or None."""
    got = ws_cands(t, 1)
    return got[0] if got else None


# ------------------------------------------------- inner byte encodings: EBCDIC (cp037/cp500), UTF-16, UTF-32, UTF-7
# A byte layer (hex / base64 / base32 / binary / decimal / octal / %xx) whose bytes are NOT UTF-8: EBCDIC (`40` = space,
# letters c1-e9 / 81-a9, `!` = 5a cp037 / 4f cp500), UTF-16 (`00` every 2nd byte, maybe a ff fe / fe ff BOM), UTF-32,
# or UTF-7 text (`+ACE-` shift runs, RFC 2152 strict: set-O punctuation encoded, as glibc iconv). Readings must be
# printable ASCII (the warmups sentence is): a UTF-8 hex/base64 line never reads as EBCDIC/UTF-16 under that gate.
_BYTE_INNERS = ("cp037", "cp500", "utf-16le", "utf-16be", "utf-16", "utf-32le", "utf-32be")
_UTF7_DIRECT = set(string.ascii_letters + string.digits + "'(),-./:? \t\r\n")
_UTF7_B64 = set(string.ascii_letters + string.digits + "+/")


def utf7_enc(s, dash=False):
    """RFC 2152 UTF-7, set-O chars shifted (glibc iconv -t UTF-7); dash=True: every shift run closed with '-'."""
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c in _UTF7_DIRECT:
            out.append(c)
            i += 1
            continue
        if c == "+":
            out.append("+-")
            i += 1
            continue
        j = i
        while j < len(s) and s[j] not in _UTF7_DIRECT and s[j] != "+":
            j += 1
        out.append("+" + base64.b64encode(s[i:j].encode("utf-16-be")).decode().rstrip("="))
        if dash or (j < len(s) and (s[j] in _UTF7_B64 or s[j] == "-")):
            out.append("-")
        i = j
    return "".join(out)


def utf7_dec(t):
    """UTF-7 text -> text, None unless it holds a real shift run (`+<base64>`) and reads printable ASCII."""
    t = _t(t)
    if not isinstance(t, str) or not t.isascii() or not re.search(r"\+[A-Za-z0-9/][A-Za-z0-9+/]*", t):
        return None
    try:
        out = t.encode("ascii").decode("utf-7")
    except (UnicodeError, ValueError):
        return None
    return out if out != t and out.isascii() and all(c.isprintable() or c in "\t\r\n" for c in out) else None


def _bytes_reads(t):
    """[(layer, bytes)] for every byte layer the text strictly parses as (hex, base64, base32, binary8, decimal,
    octal3, %xx). Never raises."""
    if not isinstance(t, str):
        return []
    s = t.strip()
    if not s or len(s) > 400000:
        return []
    out = []
    flat = re.sub(r"\s+", "", s)
    h = re.sub(r"(?i)0x|\\x|[:,]", "", re.sub(r"\s+", "", s))
    if h and re.fullmatch(r"[0-9a-fA-F]+", h) and len(h) % 2 == 0:
        out.append(("hex", bytes.fromhex(h)))
    toks = _toks(s)
    if toks and all(re.fullmatch(r"[01]{8}", x) for x in toks):
        out.append(("binary8", bytes(int(x, 2) for x in toks)))
    elif re.fullmatch(r"(?:[01]{8})+", flat) and len(toks) == 1:
        out.append(("binary8", bytes(int(flat[i:i + 8], 2) for i in range(0, len(flat), 8))))
    if len(toks) > 1 and all(re.fullmatch(r"\d{1,3}", x) and int(x) < 256 for x in toks):
        out.append(("decimal", bytes(int(x) for x in toks)))
        if all(re.fullmatch(r"[0-7]{3}", x) for x in toks):
            out.append(("octal3", bytes(int(x, 8) for x in toks)))
    if "%" in s and re.fullmatch(r"(?:%[0-9a-fA-F]{2}|[^%\s])+", flat):
        out.append(("url%xx", urllib.parse.unquote_to_bytes(flat)))
    if re.fullmatch(r"[A-Z2-7]+=*", flat) and len(flat) % 8 in (0, 2, 4, 5, 7):
        try:
            out.append(("base32", base64.b32decode(flat.rstrip("=") + "=" * (-len(flat.rstrip("=")) % 8))))
        except (ValueError, TypeError):
            pass
    if re.fullmatch(r"[A-Za-z0-9+/\-_]+=*", flat) and len(flat.rstrip("=")) % 4 != 1:
        try:
            out.append(("base64", base64.b64decode(_b64pad(flat.rstrip("=").replace("-", "+").replace("_", "/")),
                                                    validate=True)))
        except (ValueError, TypeError):
            pass
    return out


def inner_bytes_dec(b, inner):
    """bytes -> text under one inner encoding, None unless it reads printable ASCII and is no plain UTF-8/ASCII read
    (EBCDIC: some byte >= 0x80; UTF-16/32: right length, a BOM or a NUL in every code unit's high bytes)."""
    if not isinstance(b, (bytes, bytearray)) or not b:
        return None
    b = bytes(b)
    try:
        if inner.startswith("cp"):
            if max(b) < 0x80:
                return None
            out = b.decode(inner)
        elif inner == "utf-7":
            return utf7_dec(b.decode("ascii"))
        else:
            w = 4 if "32" in inner else 2
            if len(b) % w or (inner in ("utf-16", "utf-32") and b[:w] not in (
                    (b"\xff\xfe", b"\xfe\xff") if w == 2 else (b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff"))):
                return None
            out = b.decode(inner).lstrip("\ufeff")
    except (UnicodeError, ValueError, LookupError):
        return None
    if not out or not out.isascii() or not all(c.isprintable() or c in "\t\r\n" for c in out):
        return None
    if inner in _EBCDIC_ALT:   # cp037 / cp500 differ only on ! [ ] | ^ : the page reading more `!`, fewer brackets
        alt = b.decode(_EBCDIC_ALT[inner])
        if alt.isascii() and _ebcdic_score(alt) > _ebcdic_score(out):
            return None
    return out


_EBCDIC_ALT = {"cp037": "cp500", "cp500": "cp037"}


def _ebcdic_score(x):
    return x.count("!") - sum(x.count(c) for c in "[]|^")


def inner_enc(s, inner, outer="hex"):
    """Text -> `outer` text of its `inner`-encoded bytes (outer: hex, HEX, hex-spaced, base64, base64-nopad, base32,
    binary8, decimal)."""
    return _bytes_out(utf7_enc(s).encode() if inner == "utf-7" else s.encode(inner), outer)


def _bytes_out(b, outer):
    """bytes -> `outer` text (hex, HEX, hex-spaced, base64, base64-nopad, base32, binary8, decimal, base85, ascii85)."""
    if outer == "base85":
        return base64.b85encode(b).decode()
    if outer == "ascii85":
        return base64.a85encode(b).decode()
    if outer == "hex":
        return b.hex()
    if outer == "HEX":
        return b.hex().upper()
    if outer == "hex-spaced":
        return " ".join(f"{x:02x}" for x in b)
    if outer == "base64":
        return base64.b64encode(b).decode()
    if outer == "base64-nopad":
        return base64.b64encode(b).decode().rstrip("=")
    if outer == "base32":
        return base64.b32encode(b).decode()
    if outer == "binary8":
        return " ".join(f"{x:08b}" for x in b)
    if outer == "decimal":
        return " ".join(str(x) for x in b)
    raise ValueError(outer)


def inner_reads(t, inner=None):
    """[(layer, inner, text)] for every byte-layer x inner-encoding reading of `t` (inner: only that one)."""
    out = []
    for layer, b in _bytes_reads(_t(t)):
        for enc in ((inner,) if inner else _BYTE_INNERS + ("utf-7",)):
            got = inner_bytes_dec(b, enc)
            if got is not None:
                out.append((layer, enc, got))
    if not inner:   # + the Unicode-form sniffer: odd fragments, UTF-8 BOM, a BOM per fragment, base85/ascii85 outers
        seen = {x for _l, _i, x in out}
        out += [r for r in unicode_form_reads(t) if r[2] not in seen]
    return out


def inner_dec(t, inner=None):
    """The first byte-layer reading of `t` under `inner` (or any inner encoding), else None."""
    r = inner_reads(t, inner)
    return r[0][2] if r else None


def inner_free(p):
    """Speculative Mastery-line decoder: every EBCDIC / UTF-16 / UTF-32 / UTF-7 reading under a byte layer, plus bare
    UTF-7 text; most English first."""
    if not isinstance(p, str) or not p.strip():
        return []
    lead = p[:len(p) - len(p.lstrip())]
    outs = [x for _l, _i, x in inner_reads(p)]
    u7 = utf7_dec(p.strip())
    if u7:
        outs.append(u7)
    return [lead + x for x in _top(p, outs, 4)] if outs else []


# ------------------------------------------------- Unicode encoding-form sniffer for ANY decoded byte layer
# D19 "Little Things" = hex of BOM fffe + UTF-16LE, and Mastery line 19 carries its OWN BOM per fragment. The same
# family under another outer (base64 / base32 / base85 / binary / decimal) or another form (UTF-16BE, UTF-32LE/BE, UTF-8
# BOM, BOM-less UCS-2) is one sniff: BOM table longest first (fffe0000 / 0000feff before fffe / feff), else the NUL
# rhythm (00 at every odd index -> LE, every even -> BE; 3 of 4 -> UTF-32). Printable-ASCII gate; never a latin-1 or
# BOM-less UTF-8 read (plain text is the strict decoders' job). A short Mastery line cut mid code unit (odd byte count)
# is read under both alignments: a trailing orphan low byte keeps its char (00 pad), a leading orphan 00 is dropped.
_UBOMS = ((b"\xff\xfe\x00\x00", "utf-32-le"), (b"\x00\x00\xfe\xff", "utf-32-be"), (b"\xef\xbb\xbf", "utf-8"),
          (b"\xff\xfe", "utf-16-le"), (b"\xfe\xff", "utf-16-be"))
_UFORMS = {"utf-16le-bom": (b"\xff\xfe", "utf-16-le"), "utf-16be-bom": (b"\xfe\xff", "utf-16-be"),
           "utf-32le-bom": (b"\xff\xfe\x00\x00", "utf-32-le"), "utf-32be-bom": (b"\x00\x00\xfe\xff", "utf-32-be"),
           "utf-8-bom": (b"\xef\xbb\xbf", "utf-8"), "utf-16le": (b"", "utf-16-le"), "utf-16be": (b"", "utf-16-be"),
           "utf-32le": (b"", "utf-32-le"), "utf-32be": (b"", "utf-32-be")}


def _uform_text(b, enc):
    try:
        s = b.decode(enc).replace("\ufeff", "")
    except (UnicodeError, ValueError):
        return None
    return s if s and s.isascii() and all(c.isprintable() or c in "\t\r\n" for c in s) else None


def _uform_rhythm(b):
    """[(bytes, enc)] the NUL rhythm allows (aligned reads first; odd UTF-16 fragments under both alignments)."""
    n, z = len(b), lambda v: not any(v)
    if n % 4 == 0 and n >= 4:
        if z(b[1::4]) and z(b[2::4]) and z(b[3::4]):
            return [(b, "utf-32-le")]
        if z(b[0::4]) and z(b[1::4]) and z(b[2::4]):
            return [(b, "utf-32-be")]
    if n % 2 == 0:
        return [(b, "utf-16-le")] if z(b[1::2]) else [(b, "utf-16-be")] if z(b[0::2]) else []
    out = []
    if z(b[1::2]):
        out.append((b + b"\x00", "utf-16-le"))   # LE cut after a low byte (== BE missing its leading 00)
    if b[0] == 0 and z(b[2::2]):
        out.append((b[1:], "utf-16-le"))           # LE starting on the previous unit's 00 high byte
    if b[-1] == 0 and z(b[0::2]):
        out.append((b[:-1], "utf-16-be"))          # BE cut after a 00 high byte
    return out


def unicode_form(b):
    """(form, text) for bytes in a Unicode encoding form (BOM'd UTF-8/16/32, BOM-less UTF-16/32 by NUL rhythm), else
    None. Text is printable ASCII, every U+FEFF (one BOM per joined fragment) dropped. Never raises."""
    try:
        if not isinstance(b, (bytes, bytearray)) or len(b) < 2:
            return None
        b = bytes(b)
        for bom, enc in _UBOMS:
            if b.startswith(bom):
                body = b[len(bom):]
                if "16" in enc and len(body) % 2:
                    tries = [(x, e) for x, e in _uform_rhythm(body) if e == enc] if body else []
                else:
                    tries = [(body, enc)]
                for x, e in tries:
                    got = _uform_text(x, e)
                    if got is not None:
                        return e.replace("-le", "le").replace("-be", "be") + "-bom", got
        if 0 not in b:
            return None
        for x, e in _uform_rhythm(b):
            got = _uform_text(x, e)
            if got is not None:
                return e.replace("-le", "le").replace("-be", "be"), got
    except Exception:  # noqa: BLE001 - malformed input reads as nothing
        return None
    return None


def unicode_form_dec(b):
    """bytes -> text under the sniffed Unicode encoding form, else None."""
    r = unicode_form(b)
    return r[1] if r else None


def unicode_form_enc(s, form="utf-16le-bom", outer="hex"):
    """Text -> `outer` text of BOM + `form` bytes (form: a _UFORMS key)."""
    bom, enc = _UFORMS[form]
    return _bytes_out(bom + s.encode(enc), outer)


def unicode_form_reads(t):
    """[(layer, form, text)] for every byte layer (hex, base64, base32, binary8, decimal, octal3, %xx, base85, ascii85)
    of `t` whose bytes sniff as a Unicode encoding form. Never raises."""
    t = _t(t)
    if not isinstance(t, str) or not t.strip():
        return []
    layers = _bytes_reads(t)
    flat = re.sub(r"\s+", "", t)
    if 5 <= len(flat) <= 400000:
        if re.fullmatch(r"[0-9A-Za-z!#$%&()*+\-;<=>?@^_`{|}~]+", flat):
            try:
                layers.append(("base85", base64.b85decode(flat)))
            except (ValueError, TypeError):
                pass
        a = flat[2:-2] if flat.startswith("<~") and flat.endswith("~>") else flat
        if re.fullmatch(r"[!-uz]+", a):
            try:
                layers.append(("ascii85", base64.a85decode(a)))
            except (ValueError, TypeError):
                pass
    out = []
    for layer, b in layers:
        r = unicode_form(b)
        if r:
            out.append((layer, r[0], r[1]))
    return out


def unicode_form_text_dec(t, form=None):
    """The first byte-layer Unicode-form reading of `t` (only `form` if given), else None."""
    for _l, f, x in unicode_form_reads(t):
        if form is None or f == form:
            return x
    return None


# ------------------------------------------------- raw wide artifact: the blob FILE in UTF-16/32 / EBCDIC bytes
# No hex layer: `file` says "Unicode text, UTF-16, little-endian" and a UTF-8 reader raises or returns NUL-laced text.
# blob_text(bytes) reads BYTES: BOM / NUL rhythm (unicode_form) first, then strict UTF-8 (U+FEFF dropped), then EBCDIC
# (cp037/cp500) when 0x40 spaces and c1-e9 / 81-a9 letters dominate, else UTF-8 with replacement. A reader that already
# did decode("utf-8", "replace") keeps the NULs and ASCII: wide_text_dec recovers that (a mangled BOM = 2 U+FFFD).
# A raw UTF-7 file is plain ASCII: the existing utf7_dec / inner_free path reads it. Mastery zips: blob_members.
_EBC_TEXT = set(range(0x81, 0x8a)) | set(range(0x91, 0x9a)) | set(range(0xa2, 0xaa)) | set(range(0xc1, 0xca)) | \
    set(range(0xd1, 0xda)) | set(range(0xe2, 0xea)) | set(range(0xf0, 0xfa)) | {0x40, 0x4b, 0x6b, 0x5a, 0x4f, 0x7a,
                                                                                 0x5e, 0x60, 0x61, 0x6d, 0x6f, 0x7d,
                                                                                 0x05, 0x0d, 0x15, 0x25}


def _ebcdic_text(b):
    """cp037/cp500 text of raw EBCDIC bytes (NEL 0x15 -> newline), None unless spaces + letters dominate."""
    n = len(b)
    if n < 4 or max(b) < 0x80 or b.count(0x40) * 25 < n or sum(x in _EBC_TEXT for x in b) * 20 < n * 19:
        return None
    best = None
    for cp in ("cp037", "cp500"):
        try:
            s = b.decode(cp).replace("\x85", "\n")
        except (UnicodeError, LookupError):
            continue
        if s.isascii() and all(c.isprintable() or c in "\t\r\n" for c in s) and (
                best is None or _ebcdic_score(s) > _ebcdic_score(best[1])):
            best = (cp, s)
    return best


def blob_form(b):
    """(form, text) for a raw artifact: str -> ("text", s); bytes -> ("utf-16le-bom" / "utf-32be" / ... via
    unicode_form, "utf-8", "cp037" / "cp500", or "utf-8-replace"). Never raises."""
    if isinstance(b, str):
        return "text", b
    try:
        b = bytes(b)
        if not b:
            return "utf-8", ""
        r = unicode_form(b)
        if r:
            return r
        if 0 not in b:
            try:
                return "utf-8", b.decode("utf-8").lstrip("﻿")
            except UnicodeError:
                pass
            e = _ebcdic_text(b)
            if e:
                return e
        return "utf-8-replace", b.decode("utf-8", "replace")
    except Exception:  # noqa: BLE001 - malformed input reads as nothing
        return "utf-8-replace", ""


def blob_text(b):
    """Raw artifact bytes (or text) -> text, whatever its wide/EBCDIC encoding (see blob_form)."""
    return blob_form(b)[1]


def blob_members(b, limit=64, maxsize=4 << 20):
    """[(name, form, text)] for every file member of a zip (each member sniffed on its own: members may each be wide),
    else [("", form, text)] for the blob itself. Never raises."""
    import io
    import zipfile
    try:
        if isinstance(b, (bytes, bytearray)) and bytes(b[:4]) == b"PK\x03\x04":
            out = []
            with zipfile.ZipFile(io.BytesIO(bytes(b))) as z:
                for zi in z.infolist()[:limit]:
                    if zi.is_dir() or zi.file_size > maxsize:
                        continue
                    try:
                        out.append((zi.filename, *blob_form(z.read(zi))))
                    except Exception:  # noqa: BLE001 - encrypted / corrupt member
                        continue
            return out
    except Exception:  # noqa: BLE001
        pass
    return [("", *blob_form(b))]


def wide_text_dec(t):
    """Text a UTF-8-replace (or latin-1) reader made of a raw UTF-16/32 file -> the real text, else None. The BOM became
    U+FFFD U+FFFD (or 'ÿþ' / 'þÿ'); ASCII + NULs survive. Needs a NUL in the text."""
    if isinstance(t, (bytes, bytearray)):
        f, s = blob_form(t)
        return s if f not in ("utf-8", "utf-8-replace", "text") and s else None
    if not isinstance(t, str) or "\x00" not in t or len(t) > 1600000:
        return None
    body = t.replace("﻿", "")
    heads = [b""]
    for mangled in ("��", "\xff\xfe", "\xfe\xff"):
        for k in (0, 2):   # utf-32-be BOM 00 00 fe ff: the mangled pair after two NULs
            if body[k:k + 2] == mangled and (k == 0 or body[:2] == "\x00\x00"):
                body = body[:k] + body[k + 2:]
                heads = [body[:k].encode("latin-1") + bom for bom in (b"\xff\xfe", b"\xfe\xff")]
                body = body[k:]
                break
        if heads != [b""]:
            break
    if not body.isascii():
        return None
    raw = body.encode("ascii")
    for h in heads:
        got = unicode_form_dec(h + raw)
        if got:
            return got
    return None


def reader_text(blob):
    """Any warmups reader's input -> text: bytes via blob_text, NUL-laced text (a raw wide file read as UTF-8) via
    wide_text_dec, other text as is."""
    if isinstance(blob, (bytes, bytearray)):
        return blob_text(blob)
    if isinstance(blob, str) and "\x00" in blob:
        return wide_text_dec(blob) or blob
    return blob


def raw_wide_enc(s, form="utf-16le-bom"):
    """Text -> what a UTF-8-replace reader shows for a raw `form` file (a _UFORMS key)."""
    bom, enc = _UFORMS[form]
    return (bom + s.encode(enc)).decode("utf-8", "replace")


def _xor(s, k):
    return bytes(b ^ k for b in _u(s))


# repeating-key XOR keyed by a title word, hex / base64 out: key = c ^ p over the crib, period = smallest repeat
def xorkey(b, key):
    return bytes(x ^ key[i % len(key)] for i, x in enumerate(b))


def xorkey_enc(s, key, rep="hex"):
    b = xorkey(_u(s), key.encode() if isinstance(key, str) else key)
    if rep.startswith("hex"):
        return b.hex().upper() if rep == "HEX" else b.hex()
    t = (base64.urlsafe_b64encode(b) if rep.startswith("base64url") else base64.b64encode(b)).decode()
    return t.rstrip("=") if rep.endswith("-nopad") else t


def _xor_reads(t):
    """[(rep, bytes)] for the blob's hex / base64 / base64url readings (whitespace and 0x / \\x / : separators dropped)."""
    s = re.sub(r"\s+", "", _t(t))
    out = []
    h = re.sub(r"0x|\\x|[:,]", "", s, flags=re.I)
    if h and len(h) % 2 == 0 and re.fullmatch(r"[0-9A-Fa-f]+", h):
        out.append(("HEX" if re.search(r"[A-F]", h) and not re.search(r"[a-f]", h) else "hex", bytes.fromhex(h)))
    if s and re.fullmatch(r"[A-Za-z0-9+/_-]+={0,2}", s) and not ("+" in s or "/" in s) & ("-" in s or "_" in s):
        url = "-" in s or "_" in s
        try:
            b = base64.b64decode(_b64pad(s.replace("-", "+").replace("_", "/")), validate=True)
            out.append((("base64url" if url else "base64") + ("" if "=" in s or len(s) % 4 == 0 else "-nopad"), b))
        except Exception:  # noqa: BLE001
            pass
    return out


def _xor_period(ks, maxp=32):
    """The smallest period p (2p <= len) the key stream repeats with, else None."""
    for p in range(1, min(maxp, len(ks) // 2) + 1):
        if all(ks[i] == ks[i % p] for i in range(p, len(ks))):
            return p
    return None


def _xor_text(b):
    try:
        s = b.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if s.isprintable() else None


def xorkey_solve(blob, hints=()):
    """(name, sentence, enc) when the blob is hex / base64 of the warmups sentence XORed with a repeating key (key =
    cipher ^ crib over the fixed prefix, cut at its smallest period; a title / prompt word as the key otherwise), else
    None. A key stream with no period <= 32 and no hint word that reads crib + slug -> None."""
    try:
        crib = _CRIB.encode()
        for rep, data in _xor_reads(blob):
            if len(data) <= len(crib):
                continue
            ks = bytes(c ^ p for c, p in zip(data, crib))
            keys = []
            per = _xor_period(ks)
            if per and 0 not in ks[:per]:   # a zero key byte = untouched text: that's the bare hex / base64 codec
                keys.append(ks[:per])
            keys += [k.encode() for k in _hint_keys(hints)]
            for key in keys:
                got = _xor_text(xorkey(data, key))
                if got and got.startswith(_CRIB) and SLUG.fullmatch(got[len(_CRIB):]):
                    return (f"xorkey:{key.decode('latin-1')}-{rep}", got,
                            (lambda key, rep: lambda s: xorkey_enc(s, key, rep))(key, rep))
    except Exception:  # noqa: BLE001
        return None
    return None


def xorkey_dec(t):
    r = xorkey_solve(t)
    return r[1] if r else None


def xorkey_fragment(p):
    """Mastery free-text fragment = hex / base64 of a sentence piece under a repeating title-word XOR key, key
    restarting per fragment: the fixed sentence at every offset as the crib, the key stream must repeat with an
    all-letter key (>= 2 full periods + 4 bytes confirmed) and the whole fragment must decode printable."""
    out = []
    try:
        crib = _CRIB.encode()
        for _rep, data in _xor_reads(p):
            for off in range(len(crib)):
                c = crib[off:]
                m = min(len(c), len(data))
                if m < 10:
                    break
                ks = bytes(x ^ y for x, y in zip(data[:m], c))
                per = _xor_period(ks, min(16, (m - 4) // 2))
                if not per or per < 2 or not ks[:per].isalpha():
                    continue
                got = _xor_text(xorkey(data, ks[:per]))
                if got and got not in out:
                    out.append(got)
    except Exception:  # noqa: BLE001
        return out
    return out[:4]


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


_XOR_PUN = ("xor", "key", "secret", "huntress", "cipher")


def _xorkey_cands(keys):
    return [(f"xorkey:{k}-{rep}", (lambda k, rep: lambda s: xorkey_enc(s, k, rep))(k, rep),
             (lambda k: lambda t: next((_xor_text(xorkey(b, k.encode())) for _r, b in _xor_reads(t)), None))(k))
            for k in keys for rep in ("hex", "base64")]


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
        # 4-bit binary hex nibbles (run together = binary8-nospace above): separators, byte gaps, nibble-swapped
        *[(f"binary4{tag}(hex)", (lambda kw: lambda s: bin4_enc(s, **kw))(kw),
           (lambda sw: lambda t: bin4_dec(t, sw))(kw.get("swap", False)))
          for tag, kw in (("", {}), ("-comma", {"sep": ","}), ("-comma-space", {"sep": ", "}), ("-dash", {"sep": "-"}),
                          ("-2space", {"byte": "  "}), ("-bytes|", {"byte": " | "}), ("-pairs-dash", {"sep": "-", "byte": " "}),
                          ("-pairs-colon", {"sep": ":", "byte": " "}), ("-swap", {"swap": True}),
                          ("-swap-blob", {"sep": "", "swap": True}))],
        # BCD of decimal char codes (8421 / Excess-3): char separators, one token per char, nibble streams
        *[(f"bcd{tag}", (lambda kw: lambda s: bcd_enc(s, **kw))(kw), bcd_dec)
          for tag, kw in (("", {}), ("-comma", {"char": ", "}), ("-2space", {"char": "  "}), ("-pipe", {"char": " | "}),
                          ("-tok", {"sep": "", "char": " "}), ("-tok3", {"sep": "", "char": " ", "pad": 3}),
                          ("-tokpacked", {"sep": "", "char": " ", "pad": -1}), ("-stream3", {"char": " ", "pad": 3}),
                          ("-streampacked", {"char": " ", "pad": -1}), ("-stream", {"char": " "}),
                          ("-blob3", {"sep": "", "char": "", "pad": 3}), ("-xs3", {"xs3": True}),
                          ("-xs3-tok", {"sep": "", "char": " ", "xs3": True}))],
        # address notation: IPv4 dotted quads, IPv6 ('::' padding), MAC, UUID (RFC / GUID mixed-endian)
        *[(f"addr-{tag}", (lambda kw: lambda s: addr_enc(s, **kw))(kw),
           (lambda k: lambda t: addr_dec(t, k))(kw["kind"]))
          for tag, kw in (("ipv4", {"kind": "ipv4"}), ("ipv4-short", {"kind": "ipv4", "pad": False}),
                          ("ipv4-comma", {"kind": "ipv4", "sep": ", "}), ("ipv4-lines", {"kind": "ipv4", "sep": "\n"}),
                          ("ipv6", {"kind": "ipv6"}), ("ipv6-short", {"kind": "ipv6", "pad": False}),
                          ("ipv6-upper", {"kind": "ipv6", "upper": True}), ("mac", {"kind": "mac"}),
                          ("mac-dash-upper", {"kind": "mac", "style": "-", "upper": True}),
                          ("mac-cisco", {"kind": "mac", "style": "."}), ("mac-short", {"kind": "mac", "pad": False}),
                          ("uuid", {"kind": "uuid"}), ("uuid-upper", {"kind": "uuid", "upper": True}),
                          ("uuid-guid", {"kind": "guid"}), ("uuid-short", {"kind": "uuid", "pad": False}))],
        # Gray-coded binary per byte (8-bit / 7-bit, spaced or run together)
        ("gray8", gray_enc, gray_dec), ("gray8-nospace", lambda s: gray_enc(s, sep=""), gray_dec),
        ("gray7", lambda s: gray_enc(s, 7), gray_dec),
        ("binary8-lsb", lsb_enc, lsb_dec), ("binary8-lsb-nospace", lambda s: lsb_enc(s, sep=""), lsb_dec),
        ("binary7-lsb", lambda s: lsb_enc(s, 7), lsb_dec),
        ("binary8-bitrev", lambda s: lsb_enc(s, whole=True), lambda t: lsb_dec(t, True)),
        ("binary8-bitrev-nospace", lambda s: lsb_enc(s, sep="", whole=True), lambda t: lsb_dec(t, True)),
        # Roman-numeral char codes (any separator / case; " / " words; hex-nibble variant with N = 0)
        *[(f"roman{tag}", (lambda kw: lambda s: roman_enc(s, **kw))(kw), roman_dec)
          for tag, kw in (("", {}), ("-lower", {"lower": True}), ("-comma", {"sep": ", "}), ("-dash", {"sep": "-"}),
                          ("-dot", {"sep": "."}), ("-words", {"word": " / "}), ("-nib", {"nib": True}))],
        # Chuck Norris unary: 7-bit ASCII classic, 8-bit bytes (= hex nibbles run together), hex digits as text
        *[(f"chuck-unary{b}{'-hex' if i else ''}", (lambda b, i: lambda s: chuck_enc(s, b, i))(b, i),
           (lambda b, i: lambda t: chuck_dec(t, b, i))(b, i)) for b in (7, 8) for i in (None, "hex")],
        # a-p letter hex (D17's middle layer): standalone, then under a letter carrier
        ("aphex", aphex_enc, aphex_dec),
        ("aphex-pairs", lambda s: aphex_enc(s, " "), aphex_dec),
        ("aphex-upper", lambda s: aphex_enc(s, upper=True), aphex_dec),
        # seven-segment display hex: segment masks (gfedcba / abcdefg / abcdefg+dp, active-low) or segment-letter sets
        *[(f"seg7{tag}", (lambda kw: lambda s: seg7_enc(s, **kw))(kw), seg7_dec)
          for tag, kw in (("-hex", {}), ("-hexraw", {"fmt": "hexraw"}), ("-dec", {"fmt": "dec"}), ("-bin", {"fmt": "bin"}),
                          ("-letters", {"fmt": "letters"}), ("-abc-hex", {"order": "abcdefg"}),
                          ("-abcdp-hex", {"order": "abcdefg", "shift": 1}), ("-inv-hex", {"inv": True}),
                          ("-run", {"fmt": "hexraw", "sep": ""}))],
        # any <=16-token alphabet over hex, map recovered from the crib (the demo encoder is one sample alphabet)
        ("crib-token-hex", crib_tok_enc, crib_tok_dec),
        *[(f"{c}(aphex{tag})", (lambda c, sp: lambda s: aphex_over_enc(s, c, sp))(c, sp),
           (lambda c: lambda t: aphex_over_dec(t, c))(c))
          for c in ("bacon24", "polybius", "tapcode", "a1z26", "a1z26-comma") for tag, sp in (("", ""), ("-pairs", " "))],
        # DNA bases: 2 bits a base (4 a byte, any of the 24 base->bit orders), then codons (64-symbol / amino-acid table)
        ("dna", dna_enc, dna_dec),
        ("dna-bytes", lambda s: dna_enc(s, sep=" "), dna_dec),
        ("dna-lower", lambda s: dna_enc(s, lower=True), dna_dec),
        ("rna", lambda s: dna_enc(s, rna=True), dna_dec),
        ("codon64", codon_enc, codon_dec),
        ("codon64-spaced", lambda s: codon_enc(s, sep=" "), codon_dec),
        *[(f"{n}:{o}", (lambda f, o, sp: lambda s: f(s, o, sp))(f, o, sp), (lambda d, o: lambda t: d(t, o))(d, o))
          for o in _DNA_ORDERS[1:] for n, f, d, sp in (("dna", dna_enc, dna_dec, ""), ("dna-bytes", dna_enc, dna_dec, " "),
                                                       ("codon64", codon_enc, codon_dec, ""))],
        ("codon-amino", lambda s: codon_enc(s, amino=True), lambda t: codon_dec(t, amino=True)),
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
        ("css-hex", css_hex_enc, css_hex_dec),
        ("css-hex-upper", lambda s: css_hex_enc(s, upper=True), css_hex_dec),
        ("css-hex-pad20", lambda s: css_hex_enc(s, pad=b" "), css_hex_dec),
        ("css-hex3", lambda s: css_hex_enc(s, "hex3"), css_hex_dec),
        ("css-hex3-upper-comma", lambda s: css_hex_enc(s, "hex3", ",", upper=True), css_hex_dec),
        ("css-rgb", lambda s: css_hex_enc(s, "rgb"), css_hex_dec),
        ("iching", iching_enc, iching_dec),
        ("iching-url", lambda s: iching_enc(s, alpha=_B64URL), lambda t: iching_dec(t, alpha=_B64URL)),
        *[(f"iching-{o}", (lambda o: lambda s: iching_enc(s, o))(o), (lambda o: lambda t: iching_dec(t, o))(o))
          for o in _HEXA_ORDERS if o != "kingwen"],
        ("trigram-octal", trigram_enc, trigram_dec),
        ("trigram-octal-blob", lambda s: trigram_enc(s, sep=""), trigram_dec),
        ("trigram-octal-inv", lambda s: trigram_enc(s, comp=True), lambda t: trigram_dec(t, comp=True)),
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
        ("morse", morse_enc, morse_text_dec),
        ("morse-3space", lambda s: morse_enc(s, word=" "), morse_text_dec),
        # Morse as timing units (1=dit 111=dah, gaps 0/000/0000000; `=`/`.`), plain and over a case-free inner codec
        ("morse-timing", morse_timing_enc, morse_timing_text),
        ("morse-timing=.", lambda s: morse_timing_enc(s, "=", "."), morse_timing_text),
        *[(f"morse-timing{('', '-cat')[cat]}({inner})", (lambda i, c: lambda s: morse_timing_enc(s, inner=i, cat=c))(
            inner, cat), morse_layer_dec) for inner in ("hex", "decimal", "octal3", "binary8", "a1z26")
          for cat in (False, True) if not (cat and inner == "a1z26")],
        # Morse over a case-free inner codec (D16 morse-hex generalized): spaced inners x word gap, fixed-width concat
        *[(f"morse{tag}({inner})", (lambda i, w: lambda s: morse_over_enc(s, i, w))(inner, w), morse_layer_dec)
          for inner in ("decimal", "octal3", "binary8", "a1z26") for tag, w in (("", " / "), ("/", "/"), ("3", "   "))],
        *[(f"morse-cat({inner})", (lambda i: lambda s: morse_over_enc(s, i, ""))(inner), morse_layer_dec)
          for inner in ("octal3", "binary8", "decimal", "base32", "base32-nopad")],
        # Baudot / ITA2: 5-bit groups (spaced / run together / dCode bit order), `*`/`.` tape, decimal; ITA2 or US-TTY
        # figures, leading LTRS or not, USOS; also over hex (FIGS digits + LTRS A-F)
        *[(f"baudot{tag}{('', '-us')[us]}{('', '-noinit')[not ini]}{('', '-usos')[uo]}",
           (lambda kw, us, ini, uo: lambda s: baudot_enc(s, table=("ita2", "us")[us], init=ini, usos=uo, **kw))(
               kw, us, ini, uo), baudot_dec)
          for tag, kw in (("", {}), ("-cat", {"sep": ""}), ("-lsb", {"lsb": True}), ("-tape", {"fmt": "tape"}),
                          ("-tape-lines", {"fmt": "tape", "sep": "\n"}), ("-dec", {"fmt": "dec"}))
          for us in (False, True) for ini in (True, False) for uo in (False, True)],
        *[(f"baudot{tag}(hex)", (lambda kw: lambda s: baudot_enc(s, inner="hex", **kw))(kw), baudot_dec)
          for tag, kw in (("", {}), ("-noinit", {"init": False}), ("-cat", {"sep": ""}), ("-lsb", {"lsb": True}),
                          ("-tape", {"fmt": "tape"}))],
        ("nato", nato_enc, nato_dec),
        ("nato-strict", nato_enc, lambda t: nato_layer_dec(t, "text")),
        ("nato-alt", lambda s: nato_layer_enc(s, alt=True), lambda t: nato_layer_dec(t, "text")),
        # NATO words over a case-free inner codec (spell the symbols): spaced inner tokens x group gap, and run together
        *[(f"nato{tag}({inner})", (lambda i, a, w: lambda s: nato_layer_enc(s, i, a, word=w))(inner, alt, w),
           (lambda i: lambda t: nato_layer_dec(t, i))(inner)) for inner in ("hex", "decimal", "octal3", "binary8")
          for tag, alt, w in (("", False, " / "), ("-alt", True, " / "), ("|", False, " | "), ("|-alt", True, " | "),
                              ("-cat", False, ""), ("-cat-alt", True, ""))],
        # digits / hex spelled as English words over a case-free inner codec; cardinal numbers as char codes
        *[(f"spelled{tag}({inner})", (lambda i, kw: lambda s: spelled_enc(s, i, **kw))(inner, kw),
           (lambda i: lambda t: spelled_dec(t, i))(inner)) for inner in ("hex", "decimal", "octal3", "binary8")
          for tag, kw in (("", {}), ("-title", {"title": True}), ("|", {"word": " | "}), ("-cat", {"word": ""}),
                          ("-cat-title", {"word": "", "title": True}), ("-comma", {"word": ", "}),
                          ("-nib", {"nib": True}), ("-nib-cat", {"nib": True, "word": ""}))
          if inner == "hex" or "nib" not in tag],
        *[(f"spelled-num{tag}", (lambda kw: lambda s: spelled_enc(s, num=True, **kw))(kw),
           lambda t: spelled_dec(t, "num"))
          for tag, kw in (("", {"word": ", "}), ("-and", {"word": ", ", "conj": True}), ("/", {"word": " / "}),
                          ("-title", {"word": ", ", "title": True}), ("-lines", {"word": "\n"}))],
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
        # hex digits through digit-capable grids: Braille ⠼ runs, Braille ASCII cells, 6x6 Polybius / tap (A-Z0-9)
        ("braille(hex)", lambda s: braille_enc(s.encode().hex()), braille_hex_dec),
        ("braille(HEX)", lambda s: braille_enc(s.encode().hex().upper()), braille_hex_dec),
        ("braille-spaced(hex)", lambda s: braille_enc(" ".join(f"{b:02x}" for b in s.encode())), braille_hex_dec),
        ("braille-pyb(hex)", lambda s: braille_pyb_enc(s.encode().hex()), braille_hex_dec),
        ("braille-pyb(HEX)", lambda s: braille_pyb_enc(s.encode().hex().upper()), braille_hex_dec),
        ("braille-ascii(hex)", lambda s: braille_ascii_enc(s.encode().hex()), braille_ascii_hex_dec),
        ("polybius6(hex)", lambda s: polybius6_enc(s, sep=""), polybius6_dec),
        ("polybius6-spaced(hex)", polybius6_enc, polybius6_dec),
        ("polybius6-comma(hex)", lambda s: polybius6_enc(s, sep=","), polybius6_dec),
        ("tapcode6(hex)", tap6_enc, tap6_dec),
        ("tapcode6-knock(hex)", lambda s: tap6_enc(s, tap="x"), tap6_dec),
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
        # DTMF tone pairs / keypad chars over hex (3 nibble maps) or a digits-only inner codec
        *[(f"dtmf{tag}({inner})", (lambda i, kw: lambda s: dtmf_enc(s, i, **kw))(inner, kw),
           (lambda i: lambda t: dtmf_dec(t, i))(inner))
          for inner in ("hex", "hex-keypad", "hex-mt8870", "decimal", "octal3", "binary8")
          for tag, kw in (("", {}), ("-cat", {"word": ""}), ("-hz", {"hz": True}), ("-comma", {"sep": ", ", "word": ""}),
                          ("-keys", {"keys": True, "sep": "", "word": " "}), ("-keys-cat", {"keys": True, "sep": "", "word": ""}))
          if inner.startswith("hex") or not kw.get("keys")],
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
        ("regional-spaced", lambda s: regional_enc(s, " ", "   "), regional_dec),
        ("regional-spaced-slash", lambda s: regional_enc(s, " ", " / "), regional_dec),
        ("regional-zwgap", lambda s: regional_enc(s, "\u200b"), regional_dec),
        ("regional-keycap", lambda s: regional_enc(s, keycap=True), regional_dec),
        ("regional-spaced-keycap", lambda s: regional_enc(s, " ", "   ", keycap=True), regional_dec),
        ("regional-shortcode", lambda s: regional_enc(s, " ", "   ", short=True), regional_dec),
        ("zw-bits8", zw_bits_enc, zw_dec),
        ("zw-bits8-inv", lambda s: zw_bits_enc(s, "‌", "​"), zw_dec),
        ("zw-fingerprint", lambda s: zw_bits_enc(s, "‌", "​", sep="‍", join="﻿"), zw_dec),
        ("zw-steganographr", lambda s: zw_bits_enc(s, width=0, sep="⁠", wrap="﻿"), zw_dec),
        ("zwsp-steg", lambda s: zw_base_enc(s, _ZWSP_STEG, 7), zw_dec),
        ("zwsp-steg-zwsp", lambda s: zw_base_enc(s, _ZWSP_STEG[:3], 11), zw_dec),
        ("zero-width-lib", lambda s: zw_base_enc(s, _ZWLIB, sep="​"), zw_dec),
        ("ws-bits8", ws_bits_enc, ws_dec),
        ("ws-bits8-inv", lambda s: ws_bits_enc(s, "\t", " "), ws_dec),
        ("ws-bits8-lines", lambda s: ws_bits_enc(s, sep="\n"), ws_dec),
        ("ws-nib4", lambda s: ws_bits_enc(s, width=4), ws_dec),
        ("ws-nib4-inv", lambda s: ws_bits_enc(s, "\t", " ", 4), ws_dec),
        ("snow", snow_enc, ws_dec),
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
        ("utf-7", utf7_enc, utf7_dec),
        ("utf-7-dash", lambda s: utf7_enc(s, dash=True), utf7_dec),
    ]
    # inner byte encodings under a byte layer: hex / base64 / ... of the cp037 / cp500 / UTF-16 / UTF-32 / UTF-7 bytes
    out += [(f"{outer}({inner})", (lambda i, o: lambda s: inner_enc(s, i, o))(inner, outer),
             (lambda i: lambda t: inner_dec(t, i))(inner))
            for inner in _BYTE_INNERS + ("utf-7",)
            for outer in ("hex", "HEX", "hex-spaced", "base64", "base64-nopad", "base32", "binary8", "decimal")]
    # Unicode encoding forms the _BYTE_INNERS grid lacks: BOM'd UTF-16BE / UTF-32 / UTF-8 and the base85 outers
    out += [(f"{outer}({form})", (lambda f, o: lambda s: unicode_form_enc(s, f, o))(form, outer),
             (lambda f: lambda t: unicode_form_text_dec(t, f))(form))
            for form in ("utf-16be-bom", "utf-32le-bom", "utf-32be-bom", "utf-8-bom")
            for outer in ("hex", "HEX", "hex-spaced", "base64", "base32", "binary8", "decimal", "base85")]
    out += [(f"{outer}({form})", (lambda f, o: lambda s: unicode_form_enc(s, f, o))(form, outer),
             (lambda f: lambda t: unicode_form_text_dec(t, f))(form))
            for form in ("utf-16le-bom", "utf-16le", "utf-16be") for outer in ("base85", "ascii85")]
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
    # generic two-symbol fixed-width groups (D17 bacon-hex generalized): pair x width x inner, one decoder for all
    out += [(f"twosym-{pr}-w{w}-{inner}{'-blob' if not sp else ''}",
             (lambda pr, w, inner, sp: lambda s: twosym_enc(s, pr, w, inner, sp))(pr, w, inner, sp), twosym_dec)
            for pr in ("ab", "AB", "ba", "01", "10", "XO", "OX")
            for inner, ws in (("hex", (4, 5, 6, 7, 8)), ("ascii", (7, 8)))
            for w in ws for sp in (" ", "")
            if (pr, w, inner, sp) not in (("01", 8, "ascii", " "), ("ab", 5, "hex", " "))]   # = D4 binary8 / D17
    # the group VALUES index an alphabet: base32 (w5), base64 std/url (w6), octal digits (w3)
    out += [(f"twosym-{pr}-w{w}-{inner}{'-blob' if not sp else ''}",
             (lambda pr, w, inner, sp: lambda s: twosym_enc(s, pr, w, inner, sp))(pr, w, inner, sp), twosym_dec)
            for pr in ("ab", "AB", "ba", "01", "10", "XO", "OX")
            for inner, w, sps in (("b32", 5, (" ", "")), ("b64", 6, (" ", "")), ("b64url", 6, (" ",)),
                                  ("octal", 3, (" ",)))
            for sp in sps]
    # Kenny code (m/p/f triplets, other characters kept) + fixed-width ternary groups: symbols x width x inner
    out += [("kenny", kenny_enc, tern_dec), ("kenny-lower", lambda s: kenny_enc(s.lower()), tern_dec)]
    out += [(f"ternary-{sy}-w{w}-{inner}{'-blob' if not sp else ''}",
             (lambda sy, w, inner, sp: lambda s: tern_enc(s, sy, w, inner, sp))(sy, w, inner, sp), tern_dec)
            for sy in ("012", "mpf")
            for inner, ws in (("alpha", (3,)), ("hex", (3,)), ("ascii", (5, 6)))
            for w in ws for sp in (" ", "")]
    # char codes / hex nibbles as fixed-width base-4..7 digit groups (ternary 0/1/2 = the entries above)
    out += [(f"radix{r}-w{w}-{inner}{'-blob' if not sp else ''}",
             (lambda r, w, inner, sp: lambda s: radix_enc(s, r, w, inner, sp))(r, w, inner, sp), radix_dec)
            for r, ascii_ws in ((4, (4,)), (5, (3, 4)), (6, (3,)), (7, (3,)))
            for inner, ws in (("hex", (2,)), ("ascii", ascii_ws))
            for w in ws for sp in (" ", "")]
    # ordered glyph sets (dice / chess / zodiac / suits / Mahjong) as radix digits, same group -> value rules
    out += [(f"glyph-{kind}-w{w}-{inner}{'-blob' if not sp else ''}",
             (lambda kind, w, inner, sp: lambda s: glyph_radix_enc(s, kind, w, inner, sp))(kind, w, inner, sp),
             glyph_radix_dec)
            for kind, ws in (("dice", ((3, "ascii"), (2, "hex"))), ("chess", ((2, "ascii"), (2, "hex"))),
                             ("zodiac", ((2, "ascii"), (2, "hex"))), ("suits8", ((3, "ascii"), (2, "hex"))),
                             ("suits4", ((4, "ascii"), (2, "hex"))), ("mahjong", ((2, "ascii"), (1, "hex"))))
            for w, inner in ws for sp in (" ", "")]
    # perfect riffle shuffle k = 1-6 (out = scytale-rows2 at k=1: listed first so the deck pun keeps its name), then
    # any k via the crib-gated keyless walk (infer returns the solved k's encoder; this entry's enc never matches)
    out += [(f"riffle-{'in' if inn else 'out'}{k}", (lambda k, inn: lambda s: riffle_enc(s, k, inn))(k, inn),
             (lambda k, inn: lambda t: riffle_dec(t, k, inn))(k, inn)) for inn in (False, True) for k in range(1, 7)]
    out += [("riffle", lambda s: None, riffle_crib_dec)]
    # Bifid / Trifid over the standard keyless square, period full / 5-10 x layout (any period 2-15: frac_crib_dec)
    out += _frac_cands()
    # columnar / scytale transposition, keyless: identity order = scytale with n columns (col-read and row-read)
    out += [(f"scytale{n}", (lambda n: lambda s: col_enc(s, n))(n), (lambda n: lambda t: col_dec(t, n))(n))
            for n in range(2, 9)]
    out += [(f"scytale-rows{n}", (lambda n: lambda s: col_dec(s, n))(n), (lambda n: lambda t: col_enc(t, n))(n))
            for n in range(2, 9)]
    # word-level transposition (speculative): whole words rail-fenced / scytale'd, or each word's letters rail-fenced;
    # one crib-gated decoder (wordtp_solve) reads every token order x per-word map
    out += [(f"word-rail{n}", (lambda n: lambda s: _wtp_words(s, "rail", n))(n), wordtp_dec) for n in (2, 3, 4)]
    out += [(f"word-scytale{m}", (lambda m: lambda s: _wtp_words(s, "scytale", m))(m), wordtp_dec) for m in (2, 3)]
    out += [(f"word-each-rail{n}", (lambda n: lambda s: " ".join(rail_enc(w, n) for w in s.split(" ")))(n), wordtp_dec)
            for n in (2, 3)]
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
    # redefence 2-8 rails x offset, any rail read order: keyless crib-pinned decoder (infer returns the solved key's
    # encoder; this entry's enc never matches)
    out += [("redefence", lambda s: None, redefence_crib_dec)]
    # skip cipher (dCode): every k-th char from start 0 / 1, next unread position on a collision (any gcd(k, L))
    out += [(f"skip{k}-s{st}", (lambda k, st: lambda s: skip_enc(s, k, st))(k, st),
             (lambda k, st: lambda t: skip_dec(t, k, st))(k, st)) for k in range(2, 13) for st in (0, 1)]
    out += [(f"affine{a},{b}", (lambda a, b: lambda s: affine(s, a, b))(a, b),
             (lambda a, b: lambda t: affine_inv(t, a, b))(a, b)) for a in _AFFINE_A for b in range(26)]
    out += [(f"xor{k:#04x}-hex", (lambda k: lambda s: _xor(s, k).hex())(k),
             (lambda k: lambda t: bytes(b ^ k for b in bytes.fromhex(t.strip())).decode())(k)) for k in range(1, 256)]
    out += [(f"xor{k:#04x}-base64", (lambda k: lambda s: base64.b64encode(_xor(s, k)).decode())(k),
             (lambda k: lambda t: bytes(b ^ k for b in base64.b64decode(_b64pad(t))).decode())(k)) for k in range(1, 256)]
    # repeating-key XOR, key = a pun word (any other key: the crib -> xorkey_solve, or _hint_cands)
    out += _xorkey_cands(_XOR_PUN)
    # chained pairs of confirmed codecs, inner first ("base64 of the reversed text", "hex of rot13", ...)
    for (_d1, n1, e1, d1, _f1), (_d2, n2, e2, d2, _f2) in itertools.product(DAYS, DAYS):
        if n1 != n2:
            out.append((f"{n2}({n1})", (lambda e1, e2: lambda s: e2(e1(s)))(e1, e2),
                        (lambda d1, d2: lambda t: d1(d2(t)))(d1, d2)))
    # a free letter map over a strict carrier beyond the DAYS x DAYS pairs: swapcase over the base64/32 family
    # (swapcase(base32) = lowercase base32), and the DAYS letter maps over the carrier variants (nopad / lower / HEX)
    have = {n: (e, d) for n, e, d in out}
    days = {n for _d, n, _e, _dd, _f in DAYS}
    frees = [(n, e, d) for _d, n, e, d, f in DAYS if f] + [("swapcase", str.swapcase, str.swapcase)]
    for (n1, e1, d1), n2 in itertools.product(frees, ("base64", "base32", "base64url-nopad", "base64-nopad",
                                                      "base32-nopad", "base64url", "base32-lower", "hex-upper")):
        if (n1 != "swapcase" and n2 in days) or (n1 == "swapcase" and n2 in ("base32-lower", "hex-upper")):
            continue   # a DAYS x DAYS pair above / = the bare carrier
        e2, d2 = have[n2]
        out.append((f"{n1}({n2})", (lambda e1, e2: lambda s: e1(e2(s)))(e1, e2),
                    (lambda d1, d2: lambda t: d2(d1(t)))(d1, d2)))
    return out


CANDIDATES = _cands()


# ------------------------------------------- wide text (PowerShell -EncodedCommand style) under the other byte outers
# base64 of UTF-16LE = `TgBpAGMAZQAg...` (an `A` every 4th char, `//5O` with a BOM), ~2.67x the text. plaintext() already
# reads every outer below (decode_chunk + unicode_form_reads); these are the EXACT encoders infer() needs to name the
# GM's bytes (base64url +/- pad, BOM'd base64-nopad, MIME-wrapped, base32 nopad / lowercase / base32hex, Z85) -- before
# them a base64url blob of UTF-16LE inferred as "hex(utf-16le)" (decoder pass), which re-encodes to the wrong bytes.
_WIDE_FORMS = ("utf-16le", "utf-16le-bom", "utf-16be", "utf-16be-bom")
_WIDE_OUTERS = ("base64url", "base64url-nopad", "base64-nopad", "base64-mime", "base32-nopad", "base32-lower",
                "base32-lower-nopad", "base32hex", "base32hex-nopad", "z85")
_B32HEX = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567", "0123456789ABCDEFGHIJKLMNOPQRSTUV")
_UNB32HEX = str.maketrans("0123456789ABCDEFGHIJKLMNOPQRSTUV", "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")


def _wide_out(b, outer):
    """bytes -> `outer` text (one of _WIDE_OUTERS)."""
    if outer.startswith("base64"):
        x = base64.b64encode(b).decode()
        if outer == "base64-mime":
            return "\n".join(x[i:i + 76] for i in range(0, len(x), 76))
        if outer.startswith("base64url"):
            x = x.replace("+", "-").replace("/", "_")
    elif outer.startswith("base32"):
        x = base64.b32encode(b).decode()
        x = x.lower() if "lower" in outer else x.translate(_B32HEX) if "hex" in outer else x
    elif outer == "z85":
        if len(b) % 4:
            raise ValueError("z85 needs whole 4-byte frames")
        return "".join(_Z85[int.from_bytes(b[i:i + 4], "big") // 85 ** k % 85]
                       for i in range(0, len(b), 4) for k in (4, 3, 2, 1, 0))
    else:
        raise ValueError(outer)
    return x.rstrip("=") if outer.endswith("nopad") else x


def wide_enc(s, form="utf-16le", outer="base64url"):
    bom, enc = _UFORMS[form]
    return _wide_out(bom + s.encode(enc), outer)


def wide_reads(t):
    """[(outer, bytes)] for the base64 (std / url, any padding, wrapped), base32 (any case / padding), base32hex and
    Z85 byte layers `t` strictly parses as. Z85 keeps trailing NULs (a UTF-16LE tail is `xx 00`). Never raises."""
    if isinstance(t, (bytes, bytearray)):
        t = bytes(t).decode("ascii", "replace")
    if not isinstance(t, str):
        return []
    flat = re.sub(r"\s+", "", t)
    if not 4 <= len(flat) <= 400000:
        return []
    out = []
    core = flat.rstrip("=")
    if re.fullmatch(r"[A-Za-z0-9+/\-_]+", core) and len(core) % 4 != 1:
        try:
            out.append(("base64", base64.b64decode(_b64pad(core.replace("-", "+").replace("_", "/")), validate=True)))
        except (ValueError, TypeError):
            pass
    up = core.upper()
    if len(up) % 8 in (0, 2, 4, 5, 7):
        for name, ok, tr in (("base32", r"[A-Z2-7]+", None), ("base32hex", r"[0-9A-V]+", _UNB32HEX)):
            if re.fullmatch(ok, up):
                try:
                    out.append((name, base64.b32decode((up.translate(tr) if tr else up) + "=" * (-len(up) % 8))))
                except (ValueError, TypeError):
                    pass
    if len(flat) % 5 == 0 and all(c in _UNZ85 for c in flat):
        z = bytearray()
        for i in range(0, len(flat), 5):
            v = 0
            for c in flat[i:i + 5]:
                v = v * 85 + _UNZ85[c]
            if v > 0xFFFFFFFF:
                z = None
                break
            z += v.to_bytes(4, "big")
        if z:
            out.append(("z85", bytes(z)))
    return out


def wide_dec(t, form=None):
    """Text under a wide-outer layer of UTF-16 (or any unicode_form) bytes -> the printable-ASCII text, else None.
    The NUL-rhythm / BOM sniff is the gate (a UTF-8 base64 blob never reads); form: accept only that sniffed form."""
    for _o, b in wide_reads(t):
        r = unicode_form(b)
        if r and (form is None or r[0] == form):
            return r[1]
    return None


_have = {c[0] for c in CANDIDATES}
CANDIDATES += [(f"{outer}({form})", (lambda f, o: lambda s: wide_enc(s, f, o))(form, outer),
                (lambda f: lambda t: wide_dec(t, f))(form))
               for form in _WIDE_FORMS for outer in _WIDE_OUTERS if f"{outer}({form})" not in _have]
del _have


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
        out += _xorkey_cands((k,))
        if len(k) <= 8:   # columnar transposition keyed by a title/prompt word
            out.append((f"columnar:{k}", (lambda k: lambda s: col_enc(s, k))(k), (lambda k: lambda t: col_dec(t, k))(k)))
            out.append((f"columnar-x:{k}", (lambda k: lambda s: col_enc(s, k, "x"))(k),
                        (lambda k: lambda t: col_dec(t, k, "x"))(k)))
            out.append((f"columnar-letters:{k}", (lambda k: lambda s: col_letters_enc(s, k))(k), None))
    for k in _redef_hint_orders(hints):   # redefence keyed by a prompt digit / word key, every offset
        out += [(_redef_name(k, o), (lambda k, o: lambda s: redefence_enc(s, k, o))(k, o),
                 (lambda k, o: lambda t: redefence_dec(t, k, o))(k, o)) for o in range(2 * len(k) - 2)]
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


# ------------------------------------------- transposition over a strict encoding (speculative, D16-18 stack cue)
# D16-17 stacked two layers, D18 introduced the rail fence: the next day may transpose a strict encoding or encode a
# transposed sentence. (A) outer transposition: a base64 / base32 / hex / Morse(-hex) string that refuses to decode
# (or decodes to junk): every keyless transposition (reverse, rails 2-20 x offset, scytale, columnar, route, ...; each
# inverted and composed with reversal) is undone on the string, gated on the first 12 chars equalling the strict
# encoding of the crib, then the strict decode must read crib + slug. (B) inner transposition: a strict decode that
# yields an anagram of the sentence -> rail / redefence / transposition / skip solvers (each anagram-gated).
def _tps_mhex_enc(s):
    return " ".join(_MORSE[c.upper()] for c in _u(s).hex())


def _tps_mhex_dec(t):
    if not re.fullmatch(r"[.\- ]+", t.strip()):
        raise ValueError("not morse-hex")
    return _t(bytes.fromhex("".join(_UNMORSE[x] for x in t.split())))


def _tps_morse_tight(s):
    return "/".join(" ".join(_MORSE.get(c.upper(), "") for c in w if c.upper() in _MORSE) for w in s.split(" "))


_B64A = frozenset(string.ascii_letters + string.digits + "+/=")
_TPS_STRICT = (   # (name, enc, dec, alphabet, fold for the prefix compare)
    ("base64", lambda s: base64.b64encode(_u(s)).decode(),
     lambda t: _t(base64.b64decode(_b64pad(t), validate=True)), _B64A, None),
    ("base64url", lambda s: base64.urlsafe_b64encode(_u(s)).decode().rstrip("="),
     lambda t: _t(base64.urlsafe_b64decode(_b64pad(t.rstrip("=")))), frozenset(string.ascii_letters + string.digits
                                                                               + "-_="), None),
    ("base32", lambda s: base64.b32encode(_u(s)).decode(), lambda t: _t(base64.b32decode(t.upper())),
     frozenset(string.ascii_letters + "234567="), str.upper),
    ("hex", lambda s: _u(s).hex(), lambda t: _t(bytes.fromhex(t)), frozenset(string.hexdigits), str.lower),
    ("morse-hex", _tps_mhex_enc, _tps_mhex_dec, frozenset(".- "), None),
    ("morse", morse_enc, morse_text_dec, frozenset(".-/ "), None),
)
_TPS_INNER = (   # strict decoders tried before an anagram-gated transposition solve: (name, enc, dec)
    [(n, e, d) for n, e, d, _a, _f in _TPS_STRICT if n != "morse"]
    + [("binary8", lambda s: " ".join(f"{b:08b}" for b in _u(s)), lambda t: _t(bytes(int(x, 2) for x in _toks(t)))),
       ("decimal", lambda s: " ".join(str(b) for b in _u(s)), lambda t: _t(bytes(int(x) for x in _toks(t))))])


@functools.lru_cache(maxsize=None)
def _tps_pre(i):
    _n, enc, _d, _a, fold = _TPS_STRICT[i]
    x = enc(_CRIB)[:12]
    return fold(x) if fold else x


def _tps_cheap(L):
    """[(tier, name, P, Q)] reverse / rails / scytale only (long Morse strings: the full family list costs ~0.5 s)."""
    out = [(0, "reverse", list(range(L))[::-1])]
    for n, o in rail_keys(L):
        rows = _rail_rows(L, n, o)
        out.append((0, f"rail{n}" + (f"-off{o}" if o else ""), sorted(range(L), key=rows.__getitem__)))
    for m in range(2, min(20, L - 1) + 1):
        out.append((0, f"scytale{m}", [i for c in range(m) for i in range(c, L, m)]))
    res = []
    for tier, name, P in out:
        Q = [0] * L
        for j, i in enumerate(P):
            Q[i] = j
        res.append((tier, name, P, Q))
    return res


_tps_cheap_c = functools.lru_cache(maxsize=16)(_tps_cheap)


def _tps_perm(name, L):
    for _tier, n, P, _Q in _tps_cheap_c(L):
        if n == name:
            return P
    return next((P for _t, n, P in _tp_families(L) if n == name), None)


def _tps_tenc(name, sfx):
    """Encoder of a solved (transposition family, composition) on any string (cheap families rebuilt directly)."""
    def enc(s):
        L = len(s)
        if "+rev-in" in sfx:
            s = s[::-1]
        P = _tps_perm(name, L)
        if P is None:
            return None
        if "-inv" in sfx:
            Q = [0] * L
            for j, i in enumerate(P):
                Q[i] = j
            P = Q
        c = _tp_apply(s, P)
        return c[::-1] if "+rev-out" in sfx else c
    return enc


def _tps_read(i, c):
    """The sentence when strict decoder i reads c as crib + slug, else None (Morse: case-free, template recased)."""
    name, _e, dec, _a, _f = _TPS_STRICT[i]
    x = safe(dec, c.strip() if name != "morse" else c)
    if not x:
        return None
    x = x.strip()
    crib = _CRIB.lower() if name == "morse" else _CRIB
    if x.startswith(crib) and SLUG.fullmatch(x[len(crib):]):
        return _CRIB + x[len(crib):]
    return None


def _tps_outer(t, t0, budget):
    import time
    L = len(t)
    chars = set(t)
    encs = [i for i, (_n, _e, _d, a, _f) in enumerate(_TPS_STRICT) if chars <= a and L > 12]
    if not encs:
        return None
    pres = [(i, _tps_pre(i), _TPS_STRICT[i][4]) for i in encs]
    tr = t[::-1]
    keys = _tp_keys(L) if L <= 400 else _tps_cheap_c(L)
    for _tier, name, P, Q in keys:
        if time.monotonic() - t0 > budget:
            return None
        for sfx, X in (("", Q), ("-inv", P)):
            heads = (("", "".join([t[j] for j in X[:12]])), ("+rev-out", "".join([tr[j] for j in X[:12]])),
                     ("+rev-in", "".join([t[X[L - 1 - k]] for k in range(12)])))
            for s2, h in heads:
                for i, pre, fold in pres:
                    if (fold(h) if fold else h) != pre:
                        continue
                    c = _tp_apply(tr if s2 == "+rev-out" else t, X)
                    c = c[::-1] if s2 == "+rev-in" else c
                    got = _tps_read(i, c)
                    if got:
                        sname, senc = _TPS_STRICT[i][0], _TPS_STRICT[i][1]
                        if sname == "morse":   # word gap ' / ' or bare '/' (CyberChef): the one keeping t's multiset
                            senc = next((e for e in (morse_enc, _tps_morse_tight) if sorted(e(got)) == sorted(t)),
                                        senc)
                        tenc = _tps_tenc(name, sfx + s2)
                        return (f"{name}{sfx}{s2}({sname})", got, (lambda tenc, senc: lambda s: tenc(senc(s)))(tenc, senc))
    return None


def _tps_inner(t, t0, budget):
    import time
    for name, enc, dec in _TPS_INNER:
        if time.monotonic() - t0 > budget:
            return None
        x = safe(dec, t)
        if not x or len(x) < len(_TP_HEAD) + 8 or x.startswith(_CRIB):
            continue
        left = max(0.05, budget - (time.monotonic() - t0))
        r = rail_solve(x) or redefence_solve(x) or riffle_solve(x) or transposition_solve(x, left) or skip_solve(x, left)
        if r and r[1].startswith(_CRIB):
            return (f"{name}({r[0]})", r[1], (lambda enc, tenc: lambda s: enc(tenc(s)))(enc, r[2]))
    return None


def tpstrict_solve(blob, budget=0.6):
    """(name, sentence, enc) when the blob is the warmups sentence under a keyless transposition of a strict encoding
    (name 'rail5-off2(base64)') or a strict encoding of a transposed sentence ('hex(rail5-off2)'), else None. Both
    gates need the strict decode to read the crib + a slug. Never raises; <= `budget` seconds."""
    import time
    try:
        t0 = time.monotonic()
        t = _t(blob).strip("\r\n")
        if "\n" in t.strip() or len(t) < 16:
            return None
        return _tps_inner(t.strip(), t0, budget / 2) or _tps_outer(t, t0, budget)
    except Exception:  # noqa: BLE001
        return None


def tpstrict_dec(t):
    r = tpstrict_solve(t)
    return r[1] if r else None


def _tps_frag_read(name, dec, c):
    x = safe(dec, c if name == "morse" else c.strip())
    if not x or not x.strip() or not x.isascii():
        return None
    if name == "morse":
        x = _recase(x) or ""
    return x if _crib_piece(x.strip()) >= 4 else None


def tpstrict_free(p, k=3, budget=0.1):
    """Mastery fragment mode: a line = reverse / rail / scytale of a strict encoding of a sentence piece. Kept only
    when the strict decode is a crib piece of >= 4 confirmed characters (_crib_piece). Never raises."""
    import time
    try:
        t0 = time.monotonic()
        t = p.rstrip("\r\n")
        st = t.strip()
        L = len(st)
        encs = [(n, d) for n, _e, d, a, _f in _TPS_STRICT if set(st) <= a]
        if L < 8 or L > 600 or not encs:
            return []
        hits = []
        for src in dict.fromkeys((st, t)):
            Ls = len(src)
            sr = src[::-1]
            for _tier, _name, P, Q in _tps_cheap_c(Ls):
                if time.monotonic() - t0 > budget:
                    break
                for X in (Q, P):
                    c = _tp_apply(src, X)
                    for cc in (c, _tp_apply(sr, X), c[::-1]):
                        if cc == src:
                            continue
                        for n, d in encs:
                            x = _tps_frag_read(n, d, cc)
                            if x and x not in hits:
                                hits.append(x)
                if len(hits) >= k:
                    break
        return sorted(hits, key=lambda x: -_crib_piece(x.strip()))[:k]
    except Exception:  # noqa: BLE001
        return []


# --------------------------------------- transposition stacked with a letter map (speculative, coverage atlas target)
# rail3(rot13), atbash(rail5-off2), rot47(scytale4), caesar7(rail3), ...: a per-character letter map commutes with any
# transposition, so the order is irrelevant to decoding. Cue: the crib multiset test fails on the blob but passes once a
# map is undone -> undo that map, then the keyless transposition solvers. Only the map that restores 'Nice work' plus a
# slug's hyphens and digits is tried; the plain (untransposed) map is left to the DAYS / caesarN entries.
def _maptp_maps():
    """[(name, enc, dec)] letter maps, the FREE_CODECS ones first, then every other Caesar shift."""
    out = [("rot13", lambda s: rot(s, 13), lambda t: rot(t, 13)), ("atbash", atbash, atbash),
           ("caesar7", lambda s: rot(s, 7), lambda t: rot(t, -7)), ("rot47", rot47, rot47)]
    out += [(f"caesar{n}", (lambda n: lambda s: rot(s, n))(n), (lambda n: lambda t: rot(t, -n))(n))
            for n in range(1, 26) if n not in (7, 13)]
    return out


_MAPTP_MAPS = _maptp_maps()
_MAPTP_HEAD = collections.Counter(_TP_HEAD.replace(" ", ""))


def _maptp_gate(x):
    """Necessary for any transposition of the sentence: 'Nice work' letters, 2+ hyphens and 2+ digits (slug)."""
    c = collections.Counter(x)
    return (all(c[ch] >= v for ch, v in _MAPTP_HEAD.items()) and c["-"] >= 2
            and sum(c[d] for d in string.digits) >= 2)


def maptp_solve(blob, budget=0.6):
    """(name, sentence, enc) when the blob is the warmups sentence under a letter map (rot13 / atbash / rot47 / any
    Caesar shift) stacked with a keyless transposition (rail / redefence / box / skip families), in either order; name
    'map(transposition)', e.g. 'rot13(rail3)'. Only the reading that starts with the full crib and ends in a slug is
    accepted. Never raises; <= `budget` seconds."""
    import time
    try:
        t0 = time.monotonic()
        t = _t(blob).strip("\r\n")
        if "\n" in t or len(t) < len(_TP_HEAD) + 8 or len(t) > 400:
            return None
        rest = collections.Counter(t)
        rest.subtract(_CRIB if " " in t else _CRIB_NS)
        if min(rest.values()) >= 0:
            return None   # the blob already holds the crib's multiset: a bare transposition, not this family
        for mname, menc, mdec in _MAPTP_MAPS:
            if time.monotonic() - t0 > budget:
                return None
            x = mdec(t)
            if not _maptp_gate(x) or x.strip().startswith(_CRIB):
                continue
            left = max(0.05, budget - (time.monotonic() - t0))
            r = rail_solve(x) or redefence_solve(x) or riffle_solve(x) or transposition_solve(x, left) or skip_solve(x, left)
            if r and r[1].startswith(_CRIB) and SLUG.fullmatch(r[1][len(_CRIB):].strip()):
                return (f"{mname}({r[0]})", r[1], (lambda menc, tenc: lambda s: menc(tenc(s)))(menc, r[2]))
        return None
    except Exception:  # noqa: BLE001
        return None


def maptp_dec(t):
    r = maptp_solve(t)
    return r[1] if r else None


# keyless crib-gated decoder (infer returns the solved map + transposition's encoder; this entry's enc never matches)
CANDIDATES.append(("map-transposition", lambda s: None, maptp_dec))


_MAPTP_CRIB = collections.Counter(_CRIB)


def maptp_free(p, k=3, budget=0.08):
    """Mastery fragment mode: a line = a FREE_CODECS letter map (rot13 / atbash / caesar7 / rot47) over a rail fence /
    keyless transposition of a sentence piece. A map is tried only when its reading's characters fit the sentence's
    (crib counts, plus slug chars [a-z0-9-]); kept only as a crib piece (rail_free / transposition_free). Never raises."""
    import time
    try:
        t0 = time.monotonic()
        t = p.rstrip("\r\n")
        if len(t.strip()) < 4:
            return []
        hits = []
        for _mname, _menc, mdec in _MAPTP_MAPS[:4]:
            if time.monotonic() - t0 > budget:
                break
            x = mdec(t)
            if x == t or any(v > _MAPTP_CRIB[ch] and not (ch.islower() or ch.isdigit() or ch == "-")
                             for ch, v in collections.Counter(x.strip()).items()):
                continue
            for c in rail_free(x) + transposition_free(x, k, max(0.01, budget - (time.monotonic() - t0))):
                if c not in hits and _crib_piece(c.strip()) >= 4:
                    hits.append(c)
        return sorted(hits, key=lambda c: -_crib_piece(c.strip()))[:k]
    except Exception:  # noqa: BLE001
        return []


def infer(plain, blob, hints=()):
    """Today's codec from the Single: (name, enc) of the first encoder E with E(plain) == blob.strip() (exact GM bytes),
    else of the first decoder D with D(blob) == plain, else a fitted affine / learned substitution map. None = no
    candidate explains the blob (the today-probe then reports "unidentified" and builds no case)."""
    if not plain or blob is None:
        return None
    blob = reader_text(blob)
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
            if dec is crib_tok_dec:   # the demo alphabet can't re-encode: hand back the recovered map's encoder
                ct = crib_tok_solve(want)
                return ct[0], ct[2]
            if dec is wordtp_dec:   # one decoder reads every word family: hand back the solved family's encoder
                wt = wordtp_solve(want)
                return wt[0], wt[2]
            if dec is redefence_crib_dec:
                rd = redefence_solve(want, hints)
                return rd[0], rd[2]
            if dec is riffle_crib_dec:
                rf = riffle_solve(want)
                return rf[0], rf[2]
            if dec is frac_crib_dec:
                fs = frac_solve(want)
                return fs[0], fs[2]
            if dec is maptp_dec:
                mt = maptp_solve(want)
                return mt[0], mt[2]
            return name, enc
    st = stack_fit(p, want)
    if st:
        return st
    ab = _fit_affine(p, want)
    if ab:
        a, b = ab
        return f"affine{a},{b}", lambda s: affine(s, a, b)
    cs = crib_solve(want, hints) if p.startswith(_CRIB) else None
    if cs and cs[1] == p:
        return cs[0], cs[2]
    xk = xorkey_solve(want, hints) if p.startswith(_CRIB) else None
    if xk and xk[1] == p:
        return xk[0], xk[2]
    pf = playfair_solve(want, hints) if p.startswith(_CRIB) else None
    if pf and pf[1] == p:
        return pf[0], pf[2]
    ss = subst_solve(want) if p.startswith(_CRIB) else None
    if ss and ss[1] == p:
        return ss[0], ss[2]
    ts = transposition_solve(want) if p.startswith(_TP_HEAD) else None
    if ts and ts[1] == p:
        return ts[0], ts[2]
    sk = skip_solve(want) if p.startswith(_TP_HEAD) else None
    if sk and sk[1] == p:
        return sk[0], sk[2]
    wt = wordtp_solve(want) if p.startswith(_CRIB) else None
    if wt and wt[1] == p:
        return wt[0], wt[2]
    tps = tpstrict_solve(want) if p.startswith(_CRIB) else None
    if tps and tps[1] == p:
        return tps[0], tps[2]
    mt = maptp_solve(blob) if p.startswith(_CRIB) else None   # unstripped: a rail may start with a space
    if mt and mt[1] == p:
        return mt[0], mt[2]
    dc = dcol_solve(blob, hints) if p.startswith(_CRIB) else None
    if dc and dc[1] == p:
        return dc[0], dc[2]
    sub = _fit_subst(p, want)
    if sub:
        return "subst", lambda s: "".join(sub.get(c, c) for c in s)
    return None


def plaintext(blob, slug, deadline=None, hints=()):
    """The Single's decoded sentence holding `slug`: lib.decode.decode_chunk -> peel -> every candidate decoder -> the
    fixed warmups sentence (identical D1-D13, so an unknown codec can still be fitted against it)."""
    from lib import decode
    text = reader_text(blob)
    if not slug:
        return None
    try:
        d = decode.decode_chunk(text.strip())
    except Exception:  # noqa: BLE001
        d = None
    if d and slug in d:
        u7 = utf7_dec(d.strip())   # UTF-7 keeps the slug readable: `warmup+ACE To` only reads as the template decoded
        return u7.strip() if u7 and _TPL in u7 and _TPL not in d and slug in u7 else d.strip()
    # strict (crib + slug, anagram-gated): before the loose `slug in` decoders below
    rs = rail_solve(text) or redefence_solve(text, hints) or riffle_solve(text) or transposition_solve(text) or skip_solve(text)
    if rs and slug in rs[1]:
        return rs[1]
    wt = wordtp_solve(text)
    if wt and slug in wt[1]:
        return wt[1]
    tps = tpstrict_solve(text)   # a transposed strict encoding / a strict encoding of a transposed sentence
    if tps and slug in tps[1]:
        return tps[1]
    mt = maptp_solve(text)   # a letter map (rot13 / atbash / rot47 / Caesar) stacked with a transposition
    if mt and slug in mt[1]:
        return mt[1]
    dc = dcol_solve(text, hints)   # Myszkowski / double columnar keyed by title / prompt words
    if dc and slug in dc[1]:
        return dc[1]
    for _l, _i, x in inner_reads(text):   # strict (printable ASCII, not a UTF-8 read): before the slow peel
        if slug in x:
            return x.strip()
    try:
        out, _steps = decode.peel(_u(text), lambda t: slug in t, max_nodes=4000, deadline=deadline)
    except Exception:  # noqa: BLE001
        out = None
    if out and slug in out:
        return out.strip()
    st = stack_dec(text)
    if st and slug in st:
        return st
    for _name, _enc, dec in CANDIDATES:
        if dec is not None:
            got = safe(dec, text.strip())
            if got and slug in got:
                return got.strip()
    cs = crib_solve(text, hints)
    if cs and slug in cs[1]:
        return cs[1]
    xk = xorkey_solve(text, hints)
    if xk and slug in xk[1]:
        return xk[1]
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
    blob = blob_text(art.read_bytes())
    hints = tuple(hints) + tuple(str(contract.get(k) or "") for k in ("name", "prompt"))
    plain = plaintext(blob, slug, hints=hints)
    if not plain:
        return None
    got = infer(plain, blob, hints)
    if not got:
        return None
    return got[0], got[1], plain


# ------------------------------------------- three-layer stacks of confirmed codecs (depth-3 peel of the DAYS codecs)
# "Morse -> hex -> base64", "base64 -> hex -> rot13": a blob under 3 stacked GM-confirmed codecs (outermost peeled
# first). CANDIDATES' chained pairs cover depth 2 and plaintext()'s 4000-node lib.decode.peel (25 rot-N per node) stalls
# near depth 2 and lacks Atbash / rot47 / octal / entities / Morse, so this is a BFS over the DAYS decoders plus a
# case-free Morse text layer: each step keeps only printable text that is new, a self-inverse layer never repeats
# back-to-back, and a chain holds at most 2 free (letter-only) layers. A full blob is accepted only as printable
# one-line text ending in a slug; a Mastery fragment only as a piece of the warmups template (or its tail + slug chars).
_STACK_INV = {"rot13", "reverse", "atbash", "rot47", "swapcase"}
_STACK_END = re.compile(r"[a-z]+(?:-[a-z]+)+-\d{2,}$")


def _stack_morse(t):
    x = morse_text_dec(t)
    return [x.upper(), x] if x else []


def _stack_layers():
    out = [(name, free, (lambda d: lambda t: [x for x in (safe(d, t),) if x])(dec)) for _d, name, _e, dec, free in DAYS]
    # swapcase: a free letter layer outside the DAYS (swapcase over base64; swapcase(base32) = lowercase base32)
    return out + [("morse", False, _stack_morse),
                  ("swapcase", True, lambda t: [t.swapcase()] if any(c.isalpha() for c in t) else [])]


def _stack_encs():
    out = {name: enc for _d, name, enc, _dec, _f in DAYS}
    out["morse"] = morse_enc
    out["swapcase"] = str.swapcase
    return out


def stack_reads(t, accept, depth=3, budget=0.4, strict_first=False):
    """[(chain, text)] for every <= `depth`-layer stack of DAYS decoders turning `t` into text `accept` takes, shortest
    chain first; chain = layer names, outermost first (strict_first: the outermost is a format layer, not a letter
    map). Never raises; stops after `budget` seconds."""
    import time
    if not isinstance(t, str) or not t.strip():
        return []
    end = time.time() + budget
    layers = _stack_layers()
    found, seen, frontier = [], {t}, [(t, (), 0)]
    for _ in range(depth):
        nxt = []
        for cur, path, nfree in frontier:
            for name, free, fn in layers:
                if (path and path[-1] == name and name in _STACK_INV) or (free and (nfree >= 2 or strict_first
                                                                                     and not path)):
                    continue
                if time.time() > end:
                    return found
                try:
                    outs = fn(cur)
                except Exception:  # noqa: BLE001 - a layer that doesn't apply
                    continue
                for o in outs:
                    if not o or o in seen:
                        continue
                    seen.add(o)
                    p2 = path + (name,)
                    try:
                        if accept(o):
                            found.append((p2, o))
                    except Exception:  # noqa: BLE001
                        pass
                    nxt.append((o, p2, nfree + free))
        frontier = nxt
    return found


def _stack_full(x):
    x = x.strip()
    return bool(_STACK_END.search(x)) and x.isprintable()


def stack_dec(t):
    """The decoded sentence of a <=3-layer DAYS stack (template-bearing reading first), else None."""
    r = stack_reads(_t(t).strip(), _stack_full) if isinstance(t, (str, bytes, bytearray)) else []
    return next((x.strip() for _c, x in r if _TPL in x), r[0][1].strip() if r else None)


def _stack_apply(s, chain, encs):
    for n in reversed(chain):
        s = encs[n](s)
    return s


def stack_fit(plain, blob):
    """(name, enc) of the stack whose re-encoding of `plain` is exactly `blob` (else the first that decodes to it)."""
    encs = _stack_encs()
    hits = [c for c, x in stack_reads(_t(blob).strip(), lambda x: x.strip() == plain.strip())]
    for chain in hits:
        try:
            if _stack_apply(plain, chain, encs).strip() == _t(blob).strip():
                return "stack:" + ">".join(chain), (lambda s, chain=chain: _stack_apply(s, chain, encs))
        except Exception:  # noqa: BLE001
            continue
    if hits:
        chain = hits[0]
        return "stack:" + ">".join(chain), (lambda s, chain=chain: _stack_apply(s, chain, encs))
    return None


def _stack_frag(x):
    if len(x) < 4 or not x.isprintable():
        return False
    if x in _TPL:
        return True
    m = re.search(r"[a-z0-9-]*$", x)
    head = x[:m.start()]
    if head:
        return m.end() > m.start() and _TPL.endswith(head)
    return "-" in x


@functools.lru_cache(maxsize=4096)
def _stack_free(p):
    from lib.decode import _bigram
    r = [x for c, x in stack_reads(p, _stack_frag, budget=0.03, strict_first=True) if len(c) >= 2]
    return tuple(sorted(dict.fromkeys(r), key=lambda x: (x not in _TPL, -_bigram(x)))[:4])


def stack_free(p):
    """Speculative Mastery-line decoder: a 2-3 layer stack fragment (outermost a format layer) -> its template / slug
    readings, template pieces first, then the most English slug reading."""
    return list(_stack_free(p.strip())) if isinstance(p, str) and p.strip() else []


# --------------------------------------------------------------------- speculative free-text decoders for lib.decode
def _top(p, outs, k=3):
    from lib.decode import _bigram
    seen = []
    for o in outs:
        if o and o != p and o not in seen:
            seen.append(o)
    return sorted(seen, key=_bigram, reverse=True)[:k]


# ------------------------------------------------- endian word swap (byte order flipped, no BOM)
# "The little one goes first" generalised: the UTF-8 bytes cut into w-byte words (w = 2/4/8) and every word
# byte-reversed = a little-endian dump of big-endian words (`od -tx4` on x86, `dd conv=swab`, objcopy --reverse-bytes,
# perl pack("V*", unpack("N*"))), then hex ('Nice' -> '694e6563' at w=2, '6563694e' at w=4). Tail: NUL-padded to a
# whole word (od / most writers), or the short tail word reversed on its own (a naive per-chunk [::-1]). The whole
# buffer reversed is the DAYS chains hex(reverse) / reverse(hex) in CANDIDATES; the free decoder reads those too.
_WSWAP = (2, 4, 8)


def wordswap(b, w):
    """b with every w-byte word byte-reversed; a short tail word is reversed on its own."""
    return b"".join(b[i:i + w][::-1] for i in range(0, len(b), w))


def wordswap_enc(s, w, fmt="hex", pad=True):
    """Text -> its UTF-8 bytes word-swapped (NUL-padded to whole words when pad) as fmt: hex / hex-upper / words
    (od -tx<w> style: one lowercase hex word per token) / base64."""
    b = _u(s)
    if pad and len(b) % w:
        b += b"\0" * (w - len(b) % w)
    x = wordswap(b, w)
    if fmt == "words":
        return " ".join(x[i:i + w].hex() for i in range(0, len(x), w))
    if fmt == "base64":
        return base64.b64encode(x).decode()
    return x.hex().upper() if fmt == "hex-upper" else x.hex()


def _wsw_bytes(t):
    """The bytes under a hex blob (whitespace / 0x / : , - separators), else under strict base64, else None."""
    if not isinstance(t, str):
        return None
    x = re.sub(r"0[xX]|[\s:,-]", "", t)
    if len(x) >= 4 and not len(x) % 2 and re.fullmatch(r"[0-9a-fA-F]+", x):
        return bytes.fromhex(x)
    x = re.sub(r"\s", "", t)
    if len(x) >= 8 and not len(x) % 4 and re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", x):
        try:
            return base64.b64decode(x, validate=True)
        except ValueError:
            return None
    return None


def _wsw_text(b):
    """Printable UTF-8 text of b (pad NULs stripped at both ends), else None."""
    b = b.strip(b"\0")
    try:
        s = b.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if s and all(c.isprintable() or c in "\n\t" for c in s) and _texty(s) >= 0.85 else None


def wordswap_dec(t, w, pad=True):
    """Undo wordswap_enc(., w, *, pad) for any of its formats -> text, else None. Gated: the bytes must not already
    read as better English unswapped (a plain hex line is not a word-swapped one)."""
    try:
        b = _wsw_bytes(t)
        if b is None or (pad and len(b) % w):
            return None
        s = _wsw_text(wordswap(b, w))
        if s is None:
            return None
        from lib.decode import _bigram
        raw = _wsw_text(b)
        return s if raw is None or _bigram(s) > _bigram(raw) else None
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return None


def wordswap_reads(t):
    """[(variant, text)] for a hex/base64 blob under a byte-order flip, most English first: w-byte word swaps
    (w = 2/4/8; NUL pad or short reversed tail; a fragment cut mid-word re-aligned at every offset, the partial head /
    tail words dropped), the reversed byte buffer, and the reversed hex text (nibble + byte reversal)."""
    from lib.decode import _bigram
    b = _wsw_bytes(t)
    if b is None or len(b) < 3:
        return []
    raw = _wsw_text(b)
    base = _bigram(raw) if raw is not None else -99.0
    reads = []
    for w in _WSWAP:
        if len(b) < w:
            continue
        for o in range(w):
            body = b[o:]
            if o:
                body = body[:len(body) - len(body) % w]
            s = _wsw_text(wordswap(body, w))
            if s:
                reads.append((f"wswap{w}" + (f"@{o}" if o else ""), s))
    s = _wsw_text(b[::-1])
    if s:
        reads.append(("revbytes", s))
    x = re.sub(r"0[xX]|[\s:,-]", "", t)
    if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", x):
        s = _wsw_text(bytes.fromhex(x[::-1]))
        if s:
            reads.append(("revhex", s))
    def crib(s):   # crib characters the read confirms (a whole crib substring, or a crib tail + slug piece)
        return len(s) if len(s) >= 4 and s in SENTENCE.replace("{slug}", "") else _crib_piece(s)
    reads = [(v, s, crib(s)) for v, s in reads if s != raw]
    reads = [(v, s) for v, s, k in sorted(reads, key=lambda r: (r[2], round(_texty(r[1]), 2), _bigram(r[1])),
                                          reverse=True) if k or _bigram(s) > base]
    return reads


def wordswap_free(p):
    """Speculative Mastery-line decoder: the byte-order-flip readings of a hex/base64 line (the slug/template picks)."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for s in list(dict.fromkeys(s for _v, s in wordswap_reads(p.strip())))[:4]]
    except Exception:   # noqa: BLE001
        return []


_have = {n for n, _e, _d in CANDIDATES}
CANDIDATES += [(f"wswap{w}-{fmt}" + ("" if pad else "-rawtail"),
                (lambda w, f, p: lambda s: wordswap_enc(s, w, f, p))(w, fmt, pad),
                (lambda w, p: lambda t: wordswap_dec(t, w, p))(w, pad))
               for w in _WSWAP for fmt, pad in (("hex", True), ("hex", False), ("hex-upper", True), ("words", True),
                                                ("base64", True))
               if f"wswap{w}-{fmt}" not in _have]
del _have



# ------------------------------------------------- nibble-swapped hex (each byte's two hex digits exchanged)
# 'Nice' = 4e 69 63 65 -> e4 96 36 56 (perl unpack "h*", CyberChef "Rotate left 4" + To Hex, ((b & 15) << 4) | b >> 4).
# Cue: ASCII text puts 2/6/7 in the LOW nibble (space = 02, a-o = x6, p-z = x7). Byte order is kept; the reversed hex
# text (nibbles swapped AND bytes reversed) is the reverse(hex) candidate / wordswap revhex -- the free decoder offers
# both, crib/English ranked. Tokens: one run, or split by whitespace : , - with optional 0x / \x prefixes.
_NIBSWAP_FMT = {
    "hex": lambda h: "".join(h),
    "hex-upper": lambda h: "".join(h).upper(),
    "hex-spaced": lambda h: " ".join(h),
    "hex-spaced-upper": lambda h: " ".join(h).upper(),
    "hex-colon": lambda h: ":".join(h),
    "0x": lambda h: " ".join("0x" + x for x in h),
    "escaped": lambda h: "".join("\\x" + x for x in h),
}


def nibswap(b):
    return bytes(((x & 15) << 4) | (x >> 4) for x in b)


def nibswap_enc(s, fmt="hex"):
    return _NIBSWAP_FMT[fmt]([f"{x:02x}" for x in nibswap(_u(s))])


def _nibswap_bytes(t):
    """The raw bytes of a hex line (one run or 2-digit tokens, 0x / \\x prefixes), else None."""
    if not isinstance(t, str):
        return None
    t = t.strip().strip("\"'[]()")
    x = re.sub(r"0[xX]|\\x|[\s:,-]", "", t)
    toks = [y for y in re.split(r"[\s:,-]+", re.sub(r"0[xX]|\\x", " ", t)) if y]
    if len(x) < 8 or len(x) % 2 or not re.fullmatch(r"[0-9a-fA-F]+", x):
        return None
    if len(toks) > 1 and any(len(y) % 2 for y in toks):
        return None
    return bytes.fromhex(x)


def _nibswap_text(b):
    try:
        out = b.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        return None
    if not out or any(unicodedata.category(c) in ("Cc", "Cn", "Co", "Cs") and c not in "\t\n\r" for c in out):
        return None
    return out


def nibswap_dec(t):
    """The text under nibble-swapped hex, else None (not hex, odd digits, non-UTF-8 / control-char read)."""
    try:
        b = _nibswap_bytes(t)
        return None if b is None else _nibswap_text(nibswap(b))
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return None


def nibswap_reads(t):
    """[(variant, text)] for a hex line read nibble-swapped ("nibswap") and as reversed hex text ("revhex": nibbles
    swapped + byte order reversed), crib pieces first then English-looking; reads the plain hex already explains
    (a printable plain-hex reading that scores better) are dropped."""
    from lib.decode import _bigram
    b = _nibswap_bytes(t)
    if b is None:
        return []
    raw = _nibswap_text(b)
    base = _bigram(raw) if raw is not None and _texty(raw) >= 0.9 else -99.0
    reads = [(v, s) for v, s in (("nibswap", _nibswap_text(nibswap(b))), ("revhex", _nibswap_text(nibswap(b)[::-1])))
             if s and s != raw]

    def crib(s):
        return len(s) if len(s) >= 4 and s in SENTENCE.replace("{slug}", "") else _crib_piece(s)
    reads = [(v, s, crib(s)) for v, s in reads]
    return [(v, s) for v, s, k in sorted(reads, key=lambda r: (r[2], round(_texty(r[1]), 2), _bigram(r[1])),
                                         reverse=True) if k or (_texty(s) >= 0.9 and _bigram(s) > base)]


def nibswap_free(p):
    """Speculative Mastery-line decoder: the nibble-swapped / reversed-hex readings of a hex line."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for _v, s in nibswap_reads(p.strip())][:2]
    except Exception:   # noqa: BLE001
        return []


_have = {n for n, _e, _d in CANDIDATES}
CANDIDATES += [(f"nibswap-{fmt}", (lambda f: lambda s: nibswap_enc(s, f))(fmt), nibswap_dec)
               for fmt in _NIBSWAP_FMT if f"nibswap-{fmt}" not in _have]
del _have


# ------------------------------------------------- wide-int char codes (2-4 chars packed per 16/32/64-bit integer)
# "Two bytes as numbers": the UTF-8 bytes cut into w-byte words (w = 2/4; NUL-padded tail) and each word written as ONE
# integer, little- or big-endian -- decimal ('Ni' = 26958 LE / 20073 BE; `od -tu2`, struct.unpack('<H')), a 0x C-array
# (`0x6563694e, ...` = uint32 LE; also u64), or 8w-bit binary groups. Width from the tokens (0x digits / binary group
# length / the largest value); a decimal line of byte-sized values only is plain char codes, never this. The last word
# loses its NUL pad (either end: an unpadded short BE tail is `\0x`); a NUL anywhere else, a non-UTF-8 or unprintable
# read is rejected. Bare no-0x hex words are the wswap family above.
_WINT_W = (2, 4)
_WINT_FMTS = ("dec", "dec-comma", "c-array", "c-array-space", "c-array-upper", "bin")
_WINT_TOK = re.compile(r"[\s,;]+")


def wint_enc(s, w=2, order="little", fmt="dec"):
    """Text -> its UTF-8 bytes (NUL-padded to whole w-byte words) as one integer per word in `fmt`."""
    b = _u(s)
    b += b"\0" * (-len(b) % w)
    vs = [int.from_bytes(b[i:i + w], order) for i in range(0, len(b), w)]
    if fmt == "bin":
        return " ".join(format(v, f"0{8 * w}b") for v in vs)
    if fmt.startswith("c-array"):
        xs = [f"0x{v:0{2 * w}X}" if fmt.endswith("upper") else f"0x{v:0{2 * w}x}" for v in vs]
        return (" " if fmt.endswith("space") else ", ").join(xs)
    return (", " if fmt == "dec-comma" else " ").join(map(str, vs))


def _wint_parse(t):
    """(kind, width, [ints]) for a token line of 0x hex / 16-64-bit binary / multi-byte decimal ints, else None.
    A `{...}` / `[...]` C or JSON array body is unwrapped; C integer suffixes (u, U, L) are dropped."""
    if not isinstance(t, str):
        return None
    t = t.strip()
    m = re.search(r"[{\[]([^{}\[\]]*)[}\]]", t)
    if m and ("{" in t or t.startswith("[")):
        t = m.group(1)
    toks = [x for x in _WINT_TOK.split(t.strip()) if x]
    if not toks or len(toks) > 20000:
        return None
    if all(re.fullmatch(r"0[xX][0-9a-fA-F]{1,16}[uUlL]{0,3}", x) for x in toks):
        hx = [x[2:].rstrip("uUlL") for x in toks]
        vs = [int(h, 16) for h in hx]
        dig = max(map(len, hx))
        w = next((k for k in (2, 4, 8) if dig <= 2 * k), None)
        return ("hex", w, vs) if w and (dig > 2 or max(vs) > 255) else None
    if all(re.fullmatch(r"[01]+", x) for x in toks):
        n = {len(x) for x in toks}
        return ("bin", len(toks[0]) // 8, [int(x, 2) for x in toks]) if len(n) == 1 and n & {16, 32, 64} else None
    if all(re.fullmatch(r"\d{1,20}", x) for x in toks):
        vs = [int(x) for x in toks]
        mx = max(vs)
        if mx <= 255:
            return None   # byte-sized char codes: the decimal codec, not packed words
        w = next((k for k in (2, 4, 8) if mx < 256 ** k), None)
        return ("dec", w, vs) if w else None
    return None


def _wint_text(vs, w, order):
    """The text under ints vs as w-byte words in `order`; pad NULs of the last word stripped, else None."""
    if any(v >= 256 ** w for v in vs):
        return None
    words = [v.to_bytes(w, order) for v in vs]
    words[-1] = words[-1].strip(b"\0")
    b = b"".join(words)
    if not b or b"\0" in b:
        return None
    try:
        s = b.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if all(c.isprintable() or c in "\n\t" for c in s) and _texty(s) >= 0.85 else None


def wint_reads(t):
    """[(variant, text)] for a packed-int char-code line, both byte orders, crib / most English read first.
    variant = u{8w}{le|be}-{dec|hex|bin}."""
    try:
        got = _wint_parse(t)
        if not got:
            return []
        kind, w, vs = got
        reads = []
        for order in ("little", "big"):
            s = _wint_text(vs, w, order)
            if s:
                reads.append((f"u{8 * w}{'le' if order == 'little' else 'be'}-{kind}", s))
        if len(reads) > 1:
            from lib.decode import _bigram
            reads.sort(key=lambda r: (_crib_piece(r[1]), _bigram(r[1])), reverse=True)
        return reads
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []


def wint_dec(t, w=None, order=None):
    """Undo wint_enc (any fmt) -> text, else None; w / order ('little' / 'big') pin the variant."""
    tag = None if w is None else f"u{8 * w}" + ("" if order is None else "le" if order == "little" else "be")
    for v, s in wint_reads(t):
        if tag is None or v.startswith(tag):
            return s
    return None


def wint_free(p):
    """Speculative Mastery-line decoder: the packed-int readings of a line (both byte orders, best first)."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for _v, s in wint_reads(p)][:2]
    except Exception:   # noqa: BLE001
        return []


_have = {n for n, _e, _d in CANDIDATES}
CANDIDATES += [(f"u{8 * w}{'le' if o == 'little' else 'be'}-{fmt}",
                (lambda w, o, f: lambda s: wint_enc(s, w, o, f))(w, o, fmt),
                (lambda w, o: lambda t: wint_dec(t, w, o))(w, o))
               for w in _WINT_W for o in ("little", "big") for fmt in _WINT_FMTS
               if f"u{8 * w}{'le' if o == 'little' else 'be'}-{fmt}" not in _have]
del _have

# ------------------------------------------------- hexdump tool output (xxd / od / hexdump rows)
# The artifact is a dump tool's text, one row per line: `xxd` (`00000000: 4e69 6365 ...  Nice work decodi`; -e = 32-bit
# LE words, a short tail word right-aligned; -b = 8-bit binary, 6 bytes a row; -i = a `0x4e, ` C array), `od` (7-digit
# octal offsets, no gutter: -x / -tx4 = native LE 16/32-bit words, -o / -d = LE 16-bit octal / decimal words, -b / -tu1
# = bytes, -c / -a = 4-wide char cells with `\n` / `303` escapes / named controls; a closing total-length offset row)
# and `hexdump` (default = od -x with hex offsets, -C = bytes + `|...|` gutter, -c = cells). `*` = the previous row
# repeated up to the next offset. The gutter prints '.' for every non-printable byte: the hex is authoritative, the
# gutter only picks between readings (xxd -g4 vs -e). Offsets fix the radix (16/8/10) and cut the padding (od -x NUL
# tail word, hexdump -c blank cells). Bytes -> UTF-8 text, else unicode_form_dec (UTF-16/32, BOM or not).
_HD_ROW = re.compile(r"\s*([0-9a-fA-F]{4,16})(:?)(?=\s|$)")
_HD_NAMES = {n: i for i, n in enumerate("nul soh stx etx eot enq ack bel bs ht nl vt ff cr so si dle dc1 dc2 dc3 dc4 "
                                        "nak syn etb can em sub esc fs gs rs us".split())}
_HD_NAMES.update(sp=32, de=127)
_HD_NAMES["del"] = 127
_HD_ESC = {"\\0": 0, "\\a": 7, "\\b": 8, "\\t": 9, "\\n": 10, "\\v": 11, "\\f": 12, "\\r": 13, "\\\\": 92}
_HD_FMTS = ("xxd", "xxd-e", "xxd-b", "xxd-i", "hexdump-C", "hexdump", "hexdump-c", "od-x", "od-tx4", "od-c", "od-b",
            "od-o", "od-d", "od-tu1")


def _hd_gut(b):
    return "".join(chr(c) if 32 <= c < 127 else "." for c in b)


def hexdump_enc(s, fmt="xxd"):
    """Text -> its UTF-8 bytes as the dump tool `fmt` prints them (a _HD_FMTS name; GNU/uutils od, util-linux
    hexdump, vim xxd on x86; no `*` row folding)."""
    b = _u(s)
    rows = []
    if fmt == "xxd-i":
        return ",\n".join("  " + ", ".join(f"0x{c:02x}" for c in b[i:i + 12]) for i in range(0, len(b), 12))
    if fmt.startswith("xxd"):
        n, g = (6, 1) if fmt == "xxd-b" else (16, 4) if fmt == "xxd-e" else (16, 2)
        for o in range(0, len(b), n):
            r = b[o:o + n]
            if fmt == "xxd-b":
                cells = [f"{c:08b}" for c in r]
            elif fmt == "xxd-e":
                cells = [r[i:i + g][::-1].hex().rjust(2 * g) for i in range(0, len(r), g)]
            else:
                cells = [r[i:i + g].hex() for i in range(0, len(r), g)]
            width = (8 if fmt == "xxd-b" else 2 * g) * (n // g) + n // g - 1
            rows.append(f"{o:08x}: " + " ".join(cells).ljust(width) + "  " + _hd_gut(r))
        return "\n".join(rows)
    hexoff = fmt.startswith("hexdump")
    for o in range(0, len(b), 16):
        r = b[o:o + 16]
        if fmt == "hexdump-C":
            area = "".join((f"{r[i]:02x} " if i < len(r) else "   ") + (" " if i == 7 else "") for i in range(16))
            rows.append(f"{o:08x}  {area} |{_hd_gut(r)}|")
            continue
        if fmt in ("od-c", "hexdump-c"):
            cells = []
            for c in r:
                e = {0: "\\0", 7: "\\a", 8: "\\b", 9: "\\t", 10: "\\n", 11: "\\v", 12: "\\f", 13: "\\r"}.get(c)
                cells.append((e or (chr(c) if 32 <= c < 127 else f"{c:03o}")).rjust(4))
            if fmt == "hexdump-c":
                cells += ["    "] * (16 - len(r))
            rows.append((f"{o:07x}" if hexoff else f"{o:07o}") + "".join(cells))
            continue
        w = {"od-tx4": 4, "od-b": 1, "od-tu1": 1}.get(fmt, 2)
        r += b"\0" * (-len(r) % w)
        vs = [int.from_bytes(r[i:i + w], "little") for i in range(0, len(r), w)]
        spec = {"od-tx4": "08x", "od-b": "03o", "od-tu1": "3d", "od-o": "06o", "od-d": "5d"}.get(fmt, "04x")
        line = "".join(" " + format(v, spec) for v in vs)
        rows.append((f"{o:07x}" + line.ljust(40)) if hexoff else f"{o:07o}" + line)
    rows.append(f"{len(b):08x}" if fmt == "hexdump-C" else f"{len(b):07x}" if hexoff else f"{len(b):07o}")
    return "\n".join(rows)


def _hd_split(body):
    """xxd row body -> (hex part, gutter|None): the first run of 2+ spaces after which exactly n gutter chars follow
    (n = the bytes the hex part holds, as hex digit pairs or as 8-bit binary groups)."""
    for m in re.finditer(r" {2,}", body):
        head, tail = body[:m.start()], body[m.start() + 2:]
        toks = head.split()
        if not toks or not all(re.fullmatch(r"[0-9a-fA-F]+", x) for x in toks):
            continue
        ns = [sum(len(x) // 2 for x in toks)]
        if all(re.fullmatch(r"[01]{8}", x) for x in toks):
            ns.insert(0, len(toks))
        for n in ns:
            if 0 < n <= len(tail) and not tail[:-n].strip(" "):
                return head, tail[-n:]
    return body, None


def _hd_rows(t):
    """['*' | (offset, colon, body, gutter|None)] for every non-blank line of t, else None (a non-dump line)."""
    rows = []
    for ln in t.splitlines():
        if not ln.strip():
            continue
        if ln.strip() == "*":
            rows.append("*")
            continue
        m = _HD_ROW.match(ln)
        if not m:
            return None
        body, gut = ln[m.end():], None
        if m.group(2):
            body, gut = _hd_split(body)
        else:
            for a, z in ("|", "|"), (">", "<"):   # hexdump -C / od -tx1z gutter
                if a in body and body.rstrip().endswith(z):
                    i = body.index(a)
                    body, gut = body[:i], body[i + 1:body.rstrip().rfind(z)]
                    break
        rows.append((m.group(1), bool(m.group(2)), body, gut))
    return rows if any(r != "*" and r[2].strip() for r in rows) else None


def _hd_cells(body):
    """od -c / -a / hexdump -c body -> bytes (4-wide right-aligned cells), else None."""
    body = body.ljust(-(-len(body) // 4) * 4)
    out = bytearray()
    for i in range(0, len(body), 4):
        cell = body[i:i + 4]
        c = cell.strip(" ")
        if cell[0] != " " and cell.strip():
            return None
        if not c:
            out.append(32)
        elif c in _HD_ESC:
            out.append(_HD_ESC[c])
        elif re.fullmatch(r"[0-3][0-7]{2}", c):
            out.append(int(c, 8))
        elif len(c) == 1:
            out += c.encode("utf-8")
        elif c in _HD_NAMES:
            out.append(_HD_NAMES[c])
        else:
            return None
    return bytes(out)


def _hd_modes(toks, colon):
    """[(mode, token -> bytes, pad byte)] the token shapes of a dump allow, the tool's default reading first."""
    if not toks:
        return []
    modes = []
    if all(re.fullmatch(r"[01]{8}", x) for x in toks) and colon:
        modes.append(("bits", lambda x: bytes([int(x, 2)]), 0))
    if all(re.fullmatch(r"[0-9a-fA-F]+", x) and not len(x) % 2 for x in toks):
        L = max(map(len, toks))
        be = ("hex", lambda x: bytes.fromhex(x), 0)
        if L == 2:
            modes.append(be)
        elif L in (4, 8, 16):
            le = ("hex-le", lambda x: bytes.fromhex(x)[::-1], 0)
            modes += [be, le] if colon else [le, be]
    if all(re.fullmatch(r"[0-3][0-7]{2}", x) for x in toks):
        modes.append(("oct1", lambda x: bytes([int(x, 8)]), 0))
    for k, w in ((6, 2), (11, 4)):
        if all(re.fullmatch(r"[0-7]{%d}" % k, x) for x in toks) and max(int(x, 8) for x in toks) < 256 ** w:
            modes.append((f"oct{w}-le", (lambda w: lambda x: int(x, 8).to_bytes(w, "little"))(w), 0))
    if all(re.fullmatch(r"-?\d{1,5}", x) for x in toks):
        vs = [int(x) for x in toks]
        if all(-128 <= v <= 255 for v in vs):
            modes.append(("dec1", lambda x: bytes([int(x) % 256]), 0))
        if all(-32768 <= v <= 65535 for v in vs) and any(v > 255 or v < -128 for v in vs):
            modes.append(("dec2-le", lambda x: (int(x) % 65536).to_bytes(2, "little"), 0))
    return modes


def _hd_join(rows, datas, radix, pad):
    """Rows' bytes stitched by their offsets in `radix` (`*` repeats filled, a padded tail cut), else None."""
    out, prev, star, base = bytearray(), b"", False, None
    for r, d in zip(rows, datas):
        if r == "*":
            star = True
            continue
        if radix:
            try:
                o = int(r[0], radix)
            except ValueError:
                return None
            base = o if base is None else base
            want = o - base
            if want < 0 or want > 1 << 22:
                return None
            if star and prev:
                while len(out) + len(prev) <= want:
                    out += prev
            star = False
            if len(out) > want:
                if any(c != pad for c in out[want:]):
                    return None
                del out[want:]
            elif len(out) < want:
                if pad != 32 or want - len(out) > 3:
                    return None
                out += b" " * (want - len(out))   # a trailing space cell lost to rstrip
        out += d
        prev = d or prev
    return bytes(out)


def _hd_text(b):
    """Printable text of dump bytes: UTF-8 (pad NULs off, one trailing newline off), else a sniffed Unicode form."""
    if not b:
        return None
    s = _wsw_text(b) or unicode_form_dec(b) or unicode_form_dec(b.rstrip(b"\0"))
    return s.rstrip("\r\n") or None if s else None


def _hd_carray(t):
    """xxd -i C array (`unsigned char x[] = { 0x4e, ... }; unsigned int x_len = N;` or the bare stdin body) -> bytes."""
    m = re.search(r"\{([^{}]*)\}", t)
    body, ln = (m.group(1), None) if m else (t, None)
    if m:
        k = re.fullmatch(r"\s*(?:(?:static\s+)?(?:const\s+)?unsigned\s+char\s+\w+\s*\[\s*\d*\s*\]\s*=\s*)?;?\s*"
                         r"(?:(?:static\s+)?(?:const\s+)?unsigned\s+int\s+\w+\s*=\s*(\d+)\s*;\s*)?",
                         t[:m.start()] + t[m.end():])
        if not k:
            return None
        ln = k.group(1)
    toks = [x for x in re.split(r"[\s,]+", body) if x]
    if len(toks) < 2 or "," not in body or not all(re.fullmatch(r"0[xX][0-9a-fA-F]{2}", x) for x in toks):
        return None
    b = bytes(int(x, 16) for x in toks)
    return b if ln is None or int(ln) == len(b) else None


def hexdump_reads(t):
    """[(mode, text)] for a dump tool's output (any of _HD_FMTS, a lone row or a `*`-folded dump), best first: the
    gutter-consistent reading, then the crib, then the tool's default byte order, then the most English. Never raises."""
    try:
        t = _t(t)
        if not isinstance(t, str) or not t.strip() or len(t) > 2000000:
            return []
        if "0x" in t or "0X" in t:
            b = _hd_carray(t)
            s = _hd_text(b) if b else None
            return [("c-array", s)] if s else []
        rows = _hd_rows(t)
        if not rows:
            return []
        data = [r for r in rows if r != "*"]
        colon = any(r[1] for r in data)
        guts = [r[3] for r in data]
        toks = [x for r in data for x in r[2].split()]
        modes = [(m, f, p, False) for m, f, p in _hd_modes(toks, colon)]
        if not colon and all(g is None for g in guts):
            modes.append(("cells", None, 32, True))
        radixes = [16] if colon or any(g is not None for g in guts) else [16, 8, 10]
        if len(data) == 1:
            radixes = [None]
        from lib.decode import _bigram
        reads = []
        for pri, (mode, f, pad, cells) in enumerate(modes):
            datas = []
            for r in rows:
                if r == "*":
                    datas.append(b"")
                    continue
                d = _hd_cells(r[2]) if cells else b"".join(f(x) for x in r[2].split())
                if d is None:
                    break
                datas.append(d)
            else:
                for radix in radixes:
                    b = _hd_join(rows, datas, radix, pad)
                    if b is None:
                        continue
                    s = _hd_text(b)
                    if s is None:
                        break
                    rd = [d for r, d in zip(rows, datas) if r != "*"]
                    gok = all(g is None or g == _hd_gut(d) for g, d in zip(guts, rd))
                    reads.append(((gok, _crib_piece(s), -pri, _bigram(s)), mode, s))
                    break
        reads.sort(key=lambda r: r[0], reverse=True)
        return [(m, s) for _k, m, s in reads]
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []


def hexdump_dec(t):
    """The text under a dump tool's output (xxd / od / hexdump, any _HD_FMTS layout), else None."""
    r = hexdump_reads(t)
    return r[0][1] if r else None


def hexdump_free(p):
    """Speculative Mastery-line decoder: the readings of one dump row (offset + words/bytes/cells + gutter)."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        return [s for _m, s in hexdump_reads(p)][:2]
    except Exception:   # noqa: BLE001
        return []


_have = {n for n, _e, _d in CANDIDATES}
CANDIDATES += [(f"hexdump-{fmt}" if not fmt.startswith("hexdump") else fmt,
                (lambda f: lambda s: hexdump_enc(s, f))(fmt), hexdump_dec)
               for fmt in _HD_FMTS if fmt not in _have and f"hexdump-{fmt}" not in _have]
del _have

# raw wide artifact read by a UTF-8-replace reader (NULs + ASCII survive): decoder-only use (infer() reads BYTES first)
CANDIDATES += [(f"raw-{form}", (lambda f: lambda s: raw_wide_enc(s, f))(form), wide_text_dec)
               for form in ("utf-16le-bom", "utf-16le", "utf-16be-bom", "utf-16be", "utf-32le-bom", "utf-32be-bom")]

# ------------------------------------------------- LEB128 / protobuf varint char codes ("Little-Endian Base 128")
# Each char code as one varint: 7 value bits a byte, low group first, high bit set on every non-final byte, written as
# hex. Value = the code point (UTF-32), each UTF-16 code unit (astral = surrogate pair) or each UTF-8 byte; as unsigned
# uLEB128 / protobuf uint32 (Go binary.AppendUvarint), protobuf sint32 zigzag (2v; Go binary.AppendVarint -- every char
# >= '@' takes 2 bytes) or DWARF/wasm signed sLEB128 (chars 0x40-0x7f take 2 bytes). ASCII uLEB is byte-for-byte plain
# hex, so a read needs >= 1 multi-byte value AND bytes that are not themselves printable UTF-8 (plain hex owns those).
# Hex as one run, byte tokens (space , : - separated, optional 0x / \x per byte) in either case.
_LEB_KINDS = ("zigzag", "uleb", "sleb")
_LEB_UNITS = ("cp", "utf16", "utf8")


def _leb_vals(s, unit):
    if unit == "utf8":
        return list(_u(s))
    if unit == "utf16":
        b = s.encode("utf-16-le")
        return [int.from_bytes(b[i:i + 2], "little") for i in range(0, len(b), 2)]
    return [ord(c) for c in s]


def _leb_one(v, kind):
    if kind == "zigzag":
        v = 2 * v if v >= 0 else -2 * v - 1
    out = bytearray()
    while True:
        b = v & 0x7f
        v >>= 7
        if kind == "sleb":
            if (v == 0 and not b & 0x40) or (v == -1 and b & 0x40):
                return bytes(out + bytes([b]))
        elif not v:
            return bytes(out + bytes([b]))
        out.append(b | 0x80)


def leb_enc(s, kind="zigzag", unit="cp", fmt="hex"):
    """Text -> one LEB128 varint per char code, hex: fmt hex (one run) / hex-space / HEX-space (upper tokens)."""
    b = b"".join(_leb_one(v, kind) for v in _leb_vals(s, unit))
    if fmt == "hex":
        return b.hex()
    return " ".join(f"{x:02X}" if fmt.startswith("HEX") else f"{x:02x}" for x in b)


def _leb_bytes(t):
    """The bytes of a hex line (one run / byte tokens, optional 0x or \\x per byte), else None."""
    if not isinstance(t, str):
        return None
    t = t.strip()
    if not t or len(t) > 60000:
        return None
    t = re.sub(r"\\x|0[xX](?=[0-9a-fA-F]{2})", " ", t)
    toks = [x for x in re.split(r"[\s,:;\-]+", t) if x]
    if not toks or not all(re.fullmatch(r"(?:[0-9a-fA-F]{2})+", x) for x in toks):
        return None
    if len(toks) > 1 and any(len(x) != 2 for x in toks):
        return None
    return bytes.fromhex("".join(toks))


def _leb_stream(b, kind):
    """[values] of a whole varint stream (no dangling continuation byte, <= 5 bytes a value), multi-byte flag."""
    from lib.binary import _leb
    vs, p, multi = [], 0, False
    while p < len(b):
        v, q = _leb(b, p, signed=kind == "sleb", cap=5)
        multi |= q - p > 1
        if kind == "zigzag":
            v = (v >> 1) ^ -(v & 1)
        vs.append(v)
        p = q
    return vs, multi


def _leb_text(vs, unit):
    if any(v < 0 for v in vs):
        return None
    try:
        if unit == "utf8":
            s = bytes(vs).decode("utf-8")
        elif unit == "utf16":
            s = b"".join(v.to_bytes(2, "little") for v in vs).decode("utf-16-le")
        else:
            s = "".join(map(chr, vs))
            s.encode("utf-8")
    except (ValueError, OverflowError):
        return None
    if not s.strip() or not all(c.isprintable() or c in "\n\t" for c in s):
        return None
    return s if _crib_piece(s) or _texty(s) >= 0.85 else None


def leb_reads(t):
    """[(variant, text)] for a hex line of LEB128 varint char codes, crib / most English read first.
    variant = leb128-{zigzag|uleb|sleb}-{cp|utf16|utf8}."""
    try:
        b = _leb_bytes(t)
        if not b:
            return []
        try:
            plain = b.decode("utf-8")
            if all(c.isprintable() or c in "\n\t" for c in plain):
                return []   # printable UTF-8 as it stands: the plain hex codec's line
        except UnicodeDecodeError:
            pass
        reads, seen = [], set()
        for kind in _LEB_KINDS:
            try:
                vs, multi = _leb_stream(b, kind)
            except (IndexError, ValueError):
                continue
            if not multi:
                continue
            for unit in _LEB_UNITS:
                s = _leb_text(vs, unit)
                if s and (kind, s) not in seen:
                    seen.add((kind, s))
                    reads.append((f"leb128-{kind}-{unit}", s))
        if len(reads) > 1:
            from lib.decode import _bigram
            reads.sort(key=lambda r: (_crib_piece(r[1]), _bigram(r[1])), reverse=True)
        return reads
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []


def leb_dec(t, kind=None):
    """Undo leb_enc (any kind/unit/fmt) -> text, else None; kind pins zigzag / uleb / sleb."""
    for v, s in leb_reads(t):
        if kind is None or v.split("-")[1] == kind:
            return s
    return None


def leb_free(p):
    """Speculative Mastery-line decoder: the LEB128 varint readings of a hex line (best first)."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for _v, s in leb_reads(p)][:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES += [(f"leb128-{k}" + ("" if u == "cp" else f"-{u}") + ("" if f == "hex" else f"-{f}"),
                (lambda k, u, f: lambda s: leb_enc(s, k, u, f))(k, u, f),
                (lambda k: lambda t: leb_dec(t, k))(k))
               for k in ("zigzag", "sleb", "uleb") for u in ("cp", "utf16")
               for f in ("hex", "hex-space", "HEX-space") if not (k == "uleb" and u == "utf16")]


# ------------------------------------------------- GSM 03.38 7-bit packed septets (SMS PDU user data) / generic 7-bit
# Each char as a 7-bit septet, 8 septets per 7 octets. GSM order (3GPP TS 23.038 6.1.2.1.1): bit stream LSB-first per
# octet, septet n at bit 7n, GSM default alphabet (ASCII positions for letters/digits/space and ! " # % & ' ( ) * + , - .
# / : ; < = > ?; '@' = 0x00, ESC 0x1B -> extension table). Generic MSB-first packing: the 7-bit ASCII codes run together
# big-endian, zero-padded to whole octets. Cue: hex ~7/8 the plain-hex length whose bytes are not printable text. A
# trailing all-zero / CR (GSM fill) septet in exactly 7 spare bits is padding. Hex: one run or byte tokens.
_GSM7 = ("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
         "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà")
_GSM7_EXT = {0x0A: "\f", 0x14: "^", 0x28: "{", 0x29: "}", 0x2F: "\\", 0x3C: "[", 0x3D: "~", 0x3E: "]", 0x40: "|",
             0x65: "€"}
_GSM7_IDX = {c: i for i, c in enumerate(_GSM7) if i != 0x1B}
_GSM7_XIDX = {c: i for i, c in _GSM7_EXT.items()}
_GSM7_FMTS = ("hex", "HEX", "hex-space", "HEX-space")
_GSM7_SPLIT = re.compile(r"[ .,!?:'-]+")
_GSM7_WORD = re.compile(r"[A-Za-z]?[a-z]*|\d+")   # a short (Mastery fragment) read must be word-shaped


def _gsm7_septets(s, order):
    out = []
    for c in s:
        if order == "msb":
            if ord(c) > 0x7F:
                return None
            out.append(ord(c))
        elif c in _GSM7_IDX:
            out.append(_GSM7_IDX[c])
        elif c in _GSM7_XIDX:
            out += [0x1B, _GSM7_XIDX[c]]
        else:
            return None
    return out


def gsm7_enc(s, order="lsb", fmt="hex"):
    """order lsb = GSM 03.38 SMS packing (GSM alphabet), msb = generic big-endian 7-bit ASCII packing."""
    v = _gsm7_septets(s, order)
    if v is None:
        return None
    if order == "msb":
        bits = "".join(f"{x:07b}" for x in v)
        bits += "0" * (-len(bits) % 8)
        b = int(bits, 2).to_bytes(len(bits) // 8, "big") if bits else b""
    else:
        acc = n = 0
        b = bytearray()
        for x in v:
            acc |= x << n
            n += 7
            while n >= 8:
                b.append(acc & 0xFF)
                acc >>= 8
                n -= 8
        if n:
            b.append(acc)
        b = bytes(b)
    h = b.hex().upper() if fmt.startswith("HEX") else b.hex()
    return " ".join(h[i:i + 2] for i in range(0, len(h), 2)) if fmt.endswith("space") else h


def _gsm7_unpack(b, order):
    if order == "msb":
        bits = bin(int.from_bytes(b, "big"))[2:].zfill(8 * len(b))
        v = [int(bits[i:i + 7], 2) for i in range(0, len(bits) - 6, 7)]
    else:
        acc = int.from_bytes(b, "little")
        v = [(acc >> (7 * i)) & 0x7F for i in range(len(b) * 8 // 7)]
    if len(b) * 8 % 7 == 0 and v and v[-1] in (0, 0x0D):
        v.pop()   # 7 spare bits: zero / CR fill, not a char
    if order == "msb":
        return "".join(map(chr, v))
    out, i = [], 0
    while i < len(v):
        if v[i] == 0x1B:
            if i + 1 >= len(v) or v[i + 1] not in _GSM7_EXT:
                return None
            out.append(_GSM7_EXT[v[i + 1]])
            i += 2
        else:
            out.append(_GSM7[v[i]])
            i += 1
    return "".join(out)


def gsm7_reads(t):
    """[(order, text)] readings of a packed-septet line (GSM LSB-first, then MSB-first ASCII), else []."""
    try:
        if not isinstance(t, str) or len(t) > 60000:
            return []
        b = _leb_bytes(t)
        if not b or len(b) < 2:
            return []
        try:   # bytes that are themselves printable text belong to plain hex
            if all(c.isprintable() or c in "\t\n\r" for c in b.decode("utf-8")):
                return []
        except UnicodeDecodeError:
            pass
        out = []
        for order in ("lsb", "msb"):
            s = _gsm7_unpack(b, order)
            if s and len(s) >= 4 and all(" " <= c <= "~" for c in s) and _texty(s) >= 0.9 and (
                    len(s) >= 16 or all(_GSM7_WORD.fullmatch(w) for w in _GSM7_SPLIT.split(s))):
                out.append((order, s))   # GM text is ASCII: a GSM-only glyph (£ é Δ ...) = a wrong read
        return out
    except Exception:   # noqa: BLE001
        return []


def gsm7_dec(t, order=None):
    """Undo gsm7_enc (any fmt) -> text, else None; order pins lsb (GSM) / msb (generic)."""
    for o, s in gsm7_reads(t):
        if order is None or o == order:
            return s
    return None


def gsm7_free(p):
    """Speculative Mastery-line decoder: the packed-septet readings of a hex line."""
    if not isinstance(p, str) or not p.strip():
        return []
    lead = p[:len(p) - len(p.lstrip())]
    return [lead + s for _o, s in gsm7_reads(p)][:2]


CANDIDATES += [(("gsm7" if o == "lsb" else "pack7-msb") + ("" if f == "hex" else f"-{f}"),
                (lambda o, f: lambda s: gsm7_enc(s, o, f))(o, f), (lambda o: lambda t: gsm7_dec(t, o))(o))
               for o in ("lsb", "msb") for f in _GSM7_FMTS]


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
    ("riffle", riffle_free),
    ("bifid", frac_free),
    ("affine", lambda p: _top(p, [affine_inv(p, a, b) for a in _AFFINE_A for b in range(26)])),
    ("columnar", lambda p: [b for b in (col_solve(p),) if b]),
    ("transposition", transposition_free),
    ("word-transposition", wordtp_free),
    ("skip", skip_free),
    ("tp-strict", tpstrict_free),
    ("map-transposition", maptp_free),
    ("punycode", lambda p: [p[:len(p) - len(p.lstrip())] + puny_dec(p)]),
    ("braille", lambda p: [b for b in (braille_dec(p),) if b]),
    ("braille-hex", lambda p: braille_hex_reads(p) or [b for b in (braille_ascii_hex_dec(p),) if b]),
    ("polybius6-hex", lambda p: [b for b in (polybius6_dec(p), tap6_dec(p)) if b]),
    ("morse-layer", morse_layer_free),
    ("morse", morse_free),
    ("morse-timing", morse_timing_free),
    ("nato-layer", nato_layer_free),
    ("spelled-digits", spelled_free),
    ("baudot", baudot_free),
    ("base45", b45_free),
    ("z85", z85_free),
    ("base100", b100_free),
    ("css-hex", css_hex_free),
    ("iching", iching_free),
    ("trigram-octal", trigram_free),
    ("upsidedown", upside_free),
    ("leet", lambda p: [b for b in (leet_dec(p),) if b]),
    ("multitap", lambda p: [b for b in (multitap_dec(p),) if b]),
    ("stack3", stack_free),
    ("t9", lambda p: [b for b in (t9_dec(p),) if b]),
    ("dtmf", dtmf_free),
    ("regional", regional_free),
    ("unistyle", lambda p: [p[:len(p) - len(p.lstrip())] + b for b in (unistyle_dec(p),) if b]),
    ("codepoint", ucp_free),
    ("inner-bytes", inner_free),
    ("zerowidth", zw_cands),
    ("whitespace", ws_cands),
    ("twosym", twosym_free),
    ("ternary", tern_free),
    ("radix", radix_free),
    ("glyph-radix", glyph_radix_free),
    ("binary4-hex", bin4_free),
    ("bcd", bcd_free),
    ("address", addr_free),
    ("gray", gray_free),
    ("binary-lsb", lsb_free),
    ("roman", roman_free),
    ("chuck-unary", chuck_free),
    ("aphex", aphex_free),
    ("seg7", seg7_free),
    ("crib-token-hex", lambda p: [b for b in (crib_tok_dec(p),) if b]),
    ("dna", dna_free),
    ("polyalpha", crib_fragment),
    ("subst", subst_fragment),
    ("xorkey", xorkey_fragment),
    ("wordswap", wordswap_free),
    ("nibswap-hex", nibswap_free),
    ("wide-int", wint_free),
    ("leb128", leb_free),
    ("hexdump", hexdump_free),
    ("gsm7", gsm7_free),
    ("raw-wide", lambda p: [b for b in (wide_text_dec(p),) if b]),
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
