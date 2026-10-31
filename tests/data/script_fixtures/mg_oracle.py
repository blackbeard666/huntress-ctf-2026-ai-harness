"""Independent oracle for the mixed-grammar-single-contract fixtures (stdlib only, never lib.codec): reads the fixture
material JSON {contract, plans} and answers one id from the contract's own spec -- the question's `artifact`
(`<zip> -> <member>`) names the member (else the plan whose language + role are the id's first two tokens), the id's
grammar is per_file iff a hex token equals that set's member stem, the field is the id tail after the member tokens.
Run: python3 mg_oracle.py <fixture.json>   (prints the expected value, or null)"""
import json
import re
import sys
from urllib.parse import urlparse


def kv(text):
    return dict(p.split("=", 1) for p in text.split("|") if "=" in p)


def answer(mat, aid, key=None):
    d = json.loads(mat)
    plans = d["plans"]
    q = next((x for x in d["contract"]["questions"] if x["id"] == aid), None)
    if q is None:
        return None
    zipname, _, member = (s.strip() for s in q["artifact"].partition("->"))
    members = [m for m in plans if m.split("/")[0] == zipname]
    stems = {m.split("/")[-1].split(".")[0]: m for m in members}
    toks = re.sub(r"^set\d+\.", "", aid).split("-")
    hexes = [i for i, t in enumerate(toks) if re.fullmatch(r"[0-9a-f]{6}", t) and t in stems]
    grammar = "per_file" if hexes else "semantic"
    if key == "grammar":
        return grammar
    if hexes:
        m = stems[toks[hexes[0]]]
        field = toks[hexes[0] + 1:]
    else:
        if member:
            m = zipname + "/" + member
            if m not in plans:
                return None
        else:
            hit = [x for x in members if kv(plans[x]).get("language") == toks[0] and kv(plans[x]).get("role") == toks[1]]
            if len(hit) != 1:
                return None
            m = hit[0]
        field = toks[2:]
    p = kv(plans[m])
    f = "-".join(field)
    if f == "campaign":
        return p.get("campaign")
    if f == "campaign-token":
        return p["campaign"].split("-", 1)[1] if "campaign" in p else None
    if f == "url":
        return p.get("url")
    if f == "url-host":
        return urlparse(p["url"]).hostname if "url" in p else None
    if f == "path-leaf":
        return p["file_path"].replace("\\", "/").split("/")[-1] if "file_path" in p else None
    if f == "file-path":
        return p.get("file_path")
    if f in ("secondary", "tertiary") and p.get("scenario") == "resource_hijacking":
        return p.get("wallet" if f == "secondary" else "mutex")
    return None


def report(mat):
    d = json.loads(mat)
    tally = {"per_file": [0, 0], "semantic": [0, 0]}
    for q in d["contract"]["questions"]:
        g = answer(mat, q["id"], "grammar")
        tally[g][1] += 1
        tally[g][0] += answer(mat, q["id"]) is not None
    return " ".join(f"{g}={a}/{n}" for g, (a, n) in tally.items())


if __name__ == "__main__":
    fx = json.load(open(sys.argv[1]))
    try:
        json.loads(fx["material"])["contract"]["questions"]
    except Exception:  # noqa: BLE001
        print(json.dumps(None))
        raise SystemExit
    out = report(fx["material"]) if fx["transform"] == "*" else answer(fx["material"], fx["transform"], fx.get("key"))
    print(json.dumps(out))
