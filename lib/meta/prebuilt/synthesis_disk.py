"""Cross-IMAGE GPT integrity synthesis (prebuilt, SPECULATIVE). Coverage-atlas row "disk-rebuilt-integrity": 'Prove
which image was rebuilt from an incomplete source' over several raw disk images. Members = the question's
`Files: [...]` list (read through ctx["read"]), else every member of the container zip (`data`), zip order.
Per member prebuilt/disk_integrity.analyse() (members with no GPT header take no part). Status per image:
intact / rebuilt / truncated / crc_mismatch (see disk_integrity.py).
  rebuilt_image (and aliases) = the member whose backup/CRC/size claims are inconsistent: the lone non-`intact`
    image; several -> the one whose status is `rebuilt`, else a JSON list of the non-intact names (stored order);
  truncated_image / crc_mismatch_image = the member(s) with that exact status (one -> name, several -> list);
  image_integrity_status_map = {member: status} (stored order); intact_images = names of the intact ones.
No GPT image in the set -> "none" (zip input) / None (cannot read).
ORDER / GROUP / HASH fields over the same member set (prebuilt/disk_layout.layout() per member, after unwrap; a member
with no MBR/GPT table takes no part -- it is left out of orders and groups):
  partition_count_order / first_start_lba_order (start LBA of the FIRST used entry in TABLE order) / image_size_order
    (member byte length, as `ls -l` shows it) / disk_guid_order (GPT disk GUID lowercase canonical; MBR images sort
    after the GPT ones) = member names ascending by that key, ties by name; "descending" / "largest first" / "most
    partitions first" in the text reverses the key (ties still by name);
  layout_groups (and aliases) = members with an IDENTICAL partition layout (same (start, end) LBA sequence, same
    sector size), each group's names sorted, groups sorted by their first name, compact JSON array of arrays (single
    images form their own group); layout_group_count = how many groups;
  partition_sha256_map = {member: [sha256 hex of each used partition's byte range, TABLE order]} (only the bytes
    present in the image are hashed: a partition cut by EOF hashes its stub); disk.partition_sha256_sequence = the
    same list for ONE image;
  rebuilt_image fallback: when the GPT integrity checks single nobody out (all intact / MBR-only set) or name several,
  the member whose layout matches another member's but whose partition contents are all zero or cut by EOF while
  the twin's are not ("rebuilt from an incomplete source") is the rebuilt one; rebuilt_images = all such, sorted.
Per-image facts are cached by the bytes' blake2b digest (never id(), D25: Mastery sets share pool processes)."""

import hashlib
import re

FIELDS = {
    ("synthesis", "rebuilt_image"): "disk_synthesis_value",
    ("synthesis", "rebuilt_image_member"): "disk_synthesis_value",
    ("synthesis", "rebuilt_image_filename"): "disk_synthesis_value",
    ("synthesis", "rebuilt_disk_image"): "disk_synthesis_value",
    ("synthesis", "rebuilt_member_image"): "disk_synthesis_value",
    ("synthesis", "inconsistent_image"): "disk_synthesis_value",
    ("synthesis", "inconsistent_image_member"): "disk_synthesis_value",
    ("synthesis", "truncated_image"): "disk_synthesis_value",
    ("synthesis", "truncated_image_member"): "disk_synthesis_value",
    ("synthesis", "crc_mismatch_image"): "disk_synthesis_value",
    ("synthesis", "image_integrity_status_map"): "disk_synthesis_value",
    ("synthesis", "image_integrity_map"): "disk_synthesis_value",
    ("synthesis", "intact_images"): "disk_synthesis_value",
    ("synthesis", "rebuilt_images"): "disk_synthesis_value",
    ("synthesis", "partition_count_order"): "disk_synthesis_value",
    ("synthesis", "partition_count_order_images"): "disk_synthesis_value",
    ("synthesis", "first_start_lba_order"): "disk_synthesis_value",
    ("synthesis", "first_partition_start_lba_order"): "disk_synthesis_value",
    ("synthesis", "first_partition_lba_order"): "disk_synthesis_value",
    ("synthesis", "start_lba_order"): "disk_synthesis_value",
    ("synthesis", "partition_start_lba_order"): "disk_synthesis_value",
    ("synthesis", "image_size_order"): "disk_synthesis_value",
    ("synthesis", "image_size_bytes_order"): "disk_synthesis_value",
    ("synthesis", "disk_size_order"): "disk_synthesis_value",
    ("synthesis", "disk_guid_order"): "disk_synthesis_value",
    ("synthesis", "layout_groups"): "disk_synthesis_value",
    ("synthesis", "partition_layout_groups"): "disk_synthesis_value",
    ("synthesis", "identical_layout_groups"): "disk_synthesis_value",
    ("synthesis", "same_layout_groups"): "disk_synthesis_value",
    ("synthesis", "layout_group_count"): "disk_synthesis_value",
    ("synthesis", "partition_layout_group_count"): "disk_synthesis_value",
    ("synthesis", "partition_sha256_map"): "disk_synthesis_value",
    ("synthesis", "partition_sha256_sequence"): "disk_synthesis_value",
    ("synthesis", "partition_sha256_sequences"): "disk_synthesis_value",
    ("synthesis", "partition_hash_map"): "disk_synthesis_value",
    ("disk", "partition_sha256_sequence"): "partition_sha256_value",
    ("disk", "partition_sha256_list"): "partition_sha256_value",
    ("disk", "partition_sha256s"): "partition_sha256_value",
    ("disk", "partition_content_sha256_sequence"): "partition_sha256_value",
    ("dd", "partition_sha256_sequence"): "partition_sha256_value",
    ("image", "partition_sha256_sequence"): "partition_sha256_value",
    ("gpt", "partition_sha256_sequence"): "partition_sha256_value",
}

_DESC = re.compile(r"\b(descending|largest first|biggest first|highest first|most partitions first|"
                   r"reverse order)\b", re.I)
_CACHE = {}


def _facts(b):
    """{"key": layout key, "count", "first", "size", "guid", "sha": [...], "zero": [...], "cut": [...]} of one member,
    or None (no partition table). Cached by content digest."""
    b = bytes(b)
    dg = hashlib.blake2b(b, digest_size=20).digest() + len(b).to_bytes(8, "little")
    if dg in _CACHE:
        return _CACHE[dg]
    from .disk_layout import _unwrap, layout
    f = None
    img = _unwrap(b)
    L = layout(img) if img else None
    if L is not None and L["parts"]:
        ss, n = L["ss"], len(img)
        sha, zero, cut = [], [], []
        for p in L["parts"]:
            a, z = p["start"] * ss, (p["end"] + 1) * ss
            seg = bytes(img[a:min(z, n)]) if a < n else b""
            sha.append(hashlib.sha256(seg).hexdigest())
            zero.append(seg.count(0) == len(seg))
            cut.append(z > n)
        f = {"key": (ss, tuple((p["start"], p["end"]) for p in L["parts"])), "count": len(L["parts"]),
             "first": L["parts"][0]["start"], "size": len(b), "guid": L.get("disk_guid"), "sha": sha,
             "zero": zero, "cut": cut}
    if len(_CACHE) > 64:
        _CACHE.clear()
    _CACHE[dg] = f
    return f


def partition_sha256_value(data, ctx):
    """disk.partition_sha256_sequence: sha256 of each used partition's bytes, TABLE order (no table -> "none")."""
    if data is None:
        return None
    try:
        f = _facts(data)
        return "none" if f is None else list(f["sha"])
    except Exception:  # noqa: BLE001
        return None


def _content_rebuilt(fx):
    """Members whose layout twins another member's but whose partitions are all zero / cut by EOF where the twin's
    are not (sorted names)."""
    out = []
    for n, f in fx.items():
        twins = [g for m, g in fx.items() if m != n and g["key"] == f["key"]]
        if not twins:
            continue
        bad = [i for i in range(f["count"]) if f["zero"][i] or f["cut"][i]]
        if bad and any(any(not (g["zero"][i] or g["cut"][i]) and g["sha"][i] != f["sha"][i] for i in bad)
                       for g in twins):
            out.append(n)
    return sorted(out)


def _order(fx, field, question):
    k = {"partition_count": "count", "first_start": "first", "first_partition": "first", "start_lba": "first",
         "partition_start": "first", "image_size": "size", "disk_size": "size", "disk_guid": "guid"}
    key = next(v for p, v in k.items() if field.startswith(p))
    desc = bool(_DESC.search((question or {}).get("question") or "")) or "descending" in field
    if key == "guid":   # MBR images (no disk GUID) after the GPT ones, by name
        have = sorted((n for n in fx if fx[n]["guid"]), key=lambda n: (fx[n]["guid"], n))
        if desc:
            have.sort(key=lambda n: fx[n]["guid"], reverse=True)
        return have + sorted(n for n in fx if not fx[n]["guid"])
    names = sorted(fx)
    names.sort(key=lambda n: fx[n][key], reverse=desc)   # stable: ties keep name order
    return names


def _layout_value(fx, field, question):
    if field.endswith("_order") or field.endswith("_order_images"):
        return _order(fx, field.replace("_order_images", "_order"), question)
    if field.startswith("partition_sha256") or field == "partition_hash_map":
        return {n: list(f["sha"]) for n, f in fx.items()}
    groups = {}
    for n in sorted(fx):
        groups.setdefault(fx[n]["key"], []).append(n)
    gl = sorted(groups.values())
    if field.endswith("_count"):
        return len(gl)
    return gl



def _one(names):
    return names[0] if len(names) == 1 else (names or "none")


def disk_synthesis_value(data, ctx):
    """synthesis.<multi-image integrity field> (see the module docstring)."""
    try:
        from .synthesis_media import _source
        from .disk_integrity import analyse
        src = _source(data, ctx)
        if src is None:
            return None
        read, names, from_zip = src
        field = ctx.get("field") or ""
        blobs = {}
        for n in names or []:
            b = read(n)
            if b:
                blobs[n] = bytes(b)
        if field in _LAYOUT_FIELDS:
            fx = {n: f for n, f in ((n, _facts(b)) for n, b in blobs.items()) if f is not None}
            if not fx:
                return "none" if from_zip else None
            return _layout_value(fx, field, ctx.get("question"))
        st = {}
        for n, b in blobs.items():
            f = analyse(b)
            if f is not None:
                st[n] = f["status"]
        if field in ("rebuilt_image", "rebuilt_images", "rebuilt_image_member", "rebuilt_image_filename",
                     "rebuilt_disk_image", "rebuilt_member_image"):
            bad = [n for n, s in st.items() if s != "intact"]
            reb = [n for n in bad if st[n] == "rebuilt"]
            if len(bad) != 1 and len(reb) != 1:
                fx = {n: f for n, f in ((n, _facts(b)) for n, b in blobs.items()) if f is not None}
                cr = _content_rebuilt(fx)
                if bad:
                    cr = [n for n in cr if n in bad] or cr
                if field == "rebuilt_images":
                    return cr or sorted(bad) or "none"
                if len(cr) == 1:
                    return cr[0]
                if cr:
                    return cr
            if field == "rebuilt_images":
                return sorted(bad) or "none"
        if not st:
            return "none" if from_zip else None
        bad = [n for n, s in st.items() if s != "intact"]
        if field.endswith("_map"):
            return st
        if field == "intact_images":
            return [n for n, s in st.items() if s == "intact"]
        if field.startswith("truncated"):
            return _one([n for n, s in st.items() if s == "truncated"])
        if field.startswith("crc_mismatch"):
            return _one([n for n, s in st.items() if s == "crc_mismatch"])
        if len(bad) == 1:
            return bad[0]
        reb = [n for n in bad if st[n] == "rebuilt"]
        return reb[0] if len(reb) == 1 else (bad or "none")
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None


_LAYOUT_FIELDS = {k[1] for k, v in FIELDS.items() if k[0] == "synthesis" and v == "disk_synthesis_value"
                  and (k[1].endswith("_order") or k[1].endswith("_order_images") or "layout_group" in k[1]
                       or k[1].startswith("partition_sha256") or k[1] == "partition_hash_map")}
