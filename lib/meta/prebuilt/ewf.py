"""EWF / Expert Witness (EnCase E01, SMART S01, logical L01) forensic image fields (fmt `ewf`, aliases `e01`,
`expert_witness`, `forensic_image`, `image`) -- prebuilt, SPECULATIVE (never asked yet).

Segment file: signature `EVF\\x09\\x0d\\x0a\\xff\\x00` (L01: `LVF...`) @0, fields_start u8 @8, segment number u16 @9.
Sections from @13: {type[16] NUL-padded, next u64 (absolute), size u64 (incl. the 76-byte descriptor), pad[40], adler32}.
  header   zlib -> ASCII "1\\r\\nmain\\r\\n<keys TAB>\\r\\n<values TAB>\\r\\n"; dates "YYYY M D h m s" (writer-local)
  header2  zlib -> UTF-16LE (BOM) "3\\nmain\\n<keys>\\n<values>\\n"; m/u = unix epoch seconds (UTC)
           keys: c case_number, n evidence_number, a description, e examiner_name, t notes, av software version,
           ov OS, m acquisition date, u system date, p password hash, md/sn model/serial
  volume/disk  E01 (1052 B): media_type u8 @0, chunk_count u32 @4, sectors_per_chunk @8, bytes_per_sector @12,
           sector_count u64 @16, media_flags u8 @36, compression_level u8 @52, error_granularity @56, set GUID @64.
           S01 (94 B): same first 16 bytes, sector_count u32 @16.
  table    entry_count u32 @0, base_offset u64 @8, adler32 @20, entries u32 from @24 (bit 31 = zlib-compressed,
           low 31 bits = offset relative to base). Uncompressed chunks carry a trailing adler32.
  hash     MD5[16] @0;  digest  MD5[16] @0 + SHA1[20] @16.   done = last segment, next = more segments follow.
acquisition_date / system_date: header2's unix epoch rendered ISO-8601 UTC ("...Z") when present (unambiguous);
else the header's stored local text rendered "YYYY-MM-DDTHH:MM:SS" with no zone (the format stores none).
computed_md5/sha1 inflate every chunk of THIS segment (a lone first segment of a multi-segment set -> None).
hash_matches = stored MD5 == computed MD5 ("Rebuilt from an incomplete source": stored hash no longer matches media).
EWF2 (Ex01/Lx01, `EVF2\\r\\n\\x81\\x00`) is recognised but not parsed (-> None). Split raw .001 members carry no
container metadata (plain bytes): not handled here.
Fixtures: ewfacquire 20140816 (ewf-tools deb) writer, pyewf (libewf-python) + ewfinfo/ewfverify oracles."""
import hashlib
import struct
import zlib
from datetime import datetime, timezone

from ..spell import Guid

_ALIASES = ("ewf", "e01", "expert_witness", "forensic_image", "image")
_STRICT = ("ewf", "e01", "expert_witness", "forensic_image")        # a non-EWF member under these fmts -> "none"

_NAMES = {
    "case_number": ("case_number",),
    "evidence_number": ("evidence_number",),
    "examiner_name": ("examiner_name", "examiner"),
    "description": ("description",),
    "notes": ("notes",),
    "acquisition_date": ("acquisition_date", "acquiry_date", "acquisition_date_utc", "acquisition_time_utc"),
    "system_date": ("system_date", "system_date_utc"),
    "acquisition_date_raw": ("acquisition_date_raw",),
    "acquisition_software": ("acquisition_software", "acquisition_software_version", "acquiry_software_version",
                             "software_version"),
    "acquisition_os": ("acquisition_os", "acquiry_operating_system", "operating_system"),
    "password_hash": ("password_hash",),
    "media_size_bytes": ("media_size_bytes", "media_size", "image_size_bytes"),
    "sector_count": ("sector_count", "number_of_sectors"),
    "bytes_per_sector": ("bytes_per_sector",),
    "sectors_per_chunk": ("sectors_per_chunk",),
    "chunk_count": ("chunk_count", "number_of_chunks"),
    "chunk_size_bytes": ("chunk_size_bytes", "chunk_size"),
    "error_granularity": ("error_granularity",),
    "media_type": ("media_type",),
    "compression_level": ("compression_level",),
    "set_identifier_guid": ("set_identifier_guid", "set_guid"),
    "stored_md5": ("stored_md5", "md5", "acquisition_md5", "stored_md5_hash"),
    "stored_sha1": ("stored_sha1", "sha1", "acquisition_sha1", "stored_sha1_hash"),
    "computed_md5": ("computed_md5", "calculated_md5", "media_md5", "computed_md5_hash"),
    "computed_sha1": ("computed_sha1", "calculated_sha1", "media_sha1"),
    "hash_matches": ("hash_matches", "md5_matches", "hash_verified", "md5_hash_matches", "integrity_valid"),
    "sha1_matches": ("sha1_matches",),
    "segment_number": ("segment_number",),
    "segment_count": ("segment_count", "number_of_segments"),
    "section_types": ("section_types", "section_names"),
}
# image.* is shared with picture formats: only the EWF-specific names go there (no md5/sha1/description/notes)
_IMAGE_SKIP = {"md5", "sha1", "description", "notes", "media_type", "media_size", "chunk_size"}

FIELDS = {
    ("ewf", "case_number"): "ewf_value", ("ewf", "evidence_number"): "ewf_value",
    ("ewf", "examiner_name"): "ewf_value", ("ewf", "examiner"): "ewf_value",
    ("ewf", "description"): "ewf_value", ("ewf", "notes"): "ewf_value",
    ("ewf", "acquisition_date"): "ewf_value", ("ewf", "acquiry_date"): "ewf_value",
    ("ewf", "acquisition_date_utc"): "ewf_value", ("ewf", "acquisition_time_utc"): "ewf_value",
    ("ewf", "system_date"): "ewf_value", ("ewf", "system_date_utc"): "ewf_value",
    ("ewf", "acquisition_date_raw"): "ewf_value",
    ("ewf", "acquisition_software"): "ewf_value", ("ewf", "acquisition_software_version"): "ewf_value",
    ("ewf", "acquiry_software_version"): "ewf_value", ("ewf", "software_version"): "ewf_value",
    ("ewf", "acquisition_os"): "ewf_value", ("ewf", "acquiry_operating_system"): "ewf_value",
    ("ewf", "operating_system"): "ewf_value", ("ewf", "password_hash"): "ewf_value",
    ("ewf", "media_size_bytes"): "ewf_value", ("ewf", "media_size"): "ewf_value",
    ("ewf", "image_size_bytes"): "ewf_value",
    ("ewf", "sector_count"): "ewf_value", ("ewf", "number_of_sectors"): "ewf_value",
    ("ewf", "bytes_per_sector"): "ewf_value", ("ewf", "sectors_per_chunk"): "ewf_value",
    ("ewf", "chunk_count"): "ewf_value", ("ewf", "number_of_chunks"): "ewf_value",
    ("ewf", "chunk_size_bytes"): "ewf_value", ("ewf", "chunk_size"): "ewf_value",
    ("ewf", "error_granularity"): "ewf_value", ("ewf", "media_type"): "ewf_value",
    ("ewf", "compression_level"): "ewf_value",
    ("ewf", "set_identifier_guid"): "ewf_value", ("ewf", "set_guid"): "ewf_value",
    ("ewf", "stored_md5"): "ewf_value", ("ewf", "md5"): "ewf_value", ("ewf", "acquisition_md5"): "ewf_value",
    ("ewf", "stored_md5_hash"): "ewf_value",
    ("ewf", "stored_sha1"): "ewf_value", ("ewf", "sha1"): "ewf_value", ("ewf", "acquisition_sha1"): "ewf_value",
    ("ewf", "stored_sha1_hash"): "ewf_value",
    ("ewf", "computed_md5"): "ewf_value", ("ewf", "calculated_md5"): "ewf_value", ("ewf", "media_md5"): "ewf_value",
    ("ewf", "computed_md5_hash"): "ewf_value",
    ("ewf", "computed_sha1"): "ewf_value", ("ewf", "calculated_sha1"): "ewf_value",
    ("ewf", "media_sha1"): "ewf_value",
    ("ewf", "hash_matches"): "ewf_value", ("ewf", "md5_matches"): "ewf_value", ("ewf", "hash_verified"): "ewf_value",
    ("ewf", "md5_hash_matches"): "ewf_value", ("ewf", "integrity_valid"): "ewf_value",
    ("ewf", "sha1_matches"): "ewf_value",
    ("ewf", "segment_number"): "ewf_value", ("ewf", "segment_count"): "ewf_value",
    ("ewf", "number_of_segments"): "ewf_value",
    ("ewf", "section_types"): "ewf_value", ("ewf", "section_names"): "ewf_value",
    ("e01", "case_number"): "ewf_value", ("e01", "evidence_number"): "ewf_value",
    ("e01", "examiner_name"): "ewf_value", ("e01", "description"): "ewf_value", ("e01", "notes"): "ewf_value",
    ("e01", "acquisition_date"): "ewf_value", ("e01", "system_date"): "ewf_value",
    ("e01", "acquisition_software"): "ewf_value", ("e01", "acquisition_software_version"): "ewf_value",
    ("e01", "acquisition_os"): "ewf_value", ("e01", "password_hash"): "ewf_value",
    ("e01", "media_size_bytes"): "ewf_value", ("e01", "sector_count"): "ewf_value",
    ("e01", "bytes_per_sector"): "ewf_value", ("e01", "sectors_per_chunk"): "ewf_value",
    ("e01", "chunk_count"): "ewf_value", ("e01", "error_granularity"): "ewf_value",
    ("e01", "media_type"): "ewf_value", ("e01", "compression_level"): "ewf_value",
    ("e01", "set_identifier_guid"): "ewf_value",
    ("e01", "stored_md5"): "ewf_value", ("e01", "stored_sha1"): "ewf_value", ("e01", "md5"): "ewf_value",
    ("e01", "sha1"): "ewf_value", ("e01", "computed_md5"): "ewf_value", ("e01", "computed_sha1"): "ewf_value",
    ("e01", "hash_matches"): "ewf_value", ("e01", "md5_matches"): "ewf_value", ("e01", "sha1_matches"): "ewf_value",
    ("e01", "segment_number"): "ewf_value", ("e01", "segment_count"): "ewf_value",
    ("e01", "section_types"): "ewf_value",
    ("expert_witness", "case_number"): "ewf_value", ("expert_witness", "evidence_number"): "ewf_value",
    ("expert_witness", "examiner_name"): "ewf_value", ("expert_witness", "description"): "ewf_value",
    ("expert_witness", "notes"): "ewf_value", ("expert_witness", "acquisition_date"): "ewf_value",
    ("expert_witness", "acquisition_software"): "ewf_value", ("expert_witness", "media_size_bytes"): "ewf_value",
    ("expert_witness", "sector_count"): "ewf_value", ("expert_witness", "bytes_per_sector"): "ewf_value",
    ("expert_witness", "chunk_count"): "ewf_value", ("expert_witness", "stored_md5"): "ewf_value",
    ("expert_witness", "stored_sha1"): "ewf_value", ("expert_witness", "computed_md5"): "ewf_value",
    ("expert_witness", "hash_matches"): "ewf_value", ("expert_witness", "segment_count"): "ewf_value",
    ("forensic_image", "case_number"): "ewf_value", ("forensic_image", "evidence_number"): "ewf_value",
    ("forensic_image", "examiner_name"): "ewf_value", ("forensic_image", "description"): "ewf_value",
    ("forensic_image", "notes"): "ewf_value", ("forensic_image", "acquisition_date"): "ewf_value",
    ("forensic_image", "acquisition_software"): "ewf_value", ("forensic_image", "media_size_bytes"): "ewf_value",
    ("forensic_image", "sector_count"): "ewf_value", ("forensic_image", "bytes_per_sector"): "ewf_value",
    ("forensic_image", "chunk_count"): "ewf_value", ("forensic_image", "stored_md5"): "ewf_value",
    ("forensic_image", "stored_sha1"): "ewf_value", ("forensic_image", "computed_md5"): "ewf_value",
    ("forensic_image", "hash_matches"): "ewf_value", ("forensic_image", "segment_count"): "ewf_value",
    ("image", "case_number"): "ewf_value", ("image", "evidence_number"): "ewf_value",
    ("image", "examiner_name"): "ewf_value", ("image", "acquisition_date"): "ewf_value",
    ("image", "acquisition_software"): "ewf_value", ("image", "media_size_bytes"): "ewf_value",
    ("image", "sector_count"): "ewf_value", ("image", "bytes_per_sector"): "ewf_value",
    ("image", "chunk_count"): "ewf_value", ("image", "stored_md5"): "ewf_value",
    ("image", "stored_sha1"): "ewf_value", ("image", "computed_md5"): "ewf_value",
    ("image", "hash_matches"): "ewf_value", ("image", "segment_count"): "ewf_value",
}

_FIELD_KEY = {alias: key for key, names in _NAMES.items() for alias in names}

_SIG1 = (b"EVF\x09\x0d\x0a\xff\x00", b"LVF\x09\x0d\x0a\xff\x00")
_SIG2 = (b"EVF2\r\n\x81\x00", b"LEF2\r\n\x81\x00")
_HDR_KEYS = {"c": "case_number", "n": "evidence_number", "a": "description", "e": "examiner_name", "t": "notes",
             "av": "acquisition_software", "ov": "acquisition_os", "m": "acquisition_date", "u": "system_date",
             "p": "password_hash"}
_MEDIA = {0x00: "removable", 0x01: "fixed", 0x03: "optical", 0x0E: "logical", 0x10: "memory"}
_LEVEL = {0: "none", 1: "fast", 2: "best"}
_MAX_MEDIA = 256 << 20


def _inflate(blob):
    try:
        return zlib.decompressobj().decompress(blob, 64 << 20)
    except zlib.error:
        return None


def _sections(d):
    out, off, seen = [], 13, set()
    while off + 76 <= len(d) and off not in seen and len(out) < 4096:
        seen.add(off)
        typ = d[off:off + 16].split(b"\0", 1)[0].decode("ascii", "replace")
        nxt, size = struct.unpack_from("<QQ", d, off + 16)
        out.append((typ, off, size))
        if typ in ("done", "next") or nxt <= off or nxt > len(d):
            break
        off = nxt
    return out


def _parse_header_text(txt, sep):
    lines = [ln for ln in txt.replace("\r\n", "\n").split("\n")]
    for i, ln in enumerate(lines):
        if ln.strip() == "main" and i + 2 < len(lines):
            keys, vals = lines[i + 1].split("\t"), lines[i + 2].split("\t")
            return {k.strip(): (vals[j] if j < len(vals) else "") for j, k in enumerate(keys)}
    return {}


def _text_date(v):
    p = (v or "").split()
    if len(p) >= 6 and all(x.isdigit() for x in p[:6]):
        try:
            return datetime(*map(int, p[:6])).strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None
    return None


def _epoch_date(v):
    v = (v or "").strip()
    if v.isdigit() and 0 < int(v) < 1 << 34:
        return datetime.fromtimestamp(int(v), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def _cache_key(d):
    return len(d), hashlib.sha1(d).digest()      # content key (never id(obj): D25); a tampered chunk changes it


_CACHE = {}


def parse(d):
    """dict of EWF facts, or None when `d` is not an EWF1 segment file."""
    if not isinstance(d, (bytes, bytearray)) or len(d) < 13 + 76 or bytes(d[:8]) not in _SIG1:
        return None
    k = _cache_key(d)
    if k in _CACHE:
        return _CACHE[k]
    d = bytes(d)
    info = {"segment_number": struct.unpack_from("<H", d, 9)[0]}
    secs = _sections(d)
    info["section_types"] = [s[0] for s in secs]
    hdr, hdr2 = {}, {}
    tables = []
    sectors_ends = []
    for typ, off, size in secs:
        body = d[off + 76:off + size] if size >= 76 else b""
        if typ == "header" and not hdr:
            raw = _inflate(body)
            if raw:
                hdr = _parse_header_text(raw.decode("latin-1", "replace"), "\t")
        elif typ == "header2" and not hdr2:
            raw = _inflate(body)
            if raw:
                enc = "utf-16" if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-16-le"
                hdr2 = _parse_header_text(raw.decode(enc, "replace"), "\t")
        elif typ in ("volume", "disk") and "sector_count" not in info and len(body) >= 20:
            info["media_type_raw"] = body[0]
            info["chunk_count"], info["sectors_per_chunk"], info["bytes_per_sector"] = \
                struct.unpack_from("<III", body, 4)
            if len(body) >= 80:
                info["sector_count"] = struct.unpack_from("<Q", body, 16)[0]
                info["media_flags"] = body[36]
                info["compression_level_raw"] = body[52]
                info["error_granularity"] = struct.unpack_from("<I", body, 56)[0]
                info["set_guid"] = body[64:80]
            else:                                       # SMART S01 volume (94 bytes): u32 sector count
                info["sector_count"] = struct.unpack_from("<I", body, 16)[0]
        elif typ == "sectors":
            sectors_ends.append(off + size)
        elif typ == "table" and len(body) >= 24:
            n, = struct.unpack_from("<I", body, 0)
            base, = struct.unpack_from("<Q", body, 8)
            n = min(n, (len(body) - 24) // 4)
            ents = struct.unpack_from("<%dI" % n, body, 24)
            tables.append((base, ents, off))
        elif typ == "hash" and len(body) >= 16:
            info.setdefault("stored_md5", body[:16].hex())
        elif typ == "digest" and len(body) >= 36:
            info["stored_md5"] = body[:16].hex()
            info["stored_sha1"] = body[16:36].hex()
    merged = {}
    for src in (hdr, hdr2):
        for kk, vv in src.items():
            if kk in _HDR_KEYS and vv.strip():
                merged.setdefault(_HDR_KEYS[kk], vv.strip())
    for name in ("acquisition_date", "system_date"):
        raw_key = {"acquisition_date": "m", "system_date": "u"}[name]
        val = _epoch_date(hdr2.get(raw_key)) or _text_date(hdr.get(raw_key)) or _text_date(hdr2.get(raw_key))
        if hdr.get(raw_key) or hdr2.get(raw_key):
            merged[name + "_raw"] = (hdr.get(raw_key) or hdr2.get(raw_key)).strip()
        if val:
            merged[name] = val
        else:
            merged.pop(name, None)
    info.update(merged)
    info["segment_count"] = info["segment_number"] if secs and secs[-1][0] == "done" else None
    info["computed"] = _compute(d, info, tables, sectors_ends)
    if len(_CACHE) > 32:
        _CACHE.clear()
    _CACHE[k] = info
    return info


def _compute(d, info, tables, sectors_ends):
    """(md5, sha1) over the inflated media, or None (missing chunks / other segments / damage)."""
    spc, bps, nsec = info.get("sectors_per_chunk"), info.get("bytes_per_sector"), info.get("sector_count")
    if not (spc and bps and nsec) or not tables or info.get("segment_count") != 1:
        return None
    media_size, chunk = nsec * bps, spc * bps
    if media_size > _MAX_MEDIA or chunk > (32 << 20):
        return None
    md5, sha1, done = hashlib.md5(), hashlib.sha1(), 0
    for base, ents, toff in tables:
        offs = [base + (e & 0x7FFFFFFF) for e in ents]
        for i, e in enumerate(ents):
            if done >= media_size:
                break
            want = min(chunk, media_size - done)
            start = offs[i]
            if e & 0x80000000:
                end = offs[i + 1] if i + 1 < len(offs) else next(
                    (x for x in sorted(sectors_ends + [toff]) if x > start), len(d))
                raw = _inflate(d[start:max(end, start)] if end > start else d[start:])
                if raw is None:
                    return None
                piece = raw[:want]
            else:
                piece = d[start:start + want]
            if len(piece) != want:
                return None
            md5.update(piece)
            sha1.update(piece)
            done += want
    if done != media_size:
        return None
    return md5.hexdigest(), sha1.hexdigest()


def ewf_value(data, ctx):
    fmt = (ctx or {}).get("fmt") or "ewf"
    field = (ctx or {}).get("field") or ""
    if data is None:
        return None
    try:
        info = parse(data)
    except Exception:
        info = None
    if info is None:
        if bytes(data[:8]) in _SIG2:
            return None                     # EWF2 recognised, not parsed
        return "none" if fmt in _STRICT else None
    key = _FIELD_KEY.get(field)
    if key is None or (fmt == "image" and field in _IMAGE_SKIP):
        return None
    try:
        return _render(info, key)
    except Exception:
        return None


def _render(info, key):
    comp = info.get("computed")
    if key in ("case_number", "evidence_number", "examiner_name", "description", "notes", "acquisition_date",
               "system_date", "acquisition_software", "acquisition_os", "password_hash", "stored_md5",
               "stored_sha1", "acquisition_date_raw"):
        v = info.get(key)
        if key == "password_hash" and v == "0":         # libewf/EnCase write "0" for "no password"
            v = None
        return v if v else "none"
    if key == "media_size_bytes":
        return info["sector_count"] * info["bytes_per_sector"] if "sector_count" in info else None
    if key in ("sector_count", "bytes_per_sector", "sectors_per_chunk", "chunk_count", "error_granularity",
               "segment_number"):
        return info.get(key)
    if key == "segment_count":
        return info.get("segment_count")
    if key == "chunk_size_bytes":
        return info["sectors_per_chunk"] * info["bytes_per_sector"] if "sectors_per_chunk" in info else None
    if key == "media_type":
        return _MEDIA.get(info.get("media_type_raw"), None)
    if key == "compression_level":
        return _LEVEL.get(info.get("compression_level_raw"))
    if key == "set_identifier_guid":
        g = info.get("set_guid")
        return Guid("bytes_le", g) if g and len(g) == 16 and any(g) else "none"
    if key == "section_types":
        return info["section_types"]
    if key == "computed_md5":
        return comp[0] if comp else None
    if key == "computed_sha1":
        return comp[1] if comp else None
    if key == "hash_matches":
        if not comp or not info.get("stored_md5"):
            return None
        return comp[0] == info["stored_md5"]
    if key == "sha1_matches":
        if not comp or not info.get("stored_sha1"):
            return None
        return comp[1] == info["stored_sha1"]
    return None
