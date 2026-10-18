#!/usr/bin/env bash
# language_of fixtures: every .bin built by an independent compiler / archiver (never by lib.binary).
# usage (repo root): bash tests/data/binary_fixtures/langof_gen.sh
set -euo pipefail
OUT=$(cd "$(dirname "$0")" && pwd); W=${TMPDIR:-/tmp}/langof_gen; rm -rf "$W"; mkdir -p "$W"; cd "$W"
printf '#include <stdio.h>\nint main(void){puts("hello c");return 0;}\n' > c.c
gcc -O2 -o "$OUT/langof_c_gcc.bin" c.c
printf '#include <iostream>\n#include <string>\nstruct S{virtual std::string f(){return "cpp";}};\nint main(){S s;std::cout<<s.f()<<"\\n";}\n' > p.cpp
clang++-18 -O2 -o "$OUT/langof_cpp_clang.bin" p.cpp
# decoy: a plain C program whose string literals name other runtimes' symbols (not linked against them)
printf '#include <stdio.h>\nint main(void){puts("caml_startup ghczmprim_GHC _gfortran_set_args kfun:main _vinit cob_init");return 0;}\n' > dc.c
gcc -O2 -o "$OUT/langof_decoy_c_cuestrings.bin" dc.c
printf 'public class Hello { public static void main(String[] a){ System.out.println("java"); } }\n' > Hello.java
javac -d . Hello.java && cp Hello.class "$OUT/langof_java_class.bin"
cp "$OUT/jvm_class_kotlin_meta.bin" "$OUT/langof_kotlin_class.bin"        # kotlinc-built class (jvm_gen.sh)
cp "$OUT/dnmeta_exe_net10.bin" "$OUT/langof_csharp_net10.bin"              # dotnet build C# exe (dnmeta_gen.sh)
dotnet new console -lang "F#" -o fs --force >/dev/null && (cd fs && dotnet build -c Release -o out >/dev/null)
cp fs/out/fs.dll "$OUT/langof_fsharp_dll.bin"
printf '(module (memory 1) (func (export "f") (result i32) i32.const 7) (data (i32.const 0) "lang"))\n' > m.wat
wat2wasm m.wat -o "$OUT/langof_wasm_wat.bin"
mkdir z && printf 'not a class\n' > z/readme.txt && (cd z && zip -q ../nojvm.zip readme.txt) && cp nojvm.zip "$OUT/langof_decoy_zip_noclass.bin"
printf 'GCC: (GNU) 13.2 caml_startup kfun:main MEI\014\013\012\013\016 just text\n' > "$OUT/langof_decoy_text_impostor.bin"
