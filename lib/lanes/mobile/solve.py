#!/usr/bin/env python3
"""Lane-level, day-independent MOBILE solver (prototype, zero LLM).

    mobile_lane.py --contract <contract.json> --artifacts <dir> [--deep]  ->  {answer_id: value}

Lane model (days 1-6): each question names one APK; the answer ("ANS-" + 16 hex, per answer_format) is carried by
assets/huntress_puzzle.json as {codec, data[, key | parts, order]} with codec in plain/reverse/base64/xor/split/hex.
Strategy: answer regex from answer_format -> every JSON asset in the APK -> decode it CODEC-AGNOSTICALLY (named codec
first, then every codec x key x assembly, then the warmups lane peel on the data) -> any candidate that fully matches
the regex. Fallbacks: regex scan of every zip entry (plain + embedded base64/hex strings), then (--deep) lib.android's
apktool/jadx scan. Mastery: one APK per set, paired by name / 'delivery N:' / sha256 / set index.
"""
import argparse
import base64
import binascii
import codecs
import hashlib
import importlib.util
import itertools
import json
import re
import sys
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path("/home/testpwn/huntress-2026")


def log(*a):
    print(*a, file=sys.stderr)


def _warmups():
    spec = importlib.util.spec_from_file_location("warmups_lane", HERE.parent / "warmups" / "solve.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


WL = _warmups()


def answer_regex(q):
    rx = WL.answer_regex(q)
    if "ANS" not in rx.pattern:   # generic fallback for this lane
        syn = ((q.get("answer_format") or {}).get("syntax") or "").lower()
        if "ans-" in syn or not syn:
            return re.compile(r"ANS-[0-9A-F]{16}")
    return rx


# ------------------------------------------------------------------ codec-agnostic puzzle decode
def key_variants(key):
    out = []
    if key is None:
        return [b"\x00"]
    if isinstance(key, int) or (isinstance(key, str) and re.fullmatch(r"\d+", key)):
        out.append(bytes([int(key) & 0xFF]))
    if isinstance(key, str):
        out.append(key.encode())
        for fn in (bytes.fromhex, base64.b64decode):
            try:
                k = fn(key)
                if k:
                    out.append(k)
            except (ValueError, binascii.Error):
                pass
    return out or [b"\x00"]


def raw_forms(data):
    """data string -> candidate byte payloads (as-is, base64, hex, base32)."""
    s = str(data)
    out = [s.encode()]
    for fn in (lambda x: base64.b64decode(x, validate=True), bytes.fromhex, base64.b32decode,
               lambda x: base64.urlsafe_b64decode(x + "=" * (-len(x) % 4))):
        try:
            b = fn(s.strip())
            if b:
                out.append(b)
        except (ValueError, binascii.Error):
            pass
    return out


def assemblies(parts, order):
    parts = [str(p) for p in parts]
    n = len(parts)
    outs = []
    if order and sorted(int(o) for o in order) == list(range(n)):
        o = [int(x) for x in order]
        slots = [None] * n
        for i, pos in enumerate(o):
            slots[pos] = parts[i]
        outs += ["".join(slots), "".join(parts[x] for x in o)]
    outs += ["".join(parts), "".join(reversed(parts))]
    if n <= 6:
        outs += ["".join(p) for p in itertools.permutations(parts)]
    return outs


def rc4(key, data):
    S, j, out = list(range(256)), 0, bytearray()
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    for c in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(c ^ S[(S[i] + S[j]) % 256])
    return bytes(out)


def xor_crib_ans(b, prefix=b"ANS-", alphabet=b"0123456789ABCDEF", maxlen=8):
    """Repeating-XOR key recovery with no key given: the answer starts with `prefix` and the rest is `alphabet`."""
    n = len(b)
    if n != len(prefix) + 16:
        return []
    outs = []
    for L in range(1, maxlen + 1):
        key = []
        for r in range(L):
            idx = range(r, n, L)
            fixed = {b[i] ^ prefix[i] for i in idx if i < len(prefix)}
            opts = fixed if fixed else set(range(256))
            opts = [k for k in opts if all((b[i] ^ k) in (prefix[i:i + 1] if i < len(prefix) else alphabet) for i in idx)]
            if len(opts) != 1:
                break
            key.append(opts[0])
        else:
            outs.append(bytes(c ^ key[i % L] for i, c in enumerate(b)))
            break
    return outs


def decode_puzzle(p, rx):
    """[(priority, value, how)] candidates that fully match rx."""
    found = []

    def take(text, how, pr):
        if isinstance(text, bytes):
            try:
                text = text.decode("utf-8")
            except UnicodeDecodeError:
                return
        for m in rx.findall(text or ""):
            found.append((pr, m, how))

    codec = str(p.get("codec") or "").lower()
    data = p.get("data", p.get("payload", p.get("value", "")))
    keys = key_variants(p.get("key"))
    # assemblies (split / parts) -- try named order first; each assembly is itself peeled below
    texts = []
    if p.get("parts"):
        texts += [(t, f"parts[{i}]") for i, t in enumerate(assemblies(p["parts"], p.get("order")))]
    if data not in (None, ""):
        texts.append((str(data), "data"))
    for pr_base, (t, src) in enumerate(texts):
        pr = 0 if pr_base == 0 else 1
        take(t, f"{src}:plain", pr)
        take(t[::-1], f"{src}:reverse", pr)
        take(codecs.decode(t, "rot13"), f"{src}:rot13", pr + 1)
        for b in raw_forms(t)[1:]:
            take(b, f"{src}:base", pr)
            take(b[::-1], f"{src}:base+rev", pr + 1)
        for b in raw_forms(t):
            for k in keys + ([bytes([i]) for i in range(1, 256)] if codec == "xor" and not p.get("key") else []):
                x = bytes(c ^ k[i % len(k)] for i, c in enumerate(b))
                take(x, f"{src}:xor{k.hex()}", pr + (0 if codec == "xor" else 1))
        for b in raw_forms(t)[1:]:
            for k in keys:
                take(rc4(k, b), f"{src}:rc4", pr + (0 if codec == "rc4" else 2))
            for x in xor_crib_ans(b):
                take(x, f"{src}:xor-crib", pr + 2)
        if not found:  # unknown layering: the warmups-lane peel with the answer regex as acceptance
            r = WL.solve_blob(t.encode(), rx, budget=0.3)
            if r:
                found.append((pr + 2, r[0], f"{src}:peel:{'>'.join(r[1])}"))
    return found


# ------------------------------------------------------------------ APK scan
def scan_apk(apk_bytes, rx, deep=False, apk_path=None):
    cands = []
    try:
        z = zipfile.ZipFile(__import__("io").BytesIO(apk_bytes))
    except zipfile.BadZipFile:
        return cands
    names = z.namelist()
    jsons = sorted((n for n in names if n.lower().endswith(".json")), key=lambda n: (Path(n).name != "huntress_puzzle.json", "puzzle" not in n))
    for n in jsons:
        try:
            p = json.loads(z.read(n))
        except (ValueError, RuntimeError):
            continue
        objs = p if isinstance(p, list) else [p]
        for o in objs:
            if isinstance(o, dict):
                cands += [(pr, v, f"{n}:{how}") for pr, v, how in decode_puzzle(o, rx)]
        if cands:   # the canonical puzzle file wins; other JSON assets are only consulted if it yields nothing
            return cands
    # fallback: literal / embedded-encoded tokens anywhere in the APK (dex strings, resources, assets)
    brx = re.compile(rx.pattern.encode())
    for n in names:
        try:
            d = z.read(n)
        except RuntimeError:
            continue
        cands += [(5, m.decode(), f"{n}:literal") for m in brx.findall(d)]
        cands += [(5, m, f"{n}:utf16") for m in rx.findall(d.decode("utf-16-le", "ignore"))]
        for tok in re.findall(rb"[A-Za-z0-9+/]{24,}={0,2}|[0-9a-fA-F]{40,}", d):
            for b in raw_forms(tok.decode()):
                cands += [(6, m.decode(), f"{n}:embedded") for m in brx.findall(b)]
    if not cands and deep and apk_path:
        sys.path.insert(0, str(ROOT))
        from lib.android import decompiled_scan  # apktool/jadx: seconds, not ms
        cands += [(7, v, "decompiled") for v in decompiled_scan(apk_path) if rx.fullmatch(v)]
    return cands


# ------------------------------------------------------------------ artifact pairing
SKIP = {"manifest.json", "contract.json", "result.json", "expected.json"}


def find_apk(c, q, idx, files):
    name = q.get("artifact") or ""
    bare = re.sub(r"^delivery \d+:\s*", "", name)
    for f in files:
        if f.name in (name, bare):
            return f
    arts = c.get("artifacts") or []
    want = next((a.get("sha256") for a in arts if a.get("filename") in (name, bare) and a.get("sha256")), None)
    if want is None and arts:
        i = q["set"] - 1 if isinstance(q.get("set"), int) else idx
        if 0 <= i < len(arts):
            want = arts[i].get("sha256")
    if want is None and c.get("sha256") and len(c.get("questions") or []) == 1:
        want = c["sha256"]
    if want:
        for f in files:
            if hashlib.sha256(f.read_bytes()).hexdigest() == want:
                return f
    m = re.search(r"(\d+)\.apk$", bare)   # ..._mastery_02.apk <-> 'delivery 2: ..._mastery_02.apk'
    if m:
        for f in files:
            if f.name.endswith(f"{m.group(1)}.apk") and Path(re.sub(r"^delivery \d+:\s*", "", f.name)).name == bare:
                return f
    apks = [f for f in files if f.suffix.lower() == ".apk"]
    return apks[0] if len(apks) == 1 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    ap.add_argument("--deep", action="store_true", help="allow apktool/jadx fallback (slow)")
    a = ap.parse_args()
    c = json.loads(Path(a.contract).read_text())
    qs = c.get("questions") or []
    ids = c.get("answer_ids") or [q.get("id") for q in qs]
    files = [f for f in sorted(Path(a.artifacts).rglob("*")) if f.is_file() and f.name not in SKIP]
    out = {}
    for idx, (aid, q) in enumerate(zip(ids, qs)):
        f = find_apk(c, q, idx, files)
        if f is None:
            log(f"{aid}: apk for {q.get('artifact')!r} not found")
            continue
        t0 = time.time()
        cands = scan_apk(f.read_bytes(), answer_regex(q), a.deep, f)
        if not cands:
            log(f"{aid}: no candidate in {f.name}")
            continue
        cands.sort(key=lambda x: x[0])
        best = cands[0]
        distinct = sorted({v for pr, v, _ in cands if pr == best[0]})
        log(f"{aid}: {best[1]} via {best[2]} ({len(distinct)} distinct at top priority, {time.time() - t0:.3f}s)")
        if len(distinct) > 1:
            log(f"  ambiguous: {distinct[:5]}")
        out[aid] = best[1]
    if not out:
        sys.exit("no answers produced")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
