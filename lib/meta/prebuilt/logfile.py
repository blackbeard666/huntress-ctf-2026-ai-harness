"""NTFS $LogFile restart / record pages (prebuilt, SPECULATIVE -- never GM-asked yet).

Input = a $LogFile (or a carved run of its pages). Every page is a multi-sector block (little-endian, libfsntfs /
MS LFS docs): signature @0, update-sequence array offset u16 @4, its count u16 @6 (1 USN + one entry per 512-B
stride). FIXUPS FIRST: the last u16 of every stride is replaced by the matching USA entry (values straddling a sector
end are wrong otherwise).
`RSTR` (or `CHKD`) restart page, pages 0 and 1: chkdsk LSN u64 @8, system page size u32 @16, log page size u32 @20,
restart area offset u16 @24, minor/major version i16 @26/@28. Restart area: current LSN u64 @0, log clients u16 @8,
client free/in-use list u16 @10/@12, flags u16 @14, seq-number bits u32 @16, area length u16 @20, client array
offset u16 @22, file size u64 @0x18, record header length u16 @0x24, page data offset u16 @0x26; client records
(0xA0 B) {oldest LSN, restart LSN, prev, next, seq, name length u32 @0x1C, UTF-16 name @0x20}.
The answered restart page is the one with the HIGHER current LSN (the newer copy, as NTFS picks it on mount).
`RCRD` record pages (from page 2 on, log-page-size strides): last LSN / file offset u64 @8, flags u32 @16, page count
u16 @20, page position u16 @22, next record offset u16 @24, last END LSN u64 @32.
rcrd_page_count = number of RCRD-signature pages; last_end_lsn / last_lsn = the highest value over those pages.
LSNs are plain base-10 integers (how LogFileParser / dfir_ntfs / NTFS Log Tracker print them); *_hex variants add
`0x%016x`. A fresh/reset $LogFile (all 0xFF, as mkntfs and ntfs-3g leave it) or a non-log file -> "none"."""
import struct

from ..spell import Hex

_RSTR = ("current_lsn", "restart_current_lsn", "restart_area_current_lsn", "chkdsk_lsn", "system_page_size_bytes",
         "system_page_size", "log_page_size_bytes", "log_page_size", "page_size_bytes", "restart_area_offset",
         "restart_offset", "major_version", "minor_version", "version", "log_version", "log_clients",
         "log_client_count", "client_count", "file_size", "file_size_bytes", "log_file_size_bytes",
         "log_file_size", "restart_area_flags_u16_hex", "client_names", "client_name", "restart_page_count",
         "clean_shutdown", "current_lsn_hex", "current_lsn_u64_hex")
_RCRD = ("rcrd_page_count", "record_page_count", "log_record_page_count", "last_end_lsn", "rcrd_last_end_lsn",
         "last_lsn", "rcrd_last_lsn", "highest_lsn", "max_lsn", "last_end_lsn_hex", "last_end_lsn_u64_hex")
FIELDS = {
    ("logfile", "current_lsn"): "logfile_value",
    ("logfile", "restart_current_lsn"): "logfile_value",
    ("logfile", "restart_area_current_lsn"): "logfile_value",
    ("logfile", "chkdsk_lsn"): "logfile_value",
    ("logfile", "system_page_size_bytes"): "logfile_value",
    ("logfile", "system_page_size"): "logfile_value",
    ("logfile", "log_page_size_bytes"): "logfile_value",
    ("logfile", "log_page_size"): "logfile_value",
    ("logfile", "page_size_bytes"): "logfile_value",
    ("logfile", "restart_area_offset"): "logfile_value",
    ("logfile", "restart_offset"): "logfile_value",
    ("logfile", "major_version"): "logfile_value",
    ("logfile", "minor_version"): "logfile_value",
    ("logfile", "version"): "logfile_value",
    ("logfile", "log_version"): "logfile_value",
    ("logfile", "log_clients"): "logfile_value",
    ("logfile", "log_client_count"): "logfile_value",
    ("logfile", "client_count"): "logfile_value",
    ("logfile", "file_size"): "logfile_value",
    ("logfile", "file_size_bytes"): "logfile_value",
    ("logfile", "log_file_size_bytes"): "logfile_value",
    ("logfile", "log_file_size"): "logfile_value",
    ("logfile", "restart_area_flags_u16_hex"): "logfile_value",
    ("logfile", "client_names"): "logfile_value",
    ("logfile", "client_name"): "logfile_value",
    ("logfile", "restart_page_count"): "logfile_value",
    ("logfile", "clean_shutdown"): "logfile_value",
    ("logfile", "current_lsn_hex"): "logfile_value",
    ("logfile", "current_lsn_u64_hex"): "logfile_value",
    ("logfile", "rcrd_page_count"): "logfile_value",
    ("logfile", "record_page_count"): "logfile_value",
    ("logfile", "log_record_page_count"): "logfile_value",
    ("logfile", "last_end_lsn"): "logfile_value",
    ("logfile", "rcrd_last_end_lsn"): "logfile_value",
    ("logfile", "last_lsn"): "logfile_value",
    ("logfile", "rcrd_last_lsn"): "logfile_value",
    ("logfile", "highest_lsn"): "logfile_value",
    ("logfile", "max_lsn"): "logfile_value",
    ("logfile", "last_end_lsn_hex"): "logfile_value",
    ("logfile", "last_end_lsn_u64_hex"): "logfile_value",
    ("ntfs_logfile", "current_lsn"): "logfile_value",
    ("ntfs_logfile", "restart_current_lsn"): "logfile_value",
    ("ntfs_logfile", "restart_area_current_lsn"): "logfile_value",
    ("ntfs_logfile", "chkdsk_lsn"): "logfile_value",
    ("ntfs_logfile", "system_page_size_bytes"): "logfile_value",
    ("ntfs_logfile", "system_page_size"): "logfile_value",
    ("ntfs_logfile", "log_page_size_bytes"): "logfile_value",
    ("ntfs_logfile", "log_page_size"): "logfile_value",
    ("ntfs_logfile", "page_size_bytes"): "logfile_value",
    ("ntfs_logfile", "restart_area_offset"): "logfile_value",
    ("ntfs_logfile", "restart_offset"): "logfile_value",
    ("ntfs_logfile", "major_version"): "logfile_value",
    ("ntfs_logfile", "minor_version"): "logfile_value",
    ("ntfs_logfile", "version"): "logfile_value",
    ("ntfs_logfile", "log_version"): "logfile_value",
    ("ntfs_logfile", "log_clients"): "logfile_value",
    ("ntfs_logfile", "log_client_count"): "logfile_value",
    ("ntfs_logfile", "client_count"): "logfile_value",
    ("ntfs_logfile", "file_size"): "logfile_value",
    ("ntfs_logfile", "file_size_bytes"): "logfile_value",
    ("ntfs_logfile", "log_file_size_bytes"): "logfile_value",
    ("ntfs_logfile", "log_file_size"): "logfile_value",
    ("ntfs_logfile", "restart_area_flags_u16_hex"): "logfile_value",
    ("ntfs_logfile", "client_names"): "logfile_value",
    ("ntfs_logfile", "client_name"): "logfile_value",
    ("ntfs_logfile", "restart_page_count"): "logfile_value",
    ("ntfs_logfile", "clean_shutdown"): "logfile_value",
    ("ntfs_logfile", "current_lsn_hex"): "logfile_value",
    ("ntfs_logfile", "current_lsn_u64_hex"): "logfile_value",
    ("ntfs_logfile", "rcrd_page_count"): "logfile_value",
    ("ntfs_logfile", "record_page_count"): "logfile_value",
    ("ntfs_logfile", "log_record_page_count"): "logfile_value",
    ("ntfs_logfile", "last_end_lsn"): "logfile_value",
    ("ntfs_logfile", "rcrd_last_end_lsn"): "logfile_value",
    ("ntfs_logfile", "last_lsn"): "logfile_value",
    ("ntfs_logfile", "rcrd_last_lsn"): "logfile_value",
    ("ntfs_logfile", "highest_lsn"): "logfile_value",
    ("ntfs_logfile", "max_lsn"): "logfile_value",
    ("ntfs_logfile", "last_end_lsn_hex"): "logfile_value",
    ("ntfs_logfile", "last_end_lsn_u64_hex"): "logfile_value",
}


def fixup(page):
    """The page with its update-sequence array applied (bytearray), or None when the header is not sane."""
    if len(page) < 512:
        return None
    off, cnt = struct.unpack_from("<HH", page, 4)
    if off < 8 or cnt < 2 or off + 2 * cnt > len(page) or off + 2 * cnt > 512:
        return None
    b = bytearray(page)
    for i in range(1, cnt):
        end = i * 512
        if end > len(b):
            break
        b[end - 2:end] = b[off + 2 * i:off + 2 * i + 2]
    return b


def _rstr(b):
    try:
        chk, sysps, logps, roff, minor, major = struct.unpack_from("<QIIHhh", b, 8)
        ra = roff
        cur, ncl, free, inuse, flags, seqbits, ralen, caoff, fsize = struct.unpack_from("<QHHHHIHHQ", b, ra)
    except struct.error:
        return None
    clients = []
    for i in range(min(ncl, 8)):
        o = ra + caoff + 0xA0 * i
        if o + 0x20 > len(b):
            break
        nl, = struct.unpack_from("<I", b, o + 0x1C)
        clients.append(bytes(b[o + 0x20:o + 0x20 + min(nl, 128)]).decode("utf-16-le", "replace"))
    return {"chkdsk_lsn": chk, "system_page_size": sysps, "log_page_size": logps, "restart_offset": roff,
            "minor": minor, "major": major, "current_lsn": cur, "log_clients": ncl, "flags": flags,
            "file_size": fsize, "clients": clients}


def parse(data):
    """{'rstr': [restart dicts], 'rcrd': [(last_lsn, flags, page_count, pos, next_off, last_end_lsn)]}."""
    rstr, rcrd = [], []
    for o in (0, 4096):
        pg = data[o:o + 4096]
        if pg[:4] in (b"RSTR", b"CHKD"):
            b = fixup(pg)
            r = _rstr(b) if b else None
            if r and r["log_page_size"] in (512, 1024, 2048, 4096, 8192, 16384, 65536):
                rstr.append(r)
    ps = rstr[0]["log_page_size"] if rstr else 4096
    for o in range(0, len(data) - 39, ps):
        if data[o:o + 4] == b"RCRD":
            b = fixup(data[o:o + ps])
            if b is None:
                continue
            last, flags, cnt, pos, nxt = struct.unpack_from("<QIHHH", b, 8)
            rcrd.append((last, flags, cnt, pos, nxt, struct.unpack_from("<Q", b, 32)[0]))
    return {"rstr": rstr, "rcrd": rcrd}


def logfile_value(data, ctx):
    if data is None:
        return None
    f = ctx.get("field") or ""
    p = parse(bytes(data[:1 << 26]))
    if f in _RCRD:
        if not p["rcrd"]:
            return "none"
        if f in ("rcrd_page_count", "record_page_count", "log_record_page_count"):
            return len(p["rcrd"])
        if "end" in f:
            v = max(r[5] for r in p["rcrd"])
        else:
            v = max(r[0] for r in p["rcrd"])
        return Hex(v, 16) if f.endswith("hex") else v
    if not p["rstr"]:
        return "none"
    r = max(p["rstr"], key=lambda x: x["current_lsn"])
    if f in ("current_lsn", "restart_current_lsn", "restart_area_current_lsn"):
        return r["current_lsn"]
    if f in ("current_lsn_hex", "current_lsn_u64_hex"):
        return Hex(r["current_lsn"], 16)
    if f == "chkdsk_lsn":
        return r["chkdsk_lsn"]
    if f.startswith("system_page_size"):
        return r["system_page_size"]
    if f.startswith("log_page_size") or f == "page_size_bytes":
        return r["log_page_size"]
    if f in ("restart_area_offset", "restart_offset"):
        return r["restart_offset"]
    if f == "major_version":
        return r["major"]
    if f == "minor_version":
        return r["minor"]
    if f in ("version", "log_version"):
        return "%d.%d" % (r["major"], r["minor"])
    if f in ("log_clients", "log_client_count", "client_count"):
        return r["log_clients"]
    if f in ("file_size", "file_size_bytes", "log_file_size_bytes", "log_file_size"):
        return r["file_size"]
    if f == "restart_area_flags_u16_hex":
        return Hex(r["flags"], 4)
    if f == "clean_shutdown":
        return bool(r["flags"] & 2)          # RESTART_SINGLE_PAGE_IO 0x1, clean dismount 0x2 (LFS)
    if f == "client_names":
        return r["clients"]
    if f == "client_name":
        return r["clients"][0] if r["clients"] else "none"
    if f == "restart_page_count":
        return len(p["rstr"])
    return None
