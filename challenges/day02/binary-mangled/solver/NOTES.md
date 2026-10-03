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
