#!/usr/bin/env python3
# VENDORED from challenges/day01/scripting-power-play/solver/solve.py: Homebase only receives this solver dir + lib,
# so the Day 2 solver must not import across challenge folders. Re-copy if the Day 1 solver gets a fix.
"""Power Play: inert PowerShell fixtures inside an AES zip. Each holds a base64 JSON descriptor (IOCs) plus a list of
native .NET types that reveal intent. Classify scenario -> ATT&CK, then pick indicators from the descriptor leaves."""
import argparse, base64, json, re, subprocess, sys, zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from lib.common import load_contract, normalize  # noqa: E402
from lib import knowledge as K  # noqa: E402

PASSWORDS = ["infected", "malware", "huntress", "virus"]
B64LIT = re.compile(r"['\"]([A-Za-z0-9+/]{16,}={0,2})['\"]")
URL = re.compile(r"^https?://\S+$", re.I)
FILENAME = re.compile(r"^[\w .-]+\.[A-Za-z0-9]{1,5}$")
WALLET = re.compile(r"^(?:wallet_\w+|bc1[a-z0-9]{25,62}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|0x[a-fA-F0-9]{40}|4[0-9AB][1-9A-HJ-NP-Za-km-z]{93})$")
MUTEX = re.compile(r"^(?:Global|Local)\\")
NOTE_WORDS = re.compile(r"recover|readme|read_me|decrypt|restore|how_to|note|ransom", re.I)


def log(*a):
    print(*a, file=sys.stderr)


def zips(artdir):
    return [p for p in sorted(Path(artdir).rglob("*")) if p.is_file() and zipfile.is_zipfile(p)]


def read_member(zpath, member):
    with zipfile.ZipFile(zpath) as z:
        hit = next((n for n in z.namelist() if n == member or Path(n).name == member), None)
        if hit is None:
            return None
        info = z.getinfo(hit)
        if not info.flag_bits & 1:
            return z.read(hit)
        if info.compress_type != 99:  # ZipCrypto
            for pw in PASSWORDS:
                try:
                    return z.read(hit, pwd=pw.encode())
                except Exception:
                    pass
    for pw in PASSWORDS:  # AES (method 99): python zipfile can't, 7z can
        r = subprocess.run(["7z", "x", "-so", f"-p{pw}", str(zpath), hit], capture_output=True,
                           stdin=subprocess.DEVNULL, timeout=30)
        if r.returncode == 0 and r.stdout:
            return r.stdout
    return None


def find_member(artdir, artifact):
    arch, _, member = (s.strip() for s in artifact.partition("->"))
    member = member or arch
    cands = zips(artdir)
    # prefer the archive whose saved name starts with the contract's container name
    cands.sort(key=lambda p: not (p.name == arch or p.name.startswith(arch + " ")))
    for z in cands:
        data = read_member(z, member)
        if data is not None:
            log(f"{artifact}: {z.name}")
            return data
    for p in Path(artdir).rglob(member):
        return p.read_bytes()
    raise FileNotFoundError(artifact)


def xor(b, k):
    return bytes(c ^ k[i % len(k)] for i, c in enumerate(b))


def decode_record(text):
    """JSON descriptor from the base64 literal; tolerate a reversing/XOR $reconstruct block in variants."""
    keys = []
    for arr in re.findall(r"@\(\s*((?:0x[0-9a-fA-F]+|\d+)(?:\s*,\s*(?:0x[0-9a-fA-F]+|\d+))*)\s*\)", text):
        keys.append(bytes(int(x, 0) & 0xFF for x in re.split(r"\s*,\s*", arr.strip())))
    keys += [s.encode() for s in re.findall(r"['\"]([^'\"\s]{2,64})['\"]", text)]
    for lit in B64LIT.findall(text):
        try:
            raw = base64.b64decode(lit)
        except Exception:
            continue
        cands = [raw, raw[::-1]]
        for k in keys:
            cands += [xor(raw, k), xor(raw[::-1], k), xor(raw, k)[::-1]]
        cands += [xor(raw, bytes([k])) for k in range(1, 256)]
        for c in cands:
            for enc in ("utf-8", "utf-16-le"):
                try:
                    obj = json.loads(c.decode(enc))
                except Exception:
                    continue
                if isinstance(obj, dict):
                    return obj
    raise ValueError("no JSON descriptor found")


def leaves(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from leaves(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from leaves(v)
    elif isinstance(obj, str):
        yield obj


def scenario(text, vals, member):
    """Intent from native types + descriptor; filename stem only as a tie-breaker."""
    t = text.lower()
    score = {"resource_hijacking": 0, "synthetic_impact": 0, "synthetic_collection": 0}
    if any(WALLET.match(v) for v in vals):
        score["resource_hijacking"] += 3
    if "diagnostics.process" in t or "win32.registry" in t:
        score["resource_hijacking"] += 1
    if any(re.match(r"^\.[\w-]+$", v) for v in vals):
        score["synthetic_impact"] += 1
    if any(NOTE_WORDS.search(v) and FILENAME.match(v) for v in vals):
        score["synthetic_impact"] += 2
    if "cryptography.aes" in t or "directoryinfo" in t:
        score["synthetic_impact"] += 1
    if any(v.lower().endswith(".zip") for v in vals) or "compression.zipfile" in t:
        score["synthetic_collection"] += 2
    if "httpwebrequest" in t:
        score["synthetic_collection"] += 1
    stem = member.lower()
    for s, w in (("resource", "resource_hijacking"), ("impact", "synthetic_impact"), ("collect", "synthetic_collection")):
        if s in stem:
            score[w] += 0.5
    best = max(score, key=score.get)
    log(member, score)
    return best


def analyse(text, member):
    rec = decode_record(text)
    vals = [v for v in leaves(rec)]
    log(member, json.dumps(rec))
    files = [v for v in vals if FILENAME.match(v) and not URL.match(v) and not v.startswith(".")]
    out = {
        "url": next((v for v in vals if URL.match(v)), None),
        "wallet": next((v for v in vals if WALLET.match(v)), None),
        "mutex": next((v for v in vals if MUTEX.match(v)), None),
        "agent": next((v for v in vals if re.match(r"^(?:Mozilla|curl|Wget|python-requests)/", v)), None),
        "extension": next((v for v in vals if re.match(r"^\.[\w-]+$", v)), None),
        "note": next((v for v in files if NOTE_WORDS.search(v)), None)
                or next((v for v in files if v.lower().endswith((".txt", ".html", ".hta"))), None),
        "file": files[0] if files else None,
    }
    out["scenario"] = scenario(text, vals, member)
    out["attack"] = K.SCENARIO_ATTACK.get(out["scenario"])
    return out


def field_for(aid, q):
    s = aid.split(".")[-1].lower()
    qt = (q.get("question") or "").lower()
    for key, words in (("scenario", ("scenario",)), ("attack", ("attack", "mitre", "technique")),
                       ("agent", ("user-agent", "user agent", "agent")), ("wallet", ("wallet",)),
                       ("mutex", ("mutex",)), ("note", ("note",)), ("extension", ("extension",)),
                       ("url", ("url",)), ("file", ("file",))):
        if any(w in s for w in words) or any(w in qt for w in words):
            return key
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    _, pairs = load_contract(a.contract)
    cache, answers = {}, {}
    for aid, q in pairs:
        art = q.get("artifact") or ""
        if "->" not in art and not art.lower().endswith(".ps1"):
            continue
        field = field_for(aid, q)
        if not field:
            log("skip", aid)
            continue
        if art not in cache:
            try:
                data = find_member(a.artifacts, art)
                cache[art] = analyse(data.decode("utf-8", "ignore").lstrip("﻿"), art.split("->")[-1].strip())
            except Exception as e:
                log("failed", art, e)
                cache[art] = {}
        val = cache[art].get(field)
        if val is None:
            log("no value", aid, field)
            continue
        answers[aid] = normalize(val, q)
    if not answers:
        sys.exit("no answers produced")
    print(json.dumps(answers))


if __name__ == "__main__":
    main()
