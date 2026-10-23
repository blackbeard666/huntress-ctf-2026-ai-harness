"""Independent oracle for xbridge_* fixtures (never lib.binary): lief (relocations / symbols / raw data), real loaders
(system CPython imports the extension, .venv CPython 3.12 imports the Cython / cffi builds, `lua` require()s the Lua
module) and `ast` over the ctypes caller sources. Prints {fixture: expected_facts}.
usage (repo root, after xbridge_gen.sh): .venv/bin/python tests/data/binary_fixtures/xbridge_oracle.py"""
import ast, json, os, pathlib, shutil, struct, subprocess, sys, tempfile
import lief

H = pathlib.Path(__file__).resolve().parent
ROOT = H.parents[2]
FLAGS = ((1, "METH_VARARGS"), (2, "METH_KEYWORDS"), (4, "METH_NOARGS"), (8, "METH_O"), (0x10, "METH_CLASS"),
         (0x20, "METH_STATIC"), (0x40, "METH_COEXIST"), (0x80, "METH_FASTCALL"), (0x200, "METH_METHOD"))
T = pathlib.Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))


def lief_view(p):
    b = lief.ELF.parse(str(p))
    rel = {r.address: r.addend for r in b.relocations if r.type == lief.ELF.Relocation.TYPE.X86_64_RELATIVE}
    rel.update({r.address: r.symbol.value + r.addend for r in b.relocations
                if r.type == lief.ELF.Relocation.TYPE.X86_64_64 and r.has_symbol and r.symbol.value})
    fn = {s.value: s.name for s in b.symbols if s.type == lief.ELF.Symbol.TYPE.FUNC and s.value}
    def cstr(va):
        out = bytearray()
        while True:
            c = bytes(b.get_content_from_virtual_address(va + len(out), 1))[0]
            if not c:
                return out.decode("latin-1")
            out.append(c)
    def u64(va):
        return struct.unpack("<Q", bytes(b.get_content_from_virtual_address(va, 8)))[0]
    return b, rel, fn, cstr, u64


def pymod(p, py, name, suffix):
    d = T / name
    d.mkdir(exist_ok=True)
    shutil.copy(p, d / (name + suffix))
    code = (f"import json,sys; sys.path.insert(0,{str(d)!r}); import {name} as m; "
            "fs={k:getattr(m,k) for k in dir(m) if callable(getattr(m,k)) and not k.startswith('_')}; "
            "print(json.dumps({'name':m.__name__,'doc':m.__doc__,'funcs':{k:v.__doc__ for k,v in fs.items()},"
            "'lib':sorted(k for k in dir(getattr(m,'lib',None)) if not k.startswith('_')) if hasattr(m,'lib') else None}))")
    return json.loads(subprocess.check_output([py, "-I", "-c", code], text=True))


def pyext(p, stripped):
    b, rel, fn, cstr, u64 = lief_view(p)
    init = next(s.name for s in b.exported_symbols if s.name.startswith("PyInit_"))
    mod = init[7:]
    live = pymod(p, "/usr/bin/python3", mod, subprocess.check_output(
        ["/usr/bin/python3-config", "--extension-suffix"], text=True).strip())
    nslot = next(a for a, t in rel.items() if cstr(t) == mod)   # PyModuleDef.m_name
    tbl, meths = rel[nslot + 24], []
    while tbl in rel:
        name = cstr(rel[tbl])
        fva = rel[tbl + 8]
        flags = u64(tbl + 16) & 0xffffffff
        meths.append((name, fn.get(fva, "sub_%x" % fva), "|".join(n for v, n in FLAGS if flags & v)))
        tbl += 32
    assert {m[0] for m in meths} == set(live["funcs"]), (meths, live)
    size = struct.unpack("<q", struct.pack("<Q", u64(nslot + 16)))[0]
    return {"extension_kind": "python_ext", "init_export": init, "module_name": live["name"],
            "module_doc": live["doc"] or "none", "module_size": str(size), "method_count": str(len(meths)),
            "method_names": [m[0] for m in meths], "method_flags": {m[0]: m[2] for m in meths},
            "method_functions": {m[0]: m[1] for m in meths},
            "methods": [{"name": m[0], "function": m[1], "flags": m[2],
                         "flags_value": str(sum(v for v, n in FLAGS if n in m[2].split("|"))),
                         "doc": live["funcs"][m[0]] or "none"} for m in meths]}


def cython(p):
    b, rel, fn, cstr, u64 = lief_view(p)
    py = str(ROOT / ".venv/bin/python")
    live = pymod(p, py, "beacon", ".cpython-312-x86_64-linux-gnu.so")
    ver = subprocess.check_output([py, "-c", "import Cython; print(Cython.__version__)"], text=True).strip()
    nslot = next(a for a, t in rel.items() if cstr(t) == "beacon")
    return {"extension_kind": "cython", "extension_kinds": ["cython", "python_ext"], "init_export": "PyInit_beacon",
            "module_name": live["name"], "module_doc": live["doc"], "cython_version": ver,
            "pyx_path": "pkg/beacon.pyx", "pyx_paths": ["pkg/beacon.pyx"],
            "multi_phase": "true" if rel.get(nslot + 32) else "false",
            "cython_functions": sorted(live["funcs"])}


def cffi(p):
    live = pymod(p, str(ROOT / ".venv/bin/python"), "_hcfg_cffi", ".cpython-312-x86_64-linux-gnu.so")
    return {"extension_kind": "cffi", "extension_kinds": ["cffi", "python_ext"], "init_export": "PyInit__hcfg_cffi",
            "module_name": live["name"], "cffi_functions": live["lib"]}


def dyn(p):
    b = lief.ELF.parse(str(p))
    ex = [s.name for s in b.dynamic_symbols if s.shndx and s.name]   # readelf --dyn-syms: defined
    im = [s.name for s in b.dynamic_symbols if not s.shndx and s.name]   # UND, table order
    return b, ex, im


def lua(p):
    b, ex, im = dyn(p)
    _, rel, fn, cstr, u64 = lief_view(p)
    init = next(n for n in ex if n.startswith("luaopen_"))
    d = T / "lua"
    d.mkdir(exist_ok=True)
    shutil.copy(p, d / (init[8:] + ".so"))
    live = subprocess.check_output(["lua", "-e", f"package.cpath='{d}/?.so'; local m=require('{init[8:]}'); "
                                    "local t={} for k in pairs(m) do t[#t+1]=k end table.sort(t) "
                                    "print(table.concat(t, ','))"], text=True).strip().split(",")
    tbl = min(a for a, t in rel.items() if cstr(t) in live)   # first luaL_Reg slot in .data.rel.ro
    order = []
    while tbl in rel:
        order.append((cstr(rel[tbl]), fn[rel[tbl + 8]]))
        tbl += 16
    assert sorted(n for n, _ in order) == sorted(live), (order, live)
    return {"extension_kind": "lua_c", "init_export": init, "module_name": init[8:], "lua_module": init[8:],
            "lua_functions": [n for n, _ in order],
            "lua_tables": [[{"name": n, "function": f} for n, f in order]],
            "lua_imports": [n for n in im if n.startswith(("lua_", "luaL_"))]}


def napi(p):
    b, ex, im = dyn(p)
    return {"extension_kind": "napi", "init_export": "napi_register_module_v1" if "napi_register_module_v1" in ex
            else "none", "module_name": "none", "napi_imports": [n for n in im if n.startswith("napi_")]}


def ruby(p):
    b, ex, im = dyn(p)
    init = next(n for n in ex if n.startswith("Init_"))
    return {"extension_kind": "ruby_ext", "init_export": init, "module_name": init[5:], "ruby_module": init[5:],
            "ruby_imports": [n for n in im if n.startswith("rb_")]}


def plain(p):
    b, ex, im = dyn(p)
    assert not any(n.startswith(("PyInit_", "luaopen_", "Init_", "napi_", "node_")) for n in ex)
    return {"extension_kind": "plain_c", "extension_kinds": ["plain_c"], "init_export": "none", "module_name": "none",
            "method_names": "none", "lua_functions": "none", "cffi_functions": "none"}


def ctypes_src(src):
    t = ast.parse(src)
    libs, hv, funcs = [], set(), []
    for n in ast.walk(t):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
            f = n.value.func
            if isinstance(f, ast.Attribute) and f.attr in ("CDLL", "LoadLibrary"):
                libs.append(n.value.args[0].value)
                hv.add(n.targets[0].id)
    for n in ast.walk(t):   # source order: lib.<fn> attribute accesses on the CDLL handle
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in hv:
            funcs.append((n.lineno, n.col_offset, n.attr))
    fs = list(dict.fromkeys(a for _, _, a in sorted(funcs)))
    return {"extension_kind": "ctypes" if libs else "none", "ctypes_libraries": libs or "none",
            "ctypes_functions": fs or "none"}


SRC = ("import ctypes\nlib = ctypes.CDLL(\"libhcfg_bridge.so.1\")\nlib.hcfg_open.argtypes = [ctypes.c_char_p, "
       "ctypes.c_int]\nlib.hcfg_open.restype = ctypes.c_void_p\nlib.hcfg_read.restype = ctypes.c_int\n"
       "print(lib.hcfg_close(None))\n")
SRC2 = "import ctypes\ndll = ctypes.cdll.LoadLibrary(\"hcfgcore.dll\")\ndll.HcfgInit.argtypes = [ctypes.c_uint32]\n"
SRC3 = 'import json; print(json.dumps({"k": "CDLL-free"}))\n'
assert (H / "xbridge_ctypes_caller.py.txt").read_text() == SRC
out = {
    "xbridge_pyext_vault": pyext(H / "xbridge_pyext_vault.bin", False),
    "xbridge_pyext_stripped": pyext(H / "xbridge_pyext_stripped.bin", True),
    "xbridge_cython_beacon": cython(H / "xbridge_cython_beacon.bin"),
    "xbridge_cffi": cffi(H / "xbridge_cffi.bin"),
    "xbridge_napi_addon": napi(H / "xbridge_napi_addon.bin"),
    "xbridge_lua_bridge": lua(H / "xbridge_lua_bridge.bin"),
    "xbridge_ruby_ext": ruby(H / "xbridge_ruby_ext.bin"),
    "xbridge_decoy_plain_c": plain(H / "xbridge_decoy_plain_c.bin"),
    "xbridge_ctypes_caller": dict(ctypes_src(SRC), ctypes_method="source"),
    "xbridge_ctypes_py312": dict(ctypes_src(SRC), ctypes_method="bytecode"),
    "xbridge_ctypes_py314": dict(ctypes_src(SRC2), ctypes_method="bytecode"),
    "xbridge_decoy_pyc": dict(ctypes_src(SRC3)),
    "xbridge_decoy_blob": None,   # `file` -> data / "Zip archive data" stub: neither ELF nor .pyc nor ctypes source
}
print(json.dumps(out, indent=1))
