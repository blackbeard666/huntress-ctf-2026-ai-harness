"""WAV chunk-level fields (prebuilt, SPECULATIVE -- never GM-asked yet): BWF bext, fact, cue, iXML, RIFF size
bookkeeping and bytes trailing the data chunk (the classic "payload appended to a WAV" hiding spot). Registered under
the GM's generic `media` token (D17 filed audio members as `media.*`, answer ids `dNN-audio-NNN-media-...`) and `wav`.
INFO text fields (info_title = INAM, info_software = ISFT, ...) stay in wav.py / media.py's router.

Layout: "RIFF"|"RF64" size u32le "WAVE", chunks id[4] size u32le body (+1 pad byte when size is odd).
  riff_chunk_ids        top-level chunk ids in FILE order (JSON list, ids verbatim incl. the trailing space of "fmt ",
                        "cue "); the walk (declared RIFF extent) stops at the first id that is not 4 printable ASCII or a body past EOF.
  riff_size_declared    the u32 after "RIFF" (int); riff_size_mismatch = declared + 8 != file length (bool).
  trailing_bytes_after_data  bytes after the data chunk (+pad) and any well-formed chunks that follow it (LIST/cue/
                        id3 after data are legitimate); a truncated data chunk -> 0. *_present -> bool.
  trailing_*_magic_prefix_hex_N  first N bytes of that trailer, lowercase hex (no trailer -> "none").
  bext_* (EBU Tech 3285): Description[256] Originator[32] OriginatorReference[32] OriginationDate[10]
                        OriginationTime[8] TimeReference u64 (low, high u32 -> int samples since midnight)
                        Version u16 UMID[64] reserved[190] CodingHistory[...]. Strings verbatim (latin-1), trailing
                        NULs stripped. bext_umid_hex: lowercase hex, a zero second half (basic 32-byte UMID) dropped
                        -- exiftool's BWF_UMID rule (s/0{64}$//), lowercased per the _hex law; all-zero -> "none".
  fact_sample_count     fact dwSampleLength u32. cue_point_count = cue dwCuePoints u32. ixml_present = an "iXML"
                        chunk exists (bool, false when absent).
Absent chunk -> "none" (bext/fact/cue fields). Not RIFF....WAVE (WebP/AVI are RIFF too, PNG renamed .wav) -> "none"."""
import struct

FIELDS = {
    ("wav", "riff_chunk_ids"): "riff_chunk_ids",
    ("wav", "chunk_ids"): "riff_chunk_ids",
    ("wav", "riff_chunk_list"): "riff_chunk_ids",
    ("wav", "riff_chunks"): "riff_chunk_ids",
    ("wav", "top_level_chunk_ids"): "riff_chunk_ids",
    ("wav", "chunk_order"): "riff_chunk_ids",
    ("wav", "riff_chunk_order"): "riff_chunk_ids",
    ("wav", "bext_description"): "bext_value",
    ("wav", "bext_originator"): "bext_value",
    ("wav", "bext_originator_reference"): "bext_value",
    ("wav", "bext_origination_date"): "bext_value",
    ("wav", "bext_origination_time"): "bext_value",
    ("wav", "bext_time_reference"): "bext_value",
    ("wav", "bext_umid_hex"): "bext_value",
    ("wav", "bext_umid"): "bext_value",
    ("wav", "bext_version"): "bext_value",
    ("wav", "bext_coding_history"): "bext_value",
    ("wav", "bext_present"): "bext_value",
    ("wav", "has_bext"): "bext_value",
    ("wav", "bwf_description"): "bext_value",
    ("wav", "bwf_originator"): "bext_value",
    ("wav", "bwf_originator_reference"): "bext_value",
    ("wav", "bwf_origination_date"): "bext_value",
    ("wav", "bwf_origination_time"): "bext_value",
    ("wav", "bwf_time_reference"): "bext_value",
    ("wav", "bwf_umid_hex"): "bext_value",
    ("wav", "bwf_version"): "bext_value",
    ("wav", "bwf_coding_history"): "bext_value",
    ("wav", "fact_sample_count"): "riff_value",
    ("wav", "fact_dw_sample_length"): "riff_value",
    ("wav", "fact_sample_length"): "riff_value",
    ("wav", "fact_num_samples"): "riff_value",
    ("wav", "riff_size_declared"): "riff_value",
    ("wav", "riff_chunk_size"): "riff_value",
    ("wav", "riff_size"): "riff_value",
    ("wav", "riff_header_size"): "riff_value",
    ("wav", "riff_declared_size"): "riff_value",
    ("wav", "riff_size_mismatch"): "riff_value",
    ("wav", "riff_size_mismatch_present"): "riff_value",
    ("wav", "has_riff_size_mismatch"): "riff_value",
    ("wav", "trailing_bytes_after_data"): "riff_value",
    ("wav", "trailing_bytes_count"): "riff_value",
    ("wav", "trailing_bytes"): "riff_value",
    ("wav", "trailing_bytes_size"): "riff_value",
    ("wav", "trailing_data_size_bytes"): "riff_value",
    ("wav", "trailing_data_bytes"): "riff_value",
    ("wav", "trailer_size_bytes"): "riff_value",
    ("wav", "trailing_bytes_present"): "riff_value",
    ("wav", "has_trailing_bytes"): "riff_value",
    ("wav", "trailing_data_present"): "riff_value",
    ("wav", "cue_point_count"): "riff_value",
    ("wav", "cue_points_count"): "riff_value",
    ("wav", "cue_count"): "riff_value",
    ("wav", "number_of_cue_points"): "riff_value",
    ("wav", "ixml_present"): "riff_value",
    ("wav", "has_ixml"): "riff_value",
    ("wav", "ixml_chunk_present"): "riff_value",
    ("wav", "trailing_bytes_magic_prefix_hex_*"): "trailer_magic",
    ("wav", "trailing_bytes_after_data_magic_prefix_hex_*"): "trailer_magic",
    ("wav", "trailer_magic_prefix_hex_*"): "trailer_magic",
    ("wav", "trailing_data_magic_prefix_hex_*"): "trailer_magic",
    ("wav", "trailing_magic_prefix_hex_*"): "trailer_magic",
    ("media", "riff_chunk_ids"): "riff_chunk_ids",
    ("media", "chunk_ids"): "riff_chunk_ids",
    ("media", "riff_chunk_list"): "riff_chunk_ids",
    ("media", "riff_chunks"): "riff_chunk_ids",
    ("media", "top_level_chunk_ids"): "riff_chunk_ids",
    ("media", "chunk_order"): "riff_chunk_ids",
    ("media", "riff_chunk_order"): "riff_chunk_ids",
    ("media", "bext_description"): "bext_value",
    ("media", "bext_originator"): "bext_value",
    ("media", "bext_originator_reference"): "bext_value",
    ("media", "bext_origination_date"): "bext_value",
    ("media", "bext_origination_time"): "bext_value",
    ("media", "bext_time_reference"): "bext_value",
    ("media", "bext_umid_hex"): "bext_value",
    ("media", "bext_umid"): "bext_value",
    ("media", "bext_version"): "bext_value",
    ("media", "bext_coding_history"): "bext_value",
    ("media", "bext_present"): "bext_value",
    ("media", "has_bext"): "bext_value",
    ("media", "bwf_description"): "bext_value",
    ("media", "bwf_originator"): "bext_value",
    ("media", "bwf_originator_reference"): "bext_value",
    ("media", "bwf_origination_date"): "bext_value",
    ("media", "bwf_origination_time"): "bext_value",
    ("media", "bwf_time_reference"): "bext_value",
    ("media", "bwf_umid_hex"): "bext_value",
    ("media", "bwf_version"): "bext_value",
    ("media", "bwf_coding_history"): "bext_value",
    ("media", "fact_sample_count"): "riff_value",
    ("media", "fact_dw_sample_length"): "riff_value",
    ("media", "fact_sample_length"): "riff_value",
    ("media", "fact_num_samples"): "riff_value",
    ("media", "riff_size_declared"): "riff_value",
    ("media", "riff_chunk_size"): "riff_value",
    ("media", "riff_size"): "riff_value",
    ("media", "riff_header_size"): "riff_value",
    ("media", "riff_declared_size"): "riff_value",
    ("media", "riff_size_mismatch"): "riff_value",
    ("media", "riff_size_mismatch_present"): "riff_value",
    ("media", "has_riff_size_mismatch"): "riff_value",
    ("media", "trailing_bytes_after_data"): "riff_value",
    ("media", "trailing_bytes_count"): "riff_value",
    ("media", "trailing_bytes"): "riff_value",
    ("media", "trailing_bytes_size"): "riff_value",
    ("media", "trailing_data_size_bytes"): "riff_value",
    ("media", "trailing_data_bytes"): "riff_value",
    ("media", "trailer_size_bytes"): "riff_value",
    ("media", "trailing_bytes_present"): "riff_value",
    ("media", "has_trailing_bytes"): "riff_value",
    ("media", "trailing_data_present"): "riff_value",
    ("media", "cue_point_count"): "riff_value",
    ("media", "cue_points_count"): "riff_value",
    ("media", "cue_count"): "riff_value",
    ("media", "number_of_cue_points"): "riff_value",
    ("media", "ixml_present"): "riff_value",
    ("media", "has_ixml"): "riff_value",
    ("media", "ixml_chunk_present"): "riff_value",
    ("media", "trailing_bytes_magic_prefix_hex_*"): "trailer_magic",
    ("media", "trailing_bytes_after_data_magic_prefix_hex_*"): "trailer_magic",
    ("media", "trailer_magic_prefix_hex_*"): "trailer_magic",
    ("media", "trailing_data_magic_prefix_hex_*"): "trailer_magic",
    ("media", "trailing_magic_prefix_hex_*"): "trailer_magic",
}


def _parse(b):
    """{'size': declared, 'chunks': [(id, body_off, body_len)], 'trail': trailer offset or None} or None (not WAVE)."""
    if not b or len(b) < 12 or b[:4] not in (b"RIFF", b"RF64") or b[8:12] != b"WAVE":
        return None
    size = struct.unpack_from("<I", b, 4)[0]
    chunks, off, flen = [], 12, len(b)
    n = size + 8 if 12 < size + 8 < flen else flen   # an appended trailer outside the RIFF extent is not a chunk
    while off + 8 <= n:
        cid = b[off:off + 4]
        if not all(32 <= c < 127 for c in cid):
            break
        sz = struct.unpack_from("<I", b, off + 4)[0]
        chunks.append((cid, off + 8, sz))
        if off + 8 + sz > n:
            break
        off += 8 + sz + (sz & 1)
    trail = None
    for i, (cid, bo, sz) in enumerate(chunks):
        if cid == b"data":
            end = bo + sz
            if end > flen:                  # truncated data chunk: nothing trails it
                trail = flen
                break
            end += (sz & 1) if end < flen and b[end] == 0 else 0
            for cid2, bo2, sz2 in chunks[i + 1:]:
                if bo2 - 8 != end or bo2 + sz2 > flen:
                    break
                end = bo2 + sz2 + ((sz2 & 1) if bo2 + sz2 < flen else 0)
            trail = min(end, flen)
            break
    return {"size": size, "chunks": chunks, "trail": trail}


def _chunk(p, cid):
    return next(((bo, sz) for c, bo, sz in p["chunks"] if c == cid), None)


def _txt(raw):
    return raw.split(b"\x00")[0].decode("latin-1").rstrip("\x00")


def _safe(fn):
    def wrap(data, ctx):
        if data is None:
            return None
        try:
            p = _parse(bytes(data))
            return "none" if p is None else fn(bytes(data), p, (ctx or {}).get("field") or "", ctx or {})
        except Exception:  # noqa: BLE001 -- a malformed WAV never raises past the extractor
            return None
    wrap.__name__ = fn.__name__
    return wrap


@_safe
def riff_chunk_ids(b, p, f, ctx):
    return [c.decode("latin-1") for c, _, _ in p["chunks"]]


_BEXT = {"description": (0, 256), "originator": (256, 32), "originator_reference": (288, 32),
         "origination_date": (320, 10), "origination_time": (330, 8), "coding_history": (602, None)}


@_safe
def bext_value(b, p, f, ctx):
    key = f.split("_", 1)[1] if f.startswith(("bext_", "bwf_")) else f
    ch = _chunk(p, b"bext")
    if key in ("present", "bext") or f == "has_bext":
        return ch is not None
    if ch is None:
        return "none"
    bo, sz = ch
    body = b[bo:bo + sz]
    if key in _BEXT:
        o, ln = _BEXT[key]
        if len(body) < o + (ln or 0):
            return "none"
        v = _txt(body[o:o + ln] if ln else body[o:])
        return v if v.strip("\x00") != "" else "none"
    if key == "time_reference":
        if len(body) < 346:
            return "none"
        lo, hi = struct.unpack_from("<II", body, 338)
        return lo + (hi << 32)
    if key == "version":
        return struct.unpack_from("<H", body, 346)[0] if len(body) >= 348 else "none"
    if key in ("umid_hex", "umid"):
        u = body[348:412]
        if len(u) < 64 or not any(u):
            return "none"
        h = u.hex()
        return h[:64] if h.endswith("0" * 64) else h
    return None


@_safe
def riff_value(b, p, f, ctx):
    if f.startswith("fact_"):
        ch = _chunk(p, b"fact")
        return struct.unpack_from("<I", b, ch[0])[0] if ch and ch[1] >= 4 and ch[0] + 4 <= len(b) else "none"
    if "mismatch" in f:
        return p["size"] + 8 != len(b)
    if f.startswith("riff_"):
        return p["size"]
    if "trail" in f:
        n = 0 if p["trail"] is None else len(b) - p["trail"]
        return n > 0 if f.endswith("_present") or f.startswith("has_") else n
    if "cue" in f:
        ch = _chunk(p, b"cue ")
        return struct.unpack_from("<I", b, ch[0])[0] if ch and ch[1] >= 4 and ch[0] + 4 <= len(b) else "none"
    if "ixml" in f:
        return _chunk(p, b"iXML") is not None
    return None


@_safe
def trailer_magic(b, p, f, ctx):
    param = str(ctx.get("param") or "")
    n = int(param) if param.isdigit() else 16
    if p["trail"] is None or p["trail"] >= len(b):
        return "none"
    return b[p["trail"]:p["trail"] + n].hex()
