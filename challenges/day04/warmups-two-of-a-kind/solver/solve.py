#!/usr/bin/env python3
"""A Little Based: peel encoding layers off a blob until a text line names an answer slug."""
import argparse, time, base64, hashlib, binascii, bz2, codecs, gzip, json, lzma, re, sys, zipfile, zlib, io
from pathlib import Path
from urllib.parse import unquote_to_bytes

SLUG = re.compile(r"\b([a-z]+-[a-z]+-[a-z]+-\d{2})\b")
B64 = re.compile(rb"^[A-Za-z0-9+/=\s]+$")
B64URL = re.compile(rb"^[A-Za-z0-9_\-=\s]+$")
B32 = re.compile(rb"^[A-Z2-7=\s]+$")
HEX = re.compile(rb"^(?:[0-9a-fA-F]{2}[\s:]*)+$")
BIN = re.compile(rb"^[01\s]+$")
# per-line wrapper such as "01\t<payload>" or "line 3: <payload>"
PREFIX = re.compile(rb"(?m)^[ \t]*[\w ]{1,12}?(?:\t|[:|>][ \t]*)(?=\S)")


def log(*a):
    print(*a, file=sys.stderr)


def printable(b):
    try:
        s = b.decode("utf-8")
    except UnicodeDecodeError:
        return None
    ok = sum(c.isprintable() or c in "\r\n\t" for c in s)
    return s if s and ok / len(s) > 0.97 else None


def answer_from(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return None
    m = SLUG.findall(lines[-1])
    return m[-1] if m else None


def candidates(b):
    """Yield (name, decoded bytes) for every plausible single decoding step."""
    s = b.strip()
    for magic, fn in ((b"\x1f\x8b", gzip.decompress), (b"BZh", bz2.decompress),
                      (b"\xfd7zXZ", lzma.decompress), (b"x", zlib.decompress)):
        if s.startswith(magic) or b.startswith(magic):
            try:
                yield magic.hex(), fn(b)
            except Exception:
                pass
    if b.startswith(b"PK\x03\x04"):
        try:
            z = zipfile.ZipFile(io.BytesIO(b))
            yield "zip", b"\n".join(z.read(n) for n in z.namelist())
        except Exception:
            pass
    t0 = printable(b)
    if t0 is not None and len(t0.splitlines()) > 1:
        pl = per_line(t0)
        if pl:
            yield "per-line", pl.encode()
    if PREFIX.search(s):
        yield "strip-prefix", PREFIX.sub(b"", s)
    compact = re.sub(rb"\s+", b"", s)
    if compact and BIN.match(s) and len(compact) % 8 == 0:
        yield "bin", int(compact, 2).to_bytes(len(compact) // 8, "big")
    if compact and HEX.match(s):
        try:
            yield "hex", binascii.unhexlify(re.sub(rb"[\s:]", b"", s))
        except Exception:
            pass
    if compact and B32.match(s) and len(compact) % 8 == 0:
        try:
            yield "b32", base64.b32decode(compact)
        except Exception:
            pass
    if compact and B64.match(s):
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
    t = printable(b)
    if t is not None:
        yield "rev", t[::-1].encode()
        if re.search(r"\d+[ ,]+\d+", t) and re.fullmatch(r"[\d\s,]+", t.strip()):
            try:
                yield "dec", bytes(int(x) for x in re.split(r"[\s,]+", t.strip()))
            except Exception:
                pass
        for n in range(1, 26):
            yield f"rot{n}", codecs.encode(t, "rot13").encode() if n == 13 else bytes(
                (((c - 65 + n) % 26) + 65) if 65 <= c <= 90 else
                (((c - 97 + n) % 26) + 97) if 97 <= c <= 122 else c for c in t.encode())


COMMON = set("""a an and answer are be code decode decoding exact for from game good great here in is it job master
nice of on send solve submit that the this to warmup well with work you your""".split())
NUMBERED = re.compile(r"^[ \t]*(?:\d{1,3}|line ?\d{1,3})(?:\t|[:|>.)] ?)(.*)$", re.I)


def english(t):
    words = re.findall(r"[A-Za-z]{2,}", t)  # single letters: hex runs are full of "a"/"d" false hits
    if not words:
        return 0.0
    hits = sum(w.lower() in COMMON for w in words)
    alpha = sum(c.isalpha() or c in " ,.!?:'-" for c in t) / len(t)
    return hits + alpha


def best_line(frag, depth=3):
    """Best English-looking decoding of one line fragment (each line may use its own encoding chain)."""
    best, seen, frontier = (english(frag), frag), {frag}, [frag.encode()]
    for _ in range(depth):
        nxt = []
        for cur in frontier:
            for name, d in candidates(cur):
                t = printable(d)
                if t is None or t in seen:
                    continue
                seen.add(t)
                nxt.append(d)
                sc = english(t)
                # a rot-N must win by real words: "er: jaunty-..." rot22 -> "an: fwqjpu-..." gains one stray "an"
                if sc > best[0] + (2.0 if name.startswith("rot") else 0.5):
                    best = (sc, t)
        frontier = nxt[:400]
    return best[1]


STRICT_HEX = re.compile(r"(?:[0-9a-fA-F]{2})+")
STRICT_B64 = re.compile(r"[A-Za-z0-9+/]+={0,2}")
STRICT_BIN = re.compile(r"[01]{8}(?:\s+[01]{8})*")


def rot(t, n):
    return "".join(chr((ord(c) - 65 + n) % 26 + 65) if "A" <= c <= "Z" else
                   chr((ord(c) - 97 + n) % 26 + 97) if "a" <= c <= "z" else c for c in t)


def strict_line(frag, depth=4):
    """Fast one-fragment decode: peel strict hex/base64 tokens (recursively); otherwise the best rot-N.
    Fragment whitespace is kept verbatim - lines split mid-sentence and trailing spaces matter."""
    cur = frag
    for _ in range(depth):
        tok, nxt = cur.strip(), None
        if STRICT_BIN.fullmatch(tok):  # space-separated 8-bit groups (checked before hex: "01100101" is hex too)
            nxt = printable(bytes(int(g, 2) for g in tok.split()))
        if nxt is None and STRICT_HEX.fullmatch(tok):
            nxt = printable(bytes.fromhex(tok))
        if nxt is None and len(tok) % 4 == 0 and STRICT_B64.fullmatch(tok):
            try:
                nxt = printable(base64.b64decode(tok, validate=True))
            except Exception:
                pass
        if nxt is None:
            break
        cur = nxt
    if cur == frag:
        best = (english(frag), 0)
        for n in range(1, 26):
            sc = english(rot(frag, n))
            if sc > best[0] + 2.0:
                best = (sc, n)
        cur = rot(frag, best[1])
    return cur


def fast_per_line(data):
    """Numbered per-line mixed encodings (b64 / rot13 / hex per line) joined into one message."""
    t = printable(data)
    if t is None:
        return None
    lines = [l for l in t.splitlines() if l.strip()]
    ms = [NUMBERED.match(l) for l in lines]
    if len(lines) < 2 or not all(ms):
        return None
    joined = "".join(strict_line(m.group(1)) for m in ms)
    return accept(joined.encode())


def per_line(t):
    """Numbered lines ("01<TAB>payload") whose payloads are each encoded differently and form ONE message
    when decoded and concatenated verbatim (fragments split mid-word, leading spaces significant)."""
    lines = [l for l in t.splitlines() if l.strip()]
    if len(lines) < 2:
        return None
    ms = [NUMBERED.match(l) for l in lines]
    frags = [m.group(1) for m in ms] if all(ms) else lines
    dec = [best_line(f) for f in frags]
    if dec == frags:
        return None
    joined = "".join(dec)
    return joined if SLUG.search(joined) else "\n".join(dec)


def accept(data):
    t = printable(data)
    if t is None:
        return None
    a = answer_from(t)
    # require plain-English context so rot-N copies of the final layer don't win
    return a if a and re.search(r"\b(submit|answer|the|is)\b", t, re.I) else None


def expand(data):
    yield from candidates(data)
    if printable(data) is None:  # single-byte XOR only on binary-looking layers
        for k in range(1, 256):
            x = bytes(c ^ k for c in data)
            if printable(x):
                yield f"xor{k:#x}", x


def peel(data, max_nodes=50000, budget=0.6):
    """BFS over decodings; shortest chain whose text's last line names a slug wins."""
    seen, frontier, n = {data}, [(data, ())], 0
    end = time.monotonic() + budget
    while frontier and time.monotonic() < end:
        nxt_frontier = []
        for cur, path in frontier:
            if time.monotonic() > end:
                break
            a = accept(cur)
            if a:
                return a, path
            for name, nxt in expand(cur):
                n += 1
                if nxt and nxt not in seen and n < max_nodes:
                    seen.add(nxt)
                    nxt_frontier.append((nxt, path + (name,)))
        frontier = nxt_frontier
    return None


def zip_members(data, depth=0):
    """Yield (basename, bytes) for every member of a zip (nested zips too), regardless of file extension."""
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
    # GM may hand out a zip bundle under a member's name (e.g. "blob-01.txt" holding blob-01..08.txt):
    # an exact inner member beats an outer same-named file that is really a container
    for f in files:
        for n, m in zip_members(f.read_bytes()):
            if n == name:
                return m
    for f in files:
        if f.name == name:
            return f.read_bytes()
    if sha:  # GM may serve every set under one generic filename; match the contract's sha256 instead
        for f in files:
            for b in [f.read_bytes()] + [m for _, m in zip_members(f.read_bytes())]:
                if hashlib.sha256(b).hexdigest() == sha:
                    return b
    raise FileNotFoundError(name)


def artifact_sha(c, q, idx):
    """sha256 the contract lists for this question's artifact (by name, else by set number / position)."""
    arts = c.get("artifacts") or []
    for a in arts:
        if a.get("filename") == q.get("artifact") and a.get("sha256"):
            return a["sha256"]
    names = {a.get("filename") for a in arts}
    if len(arts) > 1 and len(names) < len(arts):  # duplicated generic names: rely on order
        i = q["set"] - 1 if isinstance(q.get("set"), int) else idx
        if 0 <= i < len(arts):
            return arts[i].get("sha256")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    c = json.loads(Path(a.contract).read_text())
    root = Path(a.artifacts)
    out = {}
    for idx, (aid, q) in enumerate(zip(c["answer_ids"] if "answer_ids" in c else [q["id"] for q in c["questions"]], c["questions"])):
        text = q.get("question", "").lower()
        if not ("decode" in text and ("slug" in text or "blob" in text)):
            log(f"skip {aid}: not a blob-decode question")
            continue
        try:
            data = find_artifact(root, q["artifact"], artifact_sha(c, q, idx))
        except FileNotFoundError:
            log(f"skip {aid}: artifact {q['artifact']} missing")
            continue
        fast = fast_per_line(data)
        r = (fast, ("fast-per-line",)) if fast else peel(data)
        if not r:
            log(f"{aid}: no slug found")
            continue
        slug, path = r
        log(f"{aid}: {'>'.join(path)} -> {slug}")
        out[aid] = slug.strip() if q.get("normalization", "trim") == "trim" else slug
    if not out:
        sys.exit("no answers produced")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
