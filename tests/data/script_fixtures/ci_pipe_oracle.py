"""Independent oracle for the ci_* fixtures: PyYAML (YAML hosts) / a Groovy string regex (Jenkinsfile) recovers the
step body with the host's own substitution, then stdlib base64 + XOR decodes Material_* with its Codec_* key.
Run: python3 -I ci_pipe_oracle.py <file>  -> plan text, or `none`."""
import base64
import re
import sys
import warnings

import yaml

warnings.simplefilter("ignore")

p = sys.argv[1]
t = open(p).read()
if p.endswith(".yml"):
    d = yaml.safe_load(t)
    env = {}
    for scope in [d] + list((d.get("jobs") or {}).values()):
        env.update({k: str(v) for k, v in ((scope.get("env") or scope.get("variables") or {}) if isinstance(scope, dict) else {}).items()})
    bodies = []
    def walk(n, key=None):
        if isinstance(n, dict):
            for k, v in n.items():
                walk(v, k)
        elif isinstance(n, list):
            if key in ("script", "commands") and all(isinstance(x, str) for x in n):
                bodies.append("\n".join(n))
            else:
                for x in n:
                    walk(x, key)
        elif isinstance(n, str) and key in ("run", "script", "bash", "pwsh", "powershell", "command"):
            bodies.append(n)
    walk(d)
    body = "\n".join(bodies)
    body = re.sub(r"\$\{\{\s*env\.(\w+)\s*\}\}|\$\((\w+)\)", lambda m: env.get(m.group(1) or m.group(2), m.group(0)), body)
else:
    env = dict(re.findall(r"^\s*(\w+)\s*=\s*'([^']*)'\s*$", t, re.M))
    lits = re.findall(r'"""(.*?)"""|"((?:[^"\\\n]|\\.)*)"\s*(\+)?', t, re.S)
    body = "".join(a or b for a, b, _ in lits).encode().decode("unicode_escape")
    body = re.sub(r"(?<!\\)\$\{(?:env\.)?(\w+)\}", lambda m: env.get(m.group(1), m.group(0)), body)
mat = re.search(r"Material_\w+='([^']*)'", body)
cod = re.search(r"Codec_\w+='base64\|single_byte_xor\|([0-9a-f]{2})'", body)
try:
    plain = bytes(b ^ int(cod.group(1), 16) for b in base64.b64decode(mat.group(1), validate=True)).decode()
    print(plain if plain.startswith("v=") else "none")
except Exception:
    print("none")
