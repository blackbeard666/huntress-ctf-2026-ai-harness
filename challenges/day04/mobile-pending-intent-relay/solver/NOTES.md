# Pending Intent Relay — solver notes

Concept: exported deep-link ChallengeActivity relays the intent's proof/answer to a
backend .../evidence endpoint (device-loopback URL, not a live service). The proof is
the decoded assets/huntress_puzzle.json value = backend answer code (ANS-<16 hex>).

Answer = decode puzzle `data` by `codec` (observed: xor with `key`; also handles
base64/hex/rot13/reverse/plain), extract the ANS- pattern.

Variant axes handled: package suffix, case ref, APK filename, Mastery `delivery N:`
label prefixes + multiple sets, codec, xor key as int / numeric string / string
(repeating key). All derived from bytes; no literals.

Proof: solver-test ok (single_solve); synthetic-mastery case covers int-key xor,
string-key xor, and base64 variants.
