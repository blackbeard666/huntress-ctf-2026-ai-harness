"""Identity fields (any file): filename, size, digests, leading magic bytes, BOMs. COPIED from the GM-verified D1/D2/D3
solvers via D10 (challenges/day10/metadata-where-do-we-begin/solver/solve.py) and D11/D12 (member-name filename)."""
import hashlib
import io
import re
import zipfile

from .spell import Hex  # noqa: F401  (re-export for extractor authors)


def members(data, depth=0):
    """(name, bytes) of every non-zip member in archive order, recursing into nested zips (D10)."""
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except (zipfile.BadZipFile, ValueError):
        return []
    out = []
    for i in z.infolist():
        if i.is_dir():
            continue
        try:
            b = z.read(i)
        except Exception:  # noqa: BLE001 - encrypted / broken member: name only
            b = b""
        if depth < 3 and i.filename.lower().endswith(".zip") and b[:2] == b"PK":
            out += members(b, depth + 1)
        else:
            out.append((i.filename, b))
    return out


def filename(data, ctx):
    """'What is the exact filename of ...?': the question's member basename (D11/D12); for a bare container (D1) the
    member whose name carries the answer-id stem, else the note, else the first .txt (D10)."""
    member = ctx.get("member") or ""
    if member:
        return member.replace("\\", "/").split("/")[-1]
    if not data or data[:2] != b"PK":
        return None
    mem = [n for n, _ in members(data)]
    stem = (ctx.get("aid") or "").lower().split(".")[-1].rsplit("-filename", 1)[0]
    for pred in (lambda n: stem and stem in n.lower(), lambda n: "note" in n.lower(), lambda n: n.lower().endswith(".txt")):
        for n in mem:
            if pred(n.rsplit("/", 1)[-1]):
                return n.rsplit("/", 1)[-1]
    return mem[0].rsplit("/", 1)[-1] if mem else None


def size_bytes(data, ctx):
    return None if data is None else len(data)


def md5(data, ctx):
    return None if data is None else hashlib.md5(data).hexdigest()


def sha1(data, ctx):
    return None if data is None else hashlib.sha1(data).hexdigest()


def sha256(data, ctx):
    return None if data is None else hashlib.sha256(data).hexdigest()


_WORDS = {"one": 1, "two": 2, "four": 4, "eight": 8, "twelve": 12, "sixteen": 16, "thirty-two": 32, "sixty-four": 64}


def prefix_len(ctx):
    """N of a magic-prefix field: the id's `-hex-N`, else the question text ('first sixteen bytes') (D2)."""
    if str(ctx.get("param") or "").isdigit():
        return int(ctx["param"])
    q = ctx.get("question") or {}
    text = f"{q.get('question', '')} {(q.get('answer_format') or {}).get('syntax', '')} {ctx.get('aid', '')}".lower()
    m = re.search(r"first\s+(\d+)\s+bytes", text) or re.search(r"prefix-hex-(\d+)", text)
    if m:
        return int(m.group(1))
    m = re.search(r"first\s+([a-z-]+)\s+bytes", text)
    if m and m.group(1) in _WORDS:
        return _WORDS[m.group(1)]
    m = re.search(r"exact\s+(\d+)\s+hex", text)
    return int(m.group(1)) // 2 if m else None


def magic_prefix_hex(data, ctx):
    n = prefix_len(ctx)
    return None if data is None or not n else data[:n].hex()


def utf8_bom_present(data, ctx):
    return None if data is None else data[:3] == b"\xef\xbb\xbf"


def utf16_bom_present(data, ctx):
    return None if data is None else data[:2] in (b"\xff\xfe", b"\xfe\xff")
