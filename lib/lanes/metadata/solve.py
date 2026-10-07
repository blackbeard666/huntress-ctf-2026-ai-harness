#!/usr/bin/env python3
"""Lane-level, day-independent METADATA-FORENSICS solver (prototype, zero LLM, stdlib + optional pyzipper).

    metadata_lane.py --contract <contract.json> --artifacts <dir> [--explain out.json] [--min-conf 2]
    -> last stdout line: {answer_id: value}

Model of the lane (days 1-6): every question asks for ONE byte-derived fact about ONE archive member.
  era 1 (Day 1-2):  natural language + answer-id slug   e.g. "What is its MD5 digest?"  id "roster-md5"
  era 2 (Day 3+):   "Determine <fmt>.<field> for <file>."  id "[setN.]dNN-<fmt>-NNN-<fmt>-<field-with-dashes>"
Each day introduces a new (fmt, field) family; impostors (magic != claimed format) answer the literal `none`.

Tiers
  1. REGISTRY  (fmt, field) -> extractor, each GM-confirmed (tagged with the day that confirmed it). conf 3.
  2. GENERIC   magic-sniff -> pure-Python structural parser -> flat {canonical_key: value} facts with the
               confirmed formatting laws ('{w}x{h}', '{major}.{minor}', true/false, base-10 ints, lowercase hex,
               absent -> none), then field-name -> key matching. conf 2 = emit, conf 1 = candidate only.
  Impostor law (Day 6, applied to every structural format): claimed fmt family != sniffed family -> 'none'.

Env: METADATA_DISABLE_DAYS=4,5|all  disables registry entries confirmed on those days (leave-one-day-out tests).
     METADATA_MIN_CONF=2           emission threshold (3 = registry only, 1 = also emit fuzzy candidates).
"""
import argparse
import binascii
import hashlib
import io
import json
import os
import re
import struct
import sys
import time
import zipfile
import zlib
from pathlib import Path


def _find_root():
    cands = [os.environ.get("HCTF_ROOT", "")] + [str(p) for p in Path(__file__).resolve().parents] + [os.getcwd()]
    for c in cands:
        if c and (Path(c) / "lib" / "common.py").is_file():
            return c
    return None


ROOT = _find_root()
if ROOT and ROOT not in sys.path:
    sys.path.insert(0, ROOT)
try:
    from lib.common import container_by_sha, delivery_missing, ZIP_PASSWORDS, _ZipFile
except Exception:  # standalone (Homebase copy without lib/)
    container_by_sha = lambda root, contract, container: None
    delivery_missing = lambda root, contract, container: False
    ZIP_PASSWORDS = [b"infected", b"flare", b"malware", b"virus", b"huntress"]
    try:
        import pyzipper
        _ZipFile = pyzipper.AESZipFile
    except ImportError:
        _ZipFile = zipfile.ZipFile
try:
    from lib.knowledge import JPEG_DIMENSIONS_FMT, PNG_DIMENSIONS_FMT, PDF_HEADER_VERSION_FMT
except Exception:
    JPEG_DIMENSIONS_FMT = PNG_DIMENSIONS_FMT = "{width}x{height}"
    PDF_HEADER_VERSION_FMT = "{major}.{minor}"

DIM_FMT = "{width}x{height}"  # confirmed for JPEG SOF (D4) and PNG IHDR (D5); applied to every WxH fact


def log(*a):
    print(*a, file=sys.stderr)


def B(x):
    return "true" if x else "false"


def dims(w, h):
    return DIM_FMT.format(width=w, height=h)


def canon(s):
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", str(s).lower())).strip("_")


def snake(name):
    """CamelCase tag name -> snake (DateTimeOriginal -> date_time_original, GPSLatitude -> gps_latitude)."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return canon(s)


def ver(major, minor):
    return PDF_HEADER_VERSION_FMT.format(major=major, minor=minor)


# =====================================================================================================  facts
class Facts:
    """Flat canonical-key -> (value, conf) map. First writer wins (parsers add the most specific source first)."""

    def __init__(self):
        self.d = {}

    def add(self, keys, value, conf=2):
        if value is None:
            return
        if callable(value):  # lazy (hashes of large members): evaluated on lookup only
            for k in ([keys] if isinstance(keys, str) else keys):
                k = canon(k)
                if k and k not in self.d:
                    self.d[k] = (value, conf)
            return
        if isinstance(value, bool):
            value = B(value)
        if isinstance(value, bytes):
            value = value.decode("latin-1")
        value = str(value)
        for k in ([keys] if isinstance(keys, str) else keys):
            k = canon(k)
            if k and k not in self.d:
                self.d[k] = (value, conf)

    def get(self, k):
        v, c = self.d[k]
        if callable(v):
            v = v()
            self.d[k] = (v, c)
        return v, c

    def absent(self, keys, conf=2):
        """Field is part of this format's schema but not in this file -> literal none."""
        for k in ([keys] if isinstance(keys, str) else keys):
            k = canon(k)
            if k not in self.d:
                self.d[k] = ("none", conf)

    def wh(self, prefixes, w, h, conf=2):
        for p in prefixes:
            pre = (p + "_") if p else ""
            self.add([pre + "width", pre + "width_pixels"], w, conf)
            self.add([pre + "height", pre + "height_pixels"], h, conf)
            self.add([pre + "dimensions", pre + "dimensions_pixels", pre + "pixel_dimensions",
                      pre + "size_pixels", pre + "resolution_pixels"], dims(w, h), conf)


# =====================================================================================================  sniffing
LEAD = b"\xef\xbb\xbf\x00\t\n\x0c\r "  # BOM / whitespace a PDF reader skips before %PDF-


def sniff(data):
    h = data[:64]
    if h.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if h[:3] == b"\xff\xd8\xff":
        return "jpeg"
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if data.lstrip(LEAD)[:5] == b"%PDF-":
        return "pdf"
    if h[:4] in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"):
        return "zip"
    if h[:4] in (b"II*\x00", b"MM\x00*"):
        return "tiff"
    if h[:4] == b"RIFF" and len(h) >= 12:
        return {b"WEBP": "webp", b"WAVE": "wav", b"AVI ": "avi"}.get(h[8:12], "riff")
    if h[:2] == b"BM" and len(data) >= 26 and struct.unpack_from("<I", data, 14)[0] in (12, 40, 52, 56, 64, 108, 124):
        return "bmp"
    if h[:4] == b"\x00\x00\x01\x00" and len(data) >= 6:
        return "ico"
    if h[:4] == b"\x7fELF":
        return "elf"
    if h[:2] == b"MZ":
        if len(data) >= 0x40:
            off = struct.unpack_from("<I", data, 0x3C)[0]
            if data[off:off + 4] == b"PE\x00\x00":
                return "pe"
        return "mz"
    if h[:2] == b"\x1f\x8b":
        return "gzip"
    if h.startswith(b"SQLite format 3\x00"):
        return "sqlite"
    if h[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return "ole"
    if h[:4] == b"fLaC":
        return "flac"
    if h[:4] == b"OggS":
        return "ogg"
    if h[:3] == b"ID3" or (len(h) > 2 and h[0] == 0xFF and (h[1] & 0xE0) == 0xE0 and (h[1] & 0x06)):
        return "mp3"
    if h[4:8] == b"ftyp":
        return "mp4"
    if h[:3] == b"BZh":
        return "bzip2"
    if h[:6] == b"\xfd7zXZ\x00":
        return "xz"
    if h[:6] == b"7z\xbc\xaf\x27\x1c":
        return "7z"
    if h[:4] == b"Rar!":
        return "rar"
    if h[:4] in (b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf", b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe"):
        return "macho"
    if h[:4] == b"\xca\xfe\xba\xbe":
        return "class"
    if h[:4] == b"dex\n":
        return "dex"
    if h[:5] == b"{\\rtf":
        return "rtf"
    if h[:4] == b"%!PS":
        return "postscript"
    if len(data) > 262 and data[257:262] == b"ustar":
        return "tar"
    if textish(data):
        return "text"
    return "data"


def textish(data):
    if data[:3] == b"\xef\xbb\xbf" or data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return True
    s = data[:4096]
    if not s:
        return True
    try:
        t = s.decode("utf-8")
    except UnicodeDecodeError:
        try:
            t = s[:-3].decode("utf-8")
        except UnicodeDecodeError:
            return False
    return sum(c.isprintable() or c in "\r\n\t\f" for c in t) / max(len(t), 1) > 0.95


# claimed format (question prefix) -> acceptable sniffed families. None = no impostor check (any bytes qualify).
FAMILY = {
    "jpeg": {"jpeg"}, "jpg": {"jpeg"}, "jfif": {"jpeg"}, "png": {"png"}, "apng": {"png"}, "gif": {"gif"},
    "bmp": {"bmp"}, "dib": {"bmp"}, "tiff": {"tiff"}, "tif": {"tiff"}, "webp": {"webp"}, "ico": {"ico"},
    "pdf": {"pdf"}, "zip": {"zip"}, "docx": {"zip"}, "xlsx": {"zip"}, "pptx": {"zip"}, "ooxml": {"zip"},
    "office": {"zip", "ole"}, "jar": {"zip"}, "apk": {"zip"}, "odt": {"zip"}, "ods": {"zip"}, "epub": {"zip"},
    "gzip": {"gzip"}, "gz": {"gzip"}, "elf": {"elf"}, "pe": {"pe"}, "exe": {"pe"}, "dll": {"pe"},
    "wav": {"wav"}, "wave": {"wav"}, "riff": {"wav", "webp", "avi", "riff"}, "avi": {"avi"},
    "mp3": {"mp3"}, "id3": {"mp3"}, "flac": {"flac"}, "ogg": {"ogg"}, "sqlite": {"sqlite"}, "sqlite3": {"sqlite"},
    "ole": {"ole"}, "cfb": {"ole"}, "doc": {"ole"}, "xls": {"ole"}, "ppt": {"ole"}, "msi": {"ole"},
    "mp4": {"mp4"}, "mov": {"mp4"}, "m4a": {"mp4"}, "heic": {"mp4"}, "bmff": {"mp4"}, "tar": {"tar"},
    "7z": {"7z"}, "rar": {"rar"}, "bzip2": {"bzip2"}, "xz": {"xz"}, "macho": {"macho"}, "dex": {"dex"},
    "class": {"class"}, "rtf": {"rtf"}, "exif": {"jpeg", "tiff", "png", "webp"},
}
NO_IMPOSTOR = {"text", "txt", "csv", "json", "xml", "html", "file", "bytes", "raw", "hash", "data", "archive",
               "member", "artifact", "identity", "encoding"}
# fields that describe the bytes regardless of the claimed format (never subject to the impostor law)
FILE_LEVEL = re.compile(r"^(filename|file_name|name|basename|extension|size(_bytes)?|file_size(_bytes)?|length|"
                        r"md5|sha1|sha224|sha256|sha384|sha512|crc32|magic.*|first_\d+.*|.*prefix_hex.*|"
                        r"detected_(type|format)|true_(type|format)|actual_(type|format)|magic_(type|format)|"
                        r"content_type|is_.*|.*impostor.*|.*_matches_extension|extension_matches.*|entropy.*)$")


# =====================================================================================================  helpers
def u8(b, o):
    return b[o]


def u16(b, o, e="<"):
    return struct.unpack_from(e + "H", b, o)[0]


def u32(b, o, e="<"):
    return struct.unpack_from(e + "I", b, o)[0]


def cstr(b):
    return b.split(b"\x00", 1)[0].decode("utf-8", "replace").strip()


def numfmt(x):
    """Rational/float -> shortest faithful decimal (72/1 -> '72', 0.5 -> '0.5')."""
    if isinstance(x, tuple):
        n, d = x
        if d == 0:
            return None
        x = n / d
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return ("%.6f" % x).rstrip("0").rstrip(".") if isinstance(x, float) else str(x)


# =====================================================================================================  file-level
def file_facts(F, data, name):
    F.add(["filename", "file_name", "name", "basename"], name.split("/")[-1] if name else None)
    ext = name.rsplit(".", 1)[-1].lower() if name and "." in name else ""
    F.add(["extension", "file_extension"], ext or "none")
    F.add(["size_bytes", "size", "file_size", "file_size_bytes", "length", "byte_count"], len(data))
    for alg in ("md5", "sha1", "sha224", "sha256", "sha384", "sha512"):
        F.add([alg, alg + "_digest", alg + "_hash"], lambda alg=alg: hashlib.new(alg, data).hexdigest())
    F.add(["crc32"], lambda: "%08x" % (binascii.crc32(data) & 0xFFFFFFFF), 1)
    kind = sniff(data)
    F.add(["detected_type", "detected_format", "true_type", "true_format", "actual_type", "actual_format",
           "magic_type", "magic_format", "content_type"], kind, 1)
    for n in (2, 4, 8, 16, 32):
        F.add([f"magic_prefix_hex_{n}", f"first_{n}_bytes_hex", f"prefix_hex_{n}"], data[:n].hex())
    F.add(["magic_hex", "magic_bytes_hex", "magic"], data[:4].hex(), 1)
    return kind


# =====================================================================================================  text
BOMS = [(b"\x00\x00\xfe\xff", "utf32be"), (b"\xff\xfe\x00\x00", "utf32le"), (b"\xef\xbb\xbf", "utf8"),
        (b"\xfe\xff", "utf16be"), (b"\xff\xfe", "utf16le")]
BOM_LABEL = {"utf8": "utf-8", "utf16le": "utf-16le", "utf16be": "utf-16be", "utf32le": "utf-32le", "utf32be": "utf-32be"}


def text_facts(F, data):
    bom = next((n for sig, n in BOMS if data.startswith(sig)), None)
    for _, n in BOMS:  # D3 law: <enc>_bom_present = 'true'/'false' from the raw leading bytes
        F.add([f"{n}_bom_present", f"{n}_bom", f"has_{n}_bom", f"{n.replace('utf', 'utf_')}_bom_present"], bom == n)
    F.add(["bom_present", "has_bom", "byte_order_mark_present"], bom is not None)
    F.add(["bom_type", "bom_encoding", "bom"], BOM_LABEL.get(bom, "none"), 1)
    F.add(["bom_hex", "bom_bytes_hex"], next((s.hex() for s, n in BOMS if n == bom), "none"), 1)
    enc = BOM_LABEL.get(bom)
    body = data[len(next((s for s, n in BOMS if n == bom), b"")):]
    try:
        txt = body.decode(enc.replace("-", "_") if enc else "utf-8")
        if not enc:
            enc = "ascii" if all(b < 0x80 for b in body) else "utf-8"
    except (UnicodeDecodeError, LookupError):
        txt, enc = body.decode("latin-1"), "unknown"
    F.add(["encoding", "text_encoding", "charset", "detected_encoding"], enc, 1)
    crlf, cr, lf = txt.count("\r\n"), txt.count("\r") - txt.count("\r\n"), txt.count("\n") - txt.count("\r\n")
    kinds = [k for k, n in (("crlf", crlf), ("lf", lf), ("cr", cr)) if n]
    F.add(["line_endings", "line_ending", "newline", "newline_style", "eol", "eol_style"],
          kinds[0] if len(kinds) == 1 else ("mixed" if kinds else "none"), 1)
    F.add(["crlf_present", "has_crlf"], crlf > 0)
    F.add(["lf_only", "unix_line_endings"], lf > 0 and not crlf and not cr)
    F.add(["mixed_line_endings", "mixed_newlines", "mixed_eol"], len(kinds) > 1)
    F.add(["crlf_count"], crlf)
    F.add(["lf_count"], lf)
    F.add(["cr_count"], cr)
    lines = txt.splitlines()
    F.add(["line_count", "lines"], len(lines))
    F.add(["trailing_newline", "final_newline", "trailing_newline_present", "ends_with_newline"],
          txt.endswith(("\n", "\r")))
    F.add(["null_bytes_present", "nul_present", "has_null_bytes"], b"\x00" in body if enc in ("ascii", "utf-8") else "\x00" in txt)
    F.add(["non_ascii_present", "has_non_ascii"], any(ord(c) > 127 for c in txt))
    F.add(["char_count", "character_count"], len(txt))
    F.add(["word_count"], len(txt.split()))
    F.add(["first_line"], lines[0] if lines else "none", 1)
    F.add(["tab_present", "has_tabs"], "\t" in txt)
    F.add(["zero_width_present", "invisible_chars_present"], any(c in txt for c in "​‌‍⁠﻿"))


# =====================================================================================================  PNG
PNG_STD = {"IHDR", "PLTE", "IDAT", "IEND", "tRNS", "cHRM", "gAMA", "iCCP", "sBIT", "sRGB", "cICP", "mDCv", "cLLi",
           "tEXt", "zTXt", "iTXt", "bKGD", "hIST", "pHYs", "sPLT", "eXIf", "tIME", "acTL", "fcTL", "fdAT"}
PNG_COLOR = {0: "grayscale", 2: "truecolor", 3: "indexed", 4: "grayscale_alpha", 6: "truecolor_alpha"}
PNG_CH = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


def png_chunks(data):
    i, out = 8, []
    while i + 8 <= len(data):
        ln, typ = struct.unpack_from(">I4s", data, i)
        body = data[i + 8:i + 8 + ln]
        crc = data[i + 8 + ln:i + 12 + ln]
        ok = len(crc) == 4 and struct.unpack(">I", crc)[0] == (binascii.crc32(typ + body) & 0xFFFFFFFF)
        out.append((typ.decode("latin-1"), body, ok, i))
        i += 12 + ln
        if typ == b"IEND":
            break
    return out, i


def png_facts(F, data):
    ch, end = png_chunks(data)
    ihdr = next((b for t, b, _, _ in ch if t == "IHDR"), None)
    if ihdr and len(ihdr) >= 13:
        w, h, bd, ct, cm, fm, im = struct.unpack(">IIBBBBB", ihdr[:13])
        F.wh(["ihdr", "", "image", "declared", "png"], w, h)
        F.add(["bit_depth", "ihdr_bit_depth"], bd)
        F.add(["color_type", "ihdr_color_type", "colour_type"], ct)
        F.add(["color_type_name"], PNG_COLOR.get(ct, "unknown"), 1)
        F.add(["compression_method", "ihdr_compression_method"], cm)
        F.add(["filter_method", "ihdr_filter_method"], fm)
        F.add(["interlace_method", "ihdr_interlace_method", "interlace"], im)
        F.add(["interlaced", "is_interlaced"], im == 1)
        F.add(["channels", "channel_count"], PNG_CH.get(ct))
        F.add(["bits_per_pixel"], bd * PNG_CH.get(ct, 1))
        idat = b"".join(b for t, b, _, _ in ch if t == "IDAT")
        try:
            raw = zlib.decompressobj().decompress(idat)
            if im == 0:
                exp = h * (1 + (w * bd * PNG_CH.get(ct, 1) + 7) // 8)
                F.add(["geometry_valid", "idat_matches_ihdr", "dimensions_valid"], len(raw) == exp, 1)
            F.add(["idat_decompressed_size", "decompressed_size"], len(raw), 1)
        except zlib.error:
            pass
        F.add(["idat_size", "idat_total_size", "idat_bytes"], len(idat))
    types = [t for t, _, _, _ in ch]
    F.add(["chunk_count", "chunks", "number_of_chunks"], len(ch))
    F.add(["chunk_order", "chunk_types", "chunk_sequence", "chunk_list"], ",".join(types), 1)
    F.add(["first_chunk", "first_chunk_type"], types[0] if types else "none")
    F.add(["last_chunk", "last_chunk_type"], types[-1] if types else "none")
    F.add(["idat_count", "idat_chunk_count"], types.count("IDAT"))
    seen = set(types)
    for t in PNG_STD | seen:
        F.add([f"{t}_present", f"{t}_chunk_present", f"has_{t}", f"has_{t}_chunk"], t in seen)
        F.add([f"{t}_count", f"{t}_chunk_count"], types.count(t))
    odd = [t for t in types if t not in PNG_STD]
    F.add(["unexpected_chunk", "unexpected_chunk_type", "nonstandard_chunk", "non_standard_chunk", "unknown_chunk",
           "custom_chunk", "private_chunk", "passenger_chunk", "extra_chunk", "unexpected_chunk_name"],
          odd[0] if odd else "none")
    F.add(["unexpected_chunk_count", "nonstandard_chunk_count", "unknown_chunk_count"], len(odd))
    F.add(["unexpected_chunk_present", "nonstandard_chunk_present", "has_passenger", "passenger_present"], bool(odd))
    bad = [t for t, _, ok, _ in ch if not ok]
    F.add(["crc_valid", "crcs_valid", "all_crc_valid", "crc_ok"], not bad)
    F.add(["crc_error_count", "bad_crc_count", "crc_errors"], len(bad))
    F.add(["bad_crc_chunk", "crc_error_chunk", "invalid_crc_chunk", "corrupt_chunk"], bad[0] if bad else "none")
    tail = len(data) - end if "IEND" in seen else 0
    F.add(["trailing_bytes", "trailing_data_size", "trailing_bytes_count", "bytes_after_iend", "appended_bytes",
           "trailing_data_bytes"], max(tail, 0))
    F.add(["trailing_data_present", "trailing_data", "has_trailing_data", "data_after_iend", "appended_data_present"],
          tail > 0)
    F.add(["iend_present", "has_iend"], "IEND" in seen)
    for t, b, _, _ in ch:
        if t == "tEXt" and b"\x00" in b:
            k, v = b.split(b"\x00", 1)
            F.add([f"text_{k.decode('latin-1')}", f"text_{snake(k.decode('latin-1'))}", snake(k.decode("latin-1"))],
                  v.decode("latin-1"))
        elif t == "zTXt" and b"\x00" in b:
            k, v = b.split(b"\x00", 1)
            try:
                F.add([f"text_{snake(k.decode('latin-1'))}", snake(k.decode("latin-1"))],
                      zlib.decompress(v[1:]).decode("latin-1"))
            except zlib.error:
                pass
        elif t == "iTXt" and b"\x00" in b:
            k, rest = b.split(b"\x00", 1)
            try:
                cf = rest[0]
                _, _, rest2 = rest[2:].split(b"\x00", 2)
                v = zlib.decompress(rest2) if cf else rest2
                F.add([f"text_{snake(k.decode('latin-1'))}", snake(k.decode("latin-1"))], v.decode("utf-8", "replace"))
            except Exception:
                pass
        elif t == "pHYs" and len(b) >= 9:
            x, y, unit = struct.unpack(">IIB", b[:9])
            F.add(["phys_pixels_per_unit", "phys_ppu", "pixels_per_unit"], dims(x, y), 1)
            F.add(["phys_unit", "phys_unit_specifier"], unit)
            if unit == 1:
                F.add(["dpi", "phys_dpi"], dims(round(x * 0.0254), round(y * 0.0254)), 1)
        elif t == "gAMA" and len(b) >= 4:
            F.add(["gamma", "gama", "gama_value"], struct.unpack(">I", b[:4])[0])
        elif t == "sRGB" and b:
            F.add(["srgb_rendering_intent", "rendering_intent"], b[0])
        elif t == "iCCP" and b"\x00" in b:
            F.add(["icc_profile_name", "iccp_profile_name", "iccp_name"], b.split(b"\x00", 1)[0].decode("latin-1"))
        elif t == "tIME" and len(b) >= 7:
            y, mo, d, hh, mi, ss = struct.unpack(">HBBBBB", b[:7])
            F.add(["modification_time", "time", "last_modified", "time_chunk"],
                  f"{y:04d}-{mo:02d}-{d:02d}T{hh:02d}:{mi:02d}:{ss:02d}", 1)
        elif t == "acTL" and len(b) >= 8:
            nf, npl = struct.unpack(">II", b[:8])
            F.add(["frame_count", "num_frames", "actl_num_frames", "animation_frames"], nf)
            F.add(["num_plays", "loop_count", "actl_num_plays"], npl)
        elif t == "eXIf":
            tiff_facts(F, b, prefix="exif")
    if "eXIf" not in seen:
        F.add(["exif_present", "has_exif"], False)
        F.absent(["exif_" + snake(n) for n in COMMON_EXIF] + ["exif_orientation", "exif_dimensions_pixels"])
    if "acTL" not in seen:
        F.add(["frame_count", "num_frames"], 1, 1)
        F.add(["animated", "is_animated"], False)
    else:
        F.add(["animated", "is_animated"], True)


# =====================================================================================================  TIFF/EXIF
TAGS = {0x0100: "ImageWidth", 0x0101: "ImageLength", 0x0102: "BitsPerSample", 0x0103: "Compression",
        0x0106: "PhotometricInterpretation", 0x010E: "ImageDescription", 0x010F: "Make", 0x0110: "Model",
        0x0111: "StripOffsets", 0x0112: "Orientation", 0x0115: "SamplesPerPixel", 0x011A: "XResolution",
        0x011B: "YResolution", 0x0128: "ResolutionUnit", 0x0131: "Software", 0x0132: "DateTime", 0x013B: "Artist",
        0x013C: "HostComputer", 0x0213: "YCbCrPositioning", 0x8298: "Copyright", 0x8769: "ExifIFDPointer",
        0x8825: "GPSInfoIFDPointer", 0x829A: "ExposureTime", 0x829D: "FNumber", 0x8822: "ExposureProgram",
        0x8827: "ISOSpeedRatings", 0x9000: "ExifVersion", 0x9003: "DateTimeOriginal", 0x9004: "DateTimeDigitized",
        0x9010: "OffsetTime", 0x9011: "OffsetTimeOriginal", 0x9201: "ShutterSpeedValue", 0x9202: "ApertureValue",
        0x9209: "Flash", 0x920A: "FocalLength", 0x927C: "MakerNote", 0x9286: "UserComment",
        0x9290: "SubSecTime", 0xA000: "FlashpixVersion", 0xA001: "ColorSpace", 0xA002: "PixelXDimension",
        0xA003: "PixelYDimension", 0xA420: "ImageUniqueID", 0xA430: "CameraOwnerName", 0xA431: "BodySerialNumber",
        0xA432: "LensSpecification", 0xA433: "LensMake", 0xA434: "LensModel", 0x9C9B: "XPTitle",
        0x9C9C: "XPComment", 0x9C9D: "XPAuthor", 0x9C9E: "XPKeywords", 0x9C9F: "XPSubject"}
GPS_TAGS = {0: "GPSVersionID", 1: "GPSLatitudeRef", 2: "GPSLatitude", 3: "GPSLongitudeRef", 4: "GPSLongitude",
            5: "GPSAltitudeRef", 6: "GPSAltitude", 7: "GPSTimeStamp", 18: "GPSMapDatum", 29: "GPSDateStamp"}
TSIZE = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}
COMMON_EXIF = ["Make", "Model", "Orientation", "Software", "DateTime", "Artist", "Copyright", "ImageDescription",
               "DateTimeOriginal", "DateTimeDigitized", "LensModel", "BodySerialNumber", "CameraOwnerName",
               "GPSLatitude", "GPSLongitude", "UserComment", "PixelXDimension", "PixelYDimension"]


def ifd_read(t, off, e, names, depth=0):
    out = {}
    if depth > 4 or off + 2 > len(t):
        return out, 0
    n = u16(t, off, e)
    for k in range(min(n, 512)):
        p = off + 2 + 12 * k
        if p + 12 > len(t):
            break
        tag, typ, cnt = struct.unpack_from(e + "HHI", t, p)
        sz = TSIZE.get(typ, 1) * cnt
        vo = p + 8 if sz <= 4 else u32(t, p + 8, e)
        raw = t[vo:vo + sz]
        if len(raw) < sz:
            continue
        if typ == 2:
            val = cstr(raw)
        elif typ in (3, 8):
            vals = struct.unpack(e + ("H" if typ == 3 else "h") * cnt, raw)
            val = vals[0] if cnt == 1 else list(vals)
        elif typ in (4, 9):
            vals = struct.unpack(e + ("I" if typ == 4 else "i") * cnt, raw)
            val = vals[0] if cnt == 1 else list(vals)
        elif typ in (5, 10):
            vals = [struct.unpack_from(e + ("II" if typ == 5 else "ii"), raw, 8 * j) for j in range(cnt)]
            val = vals[0] if cnt == 1 else vals
        elif typ == 1:
            val = raw[0] if cnt == 1 else list(raw)
        else:
            val = raw
        out[names.get(tag, "Tag0x%04X" % tag)] = val
    nxt = u32(t, off + 2 + 12 * n, e) if off + 6 + 12 * n <= len(t) else 0
    return out, nxt


def fmt_tag(name, val):
    """-> (string, conf). ints / ASCII are raw (conf 2); rationals & arrays are best-effort (conf 1)."""
    if isinstance(val, str):
        return val, 2
    if isinstance(val, int):
        return str(val), 2
    if isinstance(val, tuple):
        return numfmt(val), (2 if val[1] == 1 else 1)
    if isinstance(val, bytes):
        if name in ("ExifVersion", "FlashpixVersion"):
            return val.decode("latin-1"), 1
        if name == "UserComment":
            return cstr(val[8:]) if val[:8] in (b"ASCII\x00\x00\x00", b"\x00" * 8) else val[8:].decode("utf-16", "replace").strip("\x00"), 1
        return val.hex(), 1
    if isinstance(val, list):
        if name.startswith("XP"):
            return bytes(val).decode("utf-16le", "replace").rstrip("\x00"), 1
        return ",".join(numfmt(v) if isinstance(v, tuple) else str(v) for v in val), 1
    return str(val), 1


def gps_deg(v, ref):
    try:
        d = sum(numfmt(x) and (x[0] / x[1]) / (60 ** i) for i, x in enumerate(v))
        return numfmt(round(-d if ref in ("S", "W") else d, 6))
    except Exception:
        return None


def tiff_facts(F, t, prefix="exif"):
    if len(t) < 8 or t[:2] not in (b"II", b"MM"):
        return
    e = "<" if t[:2] == b"II" else ">"
    F.add([f"{prefix}_byte_order", "byte_order", "endianness"], "little" if e == "<" else "big", 1)
    ifd0, nxt = ifd_read(t, u32(t, 4, e), e, TAGS)
    tags = dict(ifd0)
    if "ExifIFDPointer" in ifd0:
        tags.update({k: v for k, v in ifd_read(t, ifd0["ExifIFDPointer"], e, TAGS, 1)[0].items() if k not in tags})
    if "GPSInfoIFDPointer" in ifd0:
        tags.update(ifd_read(t, ifd0["GPSInfoIFDPointer"], e, GPS_TAGS, 1)[0])
    F.add([f"{prefix}_present", f"has_{prefix}"], True)
    F.add([f"{prefix}_tag_count", f"{prefix}_ifd0_entry_count", "ifd0_entry_count"], len(ifd0))
    F.add([f"{prefix}_thumbnail_present", "thumbnail_present", "has_thumbnail"], bool(nxt))
    for name, val in tags.items():
        s, c = fmt_tag(name, val)
        sn = snake(name)
        keys = [f"{prefix}_{sn}", sn, f"{prefix}_{name.lower()}", name.lower()]
        if "date_time" in sn:
            keys += [f"{prefix}_{sn.replace('date_time', 'datetime')}", sn.replace("date_time", "datetime")]
        if sn.startswith("gps_"):
            keys += [f"{prefix}_{sn[4:]}", f"gps_{sn[4:]}"]
        F.add(keys, s, c)
    for la, ref, key in (("GPSLatitude", "GPSLatitudeRef", "latitude"), ("GPSLongitude", "GPSLongitudeRef", "longitude")):
        if la in tags and isinstance(tags[la], list):
            F.add([f"{prefix}_gps_{key}", f"gps_{key}", key, f"{prefix}_{key}"], gps_deg(tags[la], tags.get(ref)), 1)
    if "PixelXDimension" in tags and "PixelYDimension" in tags:
        F.wh([prefix, f"{prefix}_pixel", "presentation"], tags["PixelXDimension"], tags["PixelYDimension"])
    if prefix == "tiff" and "ImageWidth" in tags and "ImageLength" in tags:
        F.wh(["", "ifd0", "image", "tiff"], tags["ImageWidth"], tags["ImageLength"])
    o = tags.get("Orientation")
    F.add([f"{prefix}_orientation", "orientation"], o)
    F.absent([f"{prefix}_{snake(n)}" for n in COMMON_EXIF])
    F.absent([f"{prefix}_orientation", f"{prefix}_dimensions_pixels"])


# =====================================================================================================  JPEG
SOF_NAMES = {0xC0: "baseline", 0xC1: "extended_sequential", 0xC2: "progressive", 0xC3: "lossless",
             0xC5: "differential_sequential", 0xC6: "differential_progressive", 0xC7: "differential_lossless",
             0xC9: "arithmetic_sequential", 0xCA: "arithmetic_progressive", 0xCB: "arithmetic_lossless",
             0xCD: "differential_arithmetic_sequential", 0xCE: "differential_arithmetic_progressive",
             0xCF: "differential_arithmetic_lossless"}


def jpeg_segments(data):
    i, out = 2, []
    while i + 4 <= len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        m = data[i + 1]
        if m == 0xFF:
            i += 1
            continue
        if m in (0xD8, 0x01, 0x00) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        if m == 0xD9:
            out.append((m, b"", i))
            return out, i + 2
        ln = u16(data, i + 2, ">")
        out.append((m, data[i + 4:i + 2 + ln], i))
        i += 2 + ln
        if m == 0xDA:
            j = data.rfind(b"\xff\xd9")  # entropy-coded data runs to EOI
            if j >= i:
                out.append((0xD9, b"", j))
                return out, j + 2
            return out, len(data)
    return out, i


def jpeg_facts(F, data):
    segs, end = jpeg_segments(data)
    marks = [m for m, _, _ in segs]
    sof = next(((m, p) for m, p, _ in segs if m in SOF_NAMES and len(p) >= 6), None)
    if sof:
        m, p = sof
        prec, h, w, nc = struct.unpack(">BHHB", p[:6])
        F.wh(["sof", "frame", "", "sof0" if m == 0xC0 else "sof_frame", "structural", "true", "actual", "jpeg"], w, h)
        F.add(["sof_precision", "precision", "bit_depth", "sample_precision", "sof_bit_depth"], prec)
        F.add(["sof_components", "components", "component_count", "sof_component_count", "num_components",
               "channels"], nc)
        F.add(["sof_marker", "sof_marker_hex"], "ff%02x" % m, 1)
        F.add(["sof_type", "frame_type", "encoding_process", "compression_process"], SOF_NAMES[m], 1)
        F.add(["sof_name", "sof_index"], "SOF%d" % (m - 0xC0), 1)
        F.add(["progressive", "is_progressive"], m in (0xC2, 0xC6, 0xCA, 0xCE))
        F.add(["baseline", "is_baseline"], m == 0xC0)
    else:
        F.absent(["sof_dimensions_pixels", "sof_width", "sof_height"])
    F.add(["segment_count", "marker_count", "segments"], len(segs))
    F.add(["sof_count"], sum(m in SOF_NAMES for m in marks))
    F.add(["dqt_count", "quantization_table_count"], marks.count(0xDB))
    F.add(["dht_count", "huffman_table_count"], marks.count(0xC4))
    F.add(["sos_count", "scan_count"], marks.count(0xDA))
    F.add(["app_segments", "app_markers"], ",".join("APP%d" % (m - 0xE0) for m in marks if 0xE0 <= m <= 0xEF) or "none", 1)
    for k in range(16):
        F.add([f"app{k}_present", f"has_app{k}"], (0xE0 + k) in marks)
        F.add([f"app{k}_count"], marks.count(0xE0 + k))
    F.add(["eoi_present", "has_eoi"], 0xD9 in marks)
    tail = len(data) - end if 0xD9 in marks else 0
    F.add(["trailing_bytes", "trailing_data_size", "bytes_after_eoi", "appended_bytes", "trailing_data_bytes"], max(tail, 0))
    F.add(["trailing_data_present", "has_trailing_data", "data_after_eoi", "appended_data_present"], tail > 0)
    com = [p for m, p, _ in segs if m == 0xFE]
    F.add(["comment", "com", "com_comment", "jpeg_comment", "com_text"], com[0].decode("utf-8", "replace").rstrip("\x00") if com else "none")
    F.add(["comment_present", "com_present", "has_comment"], bool(com))
    exif = xmp = icc = jfif = adobe = False
    for m, p, _ in segs:
        if m == 0xE0 and p.startswith(b"JFIF\x00") and len(p) >= 12:
            jfif = True
            F.add(["jfif_version", "app0_version"], "%d.%02d" % (p[5], p[6]))
            F.add(["jfif_density_units", "density_units"], p[7])
            F.add(["jfif_density", "density", "jfif_resolution"], dims(u16(p, 8, ">"), u16(p, 10, ">")))
            F.add(["jfif_x_density", "x_density"], u16(p, 8, ">"))
            F.add(["jfif_y_density", "y_density"], u16(p, 10, ">"))
        elif m == 0xE1 and p.startswith(b"Exif\x00\x00") and not exif:
            exif = True
            tiff_facts(F, p[6:], prefix="exif")
        elif m == 0xE1 and p.startswith(b"http://ns.adobe.com/xap/1.0/\x00"):
            xmp = True
            x = p[29:].decode("utf-8", "replace")
            for tag in ("CreatorTool", "creator", "title", "description", "CreateDate", "ModifyDate", "Label", "Rating"):
                mm = re.search(r"(?:xmp|dc|photoshop|exif|tiff)?:?%s(?:=\"([^\"]*)\"|>\s*(?:<rdf:\w+>\s*<rdf:li[^>]*>)?([^<]+))" % tag, x)
                if mm:
                    F.add([f"xmp_{snake(tag)}"], (mm.group(1) or mm.group(2) or "").strip(), 1)
        elif m == 0xE2 and p.startswith(b"ICC_PROFILE\x00"):
            icc = True
        elif m == 0xEE and p.startswith(b"Adobe"):
            adobe = True
    F.add(["exif_present", "has_exif", "app1_exif_present"], exif)
    F.add(["xmp_present", "has_xmp"], xmp)
    F.add(["icc_present", "icc_profile_present", "has_icc_profile"], icc)
    F.add(["jfif_present", "has_jfif"], jfif)
    F.add(["adobe_present", "has_adobe"], adobe)
    if not exif:
        F.absent(["exif_" + snake(n) for n in COMMON_EXIF] + ["exif_orientation", "exif_dimensions_pixels"])
    if sof and exif and "exif_dimensions_pixels" in F.d and F.d["exif_dimensions_pixels"][0] != "none":
        F.add(["exif_sof_dimensions_match", "dimensions_match", "presentation_matches_structure"],
              F.d["exif_dimensions_pixels"][0] == F.d["sof_dimensions_pixels"][0], 1)
    o = F.d.get("exif_orientation", ("none",))[0]
    if sof and o in ("5", "6", "7", "8"):
        F.add(["display_dimensions_pixels", "display_dimensions", "oriented_dimensions_pixels"], dims(h, w), 1)
    elif sof:
        F.add(["display_dimensions_pixels", "display_dimensions", "oriented_dimensions_pixels"], dims(w, h), 1)


# =====================================================================================================  GIF / BMP / WEBP / ICO
def gif_facts(F, data):
    F.add(["header_version", "version", "gif_version", "signature_version"], data[3:6].decode("latin-1"))
    F.add(["signature", "header", "magic_string"], data[:6].decode("latin-1"), 1)
    w, h, pk, bg, ar = struct.unpack_from("<HHBBB", data, 6)
    F.wh(["logical_screen", "lsd", "screen", "canvas", "", "gif"], w, h)
    gct = bool(pk & 0x80)
    F.add(["global_color_table_present", "gct_present", "global_color_table_flag", "has_global_color_table"], gct)
    F.add(["global_color_table_size", "gct_size", "global_color_table_entries", "color_table_size"],
          (2 << (pk & 7)) if gct else 0)
    F.add(["color_resolution", "color_resolution_bits"], ((pk >> 4) & 7) + 1)
    F.add(["sort_flag", "gct_sorted"], bool(pk & 8))
    F.add(["background_color_index", "background_index", "bg_color_index"], bg)
    F.add(["pixel_aspect_ratio", "aspect_ratio"], ar)
    i = 13 + (3 * (2 << (pk & 7)) if gct else 0)
    frames, comments, delays, loop, ext, first, trailer = 0, [], [], None, 0, None, False
    while i < len(data):
        b = data[i]
        if b == 0x3B:
            trailer = True
            i += 1
            break
        if b == 0x21 and i + 2 <= len(data):
            label = data[i + 1]
            ext += 1
            j = i + 2
            blocks = []
            while j < len(data) and data[j]:
                blocks.append(data[j + 1:j + 1 + data[j]])
                j += 1 + data[j]
            if label == 0xFE:
                comments.append(b"".join(blocks).decode("latin-1"))
            elif label == 0xF9 and blocks and len(blocks[0]) >= 3:
                delays.append(u16(blocks[0], 1))
            elif label == 0xFF and blocks and blocks[0][:11] in (b"NETSCAPE2.0", b"ANIMEXTS1.0") and len(blocks) > 1 and len(blocks[1]) >= 3:
                loop = u16(blocks[1], 1)
            i = j + 1
        elif b == 0x2C and i + 10 <= len(data):
            frames += 1
            x, y, iw, ih, ipk = struct.unpack_from("<HHHHB", data, i + 1)
            if first is None:
                first = (x, y, iw, ih, ipk)
            j = i + 10 + (3 * (2 << (ipk & 7)) if ipk & 0x80 else 0) + 1
            while j < len(data) and data[j]:
                j += 1 + data[j]
            i = j + 1
        else:
            break
    F.add(["frame_count", "image_count", "frames", "num_frames", "image_descriptor_count"], frames)
    F.add(["animated", "is_animated"], frames > 1)
    F.add(["extension_count"], ext)
    F.add(["comment", "comment_text"], comments[0] if comments else "none")
    F.add(["comment_count"], len(comments))
    F.add(["comment_present", "has_comment"], bool(comments))
    F.add(["loop_count", "netscape_loop_count", "iterations"], loop if loop is not None else "none")
    F.add(["first_frame_delay", "frame_delay", "delay_time"], delays[0] if delays else "none", 1)
    F.add(["total_delay", "duration_centiseconds"], sum(delays), 1)
    if first:
        F.wh(["first_frame", "image_descriptor", "frame", "image"], first[2], first[3])
        F.add(["first_frame_offset", "image_position"], f"{first[0]},{first[1]}", 1)
        F.add(["interlaced", "is_interlaced"], bool(first[4] & 0x40))
    F.add(["trailer_present", "has_trailer"], trailer)
    F.add(["trailing_bytes", "trailing_data_size", "bytes_after_trailer", "appended_bytes"], len(data) - i if trailer else 0)
    F.add(["trailing_data_present", "has_trailing_data"], trailer and len(data) > i)


DIB = {12: "BITMAPCOREHEADER", 40: "BITMAPINFOHEADER", 52: "BITMAPV2INFOHEADER", 56: "BITMAPV3INFOHEADER",
       64: "OS22XBITMAPHEADER", 108: "BITMAPV4HEADER", 124: "BITMAPV5HEADER"}


def bmp_facts(F, data):
    fsize, _, off = struct.unpack_from("<IIi", data, 2)
    hs = u32(data, 14)
    F.add(["file_size_field", "bf_size", "declared_file_size", "header_file_size", "declared_size"], fsize)
    F.add(["declared_size_matches", "file_size_valid", "size_matches"], fsize == len(data))
    F.add(["pixel_data_offset", "pixel_offset", "bf_off_bits", "data_offset", "pixel_array_offset"], off)
    F.add(["dib_header_size", "info_header_size", "bi_size", "header_size"], hs)
    F.add(["dib_header_type", "dib_header", "header_type", "dib_version"], DIB.get(hs, "unknown"), 1)
    if hs == 12:
        w, h, planes, bpp = struct.unpack_from("<HHHH", data, 18)
        comp = 0
    else:
        w, h, planes, bpp, comp = struct.unpack_from("<iiHHI", data, 18)
    F.wh(["dib", "", "image", "bmp", "header", "bitmap"], abs(w), abs(h))
    F.add(["top_down", "is_top_down"], h < 0)
    F.add(["bit_depth", "bits_per_pixel", "bit_count", "bpp", "bi_bit_count"], bpp)
    F.add(["planes", "color_planes"], planes)
    F.add(["compression", "compression_method", "bi_compression"], comp)
    if hs >= 40:
        isz, xp, yp, cu, ci = struct.unpack_from("<IiiII", data, 34)
        F.add(["image_size", "bi_size_image", "pixel_data_size"], isz)
        F.add(["pixels_per_meter", "resolution_ppm"], dims(xp, yp), 1)
        F.add(["x_pixels_per_meter"], xp)
        F.add(["y_pixels_per_meter"], yp)
        F.add(["colors_used", "palette_size", "clr_used"], cu)
        F.add(["colors_important", "clr_important"], ci)
    row = ((abs(w) * bpp + 31) // 32) * 4
    F.add(["trailing_bytes", "trailing_data_size"], max(len(data) - (off + row * abs(h)), 0), 1)


def webp_facts(F, data):
    F.add(["riff_size", "declared_size"], u32(data, 4))
    i, chunks = 12, []
    while i + 8 <= len(data):
        cid, ln = data[i:i + 4].decode("latin-1"), u32(data, i + 4)
        body = data[i + 8:i + 8 + ln]
        chunks.append(cid)
        if cid == "VP8X" and len(body) >= 10:
            F.add(["vp8x_flags"], body[0], 1)
            F.add(["animated", "is_animated"], bool(body[0] & 2))
            F.add(["alpha", "has_alpha"], bool(body[0] & 16))
            F.wh(["canvas", "vp8x", "", "webp"], 1 + int.from_bytes(body[4:7], "little"), 1 + int.from_bytes(body[7:10], "little"))
        elif cid == "VP8 " and len(body) >= 10 and body[3:6] == b"\x9d\x01\x2a":
            F.wh(["vp8", "frame", "", "webp", "bitstream", "canvas", "image"], u16(body, 6) & 0x3FFF, u16(body, 8) & 0x3FFF)
        elif cid == "VP8L" and len(body) >= 5 and body[0] == 0x2F:
            v = u32(body, 1)
            F.wh(["vp8l", "frame", "", "webp", "bitstream", "canvas", "image"], (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1)
        elif cid == "EXIF":
            tiff_facts(F, body[6:] if body.startswith(b"Exif\x00\x00") else body, prefix="exif")
        i += 8 + ln + (ln & 1)
    F.add(["chunk_count"], len(chunks))
    F.add(["chunk_order", "chunk_types"], ",".join(c.strip() for c in chunks), 1)
    F.add(["encoding", "compression", "bitstream_type"],
          "lossless" if "VP8L" in chunks else ("lossy" if "VP8 " in chunks else "none"), 1)
    for c in ("VP8X", "VP8 ", "VP8L", "ALPH", "ANIM", "ANMF", "ICCP", "EXIF", "XMP "):
        F.add([f"{c.strip()}_present", f"{c.strip()}_chunk_present"], c in chunks)


def ico_facts(F, data):
    typ, cnt = u16(data, 2), u16(data, 4)
    F.add(["image_count", "icon_count", "entry_count", "count"], cnt)
    F.add(["resource_type", "type"], typ, 1)
    for k in range(min(cnt, 64)):
        e = data[6 + 16 * k: 22 + 16 * k]
        if len(e) < 16:
            break
        w, h = e[0] or 256, e[1] or 256
        if k == 0:
            F.wh(["first_image", "first_icon", "", "ico"], w, h)
            F.add(["bit_depth", "bits_per_pixel"], u16(e, 6))
        img = data[u32(e, 12):u32(e, 12) + 8]
        if k == 0:
            F.add(["first_image_format", "image_format"], "png" if img.startswith(b"\x89PNG") else "bmp", 1)


# =====================================================================================================  PDF
OBJ_RE = re.compile(rb"(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj", re.S)


def pdf_objects(data):
    objs = {}
    for m in OBJ_RE.finditer(data):
        objs[int(m.group(1))] = m.group(3)
    for body in list(objs.values()):
        if b"/ObjStm" not in body:
            continue
        sm = re.search(rb"stream\r?\n(.*?)\r?\n?endstream", body, re.S)
        n, first = re.search(rb"/N\s+(\d+)", body), re.search(rb"/First\s+(\d+)", body)
        if not (sm and n and first):
            continue
        try:
            raw = zlib.decompress(sm.group(1)) if b"/FlateDecode" in body else sm.group(1)
            nums = list(map(int, raw[:int(first.group(1))].split()))
        except (zlib.error, ValueError):
            continue
        pairs = list(zip(nums[0::2], nums[1::2]))[:int(n.group(1))]
        base = int(first.group(1))
        for i, (num, off) in enumerate(pairs):
            end = base + pairs[i + 1][1] if i + 1 < len(pairs) else len(raw)
            objs.setdefault(num, raw[base + off:end])
    return objs


def pdf_string(raw):
    """Body of a PDF (literal) or <hex> string -> text (PDFDocEncoding ~ latin-1, UTF-16BE with BOM)."""
    if raw.startswith(b"<"):
        try:
            b = bytes.fromhex(raw[1:-1].decode("latin-1"))
        except ValueError:
            return None
    else:
        s = raw[1:-1]
        out, i = bytearray(), 0
        esc = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f", b"(": b"(", b")": b")", b"\\": b"\\"}
        while i < len(s):
            c = s[i:i + 1]
            if c == b"\\" and i + 1 < len(s):
                n = s[i + 1:i + 2]
                if n in esc:
                    out += esc[n]
                    i += 2
                    continue
                mo = re.match(rb"[0-7]{1,3}", s[i + 1:i + 4])
                if mo:
                    out.append(int(mo.group(0), 8) & 0xFF)
                    i += 1 + len(mo.group(0))
                    continue
                if n in (b"\n", b"\r"):
                    i += 2
                    continue
                i += 1
                continue
            out += c
            i += 1
        b = bytes(out)
    if b.startswith(b"\xfe\xff"):
        return b[2:].decode("utf-16-be", "replace")
    if b.startswith(b"\xef\xbb\xbf"):
        return b[3:].decode("utf-8", "replace")
    return b.decode("latin-1")


PDF_STR = rb"(\((?:\\.|[^\\)])*\)|<[0-9A-Fa-f\s]*>)"
INFO_KEYS = ["Title", "Author", "Subject", "Keywords", "Creator", "Producer", "CreationDate", "ModDate", "Trapped"]


def pdf_facts(F, data):
    m = re.match(rb"%PDF-(\d+)\.(\d+)", data.lstrip(LEAD)[:16])
    if m:
        hv = ver(int(m.group(1)), int(m.group(2)))
        F.add(["header_version", "pdf_header_version", "version_header", "magic_version", "header",
               "file_header_version", "signature_version"], hv)
    else:
        F.absent(["header_version"])
        hv = None
    F.add(["header_offset", "header_position"], len(data) - len(data.lstrip(LEAD)), 1)
    F.add(["bom_prefix_present", "leading_bom"], data.startswith(b"\xef\xbb\xbf"))
    objs = pdf_objects(data)
    roots = re.findall(rb"/Root\s+(\d+)\s+\d+\s+R", data)
    cat = objs.get(int(roots[-1])) if roots and int(roots[-1]) in objs else next(
        (b for b in objs.values() if re.search(rb"/Type\s*/Catalog\b", b)), None)
    cm = re.search(rb"/Version\s*/([^\s/<>\[\]()]+)", cat or b"")
    cv = cm.group(1).decode("latin-1") if cm else None
    F.add(["catalog_version", "declared_version", "root_version", "version_override", "catalog_version_override",
           "catalog_declared_version"], cv or "none")
    key = lambda v: tuple(int(x) for x in v.split(".")) if v and re.fullmatch(r"\d+\.\d+", v) else (-1,)
    eff = max((v for v in (hv, cv) if v), key=key, default=None)
    F.add(["effective_version", "version", "pdf_version", "actual_version"], eff or "none", 1)
    F.add(["versions_conflict", "version_conflict", "version_mismatch", "versions_differ"], bool(cv) and cv != hv, 1)
    pages = [b for b in objs.values() if re.search(rb"/Type\s*/Page\b(?!s)", b)]
    pc = None
    if cat:
        pr = re.search(rb"/Pages\s+(\d+)\s+\d+\s+R", cat)
        if pr and int(pr.group(1)) in objs:
            cnt = re.search(rb"/Count\s+(\d+)", objs[int(pr.group(1))])
            pc = int(cnt.group(1)) if cnt else None
    F.add(["page_count", "pages", "number_of_pages", "num_pages", "pages_count"], pc if pc is not None else len(pages))
    F.add(["page_objects", "page_object_count"], len(pages))
    F.add(["object_count", "objects", "obj_count", "indirect_object_count"], len(objs))
    eofs = data.count(b"%%EOF")
    F.add(["eof_count", "eof_marker_count", "revision_count", "revisions"], eofs)
    F.add(["incremental_updates", "incremental_update_count", "update_count"], max(eofs - 1, 0))
    F.add(["incremental_update_present", "incrementally_updated", "has_incremental_updates"], eofs > 1)
    F.add(["xref_count", "xref_section_count", "xref_table_count"], len(re.findall(rb"(?<![a-z])xref\s", data)))
    F.add(["xref_stream_present", "has_xref_stream"], bool(re.search(rb"/Type\s*/XRef\b", data)))
    sx = re.findall(rb"startxref\s+(\d+)", data)
    F.add(["startxref", "startxref_offset", "xref_offset"], int(sx[-1]) if sx else "none")
    last = data.rfind(b"%%EOF")
    tail = data[last + 5:].lstrip(b"\r\n") if last >= 0 else b""
    F.add(["trailing_bytes", "trailing_data_size", "bytes_after_eof"], len(tail))
    F.add(["trailing_data_present", "has_trailing_data", "data_after_eof"], bool(tail))
    trailer = b" ".join(re.findall(rb"trailer\s*(<<.*?>>)", data, re.S)) + b" ".join(
        b for b in objs.values() if re.search(rb"/Type\s*/XRef\b", b))
    F.add(["encrypted", "is_encrypted", "encryption_present", "has_encryption"], b"/Encrypt" in trailer)
    F.add(["linearized", "is_linearized"], bool(re.search(rb"/Linearized\b", data[:2048])))
    allb = data + b"".join(objs.values())
    F.add(["javascript_present", "has_javascript", "contains_javascript", "js_present"], bool(re.search(rb"/(JavaScript|JS)\b", allb)))
    F.add(["openaction_present", "has_openaction", "open_action_present"], b"/OpenAction" in allb)
    F.add(["embedded_files_present", "has_embedded_files", "embedded_file_present"], bool(re.search(rb"/(EmbeddedFiles?|EmbeddedFile)\b", allb)))
    F.add(["launch_action_present", "has_launch_action"], b"/Launch" in allb)
    F.add(["acroform_present", "has_acroform", "has_forms"], b"/AcroForm" in allb)
    F.add(["xmp_present", "metadata_stream_present", "has_xmp"], bool(re.search(rb"/Type\s*/Metadata\b", allb)))
    F.add(["object_stream_present", "has_object_streams"], b"/ObjStm" in data)
    F.add(["image_count"], len(re.findall(rb"/Subtype\s*/Image\b", allb)))
    F.add(["font_count"], len({m.group(1) for m in re.finditer(rb"/BaseFont\s*/([^\s/<>\[\]()]+)", allb)}))
    refs = re.findall(rb"/Info\s+(\d+)\s+\d+\s+R", data)
    info = objs.get(int(refs[-1])) if refs and int(refs[-1]) in objs else None
    F.add(["info_present", "has_info", "info_dictionary_present"], info is not None)
    for k in INFO_KEYS:
        mm = re.search(rb"/" + k.encode() + rb"\s*" + PDF_STR, info or b"")
        v = pdf_string(mm.group(1)) if mm else None
        keys = [f"info_{snake(k)}", snake(k), f"info_{k.lower()}", k.lower(), f"document_{snake(k)}"]
        if k == "ModDate":
            keys += ["modification_date", "info_modification_date", "modified_date", "mod_date"]
        if k == "CreationDate":
            keys += ["created_date", "creation_date", "info_creation_date", "create_date"]
        F.add(keys, v if v is not None else "none", 2 if "Date" not in k else 1)
    if info is None:
        F.absent([f"info_{snake(k)}" for k in INFO_KEYS])
    if cat:
        lm = re.search(rb"/Lang\s*" + PDF_STR, cat)
        F.add(["lang", "language", "catalog_lang"], pdf_string(lm.group(1)) if lm else "none", 1)


# =====================================================================================================  ZIP / OOXML
def zip_facts(F, data):
    e = data.rfind(b"PK\x05\x06")
    if e >= 0 and e + 22 <= len(data):
        _, _, n_disk, n_total, cd_size, cd_off, clen = struct.unpack_from("<HHHHIIH", data, e + 4)
        F.add(["entry_count", "eocd_entry_count", "central_directory_entries", "total_entries", "cd_entry_count",
               "number_of_entries", "member_count_eocd"], n_total)
        F.add(["central_directory_offset", "cd_offset"], cd_off)
        F.add(["central_directory_size", "cd_size"], cd_size)
        com = data[e + 22:e + 22 + clen]
        F.add(["comment", "archive_comment", "zip_comment", "eocd_comment"], com.decode("utf-8", "replace") if com else "none")
        F.add(["comment_present", "has_comment"], bool(com))
        F.add(["comment_length"], clen)
        F.add(["trailing_bytes", "trailing_data_size", "bytes_after_eocd"], len(data) - (e + 22 + clen))
    F.add(["local_header_count", "local_file_header_count"], data.count(b"PK\x03\x04"))
    F.add(["prepended_bytes", "leading_bytes", "data_before_first_header"], max(data.find(b"PK\x03\x04"), 0))
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except Exception:
        return
    infos = z.infolist()
    files = [i for i in infos if not i.is_dir()]
    F.add(["file_count", "member_count", "files", "entries", "num_files", "number_of_files"], len(files))
    F.add(["directory_count", "dir_count"], len(infos) - len(files))
    F.add(["entry_count"], len(infos))
    F.add(["first_entry", "first_member", "first_file", "first_entry_name"], infos[0].filename if infos else "none")
    F.add(["last_entry", "last_member", "last_entry_name"], infos[-1].filename if infos else "none")
    F.add(["entry_names", "member_names", "file_names", "filenames"], ",".join(i.filename for i in infos), 1)
    F.add(["encrypted", "is_encrypted", "encrypted_entries_present", "password_protected"], any(i.flag_bits & 1 for i in infos))
    F.add(["encrypted_entry_count", "encrypted_count"], sum(bool(i.flag_bits & 1) for i in infos))
    F.add(["aes_encrypted", "aes_present"], any(i.compress_type == 99 for i in infos))
    meth = {0: "stored", 8: "deflate", 9: "deflate64", 12: "bzip2", 14: "lzma", 93: "zstd", 99: "aes"}
    F.add(["compression_method", "compression", "first_entry_compression"],
          meth.get(infos[0].compress_type, str(infos[0].compress_type)) if infos else "none", 1)
    F.add(["total_uncompressed_size", "uncompressed_size", "total_size"], sum(i.file_size for i in infos))
    F.add(["total_compressed_size", "compressed_size"], sum(i.compress_size for i in infos))
    if infos:
        d = infos[0].date_time
        F.add(["first_entry_mtime", "first_entry_date", "first_entry_modified"],
              "%04d-%02d-%02d %02d:%02d:%02d" % d, 1)
        F.add(["created_by_version", "version_made_by"], infos[0].create_version, 1)
        F.add(["created_by_system", "host_os"], infos[0].create_system, 1)
    F.add(["zip64", "is_zip64"], any(i.file_size >= 0xFFFFFFFF or i.header_offset >= 0xFFFFFFFF for i in infos) or b"PK\x06\x06" in data)
    names = set(z.namelist())
    F.add(["duplicate_names_present", "has_duplicate_entries"], len(names) != len(infos))
    F.add(["path_traversal_present", "zip_slip", "has_path_traversal"], any(".." in n.split("/") or n.startswith("/") for n in names))
    ooxml = "[Content_Types].xml" in names
    kind = ("docx" if any(n.startswith("word/") for n in names) else "xlsx" if any(n.startswith("xl/") for n in names)
            else "pptx" if any(n.startswith("ppt/") for n in names) else "ooxml") if ooxml else None
    if "mimetype" in names:
        try:
            F.add(["mimetype", "mime_type"], z.read("mimetype").decode("latin-1").strip())
        except Exception:
            pass
    if "META-INF/MANIFEST.MF" in names:
        try:
            for line in z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace").splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    F.add([f"manifest_{snake(k.replace('-', ''))}", snake(k.replace("-", ""))], v.strip())
        except Exception:
            pass
    F.add(["ooxml", "is_ooxml"], ooxml)
    F.add(["container_type", "document_type", "ooxml_type", "office_type"], kind or "zip", 1)
    for part, ns in (("docProps/core.xml", None), ("docProps/app.xml", None), ("meta.xml", None)):
        if part not in names:
            continue
        try:
            x = z.read(part).decode("utf-8", "replace")
        except Exception:
            continue
        for mm in re.finditer(r"<(?:(\w+):)?(\w+)(?:\s[^>]*)?>([^<]*)</(?:\w+:)?\2>", x):
            pre, tag, val = mm.group(1) or "", mm.group(2), mm.group(3).strip()
            if not val:
                continue
            sn = snake(tag)
            keys = [sn, f"{pre}_{sn}", f"core_{sn}" if "core" in part else f"app_{sn}"]
            if tag == "creator":
                keys += ["author"]
            if tag == "lastModifiedBy":
                keys += ["last_modified_by"]
            if tag in ("created", "modified"):
                keys += [f"{tag}_date", f"date_{tag}"]
            F.add(keys, val, 2 if "date" not in sn and tag not in ("created", "modified") else 1)
    F.absent(["creator", "last_modified_by", "title"] if ooxml else [])


# =====================================================================================================  GZIP / ELF / PE
def gzip_facts(F, data):
    cm, flg, mtime, xfl, os_ = struct.unpack_from("<BBIBB", data, 2)
    F.add(["compression_method", "cm", "method"], cm)
    F.add(["flags", "flg"], flg)
    F.add(["mtime", "modification_time", "timestamp", "mtime_unix"], mtime)
    if mtime:
        F.add(["mtime_iso", "mtime_utc"], time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime)), 1)
    F.add(["extra_flags", "xfl"], xfl)
    F.add(["os", "operating_system", "os_id"], os_)
    i = 10
    if flg & 4:
        i += 2 + u16(data, i)
    name = com = None
    if flg & 8:
        j = data.index(b"\x00", i)
        name, i = data[i:j].decode("latin-1"), j + 1
    if flg & 16:
        j = data.index(b"\x00", i)
        com, i = data[i:j].decode("latin-1"), j + 1
    F.add(["original_filename", "original_name", "fname", "filename_field", "embedded_filename", "stored_name"], name or "none")
    F.add(["comment", "fcomment"], com or "none")
    F.add(["fname_present", "original_filename_present", "has_filename"], bool(flg & 8))
    F.add(["fhcrc_present", "header_crc_present"], bool(flg & 2))
    if len(data) >= 18:
        F.add(["isize", "uncompressed_size", "original_size", "decompressed_size"], u32(data, len(data) - 4))
        F.add(["crc32_trailer", "trailer_crc32", "data_crc32"], "%08x" % u32(data, len(data) - 8), 1)


ELF_MACH = {3: "x86", 62: "x86-64", 183: "AArch64", 40: "ARM", 8: "MIPS", 20: "PowerPC", 21: "PowerPC64", 243: "RISC-V"}
ELF_TYPE = {0: "ET_NONE", 1: "ET_REL", 2: "ET_EXEC", 3: "ET_DYN", 4: "ET_CORE"}


def elf_facts(F, data):
    cls, enc, ev, osabi = data[4], data[5], data[6], data[7]
    e = "<" if enc == 1 else ">"
    F.add(["class", "elf_class", "ei_class"], {1: "ELF32", 2: "ELF64"}.get(cls, str(cls)))
    F.add(["bits", "bitness"], {1: 32, 2: 64}.get(cls))
    F.add(["endianness", "data", "ei_data", "byte_order", "endian"], {1: "little", 2: "big"}.get(enc, str(enc)))
    F.add(["ei_version", "ident_version"], ev)
    F.add(["osabi", "os_abi", "ei_osabi"], osabi)
    if cls == 2:
        typ, mach, v, entry, phoff, shoff, flags, ehs, phes, phn, shes, shn, shx = struct.unpack_from(e + "HHIQQQIHHHHHH", data, 16)
    else:
        typ, mach, v, entry, phoff, shoff, flags, ehs, phes, phn, shes, shn, shx = struct.unpack_from(e + "HHIIIIIHHHHHH", data, 16)
    F.add(["type", "e_type", "elf_type", "file_type"], ELF_TYPE.get(typ, str(typ)))
    F.add(["machine", "e_machine", "architecture", "arch"], ELF_MACH.get(mach, str(mach)))
    F.add(["entry_point", "entry", "e_entry", "entry_point_address"], hex(entry), 1)
    F.add(["program_header_count", "phnum", "e_phnum", "segment_count"], phn)
    F.add(["section_header_count", "shnum", "e_shnum", "section_count"], shn)
    F.add(["shstrndx", "e_shstrndx"], shx)
    F.add(["flags", "e_flags"], hex(flags), 1)
    try:
        so = shoff + shx * shes
        strtab_off = struct.unpack_from(e + ("Q" if cls == 2 else "I"), data, so + (24 if cls == 2 else 16))[0]
        names = []
        for k in range(shn):
            no = u32(data, shoff + k * shes, e)
            names.append(cstr(data[strtab_off + no:strtab_off + no + 64]))
        F.add(["section_names", "sections"], ",".join(names), 1)
        F.add(["stripped", "is_stripped"], ".symtab" not in names)
        F.add(["debug_info_present", "has_debug_info"], ".debug_info" in names)
    except Exception:
        pass
    for k in range(phn):
        p = phoff + k * phes
        if p + 4 <= len(data) and u32(data, p, e) == 3:
            o = struct.unpack_from(e + ("Q" if cls == 2 else "I"), data, p + (8 if cls == 2 else 4))[0]
            F.add(["interpreter", "interp", "program_interpreter"], cstr(data[o:o + 256]))
            break
    else:
        F.add(["interpreter", "interp"], "none")


PE_MACH = {0x14C: "i386", 0x8664: "x86-64", 0xAA64: "AArch64", 0x1C0: "ARM", 0x1C4: "ARMNT"}


def pe_facts(F, data):
    off = u32(data, 0x3C)
    mach, nsec, ts, _, _, osz, ch = struct.unpack_from("<HHIIIHH", data, off + 4)
    F.add(["machine", "file_header_machine", "architecture"], PE_MACH.get(mach, hex(mach)))
    F.add(["number_of_sections", "section_count", "nsections"], nsec)
    F.add(["timestamp", "time_date_stamp", "compile_timestamp", "timedatestamp"], ts)
    F.add(["timestamp_iso", "compile_time"], time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)), 1)
    F.add(["characteristics"], hex(ch), 1)
    F.add(["is_dll", "dll"], bool(ch & 0x2000))
    o = off + 24
    magic = u16(data, o)
    F.add(["optional_header_magic", "pe_type", "format"], {0x10B: "PE32", 0x20B: "PE32+"}.get(magic, hex(magic)), 1)
    F.add(["linker_version"], "%d.%d" % (data[o + 2], data[o + 3]), 1)
    F.add(["entry_point", "address_of_entry_point", "entry_point_rva"], hex(u32(data, o + 16)), 1)
    ib = struct.unpack_from("<Q", data, o + 24)[0] if magic == 0x20B else u32(data, o + 28)
    F.add(["image_base"], hex(ib), 1)
    sub = u16(data, o + 68)
    F.add(["subsystem"], sub, 1)
    F.add(["subsystem_name"], {2: "windows_gui", 3: "windows_cui", 1: "native"}.get(sub, str(sub)), 1)
    F.add(["dll_characteristics"], hex(u16(data, o + 70)), 1)
    nrva_off = o + (108 if magic == 0x20B else 92)
    dd = nrva_off + 4
    try:
        clr_rva = u32(data, dd + 14 * 8)
        F.add(["dotnet", "is_dotnet", "clr_present", "managed"], clr_rva != 0)
    except struct.error:
        pass
    so = o + osz
    names = [cstr(data[so + 40 * k: so + 40 * k + 8]) for k in range(nsec)]
    F.add(["section_names", "sections"], ",".join(names), 1)


# =====================================================================================================  audio / db / misc
def riff_wav_facts(F, data):
    F.add(["riff_size", "chunk_size", "declared_size"], u32(data, 4))
    F.add(["form_type", "riff_type", "format"], data[8:12].decode("latin-1").strip(), 1)
    F.add(["riff_size_valid", "declared_size_matches"], u32(data, 4) + 8 == len(data))
    i, chunks, fmt, dsize = 12, [], None, None
    while i + 8 <= len(data):
        cid, ln = data[i:i + 4].decode("latin-1"), u32(data, i + 4)
        body = data[i + 8:i + 8 + ln]
        chunks.append(cid.strip())
        if cid == "fmt " and len(body) >= 16:
            fmt = struct.unpack_from("<HHIIHH", body)
        elif cid == "data":
            dsize = ln
        elif cid == "LIST" and body[:4] == b"INFO":
            j = 4
            while j + 8 <= len(body):
                sid, sl = body[j:j + 4].decode("latin-1"), u32(body, j + 4)
                val = cstr(body[j + 8:j + 8 + sl])
                nm = {"INAM": "title", "IART": "artist", "ICMT": "comment", "ICRD": "creation_date", "ISFT": "software",
                      "IGNR": "genre", "ICOP": "copyright", "IPRD": "product", "IENG": "engineer"}.get(sid)
                F.add([f"info_{sid.lower()}", sid.lower()] + ([nm, f"info_{nm}"] if nm else []), val)
                j += 8 + sl + (sl & 1)
        i += 8 + ln + (ln & 1)
    F.add(["chunk_count"], len(chunks))
    F.add(["chunk_order", "chunk_types"], ",".join(chunks), 1)
    for c in set(chunks) | {"fmt", "data", "LIST", "fact", "cue", "bext", "id3"}:
        F.add([f"{c}_present", f"{c}_chunk_present", f"has_{c}_chunk"], c in chunks)
    if fmt:
        af, ch, sr, br, ba, bps = fmt
        F.add(["audio_format", "format_tag", "wformattag", "audio_format_code"], af)
        F.add(["channels", "channel_count", "num_channels", "nchannels"], ch)
        F.add(["sample_rate", "sampling_rate", "samples_per_sec", "sample_rate_hz", "frequency"], sr)
        F.add(["byte_rate", "avg_bytes_per_sec", "bytes_per_second"], br)
        F.add(["block_align", "frame_size"], ba)
        F.add(["bits_per_sample", "bit_depth", "sample_width_bits"], bps)
        F.add(["bitrate", "bit_rate"], br * 8, 1)
        if dsize is not None and ba:
            F.add(["data_size", "data_chunk_size", "data_bytes"], dsize)
            F.add(["frame_count", "sample_frames", "num_frames", "nframes", "sample_count", "total_samples"], dsize // ba)
            if sr:
                F.add(["duration_seconds", "duration", "length_seconds"], numfmt(round(dsize / ba / sr, 3)), 1)


ID3_FRAMES = {"TIT2": "title", "TPE1": "artist", "TALB": "album", "TYER": "year", "TDRC": "recording_time",
              "TCON": "genre", "COMM": "comment", "TRCK": "track", "TSSE": "encoder", "TENC": "encoded_by",
              "TCOM": "composer", "TPE2": "album_artist", "WXXX": "url", "TXXX": "user_text", "TCOP": "copyright"}
MP3_BR = {1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320], 2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]}
MP3_SR = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}


def id3_text(fid, b):
    if not b:
        return ""
    enc, body = b[0], b[1:]
    if fid == "COMM" and len(body) > 3:
        body = body[3:]
        sep = b"\x00\x00" if enc in (1, 2) else b"\x00"
        k = body.find(sep)
        body = body[k + len(sep):] if k >= 0 else body
    codec = {0: "latin-1", 1: "utf-16", 2: "utf-16-be", 3: "utf-8"}.get(enc, "latin-1")
    try:
        return body.decode(codec).rstrip("\x00").split("\x00")[0].strip()
    except UnicodeDecodeError:
        return body.decode("latin-1").strip("\x00")


def mp3_facts(F, data):
    i = 0
    if data[:3] == b"ID3" and len(data) >= 10:
        maj, rev, flg = data[3], data[4], data[5]
        size = (data[6] << 21) | (data[7] << 14) | (data[8] << 7) | data[9]
        F.add(["id3_version", "id3v2_version", "tag_version"], f"2.{maj}.{rev}", 1)
        F.add(["id3_major_version", "id3v2_major_version"], maj)
        F.add(["id3_present", "id3v2_present", "has_id3", "has_id3v2"], True)
        F.add(["id3_size", "id3v2_size", "tag_size"], size)
        j, end, nframes = 10, 10 + size, 0
        while j + 10 <= end and data[j:j + 4].strip(b"\x00"):
            fid = data[j:j + 4].decode("latin-1")
            fs = u32(data, j + 4, ">") if maj < 4 else ((data[j + 4] << 21) | (data[j + 5] << 14) | (data[j + 6] << 7) | data[j + 7])
            body = data[j + 10:j + 10 + fs]
            nframes += 1
            if fid[0] == "T" or fid == "COMM":
                nm = ID3_FRAMES.get(fid)
                F.add([f"id3_{fid.lower()}", fid.lower()] + ([nm, f"id3_{nm}", f"tag_{nm}"] if nm else []), id3_text(fid, body))
            j += 10 + fs
        F.add(["id3_frame_count", "frame_count_id3"], nframes)
        i = end
    else:
        F.add(["id3_present", "id3v2_present", "has_id3v2"], False)
    for nm in ("title", "artist", "album", "comment"):
        F.absent([f"id3_{nm}"])
    while i + 4 <= len(data) and not (data[i] == 0xFF and (data[i + 1] & 0xE0) == 0xE0):
        i += 1
    if i + 4 <= len(data):
        h = u32(data, i, ">")
        vid, layer, bri, sri, ch = (h >> 19) & 3, (h >> 17) & 3, (h >> 12) & 15, (h >> 10) & 3, (h >> 6) & 3
        F.add(["mpeg_version"], {3: "1", 2: "2", 0: "2.5"}.get(vid, "none"), 1)
        F.add(["layer", "mpeg_layer"], {1: 3, 2: 2, 3: 1}.get(layer, 0))
        try:
            F.add(["bitrate_kbps", "bitrate", "bit_rate"], MP3_BR[1 if vid == 3 else 2][bri], 1)
            F.add(["sample_rate", "sampling_rate", "sample_rate_hz"], MP3_SR[vid][sri])
        except (KeyError, IndexError):
            pass
        F.add(["channel_mode"], {0: "stereo", 1: "joint_stereo", 2: "dual_channel", 3: "mono"}[ch], 1)
        F.add(["channels", "channel_count"], 1 if ch == 3 else 2)
    if len(data) >= 128 and data[-128:-125] == b"TAG":
        t = data[-128:]
        F.add(["id3v1_present", "has_id3v1"], True)
        for nm, a, b in (("title", 3, 33), ("artist", 33, 63), ("album", 63, 93), ("year", 93, 97)):
            F.add([f"id3v1_{nm}"], cstr(t[a:b]))
    else:
        F.add(["id3v1_present", "has_id3v1"], False)


def flac_facts(F, data):
    i, last = 4, False
    while not last and i + 4 <= len(data):
        hd = data[i]
        last, typ, ln = bool(hd & 0x80), hd & 0x7F, int.from_bytes(data[i + 1:i + 4], "big")
        b = data[i + 4:i + 4 + ln]
        if typ == 0 and len(b) >= 18:
            v = int.from_bytes(b[10:18], "big")
            sr, ch, bps, tot = v >> 44, ((v >> 41) & 7) + 1, ((v >> 36) & 31) + 1, v & ((1 << 36) - 1)
            F.add(["sample_rate", "sampling_rate"], sr)
            F.add(["channels", "channel_count"], ch)
            F.add(["bits_per_sample", "bit_depth"], bps)
            F.add(["total_samples", "sample_count", "frame_count"], tot)
            F.add(["md5_signature", "audio_md5", "streaminfo_md5"], b[18:34].hex(), 1)
        elif typ == 4 and len(b) >= 8:
            vl = u32(b, 0)
            F.add(["vendor", "vendor_string"], b[4:4 + vl].decode("utf-8", "replace"))
            j = 4 + vl
            n = u32(b, j)
            j += 4
            for _ in range(n):
                cl = u32(b, j)
                kv = b[j + 4:j + 4 + cl].decode("utf-8", "replace")
                j += 4 + cl
                if "=" in kv:
                    k, val = kv.split("=", 1)
                    F.add([snake(k), f"vorbis_{snake(k)}", f"comment_{snake(k)}"], val)
        i += 4 + ln


def sqlite_varint(b, i):
    v = 0
    for k in range(9):
        c = b[i + k]
        if k == 8:
            return (v << 8) | c, i + 9
        v = (v << 7) | (c & 0x7F)
        if c < 0x80:
            return v, i + k + 1
    return v, i + 9


def sqlite_master(data, ps):
    rows = []

    def page(no, depth=0):
        if depth > 6 or no < 1:
            return
        base = (no - 1) * ps
        h = base + (100 if no == 1 else 0)
        if h + 8 > len(data):
            return
        typ, ncell = data[h], u16(data, h + 3, ">")
        hdr = 12 if typ in (2, 5) else 8
        for c in range(ncell):
            co = base + u16(data, h + hdr + 2 * c, ">")
            if typ == 5:
                page(u32(data, co, ">"), depth + 1)
            elif typ == 13:
                _, p = sqlite_varint(data, co)
                _, p = sqlite_varint(data, p)
                hl, q = sqlite_varint(data, p)
                end, types = p + hl, []
                while q < end:
                    t, q = sqlite_varint(data, q)
                    types.append(t)
                vals, r = [], end
                for t in types:
                    if t >= 13 and t % 2:
                        n = (t - 13) // 2
                        vals.append(data[r:r + n].decode("utf-8", "replace"))
                        r += n
                    elif t >= 12:
                        n = (t - 12) // 2
                        vals.append(data[r:r + n])
                        r += n
                    else:
                        n = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 6, 6: 8, 7: 8, 8: 0, 9: 0}.get(t, 0)
                        vals.append(int.from_bytes(data[r:r + n], "big", signed=True) if n else (1 if t == 9 else 0 if t == 8 else None))
                        r += n
                rows.append(vals)
        if typ == 5:
            page(u32(data, h + 8, ">"), depth + 1)

    page(1)
    return rows


def sqlite_facts(F, data):
    ps = u16(data, 16, ">")
    ps = 65536 if ps == 1 else ps
    F.add(["page_size", "page_size_bytes"], ps)
    F.add(["write_version", "file_format_write_version"], data[18])
    F.add(["read_version", "file_format_read_version"], data[19])
    F.add(["journal_mode"], "wal" if data[18] == 2 else "rollback", 1)
    F.add(["reserved_bytes", "reserved_space"], data[20])
    F.add(["file_change_counter", "change_counter"], u32(data, 24, ">"))
    F.add(["page_count", "database_size_pages", "in_header_database_size", "db_size_pages"], u32(data, 28, ">"))
    F.add(["freelist_trunk_page", "first_freelist_trunk_page"], u32(data, 32, ">"))
    F.add(["freelist_count", "freelist_page_count", "free_pages"], u32(data, 36, ">"))
    F.add(["schema_cookie"], u32(data, 40, ">"))
    F.add(["schema_format", "schema_format_number"], u32(data, 44, ">"))
    F.add(["default_cache_size"], u32(data, 48, ">"))
    enc = u32(data, 56, ">")
    F.add(["text_encoding", "encoding", "database_text_encoding"], {1: "utf-8", 2: "utf-16le", 3: "utf-16be"}.get(enc, str(enc)), 1)
    F.add(["text_encoding_code"], enc)
    F.add(["user_version"], struct.unpack_from(">i", data, 60)[0])
    F.add(["incremental_vacuum", "auto_vacuum"], u32(data, 64, ">") != 0, 1)
    F.add(["application_id"], u32(data, 68, ">"))
    F.add(["version_valid_for"], u32(data, 92, ">"))
    v = u32(data, 96, ">")
    F.add(["sqlite_version_number", "library_version_number"], v)
    F.add(["sqlite_version", "library_version"], f"{v // 1000000}.{v // 1000 % 1000}.{v % 1000}", 1)
    F.add(["size_valid", "page_count_valid"], u32(data, 28, ">") * ps == len(data), 1)
    try:
        rows = sqlite_master(data, ps)
        tables = [r[1] for r in rows if r and r[0] == "table" and len(r) > 1]
        F.add(["table_count", "tables_count", "number_of_tables"], len(tables))
        F.add(["table_names", "tables"], ",".join(tables), 1)
        F.add(["first_table", "first_table_name"], tables[0] if tables else "none")
        F.add(["index_count"], sum(1 for r in rows if r and r[0] == "index"))
        F.add(["view_count"], sum(1 for r in rows if r and r[0] == "view"))
        F.add(["trigger_count"], sum(1 for r in rows if r and r[0] == "trigger"))
    except Exception:
        pass


def mp4_facts(F, data):
    i, boxes = 0, []
    while i + 8 <= len(data) and len(boxes) < 64:
        sz, typ = u32(data, i, ">"), data[i + 4:i + 8].decode("latin-1")
        if sz == 1 and i + 16 <= len(data):
            sz = struct.unpack_from(">Q", data, i + 8)[0]
        boxes.append(typ)
        if typ == "ftyp":
            F.add(["major_brand", "brand", "ftyp_major_brand"], data[i + 8:i + 12].decode("latin-1").strip())
            F.add(["minor_version", "ftyp_minor_version"], u32(data, i + 12, ">"))
            F.add(["compatible_brands"], ",".join(data[j:j + 4].decode("latin-1").strip() for j in range(i + 16, i + sz, 4)), 1)
        if typ == "moov":
            m = data.find(b"mvhd", i, i + sz)
            if m > 0:
                v = data[m + 4]
                ts, dur = (u32(data, m + 16, ">"), u32(data, m + 20, ">")) if v == 0 else (u32(data, m + 24, ">"), struct.unpack_from(">Q", data, m + 28)[0])
                F.add(["timescale", "mvhd_timescale"], ts)
                F.add(["duration_units", "mvhd_duration"], dur)
                if ts:
                    F.add(["duration_seconds", "duration"], numfmt(round(dur / ts, 3)), 1)
        if sz < 8:
            break
        i += sz
    F.add(["box_order", "top_level_boxes", "atoms"], ",".join(boxes), 1)
    F.add(["box_count", "atom_count"], len(boxes))


def ole_facts(F, data):
    F.add(["minor_version"], u16(data, 24))
    F.add(["major_version", "dll_version"], u16(data, 26))
    F.add(["sector_size"], 1 << u16(data, 30))
    F.add(["mini_sector_size"], 1 << u16(data, 32))
    F.add(["fat_sector_count", "num_fat_sectors"], u32(data, 44))
    F.add(["vba_present", "macros_present", "has_macros"], b"V\x00B\x00A\x00" in data or b"_VBA_PROJECT" in data.replace(b"\x00", b""), 1)


def tar_facts(F, data):
    i, names = 0, []
    while i + 512 <= len(data) and data[i:i + 1] != b"\x00":
        name = cstr(data[i:i + 100])
        try:
            sz = int(data[i + 124:i + 136].strip(b"\x00 ") or b"0", 8)
        except ValueError:
            break
        names.append(name)
        i += 512 + ((sz + 511) // 512) * 512
    F.add(["entry_count", "member_count", "file_count"], len(names))
    F.add(["first_entry", "first_member"], names[0] if names else "none")


PARSERS = {"png": png_facts, "jpeg": jpeg_facts, "gif": gif_facts, "bmp": bmp_facts, "webp": webp_facts,
           "ico": ico_facts, "pdf": pdf_facts, "zip": zip_facts, "gzip": gzip_facts, "elf": elf_facts,
           "pe": pe_facts, "wav": riff_wav_facts, "avi": riff_wav_facts, "riff": riff_wav_facts, "mp3": mp3_facts,
           "flac": flac_facts, "sqlite": sqlite_facts, "mp4": mp4_facts, "ole": ole_facts, "tar": tar_facts,
           "tiff": lambda F, d: tiff_facts(F, d, prefix="tiff")}

_FACT_CACHE = {}


def all_facts(data, name, fmt):
    key = (id(data), len(data), name, fmt)
    if key in _FACT_CACHE:
        return _FACT_CACHE[key]
    F = Facts()
    kind = sniff(data)
    try:  # format parser first: its keys win over generic file/text aliases
        if kind in PARSERS:
            PARSERS[kind](F, data)
        if kind == "tiff":
            tiff_facts(F, data, prefix="exif")
    except Exception as e:  # truncated / hostile structure: keep what was parsed
        log(f"  parser {kind} error: {e!r}")
    if fmt in ("text", "txt", "csv", "json", "xml", "html", "encoding") or kind == "text":
        try:
            text_facts(F, data)
        except Exception as e:
            log(f"  text parser error: {e!r}")
    file_facts(F, data, name)
    _FACT_CACHE[key] = (F, kind)
    return F, kind


# =====================================================================================================  field matching
UNITS = {"pixels", "pixel", "px", "bytes", "byte", "value", "field", "string", "str", "int", "integer", "number"}


def lookup(F, field, fmt):
    """-> (value, conf, matched_key) or None. conf = min(fact conf, match conf)."""
    f = canon(field)
    tries = [f]
    for pre in {fmt, canon(fmt)} | ({"jpg", "jpeg"} if fmt in ("jpg", "jpeg") else set()):
        if f.startswith(pre + "_"):
            tries.append(f[len(pre) + 1:])
    tries.append(f"{canon(fmt)}_{f}")
    toks = f.split("_")
    if toks[-1] in UNITS and len(toks) > 1:
        tries.append("_".join(toks[:-1]))
    if toks[0] == "is" and len(toks) > 1:
        tries.append("_".join(toks[1:]))
    for k in tries:
        if k in F.d:
            v, c = F.get(k)
            return v, c, k
    core = lambda k: frozenset(t for t in k.split("_") if t not in UNITS and t != fmt)
    fs = core(f)
    if not fs:
        return None
    hits = {k: F.get(k) for k in list(F.d) if core(k) == fs}
    if hits and len({v[0] for v in hits.values()}) == 1:
        k = min(hits)
        return hits[k][0], min(hits[k][1], 2), k
    hits = {k: F.get(k) for k in list(F.d) if fs <= core(k) and len(core(k)) - len(fs) <= 1}
    if hits and len({v[0] for v in hits.values()}) == 1:
        k = min(hits)
        return hits[k][0], min(hits[k][1], 1), k
    return None


# =====================================================================================================  registry
REGISTRY = {}  # (fmt, field-regex) -> (day, fn(ctx) -> value)


def reg(fmt, field, day):
    def deco(fn):
        REGISTRY[(fmt, field)] = (day, fn)
        return fn
    return deco


def _disabled_days():
    v = os.environ.get("METADATA_DISABLE_DAYS", "").strip().lower()
    if v == "all":
        return set(range(0, 100))
    return {int(x) for x in re.findall(r"\d+", v)}


@reg("file", r"filename", 1)
def r_filename(c):
    return c["name"].split("/")[-1]


@reg("file", r"size_bytes", 1)
def r_size(c):
    return str(len(c["data"]))


@reg("file", r"(md5|sha1|sha256)", 1)
def r_digest(c):
    return hashlib.new(c["field"], c["data"]).hexdigest()


@reg("file", r"magic_prefix_hex_(\d+)", 2)
def r_magic(c):
    return c["data"][:int(c["m"].group(1))].hex()


@reg("text", r"(utf8|utf16le|utf16be|utf32le|utf32be)_bom_present", 3)
def r_bom(c):
    sig = {"utf8": b"\xef\xbb\xbf", "utf16le": b"\xff\xfe", "utf16be": b"\xfe\xff", "utf32le": b"\xff\xfe\x00\x00",
           "utf32be": b"\x00\x00\xfe\xff"}[c["m"].group(1)]
    d = c["data"]
    hit = d.startswith(sig) and not (c["m"].group(1) == "utf16le" and d.startswith(b"\xff\xfe\x00\x00"))
    return B(hit)


@reg("jpeg", r"sof_dimensions_pixels", 4)
def r_jpeg_sof(c):
    if sniff(c["data"]) != "jpeg":
        return "none"
    segs, _ = jpeg_segments(c["data"])
    p = next((p for m, p, _ in segs if m in SOF_NAMES and len(p) >= 6), None)
    if p is None:
        return "none"
    _, h, w, _ = struct.unpack(">BHHB", p[:6])
    return JPEG_DIMENSIONS_FMT.format(width=w, height=h)


@reg("png", r"ihdr_dimensions_pixels", 5)
def r_png_ihdr(c):
    d = c["data"]
    if sniff(d) != "png" or d[12:16] != b"IHDR":
        return "none"
    w, h = struct.unpack(">II", d[16:24])
    return PNG_DIMENSIONS_FMT.format(width=w, height=h)


@reg("pdf", r"header_version", 6)
def r_pdf_header(c):
    m = re.match(rb"%PDF-(\d+)\.(\d+)", c["data"].lstrip(LEAD)[:16])
    return PDF_HEADER_VERSION_FMT.format(major=int(m.group(1)), minor=int(m.group(2))) if m else "none"


def registry_answer(fmt, field, ctx):
    off = _disabled_days()
    for (rf, rx), (day, fn) in REGISTRY.items():
        if day in off:
            continue
        if rf != fmt and not (rf == "file" and fmt in ("file", "")):
            continue
        m = re.fullmatch(rx, field)
        if m:
            return fn(dict(ctx, m=m, field=field)), day
    return None, None


# =====================================================================================================  questions
SET_RE = re.compile(r"^(?:set|slot)[._-]?\d+[._-]")
GRAMMAR = re.compile(r"\bdetermine\s+([a-z][a-z0-9]*)\.([a-z0-9_]+)\s+(?:for|of|in)\s+(.+?)\s*\.?\s*$", re.I)
LOOSE = re.compile(r"(?<![\w.-])([a-z][a-z0-9]*)\.([a-z][a-z0-9]*(?:_[a-z0-9]+)+|[a-z][a-z0-9]*)\b(?!\.)", re.I)
AID_V2 = re.compile(r"^(?:d\d+-)?([a-z0-9]+)-(\d+)-\1-([a-z0-9-]+)$")
ERA1_SUFFIX = [(r"filename", "filename"), (r"file-?name", "filename"), (r"size-bytes", "size_bytes"),
               (r"size", "size_bytes"), (r"md5", "md5"), (r"sha-?1", "sha1"), (r"sha-?256", "sha256"),
               (r"sha-?512", "sha512"), (r"crc-?32", "crc32"), (r"magic-prefix-hex-(\d+)", None),
               (r"prefix-hex-(\d+)", None), (r"first-(\d+)-bytes(?:-hex)?", None)]
NUMW = {"one": 1, "two": 2, "four": 4, "eight": 8, "twelve": 12, "sixteen": 16, "thirty-two": 32, "sixty-four": 64}


def parse_question(aid, q):
    """-> dict(fmt, field, file, stem) ; fmt 'file' for the era-1 identity family."""
    slug = SET_RE.sub("", aid)
    qt = (q.get("question") or "").strip()
    stale = bool(q.get("id")) and q.get("id") != aid
    m = GRAMMAR.search(qt) if not stale else None
    if m:
        fmt, field, file = m.group(1).lower(), m.group(2).lower(), m.group(3).strip().strip("'\"`")
        stem = slug
        mm = re.search(r"-" + re.escape(fmt) + "-" + re.escape(field.replace("_", "-")) + "$", slug)
        if mm:
            stem = slug[:mm.start()]
        return dict(fmt=fmt, field=field, file=file, stem=stem)
    for mm in (LOOSE.finditer(qt) if not stale else ()):  # other verbs: "Report png.bit_depth of x.png"
        fmt, field = mm.group(1).lower(), mm.group(2).lower()
        if fmt in FAMILY or fmt in NO_IMPOSTOR or "_" in field:
            fm = re.search(r"\b(?:for|of|in)\s+(\S+?)\s*\.?\s*$", qt)
            return dict(fmt=fmt, field=field, file=fm.group(1).strip("'\"`") if fm else None,
                        stem=re.sub(r"-" + re.escape(fmt) + "-" + re.escape(field.replace("_", "-")) + "$", "", slug))
    m = AID_V2.match(slug)
    if m:
        return dict(fmt=m.group(1), field=m.group(3).replace("-", "_"), file=None, stem=f"{m.group(1)}-{m.group(2)}")
    for fmt in sorted(set(FAMILY) | {"text"}, key=len, reverse=True):
        k = slug.rfind(f"-{fmt}-")
        if k > 0:
            return dict(fmt=fmt, field=slug[k + len(fmt) + 2:].replace("-", "_"), file=None, stem=slug[:k])
    for rx, field in ERA1_SUFFIX:
        mm = re.search(r"-(" + rx + r")$", slug)
        if mm:
            if field is None:
                field = f"magic_prefix_hex_{mm.group(2)}"
            return dict(fmt="file", field=field, file=None, stem=slug[:mm.start()])
    t = qt.lower()  # natural-language fallback
    nl = None
    if "filename" in t or "file name" in t:
        nl = "filename"
    elif "md5" in t:
        nl = "md5"
    elif re.search(r"sha-?1\b", t):
        nl = "sha1"
    elif re.search(r"sha-?256", t):
        nl = "sha256"
    elif "size" in t and "byte" in t:
        nl = "size_bytes"
    else:
        mm = re.search(r"first\s+(\d+|[a-z-]+)\s+bytes", t)
        if mm and "hex" in t:
            n = int(mm.group(1)) if mm.group(1).isdigit() else NUMW.get(mm.group(1))
            nl = f"magic_prefix_hex_{n}" if n else None
    if nl:
        return dict(fmt="file", field=nl, file=None, stem=slug)
    return None


# =====================================================================================================  evidence
def _tokens(s):
    return [t for t in re.split(r"[^a-z0-9]+", s.lower()) if t]


class Evidence:
    def __init__(self, root, contract):
        self.root, self.contract = Path(root), contract
        self.files = sorted(p for p in self.root.rglob("*") if p.is_file())
        self._b, self._m = {}, {}

    def read(self, p):
        if p not in self._b:
            self._b[p] = p.read_bytes()
        return self._b[p]

    def members(self, data, depth=0):
        """[(basename, fullname, bytes, parent_basename, depth)] for a zip blob, recursing into nested zips."""
        key = (id(data), len(data))
        if key in self._m:
            return self._m[key]
        out = []
        self._walk(data, None, depth, out)
        self._m[key] = out
        return out

    def _walk(self, data, parent, depth, out):
        if depth > 4 or data[:2] != b"PK":
            return
        try:
            z = _ZipFile(io.BytesIO(data))
        except Exception:
            return
        for info in z.infolist():
            if info.filename.endswith("/"):
                continue
            b = None
            try:
                b = z.read(info.filename)
            except (RuntimeError, NotImplementedError, Exception):
                for pw in ZIP_PASSWORDS:
                    try:
                        b = z.read(info.filename, pwd=pw)
                        break
                    except Exception:
                        continue
            if b is None:
                continue
            base = info.filename.rsplit("/", 1)[-1]
            out.append((base, info.filename, b, parent, depth))
            if b[:4] == b"PK\x03\x04":
                self._walk(b, base, depth + 1, out)

    def containers(self, container):
        cbase = container.rsplit("/", 1)[-1]
        cands = [p for p in self.files if p.name in (container, cbase)]
        try:
            p = container_by_sha(self.root, self.contract, container)
        except Exception:
            p = None
        if p is not None and p not in cands:
            cands.insert(0, p)
        return cands

    def resolve(self, artifact, member_override=None, hint=""):
        """-> (bytes, member_name, container_member_list). member_override wins over the artifact's member."""
        container, _, member = (artifact or "").partition("->")
        container, member = container.strip(), (member_override or member).strip()
        cbase = container.rsplit("/", 1)[-1]
        mbase = member.rsplit("/", 1)[-1]
        cands = self.containers(container)
        pools = []
        for p in cands:
            raw = self.read(p)
            mems = self.members(raw)
            if not member:
                inner = [m for m in mems if m[3] == cbase and m[4] > 0]  # same-named bundle wrapping the real zip
                if inner:
                    return None, cbase, inner
                return raw, p.name, [m for m in mems if m[4] == 0] or [(p.name, p.name, raw, None, 0)]
            pools.append(mems)
            for want in (lambda m: m[0] == mbase and m[4] == 0, lambda m: m[0] == mbase and m[3] == cbase,
                         lambda m: m[0] == mbase, lambda m: m[0].lower() == mbase.lower()):
                hit = next((m for m in mems if want(m)), None)
                if hit:
                    return hit[2], hit[0], [m for m in mems if m[3] == hit[3]]
            if not mems and raw and p.name == mbase:
                return raw, p.name, []
        if not cands:  # the named container is not on disk: look inside every bundle, prefer parent == container
            try:
                missing = delivery_missing(self.root, self.contract, container)
            except Exception:
                missing = False
            allm = []
            for p in self.files:
                if member and p.name == mbase:
                    return self.read(p), p.name, []
                allm += self.members(self.read(p))
            pools.append(allm)
            for want in (lambda m: m[0] == mbase and m[3] == cbase,) + (() if missing else (lambda m: m[0] == mbase,)):
                hit = next((m for m in allm if want(m)), None)
                if hit:
                    return hit[2], hit[0], [m for m in allm if m[3] == hit[3]]
            if not member:
                hit = [m for m in allm if m[3] == cbase]
                if hit:
                    return None, cbase, hit
            if missing:
                raise FileNotFoundError(f"{container}: delivery missing (not answering from another set)")
        # hinted fallback (stale question text): best token match of hint vs member names in the pools
        htoks = _tokens(hint)
        best = None
        for mems in pools:
            names = [m for m in mems if m[4] == min((x[4] for x in mems), default=0)]
            for m in mems:
                mt = _tokens(m[0])
                score = sum(any(h.startswith(t) or t.startswith(h) for h in htoks) for t in mt if len(t) >= 2)
                if len(names) == 1:
                    score += 0.5
                if score and (best is None or score > best[0]):
                    best = (score, m)
        if best:
            return best[1][2], best[1][0], []
        raise FileNotFoundError(f"{artifact!r} not found (hint {hint!r})")


def pick_member(mems, label, subject):
    """Era-1 filename questions name only the zip: resolve the subject ('renamed evidence-note copy') to a member."""
    if label:
        for m in mems:
            if m[0] == label or m[1] == label:
                return m
    want = set(_tokens(subject)) - {"the", "of", "first", "a", "an", "file", "renamed", "exact", "filename"}
    best = None
    for m in mems:
        stem = m[0].rsplit(".", 1)[0]
        mt = set(_tokens(stem))
        exact = _tokens(stem) == _tokens(subject.replace("renamed ", ""))
        score = (2 if exact else 0) + len(want & mt) - 0.01 * len(mt - want)
        if score > 0 and (best is None or score > best[0]):
            best = (score, m)
    if best:
        return best[1]
    return mems[0] if len(mems) == 1 else None


# =====================================================================================================  answer format
def fits_format(v, q):
    af = q.get("answer_format") or {}
    kind, syn = af.get("kind"), (af.get("syntax") or "").lower()
    acc = af.get("accepted_values")
    if acc:
        hit = next((a for a in acc if str(a).lower() == v.lower()), None)
        return hit
    if v == "none":
        return v if ("none" in syn or kind == "exact_text") else None
    if kind == "integer" and not re.fullmatch(r"-?\d+", v):
        return None
    m = re.search(r"exact\s+(\d+)[- ]character hex|exact\s+(\d+)\s+hexadecimal", syn)
    if m and not re.fullmatch(r"[0-9a-fA-F]{%s}" % (m.group(1) or m.group(2)), v):
        return None
    return v


def normalize(v, q):
    v = str(v)
    norm = (q or {}).get("normalization")
    if norm in ("trim", "case_insensitive", "exact", None):
        v = v.strip()
    if norm in ("case_insensitive", "lowercase"):
        v = v.lower()
    return v


# =====================================================================================================  main
def solve(contract, artifacts, min_conf=None):
    min_conf = int(os.environ.get("METADATA_MIN_CONF", "2")) if min_conf is None else min_conf
    _FACT_CACHE.clear()  # keyed by id(bytes): only valid while this solve's Evidence keeps the blobs alive
    qs = contract.get("questions") or []
    ids = contract.get("answer_ids") or [q.get("id") for q in qs]
    pairs = [(aid, qs[i] if i < len(qs) else {}) for i, aid in enumerate(ids)]
    ev = Evidence(artifacts, contract)
    parsed = {aid: parse_question(aid, q) if q else None for aid, q in pairs}
    # era-1 groups: share the member label across sibling questions (filename asks name only the zip)
    labels = {}
    for aid, q in pairs:
        P = parsed[aid]
        art = (q or {}).get("artifact") or ""
        if P and "->" in art and not (q.get("id") and q.get("id") != aid):
            labels.setdefault((SET_RE.match(aid).group(0) if SET_RE.match(aid) else "", P["stem"]),
                              art.split("->", 1)[1].strip())
    out, explain = {}, {}
    for aid, q in pairs:
        P = parsed[aid]
        rec = explain.setdefault(aid, {})
        if not q or not P:
            rec["skip"] = "unparsed question"
            continue
        rec.update(P)
        setp = SET_RE.match(aid).group(0) if SET_RE.match(aid) else ""
        art = q.get("artifact") or ""
        stale = bool(q.get("id")) and q.get("id") != aid
        try:
            member = P["file"] if (P["file"] and "->" not in art) else None
            if stale:  # question text belongs to another id: trust answer_ids, resolve by the id stem
                art, member = art.split("->")[0].strip() + " -> " + P["stem"], None
            data, name, sib = ev.resolve(art, member, hint=P["stem"] + " " + (P["file"] or ""))
            if "->" not in art and not member and P["fmt"] == "file":
                subj = re.search(r"filename of (?:the )?(.+?)\?", q.get("question", ""))
                m = pick_member(sib, labels.get((setp, P["stem"])), subj.group(1) if subj else P["stem"].replace("-", " "))
                if not m:
                    raise FileNotFoundError("cannot resolve member for filename question")
                data, name = m[2], m[0]
        except Exception as e:
            rec["error"] = str(e)
            log(f"{aid}: {e}")
            continue
        fmt, field = P["fmt"], P["field"]
        ctx = dict(data=data, name=name, q=q)
        val, conf, src = None, 0, None
        v, day = registry_answer(fmt, field, ctx)
        if v is not None:
            val, conf, src = v, 3, f"registry(day{day})"
        else:
            F, kind = all_facts(data, name, fmt)
            fam = FAMILY.get(fmt)
            if fam and fmt not in NO_IMPOSTOR and kind not in fam and not FILE_LEVEL.match(field):
                val, conf, src = "none", 2, f"impostor({kind}!={fmt})"
            else:
                hit = lookup(F, field, fmt)
                if hit:
                    val, conf, src = hit[0], hit[1], f"generic[{kind}].{hit[2]}"
            rec["sniffed"] = kind
        if val is not None:
            fv = fits_format(normalize(val, q), q)
            if fv is None:
                rec["rejected_by_format"] = val
                conf, val = 0, val
            else:
                val = fv
        rec.update(value=val, conf=conf, source=src, member=name, size=len(data))
        if val is not None and conf >= min_conf:
            out[aid] = normalize(val, q)
        log(f"{aid}: {fmt}.{field} <- {name} ({len(data)}B) = {val!r} conf={conf} via {src}"
            + ("" if conf >= min_conf else "  [NOT EMITTED]"))
    return out, explain


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    ap.add_argument("--explain", help="write per-question diagnostics (value, conf, source, candidates) here")
    ap.add_argument("--min-conf", type=int, default=None)
    a = ap.parse_args()
    t0 = time.time()
    contract = json.loads(Path(a.contract).read_text())
    out, explain = solve(contract, a.artifacts, a.min_conf)
    if a.explain:
        Path(a.explain).write_text(json.dumps(explain, indent=1, default=str))
    log(f"metadata_lane: {len(out)}/{len(explain)} answered in {1000 * (time.time() - t0):.1f} ms")
    if not out:
        print("{}")
        sys.exit(1)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
