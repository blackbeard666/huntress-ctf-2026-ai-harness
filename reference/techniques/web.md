# web — technique log (lane-days D01-D25 released; D21 still unsolved; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Late release, catch-up pace.** No web on calendar days 1-18. Cal. 19 released D01-D03, 20 D04-D05, 21 D06-D08,
  22 D09-D10, 23 D11-D13, 24 D14-D15, 25 D16-D18, 26 D19-D20, 27 D21-D23, 28 D24-D25. GM ids are
  `web-exploitation-day-NN-<slug>` (slug = title, e.g. `...-day-24-fail-open-friday`). The folder is
  `challenges/<cal-day>/web-<title>`, so lane-day != folder day. D26-D31 = 6 left for cal. 29-31 (~2 per day).
  Each lane-day = ONE classic bug, named by a title pun: D01 backup "Back Up a Minute", D02 IDOR "Permission to
  Slip", D03 SQLi "Query Me This", D04 traversal "Stay in Your Directory", D05 function-level authz "Administratively
  Speaking", D06 reflected XSS "Reflect Upon This", D07 stored XSS "Stored for Later", D08 session fixation "Session
  Impression", D09 CSRF "Forged With Care", D10 upload "Uploading Expectations", D11 SSTI "Template Temper", D12
  2nd-order SQLi "Ask Again Later", D13 mass assignment "Posted Too Much", D14 field/action authz "The API Has
  Opinions", D15 SSRF "Fetch Quest", D16 cmd injection "Shell Company", D17 unbound reset token "Reset
  Expectations", D18 GraphQL authz "Resolver Revolt", D19 forged webhook "Trust the Webhook", D20 unsigned state
  "Serialized Offender", D21 race "Double Spent", D22 WS stream authz "Socket to Me", D23 proxy client-IP header
  "Forwarded Misgivings", **D24 fail-open on an undecodable policy "Fail Open Friday", D25 security event logged as
  something benign "If a Breach Falls in a Log"**. Arc: info-disclosure -> access control -> injection -> file read
  -> XSS -> session -> CSRF -> upload -> SSTI -> OWASP API run -> cmd injection -> auth flow -> GraphQL -> integrity
  (A08: D19-D20) -> infrastructure trust (D21-D23) -> **OWASP Top 10:2025's new categories (D24 = A10 Mishandling of
  Exceptional Conditions, D25 = A09 Logging & Alerting Failures)**. Still unseen 2025 categories: A02 Security
  Misconfiguration, A03 Software Supply Chain Failures, A04 Cryptographic Failures (JWT / weak tokens never seen),
  A07 Authentication Failures beyond D17. Expect D26-D31 to cover them.
- **No artifact: a live target.** `start` returns `result: preparing` until ready, then `targets: [{"id": "Target N",
  "url": "https://<48hex>.2026.huntress.ctf.games/"}]`. Reachable directly from the host, behind Cloudflare. After
  CORRECT every path returns `410 {"state":"completed"}`; an untimed target stops after 30 min idle.
- **Contract is fixed:** `proof-N` "Recover the proof from Target N.", artifact `Target N`, `exact_text`, `trim`.
  Answer = token `proof_<32 lowercase hex>` printed by the app. The prompt (one or two sentences) names the bug.
- **Since D05 every app is the same kit** ("A small, complete training app with one deliberately isolated security
  boundary"; framework banner = costume). `GET /api/clues` names the routes (`feature_route: /<word>-<hex6>`, often
  `secondary_route`), `current_role: analyst` (D18: `current_user`), plus usually ONE concept key (list under
  Variant axes / Clue key set). D24 added `expected_behavior`, a VALUE stating the secure behaviour to violate. No
  concept key (D11-D13, D15, D21, D25) -> the prompt and the bare-route errors route (D25's secondary self-documents
  a `report: {method, fields[]}` schema). Bare routes answer JSON errors naming the missing piece
  (`session_id_required`, `post_required` (405), `administrator_required`, `internal_only`, `absolute_url_required`,
  `fetch_failed`, `field_action_forbidden`, `path_required`, `account_id_required`, `self_service_only`,
  `webhook_rejected`, `state_required`, `role_not_permitted`, `credit_not_overspent` + `credits`, 409
  `credit_unavailable`, 426 `websocket_upgrade_required`, `loopback_only` + `evaluated_client`, D24
  `remote_policy_required` + `format_route`; a GraphQL route answers GET with 404 `not_found`).
- **The runtime config is readable.** Any file read (D16 `cat /run/huntress/*`) shows `/run/huntress/config.json`
  `{"schema":"huntress.web_exploitation.runtime_config.v1","profile_id":"framework_go_gin_command_injection",
  "weakness":"os_command_injection",...}`. It NAMES the class.
- **"Browser" checks are of two kinds.** D06/D09: no browser, judged by fetch-metadata + Referer. D07: a REAL
  moderator bot visits stored content seconds (sometimes >12 s) later. D22 checked only that an `Origin` was present.
- **Mastery = today's bug + earlier lane-days on extra targets** (2 targets D03-D07, 3 since D08, 4 since D15, **5
  on cal. 27-28**; a D04 PHP traversal target sat at slot 4 in all four cal. 27-28 runs). The prompt describes only
  today's bug, so an earlier-day solver must NOT read its parameters from the prompt. With a handler on disk, Mastery answers in 13-20 s solve.
- **A new class beats the generic seed unless the handler ships before TT.** TT `solver_incomplete` on D09, D10,
  D12, D13, D15-D18, D22, D24 (plugins landed 0-30 s after TT started). D19, D20, D23, D25 shipped in time and
  passed TT first try. D24: the answer-first worker submitted a by-hand proof at 41 s, which unlocked TT before the
  plugin existed.

## Variant axes (what differs between single, Time Trial and Mastery -- parse every value listed)
- **Target host / count**: random 48-hex host per attempt. 1 target (single, TT), 2-5 (Mastery; 5 on cal. 27-28). Rule:
  map question `artifact` "Target N" to `targets[].id` (fallback: Nth entry). Never reuse a URL across attempts.
- **Mastery composition / order**: earlier-day targets at any index; the prompt is today's only. Rule: cheap recon on
  every target (home, robots, /api/clues, /openapi.json), hinted probes first, the rest staged, targets in threads.
  Import earlier solvers' `answer()` ONLY (day-21 `fallback()`s recurse into each other).
- **Earlier-day defaults must be prompt-free (cal. 27-28, 4 of 4 Mastery runs)**: every set carried a D04 traversal
  target at slot 4 (PHP 8.3, `/` 302 -> entry page, no `/api/clues`, entry `handbook.php` | `notes.php` |
  `reader.php` (new cal. 28) with `?doc=<x>.php`). The D04 solver's `lfi()` still takes its read path from the
  prompt and falls back to `/flag.txt`, so it missed proof-4 every time (proposed fix NOT applied by cal. 28);
  hand-solved with `<entry>?doc=../../../../../run/huntress/objective.txt`. Rule: the read path ALWAYS includes
  `/run/huntress/objective.txt`. The doc param comes from any home link `?<k>=<x>.php`. Today's PHP Slim app (D25)
  HAS `/api/clues`: PHP costume alone does not mean D04.
- **Clue route words** (`/<word>-<hex6>`): feature `dispatch` | `execute` | `process` | `action` | `submit` |
  `inspect`. Secondary `callback` | `internal` | `status` | `result` | `audit` | `account` | `staff-<hex8>`. Fixed
  paths `/preferences` (D09), `/api/inventory` (D14), `/api/recovery` (D17), `/api/state-format` (D20),
  `/api/policy-format` (D24). Re-dealt within a day (D22 dispatch -> process; D24 inspect -> submit; D25
  process/status -> execute/audit). Rule: pick routes by the clue KEY's role (or a guide's `*_route` /
  `transport` value), never by the word in the value.
- **Clue key set**: one concept key (D06 `callback_nonce`, D07 `moderator_data_route`+`receipt_route_template`, D08
  `session_hint`, D09 `preferences_route`, D10 `render_route`/`preview_guide`/`upload_shape`, D14 `inventory_route`+
  `protected_reference`, D16 `input_parameter`+`example_path`, D17 `recovery_guide_route`, D18 `protected_reference`+
  `note`, D20 `state_format_route`, D24 `policy_format_route`) | VALUE keys to echo, not routes (D19 `event_type` +
  `owner_scope`; D22 `stream_reference` int, re-dealt 13777 -> 14733; D23 `deployment: trusted_reverse_proxy`; D24
  `expected_behavior` sentence) | only feature+secondary (D12, D13, D15, D21, D25) | only feature (D05, D11). Rule:
  no concept key -> prompt + bare GET of each route. A key shared by two classes (`protected_reference`: D14 / D18) -> route on the companion key, or race both.
- **Framework costume** (never changes the exploit): Django, Laravel, Node, FastAPI, Spring Boot, Sinatra, NestJS,
  Jakarta Servlet, ASP.NET Core, Gin, Symfony, GraphQL.js, Starlette, Quarkus, Rails (D21), Koa (D22), Micronaut
  (D23), ASP.NET Core Razor Pages (D24), Slim/PHP (D25); PHP+Apache for the D04 app. Rule: ignore it, except that
  Go drops a raw `;` from a query (percent-encode).
- **Request body encoding (D12, D13, D19, D20)**: POST routes accept form AND JSON but only JSON binds; D19 answers
  `[]` with a bare 500. D20 nests `{"<request_field>": base64url(JSON)}` (no `=`), named by the guide's `encoding`.
  Rule: JSON object first; when a guide names an `encoding`, build the inner blob with exactly that codec.
- **Format guides (`*_format_route`, D20, D24)**: a fixed `/api/<x>-format` JSON describes the request. D20 `{transport,
  request_field, encoding, sample_state, sample_encoded}` -> tamper the DATA. D24 `{query_parameter: policy, prefix:
  "remote:<hex12>:" (re-dealt per attempt), encoding: "base64url UTF-8 JSON", sample_decision, sample_encoded}` ->
  the valid sample returns `{"ok":true,"policy":"standard"}` (no proof); keep the prefix and make the payload
  UNDECODABLE (`%%%invalid`, `!!!`) -> fail open. Rule: read every guide field each attempt; replay the sample once,
  then mutate one thing at a time (data -> privilege ladder; format -> malformed body, wrong type, empty, truncated).
- **Self-described report schema (D25)**: secondary GET = audit log `{events:[{export_id, event}], report: {method:
  POST, fields: [export_id, missing_event, observed_event]}}`. Feature POST `{}` -> `{export_id: <24hex>, operation:
  protected_export}`, logged as `event: page_view`. Same shape in TT and Mastery (ids re-dealt). Rule: fill fields
  by name: `*_id` = id from the action response, `missing*|expected*` = the action's `operation`,
  `observed*|logged*|recorded*` = what the log shows for that id; POST JSON to the secondary.
- **Privilege value spelling**: D13 bound `role: admin`; D20 accepted ONLY `role: "administrator"` (`admin`/`staff`/
  flags -> `role_not_permitted`). Rule: ladder `administrator, admin, superuser, root, owner, staff, manager`.
- **Trusted client identity (D23)**: `loopback_only` names the rule and `evaluated_client` echoes what the app
  believed (`10.x` = the proxy hop). `X-Forwarded-For: 127.0.0.1` flipped it in single, TT and Mastery. Rule: one
  header at a time, ladder `X-Forwarded-For, X-Real-IP, Forwarded: for=, X-Client-IP, True-Client-IP, Client-IP,
  X-Original-Forwarded-For, X-Cluster-Client-IP` x `127.0.0.1, ::1, localhost`. Any header the error names goes
  first; private ranges only when it says internal/private. Watch `evaluated_client` change.
- **Transport upgrade (D22)**: feature GET -> 426 `websocket_upgrade_required`; handshake WITHOUT `Origin` -> 403, with
  any Origin -> 101; `?stream=<stream_reference>`; the FIRST text frame carries `unauthorized_event_stream` + evidence
  (same in TT/Mastery). Rule: stdlib TLS socket, `Origin: <target>`; fall back to a `{"stream":ref}` frame.
- **One-shot state (D21)**: secondary 403 `credit_not_overspent` + `credits: N`; one feature POST spends the credit
  forever (409 `credit_unavailable`). Rule: GET-only recon, ONE barrier-synced burst of ~24 POST `{}`, GET secondary.
- **Earlier classes (one line each)**: D01 robots `Disallow: /snapshots-<hex>/` | `/deploy-<hex5>/` -> `.json.bak`
  (depth 2). D02 foreign ids in `/api/history`. D03 `('%..%')` wrapper -> tautology ladder over `'` `')` `'))` `"` +
  `--`/`#`. D04 every param holding `.`/`/` x `../`*10 + objective path. D05 GET then POST every clue route. D07 board
  noun `messages` | `postcards`. D09 outside mailbox `review-NNNN@outside.example.invalid`. D10 preview URL from the
  upload response's `path`. D11 SSTI param `template`, `{{..}}` evaluated, var `objective`. D12 `x' OR '1'='1' -- ` as
  JSON in every field, re-GET secondary after EACH plant. D13 `display_name` + privilege keys. D14 single field x
  action pair. D15 `?url=http://127.0.0.1:8080<secondary>`. D16 `input_parameter` + `example_path%3Bcat
  /run/huntress/objective.txt`. D17 token for the `self_service:true` id redeemed with another id. D18 introspect,
  protected id as a STRING. D19 alias-union JSON body. D20 guide `transport`/`request_field`/`encoding`, role ladder.
- **Proof carrier**: HTML text / `<pre>` / `<article>`, JSON `support_note` | `note` | `evidence` | `rows[]` |
  `stdout`, GraphQL `data.<alias>.note`, a bot receipt, a WebSocket text frame. Rule: regex `proof_[0-9a-f]{32}` over
  every body/frame; never key on field names or on `effect`.

## Recognition cues -> first move
- `targets[]` -> `curl --max-time 20 -sS -A 'Mozilla/5.0' -i <url>` (the hook blocks curl without `--max-time`, and
  Cloudflare 403'd urllib's default UA), then `/robots.txt`, `/api/clues`, `/openapi.json`, `/sitemap.xml`.
- Read /api/clues FIRST and GET each route bare: the JSON error names the missing piece. No concept key -> the
  prompt's verb names the bug. Any `*_guide_route` / `inventory_route` is a JSON map of the next requests.
- **Before ANY POST: is the state one-shot?** "one credit", "twice", "race", "at the same time", a secondary that
  reports `credits`/`balance`/`remaining` -> GET only, then burst (D21). A sequential ladder POST burns the target.
- `Disallow:` -> D01 crawl. "Signed in as" + `/<things>/<id>` -> D02 IDOR. Search / "database" -> D03. `?doc=` +
  "stay inside" / "runbooks ... proper directory" -> D04 traversal. "staff-only door, just a sign" -> D05 GET it.
- "repeats everything", `callback_nonce` -> D06. "guestbook", `moderator_data_route` -> D07 bot; poll. `session_hint`
  -> D08 `?sid=`. "even strangers", hidden `csrf_token` -> D09 cross-site submit. `upload_shape` -> D10 `.html` with
  `{{objective}}`. "evaluates everything" -> D11 `?template={{objective}}`. "plant ... come back later" -> D12.
  "binds whatever you hand it" -> D13. `inventory_route` -> D14. `absolute_url_required` + `internal_only` -> D15.
  `input_parameter` + `example_path` -> D16. `recovery_guide_route` -> D17. `protected_reference` + `note`, GET 404
  -> D18 GraphQL. `event_type` + `owner_scope`, `webhook_rejected` -> D19 alias-union body. `state_format_route` ->
  D20 b64url state with `role: administrator`.
- "One credit ... race it", secondary 403 `credit_not_overspent` -> D21 barrier burst of POST `{}` (UNSOLVED). "upgraded
  to websockets", `stream_reference`, 426 -> D22 WS handshake + `Origin` + `?stream=<ref>`. "whatever the proxy
  whispers", `deployment: trusted_reverse_proxy`, 403 `loopback_only` -> D23 `X-Forwarded-For: 127.0.0.1`.
- "remote policy decoder ... cannot be decoded", clue `policy_format_route` + `expected_behavior`, feature 400
  `remote_policy_required` -> D24: GET the format guide, `?<query_parameter>=<prefix>%%%invalid` (keep the prefix,
  break the base64url) -> `exceptional_condition_fail_open`. A decodable sample only gives `policy: standard`.
- "nobody wrote it down ... the decisive moment the logs missed", clues only feature+secondary, feature 405
  `post_required`, secondary = `events[]` + `report{method, fields}` -> D25: POST `{}` to feature, GET the log, POST
  `{export_id, missing_event: <operation>, observed_event: <logged event>}` to the secondary.
- **Prompt words naming a SECURE behaviour** ("deny access when ... unavailable", "decisive moment ... missed") point
  at the A09/A10-style days: do the action, then show the app what it failed to do or how it failed.
- Proof regex hit = landed; an `effect` alone is NOT (D12 empty rows; D16 baseline already says completed).

## Day by day
- **D01-D20 (cal. 19-26)**: one request each once routed (see Earlier classes). Singles 36-116 s. TT
  `solver_incomplete` whenever the plugin was late (D09-D10, D12-D13, D15-D18). D19 lost ~60 s bisecting narrow
  webhook bodies; D20 needed `administrator`. A live turn chaining `ls -la; cat /run/huntress/*` was stopped by a
  safety classifier: keep injections to one plain read of the objective file.
- **D21-D23 (cal. 27)**: D21 Double Spent (race, one credit): NOT SOLVED, the credit was 0 at the first GET
  (race_bisect / dry-run POSTs spent it); draft plugin in `challenges/day27/web-double-spent/solver/`. D22 Socket to
  Me: WS handshake + `Origin` + `?stream=<ref>`, first frame `unauthorized_event_stream`, ~71 s; TT
  `solver_incomplete` (plugin 20 s late). D23 Forwarded Misgivings: `X-Forwarded-For: 127.0.0.1` past
  `loopback_only`, ~64 s, TT 10.5 s first try. Both Mastery 4/5: proof-4 a D04 PHP target, hand-solved.
- **D24 Fail Open Friday (cal. 28)**: fail-open access decision on an exceptional condition (OWASP 2025 A10).
  Clues `{framework: ASP.NET Core Razor Pages, feature_route: /inspect-<hex6>, policy_format_route, current_role,
  expected_behavior}`; bare feature -> `remote_policy_required`. Guide (see Variant axes) -> `curl -G <feature>
  --data-urlencode 'policy=<prefix>%%%invalid'` -> `exceptional_condition_fail_open` + evidence (the valid sample only
  gives `policy: standard`). Re-runnable. Single CORRECT 41 s from start (answer-first worker, by hand). Plugin
  `day28_web_fail_open_friday` (KEY `^policy_format_route$`, bad-suffix ladder `!!!`, `%%%`, `@@@@`, `eyJ`, `e30`,
  empty) landed AFTER TT began -> **TT `solver_incomplete`**; live worker CORRECT ~42 s after TT start. Mastery 4/5
  (proof-4 = D04 `reader.php`, hand-solved; CORRECT ~2:40 after start).
- **D25 If a Breach Falls in a Log (cal. 28)**: security logging failure (OWASP 2025 A09). Clues `{framework: Slim,
  feature_route: /process-<hex6>, secondary_route: /status-<hex6>, current_role}`. Feature 405 `post_required`; POST
  `{}` -> `export_id` + `operation: protected_export`; the secondary's audit log shows that id as `page_view` and
  advertises `report.fields`. POST `{export_id, missing_event: "protected_export", observed_event: "page_view"}` to
  the secondary -> `decisive_security_event_missing` + evidence. Re-runnable. Single CORRECT ~86 s from start, plugin
  `day28_web_if_a_breach_falls_in_a_log` (KEY `^secondary_route$`, gated on a `missing*` report field) promoted
  BEFORE submit -> TT first try (solve 5 s). Mastery 4/5 (proof-4 = D04 `notes.php`, hand-solved; CORRECT ~2:04).

## GM answer conventions learned
- Answer = bare `proof_<32 lowercase hex>` (the CORRECT body's `flag` is a different value; never submit it). `trim`.
  Ids `proof-1`..`proof-N` in target order. Batch all Mastery proofs in one submit; partial = `accepted`+`remaining`
  (cal. 27-28: all four Mastery runs submitted 4, `remaining: 1`, then proof-4 alone -> CORRECT).
- `effect` spellings confirmed: `framework_authorization_bypassed` (D05), `isolated_browser_callback` (D06),
  `fixed_session_privilege_transfer` (D08), `delayed_query_revealed_private_row` (D12), `bound_privileged_property`
  (D13), `api_field_action_authorization_bypassed` (D14), `internal_service_reached` (D15),
  `worker_command_completed` (D16, also on the harmless baseline), `synthetic_account_recovery` (D17),
  `forged_event_consumed` (D19), `serialized_role_trusted` (D20), `unauthorized_event_stream` (D22),
  `proxy_trust_admin_bypass` (D23), `exceptional_condition_fail_open` (D24), `decisive_security_event_missing`
  (D25). Failure spelling `credit_unavailable` (D21). D18: none (plain GraphQL `data`).
- `already_solved` after CORRECT is harmless; a 503 `temporarily_unavailable` on submit may still have landed.
- TT/Mastery are "regular scored challenges by default"; `run_for_time:true` asks for a timed Hall-of-Fame attempt
  (`last_timed.json`: `no_clock:true`). The transport line varies per contract; `hctf` owns it.

## Pitfalls that cost time
- **Burning a one-shot target (D21, unsolved).** A single sequential POST to the sink spends the only credit. Dry
  runs, race_bisect, default ladders and earlier-day handlers that POST to `feature_route` must NOT run before the
  race handler. Recon on a credit/balance kit is GET-only; the burst is the first POST.
- **Earlier-day solvers keyed on the prompt** miss Mastery targets: the D04 solver missed proof-4 in ALL FOUR
  cal. 27-28 Mastery runs (fallback `/flag.txt`). When you see a PHP `?doc=` entry page with no `/api/clues`, read
  `/run/huntress/objective.txt` by hand at once (`../`*5-10); don't wait for the solver's ~60 s budget.
- Shipping a new class without its handler: TT `solver_incomplete` on D09-D10, D12-D13, D15-D18, D22, D24. Write
  `lib/web/handlers/dayNN_*.py` (KEY_MAP on a concept KEY + HANDLERS) BEFORE the single submit (D11, D19, D20, D23,
  D25 did). A 20 s delay is enough to lose the TT, and a by-hand submit from a parallel worker (D24) unlocks TT
  just as early.
- Missing `Origin` on a WebSocket handshake = 403 (D22): send one. No websocket package in the venv; use stdlib.
- Bisecting a generic rejection one field at a time (D19 ~60 s lost): send ONE alias-union body first.
- Stopping at `role: admin` (D20 wanted `administrator`): `role_not_permitted` = right field, keep laddering.
- Treating `effect` as success (D12 empty rows; D16 baseline). Success = proof regex. A valid guide sample (D24
  `policy: standard`) is the baseline, not the exploit.
- Raw `;` in a Go query string is dropped -> `%3B`. GraphQL 404 on GET -> POST. Form bodies on JSON APIs are ignored
  (D12); JSON arrays 500 (D19). JSON object first.
- Trusting the echo (D13) or the stated policy ("txt only", "self-service only"). SSRF `fetch_failed` = wrong port
  (D15: 8080). D14 lists/`*` forbidden. A 500 on `{{unknown}}` (D11) = undefined variable.
- Choosing routes by the WORD in a clue value or by prompt keywords in Mastery. One-level crawls (D01). Solvers
  importing each other's `fallback()`. Hammering one target with every probe in parallel.
- Polling a bot receipt for a fixed 12 s (D07's bot sometimes comes later). Live cases can't be replayed after
  CORRECT (410): save target responses during the solve; never hard-code proofs.
- `curl` without `--max-time` is blocked by the hook (and `sleep` by no_block.py); urllib's default UA can draw a
  Cloudflare 403.

## reviewer cross-check (measured on a parallel agent; folded into the drivers)
- D03 oracle trap: `q` sits in an EVEN number of `LIKE '%q%'` clauses, so `' OR '1'='1` and `'1'='2` BOTH return all
  rows; oracle = `nope' OR (<cond>) OR '1'='2`. D04: depth 1-2 `../` silently returns the normal page; use >= 3.
  `control_unavailable` on `op=start` is TRANSIENT (26.7 s hang); back off and re-send.
