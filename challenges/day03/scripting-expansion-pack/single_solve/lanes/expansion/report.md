# Expansion-form lane report (batch-*-expansion)

## Bottom line
1. **Non-FOR assembly gives `delayed`.** If the echoed variable is not built in a `for ... do` loop, answer `delayed`. This
   matches 7/7 GM verdicts (memory, remote, impact = percent join; embedded, staged = `call set %%` join;
   outbound, relay = `!x!` join) and every rejection: percent x2, call_double x2, call-double, double_call, immediate.
   Reading: the form is how the final handoff reads the value, i.e. `echo(!var!)` under EnableDelayedExpansion. The
   join line is only assembly. (confidence: high on this data)
2. **FOR assembly gives `for_indirect` or `call_double`. Nothing in the bytes can tell these apart semantically.**
   host-context gives for_indirect. local-dispatch gives call_double (for_indirect and delayed were rejected).
   Data-fitting tie-breaks, in my order of preference (confidence: low, about 50/50):
   a. Accumulator reset is unconditional (`set "T="`) gives for_indirect. Reset under `if defined X set "T="` gives
      call_double.
   b. Multi-char fragment prefix (`%%fragment%%G%%`) gives for_indirect. Single-letter prefix (`%%h%%G%%`) gives
      call_double.
   c. Role: benign gives for_indirect, launcher gives call_double. Both plans have `adapter=call`.
   d. Codec base64_literal|identity vs decimal_bytes|reverse (probably coincidence).
   In a timed run, submit the (a) choice and flip to the other value if it comes back incorrect.

## Why no semantic rule over the join line works (real cmd.exe phase analysis)
- host-context: `for %%G in (0 1 2 3) do call set "T=%%T%%%%fragment%%G%%"`
  local-dispatch: `for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"`
  - Phase 1 (`%%` becomes `%`): `%T%%fragment%G%` / `%cfg%%h%G%`.
  - Phase 4: only `G` is an active FOR variable. There is no `~`, so no modifiers apply. `%c`, `%h`, `%f`, `%r` stay
    literal. Result: `%T%%fragment0%` / `%cfg%%h0%`.
  - Phase 5: there is no `!`, so nothing happens.
  - The CALL re-runs phase 1 and expands the accumulator plus the fragment. An undefined accumulator becomes empty
    inside a batch file. There are no carets, so caret doubling does not matter.
  - The two lines are mechanically identical. `h` is not a FOR variable, so the single-letter prefix changes nothing.
    The `if defined HUNTRESS_READY set "cfg="` guard is always true. So the GM's for_indirect vs call_double split
    cannot be a cmd-semantics fact.
- embedded-write `call set "ReCoVeReD=%%FrAg0%%..."` really is a CALL double pass. The FrAg values were set with
  `^|`, and phase 2 strips the carets, so the stored values hold a literal `|`. That is safe inside the quotes. The GM
  rejected call_double for it anyway. So the key is not "the join's mechanism".
- The percent joins (memory/remote/impact) are percent-expanded at parse time, after the fragments were set on earlier
  separate lines. They are not inside a block, the values contain no `!`, `%`, `"` or `^`, and they work. GM: delayed.
- LF-only lines are generator-inserted blocks: fragments 0-2, the goto/separator lines, and the control mutation lines.
  cmd treats LF as a line end and strips CR, so execution is unchanged. I checked the 512-byte label-search boundaries.
  None of them falls on a searched label (`:HUNTRESS_INSPECT`, `_SEPARATOR_DONE`, `_DISPATCH`, `_RECOVER`, `_EMIT`), so
  the LF goto quirk does not change any path.
- Every echo is `echo(!var!`. That is why the handoff (pipe-laden plan) needs delayed expansion: `%var%` would break on
  `|`. It is the only expansion common to all 7 "delayed" files.

## Other hidden-feature checks (all negative)
- No non-ASCII bytes, tabs or trailing spaces. The FOR lines hold plain ASCII.
- The zip entries have no comments or odd extra fields (all AES, identical).
- The HUNTRESS-MATERIAL decode equals the echoed plan in all 9 files. It has no extra keys (no expansion/control field).
- Values that do not track the label: the neutral_* marker names, campaign/neutral hex mod 2..5, HUNTRESS-EXTENSION vs
  the real extension, SeT/set case, separator type, `:HUNTRESS_UNUSED`, and the JS sibling styles.
- The label distribution (7 delayed / 1 / 1) cannot be a permutation of the visible joins (2 for, 3 percent, 2 call,
  2 delayed). So the key is not shuffled visible data. It is "delayed" by default, and only FOR files differ.

## Note for control (batch-*-control)
Its obvious readings were rejected too (stager linear/double_pipe, launcher if_defined, uploader call_label). That fits
the same pattern: the GM vocabulary or label is not the literal surface construct. Treat it as a separate open question.
