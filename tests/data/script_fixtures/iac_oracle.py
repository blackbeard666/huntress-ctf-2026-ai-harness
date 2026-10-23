"""Independent oracle for the iac_* fixtures: python-hcl2 (Terraform), PyYAML with CloudFormation short-tag
constructors (CFN YAML / Ansible), json (CFN JSON / ARM, + a regex ARM concat() evaluator), a Bicep regex -- then the
D21 bash `Material_x='<hex>'` / `Codec_x='xor_hex|<k>'` pair decoded with stdlib bytes.fromhex + XOR.
Run: .venv/bin/python -I iac_oracle.py <file>  -> plan text, or `none`."""
import json
import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools", "pylib-hcl2"))

import yaml

p = sys.argv[1]
t = open(p).read()


def cfn(v):
    if isinstance(v, str):
        return v
    if isinstance(v, dict) and len(v) == 1:
        k, x = next(iter(v.items()))
        k = k.replace("Fn::", "")
        if k == "Base64":
            return cfn(x)
        if k == "Sub":
            return cfn(x[0] if isinstance(x, list) else x)
        if k == "Join":
            return x[0].join(cfn(y) for y in x[1])
        return "${%s}" % x
    return ""


class L(yaml.SafeLoader):
    pass


for tag in ("Base64", "Sub", "Join", "Ref", "GetAtt"):
    key = tag if tag == "Ref" else "Fn::" + tag
    L.add_constructor("!" + tag, lambda ld, node, key=key: {key: (
        ld.construct_scalar(node) if isinstance(node, yaml.ScalarNode) else
        ld.construct_sequence(node, deep=True) if isinstance(node, yaml.SequenceNode) else ld.construct_mapping(node, deep=True))})

bodies = []
if p.endswith(".tf"):
    import hcl2
    d = hcl2.loads(t)

    def walk(n, key=None):
        if isinstance(n, dict):
            for k, v in n.items():
                walk(v, k)
        elif isinstance(n, list):
            for v in n:
                walk(v, key)
        elif isinstance(n, str) and key in ("command", "user_data"):
            lits = re.findall(r'"((?:[^"\\]|\\.)*)"', n)    # HCL literals (hcl2 keeps their quoting)
            bodies.append("".join(json.loads('"' + x + '"', strict=False) for x in lits).replace("$${", "${"))
    walk(d)
elif p.endswith(".bicep"):
    for v in re.findall(r"scriptContent:\s*'((?:[^'\\\n]|\\.)*)'", t):
        bodies.append(re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t", "r": "\r"}.get(m.group(1), m.group(1)), v))
elif p.endswith((".template", ".jsonc")):
    d = json.loads(t)
    for r in (d.get("Resources") or {}).values():
        bodies.append(cfn(r["Properties"].get("LaunchTemplateData", r["Properties"]).get("UserData")))
    for r in d.get("resources") or []:
        sc = r["properties"].get("scriptContent", "")
        if sc.startswith("[concat("):
            sc = "".join(x.replace("''", "'") for x in re.findall(r"'((?:[^']|'')*)'", sc))
        bodies.append(sc)
else:
    d = yaml.load(t, Loader=L)
    if isinstance(d, dict):
        for r in (d.get("Resources") or {}).values():
            bodies.append(cfn(r["Properties"].get("UserData")))
    else:
        for play in d:
            for task in play.get("tasks", []):
                for k, v in task.items():
                    if k.endswith("shell"):
                        bodies.append(v if isinstance(v, str) else v.get("cmd"))
body = "\n".join(b for b in bodies if b)
m = re.search(r"Material_(\w+)=[\"']([0-9a-fA-F]+)[\"']", body)
c = re.search(r"Codec_(\w+)=[\"']xor_hex\|([0-9a-fA-F]{2})[\"']", body)
out = "none"
if m and c:
    try:
        x = bytes(b ^ int(c.group(2), 16) for b in bytes.fromhex(m.group(2))).decode()
        out = x if x.startswith("v=3|") and x.count("|") > 8 else "none"
    except ValueError:
        pass
print(out)
