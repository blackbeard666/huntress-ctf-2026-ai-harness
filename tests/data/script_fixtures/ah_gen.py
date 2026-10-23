"""Writes the github-action-definition-route fixtures' synthetic repo trees (stdlib only): ah_<name>.tree =
{member path: text}. The expected rows come from ah_oracle.py (PyYAML), never from lib.codec."""
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
trees = {
    "ah_repo_tree": {
        ".github/workflows/ci.yml": (
            "name: ci\non:\n  push:\n  pull_request_target:\njobs:\n  build:\n    runs-on: windows-latest\n"
            "    steps:\n      - uses: actions/checkout@v4\n      - uses: ./.github/actions/setup\n"
            "      - name: stage\n        run: |\n          $u = 'https://stage.example.invalid/a.ps1'\n"
            "          Write-Host $u\n      - name: cmd step\n        shell: cmd\n        run: echo stage>%TEMP%\\s.txt\n"
            "      - uses: actions/github-script@v7\n        with:\n          script: |\n"
            "            const fs = require('fs');\n            core.info('handoff');\n"
            "      - name: perl\n        shell: perl {0}\n        run: print \"x\\n\";\n"
            "      - run: ':'\n  reuse:\n    uses: octo/shared/.github/workflows/deploy.yml@v2\n"
            "    with:\n      target: prod\n    secrets: inherit\n"),
        ".github/actions/setup/action.yml": (
            "name: setup\ndescription: composite\nruns:\n  using: composite\n  steps:\n"
            "    - run: python3 -c \"print(1)\"\n      shell: python\n    - run: ./tools/boot.sh\n      shell: bash\n"
            "    - uses: ./.github/actions/js\n"),
        ".github/actions/js/action.yaml": (
            "name: js\nruns:\n  using: node20\n  pre: setup.js\n  main: dist/index.js\n  post: cleanup.ts\n"),
        ".github/actions/js/dist/index.js": "console.log('main');\n",
        ".github/actions/js/setup.js": "console.log('pre');\n",
        ".github/actions/dock/action.yml": (
            "name: dock\nruns:\n  using: docker\n  image: Dockerfile\n  entrypoint: /bin/sh\n"
            "  args:\n    - -c\n    - echo hi\n  post-entrypoint: /cleanup.ps1\n"),
        ".github/actions/dock/Dockerfile": "FROM alpine:3.20\nCOPY cleanup.ps1 /cleanup.ps1\nENTRYPOINT [\"/bin/sh\"]\n",
    },
    "ah_docker_uri": {
        "action.yml": ("name: remote\nruns:\n  using: docker\n  image: docker://ghcr.io/octo/tool:1\n"
                       "  entrypoint: python3\n  args: ['-c', 'print(2)']\n"),
    },
    # decoy: the D21 member shape -- descriptor in env, the only step is the no-op `run: ':'` -> no handoff
    "ah_decoy_noop": {
        "polyglot-github_actions-benign-utility.yml": (
            "name: Huntress inert analysis 278f1c07\non:\n  workflow_dispatch:\njobs:\n  analyze:\n"
            "    runs-on: ubuntu-latest\n    env:\n      HUNTRESS_DESCRIPTOR: \"dj0zfGxhbmd1YWdl\"\n    steps:\n"
            "      - name: Preserve modeled descriptor\n        run: ':'\n"),
    },
}
for k, v in trees.items():
    (out / (k + ".tree")).write_text(json.dumps(v, indent=1, sort_keys=True) + "\n")
