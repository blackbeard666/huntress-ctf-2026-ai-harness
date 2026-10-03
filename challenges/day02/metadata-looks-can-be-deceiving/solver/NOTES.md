# Looks Can Be Deceiving (day02 metadata)
Concept: report the first N (16) bytes of a named zip member as lowercase hex — the true magic, regardless of extension.
Variant axes handled: archive/member names (via lib.common.find_artifact, nested zips, passwords), N parsed from
question/syntax/answer-id, mastery set prefixes, question order/subsets. Also answers size/md5/sha1/sha256 if asked.
- Stale question text (variant-time_trial-d8dfe119): the contract's `questions[].id/artifact` named `roster.csv` but
  `answer_ids` said `readme-executable-...` and the zip only held `readme.exe`. When the named member is missing, the
  solver falls back (lib.common.find_artifact_hinted) to the archive member best matching the answer-id stem
  (token-prefix match, exe~executable), or the only member. Always answer under `answer_ids`, trust the bytes.
- Cases: pruned 5 duplicate unverified captures from expired time-trial retries (same artifact sha as kept cases).
  `variant-time_trial-1b2941f2` (roster.csv, zip sha cb06ac9e…) expected = `head -c16 roster.csv | xxd -p` from an
  independent unzip — derived from bytes, NOT GM-confirmed (every time-trial submit returned `expired`).
- Mastery bundle wrapper (variant-mastery-f9182e51): the GM shipped ONE download named after set1's container
  (`metadata-day-02-evidence-01.zip`) that actually holds both per-set zips (`...-01.zip`, `...-02.zip`), each holding
  its member. The old lookup matched the same-named outer zip, failed to find the member, and the hinted fallback
  returned the inner zip's bytes (PK header) as the answer. Fixed in `lib.common.find_artifact`: if a same-named
  container lacks the member it keeps looking, recursively walking zip members (`iter_entries`, depth 4) and preferring
  a `member` whose parent zip is the named container. Expected values from an independent `unzip` + `head -c16 | xxd -p`
  (unverified by GM: the 5 s mastery deadline expired).
