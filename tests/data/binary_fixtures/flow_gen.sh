#!/bin/bash
# Flattened-dispatcher fixtures: gcc (ELF) / zig cc = clang (PE, MinGW-free) from flow_src.c, oracle = the same source
# built with -DTRACE and RUN natively (state + case-line trace) + objdump --dwarf=decodedline (line -> address).
set -e
H="$(cd "$(dirname "$0")" && pwd)"; R="$(cd "$H/../../.." && pwd)"; W="${TMPDIR:-/tmp}/flowgen"; mkdir -p "$W"
Z() { (cd "$W" && PYTHONPATH="$R/tools/pyziglang" python3 -m ziglang cc "$@"); }
gcc -O0 -g -fno-stack-protector -o "$H/flow_elf_o0_pie.bin" "$H/flow_src.c"
gcc -O0 -g -DTRACE -o "$W/t_o0" "$H/flow_src.c"
Z -target x86_64-linux-musl -O0 -gdwarf-4 -fno-sanitize=all -DDENSE -DK=0 -o "$W/jt" "$H/flow_src.c"; cp "$W/jt" "$H/flow_elf_clang_jt.bin"   # static, jump-table dispatch
gcc -O0 -g -DDENSE -DK=0 -DTRACE -o "$W/t_jt" "$H/flow_src.c"
Z -target x86_64-windows-gnu -O0 -gdwarf-4 -fno-sanitize=all -DK=0x0BADF00Du -o "$W/flow_pe.exe" "$H/flow_src.c"
cp "$W/flow_pe.exe" "$H/flow_pe_o0.bin"
gcc -O0 -g -DTRACE -DK=0x0BADF00Du -o "$W/t_pe" "$H/flow_src.c"   # same C semantics -> same state trace
gcc -O0 -o "$H/flow_decoy_plain.bin" "$H/flow_plain.c"
printf 'while(1){switch(state){case 1: state=2; break;}}  -- C text, not a program\n' > "$H/flow_decoy_text.bin"
python3 "$H/flow_oracle.py" "$H/flow_elf_o0_pie.bin" "$W/t_o0" > "$H/flow_elf_o0_pie.json"
python3 "$H/flow_oracle.py" "$H/flow_elf_clang_jt.bin" "$W/t_jt" > "$H/flow_elf_clang_jt.json"
python3 "$H/flow_oracle.py" "$H/flow_pe_o0.bin" "$W/t_pe" > "$H/flow_pe_o0.json"
python3 "$H/flow_oracle.py" "$H/flow_decoy_plain.bin" - > "$H/flow_decoy_plain.json"
python3 "$H/flow_oracle.py" "$H/flow_decoy_text.bin" - > "$H/flow_decoy_text.json"
