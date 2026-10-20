"""WebAssembly binary module header / section fields (WebAssembly Core spec 5.5; prebuilt, SPECULATIVE).

Preamble: magic b'\\0asm' (as a LE u32: 0x6d736100) + version u32 LE @4 (1 for the MVP/core-1/2 binary format).
Then sections: id u8, size LEB128 u32, payload. Custom sections (id 0) start with a name (vec(byte) UTF-8).
section_ids = every section id in file order (JSON list of ints, custom ones included, as `wasm-objdump -h`);
section_names = the same order spelled as wasm-objdump does (Type/Import/Function/.../Custom).
export_names = the export section's names in stored order; import_names = the import FIELD names (import_module_names
the module names). function_count = the Function section's entry count (defined functions, imports excluded).
Wrong magic / truncated preamble -> "none"; a section that does not exist -> "none" for its counts/lists."""
import struct

from ..spell import Hex

FIELDS = {
    ("wasm", "magic_u32_hex"): "wasm_value",
    ("wasm", "magic"): "wasm_value",
    ("wasm", "version_u32"): "wasm_value",
    ("wasm", "version"): "wasm_value",
    ("wasm", "binary_version"): "wasm_value",
    ("wasm", "version_u32_hex"): "wasm_value",
    ("wasm", "section_ids"): "wasm_value",
    ("wasm", "section_id_list"): "wasm_value",
    ("wasm", "section_names"): "wasm_value",
    ("wasm", "section_count"): "wasm_value",
    ("wasm", "custom_section_names"): "wasm_value",
    ("wasm", "export_names"): "wasm_value",
    ("wasm", "export_count"): "wasm_value",
    ("wasm", "export_kinds"): "wasm_value",
    ("wasm", "import_names"): "wasm_value",
    ("wasm", "import_field_names"): "wasm_value",
    ("wasm", "import_module_names"): "wasm_value",
    ("wasm", "import_count"): "wasm_value",
    ("wasm", "function_count"): "wasm_value",
    ("wasm", "type_count"): "wasm_value",
    ("wasm", "start_function_index"): "wasm_value",
    ("wasm", "memory_count"): "wasm_value",
    ("wasm", "data_segment_count"): "wasm_value",
}

_NAMES = {0: "Custom", 1: "Type", 2: "Import", 3: "Function", 4: "Table", 5: "Memory", 6: "Global", 7: "Export",
          8: "Start", 9: "Elem", 10: "Code", 11: "Data", 12: "DataCount", 13: "Tag"}
_KINDS = {0: "func", 1: "table", 2: "memory", 3: "global", 4: "tag"}


def _leb(b, off):
    r = shift = 0
    while True:
        if off >= len(b) or shift > 35:
            raise ValueError("leb")
        x = b[off]
        off += 1
        r |= (x & 0x7F) << shift
        shift += 7
        if not x & 0x80:
            return r, off


def _name(b, off):
    n, off = _leb(b, off)
    if off + n > len(b):
        raise ValueError("name")
    return bytes(b[off:off + n]).decode("utf-8", "replace"), off + n


def _sections(b):
    out, off = [], 8
    while off < len(b):
        sid = b[off]
        size, p = _leb(b, off + 1)
        if p + size > len(b):
            break   # truncated tail: keep what parsed
        out.append((sid, bytes(b[p:p + size])))
        off = p + size
    return out


def _imports(payload):
    n, off = _leb(payload, 0)
    out = []
    for _ in range(n):
        mod, off = _name(payload, off)
        fld, off = _name(payload, off)
        kind = payload[off]
        off += 1
        if kind == 0 or kind == 4:              # func typeidx / tag (attr u8 + typeidx)
            if kind == 4:
                off += 1
            _, off = _leb(payload, off)
        elif kind == 1:                          # table: reftype + limits
            off += 1
            off = _limits(payload, off)
        elif kind == 2:                          # memory: limits
            off = _limits(payload, off)
        elif kind == 3:                          # global: valtype + mut
            off += 2
        else:
            raise ValueError("import kind")
        out.append((mod, fld, kind))
    return out


def _limits(p, off):
    flag = p[off]
    off += 1
    _, off = _leb(p, off)
    if flag & 1:
        _, off = _leb(p, off)
    return off


def _exports(payload):
    n, off = _leb(payload, 0)
    out = []
    for _ in range(n):
        nm, off = _name(payload, off)
        kind = payload[off]
        idx, off = _leb(payload, off + 1)
        out.append((nm, kind, idx))
    return out


def wasm_value(data, ctx):
    try:
        return _wasm_value(data, (ctx or {}).get("field") or "")
    except (struct.error, ValueError, IndexError):
        return "none"


def _first(secs, sid):
    for s, p in secs:
        if s == sid:
            return p
    return None


def _wasm_value(b, field):
    if b is None:
        return None
    if not isinstance(b, (bytes, bytearray)) or len(b) < 8 or b[:4] != b"\0asm":
        return "none"
    ver, = struct.unpack_from("<I", b, 4)
    if field in ("magic_u32_hex", "magic"):
        return Hex(0x6D736100, 8)
    if field in ("version_u32", "version", "binary_version"):
        return ver
    if field == "version_u32_hex":
        return Hex(ver, 8)
    secs = _sections(b)
    if field in ("section_ids", "section_id_list"):
        return [s for s, _ in secs]
    if field == "section_names":
        return [_NAMES.get(s, str(s)) for s, _ in secs]
    if field == "section_count":
        return len(secs)
    if field == "custom_section_names":
        return [_name(p, 0)[0] for s, p in secs if s == 0]
    if field.startswith("export"):
        p = _first(secs, 7)
        if p is None:
            return "none"
        ex = _exports(p)
        if field == "export_count":
            return len(ex)
        if field == "export_kinds":
            return [_KINDS.get(k, str(k)) for _, k, _ in ex]
        return [n for n, _, _ in ex]
    if field.startswith("import"):
        p = _first(secs, 2)
        if p is None:
            return "none"
        im = _imports(p)
        if field == "import_count":
            return len(im)
        if field == "import_module_names":
            return [m for m, _, _ in im]
        return [f for _, f, _ in im]
    sid = {"function_count": 3, "type_count": 1, "memory_count": 5, "data_segment_count": 11,
           "start_function_index": 8}.get(field)
    if sid is None:
        return None
    p = _first(secs, sid)
    if p is None:
        return "none"
    return _leb(p, 0)[0]
