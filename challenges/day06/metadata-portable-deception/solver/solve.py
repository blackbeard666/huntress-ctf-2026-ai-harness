#!/usr/bin/env python3
"""Portable Deception: PDF structure facts (pdf.<field>) of the named archive member, read from the bytes.

A bundle mixes real PDFs, renamed impostors (non-PDF bytes behind a .pdf name) and multiple declared versions (the
`%PDF-x.y` header vs the catalog's /Version override, PDF 32000 7.2.2). GM-confirmed: pdf.header_version is the x.y of
the leading `%PDF-x.y` magic (e.g. 1.4); an impostor has no header -> literal `none` (contract syntax). The other
fields are answered best-effort from the same parse."""
import argparse, json, re, sys, zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from lib.common import load_contract, find_artifact_hinted, normalize
from lib.knowledge import BOOL

HEADER = re.compile(rb"%PDF-(\d+\.\d+)")
LEAD = b"\xef\xbb\xbf\x00\t\n\x0c\r "      # UTF-8 BOM / whitespace a reader skips before the magic
OBJ = re.compile(rb"(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj", re.S)
MAGIC = [(b"%PDF-", "pdf"), (b"\x89PNG\r\n\x1a\n", "png"), (b"\xff\xd8\xff", "jpeg"), (b"GIF8", "gif"),
         (b"PK\x03\x04", "zip"), (b"PK\x05\x06", "zip"), (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "ole"),
         (b"{\\rtf", "rtf"), (b"MZ", "pe"), (b"\x7fELF", "elf"), (b"\x1f\x8b", "gzip"), (b"Rar!", "rar"),
         (b"7z\xbc\xaf\x27\x1c", "7z"), (b"BM", "bmp"), (b"RIFF", "riff"), (b"<?xml", "xml"), (b"<!DOCTYPE html", "html"),
         (b"<html", "html"), (b"%!PS", "postscript")]


def log(*a):
    print(*a, file=sys.stderr)


def header_version(data):
    """x.y of the `%PDF-x.y` magic at the start of the file (after a BOM/whitespace at most), else None.
    A `%PDF-` string deeper in an impostor is a decoy, not its header."""
    m = HEADER.match(data.lstrip(LEAD)[:16])
    return m.group(1).decode() if m else None


def sniff(data):
    head = data.lstrip(LEAD)[:16]
    for magic, kind in MAGIC:
        if head.startswith(magic) or (magic.startswith(b"<") and head.lower().startswith(magic.lower())):
            return kind
    return "text" if data and all(32 <= b < 127 or b in b"\t\r\n" for b in data[:512]) else "unknown"


def _name(raw):
    """Decode a PDF name token body (#xx escapes)."""
    return re.sub(rb"#([0-9A-Fa-f]{2})", lambda m: bytes([int(m.group(1), 16)]), raw).decode("latin-1")


def objects(data):
    """{obj_num: body} with later (incremental-update) definitions overriding earlier ones, plus objects unpacked
    from FlateDecode /ObjStm object streams."""
    objs = {}
    for m in OBJ.finditer(data):
        objs[int(m.group(1))] = m.group(3)
    for body in list(objs.values()):
        if b"/ObjStm" not in body:
            continue
        sm = re.search(rb"stream\r?\n(.*?)\r?\n?endstream", body, re.S)
        n = re.search(rb"/N\s+(\d+)", body)
        first = re.search(rb"/First\s+(\d+)", body)
        if not (sm and n and first):
            continue
        try:
            raw = zlib.decompress(sm.group(1)) if b"/FlateDecode" in body else sm.group(1)
        except zlib.error:
            continue
        nums = list(map(int, raw[:int(first.group(1))].split()))
        pairs = list(zip(nums[0::2], nums[1::2]))[:int(n.group(1))]
        base = int(first.group(1))
        for i, (num, off) in enumerate(pairs):
            end = base + pairs[i + 1][1] if i + 1 < len(pairs) else len(raw)
            objs.setdefault(num, raw[base + off:end])
    return objs


def catalog(data, objs):
    """Body of the document catalog: the last trailer's (or xref stream's) /Root, else any /Type /Catalog object."""
    roots = re.findall(rb"/Root\s+(\d+)\s+\d+\s+R", data)
    if roots and int(roots[-1]) in objs:
        return objs[int(roots[-1])]
    for body in objs.values():
        if re.search(rb"/Type\s*/Catalog\b", body):
            return body
    return None


def catalog_version(cat):
    m = re.search(rb"/Version\s*/([^\s/<>\[\]()]+)", cat or b"")
    return _name(m.group(1)) if m else None


def _vkey(v):
    return tuple(int(x) for x in v.split(".")) if v and re.fullmatch(r"\d+\.\d+", v) else (-1,)


def info(data, objs, key):
    refs = re.findall(rb"/Info\s+(\d+)\s+\d+\s+R", data)
    body = objs.get(int(refs[-1])) if refs else None
    m = re.search(rb"/" + key + rb"\s*\(((?:\\.|[^\\)])*)\)", body or b"")
    return m.group(1).decode("latin-1") if m else None


def facts(data):
    objs = objects(data) if header_version(data) else {}
    cat = catalog(data, objs)
    hv, cv = header_version(data), catalog_version(cat)
    return {"header_version": hv, "catalog_version": cv,
            "effective_version": max((v for v in (hv, cv) if v), key=_vkey, default=None),
            "is_pdf": hv is not None, "detected_type": sniff(data), "objs": objs, "catalog": cat}


def field_of(q, aid):
    m = re.search(r"\bpdf\.([a-z0-9_]+)", q.get("question", ""), re.I)
    if m:
        return m.group(1).lower()
    m = re.search(r"-pdf-\d+-pdf-([a-z0-9-]+)$", aid.split(".")[-1])
    return m.group(1).replace("-", "_") if m else None


INFO_KEYS = {"title": b"Title", "author": b"Author", "creator": b"Creator", "producer": b"Producer",
             "subject": b"Subject", "keywords": b"Keywords", "creation_date": b"CreationDate",
             "mod_date": b"ModDate", "modification_date": b"ModDate"}


def answer(field, data):
    f = facts(data)
    none = lambda v: v if v is not None else "none"
    if field in ("header_version", "version_header", "magic_version"):
        return none(f["header_version"])
    if field in ("catalog_version", "declared_version", "root_version", "version_override", "catalog_version_override"):
        return none(f["catalog_version"])
    if field in ("effective_version", "version"):
        return none(f["effective_version"])
    if field in ("is_pdf", "real_pdf", "is_real_pdf", "magic_matches_extension", "extension_matches", "valid_pdf"):
        return BOOL[f["is_pdf"]]
    if field in ("is_impostor", "impostor", "renamed", "extension_mismatch"):
        return BOOL[not f["is_pdf"]]
    if field in ("detected_type", "actual_type", "content_type", "true_type", "magic_type", "detected_format"):
        return f["detected_type"]
    if field in ("versions_conflict", "version_conflict", "version_mismatch"):
        return BOOL[bool(f["catalog_version"]) and f["catalog_version"] != f["header_version"]]
    if field in ("page_count", "pages"):
        return str(len(re.findall(rb"/Type\s*/Page\b", b"".join(f["objs"].values())))) if f["is_pdf"] else "none"
    if field in ("eof_count", "revision_count", "revisions"):
        return str(data.count(b"%%EOF"))
    if field in ("incremental_updates", "incremental_update_count"):
        return str(max(data.count(b"%%EOF") - 1, 0))
    if field in INFO_KEYS:
        return none(info(data, f["objs"], INFO_KEYS[field]))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    _, pairs = load_contract(a.contract)
    out = {}
    for aid, q in pairs:
        if not q or not q.get("artifact"):
            continue
        field = field_of(q, aid)
        if not field:
            continue
        try:
            fm = re.search(r"for\s+(\S+?)\.?$", q.get("question", "").strip())
            hint = fm.group(1) if fm else aid.split(".")[-1].split("-pdf-")[0]
            data, src = find_artifact_hinted(a.artifacts, q["artifact"], hint)
            v = answer(field, data)
        except Exception as e:
            log(f"{aid}: {e}")
            continue
        if v is None:
            log(f"{aid}: unrecognized field pdf.{field}, skipped")
            continue
        out[aid] = normalize(v, q)
        f = facts(data)
        deep = [m.start() for m in HEADER.finditer(data)]
        log(f"{aid}: {src} ({len(data)} bytes) head={data[:8]!r} type={f['detected_type']} "
            f"header={f['header_version']} catalog={f['catalog_version']} effective={f['effective_version']} "
            f"%PDF-@{deep[:4]} eofs={data.count(b'%%EOF')} pdf.{field} -> {out[aid]}")
    if not out:
        sys.exit("no answers produced")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
