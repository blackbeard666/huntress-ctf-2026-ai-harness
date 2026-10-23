"""Independent oracle for ehctl_* fixtures (does NOT use lib.binary).
C++: landing pads = gcc's own `-S` call-site table labels (.uleb128 .Lx-.LFBy) resolved by `nm` on the -Wa,-L twin
(identical .text), function = enclosing `nm` symbol, catch types = ttype `DW.ref._ZTI*` entries via `c++filt`.
Signals: `gdb -batch` breakpoints on signal/sigaction -> $rdi and `info symbol` of the handler pointer.
Traps: `objdump -d` int3/ud2 lines. usage: python3 ehctl_oracle.py <tmpdir printed by ehctl_gen.sh>"""
import re, subprocess, sys, json
T = sys.argv[1]
sh = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True).stdout

def cxx(stem):
    syms = {}
    for ln in sh(f"nm -n {T}/{stem}.lbl").splitlines():
        a, _, n = ln.split()[-3:] if len(ln.split()) == 3 else (None, None, None)
        if a:
            syms[n] = int(a, 16)
    funcs = sorted((v, n) for n, v in syms.items() if not n.startswith(".L") and v)
    owner = lambda va: max((v, n) for v, n in funcs if v <= va)[1]
    s = open(f"{T}/{stem}.s").read()
    lps, catch, clean, efn, cfn, types = [], [], [], [], [], []
    pers = re.findall(r"\.cfi_personality 0x[0-9a-f]+,(?:DW\.ref\.)?(\S+)", s)
    for blk in re.findall(r"\.LLSDACSB\w+:\n(.*?)\.LLSDACSE\w+:\n(.*?)(?=^\t\.text|\Z)", s, re.S | re.M):
        ul = re.findall(r"\.uleb128 (\S+)", blk[0])
        for i in range(0, len(ul), 4):
            lp, act = ul[i + 2], ul[i + 3]
            if lp == "0":
                continue
            va = syms[lp.split("-")[0]]
            lps.append(va); efn.append(owner(va))
            (clean if act == "0" else catch).append(va)
            if act != "0":
                cfn.append(owner(va))
        for t in re.findall(r"\.long\s+(?:DW\.ref\.)?(_ZTI\w+|0)", blk[1]):
            types.append("..." if t == "0" else sh(f"echo {t} | c++filt").strip().replace("typeinfo for ", ""))
    u = lambda xs: list(dict.fromkeys(xs)) or "none"
    h = lambda xs: [hex(x) for x in sorted(set(xs))] or "none"
    return {"personality": pers[0] if pers else "none", "landing_pads": h(lps), "landing_pad_count": str(len(set(lps))),
            "catch_landing_pads": h(catch), "cleanup_landing_pads": h(clean), "eh_functions": u(efn),
            "catch_functions": u(cfn), "catch_types": u(types)}

def sig(path):
    out = sh(f"gdb -batch -nx -ex 'set startup-with-shell off' -ex 'set breakpoint pending on' -ex 'handle SIGILL nostop noprint pass' "
             f"-ex 'break sigaction' -ex 'break signal' -ex run "
             f"-ex 'printf \"S %d \", $rdi' -ex 'info symbol *(void**)$rsi' -ex c "
             f"-ex 'printf \"S %d \", $rdi' -ex 'info symbol *(void**)$rsi' -ex c "
             f"-ex 'printf \"S %d \", $rdi' -ex 'info symbol $rsi' -ex kill {path} 2>&1")
    pairs = re.findall(r"S (\d+) (\w+) in section", out)
    names = {"5": "SIGTRAP", "4": "SIGILL", "11": "SIGSEGV"}
    traps = re.findall(r"\t(int3|ud2)\s*$", sh(f"objdump -d --no-show-raw-insn -Mintel {path} | sed -n '/<main>:/,/^$/p'"), re.M)
    return {"signals": [names[n] for n, _ in pairs] or "none", "signal_numbers": [n for n, _ in pairs] or "none",
            "signal_handlers": [f"{names[n]}:{h}" for n, h in pairs] or "none",
            "signal_handler_functions": [h for _, h in pairs] or "none",
            "trap_instructions": list(dict.fromkeys(traps)) or "none", "trap_functions": ["main"] if traps else "none",
            "int3_anti_debug": "true" if "int3" in traps and any(n == "5" for n, _ in pairs) else "false",
            "has_exception_handlers": "true" if pairs else "false", "handler:SIGTRAP": dict((names[n], h) for n, h in pairs).get("SIGTRAP", "none")}

print(json.dumps({"ehctl_cxx_nopie": cxx("cxx_nopie"), "ehctl_cxx_pie_cold": cxx("cxx_pie_cold"),
                  "ehctl_sig_o0": sig("ehctl_sig_o0.bin"), "ehctl_sig_o2_noplt": sig("ehctl_sig_o2_noplt.bin")}, indent=1))
