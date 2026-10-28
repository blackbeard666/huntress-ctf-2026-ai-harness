## Web lane: what to extend
(For this lane the generic rules above on "bytes in, value out, < 1 s" and on fixture generators/oracle tools
read as below: a handler talks to a live kit through `lib.websolve.fetch`, and fixtures are recorded kits.)
Every web challenge is a LIVE target of one kit: `GET /api/clues` returns {framework, feature_route, often
secondary_route, current_role} plus zero or one CONCEPT key naming the vuln class, and the answer is the token
`proof_<hex>` the app prints once the bug is exploited (read from `/run/huntress/objective.txt` server-side). The
generic solver (`lib/web/__init__.py`) dispatches on the clue KEYS (never their values) to the handlers in
`lib/web/handlers/` -- per-day plugins `dayNN_web_*.py` and, from you, generic class handlers in
`lib/web/handlers/prebuilt/` -- and races them with `default` and every earlier day's solver. Mastery mixes earlier
classes onto fresh targets, and a new class costs a ~40 s hand exploit per target unless a handler already knows it.
The coverage atlas (`reference/coverage/web.md`) lists the classes not seen yet; your target names one.

Write ONE module `lib/web/handlers/prebuilt/prebuilt_<target id with _>.py`:
```python
KEY_MAP = [(r"<regex on a CONCEPT /api/clues key of this class>", "prebuilt_<id>")]
HANDLERS = {"prebuilt_<id>": exploit}           # exploit(base, clues) -> "proof_..." or None
KEY_COMPANIONS = {}                             # optional {pattern: sibling-key regex}: the pattern only counts beside it
RUN_ALONE = False                               # True if ONE-SHOT (a credit/action a raced probe would spend): race it alone
```
- `exploit` re-runs the WHOLE class end to end against `base` with the clues dict: recon what is per-target (the clue
  routes, the bare routes' JSON errors -- `<name>_required`, `post_required` 405 ... --, a guide/inventory JSON the
  clues point to), then a SHORT ordered ladder of payloads for the class, then read the proof (`websolve.proof(body)`).
  Return None the moment the target is clearly not this class. <= ~25 requests, each through `lib.websolve.fetch`
  (browser UA, <= 6 s timeouts, honours the solve deadline) -- the only network I/O allowed (no urllib.request,
  socket, subprocess, threads). Never scan, fuzz or brute force; derive every value from what the app shows.
- KEY_MAP keys on the class's CONCEPT keys only. Never on kit furniture (`framework`, `feature_route`,
  `secondary_route`, `current_role`, `routes`, `role`, `username`, `user`, `message`): a furniture match races your
  handler on EVERY target (the gate rejects it). A key that means your class only next to a sibling -> KEY_COMPANIONS
  (D25: `protected_reference` alone is not Day 14's class; it only counts with `inventory_route`).
- Never edit `lib/web/handlers/__init__.py`, `lib/web/__init__.py`, `lib/websolve.py`, the per-day plugins or any
  solver; never change what an existing handler returns.

Fixtures = RECORDED KITS replayed by a local mock (no live target exists off-peak; the targets of past days answer 410).
2+ per module in `tests/data/web_fixtures/<id>-<variant>.json`, the format in `tests/test_web_fixtures.py`'s docstring:
{"handler", "expected": "proof_<hex>" | null, "decoy", "source", "oracle", "routes": [declarative rules: method, path,
query/form/json regexes -> status + JSON/text response]}. Take the kit shape (clue keys, routes, error bodies, response
fields) from real evidence -- `reference/coverage/web.md` (recognition cues + rows), the per-day plugins' docstrings,
`challenges/day*/web-*/solver/` NOTES/solve.py, `.run/web_race.jsonl` clue key sets -- and say which in `source`.
`expected` is the proof planted on the rule only the exploit path reaches; `oracle` says why that request shape is the
bug (the GM accepted it on Dnn / the atlas row's first move). At least one variant beyond the plain form (a sequel the
atlas names: filter, other param, POST-only) and at least one DECOY (same kit, bug patched or a near-miss class:
expected null, `"decoy": true`) -- your handler must return no proof there. NEVER contact a live target, a
`*.huntress.ctf.games` host or the Game Master: the gate runs offline and fails on any non-local request.

## Gate commands
`python3 tests/test_web_fixtures.py` (every web fixture on its mock, every handler module imports, the prebuilt module
structure rules above). Run it ONCE before you stop.
