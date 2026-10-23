"""Independent oracle for the github-action-definition-route fixtures: PyYAML safe_load + the GitHub Actions docs'
rules (shell keywords, defaults.run.shell, windows default pwsh, runs.using composite/node*/docker), stdlib posixpath.
Prints `<field>` values (','-joined, row order = member order, then document order) for one tree."""
import json
import posixpath
import sys

import yaml

SH = {"bash": "bash", "sh": "bash", "pwsh": "powershell", "powershell": "powershell", "python": "python",
      "cmd": "batch", "perl": "perl", "node": "node", "python3": "python"}
EXT = {".sh": "bash", ".ps1": "powershell", ".py": "python", ".js": "node", ".ts": "typescript", ".cmd": "batch"}
tree, field = json.load(open(sys.argv[1])), sys.argv[2]
rows = []


def using(path):
    for n in (path + "/action.yml", path + "/action.yaml"):
        if n in tree:
            u = str(yaml.safe_load(tree[n])["runs"]["using"])
            return "node" if u.startswith("node") else u
    return "github_actions"


def steps(name, sts, dflt):
    for st in sts or []:
        if "run" in st and str(st["run"]).strip() not in (":", "true"):
            rows.append(("run", SH[str(st.get("shell", dflt)).split()[0]]))
        u = str(st.get("uses", ""))
        if u.startswith("actions/github-script"):
            rows.append(("github_script", "node"))
        elif "/.github/workflows/" in "/" + u:
            rows.append(("reusable_workflow", "github_actions"))
        elif u.startswith("./"):
            rows.append(("local_action", using(posixpath.normpath(u))))


def entry(e):
    w = posixpath.basename(e.split()[0])
    return EXT.get(posixpath.splitext(w)[1]) or SH.get(w)


for name, text in tree.items():
    if not name.endswith((".yml", ".yaml")):
        continue
    d = yaml.safe_load(text)
    if "runs" in d:
        r = d["runs"]
        if r["using"] == "composite":
            steps(name, r["steps"], "bash")
        elif r["using"].startswith("node"):
            for k in ("pre", "main", "post"):
                if k in r:
                    rows.append(("node_" + k, "typescript" if r[k].endswith(".ts") else "node"))
        else:
            rows.append(("docker_image", "container" if r["image"].startswith("docker://") else "dockerfile"))
            for k in ("pre-entrypoint", "entrypoint", "post-entrypoint"):
                if k in r:
                    rows.append(("docker_" + k.replace("-", "_"), entry(r[k])))
        continue
    for job in d.get("jobs", {}).values():
        dflt = "pwsh" if "windows" in str(job.get("runs-on", "")) else "bash"
        if "uses" in job:
            steps(name, [{"uses": job["uses"]}], dflt)
        steps(name, job.get("steps"), dflt)
print(",".join(r[0 if field == "via" else 1] for r in rows))
