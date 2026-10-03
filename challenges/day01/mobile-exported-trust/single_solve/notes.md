# Exported Trust — single solve

hypothesis: exported deep-link Activity builds the backend evidence request | evidence: droidasc getmanifest shows .ChallengeActivity exported=true, intent-filter VIEW+BROWSABLE scheme=huntress01 host=exported-trust pathPrefix=/unlock | result: confirmed
hypothesis: handler attaches embedded credential + proof | evidence: ChallengeActivity.onCreate builds http://127.0.0.1:19090/mobile/attempt/d01-ec1629b73a8465b3/evidence?case_id=<>&client_secret=SECRET-A8614359B0F872F166A024&proof=<answer> | result: confirmed
hypothesis: proof value = assets/huntress_puzzle.json data | evidence: {"codec":"plain","data":"ANS-DACC86F43B0B1C1A"}; backend is on-device 127.0.0.1 (unreachable from Homebase) so evidence code == proof | result: CORRECT
hypothesis: backend reachable via hctf hb exec curl | evidence: curl 127.0.0.1:19090 -> connection refused (loopback only on device) | result: dead end; answer is static puzzle data

## RESULT: CORRECT — ANS-DACC86F43B0B1C1A
