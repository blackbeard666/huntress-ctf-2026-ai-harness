"""Semantic-identity groups of a cluster zip (`cluster-NNN.zip`): members equal after a format-aware normalization -- the
D30 flavor's "semantic identity" beside the GM-verified exact relation.identical_sha256_groups (lib/meta/relation.py).
Speculative tier.

Members/labels as relation_variants: every non-directory entry at any depth minus the delivery manifest
(`*manifest*.json`, or an `index.json` that parses as an artifact list); label = manifest `id` by member path then
basename, else the basename without extension. D30 clusters carry five families (manifest `family`): text (.txt),
script (.ps1), json, png, zip -- each a template plus `duplicate_ref` copies.

Canonical key per member, chosen by MAGIC (not by extension):
  PNG  (89 50 4E 47): decoded pixels (Pillow: size + RGBA bytes) -- so recompressed / refiltered copies and copies
       with tEXt/iTXt/zTXt/tIME added or chunks reordered collapse; fallback IHDR + PLTE + tRNS + inflated IDAT.
  JPEG (FF D8 FF): every marker segment except APPn (E0..EF) and COM (FE), then the bytes from the first SOS through
       the first EOI after it (trailing bytes ignored).
  zip  (PK 03 04 / PK 05 06): sorted (name, sha256(data)) of the file entries -- timestamps, extra fields, comments,
       compression method and entry order ignored; a bad stored CRC is re-read raw from the local header.
  gzip (1F 8B): the canonical key of the decompressed payload (gzip header name/mtime ignored), tagged gzip.
  text (valid UTF-8 / BOM-marked UTF-16, no NUL): BOM stripped, CRLF/CR -> LF, each line rstripped, trailing newlines
       stripped, case kept. JSON is recognized inside text: a leading object/array (json raw_decode, so the D30 template
       `{...}\\n` + LF with its literal backslash-n still parses) -> dumps(sort_keys, compact) + the normalized remainder.
  anything else: sha256 of the raw bytes.
Fields (groups of >= 2, each sorted, groups sorted -> compact JSON; non-zip -> "none"):
  semantic_identity_groups (+ semantically_identical_groups, semantic_groups, normalized_content_groups, ...): all
    families; canonical_json_groups: json-keyed members only; normalized_text_groups: text-keyed (txt/ps1/csv);
    pixel_identical_groups: png/jpeg; same_content_different_hash_groups: semantic groups holding >= 2 distinct
    sha256 (i.e. NOT a pure exact group). *_count: the number of such groups; semantic_unique_count: distinct keys.
One parse per container sha256 (never id())."""
import hashlib
import io
import json
import struct
import zlib

FIELDS = {
    ("relation", "semantically_identical_groups"): "semantic_value",
    ("relation", "semantic_groups"): "semantic_value",
    ("relation", "semantic_duplicate_groups"): "semantic_value",
    ("relation", "semantic_equivalence_groups"): "semantic_value",
    ("relation", "semantically_equivalent_groups"): "semantic_value",
    ("relation", "semantic_identity_groups"): "semantic_value",
    ("relation", "normalized_content_groups"): "semantic_value",
    ("relation", "normalized_identical_groups"): "semantic_value",
    ("relation", "canonical_content_groups"): "semantic_value",
    ("relation", "content_equivalent_groups"): "semantic_value",
    ("relation", "canonical_json_groups"): "semantic_value",
    ("relation", "json_canonical_groups"): "semantic_value",
    ("relation", "normalized_json_groups"): "semantic_value",
    ("relation", "normalized_text_groups"): "semantic_value",
    ("relation", "text_normalized_groups"): "semantic_value",
    ("relation", "pixel_identical_groups"): "semantic_value",
    ("relation", "identical_pixel_groups"): "semantic_value",
    ("relation", "image_pixel_groups"): "semantic_value",
    ("relation", "same_content_different_hash_groups"): "semantic_value",
    ("relation", "semantic_only_groups"): "semantic_value",
    ("relation", "semantic_not_exact_groups"): "semantic_value",
    ("relation", "semantic_identity_group_count"): "semantic_value",
    ("relation", "semantic_group_count"): "semantic_value",
    ("relation", "same_content_different_hash_group_count"): "semantic_value",
    ("relation", "semantic_unique_count"): "semantic_value",
    ("relation", "unique_semantic_count"): "semantic_value",
    ("corpus", "semantic_identity_groups"): "semantic_value",
    ("corpus", "same_content_different_hash_groups"): "semantic_value",
    ("cluster", "semantic_identity_groups"): "semantic_value",
    ("cluster", "same_content_different_hash_groups"): "semantic_value",
    ("dedup", "semantic_identity_groups"): "semantic_value",
    ("dedup", "same_content_different_hash_groups"): "semantic_value",
    ("inventory", "semantic_identity_groups"): "semantic_value",
    ("inventory", "same_content_different_hash_groups"): "semantic_value",
}

_CACHE = {}   # container sha256 -> [(label, sha256 hex, (family, key))] | None
_LIST_KEYS = ("artifacts", "members", "files", "entries", "items")
_PATH_KEYS = ("path", "filename", "file", "name", "member", "member_path")
_MAX_INFLATE = 64 << 20


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


def _raw_read(data, zi):
    """A zip entry's bytes straight from its local header (no CRC check), or None."""
    off = zi.header_offset
    if data[off:off + 4] != b"PK\x03\x04":
        return None
    nlen, xlen = struct.unpack_from("<HH", data, off + 26)
    start = off + 30 + nlen + xlen
    comp = data[start:start + zi.compress_size]
    if zi.compress_type == 0:
        return bytes(comp)
    if zi.compress_type == 8:
        return zlib.decompressobj(-15).decompress(comp, _MAX_INFLATE)
    return None


def _read(z, zi, data):
    try:
        return z.read(zi)
    except (RuntimeError, NotImplementedError):          # encrypted entry: the password-aware read
        try:
            from lib.common import read_member
            return read_member(io.BytesIO(data), zi.filename)
        except Exception:  # noqa: BLE001
            return None
    except Exception:  # noqa: BLE001 - bad CRC / damaged stream
        try:
            return _raw_read(data, zi)
        except Exception:  # noqa: BLE001
            return None


def _norm_text(s):
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(ln.rstrip() for ln in s.split("\n")).rstrip("\n")


def _decode_text(b):
    if b[:3] == b"\xef\xbb\xbf":
        b = b[3:]
    elif b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        try:
            return b.decode("utf-16")
        except UnicodeDecodeError:
            return None
    if b"\x00" in b:
        return None
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _text_key(b):
    s = _decode_text(b)
    if s is None:
        return None
    t = s.lstrip()
    if t[:1] in ("{", "["):
        try:
            obj, end = json.JSONDecoder().raw_decode(t)
            canon = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            return "json", (canon, _norm_text(t[end:]).strip())
        except ValueError:
            pass
    return "text", _norm_text(s)


def _png_key(b):
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(b))
        im.load()
        return "image", (im.size, im.convert("RGBA").tobytes())
    except Exception:  # noqa: BLE001 - Pillow refused it: the chunk-level key
        pass
    pos, keep, idat = 8, [], []
    while pos + 8 <= len(b):
        ln, = struct.unpack_from(">I", b, pos)
        typ, body = b[pos + 4:pos + 8], b[pos + 8:pos + 8 + ln]
        if typ in (b"IHDR", b"PLTE", b"tRNS"):
            keep.append(typ + body)
        elif typ == b"IDAT":
            idat.append(body)
        elif typ == b"IEND":
            break
        pos += 12 + ln
    try:
        pix = zlib.decompressobj().decompress(b"".join(idat), _MAX_INFLATE)
    except zlib.error:
        pix = b"".join(idat)
    return "image", (b"".join(keep), pix)


def _jpeg_key(b):
    pos, keep = 2, []
    while pos + 4 <= len(b):
        if b[pos] != 0xFF:
            return "image", b[2:]
        mk = b[pos + 1]
        if mk == 0xFF:                                   # fill byte
            pos += 1
            continue
        if mk == 0xD9:
            break
        if 0xD0 <= mk <= 0xD7 or mk == 0x01:
            pos += 2
            continue
        ln, = struct.unpack_from(">H", b, pos + 2)
        if mk == 0xDA:
            eoi = b.find(b"\xff\xd9", pos + 2 + ln)
            keep.append(b[pos:len(b) if eoi < 0 else eoi + 2])
            break
        if not (0xE0 <= mk <= 0xEF or mk == 0xFE):
            keep.append(b[pos:pos + 2 + ln])
        pos += 2 + ln
    return "image", b"".join(keep)


def _zip_key(b):
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(b))
        ents = []
        for zi in z.infolist():
            if zi.is_dir() or zi.filename.endswith(("/", "\\")):
                continue
            d = _read(z, zi, b)
            ents.append((zi.filename, hashlib.sha256(d).hexdigest() if d is not None else "?"))
    except Exception:  # noqa: BLE001 - not a readable zip
        return None
    return "zip", tuple(sorted(ents))


def _key(b, depth=0):
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return _png_key(b)
    if b[:3] == b"\xff\xd8\xff":
        return _jpeg_key(b)
    if b[:4] in (b"PK\x03\x04", b"PK\x05\x06"):
        k = _zip_key(b)
        if k:
            return k
    if b[:2] == b"\x1f\x8b" and depth < 3:
        import gzip
        try:
            fam, k = _key(gzip.decompress(b), depth + 1)
            return "gzip", (fam, k)
        except Exception:  # noqa: BLE001 - damaged gzip: raw bytes
            pass
    return _text_key(b) or ("bytes", hashlib.sha256(b).hexdigest())


def _members(data):
    """[(label, sha256, (family, key))] of the cluster zip's artifacts, or None for a non-zip."""
    if not data or data[:2] != b"PK":
        return None
    ck = hashlib.sha256(data).hexdigest()
    if ck in _CACHE:
        return _CACHE[ck]
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        infos = [zi for zi in z.infolist() if not zi.is_dir() and not zi.filename.endswith(("/", "\\"))]
    except Exception:  # noqa: BLE001 - not a zip
        _CACHE[ck] = None
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
        b = _read(z, zi, data)
        if b is None:
            _CACHE[ck] = None
            return None
        path = zi.filename.replace("\\", "/")
        base = path.rsplit("/", 1)[-1]
        label = ids.get(zi.filename) or ids.get(path) or ids.get(base)
        if label is None:
            label = base.rsplit(".", 1)[0] if "." in base.lstrip(".") else base
        try:
            key = _key(b)
        except Exception:  # noqa: BLE001 - a hostile member: identity by raw bytes
            key = ("bytes", hashlib.sha256(b).hexdigest())
        out.append((label, hashlib.sha256(b).hexdigest(), key))
    if len(_CACHE) > 64:
        _CACHE.clear()
    _CACHE[ck] = out
    return out


def _family_ok(field, fam):
    if "json" in field:
        return fam == "json"
    if "text" in field:
        return fam == "text"
    if "pixel" in field:
        return fam == "image"
    return True


def semantic_value(data, ctx):
    ctx = ctx or {}
    field = ctx.get("field") or ""
    members = _members(data)
    if members is None:
        return "none"
    cls = {}
    for label, sha, (fam, key) in members:
        if _family_ok(field, fam):
            cls.setdefault((fam, key), []).append((label, sha))
    groups = [g for g in cls.values() if len(g) > 1]
    if field.startswith(("same_content_different_hash", "semantic_only", "semantic_not_exact")):
        groups = [g for g in groups if len({sha for _, sha in g}) > 1]
    out = sorted(sorted(lbl for lbl, _ in g) for g in groups)
    if field.endswith("_groups"):
        return out
    if field.endswith("_group_count"):
        return len(out)
    if field in ("semantic_unique_count", "unique_semantic_count"):
        return len(cls)
    return None
