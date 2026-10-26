"""Independent oracle for cverdict_* fixtures (no lib/ import): the CERT GDB `exploitable` plugin transcript written by
cverdict_gen.sh (rule, rating, gdb bt, $_siginfo, regs, x/i $pc, info proc mappings) + readelf -lWd --dyn-syms for the
checksec-style mitigations. fault_class / CWE come from the plugin rule + gdb backtrace function names (table below).
usage: python3 -I cverdict_oracle.py <name>   (writes cverdict_<name>.json)"""
import json, re, subprocess, sys, pathlib
H = pathlib.Path(__file__).resolve().parent
n = sys.argv[1]
t = (H / f"cverdict_{n}.expl").read_text()
exe = H / f"cverdict_{n}_exe.elf"
rule = re.search(r"^Short description: (\w+)", t, re.M).group(1)
rating = re.search(r"^Exploitability Classification: (\w+)", t, re.M).group(1)
signo, code = map(int, re.search(r"SIGINFO signo=(\d+) code=(-?\d+)", t).groups())
siaddr = int(re.search(r"SIADDR (\S+)", t).group(1), 0)
pc, sp = (int(v, 16) for v in re.search(r"REGS pc=(\S+) sp=(\S+)", t).groups())
retw = int(re.search(r"RETWORD (\S+)", t).group(1), 0)
insn = re.search(r"=> 0x[0-9a-f]+(?: <[^>]*>)?:\s*(.*)", t)
bt = re.findall(r"^#\d+\s+(?:0x[0-9a-f]+ in )?([\w.]+)", t, re.M)
maps = [(int(a, 16), int(b, 16), rest.strip()) for a, b, rest in
        re.findall(r"^\s*(0x[0-9a-f]+)\s+(0x[0-9a-f]+)\s+0x[0-9a-f]+\s+0x[0-9a-f]+\s+[rwxsp-]{4}\s*(.*)$", t, re.M)]
has_fa = signo in (4, 7, 8, 11) and code > 0
fa = siaddr if has_fa else None
tgt = retw if insn and insn.group(1).startswith("ret") and code == 128 else fa


def region(a):
    if a is None:
        return "none"
    if a < 0x10000:
        return "null_page"
    if 0x7FFFFFFFFFFF < a < 0xFFFF800000000000:
        return "non_canonical"
    for s, e, name in maps:
        if s <= a < e:
            return "stack" if name == "[stack]" else "heap" if name == "[heap]" or not name else "module"
    return "unmapped"


cls = {"ReturnAv": "stack_overrun", "SegFaultOnPc": "exec_non_code", "BranchAv": "exec_non_code",
       "StackCodeExecution": "exec_non_code", "StackBufferOverflow": "stack_canary", "DestAv": "wild_write",
       "SourceAv": "wild_read", "DestAvNearNull": "null_deref", "SourceAvNearNull": "null_deref",
       "SegFaultOnPcNearNull": "null_deref", "BranchAvNearNull": "null_deref",
       "FloatingPointException": "divide_by_zero", "HeapError": "heap_corruption", "AbortSignal": "abort"}[rule]
if rule == "HeapError" and re.search(r'malloc_printerr \(str=[^"]*"[^"]*double free', t):
    cls = "double_free"
if rule == "AbortSignal" and "__assert_fail" in bt:
    cls = "assertion"
cwe = {"stack_overrun": 121, "exec_non_code": 119, "stack_canary": 121, "wild_write": 787, "wild_read": 125,
       "null_deref": 476, "divide_by_zero": 369, "heap_corruption": 122, "double_free": 415, "assertion": 617}.get(cls)
re_ = lambda *a: subprocess.run(["readelf", "-W", *a, str(exe)], capture_output=True, text=True).stdout
lw, dw, sw, hw = re_("-l"), re_("-d"), re_("--dyn-syms"), re_("-h")
gs = re.search(r"GNU_STACK(?:\s+\S+){5}\s+(\w+)", lw)
syms = set(re.findall(r"\s(__\w+_chk(?:_fail)?)(?=@|\s|$)", sw, re.M))
now = re.search(r"\(BIND_NOW\)|Flags:.*\bNOW\b", dw) is not None
tf = lambda b: "true" if b else "false"
mit = {"canary": tf("__stack_chk_fail" in syms), "nx": tf(gs is not None and "E" not in gs.group(1)),
       "pie": tf("DYN" in re.search(r"Type:\s+(\w+)", hw).group(1) and "PIE" in dw),
       "relro": ("full" if now else "partial") if "GNU_RELRO" in lw else "none",
       "fortify": tf(any(s.endswith("_chk") and not s.startswith("__stack_chk") for s in syms)), "cfg": "false"}
exp = {"exploitability": rating, "exploitable_rule": rule, "fault_class": cls,
       "cwe": f"CWE-{cwe}" if cwe else "none", "signal_number": str(signo), "si_code": str(code),
       "fault_address": hex(fa) if fa is not None else "none", "fault_address_class": region(tgt), **mit}
(H / f"cverdict_{n}.json").write_text(json.dumps({
    "family": "crash_verdict", "encoding": "none", "expected_offset": None, "expected_config": None,
    "expected_facts": exp, "companion": exe.name,
    "oracle_other_tags": re.findall(r"(\w+) \(\d+/22\)", (re.search(r"^Other tags: (.*)$", t, re.M) or [0, ""])[1]),
    "generator_cmd": "bash cverdict_gen.sh   # gcc crasher, gdb run -> generate-core-file at the fatal signal",
    "oracle_cmd": f"python3 -I cverdict_oracle.py {n}   # CERT GDB exploitable plugin (tools/exploitable) + gdb "
                  "$_siginfo / info proc mappings / bt + readelf -lWd --dyn-syms",
    "decoy": False,
    "note": "lib.binary.crash_verdict_field(core, key, exe=companion); fact names SPECULATIVE (GM label not seen)"},
    indent=1) + "\n")
print(n, exp)
