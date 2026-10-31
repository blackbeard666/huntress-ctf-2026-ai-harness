# web — technique log (lane-days D01-D29 released; D21 still unsolved; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Late release, catch-up pace.** No web on calendar days 1-18. Cal. 19 released D01-D03, 20 D04-D05, 21 D06-D08,
  22 D09-D10, 23 D11-D13, 24 D14-D15, 25 D16-D18, 26 D19-D20, 27 D21-D23, 28 D24-D25, **29 D26-D27, 30 D28-D29**.
  GM ids are `web-exploitation-day-NN-<slug>` (slug = title). The folder is `challenges/<cal-day>/web-<title>`, so
  lane-day != folder day (handlers are named by CAL day: `day30_web_queue_the_confusion` = lane D29). **D30-D31 =
  the last 2 lane-days, expected cal. 31.**
  Each lane-day = ONE classic bug, named by a title pun: D01 backup, D02 IDOR, D03 SQLi, D04 traversal, D05
  function-level authz, D06 reflected XSS, D07 stored XSS, D08 session fixation, D09 CSRF, D10 upload, D11 SSTI,
  D12 2nd-order SQLi, D13 mass assignment, D14 field/action authz, D15 SSRF, D16 cmd injection, D17 unbound reset
  token, D18 GraphQL authz, D19 forged webhook, D20 unsigned state, D21 race, D22 WS stream authz, D23 proxy client-IP
  header, D24 fail-open (A10:2025), D25 logging failure (A09:2025), **D26 unverified update artifact "Trust the
  Build" (A03:2025 supply chain), D27 SSRF chained into IDOR "Internal Affairs", D28 trusted delegated-identity header
  "Pass the Identity", D29 queued job owner binding "Queue the Confusion"**.
  Arc: info-disclosure -> access control -> injection -> XSS -> session/CSRF -> upload/SSTI -> OWASP API run -> cmd
  injection -> auth flow -> GraphQL -> integrity (D19-D20) -> infrastructure trust (D21-D23) -> OWASP 2025 newcomers
  (D24 A10, D25 A09, D26 A03) -> **SERVICE BOUNDARIES (D27-D29: "two service boundaries", "delegated service
  boundary", a job queue between services; trust passed between internal services, not between browser and app)**.
  D27 was the first CHAINED day (two bugs, one proof). Still unseen: A02 misconfiguration, A04 crypto (JWT / weak
  tokens never seen), service-to-service tokens, tenant isolation, gateway/backend parse differentials.
- **No artifact: a live target.** `start` returns `result: preparing` until ready, then `targets: [{"id": "Target N",
  "url": "https://<48hex>.2026.huntress.ctf.games/"}]`. Reachable directly, behind Cloudflare. After CORRECT every
  path returns `410 {"state":"completed"}` (`/api/clues` = `{state}` only); an untimed target stops after 30 min idle.
- **Contract is fixed:** `proof-N` "Recover the proof from Target N.", artifact `Target N`, `exact_text`, `trim`.
  Answer = token `proof_<32 lowercase hex>` printed by the app. The prompt (one or two sentences) names the bug.
- **Since D05 every app is the same kit.** `GET /api/clues` names the routes (`feature_route: /<word>-<hex6>`, often
  `secondary_route`), `current_role: analyst` (D18: `current_user`), plus usually ONE concept key (see Variant axes).
  Since D26 the concept keys are fixed `/api/<noun>` GUIDES (`update_feed`/`update_policy`, `topology_route`/
  `case_directory_route`, `identity_directory_route`, `owner_directory_route`) whose JSON hands you the victim /
  internal URL / restricted value. Bare routes answer JSON errors naming the missing piece, now often WITH the field
  name (`target_required` + `query_parameter: target`, `post_required` + `request_fields: [owner]`,
  `job_id_required` + `query_parameter: id`) or a header in `Vary` (D28 `Vary: x-delegated-user`).
- **The runtime config is readable.** Any file read shows `/run/huntress/config.json` (`weakness` names the class).
- **Mastery = today's bug + earlier lane-days** (5 targets cal. 27-30, **6 on D29**). The prompt describes only
  today's bug. With handlers on disk Mastery is 11-28 s total; all four cal. 29-30 Mastery runs were 5/5 or 6/6
  first try (the D04 solver was made prompt-free in the cal. 28 post-mortem).
- **Handler before TT = TT first try.** D26-D29 all promoted their plugin before (or right at) the single submit ->
  TT 9-20 s, first try. Late plugins (D09-D10, D12-D13, D15-D18, D22, D24) cost the TT.

## Variant axes (what differs between single, Time Trial and Mastery -- parse every value listed)
- **Target host / count**: random 48-hex host per attempt. 1 target (single, TT), 2-6 (Mastery; 6 on D29). Rule: map
  question `artifact` "Target N" to `targets[].id` (fallback: Nth entry). Never reuse a URL across attempts.
- **Mastery composition / order**: earlier-day targets at any index; the prompt is today's only. Rule: cheap recon on
  every target, hinted probes first, targets in threads; earlier solvers' `answer()` ONLY, never their `fallback()`.
  Earlier-day defaults must be prompt-free: the D04 PHP target (`handbook.php` | `notes.php` | `reader.php`
  `?doc=<x>.php`, no `/api/clues`) always gets `../`*5-10 + `run/huntress/objective.txt`.
- **Clue route words** (`/<word>-<hex6>`): feature `dispatch` | `execute` | `process` | `action` | `submit` |
  `inspect`; secondary `callback` | `internal` | `status` | `result` | `audit` | `account` | `staff-<hex8>`. Re-dealt
  within a day. Fixed guide paths `/api/<noun>` (`/api/updates`, `/api/update-policy`, `/api/topology`,
  `/api/cases`, `/api/identities`, `/api/owners`, `/api/*-format`). Rule: pick routes by the clue KEY, never the word.
- **Clue key set**: one concept key (D06 `callback_nonce`, D07 `moderator_data_route`, D08 `session_hint`, D09
  `preferences_route`, D10 `upload_shape`, D14 `inventory_route`, D16 `input_parameter`+`example_path`, D17
  `recovery_guide_route`, D18 `protected_reference`+`note`, D20 `state_format_route`, D24 `policy_format_route`, D26
  `update_feed`+`update_policy`, D27 `topology_route`+`case_directory_route` (+ value `service_pattern: server-side
  case fetch`), D28 `identity_directory_route`, D29 `owner_directory_route`) | VALUE keys (D19 `event_type`+
  `owner_scope`, D22 `stream_reference`, D23 `deployment`, D24 `expected_behavior`) | none (D11-D13, D15, D21, D25).
  Rule: no concept key -> prompt + bare GET of each route; a key shared by two classes -> race both.
- **Directory guides -> who to become (D27-D29)**: `{"caller": "analyst", "records_owner": "executive"}` (D28),
  `{"caller": ..., "restricted_owner": "executive"}` (D29), `{"cases": [{id, owner}]}` (D27). Same shape in single,
  TT and Mastery (handlers unchanged). Rule: victim = every string value whose key is NOT `caller|current*|self|me`,
  `restrict*|protect*|*_owner` keys first; for lists, the entries whose `owner` != your role first.
- **Self-describing errors**: `query_parameter` / `request_fields[]` in a 4xx body name the exact param or body
  field (D27, D29); `Vary: x-<header>` on a 403 names the trusted header (D28). Rule: read these BEFORE any ladder;
  fall back to ladders (`target|url|uri`; `id|case|case_id`; `X-Delegated-User, X-Forwarded-User, X-Remote-User,
  X-On-Behalf-Of, X-Impersonate-User, X-User`) only when absent.
- **Signed manifest, unverified artifact (D26)**: feed = `{updates: [{package, version, artifact: {build, hook},
  artifact_sha256, signature}]}`, policy = `{hooks: [{name, access: routine|restricted}]}`. Rule: replay the feed
  entry verbatim, swap ONLY `artifact.hook` to a non-`routine` hook (keep sha256 + signature) -> `{}`/edited
  package names give `update_not_found`.
- **Internal topology (D15, D27)**: D15 port 8080 was guessed; D27's `topology_route` hands `case_service:
  http://127.0.0.1:8080/status-<hex6>` (`network: loopback`). Rule: use the topology URL verbatim, append the object
  id (`?id=<case>`), pass it through the fetch param the error names.
- **Request body encoding (D12, D13, D19, D20, D29)**: only JSON binds; D20 nests `{"<field>": b64url(JSON)}`. Rule:
  JSON object first; a guide's `encoding` names the inner codec.
- **Format guides (D20, D24)**: read every guide field each attempt; replay the sample once, then mutate one thing at
  a time (data -> privilege ladder; format -> malformed / undecodable, keep any `prefix`).
- **Self-described report schema (D25)**: fill `report.fields` by name (`*_id`, `missing*` = the action's
  `operation`, `observed*` = what the log shows).
- **Privilege value spelling**: D13 `admin`; D20 ONLY `administrator`; D28/D29 victim `executive` (from the guide,
  never guessed). Rule: guide value first, then `administrator, admin, superuser, root, owner, staff, manager`.
- **Trusted client identity headers (D23 IP, D28 user)**: D23 `X-Forwarded-For: 127.0.0.1` past `loopback_only`
  (`evaluated_client` echoes the belief); D28 `X-Delegated-User: <records_owner>` past `delegated_identity_rejected`.
  Rule: header named by error/`Vary` first, then the IP or user ladder, one header at a time.
- **Async job binding (D29)**: feature 405 `post_required` + `request_fields: [owner]`; POST `{"owner": <restricted>}`
  -> `{id: "<n>", queued_owner}`; secondary 400 `job_id_required` + `query_parameter: id`; `?id=<n>` -> proof.
- **Transport upgrade (D22)**: 426 -> stdlib WS with `Origin` (none = 403), `?stream=<ref>`, first text frame.
- **One-shot state (D21)**: `credit_not_overspent` + `credits` -> GET-only recon, ONE barrier burst of ~24 POST `{}`.
- **Earlier classes (one line each)**: D01 robots `Disallow` -> `.json.bak` (depth 2). D02 foreign ids in
  `/api/history`. D03 `('%..%')` -> tautology ladder. D05 GET then POST every route. D07 board noun `messages` |
  `postcards`. D09 outside mailbox. D10 preview URL from the upload `path`. D11 `{{objective}}`. D12 plant, re-GET
  after EACH. D13 `display_name` + privilege keys. D14 single field x action. D15 `?url=http://127.0.0.1:8080<sec>`.
  D16 `%3Bcat /run/huntress/objective.txt`. D17 self-service token redeemed for another id. D18 introspect, id as STRING.
- **Proof carrier**: HTML / JSON `evidence` | `note` | `rows[]` | `stdout`, GraphQL `data`, bot receipt, WS frame.
  Rule: regex `proof_[0-9a-f]{32}` over every body/frame; never key on field names or on `effect`.

## Recognition cues -> first move
- `targets[]` -> `curl --max-time 20 -sS -A 'Mozilla/5.0' -i <url>` (hook blocks curl without `--max-time`;
  Cloudflare 403s urllib's default UA), then `/robots.txt`, `/api/clues`, `/openapi.json`. Use `-i`: headers matter
  (D28's answer was in `Vary`).
- Read /api/clues FIRST, GET every `*_route` / `/api/<noun>` value and each feature/secondary bare: the JSON error
  (and `Vary`) names the missing piece. No concept key -> the prompt's verb names the bug.
- **Before ANY POST: is the state one-shot?** "credit", "twice", "race", `credits`/`balance` -> GET only, burst (D21).
- D01-D20 cues: `Disallow:` crawl; "Signed in as" IDOR; search box SQLi; `?doc=` traversal; "just a sign" GET it;
  `callback_nonce` XSS; `moderator_data_route` bot; `session_hint` `?sid=`; hidden `csrf_token` cross-site;
  `upload_shape` `.html` `{{objective}}`; "evaluates everything" SSTI; "come back later" 2nd-order; "binds whatever"
  mass assignment; `inventory_route`; `absolute_url_required`+`internal_only` SSRF; `example_path` cmd;
  `recovery_guide_route`; GraphQL 404; `event_type`+`owner_scope`; `state_format_route` (role `administrator`).
- D21-D25: "race it" burst; 426 WS + `Origin`; `trusted_reverse_proxy` + `loopback_only` -> XFF; `policy_format_route`
  -> undecodable payload; "logs missed" -> POST the log's own `report` schema.
- **"updater trusts its packages", `update_feed` + `update_policy`** -> D26: POST the feed entry with
  `artifact.hook` = the restricted hook, signature untouched -> `unverified_update_activated`.
- **"public fetch ... internal door ... somebody else's records", `topology_route` + `case_directory_route`** -> D27:
  `<feature>?target=<topology case_service>?id=<case owned by someone else>` -> `ssrf_then_object_authorization`.
- **"hall pass ... photocopies ... delegated service boundary", `identity_directory_route`, 403
  `delegated_identity_rejected` + `Vary: x-delegated-user`** -> D28: GET feature with `X-Delegated-User:
  <records_owner>` -> `delegated_identity_trusted`.
- **"job went into the queue with your name ... loosen the binding", `owner_directory_route`** -> D29: POST
  `{"owner": <restricted_owner>}` to feature, then `<secondary>?id=<returned id>` -> `queue_owner_binding_bypassed`.
- **Prompts naming a service boundary / hallway / delegation** (D27-D29): the trust is between internal services;
  a guide route hands you the victim or the internal URL -- become THAT identity at the hop the prompt names.
- Prompt words naming a SECURE behaviour (D24/D25): do the action, then show the app what it failed to do.
- Proof regex hit = landed; an `effect` alone is NOT (D12 empty rows; D16 baseline already says completed).

## Day by day
- **D01-D20 (cal. 19-26)**: one request each once routed. Singles 36-116 s. TT `solver_incomplete` whenever the plugin
  was late. D19 lost ~60 s bisecting narrow webhook bodies; D20 needed `administrator`. A live turn chaining
  `ls -la; cat /run/huntress/*` was stopped by a safety classifier: keep injections to one plain read.
- **D21-D25 (cal. 27-28)**: D21 race NOT SOLVED (credit spent by a dry-run POST before the burst; draft plugin in
  `challenges/day27/web-double-spent/solver/`). D22 WS ~71 s, TT lost (plugin 20 s late). D23 XFF ~64 s, TT 10.5 s.
  D24 fail-open 41 s by hand, TT lost (plugin late). D25 logging ~86 s, TT first try. All four Mastery 4/5 (D04 slot,
  solver keyed on the prompt; fixed in the cal. 28 post-mortem).
- **D26 Trust the Build (cal. 29, Fiber)**: A03:2025 supply chain. Clues `{feature_route: /action-<hex6>,
  update_feed: /api/updates, update_policy: /api/update-policy}`. Signed manifest replayed with `artifact.hook:
  privileged_export` (policy `access: restricted`), sha256 + signature untouched -> `unverified_update_activated`.
  Edited/empty bodies -> `update_not_found`. Single CORRECT ~63 s; plugin promoted first -> TT 10.7 s, Mastery 5/5
  12.7 s, first try.
- **D27 Internal Affairs (cal. 29, Ktor)**: first CHAINED day, SSRF -> IDOR. Clues `{feature_route: /process-<hex6>,
  topology_route: /api/topology, case_directory_route: /api/cases, service_pattern: "server-side case fetch"}`.
  Feature bare -> `target_required` + `query_parameter: target`; topology -> `case_service:
  http://127.0.0.1:8080/status-<hex6>` (direct GET = `internal_only`). `?target=<case_service>?id=<foreign case>` ->
  `ssrf_then_object_authorization`. Single ~77 s; TT 19.6 s, Mastery 5/5 27.5 s, first try.
- **Cal. 29 folder re-check (cal. 31 post-run, D26 + D27)**: all six modes CORRECT first try; no `solver/NOTES.md`,
  no `VARIANT AXIS:` lines, guide shapes identical in single/TT/Mastery (only host + `<word>-<hex6>` re-dealt).
  The auto cases' `live_target.json` hold only `{attempt, targets[url]}` (no bodies) -> not replayable after 410.
- **D28 Pass the Identity (cal. 30, Axum)**: trusted delegated-identity header (confused deputy / A07). Clues
  `{feature_route: /execute-<hex6>, secondary_route: /result-<hex6>, identity_directory_route: /api/identities}`;
  directory `{caller: analyst, records_owner: executive}`; feature 403 `delegated_identity_rejected` with `Vary:
  x-delegated-user`. `curl -H 'X-Delegated-User: executive' <feature>` -> `delegated_identity_trusted` (the secondary
  stayed rejected: the header works on the FEATURE route). GET-only, re-runnable. Single CORRECT ~49 s
  (answer-first worker, by hand, 3 curl calls); TT 13.4 s, Mastery 5/5 11.1 s, first try.
- **D29 Queue the Confusion (cal. 30, Pyramid)**: async job owner binding (client chooses the job's owner). Clues
  `{feature_route: /process-<hex6>, secondary_route: /audit-<hex6>, owner_directory_route: /api/owners}`; directory
  `{caller: analyst, restricted_owner: executive}`; feature 405 `post_required` + `request_fields: ["owner"]`; POST
  JSON `{"owner":"executive"}` -> `{ok, id: "13", queued_owner: "executive"}`; secondary 400 `job_id_required` +
  `query_parameter: id`; `<secondary>?id=13` -> `queue_owner_binding_bypassed`. Single ~53 s, plugin promoted before
  submit; TT 9.2 s, Mastery **6/6** 11.0 s, first try.

## GM answer conventions learned
- Answer = bare `proof_<32 lowercase hex>` (the CORRECT body's `flag` is a different value; never submit it). `trim`.
  Ids `proof-1`..`proof-N` in target order. Batch all Mastery proofs in one submit; partial = `accepted`+`remaining`.
- `effect` spellings confirmed: `framework_authorization_bypassed` (D05), `isolated_browser_callback` (D06),
  `fixed_session_privilege_transfer` (D08), `delayed_query_revealed_private_row` (D12), `bound_privileged_property`
  (D13), `api_field_action_authorization_bypassed` (D14), `internal_service_reached` (D15),
  `worker_command_completed` (D16, also on the harmless baseline), `synthetic_account_recovery` (D17),
  `forged_event_consumed` (D19), `serialized_role_trusted` (D20), `unauthorized_event_stream` (D22),
  `proxy_trust_admin_bypass` (D23), `exceptional_condition_fail_open` (D24), `decisive_security_event_missing`
  (D25), `unverified_update_activated` (D26, + `package`), `ssrf_then_object_authorization` (D27),
  `delegated_identity_trusted` (D28), `queue_owner_binding_bypassed` (D29). Failure spellings `credit_unavailable`
  (D21), `update_not_found` (D26), `delegated_identity_rejected` (D28), `job_id_required` (D29).
- `already_solved` after CORRECT is harmless; a 503 `temporarily_unavailable` on submit may still have landed.
- TT/Mastery are "regular scored challenges by default"; `run_for_time:true` asks for a timed Hall-of-Fame attempt.

## Pitfalls that cost time
- **Burning a one-shot target (D21, unsolved).** Dry runs, race_bisect, default ladders and earlier-day handlers that
  POST to `feature_route` must NOT run before the race handler. Recon on a credit/balance kit is GET-only.
- **Verifying a plugin on a COMPLETED target (D28)**: after CORRECT `/api/clues` returns only `{state}`, so the
  plugin verifier reported "KEY_MAP matches none of ['state']". Not a plugin bug: verify on a fresh TT target or a
  recorded case; save target responses during the solve (410 afterwards) -- the harness's auto cases
  (`live_target.json`) store URLs only, so save the clue/guide/error bodies yourself into `solver/cases/`.
- Shipping a new class without its handler loses the TT. Write `lib/web/handlers/dayNN_*.py` (KEY_MAP on a concept
  KEY + HANDLERS) BEFORE the single submit (D11, D19, D20, D23, D25-D29 did; D22, D24 did not).
- Ignoring response headers: `curl` without `-i` would have hidden D28's `Vary: x-delegated-user`.
- Guessing the victim / internal port: since D27 a guide hands them over (`records_owner`, `restricted_owner`,
  `case_service` URL). Read the guide before any ladder.
- Missing `Origin` on a WebSocket handshake = 403 (D22). No websocket package in the venv; use stdlib.
- Bisecting a generic rejection one field at a time (D19 ~60 s lost): send ONE alias-union body first.
- Stopping at `role: admin` (D20 wanted `administrator`): `role_not_permitted` = right field, keep laddering.
- Treating `effect` as success (D12, D16). A valid guide sample (D24 `policy: standard`) is the baseline.
- Raw `;` in a Go query string is dropped -> `%3B`. GraphQL 404 on GET -> POST. Form bodies on JSON APIs are ignored.
- Choosing routes by the WORD in a clue value or by prompt keywords in Mastery. Solvers importing each other's
  `fallback()`. Hammering one target with every probe in parallel. Polling a bot receipt for a fixed 12 s (D07).
- `curl` without `--max-time` is blocked by the hook (and `sleep` by no_block.py).

## reviewer cross-check (measured on a parallel agent; folded into the drivers)
- D03 oracle trap: `q` sits in an EVEN number of `LIKE '%q%'` clauses, so `' OR '1'='1` and `'1'='2` BOTH return all
  rows; oracle = `nope' OR (<cond>) OR '1'='2`. D04: depth 1-2 `../` silently returns the normal page; use >= 3.
  `control_unavailable` on `op=start` is TRANSIENT (26.7 s hang); back off and re-send.
