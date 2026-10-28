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
import binascii
import codecs
import collections
import functools
import gzip
import html
import html.entities
import itertools
import json
import math
import quopri
import os
import re
import string
import struct
import time
import unicodedata
import urllib.parse
import zlib

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


def netstr_dec(t):
    """D24: concatenated netstrings `<len>:<data>,` (len in characters) -> the joined data; raises unless the WHOLE
    text parses (a ',' data char is `1:,,`)."""
    t, out, i = t.strip(), [], 0
    while i < len(t):
        m = re.compile(r"(\d+):").match(t, i)
        j = m.end() if m else -1
        if not m or t[j + int(m.group(1)):j + int(m.group(1)) + 1] != ",":
            raise ValueError("not a netstring run")
        out.append(t[j:j + int(m.group(1))])
        i = j + int(m.group(1)) + 1
    if not out:
        raise ValueError("empty")
    return "".join(out)


_UTOK = re.compile(r"(?:U\+|u\+|\\u|\\U|%u|0x)([0-9A-Fa-f]{2,8})")


def uplus_dec(t):
    """D25: code-point tokens `U+004E U+0069 ...` (also u+/\\u/\\U/%u/0x) separated by whitespace/`,;` -> the text;
    raises unless the WHOLE text is tokens."""
    t = t.strip()
    if not t or not re.fullmatch(r"(?:%s[\s,;]*)+" % _UTOK.pattern, t):
        raise ValueError("not a code-point run")
    return "".join(chr(int(h, 16)) for h in _UTOK.findall(t))


def bf_enc(s):
    """D26: the GM's Brainfuck form -- one cell, per UTF-8 byte the +/- delta from the previous byte then '.'."""
    out, cur = [], 0
    for b in _u(s):
        out.append(("+" * (b - cur) if b > cur else "-" * (cur - b)) + ".")
        cur = b
    return "".join(out)


def bf_dec(t, max_steps=5_000_000):
    """D26: run a Brainfuck program (8-bit wrapping cells, no input) -> its output text; raises unless the WHOLE
    text is Brainfuck with a '+' and a '.' (a Morse run of '-'/'.' is not)."""
    if not re.fullmatch(r"[+\-<>\[\].,\s]+", t) or "." not in t or "+" not in t:
        raise ValueError("not a Brainfuck program")
    c = re.sub(r"[^+\-<>\[\].]", "", t)
    st, jmp = [], {}
    for j, ch in enumerate(c):
        if ch == "[":
            st.append(j)
        elif ch == "]":
            if not st:
                raise ValueError("unbalanced ]")
            k = st.pop()
            jmp[k], jmp[j] = j, k
    if st:
        raise ValueError("unbalanced [")
    tape, p, i, n, out = bytearray(65536), 0, 0, 0, bytearray()
    while i < len(c) and n < max_steps:
        ch = c[i]
        if ch == "+":
            tape[p] = (tape[p] + 1) & 255
        elif ch == "-":
            tape[p] = (tape[p] - 1) & 255
        elif ch == ">":
            p += 1
        elif ch == "<":
            p -= 1
        elif ch == ".":
            out.append(tape[p])
        elif ch == "[" and not tape[p]:
            i = jmp[i]
        elif ch == "]" and tape[p]:
            i = jmp[i]
        i += 1
        n += 1
    return _t(bytes(out))


# D27 "Monkey Business" ("Ook. Ook? Ook! Someone seems chatty."): Ook! = Brainfuck, one token pair per instruction
_OOK = {">": "Ook. Ook?", "<": "Ook? Ook.", "+": "Ook. Ook.", "-": "Ook! Ook!", ".": "Ook! Ook.", ",": "Ook. Ook!",
        "[": "Ook! Ook?", "]": "Ook? Ook!"}
_OOK_INV = {v: k for k, v in _OOK.items()}


def ook_enc(s):
    """D27: the GM's Ook! form -- the D26 one-cell Brainfuck program, each instruction as its `Ook? Ook!` pair, single
    spaces throughout, no trailing newline."""
    return " ".join(_OOK[c] for c in bf_enc(s))


def ook_dec(t):
    """D27: Ook! program -> its output text; raises unless the WHOLE text is an even run of Ook./Ook?/Ook! tokens."""
    toks = re.findall(r"Ook[.?!]", t)
    if not toks or len(toks) % 2 or re.sub(r"Ook[.?!]|\s", "", t):
        raise ValueError("not an Ook! program")
    try:
        prog = "".join(_OOK_INV[toks[i] + " " + toks[i + 1]] for i in range(0, len(toks), 2))
    except KeyError as e:
        raise ValueError("not an Ook! pair") from e
    return bf_dec(prog)


def _gz9f(b):
    """gzip as the GM writes it (D21): zlib wbits 31 (mtime 0, OS 3), level 9 (XFL 2), memLevel 8, Z_FILTERED."""
    c = zlib.compressobj(9, zlib.DEFLATED, 31, 8, zlib.Z_FILTERED)
    return c.compress(b) + c.flush()


def _zl9f(b):
    """zlib as the GM writes it (D22): wbits 15 (header 78 da), level 9, memLevel 8, Z_FILTERED."""
    c = zlib.compressobj(9, zlib.DEFLATED, 15, 8, zlib.Z_FILTERED)
    return c.compress(b) + c.flush()


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
    # D20 "Big Entrance" ("Same bar. This time the big one goes first."): lowercase hex of BOM feff + UTF-16BE, no
    # separators (byte-exact on the Single, TT de73f228 and 98/98 Mastery 91bb3658 line 20)
    (20, "utf16be-hex", lambda s: (b"\xfe\xff" + s.encode("utf-16-be")).hex(),
     lambda t: bytes.fromhex(re.sub(r"\s+", "", t)).decode("utf-16"), False),
    # D21 "Under Pressure" ("A familiar wrapper. Something compressed inside."): std base64 (padded) of gzip -- mtime 0,
    # XFL 2, OS 3, deflate level 9 strategy Z_FILTERED (byte-exact on the Single, TT 4c426659 and 103/103 Mastery
    # 664b2505 line 21; Python's default gzip.compress stream differs on the long sentence)
    (21, "b64-gzip", lambda s: base64.b64encode(_gz9f(_u(s))).decode(),
     lambda t: _t(gzip.decompress(base64.b64decode(_b64pad(t)))), False),
    # D22 "Deflated Ego" ("Another familiar wrapper. This one needs a little inflation."): std base64 (padded) of a zlib
    # stream (78 da), level 9 Z_FILTERED (byte-exact on the Single, TT 2a0bae7a and 108/108 Mastery 6bd39775 line 22)
    (22, "b64-zlib", lambda s: base64.b64encode(_zl9f(_u(s))).decode(),
     lambda t: _t(zlib.decompress(base64.b64decode(_b64pad(t)))), False),
    # D23 "Eighty-Five Alive" ("The alphabet got bigger. Adobe might recognize the neighbors."): Adobe Ascii85 of the
    # UTF-8 bytes, <~ ~> delimiters, no 'y', no wrap (byte-exact on the Single, TT 519a0e26 and 113/113 Mastery
    # d271467d line 23)
    (23, "ascii85-adobe", lambda s: base64.a85encode(_u(s), adobe=True).decode(),
     lambda t: _t(base64.a85decode(re.sub(r"\s+", "", t), adobe=True)), False),
    # D24 "String Theory" ("Count carefully. The comma knows where to stop."): one netstring per character, `1:c,`
    # concatenated, no separators (byte-exact on the Single, TT 6b420728 and 118/118 Mastery 39a9fb2c line 24)
    (24, "netstring", lambda s: "".join(f"1:{c}," for c in s), netstr_dec, False),
    # D25 "You Have a Point": one Unicode code point per character, `U+XXXX` (uppercase hex, >= 4 digits), single
    # spaces (byte-exact on the Single, TT 76bfa85f and 123/123 Mastery 0b1ae1d0 line 25)
    (25, "uplus", lambda s: " ".join(f"U+{ord(c):04X}" for c in s), uplus_dec, False),
    # D26 "Food for Thought": a Brainfuck program printing the text from ONE cell -- per UTF-8 byte the +/- delta from
    # the previous byte, then '.', no separators (byte-exact on the Single, TT 2b70c93f and 256/256 Mastery
    # ca7796e4 line 26)
    (26, "brainfuck", bf_enc, bf_dec, False),
    # D27 "Monkey Business": the D26 Brainfuck program written in Ook! token pairs, single spaces (byte-exact on the
    # Single, TT e0e29c6f and 133/133 Mastery c6135949 line 27)
    (27, "ook", ook_enc, ook_dec, False),
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


# base92 (thenoviceoof / py3base92 / chepy to_base92): 91-symbol alphabet '!' + '#'..'_' + 'a'..'}' (no '"', '`', '~').
# Bits are taken MSB-first: each 13-bit group -> 2 chars (hi = v // 91, lo = v % 91), a trailing <= 6-bit group -> 1
# char, a 7..12-bit tail -> 2 chars (zero-padded to 13). The lone string '~' is the empty input. Strict: any char
# outside the alphabet, a pair > 8191 or a lone tail char > 63 rejects the line.
_B92 = "!" + "".join(map(chr, range(35, 96))) + "".join(map(chr, range(97, 126)))
_UNB92 = {c: i for i, c in enumerate(_B92)}


def b92_enc(s):
    b = _u(s)
    if not b:
        return "~"
    bits = "".join(f"{x:08b}" for x in b)
    out = []
    for i in range(0, len(bits) - len(bits) % 13, 13):
        v = int(bits[i:i + 13], 2)
        out += [_B92[v // 91], _B92[v % 91]]
    tail = bits[len(bits) - len(bits) % 13:]
    if tail and len(tail) < 7:
        out.append(_B92[int(tail.ljust(6, "0"), 2)])
    elif tail:
        v = int(tail.ljust(13, "0"), 2)
        out += [_B92[v // 91], _B92[v % 91]]
    return "".join(out)


def b92_dec(t):
    t = t.strip()
    if t == "~":
        return ""
    if not t or len(t) > 8192:
        raise ValueError("not base92")
    d = [_UNB92[c] for c in t]
    bits = []
    for i in range(0, len(d) - 1, 2):
        v = d[i] * 91 + d[i + 1]
        if v > 8191:
            raise ValueError("base92 pair out of range")
        bits.append(f"{v:013b}")
    if len(d) % 2:
        if d[-1] > 63:
            raise ValueError("base92 tail out of range")
        bits.append(f"{d[-1]:06b}")
    bits = "".join(bits)
    return _t(bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits) - 7, 8)))


# base94 / base95 big-integer text: bytes as one big-endian integer written in radix 94 over '!'..'~' (all printable
# ASCII but space) or radix 95 over ' '..'~' (with space), digit 0 = the lowest code point, leading zero bytes dropped.
# The alphabets cover almost any printable line, so the decoder also demands printable ASCII back (else ValueError).
_B94 = "".join(map(chr, range(33, 127)))
_B95 = "".join(map(chr, range(32, 127)))


def bigalpha_enc(s, alpha):
    n, out, r = int.from_bytes(_u(s), "big"), [], len(alpha)
    while n:
        n, d = divmod(n, r)
        out.append(alpha[d])
    return "".join(reversed(out))


def bigalpha_dec(t, alpha):
    t = t.strip("\r\n") if " " in alpha else t.strip()
    if not t or len(t) > 4096:
        raise ValueError("not big-radix text")
    n, r = 0, len(alpha)
    for c in t:
        n = n * r + alpha.index(c)
    out = _t(n.to_bytes((n.bit_length() + 7) // 8, "big"))
    if not out or not all(" " <= c <= "~" or c in "\t\r\n" for c in out):
        raise ValueError("big-radix reading is not ASCII text")
    return out


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


# Dense Unicode base-N (qntm's base65536 / base32768 / base2048, npm v5/v3/v5; sublee's PyPI base65536; PyPI base2048):
# the bits MSB-first in N-bit groups, each group = one char of a 2^N repertoire (the inclusive code-point ranges
# below, in order); a final short group uses the second repertoire (N-8 bits) and must be the last char. base32768 /
# base2048 pad the tail out with 1-bits (decoder: leftover bits all 1s); base65536 needs no padding (a lone tail byte
# = one char of U+1500..U+15FF) and indexes its repertoire byte-swapped (char = block[b2] + b1). Cue: ~55 (2048: ~80)
# dense CJK / Hangul-like / Indic glyphs for a 110-byte sentence, no spaces. Strict: no stray char, padding checked.
_DENSE = {
    "base65536": (16, "㐀䳿一黿ꄀꏿꔀꗿ\U00010600\U000106ff\U00012000\U000122ff"
                      "\U00013000\U000133ff\U00014400\U000145ff\U00016800\U000169ff\U00020000\U000285ff",
                  "ᔀᗿ"),
    "base32768": (15, "ҠҿԀԟڀڿݠޟ߀ߟကဟႠႿᄀ"
                      "ᅟᆀᆟᇠሿበቿዠዿጠጿᎠᏟᐠᙟ"
                      "ᚠᛟកសᠠᡟᣀᣟᦀᦟ᧠᧿ᨠᨿᯀ"
                      "ᯟᰀᰟᴀᴟ⇠⇿⋀⋟⍀⏟␀␟─❟"
                      "➀➿⠀⥿⦠⦿⨠⩟⪀⪿⫠⭟ⰀⰟⲀ"
                      "ⳟⴀⴟⵀⵟ⺠⻟㇀㇟㐀䶟䷀龿ꀀꑿ"
                      "꒠꒿ꔀꗿꙀꙟꚠꛟ꜀ꝟꞀꞟꡀꡟ",
                  "ƀƟɀʟ"),
    "base2048": (11, "89AZaz\xc6\xc6\xd0\xd0\xd8\xd8\xde\xdf\xe6\xe6\xf0\xf0\xf8\xf8\xfe\xfeĐđĦħ"
                     "ııĸĸŁłŊŋŒœŦŧƀƟƢ"
                     "ƮƱǃǝǝǤǥǶǷȜȝȠȥȴʯ"
                     "ͰͳͶͷͻͽͿͿΑΡΣΩαωϏ"
                     "ϏϗϯϳϳϷϸϺϿЂЂЄІЈЋ"
                     "ЏИКикяђђєіјћџѵѸ"
                     "ҁҊӀӃӏӔӕӘәӠӡӨөӶӷ"
                     "ӺԯԱՖաֆאתװײؠءاؿف"
                     "ي٠٩ٮٯٱٴٹڿہہۃےەە"
                     "ۮۼۿۿܐܐܒܯݍޥޱޱ߀ߪࠀ"
                     "ࠕࡀࡘࡠࡪࢠࢴࢶࢽऄनपरलळ"
                     "वहऽऽॐॐॠॡ०९ॲঀঅঌএ"
                     "ঐওনপরললশহঽঽৎৎৠৡ"
                     "০ৱ৴৹ৼৼਅਊਏਐਓਨਪਰਲ"
                     "ਲਵਵਸਹੜੜ੦੯ੲੴઅઍએઑ"
                     "ઓનપરલળવહઽઽૐૐૠૡ૦"
                     "૯ૹૹଅଌଏଐଓନପରଲଳଵହ"
                     "ଽଽୟୡ୦୯ୱ୷ஃஃஅஊஎஐஒ"
                     "ஓககஙசஜஜஞடணதநபமஹ"
                     "ௐௐ௦௲అఌఎఐఒనపహఽఽౘ"
                     "ౚౠౡ౦౯౸౾ಀಀಅಌಎಐಒನ"
                     "ಪಳವಹಽಽೞೞೠೡ೦೯ೱೲഅ"
                     "ഌഎഐഒഺഽഽൎൎൔൖ൘ൡ൦൸"
                     "ൺൿඅඖකනඳරලලවෆ෦෯ก"
                     "ะาาเๅ๐๙ກຂຄຄງຈຊຊ"
                     "ຍຍດທນຟມຣລລວວສຫອ"
                     "ະາາຽຽເໄ໐໙ໞໟༀༀ༠༳"
                     "ཀགངཇཉཌཎདནབམཛཝཨཪཬྈ"
                     "ྌကဥဧဪဿ၉ၐၕ",
                 "07"),
}


@functools.lru_cache(maxsize=None)
def _dense_tables(name):
    """(bits, [(first, last, base_index, nbits)] sorted by first, {nbits: [(base_index, first, last)]})."""
    bits, main, tail = _DENSE[name]
    ranges, enc = [], {}
    for nb, rep in ((bits, main), (bits - 8, tail)):
        idx = 0
        for a, b in zip(rep[0::2], rep[1::2]):
            ranges.append((ord(a), ord(b), idx, nb))
            enc.setdefault(nb, []).append((idx, ord(a), ord(b)))
            idx += ord(b) - ord(a) + 1
        if idx != 1 << nb:
            raise ValueError(f"{name} repertoire size {idx} != 2^{nb}")
    ranges.sort()
    return bits, ranges, enc


def _dense_z(name, nb, z):
    """Repertoire index for an nb-bit group z (base65536's 16-bit groups are stored byte-swapped)."""
    return ((z & 0xFF) << 8 | z >> 8) if name == "base65536" and nb == 16 else z


def dense_enc(s, name="base65536"):
    bits, _r, enc = _dense_tables(name)
    data = _u(s) if isinstance(s, str) else bytes(s)
    acc, n, out = 0, 0, []

    def put(nb, z):
        i = _dense_z(name, nb, z)
        for base, a, b in enc[nb]:
            if i < base + b - a + 1:
                out.append(chr(a + i - base))
                return
    for byte in data:
        acc, n = acc << 8 | byte, n + 8
        while n >= bits:
            n -= bits
            put(bits, acc >> n)
            acc &= (1 << n) - 1
    if n:
        nb = bits if n > bits - 8 else bits - 8
        put(nb, (acc << (nb - n)) | ((1 << (nb - n)) - 1))   # pad with 1-bits (none for base65536)
    return "".join(out)


def dense_dec(t, name="base65536", raw=False):
    """Bytes under one dense base-N line (raw=True) or its UTF-8 text; ValueError on any stray char / bad tail."""
    import bisect
    bits, ranges, _e = _dense_tables(name)
    t = t.strip()
    if not t or len(t) > 65536:
        raise ValueError(f"not {name}")
    starts = [r[0] for r in ranges]
    acc, n, out = 0, 0, bytearray()
    for k, c in enumerate(t):
        o = ord(c)
        j = bisect.bisect_right(starts, o) - 1
        if j < 0 or o > ranges[j][1]:
            raise ValueError(f"not {name}: {c!r}")
        a, _b, base, nb = ranges[j]
        if nb != bits and k != len(t) - 1:
            raise ValueError(f"{name}: short char before the end")
        i = base + o - a
        z = _dense_z(name, nb, i)
        acc, n = acc << nb | z, n + nb
        while n >= 8:
            n -= 8
            out.append(acc >> n)
            acc &= (1 << n) - 1
    if acc != (1 << n) - 1:
        raise ValueError(f"{name}: padding mismatch")
    return bytes(out) if raw else _t(bytes(out))


def dense_free(p):
    """Speculative free-line base65536 / base32768 / base2048: a line of >= 2 chars, >= 1 non-ASCII, that decodes
    strictly to printable text under one of the three repertoires (the line's leading indent kept)."""
    s = p.strip()
    if len(s) < 2 or s.isascii():
        return []
    lead = p[:len(p) - len(p.lstrip())]
    got = (safe(lambda x, nm=nm: dense_dec(x, nm), s) for nm in _DENSE)
    return [lead + g for g in got if g and g.strip() and any(c.isalpha() for c in g)]


# Base-122 (kevinAlbs/Base122 encode.js; PyPI base122 b122encode): the bytes MSB-first in 7-bit groups, the last one
# zero-padded; a group is one 1-byte UTF-8 char unless it is one of the 6 "illegal" values (NUL \n \r " & \) -> then
# it and the NEXT group share a 2-byte char 110sss1x 10xxxxxx (sss = illegal index, x = the next 7 bits); an illegal
# LAST group is written "shortened" (sss = 7, x = the group itself). Cue: valid UTF-8 of ~1.14 x the byte length
# mixing ASCII and C0 control chars (\t \x0b \x1c ...) with U+0080..U+07FF code points (lead bytes c2-df); no \n \r " &
# \ at all. The artifact may be raw bytes (strip only CR/LF/BOM: \t \x0b \x0c \x1c-\x1f and space are data). Strict:
# no illegal 1-byte char, every 2-byte char of the 110sss1x form with sss != 6, shortened only last, zero pad bits.
_B122_ILL = (0, 10, 13, 34, 38, 92)


def b122_enc(s, raw=False):
    data = _u(s) if isinstance(s, str) else bytes(s)
    nbits = len(data) * 8
    val = int.from_bytes(data, "big") << (-nbits % 7)
    g = [(val >> (7 * k)) & 127 for k in range(-(-nbits // 7) - 1, -1, -1)]
    out, i = [], 0
    while i < len(g):
        b = g[i]
        if b in _B122_ILL:
            sss, nxt = (_B122_ILL.index(b), g[i + 1]) if i + 1 < len(g) else (7, b)
            out.append(chr(0x80 | sss << 8 | nxt))
            i += 2
        else:
            out.append(chr(b))
            i += 1
    t = "".join(out)
    return _u(t) if raw else t


def b122_dec(t, raw=False):
    """Bytes under one Base-122 string / raw UTF-8 bytes (raw=True) or its UTF-8 text; ValueError when it isn't one."""
    if isinstance(t, (bytes, bytearray)):
        t = bytes(t).decode("utf-8")
    t = t.strip("\r\n﻿")
    if not t:
        raise ValueError("empty")
    if not raw and not any(ord(c) > 127 for c in t) and t.isprintable() and " " in t:
        raise ValueError("plain prose, not base122")
    try:
        return _b122_core(t, raw)
    except ValueError:   # a raw artifact read as Latin-1 ("Â\x80" mojibake): re-read its bytes as UTF-8
        if not (any(0xC2 <= ord(c) <= 0xDF for c in t) and max(map(ord, t)) < 256):
            raise
        return _b122_core(t.encode("latin-1").decode("utf-8"), raw)


def _b122_core(t, raw):
    g = []
    for k, c in enumerate(t):
        o = ord(c)
        if o < 128:
            if o in _B122_ILL:
                raise ValueError(f"base122: illegal 1-byte {c!r}")
            g.append(o)
            continue
        sss = o >> 8
        if o > 0x7FF or not o & 0x80 or sss == 6:
            raise ValueError(f"base122: bad 2-byte char {c!r}")
        if sss == 7:
            if k != len(t) - 1 or (o & 127) not in _B122_ILL:
                raise ValueError("base122: shortened char not last")
        else:
            g.append(_B122_ILL[sss])
        g.append(o & 127)
    n = len(g) * 7 // 8
    if -(-n * 8 // 7) != len(g):
        raise ValueError("base122: stray tail group")
    val = 0
    for x in g:
        val = val << 7 | x
    pad = len(g) * 7 - n * 8
    if val & ((1 << pad) - 1):
        raise ValueError("base122: nonzero pad bits")
    out = (val >> pad).to_bytes(n, "big")
    return out if raw else _t(out)


def b122_free(p):
    """Speculative free-line Base-122: a line with a 2-byte (U+0080..U+07FF) or C0-control char that decodes strictly
    to printable text with letters."""
    if not any(ord(c) > 127 or (ord(c) < 32 and c not in "\r\n") for c in p):
        return []
    got = safe(b122_dec, p)
    return [got] if got and got.strip() and any(c.isalpha() for c in got) else []

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
        ("base92", b92_enc, b92_dec),
        ("base94", lambda s: bigalpha_enc(s, _B94), lambda t: bigalpha_dec(t, _B94)),
        ("base95", lambda s: bigalpha_enc(s, _B95), lambda t: bigalpha_dec(t, _B95)),
        ("base45", b45_enc, b45_dec),
        ("z85", z85_enc, z85_dec),
        ("z85-pad", lambda s: z85_enc(s, pad=True), z85_dec),
        ("base100", b100_enc, b100_dec),
        *[(nm, (lambda nm: lambda s: dense_enc(s, nm))(nm), (lambda nm: lambda t: dense_dec(t, nm))(nm))
          for nm in _DENSE],
        ("base122", b122_enc, b122_dec),
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
    cps = cpshift_solve(want) if p.startswith(_CRIB) else None   # exact re-encodable K before glyph-bytes' generic read
    if cps and cps[1] == p and cps[2](p) == want:
        return cps[0], cps[2]
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
            if dec is byteadd_dec:
                ba = byteadd_solve(want)
                return ba[0], ba[2]
            if dec is byterot_dec:
                br = byterot_solve(want)
                return br[0], br[2]
            if dec is cpshift_dec:
                cs_ = cpshift_solve(want)
                return cs_[0], cs_[2]
            if dec is delta_dec:
                dl = delta_solve(want)
                return dl[0], dl[2]
            if dec is invis_dec:
                iv = invis_solve(want)
                return iv[0], iv[2]
            if dec is maptp_dec:
                mt = maptp_solve(want)
                return mt[0], mt[2]
            if dec is keyb64_dec:
                kb = keyb64_solve(want)
                return kb[0], kb[2]
            if dec is decompress_dec:
                dz = decompress_solve(want)
                return dz[0], dz[2]
            if dec is armor_dec:
                ar = armor_solve(want)
                return ar[0], ar[2]
            if dec is scriptmap_dec:
                sm = scriptmap_solve(want)
                return sm[0], sm[2]
            if dec is openssl_dec:
                os_ = openssl_solve(want)
                return os_[0], os_[2] or (lambda s: None)
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
    ba = byteadd_solve(want) if p.startswith(_CRIB) else None
    if ba and ba[1] == p:
        return ba[0], ba[2]
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
    os_ = openssl_solve(want, hints) if hints else None   # passphrase = a title / prompt word
    if os_ and os_[1] == p:
        return os_[0], os_[2] or (lambda s: None)
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
    _zd_learn(hints)
    tc = textcomp_dec(text.strip())   # whole-input text compression (RLE '1N1i..'): a looser stage reads it as junk + slug
    if tc and _TPL in tc and tc.rstrip().endswith(slug):
        return tc.strip()
    lp = lenpfx_dec(text.strip())   # length-prefix frames: the protobuf walk keeps one field, `0eNice ..` reads as text
    if lp and _TPL in lp and slug in lp:
        return lp.strip()
    nd = names_dec(text.strip())   # Unicode character names: strict whole-fragment, ms; the CANDIDATES sweep is seconds away
    if nd and slug in nd:
        return nd.strip()
    try:
        d = decode.decode_chunk(text.strip())
    except Exception:  # noqa: BLE001
        d = None
    if d and slug in d:
        u7 = utf7_dec(d.strip())   # UTF-7 keeps the slug readable: `warmup+ACE To` only reads as the template decoded
        return u7.strip() if u7 and _TPL in u7 and _TPL not in d and slug in u7 else d.strip()
    cu = cuswap_dec(text.strip())   # byte-swapped code-unit escapes: decode_chunk reads them as CJK
    if cu and slug in cu:
        return cu.strip()
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
    xz = xorz_solve(text, hints) if hints else None   # hint-word key over a compressed stream (no-hint: CANDIDATES)
    if xz and slug in xz[1]:
        return xz[1]
    os_ = openssl_solve(text, hints) if hints else None   # OpenSSL envelope keyed by a title / prompt word
    if os_ and slug in os_[1]:
        return os_[1]
    pf = playfair_solve(text, hints)
    if pf and slug in pf[1]:
        return pf[1]
    ss = subst_solve(text)
    if ss and slug in ss[1]:
        return ss[1]
    ks = knob_sweep(text)   # a seen day's codec with one knob turned (byte order, radix, polarity, ...)
    if ks and slug in ks[1]:
        return ks[1]
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


# ------------------------------------------------- middle-endian / PDP-11 32-bit words (2143, 3412)
# PDP-11 stores a 32-bit value as two little-endian 16-bit halves, high half first: 0x0A0B0C0D -> 0b 0a 0d 0c ("2143"
# against big-endian); the other middle-endian (Honeywell 316, ARM FPA doubles) is 0c 0d 0a 0b ("3412"). 'N' as UTF-32
# in PDP order = 00 00 4e 00 (`iconv -t UTF-32BE | dd conv=swab`), in 3412 = 00 4e 00 00 (`iconv -t UTF-32LE | dd
# conv=swab`). Cue: hex whose 4-byte words read neither as utf-32-le nor -be, often a permuted BOM (00 00 ff fe /
# fe ff 00 00). The free decoder tries all 24 byte orders of each word under utf-32-be / utf-16-be / utf-8, crib +
# English ranked; a read must beat the buffer's own plain utf-32/16/8 reading on bigrams (plain text is declined).
_PERM4 = tuple("".join(p) for p in itertools.permutations("1234"))
_PDP_UNITS = {"utf-32": "utf-32-be", "utf-16": "utf-16-be", "utf-8": "utf-8"}


def permute4(b, order):
    """b cut to whole 4-byte words, each word rearranged: output byte k = input byte int(order[k]) - 1."""
    n = len(b) - len(b) % 4
    out = bytearray(n)
    for k, c in enumerate(order):
        out[k::4] = b[int(c) - 1:n:4]
    return bytes(out)


def _perm4_inv(order):
    """The order that undoes permute4(., order)."""
    return "".join(str(order.index(str(k)) + 1) for k in range(1, 5))


def pdp_enc(s, order="2143", unit="utf-32", fmt="hex", bom=False):
    """Text -> its utf-32 / utf-16 / utf-8 big-endian code units (optional BOM, NUL-padded to whole 4-byte words) with
    every 32-bit word in byte order `order`, as hex / hex-upper / words (8-digit groups) / base64."""
    b = (("﻿" if bom else "") + s).encode(_PDP_UNITS[unit])
    b += b"\0" * (-len(b) % 4)
    x = permute4(b, order)
    if fmt == "words":
        return " ".join(x[i:i + 4].hex() for i in range(0, len(x), 4))
    if fmt == "base64":
        return base64.b64encode(x).decode()
    return x.hex().upper() if fmt == "hex-upper" else x.hex()


def _pdp_ok(s):
    """Reads as the (mostly ASCII) English sentence: printable, texty, >= 80 % ASCII (random words decode as CJK)."""
    return bool(s) and all(c.isprintable() or c in "\n\t" for c in s) and _texty(s) >= 0.85 \
        and sum(c < "\x80" for c in s) >= 0.8 * len(s)


def _pdp_text(x, unit):
    """Printable text of the big-endian code units x under unit (leading BOM and pad NULs stripped), else None."""
    try:
        s = x.decode(_PDP_UNITS[unit]).lstrip("﻿").strip("\0")
    except (UnicodeDecodeError, ValueError):
        return None
    return s if _pdp_ok(s) else None


def _pdp_plain(b):
    """b already reads as text in a standard form (utf-32/16 either endianness, BOM or not, or utf-8) -> that text."""
    for enc in ("utf-32-be", "utf-32-le", "utf-16-be", "utf-16-le", "utf-8"):
        try:
            s = b.decode(enc).lstrip("﻿").strip("\0")
        except (UnicodeDecodeError, ValueError):
            continue
        if _pdp_ok(s):
            return s
    return None


def _pdp_better(s, raw):
    """A permuted read s beats the bytes' own plain reading raw (None = not plain text at all) on English bigrams."""
    from lib.decode import _bigram
    return s is not None and s != raw and (raw is None or _bigram(s) > _bigram(raw))


def pdp_dec(t, order="2143", unit="utf-32"):
    """Undo pdp_enc(., order, unit, any fmt, any bom) -> text, else None. Gated: the read must beat the bytes' own
    plain utf-32/16/8 reading (a plain utf-32 line is not a middle-endian dump)."""
    try:
        b = _wsw_bytes(t)
        if b is None or len(b) % 4:
            return None
        s = _pdp_text(permute4(b, _perm4_inv(order)), unit)
        return s if _pdp_better(s, _pdp_plain(b)) else None
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return None


def pdp_reads(t):
    """[(variant, text)] for a hex/base64 blob of whole 4-byte words read under every one of the 24 word byte orders
    (variant 'pdp<order>-<unit>' = the order the words were STORED in), crib first, then most English."""
    from lib.decode import _bigram
    b = _wsw_bytes(t)
    if b is None or len(b) < 4 or len(b) % 4:
        return []
    raw = _pdp_plain(b)
    seen, reads = set(), []
    for order in _PERM4[1:]:   # 1234 = plain big-endian = raw
        x = permute4(b, _perm4_inv(order))
        for unit in _PDP_UNITS:
            s = _pdp_text(x, unit)
            if s not in seen and _pdp_better(s, raw):
                seen.add(s)
                reads.append((f"pdp{order}-{unit}", s))
    def crib(s):
        return len(s) if len(s) >= 4 and s in SENTENCE.replace("{slug}", "") else _crib_piece(s)
    return [(v, s) for v, s in sorted(reads, key=lambda r: (crib(r[1]), round(_texty(r[1]), 2), _bigram(r[1])),
                                      reverse=True)]


def pdp_free(p):
    """Speculative Mastery-line decoder: the middle-endian word-order readings of a hex/base64 line."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for _v, s in pdp_reads(p.strip())[:4]]
    except Exception:   # noqa: BLE001
        return []


_have = {n for n, _e, _d in CANDIDATES}
CANDIDATES += [(f"pdp{o}-{u}-{fmt}" + ("-bom" if bom else ""),
                (lambda o, u, f, bm: lambda s: pdp_enc(s, o, u, f, bm))(o, u, fmt, bom),
                (lambda o, u: lambda t: pdp_dec(t, o, u))(o, u))
               for o in ("2143", "3412") for u in ("utf-32", "utf-16", "utf-8")
               for fmt, bom in (("hex", False), ("hex", True), ("hex-upper", False), ("words", False),
                                ("base64", False))
               if not (bom and u == "utf-8") and not (u == "utf-16" and o == "2143")   # = utf-16-le, not middle-endian
               and f"pdp{o}-{u}-{fmt}" not in _have]
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

# ------------------------------------------------- float / fixed-point char codes ("You Have a Point")
# One char code per number, carried as a floating / fixed point value: IEEE-754 bit patterns as hex tokens (float32
# `0x429c0000` = 78.0 BE, `0x00009c42` LE; 16-hex doubles), decimals (`78.0`, `7.8e1`, C99 hex floats `0x1.38p+6`),
# a common scale (`0.78` = code / 100, Q8.8 / x10 fixed point ints `19968` = 78 * 256), or the packed '<f' / '>d'
# array itself as base64 / one hex run. Gate: every value lands on an integer code (after one common 10^k / 2^k scale)
# and the text reads as text; plain byte-sized decimal codes (`78 105 99`) are the decimal codec, not this one.
_FLT_TOK = re.compile(r"[\s,;]+")
_FLT_SCALES = tuple(10.0 ** k for k in range(-6, 7)) + tuple(2.0 ** k for k in range(-16, 17) if k)


def flt_enc(s, fmt="f32be-hex"):
    """Text -> one float / fixed point number per code point in `fmt`: f32{be,le}-hex, f64{be,le}-hex, dec (78.0),
    centi (0.78), sci (7.8e+01), hexfloat (0x1.38p+6), q8 / x10 (fixed point ints), b64-{f32le,f32be,f64le,f64be}."""
    cs = [ord(c) for c in s]
    if fmt.endswith("-hex") and fmt[:3] in ("f32", "f64"):
        f = (">" if fmt[3:5] == "be" else "<") + ("f" if fmt[:3] == "f32" else "d")
        return " ".join("0x" + struct.pack(f, c).hex() for c in cs)
    if fmt.startswith("b64-"):
        v = fmt[4:]
        f = (">" if v[3:] == "be" else "<") + str(len(cs)) + ("f" if v[:3] == "f32" else "d")
        return base64.b64encode(struct.pack(f, *cs)).decode()
    if fmt == "dec":
        return " ".join(f"{c:.1f}" for c in cs)
    if fmt == "centi":
        return " ".join(f"{c / 100:g}" for c in cs)
    if fmt == "sci":
        return " ".join(f"{c:.2e}" for c in cs)
    if fmt == "hexfloat":
        return " ".join(re.sub(r"\.?0*p", "p", float(c).hex()) for c in cs)   # C99 %a style: 0x1.38p+6
    if fmt in ("q8", "x10"):
        return " ".join(str(c * (256 if fmt == "q8" else 10)) for c in cs)
    return None


_FLT_FMTS = ("f32be-hex", "f32le-hex", "f64be-hex", "f64le-hex", "dec", "centi", "sci", "hexfloat", "q8", "x10",
             "b64-f32le", "b64-f32be", "b64-f64le", "b64-f64be")


def _flt_codes(vals, scale=1.0):
    """vals * scale as integer code points, else None (a non-integral / non-finite / out-of-range value)."""
    out = []
    for v in vals:
        if not math.isfinite(v):
            return None
        x = v * scale
        r = round(x)
        if abs(x - r) > 1e-6 * max(1.0, abs(r)) or not 9 <= r <= 0x10FFFF:
            return None
        out.append(r)
    return out


def _flt_text(cs):
    try:
        s = "".join(map(chr, cs))
    except (ValueError, OverflowError):
        return None
    return s if all(c.isprintable() or c in "\n\t" for c in s) and _texty(s) >= 0.85 else None


def _flt_packed(b, tag):
    """Reads of raw bytes b as a packed float32 / float64 array, both byte orders."""
    reads = []
    for w, f in ((4, "f"), (8, "d")):
        if len(b) < 3 * w or len(b) % w:
            continue
        for o, oc in (("le", "<"), ("be", ">")):
            cs = _flt_codes(struct.unpack(f"{oc}{len(b) // w}{f}", b))
            s = cs and _flt_text(cs)
            if s:
                reads.append((f"{tag}-f{8 * w}{o}", s))
    return reads


def _flt_scaled(vals, tag, ints=False):
    """Reads of numbers vals under one common scale (1, 10^k, 2^k); fixed point ints need a real (>1) divisor."""
    reads, seen = [], set()
    for sc in _FLT_SCALES:
        if ints and sc >= 1.0:
            continue
        cs = _flt_codes(vals, sc)
        s = cs and _flt_text(cs)
        if s and s not in seen:
            seen.add(s)
            reads.append((tag if sc == 1.0 else f"{tag}-x{sc:g}", s))
    return reads


def flt_reads(t):
    """[(variant, text)] for a float / fixed-point char-code line, crib / most English read first."""
    try:
        if not isinstance(t, str):
            return []
        t = t.strip()
        if not t or len(t) > 400000:
            return []
        m = re.fullmatch(r"[\[{(]\s*(.*?)\s*[\]})]", t, re.S)
        if m:
            t = m.group(1)
        toks = [x for x in _FLT_TOK.split(t) if x]
        reads = []
        if len(toks) == 1 and len(t) >= 16:
            x = toks[0]
            if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", x) and len(x) % 8 == 0:
                reads = _flt_packed(bytes.fromhex(x), "hexrun")
            elif re.fullmatch(r"[A-Za-z0-9+/_-]+={0,2}", x):
                try:
                    b = base64.b64decode(_b64pad(x.replace("-", "+").replace("_", "/")), validate=True)
                except (binascii.Error, ValueError):
                    b = b""
                reads = _flt_packed(b, "b64")
        elif len(toks) >= 3:
            if all(re.fullmatch(r"(?:0[xX])?(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{16})", x) for x in toks):
                hx = [x[2:] if x[:2] in ("0x", "0X") else x for x in toks]
                if len({len(h) for h in hx}) == 1:
                    w = len(hx[0]) // 2
                    for o in ("be", "le"):
                        f = (">" if o == "be" else "<") + ("f" if w == 4 else "d")
                        vals = [struct.unpack(f, bytes.fromhex(h))[0] for h in hx]
                        reads += [(f"f{8 * w}{o}-hex" + v[3:], s) for v, s in _flt_scaled(vals, "hex")]
            elif all(re.fullmatch(r"\d{1,20}", x) for x in toks):
                vals = [int(x) for x in toks]
                if max(vals) > 255:   # byte-sized codes = the decimal codec, not fixed point
                    reads = _flt_scaled([float(v) for v in vals], "fixed", ints=True)
            else:
                vals = []
                for x in toks:
                    x = x.rstrip("fFdD") if not x.lower().startswith(("0x", "-0x", "+0x")) else x
                    if re.fullmatch(r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?", x):
                        vals.append(float(x))
                    elif re.fullmatch(r"[+-]?0[xX][0-9a-fA-F]*\.?[0-9a-fA-F]*[pP][+-]?\d+", x):
                        vals.append(float.fromhex(x))
                    else:
                        return []
                if any(re.search(r"[.eEpP]", x) for x in toks):
                    reads = _flt_scaled(vals, "dec")
        if len(reads) > 1:
            from lib.decode import _bigram
            reads.sort(key=lambda r: (_crib_piece(r[1]), _bigram(r[1])), reverse=True)
        return reads
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []


def flt_dec(t, variant=None):
    """Undo flt_enc (any fmt) -> text, else None; `variant` (a flt_reads tag prefix, e.g. 'f32be') pins the read."""
    for v, s in flt_reads(t):
        if variant is None or v.startswith(variant) or v.endswith(variant):
            return s
    return None


def flt_free(p):
    """Speculative Mastery-line decoder: the float / fixed-point char-code readings of a line (best first)."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for _v, s in flt_reads(p)][:2]
    except Exception:   # noqa: BLE001
        return []


_FLT_PIN = {"f32be-hex": "f32be", "f32le-hex": "f32le", "f64be-hex": "f64be", "f64le-hex": "f64le",
            "b64-f32le": "b64-f32le", "b64-f32be": "b64-f32be", "b64-f64le": "b64-f64le", "b64-f64be": "b64-f64be"}
_have = {n for n, _e, _d in CANDIDATES}
CANDIDATES += [(f"float-{fmt}", (lambda f: lambda s: flt_enc(s, f))(fmt),
                (lambda v: lambda t: flt_dec(t, v))(_FLT_PIN.get(fmt)))
               for fmt in _FLT_FMTS if f"float-{fmt}" not in _have]
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


# ------------------------------------------------- knob sweep: a seen day's codec with ONE knob turned
# D20 "Big Entrance" = D19's UTF-16 hex with the byte order flipped ("Same bar. This time the big one goes first."): the
# GM re-runs an earlier codec with one parameter changed. knob_sweep(t) walks every DAYS family's knobs, cheapest first,
# and returns the first read the template crib / slug confirms:
#   letters  rot/Caesar k (both directions), rot47-style shift k over the 94 printables, atbash+k, reversal at
#            char / word / per-word level, rail fences 2-12 x every offset
#   numbers  any 0x / \x / % / &#x / &# / \u / U+ / 0b / 0o prefix, any separator, radix 2-36 per token, fixed-width
#            runs (binary 5/7/8/16 either bit order, octal/decimal 3, hex 2/4/8), values > 255 = code points
#   base32   RFC 4648 / base32hex / Crockford / z-base-32, any case, padded or not; base64 std / url / reversed
#   2-symbol Bacon / binary polarity, bit order and width 4/5/7/8/16 (5-bit groups read as letters 26/24 or hex nibbles)
#   Morse    dot/dash swapped, then text or hex digits
#   bytes    every parse x {identity, reversed, nibble-swapped, reversed hex, bit-reversed, 2/4/8-byte word swap} x
#            {UTF-8, UTF-16 BOM/LE/BE, UTF-32 BOM/LE/BE}
# The blob text reversed is tried last (reversal at the char level of a byte encoding). Budget ~0.2 s, never raises.
_KS_CRIBS = ("nice work decoding", "decoding this warmup", "submit this exact", "answer to the game master")
_KS_CRIBS_EXACT = ("Nice work decoding", "decoding this warmup", "submit this exact", "answer to the Game Master")
_KS_ENCS = ("utf-8", "utf-16", "utf-16-le", "utf-16-be", "utf-32", "utf-32-le", "utf-32-be")
_KS_B32 = {"rfc4648": "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567", "base32hex": "0123456789ABCDEFGHIJKLMNOPQRSTUV",
           "crockford": "0123456789ABCDEFGHJKMNPQRSTVWXYZ", "zbase32": "ybndrfg8ejkmcpqxot1uwisza345h769"}
_KS_B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_KS_PREFIX = re.compile(r"(?i)0x|\\x|&#x|&#|\\u\{?|\\U|%u|u\+|0b|0o|\\|%|[;}\"'\[\](){}<>]")
_KS_SEP = re.compile(r"[\s,;:|/_.\-]+")
_KS_DIG = "0123456789abcdefghijklmnopqrstuvwxyz"


def _ks_ok(s):
    """The read is the warmups sentence: a crib phrase (any case: Morse reads come back lowercase) in printable text."""
    if not s or len(s) < 8:
        return False
    low = s.lower()
    if s not in (low, s.upper()):   # mixed case must match exactly: a +32 printable shift only swaps letter case
        return _texty(s) > 0.9 and any(c in s for c in _KS_CRIBS_EXACT)
    return any(c in low for c in _KS_CRIBS) and _texty(s) > 0.9


def _ks_texts(b):
    """[(encoding, text)] of a byte string: every UTF width / order that reads as printable text."""
    out = []
    for e in _KS_ENCS:
        if e.startswith("utf-16") and len(b) % 2 or e.startswith("utf-32") and len(b) % 4:
            continue
        try:
            s = b.decode(e).rstrip("\x00")
        except Exception:  # noqa: BLE001
            continue
        if s and (e != "utf-8" or not s.startswith("﻿")) and all(c.isprintable() or c in "\t\r\n" for c in s):
            out.append((e, s.lstrip("﻿")))
    return out


def _ks_bytes_x(b):
    """(knob, bytes) -- the byte-level knobs, identity first."""
    yield "", b
    yield "rev", b[::-1]
    yield "nibswap", nibswap(b)
    yield "revhex", nibswap(b[::-1])
    yield "bitrev", bytes(int(f"{x:08b}"[::-1], 2) for x in b)
    for w in (2, 4, 8):
        if len(b) > w:
            yield f"wswap{w}", wordswap(b + b"\x00" * (-len(b) % w), w)


def _ks_vals(name, vals):
    """(knob, bytes-or-text) reads of an integer list: bytes when all < 256, UTF-16 units / code points otherwise."""
    if not vals:
        return
    if max(vals) < 256:
        yield name, bytes(vals)
    if max(vals) < 0x10000:
        yield name + "-u16be", b"".join(v.to_bytes(2, "big") for v in vals)
    if max(vals) < 0x110000 and min(vals) >= 0:
        try:
            yield name + "-cp", "".join(map(chr, vals))
        except ValueError:
            pass


def _ks_int(tok, r):
    try:
        return int(tok, r)
    except ValueError:
        return None


def _ks_two(t):
    """(knob, values) of a two-symbol blob (binary / Bacon / any glyph pair): polarity x bit order x group width."""
    body = re.sub(r"\s+", " ", t.strip())
    syms = sorted(set(body.replace(" ", "")))
    if len(syms) != 2:
        return
    groups = body.split(" ")
    flat = body.replace(" ", "")
    ws = {len(g) for g in groups}
    for pol in (0, 1):
        zero, one = syms[pol], syms[1 - pol]
        bits = [g.replace(zero, "0").replace(one, "1") for g in groups]
        fb = flat.replace(zero, "0").replace(one, "1")
        chunks = [("tok", bits)] if len(ws) == 1 or len(groups) > 1 and len(ws) <= 3 else []
        chunks += [(f"w{w}", [fb[i:i + w] for i in range(0, len(fb) - len(fb) % w, w)])
                   for w in (8, 7, 16, 5, 4) if len(fb) % w == 0 and len(fb) >= 4 * w]
        for wn, cs in chunks:
            for order in ("msb", "lsb"):
                vals = [int(c[::-1] if order == "lsb" else c, 2) for c in cs if c]
                yield f"2sym-{syms[pol]}0-{wn}-{order}", vals, {len(c) for c in cs}


def _ks_letters(t):
    """Letter-level knobs (D2/D12/D13/D14/D15/D18 families): rot k, atbash+k, rot47-style shifts, reversals, rails."""
    yield "reverse", t[::-1]
    yield "wordrev", " ".join(t.split(" ")[::-1])
    yield "perword", " ".join(w[::-1] for w in t.split(" "))
    for k in range(1, 26):
        yield f"rot{k}", rot(t, k)
    for k in range(1, 26):
        yield f"atbash+{k}", atbash(rot(t, k))
        yield f"rot{k}-rev", rot(t, k)[::-1]
    for k in range(1, 94):
        yield f"rot94-{k}", "".join(chr((ord(c) - 33 + k) % 94 + 33) if 33 <= ord(c) <= 126 else c for c in t)
    for k in range(1, 94):
        yield f"rot94-{k}-rev", "".join(chr((ord(c) - 33 + k) % 94 + 33) if 33 <= ord(c) <= 126 else c
                                        for c in t)[::-1]
    for n in range(2, 13):
        for o in range(2 * n - 2):
            yield f"rail{n}@{o}", rail_dec(t, n, o)
            yield f"rail{n}@{o}-rev", rail_dec(t[::-1], n, o)


def _ks_parses(t):
    """(knob, bytes|str) -- every numeric / base-N / two-symbol / Morse parse of the blob, cheapest first."""
    s = t.strip()
    compact = re.sub(r"\s+", "", s)
    # hex: any prefix / separator / case
    x = _KS_SEP.sub("", _KS_PREFIX.sub(" ", s))
    if len(x) >= 8 and re.fullmatch(r"[0-9a-fA-F]+", x):
        if len(x) % 2 == 0:
            yield "hex", bytes.fromhex(x)
        yield "hexrev", bytes.fromhex(x[::-1]) if len(x) % 2 == 0 else None
    # base32 family (any case, padding optional)
    u = compact.rstrip("=").upper()
    if len(u) >= 8 and re.fullmatch(r"[0-9A-Z]+", u):
        for an, alpha in _KS_B32.items():
            a = alpha.upper()
            if an == "crockford":
                u2 = u.translate(str.maketrans("OIL", "011"))
            else:
                u2 = u
            if set(u2) <= set(a):
                n = 0
                bits = 0
                out = bytearray()
                for c in u2:
                    n = n << 5 | a.index(c)
                    bits += 5
                    if bits >= 8:
                        bits -= 8
                        out.append(n >> bits & 255)
                yield f"b32-{an}", bytes(out)
    # base64 std / url, padded or not
    if len(compact) >= 8 and re.fullmatch(r"[A-Za-z0-9+/_\-]+=*", compact):
        b = compact.rstrip("=").replace("-", "+").replace("_", "/")
        try:
            yield "b64", base64.b64decode(b + "=" * (-len(b) % 4))
        except Exception:  # noqa: BLE001
            pass
    # Morse, dot/dash swapped (plain Morse is the confirmed D16 decoder's)
    if len(s) >= 8 and set(compact) <= set(".-/|_*·•−–—"):
        sw = s.translate({ord("."): "-", ord("-"): ".", ord("·"): "-", ord("•"): "-", ord("_"): ".", ord("−"): ".",
                          ord("–"): ".", ord("—"): "."})
        m = safe(morse_alt_dec, sw)
        if m:
            yield "morse-swap", m
            h = re.sub(r"\s+", "", m)
            if len(h) % 2 == 0 and re.fullmatch(r"[0-9a-fA-F]+", h):
                yield "morse-swap-hex", bytes.fromhex(h)
    # two-symbol (binary / Bacon): polarity x order x width
    for name, vals, widths in _ks_two(s):
        yield from _ks_vals(name, vals)
        if widths == {5}:
            if max(vals) < 26:
                yield name + "-bacon26", "".join(chr(97 + v) for v in vals)
            if max(vals) < 24:
                yield name + "-bacon24", "".join("abcdefghiklmnopqrstuwxyz"[v] for v in vals)
            if max(vals) < 16:
                h = "".join("%x" % v for v in vals)
                if len(h) % 2 == 0:
                    yield name + "-hexnib", bytes.fromhex(h)
        if widths == {4}:
            h = "".join("%x" % v for v in vals)
            if len(h) % 2 == 0:
                yield name + "-nib", bytes.fromhex(h)
    # tokens in any radix (octal / decimal / hex / ... width-free), then fixed-width digit runs
    toks = [z for z in _KS_SEP.split(_KS_PREFIX.sub(" ", s).lower()) if z]
    if len(toks) >= 4:
        hi = max(_KS_DIG.index(c) for z in toks for c in z if c in _KS_DIG) if all(
            set(z) <= set(_KS_DIG) for z in toks) else 99
        for r in (8, 10, 16, 2, 4, 3, 5, 6, 7, 9, 12, 32, 36):
            if hi < r:
                vals = [_ks_int(z, r) for z in toks]
                if None not in vals:
                    yield from _ks_vals(f"radix{r}", vals)
    if len(toks) == 1 and toks[0].isdigit():
        d = toks[0]
        for r, w in ((8, 3), (10, 3), (8, 4), (10, 5), (10, 2), (16, 4)):
            if len(d) % w == 0 and max(d) < _KS_DIG[r]:
                yield from _ks_vals(f"radix{r}w{w}", [int(d[i:i + w], r) for i in range(0, len(d), w)])


def _ks_reads(t, deadline):
    """(knob, text) reads, cheapest knobs first; stops at the deadline."""
    for side, src in (("", t), ("blobrev-", t.strip()[::-1])):
        for pn, got in _ks_parses(src):
            if got is None:
                continue
            if isinstance(got, str):
                yield side + pn, got
                continue
            for bn, b in _ks_bytes_x(got):
                for e, s in _ks_texts(b):
                    yield side + "-".join(z for z in (pn, bn, e) if z), s
            if time.monotonic() > deadline:
                return
    for ln, s in _ks_letters(t.strip("\r\n")):
        yield ln, s
        if time.monotonic() > deadline:
            return


def knob_sweep(t, budget=0.18):
    """(knob, sentence) -- the first crib/slug-confirmed read of t under a seen day's codec with one knob turned, else
    None. Never raises."""
    try:
        t = reader_text(t)
        if not isinstance(t, str) or len(t.strip()) < 8:
            return None
        deadline = time.monotonic() + budget
        for name, s in _ks_reads(t, deadline):
            if s and _ks_ok(s):
                return name, s.strip()
    except Exception:  # noqa: BLE001
        return None
    return None


def knob_dec(t):
    ks = knob_sweep(t)
    return ks[1] if ks else None


def knob_free(p, k=4, budget=0.1):
    """Speculative Mastery-line decoder: knob-turned reads of a line cut mid-sentence, kept when the crib confirms them
    (a crib substring / a crib tail + slug piece), most crib first."""
    try:
        if not isinstance(p, str) or len(p.strip()) < 4:
            return []
        deadline = time.monotonic() + budget
        hits, seen = [], set()
        for _n, s in _ks_reads(p.strip("\r\n"), deadline):   # spaces kept: a rail / reversal moves them
            s = s.strip("\x00")
            if s and s.strip() not in seen and all(c.isprintable() for c in s):
                seen.add(s.strip())
                c = _crib_piece(s)
                if c >= 6 or _ks_ok(s):
                    hits.append((c, s))
                    if len(hits) >= 3 * k:
                        break
        hits.sort(key=lambda h: -h[0])
        return [s for _c, s in hits[:k]]
    except Exception:  # noqa: BLE001
        return []


# ------------------------------------------------- big-integer text (RSA long_to_bytes / "Big" number family)
# The WHOLE message (or, in Mastery, each fragment) as ONE integer: n = int.from_bytes(bytes, 'big' | 'little') written
# in radix 10 / 8 / 2 / 36 / 62 (optional 0o / 0b / 0x prefix), no separators. Bytes = UTF-8, or UTF-16 (BOM / LE /
# BE: then sniffed by unicode_form_dec). Decode: n = int(t, base); n.to_bytes((n.bit_length() + 7) // 8, order).
# Cue: one unbroken digit run ~2.41 decimal digits per char (a 4+ digit token -- decimal char codes are <= 3 digits
# and need separators, which lib.decode's _NUMS requires). Crib-gated: only printable, wordy text is returned.
_BIGN_ALPHA = {10: string.digits, 8: "01234567", 2: "01", 36: string.digits + string.ascii_lowercase,
               62: _B62, 16: string.hexdigits[:16]}
_BIGN_FORMS = {"utf8": "utf-8", "utf16": "utf-16", "utf16le": "utf-16-le", "utf16be": "utf-16-be"}


def bignum_enc(s, radix=10, order="big", form="utf8"):
    b = _t(s).encode(_BIGN_FORMS[form])
    n = int.from_bytes(b, order)
    if radix in (10, 8, 2, 16):
        return format(n, {10: "d", 8: "o", 2: "b", 16: "x"}[radix])
    out, a = "", _BIGN_ALPHA[radix]
    while n:
        n, r = divmod(n, radix)
        out = a[r] + out
    return out or "0"


def _bign_int(t, radix):
    if radix == 62:
        n = 0
        for c in t:
            n = n * 62 + _B62.index(c)
        return n
    return int(t, radix)


def _bign_text(b):
    """bytes -> text: UTF-8, else a sniffed UTF-16/32 form; printable + wordy, else None."""
    x = None
    if b[:2] in (b"\xff\xfe", b"\xfe\xff") or (len(b) >= 4 and b.count(0) * 3 >= len(b)):
        x = unicode_form_dec(b)
    if x is None:
        try:
            x = b.decode("utf-8")
        except UnicodeDecodeError:
            return None
    x = x.lstrip("﻿")
    from lib.decode import _bigram
    if not x or not all(c.isprintable() for c in x) or _texty(x) < 0.9 or _bigram(x) < -8:
        return None
    return x


def bignum_reads(t):
    """[(radix, order, text)] for every big-integer reading of ONE token (prefix 0b/0o/0x honoured). Never raises."""
    try:
        from lib.decode import _bigram
        t = _t(t).strip()
        if not 4 <= len(t) <= 20000 or not t.isascii() or not t.isalnum():
            return []
        pre = t[:2].lower()
        if pre in ("0b", "0o", "0x") and len(t) > 4:
            radices = [{"0b": 2, "0o": 8, "0x": 16}[pre]]
            t = t[2:]
        elif t.isdigit():
            radices = [r for r in (2, 8, 10) if set(t) <= set(_BIGN_ALPHA[r])]
        else:
            radices = [36, 62] if t.lower() == t or t.upper() == t else [62]   # base36 either case (numpy: upper)
        out = []
        for r in radices:
            n = _bign_int(t.lower() if r == 36 else t, r)
            if not n:
                continue
            for order in ("big", "little"):
                L = (n.bit_length() + 7) // 8
                for k in (L, L + 1) if L % 2 else (L,):   # UTF-16: the NUL high byte at the integer's top is dropped
                    x = _bign_text(n.to_bytes(k, order))
                    if x is not None and (r, x) not in [(q[0], q[2]) for q in out]:
                        out.append((r, order, x))
                        break
        return sorted(out, key=lambda q: (-_bigram(q[2]) if len(q[2]) >= 12 else 0, q[1] != "big"))
    except Exception:  # noqa: BLE001
        return []


def bignum_dec(t, radix=None, order=None):
    """One big-integer token -> text, else None."""
    try:
        for r, o, x in bignum_reads(t):
            if (radix is None or r == radix) and (order is None or o == order):
                return x
        return None
    except Exception:  # noqa: BLE001
        return None


def bignum_free(p):
    """Speculative Mastery-line decoder: the fragment as its own big integer (leading spaces kept)."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + x for _r, _o, x in bignum_reads(p.strip())][:3]
    except Exception:  # noqa: BLE001
        return []


_have = {n for n, _e, _d in CANDIDATES}
CANDIDATES += [(f"bignum{r}-{o}" + ("" if f == "utf8" else f"-{f}"),
                (lambda r, o, f: lambda s: bignum_enc(s, r, o, f))(r, o, f),
                (lambda r, o: lambda t: bignum_dec(t, r, o))(r, o))
               for r in (10, 8, 2, 36, 62) for o in ("big", "little") for f in _BIGN_FORMS
               if f"bignum{r}-{o}" + ("" if f == "utf8" else f"-{f}") not in _have]
del _have


# --------------------------------------------- big-radix alphabets (the whole text as ONE integer, any printable radix)
# Generic catch-all for "the alphabet got bigger" when no 4/5-char chunk codec fits: n = int.from_bytes(utf8, 'big' |
# 'little') written in radix len(A) over A = base94 '!'..'~' / base95 ' '..'~' / RFC1924 b85 / Ascii85 '!'..'u' / Z85 /
# basE91 / base64 / base62 (+ inverted) / base58 (bitcoin, flickr) -- or the line's own sorted charset. Digits most-
# significant first ('big') or reversed ('little'). base58-style leading A[0] symbols = leading zero bytes (text has
# none, so they are dropped). Capped at 2000 chars; crib-gated by _bign_text (printable, wordy UTF-8/UTF-16 only).
_BIGR_ALPHAS = {
    "b94": _B94, "b95": _B95, "a85": "".join(map(chr, range(33, 118))),
    "b85": string.digits + string.ascii_uppercase + string.ascii_lowercase + "!#$%&()*+-;<=>?@^_`{|}~",
    "z85": string.digits + string.ascii_lowercase + string.ascii_uppercase + ".-:+=^!/*?&<>()[]{}@%$#",
    "b91": _B91, "b64": string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/",
    "b62": _B62, "b62inv": _B62_INV, "b58": _B58,
    "b58flickr": "123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ",
}


def bigradix_enc(s, alpha, digits="big", order="big", lead0=False):
    b = _u(s)
    n, out, r = int.from_bytes(b, order), [], len(alpha)
    while n:
        n, d = divmod(n, r)
        out.append(alpha[d])
    if lead0:
        out += [alpha[0]] * (len(b) - len(b.lstrip(b"\0")))
    return "".join(out if digits == "little" else reversed(out))


def bigradix_reads(t, alphas=None):
    """[(alpha_name, digits, order, text)] for every big-radix reading of ONE line (alphas: names, or "sorted" = the
    line's own sorted charset). Never raises."""
    try:
        t = _t(t)
        t = t.strip("\r\n")
        if not t.strip() or len(t) > 2000:
            return []
        cs = set(t)
        names = list(_BIGR_ALPHAS) + ["sorted"] if alphas is None else list(alphas)
        out, seen = [], set()
        for name in names:
            a = "".join(sorted(cs)) if name == "sorted" else _BIGR_ALPHAS.get(name)
            if not a or len(a) < 3:
                continue
            u = t if " " in a else t.strip()
            if not u or not set(u) <= set(a):
                continue
            ix = {c: i for i, c in enumerate(a)}
            r = len(a)
            for digits in ("big", "little"):
                v = u if digits == "big" else u[::-1]
                v = v.lstrip(a[0])          # base58-style leading zero symbols: zero bytes, absent from text
                if not v:
                    continue
                n = 0
                for c in v:
                    n = n * r + ix[c]
                L = (n.bit_length() + 7) // 8
                for order in ("big", "little"):
                    for k in (L, L + 1) if L % 2 else (L,):
                        x = _bign_text(n.to_bytes(k, order))
                        if x is not None and (len(x) < 4 or len(x) < 16 and not x.isascii()):
                            x = None    # 2-3 char / short non-ASCII readings: chance hits of a wide alphabet
                        if x is not None:
                            if x not in seen:
                                seen.add(x)
                                out.append((name, digits, order, x))
                            break
        from lib.decode import _bigram
        return sorted(out, key=lambda q: -_bigram(q[3]) if len(q[3]) >= 12 else 0)   # text before its reversal
    except Exception:  # noqa: BLE001
        return []


def bigradix_dec(t, alpha=None, digits=None, order=None):
    """One line under a big-radix alphabet (name in _BIGR_ALPHAS or "sorted"; None = any) -> text, else None."""
    try:
        for name, d, o, x in bigradix_reads(t, None if alpha is None else (alpha,)):
            if (digits is None or d == digits) and (order is None or o == order):
                return x
        return None
    except Exception:  # noqa: BLE001
        return None


def bigradix_free(p):
    """Speculative Mastery-line decoder: the fragment as one big-radix integer (leading spaces kept unless the
    alphabet has a space)."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        outs = [lead + x for _a, _d, _o, x in bigradix_reads(p.strip())]
        outs += [x for _a, _d, _o, x in bigradix_reads(p, ("b95",)) if lead and x not in outs]
        return outs[:4]
    except Exception:  # noqa: BLE001
        return []


_have = {n for n, _e, _d in CANDIDATES}
CANDIDATES += [(f"bigradix-{a}-{d}" + ("" if o == "big" else "-le"),
                (lambda a, d, o: lambda s: bigradix_enc(s, _BIGR_ALPHAS[a], d, o))(a, d, o),
                (lambda a, d, o: lambda t: bigradix_dec(t, a, d, o))(a, d, o))
               for a in _BIGR_ALPHAS for d in ("big", "little") for o in ("big", "little")
               if f"bigradix-{a}-{d}" + ("" if o == "big" else "-le") not in _have]
del _have


# ------------------------------------------- byte-swapped code-unit escapes (D9 \uXXXX with the UTF-16 byte order flipped)
# `\u4e00\u6900\u6300` = "Nic": UTF-16LE bytes read as big-endian code units ((v & 255) << 8 | v >> 8), so json.loads /
# html.unescape / unescape() read CJK U+2000-U+7Exx with every low byte 00 (space -> U+2000). Any escape form: \uXXXX,
# &#xHHHH; / &#DDDDD;, U+XXXX, %uXXXX, 0xXXXX; astral = a swapped surrogate pair. Whole fragment only (one pair of quotes
# or brackets); the cue gate (swapped read mostly ASCII, straight read not) keeps real CJK text and D9 lines out.
_CU_TOK = re.compile(r"\\u([0-9A-Fa-f]{4})|&#[xX]([0-9A-Fa-f]{1,6});?|&#([0-9]{1,7});?|[Uu]\+([0-9A-Fa-f]{4,6})"
                     r"|%[uU]([0-9A-Fa-f]{4})|0[xX]([0-9A-Fa-f]{4})(?![0-9A-Fa-f])")
_CU_FULL = re.compile(r"(?:(?:" + _CU_TOK.pattern + r")|[\s,;])+")
_CU_FMT = {"json\\u": ('"', "\\u{:04x}", "", '"'), "\\u": ("", "\\u{:04x}", "", ""), "\\U": ("", "\\u{:04X}", "", ""),
           "&#x": ("", "&#x{:x};", "", ""), "&#X": ("", "&#x{:X};", "", ""), "&#": ("", "&#{:d};", "", ""),
           "U+": ("", "U+{:04X}", "", ""), "U+-spaced": ("", "U+{:04X}", " ", ""), "%u": ("", "%u{:04X}", "", ""),
           "%u-lower": ("", "%u{:04x}", "", ""), "0x": ("", "0x{:04x}", " ", ""), "0x-comma": ("", "0x{:04x}", ", ", "")}


def _cu_swap(v):
    return (v & 255) << 8 | v >> 8


def cuswap_enc(s, fmt="json\\u", swap=True):
    """Text -> code-unit escapes in `fmt` (a _CU_FMT key); swap=True writes each UTF-16 unit byte-swapped."""
    pre, tok, sep, post = _CU_FMT[fmt]
    b = s.encode("utf-16-le" if swap else "utf-16-be", "surrogatepass")
    return pre + sep.join(tok.format(int.from_bytes(b[i:i + 2], "big")) for i in range(0, len(b), 2)) + post


def _cu_vals(t):
    """Whole-fragment code-unit escape values (whitespace gaps kept as literal spaces like ucp_dec), else None."""
    if not isinstance(t, str):
        return None
    t = t.strip()
    if len(t) >= 2 and (t[0] == t[-1] and t[0] in "\"'" or t[0] + t[-1] == "[]"):
        t = t[1:-1].strip()
    if not t or len(t) > 400000 or not _CU_FULL.fullmatch(t):
        return None
    toks = list(_CU_TOK.finditer(t))
    if len(toks) < 2:
        return None
    vals = []
    for m in toks:
        i, g = next((i, g) for i, g in enumerate(m.groups()) if g)
        vals.append(int(g, 10 if i == 2 else 16))
    gaps = [t[a.end():b.start()] for a, b in zip(toks, toks[1:])]
    if any(gaps) and not all(gaps) and not any(chr(min(v, 0x10FFFF)).isspace() or v == 0x2000 for v in vals):
        out = []
        for i, v in enumerate(vals):
            out.append(v)
            if i < len(gaps) and re.search(r"\s", gaps[i]):
                out.append(-1)   # literal space: 0x20 straight, 0x2000 swapped
        return out
    return vals


def _asciish(x):
    return bool(x) and sum(32 <= ord(c) < 127 or c in "\t\n" for c in x) >= 0.9 * len(x)


def cuswap_dec(t, swap=True):
    """Byte-swapped code-unit escapes -> text, None unless the swapped read is printable, mostly ASCII and the straight
    read is not (the cue). swap=None: that swapped read when cued, else the straight read; swap=False: straight only."""
    try:
        vals = _cu_vals(t)
        if not vals:
            return None
        straight = _ucp_str([32 if v < 0 else v for v in vals])
        if swap is False:
            return straight
        sw = None
        if all(v <= 0xFFFF for v in vals):
            sw = _ucp_str([32 if v < 0 else _cu_swap(v) for v in vals])
        if sw and _asciish(sw) and not _asciish(straight or ""):
            return sw
        return straight if swap is None else None
    except Exception:  # noqa: BLE001
        return None


def cuswap_free(p):
    d = cuswap_dec(p)
    return [p[:len(p) - len(p.lstrip())] + d] if d else []


_have = {c[0] for c in CANDIDATES}
CANDIDATES += [(f"cuswap-{f}", (lambda f: lambda s: cuswap_enc(s, f))(f), cuswap_dec)
               for f in _CU_FMT if f"cuswap-{f}" not in _have]
del _have


# ------------------------------------------------- binary code units (16/32-bit groups of UTF-16 / UTF-32 units)
# D4's binary at the D19/D20 width/order knob: the text as UTF-16 (or UTF-32) code units, each unit one [01]{16} /
# [01]{32} group = int(g, 2).to_bytes(w, 'big') -- BE (`0000000001001110` = N) or LE (halves swapped,
# `0100111000000000`), an optional BOM group first (1111111011111111 = feff BE, 1111111111111110 LE), groups split by
# whitespace , ; | or run together (len % 16 == 0). Cue: one 8-bit half of the units all zero; 8-bit groups (binary8)
# and packed UTF-8 words (wint, no zero halves) are other families and read None here.
_CUBIN_ENC = {(2, "big"): "utf-16-be", (2, "little"): "utf-16-le", (4, "big"): "utf-32-be", (4, "little"): "utf-32-le"}
_CUBIN_BOM = {(2, "big"): b"\xfe\xff", (2, "little"): b"\xff\xfe", (4, "big"): b"\0\0\xfe\xff",
              (4, "little"): b"\xff\xfe\0\0"}


def cubin_enc(s, w=2, order="big", bom=False, sep=" "):
    """Text -> its UTF-16 / UTF-32 (w = 2 / 4) code units in `order`, one 8w-bit binary group per unit."""
    b = (_CUBIN_BOM[w, order] if bom else b"") + s.encode(_CUBIN_ENC[w, order], "surrogatepass")
    return sep.join(format(int.from_bytes(b[i:i + w], "big"), f"0{8 * w}b") for i in range(0, len(b), w))


def _cubin_groups(t):
    """[(w, [ints])] candidate unit splits of a 0/1 line: equal 16/32-bit tokens, or one run cut every 16 / 32 bits."""
    if not isinstance(t, str):
        return []
    toks = [x for x in re.split(r"[\s,;|]+", t.strip()) if x]
    if not toks or len(toks) > 50000 or not all(re.fullmatch(r"[01]+", x) for x in toks):
        return []
    n = {len(x) for x in toks}
    if len(toks) > 1:
        k = len(toks[0])
        return [(k // 8, [int(x, 2) for x in toks])] if len(n) == 1 and k in (16, 32) else []
    flat = toks[0]
    return [(w, [int(flat[i:i + 8 * w], 2) for i in range(0, len(flat), 8 * w)])
            for w in (2, 4) if len(flat) % (8 * w) == 0 and len(flat) >= 16 * w]


def cubin_reads(t):
    """[(variant, text)]: the UTF-16 / UTF-32 BE / LE reads of a binary code-unit line. variant = cubin{16|32}{be|le}."""
    out = []
    try:
        for w, vs in _cubin_groups(t):
            b = b"".join(v.to_bytes(w, "big") for v in vs)
            for order in ("big", "little"):
                body = b[w:] if b[:w] == _CUBIN_BOM[w, order] else b
                if not body:
                    continue
                units = [body[i:i + w] for i in range(0, len(body), w)]
                hi = [u[:-1] if order == "big" else u[1:] for u in units]
                if sum(not any(h) for h in hi) < 0.5 * len(units):
                    continue   # the cue: most units carry an all-zero high half
                try:
                    s = body.decode(_CUBIN_ENC[w, order])
                except UnicodeDecodeError:
                    continue
                if "\0" in s or not all(c.isprintable() or c in "\n\t" for c in s) or _texty(s) < 0.85:
                    continue
                out.append((f"cubin{8 * w}{'be' if order == 'big' else 'le'}", s))
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []
    return out


def cubin_dec(t, w=None, order=None):
    """Undo cubin_enc (any width / order / BOM / separator) -> text, else None; w / order pin the variant."""
    tag = "cubin" + ("" if w is None else str(8 * w)) + ("" if order is None else "be" if order == "big" else "le")
    return next((s for v, s in cubin_reads(t) if v.startswith(tag)), None)


def cubin_free(p):
    """Speculative Mastery-line decoder: the code-unit binary reading of a line."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for _v, s in cubin_reads(p)][:1]
    except Exception:   # noqa: BLE001
        return []


_have = {c[0] for c in CANDIDATES}
CANDIDATES += [(f"cubin{8 * w}{'be' if o == 'big' else 'le'}" + ("-bom" if bom else "") + ("-stream" if sep == "" else ""),
                (lambda w, o, bom, sep: lambda s: cubin_enc(s, w, o, bom, sep))(w, o, bom, sep),
                (lambda w, o: lambda t: cubin_dec(t, w, o))(w, o))
               for w in (2, 4) for o in ("big", "little") for bom in (False, True) for sep in (" ", "")
               if f"cubin{8 * w}{'be' if o == 'big' else 'le'}" + ("-bom" if bom else "")
               + ("-stream" if sep == "" else "") not in _have]
del _have


# ------------------------------------------------- astral text under a byte layer: UTF-16 surrogates, CESU-8, MUTF-8
# Non-BMP / non-ASCII "fancy" letters (Mathematical Bold N = U+1D40D) under hex / base64 bytes: UTF-16 (BE/LE, maybe a
# BOM; astral chars as d835 dcxx surrogate pairs), CESU-8 (each surrogate half as its own 3-byte ed a0..bf / ed b0..bf
# sequence), Modified UTF-8 (CESU-8 + NUL as c0 80) or overlong UTF-8 (c0 / c1 / e0 80.. / f0 80.. leads). Read with a
# lenient UTF-8 decoder that pairs surrogate halves and keeps overlong values, or utf-16 (surrogatepass), then fold to
# ASCII (unistyle_dec, else NFKC). The plain-ASCII UTF-8 / UTF-16 reads stay the strict decoders' / unicode_form's job.
_ASTRAL_FORMS = ("utf16be", "utf16le", "utf16be-bom", "utf16le-bom", "cesu8", "mutf8", "overlong")


def astral_enc(s, form="utf16be", outer="hex", style="bold"):
    """Text -> `outer` text of its `style`d (unistyle, ASCII spaces kept; overlong: plain) bytes under `form`."""
    x = s if form == "overlong" or not style else unistyle_enc(s, style, space=" ")
    if form.startswith("utf16"):
        e = "utf-16-be" if "be" in form else "utf-16-le"
        b = (("﻿" if form.endswith("bom") else "") + x).encode(e)
    elif form == "overlong":
        b = b"".join(bytes((0xC0 | ord(c) >> 6, 0x80 | ord(c) & 63)) if ord(c) < 0x80 else c.encode() for c in x)
    else:
        u = x.encode("utf-16-be")
        b = b"".join(b"\xc0\x80" if form == "mutf8" and v == 0 else chr(v).encode("utf-8", "surrogatepass")
                     for v in (int.from_bytes(u[i:i + 2], "big") for i in range(0, len(u), 2)))
    return _bytes_out(b, outer)


def _lenient_utf8(b):
    """(text, quirks) of bytes under a lenient UTF-8 reader: overlong forms keep their value, surrogate halves pair up
    (CESU-8); quirks subset of {cesu8, mutf8, overlong}. None on a bad lead / continuation, lone surrogate, > U+10FFFF."""
    cps, quirks, i, n = [], set(), 0, len(b)
    while i < n:
        x = b[i]
        if x < 0x80:
            cps.append(x)
            i += 1
            continue
        k, cp = (1, x & 0x1F) if 0xC0 <= x < 0xE0 else (2, x & 0x0F) if 0xE0 <= x < 0xF0 else \
            (3, x & 0x07) if 0xF0 <= x < 0xF8 else (0, 0)
        if not k or i + k >= n:
            return None
        for c in b[i + 1:i + 1 + k]:
            if c & 0xC0 != 0x80:
                return None
            cp = cp << 6 | c & 0x3F
        if cp < (0x80, 0x800, 0x10000)[k - 1]:
            quirks.add("mutf8" if cp == 0 and k == 1 else "overlong")
        if cp > 0x10FFFF:
            return None
        if 0xD800 <= cp < 0xE000:
            quirks.add("cesu8")
        cps.append(cp)
        i += k + 1
    out, j = [], 0
    while j < len(cps):
        v = cps[j]
        if 0xD800 <= v < 0xDC00 and j + 1 < len(cps) and 0xDC00 <= cps[j + 1] < 0xE000:
            out.append(chr(0x10000 + ((v - 0xD800) << 10) + cps[j + 1] - 0xDC00))
            j += 2
            continue
        if 0xD800 <= v < 0xE000:
            return None
        out.append(chr(v))
        j += 1
    return "".join(out), quirks


def _astral_fold(s, quirky):
    """Decoded text -> printable-ASCII sentence (styled letters folded), else None."""
    s = s.replace("﻿", "")
    if not s:
        return None
    if s.isascii():
        out = s if quirky else None   # plain ASCII UTF-8 / UTF-16 is another family's read
    else:
        out = unistyle_dec(s)
        if out is None:
            n = unicodedata.normalize("NFKC", s)
            out = n if n != s and n.isascii() else None
    if not out or not all(c.isprintable() or c in "\t\r\n" for c in out) or _texty(out) < 0.85:
        return None
    return out


def astral_reads(t):
    """[(form, text)] for every byte-layer x (UTF-16 surrogates / CESU-8 / MUTF-8 / overlong / styled UTF-8) reading of
    `t` that folds to printable ASCII. Never raises."""
    out = []
    try:
        for _layer, b in _bytes_reads(_t(t)):
            if not b:
                continue
            got = _lenient_utf8(b)
            if got is not None:
                s, q = got
                f = _astral_fold(s, bool(q))
                if f is not None:
                    out.append(("overlong" if "overlong" in q else "mutf8" if "mutf8" in q else
                                "cesu8" if "cesu8" in q else "utf8", f))
            if len(b) % 2:
                continue
            boms = {b"\xfe\xff": "be", b"\xff\xfe": "le"}
            orders = [boms[b[:2]]] if b[:2] in boms else ["be", "le"]
            for o in orders:
                try:
                    s = b.decode("utf-16-" + o)
                except UnicodeDecodeError:
                    continue
                f = _astral_fold(s, False)
                if f is not None:
                    out.append((f"utf16{o}" + ("-bom" if b[:2] in boms else ""), f))
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []
    return out


def astral_dec(t, form=None):
    """Undo astral_enc (any style / outer) -> ASCII text, else None; form pins the byte form (cesu8 also accepts
    mutf8 reads, utf16xx also its -bom)."""
    ok = {"cesu8": ("cesu8", "mutf8"), "mutf8": ("mutf8", "cesu8")}.get(form, (form,))
    return next((s for f, s in astral_reads(t) if form is None or f in ok or f.startswith(form)), None)


def astral_free(p):
    """Speculative Mastery-line decoder: the astral / CESU / overlong reading of a line."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for s in dict.fromkeys(s for _f, s in astral_reads(p))][:2]
    except Exception:   # noqa: BLE001
        return []


_have = {c[0] for c in CANDIDATES}
CANDIDATES += [(f"astral-{f}-{o}", (lambda f, o: lambda s: astral_enc(s, f, o))(f, o),
                (lambda f: lambda t: astral_dec(t, f))(f))
               for f in _ASTRAL_FORMS for o in ("hex", "base64") if f"astral-{f}-{o}" not in _have]
del _have


# ------------------------------------------------- SCSU / BOCU-1 compressed Unicode under a byte layer (hex / base64)
# SCSU (UTS #6): ASCII passes through; 0x80-0xff index the active dynamic window (Latin-1 0x80 by default), 01-08 SQn
# quote one char from window n, 10-17 SCn / 18-1f SDn select / define a window, 0b SDX an astral window (styled math
# letters), 0e SQU / 0f SCU UTF-16 quote / Unicode mode (e0-f1 tags back). Pure ASCII SCSU = identity bytes, so only a
# non-ASCII (styled / accented) read counts. BOCU-1 (UTN #6, ICU): each code point = signed diff from `prev` (0x40 for
# ASCII); printable ASCII = byte + 0x50, space and controls <= 0x20 kept (controls reset prev), ff = reset. ICU
# `uconv -t SCSU|BOCU-1` writes both. Readings must fold to printable ASCII (_astral_fold).
_SCSU_STATIC = (0x0000, 0x0080, 0x0100, 0x0300, 0x2000, 0x2080, 0x2100, 0x3000)
_SCSU_DYN = (0x0080, 0x00C0, 0x0400, 0x0600, 0x0900, 0x3040, 0x30A0, 0xFF00)
_SCSU_SPECIAL = {0xF9: 0x00C0, 0xFA: 0x0250, 0xFB: 0x0370, 0xFC: 0x0530, 0xFD: 0x3040, 0xFE: 0x30A0, 0xFF: 0xFF60}


def _scsu_off(x):
    if 0x01 <= x <= 0x67:
        return x * 0x80
    if 0x68 <= x <= 0xA7:
        return x * 0x80 + 0xAC00
    if x in _SCSU_SPECIAL:
        return _SCSU_SPECIAL[x]
    raise ValueError("reserved SCSU window offset")


def scsu_decode(b):
    """SCSU bytes -> str (UTS #6 decoder; surrogate halves paired), else None."""
    try:
        dyn, win, uni, i, n, cu = list(_SCSU_DYN), 0, False, 0, len(b), []
        while i < n:
            x = b[i]
            i += 1
            if uni:
                if 0xE0 <= x <= 0xE7:
                    win, uni = x - 0xE0, False
                elif 0xE8 <= x <= 0xEF:
                    win, uni, dyn[x - 0xE8] = x - 0xE8, False, _scsu_off(b[i])
                    i += 1
                elif x == 0xF1:
                    h, lo = b[i], b[i + 1]
                    win, uni, dyn[h >> 5] = h >> 5, False, 0x10000 + 0x80 * ((h & 0x1F) << 8 | lo)
                    i += 2
                elif x == 0xF2:
                    return None
                else:
                    if x == 0xF0:
                        x = b[i]
                        i += 1
                    cu.append(x << 8 | b[i])
                    i += 1
            elif x in (0x00, 0x09, 0x0A, 0x0D) or 0x20 <= x < 0x80:
                cu.append(x)
            elif x >= 0x80:
                cu.append(dyn[win] + x - 0x80)
            elif 0x01 <= x <= 0x08:
                y = b[i]
                i += 1
                cu.append(_SCSU_STATIC[x - 1] + y if y < 0x80 else dyn[x - 1] + y - 0x80)
            elif 0x10 <= x <= 0x17:
                win = x - 0x10
            elif 0x18 <= x <= 0x1F:
                win, dyn[x - 0x18] = x - 0x18, _scsu_off(b[i])
                i += 1
            elif x == 0x0B:
                h, lo = b[i], b[i + 1]
                win, dyn[h >> 5] = h >> 5, 0x10000 + 0x80 * ((h & 0x1F) << 8 | lo)
                i += 2
            elif x == 0x0E:
                cu.append(b[i] << 8 | b[i + 1])
                i += 2
            elif x == 0x0F:
                uni = True
            else:
                return None
        out, j = [], 0
        while j < len(cu):
            v = cu[j]
            if 0xD800 <= v < 0xDC00 and j + 1 < len(cu) and 0xDC00 <= cu[j + 1] < 0xE000:
                out.append(chr(0x10000 + ((v - 0xD800) << 10) + cu[j + 1] - 0xDC00))
                j += 2
                continue
            if 0xD800 <= v < 0xE000 or v > 0x10FFFF:
                return None
            out.append(chr(v))
            j += 1
        return "".join(out)
    except (IndexError, ValueError):
        return None


def scsu_encode(s):
    """str -> SCSU bytes (simple writer: ASCII as is, Latin-1 via window 0, an astral 128-block via SDX, else SQU)."""
    out, cur = bytearray(), 0x80
    for c in s:
        v = ord(c)
        if v in (0x00, 0x09, 0x0A, 0x0D) or 0x20 <= v < 0x80:
            out.append(v)
        elif 0x80 <= v < 0x100 and cur == 0x80:
            out.append(v)
        elif v >= 0x10000:
            blk = (v - 0x10000) >> 7
            if cur != 0x10000 + (blk << 7):
                cur = 0x10000 + (blk << 7)
                out += bytes((0x0B, blk >> 8, blk & 0xFF))   # window 0
            out.append(0x80 + (v & 0x7F))
        else:
            out += b"\x0e" + v.to_bytes(2, "big")
    return bytes(out)


_BOCU_TC = 243     # trail count: 0x21..0xff + 20 control trail bytes
_BOCU_R1P, _BOCU_R1N = 63, -64
_BOCU_R2P, _BOCU_R2N = 63 + 43 * 243, -64 - 43 * 243
_BOCU_R3P, _BOCU_R3N = _BOCU_R2P + 3 * 243 ** 2, _BOCU_R2N - 3 * 243 ** 2
_BOCU_CTRL = (1, 2, 3, 4, 5, 6, *range(0x10, 0x1A), 0x1C, 0x1D, 0x1E, 0x1F)
_BOCU_B2T = {b: t for t, b in enumerate(_BOCU_CTRL)}


def _bocu_prev(c):
    if 0x3040 <= c <= 0x309F:
        return 0x3070
    if 0x4E00 <= c <= 0x9FA5:
        return 0x4E00 - _BOCU_R2N
    if 0xAC00 <= c <= 0xD7A3:
        return (0xD7A3 + 0xAC00) // 2
    return (c & ~0x7F) + 0x40


def bocu1_encode(s):
    """str -> BOCU-1 bytes (ICU ucnvbocu.cpp packDiff)."""
    out, prev = bytearray(), 0x40
    for ch in s:
        c = ord(ch)
        if c <= 0x20:
            prev = prev if c == 0x20 else 0x40
            out.append(c)
            continue
        d, prev = c - prev, _bocu_prev(c)
        if _BOCU_R1N <= d <= _BOCU_R1P:
            out.append(0x90 + d)
            continue
        if d > 0:
            lead, k, d = ((0xD0, 1, d - _BOCU_R1P - 1) if d <= _BOCU_R2P else (0xFB, 2, d - _BOCU_R2P - 1)
                          if d <= _BOCU_R3P else (0xFE, 3, d - _BOCU_R3P - 1))
        else:
            lead, k, d = ((0x50, 1, d - _BOCU_R1N) if d >= _BOCU_R2N else (0x25, 2, d - _BOCU_R2N)
                          if d >= _BOCU_R3N else (0x22, 3, d - _BOCU_R3N))
        tr = []
        for _ in range(k):
            d, m = divmod(d, _BOCU_TC)
            tr.append(_BOCU_CTRL[m] if m < 20 else m + 13)
        out += bytes([lead + d] + tr[::-1])
    return bytes(out)


def bocu1_decode(b):
    """BOCU-1 bytes -> str, else None (illegal trail / out-of-range code point / truncated)."""
    try:
        out, prev, i, n = [], 0x40, 0, len(b)
        while i < n:
            x = b[i]
            i += 1
            if x <= 0x20:
                prev = prev if x == 0x20 else 0x40
                out.append(chr(x))
                continue
            if x == 0xFF:
                prev = 0x40
                continue
            if 0x50 <= x < 0xD0:
                d, k = x - 0x90, 0
            elif x >= 0xD0:
                d, k = ((x - 0xD0) * _BOCU_TC + _BOCU_R1P + 1, 1) if x < 0xFB else \
                    ((x - 0xFB) * _BOCU_TC ** 2 + _BOCU_R2P + 1, 2) if x < 0xFE else (_BOCU_R3P + 1, 3)
            else:
                d, k = ((x - 0x50) * _BOCU_TC + _BOCU_R1N, 1) if x >= 0x25 else \
                    ((x - 0x25) * _BOCU_TC ** 2 + _BOCU_R2N, 2) if x > 0x21 else (-_BOCU_TC ** 3 + _BOCU_R3N, 3)
            t = 0
            for y in b[i:i + k] if i + k <= n else None:
                t = t * _BOCU_TC + (y - 13 if y >= 0x21 else _BOCU_B2T[y])
            i += k
            c = prev + d + t
            if not 0 <= c <= 0x10FFFF or 0xD800 <= c < 0xE000:
                return None
            out.append(chr(c))
            prev = _bocu_prev(c)
        return "".join(out)
    except (KeyError, TypeError):
        return None


_COMPRESSED_FORMS = {"scsu": (scsu_encode, scsu_decode), "bocu1": (bocu1_encode, bocu1_decode)}


def compressed_enc(s, form="bocu1", outer="hex", style=None):
    """Text -> `outer` text of its (`style`d, unistyle) SCSU / BOCU-1 bytes."""
    x = unistyle_enc(s, style, space=" ") if style else s
    return _bytes_out(_COMPRESSED_FORMS[form][0](x), outer)


def compressed_reads(t):
    """[(form, text)] for every byte layer x SCSU / BOCU-1 reading of `t` folding to printable ASCII. SCSU must use a
    window / quote tag or a high byte (pure ASCII = identity = plain text, not this family). Never raises."""
    out = []
    try:
        for _layer, b in _bytes_reads(_t(t)):
            if not b:
                continue
            for form, (_e, dec) in _COMPRESSED_FORMS.items():
                if form == "scsu" and max(b) < 0x80 and not any(1 <= x <= 0x1F and x not in (9, 10, 13) for x in b):
                    continue
                s = dec(b)
                if s is None:
                    continue
                f = _astral_fold(s, form == "bocu1")
                if f is not None and not (form == "scsu" and _lenient_utf8(b) is not None):
                    out.append((form, f))
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []
    return out


def compressed_dec(t, form=None):
    """Undo compressed_enc (any style / outer) -> ASCII text, else None; form pins scsu / bocu1."""
    return next((s for f, s in compressed_reads(t) if form is None or f == form), None)


def compressed_free(p):
    """Speculative Mastery-line decoder: the SCSU / BOCU-1 reading of a line."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for s in dict.fromkeys(s for _f, s in compressed_reads(p))][:2]
    except Exception:   # noqa: BLE001
        return []


_have = {c[0] for c in CANDIDATES}
CANDIDATES += [(f"{f}-{o}" + (f"-{st}" if st else ""), (lambda f, o, st: lambda s: compressed_enc(s, f, o, st))(f, o, st),
                (lambda f: lambda t: compressed_dec(t, f))(f))
               for f, st in (("bocu1", None), ("scsu", "bold"), ("bocu1", "bold")) for o in ("hex", "base64")
               if f"{f}-{o}" + (f"-{st}" if st else "") not in _have]
del _have


# ------------------------------------------------- byte-add (Caesar on bytes): c = (p + k) mod 256, hex / base64 / binary
# Not XOR: the decoded bytes are non-printable, c ^ crib has no period, but (c - crib) mod 256 is ONE constant k over
# the whole "Nice work ..." crib (k = (c0 - 0x4e) % 256, every crib byte verified). "Subtract k" = add 256 - k, so one
# family covers both directions (named by the additive k). Wide variant: the text's UTF-16LE/BE code units + k mod
# 65536 (k = unit0 - 'N'), same outers. k = 0 is the bare hex / base64 codec; k = 128 is byte-identical to xor0x80.
def byteadd(b, k, width=1, order="big"):
    if width == 1:
        return bytes((x + k) & 255 for x in b)
    us = [int.from_bytes(b[i:i + 2], order) for i in range(0, len(b) - 1, 2)]
    return b"".join(((u + k) & 0xFFFF).to_bytes(2, order) for u in us)


_BA_WIDE = {"": (1, "big", "utf-8"), "u16le": (2, "little", "utf-16-le"), "u16be": (2, "big", "utf-16-be")}


def _ba_out(b, rep):
    if rep in ("hex", "HEX", "hex-spaced"):
        h = b.hex().upper() if rep == "HEX" else b.hex()
        return " ".join(h[i:i + 2] for i in range(0, len(h), 2)) if rep == "hex-spaced" else h
    if rep in ("binary8", "binary8-nospace"):
        return ("" if rep.endswith("nospace") else " ").join(f"{x:08b}" for x in b)
    if rep == "decimal":
        return " ".join(str(x) for x in b)
    t = (base64.urlsafe_b64encode(b) if rep.startswith("base64url") else base64.b64encode(b)).decode()
    return t.rstrip("=") if rep.endswith("-nopad") else t


def byteadd_enc(s, k, rep="hex", wide=""):
    width, order, enc = _BA_WIDE[wide]
    return _ba_out(byteadd(s.encode(enc), k % (256 if width == 1 else 65536), width, order), rep)


def _ba_reads(t):
    """[(rep, bytes)]: hex / HEX / hex-spaced / base64(url)(-nopad) / binary8(-nospace) / decimal readings."""
    out = []
    t = _t(t) if not isinstance(t, str) else t
    s = t.strip()
    for rep, b in _xor_reads(s):
        if rep in ("hex", "HEX") and re.search(r"[0-9a-fA-F]{2}\s+[0-9a-fA-F]{2}", s) and not re.search(
                r"[0-9a-fA-F]{3}", s):
            rep = "hex-spaced"
        out.append((rep, b))
    for rep, b in _bytes_reads(s):
        if rep == "binary8":
            out.append(("binary8" if re.search(r"\s", s) else "binary8-nospace", b))
        elif rep == "decimal":
            out.append((rep, b))
    return out


def _ba_text(b, enc):
    try:
        x = b.decode(enc)
    except (UnicodeDecodeError, ValueError):
        return None
    return x if x and x.isprintable() and x.isascii() else None


def byteadd_solve(blob, hints=()):
    """(name, sentence, enc) when the blob is a byte layer of the warmups sentence with k added to every byte (or to
    every UTF-16 code unit), k derived from the crib's first unit and verified over the whole crib, else None."""
    try:
        for rep, data in _ba_reads(blob):
            for wide, (width, order, enc) in _BA_WIDE.items():
                crib = _CRIB.encode(enc)
                if len(data) <= len(crib) or len(data) % width:
                    continue
                mod = 256 if width == 1 else 65536
                c0, p0 = int.from_bytes(data[:width], order), int.from_bytes(crib[:width], order)
                k = (c0 - p0) % mod
                if not k or byteadd(crib, k, width, order) != data[:len(crib)]:
                    continue
                got = _ba_text(byteadd(data, -k % mod, width, order), enc)
                if got and got.startswith(_CRIB) and SLUG.fullmatch(got[len(_CRIB):]):
                    name = f"byteadd{k}" + (f"-{wide}" if wide else "") + f"-{rep}"
                    return name, got, (lambda k, rep, wide: lambda s: byteadd_enc(s, k, rep, wide))(k, rep, wide)
    except Exception:  # noqa: BLE001
        return None
    return None


def byteadd_dec(t):
    r = byteadd_solve(t)
    return r[1] if r else None


_BA_SLUGPART = re.compile(r"[a-z]+(?:-[a-z]+)*(?:-\d*)?")


def _ba_piece(x):
    """True when x is a contiguous piece of crib + slug (>= 6 chars): inside the crib, crib tail + slug head, or a
    whole slug."""
    if len(x) < 6:
        return False
    for j in range(len(_CRIB)):
        head = _CRIB[j:]
        if head.startswith(x):
            return True
        if x.startswith(head) and _BA_SLUGPART.fullmatch(x[len(head):]):
            return True
    return bool(SLUG.fullmatch(x))


def byteadd_free(p):
    """Mastery free-text fragment under byte-add (any k 1..255) or UTF-16 unit-add (k from a crib alignment): every
    reading that decodes to a contiguous piece of the sentence."""
    out = []
    try:
        lead = p[:len(p) - len(p.lstrip())]
        for _rep, data in _ba_reads(p):
            if len(data) < 6:
                continue
            for k in range(1, 256):
                x = _ba_text(byteadd(data, -k & 255), "utf-8")
                if x and _ba_piece(x):
                    out.append(lead + x)
            if len(data) % 2:
                continue
            for wide in ("u16le", "u16be"):
                width, order, enc = _BA_WIDE[wide]
                u0 = int.from_bytes(data[:2], order)
                for k in {(u0 - ord(c)) & 0xFFFF for c in set(_CRIB) | set("abcdefghijklmnopqrstuvwxyz-0123456789")}:
                    if not k:
                        continue
                    x = _ba_text(byteadd(data, -k & 0xFFFF, 2, order), enc)
                    if x and _ba_piece(x):
                        out.append(lead + x)
    except Exception:  # noqa: BLE001
        return []
    return list(dict.fromkeys(out))


CANDIDATES.append(("byteadd", lambda s: None, byteadd_dec))


# ------------------------------------------------- byte bit-rotation: each byte ROL r (r = 1..7) or bit-reversed, hex/base64
# CyberChef "Rotate left/right" (Carry through off), x86 rol/ror per byte. Cue: no decoded byte is printable but every
# byte's popcount equals an ASCII letter's (a rotation keeps the 1-bits). ROR r = ROL 8-r (named by the left amount);
# ROL 4 = nibble swap (nibswap-* above, matched first); "bitrev" = each byte's 8 bits mirrored (binary-lsb at byte
# level). Same outer reps as byteadd (hex / HEX / hex-spaced / base64(url)(-nopad) / binary8 / decimal).
def _rolb8(x, r):
    return ((x << r) | (x >> (8 - r))) & 255 if r & 7 else x


_BR_MAPS = {f"rol{r}": bytes(_rolb8(x, r) for x in range(256)) for r in range(1, 8)}
_BR_MAPS["bitrev"] = bytes(int(f"{x:08b}"[::-1], 2) for x in range(256))
_BR_INV = {n: bytes(m.index(x) for x in range(256)) for n, m in _BR_MAPS.items()}
_BR_REVCRIB = ("warmup", "submit", "answer", "Master", "exact")


def byterot_enc(s, op="rol1", rep="hex"):
    return _ba_out(_u(s).translate(_BR_MAPS[op]), rep)


def byterot_solve(blob, hints=()):
    """(name, sentence, enc) when the blob's bytes are the text with every byte rotated (ROL 1-7) or bit-reversed:
    the warmups crib + slug first, else the one op whose read is printable text, else None."""
    try:
        loose = []
        for rep, data in _ba_reads(blob):
            if len(data) < 6 or _ba_text(data, "utf-8"):
                continue
            for op, inv in _BR_INV.items():
                got = _ba_text(data.translate(inv), "utf-8")
                if not got:
                    continue
                enc = (lambda o, r: lambda s: byterot_enc(s, o, r))(op, rep)
                if got.startswith(_CRIB) and SLUG.fullmatch(got[len(_CRIB):]):
                    return f"byte{op}-{rep}", got, enc
                back = got[::-1]   # a reversed sentence is a byte-order codec (bit stream reversed), not this one
                if _texty(got) >= 0.9 and not (_ba_piece(back.strip()) or any(c in back for c in _BR_REVCRIB)):
                    loose.append((f"byte{op}-{rep}", got, enc))
        if len({g for _n, g, _e in loose}) == 1:
            return loose[0]
    except Exception:  # noqa: BLE001
        return None
    return None


def byterot_dec(t):
    r = byterot_solve(t)
    return r[1] if r else None


def byterot_free(p):
    """Mastery free-text fragment under a per-byte rotation / bit reversal: every op whose read is a contiguous
    piece of the warmups sentence."""
    out = []
    try:
        lead = p[:len(p) - len(p.lstrip())]
        for _rep, data in _ba_reads(p):
            if len(data) < 6 or _ba_text(data, "utf-8"):
                continue
            for inv in _BR_INV.values():
                x = _ba_text(data.translate(inv), "utf-8")
                if x and (_ba_piece(x) or x.startswith(_CRIB)):
                    out.append(lead + x)
    except Exception:  # noqa: BLE001
        return []
    return list(dict.fromkeys(out))


CANDIDATES.append(("byterot", lambda s: None, byterot_dec))


# ------------------------------------------------- alternate base-N alphabets: Crockford / z-base-32 / Geohash, crypt / bcrypt / keyed base64
# Same bit stream as RFC 4648 (MSB first, left-aligned), only the alphabet differs -> str.translate to the RFC alphabet,
# then the std decoder. base32: Crockford (0-9A-Z minus I L O U, decoder folds O->0, I/L->1, drops '-'), z-base-32
# (ybndrfg8ejkmcpqxot1uwisza345h769), Geohash (0-9 b-z minus i l o), unpadded or '='-padded. base64: CyberChef's preset
# alphabets (itoa64/crypt ./0-9A-Za-z, bcrypt ./A-Za-z0-9, z64, Radix-64, XML, y64, filename-safe, ROT13, and the
# keyed CTF classics Atom128 / Megan35 / Zong22 / Hazz15 whose 65th char is the pad), crypt64-le = passlib h64
# (md5crypt / phpass: 3 bytes little-endian -> 4 chars LSB first). Any other shuffled / keyword alphabet: keyb64_solve
# recovers char -> sextet from the fixed 87-char sentence crib (exactly 116 chars), the rest by keyword order.
_RFC32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
_RFC64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_ALT32 = {"crockford32": "0123456789ABCDEFGHJKMNPQRSTVWXYZ", "zbase32": "ybndrfg8ejkmcpqxot1uwisza345h769",
          "geohash32": "0123456789bcdefghjkmnpqrstuvwxyz"}
_ALT64 = {"crypt64": "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
          "bcrypt64": "./ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
          "z64": "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/=",
          "radix64": "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/=",
          "xml64": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.",
          "y64": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-",
          "fname64": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=",
          "rot13-64": "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm0123456789+/=",
          "atom128": "/128GhIoPQROSTeUbADfgHijKLM+n0pFWXY456xyzB7=39VaqrstJklmNuZvwcdEC",
          "megan35": "3GHIJKLMNOPQRSTUb=cdefghijklmnopWXYZ/12+406789VaqrstuvwxyzABCDEF5",
          "zong22": "ZKj9n+yf0wDVX1s/5YbdxSo=ILaUpPBCHg8uvNO4klm6iJGhQ7eFrWczAMEq3RTt2",
          "hazz15": "HNO4klm6ij9n+J2hyf0gzA8uvwDEq3X1Q7ZKeFrWcVTts/MRGYbdxSo=ILaUpPBC5"}


def _alt_text(b):
    """Strict text read of decoded bytes: UTF-8, printable, mostly alphanumeric (a wrong alphabet reads as junk)."""
    try:
        s = bytes(b).decode("utf-8")
    except Exception:  # noqa: BLE001
        return None
    return s if s and all(c.isprintable() or c in "\t\r\n" for c in s) and _texty(s) > 0.8 else None


def alt32_enc(s, name, pad=False, lower=False):
    t = base64.b32encode(_u(s)).decode().rstrip("=").translate(str.maketrans(_RFC32, _ALT32[name]))
    t = t.lower() if lower else t
    return t + "=" * (-len(t) % 8) if pad else t


def alt32_bytes(t, name):
    a = _ALT32[name]
    s = re.sub(r"\s+", "", t or "").rstrip("=")
    if name == "crockford32":
        s = s.replace("-", "").upper().translate(str.maketrans("OIL", "011"))
    else:
        s = s.lower()
    if len(s) < 2 or set(s) - set(a) or len(s) % 8 in (1, 3, 6):
        return None
    return base64.b32decode(s.translate(str.maketrans(a, _RFC32)) + "=" * (-len(s) % 8))


def alt32_dec(t, name):
    try:
        b = alt32_bytes(t, name)
    except Exception:  # noqa: BLE001
        return None
    return _alt_text(b) if b else None


def alt64_enc(s, name, pad=False):
    if name == "crypt64-le":
        return h64_enc(s)
    a = _ALT64[name]
    t = base64.b64encode(_u(s)).decode().rstrip("=").translate(str.maketrans(_RFC64, a[:64]))
    return t + (a[64] if len(a) > 64 else "=") * (-len(t) % 4) if pad else t


def alt64_bytes(t, name, alpha=None):
    a = alpha or _ALT64[name]
    s = re.sub(r"\s+", "", t or "")
    p = a[64] if len(a) > 64 else "="
    if p not in a[:64]:
        s = s.rstrip(p)
    if len(s) < 2 or set(s) - set(a[:64]) or len(s) % 4 == 1:
        return None
    return base64.b64decode(s.translate(str.maketrans(a[:64], _RFC64)) + "=" * (-len(s) % 4))


def alt64_dec(t, name):
    try:
        b = h64_bytes(t) if name == "crypt64-le" else alt64_bytes(t, name)
    except Exception:  # noqa: BLE001
        return None
    return _alt_text(b) if b else None


def h64_enc(s):
    """passlib h64.encode_bytes: each 3-byte group little-endian, 6 bits at a time LSB first, over ./0-9A-Za-z."""
    a, b, out = _ALT64["crypt64"], _u(s), []
    for i in range(0, len(b), 3):
        g = b[i:i + 3]
        v = int.from_bytes(g, "little")
        out += [a[v >> 6 * k & 63] for k in range(len(g) + 1)]
    return "".join(out)


def h64_bytes(t):
    a = _ALT64["crypt64"]
    s = re.sub(r"\s+", "", t or "")
    if len(s) < 2 or set(s) - set(a) or len(s) % 4 == 1:
        return None
    out = bytearray()
    for i in range(0, len(s), 4):
        g = s[i:i + 4]
        v = sum(a.index(c) << 6 * k for k, c in enumerate(g))
        n = len(g) - 1
        if v >> 8 * n:   # bits past the last byte must be zero (passlib rejects them)
            return None
        out += v.to_bytes(n, "little")
    return bytes(out)


_KB64_HEAD = base64.b64encode(_u(_CRIB)).decode() if len(_u(_CRIB)) % 3 == 0 else None


_KB64_SLUGB = frozenset(b"abcdefghijklmnopqrstuvwxyz0123456789-")


def _kb64_keyword(m, inv, want=""):
    """Keyword alphabets (dedup(keyword) + the rest of the std / url alphabet in std order). Low sextets (the keyword's
    slots) never occur in ASCII's base64, so read the keyword set K off the tail instead: for a keyword length k, the
    crib-placed chars at positions >= k keep std order and each gap between two of them holds exactly as many tail
    chars as their position difference says -- every unplaced char of a gap is all-tail or all-keyword. K's unplaced
    chars fill the prefix holes (<= 10; only the ones in `want` permuted). Yields char -> sextet maps, None after each k
    (a longer k only adds freedom: the shortest k that reads is the keyword)."""
    pos = {c: _RFC64.index(x) for c, x in m.items()}
    for base in (_RFC64, _RFC64[:62] + "-_"):
        bi = {c: i for i, c in enumerate(base)}
        if any(c not in bi for c in m):
            continue
        for k in range(1, 33):
            tail = sorted((c for c in m if pos[c] >= k), key=bi.get)
            ranks = [pos[c] - k for c in tail]
            if any(b <= a for a, b in zip(ranks, ranks[1:])):
                continue
            kw0 = {c for c in m if pos[c] < k}
            holes = [i for i in range(k) if _RFC64[i] not in inv]
            bounds = [(-1, -1)] + [(bi[c], r) for c, r in zip(tail, ranks)] + [(len(base), 64 - k)]
            opts, n = [], 1
            for (j1, r1), (j2, r2) in zip(bounds, bounds[1:]):
                unpl = [c for c in base[j1 + 1:j2] if c not in m]
                extra = len(unpl) - (r2 - r1 - 1)   # how many of the gap's unplaced chars are keyword chars
                if extra < 0 or extra > len(holes):
                    n = 0
                    break
                opts.append(list(itertools.combinations(unpl, extra)))
                n *= len(opts[-1])
            if not n or n > 256 or len(holes) > 10:
                continue
            for pick in itertools.product(*opts):
                unk = [c for g in pick for c in g]
                if len(unk) != len(holes):
                    continue
                kw = kw0 | set(unk)
                rest = [c for c in base if c not in kw]
                used = [c for c in unk if c in want]   # only the slug's unknown chars need every slot
                idle = [c for c in unk if c not in want]
                for hs in itertools.permutations(holes, len(used)):
                    fill = dict(zip(hs, used))
                    fill.update(zip([h for h in holes if h not in fill], idle))
                    alpha = [fill.get(i) or inv[_RFC64[i]] for i in range(k)] + rest
                    if all(alpha[pos[c]] == c for c in m):
                        yield {c: _RFC64[i] for i, c in enumerate(alpha)}
            yield None   # end of keyword length k: the caller keeps the shortest k that reads


def _kb64_csp(rest, m, limit=2, budget=200000):
    """Random shuffles: the slug's 4-char groups after the crib, each unknown char given a free sextet so every
    decoded byte is a slug byte. Yields the assignment only when it is the unique one (<= `budget` tries)."""
    free = [x for x in _RFC64 if x not in set(m.values())]
    groups = [rest[i:i + 4] for i in range(0, len(rest), 4)]
    sols, tries = [], [0]

    def rec(gi, asg, used):
        if len(sols) >= limit or tries[0] > budget:
            return
        if gi == len(groups):
            sols.append(dict(asg))
            return
        g = groups[gi]
        unk = [c for c in dict.fromkeys(g) if c not in m and c not in asg]
        for q in itertools.permutations([x for x in free if x not in used], len(unk)):
            tries[0] += 1
            a2 = {**asg, **dict(zip(unk, q))}
            std = "".join(m.get(c) or a2[c] for c in g)
            try:
                b = base64.b64decode(std + "=" * (-len(std) % 4))
            except Exception:  # noqa: BLE001
                continue
            if b and all(x in _KB64_SLUGB for x in b):
                rec(gi + 1, a2, used | set(q))

    if len(rest) % 4 != 1:
        rec(0, {}, frozenset())
    if len(sols) == 1 and tries[0] <= budget:
        yield {**m, **sols[0]}


def keyb64_solve(blob):
    """(name, sentence, enc) when the blob is the warmups sentence base64'd over a shuffled / keyword alphabet: the
    87-byte crib fixes the first 116 chars' sextets (char -> value, must be a bijection); chars the crib never used are
    placed by keyword order (dedup(keyword) + the std rest), else by the unique assignment whose slug bytes are all
    [a-z0-9-]. None otherwise (an ambiguous random shuffle: the GM must judge, not a guess)."""
    try:
        s = re.sub(r"\s+", "", reader_text(blob) or "")
        head = _KB64_HEAD
        if not head or len(s) < len(head) + 4 or s.startswith(head):
            return None
        m = {}
        for c, x in zip(s, head):
            if m.setdefault(c, x) != x:
                return None
        if len(set(m.values())) != len(m):
            return None
        last = s[-1]
        tails = [s.rstrip(last), s] if last not in m else [s]   # a pad char the crib never used: drop its run
        inv = {x: c for c, x in m.items()}
        for tail in tails:
            if len(tail) % 4 == 1:
                continue
            for gen in (_kb64_keyword(m, inv, set(tail[len(head):])), _kb64_csp(tail[len(head):], m)):
                hits = {}
                for mm in itertools.islice(gen, 4096):
                    if mm is None:
                        if hits:
                            break
                        continue
                    std = "".join(mm.get(c, "") for c in tail)
                    if len(std) != len(tail):
                        continue
                    try:
                        got = base64.b64decode(std + "=" * (-len(std) % 4)).decode("utf-8")
                    except Exception:  # noqa: BLE001
                        continue
                    if got.startswith(_CRIB) and SLUG.fullmatch(got[len(_CRIB):]):
                        hits.setdefault(got, mm)
                if len(hits) != 1:   # none, or an ambiguous fill: never guess
                    continue
                got, mm = next(iter(hits.items()))
                iv = {x: c for c, x in mm.items()}
                alpha = "".join(iv.get(x, "?") for x in _RFC64)
                pad = s[len(tail):len(tail) + 1]
                enc = (lambda a, p: lambda x: (lambda t: t + p * (-len(t) % 4) if p else t)(
                    base64.b64encode(_u(x)).decode().rstrip("=").translate(str.maketrans(_RFC64, a))))(alpha, pad)
                return f"keyb64:{alpha}" + (f"|pad{pad}" if pad else ""), got, enc
    except Exception:  # noqa: BLE001
        return None
    return None


def keyb64_dec(t):
    r = keyb64_solve(t)
    return r[1] if r else None


def altbase_free(p):
    """Mastery free-text fragment under an alternate base32 / base64 alphabet: every alphabet whose read is text."""
    out = []
    lead = p[:len(p) - len(p.lstrip())]
    for n in _ALT32:
        x = alt32_dec(p, n)
        if x:
            out.append(lead + x)
    for n in list(_ALT64) + ["crypt64-le"]:
        x = alt64_dec(p, n)
        if x:
            out.append(lead + x)
    return list(dict.fromkeys(out))


CANDIDATES += [(n + ("-lower" if lo else "") + ("-pad" if pad else ""),
                (lambda n, pad, lo: lambda s: alt32_enc(s, n, pad, lo))(n, pad, lo), (lambda n: lambda t: alt32_dec(t, n))(n))
               for n in _ALT32 for pad in (False, True) for lo in ((False, True) if n == "crockford32" else (False,))]
CANDIDATES += [(n + ("-pad" if pad else ""), (lambda n, pad: lambda s: alt64_enc(s, n, pad))(n, pad),
                (lambda n: lambda t: alt64_dec(t, n))(n))
               for n in list(_ALT64) + ["crypt64-le"] for pad in (False, True) if not (pad and n == "crypt64-le")]
CANDIDATES.append(("keyed-base64", lambda s: None, keyb64_dec))


# ------------------------------------- checksummed base-N (speculative, coverage atlas target bech32-base58check)
# Crypto-address dress. bech32 / bech32m (BIP173 / BIP350): hrp + '1' + 5-bit symbols of 'qpzry9x8gf2tvdw0s3jn54khce6mua7l',
# last 6 = BCH checksum (polymod const 1 / 0x2bc830a3), data regrouped 5->8 bits (pad bits < 5 and zero); a segwit
# shape carries one witness-version symbol before the regrouped program. No 90-char limit (a sentence is ~160 chars).
# base58check: base58 (bitcoin / Ripple / Flickr alphabet) of version + payload + sha256d(version + payload)[:4]; the
# decoder verifies the checksum then strips 1 version byte (-nover: none). The checksum is the gate: a flipped symbol
# or an unchecked base58 line reads as None.
_BECH = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
_BECH_CONST = {"bech32": 1, "bech32m": 0x2bc830a3}
_B58_RIPPLE = "rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz"
_B58_FLICKR = "123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"
_B58S = {"bitcoin": _B58, "ripple": _B58_RIPPLE, "flickr": _B58_FLICKR}


def _bech_polymod(vals):
    gen = (0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3)
    chk = 1
    for v in vals:
        top = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ v
        for i in range(5):
            chk ^= gen[i] if (top >> i) & 1 else 0
    return chk


def _bech_hrp(h):
    return [ord(c) >> 5 for c in h] + [0] + [ord(c) & 31 for c in h]


def _regroup(data, frm, to, pad):
    acc = bits = 0
    out = []
    for v in data:
        acc = (acc << frm | v) & 0xffffff
        bits += frm
        while bits >= to:
            bits -= to
            out.append(acc >> bits & ((1 << to) - 1))
    if pad:
        if bits:
            out.append(acc << (to - bits) & ((1 << to) - 1))
    elif bits >= frm or acc << (to - bits) & ((1 << to) - 1):
        return None
    return out


def bech32_enc(s, variant="bech32", hrp="ctf", witver=None):
    d = ([witver] if witver is not None else []) + _regroup(_u(s), 8, 5, True)
    chk = _bech_polymod(_bech_hrp(hrp) + d + [0] * 6) ^ _BECH_CONST[variant]
    return hrp + "1" + "".join(_BECH[x] for x in d + [chk >> 5 * (5 - i) & 31 for i in range(6)])


def bech32_parse(t):
    """(variant, hrp, 5-bit data without checksum) of a checksum-valid bech32 / bech32m string, else None."""
    t = t.strip() if isinstance(t, str) else ""
    if not t or t != t.lower() and t != t.upper():
        return None
    t = t.lower()
    pos = t.rfind("1")
    if pos < 1 or pos + 7 > len(t) or any(not 33 <= ord(c) <= 126 for c in t[:pos]):
        return None
    data = [_BECH.find(c) for c in t[pos + 1:]]
    if -1 in data:
        return None
    pm = _bech_polymod(_bech_hrp(t[:pos]) + data)
    for v, k in _BECH_CONST.items():
        if pm == k:
            return v, t[:pos], data[:-6]
    return None


def _chk_text(x):
    return bool(x) and all(c.isprintable() or c in "\t\r\n" for c in x)


def bech32_dec(t, variant=None):
    """The text of a checksum-valid bech32 / bech32m line (variant: only that constant), plain or segwit-shaped."""
    try:
        r = bech32_parse(t)
        if not r or variant and r[0] != variant:
            return None
        for skip in (0, 1):
            b = _regroup(r[2][skip:], 5, 8, False)
            if b:
                try:
                    x = bytes(b).decode("utf-8")
                except UnicodeDecodeError:
                    continue
                if _chk_text(x):
                    return x
    except Exception:  # noqa: BLE001
        pass
    return None


def b58x_enc(b, alpha=_B58):
    n = int.from_bytes(b, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = alpha[r] + out
    return alpha[0] * (len(b) - len(b.lstrip(b"\0"))) + out


def b58x_dec(t, alpha=_B58):
    """Bytes of a base58 string in `alpha` (leading alpha[0] = zero bytes), None on a foreign symbol."""
    t = t.strip() if isinstance(t, str) else ""
    n = 0
    for c in t:
        i = alpha.find(c)
        if i < 0:
            return None
        n = n * 58 + i
    if not t:
        return None
    return b"\0" * (len(t) - len(t.lstrip(alpha[0]))) + (n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b"")


def _sha256d4(b):
    import hashlib
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()[:4]


def b58check_enc(s, alpha="bitcoin", ver=b"\0"):
    p = ver + _u(s)
    return b58x_enc(p + _sha256d4(p), _B58S[alpha])


def b58check_dec(t, alpha="bitcoin", ver=1):
    """Payload text of a base58check string: checksum verified, `ver` leading version bytes stripped; else None."""
    try:
        b = b58x_dec(t, _B58S[alpha])
        if not b or len(b) < 5 + ver or _sha256d4(b[:-4]) != b[-4:]:
            return None
        x = b[ver:-4].decode("utf-8")
        return x if _chk_text(x) else None
    except Exception:  # noqa: BLE001
        return None


def chkbase_free(p):
    """Mastery free-text line under bech32 / bech32m / base58check (any alphabet): checksum-gated reads only."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        outs = [bech32_dec(p)] + [b58check_dec(p, a, v) for a in _B58S for v in (1, 0)]
        return [lead + x for x in dict.fromkeys(o for o in outs if o)][:2]
    except Exception:  # noqa: BLE001
        return []


CANDIDATES += [(v + ("-segwit" if w is not None else ""),
                (lambda v, w: lambda s: bech32_enc(s, v, witver=w))(v, w), (lambda v: lambda t: bech32_dec(t, v))(v))
               for v in _BECH_CONST for w in (None, 0 if v == "bech32" else 1)]
CANDIDATES += [(f"base58check-{a}" + ("" if ver else "-nover"),
                (lambda a, ver: lambda s: b58check_enc(s, a, b"\0" * ver))(a, ver),
                (lambda a, ver: lambda t: b58check_dec(t, a, ver))(a, ver))
               for a in _B58S for ver in (1, 0)]
CANDIDATES += [(f"base58-{a}", (lambda a: lambda s: b58x_enc(_u(s), _B58S[a]))(a),
                (lambda a: lambda t: _t(b58x_dec(t, _B58S[a])))(a)) for a in ("ripple", "flickr")]


# --------------------------------- 256-glyph byte maps (speculative, coverage atlas target base256-glyph-bytes)
# "An alphabet as big as a byte": one glyph per byte. Offset blocks = chr(base + b) for one 256-wide window (Braille
# U+2800+b, U+0100+b, any aligned block, or base = min - 0x20 when a space byte sets the low edge); base256emoji
# (multiformats / py-multibase: a fixed 256-emoji table, optional multibase prefix 🚀 = table[0]); cp437 (codec, or
# the graphic glyphs ☺☻♥.. for 0x00-0x1f / ⌂ 0x7f) and Latin-1 (ord < 256) renderings of an inner byte layer. Bytes ->
# UTF-8 text, else the inner layer (decode_chunk of the text, or the compressor sweep over the raw bytes). Strict:
# offset forms need every glyph non-ASCII (an ASCII space kept as 0x20 allowed); cp437 / Latin-1 need >= 1 non-ASCII
# glyph and an inner layer that reads back; an unaligned (min - 0x20) base must read English. VS15/VS16 presentation selectors are dropped. Never raises.
_B256E = "🚀🪐☄🛰🌌🌑🌒🌓🌔🌕🌖🌗🌘🌍🌏🌎🐉☀💻🖥💾💿😂❤😍🤣😊🙏💕😭😘👍😅👏😁🔥🥰💔💖💙😢🤔😆🙄💪😉☺👌🤗💜😔😎😇🌹🤦🎉💞✌✨🤷😱😌🌸🙌😋💗💚😏💛🙂💓🤩😄😀🖤😃💯🙈👇🎶😒🤭❣😜💋👀😪😑💥🙋😞😩😡🤪👊🥳😥🤤👉💃😳✋😚😝😴🌟😬🙃🍀🌷😻😓⭐✅🥺🌈😈🤘💦✔😣🏃💐☹🎊💘😠☝😕🌺🎂🌻😐🖕💝🙊😹🗣💫💀👑🎵🤞😛🔴😤🌼😫⚽🤙☕🏆🤫👈😮🙆🍻🍃🐶💁😲🌿🧡🎁⚡🌞🎈❌✊👋😰🤨😶🤝🚶💰🍓💢🤟🙁🚨💨🤬✈🎀🍺🤓😙💟🌱😖👶🥴▶➡❓💎💸⬇😨🌚🦋😷🕺⚠🙅😟😵👎🤲🤠🤧📌🔵💅🧐🐾🍒😗🤑🌊🤯🐷☎💧😯💆👆🎤🙇🍑❄🌴💣🐸💌📍🥀🤢👅💡💩👐📸👻🤐🤮🎼🥵🚩🍎🍊👼💍📣🥂"
_B256E_IX = {c: i for i, c in enumerate(_B256E)}
_CP437G = " ☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼"
_CP437_IX = {c: i for i, c in enumerate(_CP437G) if i}
_CP437_IX["⌂"] = 0x7F
_GB_BASES = {"braille": 0x2800, "u0100": 0x100}


def glyph_bytes_enc(s, form="braille"):
    """One glyph per UTF-8 byte: form = braille / u0100 / a hex base ('0x3000') / base256emoji[-mb]."""
    b = _u(s)
    if form.startswith("base256emoji"):
        return ("🚀" if form.endswith("-mb") else "") + "".join(_B256E[x] for x in b)
    base = _GB_BASES.get(form)
    return "".join(chr((int(form, 16) if base is None else base) + x) for x in b)


def _gb_cp437(t):
    try:
        return t.encode("cp437")
    except UnicodeEncodeError:
        pass
    out = bytearray()
    for c in t:
        v = _CP437_IX.get(c)
        if v is None:
            try:
                v = c.encode("cp437")[0]
            except UnicodeEncodeError:
                return None
        out.append(v)
    return bytes(out)


def glyph_bytes_reads(t):
    """[(form, bytes)] for every 256-glyph byte-map reading of `t` (no text gate yet). Never raises."""
    out = []
    try:
        if not isinstance(t, str):
            return []
        t = t.strip().replace("️", "").replace("︎", "")
        if len(t) < 2 or len(t) > 50000 or t.isascii():
            return []
        if all(c in _B256E_IX for c in t):
            b = bytes(_B256E_IX[c] for c in t)
            if t[0] == "🚀":
                out.append(("base256emoji-mb", b[1:]))
            out.append(("base256emoji", b))
        g = [ord(c) for c in t if c != " "]
        if g and min(g) >= 0x80 and max(g) - min(g) < 256:
            lo, hi = min(g), max(g)
            for base in dict.fromkeys((lo & ~0xFF, lo & ~0x7F, lo - 0x20, hi & ~0xFF)):
                if 0 < base <= lo and hi - base <= 255 and (" " not in t or base >= 0x100):
                    b = bytes(0x20 if c == " " else ord(c) - base for c in t)
                    out.append(({0x2800: "braille", 0x100: "u0100"}.get(base, f"0x{base:x}"), b))
        if all(ord(c) < 256 for c in t):
            out.append(("latin1", t.encode("latin-1")))
        b = _gb_cp437(t)
        if b is not None and (not out or out[-1][1] != b):
            out.append(("cp437", b))
    except Exception:   # noqa: BLE001
        return []
    return out


def _gb_ascii(b):
    s = _txt(b)
    return s if s and s.isascii() and _texty(s) >= 0.7 else None


def glyph_bytes_texts(t, form=None, inner=True):
    """[(form, text)] readings: direct UTF-8 text, else (inner) decode_chunk of that text / the compressor sweep over
    the raw bytes. Offset / emoji forms read direct; cp437 / Latin-1 only through an inner layer."""
    out = []
    try:
        for f, b in glyph_bytes_reads(t):
            if form and f != form:
                continue
            s = _gb_ascii(b) if f not in ("cp437", "latin1") else None
            loose = f.startswith("0x") and int(f, 16) % 0x80   # min - 0x20 guess: English only, no inner layer
            if s and loose and not (SLUG.search(s) or _kbd_score(s) >= _RD_OK):
                continue
            if s:
                out.append((f, s))
            if not inner or not b or loose:
                continue
            if s and not SLUG.search(s):
                from lib.decode import decode_chunk
                x = safe(decode_chunk, s)
                if x and x != s and x.isascii() and (SLUG.search(x) or _kbd_score(x) > _kbd_score(s)):
                    out.append((f + "+chunk", x))
            if not s:
                x = safe(decompress_dec, b)
                if x:
                    out.append((f + "+squeeze", x))
    except Exception:   # noqa: BLE001
        return []
    return out


def glyph_bytes_dec(t, form=None):
    """The sentence under a 256-glyph byte map (slug-bearing reading first), else None."""
    r = [s for _f, s in glyph_bytes_texts(t, form)]
    return next((s for s in r if SLUG.search(s)), None) or max((s for s in r if _kbd_score(s) >= _RD_OK),
                                                                key=_kbd_score, default=None)


def glyph_bytes_free(p):
    """Speculative Mastery-line decoder: the English direct 256-glyph byte-map readings of a fragment, best first."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        r = dict.fromkeys(s for f, s in glyph_bytes_texts(p, inner=False)   # named maps: any text; else English
                          if f in ("braille", "u0100", "base256emoji", "base256emoji-mb") or _kbd_score(s) >= _RD_OK)
        return [lead + s for s in sorted(r, key=_kbd_score, reverse=True)][:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES += [(f"glyph-bytes-{f}", (lambda f: lambda s: glyph_bytes_enc(s, f))(f),
                (lambda f: lambda t: glyph_bytes_dec(t, f))(f))
               for f in ("braille", "u0100", "base256emoji", "base256emoji-mb")]
CANDIDATES.append(("glyph-bytes", lambda s: None, glyph_bytes_dec))


# --------------------------------- compressor sweep (speculative, coverage atlas target compression-family-sweep)
# D21 = std padded base64 of gzip ("A familiar wrapper. Something compressed inside."). The lane turns ONE knob a day
# (D19 -> D20), so expect the same wrapper with another squeeze or the same gzip under another wrapper: every wrapper
# reading (base64 std / url, padded or not; hex any case / spaced / 0x; base32 any case / pad; ascii85 / base85; 8-bit
# binary; decimal) x a magic sniff (1f8b gzip, zlib CMF/FLG % 31, BZh bz2, fd377a585a00 xz, lzma-alone props + 0x00
# range-coder byte, zstd 28b52ffd, lz4 frame 04224d18) -> bounded decompress of COMPLETE streams (concatenated
# members allowed); raw deflate by trial (wbits -15) when no magic. Text = printable ASCII. Never raises.
_DZ_MAX = 1 << 20
_A85 = re.compile(r"(?:<~)?[!-uz\s]+(?:~>)?")
_B85 = re.compile(r"[0-9A-Za-z!#$%&()*+\-;<=>?@^_`{|}~]+")
_Z85_ABC = string.digits + string.ascii_lowercase + string.ascii_uppercase + ".-:+=^!/*?&<>()[]{}@%$#"
_B85_ABC = string.digits + string.ascii_uppercase + string.ascii_lowercase + "!#$%&()*+-;<=>?@^_`{|}~"
_Z85_TO_B85 = str.maketrans(_Z85_ABC, _B85_ABC)


def _dz_wrappers(t):
    """[(wrapper, bytes)] for every text wrapper `t` strictly parses as (labels re-encode via _dz_out)."""
    if isinstance(t, (bytes, bytearray)):
        b = bytes(t)
        out = [("raw", b)]
        try:
            t = b.decode("ascii")
        except UnicodeDecodeError:
            return out
    else:
        out = []
    s = t.strip() if isinstance(t, str) else ""
    if not s or len(s) > 400000:
        return out
    flat = re.sub(r"\s+", "", s)
    h = re.sub(r"(?i)0x|\\x|[:,\-]", "", flat)
    if h and re.fullmatch(r"[0-9a-fA-F]+", h) and len(h) % 2 == 0:
        out.append(("HEX" if h.isupper() and not h.isdigit() else "hex-spaced" if flat != s else "hex",
                    bytes.fromhex(h)))
    toks = s.split()
    if re.fullmatch(r"[01]+", flat) and len(flat) % 8 == 0 and all(len(x) % 8 == 0 for x in toks):
        out.append(("binary8" if len(toks) > 1 else "binary8-nospace",
                    bytes(int(flat[i:i + 8], 2) for i in range(0, len(flat), 8))))
    if len(toks) > 1 and all(x.isdigit() and int(x) < 256 for x in toks):
        out.append(("decimal", bytes(int(x) for x in toks)))
    u = flat.rstrip("=")
    if re.fullmatch(r"[A-Za-z0-9+/\-_]+", u) and len(u) % 4 != 1 and not ("+" in u or "/" in u) & ("-" in u or "_" in u):
        url = "-" in u or "_" in u
        try:
            out.append((("base64url" if url else "base64") + ("" if u != flat or len(u) % 4 == 0 else "-nopad"),
                        base64.b64decode(u.replace("-", "+").replace("_", "/") + "=" * (-len(u) % 4), validate=True)))
        except (ValueError, TypeError):
            pass
    if re.fullmatch(r"[A-Z2-7]+|[a-z2-7]+", u) and len(u) % 8 in (0, 2, 4, 5, 7):
        try:
            out.append(("base32" + ("-lower" if u.islower() else "") + ("" if u != flat or len(u) % 8 == 0 else "-nopad"),
                        base64.b32decode(u.upper() + "=" * (-len(u) % 8))))
        except (ValueError, TypeError):
            pass
    if _A85.fullmatch(s):
        try:
            out.append(("ascii85-armored" if s.startswith("<~") else "ascii85",
                        base64.a85decode(s, adobe=s.startswith("<~") and s.endswith("~>"), ignorechars=" \t\r\n")))
        except (ValueError, TypeError):
            pass
    if _B85.fullmatch(flat):
        try:
            out.append(("base85", base64.b85decode(flat)))
        except (ValueError, TypeError):
            pass
    if len(flat) % 5 == 0 and all(c in _Z85_ABC for c in flat):
        try:
            out.append(("z85", base64.b85decode(flat.translate(_Z85_TO_B85))))
        except (ValueError, TypeError):
            pass
    return out


def _dz_out(b, wrapper):
    """bytes -> `wrapper` text (a _dz_wrappers label)."""
    if wrapper == "raw":
        return b.decode("latin-1")
    if wrapper.startswith("base64"):
        x = (base64.urlsafe_b64encode(b) if wrapper.startswith("base64url") else base64.b64encode(b)).decode()
        return x.rstrip("=") if wrapper.endswith("-nopad") else x
    if wrapper.startswith("base32"):
        x = base64.b32encode(b).decode()
        x = x.lower() if "-lower" in wrapper else x
        return x.rstrip("=") if wrapper.endswith("-nopad") else x
    if wrapper == "binary8-nospace":
        return "".join(f"{x:08b}" for x in b)
    if wrapper == "ascii85-armored":
        return base64.a85encode(b, adobe=True).decode()
    if wrapper == "z85":
        return base64.b85encode(b + b"\0" * (-len(b) % 4)).decode().translate(str.maketrans(_B85_ABC, _Z85_ABC))
    return _bytes_out(b, wrapper)


def _dz_kind(b):
    """The compressor a byte string's magic names, else 'deflate' (raw, by trial)."""
    if b[:2] == b"\x1f\x8b":
        return "gzip"
    if len(b) > 2 and b[0] & 0x0F == 8 and b[0] >> 4 <= 7 and (b[0] << 8 | b[1]) % 31 == 0:
        return "zlib-dict" if b[1] & 0x20 else "zlib"
    if b[:3] == b"BZh" and b[3:4] in (b"1", b"2", b"3", b"4", b"5", b"6", b"7", b"8", b"9"):
        return "bz2"
    if b[:6] == b"\xfd7zXZ\x00":
        return "xz"
    if len(b) >= 18 and b[0] < 225 and b[13] == 0 and b[0] in (0x5D, 0x5E, 0x2C, 0x5B, 0x6C, 0x09, 0x03, 0x00):
        return "lzma"
    if b[:4] == b"\x28\xb5\x2f\xfd":
        return "zstd"
    if b[:4] == b"\x04\x22\x4d\x18":
        return "lz4"
    if b[:10] == _SNAPPY_ID:
        return "snappy"
    return "deflate"


def _dz_obj(kind):
    import bz2
    import lzma
    if kind in ("gzip", "zlib", "deflate"):
        return zlib.decompressobj({"gzip": 31, "zlib": 15, "deflate": -15}[kind])
    if kind == "bz2":
        return bz2.BZ2Decompressor()
    if kind in ("xz", "lzma"):
        return lzma.LZMADecompressor(lzma.FORMAT_XZ if kind == "xz" else lzma.FORMAT_ALONE, memlimit=1 << 26)
    return None


def _dz_stream(kind, b):
    """(output, unused) of ONE complete `kind` stream at the head of `b`, else None (truncated / corrupt / bomb)."""
    try:
        if kind == "zstd":
            import zstandard
            d = zstandard.ZstdDecompressor().decompressobj()
            out = d.decompress(b)
            return (out, d.unused_data) if d.eof and len(out) <= _DZ_MAX else None
        if kind == "lz4":
            import lz4.frame
            d = lz4.frame.LZ4FrameDecompressor()
            out = d.decompress(b, max_length=_DZ_MAX)
            return (out, d.unused_data or b"") if d.eof else None   # unused_data is None when nothing trails
        if kind == "brotli":
            import brotli
            d = brotli.Decompressor()
            out = d.process(b, output_buffer_limit=_DZ_MAX)
            return (out, b"") if d.is_finished() and len(out) <= _DZ_MAX else None
        if kind == "snappy":
            out = _snappy_framed(b)
            return None if out is None else (out, b"")
        if kind == "snappy-raw":
            out = _snappy_raw(b)
            return None if out is None else (out, b"")
        if kind == "zlib-dict":
            zd = _zd_lookup(b)
            if zd is None:
                return None
            d = zlib.decompressobj(15, zdict=zd)
            out = d.decompress(b, _DZ_MAX)
            return (out, d.unused_data) if d.eof else None
        d = _dz_obj(kind)
        out = d.decompress(b, _DZ_MAX)
        return (out, d.unused_data) if d.eof else None
    except Exception:   # noqa: BLE001 -- zlib.error / OSError / LZMAError / EOFError / ImportError
        return None


# Third-party squeezes (coverage atlas target third-party-compressors): zstd / lz4 frame sniffed above; snappy framed
# (stream id ff060000 'sNaPpY', masked CRC-32C per chunk verified) and raw snappy (varint length must match exactly)
# by a pure-python reader; brotli (no magic) by trial after raw deflate fails. Raw snappy / brotli run only when no
# magic matched, and the text gate still applies.
_SNAPPY_ID = b"\xff\x06\x00\x00sNaPpY"
_CRC32C = []
for _i in range(256):
    _c = _i
    for _ in range(8):
        _c = (_c >> 1) ^ (0x82F63B78 if _c & 1 else 0)
    _CRC32C.append(_c)


def _crc32c_masked(b):
    c = 0xFFFFFFFF
    for x in b:
        c = _CRC32C[(c ^ x) & 0xFF] ^ (c >> 8)
    c ^= 0xFFFFFFFF
    return (((c >> 15) | (c << 17)) + 0xA282EAD8) & 0xFFFFFFFF


def _snappy_raw(b):
    """Raw snappy block -> bytes, else None (bad varint / tag / offset / length mismatch / over _DZ_MAX)."""
    n = sh = i = 0
    while True:
        if i >= len(b) or sh > 28:
            return None
        x = b[i]
        n |= (x & 0x7F) << sh
        i, sh = i + 1, sh + 7
        if not x & 0x80:
            break
    if n > _DZ_MAX or n == 0:
        return None
    out = bytearray()
    while i < len(b):
        tag = b[i]
        i += 1
        t = tag & 3
        if t == 0:
            ln = tag >> 2
            if ln >= 60:
                k = ln - 59
                if i + k > len(b):
                    return None
                ln = int.from_bytes(b[i:i + k], "little")
                i += k
            ln += 1
            if i + ln > len(b):
                return None
            out += b[i:i + ln]
            i += ln
        else:
            if t == 1:
                if i >= len(b):
                    return None
                ln, off = 4 + ((tag >> 2) & 7), (tag >> 5) << 8 | b[i]
                i += 1
            else:
                k = 2 if t == 2 else 4
                if i + k > len(b):
                    return None
                ln, off = (tag >> 2) + 1, int.from_bytes(b[i:i + k], "little")
                i += k
            if off == 0 or off > len(out):
                return None
            for _ in range(ln):
                out.append(out[-off])
        if len(out) > n:
            return None
    return bytes(out) if len(out) == n else None


def _snappy_framed(b):
    """Snappy framing format (stream id first; concatenated streams allowed) -> bytes, else None (bad CRC / reserved
    unskippable chunk / truncated)."""
    if b[:10] != _SNAPPY_ID:
        return None
    out, i = bytearray(), 0
    while i < len(b):
        if i + 4 > len(b):
            return None
        typ, ln = b[i], int.from_bytes(b[i + 1:i + 4], "little")
        body, i = b[i + 4:i + 4 + ln], i + 4 + ln
        if len(body) != ln:
            return None
        if typ == 0xFF:
            if body != b"sNaPpY":
                return None
        elif typ in (0, 1):
            if ln < 4:
                return None
            data = body[4:] if typ == 1 else _snappy_raw(body[4:])
            if data is None or _crc32c_masked(data) != int.from_bytes(body[:4], "little"):
                return None
            out += data
            if len(out) > _DZ_MAX:
                return None
        elif typ < 0x80:
            return None
    return bytes(out)


def _snappy_raw_enc(b):
    """A valid raw snappy block (literal runs only: decoders accept it; not byte-identical to a matching compressor)."""
    n, v = len(b), bytearray()
    while True:
        v.append((n & 0x7F) | (0x80 if n > 0x7F else 0))
        n >>= 7
        if not n:
            break
    for j in range(0, len(b), 65536):
        lit = b[j:j + 65536]
        m = len(lit) - 1
        v += bytes([m << 2]) if m < 60 else bytes([(59 + (1 if m < 256 else 2)) << 2]) + m.to_bytes(
            1 if m < 256 else 2, "little")
        v += lit
    return bytes(v)


def _snappy_framed_enc(b):
    out = bytearray(_SNAPPY_ID)
    for j in range(0, len(b), 65536):
        blk = b[j:j + 65536]
        # literal-only never saves the 1/8 the reference writers require -> they (and we) emit an uncompressed chunk
        body = _crc32c_masked(blk).to_bytes(4, "little") + blk
        out += b"\x01" + len(body).to_bytes(3, "little") + body
    return bytes(out)


_GZ_OS = {0: "FAT", 1: "Amiga", 2: "VMS", 3: "Unix", 4: "VM/CMS", 5: "Atari", 6: "HPFS", 7: "Macintosh", 8: "Z-System",
          9: "CP/M", 10: "TOPS-20", 11: "NTFS", 12: "QDOS", 13: "Acorn", 255: "unknown"}


def _gz_header(b):
    """ONE gzip member header at the head of `b` (RFC 1952: FEXTRA / FNAME / FCOMMENT / FHCRC) -> dict (hlen, flg,
    mtime, xfl, os, fextra, fname, fcomment), else None (wrong magic / reserved flag bits / header cut short)."""
    if len(b) < 10 or b[:3] != b"\x1f\x8b\x08" or b[3] & 0xE0:
        return None
    flg, i = b[3], 10
    h = {"flg": flg, "mtime": int.from_bytes(b[4:8], "little"), "xfl": b[8], "os": b[9], "fextra": None,
         "fname": None, "fcomment": None}
    if flg & 4:
        if len(b) < 12:
            return None
        n = int.from_bytes(b[10:12], "little")
        h["fextra"], i = b[12:12 + n], 12 + n
    for bit, key in ((8, "fname"), (16, "fcomment")):
        if flg & bit:
            j = b.find(b"\x00", i)
            if j < 0:
                return None
            h[key], i = b[i:j].decode("latin-1"), j + 1
    i += 2 if flg & 2 else 0
    if i > len(b):
        return None
    h["hlen"] = i
    return h


def _gz_lenient(b):
    """(output, members, tail) of a gzip blob zlib's wbits-31 path rejects: every member = parsed header + raw-deflate
    body (wbits -15) that reaches its final block; a full 8-byte trailer must match CRC32 + ISIZE; the LAST member may
    carry a truncated trailer (0-7 bytes, which must be a prefix of the true one) or be followed by non-gzip trailing
    garbage. tail = trailer bytes present on the last member. None when any body is cut / corrupt or a CRC is wrong."""
    out, rest, n = b"", b, 0
    while True:
        h = _gz_header(rest)
        if h is None:
            return None
        d = zlib.decompressobj(-15)
        try:
            data = d.decompress(rest[h["hlen"]:], _DZ_MAX)
        except zlib.error:
            return None
        if not d.eof or len(out) + len(data) > _DZ_MAX:
            return None
        trl = (zlib.crc32(data).to_bytes(4, "little") + (len(data) & 0xFFFFFFFF).to_bytes(4, "little"))
        got, rest, n = d.unused_data[:8], d.unused_data[8:], n + 1
        if got != trl[:len(got)]:
            return None
        out += data
        if len(got) < 8 or rest[:2] != b"\x1f\x8b":
            return out, n, len(got)


def gzip_hints(t):
    """[{wrapper, member, fname, fcomment, fextra, mtime, xfl, os}] for every gzip member header under any wrapper
    reading of `t`. An FNAME (base64 'H4sICA') may hint the NEXT layer -- surface it in solver notes, NEVER as the
    answer. Never raises."""
    out = []
    try:
        for wrapper, b in _dz_wrappers(t):
            rest, m = b, 0
            while m < 16:
                h = _gz_header(rest)
                if h is None:
                    break
                out.append({"wrapper": wrapper, "member": m, "fname": h["fname"], "fcomment": h["fcomment"],
                            "fextra": h["fextra"].hex() if h["fextra"] is not None else None, "mtime": h["mtime"],
                            "xfl": h["xfl"], "os": _GZ_OS.get(h["os"], h["os"])})
                d = zlib.decompressobj(-15)
                try:
                    d.decompress(rest[h["hlen"]:], _DZ_MAX)
                except zlib.error:
                    break
                if not d.eof:
                    break
                rest, m = d.unused_data[8:], m + 1
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return out
    return out


def _dz_inflate(b):
    """[(kind, bytes)]: the sniffed compressor's output (concatenated members of the same kind allowed, trailing NUL
    padding ignored), then a lenient gzip read (truncated trailer / trailing garbage after a CRC-checked member), then
    raw deflate by trial if that fails."""
    kind = _dz_kind(b)
    for k in dict.fromkeys((kind, "gzip+", "deflate") + (("brotli", "snappy-raw") if kind == "deflate" else ())):
        if k == "gzip+":
            lz = _gz_lenient(b) if kind == "gzip" else None
            if lz and lz[0]:
                return [("gzip", lz[0])]
            continue
        out, rest = b"", b
        while rest:
            got = _dz_stream(k, rest)
            if got is None or len(out) + len(got[0]) > _DZ_MAX:
                out = None
                break
            out, rest = out + got[0], got[1]
            if not rest.strip(b"\x00") or k == "deflate" or _dz_kind(rest) != k:
                rest = rest.strip(b"\x00")
                break
        if out and not rest:
            return [(k, out)]
    return []


# zlib header knobs (coverage atlas target zlib-header-sweep): D22 = base64 of zlib 78da. The next knob may be a
# smaller window (CMF 08..68: b64 'CI'..'aI'), another level (FLG 01/5e/9c/da), raw deflate (no header) or an FDICT
# preset dictionary (FLG bit 5 + DICTID = adler32(dict)). The dictionary is picked by its adler32 among the crib
# sentence's word runs / prefixes / suffixes and the title/prompt words (`_zd_learn(hints)`); no match -> None.
_ZD_EXTRA = {}


def _zd_learn(hints=()):
    """Add the title / prompt words (each hint whole, its words, adjacent word runs, lower/title case) as FDICT
    dictionary candidates."""
    try:
        for h in hints or ():
            if not isinstance(h, str) or not h.strip():
                continue
            ws = re.findall(r"[A-Za-z0-9']+", h)
            runs = [h.strip()] + [" ".join(ws[i:j]) for i in range(len(ws)) for j in range(i + 1, min(len(ws), i + 6) + 1)]
            for r in runs:
                for v in (r, r.lower(), r.title(), r.upper(), r.replace(" ", "")):
                    _ZD_EXTRA.setdefault(zlib.adler32(v.encode()), v.encode())
    except Exception:   # noqa: BLE001
        pass


@functools.lru_cache(maxsize=1)
def _zd_base():
    """{adler32: dict bytes} over the fixed sentence: whole, every prefix / suffix, every word run (+/- a trailing
    space), and lane words."""
    s = _CRIB
    ws = s.split()
    cands = [s, s.strip(), SENTENCE.replace("{slug}", "")] + [s[:i] for i in range(1, len(s) + 1)] + \
        [s[i:] for i in range(len(s))] + ["huntress", "Huntress", "warmup", "warmups", "Game Master", "deflate",
                                          "inflate", "zlib", "dictionary", "answer", "slug"]
    for i in range(len(ws)):
        for j in range(i + 1, len(ws) + 1):
            r = " ".join(ws[i:j])
            cands += [r, r + " ", " " + r, " " + r + " ", r.strip("!:"), r.lower()]
    out = {}
    for c in cands:
        if c:
            out.setdefault(zlib.adler32(c.encode()), c.encode())
    return out


def _zd_lookup(b):
    """The FDICT dictionary whose adler32 is a zlib stream's DICTID, else None."""
    if len(b) < 6:
        return None
    did = int.from_bytes(b[2:6], "big")
    return _ZD_EXTRA.get(did) or _zd_base().get(did)


def zlib_any(b, hints=()):
    """Inflate one zlib-family stream under any header knob: RFC 1950 (any window 08..78, any level, FDICT with a
    crib / hint dictionary), else raw deflate, else gzip/zlib auto-detect (wbits 47). Complete streams only (bounded
    to 1 MiB); None when nothing inflates. Never raises."""
    try:
        b = bytes(b)
        if len(b) < 2:
            return None
        if hints:
            _zd_learn(hints)
        trials = []
        if b[0] & 0x0F == 8 and b[0] >> 4 <= 7 and (b[0] << 8 | b[1]) % 31 == 0:
            if b[1] & 0x20:
                zd = _zd_lookup(b)
                if zd is not None:
                    trials.append((15, zd))
            else:
                trials.append((15, None))
        trials += [(-15, None), (47, None)]
        for wb, zd in trials:
            try:
                d = zlib.decompressobj(wb, zdict=zd) if zd is not None else zlib.decompressobj(wb)
                out = d.decompress(b, _DZ_MAX)
                if d.eof and not d.unused_data.strip(b"\x00"):
                    return out
            except zlib.error:
                continue
    except Exception:   # noqa: BLE001
        return None
    return None


def _dz_text(b):
    try:
        s = b.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if s and s.isascii() and all(c.isprintable() or c in "\t\r\n" for c in s) else None


def decompress_reads(t):
    """[(name, text, kind, wrapper, raw)] for every wrapper x compressor reading of `t` that inflates to printable
    ASCII (name = '<kind>-<wrapper>'). Never raises."""
    out = []
    try:
        for wrapper, b in _dz_wrappers(t):
            if len(b) < 6:
                continue
            for kind, data in _dz_inflate(b):
                s = _dz_text(data)
                if s is not None:
                    out.append((f"{kind}-{wrapper}", s, kind, wrapper, b))
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []
    return out


def decompress_sweep(t, gate=SLUG):
    """The first wrapper x compressor reading of `t` whose text matches `gate` (None = any printable text), else None."""
    return next((s for _n, s, *_r in decompress_reads(t) if gate is None or gate.search(s)), None)


def _dz_enc(kind, raw):
    """A compressor re-encoder that copies the observed stream's knobs (gzip header / zlib level + window / bz2 block
    size / xz check)."""
    import bz2
    import lzma
    if kind == "gzip":
        lvl = {2: 9, 4: 1}.get(raw[8], 6)
        h = _gz_header(raw)
        # the observed header verbatim (mtime / XFL / OS / FEXTRA / FNAME / FCOMMENT / FHCRC: all header-only bytes)
        hdr = raw[:h["hlen"]] if h else b"\x1f\x8b\x08\x00\x00\x00\x00\x00" + raw[8:10]
        lz = None if _dz_stream("gzip", raw) else _gz_lenient(raw)
        tail = lz[2] if lz and lz[1] == 1 else 8   # a single member's truncated trailer is cut the same way

        def gz(b):
            c = zlib.compressobj(lvl, zlib.DEFLATED, -15)
            return hdr + c.compress(b) + c.flush() + (zlib.crc32(b).to_bytes(4, "little") +
                                                      (len(b) & 0xFFFFFFFF).to_bytes(4, "little"))[:tail]
        return gz
    if kind == "zlib":
        lvl, wb = (1, 6, 6, 9)[raw[1] >> 6], (raw[0] >> 4) + 8

        def zl(b):
            c = zlib.compressobj(lvl, zlib.DEFLATED, wb)
            return c.compress(b) + c.flush()
        return zl
    if kind == "zlib-dict":
        lvl, wb, zd = (1, 6, 6, 9)[raw[1] >> 6], (raw[0] >> 4) + 8, _zd_lookup(raw) or b""
        return lambda b: (lambda c: c.compress(b) + c.flush())(zlib.compressobj(lvl, zlib.DEFLATED, wb, zdict=zd))
    if kind == "deflate":
        return lambda b: (lambda c: c.compress(b) + c.flush())(zlib.compressobj(9, zlib.DEFLATED, -15))
    if kind == "bz2":
        return lambda b: bz2.compress(b, int(chr(raw[3])))
    if kind == "xz":
        chk = {0: lzma.CHECK_NONE, 1: lzma.CHECK_CRC32, 4: lzma.CHECK_CRC64, 10: lzma.CHECK_SHA256}.get(raw[7] & 15,
                                                                                                         lzma.CHECK_CRC64)
        return lambda b: lzma.compress(b, lzma.FORMAT_XZ, chk)
    if kind == "lzma":
        return lambda b: lzma.compress(b, lzma.FORMAT_ALONE)
    if kind == "zstd":
        import zstandard
        return lambda b: zstandard.ZstdCompressor().compress(b)
    if kind == "brotli":
        import brotli
        return lambda b: brotli.compress(b)
    if kind == "snappy":
        return _snappy_framed_enc
    if kind == "snappy-raw":
        return _snappy_raw_enc
    import lz4.frame
    flg, bd = (raw[4], raw[5]) if len(raw) > 5 else (0x64, 0x40)   # the observed frame descriptor's knobs

    def lz(b):
        z = lz4.frame.compress(b, block_size=(bd >> 4) & 7 if (bd >> 4) & 7 >= 4 else 0, block_linked=not flg & 0x20,
                               block_checksum=bool(flg & 0x10), content_checksum=bool(flg & 4), store_size=bool(flg & 8))
        # liblz4 marks a one-block frame block-independent; a linked-mode writer (Rust lz4_flex, lz4 CLI) does not:
        # copy the observed B.Indep bit and recompute the descriptor checksum HC = (xxh32(FLG..) >> 8) & 0xFF
        if (z[4] ^ flg) == 0x20:
            dl = 2 + (8 if flg & 8 else 0) + (4 if flg & 1 else 0)
            desc = bytes([flg]) + z[5:4 + dl]
            z = z[:4] + desc + bytes([(_xxh32(desc) >> 8) & 0xFF]) + z[5 + dl:]
        return z
    return lz


def _xxh32(b, seed=0):
    """XXH32 (the lz4 frame descriptor checksum), pure python."""
    p1, p2, p3, p4, p5, m = 2654435761, 2246822519, 3266489917, 668265263, 374761393, 0xFFFFFFFF
    rl = lambda x, r: ((x << r) | (x >> (32 - r))) & m   # noqa: E731
    n, i = len(b), 0
    if n >= 16:
        v = [(seed + p1 + p2) & m, (seed + p2) & m, seed & m, (seed - p1) & m]
        while i + 16 <= n:
            for j in range(4):
                v[j] = (rl((v[j] + int.from_bytes(b[i + 4 * j:i + 4 * j + 4], "little") * p2) & m, 13) * p1) & m
            i += 16
        h = (rl(v[0], 1) + rl(v[1], 7) + rl(v[2], 12) + rl(v[3], 18)) & m
    else:
        h = (seed + p5) & m
    h = (h + n) & m
    while i + 4 <= n:
        h = (rl((h + int.from_bytes(b[i:i + 4], "little") * p3) & m, 17) * p4) & m
        i += 4
    while i < n:
        h = (rl((h + b[i] * p5) & m, 11) * p1) & m
        i += 1
    h = ((h ^ (h >> 15)) * p2) & m
    h = ((h ^ (h >> 13)) * p3) & m
    return h ^ (h >> 16)


# Stacked on D21 (atlas row 140): the inflated text may be ANOTHER seen codec (gzip of hex / rot13 / Morse / base64),
# or an old free transform may sit over the compressed wrapper (reversed / rot13 / Atbash / ROT47 base64 of gzip:
# rot13('H4sI') = 'U4fV', reversed ends 'Is4H'). Undo the free transform only when the blob as-is inflates to nothing;
# re-run nested decompress + decode_chunk + CANDIDATES on an inflated text that isn't English (depth cap 3, slug gate).
_RD_PRE = (("rev", lambda t: t[::-1]), ("rot13", lambda t: rot(t, 13)), ("atbash", atbash), ("rot47", rot47))
_RD_OK = -6.0   # _kbd_score of the plain sentence ~ -3.4, of its rot13 ~ -8, of hex / Morse / base64 <= -11


def _rd_pre_reads(t):
    """[(pre, f, reads)]: decompress_reads of the blob as-is, else of the blob with one free transform undone (all
    involutions, so f also re-applies it)."""
    r = decompress_reads(t)
    if r or not isinstance(t, str):
        return [("", None, r)] if r else []
    return [(pre, f, r) for pre, f in _RD_PRE for r in (decompress_reads(f(t)),) if r]


def _rd_inner(s, depth, deadline):
    """(name, plain, enc|None) for an inflated text `s` that is another codec: a nested squeeze, decode_chunk, then the
    CANDIDATES decoders -- plain slug-gated and more English than `s`; enc = the first CANDIDATES encoder that
    reproduces `s` exactly (None = decodes but can't re-encode)."""
    if depth <= 0:
        return None
    base = _kbd_score(s)
    r = decompress_solve(s, _depth=depth)
    if r and _kbd_score(r[1]) > base:
        return r
    r = xorkey_solve(s)   # XOR of the text, then compressed: the inflated hex / base64 is a crib-keyed xorkey blob
    if r:
        return r
    from lib.decode import decode_chunk
    hit = None
    p = safe(decode_chunk, s)
    if p and SLUG.search(p) and _kbd_score(p) > base:
        hit = ("chunk", p)
    for name, _enc, dec in CANDIDATES:
        if hit or time.monotonic() > deadline:
            break
        if dec is not None and dec is not decompress_dec:
            p = safe(dec, s)
            if p and SLUG.search(p) and _kbd_score(p) > base:
                hit = (name, p)
    if not hit:
        return None
    want = s.strip()
    for name, enc, _dec in CANDIDATES:
        if time.monotonic() > deadline + 0.3:
            break
        if (safe(enc, hit[1]) or "").strip() == want:
            return name, hit[1], enc
    return hit[0], hit[1], None


def decompress_solve(blob, hints=(), _depth=3):
    """(name, sentence, enc) for the first slug-gated wrapper x compressor reading of the blob (after undoing a free
    transform over the wrapper, and re-decoding an inflated text that is another codec), else None."""
    try:
        deadline = time.monotonic() + 0.5
        for pre, f, reads in _rd_pre_reads(blob):
            for name, s, kind, wrapper, raw in reads:
                z = _dz_enc(kind, raw)
                outer = (lambda z, w, f: lambda x: (lambda y: f(y) if f else y)(_dz_out(z(_u(x)), w)))(z, wrapper, f)
                nm = f"{pre}({name})" if pre else name
                if SLUG.search(s) and _kbd_score(s) >= _RD_OK:
                    return nm, s, outer
                rd = _rd_inner(s, _depth - 1, deadline) if _depth > 1 else None
                if rd:
                    ie = rd[2]
                    return (f"{nm}[{rd[0]}]", rd[1], (lambda o, ie: lambda x: (lambda y: y and o(y))(safe(ie, x)))(outer, ie)
                            if ie else (lambda x: None))
                if SLUG.search(s):
                    return nm, s, outer
    except Exception:   # noqa: BLE001
        return None
    return None


def decompress_dec(t):
    r = decompress_solve(t)
    return r[1] if r else None


def _rd_free(s, depth=2):
    """Mastery-fragment re-decodes of an inflated text (no slug in a fragment): nested squeeze + decode_chunk, kept
    only when more English than `s`."""
    if depth <= 0 or _kbd_score(s) >= _RD_OK:
        return []
    from lib.decode import decode_chunk
    base = _kbd_score(s)
    outs = [x for _p, _f, rs in _rd_pre_reads(s) for _n, x, *_r in rs]
    outs = [y for x in outs for y in (_rd_free(x, depth - 1) or [x])]
    outs += [x for x in (safe(decode_chunk, s),) if x]
    return sorted((x for x in dict.fromkeys(outs) if _kbd_score(x) > base), key=_kbd_score, reverse=True)


def decompress_free(p):
    """Speculative Mastery-line decoder: the inflated text of a line (a per-fragment member under any wrapper, maybe
    under a free transform), its re-decode first when the inflated text is another codec."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        outs = [y for _p, _f, rs in _rd_pre_reads(p) for _n, s, *_r in rs for y in _rd_free(s) + [s]]
        return [lead + s for s in dict.fromkeys(outs)][:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES.append(("decompress-sweep", lambda s: None, decompress_dec))


# XOR over a compressed stream (coverage atlas target xor-over-compressed-magic): wrapper decode -> no magic; the
# repeating key = first bytes ^ a known compressor header (gzip 1f8b0800 00000000 xfl os = 10 bytes, bz2 'BZh'+level
# +314159265359 = 10, xz magic+flags+crc32 = 12, lzma-alone props+dict+size = 13, zip local header = 10, zstd 4,
# zlib 78xx = 2), cut at the smallest period that fits (1..10). zlib's 2 known bytes leave key bytes 2.. of a
# period-3/4 key open: those are swept (any byte for 3, letters for 4) behind a cheap prefix-inflate filter. Title /
# prompt words are tried as keys too. The reverse order (XOR of the text, then compressed) is decompress_solve's
# inflated text routed into xorkey_solve.
def _xz_hdrs():
    out = [("gzip", b"\x1f\x8b\x08\x00\x00\x00\x00\x00" + bytes([x, o])) for x in (0, 2, 4) for o in (3, 255, 0, 11, 7)]
    out += [("bz2", b"BZh" + bytes([d]) + b"\x31\x41\x59\x26\x53\x59") for d in b"987654321"]
    out += [("xz", b"\xfd7zXZ\x00\x00" + bytes([c]) + zlib.crc32(bytes([0, c])).to_bytes(4, "little")) for c in (4, 1, 10, 0)]
    out += [("lzma", b"\x5d\x00\x00" + bytes([d]) + b"\x00" + b"\xff" * 8) for d in (0x80, 0x10, 0x01, 0x40, 0x20)]
    out += [("zip", b"PK\x03\x04" + v + b"\x00\x00" + m) for v in (b"\x14\x00", b"\x0a\x00") for m in (b"\x08\x00", b"\x00\x00")]
    out += [("gzip", b"\x1f\x8b\x08\x08"), ("gzip", b"\x1f\x8b\x08\x00"), ("zstd", b"\x28\xb5\x2f\xfd")]
    out += [("zlib", b"\x78" + bytes([f])) for f in (0xDA, 0x9C, 0x01, 0x5E)]
    return out


_XZ_HDRS = _xz_hdrs()


def _xz_x(b, key):
    """Repeating-key XOR via one big-int op (the sweep runs ~1000 of these)."""
    n = len(b)
    k = (key * (n // len(key) + 1))[:n]
    return (int.from_bytes(b, "big") ^ int.from_bytes(k, "big")).to_bytes(n, "big")


def _xz_keys(b, hints=()):
    """[(kind|None, key)] candidate keys for a byte string that carries no compressor magic of its own."""
    keys, seen = [], set()

    def add(kind, k):
        if k and any(k) and k not in seen:
            seen.add(k)
            keys.append((kind, k))
    for kind, h in _XZ_HDRS:
        if len(b) <= len(h) + 4:
            continue
        ks = bytes(x ^ y for x, y in zip(b, h))
        for p in range(1, min(10, len(h)) + 1):
            if all(ks[i] == ks[i % p] for i in range(p, len(h))):
                add(kind, ks[:p])
    for k in _hint_keys(hints):
        add(None, k.encode())
    return keys


def _xz_zlib_sweep(b):
    """Period-3 (any byte) / period-4 (letters) keys over a zlib 78xx stream: key bytes 0-1 from the header, the rest
    swept; a candidate survives only if its 40-byte prefix inflates without error."""
    out = []
    head = b[:40]
    for f in (0xDA, 0x9C, 0x01, 0x5E):
        k01 = bytes([b[0] ^ 0x78, b[1] ^ f])
        for tail in [bytes([x]) for x in range(256)] + [bytes([x, y]) for x in range(97, 123) for y in range(97, 123)]:
            k = k01 + tail
            try:
                zlib.decompressobj(15).decompress(_xz_x(head, k))
            except zlib.error:
                continue
            out.append(("zlib", k))
    return out


def _xz_texts(d, kind):
    """[(kind, text)] the decrypted bytes inflate to (zip = the archive's joined members)."""
    if kind == "zip" or d[:4] == b"PK\x03\x04":
        r = safe(archive_solve, d)
        return [("zip", r[1])] if r else []
    if _dz_kind(d) == "deflate" and kind is not None:
        return []
    return [(k, s) for k, data in _dz_inflate(d) for s in (_dz_text(data),) if s]


def xorz_reads(t, hints=(), sweep=True):
    """[(name, text, kind, wrapper, key, decrypted)] for every wrapper reading of `t` that has no magic, XORs (key from
    a known header / a hint word) to a compressor stream and inflates to printable ASCII. Never raises."""
    out = []
    try:
        deadline = time.monotonic() + 0.6
        for i, (wrapper, b) in enumerate(_dz_wrappers(t)):
            if len(b) < 14 or _dz_kind(b) != "deflate":
                continue
            keys = _xz_keys(b, hints)
            # the sweep reads only the blob's most specific wrapper (a hex blob also parses as base64)
            if sweep and i == 0 and len(b) <= 4096 and not any(_dz_kind(_xz_x(b, k)) == "zlib" and len(k) <= 2 and _xz_texts(_xz_x(b, k), "zlib")
                                 for _kd, k in keys):
                keys += _xz_zlib_sweep(b)
            for kind, key in keys:
                if time.monotonic() > deadline:
                    break
                d = _xz_x(b, key)
                for k, s in _xz_texts(d, kind):
                    out.append((f"xor{len(key)}[{key.hex()}]({k}-{wrapper})", s, k, wrapper, key, d))
                if out:
                    return out
    except Exception:   # noqa: BLE001
        return out
    return out


def xorz_solve(blob, hints=()):
    """(name, sentence, enc) for a slug-gated XOR-over-compressed reading of the blob (the inflated text may itself be
    XORed / another codec: xorkey_solve, then decompress_solve's inner re-decode), else None."""
    try:
        for name, s, kind, wrapper, key, d in xorz_reads(blob, hints):
            z = None if kind == "zip" else _dz_enc(kind, d)
            enc = (lambda z, key, w: lambda x: _dz_out(_xz_x(z(_u(x)), key), w))(z, key, wrapper) if z else (lambda x: None)
            if SLUG.search(s) and _kbd_score(s) >= _RD_OK:
                return name, s, enc
            xk = xorkey_solve(s, hints)
            if xk:
                return (f"{name}[{xk[0]}]", xk[1],
                        (lambda o, ie: lambda x: (lambda y: y and o(y))(safe(ie, x)))(enc, xk[2]) if z else (lambda x: None))
            rd = _rd_inner(s, 2, time.monotonic() + 0.4)
            if rd:
                return (f"{name}[{rd[0]}]", rd[1],
                        (lambda o, ie: lambda x: (lambda y: y and o(y))(safe(ie, x)))(enc, rd[2]) if z and rd[2] else (lambda x: None))
            if SLUG.search(s):
                return name, s, enc
    except Exception:   # noqa: BLE001
        return None
    return None


def xorz_dec(t):
    r = xorz_solve(t)
    return r[1] if r else None


def xorz_free(p):
    """Speculative Mastery-line decoder: one line = a whole XOR-keyed compressed member (key restarting per line); the
    header-derived keys only (no sweep), the inflated text as-is."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for s in dict.fromkeys(s for _n, s, *_r in xorz_reads(p, sweep=False))][:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES.append(("xor-compressed", lambda s: None, xorz_dec))


# ------------------------------------- text armor wrappers (speculative, coverage atlas target text-armor-wrappers)
# "A familiar wrapper" read literally: a body inside a standard text armor -- data: URI ([mime][;base64]), PEM
# -----BEGIN X----- (RFC 1421 headers), PGP ASCII armor (headers, =CRC24 verified when present; literal / compressed
# OpenPGP packets opened; cleartext-signed text undashed), MIME part / email (each part by its CTE), begin-base64
# (uuencode -m), Intel HEX (:LLAAAATT..CC, checksum) / Motorola S-record (S0-S9, checksum), JSON / XML envelope (each
# string leaf). unarmor(t) -> [(form, bytes, rewrap)]; rewrap(bytes) -> the blob with ITS body swapped (headers, label,
# line width, record size kept verbatim), so a re-encode reproduces the observed wrapper. Body bytes -> printable text,
# else decompress_reads (gzip & co.), else a nested codec (_rd_inner). Never raises.
_ARM_MAX = 400000
_ARM_PEM = re.compile(r"-----BEGIN ([A-Z0-9 ._-]+)-----[ \t]*\r?\n(.*?)\r?\n-----END \1-----", re.S)
_ARM_HDRS = re.compile(r"(?i)(?:mime-version|content-[a-z-]+|from|to|subject|date|message-id|return-path|received|"
                       r"x-[a-z0-9-]+)[ \t]*:")


def _crc24(b):
    crc = 0xB704CE
    for x in b:
        crc ^= x << 16
        for _ in range(8):
            crc <<= 1
            if crc & 0x1000000:
                crc ^= 0x1864CFB
    return crc & 0xFFFFFF


def _arm_b64(body):
    """Strict base64 of a (whitespace-wrapped) body, padding optional -> bytes | None."""
    flat = re.sub(r"\s+", "", body)
    u = flat.rstrip("=")
    if not u or len(u) % 4 == 1 or not re.fullmatch(r"[A-Za-z0-9+/]+", u):
        return None
    try:
        return base64.b64decode(u + "=" * (-len(u) % 4), validate=True)
    except (ValueError, TypeError):
        return None


def _arm_lines(body):
    """(width, newline, padded) of an observed wrapped base64 body (width None = one line)."""
    nl = "\r\n" if "\r\n" in body else "\n"
    ls = [x for x in body.strip().splitlines() if x.strip()]
    return (len(ls[0].strip()) if len(ls) > 1 else None), nl, body.strip().endswith("=") or len(re.sub(r"\s", "", body)) % 4 == 0


def _arm_b64out(b, shape):
    width, nl, pad = shape
    x = base64.b64encode(b).decode()
    x = x if pad else x.rstrip("=")
    return nl.join(x[i:i + width] for i in range(0, len(x), width)) if width else x


def _arm_swap(blob, start, end, new):
    return blob[:start] + new + blob[end:]


def _pgp_len(b, i, new):
    """(length, header_end) of an OpenPGP packet body length at b[i:] (new / old format), None = indeterminate."""
    if new:
        o = b[i]
        if o < 192:
            return o, i + 1
        if o < 224:
            return ((o - 192) << 8) + b[i + 1] + 192, i + 2
        if o == 255:
            return int.from_bytes(b[i + 1:i + 5], "big"), i + 5
        return None
    return None


def _pgp_open(b, depth=3):
    """bytes inside OpenPGP literal (tag 11) / compressed (tag 8: zip / zlib / bzip2) packets, else None."""
    import bz2
    if depth <= 0 or not b or not b[0] & 0x80:
        return None
    ctb = b[0]
    if ctb & 0x40:
        tag, ln = ctb & 0x3F, _pgp_len(b, 1, True)
    else:
        tag, lt = (ctb >> 2) & 0x0F, ctb & 3
        ln = ((int.from_bytes(b[1:1 + (1, 2, 4)[lt]], "big"), 1 + (1, 2, 4)[lt]) if lt < 3 else (len(b) - 1, 1))
    if not ln:
        return None
    n, h = ln
    body = b[h:h + n]
    if len(body) != n:
        return None
    if tag == 11 and len(body) >= 6:
        fl = body[1]
        return body[2 + fl + 4:] if body[0:1] in (b"b", b"t", b"u", b"m", b"l", b"1") and len(body) >= 6 + fl else None
    if tag == 8 and body:
        try:
            d = zlib.decompressobj(-15) if body[0] == 1 else zlib.decompressobj() if body[0] == 2 else None
            data = d.decompress(body[1:], _DZ_MAX) if d else bz2.decompress(body[1:]) if body[0] == 3 else \
                body[1:] if body[0] == 0 else None
        except (zlib.error, OSError, ValueError):
            return None
        return _pgp_open(data, depth - 1) if data else None
    return None


def _pgp_wrap(new, packets):
    """Re-wrap bytes as the observed literal packet (old / new CTB, format, filename, date); compressed packets are
    not rebuilt (None)."""
    b = packets
    ctb = b[0]
    if ctb & 0x40:
        tag, (n, h) = ctb & 0x3F, _pgp_len(b, 1, True)
    else:
        lt = ctb & 3
        tag, n, h = (ctb >> 2) & 0x0F, int.from_bytes(b[1:1 + (1, 2, 4)[lt]], "big") if lt < 3 else len(b) - 1, \
            1 + (1, 2, 4)[lt] if lt < 3 else 1
    if tag != 11:
        return None
    body = b[h:h + n]
    lit = body[:2 + body[1] + 4] + new
    if ctb & 0x40:
        m = len(lit)
        hdr = bytes([m]) if m < 192 else bytes([((m - 192) >> 8) + 192, (m - 192) & 0xFF]) if m < 8384 else \
            b"\xff" + m.to_bytes(4, "big")
    else:
        lt = ctb & 3
        hdr = b"" if lt == 3 else len(lit).to_bytes((1, 2, 4)[lt], "big")
    return bytes([ctb]) + hdr + lit


def _arm_pem(blob):
    out = []
    for m in _ARM_PEM.finditer(blob):
        label, inner = m.group(1), m.group(2)
        a = m.start(2)
        # RFC 1421 / OpenPGP armor headers ("Key: value" lines) end at the first blank line
        hm = re.match(r"((?:[A-Za-z][A-Za-z0-9-]*:[^\r\n]*\r?\n(?:[ \t][^\r\n]*\r?\n)*)+)\r?\n", inner)
        b0 = hm.end() if hm else 0
        if not hm and label.startswith("PGP") and re.match(r"\r?\n", inner):
            b0 = len(re.match(r"\r?\n", inner).group())
        body = inner[b0:]
        crc = None
        cm = re.search(r"\r?\n=([A-Za-z0-9+/]{4})\s*$", body)
        if cm and label.startswith("PGP"):
            crc = base64.b64decode(cm.group(1))
            body = body[:cm.start()]
        raw = _arm_b64(body)
        if raw is None:
            continue
        if crc is not None and int.from_bytes(crc, "big") != _crc24(raw):
            continue   # a corrupted armor: the checksum is the format's own verdict
        shape = _arm_lines(body)
        ba, bz = a + b0, a + b0 + len(body)
        crc_at = (a + b0 + cm.start(), a + b0 + cm.end()) if crc is not None else None

        def rewrap(new, ba=ba, bz=bz, shape=shape, crc_at=crc_at):
            enc = _arm_b64out(new, shape)
            if crc_at:
                tail = blob[crc_at[0]:crc_at[1]]
                nl = re.match(r"\r?\n", tail).group()
                return blob[:ba] + enc + nl + "=" + base64.b64encode(_crc24(new).to_bytes(3, "big")).decode() + \
                    tail[len(nl) + 5:] + blob[crc_at[1]:]
            return blob[:ba] + enc + blob[bz:]
        lit = _pgp_open(raw) if label.startswith("PGP") else None
        if lit is not None:
            out.append(("pgp-literal", lit, (lambda raw, rw: lambda b: (lambda p: p and rw(p))(_pgp_wrap(b, raw)))(raw, rewrap)))
        out.append(("pgp" if label.startswith("PGP") else "pem", raw, rewrap))
    return out


def _arm_clearsig(blob):
    """PGP cleartext signature: Hash: headers, blank line, dash-escaped text, then the signature block."""
    m = re.search(r"-----BEGIN PGP SIGNED MESSAGE-----[ \t]*\r?\n((?:[A-Za-z-]+: [^\r\n]*\r?\n)*)\r?\n", blob)
    sig = blob.find("-----BEGIN PGP SIGNATURE-----", m.end()) if m else -1
    if sig < 0:
        return []
    t0 = m.end()
    txt = blob[t0:sig].rstrip("\r\n")
    nl = "\r\n" if "\r\n" in txt else "\n"
    plain = re.sub(r"(?m)^- ", "", txt).replace("\r\n", "\n")
    return [("pgp-cleartext", _u(plain), lambda b: _arm_swap(
        blob, t0, t0 + len(txt), nl.join(("- " + x if x.startswith("-") else x) for x in _t(b).split("\n"))))]


def _arm_datauri(blob):
    s = blob.strip()
    m = re.fullmatch(r"data:([^,\s]*),(\S*)", s)
    if not m:
        return []
    meta, body = m.groups()
    a = blob.find(",") + 1
    z = a + len(body)
    if meta.lower().endswith(";base64"):
        raw = _arm_b64(body)
        pad = body.endswith("=") or len(body) % 4 == 0
        return [] if raw is None else [("data-uri-base64", raw, lambda b: _arm_swap(blob, a, z, _arm_b64out(b, (None, "", pad))))]
    lit = set(re.sub(r"%[0-9A-Fa-f]{2}", "", body)) | set(string.ascii_letters + string.digits)
    up = not re.search(r"%[0-9A-F]?[a-f]", body)
    raw = urllib.parse.unquote_to_bytes(body)

    def rw(b):
        enc = "".join(chr(x) if chr(x) in lit and x < 128 else (f"%{x:02X}" if up else f"%{x:02x}") for x in b)
        return _arm_swap(blob, a, z, enc)
    return [("data-uri", raw, rw)]


def _arm_beginb64(blob):
    m = re.search(r"(?m)^begin-base64(?:-encoded)? [0-7]{3,4} [^\r\n]*\r?\n(.*?)\r?\n====[ \t]*$", blob, re.S)
    if not m:
        return []
    raw = _arm_b64(m.group(1))
    shape = _arm_lines(m.group(1))
    a, z = m.start(1), m.end(1)
    return [] if raw is None else [("begin-base64", raw, lambda b: _arm_swap(blob, a, z, _arm_b64out(b, shape)))]


def _arm_mime(blob):
    s = blob.lstrip()
    if not _ARM_HDRS.match(s) or not re.search(r"(?im)^content-(?:transfer-encoding|type)[ \t]*:", s):
        return []
    import email
    import email.policy
    msg = email.message_from_string(s, policy=email.policy.compat32)
    out = []
    for part in msg.walk():
        if part.is_multipart():
            continue
        cte = (part.get("Content-Transfer-Encoding") or "7bit").strip().lower()
        src = part.get_payload(decode=False)
        if not isinstance(src, str) or not src.strip():
            continue
        if cte == "base64" and _arm_b64(src) is None:
            continue   # email's own base64 is lenient: a non-base64 body under the header is a decoy
        raw = part.get_payload(decode=True)
        if raw is None:
            continue
        at = blob.find(src.strip())
        body = src.strip()
        if at < 0:
            continue

        def rw(b, at=at, body=body, cte=cte):
            if cte == "base64":
                enc = _arm_b64out(b, _arm_lines(body))
            elif cte == "quoted-printable":
                enc = quopri.encodestring(b).decode("ascii").rstrip("\n")
                enc = enc.replace("\n", "\r\n") if "\r\n" in body else enc
            elif cte in ("x-uuencode", "uuencode", "x-uue"):
                return None
            else:
                enc = b.decode("latin-1")
            return _arm_swap(blob, at, at + len(body), enc)
        out.append((f"mime-{cte}", raw, rw))
    return out


def _arm_ihex(blob):
    ls = [x.strip() for x in blob.strip().splitlines() if x.strip()]
    if not ls or not all(re.fullmatch(r":[0-9A-Fa-f]{10,}", x) for x in ls):
        return []
    base, recs, eof = 0, [], False
    for x in ls:
        r = bytes.fromhex(x[1:])
        if len(r) != r[0] + 5 or sum(r) & 0xFF or eof:
            return []
        typ, addr, data = r[3], int.from_bytes(r[1:3], "big"), r[4:-1]
        if typ == 0:
            recs.append((base + addr, data))
        elif typ == 1:
            eof = True
        elif typ == 2 and len(data) == 2:
            base = int.from_bytes(data, "big") << 4
        elif typ == 4 and len(data) == 2:
            base = int.from_bytes(data, "big") << 16
        elif typ not in (3, 5):
            return []
    if not recs:
        return []
    raw = b"".join(d for _a, d in sorted(recs, key=lambda r: r[0]))
    first = next(x for x in ls if x[7:9] == "00")
    width, start, lower = int(first[1:3], 16), int(first[3:7], 16), any(c in "abcdef" for c in "".join(ls))
    pre = [x for x in ls[:ls.index(first)]]
    post = [x for x in ls[ls.index(first):] if x[7:9] not in ("00",)]
    nl = "\r\n" if "\r\n" in blob else "\n"
    tail = nl if blob.endswith(("\n", "\r\n")) else ""

    def rec(addr, typ, data):
        r = bytes([len(data)]) + (addr & 0xFFFF).to_bytes(2, "big") + bytes([typ]) + data
        x = ":" + (r + bytes([-sum(r) & 0xFF])).hex().upper()
        return x.lower() if lower else x

    def rw(b):
        if start + len(b) > 0x10000:
            return None
        body = [rec(start + i, 0, b[i:i + width]) for i in range(0, len(b), width)]
        return nl.join(pre + body + post) + tail
    return [("intel-hex", raw, rw)]


def _arm_srec(blob):
    ls = [x.strip() for x in blob.strip().splitlines() if x.strip()]
    if not ls or not all(re.fullmatch(r"S[0-9][0-9A-Fa-f]{6,}", x) and len(x) % 2 == 0 for x in ls):
        return []
    recs, typs = [], []
    for x in ls:
        r = bytes.fromhex(x[2:])
        if len(r) != r[0] + 1 or (sum(r[:-1]) + r[-1]) & 0xFF != 0xFF:
            return []
        t = int(x[1])
        if t == 4:
            return []
        al = {0: 2, 1: 2, 2: 3, 3: 4, 5: 2, 6: 3, 7: 4, 8: 3, 9: 2}[t]
        if r[0] < al + 1:
            return []
        if t in (1, 2, 3):
            recs.append((int.from_bytes(r[1:1 + al], "big"), r[1 + al:-1]))
        typs.append(t)
    if not recs:
        return []
    raw = b"".join(d for _a, d in sorted(recs, key=lambda r: r[0]))
    di = next(i for i, x in enumerate(ls) if x[1] in "123")
    dt, first = int(ls[di][1]), bytes.fromhex(ls[di][2:])
    al = {1: 2, 2: 3, 3: 4}[dt]
    width, start = first[0] - al - 1, int.from_bytes(first[1:1 + al], "big")
    pre = ls[:di]
    post = [x for x in ls[di:] if x[1] not in "123"]
    lower = any(c in "abcdef" for c in "".join(ls))
    nl = "\r\n" if "\r\n" in blob else "\n"
    tail = nl if blob.endswith(("\n", "\r\n")) else ""

    def rec(t, addr, data, al):
        r = bytes([al + len(data) + 1]) + addr.to_bytes(al, "big") + data
        x = f"S{t}" + (r + bytes([~sum(r) & 0xFF])).hex().upper()
        return x.lower().replace("s", "S", 1) if lower else x

    def rw(b):
        body = [rec(dt, start + i, b[i:i + width], al) for i in range(0, len(b), width)]
        n = len(body)
        po = [rec(5, n, b"", 2) if x[1] == "5" else rec(6, n, b"", 3) if x[1] == "6" else x for x in post]
        return nl.join(pre + body + po) + tail
    return [("srec", raw, rw)]


def _arm_envelope(blob):
    """JSON / XML envelope: every string leaf (value / element text / attribute) as a body."""
    s = blob.strip()
    leaves = []
    if s[:1] in "{[":
        try:
            obj = json.loads(s)
        except ValueError:
            return []
        stack = [obj]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                stack.extend(reversed(list(o.values())))
            elif isinstance(o, list):
                stack.extend(reversed(o))
            elif isinstance(o, str):
                leaves.append(o)
        form = "json"
    elif s[:1] == "<" and "<!ENTITY" not in s.upper():
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(s)
        except ET.ParseError:
            return []
        for el in root.iter():
            leaves += list(el.attrib.values()) + ([el.text] if el.text else [])
        form = "xml"
    else:
        return []
    out = []
    for v in leaves:
        v = v.strip()
        at = blob.find(v)
        if len(v) < 8 or at < 0:
            continue
        out.append((f"{form}-envelope", _u(v), (lambda at, n: lambda b: _arm_swap(blob, at, at + n, _t(b)))(at, len(v))))
    return out


_ARM_PARSERS = (_arm_datauri, _arm_clearsig, _arm_pem, _arm_beginb64, _arm_mime, _arm_ihex, _arm_srec, _arm_envelope)


def unarmor(t):
    """[(form, body bytes, rewrap)] for every text armor `t` strictly parses as; rewrap(bytes) -> the same armor text
    around new body bytes (None = can't rebuild). Never raises."""
    try:
        blob = t.decode("utf-8") if isinstance(t, (bytes, bytearray)) else t
        if not isinstance(blob, str) or not blob.strip() or len(blob) > _ARM_MAX:
            return []
        out = []
        for parse in _ARM_PARSERS:
            try:
                out += [(f, b, rw) for f, b, rw in parse(blob) if b]
            except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
                continue
        return out
    except Exception:   # noqa: BLE001
        return []


def armor_reads(t):
    """[(name, text, raw_bytes, rewrap, kind|None)]: the printable body of every armor reading, else its inflated
    text (kind = the compressor). Never raises."""
    out = []
    try:
        for form, b, rw in unarmor(t):
            s = _dz_text(b)
            if s is not None and s.strip():
                out.append((form, s, b, rw, None))
            for name, x, kind, _w, raw in decompress_reads(b):
                if raw == b:
                    out.append((f"{form}[{kind}]", x, b, rw, kind))
    except Exception:   # noqa: BLE001
        return []
    return out


def armor_solve(blob, hints=()):
    """(name, sentence, enc) for the first slug-gated armor reading (a body that is another codec re-decoded), else
    None. enc(sentence) rebuilds the observed wrapper (None when the wrapper can't be rebuilt)."""
    try:
        deadline = time.monotonic() + 0.5
        reads = armor_reads(blob)
        for name, s, b, rw, kind in reads:
            z = _dz_enc(kind, b) if kind else (lambda x: x)
            enc = (lambda rw, z: lambda x: (lambda y: rw(y))(z(_u(x))))(rw, z)
            if SLUG.search(s) and _kbd_score(s) >= _RD_OK:
                return name, s, enc
        for name, s, b, rw, kind in reads:
            z = _dz_enc(kind, b) if kind else (lambda x: x)
            rd = _rd_inner(s, 2, deadline)
            if rd:
                ie = rd[2]
                return (f"{name}[{rd[0]}]", rd[1],
                        (lambda rw, z, ie: lambda x: (lambda y: y and rw(z(_u(y))))(safe(ie, x)))(rw, z, ie)
                        if ie else (lambda x: None))
        for name, s, b, rw, kind in reads:
            if SLUG.search(s):
                z = _dz_enc(kind, b) if kind else (lambda x: x)
                return name, s, (lambda rw, z: lambda x: rw(z(_u(x))))(rw, z)
    except Exception:   # noqa: BLE001
        return None
    return None


def armor_dec(t):
    r = armor_solve(t)
    return r[1] if r else None


def armor_free(p):
    """Speculative Mastery-line decoder: the unwrapped (maybe inflated) body of a one-line armor (data: URI, JSON)."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        outs = [s for _n, s, *_r in armor_reads(p)]
        outs = [y for x in outs for y in (_rd_free(x) + [x])]
        return [lead + s for s in dict.fromkeys(outs)][:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES.append(("text-armor", lambda s: None, armor_dec))


# ------------------------------------- archive containers (speculative, coverage atlas target archive-container-in-base64)
# "A wrapper / package / bundle" read literally: an archive inside base64 / hex / raw bytes -- zip (stored / deflated /
# bzip2 / lzma; ZipCrypto or AES tried with b"infected"), tar (plain or gzip / bzip2 / xz: 'ustar' at 257), 7z (copy /
# LZMA / LZMA2 / deflate / bzip2 coders, encoded header; no AES), cpio (newc / crc 070701-2, odc 070707, binary 0x71c7)
# and ar (!<arch>, GNU / BSD long names). Every file member is read in archive order, each decoded with the pipeline
# (printable text, else decompress_reads, else a nested codec) and joined. archive_members(b) -> [(form, [(name,
# bytes)])]. Never raises.
_ARC_MAX = 4 << 20
_ARC_PW = (b"infected",)


def _arc_zip(b):
    import io
    import zipfile
    out = []
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        for zi in z.infolist()[:64]:
            if zi.is_dir() or zi.file_size > _ARC_MAX or zi.filename.startswith("__MACOSX/"):
                continue
            if not zi.flag_bits & 1:
                out.append((zi.filename, z.read(zi)))
                continue
            got = None
            for pw in _ARC_PW:
                try:
                    got = z.read(zi, pwd=pw)
                    break
                except Exception:   # noqa: BLE001 -- AES (compress_type 99) or a wrong password
                    try:
                        import pyzipper
                        with pyzipper.AESZipFile(io.BytesIO(b)) as az:
                            got = az.read(zi.filename, pwd=pw)
                        break
                    except Exception:   # noqa: BLE001
                        continue
            if got is None:
                raise ValueError("encrypted member")
            out.append((zi.filename, got))
    return [("zip", out)] if out else []


def _arc_tar(b):
    import io
    import tarfile
    out = []
    with tarfile.open(fileobj=io.BytesIO(b), mode="r:") as tf:
        for m in tf.getmembers()[:64]:
            if m.isfile() and m.size <= _ARC_MAX:
                out.append((m.name, tf.extractfile(m).read()))
    return [("tar", out)] if out else []


def _arc_ar(b):
    if not b.startswith(b"!<arch>\n"):
        return []
    i, out, longnames = 8, [], b""
    while i + 60 <= len(b):
        h = b[i:i + 60]
        if h[58:60] != b"`\n":
            raise ValueError("bad ar header")
        name, size = h[:16].decode("ascii").rstrip(), int(h[48:58].decode("ascii").strip() or "x")
        data = b[i + 60:i + 60 + size]
        if len(data) != size:
            raise ValueError("truncated ar member")
        i += 60 + size + (size & 1)
        if name in ("/", "/SYM64/", "__.SYMDEF", "__.SYMDEF SORTED"):
            continue
        if name == "//":
            longnames = data
            continue
        if name.startswith("#1/"):    # BSD: the name leads the data
            n = int(name[3:])
            name, data = data[:n].rstrip(b"\x00").decode("latin-1"), data[n:]
        elif re.fullmatch(r"/\d+", name):
            off = int(name[1:])
            name = longnames[off:].split(b"\n")[0].decode("latin-1").rstrip("/")
        else:
            name = name.rstrip("/")
        out.append((name, data))
    if i != len(b) and b[i:].strip(b"\n"):
        raise ValueError("trailing ar bytes")
    return [("ar", out)] if out else []


def _arc_cpio(b):
    import struct
    i, out, form = 0, [], None
    while i < len(b):
        m = b[i:i + 6]
        if m in (b"070701", b"070702"):
            form = "cpio-newc"
            f = [int(b[i + 6 + 8 * k:i + 14 + 8 * k], 16) for k in range(13)]
            mode, fsize, nsize = f[1], f[6], f[11]
            hl, pad = 110, 4
        elif m == b"070707":
            form = "cpio-odc"
            mode, nsize, fsize = int(b[i + 18:i + 24], 8), int(b[i + 59:i + 65], 8), int(b[i + 65:i + 76], 8)
            hl, pad = 76, 1
        elif b[i:i + 2] in (b"\xc7\x71", b"\x71\xc7"):
            form = "cpio-bin"
            e = "<" if b[i:i + 2] == b"\xc7\x71" else ">"
            v = struct.unpack(e + "13H", b[i:i + 26])
            mode, nsize, fsize = v[2], v[10], (v[11] << 16) | v[12]
            hl, pad = 26, 2
        else:
            raise ValueError("bad cpio header")
        name = b[i + hl:i + hl + nsize].rstrip(b"\x00").decode("latin-1")
        i += hl + nsize
        i += -i % pad
        data = b[i:i + fsize]
        if len(data) != fsize:
            raise ValueError("truncated cpio member")
        i += fsize
        i += -i % pad
        if name == "TRAILER!!!":
            break
        if mode & 0o170000 == 0o100000 and fsize <= _ARC_MAX:
            out.append((name, data))
    return [(form, out)] if out else []


def _7z_num(b, i):
    first, mask, v = b[i], 0x80, 0
    for k in range(8):
        if not first & mask:
            return v | ((first & (mask - 1)) << (8 * k)), i + 1 + k
        v |= b[i + 1 + k] << (8 * k)
        mask >>= 1
    return v, i + 9


def _7z_bits(b, i, n):
    bits = [bool(b[i + k // 8] & (0x80 >> (k % 8))) for k in range(n)]
    return bits, i + (n + 7) // 8


def _7z_digests(b, i, n):
    if b[i]:
        defined, i = [True] * n, i + 1
    else:
        defined, i = _7z_bits(b, i + 1, n)
    return i + 4 * sum(defined)


def _7z_streams(b, i):
    """StreamsInfo at b[i] -> (pack_pos, pack_sizes, folders [(coders, unpack_sizes)], substream counts, sizes), i."""
    pack_pos, packs, folders, nsub, subsizes = 0, [], [], None, None
    while True:
        t = b[i]
        i += 1
        if t == 0:
            break
        if t == 0x06:
            pack_pos, i = _7z_num(b, i)
            n, i = _7z_num(b, i)
            while b[i] != 0:
                if b[i] == 0x09:
                    i += 1
                    for _ in range(n):
                        x, i = _7z_num(b, i)
                        packs.append(x)
                elif b[i] == 0x0A:
                    i = _7z_digests(b, i + 1, n)
                else:
                    raise ValueError("7z packinfo")
            i += 1
        elif t == 0x07:
            if b[i] != 0x0B:
                raise ValueError("7z folder")
            nf, i = _7z_num(b, i + 1)
            if b[i]:
                raise ValueError("7z external")
            i += 1
            for _ in range(nf):
                nc, i = _7z_num(b, i)
                coders, outs = [], 0
                for _ in range(nc):
                    flag = b[i]
                    cid, i = b[i + 1:i + 1 + (flag & 0xF)], i + 1 + (flag & 0xF)
                    nin = nout = 1
                    if flag & 0x10:
                        nin, i = _7z_num(b, i)
                        nout, i = _7z_num(b, i)
                    props = b""
                    if flag & 0x20:
                        ps, i = _7z_num(b, i)
                        props, i = b[i:i + ps], i + ps
                    coders.append((cid, props, nin, nout))
                    outs += nout
                if nc != 1 or outs != 1:
                    raise ValueError("7z coder chain")   # one coder per folder (7z's default for text)
                folders.append([coders, []])
            if b[i] != 0x0C:
                raise ValueError("7z unpack sizes")
            i += 1
            for f in folders:
                x, i = _7z_num(b, i)
                f[1].append(x)
            while b[i] != 0:
                if b[i] == 0x0A:
                    i = _7z_digests(b, i + 1, len(folders))
                else:
                    raise ValueError("7z unpackinfo")
            i += 1
        elif t == 0x08:
            nsub = [1] * len(folders)
            while b[i] != 0:
                if b[i] == 0x0D:
                    i += 1
                    for k in range(len(folders)):
                        nsub[k], i = _7z_num(b, i)
                elif b[i] == 0x09:
                    i += 1
                    subsizes = []
                    for k, f in enumerate(folders):
                        if not nsub[k]:
                            continue
                        left = f[1][0]
                        for _ in range(nsub[k] - 1):
                            x, i = _7z_num(b, i)
                            subsizes.append(x)
                            left -= x
                        subsizes.append(left)
                elif b[i] == 0x0A:
                    unknown = sum(n for n in nsub if n != 1) + sum(1 for n in nsub if n == 1)
                    i = _7z_digests(b, i + 1, unknown)
                else:
                    raise ValueError("7z substreams")
            i += 1
        else:
            raise ValueError("7z streams")
    if nsub is None:
        nsub = [1] * len(folders)
    if subsizes is None:
        subsizes = [f[1][0] for k, f in enumerate(folders) if nsub[k]]
    return (pack_pos, packs, folders, nsub, subsizes), i


def _7z_unpack(b, si):
    """[folder bytes] of a parsed StreamsInfo (pack streams start at 32 + pack_pos)."""
    import bz2
    import lzma
    pack_pos, packs, folders, _n, _s = si
    at, out = 32 + pack_pos, []
    for (coders, sizes), psize in zip(folders, packs):
        cid, props, _ni, _no = coders[0]
        raw, at = b[at:at + psize], at + psize
        if len(raw) != psize:
            raise ValueError("7z truncated pack")
        if cid == b"\x00":
            data = raw
        elif cid in (b"\x03\x01\x01", b"\x21"):
            fid = lzma.FILTER_LZMA1 if cid != b"\x21" else lzma.FILTER_LZMA2
            flt = lzma._decode_filter_properties(fid, props)
            data = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[flt]).decompress(raw, sizes[0])
        elif cid == b"\x04\x01\x08":
            data = zlib.decompressobj(-15).decompress(raw, sizes[0])
        elif cid == b"\x04\x02\x02":
            data = bz2.decompress(raw)
        else:
            raise ValueError("7z coder unsupported")   # AES, BCJ, PPMd ...
        if len(data) < sizes[0]:
            raise ValueError("7z short folder")
        out.append(data[:sizes[0]])
    return out


def _arc_7z(b):
    import struct
    if not b.startswith(b"7z\xbc\xaf\x27\x1c") or len(b) < 32:
        return []
    off, size = struct.unpack("<QQ", b[12:28])
    if zlib.crc32(b[12:32]) != struct.unpack("<I", b[8:12])[0]:
        raise ValueError("7z start header crc")
    hdr = b[32 + off:32 + off + size]
    if len(hdr) != size or zlib.crc32(hdr) != struct.unpack("<I", b[28:32])[0]:
        raise ValueError("7z next header crc")
    for _ in range(4):
        if hdr[:1] != b"\x17":
            break
        si, _i = _7z_streams(hdr, 1)
        hdr = _7z_unpack(b, si)[0]
    if hdr[:1] != b"\x01":
        raise ValueError("7z header")
    i, si, names, empty = 1, None, [], []
    while hdr[i] != 0:
        t = hdr[i]
        i += 1
        if t == 0x04:
            si, i = _7z_streams(hdr, i)
        elif t == 0x05:
            nfiles, i = _7z_num(hdr, i)
            empty = [False] * nfiles
            while True:
                pt, i = _7z_num(hdr, i)
                if pt == 0:
                    break
                ps, i = _7z_num(hdr, i)
                body, i = hdr[i:i + ps], i + ps
                if pt == 0x0E:
                    empty = _7z_bits(body, 0, nfiles)[0]
                elif pt == 0x11 and body[:1] == b"\x00":
                    names = body[1:].decode("utf-16-le").split("\x00")[:nfiles]
        else:
            raise ValueError("7z header property")
    if si is None:
        return []
    blobs = _7z_unpack(b, si)
    streams = []
    sizes = iter(si[4])
    for k, data in enumerate(blobs):
        at = 0
        for _ in range(si[3][k]):
            n = next(sizes)
            streams.append(data[at:at + n])
            at += n
    out, it = [], iter(streams)
    for k, e in enumerate(empty):
        if not e:
            out.append((names[k] if k < len(names) else str(k), next(it)))
    return [("7z", out)] if out else []


def _arc_kind(b):
    if b.startswith(b"PK\x03\x04") or b.startswith(b"PK\x05\x06"):
        return _arc_zip
    if b.startswith(b"7z\xbc\xaf\x27\x1c"):
        return _arc_7z
    if b.startswith(b"!<arch>\n"):
        return _arc_ar
    if b[:6] in (b"070701", b"070702", b"070707") or b[:2] in (b"\xc7\x71", b"\x71\xc7"):
        return _arc_cpio
    if b[257:262] == b"ustar":
        return _arc_tar
    return None


def archive_members(t):
    """[(form, [(name, bytes)])] for every archive `t` (raw bytes, or base64 / hex / ... text) strictly opens as --
    directly or after one compressor (tar.gz / tar.xz / tar.bz2). A corrupt / encrypted-unknown archive yields
    nothing. Never raises."""
    out = []
    try:
        for wrapper, b in _dz_wrappers(t):
            tries = [("", b)]
            if not _arc_kind(b):
                tries += [(f"{k}+", x) for k, x in _dz_inflate(b) if x[257:262] == b"ustar"]
            for pre, x in tries:
                f = _arc_kind(x)
                if not f:
                    continue
                try:
                    out += [(f"{pre}{form}-{wrapper}", ms) for form, ms in f(x)]
                except Exception:   # noqa: BLE001 -- a decoy archive reads as nothing
                    continue
    except Exception:   # noqa: BLE001
        return []
    return out


def _arc_member_text(b, deadline):
    """Candidate texts of one member: printable as is, else inflated, then its nested-codec re-decodes."""
    s = _dz_text(b)
    outs = [s] if s is not None else []
    outs += [x for _n, x, *_r in decompress_reads(b)]
    if time.monotonic() < deadline:
        outs = [y for x in outs for y in (_rd_free(x) + [x])]
    return list(dict.fromkeys(outs))


def archive_solve(t):
    """(name, sentence) for the first archive reading whose members, decoded and joined in archive order (else name
    order), hold the slug in English; else None."""
    try:
        deadline = time.monotonic() + 0.6
        for form, ms in archive_members(t):
            raw = [m for _n, m in ms]
            texts = [_dz_text(m) for m in raw]
            if all(x is not None for x in texts):
                for joined in ("".join(texts), "".join(x.rstrip("\r\n") for x in texts)):
                    if SLUG.search(joined) and _kbd_score(joined) >= _RD_OK:
                        return form, joined
                    rd = _rd_inner(joined, 2, deadline)
                    if rd:
                        return f"{form}[{rd[0]}]", rd[1]
            for order in (ms, sorted(ms, key=lambda m: m[0])):
                best = []
                for _n, m in order:
                    c = _arc_member_text(m, deadline)
                    if not c:
                        best = None
                        break
                    best.append(max(c, key=_kbd_score))
                if not best:
                    continue
                for joined in ("".join(best), "".join(x.rstrip("\r\n") for x in best)):
                    if SLUG.search(joined) and _kbd_score(joined) >= _RD_OK:
                        return f"{form}[members]", joined
    except Exception:   # noqa: BLE001
        return None
    return None


def archive_dec(t):
    r = archive_solve(t)
    return r[1] if r else None


def archive_free(p):
    """Speculative Mastery-line decoder: the joined member text of a one-line base64 / hex archive."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        outs = []
        for _f, ms in archive_members(p.strip()):
            texts = [_dz_text(m) for _n, m in ms]
            if all(x is not None for x in texts):
                j = "".join(x.rstrip("\r\n") for x in texts)
                outs += _rd_free(j) + [j]
        return [lead + s for s in dict.fromkeys(outs)][:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES.append(("archive-container", lambda s: None, archive_dec))


# ------------------------------------ OpenSSL enc envelope (speculative, coverage atlas target openssl-salted-envelope)
# `openssl enc -e [-a] -pass pass:<pw>`: b"Salted__" + 8-byte salt + ciphertext (base64 'U2FsdGVkX1...', hex or raw).
# key || iv = EVP_BytesToKey(md5 = OpenSSL < 1.1 default, sha256 = 1.1+ default, sha1) or PBKDF2-HMAC-SHA256 10000
# iterations (-pbkdf2 default); both streams are prefix-stable, so one 48-byte derivation serves every cipher. Ciphers:
# aes-128/192/256-cbc / -ecb / -ctr, des-ede3-cbc, bf-cbc, rc4, chacha20. Passphrases: the title / prompt words (as
# written, lower, Title, UPPER, run together) + password / infected / huntress puns. Gate: a CBC / ECB key must leave
# valid PKCS#7 padding, then the plaintext (or its decompress_reads inflation, or a nested codec) must read as the
# slug sentence (Single) / English (Mastery fragment). openssl_solve(t, hints) -> (name, plain, enc). Never raises.
_OS_MAGIC = b"Salted__"
_OS_PW = ("password", "infected", "huntress", "Huntress", "HUNTRESS", "salted", "Salted", "salt", "openssl", "secret",
          "warmup", "warmups")
_OS_KDF = ("pbkdf2-sha256", "md5", "sha256", "sha1")
# name -> (module, key len, iv len, mode); iv len 0 = stream cipher keyed by the key alone
_OS_CIPHERS = (("aes-256-cbc", "AES", 32, 16, "cbc"), ("aes-128-cbc", "AES", 16, 16, "cbc"),
               ("aes-192-cbc", "AES", 24, 16, "cbc"), ("aes-256-ctr", "AES", 32, 16, "ctr"),
               ("aes-128-ctr", "AES", 16, 16, "ctr"), ("aes-192-ctr", "AES", 24, 16, "ctr"),
               ("aes-256-ecb", "AES", 32, 0, "ecb"), ("aes-128-ecb", "AES", 16, 0, "ecb"),
               ("des-ede3-cbc", "DES3", 24, 8, "cbc"), ("bf-cbc", "Blowfish", 16, 8, "cbc"),
               ("rc4", "ARC4", 16, 0, "stream"), ("chacha20", "ChaCha20", 32, 16, "chacha"))


def _os_kdf(pw, salt, kdf, n=48):
    import hashlib
    if kdf.startswith("pbkdf2"):
        return hashlib.pbkdf2_hmac(kdf.split("-")[1], pw, salt, 10000, n)
    out, d = b"", b""
    while len(out) < n:
        d = hashlib.new(kdf, d + pw + salt).digest()
        out += d
    return out[:n]


def _os_cipher(spec, km):
    """A fresh pycryptodome cipher object for `spec` keyed from the derived stream `km` (None: library missing)."""
    _n, mod, kl, il, mode = spec
    try:
        from Crypto.Cipher import AES, ARC4, DES3, Blowfish, ChaCha20
    except Exception:   # noqa: BLE001 -- no pycryptodome: no OpenSSL envelope reads
        return None
    key, iv = km[:kl], km[kl:kl + il]
    if mode == "stream":
        return ARC4.new(key)
    if mode == "chacha":   # openssl chacha20 iv = 4-byte little-endian block counter || 12-byte nonce
        c = ChaCha20.new(key=key, nonce=iv[4:])
        c.seek(int.from_bytes(iv[:4], "little") * 64)
        return c
    m = {"AES": AES, "DES3": DES3, "Blowfish": Blowfish}[mod]
    if mode == "ctr":
        return m.new(key, m.MODE_CTR, nonce=b"", initial_value=iv)
    if mode == "ecb":
        return m.new(key, m.MODE_ECB)
    return m.new(key, m.MODE_CBC, iv=iv)


def _os_unpad(spec, km, ct):
    """Plaintext bytes of `ct`, or None when a block mode's PKCS#7 padding is invalid (checked on the last block first)."""
    mode = spec[4]
    if mode in ("cbc", "ecb"):
        bs = 8 if spec[1] in ("DES3", "Blowfish") else 16
        if not ct or len(ct) % bs:
            return None
        if mode == "cbc":   # the last block alone: CBC chains on the previous ciphertext block
            prev = ct[-2 * bs:-bs] if len(ct) > bs else km[spec[2]:spec[2] + bs]
            last = bytes(a ^ b for a, b in zip(_os_cipher((None, spec[1], spec[2], 0, "ecb"), km).decrypt(ct[-bs:]),
                                               prev))
        else:
            last = _os_cipher(spec, km).decrypt(ct[-bs:])
        p = last[-1]
        if not 1 <= p <= bs or last[-p:] != bytes([p]) * p:
            return None
        pt = _os_cipher(spec, km).decrypt(ct)
        return pt[:-p]
    return _os_cipher(spec, km).decrypt(ct)


def _os_passwords(hints):
    out = []
    for h in hints or ():
        h = unicodedata.normalize("NFKD", str(h)).encode("ascii", "ignore").decode().strip()
        words = re.findall(r"[A-Za-z0-9]{2,}", h)
        for w in words + ["".join(words), "".join(x.capitalize() for x in words), h] if words else ():
            for v in (w, w.lower(), w.capitalize(), w.upper()):
                if v and v not in out:
                    out.append(v)
    return out[:48] + [p for p in _OS_PW if p not in out]


def openssl_envelopes(t):
    """[(wrapper, salt, ciphertext)] for every wrapper reading of `t` that starts with the OpenSSL 'Salted__' magic."""
    try:
        return [(w, b[8:16], b[16:]) for w, b in _dz_wrappers(t) if b[:8] == _OS_MAGIC and len(b) > 16]
    except Exception:   # noqa: BLE001
        return []


def _os_texts(pt, deadline, fragment):
    """[(tag, text, kind)] readings of decrypted bytes: printable as is, inflated, or a nested codec; crib-gated."""
    out = []
    s = _dz_text(pt)
    if s is not None:
        if (SLUG.search(s) or fragment) and _kbd_score(s) >= _RD_OK:
            return [("", s, None)]
        rd = _rd_inner(s, 2, deadline) if time.monotonic() < deadline else None
        if rd:
            return [(f"[{rd[0]}]", rd[1], None)]
        if SLUG.search(s):
            out.append(("", s, None))
    if _dz_kind(pt) == "deflate":   # no compressor magic: random bytes of a wrong key, never trial-inflated
        return out
    for _n, x, kind, _w, _raw in decompress_reads(pt):
        if (SLUG.search(x) or fragment) and _kbd_score(x) >= _RD_OK:
            return [(f"+{kind}", x, kind)] + out
    return out


def openssl_reads(t, hints=(), fragment=False, budget=0.5):
    """[(name, text, enc)] for the first passphrase x KDF x cipher that opens an OpenSSL 'Salted__' envelope of `t`;
    enc re-encrypts with the observed salt / passphrase / KDF / cipher / wrapper (None = nested codec). Never raises."""
    try:
        envs = openssl_envelopes(t)
        if not envs:
            return []
        deadline = time.monotonic() + budget
        flat = t.strip() if isinstance(t, str) else ""
        wrap = next((len(x) for x in flat.splitlines()[:1] if "\n" in flat), 0)   # openssl -a: 64-column lines
        for pw in _os_passwords(hints):
            for wrapper, salt, ct in envs:
                for kdf in _OS_KDF:
                    if time.monotonic() > deadline:
                        return []
                    km = _os_kdf(pw.encode(), salt, kdf)
                    for spec in _OS_CIPHERS:
                        try:
                            pt = _os_unpad(spec, km, ct)
                        except Exception:   # noqa: BLE001
                            pt = None
                        if pt is None:
                            continue
                        for tag, text, kind in _os_texts(pt, deadline, fragment):
                            name = f"openssl-{spec[0]}-{kdf}:{pw}-{wrapper}{tag}"
                            enc = None if tag.startswith("[") else (
                                lambda spec, km, salt, wrapper, z: lambda x: _os_wrap(_dz_out(
                                    _OS_MAGIC + salt + _os_encrypt(spec, km, z(_u(x)) if z else _u(x)), wrapper), wrap)
                            )(spec, km, salt, wrapper, _dz_enc(kind, pt) if kind else None)
                            return [(name, text, enc)]
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []
    return []


def _os_encrypt(spec, km, b):
    if spec[4] in ("cbc", "ecb"):
        bs = 8 if spec[1] in ("DES3", "Blowfish") else 16
        b += bytes([bs - len(b) % bs]) * (bs - len(b) % bs)
    return _os_cipher(spec, km).encrypt(b)


def _os_wrap(x, n):
    return "\n".join(x[i:i + n] for i in range(0, len(x), n)) if n else x


def openssl_solve(t, hints=()):
    r = openssl_reads(t, hints)
    return r[0] if r and SLUG.search(r[0][1]) else None


def openssl_dec(t, hints=()):
    r = openssl_solve(t, hints)
    return r[1] if r else None


def openssl_free(p):
    """Speculative Mastery-line decoder: one line = one base64 / hex OpenSSL envelope under a default passphrase."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for _n, s, _e in openssl_reads(p.strip(), fragment=True, budget=0.25)][:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES.append(("openssl-salted", lambda s: None, openssl_dec))


# ------------------------------------------------------------ LZ-String (pieroxy lz-string 1.5, the JS web compressor)
# compressToBase64 (A-Za-z0-9+/ + '=' pad), compressToEncodedURIComponent (A-Za-z0-9+-, no pad; '$' = 64 never
# emitted), compressToUTF16 (15-bit units + 32: dense U+0020..U+801F CJK-range chars + a trailing ' ') and
# compressToUint8Array (16-bit units big-endian, as hex). No magic: the gate is the stream itself -- an LZW bitstream
# that must hit its end marker (code 2) with every later bit zero, inside the input, and read as text.
_LZ_B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
_LZ_URI = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-$"
_LZ_MAX = 1 << 16


def _lz_compress(s, bits, out):
    """Port of lz-string _compress over UTF-16 code units -> [ints of `bits` width] (fed to `out`)."""
    b = s.encode("utf-16-be", "surrogatepass")
    units = [chr(int.from_bytes(b[i:i + 2], "big")) for i in range(0, len(b), 2)]
    dic, create, w = {}, set(), ""
    st = {"enl": 2, "size": 3, "nb": 2, "val": 0, "pos": 0}
    data = []

    def put(bit):
        st["val"] = (st["val"] << 1) | bit
        if st["pos"] == bits - 1:
            st["pos"] = 0
            data.append(st["val"])
            st["val"] = 0
        else:
            st["pos"] += 1

    def emit(v, n):
        for _ in range(n):
            put(v & 1)
            v >>= 1

    def grow():
        st["enl"] -= 1
        if st["enl"] == 0:
            st["enl"] = 1 << st["nb"]
            st["nb"] += 1

    def flush_w():
        if w in create:
            o = ord(w[0])
            if o < 256:
                emit(0, st["nb"])
                emit(o, 8)
            else:
                emit(1, st["nb"])
                emit(o, 16)
            grow()
            create.discard(w)
        else:
            emit(dic[w], st["nb"])
        grow()

    for c in units:
        if c not in dic:
            dic[c] = st["size"]
            st["size"] += 1
            create.add(c)
        if w + c in dic:
            w = w + c
        else:
            flush_w()
            dic[w + c] = st["size"]
            st["size"] += 1
            w = c
    if w:
        flush_w()
    emit(2, st["nb"])
    while True:
        st["val"] <<= 1
        if st["pos"] == bits - 1:
            data.append(st["val"])
            break
        st["pos"] += 1
    return out(data)


def lzstring_enc(s, form="base64"):
    """lz-string compressTo<form>: base64 / uri / utf16 / hex (compressToUint8Array as hex)."""
    if form == "base64":
        r = _lz_compress(s, 6, lambda d: "".join(_LZ_B64[v] for v in d))
        return r + "=" * ((4 - len(r) % 4) % 4)
    if form == "uri":
        return _lz_compress(s, 6, lambda d: "".join(_LZ_URI[v] for v in d))
    if form == "utf16":
        return _lz_compress(s, 15, lambda d: "".join(chr(v + 32) for v in d)) + " "
    if form == "hex":
        return _lz_compress(s, 16, lambda d: b"".join(v.to_bytes(2, "big") for v in d).hex())
    raise ValueError(form)


def _lz_decompress(vals, bits):
    """lz-string _decompress over a list of `bits`-wide ints -> str, else None (overrun, bad code, junk after end)."""
    n = len(vals)
    if not n:
        return None
    reset = 1 << (bits - 1)
    st = {"val": vals[0], "pos": reset, "idx": 1}

    def read(k):
        r = 0
        for i in range(k):
            if st["idx"] > n:
                raise ValueError("overrun")
            if st["val"] & st["pos"]:
                r |= 1 << i
            st["pos"] >>= 1
            if st["pos"] == 0:
                st["pos"] = reset
                st["val"] = vals[st["idx"]] if st["idx"] < n else 0
                st["idx"] += 1
        return r

    def tail_zero():
        return st["idx"] <= n and not (st["val"] & ((st["pos"] << 1) - 1)) and not any(vals[st["idx"]:])

    try:
        dic = ["", "", ""]
        nb, enl = 3, 4
        k = read(2)
        if k == 2:
            return "" if tail_zero() else None
        if k == 3:
            return None
        c = chr(read(8 if k == 0 else 16))
        dic.append(c)
        w, out, total = c, [c], 1
        while True:
            k = read(nb)
            if k == 2:
                return "".join(out) if tail_zero() else None
            if k in (0, 1):
                dic.append(chr(read(8 if k == 0 else 16)))
                k = len(dic) - 1
                enl -= 1
                if enl == 0:
                    enl = 1 << nb
                    nb += 1
            if k < len(dic) and k >= 3:
                e = dic[k]
            elif k == len(dic):
                e = w + w[0]
            else:
                return None
            out.append(e)
            total += len(e)
            if total > _LZ_MAX:
                return None
            dic.append(w + e[0])
            enl -= 1
            w = e
            if enl == 0:
                enl = 1 << nb
                nb += 1
    except (ValueError, IndexError):
        return None


def lzstring_reads(t):
    """Every (form, text) lz-string reading of one blob/line: base64 / uri / utf16 / hex, text-gated."""
    out = []
    try:
        if not isinstance(t, str):
            return out
        x = t.strip("\r\n")
        cands = []
        s = x.strip()
        if 4 <= len(s) and re.fullmatch(r"[A-Za-z0-9+/]+={0,3}", s):
            cands.append(("base64", [_LZ_B64.index(c) for c in s.rstrip("=")], 6))
        u = s.replace(" ", "+")
        if 4 <= len(u) and re.fullmatch(r"[A-Za-z0-9+\-$]+", u):
            cands.append(("uri", [_LZ_URI.index(c) for c in u], 6))
        v = x[:-1] if x.endswith(" ") else x
        if len(v) >= 2 and all(0x20 <= ord(c) <= 0x801F for c in v) and sum(ord(c) > 0x7F for c in v) >= len(v) // 2:
            cands.append(("utf16", [ord(c) - 32 for c in v], 15))
        h = s.lower()
        if len(h) >= 8 and len(h) % 4 == 0 and re.fullmatch(r"[0-9a-f]+", h):
            cands.append(("hex", [int(h[i:i + 4], 16) for i in range(0, len(h), 4)], 16))
        for form, vals, bits in cands:
            r = _lz_decompress(vals, bits)
            if r and r.isprintable() and _texty(r) >= 0.6:
                out.append((form, r))
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []
    return out


def lzstring_dec(t, form=None):
    """Undo lzstring_enc (any form, or the pinned one) -> text, else None."""
    return next((s for f, s in lzstring_reads(t) if form is None or f == form), None)


def lzstring_free(p):
    """Speculative Mastery-line decoder: the lz-string reading(s) of a line."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for s in dict.fromkeys(s for _f, s in lzstring_reads(p))][:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES += [(f"lzstring-{f}", (lambda f: lambda s: lzstring_enc(s, f))(f), (lambda f: lambda t: lzstring_dec(t, f))(f))
               for f in ("base64", "uri", "utf16", "hex")]



# ------------------------------------------------------------ signed web cookies (itsdangerous / Flask / Django signing)
# "Familiar wrapper": a Flask session cookie '.eJ<b64url(zlib(json))>.<ts>.<sig>' (leading dot = deflated), the plain
# itsdangerous 'eyJ<b64url(json)>[.<ts>].<sig>', and Django signing '[.]eJ...:<ts>:<sig>'. Payload part 0 is
# urlsafe base64 without padding; the signature is never checked (no key). The JSON body must parse: a bare base64
# line of prose is someone else's codec. A Mastery fragment may be only the '.eJ..' / 'eyJ..' payload part.
_SC_TOKEN = re.compile(r"\.?[A-Za-z0-9_-]{4,}={0,2}(?:[.:][A-Za-z0-9_=-]*)*")
_SC_HDR = re.compile(r"^\s*(?:set-)?cookie\s*:\s*", re.I)
_SC_NAME = re.compile(r"^[A-Za-z_][\w-]*=(?=[.A-Za-z0-9_-])")


def _sc_b64(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def signed_cookie_enc(s, form="flask", ts="ZPm9Gg", key=b"secret-key"):
    """Sign `s` (a JSON string) like itsdangerous / Django: form flask (deflated + ts), itsdangerous (+ts), its-nots,
    django (deflated) / django-plain. HMAC-SHA1 under a dummy key: the signature is shape only."""
    import hashlib
    import hmac
    import zlib
    b = json.dumps(s, separators=(",", ":")).encode()
    deflate = form in ("flask", "django")
    if deflate:
        b = zlib.compress(b)
    p = ("." if deflate else "") + base64.urlsafe_b64encode(b).decode().rstrip("=")
    sep = ":" if form.startswith("django") else "."
    v = p if form == "its-nots" else p + sep + ts
    sig = base64.urlsafe_b64encode(hmac.new(key, v.encode(), hashlib.sha1).digest()).decode().rstrip("=")
    return v + sep + sig


def _sc_leaves(o):
    """String leaves of a decoded JSON body, depth-first; Flask's tagged {" b": b64} bytes unwrapped to text."""
    out, stack = [], [o]
    while stack and len(out) < 256:
        x = stack.pop()
        if isinstance(x, dict):
            if len(x) == 1 and " b" in x and isinstance(x[" b"], str):
                try:
                    out.append(base64.b64decode(x[" b"], validate=True).decode("utf-8"))
                except Exception:   # noqa: BLE001
                    pass
                continue
            stack.extend(reversed(list(x.values())))
        elif isinstance(x, list):
            stack.extend(reversed(x))
        elif isinstance(x, str):
            out.append(x)
    return out


def signed_cookie_reads(t):
    """[(form, json_text, leaves)] for every signed-cookie part of one line/blob that is (deflated) base64url JSON.
    Never raises."""
    out = []
    try:
        if isinstance(t, (bytes, bytearray)):
            t = t.decode("utf-8")
        if not isinstance(t, str) or len(t) > 1 << 20:
            return out
        s = _SC_HDR.sub("", t.strip()).strip().strip("\"'")
        s = _SC_NAME.sub("", s, count=1).split(";")[0].strip().strip("\"'")
        if not _SC_TOKEN.fullmatch(s):
            return out
        sep = ":" if ":" in s and "." not in s.lstrip(".") else "."
        parts = s.split(":") if sep == ":" else s.split(".")
        if s.startswith("."):   # leading dot = deflated payload (split left an empty part 0)
            parts = ["." + parts[1]] + parts[2:] if sep == "." else parts
        for i, part in enumerate(parts):
            dot = part.startswith(".")
            body = part.lstrip(".").rstrip("=")
            if len(body) < 4 or len(body) % 4 == 1:
                continue
            try:
                raw = _sc_b64(body)
            except Exception:   # noqa: BLE001
                continue
            if dot or raw[:1] == b"x":
                import zlib
                try:
                    d = zlib.decompressobj()
                    z = d.decompress(raw, 1 << 20)
                    if not d.eof:
                        z = None
                except zlib.error:
                    z = None
                if z is None and dot:
                    continue
                raw = z if z is not None else raw
            try:
                txt = raw.decode("utf-8")
                obj = json.loads(txt)
            except (UnicodeDecodeError, ValueError):
                continue
            if not isinstance(obj, (str, dict, list)):
                continue
            form = ("django" if sep == ":" else "itsdangerous") + ("-zlib" if dot else "") + ("" if i == 0 else f"-p{i}")
            out.append((form, txt, _sc_leaves(obj)))
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []
    return out


def _sc_pick(txt, leaves):
    """The slug-holding string leaf, else the only string leaf, else the whole JSON text."""
    hit = next((x for x in leaves if SLUG.search(x)), None)
    if hit is not None:
        return hit
    if len(leaves) == 1 and leaves[0].strip():
        return leaves[0]
    return txt if txt.strip() not in ("", '""', "{}", "[]") else None


def signed_cookie_dec(t):
    """Undo a Flask/itsdangerous/Django signed cookie -> the slug string leaf (or the lone leaf / JSON text), else
    None."""
    for _f, txt, leaves in signed_cookie_reads(t):
        got = _sc_pick(txt, leaves)
        if got is not None:
            return got
    return None


def signed_cookie_free(p):
    """Speculative Mastery-line decoder: the decoded payload of a one-line signed cookie / its '.eJ..' fragment."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        outs = [x for _f, txt, lv in signed_cookie_reads(p) for x in (_sc_pick(txt, lv),) if x is not None]
        return [lead + s for s in dict.fromkeys(outs)][:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES += [(f"signed-cookie-{f}", (lambda f: lambda s: signed_cookie_enc(s, f))(f), signed_cookie_dec)
               for f in ("flask", "itsdangerous", "its-nots", "django", "django-plain")]


# ------------------------------------------------------------ JWT / JWS / JWE compact tokens (JOSE, "Familiar wrapper")
# 'eyJ<hdr>.eyJ<claims>.<sig>' (JWS; alg none leaves the sig empty) and the 5-part JWE 'hdr.key.iv.ct.tag'. Every
# segment is urlsafe base64 without padding; the header is JSON and, with "zip":"DEF", the payload is RAW deflate
# (RFC 7516, wbits -15). The signature is never checked. The claim string holding the slug wins (nested objects and
# JSON-in-a-string claims are walked), else the one non-registered claim. A Mastery fragment may be one segment alone
# (it must then be JSON). Prose, plain base64 of text, a truncated token or an encrypted JWE body -> None.
_JW_PREFIX = re.compile(r"^(?:[A-Za-z_][\w-]*\s*[:=]\s*)?(?:bearer\s+)?", re.I)
_JW_TOKEN = re.compile(r"[A-Za-z0-9_-]+={0,2}(?:\.[A-Za-z0-9_-]*={0,2}){0,4}")
_JW_REG = frozenset(("alg", "typ", "cty", "kid", "enc", "zip", "iss", "aud", "jti", "iat", "nbf", "exp", "sub",
                     "crit", "jku", "x5u", "x5t", "epk", "apu", "apv", "iv", "tag", "p2s", "p2c"))


def jwt_enc(s, form="hs256", key=b"secret"):
    """`s` as the "msg" claim of a compact JOSE token. form: none (alg none, empty sig), hs256, nested
    ({"data": {"msg": s}}), def (JWS-shaped, "zip":"DEF" raw-deflated claims), jwe (5-part, unencrypted raw-deflated
    ciphertext) or seg (the claims segment alone, a Mastery fragment)."""
    import hashlib
    import hmac

    def e(b):
        return base64.urlsafe_b64encode(b).decode().rstrip("=")

    def j(o):
        return json.dumps(o, separators=(",", ":")).encode()
    claims = j({"data": {"msg": s}} if form == "nested" else {"sub": "warmup", "msg": s})
    if form == "seg":
        return e(claims)
    hdr = {"alg": "none" if form == "none" else "HS256", "typ": "JWT"}
    if form in ("def", "jwe"):
        c = zlib.compressobj(9, zlib.DEFLATED, -15)
        claims = c.compress(claims) + c.flush()
        hdr["zip"] = "DEF"
    if form == "jwe":
        return ".".join((e(j({"alg": "dir", "enc": "A128GCM", "zip": "DEF"})), "", e(b"\0" * 12), e(claims),
                         e(b"\0" * 16)))
    v = e(j(hdr)) + "." + e(claims)
    return v + "." + ("" if form == "none" else e(hmac.new(key, v.encode(), hashlib.sha256).digest()))


def _jw_b64(s):
    s = s.rstrip("=")
    if len(s) % 4 == 1:
        raise ValueError("bad base64url length")
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _jw_inflate(b, wbits):
    try:
        d = zlib.decompressobj(wbits)
        z = d.decompress(b, 1 << 20)
        return z if d.eof and not d.unused_data else None
    except zlib.error:
        return None


def _jw_leaves(o, key=""):
    """[(claim_key, string)] depth-first; a string claim that is itself a JSON object/array is walked too."""
    out, stack = [], [(key, o, 0)]
    while stack and len(out) < 256:
        k, x, d = stack.pop()
        if isinstance(x, dict):
            stack.extend((str(kk), v, d) for kk, v in reversed(list(x.items())))
        elif isinstance(x, list):
            stack.extend((k, v, d) for v in reversed(x))
        elif isinstance(x, str):
            if d < 3 and x[:1] in "{[":
                try:
                    y = json.loads(x)
                    if isinstance(y, (dict, list)):
                        stack.append((k, y, d + 1))
                        continue
                except ValueError:
                    pass
            out.append((k, x))
    return out


def _jw_body(b, zipdef, need_json):
    """Decoded payload bytes -> leaves ([(key, str)]), else None. DEF = raw deflate (zlib-wrapped tolerated)."""
    if zipdef:
        b = _jw_inflate(b, -15) or _jw_inflate(b, 15)
        if b is None:
            return None
    try:
        txt = b.decode("utf-8")
    except UnicodeDecodeError:
        return None
    try:
        o = json.loads(txt)
    except ValueError:
        o = None
    if isinstance(o, (dict, list)):
        return _jw_leaves(o)
    if isinstance(o, str) and not need_json:
        return [("", o)]
    if need_json or not txt.strip() or not txt.isprintable() or _texty(txt) < 0.8:
        return None
    return [("", txt)]


def jwt_reads(t):
    """[(form, payload_leaves, header_leaves)] for one line/blob that is a compact JWS / JWE (or one JSON segment of
    one). Never raises."""
    out = []
    try:
        if isinstance(t, (bytes, bytearray)):
            t = t.decode("utf-8")
        if not isinstance(t, str) or len(t) > 1 << 20:
            return out
        s = t.strip().strip("\"'")
        s = _JW_PREFIX.sub("", s, count=1).split(";")[0].strip().strip("\"'")
        if not _JW_TOKEN.fullmatch(s):
            return out
        parts = s.split(".")
        if len(parts) == 1:
            try:
                raw = _jw_b64(parts[0])
            except ValueError:
                return out
            for zd in (False, True):
                lv = _jw_body(raw, zd, True)
                if lv:
                    out.append(("jose-seg" + ("-def" if zd else ""), lv, []))
                    break
            return out
        if len(parts) not in (2, 3, 5):
            return out
        try:
            hdr = json.loads(_jw_b64(parts[0]).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return out
        if not isinstance(hdr, dict) or not ({"alg", "enc", "typ"} & set(hdr)):
            return out
        zipdef = str(hdr.get("zip", "")).upper() == "DEF"
        hl = [(k, v) for k, v in _jw_leaves(hdr) if k not in _JW_REG]
        seg = parts[3] if len(parts) == 5 else parts[1]
        lv = None
        if seg:
            try:
                lv = _jw_body(_jw_b64(seg), zipdef, False)
            except ValueError:
                lv = None
        form = ("jwe" if len(parts) == 5 else "jws") + ("-def" if zipdef else "")
        if lv or hl:
            out.append((form, lv or [], hl))
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []
    return out


def _jw_pick(lv, hl):
    """The slug-holding claim, else the one non-registered payload claim (else the longest), else a header field."""
    for k, x in lv + hl:
        if SLUG.search(x):
            return x
    for pool in (lv, hl):
        free = [x for k, x in pool if k not in _JW_REG and x.strip()]
        if len(free) == 1:
            return free[0]
        if free:
            return max(free, key=len)
    rest = [x for _k, x in lv if x.strip()]
    return max(rest, key=len) if rest else None


def jwt_dec(t):
    """Undo a compact JWT / JWS / JWE (zip DEF inflated) or one JSON segment -> the slug claim (else the message
    claim), else None."""
    for _f, lv, hl in jwt_reads(t):
        got = _jw_pick(lv, hl)
        if got is not None:
            return got
    return None


def jwt_free(p):
    """Speculative Mastery-line decoder: the message claim of a one-line JOSE token / its lone claims segment."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        outs = [x for _f, lv, hl in jwt_reads(p) for x in (_jw_pick(lv, hl),) if x is not None]
        return [lead + s for s in dict.fromkeys(outs)][:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES += [(f"jwt-{f}", (lambda f: lambda s: jwt_enc(s, f))(f), jwt_dec)
               for f in ("none", "hs256", "nested", "def", "jwe", "seg")]


# ------------------------------------------------------------ SAML HTTP-Redirect (url-quoted base64 of raw deflate)
# Three seen layers stacked: D7 %XX over D1 base64 over D22 deflate with the zlib header removed (wbits -15), the
# SAML HTTP-Redirect binding. Cues: %2B / %2F / %3D inside base64-ish text, a 'SAMLRequest=' / 'data=' query key. The
# value may sit in a query string / URL / Location header, be form-decoded ('+' -> ' '), double-quoted (%252B), or
# carry a zlib / gzip header instead. The deflate stream must end exactly (no trailing bytes) and read as printable
# UTF-8; an XML body yields the text node / attribute holding the slug.
_SR_KV = re.compile(r"(?:^|[?&;\s])([A-Za-z_][\w.\-]*)=([^&;\s#\"'<>]*)")
_SR_B64 = re.compile(r"[A-Za-z0-9+/_\-]+={0,2}")


def saml_redirect_enc(s, kind="raw", form="quoted"):
    """`s` -> base64 of `kind` (raw deflate / zlib / gzip) -> form: quoted (%XX, uppercase), query
    ('SAMLRequest=<quoted>&RelayState=token') or bare (no quoting)."""
    wb = {"raw": -15, "zlib": 15, "gzip": 31}[kind]
    c = zlib.compressobj(9, zlib.DEFLATED, wb)
    b = base64.b64encode(c.compress(_u(s)) + c.flush()).decode()
    if form == "bare":
        return b
    q = urllib.parse.quote(b, safe="")
    return "SAMLRequest=" + q + "&RelayState=token" if form == "query" else q


def _sr_values(s):
    """Candidate (still-quoted) base64 values: query values (SAML / data keys first), then the whole token."""
    kv = [(k, v) for k, v in _SR_KV.findall(s) if v]
    kv.sort(key=lambda x: (not re.search(r"(?i)saml|^data$|^payload$", x[0]),))
    return list(dict.fromkeys([v for _k, v in kv] + [re.sub(r"\s+", "", s)]))


def _sr_unquote(v):
    """Every distinct base64 reading of a quoted value: %XX undone (once / twice), '+' kept or form-decoded ' ' -> '+'."""
    outs, cur = [], v
    for _ in range(3):
        outs.append(cur)
        if not re.search(r"%[0-9A-Fa-f]{2}", cur):
            break
        try:
            cur = urllib.parse.unquote(cur, errors="strict")
        except UnicodeDecodeError:
            break
    outs += [x.replace(" ", "+") for x in list(outs)]
    return [x for x in dict.fromkeys(outs) if _SR_B64.fullmatch(x)]


def _sr_inflate(b):
    """(kind, bytes) of the one complete raw / zlib / gzip stream `b` is, else None."""
    for kind, wb in (("raw", -15), ("zlib", 15), ("gzip", 31)):
        try:
            d = zlib.decompressobj(wb)
            out = d.decompress(b, 1 << 20)
            if d.eof and not d.unused_data and not d.unconsumed_tail:
                return kind, out
        except zlib.error:
            continue
    return None


def _sr_pick(txt):
    """An XML body -> the slug-holding text node / attribute value (else the lone text node); prose -> itself."""
    import html
    if not txt.lstrip().startswith("<"):
        return txt
    leaves = [html.unescape(x).strip() for x in re.findall(r">([^<]+)<", txt) + re.findall(r"=\s*\"([^\"]*)\"", txt)
              + re.findall(r"=\s*'([^']*)'", txt)]
    leaves = [x for x in leaves if x]
    hit = next((x for x in leaves if SLUG.search(x)), None)
    if hit is not None:
        return hit
    texts = [html.unescape(x).strip() for x in re.findall(r">([^<]+)<", txt) if x.strip()]
    return texts[0] if len(texts) == 1 else txt


def saml_redirect_reads(t):
    """[(form, text)] for every query value / bare token of `t` that is (url-quoted) base64 of a complete raw deflate
    / zlib / gzip stream reading as printable UTF-8. form = '<kind>-<quoted|bare>'. Never raises."""
    out = []
    try:
        if isinstance(t, (bytes, bytearray)):
            t = bytes(t).decode("utf-8")
        if not isinstance(t, str) or not t.strip() or len(t) > 1 << 20:
            return out
        for v in _sr_values(t.strip()):
            for u in _sr_unquote(v):
                body = u.rstrip("=")
                if len(body) < 4 or len(body) % 4 == 1 or (re.search(r"[+/]", body) and re.search(r"[-_]", body)):
                    continue
                try:
                    raw = base64.b64decode(body.replace("-", "+").replace("_", "/") + "=" * (-len(body) % 4),
                                           validate=True)
                except (ValueError, TypeError):
                    continue
                got = _sr_inflate(raw)
                if got is None:
                    continue
                try:
                    txt = got[1].decode("utf-8")
                except UnicodeDecodeError:
                    continue
                if not txt.strip() or not all(c.isprintable() or c in "\t\r\n" for c in txt):
                    continue
                out.append((f"{got[0]}-{'quoted' if u != v else 'bare'}", txt))
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []
    return list(dict.fromkeys(out))


def saml_redirect_dec(t):
    """Undo a SAML HTTP-Redirect value (query / %XX / base64 / raw deflate) -> the sentence (or the XML leaf holding
    the slug), else None."""
    r = saml_redirect_reads(t)
    return _sr_pick(r[0][1]) if r else None


def saml_redirect_free(p):
    """Speculative Mastery-line decoder: the inflated text of one SAML-redirect line."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for s in dict.fromkeys(_sr_pick(x) for _f, x in saml_redirect_reads(p))][:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES += [(f"saml-redirect-{k}-{f}", (lambda k, f: lambda s: saml_redirect_enc(s, k, f))(k, f), saml_redirect_dec)
               for k in ("raw", "zlib", "gzip") for f in ("quoted", "query")]


# ------------------------------------------------------------ PDF stream filter chains (ISO 32000-1 7.4)
# A document-flavoured 'inflate': `/Filter /Name` or `/Filter [/A /B ...]` (abbreviations AHx A85 LZW Fl RL too) applied
# in order to the bytes between 'stream\r?\n' and 'endstream' (/Length when direct and consistent, else up to the EOL
# before 'endstream'). ASCIIHexDecode = hex up to '>', ASCII85Decode = Adobe a85 up to '~>', FlateDecode = zlib (raw /
# gzip fallbacks), LZWDecode = MSB-first 9..12-bit LZW with /EarlyChange (default 1), RunLengthDecode = len <128 copy
# len+1, >128 repeat 257-len, 128 EOD. The PDF may come as text or base64 / hex of the file. Without the skeleton a
# bare chain is peeled only through a PDF-only marker ('~>'-closed a85, '>'-closed hex, LZW opening on its clear code
# and closing on EOD, RL closing on 128), up to 4 layers. A content stream yields its shown text ((..) Tj / [..] TJ).
_PDF_FN = {"ASCIIHexDecode": "AHx", "AHx": "AHx", "ASCII85Decode": "A85", "A85": "A85", "FlateDecode": "Fl",
           "Fl": "Fl", "LZWDecode": "LZW", "LZW": "LZW", "RunLengthDecode": "RL", "RL": "RL"}
_PDF_MAXOUT = 1 << 22
_PDF_STREAM = re.compile(rb"(?<![A-Za-z])stream(?:\r\n|\n|\r)")
_PDF_FILTER = re.compile(rb"/Filter\s*(\[[^\]]*\]|/[A-Za-z0-9]+)")
_PDF_LEN = re.compile(rb"/Length\s+(\d+)(?!\s+\d+\s+R)")
_PDF_TJ = re.compile(rb"\((?:\\.|[^\\)])*\)\s*(?:Tj|'|\")|\[(?:[^\]\\]|\\.)*\]\s*TJ", re.S)
_PDF_STR = re.compile(rb"\(((?:\\.|[^\\)])*)\)", re.S)
_PDF_ESC = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f"}


def _pdf_ahx(b, strict=False):
    s = re.sub(rb"\s+", b"", b)
    if strict and s.startswith(b"<"):
        s = s[1:]
    i = s.find(b">")
    if strict and (i < 0 or s[i + 1:]):
        raise ValueError("AHx EOD")
    s = s if i < 0 else s[:i]
    if not re.fullmatch(rb"[0-9A-Fa-f]*", s) or (strict and len(s) < 2):
        raise ValueError("AHx")
    return bytes.fromhex((s + b"0" * (len(s) % 2)).decode())


def _pdf_a85(b, strict=False):
    s = re.sub(rb"\s+", b"", b)
    if s.startswith(b"<~"):
        s = s[2:]
    i = s.find(b"~>")
    if strict and (i < 0 or s[i + 2:]):
        raise ValueError("A85 EOD")
    s = s if i < 0 else s[:i]
    if not re.fullmatch(rb"[!-uz]*", s) or (strict and len(s) < 2):
        raise ValueError("A85")
    return base64.a85decode(s)


def _pdf_flate(b, strict=False):
    for wb in ((15,) if strict else (15, -15, 31)):
        try:
            d = zlib.decompressobj(wb)
            out = d.decompress(b, _PDF_MAXOUT)
            if out and (d.eof or not strict):
                return out
        except zlib.error:
            continue
    raise ValueError("Fl")


def _pdf_lzw(b, strict=False, early=1):
    if strict and (len(b) < 3 or b[0] != 0x80 or b[1] & 0x80):
        raise ValueError("LZW clear")
    tab = [bytes([i]) for i in range(256)] + [b"", b""]
    out, prev, bits, acc, nacc = bytearray(), None, 9, 0, 0
    for byte in b:
        acc, nacc = (acc << 8) | byte, nacc + 8
        while nacc >= bits:
            nacc -= bits
            code = (acc >> nacc) & ((1 << bits) - 1)
            acc &= (1 << nacc) - 1
            if code == 256:
                del tab[258:]
                prev, bits = None, 9
                continue
            if code == 257:
                return bytes(out)
            if code < len(tab) and (code < 256 or code > 257):
                e = tab[code]
            elif code == len(tab) and prev is not None:
                e = prev + prev[:1]
            else:
                raise ValueError("LZW code")
            out += e
            if len(out) > _PDF_MAXOUT:
                raise ValueError("LZW size")
            if prev is not None and len(tab) < 4096:
                tab.append(prev + e[:1])
            prev = e
            n = len(tab) + early
            bits = 9 if n < 512 else 10 if n < 1024 else 11 if n < 2048 else 12
    if strict:
        raise ValueError("LZW EOD")
    return bytes(out)


def _pdf_rl(b, strict=False):
    out, i = bytearray(), 0
    while i < len(b):
        n = b[i]
        i += 1
        if n == 128:
            if strict and i != len(b):
                raise ValueError("RL tail")
            return bytes(out)
        if n < 128:
            if i + n + 1 > len(b):
                raise ValueError("RL short")
            out += b[i:i + n + 1]
            i += n + 1
        else:
            if i >= len(b):
                raise ValueError("RL short")
            out += b[i:i + 1] * (257 - n)
            i += 1
        if len(out) > _PDF_MAXOUT:
            raise ValueError("RL size")
    if strict:
        raise ValueError("RL EOD")
    return bytes(out)


_PDF_DEC = {"AHx": _pdf_ahx, "A85": _pdf_a85, "Fl": _pdf_flate, "LZW": _pdf_lzw, "RL": _pdf_rl}


def _pdf_unesc(s):
    out, i = bytearray(), 0
    while i < len(s):
        c = s[i:i + 1]
        if c != b"\\" or i + 1 >= len(s):
            out += c
            i += 1
            continue
        n = s[i + 1:i + 2]
        m = re.match(rb"[0-7]{1,3}", s[i + 1:i + 4])
        if m:
            out.append(int(m.group(), 8) & 0xFF)
            i += 1 + len(m.group())
        elif n in (b"\r", b"\n"):
            i += 3 if s[i + 1:i + 3] == b"\r\n" else 2
        else:
            out += _PDF_ESC.get(n, n)
            i += 2
    return bytes(out)


def _pdf_shown(b):
    """The text a content stream shows ((..) Tj / ' / " and [(..) n (..)] TJ), joined; None if it shows none."""
    parts = [_pdf_unesc(s) for m in _PDF_TJ.finditer(b) for s in _PDF_STR.findall(m.group())]
    return b"".join(parts) if parts else None


def pdf_streams(data):
    """[(filters, decoded bytes)] for every stream object of the PDF `data` (bytes) whose /Filter chain is all
    supported and decodes. Never raises."""
    out = []
    try:
        for m in _PDF_STREAM.finditer(data):
            head = data[max(0, m.start() - 4096):m.start()]
            k = head.rfind(b"obj")
            head = head[k + 3:] if k >= 0 else head
            k = head.rfind(b"endobj")
            head = head[k + 6:] if k >= 0 else head
            st, e = m.end(), data.find(b"endstream", m.end())
            if e < 0:
                continue
            ln = _PDF_LEN.search(head)
            if ln and st + int(ln.group(1)) <= e and not data[st + int(ln.group(1)):e].strip(b"\r\n \t"):
                body = data[st:st + int(ln.group(1))]
            else:
                body = data[st:e]
                body = body[:-2] if body.endswith(b"\r\n") else body[:-1] if body.endswith((b"\n", b"\r")) else body
            fm = _PDF_FILTER.search(head)
            names = [x.decode() for x in re.findall(rb"/([A-Za-z0-9]+)", fm.group(1))] if fm else []
            if any(n not in _PDF_FN for n in names):
                continue
            early = 0 if re.search(rb"/EarlyChange\s+0\b", head) else 1
            try:
                for n in names:
                    f = _PDF_FN[n]
                    body = _pdf_lzw(body, early=early) if f == "LZW" else _PDF_DEC[f](body)
            except Exception:   # noqa: BLE001 -- a broken stream reads as nothing
                continue
            out.append(([_PDF_FN[n] for n in names], body))
    except Exception:   # noqa: BLE001
        return out
    return out


def _pdf_bare(b, depth=4):
    """[(chain, bytes)] for every skeleton-less peel of `b` through strict PDF filters (outermost first)."""
    out, todo, seen = [], [((), b)], set()
    while todo:
        chain, x = todo.pop(0)
        if len(chain) >= depth:
            continue
        for f in ("A85", "AHx", "Fl", "LZW", "RL"):
            if chain and chain[-1] == f and f in ("A85", "AHx"):
                continue
            try:
                y = _PDF_DEC[f](x, strict=True)
            except Exception:   # noqa: BLE001
                continue
            if not y or (f, y) in seen:
                continue
            seen.add((f, y))
            out.append((chain + (f,), y))
            todo.append((chain + (f,), y))
    return out


def _pdf_sources(t):
    """[(form, pdf bytes)] for `t` as PDF text / bytes, or base64 / hex / ... of a PDF file."""
    if isinstance(t, (bytes, bytearray)):
        raw = bytes(t)
    elif isinstance(t, str):
        raw = t.encode("latin-1", "replace") if all(ord(c) < 256 for c in t) else t.encode("utf-8")
    else:
        return []
    out = [("pdf", raw)] if _PDF_STREAM.search(raw) and b"endstream" in raw else []
    if not out and len(raw) < 400000:
        out += [(f"pdf-{w}", b) for w, b in _dz_wrappers(raw.decode("latin-1").strip())
                if _PDF_STREAM.search(b) and b"endstream" in b]
    return out


def pdf_chain_reads(t):
    """[(name, text)] for every PDF stream (or bare PDF filter chain) of `t` that decodes to printable text; a content
    stream also yields its shown text first. Never raises."""
    out = []
    try:
        srcs = _pdf_sources(t)
        hits = [(f"{form}[{'+'.join(ch) or 'none'}]", b) for form, data in srcs for ch, b in pdf_streams(data) if ch]
        if not srcs:
            s = t.strip() if isinstance(t, str) else bytes(t).strip()
            s = s.encode("latin-1") if isinstance(s, str) and all(ord(c) < 256 for c in s) else s
            if isinstance(s, bytes) and 4 <= len(s) <= 400000:
                hits = [(f"pdf-bare[{'+'.join(ch)}]", b) for ch, b in _pdf_bare(s) if set(ch) - {"Fl"}]
                for w, x in _dz_wrappers(s.decode("latin-1")):   # base64 / hex of a binary chain: LZW / RL only
                    hits += [(f"pdf-bare-{w}[{'+'.join(ch)}]", b) for ch, b in _pdf_bare(x, 3)
                             if set(ch) & {"LZW", "RL"}]
        for name, b in hits:
            sh = _pdf_shown(b)
            for tag, x in ((f"{name}:Tj", sh), (name, b)):
                txt = _dz_text(x) if x else None
                if txt is not None:
                    out.append((tag, txt))
    except Exception:   # noqa: BLE001
        return out
    return list(dict.fromkeys(out))


def pdf_chain_solve(t):
    """(name, sentence) for the first PDF stream reading holding the slug in English, else None."""
    reads = pdf_chain_reads(t)
    for name, s in reads:
        if SLUG.search(s) and _kbd_score(s) >= _RD_OK:
            return name, s.strip("\r\n")
    for name, s in reads:
        rd = _rd_inner(s, 2, time.monotonic() + 0.4)
        if rd:
            return f"{name}[{rd[0]}]", rd[1]
    return None


def pdf_chain_dec(t):
    r = pdf_chain_solve(t)
    return r[1] if r else None


def pdf_chain_free(p):
    """Speculative Mastery-line decoder: the decoded stream text of a one-line PDF (base64 / hex) or bare chain."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        outs = []
        for _n, s in pdf_chain_reads(p.strip()):
            s = s.strip("\r\n")
            outs += _rd_free(s) + [s]
        return [lead + s for s in dict.fromkeys(outs)][:2]
    except Exception:   # noqa: BLE001
        return []


def _pdf_lzw_enc(b):
    """PDF LZWDecode encoder (EarlyChange 1): clear, codes MSB-first 9..12 bits (width of the next free code), EOD."""
    def width(n):
        return 9 if n < 512 else 10 if n < 1024 else 11 if n < 2048 else 12

    tab, codes, w, nxt = {bytes([i]): i for i in range(256)}, [(256, 9)], b"", 258
    for c in b:
        wc = w + bytes([c])
        if wc in tab or not w:
            w = wc
            continue
        codes.append((tab[w], width(nxt)))
        tab[wc], nxt = nxt, nxt + 1
        if nxt >= 4094:
            codes.append((256, width(nxt)))
            tab, nxt = {bytes([i]): i for i in range(256)}, 258
        w = bytes([c])
    if w:
        codes.append((tab[w], width(nxt)))
        nxt += 1
    codes.append((257, width(nxt)))
    acc = n = 0
    out = bytearray()
    for v, k in codes:
        acc, n = (acc << k) | v, n + k
        while n >= 8:
            n -= 8
            out.append((acc >> n) & 0xFF)
    if n:
        out.append((acc << (8 - n)) & 0xFF)
    return bytes(out)


def _pdf_rl_enc(b):
    out = bytearray()
    for i in range(0, len(b), 128):
        c = b[i:i + 128]
        out += bytes([len(c) - 1]) + c
    return bytes(out + b"\x80")


_PDF_ENC = {"AHx": lambda b: b.hex().encode() + b">", "A85": lambda b: base64.a85encode(b, adobe=True)[2:],
            "Fl": zlib.compress, "LZW": _pdf_lzw_enc, "RL": _pdf_rl_enc}
_PDF_LONG = {v: k for k, v in _PDF_FN.items() if len(k) > 3}


def pdf_chain_enc(s, chain=("A85", "Fl"), skeleton=True):
    """`s` under the PDF filter chain (first = outermost, as in /Filter): a one-object PDF (base64 when binary), or
    the bare chain bytes (a85 keeps its '<~' when outermost) as text / base64."""
    b = _u(s)
    for f in reversed(chain):
        b = _PDF_ENC[f](b)
    if not skeleton:
        if chain[0] == "A85":
            b = b"<~" + b
        return b.decode("ascii") if chain[0] in ("A85", "AHx") else base64.b64encode(b).decode()
    flt = "/" + _PDF_LONG[chain[0]] if len(chain) == 1 else "[" + " ".join("/" + _PDF_LONG[f] for f in chain) + "]"
    pdf = (b"%PDF-1.4\n1 0 obj\n<< /Length " + str(len(b)).encode() + b" /Filter " + flt.encode() + b" >>\nstream\n"
           + b + b"\nendstream\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n")
    return pdf.decode("ascii") if chain[0] in ("A85", "AHx") else base64.b64encode(pdf).decode()


CANDIDATES += [(f"pdf-{'-'.join(c).lower()}{'' if k else '-bare'}", (lambda c, k: lambda s: pdf_chain_enc(s, c, k))(c, k),
                pdf_chain_dec)
               for c, k in ((("A85", "Fl"), False), (("AHx", "Fl"), False), (("A85", "Fl"), True),
                            (("Fl",), True), (("A85", "LZW"), True), (("AHx", "RL"), True))]

# ------------------------------------ inflate-then-header containers (speculative, coverage atlas target inflate-container-headers)
# D22's zlib, but the inflated bytes carry a container header that a strict 'starts with Nice work' gate (and the
# printable-text gate of decompress_reads) rejects: a git loose object (zlib of 'blob|commit|tag|tree <len>\0' + body;
# the length must match, a commit / tag yields its message), a PNG text chunk (tEXt, zTXt = zlib, iTXt optionally
# zlib; every chunk CRC verified), and an HTTP message ('Transfer-Encoding: chunked' hex size lines de-chunked, then
# Content-Encoding gzip / x-gzip / deflate (zlib or raw) / br / zstd undone right to left), also a bare chunked body.
# Under any _dz_wrappers reading (base64 / hex / ... / raw bytes) or as the raw text itself. After every inflate a git
# header is stripped. container_reads(t) -> [(form, text)]; an XML / HTML body yields its slug-holding leaf. Never raises.
_IC_GIT = re.compile(rb"(blob|commit|tag|tree) (\d+)\x00")
_IC_PNG = b"\x89PNG\r\n\x1a\n"
_IC_HTTP = re.compile(rb"(?:HTTP/\d(?:\.\d)? \d{3}[^\r\n]*|[A-Z]+ \S+ HTTP/\d(?:\.\d)?)\r?\n")


def _ic_git(d):
    """Body of a git object `d` ('<type> <len>\\0' + exactly len bytes): blob = all, commit / tag = the message after
    the header block, tree = None (binary). `d` without the header -> None."""
    m = _IC_GIT.match(d)
    if not m or int(m.group(2)) != len(d) - m.end():
        return None
    kind, body = m.group(1), d[m.end():]
    if kind == b"tree":
        return None
    if kind != b"blob":
        body = body.split(b"\n\n", 1)[1].rstrip(b"\n") if b"\n\n" in body else None
    return body


def _ic_inflate(b):
    """(kind, bytes) of the one complete zlib / raw deflate / gzip stream `b` is, else None."""
    for kind, wb in (("zlib", 15), ("raw", -15), ("gzip", 31)):
        try:
            d = zlib.decompressobj(wb)
            out = d.decompress(b, _DZ_MAX)
            if d.eof and not d.unused_data and not d.unconsumed_tail:
                return kind, out
        except zlib.error:
            continue
    return None


def _ic_png(b):
    """[(form, bytes)] for the text chunks of a PNG (CRC-checked; a bad CRC / truncation drops the chunk and stops)."""
    out, i = [], 8
    while i + 12 <= len(b):
        n, typ = int.from_bytes(b[i:i + 4], "big"), b[i + 4:i + 8]
        data, crc = b[i + 8:i + 8 + n], b[i + 8 + n:i + 12 + n]
        if len(data) != n or len(crc) != 4 or zlib.crc32(typ + data) != int.from_bytes(crc, "big"):
            break
        i += 12 + n
        if typ == b"IEND":
            break
        kw, _s, rest = data.partition(b"\x00")
        if not _s:
            continue
        if typ == b"tEXt":
            out.append(("png-text", rest.decode("latin-1").encode("utf-8")))
        elif typ == b"zTXt" and rest[:1] == b"\x00":
            z = _ic_inflate(rest[1:])
            if z and z[0] == "zlib":
                out.append(("png-ztxt", z[1].decode("latin-1").encode("utf-8")))
        elif typ == b"iTXt" and len(rest) >= 2:
            flag, meth = rest[0], rest[1]
            parts = rest[2:].split(b"\x00", 2)
            if len(parts) != 3:
                continue
            txt = parts[2]
            if flag == 1:
                z = _ic_inflate(txt) if meth == 0 else None
                if not z or z[0] != "zlib":
                    continue
                txt = z[1]
            out.append(("png-itxt" + ("-z" if flag == 1 else ""), txt))
    return out


def _ic_dechunk(b):
    """HTTP/1.1 chunked body -> bytes (size line hex [;ext], CRLF or LF, a 0 chunk ends; trailers ignored), else None."""
    out, i = bytearray(), 0
    while True:
        j = b.find(b"\n", i)
        if j < 0:
            return None
        m = re.fullmatch(rb"\s*([0-9A-Fa-f]{1,8})\s*(?:;[^\r\n]*)?\r?", b[i:j])
        if not m:
            return None
        n, i = int(m.group(1), 16), j + 1
        if n == 0:
            return bytes(out)
        if i + n > len(b):
            return None
        out += b[i:i + n]
        i += n
        if b[i:i + 2] == b"\r\n":
            i += 2
        elif b[i:i + 1] == b"\n":
            i += 1
        else:
            return None


def _ic_coding(b, enc):
    """Undo one Content-Encoding token, else None."""
    enc = enc.strip().lower()
    if enc in ("", "identity", "chunked"):
        return b
    if enc in ("gzip", "x-gzip", "deflate"):
        z = _ic_inflate(b)
        return z[1] if z and (z[0] == "gzip") == (enc != "deflate") else None
    try:
        if enc == "br":
            import brotli
            return brotli.decompress(b)
        if enc == "zstd":
            import zstandard
            return zstandard.ZstdDecompressor().decompressobj().decompress(b)
    except Exception:   # noqa: BLE001
        return None
    return None


def _ic_http(b):
    """(form, body bytes) of one HTTP request / response with its transfer + content codings undone, else None."""
    m = _IC_HTTP.match(b)
    if not m:
        return None
    k = b.find(b"\r\n\r\n", m.end() - 2)
    k, sep = (k, 4) if k >= 0 else (b.find(b"\n\n", m.end() - 1), 2)
    if k < 0:
        return None
    hdr = {}
    for ln in b[m.end():k].decode("latin-1").splitlines():
        name, _c, v = ln.partition(":")
        if _c:
            hdr[name.strip().lower()] = (hdr.get(name.strip().lower(), "") + "," + v.strip()).strip(",")
    body = b[k + sep:]
    te = [x.strip().lower() for x in hdr.get("transfer-encoding", "").split(",") if x.strip()]
    if "chunked" in te:
        body = _ic_dechunk(body)
    elif hdr.get("content-length", "").strip().isdigit():
        n = int(hdr["content-length"])
        body = body[:n] if len(body) >= n else None
    if body is None:
        return None
    ce = [x for x in hdr.get("content-encoding", "").split(",") if x.strip()]
    for enc in reversed(ce):
        body = _ic_coding(body, enc)
        if body is None:
            return None
    form = "http" + ("-chunked" if "chunked" in te else "") + "".join("-" + x.strip().lower() for x in ce)
    return form, body


def _ic_text(form, d):
    """[(form, text)] for an opened container body: printable UTF-8 as-is, else a git object / one more inflate."""
    s = _txt(d) if d else None
    if s is not None and s.strip():
        return [(form, s)]
    g = _ic_git(d or b"")
    if g is not None:
        return _ic_text(form + "-git", g)
    z = _ic_inflate(d) if d and form.count("-") < 6 else None
    return _ic_text(f"{form}-{z[0]}", z[1]) if z else []


def _ic_bytes(b):
    """[(form, text)] for one candidate byte string."""
    out = []
    if b.startswith(_IC_PNG):
        for form, d in _ic_png(b):
            out += _ic_text(form, d)
        return out
    h = _ic_http(b)
    if h:
        return _ic_text(*h)
    if re.match(rb"\s*[0-9A-Fa-f]{1,8}\s*(?:;[^\r\n]*)?\r?\n", b):
        d = _ic_dechunk(b)
        if d:
            z = _ic_inflate(d)
            if z:
                return _ic_text("chunked-" + z[0], z[1])
            for enc in ("br", "zstd"):
                x = _ic_coding(d, enc)
                if x:
                    return _ic_text("chunked-" + enc, x)
    z = _ic_inflate(b)
    if z:
        g = _ic_git(z[1])
        if g is not None:
            out += _ic_text(f"git-{z[0]}", g)
    return out


def container_reads(t):
    """[(form, text)] for every wrapper reading of `t` that opens as a git loose object / PNG text chunk / HTTP message
    (chunked + content-coded) / bare chunked compressed body. Never raises."""
    out = []
    try:
        if isinstance(t, (bytes, bytearray)):
            cands = _dz_wrappers(bytes(t))
        elif isinstance(t, str) and t.strip() and len(t) <= 1 << 20:
            cands = _dz_wrappers(t)
            try:
                cands = [("text", t.lstrip().encode("latin-1"))] + cands
            except UnicodeEncodeError:
                pass
        else:
            return out
        for wrapper, b in cands:
            if len(b) >= 8:
                out += [(f"{form}-{wrapper}", s) for form, s in _ic_bytes(b)]
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []
    return list(dict.fromkeys(out))


def container_dec(t):
    """The slug-holding container text of `t` (else the first one), else None."""
    r = [_sr_pick(s) for _f, s in container_reads(t)]
    return next((s for s in r if SLUG.search(s)), r[0] if r else None)


def container_free(p):
    """Speculative Mastery-line decoder: the opened container text of one line."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for s in dict.fromkeys(_sr_pick(x) for _f, x in container_reads(p))][:2]
    except Exception:   # noqa: BLE001
        return []


def _ic_chunk(n, tag, data):
    return n.to_bytes(4, "big") + tag + data + zlib.crc32(tag + data).to_bytes(4, "big")


def container_enc(s, form="git-blob"):
    """`s` -> base64 of: git-blob (zlib level 1 of 'blob <len>\\0' + s, as git writes loose objects), png-ztxt /
    png-itxt (a 1x1 PNG with a zTXt / compressed iTXt 'Comment'), http-chunked-gzip (an HTTP/1.1 200 response,
    gzip Content-Encoding, 'Transfer-Encoding: chunked' in 32-byte chunks)."""
    b = _u(s)
    if form == "git-blob":
        return base64.b64encode(zlib.compress(b"blob %d\x00" % len(b) + b, 1)).decode()
    if form.startswith("png-"):
        txt = (b"Comment\x00\x00" + zlib.compress(b) if form == "png-ztxt"
               else b"Comment\x00\x01\x00\x00\x00" + zlib.compress(b))
        tag = b"zTXt" if form == "png-ztxt" else b"iTXt"
        png = (_IC_PNG + _ic_chunk(13, b"IHDR", b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x00\x00\x00\x00")
               + _ic_chunk(len(txt), tag, txt) + _ic_chunk(10, b"IDAT", zlib.compress(b"\x00\x00"))
               + _ic_chunk(0, b"IEND", b""))
        return base64.b64encode(png).decode()
    if form == "http-chunked-gzip":
        z = gzip.compress(b, mtime=0)
        body = b"".join(b"%x\r\n" % len(z[i:i + 32]) + z[i:i + 32] + b"\r\n" for i in range(0, len(z), 32))
        msg = (b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Encoding: gzip\r\n"
               b"Transfer-Encoding: chunked\r\n\r\n" + body + b"0\r\n\r\n")
        return base64.b64encode(msg).decode()
    return None


CANDIDATES += [(f"inflate-container-{f}", (lambda f: lambda s: container_enc(s, f))(f), container_dec)
               for f in ("git-blob", "png-ztxt", "png-itxt", "http-chunked-gzip")]


# HTTP/1.1 CHUNKED TRANSFER as a text framing (speculative, no day; coverage atlas target http-chunked-transfer,
# "Count carefully" in base 16): `<hex size>[;ext[=val]]` CRLF, exactly size bytes (UTF-8; chars as a fallback), CRLF,
# ... a 0 chunk ends (trailer headers / the final blank line optional, LF-only lines tolerated, a run that stops
# cleanly at a chunk boundary without the 0 chunk is kept). Also the one-line form with literal `\r\n` / `\n` escapes
# (a Mastery line), an HTTP message carrying it, every _dz_wrappers reading, and a gzip / zlib / raw deflate / br /
# zstd body (inflate-container's _ic_* helpers). Inflate-container keeps the HTTP-message / bare compressed forms;
# this adds the plain bare body. chunked_reads(t) -> [(form, text)]. Never raises.
_HC_SIZE = {bytes: re.compile(rb"[ \t]*([0-9A-Fa-f]{1,16})[ \t]*(;[^\r\n]*)?\r?(?:\n|\Z)"),
            str: re.compile(r"[ \t]*([0-9A-Fa-f]{1,16})[ \t]*(;[^\r\n]*)?\r?(?:\n|\Z)")}


def _hc_dechunk(b):
    """bytes (size = bytes) or str (size = characters) -> (payload, ended_by_0) for a WHOLE chunked body, else None."""
    rx, crlf, lf = _HC_SIZE[type(b)], *(("\r\n", "\n") if isinstance(b, str) else (b"\r\n", b"\n"))
    out, i, n, k = [], 0, len(b), 0
    while True:
        if i >= n or not b[i:].strip():
            return (b[:0].join(out), False) if k >= 2 else None    # clean stop at a chunk boundary, no 0 chunk
        m = rx.match(b, i)
        if not m:
            return None
        size, i = int(m.group(1), 16), m.end()
        if size == 0:
            return (b[:0].join(out), True) if k else None          # trailers / final CRLF ignored
        if i + size > n:
            return None                                            # truncated mid-chunk
        out.append(b[i:i + size])
        i, k = i + size, k + 1
        if b[i:i + 2] == crlf:
            i += 2
        elif b[i:i + 1] == lf:
            i += 1
        elif i < n:
            return None                                            # size disagrees with the data


def _hc_unescape(t):
    """One-line text with literal \\r\\n / \\n escapes (and no real newline) -> the real-newline text, else None."""
    if "\n" in t.strip() or not re.search(r"\\r\\n|\\n", t):
        return None
    return re.sub(r"\\r\\n|\\n|\\r", lambda m: {"\\r\\n": "\r\n", "\\n": "\n", "\\r": "\r"}[m.group()], t)


def _hc_body(form, d):
    """[(form, text)] for a de-chunked payload: printable text as-is, else one content coding undone."""
    if isinstance(d, str):
        return [(form, d)] if d.strip() and _txt(d.encode("utf-8")) is not None else []
    s = _txt(d)
    if s is not None and s.strip():
        return [(form, s)]
    z = _ic_inflate(d)
    if z:
        s = _txt(z[1])
        return [(f"{form}-{z[0]}", s)] if s and s.strip() else []
    for enc in ("br", "zstd"):
        x = _ic_coding(d, enc)
        s = _txt(x) if x else None
        if s and s.strip():
            return [(f"{form}-{enc}", s)]
    return []


def _hc_bytes(form, b):
    """[(form, text)] for one candidate buffer (an HTTP message, else a bare chunked body: bytes, then chars)."""
    if isinstance(b, bytes) and _IC_HTTP.match(b):
        h = _ic_http(b)
        return [(f"{form}-{h[0]}", s) for _f, s in _ic_text(*h)] if h and "chunked" in h[0] else []
    if not _HC_SIZE[type(b)].match(b):
        return []
    r = _hc_dechunk(b)
    if r:
        return _hc_body(form + ("" if r[1] else "-no0"), r[0])
    return []


def chunked_reads(t):
    """[(form, text)] for every reading of `t` as an HTTP/1.1 chunked body (raw / escaped one-line / wrapped)."""
    out = []
    try:
        if isinstance(t, (bytes, bytearray)):
            t = bytes(t)
            out += _hc_bytes("raw", t)
            try:
                t = t.decode("utf-8")
            except UnicodeDecodeError:
                return out
        if not isinstance(t, str) or not t.strip() or len(t) > 1 << 20:
            return out
        texts = [("text", t.lstrip(" \t"))]
        u = _hc_unescape(t.strip())
        if u is not None:
            texts.append(("escaped", u))
        for form, s in texts:
            b = s.encode("utf-8")
            r = _hc_bytes(form, b)
            if not r and not s.isascii():
                r = _hc_bytes(form + "-chars", s)
            out += r
        if not out:
            for wrapper, b in _dz_wrappers(t):
                if len(b) >= 5:
                    out += _hc_bytes(wrapper, b)
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []
    return list(dict.fromkeys(out))


def chunked_dec(t):
    """The slug-holding de-chunked text of `t` (else the first reading), else None."""
    r = [_sr_pick(s) for _f, s in chunked_reads(t)]
    return next((s for s in r if SLUG.search(s)), r[0] if r else None)


def chunked_free(p):
    """Speculative Mastery-line decoder: one line that is an escaped / wrapped chunked body -> its text."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return [lead + s for s in dict.fromkeys(_sr_pick(x).strip("\r\n") for _f, x in chunked_reads(p))
                if s and s.isprintable()][:2]
    except Exception:   # noqa: BLE001
        return []


def chunked_enc(s, sizes=(16,), eol="\r\n", ext="", final=True, escaped=False, coding=None, upper=False):
    """Plain -> an HTTP/1.1 chunked body: chunks cycling through `sizes` (0 = one chunk per word incl. its space),
    hex size (`upper` digits) + `ext` chunk extension, `eol` line ends, the '0' chunk + blank line when `final`,
    `escaped` = one line with literal \\r\\n, `coding` gzip / deflate = the compressed body base64'd."""
    b = _u(s)
    if coding:
        b = gzip.compress(b, mtime=0) if coding == "gzip" else zlib.compress(b)
    if sizes == (0,):
        parts = re.findall(rb"\S+\s*", b)
    else:
        parts, i, k = [], 0, 0
        while i < len(b):
            parts.append(b[i:i + sizes[k % len(sizes)]])
            i, k = i + sizes[k % len(sizes)], k + 1
    e = eol.encode()
    out = b"".join((b"%X" if upper else b"%x") % len(c) + ext.encode() + e + c + e for c in parts)
    out += (b"0" + e + e) if final else b""
    if coding:
        return base64.b64encode(out).decode()
    t = out.decode("utf-8")
    return t.replace("\r", "\\r").replace("\n", "\\n") if escaped else t


CANDIDATES += [
    ("http-chunked-1char", lambda s: chunked_enc(s, (1,)), chunked_dec),
    ("http-chunked-words", lambda s: chunked_enc(s, (0,)), chunked_dec),
    ("http-chunked-16", lambda s: chunked_enc(s, (16,), upper=True), chunked_dec),
    ("http-chunked-ext", lambda s: chunked_enc(s, (10,), ext=";name=value"), chunked_dec),
    ("http-chunked-lf", lambda s: chunked_enc(s, (7,), eol="\n", final=False), chunked_dec),
    ("http-chunked-escaped", lambda s: chunked_enc(s, (8,), escaped=True), chunked_dec),
    ("http-chunked-gzip-b64", lambda s: chunked_enc(s, (32,), coding="gzip"), chunked_dec),
]


# ------------------------------------------------------------ text-level compression (keyless 'pressure' / 'squeeze')
# Compression written out as TEXT, no binary bytes: run-length ('3a2b' count-first / 'a3b2' count-after, count always
# >= 1 or omitted for a single char, a digit char optionally '\'-escaped), LZ77 '(offset,length,char)' tuples (offset =
# distance back; also the (length,offset) order), LZW as an integer list (ASCII codes, later ones >= 256: initial dict
# 256, 8-bit + clear 256 / end 257 first-free 258, 7-bit 128) and Huffman as a '{char: bits}' table + a bit string.
# Every read must consume the whole input and come out printable; a speculative Mastery line must also be a piece of
# the warmups template (or its tail + slug chars), so prose, hex or decimal char codes don't read as compression.
_TC_SLUGBIT = re.compile(r"[a-z0-9-]*")
_TC_WORDS = set(re.findall(r"[a-z]+", _TPL.lower()))


def _tc_piece(x):
    """`x` if it is a piece of the warmups sentence (template substring, its tail + slug chars, or slug chars)."""
    if not x or len(x) < 3 or not x.isprintable():
        return None
    if x in _TPL:
        return x
    for i in range(len(_TPL)):
        if x.startswith(_TPL[i:]) and _TC_SLUGBIT.fullmatch(x[len(_TPL) - i:]):
            return x
    if re.fullmatch(r"[a-z]*(?:-[a-z]+)*-?\d*", x) and ("-" in x or x[-1].isdigit()) and not re.search(r"(.)\1\1", x):
        return x
    return None


def _tc_score(s):
    return (bool(SLUG.search(s)) and _TPL in s, bool(_tc_piece(s)),
            sum(w in _TC_WORDS for w in re.findall(r"[a-z]+", s.lower())), _texty(s))


def _tc_best(reads):
    """The most sentence-like reading; None unless it is a template piece / holds a slug / reads as template words."""
    reads = [s for s in reads if s and (s.isprintable() or s.replace("\n", "").isprintable())]
    reads = [s for s in reads if _tc_piece(s) or SLUG.search(s) or (_tc_score(s)[2] >= 2 and _texty(s) >= 0.9)]
    return max(reads, key=_tc_score) if reads else None


def rle_enc(s, order="cf", ones=True):
    """Run-length: order cf = '3a' (count first) / ca = 'a3'; ones=False omits the count of a single char."""
    out = []
    for ch, g in itertools.groupby(s):
        n = len(list(g))
        c = str(n) if (ones or n > 1) else ""
        out.append(c + ch if order == "cf" else ch + c)
    return "".join(out)


def rle_reads(t, cap=6):
    """Every whole-input RLE reading of `t` (4 layouts, counts 1-2 digits, '\\'-escaped chars), up to `cap` per layout."""
    out = []
    n = len(t)
    nd = sum(c.isdigit() for c in t)
    if not 2 <= n <= 1500 or not nd:
        return out
    for order in ("cf", "ca"):
        for ones in (True, False):
            if ones and nd * 3 < n:   # every token carries a count: about half the input is digits
                continue
            # res[i] = up to `cap` (text, counts-seen) decodes of t[i:]
            res = [None] * (n + 1)
            res[n] = [("", 0)]
            for i in range(n - 1, -1, -1):
                acc = []
                chars = [(t[i], 1)] + ([(t[i + 1], 2)] if t[i] == "\\" and i + 1 < n else [])
                cnts = [(int(t[i:i + k]), k) for k in (1, 2) if i + k <= n and t[i:i + k].isdigit() and t[i] != "0"]
                if order == "cf":
                    opts = [(c, k, ch, w) for c, k in cnts if i + k < n for ch, w in
                            ([(t[i + k], 1)] + ([(t[i + k + 1], 2)] if t[i + k] == "\\" and i + k + 1 < n else []))]
                    toks = [(i + k + w, ch * c, 1) for c, k, ch, w in opts if ones or c >= 2]
                    if not ones:
                        toks += [(i + w, ch, 0) for ch, w in chars]
                else:
                    toks = []
                    for ch, w in chars:
                        j = i + w
                        for k in (1, 2):
                            if j + k <= n and t[j:j + k].isdigit() and t[j] != "0" and (ones or int(t[j:j + k]) >= 2):
                                toks.append((j + k, ch * int(t[j:j + k]), 1))
                        if not ones:
                            toks.append((j, ch, 0))
                for j, piece, c in toks:
                    for rest, rc in res[j] or ():
                        acc.append((piece + rest, c + rc))
                        if len(acc) >= cap:
                            break
                    if len(acc) >= cap:
                        break
                res[i] = acc
            for s, c in res[0] or ():
                if c >= (2 if ones else 1) and s != t:
                    out.append(s)
    return list(dict.fromkeys(out))


def rle_dec(t):
    return _tc_best(rle_reads(t.strip()))


_LZ77_TUP = re.compile(r"[(\[<{]\s*(\d+)\s*[,;]\s*(\d+)\s*(?:[,;]\s?(?:'(\\.|.)'|\"(\\.|.)\"|(None|null|nil|NULL|EOF|''|\"\"|\\0)|([^\s)\]>}]))|[,;]( ))?\s*[)\]>}]")


def _tc_unesc(c):
    if len(c) == 2 and c[0] == "\\":
        return {"n": "\n", "t": "\t", "s": " ", "0": ""}.get(c[1], c[1])
    return c


def lz77_enc(s, window=255, fmt="({o},{l},{c})", sep=""):
    """Greedy LZ77 (offset = distance back, longest match, the next literal always emitted)."""
    out, i = [], 0
    while i < len(s):
        bo = bl = 0
        for o in range(1, min(i, window) + 1):
            k = 0
            while i + k < len(s) - 1 and s[i - o + k] == s[i + k]:
                k += 1
            if k > bl:
                bo, bl = o, k
        out.append(fmt.format(o=bo, l=bl, c=s[i + bl]))
        i += bl + 1
    return sep.join(out)


def lz77_reads(t):
    t = t.strip()
    toks, pos = [], 0
    for m in _LZ77_TUP.finditer(t):
        if t[pos:m.start()].strip(" \t\r\n,;[]"):
            return []
        q = m.group(3) or m.group(4) or m.group(6) or m.group(7)
        toks.append((int(m.group(1)), int(m.group(2)), _tc_unesc(q) if q else ""))
        pos = m.end()
    if len(toks) < 2 or t[pos:].strip(" \t\r\n,;[]"):
        return []
    out = []
    for swap in (False, True):
        buf = []
        try:
            for a, b, c in toks:
                o, ln = (b, a) if swap else (a, b)
                if ln and not 1 <= o <= len(buf) or len(buf) + ln > 8000:
                    raise ValueError
                for _ in range(ln):
                    buf.append(buf[-o])
                buf.append(c)
        except (ValueError, IndexError):
            continue
        out.append("".join(buf))
    return list(dict.fromkeys(out))


def lz77_dec(t):
    return _tc_best(lz77_reads(t))


def lzw_enc(s, first=256, clear=False, sep=", ", brackets=True):
    """Classic LZW over a 256-char dict -> decimal code list ('[78, 105, ..., 256, ...]'); clear=True: 256 clear,
    257 end, first free code 258."""
    if clear:
        first = 258
    d = {chr(i): i for i in range(min(first, 256))}
    nxt, w, out = first, "", [256] if clear else []
    for ch in s:
        if w + ch in d:
            w += ch
        else:
            out.append(d[w])
            d[w + ch] = nxt
            nxt += 1
            w = ch
    if w:
        out.append(d[w])
    if clear:
        out.append(257)
    body = sep.join(map(str, out))
    return "[" + body + "]" if brackets else body


_LZW_LIST = re.compile(r"[\[({]?\s*\d+(?:\s*[,;\s]\s*\d+)+\s*[\])}]?")


def lzw_reads(t):
    t = t.strip()
    if not _LZW_LIST.fullmatch(t):
        return []
    codes = [int(x) for x in re.findall(r"\d+", t)]
    out = []
    for first, clear, end in ((256, None, None), (258, 256, 257), (128, None, None)):
        base = min(first, 256) if clear is None else 256
        if max(codes) < first or len(codes) > 20000:
            continue
        d, prev, buf, ok = {}, None, [], True
        for c in codes:
            if c == clear:
                d, prev = {}, None
                continue
            if c == end:
                break
            if c < base:
                e = chr(c)
            elif c in d:
                e = d[c]
            elif c == first + len(d) and prev is not None:
                e = prev + prev[0]
            else:
                ok = False
                break
            if prev is not None:
                d[first + len(d)] = prev + e[0]
            buf.append(e)
            prev = e
        if ok and buf:
            out.append("".join(buf))
    return list(dict.fromkeys(out))


def lzw_dec(t):
    return _tc_best(lzw_reads(t))


_HUF_Q = r"""(?:'((?:\\.|[^'\\]){1,6})'|"((?:\\.|[^"\\]){1,6})")"""
_HUF_C2B = re.compile(_HUF_Q + r"""\s*[:=]\s*['"]?([01]{1,24})\b['"]?""")
_HUF_B2C = re.compile(r"""['"]([01]{1,24})['"]\s*[:=]\s*""" + _HUF_Q)
_HUF_TUP = re.compile(_HUF_Q + r"\s*:\s*[(\[]\s*(\d{1,2})\s*,\s*(\d{1,7})\s*[)\]]")
_HUF_BARE = re.compile(r"(?:(?<=[\s,{])|^)([^\s,{}'\"])\s*[:=]\s*([01]{1,24})(?=[\s,}]|$)")
_HUF_NAMES = {"space": " ", "sp": " ", "␣": " ", "nl": "\n", "newline": "\n", "\\s": " "}


def _huf_char(c):
    c = _HUF_NAMES.get(c.lower(), c) if len(c) > 1 else c
    if len(c) > 1 and c.startswith("\\"):
        try:
            c = codecs.decode(c, "unicode_escape")
        except (UnicodeDecodeError, ValueError):
            return None
    return c if len(c) == 1 else None


def huffman_reads(t):
    """A '{char: bits}' (or '{bits: char}' / dahuffman '{char: (nbits, value)}') table + the longest bit run outside it."""
    t = t.strip()
    if len(t) > 20000:
        return []
    table, spans = {}, []
    for rx, kind in ((_HUF_C2B, 0), (_HUF_B2C, 1), (_HUF_TUP, 2), (_HUF_BARE, 3)):
        ms = list(rx.finditer(t))
        if len(ms) < 2:
            continue
        for m in ms:
            g = m.groups()
            if kind == 0:
                ch, bits = _huf_char(g[0] or g[1]), g[2]
            elif kind == 1:
                ch, bits = _huf_char(g[1] or g[2]), g[0]
            elif kind == 2:
                ch, bits = _huf_char(g[0] or g[1]), format(int(g[3]), f"0{int(g[2])}b")
                if len(bits) != int(g[2]):
                    ch = None
            else:
                ch, bits = _huf_char(g[0]), g[1]
            if ch is None or table.get(bits, ch) != ch:
                return []
            table[bits] = ch
            spans.append(m.span())
        break
    if len(table) < 2:
        return []
    codes = sorted(table)
    if any(b.startswith(a) for a, b in zip(codes, codes[1:])):
        return []   # not prefix-free
    lo, hi = min(s for s, _e in spans), max(e for _s, e in spans)
    rest = t[:lo] + " " + t[hi:]
    runs = [re.sub(r"\s", "", m.group()) for m in re.finditer(r"[01](?:[01 ]*[01])?", rest)]
    bits = max(runs, key=len, default="")
    if len(bits) < 4:
        return []
    out, cur = [], ""
    for b in bits:
        cur += b
        if cur in table:
            out.append(table[cur])
            cur = ""
    if cur and (len(cur) >= 8 or not any(c.startswith(cur) for c in codes)):
        return []   # leftover = byte padding only
    return ["".join(out)] if out else []


def huffman_dec(t):
    return _tc_best(huffman_reads(t))


_TC_READERS = (("rle", rle_reads), ("lz77", lz77_reads), ("lzw", lzw_reads), ("huffman", huffman_reads))


def textcomp_reads(t):
    """[(family, text)] of every text-level compression reading of `t`."""
    out = []
    for name, fn in _TC_READERS:
        try:
            out += [(name, s) for s in fn(t)]
        except Exception:   # noqa: BLE001
            continue
    return out


def textcomp_dec(t):
    try:
        return _tc_best([s for _n, s in textcomp_reads(t)])
    except Exception:   # noqa: BLE001
        return None


def textcomp_free(p):
    """Speculative Mastery-line decoder: a text-compression reading that is a piece of the warmups sentence."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return list(dict.fromkeys(lead + s for _n, s in textcomp_reads(p) if _tc_piece(s)))[:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES += [(f"rle-{o}", (lambda o: lambda s: rle_enc(s, o))(o), rle_dec) for o in ("cf", "ca")]
CANDIDATES += [("lz77-tuples", lz77_enc, lz77_dec), ("lz77-tuples-spaced", lambda s: lz77_enc(s, sep=" "), lz77_dec),
               ("lzw-codes", lzw_enc, lzw_dec), ("lzw-codes-clear", lambda s: lzw_enc(s, clear=True), lzw_dec),
               ("huffman-table", lambda s: None, huffman_dec)]

# yEnc and BinHex 4.0: retro binary-to-text wrappers. yEnc body = (byte + 42) % 256 as Latin-1 chars, critical chars
# (NUL LF CR =) and edge TAB/space escaped as '=' + (c + 64), framed by `=ybegin ... name=` / optional `=ypart` /
# `=yend size= crc32=` (size and CRC-32 checked when present). BinHex 4.0 (.hqx): optional banner
# `(This file must be converted with BinHex 4.0)`, then `:...:` over a 64-char 6-bit alphabet, RLE90 (0x90 n), and a
# header (name, type, creator, flags, data/rsrc lengths) + data fork + resource fork, each CRC-16/XMODEM checked
# (binascii.a2b_hqx is gone in 3.11+). Both decoders return the data fork as text, never raise, and refuse a bad CRC.
_HQX = "!\"#$%&'()*+,-012345689@ABCDEFGHIJKLMNPQRSTUVXYZ[`abcdefhijklmpqr"
_UNHQX = {c: i for i, c in enumerate(_HQX)}
_HQX_BANNER = "(This file must be converted with BinHex 4.0)"


def yenc_enc(s, name="data.txt", line=128, frame=True):
    b = _u(s)
    rows, cur = [], []
    for i, x in enumerate(b):
        c = (x + 42) % 256
        edge = not cur or i == len(b) - 1 or len(cur) >= line - 1
        if c in (0, 10, 13, 61) or (edge and c in (9, 32)) or (not cur and c == 46):
            cur += ["=", chr(c + 64 & 255)]
        else:
            cur.append(chr(c))
        if len(cur) >= line:
            rows.append("".join(cur))
            cur = []
    if cur:
        rows.append("".join(cur))
    if not frame:
        return "\n".join(rows)
    return "\r\n".join([f"=ybegin line={line} size={len(b)} name={name}", *rows,
                        f"=yend size={len(b)} crc32={zlib.crc32(b):08x}", ""])


def _ykv(ln):
    kv = {}
    head, _s, name = ln.partition(" name=")
    for m in re.finditer(r"(\w+)=(\S*)", head):
        kv[m.group(1)] = m.group(2)
    if _s:
        kv["name"] = name.strip()
    return kv


def yenc_bytes(t, bare=True):
    """Decoded bytes of a yEnc article (framed, or a bare body when `bare` and it has high chars), else None."""
    if not isinstance(t, str) or not t.strip() or any(ord(c) > 255 for c in t):
        return None
    lines = re.split(r"\r\n|\n|\r", t)
    begin = next((i for i, ln in enumerate(lines) if ln.startswith("=ybegin ")), None)
    head, part, end = {}, {}, {}
    if begin is None:
        if not bare or "=y" in t or not any(ord(c) >= 0x80 for c in t):
            return None
        body = [ln for ln in t.strip().splitlines() if ln]
    else:
        head, body = _ykv(lines[begin]), []
        for ln in lines[begin + 1:]:
            if ln.startswith("=ypart "):
                part = _ykv(ln)
            elif ln.startswith("=yend"):
                end = _ykv(ln)
                break
            elif ln:
                body.append(ln)
    out = bytearray()
    for ln in body:
        it = iter(ln)
        for c in it:
            if c == "=":
                c = next(it, None)
                if c is None:
                    return None
                out.append((ord(c) - 106) % 256)
            else:
                out.append((ord(c) - 42) % 256)
    try:
        size = end.get("size") or (head.get("size") if not part else None)
        if size is not None and int(size) != len(out):
            return None
        crc = end.get("pcrc32") if part else end.get("crc32")
        if crc and int(crc, 16) != zlib.crc32(out):
            return None
    except ValueError:
        return None
    return bytes(out) if out else None


def yenc_dec(t, bare=True):
    try:
        b = yenc_bytes(t, bare)
        s = _t(b) if b else None
        return s if s and (s.isprintable() or _texty(s) >= 0.9) else None
    except (UnicodeDecodeError, ValueError, TypeError):
        return None


def _rle90(b):
    out, i = bytearray(), 0
    while i < len(b):
        c, n = b[i], 1
        if c == 0x90:
            out += b"\x90\x00"
        else:
            while i + n < len(b) and b[i + n] == c and n < 255:
                n += 1
            out += bytes([c, 0x90, n]) if n > 3 else bytes([c])
            n = 1 if n <= 3 else n
        i += n
    return bytes(out)


def _unrle90(b):
    out, i = bytearray(), 0
    while i < len(b):
        if b[i] != 0x90:
            out.append(b[i])
            i += 1
            continue
        if i + 1 >= len(b):
            return None
        n = b[i + 1]
        if n == 0:
            out.append(0x90)
        elif not out:
            return None
        else:
            out += bytes([out[-1]]) * (n - 1)
        i += 2
    return bytes(out)


def binhex_enc(s, name="data.txt", ftype=b"TEXT", creator=b"????", eol="\r"):
    """BinHex 4.0 file laid out like CPython <=3.10 binhex.binhex(): banner, ':' + 63 chars, 64-char lines, ':'."""
    data, nm = _u(s), _u(name)
    hdr = bytes([len(nm)]) + nm + b"\0" + ftype + creator + b"\0\0" + len(data).to_bytes(4, "big") + bytes(4)
    raw = b"".join(x + binascii.crc_hqx(x, 0).to_bytes(2, "big") for x in (hdr, data, b""))
    r = _rle90(raw)
    acc = nb = 0
    chars = []
    for x in r:
        acc, nb = acc << 8 | x, nb + 8
        while nb >= 6:
            nb -= 6
            chars.append(_HQX[acc >> nb & 63])
    if nb:
        chars.append(_HQX[acc << (6 - nb) & 63])
    h = "".join(chars)
    rows, first = [], 0
    while len(h) - first >= (63 if not rows else 64):
        n = 63 if not rows else 64
        rows.append(h[first:first + n])
        first += n
    rows.append(h[first:] + ":")
    return _HQX_BANNER + eol + eol + ":" + eol.join(rows) + eol


def binhex_parse(t):
    """{name, type, creator, flags, data, rsrc} of a BinHex 4.0 text (banner optional), None unless every CRC holds."""
    if not isinstance(t, str):
        return None
    m = t.find(_HQX_BANNER)
    s = t[m + len(_HQX_BANNER):] if m >= 0 else t.strip()
    i = s.find(":")
    j = s.find(":", i + 1)
    if i < 0 or j < 0 or (m < 0 and (i or j != len(s) - 1)):
        return None
    body = re.sub(r"\s", "", s[i + 1:j])
    if len(body) < 30 or any(c not in _UNHQX for c in body):
        return None
    acc = nb = 0
    raw = bytearray()
    for c in body:
        acc, nb = (acc << 6 | _UNHQX[c]) & 0xFFFF, nb + 6
        if nb >= 8:
            nb -= 8
            raw.append(acc >> nb & 255)
    b = _unrle90(bytes(raw))
    if not b:
        return None
    nl = b[0]
    h = nl + 20
    if not 1 <= nl <= 63 or len(b) < h + 2 or b[nl + 1] != 0:
        return None
    if binascii.crc_hqx(b[:h], 0) != int.from_bytes(b[h:h + 2], "big"):
        return None
    dlen, rlen = int.from_bytes(b[nl + 12:nl + 16], "big"), int.from_bytes(b[nl + 16:nl + 20], "big")
    d0, r0 = h + 2, h + 4 + dlen
    data, rsrc = b[d0:d0 + dlen], b[r0:r0 + rlen]
    if len(b) < r0 or binascii.crc_hqx(data, 0) != int.from_bytes(b[d0 + dlen:r0], "big"):
        return None
    if len(b) >= r0 + rlen + 2 and binascii.crc_hqx(rsrc, 0) != int.from_bytes(b[r0 + rlen:r0 + rlen + 2], "big"):
        return None
    return {"name": b[1:1 + nl].decode("latin-1"), "type": b[nl + 2:nl + 6].decode("latin-1"),
            "creator": b[nl + 6:nl + 10].decode("latin-1"), "flags": int.from_bytes(b[nl + 10:nl + 12], "big"),
            "data": data, "rsrc": rsrc}


def binhex_dec(t):
    try:
        r = binhex_parse(t)
        s = _t(r["data"]) if r and r["data"] else None
        return s if s and (s.isprintable() or _texty(s) >= 0.9) else None
    except (UnicodeDecodeError, ValueError, TypeError, IndexError):
        return None


def retro_free(p):
    """Speculative Mastery-line decoder: a one-line BinHex `:...:` or bare/framed yEnc reading of a sentence piece."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        reads = (binhex_dec(p), yenc_dec(p))
        return list(dict.fromkeys(lead + s for s in reads if s and _tc_piece(s)))[:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES += [("yenc", yenc_enc, lambda t: yenc_dec(t, bare=False)),
               ("yenc-bare", lambda s: yenc_enc(s, frame=False), yenc_dec),
               ("binhex4", binhex_enc, binhex_dec),
               ("binhex4-lf", lambda s: binhex_enc(s, eol="\n"), binhex_dec)]


# ------------------------------------------- base85 variant sweep (speculative, coverage atlas target base85-variant-sweep)
# D23 = Adobe Ascii85 '<~...~>' ("The alphabet got bigger"). The lane turns one knob a day, so read every 85-char
# family: Adobe with a lost / half delimiter, bare a85 ('z' = 4 NULs, 'y' = 4 spaces btoa-style), wrapped lines, btoa
# ('xbtoa Begin' .. 'xbtoa End N <len> ...', whole zero-padded groups trimmed to N), RFC 1924 / git / Python b85, Z85
# (translated index-for-index onto the b85 alphabet, partial last group ok, <= 3 NUL pad dropped), IPv6 RFC 1924 (one
# 20-char token = a 128-bit big-endian integer -> 16 bytes; non-text -> the IPv6 address). Each byte reading is then
# tried as text, a magic-sniffed squeeze (_dz_inflate), UTF-16, and decode_chunk (hex / base64 inner). Never raises.
_BTOA = re.compile(r"xbtoa Begin[^\n]*\n(.*?)\n\s*xbtoa End(?:\s+N\s+(\d+))?", re.S)
_A85_SET = frozenset(map(chr, range(33, 118))) | {"z", "y"}
_B85_SET, _Z85_SET = frozenset(_B85_ABC), frozenset(_Z85_ABC)
_UNB85 = {c: i for i, c in enumerate(_B85_ABC)}


def ipv6_1924_dec(tok):
    """RFC 1924 compact IPv6: 20 base-85 digits (b85 alphabet) of one 128-bit integer -> 16 bytes."""
    if len(tok) != 20 or not all(c in _UNB85 for c in tok):
        raise ValueError("not rfc1924")
    v = 0
    for c in tok:
        v = v * 85 + _UNB85[c]
    if v >> 128:
        raise ValueError("rfc1924 out of range")
    return v.to_bytes(16, "big")


def btoa_enc(s, width=78):
    """btoa 4.x: whole zero-padded groups ('z' / 'y'), 78-col lines, trailer with N and the E/S/R checksums."""
    b = _u(s)
    body = base64.a85encode(b + b"\0" * (-len(b) % 4), foldspaces=True).decode()
    e = sm = r = 0
    for c in b:
        e ^= c
        sm = (sm + c + 1) & 0xFFFFFFFF
        r = ((r << 1 | r >> 31) + c) & 0xFFFFFFFF
    lines = [body[i:i + width] for i in range(0, len(body), width)]
    return "xbtoa Begin\n" + "\n".join(lines) + f"\nxbtoa End N {len(b)} {len(b):x} E {e:x} S {sm:x} R {r:x}\n"


def b85_reads(t):
    """[(name, bytes)] for every 85-char family `t` strictly parses as."""
    if isinstance(t, (bytes, bytearray)):
        try:
            t = bytes(t).decode("ascii")
        except UnicodeDecodeError:
            return []
    s = t.strip() if isinstance(t, str) else ""
    if not s or len(s) > 400000:
        return []
    out = []

    def add(name, fn):
        try:
            b = fn()
        except (ValueError, TypeError, OverflowError):
            return
        if b:
            out.append((name, b))
    m = _BTOA.search(s)
    if m:
        body, n = re.sub(r"\s+", "", m.group(1)), m.group(2)
        add("btoa", lambda: base64.a85decode(body, foldspaces=True)[:int(n) if n else None])
        return out
    flat = re.sub(r"\s+", "", s)
    if flat.startswith("<~") or flat.endswith("~>"):
        core = flat[2:] if flat.startswith("<~") else flat
        core = core[:-2] if core.endswith("~>") else core
        add("ascii85-adobe", lambda: base64.a85decode("<~" + core + "~>", adobe=True))
        if "y" in core:
            add("ascii85-adobe-y", lambda: base64.a85decode(core, foldspaces=True))
        return out
    if all(c in _A85_SET for c in flat) and len(flat.replace("z", "").replace("y", "")) % 5 != 1:
        add("ascii85", lambda: base64.a85decode(flat))
        if "y" in flat:
            add("ascii85-y", lambda: base64.a85decode(flat, foldspaces=True))
    if len(flat) == 20:
        add("ipv6-rfc1924", lambda: ipv6_1924_dec(flat))
    if all(c in _B85_SET for c in flat) and len(flat) % 5 != 1:
        add("base85", lambda: base64.b85decode(flat))
    if all(c in _Z85_SET for c in flat) and len(flat) % 5 != 1:
        add("z85", lambda: base64.b85decode(flat.translate(_Z85_TO_B85)))
    return out


def _b85_texts(b):
    """[(inner, text)] for one decoded byte string: printable text, a sniffed squeeze, UTF-16, then decode_chunk."""
    k = len(b) - len(b.rstrip(b"\0"))
    s = _txt(b[:len(b) - k] if 0 < k <= 3 else b)
    out = [("", s)] if s else []
    if not s and len(b) >= 6:
        out += [(kind, x) for kind, data in _dz_inflate(b) for x in (_dz_text(data),) if x]
    if not s and len(b) >= 4 and len(b) % 2 == 0:
        enc = ("utf-16" if b[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-16-le" if not any(b[1::2]) else
               "utf-16-be" if not any(b[0::2]) else None)
        try:
            x = b.decode(enc) if enc else None
        except UnicodeDecodeError:
            x = None
        if x and x.isprintable():
            out.append((enc, x))
    from lib.decode import decode_chunk
    for name, x in list(out):
        if not SLUG.search(x) and (" " not in x.strip() or re.fullmatch(r"[0-9A-Fa-f\s]+", x)):
            p = safe(decode_chunk, x)
            if p and p != x and p.isprintable() and _texty(p) >= 0.85:
                out.append((name + "+chunk", p))
    return out


def b85_any_reads(t):
    """[(name, text)] for every 85-char family x inner-layer reading of `t`. Never raises."""
    try:
        reads = []
        for n, b in b85_reads(t):
            texts = _b85_texts(b)
            reads += [(n + (f"[{i}]" if i else ""), x) for i, x in texts]
            if not texts and n == "ipv6-rfc1924":
                import ipaddress
                reads.append((n, str(ipaddress.IPv6Address(b))))
        return reads
    except Exception:   # noqa: BLE001 -- a decoy never raises past the decoder
        return []


def b85_any(t, gate=SLUG):
    """The slug-gated (else the first texty / IPv6) reading of a whole blob under any 85-char family, else None."""
    reads = b85_any_reads(t)
    hit = next((x for _n, x in reads if gate is not None and gate.search(x)), None)
    return hit or next((x for n, x in reads if _texty(x) >= 0.85 or n == "ipv6-rfc1924"), None)


def b85_free(p):
    """Speculative Mastery-line decoder: one 85-char token (own delimiters / btoa frame) that reads as a sentence piece."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead, s = p[:len(p) - len(p.lstrip())], p.strip()
        if " " in s and not _BTOA.search(s):
            return []
        return list(dict.fromkeys(lead + x for _n, x in b85_any_reads(s) if _tc_piece(x)))[:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES += [("base85-any", lambda s: None, b85_any),
               ("ascii85-btoa", btoa_enc, b85_any),
               ("ascii85-y", lambda s: base64.a85encode(_u(s), foldspaces=True).decode(), b85_any),
               ("ascii85-adobe-wrap75", lambda s: base64.a85encode(_u(s), adobe=True, wrapcol=75).decode(), b85_any),
               ("ascii85-adobe-open", lambda s: base64.a85encode(_u(s), adobe=True).decode()[:-2], b85_any),
               ("ascii85-adobe-hex", lambda s: base64.a85encode(_u(s).hex().encode(), adobe=True).decode(), b85_any),
               ("base85-hex", lambda s: base64.b85encode(_u(s).hex().encode()).decode(), b85_any),
               ("ascii85-zlib", lambda s: base64.a85encode(zlib.compress(_u(s), 9)).decode(), b85_any)]


# ---------------------------------- serialization wrappers (speculative, coverage atlas target serialization-wrappers)
# "Wrapper / package / pickled / marshalled" read literally: the sentence is a string value inside a serialized object
# -- Python pickle (protocol 0-5) and marshal, msgpack, CBOR, BSON, protobuf wire, PHP serialize() (raw text or under
# base64 / hex) and Java ObjectOutputStream (aced0005). NEVER deserializes: tiny strict walkers pull the string /
# bytes values out (a stream that doesn't parse to its exact end reads as nothing); Java is a magic-gated scan of its
# TC_STRING / TC_LONGSTRING records. (.NET BinaryFormatter: no offline writer for a fixture -- not built.)
# ser_strings(t) -> [(form, [bytes])]. Never raises.
_SER_DEPTH = 48
_PK_FIX = dict.fromkeys(b"(.012NRabd}el]ost)uQ\x81\x85\x86\x87\x88\x89\x8f\x90\x91\x92\x93\x94\x97\x98", 0)
_PK_FIX.update(dict.fromkeys(b"\x80Khq\x82", 1))
_PK_FIX.update(dict.fromkeys(b"M\x83", 2))
_PK_FIX.update(dict.fromkeys(b"Jjr\x84", 4))
_PK_FIX.update(dict.fromkeys(b"G\x95", 8))
_PK_LEN = {0x55: (1, 1), 0x43: (1, 1), 0x8c: (1, 1), 0x8a: (1, 0), 0x54: (4, 1), 0x42: (4, 1), 0x58: (4, 1),
           0x8b: (4, 0), 0x8d: (8, 1), 0x8e: (8, 1), 0x96: (8, 1)}   # opcode -> (length width, is a string value)


def _ser_pickle(b):
    """Pickle opcode walk (pickletools' arg table, nothing executed): string / bytes args up to STOP, else None."""
    i, n, out = 0, len(b), []
    while i < n:
        op = b[i]
        i += 1
        if op in _PK_FIX:
            if op == 0x2e:   # STOP
                return out if not b[i:].strip(b"\x00\r\n") else None
            i += _PK_FIX[op]
        elif op in b"ILFSVgpPci":   # newline-terminated args (GLOBAL / INST: two lines)
            for _ in range(2 if op in b"ci" else 1):
                j = b.find(b"\n", i)
                if j < 0:
                    return None
                arg, i = b[i:j], j + 1
            if op == 0x56:   # UNICODE
                out.append(arg.decode("raw_unicode_escape").encode("utf-8", "surrogatepass"))
            elif op == 0x53:   # STRING: a repr
                if len(arg) < 2 or arg[:1] not in b"'\"" or arg[-1:] != arg[:1]:
                    return None
                out.append(codecs.escape_decode(arg[1:-1])[0])
        elif op in _PK_LEN:
            w, keep = _PK_LEN[op]
            if i + w > n:
                return None
            L = int.from_bytes(b[i:i + w], "little", signed=w == 4 and op in (0x54, 0x8b))
            i += w
            if L < 0 or i + L > n:
                return None
            if keep:
                out.append(b[i:i + L])
            i += L
        else:
            return None
    return None


def _ser_marshal(b):
    """Python marshal walk of a non-code object tree; a code object / .pyc falls back to a scan of its string
    records. Values only (dict keys skipped)."""
    n, out, pos = len(b), [], [0]

    def take(k):
        j = pos[0]
        if k < 0 or j + k > n:
            raise ValueError
        pos[0] = j + k
        return b[j:j + k]

    def u32():
        return int.from_bytes(take(4), "little", signed=True)

    def rd(d, keep=True):
        if d > _SER_DEPTH:
            raise ValueError
        t = take(1)[0] & 0x7f
        if t in b"NTFS.":
            return
        if t in b"ir":
            take(4)
        elif t == 0x6c:   # long: digit count, 15-bit digits
            take(2 * abs(u32()))
        elif t in b"gy":
            take(8 if t == 0x67 else 16)
        elif t in b"fx":
            for _ in range(1 if t == 0x66 else 2):
                take(take(1)[0])
        elif t in b"zZ":
            s = take(take(1)[0])
            if keep:
                out.append(s)
        elif t in b"suatA":
            s = take(u32())
            if keep:
                out.append(s)
        elif t in b"([<>)":
            for _ in range(take(1)[0] if t == 0x29 else u32()):
                rd(d + 1)
        elif t == 0x7b:
            while True:
                if pos[0] < n and b[pos[0]] == 0x30:
                    pos[0] += 1
                    break
                rd(d + 1, False)
                rd(d + 1)
        else:
            raise ValueError
    try:
        rd(0)
        return out if pos[0] == n else None
    except (ValueError, IndexError, RecursionError):
        pass
    if not (b[:1] in (b"c", b"\xe3") or b[2:4] == b"\r\n" and b[16:17] in (b"c", b"\xe3")):
        return None
    out, i = [], 0
    while i < n - 1:
        t = b[i] & 0x7f
        L, h = (b[i + 1], 2) if t in b"zZ" else (int.from_bytes(b[i + 1:i + 5], "little"), 5) if t in b"uatA" else (0, 0)
        s = b[i + h:i + h + L] if h and 0 < L <= n - i - h else None
        if s is not None and _dz_text(s) is not None:
            out.append(s)
            i += h + L
        else:
            i += 1
    return out or None


def _ser_msgpack(b):
    n, out = len(b), []

    def rd(i, d, keep=True):
        if d > _SER_DEPTH or i >= n:
            raise ValueError
        t = b[i]
        i += 1
        if t <= 0x7f or t >= 0xe0 or t in (0xc0, 0xc2, 0xc3):
            return i
        if t <= 0x9f:   # fixmap / fixarray
            for k in range((t & 15) * 2 if t <= 0x8f else t & 15):
                i = rd(i, d + 1, not (t <= 0x8f and k % 2 == 0))
            return i
        fix = {0xca: 4, 0xcb: 8, 0xcc: 1, 0xcd: 2, 0xce: 4, 0xcf: 8, 0xd0: 1, 0xd1: 2, 0xd2: 4, 0xd3: 8,
               0xd4: 2, 0xd5: 3, 0xd6: 5, 0xd7: 9, 0xd8: 17}
        if t in fix:
            if i + fix[t] > n:
                raise ValueError
            return i + fix[t]
        if t <= 0xbf or t in (0xc4, 0xc5, 0xc6, 0xd9, 0xda, 0xdb, 0xc7, 0xc8, 0xc9):
            if t <= 0xbf:
                L = t & 31
            else:
                w = {0xc4: 1, 0xd9: 1, 0xc7: 1, 0xc5: 2, 0xda: 2, 0xc8: 2}.get(t, 4)
                L, i = int.from_bytes(b[i:i + w], "big"), i + w
                i += t in (0xc7, 0xc8, 0xc9)   # ext type byte
            if i + L > n:
                raise ValueError
            if keep and t not in (0xc7, 0xc8, 0xc9):
                out.append(b[i:i + L])
            return i + L
        if t in (0xdc, 0xdd, 0xde, 0xdf):
            w = 2 if t in (0xdc, 0xde) else 4
            if i + w > n:
                raise ValueError
            c, i = int.from_bytes(b[i:i + w], "big"), i + w
            if c > n:
                raise ValueError
            for k in range(c * 2 if t >= 0xde else c):
                i = rd(i, d + 1, not (t >= 0xde and k % 2 == 0))
            return i
        raise ValueError   # 0xc1 never used
    try:
        return out if n > 1 and rd(0, 0) == n else None
    except (ValueError, IndexError, RecursionError):
        return None


def _ser_cbor(b):
    n, out = len(b), []

    def arg(i, ai):
        if ai < 24:
            return ai, i
        if ai > 27 or i + (1 << (ai - 24)) > n:
            raise ValueError
        w = 1 << (ai - 24)
        return int.from_bytes(b[i:i + w], "big"), i + w

    def rd(i, d, keep=True):
        if d > _SER_DEPTH or i >= n:
            raise ValueError
        mt, ai = b[i] >> 5, b[i] & 31
        i += 1
        if ai == 31:   # indefinite length
            if mt in (2, 3):
                parts = []
                while b[i] != 0xff:
                    if b[i] >> 5 != mt or b[i] & 31 == 31:
                        raise ValueError
                    L, i = arg(i + 1, b[i] & 31)
                    parts.append(b[i:i + L])
                    i += L
                if keep:
                    out.append(b"".join(parts))
                return i + 1
            if mt in (4, 5):
                k = 0
                while b[i] != 0xff:
                    i = rd(i, d + 1, not (mt == 5 and k % 2 == 0))
                    k += 1
                return i + 1
            raise ValueError
        v, i = arg(i, ai)
        if mt in (0, 1, 7):
            return i
        if mt in (2, 3):
            if i + v > n:
                raise ValueError
            if keep:
                out.append(b[i:i + v])
            return i + v
        if mt in (4, 5):
            if v > n:
                raise ValueError
            for k in range(v * 2 if mt == 5 else v):
                i = rd(i, d + 1, not (mt == 5 and k % 2 == 0))
            return i
        return rd(i, d + 1, keep)   # tag
    try:
        b = b[3:] if b[:3] == b"\xd9\xd9\xf7" else b   # self-described CBOR tag 55799
        return out if n > 1 and b[:1] != b"\xff" and rd(0, 0) == len(b) else None
    except (ValueError, IndexError, RecursionError):
        return None


_BSON_FIX = {0x01: 8, 0x07: 12, 0x08: 1, 0x09: 8, 0x0c: 12, 0x10: 4, 0x11: 8, 0x12: 8, 0x13: 16}


def _ser_bson(b):
    n, out = len(b), []

    def doc(i, d):
        if d > _SER_DEPTH or i + 5 > n:
            raise ValueError
        L = int.from_bytes(b[i:i + 4], "little")
        end = i + L
        if L < 5 or end > n or b[end - 1] != 0:
            raise ValueError
        i += 4
        while i < end - 1:
            t = b[i]
            j = b.index(b"\x00", i + 1)
            i = j + 1
            if t in (0x02, 0x0d, 0x0e):
                k = int.from_bytes(b[i:i + 4], "little")
                if k < 1 or i + 4 + k > end or b[i + 3 + k] != 0:
                    raise ValueError
                out.append(b[i + 4:i + 3 + k])
                i += 4 + k
            elif t in (0x03, 0x04):
                i = doc(i, d + 1)
            elif t == 0x05:
                k = int.from_bytes(b[i:i + 4], "little")
                out.append(b[i + 5:i + 5 + k])
                i += 5 + k
            elif t == 0x0b:
                i = b.index(b"\x00", b.index(b"\x00", i) + 1) + 1
            elif t == 0x0f:
                i += int.from_bytes(b[i:i + 4], "little")
            elif t in _BSON_FIX:
                if t == 0x0c:   # DBPointer: string + ObjectId
                    i += 4 + int.from_bytes(b[i:i + 4], "little")
                i += _BSON_FIX[t]
            elif t not in (0x06, 0x0a, 0xff, 0x7f):
                raise ValueError
        if i != end - 1:
            raise ValueError
        return end
    try:
        return out if doc(0, 0) == n else None
    except (ValueError, IndexError, RecursionError):
        return None


def _ser_proto(b, d=0):
    """Protobuf wire walk: a length-delimited field is printable text, else a nested message, else raw bytes."""
    if d > 12:
        return None
    i, n, out = 0, len(b), []

    def varint():
        nonlocal i
        v = s = 0
        while True:
            if i >= n or s > 63:
                raise ValueError
            c = b[i]
            i += 1
            v |= (c & 0x7f) << s
            s += 7
            if c < 0x80:
                return v
    try:
        while i < n:
            tag = varint()
            wt = tag & 7
            if tag >> 3 < 1 or tag >> 3 > 536870911:
                return None
            if wt == 0:
                varint()
            elif wt in (1, 5):
                i += 8 if wt == 1 else 4
            elif wt == 2:
                L = varint()
                if i + L > n:
                    return None
                p = b[i:i + L]
                i += L
                sub = None if not p or p[0] >= 0x20 and _dz_text(p) is not None else _ser_proto(p, d + 1)
                out += sub if sub else [p]
            else:
                return None
        return out if i == n and out else None
    except (ValueError, IndexError):
        return None


def _ser_php(b):
    """PHP serialize() walk: N; b:/i:/d:..; s:N:"N bytes"; a:N:{..} O:N:"C":M:{..} C:N:"C":M:{M bytes} E:/r:/R:."""
    n, out = len(b), []

    def num(i, end):
        j = b.index(end, i)
        return b[i:j], j + 1

    def rd(i, d, keep=True):
        if d > _SER_DEPTH:
            raise ValueError
        t, c = b[i:i + 1], b[i + 1:i + 2]
        if t == b"N" and c == b";":
            return i + 2
        if c != b":":
            raise ValueError
        i += 2
        if t in (b"b", b"i", b"d", b"r", b"R"):
            v, i = num(i, b";")
            if not re.fullmatch(rb"-?(?:\d+(?:\.\d*)?(?:E[+-]?\d+)?|INF|NAN)", v):
                raise ValueError
            return i
        if t in (b"s", b"E", b"O", b"C"):
            v, i = num(i, b":")
            L = int(v)
            if b[i:i + 1] != b'"' or b[i + 1 + L:i + 3 + L] not in (b'";', b'":'):
                raise ValueError
            s, i = b[i + 1:i + 1 + L], i + 2 + L
            if t in (b"s", b"E"):
                if b[i:i + 1] != b";":
                    raise ValueError
                if keep:
                    out.append(s)
                return i + 1
            i += 1
        elif t != b"a":
            raise ValueError
        v, i = num(i, b":")
        k = int(v)
        if b[i:i + 1] != b"{":
            raise ValueError
        i += 1
        if t == b"C":
            if keep:
                out.append(b[i:i + k])
            i += k
        else:
            for _ in range(k):
                i = rd(rd(i, d + 1, False), d + 1, keep)
        if b[i:i + 1] != b"}":
            raise ValueError
        return i + 1
    try:
        return out if b[:1] in b"NbidsaOCE" and n > 3 and rd(0, 0) == len(b.rstrip(b"\r\n")) else None
    except (ValueError, IndexError, RecursionError):
        return None


def _ser_scan(b, magic, rec):
    """Magic-gated scan: every printable length-prefixed string record (`rec`(b, i) -> (start, length) | None)."""
    if not b.startswith(magic):
        return None
    out, i, n = [], len(magic), len(b)
    while i < n:
        r = rec(b, i)
        s = b[r[0]:r[0] + r[1]] if r and 0 < r[1] <= n - r[0] else None
        if s is not None and _dz_text(s) is not None:
            out.append(s)
            i = r[0] + r[1]
        else:
            i += 1
    return out or None


def _java_rec(b, i):
    if b[i] == 0x74:
        return i + 3, int.from_bytes(b[i + 1:i + 3], "big")
    if b[i] == 0x7c:
        return i + 9, int.from_bytes(b[i + 1:i + 9], "big")
    return None


_SER_FORMS = (
    ("pickle", _ser_pickle),
    ("java", lambda b: _ser_scan(b, b"\xac\xed\x00\x05", _java_rec)),
    ("php", _ser_php),
    ("bson", _ser_bson),
    ("marshal", _ser_marshal),
    ("msgpack", _ser_msgpack),
    ("cbor", _ser_cbor),
)


def _ser_try(fn, b):
    try:
        return fn(b)
    except Exception:   # noqa: BLE001 -- a walker that doesn't apply
        return None


def ser_strings(t):
    """[(form, [bytes])] for every serialized reading of `t` (raw bytes / text, base64 / hex / ...; also after one
    compressor): the string / bytes values in stream order. Protobuf only when no other format parses. Never raises."""
    out = []
    try:
        ws = list(_dz_wrappers(t))
        if isinstance(t, str) and t.strip():
            ws.append(("text", t.strip().encode("utf-8")))
        for wrapper, b in ws:
            if len(b) < 4 or len(b) > _ARC_MAX:
                continue
            for pre, x in [("", b)] + [(f"{k}+", y) for k, y in _dz_inflate(b)]:
                got = [(f"{pre}{form}-{wrapper}", v) for form, fn in _SER_FORMS for v in (_ser_try(fn, x),) if v]
                if not got and wrapper != "text":
                    got = [(f"{pre}protobuf-{wrapper}", v) for v in (_ser_try(_ser_proto, x),) if v]
                out += got
                if got:
                    break
    except Exception:   # noqa: BLE001
        return out
    return out


def _ser_texts(vals, deadline):
    """[candidate text]: each value (printable, inflated, nested codec), then the values joined."""
    outs = []
    for v in vals:
        outs += _arc_member_text(v, deadline) if time.monotonic() < deadline else [x for x in (_dz_text(v),) if x]
    texts = [x for x in (_dz_text(v) for v in vals) if x]
    if len(texts) > 1:
        outs += [" ".join(x.strip() for x in texts), "".join(texts)]
    return list(dict.fromkeys(x for x in outs if x))


def ser_solve(t):
    """(form, sentence) for the first serialized reading holding the slug in English (one value, a nested decode of
    a value, else the values joined); else None."""
    try:
        deadline = time.monotonic() + 0.6
        for form, vals in ser_strings(t):
            hits = [x for x in _ser_texts(vals, deadline) if SLUG.search(x) and _kbd_score(x) >= _RD_OK]
            if hits:
                return form, hits[0]
            for x in [y for y in (_dz_text(v) for v in vals) if y]:
                if time.monotonic() > deadline:
                    break
                rd = _rd_inner(x, 2, deadline)
                if rd:
                    return f"{form}[{rd[0]}]", rd[1]
    except Exception:   # noqa: BLE001
        return None
    return None


def ser_dec(t):
    r = ser_solve(t)
    return r[1] if r else None


def ser_free(p):
    """Speculative Mastery-line decoder: the English string value(s) of a one-line serialized blob."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        deadline = time.monotonic() + 0.3
        outs = []
        for _f, vals in ser_strings(p.strip()):
            for x in _ser_texts(vals, deadline):
                outs += [y for y in _rd_free(x) + [x] if _kbd_score(y) >= _RD_OK]
        outs = sorted(dict.fromkeys(outs), key=_kbd_score, reverse=True)
        return [lead + s for s in outs][:2]
    except Exception:   # noqa: BLE001
        return []


CANDIDATES.append(("serialization-wrapper", lambda s: None, ser_dec))


# Zalgo / combining-mark noise: base letters buried under stacked U+0300-036F (also U+0483-0489, U+1DC0.., U+20D0..)
# combining marks, or the sentence NFD-decomposed with accents hung on its letters. Read: NFD, drop every combining
# mark (unicodedata.combining() > 0 or category Mn/Me), keep the rest. The marks must sit in the blob AS combining
# characters (NFC French/Spanish prose with precomposed accents stays None) and what remains must be printable ASCII
# (Devanagari / Thai / pointed Hebrew, whose marks are part of the script, stay None).
_ZALGO_UP = "".join(map(chr, (0x30D, 0x30E, 0x304, 0x305, 0x33F, 0x311, 0x306, 0x310, 0x352, 0x357, 0x351, 0x307)))
_ZALGO_MID = "".join(map(chr, (0x315, 0x31B, 0x340, 0x341, 0x358, 0x321, 0x322, 0x327, 0x328, 0x334, 0x335, 0x336)))
_ZALGO_DOWN = "".join(map(chr, (0x316, 0x317, 0x318, 0x319, 0x31C, 0x31D, 0x31E, 0x31F, 0x320, 0x324, 0x325, 0x326)))


def zalgo_enc(s, n=3, space=False):
    """Plain -> zalgo: after every non-space char (every char with space=True) n up + 1 mid + n down marks, picked
    deterministically from the char's position (the generators are random: the decoder is what identifies)."""
    out = []
    for i, c in enumerate(s):
        out.append(c)
        if c.isspace() and not space:
            continue
        out += [_ZALGO_UP[(i + k) % len(_ZALGO_UP)] for k in range(n)]
        out.append(_ZALGO_MID[i % len(_ZALGO_MID)])
        out += [_ZALGO_DOWN[(i * 3 + k) % len(_ZALGO_DOWN)] for k in range(n)]
    return "".join(out)


def _zmark(c):
    return unicodedata.combining(c) > 0 or unicodedata.category(c) in ("Mn", "Me")


def zalgo_dec(t):
    """Zalgo / NFD-decomposed text -> the base text, else None (no raw combining marks, < 3 of them, or a non-ASCII
    remainder)."""
    try:
        if isinstance(t, (bytes, bytearray)):
            t = bytes(t).decode("utf-8")
        if not isinstance(t, str) or not t.strip() or len(t) > 200000:
            return None
        if sum(map(_zmark, t)) < 3:
            return None
        out = "".join(c for c in unicodedata.normalize("NFD", t) if not _zmark(c))
        if not out.strip() or any(not (c.isascii() and (c.isprintable() or c in "\t\n\r")) for c in out):
            return None
        return out
    except Exception:   # noqa: BLE001
        return None


def zalgo_free(p):
    """Speculative Mastery-line decoder: the line with its combining-mark noise stripped."""
    r = zalgo_dec(p) if isinstance(p, str) else None
    return [r] if r else []


CANDIDATES += [("zalgo", zalgo_enc, zalgo_dec), ("zalgo-mini", lambda s: zalgo_enc(s, 1), zalgo_dec),
               ("zalgo-spaces", lambda s: zalgo_enc(s, space=True), zalgo_dec)]


# NETSTRING KNOBS (speculative, no day; D24 "String Theory" = 1-char frames, netstr_dec): `<len>:<payload>,` frames
# with len > 1 / mixed lengths, len counted in UTF-8 BYTES (DJB spec) or in characters, leading zeros, whitespace or
# newlines between frames, a missing final ',', nested netstrings, and frames whose payload is itself a strict chunk
# codec (base64 / hex / ... per frame or over the joined payload). The WHOLE text must parse.
_NS_LEN = {bytes: re.compile(rb"\s*([0-9]{1,7}):"), str: re.compile(r"\s*([0-9]{1,7}):")}


def _ns_frames(b):
    """bytes (len = UTF-8 bytes) or str (len = characters) -> [payload] when the WHOLE buffer is a netstring run
    (optional whitespace between frames, the last frame may lack its ','), else None."""
    rx, comma = _NS_LEN[type(b)], b"," if isinstance(b, bytes) else ","
    out, i, n = [], 0, len(b)
    while True:
        while i < n and b[i:i + 1].isspace():
            i += 1
        if i >= n:
            return out or None
        m = rx.match(b, i)
        if not m:
            return None
        j = m.end()
        k = j + int(m.group(1))
        if k > n:
            return None
        out.append(b[j:k])
        if b[k:k + 1] == comma:
            i = k + 1
        elif not b[k:].strip():
            return out          # missing final comma (only the last frame)
        else:
            return None


def _ns_runs(t):
    """[(unit, [payload str])] for every unit (UTF-8 bytes, characters) under which the whole text parses."""
    runs = []
    try:
        fb = _ns_frames(t.encode("utf-8"))
        if fb:
            runs.append(("bytes", [x.decode("utf-8") for x in fb]))
    except UnicodeDecodeError:  # a byte count that splits a multibyte char
        pass
    if not t.isascii():
        fc = _ns_frames(t)
        if fc and (not runs or fc != runs[0][1]):
            runs.append(("chars", fc))
    return runs


def _ns_english(s):
    return bool(s) and s.isprintable() and _texty(s) >= 0.85 and (
        bool(_tc_piece(s)) or (" " in s.strip() and bool(re.search(r"[A-Za-z]{2}", s))))


def netstr_any_reads(t, _depth=0):
    """[(how, text)] readings of a whole-text netstring run, best first; [] when it is not one."""
    try:
        if isinstance(t, (bytes, bytearray)):
            t = bytes(t).decode("utf-8")
        if not isinstance(t, str) or not t.strip() or len(t) > 200000 or not re.match(r"\s*\d", t):
            return []
        from lib import decode as _dc
        reads = []
        for unit, pay in _ns_runs(t.strip()):
            joined = "".join(pay)
            if not joined.strip():
                continue
            if _depth < 4:
                if all(re.match(r"\s*\d+:", p) for p in pay):
                    inner = [netstr_any_reads(p, _depth + 1) for p in pay]     # every payload a netstring run
                    if all(inner):
                        reads.append((f"nested-{unit}", "".join(r[0][1] for r in inner)))
                ij = netstr_any_reads(joined, _depth + 1)                      # or the frames chop one inner stream
                if ij:
                    reads.append((f"nested-joined-{unit}", ij[0][1]))
            reads.append((unit, joined))
            if not _ns_english(joined):
                # coded frames: a strict chunk codec per payload or over the joined payload, kept only if it reads
                per = [_dc.decode_chunk(p, _nested=True) if p.strip() else p for p in pay]
                if all(x is not None for x in per) and _ns_english("".join(per)):
                    reads.append((f"{unit}-per-frame", "".join(per)))
                whole = _dc.decode_chunk(joined, _nested=True)
                if whole is not None and _ns_english(whole):
                    reads.append((f"{unit}-joined", whole))
        seen = set()
        reads = [r for r in reads if not (r[1] in seen or seen.add(r[1]))]
        return sorted(reads, key=lambda r: (not (SLUG.search(r[1]) and _TPL in r[1]), not _ns_english(r[1])))
    except Exception:   # noqa: BLE001
        return []


def netstr_any(t):
    """Whole text = a netstring run (any knob above) -> its best reading, else None."""
    r = netstr_any_reads(t)
    return r[0][1] if r else None


def netstr_any_free(p):
    """Speculative Mastery-line decoder: a fragment that is a whole netstring run (len > 1, bytes or chars, nested,
    coded frames) -> its readings, leading indent kept. D24's 1-char strict form stays netstr_dec's."""
    try:
        if not isinstance(p, str) or not re.match(r"\s*\d{1,7}:", p):
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return list(dict.fromkeys(lead + x for _h, x in netstr_any_reads(p) if x and x.isprintable()))[:3]
    except Exception:   # noqa: BLE001
        return []


def netstr_enc(s, sizes=(1,), unit="chars", sep="", final=True, lz=0, inner=None):
    """Plain -> netstring frames: payload chunks cycling through `sizes` (0 = one frame per word incl. its space),
    len in chars or UTF-8 bytes, zero-padded to `lz` digits, `sep` between frames, optional final ',', `inner` per
    frame payload codec."""
    if sizes == (0,):
        chunks = re.findall(r"\S+\s*", s)
    else:
        chunks, i, k = [], 0, 0
        while i < len(s):
            chunks.append(s[i:i + sizes[k % len(sizes)]])
            i, k = i + sizes[k % len(sizes)], k + 1
    out = []
    for c in chunks:
        c = inner(c) if inner else c
        n = len(c.encode("utf-8")) if unit == "bytes" else len(c)
        out.append(f"{n:0{lz}d}:{c},")
    r = sep.join(out)
    return r if final else r[:-1]


CANDIDATES += [
    ("netstring-whole", lambda s: netstr_enc(s, (len(s) or 1,)), netstr_any),
    ("netstring-words", lambda s: netstr_enc(s, (0,)), netstr_any),
    ("netstring-mixed", lambda s: netstr_enc(s, (3, 1, 4, 1, 5, 9, 2, 6)), netstr_any),
    ("netstring-bytes", lambda s: netstr_enc(s, (4,), unit="bytes"), netstr_any),
    ("netstring-newline", lambda s: netstr_enc(s, (5,), sep="\n"), netstr_any),
    ("netstring-zeropad", lambda s: netstr_enc(s, (2,), lz=3), netstr_any),
    ("netstring-nofinal", lambda s: netstr_enc(s, (6,), final=False), netstr_any),
    ("netstring-nested", lambda s: netstr_enc(netstr_enc(s), (8,)), netstr_any),
    ("netstring-b64-frames", lambda s: netstr_enc(s, (0,), inner=lambda c: base64.b64encode(_u(c)).decode()),
     netstr_any),
    ("netstring-hex-frames", lambda s: netstr_enc(s, (6,), inner=lambda c: _u(c).hex()), netstr_any),
]


# INDEXED / RUN-COUNT FRAMES (speculative, no day; "Count carefully" re-read): the number beside each payload is a
# POSITION (frames shuffled: `17:a,3:b`, `a@17`, `[17]a`; sort by index, indices exactly 0..n-1 or 1..n) or a REPEAT
# COUNT (run-length: `3:o,` = 'ooo', `o*3`). Netstring length and count read the same when every N = 1, so netstring
# wins first; then index (a permutation of range(n)), then count (1-char payloads, some N > 1).
_FR_SEPS = (", ", "; ", ",", ";", " | ", "|", "\n", " ", "")


def _fr_index(t):
    """[(form, sep, text)] for every frame form / separator under which the WHOLE text is a permutation of indices."""
    out = []
    for sep in _FR_SEPS:
        s = re.escape(sep)
        for form, rx, pre in (("colon", rf"(?:^|{s})(\d{{1,5}}):", True), ("bracket", rf"(?:^|{s})\[(\d{{1,5}})\]", True),
                              ("at", rf"@(\d{{1,5}})(?:{s}|$)" if sep else r"@(\d{1,5})", False)):
            if not sep and form == "colon":
                continue          # `17:a3:b` has no frame boundary
            parts = re.split(rx, t)
            if pre:
                if len(parts) < 5 or parts[0]:
                    continue
                idx, pay = parts[1::2], parts[2::2]
            else:
                if len(parts) < 5 or parts[-1]:
                    continue
                idx, pay = parts[1::2], parts[0:-1:2]
            n = len(idx)
            try:
                ix = [int(x) for x in idx]
            except ValueError:
                continue
            base = min(ix)
            if base not in (0, 1) or sorted(ix) != list(range(base, base + n)) or not all(pay):
                continue
            if sep and pay[-1].endswith(sep) and pre:   # an optional trailing separator after the last frame
                out.append((form, sep, "".join(p for _i, p in sorted(zip(ix, pay[:-1] + [pay[-1][:-len(sep)]])))))
            out.append((form, sep, "".join(p for _i, p in sorted(zip(ix, pay)))))
    return out


def _fr_count(t):
    """[(form, sep, text)]: run-count frames `N:c` (sep-joined, final sep optional) or `c*N` -> c repeated N."""
    out = []
    for sep in _FR_SEPS:
        s = re.escape(sep)
        for form, frame, cnt_first in (("colon", r"(\d{1,4}):(.)", True), ("star", r"(.)\*(\d{1,4})", False)):
            if not sep and form == "colon" and not re.fullmatch(r"(?:\d{1,4}:.)+", t, re.S):
                continue
            m = re.fullmatch(rf"{frame}(?:{s}{frame})*(?:{s})?", t, re.S)
            if not m:
                continue
            fr = re.findall(rf"{frame}(?:{s}|$)" if sep else frame, t, re.S)
            pairs = [(int(a), b) if cnt_first else (int(b), a) for a, b in fr]
            if len(pairs) < 2 or (cnt_first and not any(n > 1 for n, _c in pairs)) or any(n < 1 or n > 4096 for n, _c in pairs):
                continue
            txt = "".join(c * n for n, c in pairs)
            if len(txt) <= 200000:
                out.append((form, sep, txt))
    return out


def frames_reads(t):
    """[(how, text)] readings of a whole-text indexed / run-count frame run, best first; [] when it is not one."""
    try:
        if isinstance(t, (bytes, bytearray)):
            t = bytes(t).decode("utf-8")
        if not isinstance(t, str) or not t.strip() or len(t) > 200000:
            return []
        t = t.strip("\r\n")
        reads = [(f"netstring-{h}", x) for h, x in netstr_any_reads(t)]
        reads += [(f"index-{f}", x) for f, _s, x in _fr_index(t)]
        reads += [(f"count-{f}", x) for f, _s, x in _fr_count(t)]
        seen = set()
        reads = [r for r in reads if r[1] and not (r[1] in seen or seen.add(r[1]))]
        reads = [r for r in reads if r[1].isprintable() and (SLUG.search(r[1]) or _ns_english(r[1]))]
        return sorted(reads, key=lambda r: (not (SLUG.search(r[1]) and _TPL in r[1]), not SLUG.search(r[1]),
                                            not _ns_english(r[1])))
    except Exception:   # noqa: BLE001
        return []


def frames_dec(t):
    """Whole text = netstring / shuffled index frames / run-count frames -> its best (slug-gated) reading, else None."""
    r = frames_reads(t)
    return r[0][1] if r else None


def frames_free(p):
    """Speculative Mastery-line decoder for a fragment that is a whole index-shuffled / run-count frame run."""
    try:
        if not isinstance(p, str) or not re.search(r"\d", p) or not re.search(r"\d+:|\[\d+\]|@\d+|\*\d+", p):
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return list(dict.fromkeys(lead + x for h, x in frames_reads(p.strip())
                                  if not h.startswith("netstring")))[:3]
    except Exception:   # noqa: BLE001
        return []


def frames_index_enc(s, form="colon", sep=",", base=0, seed=None):
    """Plain -> one frame per character tagged with its position, frames shuffled (deterministic seed)."""
    import random
    fr = [(i + base, c) for i, c in enumerate(s)]
    random.Random(len(s) if seed is None else seed).shuffle(fr)
    fmt = {"colon": "{0}:{1}", "bracket": "[{0}]{1}", "at": "{1}@{0}"}[form]
    return sep.join(fmt.format(i, c) for i, c in fr)


def frames_count_enc(s, form="colon", sep=","):
    """Plain -> run-count frames over runs of equal characters: `N:c` or `c*N`, sep-joined."""
    fmt = "{0}:{1}" if form == "colon" else "{1}*{0}"
    return sep.join(fmt.format(len(m.group(0)), m.group(1)) for m in re.finditer(r"(.)\1*", s, re.S))


CANDIDATES += [
    ("frames-index-colon", lambda s: frames_index_enc(s), frames_dec),
    ("frames-index-colon-1based-semicolon", lambda s: frames_index_enc(s, sep=";", base=1), frames_dec),
    ("frames-index-bracket", lambda s: frames_index_enc(s, "bracket", ""), frames_dec),
    ("frames-index-at-space", lambda s: frames_index_enc(s, "at", " "), frames_dec),
    ("frames-count-colon", lambda s: frames_count_enc(s), frames_dec),
    ("frames-count-star", lambda s: frames_count_enc(s, "star"), frames_dec),
]



# TNETSTRINGS (speculative, no day; sibling spec of D24's netstrings, Zed Shaw's typed netstrings): `<len>:<data><tag>`
# with tag ',' string (';' unicode in some forks), '#' int, '^' float, '!' bool, '~' null, ']' list, '}' dict; len in
# UTF-8 bytes (spec) or characters. ']' / '}' payloads parse recursively; the WHOLE text must be 1+ tnetstrings.
# Reading = the string leaves in order (dict values; int-keyed dicts sorted by key), else int leaves as char codes.
_TN_LEN = {bytes: re.compile(rb"\s*([0-9]{1,9}):"), str: re.compile(r"\s*([0-9]{1,9}):")}


def _tn_parse(b, i, depth=0):
    """-> ((tag, value), end) for the tnetstring at b[i:]; raises ValueError on any malformation."""
    m = _TN_LEN[type(b)].match(b, i)
    if not m or depth > 32:
        raise ValueError("not a tnetstring")
    j = m.end()
    k = j + int(m.group(1))
    if k >= len(b):
        raise ValueError("overrun")
    tag, pay = b[k:k + 1], b[j:k]
    tag = tag.decode("latin-1") if isinstance(tag, bytes) else tag
    if tag in ",;":
        val = pay.decode("utf-8") if isinstance(pay, bytes) else pay
    elif tag == "#":
        val = int(pay)
    elif tag == "^":
        val = pay.decode("ascii") if isinstance(pay, bytes) else pay
        float(val)
    elif tag == "!":
        p = pay.decode("ascii") if isinstance(pay, bytes) else pay
        if p not in ("true", "false"):
            raise ValueError("bool")
        val = p == "true"
    elif tag == "~":
        if len(pay):
            raise ValueError("null")
        val = None
    elif tag in "]}":
        val, q = [], 0
        while q < len(pay):
            node, q = _tn_parse(pay, q, depth + 1)
            val.append(node)
        if tag == "}":
            if len(val) % 2:
                raise ValueError("odd dict")
            val = list(zip(val[0::2], val[1::2]))
    else:
        raise ValueError("tag")
    return (tag, val), k + 1


def _tn_top(b):
    """Whole buffer -> [node] (whitespace allowed between top-level tnetstrings), else None."""
    try:
        out, i = [], 0
        while True:
            while i < len(b) and b[i:i + 1].isspace():
                i += 1
            if i >= len(b):
                return out or None
            node, i = _tn_parse(b, i)
            out.append(node)
    except (ValueError, UnicodeDecodeError, OverflowError, RecursionError):
        return None


def _tn_dict_order(pairs):
    """Dict pairs in reading order: by int key when the keys are exactly 0..n-1 / 1..n, else insertion order."""
    try:
        ks = [int(k[1]) for k, _v in pairs]
        if sorted(ks) == list(range(min(ks), min(ks) + len(ks))) and min(ks) in (0, 1):
            return [p for _k, p in sorted(zip(ks, pairs))]
    except (ValueError, TypeError):
        pass
    return pairs


def _tn_leaves(node, keys=False):
    """Flatten to [(tag, value)] leaves in order (dict values only unless keys=True)."""
    tag, val = node
    if tag == "]":
        return [x for n in val for x in _tn_leaves(n, keys)]
    if tag == "}":
        return [x for k, v in _tn_dict_order(val) for x in ((_tn_leaves(k, keys) if keys else []) + _tn_leaves(v, keys))]
    return [node]


def tnet_reads(t, _depth=0, _cue=False):
    """[(how, text)] readings of a whole-text tnetstring run, best first (slug / English-gated); [] when not one.
    _cue: demand a non-',' tag (a ','-only run is a plain netstring run -- netstring-any's)."""
    try:
        if isinstance(t, (bytes, bytearray)):
            t = bytes(t).decode("utf-8")
        if not isinstance(t, str) or not t.strip() or len(t) > 200000 or not re.match(r"\s*\d", t):
            return []
        t = t.strip()
        tops = []
        for unit, buf in (("bytes", t.encode("utf-8")), ("chars", t)):
            if unit == "chars" and t.isascii():
                continue
            top = _tn_top(buf)
            if top:
                tops.append((unit, top))
        reads = []
        for unit, top in tops:
            root = ("]", top)
            if _cue and not re.search(r"[#^!~\]};]", "".join(n[0] for n in _tn_walk(root))):
                continue
            for keys in (False, True):
                lv = [x for n in top for x in _tn_leaves(n, keys)]
                strs = [v for g, v in lv if g in ",;"]
                if strs:
                    joined = "".join(strs)
                    reads.append((f"{unit}-strings" + ("-keys" if keys else ""), joined))
                    if not keys and _depth < 3 and re.match(r"\s*\d+:", joined):
                        reads += [(f"{unit}-nested-{h}", x) for h, x in tnet_reads(joined, _depth + 1)]
                    if not keys and not _ns_english(joined) and _depth < 3:
                        from lib import decode as _dc
                        whole = _dc.decode_chunk(joined, _nested=True)
                        if whole is not None:
                            reads.append((f"{unit}-strings-coded", whole))
                if not keys and lv and all(g == "#" for g, _v in lv) and all(0 < v < 0x110000 for _g, v in lv):
                    reads.append((f"{unit}-charcodes", "".join(chr(v) for _g, v in lv)))
                if not keys and lv:
                    reads.append((f"{unit}-scalars", "".join(
                        v if g in ",;" else "" if g == "~" else str(v).lower() if g == "!" else str(v) for g, v in lv)))
        seen = set()
        reads = [r for r in reads if r[1] and r[1].isprintable() and not (r[1] in seen or seen.add(r[1]))
                 and (SLUG.search(r[1]) or _ns_english(r[1]))]
        return sorted(reads, key=lambda r: (not (SLUG.search(r[1]) and _TPL in r[1]), not SLUG.search(r[1]),
                                            not _ns_english(r[1])))
    except Exception:   # noqa: BLE001
        return []


def _tn_walk(node):
    yield node
    tag, val = node
    if tag == "]":
        for n in val:
            yield from _tn_walk(n)
    elif tag == "}":
        for k, v in val:
            yield from _tn_walk(k)
            yield from _tn_walk(v)


def tnet_dec(t):
    """Whole text = tnetstring(s) -> its best slug / English-gated reading, else None."""
    r = tnet_reads(t)
    return r[0][1] if r else None


def tnet_free(p):
    """Speculative Mastery-line decoder: a fragment that is a whole tnetstring run with at least one typed tag
    (',' only = plain netstrings, left to netstring-any / D24), leading indent kept."""
    try:
        if not isinstance(p, str) or not re.match(r"\s*\d{1,9}:", p) or not re.search(r"[#^!~\]};]\s*$", p):
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return list(dict.fromkeys(lead + x for _h, x in tnet_reads(p, _cue=True)))[:3]
    except Exception:   # noqa: BLE001
        return []


def tnet_dump(v):
    """Python value -> tnetstring text (len in UTF-8 bytes): str ',', bool '!', int '#', float '^', None '~',
    list ']', dict '}'."""
    if isinstance(v, str):
        tag, pay = ",", v
    elif isinstance(v, bool):
        tag, pay = "!", "true" if v else "false"
    elif isinstance(v, int):
        tag, pay = "#", str(v)
    elif isinstance(v, float):
        tag, pay = "^", repr(v)
    elif v is None:
        tag, pay = "~", ""
    elif isinstance(v, (list, tuple)):
        tag, pay = "]", "".join(tnet_dump(x) for x in v)
    elif isinstance(v, dict):
        tag, pay = "}", "".join(tnet_dump(str(k)) + tnet_dump(x) for k, x in v.items())
    else:
        raise TypeError(type(v))
    return f"{len(pay.encode('utf-8'))}:{pay}{tag}"


CANDIDATES += [
    ("tnetstring-flat", lambda s: tnet_dump(s), tnet_dec),
    ("tnetstring-list1", lambda s: tnet_dump(list(s)), tnet_dec),
    ("tnetstring-dict-index", lambda s: tnet_dump({i: c for i, c in enumerate(s)}), tnet_dec),
    ("tnetstring-nested-words", lambda s: tnet_dump([[w, None] for w in re.findall(r"\S+\s*", s)]), tnet_dec),
    ("tnetstring-charcodes", lambda s: tnet_dump([ord(c) for c in s]), tnet_dec),
]


# BENCODE + RIVEST S-EXPRESSIONS (speculative, no day; netstrings' `<len>:<data>` atom with NO trailing ','):
# bencode (BitTorrent) `4:spam` string, `i42e` int, `l..e` list, `d..e` dict (keys sorted byte-wise; reading order =
# int-like keys numerically, else as written); Rivest SPKI canonical sexp `(3:abc5:hello)` with `[hint]` display
# hints, plus the transport / advanced atoms `{b64 of canonical}`, `|b64|`, `#hex#` (optional decimal length prefix,
# whitespace between elements). Nodes reuse the tnetstring shape: (',', text) / ('#', int) / (']', [n]) / ('}', pairs).
_BC_LEN = {bytes: re.compile(rb"(0|[1-9][0-9]{0,8}):"), str: re.compile(r"(0|[1-9][0-9]{0,8}):")}
_BC_INT = {bytes: re.compile(rb"i(0|-?[1-9][0-9]{0,30})e"), str: re.compile(r"i(0|-?[1-9][0-9]{0,30})e")}


def _bx_text(pay):
    return pay.decode("utf-8") if isinstance(pay, (bytes, bytearray)) else pay


def _bc_parse(b, i, depth=0):
    """-> (node, end) for the bencoded value at b[i:]; raises ValueError on any malformation."""
    if depth > 64 or i >= len(b):
        raise ValueError("not bencode")
    c = b[i:i + 1]
    c = c.decode("latin-1") if isinstance(c, bytes) else c
    if c == "i":
        m = _BC_INT[type(b)].match(b, i)
        if not m:
            raise ValueError("int")
        return ("#", int(m.group(1))), m.end()
    if c in "ld":
        out, j = [], i + 1
        while b[j:j + 1] not in (b"e", "e"):
            if j >= len(b):
                raise ValueError("unterminated")
            node, j = _bc_parse(b, j, depth + 1)
            out.append(node)
        if c == "d":
            if len(out) % 2 or any(k[0] != "," for k in out[0::2]):
                raise ValueError("dict")
            return ("}", list(zip(out[0::2], out[1::2]))), j + 1
        return ("]", out), j + 1
    m = _BC_LEN[type(b)].match(b, i)
    if not m:
        raise ValueError("not bencode")
    k = m.end() + int(m.group(1))
    if k > len(b):
        raise ValueError("overrun")
    return (",", _bx_text(b[m.end():k])), k


def _bc_top(b):
    """Whole buffer -> [node] (1+ bencoded values, whitespace allowed between), else None."""
    try:
        out, i = [], 0
        while True:
            while i < len(b) and b[i:i + 1].isspace():
                i += 1
            if i >= len(b):
                return out or None
            node, i = _bc_parse(b, i)
            out.append(node)
    except (ValueError, UnicodeDecodeError, OverflowError, RecursionError):
        return None


_SX_ATOM = re.compile(rb"([0-9]{0,9})(?::|(\|[A-Za-z0-9+/=\s]*\|)|(#[0-9A-Fa-f\s]*#)|(\{[A-Za-z0-9+/=\s]*\}))")


def _sx_ws(b, i):
    while i < len(b) and b[i:i + 1].isspace():
        i += 1
    return i


def _sx_atom(b, i, depth):
    """-> (bytes, end) for a verbatim `len:data`, `|b64|` or `#hex#` atom (or a `{transport}` node), else ValueError."""
    m = _SX_ATOM.match(b, i)
    if not m or not (m.group(1) or m.group(2) or m.group(3) or m.group(4)):
        raise ValueError("atom")
    if m.group(2) or m.group(3):
        body = re.sub(rb"\s+", b"", m.group(0)[len(m.group(1)) + 1:-1])
        val = base64.b64decode(body, validate=True) if m.group(2) else bytes.fromhex(body.decode())
        if m.group(1) and int(m.group(1)) != len(val):
            raise ValueError("atom length")
        return val, m.end()
    if m.group(4):
        if m.group(1):
            raise ValueError("transport")
        inner = base64.b64decode(re.sub(rb"\s+", b"", m.group(4)[1:-1]), validate=True)
        node, j = _sx_parse(inner, 0, depth + 1)
        if _sx_ws(inner, j) != len(inner):
            raise ValueError("transport tail")
        return node, m.end()
    k = m.end() + int(m.group(1))
    if not m.group(1) or k > len(b):
        raise ValueError("overrun")
    return b[m.end():k], k


def _sx_parse(b, i, depth=0):
    """-> (node, end) for the sexp element at b[i:] (bytes; len = bytes); hints dropped; ValueError otherwise."""
    if depth > 64:
        raise ValueError("deep")
    i = _sx_ws(b, i)
    if b[i:i + 1] == b"(":
        out, j = [], _sx_ws(b, i + 1)
        while b[j:j + 1] != b")":
            if j >= len(b):
                raise ValueError("unterminated")
            node, j = _sx_parse(b, j, depth + 1)
            out.append(node)
            j = _sx_ws(b, j)
        return ("]", out), j + 1
    if b[i:i + 1] == b"[":
        _hint, j = _sx_atom(b, _sx_ws(b, i + 1), depth)
        j = _sx_ws(b, j)
        if isinstance(_hint, tuple) or b[j:j + 1] != b"]":
            raise ValueError("hint")
        val, j = _sx_atom(b, _sx_ws(b, j + 1), depth)
        if isinstance(val, tuple):
            raise ValueError("hinted transport")
        return (",", val.decode("utf-8")), j
    val, j = _sx_atom(b, i, depth)
    return (val if isinstance(val, tuple) else (",", val.decode("utf-8"))), j


def _sx_top(b):
    """Whole buffer (bytes) -> [node] of 1+ s-expressions with at least one list / transport form, else None."""
    try:
        if not re.match(rb"\s*[(\[{]", b) and not re.search(rb"[|#]", b):
            return None
        out, i = [], _sx_ws(b, 0)
        while i < len(b):
            node, i = _sx_parse(b, i)
            out.append(node)
            i = _sx_ws(b, i)
        return out or None
    except (ValueError, UnicodeDecodeError, OverflowError, RecursionError, binascii.Error):
        return None


def _sx_nohead(node):
    """String leaves skipping each multi-element list's head atom (`(msg ...)` type tags)."""
    tag, val = node
    if tag == "]":
        start = 1 if len(val) > 1 and val[0][0] == "," else 0
        return [x for n in val[start:] for x in _sx_nohead(n)]
    return [node] if tag == "," else []


def bencsexp_reads(t, _depth=0):
    """[(how, text)] readings of a whole-text bencode / Rivest sexp run, best first (slug / English-gated)."""
    try:
        if isinstance(t, (bytes, bytearray)):
            t = bytes(t).decode("utf-8")
        if not isinstance(t, str) or not t.strip() or len(t) > 200000:
            return []
        t = t.strip()
        tops = []
        for unit, buf in (("bytes", t.encode("utf-8")), ("chars", t)):
            if unit == "chars" and t.isascii():
                continue
            top = _bc_top(buf)
            if top:
                tops.append((f"bencode-{unit}", top))
        top = _sx_top(t.encode("utf-8"))
        if top:
            tops.append(("sexp", top))
        reads = []
        for unit, top in tops:
            for keys in (False, True):
                lv = [x for n in top for x in _tn_leaves(n, keys)]
                strs = [v for g, v in lv if g == ","]
                if strs:
                    joined = "".join(strs)
                    reads.append((f"{unit}-strings" + ("-keys" if keys else ""), joined))
                    if not keys and _depth < 3 and re.match(r"\s*(?:\d+:|[(\[{dl])", joined) and joined != t:
                        reads += [(f"{unit}-nested-{h}", x) for h, x in bencsexp_reads(joined, _depth + 1)]
                    if not keys and not _ns_english(joined) and _depth < 3:
                        from lib import decode as _dc
                        whole = _dc.decode_chunk(joined, _nested=True)
                        if whole is not None:
                            reads.append((f"{unit}-strings-coded", whole))
                if not keys and lv and all(g == "#" for g, _v in lv) and all(0 < v < 0x110000 for _g, v in lv):
                    reads.append((f"{unit}-charcodes", "".join(chr(v) for _g, v in lv)))
                if not keys and lv:
                    reads.append((f"{unit}-scalars", "".join(str(v) for _g, v in lv)))
            if unit == "sexp":
                reads.append(("sexp-nohead", "".join(v for n in top for _g, v in _sx_nohead(n))))
        seen = set()
        reads = [r for r in reads if r[1] and r[1].isprintable() and not (r[1] in seen or seen.add(r[1]))
                 and (SLUG.search(r[1]) or _ns_english(r[1]))]
        return sorted(reads, key=lambda r: (not (SLUG.search(r[1]) and _TPL in r[1]),
                                            not (SLUG.search(r[1]) and r[1].startswith(_TPL[:12])),
                                            not SLUG.search(r[1]), not _ns_english(r[1])))
    except Exception:   # noqa: BLE001
        return []


def bencsexp_dec(t):
    """Whole text = bencode / Rivest sexp -> its best slug / English-gated reading, else None."""
    r = bencsexp_reads(t)
    return r[0][1] if r else None


def bencsexp_free(p):
    """Speculative Mastery-line decoder: a fragment that is a whole bencode value run (list / dict / int-led, or a
    length-led string run without netstring commas) or a Rivest sexp (`(`, `[`, `{` led), leading indent kept."""
    try:
        if not isinstance(p, str) or not re.match(r"\s*(?:[ld](?:\d|i-?\d|e)|i-?\d|\d{1,9}:|[(\[{])", p):
            return []
        if re.match(r"\s*\d{1,9}:", p) and re.search(r"[,#^!~\]};]\s*$", p):
            return []   # `,`-terminated = netstrings / tnetstrings (netstring-any / D24 / tnetstring)
        lead = p[:len(p) - len(p.lstrip())]
        return list(dict.fromkeys(lead + x for _h, x in bencsexp_reads(p)))[:3]
    except Exception:   # noqa: BLE001
        return []


def benc_dump(v):
    """Python value -> bencode text (len in UTF-8 bytes; dict keys sorted byte-wise per spec)."""
    if isinstance(v, str):
        return f"{len(v.encode('utf-8'))}:{v}"
    if isinstance(v, int):
        return f"i{v}e"
    if isinstance(v, (list, tuple)):
        return "l" + "".join(benc_dump(x) for x in v) + "e"
    if isinstance(v, dict):
        return "d" + "".join(benc_dump(k) + benc_dump(v[k]) for k in sorted(map(str, v), key=lambda k: k.encode())) + "e"
    raise TypeError(type(v))


def sexp_dump(v):
    """Python str / nested list -> Rivest canonical sexp text (len in UTF-8 bytes)."""
    if isinstance(v, str):
        return f"{len(v.encode('utf-8'))}:{v}"
    return "(" + "".join(sexp_dump(x) for x in v) + ")"


CANDIDATES += [
    ("bencode-list1", lambda s: benc_dump(list(s)), bencsexp_dec),
    ("bencode-string", lambda s: benc_dump(s), bencsexp_dec),
    ("bencode-dict-index", lambda s: benc_dump({f"{i:04d}": c for i, c in enumerate(s)}), bencsexp_dec),
    ("bencode-charcodes", lambda s: benc_dump([ord(c) for c in s]), bencsexp_dec),
    ("sexp-canonical", lambda s: sexp_dump(list(s)), bencsexp_dec),
    ("sexp-words", lambda s: sexp_dump(["msg"] + re.findall(r"\S+\s*", s)), bencsexp_dec),
    ("sexp-transport", lambda s: "{" + base64.b64encode(sexp_dump(list(s)).encode("utf-8")).decode() + "}",
     bencsexp_dec),
]

# BINARY LENGTH-PREFIX FRAMES (speculative, no day; coverage atlas length-prefix-binary-tlv): after a hex / base64 /
# base32 layer the bytes are a run of [len][payload] frames -- Pascal u8, u16/u32 BE/LE, LEB128 varint, TLV (1 type
# byte + u8 / u16 BE/LE len), protobuf wire (varint tag of wire type 2 + varint len) -- or the TEXT itself is a run of
# fixed-width length digits + payload (`0eNice work dec`: 2 / 4 hex digits, 2 / 3 decimal digits). The WHOLE stream
# must parse; the payloads join (raw, or each / all through a strict chunk codec) into English. Bytes that already read
# as printable text belong to plain hex / base64: a byte-frame reading of them needs the full crib.
_LP_BYTE_KINDS = ("u8", "u16be", "u16le", "u32be", "u32le", "varint", "tlv8", "tlv16be", "tlv16le", "proto")
_LP_TEXT_KINDS = (("hex2", 16, 2), ("hex4", 16, 4), ("dec2", 10, 2), ("dec3", 10, 3))


def _lp_varint(b, p):
    v, s = 0, 0
    while p < len(b) and s < 35:
        v |= (b[p] & 0x7F) << s
        p, s = p + 1, s + 7
        if not b[p - 1] & 0x80:
            return v, p
    return None, None


def _lp_walk(b, kind):
    """[payload bytes] when the WHOLE buffer is a run of `kind` frames (>= 1 non-empty payload), else None."""
    out, p, n = [], 0, len(b)
    while p < n:
        if kind == "proto":
            tag, p = _lp_varint(b, p)
            if tag is None or tag & 7 != 2 or tag >> 3 == 0:
                return None
            ln, p = _lp_varint(b, p)
            if ln is None:
                return None
        elif kind == "varint":
            ln, p = _lp_varint(b, p)
            if ln is None:
                return None
        else:
            if kind.startswith("tlv"):
                p += 1
            w = 1 if kind in ("u8", "tlv8") else 2 if kind.endswith(("16be", "16le")) else 4
            if p + w > n:
                return None
            ln = int.from_bytes(b[p:p + w], "little" if kind.endswith("le") else "big")
            p += w
        if p + ln > n:
            return None
        out.append(b[p:p + ln])
        p += ln
    return out if any(out) else None


def _lp_text_walk(t, base, w):
    """[payload str] when the whole text is a run of `w`-digit base-`base` lengths + that many chars, else None."""
    out, p, n = [], 0, len(t)
    dig = "0123456789abcdefABCDEF" if base == 16 else "0123456789"
    while p < n:
        h = t[p:p + w]
        if len(h) != w or any(c not in dig for c in h):
            return None
        ln = int(h, base)
        p += w
        if p + ln > n:
            return None
        out.append(t[p:p + ln])
        p += ln
    return out if len(out) > 1 else None   # one frame = the text minus a 2-4 char head: no evidence


def _lp_layers(t):
    """[(layer, bytes)] of a hex / base64(url) / base32 line (each strict, whole-line)."""
    out = []
    b = _leb_bytes(t)
    if b:
        out.append(("hex", b))
    s = re.sub(r"\s+", "", t)
    if s and len(s) <= 80000 and re.fullmatch(r"[A-Za-z0-9+/_-]+={0,2}", s) and len(s.rstrip("=")) % 4 != 1:
        try:
            x = base64.b64decode(s.rstrip("=").replace("-", "+").replace("_", "/") + "=" * (-len(s.rstrip("=")) % 4),
                                 validate=True)
            if x and x != b:
                out.append(("b64", x))
        except (binascii.Error, ValueError):
            pass
    if s and re.fullmatch(r"[A-Z2-7]+=*", s.upper()) and len(s) % 8 in (0, 2, 4, 5, 7):
        try:
            out.append(("b32", base64.b32decode(s.upper().rstrip("=") + "=" * (-len(s.rstrip("=")) % 8))))
        except (binascii.Error, ValueError):
            pass
    return out


def _lp_join(pay, how, reads, _dc):
    """Append (how, text) readings of joined str payloads: raw if it reads, else per-frame / joined chunk codec."""
    joined = "".join(pay)
    if _ns_english(joined) or _crib_piece(joined):
        reads.append((how, joined))
        return
    if len(pay) <= 600:
        per = [_dc.decode_chunk(x, _nested=True) if x.strip() else x for x in pay]
        if all(x is not None for x in per) and _ns_english("".join(per)):
            reads.append((f"{how}-per-frame", "".join(per)))
    whole = _dc.decode_chunk(joined, _nested=True) if joined.strip() else None
    if whole is not None and _ns_english(whole):
        reads.append((f"{how}-joined", whole))


def lenpfx_reads(t):
    """[(how, text)] readings of a binary length-prefix frame run (under hex / b64 / b32) or a digit-length text frame
    run, crib first; [] when it is not one. Never raises."""
    try:
        if isinstance(t, (bytes, bytearray)):
            t = bytes(t).decode("utf-8")
        if not isinstance(t, str) or not t.strip() or len(t) > 120000:
            return []
        from lib import decode as _dc
        t, reads = t.strip(), []
        for layer, b in _lp_layers(t):
            try:
                owned = b.decode("utf-8").isprintable()   # plain hex / base64 of text: those decoders own it
            except UnicodeDecodeError:
                owned = False
            got = []
            for kind in _LP_BYTE_KINDS:
                fr = _lp_walk(b, kind)
                if not fr:
                    continue
                try:
                    pay = [x.decode("utf-8") for x in fr]
                except UnicodeDecodeError:
                    continue
                _lp_join(pay, f"{layer}-{kind}", got, _dc)
            reads += [r for r in got if not owned or (SLUG.search(r[1]) and _TPL in r[1])]
        for kind, base, w in _LP_TEXT_KINDS:
            fr = _lp_text_walk(t, base, w)
            if fr:
                _lp_join(fr, f"text-{kind}", reads, _dc)
        seen = set()
        reads = [r for r in reads if r[1] != t and not (r[1] in seen or seen.add(r[1]))]
        return sorted(reads, key=lambda r: (not (SLUG.search(r[1]) and _TPL in r[1]), not _crib_piece(r[1]),
                                            not _ns_english(r[1]), -_texty(r[1])))
    except Exception:   # noqa: BLE001
        return []


def lenpfx_dec(t):
    """Whole text = a length-prefix frame run (any knob above) -> its best reading, else None."""
    r = lenpfx_reads(t)
    return r[0][1] if r else None


def lenpfx_free(p):
    """Speculative Mastery-line decoder: a fragment that is a whole length-prefix frame run, leading indent kept."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return list(dict.fromkeys(lead + x for _h, x in lenpfx_reads(p) if x and x.isprintable()))[:3]
    except Exception:   # noqa: BLE001
        return []


def lenpfx_enc(s, kind="u8", chunks="chars", fmt="hex", types=(1, 2)):
    """Plain -> length-prefix frames: one frame per char / word (incl. its trailing space) / whole, under `kind`
    (byte kinds above; tlv* cycle through `types`, proto = field 1) as hex / b64, or text kinds (hex2 ...) raw."""
    parts = list(s) if chunks == "chars" else re.findall(r"\S+\s*", s) if chunks == "words" else [s]
    tk = dict((k, (bs, w)) for k, bs, w in _LP_TEXT_KINDS)
    if kind in tk:
        bs, w = tk[kind]
        return "".join((f"{len(c):0{w}x}" if bs == 16 else f"{len(c):0{w}d}") + c for c in parts)

    def var(v):
        o = bytearray()
        while True:
            o.append((v & 0x7F) | (0x80 if v > 0x7F else 0))
            v >>= 7
            if not v:
                return bytes(o)
    out = bytearray()
    for i, c in enumerate(parts):
        c = _u(c)
        if kind == "proto":
            out += b"\x0a" + var(len(c))
        elif kind == "varint":
            out += var(len(c))
        else:
            if kind.startswith("tlv"):
                out.append(types[i % len(types)])
            w = 1 if kind in ("u8", "tlv8") else 2 if kind.endswith(("16be", "16le")) else 4
            out += len(c).to_bytes(w, "little" if kind.endswith("le") else "big")
        out += c
    return out.hex() if fmt == "hex" else base64.b64encode(bytes(out)).decode()


CANDIDATES += [
    ("lenpfx-u8-chars-hex", lambda s: lenpfx_enc(s, "u8"), lenpfx_dec),
    ("lenpfx-u8-words-hex", lambda s: lenpfx_enc(s, "u8", "words"), lenpfx_dec),
    ("lenpfx-pascal-b64", lambda s: lenpfx_enc(s, "u8", "whole", "b64"), lenpfx_dec),
    ("lenpfx-u16be-words-hex", lambda s: lenpfx_enc(s, "u16be", "words"), lenpfx_dec),
    ("lenpfx-u16le-words-hex", lambda s: lenpfx_enc(s, "u16le", "words"), lenpfx_dec),
    ("lenpfx-u32be-words-b64", lambda s: lenpfx_enc(s, "u32be", "words", "b64"), lenpfx_dec),
    ("lenpfx-u32le-words-hex", lambda s: lenpfx_enc(s, "u32le", "words"), lenpfx_dec),
    ("lenpfx-varint-whole-hex", lambda s: lenpfx_enc(s, "varint", "whole"), lenpfx_dec),
    ("lenpfx-proto-words-hex", lambda s: lenpfx_enc(s, "proto", "words"), lenpfx_dec),
    ("lenpfx-proto-words-b64", lambda s: lenpfx_enc(s, "proto", "words", "b64"), lenpfx_dec),
    ("lenpfx-tlv8-chars-hex", lambda s: lenpfx_enc(s, "tlv8"), lenpfx_dec),
    ("lenpfx-tlv16be-words-hex", lambda s: lenpfx_enc(s, "tlv16be", "words"), lenpfx_dec),
    ("lenpfx-hex2-words", lambda s: lenpfx_enc(s, "hex2", "words"), lenpfx_dec),
    ("lenpfx-hex4-words", lambda s: lenpfx_enc(s, "hex4", "words"), lenpfx_dec),
]



# --- string-builder literals ("String" as code) -------------------------------------------------------------------
# The blob is SOURCE that builds the sentence: "Ni" + "ce" (JS/Java/C#), Python implicit 'N' 'i', chr(78)+chr(105),
# String.fromCharCode(78,105), [char]78+[char]105, new char[]{'N','i'}, ''.join([...]), ["N","i"] JSON, b'\x4e',
# StringBuilder .append chains, `s = ..; s += ..`. Never eval: lib.codec._fs_eval folds literal-only nodes (an unknown
# identifier / call -> None). A lone plain literal is not a builder (no evidence) -> None.
_SB_CHARCAST = re.compile(r"\(\s*(?:char|wchar_t|Char|System\.Char)\s*\)\s*(0[xX][0-9a-fA-F]+|\d+)")
_SB_FCC = re.compile(r"String\.fromCharCode\s*(?:\.apply\s*\(\s*(?:null|undefined|this|String)?\s*,|\(\s*\.\.\.)\s*"
                     r"\[(?P<a>[\dxXa-fA-F,\s]*)\]\s*\)")
_SB_CARR = re.compile(r"(?s)^(?:new\s+(?:String|string)\s*\()?\s*(?:new\s+)?(?:char|Char|wchar_t)\s*\[\s*\d*\s*\]\s*"
                      r"(?:[A-Za-z_]\w*\s*\[\s*\d*\s*\]\s*)?=?\s*\{(?P<a>.*)\}\s*\)?$")
_SB_HEAD = re.compile(r"^\s*(?:(?:var|let|const|final|static|auto|my|our|local|Dim|string|String|str|char\s*\*|"
                      r"(?:std::)?string|StringBuilder|\[string\])\s+)*(?P<n>\$?[A-Za-z_]\w*)\s*(?:\[\s*\d*\s*\])?"
                      r"(?::\s*[\w\[\]]+)?\s*(?P<op>\+=|\.=|&=|\.\.=|=(?!=))\s*(?P<v>.+?)\s*;?\s*$", re.S)
_SB_OUT = re.compile(r"(?is)^\s*(?:print|println|puts|echo|console\.log|alert|document\.write|System\.out\.print(?:ln)?|"
                     r"Console\.Write(?:Line)?|Write-(?:Host|Output)|WScript\.Echo|MsgBox|printf)\s*(?:\((?P<a>.*)\)|"
                     r"(?P<b>[^()].*?))\s*;?\s*$")
_SB_APPEND = re.compile(r"\.(?:append|Append|AppendLine|concat|push|write|Write|add|Add)\s*\(")
_SB_STRUCT = re.compile(r"""(?ix)(?:chrw?\s*\(|\[char\]|fromCharCode|\(\s*char\s*\)|\.join\s*\(|-join|\bjoin\s*\(|
                        char\s*\[\s*\d*\s*\]|\bbytes\s*\(|^\s*[bB]['"]|(?:["'`]|\))\s*(?:\+|&|\.\.?|,)\s*(?:["'`(]|chr|\[)|
                        ["']\s+["']|\w\s*(?:\+|&)\s*["']|\.append|\+=|&=|\.=|\.\.=)""")


def _sb_pre(e):
    """Normalise the literal forms _fs_eval lacks; strip line continuations."""
    e = re.sub(r"\s*(?:\\|\s_)\r?\n", " ", e)
    e = _SB_CHARCAST.sub(lambda m: f"chr({m.group(1)})", e)
    e = _SB_FCC.sub(lambda m: f"String.fromCharCode({m.group('a')})", e)
    return e


def _sb_val(e, env, cx):
    """String value of one literal-only expression (+ char-array / JSON-list / bytes forms), or None."""
    e = _sb_pre(e).strip().rstrip(";").strip()
    if not e:
        return None
    m = _SB_CARR.match(e)
    if m:
        items = cx._fs_split(m.group("a"), cx._FS_COMMA)
        items = [i for i in items if i.strip()]
        if items and all(re.fullmatch(r"\s*(?:0[xX][0-9a-fA-F]+|\d+)\s*", i) for i in items):
            return cx._fs_ints(",".join(items))
        vals = [cx._fs_eval(i, env) for i in items]
        return None if not items or None in vals else "".join(vals)
    m = re.fullmatch(r"(?s)\[(?P<a>.*)\]", e)
    if m:   # JSON / Python / JS list of string literals (["N","i"]): joined in order
        items = [i for i in cx._fs_split(m.group("a"), cx._FS_COMMA) if i.strip()]
        if len(items) >= 2 and all(cx._FS_LIT.fullmatch(i.strip()) for i in items):
            vals = [cx._fs_eval(i, env) for i in items]
            return None if None in vals else "".join(vals)
        return None
    m = re.fullmatch(r"(?s)(?:bytes|bytearray)\s*\(\s*\[(?P<a>[\dxXa-fA-F,\s]+)\]\s*\)(?:\.decode\s*\([^)]*\))?", e)
    if m:
        return cx._fs_ints(m.group("a"))
    m = re.fullmatch(r"(?s)(?P<s>[rRuU]?[\"'][^\"']*[\"'])\.join\s*\(\s*\[?\s*chr\s*\(\s*(?P<v>[A-Za-z_]\w*)\s*\)\s*for\s+"
                     r"(?P=v)\s+in\s+[\[(](?P<a>[\dxXa-fA-F,\s]+)[\])]\s*\]?\s*\)", e)
    if m:
        sep = cx._fs_eval(m.group("s"), env)
        codes = [c for c in re.split(r"[\s,]+", m.group("a").strip()) if c]
        chars = cx._fs_ints(",".join(codes))
        return None if sep is None or chars is None else sep.join(chars)
    v = cx._fs_eval(e, env)
    if v is None and re.fullmatch(r"(?s)[bB][\"'].*[\"']", e):
        v = cx._fs_eval(e[1:], env)
    return v


def _sb_appends(t, env, cx):
    """StringBuilder / array-push chains: every `.append(x)` argument (+ a `new StringBuilder(x)` seed) in order."""
    out, n = [], 0
    m = re.search(r"new\s+StringBuilder\s*\(", t)
    a = cx._fs_args(t, m.end()) if m else None
    if a and a.strip():
        seed = _sb_val(a, env, cx)
        if seed is None:
            return None
        out.append(seed)
    for m in _SB_APPEND.finditer(t):
        a = cx._fs_args(t, m.end())
        if not a or len(cx._fs_split(a, cx._FS_COMMA)) != 1:
            return None
        v = _sb_val(a, env, cx)
        if v is None:
            return None
        out.append(v)
        n += 1
    return "".join(out) if n >= 2 else None


def strbuild_dec(t):
    """Whole text = source code that builds a string from literal pieces -> the built string, else None."""
    try:
        if isinstance(t, (bytes, bytearray)):
            t = bytes(t).decode("utf-8")
        if not isinstance(t, str) or not t.strip() or len(t) > 60000 or not re.search(r"[\"'`\[{(]", t):
            return None
        from lib import codec as cx
        t = t.strip()
        if not _SB_STRUCT.search(t):
            return None
        got = None
        if len(_SB_APPEND.findall(t)) >= 2:
            got = _sb_appends(t, {}, cx)
        if got is None:
            got = _sb_val(t, {}, cx)
        if got is None:
            m = _SB_OUT.match(t) or _SB_HEAD.match(t)
            if m:
                got = _sb_val(m.group("a") if "a" in m.re.groupindex and m.group("a") is not None else
                              m.group("b") if "b" in m.re.groupindex else m.group("v"), {}, cx)
        if got is None:   # statements: x = ..; x += ..; print(x)
            env, last, outv = {}, None, None
            stmts = [s for s in cx._fs_split(_sb_pre(t), re.compile(r"\s*(?:;|\r?\n)\s*")) if s.strip()]
            if len(stmts) < 2 or len(stmts) > 400:
                return None
            for s in stmts:
                if re.fullmatch(r"(?i)\s*(?:using\s.*|import\s.*|#.*|//.*|(?:public\s+)?(?:static\s+)?(?:void|class)\b.*|"
                                r"[{}]|(?:Dim|var|let|my|local)\s+\$?\w+|\$?\w+\s*=\s*new\s+StringBuilder\s*\(\s*\)|.*\bjoin\s*\(\s*\w+\s*\)|"
                                r"\w+\.(?:ToString|toString)\s*\(\s*\)|)\s*", s):
                    continue
                m = _SB_OUT.match(s)
                if m:
                    a = m.group("a") if m.group("a") is not None else m.group("b")
                    outv = _sb_val(a, env, cx)
                    if outv is None:
                        return None
                    continue
                m = _SB_HEAD.match(s)
                if not m:
                    return None
                k, op = m.group("n").lstrip("$"), m.group("op")
                v = _sb_val(m.group("v"), env, cx)
                if v is None:
                    return None
                if op != "=":
                    if k not in env:
                        return None
                    v = env[k] + v
                env[k], last = v, k
            got = outv if outv is not None else env.get(last)
        if not got or got == t or not got.replace("\n", " ").replace("\t", " ").isprintable():
            return None
        return got
    except Exception:   # noqa: BLE001
        return None


def strbuild_free(p):
    """Speculative Mastery-line decoder: one line of literal-only string-building source, leading indent kept."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        v = strbuild_dec(p)
        return [p[:len(p) - len(p.lstrip())] + v] if v and "\n" not in v else []
    except Exception:   # noqa: BLE001
        return []


def _sb_q(c, q='"'):
    return q + (c.replace("\\", "\\\\").replace(q, "\\" + q)) + q


def strbuild_enc(s, form="concat"):
    """Plain -> one string-building source form (per char unless the form is word-wise)."""
    w = re.findall(r"\S+\s*", s)
    if form == "concat":
        return " + ".join(_sb_q(x) for x in w)
    if form == "implicit":
        return " ".join(_sb_q(x, "'") for x in w)
    if form == "fromcharcode":
        return "String.fromCharCode(" + ",".join(str(ord(c)) for c in s) + ")"
    if form == "chr":
        return "+".join(f"chr({ord(c)})" for c in s)
    if form == "pschar":
        return "+".join(f"[char]{ord(c)}" for c in s)
    if form == "chararray":
        return "new char[]{" + ",".join(_sb_q(c, "'") for c in s) + "}"
    if form == "pyjoin":
        return "''.join([" + ", ".join(_sb_q(c, "'") for c in s) + "])"
    if form == "jsonlist":
        return json.dumps(list(s))
    if form == "bytes":
        return "b'" + "".join(f"\\x{b:02x}" for b in _u(s)) + "'"
    if form == "append":
        return "var sb = new StringBuilder();\n" + "".join(f"sb.append({_sb_q(x)});\n" for x in w) + "sb.toString();"
    return None


CANDIDATES += [(f"strbuild-{f}", (lambda f: lambda s: strbuild_enc(s, f))(f), strbuild_dec)
               for f in ("concat", "implicit", "fromcharcode", "chr", "pschar", "chararray", "pyjoin", "jsonlist",
                         "bytes", "append")]


# RESP (speculative, no day; Redis serialization protocol, the length-prefixed "string protocol" sibling of D24's
# netstrings): `*<n>` array, `$<len>` bulk string (len in UTF-8 bytes per spec, or chars), `+text` simple, `-err`,
# `:int`; RESP3 `=<len>` verbatim (`txt:` / `mkd:` 3-char format + ':' stripped), `_` null, `#t`/`#f`, `,` double,
# `(` bignum, `!` blob error, `%` map, `~` set, `>` push, `|` attribute (skipped). Lines end CRLF or bare LF (also the
# docs' literal `\r\n` escapes on one line). Reading = string leaves joined (or space-joined when one per word), else
# int leaves as char codes; the WHOLE text must be 1+ RESP values. Nodes reuse the tnetstring shape.
_RESP_LINE = {bytes: re.compile(rb"([^\r\n]*)\r?\n"), str: re.compile(r"([^\r\n]*)\r?\n")}
_RESP_NUM = re.compile(r"-1|0|[1-9][0-9]{0,8}")


def _resp_eol(b, j):
    """End of the CRLF / LF that must follow a length-prefixed payload at b[j:]; raises otherwise."""
    for nl in ("\r\n", "\n"):
        nl = nl.encode() if isinstance(b, bytes) else nl
        if b[j:j + len(nl)] == nl:
            return j + len(nl)
    if j == len(b):     # a final payload with its terminator stripped (copy-paste / .strip())
        return j
    raise ValueError("bulk terminator")


def _resp_parse(b, i, depth=0):
    """-> (node, end) for the RESP value at b[i:]; node = (',', text) / ('#', int) / ('~', None) / (']', [n]) /
    ('}', pairs) / ('|', None) attribute marker; raises ValueError on any malformation."""
    if depth > 32 or i >= len(b):
        raise ValueError("not RESP")
    t = b[i:i + 1]
    t = t.decode("latin-1") if isinstance(t, bytes) else t
    m = _RESP_LINE[type(b)].match(b, i + 1)
    if t not in "+-:$*=_#,(!%~>|" or not m:
        raise ValueError("not RESP")
    line = _bx_text(m.group(1))
    j = m.end()
    if t in "+-":
        return (",", line), j
    if t == ":":
        if not re.fullmatch(r"[+-]?[0-9]{1,30}", line):
            raise ValueError("int")
        return ("#", int(line)), j
    if t == "(":
        if not re.fullmatch(r"-?[0-9]{1,400}", line):
            raise ValueError("bignum")
        return ("#", int(line)), j
    if t == "_":
        if line:
            raise ValueError("null")
        return ("~", None), j
    if t == "#":
        if line not in ("t", "f"):
            raise ValueError("bool")
        return ("!", line == "t"), j
    if t == ",":
        float(line)
        return ("^", line), j
    if not _RESP_NUM.fullmatch(line):
        raise ValueError("length")
    n = int(line)
    if t in "$=!":
        if n < 0:
            if t != "$":
                raise ValueError("length")
            return ("~", None), j
        if j + n > len(b):
            raise ValueError("overrun")
        pay = _bx_text(b[j:j + n])
        if t == "=":
            if not re.match(r"[a-z]{3}:", pay):
                raise ValueError("verbatim format")
            pay = pay[4:]
        return (",", pay), _resp_eol(b, j + n)
    if n < 0:
        return ("~", None), j
    items = []
    for _ in range(n * (2 if t in "%|" else 1)):
        node, j = _resp_parse(b, j, depth + 1)
        items.append(node)
    if t == "|":    # attribute: metadata ahead of the real reply -- parse and drop
        return ("|", None), j
    if t == "%":
        return ("}", list(zip(items[0::2], items[1::2]))), j
    return ("]", [x for x in items if x[0] != "|"]), j


def _resp_top(b):
    """Whole buffer -> [node] (1+ RESP values, whitespace between), else None."""
    try:
        out, i = [], 0
        while True:
            while i < len(b) and b[i:i + 1].isspace():
                i += 1
            if i >= len(b):
                return [n for n in out if n[0] != "|"] or None
            node, i = _resp_parse(b, i)
            out.append(node)
    except (ValueError, UnicodeDecodeError, OverflowError, RecursionError, IndexError):
        return None


def _resp_unescape(t):
    """The docs' one-line form `*2\\r\\n$3\\r\\nfoo...` -> real line breaks (only when the text has no real ones)."""
    if "\n" in t.strip() or not re.search(r"\\r\\n|\\n", t):
        return None
    return t.replace("\\r\\n", "\r\n").replace("\\n", "\n").replace("\\r", "\r")


def resp_reads(t, _depth=0):
    """[(how, text)] readings of a whole-text RESP run, best first (slug / English-gated); [] when not one."""
    try:
        if isinstance(t, (bytes, bytearray)):
            t = bytes(t).decode("utf-8")
        if not isinstance(t, str) or len(t) > 200000 or not re.match(r"\s*[-+:$*=_#,(!%~>|]", t):
            return []
        t = t.strip(" \t")
        cands = [("", t)] + [("escaped-", u) for u in (_resp_unescape(t),) if u]
        tops = []
        for tag, txt in cands:
            txt = txt.lstrip()
            for unit, buf in (("bytes", txt.encode("utf-8")), ("chars", txt)):
                if unit == "chars" and txt.isascii():
                    continue
                top = _resp_top(buf)
                if top:
                    tops.append((tag + unit, top))
        reads = []
        for unit, top in tops:
            if len(top) == 1 and top[0][0] == "," and len(tops) and not re.match(r"\s*[$=]", t):
                # one bare simple string `+text` / `-ERR text`: only a cue when it is the WHOLE text on one line
                pass
            for keys in (False, True):
                lv = [x for n in top for x in _tn_leaves(n, keys)]
                strs = [v for g, v in lv if g == ","]
                if strs:
                    joined = "".join(strs)
                    reads.append((f"{unit}-strings" + ("-keys" if keys else ""), joined))
                    if not keys and len(strs) > 1 and all(s and not re.search(r"\s", s) for s in strs) \
                            and any(len(s) > 1 for s in strs):
                        reads.append((f"{unit}-words", " ".join(strs)))
                    if not keys and _depth < 3 and re.match(r"\s*[*$+=]", joined):
                        reads += [(f"{unit}-nested-{h}", x) for h, x in resp_reads(joined, _depth + 1)]
                    if not keys and not _ns_english(joined) and _depth < 3:
                        from lib import decode as _dc
                        whole = _dc.decode_chunk(joined, _nested=True)
                        if whole is not None:
                            reads.append((f"{unit}-strings-coded", whole))
                if not keys and lv and all(g == "#" for g, _v in lv) and all(0 < v < 0x110000 for _g, v in lv):
                    reads.append((f"{unit}-charcodes", "".join(chr(v) for _g, v in lv)))
        seen = set()
        reads = [r for r in reads if r[1] and r[1].isprintable() and not (r[1] in seen or seen.add(r[1]))
                 and (SLUG.search(r[1]) or _ns_english(r[1]))]
        return sorted(reads, key=lambda r: (not (SLUG.search(r[1]) and _TPL in r[1]), not SLUG.search(r[1]),
                                            not _ns_english(r[1])))
    except Exception:   # noqa: BLE001
        return []


def resp_dec(t):
    """Whole text = RESP value(s) -> its best slug / English-gated reading, else None."""
    r = resp_reads(t)
    return r[0][1] if r else None


def resp_free(p):
    """Speculative Mastery-line decoder: a one-line RESP fragment in the docs' escaped form (`*2\\r\\n$1\\r\\nN...`),
    or a single `$<len>`/`=<len>` bulk with its body on the same line; leading indent kept."""
    try:
        if not isinstance(p, str) or not re.match(r"\s*[*$=%~>]-?\d{1,9}(\\r)?\\n", p):
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return list(dict.fromkeys(lead + x for _h, x in resp_reads(p)))[:3]
    except Exception:   # noqa: BLE001
        return []


def resp_enc(s, form="chars", nl="\r\n", escaped=False):
    """Plain -> RESP: chars/words/tokens = array of bulk strings (1 char / word without its space / word + space),
    bulk = one `$` bulk, simple = `+text`, verbatim = RESP3 `=` txt:, codes = array of `:` ints."""
    def bulk(x):
        return f"${len(x.encode('utf-8'))}{nl}{x}{nl}"
    if form == "bulk":
        out = bulk(s)
    elif form == "simple":
        out = f"+{s}{nl}"
    elif form == "verbatim":
        out = f"={len(s.encode('utf-8')) + 4}{nl}txt:{s}{nl}"
    elif form == "codes":
        out = f"*{len(s)}{nl}" + "".join(f":{ord(c)}{nl}" for c in s)
    else:
        parts = list(s) if form == "chars" else s.split() if form == "words" else re.findall(r"\S+\s*", s)
        out = f"*{len(parts)}{nl}" + "".join(bulk(x) for x in parts)
    return out.replace("\r", "\\r").replace("\n", "\\n") if escaped else out


CANDIDATES += [(f"resp-{f}{'-lf' if nl == chr(10) else ''}{'-escaped' if e else ''}",
                (lambda f, nl, e: lambda s: resp_enc(s, f, nl, e))(f, nl, e), resp_dec)
               for f, nl, e in (("chars", "\r\n", False), ("words", "\r\n", False), ("tokens", "\r\n", False),
                                ("bulk", "\r\n", False), ("simple", "\r\n", False), ("verbatim", "\r\n", False),
                                ("codes", "\r\n", False), ("chars", "\n", False), ("words", "\n", False),
                                ("chars", "\r\n", True), ("words", "\r\n", True))]


_ASN1_STR = {0x0C: "utf-8", 0x12: "latin-1", 0x13: "latin-1", 0x14: "latin-1", 0x16: "latin-1", 0x19: "latin-1",
             0x1A: "latin-1", 0x1B: "latin-1", 0x1C: "utf-32-be", 0x1E: "utf-16-be", 0x04: None, 0x03: None}
_ASN1_PEM = re.compile(r"-----BEGIN ([A-Z0-9 ]+)-----\s*([A-Za-z0-9+/=\s]+?)\s*-----END \1-----")


def _asn1_tlv(b, p, depth, leaves):
    """Parse one BER TLV at b[p:], appending (tag, content) string/opaque leaves in order -> end offset, else None.
    Constructed (0x20) types recurse (definite or BER indefinite 0x80 ... 00 00); primitive non-string universal types
    (INTEGER, OID, NULL, BOOLEAN, times ...) are skipped; primitive context/application tags are kept as opaque."""
    n = len(b)
    if p + 2 > n or depth > 40:
        return None
    t0 = b[p]
    p += 1
    num = t0 & 0x1F
    if num == 0x1F:   # high tag number form
        num = 0
        for _ in range(4):
            if p >= n:
                return None
            num = (num << 7) | (b[p] & 0x7F)
            p += 1
            if not b[p - 1] & 0x80:
                break
        else:
            return None
    if p >= n:
        return None
    l0 = b[p]
    p += 1
    cons, cls = t0 & 0x20, t0 & 0xC0
    if l0 == 0x80:   # BER indefinite: constructed only, children until 00 00
        if not cons:
            return None
        while True:
            if p + 2 > n:
                return None
            if b[p] == 0 and b[p + 1] == 0:
                return p + 2
            p = _asn1_tlv(b, p, depth + 1, leaves)
            if p is None:
                return None
    if l0 & 0x80:
        k = l0 & 0x7F
        if not 1 <= k <= 4 or p + k > n:
            return None
        ln = int.from_bytes(b[p:p + k], "big")
        p += k
    else:
        ln = l0
    end = p + ln
    if end > n:
        return None
    if cons:
        while p < end:
            p = _asn1_tlv(b, p, depth + 1, leaves)
            if p is None or p > end:
                return None
        return end
    if t0 == 0 and ln == 0:
        return None   # a stray EOC outside an indefinite run
    if cls == 0 and num in _ASN1_STR:
        leaves.append((num, b[p:end]))
    elif cls == 0 and (num == 0 or num > 0x1E):
        return None
    elif cls:
        leaves.append((-1, b[p:end]))
    return end


def _asn1_walk(b):
    """[(tag, content)] when the WHOLE buffer is one or more complete TLVs whose first is constructed or a string
    type and that hold >= 1 non-empty string leaf, else None."""
    if not b or len(b) < 3 or not (b[0] & 0x20 or b[0] in _ASN1_STR):
        return None
    leaves, p = [], 0
    while p < len(b):
        p = _asn1_tlv(b, p, 0, leaves)
        if p is None:
            return None
    return leaves if any(v for _t, v in leaves) else None


def _asn1_text(tag, v, depth=0):
    """A string leaf's text: its declared charset; OCTET/BIT/opaque = encapsulated DER (recursed) or UTF-8, else None."""
    try:
        if tag == 0x03:
            if not v or v[0] > 7:
                return None
            v = v[1:]
        if tag in (0x04, 0x03, -1):
            sub = _asn1_walk(v) if depth < 4 and len(v) > 2 else None
            if sub:
                parts = [_asn1_text(t, x, depth + 1) for t, x in sub]
                if all(x is not None for x in parts):
                    return "".join(parts)
            return v.decode("utf-8")
        return v.decode(_ASN1_STR[tag])
    except (UnicodeDecodeError, ValueError, KeyError):
        return None


def _asn1_layers(t):
    """[(layer, bytes)] of a PEM block / hex / base64(url) / base32 line."""
    m = _ASN1_PEM.search(t)
    if m:
        try:
            return [("pem", base64.b64decode(re.sub(r"\s+", "", m.group(2)), validate=True))]
        except (binascii.Error, ValueError):
            return []
    return _lp_layers(t)


def asn1_reads(t):
    """[(how, text)] readings of an ASN.1 DER/BER TLV tree (under PEM / hex / b64 / b32): its string leaves in order,
    joined raw (or per-leaf / joined through the chunk codecs), crib first; [] when it is not one. Never raises."""
    try:
        if isinstance(t, (bytes, bytearray)):
            t = bytes(t).decode("utf-8")
        if not isinstance(t, str) or not t.strip() or len(t) > 120000:
            return []
        from lib import decode as _dc
        t, reads = t.strip(), []
        for layer, b in _asn1_layers(t):
            try:
                owned = b.decode("utf-8").isprintable()   # plain hex / base64 of text: those decoders own it
            except UnicodeDecodeError:
                owned = False
            lv = _asn1_walk(b)
            if not lv:
                continue
            pay = [_asn1_text(tag, v) for tag, v in lv]
            if any(x is None for x in pay):
                continue
            got = []
            _lp_join(pay, f"{layer}-asn1", got, _dc)
            if len(pay) > 1 and not got:
                _lp_join([" ".join(pay)], f"{layer}-asn1-spaced", got, _dc)
            reads += [r for r in got if not owned or (SLUG.search(r[1]) and _TPL in r[1])]
        seen = set()
        reads = [r for r in reads if r[1] != t and not (r[1] in seen or seen.add(r[1]))]
        return sorted(reads, key=lambda r: (not (SLUG.search(r[1]) and _TPL in r[1]), not _crib_piece(r[1]),
                                            not _ns_english(r[1]), -_texty(r[1])))
    except Exception:   # noqa: BLE001
        return []


def asn1_dec(t):
    """Whole text = an ASN.1 DER/BER TLV tree -> its best reading, else None."""
    r = asn1_reads(t)
    return r[0][1] if r else None


def asn1_free(p):
    """Speculative Mastery-line decoder: a fragment that is a whole ASN.1 TLV tree, leading indent kept."""
    try:
        if not isinstance(p, str) or not p.strip():
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return list(dict.fromkeys(lead + x for _h, x in asn1_reads(p) if x and x.isprintable()))[:3]
    except Exception:   # noqa: BLE001
        return []


def _asn1_len(n):
    if n < 0x80:
        return bytes([n])
    k = (n.bit_length() + 7) // 8
    return bytes([0x80 | k]) + n.to_bytes(k, "big")


def asn1_enc(s, form="seq-chars", fmt="hex", tag=0x0C):
    """Plain -> ASN.1: seq-chars / seq-words = DER SEQUENCE of one `tag` string per char / word (+ its space),
    one = a single `tag` string (0x04 = OCTET STRING), ber-chars = BER indefinite SEQUENCE of chars; as hex / spaced
    hex / b64 / PEM."""
    def tlv(tg, v):
        return bytes([tg]) + _asn1_len(len(v)) + v
    if form == "one":
        der = tlv(tag, s.encode("utf-8"))
    else:
        parts = list(s) if form in ("seq-chars", "ber-chars") else re.findall(r"\S+\s*", s)
        body = b"".join(tlv(tag, x.encode("utf-8")) for x in parts)
        der = b"\x30\x80" + body + b"\x00\x00" if form == "ber-chars" else tlv(0x30, body)
    if fmt == "hex":
        return der.hex()
    if fmt == "hexsp":
        return " ".join(f"{x:02x}" for x in der)
    b64 = base64.b64encode(der).decode()
    if fmt == "pem":
        return "-----BEGIN DATA-----\n" + "\n".join(b64[i:i + 64] for i in range(0, len(b64), 64)) + "\n-----END DATA-----"
    return b64


CANDIDATES += [(f"asn1-{f}-{x}{'' if g == 0x0C else f'-{g:02x}'}",
                (lambda f, x, g: lambda s: asn1_enc(s, f, x, g))(f, x, g), asn1_dec)
               for f, x, g in (("seq-chars", "hex", 0x0C), ("seq-chars", "b64", 0x0C), ("seq-chars", "hexsp", 0x0C),
                               ("seq-words", "hex", 0x0C), ("seq-words", "b64", 0x0C), ("seq-chars", "hex", 0x16),
                               ("seq-words", "b64", 0x04), ("one", "hex", 0x04), ("one", "b64", 0x0C),
                               ("one", "pem", 0x04), ("ber-chars", "hex", 0x0C), ("ber-chars", "b64", 0x0C))]

# DELIMITED-FIELD FRAMING (speculative, no day; the delimiter-ESCAPING sibling of D24's netstrings: the payload holds
# the delimiter, escaped instead of counted). One char or word per field: CSV `"N","i",""""` (RFC 4180 doubled quote,
# QUOTE_ALL or QUOTE_MINIMAL `N,i,","`, `;` / `|` / tab delimiters, `\"` backslash quoting, blanks after the delimiter),
# TSV whose bare fields carry `\t` `\n` `\\` escapes (PostgreSQL COPY / MySQL), Lisp char lists `(#\N #\i #\space)`
# (Scheme / CL `#\Space` `#\ ` `#\x41` `#\U+0041` / Unicode names, `#(..)` vectors, Clojure `[\N \i \space]`), YAML flow
# sequences `[N, i, ' ', '''']` (plain / 'single' with '' / "double" with backslash escapes). Fields join with '' (or ' '
# for space-free words); a reading must parse the WHOLE text and read as English / a piece of the warmups sentence.
_DF_NAMES = {"space": " ", "newline": "\n", "linefeed": "\n", "tab": "\t", "return": "\r", "nul": "\0", "null": "\0",
             "alarm": "\a", "backspace": "\b", "delete": "\x7f", "rubout": "\x7f", "del": "\x7f", "escape": "\x1b",
             "esc": "\x1b", "altmode": "\x1b", "page": "\f", "formfeed": "\f", "comma": ","}
_DF_TSV = {"t": "\t", "n": "\n", "r": "\r", "\\": "\\", "0": "\0", "b": "\b", "f": "\f", "v": "\v", "N": None}
_DF_YDQ = {"0": "\0", "a": "\a", "b": "\b", "t": "\t", "\t": "\t", "n": "\n", "v": "\v", "f": "\f", "r": "\r",
           "e": "\x1b", " ": " ", '"': '"', "/": "/", "\\": "\\", "N": "\x85", "_": "\xa0", "L": " ", "P": " "}


def _df_csv_split(t, sep, bs=False, sp=False, tsv=False):
    """RFC 4180 fields of the whole `t` -> [(quoted, value)] (a line break ends a field like `sep`), else None.
    bs: `\\"` / `\\\\` inside quotes instead of doubled quotes; sp: blanks around a field ignored; tsv: bare fields
    unescape `\\t \\n \\\\`."""
    f, i, n = [], 0, len(t)
    while True:
        j = i
        while sp and j < n and t[j] == " ":
            j += 1
        if j < n and t[j] == '"':
            k, buf = j + 1, []
            while True:
                if k >= n:
                    return None
                c = t[k]
                if bs and c == "\\" and k + 1 < n:
                    buf.append(t[k + 1])
                    k += 2
                elif c == '"' and not bs and t[k + 1:k + 2] == '"':
                    buf.append('"')
                    k += 2
                elif c == '"':
                    k += 1
                    break
                else:
                    buf.append(c)
                    k += 1
            while sp and k < n and t[k] == " ":
                k += 1
            f.append((True, "".join(buf)))
        else:
            k = j
            while k < n and t[k] != sep and t[k] not in "\r\n":
                if t[k] == '"':
                    return None             # a bare quote inside an unquoted field
                k += 1
            v = t[j:k].rstrip(" ") if sp else t[i:k]
            if tsv:
                parts = re.split(r"(\\.)", v)
                if any(p[:1] == "\\" and _DF_TSV.get(p[1:]) is None for p in parts) or "\\" in parts[-1]:
                    return None
                v = "".join(_DF_TSV[p[1:]] if p[:1] == "\\" else p for p in parts)
            f.append((False, v))
        if k >= n:
            return f
        if t[k] == sep:
            i = k + 1
            continue
        if t[k] not in "\r\n":
            return None                     # junk after a closing quote
        k += 2 if t[k:k + 2] == "\r\n" else 1
        if not t[k:].strip("\r\n"):
            return f                        # trailing record terminator
        i = k


def _df_csv(t):
    """[(form, [field], strict)] for every CSV / TSV dialect under which the whole text is a field run of one char
    (or one quoted / space-free word) per field; strict = bare multi-char fields (needs a template-piece reading)."""
    out = []
    for sep in _DF_SEPS:
        if t.count(sep) < 2:
            continue
        for bs, sp, tsv in ((False, False, True), (False, False, False), (True, False, False), (False, True, False)):
            if (tsv and sep != "\t") or (sp and sep == "\t") or (sep == "\t" and not tsv and out and "tsv" in out[-1][0]):
                continue
            if (bs and '\\"' not in t) or (tsv and "\\" not in t):
                continue
            f = _df_csv_split(t, sep, bs, sp, tsv)
            if not f or len(f) < 3:
                continue
            if f[-1] == (False, "") and t.rstrip("\r\n").endswith(sep):
                f = f[:-1]                  # trailing delimiter
            if any(v == "" for _q, v in f):
                continue
            bare = [v for q, v in f if not q]
            if any(len(v) > 1 and not re.fullmatch(r"\S+ ?", v) for v in bare):
                continue
            out.append((f"csv{'-bs' if bs else ''}{'-sp' if sp else ''}{'-tsv' if tsv else ''}-{ord(sep):02x}",
                        [v for _q, v in f], any(len(v) > 1 for v in bare)))
    return out


_DF_SEPS = (",", "\t", ";", "|")
_DF_LTOK = re.compile(r"(?s)(#\\|\\)(.)([A-Za-z0-9_+-]*)")


def _df_char(c, rest, clj):
    """One Lisp char literal body -> its char, else None."""
    if not rest:
        return c
    name = c + rest
    lo = name.lower()
    if lo in _DF_NAMES:
        return _DF_NAMES[lo]
    m = re.fullmatch(r"(?i)(?:x|u\+?)([0-9a-f]{1,6})", name) if not clj else re.fullmatch(r"u([0-9a-fA-F]{4})", name)
    if m and int(m.group(1), 16) < 0x110000:
        return chr(int(m.group(1), 16))
    m = re.fullmatch(r"o([0-7]{1,3})", name) if clj else None
    if m:
        return chr(int(m.group(1), 8))
    try:
        return unicodedata.lookup(name.replace("_", " "))
    except (KeyError, ValueError):
        return None


def _df_lisp(t):
    """[(form, [char])] when the whole text is a Lisp / Clojure list, vector or bare run of char literals."""
    m = re.fullmatch(r"(?s)\s*['`]?(#?\(|\[)(.*)([)\]])\s*", t)
    body, form = (m.group(2), "list") if m and (m.group(1)[-1] + m.group(3)) in ("()", "[]") else (t, "bare")
    out, i, n, kinds = [], 0, len(body), set()
    while True:
        while i < n and (body[i].isspace() or body[i] == ","):
            i += 1
        if i >= n:
            break
        mt = _DF_LTOK.match(body, i)
        if not mt:
            return []
        kinds.add(mt.group(1))
        ch = _df_char(mt.group(2), mt.group(3), mt.group(1) == "\\")
        i = mt.end()
        if ch is None or (i < n and not (body[i].isspace() or body[i] in ",#\\")):
            return []
        out.append(ch)
    if len(out) < 3 or len(kinds) != 1:
        return []
    return [(("scheme-" if "#\\" in kinds else "clojure-") + form, out)]


def _df_yq(body, i, q):
    """Quoted YAML scalar starting at body[i] == q -> (value, end) or None (line folding: break + indent = ' ')."""
    k, buf, n = i + 1, [], len(body)
    while k < n:
        c = body[k]
        if q == "'" and c == "'":
            if body[k + 1:k + 2] == "'":
                buf.append("'")
                k += 2
                continue
            return "".join(buf), k + 1
        if q == '"' and c == '"':
            return "".join(buf), k + 1
        if q == '"' and c == "\\":
            e = body[k + 1:k + 2]
            if e in _DF_YDQ:
                buf.append(_DF_YDQ[e])
                k += 2
                continue
            m = re.compile(r"x([0-9a-fA-F]{2})|u([0-9a-fA-F]{4})|U([0-9a-fA-F]{8})").match(body, k + 1)
            if not m or int(m.group(0)[1:], 16) >= 0x110000:
                return None
            buf.append(chr(int(m.group(0)[1:], 16)))
            k = m.end()
            continue
        if c in "\r\n":
            m = re.compile(r"[ \t]*(?:\r?\n[ \t]*)+").match(body, k)
            while buf and buf[-1] in " \t":
                buf.pop()
            nl = m.group(0).count("\n") - 1
            buf.append("\n" * nl if nl else " ")
            k = m.end()
            continue
        buf.append(c)
        k += 1
    return None


def _df_yaml(t):
    """[(form, [field])] when the whole text is a YAML flow sequence of scalars (>= 3)."""
    s = t.strip()
    if len(s) < 7 or s[0] != "[" or s[-1] != "]":
        return []
    body, out, i, quoted = s[1:-1], [], 0, False
    n = len(body)
    while True:
        while i < n and body[i].isspace():
            i += 1
        if i >= n:
            break
        if body[i] in "'\"":
            r = _df_yq(body, i, body[i])
            if r is None:
                return []
            v, i = r
            quoted = True
        else:
            m = re.compile(r"[^,\[\]{}]+").match(body, i)
            if not m or body[i] in "#&*!|>%@`" or re.match(r"-\s|\?\s|:\s", body[i:i + 2] + " "):
                return []
            v, i = m.group(0).strip(), m.end()
            if not v or ": " in v or " #" in v or re.fullmatch(r"(?i)[-+]?(?:\d[\d_]*(?:\.\d*)?(?:e[-+]?\d+)?|0x[0-9a-f]+|"
                                                               r"0o[0-7]+|\.\d+|\.inf|\.nan|~|null)", v):
                return []           # a YAML number / null is not a string field (char codes stay the char-code decoders')
            v = re.sub(r"\s*\n\s*", " ", v)
        out.append(v)
        while i < n and body[i].isspace():
            i += 1
        if i < n:
            if body[i] != ",":
                return []
            i += 1
    if len(out) < 3:
        return []
    return [("yaml-flow" + ("" if quoted else "-plain"), out)]


def _df_ok(s, strict=False):
    if not s or not s.replace("\n", " ").replace("\t", " ").isprintable() or not re.search(r"[A-Za-z]{2}", s):
        return False
    s = s.replace("\n", " ").replace("\t", " ")
    if strict:
        return bool((SLUG.search(s) and _TPL in s) or _tc_piece(s))   # bare words: netstring / chunk frames split on ','
    return _ns_english(s)


def delim_reads(t):
    """[(how, text)] readings of a whole-text delimited field run (CSV / TSV / Lisp chars / YAML flow), best first."""
    try:
        if isinstance(t, (bytes, bytearray)):
            t = bytes(t).decode("utf-8")
        if not isinstance(t, str) or not t.strip() or len(t) > 200000:
            return []
        from lib import decode as _dc
        t = t.strip("\r\n")
        runs = [(h, f, False) for h, f in _df_lisp(t) + _df_yaml(t)]
        if not re.fullmatch(r"\s*\[.*\]\s*", t, re.S) or not runs:
            runs += _df_csv(t)
        reads = []
        for how, fields, strict in runs:
            joined = "".join(fields)
            if _df_ok(joined, strict):
                reads.append((how, joined))
            if len(fields) >= 3 and all(len(x) > 1 and not re.search(r"\s", x) for x in fields):
                sp = " ".join(fields)
                if _df_ok(sp, strict):
                    reads.append((how + "-spaced", sp))
            if not strict and not _ns_english(joined) and len(joined) >= 4:
                whole = _dc.decode_chunk(joined, _nested=True)      # fields carrying one strict chunk codec
                if whole is not None and _df_ok(whole):
                    reads.append((how + "-joined", whole))
        seen = set()
        reads = [r for r in reads if not (r[1] in seen or seen.add(r[1]))]
        return sorted(reads, key=lambda r: (not (SLUG.search(r[1]) and _TPL in r[1]), not _ns_english(r[1])))
    except Exception:   # noqa: BLE001
        return []


def delim_dec(t):
    """Whole text = a delimited one-char/word-per-field run -> its best reading, else None."""
    r = delim_reads(t)
    return r[0][1] if r else None


def delim_free(p):
    """Speculative Mastery-line decoder: a fragment that is a whole delimited field run, leading indent kept."""
    try:
        if not isinstance(p, str) or not p.strip() or not re.search(r"[\"',\t;|\[\\]", p):
            return []
        lead = p[:len(p) - len(p.lstrip())]
        return list(dict.fromkeys(lead + x for _h, x in delim_reads(p) if x and x.isprintable()))[:3]
    except Exception:   # noqa: BLE001
        return []


def _df_yaml_scalar(c):
    return c if re.fullmatch(r"[A-Za-z][A-Za-z]*", c) and c.lower() not in (
        "y", "n", "yes", "no", "on", "off", "true", "false", "null") else "'" + c.replace("'", "''") + "'"


def delim_enc(s, form="csv"):
    """Plain -> one delimited-field form (one char per field; *-words = one word incl. its space per field)."""
    w = re.findall(r"\S+\s*", s)
    cq = lambda x: '"' + x.replace('"', '""') + '"'   # noqa: E731
    if form == "csv":
        return ",".join(cq(c) for c in s)
    if form == "csv-min":
        return ",".join(cq(c) if c in ',"\r\n' else c for c in s)
    if form == "csv-words":
        return ",".join(cq(x) for x in w)
    if form == "csv-semi":
        return ";".join(cq(c) for c in s)
    if form == "csv-bs":
        return ", ".join('"' + c.replace("\\", "\\\\").replace('"', '\\"') + '"' for c in s)
    if form == "tsv":
        return "\t".join({"\t": "\\t", "\n": "\\n", "\r": "\\r", "\\": "\\\\"}.get(c, c) for c in s)
    if form == "scheme":
        return "(" + " ".join("#\\" + {" ": "space", "\n": "newline", "\t": "tab"}.get(c, c) for c in s) + ")"
    if form == "cl":
        return "(" + " ".join("#\\" + {" ": "Space", "\n": "Newline", "\t": "Tab"}.get(c, c) for c in s) + ")"
    if form == "clojure":
        return "[" + " ".join("\\" + {" ": "space", "\n": "newline", "\t": "tab"}.get(c, c) for c in s) + "]"
    if form == "yaml":
        return "[" + ", ".join(_df_yaml_scalar(c) for c in s) + "]"
    if form == "yaml-words":
        return "[" + ", ".join(_df_yaml_scalar(x) for x in w) + "]"
    return None


CANDIDATES += [(f"delim-{f}", (lambda f: lambda s: delim_enc(s, f))(f), delim_dec)
               for f in ("csv", "csv-min", "csv-words", "csv-semi", "csv-bs", "tsv", "scheme", "cl", "clojure", "yaml",
                         "yaml-words")]



# Unicode character NAMES, one per character ("every character has a name"): a `, ; | / tab newline`-separated list
# (`LATIN CAPITAL LETTER N, LATIN SMALL LETTER I, SPACE, ..`, any case, aliases / abbreviations like `LF`, `NBSP`
# allowed: unicodedata.lookup takes them), a run of Python/Perl `\N{NAME}` / `\N{U+4E}` escapes, `U+004E LATIN
# CAPITAL LETTER N` lines (uniname / charnames style) or raw UnicodeData.txt lines (`004E;LATIN CAPITAL LETTER N;Lu;..`),
# or names separated by single spaces only (segmented by the longest name that resolves). The WHOLE fragment must resolve.
_UN_ESC = re.compile(r"\\N\{([^{}\n]{1,90})\}")
_UN_CP = re.compile(r"(?i)^(?:U\+|0x)?([0-9a-f]{4,6})(?:\s*[;:\t=]\s*|\s+-?\s*|$)(.*)$")
_UN_SPLIT = ("\n", ",", ";", "|", " / ", "\t")


def _un_name(n):
    """One character name (or alias / abbreviation, any case, `_` for space) -> its char(s), else None."""
    n = n.strip().strip("\"'`{}<>[]").strip()
    if not n or len(n) > 90 or not re.fullmatch(r"[A-Za-z0-9 _()+\-]+", n):
        return None
    for x in (n, n.replace("_", " "), re.sub(r"\s*\([^()]*\)$", "", n)):
        x = re.sub(r"\s+", " ", x).strip()
        if not x:
            continue
        m = re.fullmatch(r"(?i)U\+([0-9a-f]{1,6})", x)
        if m:
            v = int(m.group(1), 16)
            return chr(v) if v < 0x110000 and not 0xD800 <= v < 0xE000 else None
        try:
            return unicodedata.lookup(x)
        except (KeyError, ValueError):
            pass
    return None


def _un_tok(t):
    """One list token: `\\N{..}`, `U+XXXX NAME` / UnicodeData line (name and code must agree), or a bare name."""
    t = t.strip()
    m = _UN_ESC.fullmatch(t)
    if m:
        return _un_name(m.group(1))
    m = _UN_CP.match(t)
    if m and (t[:2].upper() in ("U+", "0X") or ";" in t or m.group(2).strip()) and not _un_name(t):
        v = int(m.group(1), 16)
        if v >= 0x110000 or 0xD800 <= v < 0xE000:
            return None
        rest = m.group(2).split(";")[0].strip() if ";" in m.group(2) and t.count(";") >= 2 else m.group(2).strip()
        if not rest or rest.startswith("<"):   # `<control>` / `<CJK Ideograph..>`: the code point alone
            return chr(v)
        return chr(v) if _un_name(rest) == chr(v) else None
    return _un_name(t)


def _un_words(t):
    """Space-only separated names -> chars (longest resolving name first, the whole run must segment), else None."""
    w = t.split()
    if not 2 <= len(w) <= 4000 or not all(re.fullmatch(r"[A-Za-z0-9\-]+", x) for x in w):
        return None
    n, best = len(w), {len(w): ""}
    for i in range(n - 1, -1, -1):
        for j in range(min(n, i + 12), i, -1):
            if j in best:
                c = _un_name(" ".join(w[i:j]))
                if c:
                    best[i] = c + best[j]
                    break
    return best.get(0)


def _un_ok(s, k):
    return s if s and k >= 3 and all(c.isprintable() or c in "\t\n\r" for c in s) else None


def names_dec(t):
    """Unicode character names -> text, None unless the WHOLE fragment (one pair of quotes allowed) resolves."""
    try:
        if not isinstance(t, str):
            return None
        t = t.strip()
        if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
            t = t[1:-1].strip()
        if not t or len(t) > 400000 or not re.search(r"[A-Za-z]{3}", t):
            return None
        esc = list(_UN_ESC.finditer(t))
        if esc:
            gaps = [t[a.end():b.start()] for a, b in zip(esc, esc[1:])]
            if t[:esc[0].start()].strip() or t[esc[-1].end():].strip() or any(g.strip(" \t\r\n,;") for g in gaps):
                return None
            cs = [_un_name(m.group(1)) for m in esc]
            if None in cs:
                return None
            keep = not any(c.isspace() for c in cs) and any(gaps) and not all(gaps)
            return _un_ok("".join(c + (" " if keep and i < len(gaps) and re.search(r"\s", gaps[i]) else "")
                                  for i, c in enumerate(cs)), len(cs))
        if "\\" in t:
            return None
        if re.match(r"(?i)U\+[0-9a-f]{4,6}\b", t) and "\n" not in t:   # `U+004E NAME U+0069 NAME ..` on one line
            toks = re.split(r"(?i)[\s,;|]*(?=\bU\+[0-9a-f]{4,6}\b)", t)
            toks = [x for x in toks if x.strip()]
            cs = [_un_tok(x.strip(" ,;|")) for x in toks]
            if len(toks) > 1 and None not in cs:
                return _un_ok("".join(cs), len(cs))
        for sep in _UN_SPLIT:
            if sep not in t:
                continue
            toks = t.split(sep)
            if sep == "\n" or not toks[-1].strip():
                toks = [x for x in toks if x.strip()] if sep == "\n" else toks[:-1]
            if sep == "\n":
                out = []
                for x in toks:   # one name / code line, or a line that is itself a list
                    c = _un_tok(x)
                    if c is None:
                        sub = names_dec(x) if len(x.strip()) > 1 else None
                        if sub is None:
                            out = None
                            break
                        c = sub
                    out.append(c)
                if out is not None:
                    return _un_ok("".join(out), len(t.split()) if len(out) < 3 else len(out))
                continue
            if sep == ";" and _UN_CP.match(t.strip()) and t.count(";") >= 2 and _un_tok(t):   # one UnicodeData line
                continue
            cs = [_un_tok(x) for x in toks]
            if toks and None not in cs:
                return _un_ok("".join(cs), len(cs))
        return _un_ok(_un_words(t), len(t.split()) // 2)
    except Exception:   # noqa: BLE001
        return None


def names_enc(s, form="comma"):
    """Plain -> its Unicode character names (`comma` `newline` `space` `lower` `esc` `uplus` `unicodedata`)."""
    ns = [unicodedata.name(c, None) for c in s]
    if None in ns:
        return None
    if form == "esc":
        return "".join(f"\\N{{{n}}}" for n in ns)
    if form == "uplus":
        return "\n".join(f"U+{ord(c):04X} {n}" for c, n in zip(s, ns))
    if form == "unicodedata":
        return "\n".join(f"{ord(c):04X};{n};{unicodedata.category(c)};{unicodedata.combining(c)};"
                         f"{unicodedata.bidirectional(c)};;;;;N;;;;;" for c, n in zip(s, ns))
    if form == "lower":
        return ", ".join(ns).lower()
    return {"comma": ", ", "newline": "\n", "space": " "}[form].join(ns)


def names_free(p):
    """Speculative Mastery-line decoder: a fragment that is wholly character names, leading indent kept."""
    if not isinstance(p, str) or len(re.findall(r"[A-Za-z]{3,}", p)) < 2:
        return []
    d = names_dec(p)
    return [p[:len(p) - len(p.lstrip())] + d] if d else []


CANDIDATES += [(f"charnames-{f}", (lambda f: lambda s: names_enc(s, f))(f), names_dec)
               for f in ("comma", "newline", "space", "lower", "esc", "uplus", "unicodedata")]


# Code-point notation knobs on D25 `U+004E`: short / lowercase `u+4e`, `\u{4E}` (ES6/Rust/Swift), `\x{4E}` (Perl),
# `\N{U+004E}` (Perl), `\U0001F600`, `\u004E`, `%u004E`, `&#x4E;` / `&#78;`, C-style `0x4E` / `0d78` / `0o116` /
# `0b1001110`; radix from the prefix. Tokens adjacent or separated by whitespace , ; -- the WHOLE text must tokenise.
# A digit is never the `0` of the next `0x`/`0d`/`0o`/`0b` prefix, so `0x4e0x69` splits. Unbraced `\xHH` / `0xHH`
# runs that read as UTF-8 BYTES (a value >= 0x80, all <= 0xFF, valid UTF-8) are byte dumps: left to hex/char-code.
_CPA_TOK = re.compile(
    r"\\N\{[Uu]\+([0-9A-Fa-f]{1,6})\}|\\[ux]\{([0-9A-Fa-f]{1,6})\}|[Uu]\+([0-9A-Fa-f]{1,6})|\\U([0-9A-Fa-f]{8})"
    r"|\\u([0-9A-Fa-f]{4})|%[uU]([0-9A-Fa-f]{4})|&#[xX]([0-9A-Fa-f]{1,6});?|&#([0-9]{1,7});?"
    r"|\\x([0-9A-Fa-f]{2})|0[xX]((?:[0-9A-Fa-f](?![xX])){1,6})|0[dD]((?:[0-9](?![dD])){1,7})"
    r"|0[oO]((?:[0-7](?![oO])){1,8})|0[bB]((?:[01](?![bB])){1,21})")
_CPA_RADIX = (16, 16, 16, 16, 16, 16, 16, 10, 16, 16, 10, 8, 2)
_CPA_BYTEY = (8, 9)     # groups of the unbraced \xHH / 0xHH forms (byte-dump shaped)
_CPA_FULL = re.compile(r"(?:(?:" + _CPA_TOK.pattern + r")|[\s,;])+")


def codepoints_any(t):
    """Any code-point notation run (see above) -> text, None unless the WHOLE fragment (one pair of quotes allowed)
    tokenises. Whitespace gaps are separators when every pair is gapped or a token encodes whitespace, else literal
    word spaces (as ucp_dec). Never raises."""
    try:
        if not isinstance(t, str):
            return None
        t = t.strip()
        if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
            t = t[1:-1].strip()
        if not t or len(t) > 200000 or not _CPA_FULL.fullmatch(t):
            return None
        toks = list(_CPA_TOK.finditer(t))
        if len(toks) < 2:
            return None
        vals, bytey = [], True
        for m in toks:
            k = next(i for i, g in enumerate(m.groups()) if g)
            vals.append(int(m.group(k + 1), _CPA_RADIX[k]))
            bytey = bytey and k in _CPA_BYTEY
        if bytey and max(vals) >= 0x80 and max(vals) <= 0xFF:
            try:
                bytes(vals).decode("utf-8")
                return None
            except UnicodeDecodeError:
                pass
        gaps = [t[a.end():b.start()] for a, b in zip(toks, toks[1:])]
        keep = not any(v <= 0x10FFFF and chr(v).isspace() for v in vals) and any(gaps) and not all(gaps)
        out = []
        for i, v in enumerate(vals):
            out.append(v)
            if keep and i < len(gaps) and re.search(r"\s", gaps[i]):
                out.append(32)
        return _ucp_str(out)
    except Exception:   # noqa: BLE001
        return None


_CPA_FMT = {"u+short": "U+{:X}", "u+lower": "u+{:04x}", "u+short-lower": "u+{:x}", "\\u{}": "\\u{{{:X}}}",
            "\\x{}": "\\x{{{:x}}}", "\\N{U+}": "\\N{{U+{:04X}}}", "0x": "0x{:X}", "0d": "0d{:d}", "0o": "0o{:o}",
            "0b": "0b{:b}", "&#x": "&#x{:X};", "&#": "&#{:d};"}


def codepoints_enc(s, fmt="u+short", sep=" "):
    return sep.join(_CPA_FMT[fmt].format(ord(c)) for c in s)


def codepoints_free(p):
    d = codepoints_any(p)
    return [p[:len(p) - len(p.lstrip())] + d] if d else []


CANDIDATES += [(f"cp-{f}" + ("" if sep == " " else "-adjacent"),
                (lambda f, sep: lambda s: codepoints_enc(s, f, sep))(f, sep), codepoints_any)
               for f in _CPA_FMT for sep in (" ", "") if not (sep == "" and f.startswith("&#"))]   # = D8 html&#n;


# ------------------------------------------------- escape soup: every character in a randomly chosen notation
# Time Trial / Mastery mutation of the D7 url%xx / D8 html&#n; / D9 \uXXXX / D25 U+XXXX codecs: each char (or each
# word) in its own notation -- URL %xx (byte) / %uXXXX, HTML &#N; / &#xH; / &name;, \uXXXX, \UXXXXXXXX, \u{..},
# \x{..}, \N{U+..}, \xNN (byte), \NNN octal (byte), U+XXXX, 0xNN / 0dNN / 0oNN / 0bNN. The WHOLE text must tokenise
# (separator runs of whitespace or one , ; | between tokens); a DP picks the split with the fewest non-ASCII chars
# (so `U+004E0x69` / `0x4e0d105` split right). Per-token radix; consecutive byte tokens are one UTF-8 run (latin-1
# when invalid); \uXXXX / %uXXXX surrogate halves pair. Gaps follow ucp_dec's literal-space rule.
_SOUP_KINDS = (   # (prefix regex, digit class, min, max, radix, suffix, unit) unit: c code point, b byte, u UTF-16
    (r"&#[xX]", "0-9A-Fa-f", 1, 6, 16, ";?", "h"), (r"&#", "0-9", 1, 7, 10, ";?", "h"),
    (r"\\N\{[Uu]\+", "0-9A-Fa-f", 1, 6, 16, r"\}", "c"), (r"\\[ux]\{", "0-9A-Fa-f", 1, 6, 16, r"\}", "c"),
    (r"\\U", "0-9A-Fa-f", 8, 8, 16, "", "c"), (r"\\u", "0-9A-Fa-f", 4, 4, 16, "", "u"),
    (r"%[uU]", "0-9A-Fa-f", 4, 4, 16, "", "u"), (r"%", "0-9A-Fa-f", 2, 2, 16, "", "b"),
    (r"\\x", "0-9A-Fa-f", 2, 2, 16, "", "b"), (r"\\", "0-7", 3, 3, 8, "", "b"),
    (r"[Uu]\+", "0-9A-Fa-f", 1, 6, 16, "", "c"), (r"0[xX]", "0-9A-Fa-f", 1, 6, 16, "", "c"),
    (r"0[dD]", "0-9", 1, 7, 10, "", "c"), (r"0[oO]", "0-7", 1, 8, 8, "", "c"), (r"0[bB]", "01", 1, 21, 2, "", "c"))
_SOUP_RX = [(re.compile(f"{p}([{d}]{{{lo},{hi}}})({s})"), lo, r, u) for p, d, lo, hi, r, s, u in _SOUP_KINDS]
_SOUP_ENT = re.compile(r"&([A-Za-z][A-Za-z0-9]{1,31});")
_SOUP_SEP = re.compile(r"\s*[,;|]\s*|\s+")


def _soup_opts(t, i):
    """[(end, unit, value)] for every escape token starting at t[i] (every digit count, longest first)."""
    out = []
    m = _SOUP_ENT.match(t, i)
    if m:
        v = html.entities.html5.get(m.group(1) + ";")
        if v and len(v) == 1:
            out.append((m.end(), "c", ord(v)))
    for rx, lo, radix, unit in _SOUP_RX:
        m = rx.match(t, i)
        if not m:
            continue
        ds, a = m.group(1), m.start(1)
        for n in range(len(ds), lo - 1, -1):
            v = int(ds[:n], radix)
            if v > 0x10FFFF:
                continue
            end = a + n
            if n == len(ds) and m.group(2):
                out.append((m.end(), unit, v))   # with the ';' terminator
            out.append((end, unit, v))
    return out


def _soup_cost(unit, v):
    return 0 if (32 <= v < 127 or v in (9, 10, 13)) else 1


def escsoup_dec(t):
    """Mixed escape notation (see above) -> text, None unless the WHOLE fragment (one pair of quotes allowed) splits into
    >= 2 tokens + separators and reads printable. Never raises."""
    try:
        if not isinstance(t, str):
            return None
        t = t.strip()
        if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
            t = t[1:-1].strip()
        n = len(t)
        if not t or n > 60000 or t[0] not in "&%\\Uu0":
            return None
        inf = (1 << 30,)
        best = [inf] * (n + 1)    # best[i] = (cost, -tokens, choice) for t[i:]
        best[n] = (0, 0, None)
        for i in range(n - 1, -1, -1):
            cand = []
            for end, unit, v in _soup_opts(t, i):
                b = best[end]
                if b is not inf and end > i:
                    cand.append((b[0] + _soup_cost(unit, v), b[1] - 1, (end, unit, v)))
            m = _SOUP_SEP.match(t, i)
            if m and i and m.end() < n and best[m.end()] is not inf and best[m.end()][2] and \
                    best[m.end()][2][1] != "s":
                b = best[m.end()]
                cand.append((b[0], b[1], (m.end(), "s", t[i:m.end()])))
            if cand:
                best[i] = min(cand, key=lambda c: (c[0], c[1]))
        if best[0] is inf:
            return None
        toks, i = [], 0
        while i < n:
            end, unit, v = best[i][2]
            toks.append((unit, v))
            i = end
        if sum(u != "s" for u, _v in toks) < 2:
            return None
        units, gaps, buf = [], [], []

        def flush():
            if buf:
                raw = bytes(buf)
                try:
                    s = raw.decode("utf-8")
                except UnicodeDecodeError:
                    s = raw.decode("latin-1")
                units.extend(map(ord, s))
                buf.clear()
        prev_tok = False
        for unit, v in toks:
            if unit == "s":
                flush()
                gaps.append((len(units), v))
                prev_tok = False
                continue
            if prev_tok:
                gaps.append((len(units) + len(buf), ""))
            prev_tok = True
            if unit == "b":
                buf.append(v)
                continue
            flush()
            if unit == "h":   # HTML numeric reference: html.unescape's own rules (cp1252 0x80-0x9F, NUL/invalid -> FFFD)
                units.extend(map(ord, html.unescape(f"&#{v};")))
            else:
                units.append(v)
        flush()
        allgap = all(g for _p, g in gaps)
        keep = gaps and not allgap and any(g for _p, g in gaps) and not any(
            u <= 0x10FFFF and chr(u).isspace() for u in units)
        if keep:
            for pos, g in sorted(gaps, reverse=True):
                if re.search(r"\s", g):
                    units.insert(pos, 32)
        return _ucp_str(units)
    except Exception:   # noqa: BLE001
        return None


_SOUP_FMT = {"url": None, "%u": "%u{:04X}", "&#": "&#{:d};", "&#x": "&#x{:x};", "\\u": "\\u{:04x}",
             "\\U": "\\U{:08X}", "\\u{}": "\\u{{{:X}}}", "\\x": None, "octal": None, "U+": "U+{:04X}", "0x": "0x{:02x}",
             "&name;": None}


def _soup_tok(c, fmt):
    if fmt in ("url", "\\x", "octal"):
        f = {"url": "%{:02X}", "\\x": "\\x{:02x}", "octal": "\\{:03o}"}[fmt]
        return "".join(f.format(b) for b in c.encode("utf-8"))
    if fmt == "&name;":
        nm = html.entities.codepoint2name.get(ord(c))
        return f"&{nm};" if nm else f"&#{ord(c)};"
    if fmt == "%u" and ord(c) > 0xFFFF:
        return ucp_enc(c, "%u{:04X}", utf16=True)
    if fmt == "\\u" and ord(c) > 0xFFFF:
        return ucp_enc(c, "\\u{:04x}", utf16=True)
    return _SOUP_FMT[fmt].format(ord(c))


def escsoup_enc(s, seed=0, per="char", sep="", fmts=None):
    """Every char (per='char') or every word incl. its trailing space (per='word') in a seeded random notation."""
    import random
    rnd, fmts = random.Random(seed), list(fmts or _SOUP_FMT)
    if per == "word":
        parts = re.findall(r"\S+\s*|\s+", s)
        return sep.join(sep.join(_soup_tok(c, f) for c in w) for w, f in ((w, rnd.choice(fmts)) for w in parts))
    return sep.join(_soup_tok(c, rnd.choice(fmts)) for c in s)


def escsoup_free(p):
    d = escsoup_dec(p)
    return [p[:len(p) - len(p.lstrip())] + d] if d else []


CANDIDATES += [(f"escsoup-{per}" + ("-spaced" if sep else ""),
                (lambda per, sep: lambda s: escsoup_enc(s, 0, per, sep))(per, sep), escsoup_dec)
               for per in ("char", "word") for sep in ("", " ")]


# ------------------------------------------------- code-point arithmetic: every code point + K (or XOR K)
# "Caesar on code points": chr(ord(c) + K) over the whole text (K < 0 too) moves ASCII into another block -- CJK, PUA,
# astral; Tags = +0xE0000 (U+E0020..E007E, optional U+E0001 LANGUAGE TAG / U+E007F CANCEL TAG wrapper), all-chars
# fullwidth = +0xFEE0 (ICU's space -> U+3000 form and the per-case math / enclosed styles are unistyle's). XOR K on code
# points likewise. Keyless from the crib: K = ord(t[0]) - ord('N') (or ^), verified over the whole crib. "-sp" = ASCII
# spaces left alone; that form at ROT8000's ASCII offset IS ROT8000 and stays its codec. Also read through a U+ / \u{}
# / &#x; token run (codepoints_any) of the shifted text.
_CPS_OPS = {"add": (lambda o, k: o + k, lambda o, k: o - k), "xor": (lambda o, k: o ^ k, lambda o, k: o ^ k)}
_CPS_R8K = _R8K_VALID[_R8K_HALF] - 33
_CPS_CH = sorted(set(_CRIB) | set("abcdefghijklmnopqrstuvwxyz-0123456789"))
_CPS_TAGS = ("\U000E0001", "\U000E007F")


def cpshift(s, k, op="add", keep=False, decode=False):
    """Every code point o -> o + k (op add; o - k when decode) or o ^ k; keep = ASCII spaces untouched. None when a
    result leaves 0..U+10FFFF."""
    f = _CPS_OPS[op][1 if decode else 0]
    out = []
    for c in s:
        o = ord(c) if not (keep and c == " ") else None
        if o is not None:
            o = f(o, k)
            if not 0 <= o <= 0x10FFFF:
                return None
        out.append(c if o is None else chr(o))
    return "".join(out)


def cpshift_enc(s, k, op="add", keep=False, fmt=None, sep=" ", wrap=("", "")):
    x = wrap[0] + cpshift(s, k, op, keep) + wrap[1]
    return codepoints_enc(x, fmt, sep) if fmt else x


def _cps_unwrap(t):
    pre = _CPS_TAGS[0] if t.startswith(_CPS_TAGS[0]) else ""
    suf = _CPS_TAGS[1] if t.endswith(_CPS_TAGS[1]) and len(t) > len(pre) else ""
    return pre, t[len(pre):len(t) - len(suf)], suf


def cpshift_solve(blob, hints=()):
    """(name, sentence, enc) when the blob is the warmups sentence with every code point + K / XOR K (raw, or as a
    code-point token run), K from the crib's first char and verified over the whole crib, else None."""
    try:
        want = reader_text(blob).strip() if not isinstance(blob, str) else blob.strip()
        if not want or len(want) > 200000:
            return None
        reads = [(None, want)]
        u = codepoints_any(want)
        if u:
            reads.append(("u", u))
        for fmt, t in reads:
            pre, body, suf = _cps_unwrap(t)
            if len(body) <= len(_CRIB):
                continue
            for op in _CPS_OPS:
                k = ord(body[0]) - ord("N") if op == "add" else ord(body[0]) ^ ord("N")
                if not k:
                    continue
                for keep in (False, True):
                    if keep and op == "add" and k == _CPS_R8K:
                        continue
                    c = cpshift(_CRIB, k, op, keep)
                    if c is None or not body.startswith(c):
                        continue
                    got = cpshift(body, k, op, keep, decode=True)
                    if not (got and got.startswith(_CRIB) and SLUG.fullmatch(got[len(_CRIB):])):
                        continue
                    name = f"cp{op}{k:+#x}" + ("-sp" if keep else "") + ("-tagwrap" if pre or suf else "")
                    fs = (None, " ")
                    if fmt:
                        fs = next(((f, sp) for f in _CPA_FMT for sp in (" ", "")
                                   if codepoints_enc(t, f, sp) == want), ("u+short", " "))
                        name += f"-{fs[0]}" + ("-adjacent" if fs[1] == "" else "")
                    return name, got, (lambda k, op, keep, fs, w: lambda s: cpshift_enc(s, k, op, keep, fs[0], fs[1], w)
                                       )(k, op, keep, fs, (pre, suf))
    except Exception:  # noqa: BLE001
        return None
    return None


def cpshift_dec(t):
    r = cpshift_solve(t)
    return r[1] if r else None


def cpshift_free(p):
    """Mastery free-text fragment under a code-point add / XOR (K from the first char against every sentence char):
    each reading that decodes to printable ASCII forming a contiguous piece of the sentence (_ba_piece). The raw read
    needs a non-printable-ASCII char (plain ASCII Caesar shapes stay the classical codecs')."""
    out = []
    try:
        lead = p[:len(p) - len(p.lstrip())]
        s = p.strip()
        if not s or len(s) > 4000:
            return []
        reads = [s] if not all(32 <= ord(c) < 127 for c in s) else []
        u = codepoints_any(s)
        if u:
            reads.append(u)
        for t in reads:
            body = _cps_unwrap(t)[1]
            if len(body) < 6:
                continue
            o0 = ord(body[0])
            for op in _CPS_OPS:
                for k in sorted({o0 - ord(c) if op == "add" else o0 ^ ord(c) for c in _CPS_CH}):
                    for keep in (False, True):
                        if not k or (keep and (" " not in body or (op == "add" and k == _CPS_R8K))):
                            continue
                        x = cpshift(body, k, op, keep, decode=True)
                        if x and x.isascii() and x.isprintable() and _ba_piece(x):
                            out.append(lead + x)
    except Exception:  # noqa: BLE001
        return []
    return list(dict.fromkeys(out))


CANDIDATES.append(("cpshift", lambda s: None, cpshift_dec))


# ------------------------------------------------- invisible Unicode smuggling ("ASCII smuggling" for LLM prompts)
# Tags block: ASCII c -> U+E0000 + ord(c) (U+E0020..E007E), optionally wrapped in U+E0001 LANGUAGE TAG ... U+E007F
# CANCEL TAG, after / between visible cover text or alone. Variation-selector byte smuggling (Paul Butler): UTF-8 byte
# b -> VS1-16 U+FE00+b (b < 16) / VS17-256 U+E0100+b-16, the run following a visible carrier emoji. The cover / carrier
# chars are ignored. Decoys: RGI emoji (a lone U+FE0E/FE0F presentation selector, keycaps) and subdivision flags
# (U+1F3F4 + tag letters + U+E007F) carry no payload. Zero-width chars (zw_cands' family) are not read here.
_INV_FLAG = "\U0001F3F4"


def tags_enc(s, cover="", wrap=False):
    body = "".join(chr(0xE0000 + ord(c)) for c in s)
    body = "\U000E0001" + body + "\U000E007F" if wrap else body
    return cover + body


def vs_enc(s, carrier="\U0001F600", cover="", after=""):
    return cover + carrier + "".join(chr(0xFE00 + b if b < 16 else 0xE0100 + b - 16) for b in _u(s)) + after


def _inv_ok(x):
    return len(x) >= 4 and all(c.isprintable() or c in "\t\r\n" for c in x)


def tags_dec(t):
    """The ASCII smuggled in Tags-block chars of t (cover text ignored), or None. Tag runs right after U+1F3F4 are
    emoji subdivision flags, not payload."""
    out, prev, flag = [], "", False
    for c in t:
        o = ord(c)
        if 0xE0000 <= o <= 0xE007F:
            flag = flag or prev == _INV_FLAG
            if not flag and o not in (0xE0001, 0xE007F):
                out.append(chr(o - 0xE0000))
            flag = flag and o != 0xE007F
        else:
            flag = False
        prev = c
    x = "".join(out)
    return x if _inv_ok(x) else None


def vs_dec(t):
    """The UTF-8 text smuggled in variation-selector runs of t (VS1-16 -> 0-15, VS17-256 -> 16-255), or None. A run
    that is a lone U+FE0E / U+FE0F is an emoji presentation selector and is skipped."""
    runs, cur = [], []
    for c in t + " ":
        o = ord(c)
        if 0xFE00 <= o <= 0xFE0F:
            cur.append(o - 0xFE00)
        elif 0xE0100 <= o <= 0xE01EF:
            cur.append(o - 0xE0100 + 16)
        else:
            if cur and not (len(cur) == 1 and cur[0] in (14, 15)):
                runs.append(cur)
            cur = []
    try:
        x = bytes(b for r in runs for b in r).decode("utf-8")
    except UnicodeDecodeError:
        return None
    return x if _inv_ok(x) else None


def invis_cands(t):
    """Tags then variation-selector readings of t; [] when neither carries printable text. Never raises."""
    try:
        t = reader_text(t)
        if not isinstance(t, str) or len(t) > 200000 or not any(ord(c) > 0xFDFF for c in t):
            return []
        return [x for x in (tags_dec(t), vs_dec(t)) if x]
    except Exception:  # noqa: BLE001
        return []


def invis_dec(t):
    got = invis_cands(t)
    return got[0] if got else None


def invis_solve(blob):
    """(name, text, enc) for a Tags / VS smuggled blob: enc re-creates the cover / carrier and tag wrapper seen."""
    try:
        t = reader_text(blob).strip()
        x = tags_dec(t)
        if x:
            vis = "".join(c for c in t if not 0xE0000 <= ord(c) <= 0xE007F)
            wrap = "\U000E0001" in t
            for cover in (vis, ""):
                if tags_enc(x, cover, wrap) == t:
                    return "tags" + ("-wrap" if wrap else "") + ("-cover" if cover else ""), x, (
                        lambda s, c=cover, w=wrap: tags_enc(s, c, w))
            return "tags", x, (lambda s, w=wrap: tags_enc(s, "", w))
        x = vs_dec(t)
        if x:
            vs = lambda c: 0xFE00 <= ord(c) <= 0xFE0F or 0xE0100 <= ord(c) <= 0xE01EF   # noqa: E731
            i = next(i for i, c in enumerate(t) if vs(c) and i + 1 < len(t) and vs(t[i + 1]))   # payload run
            j = next((j for j in range(i, len(t)) if not vs(t[j])), len(t))
            kw = dict(carrier=t[i - 1] if i else "", cover=t[:max(i - 1, 0)], after=t[j:])
            enc = (lambda s, kw=kw: vs_enc(s, **kw)) if vs_enc(x, **kw) == t else vs_enc
            return "vs-smuggle", x, enc
    except Exception:  # noqa: BLE001
        return None
    return None


def invis_free(p):
    lead = p[:len(p) - len(p.lstrip())]
    return [lead + x for x in invis_cands(p)]


CANDIDATES += [("tags", tags_enc, invis_dec),
               ("tags-wrap", lambda s: tags_enc(s, wrap=True), invis_dec),
               ("vs-smuggle", vs_enc, invis_dec)]


# ------------------------------------------------- delta / chained code points ("Point to point" re-read)
# An integer token list (signed decimal, 0x / U+ / bare hex, any , ; | whitespace separators, optional [..] wrapper)
# whose values are mostly small and signed: the first value absolute, then each the difference (or XOR) against the
# previous char -- or the reverse shape, a running sum / running XOR of the code points. Decoder ops: psum (running
# sum = undo differences), pnsum (c_i = c_{i-1} - v_i), pxor (running XOR, c_i = v_i ^ c_{i-1}), adiff (adjacent
# difference = undo a cumulative sum), axor (c_i = v_i ^ v_{i-1}); each optionally mod 256 (over UTF-8 bytes) or mod
# 0x110000, tokens and/or output read back to front. Crib-gated: the whole decode must start 'Nice work'. Plain char
# codes are never re-summed: no op is the identity, and the Mastery fragment reader needs most values outside 32..126.
_DLT_TOK = re.compile(r"([+-]?)(0[xX]|[Uu]\+)?([0-9A-Fa-f]+)")
_DLT_SPLIT = re.compile(r"[\s,;|]+")
_DLT_OPS = ("psum", "pnsum", "pxor", "adiff", "axor")
_DLT_MODS = (None, 256, 0x110000)
_DLT_WRAP = {"[": "]", "(": ")", "{": "}"}


def _dlt_decode(v, op):
    out, acc = [], 0
    for i, x in enumerate(v):
        if op == "psum":
            acc = acc + x
        elif op == "pnsum":
            acc = x if not i else acc - x
        elif op == "pxor":
            acc ^= x
        elif op == "adiff":
            acc = x - (v[i - 1] if i else 0)
        else:
            acc = x ^ (v[i - 1] if i else 0)
        out.append(acc)
    return out


def _dlt_encode(c, op):
    if op == "psum":
        return [x - (c[i - 1] if i else 0) for i, x in enumerate(c)]
    if op == "pnsum":
        return [x if not i else c[i - 1] - x for i, x in enumerate(c)]
    if op == "pxor":
        return [x ^ (c[i - 1] if i else 0) for i, x in enumerate(c)]
    out, acc = [], 0
    for x in c:
        acc = acc + x if op == "adiff" else acc ^ x
        out.append(acc)
    return out


def _dlt_text(vals, mod):
    if mod == 256:
        vals = [x % 256 for x in vals]
        try:
            return bytes(vals).decode("utf-8")
        except UnicodeDecodeError:
            return None
    if mod:
        vals = [x % mod for x in vals]
    if any(not 0 <= x <= 0x10FFFF or 0xD800 <= x <= 0xDFFF for x in vals):
        return None
    return "".join(map(chr, vals))


def delta_enc(s, op="psum", mod=None, radix=10, prefix="", upper=False, width=0, plus=False, sep=" ",
              wrap=("", ""), revtok=False, revout=False):
    """Plain -> its delta / chained token list (the exact inverse of the decoder op; see the section comment)."""
    s = s[::-1] if revout else s
    c = list(s.encode("utf-8")) if mod == 256 else [ord(ch) for ch in s]
    v = _dlt_encode(c, op)
    if mod:
        v = [x % mod for x in v]
    v = v[::-1] if revtok else v
    toks = []
    for x in v:
        d = (f"{abs(x):0{width}x}" if radix == 16 else f"{abs(x):0{width}d}")
        toks.append(("-" if x < 0 else "+" if plus and x > 0 else "") + prefix + (d.upper() if upper else d))
    return wrap[0] + sep.join(toks) + wrap[1]


def _dlt_parse(t):
    """[(radix, ints, fmt kwargs)] readings of a whole-fragment integer token list, [] when it isn't one."""
    t = t.strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        t = t[1:-1].strip()
    if not t or len(t) > 100000:
        return []
    w0 = w1 = ""
    if t[0] in _DLT_WRAP and t[-1] == _DLT_WRAP[t[0]]:
        inner = t[1:-1]
        w0 = t[0] + inner[:len(inner) - len(inner.lstrip())]
        w1 = inner[len(inner.rstrip()):] + t[-1]
        t = inner.strip()
    seps = _DLT_SPLIT.findall(t)
    raw = _DLT_SPLIT.split(t)
    ms = [_DLT_TOK.fullmatch(x) for x in raw]
    if len(ms) < 4 or None in ms:
        return []
    pfx = {m.group(2) or "" for m in ms}
    if len(pfx) > 1:
        return []
    pfx = pfx.pop()
    digs = [m.group(3) for m in ms]
    alldec = all(d.isdigit() for d in digs)
    radices = [16] if pfx else ([10, 16] if alldec else [16])
    width = min(map(len, digs)) if any(d[0] == "0" and len(d) > 1 for d in digs) else 0
    kw = dict(prefix=pfx, upper=any(ch in "ABCDEF" for d in digs for ch in d), width=width,
              plus=any(m.group(1) == "+" for m in ms), sep=seps[0] if len(set(seps)) == 1 else " ", wrap=(w0, w1))
    return [(r, [int(m.group(1) + m.group(3), r) for m in ms], dict(kw, radix=r)) for r in radices]


def _dlt_reads(v):
    """Every (op, mod, revtok, revout, text) decode of the int list v (printable text only)."""
    for revtok in (False, True):
        w = v[::-1] if revtok else v
        for op in _DLT_OPS:
            vals = _dlt_decode(w, op)
            for mod in (_DLT_MODS if max(map(abs, v)) < 256 else (None, 0x110000, 256)):
                x = _dlt_text(vals, mod)
                if not x or not x.isprintable():
                    continue
                for revout in (False, True):
                    yield op, mod, revtok, revout, x[::-1] if revout else x


def delta_solve(blob, hints=()):
    """(name, sentence, enc) when the blob is a delta / chained token list of a text starting 'Nice work', else None."""
    try:
        want = reader_text(blob).strip() if not isinstance(blob, str) else blob.strip()
        for radix, v, kw in _dlt_parse(want):
            for op, mod, revtok, revout, x in _dlt_reads(v):
                if not x.startswith(_CRIB[:9]):
                    continue
                name = (f"delta-{op}" + ({256: "-mod256", 0x110000: "-mod110000"}.get(mod, "")) + ("-revtok" if revtok else "")
                        + ("-revout" if revout else "") + ("-hex" if radix == 16 else "-dec"))
                kw2 = dict(kw, op=op, mod=mod, revtok=revtok, revout=revout)
                return name, x, (lambda kw2: lambda s: delta_enc(s, **kw2))(kw2)
    except Exception:  # noqa: BLE001
        return None
    return None


def delta_dec(t):
    r = delta_solve(t)
    return r[1] if r else None


def delta_free(p):
    """Mastery fragment under a delta / chained token list: every reading that is printable ASCII and a contiguous
    piece of the sentence (_ba_piece). Needs most values after the first outside 32..126 (plain char codes stay the
    decimal / hex codecs')."""
    out = []
    try:
        if not isinstance(p, str):
            return []
        lead = p[:len(p) - len(p.lstrip())]
        for _radix, v, _kw in _dlt_parse(p):
            if sum(not 32 <= x <= 126 for x in v[1:]) * 2 < len(v) - 1:
                continue
            for _op, _mod, _rt, _ro, x in _dlt_reads(v):
                if x.isascii() and _ba_piece(x):
                    out.append(lead + x)
    except Exception:  # noqa: BLE001
        return []
    return list(dict.fromkeys(out))


# ------------------------------------------------- UTF-8 mojibake / multibyte byte escapes ("Encoding confusion")
# Sibling of D19-D20 / D25: the UTF-8 bytes of the sentence (often fullwidth-styled, or with smart quotes) re-read as
# cp1252 / latin-1 (`ï¼®ï½‰`, `â€œ`), possibly 2-3 times over (double-encoded `ÃƒÂ¯Ã‚Â¼`), or written as byte escapes
# of the multibyte sequences (`\xef\xbc\xae`, `%EF%BC%AE`). Repair = encode under the page, decode UTF-8 STRICT, up to
# 3 rounds; cp1252 is the WHATWG/"sloppy" page (0x81 0x8D 0x8F 0x90 0x9D -> U+0081.. C1 controls, as browsers / Node's
# TextDecoder write them), latin-1 is the other try (they differ only on 0x80-0x9F). Then NFKC: fullwidth -> ASCII.
# Gate: something changed, a real multibyte sequence was decoded, the result is printable. Stdlib only (no ftfy).
_MOJI_C1252 = {}
for _b in range(256):
    try:
        _MOJI_C1252[bytes([_b]).decode("cp1252")] = _b
    except UnicodeDecodeError:
        _MOJI_C1252[chr(_b)] = _b
_MOJI_C1252_DEC = {v: c for c, v in _MOJI_C1252.items()}
_MOJI_PAGES = ("cp1252", "latin-1")


def _moji_bytes(t, page):
    """Text -> the bytes it was read from under `page` (cp1252 = sloppy WHATWG table), None if a char is off-page."""
    if page == "latin-1":
        return t.encode("latin-1") if all(ord(c) < 256 for c in t) else None
    try:
        return bytes(_MOJI_C1252[c] for c in t)
    except KeyError:
        return None


def mojibake_enc(s, page="cp1252", n=1, style=None):
    """Plain -> its UTF-8 bytes re-read `n` times under `page` (style: unistyle_enc it first, e.g. "fullwidth")."""
    if style:
        s = unistyle_enc(s, style)
    for _ in range(n):
        b = s.encode("utf-8")
        s = "".join(_MOJI_C1252_DEC[x] for x in b) if page == "cp1252" else b.decode("latin-1")
    return s


def _moji_round(t):
    """One repair round: the strict UTF-8 reading of t's bytes under the first page that has a multibyte sequence."""
    if t.isascii():
        return None
    for page in _MOJI_PAGES:
        b = _moji_bytes(t, page)
        if b is None or max(b) < 0xC2:
            continue
        try:
            u = b.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if u != t:
            return u
    return None


def _moji_runs(t):
    """Run-wise repair when the whole line is not one page (mojibake runs beside genuine non-Latin text)."""
    hit = [False]

    def fix(m):
        u = _moji_round(m[0])
        if u is None:
            return m[0]
        hit[0] = True
        return u
    out = re.sub("[\u0080-ÿŒœŠšŸŽžƒˆ˜–—‘-„"
                 "†-•…‰‹›€™]{2,}", fix, t)
    return out if hit[0] else None


def _moji_esc(t):
    """`\\xHH` / `%HH` runs holding a byte >= 0x80 -> their strict UTF-8 text (other chars kept), else None."""
    hit = [False]

    def fix(m):
        b = bytes(int(h, 16) for h in re.findall(r"[0-9a-fA-F]{2}", m[0]))
        if max(b) < 0x80:
            return m[0]
        try:
            u = b.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError from None
        hit[0] = True
        return u
    try:
        out = re.sub(r"(?:\\\\?x[0-9a-fA-F]{2})+", fix, t)
        if "%" in out:
            pct = re.sub(r"(?:%[0-9a-fA-F]{2})+", fix, out)
            if hit[0] and pct != out and not re.search(r"\s", out) and "+" in pct:
                pct = pct.replace("+", " ")   # form-encoded (quote_plus): '+' = space
            out = pct
    except ValueError:
        return None
    return out if hit[0] else None


def _moji_ok(x):
    return bool(x) and all(c.isprintable() or c in "\t\r\n" for c in x)


def mojibake_reads(t):
    """[text] every repaired reading of t (byte escapes first, then up to 3 mojibake rounds), NFKC-normalized."""
    if not isinstance(t, str):
        return []
    t = t.strip()
    if not t or len(t) > 100000:
        return []
    out = []
    starts = [t]
    e = _moji_esc(t)
    if e is not None:
        starts.insert(0, e)
        out.append(e)
    for s in starts:
        cur = s
        for _ in range(3):
            u = _moji_round(cur)
            if u is None:
                u = _moji_runs(cur)
            if u is None:
                break
            cur = u
            out.append(cur)
    res = []
    for x in reversed(out):   # most-repaired first
        n = unicodedata.normalize("NFKC", x)
        if _moji_ok(n) and n not in res:
            res.append(n)
    return res


def mojibake_dec(t):
    """Mojibake / UTF-8 byte-escaped text -> repaired NFKC text, None unless a multibyte UTF-8 read changed it."""
    try:
        r = mojibake_reads(_t(t))
    except Exception:  # noqa: BLE001
        return None
    return r[0] if r else None


def mojibake_free(p):
    """Mastery line under mojibake / multibyte byte escapes: every repaired reading (+ smart quotes folded to ASCII)."""
    try:
        if not isinstance(p, str):
            return []
        lead = p[:len(p) - len(p.lstrip())]
        outs = []
        for x in mojibake_reads(p):
            outs.append(x)
            f = x.translate(_MOJI_QUOTES)
            if f != x:
                outs.append(f)
        return [lead + x for x in dict.fromkeys(outs)]
    except Exception:  # noqa: BLE001
        return []


_MOJI_QUOTES = str.maketrans({"‘": "'", "’": "'", "‚": "'", "“": '"', "”": '"',
                              "„": '"', "–": "-", "—": "-"})
CANDIDATES += [(f"mojibake-{page}" + (f"x{n}" if n > 1 else "") + (f"({st})" if st else ""),
                (lambda pg, k, y: lambda s: mojibake_enc(s, pg, k, y))(page, n, st), mojibake_dec)
               for st in ("fullwidth",) for page in _MOJI_PAGES for n in (1, 2, 3)]
CANDIDATES += [(f"utf8-{name}(fullwidth)", (lambda f: lambda s: "".join(
    f.format(x) for x in unistyle_enc(s, "fullwidth").encode("utf-8")))(fmt), mojibake_dec)
    for name, fmt in (("xesc", "\\x{:02x}"), ("XESC", "\\x{:02X}"), ("pct", "%{:02X}"), ("pct-lower", "%{:02x}"))]


# keyless crib-gated decoder (infer returns the solved shape's encoder; these entries' encoders are common shapes)
CANDIDATES += [("delta-psum-dec", lambda s: delta_enc(s), delta_dec),
               ("delta-psum-dec-comma", lambda s: delta_enc(s, sep=", "), delta_dec),
               ("delta-psum-mod256-hex", lambda s: delta_enc(s, mod=256, radix=16, width=2), delta_dec),
               ("delta-pxor-hex", lambda s: delta_enc(s, op="pxor", radix=16, prefix="0x", width=2), delta_dec),
               ("delta-adiff-dec", lambda s: delta_enc(s, op="adiff"), delta_dec)]


# ------------------------------------------------- letter maps into another SCRIPT ("every character has a place")
# Each Latin letter -> one glyph of a non-Latin script (Elder Futhark runes, Greek / Cyrillic keyboard-or-transliteration
# letters, Ogham, Tifinagh, Old Italic, Gothic, or an arbitrary glyph alphabet: Deseret / Shavian / symbols), word
# lengths kept, ASCII digits / punctuation kept, the space kept or written as one separator (Ogham U+1680, runic ᛫).
# Solve = the fixed 87-char crib fixes letter -> glyph for its 21 letters (a FUNCTION: runes fold c/k/q onto ᚲ, so a
# glyph may stand for several letters); the slug's glyphs read through a standard table the crib agrees with, else
# the crib's inverse + the 5 unseen letters (f j q y z) on unseen glyphs, picked by the slug word list (generator words
# first). Glyph case folds (Greek / Cyrillic / Deseret), Greek final sigma = sigma. Gate: crib aligned exactly, >= 12
# distinct non-ASCII glyphs, the tail reads as a slug.
def _sm_tab(pairs):
    p = pairs.split()
    return dict(zip(p[0::2], p[1::2]))


_SM_TABLES = {
    "futhark": _sm_tab("a ᚨ b ᛒ c ᚲ d ᛞ e ᛖ f ᚠ g ᚷ h ᚺ i ᛁ j ᛃ k ᚲ l ᛚ m ᛗ n ᚾ o ᛟ p ᛈ q ᚲ r ᚱ s ᛊ t ᛏ u ᚢ "
                       "v ᚹ w ᚹ x ᛉ y ᛃ z ᛉ"),
    "greek": _sm_tab("a α b β c κ d δ e ε f φ g γ h η i ι j ξ k κ l λ m μ n ν o ο p π q θ r ρ s σ t τ u υ v β "
                     "w ω x χ y ψ z ζ"),
    "greek-keyboard": _sm_tab("a α b β c ψ d δ e ε f φ g γ h η i ι j ξ k κ l λ m μ n ν o ο p π q ; r ρ s σ t τ "
                              "u θ v ω w ς x χ y υ z ζ"),
    "cyrillic": _sm_tab("a а b б c ц d д e е f ф g г h х i и j й k к l л m м n н o о p п q я r р s с t т u у v в "
                        "w щ x ж y ы z з"),
    "cyrillic-yawert": _sm_tab("a а b б c ц d д e е f ф g г h ч i и j й k к l л m м n н o о p п q я r р s с t т "
                               "u у v ж w в x ь y ы z з"),
    "ogham": _sm_tab("a ᚐ b ᚁ c ᚉ d ᚇ e ᚓ f ᚃ g ᚌ h ᚆ i ᚔ j ᚔ k ᚉ l ᚂ m ᚋ n ᚅ o ᚑ p ᚚ q ᚊ r ᚏ s ᚄ t ᚈ u ᚒ "
                     "v ᚃ w ᚃ x ᚕ y ᚔ z ᚎ"),
    "tifinagh": _sm_tab("a ⴰ b ⴱ c ⵛ d ⴷ e ⴻ f ⴼ g ⴳ h ⵀ i ⵉ j ⵊ k ⴽ l ⵍ m ⵎ n ⵏ o ⵧ p ⵒ q ⵇ r ⵔ s ⵙ t ⵜ u ⵓ "
                        "v ⵠ w ⵡ x ⵅ y ⵢ z ⵣ"),
    "old-italic": _sm_tab("a 𐌀 b 𐌁 c 𐌂 d 𐌃 e 𐌄 f 𐌚 g 𐌂 h 𐌇 i 𐌉 j 𐌉 k 𐌊 l 𐌋 m 𐌌 n 𐌍 o 𐌏 p 𐌐 q 𐌒 r 𐌓 "
                          "s 𐌔 t 𐌕 u 𐌖 v 𐌅 w 𐌅 x 𐌗 y 𐌖 z 𐌆"),
    "gothic": _sm_tab("a 𐌰 b 𐌱 c 𐌺 d 𐌳 e 𐌴 f 𐍆 g 𐌲 h 𐌷 i 𐌹 j 𐌾 k 𐌺 l 𐌻 m 𐌼 n 𐌽 o 𐍉 p 𐍀 q 𐌵 r 𐍂 s 𐍃 "
                      "t 𐍄 u 𐌿 v 𐍅 w 𐍅 x 𐍇 y 𐍅 z 𐌶"),
}
_SM_INV = {n: {g: {k for k, v in tab.items() if v == g} for g in tab.values()} for n, tab in _SM_TABLES.items()}
_SM_BYLEN = {}
_SM_SEPS = " \u1680\u16eb\u16ec\u16ed\u00b7\u2027\u2e31\u3000"


def _sm_fold(c):
    return "σ" if c == "ς" else c.lower()


def _sm_align(crib, t, need=12):
    """(enc {letter: folded glyph}, raw {letter: glyph as written}, sep) when t[:len(crib)] is crib under one letter ->
    glyph function (non-letters kept, space -> one separator), else None."""
    enc, raw, sep = {}, {}, None
    if len(t) < len(crib):
        return None
    for p, c in zip(crib, t):
        if p.isalpha():
            if c.isascii() or c.isspace() or c in _SM_SEPS:
                return None
            g = _sm_fold(c)
            if enc.setdefault(p.lower(), g) != g:
                return None
            raw.setdefault(p, c)
        elif p == " ":
            if c != " " and not c.isspace() and c not in _SM_SEPS:
                return None
            if sep is None:
                sep = c
            elif sep != c:
                return None
        elif p != c:
            return None
    if len(set(enc.values())) < min(need, len(enc)) or sum(c.isalpha() for c in crib) < 10:
        return None
    return enc, raw, sep or " "


def _sm_tail(enc, tail, sep, prefix=False):
    """[(slug text, {letter: glyph} additions)] best-first readings of the slug glyphs: a crib-consistent standard
    table's inverse, else the crib inverse + unseen letters on unseen glyphs (1:1 when the crib map is). prefix: the
    last word may be cut (Mastery fragment)."""
    from lib import slug as S
    tail = tail.replace(sep, " ") if sep != " " else tail
    if any(c.isascii() and c.isalpha() for c in tail):
        return None
    glyph = lambda c: not c.isascii() and not c.isspace()   # noqa: E731
    if not any(glyph(c) for c in tail):
        return [(tail, {})]
    inv = {}
    for k, v in enc.items():
        inv.setdefault(v, set()).add(k)
    inj = all(len(s) == 1 for s in inv.values())
    free = set(_LC) - set(enc)
    tabs = [n for n, tab in _SM_TABLES.items() if all(_sm_fold(tab[k]) == v for k, v in enc.items())]
    if tabs:
        ti = {_sm_fold(g): s for g, s in _SM_INV[tabs[0]].items()}
        cand = lambda g: ti.get(g, set())   # noqa: E731
    else:
        cand = lambda g: (inv[g] | (set() if inj else free)) if g in inv else free   # noqa: E731
    vocab = S.vocab()
    if not _SM_BYLEN:
        if _SUBST_POOL[0] is None:
            _SUBST_POOL[0] = sorted(vocab) + sorted(w for w in S.english()
                                                    if w not in vocab and w.isascii() and w.isalpha())
        for w in _SUBST_POOL[0]:
            _SM_BYLEN.setdefault(len(w), []).append(w)
    spans = [(m.start(), m.end()) for m in re.finditer(r"[^\x00-\x7f\s]+", tail)]
    cut = prefix and spans and spans[-1][1] == len(tail.rstrip())
    fits = []
    for k, (a, b) in enumerate(spans):
        gs = [_sm_fold(c) for c in tail[a:b]]
        cs = [cand(g) for g in gs]
        if not all(cs):
            return None
        last = cut and k == len(spans) - 1
        f = [w for n in (sorted(x for x in _SM_BYLEN if x >= len(gs)) if last else (len(gs),))
             for w in _SM_BYLEN.get(n, ()) if all(x in c for x, c in zip(w, cs))]
        if not f:
            return None
        fits.append((gs, f[:400]))
    out, budget = [], [20000]

    def walk(k, add, back, sc, words):
        budget[0] -= 1
        if budget[0] < 0 or len(out) >= 6:
            return
        if k == len(fits):
            out.append((sc, words, dict(add)))
            return
        gs, f = fits[k]
        for w in f:
            a2, b2, ok = dict(add), dict(back), True
            for x, g in zip(w, gs):
                if x in enc or tabs:
                    continue
                if a2.setdefault(x, g) != g or (inj and b2.setdefault(g, x) != x):
                    ok = False
                    break
            if ok:
                walk(k + 1, a2, b2, sc + (w in vocab), words + [w[:len(gs)]])
    walk(0, {}, {}, 0, [])
    if not out:
        return None
    res = []
    for sc, words, add in sorted(out, key=lambda o: -o[0]):
        txt, pos = "", 0
        for (a, b), w in zip(spans, words):
            txt += tail[pos:a] + w
            pos = b
        res.append((txt + tail[pos:], add))
    return res


def _sm_encoder(enc, raw, sep):
    def e(s):
        o = []
        for ch in s:
            if ch == " ":
                o.append(sep)
            elif ch in raw:
                o.append(raw[ch])
            elif ch.isascii() and ch.isalpha() and ch.lower() in enc:
                g = enc[ch.lower()]
                o.append(g.upper() if ch.isupper() else g)
            else:
                o.append(ch)
        return "".join(o)
    return e


def scriptmap_solve(blob):
    """(name, sentence, enc) when the blob is the warmups sentence under a letter -> glyph map into another script
    (crib-learned, slug glyphs via a standard table or the slug word list), else None. Never raises."""
    try:
        t = _t(blob).strip()
        wrap = t[:1] == "\u169b" and t[-1:] == "\u169c"   # Ogham feather marks around the text
        t = t.strip("\u169b\u169c").strip()
        if t.isascii() or len(t) <= len(_CRIB) or len(t) > 400:
            return None
        al = _sm_align(_CRIB, t)
        if not al:
            return None
        enc, raw, sep = al
        rd = _sm_tail(enc, t[len(_CRIB):], sep)
        for tail, add in rd or ():
            if SLUG.fullmatch(tail):
                tabs = [n for n, tab in _SM_TABLES.items() if all(_sm_fold(tab[k]) == v for k, v in enc.items())]
                full = dict(enc, **add)
                if tabs:
                    full = dict({k: v for k, v in _SM_TABLES[tabs[0]].items()}, **enc)
                name = "script-" + (tabs[0] if tabs else "map")
                e = _sm_encoder(full, raw, sep)
                return name, _CRIB + tail, (lambda s: "\u169b" + e(s) + "\u169c") if wrap else e
        return None
    except Exception:  # noqa: BLE001
        return None


def scriptmap_dec(t):
    r = scriptmap_solve(t)
    return r[1] if r else None


def scriptmap_free(p, k=3):
    """Mastery fragment under a letter -> glyph script map: the crib fitted at every offset (>= 10 letters, >= 8
    glyphs) -> decoded fragments (slug words via the word list, the last may be cut). Never raises."""
    out = []
    try:
        if not isinstance(p, str) or p.isascii() or len(p) > 400:
            return out
        lead = p[:len(p) - len(p.lstrip())]
        q = p.strip()
        for off in range(len(_CRIB)):
            crib = _CRIB[off:]
            n = min(len(crib), len(q))
            if sum(c.isalpha() for c in crib[:n]) < 10:
                break
            al = _sm_align(crib[:n], q, need=8)
            if not al:
                continue
            got = crib[:n]
            if len(q) > n:
                rd = _sm_tail(al[0], q[n:], al[2], prefix=True)
                if not rd:
                    continue
                got += rd[0][0]
            if lead + got not in out:
                out.append(lead + got)
            if len(out) >= k:
                break
    except Exception:  # noqa: BLE001
        return out
    return out


CANDIDATES += [(f"script-{n}", (lambda tab: lambda s: "".join(
    (tab[c.lower()].upper() if c.isupper() else tab[c.lower()]) if c.isascii() and c.lower() in tab else c
    for c in s))(tab), scriptmap_dec) for n, tab in _SM_TABLES.items()]
CANDIDATES.append(("script-map", lambda s: None, scriptmap_dec))


# ---- ASCII-art text: FIGlet banners (standard / banner / big) and 5x7 dot-matrix (HD44780-style LCD font) ----------
# FIGlet: glyph tables vendored from the standard FIGlet 2.2 fonts (ASCII 32-126, endmarks stripped; hardblank kept):
# name -> (hardblank, height, full_layout, b85(zlib(glyph rows: \x1f between rows, \n between glyphs))). The renderer
# mirrors figlet/pyfiglet's horizontal smushing + width-80 wrap at the last blank, so the encoder reproduces
# `pyfiglet.figlet_format(s, font)` byte for byte and the decoder re-derives the text glyph by glyph (greedy with
# backtracking on the smushed prefix, every block verified by re-rendering).
_FIG_FONTS = {
    "standard": ("$", 6, 24463,
        "c-oy<Np9;f4Bh7v=AuATpolI|^cY<cP!FQRe{pycDJw(2lQ@PY&X0plZwICCg{aa&jT%n1pRV=epnmA8tY7=0-1_MsS$U)QXFFxDeC1Z{y!uyJ_glA{+_G!k*o3T$>fga)@Tq#MllQ+uRdnH6iA4>faww(g)>l>AqPP3*BBcFKB$rxX2sl^Q@7ifU$o6*5g~j@7{U-YA_qw!NxExU{^Frs=RK(jjfwRdyT<>`9{P;pu&Eozs<MO%dYCcr`M7(fhGJ}g)$|8)*^cVKqjo^8>efl{#`7$VQil$|r*dT}UltXz+=%4bOD1wLFM=?@lk)mu@HFsHf+>-!lHNR<;k`5a5iR1xiUv-{hg+)QIrK|*HWic>N!FJPGT+8m350kOc#N%OkFt41|h|Ln5q^Df9r0@fY1ZXSxmHZv9ySkYhk45XKAwq-@DZ><;6dg;W6sG&KHZcvGKOudk%4j;_>bx3|JhRe_^6X>FrJO-0kUv0s%4L?y<Wh$6=35Uo9|QPJBdUg{$_d{n6pgQ_Tz?(Oox)MC&N8*wVBq;R(ywUUaAtDt2sgeK&f$U`>NKW}X6ijcomy%9T~z?zmw1~~w1`-;dzVuP5FtQX?V_wl`Abtnq$bE~qYc8(c6p}^^=FYqW6x@iE?PYrHEF?#RRnJt-amo_$7*#wO@~UaR7K5$CP|_F>0NW7(an5cTL6Pw;a)voJn*yr)KqCwrW6;bN24B7azOSQ!yIA|^6(pHiT~LnHrR7`)93<QJiH()X4O+!^hL01OI1++`IY)V%h&At<gI01tdqbFu}^(i>uBh#rN&B|T%&hzpA#{uaPA+0Lt>KoWLBBmiQ(Ys+`tDj2I^kIxiw)I4~ieO`1>A{!+ZF4=8TDP899L(vYh)~cmsZL54i0NtNFyUt}`SuOn8b1r44ekIek6Te$sn7`^8C^l=(Ud4-VBH9YPnoPDFj4E9a;%%k(n3&+XKGrl?V@UC`(}ZJCy<6EqBdPj%Z!Ax62_Ng3PFZM@eU2~B_Sl?4~Q{-LjCm0i0GhNSIm48QnjWunnzio<G3H&MB(5bD|5O_Ioy+z2&wL$K*L7u#f8ZX)X}M}P244)Dv<>?2ty^0(Ab{u*&BKbJ+6Nt&}3*e^IgfLBine}YyN9VzbuNNa$sP_$!b@4X@CUhe1v?So>g_54gV2_tPJj~p_Sl)0zQ@NHOKJHpF0=6no=(%Nr1&=tx$zu7~uKMH6I`0AfI@cFxfZPqw^FL=^JmjLBAeb3h>;tlNrrD+=|o7Xn;?ae=vKfHP"),
    "banner": ("$", 8, 64,
        "c-pO5S#sqd4E%qWh^qSC|BRDhtc?bQJx;|aV1(3K5JbN6{gLhKBLIF${}%iW{yw>1`uEmrGy1HrNS|qxET~VLh~9ToxSnmFr<7m&tj%b0L8<ngj!GIu9(DTO-=S;SG#BHdvM3t3IU9DSugW5(hm)@(FP=-cNgG9$FIi3{BkybdzIf+7G)}6%R9i>Y?0S=?qoXEi>#5CQvzJzN-!XqNynXBW#Bs;rnorT;IDXQ6Yi&I~ezKmAuj^6HiUadEhpXC;#1}HI&@~tp>;#Z_?Y`L81hvO#7ZRUd(-eWG3nJz@o{Id0YD(fgu8S!ZWic*e{^;M$H9C=x>C5<`s&AC9;%}7N%g5~dMqitOBm9K!biDsF*$0>T!sWu4W@VB?S)R%HWu0$6n<bbqrTDp0K=K5)Hfr{7JLX8GNT>FSJM27@r8oo8$ozep1&gEQc$`w}c-&{{s(gj~BPaRx6+gB=?eJS!b(+7|2<?%~^_2z?eJ}R!DRrce7L!)j_A*prPu!=J(YUXjQOpk<rgy1`>nGRVHJl?qtGEe2Ul*_A953SNP2PCp_anv50eF$u!0H>pL0mqlt30M4`$v_k#rd;1E6p8GF<bd?MoBwa&-m>mSnZNe_!aFjsfSDFmRY>rvRB%4&OkhOj`gb3z@2fDPml8WkySgKd(0{phuibxkC1cp3+hJtLvMVryf-iq;qEW|W|NK*bRSBk!Z2Ov^c1i`9zIJ30{-KYJPTsOCyEg>=`e)<z$cozj!&}J3Lg%_1}Nk6*E{)5{uS;&C~+*W9@)$FlFTt)5es|z`sOZ|AZ7e0A9pc%>tz>@Yd&(~?+@c<?y#rwAevHQ0rW(ko!w;+K7vreXL&C<Yxi;Y%uc20?&eP(@VOltd;eQ5I^AMMe2oj9;Tv{#D-N_?&=O)2-|l}Pu0{IW)jzRL33+hLi|z&%xdrJDH?~(DFaDIMn&L?X@ejg}T^R"),
    "big": ("$", 8, 24463,
        "c-oy=TaN1>4E^sW@JFP{NLAUusLQxtNS=kT_zQl3c{Z80H{p`tw~q}2hl9!Q0f68jLToOWE+>9FNFTb;d-=^Xy^-htrEh+6z~lzy_Q)5cU!KB5KK+Pgp3VQ_W<E=jeubPRUFaiCrRC}7)7m6nNEAXA7Qj2AGRl=jLL@!YGEWcEo!-dzJjnMflt*9e(TMP9q(T%u&$Q}WC?rXI$c8=f4e*oZl62^UcN2}oA7{34Bw3F3QvE@~v*fJ%cukyw6S_!d3hB$nnq9M+&gg~0&xiEb)5-w9@I_XN$nQjw;t4M%9elEO@YYMN^;exUQK7D{ewTL+OQ5y88!nygdjFIW(uY{mC-T$E>*!Zp;M?U3sEYu$@dXlJOFfZY$Dt&?)m$wDWH(Z1&FLTq^4#;B@^#6hu#L!ElTE(qO;y5YVq(GQI)=Pn2`Gh>o5Bp?NBr>3fU}WX<AgDyj)Z%O8IY$<_)PLkT@NC8WGYtDD{_IPRO3yi17GT?Q#9WC#l|AAjp5KxDb!1_4AIiX=NK<4#T(e}m*m>eNvobBXNhR^yF9H4a;)=Z@!pWnoK>7t%>O5S8J#%L3hp&^XqWv9L|EHdpgwc7oZs*+QdyfgSmqV9d8M(NjSZ8$Y7rD`5Gp|`TE7Yqry>J+jr9s$ST}TKI>Eh;eO_H+P&M|<JXH9qR-e`Bf(KA>OtK70T*eD|r=AiCM9)JpqK@>vu=Z%d0}-quY=zj0u^5YRjrm4;sPrtt=v-{&+eO?hda{-RXpavQ`+@KvU~TmMWIwLt3tKTtwwBED#Si{yy8#7u9n_AYm2BwCP^TiqW`r=vI;KUhX9k|!331OQZ4fZ_L}`F>_fzx0b$04JH6LA#i{i7?bcu~a_9|<Y8nJtJFK!HK83;0Xf#OL3B^6e7M^iYi<kKg+PxBKibnx1H@qb&s2HWn*2cYr=jgSs2Kj-JEG6&nE7_j_=N2Xb_-4g7E7+Vx?>%~0p|LkYP+A>p#(Fz|psCiw;p{`Yx=9NnDea&g>kJ9gW^n7|=J->nH$anUC;jfI9<3C~bmj1;Hh~$E5Bg74QR27Q!SOte7^9_H}N4j9%uN;&8ifkj+xLb>r#=+#K_!eEKS8<GbL|svQ5Y+f{`#`N8T04eYt>cwH(Ec{<aw8vP%&*Ywk5?$O9vzDg)b9I%L|E_pVc04npUs%Q@2n~JT=}UjJ$4^d_b;U%du{eX(DtbYy%f6?x#FUq)iNz!Qoy*S&qfXig3f*?M|nNg5N)H_>?+;tJmZ=_R7bCS;WWDJk6Oy((yzLO>Q46LeY20EvF^hVmg(XpU8<a}086BewC#(4d--)AG@duk<(q;j>6Hy^Z1dZmj5IcCJD#4})PD$nvHLU*HaqBTK7Eu&+lyDz{gmeC?{R5b<w&^H=M`$#`BnE0h4CW4o!xuOF>Nfzw3GtV^Vy+f0GjN~>*IxdMAN8@=Vi~U{@hmZusQ#j1fCoE9dBt`vMuGw`FHCd#6pwly*VF!rWBUv2{-Juz^}p2$W_>z^N_i}?0JqJ<9mC!BB$A=<nM6ABFb=1Q%FG=m>NS<Kj0%Z1b+R8j^Xbe{{bVJ?d$"),
}
# 5x7 dot matrix: the classic HD44780-style LCD font (luma.core LCD_FONT / avrfreaks 5x7), 0x20-0x7E, 5 column bytes per
# char, bit 0 = top row.
_DM_COLS = bytes.fromhex(
    "000000000000005f00000003000300147f147f14242a7f2a12231308646236495522500005030000001c2241000041221c00"
    "14083e081408083e080800503000000808080808006060000020100804023e5149453e00427f400042615149462141454b31"
    "1814127f1027454545393c4a49493001710905033649494936064949291e0036360000005636000008142241001414141414"
    "00412214080201510906324979413e7e1111117e7f494949363e414141227f4141221c7f494949417f090909013e4149497a"
    "7f0808087f00417f41002040413f017f081422417f404040407f020c027f7f0408107f3e4141413e7f090909063e4151215e"
    "7f09192946464949493101017f01013f4040403f1f2040201f3f4038403f631408146307087008076151494543007f414100"
    "02040810200041417f0004020102044040404040000102040020545454787f484444383844444420384444487f3854545418"
    "087e0901020c5252523e7f0804047800447d40002040443d007f1028440000417f40007c041804787c080404783844444438"
    "7c14141408081414187c7c080404084854545420043f4440203c4040207c1c2040201c3c4030403c44281028440c5050503c"
    "4464544c44000836410000007f000000413608001008081008")


@functools.lru_cache(maxsize=None)
def _fig_font(name):
    hb, h, full, blob = _FIG_FONTS[name]
    rows = zlib.decompress(base64.b85decode(blob)).decode("latin-1").split("\n")
    chars = {chr(32 + i): g.split("\x1f") for i, g in enumerate(rows)}
    chars = {c: g for c, g in chars.items() if c == " " or "".join(g)}
    return hb, h, full, chars


def _fig_smush(l, r, mode, hb, pw, cw):
    """figlet smushchar(): the merged sub-character, or None."""
    if l == " ":
        return r
    if r == " ":
        return l
    if pw < 2 or cw < 2 or not mode & 128:
        return None
    if not mode & 63:
        return r if l == hb else l if r == hb else r
    if mode & 32 and l == hb and r == hb:
        return l
    if l == hb or r == hb:
        return None
    if mode & 1 and l == r:
        return l
    rules = ()
    if mode & 2:
        rules += (("_", "|/\\[]{}()<>"),)
    if mode & 4:
        rules += (("|", "/\\[]{}()<>"), ("\\/", "[]{}()<>"), ("[]", "{}()<>"), ("{}", "()<>"), ("()", "<>"))
    for a, b in rules:
        if l in a and r in b:
            return r
        if r in a and l in b:
            return l
    if mode & 8 and (l + r in ("[]", "{}", "()") or r + l in ("[]", "{}", "()")):
        return "|"
    if mode & 16:
        if l == "/" and r == "\\":
            return "|"
        if l == "\\" and r == "/":
            return "Y"
        if l == ">" and r == "<":
            return "X"
    return None


def _fig_add(buf, pw, g, font):
    """Append glyph rows g to buffer rows buf (figlet horizontal layout) -> (new rows, total width)."""
    hb, h, mode, _c = font
    cw = len(max(g, key=len)) if g else 0
    amt = 0
    if mode & 192:
        amt = cw
        for L, R in zip(buf, g):
            lb = max(len(L.rstrip(" ")) - 1, 0)
            c1 = L[lb] if lb < len(L) else ""
            if lb >= len(L):
                lb = 0
            cb = len(R) - len(R.lstrip(" "))
            c2 = R[cb] if cb < len(R) else ""
            a = cb + len(L) - 1 - lb
            if c1 in ("", " ") or (c2 and _fig_smush(c1, c2, mode, hb, pw, cw) is not None):
                a += 1
            amt = min(amt, a)
    out = []
    for L, R in zip(buf, g):
        L = list(L)
        for i in range(amt):
            k = len(L) - amt + i
            if 0 <= k < len(L):
                L[k] = _fig_smush(L[k], R[i], mode, hb, pw, cw)
        out.append("".join(L) + R[amt:])
    return out, cw


def figlet_enc(s, font="standard", width=80):
    """pyfiglet.figlet_format(s, font, width) (left-justified, hardblanks -> spaces); width=0: no wrap."""
    try:
        f = _fig_font(font)
    except Exception:  # noqa: BLE001
        return None
    hb, h, mode, chars = f
    blocks, buf, pw, marks, i = [], [""] * h, 0, [], 0
    while i < len(s):
        c = s[i]
        g = chars.get(c)
        if g is None:
            i += 1
            continue
        if c == " ":
            marks.append((list(buf), i))
        new, cw = _fig_add(buf, pw, g, f)
        if width and len(new[0]) >= width and buf[0]:
            if marks:
                saved, i = marks.pop()
                blocks.append(saved)
            else:
                blocks.append(buf)
                i -= 1
            buf, pw, marks = [""] * h, 0, []
            i += 1
            continue
        buf, pw = new, cw
        i += 1
    if buf[0]:
        blocks.append(buf)
    return "".join("\n".join(b) + "\n" for b in blocks).replace(hb, " ")


def _fig_block(rows, f, budget, wild0=False):
    """Text whose (unwrapped) rendering is exactly rows (hardblanks shown as spaces), else None. Depth-first over
    glyphs on a sliding window of the buffer tail (only the last glyph-width columns can still change). wild0: row 0
    is not compared (a caller's .strip() may have eaten its indent; the caller re-checks it)."""
    hb, h, mode, chars = f
    want = [r.rstrip(" ") for r in rows]
    if not any(want) or len(rows) != h:
        return None
    wmax = max(len(x) for x in want)
    pad = [x.ljust(wmax + 64) for x in want]
    if wild0:
        pad[0] = None
    cmp = [r for r in range(h) if pad[r] is not None]
    win = max(len(max(g, key=len)) for g in chars.values()) + 2
    items = []
    for c, g in chars.items():
        cw = len(max(g, key=len)) if g else 0
        items.append((c, g, cw, [(len(R) - len(R.lstrip(" ")), R.lstrip(" ")[:1]) for R in g]))
    steps = [0]
    drop = 1 if mode & 128 else 0   # smushing may still rewrite each row's last visible char; kerning never does
    dead = set()

    def add(off, tail, edge, pw, g, cw, prof):
        amt = 0
        if mode & 192:
            amt = cw
            for (ln, lb, c1), (cb, c2) in zip(edge, prof):
                a = cb + ln - 1 - lb
                if c1 in ("", " ") or (c2 and _fig_smush(c1, c2, mode, hb, pw, cw) is not None):
                    a += 1
                if a < amt:
                    amt = a
        for r, (L, R) in enumerate(zip(tail, g)):   # the appended part R[amt:] never changes again (but its last mark)
            q = R[amt:].replace(hb, " ").rstrip(" ")
            q = q[:len(q) - drop]
            if q and pad[r] is not None and pad[r][off + len(L):off + len(L) + len(q)] != q:
                return None
        out = []
        for L, R in zip(tail, g):
            if amt:
                n = len(L)
                L = list(L)
                for i in range(amt):
                    k = n - amt + i
                    if 0 <= k:
                        L[k] = _fig_smush(L[k], R[i], mode, hb, pw, cw)
                L = "".join(L)
            out.append(L + R[amt:])
        return out

    def dfs(off, tail, pw, text):
        steps[0] += 1
        if steps[0] > budget:
            return None
        if text and all(pad[r][off:].rstrip(" ") == tail[r].replace(hb, " ").rstrip(" ") for r in cmp):
            return text
        cands = []
        edge = []
        for L in tail:
            lb = max(len(L.rstrip(" ")) - 1, 0)
            c1 = L[lb] if lb < len(L) else ""
            edge.append((len(L), 0 if lb >= len(L) else lb, c1))
        for c, g, cw, prof in items:
            new = add(off, tail, edge, pw, g, cw, prof)
            if new is None:
                continue
            if c != " " and len(new[0]) <= len(tail[0]):
                continue
            vis = [x.replace(hb, " ") for x in new]
            if off + len(vis[0]) > wmax + 64:
                continue
            good = True
            for r in cmp:
                p = vis[r].rstrip(" ")
                p = p[:len(p) - drop]
                if pad[r][off:off + len(p)] != p:
                    good = False
                    break
            if not good:
                continue
            k = max(len(new[0]) - win, 0)
            if k and any(pad[r][off:off + k] != vis[r][:k] for r in cmp):
                continue
            cands.append((-sum(len(x.rstrip(" ")) for x in vis), c == " ", c, k, new, cw))
        cands.sort(key=lambda x: x[:2])
        for _w, _s, c, k, new, cw in cands[:6]:
            if c == " " and text.endswith(" "):
                continue
            key = (off + k, tuple(x[k:] for x in new), cw, c == " ")
            if key in dead:
                continue
            r = dfs(off + k, list(key[1]), cw, text + c)
            if r is not None:
                return r
            dead.add(key)
        return None

    return dfs(0, [""] * h, 0, "")


_FIG_SENT = re.compile(re.escape(SENTENCE.format(slug="\x00")).replace("\x00", SLUG.pattern))


def figlet_reads(t):
    try:
        t = _t(t) if not isinstance(t, str) else t
    except Exception:  # noqa: BLE001
        return []
    return list(_figlet_reads(t)) if isinstance(t, str) else []


@functools.lru_cache(maxsize=32)
def _figlet_reads(t):
    """[(font, text)] for a FIGlet banner in a vendored font: the rows cut into font-height blocks (width-80 wrap),
    each block decoded glyph by glyph, then the blocks joined (' ' at a blank wrap) and re-rendered to check. Never raises."""
    out = []
    try:
        lines = t.replace("\r\n", "\n").split("\n")
        while lines and not lines[-1].strip():
            lines.pop()
        while lines and not lines[0].strip() and len(lines) > 1:
            lines.pop(0)
        if len(lines) < 4 or len(t) > 60000 or not all(x.isascii() and x.isprintable() for x in lines):
            return out
        ind = min([len(x) - len(x.lstrip(" ")) for x in lines[1:] if x.strip()] or [0])
        views = [lines] + ([[x[ind:] for x in lines]] if ind else [])   # figlet.js / toilet: a left margin column
        for name, ls0 in itertools.product(_FIG_FONTS, views):
            if out and out[-1][0] == name:
                continue
            f = _fig_font(name)
            h = f[1]
            ls = list(ls0)
            while len(ls) % h:
                ls.append("")
            pieces = []
            for k in range(0, len(ls), h):   # row 0 checked after: blob.strip() may have eaten its indent
                p = _fig_block(ls[k:k + h], f, 4000, wild0=not k)
                if p is None or (not k and (figlet_enc(p, name, 0) or " ").split("\n")[0].strip(" ")
                                 != ls[0].strip(" ")):
                    break
                pieces.append(p)
            else:
                text = pieces[0] if pieces else None
                for p in pieces[1:]:
                    text += " " + p
                if not text:
                    continue
                if len(pieces) > 1:   # wrap at a blank (dropped) or mid-word: keep the joins that re-render the blocks
                    seps = []
                    for j, p in enumerate(pieces[1:], 1):
                        want = "\n".join(x.rstrip() for x in ls[(j - 1) * h:(j + 1) * h])
                        ok = [sep for sep in (" ", "") if "\n".join(x.rstrip() for x in (figlet_enc(
                            pieces[j - 1] + sep + p, name) or "").split("\n")[:2 * h]) == want]
                        seps.append(ok or [" "])
                    best = None
                    for combo in itertools.islice(itertools.product(*seps), 256):
                        cand = pieces[0] + "".join(sp + p for sp, p in zip(combo, pieces[1:]))
                        score = (2 if _FIG_SENT.fullmatch(cand) else 1 if SLUG.search(cand) else 0)
                        if best is None or score > best[0]:
                            best = (score, cand)
                    text = best[1]
                out.append((name, text.strip(" ")))
    except Exception:  # noqa: BLE001
        return tuple(out)
    return tuple(out)


def figlet_dec(t, font=None):
    for n, s in figlet_reads(t):
        if font in (None, n):
            return s
    return None


@functools.lru_cache(maxsize=None)
def _dm_tables():
    """{7 row ints (5 bits, MSB = left column): char}."""
    tab = {}
    for i in range(95):
        cols = _DM_COLS[5 * i:5 * i + 5]
        rows = tuple(sum(((cols[c] >> r) & 1) << (4 - c) for c in range(5)) for r in range(7))
        tab.setdefault(rows, chr(32 + i))
    return tab


def _dm_rows(c):
    i = ord(c) - 32
    if not 0 <= i < 95:
        return None
    cols = _DM_COLS[5 * i:5 * i + 5]
    return [sum(((cols[k] >> r) & 1) << (4 - k) for k in range(5)) for r in range(7)]


def dotmatrix_enc(s, form="blocks", on="#", off="."):
    """5x7 dot-matrix rendering: blocks = 7 rows of 5 per char, a blank line between chars; banner = one 7-row strip,
    1 off-column between glyphs; hexrows = 7 row bytes per char; hexcols = 5 column bytes per char (bit 0 = top)."""
    gl = [_dm_rows(c) for c in s]
    if any(g is None for g in gl):
        return None
    bit = lambda v, k: on if v >> (4 - k) & 1 else off
    if form == "blocks":
        return "\n\n".join("\n".join("".join(bit(v, k) for k in range(5)) for v in g) for g in gl)
    if form == "banner":
        return "\n".join(off.join("".join(bit(g[r], k) for k in range(5)) for g in gl) for r in range(7))
    if form == "hexrows":
        return " ".join(" ".join(f"{v:02x}" for v in g) for g in gl)
    if form == "hexcols":
        return " ".join(_DM_COLS[5 * (ord(c) - 32):5 * (ord(c) - 32) + 5].hex(" ") for c in s)
    return None


_DM_ON = "#*X@O1█■●x+o"
_DM_OFF = ". -_0░□○"


def _dm_glyphs_text(glyphs):
    tab = _dm_tables()
    out = []
    for g in glyphs:
        c = tab.get(tuple(g))
        if c is None:
            return None
        out.append(c)
    return "".join(out)


def _dm_nums(t):
    """Text from 5x7 numeric glyph tokens (hex / 0x.. / binary / decimal): 7 row values (5-bit, right- or left-aligned,
    either bit order, optional 8th zero row) or 5 column bytes (bit 0 or bit 6 = top) per char."""
    toks = re.findall(r"(?:0x)?[0-9a-fA-F]+", t)
    if len(toks) < 5 or len(toks) > 20000:
        return None
    if re.sub(r"(?:0x)?[0-9a-fA-F]+|[\s,;:\[\]{}()|/-]", "", t):
        return None
    vals = []
    for radix in ((2,) if all(set(x) <= set("01") and len(x) >= 5 for x in toks) else ()) + (16, 10):
        try:
            vals.append([int(x, radix) for x in toks])
        except ValueError:
            continue
    rev5 = lambda v: int(f"{v:05b}"[::-1], 2)
    for vs in vals:
        if max(vs) > 255:
            continue
        for n in (7, 8):   # row-major
            if len(vs) % n:
                continue
            gs = [vs[i:i + n] for i in range(0, len(vs), n)]
            if n == 8 and any(g[7] for g in gs):
                continue
            for fix in (lambda v: v, lambda v: v >> 3, rev5, lambda v: rev5(v >> 3) if v & 7 == 0 else 99):
                g2 = [[fix(v) for v in g[:7]] for g in gs]
                if any(v > 31 for g in g2 for v in g):
                    continue
                r = _dm_glyphs_text(g2)
                if r:
                    return r
        for n in (5, 8):   # column-major
            if len(vs) % n:
                continue
            gs = [vs[i:i + n] for i in range(0, len(vs), n)]
            if n == 8 and any(any(g[5:]) for g in gs):
                continue
            for top in (0, 6, 1, 7):
                g2 = []
                for g in gs:
                    cols = g[:5]
                    if top in (6, 7):
                        cols = [int(f"{c:08b}"[::-1], 2) >> (1 if top == 6 else 0) for c in cols]
                    elif top == 1:
                        cols = [c >> 1 for c in cols]
                    if any(c > 127 for c in cols):
                        break
                    g2.append([sum(((cols[k] >> r) & 1) << (4 - k) for k in range(5)) for r in range(7)])
                else:
                    r = _dm_glyphs_text(g2)
                    if r:
                        return r
    return None


def _dm_art(t):
    """Text from a 5x7 dot-matrix drawn in two symbols: per-char 7-row blocks (5 wide) or 7/8-row strips (glyph pitch
    5-8, strips stacked with optional separator lines)."""
    lines = t.replace("\r\n", "\n").split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)
    if len(lines) < 7:
        return None
    syms = set("".join(lines)) - {" "}
    if not syms or len(syms) > 2:
        return None
    ons = [c for c in syms if c not in _DM_OFF] or [c for c in syms if c in _DM_ON]
    if len(ons) != 1:
        return None
    on = ons[0]
    bits = [[1 if c == on else 0 for c in x] for x in lines]
    for sep in (1, 0, 2):   # per-char blocks
        if max(len(b) for b in bits) > 5:
            break
        step = 7 + sep
        if (len(bits) + sep) % step:
            continue
        gs = []
        for k in range(0, len(bits), step):
            blk = bits[k:k + 7]
            if any(any(x) for x in bits[k + 7:k + step]):
                break
            gs.append([sum(v << (4 - i) for i, v in enumerate((b + [0] * 5)[:5])) for b in blk])
        else:
            r = _dm_glyphs_text(gs)
            if r:
                return r
    for h in (7, 8):
        for sep in (0, 1, 2):
            step = h + sep
            if (len(bits) + sep) % step:
                continue
            strips = []
            for k in range(0, len(bits), step):
                blk = bits[k:k + h]
                if any(any(x) for x in bits[k + h:k + step]):
                    break
                if h == 8:
                    if any(blk[7]):
                        if any(blk[0]):
                            break
                        blk = blk[1:]
                    else:
                        blk = blk[:7]
                strips.append(blk)
            else:
                for pitch in (6, 8, 5, 7):
                    out = []
                    for blk in strips:
                        w = max(len(b) for b in blk)
                        n = (w + pitch - 1) // pitch
                        if n == 0:
                            out = None
                            break
                        rows = [b + [0] * (n * pitch - len(b)) for b in blk]
                        if any(any(r[j * pitch + 5:(j + 1) * pitch]) for r in rows for j in range(n)):
                            out = None
                            break
                        gs = [[sum(r[j * pitch + i] << (4 - i) for i in range(5)) for r in rows] for j in range(n)]
                        s = _dm_glyphs_text(gs)
                        if s is None:
                            out = None
                            break
                        out.append(s.rstrip(" ") if len(strips) > 1 else s)
                    if out:
                        return " ".join(out) if len(out) > 1 else out[0]
    return None


def dotmatrix_dec(t):
    """The text under a 5x7 dot-matrix rendering (two-symbol art or numeric glyph rows), else None. Never raises."""
    try:
        t = _t(t) if not isinstance(t, str) else t
        if len(t) > 200000:
            return None
        r = _dm_nums(t) if "\n" not in t.strip() or not set(t) - set("0123456789abcdefABCDEFx \t\r\n,;:[]{}()|/-") else None
        return r if r is not None else _dm_art(t)
    except Exception:  # noqa: BLE001
        return None


def asciiart_free(p):
    """Mastery fragment as 5x7 numeric glyph tokens (one line) -> [text]. Never raises."""
    try:
        r = _dm_nums(p) if isinstance(p, str) and "\n" not in p.strip() else None
        return [r] if r and r.isprintable() else []
    except Exception:  # noqa: BLE001
        return []


CANDIDATES += [(f"figlet-{f}", (lambda f: lambda s: figlet_enc(s, f))(f), (lambda f: lambda t: figlet_dec(t, f))(f))
               for f in _FIG_FONTS]
CANDIDATES += [(f"figlet-{f}-nowrap", (lambda f: lambda s: figlet_enc(s, f, 0))(f),
                (lambda f: lambda t: figlet_dec(t, f))(f)) for f in _FIG_FONTS]
CANDIDATES += [(f"dotmatrix5x7-{f}", (lambda f: lambda s: dotmatrix_enc(s, f))(f), dotmatrix_dec)
               for f in ("blocks", "banner", "hexrows", "hexcols")]


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
    ("dense-unicode", dense_free),
    ("base122", b122_free),
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
    ("cuswap", cuswap_free),
    ("cubin", cubin_free),
    ("inner-bytes", inner_free),
    ("invisible-tags-vs", invis_free),
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
    ("middle-endian", pdp_free),
    ("nibswap-hex", nibswap_free),
    ("wide-int", wint_free),
    ("float-charcodes", flt_free),
    ("leb128", leb_free),
    ("hexdump", hexdump_free),
    ("gsm7", gsm7_free),
    ("raw-wide", lambda p: [b for b in (wide_text_dec(p),) if b]),
    ("knob-sweep", knob_free),
    ("bignum", bignum_free),
    ("bigradix", bigradix_free),
    ("astral", astral_free),
    ("scsu-bocu", compressed_free),
    ("byteadd", byteadd_free),
    ("byterot", byterot_free),
    ("altbase", altbase_free),
    ("checksum-basen", chkbase_free),
    ("glyph-bytes", glyph_bytes_free),
    ("compress-sweep", decompress_free),
    ("xor-compressed", xorz_free),
    ("text-armor", armor_free),
    ("archive-container", archive_free),
    ("serialization-wrapper", ser_free),
    ("openssl-salted", openssl_free),
    ("lzstring", lzstring_free),
    ("jwt-jose", jwt_free),
    ("signed-cookie", signed_cookie_free),
    ("saml-redirect", saml_redirect_free),
    ("pdf-filter-chain", pdf_chain_free),
    ("inflate-container", container_free),
    ("http-chunked", chunked_free),
    ("text-compression", textcomp_free),
    ("yenc-binhex", retro_free),
    ("base85-any", b85_free),
    ("zalgo", zalgo_free),
    ("netstring-any", netstr_any_free),
    ("indexed-frames", frames_free),
    ("tnetstring", tnet_free),
    ("bencode-sexp", bencsexp_free),
    ("length-prefix", lenpfx_free),
    ("string-builder", strbuild_free),
    ("resp", resp_free),
    ("asn1-tlv", asn1_free),
    ("delimited-fields", delim_free),
    ("charnames", names_free),
    ("codepoint-any", codepoints_free),
    ("escape-soup", escsoup_free),
    ("cpshift", cpshift_free),
    ("delta-chain", delta_free),
    ("mojibake", mojibake_free),
    ("script-letter-map", scriptmap_free),
    ("ascii-art-dotmatrix", asciiart_free),
)


# ------------------------------------------- Brainfuck token dialects ("same language, other words", D26's sibling)
# Ook! / Blub (word + mark, PAIRED: '. ?' = >, '? .' = <, '. .' = +, '! !' = -, '! .' = ., '. !' = ,, '! ?' = [,
# '? !' = ]; short Ook = the bare marks), COW (moO > mOo < MoO + MOo - Moo out oom in MOO [ moo ] OOO zero), Pikalang
# (pipi > pichu < pi + ka - pikachu . pikapi , pika [ chu ]), Alphuck (a c e i j o p s = > < + - . , [ ]), ReverseFuck
# (+/- and </> swapped; or every command by its opposite, . , and [ ] too), Binaryfuck 3-bit (000..111 = > < + - . , [ ]).
# Any other <= 8-token set (Roadrunner's Meep case variants, a custom word map): tokens assigned to commands by the crib
# (the output must read 'Nice work' / a sentence piece), '[' ']' first by count + balance, '>' / '<' by first use (a
# mirrored tape prints the same), each try run-length compiled and dropped at its first off-crib / control byte.
_BF_OPS = "><+-.,[]"
_OOK_PAIRS = {".?": ">", "?.": "<", "..": "+", "!!": "-", "!.": ".", ".!": ",", "!?": "[", "?!": "]"}
_OOK_MARK = {v: k for k, v in _OOK_PAIRS.items()}
_BFD_WORDS = {
    "cow": {**dict(zip("moO mOo MoO MOo Moo oom MOO moo".split(), _BF_OPS)), "OOO": "z"},
    "pikalang": dict(zip("pipi pichu pi ka pikachu pikapi pika chu".split(), _BF_OPS)),
    "binaryfuck": dict(zip("000 001 010 011 100 101 110 111".split(), _BF_OPS)),
}
_BFD_CHARS = {
    "alphuck": dict(zip("aceijops", _BF_OPS)),
    "reversefuck": dict(zip("<>-+.,[]", _BF_OPS)),
    "reversefuck-full": dict(zip("<>-+,.][", _BF_OPS)),
}
_BFD_LOOSE = ("alphuck", "reversefuck", "reversefuck-full", "binaryfuck")   # single chars / bits: a piece needs the crib
_OOK_TOK = re.compile(r"(?:ook|blub)\s*([.?!])", re.I)


def bfd_enc(s, dialect="ook", sep=" "):
    """The GM's D26 Brainfuck (bf_enc) re-spelled in a token dialect: ook / blub / ook-short / cow / pikalang / alphuck
    / reversefuck / binaryfuck."""
    bf = bf_enc(s)
    if dialect in ("ook", "blub"):
        w = dialect.capitalize()
        return sep.join(f"{w}{_OOK_MARK[c][0]} {w}{_OOK_MARK[c][1]}" for c in bf)
    if dialect == "ook-short":
        return sep.join(_OOK_MARK[c] for c in bf)
    table = _BFD_WORDS.get(dialect) or _BFD_CHARS[dialect]
    inv = {v: k for k, v in table.items() if v != "z"}
    return sep.join(inv[c] for c in bf) if dialect in _BFD_WORDS else "".join(inv[c] for c in bf)


def _bf_run(code, want=b"", max_steps=600_000, quiet=25_000):
    """Run Brainfuck `code` ('z' = zero the cell; ',' reads nothing) run-length compiled -> output bytes, else None:
    unbalanced, a control byte, a byte off `want` (the output's required prefix), the step cap or a long silence."""
    ops, st = [], []
    for ch in code:
        if ch in "+-<>" and ops and ops[-1][0] == ch:
            ops[-1][1] += 1
        elif ch == "[":
            st.append(len(ops))
            ops.append(["[", 0])
        elif ch == "]":
            if not st:
                return None
            k = st.pop()
            ops[k][1] = len(ops)
            ops.append(["]", k])
        elif ch in "+-<>.z":
            ops.append([ch, 1])
    if st:
        return None
    tape, p, i, n, last, out, L = bytearray(65536), 0, 0, 0, 0, bytearray(), len(ops)
    while i < L:
        o, a = ops[i]
        if o == "+":
            tape[p] = (tape[p] + a) & 255
        elif o == "-":
            tape[p] = (tape[p] - a) & 255
        elif o == ">":
            p = (p + a) & 65535
        elif o == "<":
            p = (p - a) & 65535
        elif o == ".":
            b = tape[p]
            if b < 9 or 13 < b < 32 or b == 127 or (len(out) < len(want) and b != want[len(out)]):
                return None
            out.append(b)
            last = n
        elif o == "z":
            tape[p] = 0
        elif o == "[":
            if not tape[p]:
                i = a
        elif tape[p]:
            i = a
        i += 1
        n += 1
        if n > max_steps or n - last > quiet:
            return None
    return bytes(out)


def bfd_codes(t):
    """[(dialect, brainfuck)] for every named token dialect that spells the WHOLE text, strict first."""
    t = t.strip()
    out = []
    if _OOK_TOK.search(t) and not _OOK_TOK.sub("", t).strip():
        marks = _OOK_TOK.findall(t)
    elif re.fullmatch(r"[.?!\s]+", t) and re.search(r"[?!]", t):
        marks = re.findall(r"[.?!]", t)
    else:
        marks = None
    if marks and len(marks) % 2 == 0:
        out.append(("ook", "".join(_OOK_PAIRS[a + b] for a, b in zip(marks[::2], marks[1::2]))))
    toks = t.split()
    for name, table in _BFD_WORDS.items():
        if name == "binaryfuck" and len(toks) == 1 and re.fullmatch(r"(?:[01]{3})+", t):
            toks = [t[k:k + 3] for k in range(0, len(t), 3)]
        if toks and all(x in table for x in toks):
            out.append((name, "".join("[-]" if table[x] == "z" else table[x] for x in toks)))
    c = re.sub(r"\s", "", t)
    for name, table in _BFD_CHARS.items():
        if c and all(x in table for x in c):
            out.append((name, "".join(table[x] for x in c)))
    return out


def _bfd_text(b):
    try:
        x = b.decode("utf-8")
    except (UnicodeError, AttributeError):
        return None
    return x if x.strip() else None


def _bf_balanced(toks, a, b):
    d = 0
    for x in toks:
        d += (x == a) - (x == b)
        if d < 0:
            return False
    return d == 0


def bfd_solve(t, want=b"", piece=False, budget=0.6):
    """A <= 8-token Brainfuck dialect with unknown words: [(text, map)] for the command assignments whose output starts
    with `want` (whole blob) or is a sentence piece (`piece`), best first; [] when none fits within `budget` seconds."""
    toks = t.split()
    if len(toks) < 2:
        toks = list(re.sub(r"\s", "", t))
    distinct = list(dict.fromkeys(toks))
    if not 3 <= len(distinct) <= 8 or len(toks) < 12:
        return []
    cnt = collections.Counter(toks)
    pairs = [(a, b) for a in distinct for b in distinct if a != b and cnt[a] == cnt[b] and _bf_balanced(toks, a, b)]
    pairs = ([None] + pairs) if len(distinct) <= 5 else (pairs + [None])
    t0, found = time.monotonic(), []
    for pr in pairs:
        rest = [x for x in distinct if not pr or x not in pr]
        if len(rest) > 6:
            continue
        for perm in itertools.permutations("><+-.," if len(rest) == 6 else "><+-.", len(rest)):
            if time.monotonic() - t0 > budget:
                return found
            if "." not in perm or ("+" not in perm and "-" not in perm):
                continue
            if ">" in perm and "<" in perm and perm.index("<") < perm.index(">"):
                continue   # the mirrored tape prints the same text
            m = dict(zip(rest, perm))
            if pr:
                m[pr[0]], m[pr[1]] = "[", "]"
            out = _bfd_text(_bf_run("".join(m[x] for x in toks), want))
            if out is None or (want and not out.encode().startswith(want)):
                continue
            if piece and not _crib_piece(out):
                continue
            found.append((out, m))
            if not piece:
                return found
    found.sort(key=lambda om: -_crib_piece(om[0]))
    return found


def bfd_dec(t):
    """Undo a Brainfuck token dialect (named first, then the crib-solved unknown map) -> the printed text; raises."""
    for _name, code in bfd_codes(t):
        out = _bfd_text(_bf_run(code, max_steps=5_000_000, quiet=500_000))
        if out:
            return out
    got = bfd_solve(t, _CRIB[:9].encode())
    if got:
        return got[0][0]
    raise ValueError("not a Brainfuck token dialect")


def bfd_free(p):
    """Mastery free line: a named token dialect's output (a loose single-char / bit dialect only as a sentence piece),
    else the crib-solved unknown word map's sentence pieces."""
    try:
        outs = []
        for name, code in bfd_codes(p):
            out = _bfd_text(_bf_run(code))
            if out and out not in outs and (name not in _BFD_LOOSE or _crib_piece(out)):
                outs.append(out)
        if not outs and len(p.split()) >= 20:
            outs = [o for o, _m in bfd_solve(p, piece=True, budget=0.3)[:3]]
        return outs
    except (ValueError, IndexError, KeyError, TypeError):
        return []


CANDIDATES += [(f"bf-{d}", (lambda d: lambda s: bfd_enc(s, d))(d), bfd_dec)
               for d in ("ook", "blub", "ook-short", "cow", "pikalang", "alphuck", "reversefuck", "binaryfuck")]
CANDIDATES += [("bf-ook-short-run", lambda s: bfd_enc(s, "ook-short", ""), bfd_dec),
               ("bf-binaryfuck-run", lambda s: bfd_enc(s, "binaryfuck", ""), bfd_dec),
               ("bf-token-map", lambda s: None, bfd_dec)]   # crib-solved unknown map: this entry's enc never matches
SPECULATIVE_FREE += (("bf-dialect", bfd_free),)


# ------------------------------------------- Full Brainfuck programs (D26's family beyond the GM's one-cell delta)
# Any real program: multiply loops (n = a*b + c per char), cell-per-char text generators ('++++++++++[>+++++++>++++++++
# ++>+++<<<-]>++.>+.'), comment text between the commands (everything but the 8 commands is a comment), pointer moves
# below cell 0 (wrap), ',' input (reads 0 / EOF=-1 / unchanged), 16-bit or unbounded cells when 8-bit wrap prints junk.
# Also behind a peel: a base64 / base32 / hex / gzip-zlib-bz2-lzma layer whose bytes are Brainfuck soup. Only claimed
# when the printed text is printable and passes the slug / crib gate (Morse '.'/'-' lines print junk -> not claimed).
_BFF_CMDS = re.compile(r"[^+\-<>\[\].,]")


def bf_run(prog, steps=10**7, cells=65536, bits=8, eof=0, quiet=None):
    """Run Brainfuck `prog` (non-command chars = comments) -> [output cell values], or None when unbalanced or over
    `steps` (run-length compiled ops; '[-]' / '[+]' = clear). bits=8/16 wrap, bits=0 unbounded ints; ',' stores
    `eof` (0, -1, or None = leave the cell); the pointer wraps over `cells`; `quiet` = max ops between outputs."""
    c = _BFF_CMDS.sub("", prog)
    c = c.replace("[-]", "z").replace("[+]", "z")
    ops, st = [], []
    for ch in c:
        if ch in "+-<>" and ops and ops[-1][0] == ch:
            ops[-1][1] += 1
        elif ch == "[":
            st.append(len(ops))
            ops.append(["[", 0])
        elif ch == "]":
            if not st:
                return None
            k = st.pop()
            ops[k][1] = len(ops)
            ops.append(["]", k])
        else:
            ops.append([ch, 1])
    if st:
        return None
    mask = (1 << bits) - 1 if bits else None
    tape, p, i, n, last, out, L = [0] * cells, 0, 0, 0, 0, [], len(ops)
    while i < L:
        o, a = ops[i]
        if o == "+":
            v = tape[p] + a
            tape[p] = v & mask if mask else v
        elif o == "-":
            v = tape[p] - a
            tape[p] = v & mask if mask else v
        elif o == ">":
            p = (p + a) % cells
        elif o == "<":
            p = (p - a) % cells
        elif o == ".":
            out.append(tape[p])
            last = n
        elif o == "z":
            tape[p] = 0
        elif o == ",":
            if eof is not None:
                tape[p] = eof & mask if mask else eof
        elif o == "[":
            if not tape[p]:
                i = a
        elif tape[p]:
            i = a
        i += 1
        n += 1
        if n > steps or (quiet and n - last > quiet):
            return None
    return out


def _bff_text(vals):
    """Printed cell values -> text (UTF-8 bytes when every value is a byte, else code points); None = junk/control."""
    if not vals:
        return None
    try:
        x = bytes(vals).decode("utf-8") if all(0 <= v < 256 for v in vals) else "".join(chr(v) for v in vals)
    except (ValueError, UnicodeError, OverflowError):
        return None
    if not x.strip() or any((ord(ch) < 32 and ch not in "\t\n\r") or 127 <= ord(ch) < 160 for ch in x):
        return None
    return x


def _bff_soup(t):
    """The command string of `t` when it reads as a Brainfuck program: balanced, >= 1 '.', a cell change."""
    c = _BFF_CMDS.sub("", t)
    if "." not in c or not re.search(r"[+-]", c):
        return None
    d = 0
    for ch in c:
        d += (ch == "[") - (ch == "]")
        if d < 0:
            return None
    return c if d == 0 else None


def _bff_outs(t, steps=2_000_000):
    """Every distinct printable output of `t` run as Brainfuck: 8-bit wrap, then 16-bit, then unbounded cells, each
    with ',' = 0, then (only when the program reads) EOF=-1 and 'unchanged'."""
    c = _bff_soup(t)
    if c is None:
        return []
    outs = []
    for bits in (8, 16, 0):
        for eof in ((0, -1, None) if "," in c else (0,)):
            x = _bff_text(bf_run(c, steps=steps, bits=bits, eof=eof, quiet=steps // 4))
            if x and x not in outs:
                outs.append(x)
        if outs:
            break
    return outs


def _bff_gate(x, piece=False):
    if piece:
        return _crib_piece(x) > 0
    return bool(_crib_piece(x) or SLUG.search(x))


def _bff_peel(t, depth=3):
    """Texts under base64 / base32 / hex / compression layers of `t` (decompress-then-redecode stacks), `t` first."""
    seen, todo, out = set(), [(t.strip(), 0)], []
    while todo and len(out) < 24:
        x, k = todo.pop(0)
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
        if k >= depth:
            continue
        s = re.sub(r"\s", "", x)
        raws = []
        if re.fullmatch(r"(?:[0-9A-Fa-f]{2})+", s):
            raws.append(bytes.fromhex(s))
        if re.fullmatch(r"[A-Za-z0-9+/_-]{8,}={0,2}", s):
            try:
                raws.append(base64.b64decode(s.replace("-", "+").replace("_", "/") + "=" * (-len(s) % 4)))
            except (binascii.Error, ValueError):
                pass
        if re.fullmatch(r"[A-Z2-7]{8,}=*", s):
            try:
                raws.append(base64.b32decode(s + "=" * (-len(s) % 8)))
            except (binascii.Error, ValueError):
                pass
        for raw in raws:
            for b in _bff_unpack(raw):
                try:
                    todo.append((b.decode("utf-8").strip(), k + 1))
                except UnicodeError:
                    pass
    return out


def _bff_unpack(raw):
    import bz2
    import lzma
    out = [raw]
    for fn in (gzip.decompress, zlib.decompress, lambda b: zlib.decompress(b, -15), bz2.decompress, lzma.decompress):
        try:
            out.append(fn(raw)[:1 << 20])
        except Exception:  # noqa: BLE001 - not this container
            pass
    return out


def bff_dec(t):
    """A full Brainfuck program (comments, loops, 8/16-bit/unbounded cells, ',' input), possibly under a base64 / hex /
    compression peel -> the printed sentence; raises unless the output is printable and passes the slug / crib gate."""
    for x in _bff_peel(t):
        for out in _bff_outs(x):
            if _bff_gate(out):
                return out
    raise ValueError("not a Brainfuck program")


def bff_free(p):
    """Mastery free line: the printed text of a full Brainfuck program (or one under a peel) when it is a crib piece."""
    try:
        return [o for x in _bff_peel(p, 2) for o in _bff_outs(x, 1_000_000) if _bff_gate(o, True)][:3]
    except (ValueError, IndexError, KeyError, TypeError, RecursionError, MemoryError):
        return []


def bff_mul_enc(s):
    """Multiply-loop generator: per UTF-8 byte n = a*b + c from a cleared cell -> '>' + a '+'s + '[<' b '+'s '>-]<' +
    c '+'s '.[-]' (a ~ sqrt n)."""
    out = []
    for n in _u(s):
        a = max(1, int(math.isqrt(n)))
        b, c = divmod(n, a)
        out.append(">" + "+" * a + "[<" + "+" * b + ">-]<" + "+" * c + ".[-]")
    return "".join(out)


def bff_gen_enc(s):
    """The common 'bf text generator' output: a shared 10x loop seeds one cell per distinct byte (n//10 *10), then each
    char moves to its cell, trims by +/- and prints."""
    bs = list(_u(s))
    distinct = sorted(set(bs))
    head = "+" * 10 + "[" + "".join(">" + "+" * (n // 10) for n in distinct) + "<" * len(distinct) + "-]"
    vals, cur, out = {n: n // 10 * 10 for n in distinct}, 0, [head]
    for n in bs:
        cell = distinct.index(n) + 1
        out.append(">" * (cell - cur) if cell > cur else "<" * (cur - cell))
        cur, d = cell, n - vals[n]
        out.append("+" * d if d > 0 else "-" * -d)
        vals[n] = n
        out.append(".")
    return "".join(out)


CANDIDATES += [("bf-full-delta", bf_enc, bff_dec), ("bf-full-mul", bff_mul_enc, bff_dec),
               ("bf-full-gen", bff_gen_enc, bff_dec)]
SPECULATIVE_FREE += (("bf-full", bff_free),)


# ------------------------------------------------------------------- Deadfish ("a very small language", 4 commands)
# One accumulator v = 0: i +1, d -1, s v*v, o output (chr(v) in the text-printing variant); after EVERY op v == -1 or
# v == 256 resets to 0. XKCD variant: x +1, k square, c output, d -1. Either case. A line of English words spelled
# only from i/d/s/o ('dido is odd') prints control bytes -> not claimed.
_DF_SETS = {"idso": "idso", "xkcd": "xdkc"}   # dialect -> its letters for (inc, dec, square, out)
_DF_CAP = 1 << 32


def deadfish_enc(s, style="delta", xkcd=False, sep="", upper=False):
    """Deadfish printing each UTF-8 byte: 'delta' = i/d runs from the last value then o; 'square' = the cheaper of a run
    or (run to r, s, run to n) per byte."""
    out, v = [], 0
    for n in _u(s):
        best = "i" * (n - v) if n >= v else "d" * (v - n)
        if style == "square":
            for r in range(16):
                c = ("i" * (r - v) if r >= v else "d" * (v - r)) + "s" + ("i" * (n - r * r) if n >= r * r
                                                                          else "d" * (r * r - n))
                if len(c) < len(best):
                    best = c
        out.append(best + "o")
        v = n
    t = sep.join(out)
    if xkcd:
        t = t.translate(str.maketrans("idso", "xdkc"))
    return t.upper() if upper else t


def deadfish_vals(t):
    """The numbers a Deadfish / XKCD-Deadfish program outputs, else None (a foreign char, no output, a runaway v)."""
    c = re.sub(r"\s", "", t or "").lower()
    if not c:
        return None
    for letters in _DF_SETS.values():
        if set(c) <= set(letters) and letters[3] in c:
            inc, dec, sq, out = letters
            v, vals = 0, []
            for ch in c:
                if ch == inc:
                    v += 1
                elif ch == dec:
                    v -= 1
                elif ch == sq:
                    v *= v
                else:
                    vals.append(v)
                if v == -1 or v == 256:
                    v = 0
                if v > _DF_CAP:
                    return None
            return vals
    return None


def _df_text(vals):
    if all(0 <= n < 256 for n in vals):
        b = bytes(vals)
        try:
            x = b.decode("utf-8")
        except UnicodeError:
            x = b.decode("latin-1")
    elif all(0 <= n < 0x110000 for n in vals):
        x = "".join(map(chr, vals))
    else:
        return None
    return x if x.strip() and all(ch.isprintable() or ch in "\t\n\r" for ch in x) else None


def deadfish_dec(t):
    """Undo Deadfish / XKCD Deadfish (chr of each output) -> the printed text; raises on a non-program / junk output."""
    vals = deadfish_vals(t)
    x = _df_text(vals) if vals else None
    if x is None:
        raise ValueError("not a Deadfish program")
    return x


def deadfish_free(p):
    """Mastery free line: a Deadfish program's printed text (crib / slug piece or prose-like), else its numbers."""
    try:
        vals = deadfish_vals(p)
        if not vals:
            return []
        x = _df_text(vals)
        if x and (_crib_piece(x) or _texty(x) >= 0.9):
            return [x]
        return []
    except (ValueError, TypeError, OverflowError):
        return []


CANDIDATES += [("deadfish-delta", deadfish_enc, deadfish_dec),
               ("deadfish-delta-sp", lambda s: deadfish_enc(s, sep=" "), deadfish_dec),
               ("deadfish-square", lambda s: deadfish_enc(s, "square"), deadfish_dec),
               ("deadfish-square-sp", lambda s: deadfish_enc(s, "square", sep=" "), deadfish_dec),
               ("deadfish-xkcd-delta", lambda s: deadfish_enc(s, xkcd=True), deadfish_dec),
               ("deadfish-xkcd-square", lambda s: deadfish_enc(s, "square", xkcd=True), deadfish_dec),
               ("deadfish-xkcd-square-sp", lambda s: deadfish_enc(s, "square", True, " "), deadfish_dec),
               ("deadfish-square-sp-upper", lambda s: deadfish_enc(s, "square", sep=" ", upper=True), deadfish_dec)]
SPECULATIVE_FREE += (("deadfish", deadfish_free),)


# ------------------------------------------- Whitespace (the esolang, D26's sibling: a program, not whitespace stego)
# Only ' ' (S), '\t' (T) and '\n' (L) are code, every other char a comment; or the visible spellings: S/T/L (or S/T/N)
# letters, [Space]/[Tab]/[LF] tokens. IMPs: S stack (S n push, LS dup, TS n copy, LT swap, LL drop, TL n slide), TS
# arithmetic (SS + ST - SL * TS / TT %), TT heap (S store, T fetch), L flow (SS mark, ST call, SL jump, TS jz, TT jneg,
# TL ret, LL end), TL I/O (SS out char, ST out num, TS/TT read -> 0). Numbers: sign S=+ T=-, bits S=0 T=1, L ends;
# labels: S/T bits, L ends. Typical generator output = push+outchar per char then LLL; loop forms (a 0-terminated
# stack/heap string printed by a labelled loop) run under a step cap. Claimed only when the WHOLE code parses, the run
# ends cleanly and prints printable text; an 8-bit space/tab stego blob (no LF, or junk parse) falls to ws_cands.
_WSL_BRACKET = re.compile(r"\[\s*(space|spc|sp|s|tab|t|lf|line\s*feed|newline|nl|n|l)\s*\]", re.I)
_WSL_TOK = {"space": "S", "spc": "S", "sp": "S", "s": "S", "tab": "T", "t": "T"}
_WSL_OPS = (("SS", "push", 1), ("SLS", "dup", 0), ("STS", "copy", 1), ("SLT", "swap", 0), ("SLL", "drop", 0),
            ("STL", "slide", 1), ("TSSS", "add", 0), ("TSST", "sub", 0), ("TSSL", "mul", 0), ("TSTS", "div", 0),
            ("TSTT", "mod", 0), ("TTS", "store", 0), ("TTT", "fetch", 0), ("LSS", "mark", 2), ("LST", "call", 2),
            ("LSL", "jump", 2), ("LTS", "jz", 2), ("LTT", "jneg", 2), ("LTL", "ret", 0), ("LLL", "end", 0),
            ("TLSS", "outc", 0), ("TLST", "outn", 0), ("TLTS", "readc", 0), ("TLTT", "readn", 0))


def wsl_enc(s, form="raw", loop=False):
    """Whitespace program printing s: push + output-char per code point then end (`loop`: push a 0 then the chars
    reversed, print with a dup/jz/outc/jump loop). form raw (real space/tab/LF) / stl (letters) / bracket tokens."""
    def num(n):
        return ("T" if n < 0 else "S") + format(abs(n), "b").replace("0", "S").replace("1", "T") + "L"
    if loop:
        c = "SS" + num(0) + "".join("SS" + num(ord(ch)) for ch in reversed(s))
        c += "LSS" + "SL" + "SLS" + "LTS" + "TL" + "TLSS" + "LSL" + "SL" + "LSS" + "TL" + "LLL"
    else:
        c = "".join("SS" + num(ord(ch)) + "TLSS" for ch in s) + "LLL"
    if form == "stl":
        return c
    if form == "bracket":
        return "".join({"S": "[Space]", "T": "[Tab]", "L": "[LF]\n"}[x] for x in c)
    return c.translate(str.maketrans("STL", " \t\n"))


def _wsl_code(t):
    """The S/T/L command string of t (bracket tokens, S/T/L|N letters, else the raw space/tab/LF), or None."""
    if not isinstance(t, str) or len(t) > 400000:
        return None
    toks = _WSL_BRACKET.findall(t)
    if len(toks) >= 8 and not _WSL_BRACKET.sub("", t).strip(" \t\r\n,;|"):
        return "".join(_WSL_TOK.get(re.sub(r"\s", "", x).lower(), "L") for x in toks)
    c = re.sub(r"\s", "", t)
    if len(c) >= 8 and (re.fullmatch(r"[STL]+", c) or re.fullmatch(r"[STN]+", c)) and "T" in c and c[-1] in "LN":
        return c.replace("N", "L")
    if "\t" in t and "\n" in t:
        return re.sub(r"[^ \t\n]", "", t).translate(str.maketrans(" \t\n", "STL"))
    return None


def _wsl_parse(c):
    """[(op, arg)] + {label: index} for the WHOLE command string c (a dangling tail after an `end` is dropped), or
    None on an unknown / unterminated instruction or a duplicate label."""
    prog, labels, i, n, ended = [], {}, 0, len(c), False
    while i < n:
        for pre, op, kind in _WSL_OPS:
            if c.startswith(pre, i):
                break
        else:
            return (prog, labels) if ended else None
        i += len(pre)
        arg = None
        if kind:
            j = c.find("L", i)
            if j < 0:
                return (prog, labels) if ended else None
            body = c[i:j]
            i = j + 1
            if kind == 1:
                bits = body[1:] if body[:1] in ("S", "T") else body
                arg = int(bits.replace("S", "0").replace("T", "1") or "0", 2) * (-1 if body[:1] == "T" else 1)
            else:
                arg = body
        if op == "mark":
            if arg in labels:
                return None
            labels[arg] = len(prog)
        else:
            prog.append((op, arg))
            ended = ended or op == "end"
    return prog, labels


def wsl_run(c, steps=300_000):
    """Run a Whitespace command string -> the printed text, else None (bad parse / label / stack, step cap, nothing
    printed, a control or non-text char out)."""
    got = _wsl_parse(c)
    if not got:
        return None
    prog, labels = got
    if any(op in ("call", "jump", "jz", "jneg") and a not in labels for op, a in prog):
        return None
    st, heap, calls, out, pc, k, L = [], {}, [], [], 0, 0, len(prog)
    try:
        while pc < L:
            k += 1
            if k > steps or len(st) > 100000:
                return None
            op, a = prog[pc]
            pc += 1
            if op == "push":
                st.append(a)
            elif op == "dup":
                st.append(st[-1])
            elif op == "copy":
                if a < 0:
                    return None
                st.append(st[-1 - a])
            elif op == "swap":
                st[-1], st[-2] = st[-2], st[-1]
            elif op == "drop":
                st.pop()
            elif op == "slide":
                top = st.pop()
                del st[len(st) - max(a, 0):]
                st.append(top)
            elif op in ("add", "sub", "mul", "div", "mod"):
                y, x = st.pop(), st.pop()
                if op in ("div", "mod") and not y:
                    return None
                st.append({"add": x + y, "sub": x - y, "mul": x * y, "div": x // y if op == "div" else 0,
                           "mod": x % y if op == "mod" else 0}[op])
                if abs(st[-1]) > 1 << 64:
                    return None
            elif op == "store":
                v, addr = st.pop(), st.pop()
                heap[addr] = v
            elif op == "fetch":
                st.append(heap.get(st.pop(), 0))
            elif op == "call":
                calls.append(pc)
                pc = labels[a]
            elif op == "jump":
                pc = labels[a]
            elif op == "jz":
                if st.pop() == 0:
                    pc = labels[a]
            elif op == "jneg":
                if st.pop() < 0:
                    pc = labels[a]
            elif op == "ret":
                pc = calls.pop()
            elif op == "end":
                break
            elif op == "outc":
                v = st.pop()
                if not 0 <= v < 0x110000:
                    return None
                out.append(chr(v))
            elif op == "outn":
                out.append(str(st.pop()))
            elif op in ("readc", "readn"):
                heap[st.pop()] = 0
    except IndexError:
        return None
    x = "".join(out)
    if x and max(map(ord, x)) < 256 and re.search(r"[\x80-\xff]", x):
        try:
            x = x.encode("latin-1").decode("utf-8")
        except UnicodeError:
            pass
    if not x.strip() or any((ord(ch) < 32 and ch not in "\t\n\r") or 127 <= ord(ch) < 160 for ch in x):
        return None
    return x


def wsl_text(t):
    """The text a Whitespace program (raw or visible notation) prints, else None. Never raises."""
    try:
        c = _wsl_code(t)
        if not c or "TLS" not in c:
            return None
        x = wsl_run(c)
        return x if x and any(ch.isalpha() for ch in x) else None
    except (ValueError, TypeError, RecursionError, MemoryError):
        return None


def wsl_dec(t):
    """Undo a Whitespace-language program -> the printed text; raises when t is not one."""
    x = wsl_text(t)
    if x is None:
        raise ValueError("not a Whitespace program")
    return x


def wsl_free(p):
    """Mastery free line: a Whitespace program's printed text when it is a crib / slug piece or prose-like."""
    x = wsl_text(p)
    return [x] if x and (_crib_piece(x) or SLUG.search(x) or _texty(x) >= 0.9) else []


_k = next(i for i, c in enumerate(CANDIDATES) if c[0] == "zw-bits8")   # before zero-width / whitespace stego
CANDIDATES[_k:_k] = [("ws-lang", wsl_enc, wsl_dec), ("ws-lang-loop", lambda s: wsl_enc(s, loop=True), wsl_dec),
                     ("ws-lang-stl", lambda s: wsl_enc(s, "stl"), wsl_dec),
                     ("ws-lang-bracket", lambda s: wsl_enc(s, "bracket"), wsl_dec)]
_k = next(i for i, c in enumerate(SPECULATIVE_FREE) if c[0] == "zerowidth")
SPECULATIVE_FREE = SPECULATIVE_FREE[:_k] + (("whitespace-lang", wsl_free),) + SPECULATIVE_FREE[_k:]
del _k


# ------------------------------------------- Befunge-93/98 and ><> (Fish): 2-D grid languages ("think in two dimensions")
# One stack, a PC at (0,0) moving right over a torus of the program's lines. Befunge: 0-9 (98: a-f) push, + - * / %
# (x/0 -> 0), ! ` > < ^ v (? = > deterministic), _ | ifs, " string mode pushes ords, : \ $ . , # g p & (0) ~ (-1), @
# end; 98 extras ; ' s j n r [ ] w q z; unknown = nop. Grid = max(80x25, text bounds) first (93 wrap), then the text
# bounds (98). ><>: 0-9a-f, + - * , % = ) (, ! ? trampolines, mirrors / \ | _ # and arrows, x = >, : ~ $ @ } { r l, o n
# output, ' " strings, g p . & i (-1), ; end, anything else / an error -> no read. Claimed only when the run ends and
# prints printable text with a letter (an ASCII-art banner of / \ | _ @ prints nothing or junk -> not claimed).
_BEF_CAP, _BEF_IDLE = 1_000_000, 60_000


def _bef_num(n, top=9, hexd=False):
    """Digits pushing n >= 0 under a digit limit `top`: d | ab* | ab*c+ | (recursive) xb*c+."""
    dig = "0123456789abcdef"
    if n <= top:
        return dig[n]
    for a in range(top, 1, -1):
        if n % a == 0 and n // a <= top:
            return dig[a] + dig[n // a] + "*"
    q, r = divmod(n, top)
    return _bef_num(q, top) + dig[top] + "*" + (dig[r] + "+" if r else "")


def _bef_str(s, q='"', top=9):
    """String-mode push of s (pushed left to right), a quote char pushed numerically between string runs."""
    out, run = [], ""
    for ch in s:
        if ch == q:
            if run:
                out.append(q + run + q)
                run = ""
            out.append(_bef_num(ord(q), top))
        else:
            run += ch
    if run:
        out.append(q + run + q)
    return "".join(out)


def befunge_enc(s, style="line", w=60):
    """Befunge-93 printing s: 'line' = the classic `"<s reversed>">:#,_@`; 'grid' = the 0 + reversed sentence pushed
    in w-char rows (`>"..."  v` / `v  <` pairs) then a `>:#,_@` print row."""
    r = s[::-1]
    if style == "line":
        return _bef_str(r) + ">:#,_@"
    rows = [_bef_str(r[i:i + w]) for i in range(0, len(r), w)] or [""]
    rows[0] = "0" + rows[0]
    wid = max(len(x) for x in rows) + 2
    out = []
    for x in rows:
        out.append((">" + x).ljust(wid) + "v")
        out.append("v".ljust(wid) + "<")
    out.append(">:#,_@")
    return "\n".join(out)


def fish_enc(s, style="mirror"):
    """><> printing s: 'mirror' = the classic `"<s>"r\\` over `o;!?l<`; 'line' = `"<s reversed>"` then a looped
    one-row printer reached by a v / < return row."""
    q = "'" if '"' in s and "'" not in s else '"'
    if style == "mirror":
        top = _bef_str(s, q, 15) + "r\\"
        return top + "\n" + " " * (len(top) - 6) + "o;!?l<"
    top = _bef_str(s[::-1], q, 15) + "v"
    return top + "\n" + "o;!?l".rjust(len(top) - 1) + "<"


def _grid(t, w=0, h=0):
    lines = t.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    while len(lines) > 1 and not lines[-1].strip():
        lines.pop()
    W, H = max(w, max(len(x) for x in lines)), max(h, len(lines))
    g = [[ord(ch) for ch in x.ljust(W)] for x in lines] + [[32] * W for _ in range(H - len(lines))]
    return g, W, H


def _out_text(out):
    x = "".join(out)
    if x and max(map(ord, x)) < 256 and re.search(r"[\x80-\xff]", x):
        try:
            x = x.encode("latin-1").decode("utf-8")
        except UnicodeError:
            pass
    if not x.strip() or not any(ch.isalpha() for ch in x) or \
            any((ord(ch) < 32 and ch not in "\t\n\r") or 127 <= ord(ch) < 160 for ch in x):
        return None
    return x.rstrip("\n") if x.count("\n") == 1 and x.endswith("\n") else x


def befunge_run(t, w=80, h=25):
    """Run a Befunge-93/98 program on a max(w x h, text-bounds) torus -> its printed text, else None."""
    g, W, H = _grid(t, w, h)
    st, out, x, y, dx, dy, sm, k, last = [], [], 0, 0, 1, 0, False, 0, 0
    pop = lambda: st.pop() if st else 0  # noqa: E731
    while True:
        k += 1
        if k > _BEF_CAP or k - last > _BEF_IDLE or len(st) > 200000 or len(out) > 100000:
            return None
        c = g[y][x]
        if sm:
            if c == 34:
                sm = False
            else:
                st.append(c)
        elif 48 <= c <= 57:
            st.append(c - 48)
        elif 97 <= c <= 102:
            st.append(c - 87)
        else:
            ch = chr(c)
            if ch == '"':
                sm = True
            elif ch in "+-*/%`w":
                b, a = pop(), pop()
                if ch == "w":
                    if a < b:
                        dx, dy = dy, -dx
                    elif a > b:
                        dx, dy = -dy, dx
                else:
                    v = (a + b if ch == "+" else a - b if ch == "-" else a * b if ch == "*" else int(a > b) if ch == "`"
                         else 0 if not b else int(a / b) if ch == "/" else a - b * int(a / b))
                    if abs(v) > 1 << 64:
                        return None
                    st.append(v)
            elif ch == "!":
                st.append(int(not pop()))
            elif ch in "><^v?":
                dx, dy = {">": (1, 0), "?": (1, 0), "<": (-1, 0), "^": (0, -1), "v": (0, 1)}[ch]
            elif ch == "_":
                dx, dy = (-1 if pop() else 1), 0
            elif ch == "|":
                dx, dy = 0, (-1 if pop() else 1)
            elif ch == ":":
                v = pop()
                st += [v, v]
            elif ch == "\\":
                b, a = pop(), pop()
                st += [b, a]
            elif ch == "$":
                pop()
            elif ch == ".":
                out.append("%d " % pop())
                last = k
            elif ch == ",":
                v = pop()
                if not 0 <= v < 0x110000:
                    return None
                out.append(chr(v))
                last = k
            elif ch == "#":
                x, y = (x + dx) % W, (y + dy) % H
            elif ch in "gp":
                yy, xx = pop(), pop()
                ok = 0 <= xx < W and 0 <= yy < H
                if ch == "g":
                    st.append(g[yy][xx] if ok else 32)
                else:
                    v = pop()
                    if ok:
                        g[yy][xx] = v
            elif ch == "&":
                st.append(0)
            elif ch == "~":
                st.append(-1)
            elif ch in "@q":
                return _out_text(out)
            elif ch == ";":   # 98 comment: jump past the matching ;
                x, y = (x + dx) % W, (y + dy) % H
                n = 0
                while g[y][x] != 59 and n < W * H:
                    x, y, n = (x + dx) % W, (y + dy) % H, n + 1
            elif ch == "'":
                x, y = (x + dx) % W, (y + dy) % H
                st.append(g[y][x])
            elif ch == "s":
                x, y = (x + dx) % W, (y + dy) % H
                g[y][x] = pop()
            elif ch == "j":
                n = pop()
                x, y = (x + dx * n) % W, (y + dy * n) % H
            elif ch == "n":
                st.clear()
            elif ch == "r":
                dx, dy = -dx, -dy
            elif ch == "[":
                dx, dy = dy, -dx
            elif ch == "]":
                dx, dy = -dy, dx
        x, y = (x + dx) % W, (y + dy) % H


def fish_run(t):
    """Run a ><> program on its text-bounds torus -> its printed text, else None (an error = 'something smells
    fishy', an unknown instruction, the step cap, no text)."""
    g, W, H = _grid(t)
    st, out, x, y, dx, dy, sq, k, last, reg = [], [], 0, 0, 1, 0, 0, 0, 0, None
    mir = {"/": lambda a, b: (-b, -a), "\\": lambda a, b: (b, a), "|": lambda a, b: (-a, b),
           "_": lambda a, b: (a, -b), "#": lambda a, b: (-a, -b)}
    try:
        while True:
            k += 1
            if k > _BEF_CAP or k - last > _BEF_IDLE or len(st) > 200000 or len(out) > 100000:
                return None
            c = g[y][x]
            ch = chr(c)
            if sq:
                if c == sq:
                    sq = 0
                else:
                    st.append(c)
            elif ch in "0123456789abcdef":
                st.append(int(ch, 16))
            elif ch in "\"'":
                sq = c
            elif ch in "><^vx":
                dx, dy = {">": (1, 0), "x": (1, 0), "<": (-1, 0), "^": (0, -1), "v": (0, 1)}[ch]
            elif ch in mir:
                dx, dy = mir[ch](dx, dy)
            elif ch in "+-*,%=)(":
                b, a = st.pop(), st.pop()
                if ch in ",%" and not b:
                    return None
                v = (a + b if ch == "+" else a - b if ch == "-" else a * b if ch == "*" else int(a == b) if ch == "="
                     else int(a > b) if ch == ")" else int(a < b) if ch == "(" else a % b if ch == "%"
                     else a // b if isinstance(a, int) and isinstance(b, int) and a % b == 0 else a / b)
                if abs(v) > 1 << 64:
                    return None
                st.append(v)
            elif ch == "!":
                x, y = (x + dx) % W, (y + dy) % H
            elif ch == "?":
                if not st.pop():
                    x, y = (x + dx) % W, (y + dy) % H
            elif ch == ".":
                yy, xx = st.pop(), st.pop()
                if not (0 <= xx < W and 0 <= yy < H):
                    return None
                x, y = int(xx), int(yy)
            elif ch == ":":
                st.append(st[-1])
            elif ch == "~":
                st.pop()
            elif ch == "$":
                st[-1], st[-2] = st[-2], st[-1]
            elif ch == "@":
                st[-3:] = [st[-1], st[-3], st[-2]]
            elif ch == "}":
                st.insert(0, st.pop())
            elif ch == "{":
                st.append(st.pop(0))
            elif ch == "r":
                st.reverse()
            elif ch == "l":
                st.append(len(st))
            elif ch in "on":
                v = st.pop()
                if ch == "n":
                    out.append(str(int(v)) if v == int(v) else str(v))
                else:
                    if v != int(v) or not 0 <= v < 0x110000:
                        return None
                    out.append(chr(int(v)))
                last = k
            elif ch == "&":
                if reg is None:
                    reg = st.pop()
                else:
                    st.append(reg)
                    reg = None
            elif ch in "gp":
                yy, xx = st.pop(), st.pop()
                ok = 0 <= xx < W and 0 <= yy < H
                if ch == "g":
                    st.append(g[int(yy)][int(xx)] if ok else 0)
                else:
                    v = st.pop()
                    if not ok or v != int(v):
                        return None
                    g[int(yy)][int(xx)] = int(v)
            elif ch == "i":
                st.append(-1)
            elif ch == ";":
                return _out_text(out)
            elif ch != " " and c != 0:
                return None
            x, y = (x + dx) % W, (y + dy) % H
    except (IndexError, TypeError, ValueError, OverflowError, ZeroDivisionError):
        return None


def grid_text(t):
    """The text a Befunge-93/98 or ><> program prints, else None. Never raises."""
    try:
        if not isinstance(t, str) or not t.strip() or len(t) > 100000 or not any(ch in t for ch in "\"'0123456789"):
            return None
        reads = []
        if ("@" in t or "q" in t) and ("," in t or "." in t):
            reads += [lambda: befunge_run(t), lambda: befunge_run(t, 0, 0)]
        if ";" in t and ("o" in t or "n" in t):
            reads.append(lambda: fish_run(t))
        for rd in reads:
            x = rd()
            if x:
                return x
    except (ValueError, TypeError, IndexError, RecursionError, MemoryError, OverflowError):
        pass
    return None


def befunge_dec(t):
    """Undo a Befunge-93/98 / ><> program -> the printed text; raises when t is not one."""
    x = grid_text(t)
    if x is None:
        raise ValueError("not a Befunge / ><> program")
    return x


def befunge_free(p):
    """Mastery free line: a one-row Befunge / ><> program's printed text when it is a crib / slug piece or prose."""
    x = grid_text(p)
    return [x] if x and (_crib_piece(x) or SLUG.search(x) or _texty(x) >= 0.9) else []


CANDIDATES += [("befunge-line", befunge_enc, befunge_dec),
               ("befunge-grid", lambda s: befunge_enc(s, "grid"), befunge_dec),
               ("fish-mirror", fish_enc, befunge_dec),
               ("fish-line", lambda s: fish_enc(s, "line"), befunge_dec)]
SPECULATIVE_FREE += (("befunge", befunge_free),)


# ------------------------------------------- JSFuck ([]()! + only): a pure-python evaluator, NEVER node / eval
# The six-symbol program is evaluated over a small JS value model (arrays, booleans, numbers with JS Number::toString,
# strings, undefined, native functions with "function NAME() { [native code] }" source text, iterator / RegExp / Date
# objects) with the ~40 primitives jsfuck.com 0.4 / 0.5 build on: [] / ![] / +[] / []+[], indexing, ["flat"/"at"/
# "filter"/"entries"/"concat"/"fontcolor"/"italics"/"split"/"join"/...], (n)["toString"](radix), String.fromCharCode,
# and Function(body) whose body is one of the encoder's fixed forms (return escape / unescape / Date / this / eval /
# /re/ / new Date(n) / "string literal"). Any other body is the wrapped PROGRAM (eval mode): never run, its string
# literal(s) are the answer (alert("...") / console.log('...') / document.write(...)), else the program text.
_JSF_CH = frozenset("[]()!+")


class _JsUndef:
    __slots__ = ()


_JU = _JsUndef()


class _JsFn:
    __slots__ = ("name", "impl", "props")

    def __init__(self, name, impl=None, props=None):
        self.name, self.impl, self.props = name, impl, props or {}


class _JsObj:
    __slots__ = ("text", "kind", "props")

    def __init__(self, text, kind="object", props=None):
        self.text, self.kind, self.props = text, kind, props or {}


class _JsProg(_JsObj):
    """The body handed to Function(...)() / eval(...) that is not one of the encoder's fixed primitives."""


def _jsn(x):
    """ECMAScript Number::toString(10)."""
    if x != x:
        return "NaN"
    if x in (math.inf, -math.inf):
        return "Infinity" if x > 0 else "-Infinity"
    if x == 0:
        return "0"
    if x < 0:
        return "-" + _jsn(-x)
    m = re.fullmatch(r"(\d+)(?:\.(\d+))?(?:e([+-]?\d+))?", repr(float(x)))
    i, f, e = m.group(1), m.group(2) or "", int(m.group(3) or 0)
    s = i + f
    lz = len(s) - len(s.lstrip("0"))
    s = s.lstrip("0").rstrip("0")
    n, k = len(i) + e - lz, len(s)
    if k <= n <= 21:
        return s + "0" * (n - k)
    if 0 < n <= 21:
        return s[:n] + "." + s[n:]
    if -6 < n <= 0:
        return "0." + "0" * -n + s
    e = n - 1
    return s[0] + ("." + s[1:] if k > 1 else "") + "e" + ("+" if e >= 0 else "-") + str(abs(e))


def _jss(v):
    """ToString."""
    if isinstance(v, str):
        return v
    if v is True or v is False:
        return "true" if v else "false"
    if v is _JU:
        return "undefined"
    if v is None:
        return "null"
    if isinstance(v, float):
        return _jsn(v)
    if isinstance(v, list):
        return ",".join("" if e is _JU or e is None else _jss(e) for e in v)
    if isinstance(v, _JsFn):
        return f"function {v.name}() {{ [native code] }}"
    return v.text


def _jsnum(v):
    """ToNumber."""
    if v is True or v is False:
        return 1.0 if v else 0.0
    if isinstance(v, float):
        return v
    if v is _JU:
        return math.nan
    if v is None:
        return 0.0
    s = _jss(v).strip(" \t\n\r\v\f\u00a0\ufeff")
    if not s:
        return 0.0
    if re.fullmatch(r"[+-]?Infinity", s):
        return -math.inf if s[0] == "-" else math.inf
    m = re.fullmatch(r"0([xob])([0-9a-f]+)", s, re.I)
    if m:
        try:
            return float(int(m.group(2), {"x": 16, "o": 8, "b": 2}[m.group(1).lower()]))
        except ValueError:
            return math.nan
    if re.fullmatch(r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?", s):
        return float(s)
    return math.nan


def _jstruth(v):
    if isinstance(v, str):
        return bool(v)
    if isinstance(v, bool):
        return v
    if isinstance(v, float):
        return not (v == 0 or v != v)
    return not (v is _JU or v is None)


def _jsadd(a, b):
    pa = _jss(a) if isinstance(a, (list, _JsFn, _JsObj)) else a
    pb = _jss(b) if isinstance(b, (list, _JsFn, _JsObj)) else b
    if isinstance(pa, str) or isinstance(pb, str):
        return _jss(pa) + _jss(pb)
    return _jsnum(pa) + _jsnum(pb)


def _jsint(v, dflt=0):
    if v is _JU:
        return dflt
    x = _jsnum(v)
    return 0 if x != x else (int(x) if abs(x) < 1e15 else (10 ** 15 if x > 0 else -10 ** 15))


def _jsarg(a, k):
    return a[k] if len(a) > k else _JU


def _js_at(this, a):
    s = this if isinstance(this, list) else _jss(this)
    k = _jsint(_jsarg(a, 0))
    k = k + len(s) if k < 0 else k
    return s[k] if 0 <= k < len(s) else _JU


def _js_slice(this, a):
    s = this if isinstance(this, list) else _jss(this)
    n = len(s)
    b, e = _jsint(_jsarg(a, 0)), _jsint(_jsarg(a, 1), n)
    b, e = (max(n + b, 0) if b < 0 else min(b, n)), (max(n + e, 0) if e < 0 else min(e, n))
    return s[b:e] if isinstance(s, str) else list(s[b:e])


def _js_concat(this, a):
    if isinstance(this, list):
        out = list(this)
        for x in a:
            out.extend(x) if isinstance(x, list) else out.append(x)
        return out
    return _jss(this) + "".join(_jss(x) for x in a)


def _js_tostring(this, a):
    if isinstance(this, float) and a and a[0] is not _JU:
        r = _jsint(a[0])
        if not 2 <= r <= 36:
            raise ValueError("radix")
        if this != this or this in (math.inf, -math.inf) or this != int(this):
            if this == this and this not in (math.inf, -math.inf):
                raise ValueError("fractional radix toString unsupported")
            return _jsn(this)
        n, neg, out = abs(int(this)), this < 0, ""
        while True:
            n, d = divmod(n, r)
            out = "0123456789abcdefghijklmnopqrstuvwxyz"[d] + out
            if not n:
                break
        return "-" + out if neg else out
    return _jss(this)


def _js_split(this, a):
    s, sep = _jss(this), _jsarg(a, 0)
    if sep is _JU:
        return [s]
    sep = _jss(sep)
    return list(s) if sep == "" else s.split(sep)


def _js_join(this, a):
    sep = "," if _jsarg(a, 0) is _JU else _jss(a[0])
    return sep.join("" if e is _JU or e is None else _jss(e) for e in this)


def _js_html(tag, attr=None):
    def f(this, a):
        at = "" if attr is None else f' {attr}="' + _jss(_jsarg(a, 0)).replace('"', "&quot;") + '"'
        return f"<{tag}{at}>{_jss(this)}</{tag}>"
    return f


def _js_escape(this, a):
    out = []
    for c in _jss(_jsarg(a, 0)):
        o = ord(c)
        out.append(c if c.isascii() and (c.isalnum() or c in "@*_+-./") else "%%%02X" % o if o < 256 else "%%u%04X" % o)
    return "".join(out)


def _js_unescape(this, a):
    return re.sub(r"%u([0-9a-fA-F]{4})|%([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1) or m.group(2), 16)),
                  _jss(_jsarg(a, 0)))


def _js_date_text(ms):
    t = time.gmtime(ms / 1000.0)
    return time.strftime("%a %b %d %Y %H:%M:%S", t) + " GMT+0000 (Coordinated Universal Time)"


def _js_regexp_obj(src, flags=""):
    return _JsObj("/" + (src or "(?:)") + "/" + flags, "regexp", {"source": src or "(?:)"})


def _js_regexp(this, a):
    src = "" if _jsarg(a, 0) is _JU else _jss(a[0])
    return _js_regexp_obj(re.sub(r"(?<!\\)/", r"\\/", src), "" if _jsarg(a, 1) is _JU else _jss(a[1]))


def _js_function(this, a):
    body = _jss(a[-1]) if a else ""
    return _JsFn("anonymous", lambda t, x: _jsf_body(body))


_JSF_STR_METHODS = {
    "at": _js_at, "charAt": lambda t, a: (_js_at(t, a) if _jsint(_jsarg(a, 0)) >= 0 else _JU) or "",
    "concat": _js_concat, "slice": _js_slice, "split": _js_split, "toString": _js_tostring, "valueOf": lambda t, a: t,
    "substr": lambda t, a: _jss(t)[_jsint(_jsarg(a, 0)):][:_jsint(_jsarg(a, 1), 1 << 30)],
    "toUpperCase": lambda t, a: _jss(t).upper(), "toLowerCase": lambda t, a: _jss(t).lower(),
    "trim": lambda t, a: _jss(t).strip(), "repeat": lambda t, a: _jss(t) * max(0, min(_jsint(_jsarg(a, 0)), 4096)),
    "indexOf": lambda t, a: float(_jss(t).find(_jss(_jsarg(a, 0)))),
    "fontcolor": _js_html("font", "color"), "fontsize": _js_html("font", "size"), "link": _js_html("a", "href"),
    "anchor": _js_html("a", "name"), "italics": _js_html("i"), "bold": _js_html("b"), "big": _js_html("big"),
    "small": _js_html("small"), "sub": _js_html("sub"), "sup": _js_html("sup"), "strike": _js_html("strike"),
    "fixed": _js_html("tt"), "blink": _js_html("blink"),
}
_JSF_ARR_METHODS = {
    "at": _js_at, "concat": _js_concat, "slice": _js_slice, "join": _js_join, "toString": _js_join,
    "entries": lambda t, a: _JsObj("[object Array Iterator]", "iterator"),
    "keys": lambda t, a: _JsObj("[object Array Iterator]", "iterator"),
    "values": lambda t, a: _JsObj("[object Array Iterator]", "iterator"),
    "reverse": lambda t, a: t.reverse() or t, "indexOf": lambda t, a: float(t.index(a[0]) if a and a[0] in t else -1),
}
_JSF_ARR_NAMES = set(_JSF_ARR_METHODS) | set("flat flatMap filter fill find findIndex findLast findLastIndex map some "
                                             "every reduce reduceRight forEach includes push pop shift unshift splice "
                                             "sort copyWithin lastIndexOf toLocaleString".split())
_JSF_NUM_METHODS = {"toString": _js_tostring, "valueOf": lambda t, a: t,
                    "toFixed": lambda t, a: "%.*f" % (max(0, min(_jsint(_jsarg(a, 0)), 100)), t)}


def _jsf_ctor(name, impl, **props):
    return _JsFn(name, impl, props)


_JSF_STRING = _jsf_ctor("String", lambda t, a: _jss(a[0]) if a else "",
                        fromCharCode=_JsFn("fromCharCode", lambda t, a: "".join(chr(_jsint(x) & 0xFFFF) for x in a)),
                        fromCodePoint=_JsFn("fromCodePoint", lambda t, a: "".join(chr(_jsint(x)) for x in a)))
_JSF_NUMBER = _jsf_ctor("Number", lambda t, a: _jsnum(a[0]) if a else 0.0)
_JSF_BOOLEAN = _jsf_ctor("Boolean", lambda t, a: _jstruth(a[0]) if a else False)
_JSF_ARRAY = _jsf_ctor("Array", lambda t, a: list(a) if len(a) != 1 or not isinstance(a[0], float) else
                       [_JU] * max(0, min(_jsint(a[0]), 4096)))
_JSF_FUNCTION = _jsf_ctor("Function", _js_function)
_JSF_REGEXP = _jsf_ctor("RegExp", _js_regexp)
_JSF_OBJECT = _jsf_ctor("Object", lambda t, a: _JsObj("[object Object]"))
_JSF_DATE = _jsf_ctor("Date", lambda t, a: _js_date_text(0))
_JSF_GLOBALS = {
    "escape": _JsFn("escape", _js_escape), "unescape": _JsFn("unescape", _js_unescape), "Date": _JSF_DATE,
    "String": _JSF_STRING, "Number": _JSF_NUMBER, "Boolean": _JSF_BOOLEAN, "Array": _JSF_ARRAY, "Object": _JSF_OBJECT,
    "Function": _JSF_FUNCTION, "RegExp": _JSF_REGEXP, "this": _JsObj("[object global]", "global"),
    "eval": _JsFn("eval", lambda t, a: _JsProg(_jss(a[0])) if a and isinstance(a[0], str) else _jsarg(a, 0)),
    "atob": _JsFn("atob", lambda t, a: base64.b64decode(_jss(_jsarg(a, 0))).decode("latin-1")),
    "btoa": _JsFn("btoa", lambda t, a: base64.b64encode(_jss(_jsarg(a, 0)).encode("latin-1")).decode()),
    "encodeURI": _JsFn("encodeURI", lambda t, a: urllib.parse.quote(_jss(_jsarg(a, 0)), safe=";,/?:@&=+$-_.!~*'()#")),
    "decodeURI": _JsFn("decodeURI", lambda t, a: urllib.parse.unquote(_jss(_jsarg(a, 0)))),
    "{}": _JsObj("[object Object]"),
}
_JSF_ESC = re.compile(r"""\\(?:u\{([0-9a-fA-F]{1,6})\}|u([0-9a-fA-F]{4})|x([0-9a-fA-F]{2})|([0-3][0-7]{0,2}|[4-7][0-7]?)|"""
                      r"""(\r\n|[\s\S]))""")
_JSF_SIMPLE_ESC = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "\n": "", "\r\n": "", "\r": "",
                   "\u2028": "", "\u2029": ""}
_JSF_LIT = re.compile(r""""(?:[^"\\\n]|\\[\s\S])*"|'(?:[^'\\\n]|\\[\s\S])*'|`(?:[^`\\$]|\\[\s\S]|\$(?!\{))*`""")


def _js_unlit(q):
    """The value of one JS string literal (quotes included): \\n / \\xHH / \\uHHHH / \\u{H} / legacy octal escapes."""
    def r(m):
        if m.group(1) or m.group(2) or m.group(3):
            return chr(int(m.group(1) or m.group(2) or m.group(3), 16))
        if m.group(4):
            return chr(int(m.group(4), 8))
        return _JSF_SIMPLE_ESC.get(m.group(5), m.group(5))
    return _JSF_ESC.sub(r, q[1:-1])


def _jsf_body(body):
    """Function(body)(): the encoder's fixed `return X` forms evaluated, any other body = the wrapped program."""
    m = re.fullmatch(r"\s*return(?:\s+|(?=[/\"'{(`\[]))(.*?)[\s;]*", body, re.S)
    if m:
        r = m.group(1)
        if r in _JSF_GLOBALS:
            return _JSF_GLOBALS[r]
        mm = re.fullmatch(r"/((?:[^/\\\n]|\\.)*)/([dgimsuy]*)", r)
        if mm:
            return _js_regexp_obj(mm.group(1), mm.group(2))
        mm = re.fullmatch(r"new\s+Date\(\s*(-?\d+)\s*\)", r)
        if mm:
            return _JsObj(_js_date_text(int(mm.group(1))), "date")
        if _JSF_LIT.fullmatch(r):
            return _js_unlit(r)
    return _JsProg(body, "program")


def _jsf_get(o, k):
    k = _jss(k)
    if o is _JU or o is None:
        raise TypeError("property of undefined")
    if isinstance(o, (str, list)):
        if k.isdigit() and (k == "0" or k[0] != "0"):
            i = int(k)
            return o[i] if i < len(o) else _JU
        if k == "length":
            return float(len(o))
        if k == "constructor":
            return _JSF_STRING if isinstance(o, str) else _JSF_ARRAY
        if isinstance(o, str):
            return _JsFn(k, _JSF_STR_METHODS[k]) if k in _JSF_STR_METHODS else _JU
        if k in _JSF_ARR_NAMES:
            return _JsFn(k, _JSF_ARR_METHODS.get(k))
        return _JU
    if isinstance(o, bool):
        return _JSF_BOOLEAN if k == "constructor" else _JsFn(k, _js_tostring) if k in ("toString", "valueOf") else _JU
    if isinstance(o, float):
        return _JSF_NUMBER if k == "constructor" else _JsFn(k, _JSF_NUM_METHODS[k]) if k in _JSF_NUM_METHODS else _JU
    if isinstance(o, _JsFn):
        if k == "constructor":
            return _JSF_FUNCTION
        if k == "name":
            return o.name
        if k == "toString":
            return _JsFn(k, _js_tostring)
        if k == "call":
            return _JsFn("call", lambda t, a: _jsf_call(t, _jsarg(a, 0), list(a[1:])))
        return o.props.get(k, _JU)
    if k == "constructor":
        return {"regexp": _JSF_REGEXP, "date": _JSF_DATE}.get(o.kind, _JSF_OBJECT)
    if k == "toString":
        return _JsFn(k, _js_tostring)
    return o.props.get(k, _JU)


def _jsf_call(f, this, args):
    if not isinstance(f, _JsFn) or f.impl is None:
        raise TypeError("not callable: " + (f.name if isinstance(f, _JsFn) else type(f).__name__))
    return f.impl(this, args)


class _JsfParser:
    """Recursive descent over [ ] ( ) ! + evaluating as it goes: expr = unary ('+' unary)*; unary = ('!'|'+') unary |
    postfix; postfix = primary ('[' expr ']' | '(' [expr] ')')*; primary = '[' [expr] ']' | '(' expr ')'."""

    def __init__(self, s, max_steps=2_000_000):
        self.s, self.i, self.n, self.steps = s, 0, len(s), max_steps

    def peek(self):
        return self.s[self.i] if self.i < self.n else ""

    def eat(self, c):
        if self.peek() != c:
            raise ValueError(f"expected {c!r} at {self.i}")
        self.i += 1

    def expr(self):
        v = self.unary()
        while self.peek() == "+":
            self.i += 1
            v = _jsadd(v, self.unary())
        return v

    def unary(self):
        ops = []
        while self.peek() in ("!", "+") and self.peek():
            ops.append(self.s[self.i])
            self.i += 1
        v = self.postfix()
        for op in reversed(ops):
            v = (not _jstruth(v)) if op == "!" else _jsnum(v)
        return v

    def postfix(self):
        c = self.peek()
        if c == "[":
            self.i += 1
            if self.peek() == "]":
                v = []
            else:
                v = [self.expr()]
            self.eat("]")
        elif c == "(":
            self.i += 1
            v = self.expr()
            self.eat(")")
        else:
            raise ValueError(f"unexpected {c!r} at {self.i}")
        this = _JU
        while True:
            self.steps -= 1
            if self.steps < 0:
                raise ValueError("step cap")
            c = self.peek()
            if c == "[":
                self.i += 1
                k = self.expr()
                self.eat("]")
                v, this = _jsf_get(v, k), v
            elif c == "(":
                self.i += 1
                args = [] if self.peek() == ")" else [self.expr()]
                self.eat(")")
                v, this = _jsf_call(v, this, args), _JU
            else:
                return v


def jsfuck_eval(t):
    """Evaluate a JSFuck program -> its final JS value (str / float / list / _JsProg ...); raises when t is not one."""
    if not isinstance(t, str):
        raise ValueError("not text")
    s = "".join(t.split()).rstrip(";")
    if len(s) < 8 or len(s) > 4_000_000 or not set(s) <= _JSF_CH or "[" not in s or "!" not in s:
        raise ValueError("not JSFuck")
    p = _JsfParser(s)
    v = p.expr()
    if p.i != p.n:
        raise ValueError(f"trailing input at {p.i}")
    return v


def _jsf_prog_text(prog):
    """A wrapped program's answer: its string literal run(s) ("a"+'b' joined) -- the longest -- else the program."""
    best = None
    for m in re.finditer(r"(?:%s)(?:\s*\+\s*(?:%s))*" % (_JSF_LIT.pattern, _JSF_LIT.pattern), prog):
        x = "".join(_js_unlit(q.group(0)) for q in _JSF_LIT.finditer(m.group(0)))
        if best is None or len(x) > len(best):
            best = x
    return best if best is not None else prog.strip()


def jsfuck_dec(t):
    """The text a JSFuck program yields (the string it evaluates to, or the string literal inside the program it
    evals / Function()s), else None. Pure python: the program is never run by a JS engine."""
    try:
        v = jsfuck_eval(t)
        if isinstance(v, _JsProg):
            v = _jsf_prog_text(v.text)
        elif isinstance(v, _JsFn) and v.name == "anonymous":
            return None
        return v if isinstance(v, str) and v else None
    except (ValueError, TypeError, KeyError, IndexError, OverflowError, RecursionError, MemoryError,
            UnicodeError, binascii.Error):
        return None


def jsfuck_free(p):
    """Mastery free line: a JSFuck line's yielded text."""
    x = jsfuck_dec(p)
    return [x] if x else []


# jsfuck.com 0.5.0's encoder ported (MAPPING / replaceMap / replaceStrings / encode), so infer() matches its bytes
_JSF5_SIMPLE = {"false": "![]", "true": "!![]", "undefined": "[][[]]", "NaN": "+[![]]",
                "Infinity": "+(+!+[]+(!+[]+[])[!+[]+!+[]+!+[]]+[+!+[]]+[+[]]+[+[]]+[+[]])"}
_JSF5_CTORS = {"Array": "[]", "Number": "(+[])", "String": "([]+[])", "Boolean": "(![])", "Function": '[]["at"]',
               "RegExp": 'Function("return/"+false+"/")()'}
_JSF5_RAW = (
    ("a", '(false+"")[1]'), ("b", '([]["entries"]()+"")[2]'), ("c", '([]["at"]+"")[3]'), ("d", '(undefined+"")[2]'),
    ("e", '(true+"")[3]'), ("f", '(false+"")[0]'), ("g", '(false+[0]+String)[20]'),
    ("h", '(+(101))["to"+String["name"]](21)[1]'), ("i", '([false]+undefined)[10]'), ("j", '([]["entries"]()+"")[3]'),
    ("k", '(+(20))["to"+String["name"]](21)'), ("l", '(false+"")[2]'), ("m", '(Number+"")[11]'),
    ("n", '(undefined+"")[1]'), ("o", '(true+[]["at"])[10]'), ("p", '(+(211))["to"+String["name"]](31)[1]'),
    ("q", '("")["fontcolor"]([0]+false+")[20]'), ("r", '(true+"")[1]'), ("s", '(false+"")[3]'), ("t", '(true+"")[0]'),
    ("u", '(undefined+"")[0]'), ("v", '(+(31))["to"+String["name"]](32)'), ("w", '(+(32))["to"+String["name"]](33)'),
    ("x", '(+(101))["to"+String["name"]](34)[1]'), ("y", '(NaN+[Infinity])[10]'),
    ("z", '(+(35))["to"+String["name"]](36)'),
    ("A", '(NaN+[]["entries"]())[11]'), ("B", '(+[]+Boolean)[10]'), ("C", 'Function("return escape")()(("")["italics"]())[2]'),
    ("D", 'Function("return escape")()([]["at"])["at"]("-1")'), ("E", '(RegExp+"")[12]'), ("F", '(+[]+Function)[10]'),
    ("G", '(false+Function("return Date")()())[30]'), ("H", None), ("I", '(Infinity+"")[0]'), ("J", None), ("K", None),
    ("L", None), ("M", '(true+Function("return Date")()())[30]'), ("N", '(NaN+"")[0]'), ("O", None), ("P", None),
    ("Q", None), ("R", '(+[]+RegExp)[10]'), ("S", '(+[]+String)[10]'), ("T", '(NaN+Function("return Date")()())[30]'),
    ("U", None), ("V", None), ("W", None), ("X", None), ("Y", None), ("Z", None),
    (" ", '(NaN+[]["at"])[11]'), ("!", None), ('"', '("")["fontcolor"]()[12]'), ("#", None), ("$", None),
    ("%", 'Function("return escape")()([]["at"])[22]'), ("&", '("")["fontcolor"](")[13]'), ("'", None),
    ("(", '([]["at"]+"")[11]'), (")", '(""+[]["at"])[12]'), ("*", None),
    ("+", '(+(+!+[]+(!+[]+[])[!+[]+!+[]+!+[]]+[+!+[]]+[+[]]+[+[]])+[])[2]'), (",", '[[]]["concat"]([[]])+""'),
    ("-", '(+(.+[0000001])+"")[2]'), (".", '(+(+!+[]+[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+[!+[]+!+[]]+[+[]])+[])[+!+[]]'),
    ("/", '(false+[0])["italics"]()[10]'), (":", '(RegExp()+"")[3]'), (";", '("")["fontcolor"](NaN+")[21]'),
    ("<", '("")["italics"]()[0]'), ("=", '("")["fontcolor"]()[11]'), (">", '("")["italics"]()[2]'),
    ("?", '(RegExp()+"")[2]'), ("@", None), ("[", '([]["entries"]()+"")[0]'), ("\\", '(RegExp("/")+"")[1]'),
    ("]", '([]["entries"]()+"")[22]'), ("^", None), ("_", None), ("`", None), ("{", '([0]+false+[]["at"])[20]'),
    ("|", None), ("}", '([]["at"]+"")["at"]("-1")'), ("~", None))


def _jsf5_num(y, M):
    head, out = int(y[0]), "+[]"
    if head > 0:
        out = "+!" + out
    for _ in range(1, head):
        out = "+!+[]" + out
    if head > 1:
        out = out[1:]
    return re.sub(r"(\d)", lambda m: M[m.group(1)], "+".join([out] + list(y[1:])))


@functools.lru_cache(maxsize=1)
def _jsf5_mapping():
    M = {}
    for d in range(10):
        M[str(d)] = "[" + _jsf5_num(str(d), {}) + "]"
    M.update(_JSF5_RAW)
    st = [32]   # the JS numberReplacer reuses replaceMap's loop counter `i`: chars re-run (emulated, else bytes differ)

    def num(m):
        st[0] = max(1, int(m.group(1)[0]))
        return _jsf5_num(m.group(1), M)
    for _ in range(20000):
        i = st[0]
        if i > 126:
            break
        v = M.get(chr(i))
        if not v:
            st[0] += 1
            continue
        for key, ctor in _JSF5_CTORS.items():
            v = re.sub(r"\b" + key, lambda m, c=ctor: c + '["constructor"]', v, flags=re.I)
        for key, simple in _JSF5_SIMPLE.items():
            v = re.sub(key, lambda m, s=simple: s, v, flags=re.I)
        v = re.sub(r"(\d\d+)", num, v)
        v = re.sub(r"\((\d)\)", lambda m: M[m.group(1)], v)
        v = re.sub(r"\[(\d)\]", lambda m: M[m.group(1)], v)
        v = re.sub("GLOBAL", 'Function("return this")()', v, flags=re.I)
        v = re.sub(r'\+""', "+[]", v)
        v = re.sub('""', "[]+[]", v)
        M[chr(i)] = v
        st[0] += 1   # the JS loop's own i++ (after numberReplacer may have reset it)
    for k, v in M.items():
        if v:
            M[k] = re.sub(r'"([^"]+)"', lambda m: "+".join(m.group(1)), v)
    other = re.compile(r"[^\[\]\(\)\!\+]")
    for _ in range(127 - 32 + 1):
        missing = {k: v for k, v in M.items() if v and other.search(v)}
        if not missing:
            break
        for k in missing:
            v = other.sub(lambda m: m.group(0) if missing.get(m.group(0)) else (M.get(m.group(0)) or "null"), M[k])
            M[k] = missing[k] = v
    return M


def _jsf5_esc(c):
    o = ord(c)
    return "\\" + format(o, "o") if o < 256 else "\\u%04x" % o


def jsfuck_enc(s, wrap=False, parent=False):
    """jsfuck.com 0.5.0 JSFuck.encode(s, wrapWithEval, runInParentScope)."""
    M = _jsf5_mapping()
    if not s:
        return ""
    unm = re.compile("[^" + re.escape("".join(k for k, v in M.items() if v)) + "]")
    n = len(unm.findall(s))
    if n > 1:
        s = re.sub(r"[^0123456789.adefilnrsuN]", lambda m: _jsf5_esc(m.group(0)).replace("\\", "t", 1), s)
    elif n:
        s = unm.sub(lambda m: _jsf5_esc(m.group(0)), re.sub(r'["\\]', lambda m: _jsf5_esc(m.group(0)), s))
    out = []
    for m in re.finditer(r"false|true|undefined|NaN|Infinity|.", s):
        c = m.group(0)
        out.append("(" + _JSF5_SIMPLE[c] + "+[])" if c in _JSF5_SIMPLE else M[c])
    out = "+".join(out) + ("+[]" if re.fullmatch(r"\d", s) else "")
    if n > 1:
        out = f"({out})[{jsfuck_enc('split')}]({jsfuck_enc('t')})[{jsfuck_enc('join')}]({jsfuck_enc(chr(92))})"
    if n:
        out = f'[][{jsfuck_enc("at")}][{jsfuck_enc("constructor")}]({jsfuck_enc(chr(34).join(["return", ""]))}+{out}+{jsfuck_enc(chr(34))})()'
    if wrap:
        head = f"[][{jsfuck_enc('at')}][{jsfuck_enc('constructor')}]"
        out = f"{head}({jsfuck_enc('return eval')})()({out})" if parent else f"{head}({out})()"
    return out


CANDIDATES += [("jsfuck", jsfuck_enc, jsfuck_dec),
               ("jsfuck-eval-alert", lambda s: jsfuck_enc('alert("%s")' % s.replace("\\", "\\\\").replace('"', '\\"'), True),
                jsfuck_dec)]
SPECULATIVE_FREE += (("jsfuck", jsfuck_free),)


# ------------------------------------------------------- Chef (recipe-shaped) and Shakespeare (play-shaped) esolangs
# "Food for Thought" / "All the world's a stage": the sentence is the OUTPUT of a Chef recipe ('Ingredients.' = char
# codes, 'Method.' = a stack machine over mixing bowls, 'Serves N.' prints the first N baking dishes top first, i.e.
# REVERSED push order -- the classic 'Hello World Souffle' pushes the sentence back to front) or of a Shakespeare play
# (noun phrase = +-2^#adjectives, 'You are as <adj> as <expr>!' assigns the listener, 'Speak your mind!' prints chr).
_CHEF_MEAS = r"(?:heaped\s+|level\s+)?(g|kg|pinch(?:es)?|ml|l|dash(?:es)?|cups?|teaspoons?|tablespoons?)\s+"
_CHEF_ING = re.compile(r"^\s*(-?\d+)?\s*(?:" + _CHEF_MEAS + r")?(\S.*?)\s*$", re.I)
_CHEF_BOWL = r"(?:the\s+)?(?:(\d+)(?:st|nd|rd|th)\s+)?mixing\s+bowl"
_CHEF_DISH = r"(?:the\s+)?(?:(\d+)(?:st|nd|rd|th)\s+)?baking\s+dish"
_CHEF_OPS = [(k, re.compile(p + r"$", re.I)) for k, p in (
    ("take", r"Take\s+(.+?)\s+from\s+(?:the\s+)?refrigerator"),
    ("put", r"Put\s+(.+?)\s+into\s+" + _CHEF_BOWL),
    ("fold", r"Fold\s+(.+?)\s+into\s+" + _CHEF_BOWL),
    ("dry", r"Add\s+dry\s+ingredients(?:\s+to\s+" + _CHEF_BOWL + r")?"),
    ("arith", r"(Add|Remove|Combine|Divide)\s+(.+?)(?:\s+(?:to|into|from)\s+" + _CHEF_BOWL + r")?"),
    ("liqbowl", r"Liqu[ei]fy\s+(?:the\s+)?contents\s+of\s+" + _CHEF_BOWL),
    ("liq", r"Liqu[ei]fy\s+(?:the\s+)?(.+?)"),
    ("stirn", r"Stir(?:\s+" + _CHEF_BOWL + r")?\s+for\s+(\d+)\s+minutes?"),
    ("stiri", r"Stir\s+(.+?)\s+into\s+" + _CHEF_BOWL),
    ("mix", r"Mix(?:\s+" + _CHEF_BOWL + r")?\s+well"),
    ("clean", r"Clean\s+" + _CHEF_BOWL),
    ("pour", r"Pour\s+contents\s+of\s+" + _CHEF_BOWL + r"\s+into\s+" + _CHEF_DISH),
    ("aside", r"Set\s+aside"),
    ("serve", r"Serve\s+with\s+(.+?)"),
    ("fridge", r"Refrigerate(?:\s+for\s+(\d+)\s+hours?)?"),
    ("until", r"([A-Za-z]+)(?:\s+(?:the\s+)?(.+?))?\s+until\s+[A-Za-z]+"),
    ("loop", r"([A-Za-z]+)\s+(?:the\s+)?(.+?)"))]


def _chef_recipes(t):
    """({title_lower: (ingredients [(name, value|None, liquid)], method_text, serves|None)}, main title), else None.
    A recipe = title line [+ comment paragraph] + 'Ingredients.' + [Cooking time / Pre-heat] + 'Method.' + [Serves]."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", t.replace("\r\n", "\n").replace("\r", "\n").strip()) if p.strip()]
    ing_at = [i for i, p in enumerate(paras) if re.match(r"Ingredients\s*\.", p, re.I)]
    if not ing_at or not any(re.match(r"Method\s*\.", p, re.I) for p in paras):
        return None
    kw = re.compile(r"(Method|Serves|Cooking|Pre-heat|Ingredients)\b", re.I)
    heads = []   # (title paragraph index, ingredients paragraph index)
    for n, i in enumerate(ing_at):
        lo = ing_at[n - 1] + 2 if n else 0
        cand = [j for j in (i - 1, i - 2) if j >= lo and "\n" not in paras[j] and not kw.match(paras[j])]
        j = cand[-1] if len(cand) == 2 and n else cand[0] if cand else (i if n == 0 else None)
        if j is None:
            return None
        heads.append((j, i))
    recipes = {}
    for n, (j, i) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(paras)
        title = "" if j == i else paras[j].rstrip(".").strip().lower()
        ings, method, serves = [], [], None
        for b in paras[i:end]:
            if re.match(r"Ingredients\s*\.", b, re.I):
                for ln in b.split("\n")[1:]:
                    m = _CHEF_ING.match(ln)
                    if not m or not ln.strip():
                        continue
                    meas = (m.group(2) or "").lower()
                    ings.append((re.sub(r"\s+", " ", m.group(3)).lower(), None if m.group(1) is None else int(m.group(1)),
                                 meas in ("ml", "l", "dash", "dashes")))
            elif re.match(r"Method\s*\.", b, re.I):
                method.append(re.sub(r"^Method\s*\.", "", b, flags=re.I))
            elif re.match(r"Serves\s+\d+", b, re.I):
                serves = int(re.match(r"Serves\s+(\d+)", b, re.I).group(1))
            elif method and not re.match(r"(Cooking|Pre-heat)\b", b, re.I):
                method.append(b)
        if not ings or not method:
            return None
        recipes[title] = (ings, " ".join(method), serves)
    return recipes, (paras[heads[0][0]].rstrip(".").strip().lower() if heads[0][0] != heads[0][1] else "")


def _chef_compile(method, names):
    """Method text -> [(op, args...)] with loop ends linked; raises ValueError on an unknown step."""
    prog, opened = [], []

    def ing(x):
        x = re.sub(r"^the\s+", "", re.sub(r"\s+", " ", x.strip()), flags=re.I).lower()
        if x not in names:
            raise ValueError("unknown ingredient " + x)
        return x
    bn = lambda g: int(g) - 1 if g else 0  # noqa: E731
    for st in re.split(r"\.(?:\s+|$)", re.sub(r"\s+", " ", method).strip()):
        st = st.strip().rstrip(".")
        if not st:
            continue
        for k, rx in _CHEF_OPS:
            m = rx.match(st)
            if not m:
                continue
            g = m.groups()
            if k in ("take", "liq", "loop"):
                if k == "loop":
                    prog.append(("loop", ing(g[1]), None))
                    opened.append(len(prog) - 1)
                else:
                    prog.append((k, ing(g[0])))
            elif k in ("put", "fold", "stiri"):
                prog.append((k, ing(g[0]), bn(g[1])))
            elif k in ("dry", "liqbowl", "mix", "clean"):
                prog.append((k, bn(g[0])))
            elif k == "arith":
                prog.append((g[0].lower(), ing(g[1]), bn(g[2])))
            elif k == "stirn":
                prog.append((k, bn(g[0]), int(g[1])))
            elif k == "pour":
                prog.append((k, bn(g[0]), bn(g[1])))
            elif k == "aside":
                prog.append((k,))
            elif k == "serve":
                prog.append((k, g[0].strip().lower()))
            elif k == "fridge":
                prog.append((k, int(g[0]) if g[0] else None))
            elif k == "until":
                if not opened:
                    raise ValueError("loop end without start")
                s = opened.pop()
                prog.append(("until", ing(g[1]) if g[1] else None, s))
                prog[s] = ("loop", prog[s][1], len(prog))
            break
        else:
            raise ValueError("unknown step " + st)
    if opened:
        raise ValueError("unclosed loop")
    return prog


def _chef_run(recipes, title, bowls, dishes, budget, depth=0):
    """Run one recipe on (bowls, dishes) [lists of [value, liquid] stacks]; returns the printed text (Refrigerate N /
    Serves N)."""
    if depth > 20:
        raise ValueError("recursion")
    ings, method, serves = recipes[title]
    val = {n: [v, liq] for n, v, liq in ings}
    prog = _chef_compile(method, val)
    out, pc, loops = [], 0, []

    def bowl(i):
        while len(bowls) <= i:
            bowls.append([])
        return bowls[i]

    def dish(i):
        while len(dishes) <= i:
            dishes.append([])
        return dishes[i]

    def get(n):
        if val[n][0] is None:
            raise ValueError("undefined ingredient " + n)
        return val[n][0]

    def show(n):
        for d in dishes[:n]:
            for v, liq in reversed(d):
                out.append(chr(int(v)) if liq else str(v))
            d.clear()
    while pc < len(prog):
        budget[0] -= 1
        if budget[0] < 0:
            raise ValueError("step cap")
        op = prog[pc]
        k = op[0]
        pc += 1
        if k == "take":
            val[op[1]][0] = 0
        elif k == "put":
            bowl(op[2]).append([get(op[1]), val[op[1]][1]])
        elif k == "fold":
            val[op[1]][0] = bowl(op[2]).pop()[0]
        elif k in ("add", "remove", "combine", "divide"):
            b, v = bowl(op[2]), get(op[1])
            if not b:
                raise ValueError("empty bowl")
            x = b[-1][0]
            b[-1][0] = (x + v if k == "add" else x - v if k == "remove" else x * v if k == "combine"
                        else (x // v if isinstance(x, int) and x % v == 0 else x / v))
        elif k == "dry":
            bowl(op[1]).append([sum(v for v, liq in val.values() if v is not None and not liq), False])
        elif k == "liq":
            val[op[1]][1] = True
        elif k == "liqbowl":
            for e in bowl(op[1]):
                e[1] = True
        elif k in ("stirn", "stiri"):
            b = bowl(op[2] if k == "stiri" else op[1])
            n = get(op[1]) if k == "stiri" else op[2]
            if b:
                e = b.pop()
                b.insert(max(0, len(b) - int(n)), e)
        elif k == "clean":
            bowl(op[1]).clear()
        elif k == "pour":
            dish(op[2]).extend([list(e) for e in bowl(op[1])])
        elif k == "loop":
            if get(op[1]) == 0:
                pc = op[2]
            else:
                loops.append(op[2])
        elif k == "until":
            if op[1]:
                val[op[1]][0] = get(op[1]) - 1
            if loops:
                loops.pop()
            pc = op[2]
        elif k == "aside":
            if loops:
                pc = loops.pop()
        elif k == "serve":
            if op[1] not in recipes:
                raise ValueError("no auxiliary recipe " + op[1])
            sub_b = [[list(e) for e in b] for b in bowls]
            sub_d = [[list(e) for e in d] for d in dishes]
            out.append(_chef_run(recipes, op[1], sub_b, sub_d, budget, depth + 1))
            bowl(0).extend(sub_b[0] if sub_b else [])
        elif k == "fridge":
            if op[1]:
                show(op[1])
            return "".join(out)
        elif k == "mix":
            pass   # random shuffle in the spec: a sentence printer never relies on it
    if serves:
        show(serves)
    return "".join(out)


def chef_dec(t, max_steps=400_000):
    """A Chef recipe program -> the text its 'Serves N.' (or Refrigerate) prints; raises ValueError for anything that is
    not a runnable recipe with printable output (a plain English recipe has no compilable Method)."""
    if isinstance(t, (bytes, bytearray)):
        t = t.decode("utf-8", "replace")
    got = _chef_recipes(t)
    if not got:
        raise ValueError("not a Chef recipe")
    recipes, main = got
    out = _chef_run(recipes, main, [], [], [max_steps])
    if not out.strip() or any((ord(ch) < 32 and ch not in "\t\n\r") or 127 <= ord(ch) < 160 for ch in out):
        raise ValueError("no printable output")
    return out


_CHEF_FOODS = ("haricot beans", "eggs", "lard", "oil", "zucchinis", "water", "red salmon", "dijon mustard", "potatoes",
               "flour", "sugar", "butter", "milk", "salt", "honey", "cocoa", "vanilla", "yeast", "cream", "cheese",
               "garlic", "onions", "carrots", "rice", "pepper", "basil", "thyme", "lemons", "apples", "pears", "plums",
               "raisins", "almonds", "walnuts", "oats", "barley", "ginger", "nutmeg", "cloves", "mint", "dates",
               "figs", "peas", "leeks", "beets", "kale", "tofu", "corn", "bacon", "ham")


def chef_enc(s, title="Hello World Souffle"):
    """'Hello World Souffle' generator: one ingredient per distinct code point (amount = code), Put them back to front,
    Liquefy the bowl, Pour it into the baking dish, Serves 1."""
    names, ings = {}, []
    for ch in s:
        if ch not in names:
            k = len(names)
            nm = _CHEF_FOODS[k % len(_CHEF_FOODS)] + ("" if k < len(_CHEF_FOODS) else " " + str(k // len(_CHEF_FOODS)))
            names[ch] = nm
            ings.append(f"{ord(ch)} g {nm}")
    steps = [f"Put {names[ch]} into the mixing bowl." for ch in reversed(s)]
    steps += ["Liquefy contents of the mixing bowl.", "Pour contents of the mixing bowl into the baking dish."]
    return (f"{title}.\n\nIngredients.\n" + "\n".join(ings) + "\n\nMethod.\n" + "\n".join(steps) + "\n\nServes 1.\n")


def chef_free(p):
    try:
        x = chef_dec(p.replace("\\n", "\n") if "\n" not in p else p)
        return [x] if _crib_piece(x) > 0 or SLUG.search(x) else []
    except (ValueError, IndexError, KeyError, TypeError, ZeroDivisionError, OverflowError, RecursionError):
        return []


_SPL_NEG_NOUNS = set("hell microsoft bastard beggar blister codpiece coward curse death devil draught famine flirt-gill "
                     "goat hate hog hound leech lie pig plague starvation toad war wolf".split())
_SPL_NOUNS = _SPL_NEG_NOUNS | set(
    "heaven king lord angel flower happiness joy plum hero rose kingdom pony animal aunt brother cat chihuahua cousin "
    "cow daughter door face father fellow granddaughter grandfather grandmother grandson hair hamster horse lamp "
    "lantern mistletoe moon morning mother nephew niece nose purse road roman sister sky son squirrel thing town tree "
    "uncle wind".split())
_SPL_NEG_ADJ = set("bad cowardly cursed damned dirty disgusting distasteful dusty evil fat-kidneyed fatherless fat foul "
                   "hairy half-witted horrible horrid infected lying miserable misused oozing rotten smelly snotty sorry "
                   "stinking stuffed stupid vile villainous worried".split())
_SPL_DET = set("a an the my mine your thy thine his her its their".split())
_SPL_BIN = {("the", "sum", "of"): "+", ("the", "difference", "between"): "-", ("the", "product", "of"): "*",
            ("the", "quotient", "between"): "/", ("the", "remainder", "of", "the", "quotient", "between"): "%"}
_SPL_UN = {("the", "square", "root", "of"): "sqrt", ("the", "square", "of"): "sq", ("the", "cube", "of"): "cube",
           ("the", "factorial", "of"): "fact", ("twice",): "twice"}
_ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}


def _roman(r):
    n, prev = 0, 0
    for ch in reversed(r.lower()):
        v = _ROMAN[ch]
        n, prev = (n - v, prev) if v < prev else (n + v, v)
    return n


def _spl_value(w, i, env):
    """(value, next index) of the SPL value starting at tokens w[i]."""
    for pre, op in sorted(_SPL_BIN.items(), key=lambda kv: -len(kv[0])):
        if tuple(w[i:i + len(pre)]) == pre:
            a, j = _spl_value(w, i + len(pre), env)
            if j >= len(w) or w[j] != "and":
                raise ValueError("binary without and")
            b, j = _spl_value(w, j + 1, env)
            if op in "/%" and b == 0:
                raise ValueError("division by zero")
            q = int(a / b) if op in "/%" else 0
            return {"+": a + b, "-": a - b, "*": a * b, "/": q, "%": a - q * b if op == "%" else 0}[op], j
    for pre, op in _SPL_UN.items():
        if tuple(w[i:i + len(pre)]) == pre:
            a, j = _spl_value(w, i + len(pre), env)
            if op == "fact" and not 0 <= a <= 200:
                raise ValueError("factorial range")
            return {"sqrt": math.isqrt(abs(a)) * (1 if a >= 0 else -1), "sq": a * a, "cube": a ** 3,
                    "fact": math.factorial(a) if op == "fact" else 0, "twice": 2 * a}[op], j + 0
    x = w[i] if i < len(w) else ""
    if x in ("nothing", "zero"):
        return 0, i + 1
    if x in ("i", "me", "myself"):
        return env["val"][env["spk"]], i + 1
    if x in ("you", "thee", "thou", "thyself", "yourself"):
        return env["val"][env["lis"]()], i + 1
    if x.startswith("@"):
        return env["val"][int(x[1:])], i + 1
    j = i + (x in _SPL_DET)
    adj = 0
    while j < len(w):
        if w[j] == "summer's" and j + 1 < len(w) and w[j + 1] == "day" or w[j] == "stone" and j + 1 < len(w) \
                and w[j + 1] == "wall":
            return 2 ** adj, j + 2
        if w[j] in _SPL_NOUNS:
            return (-1 if w[j] in _SPL_NEG_NOUNS else 1) * 2 ** adj, j + 1
        if w[j] == "and" or w[j].startswith("@") or not re.fullmatch(r"[a-z'\-]+", w[j]):
            break
        adj += 1
        j += 1
    raise ValueError("no noun phrase")


def _spl_parse(t):
    """(characters, events) of a Shakespeare play, else None. events: ('scene', act, scene) | ('enter', [ids]) |
    ('exit', [ids]) | ('exeunt', [ids]|None) | ('say', id, sentence)."""
    t = re.sub(r"\s+", " ", t.replace("\r", " ")).strip()
    a = re.search(r"\bAct\s+[IVXLCDM]+\s*:", t)
    if not a:
        return None
    head = t[:a.start()]
    m = re.match(r"[^.!]*[.!]", head)
    if not m:
        return None
    chars = [c.strip() for c in re.findall(r"(?:^|[.!?])\s*([A-Z][A-Za-z' -]{0,40}?)\s*,", head[m.end() - 1:])]
    chars = list(dict.fromkeys(c for c in chars if c))
    if not chars:
        return None
    body = t[a.start():]
    names = sorted(range(len(chars)), key=lambda k: -len(chars[k]))
    nrx = "|".join(re.escape(chars[k]) for k in names)
    cid = {c.lower(): k for k, c in enumerate(chars)}
    tok = re.compile(r"\bAct\s+([IVXLCDM]+)\s*:[^.!]*[.!]|\bScene\s+([IVXLCDM]+)\s*:[^.!]*[.!]|\[\s*(Enter|Exit|Exeunt)"
                     r"([^\]]*)\]|\[[^\]]*\]|(?:^|(?<=[.!?\]]))\s*(" + nrx + r")\s*:", re.I)

    def ids(s):
        return [cid[c.strip().lower()] for c in re.split(r",|\band\b", s) if c.strip()]
    ev, act, spk, pos = [], 0, None, 0
    ms = list(tok.finditer(body))
    for n, m in enumerate(ms):
        end = ms[n + 1].start() if n + 1 < len(ms) else len(body)
        if m.group(1):
            act, spk = _roman(m.group(1)), None
        elif m.group(2):
            ev.append(("scene", act, _roman(m.group(2))))
            spk = None
        elif m.group(3):
            k = m.group(3).lower()
            who = ids(m.group(4)) if m.group(4).strip() else None
            if k != "exeunt" and not who:
                return None
            ev.append((k, who))
            spk = None
        elif m.group(5):
            spk = cid[m.group(5).lower()]
            for s in re.findall(r"[^.!?]+[.!?]", body[m.end():end]):
                ev.append(("say", spk, s.strip()))
    return chars, ev


def spl_dec(t, max_steps=400_000):
    """A Shakespeare (SPL) play -> the text its 'Speak your mind!' / 'Open your heart!' lines print; raises ValueError
    for anything that is not a play with printable output."""
    if isinstance(t, (bytes, bytearray)):
        t = t.decode("utf-8", "replace")
    got = _spl_parse(t)
    if not got:
        raise ValueError("not a Shakespeare play")
    chars, ev = got
    labels, act = {}, 0
    for i, e in enumerate(ev):
        if e[0] == "scene":
            labels[(e[1], e[2])] = i
    val, stk, stage, out = [0] * len(chars), [[] for _ in chars], [], []
    nrx = re.compile(r"\b(" + "|".join(re.escape(c) for c in sorted(chars, key=len, reverse=True)) + r")\b", re.I)
    cid = {c.lower(): k for k, c in enumerate(chars)}
    env = {"val": val, "spk": None}

    def lis():
        o = [c for c in stage if c != env["spk"]]
        if len(o) != 1:
            raise ValueError("ambiguous listener")
        return o[0]
    env["lis"] = lis
    cond, pc, steps, said = None, 0, 0, 0
    while pc < len(ev):
        steps += 1
        if steps > max_steps:
            raise ValueError("step cap")
        e = ev[pc]
        pc += 1
        k = e[0]
        if k == "scene":
            act = e[1]
        elif k == "enter":
            stage.extend(c for c in e[1] if c not in stage)
        elif k == "exit":
            stage[:] = [c for c in stage if c not in e[1]]
        elif k == "exeunt":
            stage[:] = [c for c in stage if e[1] and c not in e[1]]
        elif k == "say":
            env["spk"] = e[1]
            s = nrx.sub(lambda m: "@%d" % cid[m.group(1).lower()], e[2])
            q = s.endswith("?")
            s = s.rstrip(".!?").strip().lower()
            mc = re.match(r"if (so|not)\s*,\s*(.*)$", s)
            if mc:
                if cond is None or cond != (mc.group(1) == "so"):
                    continue
                s = mc.group(2)
            w = re.findall(r"@\d+|[a-z][a-z'\-]*", s)
            if q:
                mq = re.match(r"(?:am|are|art|be|is) (.+?) (?:(better|bigger|fresher|friendlier|nicer|jollier|punier"
                              r"|smaller|worse|more [a-z\-]+) than|as [a-z\-]+ as) (.+)$", " ".join(w))
                if not mq:
                    raise ValueError("bad question")
                x, j = _spl_value(mq.group(1).split(), 0, env)
                y, j = _spl_value(mq.group(3).split(), 0, env)
                c = mq.group(2)
                cond = (x == y if c is None else x < y if c in ("punier", "smaller", "worse")
                        or (c.startswith("more ") and c[5:] in _SPL_NEG_ADJ) else x > y)
            elif re.match(r"speak (?:your|thy|thine) mind$", s):
                out.append(chr(val[lis()]))
                said += 1
            elif re.match(r"open (?:your|thy|thine) heart$", s):
                out.append(str(val[lis()]))
                said += 1
            elif re.match(r"(?:listen to (?:your|thy|thine) heart|open (?:your|thy|thine) mind)$", s):
                val[lis()] = -1 if "mind" in s else 0
            elif re.match(r"(?:let us|we shall|we must) (?:proceed|return) to (scene|act) ([ivxlcdm]+)$", s):
                mg = re.match(r".* (scene|act) ([ivxlcdm]+)$", s)
                key = (act, _roman(mg.group(2))) if mg.group(1) == "scene" else \
                    min((kk for kk in labels if kk[0] == _roman(mg.group(2))), default=None)
                if key not in labels:
                    raise ValueError("no such scene")
                pc = labels[key]
            elif w[:1] == ["remember"]:
                stk[lis()].append(_spl_value(w, 1, env)[0])
            elif w[:1] == ["recall"]:
                if not stk[lis()]:
                    raise ValueError("empty stack")
                val[lis()] = stk[lis()].pop()
            elif w[:1] in (["you"], ["thou"], ["thee"]):
                j = 1 + (len(w) > 1 and w[1] in ("am", "are", "art", "be", "is"))
                if j < len(w) and w[j] == "as":
                    j += 1 if j + 1 < len(w) and w[j + 1] not in _SPL_NOUNS and j + 2 < len(w) and w[j + 2] != "as" \
                        else 3 if j + 2 < len(w) and w[j + 2] == "as" else 1
                val[lis()] = _spl_value(w, j, env)[0]
    x = "".join(out)
    if not said or not x.strip() or any((ord(ch) < 32 and ch not in "\t\n\r") or 127 <= ord(ch) < 160 for ch in x):
        raise ValueError("no printable output")
    return x


def spl_enc(s, a="Romeo", b="Juliet"):
    """Two-character play: per char, 'You are as lovely as <sum of a [big]*k cat noun phrases>! Speak your mind!'."""
    def np_(n):
        return "a " + "big " * n + "cat"

    def expr(v):
        bits = [k for k in range(v.bit_length()) if v >> k & 1] or [None]
        e = "nothing" if bits == [None] else np_(bits[-1])
        for k in reversed(bits[:-1]):
            e = f"the sum of {np_(k)} and {e}"
        return e
    lines = [f"You are as lovely as {expr(ord(ch))}! Speak your mind!" for ch in s]
    return (f"A Play of Letters.\n\n{a}, a young man.\n{b}, a lady.\n\n Act I: The message.\n\n Scene I: The speech."
            f"\n\n[Enter {a} and {b}]\n\n{b}:\n " + "\n ".join(lines) + "\n\n[Exeunt]\n")


def spl_free(p):
    try:
        x = spl_dec(p.replace("\\n", "\n") if "\n" not in p else p)
        return [x] if _crib_piece(x) > 0 or SLUG.search(x) else []
    except (ValueError, IndexError, KeyError, TypeError, ZeroDivisionError, OverflowError, RecursionError):
        return []


CANDIDATES += [("chef", chef_enc, chef_dec), ("shakespeare", spl_enc, spl_dec)]
SPECULATIVE_FREE += (("chef", chef_free), ("shakespeare", spl_free))


# ------------------------------------- Toy instruction-set listings ("a very small language" read as a tiny machine)
# A program whose output is the sentence, SIMULATED (never executed): generic assembly / stack-VM lines (PUSH 78 / OUT,
# MOV R1, 'N' / PRINT R1, LDA #$4E / JSR $FFD2, mov ah,0eh / mov al,4eh / int 10h, mov dl,.. / mov ah,2 / int 21h),
# Forth (78 emit, char N emit, ." text"), dc (78P, 16i 4EP, [text]P) and PostScript ((text) show / print / =).
# Literals: 78, -3, 0x4E, $4E, 4Eh, 0b.., 116o, 'N', #imm. Jumps / LOOP / DJNZ / dc macros run under a step cap; an
# unknown mnemonic or word rejects the listing, so a decimal char-code list (D5) or prose never reads as a program.
_VM_STEPS = 200_000
_VM_PUSH = {"push", "psh", "pushi", "ipush", "bipush", "sipush", "ldc", "const", "lit", "pushc", "pushb"}
_VM_LOAD = {"load", "ld", "lda", "ldi", "li", "set", "mov", "mvi", "movl", "movb", "movw", "movi", "let", "ldx", "ldy",
            "store", "assign", "lit8"}
_VM_ARITH = {"add": lambda a, b: a + b, "addi": lambda a, b: a + b, "plus": lambda a, b: a + b,
             "sub": lambda a, b: a - b, "subi": lambda a, b: a - b, "minus": lambda a, b: a - b,
             "mul": lambda a, b: a * b, "mult": lambda a, b: a * b, "imul": lambda a, b: a * b,
             "times": lambda a, b: a * b, "div": lambda a, b: a // b, "idiv": lambda a, b: a // b,
             "mod": lambda a, b: a % b, "xor": lambda a, b: a ^ b, "and": lambda a, b: a & b, "or": lambda a, b: a | b,
             "shl": lambda a, b: a << b, "shr": lambda a, b: a >> b, "adc": lambda a, b: a + b,
             "sbc": lambda a, b: a - b, "cmp": None}
_VM_UNARY = {"inc": 1, "incr": 1, "inx": 1, "iny": 1, "dec": -1, "decr": -1, "dex": -1, "dey": -1, "neg": 0}
_VM_OUT = {"out", "outc", "print", "prn", "prt", "printc", "putc", "putchar", "putch", "emit", "write", "wrt", "chr",
           "say", "echo", "display", "disp", "outchar", "pchar", "printchar", "printch", "output", "print_char",
           "wrch", "tx", "send", "prc", "oute"}
_VM_CALL_OUT = {"putchar", "_putchar", "putc", "chrout", "$ffd2", "0xffd2", "ffd2h", "65490", "printchar",
                "print_char", "outch", "outchar", "wrch", "oswrch", "$ffee", "0xffee", "emit", "bdos"}
_VM_HALT = {"hlt", "halt", "end", "stop", "ret", "exit", "quit", "bye", "brk", "done"}
_VM_NOP = {"nop", "start", "begin", "org", ".org", "section", ".text", ".code", "bits", "use16", "cpu", "global",
           "main", "clc", "cld", "cli", "sei", "sti"}
_VM_JMP = {"jmp", "jp", "goto", "br", "bra", "j", "b", "jr"}
_VM_JCOND = {"jz": "z", "je": "z", "beq": "z", "brz": "z", "jeq": "z", "jnz": "nz", "jne": "nz", "bne": "nz",
             "brnz": "nz", "jgt": "gt", "jg": "gt", "bgt": "gt", "jlt": "lt", "jl": "lt", "blt": "lt", "jge": "ge",
             "bge": "ge", "jle": "le", "ble": "le", "jpos": "gt", "jneg": "lt"}
_VM_ACC = {"acc", "ac", "accumulator", "a"}
_VM_INT = re.compile(r"""[#]?(?:(-?\d+)|(-?)0x([0-9a-f]+)|(-?)\$([0-9a-f]+)|(-?)(\d[0-9a-f]*)h|0b([01]+)|([01]+)b
                     |0o([0-7]+)|([0-7]+)[oq]|'(.)'|"(.)")""", re.I | re.X)
_VM_REG = re.compile(r"[a-z_.%][\w.]*", re.I)
_VM_LABEL = re.compile(r"^\s*([a-z_.$][\w.$]*):(?!:)", re.I)


def _vm_int(tok):
    """A numeric / char literal -> int, else None."""
    m = _VM_INT.fullmatch(tok.strip())
    if not m:
        return None
    g = m.groups()
    if g[0] is not None:
        return int(g[0])
    for sign, digits in ((g[1], g[2]), (g[3], g[4]), (g[5], g[6])):
        if digits is not None:
            return int(digits, 16) * (-1 if sign else 1)
    for digits, base in ((g[7], 2), (g[8], 2), (g[9], 8), (g[10], 8)):
        if digits is not None:
            return int(digits, base)
    return ord(g[11] if g[11] is not None else g[12])


def _vm_strip(line):
    """Drop a ; / // / '# ' comment (outside quotes)."""
    out, q = [], None
    for i, ch in enumerate(line):
        if q:
            q = None if ch == q else q
        elif ch in "'\"":
            q = ch
        elif ch == ";" or line.startswith("//", i) or (ch == "#" and (i + 1 == len(line) or line[i + 1] in " \t#")):
            break
        out.append(ch)
    return "".join(out)


def _vm_operands(rest):
    """'al, 0x4e' / 'R1 78' / '"text"' -> operand tokens (quotes kept)."""
    return [m.group() for m in re.finditer(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[^\s,]+', rest)]


_VM_ALL = (_VM_PUSH | _VM_LOAD | set(_VM_ARITH) | set(_VM_UNARY) | _VM_OUT | _VM_HALT | _VM_NOP | _VM_JMP
           | set(_VM_JCOND) | {"pop", "dup", "swap", "drop", "discard", "over", "int", "syscall", "call", "jsr", "bsr",
                               "loop", "djnz", "dbra", "dbf", "jcxz", "xchg", "nl", "newline", "crlf", "space"})


def _vm_parse(lines):
    """Lines -> ([(mnemonic, operands)], labels) or None (an unknown mnemonic / a bare-number line)."""
    prog, labels = [], {}
    for line in lines:
        line = _vm_strip(line)
        while True:
            m = _VM_LABEL.match(line)
            if not m:
                break
            labels[m.group(1).lower()] = len(prog)
            line = line[m.end():]
        if not line.strip():
            continue
        parts = line.strip().split(None, 1)
        op = parts[0].lower()
        if op not in _VM_ALL:
            return None
        prog.append((op, _vm_operands(parts[1]) if len(parts) > 1 else []))
    return (prog, labels) if prog else None


_X86 = re.compile(r"[re]?([abcd])x|([abcd])([lh])", re.I)


class _VMState:
    def __init__(self):
        self.r, self.stack, self.out, self.flag, self.last = {}, [], [], 0, "a"

    def get(self, name):
        n = name.lower()
        n = "a" if n in _VM_ACC else n
        m = _X86.fullmatch(n)
        if m and m.group(2):
            v = self.r.get(m.group(2) + "x", 0)
            return (v >> 8 if m.group(3) == "h" else v) & 0xFF
        return self.r.get(m.group(1) + "x" if m else n, 0)

    def put(self, name, v):
        n = name.lower()
        n = "a" if n in _VM_ACC else n
        m = _X86.fullmatch(n)
        if m and m.group(2):
            k, old = m.group(2) + "x", self.r.get(m.group(2) + "x", 0)
            v = (old & 0xFF) | (v & 0xFF) << 8 if m.group(3) == "h" else (old & ~0xFF) | (v & 0xFF)
            n = k
        elif m:
            n = m.group(1) + "x"
        self.r[n] = v
        self.last = name.lower()

    def val(self, tok):
        v = _vm_int(tok)
        if v is not None:
            return v
        if _VM_REG.fullmatch(tok):
            return self.get(tok)
        raise ValueError("operand")

    def emit(self, v):
        if isinstance(v, str):
            self.out.extend(v.encode("utf-8"))
        elif 0 <= v < 0x110000:
            self.out.append(v)
        else:
            raise ValueError("unprintable")


def _vm_run(prog, labels):
    """Simulate a parsed listing -> the printed code points, or None."""
    st = _VMState()
    stacky = any(op in _VM_PUSH or op in ("dup", "swap", "drop", "over") for op, _a in prog)
    pc = steps = 0
    while pc < len(prog):
        steps += 1
        if steps > _VM_STEPS:
            return None
        op, a = prog[pc]
        pc += 1
        if op in _VM_PUSH:
            st.stack.append(st.val(a[0]) if a else st.get("a"))
        elif op == "pop":
            v = st.stack.pop() if st.stack else 0
            if a:
                st.put(a[0], v)
        elif op == "dup":
            st.stack.append(st.stack[-1])
        elif op == "swap":
            st.stack[-2:] = st.stack[-2:][::-1]
        elif op in ("drop", "discard"):
            st.stack.pop()
        elif op == "over":
            st.stack.append(st.stack[-2])
        elif op in _VM_LOAD:
            if len(a) >= 2:
                st.put(a[0], st.val(a[-1]))
            elif a:
                v = st.val(a[0])
                if op == "store" and stacky:
                    st.put(a[0], st.stack.pop())
                elif op in ("ldx", "ldy"):
                    st.put(op[-1], v)
                elif stacky and op in ("ldc", "load", "ld", "lit8"):
                    st.stack.append(v)
                else:
                    st.put("a", v)
            else:
                return None
        elif op == "xchg" and len(a) == 2:
            x, y = st.get(a[0]), st.get(a[1])
            st.put(a[0], y)
            st.put(a[1], x)
        elif op in _VM_ARITH:
            fn = _VM_ARITH[op] or (lambda x, y: x - y)
            if len(a) >= 2:
                v = fn(st.get(a[0]), st.val(a[-1]))
                if op != "cmp":
                    st.put(a[0], v)
            elif a and stacky and st.stack:
                v = fn(st.stack[-1], st.val(a[0]))
                if op != "cmp":
                    st.stack[-1] = v
            elif a:
                v = fn(st.get("a"), st.val(a[0]))
                if op != "cmp":
                    st.put("a", v)
            elif len(st.stack) >= 2:
                y, x = st.stack.pop(), st.stack.pop()
                v = fn(x, y)
                if op != "cmp":
                    st.stack.append(v)
            else:
                return None
            st.flag = v
        elif op in _VM_UNARY:
            d = _VM_UNARY[op]
            tgt = a[0] if a else ("xy"[op[-1] == "y"] if op in ("inx", "iny", "dex", "dey") else None)
            if tgt is None and stacky and st.stack:
                st.stack[-1] = st.stack[-1] + d if d else -st.stack[-1]
                st.flag = st.stack[-1]
            else:
                tgt = tgt or "a"
                st.put(tgt, st.get(tgt) + d if d else -st.get(tgt))
                st.flag = st.get(tgt)
        elif op in _VM_OUT or op in ("nl", "newline", "crlf", "space"):
            if op in ("nl", "newline", "crlf", "space"):
                st.emit(" " if op == "space" else "\n")
            elif a and a[-1][:1] == '"' and len(a[-1]) > 3:
                st.emit(a[-1][1:-1].encode().decode("unicode_escape", "strict") if "\\" in a[-1] else a[-1][1:-1])
            elif a:
                v = st.val(a[-1])
                if len(a) == 1 and _vm_int(a[0]) is not None and v < 32 and v not in (9, 10, 13) and "a" in st.r:
                    v = st.get("a")   # 8080 / Z80 `OUT port` writes A
                st.emit(v)
            elif stacky and st.stack:
                st.emit(st.stack.pop())
            else:
                st.emit(st.get("a") if "a" in st.r else st.get(st.last))
        elif op in ("int", "syscall"):
            n = _vm_int(a[0]) if a else None
            ah = st.get("ah")
            if n == 0x10 and ah == 0x0E:
                st.emit(st.get("al"))
            elif n == 0x21 and ah in (2, 6):
                st.emit(st.get("dl"))
        elif op in ("call", "jsr", "bsr"):
            if a and a[0].lower() in _VM_CALL_OUT:
                if stacky and st.stack:
                    st.emit(st.stack.pop())
                else:
                    st.emit(st.get("a") if "a" in st.r else st.get(st.last))
            elif a and a[0].lower() in labels:
                return None   # no subroutine model
        elif op in _VM_JMP or op in _VM_JCOND or op in ("loop", "djnz", "dbra", "dbf", "jcxz"):
            if not a or a[-1].lower() not in labels:
                return None
            tgt, f = labels[a[-1].lower()], st.flag
            if op in _VM_JMP:
                take = True
            elif op in _VM_JCOND:
                take = {"z": f == 0, "nz": f != 0, "gt": f > 0, "lt": f < 0, "ge": f >= 0, "le": f <= 0}[_VM_JCOND[op]]
            elif op == "loop":
                st.put("cx", st.get("cx") - 1)
                take = st.get("cx") != 0
            elif op == "jcxz":
                take = st.get("cx") == 0
            else:
                reg = a[0] if len(a) == 2 else "b"
                st.put(reg, st.get(reg) - 1)
                take = st.get(reg) not in (0, -1) if op in ("dbra", "dbf") else st.get(reg) != 0
            if take:
                pc = tgt
        elif op in _VM_HALT:
            break
        # _VM_NOP: nothing
    return st.out


_FORTH_ARITH = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a // b,
                "mod": lambda a, b: a % b, "and": lambda a, b: a & b, "or": lambda a, b: a | b,
                "xor": lambda a, b: a ^ b}


def _forth_run(t):
    """Forth: n emit / char X emit / [char] X emit / ." text" / s" text" type / .( text) / cr / bl / space(s)."""
    out, stack, base, i, n, saw = [], [], 10, 0, len(t), False
    while i < n:
        if t[i].isspace():
            i += 1
            continue
        j = i
        while j < n and not t[j].isspace():
            j += 1
        w, wl = t[i:j], t[i:j].lower()
        i = j
        if wl in ('."', 's"', ".("):
            end = t.find(")" if wl == ".(" else '"', i + 1)
            if end < 0:
                return None
            s = t[i + 1:end]
            i = end + 1
            if wl == 's"':
                stack.append(s)
            else:
                out.extend(s.encode("utf-8"))
                saw = True
            continue
        if wl == "\\":
            nl = t.find("\n", i)
            i = n if nl < 0 else nl + 1
            continue
        if wl == "(":
            end = t.find(")", i)
            i = n if end < 0 else end + 1
            continue
        if wl in ("char", "[char]"):
            while i < n and t[i].isspace():
                i += 1
            if i >= n:
                return None
            stack.append(ord(t[i]))
            while i < n and not t[i].isspace():
                i += 1
            continue
        try:
            if wl == "emit":
                v = stack.pop()
                if isinstance(v, str) or not 0 <= v < 0x110000:
                    return None
                out.append(v)
                saw = True
            elif wl == "type":
                v = stack.pop()
                if isinstance(v, str):
                    out.extend(v.encode("utf-8"))
                    saw = True
                else:
                    return None
            elif wl == "cr":
                out.append(10)
            elif wl == "space":
                out.append(32)
            elif wl == "spaces":
                out.extend([32] * max(0, min(stack.pop(), 256)))
            elif wl == "bl":
                stack.append(32)
            elif wl in _FORTH_ARITH:
                b, a = stack.pop(), stack.pop()
                stack.append(_FORTH_ARITH[wl](a, b))
            elif wl in ("1+", "1-", "2*", "negate"):
                stack.append({"1+": lambda v: v + 1, "1-": lambda v: v - 1, "2*": lambda v: v * 2,
                              "negate": lambda v: -v}[wl](stack.pop()))
            elif wl == "dup":
                stack.append(stack[-1])
            elif wl == "drop":
                stack.pop()
            elif wl == "swap":
                stack[-2:] = stack[-2:][::-1]
            elif wl == "over":
                stack.append(stack[-2])
            elif wl in ("hex", "decimal"):
                base = 16 if wl == "hex" else 10
            elif wl == "bye":
                break
            else:
                m = re.fullmatch(r"(-?)(?:\$([0-9a-f]+)|#(\d+)|%([01]+)|'(.)'?|([0-9a-z]+))", wl, re.I)
                if not m:
                    return None
                sign = -1 if m.group(1) else 1
                if m.group(2):
                    v = int(m.group(2), 16)
                elif m.group(3):
                    v = int(m.group(3))
                elif m.group(4):
                    v = int(m.group(4), 2)
                elif m.group(5):
                    v = ord(w[len(m.group(1)) + 1])
                else:
                    v = int(m.group(6), base)
                stack.append(sign * v)
        except (IndexError, ValueError, ZeroDivisionError, TypeError):
            return None
        if len(out) > 1 << 16:
            return None
    return out if saw else None


def _dc_run(t):
    """GNU dc: numbers (A-F digits, _ sign, i input base), [strings], P (number -> base-256 bytes) n p, + - * / % ^,
    d r c z, k i o, s/l/x registers + < > = conditionals (macros under the step cap), # comments, q."""
    stack, regs, out, ibase = [], {}, [], 10
    work, steps, saw = [(t, 0)], 0, False
    try:
        while work:
            src, i = work.pop()
            while i < len(src):
                steps += 1
                if steps > _VM_STEPS or len(out) > 1 << 16:
                    return None
                ch = src[i]
                i += 1
                if ch.isspace():
                    continue
                if ch == "#":
                    nl = src.find("\n", i)
                    i = len(src) if nl < 0 else nl + 1
                    continue
                if ch.isdigit() or ch in "ABCDEF_":
                    neg, v = ch == "_", 0
                    if neg:
                        if i >= len(src) or not (src[i].isdigit() or src[i] in "ABCDEF"):
                            return None
                    else:
                        i -= 1
                    while i < len(src) and (src[i].isdigit() or src[i] in "ABCDEF"):
                        v = v * ibase + int(src[i], 16)
                        i += 1
                    stack.append(-v if neg else v)
                elif ch == "[":
                    depth, j = 1, i
                    while j < len(src) and depth:
                        depth += {"[": 1, "]": -1}.get(src[j], 0)
                        j += 1
                    if depth:
                        return None
                    stack.append(src[i:j - 1])
                    i = j
                elif ch == "P":
                    v = stack.pop()
                    if isinstance(v, str):
                        out.extend(v.encode("utf-8"))
                    else:
                        v = abs(v)
                        out.extend(v.to_bytes(max(1, (v.bit_length() + 7) // 8), "big"))
                    saw = True
                elif ch in "np":
                    v = stack.pop() if ch == "n" else stack[-1]
                    out.extend((v if isinstance(v, str) else str(v).replace("-", "_")).encode("utf-8"))
                    if ch == "p":
                        out.append(10)
                elif ch in "+-*/%^":
                    b, a = stack.pop(), stack.pop()
                    if isinstance(a, str) or isinstance(b, str) or (ch == "^" and not 0 <= b < 64):
                        return None
                    stack.append({"+": a + b, "-": a - b, "*": a * b, "/": int(a / b) if b else None,
                                  "%": a - b * int(a / b) if b else None, "^": a ** b}[ch])
                    if stack[-1] is None:
                        return None
                elif ch == "d":
                    stack.append(stack[-1])
                elif ch == "r":
                    stack[-2:] = stack[-2:][::-1]
                elif ch == "c":
                    stack.clear()
                elif ch == "z":
                    stack.append(len(stack))
                elif ch in "kio":
                    v = stack.pop()
                    if ch == "i":
                        if not 2 <= v <= 16:
                            return None
                        ibase = v
                elif ch in "slSL" and i < len(src):
                    r = src[i]
                    i += 1
                    if ch in "sS":
                        regs[r] = stack.pop()
                    else:
                        stack.append(regs.get(r, 0))
                elif ch == "x":
                    v = stack.pop()
                    if isinstance(v, str):
                        work.append((src, i))
                        src, i = v, 0
                    else:
                        stack.append(v)
                elif ch in "<>=!" and i < len(src):
                    neg = ch == "!"
                    if neg:
                        ch = src[i]
                        i += 1
                        if ch not in "<>=" or i >= len(src):
                            return None
                    r = src[i]
                    i += 1
                    a, b = stack.pop(), stack.pop()
                    take = {"<": a < b, ">": a > b, "=": a == b}[ch] != neg
                    if take and isinstance(regs.get(r), str):
                        work.append((src, i))
                        src, i = regs[r], 0
                elif ch == "q":
                    return out if saw else None
                else:
                    return None
    except (IndexError, ValueError, TypeError, OverflowError):
        return None
    return out if saw else None


_PS_TOK = re.compile(r"%[^\n]*|\((?:[^()\\]|\\.|\((?:[^()\\]|\\.)*\))*\)|<(?!<)[0-9a-fA-F\s]*>|<<|>>|[{}\[\]]"
                     r"|/?[^\s(){}\[\]<>/%]+", re.S)
_PS_ESC = {"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f", "\\": "\\", "(": "(", ")": ")", "\n": ""}


def _ps_string(s):
    return re.sub(r"\\([0-7]{1,3}|.)", lambda m: chr(int(m.group(1), 8)) if m.group(1)[0] in "01234567"
                  else _PS_ESC.get(m.group(1), m.group(1)), s, flags=re.S)


def _ps_run(t):
    """PostScript: string literals ( ) / < hex >, shown by show / print / = / ashow / widthshow; other words inert."""
    if not re.search(r"\)\s*(?:show|print|=|ashow|widthshow|awidthshow|kshow)\b|\)\s*=", t):
        return None
    out, stack, saw = [], [], False
    for m in _PS_TOK.finditer(t):
        w = m.group()
        if w[0] == "%":
            continue
        if w[0] == "(":
            stack.append(_ps_string(w[1:-1]))
        elif w[0] == "<" and w != "<<":
            h = re.sub(r"\s", "", w[1:-1])
            stack.append(bytes.fromhex(h + "0" * (len(h) % 2)).decode("latin-1"))
        elif w in ("show", "print", "=", "==", "ashow", "widthshow", "awidthshow", "kshow"):
            if not stack or not isinstance(stack[-1], str):
                continue
            s = stack.pop()
            out.extend(s.encode("latin-1", "replace") if w != "==" else ("(" + s + ")").encode("latin-1", "replace"))
            if w in ("=", "=="):
                out.append(10)
            saw = True
        else:
            v = _vm_int(w) if re.fullmatch(r"-?\d+", w) else None
            stack.append(v if v is not None else w)
    if saw and out and out[-1] == 10:
        out.pop()
    return out if saw else None


def _vm_programs(t):
    """Line splits worth parsing as an assembly / stack-VM listing: real lines, then ; | ' / ' separated one-liners,
    then a whitespace stream cut at each known mnemonic."""
    lines = t.replace("\\n", "\n").splitlines()
    yield lines
    body = [x for x in lines if x.strip()]
    if len(body) <= 2:
        one = " ".join(body)
        for sep in (r";", r"\|", r"\s/\s", r"\s*\\\s*"):
            parts = re.split(sep, one)
            if len(parts) > 2:
                yield parts
        toks = _vm_operands(one)
        cut, cur = [], []
        for tok in toks:
            if tok.lower() in _VM_ALL and cur and cur[0].lower() not in ("call", "jsr", "bsr", "int") or (
                    tok.lower() in _VM_ALL and cur and len(cur) > 1):
                cut.append(" ".join(cur))
                cur = []
            cur.append(tok)
        if cur:
            cut.append(" ".join(cur))
        if len(cut) > 2:
            yield cut


def vm_reads(t):
    """Every dialect's printed text for a listing (PostScript, dc, Forth, assembly / stack VM), deduped."""
    t = (t or "").strip()
    if not t or len(t) > 1 << 17:
        return []
    reads = []
    for run in (_ps_run, _dc_run, _forth_run):
        try:
            vals = run(t)
        except (ValueError, IndexError, TypeError, OverflowError, RecursionError):
            vals = None
        x = _df_text(vals) if vals else None
        if x and x not in reads:
            reads.append(x)
    for lines in _vm_programs(t):
        try:
            p = _vm_parse(lines)
            vals = _vm_run(*p) if p else None
        except (ValueError, IndexError, TypeError, KeyError, OverflowError, ZeroDivisionError, UnicodeError):
            vals = None
        x = _df_text(vals) if vals else None
        if x and x not in reads:
            reads.append(x)
    return reads


def vm_dec(t):
    """Simulate a toy instruction-set listing -> what it prints; raises on a non-program / junk output."""
    reads = vm_reads(t)
    for x in reads:
        if SLUG.search(x) or _crib_piece(x):
            return x
    if reads and _texty(reads[0]) >= 0.9:
        return reads[0]
    raise ValueError("not a toy instruction listing")


def vm_free(p):
    """Mastery free line: a listing's printed text when it is a crib / slug piece."""
    try:
        return [x for x in vm_reads(p) if _crib_piece(x) or SLUG.search(x)][:1]
    except (ValueError, TypeError, IndexError, KeyError, OverflowError, RecursionError):
        return []


def vm_enc(s, dialect="stack"):
    """A listing printing s, one char per step: stack (PUSH n / OUT), reg (MOV R1, n / PRINT R1), acc (LDA #$hh /
    JSR $FFD2), x86 (mov al,..h / int 10h), forth (n emit), dc (nP), ps ((text) show)."""
    cps = [ord(c) for c in s]
    if dialect == "stack":
        return "\n".join(f"PUSH {n}\nOUT" for n in cps) + "\nHALT"
    if dialect == "reg":
        return "\n".join(f"MOV R1, {n}\nPRINT R1" for n in cps) + "\nHALT"
    if dialect == "acc":
        return "\n".join(f"LDA #${n:02X}\nJSR $FFD2" for n in cps) + "\nBRK"
    if dialect == "x86":
        return "mov ah, 0Eh\n" + "\n".join(f"mov al, {n:02X}h\nint 10h" for n in cps) + "\nhlt"
    if dialect == "forth":
        return " ".join(f"{n} emit" for n in cps)
    if dialect == "dc":
        return "".join(f"{n}P" for n in cps)
    if dialect == "ps":
        return "%!PS\n(" + s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ") print"
    raise ValueError(dialect)


CANDIDATES += [(f"vm-{d}", (lambda d: lambda s: vm_enc(s, d))(d), vm_dec)
               for d in ("stack", "reg", "acc", "x86", "forth", "dc", "ps")]
SPECULATIVE_FREE += (("vm-listing", vm_free),)


# Malbolge: 59049 ten-trit words; the program loads at 0 (whitespace skipped, every char must satisfy (c + i) % 94 in
# the op set), the rest fills with crazy(m[i-1], m[i-2]); op = (m[c] + c) % 94, then m[c] is re-encrypted by xlat2.
_MB_X2 = '5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1CB6v^=I_0/8|jsb9m<.TVac`uY*MK\'X~xDl}REokN:#?G"i@'
_MB_OPS = frozenset((4, 5, 23, 39, 40, 62, 68, 81))
_MB_N = 59049
_MB_CZ = []


def _mb_crazy(a, b):
    """The tritwise crazy op (a = accumulator, b = memory) via a 3-trit x 3-trit table, mod 3^10."""
    if not _MB_CZ:
        t = ((1, 0, 0), (1, 0, 2), (2, 2, 1))
        _MB_CZ.extend(sum(t[y // 3 ** k % 3][x // 3 ** k % 3] * 3 ** k for k in range(3))
                      for y in range(27) for x in range(27))
    r, p = 0, 1
    for _ in range(4):
        r += _MB_CZ[b % 27 * 27 + a % 27] * p
        a, b, p = a // 27, b // 27, p * 27
    return r % _MB_N


def _mb_soup(t):
    """The program's char codes when every non-space char of `t` is a valid Malbolge op at its index, else None."""
    c = [ord(ch) for ch in t if not ch.isspace()]
    if not 8 <= len(c) <= _MB_N or any(not 33 <= x <= 126 or (x + i) % 94 not in _MB_OPS for i, x in enumerate(c)):
        return None
    return c


def malbolge_run(prog, steps=1_500_000, quiet=300_000):
    """Run a Malbolge program (list of char codes, no input: 'in' reads EOF = 59048) -> the bytes it printed (a % 256),
    stopping at 'end', a non-printable instruction, the step cap or `quiet` steps without output."""
    mem, out, a, c, d, last = list(prog), [], 0, 0, 0, 0
    for n in range(steps):
        if max(c, d) >= len(mem):
            while len(mem) <= max(c, d):
                mem.append(_mb_crazy(mem[-1], mem[-2]))
        x = mem[c]
        if not 33 <= x <= 126:
            break
        op = (x + c) % 94
        if op == 4:
            c = mem[d]
            while len(mem) <= c:
                mem.append(_mb_crazy(mem[-1], mem[-2]))
        elif op == 5:
            out.append(a % 256)
            last = n
        elif op == 23:
            a = _MB_N - 1
        elif op == 39:
            a = mem[d] = mem[d] % 3 * 19683 + mem[d] // 3
        elif op == 40:
            d = mem[d]
        elif op == 62:
            a = mem[d] = _mb_crazy(a, mem[d])
        elif op == 81:
            break
        if 33 <= mem[c] <= 126:
            mem[c] = ord(_MB_X2[mem[c] - 33])
        c, d = (c + 1) % _MB_N, (d + 1) % _MB_N
        if n - last > quiet:
            break
    return out


def malbolge_reads(t, steps=1_500_000):
    """Printable outputs of `t` (or of a base64 / hex / compression peel of it) run as Malbolge."""
    out = []
    for x in _bff_peel(t, 2):
        prog = _mb_soup(x)
        if prog:
            y = _bff_text(malbolge_run(prog, steps))
            if y and y not in out:
                out.append(y)
    return out


def malbolge_dec(t):
    """A Malbolge program -> the sentence it prints; raises unless the output passes the slug / crib gate."""
    for y in malbolge_reads(t):
        if _bff_gate(y):
            return y
    raise ValueError("not a Malbolge program")


def malbolge_free(p):
    """Mastery free line: the printed text of a Malbolge program when it is a crib piece."""
    try:
        return [y for y in malbolge_reads(p, 1_000_000) if _bff_gate(y, True)][:3]
    except (ValueError, IndexError, KeyError, TypeError, RecursionError, MemoryError):
        return []


def malbolge_enc(s):
    """Straight-line generator (d == c, so rotr / crazy act on their own source char): per UTF-8 byte the shortest
    nop / rotr / crazy run (BFS on a) leaving a % 256 == byte, then 'out'; 'end' last."""
    i, a, prog = 0, 0, []
    for byte in _u(s):
        front, hit = [(a, "")], None
        for depth in range(200):
            hit = next((f for f in front if f[0] % 256 == byte), None)
            if hit:
                break
            j, nxt, seen = i + depth, [], set()
            ops = [(op, 33 + (op - j - 33) % 94) for op in (68, 39, 62)]
            for v, run in front:
                for op, ch in ops:
                    w = v if op == 68 else ch % 3 * 19683 + ch // 3 if op == 39 else _mb_crazy(v, ch)
                    if w not in seen:
                        seen.add(w)
                        nxt.append((w, run + chr(ch)))
            front = nxt
        if not hit:
            raise ValueError(f"no Malbolge run for byte {byte}")
        a, i = hit[0], i + len(hit[1])
        prog.append(hit[1] + chr(33 + (5 - i - 33) % 94))
        i += 1
    return "".join(prog) + chr(33 + (81 - i - 33) % 94)


CANDIDATES.append(("malbolge", malbolge_enc, malbolge_dec))
SPECULATIVE_FREE += (("malbolge", malbolge_free),)


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
