"""U-Boot legacy uImage header fields (prebuilt, SPECULATIVE -- never GM-asked yet).

image_header_t (u-boot include/image.h), 64 bytes, all BIG-endian: ih_magic u32 = 0x27051956, ih_hcrc u32 (CRC32 of
the header with ih_hcrc zeroed), ih_time u32 (unix seconds), ih_size u32 (data bytes), ih_load u32, ih_ep u32,
ih_dcrc u32 (CRC32 of the data), ih_os u8, ih_arch u8, ih_type u8, ih_comp u8, ih_name[32] (NUL-trimmed).
hcrc/dcrc/load/entry render `0x` + 8 lowercase digits (u32 struct width); time_utc = ih_time as ISO-8601 UTC
"YYYY-MM-DDTHH:MM:SSZ" (the only epoch in the format; `file` prints the same instant); size = ih_size (int).
os/arch/type/comp names = the mkimage short names from u-boot common/image.c tables (`mkimage -A arm -O linux
-T kernel -C gzip`), remapped onto answer_format.accepted_values when the contract lists another spelling; the
`*_u8_hex` siblings give the raw byte. *_valid fields recompute the CRCs (hcrc over the zeroed header, dcrc over
ih_size data bytes following the header). Wrong magic / short header -> "none".
Fixtures: mkimage 2025.10 (u-boot-tools deb, tools/u-boot-tools) writer; `file` / dumpimage -l readers."""
import datetime
import struct
import zlib

from ..spell import Hex

_OS = {0: "invalid", 1: "openbsd", 2: "netbsd", 3: "freebsd", 4: "4_4bsd", 5: "linux", 6: "svr4", 7: "esix",
       8: "solaris", 9: "irix", 10: "sco", 11: "dell", 12: "ncr", 13: "lynxos", 14: "vxworks", 15: "psos", 16: "qnx",
       17: "u-boot", 18: "rtems", 19: "artos", 20: "unity", 21: "integrity", 22: "ose", 23: "plan9", 24: "openrtos",
       25: "arm-trusted-firmware", 26: "tee", 27: "opensbi", 28: "efi", 29: "elf"}
_ARCH = {0: "invalid", 1: "alpha", 2: "arm", 3: "x86", 4: "ia64", 5: "mips", 6: "mips64", 7: "ppc", 8: "s390",
         9: "sh", 10: "sparc", 11: "sparc64", 12: "m68k", 13: "nios", 14: "microblaze", 15: "nios2", 16: "blackfin",
         17: "avr32", 18: "st200", 19: "sandbox", 20: "nds32", 21: "or1k", 22: "arm64", 23: "arc", 24: "x86_64",
         25: "xtensa", 26: "riscv"}
_TYPE = {0: "invalid", 1: "standalone", 2: "kernel", 3: "ramdisk", 4: "multi", 5: "firmware", 6: "script",
         7: "filesystem", 8: "flat_dt", 9: "kwbimage", 10: "imximage", 11: "ublimage", 12: "omapimage",
         13: "aisimage", 14: "kernel_noload", 15: "pblimage", 16: "mxsimage", 17: "gpimage", 18: "atmelimage",
         19: "socfpgaimage", 20: "x86_setup", 21: "lpc32xximage", 22: "loadables", 23: "rkimage", 24: "rksd",
         25: "rkspi", 26: "zynqimage", 27: "zynqmpimage", 28: "zynqmpbif", 29: "fpga", 30: "vybridimage",
         31: "tee", 32: "firmware_ivt", 33: "pmmc", 34: "stm32image", 35: "socfpgaimage_v1", 36: "mtk_image",
         37: "imx8mimage", 38: "imx8image", 39: "copro", 40: "sunxi_egon", 41: "sunxi_toc0"}
_COMP = {0: "none", 1: "gzip", 2: "bzip2", 3: "lzma", 4: "lzo", 5: "lz4", 6: "zstd"}

FIELDS = {
    ("uimage", "magic_u32_hex"): "uimage_value",
    ("uimage", "ih_magic_u32_hex"): "uimage_value",
    ("uimage", "hcrc_u32_hex"): "uimage_value",
    ("uimage", "ih_hcrc_u32_hex"): "uimage_value",
    ("uimage", "header_crc_u32_hex"): "uimage_value",
    ("uimage", "header_crc32_u32_hex"): "uimage_value",
    ("uimage", "dcrc_u32_hex"): "uimage_value",
    ("uimage", "ih_dcrc_u32_hex"): "uimage_value",
    ("uimage", "data_crc_u32_hex"): "uimage_value",
    ("uimage", "data_crc32_u32_hex"): "uimage_value",
    ("uimage", "hcrc_valid"): "uimage_value",
    ("uimage", "header_crc_valid"): "uimage_value",
    ("uimage", "dcrc_valid"): "uimage_value",
    ("uimage", "data_crc_valid"): "uimage_value",
    ("uimage", "time_utc"): "uimage_value",
    ("uimage", "ih_time_utc"): "uimage_value",
    ("uimage", "timestamp_utc"): "uimage_value",
    ("uimage", "creation_time_utc"): "uimage_value",
    ("uimage", "created_utc"): "uimage_value",
    ("uimage", "time_unix"): "uimage_value",
    ("uimage", "ih_time"): "uimage_value",
    ("uimage", "size"): "uimage_value",
    ("uimage", "ih_size"): "uimage_value",
    ("uimage", "data_size"): "uimage_value",
    ("uimage", "data_size_bytes"): "uimage_value",
    ("uimage", "size_bytes"): "uimage_value",
    ("uimage", "image_size"): "uimage_value",
    ("uimage", "image_data_size"): "uimage_value",
    ("uimage", "load_u32_hex"): "uimage_value",
    ("uimage", "ih_load_u32_hex"): "uimage_value",
    ("uimage", "load_address_u32_hex"): "uimage_value",
    ("uimage", "load_addr_u32_hex"): "uimage_value",
    ("uimage", "entry_u32_hex"): "uimage_value",
    ("uimage", "ih_ep_u32_hex"): "uimage_value",
    ("uimage", "ep_u32_hex"): "uimage_value",
    ("uimage", "entry_point_u32_hex"): "uimage_value",
    ("uimage", "entry_address_u32_hex"): "uimage_value",
    ("uimage", "os"): "uimage_value",
    ("uimage", "os_name"): "uimage_value",
    ("uimage", "ih_os"): "uimage_value",
    ("uimage", "ih_os_name"): "uimage_value",
    ("uimage", "operating_system"): "uimage_value",
    ("uimage", "arch"): "uimage_value",
    ("uimage", "arch_name"): "uimage_value",
    ("uimage", "ih_arch"): "uimage_value",
    ("uimage", "ih_arch_name"): "uimage_value",
    ("uimage", "architecture"): "uimage_value",
    ("uimage", "cpu_architecture"): "uimage_value",
    ("uimage", "type"): "uimage_value",
    ("uimage", "type_name"): "uimage_value",
    ("uimage", "ih_type"): "uimage_value",
    ("uimage", "ih_type_name"): "uimage_value",
    ("uimage", "image_type"): "uimage_value",
    ("uimage", "comp"): "uimage_value",
    ("uimage", "comp_name"): "uimage_value",
    ("uimage", "ih_comp"): "uimage_value",
    ("uimage", "ih_comp_name"): "uimage_value",
    ("uimage", "compression"): "uimage_value",
    ("uimage", "compression_type"): "uimage_value",
    ("uimage", "os_u8_hex"): "uimage_value",
    ("uimage", "ih_os_u8_hex"): "uimage_value",
    ("uimage", "arch_u8_hex"): "uimage_value",
    ("uimage", "ih_arch_u8_hex"): "uimage_value",
    ("uimage", "type_u8_hex"): "uimage_value",
    ("uimage", "ih_type_u8_hex"): "uimage_value",
    ("uimage", "comp_u8_hex"): "uimage_value",
    ("uimage", "ih_comp_u8_hex"): "uimage_value",
    ("uimage", "image_name"): "uimage_value",
    ("uimage", "ih_name"): "uimage_value",
    ("uimage", "name"): "uimage_value",
}

_ALIAS = {"ih_magic": "magic", "header_crc": "hcrc", "header_crc32": "hcrc", "ih_hcrc": "hcrc",
          "data_crc": "dcrc", "data_crc32": "dcrc", "ih_dcrc": "dcrc", "header_crc_valid": "hcrc_valid",
          "data_crc_valid": "dcrc_valid", "ih_time": "time", "timestamp": "time", "creation_time": "time",
          "created": "time", "ih_size": "size", "data_size": "size", "image_size": "size",
          "image_data_size": "size", "ih_load": "load", "load_address": "load", "load_addr": "load",
          "ih_ep": "entry", "ep": "entry", "entry_point": "entry", "entry_address": "entry",
          "ih_os": "os", "operating_system": "os", "ih_arch": "arch", "architecture": "arch",
          "cpu_architecture": "arch", "ih_type": "type", "image_type": "type", "ih_comp": "comp",
          "compression": "comp", "compression_type": "comp", "ih_name": "image_name", "name": "image_name"}


def _enum(v, ctx):
    fmt = ((ctx or {}).get("question") or {}).get("answer_format") or {}
    acc = fmt.get("accepted_values") or fmt.get("values") or []
    if isinstance(acc, (list, tuple)):
        for a in acc:
            if str(a).lower() == v.lower():
                return str(a)
    return v


def _hdr(b):
    if not b or len(b) < 64 or b[:4] != b"\x27\x05\x19\x56":
        return None
    magic, hcrc, t, size, load, ep, dcrc, os_, arch, typ, comp = struct.unpack_from(">7I4B", b, 0)
    name = b[32:64].split(b"\0", 1)[0].decode("latin-1").strip()
    return dict(magic=magic, hcrc=hcrc, time=t, size=size, load=load, entry=ep, dcrc=dcrc, os=os_, arch=arch,
                type=typ, comp=comp, image_name=name)


def uimage_value(data, ctx):
    try:
        return _value(data, ctx)
    except Exception:
        return None


def _value(b, ctx):
    if b is None:
        return None
    h = _hdr(b)
    if h is None:
        return "none"
    f = ctx.get("field") or ""
    suf = ""
    for s in () if f in ("image_name", "ih_name", "name") else ("_u32_hex", "_u8_hex", "_utc", "_unix", "_bytes", "_name"):
        if f.endswith(s):
            f, suf = f[:-len(s)], s
            break
    f = _ALIAS.get(f, f)
    if f == "hcrc_valid":
        z = bytearray(b[:64])
        z[4:8] = b"\0\0\0\0"
        return (zlib.crc32(bytes(z)) & 0xFFFFFFFF) == h["hcrc"]
    if f == "dcrc_valid":
        d = b[64:64 + h["size"]]
        return len(d) == h["size"] and (zlib.crc32(d) & 0xFFFFFFFF) == h["dcrc"]
    if f not in h:
        return None
    v = h[f]
    if f in ("os", "arch", "type", "comp"):
        if suf == "_u8_hex":
            return Hex(v, 2)
        tbl = {"os": _OS, "arch": _ARCH, "type": _TYPE, "comp": _COMP}[f]
        return _enum(tbl[v], ctx) if v in tbl else None
    if f == "time":
        if suf != "_utc":
            return v                                   # ih_time / time_unix: the raw unix seconds
        return datetime.datetime.fromtimestamp(v, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if f in ("magic", "hcrc", "dcrc", "load", "entry"):
        return Hex(v, 8)
    return v
