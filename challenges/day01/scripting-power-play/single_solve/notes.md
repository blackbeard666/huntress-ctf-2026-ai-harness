# Power Play — single_solve notes
hypothesis | evidence | result
artifact file "evidence.zip -> resource-sample.ps1" is a zip | python zipfile lists 3 ps1, AES (compress_type 99) | yes
7z with no password | "Break signaled", empty file | dead end
password = "infected" (standard sample convention) | 7z x -pinfected ok | extracted 3 ps1
each ps1: FromBase64String('<json>') -> descriptor record | base64 -d | JSON with URL/wallet/mutex/etc
resource: Diagnostics.Process+Registry+WebClient, wallet_ + pool URL | resource_hijacking / T1496 | submitted
collection: IO.File, ZipFile, HttpWebRequest, Login Data/Cookies, stage-*.zip | synthetic_collection / T1005? | submitted
impact: Aes, DirectoryInfo, .locked-*, RECOVERY-*.txt | synthetic_impact / T1486 | submitted
mutex = value matching Global\\HuntressLab_* (JSON-unescaped to single backslash)
collection-attack = T1005 | Data from Local System | INCORRECT
collection-attack = T1560 | ZipFile + stage-*.zip, base IDs used for the others | INCORRECT
collection-attack = T1119 | Collection-tactic trio leftover | INCORRECT (cap reached) -> HELP.md
solver written; solver-test ok; synthetic XOR/AES/evidence-02 variant ok
re-derive collection-attack (2026-10-03, run 3) | JSON d = "stage-e536c782dd01.zip" (staging archive), c = [update-*.dat, "Login Data", "Cookies"], native IO.File+ZipFile+HttpWebRequest | best remaining candidate T1074 (Data Staged), alternates T1555.003 / T1539 / T1041 -- NOT submitted, local cap 3/3 reached
