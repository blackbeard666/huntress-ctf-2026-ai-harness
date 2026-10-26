"""Independent oracle for the stage-config-survival-diff fixtures. Reads every stage of a cfgchain_*.tree with a
real reader (Elixir 1.18 Config.Reader / :file.consult via cfgchain_oracle.exs, tomllib, PyYAML safe_load, json,
shlex for vm.args / .env, '|'-split for v=3 plans), then answers `lost_key|lost_value|vanished_at|last_seen`:
the first key of the ORIGIN stage (the first non-plan stage) that is absent (snake/camel/upper-normalised) from the
final stage, whose value no final-stage key carries (a rename), preferring keys the campaign's v=3 plan names.
vanished_at = the stage after its last appearance. Usage: cfgchain_oracle.py <tree> <field>"""
import json, os, re, shlex, subprocess, sys, tempfile, tomllib
import yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
ENVP = os.path.join(ROOT, "../../../tools/erlang-dl/root/usr/lib/erlang/bin") + ":" + \
    os.path.join(ROOT, "../../../tools/elixir/bin") + ":" + os.environ["PATH"]


def norm(k):
    return re.sub(r"[^a-z0-9]+", "_", re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(k)).lower()).strip("_")


def leaves(x, out):
    if isinstance(x, dict):
        for k, v in x.items():
            if isinstance(v, dict):
                leaves(v, out)
            else:
                out.setdefault(str(k), str(v).lower() if isinstance(v, bool) else str(v))
    return out


def read(name, text):
    base = name.rsplit("/", 1)[-1]
    if text.startswith("v="):
        return "plan", dict(p.split("=", 1) for p in text.strip().split("|"))
    if base.endswith(".exs") or base.endswith(".config"):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, base)
            open(f, "w").write(text)
            r = subprocess.run(["elixir", os.path.join(ROOT, "cfgchain_oracle.exs"), f], capture_output=True,
                               text=True, env={**os.environ, "PATH": ENVP}, timeout=60)
        return "x", dict(ln.split("\t", 1) for ln in r.stdout.splitlines() if "\t" in ln)
    if base == "vm.args":
        out = {}
        for ln in text.splitlines():
            w = shlex.split(ln)
            if len(w) == 2:
                out.setdefault(w[0].lstrip("-+"), w[1])
        return "x", out
    if base.startswith(".env"):
        return "x", {k: v for k, v in (shlex.split(ln)[0].split("=", 1) for ln in text.splitlines() if "=" in ln)}
    if base.endswith(".toml"):
        return "x", leaves(tomllib.loads(text), {})
    if base.endswith((".yml", ".yaml")):
        return "x", leaves(yaml.safe_load(text), {})
    return "x", leaves(json.loads(text), {})


tree, field = json.load(open(sys.argv[1])), sys.argv[2]
chain = [(m,) + read(m, t) for m, t in tree.items()]
stages = [(m, d) for m, f, d in chain if f != "plan"]
plan = next((d for m, f, d in chain if f == "plan"), {})
first, final = stages[0][1], stages[-1][1]
fin_n, fin_v = {norm(k) for k in final}, set(final.values())
cands = [k for k in first if norm(k) not in fin_n and first[k] not in fin_v]
cands.sort(key=lambda k: norm(k) not in {norm(p) for p in plan})
if not cands:
    print("none")
    raise SystemExit
k = cands[0]
last = max(i for i, (m, d) in enumerate(stages) if norm(k) in {norm(x) for x in d})
val = {norm(x): v for x, v in stages[last][1].items()}[norm(k)]
print({"lost_key": k, "lost_value": val, "vanished_at": stages[last + 1][0], "last_seen": stages[last][0]}[field])
