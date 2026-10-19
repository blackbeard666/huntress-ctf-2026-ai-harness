"""Independent oracle for antiana_*.bin: GNU objdump -d -Mintel (+ -s rodata), readelf -sW, strings -a; no lib.binary,
no capstone. usage: python3 antiana_oracle.py <file.bin>  -> JSON expected_facts on stdout."""
import json, re, subprocess, sys

p = sys.argv[1]
run = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout  # noqa: E731
if "ELF" not in run("file", "-b", p):
    print(json.dumps({k: "none" for k in ("anti_debug", "anti_vm", "anti_debug_techniques", "anti_vm_techniques",
                                          "vm_strings", "dmi_paths", "env_gates", "env_gate_values", "decoy_functions",
                                          "mitre_technique", "uses:tracerpid")}))
    sys.exit()
if not run("readelf", "-SW", p).count("] .text"):
    print(json.dumps({k: None for k in ("anti_debug", "anti_vm", "env_gates", "decoy_functions", "uses:tracerpid")}))
    sys.exit()
dis = run("objdump", "-d", "-Mintel", "--no-show-raw-insn", p)
strs = run("strings", "-a", "-n", "3", p).splitlines()
# rodata address -> string (objdump -s gives the bytes)
ro = {}
for sec in (".rodata",):
    hexd = run("objdump", "-s", "-j", sec, p)
    base, buf = None, bytearray()
    for ln in hexd.splitlines():
        m = re.match(r"\s+([0-9a-f]+) ((?:[0-9a-f]{2,8} ?){1,4})", ln)
        if m:
            base = base if base is not None else int(m.group(1), 16)
            buf += bytes.fromhex(m.group(2).replace(" ", ""))
    ro = (base, bytes(buf))
cstr = lambda a: ro[1][a - ro[0]:ro[1].index(b"\0", a - ro[0])].decode()  # noqa: E731
funcs, cur = {}, None
for ln in dis.splitlines():
    m = re.match(r"[0-9a-f]+ <([^>]+)>:", ln)
    if m:
        cur = m.group(1); funcs[cur] = []
    elif cur and re.match(r"\s+[0-9a-f]+:\t", ln):
        a, ins = ln.split(":\t", 1)
        funcs[cur].append((int(a, 16), ins.strip()))
user = {f: v for f, v in funcs.items() if not f.startswith("_") and "@plt" not in f and f not in ("frame_dummy",
        "deregister_tm_clones", "register_tm_clones")}
dbg, vm, gates, vals = [], [], [], []
for f, ins in user.items():
    for k, (a, t) in enumerate(ins):
        if "<ptrace@plt>" in t and any(re.match(r"mov\s+edi,0x0$", x) for _, x in ins[max(0, k - 5):k]):
            dbg.append("ptrace_traceme")
if any("TracerPid" in s for s in strs):
    dbg.append("tracerpid")
if any(t.startswith(("rdtsc", "rdtscp")) for ins in user.values() for _, t in ins):
    dbg.append("timing")
for f, ins in user.items():
    for k, (a, t) in enumerate(ins):
        if t == "cpuid":
            leaf = next((x.split(",")[1] for _, x in reversed(ins[:k]) if re.match(r"mov\s+eax,", x)), None)
            if leaf == "0x1" and any(re.search(r"shr\s+\w+,0x1f|bt\s+\w+,0x1f|0x80000000", x) for _, x in ins[k:k + 20]):
                vm.append("cpuid_hypervisor")
            if leaf and leaf.startswith("0x4000000"):
                vm.append("cpuid_hypervisor_vendor")
dmi = [s for s in strs if s.startswith("/sys/class/dmi/")]
if dmi:
    vm.append("dmi")
vend = re.compile(r"VMware|VirtualBox|VBox|innotek|QEMU|KVMKVMKVM|Microsoft Hv|XenVMMXenVMM|Parallels|Hyper-V")
vms = [s for s in strs if vend.search(s)]
if vms:
    vm.append("vm_strings")
# getenv("X") then strcmp(.., "Y") later in the same function: lea reg,[rip+d] # <addr> feeding rdi / rsi
for f, ins in user.items():
    seen = False
    for k, (a, t) in enumerate(ins):
        if "<getenv@plt>" in t or "<strcmp@plt>" in t:
            for _, x in reversed(ins[max(0, k - 6):k]):
                m = re.search(r"# ([0-9a-f]+) <", x) if x.startswith("lea") else None
                if m:
                    (gates if "getenv" in t else vals if seen else []).append(cstr(int(m.group(1), 16)))
                    break
            seen = seen or "getenv" in t
syms = [ln.split()[-1] for ln in run("readelf", "-sW", p).splitlines() if " FUNC " in ln and " UND " not in ln]
dec = list(dict.fromkeys(s for s in syms if "decoy" in s.lower()))
order = lambda lst, ref: [x for x in ref if x in lst] or "none"  # noqa: E731
dbg = order(dbg, ["ptrace_traceme", "tracerpid", "timing"])
vm = order(vm, ["cpuid_hypervisor", "cpuid_hypervisor_vendor", "dmi", "vm_strings"])
print(json.dumps({"anti_debug": "true" if dbg != "none" else "false", "anti_vm": "true" if vm != "none" else "false",
                  "anti_debug_techniques": dbg, "anti_vm_techniques": vm, "vm_strings": vms or "none",
                  "dmi_paths": dmi or "none", "env_gates": list(dict.fromkeys(gates)) or "none",
                  "env_gate_values": list(dict.fromkeys(vals)) or "none", "decoy_functions": dec or "none",
                  "mitre_technique": "T1622" if dbg != "none" else "T1497.001" if vm != "none" else "none",
                  "uses:tracerpid": "true" if "tracerpid" in dbg else "false"}))
