"""Mach-O / PE architecture NAME vocabulary (prebuilt, SPECULATIVE). Only for fields that explicitly ask for a NAME /
constant: D20 proved the GM answers a bare cpu-type question in hex (macho.cpu_type_set ["0x0100000c"]; the name list
["arm64"] was REJECTED there), so nothing here is registered under a `_hex` / `_set` field the built-ins own.

Mach-O (<mach/machine.h>, <mach-o/loader.h>; fat header always big-endian, see lib/meta/macho.py):
  arch_names / arch_name_set / architectures / archs = lipo/`file` arch names of every slice, fat_arch order (thin =
    its header, one element), compact JSON list. *_set drops duplicates keeping the first; the others keep them.
    Vocabulary = llvm-lipo -archs: 7 i386; 0x01000007 x86_64 (subtype 8 x86_64h); 12 arm (5 armv4t, 6 armv6, 7 armv5,
    8 xscale, 9 armv7, 10 armv7f, 11 armv7s, 12 armv7k, 13 armv8, 14 armv6m, 15 armv7m, 16 armv7em); 0x0100000c
    arm64 (2 arm64e); 0x0200000c arm64_32; 18 ppc; 0x01000012 ppc64. The subtype is masked with 0x00ffffff
    (arm64e's ptrauth capability bits 0x80000002 still -> arm64e). Unknown cputype -> "0x%08x".
  arch_name / architecture / arch (singular) = the thin file's name; a fat file -> the list.
  cputype_constant_name = CPU_TYPE_* (7 = CPU_TYPE_X86, the <mach/machine.h> primary name; CPU_TYPE_I386 is its alias).
  filetype_name = MH_* constant (MH_OBJECT/MH_EXECUTE/MH_DYLIB/...), first slice for a fat file.
  platform_name = LC_BUILD_VERSION platform lowercased (1 macos, 2 ios, 3 tvos, 4 watchos, 5 bridgeos, 6 maccatalyst,
    7 iossimulator, 8 tvossimulator, 9 watchossimulator, 10 driverkit, 11 visionos, 12 visionossimulator), else the
    first LC_VERSION_MIN_* (macos/ios/tvos/watchos); none -> "none". platform_constant = PLATFORM_<UPPER>.
PE (COFF FileHeader.Machine u16 @ e_lfanew+4): coff_machine_name = the short dumpbin/VS platform name (x86, x64,
  ARM, ARMNT, ARM64, ARM64EC, IA64, ...); coff_machine_constant = IMAGE_FILE_MACHINE_* (winnt.h / pefile spelling).
Not the format (wrong magic / truncated) -> "none"."""
import struct

FIELDS = {
    ("macho", "arch_names"): "macho_arch_value",
    ("macho", "arch_name_set"): "macho_arch_value",
    ("macho", "arch_name_list"): "macho_arch_value",
    ("macho", "arch_set"): "macho_arch_value",
    ("macho", "arch_list"): "macho_arch_value",
    ("macho", "archs"): "macho_arch_value",
    ("macho", "architectures"): "macho_arch_value",
    ("macho", "architecture_names"): "macho_arch_value",
    ("macho", "architecture_set"): "macho_arch_value",
    ("macho", "architecture_list"): "macho_arch_value",
    ("macho", "slice_arch_names"): "macho_arch_value",
    ("macho", "fat_arch_names"): "macho_arch_value",
    ("macho", "lipo_archs"): "macho_arch_value",
    ("macho", "cpu_type_names"): "macho_arch_value",
    ("macho", "cputype_names"): "macho_arch_value",
    ("macho", "cpu_type_name_set"): "macho_arch_value",
    ("macho", "cputype_name_set"): "macho_arch_value",
    ("macho", "arch_name"): "macho_arch_value",
    ("macho", "arch"): "macho_arch_value",
    ("macho", "architecture"): "macho_arch_value",
    ("macho", "architecture_name"): "macho_arch_value",
    ("macho", "cpu_type_name"): "macho_arch_value",
    ("macho", "cputype_name"): "macho_arch_value",
    ("macho", "cputype_constant_name"): "macho_arch_value",
    ("macho", "cputype_constant"): "macho_arch_value",
    ("macho", "cpu_type_constant"): "macho_arch_value",
    ("macho", "cpu_type_constant_name"): "macho_arch_value",
    ("macho", "cputype_constant_names"): "macho_arch_value",
    ("macho", "cpu_type_constant_names"): "macho_arch_value",
    ("macho", "filetype_name"): "macho_arch_value",
    ("macho", "file_type_name"): "macho_arch_value",
    ("macho", "filetype_constant"): "macho_arch_value",
    ("macho", "file_type_constant"): "macho_arch_value",
    ("macho", "filetype_constant_name"): "macho_arch_value",
    ("macho", "platform_name"): "macho_arch_value",
    ("macho", "build_version_platform_name"): "macho_arch_value",
    ("macho", "platform_constant"): "macho_arch_value",
    ("macho", "build_version_platform_constant"): "macho_arch_value",
    # the same under the other format tokens a question could use
    ("mach_o", "arch_names"): "macho_arch_value",
    ("mach_o", "arch_name_set"): "macho_arch_value",
    ("mach_o", "archs"): "macho_arch_value",
    ("mach_o", "architectures"): "macho_arch_value",
    ("mach_o", "arch_name"): "macho_arch_value",
    ("mach_o", "architecture"): "macho_arch_value",
    ("mach_o", "cputype_constant_name"): "macho_arch_value",
    ("mach_o", "filetype_name"): "macho_arch_value",
    ("mach_o", "platform_name"): "macho_arch_value",
    ("universal", "arch_names"): "macho_arch_value",
    ("universal", "arch_name_set"): "macho_arch_value",
    ("universal", "archs"): "macho_arch_value",
    ("universal", "architectures"): "macho_arch_value",
    ("macos", "arch_names"): "macho_arch_value",
    ("macos", "arch_name_set"): "macho_arch_value",
    ("macos", "archs"): "macho_arch_value",
    ("macos", "architectures"): "macho_arch_value",
    # PE COFF machine
    ("pe", "coff_machine_name"): "pe_machine_value",
    ("pe", "machine_name"): "pe_machine_value",
    ("pe", "file_header_machine_name"): "pe_machine_value",
    ("pe", "arch"): "pe_machine_value",
    ("pe", "arch_name"): "pe_machine_value",
    ("pe", "architecture"): "pe_machine_value",
    ("pe", "coff_machine_constant"): "pe_machine_value",
    ("pe", "coff_machine_constant_name"): "pe_machine_value",
    ("pe", "machine_constant"): "pe_machine_value",
    ("pe", "file_header_machine_constant"): "pe_machine_value",
}

_THIN = {b"\xce\xfa\xed\xfe": "<", b"\xcf\xfa\xed\xfe": "<", b"\xfe\xed\xfa\xce": ">", b"\xfe\xed\xfa\xcf": ">"}
_ARM = {5: "armv4t", 6: "armv6", 7: "armv5", 8: "xscale", 9: "armv7", 10: "armv7f", 11: "armv7s", 12: "armv7k",
        13: "armv8", 14: "armv6m", 15: "armv7m", 16: "armv7em"}
_CPU_NAME = {7: "i386", 0x01000007: "x86_64", 12: "arm", 0x0100000c: "arm64", 0x0200000c: "arm64_32", 18: "ppc",
             0x01000012: "ppc64", 6: "m68k", 10: "m88k", 11: "hppa", 14: "sparc", 15: "i860", 1: "vax"}
_CPU_CONST = {1: "CPU_TYPE_VAX", 6: "CPU_TYPE_MC680x0", 7: "CPU_TYPE_X86", 0x01000007: "CPU_TYPE_X86_64",
              10: "CPU_TYPE_MC98000", 11: "CPU_TYPE_HPPA", 12: "CPU_TYPE_ARM", 0x0100000c: "CPU_TYPE_ARM64",
              0x0200000c: "CPU_TYPE_ARM64_32", 13: "CPU_TYPE_MC88000", 14: "CPU_TYPE_SPARC", 15: "CPU_TYPE_I860",
              18: "CPU_TYPE_POWERPC", 0x01000012: "CPU_TYPE_POWERPC64"}
_FILETYPE = {1: "MH_OBJECT", 2: "MH_EXECUTE", 3: "MH_FVMLIB", 4: "MH_CORE", 5: "MH_PRELOAD", 6: "MH_DYLIB",
             7: "MH_DYLINKER", 8: "MH_BUNDLE", 9: "MH_DYLIB_STUB", 10: "MH_DSYM", 11: "MH_KEXT_BUNDLE",
             12: "MH_FILESET", 13: "MH_GPU_EXECUTE", 14: "MH_GPU_DYLIB"}
_PLATFORM = {1: "macos", 2: "ios", 3: "tvos", 4: "watchos", 5: "bridgeos", 6: "maccatalyst", 7: "iossimulator",
             8: "tvossimulator", 9: "watchossimulator", 10: "driverkit", 11: "visionos", 12: "visionossimulator"}
_VMIN = {0x24: 1, 0x25: 2, 0x2f: 3, 0x30: 4}


def arch_name(cpu, sub):
    """llvm-lipo / `file` arch name of (cputype, cpusubtype)."""
    s = sub & 0x00ffffff
    if cpu == 0x01000007 and s == 8:
        return "x86_64h"
    if cpu == 0x0100000c and s == 2:
        return "arm64e"
    if cpu == 12 and s in _ARM:
        return _ARM[s]
    return _CPU_NAME.get(cpu, "0x%08x" % cpu)


def _header(b, off=0):
    """(endian, cputype, cpusubtype, filetype, ncmds, header size) of a thin mach_header at off, or None."""
    e = _THIN.get(bytes(b[off:off + 4]))
    if e is None or off + 28 > len(b):
        return None
    cpu, sub, ft, ncmds = struct.unpack_from(e + "IIII", b, off + 4)
    return e, cpu, sub, ft, ncmds, 32 if bytes(b[off:off + 4]) in (b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf") else 28


def _slices(b):
    """[(cputype, cpusubtype, slice offset or None)] in fat_arch order (thin = [its header]), or None."""
    if len(b) >= 8 and b[:4] in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
        n = struct.unpack_from(">I", b, 4)[0]
        is64 = b[3] == 0xbf
        w = 32 if is64 else 20
        if not 0 < n < 20 or 8 + n * w > len(b):
            return None
        out = []
        for i in range(n):
            o = 8 + i * w
            cpu, sub = struct.unpack_from(">II", b, o)
            off = struct.unpack_from(">Q" if is64 else ">I", b, o + 8)[0]
            out.append((cpu, sub, off))
        return out
    h = _header(b)
    return [(h[1], h[2], 0)] if h else None


def _first_header(b, sl):
    for _, _, off in sl:
        h = _header(b, off) if off is not None else None
        if h:
            return off, h
    return None


def _platform(b, off, h):
    e, _, _, _, ncmds, hs = h
    p = off + hs
    vmin = None
    for _ in range(min(ncmds, 512)):
        if p + 8 > len(b):
            break
        cmd, size = struct.unpack_from(e + "II", b, p)
        if size < 8:
            break
        if cmd == 0x32 and p + 12 <= len(b):        # LC_BUILD_VERSION: cmd, cmdsize, platform, minos, sdk, ntools
            return struct.unpack_from(e + "I", b, p + 8)[0]
        if cmd in _VMIN and vmin is None:
            vmin = _VMIN[cmd]
        p += size
    return vmin


def _dedupe(xs):
    out = []
    for x in xs:
        if x not in out:
            out.append(x)
    return out


def macho_arch_value(data, ctx):
    if data is None:
        return None
    try:
        b = bytes(data)
        f = ctx.get("field") or ""
        sl = _slices(b)
        if not sl:
            return "none"
        if "filetype" in f or "file_type" in f or "platform" in f:
            fh = _first_header(b, sl)
            if fh is None:
                return "none"
            off, h = fh
            if "platform" in f:
                pl = _platform(b, off, h)
                if pl is None:
                    return "none"
                name = _PLATFORM.get(pl, str(pl))
                return "PLATFORM_" + name.upper() if "constant" in f else name
            return _FILETYPE.get(h[3], "0x%08x" % h[3])
        if "constant" in f:
            vals = [_CPU_CONST.get(c, "0x%08x" % c) for c, _, _ in sl]
            if f.endswith("_names"):
                return vals
            return vals[0] if len(vals) == 1 else vals
        vals = [arch_name(c, s) for c, s, _ in sl]
        if f.endswith("_set"):
            return _dedupe(vals)
        if f in ("arch_name", "arch", "architecture", "architecture_name", "cpu_type_name", "cputype_name"):
            return vals[0] if len(vals) == 1 else vals
        return vals
    except Exception:
        return None


_PE_MACHINE = {
    0x014c: ("x86", "IMAGE_FILE_MACHINE_I386"), 0x8664: ("x64", "IMAGE_FILE_MACHINE_AMD64"),
    0xaa64: ("ARM64", "IMAGE_FILE_MACHINE_ARM64"), 0x01c0: ("ARM", "IMAGE_FILE_MACHINE_ARM"),
    0x01c2: ("THUMB", "IMAGE_FILE_MACHINE_THUMB"), 0x01c4: ("ARMNT", "IMAGE_FILE_MACHINE_ARMNT"),
    0xa641: ("ARM64EC", "IMAGE_FILE_MACHINE_ARM64EC"), 0xa64e: ("ARM64X", "IMAGE_FILE_MACHINE_ARM64X"),
    0x0200: ("IA64", "IMAGE_FILE_MACHINE_IA64"), 0x5032: ("RISCV32", "IMAGE_FILE_MACHINE_RISCV32"),
    0x5064: ("RISCV64", "IMAGE_FILE_MACHINE_RISCV64"), 0x5128: ("RISCV128", "IMAGE_FILE_MACHINE_RISCV128"),
    0x6232: ("LOONGARCH32", "IMAGE_FILE_MACHINE_LOONGARCH32"),
    0x6264: ("LOONGARCH64", "IMAGE_FILE_MACHINE_LOONGARCH64"), 0x0ebc: ("EBC", "IMAGE_FILE_MACHINE_EBC"),
    0x0166: ("MIPS", "IMAGE_FILE_MACHINE_R4000"), 0x01f0: ("PPC", "IMAGE_FILE_MACHINE_POWERPC"),
    0x01f1: ("PPCFP", "IMAGE_FILE_MACHINE_POWERPCFP"), 0x01a2: ("SH3", "IMAGE_FILE_MACHINE_SH3"),
    0x01a6: ("SH4", "IMAGE_FILE_MACHINE_SH4"), 0x0184: ("ALPHA", "IMAGE_FILE_MACHINE_ALPHA"),
    0x0000: ("UNKNOWN", "IMAGE_FILE_MACHINE_UNKNOWN"),
}


def pe_machine_value(data, ctx):
    if data is None:
        return None
    try:
        b = bytes(data[:4096])
        if len(b) < 0x40 or b[:2] != b"MZ":
            return "none"
        lfanew = struct.unpack_from("<I", b, 0x3c)[0]
        if lfanew + 6 > len(data) or bytes(data[lfanew:lfanew + 4]) != b"PE\0\0":
            return "none"
        m = struct.unpack_from("<H", bytes(data[lfanew + 4:lfanew + 6]))[0]
        ent = _PE_MACHINE.get(m)
        f = ctx.get("field") or ""
        if ent is None:
            return "0x%04x" % m
        return ent[1] if "constant" in f else ent[0]
    except Exception:
        return None
