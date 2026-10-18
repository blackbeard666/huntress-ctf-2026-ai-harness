"""FLAC STREAMINFO / OpusHead / Vorbis identification header / Ogg page fields -- prebuilt, SPECULATIVE (never asked).

Pure struct, no codec work. Registered under `media` (the D17 audio token) and the container/codec tokens `flac`, `ogg`,
`opus`, `vorbis`; field names are `<codec>_<spec struct field>` (flac_min_block_size, opus_pre_skip, vorbis_blocksizes,
ogg_serial_numbers_hex), and the bare `<struct field>` under the codec's own token (flac.total_samples).
  FLAC  native `fLaC` (an ID3v2 prefix is skipped) or Ogg-FLAC (0x7F "FLAC" mapping packet). STREAMINFO big-endian:
        u16 min/max block size, u24 min/max frame size, u20 sample rate, u3 channels-1, u5 bps-1, u36 total samples,
        16-byte MD5 (all zero = "not computed" -> "none"; else 32 lowercase hex). metadata_block_types = the stored
        order of block type NAMES (libFLAC/metaflac spelling: STREAMINFO, PADDING, APPLICATION, SEEKTABLE,
        VORBIS_COMMENT, CUESHEET, PICTURE; an unknown type -> its number).
  Opus  OpusHead (RFC 7845 5.1), little-endian: u8 version, u8 channel count, u16 pre-skip, u32 input sample rate,
        s16 output gain (raw Q7.8 dB as stored; exiftool shows the linear factor 10^(g/5120) instead), u8 mapping family.
  Vorbis identification header (Vorbis I spec 4.2.2): u32 version, u8 channels, u32 rate, s32 bitrate max/nominal/min
        (raw signed as stored), blocksizes byte -> [2^low nibble, 2^high nibble] (blocksize_0, blocksize_1).
  Ogg   every page in file order: page_count = all pages of all logical streams; serial_numbers_hex = distinct serials
        in first-seen order as 0x%08x; last_granule = the granule position of the LAST page of the FIRST logical stream
        carrying one (-1 = no packet ends there, skipped) -- the value an audio length tool reads.
A member whose bytes carry no such header (PNG/text/ZIP, or an Opus file asked for flac_*) -> "none"; empty -> None."""
import struct

FIELDS = {
    # media (D17 token) + ogg: the codec-prefixed names for everything
    ("media", "flac_min_block_size"): "header_value",
    ("media", "flac_max_block_size"): "header_value",
    ("media", "flac_min_blocksize"): "header_value",
    ("media", "flac_max_blocksize"): "header_value",
    ("media", "flac_min_frame_size"): "header_value",
    ("media", "flac_max_frame_size"): "header_value",
    ("media", "flac_sample_rate"): "header_value",
    ("media", "flac_channels"): "header_value",
    ("media", "flac_channel_count"): "header_value",
    ("media", "flac_bits_per_sample"): "header_value",
    ("media", "flac_total_samples"): "header_value",
    ("media", "flac_md5_signature"): "header_value",
    ("media", "flac_md5"): "header_value",
    ("media", "flac_streaminfo_md5"): "header_value",
    ("media", "flac_metadata_block_types"): "header_value",
    ("media", "flac_metadata_block_names"): "header_value",
    ("media", "flac_metadata_block_count"): "header_value",
    ("media", "opus_version"): "header_value",
    ("media", "opus_channel_count"): "header_value",
    ("media", "opus_channels"): "header_value",
    ("media", "opus_pre_skip"): "header_value",
    ("media", "opus_preskip"): "header_value",
    ("media", "opus_input_sample_rate"): "header_value",
    ("media", "opus_original_sample_rate"): "header_value",
    ("media", "opus_output_gain"): "header_value",
    ("media", "opus_channel_mapping_family"): "header_value",
    ("media", "opus_mapping_family"): "header_value",
    ("media", "vorbis_version"): "header_value",
    ("media", "vorbis_channels"): "header_value",
    ("media", "vorbis_audio_channels"): "header_value",
    ("media", "vorbis_sample_rate"): "header_value",
    ("media", "vorbis_bitrate_nominal"): "header_value",
    ("media", "vorbis_bitrate_maximum"): "header_value",
    ("media", "vorbis_bitrate_minimum"): "header_value",
    ("media", "vorbis_nominal_bitrate"): "header_value",
    ("media", "vorbis_blocksizes"): "header_value",
    ("media", "vorbis_blocksize_0"): "header_value",
    ("media", "vorbis_blocksize_1"): "header_value",
    ("media", "ogg_serial_numbers_hex"): "header_value",
    ("media", "ogg_serial_numbers"): "header_value",
    ("media", "ogg_stream_serial_numbers_hex"): "header_value",
    ("media", "ogg_page_count"): "header_value",
    ("media", "ogg_last_granule"): "header_value",
    ("media", "ogg_last_granule_position"): "header_value",
    ("media", "ogg_stream_count"): "header_value",
    ("ogg", "flac_min_block_size"): "header_value",
    ("ogg", "flac_max_block_size"): "header_value",
    ("ogg", "flac_sample_rate"): "header_value",
    ("ogg", "flac_channels"): "header_value",
    ("ogg", "flac_bits_per_sample"): "header_value",
    ("ogg", "flac_total_samples"): "header_value",
    ("ogg", "flac_md5_signature"): "header_value",
    ("ogg", "flac_metadata_block_types"): "header_value",
    ("ogg", "opus_version"): "header_value",
    ("ogg", "opus_channel_count"): "header_value",
    ("ogg", "opus_pre_skip"): "header_value",
    ("ogg", "opus_input_sample_rate"): "header_value",
    ("ogg", "opus_output_gain"): "header_value",
    ("ogg", "opus_channel_mapping_family"): "header_value",
    ("ogg", "vorbis_version"): "header_value",
    ("ogg", "vorbis_channels"): "header_value",
    ("ogg", "vorbis_sample_rate"): "header_value",
    ("ogg", "vorbis_bitrate_nominal"): "header_value",
    ("ogg", "vorbis_bitrate_maximum"): "header_value",
    ("ogg", "vorbis_bitrate_minimum"): "header_value",
    ("ogg", "vorbis_blocksizes"): "header_value",
    ("ogg", "ogg_serial_numbers_hex"): "header_value",
    ("ogg", "ogg_page_count"): "header_value",
    ("ogg", "ogg_last_granule"): "header_value",
    ("ogg", "ogg_last_granule_position"): "header_value",
    ("ogg", "ogg_stream_count"): "header_value",
    ("ogg", "serial_numbers_hex"): "header_value",
    ("ogg", "serial_numbers"): "header_value",
    ("ogg", "stream_serial_numbers_hex"): "header_value",
    ("ogg", "page_count"): "header_value",
    ("ogg", "last_granule"): "header_value",
    ("ogg", "last_granule_position"): "header_value",
    ("ogg", "stream_count"): "header_value",
    # flac token: bare STREAMINFO names (+ streaminfo_ / flac_ forms)
    ("flac", "min_block_size"): "header_value",
    ("flac", "max_block_size"): "header_value",
    ("flac", "min_blocksize"): "header_value",
    ("flac", "max_blocksize"): "header_value",
    ("flac", "min_frame_size"): "header_value",
    ("flac", "max_frame_size"): "header_value",
    ("flac", "sample_rate"): "header_value",
    ("flac", "channels"): "header_value",
    ("flac", "channel_count"): "header_value",
    ("flac", "bits_per_sample"): "header_value",
    ("flac", "total_samples"): "header_value",
    ("flac", "md5_signature"): "header_value",
    ("flac", "md5"): "header_value",
    ("flac", "metadata_block_types"): "header_value",
    ("flac", "metadata_block_names"): "header_value",
    ("flac", "metadata_block_count"): "header_value",
    ("flac", "streaminfo_min_block_size"): "header_value",
    ("flac", "streaminfo_max_block_size"): "header_value",
    ("flac", "streaminfo_sample_rate"): "header_value",
    ("flac", "streaminfo_channels"): "header_value",
    ("flac", "streaminfo_bits_per_sample"): "header_value",
    ("flac", "streaminfo_total_samples"): "header_value",
    ("flac", "streaminfo_md5_signature"): "header_value",
    ("flac", "flac_min_block_size"): "header_value",
    ("flac", "flac_max_block_size"): "header_value",
    ("flac", "flac_sample_rate"): "header_value",
    ("flac", "flac_channels"): "header_value",
    ("flac", "flac_bits_per_sample"): "header_value",
    ("flac", "flac_total_samples"): "header_value",
    ("flac", "flac_md5_signature"): "header_value",
    ("flac", "flac_metadata_block_types"): "header_value",
    # opus token: bare OpusHead names (+ opushead_ / opus_ forms) and the Ogg page fields
    ("opus", "version"): "header_value",
    ("opus", "channel_count"): "header_value",
    ("opus", "channels"): "header_value",
    ("opus", "pre_skip"): "header_value",
    ("opus", "preskip"): "header_value",
    ("opus", "input_sample_rate"): "header_value",
    ("opus", "original_sample_rate"): "header_value",
    ("opus", "output_gain"): "header_value",
    ("opus", "channel_mapping_family"): "header_value",
    ("opus", "mapping_family"): "header_value",
    ("opus", "opushead_version"): "header_value",
    ("opus", "opushead_channel_count"): "header_value",
    ("opus", "opushead_pre_skip"): "header_value",
    ("opus", "opushead_input_sample_rate"): "header_value",
    ("opus", "opushead_output_gain"): "header_value",
    ("opus", "opushead_channel_mapping_family"): "header_value",
    ("opus", "opus_version"): "header_value",
    ("opus", "opus_channel_count"): "header_value",
    ("opus", "opus_pre_skip"): "header_value",
    ("opus", "opus_input_sample_rate"): "header_value",
    ("opus", "opus_output_gain"): "header_value",
    ("opus", "opus_channel_mapping_family"): "header_value",
    ("opus", "ogg_serial_numbers_hex"): "header_value",
    ("opus", "ogg_page_count"): "header_value",
    ("opus", "ogg_last_granule"): "header_value",
    # vorbis token
    ("vorbis", "version"): "header_value",
    ("vorbis", "channels"): "header_value",
    ("vorbis", "audio_channels"): "header_value",
    ("vorbis", "sample_rate"): "header_value",
    ("vorbis", "bitrate_nominal"): "header_value",
    ("vorbis", "bitrate_maximum"): "header_value",
    ("vorbis", "bitrate_minimum"): "header_value",
    ("vorbis", "nominal_bitrate"): "header_value",
    ("vorbis", "blocksizes"): "header_value",
    ("vorbis", "blocksize_0"): "header_value",
    ("vorbis", "blocksize_1"): "header_value",
    ("vorbis", "vorbis_version"): "header_value",
    ("vorbis", "vorbis_channels"): "header_value",
    ("vorbis", "vorbis_sample_rate"): "header_value",
    ("vorbis", "vorbis_bitrate_nominal"): "header_value",
    ("vorbis", "vorbis_blocksizes"): "header_value",
    ("vorbis", "ogg_serial_numbers_hex"): "header_value",
    ("vorbis", "ogg_page_count"): "header_value",
    ("vorbis", "ogg_last_granule"): "header_value",
}

_BLOCK_NAMES = {0: "STREAMINFO", 1: "PADDING", 2: "APPLICATION", 3: "SEEKTABLE", 4: "VORBIS_COMMENT", 5: "CUESHEET",
                6: "PICTURE"}
# alias -> canonical key (after the codec prefix is applied)
_ALIAS = {
    "flac_min_blocksize": "flac_min_block_size", "flac_max_blocksize": "flac_max_block_size",
    "flac_channel_count": "flac_channels", "flac_md5": "flac_md5_signature", "flac_streaminfo_md5": "flac_md5_signature",
    "flac_metadata_block_names": "flac_metadata_block_types",
    "opus_channels": "opus_channel_count", "opus_preskip": "opus_pre_skip",
    "opus_original_sample_rate": "opus_input_sample_rate", "opus_mapping_family": "opus_channel_mapping_family",
    "vorbis_audio_channels": "vorbis_channels", "vorbis_nominal_bitrate": "vorbis_bitrate_nominal",
    "ogg_serial_numbers": "ogg_serial_numbers_hex", "ogg_stream_serial_numbers_hex": "ogg_serial_numbers_hex",
    "ogg_last_granule_position": "ogg_last_granule",
}


def _canon(fmt, field):
    f = field
    for infix in ("streaminfo_", "opushead_", "opus_head_", "identification_"):
        if f.startswith(infix):
            f = f[len(infix):]
    if not f.startswith(("flac_", "opus_", "vorbis_", "ogg_")):
        if fmt in ("flac", "opus", "vorbis"):
            f = fmt + "_" + f
        elif fmt == "ogg":
            f = "ogg_" + f
    return _ALIAS.get(f, f)


def _ogg_pages(b):
    """[(header_type, granule, serial, [segment-joined packet pieces with 'complete' flags])] for every OggS page."""
    pages, off, n = [], 0, len(b)
    while off + 27 <= n and b[off:off + 4] == b"OggS":
        htype, gran, serial = b[off + 5], struct.unpack_from("<q", b, off + 6)[0], struct.unpack_from("<I", b, off + 14)[0]
        nseg = b[off + 26]
        lace = b[off + 27:off + 27 + nseg]
        if len(lace) < nseg:
            break
        body = off + 27 + nseg
        pieces, start, ln = [], body, 0
        for v in lace:
            ln += v
            if v < 255:
                pieces.append((b[start:start + ln], True))
                start, ln = start + ln, 0
        if ln:
            pieces.append((b[start:start + ln], False))
        pages.append((htype, gran, serial, pieces))
        off = body + sum(lace)
    return pages


def _ogg_streams(pages, limit=64):
    """{serial: [first `limit` complete packets]} plus serial order."""
    pk, partial, order = {}, {}, []
    for _htype, _g, serial, pieces in pages:
        if serial not in pk:
            pk[serial], partial[serial] = [], b""
            order.append(serial)
        for data, complete in pieces:
            partial[serial] += data
            if complete:
                if len(pk[serial]) < limit:
                    pk[serial].append(partial[serial])
                partial[serial] = b""
    return pk, order


def _flac_blocks(b, off):
    """[(type, payload)] of native FLAC metadata blocks starting at `off` (just past fLaC)."""
    out = []
    while off + 4 <= len(b):
        hdr = b[off]
        ln = int.from_bytes(b[off + 1:off + 4], "big")
        out.append((hdr & 0x7F, b[off + 4:off + 4 + ln]))
        off += 4 + ln
        if hdr & 0x80:
            break
    return out


def _streaminfo(p):
    if len(p) < 34:
        return None
    mn, mx = struct.unpack_from(">HH", p, 0)
    x = int.from_bytes(p[10:18], "big")
    md5 = p[18:34]
    return {"flac_min_block_size": mn, "flac_max_block_size": mx,
            "flac_min_frame_size": int.from_bytes(p[4:7], "big"), "flac_max_frame_size": int.from_bytes(p[7:10], "big"),
            "flac_sample_rate": x >> 44, "flac_channels": ((x >> 41) & 7) + 1,
            "flac_bits_per_sample": ((x >> 36) & 0x1F) + 1, "flac_total_samples": x & 0xFFFFFFFFF,
            "flac_md5_signature": "none" if not any(md5) else md5.hex()}


def _with_blocks(si, blocks):
    si = dict(si)
    si["flac_metadata_block_types"] = [_BLOCK_NAMES.get(t, t) for t, _ in blocks]
    si["flac_metadata_block_count"] = len(blocks)
    return si


def _parse(b):
    """{canonical field: value} of every header present; {} when none is."""
    out = {}
    off = 0
    if b[:3] == b"ID3" and len(b) >= 10:
        off = 10 + ((b[6] & 0x7F) << 21 | (b[7] & 0x7F) << 14 | (b[8] & 0x7F) << 7 | (b[9] & 0x7F))
        if b[5] & 0x10:
            off += 10
    if b[off:off + 4] == b"fLaC":
        blocks = _flac_blocks(b, off + 4)
        if blocks and blocks[0][0] == 0:
            si = _streaminfo(blocks[0][1])
            if si:
                out.update(_with_blocks(si, blocks))
        return out
    if b[:4] != b"OggS":
        return out
    pages = _ogg_pages(b)
    if not pages:
        return out
    pk, order = _ogg_streams(pages)
    out["ogg_page_count"] = len(pages)
    out["ogg_serial_numbers_hex"] = ["0x%08x" % s for s in order]
    out["ogg_stream_count"] = len(order)
    first = order[0]
    grans = [g for _h, g, s, _p in pages if s == first and g != -1]
    if grans:
        out["ogg_last_granule"] = grans[-1]
    for s in order:
        p = pk[s]
        if not p:
            continue
        h = p[0]
        if h[:8] == b"OpusHead" and len(h) >= 19 and "opus_version" not in out:
            v, ch, pre, rate, gain, fam = struct.unpack_from("<BBHIhB", h, 8)
            out.update(opus_version=v, opus_channel_count=ch, opus_pre_skip=pre, opus_input_sample_rate=rate,
                       opus_output_gain=gain, opus_channel_mapping_family=fam)
        elif h[:7] == b"\x01vorbis" and len(h) >= 29 and "vorbis_version" not in out:
            ver, ch, rate, bmax, bnom, bmin, bs = struct.unpack_from("<IBIiiiB", h, 7)
            out.update(vorbis_version=ver, vorbis_channels=ch, vorbis_sample_rate=rate, vorbis_bitrate_maximum=bmax,
                       vorbis_bitrate_nominal=bnom, vorbis_bitrate_minimum=bmin,
                       vorbis_blocksizes=[1 << (bs & 0xF), 1 << (bs >> 4)],
                       vorbis_blocksize_0=1 << (bs & 0xF), vorbis_blocksize_1=1 << (bs >> 4))
        elif h[:5] == b"\x7fFLAC" and h[9:13] == b"fLaC" and "flac_sample_rate" not in out:
            # Ogg-FLAC mapping: packet 0 = 0x7F FLAC maj min u16 nhdr fLaC + STREAMINFO block; then 1 block / packet
            blocks = _flac_blocks(h, 13)
            for q in p[1:]:
                if blocks and len(q) >= 4 and not (h[13] & 0x80):
                    blocks.append((q[0] & 0x7F, q[4:]))
                    if q[0] & 0x80:
                        break
            si = _streaminfo(blocks[0][1]) if blocks and blocks[0][0] == 0 else None
            if si:
                out.update(_with_blocks(si, blocks))
    return out


def header_value(data, ctx):
    """<fmt>.<codec>_<header field>: the struct value; a member without that header -> "none"."""
    if not data:
        return None
    try:
        ctx = ctx or {}
        key = _canon(ctx.get("fmt") or "", ctx.get("field") or "")
        vals = _parse(bytes(data))
        if key in vals:
            return vals[key]
        return "none"
    except Exception:  # noqa: BLE001 -- a malformed member never raises past the extractor
        return None
