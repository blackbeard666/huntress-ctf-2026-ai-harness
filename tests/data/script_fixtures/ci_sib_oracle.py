"""Independent oracle for the ci_sib_* fixtures: PyYAML (GitLab `!reference` accepted) finds every HUNTRESS_DESCRIPTOR
binding -- a map key, a `- name: X` + `value:` list item, or a shlex-split `export X=..` script line -- and stdlib
base64 decodes it. Run: python3 -I ci_sib_oracle.py <file>  -> plan text, or `none`."""
import base64
import binascii
import re
import shlex
import sys

import yaml

yaml.SafeLoader.add_constructor("!reference", lambda l, n: l.construct_sequence(n))
d = yaml.safe_load(open(sys.argv[1]).read())
vals = []


def walk(n):
    if isinstance(n, dict):
        if str(n.get("name", "")).upper() == "HUNTRESS_DESCRIPTOR" and "value" in n:
            vals.append(str(n["value"]))
        for k, v in n.items():
            if str(k).upper() == "HUNTRESS_DESCRIPTOR" or re.fullmatch(r"HUNTRESS_DESCRIPTOR_\w+", str(k)):
                vals.append(str(v))
            walk(v)
    elif isinstance(n, list):
        for x in n:
            walk(x)
    elif isinstance(n, str):
        for ln in n.splitlines():
            for w in (shlex.split(ln) if ln.strip().startswith("export ") else []):
                if w.startswith("HUNTRESS_DESCRIPTOR="):
                    vals.append(w.split("=", 1)[1])


walk(d)
for v in vals:
    try:
        p = base64.b64decode(re.sub(r"\s", "", v), validate=True).decode()
        if p.startswith("v=3|"):
            print(p)
            break
    except (binascii.Error, UnicodeDecodeError):
        pass
else:
    print("none")
