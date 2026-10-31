"""gf-func-body fixtures: expected values from binutils objdump -M intel / readelf -sW (never lib.binary)."""
import json, re, subprocess, sys, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
GEN = {"fb_d01.elf": "gcc -O2 -fcf-protection=none -fno-asynchronous-unwind-tables -o fb_d01.elf fb_src/fb.c",
       "fb_d01_stripped.elf": "strip -s -o fb_d01_stripped.elf fb_d01.elf",
       "fb_d01_O0.elf": "gcc -O0 -fcf-protection=full -fno-asynchronous-unwind-tables -o fb_d01_O0.elf fb_src/fb.c",
       "fb_d01_m32.o": "gcc -m32 -O2 -fcf-protection=none -fno-asynchronous-unwind-tables -c -o fb_d01_m32.o fb_src/fb.c",
       "gf_decoy_random.bin": "head -c 4096 /dev/urandom > gf_decoy_random.bin"}
DIS_Q = ("In the bundled Day 1 ELF, find the {s} FUNC symbol in the symbol table and disassemble its bytes. Submit its "
         "decoded instructions in execution order as a JSON array of strings, without addresses or byte columns. If "
         "that symbol is absent, submit []. Unrelated format example: [\"nop\",\"ret\"]. A stripped ELF (one without a "
         ".symtab section) has no {s} symbol, even if the function's code is still present and can be found by "
         "disassembly; it still takes [].")
DIS_AF = {"kind": "json", "syntax": "JSON array of instruction strings in execution order; an empty array if the "
          "recover_code symbol is absent. Intel or AT&T spelling of the same constant-return instructions is accepted."}
RC_Q = ("In evidence.zip, Use all d01-- members in ZIP central-directory order. Look for a FUNC symbol named {s} in "
        "the Day 1 ELF's .symtab symbol table. If there is no such symbol, submit the literal token none. A stripped "
        "ELF (one without a .symtab section) has no {s} symbol, even if the function's code is still present and can "
        "be found by disassembly; it still takes none, not the disassembled immediate. Otherwise decode that symbol's "
        "exact bytes as mov eax, imm32 followed by ret and submit the immediate as an unsigned base-10 integer.")
RC_AF = {"kind": "pattern", "syntax": "unsigned base-10 integer, or the literal token none when the recover_code FUNC "
         "symbol is absent"}
SZ_Q = "Look up the {s} FUNC symbol in the ELF's .symtab and submit its st_size in bytes; none if the symbol is absent."
AD_Q = ("Look up the {s} FUNC symbol in the ELF's .symtab and submit its st_value virtual address; none if the symbol "
        "is absent.")
INT_AF = {"kind": "pattern", "syntax": "base-10 integer, or the literal token none"}
HEX_AF = {"kind": "pattern", "syntax": "lowercase hexadecimal with 0x prefix, or the literal token none"}

OBJ = "objdump -d -M intel --no-show-raw-insn --disassemble={s} {m}"
NORM = (" | python3 -c 'import sys,re,json; print(json.dumps([re.sub(r\"0x[0-9a-f]+\",lambda h:str(int(h.group(0),16)),"
        "re.sub(r\",\",\", \",\" \".join(l.split(\"\\t\")[-1].split()))) for l in sys.stdin if re.match(r\"\\s+[0-9a-f]+:\\t\",l)]"
        ",separators=(\",\",\":\")))'")
RD = "readelf -sW {m} | awk '$4==\"FUNC\" && $8==\"{s}\" {{print ${c}}}' | head -1"


def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True, check=True).stdout.strip()


def emit(member, field, q, af, cmd, conv, decoy=False):
    out = sh(cmd) if cmd else ""
    exp = conv(out)
    d = {"kind": "generic_field", "member": member, "field": field, "question": q, "answer_format": af,
         "expected": exp, "generator_cmd": GEN[member] + "  # fb_src/fb_gen.sh", "oracle_cmd": cmd or "file " + member,
         "oracle_output": out}
    if decoy:
        d["decoy"] = True
    json.dump(d, open(f"{member}.{field}.json", "w"), indent=1)
    print(member, field, repr(exp))


def dis(o):   # objdump lines -> JSON array; empty output (no such symbol in .symtab) -> []
    return json.dumps(json.loads(o), separators=(",", ":")) if o else "[]"


def imm(o):   # the mov eax, imm of a (frame) mov+ret body
    a = json.loads(o) if o else []
    core = [x for x in a if x not in ("endbr64", "push rbp", "mov rbp, rsp", "pop rbp")]
    return core[0].split(", ")[1] if core and len(core) == 2 and core[0].startswith("mov eax, ") else "none"


for m in ("fb_d01.elf", "fb_d01_O0.elf", "fb_d01_m32.o", "fb_d01_stripped.elf"):
    emit(m, "disassembly", DIS_Q.format(s="recover_code"), DIS_AF, OBJ.format(s="recover_code", m=m) + NORM, dis,
         decoy=m.endswith("stripped.elf"))
    emit(m, "recover_code", RC_Q.format(s="recover_code"), RC_AF, OBJ.format(s="recover_code", m=m) + NORM, imm,
         decoy=m.endswith("stripped.elf"))
emit("fb_d01.elf", "seed_big_disassembly", DIS_Q.format(s="seed_big"), DIS_AF, OBJ.format(s="seed_big", m="fb_d01.elf")
     + NORM, dis)
emit("fb_d01_m32.o", "seed_big_disassembly", DIS_Q.format(s="seed_big"), DIS_AF,
     OBJ.format(s="seed_big", m="fb_d01_m32.o") + NORM, dis)
emit("fb_d01.elf", "missing_fn_disassembly", DIS_Q.format(s="missing_fn"), DIS_AF,
     OBJ.format(s="missing_fn", m="fb_d01.elf") + " 2>/dev/null" + NORM, dis, decoy=True)
emit("fb_d01.elf", "mix_size", SZ_Q.format(s="mix"), INT_AF, RD.format(m="fb_d01.elf", s="mix", c=3), lambda o: o or "none")
emit("fb_d01_O0.elf", "recover_code_size", SZ_Q.format(s="recover_code"), INT_AF,
     RD.format(m="fb_d01_O0.elf", s="recover_code", c=3), lambda o: o or "none")
emit("fb_d01.elf", "mix_address", AD_Q.format(s="mix"), HEX_AF, RD.format(m="fb_d01.elf", s="mix", c=2),
     lambda o: hex(int(o, 16)) if o else "none")
emit("fb_d01_stripped.elf", "mix_address", AD_Q.format(s="mix"), HEX_AF, RD.format(m="fb_d01_stripped.elf", s="mix", c=2),
     lambda o: hex(int(o, 16)) if o else "none", decoy=True)
emit("gf_decoy_random.bin", "recover_code", RC_Q.format(s="recover_code"), RC_AF, "", lambda o: None, decoy=True)
emit("fb_d01.elf", "mix_disassembly", DIS_Q.format(s="mix"), DIS_AF, OBJ.format(s="mix", m="fb_d01.elf") + NORM,
     lambda o: None)   # lea [..]: left to the worker
