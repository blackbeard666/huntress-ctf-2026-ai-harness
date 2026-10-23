"""WebAssembly binary module header / section fields (WebAssembly Core spec 5.5; prebuilt, SPECULATIVE).

Preamble: magic b'\\0asm' (as a LE u32: 0x6d736100) + version u32 LE @4 (1 for the MVP/core-1/2 binary format).
Then sections: id u8, size LEB128 u32, payload. Custom sections (id 0) start with a name (vec(byte) UTF-8).
section_ids = every section id in file order (JSON list of ints, custom ones included, as `wasm-objdump -h`);
section_names = the same order spelled as wasm-objdump does (Type/Import/Function/.../Custom).
export_names = the export section's names in stored order; import_names = the import FIELD names (import_module_names
the module names). function_count = the Function section's entry count (defined functions, imports excluded).
Wrong magic / truncated preamble -> "none"; a section that does not exist -> "none" for its counts/lists.

Depth (wasm-start-exports): has_wasi_start = an export named `_start` of kind func (bool; no Export section -> false);
import_qualified_names = `module.field` per import, stored order (import_names keeps the bare FIELD names -- that
spelling has a fixture; the atlas also mentions `module.field`, so both are offered); import_modules = sorted unique
module names. memory_min_pages / memory_max_pages = limits of the first Memory-section entry (else the first imported
memory); no max -> "none". name_section_module_name = custom "name" subsection 0; name_section_function_names =
subsection 1 name map (stored order). producers_language / _processed_by / _sdk = custom "producers" field entries as
JSON ["name version"] (stored order; an empty version -> just the name, e.g. clang -g writes language "C11" + "");
target_features = custom "target_features" feature names (stored order, prefix dropped) and
target_features_prefixed keeps the `+`/`-`/`=` prefix as wasm-tools prints it. A missing custom section -> "none"."""
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
    ("wasm", "has_wasi_start"): "wasm_value",
    ("wasm", "has_start_export"): "wasm_value",
    ("wasm", "wasi_start_present"): "wasm_value",
    ("wasm", "is_wasi_command"): "wasm_value",
    ("wasm", "has_start_section"): "wasm_value",
    ("wasm", "start_section_present"): "wasm_value",
    ("wasm", "start_function"): "wasm_value",
    ("wasm", "start_func_index"): "wasm_value",
    ("wasm", "import_qualified_names"): "wasm_value",
    ("wasm", "import_full_names"): "wasm_value",
    ("wasm", "import_module_field_names"): "wasm_value",
    ("wasm", "imports"): "wasm_value",
    ("wasm", "import_modules"): "wasm_value",
    ("wasm", "import_module_set"): "wasm_value",
    ("wasm", "exports"): "wasm_value",
    ("wasm", "memory_min_pages"): "wasm_value",
    ("wasm", "memory_initial_pages"): "wasm_value",
    ("wasm", "memory_max_pages"): "wasm_value",
    ("wasm", "memory_maximum_pages"): "wasm_value",
    ("wasm", "name_section_module_name"): "wasm_value",
    ("wasm", "module_name"): "wasm_value",
    ("wasm", "name_section_function_names"): "wasm_value",
    ("wasm", "function_names"): "wasm_value",
    ("wasm", "producers_language"): "wasm_value",
    ("wasm", "producers_processed_by"): "wasm_value",
    ("wasm", "producers_sdk"): "wasm_value",
    ("wasm", "producer_language"): "wasm_value",
    ("wasm", "producer_processed_by"): "wasm_value",
    ("wasm", "producer_sdk"): "wasm_value",
    ("wasm", "processed_by"): "wasm_value",
    ("wasm", "producers_field_names"): "wasm_value",
    ("wasm", "target_features"): "wasm_value",
    ("wasm", "target_feature_names"): "wasm_value",
    ("wasm", "target_features_prefixed"): "wasm_value",
}

_ALIAS = {"has_start_export": "has_wasi_start", "wasi_start_present": "has_wasi_start",
          "is_wasi_command": "has_wasi_start", "start_section_present": "has_start_section",
          "start_function": "start_function_index", "start_func_index": "start_function_index",
          "import_full_names": "import_qualified_names", "import_module_field_names": "import_qualified_names",
          "imports": "import_qualified_names", "import_module_set": "import_modules", "exports": "export_names",
          "memory_initial_pages": "memory_min_pages", "memory_maximum_pages": "memory_max_pages",
          "module_name": "name_section_module_name", "function_names": "name_section_function_names",
          "producer_language": "producers_language", "producer_processed_by": "producers_processed_by",
          "producer_sdk": "producers_sdk", "processed_by": "producers_processed_by",
          "target_feature_names": "target_features"}

_NAMES = {0: "Custom", 1: "Type", 2: "Import", 3: "Function", 4: "Table", 5: "Memory", 6: "Global", 7: "Export",
          8: "Start", 9: "Elem", 10: "Code", 11: "Data", 12: "DataCount", 13: "Tag"}
_KINDS = {0: "func", 1: "table", 2: "memory", 3: "global", 4: "tag"}


def _leb(b, off):
    r = shift = 0
    while True:
        if off >= len(b) or shift > 63:
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
        lim = None
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
            lim = _limits_val(payload, off)
            off = _limits(payload, off)
        elif kind == 3:                          # global: valtype + mut
            off += 2
        else:
            raise ValueError("import kind")
        out.append((mod, fld, kind, lim))
    return out


def _limits(p, off):
    flag = p[off]
    off += 1
    _, off = _leb(p, off)
    if flag & 1:
        _, off = _leb(p, off)
    return off


def _limits_val(p, off):
    """(min, max-or-None) of a limits record (flag bit0 = has max; memory64 bit2 only widens the LEBs)."""
    flag = p[off]
    lo, off = _leb(p, off + 1)
    hi = _leb(p, off)[0] if flag & 1 else None
    return lo, hi


def _custom(secs, name):
    for s, p in secs:
        if s == 0:
            nm, off = _name(p, 0)
            if nm == name:
                return p[off:]
    return None


def _producers(p):
    """{field_name: ["name version", ...]} of a producers custom section payload."""
    n, off = _leb(p, 0)
    out = {}
    for _ in range(n):
        fname, off = _name(p, off)
        cnt, off = _leb(p, off)
        vals = []
        for _ in range(cnt):
            nm, off = _name(p, off)
            ver, off = _name(p, off)
            vals.append((nm + " " + ver).strip())
        out[fname] = vals
    return out


def _name_subsections(p):
    out, off = {}, 0
    while off < len(p):
        sid = p[off]
        size, off = _leb(p, off + 1)
        out.setdefault(sid, p[off:off + size])
        off += size
    return out


def _depth(secs, field):
    if field == "has_wasi_start":
        p = _first(secs, 7)
        return any(n == "_start" and k == 0 for n, k, _ in _exports(p)) if p is not None else False
    if field == "has_start_section":
        return _first(secs, 8) is not None
    if field in ("import_qualified_names", "import_modules"):
        p = _first(secs, 2)
        if p is None:
            return "none"
        im = _imports(p)
        if field == "import_modules":
            return sorted({m for m, _, _, _ in im})
        return [m + "." + f for m, f, _, _ in im]
    if field in ("memory_min_pages", "memory_max_pages"):
        p = _first(secs, 5)
        lim = None
        if p is not None and _leb(p, 0)[0] > 0:
            lim = _limits_val(p, _leb(p, 0)[1])
        elif _first(secs, 2) is not None:
            lim = next((x[3] for x in _imports(_first(secs, 2)) if x[2] == 2), None)
        if lim is None:
            return "none"
        v = lim[0] if field == "memory_min_pages" else lim[1]
        return "none" if v is None else v
    if field in ("name_section_module_name", "name_section_function_names"):
        p = _custom(secs, "name")
        if p is None:
            return "none"
        sub = _name_subsections(p)
        if field == "name_section_module_name":
            return _name(sub[0], 0)[0] if 0 in sub else "none"
        if 1 not in sub:
            return "none"
        q = sub[1]
        n, off = _leb(q, 0)
        names = []
        for _ in range(n):
            _, off = _leb(q, off)
            nm, off = _name(q, off)
            names.append(nm)
        return names
    if field.startswith("producers_"):
        p = _custom(secs, "producers")
        if p is None:
            return "none"
        pr = _producers(p)
        if field == "producers_field_names":
            return list(pr)
        key = field[len("producers_"):].replace("_", "-")
        return pr.get(key, "none")
    if field in ("target_features", "target_features_prefixed"):
        p = _custom(secs, "target_features")
        if p is None:
            return "none"
        n, off = _leb(p, 0)
        out = []
        for _ in range(n):
            pre = chr(p[off])
            nm, off = _name(p, off + 1)
            out.append(pre + nm if field.endswith("_prefixed") else nm)
        return out
    return None


_DEPTH = {"has_wasi_start", "has_start_section", "import_qualified_names", "import_modules", "memory_min_pages",
          "memory_max_pages", "name_section_module_name", "name_section_function_names", "producers_language",
          "producers_processed_by", "producers_sdk", "producers_field_names", "target_features",
          "target_features_prefixed"}


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
    field = _ALIAS.get(field, field)
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
    if field in _DEPTH:
        return _depth(secs, field)
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
            return [m for m, _, _, _ in im]
        return [f for _, f, _, _ in im]
    sid = {"function_count": 3, "type_count": 1, "memory_count": 5, "data_segment_count": 11,
           "start_function_index": 8}.get(field)
    if sid is None:
        return None
    p = _first(secs, sid)
    if p is None:
        return "none"
    return _leb(p, 0)[0]
