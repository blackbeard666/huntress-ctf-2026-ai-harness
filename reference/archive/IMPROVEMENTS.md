# Pre-Day-2 improvements plan

Goal: faster + more correct analysis, bounded agent cost (ilio-mini-style limits), live visibility.

## 1. Agent cost/turn limits (ilio-style) — correctness & cost safety
- `claude -p --max-turns` per stage: single 80, generalize 50, fix 30. Bounds runaway loops/cost.
- Lower stop-gate `MAX_BLOCKS` 25 -> 10 (a stuck worker escalates to HELP sooner instead of grinding).
- Per-stage wall-clock already via timeouts; set single 25min, generalize 12min (fix stays deadline-bound).
- `--output-format stream-json` kept (already) so limits + live view both work.

## 2. Deterministic triage (`hctf triage`) — grounds the agent, cuts cold-solve time
- New `hctf/triage.py`: no-LLM pass — `file`, `exiftool -j`, zip listing, signature scans (ELF/PE/.NET/APK/DEX,
  PowerShell/JS/VBS markers, base64/hex/compression), per-lane routing hints naming the skills.
- Writes `<mode dir>/triage.md`. Orchestrator runs it after artifact download, before the worker.
- Worker prompt references triage.md first.

## 3. Shared solver library `lib/` — reuse across days (biggest Day-2 speedup + correctness)
- `lib/common.py` (artifact finding, zip/nested extract, normalization, GM vocab helpers),
  `lib/warmups.py` (layered decoder), `lib/binaryre.py` (ELF/PE parse + confirmed vocab),
  `lib/scripting.py` (deobfuscation + indicator regexes + ATT&CK map), `lib/metadata.py`, `lib/mobile.py`.
- Extract proven Day-1 logic + confirmed vocabulary (endianness=little, machine=x86-64, collection=T1555.003).
- `run_solver` adds repo root to PYTHONPATH so `import lib.*` works; `solver-authoring` skill tells workers to
  prefer lib helpers and add to them.

## 4. ASC decompiler for mobile
- `pip install droidasc` into `.venv` + Homebase; add to `setup/install.sh`.
- `mobile-android` skill: primary path = `droidasc getmanifest` -> `findrefs` -> `getclass` on the handler;
  jadx/apktool as whole-app fallback. Lower RAM, on-demand, faster agent reasoning on big APKs.

## 5. Live view — see each agent think/act in real time
- `hctf watch`: full-screen board (challenge x mode, stage, elapsed, current agent action from stream-json), auto-refresh.
- `hctf tail <challenge>`: stream one agent's reasoning + tool calls live.

## 6. Correctness
- Baked vocabulary (skills + lib) to avoid wrong-answer-cap churn.
- Triage grounds answers in real file facts (less hallucination).
- Keep stop-gate: done only when solver-test passes.
