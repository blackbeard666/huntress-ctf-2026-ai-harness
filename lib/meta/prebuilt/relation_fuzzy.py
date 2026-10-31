"""Fuzzy / similarity hashing (ssdeep CTPH) of a member or across a cluster zip's members. Speculative tier (never asked
by the GM yet); fmt `relation` plus the aliases `fuzzy` and `ssdeep`.

CTPH = libfuzzy 2.14 (`ssdeep -s`, ppdeep) re-implemented in pure Python (ssdeep/ppdeep/tlsh are not installed in-window):
rolling hash window 7 (h1 sum, h2 weighted sum, h3 shift-5 xor; uint32), piece hash = FNV-1 mod 64 (init 0x27), base64
alphabet, block size = 3*2^k with 3*2^k*64 >= len, halved while the first part has < 32 chars; part 1 <= 63 chars + tail,
part 2 (block size * 2) <= 31 chars + tail; tail = b64[piece hash] when the final rolling hash != 0, else the char saved
at the last trigger past the cap. Output `blocksize:hash1:hash2`.
Compare = libfuzzy fuzzy_compare: runs > 3 of one char cut to 3, block sizes must be equal or x2, identical -> 100,
needs a common 7-char substring, weighted edit distance (ins/del 1, sub 2) scaled by 64/(l1+l2) -> 100 - 100*d/64,
capped at bs/3*min(l1,l2) for block sizes < 45. All integer division.

Members/labels (same convention as relation.identical_sha256_groups): every non-directory entry of the cluster zip minus
its delivery manifest; label = manifest `id` by path then basename, else basename without extension.
  ssdeep / ssdeep_hash / fuzzy_hash / ctph: hash of the member the question names (label, path or basename), else of
    the given bytes themselves (a single member handed out directly).
  ssdeep_hashes: {label: hash} of every member (label order).
  most_similar_pair: [a, b] (sorted labels) of the highest-scoring pair; ties -> smallest (a, b).
  similarity_percent / ssdeep_score: the score of the two members the question names, else of the most similar pair.
  similar_groups: connected components (pairs scoring >= threshold; threshold from the question, default 50) of >= 2
    members, each sorted, groups sorted. similar_pairs: [[a, b], ...] scoring >= threshold.
Corpus fields on a non-zip / < 2 members -> "none". One analysis per container sha256 (never id())."""
import hashlib
import io
import json
import re
import struct
import zlib

_HASH_FIELDS = ("ssdeep", "ssdeep_hash", "ssdeep_digest", "ssdeep_signature", "fuzzy_hash", "ctph", "ctph_hash")
_CORPUS = {
    "ssdeep_hashes": "hashes", "fuzzy_hashes": "hashes", "ssdeep_map": "hashes",
    "most_similar_pair": "pair", "ssdeep_most_similar_pair": "pair", "most_similar_members": "pair",
    "closest_pair": "pair",
    "similarity_percent": "score", "ssdeep_similarity_percent": "score", "ssdeep_score": "score",
    "similarity_score": "score", "ssdeep_compare_score": "score", "fuzzy_similarity_percent": "score",
    "max_similarity_percent": "score",
    "ssdeep_similar_groups": "groups", "fuzzy_similar_groups": "groups", "ctph_similar_groups": "groups",
    "ssdeep_groups": "groups", "ssdeep_similar_pairs": "pairs", "fuzzy_similar_pairs": "pairs",
}

FIELDS = {
    ("relation", "ssdeep"): "fuzzy_value",
    ("relation", "ssdeep_hash"): "fuzzy_value",
    ("relation", "ssdeep_digest"): "fuzzy_value",
    ("relation", "fuzzy_hash"): "fuzzy_value",
    ("relation", "ctph"): "fuzzy_value",
    ("relation", "ssdeep_hashes"): "fuzzy_value",
    ("relation", "fuzzy_hashes"): "fuzzy_value",
    ("relation", "most_similar_pair"): "fuzzy_value",
    ("relation", "ssdeep_most_similar_pair"): "fuzzy_value",
    ("relation", "most_similar_members"): "fuzzy_value",
    ("relation", "similarity_percent"): "fuzzy_value",
    ("relation", "ssdeep_similarity_percent"): "fuzzy_value",
    ("relation", "ssdeep_score"): "fuzzy_value",
    ("relation", "similarity_score"): "fuzzy_value",
    ("relation", "ssdeep_compare_score"): "fuzzy_value",
    ("relation", "max_similarity_percent"): "fuzzy_value",
    ("relation", "ssdeep_similar_groups"): "fuzzy_value",
    ("relation", "fuzzy_similar_groups"): "fuzzy_value",
    ("relation", "ctph_similar_groups"): "fuzzy_value",
    ("relation", "ssdeep_groups"): "fuzzy_value",
    ("relation", "ssdeep_similar_pairs"): "fuzzy_value",
    ("fuzzy", "ssdeep"): "fuzzy_value",
    ("fuzzy", "ssdeep_hash"): "fuzzy_value",
    ("fuzzy", "hash"): "fuzzy_value",
    ("fuzzy", "fuzzy_hash"): "fuzzy_value",
    ("fuzzy", "ctph"): "fuzzy_value",
    ("fuzzy", "ssdeep_hashes"): "fuzzy_value",
    ("fuzzy", "hashes"): "fuzzy_value",
    ("fuzzy", "most_similar_pair"): "fuzzy_value",
    ("fuzzy", "similarity_percent"): "fuzzy_value",
    ("fuzzy", "similarity_score"): "fuzzy_value",
    ("fuzzy", "ssdeep_score"): "fuzzy_value",
    ("fuzzy", "similar_groups"): "fuzzy_value",
    ("fuzzy", "similar_pairs"): "fuzzy_value",
    ("ssdeep", "ssdeep"): "fuzzy_value",
    ("ssdeep", "hash"): "fuzzy_value",
    ("ssdeep", "ssdeep_hash"): "fuzzy_value",
    ("ssdeep", "digest"): "fuzzy_value",
    ("ssdeep", "hashes"): "fuzzy_value",
    ("ssdeep", "ssdeep_hashes"): "fuzzy_value",
    ("ssdeep", "most_similar_pair"): "fuzzy_value",
    ("ssdeep", "similarity_percent"): "fuzzy_value",
    ("ssdeep", "similarity_score"): "fuzzy_value",
    ("ssdeep", "score"): "fuzzy_value",
    ("ssdeep", "compare_score"): "fuzzy_value",
    ("ssdeep", "similar_groups"): "fuzzy_value",
    ("ssdeep", "similar_pairs"): "fuzzy_value",
}

_B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_SL = 64            # SPAMSUM_LENGTH
_MINBS = 3
_WIN = 7
_INIT = 0x27        # FNV-1 0x28021967 mod 64
_CACHE = {}         # container sha256 -> analysis | None
_HCACHE = {}        # member sha256 -> ssdeep string
_LIST_KEYS = ("artifacts", "members", "files", "entries", "items")
_PATH_KEYS = ("path", "filename", "file", "name", "member", "member_path")


def _fnv_table():
    # piece hash step: h' = ((h * 0x01000193) ^ c) mod 64 depends only on h mod 64 and c mod 64
    return [[((h * 0x01000193) ^ c) & 63 for c in range(64)] for h in range(64)]


_FNV = None


def _rolls(data):
    """The rolling-hash value after every byte (block-size independent, computed once)."""
    out = [0] * len(data)
    win = [0] * _WIN
    h1 = h2 = h3 = 0
    n = 0
    for i, c in enumerate(data):
        h2 = h2 - h1 + _WIN * c
        h1 = h1 + c - win[n]
        win[n] = c
        n = n + 1 if n < _WIN - 1 else 0
        h3 = ((h3 << 5) & 0xFFFFFFFF) ^ c
        out[i] = (h1 + h2 + h3) & 0xFFFFFFFF
    return out


def _pass(data, rolls, bs):
    global _FNV
    if _FNV is None:
        _FNV = _fnv_table()
    fnv = _FNV
    bs2 = bs * 2
    p1 = p2 = _INIT
    s1, s2 = [], []
    last1 = last2 = ""
    for i, c in enumerate(data):
        c &= 63
        p1 = fnv[p1][c]
        p2 = fnv[p2][c]
        r = rolls[i]
        if r % bs == bs - 1:
            last1 = _B64[p1]
            if len(s1) < _SL - 1:
                s1.append(last1)
                p1 = _INIT
                last1 = ""
            if r % bs2 == bs2 - 1:
                last2 = _B64[p2]
                if len(s2) < _SL // 2 - 1:
                    s2.append(last2)
                    p2 = _INIT
                    last2 = ""
    return s1, s2, p1, p2, last1, last2


def ssdeep_hash(data):
    """libfuzzy-compatible `blocksize:hash1:hash2` of bytes."""
    data = bytes(data)
    key = hashlib.sha256(data).digest()
    if key in _HCACHE:
        return _HCACHE[key]
    rolls = _rolls(data)
    final = rolls[-1] if rolls else 0
    bs = _MINBS
    while bs * _SL < len(data):
        bs *= 2
    while True:
        s1, s2, p1, p2, last1, last2 = _pass(data, rolls, bs)
        if bs > _MINBS and len(s1) < _SL // 2:
            bs //= 2
            continue
        break
    if final != 0:
        s1.append(_B64[p1])
        s2.append(_B64[p2])
    else:
        s1.append(last1)
        s2.append(last2)
    out = "%d:%s:%s" % (bs, "".join(s1), "".join(s2))
    if len(_HCACHE) > 4096:
        _HCACHE.clear()
    _HCACHE[key] = out
    return out


_RUNS = re.compile(r"(.)\1{3,}")


def _elim(s):
    return _RUNS.sub(lambda m: m.group(1) * 3, s)


def _edit(a, b):
    """Weighted edit distance: insert/delete 1, substitute 2 (libfuzzy edit_distn)."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (0 if ca == cb else 2))
        prev = cur
    return prev[-1]


def _score_strings(a, b, bs):
    if len(a) > _SL or len(b) > _SL or len(a) < _WIN or len(b) < _WIN:
        return 0
    grams = {a[i:i + _WIN] for i in range(len(a) - _WIN + 1)}
    if not any(b[i:i + _WIN] in grams for i in range(len(b) - _WIN + 1)):
        return 0
    score = _edit(a, b) * _SL // (len(a) + len(b))
    score = 100 * score // _SL
    if score >= 100:
        return 0
    score = 100 - score
    if bs >= (99 + _WIN) // _WIN * _MINBS:
        return score
    cap = bs // _MINBS * min(len(a), len(b))
    return min(score, cap)


def ssdeep_compare(h1, h2):
    """libfuzzy fuzzy_compare score 0..100 of two `bs:h1:h2` strings."""
    try:
        b1, x1, y1 = h1.split(":", 2)
        b2, x2, y2 = h2.split(":", 2)
        b1, b2 = int(b1), int(b2)
    except ValueError:
        return 0
    y1, y2 = y1.split(",", 1)[0], y2.split(",", 1)[0]
    if b1 != b2 and b1 != b2 * 2 and b2 != b1 * 2:
        return 0
    x1, y1, x2, y2 = _elim(x1), _elim(y1), _elim(x2), _elim(y2)
    if b1 == b2 and x1 == x2 and y1 == y2:
        return 100
    if b1 == b2:
        return max(_score_strings(x1, x2, b1), _score_strings(y1, y2, b1 * 2))
    if b1 == b2 * 2:
        return _score_strings(x1, y2, b1)
    return _score_strings(y1, x2, b2)


def _manifest_artifacts(raw):
    try:
        doc = json.loads(raw.decode("utf-8-sig"))
    except Exception:  # noqa: BLE001 - not json
        return None
    arts = doc if isinstance(doc, list) else (
        next((doc[k] for k in _LIST_KEYS if isinstance(doc.get(k), list)), None) if isinstance(doc, dict) else None)
    if arts is None or not all(isinstance(a, dict) for a in arts):
        return None
    return arts


def _raw_lfh(buf, zi):
    off = zi.header_offset
    if buf[off:off + 4] != b"PK\x03\x04":
        return None
    nlen, xlen = struct.unpack_from("<HH", buf, off + 26)
    comp = buf[off + 30 + nlen + xlen:off + 30 + nlen + xlen + zi.compress_size]
    if zi.compress_type == 0:
        return bytes(comp)
    if zi.compress_type == 8:
        return zlib.decompressobj(-15).decompress(comp)
    return None


def _members(data):
    """[(label, path, bytes)] of a zip, or None."""
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        infos = [zi for zi in z.infolist() if not zi.is_dir() and not zi.filename.endswith(("/", "\\"))]
    except Exception:  # noqa: BLE001 - not a zip
        return None

    def read(zi):
        try:
            return z.read(zi)
        except (RuntimeError, NotImplementedError):          # encrypted member: the password-aware read
            try:
                from lib.common import read_member
                return read_member(io.BytesIO(data), zi.filename)
            except Exception:  # noqa: BLE001
                return None
        except Exception:  # noqa: BLE001 - bad CRC: raw local-header bytes
            try:
                return _raw_lfh(data, zi)
            except Exception:  # noqa: BLE001
                return None

    ids, manifests = {}, set()
    for zi in infos:
        base = zi.filename.replace("\\", "/").rsplit("/", 1)[-1].lower()
        if not base.endswith(".json") or not ("manifest" in base or base == "index.json"):
            continue
        raw = read(zi)
        arts = _manifest_artifacts(raw) if raw is not None else None
        if arts is None:
            if "manifest" in base:
                manifests.add(zi.filename)
            continue
        manifests.add(zi.filename)
        for a in arts:
            if a.get("id") is None:
                continue
            for k in _PATH_KEYS:
                if isinstance(a.get(k), str) and a[k]:
                    ids.setdefault(a[k], str(a["id"]))
    out = []
    for zi in infos:
        if zi.filename in manifests:
            continue
        b = read(zi)
        if b is None:
            continue
        path = zi.filename.replace("\\", "/")
        base = path.rsplit("/", 1)[-1]
        label = ids.get(zi.filename) or ids.get(path) or ids.get(base)
        if label is None:
            label = base.rsplit(".", 1)[0] if "." in base.lstrip(".") else base
        out.append((label, path, b))
    return out


def _analyse(data):
    if not data or data[:2] != b"PK":
        return None
    key = hashlib.sha256(data).hexdigest()
    if key in _CACHE:
        return _CACHE[key]
    mem = _members(data)
    res = None
    if mem:
        hashes = {}
        for label, _p, b in mem:
            hashes.setdefault(label, ssdeep_hash(b))
        labels = sorted(hashes)
        scores = {}
        for i, a in enumerate(labels):
            for b in labels[i + 1:]:
                scores[(a, b)] = ssdeep_compare(hashes[a], hashes[b])
        res = {"members": mem, "hashes": hashes, "labels": labels, "scores": scores}
    if len(_CACHE) > 64:
        _CACHE.clear()
    _CACHE[key] = res
    return res


def _named(res, ctx):
    """Labels of corpus members the question/artifact names, in order of appearance."""
    text = " ".join(str(x) for x in ((ctx.get("question") or {}).get("question"), ctx.get("member")) if x)
    hits = []
    for label, path, _b in res["members"]:
        base = path.rsplit("/", 1)[-1]
        for tok in {label, path, base}:
            m = re.search(r"(?<![\w.-])%s(?![\w-])" % re.escape(tok), text)
            if m:
                hits.append((m.start(), label))
                break
    out = []
    for _pos, lab in sorted(hits):
        if lab not in out:
            out.append(lab)
    return out


def _threshold(ctx):
    q = str((ctx.get("question") or {}).get("question") or "")
    m = re.search(r"(?:>=|≥|=>|at least|threshold(?: of)?|score(?: of)?|minimum(?: score)?(?: of)?)\s*(\d{1,3})\b",
                  q, re.I)
    if m and 0 <= int(m.group(1)) <= 100:
        return int(m.group(1))
    return 50


def fuzzy_value(data, ctx):
    ctx = ctx or {}
    field = ctx.get("field") or ""
    if data is None:
        return None
    kind = "hash" if field in _HASH_FIELDS or field in ("hash", "digest") else _CORPUS.get(field)
    if kind is None:
        kind = {"hashes": "hashes", "similar_groups": "groups", "similar_pairs": "pairs", "score": "score",
                "compare_score": "score"}.get(field)
    if kind is None:
        return None
    try:
        res = _analyse(data) if data[:2] == b"PK" else None
    except Exception:  # noqa: BLE001 - malformed container
        res = None
    if kind == "hash":
        if res:
            named = _named(res, ctx)
            if named:
                return res["hashes"][named[0]]
        return ssdeep_hash(data)
    if not res or len(res["labels"]) < 2:
        return "none"
    scores = res["scores"]
    if kind == "hashes":
        return {lab: res["hashes"][lab] for lab in res["labels"]}
    best = min(scores, key=lambda k: (-scores[k], k))
    if kind == "pair":
        return list(best)
    if kind == "score":
        named = _named(res, ctx)
        if len(named) >= 2:
            a, b = sorted(named[:2])
            return scores.get((a, b), 0)
        return scores[best]
    thr = _threshold(ctx)
    edges = sorted(k for k, v in scores.items() if v >= thr)
    if kind == "pairs":
        return [list(k) for k in edges]
    parent = {lab: lab for lab in res["labels"]}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        parent[find(a)] = find(b)
    comps = {}
    for lab in res["labels"]:
        comps.setdefault(find(lab), []).append(lab)
    return sorted(sorted(g) for g in comps.values() if len(g) >= 2)
