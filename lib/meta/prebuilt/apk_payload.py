"""APK payload inventory (prebuilt, SPECULATIVE -- never GM-asked yet): native libs, multidex, assets, zip layout.

Own central-directory walk (EOCD -> CD file headers 0x02014b50, CD order, duplicates KEPT -- Janus/MasterKey style
dupes are the point of duplicate_entry_names); member data read via its local header (0x04034b50, data offset =
lfh + 30 + lfh name_len + lfh extra_len) and inflated with zlib raw deflate (method 8) or taken verbatim (method 0).
  native_abis          sorted set of <abi> for files lib/<abi>/<name>.so (JSON list)
  native_lib_names     full member names lib/<abi>/*.so in CD order; native_lib_e_machines_u16_hex = their ELF
                       e_machine (u16 @0x12, EI_DATA byte order) as "0x00b7" strings, null for a non-ELF .so
  abi_mismatch         member names whose e_machine disagrees with the dir ABI (arm64-v8a 0xb7, armeabi(-v7a) 0x28,
                       x86 0x03, x86_64 0x3e, riscv64 0xf3, mips/mips64 0x08); a non-ELF .so under a known ABI counts
  dex_names / dex_count / dex_versions   root classes.dex, classes<N>.dex (CD order); version = the 3 stored digits
  classes_dex_*        the dex.* header fields (prebuilt dex.py) of the root classes.dex; classes_dex_sha256/md5/sha1
                       = digest of its decompressed bytes
  zip_alignment_ok     every STORED entry's data offset % 4 == 0, and % 4096 == 0 for a stored .so (zipalign -p)
  entry_dos_times_constant  every CD entry carries the same DOS date+time (1980-01-01 00:00 on reproducible builds)
Not a zip -> "none"; a zip without AndroidManifest.xml (a JAR/plain zip posing as an APK) -> "none"."""
import hashlib
import struct
import zlib

FIELDS = {
    ("apk", "native_abis"): "payload_value",
    ("apk", "native_abi_set"): "payload_value",
    ("apk", "abis"): "payload_value",
    ("apk", "supported_abis"): "payload_value",
    ("apk", "native_code"): "payload_value",
    ("apk", "native_lib_names"): "payload_value",
    ("apk", "native_library_names"): "payload_value",
    ("apk", "native_libs"): "payload_value",
    ("apk", "native_lib_basenames"): "payload_value",
    ("apk", "native_lib_count"): "payload_value",
    ("apk", "native_library_count"): "payload_value",
    ("apk", "native_lib_e_machines_u16_hex"): "payload_value",
    ("apk", "native_lib_e_machine_u16_hex"): "payload_value",
    ("apk", "native_lib_machines_u16_hex"): "payload_value",
    ("apk", "abi_mismatch"): "payload_value",
    ("apk", "abi_mismatches"): "payload_value",
    ("apk", "abi_mismatch_names"): "payload_value",
    ("apk", "native_abi_mismatch"): "payload_value",
    ("apk", "has_abi_mismatch"): "payload_value",
    ("apk", "abi_mismatch_present"): "payload_value",
    ("apk", "dex_count"): "payload_value",
    ("apk", "classes_dex_count"): "payload_value",
    ("apk", "multidex_count"): "payload_value",
    ("apk", "is_multidex"): "payload_value",
    ("apk", "dex_names"): "payload_value",
    ("apk", "dex_file_names"): "payload_value",
    ("apk", "dex_files"): "payload_value",
    ("apk", "dex_versions"): "payload_value",
    ("apk", "dex_version_list"): "payload_value",
    ("apk", "classes_dex_sha256"): "payload_value",
    ("apk", "classes_dex_sha1"): "payload_value",
    ("apk", "classes_dex_md5"): "payload_value",
    ("apk", "classes_dex_size"): "payload_value",
    ("apk", "classes_dex_size_bytes"): "payload_value",
    ("apk", "has_resources_arsc"): "payload_value",
    ("apk", "resources_arsc_present"): "payload_value",
    ("apk", "asset_names"): "payload_value",
    ("apk", "assets"): "payload_value",
    ("apk", "asset_count"): "payload_value",
    ("apk", "entry_count"): "payload_value",
    ("apk", "member_count"): "payload_value",
    ("apk", "zip_entry_count"): "payload_value",
    ("apk", "cd_member_names"): "payload_value",
    ("apk", "central_directory_member_names"): "payload_value",
    ("apk", "member_names"): "payload_value",
    ("apk", "entry_names"): "payload_value",
    ("apk", "zip_alignment_ok"): "payload_value",
    ("apk", "zipalign_ok"): "payload_value",
    ("apk", "is_zipaligned"): "payload_value",
    ("apk", "zip_aligned"): "payload_value",
    ("apk", "misaligned_entry_names"): "payload_value",
    ("apk", "duplicate_entry_names"): "payload_value",
    ("apk", "duplicate_member_names"): "payload_value",
    ("apk", "duplicate_entries"): "payload_value",
    ("apk", "has_duplicate_entries"): "payload_value",
    ("apk", "entry_dos_times_constant"): "payload_value",
    ("apk", "dos_times_constant"): "payload_value",
    ("apk", "reproducible_timestamps"): "payload_value",
    # the dex.* header fields of the root classes.dex (prebuilt dex.py), prefixed classes_dex_
    ("apk", "classes_dex_magic"): "classes_dex_value",
    ("apk", "classes_dex_version"): "classes_dex_value",
    ("apk", "classes_dex_dex_version"): "classes_dex_value",
    ("apk", "classes_dex_format_version"): "classes_dex_value",
    ("apk", "classes_dex_checksum_u32_hex"): "classes_dex_value",
    ("apk", "classes_dex_adler32_u32_hex"): "classes_dex_value",
    ("apk", "classes_dex_checksum_valid"): "classes_dex_value",
    ("apk", "classes_dex_signature_sha1_hex"): "classes_dex_value",
    ("apk", "classes_dex_signature_hex"): "classes_dex_value",
    ("apk", "classes_dex_signature_valid"): "classes_dex_value",
    ("apk", "classes_dex_file_size"): "classes_dex_value",
    ("apk", "classes_dex_file_size_bytes"): "classes_dex_value",
    ("apk", "classes_dex_header_size"): "classes_dex_value",
    ("apk", "classes_dex_endian_tag_u32_hex"): "classes_dex_value",
    ("apk", "classes_dex_map_off"): "classes_dex_value",
    ("apk", "classes_dex_string_ids_size"): "classes_dex_value",
    ("apk", "classes_dex_string_count"): "classes_dex_value",
    ("apk", "classes_dex_type_ids_size"): "classes_dex_value",
    ("apk", "classes_dex_proto_ids_size"): "classes_dex_value",
    ("apk", "classes_dex_field_ids_size"): "classes_dex_value",
    ("apk", "classes_dex_method_ids_size"): "classes_dex_value",
    ("apk", "classes_dex_method_count"): "classes_dex_value",
    ("apk", "classes_dex_class_defs_size"): "classes_dex_value",
    ("apk", "classes_dex_class_count"): "classes_dex_value",
    ("apk", "classes_dex_data_size"): "classes_dex_value",
    ("apk", "classes_dex_data_off"): "classes_dex_value",
}

_ABI_MACHINE = {"arm64-v8a": 0xB7, "armeabi-v7a": 0x28, "armeabi": 0x28, "x86": 0x03, "x86_64": 0x3E,
                "riscv64": 0xF3, "mips": 0x08, "mips64": 0x08}
_ALIAS = {
    "native_abi_set": "native_abis", "abis": "native_abis", "supported_abis": "native_abis",
    "native_code": "native_abis", "native_library_names": "native_lib_names", "native_libs": "native_lib_names",
    "native_library_count": "native_lib_count", "native_lib_e_machine_u16_hex": "native_lib_e_machines_u16_hex",
    "native_lib_machines_u16_hex": "native_lib_e_machines_u16_hex", "abi_mismatches": "abi_mismatch",
    "abi_mismatch_names": "abi_mismatch", "native_abi_mismatch": "abi_mismatch",
    "abi_mismatch_present": "has_abi_mismatch", "classes_dex_count": "dex_count", "multidex_count": "dex_count",
    "dex_file_names": "dex_names", "dex_files": "dex_names", "dex_version_list": "dex_versions",
    "classes_dex_size_bytes": "classes_dex_size", "resources_arsc_present": "has_resources_arsc",
    "assets": "asset_names", "member_count": "entry_count", "zip_entry_count": "entry_count",
    "central_directory_member_names": "cd_member_names", "member_names": "cd_member_names",
    "entry_names": "cd_member_names", "zipalign_ok": "zip_alignment_ok", "is_zipaligned": "zip_alignment_ok",
    "zip_aligned": "zip_alignment_ok", "duplicate_member_names": "duplicate_entry_names",
    "duplicate_entries": "duplicate_entry_names", "dos_times_constant": "entry_dos_times_constant",
    "reproducible_timestamps": "entry_dos_times_constant",
}


def _entries(b):
    """CD entries [(name, method, csize, lfh_off, dos_time, dos_date)] in CD order, or None (not a zip)."""
    eo = b.rfind(b"PK\x05\x06", max(0, len(b) - 0x10000 - 22))
    if eo < 0 or eo + 22 > len(b):
        return None
    _, _, _, n_tot, cd_size, cd_off, _ = struct.unpack_from("<HHHHIIH", b, eo + 4)
    base = eo - cd_size - cd_off              # bytes prepended before the zip (Janus: a DEX in front)
    if base < 0 or b[base + cd_off:base + cd_off + 4] != b"PK\x01\x02":
        base = 0
    p, out = base + cd_off, []
    while p + 46 <= len(b) and b[p:p + 4] == b"PK\x01\x02":
        (_, _, flags, method, mtime, mdate, _, csize, _, nlen, xlen, clen, _, _, _,
         lfh) = struct.unpack_from("<HHHHHHIIIHHHHHII", b, p + 4)
        raw = b[p + 46:p + 46 + nlen]
        name = raw.decode("utf-8" if flags & 0x800 else "cp437", "replace")
        out.append((name, method, csize, base + lfh, mtime, mdate))
        p += 46 + nlen + xlen + clen
    return out


def _data_off(b, lfh):
    if b[lfh:lfh + 4] != b"PK\x03\x04":
        return None
    nlen, xlen = struct.unpack_from("<HH", b, lfh + 26)
    return lfh + 30 + nlen + xlen


def _read(b, ent):
    _, method, csize, lfh, _, _ = ent
    off = _data_off(b, lfh)
    if off is None:
        return None
    raw = b[off:off + csize]
    if method == 0:
        return bytes(raw)
    if method == 8:
        try:
            return zlib.decompressobj(-15).decompress(raw)
        except zlib.error:
            return None
    return None


def _machine(so):
    if not so or len(so) < 20 or so[:4] != b"\x7fELF":
        return None
    return struct.unpack_from(">H" if so[5] == 2 else "<H", so, 18)[0]


def _native(ents):
    out = []
    for e in ents:
        parts = e[0].split("/")
        if len(parts) == 3 and parts[0] == "lib" and parts[1] and parts[2].endswith(".so"):
            out.append((parts[1], e))
    return out


def _dexes(ents):
    out = []
    for e in ents:
        n = e[0]
        if n.startswith("classes") and n.endswith(".dex") and "/" not in n:
            mid = n[7:-4]
            if mid == "" or (mid.isdigit() and mid[0] != "0" and int(mid) >= 2):
                out.append(e)
    return out


def _apk(data):
    """(bytes, CD entries) of an APK, or None (not a zip / no AndroidManifest.xml)."""
    if not isinstance(data, (bytes, bytearray)):
        return None
    b = bytes(data)
    ents = _entries(b)
    if not ents or not any(e[0] == "AndroidManifest.xml" for e in ents):
        return None
    return b, ents


def payload_value(data, ctx):
    if data is None:
        return None
    try:
        r = _payload(data, _ALIAS.get((ctx or {}).get("field") or "", (ctx or {}).get("field") or ""))
    except (struct.error, ValueError, IndexError):
        return "none"
    return "none" if r is None else r


def _payload(data, field):
    a = _apk(data)
    if a is None:
        return None
    b, ents = a
    names = [e[0] for e in ents]
    if field == "entry_count":
        return len(ents)
    if field == "cd_member_names":
        return names
    if field in ("duplicate_entry_names", "has_duplicate_entries"):
        seen, dup = set(), []
        for n in names:
            if n in seen and n not in dup:
                dup.append(n)
            seen.add(n)
        return bool(dup) if field.startswith("has_") else dup
    if field == "entry_dos_times_constant":
        return len({(e[4], e[5]) for e in ents}) == 1
    if field == "has_resources_arsc":
        return "resources.arsc" in names
    if field in ("asset_names", "asset_count"):
        assets = [n for n in names if n.startswith("assets/") and not n.endswith("/")]
        return len(assets) if field == "asset_count" else assets
    if field in ("zip_alignment_ok", "misaligned_entry_names"):
        bad = []
        for e in ents:
            if e[1] != 0:
                continue
            off = _data_off(b, e[3])
            align = 4096 if e[0].endswith(".so") else 4
            if off is None or off % align:
                bad.append(e[0])
        return bad if field == "misaligned_entry_names" else not bad
    nat = _native(ents)
    if field == "native_abis":
        return sorted({abi for abi, _ in nat})
    if field == "native_lib_names":
        return [e[0] for _, e in nat]
    if field == "native_lib_basenames":
        out = []
        for _, e in nat:
            bn = e[0].rsplit("/", 1)[1]
            if bn not in out:
                out.append(bn)
        return out
    if field == "native_lib_count":
        return len(nat)
    if field == "native_lib_e_machines_u16_hex":
        ms = [_machine(_read(b, e)) for _, e in nat]
        return [None if m is None else "0x%04x" % m for m in ms]
    if field in ("abi_mismatch", "has_abi_mismatch"):
        bad = []
        for abi, e in nat:
            want = _ABI_MACHINE.get(abi)
            if want is not None and _machine(_read(b, e)) != want:
                bad.append(e[0])
        return bool(bad) if field.startswith("has_") else bad
    dx = _dexes(ents)
    if field in ("dex_count", "is_multidex"):
        return len(dx) > 1 if field == "is_multidex" else len(dx)
    if field == "dex_names":
        return [e[0] for e in dx]
    if field == "dex_versions":
        out = []
        for e in dx:
            d = _read(b, e)
            ok = d and len(d) >= 8 and d[:4] == b"dex\n" and d[7] == 0 and d[4:7].isdigit()
            out.append(d[4:7].decode() if ok else None)
        return out
    if field in ("classes_dex_sha256", "classes_dex_sha1", "classes_dex_md5", "classes_dex_size"):
        d = _classes_dex(b, ents)
        if d is None:
            return None
        if field == "classes_dex_size":
            return len(d)
        return hashlib.new(field.rsplit("_", 1)[1], d).hexdigest()
    return None


def _classes_dex(b, ents):
    for e in ents:                          # first root classes.dex in CD order (what zipfile/aapt list first)
        if e[0] == "classes.dex":
            return _read(b, e)
    return None


def classes_dex_value(data, ctx):
    """apk.classes_dex_<f> = dex.<f> of the APK's root classes.dex."""
    if data is None:
        return None
    ctx = dict(ctx or {})
    try:
        a = _apk(data)
        d = _classes_dex(*a) if a else None
    except (struct.error, ValueError, IndexError):
        return "none"
    if d is None:
        return "none"
    from .dex import dex_value
    ctx["field"] = (ctx.get("field") or "")[len("classes_dex_"):]
    ctx["fmt"] = "dex"
    return dex_value(d, ctx)
