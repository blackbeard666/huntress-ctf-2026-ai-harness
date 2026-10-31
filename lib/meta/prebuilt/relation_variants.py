"""Exact-identity siblings of the GM-verified D30 relation.identical_sha256_groups (lib/meta/relation.py) on a cluster
zip (`cluster-NNN.zip`): other digests (md5/sha1/sha512), byte size, and the aggregates a dedup question could ask
(unique count, group count, duplicate members, largest group, singletons, member count). Speculative tier.

Members = every non-directory entry of the cluster zip at any depth (`artifacts/<word>-NN.ext`), minus the delivery
manifest (`*manifest*.json`, or an `index.json` that parses as an artifact list). Hashed as RAW member bytes (an inner
zip with bad-CRC entries is just bytes here); when the OUTER read fails its CRC the member is re-read straight from
its local header without the CRC check. Label = manifest `id` mapped by member path then basename; no manifest ->
basename without extension (D30 timed `artifacts/<word>-NN.txt` -> `<word>-NN`). Groups: classes of >= 2 labels,
each sorted, the groups sorted -> compact JSON. Non-zip input -> "none". One parse per container sha256 (never id()).

Also registers identical_sha256_groups under the format aliases corpus/cluster/dedup/inventory (the `relation` key is
the built-in verified entry)."""
import hashlib
import io
import json
import struct
import zlib

FIELDS = {
    ("relation", "identical_md5_groups"): "relation_value",
    ("relation", "identical_sha1_groups"): "relation_value",
    ("relation", "identical_sha512_groups"): "relation_value",
    ("relation", "identical_size_groups"): "relation_value",
    ("relation", "identical_size_bytes_groups"): "relation_value",
    ("relation", "identical_content_groups"): "relation_value",
    ("relation", "identical_groups"): "relation_value",
    ("relation", "identical_hash_groups"): "relation_value",
    ("relation", "duplicate_groups"): "relation_value",
    ("relation", "duplicate_sha256_groups"): "relation_value",
    ("relation", "duplicate_md5_groups"): "relation_value",
    ("relation", "duplicate_sha1_groups"): "relation_value",
    ("relation", "duplicate_sha512_groups"): "relation_value",
    ("relation", "unique_sha256_count"): "relation_value",
    ("relation", "unique_md5_count"): "relation_value",
    ("relation", "unique_sha1_count"): "relation_value",
    ("relation", "unique_sha512_count"): "relation_value",
    ("relation", "unique_content_count"): "relation_value",
    ("relation", "distinct_sha256_count"): "relation_value",
    ("relation", "unique_size_count"): "relation_value",
    ("relation", "duplicate_group_count"): "relation_value",
    ("relation", "identical_group_count"): "relation_value",
    ("relation", "duplicate_member_count"): "relation_value",
    ("relation", "duplicate_member_count_in_groups"): "relation_value",
    ("relation", "duplicate_member_count_redundant"): "relation_value",
    ("relation", "redundant_member_count"): "relation_value",
    ("relation", "redundant_copy_count"): "relation_value",
    ("relation", "duplicate_copy_count"): "relation_value",
    ("relation", "largest_group_size"): "relation_value",
    ("relation", "largest_duplicate_group_size"): "relation_value",
    ("relation", "singleton_ids"): "relation_value",
    ("relation", "singleton_count"): "relation_value",
    ("relation", "unique_member_ids"): "relation_value",
    ("relation", "duplicate_ids"): "relation_value",
    ("relation", "duplicate_member_ids"): "relation_value",
    ("relation", "member_count"): "relation_value",
    ("relation", "member_ids"): "relation_value",
    ("corpus", "identical_sha256_groups"): "relation_value",
    ("corpus", "identical_md5_groups"): "relation_value",
    ("corpus", "identical_sha1_groups"): "relation_value",
    ("corpus", "identical_sha512_groups"): "relation_value",
    ("corpus", "identical_size_groups"): "relation_value",
    ("corpus", "duplicate_groups"): "relation_value",
    ("corpus", "unique_sha256_count"): "relation_value",
    ("corpus", "duplicate_group_count"): "relation_value",
    ("corpus", "duplicate_member_count"): "relation_value",
    ("corpus", "largest_group_size"): "relation_value",
    ("corpus", "singleton_ids"): "relation_value",
    ("corpus", "member_count"): "relation_value",
    ("cluster", "identical_sha256_groups"): "relation_value",
    ("cluster", "identical_md5_groups"): "relation_value",
    ("cluster", "identical_sha1_groups"): "relation_value",
    ("cluster", "identical_sha512_groups"): "relation_value",
    ("cluster", "identical_size_groups"): "relation_value",
    ("cluster", "duplicate_groups"): "relation_value",
    ("cluster", "unique_sha256_count"): "relation_value",
    ("cluster", "duplicate_group_count"): "relation_value",
    ("cluster", "duplicate_member_count"): "relation_value",
    ("cluster", "largest_group_size"): "relation_value",
    ("cluster", "singleton_ids"): "relation_value",
    ("cluster", "member_count"): "relation_value",
    ("dedup", "identical_sha256_groups"): "relation_value",
    ("dedup", "identical_md5_groups"): "relation_value",
    ("dedup", "identical_sha1_groups"): "relation_value",
    ("dedup", "identical_sha512_groups"): "relation_value",
    ("dedup", "identical_size_groups"): "relation_value",
    ("dedup", "duplicate_groups"): "relation_value",
    ("dedup", "unique_sha256_count"): "relation_value",
    ("dedup", "duplicate_group_count"): "relation_value",
    ("dedup", "duplicate_member_count"): "relation_value",
    ("dedup", "largest_group_size"): "relation_value",
    ("dedup", "singleton_ids"): "relation_value",
    ("dedup", "member_count"): "relation_value",
    ("inventory", "identical_sha256_groups"): "relation_value",
    ("inventory", "identical_md5_groups"): "relation_value",
    ("inventory", "identical_sha1_groups"): "relation_value",
    ("inventory", "identical_sha512_groups"): "relation_value",
    ("inventory", "identical_size_groups"): "relation_value",
    ("inventory", "duplicate_groups"): "relation_value",
    ("inventory", "unique_sha256_count"): "relation_value",
    ("inventory", "duplicate_group_count"): "relation_value",
    ("inventory", "duplicate_member_count"): "relation_value",
    ("inventory", "largest_group_size"): "relation_value",
    ("inventory", "singleton_ids"): "relation_value",
    ("inventory", "member_count"): "relation_value",
}

_CACHE = {}   # container sha256 -> [(label, raw bytes)] | None
_LIST_KEYS = ("artifacts", "members", "files", "entries", "items")
_PATH_KEYS = ("path", "filename", "file", "name", "member", "member_path")


def _manifest_artifacts(raw):
    """The artifact dicts of a delivery-manifest json blob, or None when it is not one."""
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


def _raw_read(data, zi):
    """A member's bytes straight from its local header (no CRC check), or None."""
    off = zi.header_offset
    if data[off:off + 4] != b"PK\x03\x04":
        return None
    nlen, xlen = struct.unpack_from("<HH", data, off + 26)
    start = off + 30 + nlen + xlen
    comp = data[start:start + zi.compress_size]
    if zi.compress_type == 0:
        return bytes(comp)
    if zi.compress_type == 8:
        return zlib.decompressobj(-15).decompress(comp)
    if zi.compress_type == 12:
        import bz2
        return bz2.decompress(comp)
    if zi.compress_type == 14:
        import lzma
        psize, = struct.unpack_from("<H", comp, 2)
        props = lzma._decode_filter_properties(lzma.FILTER_LZMA1, comp[4:4 + psize])
        return lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[props]).decompress(comp[4 + psize:])
    return None


def _read(z, zi, data):
    try:
        return z.read(zi)
    except (RuntimeError, NotImplementedError):          # encrypted member: the password-aware read
        try:
            from lib.common import read_member
            return read_member(io.BytesIO(data), zi.filename)
        except Exception:  # noqa: BLE001
            return None
    except Exception:  # noqa: BLE001 - bad CRC / damaged stream on the OUTER zip
        try:
            return _raw_read(data, zi)
        except Exception:  # noqa: BLE001
            return None


def _members(data):
    """[(label, bytes)] of the cluster zip's artifacts, or None for a non-zip."""
    if not data or data[:2] != b"PK":
        return None
    key = hashlib.sha256(data).hexdigest()
    if key in _CACHE:
        return _CACHE[key]
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        infos = [zi for zi in z.infolist() if not zi.is_dir() and not zi.filename.endswith(("/", "\\"))]
    except Exception:  # noqa: BLE001 - not a zip
        _CACHE[key] = None
        return None
    ids, manifests = {}, set()
    for zi in infos:
        base = zi.filename.replace("\\", "/").rsplit("/", 1)[-1].lower()
        if not base.endswith(".json") or not ("manifest" in base or base == "index.json"):
            continue
        raw = _read(z, zi, data)
        arts = _manifest_artifacts(raw) if raw is not None else None
        if arts is None:
            if "manifest" in base:
                manifests.add(zi.filename)   # a *manifest*.json is never an artifact, even unparsable
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
        b = _read(z, zi, data)
        if b is None:
            _CACHE[key] = None
            return None
        path = zi.filename.replace("\\", "/")
        base = path.rsplit("/", 1)[-1]
        label = ids.get(zi.filename) or ids.get(path) or ids.get(base)
        if label is None:
            label = base.rsplit(".", 1)[0] if "." in base.lstrip(".") else base
        out.append((label, b))
    if len(_CACHE) > 64:
        _CACHE.clear()
    _CACHE[key] = out
    return out


def _classes(members, kind):
    keyf = {"md5": lambda b: hashlib.md5(b).hexdigest(), "sha1": lambda b: hashlib.sha1(b).hexdigest(),
            "sha512": lambda b: hashlib.sha512(b).hexdigest(), "size": len}.get(
        kind, lambda b: hashlib.sha256(b).hexdigest())
    cls = {}
    for label, b in members:
        cls.setdefault(keyf(b), []).append(label)
    return list(cls.values())


def _kind(field):
    for k in ("sha512", "sha256", "sha1", "md5"):
        if k in field:
            return k
    return "size" if field.startswith(("identical_size", "unique_size", "duplicate_size")) else "sha256"


def relation_value(data, ctx):
    ctx = ctx or {}
    field = ctx.get("field") or ""
    asked = ctx.get("asked") or field
    members = _members(data)
    if members is None:
        return "none"
    cls = _classes(members, _kind(field))
    groups = sorted(sorted(g) for g in cls if len(g) > 1)
    if field.endswith("_groups"):
        return groups
    if field in ("unique_member_ids", "singleton_ids"):
        return sorted(g[0] for g in cls if len(g) == 1)
    if field == "singleton_count":
        return sum(1 for g in cls if len(g) == 1)
    if field in ("duplicate_ids", "duplicate_member_ids"):
        return sorted(x for g in groups for x in g)
    if field.startswith(("unique_", "distinct_")) and field.endswith("_count"):
        return len(cls)
    if field in ("duplicate_group_count", "identical_group_count"):
        return len(groups)
    if field in ("duplicate_member_count_redundant", "redundant_member_count", "redundant_copy_count",
                 "duplicate_copy_count"):
        return sum(len(g) - 1 for g in groups)
    if field.startswith("duplicate_member_count"):   # members in a duplicate group (in_groups) unless asked redundant
        if any(w in asked for w in ("redundant", "extra", "minus", "excess")):
            return sum(len(g) - 1 for g in groups)
        return sum(len(g) for g in groups)
    if field.startswith("largest_"):
        return max((len(g) for g in cls), default=0)
    if field == "member_count":
        return len(members)
    if field == "member_ids":
        return sorted(lbl for lbl, _ in members)
    return None
