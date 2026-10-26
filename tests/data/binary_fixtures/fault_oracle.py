"""Independent oracle for fault_*.json (no lib/ import): GNU objdump -M intel / aarch64 objdump for the instruction,
readelf -sW (FUNC symbols) or readelf --debug-dump=frames (FDE ranges, stripped) for the function, gdb on the core for
pc / signal / si_addr / return address. objdump text is normalised to the GM convention (lowercase, decimal numbers,
`, ` separators, spaced +/- inside [..]). usage: python3 fault_oracle.py [--write]"""
import json, pathlib, re, subprocess, sys
D = pathlib.Path(__file__).resolve().parent
run = lambda *a: subprocess.run(a, capture_output=True, text=True, cwd=D).stdout   # noqa: E731
SIZE = {"byte": 1, "word": 2, "dword": 4, "qword": 8, "xmmword": 16}


def objdump(exe, va, a64=False):
    out = run("aarch64-linux-gnu-objdump" if a64 else "objdump", "-d", *([] if a64 else ["-M", "intel"]),
              f"--start-address={va:#x}", f"--stop-address={va + 16:#x}", exe)
    ins = []
    for l in out.splitlines():
        m = re.match(r"\s*([0-9a-f]+):\t([0-9a-f ]+)\t(.*)", l)
        if m:
            ins.append((int(m.group(1), 16), len(m.group(2).split()) if not a64 else 4, m.group(3)))
    return ins


def gm(t, a64=False):
    t = re.sub(r"\s*[#;<].*$", "", t) if not a64 else re.sub(r"\s*(//|<).*$", "", t)
    t = " ".join(t.lower().split())
    mn, _, ops = t.partition(" ")
    if mn in ("call", "jmp", "bl", "b") and re.fullmatch(r"[0-9a-f]+", ops):
        ops = "0x" + ops
    ops = re.sub(r",(?=\S)", ", ", ops)
    ops = re.sub(r"\[([^\]]*)\]", lambda m: "[" + re.sub(r"\s*([+-])\s*", r" \1 ", m.group(1)) + "]", ops)
    ops = re.sub(r"0x[0-9a-f]+", lambda m: str(int(m.group(0), 16)), ops)
    return (mn + " " + ops).strip()


def func_of(exe, va):
    best = None
    for l in run("readelf", "-sW", exe).splitlines():
        t = l.split()
        if len(t) >= 8 and t[3] == "FUNC" and t[1] != "0000000000000000" and int(t[1], 16):
            a, n = int(t[1], 16), int(t[2], 0)
            if a <= va < a + max(n, 1) and (best is None or a > best[0]):
                best = (a, t[7].split("@")[0])
    if best:
        return best
    for l in run("readelf", "--debug-dump=frames", exe).splitlines():
        m = re.search(r"FDE cie=\w+ pc=([0-9a-f]+)\.\.([0-9a-f]+)", l)
        if m and int(m.group(1), 16) <= va < int(m.group(2), 16):
            return int(m.group(1), 16), f"sub_{int(m.group(1), 16):x}"
    return None


def facts(exe, va, a64=False, sig=None, si_addr=None, base_val=None):
    ins = objdump(exe, va, a64)
    if not ins or ins[0][0] != va:
        return None
    _, size, txt = ins[0]
    g = gm(txt, a64)
    mn = g.split(" ")[0]
    out = {"fault_va": hex(va), "fault_insn": g, "fault_mnemonic": mn, "fault_insn_size": str(size)}
    f = func_of(exe, va)
    if f:
        out.update(fault_function=f[1], fault_function_offset=hex(va - f[0]), fault_symbol=f"{f[1]}+{hex(va - f[0])}")
    m = re.search(r"\[([^\]]*)\]", g)
    rw = None
    if m and mn != "lea":
        parts = [p.strip() for p in re.split(r"[,+]| - ", m.group(1))]
        regs = [p for p in parts if re.fullmatch(r"[a-z][a-z0-9]*", p)]
        idx = next((p.split("*")[0] for p in parts if "*" in p), regs[1] if len(regs) > 1 else "none")
        num = re.search(r"(?:#|[+-] )(-?\d+)\b", m.group(1))
        disp = int(num.group(1)) * (-1 if " - " in m.group(1) else 1) if num else 0
        out.update(fault_mem_base=regs[0], fault_mem_index=idx, fault_mem_disp=str(disp))
        if a64:
            out["fault_access_size"] = "1" if mn.endswith("b") else "2" if mn.endswith("h") else \
                "4" if g.split(" ")[1].startswith("w") else "8"
            rw = "write" if mn.startswith("st") else "read"
        else:
            sz = re.search(r"(\w+) ptr", g)
            out["fault_access_size"] = str(SIZE[sz.group(1)]) if sz else "none"
            rw = "write" if g.split(" ", 1)[1].startswith(sz.group(0) if sz else "[") and mn.startswith("mov") \
                else "read"
        out["fault_access"] = rw
    tgt = re.search(r"<([^>@+]+)", txt)
    if mn in ("div", "idiv"):
        cls = "divide_error"
    elif mn == "ud2":
        cls = "ud2_trap"
    elif mn == "int3":
        cls = "int3_trap"
    elif mn == "call" and tgt and "stack_chk_fail" in tgt.group(1):
        cls = "stack_protector"
    elif rw:
        null = (si_addr is not None and si_addr < 0x1000) or base_val == 0
        cls = (("null_pointer_" if null else "bad_pointer_") if sig in (11, 7) or si_addr is not None
               else "memory_") + rw
    else:
        cls = None
    if cls:
        out["fault_class"] = cls
    return out


def gdb_core(exe, core):
    o = run("gdb", "-nx", "-batch", "-ex", "set disassembly-flavor intel", "-ex", "p/x $pc",
            "-ex", "p $_siginfo.si_signo", "-ex", "p/x $_siginfo._sifields._sigfault.si_addr", "-ex", "bt", exe, core)
    pc = int(re.search(r"\$1 = (0x[0-9a-f]+)", o).group(1), 16)
    sig = int(re.search(r"\$2 = (\d+)", o).group(1))
    sa = re.search(r"\$3 = (0x[0-9a-f]+)", o)
    frames = [(int(m.group(1), 16), m.group(2)) for m in re.finditer(r"#\d+\s+(0x[0-9a-f]+) in (\S+)", o)]
    return pc, sig, int(sa.group(1), 16) if sa and sig in (11, 7) else None, frames, o


def caller_site(exe, ret):
    """objdump: the call instruction ending exactly at return address `ret`."""
    for back in (2, 3, 5, 6, 7):
        ins = objdump(exe, ret - back)
        if ins and ins[0][0] == ret - back and ins[0][1] == back and ins[0][2].startswith("call"):
            return ret - back
    return None


CASES = {}
q = lambda n: (D / n).read_text().strip()   # noqa: E731
# 1) stripped text report
m = re.search(r"rip=(0x[0-9a-f]+) si_addr=(0x[0-9a-f]+)", q("fault_x64_strip_idx.question"))
CASES["fault_x64_strip_idx"] = dict(args={"question": q("fault_x64_strip_idx.question")},
                                    exp=facts("fault_x64_strip_idx.bin", int(m.group(1), 16), sig=11,
                                              si_addr=int(m.group(2), 16)))
# 2) badcall core: pc = 0 -> the caller's call site (gdb bt frame #1 return address)
pc, sig, sa, fr, _ = gdb_core("fault_x64_badcall.bin", "fault_x64_badcall.core")
site = caller_site("fault_x64_badcall.bin", next(a for a, n in fr if n == "main"))
e = facts("fault_x64_badcall.bin", site, sig=sig)
e["fault_class"] = "call_bad_pointer" if pc < 0x1000 else e.get("fault_class")
e["fault_signal"] = "SIGSEGV" if sig == 11 else str(sig)
CASES["fault_x64_badcall"] = dict(args={"core": "fault_x64_badcall.core"}, exp=e)
# 3) int3 by file offset
off = int(re.search(r"offset (0x[0-9a-f]+)", q("fault_x64_int3_off.question")).group(1), 16)
lo = next(l.split() for l in run("readelf", "-lW", "fault_x64_int3_off.bin").splitlines()
          if l.split()[:1] == ["LOAD"] and int(l.split()[1], 16) <= off < int(l.split()[1], 16) + int(l.split()[4], 16))
e = facts("fault_x64_int3_off.bin", off - int(lo[1], 16) + int(lo[2], 16))
e["fault_file_offset"] = hex(off)
CASES["fault_x64_int3_off"] = dict(args={"question": q("fault_x64_int3_off.question")}, exp=e)
# 4) aarch64 VA
CASES["fault_a64_ldrb"] = dict(args={"va": q("fault_a64_ldrb.va")},
                               exp=facts("fault_a64_ldrb.bin", int(q("fault_a64_ldrb.va"), 16), a64=True, base_val=0))
# 5) existing core_gen.sh cores (gdb pc relocated -> `info symbol`-free: exe VA = pc - (AT_ENTRY - e_entry))
for name, bt_fn in (("x64_nullw", None), ("x64_div0", None), ("x64_ud2", None), ("x64_smash", "smash")):
    exe, core = f"core_{name}_exe.elf", f"core_{name}.bin"
    pc, sig, sa, fr, o = gdb_core(exe, core)
    at_entry = int(re.search(r"AT_ENTRY\s.*?(0x[0-9a-f]+)", run("gdb", "-nx", "-batch", "-ex", "info auxv", exe,
                                                                  core)).group(1), 16)
    e_entry = int(re.search(r"Entry point address:\s+(0x[0-9a-f]+)", run("readelf", "-hW", exe)).group(1), 16)
    bias = at_entry - e_entry
    va = pc - bias if not bt_fn else caller_site(exe, next(a for a, n in fr if n == bt_fn) - bias)
    base = re.search(r"\[(\w+)", (objdump(exe, va) or [(0, 0, "")])[0][2])
    bv = None
    if base:
        r = re.search(r"= (0x[0-9a-f]+|\d+)", run("gdb", "-nx", "-batch", "-ex", f"p/x ${base.group(1)}", exe, core))
        bv = int(r.group(1), 0) if r else None
    e = facts(exe, va, sig=sig, si_addr=sa, base_val=bv)
    CASES[f"fault_core_{name}"] = dict(args={"core": core}, input=exe, exp=e)
# decoys
CASES["fault_decoy_text"] = dict(args={"question": "rip 0x401136"}, exp=None, decoy=True)
CASES["fault_decoy_unmapped"] = dict(args={"va": "0x13370000"}, exp=None, decoy=True)

if __name__ == "__main__":
    for n, c in CASES.items():
        print(n, json.dumps(c["exp"]))
        if "--write" in sys.argv:
            j = {"family": "fault_insn", "encoding": "none", "expected_offset": None, "expected_config": None,
                 "input": c.get("input", n + ".bin"), "args": c["args"], "expected_facts": c["exp"],
                 "generator_cmd": "bash fault_gen.sh   # gcc / aarch64-linux-gnu-gcc crashers, strip -s, gdb "
                                  "generate-core-file; fault_core_* reuse core_gen.sh cores",
                 "oracle_cmd": "python3 fault_oracle.py --write   # objdump -M intel / aarch64 objdump, readelf -sW / "
                               "--debug-dump=frames, gdb (pc, $_siginfo, bt, info auxv)",
                 "decoy": bool(c.get("decoy")),
                 "note": "lib.binary.fault_insn_field(input, key, **args) per expected_facts key; null expected = "
                         "None (cannot locate). Field names SPECULATIVE (GM label not seen)"}
            (D / f"{n}.json").write_text(json.dumps(j, indent=1) + "\n")
