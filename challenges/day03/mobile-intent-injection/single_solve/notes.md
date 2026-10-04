# Notes: Day 03 mobile Intent Injection (single_solve)
hypothesis | evidence | result
- Same app shape as Day 01/02 (exported deep link -> loopback evidence endpoint, proof = puzzle asset) | manifest: exported .ChallengeActivity huntress03://intent-injection/unlock; mechanic "attacker-controlled nested Intent"; dex: getStringExtra answer/case_id, http://127.0.0.1:19090/mobile/attempt/d03-.../evidence?case_id=..&client_secret=SECRET-..&proof= | confirmed
- answer = base64-decoded assets/huntress_puzzle.json data | QU5TLUU0QzhFMzVBOEE5QjVENjc= -> ANS-E4C8E35A8A9B5D67 | CORRECT (exit 0)
- Backend never called: loopback 127.0.0.1 endpoint not reachable from outside the device; GM confirmed puzzle value directly.
