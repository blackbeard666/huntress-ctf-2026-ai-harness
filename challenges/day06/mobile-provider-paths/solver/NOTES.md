# Provider Paths — solver notes (Day 06 mobile-android)

Concept: APK with an exported ContentProvider on an overbroad path
(`.ProviderPathsProvider`, authorities `<pkg>.evidence`, `grantUriPermissions=true`,
no path-permission) plus an exported deep-link `ChallengeActivity`
(`huntress06://provider-paths/unlock`) that relays `answer`/`case_id` query params as
`proof`/`case_id` to a device-loopback backend
`http://127.0.0.1:19090/mobile/attempt/<id>/evidence?...&client_secret=SECRET-...&proof=<answer>`.

As in days 01–05, the `proof` the app sends is the decoded value of
`assets/huntress_puzzle.json`, and the backend's returned evidence code EQUALS that
value. The loopback is device-relative (connection refused from Homebase) and the
provider's `query()` is a stub, so no network request is needed — the answer is the
decoded puzzle value.

Single solve (GM-confirmed, flag 8b948437b1b1f1a6c5985542f3c11b4c):
`{"codec":"hex","data":"414e532d34364132344243444145354336453142"}` → `ANS-46A24BCDAE5C6E1B`.

Solver: decodes `huntress_puzzle.json` across codecs (plain/base64/base32/hex/rot13/
reverse/xor/split), fullmatch `ANS-<16 hex>` then looser search then `lib.decode.peel`;
falls back to `lib.android.extract_answer` (raw zip entries → dex strings → decompiled
scan) if the answer ever moves out of the puzzle json.

Variant axes: package suffix, case ref, APK filename, Mastery `delivery N:` prefixes
and `setN.answer` ids (`locate_apk` strips the prefix). No literals.
