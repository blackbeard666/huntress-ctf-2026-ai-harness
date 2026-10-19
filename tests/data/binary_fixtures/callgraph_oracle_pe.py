"""Independent PE x64 call-graph oracle: objdump -p (exports, import IAT slots, .pdata function table),
objdump -h (section map for pointer reads) and objdump -d text. Facts for exported (named) functions only.
usage: python3 callgraph_oracle_pe.py <exe>"""
import json, re, subprocess, sys

path = sys.argv[1]
raw = open(path, "rb").read()
P = subprocess.run(["objdump", "-p", path], capture_output=True, text=True).stdout
base = int(re.search(r"^ImageBase\s+([0-9a-f]+)", P, re.M).group(1), 16)
iat, exp, pdata = {}, {}, []
for blk in re.split(r"\n\s*DLL Name: ", P)[1:]:
    for m in re.finditer(r"^\s+([0-9a-f]{8})\s+<none>\s+[0-9a-f]{4}\s+(\S+)", blk, re.M):
        iat[base + int(m.group(1), 16)] = m.group(2)
eat = re.search(r"Export Address Table -- Ordinal Base (\d+)\n.*?\n((?:\s+\[.*\n)+)", P)
npt = re.search(r"\[Ordinal/Name Pointer\] Table -- Ordinal Base \d+\n.*?\n((?:\s+\[.*\n)+)", P)
addr_by_ord = {int(m.group(1)): int(m.group(2), 16) for m in re.finditer(r"\+base\[\s*(\d+)\]\s+([0-9a-f]+) Export RVA", eat.group(2))} if eat else {}
for m in re.finditer(r"\+base\[\s*(\d+)\]\s+[0-9a-f]{4} (\S+)", npt.group(1) if npt else ""):
    exp[base + addr_by_ord[int(m.group(1))]] = m.group(2)
for m in re.finditer(r"^\s+[0-9a-f]{16}:\s+([0-9a-f]{16})\s+([0-9a-f]{16})\s+[0-9a-f]{16}$", P, re.M):
    pdata.append((int(m.group(1), 16), int(m.group(2), 16)))
H = subprocess.run(["objdump", "-h", path], capture_output=True, text=True).stdout
secs = [(int(m.group(2), 16), int(m.group(1), 16), int(m.group(3), 16))
        for m in re.finditer(r"^\s+\d+ \S+\s+([0-9a-f]+)\s+([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)", H, re.M)]
def ptr(va):
    for a, sz, off in secs:
        if a <= va < a + sz:
            return int.from_bytes(raw[off + va - a: off + va - a + 8], "little")
D = subprocess.run(["objdump", "-d", "--no-show-raw-insn", path], capture_output=True, text=True).stdout.splitlines()
ins = {}
for ln in D:
    m = re.match(r"^\s+([0-9a-f]+):\s+(.*)$", ln)
    if m:
        ins[int(m.group(1), 16)] = m.group(2)
refs = {int(m.group(1), 16) for t in ins.values() for m in re.finditer(r"# 0x([0-9a-f]+)", t)}  # code-referenced data


def thunk(t):
    m = re.match(r"jmp\s+\*0x[0-9a-f]+\(%rip\)\s+# 0x([0-9a-f]+)", ins.get(t, ""))
    return iat.get(int(m.group(1), 16)) if m else None
nm = lambda a: exp.get(a, f"sub_{a:x}")
sites, ind = [], {}
for lo, hi in sorted(pdata):
    if lo not in exp:
        continue
    cur, back = exp[lo], []
    for a in sorted(k for k in ins if lo <= k < hi):
        t = ins[a]
        op, _, ops = t.partition(" ")
        ops = ops.strip()
        if op == "call":
            tgt, kind = None, None
            if re.match(r"^0x[0-9a-f]+$", ops):
                v = int(ops, 16)
                tgt, kind = (thunk(v), "plt") if thunk(v) else (nm(v), "direct")
            elif ops.startswith("*"):
                ind[cur] = ind.get(cur, 0) + 1
                g = re.search(r"# 0x([0-9a-f]+)", ops)
                if g and int(g.group(1), 16) in iat:
                    tgt, kind = iat[int(g.group(1), 16)], "plt"
                    ind[cur] -= 1
                r = re.match(r"^\*%(\w+)$", ops) or re.match(r"^\*\(%(\w+),%\w+,8\)$", ops)
                if r:
                    for pop, pops in reversed(back):
                        if pops.split("#")[0].strip().split(",")[-1] != "%" + r.group(1):
                            continue
                        g = re.search(r"# 0x([0-9a-f]+)", pops)
                        if g and pop == "lea" and "(%r8" not in ops and "*(" not in ops:
                            tgt, kind = nm(int(g.group(1), 16)), "indirect"
                        elif g and pop == "lea":
                            k = int(g.group(1), 16)
                            k0 = k
                            while (k == k0 or k not in refs) and ptr(k) in exp:
                                sites.append([cur, exp[ptr(k)], "indirect"]); k += 8
                        elif g and pop == "mov":
                            tgt, kind = nm(ptr(int(g.group(1), 16))), "indirect"
                        break
            if tgt:
                sites.append([cur, tgt, kind])
            back = []
        elif op in ("ret", "jmp"):
            back = []
        else:
            back.append((op, ops))
edges = []
for s in sites:
    if s not in edges:
        edges.append(s)
print(json.dumps({"named_edges": edges,
                  "indirect_targets": list(dict.fromkeys(t for c, t, k in sites if k == "indirect")),
                  "named_indirect_calls_by_function": ind}))
