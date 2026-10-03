#!/usr/bin/env python3
"""A Little Based: peel encoding layers off a blob until a text line names an answer slug."""
import argparse, base64, hashlib, binascii, bz2, codecs, gzip, json, lzma, re, sys, zipfile, zlib, io
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


def peel(data, max_nodes=50000):
    """BFS over decodings; shortest chain whose text's last line names a slug wins."""
    seen, frontier, n = {data}, [(data, ())], 0
    while frontier:
        nxt_frontier = []
        for cur, path in frontier:
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


def find_artifact(root, name, sha=None):
    p = root / name
    if p.is_file():
        return p.read_bytes()
    for f in root.rglob("*"):
        if f.is_file() and f.name == name:
            return f.read_bytes()
    for f in root.rglob("*.zip"):
        with zipfile.ZipFile(f) as z:
            for n in z.namelist():
                if Path(n).name == name:
                    return z.read(n)
    if sha:  # GM may serve every set under one generic filename; match the contract's sha256 instead
        for f in root.rglob("*"):
            if f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest() == sha:
                return f.read_bytes()
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
        r = peel(data)
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
