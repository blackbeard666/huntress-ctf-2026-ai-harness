# Expansion Pack solver notes

## Variant axes handled
- **Fragment variable names ending in a digit** (time_trial fde517bd, `impact-plan.cmd`): the fragments were
  `item0..item3`, joined as `set "item9=%item0%%item1%%item2%%item3%"` inside a `for /l ... do call :LABEL`
  subroutine. `Batch.percent` used to read `%item0` as a batch argument (`%~?[a-z]*[0-9]`), which mangled the join.
  The plan never parsed and adapter/campaign/note_name/graph came back empty; role/attack fell back to
  benign_utility/none. Fixed: only `%N`, `%~<mods>N` and `%*` are arguments, as in cmd.
- **`HUNTRESS-CODEC: base64_literal|add_N`** material: `decode_material` now also tries subtracting a constant
  (the key comes from the known `v` prefix). This is only a fallback/cross-check.
- Mixed CRLF/LF lines and mixed-case `SeT` were already handled.

## Control vocabulary
- `set "X=1"` + `if defined X <stmt>` = `if_guard`. This was confirmed on 2026-10-04 (`lib/knowledge.py` BATCH_CONTROL_VOCAB).

## Mastery 8fc12060: clock, not answers (2026-10-04)
- Shape: one download, `evidence-01.zip` (outer bundle), holding AES inner `evidence-01.zip` + `evidence-02.zip`. That's
  2 sets × 159 = 318 answer_ids. Set N is read from inner `evidence-0N.zip`; the per-set values were checked by hand
  (set 1 vs set 2 relay `.cmd`, set 2 resource `.ps1` base64 JSON, set 2 relay `.js` rolling-XOR plan).
- The Mastery clock is **7 s** (started_at → deadline). The GM log shows start 07:24:49.9 → download saved 07:24:55. The
  answers never got submitted in time, so the per-field probe had nothing to judge (`probed: 0`).
- Solver fix: `find_member` called `lib.common.find_artifact` 42 times. Each call re-walked the nested zips and
  re-decrypted every AES member (903 PBKDF2 runs, ~1.3 s). Now the tree is walked once (`_indexed`), and only a
  **unique** (container, member) hit is used. Same-named per-set downloads still go through `container_by_sha`.
  `lib.common.iter_entries` also memoizes each loader. Solve time: 1.04 s → 0.2 s, output unchanged.
- The remaining budget is GM transport (start + download + submit ≈ 2.7 s/call on the public GM). The solver can't
  shrink that; it's an `hb_timed` / transport question for the orchestrator.
