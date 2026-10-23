"""Writes ffi_*.json expected facts from INDEPENDENT readers (never lib.binary): `readelf --dyn-syms -W` (export /
import names in table order), `readelf -p .comment` (rustc), `go version -m` (Go buildinfo), the `javac -h` header
comments (JNI Method / Signature per export) and `javap` (class name), and a real CPython import of the extension.
usage (repo root, after ffi_gen.sh <workdir>): python3 tests/data/binary_fixtures/ffi_oracle.py <workdir>"""
import json, pathlib, re, subprocess, sys
here, W = pathlib.Path(__file__).parent, pathlib.Path(sys.argv[1])
GEN = "bash tests/data/binary_fixtures/ffi_gen.sh <workdir>"
sh = lambda *a: subprocess.run(a, capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "GOTOOLCHAIN": "local",
                                                                      "HOME": str(W)}).stdout


def dynsym(p):
    ex, im = [], []
    for ln in sh("readelf", "--dyn-syms", "-W", str(p)).splitlines():
        c = ln.split()
        if len(c) < 8 or not c[0].rstrip(":").isdigit() or c[0] == "0:":
            continue
        name = c[7].split("@")[0]
        if c[6] == "UND":
            im.append(name)
        elif c[4] in ("GLOBAL", "WEAK", "UNIQUE") and c[5] in ("DEFAULT", "PROTECTED") and c[3] != "SECTION":
            ex.append(name)
    return ex, im


def write(stem, facts, oracle, decoy=False):
    p = here / f"ffi_{stem}.bin"
    j = {"family": "ffi_boundary", "file": p.name, "decoy": decoy, "generator_cmd": GEN, "oracle_cmd": oracle,
         "expected_facts": facts}
    (here / f"ffi_{stem}.json").write_text(json.dumps(j, indent=1) + "\n")


RE = "readelf --dyn-syms -W <bin> (defined GLOBAL/WEAK, table order; UND = imports)"
# JNI: header comments give Method + Signature per mangled export; javap gives the dotted class name.
ex, _ = dynsym(here / "ffi_jni_vault.bin")
hdr = next((W / "jni").glob("*.h")).read_text()
cls = re.search(r"class (\S+)", sh("javap", "-cp", str(W / "jni"), "com.huntress.ctf_2026.Vault")).group(1)
meta = {m.group(3): (m.group(1), m.group(2)) for m in re.finditer(
    r"Method:\s+(\S+)\s+\*\s+Signature:\s+(\S+)\s+\*/\s+JNIEXPORT \S+ JNICALL (\S+)", hdr)}
jm = [{"symbol": n, "class": cls, "method": meta[n][0],
       "signature": meta[n][1][1:meta[n][1].index(")")] if "__" in n[5:] else "none"} for n in ex if n in meta]
write("jni_vault", {"ffi_kind": "jni", "ffi_kinds": ["jni"], "exports": ex, "export_count": str(len(ex)),
                    "jni_methods": jm, "jni_class": jm[0]["class"], "jni_method": jm[0]["method"],
                    "jni_onload": "true", "jni_onunload": "false", "python_module": "none", "go_version": "none"},
      RE + " + javac -h header Method/Signature comments + javap class name")
# CPython extension: import it for real under the interpreter whose Python.h built it.
ex, _ = dynsym(here / "ffi_pyext.bin")
mod = sh("/usr/bin/python3", "-I", "-c", "import importlib.machinery as m,importlib.util as u,sys;"
         "l=m.ExtensionFileLoader('hcfg_native',sys.argv[1]);s=u.spec_from_loader('hcfg_native',l);"
         "x=u.module_from_spec(s);l.exec_module(x);print(x.__name__, x.secret())", str(here / "ffi_pyext.bin")).split()
write("pyext", {"ffi_kind": "python_ext", "ffi_kinds": ["python_ext"], "exports": ex, "python_module": mod[0],
                "jni_methods": "none", "jni_onload": "false", "rustc_version": "none"},
      RE + " + /usr/bin/python3 ExtensionFileLoader import -> module.__name__")
# Rust cdylib: .comment carries the rustc version.
ex, _ = dynsym(here / "ffi_rust_cdylib.bin")
rv = re.search(r"rustc version (.+)", sh("readelf", "-p", ".comment", str(here / "ffi_rust_cdylib.bin"))).group(1)
write("rust_cdylib", {"ffi_kind": "rust_cdylib", "ffi_kinds": ["rust_cdylib"], "exports": ex, "user_exports": ex,
                      "export_count": str(len(ex)), "rustc_version": rv.strip(), "go_version": "none",
                      "jni_methods": "none", "python_module": "none"}, RE + " + readelf -p .comment")
# Go c-shared: `go version -m`; //export names = the plain names whose _cgoexp_<hash>_ twin is exported.
ex, _ = dynsym(here / "ffi_go_c_shared.bin")
gv = sh("go", "version", "-m", str(here / "ffi_go_c_shared.bin")).splitlines()
rows = [ln.strip().split("\t") for ln in gv[1:]]
setting = {r[1].partition("=")[0]: r[1].partition("=")[2] for r in rows if r[0] == "build"}
twins = {re.sub(r"^_cgoexp_[0-9a-f]+_", "", n) for n in ex if n.startswith("_cgoexp_")}
write("go_c_shared", {"ffi_kind": "go_c_shared", "ffi_kinds": ["go_c_shared"], "exports": ex,
                      "export_count": str(len(ex)), "go_exports": [n for n in ex if n in twins],
                      "user_exports": [n for n in ex if n in twins],
                      "go_version": gv[0].split(": ")[1], "go_path": next(r[1] for r in rows if r[0] == "path"),
                      "go_module": next(r[1] for r in rows if r[0] == "mod"),
                      "go_module_version": next(r[2] for r in rows if r[0] == "mod"),
                      "go_buildmode": setting["-buildmode"], "go_settings": setting, "go_deps": "none",
                      "jni_methods": "none", "python_module": "none"}, RE + " + go version -m <bin>")
# OCaml stubs (synthetic, no OCaml toolchain): caml_* exports + caml_* runtime imports.
ex, im = dynsym(here / "ffi_ocaml_stub.bin")
write("ocaml_stub", {"ffi_kind": "ocaml_stub", "ffi_kinds": ["ocaml_stub"], "exports": ex,
                     "ocaml_stubs": [n for n in ex if n.startswith("caml_")],
                     "ocaml_runtime_imports": [n for n in im if n.startswith("caml_")], "python_module": "none"}, RE)
# Decoys.
ex, _ = dynsym(here / "ffi_decoy_plain_c.bin")
write("decoy_plain_c", {"ffi_kind": "plain_c", "ffi_kinds": ["plain_c"], "exports": ex, "jni_methods": "none",
                        "jni_onload": "false", "python_module": "none", "go_version": "none", "go_exports": "none",
                        "rustc_version": "none", "ocaml_stubs": "none"},
      RE + " (JNI/PyInit/crosscall2/rustc names live only in .rodata strings)", decoy=True)
write("decoy_notelf", None, "file <bin> -> Java source, ASCII text (not ELF): cannot answer", decoy=True)
