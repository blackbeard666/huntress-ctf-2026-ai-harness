"""Prefixed / self-executing ZIP launchers (prebuilt, SPECULATIVE -- never GM-asked yet).

A shebang jar (`cat stub.sh app.jar`), an exe+zip overlay (PE SFX), a zipapp (`python -m zipapp -p ...`) or any
`cat prefix archive.zip` keeps a valid ZIP whose magic @0 is NOT "PK". The archive is located from the TAIL: the
last EOCD whose comment ends at EOF (lib/meta/prebuilt/zip.py `_eocd`, the D7/D8 rule), ZIP64 via its locator.
  archive_start = cd_start - cd_offset, cd_start = eocd_offset - cd_size (zip64: eocd64_offset - cd_size). It is the
    prefix length while the CD offsets are still RELATIVE to the zip (plain `cat`); `zip -A` rewrites them absolute,
    so archive_start becomes 0. prefix_length_bytes therefore = the file offset of the first local header ("PK\\x03\\x04"
    at archive_start + min(CD local-header offset)), which is the prefix length in BOTH cases (= Python zipfile's
    min(ZipInfo.header_offset), 7z's `Offset`, unzip's "N extra bytes at beginning").
  lfh_offsets_relative: archive_start > 0 (CD offsets need the prefix added; unzip warns, `zip -A` clears it).
  prefix_kind: "shebang" (#!), "pe" (MZ + e_lfanew -> PE\\0\\0), "elf" (\\x7fELF), "script" (printable ASCII text without
    #!), else "data"; no prefix -> "none". shebang_line: the first prefix line verbatim, without CR/LF.
  pe_overlay_offset_hex: pefile-free -- max(PointerToRawData + SizeOfRawData) over the section table (pefile's
    get_overlay_data_start_offset); u32 -> Hex(.., 8). No PE / no bytes past it -> "none".
  overlay_magic_hex_8 (family overlay_magic_hex_N): N bytes at the PE overlay, else at the embedded archive start,
    lowercase hex without 0x (the file.magic_prefix_hex_* spelling).
  embedded_archive_format: the earliest archive that starts AFTER offset 0 (after the PE overlay start for a PE):
    zip (first LFH from the EOCD walk) / 7z ('7z\\xbc\\xaf\\x27\\x1c') / rar ('Rar!\\x1a\\x07') / cab ('MSCF\\0\\0\\0\\0').
  embedded_jar_main_class: META-INF/MANIFEST.MF Main-Class (jar.parse_manifest) of the shifted zip.
  zipapp_main_present: a top-level `__main__.py` member (what `python app.pyz` runs).
Registered under fmt zip and the aliases jar / pyz / sfx. Not a zip (no EOCD) -> "none" for zip-derived fields."""
import io
import struct
import zipfile

from ..spell import Hex
from .zip import _eocd

FIELDS = {
    ("zip", "prefix_length_bytes"): "prefix_length",
    ("zip", "prefix_length"): "prefix_length",
    ("zip", "prefix_size_bytes"): "prefix_length",
    ("zip", "stub_size_bytes"): "prefix_length",
    ("zip", "archive_start_offset"): "prefix_length",
    ("zip", "zip_start_offset"): "prefix_length",
    ("zip", "archive_offset"): "prefix_length",
    ("zip", "eocd_offset"): "eocd_offset",
    ("zip", "prefix_kind"): "prefix_kind",
    ("zip", "prefix_type"): "prefix_kind",
    ("zip", "shebang_line"): "shebang_line",
    ("zip", "shebang"): "shebang_line",
    ("zip", "pe_overlay_offset_hex"): "pe_overlay_offset",
    ("zip", "overlay_offset_hex"): "pe_overlay_offset",
    ("zip", "pe_overlay_offset"): "pe_overlay_offset",
    ("zip", "overlay_offset"): "pe_overlay_offset",
    ("zip", "overlay_magic_hex_8"): "overlay_magic",
    ("zip", "overlay_magic_hex_*"): "overlay_magic",
    ("zip", "embedded_archive_format"): "embedded_archive_format",
    ("zip", "embedded_archive_type"): "embedded_archive_format",
    ("zip", "embedded_archive_offset"): "embedded_archive_offset",
    ("zip", "embedded_jar_main_class"): "embedded_jar_main_class",
    ("zip", "zipapp_main_present"): "zipapp_main_present",
    ("zip", "main_py_present"): "zipapp_main_present",
    ("zip", "lfh_offsets_relative"): "lfh_offsets_relative",
    ("zip", "cd_offsets_relative"): "lfh_offsets_relative",
    ("zip", "offsets_relative_to_prefix"): "lfh_offsets_relative",
    ("jar", "prefix_length_bytes"): "prefix_length",
    ("jar", "prefix_length"): "prefix_length",
    ("jar", "prefix_size_bytes"): "prefix_length",
    ("jar", "stub_size_bytes"): "prefix_length",
    ("jar", "archive_start_offset"): "prefix_length",
    ("jar", "zip_start_offset"): "prefix_length",
    ("jar", "archive_offset"): "prefix_length",
    ("jar", "eocd_offset"): "eocd_offset",
    ("jar", "prefix_kind"): "prefix_kind",
    ("jar", "prefix_type"): "prefix_kind",
    ("jar", "shebang_line"): "shebang_line",
    ("jar", "shebang"): "shebang_line",
    ("jar", "pe_overlay_offset_hex"): "pe_overlay_offset",
    ("jar", "overlay_offset_hex"): "pe_overlay_offset",
    ("jar", "pe_overlay_offset"): "pe_overlay_offset",
    ("jar", "overlay_offset"): "pe_overlay_offset",
    ("jar", "overlay_magic_hex_8"): "overlay_magic",
    ("jar", "overlay_magic_hex_*"): "overlay_magic",
    ("jar", "embedded_archive_format"): "embedded_archive_format",
    ("jar", "embedded_archive_type"): "embedded_archive_format",
    ("jar", "embedded_archive_offset"): "embedded_archive_offset",
    ("jar", "embedded_jar_main_class"): "embedded_jar_main_class",
    ("jar", "zipapp_main_present"): "zipapp_main_present",
    ("jar", "main_py_present"): "zipapp_main_present",
    ("jar", "lfh_offsets_relative"): "lfh_offsets_relative",
    ("jar", "cd_offsets_relative"): "lfh_offsets_relative",
    ("jar", "offsets_relative_to_prefix"): "lfh_offsets_relative",
    ("pyz", "prefix_length_bytes"): "prefix_length",
    ("pyz", "prefix_length"): "prefix_length",
    ("pyz", "prefix_size_bytes"): "prefix_length",
    ("pyz", "stub_size_bytes"): "prefix_length",
    ("pyz", "archive_start_offset"): "prefix_length",
    ("pyz", "zip_start_offset"): "prefix_length",
    ("pyz", "archive_offset"): "prefix_length",
    ("pyz", "eocd_offset"): "eocd_offset",
    ("pyz", "prefix_kind"): "prefix_kind",
    ("pyz", "prefix_type"): "prefix_kind",
    ("pyz", "shebang_line"): "shebang_line",
    ("pyz", "shebang"): "shebang_line",
    ("pyz", "pe_overlay_offset_hex"): "pe_overlay_offset",
    ("pyz", "overlay_offset_hex"): "pe_overlay_offset",
    ("pyz", "pe_overlay_offset"): "pe_overlay_offset",
    ("pyz", "overlay_offset"): "pe_overlay_offset",
    ("pyz", "overlay_magic_hex_8"): "overlay_magic",
    ("pyz", "overlay_magic_hex_*"): "overlay_magic",
    ("pyz", "embedded_archive_format"): "embedded_archive_format",
    ("pyz", "embedded_archive_type"): "embedded_archive_format",
    ("pyz", "embedded_archive_offset"): "embedded_archive_offset",
    ("pyz", "embedded_jar_main_class"): "embedded_jar_main_class",
    ("pyz", "zipapp_main_present"): "zipapp_main_present",
    ("pyz", "main_py_present"): "zipapp_main_present",
    ("pyz", "lfh_offsets_relative"): "lfh_offsets_relative",
    ("pyz", "cd_offsets_relative"): "lfh_offsets_relative",
    ("pyz", "offsets_relative_to_prefix"): "lfh_offsets_relative",
    ("sfx", "prefix_length_bytes"): "prefix_length",
    ("sfx", "prefix_length"): "prefix_length",
    ("sfx", "prefix_size_bytes"): "prefix_length",
    ("sfx", "stub_size_bytes"): "prefix_length",
    ("sfx", "archive_start_offset"): "prefix_length",
    ("sfx", "zip_start_offset"): "prefix_length",
    ("sfx", "archive_offset"): "prefix_length",
    ("sfx", "eocd_offset"): "eocd_offset",
    ("sfx", "prefix_kind"): "prefix_kind",
    ("sfx", "prefix_type"): "prefix_kind",
    ("sfx", "shebang_line"): "shebang_line",
    ("sfx", "shebang"): "shebang_line",
    ("sfx", "pe_overlay_offset_hex"): "pe_overlay_offset",
    ("sfx", "overlay_offset_hex"): "pe_overlay_offset",
    ("sfx", "pe_overlay_offset"): "pe_overlay_offset",
    ("sfx", "overlay_offset"): "pe_overlay_offset",
    ("sfx", "overlay_magic_hex_8"): "overlay_magic",
    ("sfx", "overlay_magic_hex_*"): "overlay_magic",
    ("sfx", "embedded_archive_format"): "embedded_archive_format",
    ("sfx", "embedded_archive_type"): "embedded_archive_format",
    ("sfx", "embedded_archive_offset"): "embedded_archive_offset",
    ("sfx", "embedded_jar_main_class"): "embedded_jar_main_class",
    ("sfx", "zipapp_main_present"): "zipapp_main_present",
    ("sfx", "main_py_present"): "zipapp_main_present",
    ("sfx", "lfh_offsets_relative"): "lfh_offsets_relative",
    ("sfx", "cd_offsets_relative"): "lfh_offsets_relative",
    ("sfx", "offsets_relative_to_prefix"): "lfh_offsets_relative",
}


def _cd_walk(b, p, n_max=65535 * 16):
    """[(local header offset, name)] walking CD headers from p."""
    out = []
    while 0 <= p and b[p:p + 4] == b"PK\x01\x02" and p + 46 <= len(b) and len(out) < n_max:
        nl, el, cl = struct.unpack_from("<HHH", b, p + 28)
        off, = struct.unpack_from("<I", b, p + 42)
        name = bytes(b[p + 46:p + 46 + nl])
        if off == 0xFFFFFFFF:   # ZIP64 extra: usize, csize, offset -- only the 0xFFFFFFFF ones, in that order
            usz, csz = struct.unpack_from("<II", b, p + 20)
            ext, q = b[p + 46 + nl:p + 46 + nl + el], 0
            while q + 4 <= len(ext):
                hid, ln = struct.unpack_from("<HH", ext, q)
                if hid == 1:
                    k = q + 4 + 8 * ((usz == 0xFFFFFFFF) + (csz == 0xFFFFFFFF))
                    if k + 8 <= q + 4 + ln:
                        off, = struct.unpack_from("<Q", ext, k)
                    break
                q += 4 + ln
        out.append((off, name))
        p += 46 + nl + el + cl
    return out


def locate(b):
    """{eocd, archive_start, prefix, entries} of the tail-located zip, or None (not a zip)."""
    if not b or len(b) < 22:
        return None
    eo = _eocd(b)
    if eo is None:
        return None
    _n, cd_size, cd_off = struct.unpack_from("<HII", b, eo + 10)
    end = eo
    if (cd_off == 0xFFFFFFFF or cd_size == 0xFFFFFFFF) and eo >= 20 and b[eo - 20:eo - 16] == b"PK\x06\x07":
        p64 = eo - 56   # the zip64 EOCD record normally sits right before its locator
        if p64 < 0 or b[p64:p64 + 4] != b"PK\x06\x06":
            p64 = b.rfind(b"PK\x06\x06", 0, eo - 20)
        if p64 >= 0 and p64 + 56 <= len(b):
            cd_size, cd_off = struct.unpack_from("<QQ", b, p64 + 40)
            end = p64
    cd_start = end - cd_size
    if cd_start < 0:
        return None
    start = cd_start - cd_off
    if b[cd_start:cd_start + 4] != b"PK\x01\x02" and cd_size:
        if 0 <= cd_off < len(b) and b[cd_off:cd_off + 4] == b"PK\x01\x02":   # junk between CD and EOCD
            cd_start, start = cd_off, 0
        else:
            return None
    start = max(start, 0)
    ents = _cd_walk(b, cd_start) if cd_size else []
    prefix = start
    if ents:
        lo = min(o for o, _ in ents)
        if b[start + lo:start + lo + 4] == b"PK\x03\x04":
            prefix = start + lo
        elif b[lo:lo + 4] == b"PK\x03\x04":
            prefix = lo
    return {"eocd": eo, "archive_start": start, "prefix": prefix, "entries": ents}


def pe_overlay(b):
    """Overlay start (end of the last section's raw data) of a PE, or None (not a PE)."""
    if not b or b[:2] != b"MZ" or len(b) < 0x40:
        return None
    lf, = struct.unpack_from("<I", b, 0x3C)
    if lf + 24 > len(b) or b[lf:lf + 4] != b"PE\x00\x00":
        return None
    nsec, = struct.unpack_from("<H", b, lf + 6)
    opt, = struct.unpack_from("<H", b, lf + 20)
    st, end = lf + 24 + opt, 0
    falign = 0
    if opt >= 40:
        falign, = struct.unpack_from("<I", b, lf + 24 + 36)
    for i in range(min(nsec, 96)):
        o = st + 40 * i
        if o + 40 > len(b):
            break
        raw_size, raw_ptr = struct.unpack_from("<II", b, o + 16)
        if raw_size == 0:
            continue
        if falign >= 0x200:     # pefile adjust_FileAlignment: the loader rounds PointerToRawData down to 0x200
            raw_ptr = raw_ptr // 0x200 * 0x200
        end = max(end, raw_ptr + raw_size)
    return end or st + 40 * nsec


def _kind(p):
    if not p:
        return "none"
    if p[:2] == b"#!":
        return "shebang"
    if p[:4] == b"\x7fELF":
        return "elf"
    if p[:2] == b"MZ" and pe_overlay(p + b"\x00" * 64) is not None:
        return "pe"
    try:
        t = p.decode("ascii")
    except UnicodeDecodeError:
        return "data"
    return "script" if all(c.isprintable() or c in "\r\n\t\f" for c in t) else "data"


def _guard(fn):
    def w(data, ctx):
        if data is None:
            return None
        try:
            return fn(bytes(data), ctx)
        except Exception:  # noqa: BLE001 -- truncated / hostile input
            return "none"
    return w


def _prefix_bytes(b):
    loc = locate(b)
    return None if loc is None else b[:loc["prefix"]]


@_guard
def prefix_length(b, ctx):
    loc = locate(b)
    return "none" if loc is None else loc["prefix"]


@_guard
def eocd_offset(b, ctx):
    loc = locate(b)
    return "none" if loc is None else loc["eocd"]


@_guard
def prefix_kind(b, ctx):
    p = _prefix_bytes(b)
    return "none" if p is None else _kind(p)


@_guard
def shebang_line(b, ctx):
    p = _prefix_bytes(b)
    if not p or p[:2] != b"#!":
        return "none"
    line = p.split(b"\n", 1)[0].rstrip(b"\r")
    return line.decode("utf-8", "replace")


@_guard
def pe_overlay_offset(b, ctx):
    ov = pe_overlay(b)
    if ov is None or ov >= len(b):
        return "none"
    return Hex(ov, 8) if (ctx.get("field") or "").endswith("_hex") else ov


def _embedded(b):
    """(format, offset) of the earliest archive starting after 0 (after the overlay for a PE), or None."""
    ov = pe_overlay(b)
    lo = ov if ov is not None else 1
    hits = []
    loc = locate(b)
    if loc is not None and loc["prefix"] >= lo:
        hits.append((loc["prefix"], "zip"))
    for fmt, sig in (("7z", b"7z\xbc\xaf\x27\x1c"), ("rar", b"Rar!\x1a\x07"), ("cab", b"MSCF\x00\x00\x00\x00")):
        i = b.find(sig, lo)
        if i >= 0:
            hits.append((i, fmt))
    if not hits:
        return None
    off, fmt = min(hits)
    return fmt, off


@_guard
def embedded_archive_format(b, ctx):
    e = _embedded(b)
    return "none" if e is None else e[0]


@_guard
def embedded_archive_offset(b, ctx):
    e = _embedded(b)
    return "none" if e is None else e[1]


@_guard
def overlay_magic(b, ctx):
    p = ctx.get("param")
    try:
        n = int(p) if p not in (None, "") else int((ctx.get("field") or "").rsplit("_", 1)[-1])
    except ValueError:
        n = 8
    ov = pe_overlay(b)
    if ov is None or ov >= len(b):
        e = _embedded(b)
        ov = None if e is None else e[1]
    if ov is None or ov >= len(b):
        return "none"
    return b[ov:ov + n]


def _zf(b):
    try:
        return zipfile.ZipFile(io.BytesIO(b))
    except Exception:  # noqa: BLE001
        return None


@_guard
def embedded_jar_main_class(b, ctx):
    from .jar import _manifest_bytes, parse_manifest
    z = _zf(b)
    mf = None if z is None else parse_manifest(_manifest_bytes(z))
    hit = (mf or {}).get("main-class")
    return "none" if hit is None or not hit[1].strip() else hit[1].strip()


@_guard
def zipapp_main_present(b, ctx):
    loc = locate(b)
    if loc is None:
        return "none"
    return any(n == b"__main__.py" for _o, n in loc["entries"])


@_guard
def lfh_offsets_relative(b, ctx):
    loc = locate(b)
    return "none" if loc is None else loc["archive_start"] > 0
