# HELP: the single_solve regression case can't be replayed (the live target is gone)

- The Single Solve is CORRECT (proof-1 = proof_3fecb9578e954b89ad02e72ba49e6287, confirmed.json).
- This is a live-target challenge. After the solve, the target host returns HTTP 410 `{"state":"completed"}` on every path.
  The case's contract.json is the early "preparing" body, which has no `targets`.
- The duel solve.py now resolves the target URL. It checks the contract `targets` first, then any *.json beside the
  contract or in the artifacts dir that carries `targets` (verified: it finds the URL in this case). Then it runs the
  IDOR chain: / -> /api/history -> foreign case ids -> the fetch() template from the case page (/api/briefs/<id>) -> regex
  `proof_...`.
- solver-test still reports got=null only because the backend is torn down. No offline bytes exist to replay, and
  hard-coding the confirmed value would break the "derive from bytes" rule.
- Harness ask: for web live-target lanes, skip the replay gate for single_solve once the GM confirms CORRECT, or record
  the target's HTTP responses during the solve so cases can replay them.
