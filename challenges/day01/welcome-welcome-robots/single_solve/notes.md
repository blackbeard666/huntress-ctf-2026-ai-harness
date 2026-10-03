# Welcome Robots (day01, welcome lane, orientation)

hypothesis | evidence | result
--- | --- | ---
Artifact holds the flag | `hctf artifact` -> HTTP 400 `invalid_delivery`; no artifacts/latest | dead end: no artifact for this challenge
GM start response issues the flag directly | contract.json: `result: issued`, `issued_flag: 729ea6044f6ee93500bc866eed812b7d`, answer_ids `[flag]` | submitted `{"flag": <issued_flag>}` -> CORRECT (exit 0)

No solver is needed (orientation, Single Solve only).
