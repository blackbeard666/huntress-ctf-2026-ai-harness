#!/bin/bash
# Script-runtime native extension fixtures for lib.binary.extension_bridge_facts (compiled / byte-compiled, never run
# by the extractor). usage (repo root): bash tests/data/binary_fixtures/xbridge_gen.sh
set -e
ROOT=$(cd "$(dirname "$0")/../../.." && pwd); OUT="$ROOT/tests/data/binary_fixtures"
T=${TMPDIR:-/tmp}/xbridge; rm -rf "$T"; mkdir -p "$T"; cd "$T"
PY312=$ROOT/.venv/bin/python
INC312=$(ls -d "$ROOT"/tools/python/cpython-3.12*/include/python3.12 | head -1)
# 1) CPython extension: module doc, 3 methods, mixed flags/docs, static impls (PyModuleDef + PyMethodDef via RELATIVE)
cat > vault.c <<'C'
#define PY_SSIZE_T_CLEAN
#include <Python.h>
static PyObject *vault_unlock(PyObject *s, PyObject *a) { return PyUnicode_FromString("HCFG"); }
static PyObject *vault_peek(PyObject *s, PyObject *a, PyObject *k) { Py_RETURN_NONE; }
static PyObject *vault_xor_key(PyObject *s, PyObject *o) { return PyLong_FromLong(0x5a); }
static PyMethodDef VaultMethods[] = {
  {"unlock", vault_unlock, METH_NOARGS, "Return the unlock tag."},
  {"peek", (PyCFunction)(void (*)(void))vault_peek, METH_VARARGS | METH_KEYWORDS, "Peek at a slot."},
  {"xor_key", vault_xor_key, METH_O, NULL},
  {NULL, NULL, 0, NULL}
};
static struct PyModuleDef vaultmodule = {PyModuleDef_HEAD_INIT, "hcfg_vault", "Native vault bridge.", -1, VaultMethods};
PyMODINIT_FUNC PyInit_hcfg_vault(void) { return PyModule_Create(&vaultmodule); }
C
gcc -shared -fPIC -O1 $(/usr/bin/python3-config --includes) -o "$OUT/xbridge_pyext_vault.bin" vault.c
cp "$OUT/xbridge_pyext_vault.bin" hcfg_vault$(/usr/bin/python3-config --extension-suffix)
# 1b) same source, stripped (-s): impl names gone -> sub_<hex>; table walk unchanged
gcc -shared -fPIC -O2 -s $(/usr/bin/python3-config --includes) -o "$OUT/xbridge_pyext_stripped.bin" vault.c
# 2) Cython 3.3 (.venv) against CPython 3.12 headers
mkdir -p pkg && cat > pkg/beacon.pyx <<'P'
"""Beacon bridge."""
def ping(host):
    return "pong:" + host
cpdef int score(int a, int b):
    return a * 31 + b
P
"$ROOT/.venv/bin/cython" -3 pkg/beacon.pyx -o beacon.c
gcc -shared -fPIC -O1 -I"$INC312" -o "$OUT/xbridge_cython_beacon.bin" beacon.c
# 3) cffi out-of-line API mode (.venv cffi 2.1)
cat > build_cffi.py <<'P'
import cffi
ffi = cffi.FFI()
ffi.cdef("int hc_add(int, int); const char *hc_tag(void);")
ffi.set_source("_hcfg_cffi", 'int hc_add(int a, int b){return a+b;} const char *hc_tag(void){return "HCFG";}')
ffi.emit_c_code("hcfg_cffi.c")
P
$PY312 build_cffi.py && gcc -shared -fPIC -O1 -I"$INC312" -o "$OUT/xbridge_cffi.bin" hcfg_cffi.c
# 4) Node N-API addon shape: napi_register_module_v1 export, napi_* imports left undefined (as node provides them)
cat > napi.c <<'C'
typedef struct napi_env__ *napi_env; typedef struct napi_value__ *napi_value; typedef void *napi_callback_info;
typedef napi_value (*napi_callback)(napi_env, napi_callback_info);
extern int napi_create_function(napi_env, const char *, unsigned long, napi_callback, void *, napi_value *);
extern int napi_set_named_property(napi_env, napi_value, const char *, napi_value);
extern int napi_create_string_utf8(napi_env, const char *, unsigned long, napi_value *);
static napi_value Beacon(napi_env env, napi_callback_info i) { napi_value v; napi_create_string_utf8(env, "HCFG", 4, &v); return v; }
__attribute__((visibility("default"))) napi_value napi_register_module_v1(napi_env env, napi_value exports) {
  napi_value fn; napi_create_function(env, 0, 0, Beacon, 0, &fn); napi_set_named_property(env, exports, "beacon", fn); return exports; }
__attribute__((visibility("default"))) int node_api_module_get_api_version_v1(void) { return 8; }
C
gcc -shared -fPIC -O1 -o "$OUT/xbridge_napi_addon.bin" napi.c
# 5) Lua C module: luaopen_hcfg_bridge + static luaL_Reg[] (Lua 5.4 API declared by hand: no lua headers installed)
cat > lmod.c <<'C'
typedef struct lua_State lua_State; typedef int (*lua_CFunction)(lua_State *);
typedef struct luaL_Reg { const char *name; lua_CFunction func; } luaL_Reg;
extern void lua_createtable(lua_State *, int, int); extern void luaL_setfuncs(lua_State *, const luaL_Reg *, int);
extern void luaL_checkversion_(lua_State *, double, unsigned long); extern void lua_pushstring(lua_State *, const char *);
extern void lua_pushinteger(lua_State *, long long);
static int l_tag(lua_State *L) { lua_pushstring(L, "HCFG"); return 1; }
static int l_port(lua_State *L) { lua_pushinteger(L, 8443); return 1; }
static int l_key(lua_State *L) { lua_pushstring(L, "k3y"); return 1; }
static const luaL_Reg bridge_funcs[] = {{"tag", l_tag}, {"port", l_port}, {"key", l_key}, {0, 0}};
int luaopen_hcfg_bridge(lua_State *L) { luaL_checkversion_(L, 504, 136); lua_createtable(L, 0, 3); luaL_setfuncs(L, bridge_funcs, 0); return 1; }
C
gcc -shared -fPIC -O1 -o "$OUT/xbridge_lua_bridge.bin" lmod.c
# 6) Ruby C extension: Init_hcfg_ruby + rb_define_* imports (ruby headers present but the shape is what matters)
cat > rbx.c <<'C'
typedef unsigned long VALUE; extern VALUE rb_define_module(const char *);
extern void rb_define_module_function(VALUE, const char *, VALUE (*)(VALUE), int); extern VALUE rb_str_new_cstr(const char *);
static VALUE tag(VALUE self) { return rb_str_new_cstr("HCFG"); }
void Init_hcfg_ruby(void) { VALUE m = rb_define_module("HcfgRuby"); rb_define_module_function(m, "tag", tag, 0); }
C
gcc -shared -fPIC -O1 -o "$OUT/xbridge_ruby_ext.bin" rbx.c
# 7) ctypes caller (.pyc partner): byte-compiled by .venv CPython 3.12 (bytecode path) and system 3.14 (strings path)
cat > caller.py <<'P'
import ctypes
lib = ctypes.CDLL("libhcfg_bridge.so.1")
lib.hcfg_open.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.hcfg_open.restype = ctypes.c_void_p
lib.hcfg_read.restype = ctypes.c_int
print(lib.hcfg_close(None))
P
cp caller.py "$OUT/xbridge_ctypes_caller.py.txt"
$PY312 -c "import py_compile; py_compile.compile('caller.py', cfile='$OUT/xbridge_ctypes_py312.bin', doraise=True)"
cat > caller2.py <<'P'
import ctypes
dll = ctypes.cdll.LoadLibrary("hcfgcore.dll")
dll.HcfgInit.argtypes = [ctypes.c_uint32]
P
/usr/bin/python3 -c "import py_compile; py_compile.compile('caller2.py', cfile='$OUT/xbridge_ctypes_py314.bin', doraise=True)"
# 8) decoys: plain C .so (no init export), a .pyc with no ctypes use, a non-ELF/non-pyc blob
cat > plain.c <<'C'
int hcfg_sum(int a, int b) { return a + b; }
const char *hcfg_name(void) { return "PyInit_fake luaopen_fake"; }
C
gcc -shared -fPIC -O1 -o "$OUT/xbridge_decoy_plain_c.bin" plain.c
echo 'import json; print(json.dumps({"k": "CDLL-free"}))' > nope.py
$PY312 -c "import py_compile; py_compile.compile('nope.py', cfile='$OUT/xbridge_decoy_pyc.bin', doraise=True)"
printf 'PK\003\004 not an extension, mentions PyInit_x and luaopen_y\n' > "$OUT/xbridge_decoy_blob.bin"
echo "generated in $OUT"
