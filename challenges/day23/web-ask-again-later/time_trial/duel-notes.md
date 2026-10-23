# web-ask-again-later (D23, GM base web-exploitation-day-12-ask-again-later) -- duel generalize notes

Derived (TT cec52bc0, from the live worker's transcript; GM-accepted): proof-1 = proof_8dfb818ff95e4eb8a6e6b435c2aa4217
Kit: /api/clues {framework: Sinatra, feature_route: /submit-<hex6>, secondary_route: /internal-<hex6>, current_role: analyst}.
POST feature_route JSON {name,...: "zz' OR 1=1 --"} -> {"ok":true,"saved":true}; GET secondary_route ->
{"rows":["Ordinary workspace note","proof_..."],"effect":"delayed_query_revealed_private_row"}.

Failure cause: at TT time no class handler existed (8 s timeout in the default ladder). The handler
`lib/web/handlers/day23_web_ask_again_later.py` (written 21:03 by the live/codify worker) covers it: keyed on
`secondary_route`, plants the tautology ladder (incl. the `--` payload) in every field as form then JSON, re-reads.
Live targets are finished, so verified against a local mock of the kit (both "quote-balanced works" and
"only some payload works" shapes): solve.py answers in 0.2-0.3 s.

VARIANT AXIS: second-order SQLi -- planted field + delayed reader (`/submit-*` -> `/internal-*`); rule: key on the clue KEY `secondary_route`, plant every payload shape (`'..'='`, `')..('`, `--`) into all common fields via form and JSON, re-GET the reader after each plant.

## Proposed lib additions
- Keep `lib/web/handlers/day23_web_ask_again_later.py` (second_order); consider ordering `zz' OR 1=1 --` JSON first -- it is the GM-live-measured winner on TT cec52bc0.
