"""Independent oracle for dtrace_*.bin: RUN the program under bwrap (--unshare-all incl. net, --clearenv, ro binds,
x86-64 ELF only, never directly on the host) once per HUNTRESS_HOST_MODEL option, json.loads its trace line; env name
and model options from `strings -n 4`. Prints expected_facts JSON. usage: python3 dtrace_oracle.py <file.bin>"""
import json, re, shutil, subprocess, sys, tempfile, os

MODELS = ("analysis", "sandbox", "workstation")
p = os.path.abspath(sys.argv[1])
strs = subprocess.run(["strings", "-n", "4", p], capture_output=True, text=True).stdout.split("\n")
envs = [s for s in strs if re.fullmatch(r"HUNTRESS_[A-Z0-9_]+", s)]
models = [m for m in MODELS if any(m == s.strip() for s in strs)]
none = {k: "none" for k in ("trace_schema", "trace_family", "trace_effects", "trace_network", "trace_keys",
                            "host_model_env", "host_models")}
none.update({f"branch_for_{m}": "none" for m in MODELS})


def run(model):
    with tempfile.TemporaryDirectory() as d:
        x = os.path.join(d, "x")
        shutil.copy(p, x)
        os.chmod(x, 0o555)
        cmd = ["bwrap", "--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib", "--ro-bind", "/lib64", "/lib64",
               "--ro-bind", x, "/x", "--unshare-all", "--unshare-net", "--die-with-parent", "--clearenv",
               "--setenv", "HUNTRESS_HOST_MODEL", model, "/x"]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10, stdin=subprocess.DEVNULL).stdout
    for line in out.splitlines():
        try:
            j = json.loads(line)
        except ValueError:
            continue
        if isinstance(j, dict) and "schema" in j:
            return j
    return None


runs = {m: run(m) for m in MODELS}
first = next((j for j in runs.values() if j), None)
if not first or first.get("schema") != "huntress.binary.dynamic_trace.v1" or not envs:
    print(json.dumps(none, indent=1))
    sys.exit(0)
exp = {"trace_schema": first["schema"], "trace_family": first.get("family", "none"),
       "trace_effects": first.get("effects", "none"), "trace_network": first.get("network", "none"),
       "trace_keys": list(first), "host_model_env": envs[0], "host_models": models or "none"}
exp.update({f"branch_for_{m}": (runs[m] or {}).get("branch", "none") for m in MODELS})
exp["_event_count_by_model"] = {m: (runs[m] or {}).get("event_count") for m in MODELS}   # informative, not checked
print(json.dumps(exp, indent=1))
