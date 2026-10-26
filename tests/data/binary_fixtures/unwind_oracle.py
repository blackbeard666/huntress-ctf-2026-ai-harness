"""Independent oracle for the unwind_* fixtures: gdb's own unwinder (bt over the core + `info frame` CFA,
`info symbol`, `info proc mappings`) and readelf --debug-dump=frames-interp / -sW for per-function CFA sizes.
usage: python3 unwind_oracle.py unwind_o0_exe.bin unwind_o0_core.bin   -> expected_facts JSON on stdout"""
import json, re, subprocess, sys
exe, core = sys.argv[1:3]
GDB = r'''
import gdb, re
gdb.execute("set pagination off")
f = gdb.newest_frame(); i = 0
while f is not None:
    f.select()
    pc = int(f.pc()); sp = int(f.read_register("sp"))
    cfa = int(re.search(r"frame at (0x[0-9a-f]+)", gdb.execute("info frame", to_string=True)).group(1), 16)
    sym = gdb.execute("info symbol %d" % pc, to_string=True).strip()
    print("FRAME %d %#x %#x %#x %s" % (i, pc, sp, cfa, sym))
    f = f.older(); i += 1
print(gdb.execute("info proc mappings", to_string=True))
'''
open("/tmp/_uw_gdb.py", "w").write(GDB)
o = subprocess.run(["gdb", "-nx", "-batch", "-ex", "set debuginfod enabled off", "-x", "/tmp/_uw_gdb.py", exe, core],
                   capture_output=True, text=True).stdout
frames = [l.split(None, 5) for l in o.splitlines() if l.startswith("FRAME ")]
maps = [l.split() for l in o.splitlines() if re.match(r"\s*0x[0-9a-f]+\s+0x", l)]
def module(pc):
    for m in maps:
        s, e, off = int(m[0], 16), int(m[1], 16), int(m[3], 16)
        if s <= pc < e and len(m) > 4:
            return m[4].rsplit("/", 1)[-1], hex(pc - s + off)
    return "none", "none"
syms, offs, mods, mofs, rets, sizes = [], [], [], [], [], []
for _, i, pc, sp, cfa, s in frames:
    m = re.match(r"(\S+)(?: \+ (\d+))? in section", s)
    syms.append(m.group(1)); offs.append(hex(int(m.group(2) or 0)))
    md, mo = module(int(pc, 16)); mods.append(md); mofs.append(mo)
    rets.append(pc); sizes.append(str(int(cfa, 16) - int(sp, 16)))
# per-function CFA size from the CFI table: largest CFA offset of the FDE (readelf frames-interp)
fs = {}
st = subprocess.run(["readelf", "-sW", exe], capture_output=True, text=True).stdout
fn = {int(l.split()[1], 16): l.split()[7] for l in st.splitlines() if len(l.split()) >= 8 and l.split()[3] == "FUNC" and int(l.split()[1], 16)}
fr = subprocess.run(["readelf", "--debug-dump=frames-interp", exe], capture_output=True, text=True).stdout
for blk in fr.split("\n\n"):
    m = re.search(r"FDE cie=\S+ pc=([0-9a-f]+)\.\.", blk)
    if m and int(m.group(1), 16) in fn:
        vals = [int(x) for x in re.findall(r"^[0-9a-f]+\s+[a-z0-9]+\+(\d+)", blk, re.M)]
        if vals:
            fs[fn[int(m.group(1), 16)]] = str(max(vals))
facts = {"unwind_frame_count": str(len(frames)), "unwind_functions": json.dumps(syms, separators=(",", ":")),
         "unwind_frames": json.dumps([f"{a}+{b}" for a, b in zip(syms, offs)], separators=(",", ":")),
         "unwind_return_addresses": json.dumps(rets, separators=(",", ":")), "unwind_frame_sizes": json.dumps(sizes, separators=(",", ":")),
         "unwind_frame_modules": json.dumps(mods, separators=(",", ":")), "unwind_module_offsets": json.dumps(mofs, separators=(",", ":"))}
for k, (s, off, md, mo, r, z) in enumerate(zip(syms, offs, mods, mofs, rets, sizes)):
    facts.update({f"unwind_frame_{k}_function": s, f"unwind_frame_{k}_offset": off, f"unwind_frame_{k}_module": md,
                  f"unwind_frame_{k}_pc": r, f"unwind_frame_{k}_size": z})
for s in syms:
    if s in fs:
        facts[f"cfa_frame_size:{s}"] = fs[s]
print(json.dumps(facts, indent=1))
