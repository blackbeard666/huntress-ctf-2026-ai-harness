# Looks Can Be Deceiving (day02 metadata)
Concept: report the first N (16) bytes of a named zip member as lowercase hex — the true magic, regardless of extension.
Variant axes handled: archive/member names (via lib.common.find_artifact, nested zips, passwords), N parsed from
question/syntax/answer-id, mastery set prefixes, question order/subsets. Also answers size/md5/sha1/sha256 if asked.
- Stale question text (variant-time_trial-d8dfe119): the contract's `questions[].id/artifact` named `roster.csv` but
  `answer_ids` said `readme-executable-...` and the zip only held `readme.exe`. When the named member is missing, the
  solver falls back (lib.common.find_artifact_hinted) to the archive member best matching the answer-id stem
  (token-prefix match, exe~executable), or the only member. Always answer under `answer_ids`, trust the bytes.
