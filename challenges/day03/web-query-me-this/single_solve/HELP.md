# web-query-me-this single_solve: solved, solver-test cannot replay

The Single Solve is CORRECT (GM status, confirmed.json: proof-1 = proof_40d939b9461649d78485c4bb732fddc6). The chain worker got there at 13:03:28; I derived the same value independently.

`hctf solver-test` fails only because the case is a live target:
- The target now returns HTTP 410 `{"state":"completed"}`.
- contract.json was overwritten with the post-solve status, which has no `targets`/`routes`, so solve.py has nothing to fetch.

Hard-coding the proof would break the rule that answers come from the bytes, so solve.py does not.

How solve.py gets the answer, live (it reads `contract["targets"][*].url`, matched by question artifact `Target N`):
- GET `<target>/lookup?q=zzz') OR 1=1-- -` with a curl User-Agent (Cloudflare 403s urllib's default UA).
- The unlisted `restricted` row ("Private escalation") carries `proof_...` in its `<p>`.
- Fallbacks: other quote/paren payload variants, then any `<p>proof_...</p>`.
- Verified by hand with curl through `hctf hb exec` before the target closed.
