#!/bin/bash
# Regenerate the mdmp_* fixtures: stdlib struct writer (mdmp_gen.py) -> independent oracle (mdmp_oracle.py:
# skelsec minidump 0.0.24 reader + pefile + capstone + file) fills expected_facts. Run from anywhere.
set -e
cd "$(dirname "$0")"
python3 mdmp_gen.py
meta() {   # name decoy companion note
  python3 - "$@" <<'PY'
import json, sys
n, decoy, comp, note = sys.argv[1:5]
m = {"family": "windows_minidump", "encoding": "none", "expected_offset": None, "expected_config": None,
     "fields": ["mdmp_is_minidump", "mdmp_exception_code", "mdmp_pc", "mdmp_fault_module"],
     "generator_cmd": f"bash mdmp_gen.sh   # python3 mdmp_gen.py (stdlib struct MINIDUMP writer): {note}",
     "oracle_cmd": f"python3 mdmp_oracle.py {n}.bin {comp} --write {n}.json   # skelsec minidump 0.0.24 (tools/pydeps-minidump) + pefile + capstone + file",
     "decoy": decoy == "1",
     "note": "lib.binary.minidump_field(dump, key, pe=companion) per expected_facts key; fact names SPECULATIVE (GM label not seen)"}
if comp:
    m["companion"] = comp
open(n + ".json", "w").write(json.dumps(m, indent=1) + "\n")
PY
  python3 mdmp_oracle.py "$1.bin" $3 --write "$1.json" >/dev/null
}
meta mdmp_x64_av_write 0 callgraph_pe_exports.bin "AMD64 AV write *0x10 at cgx.exe op_mul+0x4, code bytes from the PE"
meta mdmp_x86_div0 0 "" "x86 WOW64_CONTEXT 0xC0000094 in calc.dll+0x1234, Memory64List"
meta mdmp_x64_cppeh 0 callgraph_pe_exports.bin "AMD64 0xE06D7363 4 EH params raised in KERNELBASE.dll (companion is cgx.exe: no function)"
meta mdmp_x64_dep 0 "" "AMD64 AV DEP (info[0]=8) executing 0x41414141 outside every module"
meta mdmp_decoy_noexc 1 callgraph_pe_exports.bin "live dump, no ExceptionStream -> exception fields none"
meta mdmp_decoy_magic 1 "" "PAGEDU64 kernel-dump magic over the AV dump -> None"
meta mdmp_decoy_trunc 1 "" "first 64 bytes of the AV dump (directory past EOF) -> None"
