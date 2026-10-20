"""Apple property lists (binary `bplist00` and XML) + macOS plist artifacts (Info.plist, .webloc) (prebuilt,
SPECULATIVE -- never GM-asked yet). Format tokens: plist, bplist, macos, webloc, info_plist.

bplist00 layout: 8-byte magic `bplist00`, objects, offset table, 32-byte trailer = 5 unused + sort_version u8 +
offset_int_size u8 + object_ref_size u8 + num_objects u64 + top_object u64 + offset_table_offset u64 (big-endian).
Object marker high nibble: 0 null/bool, 1 int, 2 real, 3 date (f64 seconds since 2001-01-01 UTC), 4 data,
5 ascii, 6 utf16be, 8 uid, a array, d dict. Values come from stdlib plistlib (keeps the STORED dict order for both
binary and XML); trailer fields are read from the raw bytes. object_count = trailer num_objects (binary only; an
XML plist has no object table -> "none").
Rendering: strings verbatim; ints base-10; bools true/false; reals Python repr; dates ISO-8601 UTC
`YYYY-MM-DDTHH:MM:SSZ` (the plist's own XML <date> spelling); data lowercase hex; arrays/dicts compact JSON.
value_<key>: <key> is a path ('/' for nesting is not expressible in a GM field name, so path components are joined
by '_'); matching squashes every non-alphanumeric char and lowercases both sides (value_cf_bundle_identifier ==
value_cfbundleidentifier == CFBundleIdentifier). Not a plist / truncated / key absent -> "none"."""
import datetime
import io
import plistlib
import re
import struct

FIELDS = {
    ("plist", "top_level_keys"): "plist_value",
    ("plist", "root_keys"): "plist_value",
    ("plist", "keys"): "plist_value",
    ("plist", "top_level_key_count"): "plist_value",
    ("plist", "key_count"): "plist_value",
    ("plist", "root_type"): "plist_value",
    ("plist", "format"): "plist_value",
    ("plist", "plist_format"): "plist_value",
    ("plist", "is_binary"): "plist_value",
    ("plist", "object_count"): "plist_value",
    ("plist", "num_objects"): "plist_value",
    ("plist", "trailer_num_objects"): "plist_value",
    ("plist", "offset_int_size"): "plist_value",
    ("plist", "offset_size"): "plist_value",
    ("plist", "trailer_offset_int_size"): "plist_value",
    ("plist", "object_ref_size"): "plist_value",
    ("plist", "ref_size"): "plist_value",
    ("plist", "trailer_object_ref_size"): "plist_value",
    ("plist", "top_object"): "plist_value",
    ("plist", "top_object_index"): "plist_value",
    ("plist", "trailer_top_object"): "plist_value",
    ("plist", "offset_table_offset"): "plist_value",
    ("plist", "trailer_offset_table_offset"): "plist_value",
    ("plist", "version"): "plist_value",
    ("plist", "bplist_version"): "plist_value",
    ("plist", "value_*"): "plist_key",
    ("plist", "key_*"): "plist_key",
    ("plist", "cf_bundle_identifier"): "plist_named",
    ("plist", "bundle_identifier"): "plist_named",
    ("plist", "bundle_id"): "plist_named",
    ("plist", "cf_bundle_executable"): "plist_named",
    ("plist", "bundle_executable"): "plist_named",
    ("plist", "cf_bundle_short_version_string"): "plist_named",
    ("plist", "bundle_short_version_string"): "plist_named",
    ("plist", "short_version_string"): "plist_named",
    ("plist", "cf_bundle_version"): "plist_named",
    ("plist", "bundle_version"): "plist_named",
    ("plist", "cf_bundle_name"): "plist_named",
    ("plist", "bundle_name"): "plist_named",
    ("plist", "cf_bundle_display_name"): "plist_named",
    ("plist", "cf_bundle_package_type"): "plist_named",
    ("plist", "cf_bundle_development_region"): "plist_named",
    ("plist", "cf_bundle_info_dictionary_version"): "plist_named",
    ("plist", "cf_bundle_signature"): "plist_named",
    ("plist", "cf_bundle_icon_file"): "plist_named",
    ("plist", "ls_minimum_system_version"): "plist_named",
    ("plist", "minimum_system_version"): "plist_named",
    ("plist", "minimum_os_version"): "plist_named",
    ("plist", "ls_ui_element"): "plist_named",
    ("plist", "ls_background_only"): "plist_named",
    ("plist", "ns_human_readable_copyright"): "plist_named",
    ("plist", "ns_principal_class"): "plist_named",
    ("plist", "dt_platform_name"): "plist_named",
    ("plist", "dt_sdk_name"): "plist_named",
    ("plist", "dt_xcode"): "plist_named",
    ("plist", "build_machine_os_build"): "plist_named",
    ("plist", "label"): "plist_named",
    ("plist", "program"): "plist_named",
    ("plist", "program_arguments"): "plist_named",
    ("plist", "run_at_load"): "plist_named",
    ("plist", "keep_alive"): "plist_named",
    ("plist", "url"): "plist_named",
    ("plist", "webloc_url"): "plist_named",
    # the same fields under the other format tokens a question could use
    ("bplist", "top_level_keys"): "plist_value",
    ("bplist", "root_keys"): "plist_value",
    ("bplist", "keys"): "plist_value",
    ("bplist", "top_level_key_count"): "plist_value",
    ("bplist", "root_type"): "plist_value",
    ("bplist", "format"): "plist_value",
    ("bplist", "object_count"): "plist_value",
    ("bplist", "num_objects"): "plist_value",
    ("bplist", "trailer_num_objects"): "plist_value",
    ("bplist", "offset_int_size"): "plist_value",
    ("bplist", "offset_size"): "plist_value",
    ("bplist", "object_ref_size"): "plist_value",
    ("bplist", "ref_size"): "plist_value",
    ("bplist", "top_object"): "plist_value",
    ("bplist", "top_object_index"): "plist_value",
    ("bplist", "offset_table_offset"): "plist_value",
    ("bplist", "version"): "plist_value",
    ("bplist", "value_*"): "plist_key",
    ("bplist", "key_*"): "plist_key",
    ("bplist", "cf_bundle_identifier"): "plist_named",
    ("bplist", "cf_bundle_executable"): "plist_named",
    ("bplist", "cf_bundle_short_version_string"): "plist_named",
    ("bplist", "cf_bundle_version"): "plist_named",
    ("bplist", "ls_minimum_system_version"): "plist_named",
    ("bplist", "url"): "plist_named",
    ("macos", "top_level_keys"): "plist_value",
    ("macos", "plist_top_level_keys"): "plist_value",
    ("macos", "root_keys"): "plist_value",
    ("macos", "object_count"): "plist_value",
    ("macos", "plist_object_count"): "plist_value",
    ("macos", "plist_format"): "plist_value",
    ("macos", "value_*"): "plist_key",
    ("macos", "plist_value_*"): "plist_key",
    ("macos", "cf_bundle_identifier"): "plist_named",
    ("macos", "bundle_identifier"): "plist_named",
    ("macos", "bundle_id"): "plist_named",
    ("macos", "cf_bundle_executable"): "plist_named",
    ("macos", "bundle_executable"): "plist_named",
    ("macos", "cf_bundle_short_version_string"): "plist_named",
    ("macos", "short_version_string"): "plist_named",
    ("macos", "cf_bundle_version"): "plist_named",
    ("macos", "cf_bundle_name"): "plist_named",
    ("macos", "cf_bundle_display_name"): "plist_named",
    ("macos", "cf_bundle_package_type"): "plist_named",
    ("macos", "ls_minimum_system_version"): "plist_named",
    ("macos", "minimum_system_version"): "plist_named",
    ("macos", "ns_human_readable_copyright"): "plist_named",
    ("macos", "label"): "plist_named",
    ("macos", "program"): "plist_named",
    ("macos", "program_arguments"): "plist_named",
    ("macos", "run_at_load"): "plist_named",
    ("macos", "url"): "plist_named",
    ("macos", "webloc_url"): "plist_named",
    ("webloc", "url"): "plist_named",
    ("webloc", "target_url"): "plist_named",
    ("webloc", "top_level_keys"): "plist_value",
    ("webloc", "format"): "plist_value",
    ("webloc", "plist_format"): "plist_value",
    ("webloc", "value_*"): "plist_key",
    ("info_plist", "top_level_keys"): "plist_value",
    ("info_plist", "value_*"): "plist_key",
    ("info_plist", "cf_bundle_identifier"): "plist_named",
    ("info_plist", "bundle_identifier"): "plist_named",
    ("info_plist", "cf_bundle_executable"): "plist_named",
    ("info_plist", "cf_bundle_short_version_string"): "plist_named",
    ("info_plist", "cf_bundle_version"): "plist_named",
    ("info_plist", "cf_bundle_name"): "plist_named",
    ("info_plist", "ls_minimum_system_version"): "plist_named",
    ("info_plist", "minimum_os_version"): "plist_named",
}

# Field name -> the plist key it names, where the squashed field differs from the squashed key.
_NAMED = {"bundle_identifier": "CFBundleIdentifier", "bundle_id": "CFBundleIdentifier",
          "bundle_executable": "CFBundleExecutable", "bundle_short_version_string": "CFBundleShortVersionString",
          "short_version_string": "CFBundleShortVersionString", "bundle_version": "CFBundleVersion",
          "bundle_name": "CFBundleName", "minimum_system_version": "LSMinimumSystemVersion",
          "minimum_os_version": "MinimumOSVersion", "webloc_url": "URL", "target_url": "URL"}
_EPOCH_2001 = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)


def _sq(s):
    return re.sub(r"[^0-9a-z]", "", str(s).lower())


def trailer(b):
    """bplist00 trailer dict, or None (not a sane binary plist)."""
    if not isinstance(b, (bytes, bytearray)) or len(b) < 40 or bytes(b[:6]) != b"bplist":
        return None
    sort_v, osz, rsz, nobj, top, tbl = struct.unpack(">5xBBBQQQ", bytes(b[-32:]))
    if osz not in (1, 2, 4, 8) or rsz not in (1, 2, 4, 8) or not nobj or top >= nobj \
            or tbl < 8 or tbl + nobj * osz > len(b) - 32:
        return None
    return {"sort_version": sort_v, "offset_int_size": osz, "object_ref_size": rsz, "num_objects": nobj,
            "top_object": top, "offset_table_offset": tbl, "version": bytes(b[6:8]).decode("latin-1")}


def _strip(b):
    b = bytes(b)
    for bom in (b"\xef\xbb\xbf",):
        if b.startswith(bom):
            b = b[len(bom):]
    return b.lstrip()


def load(b):
    """(root object, 'binary'|'xml') or None. plistlib keeps the stored dict order."""
    if not isinstance(b, (bytes, bytearray)) or len(b) < 8:
        return None
    raw = bytes(b)
    if raw[:6] == b"bplist":
        if trailer(raw) is None:
            return None
        kind, fmt = "binary", plistlib.FMT_BINARY
    else:
        s = _strip(raw)
        if not (s.startswith(b"<?xml") or s.startswith(b"<!DOCTYPE plist") or s.startswith(b"<plist")) \
                or b"<plist" not in s[:4096]:
            return None
        raw, kind, fmt = s, "xml", plistlib.FMT_XML
    try:
        return plistlib.load(io.BytesIO(raw), fmt=fmt, dict_type=dict), kind
    except Exception:  # noqa: BLE001 -- malformed / truncated / hostile plist
        return None


def _jsonable(v):
    if isinstance(v, dict):
        return {str(k): _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, (bytes, bytearray)):
        return bytes(v).hex()
    if isinstance(v, datetime.datetime):
        return _date(v)
    if isinstance(v, plistlib.UID):
        return v.data
    return v


def _date(d):
    if d.tzinfo is None:   # plistlib returns naive UTC datetimes (2001-epoch seconds already converted)
        d = d.replace(tzinfo=datetime.timezone.utc)
    return d.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def render(v):
    """A typed value lib.meta.spell renders the GM way."""
    if isinstance(v, bool) or isinstance(v, (int, str)):
        return v
    if isinstance(v, float):
        return repr(v)
    if isinstance(v, datetime.datetime):
        return _date(v)
    if isinstance(v, plistlib.UID):
        return v.data
    if isinstance(v, (bytes, bytearray)):
        return bytes(v)
    if isinstance(v, (list, tuple, dict)):
        return _jsonable(v)
    return str(v)


def _find(root, want):
    """The value at the squashed path `want` (components joined by '_'), depth-first in stored order, else None.
    A direct top-level key wins over a nested path."""
    if isinstance(root, dict):
        for k, v in root.items():
            if _sq(k) == want:
                return (v,)
    stack = [("", root)]
    while stack:
        pre, node = stack.pop(0)
        items = node.items() if isinstance(node, dict) else enumerate(node) if isinstance(node, list) else ()
        for k, v in items:
            p = pre + _sq(k)
            if p == want:
                return (v,)
            if isinstance(v, (dict, list)) and want.startswith(p):
                stack.append((p, v))
    return None


def plist_value(data, ctx):
    """Structural fields: top-level keys, root type, format, bplist trailer numbers."""
    if data is None:
        return None
    try:
        field = ctx.get("field") or ""
        for p in ("trailer_", "plist_"):
            if field.startswith(p) and field not in ("plist_format",):
                field = field[len(p):]
        ld = load(data)
        if ld is None:
            return "none"
        root, kind = ld
        if field in ("top_level_keys", "root_keys", "keys"):
            return [str(k) for k in root] if isinstance(root, dict) else "none"
        if field in ("top_level_key_count", "key_count"):
            return len(root) if isinstance(root, dict) else "none"
        if field == "root_type":
            return {dict: "dict", list: "array", str: "string", bytes: "data", bool: "boolean", int: "integer",
                    float: "real", datetime.datetime: "date"}.get(type(root), type(root).__name__)
        if field in ("format", "plist_format"):
            return kind
        if field == "is_binary":
            return kind == "binary"
        t = trailer(data) if kind == "binary" else None
        if t is None:
            return "none"
        key = {"object_count": "num_objects", "num_objects": "num_objects", "offset_int_size": "offset_int_size",
               "offset_size": "offset_int_size", "object_ref_size": "object_ref_size", "ref_size": "object_ref_size",
               "top_object": "top_object", "top_object_index": "top_object",
               "offset_table_offset": "offset_table_offset", "version": "version",
               "bplist_version": "version"}.get(field)
        return t[key] if key else None
    except Exception:  # noqa: BLE001
        return None


def plist_key(data, ctx):
    """value_<path> / key_<path>: the value stored under that key (path components joined by '_')."""
    if data is None:
        return None
    try:
        ld = load(data)
        if ld is None:
            return "none"
        hit = _find(ld[0], _sq(ctx.get("param") or ""))
        return render(hit[0]) if hit else "none"
    except Exception:  # noqa: BLE001
        return None


def plist_named(data, ctx):
    """A well-known key named by the field (cf_bundle_identifier -> CFBundleIdentifier, url -> URL)."""
    if data is None:
        return None
    try:
        ld = load(data)
        if ld is None:
            return "none"
        field = ctx.get("field") or ""
        hit = _find(ld[0], _sq(_NAMED.get(field, field)))
        return render(hit[0]) if hit else "none"
    except Exception:  # noqa: BLE001
        return None

