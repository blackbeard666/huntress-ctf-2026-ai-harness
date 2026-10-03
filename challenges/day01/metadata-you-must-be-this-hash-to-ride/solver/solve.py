#!/usr/bin/env python3
"""Identity inventory solver: filename / size / MD5 / SHA-1 / SHA-256 of a member inside a zip.

Contract questions look like:
  <prefix>-filename   artifact "X.zip"                  -> which member is "<subject>"?
  <prefix>-size-bytes artifact "X.zip -> member.ext"     -> len(bytes)
  <prefix>-md5 / -sha1 / -sha256                          -> digest of member bytes
Member is resolved from the real archive listing (basename match, then fuzzy subject match).
"""
import argparse, hashlib, io, json, os, re, sys, zipfile


def log(*a):
    print(*a, file=sys.stderr)


def find_artifact(adir, name):
    p = os.path.join(adir, name)
    if os.path.isfile(p):
        return p
    for root, _, files in os.walk(adir):
        if name in files:
            return os.path.join(root, name)
    zips = [os.path.join(r, f) for r, _, fs in os.walk(adir) for f in fs if f.lower().endswith(".zip")]
    if len(zips) == 1:
        log(f"[!] {name} not found, using {zips[0]}")
        return zips[0]
    return None


def members(path, _cache={}):
    """Ordered list of (basename, fullname, bytes) for every file in the archive (recursing into nested zips)."""
    if path in _cache:
        return _cache[path]
    out = []

    def walk(data):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for i in z.infolist():
                if i.is_dir():
                    continue
                b = z.read(i)
                out.append((os.path.basename(i.filename), i.filename, b))
                if b[:4] == b"PK\x03\x04":
                    try:
                        walk(b)
                    except zipfile.BadZipFile:
                        pass

    with open(path, "rb") as f:
        raw = f.read()
    if raw[:4] == b"PK\x03\x04" or zipfile.is_zipfile(path):
        walk(raw)
    else:  # plain file handed out directly
        out.append((os.path.basename(path), path, raw))
    _cache[path] = out
    return out


def tokens(s):
    return set(t for t in re.split(r"[^a-z0-9]+", s.lower()) if t)


def resolve(mems, label, subject):
    if label:
        for m in mems:
            if m[0] == label or m[1] == label:
                return m
        for m in mems:
            if m[0].lower() == label.lower():
                return m
    # fuzzy: subject words / label stem vs member basenames
    want = tokens(subject) | tokens(os.path.splitext(label or "")[0])
    want -= {"the", "of", "first", "renamed", "a", "file"}
    best, score = None, 0
    for m in mems:
        s = len(want & tokens(os.path.splitext(m[0])[0]))
        if s > score:
            best, score = m, s
    if best:
        return best
    return mems[0] if len(mems) == 1 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    c = json.load(open(a.contract))
    qs = c.get("questions") or []
    ids = c.get("answer_ids") or [q.get("id") for q in qs]

    # group by subject prefix (strip the field suffix) to share the member label across questions
    fields = ["filename", "size-bytes", "md5", "sha1", "sha256"]
    groups = {}
    for aid, q in zip(ids, qs):
        for f in fields:
            if aid.endswith("-" + f):
                groups.setdefault(aid[: -len(f) - 1], {})[f] = (aid, q)
                break

    ans = {}
    for prefix, g in groups.items():
        zipname, label = None, None
        subject_q = ""
        for f, (aid, q) in g.items():
            art = q.get("artifact", "")
            parts = [p.strip() for p in art.split("->")]
            zipname = zipname or parts[0]
            if len(parts) > 1:
                label = label or parts[-1]
            if f == "filename":
                m = re.search(r"filename of (?:the )?(.+?)\?", q.get("question", ""))
                subject_q = m.group(1) if m else ""
        subject = subject_q or prefix.split(".")[-1].replace("-", " ")
        path = find_artifact(a.artifacts, zipname)
        if not path:
            log(f"[!] artifact {zipname} missing for {prefix}")
            continue
        mems = members(path)
        log(f"[*] {prefix}: {zipname} members={[m[1] for m in mems]} label={label} subject={subject!r}")
        m = resolve(mems, label, subject)
        if not m:
            log(f"[!] could not resolve member for {prefix}")
            continue
        name, _, b = m
        vals = {
            "filename": name,
            "size-bytes": str(len(b)),
            "md5": hashlib.md5(b).hexdigest(),
            "sha1": hashlib.sha1(b).hexdigest(),
            "sha256": hashlib.sha256(b).hexdigest(),
        }
        for f, (aid, q) in g.items():
            v = vals[f].strip()
            if q.get("normalization") in ("lowercase", "case_insensitive"):
                v = v.lower()
            ans[aid] = v
    if not ans:
        log("[!] no recognised questions")
        sys.exit(1)
    print(json.dumps(ans))


if __name__ == "__main__":
    main()
