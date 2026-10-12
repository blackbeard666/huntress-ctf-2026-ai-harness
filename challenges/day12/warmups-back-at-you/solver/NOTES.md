VARIANT AXIS: Mastery line 12 is a PLAIN reversed fragment (`69-enud-m` -> `m-dune-96`); the solver's reversed-then-decoded candidate (decode_chunk rot-N-shifts it to `d-ulev-96`) out-scored it on bigrams in 11/58 sets. Rule: rank reversal readings by priority (raw reversed > decoded-then-reversed > reversed-then-decoded), bigram score only breaks ties within a priority.

## Proposed lib additions
- `lib.decode.decode_chunk`: never apply rot-N to a fragment that already reads as plain slug text (lowercase words/digits/hyphens), or expose a "reversed" reading ahead of rot-N for day-12 style fragments.
