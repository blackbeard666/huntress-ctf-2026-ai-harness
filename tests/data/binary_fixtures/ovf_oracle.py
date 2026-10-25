"""Independent oracle for the ovf_* fixtures (no lib.binary): objdump -d -Mintel text for the sink call / frame /
buffer lea / canary, readelf -lW -dW -sW for checksec facts, and gdb runs of the REAL binary (ASLR off) fed a de Bruijn
pattern (own recursive generator) to find the shortest input that changes the saved return address / reaches the
__stack_chk_fail call, and the cyclic offset seen in the saved RIP.
usage: python3 ovf_oracle.py FILE.bin [--argv]   -> JSON facts on stdout"""
import json, os, re, subprocess, sys, tempfile

SINKS = r"gets|strcpy|stpcpy|strcat|sprintf|fgets|read|recv|memcpy|strncpy|__isoc\d\d_scanf|scanf|sscanf|fread"


def sh(*a, inp=None):
    return subprocess.run(a, capture_output=True, text=True, errors="replace", input=inp, timeout=60).stdout


def debruijn(k, n, alpha="abcdefghijklmnopqrstuvwxyz"):
    a, seq = [0] * k * n, []

    def db(t, p):
        if t > n:
            if n % p == 0:
                seq.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)
    db(1, 1)
    return "".join(alpha[i] for i in seq)


f, use_argv = sys.argv[1], "--argv" in sys.argv
dis = sh("objdump", "-d", "-Mintel", "--no-show-raw-insn", f)
funcs = re.findall(r"\n([0-9a-f]+) <(\w+)>:\n(.*?)(?=\n\n|\Z)", dis, re.S)
out = {}
for addr, name, body in funcs:
    lines = [ln.split("\t") for ln in body.splitlines() if "\t" in ln]
    ins = [(int(l[0].strip().rstrip(":"), 16), l[1].strip() if len(l) > 1 else "") for l in lines]
    for k, (a, t) in enumerate(ins):
        m = re.match(rf"call\s+[0-9a-f]+ <({SINKS})@plt>", t)
        if not m or name in ("main",) and not use_argv and False:
            continue
        sink = re.sub(r"__isoc\d\d_", "", m.group(1))
        prev = [x for _, x in ins[max(0, k - 8):k]]
        buf = next((x for x in reversed(prev) if re.match(r"lea\s+r\w+,\[rbp-0x", x) or re.match(r"mov\s+r(si|di),rsp", x)), None)
        if not buf:
            continue
        frame = next((int(x.split(",")[1], 16) for _, x in ins[:10] if re.match(r"sub\s+rsp,0x", x)), None)
        if frame is None:
            frame = next(((1 << 64) - int(x.split(",")[1], 16) for _, x in ins[:10] if re.match(r"add\s+rsp,0xf", x)), None)
        pushes = sum(1 for _, x in ins[:6] if x.startswith("push"))
        rbp = any(x == "mov    rbp,rsp" for _, x in ins[:6])
        off = int(buf.split("-")[1].rstrip("]"), 16) if "rbp-" in buf else 0
        dist = off + 8 if rbp else 8 * pushes + frame - off
        can = next((int(x.split("-")[1].split("]")[0], 16) for _, x in ins if re.match(r"mov\s+QWORD PTR \[rbp-0x\w+\],rax", x)
                    and any("fs:0x28" in y for _, y in ins)), None) if "__stack_chk_fail" in body else None
        ln = None
        lreg = {"read": "edx", "fgets": "esi", "memcpy": "edx", "strncpy": "edx", "recv": "edx"}.get(sink)
        if lreg:
            ln = next((int(x.split(",")[1], 16) for x in reversed(prev) if re.match(rf"mov\s+{lreg},0x", x)), None)
        chk = next((a for a, x in ins if "<__stack_chk_fail@plt>" in x), None)
        rets = [a for a, x in ins if x == "ret"]
        out = {"vulnerable_function": name, "unsafe_call": sink, "frame_size": frame, "buffer_offset": off,
               "distance_to_return": dist, "read_length": ln, "canary": can is not None,
               "distance_to_canary": off - can if can else None, "_fa": int(addr, 16), "_ret": rets[-1], "_chk": chk}
        break
    if out:
        break
lw, dw, sw = sh("readelf", "-lW", f), sh("readelf", "-dW", f), sh("readelf", "-sW", "--dyn-syms", f)
gs = re.search(r"GNU_STACK.*?\s(RWE|RW)\s", lw)
out["nx"] = bool(gs) and gs.group(1) == "RW"
out["pie"] = "DYN (Position-Independent" in sh("readelf", "-hW", f)
now = "BIND_NOW" in dw or re.search(r"FLAGS_1.*\bNOW\b", dw) is not None
out["relro"] = ("full" if now else "partial") if "GNU_RELRO" in lw else "none"
out["binary_canary"] = "__stack_chk_fail" in sw

# gdb: break at the function's last ret and at its __stack_chk_fail call (function-relative), read the saved RIP slot
fn, rel_ret = out["vulnerable_function"], out["_ret"] - out["_fa"]
pat = debruijn(26, 4)
tmp = tempfile.mkdtemp()


def run(L):
    p = os.path.join(tmp, "in")
    open(p, "w").write(pat[:L])
    cmds = ["set disable-randomization on", "set pagination off", f"break *{fn}+{rel_ret}"]
    if out["_chk"]:
        cmds.append(f"break *{fn}+{out['_chk'] - out['_fa']}")
    cmds += [f"run '{pat[:L]}'" if use_argv else f"run < {p}", "printf \"PC=%lx\\n\", $pc",
             "printf \"RET=%lx\\n\", *(long*)($pc == " + f"{fn}+{rel_ret}" + " ? $rsp : $rbp+8)"]
    o = sh("gdb", "-q", "-batch", "-nx", *sum((["-ex", c] for c in cmds), []), f)
    pc = re.search(r"PC=([0-9a-f]+)", o)
    rv = re.search(r"RET=([0-9a-f]+)", o)
    return (int(pc.group(1), 16) if pc else None), (int(rv.group(1), 16) if rv else None)


pc0, base_ret = run(0)
ret_pc = pc0


def first(pred, hi=512):
    if not pred(*run(hi)):
        return None
    lo = 0
    while lo < hi:
        mid = (lo + hi) // 2
        if pred(*run(mid)):
            hi = mid
        else:
            lo = mid + 1
    return lo


out["ret_overwrite_length"] = first(lambda pc, r: r is not None and r != base_ret)
out["canary_trip_length"] = first(lambda pc, r: pc is not None and pc != ret_pc) if out["_chk"] else None
pc, r = run(512)
out["cyclic_offset"] = pat.find(r.to_bytes(8, "little")[:4].decode("latin-1")) if r and r != base_ret else None
out["crash_length"] = out["canary_trip_length"] if out["canary"] and out["canary_trip_length"] is not None \
    else out["ret_overwrite_length"]
out["vulnerable"] = out["ret_overwrite_length"] is not None or out["canary_trip_length"] is not None
print(json.dumps({k: v for k, v in out.items() if not k.startswith("_")}))
