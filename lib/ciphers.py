"""Classical / keyed cipher helpers for the warmups lane (and any crypto-flavoured puzzle).

The warmups peeler (lib/decode.py) handles *encodings* well but had near-zero *cipher* capability — only
single-byte XOR. This adds the families the hardening audit flagged: repeating-key (Vigenère-class) XOR with
keylength search, Vigenère/Caesar/Atbash, Morse, base58, quoted-printable — plus an english_score cracker so
keyed ciphers can be broken without the key. Pure stdlib. Decoders are tolerant; crackers return ranked guesses.
"""
import binascii
import re
import string
from collections import Counter

_ENGLISH_FREQ = {  # relative letter frequency, for scoring candidate plaintexts
    'e': 12.7, 't': 9.1, 'a': 8.2, 'o': 7.5, 'i': 7.0, 'n': 6.7, 's': 6.3, 'h': 6.1, 'r': 6.0, 'd': 4.3,
    'l': 4.0, 'c': 2.8, 'u': 2.8, 'm': 2.4, 'w': 2.4, 'f': 2.2, 'g': 2.0, 'y': 2.0, 'p': 1.9, 'b': 1.5,
    'v': 1.0, 'k': 0.8, 'j': 0.15, 'x': 0.15, 'q': 0.10, 'z': 0.07,
}


def english_score(text):
    """Higher = more English-like. Combines printable ratio, letter-frequency correlation and space rate.
    Use to rank cracker candidates; not a hard accept (the warmup `accept` predicate still decides)."""
    if not text:
        return -1e9
    s = text.lower()
    n = len(s)
    printable = sum(c in string.printable for c in text) / n
    if printable < 0.9:
        return -1e9
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return printable
    freq = Counter(letters)
    corr = sum(_ENGLISH_FREQ.get(c, 0) * (freq.get(c, 0) / len(letters)) for c in _ENGLISH_FREQ)
    spaces = s.count(" ") / n
    return printable + corr / 10 + (0.5 if 0.05 < spaces < 0.25 else 0)


# --- Caesar / Atbash / Vigenère ------------------------------------------------------------------
def caesar(text, shift):
    out = []
    for c in text:
        if c.isupper():
            out.append(chr((ord(c) - 65 + shift) % 26 + 65))
        elif c.islower():
            out.append(chr((ord(c) - 97 + shift) % 26 + 97))
        else:
            out.append(c)
    return "".join(out)


def caesar_all(text):
    """All 26 Caesar shifts, ranked by english_score. Returns [(shift, text, score), ...]."""
    out = [(s, caesar(text, -s), 0) for s in range(26)]
    return sorted(((s, t, english_score(t)) for s, t, _ in out), key=lambda r: -r[2])


def atbash(text):
    f = lambda c, a: chr(a + 25 - (ord(c) - a))  # noqa: E731
    return "".join(f(c, 65) if c.isupper() else f(c, 97) if c.islower() else c for c in text)


def vigenere_decrypt(text, key):
    key = [k for k in key.lower() if k.isalpha()]
    if not key:
        return text
    out, j = [], 0
    for c in text:
        if c.isalpha():
            a = 65 if c.isupper() else 97
            out.append(chr((ord(c) - a - (ord(key[j % len(key)]) - 97)) % 26 + a))
            j += 1
        else:
            out.append(c)
    return "".join(out)


def vigenere_crack(text, max_keylen=16):
    """Break a Vigenère cipher without the key: find key length by index-of-coincidence, then solve each
    column as a Caesar by letter frequency. Returns [(key, plaintext, score), ...] best first."""
    letters = [c.lower() for c in text if c.isalpha()]
    if len(letters) < 20:
        return []

    def ioc(seq):
        n = len(seq)
        if n < 2:
            return 0
        f = Counter(seq)
        return sum(v * (v - 1) for v in f.values()) / (n * (n - 1))

    best_len, best_ioc = 1, 0
    for klen in range(1, min(max_keylen, len(letters) // 2) + 1):
        avg = sum(ioc(letters[i::klen]) for i in range(klen)) / klen
        if avg > best_ioc:
            best_ioc, best_len = avg, klen
    results = []
    for klen in {best_len, max(1, best_len // 2)}:  # try the top length and a sub-multiple
        key = []
        for i in range(klen):
            col = letters[i::klen]
            best_shift = max(range(26), key=lambda sh: sum(
                _ENGLISH_FREQ.get(chr((ord(c) - 97 - sh) % 26 + 97), 0) for c in col))
            key.append(chr(best_shift + 97))
        k = "".join(key)
        pt = vigenere_decrypt(text, k)
        results.append((k, pt, english_score(pt)))
    return sorted(results, key=lambda r: -r[2])


# --- XOR (single + repeating key) ----------------------------------------------------------------
def repeating_key_xor(data, key):
    if isinstance(key, str):
        key = key.encode()
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def xor_crack(data, max_keylen=40):
    """Break repeating-key XOR: keylength by normalised Hamming distance, each key byte by english_score of
    its column. Returns [(key_bytes, plaintext, score), ...] best first (plaintext as latin-1 str)."""
    if len(data) < 4:
        return []

    def hamming(a, b):
        return sum(bin(x ^ y).count("1") for x, y in zip(a, b))

    sizes = []
    for ks in range(1, min(max_keylen, len(data) // 2) + 1):
        nb = min(len(data) // ks, 12)  # average normalised Hamming over many adjacent blocks for a clean signal
        if nb < 2:
            continue
        blocks = [data[i * ks:(i + 1) * ks] for i in range(nb)]
        pairs = [(blocks[i], blocks[i + 1]) for i in range(nb - 1)]
        d = sum(hamming(a, b) for a, b in pairs) / (len(pairs) * ks)
        sizes.append((d, ks))
    sizes.sort()
    def _col_score(cb):  # English columns are mostly letters+spaces; spaces (0x20) are the strongest signal
        s = cb.decode("latin-1")
        return sum(c.isalpha() or c == " " for c in s) + 3 * s.count(" ")

    out = []
    for _, ks in sizes[:4]:
        key = bytes(max(range(256), key=lambda kb: _col_score(bytes(b ^ kb for b in data[i::ks])))
                    for i in range(ks))
        pt = repeating_key_xor(data, key).decode("latin-1")
        out.append((key, pt, english_score(pt)))
    return sorted(out, key=lambda r: -r[2])


# --- Morse / base58 / quoted-printable -----------------------------------------------------------
_MORSE = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E", "..-.": "F", "--.": "G", "....": "H",
    "..": "I", ".---": "J", "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O", ".--.": "P",
    "--.-": "Q", ".-.": "R", "...": "S", "-": "T", "..-": "U", "...-": "V", ".--": "W", "-..-": "X",
    "-.--": "Y", "--..": "Z", "-----": "0", ".----": "1", "..---": "2", "...--": "3", "....-": "4",
    ".....": "5", "-....": "6", "--...": "7", "---..": "8", "----.": "9",
}


def morse_decode(text):
    """Decode Morse (dots/dashes). Accepts `.`/`-` with `/` or multi-space word separators."""
    text = text.replace("/", " / ")
    words = re.split(r"\s{2,}|\s/\s|/", text.strip())
    out = []
    for w in words:
        out.append("".join(_MORSE.get(sym, "") for sym in w.split()))
    return " ".join(x for x in out if x)


_B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def base58_decode(s):
    s = s.strip()
    num = 0
    for ch in s:
        num = num * 58 + _B58.index(ch)
    full = num.to_bytes((num.bit_length() + 7) // 8, "big")
    pad = len(s) - len(s.lstrip("1"))
    return b"\x00" * pad + full


def quoted_printable_decode(s):
    if isinstance(s, bytes):
        s = s.decode("latin-1")
    s = re.sub(r"=\r?\n", "", s)  # soft line breaks
    return re.sub(r"=([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), s)
