#!/bin/sh
# Independent oracle for gfortran_* fixtures: binutils (file, readelf -d/-S/-wi, nm -S --defined-only) parsed by a
# python3 one-off (no lib.binary); HCFG offset = bytes.find(b'HCFG') + zlib.crc32 check, mapped through readelf -S/nm -S.
f=$1
python3 - "$f" <<'PY'
import json, re, subprocess, sys, zlib, struct
f = sys.argv[1]
run = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout
fb = run("file", "-b", f)
dyn = run("readelf", "-dW", f)
needed = re.findall(r"\(NEEDED\)\s+Shared library: \[([^\]]+)\]", dyn)
und = {l.split()[-1].split("@")[0] for l in run("nm", "-D", "--undefined-only", f).splitlines() if l.split()}
nm = [l.split() for l in run("nm", "-S", "--defined-only", f).splitlines()]
nm = [(x[-1], x[-2], int(x[0], 16), int(x[1], 16) if len(x) == 4 else 0) for x in nm if len(x) >= 3]
imps = sorted(n for n in und if n.startswith("_gfortran_"))
gf = next((n for n in needed if n.startswith("libgfortran.so")), None)
mod = [(n, t) for n, t, _, _ in nm if n.startswith("__") and "_MOD_" in n]
info = run("readelf", "-wi", f)
prod = re.search(r"DW_AT_producer\s*:.*?: (GNU Fortran[^\n]*)", info) or re.search(r"DW_AT_producer\s*:.*?: (GNU [^\n]*)", info)
lang = re.search(r"DW_AT_language\s*: (\d+)", info)
cu = re.search(r"DW_TAG_compile_unit\).*?DW_AT_name\s*:\s*(?:\(indirect[^)]*\): )?([^\n]+)", info, re.S)
prog = re.search(r"DW_AT_external[^\n]*\n(?:[^\n]*\n){0,1}?[^\n]*DW_AT_name\s*:.*?: (\w+)\n(?:[^\n]*\n){0,8}?[^\n]*DW_AT_main_subprogram", info)
if not prog:
    m = info.find("DW_AT_main_subprogram")
    names = re.findall(r"DW_AT_name\s*:(?:.*?: )?\s*(\w+)\n", info[:m]) if m >= 0 else []
    prog = names[-1] if names else "none"
else:
    prog = prog.group(1)
commons = sorted(set(re.findall(r"DW_TAG_common_block\)\n\s*<\w+>\s+DW_AT_name\s*:\s*(?:\(indirect[^)]*\): )?(\w+)", info)))
ext = sorted(n[:-1] for n, t, _, _ in nm if t == "T" and re.match(r"^[a-z][a-z0-9_]*_$", n))
out = {"format": "elf" if fb.startswith("ELF") else "none",
       "architecture": "x86-64" if "x86-64" in fb else "none", "needed": needed,
       "has_libgfortran_needed": "true" if gf else "false", "libgfortran_soname": gf or "none",
       "gfortran_imports": imps, "has_main_program": "true" if any(n == "MAIN__" for n, *_ in nm) else "false",
       "has_gfortran_runtime": "true" if (gf or imps) else "false",
       "fortran_modules": sorted({n[2:].partition("_MOD_")[0] for n, _ in mod}),
       "module_procedures": sorted("::".join(n[2:].split("_MOD_", 1)) for n, t in mod if t in "Tt"),
       "module_procedures_mangled": sorted(n for n, t in mod if t in "Tt"),
       "module_variables": sorted("::".join(n[2:].split("_MOD_", 1)) for n, t in mod if t in "DdBbRr"),
       "module_variables_mangled": sorted(n for n, t in mod if t in "DdBbRr"),
       "common_blocks": commons, "common_blocks_mangled": [c + "_" for c in commons],
       "external_procedures": ext,
       "dwarf_producer": re.match(r"(.*?\d+(?:\.\d+)+)", prod.group(1)).group(1) if prod else "none",
       "dwarf_language_code": int(lang.group(1)) if lang else "none",
       "main_source": cu.group(1).strip() if cu and "Fortran" in (prod.group(1) if prod else "") else "none",
       "program_name": prog if "Fortran" in (prod.group(1) if prod else "") else "none"}
d = open(f, "rb").read()
o, hit = d.find(b"HCFG"), None
while o >= 0:
    ln, crc = struct.unpack_from("<HI", d, o + 6)
    k = d[o + 5]
    if zlib.crc32(bytes(c ^ k for c in d[o + 12:o + 12 + ln])) == crc:
        hit = o
        break
    o = d.find(b"HCFG", o + 1)
sym = ent = sec = "none"
if hit is not None:
    for l in run("readelf", "-SW", f).splitlines():
        m = re.match(r"\s*\[\s*\d+\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)", l)
        if m and m.group(2) != "NOBITS" and int(m.group(3), 16) and int(m.group(4), 16) <= hit < int(m.group(4), 16) + int(m.group(5), 16):
            sec, va = m.group(1), int(m.group(3), 16) + hit - int(m.group(4), 16)
            c = [(n, a) for n, t, a, s in nm if t in "DdRrBb" and a <= va < a + max(s, 1)]
            if c:
                sym = c[0][0]
                ent = "::".join(sym[2:].split("_MOD_", 1)) if "_MOD_" in sym else sym.rstrip("_")
    cfg = json.loads(bytes(c ^ d[hit + 5] for c in d[hit + 12:hit + 12 + struct.unpack_from("<H", d, hit + 6)[0]]))
    out["hcfg_offset"], out["hcfg_config"] = hit, cfg
out.update(hcfg_symbol=sym, hcfg_entity=ent, hcfg_section=sec)
print(json.dumps(out, indent=1))
PY
