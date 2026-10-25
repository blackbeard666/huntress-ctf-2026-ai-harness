"""Windows registry hive VALUES and host identity labels (prebuilt, SPECULATIVE -- never GM-asked yet), under the
GM's D25 format word `registry` and its aliases (hive, regf, reg, ntuser, windows_registry).

D25 "Hive Mind" flavour: the hive's identity lives in ROOT VALUES separated from the host labels -- `Marker` REG_SZ
(`HUNTRESS-HIVE-4203` on the single solve, random hex on the timed sets) + `Ordinal` REG_DWORD stored INLINE
(4203 = the marker number). Walk (regf.py helpers, libregf spec): root nk -> value count u32 @nk+0x24, value list
offset u32 @nk+0x28 -> u32 cell offsets -> `vk` cells: name len u16 @+2, data size u32 @+4 (bit 31 = data inline in
the offset field), data offset @+8, type u32 @+0xc, flags u16 @+0x10 (1 = ASCII name), name @+0x14; `db` big data
when size > 16344. Root = base-block root cell (u32 @0x24 + 0x1000) when it is a KEY_HIVE_ENTRY nk, else the first
such nk found scanning the hbins (same fallback as registry_fmt.py).

Value data rendering (every field below): REG_SZ / EXPAND_SZ / LINK = UTF-16LE up to the first NUL; DWORD / QWORD /
DWORD_BIG_ENDIAN = base-10 int; MULTI_SZ = list (compact JSON, stored order, empty strings dropped); BINARY / NONE /
anything else = lowercase hex.
- root_value_<name>: the root key's value whose name matches <name> case-insensitively (underscores/punctuation
  ignored: root_value_install_date == InstallDate); root_value_<name>_type -> its REG_* type name. Absent -> "none".
- root_value_types: sorted list of "Name:REG_TYPE" for every root value ([] when none).
- value_<path>: a value anywhere in the tree. A backslash path in the question wins (last component = value name,
  the rest = root-relative key path, HKLM/HKCU prefixes dropped); else <path>'s underscore tokens are matched greedily
  against subkey names then a value name (punctuation-insensitive). "(default)"/"default" = the unnamed value.
- hive_type (first rule that matches the root's subkeys, case-insensitive): SYSTEM (ControlSet00N + Select),
  SOFTWARE (Microsoft + Classes), SAM (SAM\\Domains), SECURITY (Policy), NTUSER (Software + Environment|Console),
  USRCLASS (Local Settings, or root name ending _Classes), AMCACHE (Root\\InventoryApplicationFile|File), BCD
  (Objects + Description), else DEFAULT.
- computer_name: SYSTEM Select\\Current N -> ControlSet00N\\Control\\ComputerName\\ComputerName\\ComputerName (the
  CURRENT set, not ControlSet001 blindly; ActiveComputerName fallback). current_control_set: "ControlSet00N".
- timezone_key_name: same control set, Control\\TimeZoneInformation\\TimeZoneKeyName (StandardName for *_standard_*).
- product_name / registered_owner / registered_organization / current_build / display_version / edition_id / ...:
  SOFTWARE Microsoft\\Windows NT\\CurrentVersion\\<CamelCase>. install_date(_utc): InstallDate REG_DWORD = unix
  seconds -> 'YYYY-MM-DDTHH:MM:SSZ' (house ISO spelling); install_date_unix = the raw int; install_time_utc =
  InstallTime REG_QWORD FILETIME -> same ISO spelling.
- machine_sid: SAM Domains\\Account value `V`, last 12 bytes = 3 LE u32 sub-authorities -> S-1-5-21-a-b-c; SECURITY
  hive fallback: Policy\\PolAcDmS default value (a binary SID).
Not "regf" -> "none"; regf without a readable root -> None; a label the hive type does not carry -> "none"."""
import datetime
import re
import struct

from .regf import _asked_path, _nk, _subkeys, _values, base_block

FIELDS = {
    ("registry", "root_value_*"): "root_value",
    ("registry", "root_key_value_*"): "root_value",
    ("registry", "root_value_types"): "root_value_types",
    ("registry", "root_key_value_types"): "root_value_types",
    ("registry", "hive_root_value_types"): "root_value_types",
    ("registry", "value_*"): "path_value",
    ("registry", "key_value_*"): "path_value",
    ("registry", "hive_type"): "hive_type",
    ("registry", "hive_kind"): "hive_type",
    ("registry", "computer_name"): "computer_name",
    ("registry", "hostname"): "computer_name",
    ("registry", "host_name"): "computer_name",
    ("registry", "active_computer_name"): "computer_name",
    ("registry", "timezone_key_name"): "timezone",
    ("registry", "time_zone_key_name"): "timezone",
    ("registry", "timezone_standard_name"): "timezone",
    ("registry", "timezone_name"): "timezone",
    ("registry", "time_zone"): "timezone",
    ("registry", "timezone"): "timezone",
    ("registry", "current_control_set"): "current_control_set",
    ("registry", "select_current"): "current_control_set",
    ("registry", "product_name"): "os_value",
    ("registry", "os_product_name"): "os_value",
    ("registry", "os_product"): "os_value",
    ("registry", "install_date_utc"): "os_value",
    ("registry", "install_date"): "os_value",
    ("registry", "install_date_unix"): "os_value",
    ("registry", "install_time_utc"): "os_value",
    ("registry", "registered_owner"): "os_value",
    ("registry", "registered_organization"): "os_value",
    ("registry", "current_build"): "os_value",
    ("registry", "current_build_number"): "os_value",
    ("registry", "current_version"): "os_value",
    ("registry", "display_version"): "os_value",
    ("registry", "edition_id"): "os_value",
    ("registry", "product_id"): "os_value",
    ("registry", "build_lab"): "os_value",
    ("registry", "release_id"): "os_value",
    ("registry", "machine_sid"): "machine_sid",
    ("registry", "computer_sid"): "machine_sid",
    ("registry", "domain_sid"): "machine_sid",
    ("registry", "account_domain_sid"): "machine_sid",
    ("hive", "root_value_*"): "root_value",
    ("hive", "root_key_value_*"): "root_value",
    ("hive", "root_value_types"): "root_value_types",
    ("hive", "root_key_value_types"): "root_value_types",
    ("hive", "hive_root_value_types"): "root_value_types",
    ("hive", "value_*"): "path_value",
    ("hive", "key_value_*"): "path_value",
    ("hive", "hive_type"): "hive_type",
    ("hive", "hive_kind"): "hive_type",
    ("hive", "computer_name"): "computer_name",
    ("hive", "hostname"): "computer_name",
    ("hive", "host_name"): "computer_name",
    ("hive", "active_computer_name"): "computer_name",
    ("hive", "timezone_key_name"): "timezone",
    ("hive", "time_zone_key_name"): "timezone",
    ("hive", "timezone_standard_name"): "timezone",
    ("hive", "timezone_name"): "timezone",
    ("hive", "time_zone"): "timezone",
    ("hive", "timezone"): "timezone",
    ("hive", "current_control_set"): "current_control_set",
    ("hive", "select_current"): "current_control_set",
    ("hive", "product_name"): "os_value",
    ("hive", "os_product_name"): "os_value",
    ("hive", "os_product"): "os_value",
    ("hive", "install_date_utc"): "os_value",
    ("hive", "install_date"): "os_value",
    ("hive", "install_date_unix"): "os_value",
    ("hive", "install_time_utc"): "os_value",
    ("hive", "registered_owner"): "os_value",
    ("hive", "registered_organization"): "os_value",
    ("hive", "current_build"): "os_value",
    ("hive", "current_build_number"): "os_value",
    ("hive", "current_version"): "os_value",
    ("hive", "display_version"): "os_value",
    ("hive", "edition_id"): "os_value",
    ("hive", "product_id"): "os_value",
    ("hive", "build_lab"): "os_value",
    ("hive", "release_id"): "os_value",
    ("hive", "machine_sid"): "machine_sid",
    ("hive", "computer_sid"): "machine_sid",
    ("hive", "domain_sid"): "machine_sid",
    ("hive", "account_domain_sid"): "machine_sid",
    ("regf", "root_value_*"): "root_value",
    ("regf", "root_key_value_*"): "root_value",
    ("regf", "root_value_types"): "root_value_types",
    ("regf", "root_key_value_types"): "root_value_types",
    ("regf", "hive_root_value_types"): "root_value_types",
    ("regf", "value_*"): "path_value",
    ("regf", "key_value_*"): "path_value",
    ("regf", "hive_type"): "hive_type",
    ("regf", "hive_kind"): "hive_type",
    ("regf", "computer_name"): "computer_name",
    ("regf", "hostname"): "computer_name",
    ("regf", "host_name"): "computer_name",
    ("regf", "active_computer_name"): "computer_name",
    ("regf", "timezone_key_name"): "timezone",
    ("regf", "time_zone_key_name"): "timezone",
    ("regf", "timezone_standard_name"): "timezone",
    ("regf", "timezone_name"): "timezone",
    ("regf", "time_zone"): "timezone",
    ("regf", "timezone"): "timezone",
    ("regf", "current_control_set"): "current_control_set",
    ("regf", "select_current"): "current_control_set",
    ("regf", "product_name"): "os_value",
    ("regf", "os_product_name"): "os_value",
    ("regf", "os_product"): "os_value",
    ("regf", "install_date_utc"): "os_value",
    ("regf", "install_date"): "os_value",
    ("regf", "install_date_unix"): "os_value",
    ("regf", "install_time_utc"): "os_value",
    ("regf", "registered_owner"): "os_value",
    ("regf", "registered_organization"): "os_value",
    ("regf", "current_build"): "os_value",
    ("regf", "current_build_number"): "os_value",
    ("regf", "current_version"): "os_value",
    ("regf", "display_version"): "os_value",
    ("regf", "edition_id"): "os_value",
    ("regf", "product_id"): "os_value",
    ("regf", "build_lab"): "os_value",
    ("regf", "release_id"): "os_value",
    ("regf", "machine_sid"): "machine_sid",
    ("regf", "computer_sid"): "machine_sid",
    ("regf", "domain_sid"): "machine_sid",
    ("regf", "account_domain_sid"): "machine_sid",
    ("reg", "root_value_*"): "root_value",
    ("reg", "root_key_value_*"): "root_value",
    ("reg", "root_value_types"): "root_value_types",
    ("reg", "root_key_value_types"): "root_value_types",
    ("reg", "hive_root_value_types"): "root_value_types",
    ("reg", "value_*"): "path_value",
    ("reg", "key_value_*"): "path_value",
    ("reg", "hive_type"): "hive_type",
    ("reg", "hive_kind"): "hive_type",
    ("reg", "computer_name"): "computer_name",
    ("reg", "hostname"): "computer_name",
    ("reg", "host_name"): "computer_name",
    ("reg", "active_computer_name"): "computer_name",
    ("reg", "timezone_key_name"): "timezone",
    ("reg", "time_zone_key_name"): "timezone",
    ("reg", "timezone_standard_name"): "timezone",
    ("reg", "timezone_name"): "timezone",
    ("reg", "time_zone"): "timezone",
    ("reg", "timezone"): "timezone",
    ("reg", "current_control_set"): "current_control_set",
    ("reg", "select_current"): "current_control_set",
    ("reg", "product_name"): "os_value",
    ("reg", "os_product_name"): "os_value",
    ("reg", "os_product"): "os_value",
    ("reg", "install_date_utc"): "os_value",
    ("reg", "install_date"): "os_value",
    ("reg", "install_date_unix"): "os_value",
    ("reg", "install_time_utc"): "os_value",
    ("reg", "registered_owner"): "os_value",
    ("reg", "registered_organization"): "os_value",
    ("reg", "current_build"): "os_value",
    ("reg", "current_build_number"): "os_value",
    ("reg", "current_version"): "os_value",
    ("reg", "display_version"): "os_value",
    ("reg", "edition_id"): "os_value",
    ("reg", "product_id"): "os_value",
    ("reg", "build_lab"): "os_value",
    ("reg", "release_id"): "os_value",
    ("reg", "machine_sid"): "machine_sid",
    ("reg", "computer_sid"): "machine_sid",
    ("reg", "domain_sid"): "machine_sid",
    ("reg", "account_domain_sid"): "machine_sid",
    ("ntuser", "root_value_*"): "root_value",
    ("ntuser", "root_key_value_*"): "root_value",
    ("ntuser", "root_value_types"): "root_value_types",
    ("ntuser", "root_key_value_types"): "root_value_types",
    ("ntuser", "hive_root_value_types"): "root_value_types",
    ("ntuser", "value_*"): "path_value",
    ("ntuser", "key_value_*"): "path_value",
    ("ntuser", "hive_type"): "hive_type",
    ("ntuser", "hive_kind"): "hive_type",
    ("ntuser", "computer_name"): "computer_name",
    ("ntuser", "hostname"): "computer_name",
    ("ntuser", "host_name"): "computer_name",
    ("ntuser", "active_computer_name"): "computer_name",
    ("ntuser", "timezone_key_name"): "timezone",
    ("ntuser", "time_zone_key_name"): "timezone",
    ("ntuser", "timezone_standard_name"): "timezone",
    ("ntuser", "timezone_name"): "timezone",
    ("ntuser", "time_zone"): "timezone",
    ("ntuser", "timezone"): "timezone",
    ("ntuser", "current_control_set"): "current_control_set",
    ("ntuser", "select_current"): "current_control_set",
    ("ntuser", "product_name"): "os_value",
    ("ntuser", "os_product_name"): "os_value",
    ("ntuser", "os_product"): "os_value",
    ("ntuser", "install_date_utc"): "os_value",
    ("ntuser", "install_date"): "os_value",
    ("ntuser", "install_date_unix"): "os_value",
    ("ntuser", "install_time_utc"): "os_value",
    ("ntuser", "registered_owner"): "os_value",
    ("ntuser", "registered_organization"): "os_value",
    ("ntuser", "current_build"): "os_value",
    ("ntuser", "current_build_number"): "os_value",
    ("ntuser", "current_version"): "os_value",
    ("ntuser", "display_version"): "os_value",
    ("ntuser", "edition_id"): "os_value",
    ("ntuser", "product_id"): "os_value",
    ("ntuser", "build_lab"): "os_value",
    ("ntuser", "release_id"): "os_value",
    ("ntuser", "machine_sid"): "machine_sid",
    ("ntuser", "computer_sid"): "machine_sid",
    ("ntuser", "domain_sid"): "machine_sid",
    ("ntuser", "account_domain_sid"): "machine_sid",
    ("windows_registry", "root_value_*"): "root_value",
    ("windows_registry", "root_key_value_*"): "root_value",
    ("windows_registry", "root_value_types"): "root_value_types",
    ("windows_registry", "root_key_value_types"): "root_value_types",
    ("windows_registry", "hive_root_value_types"): "root_value_types",
    ("windows_registry", "value_*"): "path_value",
    ("windows_registry", "key_value_*"): "path_value",
    ("windows_registry", "hive_type"): "hive_type",
    ("windows_registry", "hive_kind"): "hive_type",
    ("windows_registry", "computer_name"): "computer_name",
    ("windows_registry", "hostname"): "computer_name",
    ("windows_registry", "host_name"): "computer_name",
    ("windows_registry", "active_computer_name"): "computer_name",
    ("windows_registry", "timezone_key_name"): "timezone",
    ("windows_registry", "time_zone_key_name"): "timezone",
    ("windows_registry", "timezone_standard_name"): "timezone",
    ("windows_registry", "timezone_name"): "timezone",
    ("windows_registry", "time_zone"): "timezone",
    ("windows_registry", "timezone"): "timezone",
    ("windows_registry", "current_control_set"): "current_control_set",
    ("windows_registry", "select_current"): "current_control_set",
    ("windows_registry", "product_name"): "os_value",
    ("windows_registry", "os_product_name"): "os_value",
    ("windows_registry", "os_product"): "os_value",
    ("windows_registry", "install_date_utc"): "os_value",
    ("windows_registry", "install_date"): "os_value",
    ("windows_registry", "install_date_unix"): "os_value",
    ("windows_registry", "install_time_utc"): "os_value",
    ("windows_registry", "registered_owner"): "os_value",
    ("windows_registry", "registered_organization"): "os_value",
    ("windows_registry", "current_build"): "os_value",
    ("windows_registry", "current_build_number"): "os_value",
    ("windows_registry", "current_version"): "os_value",
    ("windows_registry", "display_version"): "os_value",
    ("windows_registry", "edition_id"): "os_value",
    ("windows_registry", "product_id"): "os_value",
    ("windows_registry", "build_lab"): "os_value",
    ("windows_registry", "release_id"): "os_value",
    ("windows_registry", "machine_sid"): "machine_sid",
    ("windows_registry", "computer_sid"): "machine_sid",
    ("windows_registry", "domain_sid"): "machine_sid",
    ("windows_registry", "account_domain_sid"): "machine_sid",
}


_TYPES = {0: "REG_NONE", 1: "REG_SZ", 2: "REG_EXPAND_SZ", 3: "REG_BINARY", 4: "REG_DWORD", 5: "REG_DWORD_BIG_ENDIAN",
          6: "REG_LINK", 7: "REG_MULTI_SZ", 8: "REG_RESOURCE_LIST", 9: "REG_FULL_RESOURCE_DESCRIPTOR",
          10: "REG_RESOURCE_REQUIREMENTS_LIST", 11: "REG_QWORD"}
# root_value_<x> params that are really list/count fields of other modules (never a value lookup)
_RESERVED = {"count", "names", "types", "list", "data", "names_sorted", "count_total"}


def _norm(s):
    return re.sub(r"[^0-9a-z]", "", (s or "").lower())


def _flags(b, off):
    p = 0x1000 + off + 4
    return struct.unpack_from("<H", b, p + 2)[0] if 0 <= off and p + 4 <= len(b) else 0


def _root(b):
    h = base_block(b)
    if h is None:
        return None, None
    k = _nk(b, h["root"]) if h["root"] < len(b) else None
    if k is not None and _flags(b, h["root"]) & 0x04:
        return h, k
    pos = b.find(b"nk", 0x1020)
    while pos != -1:
        off = pos - 4 - 0x1000
        if off % 8 == 0 and _flags(b, off) & 0x04:
            k2 = _nk(b, off)
            if k2 is not None:
                return h, k2
        pos = b.find(b"nk", pos + 1)
    return h, k


def _render(typ, data):
    if typ in (1, 2, 6):
        if len(data) % 2:
            data = data[:-1]
        return data.decode("utf-16-le", "replace").split("\x00", 1)[0]
    if typ == 4 and len(data) >= 4:
        return struct.unpack_from("<I", data)[0]
    if typ == 5 and len(data) >= 4:
        return struct.unpack_from(">I", data)[0]
    if typ == 11 and len(data) >= 8:
        return struct.unpack_from("<Q", data)[0]
    if typ == 7:
        if len(data) % 2:
            data = data[:-1]
        return [x for x in data.decode("utf-16-le", "replace").split("\x00") if x]
    return bytes(data).hex()


def _child(b, k, name):
    n = _norm(name)
    for c in _subkeys(b, k):
        if c["name"].lower() == name.lower() or _norm(c["name"]) == n:
            return c
    return None


def _key(b, k, path):
    for part in path:
        if k is None:
            return None
        k = _child(b, k, part)
    return k


def _value(b, k, name):
    """(type, data) of `k`'s value `name` (exact case-insensitive, then punctuation-insensitive), or None."""
    if k is None:
        return None
    vals = _values(b, k)
    want = "" if name.lower() in ("(default)", "default", "@") else name
    for vn, vt, vd in vals:
        if vn.lower() == want.lower():
            return vt, vd
    n = _norm(want)
    for vn, vt, vd in vals:
        if n and _norm(vn) == n:
            return vt, vd
    return None


def _guard(fn):
    def run(data, ctx):
        if data is None:
            return None
        try:
            data = bytes(data)
            h, root = _root(data)
            if h is None:
                return "none"
            if root is None:
                return None
            return fn(data, root, ctx)
        except Exception:  # noqa: BLE001 - truncated / malformed hive
            return None
    run.__name__ = fn.__name__
    return run


@_guard
def root_value(b, root, ctx):
    """root_value_<name>: a root value's data; root_value_<name>_type: its REG_* type name."""
    p = (ctx.get("param") or "").strip("_")
    if not p or p in _RESERVED:
        return None
    v = _value(b, root, p)
    if v is not None:
        return _render(*v)
    if p.endswith("_type"):
        v = _value(b, root, p[:-5])
        if v is not None:
            return _TYPES.get(v[0], "REG_UNKNOWN_%d" % v[0])
    return "none"


@_guard
def root_value_types(b, root, ctx):
    return sorted("%s:%s" % (vn, _TYPES.get(vt, "REG_UNKNOWN_%d" % vt)) for vn, vt, vd in _values(b, root))


def _tok_walk(b, k, toks, depth=0):
    """Greedy match of underscore tokens onto subkey names then a value name; (type, data) or None."""
    if k is None or not toks or depth > 12:
        return None
    v = _value(b, k, "".join(toks))
    if v is not None:
        return v
    subs = _subkeys(b, k)
    for i in range(len(toks) - 1, 0, -1):
        n = "".join(toks[:i])
        for c in subs:
            if _norm(c["name"]) == n:
                r = _tok_walk(b, c, toks[i:], depth + 1)
                if r is not None:
                    return r
    return None


@_guard
def path_value(b, root, ctx):
    """value_<path>: a value anywhere in the tree (question backslash path first, else the field's tokens)."""
    path = _asked_path(ctx)
    if path and path[0].lower() == root["name"].lower():
        path = path[1:]
    if len(path) >= 2 or (path and _value(b, root, path[0]) is not None):
        v = _value(b, _key(b, root, path[:-1]), path[-1])
        if v is not None:
            return _render(*v)
        v = _value(b, _key(b, root, path), ctx.get("param") or "")
        if v is not None:
            return _render(*v)
    p = (ctx.get("param") or "").strip("_")
    if not p or p in _RESERVED:
        return None
    v = _tok_walk(b, root, [_norm(t) for t in p.split("_") if _norm(t)])
    return _render(*v) if v is not None else "none"


def _names(b, k):
    return {c["name"].lower(): c for c in _subkeys(b, k)}


def _hive_type(b, root):
    s = _names(b, root)
    if any(re.fullmatch(r"controlset\d{3}", n) for n in s) and "select" in s:
        return "SYSTEM"
    if "microsoft" in s and "classes" in s:
        return "SOFTWARE"
    if "sam" in s and _child(b, s["sam"], "Domains") is not None:
        return "SAM"
    if "policy" in s:
        return "SECURITY"
    if "software" in s and ("environment" in s or "console" in s):
        return "NTUSER"
    if "local settings" in s or root["name"].lower().endswith("_classes"):
        return "USRCLASS"
    if "root" in s and ({"inventoryapplicationfile", "file"} & set(_names(b, s["root"]))):
        return "AMCACHE"
    if "objects" in s and "description" in s:
        return "BCD"
    return "DEFAULT"


@_guard
def hive_type(b, root, ctx):
    return _hive_type(b, root)


def _control_set(b, root):
    """The current ControlSet00N nk (Select\\Current, else Default, else the lowest ControlSet), or None."""
    sel = _child(b, root, "Select")
    for name in ("Current", "Default"):
        v = _value(b, sel, name) if sel is not None else None
        if v is not None and v[0] == 4 and len(v[1]) >= 4:
            cs = _child(b, root, "ControlSet%03d" % struct.unpack_from("<I", v[1])[0])
            if cs is not None:
                return cs
    sets = sorted((c for c in _subkeys(b, root) if re.fullmatch(r"(?i)controlset\d{3}", c["name"])),
                  key=lambda c: c["name"].lower())
    return sets[0] if sets else _child(b, root, "CurrentControlSet")


@_guard
def current_control_set(b, root, ctx):
    cs = _control_set(b, root)
    return cs["name"] if cs is not None else "none"


def _cs_value(b, root, keys, names):
    cs = _control_set(b, root)
    for kp in keys:
        k = _key(b, cs, kp) if cs is not None else None
        for n in names:
            v = _value(b, k, n)
            if v is not None:
                return _render(*v)
    return "none"


@_guard
def computer_name(b, root, ctx):
    if (ctx.get("field") or "").startswith("active_"):
        return _cs_value(b, root, [("Control", "ComputerName", "ActiveComputerName")], ["ComputerName"])
    return _cs_value(b, root, [("Control", "ComputerName", "ComputerName"),
                                ("Control", "ComputerName", "ActiveComputerName")], ["ComputerName"])


@_guard
def timezone(b, root, ctx):
    names = ["StandardName"] if "standard" in (ctx.get("field") or "") else ["TimeZoneKeyName", "StandardName"]
    return _cs_value(b, root, [("Control", "TimeZoneInformation")], names)


_OS = {"product_name": "ProductName", "os_product_name": "ProductName", "os_product": "ProductName",
       "install_date_utc": "InstallDate", "install_date": "InstallDate", "install_date_unix": "InstallDate",
       "install_time_utc": "InstallTime", "current_build": "CurrentBuild", "current_build_number": "CurrentBuildNumber"}


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


@_guard
def os_value(b, root, ctx):
    f = ctx.get("field") or ""
    name = _OS.get(f) or "".join(p.capitalize() for p in f.split("_"))
    cv = _key(b, root, ("Microsoft", "Windows NT", "CurrentVersion")) or \
        _key(b, root, ("Software", "Microsoft", "Windows NT", "CurrentVersion"))
    v = _value(b, cv, name)
    if v is None and name == "CurrentBuild":
        v = _value(b, cv, "CurrentBuildNumber")
    if v is None:
        return "none"
    val = _render(*v)
    if name == "InstallDate" and isinstance(val, int) and f != "install_date_unix":
        return _iso(datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=val))   # unix seconds, UTC
    if name == "InstallTime" and isinstance(val, int):
        return _iso(datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=val // 10))   # FILETIME
    return val


def _sid(raw):
    """Binary SID -> 'S-1-...', or None."""
    if len(raw) < 8 or raw[0] != 1 or len(raw) < 8 + 4 * raw[1]:
        return None
    auth = int.from_bytes(raw[2:8], "big")
    subs = struct.unpack_from("<%dI" % raw[1], raw, 8)
    return "S-1-%d" % auth + "".join("-%d" % s for s in subs)


@_guard
def machine_sid(b, root, ctx):
    acct = _key(b, root, ("SAM", "Domains", "Account"))
    v = _value(b, acct, "V")
    if v is not None and len(v[1]) >= 12:
        return "S-1-5-21-%d-%d-%d" % struct.unpack_from("<III", v[1], len(v[1]) - 12)
    v = _value(b, _key(b, root, ("Policy", "PolAcDmS")), "")
    if v is not None:
        return _sid(v[1]) or "none"
    return "none"
