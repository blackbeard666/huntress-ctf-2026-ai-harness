# Mastery compounding — what the organizers want, what Days 1-8 did, how the harness prepares

**Organizer signal (Day 8):** "Is Mastery Mode doing what it is supposed to be doing? Is there at least one new
'compounding' concept from some days past, and still Single Solve presents something new?" Read as the intended design:
**Single = today's new concept; Mastery = today's concept compounded with at least one concept from days past.**
Expect Mastery to start doing that in every lane — possibly with questions/artifacts that never appear in today's Single,
and with earlier-day artifacts mutated.

## Audit of Days 1-8 (contracts on disk, 2026-10-08)
Common to every lane/day: the TT and Mastery question lists equal that day's Single (modulo `setN.` and renamed
deliveries) — Mastery never asked anything the Single didn't. Compounding, where it exists, lives in the bytes or in the
Single itself.

| Lane | Single new each day? | Mastery shape | Earlier days in Mastery | Verdict |
|---|---|---|---|---|
| warmups | yes (base64, rot13, hex, binary, decimal, octal, %XX, &#NN;) | (5N-2) sets x 1, each blob = N lines, line k = Day k's encoding, fresh text | all earlier days, every set | **compounds as designed** |
| metadata | yes (D8 extends D7's ZIP concept, keeps `d07-` id) | D2-7: 2 x today's 1 field; D8: 5 x 12 | none D2-7; D8 carries D1-7 with byte-identical answers | missing → weak |
| script-analysis | yes (+1 language/host per day) | 2 x Single (D8: 5 x 615) | inside the Single (cumulative files, values change day to day) | weak: Mastery = N x Single |
| binary-RE | yes container, but D4-8 ask the same config fields; D7 Kotlin ≈ D6 Java | 2 x Single (D8: 5 x 80) | inside the Single; earlier ELFs identical in every Single, small variant pool in Mastery (D8: a stripped d01 ELF) | weak: Mastery = N x Single |
| mobile | yes theme, but D8 encoding `reverse` repeats D2 | 3 x 1 (D8: 5 x 1), same manifest/encoding, only key/case id change | none ever | missing |

## Harness preparation (2026-10-08)
- **Compounding probe** (`hctf/compound.py`, `hctf compound-check <id>|--day N`, orchestrator `_start_compound_pre`):
  replays the single's solver on every EARLIER day's GM-verified cases of the lane (single + newest TT/Mastery case per
  day). Hard misses → `compound-dKK-*` regression cases + one generalize BEFORE Mastery (runs beside the first TT).
  Soft = a case answered with nothing at all (retired id scheme, e.g. binary D1/D2 before the D3 `d01_*` rename).
- **Mastery delta** (`orchestrate.mastery_delta`): status-time TT/Mastery contracts vs today's Single — question ids
  and artifact kinds the Single never asks go into the Single worker's prompt (positive control: D7 metadata replay
  contract → 10 earlier-day ids + .jpg/.pdf/.png/.txt).
- **Guidance**: single.md, generalize.md, solver-authoring skill: "Mastery compounds; never assume Mastery = N x Single;
  absent-by-design → answer per the question".
- **Baseline** `hctf compound-check --day 8` (2026-10-08): metadata 17/17, mobile 15/15, script 19/19, warmups 19/19
  earlier-day cases fully right; binary 14/19 — the 5 misses are D1/D2 cases under the retired id scheme (soft, 0
  answered). Today's solvers still know every earlier concept.
- Not covered yet: earlier concepts LAYERED inside one artifact (e.g. a mobile payload encoded with D3 base64 then D7
  caesar) — the probe replays earlier cases as they were, it does not synthesize combinations.
