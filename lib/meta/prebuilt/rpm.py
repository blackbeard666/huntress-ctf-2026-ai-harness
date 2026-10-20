"""RPM package fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Layout (all BIG-endian): 96-byte lead -- magic ed ab ee db, major u8 @4, minor u8 @5, type u16 @6 (0 binary, 1 source),
archnum u16 @8, name 66 B @10 (NUL-padded, "name-version-release"), osnum u16 @76, signature_type u16 @78 -- then the
signature header, padded to an 8-byte boundary, then the main header. Each header: magic 8e ad e8 01, 4 reserved,
nindex u32, hsize u32, nindex 16-byte entries (tag, type, offset, count) and an hsize-byte store. Types: 2 INT8,
3 INT16, 4 INT32, 5 INT64, 6 STRING, 7 BIN, 8 STRING_ARRAY, 9 I18NSTRING (first = the C locale).
Main-header tags: NAME 1000, VERSION 1001, RELEASE 1002, EPOCH 1003, SUMMARY 1004, DESCRIPTION 1005, BUILDTIME 1006
(unix seconds; *_utc renders it ISO-8601 Z), BUILDHOST 1007, SIZE 1009, VENDOR 1011, LICENSE 1014, PACKAGER 1015,
GROUP 1016, URL 1020, OS 1021, ARCH 1022, SOURCERPM 1044, REQUIRENAME 1049, RPMVERSION 1064, PAYLOADFORMAT 1124,
PAYLOADCOMPRESSOR 1125, PAYLOADFLAGS 1126; file list = DIRNAMES[DIRINDEXES[i]] + BASENAMES[i] (stored order).
Values are the stored strings (rpm -qp --qf spelling). Not an RPM (wrong lead magic / no header magic) -> "none";
tag absent (e.g. EPOCH, VENDOR) -> "none"."""
import datetime
import struct

FIELDS = {
    ("rpm", "name"): "header_value",
    ("rpm", "header_name"): "header_value",
    ("rpm", "package_name"): "header_value",
    ("rpm", "header_package_name"): "header_value",
    ("rpm", "version"): "header_value",
    ("rpm", "header_version"): "header_value",
    ("rpm", "package_version"): "header_value",
    ("rpm", "header_package_version"): "header_value",
    ("rpm", "release"): "header_value",
    ("rpm", "header_release"): "header_value",
    ("rpm", "epoch"): "header_value",
    ("rpm", "header_epoch"): "header_value",
    ("rpm", "summary"): "header_value",
    ("rpm", "header_summary"): "header_value",
    ("rpm", "description"): "header_value",
    ("rpm", "header_description"): "header_value",
    ("rpm", "build_time"): "header_value",
    ("rpm", "header_build_time"): "header_value",
    ("rpm", "buildtime"): "header_value",
    ("rpm", "header_buildtime"): "header_value",
    ("rpm", "build_host"): "header_value",
    ("rpm", "header_build_host"): "header_value",
    ("rpm", "buildhost"): "header_value",
    ("rpm", "header_buildhost"): "header_value",
    ("rpm", "size"): "header_value",
    ("rpm", "header_size"): "header_value",
    ("rpm", "installed_size"): "header_value",
    ("rpm", "header_installed_size"): "header_value",
    ("rpm", "size_bytes"): "header_value",
    ("rpm", "header_size_bytes"): "header_value",
    ("rpm", "vendor"): "header_value",
    ("rpm", "header_vendor"): "header_value",
    ("rpm", "license"): "header_value",
    ("rpm", "header_license"): "header_value",
    ("rpm", "packager"): "header_value",
    ("rpm", "header_packager"): "header_value",
    ("rpm", "group"): "header_value",
    ("rpm", "header_group"): "header_value",
    ("rpm", "url"): "header_value",
    ("rpm", "header_url"): "header_value",
    ("rpm", "homepage"): "header_value",
    ("rpm", "header_homepage"): "header_value",
    ("rpm", "os"): "header_value",
    ("rpm", "header_os"): "header_value",
    ("rpm", "arch"): "header_value",
    ("rpm", "header_arch"): "header_value",
    ("rpm", "architecture"): "header_value",
    ("rpm", "header_architecture"): "header_value",
    ("rpm", "source_rpm"): "header_value",
    ("rpm", "header_source_rpm"): "header_value",
    ("rpm", "sourcerpm"): "header_value",
    ("rpm", "header_sourcerpm"): "header_value",
    ("rpm", "rpm_version"): "header_value",
    ("rpm", "header_rpm_version"): "header_value",
    ("rpm", "rpmversion"): "header_value",
    ("rpm", "header_rpmversion"): "header_value",
    ("rpm", "payload_format"): "header_value",
    ("rpm", "header_payload_format"): "header_value",
    ("rpm", "payloadformat"): "header_value",
    ("rpm", "header_payloadformat"): "header_value",
    ("rpm", "payload_compressor"): "header_value",
    ("rpm", "header_payload_compressor"): "header_value",
    ("rpm", "payloadcompressor"): "header_value",
    ("rpm", "header_payloadcompressor"): "header_value",
    ("rpm", "payload_compression"): "header_value",
    ("rpm", "header_payload_compression"): "header_value",
    ("rpm", "payload_flags"): "header_value",
    ("rpm", "header_payload_flags"): "header_value",
    ("rpm", "payloadflags"): "header_value",
    ("rpm", "header_payloadflags"): "header_value",
    ("rpm", "platform"): "header_value",
    ("rpm", "header_platform"): "header_value",
    ("rpm", "optflags"): "header_value",
    ("rpm", "header_optflags"): "header_value",
    ("rpm", "build_time_utc"): "header_value",
    ("rpm", "buildtime_utc"): "header_value",
    ("rpm", "requires"): "header_value",
    ("rpm", "require_names"): "header_value",
    ("rpm", "requirename"): "header_value",
    ("rpm", "provides"): "header_value",
    ("rpm", "provide_names"): "header_value",
    ("rpm", "file_names"): "header_value",
    ("rpm", "file_paths"): "header_value",
    ("rpm", "filenames"): "header_value",
    ("rpm", "file_count"): "header_value",
    ("rpm", "nvr"): "header_value",
    ("rpm", "nevra"): "header_value",
    ("rpm", "header_index_count"): "header_value",
    ("rpm", "header_entry_count"): "header_value",
    ("rpm", "header_tag_count"): "header_value",
    ("rpm", "lead_type"): "lead_value",
    ("rpm", "lead_archnum"): "lead_value",
    ("rpm", "lead_arch_num"): "lead_value",
    ("rpm", "lead_name"): "lead_value",
    ("rpm", "lead_osnum"): "lead_value",
    ("rpm", "lead_os_num"): "lead_value",
    ("rpm", "lead_signature_type"): "lead_value",
    ("rpm", "lead_version"): "lead_value",
    ("rpm", "lead_major"): "lead_value",
    ("rpm", "lead_minor"): "lead_value",
    ("rpm", "package_type"): "lead_value",
}

_TAGS = {"name": 1000, "version": 1001, "release": 1002, "epoch": 1003, "summary": 1004, "description": 1005,
         "build_time": 1006, "build_host": 1007, "size": 1009, "vendor": 1011, "license": 1014, "packager": 1015,
         "group": 1016, "url": 1020, "os": 1021, "arch": 1022, "source_rpm": 1044, "rpm_version": 1064,
         "payload_format": 1124, "payload_compressor": 1125, "payload_flags": 1126, "platform": 1132,
         "optflags": 1122, "requires": 1049, "provides": 1047}
_ALIAS = {"buildtime": "build_time", "buildhost": "build_host", "installed_size": "size", "size_bytes": "size",
          "sourcerpm": "source_rpm", "payloadcompressor": "payload_compressor",
          "payload_compression": "payload_compressor", "payloadformat": "payload_format",
          "payloadflags": "payload_flags", "rpmversion": "rpm_version", "architecture": "arch",
          "package_name": "name", "package_version": "version", "homepage": "url", "require_names": "requires",
          "requirename": "requires", "provide_names": "provides", "file_paths": "file_names",
          "filenames": "file_names", "header_entry_count": "header_index_count",
          "header_tag_count": "header_index_count", "buildtime_utc": "build_time_utc",
          "lead_arch_num": "lead_archnum", "lead_os_num": "lead_osnum", "package_type": "lead_type"}
_MAX_ENTRIES = 4096


def _header(b, off):
    """({tag: value}, nindex, end_offset) of the header structure at `off`, or None."""
    if len(b) < off + 16 or bytes(b[off:off + 4]) != b"\x8e\xad\xe8\x01":
        return None
    nindex, hsize = struct.unpack_from(">II", b, off + 8)
    if nindex > _MAX_ENTRIES:
        return None
    store = off + 16 + 16 * nindex
    end = store + hsize
    if end > len(b):
        return None
    tags = {}
    for i in range(nindex):
        tag, typ, o, cnt = struct.unpack_from(">IIII", b, off + 16 + 16 * i)
        p = store + o
        try:
            if typ in (6, 8, 9):
                vals, q = [], p
                for _ in range(1 if typ == 6 else cnt):
                    z = b.index(b"\x00", q, end)
                    vals.append(bytes(b[q:z]).decode("utf-8", "replace"))
                    q = z + 1
                v = vals[0] if typ in (6, 9) else vals
            elif typ in (2, 3, 4, 5):
                w = {2: 1, 3: 2, 4: 4, 5: 8}[typ]
                c = {2: "B", 3: "H", 4: "I", 5: "Q"}[typ]
                if p + w * cnt > end:
                    continue
                vals = list(struct.unpack_from(">%d%s" % (cnt, c), b, p))
                v = vals[0] if cnt == 1 else vals
            elif typ == 7:
                v = bytes(b[p:p + cnt])
            else:
                continue
        except (ValueError, struct.error):
            continue
        tags.setdefault(tag, v)
    return tags, nindex, end


def lead(b):
    if not b or len(b) < 96 or bytes(b[:4]) != b"\xed\xab\xee\xdb":
        return None
    typ, archnum = struct.unpack_from(">HH", b, 6)
    osnum, sigtype = struct.unpack_from(">HH", b, 76)
    name = bytes(b[10:76]).split(b"\x00", 1)[0].decode("utf-8", "replace")
    return {"lead_major": b[4], "lead_minor": b[5], "lead_version": "%d.%d" % (b[4], b[5]), "lead_type": typ,
            "lead_archnum": archnum, "lead_name": name, "lead_osnum": osnum, "lead_signature_type": sigtype}


def main_header(b):
    """(tags, nindex) of the RPM main header, or None."""
    if lead(b) is None:
        return None
    sig = _header(b, 96)
    if sig is None:
        return None
    off = sig[2] + (-sig[2] % 8)
    h = _header(b, off)
    return (h[0], h[1]) if h else None


def _iso(t):
    return datetime.datetime.fromtimestamp(int(t), datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _first(v):
    return v[0] if isinstance(v, list) and v else v


def header_value(data, ctx):
    if data is None:
        return None
    try:
        mh = main_header(data)
        if mh is None:
            return "none"
        tags, nindex = mh
        f = ctx.get("field") or ""
        f = f[len("header_"):] if f.startswith("header_") and f != "header_index_count" else f
        f = _ALIAS.get(f, f)
        if f == "header_index_count":
            return nindex
        if f in ("file_names", "file_count"):
            bn, dn, di = tags.get(1117), tags.get(1118), tags.get(1116)
            if isinstance(bn, str):
                bn = [bn]
            if isinstance(di, int):
                di = [di]
            if bn is None:
                old = tags.get(1027)
                names = [old] if isinstance(old, str) else (old or [])
            elif dn is None or di is None or len(di) != len(bn):
                return None
            else:
                names = [dn[d] + n for d, n in zip(di, bn)]
            return len(names) if f == "file_count" else names
        if f in ("nvr", "nevra"):
            n, v, r = tags.get(1000), tags.get(1001), tags.get(1002)
            if not (n and v and r):
                return "none"
            if f == "nvr":
                return "%s-%s-%s" % (n, v, r)
            e = _first(tags.get(1003))
            return "%s-%s%s-%s.%s" % (n, "%s:" % e if e is not None else "", v, r, tags.get(1022) or "none")
        if f == "build_time_utc":
            t = _first(tags.get(1006))
            return _iso(t) if t is not None else "none"
        tag = _TAGS.get(f)
        if tag is None:
            return None
        v = tags.get(tag)
        if v is None:
            return "none"
        if isinstance(v, list) and tag not in (1049, 1047):
            v = _first(v)
        return v
    except Exception:  # noqa: BLE001
        return None


def lead_value(data, ctx):
    if data is None:
        return None
    try:
        ld = lead(data)
        if ld is None:
            return "none"
        f = ctx.get("field") or ""
        return ld.get(_ALIAS.get(f, f))
    except Exception:  # noqa: BLE001
        return None
