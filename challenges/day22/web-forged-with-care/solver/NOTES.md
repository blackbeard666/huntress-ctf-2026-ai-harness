# Day 22 web — Forged With Care (CSRF)

Derived answers (from the live workers' logs; the targets are now 410 `{"state":"completed"}`):
- single_solve (e1a79165): proof-1 = proof_d7ca4db36ad249db96741ac9f75eb854 (GM CORRECT)
- time_trial 1650d5ed: proof-1 = proof_fda7dd0cde44472f925389a17155b017 (GM CORRECT, live worker)

Construct: `/api/clues` -> `{"feature_route":"/submit-<hex6>","preferences_route":"/preferences",...}`. GET `/` sets
`arena_session`; `/preferences` has `<form method='get' action='/submit-..'>` with `<select name=destination>`
(`daily` + `review-NNNN@outside.example.invalid`) and hidden `csrf_token` (= session value). A same-site submit gives
`changed_across_sites:false`. The same request with `Sec-Fetch-Site: cross-site` (+ Mode/Dest navigate/document and a
foreign Referer) makes `/api/preferences` return `evidence: proof_<hex>`. The token is optional (the single used no
token, the TT included it).

Speed fix: the old solve.py was only the generic `lib.web` race (no CSRF handler). It ran 41 s and missed. Now
`csrf()` parses the form generically: every form on each clue-named page, GET/POST per the form, non-current external
option first, with the token / without it / swapped method. It needs about 5 requests (~1 s). `lib.web.solve_target`
runs only if that misses AND the home page is alive (2xx/3xx). Expired targets exit in about 1 s.
`answer()` stays self-contained (lib.web races every web solver's answer(); it must not call back into lib.web).

VARIANT AXIS: TT vs single differ only in the route hex (`/submit-<hex6>`), the mailbox number and whether csrf_token
is sent -- parse the form (action/method/select/hidden) from the clue-named page and send it as a cross-site
navigation, never hard-code the route.

## Proposed lib additions
- lib/web/handlers: a `csrf` handler (port `csrf()` from this solve.py), keyed on clue keys `preferences_route` /
  `browser_session`, or any page with a `<form>` holding a `csrf|token` hidden input. Headers: Sec-Fetch-Site cross-site,
  Sec-Fetch-Mode navigate, Sec-Fetch-Dest document, a foreign Referer (and Origin for POST).
- lib.web.solve_target: skip the 40 s race when GET base returns a non-2xx/3xx status (expired target = 410
  `{"state":"completed"}`); that alone is what made dead-target runs take ~9-40 s.
