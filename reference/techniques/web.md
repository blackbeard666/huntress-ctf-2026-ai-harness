# web — technique log (lane-days D01-D23 released; D21 still unsolved; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Late release, catch-up pace.** No web on calendar days 1-18. Cal. 19 released D01-D03, 20 D04-D05, 21 D06-D08,
  22 D09-D10, 23 D11-D13, 24 D14-D15, 25 D16-D18, 26 D19-D20, 27 D21-D23. GM ids are `web-exploitation-day-NN-<slug>`.
  The slug is usually the title (D07 "Stored for Later" = `...-day-07-stored-xss`). The folder is
  `challenges/<cal-day>/web-<title>`, so lane-day != folder day. D24-D31 = 8 left for cal. 28-31 (~2 per day).
  Each lane-day = ONE classic bug, named by a title pun: D01 backup exposure "Back Up a Minute", D02 IDOR
  "Permission to Slip", D03 SQLi "Query Me This", D04 path traversal "Stay in Your Directory", D05 missing
  function-level authz "Administratively Speaking", D06 reflected XSS "Reflect Upon This", D07 stored XSS "Stored for
  Later", D08 session fixation "Session Impression", D09 CSRF "Forged With Care", D10 unrestricted upload "Uploading
  Expectations", D11 SSTI "Template Temper", D12 second-order SQLi "Ask Again Later", D13 mass assignment "Posted Too
  Much", D14 per-field/action API authz "The API Has Opinions", D15 SSRF "Fetch Quest", D16 OS command injection
  "Shell Company", D17 reset token not bound to the account "Reset Expectations", D18 GraphQL resolver without
  field-level authz "Resolver Revolt", D19 unauthenticated webhook "Trust the Webhook", D20 unsigned client-side
  state "Serialized Offender", **D21 race / double spend "Double Spent", D22 WebSocket event stream without authz
  "Socket to Me", D23 trusted reverse-proxy client-IP header "Forwarded Misgivings"**. Arc: info-disclosure -> access
  control -> injection -> file read -> XSS x2 -> session -> CSRF -> upload -> SSTI -> 2nd-order SQLi -> OWASP API run
  -> cmd injection -> auth flow -> GraphQL -> integrity (A08: D19-D20) -> **infrastructure / protocol trust (D21
  timing, D22 upgraded transport, D23 proxy headers)**. Sequels are common (D10->D11, D03->D12, D05->D13->D14,
  D14->D18). Signed-but-weak tokens (JWT, signed cookies) are STILL unseen. D23's proxy theme points at Host-header /
  cache poisoning and CORS. D22 points at other transports (SSE, socket.io, JSON-RPC).
- **No artifact: a live target.** `start` returns `result: preparing` until ready, then `targets: [{"id": "Target N",
  "url": "https://<48hex>.2026.huntress.ctf.games/"}]`. Reachable directly from the host, behind Cloudflare. After
  CORRECT every path returns `410 {"state":"completed"}`; an untimed target stops after 30 min idle.
- **Contract is fixed:** `proof-N` "Recover the proof from Target N.", artifact `Target N`, `exact_text`, `trim`.
  Answer = token `proof_<32 lowercase hex>` printed by the app. The prompt (one or two sentences) names the bug.
- **Since D05 every app is the same kit** ("A small, complete training app with one deliberately isolated security
  boundary"; framework banner = costume). `GET /api/clues` names the routes (`feature_route: /<word>-<hex6>`, often
  `secondary_route`), `current_role: analyst` (D18: `current_user`), plus usually ONE concept key (`session_hint`,
  `callback_nonce`, `moderator_data_route`+`receipt_route_template`, `preferences_route`, `render_route`+
  `preview_guide`+`upload_policy`+`upload_shape`, D14 `inventory_route`+`protected_reference`, D16 `input_parameter`+
  `example_path`, D17 `recovery_guide_route`, D18 `protected_reference`+`note`, D19 `event_type`+`owner_scope` (body
  VALUES), D20 `state_format_route`, D22 `stream_reference: <int>` (a VALUE), D23 `deployment:
  "trusted_reverse_proxy"` (a VALUE naming the trust model)). D11-D13, D15, D21 had NO concept key: the prompt and the
  bare-route errors are the routing signal. Bare routes answer JSON errors naming the missing piece
  (`session_id_required`, `post_required` (405), `administrator_required` (403), `internal_only`,
  `absolute_url_required`, `fetch_failed`, `field_action_forbidden`, `path_required`, `account_id_required`,
  `self_service_only`, `webhook_rejected`, `state_required`, `role_not_permitted`, D21 secondary 403
  `credit_not_overspent` + `credits`, D21 feature POST 409 `credit_unavailable`, D22 426 `websocket_upgrade_required`,
  D23 403 `loopback_only` + `evaluated_client: "10.x"`; a GraphQL route answers GET with 404 `not_found`).
- **The runtime config is readable.** Any file read (D16 `cat /run/huntress/*`) shows `/run/huntress/config.json`
  `{"schema":"huntress.web_exploitation.runtime_config.v1","profile_id":"framework_go_gin_command_injection",
  "weakness":"os_command_injection",...}`. It NAMES the class.
- **"Browser" checks are of two kinds.** D06/D09: no browser, judged by fetch-metadata + Referer. D07: a REAL
  moderator bot visits stored content seconds (sometimes >12 s) later. D22 checked only that an `Origin` was present.
- **Mastery = today's bug + earlier lane-days on extra targets** (2 targets D03-D07, 3 since D08, 4 since D15, **5
  on cal. 27**). The prompt describes only today's bug, so an earlier-day solver must NOT read its parameters from
  the prompt. With a handler on disk, Mastery answers in 13-20 s solve.
- **A new class beats the generic seed unless the handler ships before TT.** TT `solver_incomplete` on D09, D10,
  D12, D13, D15-D18, D22 (plugins landed 0-20 s after TT started). D19, D20, D23 shipped in time and passed TT
  first try.

## Variant axes (what differs between single, Time Trial and Mastery -- parse every value listed)
- **Target host / count**: random 48-hex host per attempt. 1 target (single, TT), 2-5 (Mastery; 5 on cal. 27). Rule:
  map question `artifact` "Target N" to `targets[].id` (fallback: Nth entry). Never reuse a URL across attempts.
- **Mastery composition / order**: earlier-day targets at any index; the prompt is today's only. Rule: cheap recon on
  every target (home, robots, /api/clues, /openapi.json), hinted probes first, the rest staged, targets in threads.
  Import earlier solvers' `answer()` ONLY (day-21 `fallback()`s recurse into each other).
- **Earlier-day defaults must be prompt-free (cal. 27)**: both Mastery sets carried a D04 traversal target (PHP +
  Apache, no `/api/clues`, entry `handbook.php?doc=<x>.php` | `notes.php?doc=..`). The D04 solver took its read path
  from the prompt; today's prompt has none, so it fell back to `/flag.txt` and missed proof-4 twice. Rule: the
  read path defaults to `/run/huntress/objective.txt` (plus any prompt path). The doc param comes from any home
  link `?<k>=<x>.php`.
- **Clue route words** (`/<word>-<hex6>`): feature `dispatch` | `execute` | `process` | `action` | `submit` |
  `inspect`. Secondary `callback` | `internal` | `status` | `result` | `audit` | `account` | `staff-<hex8>`. Fixed
  paths `/preferences` (D09), `/api/inventory` (D14), `/api/recovery` (D17), `/api/state-format` (D20). Re-dealt
  within a day (D22 dispatch -> process). Rule: pick routes by the clue KEY's role (or a guide's `*_route` /
  `transport` value), never by the word in the value.
- **Clue key set**: one concept key (D06-D10, D14, D16-D20) | VALUE keys to echo, not routes (D19 `event_type` +
  `owner_scope`; D22 `stream_reference` int, re-dealt 13777 -> 14733; D23 `deployment: trusted_reverse_proxy`) | only
  feature+secondary (D12, D13, D15, D21) | only feature (D05, D11). Rule: no concept key -> prompt + bare GET of each
  route. A key shared by two classes (`protected_reference`: D14 / D18) -> route on the companion key, or race both.
- **Framework costume** (never changes the exploit): Django, Laravel, Node, FastAPI, Spring Boot, Sinatra, NestJS,
  Jakarta Servlet, ASP.NET Core, Gin, Symfony, GraphQL.js, Starlette, Quarkus, Rails (D21), Koa (D22), Micronaut
  (D23); PHP+Apache for the D04 app. Rule: ignore it, except that Go drops a raw `;` from a query (percent-encode).
- **Request body encoding (D12, D13, D19, D20)**: POST routes accept form AND JSON but only JSON binds; D19 answers
  `[]` with a bare 500. D20 nests `{"<request_field>": base64url(JSON)}` (no `=`), named by the guide's `encoding`.
  Rule: JSON object first; when a guide names an `encoding`, build the inner blob with exactly that codec.
- **Privilege value spelling**: D13 bound `role: admin`; D20 accepted ONLY `role: "administrator"` (`admin`/`staff`/
  flags -> `role_not_permitted`). Rule: ladder `administrator, admin, superuser, root, owner, staff, manager`.
- **Trusted client identity (D23)**: `loopback_only` names the rule and `evaluated_client` echoes what the app
  believed (`10.x` = the proxy hop). `X-Forwarded-For: 127.0.0.1` flipped it in single, TT and Mastery. Rule: one
  header at a time, ladder `X-Forwarded-For, X-Real-IP, Forwarded: for=, X-Client-IP, True-Client-IP, Client-IP,
  X-Original-Forwarded-For, X-Cluster-Client-IP` x `127.0.0.1, ::1, localhost`. Any header the error names goes
  first; private ranges only when it says internal/private. Watch `evaluated_client` change.
- **Transport upgrade (D22)**: feature GET -> 426 `websocket_upgrade_required`. The handshake WITHOUT `Origin` -> 403;
  with an Origin (own host or foreign) -> 101. The stream is selected by `?stream=<stream_reference>` and the FIRST
  server text frame carries `{"ok":true,"effect":"unauthorized_event_stream","evidence":"proof_.."}`. Same shape in
  TT and Mastery. Rule: raw stdlib TLS socket (no websocket lib in the venv), `Origin: <target origin>`, query
  `stream=<ref>`; fall back to a `{"stream":ref}` / `{"subscribe":ref}` text frame.
- **One-shot state (D21)**: secondary (`audit-<hex6>`) = 403 `credit_not_overspent` + `credits: N`; feature POST spends
  the single credit (`credits: 0`, then 409 `credit_unavailable` forever, no reset route). Rule: GET-only recon,
  then ONE barrier-synced burst of ~24 concurrent POSTs `{}` to `feature_route` before anything else POSTs, then GET
  the secondary.
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
- "One credit, two purchases ... race it", clues only feature+secondary (`/execute-..`, `/audit-..`), secondary 403
  `credit_not_overspent` -> D21: N concurrent POST `{}` released on a barrier (threads or HTTP/2 multiplexing), then
  GET secondary. UNSOLVED so far: the only target was already at `credits: 0`.
- "upgraded to websockets ... event stream that was never meant for you", clue `stream_reference`, 426
  `websocket_upgrade_required` -> D22: WS handshake to `feature_route?stream=<ref>` WITH an `Origin` header; read
  frames for the proof.
- "believes whatever the proxy whispers ... right header ... protected path", clue `deployment:
  trusted_reverse_proxy`, 403 `loopback_only` + `evaluated_client` -> D23: `curl -H 'X-Forwarded-For: 127.0.0.1'
  <feature>` -> `proxy_trust_admin_bypass` + `evidence`.
- Proof regex hit = landed; an `effect` alone is NOT (D12 empty rows; D16 baseline already says completed).

## Day by day
- **D01-D15 (cal. 19-24)**: D01 robots -> index -> `.json.bak`. D02 `/api/history` foreign id. D03 `?q=zz') OR 1=1
  --`. D04 `?doc=../`*6+path. D05 GET the feature route. D06 reflect `fetch(cb?nonce)`, GET cb same-origin. D07 stored
  script for the bot. D08 `?sid=<hint>`. D09 cross-site submit. D10 `.html` upload. D11 `?template={{objective}}`.
  D12 JSON plant, GET secondary. D13 JSON privilege keys. D14 single field x action. D15 `?url=http://127.0.0.1:8080
  <secondary>`. Singles 47-116 s (D08 Mastery ~15 min: every solver on every target).
- **D16-D20 (cal. 25-26)**: D16 Shell Company (Gin, `%3B`-encoded `cat`) ~40 s. D17 Reset Expectations (own token
  redeemed with the executive id) ~39 s. D18 Resolver Revolt (POST introspection) ~36 s. D16-D18 TT all
  `solver_incomplete` (plugins late). D19 Trust the Webhook: ~30 narrow bodies -> `webhook_rejected`, one alias-union
  body -> `forged_event_consumed`, ~95 s; TT/Mastery first try. D20 Serialized Offender: guide -> b64url state,
  `administrator` only, ~50 s after ready; TT 15 s, Mastery 4/4. A live turn chaining `ls -la; cat /run/huntress/*`
  was stopped by a safety classifier: keep an injection to one plain read of the objective file.
- **D21 Double Spent (cal. 27)**: race condition / double spend (business logic, A04). Clues `{framework: Rails,
  feature_route: /execute-<hex6>, secondary_route: /audit-<hex6>, current_role}`. Secondary 403 `{"error":
  "credit_not_overspent","credits":0}`. Feature POST 409 `{"ok":false,"credits":0,"effect":"credit_unavailable"}`
  under sequential, 8x curl, 10x HTTP/2 and a 24x barrier burst. **NOT SOLVED.** The credit was already 0 at the
  workers' first GET and never came back (~5 min). The likely cause is the harness's race_bisect / prior-solver dry
  run, which ran 16 s on the fresh target and sent default-ladder POSTs to `feature_route`. TT/Mastery were not
  started. A plugin draft (GET gate + 24-POST barrier burst) is in `solver/`; HELP.md is in single_solve/. Success
  `effect` spelling still unknown.
- **D22 Socket to Me (cal. 27)**: WebSocket event stream without per-subscriber authz (CSWSH-flavoured). Clues
  `{framework: Koa, feature_route: /dispatch-<hex6>, current_role, stream_reference: 13777}`. GET -> 426. Handshake +
  `Origin` + `?stream=<ref>` -> first frame `unauthorized_event_stream` + `evidence`. Stdlib client: `socket` +
  `ssl` + `Sec-WebSocket-Key` handshake, read until the proof regex hits. Single CORRECT ~71 s from start. **TT
  `solver_incomplete`**: the handler landed 20 s after TT solve began. The live worker wrote a raw WS client, CORRECT
  ~40 s after ready. Mastery 4/5 in 18.5 s; proof-4 was a D04 `notes.php?doc=` target, solved by hand.
- **D23 Forwarded Misgivings (cal. 27)**: app trusts a client-supplied proxy header (`X-Forwarded-For` spoofing).
  Clues `{framework: Micronaut, feature_route: /action-<hex6>, current_role, deployment: "trusted_reverse_proxy"}`.
  GET feature -> 403 `{"error":"loopback_only","evaluated_client":"10.x"}`. Same GET with `X-Forwarded-For:
  127.0.0.1` -> `{"ok":true,"effect":"proxy_trust_admin_bypass","evaluated_client":"127.0.0.1","evidence":..}`.
  Re-runnable. Single CORRECT ~64 s from start (handler promoted before TT). TT 10.5 s (solve 2 s), first try.
  Mastery 4/5 in 20 s; proof-4 was a D04 `handbook.php?doc=../`*10`run/huntress/objective.txt` target (proof in
  `<article>`), solved by hand ~80 s after start.

## GM answer conventions learned
- Answer = bare `proof_<32 lowercase hex>` (the CORRECT body's `flag` is a different value; never submit it). `trim`.
  Ids `proof-1`..`proof-N` in target order. Batch all Mastery proofs in one submit; partial = `accepted`+`remaining`
  (cal. 27: both Mastery runs submitted 4, `remaining: 1`, then proof-4 alone -> CORRECT).
- `effect` spellings confirmed: `framework_authorization_bypassed` (D05), `isolated_browser_callback` (D06),
  `fixed_session_privilege_transfer` (D08), `delayed_query_revealed_private_row` (D12), `bound_privileged_property`
  (D13), `api_field_action_authorization_bypassed` (D14), `internal_service_reached` (D15),
  `worker_command_completed` (D16, also on the harmless baseline), `synthetic_account_recovery` (D17),
  `forged_event_consumed` (D19), `serialized_role_trusted` (D20), `unauthorized_event_stream` (D22),
  `proxy_trust_admin_bypass` (D23). Failure spelling `credit_unavailable` (D21). D18: none (plain GraphQL `data`).
- `already_solved` after CORRECT is harmless; a 503 `temporarily_unavailable` on submit may still have landed.
- TT/Mastery are "regular scored challenges by default"; `run_for_time:true` asks for a timed Hall-of-Fame attempt
  (`last_timed.json`: `no_clock:true`). The transport line varies per contract; `hctf` owns it.

## Pitfalls that cost time
- **Burning a one-shot target (D21, unsolved).** A single sequential POST to the sink spends the only credit. Dry
  runs, race_bisect, default ladders and earlier-day handlers that POST to `feature_route` must NOT run before the
  race handler. Recon on a credit/balance kit is GET-only; the burst is the first POST.
- **Earlier-day solvers keyed on the prompt** miss Mastery targets (D04 twice on cal. 27). Today's prompt describes
  only today's bug, so hard-code each class's known defaults (`/run/huntress/objective.txt`).
- Shipping a new class without its handler: TT `solver_incomplete` on D09-D10, D12-D13, D15-D18, D22. Write
  `lib/web/handlers/dayNN_*.py` (KEY_MAP on a concept KEY + HANDLERS) BEFORE the single submit (D11, D19, D20, D23
  did). A 20 s delay is enough to lose the TT.
- Missing `Origin` on a WebSocket handshake = 403 (D22): send one. No websocket package in the venv; use stdlib.
- Bisecting a generic rejection one field at a time (D19 ~60 s lost): send ONE alias-union body first.
- Stopping at `role: admin` (D20 wanted `administrator`): `role_not_permitted` = right field, keep laddering.
- Treating `effect` as success (D12 empty rows; D16 baseline). Success = proof regex.
- Raw `;` in a Go query string is dropped -> `%3B`. GraphQL 404 on GET -> POST. Form bodies on JSON APIs are ignored
  (D12); JSON arrays 500 (D19). JSON object first.
- Trusting the echo (D13) or the stated policy ("txt only", "self-service only"). SSRF `fetch_failed` = wrong port
  (D15: 8080). D14 lists/`*` forbidden. A 500 on `{{unknown}}` (D11) = undefined variable.
- Choosing routes by the WORD in a clue value or by prompt keywords in Mastery. One-level crawls (D01). Solvers
  importing each other's `fallback()`. Hammering one target with every probe in parallel.
- Polling a bot receipt for a fixed 12 s (the D07 moderator sometimes comes later).
- Live cases can't be replayed after CORRECT (410). Save target responses during the solve; never hard-code proofs.
- `curl` without `--max-time` is blocked by the hook (and `sleep` by no_block.py); urllib's default UA can draw a
  Cloudflare 403.

## reviewer cross-check (measured on a parallel agent; folded into the drivers)
- **Blind SQLi oracle trap (D03).** `q` sits in an EVEN number of `col LIKE '%q%'` clauses, so `' OR '1'='1` and
  `' OR '1'='2` BOTH return all rows. Oracle = quote balance: `nope' OR (<cond>) OR '1'='2`; calibrate on `1=1`/`1=2`.
- **LFI.** The `?doc=` viewer silently returns the NORMAL page for depth 1-2; use >= 3 `../` into the objective path.
- **`control_unavailable` is TRANSIENT** (a 26.7 s hang on `op=start`; resend succeeded). Back off and re-send.
