"""Mach-O header / LC_UUID / LC_BUILD_VERSION / LC_VERSION_MIN_* fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Thin file (<mach-o/loader.h>): magic u32 (MH_MAGIC 0xfeedface / MH_MAGIC_64 0xfeedfacf; the byte-swapped MH_CIGAM*
forms = a big-endian file), cputype u32, cpusubtype u32, filetype u32, ncmds u32, sizeofcmds u32, flags u32
(+ reserved u32 on 64-bit) -> load commands {cmd u32, cmdsize u32, ...}. Header values are reported as stored, in the
file's byte order (cputype ARM64 = 0x0100000c, x86_64 = 0x01000007; otool -h prints them in decimal).
Fat file (<mach-o/fat.h>, ALWAYS big-endian): FAT_MAGIC 0xcafebabe (fat_arch 20 bytes) / FAT_MAGIC_64 0xcafebabf
(fat_arch_64 32 bytes), nfat_arch u32. 0xcafebabe is also the Java .class magic: like `file`, require
nfat_arch < 20 and a slice offset that lands on a Mach-O magic, else "not Mach-O". The thin-header fields of a fat
file answer from the FIRST slice (otool -h / `file` order); fat_nfat_arch / fat_arch_cputypes describe the wrapper.
uuid = LC_UUID (0x1b) 16 raw bytes as canonical 8-4-4-4-12 text, lowercase (Python uuid style) unless the
answer_format asks for upper case (otool/dwarfdump print UPPERCASE; spell.alternates covers the case flip).
min_os_version = LC_BUILD_VERSION (0x32) minos, else LC_VERSION_MIN_MACOSX/IPHONEOS/TVOS/WATCHOS (0x24/0x25/0x2f/
0x30) version; nibble-encoded xxxx.yy.zz. Rendered like otool -l ("13.2.1", "10.13": patch dropped when 0) unless
the answer_format's syntax names a three-part X.Y.Z / patch form (then always 3 parts) -- GM spelling unverified.
Not Mach-O / truncated -> "none"; a load command the file lacks (no LC_UUID in an MH_OBJECT) -> "none"."""
import struct
import uuid

from ..spell import Guid, Hex

FIELDS = {
    ("macho", "magic_u32_hex"): "macho_value",
    ("macho", "mach_header_magic_u32_hex"): "macho_value",
    ("macho", "cputype_u32_hex"): "macho_value",
    ("macho", "cpu_type_u32_hex"): "macho_value",
    ("macho", "mach_header_cputype_u32_hex"): "macho_value",
    ("macho", "header_cputype_u32_hex"): "macho_value",
    ("macho", "cpusubtype_u32_hex"): "macho_value",
    ("macho", "cpu_subtype_u32_hex"): "macho_value",
    ("macho", "mach_header_cpusubtype_u32_hex"): "macho_value",
    ("macho", "filetype_u32_hex"): "macho_value",
    ("macho", "file_type_u32_hex"): "macho_value",
    ("macho", "mach_header_filetype_u32_hex"): "macho_value",
    ("macho", "header_filetype_u32_hex"): "macho_value",
    ("macho", "ncmds"): "macho_value",
    ("macho", "mach_header_ncmds"): "macho_value",
    ("macho", "header_ncmds"): "macho_value",
    ("macho", "load_command_count"): "macho_value",
    ("macho", "number_of_load_commands"): "macho_value",
    ("macho", "num_load_commands"): "macho_value",
    ("macho", "sizeofcmds"): "macho_value",
    ("macho", "mach_header_sizeofcmds"): "macho_value",
    ("macho", "size_of_cmds"): "macho_value",
    ("macho", "flags_u32_hex"): "macho_value",
    ("macho", "mach_header_flags_u32_hex"): "macho_value",
    ("macho", "header_flags_u32_hex"): "macho_value",
    ("macho", "uuid"): "macho_value",
    ("macho", "lc_uuid"): "macho_value",
    ("macho", "uuid_guid"): "macho_value",
    ("macho", "lc_uuid_guid"): "macho_value",
    ("macho", "lc_uuid_uuid"): "macho_value",
    ("macho", "min_os_version"): "macho_value",
    ("macho", "minos"): "macho_value",
    ("macho", "minos_version"): "macho_value",
    ("macho", "minimum_os_version"): "macho_value",
    ("macho", "build_version_minos"): "macho_value",
    ("macho", "lc_build_version_minos"): "macho_value",
    ("macho", "version_min"): "macho_value",
    ("macho", "version_min_version"): "macho_value",
    ("macho", "deployment_target"): "macho_value",
    ("macho", "sdk_version"): "macho_value",
    ("macho", "build_version_sdk"): "macho_value",
    ("macho", "lc_build_version_sdk"): "macho_value",
    ("macho", "build_version_platform"): "macho_value",
    ("macho", "platform"): "macho_value",
    ("macho", "fat_nfat_arch"): "macho_value",
    ("macho", "nfat_arch"): "macho_value",
    ("macho", "fat_arch_count"): "macho_value",
    ("macho", "arch_count"): "macho_value",
    ("macho", "slice_count"): "macho_value",
    ("macho", "fat_magic_u32_hex"): "macho_value",
    ("macho", "fat_arch_cputypes"): "macho_value",
    ("macho", "fat_cputypes"): "macho_value",
    ("macho", "is_fat"): "macho_value",
    ("macho", "is_universal"): "macho_value",
    ("macho", "load_command_names"): "macho_value",
    ("macho", "load_commands"): "macho_value",
}

_THIN = {0xfeedface: ("<", False), 0xfeedfacf: ("<", True), 0xcefaedfe: (">", False), 0xcffaedfe: (">", True)}
_LC = {0x1: "LC_SEGMENT", 0x2: "LC_SYMTAB", 0xb: "LC_DYSYMTAB", 0xc: "LC_LOAD_DYLIB", 0xd: "LC_ID_DYLIB",
       0xe: "LC_LOAD_DYLINKER", 0x19: "LC_SEGMENT_64", 0x1b: "LC_UUID", 0x1d: "LC_CODE_SIGNATURE",
       0x1e: "LC_SEGMENT_SPLIT_INFO", 0x21: "LC_ENCRYPTION_INFO", 0x22: "LC_DYLD_INFO", 0x80000022: "LC_DYLD_INFO_ONLY",
       0x24: "LC_VERSION_MIN_MACOSX", 0x25: "LC_VERSION_MIN_IPHONEOS", 0x26: "LC_FUNCTION_STARTS",
       0x29: "LC_DATA_IN_CODE", 0x2a: "LC_SOURCE_VERSION", 0x2b: "LC_DYLIB_CODE_SIGN_DRS", 0x2c: "LC_ENCRYPTION_INFO_64",
       0x2f: "LC_VERSION_MIN_TVOS", 0x30: "LC_VERSION_MIN_WATCHOS", 0x31: "LC_NOTE", 0x32: "LC_BUILD_VERSION",
       0x80000033: "LC_DYLD_EXPORTS_TRIE", 0x80000034: "LC_DYLD_CHAINED_FIXUPS", 0x80000028: "LC_MAIN",
       0x8000001c: "LC_RPATH", 0x80000018: "LC_LOAD_WEAK_DYLIB", 0x8000001f: "LC_REEXPORT_DYLIB"}
_PLATFORM = {1: "MACOS", 2: "IOS", 3: "TVOS", 4: "WATCHOS", 5: "BRIDGEOS", 6: "MACCATALYST", 7: "IOSSIMULATOR",
             8: "TVOSSIMULATOR", 9: "WATCHOSSIMULATOR", 10: "DRIVERKIT", 11: "VISIONOS", 12: "VISIONOSSIMULATOR"}
_VMIN_PLATFORM = {0x24: 1, 0x25: 2, 0x2f: 3, 0x30: 4}


def _thin(b, base=0):
    """The parsed thin header at `base`, or None."""
    if base + 28 > len(b):
        return None
    magic, = struct.unpack_from("<I", b, base)
    if magic not in _THIN:
        return None
    e, is64 = _THIN[magic]
    cpu, sub, ft, ncmds, sz, flags = struct.unpack_from(e + "6I", b, base + 4)
    off, end = base + (32 if is64 else 28), len(b)
    cmds = []
    for _ in range(min(ncmds, 4096)):
        if off + 8 > end:
            break
        cmd, csz = struct.unpack_from(e + "II", b, off)
        cmds.append((cmd, bytes(b[off:off + max(csz, 8)])))
        if csz < 8:
            break
        off += csz
    return {"e": e, "magic": struct.unpack_from(e + "I", b, base)[0], "cpu": cpu, "sub": sub, "filetype": ft,
            "ncmds": ncmds, "sizeofcmds": sz, "flags": flags, "cmds": cmds}


def _fat(b):
    """[(cputype, offset, size)] of a fat file, or None (Java .class shares 0xcafebabe -- slices must be Mach-O)."""
    if len(b) < 8:
        return None
    magic, n = struct.unpack_from(">II", b, 0)
    if magic not in (0xcafebabe, 0xcafebabf) or not 0 < n < 20:
        return None
    w, out = (20 if magic == 0xcafebabe else 32), []
    for i in range(n):
        o = 8 + i * w
        if o + w > len(b):
            return None
        if magic == 0xcafebabe:
            cpu, _, off, size = struct.unpack_from(">4I", b, o)
        else:
            cpu, _, off, size = struct.unpack_from(">IIQQ", b, o)
        out.append((cpu, off, size))
    if not any(_thin(b, off) for _, off, _ in out):
        return None
    return out


def _syntax(ctx):
    fmt = ((ctx or {}).get("question") or {}).get("answer_format") or {}
    return " ".join(str(v) for v in fmt.values() if isinstance(v, str)).lower()


def _ver(v, ctx):
    major, minor, patch = v >> 16, (v >> 8) & 0xff, v & 0xff
    syn = _syntax(ctx)
    if patch or "x.y.z" in syn or "patch" in syn or "three" in syn or "major.minor.p" in syn:
        return "%d.%d.%d" % (major, minor, patch)
    return "%d.%d" % (major, minor)


def _version_cmd(h):
    """(platform, minos, sdk) from LC_BUILD_VERSION, else the first LC_VERSION_MIN_*, else None."""
    for cmd, body in h["cmds"]:
        if cmd == 0x32 and len(body) >= 20:
            return struct.unpack_from(h["e"] + "3I", body, 8)
    for cmd, body in h["cmds"]:
        if cmd in _VMIN_PLATFORM and len(body) >= 16:
            v, sdk = struct.unpack_from(h["e"] + "II", body, 8)
            return _VMIN_PLATFORM[cmd], v, sdk
    return None


def macho_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(bytes(data), ctx)
    except Exception:
        return None


def _value(b, ctx):
    f = (ctx or {}).get("field") or ""
    fat = _fat(b)
    if fat is not None:
        if f in ("fat_nfat_arch", "nfat_arch", "fat_arch_count", "arch_count", "slice_count"):
            return len(fat)
        if f == "fat_magic_u32_hex":
            return Hex(struct.unpack_from(">I", b, 0)[0], 8)
        if f in ("fat_arch_cputypes", "fat_cputypes"):
            return ["0x%08x" % c for c, _, _ in fat]
        h = next((x for x in (_thin(b, off) for _, off, _ in fat) if x), None)
    else:
        h = _thin(b)
    if f in ("is_fat", "is_universal"):
        return fat is not None if (fat is not None or h is not None) else "none"
    if h is None:
        return "none"
    if f in ("fat_nfat_arch", "nfat_arch", "fat_arch_count", "arch_count", "slice_count", "fat_magic_u32_hex",
             "fat_arch_cputypes", "fat_cputypes"):
        return "none"
    if f.endswith("magic_u32_hex"):
        return Hex(h["magic"], 8)
    if "cpusubtype" in f or "cpu_subtype" in f:
        return Hex(h["sub"], 8)
    if "cputype" in f or "cpu_type" in f:
        return Hex(h["cpu"], 8)
    if "filetype" in f or "file_type" in f:
        return Hex(h["filetype"], 8)
    if f.endswith("flags_u32_hex"):
        return Hex(h["flags"], 8)
    if "ncmds" in f or f in ("load_command_count", "number_of_load_commands", "num_load_commands"):
        return h["ncmds"]
    if "sizeofcmds" in f or f == "size_of_cmds":
        return h["sizeofcmds"]
    if f in ("load_command_names", "load_commands"):
        return [_LC.get(c, "0x%x" % c) for c, _ in h["cmds"]]
    if "uuid" in f:
        body = next((bd for c, bd in h["cmds"] if c == 0x1b and len(bd) >= 24), None)
        if body is None:
            return "none"
        s = str(uuid.UUID(bytes=body[8:24]))
        return Guid("text", s.upper() if "upper" in _syntax(ctx) else s)
    vc = _version_cmd(h)
    if "sdk" in f:
        return _ver(vc[2], ctx) if vc and vc[2] else "none"
    if "platform" in f:
        return _PLATFORM.get(vc[0], str(vc[0])) if vc else "none"
    if "min" in f or f == "deployment_target":
        return _ver(vc[1], ctx) if vc else "none"
    return None
