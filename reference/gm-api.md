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
- **Dual-pool routes (new at the Day 8 drop, 2026-10-08; gm-openapi.json refreshed then).** Time Trial / Mastery:
  plain `start`/`retry` = the REGULAR pool (untimed play, `hall_of_fame_eligible: false`, warmups D8 had no deadline);
  `"run_for_time": true` = a fresh timed **Hall of Fame** attempt (`hall_of_fame_eligible: true`). Status/start bodies
  now carry `run_for_time`, `hall_of_fame_eligible`, `ranked_attempts_remaining` (~32/mode), `regular_variants_remaining`,
  `training_variants_remaining`, `variant_fresh`. Observed refusals:
  - `503 {"error":"training_rotation_invalid"}` -- regular pool broken for every lane but warmups at the D8 drop
    (deterministic, NOT load: never back off on it).
  - `409 {"error":"timed_intent_not_available"}` -- the route has no timed pool (Single Solve; "legacy" routes such as
    binary D8, which has no `ranked_*` fields but is HoF-eligible anyway): resend without `run_for_time`.
  - A `run_for_time` start on a LIVE attempt resumes it (no new ranked attempt). The clock starts at that start POST.
  Harness policy (user, 2026-10-08): **always HoF on TT/Mastery** (`hb_timed._post_start`; `HCTF_RUN_FOR_TIME=0` opts
  out for scouting/probes). The prerequisite check reads the latest TT attempt -- keep TT and Mastery in the same pool.
- The GM proxy drops idle keep-alive sockets after ~4-5 s (D8: 3.5 s idle reused fine, 5.4-8 s idle ->
  `RemoteDisconnected` on the submit). hb_timed never reuses a socket idle > 3 s and opens a fresh one for no-resend calls.
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

## Hall of Fame + timed/regular pools (course lessons as of 2026-10-12; reference/welcome/*.md)
- **Hall of Fame = public speed scoreboard**, separate from CourseStack points ("CourseStack ranks total points
  separately"): `GET https://2026.huntress.ctf.games/api/speed-scoreboard?mode=time_trial|mastery&view=rankings|leaders
  &limit<=1000&offset=N&sort=elapsed_ms&direction=asc[&challenge=<id>]` (no auth) -> rows {team_name, challenge_id,
  rank, elapsed_ms (GM-measured, shorter than our hb_timed elapsed), par_ms, under_par_ms, answer_count, set_count}.
  Every fresh, `hall_of_fame_eligible` timed attempt can improve the team's fastest time; untimed runs never rank;
  pre-eligibility attempts are not added retroactively (our rows start at Day 7). Main = `sec1-huntress-harness`,
  alt = `[redacted]`. Snapshot 2026-10-12 (Day 9): leaders 0.26-1.5 s, we rank #16-#33 (reference/hof/).
- `op=list` timed entries carry `run_for_time_supported: true`. There a PLAIN start is an UNTIMED regular attempt that
  still earns the flag + CourseStack points; `"run_for_time": true` on start/retry = timed + HoF. Regular and timed
  attempts draw from separate artifacts; timed never repeats an artifact; `ranked_attempts_remaining` and
  `regular_variants_remaining` are separate; regular pool exhausted -> retry still serves the last regular artifact
  (`variant_fresh: false`) for the flag.
- Older routes without `run_for_time_supported`: timed by default; after the last fresh variant `retry` ->
  `rotation_exhausted`; `{"op":"practice","challenge":id}` continues on that artifact untimed (no HoF, `practice: true`)
  and a correct submit still completes the mode and unlocks the next one.
- **Exhausted pool -> untimed fallback (harness since 2026-10-12)**: the live exhaustion verdict is
  `retry_variants_unavailable` (r11a binary D11 TT), not only `rotation_exhausted`. Both -> `error:exhausted` ->
  `timed_stage` switches to `op=untimed` (`hb_timed._post_untimed`: plain `retry` = regular pool on a
  run_for_time_supported route; a legacy route refuses it -> `practice`), runs local with no clock
  (`HCTF_UNTIMED_BUDGET` 60 s solver budget), generalizes between rounds (`HCTF_UNTIMED_ROUNDS` 3; 0 = old stop).
  `ranked_attempts_remaining == 0` in last_timed.json -> the next start goes plain (no doomed run_for_time request).
- Day 10/11 routes are LEGACY (no `run_for_time_supported`; timed by default). Day 11 first-attempt pools (main):
  binary `unique_attempts_remaining` 0 + `hall_of_fame_eligible: false` (nobody ranks binary D11), metadata 1, mobile
  15 TT / 7 Mastery, script 31, warmups 255. One failed attempt on a 0-1 pool = the untimed fallback or a lost mode.
- Vantage (2026-10-12, `.run/gm_rtt_bench.py`, keep-alive GETs): light request (op=openapi) p50 52 ms from Homebase
  public / 92 ms Homebase inside proxy / 315 ms WSL; op=status 0.22 s Homebase vs 1.8 s WSL (bandwidth). HTTP/2 = no
  gain (309 vs 322 ms). Homebase public is already next to the origin (Cloudflare front): no probe VM needed.
- `hctf hof [--day N] [--save]`: the public board per challenge vs #1 + day sums. Post-run `hof_race` (orchestrate):
  up to `HCTF_HOF_RACE`=3 extra eligible retries per passed TT/Mastery (Mastery first) while >= `HCTF_HOF_RACE_MIN`=8
  remain, reserve `HCTF_HOF_RESERVE`=5; stops on the first failure; skipped on a replay proxy.
- `start` always reconnects to the current attempt (never changes mode/spends a variant); while CourseStack scoring is
  pending the attempt stays in place. Teammates share one attempt, one deadline, one Mastery progress.
- Unexplained by the lessons: `503 attempt_context_invalid` (r9b, script D9 Mastery: start/retry/plain start/status).
