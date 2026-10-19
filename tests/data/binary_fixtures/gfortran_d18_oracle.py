"""Independent oracle for the gfortran_d18_* fixtures (D18 "Flow State" gfortran shape). Never imports lib.binary:
readelf -sW (STT_FILE, LOCAL FUNC `name.N`, MAIN__), readelf -dW (NEEDED), nm -D --undefined-only (imports),
objdump -d -M intel (the edi/esi/r9d immediates before the _gfortran_select_string / _gfortran_get_environment_variable_i4
calls + a tiny cmp/je/sub/jne/jmp walk from the select call to the procedure each case reaches), pyelftools for the bytes
at the table / string addresses, readelf -p .comment. Prints the expected_facts JSON.
usage: python3 gfortran_d18_oracle.py <file.bin>"""
import json, re, struct, subprocess, sys
from elftools.elf.elffile import ELFFile

path = sys.argv[1]
run = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout   # noqa: E731
facts = {"source_file": "none", "main_program": "none", "procedures": [], "procedures_mangled": [],
         "procedures_by_address": [], "procedures_by_address_mangled": [], "case_table": [], "case_values": [],
         "case_map": {}, "case_procedures": {}, "default_procedure": "none", "env_var": "none", "needed": [],
         "imports": [], "compiler_banner": "none"}
try:
    ef = ELFFile(open(path, "rb"))
    ef.iter_sections()
    ok = True
except Exception:   # truncated / not an ELF
    ok = False
syms = []
for ln in run("readelf", "-sW", path).splitlines():
    p = ln.split()
    if len(p) >= 8 and p[0].endswith(":") and p[0][:-1].isdigit():
        syms.append((p[7], p[3], p[4], int(p[1], 16), p[6]))   # name type bind value ndx
if ok:
    files = [s[0] for s in syms if s[1] == "FILE" and re.search(r"\.f\d*$", s[0], re.I)]
    facts["source_file"] = files[0] if files else "none"
    facts["main_program"] = "MAIN__" if any(s[0] == "MAIN__" and s[1] == "FUNC" for s in syms) else "none"
    pr = [s for s in syms if s[1] == "FUNC" and s[2] == "LOCAL" and re.match(r"^[A-Za-z]\w*\.\d+$", s[0])]
    facts["procedures_mangled"] = [s[0] for s in pr]
    facts["procedures"] = [s[0].rsplit(".", 1)[0] for s in pr]
    ba = sorted(pr, key=lambda s: s[3])
    facts["procedures_by_address_mangled"] = [s[0] for s in ba]
    facts["procedures_by_address"] = [s[0].rsplit(".", 1)[0] for s in ba]
    facts["needed"] = re.findall(r"\(NEEDED\)\s+Shared library: \[([^\]]+)\]", run("readelf", "-dW", path))
    facts["imports"] = sorted({l.split()[-1].split("@")[0] for l in run("nm", "-D", "--undefined-only", path).splitlines()
                               if "_gfortran_" in l})
    cm = re.findall(r"\]\s+(\S.*)$", run("readelf", "-p", ".comment", path), re.M)
    facts["compiler_banner"] = cm[0].strip() if cm else "none"

    def mem(va, n):
        for seg in ef.iter_segments():
            if seg["p_type"] == "PT_LOAD" and seg["p_vaddr"] <= va < seg["p_vaddr"] + seg["p_filesz"]:
                return seg.data()[va - seg["p_vaddr"]:va - seg["p_vaddr"] + n]
        return b""
    ins = []   # (addr, mnemonic, operands)
    for ln in run("objdump", "-d", "--no-show-raw-insn", "-M", "intel", "-j", ".text", path).splitlines():
        m = re.match(r"\s+([0-9a-f]+):\s+(\S+)\s*(.*)$", ln)
        if m:
            ins.append((int(m.group(1), 16), m.group(2), m.group(3)))
    idx = {a: k for k, (a, _, _) in enumerate(ins)}

    def before(k, reg):
        for a, mn, op in reversed(ins[max(0, k - 25):k]):
            m = re.match(rf"{reg},0x([0-9a-f]+)$", op)
            if mn == "mov" and m:
                return int(m.group(1), 16)
    sel = None
    for k, (a, mn, op) in enumerate(ins):
        if mn == "call" and "<_gfortran_get_environment_variable_i4@plt>" in op and facts["env_var"] == "none":
            s = mem(before(k, "edi"), before(k, "r9d") or 64)
            facts["env_var"] = re.match(rb"\w+", s).group(0).decode()
        if mn == "call" and "<_gfortran_select_string@plt>" in op and sel is None:
            sel, tbl, cnt = k, before(k, "edi"), before(k, "esi")
    if sel is not None:
        tab = []
        for j in range(cnt):
            lp, ll, hp, hl, no = struct.unpack("<QQQQi", mem(tbl + 40 * j, 36))
            if not lp and not hp:
                tab.append(["default", no])
            else:
                lo, hi = mem(lp, ll).decode(), mem(hp, hl).decode()
                tab.append([lo if lo == hi else f"{lo}:{hi}", no])
        facts["case_table"] = tab
        facts["case_values"] = [t[0] for t in tab if t[0] != "default"]
        facts["case_map"] = {t[0]: t[1] for t in tab if t[0] != "default"}
        paddr = {s[3]: s[0].rsplit(".", 1)[0] for s in pr}

        def walk(eax):
            k, flag = sel + 1, None
            for _ in range(200):
                a, mn, op = ins[k]
                m = re.match(r"eax,0x([0-9a-f]+)$", op)
                if mn == "cmp" and m:
                    flag = eax == int(m.group(1), 16)
                elif mn == "sub" and m:
                    eax -= int(m.group(1), 16)
                    flag = eax == 0
                elif mn == "mov" and m and int(m.group(1), 16) in paddr:
                    return paddr[int(m.group(1), 16)]
                elif mn in ("je", "jne", "jmp"):
                    if mn == "jmp" or (mn == "je") == flag:
                        k = idx[int(op.split()[0], 16)]
                        continue
                elif mn == "call" and op.split()[0].isalnum() and int(op.split()[0], 16) in paddr:
                    return paddr[int(op.split()[0], 16)]
                k += 1
        if paddr:
            facts["case_procedures"] = {t[0]: walk(t[1]) for t in tab if t[0] != "default"}
            facts["default_procedure"] = walk(next((t[1] for t in tab if t[0] == "default"), 0))
print(json.dumps(facts, indent=1))
