## Mobile lane: what to extend
Every mobile challenge so far asked one `answer` = `ANS-<16 hex>` from an APK, and on all 15 days it sat in
`assets/huntress_puzzle.json` under a rotating codec. The day's solver calls `lib/android.py`'s `puzzle_candidates`,
`raw_entry_scan` and `dex_strings` (with `decode_payload` / `decode_any`); `extract_answer` chains them. The risk for
the next days is the answer MOVING (UTF-16 strings, resources.arsc, a nested dex/zip in assets, split between dex and
`.so` rodata, AES with a hardcoded key, a computed value). Your target names one such place or encoding: add ONE
bounded branch to the matching lib.android function (pure Python + zipfile/androguard/pycryptodome/lief/unicorn;
no subprocess in the in-window path; < 2 s on a 13 KB-20 MB APK; returns None / [] when absent, never raises).
Never change what an existing path returns for the 15 GM-verified days.

Fixtures: 2+ per target in `tests/data/android_fixtures/<name>.{apk|zip,json}`, the json =
{"entry": "<lib.android function>", "expected": "ANS-<16 hex>", "generator_cmd": "...", "oracle_cmd": "..."} plus one
DECOY ({"decoy": true, "expected": null}: same layout, no valid token / a near-miss). Build each APK/zip with an
INDEPENDENT tool (`zip`, `aapt2 link`, `apktool b`, `python3 -c 'import zipfile ...'`, `openssl enc` for ciphers) and
take `expected` from an independent reader (`unzip -p | strings`, `aapt dump`, `jadx` output, an `openssl enc -d`
one-liner) -- never from lib.android.

## Gate commands
`python3 tests/test_lane_fixtures.py` + every mobile regression case of every day (the harness runs them).
