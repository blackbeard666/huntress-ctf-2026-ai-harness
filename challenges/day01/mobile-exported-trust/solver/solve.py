#!/usr/bin/env python3
"""Exported Trust (mobile-android, Day 01) solver.

Concept: the handed-out APK is an exported deep-link Activity that posts an embedded
credential to a (narrative) backend. The real evidence code lives in an embedded asset,
assets/huntress_puzzle.json: {"schema":...,"codec":"<codec>","data":"<encoded ANS code>"}.
Decode `data` per `codec` to get the ANS- + 16 hex evidence code.

Variants change: APK file name, package suffix, case reference, and (potentially) the
puzzle codec. So we derive everything from the APK bytes, decode per codec, and fall back
to scanning for the ANS- pattern.
"""
import argparse, base64, binascii, bz2, codecs, gzip, io, json, lzma, os, re, sys, zipfile, zlib

ANS_RE = re.compile(rb"ANS-[0-9A-Fa-f]{16}")


def log(*a):
    print(*a, file=sys.stderr)


def strip_artifact_name(name):
    # "delivery 1: exported_trust_mastery_01.apk" -> "exported_trust_mastery_01.apk"
    name = name.strip()
    m = re.match(r"(?:delivery\s*\d+\s*:\s*)(.+)", name, re.I)
    return (m.group(1) if m else name).strip()


def _all_files(adir):
    return [os.path.join(r, f) for r, _, fs in os.walk(adir) for f in fs]


def _apk_mentions(path, needle):
    """True if the APK's manifest/dex (UTF-8 or UTF-16LE) contains `needle`."""
    try:
        with zipfile.ZipFile(path) as z:
            blob = b"".join(z.read(n) for n in z.namelist()
                            if n.endswith((".xml", ".dex", ".json", ".arsc")))
    except Exception:
        with open(path, "rb") as f:
            blob = f.read()
    return needle.encode() in blob or needle.encode("utf-16le") in blob


def find_artifact(adir, raw_name, question=""):
    """Resolve a question's artifact. The on-disk name may keep or drop the
    Mastery "delivery N: " prefix, so try both, then suffix/case-insensitive
    matches, then disambiguate multiple APKs by the package named in the question."""
    raw_name = (raw_name or "").strip()
    name = strip_artifact_name(raw_name)
    files = _all_files(adir)
    for want in (raw_name, name):
        if not want:
            continue
        for p in files:
            if os.path.basename(p) == want:
                return p
    if name:
        for p in files:  # e.g. "delivery 1: x.apk" on disk vs "x.apk" asked, or case drift
            b = os.path.basename(p).lower()
            if b == name.lower() or strip_artifact_name(b) == name.lower() or b.endswith(name.lower()):
                return p
    apks = [p for p in files if p.lower().endswith(".apk") or zipfile.is_zipfile(p)]
    if len(apks) == 1:
        log(f"[!] {raw_name} not found, using {apks[0]}")
        return apks[0]
    m = re.search(r"package\s+([A-Za-z0-9_.]+[A-Za-z0-9_])", question or "")
    if m:
        hits = [p for p in apks if _apk_mentions(p, m.group(1))]
        if len(hits) == 1:
            log(f"[!] {raw_name} matched by package {m.group(1)}: {hits[0]}")
            return hits[0]
    return None


def read_puzzle(apk_path):
    """Return the parsed huntress_puzzle.json dict from inside the APK, if present."""
    with zipfile.ZipFile(apk_path) as z:
        cand = [n for n in z.namelist() if n.lower().endswith("huntress_puzzle.json")]
        if not cand:
            cand = [n for n in z.namelist() if n.lower().endswith(".json") and "puzzle" in n.lower()]
        for n in cand:
            try:
                return json.loads(z.read(n).decode("utf-8", "replace"))
            except ValueError:
                continue
    return None


def _try(fn):
    try:
        return fn()
    except Exception:
        return None


def decode_codec(data, codec):
    """Decode a string `data` per a named `codec`. Returns bytes or None."""
    if data is None:
        return None
    raw = data.encode() if isinstance(data, str) else data
    c = (codec or "plain").strip().lower().replace("-", "").replace("_", "")
    table = {
        "plain": lambda: raw,
        "none": lambda: raw,
        "utf8": lambda: raw,
        "ascii": lambda: raw,
        "base64": lambda: base64.b64decode(raw + b"=" * (-len(raw) % 4)),
        "b64": lambda: base64.b64decode(raw + b"=" * (-len(raw) % 4)),
        "base64url": lambda: base64.urlsafe_b64decode(raw + b"=" * (-len(raw) % 4)),
        "base32": lambda: base64.b32decode(raw + b"=" * (-len(raw) % 8)),
        "b32": lambda: base64.b32decode(raw + b"=" * (-len(raw) % 8)),
        "base85": lambda: base64.b85decode(raw),
        "b85": lambda: base64.b85decode(raw),
        "ascii85": lambda: base64.a85decode(raw),
        "a85": lambda: base64.a85decode(raw),
        "hex": lambda: binascii.unhexlify(re.sub(rb"\s+", b"", raw)),
        "base16": lambda: binascii.unhexlify(re.sub(rb"\s+", b"", raw)),
        "rot13": lambda: codecs.decode(data, "rot13").encode(),
        "reverse": lambda: raw[::-1],
        "reversed": lambda: raw[::-1],
        "gzip": lambda: gzip.decompress(binascii.unhexlify(raw)) if not raw.startswith(b"\x1f\x8b") else gzip.decompress(raw),
        "zlib": lambda: zlib.decompress(raw),
        "bz2": lambda: bz2.decompress(raw),
        "lzma": lambda: lzma.decompress(raw),
        "xz": lambda: lzma.decompress(raw),
    }
    fn = table.get(c)
    if fn:
        out = _try(fn)
        if out is not None:
            return out
    # fall back: try every decoder and keep whatever yields an ANS code
    for fn in table.values():
        out = _try(fn)
        if out and ANS_RE.search(out):
            return out
    return raw


def evidence_code(apk_path):
    puzzle = read_puzzle(apk_path)
    decoded = None
    if puzzle is not None:
        decoded = decode_codec(puzzle.get("data"), puzzle.get("codec"))
    # Pull the ANS- pattern out of the decoded bytes (handles nested/plain alike)
    if decoded is not None:
        m = ANS_RE.search(decoded if isinstance(decoded, bytes) else str(decoded).encode())
        if m:
            v = m.group().decode()
            return "ANS-" + v[4:].upper()
    # last resort: scan the whole APK for an ANS- literal
    with open(apk_path, "rb") as f:
        m = ANS_RE.search(f.read())
    if m:
        v = m.group().decode()
        return "ANS-" + v[4:].upper()
    return None


def normalize(val, norm):
    norm = (norm or "").lower()
    if "trim" in norm:
        val = val.strip()
    if "lower" in norm and "case" in norm:
        val = val.lower()
    return val


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    args = ap.parse_args()
    contract = json.load(open(args.contract))
    out = {}
    ids = contract.get("answer_ids") or [q["id"] for q in contract["questions"]]
    qs = contract["questions"]
    for aid, q in zip(ids, qs):
        text = (q.get("question", "") + " " + q.get("prompt", "")).lower()
        if "evidence" not in text and "exported" not in text and "deep-link" not in text:
            continue  # not our concept; let another solver handle it
        apk = find_artifact(args.artifacts, q.get("artifact", ""), q.get("question", ""))
        if not apk:
            log(f"[!] no artifact for {aid} ({q.get('artifact')})")
            continue
        code = evidence_code(apk)
        if not code:
            log(f"[!] no ANS code derived for {aid} from {apk}")
            continue
        out[aid] = normalize(code, q.get("normalization"))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
