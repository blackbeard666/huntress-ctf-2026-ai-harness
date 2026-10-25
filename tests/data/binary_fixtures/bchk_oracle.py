"""bchk_oracle.py A B: independent bounds-check twin facts via binutils `objdump -d -C -M intel` + `readelf -sW`.
Changed function = same name, masked text differs. Sinks = call targets (<sym@plt>, <sym>, or `# addr <sym>` for
GOT calls) matched by the family table below; guards = cmp followed by a conditional jump; indexed access = memory
operand [reg+reg*N] / [reg+reg] outside lea, unguarded when no guard precedes it. Prints JSON facts."""
import json, re, subprocess, sys

FAM = [("ubsan", "__ubsan_handle_out_of_bounds"), ("rust_panic_bounds_check", "panic_bounds_check"),
       ("rust_slice_index_fail", "slice_end_index_len_fail"), ("rust_slice_index_fail", "slice_index_len_fail"),
       ("go_panic_index", "runtime.panicIndex"), ("go_panic_slice", "runtime.panicSlice"),
       ("go_panic_bounds", "runtime.panicBounds"), ("fortify_chk", "_chk")]
JCC = {"ja", "jae", "jb", "jbe", "jg", "jge", "jl", "jle"}

def funcs(path):
    out = subprocess.run(["objdump", "-d", "-C", "-M", "intel", "--no-show-raw-insn", path], capture_output=True, text=True).stdout
    fs, cur = {}, None
    for ln in out.splitlines():
        m = re.match(r"^[0-9a-f]+ <(.+)>:$", ln)
        if m:
            cur = m.group(1); fs[cur] = []; continue
        m = re.match(r"^\s+[0-9a-f]+:\s+(\S+)\s*(.*)$", ln)
        if m and cur and m.group(1) not in ("nop", "int3", "endbr64", "cs", "xchg"):
            fs[cur].append((m.group(1), m.group(2).strip()))
    return fs

def objsizes(path):
    out = subprocess.run(["readelf", "-sW", path], capture_output=True, text=True).stdout
    return {c[7]: int(c[2], 0) for c in (l.split() for l in out.splitlines()) if len(c) >= 8 and c[3] == "OBJECT"}

def facts(ins, osz):
    sinks, guards, acc, objs = [], [], [], []
    for k, (mn, op) in enumerate(ins):
        if mn == "call":
            m = re.search(r"<([^>+]+?)(?:@plt)?>\s*$", op)
            if m:
                nm = m.group(1)
                fam = next((f for f, s in FAM if s in nm and not nm.startswith("__stack_chk")), None)
                if fam:
                    sinks.append((fam, nm.split("::h")[0]))
        if mn == "cmp" and k + 1 < len(ins) and ins[k + 1][0] in JCC:
            guards.append((op, ins[k + 1][0]))
        if mn != "lea" and re.search(r"\[[a-z][a-z0-9]*\+(?!0x)[a-z][a-z0-9]*(\*[1248])?\]", op) and "rip" not in op:
            acc.append(bool(guards))
        m = re.search(r"# [0-9a-f]+ <([A-Za-z_][\w.]*)>$", op)
        if m and m.group(1) in osz:
            objs.append(m.group(1))
    return sinks, guards, acc, objs

A, B = sys.argv[1], sys.argv[2]
FA, FB, OB = funcs(A), funcs(B), objsizes(B)
res = {}
for n in FA:
    if n not in FB or n.endswith("@plt") or n.startswith(("_init", "_fini", "_start", ".")):
        continue
    mask = lambda xs: [(m, re.sub(r"\b[0-9a-f]{3,}\b|0x[0-9a-f]+", "X", o)) for m, o in xs]
    if mask(FA[n]) == mask(FB[n]):
        continue
    sa, ga, aa, _ = facts(FA[n], objsizes(A))
    sb, gb, ab, ob = facts(FB[n], OB)
    r = {"bounds_check_function_demangled": n, "bounds_check_calls_a": str(len(sa)), "bounds_check_calls_b": str(len(sb)),
         "bounds_compares_a": str(len(ga)), "bounds_compares_b": str(len(gb)),
         "unchecked_accesses_a": str(aa.count(False)), "unchecked_accesses_b": str(ab.count(False)),
         "bounds_check_twin": "b" if len(sb) + len(gb) > len(sa) + len(ga) else "a" if len(sa) + len(ga) > len(sb) + len(gb) else "none",
         "bounds_check_kind": sb[0][0] if sb else "manual_compare" if gb else "none",
         "bounds_check_sink": sb[0][1] if sb else "none"}
    m = re.search(r",(0x[0-9a-f]+)$", gb[0][0]) if gb else None
    if m:
        lim = int(m.group(1), 16)
        r["bounds_limit"] = str(lim)
        r["buffer_length"] = str(lim + 1 if gb[0][1] in ("ja", "jbe", "jg", "jle") else lim)
    if ob:
        r["buffer_object"], r["buffer_object_size"] = ob[0], str(OB[ob[0]])
    res[n] = r
print(json.dumps(res, indent=1))
