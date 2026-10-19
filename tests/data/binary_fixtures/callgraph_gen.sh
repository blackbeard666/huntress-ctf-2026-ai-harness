#!/bin/bash
# Build the call-graph fixtures from callgraph_src.c (function-pointer table, `lea/mov reg; call reg`, data pointer).
# usage (repo root): bash tests/data/binary_fixtures/callgraph_gen.sh
set -e
D=$(cd "$(dirname "$0")" && pwd); R=$(cd "$D/../../.." && pwd); W=$(mktemp -d)
Z() { (cd "$W" && PYTHONPATH="$R/tools/pyziglang" python3 -m ziglang cc "$@"); }
gcc -O1 -no-pie -fno-pie -fcf-protection=none -o "$D/callgraph_c_nopie.bin" "$D/callgraph_src.c"
gcc -O1 -fpie -pie -o "$D/callgraph_c_pie.bin" "$D/callgraph_src.c"
strip -o "$D/callgraph_c_pie_stripped.bin" "$D/callgraph_c_pie.bin"
sed 's/__attribute__((noinline))/__declspec(dllexport) __attribute__((noinline))/' "$D/callgraph_src.c" > "$W/cgx.c"
Z -target x86_64-windows-gnu -O1 -fno-optimize-sibling-calls -s -o cgx.exe cgx.c && cp "$W/cgx.exe" "$D/callgraph_pe_exports.bin"
Z -target aarch64-linux-gnu -O1 -o arm.elf "$D/callgraph_src.c" && cp "$W/arm.elf" "$D/callgraph_decoy_aarch64.bin"
printf '#!/bin/sh\n# not a program: call main() then exit\necho call main\n' > "$D/callgraph_decoy_script.bin"
cp "$D/gfortran_d18_flow_v000.bin" "$D/callgraph_d18_fortran.bin"
rm -rf "$W"
