"""Independent oracle for cobfacts_* fixtures: readelf -dW (NEEDED), nm -D (cob_* dynsyms), objdump -d -M intel
(argument loads before each call/jmp <cob_check_version@plt> / <cob_set_programid@plt>, register copies followed)
and pyelftools (the C string at the loaded address). usage: python3 cobfacts_oracle.py <file.bin>"""
import json, re, subprocess, sys
from elftools.elf.elffile import ELFFile

path = sys.argv[1]
run = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout   # noqa: E731
needed = re.findall(r"\(NEEDED\)\s+Shared library: \[([^\]]+)\]", run("readelf", "-dW", path))
imports = sorted({l.split()[-1].split("@")[0] for l in run("nm", "-D", path).splitlines()
                  if l.split() and l.split()[-1].startswith("cob_")})
rt = any(n.startswith("libcob.so") for n in needed) or "cob_init" in imports
f = open(path, "rb"); elf = ELFFile(f)


def cstr(va):
    for s in elf.iter_sections():
        if s["sh_type"] != "SHT_NOBITS" and s["sh_addr"] <= va < s["sh_addr"] + s["sh_size"]:
            b = s.data()[va - s["sh_addr"]:]
            return b[:b.index(b"\0")].decode()
    return None


lines = run("objdump", "-d", "-M", "intel", "--no-show-raw-insn", path).splitlines()
calls = {}
for i, l in enumerate(lines):
    m = re.search(r"\t(?:call|jmp)\s+[0-9a-f]+ <(cob_check_version|cob_set_programid)@plt>", l)
    if not m:
        continue
    reg = {}
    for p in lines[max(0, i - 8):i]:
        mm = re.search(r"\t(lea|mov)\s+(\w+),(.*)$", p)
        if not mm:
            continue
        op, dst, src = mm.groups()
        dst = dst[-2:]
        if op == "lea" and "# " in src:
            reg[dst] = int(src.split("# ")[1].split()[0], 16)
        elif op == "mov" and src.startswith("0x"):
            reg[dst] = int(src, 16)
        elif op == "mov" and re.fullmatch(r"\w+", src):
            reg[dst] = reg.get(src[-2:])
    calls.setdefault(m.group(1), (cstr(reg["di"]) if reg.get("di") else None, cstr(reg["si"]) if reg.get("si") else None))
cv, sp = calls.get("cob_check_version"), calls.get("cob_set_programid")
print(json.dumps({"has_cobol_runtime": "true" if rt else "false", "needed": needed, "imports": imports if rt else [],
                  "cobol_runtime_version": cv[1] if cv else "none", "source_file": cv[0] if cv else "none",
                  "program_id_set_programid": sp[1] if sp else "none"}, indent=1))
