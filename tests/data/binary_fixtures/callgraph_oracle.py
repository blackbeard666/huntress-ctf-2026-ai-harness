"""Independent call-graph oracle: objdump -d (AT&T text) + nm + pyelftools section bytes.
usage: python3 callgraph_oracle.py <elf> [--names-from <unstripped twin>]
Resolves: call ADDR <f>/<f@plt>, call *GOT(%rip) # <f@VER>, call *%reg via the nearest preceding
mov $imm / lea x(%rip) / mov x(%rip) to that register since the previous call/jmp/ret, call *TAB(,%r,8)."""
import json, re, subprocess, sys
from elftools.elf.elffile import ELFFile

path = sys.argv[1]
twin = sys.argv[sys.argv.index("--names-from") + 1] if "--names-from" in sys.argv else path
nm = {}
for ln in subprocess.run(["nm", "--defined-only", twin], capture_output=True, text=True).stdout.splitlines():
    a, t, n = ln.split(None, 2)
    if t in "tTwW":
        nm[int(a, 16)] = n
stripped = twin != path
name = (lambda a: f"sub_{a:x}") if stripped else (lambda a: nm[a])
f = ELFFile(open(path, "rb"))
got, rel = {}, {}  # readelf -r view via pyelftools: GOT slot -> import name, RELATIVE slot -> addend
for sec in f.iter_sections():
    if sec["sh_type"] in ("SHT_RELA", "SHT_REL") and sec["sh_link"]:
        st = f.get_section(sec["sh_link"])
        for r in sec.iter_relocations():
            if r["r_info_sym"]:
                got[r["r_offset"]] = st.get_symbol(r["r_info_sym"]).name.split("@")[0]
            elif r["r_info_type"] == 8 and "r_addend" in r.entry:
                rel[r["r_offset"]] = r["r_addend"]
def ptr(va):
    if va in rel:
        return rel[va]
    for s in f.iter_sections():
        if s["sh_addr"] <= va < s["sh_addr"] + s["sh_size"] and s["sh_type"] != "SHT_NOBITS":
            return int.from_bytes(s.data()[va - s["sh_addr"]: va - s["sh_addr"] + 8], "little")
dis = subprocess.run(["objdump", "-d", "--no-show-raw-insn", "-j", ".text", "-j", ".init", path],
                     capture_output=True, text=True).stdout.splitlines()
refs = {int(m.group(1), 16) for ln in dis for m in re.finditer(r"# ([0-9a-f]+) <", ln)}  # code-referenced data
refs |= {int(m.group(1), 16) for ln in dis for m in re.finditer(r"\*?0x([0-9a-f]{5,})\(", ln)}
edges, sites, ind, cur, back = [], [], {}, None, []
hdr = re.compile(r"^([0-9a-f]+) <(.+)>:$")
for ln in dis:
    m = hdr.match(ln)
    if m:
        cur, back = name(int(m.group(1), 16)) if not stripped else None, []
        if not stripped:
            cur = m.group(2)
        continue
    m = re.match(r"^\s+([0-9a-f]+):\s+(\S+)\s*(.*)$", ln)
    if not m:
        continue
    ins, ops = m.group(2), m.group(3)
    if stripped:  # caller of a site in a stripped file: nearest twin symbol at or below the address
        a = int(m.group(1), 16)
        cur = name(max(k for k in nm if k <= a)) if any(k <= a for k in nm) else "?"
        cur = "main" if nm.get(max(k for k in nm if k <= a)) == "main" else cur
    if ins == "call":
        tgt, kind = None, None
        d = re.match(r"^[0-9a-f]+ <([^>+]+)>$", ops)
        if d:
            tgt, kind = (d.group(1)[:-4], "plt") if d.group(1).endswith("@plt") else (d.group(1), "direct")
            if kind == "direct" and stripped:
                tgt = "main" if nm.get(int(ops.split()[0], 16)) == "main" else name(int(ops.split()[0], 16))
        elif ops.startswith("*"):
            ind[cur] = ind.get(cur, 0)
            g = re.search(r"# ([0-9a-f]+) <", ops)
            if g and "(%rip)" in ops and int(g.group(1), 16) in got:
                tgt, kind = got[int(g.group(1), 16)], "plt"
            elif g and "(%rip)" in ops:
                ind[cur] += 1
                v = ptr(int(g.group(1), 16))
                tgt, kind = (name(v), "indirect") if v in nm else (None, None)
            r = re.match(r"^\*%(\w+)$", ops)
            if r:
                ind[cur] += 1
                reg = r.group(1)[-2:]
                for pins, pops in reversed(back):
                    dst = pops.split("#")[0].strip().split(",")[-1]
                    if pins in ("test", "cmp") or dst not in ("%" + reg, "%e" + reg, "%r" + reg):
                        continue
                    i = re.match(r"^\$0x([0-9a-f]+),", pops)
                    g = re.search(r"# ([0-9a-f]+) <([^>]+)>", pops)
                    if pins == "mov" and i:
                        v = int(i.group(1), 16)
                        tgt, kind = (("main" if nm.get(v) == "main" else name(v)), "indirect") if v in nm else (None, None)
                    elif pins == "lea" and g:
                        v = int(g.group(1), 16)
                        tgt, kind = (name(v), "indirect") if v in nm else (None, None)
                    elif pins == "mov" and g:
                        if int(g.group(1), 16) in got:
                            tgt, kind = got[int(g.group(1), 16)], "plt"
                        else:
                            v = ptr(int(g.group(1), 16))
                            tgt, kind = (name(v), "indirect") if v in nm else (None, None)
                    break
            t = re.match(r"^\*0x([0-9a-f]+)\(,%\w+,8\)$", ops)
            bt = re.match(r"^\*\(%(\w+),%\w+,8\)$", ops)
            if bt:  # base register loaded by an earlier lea x(%rip),%base  # <table>
                for pins, pops in reversed(back):
                    g = re.search(r"# ([0-9a-f]+) <", pops)
                    if pins == "lea" and g and pops.split("#")[0].strip().endswith("%" + bt.group(1)):
                        t = re.match(r"(0x[0-9a-f]+)", "0x" + g.group(1))
                        break
            if t:
                ind[cur] += 1
                k, seen = int(t.group(1), 16), []
                k0 = k
                while (k == k0 or k not in refs) and ptr(k) in nm:
                    seen.append(name(ptr(k)))
                    k += 8
                for s in seen:
                    sites.append([cur, s, "indirect"])
                back = []
                continue
        if tgt:
            sites.append([cur, tgt, kind])
        back = []
        continue
    if ins in ("ret", "jmp"):
        back = []
        continue
    back.append((ins, ops))
for s in sites:
    if s not in edges:
        edges.append(s)
it = []
for c, t, k in sites:
    if k == "indirect" and t not in it:
        it.append(t)
out = {"edges": edges, "indirect_targets": it,
       "imports_called": list(dict.fromkeys(t for c, t, k in sites if k == "plt")),
       "indirect_calls_by_function": {k: v for k, v in ind.items() if v}}
out["main_callees"] = list(dict.fromkeys(t for c, t, k in edges if c == "main"))
if not stripped and "main" in nm.values():  # BFS over edges from main, local (nm text) functions, address order
    loc = {v: k for k, v in nm.items()}
    seen, todo = {"main"}, ["main"]
    while todo:
        c = todo.pop()
        for e in edges:
            if e[0] == c and e[1] in loc and e[1] not in seen:
                seen.add(e[1]); todo.append(e[1])
    out["reached_from_main"] = sorted(seen - {"main"}, key=loc.get)
print(json.dumps(out))
