"""Windows Prefetch (.pf) fields (prebuilt, SPECULATIVE; prefetch.executable_name is GM-verified D26 via
lib/meta/prefetch.py, which calls pf_value here).

Win10/11 files are wrapped: "MAM" + type byte, uncompressed size u32 @4, stream @8 -- or @12 when the type's high bit
0x80 is set: then a CRC32 u32 @8 = crc32(the 12-byte header with the CRC field zeroed + payload). Type low nibble
(RtlDecompressBufferEx COMPRESSION_FORMAT_*): 4 = LZXpress Huffman (MS-XCA 2.2: per 64 KiB of output a 256-byte table of
512 4-bit code lengths, then 16-bit LE words read MSB-first), 3 = plain LZ77 Xpress (MS-XCA 2.4: u32 flag words,
u16 matches, shared half-byte length nibbles), 2 = LZNT1 (MS-XCA 2.5: 4 KiB chunks, u16 chunk headers, position-
dependent offset/length split). All three decoded here in pure Python (D26 single was MAM\x04, timed plain SCCA v30:
the kit flips the wrapper, so every wrapper is decoded rather than answered "none").
SCCA (libscca "Windows Prefetch File (PF) format", little-endian): header 84 bytes = format version u32 @0
(17 XP/2003, 23 Vista/7, 26 8.1, 30 10/11, 31 Win11 24H2+), "SCCA" @4, file size u32 @12, executable name UTF-16LE
60 bytes @16 (NUL-terminated, max 29 chars + NUL; kept as stored -- case and non-ASCII verbatim; a field with no NUL
yields all 30 chars), prefetch (path) hash u32 @76. File information @84: metrics array offset u32 @84 (its value
gives the file-information size: 0x98 v17 = 68 B, 0xF0 v23 = 156 B, 0x130 v26/v30 = 220 B, 0x128 v30 "variant 2"
= 212 B), filename strings offset/size u32 @100/@104, volumes information offset u32 @108, number of volumes u32 @112.
  last run time FILETIME: v17 @0x78, v23 @0x80, v26/v30/v31 8 x FILETIME @0x80 (newest first; unused slots zero).
  run count u32: v17 @0x90, v23 @0x98, v26 @0xD0, v30/v31 @0xD0 (220-B info) or @0xC8 (212-B "variant 2", metrics
  array @0x128) -- picked by the metrics offset @84, so a v31 is parsed exactly as a v30.
  An UNKNOWN version with "SCCA" @4 still answers the fixed header (executable_name, prefetch_hash, file_size_bytes,
  format_version, ...); version-dependent fields -> None.
  volume information entry (first volume, @ volumes offset): device path offset u32 @0 (relative to the volumes
  block) + chars u32 @4, creation FILETIME @8, serial number u32 @16.
New: file_size_bytes = SCCA header u32 @12 (int); header_file_size_matches = that == the (decompressed) SCCA length;
executable_name_length = chars of the stored name; compression_format = xpress_huffman / xpress / lznt1 for a MAM
wrapper, "none" for plain SCCA; uncompressed_size_bytes = MAM u32 @4 ("none" for plain SCCA); mam_crc32_u32_hex /
mam_crc32_valid ("none" without the 0x80 flag).
Times: FILETIME (100 ns since 1601-01-01 UTC) -> ISO-8601 UTC 'YYYY-MM-DDTHH:MM:SSZ' (same spelling as lnk.*_time /
regf.*_time), zero -> "none". last_run_time = slot 0 (the most recent run); last_run_times = every non-zero slot,
stored order. prefetch_hash / volume_serial -> Hex(u32, 8) ("0x" + 8 lowercase digits, NOT the filename's upper-case
'-AC08706A'). volume_* = the FIRST volume entry. format_version -> int ("30").
Decoys: neither SCCA nor MAM (a renamed LNK, an SCCB signature) -> "none"; a MAM stream that does not decompress to
SCCA (unknown type nibble, garbage payload), or SCCA truncated before the asked field -> None."""
import datetime
import struct
import time
import zlib

from ..spell import Hex

FIELDS = {
    ("prefetch", "executable_filename"): "pf_value",
    ("prefetch", "executable_file_name"): "pf_value",
    ("prefetch", "exe_name"): "pf_value",
    ("prefetch", "executable"): "pf_value",
    ("prefetch", "header_executable_name"): "pf_value",
    ("prefetch", "run_count"): "pf_value",
    ("prefetch", "execution_count"): "pf_value",
    ("prefetch", "run_counter"): "pf_value",
    ("prefetch", "file_information_run_count"): "pf_value",
    ("prefetch", "last_run_time_utc"): "pf_value",
    ("prefetch", "last_run_time"): "pf_value",
    ("prefetch", "last_run_utc"): "pf_value",
    ("prefetch", "last_run"): "pf_value",
    ("prefetch", "last_run_timestamp"): "pf_value",
    ("prefetch", "last_execution_time"): "pf_value",
    ("prefetch", "last_execution_time_utc"): "pf_value",
    ("prefetch", "last_executed_utc"): "pf_value",
    ("prefetch", "latest_run_time_utc"): "pf_value",
    ("prefetch", "last_run_times"): "pf_value",
    ("prefetch", "last_run_times_utc"): "pf_value",
    ("prefetch", "previous_run_times"): "pf_value",
    ("prefetch", "run_times"): "pf_value",
    ("prefetch", "format_version"): "pf_value",
    ("prefetch", "version"): "pf_value",
    ("prefetch", "file_format_version"): "pf_value",
    ("prefetch", "header_version"): "pf_value",
    ("prefetch", "scca_version"): "pf_value",
    ("prefetch", "prefetch_hash_u32_hex"): "pf_value",
    ("prefetch", "prefetch_hash"): "pf_value",
    ("prefetch", "prefetch_hash_hex"): "pf_value",
    ("prefetch", "hash_u32_hex"): "pf_value",
    ("prefetch", "path_hash_u32_hex"): "pf_value",
    ("prefetch", "header_hash_u32_hex"): "pf_value",
    ("prefetch", "volume_serial_u32_hex"): "pf_value",
    ("prefetch", "volume_serial_number_u32_hex"): "pf_value",
    ("prefetch", "volume_serial_number"): "pf_value",
    ("prefetch", "volume_serial"): "pf_value",
    ("prefetch", "volume_serial_hex"): "pf_value",
    ("prefetch", "volume_information_serial_number_u32_hex"): "pf_value",
    ("prefetch", "volume_device_path"): "pf_value",
    ("prefetch", "volume_path"): "pf_value",
    ("prefetch", "volume_creation_time_utc"): "pf_value",
    ("prefetch", "volume_creation_time"): "pf_value",
    ("prefetch", "volume_count"): "pf_value",
    ("prefetch", "number_of_volumes"): "pf_value",
    ("prefetch", "file_names"): "pf_value",
    ("prefetch", "filenames"): "pf_value",
    ("prefetch", "filename_strings"): "pf_value",
    ("prefetch", "loaded_file_names"): "pf_value",
    ("prefetch", "file_count"): "pf_value",
    ("prefetch", "number_of_file_metrics_entries"): "pf_value",
    ("prefetch", "is_compressed"): "pf_value",
    ("prefetch", "file_size_bytes"): "pf_value",
    ("prefetch", "file_size"): "pf_value",
    ("prefetch", "header_file_size"): "pf_value",
    ("prefetch", "header_file_size_bytes"): "pf_value",
    ("prefetch", "scca_file_size_bytes"): "pf_value",
    ("prefetch", "header_file_size_matches"): "pf_value",
    ("prefetch", "file_size_matches"): "pf_value",
    ("prefetch", "file_size_matches_header"): "pf_value",
    ("prefetch", "header_size_matches"): "pf_value",
    ("prefetch", "executable_name_length"): "pf_value",
    ("prefetch", "executable_name_char_count"): "pf_value",
    ("prefetch", "executable_name_chars"): "pf_value",
    ("prefetch", "exe_name_length"): "pf_value",
    ("prefetch", "compression_format"): "pf_value",
    ("prefetch", "compression"): "pf_value",
    ("prefetch", "compression_algorithm"): "pf_value",
    ("prefetch", "compression_type"): "pf_value",
    ("prefetch", "mam_compression_format"): "pf_value",
    ("prefetch", "uncompressed_size_bytes"): "pf_value",
    ("prefetch", "uncompressed_size"): "pf_value",
    ("prefetch", "decompressed_size_bytes"): "pf_value",
    ("prefetch", "decompressed_size"): "pf_value",
    ("prefetch", "mam_uncompressed_size_bytes"): "pf_value",
    ("prefetch", "mam_uncompressed_size"): "pf_value",
    ("prefetch", "mam_crc32_u32_hex"): "pf_value",
    ("prefetch", "mam_crc32_valid"): "pf_value",
}

_MAX_OUT = 32 << 20
_BUDGET_S = 0.6   # in-window: a hostile size field must not eat the Mastery clock -> None


def _xpress_huffman(src, pos, out_size):
    """MS-XCA 2.2 LZXpress Huffman decompression of src[pos:] to out_size bytes (raises on bad input)."""
    out = bytearray()
    n = len(src)
    deadline = time.monotonic() + _BUDGET_S
    rd16 = lambda p: src[p] | (src[p + 1] << 8) if p + 1 < n else (src[p] if p < n else 0)  # noqa: E731
    while len(out) < out_size:
        if pos + 256 > n:
            raise ValueError("truncated huffman table")
        if time.monotonic() > deadline:
            raise ValueError("decompression budget exceeded")
        lens = []
        for b in src[pos:pos + 256]:
            lens.append(b & 15)
            lens.append(b >> 4)
        table, code = [None] * 32768, 0
        for ln in range(1, 16):
            for sym in range(512):
                if lens[sym] == ln:
                    a, z = code << (15 - ln), (code + 1) << (15 - ln)
                    if z > 32768:
                        raise ValueError("oversubscribed huffman table")
                    table[a:z] = [(sym, ln)] * (z - a)
                    code += 1
            code <<= 1
        cur = pos + 256
        bits = ((rd16(cur) << 16) | rd16(cur + 2)) & 0xFFFFFFFF
        cur += 4
        extra = 16
        block_end = min(len(out) + 65536, out_size)
        while len(out) < block_end:
            ent = table[bits >> 17]
            if ent is None:
                raise ValueError("bad huffman code")
            sym, ln = ent
            bits = (bits << ln) & 0xFFFFFFFF
            extra -= ln
            if extra < 0:
                bits = (bits + (rd16(cur) << -extra)) & 0xFFFFFFFF
                extra += 16
                cur += 2
            if sym < 256:
                out.append(sym)
                continue
            sym -= 256
            mlen, obits = sym & 15, sym >> 4
            if mlen == 15:
                if cur >= n:
                    raise ValueError("truncated match length")
                mlen = src[cur]
                cur += 1
                if mlen == 255:
                    mlen = rd16(cur)
                    cur += 2
                    if mlen < 15:
                        raise ValueError("bad match length")
                    mlen -= 15
                mlen += 15
            mlen += 3
            moff = (bits >> (32 - obits) if obits else 0) + (1 << obits)
            bits = (bits << obits) & 0xFFFFFFFF
            extra -= obits
            if extra < 0:
                bits = (bits + (rd16(cur) << -extra)) & 0xFFFFFFFF
                extra += 16
                cur += 2
            if moff > len(out):
                raise ValueError("match before start")
            st = len(out) - moff
            if moff >= mlen:
                out += out[st:st + mlen]
            else:
                for i in range(mlen):
                    out.append(out[st + i])
        pos = cur
    return bytes(out[:out_size])


def _lznt1(src, pos, out_size):
    """MS-XCA 2.5 LZNT1 decompression of src[pos:] (4 KiB chunks) up to out_size bytes (raises on bad input)."""
    out = bytearray()
    n = len(src)
    deadline = time.monotonic() + _BUDGET_S
    while pos + 2 <= n and len(out) < out_size:
        if time.monotonic() > deadline:
            raise ValueError("decompression budget exceeded")
        hdr = src[pos] | (src[pos + 1] << 8)
        pos += 2
        if hdr == 0:
            break
        end = pos + (hdr & 0x0FFF) + 1
        if end > n:
            raise ValueError("truncated lznt1 chunk")
        if not hdr & 0x8000:
            out += src[pos:end]
            pos = end
            continue
        start = len(out)
        while pos < end:
            flags = src[pos]
            pos += 1
            for bit in range(8):
                if pos >= end:
                    break
                if not flags >> bit & 1:
                    out.append(src[pos])
                    pos += 1
                    continue
                if pos + 2 > end:
                    raise ValueError("truncated lznt1 token")
                tok = src[pos] | (src[pos + 1] << 8)
                pos += 2
                cpos, shift = len(out) - start - 1, 0
                while cpos >= 0x10:
                    cpos >>= 1
                    shift += 1
                moff = (tok >> (12 - shift)) + 1
                mlen = (tok & (0x0FFF >> shift)) + 3
                if moff > len(out) - start:
                    raise ValueError("lznt1 match before chunk start")
                st = len(out) - moff
                for i in range(mlen):
                    out.append(out[st + i])
        pos = end
    return bytes(out[:out_size])


def _xpress_plain(src, pos, out_size):
    """MS-XCA 2.4 plain LZ77 Xpress decompression of src[pos:] up to out_size bytes (raises on bad input)."""
    out = bytearray()
    n = len(src)
    deadline = time.monotonic() + _BUDGET_S
    flags = nflags = 0
    half = None
    while len(out) < out_size:
        if nflags == 0:
            if pos + 4 > n:
                break
            if time.monotonic() > deadline:
                raise ValueError("decompression budget exceeded")
            flags, = struct.unpack_from("<I", src, pos)
            pos += 4
            nflags = 32
        nflags -= 1
        if not flags >> nflags & 1:
            if pos >= n:
                break
            out.append(src[pos])
            pos += 1
            continue
        if pos + 2 > n:
            break
        tok = src[pos] | (src[pos + 1] << 8)
        pos += 2
        mlen, moff = tok & 7, (tok >> 3) + 1
        if mlen == 7:
            if half is None:
                mlen, half = src[pos] & 15, pos
                pos += 1
            else:
                mlen, half = src[half] >> 4, None
            if mlen == 15:
                mlen = src[pos]
                pos += 1
                if mlen == 255:
                    mlen = src[pos] | (src[pos + 1] << 8)
                    pos += 2
                    if mlen == 0:
                        mlen, = struct.unpack_from("<I", src, pos)
                        pos += 4
                    if mlen < 22:
                        raise ValueError("bad xpress match length")
                    mlen -= 22
                mlen += 15
            mlen += 7
        mlen += 3
        if moff > len(out):
            raise ValueError("xpress match before start")
        st = len(out) - moff
        if moff >= mlen:
            out += out[st:st + mlen]
        else:
            for i in range(mlen):
                out.append(out[st + i])
    return bytes(out[:out_size])


_MAM = {2: ("lznt1", _lznt1), 3: ("xpress", _xpress_plain), 4: ("xpress_huffman", _xpress_huffman)}


def _scca(b):
    """(SCCA bytes, wrapper info dict) | "none" (not a prefetch file) | None (MAM that does not decompress)."""
    if not isinstance(b, (bytes, bytearray)) or len(b) < 8:
        return "none"
    b = bytes(b)
    if b[:3] == b"MAM":
        kind = _MAM.get(b[3] & 0x0F)
        if kind is None:
            return None
        size, = struct.unpack_from("<I", b, 4)
        if not 84 <= size <= _MAX_OUT:
            return None
        info = {"format": kind[0], "size": size, "crc": None, "crc_ok": None}
        if b[3] & 0x80:
            if len(b) < 12:
                return None
            crc, = struct.unpack_from("<I", b, 8)
            info["crc"], info["crc_ok"] = crc, zlib.crc32(b[:8] + b"\0\0\0\0" + b[12:]) == crc
        try:
            raw = kind[1](b, 12 if b[3] & 0x80 else 8, size)
        except (ValueError, IndexError, TypeError, struct.error):
            return None
        return (raw, info) if raw[4:8] == b"SCCA" else None
    if b[4:8] == b"SCCA":
        return b, None
    return "none"


def _u32(b, o):
    return struct.unpack_from("<I", b, o)[0] if o + 4 <= len(b) else None


def _u64(b, o):
    return struct.unpack_from("<Q", b, o)[0] if o + 8 <= len(b) else None


def _utf16z(b, o, nbytes):
    s = b[o:o + nbytes]
    for i in range(0, len(s) - 1, 2):
        if s[i:i + 2] == b"\0\0":
            s = s[:i]
            break
    return s[:len(s) & ~1].decode("utf-16-le", "replace")


def _filetime(v):
    if v is None:
        return None
    if not v:
        return "none"
    try:
        t = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=v // 10)
    except OverflowError:
        return None
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


_KNOWN = (17, 23, 26, 30, 31)


def _last_runs(b, ver):
    if ver == 17:
        return [_u64(b, 0x78)]
    if ver == 23:
        return [_u64(b, 0x80)]
    if ver in (26, 30, 31):
        return [_u64(b, 0x80 + 8 * i) for i in range(8)]
    return None


def _run_count(b, ver):
    off = {17: 0x90, 23: 0x98, 26: 0xD0}.get(ver)
    if ver in (30, 31):   # 220-B file information (metrics @0x130) vs the 212-B "variant 2" (metrics @0x128)
        off = 0xC8 if _u32(b, 84) == 0x128 else 0xD0
    return _u32(b, off) if off else None


def _volume(b, ver):
    """(device path, serial, creation FILETIME) of the first volume entry, "none" if none, None if unreadable."""
    voff, nvol = _u32(b, 108), _u32(b, 112)
    if voff is None or nvol is None:
        return None
    if nvol == 0:
        return "none"
    if voff + 20 > len(b):
        return None
    dp, dn = _u32(b, voff), _u32(b, voff + 4)
    path = _utf16z(b, voff + dp, 2 * dn) if dp and voff + dp + 2 * dn <= len(b) else None
    return path, _u32(b, voff + 16), _u64(b, voff + 8)


def _file_names(b):
    off, size = _u32(b, 100), _u32(b, 104)
    if off is None or size is None or off + size > len(b):
        return None
    s = b[off:off + size]
    out, i = [], 0
    while i + 1 < len(s):
        j = i
        while j + 1 < len(s) and s[j:j + 2] != b"\0\0":
            j += 2
        out.append(s[i:j].decode("utf-16-le", "replace"))
        i = j + 2
    return out


_NAME = ("executable_name", "executable_filename", "executable_file_name", "exe_name", "executable",
         "header_executable_name")
_FSIZE = ("file_size_bytes", "file_size", "header_file_size", "header_file_size_bytes", "scca_file_size_bytes")
_FSIZE_OK = ("header_file_size_matches", "file_size_matches", "file_size_matches_header", "header_size_matches")
_NAME_LEN = ("executable_name_length", "executable_name_char_count", "executable_name_chars", "exe_name_length")
_COMP = ("compression_format", "compression", "compression_algorithm", "compression_type", "mam_compression_format")
_USIZE = ("uncompressed_size_bytes", "uncompressed_size", "decompressed_size_bytes", "decompressed_size",
          "mam_uncompressed_size_bytes", "mam_uncompressed_size")


def _value(b, field, mam):
    ver = _u32(b, 0)
    f = field
    for suf in ("_utc",):
        if f.endswith(suf) and f not in ("last_run_times_utc",):
            f = f[:-len(suf)]
    # fixed header / wrapper: every version, known or not
    if f in ("format_version", "version", "file_format_version", "header_version", "scca_version"):
        return ver
    if f == "is_compressed":
        return mam is not None
    if f in _COMP:
        return mam["format"] if mam else "none"
    if f in _USIZE:
        return mam["size"] if mam else "none"
    if f == "mam_crc32_u32_hex":
        return Hex(mam["crc"], 8) if mam and mam["crc"] is not None else "none"
    if f == "mam_crc32_valid":
        return mam["crc_ok"] if mam and mam["crc"] is not None else "none"
    if f in _NAME or f in _NAME_LEN:
        name = _utf16z(b, 16, 60).strip() if len(b) >= 76 else None
        if name is None:
            return None
        if f in _NAME_LEN:
            return len(name)
        return name if name else "none"
    if f in _FSIZE:
        return _u32(b, 12)
    if f in _FSIZE_OK:
        return _u32(b, 12) == len(b)
    if "hash" in f:
        h = _u32(b, 76)
        return Hex(h, 8) if h is not None else None
    if ver not in _KNOWN:
        return None   # version-dependent layout of an unknown SCCA version: cannot answer
    if f in ("run_count", "execution_count", "run_counter", "file_information_run_count"):
        return _run_count(b, ver)
    if f in ("last_run_times", "last_run_times_utc", "previous_run_times", "run_times"):
        lr = _last_runs(b, ver)
        if lr is None or None in lr:
            return None
        return [_filetime(v) for v in lr if v]
    if f.startswith("last_") or f == "latest_run_time":
        lr = _last_runs(b, ver)
        return _filetime(lr[0]) if lr else None
    if f in ("volume_count", "number_of_volumes"):
        return _u32(b, 112)
    if f in ("file_names", "filenames", "filename_strings", "loaded_file_names"):
        return _file_names(b)
    if f in ("file_count", "number_of_file_metrics_entries"):
        return _u32(b, 88)
    if f.startswith("volume"):
        v = _volume(b, ver)
        if not isinstance(v, tuple):
            return v
        path, serial, ctime = v
        if "serial" in f:
            return Hex(serial, 8) if serial is not None else None
        if "creation" in f:
            return _filetime(ctime)
        return path if path else None
    return None


def pf_value(data, ctx):
    """prefetch.<field> of an SCCA / MAM-compressed (Xpress-Huffman, Xpress, LZNT1) .pf member."""
    try:
        s = _scca(data)
        if not isinstance(s, tuple):
            return s
        b, mam = s
        if len(b) < 84:
            return None
        return _value(b, (ctx or {}).get("field") or "", mam)
    except (struct.error, ValueError, IndexError, TypeError, OverflowError, UnicodeError):
        return None
