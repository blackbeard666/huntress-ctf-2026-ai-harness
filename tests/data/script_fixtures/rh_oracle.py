"""Independent oracle for the git-repo-hooks-route fixtures: rebuilds a rh_<name>.tree into a temp dir and answers
one selector with the git CLI (git config --get-regexp / git check-attr), PyYAML, stdlib json and the shebang line --
never lib.codec. Usage: rh_oracle.py <tree> <field@selector>; prints the value (or null when the surface is absent)."""
import json
import os
import subprocess
import sys
import tempfile

import yaml

tree, sel = json.load(open(sys.argv[1])), sys.argv[2]
d = tempfile.mkdtemp()
for n, t in tree.items():
    os.makedirs(os.path.dirname(os.path.join(d, n)) or d, exist_ok=True)
    open(os.path.join(d, n), "w").write(t)
for sub in ("objects", "refs"):   # a valid repo (HEAD/objects/refs are not shipped in the tree) so git never walks up
    os.makedirs(os.path.join(d, ".git", sub), exist_ok=True)
open(os.path.join(d, ".git", "HEAD"), "w").write("ref: refs/heads/master\n")
env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", HOME=d, GIT_CEILING_DIRECTORIES=os.path.dirname(d))


def git(*a):
    r = subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, env=env)
    return r.stdout.strip()


def cfg(regex, f=".git/config"):
    out = git("config", "--file", os.path.join(d, f), "--get-regexp", regex) if os.path.exists(os.path.join(d, f)) else ""
    return [ln.split(" ", 1) for ln in out.splitlines() if ln]


def shebang_interp(p):
    first = open(os.path.join(d, p)).readline().strip()
    ws = first[2:].split()
    w = ws[0].rsplit("/", 1)[-1]
    return ws[1] if w == "env" else w


field, _, what = sel.partition("@")
val = None
if sel == "command@smudge":
    val = ",".join(v for k, v in cfg(r"^filter\..*\.smudge$"))
elif sel == "pattern@smudge":
    name = cfg(r"^filter\..*\.smudge$")[0][0].split(".")[1]
    pats = [ln.split()[0] for ln in open(os.path.join(d, ".gitattributes")) if f"filter={name}" in ln.split()]
    assert all(git("check-attr", "filter", "--", p.replace("*", "x")).endswith(": " + name) for p in pats)
    val = ",".join(pats)
elif sel == "command@textconv":
    val = ",".join(v for k, v in cfg(r"^diff\..*\.textconv$"))
elif sel == "command@hooksPath":
    val = git("config", "--file", os.path.join(d, ".git/config"), "core.hooksPath")
elif sel.startswith("interpreter@"):
    hp = git("config", "--file", os.path.join(d, ".git/config"), "core.hooksPath")
    cands = [p for p in (f".git/hooks/{what}", f"{hp}/{what}" if hp else "") if p and os.path.exists(os.path.join(d, p))]
    val = ",".join(shebang_interp(p) for p in cands)
elif sel == "command@update":
    val = ",".join(v[1:] for k, v in cfg(r"^submodule\..*\.update$", ".gitmodules") if v.startswith("!"))
elif sel.startswith("command@local#"):
    doc = yaml.safe_load(open(os.path.join(d, ".pre-commit-config.yaml")))
    hid = what.split("#", 1)[1]
    val = ",".join(" ".join([h["entry"], *h.get("args", [])]) for r in doc["repos"] if r["repo"] == "local"
                   for h in r["hooks"] if h["id"] == hid)
elif sel == "trigger@local#evil":
    doc = yaml.safe_load(open(os.path.join(d, ".pre-commit-config.yaml")))
    val = ",".join(",".join(h.get("stages") or doc.get("default_stages")) for r in doc["repos"] if r["repo"] == "local"
                   for h in r["hooks"] if h["id"] == "evil")
elif field == "command" and what.startswith("post") and what.endswith("Command"):
    v = json.load(open(os.path.join(d, ".devcontainer/devcontainer.json"))).get(what)
    val = " ".join(v) if isinstance(v, list) else v
elif sel == "command@folderOpen":
    ts = json.load(open(os.path.join(d, ".vscode/tasks.json")))["tasks"]
    val = ",".join(" ".join([t["command"], *t.get("args", [])]) for t in ts
                   if (t.get("runOptions") or {}).get("runOn") == "folderOpen")
elif sel == "command@husky":
    val = ",".join(open(os.path.join(d, ".husky", f)).read().strip() for f in sorted(os.listdir(os.path.join(d, ".husky")))
                   if os.path.isfile(os.path.join(d, ".husky", f)))
elif sel == "surface":   # decoy probe: any auto-run surface at all?
    hp = git("config", "--file", os.path.join(d, ".git/config"), "core.hooksPath")
    live = [f for f in os.listdir(os.path.join(d, ".git/hooks")) if not f.endswith(".sample")]
    drv = cfg(r"^(filter|diff|merge)\.|^core\.(fsmonitor|hookspath|sshcommand|pager|editor)$|^alias\.")
    dc = json.load(open(os.path.join(d, ".devcontainer/devcontainer.json")))
    lc = [k for k in dc if k.endswith("Command")]
    fo = [t for t in json.load(open(os.path.join(d, ".vscode/tasks.json")))["tasks"]
          if (t.get("runOptions") or {}).get("runOn") == "folderOpen"]
    val = None if not (hp or live or drv or lc or fo or os.path.exists(os.path.join(d, ".gitmodules"))) else "present"
print(json.dumps(val or None))
