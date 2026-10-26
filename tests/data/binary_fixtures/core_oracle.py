"""Independent oracle for core_* fixtures: gdb / gdb-multiarch (signal, siginfo, registers, stack word, auxv,
`info symbol $pc`), readelf -n (NT_FILE mappings, build-id), file(1) (ET_CORE?), pyelftools (NT_PRPSINFO fname/psargs).
Never imports lib/. usage: python3 core_oracle.py core_X.bin core_X_exe.elf  -> JSON facts on stdout."""
import json, re, signal, subprocess, sys
from elftools.elf.elffile import ELFFile

core, exe = sys.argv[1], sys.argv[2]
out = {}
ft = subprocess.run(["file", "-b", core], capture_output=True, text=True).stdout
out["core_is_core"] = "true" if " core file" in ft else "false"
if out["core_is_core"] == "false":
    print(json.dumps(out)); sys.exit(0)
a64 = "aarch64" in ft
w = "w" if "32-bit" in ft else "g"
cmds = ["p $_siginfo.si_signo", "p $_siginfo.si_code", "p $_siginfo._sifields._sigfault.si_addr", "p/x $pc",
        "p/x $sp", "info symbol $pc", f"x/{w}x $sp", "info auxv", "p/x $" + ("x0" if a64 else "rax" if w == "g" else "eax")]
g = subprocess.run(["gdb-multiarch" if a64 else "gdb", "-nx", "-batch", "-iex", "set debuginfod enabled off",
                                              "-iex", "set sysroot /nonexistent"]   # companion exe symbols only
                   + sum((["-ex", c] for c in cmds), []) + [exe, core], capture_output=True, text=True, timeout=60).stdout
m = re.search(r"terminated with signal (SIG\w+)", g)
if m:
    out["core_signal"] = m.group(1)
    out["core_signal_number"] = str(signal.Signals[m.group(1)].value)
vals = dict(re.findall(r"^\$(\d+) = (.*)$", g, re.M))
seq = iter(sorted(vals, key=int))
def nxt(pat):
    for k in sorted(vals, key=int):
        if re.fullmatch(pat, vals[k]):
            v = vals.pop(k); return v
    return None
if "Unable to read siginfo" not in g:
    signo, code = nxt(r"-?\d+"), nxt(r"-?\d+")
    out["core_si_signo"], out["core_si_code"] = signo, code
    addr = nxt(r"\(void \*\) .*")
    if addr and int(code) > 0:
        out["core_fault_address"] = hex(int(addr.split()[2], 16))
out["core_pc"], out["core_sp"] = nxt(r"0x[0-9a-f]+"), nxt(r"0x[0-9a-f]+")
out["core_reg_" + ("x0" if a64 else "rax" if w == "g" else "eax")] = nxt(r"0x[0-9a-f]+")
m = re.search(r"^(\w+) \+ (\d+) in section", g, re.M)
if m:
    out["core_pc_function"], out["core_pc_function_offset"] = m.group(1), hex(int(m.group(2)))
elif "No symbol matches $pc" in g:
    out["core_pc_function"] = out["core_pc_function_offset"] = "none"
m = re.search(r"^0x[0-9a-f]+(?: <[^>]*>)?:\s+(0x[0-9a-f]+)", g, re.M)
if m:
    out["core_stack_top"] = hex(int(m.group(1), 16))
m = re.search(r"AT_ENTRY\s+.*?(0x[0-9a-f]+)", g)
out["core_entry"] = m.group(1) if m else "none"
m = re.search(r'AT_EXECFN\s+.*?0x[0-9a-f]+ "([^"]*)"', g)
out["core_execfn"] = m.group(1) if m else "none"
# NT_FILE via readelf -n: the mapping holding pc
rn = subprocess.run(["readelf", "-nW", core], capture_output=True, text=True).stdout
pc = int(out["core_pc"], 16) if out.get("core_pc") else -1
ent = re.findall(r"^\s+(0x[0-9a-f]+)\s+(0x[0-9a-f]+)\s+(0x[0-9a-f]+)\n\s+(\S+)", rn, re.M)
pg = re.search(r"Page size: (\d+)", rn)
for s, e, o, nm in ent:
    if int(s, 16) <= pc < int(e, 16):
        out["core_pc_module"] = nm
        out["core_pc_module_offset"] = hex(pc - int(s, 16) + int(o, 16) * int(pg.group(1)))
if ent:
    out["core_mapped_file_count"] = str(len(ent))
xb = re.search(r"Build ID: ([0-9a-f]+)", subprocess.run(["readelf", "-nW", exe], capture_output=True, text=True).stdout)
out["core_exe_build_id"] = xb.group(1) if xb else "none"
# NT_PRPSINFO through pyelftools
with open(core, "rb") as fh:
  try:
    ef = ELFFile(fh)
    for seg in ef.iter_segments():
        if seg["p_type"] == "PT_NOTE":
            for n in seg.iter_notes():
                if n["n_type"] == "NT_PRPSINFO":
                    d = n["n_desc"]
                    out["core_fname"] = d["pr_fname"].split(b"\0")[0].decode()
                    out["core_psargs"] = d["pr_psargs"].split(b"\0")[0].decode().rstrip() or "none"
  except Exception:   # truncated note segment: no prpsinfo
    out["core_fname"] = out["core_psargs"] = "none"
if "core_signal" not in out:   # gdb found no crash at all -> absent
    for k in ("core_signal", "core_pc", "core_fault_address", "core_pc_function"):
        out[k] = "none"
print(json.dumps({k: v for k, v in out.items() if v is not None}, indent=1))
