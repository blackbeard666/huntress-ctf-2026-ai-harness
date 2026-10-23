"""Independent oracle for the yst_* fixtures: PyYAML safe_load_all for the descriptor value (escapes, !!binary, aliases,
CRLF, multi-doc resolved by the YAML library), the raw `#` comment block for the marker; stdlib base64 / bytes.fromhex.
Prints the v=3 plan (or `none`)."""
import base64, re, sys
import yaml


def peel(v):
    if isinstance(v, bytes):
        v = v.decode()
    v = re.sub(r"[\s.]", "", v)
    for f in (lambda s: base64.b64decode(s, validate=True), bytes.fromhex):
        try:
            p = f(v).decode()
        except Exception:
            continue
        if p.startswith("v=3|"):
            return p
    return None


def find(o):
    if isinstance(o, dict):
        for k, x in o.items():
            if k == "HUNTRESS_DESCRIPTOR":
                return x
            r = find(x)
            if r is not None:
                return r
    return None


text = open(sys.argv[1], "rb").read().decode()
out = None
for doc in yaml.safe_load_all(text):
    v = find(doc)
    out = out or (peel(v) if v is not None else None)
if not out:
    lines = text.replace("\r", "").split("\n")
    i = next(k for k, l in enumerate(lines) if "HUNTRESS_ANALYSIS_V1:" in l)
    mat = lines[i].split("HUNTRESS_ANALYSIS_V1:", 1)[1].strip()
    for l in lines[i + 1:]:
        if not l.startswith("#"):
            break
        mat += l[1:].strip()
    out = peel(mat.split("-", 1)[1]) if "-" in mat else None
print(out or "none")
