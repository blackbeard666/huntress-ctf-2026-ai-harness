"""Android device artifacts (prebuilt, SPECULATIVE -- never GM-asked yet): `adb backup` .ab files, packages.xml
(text or ABX binary XML) and packages.list.

.ab (fmt android_backup, alias ab; BackupManagerService / FullBackup): a text header of 4 '\\n'-terminated lines
  "ANDROID BACKUP" / <version 1..5> / <compressed 0|1> / <encryption "none" | "AES-256">
then, when encrypted, 5 more lines (user password salt hex, master key checksum salt hex, PBKDF2 rounds, user key IV
hex, encrypted master key blob hex) and AES ciphertext (no password -> tar fields are None). Otherwise the payload is a
zlib stream (compressed=1, with 0x78 header) or raw bytes (compressed=0) holding a tar whose members are
`apps/<pkg>/_manifest`, `apps/<pkg>/{a,f,db,sp,r,ef,obb,k,c,d_*}/...`. _manifest (FullBackup.writeAppManifest) =
lines: manifest version, package name, versionCode, platform SDK_INT, installer package ('' if none), apk included
0|1, signature count, then each signature (Signature.toCharsString hex).
  backup_version / header_version: int; compressed: the stored 0/1 as int; is_compressed: bool; encryption: the stored
  text verbatim ("none" or "AES-256" -- note "none" is also the literal the GM uses for an absent field: same string);
  is_encrypted: bool; package_names: unique `apps/<pkg>/` names in tar order (JSON list); package_count; file_count /
  member_count / entry_count: number of tar members (adb backups carry no directory entries; we count every member);
  member_names: the tar names in order; manifest_* : the FIRST package's _manifest.

packages.xml (fmt packages_xml): text `<packages>` or Android 12+ ABX (`ABX\\0` magic, BinaryXmlSerializer: big-endian
token stream, interned strings u16 index / 0xFFFF + writeUTF). package_names (document order of <package name=>),
package_count, shared_user_names, version_sdk_version / database_version / fingerprint (the <version> element of the
internal volume, first one), first package's code_path / version_code / installer / user_id / primary_cpu_abi, and
first_install_time (attribute `it`, hex ms since the Unix epoch) -> *_utc ISO-8601 'YYYY-MM-DDTHH:MM:SSZ' (ms dropped,
same spelling as gzip/lnk *_utc); `ft` (timestamp) and `ut` (lastUpdateTime) likewise. ABX LONG/LONG_HEX attributes are
already integers. Wildcard `package_*` fields not covered: one package is addressed only as the first.

packages.list (fmt packages_list): one line per package `name uid debuggable dataDir seinfo gids...`
(PackageManagerService writePackageListLPr). package_names (file order), package_count, first line's uid /
debuggable (0/1 -> bool) / data_dir / seinfo. Wrong magic / truncated / not this format -> "none"."""
import datetime
import io
import re
import struct
import tarfile
import zlib

FIELDS = {
    ("android_backup", "backup_version"): "ab_value",
    ("android_backup", "header_version"): "ab_value",
    ("android_backup", "version"): "ab_value",
    ("android_backup", "format_version"): "ab_value",
    ("android_backup", "compressed"): "ab_value",
    ("android_backup", "header_compressed"): "ab_value",
    ("android_backup", "is_compressed"): "ab_value",
    ("android_backup", "encryption"): "ab_value",
    ("android_backup", "header_encryption"): "ab_value",
    ("android_backup", "encryption_algorithm"): "ab_value",
    ("android_backup", "is_encrypted"): "ab_value",
    ("android_backup", "encrypted"): "ab_value",
    ("android_backup", "pbkdf2_rounds"): "ab_value",
    ("android_backup", "user_password_salt_hex"): "ab_value",
    ("android_backup", "master_key_checksum_salt_hex"): "ab_value",
    ("android_backup", "user_key_iv_hex"): "ab_value",
    ("android_backup", "package_names"): "ab_value",
    ("android_backup", "packages"): "ab_value",
    ("android_backup", "app_package_names"): "ab_value",
    ("android_backup", "package_count"): "ab_value",
    ("android_backup", "number_of_packages"): "ab_value",
    ("android_backup", "file_count"): "ab_value",
    ("android_backup", "member_count"): "ab_value",
    ("android_backup", "entry_count"): "ab_value",
    ("android_backup", "tar_member_count"): "ab_value",
    ("android_backup", "number_of_files"): "ab_value",
    ("android_backup", "member_names"): "ab_value",
    ("android_backup", "file_names"): "ab_value",
    ("android_backup", "tar_member_names"): "ab_value",
    ("android_backup", "manifest_version"): "ab_value",
    ("android_backup", "manifest_package_name"): "ab_value",
    ("android_backup", "package_name"): "ab_value",
    ("android_backup", "manifest_version_code"): "ab_value",
    ("android_backup", "version_code"): "ab_value",
    ("android_backup", "manifest_platform_version"): "ab_value",
    ("android_backup", "platform_version"): "ab_value",
    ("android_backup", "manifest_sdk_int"): "ab_value",
    ("android_backup", "sdk_int"): "ab_value",
    ("android_backup", "manifest_installer"): "ab_value",
    ("android_backup", "installer"): "ab_value",
    ("android_backup", "installer_package_name"): "ab_value",
    ("android_backup", "manifest_apk_included"): "ab_value",
    ("android_backup", "apk_included"): "ab_value",
    ("android_backup", "manifest_signature_count"): "ab_value",
    ("android_backup", "signature_count"): "ab_value",
    ("android_backup", "manifest_signatures"): "ab_value",
    ("android_backup", "signatures"): "ab_value",
    ("ab", "backup_version"): "ab_value",
    ("ab", "header_version"): "ab_value",
    ("ab", "version"): "ab_value",
    ("ab", "format_version"): "ab_value",
    ("ab", "compressed"): "ab_value",
    ("ab", "header_compressed"): "ab_value",
    ("ab", "is_compressed"): "ab_value",
    ("ab", "encryption"): "ab_value",
    ("ab", "header_encryption"): "ab_value",
    ("ab", "encryption_algorithm"): "ab_value",
    ("ab", "is_encrypted"): "ab_value",
    ("ab", "encrypted"): "ab_value",
    ("ab", "pbkdf2_rounds"): "ab_value",
    ("ab", "user_password_salt_hex"): "ab_value",
    ("ab", "master_key_checksum_salt_hex"): "ab_value",
    ("ab", "user_key_iv_hex"): "ab_value",
    ("ab", "package_names"): "ab_value",
    ("ab", "packages"): "ab_value",
    ("ab", "app_package_names"): "ab_value",
    ("ab", "package_count"): "ab_value",
    ("ab", "number_of_packages"): "ab_value",
    ("ab", "file_count"): "ab_value",
    ("ab", "member_count"): "ab_value",
    ("ab", "entry_count"): "ab_value",
    ("ab", "tar_member_count"): "ab_value",
    ("ab", "number_of_files"): "ab_value",
    ("ab", "member_names"): "ab_value",
    ("ab", "file_names"): "ab_value",
    ("ab", "tar_member_names"): "ab_value",
    ("ab", "manifest_version"): "ab_value",
    ("ab", "manifest_package_name"): "ab_value",
    ("ab", "package_name"): "ab_value",
    ("ab", "manifest_version_code"): "ab_value",
    ("ab", "version_code"): "ab_value",
    ("ab", "manifest_platform_version"): "ab_value",
    ("ab", "platform_version"): "ab_value",
    ("ab", "manifest_sdk_int"): "ab_value",
    ("ab", "sdk_int"): "ab_value",
    ("ab", "manifest_installer"): "ab_value",
    ("ab", "installer"): "ab_value",
    ("ab", "installer_package_name"): "ab_value",
    ("ab", "manifest_apk_included"): "ab_value",
    ("ab", "apk_included"): "ab_value",
    ("ab", "manifest_signature_count"): "ab_value",
    ("ab", "signature_count"): "ab_value",
    ("ab", "manifest_signatures"): "ab_value",
    ("ab", "signatures"): "ab_value",
    ("packages_xml", "package_names"): "pkgxml_value",
    ("packages_xml", "packages"): "pkgxml_value",
    ("packages_xml", "package_count"): "pkgxml_value",
    ("packages_xml", "number_of_packages"): "pkgxml_value",
    ("packages_xml", "shared_user_names"): "pkgxml_value",
    ("packages_xml", "shared_user_count"): "pkgxml_value",
    ("packages_xml", "is_abx"): "pkgxml_value",
    ("packages_xml", "is_binary_xml"): "pkgxml_value",
    ("packages_xml", "xml_format"): "pkgxml_value",
    ("packages_xml", "version_sdk_version"): "pkgxml_value",
    ("packages_xml", "sdk_version"): "pkgxml_value",
    ("packages_xml", "version_database_version"): "pkgxml_value",
    ("packages_xml", "database_version"): "pkgxml_value",
    ("packages_xml", "version_fingerprint"): "pkgxml_value",
    ("packages_xml", "fingerprint"): "pkgxml_value",
    ("packages_xml", "code_paths"): "pkgxml_value",
    ("packages_xml", "installers"): "pkgxml_value",
    ("packages_xml", "package_name"): "pkgxml_value",
    ("packages_xml", "first_package_name"): "pkgxml_value",
    ("packages_xml", "code_path"): "pkgxml_value",
    ("packages_xml", "version_code"): "pkgxml_value",
    ("packages_xml", "installer"): "pkgxml_value",
    ("packages_xml", "installer_package_name"): "pkgxml_value",
    ("packages_xml", "user_id"): "pkgxml_value",
    ("packages_xml", "uid"): "pkgxml_value",
    ("packages_xml", "primary_cpu_abi"): "pkgxml_value",
    ("packages_xml", "first_install_time"): "pkgxml_value",
    ("packages_xml", "first_install_time_utc"): "pkgxml_value",
    ("packages_xml", "first_install_time_ms"): "pkgxml_value",
    ("packages_xml", "first_install_time_hex"): "pkgxml_value",
    ("packages_xml", "last_update_time"): "pkgxml_value",
    ("packages_xml", "last_update_time_utc"): "pkgxml_value",
    ("packages_xml", "timestamp"): "pkgxml_value",
    ("packages_xml", "timestamp_utc"): "pkgxml_value",
    ("packages_list", "package_names"): "pkglist_value",
    ("packages_list", "packages"): "pkglist_value",
    ("packages_list", "package_count"): "pkglist_value",
    ("packages_list", "number_of_packages"): "pkglist_value",
    ("packages_list", "package_name"): "pkglist_value",
    ("packages_list", "uid"): "pkglist_value",
    ("packages_list", "user_id"): "pkglist_value",
    ("packages_list", "debuggable"): "pkglist_value",
    ("packages_list", "is_debuggable"): "pkglist_value",
    ("packages_list", "debuggable_package_names"): "pkglist_value",
    ("packages_list", "data_dir"): "pkglist_value",
    ("packages_list", "seinfo"): "pkglist_value",
    ("packages_list", "data_dirs"): "pkglist_value",
    ("packages_list", "uids"): "pkglist_value",
}

_AB_MAGIC = b"ANDROID BACKUP\n"
_MAX_OUT = 64 << 20


# ---------------------------------------------------------------- .ab
def _ab_header(b):
    """(header lines, payload offset) or None."""
    if not b or not b.startswith(_AB_MAGIC):
        return None
    lines, off = [], 0
    for _ in range(4):
        j = b.find(b"\n", off)
        if j < 0 or j - off > 64:
            return None
        lines.append(b[off:j].decode("latin-1").strip())
        off = j + 1
    if not lines[1].isdigit() or lines[2] not in ("0", "1"):
        return None
    if lines[3].lower() != "none":
        for _ in range(5):
            j = b.find(b"\n", off)
            if j < 0 or j - off > 4096:
                break
            lines.append(b[off:j].decode("latin-1").strip())
            off = j + 1
    return lines, off


def _ab_tar(b, hdr):
    """[(name, type, data or None)] of the backup tar (stops cleanly at truncation), or None."""
    lines, off = hdr
    if lines[3].lower() != "none":
        return None
    payload = b[off:]
    if lines[2] == "1":
        try:
            d = zlib.decompressobj()
            payload = d.decompress(payload, _MAX_OUT)
        except zlib.error:
            return None
    out = []
    try:
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:") as tf:
            for m in tf:
                data = None
                if m.isfile() and m.name.endswith("/_manifest") and m.size < 1 << 20:
                    try:
                        f = tf.extractfile(m)
                        data = f.read() if f else None
                    except (tarfile.TarError, OSError, EOFError):
                        data = None
                out.append((m.name, m.type, data))
    except (tarfile.TarError, OSError, EOFError, ValueError):
        pass
    return out or None


def _manifest(members):
    for name, _t, data in members or ():
        if data is not None and name.startswith("apps/"):
            return data.decode("utf-8", "replace").split("\n")
    return None


def ab_value(data, ctx):
    try:
        return _ab_value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- defensive: never raise past the extractor
        return None


def _ab_value(b, field):
    if b is None:
        return None
    hdr = _ab_header(b)
    if hdr is None:
        return "none"
    lines = hdr[0]
    enc = lines[3]
    encrypted = enc.lower() != "none"
    if field in ("backup_version", "header_version", "version", "format_version"):
        return int(lines[1])
    if field in ("compressed", "header_compressed"):
        return int(lines[2])
    if field == "is_compressed":
        return lines[2] == "1"
    if field in ("encryption", "header_encryption", "encryption_algorithm"):
        return enc
    if field in ("is_encrypted", "encrypted"):
        return encrypted
    if field in ("user_password_salt_hex", "master_key_checksum_salt_hex", "pbkdf2_rounds", "user_key_iv_hex"):
        i = {"user_password_salt_hex": 4, "master_key_checksum_salt_hex": 5, "pbkdf2_rounds": 6,
             "user_key_iv_hex": 7}[field]
        if not encrypted or len(lines) <= i or not lines[i]:
            return "none"
        v = lines[i]
        if field == "pbkdf2_rounds":
            return int(v) if v.isdigit() else None
        return v.lower()
    members = _ab_tar(b, hdr)
    if members is None:
        return None              # encrypted (no password) or an undecodable payload: cannot answer
    if field in ("package_names", "packages", "app_package_names", "package_count", "number_of_packages"):
        seen = []
        for name, _t, _d in members:
            parts = name.split("/")
            if len(parts) >= 2 and parts[0] == "apps" and parts[1] and parts[1] not in seen:
                seen.append(parts[1])
        return seen if field in ("package_names", "packages", "app_package_names") else len(seen)
    if field in ("file_count", "member_count", "entry_count", "tar_member_count", "number_of_files"):
        return len(members)
    if field in ("member_names", "file_names", "tar_member_names"):
        return [n for n, _t, _d in members]
    man = _manifest(members)
    if man is None:
        return "none"
    idx = {"manifest_version": 0, "manifest_package_name": 1, "package_name": 1, "manifest_version_code": 2,
           "version_code": 2, "manifest_platform_version": 3, "platform_version": 3, "manifest_sdk_int": 3,
           "sdk_int": 3, "manifest_installer": 4, "installer": 4, "installer_package_name": 4,
           "manifest_apk_included": 5, "apk_included": 5, "manifest_signature_count": 6, "signature_count": 6}
    if field in idx:
        i = idx[field]
        if len(man) <= i:
            return "none"
        v = man[i].strip()
        if field.endswith("apk_included"):
            return v == "1"
        if i in (0, 2, 3, 6):
            return int(v) if re.fullmatch(r"-?\d+", v) else (v or "none")
        return v or "none"
    if field in ("manifest_signatures", "signatures"):
        if len(man) <= 6 or not man[6].strip().isdigit():
            return "none"
        n = int(man[6].strip())
        return [s.strip() for s in man[7:7 + n]]
    return None


# ---------------------------------------------------------------- packages.xml (text / ABX)
_ABX_MAGIC = b"ABX\x00"


def _abx_events(b):
    """[(kind, name, attrs)] with kind 'start'/'end' from an ABX stream (BinaryXmlSerializer), or None."""
    pos, n, pool, ev, attrs, cur = 4, len(b), [], [], None, None

    def u16():
        nonlocal pos
        v, = struct.unpack_from(">H", b, pos)
        pos += 2
        return v

    def utf():
        nonlocal pos
        ln = u16()
        s = b[pos:pos + ln]
        if len(s) != ln:
            raise ValueError("short")
        pos += ln
        return s.decode("utf-8", "replace")

    def interned():
        i = u16()
        if i == 0xFFFF:
            s = utf()
            pool.append(s)
            return s
        return pool[i]

    def flush():
        nonlocal cur, attrs
        if cur is not None:
            ev.append(("start", cur, attrs))
            cur, attrs = None, None

    try:
        while pos < n:
            t = b[pos]
            pos += 1
            tok, typ = t & 0x0F, t & 0xF0
            if tok == 15:            # ATTRIBUTE
                name = interned()
                if typ == 0x20:
                    v = utf()
                elif typ == 0x30:
                    v = interned()
                elif typ in (0x40, 0x50):
                    ln = u16()
                    raw = b[pos:pos + ln]
                    pos += ln
                    v = raw.hex()
                elif typ in (0x60, 0x70):
                    v, = struct.unpack_from(">i", b, pos)
                    pos += 4
                elif typ in (0x80, 0x90):
                    v, = struct.unpack_from(">q", b, pos)
                    pos += 8
                elif typ == 0xA0:
                    v, = struct.unpack_from(">f", b, pos)
                    pos += 4
                elif typ == 0xB0:
                    v, = struct.unpack_from(">d", b, pos)
                    pos += 8
                elif typ in (0xC0, 0xD0):
                    v = typ == 0xC0
                elif typ == 0x10:
                    v = None
                else:
                    break
                if attrs is not None:
                    attrs[name] = (v, typ)
                continue
            flush()
            if tok == 2:
                cur, attrs = interned(), {}
            elif tok == 3:
                ev.append(("end", interned(), None))
            elif tok in (0, 1):
                if typ == 0x20:
                    utf()
            elif tok in (4, 5, 6, 7, 8, 9, 10):
                if typ == 0x20:
                    utf()
                elif typ == 0x30:
                    interned()
            else:
                break
        flush()
    except (struct.error, IndexError, ValueError):
        flush()
    return ev


def _text_events(b):
    import xml.etree.ElementTree as ET
    ev = []
    try:
        for kind, el in ET.iterparse(io.BytesIO(b), events=("start",)):
            ev.append((kind, el.tag, {k: (v, 0x20) for k, v in el.attrib.items()}))
    except ET.ParseError:
        pass
    return ev


def _pkgxml(b):
    """(is_abx, [(tag, attrs)] start elements) or None when this is not a packages.xml."""
    if not b:
        return None
    if b.startswith(_ABX_MAGIC):
        ev, abx = _abx_events(b), True
    else:
        head = b[:4096].lstrip(b"\xef\xbb\xbf \t\r\n")
        if not head.startswith(b"<") or b"<packages" not in b[:8192]:
            return None
        ev, abx = _text_events(b), False
    starts = [(name, attrs) for kind, name, attrs in (ev or ()) if kind == "start"]
    if not starts or starts[0][0] != "packages":
        return None
    return abx, starts


def _attr_int(v):
    """An attribute as int: ABX LONG/INT already int; text: hex for LONG_HEX-style attrs handled by the caller."""
    val, typ = v
    if isinstance(val, int) and not isinstance(val, bool):
        return val
    return None


def _ms_attr(attrs, key):
    """Hex-ms timestamp attribute (`it`/`ft`/`ut`) -> int ms, or None."""
    if key not in attrs:
        return None
    val, typ = attrs[key]
    if isinstance(val, int) and not isinstance(val, bool):
        return val
    s = str(val).strip()
    if re.fullmatch(r"[0-9A-Fa-f]+", s):
        return int(s, 16)
    return None


def _utc_ms(ms):
    try:
        t = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=ms)
    except (OverflowError, ValueError):
        return None
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _s(v):
    val = v[0]
    if isinstance(val, bool):
        return "true" if val else "false"
    return str(val)


def pkgxml_value(data, ctx):
    try:
        return _pkgxml_value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001
        return None


def _pkgxml_value(b, field):
    if b is None:
        return None
    px = _pkgxml(b)
    if px is None:
        return "none"
    abx, starts = px
    if field in ("is_abx", "is_binary_xml"):
        return abx
    if field == "xml_format":
        return "abx" if abx else "text"
    pkgs = [a for t, a in starts if t == "package" and "name" in a]
    if field in ("package_names", "packages", "package_count", "number_of_packages"):
        names = [_s(a["name"]) for a in pkgs]
        return names if field in ("package_names", "packages") else len(names)
    if field in ("shared_user_names", "shared_user_count"):
        names = [_s(a["name"]) for t, a in starts if t == "shared-user" and "name" in a]
        return names if field == "shared_user_names" else len(names)
    if field in ("code_paths", "installers"):
        key = "codePath" if field == "code_paths" else "installer"
        return [_s(a[key]) for a in pkgs if key in a]
    vkey = {"version_sdk_version": "sdkVersion", "sdk_version": "sdkVersion", "version_database_version":
            "databaseVersion", "database_version": "databaseVersion", "version_fingerprint": "fingerprint",
            "fingerprint": "fingerprint"}.get(field)
    if vkey:
        for t, a in starts:
            if t == "version" and vkey in a:
                v = _attr_int(a[vkey])
                if v is not None:
                    return v
                s = _s(a[vkey]).strip()
                return int(s) if vkey != "fingerprint" and re.fullmatch(r"-?\d+", s) else s
        return "none"
    if not pkgs:
        return "none"
    p = pkgs[0]
    if field in ("package_name", "first_package_name"):
        return _s(p["name"])
    akey = {"code_path": "codePath", "installer": "installer", "installer_package_name": "installer",
            "primary_cpu_abi": "primaryCpuAbi", "version_code": "version", "user_id": "userId",
            "uid": "userId"}.get(field)
    if akey:
        if akey not in p:
            if akey == "userId" and "sharedUserId" in p:
                akey = "sharedUserId"
            else:
                return "none"
        v = _attr_int(p[akey])
        if v is not None:
            return v
        s = _s(p[akey]).strip()
        if akey in ("version", "userId", "sharedUserId") and re.fullmatch(r"-?\d+", s):
            return int(s)
        return s
    tkey = {"first_install_time": "it", "first_install_time_utc": "it", "first_install_time_ms": "it",
            "first_install_time_hex": "it", "last_update_time": "ut", "last_update_time_utc": "ut",
            "timestamp": "ft", "timestamp_utc": "ft"}.get(field)
    if tkey:
        ms = _ms_attr(p, tkey)
        if ms is None:
            return "none"
        if field.endswith("_ms"):
            return ms
        if field.endswith("_hex"):
            return "%x" % ms             # the stored spelling (Long.toHexString, lowercase, unpadded)
        return _utc_ms(ms)
    return None


# ---------------------------------------------------------------- packages.list
_PL_LINE = re.compile(r"^([A-Za-z0-9_.]+) (\d+) ([01]) (/\S*) (\S+)(?: (\S+))?")


def _pkglist(b):
    if not b or b[:1] in (b"<", b"\x00") or b.startswith(_ABX_MAGIC):
        return None
    try:
        text = b.decode("utf-8")
    except UnicodeDecodeError:
        return None
    rows = []
    for ln in text.splitlines():
        if not ln.strip():
            continue
        m = _PL_LINE.match(ln)
        if not m:
            return None
        rows.append(m.groups())
    return rows or None


def pkglist_value(data, ctx):
    try:
        return _pkglist_value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001
        return None


def _pkglist_value(b, field):
    if b is None:
        return None
    rows = _pkglist(b)
    if rows is None:
        return "none"
    if field in ("package_names", "packages"):
        return [r[0] for r in rows]
    if field in ("package_count", "number_of_packages"):
        return len(rows)
    if field == "debuggable_package_names":
        return [r[0] for r in rows if r[2] == "1"]
    if field == "data_dirs":
        return [r[3] for r in rows]
    if field == "uids":
        return [int(r[1]) for r in rows]
    r = rows[0]
    if field == "package_name":
        return r[0]
    if field in ("uid", "user_id"):
        return int(r[1])
    if field == "debuggable":
        return int(r[2])
    if field == "is_debuggable":
        return r[2] == "1"
    if field == "data_dir":
        return r[3]
    if field == "seinfo":
        return r[4]
    return None
