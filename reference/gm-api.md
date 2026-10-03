# Game Master and CourseStack API notes (measured 2026-10-03)

## Reachability (important)
- GM `http://10.0.0.219/huntress-ctf-proxy` is reachable ONLY from inside Homebase (10.1.50.243).
  Over the player VPN (Windows OpenVPN, routes 10.0.0.0/16 + 10.1.0.0/16 via 10.200.0.1) the GM times out
  on TCP/80 and ICMP, whether Homebase is stopped or running.
- Homebase SSH (`HuntressCTF@10.1.50.243`) IS reachable over the VPN, but only while the VM is running.
- From Homebase, plain `curl` with no extra headers works; identity is supplied by the network path.
- SSH tunnels DO NOT work: sshd answers `channel open failed: administratively prohibited` for -L and -D.
  Treat this as a deliberate organizer control; do not try to get around it.
- Works: run the GM client ON Homebase over SSH (key auth, project key secrets/huntress_homebase installed in Homebase
  ~/.ssh/authorized_keys; a factory Reset wipes it). A fresh ssh exec takes ~3.4s; with ControlMaster multiplexing 0.6-2s;
  8 parallel calls over one mux finish in 2.5s. rsync is present on both ends for moving artifacts.
- Homebase: Ubuntu 24.04 on AWS, 2 vCPU, 3 GB RAM, 38 GB disk (29 GB free). Has codex-cli 0.159.3,
  Claude Code 2.1.286, docker, node, python3.
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
