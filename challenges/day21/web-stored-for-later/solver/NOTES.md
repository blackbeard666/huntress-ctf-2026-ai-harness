# Stored for Later (web D07, stored XSS) -- solver notes

## Derived answers
- compound-live-web-stay-in-your-directory-676f62da (D04 LFI target, `/run/huntress/objective.txt`):
  `proof-1 = proof_1465f13420af477c8bd8214ac7bd08a4` (re-derived live via the D04 solver's LFI probe; matches expected).

## Fix (compound timeout)
- `fallback()` called the sibling day-21 solvers' `fallback()`, and `web-session-impression`'s fallback calls back
  into this one -> unbounded mutual recursion -> timeout. Now: each earlier solver's `answer()` only, D04
  (`day20/web-stay-in-your-directory`, which runs every D01-D04 probe ordered by prompt wording) first.
- Speed: `answer()` (XSS) and `fallback()` (earlier-day probes) run in two threads; answer()'s value wins.
  `main()` `os._exit(0)`s after printing so a still-probing thread doesn't hold the process. LFI compound: 7.8 s -> 3.0 s.

VARIANT AXIS: Mastery/TT compounding put an earlier day's concept (D04 LFI viewer) on the target instead of today's XSS board; rule: on no XSS routes, run the earlier web solvers' answer() (D04 first, it chains D01-D04) concurrently with today's probe -- never their fallback() (the day-21 solvers' fallbacks import each other).

## Proposed lib additions
- `lib.web.compound_probe(question, contract)`: one shared, non-recursive chain of every earlier web day's probe
  (D01 backup, D02 IDOR, D03 SQLi, D04 LFI, D05 access control, D06 reflected XSS, D07 stored XSS) so the day solvers
  stop importing each other's `fallback()` (cycle stored-for-later <-> session-impression).
