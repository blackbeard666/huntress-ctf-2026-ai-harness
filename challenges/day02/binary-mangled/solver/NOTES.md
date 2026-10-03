# Mangled (Day 02 binary) solver notes

Concept: `evidence.zip` (AES, pw `infected`) holds a plain C build (`day01-c.elf`) and a C++ build (`day02-cpp.elf` or
MinGW PE32+ `day02-cpp.exe`). Answer ids are `c_*`, `cpp_*` or bare config fields (campaign/domain/url/mutex), with
`setN.` prefixes in Mastery (`delivery N: evidence.zip`). Field-by-field derivation is in the `solve.py` docstring.

## Variant axes handled
- C++ build as ELF or PE (MinGW): symbols come from the COFF symbol table + string table; `cpp_format` -> `elf`/`pe`
  (`elf` GM-confirmed; `pe` by analogy, still unconfirmed, so it is kept out of the PE cases' `expected.json`).
- Different HCFG config per variant (xor key 0x31.., crc32, BR02-NNN campaign/domain/url/mutex). Header crc is checked.
- Different C builds: `BR01-CATALOG-NNN` marker, recover_code = `mov eax, imm; ret` (observed 8100 + NNN).
- **Stripped C build** (Mastery 20e92453 set2, `BR01-CATALOG-010`): no `.symtab`, so there is no `recover_code`
  symbol. Fallback `stripped_return_const`: scan `.text` for a leaf `b8 imm32 c3`; ties are broken by the immediate
  that `main` also inlines. Checked against every C build in the cases: matches the symbol-based value on all of them.
  `c_has_symtab` -> `false` for this build.
- Mastery: several deliveries with the C/C++ builds mixed independently per set.

## Regression cases
The variant `expected.json` files were never GM-confirmed (the attempts expired). They come from an independent
derivation (readelf -p/.symtab, objdump `mov eax; ret`, nm + c++filt, separate HCFG decode with crc check) that matches
the solver on every field. PE `cpp_format` is left out on purpose.

## Hardening pass after variant-time_trial-fcdfb939 + Mastery 2ab64f7f/2f91811c/502cee3d/e5df4078 (2026-10-04)
- **No new byte-level axis.** Re-derived every field independently (readelf -p .huntress, objdump `mov eax; ret`
  incl. stripped C build BR01-CATALOG-014 -> 8114, `objdump -t`/nm + c++filt for the MinGW PE and ELF C++ builds,
  separate HCFG decode with crc check). The solver already matched on every field. These attempts *expired*:
  the GM clock is ~5s (Time Trial) / ~12s (Mastery) from start, and the submits arrived 7-37s after start (fcdfb939 never
  submitted). The solver takes 0.2-0.5s, so the latency is in the orchestration path, not in solve.py.
- Those 5 cases now have a real `expected.json` (PE `cpp_format` still left out: `pe` is unconfirmed).
- Robustness: `mangled_score_symbol` no longer needs `c++filt` (a built-in Itanium nested-name parse finds
  `<Class>::score`). Checked with c++filt removed from PATH. `cpp_format` vocabulary now comes from `lib.knowledge.BINARY_FORMAT`.
- Imports: stdlib, pyelftools, pefile, capstone, pyzipper, lib.knowledge, optional `c++filt`. All are available on Homebase.

## Hardening pass after Mastery a497ff5e (2026-10-04)
- **No new variant axis.** set1 = C build BR01-CATALOG-000 + MinGW PE32+ C++ build (key 0x32, crc 0xffdeebbe, BR02-001);
  set2 = C build BR01-CATALOG-003 + ELF C++ build (key 0x33, crc 0x87162f3d, BR02-002). Both have an unused base class
  `BehaviorEngine` (only _ZTI/_ZTS, no _ZTV); the vtable answer is `_ZTV15DiscoveryEngine`. Re-derived independently
  (pyzipper extract + sha256sum, readelf -p .huntress, objdump `recover_code` -> 0x1fa4/0x1fa7, nm + c++filt, separate
  HCFG decode with crc check). This matches the solver on all 34 ids (0.34s).
- **Why it failed:** no submit was ever sent. The server started the attempt at 18:43:42.5Z, the local start log is 18:43:45Z,
  downloads finished 18:43:46Z, and the deadline was 18:43:54.5Z (12s). The problem is orchestration latency, not solve.py.
- `expected.json` now filled (set1 PE `cpp_format` still omitted: `pe` is unconfirmed).

## Hardening pass after Mastery a7c4de42 (2026-10-04)
- **No new variant axis.** First Mastery with a **MinGW PE32+ C++ build in both sets**. set1 = BR01-CATALOG-000 (8100) +
  PE (key 0x32, crc 0xffdeebbe, BR02-001); set2 = BR01-CATALOG-008 (8108) + PE (key 0x36, crc 0xe810e785, BR02-005).
  Re-derived independently (pyzipper + sha256sum, readelf -p .huntress, objdump `recover_code` 0x1fa4/0x1fac,
  `objdump -t` COFF symbols, separate HCFG decode with crc check). This matches the solver on all 34 ids (0.5s).
- **Why it failed:** no submit was sent. Start was 18:46:34.9Z, the local start log is 18:46:37Z, downloads finished
  18:46:39Z, and the deadline was 18:46:46.9Z (12s). Orchestration latency again.
- Risk to watch: both `cpp_format` answers are `pe`, which is **still GM-unconfirmed** (the only PE `pe` submit,
  time_trial 1e04f2da, expired). The PE has no format label of its own. If a run comes back `incorrect` on
  `cpp_format` for a PE build, update `lib.knowledge.BINARY_FORMAT["PE"]`. `expected.json` omits the two
  `cpp_format` ids for that reason.

## Hardening pass after Mastery 5b8e8d0f (2026-10-04)
- **No new variant axis.** set1 = BR01-CATALOG-000 (0x1fa4 = 8100) + MinGW PE32+ C++ build; set2 = BR01-CATALOG-013
  (0x1fb1 = 8113, symtab present) + ELF C++ build. Both C++ builds carry the same HCFG (key 0x32, crc 0xffdeebbe, BR02-001)
  and the unused `BehaviorEngine` base (only _ZTI/_ZTS). The vtable answer is `_ZTV15DiscoveryEngine`. Re-derived independently
  (pyzipper + sha256sum, readelf -p .huntress, objdump `recover_code`, nm / `objdump -t` COFF, separate HCFG decode with
  crc check). This matches the solver on all 34 ids (0.33s).
- **Why it failed:** no submit was sent. Start was 18:49:19.1Z, the local start log is 18:49:21Z, downloads finished
  18:49:24Z, and the deadline was 18:49:31.1Z (12s). Orchestration latency again, not solve.py.
- `expected.json` filled (set1 PE `cpp_format` omitted: `pe` still GM-unconfirmed).
