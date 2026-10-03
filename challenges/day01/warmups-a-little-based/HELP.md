# HELP: warmups-day-01 mastery fails because of the artifact downloader, not the solver

**Symptom:** "solver did not produce all answers". Mastery attempts 12a9038a, 947c5f7c, c9228246, 214a48f3, e274eba9, a2f1456a, 992bc2b9, 16aba124, d0a9befd, 7e0a60ae, 848d1d25 and 94269ad2 got answers for set1 only (12 attempts in a row). The orchestrator keeps starting solver-hardening workers for this. Those runs can't help, because the solver is not what's failing. The deadline is 30 s, so this has to be fixed in the downloader.

**Cause:** the mastery contract lists 3 entries in `downloads`/`artifacts`, and each one is named `blob.txt` (only the
sha256 values differ). `hctf artifact` saves just one file (`artifacts/<ts>/manifest.json` lists a single `blob.txt`,
sha256 = the set1 entry). set2/set3 bytes never reach the disk, so no solver can answer them.

**Fix needed in the harness (outside this challenge folder, so I didn't change it):**
1. `hctf/gm.py` `cmd_artifact`: when the start contract has `downloads`/`artifacts`, fetch **every** capability
   (`op=download`), not only what `op=artifact` returns.
2. `_save_bytes`: don't overwrite on a name clash. Save as `blob.txt`, `blob_2.txt`, ... or name the file after its
   sha256 prefix. The solver already matches files by the contract's `sha256` (`artifact_sha` / `find_artifact`)
   and handles de-duplicated names (case `synthetic-dupname-prefix`).
3. `hctf/cli.py` `c_artifact`: only warn on a sha mismatch when `len(manifest) == 1`. It should also check that the
   manifest covers every `artifacts[].sha256` in the contract.

**Solver status:** `hctf solver-test warmups-day-01` passes all 18 cases. Cases variant-mastery-c9228246, -214a48f3, -e274eba9, -16aba124, -d0a9befd, -7e0a60ae, -848d1d25 and -94269ad2 hold all 3 real sets (the set2/set3 bytes were fetched after expiry via `gm.py download <capability>`), and the solver answers all 3 when the bytes are present. `hctf solver-run warmups-day-01/mastery`
answers set1 and reports set2/set3 missing only because their bytes are not on disk.

**Smallest fix (in `hctf/cli.py` `c_artifact`, after the `artifact` call):** for each `start.json["artifacts"]` entry
whose `sha256` is not in `env["saved"]`, run `call(a.id, "download", <last path segment of entry["download"]>, rdir)`.
Then save to a unique name such as `<sha256[:12]>-blob.txt`, or make `gm._save_bytes` add `_2`, `_3` on a name clash.
The solver finds files by sha256, so it does not care about the names. Note: `gm.cmd_artifact` already accepts `--delivery N`,
which may select set N directly.

**Exact bug (hctf/gm.py):** `cmd_artifact` follows the capability links only when `op=artifact` returns JSON (lines ~93-99).
For mastery it returns set1's raw bytes (line 100), so `downloads[1:]` are never fetched. Fix: after the artifact call, run
`cmd_download(<last path segment>, outdir)` for every `start.json["downloads"]` entry whose sha256 hasn't been saved yet,
and have `_save_bytes` add `_2`, `_3` to the name on a clash.
