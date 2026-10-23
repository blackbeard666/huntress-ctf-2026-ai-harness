"""Oracle for dwarf_*.bin: expected dwarf_facts from llvm-dwarfdump-18 TEXT output only (--debug-info / --debug-line)
run on a GNU `objcopy --decompress-debug-sections` copy (llvm-dwarfdump-18 reads SHF_COMPRESSED but not legacy .zdebug). Independent of lib.binary / pyelftools.
usage: python3 dwarf_oracle.py <file.bin>   -> prints the expected_facts JSON"""
import json, re, subprocess, sys

import os, tempfile
src = sys.argv[1]
f = os.path.join(tempfile.mkdtemp(), "plain.elf")
if subprocess.run(["objcopy", "--decompress-debug-sections", src, f], capture_output=True).returncode:
    f = src   # not an ELF (text decoy): llvm-dwarfdump reports no units
run = lambda *a: subprocess.run(["llvm-dwarfdump-18", *a, f], capture_output=True, text=True).stdout  # noqa: E731
info, line = run("--debug-info"), run("--debug-line")
has = bool(re.search(r"Compile Unit:", info))
out = {"has_dwarf": "true" if has else "false"}
dies, stack, cus = [], [], []
cur = None
for ln in info.splitlines():
    m = re.match(r"0x[0-9a-f]+: Compile Unit: .*version = 0x(\w+)", ln)
    if m:
        cus.append({"version": str(int(m.group(1), 16)), "dies": []})
        stack = []
        continue
    m = re.match(r"0x[0-9a-f]+:( *)(DW_TAG_\w+|NULL)", ln)
    if m:
        depth = (len(m.group(1)) - 1) // 2
        if m.group(2) == "NULL":
            cur = None
            continue
        cur = {"tag": m.group(2), "depth": depth, "at": {}, "kids": []}
        del stack[depth:]
        (stack[-1]["kids"] if stack else cus[-1]["dies"]).append(cur)
        stack.append(cur)
        continue
    m = re.match(r"\s+(DW_AT_\w+)\t\((.*)\)$", ln)
    if m and cur is not None:
        v = m.group(2)
        cur["at"][m.group(1)] = v[1:-1] if v.startswith('"') and v.endswith('"') else v
cu_rows, funcs, gvars, structs, fields, typedefs, enums, enumerators = [], [], [], [], {}, [], [], []
params, locals_ = {}, {}
def add(l, v):
    if v not in l:
        l.append(v)
def members(d):
    return [k["at"]["DW_AT_name"] for k in d["kids"] if k["tag"] == "DW_TAG_member" and "DW_AT_name" in k["at"]]
for cu in cus:
    top = cu["dies"][0]
    a = top["at"]
    cu_rows.append([a.get("DW_AT_name", "none"), a.get("DW_AT_language", "none"), a.get("DW_AT_producer", "none")])
    cu.setdefault("comp_dir", a.get("DW_AT_comp_dir", "none"))
    def walk(d, depth):
        a = d["at"]
        nm = a.get("DW_AT_name")
        if d["tag"] == "DW_TAG_subprogram" and nm and "DW_AT_low_pc" in a:
            lo = int(a["DW_AT_low_pc"], 16)
            hi = a["DW_AT_high_pc"]
            m = re.match(r"0x([0-9a-f]+)", hi)
            hi = int(m.group(1), 16)   # llvm-dwarfdump prints high_pc as an absolute address (offset forms resolved)
            if not any(x["name"] == nm and x["low_pc"] == f"0x{lo:x}" for x in funcs):
                funcs.append({"name": nm, "low_pc": f"0x{lo:x}", "high_pc": f"0x{hi:x}", "size": hi - lo})
            params[nm] = [k["at"]["DW_AT_name"] for k in d["kids"]
                          if k["tag"] == "DW_TAG_formal_parameter" and "DW_AT_name" in k["at"]]
            lv = []
            def lw(x):
                for k in x["kids"]:
                    if k["tag"] == "DW_TAG_variable" and "DW_AT_name" in k["at"]:
                        add(lv, k["at"]["DW_AT_name"])
                    if k["tag"] == "DW_TAG_lexical_block":
                        lw(k)
            lw(d)
            locals_[nm] = lv
        if d["tag"] == "DW_TAG_variable" and depth == 1 and nm and "DW_AT_declaration" not in a:
            add(gvars, nm)
        if d["tag"] == "DW_TAG_structure_type" and nm:
            add(structs, nm)
            if members(d):
                fields.setdefault(nm, members(d))
        if d["tag"] == "DW_TAG_typedef" and nm:
            add(typedefs, nm)
            ref = re.match(r"(0x[0-9a-f]+)", a.get("DW_AT_type", ""))
            if ref:
                tgt = next((x for x in flat if x[0] == ref.group(1)), None)
        if d["tag"] == "DW_TAG_enumeration_type" and nm:
            add(enums, nm)
        if d["tag"] == "DW_TAG_enumerator" and nm:
            add(enumerators, nm)
        for k in d["kids"]:
            walk(k, depth + 1)
    flat = []
    walk(top, 0)
# typedef of an anonymous struct: fields keyed by the typedef name (re-parse with offsets)
offs = {}
cur_off = None
for ln in info.splitlines():
    m = re.match(r"(0x[0-9a-f]+):( *)(DW_TAG_\w+|NULL)", ln)
    if m:
        cur_off = (m.group(1), m.group(3), len(m.group(2)))
        offs[int(cur_off[0], 16)] = {"tag": m.group(3), "depth": len(m.group(2)), "at": {}, "lines": []}
        continue
    m = re.match(r"\s+(DW_AT_\w+)\t\((.*)\)$", ln)
    if m and cur_off:
        offs[int(cur_off[0], 16)]["at"][m.group(1)] = m.group(2)
keys = sorted(offs)
def kids_of(o):
    d, r = offs[o]["depth"], []
    for k in keys[keys.index(o) + 1:]:
        if offs[k]["depth"] <= d:
            break
        if offs[k]["depth"] == d + 2 and offs[k]["tag"] == "DW_TAG_member" and "DW_AT_name" in offs[k]["at"]:
            r.append(offs[k]["at"]["DW_AT_name"].strip('"'))
    return r
for o in keys:
    x = offs[o]
    if x["tag"] == "DW_TAG_typedef" and "DW_AT_type" in x["at"]:
        m = re.match(r"(0x[0-9a-f]+)", x["at"]["DW_AT_type"])
        t = offs.get(int(m.group(1), 16)) if m else None
        nm = x["at"]["DW_AT_name"].strip('"')
        if t and t["tag"] == "DW_TAG_structure_type" and "DW_AT_name" not in t["at"] and nm not in fields:
            fields[nm] = kids_of(int(m.group(1), 16))
# line tables: file_names in table order, all CUs
files, paths = [], []
cu_i = -1
for tbl in re.split(r"\ndebug_line\[", line)[1:]:
    cu_i += 1
    comp = cus[cu_i]["comp_dir"] if cu_i < len(cus) else ""
    ver = int(re.search(r"version: (\d+)", tbl).group(1))
    dirs = {int(i): d for i, d in re.findall(r'include_directories\[\s*(\d+)\] = "(.*)"', tbl)}
    for i, nm, di in re.findall(r'file_names\[\s*(\d+)\]:\n\s+name: "(.*)"\n\s+dir_index: (\d+)', tbl):
        di = int(di)
        d = comp if (ver < 5 and di == 0) else dirs.get(di, "")
        if d and not d.startswith("/") and comp:
            d = comp + "/" + d
        p = nm if nm.startswith("/") or not d else d + "/" + nm
        add(files, nm)
        add(paths, p)
if has:
    out.update({
        "dwarf_version": cus[0]["version"], "cu_count": str(len(cus)),
        "cu_name": cu_rows[0][0], "language": cu_rows[0][1], "producer": cu_rows[0][2],
        "comp_dir": cus[0]["comp_dir"], "cu_names": [r[0] for r in cu_rows],
        "languages": sorted({r[1] for r in cu_rows}), "cus": cu_rows,
        "functions": funcs, "function_names": [x["name"] for x in funcs],
        "files": files, "file_paths": paths, "global_variables": gvars,
        "structs": structs, "struct_fields": fields, "typedefs": typedefs, "enums": enums,
        "enumerators": enumerators, "params": params, "locals": locals_,
    })
KEYS = ("dwarf_version", "cu_count", "cu_name", "language", "producer", "comp_dir", "cu_names", "languages", "cus",
        "functions", "function_names", "files", "file_paths", "global_variables", "structs", "struct_fields", "typedefs",
        "enums", "enumerators", "params", "locals")
for k in KEYS:
    if out.get(k) in (None, [], {}):
        out[k] = "none"
if f == src:
    out["has_dwarf"] = "none"   # not an ELF: no field to read
print(json.dumps(out, indent=1))
