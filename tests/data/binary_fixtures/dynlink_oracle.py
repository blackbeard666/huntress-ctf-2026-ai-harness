"""Independent oracle for the dynlink_* fixtures: binutils only (readelf --dyn-syms / -d / -lW, objdump -d -Mintel,
xxd-style byte reads at the readelf-mapped offset) -- no capstone, no pyelftools, no lib.binary.
usage: python3 dynlink_oracle.py LOADER.bin PLUGIN.bin  -> JSON of the facts it can derive"""
import json, re, subprocess, sys

sh = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout


def segs(p):
    out = []
    for m in re.finditer(r"LOAD\s+0x([0-9a-f]+)\s+0x([0-9a-f]+)\s+0x[0-9a-f]+\s+0x([0-9a-f]+)", sh("readelf", "-lW", p)):
        out.append((int(m.group(2), 16), int(m.group(1), 16), int(m.group(3), 16)))
    return out


def cstr(p, va):
    data = open(p, "rb").read()
    for v, o, n in segs(p):
        if v <= va < v + n:
            s = o + va - v
            return data[s:data.index(b"\0", s)].decode()


def dynsyms(p):
    rows = []
    for ln in sh("readelf", "--dyn-syms", "-W", p).splitlines():
        f = ln.split()
        if len(f) >= 8 and f[0].rstrip(":").isdigit() and f[0] != "0:":
            rows.append((f[7].split("@")[0], int(f[1], 16), f[6] != "UND"))
    return rows


def calls(p):
    out, regs = [], {}
    for ln in sh("objdump", "-d", "-Mintel", "--no-show-raw-insn", p).splitlines():
        m = re.match(r"\s*[0-9a-f]+:\s+(\S+)\s*(.*)", ln)
        if not m:
            continue
        mn, ops = m.groups()
        c = re.search(r"<(dlopen|dlsym)(@plt|@GLIBC[^>]*)>", ops)
        if mn == "call" and c:
            arg = regs.get("di" if c.group(1) == "dlopen" else "si")
            out.append((c.group(1), cstr(p, arg) if arg else None))
        if mn == "call":
            regs = {}
            continue
        d, _, s = ops.partition(",")
        d = re.sub(r"^[re]", "", d) if re.fullmatch(r"[re](di|si|ax|dx|cx)", d) else d
        a = re.search(r"#\s*([0-9a-f]+)", s)
        if mn == "lea" and a:
            regs[d] = int(a.group(1), 16)
        elif mn == "mov" and re.fullmatch(r"0x[0-9a-f]+", s):
            regs[d] = int(s, 16)
        elif mn == "mov" and re.fullmatch(r"[re](di|si|ax|dx|cx)", s):
            regs[d] = regs.get(s[1:])
        else:
            regs.pop(d, None)
    return out


L, P = sys.argv[1:3]
res = {}
cl = calls(L)
libs = [s for a, s in cl if a == "dlopen" and s]
syms = [s for a, s in cl if a == "dlsym" and s]
res["loaded_library"] = libs[0] if libs else "none"
res["resolved_symbols"] = json.dumps(syms, separators=(",", ":")) if syms else "none"
res["loader_needs_libdl"] = "true" if "[libdl.so" in sh("readelf", "-d", L) else "false"
exps = [n for n, _, d in dynsyms(P) if d]
res["plugin_exports"] = json.dumps(exps, separators=(",", ":")) if exps else "none"
hdr = next((v for n, v, d in dynsyms(P) if n == "caml_plugin_header" and d), None)
res["plugin_header_magic"] = "none"
if hdr is not None:
    data = open(P, "rb").read()
    o = next(o + hdr - v for v, o, n in segs(P) if v <= hdr < v + n)
    # intext small header (8495a6be, 5 x u32) then a0 (block tag0 size2) then 0x20|len string = dynu_magic
    if data[o:o + 4].hex() == "8495a6be" and data[o + 21] & 0xE0 == 0x20:
        res["plugin_header_magic"] = data[o + 22:o + 22 + (data[o + 21] & 0x1F)].decode()
print(json.dumps(res, indent=1))
