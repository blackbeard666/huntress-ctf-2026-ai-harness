#!/usr/bin/env python3
"""Solver for this challenge -- harness skeleton. Fill in `answer()`; keep the I/O contract unchanged.

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess to 7z/jadx/etc., all sets well under 1 s. Mastery questions name
their files like 'delivery 2: sample_02.apk' or 'evidence.zip -> member': `artifact_bytes()` resolves both (by sha256
pairing first, so same-named per-set deliveries never get mixed up)."""
import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib.decode import decode_chunk, decode_chunked  # noqa: E402
from lib.common import container_by_sha, delivery_missing, find_artifact, load_contract, normalize  # noqa: E402

_cache = {}


def artifact_bytes(root, contract, artifact):
    """Bytes for a question's `artifact` string (cached per artifact)."""
    if artifact in _cache:
        return _cache[artifact]
    container, _, member = (x.strip() for x in artifact.partition("->"))
    data = None
    p = container_by_sha(root, contract, container)
    if p is not None and not member:
        data = p.read_bytes()
    elif not delivery_missing(root, contract, container):
        for cand in (artifact, container.split(": ", 1)[-1] + (f" -> {member}" if member else "")):
            try:
                data = find_artifact(root, cand)
                break
            except FileNotFoundError:
                continue
    _cache[artifact] = data
    return data


_ENT = re.compile(r"^(?:\s*&#(?:\d+|[xX][0-9a-fA-F]+);)+\s*$|^(?:&#?\w+;)+$")
_SLUG = re.compile(r"[a-z]+-[a-z]+-[a-z]+-\d{2}")


def _line(p):
    """One fragment: HTML numeric/named entities (day 8), else the lib's per-format chunk decoder."""
    if _ENT.match(p):
        return html.unescape(p)
    return decode_chunk(p)


def _decode(text):
    lines = text.split("\n")
    rows = [re.match(r"^(\d+)\t(.*)$", ln.rstrip("\r")) for ln in lines if ln.strip()]
    if rows and all(rows):
        rows = sorted(((int(m.group(1)), m.group(2)) for m in rows))
        return "".join(_line(p) for _, p in rows)
    if "&#" in text or re.search(r"&\w+;", text):
        return html.unescape(text.strip())
    return decode_chunk(text.strip())


def _slug(text):
    if not text:
        return None
    for ln in reversed([x for x in text.splitlines() if x.strip()]):
        hits = _SLUG.findall(ln)
        if hits:
            return hits[-1]
    return None


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    if data is None:
        return None
    return _slug(_decode(data.decode("utf-8", "replace")))


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing (None or an exception): a cheap generic second try for a variant shape
    the direct parse doesn't know (Time Trial / Mastery mutate the task) -- e.g. the lane lib's name-agnostic decoder
    over `data`, then a match against question["answer_format"]. None = give up on this field only."""
    if data is None:
        return None
    t = data.decode("utf-8", "replace")
    try:
        v = _slug(decode_chunked(t))
    except Exception:  # noqa: BLE001
        v = None
    return v or _slug(html.unescape(t))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    contract, pairs = load_contract(a.contract)
    out = {}
    for aid, q in pairs:
        data = artifact_bytes(a.artifacts, contract, q.get("artifact") or "")
        try:
            v = answer(aid, q, data, contract)
        except Exception as e:  # noqa: BLE001 - one bad field must not sink the other answers
            print(f"{aid}: {e!r}", file=sys.stderr)
            v = None
        if v is None:
            try:
                v = fallback(aid, q, data, contract)
            except Exception as e:  # noqa: BLE001
                print(f"{aid}: fallback {e!r}", file=sys.stderr)
        if v is not None:
            out[aid] = normalize(v, q)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
