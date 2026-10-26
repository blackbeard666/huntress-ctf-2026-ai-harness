"""Writes the unwind_*.json fixtures: expected_facts come only from unwind_oracle.py (gdb + readelf)."""
import json, subprocess
def oracle(exe, core):
    return json.loads(subprocess.run(["python3", "unwind_oracle.py", exe, core], capture_output=True, text=True, check=True).stdout)
GEN = "sh unwind_gen.sh   # gcc -O0 -fno-omit-frame-pointer -no-pie / gcc -O2 -fomit-frame-pointer (PIE) unwind_crasher.c; core = gdb generate-core-file at the SIGSEGV"
def put(name, data, exe, facts, oc, decoy=False, note=""):
    json.dump({"family": "static_stack_unwind", "encoding": "none", "expected_offset": None, "expected_config": None,
               "data_file": data, "exe_file": exe, "expected_facts": facts, "generator_cmd": GEN, "oracle_cmd": oc,
               "decoy": decoy, "note": note}, open(f"{name}.json", "w"), indent=1)
for v, how in (("o0", "rbp-framed code, CFI rbp+16"), ("o2", "-fomit-frame-pointer: CFI rsp+N only")):
    f = oracle(f"unwind_{v}_exe.bin", f"unwind_{v}_core.bin")
    put(f"unwind_{v}_cfi", f"unwind_{v}_core.bin", f"unwind_{v}_exe.bin", f,
        f"python3 unwind_oracle.py unwind_{v}_exe.bin unwind_{v}_core.bin   # gdb bt/info frame/info symbol/info proc mappings + readelf --debug-dump=frames-interp",
        note=f"lib.binary.stack_unwind_field(core, key, exe=exe); {how}. Field names SPECULATIVE (GM label not seen)")
f = oracle("unwind_o0_exe.bin", "unwind_o0_core.bin")
keep = {k: v for k, v in f.items() if k in ("unwind_frame_count", "unwind_return_addresses", "unwind_frame_sizes",
                                            "unwind_frame_modules", "unwind_module_offsets") or
        (k.startswith("unwind_frame_") and k.endswith(("_pc", "_size", "_module")))}
keep.update({"unwind_functions": json.dumps(["none"] * int(f["unwind_frame_count"]), separators=(",", ":")),
             "unwind_method": "frame_pointer"})
put("unwind_o0_fpchain", "unwind_o0_core.bin", None, keep,
    "python3 unwind_oracle.py unwind_o0_exe.bin unwind_o0_core.bin   # same gdb walk; symbol-free columns only (no exe handed in -> functions none)",
    note="core alone: saved-rbp/ret chain over the stack PT_LOAD; must equal gdb's addresses/CFA sizes")
fr = oracle("unwind_o2_exe.bin", "unwind_o2_core.bin")
put("unwind_decoy_exe_only", "unwind_o2_exe.bin", None,
    {"unwind_frames": "none", "unwind_frame_count": "none", "unwind_functions": "none",
     "cfa_frame_size:leaf": fr["cfa_frame_size:leaf"], "cfa_frame_size:process": fr["cfa_frame_size:process"]},
    "readelf --debug-dump=frames-interp unwind_o2_exe.bin (max CFA offset per FDE); no core -> no frames",
    decoy=True, note="executable handed in as the 'core': frame fields none, CFA sizes still answerable")
put("unwind_decoy_text", "unwind_crasher.c", None,
    {"unwind_frames": "none", "unwind_frame_count": "none", "cfa_frame_size:leaf": "none", "unwind_method": "none"},
    "file unwind_crasher.c -> C source, ASCII text (not ELF)", decoy=True, note="not an ELF at all")
PEGEN = "sh unwind_gen.sh   # zig cc -target x86_64-windows-gnu -O0 -fno-omit-frame-pointer / -O2 -fomit-frame-pointer (MinGW PE32+, functions dllexport'ed), x86-windows-gnu PE32 decoy"
for v in ("o0", "o2"):
    f = json.loads(subprocess.run(["python3", "unwind_pe_oracle.py", f"unwind_pe_{v}.bin"], capture_output=True, text=True, check=True).stdout)
    json.dump({"family": "static_stack_unwind", "encoding": "none", "expected_offset": None, "expected_config": None,
               "data_file": f"unwind_pe_{v}.bin", "exe_file": None, "expected_facts": f, "generator_cmd": PEGEN,
               "oracle_cmd": f"python3 unwind_pe_oracle.py unwind_pe_{v}.bin   # GNU objdump -x (pei-x86-64 UNWIND_INFO dump) + objdump -p exports",
               "decoy": False, "note": "PE x64 .pdata/.xdata UWOP codes; cfa_frame_size = prolog allocation + 8 (return address)"},
              open(f"unwind_pe_{v}.json", "w"), indent=1)
json.dump({"family": "static_stack_unwind", "encoding": "none", "expected_offset": None, "expected_config": None,
           "data_file": "unwind_pe_x86_decoy.bin", "exe_file": None,
           "expected_facts": {"cfa_frame_size:leaf": "none", "pe_unwind_codes:leaf": "none", "pe_runtime_function_count": "none",
                              "unwind_frames": "none"},
           "generator_cmd": PEGEN, "oracle_cmd": "file unwind_pe_x86_decoy.bin -> PE32 Intel i386 (no x64 .pdata unwind data); objdump -x shows no Function Table",
           "decoy": True, "note": "i386 PE with the same exports: x64 UNWIND_INFO fields absent"}, open("unwind_pe_x86_decoy.json", "w"), indent=1)
