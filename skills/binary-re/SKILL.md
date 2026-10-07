---
name: binary-re
description: Huntress binary-reverse-engineering lane - ELF/PE/Mach-O structure and reversing. Covers header/section/symbol inspection (readelf, rizin, Ghidra headless), custom sections, entry points, recovering constants and strings returned by functions, .NET/Go/Rust, packers, and z3/angr/unicorn for checks. Use for binary-reverse-engineering-day-NN challenges.
---

**Installed: readelf/objdump/nm/c++filt, rizin + rabin2 (radare2), Ghidra `analyzeHeadless`, ilspycmd (.NET), GoReSym (Go), rustfilt (Rust), javap/jar, upx, capstone/pyelftools/pefile/lief/dnfile (venv), yara.**

# Day-1-style structural questions (answer from the headers, exactly)
- `readelf -h` : ELF class (`ELF32`/`ELF64`), data (endianness, e.g. `little endian` -> the exact token the question wants),
  machine (`Advanced Micro Devices X86-64` -> usually `x86-64`/`AArch64`; match the format's `syntax`), type
  (`EXEC`/`DYN`/`REL`/`CORE`), entry point (give it as `0x...` lowercase per the format).
- `readelf -SW` : sections; recover a custom section's bytes with
  `readelf -x .huntress file` or `objcopy -O binary --only-section=.huntress file /dev/stdout`.
- `readelf -sW` / `nm` : symbols. `.symtab` present? -> true/false. "exported/designated analysis symbol" = read the dynsym/symtab.
- A constant returned by a function: decompile just that function (`rizin -q -c "aaa; pdf @ sym.recover_code" file`
  or Ghidra headless) and read the returned literal. Verify against the disassembly.

# General reversing
- Triage: `file`, `rizin -c "iI" -q`, `rabin2 -I`, `strings -n6`. Detect packers (UPX -> `upx -d` a copy), .NET (`ilspycmd` /
  decompile), Go (`GoReSym`/symbols), Rust (demangle). PE: `rizin`/`rabin2 -I`, imports with `rabin2 -i`.
- Ghidra headless for bigger binaries:
  `analyzeHeadless <proj_dir> tmp -import file -postScript <script>.py -deleteProject` (scripts go in `$TMPDIR`).
- Flag/constant usually computed at runtime: emulate the routine (unicorn) or run a copy under `gdb` with a breakpoint right
  after it, rather than reversing everything. Patch a copy, never the original.
- Checks and key schedules: model in z3, or `angr` with `claripy.BVS` input + printable constraints + `explore(find=, avoid=)`.
  Crypto by constants (AES tables, `0x9E3779B9` TEA, `expand 32-byte k`): identify, then reimplement with pycryptodome.

# Solver tips
`lib.binary` has the hardening helpers (use them instead of fragile byte regexes): `packer_info(data)` +
`unpack_upx(path)` (entropy/UPX gate — unpack BEFORE analysis), `go_pclntab_funcs(data)` + `go_buildinfo(data)`
(recover STRIPPED-Go function names from .gopclntab — they survive stripping), `rustfilt(sym)`,
`macho_facts(data)` (Mach-O via lief), `recover_return_constants(data)` (capstone, robust where `b8..c3`
went ambiguous), and `ghidra_decompile(path)` (headless, JDK 21 wired; heavy — last resort).
Parse structure with `pyelftools`/`lief`/`rizin -j` (JSON) and derive every value from the binary in the variant; never hard-code
an address, symbol name or constant. Keep heavy analysis (angr/Ghidra) off the timed path unless it's genuinely required.
