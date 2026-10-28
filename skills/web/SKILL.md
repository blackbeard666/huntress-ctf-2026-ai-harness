---
name: web
description: Huntress web lane - web application / web-traffic analysis of the Game Master's artifact (app source bundles, HAR and pcap captures, server/access logs, web shells, minified or packed JS, HTML/SVG smuggling pages, tokens and cookies), and, when the contract names one, requests to the challenge-owned target via hctf hb exec. Use for web-day-NN challenges (GM lane `web`).
---

**Installed: curl, jq, js-beautify, node, python3 (`requests`, `lxml`, `bs4`, `jwt`, `dpkt` in .venv), tshark, 7z/unzip, rg.**

# Live targets (what the lane really is, since D19)
GM lane `web-exploitation`. There is NO downloadable artifact (the artifacts dir is empty on purpose): the started
attempt's contract (`start.json`) carries `targets: [{"id": "Target 1", "url": "https://<hash>.2026.huntress.ctf.games/"}]`
and each question's `artifact` names one ("Target 1"). The harness already waited for the target to come up
(`preparing` -> `active`; `hctf start` reconnects and waits too) -- never `hctf retry` (it re-rolls the attempt and
the target you are working on), and a solved attempt's target answers HTTP 410 afterwards. Reach it directly from here with
`curl -sS -A 'Mozilla/5.0' --max-time 10 <url>` (Cloudflare 403s default library user agents; no `hctf hb exec`
needed). `solve.py` reads `contract["targets"]`, matches the question's `artifact`, and fetches with a browser UA.

# Scope
Only the Game Master's artifact and the target the CONTRACT names are in scope. Never scan, fuzz, brute-force or
load-test anything; send only the few targeted requests the evidence (page, JS, robots.txt, links) points to.

# First moves (by what the artifact is)
- **App source bundle** (zip of .php/.js/.py/.java/templates): `rg -n` for routes, auth checks, secrets, `eval|exec|
  system|unserialize|pickle|innerHTML|query(` sinks; read the route the question names, not the whole app.
- **HAR** (JSON `log.entries`): `jq '.log.entries[] | {m:.request.method,u:.request.url,s:.response.status}'`; bodies
  in `.response.content.text` (base64 when `.encoding=="base64"`); cookies/headers per entry.
- **pcap/pcapng**: `tshark -r f -Y http.request -T fields -e frame.number -e http.request.method -e http.host -e
  http.request.uri`; `tshark -r f --export-objects http,outdir`; follow a stream: `-qz follow,tcp,ascii,N`.
- **Access / server logs**: split fields with `awk`/python (combined log format); `sort | uniq -c` by IP, status, path,
  user-agent; the attack is the odd path/UA/status sequence (traversal, `UNION`, `%27`, `cmd=`, webshell POSTs).
- **Web shell / dropper page** (php/aspx/jsp/html): decode layer by layer (base64, gzinflate/str_rot13, `eval(atob(`,
  `String.fromCharCode`, packed `eval(function(p,a,c,k,e,d)`) -- `lib.codec` and the script-analysis skill's codec
  notes apply; `js-beautify` first, then `node` only on de-fanged code (print, never execute payload calls).
- **HTML/SVG smuggling**: the blob is in a `data:`/base64 string or a JS byte array -> rebuild the file, then hand it to
  the lane its bytes belong to (zip -> metadata, script -> script-analysis, binary -> binary-re).
- **Tokens / cookies**: JWT = 3 base64url parts (`python -c 'import jwt; print(jwt.get_unverified_header(t),
  jwt.decode(t, options={"verify_signature": False}))'`); Flask/Express session cookies are base64(json) + signature.
- **Live target named in the contract**: GET the page and its JS first, map the endpoints the JS calls, then reproduce
  exactly the request the question is about (headers, cookie, parameter).

# Reading the questions
Each question names its artifact and an answer_format: enum labels follow the GM label grammar in the playbook;
paths/URLs/parameters are usually asked verbatim (keep case, no trailing slash unless the bytes have one);
ATT&CK ids follow the shared reference (`lib.refs.attack`). Timestamps: keep the log's own timezone/format unless
the normalization says otherwise.

# Solver tips
Parse the artifact with standard libraries, not a hand-written parser: `json` for HAR, `dpkt` for pcap, `bs4`/`lxml`
for HTML, `jwt` for tokens, a regex only for log lines. **`solve.py` runs on Homebase in the timed modes, where tshark
and jq are NOT installed** (no sudo there): use tshark/jq for your own analysis, Python libraries inside the solver.
Locate things by structure (route name, header, field) rather than by offset or line number:
variants rename hosts, ids, paths and reorder entries. When an answer must be FETCHED from the live target, keep the
request-building in `solve.py` with a short timeout and the base URL read from the contract, so each variant's answer
is fetched, not stored.

# Speed first: submit the proof, then the CLASS becomes code (a clue-keyed plugin)
- Submit the single's proof the moment you (or the answer-first worker) have it -- never delay the single to polish
  `solve.py`. The Time Trial and Mastery get BRAND-NEW targets (this one dies with HTTP 410 at CORRECT; Mastery has 3 and
  puts today's class on ANY slot -- proof-1/2/3 only name slots), so a proof you got by hand never carries over.
- What carries over is a HANDLER for the class: `lib/web/handlers/<dayNN>_web_<challenge>.py` with
  `KEY_MAP = [(r"<regex on a /api/clues KEY>", name)]`, `HANDLERS = {name: fn}`, `fn(base, clues) -> "proof_..." or
  None` re-running the exploit end to end (recon what is per-target, then upload / forge / trigger / read; short
  timeouts; browser UA; nothing from a manual session). `lib.web.handlers` auto-loads it, so the generic solver
  dispatches to it on every fresh target -- and on later days' compounded Mastery targets. A key that only means the
  class next to a sibling key gets `KEY_COMPANIONS = {r"<key>": r"<sibling key>"}` (D25: `protected_reference` alone
  is not Day 14's BOLA class -- its kit always has `inventory_route`).
- **Plugin first (D25)**: the single's answer-first worker writes that plugin as a DRAFT in its own `$TMPDIR`, then gets
  the single's proof BY RUNNING it: `.venv/bin/python -m lib.web.plugin $TMPDIR/<name>.py <target url>` imports the
  draft, checks its KEY_MAP dispatches on the target's `/api/clues`, runs it, prints `PROOF proof_...` and PROMOTES it
  into `lib/web/handlers/` atomically (exit 1 = no proof, 2 = not a plugin, 3 = no clue key matches). So the plugin is
  in place at the single's CORRECT and the Time Trial's first run dispatches to it. Two failed draft fixes -> submit
  the hand-derived proof (never hold the single); the codify worker then writes the plugin. With a plugin in place the
  codify worker only HARDENS it on a fresh target and promotes a verified improvement through the same verifier.
- Never write `lib/web/handlers/<name>.py` in place (a timed runner imports it at any moment -- D25 picked one up
  mid-edit): every worker (generalize, speed fix, codify) edits a draft and lands it with `lib.web.plugin`. Never put
  class logic in `solve.py` (keep it the generic dispatcher) or `handlers/__init__.py` (two web chains may run at once).
  Key on a concept clue KEY, never on proof-N, a target slot, a host or a value. If the exploit is genuinely one-shot on
  a fresh target (a single credit / action a raced probe would spend -- D27 Double Spent), say so in the plugin's
  docstring AND set `RUN_ALONE = True` (or `RUN_ALONE = ["<name>"]`): the generic solver then races ONLY your handler
  for a confirmed-kit target, never the `default` ladder / prior-day solvers / other furniture-key handlers beside it
  (their sequential POST would burn the one credit). A burned target is NOT unsolvable -- reset it with `arena stop` ->
  `arena start` (a fresh target + fresh credit; the organizer's sanctioned recovery, not an in-app reset route) and run
  the burst once on the fresh one.
