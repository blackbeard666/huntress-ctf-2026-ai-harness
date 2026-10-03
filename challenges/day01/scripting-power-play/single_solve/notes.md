# Power Play — single solve notes
hypothesis | evidence | result
zip is AES, pw infected | 7z -pinfected extracts 3 ps1 | ok
IOCs in base64 JSON descriptor | decoded descriptors in work/ | 14 answers accepted 2026-10-03
collection ATT&CK | T1005/T1560/T1119/T1074/T1074.001 rejected; T1555.003 (Login Data/Cookies) | CORRECT 2026-10-03
2026-10-04 rerun: start.json had been overwritten by an already-solved status reply (no attempt_id) and confirmed.json was deleted | restored both from git HEAD, after checking them against the CORRECT entry in HEAD submissions.jsonl | solver-test ok
resubmit to re-confirm | GM: already_solved (not scored) | n/a
