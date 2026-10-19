"""Independent oracle for flow_* fixtures (never imports lib/): runs the -DTRACE twin natively for the state sequence /
executed case lines / return value, maps case lines to addresses with `objdump --dwarf=decodedline` (lowest address of
the line inside flow_state, image base subtracted), counts the x*(x+1) predicates in flow_src.c, `file -b` for type.
usage: python3 flow_oracle.py FIXTURE.bin TRACE_EXE|-   -> fixture json on stdout"""
import json, pathlib, re, subprocess, sys

fx, tr = sys.argv[1], sys.argv[2]
H = pathlib.Path(__file__).resolve().parent
fb = subprocess.run(["file", "-b", fx], capture_output=True, text=True).stdout.strip()
name = pathlib.Path(fx).name
facts = {"flattened": "false", "state_sequence": "none", "block_order": "none", "return_value": "none",
         "dispatcher": "none"}
decoy = tr == "-"
if "text" in fb:
    facts = {k: None for k in facts}
elif not decoy:
    out = subprocess.run([tr], capture_output=True, text=True).stdout.split("\n")
    states = [int(l[2:]) for l in out if l.startswith("S ")]
    lines = [int(l[2:]) for l in out if l.startswith("L ")]
    ret = next(int(l[2:]) for l in out if l.startswith("R "))
    pe = fx.endswith("pe_o0.bin")
    hdr = subprocess.run(["objdump", "-h" if pe else "-f", fx], capture_output=True, text=True).stdout
    base = int(re.search(r"ImageBase\s+([0-9a-f]+)", subprocess.run(["objdump", "-p", fx], capture_output=True,
               text=True).stdout).group(1), 16) if pe else 0
    sym = subprocess.run(["objdump", "-t", fx], capture_output=True, text=True).stdout
    m = re.search(r"^([0-9a-f]+) .*\.text\s+([0-9a-f]+)\s+flow_state$", sym, re.M)
    if not pe:
        lo, hi = int(m.group(1), 16), int(m.group(1), 16) + int(m.group(2), 16)
    if pe:   # PE: no symtab -> RVA from the export table, end from the matching .pdata RUNTIME_FUNCTION
        pd = subprocess.run(["objdump", "-p", fx], capture_output=True, text=True).stdout
        ords = dict(re.findall(r"^\s*\[\s*\d+\] \+base\[\s*(\d+)\]\s+([0-9a-f]{8}) Export RVA", pd, re.M))
        o = re.search(r"^\s*\[\s*\d+\] \+base\[\s*(\d+)\]\s+[0-9a-f]+ flow_state$", pd, re.M).group(1)
        lo = base + int(ords[o], 16)
        hi = int(re.search(r"^\s*[0-9a-f]+:\s+%016x\s+([0-9a-f]+)" % lo, pd, re.M).group(1), 16)
    dl = subprocess.run(["objdump", "--dwarf=decodedline", fx], capture_output=True, text=True).stdout
    addr = {}
    for f, ln, a in re.findall(r"^\S*(flow_src\.c)\s+(\d+)\s+0x([0-9a-f]+)", dl, re.M):
        a = int(a, 16)
        if lo <= a < hi:
            addr[int(ln)] = min(addr.get(int(ln), a), a)
    facts = {"flattened": "true", "state_sequence": states, "block_order": [f"0x{addr[l]:x}" for l in lines],
             "return_value": ret, "state_count": len(set(states)), "dispatch_count": len(states),
             "initial_state": f"0x{states[0]:08x}", "final_state": f"0x{states[-1]:08x}", "function": "flow_state",
             "opaque_predicates": (H / "flow_src.c").read_text().count("(x * (x + 1)) % 2 == 0")}
json.dump({"family": "flattening", "encoding": "none", "expected_offset": None, "expected_config": None,
           "expected_facts": facts,
           "generator_cmd": "bash flow_gen.sh   # gcc -O0 PIE + zig cc musl static dense/jump-table (ELF), zig cc -target x86_64-windows-gnu (PE) of flow_src.c / flow_plain.c",
           "oracle_cmd": f"python3 flow_oracle.py {name} <-DTRACE twin>   # run trace build natively + objdump --dwarf=decodedline/-t/-p + file -b",
           "file_b": fb[:60], "decoy": decoy,
           "note": "lib.binary.flattening_field(data, key) per expected_facts key; vocabulary SPECULATIVE (GM label not seen)"},
          sys.stdout, indent=1)
print()
