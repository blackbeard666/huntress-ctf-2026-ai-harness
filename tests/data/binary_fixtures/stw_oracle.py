"""stw_oracle.py A B SYM: independent oracle for stripped twin fixtures -- binutils only (objdump -d on the SYMBOLIZED
build for per-symbol bodies, readelf -lW for VA->offset, readelf --debug-dump=frames on the STRIPPED twin for the FDE).
SYM must be a symbolized build of A or B with identical text (strip -s keeps addresses). Prints expected facts JSON."""
import json, re, subprocess, sys
a, b, sym = sys.argv[1:4]
run = lambda *c: subprocess.run(c, capture_output=True, text=True, check=True).stdout


def bodies(p, names=None):
    out, cur = {}, None
    for ln in run("objdump", "-d", "--no-show-raw-insn", "-M", "intel", "-j", ".text", p).splitlines():
        m = re.match(r"^([0-9a-f]+) <(.*)>:$", ln)
        if m:
            cur = int(m.group(1), 16)
            out[cur] = []
        elif cur is not None and "\t" in ln:
            ins = ln.split("\t", 1)[1].split("#")[0].strip()
            if ins.startswith(("nop", "int3", "xchg   ax,ax", "cs nop", "data16")):
                continue
            ins = re.sub(r"\b[0-9a-f]+ <([^>+]*)(\+0x[0-9a-f]+)?>", lambda x: "<" + x.group(1) + ("+L" if x.group(2) else "") + ">", ins)
            out[cur].append(re.sub(r"\[rip\+0x[0-9a-f]+\]", "[rip+X]", ins))
    return out


def syms(p):
    return {int(x.split()[1], 16): x.split()[7] for x in run("readelf", "-sW", p).splitlines()
            if len(x.split()) >= 8 and x.split()[3] == "FUNC" and x.split()[6] != "UND" and int(x.split()[2]) > 0}


def fdes(p):
    return {int(m.group(1), 16): int(m.group(2), 16) - int(m.group(1), 16)
            for m in re.finditer(r"FDE cie=\w+ pc=([0-9a-f]+)\.\.([0-9a-f]+)", run("readelf", "--debug-dump=frames", p))}


def off(p, va):
    for ln in run("readelf", "-lW", p).splitlines():
        x = ln.split()
        if x and x[0] == "LOAD":
            o, v, fs = int(x[1], 16), int(x[2], 16), int(x[4], 16)
            if v <= va < v + fs:
                return va - v + o


# symbol bodies of A and B through the symbolized twin: objdump the stripped twin with sym's names by address
names = syms(sym)
# stripped twins have no per-function labels: split objdump output at the .eh_frame FDE starts
def split(p):
    d = run("objdump", "-d", "--no-show-raw-insn", "-M", "intel", "-j", ".text", p)
    ins = [(int(m.group(1), 16), m.group(2).split("#")[0].strip()) for m in re.finditer(r"^\s+([0-9a-f]+):\t(.*)$", d, re.M)]
    starts = sorted(s for s in fdes(p) if any(s == x for x, _ in ins))
    out = {}
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else 1 << 64
        body = [re.sub(r"\b[0-9a-f]+ <[^>]*>", "T", re.sub(r"\[rip\+0x[0-9a-f]+\]|0x4[0-9a-f]{5}\b", "C", t)) for x, t in ins if s <= x < e
                and not t.startswith(("nop", "int3", "cs nop", "data16", "xchg   ax,ax"))]
        out[s] = body
    return out
fa, fb = split(a), split(b)
# pair by order (the oracle's twins keep function order; checked by the symbol name list being equal in count)
assert len(fa) == len(fb)
changed = [(x, y) for x, y in zip(sorted(fa), sorted(fb)) if fa[x] != fb[y]]
fdA, fdB = fdes(a), fdes(b)
symtext_is_a = run("objdump", "-d", "-j", ".text", sym).split("\n", 3)[3] == run("objdump", "-d", "-j", ".text", a).split("\n", 3)[3]
res = {"changed_function_count": str(len(changed))}
if changed:
    x, y = max(changed, key=lambda c: abs(len(fa[c[0]]) - len(fb[c[1]])))
    nm = names.get(x if symtext_is_a else y, "none")
    res.update({"changed_function": nm, "changed_function_name": nm, "changed_function_va": hex(x),
                "changed_function_va_b": hex(y), "changed_function_offset": hex(off(a, x)),
                "changed_function_offset_b": hex(off(b, y)),
                "eh_frame_range": f"{hex(x)}-{hex(x + fdA[x])}", "eh_frame_range_b": f"{hex(y)}-{hex(y + fdB[y])}",
                "eh_frame_size": str(fdA[x]), "eh_frame_size_b": str(fdB[y])})
else:
    res.update({"changed_function": "none", "patched_function": "none"})
print(json.dumps(res, indent=1))
