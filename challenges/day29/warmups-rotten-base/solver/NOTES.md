# warmups-day-25 "You Have a Point" -- solver notes

Concept: Unicode code points `U+XXXX` per character (single/TT: whole blob; Mastery: line 25).

## variant-mastery-0b1ae1d0 (re-derived from the bytes)
Mastery blobs have 25 numbered lines; line 25 = `U+006C U+0065 U+002D U+0035 U+0032` -> `le-52`. Decoding lines 1-24
with their day codecs + line 25 as code points gives e.g. set1 `hearty-meadow-maple-52`, set2 `droll-blanket-copper-77`,
set3 `cozy-meadow-ripple-57` (the solver had emitted `-07`/`-22`/`-02`: GM-rejected).
Cause: `_uplus_lines` pre-decoded line 25 to plain text, then `decode._positional` treated the last line (no day-25
codec registered) as an unknown codec and "re-decoded" plain `le-52` via `_unknown_line_cands` -> wrong digits.
Same bug class as D23's `_a85_lines`. Fix: in Mastery, leave line 25 raw and register `uplus` as day-25 free codec.

VARIANT AXIS: Mastery grew to 25 lines (line 25 = U+XXXX code points); a pre-decoded plain last line gets mangled by the positional unknown-last-line path -> never pre-decode Mastery lines, register each new day's codec via `decode.register_free(name, day, fn)` so `_positional` decodes line k with day k's codec.

## Generalize 2026-10-25 (variant-mastery-{0b1ae1d0,664b2505,d271467d,f9ac3fc4})
- Each `variant-mastery-<id>` has byte-identical artifacts and identical questions to `auto-mastery-<id>`, whose
  expected.json is fully GM-verified (123/103/113/83 fields). The current solve.py reproduces 100% of those verified values and
  outputs none of the gm_feedback-rejected ones (e.g. set1 `hearty-meadow-maple-07` rejected -> verified `-52`). That failure came
  from an older solver (positional pre-decode of line 25), and it was already fixed. These cases still show
  `unverified` only because their expected.json is empty.
- Speed: solve.py takes 0.10 s on single_solve and 0.3-0.9 s per 83-123-set Mastery case. The 4.25 s / 13 s timings are
  `hctf solver-run` CLI overhead, not the solver.
VARIANT AXIS: none new -- the 4 variant-mastery cases are the same attempts as auto-mastery-* (same sha256); the line-25
  `U+XXXX` code-point fragment is decoded by the registered day-25 codec (`_uplus`, 2-8 hex digits, u+/\\u/%u/0x forms), not pre-decoded.

## Proposed lib additions
- `lib/warmups_codecs.DAYS[25]` / `decode.register_free("uplus", 25, ...)`: code-point tokens
  `(?:U\+|u\+|\\u|\\U|%u|0x)[0-9A-Fa-f]{2,8}` separated by whitespace/`,;` -> `chr(int(h,16))` (see solve.py `_uplus`).
- `decode._positional`: when the last line's unknown-codec candidates include the fragment itself verbatim (already
  plain text), prefer it -- would have avoided both the D23 and D25 pre-decode traps.

## Generalize 2026-10-28 (compound-d27-single_solve)
- The case's `artifacts/blob.txt` was the WRONG bytes: sha256 `7a556d5e...` = Day 26's Brainfuck blob (decodes to D26's
  verified `happy-comet-blossom-79`), while its contract declares `5b3672622a...` (33929-byte Ook! blob). The correct
  bytes are `challenges/day27/warmups-monkey-business/single_solve/artifacts/latest/blob.txt`; the unchanged solver decodes
  them (Ook! -> Brainfuck -> text) to the GM-verified `hearty-castle-fern-71` in 0.2 s. Fix = case data only: copied the
  sha-matching blob into the case; no solve.py change. Day 27's own `solver/cases/single_solve` has the same wrong blob
  (outside this folder -- not touched).
VARIANT AXIS: none -- the compound-d27 failure was a case-construction bug (an earlier day's blob saved under D27's contract); always check `sha256(artifact) == contract.artifacts[].sha256` before debugging a compound case.

## Proposed lib additions (2026-10-28)
- Case builder / `hctf solver-test`: verify each case artifact's sha256 against `contract.artifacts[].sha256` and flag a
  mismatch as a CASE error, not a solver diff. day27/warmups-monkey-business/solver/cases/single_solve/artifacts/blob.txt
  needs replacing with day27 single_solve/artifacts/latest/blob.txt (sha 5b3672...).

## Generalize 2026-10-28 #2 (compound-d27-single_solve again)
- Same case-data bug came back: `hctf/compound.py adopt()` re-copies the case from
  `day27/warmups-monkey-business/solver/cases/single_solve`, whose `artifacts/blob.txt` is still Day 26's Brainfuck blob
  (sha 7a556d5e..., = day26 single_solve blob -> `happy-comet-blossom-79`) under D27's contract (declares 5b3672622a...).
  Replaced the local copy (rm + cp to break the hardlink to .generalize-snapshot) with the sha-matching
  `day27/.../single_solve/artifacts/latest/blob.txt`; the unchanged solver gives the GM-verified `hearty-castle-fern-71`.
  No solve.py change; full `hctf solver-test` passes every verified case.
VARIANT AXIS: none -- compound-d27 is a broken SOURCE case (wrong-sha artifact); the bytes cannot yield the expected answer, so no solver change can fix it.
- ACTION NEEDED (outside this folder, not touched): copy `challenges/day27/warmups-monkey-business/single_solve/artifacts/latest/blob.txt`
  over `challenges/day27/warmups-monkey-business/solver/cases/single_solve/artifacts/blob.txt`, or the next adopt() reintroduces it.
- Proposed: `compound.adopt()` / `solver-test` should check each case artifact's sha256 against `contract.artifacts[].sha256` and skip/flag a mismatch as a case error.
