# Expansion Pack notes (hypothesis | evidence | result)
- PS (3 samples) + JScript (9) reuse day02 solver | 87 ids submitted together | ACCEPTED all
- Batch plan = fragments joined in :HUNTRESS_INSPECT, echoed; HUNTRESS-MATERIAL is a 2nd encoded copy (equal) | solver/batchplan.py emulator | role/adapter/campaign/indicator/graph (45 ids) ACCEPTED
- Batch ATT&CK not yet submitted (planned: launcher/chain/relay T1059.003, others as JScript roles)
- NOTE: multi-id submit is all-or-nothing; a failed batch marks every value "already judged incorrect" locally -> use --force to retry singly.
## expansion (GM truth vs rendered join line)
| file | role | join rendered | GM accepted | GM rejected |
| host-context.cmd | benign | for+call set | for_indirect | |
| memory-stage.bat | stager | percent | delayed | percent |
| embedded-write.cmd | dropper | call set %% | delayed | call_double, call-double, percent |
| remote-write.bat | downloader | percent | delayed | percent_expansion |
| outbound-transfer.cmd | uploader | !delayed! (in call :label) | delayed | |
| local-dispatch.bat | launcher | for+call set (if defined reset) | call_double | for_indirect, delayed |
| impact-plan.cmd | impact | percent | delayed | percent, immediate |
| staged-handoff.bat | chain | call set %% | delayed | call_double, double_call |
| relay-handoff.cmd | relay | !delayed! (if defined) | delayed | |
All echo lines are `echo(!var!`. Rule not yet understood.
## control
- rejected: stager linear, stager double_pipe, launcher if_defined, uploader call_label
- rejected also: stager goto, dropper goto, benign errorlevel, relay if_defined
## ATT&CK (all ACCEPTED): benign none, stager/downloader T1105, impact T1486, dropper T1140, uploader T1041, launcher/chain/relay T1059.003
## relaunch #1 (control)
- control block = LF-only generator lines between `:HUNTRESS_SEPARATOR_DONE` and the echo | byte line endings | launcher+relay share the same block: `set "HUNTRESS_READY=1"` + `if defined HUNTRESS_READY <first join line>`
- straight files (stager/downloader/impact, no control lines) = `direct` | GM | ACCEPTED x3
- if-defined form: defined_guard (relay), flag_guard, for_loop, variable_guard (launcher), direct, defined_flag (relay) | GM | all REJECTED -> both fields at the 6-wrong cap
- solver: control_form -> direct/errorlevel_guard/goto_dispatch/call_subroutine + DEFINED_GUARD_FORM (untried "environment_guard"); expansion_form now emits the GM rule (non-FOR -> delayed; FOR -> for_indirect, or call_double when reset is under `if defined`) | solver-test ok, 157/157 confirmed reproduced
