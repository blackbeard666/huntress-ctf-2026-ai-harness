# Hex Appeal (warmups-day-03) solver notes

## Variant axes covered
- **single_solve**: one hex blob -> English sentence; the slug is at the end.
- **mastery 13-set, mixed encoding per line** (variant-mastery-7251cf01): each blob has numbered lines `NN<TAB>payload`.
  Each line uses its own encoding (base64 / rot13 / hex), and the lines are pieces of ONE sentence split mid-word.
  Decode every payload and join them as-is (trailing spaces on a payload matter). All sets ship as `blob.txt`;
  the solver matches each set to its file by the contract's `artifacts[].sha256`.
  - Fast path `fast_per_line`/`strict_line`: strict hex, then strict base64 (applied again if the result is
    still encoded), otherwise the rot-N with the best English score. This takes about 0.2s for all 13 sets.
  - Bug fixed: `english()` counted single letters, and hex strings are full of "a", so the hex line was
    scored as English and never decoded. The BFS took about 32s per blob and still found no slug, which
    caused the live timeout. `english()` now only counts words of 2+ letters.
  - The fallback `peel` BFS now stops after 0.6s per question, so one bad blob cannot use up the whole
    mastery clock.
