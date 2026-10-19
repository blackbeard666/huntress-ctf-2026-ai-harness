"""Independent oracle for the switch_* fixtures (lib.binary.switch_tables). Never imports lib.binary / capstone:
GNU objdump -d -M intel (x86-64) / aarch64-linux-gnu-objdump -d (AArch64) text for the dispatch idiom (cmp imm + ja /
b.hi / b.ls, lea rip `# addr` / adrp+add / adr, movsxd / jmp [idx*8+t] / ldrb+add sxtb, jmp reg / br), pyelftools for
the table bytes and the symbol table; callee = first `call`/`bl` line of the case block (objdump's own <sym> label,
`sub_<hex>` when objdump prints none). gfortran SELECT CASE: delegates to gfortran_d18_oracle.py (case_table /
case_procedures / default_procedure). Primary switch = first by address in a function not starting with `_`.
usage: python3 switch_oracle.py <file.bin>   -> expected_facts JSON"""
import json, re, subprocess, sys
from elftools.elf.elffile import ELFFile

path = sys.argv[1]
none = {"case_count": "none", "cases": "none", "case_callees": "none", "default_symbol": "none"}
try:
    ef = ELFFile(open(path, "rb"))
    arch = ef["e_machine"]
    segs = [s for s in ef.iter_segments() if s["p_type"] == "PT_LOAD"]
    syms = []
    for sec in ef.iter_sections():
        if sec["sh_type"] in ("SHT_SYMTAB", "SHT_DYNSYM"):
            syms += [(s["st_value"], s["st_size"], s.name) for s in sec.iter_symbols()
                     if s["st_info"]["type"] == "STT_FUNC" and s["st_value"] and s.name]
except Exception:
    print(json.dumps(None if open(path, "rb").read(4) != b"\x7fELF" else none)); sys.exit()
if b"_gfortran_select_string" in open(path, "rb").read():
    g = json.loads(subprocess.run([sys.executable, "gfortran_d18_oracle.py", path], capture_output=True, text=True).stdout)
    cp = g["case_procedures"]
    cs = [{"case": c, "target": n, "symbol": cp.get(c, "none"), "callee": cp.get(c, "none")} for c, n in g["case_table"] if c != "default"]
    print(json.dumps({"case_count": len(cs), "cases": cs, "case_callees": {c["case"]: c["callee"] for c in cs},
                      "default_symbol": g["default_procedure"]}, indent=1)); sys.exit()


def rd(va, n):
    for s in segs:
        if s["p_vaddr"] <= va and va + n <= s["p_vaddr"] + s["p_filesz"]:
            d = s.data()
            return d[va - s["p_vaddr"]:va - s["p_vaddr"] + n]


def sym(va):
    best = None
    for v, sz, n in syms:
        if v == va:
            return n
        if v < va < v + sz:
            best = f"{n}+0x{va - v:x}"
    return best or "none"


a64 = arch == "EM_AARCH64"
od = "aarch64-linux-gnu-objdump" if a64 else "objdump"
txt = subprocess.run([od, "-d", "-w", "--no-show-raw-insn"] + ([] if a64 else ["-M", "intel"]) + [path],
                     capture_output=True, text=True).stdout.splitlines()
ins, func = [], None
for ln in txt:
    m = re.match(r"^([0-9a-f]+) <(.+)>:", ln)
    if m:
        func = m.group(2)
        continue
    m = re.match(r"^\s*([0-9a-f]+):\s+(.*)$", ln)
    if m:
        ins.append((int(m.group(1), 16), m.group(2).strip(), func))
pos = {a: k for k, (a, _, _) in enumerate(ins)}


def callee(va):
    k = pos.get(va)
    for a, t, _ in ins[k:k + 16] if k is not None else []:
        m = re.match(r"(?:call|bl)\s+([0-9a-f]+)(?: <([^>]+)>)?", t)
        if m:
            return m.group(2) if m.group(2) and "+" not in m.group(2) else f"sub_{int(m.group(1), 16):x}"
        if re.match(r"(ret|jmp|b|br|notrack)\b", t):
            break
    return "none"


sws = []
for k, (a, t, f) in enumerate(ins):
    if a64:
        m = re.fullmatch(r"br\s+(x\d+)", t)
    else:
        m = re.fullmatch(r"(?:notrack )?jmp\s+(r\w+|QWORD PTR \[(\w+)\*8\+0x([0-9a-f]+)\])", t)
    if not m:
        continue
    win = ins[max(0, k - 24):k]
    n = dflt = tbl = None
    low = 0
    for j, (b, u, _) in enumerate(win):
        mc = re.fullmatch(r"cmp\s+(\w+),\s*#?(0x[0-9a-f]+|\d+)", u)
        if mc and j + 1 < len(win):
            nx = win[j + 1][1]
            mj = re.match(r"(ja|b\.hi|b\.ls)\s+([0-9a-f]+)", nx)
            if mj:
                n = int(mc.group(2), 0) + 1
                dflt = int(mj.group(2), 16) if mj.group(1) != "b.ls" else win[j + 1][0] + 4
                for b2, u2, _ in reversed(win[:j]):
                    ms = re.fullmatch(r"(sub|add)\s+(\w+),\s*(?:\w+,\s*)?#?(-?0x[0-9a-f]+|-?\d+)", u2)
                    if ms and ms.group(2)[1:] in mc.group(1):
                        v = int(ms.group(3), 0)
                        v = v - (1 << 32) if v >= 1 << 31 else v   # `add edi,0xfffffffd` = -3
                        low = v * (1 if ms.group(1) == "sub" else -1)
                        break
    if not n:
        continue
    if a64:
        adrp = [int(re.search(r"(?:adrp|adr)\s+x\d+,\s*([0-9a-f]+)", u).group(1), 16) for _, u in [(0, w[1]) for w in win]
                if re.match(r"adrp\s", u)]
        adds = [int(re.search(r"#(0x[0-9a-f]+)", u).group(1), 16) for _, u, _ in win if re.match(r"add\s+x\d+, x\d+, #0x", u)]
        adr = [int(re.search(r"adr\s+x\d+,\s*([0-9a-f]+)", u).group(1), 16) for _, u, _ in win if re.match(r"adr\s", u)]
        ld = next((u for _, u, _ in win if re.match(r"ldr[bh]?\s+w\d+, \[x\d+, w\d+, uxtw", u)), None)
        if not (adrp and adds and adr and ld):
            continue
        tbl, w = adrp[-1] + adds[-1], (1 if ld.startswith("ldrb") else 2 if ld.startswith("ldrh") else 4)
        raw = rd(tbl, n * w)
        tg = [adr[-1] + int.from_bytes(raw[i * w:(i + 1) * w], "little", signed=True) * 4 for i in range(n)]
    elif m.group(2):
        tbl = int(m.group(3), 16)
        raw = rd(tbl, n * 8)
        tg = [int.from_bytes(raw[i * 8:(i + 1) * 8], "little") for i in range(n)]
    else:
        lea = [int(re.search(r"# ([0-9a-f]+)", u).group(1), 16) for _, u, _ in win if u.startswith("lea") and "[rip+" in u]
        if not lea or not any(u.startswith("movsxd") for _, u, _ in win):
            continue
        tbl = lea[-1]
        raw = rd(tbl, n * 4)
        tg = [tbl + int.from_bytes(raw[i * 4:(i + 1) * 4], "little", signed=True) for i in range(n)]
    cs = [{"case": i + low, "target": f"0x{x:x}", "symbol": sym(x), "callee": callee(x)} for i, x in enumerate(tg) if x != dflt]
    sws.append((f or "none", a, cs, callee(dflt) if callee(dflt) != "none" else sym(dflt)))
if not sws:
    print(json.dumps(none, indent=1)); sys.exit()
f, a, cs, d = min(sws, key=lambda s: (s[0].startswith("_"), s[1]))
print(json.dumps({"case_count": len(cs), "cases": cs, "case_callees": {str(c["case"]): c["callee"] for c in cs},
                  "default_symbol": d}, indent=1))
