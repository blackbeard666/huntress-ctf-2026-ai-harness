#!/usr/bin/env python3
"""BOM Voyage: text-encoding facts (text.<field>) of the named archive member, derived from its raw bytes."""
import argparse, codecs, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from lib.common import load_contract, find_artifact_hinted, normalize
from lib.knowledge import BOOL

BOMS = {
    "utf8": codecs.BOM_UTF8,
    "utf16le": codecs.BOM_UTF16_LE,
    "utf16be": codecs.BOM_UTF16_BE,
    "utf32le": codecs.BOM_UTF32_LE,
    "utf32be": codecs.BOM_UTF32_BE,
}


def log(*a):
    print(*a, file=sys.stderr)


def field_of(q, aid):
    """The 'text.<field>' named in the question, else the answer-id suffix after '-text-'."""
    m = re.search(r"\btext\.([a-z0-9_]+)", q.get("question", ""), re.I)
    if m:
        return m.group(1).lower()
    m = re.search(r"-text-([a-z0-9-]+)$", aid.split(".")[-1])
    return m.group(1).replace("-", "_") if m else None


def answer(field, data):
    m = re.fullmatch(r"(utf\d+(?:le|be)?)_bom_present", field)
    if m and m.group(1) in BOMS:
        bom = BOMS[m.group(1)]
        # a UTF-16LE BOM is a prefix of the UTF-32LE BOM; don't report it for a UTF-32LE file
        if m.group(1) == "utf16le" and data.startswith(codecs.BOM_UTF32_LE):
            return BOOL[False]
        return BOOL[data.startswith(bom)]
    if field == "bom_present":
        return BOOL[any(data.startswith(b) for b in BOMS.values())]
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
            hint = aid.split(".")[-1].split("-text-")[0]
            data, src = find_artifact_hinted(a.artifacts, q["artifact"], hint)
            v = answer(field, data)
        except Exception as e:
            log(f"{aid}: {e}")
            continue
        if v is None:
            log(f"{aid}: unrecognized field text.{field}, skipped")
            continue
        out[aid] = normalize(v, q)
        log(f"{aid}: {src} ({len(data)} bytes, head {data[:4].hex()}) text.{field} -> {out[aid]}")
    if not out:
        sys.exit("no answers produced")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
