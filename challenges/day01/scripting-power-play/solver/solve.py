#!/usr/bin/env python3
"""Power Play: triage inert PowerShell fixtures (base64 JSON descriptor + native .NET types) from an encrypted zip."""
import argparse, atexit, base64, json, re, shutil, subprocess, sys, tempfile, zipfile, io
from pathlib import Path

DEFAULT_PASSWORDS = [None, "infected", "malware", "huntress"]
SCENARIO_TECH = {"resource_hijacking": "T1496", "synthetic_impact": "T1486",
                 "synthetic_collection": "T1555.003"}  # confirmed: Credentials from Web Browsers
B64LIT = re.compile(r"['\"]([A-Za-z0-9+/]{16,}={0,2})['\"]")
URL = re.compile(r"^https?://\S+$")


def log(*a):
    print(*a, file=sys.stderr)


def zip_candidates(artdir, artifact):
    """Find the archive named by the question's artifact ("x.zip -> member"), tolerating odd saved names."""
    arch = artifact.split("->")[0].strip()
    files = expand_nested([p for p in Path(artdir).rglob("*") if p.is_file()])
    exact = [p for p in files if p.name == arch or p.name.startswith(arch + " ->") or p.name == artifact]
    stem = Path(arch).stem
    loose = [p for p in files if p not in exact and stem in p.name]
    rest = [p for p in files if p not in exact and p not in loose]
    return [p for p in exact + loose + rest if zipfile.is_zipfile(p)]


_NESTED = {}


def expand_nested(files, depth=3):
    """Add zips stored inside zips (a bundle wrapping evidence-01.zip, evidence-02.zip, ...) as temp files."""
    out, todo = list(files), [(p, depth) for p in files]
    while todo:
        p, d = todo.pop(0)
        if d <= 0 or not zipfile.is_zipfile(p):
            continue
        key = str(p)
        if key not in _NESTED:
            _NESTED[key] = []
            try:
                with zipfile.ZipFile(p) as z:
                    for info in z.infolist():
                        if info.is_dir() or (info.flag_bits & 1) or not info.filename.lower().endswith(".zip"):
                            continue
                        tdir = Path(tempfile.mkdtemp(prefix="nested-"))
                        atexit.register(shutil.rmtree, tdir, True)
                        q = tdir / Path(info.filename).name
                        q.write_bytes(z.read(info))
                        _NESTED[key].append(q)
            except Exception as e:
                log("nested expand failed", p, e)
        for q in _NESTED[key]:
            if q not in out:
                out.append(q)
                todo.append((q, d - 1))
    return out


def read_member(zpath, member, passwords):
    with zipfile.ZipFile(zpath) as z:
        names = z.namelist()
        hit = next((n for n in names if n == member or n.endswith("/" + member)), None)
        if hit is None:
            return None
        info = z.getinfo(hit)
        for pw in passwords:
            if not (info.flag_bits & 1):
                return z.read(hit)
            data = None
            if info.compress_type != 99:
                try:
                    data = z.read(hit, pwd=pw.encode() if pw else None)
                except Exception:
                    pass
            else:
                data = read_7z(zpath, hit, pw)
            if data is not None:
                return data
    return None


def read_7z(zpath, member, pw):
    if pw is None:
        return None
    try:
        r = subprocess.run(["7z", "x", "-so", f"-p{pw}", str(zpath), member], capture_output=True,
                           stdin=subprocess.DEVNULL, timeout=30)
    except Exception as e:
        log("7z failed", e)
        return None
    return r.stdout if r.returncode == 0 and r.stdout else None


def xor(b, k):
    return bytes(c ^ k[i % len(k)] for i, c in enumerate(b))


def script_keys(text):
    """Possible byte keys a $reconstruct block may use: byte-array literals and string keys."""
    keys = []
    for arr in re.findall(r"@\(\s*((?:0x[0-9a-fA-F]+|\d+)(?:\s*,\s*(?:0x[0-9a-fA-F]+|\d+))*)\s*\)", text):
        try:
            k = bytes(int(x, 0) & 0xFF for x in re.split(r"\s*,\s*", arr.strip()))
            keys.append(k)
        except ValueError:
            pass
    for s in re.findall(r"['\"]([^'\"\s]{2,64})['\"]", text):
        keys.append(s.encode())
    return keys


def decode_record(text):
    """Return the JSON descriptor decoded from the specimen."""
    keys = script_keys(text)
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


def flat(obj):
    """String leaves in source order."""
    if isinstance(obj, dict):
        for v in obj.values():
            yield from flat(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from flat(v)
    elif isinstance(obj, str):
        yield obj


def native_types(text):
    return [t.lower() for t in re.findall(r"\[([A-Za-z_][\w.]*)\]", text)]


def classify(text, rec):
    vals = list(flat(rec))
    nt = " ".join(native_types(text))
    score = {"resource_hijacking": 0, "synthetic_collection": 0, "synthetic_impact": 0}
    if any(v.lower().startswith("wallet") or re.match(r"^(bc1|0x[0-9a-f]{40}|4[0-9AB])", v) for v in vals):
        score["resource_hijacking"] += 2
    if "diagnostics.process" in nt: score["resource_hijacking"] += 2
    if any(re.search(r"stratum|pool|xmrig", v, re.I) for v in vals): score["resource_hijacking"] += 2
    if re.search(r"\.aes\b|cryptography\.(aes|rijndael)", nt): score["synthetic_impact"] += 3
    if any(re.match(r"^\.\w", v) for v in vals): score["synthetic_impact"] += 1
    if any(re.search(r"(recovery|readme|decrypt|restore)[^/\\]*\.(txt|html?)$", v, re.I) for v in vals):
        score["synthetic_impact"] += 2
    if "compression.zipfile" in nt: score["synthetic_collection"] += 3
    if any(v.lower().endswith(".zip") for v in vals): score["synthetic_collection"] += 1
    if "net.httpwebrequest" in nt: score["synthetic_collection"] += 1
    best = max(score, key=score.get)
    log("scores", score)
    return best


def is_url(v): return bool(URL.match(v))
def is_mutex(v): return bool(re.match(r"^(Global|Local)\\", v)) or "mutex" in v.lower()
def is_ua(v): return v.startswith("Mozilla/") or "user-agent" in v.lower()


def is_filename(v):
    return (not is_url(v) and not is_mutex(v) and not is_ua(v) and "\\" not in v and "/" not in v
            and re.match(r"^[^.\s][^\\/:*?\"<>|]*\.[A-Za-z0-9]{1,5}$", v) is not None)


def answer(kind, scenario, rec, q):
    vals = list(flat(rec))
    text = q["question"].lower()
    if kind == "scenario" or "scenario" in text:
        acc = q["answer_format"].get("accepted_values") or []
        return scenario if not acc or scenario in acc else None
    if kind == "attack" or "att&ck" in text:
        return SCENARIO_TECH.get(scenario)
    if kind == "url" or "url" in text:
        return next((v for v in vals if is_url(v)), None)
    if kind == "wallet" or "wallet" in text:
        return next((v for v in vals if re.match(r"^(wallet|bc1|0x[0-9a-fA-F]{40}|4[0-9AB][1-9A-HJ-NP-Za-km-z]{93})", v)), None)
    if kind == "mutex" or "mutex" in text:
        return next((v for v in vals if is_mutex(v)), None)
    if kind in ("user-agent", "agent") or "user-agent" in text or "user agent" in text:
        return next((v for v in vals if is_ua(v)), None)
    if kind == "extension" or "extension" in text:
        return next((v for v in vals if re.match(r"^\.[\w-]+$", v)), None)
    if kind == "note" or "note" in text:
        return next((v for v in vals if is_filename(v) and re.search(r"recovery|readme|decrypt|restore|note", v, re.I)), None)
    if kind == "file" or "filename" in text:
        return next((v for v in vals if is_filename(v)), None)
    if kind == "registry" or "registry" in text:
        return next((v for v in vals if re.match(r"^(HK\w+|HKEY_)", v)), None)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    c = json.loads(Path(a.contract).read_text())
    qs, ids = c.get("questions") or [], c.get("answer_ids") or [q.get("id") for q in c.get("questions", [])]
    if not qs:
        sys.exit("contract has no questions")
    pws = list(DEFAULT_PASSWORDS)
    for src in (c.get("prompt", ""), c.get("guidance", ""), *[q["question"] for q in qs]):
        for m in re.findall(r"password[^'\"`]*['\"`]([^'\"`]+)['\"`]", src or "", re.I):
            pws.insert(1, m)
    cache, out = {}, {}
    for aid, q in zip(ids, qs):
        art = q.get("artifact", "")
        if "->" not in art or not art.split("->")[1].strip().lower().endswith(".ps1"):
            continue
        member = art.split("->")[1].strip()
        key = art
        if key not in cache:
            cache[key] = None
            for zp in zip_candidates(a.artifacts, art):
                data = read_member(zp, member, pws)
                if data is not None:
                    text = data.decode("utf-8", "replace")
                    try:
                        rec = decode_record(text)
                    except ValueError as e:
                        log(art, e)
                        continue
                    cache[key] = (classify(text, rec), rec)
                    log(art, "->", zp.name, cache[key])
                    break
        if not cache[key]:
            log("could not read", art)
            continue
        scenario, rec = cache[key]
        v = answer(aid.split(".")[-1].split("-")[-1] if "user-agent" not in aid else "user-agent", scenario, rec, q)
        if v is not None:
            out[aid] = v.strip() if q.get("normalization", "trim") == "trim" else v
    print(json.dumps(out))


if __name__ == "__main__":
    main()
