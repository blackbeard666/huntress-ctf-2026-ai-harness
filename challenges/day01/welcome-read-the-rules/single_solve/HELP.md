# HELP: read-the-rules is blocked on the GM side

**Flag found:** `flag{bf61aced6e7f9335385a70f33b20d188}`. It sits in an HTML comment in the rendered DOM of
https://ctf.huntress.com/rules (see work/rendered.html, produced by headless Chromium `--dump-dom`; the raw HTML is a
client-rendered Next.js shell with no flag in it).

**What blocks submission:**
- `hctf start read-the-rules` keeps returning HTTP 503 `{"error":"artifact_unavailable"}` (three times: 06:26Z,
  15:22Z, and again in this run). So there's no contract and no answer_ids.
- `hctf submit read-the-rules '{"flag": "<flag>"}'` returns 409 `start_required`. (`flag` is a guess taken from
  Welcome Robots' contract; this challenge never gave its own answer_ids.)

**Next steps for the orchestrator/human:**
1. Retry `hctf start read-the-rules` later. Once it succeeds, submit the flag under the answer_id it returns.
2. Or submit the flag by hand in the "Read the Rules" CourseStack lesson, which the prompt explicitly allows.

No solver was needed (orientation challenge, Single Solve only).
