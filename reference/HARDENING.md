# Hardening readiness: are we ready when the artifacts get harder?

Cross-lane audit of Days 1–5 (2026-10-05). Question: how much do our solvers depend on "easy mode"
(symbols, un-obfuscated code, inert fixtures) vs. actually handle hardening — stripping, packing,
obfuscation, stego, anti-reversing?

## The one-line finding

**We are solving the *simulated* difficulty, not real hardening.** Across every lane the Days 1–5 artifacts
have been easy mode; the genuine difficulty is the GM's synthetic-label spelling under a clock, not the
artifact. The biggest near-term risk is **not exotic obfuscation — it's the organizers moving the answer or
adding one layer**, which breaks some lanes with *zero* obfuscation.

## Readiness by lane

| Lane | Rating | Why |
|---|---|---|
| **mobile-android** | **2/5** | Solvers are **JSON readers** — they read `assets/huntress_puzzle.json` and never touch the dex/manifest/resources. Every APK is the same 12.7 KB stub with the answer in plaintext JSON (one case has a 1-byte `classes.dex` and still passes). Breaks if the answer simply *moves* — no obfuscation needed. apktool/jadx installed but **unused**. |
| **binary-RE** | **2/5** | Header/symbol **extractors**, not RE engines. Lean on `.symtab`/DWARF being present. **Ghidra is non-functional** (needs JDK 21, only JDK 25 installed). Day 4 stripped-Go names live in `.gopclntab` that no solver parses. **Day 5 Rust solver is byte-identical to Day 4's Go solver** (copy-paste, no Rust path). No UPX/packer handling. |
| **metadata-forensics** | **3/5** | Strong tool-independent byte parsers for the format reads seen so far, but no stego/LSB, no encrypted-container cracking, no exotic containers. `exiftool`/`olevba`/`qpdf` the skill tells workers to use are **not installed locally** (Homebase only). |
| **warmups** | **3/5** | Encoding-peel (base/hex/xor/zip/rot) is solid; **cipher capability is near-zero** — only single-byte XOR, no repeating-key/Vigenère/classical/keyed crypto. Skill advertises base58/QP that aren't implemented. |
| **script-analysis** | **4/5 as-designed** | Best-prepared: every Days 1–5 "obfuscation" is an **inert simulated fixture** (codec+key printed in the file). Good JS tooling (box-js, webcrack, js-beautify) + pwsh + `pyinstxtractor-ng`. But **untested vs real armoring**; missing pyc decompilers (pycdc/decompyle3) and .NET (de4dot/ilspycmd) for genuinely compiled/armored samples. |

## Cross-cutting themes

1. **Solvers are extractors, not analysis engines.** Mobile = JSON reader; binary = header/symbol reader;
   metadata = byte parser. None decompile or emulate. Fine for easy mode, fragile under hardening.
2. **Cheapest escalations break us first.** Mobile: relocate the answer (0 obfuscation). Binary: ask a
   constant/function question on a *stripped* binary. These cost the organizers almost nothing.
3. **Skill/tool parity is broken.** Skills tell workers to use tools that are absent or non-functional
   locally: Ghidra (JDK mismatch), `exiftool`/`olevba`/`qpdf` (Homebase only), pyc decompilers (absent).
   → wasted worker turns and silent failures on the local path.
4. **Copy-paste fragility.** Day5 binary = Day4 (no Rust path); 5× near-identical mobile solvers; no shared
   `lib/android.py`. Any hardening fix must be made and tested N times during a live drop.
5. **Silver linings.** Everything is **static** → anti-debug/anti-VM/anti-tamper never fire on us. The right
   tools are mostly **already installed** (apktool, jadx, rizin, ghidra, box-js, webcrack) — just unused.

## Prioritized prep plan

### P0 — breaks us NOW with little/no obfuscation (do before the ramp)
- **Mobile: stop being a JSON reader.** Build `lib/android.py` with a fallback chain: `huntress_puzzle.json`
  → apktool manifest/resources scan (exported components, deep links, `strings.xml`, `resources.arsc`) →
  jadx decompile + `ANS-` regex across all `classes*.dex` (multidex) → simple static decrypt-routine eval.
  Consolidate the 5 copy-pasted solvers into it.
- **Binary: fix Ghidra** (install JDK 21, set `JAVA_HOME_OVERRIDE` in `tools/ghidra/support/launch.properties`;
  add a headless decompile-dump helper in `lib/`). Add a `.gopclntab` parser (stripped Go) and a real Rust
  path (Day 5 solver currently = Day 4). Replace the fragile `b8..c3` constant regex with capstone
  disassembly anchored at entry/main (it self-reports "ambiguous" and bails today).

### P1 — likely escalations
- **Binary: packer gate** — install `upx`, add an entropy/`UPX!` detector that auto-runs `upx -d` before
  analysis; add `GoReSym`/`rustfilt`.
- **Script: compiled/armored coverage** — add `pycdc`/`decompyle3` (pyc→source after pyinstxtractor) and
  `de4dot`/`ilspycmd` (.NET); define a safe sandboxed dynamic path for runtime-decrypt payloads.
- **Metadata: stego + crack pipeline** — LSB/bit-plane extractor (zsteg or PIL/numpy), `foremost`/binwalk
  carving + auto-inflate `zTXt/iTXt`; `zip2john`/`office2john`/`pdf2john` → the installed `hashcat` with a
  wordlist. Install `exiftool`/`olevba`/`qpdf` locally for skill parity.

### P2 — lower likelihood, high impact if dropped
- **Warmups: cipher capability** — repeating-key XOR, Vigenère/substitution/Atbash, Morse, base58, QP,
  optional AES-ECB-with-crib in `lib/decode.py`.
- **Binary: Mach-O (`macho_facts` via lief) + real .NET-IL** decompilation.

### Cross-cutting
- **Skill/tool parity audit:** every tool a skill names must be installed and functional locally; fix or
  remove the dead references (Ghidra, exiftool, pyc decompilers).
- **Adversarial regression fixtures:** add hardened synthetic cases to each lane's `cases/` (stripped/packed
  binary, relocated-answer/obfuscated APK, LSB-stego PNG, password zip, armored pyc) so hardening is caught
  in `hctf solver-test` **before** a live drop, not during one.

## Bottom line
Rank order to harden: **mobile (2) and binary (2) first** — they break cheapest — then the metadata/script
tool gaps, then warmups ciphers. The work is mostly *wiring in tools we already have* and *generalizing
extractors into analyzers*, not inventing new capability.

---

## Implementation status (2026-10-05) — prep plan DONE

All P0–P2 implemented and verified by `tests/test_hardening.py` (14/14 adversarial fixtures pass). Each lib
module is wired into its lane skill.

| Item | Status | Where |
|---|---|---|
| Mobile fallback chain (json→zip-scan→dex→apktool/jadx) + manifest facts | ✅ | `lib/android.py` |
| Binary: Ghidra JDK 21 fix (launches now) + headless decompile helper | ✅ | `tools/ghidra/support/launch.properties`, `lib/binary.ghidra_decompile`, `lib/ghidra_scripts/DecompileDump.java` |
| Binary: stripped-Go `.gopclntab` recovery, buildinfo, Mach-O, capstone constant recovery | ✅ | `lib/binary.py` |
| Binary: packer gate + UPX unpack (`upx` installed) | ✅ | `lib/binary.packer_info`/`unpack_upx` |
| Warmups: classical/keyed ciphers (caesar/atbash/vigenère+crack, repeating-XOR+crack, morse, base58, QP) | ✅ | `lib/ciphers.py` |
| Metadata: LSB/bit-plane stego, trailing-data carve, PNG text chunks, binwalk carve, wordlist zip crack | ✅ | `lib/stego.py` |
| Script: compiled-Python recovery (PyInstaller extract + decompyle3 + dis fallback) | ✅ | `lib/pyc.py` |
| Tools installed | ✅ | JDK 21, upx, john, foremost (apt); decompyle3 (uv). `setup/harden-env.sh` reproduces it |
| Adversarial regression harness | ✅ | `tests/test_hardening.py` |

**Dynamic-analysis path (the "static is not a guarantee" gap):** binary emulation via `angr`+`unicorn` (in
venv), JS sandbox via `box-js`. These cover computed-constant / runtime-string cases statically-ish.

### Residual gaps (documented, lower likelihood / need heavy deps)
- **.NET deobfuscation** (de4dot/ilspycmd) — needs a mono/dotnet runtime (not installed; heavy). Day-3 .NET
  was header-level only. Install mono if a managed-logic challenge drops.
- **pyarmor with real bytecode encryption** — needs dynamic unpacking, not static decompilation.
- **Modern-Python (3.9+) full decompilation** — decompyle3 covers 3.7–3.8; `dis` fallback still surfaces
  consts/strings. Build `pycdc` for full modern decompilation if needed.
- **`zip2john`/`office2john` → hashcat** — distro `john` lacks the *2john tools; `lib.stego.crack_zip` does a
  pyzipper wordlist instead (install john-jumbo for the full hashcat pipeline).
- **Live-target / runtime-only challenges** — reachable only inside the CTF network (Homebase). No generic
  interactive-target solver yet; `hctf hb exec` is the manual path.
- **GoReSym/rustfilt** — `lib.binary.go_pclntab_funcs` covers stripped-Go names; GoReSym/rustfilt are nicer
  but optional downloads (noted in `setup/harden-env.sh`).
