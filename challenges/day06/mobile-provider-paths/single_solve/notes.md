# Provider Paths (Day 06 mobile) — notes

Mechanic (manifest meta-data): "exported ContentProvider path". Provider
`.ProviderPathsProvider` exported=true, authorities `...evidence`, grantUriPermissions,
overbroad (no path-permission). query()/etc are stubs (return 0/null) in this static APK.

ChallengeActivity (deep link huntress06://provider-paths/unlock) relays query params
answer->proof, case_id to loopback backend:
  http://127.0.0.1:19090/mobile/attempt/d06-23240766b53757eb/evidence
    ?case_id=<case_id>&client_secret=SECRET-FBEDFA27CEEE5486DEE5DD&proof=<answer>
Loopback is device-relative (connection refused from Homebase) — not needed.

Pattern (confirmed days 01-05, HARDENING.md + prior solver NOTES): the proof the app sends =
decoded assets/huntress_puzzle.json, and the backend evidence code EQUALS that value.
So answer = decoded puzzle data.

puzzle.json: {"codec":"hex","data":"414e532d34364132344243444145354336453142"}
hypothesis: hex-decode data | evidence: `echo ..|xxd -r -p` = ANS-46A24BCDAE5C6E1B | result: 16 uppercase hex, matches fmt
