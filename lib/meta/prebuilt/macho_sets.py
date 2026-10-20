"""Mach-O universal (fat) per-slice SET fields (prebuilt, SPECULATIVE except where noted).

D20 GM-verified `macho.cpu_type_set` (built-in lib/meta/macho.py): every slice's cputype as "0x%08x" in a compact
JSON list, thin arm64 -> ["0x0100000c"] (the arch-name list ["arm64"] was REJECTED). This module answers the sibling
set/list fields (and the same fields under the format tokens mach_o / universal / macos) with LISTS, never a bare
scalar.

Fat header (<mach-o/fat.h>, ALWAYS big-endian): magic u32 FAT_MAGIC 0xcafebabe (fat_arch 20 B: cputype, cpusubtype,
offset u32, size u32, align u32) / FAT_MAGIC_64 0xcafebabf (fat_arch_64 32 B: cputype, cpusubtype, offset u64,
size u64, align u32, reserved u32), nfat_arch u32. Each slice at `offset` carries its own mach_header in its own byte
order (bytes cffaedfe/cefaedfe = little-endian MH_MAGIC_64/MH_MAGIC, feedfacf/feedface = big-endian).
0xcafebabe is also the Java .class magic: u32 @4 is then (minor << 16 | major) with major >= 45, so nfat_arch >= 45
(or 0) -> not fat -> "none".

Conventions (GM spelling unverified beyond cpu_type_set):
  *_set   = fat_arch (table) order, duplicates dropped keeping the first occurrence; *_list = no dedupe.
  cpu_subtype_* = the RAW cpusubtype including capability bits (arm64e ptrauth 0x80000002); *_masked_* = & 0x00ffffff.
  thin file: the set/list fields answer from its own header (one element); slice_count = 1; fat_* table fields
  (nfat_arch, magic, offsets, sizes, aligns) = "none"; fat_slice_mismatch = false; mismatched_slice_indexes = [].
  slice_header_* = read from each slice's OWN header at its offset (a slice without a Mach-O magic is skipped);
  fat_slice_mismatch = any fat_arch cputype != that slice header's cputype (unreadable slice header = mismatch).
Not Mach-O (ELF / PE / text / Java class / truncated table) -> "none"."""
import struct

from ..spell import Hex

FIELDS = {
    # macho.* -- cpu_type_set is built-in (D20); slice_count, fat_nfat_arch, nfat_arch, fat_arch_count, arch_count,
    # fat_magic_u32_hex, fat_arch_cputypes, fat_cputypes, is_fat, is_universal live in prebuilt macho.py
    ("macho", "cputype_set"): "set_value",
    ("macho", "cpu_types"): "set_value",
    ("macho", "cputypes"): "set_value",
    ("macho", "cpu_type_set_hex"): "set_value",
    ("macho", "fat_arch_cputype_set"): "set_value",
    ("macho", "cpu_type_list"): "set_value",
    ("macho", "cputype_list"): "set_value",
    ("macho", "fat_arch_cputype_list"): "set_value",
    ("macho", "cpu_subtype_set"): "set_value",
    ("macho", "cpusubtype_set"): "set_value",
    ("macho", "cpu_subtypes"): "set_value",
    ("macho", "cpu_subtype_list"): "set_value",
    ("macho", "cpusubtype_list"): "set_value",
    ("macho", "cpu_subtype_masked_set"): "set_value",
    ("macho", "cpusubtype_masked_set"): "set_value",
    ("macho", "slices_count"): "set_value",
    ("macho", "number_of_slices"): "set_value",
    ("macho", "architecture_count"): "set_value",
    ("macho", "fat_arch_offsets_hex"): "set_value",
    ("macho", "fat_arch_offsets"): "set_value",
    ("macho", "slice_offsets"): "set_value",
    ("macho", "fat_arch_sizes"): "set_value",
    ("macho", "slice_sizes"): "set_value",
    ("macho", "fat_arch_aligns"): "set_value",
    ("macho", "fat_arch_alignments"): "set_value",
    ("macho", "fat_arch_align_exponents"): "set_value",
    ("macho", "slice_header_cputype_set"): "set_value",
    ("macho", "slice_cputype_set"): "set_value",
    ("macho", "slice_header_cputype_list"): "set_value",
    ("macho", "slice_header_cpusubtype_set"): "set_value",
    ("macho", "slice_magics_u32_hex"): "set_value",
    ("macho", "fat_slice_mismatch"): "set_value",
    ("macho", "fat_arch_mismatch"): "set_value",
    ("macho", "slice_header_mismatch"): "set_value",
    ("macho", "mismatched_slice_indexes"): "set_value",
    ("macho", "mismatched_slice_indices"): "set_value",
    ("macho", "filetype_set"): "set_value",
    ("macho", "file_type_set"): "set_value",
    # the same fields under the other format tokens a question could use
    ("mach_o", "cpu_type_set"): "set_value",
    ("mach_o", "cputype_set"): "set_value",
    ("mach_o", "cpu_types"): "set_value",
    ("mach_o", "cputypes"): "set_value",
    ("mach_o", "cpu_type_set_hex"): "set_value",
    ("mach_o", "fat_arch_cputype_set"): "set_value",
    ("mach_o", "cpu_type_list"): "set_value",
    ("mach_o", "cputype_list"): "set_value",
    ("mach_o", "fat_arch_cputype_list"): "set_value",
    ("mach_o", "cpu_subtype_set"): "set_value",
    ("mach_o", "cpusubtype_set"): "set_value",
    ("mach_o", "cpu_subtypes"): "set_value",
    ("mach_o", "cpu_subtype_list"): "set_value",
    ("mach_o", "cpusubtype_list"): "set_value",
    ("mach_o", "cpu_subtype_masked_set"): "set_value",
    ("mach_o", "cpusubtype_masked_set"): "set_value",
    ("mach_o", "slice_count"): "set_value",
    ("mach_o", "slices_count"): "set_value",
    ("mach_o", "number_of_slices"): "set_value",
    ("mach_o", "architecture_count"): "set_value",
    ("mach_o", "arch_count"): "set_value",
    ("mach_o", "fat_nfat_arch"): "set_value",
    ("mach_o", "nfat_arch"): "set_value",
    ("mach_o", "fat_arch_count"): "set_value",
    ("mach_o", "fat_magic_u32_hex"): "set_value",
    ("mach_o", "fat_arch_cputypes"): "set_value",
    ("mach_o", "fat_cputypes"): "set_value",
    ("mach_o", "fat_arch_offsets_hex"): "set_value",
    ("mach_o", "fat_arch_offsets"): "set_value",
    ("mach_o", "slice_offsets"): "set_value",
    ("mach_o", "fat_arch_sizes"): "set_value",
    ("mach_o", "slice_sizes"): "set_value",
    ("mach_o", "fat_arch_aligns"): "set_value",
    ("mach_o", "fat_arch_alignments"): "set_value",
    ("mach_o", "fat_arch_align_exponents"): "set_value",
    ("mach_o", "slice_header_cputype_set"): "set_value",
    ("mach_o", "slice_cputype_set"): "set_value",
    ("mach_o", "slice_header_cputype_list"): "set_value",
    ("mach_o", "slice_header_cpusubtype_set"): "set_value",
    ("mach_o", "slice_magics_u32_hex"): "set_value",
    ("mach_o", "fat_slice_mismatch"): "set_value",
    ("mach_o", "fat_arch_mismatch"): "set_value",
    ("mach_o", "slice_header_mismatch"): "set_value",
    ("mach_o", "mismatched_slice_indexes"): "set_value",
    ("mach_o", "mismatched_slice_indices"): "set_value",
    ("mach_o", "filetype_set"): "set_value",
    ("mach_o", "file_type_set"): "set_value",
    ("mach_o", "is_universal"): "set_value",
    ("mach_o", "is_fat"): "set_value",
    ("universal", "cpu_type_set"): "set_value",
    ("universal", "cputype_set"): "set_value",
    ("universal", "cpu_types"): "set_value",
    ("universal", "cputypes"): "set_value",
    ("universal", "cpu_type_set_hex"): "set_value",
    ("universal", "fat_arch_cputype_set"): "set_value",
    ("universal", "cpu_type_list"): "set_value",
    ("universal", "cputype_list"): "set_value",
    ("universal", "fat_arch_cputype_list"): "set_value",
    ("universal", "cpu_subtype_set"): "set_value",
    ("universal", "cpusubtype_set"): "set_value",
    ("universal", "cpu_subtypes"): "set_value",
    ("universal", "cpu_subtype_list"): "set_value",
    ("universal", "cpusubtype_list"): "set_value",
    ("universal", "cpu_subtype_masked_set"): "set_value",
    ("universal", "cpusubtype_masked_set"): "set_value",
    ("universal", "slice_count"): "set_value",
    ("universal", "slices_count"): "set_value",
    ("universal", "number_of_slices"): "set_value",
    ("universal", "architecture_count"): "set_value",
    ("universal", "arch_count"): "set_value",
    ("universal", "fat_nfat_arch"): "set_value",
    ("universal", "nfat_arch"): "set_value",
    ("universal", "fat_arch_count"): "set_value",
    ("universal", "fat_magic_u32_hex"): "set_value",
    ("universal", "fat_arch_cputypes"): "set_value",
    ("universal", "fat_cputypes"): "set_value",
    ("universal", "fat_arch_offsets_hex"): "set_value",
    ("universal", "fat_arch_offsets"): "set_value",
    ("universal", "slice_offsets"): "set_value",
    ("universal", "fat_arch_sizes"): "set_value",
    ("universal", "slice_sizes"): "set_value",
    ("universal", "fat_arch_aligns"): "set_value",
    ("universal", "fat_arch_alignments"): "set_value",
    ("universal", "fat_arch_align_exponents"): "set_value",
    ("universal", "slice_header_cputype_set"): "set_value",
    ("universal", "slice_cputype_set"): "set_value",
    ("universal", "slice_header_cputype_list"): "set_value",
    ("universal", "slice_header_cpusubtype_set"): "set_value",
    ("universal", "slice_magics_u32_hex"): "set_value",
    ("universal", "fat_slice_mismatch"): "set_value",
    ("universal", "fat_arch_mismatch"): "set_value",
    ("universal", "slice_header_mismatch"): "set_value",
    ("universal", "mismatched_slice_indexes"): "set_value",
    ("universal", "mismatched_slice_indices"): "set_value",
    ("universal", "filetype_set"): "set_value",
    ("universal", "file_type_set"): "set_value",
    ("universal", "is_universal"): "set_value",
    ("universal", "is_fat"): "set_value",
    ("macos", "cpu_type_set"): "set_value",
    ("macos", "cputype_set"): "set_value",
    ("macos", "cpu_types"): "set_value",
    ("macos", "cpu_type_list"): "set_value",
    ("macos", "cpu_subtype_set"): "set_value",
    ("macos", "cpu_subtype_masked_set"): "set_value",
    ("macos", "slice_count"): "set_value",
    ("macos", "fat_nfat_arch"): "set_value",
    ("macos", "fat_magic_u32_hex"): "set_value",
    ("macos", "fat_arch_offsets_hex"): "set_value",
    ("macos", "fat_arch_sizes"): "set_value",
    ("macos", "fat_arch_aligns"): "set_value",
    ("macos", "slice_header_cputype_set"): "set_value",
    ("macos", "fat_slice_mismatch"): "set_value",
    ("macos", "mismatched_slice_indexes"): "set_value",
    ("macos", "filetype_set"): "set_value",
    ("macos", "is_universal"): "set_value",
}

# mach_header magic bytes as stored -> struct byte order of the rest of the header
_THIN = {b"\xcf\xfa\xed\xfe": "<", b"\xce\xfa\xed\xfe": "<", b"\xfe\xed\xfa\xcf": ">", b"\xfe\xed\xfa\xce": ">"}


def _header(b, off):
    """(magic, cputype, cpusubtype, filetype) of the mach_header at `off` in its own byte order, or None."""
    if off < 0 or off + 16 > len(b):
        return None
    e = _THIN.get(bytes(b[off:off + 4]))
    if e is None:
        return None
    return struct.unpack_from(e + "4I", b, off)


def _fat(b):
    """(magic, [{cpu, sub, off, size, align}]) of a fat header, None when not fat; Java .class (nfat >= 45) = None."""
    if len(b) < 8:
        return None
    magic, n = struct.unpack_from(">II", b, 0)
    if magic not in (0xcafebabe, 0xcafebabf) or not 0 < n < 45:
        return None
    w = 20 if magic == 0xcafebabe else 32
    if 8 + n * w > len(b):
        return None
    arcs = []
    for i in range(n):
        o = 8 + i * w
        if magic == 0xcafebabe:
            cpu, sub, off, size, align = struct.unpack_from(">5I", b, o)
        else:
            cpu, sub, off, size, align = struct.unpack_from(">IIQQI", b, o)
        arcs.append({"cpu": cpu, "sub": sub, "off": off, "size": size, "align": align})
    return magic, arcs


def _dedupe(xs):
    out = []
    for x in xs:
        if x not in out:
            out.append(x)
    return out


def _h(v):
    return "0x%08x" % v


def set_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(bytes(data), (ctx or {}).get("field") or "")
    except Exception:
        return None


def _value(b, f):
    fat = _fat(b)
    if fat is not None:
        magic, arcs = fat
        hdrs = [_header(b, a["off"]) for a in arcs]
        if not any(hdrs):
            return "none"           # cafebabe with nothing Mach-O behind it
        cpus, subs = [a["cpu"] for a in arcs], [a["sub"] for a in arcs]
    else:
        h = _header(b, 0)
        if h is None:
            return "none"
        magic, arcs, hdrs = None, None, [h]
        cpus, subs = [h[1]], [h[2]]
    good = [h for h in hdrs if h]

    if f in ("is_universal", "is_fat"):
        return fat is not None
    if f in ("slice_count", "slices_count", "number_of_slices", "architecture_count", "arch_count"):
        return len(cpus)
    if f in ("cpu_type_list", "cputype_list", "fat_arch_cputype_list"):
        return [_h(c) for c in cpus]
    if f in ("cpu_subtype_list", "cpusubtype_list"):
        return [_h(s) for s in subs]
    if "subtype" in f and "masked" in f:
        return _dedupe([_h(s & 0x00ffffff) for s in subs])
    if f == "slice_header_cpusubtype_set":
        return _dedupe([_h(h[2]) for h in good])
    if f in ("cpu_subtype_set", "cpusubtype_set", "cpu_subtypes"):
        return _dedupe([_h(s) for s in subs])
    if f in ("slice_header_cputype_set", "slice_cputype_set"):
        return _dedupe([_h(h[1]) for h in good])
    if f == "slice_header_cputype_list":
        return [_h(h[1]) for h in good]
    if f == "slice_magics_u32_hex":
        return [_h(h[0]) for h in good]
    if f in ("filetype_set", "file_type_set"):
        return _dedupe([_h(h[3]) for h in good])
    if f in ("fat_slice_mismatch", "fat_arch_mismatch", "slice_header_mismatch",
             "mismatched_slice_indexes", "mismatched_slice_indices"):
        bad = [i for i, (c, h) in enumerate(zip(cpus, hdrs)) if h is None or h[1] != c] if fat is not None else []
        return bool(bad) if f.endswith("mismatch") else bad
    if f in ("cpu_type_set", "cputype_set", "cpu_types", "cputypes", "cpu_type_set_hex", "fat_arch_cputype_set"):
        return _dedupe([_h(c) for c in cpus])
    # fat-table-only fields: absent on a thin file
    if fat is None:
        return "none"
    if f in ("fat_nfat_arch", "nfat_arch", "fat_arch_count"):
        return len(arcs)
    if f == "fat_magic_u32_hex":
        return Hex(magic, 8)
    if f in ("fat_arch_cputypes", "fat_cputypes"):
        return [_h(c) for c in cpus]
    if f == "fat_arch_offsets_hex":
        width = 8 if magic == 0xcafebabe else 16
        return ["0x%0*x" % (width, a["off"]) for a in arcs]
    if f in ("fat_arch_offsets", "slice_offsets"):
        return [a["off"] for a in arcs]
    if f in ("fat_arch_sizes", "slice_sizes"):
        return [a["size"] for a in arcs]
    if f in ("fat_arch_aligns", "fat_arch_alignments"):
        return [1 << a["align"] if a["align"] < 64 else a["align"] for a in arcs]
    if f == "fat_arch_align_exponents":
        return [a["align"] for a in arcs]
    return None
