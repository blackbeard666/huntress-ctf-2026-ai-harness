"""cpio archives (newc / crc / odc / old binary) and Apple pbzx payloads (prebuilt, SPECULATIVE -- never GM-asked yet).
Format tokens: cpio, payload (macOS .pkg Payload / OTA pbzx), initramfs, pbzx.

Wrappers peeled first (magic, never extension): gzip 1f8b, xz fd377a585a00, bzip2 "BZh", zstd 28b52ffd, lz4 frame
04224d18, and pbzx = "pbzx" + u64 BE flags, then chunks {u64 BE uncompressed size, u64 BE stored size, data} -- data is
an XZ stream (fd377a585a00) unless stored size == uncompressed size (raw chunk); the chunk outputs concatenate to cpio.
Headers (libarchive cpio(5)):
  newc "070701" / crc "070702": 110 B = magic + 13 x 8 ASCII-hex fields (ino mode uid gid nlink mtime filesize
    devmajor devminor rdevmajor rdevminor namesize check); name (namesize incl. NUL) padded so header+name is 4-aligned,
    data padded to 4.
  odc "070707": 76 B = magic + dev ino mode uid gid nlink rdev (6 octal digits each) mtime (11) namesize (6)
    filesize (11); no padding.
  bin: 26 B of u16 (magic 0o070707 = 0x71c7; bytes c7 71 -> little-endian, 71 c7 -> big-endian) dev ino mode uid gid
    nlink rdev mtime[2] namesize filesize[2] (the 32-bit values are most-significant u16 FIRST, each u16 in the
    archive byte order); name and data padded to even.
The archive ends at the "TRAILER!!!" entry (excluded from every list); only the FIRST archive is read (`cpio -t`
semantics; a concatenated initramfs tail is ignored).
Renderings: member_names = stored names verbatim, archive order (".", "./x" kept as stored); member_modes = full
st_mode as C "%#o" ("0100755", dirs "040755"); member_modes_octal = "%04o" of mode & 0o7777 (tar.py convention);
member_mtimes_utc = unix seconds (cpio mtime is UTC epoch) as 'YYYY-MM-DDTHH:MM:SSZ'; *_unix = raw ints;
member_sizes = filesize (symlink size = target length). member_cpu_type_set = Mach-O members' cputype "0x%08x"
(fat members: every fat_arch), member_e_machine_set = ELF members' e_machine "0x%04x" (deduped, first occurrence; none
-> "none"). wrapper/compression = the peeled layers ("none", "gzip", "xz", "pbzx", "pbzx+xz"...).
No cpio magic after unwrapping -> "none"; a truncated tail keeps the members that parsed."""
import bz2
import lzma
import struct

from .ar import _dedupe, _elf_machine, _iso, _macho_cpu

FIELDS = {
    ("cpio", "format"): "cpio_value",
    ("cpio", "cpio_format"): "cpio_value",
    ("cpio", "archive_format"): "cpio_value",
    ("cpio", "header_format"): "cpio_value",
    ("cpio", "variant"): "cpio_value",
    ("cpio", "magic"): "cpio_value",
    ("cpio", "member_names"): "cpio_value",
    ("cpio", "member_name_list"): "cpio_value",
    ("cpio", "file_names"): "cpio_value",
    ("cpio", "entry_names"): "cpio_value",
    ("cpio", "names"): "cpio_value",
    ("cpio", "path_names"): "cpio_value",
    ("cpio", "member_count"): "cpio_value",
    ("cpio", "entry_count"): "cpio_value",
    ("cpio", "file_count"): "cpio_value",
    ("cpio", "number_of_members"): "cpio_value",
    ("cpio", "number_of_entries"): "cpio_value",
    ("cpio", "member_modes"): "cpio_value",
    ("cpio", "member_modes_octal"): "cpio_value",
    ("cpio", "member_mtimes_utc"): "cpio_value",
    ("cpio", "member_mtimes"): "cpio_value",
    ("cpio", "member_mtimes_unix"): "cpio_value",
    ("cpio", "member_sizes"): "cpio_value",
    ("cpio", "member_sizes_bytes"): "cpio_value",
    ("cpio", "member_uids"): "cpio_value",
    ("cpio", "member_gids"): "cpio_value",
    ("cpio", "member_inodes"): "cpio_value",
    ("cpio", "member_nlinks"): "cpio_value",
    ("cpio", "member_linknames"): "cpio_value",
    ("cpio", "symlink_targets"): "cpio_value",
    ("cpio", "member_cpu_type_set"): "cpio_value",
    ("cpio", "member_cputype_set"): "cpio_value",
    ("cpio", "member_e_machine_set"): "cpio_value",
    ("cpio", "member_machine_set"): "cpio_value",
    ("cpio", "wrapper"): "cpio_value",
    ("cpio", "compression"): "cpio_value",
    ("cpio", "payload_compression"): "cpio_value",
    ("cpio", "pbzx_flags_u64_hex"): "cpio_value",
    ("cpio", "pbzx_chunk_count"): "cpio_value",
    ("payload", "format"): "cpio_value",
    ("payload", "cpio_format"): "cpio_value",
    ("payload", "archive_format"): "cpio_value",
    ("payload", "header_format"): "cpio_value",
    ("payload", "variant"): "cpio_value",
    ("payload", "magic"): "cpio_value",
    ("payload", "member_names"): "cpio_value",
    ("payload", "member_name_list"): "cpio_value",
    ("payload", "file_names"): "cpio_value",
    ("payload", "entry_names"): "cpio_value",
    ("payload", "names"): "cpio_value",
    ("payload", "path_names"): "cpio_value",
    ("payload", "member_count"): "cpio_value",
    ("payload", "entry_count"): "cpio_value",
    ("payload", "file_count"): "cpio_value",
    ("payload", "number_of_members"): "cpio_value",
    ("payload", "number_of_entries"): "cpio_value",
    ("payload", "member_modes"): "cpio_value",
    ("payload", "member_modes_octal"): "cpio_value",
    ("payload", "member_mtimes_utc"): "cpio_value",
    ("payload", "member_mtimes"): "cpio_value",
    ("payload", "member_mtimes_unix"): "cpio_value",
    ("payload", "member_sizes"): "cpio_value",
    ("payload", "member_sizes_bytes"): "cpio_value",
    ("payload", "member_uids"): "cpio_value",
    ("payload", "member_gids"): "cpio_value",
    ("payload", "member_inodes"): "cpio_value",
    ("payload", "member_nlinks"): "cpio_value",
    ("payload", "member_linknames"): "cpio_value",
    ("payload", "symlink_targets"): "cpio_value",
    ("payload", "member_cpu_type_set"): "cpio_value",
    ("payload", "member_cputype_set"): "cpio_value",
    ("payload", "member_e_machine_set"): "cpio_value",
    ("payload", "member_machine_set"): "cpio_value",
    ("payload", "wrapper"): "cpio_value",
    ("payload", "compression"): "cpio_value",
    ("payload", "payload_compression"): "cpio_value",
    ("payload", "pbzx_flags_u64_hex"): "cpio_value",
    ("payload", "pbzx_chunk_count"): "cpio_value",
    ("initramfs", "format"): "cpio_value",
    ("initramfs", "cpio_format"): "cpio_value",
    ("initramfs", "archive_format"): "cpio_value",
    ("initramfs", "header_format"): "cpio_value",
    ("initramfs", "variant"): "cpio_value",
    ("initramfs", "magic"): "cpio_value",
    ("initramfs", "member_names"): "cpio_value",
    ("initramfs", "member_name_list"): "cpio_value",
    ("initramfs", "file_names"): "cpio_value",
    ("initramfs", "entry_names"): "cpio_value",
    ("initramfs", "names"): "cpio_value",
    ("initramfs", "path_names"): "cpio_value",
    ("initramfs", "member_count"): "cpio_value",
    ("initramfs", "entry_count"): "cpio_value",
    ("initramfs", "file_count"): "cpio_value",
    ("initramfs", "number_of_members"): "cpio_value",
    ("initramfs", "number_of_entries"): "cpio_value",
    ("initramfs", "member_modes"): "cpio_value",
    ("initramfs", "member_modes_octal"): "cpio_value",
    ("initramfs", "member_mtimes_utc"): "cpio_value",
    ("initramfs", "member_mtimes"): "cpio_value",
    ("initramfs", "member_mtimes_unix"): "cpio_value",
    ("initramfs", "member_sizes"): "cpio_value",
    ("initramfs", "member_sizes_bytes"): "cpio_value",
    ("initramfs", "member_uids"): "cpio_value",
    ("initramfs", "member_gids"): "cpio_value",
    ("initramfs", "member_inodes"): "cpio_value",
    ("initramfs", "member_nlinks"): "cpio_value",
    ("initramfs", "member_linknames"): "cpio_value",
    ("initramfs", "symlink_targets"): "cpio_value",
    ("initramfs", "member_cpu_type_set"): "cpio_value",
    ("initramfs", "member_cputype_set"): "cpio_value",
    ("initramfs", "member_e_machine_set"): "cpio_value",
    ("initramfs", "member_machine_set"): "cpio_value",
    ("initramfs", "wrapper"): "cpio_value",
    ("initramfs", "compression"): "cpio_value",
    ("initramfs", "payload_compression"): "cpio_value",
    ("initramfs", "pbzx_flags_u64_hex"): "cpio_value",
    ("initramfs", "pbzx_chunk_count"): "cpio_value",
    ("pbzx", "format"): "cpio_value",
    ("pbzx", "cpio_format"): "cpio_value",
    ("pbzx", "archive_format"): "cpio_value",
    ("pbzx", "header_format"): "cpio_value",
    ("pbzx", "variant"): "cpio_value",
    ("pbzx", "magic"): "cpio_value",
    ("pbzx", "member_names"): "cpio_value",
    ("pbzx", "member_name_list"): "cpio_value",
    ("pbzx", "file_names"): "cpio_value",
    ("pbzx", "entry_names"): "cpio_value",
    ("pbzx", "names"): "cpio_value",
    ("pbzx", "path_names"): "cpio_value",
    ("pbzx", "member_count"): "cpio_value",
    ("pbzx", "entry_count"): "cpio_value",
    ("pbzx", "file_count"): "cpio_value",
    ("pbzx", "number_of_members"): "cpio_value",
    ("pbzx", "number_of_entries"): "cpio_value",
    ("pbzx", "member_modes"): "cpio_value",
    ("pbzx", "member_modes_octal"): "cpio_value",
    ("pbzx", "member_mtimes_utc"): "cpio_value",
    ("pbzx", "member_mtimes"): "cpio_value",
    ("pbzx", "member_mtimes_unix"): "cpio_value",
    ("pbzx", "member_sizes"): "cpio_value",
    ("pbzx", "member_sizes_bytes"): "cpio_value",
    ("pbzx", "member_uids"): "cpio_value",
    ("pbzx", "member_gids"): "cpio_value",
    ("pbzx", "member_inodes"): "cpio_value",
    ("pbzx", "member_nlinks"): "cpio_value",
    ("pbzx", "member_linknames"): "cpio_value",
    ("pbzx", "symlink_targets"): "cpio_value",
    ("pbzx", "member_cpu_type_set"): "cpio_value",
    ("pbzx", "member_cputype_set"): "cpio_value",
    ("pbzx", "member_e_machine_set"): "cpio_value",
    ("pbzx", "member_machine_set"): "cpio_value",
    ("pbzx", "wrapper"): "cpio_value",
    ("pbzx", "compression"): "cpio_value",
    ("pbzx", "payload_compression"): "cpio_value",
    ("pbzx", "pbzx_flags_u64_hex"): "cpio_value",
    ("pbzx", "pbzx_chunk_count"): "cpio_value",
}

_MAX_OUT = 256 << 20
_MAX_MEMBERS = 20000


def _bounded(dec, b):
    out = dec.decompress(b, _MAX_OUT)
    return out


def _pbzx(b):
    """(cpio bytes, flags, chunk_count, inner) of a pbzx stream, or None."""
    flags, = struct.unpack_from(">Q", b, 4)
    off, out, n, inner = 12, [], 0, set()
    total = 0
    while off + 16 <= len(b):
        usize, csize = struct.unpack_from(">QQ", b, off)
        off += 16
        chunk = b[off:off + csize]
        off += csize
        n += 1
        if chunk[:6] == b"\xfd7zXZ\x00":
            out.append(_bounded(lzma.LZMADecompressor(), chunk))
            inner.add("xz")
        else:
            out.append(chunk)
        total += len(out[-1])
        if total > _MAX_OUT or csize == 0:
            break
    return b"".join(out), flags, n, inner


def unwrap(b):
    """(cpio-candidate bytes, [layer names], pbzx info dict or None)."""
    layers, info = [], None
    for _ in range(4):
        if b[:2] == b"\x1f\x8b":
            b = _bounded(zlib_gzip(), b)
            layers.append("gzip")
        elif b[:6] == b"\xfd7zXZ\x00":
            b = _bounded(lzma.LZMADecompressor(), b)
            layers.append("xz")
        elif b[:3] == b"BZh":
            b = _bounded(bz2.BZ2Decompressor(), b)
            layers.append("bzip2")
        elif b[:4] == b"\x28\xb5\x2f\xfd":
            import zstandard
            b = zstandard.ZstdDecompressor().decompressobj().decompress(b)[:_MAX_OUT]
            layers.append("zstd")
        elif b[:4] == b"\x04\x22\x4d\x18":
            import lz4.frame
            b = lz4.frame.decompress(b)[:_MAX_OUT]
            layers.append("lz4")
        elif b[:4] == b"pbzx" and len(b) >= 12:
            b, flags, n, inner = _pbzx(b)
            info = {"flags": flags, "chunks": n}
            layers.append("+".join(["pbzx"] + sorted(inner)))
        else:
            break
    return b, layers, info


def zlib_gzip():
    import zlib
    return zlib.decompressobj(16 + zlib.MAX_WBITS)


def _hex(s):
    return int(s, 16)


def parse_cpio(b):
    """{"format", "members": [dict]} of the first cpio archive in b, or None."""
    m = b[:6]
    if m in (b"070701", b"070702"):
        fmt = "newc" if m == b"070701" else "crc"
    elif m == b"070707":
        fmt = "odc"
    elif b[:2] in (b"\xc7\x71", b"\x71\xc7"):
        fmt = "bin"
    else:
        return None
    end = "<" if b[:2] == b"\xc7\x71" else ">"
    off, ms = 0, []
    while len(ms) < _MAX_MEMBERS:
        try:
            if fmt in ("newc", "crc"):
                h = b[off:off + 110]
                if len(h) < 110 or h[:6] not in (b"070701", b"070702"):
                    break
                v = [_hex(h[6 + 8 * i:14 + 8 * i]) for i in range(13)]
                ino, mode, uid, gid, nlink, mtime, size = v[:7]
                nsz = v[11]
                nstart = off + 110
                dstart = (nstart + nsz + 3) & ~3
                nxt = (dstart + size + 3) & ~3
            elif fmt == "odc":
                h = b[off:off + 76]
                if len(h) < 76 or h[:6] != b"070707":
                    break
                o = lambda a, n: int(h[a:a + n], 8)  # noqa: E731
                ino, mode, uid, gid, nlink = o(12, 6), o(18, 6), o(24, 6), o(30, 6), o(36, 6)
                mtime, nsz, size = o(48, 11), o(59, 6), o(65, 11)
                nstart = off + 76
                dstart = nstart + nsz
                nxt = dstart + size
            else:
                h = b[off:off + 26]
                if len(h) < 26:
                    break
                u = struct.unpack(end + "13H", h)
                if u[0] != 0o070707:
                    break
                ino, mode, uid, gid, nlink = u[2], u[3], u[4], u[5], u[6]
                mtime = (u[8] << 16) | u[9]
                nsz = u[10]
                size = (u[11] << 16) | u[12]
                nstart = off + 26
                dstart = (nstart + nsz + 1) & ~1
                nxt = (dstart + size + 1) & ~1
        except ValueError:
            break
        name = b[nstart:nstart + nsz].split(b"\0", 1)[0].decode("utf-8", "surrogateescape")
        if name == "TRAILER!!!":
            break
        if nsz == 0 or dstart + size > len(b):
            break
        ms.append({"name": name, "ino": ino, "mode": mode, "uid": uid, "gid": gid, "nlink": nlink,
                   "mtime": mtime, "size": size, "data": b[dstart:dstart + size]})
        off = nxt
    return {"format": fmt, "members": ms}


def _fat_cpus(d):
    if len(d) >= 8 and d[:4] in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
        n, = struct.unpack_from(">I", d, 4)
        w = 20 if d[3] == 0xbe else 32
        if 0 < n < 20 and 8 + n * w <= len(d):
            return [struct.unpack_from(">I", d, 8 + i * w)[0] for i in range(n)]
        return []
    c = _macho_cpu(d)
    return [] if c is None else [c]


def cpio_value(data, ctx):
    try:
        return _value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- defensive: a hostile member never raises past the extractor
        return None


def _value(data, f):
    if data is None:
        return None
    raw = bytes(data)
    b, layers, info = unwrap(raw)
    if f in ("pbzx_flags_u64_hex", "pbzx_chunk_count"):
        if info is None:
            return "none"
        if f == "pbzx_chunk_count":
            return info["chunks"]
        from ..spell import Hex
        return Hex(info["flags"], 16)
    a = parse_cpio(b)
    if a is None:
        return "none"
    ms = a["members"]
    if f in ("wrapper", "compression", "payload_compression"):
        return "+".join(layers) if layers else "none"
    if f in ("format", "cpio_format", "archive_format", "header_format", "variant"):
        return a["format"]
    if f == "magic":
        return {"newc": "070701", "crc": "070702", "odc": "070707", "bin": "070707"}[a["format"]]
    if f.endswith("_count") or f.startswith("number_of_"):
        return len(ms)
    if f in ("member_cpu_type_set", "member_cputype_set"):
        v = _dedupe("0x%08x" % c for m in ms for c in _fat_cpus(m["data"]))
        return v or "none"
    if f in ("member_e_machine_set", "member_machine_set"):
        v = _dedupe("0x%04x" % c for c in (_elf_machine(m["data"]) for m in ms) if c is not None)
        return v or "none"
    if f in ("member_linknames", "symlink_targets"):
        v = [m["data"].decode("utf-8", "surrogateescape") for m in ms if m["mode"] & 0o170000 == 0o120000]
        return v or "none"
    if "name" in f:
        return [m["name"] for m in ms]
    if f == "member_modes_octal":
        return ["%04o" % (m["mode"] & 0o7777) for m in ms]
    if f == "member_modes":
        return ["0%o" % m["mode"] for m in ms]
    if "mtime" in f:
        return [m["mtime"] for m in ms] if f.endswith("_unix") else [_iso(m["mtime"]) for m in ms]
    if "size" in f:
        return [m["size"] for m in ms]
    key = {"member_uids": "uid", "member_gids": "gid", "member_inodes": "ino", "member_nlinks": "nlink"}.get(f)
    if key:
        return [m[key] for m in ms]
    return None
