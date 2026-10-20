"""Debian binary package (.deb) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

A .deb is an ar archive: "!<arch>\\n", then per member a 60-byte header -- name[16] mtime[12] uid[6] gid[6]
mode[8] size[10] "`\\n" (ASCII, space-padded; GNU names end with '/') -- and the data padded to an even offset.
Members in order: debian-binary ("2.0\\n"), control.tar[.gz|.xz|.zst|.bz2], data.tar[...]. The ./control file inside
control.tar is RFC-822 style "Key: value" with continuation lines starting with a space.
Values are returned exactly as stored in ./control (dpkg-deb -f spelling); folded continuation lines are joined with a
single space, except Description which is its synopsis (first line). Absent control key -> "none".
member_names = the ar member names in archive order (trailing '/' stripped, like `ar t`).
Not an ar archive / no debian-binary member -> "none" (a plain static library .a is a decoy)."""
import io
import re
import tarfile

FIELDS = {
    ("deb", "package"): "control_value",
    ("deb", "package_name"): "control_value",
    ("deb", "version"): "control_value",
    ("deb", "package_version"): "control_value",
    ("deb", "architecture"): "control_value",
    ("deb", "arch"): "control_value",
    ("deb", "maintainer"): "control_value",
    ("deb", "depends"): "control_value",
    ("deb", "pre_depends"): "control_value",
    ("deb", "recommends"): "control_value",
    ("deb", "suggests"): "control_value",
    ("deb", "conflicts"): "control_value",
    ("deb", "provides"): "control_value",
    ("deb", "replaces"): "control_value",
    ("deb", "section"): "control_value",
    ("deb", "priority"): "control_value",
    ("deb", "homepage"): "control_value",
    ("deb", "source"): "control_value",
    ("deb", "installed_size"): "control_value",
    ("deb", "description"): "control_value",
    ("deb", "original_maintainer"): "control_value",
    ("deb", "multi_arch"): "control_value",
    ("deb", "control_*"): "control_value",
    ("deb", "control_keys"): "control_keys",
    ("deb", "control_field_names"): "control_keys",
    ("deb", "member_names"): "member_names",
    ("deb", "ar_member_names"): "member_names",
    ("deb", "archive_member_names"): "member_names",
    ("deb", "member_count"): "member_count",
    ("deb", "ar_member_count"): "member_count",
    ("deb", "debian_binary"): "debian_binary",
    ("deb", "debian_binary_version"): "debian_binary",
    ("deb", "format_version"): "debian_binary",
    ("deb", "package_format_version"): "debian_binary",
    ("deb", "control_member_name"): "control_member_name",
    ("deb", "control_tar_name"): "control_member_name",
    ("deb", "control_archive_name"): "control_member_name",
    ("deb", "data_member_name"): "data_member_name",
    ("deb", "data_tar_name"): "data_member_name",
    ("deb", "data_archive_name"): "data_member_name",
    ("deb", "control_tar_member_names"): "control_tar_names",
    ("deb", "control_file_names"): "control_tar_names",
    ("deb", "control_files"): "control_tar_names",
}

# field -> control key when "_"->"-" + Title-Case would be wrong
_KEYS = {"package_name": "Package", "package_version": "Version", "arch": "Architecture"}


def ar_members(b):
    """[(name, data_bytes)] of an ar archive in stored order, or None."""
    if not b or bytes(b[:8]) != b"!<arch>\n":
        return None
    out, off, n = [], 8, len(b)
    while off + 60 <= n:
        h = bytes(b[off:off + 60])
        if h[58:60] != b"`\n":
            break
        name = h[:16].decode("latin-1").rstrip()
        try:
            size = int(h[48:58].decode("ascii").strip() or "0")
        except ValueError:
            break
        if name.endswith("/") and name != "/" and name != "//":
            name = name[:-1]
        off += 60
        out.append((name, bytes(b[off:off + size])))
        off += size + (size & 1)
    return out


def _deb_members(b):
    m = ar_members(b)
    if not m or not any(nm == "debian-binary" for nm, _ in m):
        return None
    return m


def _decompress(name, blob):
    if name.endswith(".gz"):
        import gzip
        return gzip.decompress(blob)
    if name.endswith(".xz") or name.endswith(".lzma"):
        import lzma
        return lzma.decompress(blob)
    if name.endswith(".bz2"):
        import bz2
        return bz2.decompress(blob)
    if name.endswith(".zst"):
        import zstandard
        with zstandard.ZstdDecompressor().stream_reader(io.BytesIO(blob)) as r:
            return r.read()
    return blob


def _member(m, prefix):
    for nm, blob in m:
        if nm.startswith(prefix):
            return nm, blob
    return None, None


def control_tar(b):
    m = _deb_members(b)
    if not m:
        return None
    nm, blob = _member(m, "control.tar")
    if nm is None:
        return None
    try:
        return tarfile.open(fileobj=io.BytesIO(_decompress(nm, blob)), mode="r:")
    except Exception:  # noqa: BLE001
        return None


def control_fields(b):
    """Ordered {Key: value} of ./control, or None (not a deb / unreadable control)."""
    tf = control_tar(b)
    if tf is None:
        return None
    try:
        ti = next((t for t in tf.getmembers() if t.isfile() and t.name.lstrip("./") == "control"), None)
        if ti is None:
            return None
        text = tf.extractfile(ti).read().decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None
    out, key = {}, None
    for line in text.splitlines():
        if line[:1] in (" ", "\t"):
            if key is not None and key != "Description":
                out[key] = (out[key] + " " + line.strip()).strip()
            continue
        mm = re.match(r"([^:\s]+):\s?(.*)$", line)
        if mm:
            key = mm.group(1)
            out.setdefault(key, mm.group(2).strip())
    return out


def _key_for(field):
    f = field[len("control_"):] if field.startswith("control_") else field
    return _KEYS.get(f) or "-".join(p.capitalize() for p in f.split("_"))


def control_value(data, ctx):
    if data is None:
        return None
    try:
        cf = control_fields(data)
        if cf is None:
            return "none"
        want = _key_for(ctx.get("field") or "").lower()
        for k, v in cf.items():
            if k.lower() == want:
                return v if v != "" else "none"
        return "none"
    except Exception:  # noqa: BLE001
        return None


def control_keys(data, ctx):
    if data is None:
        return None
    try:
        cf = control_fields(data)
        return list(cf) if cf is not None else "none"
    except Exception:  # noqa: BLE001
        return None


def member_names(data, ctx):
    if data is None:
        return None
    try:
        m = _deb_members(data)
        return [nm for nm, _ in m] if m else "none"
    except Exception:  # noqa: BLE001
        return None


def member_count(data, ctx):
    if data is None:
        return None
    try:
        m = _deb_members(data)
        return len(m) if m else "none"
    except Exception:  # noqa: BLE001
        return None


def debian_binary(data, ctx):
    if data is None:
        return None
    try:
        m = _deb_members(data)
        if not m:
            return "none"
        _, blob = _member(m, "debian-binary")
        return blob.decode("ascii", "replace").strip() or "none"
    except Exception:  # noqa: BLE001
        return None


def control_member_name(data, ctx):
    return _named(data, "control.tar")


def data_member_name(data, ctx):
    return _named(data, "data.tar")


def _named(data, prefix):
    if data is None:
        return None
    try:
        m = _deb_members(data)
        nm = _member(m, prefix)[0] if m else None
        return nm or "none"
    except Exception:  # noqa: BLE001
        return None


def control_tar_names(data, ctx):
    """Entries of control.tar in stored order, names verbatim (usually './', './control', './md5sums')."""
    if data is None:
        return None
    try:
        tf = control_tar(data)
        return [t.name for t in tf.getmembers()] if tf is not None else "none"
    except Exception:  # noqa: BLE001
        return None
