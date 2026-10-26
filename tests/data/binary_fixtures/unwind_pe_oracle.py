"""Independent oracle for the unwind_pe_* fixtures: GNU objdump -x (pei-x86-64 .pdata function table + per-function
UNWIND_INFO dump) and objdump -p (export table names).  usage: python3 unwind_pe_oracle.py unwind_pe_o2.bin"""
import json, re, subprocess, sys
x = subprocess.run(["objdump", "-x", sys.argv[1]], capture_output=True, text=True).stdout
p = subprocess.run(["objdump", "-p", sys.argv[1]], capture_output=True, text=True).stdout
base = int(re.search(r"ImageBase\s+([0-9a-f]+)", p).group(1), 16)
eat = [int(a, 16) for a in re.findall(r"\[\s*\d+\] \+base\[\s*\d+\] ([0-9a-f]{8}) Export RVA", p)]
names = {eat[int(o)]: n for o, n in re.findall(r"\[\s*\d+\] \+base\[\s*\d+\]\s+([0-9a-f]{4}) (\w+)\s*$", p, re.M)}
rows = re.findall(r"^ [0-9a-f]+:\t([0-9a-f]{16}) [0-9a-f]{16} [0-9a-f]{16}$", x, re.M)
facts = {"pe_runtime_function_count": str(sum(1 for r in rows if int(r, 16)))}
for m in re.finditer(r"\(rva: [0-9a-f]+\): ([0-9a-f]+) - [0-9a-f]+\n\tVersion: \d, Flags: (.*)\n\tNbr codes: \d+, Prologue size: "
                     r"0x([0-9a-f]+), Frame offset: 0x[0-9a-f]+, Frame reg: (\w+)\n((?:\t  pc\+.*\n)*)", x):
    rva = int(m.group(1), 16) - base
    if rva not in names:
        continue
    ops, alloc, pushed = [], 0, []
    for l in m.group(5).splitlines():
        l = l.split(": ", 1)[1]
        if l.startswith("push "):
            ops.append(f"UWOP_PUSH_NONVOL({l[5:]})"); alloc += 8; pushed.append(l[5:])
        elif l.startswith("alloc "):
            n = int(l.rsplit("- ", 1)[1], 16); alloc += n
            ops.append(("UWOP_ALLOC_SMALL" if "small" in l else "UWOP_ALLOC_LARGE") + f"({n})")
        elif l.startswith("FPReg"):
            ops.append("UWOP_SET_FPREG")
        elif l.startswith("save xmm"):
            ops.append("UWOP_SAVE_XMM128")
        else:
            ops.append("?" + l)
    n = names[rva]
    facts.update({f"cfa_frame_size:{n}": str(alloc + 8), f"pe_stack_alloc:{n}": str(alloc),
                  f"pe_frame_register:{n}": m.group(4), f"pe_prolog_size:{n}": str(int(m.group(3), 16)),
                  f"pe_unwind_codes:{n}": json.dumps(ops, separators=(",", ":")) if ops else "none",
                  f"pe_pushed_registers:{n}": json.dumps(pushed, separators=(",", ":")) if pushed else "none",
                  f"cfa_frame_size:{hex(rva)}": str(alloc + 8)})
print(json.dumps(facts, indent=1))
