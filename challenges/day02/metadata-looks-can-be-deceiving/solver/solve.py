#!/usr/bin/env python3
"""Looks Can Be Deceiving: report the leading magic bytes (first N bytes as hex) of the named archive member."""
import argparse, hashlib, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from lib.common import load_contract, find_artifact_hinted, normalize

WORDS = {"one": 1, "two": 2, "four": 4, "eight": 8, "twelve": 12, "sixteen": 16, "thirty-two": 32, "sixty-four": 64}


def log(*a):
    print(*a, file=sys.stderr)


def prefix_len(q, aid):
    text = f"{q.get('question', '')} {q.get('answer_format', {}).get('syntax', '')} {aid}".lower()
    m = re.search(r"first\s+(\d+)\s+bytes", text) or re.search(r"prefix-hex-(\d+)", text)
    if m:
        return int(m.group(1))
    m = re.search(r"first\s+([a-z-]+)\s+bytes", text)
    if m and m.group(1) in WORDS:
        return WORDS[m.group(1)]
    m = re.search(r"exact\s+(\d+)\s+hex", text)
    if m:
        return int(m.group(1)) // 2
    return None


def answer(q, aid, data):
    slug = aid.split(".")[-1]
    text = q.get("question", "").lower()
    if "magic" in slug or ("first" in text and "bytes" in text and "hex" in text):
        n = prefix_len(q, aid)
        if not n:
            raise ValueError(f"cannot determine prefix length for {aid}")
        return data[:n].hex()
    if "sha256" in slug or "sha-256" in text:
        return hashlib.sha256(data).hexdigest()
    if "sha1" in slug or "sha-1" in text:
        return hashlib.sha1(data).hexdigest()
    if "md5" in slug or "md5" in text:
        return hashlib.md5(data).hexdigest()
    if "size" in slug or "size" in text:
        return str(len(data))
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
        try:
            # hint = answer-id stem before the question-kind suffix; used only if the named member is absent
            hint = re.split(r"-(?:magic|sha256|sha1|md5|size)\b", aid.split(".")[-1])[0]
            data, src = find_artifact_hinted(a.artifacts, q["artifact"], hint)
            v = answer(q, aid, data)
        except Exception as e:
            log(f"{aid}: {e}")
            continue
        if v is None:
            log(f"{aid}: unrecognized question, skipped")
            continue
        out[aid] = normalize(v, q)
        log(f"{aid}: {src} ({len(data)} bytes) -> {out[aid]}")
    if not out:
        sys.exit("no answers produced")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
