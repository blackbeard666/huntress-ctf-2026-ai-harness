# Web coverage atlas

Lane: a LIVE challenge-owned target per question (`targets[{id:"Target N", url}]`, no artifact), one `proof-N`
question per target, answer = the token `proof_<32 hex>` the app prints once the bug is exploited (`trim`). One
classic OWASP-style bug per lane-day, named by a title pun: D01 exposed backup (robots `Disallow` -> index ->
`.json.bak`), D02 IDOR, D03 SQLi (paren-wrapped LIKE), D04 path traversal to the prompt-named file
`/run/huntress/objective.txt`, D05 unprotected "feature route" named by `/api/clues` (missing function-level authz;
JSON `effect: framework_authorization_bypassed`, `evidence: proof_...`). Mastery = today's bug + one earlier
lane-day's bug on a second target (D01 twice so far), described only by today's prompt. Release pace: lane-days
D01-D03 on calendar day 19 and D04-D05 on day 20, so expect 2-3 new bugs per calendar day. The arc so far runs
info-disclosure -> broken access control (object) -> injection (SQL) -> file read -> broken access control
(function). Next most likely: the remaining OWASP classics that a proof file or a JSON `effect` can demonstrate:
OS command injection, SSTI, SSRF, auth/session forgery (JWT / cookie / role claim, mass assignment), header-trust
bypasses, XSS, XXE, upload. File-read bugs reuse the prompt's mounted proof path.
Snapshot 2026-10-20 (after D05; first atlas for the lane; `hctf prebuild` has NO `web` lane config yet, see gap
`enable-web-prebuild-lane`).

Status legend: `seen Dnn` = GM-confirmed lane-day (solver in `challenges/<cal-day>/web-*/solver/solve.py`).
`gap` = nothing reusable in lib (each day's solver re-implements fetch + regex). Allowed prebuild imports exclude
`urllib.request`, so prebuilt web modules must be PURE: given page/JSON bodies -> a request plan
`[(method, path, headers, body)]`; given a response -> proof or next hints. The solver does the fetching.

## Coverage table

| # | concept | status | recognition cues | first move | likelihood next 3 cal. days |
|---|---|---|---|---|---|
| 1 | exposed backup / forced browsing via robots | seen D01 (Mastery D03, D04) | robots `Disallow: /<word>-<hex>/`, comment "crawler policy", "diary", "archive", "forgot to clean up" | robots -> index -> every link (depth 2) | done; keeps returning in Mastery |
| 2 | IDOR (object-level authz) | seen D02 | "Signed in as", `/<things>/<id>`, `fetch('/api/<things>/'+id)`, "someone else's row" | foreign ids from `/api/history`-style feeds | done; Mastery |
| 3 | SQL injection (UNION-less tautology) | seen D03 | search form, "database", "one pointed question" | `zz') OR 1=1 --` family | done; Mastery |
| 4 | path traversal / LFI | seen D04 | `?doc=`/`?page=`/`?file=` with filename value, "directory", "boundary", "mounted at /path" | `../`*10 + prompt path | done; Mastery |
| 5 | missing function-level authz (unlinked route) | seen D05 | "staff-only", "sign, no lock", "bouncer", `/api/clues` `feature_route`, `current_role` | GET the clue route | done; Mastery |
| 6 | role / privilege via client-controlled header, query or cookie | gap (D05 solver tries X-Role / `?role=admin` / `role=admin` cookie) | `current_role` in clues, `role=` cookie, `X-User-Role` mention | flip the value the app names | high: D05 sequel "now there is a lock" |
| 7 | JWT tampering (`alg:none`, weak/leaked HS256 secret, kid/jku) | gap | 3 base64url parts in cookie / `Authorization`, "token", "signature" | decode; resign with `none` or the leaked secret | high |
| 8 | signed-cookie / session forgery (Flask `itsdangerous`, Express `s:`, base64 JSON cookie) | gap | `session=eyJ...` dot parts, `s%3A` prefix, base64 JSON cookie | decode; re-sign if the secret leaks (backup, .env, clues) | high |
| 9 | mass assignment / over-posting | gap | JSON profile update, `is_admin`/`role` in GET but not in the form | add `role:"admin"` / `is_admin:true` to PUT/POST | high |
| 10 | OS command injection | gap | "ping", "lookup host", "diagnostics", "convert", tool output in page | `;cat /run/huntress/objective.txt`, `|`, `$()`, backticks, `%0a` | high |
| 11 | SSTI (Jinja2 / Twig / ERB / EJS / Handlebars) | gap | "template", "preview", "greeting card", `{{7*7}}` -> 49 | engine probe then file-read gadget | high |
| 12 | SSRF | gap | "fetch URL", "preview link", "webhook", "import from URL", "internal" | `http://127.0.0.1:<port>/...`, `file:///run/...`, the internal host the app names | high |
| 13 | XSS (reflected / stored / DOM) | gap | "comment", "guestbook", "report to admin", reflected param in HTML | reflected marker, then `<script>` / handler; app may return `effect` JSON or need a bot | med-high (proof needs a bot or server-side check) |
| 14 | default / leaked credentials login | gap | login form, creds in comment / backup / JS / README | use the leaked pair; vendor default only (no brute force) | med-high |
| 15 | auth bypass by header trust (`X-Forwarded-For: 127.0.0.1`, `X-Original-URL`, `X-Forwarded-Host`) | gap | "internal only", "localhost only", 403 with IP in message | spoof the header the error names | med-high |
| 16 | HTTP verb / method-override tampering | gap | 405/403 on GET, `X-HTTP-Method-Override`, `_method=` | HEAD/POST/PUT/OPTIONS + overrides | med |
| 17 | path-normalisation authz bypass (`/admin/..;/`, `//admin`, `%2e`, case, trailing `.`/`/`) | gap | 403 on a named route, proxy in front (`Server:`/`Via:`) | normalisation variants of the blocked path | med |
| 18 | XXE | gap | XML upload/import, `Content-Type: application/xml`, SOAP, SVG/DOCX upload | external entity `file:///run/huntress/objective.txt` | med |
| 19 | NoSQL injection (Mongo operators) | gap | JSON login, "MongoDB", `username[$ne]=` | `{"$ne": null}`, `$regex`, `$gt:""` | med |
| 20 | file upload -> webshell / served file | gap | upload form, "avatar", "attachments", files served back | upload a script/template the server executes or a path-traversal filename | med |
| 21 | insecure deserialization (pickle / PHP `O:` / node-serialize / Java `rO0`) | gap | base64 cookie starting `gASV`/`Tzo`/`rO0`/`{"rce"` | craft a gadget that reads the proof file | med-low |
| 22 | exposed VCS / env / debug (`/.git/`, `/.env`, Werkzeug/Django DEBUG, actuator, phpinfo) | gap | `X-Powered-By`, DEBUG 404 page listing routes, `/.git/HEAD` 200 | fetch the leak, reconstruct `.git` objects | med (D01 cousin) |
| 23 | GraphQL introspection / hidden field | gap | `/graphql`, `{"data":` | `__schema` query, then the hidden field | med |
| 24 | open redirect / CORS / CSRF | gap | `?next=`, `Access-Control-Allow-Origin` reflecting | prove with the app's `effect` response | low (hard to prove with a static proof) |
| 25 | prototype pollution (Node) | gap | JSON merge endpoint, "settings", Node banner | `{"__proto__":{"isAdmin":true}}` | med-low |
| 26 | race condition / business logic (negative qty, coupon reuse, price tamper) | gap | shop / wallet / voucher | parallel requests, negative/overflow values in the app's own form | med-low |
| 27 | password-reset / predictable token / OTP | gap | "forgot password", token in response, sequential/time-based token | read the token the app leaks; no brute force | med-low |
| 28 | UNION / error / blind SQLi | gap (D03 needed only a tautology) | numeric id param, DB errors shown | `ORDER BY` count, `UNION SELECT`, boolean diff | med (SQLi sequel) |
| 29 | LFI filters (`../` stripped, suffix appended, prefix required, encoding) | partial (D04 solver tries `....//`, `..%2f`, `php://filter`, prefixed) | traversal returns "not allowed" / `.php` appended | double encoding, `%00`, `....//`, `pages/../../`, wrappers | med (TT/Mastery sequel) |
| 30 | HTTP request smuggling / cache poisoning / host-header | gap | proxy + cache headers, password-reset links using Host | `X-Forwarded-Host`, CL/TE | low |
| 31 | static web evidence (HAR, pcap, access logs, web shell, minified JS) | gap (never released; skill covers it) | `.har`, pcap magic, combined-log lines, `eval(gzinflate(base64_decode(` | jq / tshark / decode layers | low (the lane is live-target so far) |

## Recognition cues (worker quick-reference)

```
FIRST 60 SECONDS ON ANY TARGET (all cheap, do them in parallel, curl --max-time 20 -A 'Mozilla/5.0'):
  GET /            -> links, forms, inline JS fetch('/api/..'), HTML comments, "Signed in as", pills, footer banner
  GET /robots.txt  -> Disallow paths (D01): fetch each, then EVERY link on what it returns (depth 2)
  GET /sitemap.xml, /api/clues, /api, /api/history  -> app-narrated routes / roles / ids (D02, D05)
  regex  proof_[0-9a-f]{32}  over EVERY body (JSON-decode, base64-decode, unzip first). JSON `evidence` = answer.
  410 {"state":"completed"} = attempt already solved; `preparing` = target not ready, re-poll hctf status.
MASTERY: 2 targets, prompt describes only today's bug -> run every concept probe on every target.

PROMPT / PAGE CUE                                     -> BUG                -> FIRST REQUEST
"backup", "diary", "archive", "forgot to clean up"     -> exposed backup     -> robots Disallow -> index -> .bak/.zip
"neighbor's records", "somebody else's row", ids       -> IDOR               -> foreign id from feed into the API template
search box, "database", "one pointed question"         -> SQLi               -> q=zz') OR 1=1 --   (+ ' " )) # variants)
"stay inside its directory", ?doc=/?page=/?file=      -> traversal/LFI      -> ?doc=../../../../../../../../../../run/huntress/objective.txt
"staff-only door, no lock, just a sign", current_role  -> unprotected route  -> GET /api/clues feature_route
current_role / role cookie / X-*-Role mention          -> role tampering     -> set the named value to admin
eyJ...eyJ...sig in cookie/Authorization               -> JWT                -> alg none / leaked secret, role claim
"ping", "host lookup", "diagnostics", "convert"       -> command injection  -> ;cat /run/huntress/objective.txt  (| $() ` %0a)
"template", "preview", "greeting", {{7*7}}=49          -> SSTI               -> engine probe -> file read
"fetch URL", "preview link", "webhook", "import"      -> SSRF               -> http://127.0.0.1/<named path>, file:///run/...
"profile", JSON PUT, is_admin in GET only              -> mass assignment    -> add role/is_admin to the body
"internal only", "localhost only"                      -> header trust       -> X-Forwarded-For: 127.0.0.1 (+ X-Real-IP, X-Original-URL)
XML/SVG/DOCX upload, application/xml                   -> XXE                -> <!ENTITY x SYSTEM "file:///run/huntress/objective.txt">
JSON login, Mongo                                     -> NoSQLi             -> {"username":{"$ne":null},"password":{"$ne":null}}
"comment", "guestbook", "report to admin"              -> XSS                -> reflected marker first; look for an `effect` reply
upload form, files served back                         -> upload             -> server-executed type or ../ filename
/.git/HEAD 200, /.env, DEBUG page                      -> VCS/debug leak     -> fetch, reconstruct, read secret -> forge
The prompt names an absolute path (/run/huntress/objective.txt): ANY file-read primitive should aim there.
Banners ("Django", "Node.js", ".php") are costume; the title pun names the bug.
```

## Readiness gaps

Priority 1 = plausible within ~3 calendar days (at 2-3 lane-days per day that is ~6-9 new bugs). "prebuild" = pure
python in a future `lib/web.py` (request planner + response parser, no I/O; the solver fetches) with offline
fixtures = recorded bodies incl. a decoy. "note" = harness/prompt change. "tool" = install. None built yet (no
`web:*` keys in `.run/prebuild-state.json`).

```json
[
  {"id": "enable-web-prebuild-lane", "concept": "harness: web is not a prebuild lane", "priority": 1, "action": "note", "detail": "hctf/prebuild.py LANES has no `web` entry, so none of the prebuild gaps below can drain. Owner of hctf/: add `web: {brief: prebuild_web, writable: (lib/web.py, tests/data/web_fixtures/), targets: tests/data/web_fixtures/TARGETS.json, gate: (tests/test_lane_fixtures.py,), regress_lane: web, requires: (lib/web.py:plan,)}` plus a minimal lib/web.py with `plan(pages) -> [requests]` and `find_proof(body) -> str|None`. Fixtures = saved target responses (the targets 410 after CORRECT, so record them during the single solve)."},
  {"id": "recon-crawl-depth2", "concept": "shared recon planner: robots/sitemap/comments/clue JSON/links, depth 2 (rows 1, 5, 22)", "priority": 1, "action": "prebuild", "detail": "The D04 Mastery miss. Pure function: given fetched bodies keyed by path, return the next same-origin GETs: robots Allow/Disallow paths, sitemap <loc>, href/src/action, fetch('/..') and axios/XHR literals in inline JS, HTML-comment paths, every string value starting with '/' in JSON (clues, history, config), plus links on any fetched directory index (depth 2), capped ~40 requests, skipping /assets and static images. Parser: proof_[0-9a-f]{32} over bodies after JSON / base64 / zip / gzip decoding. Fixtures: D01-style robots -> index -> .json.bak (proof one link deeper), D05-style /api/clues -> feature_route, decoy release-notes.txt."},
  {"id": "mastery-concept-dispatcher", "concept": "run every known lane concept on every target (Mastery mixes days)", "priority": 1, "action": "prebuild", "detail": "Registry in lib/web.py: concept -> (cheap detector over the recon pages, request planner). Order by detector hits, not prompt keywords: backup crawl, clue routes, IDOR feed ids, LFI params, SQLi forms, then role tampering, command injection, SSTI, SSRF. The per-day solve.py calls `dispatch(pages)` instead of importing earlier days' solvers one by one (D05 did that via fallback()). Fixture: a two-target recorded pair where target 1 is D01-style and the prompt is an LFI prompt."},
  {"id": "role-tamper-planner", "concept": "client-controlled role: header / query / cookie / JSON body / JWT claim (rows 6, 9)", "priority": 1, "action": "prebuild", "detail": "D05 had current_role: analyst and a route that needed nothing; the sequel likely enforces a role the client controls. From recon: the role field name and value the app shows (current_role, role, is_admin, group, tier), cookies set by the app, headers named in clues/errors. Plan: cookie role=<admin|staff|owner|the higher value the app lists>, base64-JSON cookie rewrite, X-Role / X-User-Role / X-Forwarded-User, ?role=, JSON body role/is_admin on PUT/POST/PATCH to the profile endpoint. Parser: `effect` + `evidence` JSON or proof regex."},
  {"id": "jwt-session-forge", "concept": "JWT alg:none / leaked-secret HS256 / Flask-itsdangerous / Express s: cookies (rows 7, 8)", "priority": 1, "action": "prebuild", "detail": "Pure python (hmac, hashlib, base64, json, zlib): decode JWT header/claims; produce alg none (+ 'None'/'NONE', empty sig), HS256 re-signed with secrets FOUND in recon (backup files, .env, clue JSON, JS bundles, comments), RS256->HS256 with a published public key (jwks.json, /.well-known). Flask session: base64url(zlib?) payload . timestamp . sig with itsdangerous key derivation (salt 'cookie-session', HMAC-SHA1 derive) re-signed with a leaked secret. Escalate role/admin/sub claims. No secret brute force beyond secrets the app itself leaks."},
  {"id": "cmd-injection-planner", "concept": "OS command injection to read the mounted proof (row 10)", "priority": 1, "action": "prebuild", "detail": "For each form/param the detector flags (host, ip, target, domain, filename, cmd): payloads with separators ; | || && %0a $() backticks, with/without a valid prefix value (127.0.0.1), reading the prompt-named path (default /run/huntress/objective.txt) via cat, also `$(cat ...)` echoed into output and `${IFS}` space bypass. Parser: proof regex in the response or in the reflected tool output block."},
  {"id": "ssti-engine-probe", "concept": "server-side template injection (row 11)", "priority": 1, "action": "prebuild", "detail": "Probe each reflected text field with arithmetic markers ({{7*7}}, ${7*7}, <%= 7*7 %>, #{7*7}, {{7*'7'}} -> 7777777 means Jinja2) and map the result to the engine; then a file-read payload per engine for the prompt path: Jinja2 cycler.__init__.__globals__.os.popen / get_flashed_messages.__globals__ / lipsum.__globals__, Twig _self.env / source(), ERB File.read, EJS/Handlebars/Nunjucks constructor chains, Freemarker ?new(). Also try reading app config (config.items(), SECRET_KEY) to feed jwt-session-forge."},
  {"id": "ssrf-planner", "concept": "server-side request forgery (row 12)", "priority": 1, "action": "prebuild", "detail": "Detect URL-taking params/forms (url, link, src, webhook, feed, image, callback). Plan: file:///run/huntress/objective.txt, http://127.0.0.1 / localhost / 0.0.0.0 / [::1] / 2130706433 / 127.1 on the target's own and named internal ports and paths (from clues/comments: /internal, /admin, /metadata), http://169.254.169.254/latest/meta-data/ only if the app names it, redirect-scheme and @-userinfo bypasses for an allowlist. Parser: proof regex in the fetched-preview body."},
  {"id": "header-trust-verb-path-bypass", "concept": "IP/header trust, method override, path normalisation (rows 15-17)", "priority": 1, "action": "prebuild", "detail": "For a route that 401/403/405s: X-Forwarded-For / X-Real-IP / X-Client-IP / True-Client-IP / Forwarded: for=127.0.0.1; X-Original-URL / X-Rewrite-URL with the blocked path; methods HEAD/POST/PUT/PATCH/OPTIONS and X-HTTP-Method-Override / _method; path variants /ADMIN, /admin/, /admin/., //admin, /./admin, /admin;/, /%61dmin, /admin..;/, /admin%2f, trailing ?/#. Stop at the first 200 carrying proof or effect JSON."},
  {"id": "xss-effect-probe", "concept": "reflected / stored / DOM XSS proven by the app (row 13)", "priority": 2, "action": "prebuild", "detail": "Reflect a unique marker in every param/form; classify the sink context (HTML text, attribute, JS string, URL) from the response; build a context-correct payload (<script>, \"><img src=x onerror=...>, '-alert(1)-', javascript:). The GM likely checks server-side (as D05 returned effect JSON) or via a report-to-admin bot endpoint: submit the payload URL there and poll the page/API for proof. Static DOM-XSS: scan inline JS for location.hash/search -> innerHTML/eval sinks."},
  {"id": "xxe-payloads", "concept": "XML external entities (row 18)", "priority": 2, "action": "prebuild", "detail": "For XML endpoints/uploads (application/xml, SOAP, SVG, DOCX/XLSX word/document.xml): classic in-band entity on the prompt path, parameter-entity variant, php://filter base64 for PHP, XInclude when the DOCTYPE is not controllable, and an SVG / DOCX container builder (zipfile) carrying the entity. Parser: proof regex, base64 decode."},
  {"id": "nosql-operator-injection", "concept": "MongoDB-style operator injection (row 19)", "priority": 2, "action": "prebuild", "detail": "JSON login/search bodies: {\"$ne\":null}, {\"$gt\":\"\"}, {\"$regex\":\".*\"}, {\"$exists\":true}; form-encoded username[$ne]=x; `$where` only when the app is Mongo-flavoured. Pick the field names from the form/JS. Parser: proof regex or a role/admin page reached with the returned session."},
  {"id": "upload-execution-planner", "concept": "file upload to execution or traversal (row 20)", "priority": 2, "action": "prebuild", "detail": "From an upload form: allowed-extension probing (double extension shell.php.jpg, .phtml/.php5, case, trailing dot, null byte), content-type/magic spoof (GIF89a prefix), filename traversal (../../), SVG with script/XXE, template files (.html/.ejs) if the app renders uploads. Payload only reads the prompt-named proof path. Parser: locate the stored URL in the response, fetch it, proof regex."},
  {"id": "vcs-debug-leak-reader", "concept": "exposed .git / .env / DEBUG pages (row 22)", "priority": 2, "action": "prebuild", "detail": "D01 cousin. Probe /.git/HEAD, /.git/config, /.env, /.DS_Store, /server-status, /debug, /actuator/env, /phpinfo.php ONLY when recon names them or as part of the capped recon list. Pure parser: .git objects (zlib) -> commits -> trees -> blobs (rebuild a file from loose objects; packfile index for refs), .DS_Store filename list, Django DEBUG 404 URL-pattern list -> new routes, .env KEY=VALUE secrets -> jwt-session-forge."},
  {"id": "sqli-union-blind", "concept": "UNION / error / boolean-blind SQLi (row 28)", "priority": 2, "action": "prebuild", "detail": "Sequel to D03. ORDER BY / NULL-count column discovery, UNION SELECT with the proof-table guess taken from error messages or sqlite_master / information_schema, string-column detection by marker; boolean-blind extraction with a diff oracle over the response length (bounded: one char at a time over [0-9a-f_proof], 32-char cap). Login-form bypass `admin'--`. SQLite/MySQL/Postgres comment and concat dialects."},
  {"id": "graphql-introspection", "concept": "GraphQL schema leak / hidden field (row 23)", "priority": 2, "action": "prebuild", "detail": "If /graphql or a `{\"data\":` response appears: standard introspection query, list every type/field, then query hidden fields (proof, secret, flag, note, evidence) and node(id) lookups for foreign objects (IDOR over GraphQL). Field suggestions ('Did you mean') when introspection is off."},
  {"id": "lfi-filter-bypass", "concept": "traversal filters / suffix / prefix rules (row 29)", "priority": 2, "action": "prebuild", "detail": "Extend D04's payload set into a planner: nested strip (....//, ..././), URL / double URL / overlong UTF-8 encoding of dot and slash, backslash, required prefix (keep the original dir: pages/../../..), appended suffix (.php/.html -> %00, ?, #, path truncation, php://filter), absolute path, file:// scheme, /proc/self/cwd and /proc/self/root prefixes. Order cheapest-first; parser decodes base64 filter output."},
  {"id": "deserialization-gadgets", "concept": "pickle / PHP / node-serialize cookies (row 21)", "priority": 3, "action": "prebuild", "detail": "Recognise base64 cookies starting gASV/gAN (pickle), Tzo/YTo (PHP O:/a:), {\"rce\" / _$$ND_FUNC$$_ (node-serialize), rO0 (Java). Build minimal gadgets that read the proof path (pickle os.popen reduce; PHP property tampering of an isAdmin/role field before any RCE). Prefer data tampering over code execution."},
  {"id": "logic-race-reset", "concept": "business logic, race, predictable reset tokens (rows 26, 27)", "priority": 3, "action": "prebuild", "detail": "Planner for numeric fields (negative, zero, huge, float, overflow), coupon/redeem replay, parallel burst plan (~20 requests) for a single-use action, and reset-token prediction from tokens the app itself leaks (timestamp, md5(email), sequential). No credential guessing."},
  {"id": "record-target-responses", "concept": "replayable live-target cases", "priority": 1, "action": "note", "detail": "Targets 410 after CORRECT and the saved contract may be the `preparing` body, so solver-test cannot replay singles (D02/D03 HELP). Harness: log every target request/response the solver or worker makes during the single into solver/cases/<case>/http/ and let solve.py replay them when the host 410s; this is also the fixture source for the web prebuild."},
  {"id": "headless-browser", "concept": "DOM / XSS needing a JS engine (row 13)", "priority": 2, "action": "tool", "detail": "Only if an XSS day needs client-side execution: `uv pip install --python .venv/bin/python playwright && .venv/bin/playwright install chromium` (or use the system chromium --headless --dump-dom). Most days are provable server-side; don't install before a day needs it."}
]
```
