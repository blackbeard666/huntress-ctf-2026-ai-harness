"""Writes gha_trust_*.json: material = workflow text (hand-authored heredocs w1..w6.yml + the real D21 member), expected =
PyYAML 6 safe_load oracle (never lib.codec). Usage: python3 -I gha_trust_gen.py <dir with the .yml> <fixture dir>"""
import json
import sys

import yaml

d, out = sys.argv[1], sys.argv[2]
ON = "y=yaml.safe_load(open(sys.argv[1]));on=y.get(True,y.get('on'))"
FILT = ON + (";print('push:branches=%s;paths=%s|pull_request:types=%s|schedule:cron=%s'%(','.join(on['push']['branches']),"
             "','.join(on['push']['paths']),','.join(on['pull_request']['types']),on['schedule'][0]['cron']))")
cases = [
    ("gha_trust_on_push_trigger", "w1.yml", "trigger", None, ON + ";print(','.join([on] if isinstance(on,str) else list(on)))"),
    ("gha_trust_on_list_selfhosted", "w2.yml", "runner_type", None,
     "y=yaml.safe_load(open(sys.argv[1]));ro=y['jobs']['test']['runs-on'];print('self-hosted' if 'self-hosted' in ro else 'github-hosted')"),
    ("gha_trust_on_map_filters_trigger", "w3.yml", "trigger", None, ON + ";print(','.join(on))"),
    ("gha_trust_job_perm_writeall", "w3.yml", "permissions@lint", None,
     "y=yaml.safe_load(open(sys.argv[1]));print(y['jobs']['lint'].get('permissions', y.get('permissions')))"),
    ("gha_trust_schedule_cron_filter", "w3.yml", "trigger_filters", None, FILT),
    ("gha_trust_workflow_call", "w4.yml", "trigger", None, ON + ";print(','.join(on))"),
    ("gha_trust_prt_privileged", "w5.yml", "privileged", None,
     ON + ";P={'pull_request_target','workflow_run','issue_comment','issues','discussion','discussion_comment'};"
          "print(','.join(e for e in on if e in P))"),
    ("gha_trust_d21_trigger_enum", "d21.yml", "trigger", "push,pull_request_target,workflow_dispatch,schedule",
     ON + ";print(','.join(on))"),
    ("gha_trust_d21_runner_enum", "d21.yml", "runner", "self_hosted,github_hosted,container",
     "y=yaml.safe_load(open(sys.argv[1]));ro=y['jobs']['analyze']['runs-on'];"
     "print('self_hosted' if 'self-hosted' in str(ro) else 'github_hosted')"),
    ("gha_trust_decoy_gitlab", "w6.yml", "trigger", None,
     "y=yaml.safe_load(open(sys.argv[1]));print('jobs' in y)  # False -> not a GitHub Actions workflow"),
]
for name, f, tr, key, oc in cases:
    path = "%s/%s" % (d, f)
    src = open(path).read()
    res = []
    exec(oc, {"sys": type("S", (), {"argv": [None, path]}), "yaml": yaml, "open": open,  # noqa: S102 - oracle one-liner
              "print": lambda *a: res.append(" ".join(map(str, a)))})
    decoy = "decoy" in name
    fx = {"material": src, "rep": "gha_workflow", "transform": tr, "key": key, "expected": None if decoy else res[0],
          "decoy": decoy,
          "note": "gha-trigger-trust-model: lib.codec.gha_workflow/gha_answer via decode(rep='gha_workflow', "
                  "transform=<field>[@job], key=<accepted csv>)" + (" ; GitLab CI file is no GHA workflow -> None"
                                                                   if decoy else ""),
          "generator_cmd": ("cp challenges/day21/scripting-actions-speak-louder/single_solve/work/extracted/evidence/"
                            "polyglot-github_actions-benign-utility.yml d21.yml  (real D21 member bytes)" if f == "d21.yml"
                            else "cat > %s <<'EOF' (hand-authored synthetic workflow, heredoc; no lib code); "
                                 "tests/data/script_fixtures/gha_trust_gen.py writes the json" % f),
          "oracle_cmd": 'python3 -I -c "import yaml,sys;%s" %s  (PyYAML 6 safe_load)' % (oc, f)}
    with open("%s/gha_trust_%s.json" % (out, name[len("gha_trust_"):]), "w") as fh:
        json.dump(fx, fh, indent=1)
    print(name, "->", repr(fx["expected"]))
