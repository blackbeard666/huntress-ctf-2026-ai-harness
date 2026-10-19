"""Independent oracle for apiint_* fixtures: import names from readelf --dyn-syms (UND) / objdump -p (PE), ptrace
request from objdump -d (AT&T `mov $imm,%edi` before `call <ptrace@plt>`), /proc/<pid>/mem from `strings`, intent
by this file's own hand table (not lib.binary). usage: python3 apiint_oracle.py X.bin -> expected_facts JSON."""
import json, re, subprocess, sys

f = sys.argv[1]
ft = subprocess.run(["file", "-b", f], capture_output=True, text=True).stdout
TAB = {"env_query": "getenv GetEnvironmentVariableA _gfortran_get_environment_variable_i4",
       "output": "printf puts __printf_chk _gfortran_st_write _gfortran_st_write_done "
                 "_gfortran_transfer_character_write _gfortran_transfer_integer_write",
       "string": "strcmp lstrcmpA _gfortran_select_string _gfortran_string_len_trim",
       "process_access": "ptrace process_vm_readv OpenProcess",
       "injection": "process_vm_writev VirtualAllocEx WriteProcessMemory CreateRemoteThread",
       "network": "WSAStartup socket connect", "dynamic_load": "LoadLibraryA GetProcAddress",
       "runtime": "__libc_start_main __gmon_start__ _gfortran_set_args _gfortran_set_options ExitProcess "
                  "__stack_chk_fail __cxa_finalize _ITM_registerTMCloneTable _ITM_deregisterTMCloneTable"}
INT = {n: k for k, v in TAB.items() for n in v.split()}
POKE = {4: "PTRACE_POKETEXT", 5: "PTRACE_POKEDATA", 13: "PTRACE_SETREGS"}
REQ = {16: "PTRACE_ATTACH", 17: "PTRACE_DETACH", 2: "PTRACE_PEEKDATA", 1: "PTRACE_PEEKTEXT", **POKE}
if ft.startswith("ELF"):
    out = subprocess.run(["readelf", "-W", "--dyn-syms", f], capture_output=True, text=True).stdout
    names = [l.split()[7].split("@")[0] for l in out.splitlines() if re.match(r"\s*\d+:", l) and len(l.split()) > 7
             and l.split()[6] == "UND"]
    dis = subprocess.run(["objdump", "-d", "--no-show-raw-insn", f], capture_output=True, text=True).stdout
    reqs, last = [], None
    for l in dis.splitlines():
        m = re.search(r"mov\s+\$0x([0-9a-f]+),%edi|xor\s+%edi,%edi", l)
        if m:
            last = int(m.group(1), 16) if m.group(1) else 0
        if re.search(r"call\s+\S+ <ptrace@plt>", l):
            reqs.append(REQ.get(last, "unknown"))
            last = None
elif ft.startswith("PE32"):
    out = subprocess.run(["objdump", "-p", f], capture_output=True, text=True).stdout
    names = re.findall(r"^\s+[0-9a-f]{8}\s+<none>\s+[0-9a-f]{4}\s+(\S+)", out, re.M)
    reqs = []
else:
    print(json.dumps({k: "none" for k in ("has_injection", "injection_apis", "process_access_apis", "effects")}))
    sys.exit()
strs = subprocess.run(["strings", "-a", f], capture_output=True, text=True).stdout
intents = {n: INT.get(n, "other") for n in names}
if "ptrace" in intents and any(r in POKE.values() for r in reqs):
    intents["ptrace"] = "injection"
inj = [n for n in names if intents[n] == "injection"]
acc = [n for n in names if intents[n] == "process_access"] + (["/proc/<pid>/mem"] if "/proc/%d/mem" in strs else [])
net = [n for n in names if intents[n] == "network"]
mitre = (["T1055.008"] if any(r in POKE.values() for r in reqs) else []) + \
        (["T1055.009"] if "process_vm_writev" in names else []) + \
        (["T1055.001"] if {"WriteProcessMemory", "CreateRemoteThread", "LoadLibraryA"} <= set(names) else [])
eff = re.search(r'"effects":"([^"]+)"', strs)
print(json.dumps({"api_intents": intents, "has_injection": "true" if inj else "false",
                  "injection_apis": inj or "none", "process_access_apis": acc or "none", "network_apis": net or "none",
                  "ptrace_requests": reqs or "none", "mitre_technique": mitre[0] if mitre else "none",
                  "mitre_techniques": mitre or "none",
                  "effects": ("process_access_and_injection" if inj and acc else "injection" if inj else
                              "modeled_process_access_no_injection" if acc else "no_process_access_no_injection"),
                  "trace_effects": eff.group(1) if eff else "none"}, indent=1))
