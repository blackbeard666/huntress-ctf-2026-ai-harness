"""Independent oracle for predbr_*.bin: RUN the program under bwrap (--unshare-all incl. net, --clearenv, ro binds,
never directly on the host) with HUNTRESS_HOST_MODEL unset, set to a bogus value, and set to each candidate (the
D10-D23 options analysis/sandbox/workstation + every lowercase `strings -n 4` token); a candidate is a host model when
its trace record differs from the bogus-value run. json.loads of the trace line. Prints the fixture JSON.
usage: python3 predbr_oracle.py <file.bin>"""
import json, re, shutil, subprocess, sys, tempfile, os

MODELS = ("analysis", "sandbox", "workstation")
p = os.path.abspath(sys.argv[1])
name = os.path.basename(p)
strs = subprocess.run(["strings", "-n", "4", p], capture_output=True, text=True).stdout.split("\n")
envs = [s for s in strs if re.fullmatch(r"HUNTRESS_[A-Z0-9_]+", s)]
cands = list(dict.fromkeys(list(MODELS) + [s for s in strs if re.fullmatch(r"[a-z][a-z0-9]{3,15}", s)]))
is_elf = open(p, "rb").read(4) == b"\x7fELF"


def run(model):
    with tempfile.TemporaryDirectory() as d:
        x = os.path.join(d, "x")
        shutil.copy(p, x)
        os.chmod(x, 0o555)
        cmd = ["bwrap", "--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib", "--ro-bind", "/lib64", "/lib64",
               "--ro-bind", x, "/x", "--unshare-all", "--unshare-net", "--die-with-parent", "--clearenv"]
        if model is not None:
            cmd += ["--setenv", "HUNTRESS_HOST_MODEL", model]
        try:
            out = subprocess.run(cmd + ["/x"], capture_output=True, text=True, timeout=10,
                                 stdin=subprocess.DEVNULL).stdout
        except Exception:  # noqa: BLE001
            return None
    for line in out.splitlines():
        try:
            j = json.loads(line)
        except ValueError:
            continue
        if isinstance(j, dict) and "branch" in j:
            return j
    return None


def trio(j):
    if not j:
        return "none", "none", "none"
    ad = j.get("analysis_detected", "none")
    return (j.get("branch", "none"), j.get("event_count", "none"),
            ("true" if ad else "false") if isinstance(ad, bool) else ad)


exp = {"host_model_env": "none", "host_models": "none"}
for m in MODELS:
    exp.update({f"branch_for_{m}": "none", f"event_count_for_{m}": "none", f"analysis_detected_for_{m}": "none"})
exp.update({"branch_unset": "none", "event_count_unset": "none", "analysis_detected_unset": "none"})
if is_elf and "HUNTRESS_HOST_MODEL" in envs:
    base = run("zz-not-a-model")
    runs = {c: run(c) for c in cands}
    models = sorted(c for c, j in runs.items() if j and j != base)
    if models:
        exp["host_model_env"] = "HUNTRESS_HOST_MODEL"
        exp["host_models"] = models
        for m in sorted(set(models) | set(MODELS)):
            b, n, ad = trio(runs.get(m) or base)
            exp.update({f"branch_for_{m}": b, f"event_count_for_{m}": n, f"analysis_detected_for_{m}": ad})
        exp["branch_unset"], exp["event_count_unset"], exp["analysis_detected_unset"] = trio(run(None))
decoy = exp["host_model_env"] == "none"
print(json.dumps({
    "family": "predicate_branch", "encoding": "none", "expected_offset": None, "expected_config": None,
    "expected_facts": exp,
    "generator_cmd": "sh predbr_gen.sh   # gcc over predbr_src/*.c (see the per-file line in predbr_gen.sh)",
    "oracle_cmd": f"python3 predbr_oracle.py {name}   # bwrap --unshare-all --clearenv run per HUNTRESS_HOST_MODEL "
                  "candidate, json.loads of the trace line",
    "decoy": decoy,
    "note": "lib.binary.predicate_branch_field(data, key) per expected_facts key; branch/event_count/analysis_detected "
            "per host model from a sandboxed REAL run (oracle) vs lib's unicorn emulation of main with libc hooked",
}, indent=1))
