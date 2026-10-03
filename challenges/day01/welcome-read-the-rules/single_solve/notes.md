# Read the Rules (read-the-rules, welcome, single_solve)

hypothesis | evidence | result
--- | --- | ---
GM start gives contract + answer_ids | `hctf start read-the-rules` -> HTTP 503 `artifact_unavailable` (log.jsonl: 06:26Z, 15:22Z, retried again this session) | no contract.json, no answer_ids
flag is in raw HTML of https://ctf.huntress.com/rules | curl -> work/rules.html (7122 B): Next.js SPA shell only, no flag | dead end (client-rendered)
flag is in rendered DOM | chrome-headless-shell --dump-dom -> work/rendered.html (28067 B): `<div><!-- flag{bf61aced6e7f9335385a70f33b20d188} --></div>` after "Contact information" section | FOUND: flag{bf61aced6e7f9335385a70f33b20d188}
submit under answer_id `flag` (the id Welcome Robots uses) | `hctf submit read-the-rules '{"flag": ...}'` -> 409 `start_required` | blocked: GM won't accept a submit until start works
