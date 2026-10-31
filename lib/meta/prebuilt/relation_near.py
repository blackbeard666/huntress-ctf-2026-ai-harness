"""Near-duplicate / fabricated members and bad-CRC inner archives of a cluster zip (`cluster-NNN.zip`). Speculative tier;
the D30 sibling of the GM-verified relation.identical_sha256_groups (lib/meta/relation.py).

Shape seen in ALL 15 D30 timed clusters: beside the exact groups (identical SHA-256), each group may be shadowed by ONE
member of the SAME size differing in 1 byte (`$ErrorActionPrfference`), and the inner zips (one `.txt` each) carry one
copy whose byte flip lands in the stored data (CD CRC32 != crc32(data) -> zipfile BadZipFile "Bad CRC-32") or in the
local-header name (BadZipFile "name differs", CRC still fine).

Members/labels as relation_variants: every non-directory entry minus the delivery manifest; label = manifest `id` by
path then basename, else basename without extension. Near-duplicate: a member NOT in an exact group whose bytes are
within 4 edits of a group's content (same length: Hamming <= 4; small files < 4 KiB with lengths within 4: banded
Levenshtein <= 4). Edges between two singletons also join (fuzzy components), but only a component holding an exact
group (>= 2 identical) yields near ids: the members outside its largest identical class.
  near_duplicate_ids / fabricated_ids / tampered_ids / modified_copy_ids: sorted labels of those near copies.
  near_duplicate_pairs: [[group representative (smallest label of the exact class), near label]] sorted.
  near_duplicate_groups: every fuzzy component of >= 2 members WITH a near copy (exact class + near copies) sorted;
    near_duplicate_groups_all (and fuzzy_/similar_ groups): every component >= 2 incl. pure-exact ones.
  crc_mismatch_ids / bad_crc_*: members (zips) with an entry whose stored CD CRC32 != crc32(raw-inflated data from
    its local header), plus an OUTER member whose own data fails its CD CRC.
  corrupted_ids / corrupt_*: members (zips) any entry of which zipfile cannot read (bad CRC, header/name mismatch,
    broken stream), plus outer bad-CRC members.
  *_count: len of the list; fabricated_member / near_duplicate_id: the single label when exactly one, else the list.
Non-zip -> "none". One parse per container sha256 (never id())."""
import hashlib
import io
import json
import struct
import zlib

FIELDS = {
    ("relation", "near_duplicate_ids"): "near_value",
    ("relation", "near_duplicate_member_ids"): "near_value",
    ("relation", "near_duplicate_members"): "near_value",
    ("relation", "near_duplicates"): "near_value",
    ("relation", "near_duplicate_id"): "near_value",
    ("relation", "near_duplicate_member"): "near_value",
    ("relation", "near_duplicate_count"): "near_value",
    ("relation", "near_duplicate_pairs"): "near_value",
    ("relation", "near_duplicate_groups"): "near_value",
    ("relation", "near_duplicate_groups_all"): "near_value",
    ("relation", "near_identical_groups"): "near_value",
    ("relation", "near_identical_ids"): "near_value",
    ("relation", "fuzzy_duplicate_groups"): "near_value",
    ("relation", "similar_groups"): "near_value",
    ("relation", "fabricated_ids"): "near_value",
    ("relation", "fabricated_member_ids"): "near_value",
    ("relation", "fabricated_members"): "near_value",
    ("relation", "fabricated_member"): "near_value",
    ("relation", "fabricated_id"): "near_value",
    ("relation", "fabricated_count"): "near_value",
    ("relation", "tampered_ids"): "near_value",
    ("relation", "tampered_member_ids"): "near_value",
    ("relation", "tampered_members"): "near_value",
    ("relation", "modified_copy_ids"): "near_value",
    ("relation", "modified_copies"): "near_value",
    ("relation", "altered_copy_ids"): "near_value",
    ("relation", "crc_mismatch_ids"): "near_value",
    ("relation", "crc_mismatch_member_ids"): "near_value",
    ("relation", "crc_mismatch_members"): "near_value",
    ("relation", "crc_mismatch_count"): "near_value",
    ("relation", "bad_crc_ids"): "near_value",
    ("relation", "bad_crc_member_ids"): "near_value",
    ("relation", "bad_crc_members"): "near_value",
    ("relation", "bad_crc_count"): "near_value",
    ("relation", "crc_failure_ids"): "near_value",
    ("relation", "corrupted_ids"): "near_value",
    ("relation", "corrupted_member_ids"): "near_value",
    ("relation", "corrupted_members"): "near_value",
    ("relation", "corrupted_count"): "near_value",
    ("relation", "corrupt_ids"): "near_value",
    ("relation", "corrupt_member_ids"): "near_value",
    ("relation", "corrupt_members"): "near_value",
    ("relation", "damaged_archive_ids"): "near_value",
}

_CACHE = {}   # container sha256 -> analysis dict | None
_LIST_KEYS = ("artifacts", "members", "files", "entries", "items")
_PATH_KEYS = ("path", "filename", "file", "name", "member", "member_path")
_MAXD = 4
_SMALL = 4096


def _manifest_artifacts(raw):
    try:
        doc = json.loads(raw.decode("utf-8-sig"))
    except Exception:  # noqa: BLE001 - not json
        return None
    if isinstance(doc, list):
        arts = doc
    elif isinstance(doc, dict):
        arts = next((doc[k] for k in _LIST_KEYS if isinstance(doc.get(k), list)), None)
    else:
        arts = None
    if arts is None or not all(isinstance(a, dict) for a in arts):
        return None
    return arts


def _lfh_data(buf, zi):
    """(local-header name bytes, inflated data) straight from the local header, no CRC check; None on failure."""
    off = zi.header_offset
    if buf[off:off + 4] != b"PK\x03\x04":
        return None
    nlen, xlen = struct.unpack_from("<HH", buf, off + 26)
    start = off + 30 + nlen + xlen
    comp = buf[start:start + zi.compress_size]
    if zi.compress_type == 0:
        return buf[off + 30:off + 30 + nlen], bytes(comp)
    if zi.compress_type == 8:
        return buf[off + 30:off + 30 + nlen], zlib.decompressobj(-15).decompress(comp)
    if zi.compress_type == 12:
        import bz2
        return buf[off + 30:off + 30 + nlen], bz2.decompress(comp)
    return None


def _zip_check(buf):
    """(crc_bad, unreadable) of a zip blob's entries; (False, False) for a non-zip or encrypted-only zip."""
    if buf[:2] != b"PK":
        return False, False
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(buf))
        infos = z.infolist()
    except Exception:  # noqa: BLE001 - not a readable zip: corrupted container
        return False, True
    crc_bad = unreadable = False
    for zi in infos:
        if zi.is_dir() or zi.flag_bits & 1:
            continue
        try:
            z.read(zi)
        except Exception:  # noqa: BLE001 - bad CRC / name mismatch / broken stream
            unreadable = True
        try:
            got = _lfh_data(buf, zi)
        except Exception:  # noqa: BLE001
            got = None
        if got is not None and (zlib.crc32(got[1]) & 0xFFFFFFFF) != zi.CRC:
            crc_bad = True
    return crc_bad, unreadable


def _members(data):
    """[(label, bytes, outer_crc_bad)] of the cluster zip, or None for a non-zip."""
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        infos = [zi for zi in z.infolist() if not zi.is_dir() and not zi.filename.endswith(("/", "\\"))]
    except Exception:  # noqa: BLE001 - not a zip
        return None

    def read(zi):
        try:
            return z.read(zi), False
        except (RuntimeError, NotImplementedError):          # encrypted member: the password-aware read
            try:
                from lib.common import read_member
                return read_member(io.BytesIO(data), zi.filename), False
            except Exception:  # noqa: BLE001
                return None, False
        except Exception:  # noqa: BLE001 - bad CRC on the OUTER zip: raw local-header bytes
            try:
                got = _lfh_data(data, zi)
            except Exception:  # noqa: BLE001
                got = None
            return (got[1], True) if got else (None, True)

    ids, manifests = {}, set()
    for zi in infos:
        base = zi.filename.replace("\\", "/").rsplit("/", 1)[-1].lower()
        if not base.endswith(".json") or not ("manifest" in base or base == "index.json"):
            continue
        raw, _ = read(zi)
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
        b, bad = read(zi)
        if b is None:
            return None
        path = zi.filename.replace("\\", "/")
        base = path.rsplit("/", 1)[-1]
        label = ids.get(zi.filename) or ids.get(path) or ids.get(base)
        if label is None:
            label = base.rsplit(".", 1)[0] if "." in base.lstrip(".") else base
        out.append((label, b, bad))
    return out


def _lev_within(a, b, k):
    """True when the Levenshtein distance of a, b is <= k (banded DP)."""
    n, m = len(a), len(b)
    if abs(n - m) > k:
        return False
    big = k + 1
    prev = [j if j <= k else big for j in range(m + 1)]
    for i in range(1, n + 1):
        lo, hi = max(1, i - k), min(m, i + k)
        cur = [big] * (m + 1)
        cur[0] = i if i <= k else big
        ai = a[i - 1]
        best = cur[0]
        for j in range(lo, hi + 1):
            v = prev[j - 1] + (ai != b[j - 1])
            if prev[j] + 1 < v:
                v = prev[j] + 1
            if cur[j - 1] + 1 < v:
                v = cur[j - 1] + 1
            cur[j] = v if v < big else big
            if v < best:
                best = v
        if best > k:
            return False
        prev = cur
    return prev[m] <= k


def _near(a, b):
    if len(a) == len(b):
        if not a:
            return False
        d = 0
        for x, y in zip(a, b):
            if x != y:
                d += 1
                if d > _MAXD:
                    break
        if d <= _MAXD:
            return d * 8 <= len(a)          # a 1-byte "near copy" of a 3-byte file is noise
        if len(a) >= _SMALL:
            return False
    if max(len(a), len(b)) >= _SMALL or min(len(a), len(b)) < 2 * _MAXD:
        return False
    return _lev_within(a, b, _MAXD)


def _analyse(data):
    if not data or data[:2] != b"PK":
        return None
    key = hashlib.sha256(data).hexdigest()
    if key in _CACHE:
        return _CACHE[key]
    members = _members(data)
    res = None
    if members is not None:
        classes = {}
        for label, b, _ in members:
            classes.setdefault(hashlib.sha256(b).hexdigest(), (b, []))[1].append(label)
        cls = [(b, sorted(lbls)) for b, lbls in classes.values()]
        parent = list(range(len(cls)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for i in range(len(cls)):
            for j in range(i + 1, len(cls)):
                if find(i) != find(j) and _near(cls[i][0], cls[j][0]):
                    parent[find(i)] = find(j)
        comps = {}
        for i in range(len(cls)):
            comps.setdefault(find(i), []).append(i)
        near_ids, pairs, groups_near, groups_all = [], [], [], []
        for idx in comps.values():
            labels = sorted(x for i in idx for x in cls[i][1])
            if len(labels) < 2:
                continue
            groups_all.append(labels)
            anchor = min(idx, key=lambda i: (-len(cls[i][1]), cls[i][1][0]))   # largest exact class
            if len(cls[anchor][1]) < 2 or len(idx) < 2:
                continue
            groups_near.append(labels)
            rep = cls[anchor][1][0]
            for i in idx:
                if i == anchor:
                    continue
                for x in cls[i][1]:
                    near_ids.append(x)
                    pairs.append([rep, x])
        crc_ids, corrupt_ids = [], []
        for label, b, outer_bad in members:
            crc_bad, unreadable = _zip_check(b)
            if crc_bad or outer_bad:
                crc_ids.append(label)
            if crc_bad or unreadable or outer_bad:
                corrupt_ids.append(label)
        res = {"near": sorted(near_ids), "pairs": sorted(pairs), "groups": sorted(groups_near),
               "groups_all": sorted(groups_all), "crc": sorted(crc_ids), "corrupt": sorted(corrupt_ids)}
    if len(_CACHE) > 64:
        _CACHE.clear()
    _CACHE[key] = res
    return res


def _shape(lst, field):
    if field.endswith("_count"):
        return len(lst)
    if field.endswith(("_member", "_id")):           # singular: the one label, else the list
        return lst[0] if len(lst) == 1 else lst
    return lst


def near_value(data, ctx):
    field = (ctx or {}).get("field") or ""
    res = _analyse(data)
    if res is None:
        return "none"
    if field.startswith(("crc_", "bad_crc")):
        return _shape(res["crc"], field)
    if field.startswith(("corrupt", "damaged")):
        return _shape(res["corrupt"], field)
    if field == "near_duplicate_pairs":
        return res["pairs"]
    if field in ("near_duplicate_groups", "near_identical_groups"):
        return res["groups"]
    if field.endswith("_groups"):                    # fuzzy/similar/semantic/near_duplicate_groups_all
        return res["groups_all"]
    return _shape(res["near"], field)
