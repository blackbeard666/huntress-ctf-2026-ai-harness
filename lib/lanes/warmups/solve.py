#!/usr/bin/env python3
"""Lane-level, day-independent WARMUPS solver (prototype, zero LLM).

    warmups_lane.py --contract <contract.json> --artifacts <dir>  ->  {answer_id: value}

Model of the lane (days 1-6): every question is "decode the blob; the final non-empty decoded line tells you the
slug to submit"; answer_format.syntax describes the slug. Variants seen: one whole-blob encoding (b64, rot13, hex,
8-bit binary, decimal, octal), layered encodings, octal escapes / unseparated digits, and the Mastery shape:
numbered lines "NN<TAB>chunk" where EACH chunk carries its own encoding and chunks split mid-word.

Strategy (no day knowledge): answer regex from answer_format -> BFS over a transform set (every radix 2/8/10/16,
base32/58/64/85, url, html, qp, rev, rot13/atbash, xor, gzip/zlib/bz2/xz/zip, numbered-chunk join) with
acceptance = the regex matches on the final non-empty line of a readable text; ties broken by an English score
(best rot-N is also tried at acceptance). Numbered chunks: per-chunk candidate lists (strict decoders, 2 levels
deep, then rot-N) + a small beam over the joined text. Hard time budget per blob.
"""
import argparse
import base64
import binascii
import bz2
import codecs
import gzip
import hashlib
import html
import io
import json
import lzma
import math
import quopri
import re
import sys
import time
import zipfile
import zlib
from pathlib import Path
from urllib.parse import unquote_to_bytes

BUDGET = 1.0          # seconds per blob (typical blob < 5 ms)
TOTAL_BUDGET = 3.0    # seconds per contract: a 28-set Mastery must still answer inside a ~6-7 s window
COMMON = set("""a an and answer are be code decode decoded decoding exact final for from game good great here in is
it job line master message nice of on please send slug solve submit that the this to warmup well with work you
your""".split())
FREQ = dict(zip("abcdefghijklmnopqrstuvwxyz", (8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, 0.15, 0.77, 4.0, 2.4,
                                                 6.7, 7.5, 1.9, 0.095, 6.0, 6.3, 9.1, 2.8, 0.98, 2.4, 0.15, 2.0, 0.074)))
NUMW = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8}


def log(*a):
    print(*a, file=sys.stderr)


# ------------------------------------------------------------------ answer regex from answer_format
def answer_regex(q):
    fmt = q.get("answer_format") or {}
    syn = (fmt.get("syntax") or fmt.get("description") or "").lower()
    if fmt.get("regex"):
        try:
            return re.compile(fmt["regex"])
        except re.error:
            pass
    m = re.search(r"(\w+) lowercase words? separated by hyphens", syn)
    if m:
        n = NUMW.get(m.group(1), int(m.group(1)) if m.group(1).isdigit() else None)
        d = re.search(r"(\w+)-digit number", syn)
        nd = NUMW.get(d.group(1), int(d.group(1)) if d and d.group(1).isdigit() else None) if d else None
        words = rf"[a-z]+(?:-[a-z]+){{{n - 1}}}" if n else r"[a-z]+(?:-[a-z]+)*"
        tail = (rf"-\d{{{nd}}}" if nd else r"-\d+") if d else ""
        return re.compile(rf"(?<![A-Za-z0-9-]){words}{tail}(?![A-Za-z0-9-])")
    m = re.search(r"([a-z0-9]+)- followed by exactly (\d+) (upper|lower)?\w* ?hex", syn)
    if m:
        hx = "0-9A-F" if m.group(3) == "upper" else ("0-9a-f" if m.group(3) == "lower" else "0-9A-Fa-f")
        return re.compile(rf"{re.escape(m.group(1).upper())}-[{hx}]{{{m.group(2)}}}")
    return re.compile(r"(?<![A-Za-z0-9-])[a-z]+(?:-[a-z]+){1,5}-\d{1,4}(?![A-Za-z0-9-])")  # generic slug


# ------------------------------------------------------------------ text scoring
def text_of(b):
    """Readable text or None (ASCII printable + whitespace, tolerate a little UTF-8)."""
    if not b:
        return None
    try:
        s = b.decode("utf-8")
    except UnicodeDecodeError:
        return None
    ok = sum(c.isprintable() or c in "\r\n\t" for c in s)
    return s if ok / len(s) > 0.97 else None


def english(t):
    if not t:
        return -99.0
    words = re.findall(r"[A-Za-z]{2,}", t)
    hits = sum(w.lower() in COMMON for w in words)
    letters = [c for c in t.lower() if c in FREQ]
    fit = sum(math.log10(FREQ[c]) for c in letters) / max(len(letters), 1)  # ~ -1.2 English, -1.6+ random
    shape = sum(c.isalpha() or c in " ,.!?:;'-\n" for c in t) / len(t)
    return 3 * hits / max(len(words), 1) + 2 * shape + 2 * (fit + 1.6) + 0.3 * min(hits, 6)


def rot(t, n):
    return "".join(chr((ord(c) - 65 + n) % 26 + 65) if "A" <= c <= "Z" else
                   chr((ord(c) - 97 + n) % 26 + 97) if "a" <= c <= "z" else c for c in t)


def atbash(t):
    return "".join(chr(155 - ord(c)) if "A" <= c <= "Z" else chr(219 - ord(c)) if "a" <= c <= "z" else c for c in t)


def rot47(t):
    return "".join(chr(33 + (ord(c) - 33 + 47) % 94) if 33 <= ord(c) <= 126 else c for c in t)


# Known plaintext the GM has used on every warmup so far (crib). Used ONLY to recover a key (Vigenere / repeating
# XOR); the answer itself still has to come out of the decoded bytes and match answer_format.
CRIBS = ["Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "]


def _period(seq, maxp=32):
    for p in range(1, min(maxp, len(seq) // 2) + 1):
        if all(seq[i] == seq[i % p] for i in range(len(seq))):
            return seq[:p]
    return None


def vigenere_crib(t):
    """Recover a Vigenere key from the crib (key advancing per letter, or per character); None if no short key."""
    for crib in CRIBS:
        if len(t) < len(crib):
            continue
        # mode A: key index advances on letters only
        letters = [c for c in t if c.isalpha()]
        cl = [c for c in crib if c.isalpha()]
        key = _period([(ord(a.lower()) - ord(b.lower())) % 26 for a, b in zip(letters, cl)])
        if key and any(key):
            out, i = [], 0
            for c in t:
                if c.isalpha():
                    base = 65 if c.isupper() else 97
                    out.append(chr((ord(c) - base - key[i % len(key)]) % 26 + base))
                    i += 1
                else:
                    out.append(c)
            return "".join(out)
        # mode B: key index advances on every character (non-letters consume a key slot)
        sh = {i: (ord(a.lower()) - ord(b.lower())) % 26 for i, (a, b) in enumerate(zip(t, crib)) if b.isalpha()}
        for p in range(1, 33):
            slots = {}
            if all(slots.setdefault(i % p, v) == v for i, v in sh.items()) and len(slots) == p and any(slots.values()):
                return "".join(chr((ord(c) - (65 if c.isupper() else 97) - slots[i % p]) % 26 + (65 if c.isupper() else 97))
                               if c.isalpha() else c for i, c in enumerate(t))
    return None


def xor_crib(b):
    for crib in CRIBS:
        cb = crib.encode()
        if len(b) < len(cb):
            continue
        key = _period([x ^ y for x, y in zip(b, cb)])
        if key and len(key) > 1:
            return bytes(c ^ key[i % len(key)] for i, c in enumerate(b))
    return None


MORSE = {v: k for k, v in {"a": ".-", "b": "-...", "c": "-.-.", "d": "-..", "e": ".", "f": "..-.", "g": "--.",
         "h": "....", "i": "..", "j": ".---", "k": "-.-", "l": ".-..", "m": "--", "n": "-.", "o": "---", "p": ".--.",
         "q": "--.-", "r": ".-.", "s": "...", "t": "-", "u": "..-", "v": "...-", "w": ".--", "x": "-..-", "y": "-.--",
         "z": "--..", "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-", "5": ".....",
         "6": "-....", "7": "--...", "8": "---..", "9": "----.", "-": "-....-", ":": "---...", "!": "-.-.--",
         ",": "--..--", ".": ".-.-.-"}.items()}


def d_morse(t):
    s = t.strip()
    if not s or not re.fullmatch(r"[.\-/ |\n!,:0-9a-z]+", s) or s.count(".") + s.count("-") < len(s) / 2:
        return None
    words = re.split(r"\s*[/|]\s*|\s{3,}", s)
    return " ".join("".join(MORSE.get(sym, sym) for sym in w.split()) for w in words).encode()


# ------------------------------------------------------------------ strict radix / base decoders
SEP = re.compile(r"[\s,;]+")


def codes(vals):
    return bytes(vals) if vals and all(0 <= v <= 255 for v in vals) else None


def d_bin(t):
    toks = [x for x in SEP.split(t.strip()) if x]
    if toks and all(re.fullmatch(r"[01]{7,8}", x) for x in toks):
        return bytes(int(x, 2) for x in toks)
    c = "".join(toks)
    if len(c) >= 16 and len(c) % 8 == 0 and re.fullmatch(r"[01]+", c):
        return int(c, 2).to_bytes(len(c) // 8, "big")
    return None


def d_oct(t):
    s = t.strip()
    if re.fullmatch(r"(?:\\[0-7]{1,3})+", s):
        return codes([int(x, 8) for x in s.split("\\")[1:]])
    toks = [x for x in SEP.split(s) if x]
    if len(toks) == 1 and re.fullmatch(r"[0-7]+", s) and len(s) % 3 == 0 and len(s) > 3:
        toks = [s[i:i + 3] for i in range(0, len(s), 3)]
    ms = [re.fullmatch(r"(?:\\|0o|0)?([0-7]{1,3})", x) for x in toks]
    return codes([int(m.group(1), 8) for m in ms]) if toks and all(ms) else None


def d_dec(t):
    toks = [x for x in SEP.split(t.strip()) if x]
    if toks and all(re.fullmatch(r"&#?\d{1,3};?|\d{1,3}", x) for x in toks):
        return codes([int(re.sub(r"\D", "", x)) for x in toks])
    return None


def d_hex(t):
    c = re.sub(r"(?i)[\s:,]|0x|\\x|%", "", t)
    if c and len(c) % 2 == 0 and re.fullmatch(r"[0-9a-fA-F]+", c):
        return binascii.unhexlify(c)
    return None


def d_b64(t):
    c = re.sub(r"\s+", "", t)
    if len(c) >= 4 and re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", c):
        try:
            return base64.b64decode(c + "=" * (-len(c) % 4), validate=True)
        except (binascii.Error, ValueError):
            return None
    if len(c) >= 4 and re.fullmatch(r"[A-Za-z0-9_-]+={0,2}", c):
        try:
            return base64.urlsafe_b64decode(c + "=" * (-len(c) % 4))
        except (binascii.Error, ValueError):
            return None
    return None


def d_b32(t):
    c = re.sub(r"\s+", "", t).upper()
    if len(c) >= 8 and re.fullmatch(r"[A-Z2-7]+=*", c):
        try:
            return base64.b32decode(c + "=" * (-len(c) % 8))
        except (binascii.Error, ValueError):
            return None
    return None


B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def d_b58(t):
    c = t.strip()
    if len(c) < 6 or not all(ch in B58 for ch in c):
        return None
    n = 0
    for ch in c:
        n = n * 58 + B58.index(ch)
    out = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return b"\0" * (len(c) - len(c.lstrip("1"))) + out


def d_b85(t):
    c = re.sub(r"\s+", "", t)
    for fn in (base64.b85decode, base64.a85decode):
        try:
            return fn(c[2:-2] if c.startswith("<~") else c)
        except Exception:  # noqa: BLE001
            continue
    return None


STRICT = (("bin", d_bin), ("oct", d_oct), ("dec", d_dec), ("hex", d_hex), ("b32", d_b32), ("b64", d_b64),
          ("b58", d_b58), ("b85", d_b85))


# ------------------------------------------------------------------ numbered / per-line chunks
NUMBERED = re.compile(r"^[ \t]*(?:line ?)?(\d{1,4})(?:\t|[:|>.)\]] ?| - )(.*)$", re.I)


def chunk_options(frag, depth=2):
    """[(decoded_text, score)] for one chunk, best first. Strict decoders (up to `depth` nested) then rot-N."""
    out = []
    frontier = [(frag, 0)]
    for lvl in range(depth):
        nxt = []
        for cur, _ in frontier:
            s = cur.strip()
            if not s:
                continue
            for name, fn in STRICT:
                try:
                    b = fn(s)
                except Exception:  # noqa: BLE001
                    b = None
                t = text_of(b) if b else None
                if t is not None and t != cur:
                    nxt.append((t, lvl + 1))
        out += nxt
        frontier = nxt
    if re.search(r"[A-Za-z]", frag):
        for n in range(26):
            out.append((rot(frag, n), 0.3 if n == 13 else (0.0 if n == 0 else -0.2)))
        out.append((atbash(frag), -0.2))
    scored = {}
    for t, bonus in out:
        sc = english(t) + bonus - (0 if t is frag else 0)
        if t not in scored or sc > scored[t]:
            scored[t] = sc
    return sorted(scored.items(), key=lambda kv: -kv[1])


def strict_options(frag, depth=2):
    """[(decoded_text, score)] from strict decoders only (radix/base, nested up to `depth`), best first."""
    out, frontier = {}, [frag]
    for _ in range(depth):
        nxt = []
        for cur in frontier:
            s = cur.strip()
            for name, fn in STRICT:
                try:
                    b = fn(s) if s else None
                except Exception:  # noqa: BLE001
                    b = None
                t = text_of(b) if b else None
                if t is not None and t != cur and t not in out:
                    out[t] = english(t)
                    nxt.append(t)
        frontier = nxt
    return sorted(out.items(), key=lambda kv: -kv[1])


def join_chunks(text, rx, beam=6):
    """Numbered-line text -> joined decoding whose final line matches rx (or the best guess, or None).
    Chunks with a readable strict decoding use it; the remaining letter chunks share ONE Caesar shift (or atbash),
    chosen on their concatenation (a slug-only chunk alone is too short to pick a shift reliably)."""
    lines = [l for l in text.splitlines() if l.strip()]
    ms = [NUMBERED.match(l) for l in lines]
    if not lines or not all(ms):
        return None
    rows = sorted(((int(m.group(1)), m.group(2)) for m in ms), key=lambda r: r[0])
    strict = [strict_options(p) for _, p in rows]
    letter = [i for i, (o, (_, p)) in enumerate(zip(strict, rows)) if (not o or o[0][1] < 1.0) and re.search("[A-Za-z]", p)]
    ciphers = ([(f"rot{n}", (lambda t, n=n: rot(t, n))) for n in range(26)] + [("atbash", atbash), ("rot47", rot47),
               ("rev", lambda t: t[::-1])])
    blob = " ".join(rows[i][1] for i in letter)
    ranked = sorted(ciphers, key=lambda c: -(english(c[1](blob)) + (0.05 if c[0] == "rot13" else 0))) if letter else ciphers[:1]
    for cname, fn in ranked[:3]:
        parts = [fn(p) if i in letter else (strict[i][0][0] if strict[i] else p) for i, (_, p) in enumerate(rows)]
        j = "".join(parts)
        if final_match(j, rx):
            return j
    # beam fallback over per-chunk alternatives
    opts = []
    for i, (_, p) in enumerate(rows):
        o = list(strict[i][:3])
        if re.search("[A-Za-z]", p):
            o += sorted(((fn(p), english(fn(p))) for _, fn in ciphers), key=lambda x: -x[1])[:4]
        opts.append(o or [(p, 0.0)])
    states = [("", 0.0)]
    for o in opts:
        states = sorted(((s + t, sc + c) for s, sc in states for t, c in o), key=lambda x: -x[1])[:beam]
    for s, _ in states:
        if final_match(s, rx):
            return s
    return states[0][0]


# ------------------------------------------------------------------ BFS over whole-blob layers
def final_match(t, rx):
    lines = [l for l in t.splitlines() if l.strip()]
    if not lines:
        return None
    m = rx.findall(lines[-1])
    return m[-1] if m else None


def transforms(b):
    s = b.strip()
    for magic, fn in ((b"\x1f\x8b", gzip.decompress), (b"BZh", bz2.decompress), (b"\xfd7zXZ", lzma.decompress),
                      (b"x", zlib.decompress)):
        if s.startswith(magic):
            try:
                yield "z", fn(s)
            except Exception:  # noqa: BLE001
                pass
    if s.startswith(b"PK\x03\x04"):
        try:
            z = zipfile.ZipFile(io.BytesIO(s))
            yield "zip", b"\n".join(z.read(n) for n in z.namelist() if not n.endswith("/"))
        except Exception:  # noqa: BLE001
            pass
    t = text_of(b)
    if t is None:
        for k in range(1, 256):
            x = bytes(c ^ k for c in b)
            if text_of(x):
                yield f"xor{k:#x}", x
        x = xor_crib(b)
        if x:
            yield "xor-crib", x
        return
    if NUMBERED.match(t.strip().splitlines()[0]):
        j = join_chunks(t, transforms.rx)
        if j:
            yield "chunks", j.encode()
        rows = [NUMBERED.match(l) for l in t.splitlines() if l.strip()]
        if all(rows):  # same encoding split over numbered lines: strip the index, join raw
            yield "deprefix", "".join(m.group(2) for m in sorted(rows, key=lambda m: int(m.group(1)))).encode()
    for name, fn in STRICT:
        try:
            out = fn(t)
        except Exception:  # noqa: BLE001
            out = None
        if out:
            yield name, out
    if "%" in t:
        yield "url", unquote_to_bytes(t.strip())
    if "&#" in t or "&x" in t:
        yield "html", html.unescape(t).encode()
    if "=" in t and re.search(r"=[0-9A-F]{2}", t):
        yield "qp", quopri.decodestring(b)
    yield "rev", t[::-1].encode()
    yield "rot13", codecs.encode(t, "rot13").encode()
    yield "atbash", atbash(t).encode()
    yield "rot47", rot47(t).encode()
    v = vigenere_crib(t)
    if v:
        yield "vigenere-crib", v.encode()
    m = d_morse(t)
    if m:
        yield "morse", m
    if t.lstrip().startswith("begin "):
        try:
            yield "uu", codecs.decode(b, "uu")
        except Exception:  # noqa: BLE001
            pass
    # each non-empty line on its own (unnumbered per-line mixed encodings)
    lines = [l for l in t.splitlines() if l.strip()]
    if 1 < len(lines) <= 64:
        parts = [(chunk_options(l) or [(l, 0)])[0][0] for l in lines]
        yield "lines", "\n".join(parts).encode()
        yield "lines-joined", "".join(parts).encode()


def accept(b, rx):
    """(score, slug, text) if b is readable text whose final line carries the answer; also tries best rot-N."""
    t = text_of(b)
    if t is None:
        return None
    lines = [l for l in t.splitlines() if l.strip()]
    if lines and all(NUMBERED.match(l) for l in lines):
        return None  # a numbered chunk container is not "decoded completely"
    best = None
    toks = t.split()
    wordy = sum(len(x) <= 16 and sum(ch.isalpha() or ch in ",.!?:'-" for ch in x) >= 0.8 * len(x) for x in toks)
    shifts = (t,) + (tuple(rot(t, n) for n in range(1, 26)) + (atbash(t),) if toks and wordy / len(toks) > 0.8 else ())
    for cand in shifts:
        slug = final_match(cand, rx)
        if slug:
            sc = english(cand)
            nhits = sum(w.lower() in COMMON for w in re.findall(r"[A-Za-z]{2,}", cand))
            if best is None or sc > best[0]:
                best = (sc, slug, cand, nhits)
    return best


def solve_blob(data, rx, budget=BUDGET):
    transforms.rx = rx
    end = time.monotonic() + budget
    seen, frontier = {data}, [(data, ())]
    fallback = None
    depth = 0
    while frontier and time.monotonic() < end and depth <= 8:
        hits = []
        for cur, path in frontier:
            a = accept(cur, rx)
            if a:
                hits.append((a[0], a[1], path, a[3]))
        good = [h[:3] for h in hits if h[0] >= 2.5 and h[3] >= 2]  # readable English context around the slug
        if good:
            sc, slug, path = max(good, key=lambda h: h[0])
            return slug, path, sc
        if hits and fallback is None:
            fallback = max(hits, key=lambda h: h[0])[:3]
        nxt = []
        for cur, path in frontier:
            if time.monotonic() > end:
                break
            for name, out in transforms(cur):
                if out and out not in seen and len(out) < 4_000_000:
                    seen.add(out)
                    nxt.append((out, path + (name,)))
        frontier = nxt
        depth += 1
    if fallback:
        return fallback[1], fallback[2], fallback[0]
    return None


# ------------------------------------------------------------------ artifact lookup
def zip_members(data, depth=0):
    if depth > 3 or not data.startswith(b"PK\x03\x04"):
        return
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except Exception:  # noqa: BLE001
        return
    for n in z.namelist():
        if n.endswith("/"):
            continue
        try:
            m = z.read(n)
        except Exception:  # noqa: BLE001
            continue
        yield Path(n).name, m
        yield from zip_members(m, depth + 1)


SKIP = {"manifest.json", "contract.json", "result.json", "expected.json"}


def all_blobs(root):
    files = [f for f in sorted(Path(root).rglob("*")) if f.is_file() and f.name not in SKIP]
    out = []
    for f in files:
        b = f.read_bytes()
        out.append((f.name, b, None))
        out += [(n, m, f.name) for n, m in zip_members(b)]
    return out


def find_blob(c, q, idx, blobs):
    name = q.get("artifact") or ""
    bare = re.sub(r"^delivery \d+:\s*", "", name)
    for n, b, parent in blobs:          # zip member wins (bundle served under one set's name)
        if parent and n in (name, bare):
            return b
    for n, b, parent in blobs:
        if not parent and n == name:
            return b
    arts = c.get("artifacts") or []
    want = None
    for a in arts:
        if a.get("filename") == name and a.get("sha256"):
            want = a["sha256"]
    if want is None and arts:
        i = q["set"] - 1 if isinstance(q.get("set"), int) else idx
        if 0 <= i < len(arts):
            want = arts[i].get("sha256")
    if want is None and c.get("sha256") and len(c.get("questions") or []) == 1:
        want = c["sha256"]
    if want:
        for n, b, _ in blobs:
            if hashlib.sha256(b).hexdigest() == want:
                return b
    tops = [b for n, b, p in blobs if not p]
    if len(tops) == 1 and not tops[0].startswith(b"PK"):
        return tops[0]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    c = json.loads(Path(a.contract).read_text())
    qs = c.get("questions") or []
    ids = c.get("answer_ids") or [q.get("id") for q in qs]
    blobs = all_blobs(a.artifacts)
    out = {}
    end = time.monotonic() + TOTAL_BUDGET
    for idx, (aid, q) in enumerate(zip(ids, qs)):
        b = find_blob(c, q, idx, blobs)
        if b is None:
            log(f"{aid}: artifact {q.get('artifact')!r} not found")
            continue
        left = max(0.05, (end - time.monotonic()) / max(1, len(ids) - idx))
        r = solve_blob(b, answer_regex(q), budget=min(BUDGET, left))
        if not r:
            log(f"{aid}: no answer")
            continue
        slug, path, sc = r
        log(f"{aid}: {'>'.join(path) or 'plain'} -> {slug} (score {sc:.1f})")
        out[aid] = slug.strip()
    if not out:
        sys.exit("no answers produced")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
