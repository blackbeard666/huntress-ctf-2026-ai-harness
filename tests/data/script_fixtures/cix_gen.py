"""Writes cix_*.json: material = hand-authored heredoc workflows cix_w1..w5 (+ the real D21 launcher member cix_d21.yml),
expected = cix_oracle.py (PyYAML 6, never lib.codec). Usage: python3 -I cix_gen.py <fixture dir>"""
import json
import subprocess
import sys

d = sys.argv[1]
cases = [   # name, source, decode transform (= oracle field[@step]), decoy
    ("cix_gha_issue_title_step", "cix_w1.yml", "injectable_step", False),
    ("cix_gha_leaked_secret", "cix_w1.yml", "leaked_secret", False),
    ("cix_gha_env_injection", "cix_w2.yml", "env_injection", False),
    ("cix_gha_github_script_sink", "cix_w2.yml", "sink@Comment", False),
    ("cix_gitlab_commit_message", "cix_w3.yml", "untrusted_context", False),
    ("cix_gha_clean_none", "cix_w4.yml", "injectable_step", False),
    ("cix_d21_launcher_count", "cix_d21.yml", "count", False),
    ("cix_decoy_notes", "cix_w5.txt", "injectable_step", True),
]
for name, src, tr, decoy in cases:
    field = tr.split("@")[0]
    oc = "python3 -I tests/data/script_fixtures/cix_oracle.py tests/data/script_fixtures/%s %s  (PyYAML 6 safe_load)" % (
        src, field)
    got = subprocess.run(["python3", "-I", "%s/cix_oracle.py" % d, "%s/%s" % (d, src), field],
                         capture_output=True, text=True).stdout.strip()
    fx = {"material": open("%s/%s" % (d, src)).read(), "rep": "ci_expressions", "transform": tr, "key": None,
          "expected": None if decoy or got == "None" else got, "decoy": decoy,
          "note": "ci-expression-injection-secrets: lib.codec.ci_expressions/ci_expr_answer via decode(rep='ci_expressions',"
                  " transform=<field>[@job|step])",
          "generator_cmd": ("cat > %s <<'EOF' (hand-authored synthetic CI file, heredoc; no lib code)" % src
                            if src != "cix_d21.yml" else "cp challenges/day21/scripting-actions-speak-louder/single_solve/"
                            "work/extracted/evidence/polyglot-github_actions-launcher.yml cix_d21.yml (real D21 member)")
                           + "; tests/data/script_fixtures/cix_gen.py writes the json",
          "oracle_cmd": oc}
    open("%s/%s.json" % (d, name), "w").write(json.dumps(fx, indent=1) + "\n")
    print(name, repr(fx["expected"]))
