"""Oracle for the adis_* fixtures, independent of lib.binary: gdb single-steps every protected function of the linked
adis_exe_all.bin (compiled here by adis_gen.sh from our own asm) and records the instructions the CPU really executes
(address order, gdb Intel syntax normalised to "mnemonic op, op") and the returned eax; `nm` rebases branch targets to
each .o's section offsets. Construction facts (techniques, junk byte counts) come from the asm source in adis_gen.sh.
usage (this dir): python3 adis_oracle.py  -> prints {fixture: {fn: {"disassembly": [...], "eax": n}}}"""
import json, re, subprocess, sys, tempfile, os
FNS = ["check_key", "skip_junk", "get_flag", "decode_it"]
G = r'''
import gdb, json
gdb.execute("set disassembly-flavor intel"); gdb.execute("set pagination off")
out = {}
for f in %r:
    gdb.execute("break " + f)
gdb.execute("run > /dev/null")
for _ in range(%d):
    fr = gdb.selected_frame(); fn = fr.name(); arch = fr.architecture()
    sp0 = int(gdb.parse_and_eval("$rsp")); tr = {}
    while True:
        pc = int(gdb.parse_and_eval("$pc"))
        if int(gdb.parse_and_eval("$rsp")) > sp0: break
        tr[pc] = arch.disassemble(pc)[0]["asm"]
        gdb.execute("stepi", to_string=True)
    out[fn] = {"trace": sorted(tr.items()), "eax": int(gdb.parse_and_eval("$eax")) & 0xffffffff}
    gdb.execute("continue", to_string=True)
print("ORACLE" + json.dumps(out))
'''
def norm(s, delta):
    s = re.sub(r"\s*<[^>]*>", "", s).strip()
    mn, _, ops = s.partition(" ")
    ops = re.sub(r"\s*,\s*", ", ", ops.strip()).replace("DWORD PTR", "dword ptr").replace("QWORD PTR", "qword ptr")
    if mn.startswith(("j", "call")) and re.fullmatch(r"0x[0-9a-f]+", ops):
        ops = hex(int(ops, 16) - delta)
    return (mn + " " + ops).strip()
def syms(p):
    return {l.split()[2]: int(l.split()[0], 16) for l in subprocess.run(["nm", p], capture_output=True, text=True)
            .stdout.splitlines() if len(l.split()) == 3}
with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as t:
    t.write(G % (FNS, len(FNS)))
r = subprocess.run(["gdb", "-batch", "-nx", "-x", t.name, "./adis_exe_all.bin"], capture_output=True, text=True)
os.unlink(t.name)
raw = json.loads(r.stdout.split("ORACLE", 1)[1].splitlines()[0])
ex = syms("adis_exe_all.bin")
res = {}
for fx in ("adis_exe_all", "adis_obj_jzjnz", "adis_obj_ebff", "adis_obj_callpop"):
    ob = syms(fx + ".bin")
    for fn in FNS:
        if fn in ob:
            d = ex[fn] - ob[fn] if fx != "adis_exe_all" else 0
            res.setdefault(fx, {})[fn] = {"disassembly": [norm(a, d) for _, a in raw[fn]["trace"]],
                                          "eax": raw[fn]["eax"]}
print(json.dumps(res, indent=1))
