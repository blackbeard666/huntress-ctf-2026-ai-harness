#!/usr/bin/env python3
"""Eight Is Enough: octal char codes (possibly layered, or one fragment of numbered per-line mixed encodings)
decode to a message whose final non-empty line names the answer slug."""
import argparse, base64, binascii, bz2, codecs, gzip, hashlib, io, json, lzma, math, re, sys, time, zipfile, zlib
from pathlib import Path
from urllib.parse import unquote_to_bytes

SLUG = re.compile(r"(?<![A-Za-z0-9-])([a-z]+-[a-z]+-[a-z]+-\d{2})(?![A-Za-z0-9-])")
NUMBERED = re.compile(r"^[ \t]*(?:\d{1,3}|line ?\d{1,3})(?:\t|[:|>.)] ?)(.*)$", re.I)
SEP = re.compile(r"[\s,;]+")
OCT_TOK = re.compile(r"(?:\\|0o|0)?([0-7]{1,3})")
DEC_TOK = re.compile(r"\d{1,3}")
BIN_TOK = re.compile(r"[01]{8}")
STRICT_B64 = re.compile(r"[A-Za-z0-9+/]+={0,2}")
B32 = re.compile(rb"^[A-Z2-7=\s]+$")
B64URL = re.compile(rb"^[A-Za-z0-9_\-=\s]+$")
COMMON = set("""a an and answer are be code decode decoding exact for from game good great here in is it job master
nice of on send solve submit that the this to warmup well with work you your""".split())


def log(*a):
    print(*a, file=sys.stderr)


def printable(b):
    try:
        s = b.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        return None
    ok = sum(c.isprintable() or c in "\r\n\t" for c in s)
    return s if s and ok / len(s) > 0.97 else None


def english(t):
    words = re.findall(r"[A-Za-z]{2,}", t)
    if not t:
        return 0.0
    hits = sum(w.lower() in COMMON for w in words)
    alpha = sum(c.isalpha() or c in " ,.!?:'-" for c in t) / len(t)
    lower = sum(c.islower() for c in t) / len(t)  # octal-misread decimal codes come out ALL CAPS
    return hits + alpha + lower


# English letter frequencies (%): rot-N choice on short fragments with no common words (e.g. only the slug)
FREQ = dict(zip("abcdefghijklmnopqrstuvwxyz", (8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, 0.15, 0.77, 4.0, 2.4,
                                                 6.7, 7.5, 1.9, 0.095, 6.0, 6.3, 9.1, 2.8, 0.98, 2.4, 0.15, 2.0, 0.074)))


def letter_fit(t):
    words = re.findall(r"[A-Za-z]{2,}", t)
    return 2 * sum(w.lower() in COMMON for w in words) + sum(math.log10(FREQ[c]) for c in t.lower() if c in FREQ)


def rot(t, n):
    return "".join(chr((ord(c) - 65 + n) % 26 + 65) if "A" <= c <= "Z" else
                   chr((ord(c) - 97 + n) % 26 + 97) if "a" <= c <= "z" else c for c in t)


# ---- char-code decoders (the day's concept: base-8 digits; siblings base 2 / 10 / 16) ----

def codes_to_bytes(vals):
    return bytes(vals) if vals and all(0 <= v <= 255 for v in vals) else None


def octal(t):
    """'116 151 ...', '\\116\\151...', '0o116,0o151', or unseparated 3-digit groups -> bytes."""
    s = t.strip()
    if re.fullmatch(r"(?:\\[0-7]{1,3})+", s):
        return codes_to_bytes([int(x, 8) for x in s.split("\\")[1:]])
    toks = [x for x in SEP.split(s) if x]
    if len(toks) == 1 and re.fullmatch(r"[0-7]+", s) and len(s) % 3 == 0 and len(s) > 3:
        toks = [s[i:i + 3] for i in range(0, len(s), 3)]
    ms = [OCT_TOK.fullmatch(x) for x in toks]
    if not toks or not all(ms):
        return None
    return codes_to_bytes([int(m.group(1), 8) for m in ms])


def decimal(t):
    toks = [x for x in SEP.split(t.strip()) if x]
    if not toks or not all(DEC_TOK.fullmatch(x) for x in toks):
        return None
    return codes_to_bytes([int(x) for x in toks])


def binary(t):
    toks = [x for x in SEP.split(t.strip()) if x]
    if toks and all(BIN_TOK.fullmatch(x) for x in toks):
        return bytes(int(x, 2) for x in toks)
    compact = "".join(toks)
    if compact and re.fullmatch(r"[01]+", compact) and len(compact) % 8 == 0 and len(compact) >= 16:
        return int(compact, 2).to_bytes(len(compact) // 8, "big")
    return None


def hexa(t):
    compact = re.sub(r"(?i)[\s:,]|0x|\\x", "", t)
    if compact and len(compact) % 2 == 0 and re.fullmatch(r"[0-9a-fA-F]+", compact):
        return binascii.unhexlify(compact)
    return None


def numeric_choice(t):
    """Octal vs decimal codes can both parse ('101 110 ...'): keep the more English-looking printable one.
    Zero-padded tokens ('040') are an octal tell; short unpadded tokens ('32') a decimal tell."""
    toks = [x for x in SEP.split(t.strip()) if x]
    opts = []
    for name, fn in (("oct", octal), ("dec", decimal)):
        b = fn(t)
        s = printable(b) if b else None
        if s is None:
            continue
        hint = 0.0
        if name == "oct" and any(len(x) == 3 and x[0] == "0" for x in toks):
            hint = 1.5
        if name == "dec" and any(len(x) < 3 and x[0] != "0" for x in toks):
            hint = 1.5
        opts.append((english(s) + hint, name, s))
    return max(opts)[1:] if opts else None


# ---- numbered per-line mixed encodings (Mastery shape on earlier days) ----

def strict_step(t):
    """One unambiguous decode of a fragment, or None. Order matters: 8-bit binary is also octal/decimal/hex digits."""
    s = t.strip()
    if not s:
        return None
    b = binary(s)
    if b is not None and printable(b):
        return "bin", printable(b)
    nc = numeric_choice(s)
    if nc:
        return nc
    b = hexa(s)
    if b is not None and printable(b):
        return "hex", printable(b)
    if STRICT_B64.fullmatch(s) and len(s) >= 4:
        try:
            out = printable(base64.b64decode(s + "=" * (-len(s) % 4), validate=True))
            if out:
                return "b64", out
        except (binascii.Error, ValueError):
            pass
    return None


def decode_fragment(frag, depth=4, rot13_prior=False):
    """Decode one fragment; whitespace of plain/rot fragments is kept verbatim (lines split mid-word).
    rot13_prior: in GM numbered blobs every fragment is encoded and the letter cipher is rot13, so a short
    slug-only fragment ('el-abegu-dhvyy-64') whose letter statistics are a near-tie still gets rot13."""
    cur, steps = frag, []
    for _ in range(depth):
        r = strict_step(cur)
        if r is None:
            break
        steps.append(r[0])
        cur = r[1]
    if not steps:
        base, best = letter_fit(frag), (0.0, 0)
        for n in range(1, 26):
            gain = letter_fit(rot(frag, n)) - base + (2.0 if rot13_prior and n == 13 else 0.0)
            if gain >= 1.0 and gain > best[0]:  # plain text keeps a small edge over a near-tie shift
                best = (gain, n)
        if best[1]:
            steps.append(f"rot{best[1]}")
            cur = rot(frag, best[1])
    return cur, steps


def per_line(data):
    t = printable(data)
    if t is None:
        return None
    lines = [l for l in t.splitlines() if l.strip()]
    ms = [NUMBERED.match(l) for l in lines]
    if not lines or (len(lines) < 2 and not all(ms)):  # one numbered line ("01<TAB>payload") still counts
        return None
    frags = [m.group(1) for m in ms] if all(ms) else lines
    dec = [decode_fragment(f, rot13_prior=all(ms)) for f in frags]
    if all(not s for _, s in dec):
        return None
    texts = [d for d, _ in dec]
    log("  per-line:", " | ".join("+".join(s) or "plain" for _, s in dec))
    joined = "".join(texts)
    return joined if (all(ms) or SLUG.search(joined)) else "\n".join(texts)


# ---- whole-blob BFS over layers ----

def candidates(b):
    s = b.strip()
    for magic, fn in ((b"\x1f\x8b", gzip.decompress), (b"BZh", bz2.decompress),
                      (b"\xfd7zXZ", lzma.decompress), (b"x", zlib.decompress)):
        if s.startswith(magic):
            try:
                yield magic.hex(), fn(s)
            except Exception:
                pass
    if s.startswith(b"PK\x03\x04"):
        try:
            z = zipfile.ZipFile(io.BytesIO(s))
            yield "zip", b"\n".join(z.read(n) for n in z.namelist())
        except Exception:
            pass
    t = printable(b)
    if t is None:
        for k in range(1, 256):
            x = bytes(c ^ k for c in b)
            if printable(x):
                yield f"xor{k:#x}", x
        return
    if len(t.strip().splitlines()) > 1:
        pl = per_line(b)
        if pl:
            yield "per-line", pl.encode()
    for name, fn in (("bin", binary), ("oct", octal), ("dec", decimal), ("hex", hexa)):
        try:
            out = fn(t)
        except Exception:
            out = None
        if out:
            yield name, out
    compact = re.sub(rb"\s+", b"", s)
    if compact and B32.match(s) and len(compact) % 8 == 0:
        try:
            yield "b32", base64.b32decode(compact)
        except Exception:
            pass
    if compact and STRICT_B64.fullmatch(compact.decode("latin-1")):
        try:
            yield "b64", base64.b64decode(compact + b"=" * (-len(compact) % 4), validate=True)
        except Exception:
            pass
    if compact and B64URL.match(s):
        try:
            yield "b64url", base64.urlsafe_b64decode(compact + b"=" * (-len(compact) % 4))
        except Exception:
            pass
    for name, fn in (("b85", base64.b85decode), ("a85", base64.a85decode)):
        try:
            yield name, fn(compact)
        except Exception:
            pass
    if b"%" in s:
        yield "url", unquote_to_bytes(s)
    yield "rev", t[::-1].encode()
    for n in range(1, 26):
        yield f"rot{n}", (codecs.encode(t, "rot13") if n == 13 else rot(t, n)).encode()


def accept(data):
    t = printable(data)
    if t is None:
        return None
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    m = SLUG.findall(lines[-1]) if lines else []
    # require plain-English context so rot-N copies of the final layer don't win
    return m[-1] if m and re.search(r"\b(submit|answer|the|is)\b", t, re.I) else None


def peel(data, budget=3.0, max_nodes=60000):
    """BFS; at the first depth with accepted outputs, keep the most English-looking one."""
    seen, frontier, n = {data}, [(data, ())], 0
    end = time.monotonic() + budget
    while frontier and time.monotonic() < end:
        hits = [(english(printable(cur)), accept(cur), path) for cur, path in frontier if accept(cur)]
        if hits:
            _, slug, path = max(hits, key=lambda h: h[0])
            return slug, path
        nxt = []
        for cur, path in frontier:
            if time.monotonic() > end:
                break
            for name, out in candidates(cur):
                n += 1
                if out and out not in seen and n < max_nodes:
                    seen.add(out)
                    nxt.append((out, path + (name,)))
        frontier = nxt
    return None


# ---- artifact lookup ----

def zip_members(data, depth=0):
    if depth > 3 or not data.startswith(b"PK\x03\x04"):
        return
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        for n in z.namelist():
            if n.endswith("/"):
                continue
            m = z.read(n)
            yield Path(n).name, m
            yield from zip_members(m, depth + 1)
    except Exception:
        pass


def find_artifact(root, name, sha=None):
    files = [f for f in sorted(root.rglob("*")) if f.is_file()]
    # a Mastery bundle can be served under one set's name (blob-01.txt = zip of blob-01..NN.txt): inner member wins
    for f in files:
        for n, m in zip_members(f.read_bytes()):
            if n == name:
                return m
    for f in files:
        if f.name == name:
            return f.read_bytes()
    if sha:
        for f in files:
            for b in [f.read_bytes()] + [m for _, m in zip_members(f.read_bytes())]:
                if hashlib.sha256(b).hexdigest() == sha:
                    return b
    raise FileNotFoundError(name)


def artifact_sha(c, q, idx):
    arts = c.get("artifacts") or []
    for a in arts:
        if a.get("filename") == q.get("artifact") and a.get("sha256"):
            return a["sha256"]
    if len(arts) > 1 and len({a.get("filename") for a in arts}) < len(arts):
        i = q["set"] - 1 if isinstance(q.get("set"), int) else idx
        if 0 <= i < len(arts):
            return arts[i].get("sha256")
    if not arts and c.get("sha256") and len(c.get("questions", [])) == 1:
        return c["sha256"]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    c = json.loads(Path(a.contract).read_text())
    root = Path(a.artifacts)
    qs = c.get("questions", [])
    ids = c.get("answer_ids") or [q.get("id") for q in qs]
    out = {}
    for idx, (aid, q) in enumerate(zip(ids, qs)):
        text = q.get("question", "").lower()
        if not ("decode" in text and ("slug" in text or "blob" in text)):
            log(f"skip {aid}: not a blob-decode question")
            continue
        try:
            data = find_artifact(root, q["artifact"], artifact_sha(c, q, idx))
        except (FileNotFoundError, KeyError):
            log(f"skip {aid}: artifact {q.get('artifact')} missing")
            continue
        pl = per_line(data)
        slug = accept(pl.encode()) if pl else None
        r = (slug, ("per-line",)) if slug else peel(data)
        if not r:
            log(f"{aid}: no slug found")
            continue
        slug, path = r
        log(f"{aid}: {'>'.join(path)} -> {slug}")
        out[aid] = slug.strip() if q.get("normalization", "trim") in ("trim", "exact", None) else slug
    if not out:
        sys.exit("no answers produced")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
