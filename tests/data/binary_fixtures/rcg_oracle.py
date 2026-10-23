"""Independent oracle for rcg_*.bin (runtime code generation): GNU objdump -d/-s/-D -b binary, `file`, ilspycmd -il.
No lib.binary, no capstone, no dnfile. usage: python3 rcg_oracle.py <file.bin>  -> JSON expected_facts on stdout."""
import json, os, re, subprocess, sys, tempfile

p = sys.argv[1]
run = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout  # noqa: E731
KEYS = ("has_runtime_codegen", "codegen_kind", "emitted_opcodes", "emitted_instructions", "emitted_constant",
        "emitted_constant_hex", "emitted_bytes")


def out(kind, ops=(), ins=(), const=None, raw=b""):
    f = dict.fromkeys(KEYS, "none")
    f["has_runtime_codegen"] = "false" if kind == "none" else "true"
    f["codegen_kind"] = kind
    if ops:
        f["emitted_opcodes"], f["emitted_instructions"] = json.dumps(list(ops)), json.dumps(list(ins))
    if const is not None:
        f["emitted_constant"], f["emitted_constant_hex"] = str(const), hex(const)
    if raw:
        f["emitted_bytes"] = raw.hex()
    print(json.dumps(f, indent=1))
    sys.exit()


ft = run("file", "-b", p)
if ft.startswith("ELF"):
    dis = run("objdump", "-d", "-Mintel", "--no-show-raw-insn", p).splitlines()
    mem = {}
    for ln in run("objdump", "-s", p).splitlines():   # every section's bytes by address
        m = re.match(r"\s+([0-9a-f]+) ((?:[0-9a-f]{2,8} ){1,4})", ln + " ")
        if m:
            for k, x in enumerate(bytes.fromhex(m.group(2).replace(" ", ""))):
                mem[int(m.group(1), 16) + k] = x
    lines = [re.match(r"\s+([0-9a-f]+):\t(.*)", x) for x in dis]
    lines = [(int(m.group(1), 16), re.sub(r"\s+", " ", m.group(2)).strip()) for m in lines if m]
    exec_ok, buf, src = False, {}, {}
    for k, (a, t) in enumerate(lines):
        m = re.match(r"call [0-9a-f]+ <(mmap|mprotect)@plt>", t)
        if m:
            prev = [x for _, x in lines[max(0, k - 12):k] if re.match(r"mov edx,0x[0-9a-f]+$", x)]
            if prev and int(prev[-1].split(",")[1], 16) & 4:
                exec_ok = True
            if m.group(1) == "mmap":
                for b, u in lines[k + 1:k + 40]:   # loads from the image, stores through the mapping (gcc forms)
                    lm = re.match(r"mov(?:zx)? (\w+),(D?WORD|QWORD|BYTE) PTR \[rip\+0x[0-9a-f]+\] # ([0-9a-f]+)", u)
                    if lm:
                        src[lm.group(1)[-2:]] = (int(lm.group(3), 16), {"BYTE": 1, "WORD": 2, "DWORD": 4, "QWORD": 8}[lm.group(2)])
                    sm = re.match(r"mov (D?WORD|QWORD|BYTE) PTR \[r(?:ax|bx)(?:\+0x([0-9a-f]+))?\],(\w+)$", u)
                    if sm and sm.group(3)[-2:] in src:
                        va, w = src[sm.group(3)[-2:]]
                        for j in range(w):
                            buf[int(sm.group(2) or "0", 16) + j] = mem[va + j]
    if not exec_ok or 0 not in buf:
        out("none")
    raw = bytearray()
    while len(raw) in buf:
        raw.append(buf[len(raw)])
    jit = tempfile.mktemp(suffix=".jit")
    open(jit, "wb").write(raw)
    ops, ins, const, end = [], [], None, len(raw)
    for ln in run("objdump", "-D", "-b", "binary", "-mi386:x86-64", "-Mintel", "--no-show-raw-insn", jit).splitlines():
        m = re.match(r"\s+([0-9a-f]+):\t(\S+)\s*(.*)", ln)
        if not m:
            continue
        mn, op = m.group(2), m.group(3).strip().replace(",", ", ")
        ops.append(mn)
        ins.append(f"{mn} {op}".strip())
        c = re.search(r", (0x[0-9a-f]+)$", op)
        if const is None and c:
            const = int(c.group(1), 16)
        if mn == "ret":
            end = int(m.group(1), 16) + 1
            break
    os.remove(jit)
    out("native_jit", ops, ins, const, bytes(raw[:end]))
if "Mono/.Net assembly" in ft or "PE32" in ft:
    il = run("ilspycmd", "-il", p).splitlines()
    ops, ins, const, pend, kind = [], [], None, None, "none"
    for k, ln in enumerate(il):
        m = re.search(r"IL_[0-9a-f]+: (\S+)\s*(.*)", ln)
        if not m:
            continue
        op, arg = m.groups()
        if op == "ldsfld" and "System.Reflection.Emit.OpCodes::" in arg:
            pend = [arg.rsplit("::", 1)[1].lower().replace("_", "."), None]
        elif pend and op == "callvirt" and "ILGenerator::Emit(" in arg:
            ops.append(pend[0]); ins.append(pend[0] if pend[1] is None else f"{pend[0]} {pend[1]}")
            const = pend[1] if const is None else const
            pend, kind = None, "dotnet_emit"
        elif pend and op.startswith("ldc.i"):
            pend[1] = int(arg) if arg else int(op.split(".")[-1].replace("m1", "-1"))
        elif op == "call" and "Expression::Constant(" in arg and kind == "none":
            prv = [re.search(r"IL_[0-9a-f]+: (\S+)\s*(.*)", x).groups() for x in il[k - 2:k] if "IL_" in x]
            ld = [a for o, a in prv if o.startswith("ldc.i")]
            if ld and any("::Compile()" in x for x in il):
                const, kind = int(ld[-1]), "dotnet_expression"
    out(kind, ops, ins, const)
print(json.dumps(dict.fromkeys(KEYS, None)))
