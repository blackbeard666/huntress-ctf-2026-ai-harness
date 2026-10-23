# Day 23 post-mortem (2026-10-23) — why 28:55 when leaders took ~5 min

Run: 24/24 GM-CORRECT (5 regular lanes + 3 web), $25.49. Regular board 14/15 at T+16:10, 15/15 at T+28:55; web 9/9 at
T+7:21. Leaders' per-attempt HoF times: script TT 0.7 s / Mastery 2.1 s — their solvers pass the variants first try.

## Where the time went (T+ from the 21:00:13 release)

| Lane | Done | Main cost |
|---|---|---|
| script-analysis | 28:55 | ~17 min of harness waste (below) + ~6 min learning a variant reactively |
| metadata | 6:42 | TT: one list field, live worker spent 4 min on forensics before trying `sorted`; Mastery: Python repr sent for a json field |
| mobile | 5:18 | reused solver submitted a decoy; live answer; **58 s** between the live pass and Mastery's start |
| warmups | 4:01 | Mastery 113 `message` fields wrong -> ~110 s generalize |
| binary | 3:28 | first try; reuse race 46.6 s (35-92 s at the drop vs 1.7 s idle), downloads 24 s + 34 s |

Script critical path: single 1:13 -> TT attempt 1:38-3:36 (593 answered, 902 empty; 100 s partial-submit bisect) ->
generalize #1 died `prompt_too_long` (1.39M tokens: six timed-out Mastery cases' full diffs, 2.6 MB) -> TT re-run on
the unchanged solver (100 s re-bisect) -> generalize #2 8:14-12:14 -> 4 `batch-*-style` wrong -> 82 s of one-word
label probes -> live answer 14:07-15:51. Mastery 16:23: 18 wrong -> ~10 min of one-word probes (~10 s per GM submit
on a 10465-field attempt) -> unblocked by hand at ~27:47 -> the harness noticed at 28:55 (55 s generalize prep + 22 s
replay after CORRECT).

The status-time 409 `start_required` reply at T+0:03-0:21 already carried the FULL TT + Mastery question lists —
verified identical to the real attempts (1495/1495 and 10465/10465 ids + text + artifact). The TT had switched to
per-file ids (`polyglot-*`, 664 of the 902 empty); the new-id check saw "11960 new timed ids" at T+1:29, its dry run
timed out (12 s) and it did nothing.

## Fixes (branch d23-fixes; `tests/test_d23_postmortem.py`)

| # | Fix | Where | Flag (default) |
|---|---|---|---|
| 1a | Online label resolve skips composite `a|b|c` labels and wrong-arity seeds; all fields probed in parallel; whole step time-bounded | `timed.resolve_labels_online`, `labels.probe_first(deadline=)` | `HCTF_LABEL_ONLINE_MAX_S` (30), `HCTF_LABEL_ONLINE_CONC` (6) |
| 1b | Live answer starts at the block, beside the online resolution (was after it) | `orchestrate.timed_stage` | `HCTF_LIVE_FIRST` (1) |
| 1d | Generalize prompt bounded: per-case diff (12 fields + count; replay timeouts named, not dumped), problem list, wrong-field lines, evidence (and its field list) | `orchestrate._case_problem`, `_cap_lines` | `HCTF_PROB_DIFF_FIELDS` (12), `HCTF_PROBS_MAX_CHARS` (40000), `HCTF_EVIDENCE_MAX_CHARS` (60000), `HCTF_EVIDENCE_MAX_FIELDS` (120) |
| 1e | Never re-run an open untimed attempt on a solver the generalize left byte-identical (also after an early generalize) | `timed_stage`, `_early_join` | `HCTF_SKIP_UNCHANGED_RERUN` (1) |
| 1f | Live pass: no generalize prep / workers when already CORRECT; unchanged code -> no replay; Mastery -> pre-worker solver kept, edits in `.generalize-unjudged/`; TT -> Mastery pre-start first, then a short-timeout replay; Mastery pre-start on every live/online TT pass | `generalize`, `_accept_after_live`, `_live_pass_prefetch` | `HCTF_FAST_LIVE_ACCEPT` (1) |
| 1g | Web Mastery: the compound-check wait ends when the target is ready (polled while `preparing`) | `_web_mastery_kick`, `_await_probes(ready=)` | `HCTF_WEB_READY_POLL` (5), `HCTF_WEB_READY_POLL_MAX` (600) |
| 2 | Contract-ahead: the runner's mid-attempt "solved" event now reaches the orchestrator on LOCAL runs (event file + poller) and on untimed pools; a solver gap of >= 25 empty fields (or a status-time contract with >= 25 ids new to the lane) starts the generalize at once, beside the attempt's banking/localization | `hb_timed._event`, `workers._local_event_poller`, `_early_kw`, `_early_event`, `_ahead_new` | `HCTF_AUTO_EARLY` (1), `HCTF_EARLY_MIN_MISSING` (25), `HCTF_AHEAD_MIN_NEW` (25) |
| 3a | List-order alternates (sorted / reversed / deduped, compact JSON or the value's own separator) probed in parallel for every rejected list field before any LLM | `timed.list_alternates`, `resolve_format_alternates` | `HCTF_FORMAT_ALT_MAX_S` (20) |
| 3b | `answer_format.kind == "json"` + a Python literal -> compact JSON (cli + timed runner); solver list/dict output rendered as compact JSON, never `str()` repr | `cli._json_coerce`, `hb_timed._json_coerce`, `solvers.answer_str`, `hb_timed._answer_str` | — |
| 4a | Resource sampler: `[res]` line every 10 s for 10 min after the release (mem available, PSI mem/cpu, cgroup `high` events, `claude` count + RSS), peaks at the end | `hctf/ressample.py` | `HCTF_RES_SAMPLE` (1) |
| 4b | A reconnect to the same open attempt does not resubmit values the GM already rejected there (banked `rejected`); they still reach the orchestrator as `partial_wrong` | `hb_timed._bank_save`, `_bank_rejected` | `HCTF_BANK_OVERLAY` (1) |
| 4c | Knowledge: ZIP CD names SORTED + Mach-O cpu set ascending (the D23 ratchet already wrote these); script batch `-style` triple's expansion `call_double` for `call set` over `%%frag%%`; per-set handoff ids | `lib/knowledge.py`, D23 solver | — |

## Open / not changed

- Drop-time contention: 25 LLM workers in the first ~2 min on a 7.8 GB WSL host inside a 6.5 GB MemoryHigh unit;
  the duel guard saw < 1.5 GB available at T+0:38. 4a measures it next run. If confirmed, the fix is host-side
  (more WSL memory via `.wslconfig`) or fewer concurrent drop-time workers — a user decision.
- The 100 s first-attempt bisect of a high-wrong-rate partial submit is GM-bound (~2-10 s per submit on large
  attempts); with #2 it no longer sits in front of the generalize.
- Feed: a generalize accepted after a live pass stays listed under "working" (cosmetic).

## Validation

- `tests/test_d23_postmortem.py`: 48 checks, offline.
- Full suite on the branch vs a pristine `ac4f216e` baseline: see the commit message.
- Not yet measured end-to-end: needs a D23 replay (hctf/replay_gm.py) or the next live day.
