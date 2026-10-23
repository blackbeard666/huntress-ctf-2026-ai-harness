""".NET single-file bundle fields (prebuilt, SPECULATIVE -- never GM-asked yet). fmt dotnet_bundle, aliases
singlefile / apphost.

A single-file app = the apphost (ELF/PE/Mach-O) + appended files + a bundle manifest. The apphost carries the
dotnet/runtime `bundle_marker` placeholder: u64 LE header offset followed by the 32-byte SHA-256 signature
8b1202b9...24b36aae (verified against the installed SDK's apphost/singlefilehost and Microsoft.NET.HostModel.dll;
an unbundled apphost keeps offset 0 -> "none"). Manifest at that offset (src/native/corehost/bundle/header.cpp):
major u32, minor u32, file count i32, bundle id (7-bit-length string); v2+ (.NET 5): deps.json offset/size i64,
runtimeconfig.json offset/size i64, flags u64; then per entry offset i64, size i64, [v6+ (.NET 6): compressed size
i64, raw-deflate when non-zero], type u8 (0 unknown, 1 assembly, 2 native, 3 deps.json, 4 runtimeconfig.json,
5 symbols), relative path string. bundle_version is "major.minor" ("6.0" for .NET 6..10).
runtimeconfig fields read the bundled *.runtimeconfig.json, or the member itself when it IS a runtimeconfig.json.
main_assembly = the type-1 entry named after the apphost (member name sans .exe), else after the runtimeconfig
(`X.runtimeconfig.json` -> X.dll), else the first type-1 entry."""
import json
import struct
import zlib

FIELDS = {
    ("dotnet_bundle", "bundle_version"): "bundle_value",
    ("dotnet_bundle", "bundle_major_version"): "bundle_value",
    ("dotnet_bundle", "major_version"): "bundle_value",
    ("dotnet_bundle", "bundle_minor_version"): "bundle_value",
    ("dotnet_bundle", "minor_version"): "bundle_value",
    ("dotnet_bundle", "header_offset"): "bundle_value",
    ("dotnet_bundle", "bundle_header_offset"): "bundle_value",
    ("dotnet_bundle", "manifest_offset"): "bundle_value",
    ("dotnet_bundle", "bundle_id"): "bundle_value",
    ("dotnet_bundle", "file_count"): "bundle_value",
    ("dotnet_bundle", "entry_count"): "bundle_value",
    ("dotnet_bundle", "bundle_file_count"): "bundle_value",
    ("dotnet_bundle", "number_of_files"): "bundle_value",
    ("dotnet_bundle", "file_names"): "bundle_value",
    ("dotnet_bundle", "entry_names"): "bundle_value",
    ("dotnet_bundle", "member_names"): "bundle_value",
    ("dotnet_bundle", "bundle_file_names"): "bundle_value",
    ("dotnet_bundle", "file_paths"): "bundle_value",
    ("dotnet_bundle", "entry_types"): "bundle_value",
    ("dotnet_bundle", "file_types"): "bundle_value",
    ("dotnet_bundle", "assembly_names"): "bundle_value",
    ("dotnet_bundle", "main_assembly"): "bundle_value",
    ("dotnet_bundle", "main_assembly_name"): "bundle_value",
    ("dotnet_bundle", "entry_assembly"): "bundle_value",
    ("dotnet_bundle", "deps_json_offset"): "bundle_value",
    ("dotnet_bundle", "deps_json_size"): "bundle_value",
    ("dotnet_bundle", "runtimeconfig_json_offset"): "bundle_value",
    ("dotnet_bundle", "runtimeconfig_json_size"): "bundle_value",
    ("dotnet_bundle", "flags_u64_hex"): "bundle_value",
    ("dotnet_bundle", "bundle_flags_u64_hex"): "bundle_value",
    ("dotnet_bundle", "compressed_file_count"): "bundle_value",
    ("dotnet_bundle", "runtimeconfig_tfm"): "bundle_value",
    ("dotnet_bundle", "tfm"): "bundle_value",
    ("dotnet_bundle", "target_framework"): "bundle_value",
    ("dotnet_bundle", "target_framework_moniker"): "bundle_value",
    ("dotnet_bundle", "framework_name"): "bundle_value",
    ("dotnet_bundle", "framework_version"): "bundle_value",
    ("dotnet_bundle", "framework_names"): "bundle_value",
    ("dotnet_bundle", "framework_versions"): "bundle_value",
    ("dotnet_bundle", "runtimeconfig_framework_name"): "bundle_value",
    ("dotnet_bundle", "runtimeconfig_framework_version"): "bundle_value",
    ("dotnet_bundle", "runtime_target_name"): "bundle_value",
    ("dotnet_bundle", "deps_runtime_target_name"): "bundle_value",
    ("singlefile", "bundle_version"): "bundle_value",
    ("singlefile", "header_offset"): "bundle_value",
    ("singlefile", "bundle_id"): "bundle_value",
    ("singlefile", "file_count"): "bundle_value",
    ("singlefile", "file_names"): "bundle_value",
    ("singlefile", "main_assembly"): "bundle_value",
    ("singlefile", "runtimeconfig_tfm"): "bundle_value",
    ("singlefile", "framework_name"): "bundle_value",
    ("singlefile", "framework_version"): "bundle_value",
    ("apphost", "bundle_version"): "bundle_value",
    ("apphost", "header_offset"): "bundle_value",
    ("apphost", "bundle_id"): "bundle_value",
    ("apphost", "file_count"): "bundle_value",
    ("apphost", "file_names"): "bundle_value",
    ("apphost", "main_assembly"): "bundle_value",
    ("apphost", "runtimeconfig_tfm"): "bundle_value",
    ("apphost", "framework_name"): "bundle_value",
    ("apphost", "framework_version"): "bundle_value",
}

_SIG = bytes.fromhex("8b1202b96a612038727b930214d7a03213f5b9e6efae3318ee3b2dce24b36aae")
_TYPES = {0: "Unknown", 1: "Assembly", 2: "NativeBinary", 3: "DepsJson", 4: "RuntimeConfigJson", 5: "Symbols"}


def _str(b, o):
    """(.NET BinaryWriter string: 7-bit-encoded length + UTF-8, next offset)."""
    n = shift = 0
    while True:
        c = b[o]
        o += 1
        n |= (c & 0x7F) << shift
        shift += 7
        if not c & 0x80:
            break
        if shift > 28:
            raise ValueError("bad 7-bit length")
    if o + n > len(b):
        raise ValueError("string past end")
    return b[o:o + n].decode("utf-8"), o + n


def _manifest(b, off):
    major, minor, count = struct.unpack_from("<IIi", b, off)
    if not (1 <= major <= 32) or not (0 <= count <= 100000):
        raise ValueError("implausible header")
    bid, o = _str(b, off + 12)
    m = {"major": major, "minor": minor, "count": count, "id": bid, "offset": off, "entries": []}
    if major >= 2:
        m["deps"] = struct.unpack_from("<qq", b, o)
        m["rcfg"] = struct.unpack_from("<qq", b, o + 16)
        m["flags"], = struct.unpack_from("<Q", b, o + 32)
        o += 40
    for _ in range(count):
        eo, es = struct.unpack_from("<qq", b, o)
        o += 16
        ec = 0
        if major >= 6:
            ec, = struct.unpack_from("<q", b, o)
            o += 8
        et = b[o]
        name, o = _str(b, o + 1)
        if eo < 0 or es < 0 or ec < 0 or eo + (ec or es) > len(b):
            raise ValueError("entry past end")
        m["entries"].append({"offset": eo, "size": es, "csize": ec, "type": et, "path": name})
    return m


def manifest(b):
    """The parsed bundle manifest of a single-file apphost, or None (no marker / unbundled / damaged)."""
    i = b.find(_SIG)
    while i >= 8:
        off, = struct.unpack_from("<q", b, i - 8)
        if 0 < off < len(b) - 12:
            try:
                return _manifest(b, off)
            except (ValueError, IndexError, struct.error, UnicodeDecodeError):
                pass
        i = b.find(_SIG, i + 1)
    return None


def _payload(b, e):
    raw = bytes(b[e["offset"]:e["offset"] + (e["csize"] or e["size"])])
    return zlib.decompress(raw, -15) if e["csize"] else raw   # v6 compression = DeflateStream (raw deflate)


def _json(raw):
    try:
        return json.loads(raw.decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError):
        return None


def _member_json(b, m, etype, suffix):
    if m is None:
        j = _json(bytes(b)) if bytes(b[:64]).lstrip(b"\xef\xbb\xbf \t\r\n").startswith(b"{") else None
        return j if isinstance(j, dict) else None
    for e in m["entries"]:
        if e["type"] == etype or e["path"].lower().endswith(suffix):
            try:
                j = _json(_payload(b, e))
            except zlib.error:
                j = None
            if isinstance(j, dict):
                return j
    return None


def _frameworks(rc):
    ro = (rc or {}).get("runtimeOptions")
    if not isinstance(ro, dict):
        return None
    fws = []
    for k in ("framework", "frameworks", "includedFrameworks"):
        v = ro.get(k)
        fws += [v] if isinstance(v, dict) else [x for x in v if isinstance(x, dict)] if isinstance(v, list) else []
    return ro, fws


def _main_assembly(m, member):
    asm = [e["path"] for e in m["entries"] if e["type"] == 1]
    if not asm:
        return "none"
    stems = []
    base = (member or "").replace("\\", "/").rsplit("/", 1)[-1]
    if base:
        stems.append(base[:-4] if base.lower().endswith(".exe") else base)
    stems += [e["path"][:-len(".runtimeconfig.json")] for e in m["entries"]
              if e["path"].lower().endswith(".runtimeconfig.json")]
    for st in stems:
        for a in asm:
            if a.lower() in (st.lower() + ".dll", st.lower() + ".exe"):
                return a
    return asm[0]


def bundle_value(data, ctx):
    if data is None:
        return None
    try:
        from ..spell import Hex
        field = ctx.get("field") or ""
        m = manifest(data)
        if field in ("runtimeconfig_tfm", "tfm", "target_framework", "target_framework_moniker", "framework_name",
                     "framework_version", "framework_names", "framework_versions", "runtimeconfig_framework_name",
                     "runtimeconfig_framework_version"):
            fw = _frameworks(_member_json(data, m, 4, ".runtimeconfig.json"))
            if fw is None:
                return "none"
            ro, fws = fw
            if field in ("runtimeconfig_tfm", "tfm", "target_framework", "target_framework_moniker"):
                return ro.get("tfm") or "none"
            key = "name" if "name" in field else "version"
            vals = [str(f.get(key)) for f in fws if f.get(key)]
            if field.endswith("s"):
                return vals if vals else "none"
            return vals[0] if vals else "none"
        if field in ("runtime_target_name", "deps_runtime_target_name"):
            rt = (_member_json(data, m, 3, ".deps.json") or {}).get("runtimeTarget")
            return rt.get("name") or "none" if isinstance(rt, dict) else "none"
        if m is None:
            return "none"
        ents = m["entries"]
        if field == "bundle_version":
            return "%d.%d" % (m["major"], m["minor"])
        if field in ("bundle_major_version", "major_version"):
            return m["major"]
        if field in ("bundle_minor_version", "minor_version"):
            return m["minor"]
        if field in ("header_offset", "bundle_header_offset", "manifest_offset"):
            return m["offset"]
        if field == "bundle_id":
            return m["id"]
        if field in ("file_count", "entry_count", "bundle_file_count", "number_of_files"):
            return m["count"]
        if field in ("file_names", "entry_names", "member_names", "bundle_file_names", "file_paths"):
            return [e["path"] for e in ents]
        if field in ("entry_types", "file_types"):
            return [_TYPES.get(e["type"], str(e["type"])) for e in ents]
        if field == "assembly_names":
            return [e["path"] for e in ents if e["type"] == 1]
        if field in ("main_assembly", "main_assembly_name", "entry_assembly"):
            return _main_assembly(m, ctx.get("member"))
        if field == "compressed_file_count":
            return sum(1 for e in ents if e["csize"])
        if field in ("flags_u64_hex", "bundle_flags_u64_hex"):
            return Hex(m["flags"], 16) if "flags" in m else "none"
        loc = {"deps_json": "deps", "runtimeconfig_json": "rcfg"}.get(field.rsplit("_", 1)[0])
        if loc and field.endswith(("_offset", "_size")):
            if loc not in m:
                return "none"
            return m[loc][0 if field.endswith("_offset") else 1]
        return None
    except Exception:  # noqa: BLE001
        return None
