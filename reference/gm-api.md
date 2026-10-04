# Game Master and CourseStack API notes (measured 2026-10-03)

## Reachability (updated 2026-10-04: pairing token)
- **DEFAULT (direct):** the GM is now reachable from anywhere at `https://2026.huntress.ctf.games` with a
  per-identity **pairing token**: header `Authorization: Bearer <token>`. No VPN, no SSH, no Homebase, no credits.
  Same `?op=...` / POST-JSON contract as the inside proxy (root path; `GET /?op=openapi`). Latency ~0.2s/call —
  easily fast enough for the ~6s timed windows, so timed runs are LOCAL now too.
  - Mint once from inside the CTF env (on Homebase): `curl -sS -X POST 'http://10.0.0.219/huntress-ctf-proxy?op=pair'`.
    Shown once. Stored at `secrets/gm_pairing_token` (gitignored); identity note in `secrets/gm_pairing_token.id`.
    Current token: minted 2026-10-04, **expires 2026-11-01T14:00:00Z** (re-pair before then).
  - The `hctf` CLI uses this by default (`remote.gm_transport()` -> "local"; token via `HUNTRESS_GM_TOKEN` or the secret).
- **INSIDE proxy (fallback / in-network backends):** `http://10.0.0.219/huntress-ctf-proxy` is reachable ONLY from
  inside Homebase (10.1.50.243); identity comes from the network path (no token). Over the player VPN the GM itself
  times out on TCP/80 + ICMP, but Homebase SSH (`HuntressCTF@10.1.50.243`) IS reachable while the VM runs.
  Use this for `hctf hb exec -- <cmd>` against challenge backends that live inside the CTF network (e.g. web lane).
  Force it for GM calls with `HCTF_GM_TRANSPORT=ssh` (expects the VM up).
- SSH tunnels DO NOT work: sshd answers `channel open failed: administratively prohibited` for -L and -D.
  Treat this as a deliberate organizer control; do not try to get around it.
- GM client on Homebase over SSH (key auth, project key secrets/huntress_homebase in Homebase ~/.ssh/authorized_keys;
  a factory Reset wipes it): fresh ssh exec ~3.4s; ControlMaster mux 0.6-2s; 8 parallel over one mux ~2.5s. rsync both ends.
- Homebase: Ubuntu 24.04 on AWS, 2 vCPU, 3 GB RAM, 38 GB disk (29 GB free). Has codex-cli 0.159.3,
  Claude Code 2.1.286, docker, node, python3. Role now: one-time pairing + in-network `hctf hb exec` + optional codex pool.
- Codex: `~/.codex/config.toml`: provider amazon-bedrock-runtime, model global.openai.gpt-6-luna, effort medium.
  `codex exec --skip-git-repo-check "<prompt>" </dev/null` works headless (stdin must be closed).
  A trivial prompt cost ~7.9k tokens (fixed overhead). Skills dir: `~/.codex/skills/` (empty).

## GM API (from ?op=openapi, saved in gm-openapi.json)
- GET  `?op=list` (smart default: earliest unfinished day) | `&day=N` (0 = welcome) | `&lane=` | `&all=true` | `&search=`
  lanes enum: warmups, metadata, script-analysis, mobile, binary, **web**, welcome   <- "web" lane exists, not announced
- GET  `?op=status&challenge=<id>` | `?op=artifact&challenge=<id>[&delivery=N]` | `?op=download&capability=<64 hex>`
- POST `{"op":"start"|"submit"|"retry","challenge":<id>,"answers":{<answer_id>:<str>}}`
  (the docs omit "op" for start/submit; the openapi spec makes "op" required, so always send it)
- 409 = attempt-state conflict (prerequisite_required, start_required); the questions contract is still returned.
- Each challenge returns `questions[]` aligned 1:1 with `answer_ids`; each question names its artifact, objective,
  normalization and answer_format.
- Challenge IDs: `<lane>-day-NN[-slug]`, with timed variants `<id>/time_trial` and `<id>/mastery` as separate IDs.
  The list response is in fixtures/list-day1.json (17 entries on Day 1 = 2 welcome + 5 lanes x 3 modes).

## CourseStack API (browser session cookies)
- playthrough = 36fc3c4d-796f-47ba-880f-9362883f7909, customer = f846c680-8c3f-4777-b41c-9b965949101e,
  homebase course-system id = aaf8fe6c-081c-4db9-8dbc-4ee4939f2694
- Credits shown in the UI = (take.course_playthrough.included_runtime_gb_seconds - take.course.course_gb_seconds)/3600
                       + credits.remaining_credit_hours
    GET /api/student/events/<event>/take        -> course.course_gb_seconds, course_playthrough.included_runtime_gb_seconds
    GET /api/student/credits/<customer>         -> remaining_credit_hours / remaining_credit_seconds
  The VM burns gbPerRuntime=2 GB-seconds per second = 2 credits/hr. Whether AI tokens draw from the same pool is not yet measured.
- GET  /api/student/courses/<playthrough>/systems?courseSystemIds=["<sys>"] -> state stopped|starting|running|stopping, ip
- POST /api/student/courses/<playthrough>/systems/<sys>/power {"power":"on"|"off"} (Reset is a separate action; never call it)
- GET  /api/student/courses/<playthrough>/vpn -> .ovpn profile
