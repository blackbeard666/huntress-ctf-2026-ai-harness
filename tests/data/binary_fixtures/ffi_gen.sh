#!/usr/bin/env bash
# Generator for the ffi_*.bin fixtures (lib.binary.ffi_facts). Independent writers: javac -h (JNI export names),
# gcc -shared, cargo cdylib, go -buildmode=c-shared. usage: ffi_gen.sh <workdir>  (writes *.bin next to this script)
set -euo pipefail
OUT=$(cd "$(dirname "$0")" && pwd); W=${1:?workdir}; mkdir -p "$W"; cd "$W"

# 1. JNI: javac -h emits the mangled export names (underscore -> _1, overloads -> __<sig>); the C side implements them.
mkdir -p jni/com/huntress/ctf_2026 && cat > jni/com/huntress/ctf_2026/Vault.java <<'EOF'
package com.huntress.ctf_2026;
public class Vault {
    static { System.loadLibrary("vault"); }
    public native String unlock(String key);
    public native int check(int[] a);
    public static native int check(String s);
    private native void ping_now();
}
EOF
(cd jni && javac -h . -d . com/huntress/ctf_2026/Vault.java)
{ echo 'int JNI_OnLoad(void *vm, void *r) { (void)vm; (void)r; return 0x10006; }'
  grep -o 'Java_[A-Za-z0-9_]*' jni/com_huntress_ctf_2026_Vault.h | sort -u | sed 's/.*/void *&(void *e, void *o) { (void)e; return o; }/'
  echo 'const char *vault_banner(void) { return "HCFG"; }'; } > jni/vault.c
gcc -shared -fPIC -O1 -o "$OUT/ffi_jni_vault.bin" jni/vault.c

# 2. CPython extension module: PyInit_<mod> against the real Python.h.
cat > pyext.c <<'EOF'
#include <Python.h>
static PyObject *secret(PyObject *s, PyObject *a) { return PyUnicode_FromString("hcfg"); }
static PyMethodDef M[] = {{"secret", secret, METH_NOARGS, 0}, {0}};
static struct PyModuleDef D = {PyModuleDef_HEAD_INIT, "hcfg_native", 0, -1, M};
PyMODINIT_FUNC PyInit_hcfg_native(void) { return PyModule_Create(&D); }
EOF
gcc -shared -fPIC -O1 $(/usr/bin/python3-config --includes) -o "$OUT/ffi_pyext.bin" pyext.c

# 3. Rust cdylib with #[no_mangle] extern "C" exports.
mkdir -p rcd/src && cat > rcd/Cargo.toml <<'EOF'
[package]
name = "hcfgplug"
version = "0.1.0"
edition = "2021"
[lib]
crate-type = ["cdylib"]
[profile.release]
strip = "symbols"
EOF
cat > rcd/src/lib.rs <<'EOF'
#[no_mangle]
pub extern "C" fn hcfg_plugin_init(x: u32) -> u32 { x.wrapping_mul(0x9e37_79b9) ^ 0x4843_4647 }
#[no_mangle]
pub extern "C" fn hcfg_plugin_name() -> *const u8 { b"rusty\0".as_ptr() }
#[no_mangle]
pub static HCFG_PLUGIN_ABI: u32 = 3;
EOF
(cd rcd && CARGO_TARGET_DIR="$W/rcd/target" cargo build --release --offline -q)
cp rcd/target/release/libhcfgplug.so "$OUT/ffi_rust_cdylib.bin"

# 4. Go c-shared with //export functions.
mkdir -p gcs && cat > gcs/go.mod <<'EOF'
module example.com/hcfg/goplug

go 1.22
EOF
cat > gcs/main.go <<'EOF'
package main

import "C"

//export HcfgGoInit
func HcfgGoInit(x C.int) C.int { return x * 7 }

//export HcfgGoName
func HcfgGoName() *C.char { return C.CString("gopher") }

func main() {}
EOF
(cd gcs && GOCACHE="$W/gocache" GOFLAGS=-mod=mod GOTOOLCHAIN=local go build -buildmode=c-shared -trimpath -buildvcs=false \
    -o "$OUT/ffi_go_c_shared.bin" .)
rm -f "$OUT/ffi_go_c_shared.h"

# 5. OCaml C stubs (no OCaml toolchain): CAMLprim-shaped caml_* exports importing the OCaml runtime API.
cat > ocs.c <<'EOF'
typedef long value;
extern value caml_copy_string(const char *);
extern value caml_alloc_string(unsigned long);
value caml_hcfg_decode(value v) { (void)v; return caml_copy_string("HCFG"); }
value caml_hcfg_blob(value n) { return caml_alloc_string((unsigned long)n); }
static int helper(void) { return 1; }
int ocs_internal_check(void) { return helper(); }
EOF
gcc -shared -fPIC -O1 -o "$OUT/ffi_ocaml_stub.bin" ocs.c

# 6. DECOY: plain C .so whose .rodata merely *mentions* JNI / PyInit / crosscall2 names (none exported).
cat > decoy.c <<'EOF'
const char *names[] = {"Java_com_evil_Decoy_run", "PyInit_decoy", "crosscall2", "JNI_OnLoad", "rustc version"};
int plain_entry(int i) { return names[i & 3][0]; }
int plain_other(void) { return 42; }
EOF
gcc -shared -fPIC -O1 -o "$OUT/ffi_decoy_plain_c.bin" decoy.c

# 7. DECOY: not an ELF at all (a Java source renamed .so).
cp jni/com/huntress/ctf_2026/Vault.java "$OUT/ffi_decoy_notelf.bin"
