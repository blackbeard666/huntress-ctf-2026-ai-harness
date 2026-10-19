---
name: web
description: Huntress web lane - web application / web-traffic analysis of the Game Master's artifact (app source bundles, HAR and pcap captures, server/access logs, web shells, minified or packed JS, HTML/SVG smuggling pages, tokens and cookies), and, when the contract names one, requests to the challenge-owned target via hctf hb exec. Use for web-day-NN challenges (GM lane `web`).
---

**Installed: curl, jq, js-beautify, node, python3 (`requests`, `lxml`, `bs4`, `jwt`, `dpkt` in .venv), tshark, 7z/unzip, rg.**

# Live targets (what the lane really is, since D19)
GM lane `web-exploitation`. There is NO downloadable artifact (the artifacts dir is empty on purpose): the started
attempt's contract (`start.json`) carries `targets: [{"id": "Target 1", "url": "https://<hash>.2026.huntress.ctf.games/"}]`
and each question's `artifact` names one ("Target 1"). The harness already waited for the target to come up
(`preparing` -> `active`; `hctf start` reconnects and waits too) -- never `hctf retry`: the team gets ONE live web
target at a time, and a solved attempt's target answers HTTP 410 afterwards. Reach it directly from here with
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
