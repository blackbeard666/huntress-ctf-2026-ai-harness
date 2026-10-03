- day02 variant-time_trial-* expected.json: derived from the bytes (independent `tr` ROT13 → "…submit this exact answer to the Game Master: <slug>"), NOT GM-confirmed — every TT submit for these attempts returned `expired` (5 s clock).

## Variant axes handled
- **Mastery bundle disguised as a member (7957bbae):** the single download is a ZIP saved as `blob-01.txt` holding
  `blob-01..08.txt` (one per set). `find_artifact` now opens any file with `PK\x03\x04` magic (any extension, nested
  zips too) and prefers the exact inner member over an outer same-named container; sha256 fallback also checks members.
- **Per-line mixed encodings, split message:** each blob is numbered lines `NN<TAB>payload`; line 1 is base64, line 2
  ROT13, and the decoded fragments are concatenated verbatim (split mid-word, e.g. `…submit this e` + `xact answer…`;
  a leading space on a payload is significant). `per_line()` strips the number prefix, picks each line's most
  English-looking decoding (BFS depth 3 over all one-step decoders), joins with "" and is offered as a BFS candidate.
  Order of encodings per line is not assumed (tested with rot13 first / base64 slug line last).
- Mastery expected.json derived from the bytes (not GM-confirmed).
