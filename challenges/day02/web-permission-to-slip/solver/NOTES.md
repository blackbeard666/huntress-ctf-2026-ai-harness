# D2 web IDOR (Permission to Slip)
- Live target: GM status returns `targets:[{id:"Target 1",url}]` after ~2 min of `result: preparing`; harness saves it as artifacts/c_targets.json (contract.json lacks it). Target returns 410 `{"state":"completed"}` once solved.
- App: home "Signed in as X" + /briefs/<id> links; brief page fetch("/api/briefs/<id>"); /api/history leaks a foreign case_id (owner executive, visibility reference_only); GET /api/briefs/<foreign> -> note `proof_<32hex>` (CORRECT).
- solve.py: derives the API template from the brief page's fetch(), foreign ids from feed JSON, regex `proof[_-]...`; stdlib urllib + cookie jar.

## Proposed lib additions
- reference/techniques/web.md: live-target days -> targets come in status body `targets[]` (+ `routes[]`), not in contract.json; proof format `proof_<32 hex>`.
