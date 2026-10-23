"""Independent oracle for cix_*.json (ci-expression-injection-secrets): PyYAML 6 safe_load + GitHub Security Lab's
untrusted-input list, never lib.codec. Usage: python3 -I cix_oracle.py <file.yml> <field>"""
import re
import sys

import yaml

UNT = re.compile(r"^(github\.head_ref|github\.event\.(issue|pull_request|comment|review|review_comment|discussion|pages|"
                 r"commits|head_commit)\b.*\.(title|body|message|name|email|label|ref|default_branch|head_ref|page_name))$")
EXP = re.compile(r"\$\{\{\s*(.*?)\s*\}\}")
path, field = sys.argv[1], sys.argv[2]
try:
    y = yaml.safe_load(open(path))
except Exception:
    y = None
if not isinstance(y, dict):
    print(None)
    raise SystemExit
out = []
if "jobs" in y:
    for jn, job in y["jobs"].items():
        for st in job.get("steps", []):
            nm = st.get("name") or st.get("uses")
            run = st.get("run") or ""
            env = st.get("env") or {}
            scr = (st.get("with") or {}).get("script", "") if "github-script" in str(st.get("uses")) else ""
            hits = [e for e in EXP.findall(run) + EXP.findall(scr) if UNT.match(e)]
            if field == "injectable_step" and hits:
                out.append(nm)
            if field == "sink" and hits:
                out.append("run" if EXP.findall(run) and any(UNT.match(e) for e in EXP.findall(run)) else "with.script")
            if field == "count":
                out += EXP.findall(yaml.safe_dump(st))
            if field == "env_injection":
                for k, v in env.items():
                    if any(UNT.match(e) for e in EXP.findall(str(v))) and re.search(
                            r"\$%s\b.*>>\s*\"?\$GITHUB_(ENV|PATH|OUTPUT)" % k, run):
                        out.append(nm)
            if field == "leaked_secret":
                for line in run.splitlines():
                    for e in EXP.findall(line):
                        if e.startswith("secrets.") and "add-mask" not in line and re.search(r"echo|curl|printf", line):
                            out.append(e.split(".", 1)[1])
else:
    for jn, job in y.items():
        if isinstance(job, dict) and "script" in job:
            for line in job["script"]:
                for v in re.findall(r"\$\{?([A-Z_][A-Z0-9_]*)", line):
                    if field == "untrusted_context" and v in ("CI_COMMIT_MESSAGE", "CI_COMMIT_TITLE",
                                                              "CI_MERGE_REQUEST_TITLE", "CI_COMMIT_REF_NAME"):
                        out.append(v)
print(str(len(out)) if field == "count" else ",".join(dict.fromkeys(out)) or "none")
