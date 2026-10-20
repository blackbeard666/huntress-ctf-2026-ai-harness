# web — technique log (lane-days D01-D05 released; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Late release, catch-up pace.** No web on calendar days 1-18. Calendar day 19 released lane-days D01-D03 and
  day 20 released D04-D05 (GM ids `web-exploitation-day-NN-<slug>`, folder `challenges/dayNN/web-*` = CALENDAR day).
  Expect 2-3 new lane-days per calendar day until it catches up. Each lane-day = ONE classic OWASP bug, named by a
  title pun: D01 backup exposure "Back Up a Minute", D02 IDOR "Permission to Slip", D03 SQLi "Query Me This",
  D04 path traversal/LFI "Stay in Your Directory", D05 missing function-level authorization "Administratively Speaking".
- **No artifact: a live target.** `start` returns `result: preparing` (no deadline) until ready, then
  `targets: [{"id": "Target N", "url": "https://<48hex>.2026.huntress.ctf.games/"}]` (D01-D02 it was only in the
  status body; since D03 also in contract.json). Reachable DIRECTLY from the host (no `hb exec` needed), behind
  Cloudflare. After CORRECT the host returns `410 {"state":"completed"}` on every path; an untimed target stops after
  30 min idle.
- **Contract is fixed:** one question per target: `proof-N` "Recover the proof from Target N.", artifact `Target N`,
  `exact_text`, normalization `trim`. The answer is always a token `proof_<32 lowercase hex>` printed by the app.
- **Mastery = 2 targets**: today's bug + ONE earlier lane-day's bug (D01 backup both times so far: D03 set 2, D04
  Target 1). The prompt describes only today's bug, so the older target has no text hint. Mastery targets take
  ~310-320 s to leave `preparing` (singles / Time Trials 4-10 s).
- **Apps narrate themselves**: robots.txt `Disallow`, HTML comments (`<!-- deployment note: remember to review
  crawler policy -->`), `/api/clues` JSON (`framework`, `feature_route`, `current_role`), `/api/history`, page JS
  `fetch('/api/...')`, the prompt naming an absolute path. Read these before guessing any path. "Framework" banners
  (Django, "tiny native Node.js HTTP server", `.php` names) are costume; the bug is what the title says.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Target host / count**: random 48-hex subdomain per attempt; 1 target (single, TT), 2 (Mastery). Rule: map
  question `artifact` "Target N" to `targets[].id` (fallback: Nth entry); never reuse a URL across attempts.
- **Mastery composition / order**: earlier-day target at set 2 (D03) or Target 1 (D04); the prompt is today's only.
  Rule: run EVERY known concept probe on EVERY target (cheap recon first), never route by prompt keywords alone.
- **Backup exposure (D01) names**: robots `Disallow: /snapshots-<hex>/` | `/deploy-<hex5>/`; index title "Deployment
  archive"; file `environment-copy-<hex>.json.bak` | `site-config-<hex6>.json.bak` (+ `release-notes.txt` decoy);
  proof under JSON key `support_note`. Rule: robots/sitemap/comment/href paths -> fetch -> follow the links ON that
  index too (depth 2, same origin) -> regex `proof_` in bodies and zip members.
- **IDOR (D02)**: object ids from `/api/history` (foreign `case_id`, owner `executive`, `visibility: reference_only`);
  API template from the page's `fetch()`. Rule: harvest every `id`/`*_id` from JSON feeds, request the foreign ones.
- **SQLi (D03)**: GET form `/lookup?q=`; WHERE wraps input in `('%..%')` + a visibility AND; errors swallowed.
  Rule: tautology list covering `'`, `')`, `'))`, `"`, `#`/`--` endings (`zz') OR 1=1 --` worked).
- **LFI (D04)**: home links `reader.php?doc=<page>`; target path named in the prompt (`/run/huntress/objective.txt`).
  Rule: every query param whose value has `.` or `/` x payloads `../`*10+path, absolute, `....//`, `..%2f`,
  `php://filter/convert.base64-encode/resource=`, and `<orig dir>/` + `../`*10 (TT variant passed with this set).
- **Access control (D05)**: `/api/clues` -> `feature_route: /dispatch-<hex6>`, `framework` label, `current_role:
  analyst`; proof in JSON key `evidence` (`{"ok":true,"effect":"framework_authorization_bypassed",...}`). Rule:
  GET (then POST) every `/...` value in the clue JSON; then role headers/query/cookie as a fallback.
- **Proof carrier**: HTML `<p>`/pill text, JSON `support_note` | `note` | `evidence`. Rule: regex
  `proof_[0-9a-f]{32}` over every body (decode JSON / base64 / zip first) -- don't key on field names.

## Recognition cues -> first move
- `targets[]` in the contract -> `curl --max-time 20 -sS -A 'Mozilla/5.0' -i <url>` (hook blocks curl without
  `--max-time`; Cloudflare 403'd urllib's default UA on D03), then `/robots.txt`, `/sitemap.xml`, `/api/clues`.
- `Disallow:` path / "deployment note" comment -> fetch it, then every link on the index it returns (D01).
- "Signed in as X" + `/<things>/<id>` links + `fetch('/api/...')` -> IDOR: foreign ids from feeds (D02).
- A search form, "the database", "one pointed question" -> SQLi tautology with paren closing (D03).
- `?doc=` / `?page=` / `?file=` with a filename value + "directory/boundary/mounted at /path" -> traversal (D04).
- "staff-only", "sign but no lock", "bouncer", `current_role` -> unprotected route from the app's own clues (D05).
- JSON body with `effect` + `evidence` -> the exploit landed; `evidence` is the answer.
- Static evidence (HAR, pcap, logs, web shells, JWTs) has NOT appeared yet; the cues for it are in the coverage atlas.

## Day by day
- **D01 Back Up a Minute (cal. day 19)** -- robots.txt `Disallow: /snapshots-<hex>/` -> directory index ->
  `environment-copy-<hex>.json.bak` -> `support_note: proof_...`. Lost time to `preparing` with no URL yet
  (re-poll `hctf status` until `targets[]` appears) and to `--from-solver` refusing a target-only mode (submitted the
  value directly).
- **D02 Permission to Slip (cal. 19)** -- IDOR: `/api/history` leaked a foreign case id; `GET /api/briefs/<id>` (template
  from the brief page's `fetch`) returned the note with the proof. Target left `preparing` after ~2 min.
- **D03 Query Me This (cal. 19)** -- SQLi: `GET /lookup?q=zz') OR 1=1 --` showed the hidden `restricted` row
  "Private escalation" with the proof. `' OR '1'='1`, `%' OR 1=1 --` and UNION all returned "Nothing matched"
  (input wrapped in parentheses). Mastery set 2 was the D01 backup target.
- **D04 Stay in Your Directory (cal. day 20)** -- "The viewer should stay inside its pages directory ... proof mounted
  at /run/huntress/objective.txt". Home linked `reader.php?doc=<page>`; `GET
  /reader.php?doc=../../../../../../run/huntress/objective.txt` (>= 6 levels; 10 is safe) printed the proof after the
  "Document viewer" pill. The absolute path and `....//` did NOT work. Single CORRECT in 51 s; TT by solver in 8.9 s.
  **Mastery had trouble**: Target 2 (LFI) was solved, but the solver missed Target 1, a D01 backup site (Node.js
  "Green Light" status page, comment "review crawler policy", robots `Disallow: /deploy-444d0/`). Its `exposed()`
  fetched the Disallow path's index but never followed that index's `site-config-<hex>.json.bak` link. A live worker
  read it by hand (~6 min after start, ~5 of them in `preparing`). Fix: depth-2 crawl + all-concepts dispatch.
- **D05 Administratively Speaking (cal. 20)** -- "a staff-only door with no lock on it -- just a sign". `/api/clues`
  -> `{"framework":"Django","feature_route":"/dispatch-fa3df6","current_role":"analyst"}`; a plain GET (POST gave
  the same) of the feature route -> `{"ok":true,"effect":"framework_authorization_bypassed","evidence":"proof_..."}`.
  No header, cookie or role change needed; `/admin/` and `<route>/admin` returned `not_found`. Single CORRECT in
  47 s; TT 15.4 s; Mastery 340 s (321 s preparing), with the other target solved by the fallback chain that imports
  the earlier days' solvers.

## GM answer conventions learned
- Answer = the bare token `proof_<32 lowercase hex>` (no flag wrapper; the GM's `flag` field in the CORRECT body is
  a different value, so never submit it). Normalization `trim`. Ids `proof-1`..`proof-N` in target order.
- Batch all Mastery proofs in one submit. A partial submit returns `accepted` + `remaining` and is kept.
- `already_solved` after CORRECT is harmless (parallel workers raced).

## Pitfalls that cost time
- Routing by prompt keywords in Mastery: the earlier-day target is described by TODAY's prompt (D04 missed T1).
- One-level crawls: a `Disallow` dir is an index page, and the proof is one link deeper (D04 Mastery).
- Live cases can't be replayed: the target 410s after CORRECT and the stored contract may be the `preparing` body
  without `targets`. Save the target's responses during the solve; don't hard-code the proof.
- Waiting on `preparing`: poll status; Mastery takes ~5 min, so start it early and don't treat the wait as a failure.
- `curl` without `--max-time` is blocked by the unattended-run hook; default urllib UA can draw a Cloudflare 403.
