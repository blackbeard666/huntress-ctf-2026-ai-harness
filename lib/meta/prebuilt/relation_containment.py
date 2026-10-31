"""Containment relations of a cluster zip (`cluster-NNN.zip`): which members are archives and what they hold, matched
to the other members by SHA-256. Speculative tier; sibling of the GM-verified relation.identical_sha256_groups
(lib/meta/relation.py) and of relation_near / relation_variants (same member set and labels).

Members: every non-directory entry of the cluster zip minus its delivery manifest; label = manifest `id` by path then
basename, else basename without extension (the D30-verified spelling). A member is a CONTAINER when its bytes open as
zip / gzip / tar / bz2 / xz (a compressed tar is one container; a zip entry with a bad CRC is raw-read from its local header: skip 30+n+e, inflate -15;
a gzip with a bad trailer is raw-inflated). Containers are walked recursively, at most 3 levels below the member.
An inner entry is labelled by the corpus label of the member whose sha256 equals its bytes (smallest label when
several), else by its inner name. D30 timed shape: inner zips each hold ONE `<word>.txt` matching no other member.
  containment_pairs: [[container, contained]] (direct parent -> child) sorted; container = member label, or
    `<member>/<inner path>` for a nested archive; contained = matching member label else the bare inner name.
  containment_map: {container: [contained, ...]} with the same spellings, lists sorted.
  contained_ids: sorted labels of members whose sha256 appears inside ANOTHER member (any depth).
  container_ids: sorted labels of members that are archives holding >= 1 file.
  containing_ids: containers that hold >= 1 other corpus member.
  nested_member_names: sorted `<member>/<inner path>` of every inner file (nested: `<member>/<a.zip>/<b.txt>`);
    nested_file_names: the bare inner names sorted (duplicates kept).
  nested_sha256s: sorted unique sha256 of every inner file.
  max_nesting_depth: 0 when no member is a container, 1 for a member holding files, +1 per nested archive level.
  orphan_inner_members: sorted `<member>/<inner path>` of inner files matching no corpus member.
  *_count: len of the list. Non-zip cluster -> "none". One parse per container sha256 (never id())."""
import hashlib
import io
import json
import struct
import zlib

FIELDS = {
    ("relation", "containment_pairs"): "containment_value",
    ("relation", "containment_pair_count"): "containment_value",
    ("relation", "containment_edges"): "containment_value",
    ("relation", "containment_relations"): "containment_value",
    ("relation", "containment_map"): "containment_value",
    ("relation", "containment"): "containment_value",
    ("relation", "contained_ids"): "containment_value",
    ("relation", "contained_member_ids"): "containment_value",
    ("relation", "contained_members"): "containment_value",
    ("relation", "contained_count"): "containment_value",
    ("relation", "container_ids"): "containment_value",
    ("relation", "container_member_ids"): "containment_value",
    ("relation", "container_members"): "containment_value",
    ("relation", "container_count"): "containment_value",
    ("relation", "archive_member_ids"): "containment_value",
    ("relation", "containing_ids"): "containment_value",
    ("relation", "containing_member_ids"): "containment_value",
    ("relation", "nested_member_names"): "containment_value",
    ("relation", "nested_member_count"): "containment_value",
    ("relation", "nested_file_names"): "containment_value",
    ("relation", "inner_member_names"): "containment_value",
    ("relation", "inner_file_names"): "containment_value",
    ("relation", "nested_sha256s"): "containment_value",
    ("relation", "nested_sha256_list"): "containment_value",
    ("relation", "inner_sha256s"): "containment_value",
    ("relation", "max_nesting_depth"): "containment_value",
    ("relation", "nesting_depth"): "containment_value",
    ("relation", "max_depth"): "containment_value",
    ("relation", "orphan_inner_members"): "containment_value",
    ("relation", "orphan_inner_member_names"): "containment_value",
    ("relation", "orphan_inner_count"): "containment_value",
    ("relation", "orphan_nested_members"): "containment_value",
}

_CACHE = {}   # container sha256 -> analysis dict | None
_LIST_KEYS = ("artifacts", "members", "files", "entries", "items")
_PATH_KEYS = ("path", "filename", "file", "name", "member", "member_path")
_MAX_DEPTH = 3


def _lfh_data(buf, zi):
    """An entry's data straight from its local header, no CRC check; None on failure."""
    off = zi.header_offset
    if buf[off:off + 4] != b"PK\x03\x04":
        return None
    nlen, xlen = struct.unpack_from("<HH", buf, off + 26)
    comp = buf[off + 30 + nlen + xlen:off + 30 + nlen + xlen + zi.compress_size]
    if zi.compress_type == 0:
        return bytes(comp)
    if zi.compress_type == 8:
        return zlib.decompressobj(-15).decompress(comp)
    if zi.compress_type == 12:
        import bz2
        return bz2.decompress(comp)
    return None


def _zip_entries(buf):
    """[(name, bytes)] of a zip blob (raw local-header read on bad CRC), or None."""
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(buf))
        infos = [zi for zi in z.infolist() if not zi.is_dir() and not zi.filename.endswith(("/", "\\"))]
    except Exception:  # noqa: BLE001 - not a zip
        return None
    out = []
    for zi in infos:
        try:
            b = z.read(zi)
        except (RuntimeError, NotImplementedError):          # encrypted: the password-aware read
            try:
                from lib.common import read_member
                b = read_member(io.BytesIO(buf), zi.filename)
            except Exception:  # noqa: BLE001
                b = None
        except Exception:  # noqa: BLE001 - bad CRC / name mismatch: raw local-header bytes
            try:
                b = _lfh_data(buf, zi)
            except Exception:  # noqa: BLE001
                b = None
        if b is not None:
            out.append((zi.filename.replace("\\", "/"), b))
    return out


def _gzip_entries(buf, label):
    """[(FNAME or label, bytes)] of a gzip blob (raw inflate on a bad trailer), or None."""
    if len(buf) < 18 or buf[:3] != b"\x1f\x8b\x08":
        return None
    flg, pos = buf[3], 10
    name = None
    try:
        if flg & 4:
            xlen, = struct.unpack_from("<H", buf, pos)
            pos += 2 + xlen
        if flg & 8:
            end = buf.index(b"\x00", pos)
            name = buf[pos:end].decode("latin-1")
            pos = end + 1
        if flg & 16:
            pos = buf.index(b"\x00", pos) + 1
        if flg & 2:
            pos += 2
        d = zlib.decompressobj(-15).decompress(buf[pos:])
    except Exception:  # noqa: BLE001 - broken gzip
        return None
    if not name:
        base = label.rsplit("/", 1)[-1]
        name = base[:-3] if base.lower().endswith(".gz") else base
    return [(name, d)]


def _tar_entries(buf):
    if len(buf) < 512 or buf[257:262] != b"ustar":
        return None
    import tarfile
    try:
        out = []
        with tarfile.open(fileobj=io.BytesIO(buf), mode="r:") as t:
            for m in t.getmembers():
                if m.isfile():
                    f = t.extractfile(m)
                    out.append((m.name, f.read() if f else b""))
        return out
    except Exception:  # noqa: BLE001 - broken tar
        return None


def _entries(buf, label):
    """[(inner name, bytes)] when buf is an archive/compressed blob, else None. A compressed tar (.tgz / .tar.bz2 /
    .tar.xz) is ONE container: its tar entries, not a single decompressed .tar child."""
    ents = _entries1(buf, label)
    if ents and len(ents) == 1 and buf[:2] != b"PK":
        tar = _tar_entries(ents[0][1])
        if tar is not None:
            return tar
    return ents


def _entries1(buf, label):
    if buf[:4] == b"PK\x03\x04" or buf[:4] == b"PK\x05\x06":
        return _zip_entries(buf)
    if buf[:2] == b"\x1f\x8b":
        return _gzip_entries(buf, label)
    if buf[:3] == b"BZh":
        import bz2
        try:
            return [(label.rsplit("/", 1)[-1].rsplit(".", 1)[0], bz2.decompress(buf))]
        except Exception:  # noqa: BLE001
            return None
    if buf[:6] == b"\xfd7zXZ\x00":
        import lzma
        try:
            return [(label.rsplit("/", 1)[-1].rsplit(".", 1)[0], lzma.decompress(buf))]
        except Exception:  # noqa: BLE001
            return None
    return _tar_entries(buf)


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


def _members(data):
    """[(label, bytes)] of the cluster zip minus its manifest, or None for a non-zip."""
    ents = _zip_entries(data)
    if ents is None:
        return None
    ids, manifests = {}, set()
    for name, raw in ents:
        base = name.rsplit("/", 1)[-1].lower()
        if not base.endswith(".json") or not ("manifest" in base or base == "index.json"):
            continue
        arts = _manifest_artifacts(raw)
        if arts is None:
            if "manifest" in base:
                manifests.add(name)
            continue
        manifests.add(name)
        for a in arts:
            if a.get("id") is None:
                continue
            for k in _PATH_KEYS:
                if isinstance(a.get(k), str) and a[k]:
                    ids.setdefault(a[k].replace("\\", "/"), str(a["id"]))
    out = []
    for name, b in ents:
        if name in manifests:
            continue
        base = name.rsplit("/", 1)[-1]
        label = ids.get(name) or ids.get(base)
        if label is None:
            label = base.rsplit(".", 1)[0] if "." in base.lstrip(".") else base
        out.append((label, b))
    return out


def _analyse(data):
    mem = _members(data)
    if mem is None:
        return None
    by_sha = {}
    for label, b in mem:
        by_sha.setdefault(hashlib.sha256(b).hexdigest(), []).append(label)
    pairs, inner, contained, containers, containing = set(), [], set(), set(), set()
    state = {"depth": 0}

    def walk(top, path, buf, depth):
        ents = _entries(buf, path)
        if not ents:
            return False
        state["depth"] = max(state["depth"], depth)
        for name, b in ents:
            sha = hashlib.sha256(b).hexdigest()
            full = path + "/" + name
            others = sorted(x for x in by_sha.get(sha, []) if x != top)
            inner.append((full, name, sha, bool(others)))
            if others:
                contained.update(others)
                containing.add(top)
                pairs.add((path, others[0]))
            else:
                pairs.add((path, name))
            if depth < _MAX_DEPTH:
                walk(top, full, b, depth + 1)
        return True

    for label, b in mem:
        if walk(label, label, b, 1):
            containers.add(label)
    cmap = {}
    for a, b in sorted(pairs):
        cmap.setdefault(a, []).append(b)
    return {
        "pairs": [list(p) for p in sorted(pairs)],
        "map": cmap,
        "contained": sorted(contained),
        "containers": sorted(containers),
        "containing": sorted(containing),
        "nested_names": sorted(f for f, _, _, _ in inner),
        "nested_bare": sorted(n for _, n, _, _ in inner),
        "nested_sha": sorted({s for _, _, s, _ in inner}),
        "depth": state["depth"],
        "orphans": sorted(f for f, _, _, m in inner if not m),
    }


def _get(data):
    key = hashlib.sha256(data).hexdigest()
    if key not in _CACHE:
        try:
            _CACHE[key] = _analyse(data)
        except Exception:  # noqa: BLE001 - never raise past the extractor
            _CACHE[key] = None
    return _CACHE[key]


_KEY = {
    "containment_pairs": "pairs", "containment_edges": "pairs", "containment_relations": "pairs",
    "containment_pair_count": "#pairs",
    "containment_map": "map", "containment": "map",
    "contained_ids": "contained", "contained_member_ids": "contained", "contained_members": "contained",
    "contained_count": "#contained",
    "container_ids": "containers", "container_member_ids": "containers", "container_members": "containers",
    "archive_member_ids": "containers", "container_count": "#containers",
    "containing_ids": "containing", "containing_member_ids": "containing",
    "nested_member_names": "nested_names", "nested_member_count": "#nested_names",
    "nested_file_names": "nested_bare", "inner_member_names": "nested_bare", "inner_file_names": "nested_bare",
    "nested_sha256s": "nested_sha", "nested_sha256_list": "nested_sha", "inner_sha256s": "nested_sha",
    "max_nesting_depth": "depth", "nesting_depth": "depth", "max_depth": "depth",
    "orphan_inner_members": "orphans", "orphan_inner_member_names": "orphans", "orphan_nested_members": "orphans",
    "orphan_inner_count": "#orphans",
}


def containment_value(data, ctx):
    if not data or data[:2] != b"PK":
        return "none"
    an = _get(data)
    if an is None:
        return "none"
    key = _KEY.get((ctx or {}).get("field") or "")
    if key is None:
        return None
    if key.startswith("#"):
        return len(an[key[1:]])
    return an[key]
