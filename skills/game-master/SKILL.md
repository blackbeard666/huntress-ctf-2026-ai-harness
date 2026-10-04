---
name: game-master
description: Driving the Huntress Game Master through the hctf CLI - list, status, start, artifact, submit, retry - and reading its results (CORRECT, incorrect, accepted + remaining, pending, expired, start_required, prerequisite_required, artifact_unavailable). Use whenever you need challenge data or to submit an answer.
---

# hctf (run `source bin/env.sh` first if `hctf` is not on PATH)
`hctf` reaches the GM directly for you (public endpoint + pairing token, handled by the CLI; SSH-to-Homebase only as a fallback). Never call the GM URL yourself and never add your own auth/identity headers — the CLI owns the token.

| Need | Command |
|---|---|
| What exists | `hctf list --all` (or `--day N`) |
| A mode's contract and state | `hctf status <id>` (also works before start: 409 `start_required` still returns the questions) |
| Start or resume | `hctf start <id>` (Single Solve only, unless your prompt says otherwise; timed modes start a real clock) |
| Download the assigned bytes | `hctf artifact <id>` -> `<mode dir>/artifacts/<ts>/` (+ `latest`), sha256 checked against start.json |
| Submit | `hctf submit <id> '{"answer_id": "value"}'` (several ids at once is fine) |
| Run the solver library | `hctf solver-run <id>` / `hctf solver-test <id>` |

Ids: Single Solve `<base>`, timed modes `<base>/time_trial` and `<base>/mastery`.

# Results
- `CORRECT` (exit 0): done. `{"status":"pending"}` means CourseStack scoring is still settling, which is fine.
- `accepted` + `remaining: N` (exit 2): those answers were right; N more are needed.
- `incorrect` (exit 1): at least one answer is wrong. Submitting fewer answers per call narrows down which one.
- refused locally (exit 4): wrong answer_id, a format mismatch, a value already judged incorrect, or a cap reached.
  Read the reason. The caps: flags are hard-capped (never brute-force); each NON-flag field has a per-field probe
  budget so you can resolve the GM's exact wording for an enum/ATT&CK/format field by trying your ranked candidate
  spellings one per submit. When one is accepted, record it in `lib/knowledge.py`. Only a true dead end is HELP.
- `expired`: the timed attempt is over. Only the orchestrator retries (`hctf retry` works only after expiry).
- `artifact_unavailable`: the challenge has no file (e.g. read-the-rules: the flag is in the HTML of
  https://ctf.huntress.com/rules; fetch the page with `curl -s` and search it, including comments and hidden elements).
- `prerequisite_required`: the previous mode isn't finished or scored yet.

Every response is logged in `<mode dir>/log.jsonl`; confirmed answers are kept in `<mode dir>/confirmed.json`.
