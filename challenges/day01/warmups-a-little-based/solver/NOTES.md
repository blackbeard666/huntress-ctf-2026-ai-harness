# A Little Based — solver notes
Concept: an encoded text blob; decode fully, the final non-empty line names a slug `word-word-word-NN`.
Single Solve: one base64 layer -> "...submit this exact answer to the Game Master: <slug>".
Solver: BFS over decodings (base64/url-safe, base32, base85/a85, hex, binary, decimal char codes, url-encoding,
gzip/zlib/bz2/lzma/zip, reverse, rot1-25, single-byte XOR on binary layers) until a plain-English text layer's last
non-empty line contains a slug. Routes by question text ("decode"+"blob"/"slug"), artifact name from each question,
handles mastery setN ids and contracts without answer_ids.
Variant axes covered: file names, layer count/order, rot/xor keys. Synthetic case: cases/synthetic-layers.

## Mastery variant axes (added after variant-mastery-12a9038a)
- **Per-line prefix**: blob lines look like `01\t<base64>` (line-number + tab). A `strip-prefix` BFS step removes a short
  `token<TAB>` / `token: ` / `token| ` wrapper from each line before the base64/base32/hex steps.
- **Generic download names**: the GM can serve every set's blob as `blob.txt`, while each question asks for
  `blob-0N.txt`. If the named file is missing, the solver takes the sha256 from `contract["artifacts"]` (matched by
  filename, otherwise by `set` number or question position when filenames repeat) and looks for an artifact-dir file
  with that hash. Case: `synthetic-dupname-prefix` (shuffled question order, de-duplicated file names on disk).
- **Zip bundle**: `warmups-day-01-mastery.zip` holding `blob-01..03.txt` (case `variant-mastery-zip-7e1d370b`).
- HARNESS GAP: for attempt 12a9038a, `hctf artifact` saved only the first of the 3 downloads (all named `blob.txt`),
  so set2/set3 bytes were never fetched and that case can only check set1. The solver is ready once the downloader
  saves every entry in `contract["downloads"]` (under unique names).
- 2026-10-03, attempt 947c5f7c (case `variant-mastery-947c5f7c`): **same harness gap, happened again**. The contract lists 3
  downloads (sha256 348f5a…, 386332…, faf4a2…), all named `blob.txt`. Only 348f5a… (set1) was saved, so set2/set3
  have no bytes on disk. set1 decodes fine (`calm-starfish-petal-16`, GM-accepted). No new decoding axis showed up;
  the solver needs no change. It will answer every set once all downloads are saved (see ../HELP.md).
- 2026-10-03, attempt c9228246 (case `variant-mastery-c9228246`): **same harness gap, third time.** After expiry I fetched
  the set2/set3 bytes from the contract's download capabilities (`gm.py download <cap>`; they still worked, sha256
  matched) and saved them as `blob_2.txt`/`blob_3.txt`. All 3 sets use `01\t<base64>` -> the solver answers all of
  them unchanged (peppy-signal-marble-92 / happy-storm-fern-19 / daring-daisy-onyx-87). No new decoding axis showed up.
  That case now covers the full 3-set "generic duplicate names + per-line prefix" layout. The older cases' links
  now return 404 `artifact_link_unavailable`, so 12a9038a/947c5f7c stay set1-only. Mastery deadline was **30 s**.
- 2026-10-03, attempt 214a48f3 (case `variant-mastery-214a48f3`): **same harness gap, fourth time.** Only set1's bytes were saved.
  I fetched set2/set3 afterwards with `hctf hb exec -- python3 hctf/gm.py download <cap> <dir>` (download only; sha256
  matched) and saved them as `blob_2.txt`/`blob_3.txt`. Same `01\t<base64>` layout. The solver answers all 3 unchanged
  (plucky-garden-pebble-88 / dapper-valley-harbor-16 / lucky-candle-wizard-45). **No new variant axis showed up.**
  Retrying mastery will keep failing the same way until `hctf artifact` saves every contract download (see ../HELP.md).
- 2026-10-03, attempt e274eba9 (case `variant-mastery-e274eba9`): **same harness gap, fifth time.** Only set1's `blob.txt` was saved.
  I fetched set2/set3 afterwards (`hctf hb exec -- python3 hctf/gm.py download <cap> /tmp/...`, then `hb exec -- cat`; sha256
  matched the contract) and saved them as `blob_2.txt`/`blob_3.txt`. Same `01\t<base64>` layout. The solver answers all 3
  unchanged (jazzy-river-quill-51 / eager-valley-badger-24 / dainty-sailor-juniper-99; I checked each by hand with `cut -f2 | base64 -d`).
  **No new variant axis showed up and solve.py was not changed.** The fix belongs in `hctf artifact` (see ../HELP.md).
- 2026-10-03, attempts a2f1456a and 992bc2b9 (cases `variant-mastery-a2f1456a`, `variant-mastery-992bc2b9`): **same harness gap,
  6th and 7th time.** Each contract lists 3 downloads, all named `blob.txt`. `artifacts/latest/manifest.json` has only set1's sha.
  set1 uses the same `01\t<base64>` layout and decodes to calm-scooter-juniper-37 / jovial-stream-coral-89 (both GM-accepted).
  `hctf solver-run warmups-day-01/mastery` answers set1 and leaves set2/set3 missing only because their bytes are not on disk.
  **No variant axis was added. solve.py did not change.** Running more generalize workers will not fix this; see ../HELP.md.
- 2026-10-03, attempt 16aba124 (case `variant-mastery-16aba124`): **same harness gap, 8th time.** Only set1's `blob.txt` was saved.
  I fetched set2/set3 afterwards with `hctf hb exec -- python3 hctf/gm.py download <cap> /tmp/dl-<cap>`, then
  `hctf hb exec -- cat /tmp/dl-<cap>/blob.txt` (`hb exec -- sh -c` returns nothing). All 3 sha256 values matched the contract.
  Same `01\t<base64>` layout: daring-cloud-onyx-66 / plucky-banner-wizard-67 / jovial-island-birch-18. The case now holds all 3 sets.
  **No new variant axis showed up and solve.py did not change.** All 13 cases pass.
  Root cause, read from `hctf/gm.py`: `cmd_artifact` only follows the download capabilities when `op=artifact` returns
  JSON. Here it returns set1's raw bytes, so the other two `downloads` are never fetched. When it does follow them,
  `_save_bytes` overwrites files that share a name.
- 2026-10-03, attempt d0a9befd (case `variant-mastery-d0a9befd`): **same harness gap, 9th time.** Only set1's `blob.txt` was saved.
  I fetched set2/set3 afterwards with `hctf hb exec -- python3 hctf/gm.py download <cap> /tmp/dl-<cap>` + `hb exec -- cat`.
  The sha256 values matched the contract. Same `01\t<base64>` layout: plucky-castle-marble-41 / handy-candle-grove-64 / quiet-piano-laurel-94
  (checked by hand with `cut -f2 | base64 -d`). The case now holds all 3 sets and expected.json is filled in. **No new variant axis showed up
  and solve.py did not change.** All 15 cases pass. `solver-run warmups-day-01/mastery` still has no answers for set2/set3 only because
  their bytes are not in `mastery/artifacts/latest`.
- 2026-10-03, attempt 7e0a60ae (case `variant-mastery-7e0a60ae`): **same harness gap, 10th time.** Only set1's `blob.txt` (ed85976c…) was saved.
  I fetched set2/set3 afterwards with `hctf hb exec -- python3 hctf/gm.py download <cap> /tmp/dl-<cap>` + `hb exec -- cat`.
  The sha256 values matched the contract (7b8dfced…, eac15608…). Same `01\t<base64>` layout: brave-canyon-petal-68 / spry-cloud-pepper-68 /
  daring-canoe-whale-22 (checked by hand with `cut -f2 | base64 -d`). expected.json is filled in. **No new variant axis showed up and
  solve.py did not change.** All 16 cases pass.
- 2026-10-03, attempt 848d1d25 (case `variant-mastery-848d1d25`): **same harness gap, 11th time.** Only set1's `blob.txt` (02bd990e…) was saved.
  I fetched set2/set3 afterwards with `hctf hb exec -- python3 hctf/gm.py download <cap> /tmp/dl-<cap>` + `hb exec -- cat`. The sha256
  values matched the contract (72273aee…, 5354de81…). Same `01\t<base64>` layout: funky-sparrow-willow-21 / jazzy-rocket-brook-58 /
  bright-beacon-ivy-33 (checked by hand with `cut -f2 | base64 -d`). expected.json now holds all 3 sets. **No new variant axis showed up
  and solve.py did not change.** All 17 cases pass. `hctf/gm.py` `cmd_artifact` is still unpatched, so the next mastery retry will fail the same way.
- 2026-10-03, attempt 94269ad2 (case `variant-mastery-94269ad2`): **same harness gap, 12th time.** Only set1's `blob.txt` (f543fbf7…) was saved.
  I fetched set2/set3 afterwards with `hctf hb exec -- python3 hctf/gm.py download <cap> /tmp/dl-<cap>` + `hb exec -- cat`. The sha256
  values matched the contract (33fef888…, 0a5e5f93…). Same `01\t<base64>` layout: gentle-scooter-cocoa-64 / calm-squirrel-wagon-52 /
  merry-cloud-bison-34 (checked by hand with `cut -f2 | base64 -d`). expected.json now holds all 3 sets. **No new variant axis showed up
  and solve.py did not change.** All 18 cases pass. `hctf/gm.py` `cmd_artifact` is still unpatched.
