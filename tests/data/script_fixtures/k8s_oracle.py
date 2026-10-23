"""Independent oracle for the k8s_* fixtures: PyYAML safe_load_all over the manifest (Helm: the values doc via PyYAML,
`{{ .Values.a.b }}` / `{{ "x" | b64dec }}` substituted with str.replace-level regex, control lines dropped), every
string leaf (Secret data base64-decoded by stdlib), then the bash `Material_x='..'` / `Codec_x='base64_literal|
add_modulo_256|K'` pair decoded with stdlib base64 + (b - K) & 0xff. Prints the plan or `none`.
Run: python3 -I k8s_oracle.py <file.yaml>"""
import base64
import re
import sys

import yaml

t = open(sys.argv[1]).read()
if "{{" in t:
    vals = next(d for d in yaml.safe_load_all(re.sub(r"\{\{.*?\}\}", "", t)) if d and "kind" not in d)

    def look(p):
        v = vals
        for k in p.split("."):
            v = v.get(k) if isinstance(v, dict) else None
        return v
    t = re.sub(r'\{\{-?\s*"([A-Za-z0-9+/=]*)"\s*\|\s*b64dec\s*-?\}\}', lambda m: base64.b64decode(m.group(1)).decode(), t)
    t = re.sub(r"\{\{-?\s*\.Values\.([\w.]+)\s*(?:\|\s*default\s+(\"[^\"]*\"))?\s*(\|\s*quote)?\s*-?\}\}",
               lambda m: str(look(m.group(1)) or (m.group(2) or '""')[1:-1]), t)
    t = "\n".join(ln for ln in t.splitlines() if not re.fullmatch(r"\s*\{\{.*\}\}\s*", ln))
    t = re.sub(r"\{\{.*?\}\}", "", t)
leaves = []


def walk(x, secret=False):
    if isinstance(x, dict):
        for k, v in x.items():
            walk(v, secret or (k == "data" and x.get("kind") is None and secret))
    elif isinstance(x, list):
        for v in x:
            walk(v)
    elif isinstance(x, str):
        leaves.append(x)


for d in yaml.safe_load_all(t):
    if not isinstance(d, dict):
        continue
    if d.get("kind") == "Secret":
        for v in (d.get("data") or {}).values():
            try:
                leaves.append(base64.b64decode(v, validate=True).decode())
            except Exception:
                pass
    walk(d)
for s in leaves:
    m = re.search(r"Material_\w+='([^']+)'", s)
    c = re.search(r"Codec_\w+='base64_literal\|add_modulo_256\|([0-9a-f]+)'", s)
    if m and c:
        try:
            raw = base64.b64decode(m.group(1), validate=True)
        except Exception:
            continue
        p = bytes((b - int(c.group(1), 16)) & 0xFF for b in raw).decode("latin-1")
        if p.startswith("v=") and "campaign_id=" in p:
            print(p)
            sys.exit(0)
print("none")
