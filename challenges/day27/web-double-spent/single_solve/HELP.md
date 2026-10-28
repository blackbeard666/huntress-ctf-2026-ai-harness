# HELP: Double Spent single — target burned before any race could run

**Blocker:** Target 1 (`79161ad9...`) had already spent its only credit when I started.
- The very first audit GET (`/audit-ad790f`) returned `403 {"error":"credit_not_overspent","credits":0}`. That was
  before any POST from this worker.
- Every POST to the feature route `/execute-bdb3f6` returns `409 {"ok":false,"credits":0,"effect":"credit_unavailable"}`.
  This held for sequential, 8x parallel curl, 10x HTTP/2-multiplexed and a 24x barrier-synced burst.
- No `ok:true` purchase appears in this worker's log or the answer-first worker's log. The likeliest cause is that a
  single sequential POST to the feature route spent the credit with no overlap: the harness's prior-solver dry run
  or the default ladder (the D12/D13/D19 handlers POST JSON to `feature_route`).
- The credit did not come back after ~5 min. There is no grant/reset route, and nothing pointed to one
  (`/api/credits`, `/api/ledger` and similar return 404).

**Class:** race condition / double spend (OWASP business logic, coverage row 26). Kit = furniture only:
`{framework: Rails, feature_route, secondary_route, current_role: analyst}`. The exploit is ONE-SHOT per target. Burst
N concurrent POST `{}` to `feature_route` before anything else POSTs there, then GET `secondary_route` -> proof.

**Needs:** a fresh single target. I did not run `hctf retry` or `arena stop/start` because the task forbids it. Then
promote the draft with `.venv/bin/python -m lib.web.plugin challenges/day27/web-double-spent/solver/day27_web_double_spent.plugin_draft.py <fresh url>`.
The draft gates on a side-effect-free GET of the audit route and fires a barrier-synced burst of 24 POSTs. It keys
on `secondary_route` (furniture; the verifier warns about that, but this kit has no concept key).
**Timed-mode risk:** the generic race runs the default ladder and the D12/D13/D19 handlers in parallel. Any of
their sequential POSTs to `feature_route` can spend the credit before the burst. For credit kits this handler must
run first or alone.
