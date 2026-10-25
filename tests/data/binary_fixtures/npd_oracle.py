"""npd_oracle.py A B [A_syms B_syms]: independent per-function patch diff via binutils objdump -d (AT&T syntax) + nm.
Functions = nm text symbols (from the *_syms copies for stripped twins); text masked: absolute addresses / rip
displacements dropped, `<sym>` kept; changed = masked text differs. Prints JSON facts."""
import json, re, subprocess, sys
from collections import Counter

def funcs(path, symsrc):
    out = subprocess.run(["objdump", "-d", "--no-show-raw-insn", "-M", "suffix", symsrc], capture_output=True, text=True).stdout
    fs, cur = {}, None
    for ln in out.splitlines():
        m = re.match(r"^([0-9a-f]+) <([^>]+)>:$", ln)
        if m:
            cur = m.group(2); fs[cur] = {"addr": int(m.group(1), 16), "ins": []}; continue
        m = re.match(r"^\s+[0-9a-f]+:\s+(.*)$", ln)
        if m and cur and m.group(1).strip():
            t = m.group(1).strip()
            t = re.sub(r"\s+#.*?<([^>+]+)(\+0x[0-9a-f]+)?>", r" #<\1>", t)
            t = re.sub(r"\b[0-9a-f]+ <", "<", t)
            t = re.sub(r"-?0x[0-9a-f]+\(%rip\)", "X(%rip)", t)
            fs[cur]["ins"].append(re.sub(r"\s+", " ", t))
    return fs

a, b = sys.argv[1], sys.argv[2]
sa, sb = (sys.argv[3], sys.argv[4]) if len(sys.argv) > 4 else (a, b)
FA, FB = funcs(a, sa), funcs(b, sb)
skip = re.compile(r"@plt$|^_init$|^_fini$|^_start$|^deregister_tm_clones$|^register_tm_clones$|^__do_global_dtors_aux$|^frame_dummy$|^\.")
names = sorted((n for n in FA if n in FB and not skip.search(n)), key=lambda n: FA[n]["addr"])
changed = [n for n in names if FA[n]["ins"] != FB[n]["ins"]]
res = {"changed_functions": changed, "addr_a": {n: hex(FA[n]["addr"]) for n in changed}, "addr_b": {n: hex(FB[n]["addr"]) for n in changed}}
for n in changed:
    ia, ib = FA[n]["ins"], FB[n]["ins"]
    plt = lambda xs: [m for x in xs for m in re.findall(r"call\w* <([^@>]+)@plt>", x)]
    res[n] = {"calls_a": plt(ia), "calls_b": plt(ib),
              "frame_a": [x for x in ia if re.match(r"sub\w* \$0x[0-9a-f]+,%rsp", x)],
              "frame_b": [x for x in ib if re.match(r"sub\w* \$0x[0-9a-f]+,%rsp", x)],
              "jcc_a": dict(Counter(x.split()[0] for x in ia if re.match(r"j(?!mp)\w+ ", x))),
              "jcc_b": dict(Counter(x.split()[0] for x in ib if re.match(r"j(?!mp)\w+ ", x))),
              "n_a": len(ia), "n_b": len(ib)}
print(json.dumps(res, indent=1))
