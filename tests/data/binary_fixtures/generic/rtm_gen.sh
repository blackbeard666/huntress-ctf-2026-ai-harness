#!/usr/bin/env bash
# gf-runtime-markers (prebuild): has_zig_runtime / has_v_runtime members. Zig members built with zig 0.17 build-exe
# (pip ziglang under tools/ziglang); rtm_d10_zig.exe / rtm_d27_v_*.elf are GM corpus members (D28 evidence, d10 PE
# twin + d27 V gcc/tcc builds) copied verbatim. expected from binutils `strings -a` / `nm` + the toolchain ground truth
# (never lib.binary). RTM_REBUILD=1 rebuilds the zig members.
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="$(cd ../../../.. && pwd)/tools/ziglang${PYTHONPATH:+:$PYTHONPATH}"
G_ZPE="python3 -m ziglang build-exe -target x86_64-windows-gnu -O ReleaseSafe -fstrip -femit-bin=rtm_zig_pe.exe rtm_src/rtm_zig.zig"
G_ZELF="python3 -m ziglang build-exe -target x86_64-linux-musl -O ReleaseSafe -fstrip -femit-bin=rtm_zig_elf.elf rtm_src/rtm_zig.zig"
if [ "${RTM_REBUILD:-0}" = 1 ]; then $G_ZPE; $G_ZELF; fi
ENUM='{"kind": "enum", "accepted_values": ["true", "false"]}'
U="In evidence.zip, use the d99-- member. "
emit() {   # emit MEMBER FIELD QUESTION EXPECTED(json) GENERATOR ORACLE [decoy]
  python3 - "$@" <<'PY'
import json, sys
m, f, q, exp, gen, orc = sys.argv[1:7]
out = {"kind": "generic_field", "member": m, "field": f, "question": q,
       "answer_format": {"kind": "enum", "accepted_values": ["true", "false"]},
       "expected": json.loads(exp), "generator_cmd": gen, "oracle_cmd": orc}
if len(sys.argv) > 7:
    out["decoy"] = True
open(f"{m.rsplit('.', 1)[0]}.{f}.json", "w").write(json.dumps(out, indent=1) + "\n")
PY
}
tf() { [ "$(bash -c "$1")" -gt 0 ] && echo '"true"' || echo '"false"'; }
O_Z="strings -a MEMBER | grep -cE 'attempt to unwrap error|integer cast truncated bits'   # Zig std panic texts; >0 -> true"
O_V="{ strings -a MEMBER | grep -c '^V panic: '; nm MEMBER 2>/dev/null | grep -cE ' (_vinit|builtin__)'; } | paste -sd+ | bc   # V C-backend; >0 -> true"
Q_Z="${U}Does the member carry the Zig standard-library runtime? Submit lowercase true or false."
Q_V="${U}Does the member carry the V (vlang) runtime? Submit lowercase true or false."
for m in rtm_zig_pe.exe rtm_zig_elf.elf; do
  g=$([ "$m" = rtm_zig_pe.exe ] && echo "$G_ZPE" || echo "$G_ZELF")
  emit $m has_zig_runtime "$Q_Z" "$(tf "${O_Z//MEMBER/$m}")" "$g" "${O_Z//MEMBER/$m}"
done
emit rtm_d10_zig.exe has_zig_runtime "$Q_Z" "$(tf "${O_Z//MEMBER/rtm_d10_zig.exe}")" "GM D28 corpus: d10--sample.exe (Zig PE twin of d10), copied verbatim" "${O_Z//MEMBER/rtm_d10_zig.exe}"
emit gf_pe_imports.exe has_zig_runtime "$Q_Z" "$(tf "${O_Z//MEMBER/gf_pe_imports.exe}")" "see ie_gen.sh (C source built with zig cc: zig toolchain, no Zig runtime)" "${O_Z//MEMBER/gf_pe_imports.exe}" decoy
emit gf_c_events.bin has_zig_runtime "$Q_Z" "$(tf "${O_Z//MEMBER/gf_c_events.bin}")" "see gen_generic.sh (gcc C ELF)" "${O_Z//MEMBER/gf_c_events.bin}" decoy
for m in rtm_d27_v_gcc.elf rtm_d27_v_tcc.elf; do
  emit $m has_v_runtime "$Q_V" "$(tf "${O_V//MEMBER/$m}")" "GM D28 corpus: d27--sample-${m:8:3}.elf (V program, C backend), copied verbatim" "${O_V//MEMBER/$m}"
done
emit gf_c_events.bin has_v_runtime "$Q_V" "$(tf "${O_V//MEMBER/gf_c_events.bin}")" "see gen_generic.sh (gcc C ELF)" "${O_V//MEMBER/gf_c_events.bin}" decoy
emit rtm_zig_elf.elf has_v_runtime "$Q_V" "$(tf "${O_V//MEMBER/rtm_zig_elf.elf}")" "$G_ZELF" "${O_V//MEMBER/rtm_zig_elf.elf}" decoy
emit rtm_d27_v_gcc.elf has_zig_runtime "$Q_Z" "$(tf "${O_Z//MEMBER/rtm_d27_v_gcc.elf}")" "GM D28 corpus: d27--sample-gcc.elf" "${O_Z//MEMBER/rtm_d27_v_gcc.elf}" decoy
