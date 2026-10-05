# Hatch Careful single solve notes
hypothesis | evidence | result
- cumulative bundle: Day 1-4 PS/JS/Batch/VBS + 14 Python fixtures | zip listing (45 members, AES pw infected) | yes
- reuse day04 solver for old lanes | 231 non-python answers submitted at once | accepted, 0 wrong
- python plan = decode_(load_(MATERIAL)) as k=v pipe text | sandboxed AST loader and CODEC decoder agree on all 14 | yes
- plan values verbatim are the labels (adapter/campaign/syntax/obfuscation/carrier/windows_chain/indicators) | 98 submitted | accepted
- roles: benign/dropper/stager/downloader/uploader/impact from steps | submitted | accepted
- launcher attack = T1059.006 (Python interpreter) | submitted | accepted
- dispatch_next_stage graph (zipapp, embedded-runtime) = relay, T1059.006 | submitted | accepted
- 5-step profile_host..dispatch_process (py2exe-service, pyarmor-pyinstaller) = staged_chain, T1059.006 | submitted | CORRECT (flag received)
