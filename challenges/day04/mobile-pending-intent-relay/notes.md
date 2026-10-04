# Pending Intent Relay — notes

hypothesis | evidence | result
- Deep-link ChallengeActivity builds backend request | droidasc getclass: GET http://127.0.0.1:19090/mobile/attempt/d04-.../evidence?case_id=&client_secret=SECRET-...&proof=<answer> | proof is the real answer
- proof value is the decoded puzzle asset | assets/huntress_puzzle.json {codec:xor, data:b64, key:29}; b64-decode then xor 29 -> ANS-60A1CA8E89978462 | matches ANS-+16hex format
- backend 127.0.0.1:19090 unreachable on Homebase (device loopback) | hctf hb exec curl -> connection refused | answer = decoded puzzle value, not a live fetch
- submit ANS-60A1CA8E89978462 | hctf submit | CORRECT (flag a484034bd3152e0dffa08f4fe97797d3)

Variant axes: package suffix, case ref, APK filename, codec (xor/base64/hex/rot13/reverse/plain), xor key, mastery sets.
