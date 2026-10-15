# Coverage atlas -- binary-reverse-engineering (as of D15, 2026-10-15)

Scope: what a D16+ `evidence.zip` group could be, how we would recognise it, which standard tool answers it, and how ready we
are. Grounded in `reference/techniques/binary-reverse-engineering.md` (lane log D1-D15), `challenges/day15/binary-stripped/solver/NOTES.md`,
`lib/binary.py` (`hcfg_scan`/`hcfg_find`, `packer_info`, `unpack_upx`, `go_buildinfo`, `go_pclntab_funcs`, `rustfilt`, `macho_facts`,
`recover_return_constants`, `ghidra_decompile`, `jar_app_classes`) and `tests/data/binary_fixtures/TARGETS.json` (all 9 targets have fixtures).

Progression so far: D1-D14 = one new compiled language per day (container nearly always ELF64 x86-64, HCFG blob re-stored per
language); D15 = first non-language TWIST (stripped + symbolized pair, new `<qualifier>_` id prefix). Asked field names are a small
fixed pool (config_*, format, machine, architecture, elf_class, elf_type, endianness, entry_point, symbols, section_names,
disassembly, has_symtab, has_cpp_*, has_hcfg_section, hcfg_offset, hcfg_version, xor_key_hex, metadata_version,
compression_methods); the prompt's language theme has not been asked since D4. So for D16+ the biggest risks are (a) a twist that
hides the HCFG from a byte scan (packing, real crypto, stack-built), (b) a new container/arch whose LABEL we have never spelled
(Mach-O, WASM, AArch64, MIPS...), (c) a new field family (imports, build-id, protections).

Tool legend: **[I]** installed (`source bin/env.sh`; checked with `which`/`ls`), **[M]** missing.
Installed: readelf/objdump/nm/c++filt/strings/objcopy (binutils x86-64 + aarch64-linux-gnu-objdump), llvm-18 (llvm-objdump-18,
llvm-readobj-18, llvm-otool, llvm-lipo, llvm-nm, llvm-dwarfdump, llvm-cxxfilt-18 under /usr/lib/llvm-18/bin), file, binwalk, upx 4.2.4,
rizin 0.9.1 (`bin/rizin`, `rz-bin`, `rz-asm`, `rz-find`, `rz-diff`) + radare2/rabin2, Ghidra (`bin/analyzeHeadless`, processors incl.
AARCH64/ARM/MIPS/PowerPC/RISCV/Sparc/x86/JVM/Dalvik), GoReSym, rustfilt, swift-demangle, nim-demangle, ilspycmd, dotnet, java/javap,
jadx, dex2jar, apktool, pyinstxtractor, pycdc/pycdas, autoit-ripper, hbc-decompiler, gdb + gdb-multiarch, ltrace/strace, yara,
7z, xxd; venv python: capstone, unicorn, angr, lief, pyelftools, pefile, dnfile, pycryptodome, pyzipper, xdis/uncompyle6/decompyle3,
lz4, yara. Cross compilers: aarch64-linux-gnu-gcc-15, clang-18 (no lld/wasm-ld: other targets compile to `.o` only).
Missing: qemu-user(-static), wabt (wasm2wat/wasm-objdump), FLOSS, capa, Detect-It-Easy (diec), de4dot, monodis, erlang (beam_disasm),
unluac/luajit-decompiler, blutter, srecord (srec_cat), binutils-multiarch, checksec, python zstandard/brotli, rzpipe/r2pipe.

## Concept table

| # | concept | status | recognition cues | standard tool + exact command | D16+ likelihood |
|---|---|---|---|---|---|
| 1 | C ELF (gcc, glibc) | seen D1, D15 | `GCC: (...)` in `.comment`, `.interp` ld-linux, `__libc_start_main` | [I] `readelf -hSW f; readelf -sW f; objdump -d -M intel f` | high (carry-over every day; mastery d01 re-rolls stripped/renamed) |
| 2 | C++ Itanium ELF / MinGW PE32+ | seen D2 | `_Z` symbols, `_ZTV`/`_ZTI`/`_ZTS`, `libstdc++`; PE `.text$_Z...` COMDAT, `.CRT`, `.tls` | [I] `nm -C f`; `objdump -t f.exe`; `c++filt` | high (carry-over; ELF/PE re-rolls per member) |
| 3 | .NET C# PE (pe_cli) | seen D3 | `BSJB` metadata root `v4.0.30319`, `mscoree.dll`/`_CorExeMain`, `.runtimeconfig.json` | [I] `ilspycmd f.dll`; python `dnfile` | high (carry-over) |
| 4 | Go (static, stripped; PE in Mastery) | seen D4 | `\xff Go buildinf:`, `.gopclntab`, `runtime.`, `go1.NN` | [I] `GoReSym -t -d -p f`; `go version -m f`; `lib.binary.go_buildinfo` | high (carry-over) |
| 5 | Rust ELF (debug_info) | seen D5 | `_ZN...17h<16hex>E` / `_R` v0 symbols, `rustc version`, `/rustc/<sha>/library` panic paths | [I] `rustfilt < syms`; `readelf -p .comment f` | high (carry-over) |
| 6 | Rust stripped / release | gap | no `.symtab`, panic strings + `/rustc/<40hex>/` paths remain, `core::fmt` strings | [I] `strings -a f \| grep -m3 /rustc/`; Ghidra headless; [M] no cargo-rustc symbol-recovery tool | med (natural "stripped" sequel for any language) |
| 7 | Java / Kotlin jar | seen D6, D7 | `PK` + `META-INF/MANIFEST.MF`, `CAFEBABE` classes, `kotlin/` packages | [I] `unzip -l f.jar; javap -v -p -c Main.class`; `jadx -d out f.jar`; `lib.binary.jar_app_classes` | high (carry-over) |
| 8 | Swift ELF (static stdlib, 67 MB) | seen D8 | `swift5_*` sections, `$s` symbols, `libswiftCore` | [I] `bin/swift-demangle`; regex `SENGR` in `.rodata` | high (carry-over) |
| 9 | Nim / D / Crystal ELF | seen D9, D11, D13 | Nim `NimMain`,`fatal.nim`; D `_D4core`,`DMDH`; Crystal `Crystal:H`,`GC_malloc` | [I] `bin/nim-demangle`; `grep -abo 'SENGR[A-Za-z0-9+/=]*' f` | high (carry-over) |
| 10 | Zig ELF + PE | seen D10 | `.comment` "zig-bootstrap"/LLD 19, stripped, `.hcfg` section | [I] `readelf -p .comment f; readelf -x .hcfg f` | high (carry-over) |
| 11 | Free Pascal ELF | seen D12 | `FPC 3.2.2`, `.fpcdata`, `FPC_` symbols, static stripped | [I] `strings -a f \| grep FPC`; `grep -abo HCFG f` | high (carry-over) |
| 12 | Objective-C (GNUstep) ELF | seen D14 | `__objc_selectors`/`__objc_classes`, `objc_msg_lookup`, `._OBJC_CLASS_` | [I] `readelf -sW f \| grep -E '_OBJC_CLASS_\|objc_sel_name_'` | high (carry-over) |
| 13 | Haskell (GHC) | gap | `hs_main`, `ghczmprim_`/`base_GHCziBase` z-encoded symbols, `GHC <ver>` rts strings, huge static ELF | [I] `strings -a f \| grep -m2 'GHC '`; `nm f \| grep -c _info$`; [M] no hsdecomp | med (classic "weird runtime" language left on the list) |
| 14 | OCaml native | gap | `caml_startup`, `camlStdlib__`, `caml_main`, `OCAMLRUNPARAM` | [I] `nm f \| grep -m5 '^.* T caml'`; `strings -a f \| grep -i ocaml` | med |
| 15 | V language | gap | `main__main`, `v__`/`builtin__` symbols, compiled via C (`.comment` GCC/tcc) | [I] `nm f \| grep -E 'main__main\|builtin__'` | low-med |
| 16 | Dart AOT (`dart compile exe`) / Flutter `libapp.so` | gap | `_kDartVmSnapshotData`/`_kDartIsolateSnapshotInstructions` symbols, `Dart_` strings, snapshot hash | [I] `readelf -sW f \| grep _kDart`; [M] blutter (`github.com/worawit/blutter`) | low-med (snapshot strings are compressed: HCFG may not be byte-visible) |
| 17 | Fortran (gfortran) | gap | `_gfortran_` imports, `MAIN__`, `libgfortran.so.5` NEEDED | [I] `readelf -dW f \| grep NEEDED`; `nm -D f \| grep gfortran` | med (pun-friendly title, trivial for organizers) |
| 18 | Ada (GNAT) | gap | `__gnat_`, `ada_main`, `GNAT Version: N`, `libgnat` | [I] `strings -a f \| grep -m1 'GNAT Version'` | med |
| 19 | Erlang/Elixir BEAM | gap | `FOR1....BEAM` IFF chunks (`AtU8`,`Code`,`LitT` zlib), escript `#!` + zip | [M] `erl -noshell -eval 'beam_lib:chunks(...)'` (apt erlang-base); [I] python `zlib` on `LitT` | low-med (would be a new container: format label unknown) |
| 20 | Heavy AOT runtimes: Julia, GraalVM native-image, Kotlin/Native | gap | Julia `libjulia`, `jl_`; GraalVM `__svm_`, `com.oracle.svm`; K/N `kfun:`, `Konan_` | [I] `nm f \| grep -m5 -E 'kfun:\|__svm\|jl_'`; `strings -a f` | low-med (K/N most likely: Kotlin already a theme) |
| 21 | Python frozen: PyInstaller / Nuitka / py2exe | gap (tooled) | PyInstaller cookie `MEI\x0c\x0b\x0a\x0b\x0e`, `pydata` section, `_MEIPASS`; Nuitka `__nuitka`, `NUITKA_ONEFILE`; py2exe `PYTHONSCRIPT` resource | [I] `bin/pyinstxtractor f; bin/pycdc x.pyc`; Nuitka: `strings -a f` + constants blob; [I] `uncompyle6`/`decompyle3` | med (blurs into script lane; HCFG would sit in a marshalled const) |
| 22 | Lua / LuaJIT bytecode | gap | `\x1bLua` + version 0x51-0x54; `\x1bLJ` (LuaJIT); embedded in a C host | [I] `xxd -l 16 f`; [M] `luac -l -l` (apt lua5.4), unluac jar, luajit-decompiler-v2 | low-med |
| 23 | Legacy Windows: Delphi, VB6, AutoIt | gap (AutoIt tooled) | Delphi `Borland`/`Embarcadero`, `DVCLAL`, `PACKAGEINFO` RCDATA; VB6 `MSVBVM60.DLL`, `VB5!`; AutoIt `AU3!EA06`, RCDATA `SCRIPT` | [I] `bin/autoit-ripper f.exe out/`; python `pefile` resources; [M] IDR/DIE | low (lane is Linux-first; Pascal already done via FPC) |
| 24 | Niche native langs: Odin, Hare, Vala, GnuCOBOL, Chapel | gap | Odin `runtime.`/`__$startup_runtime`; Vala `g_object_`/GLib; COBOL `cob_init`, `libcob` | [I] `readelf -dW f \| grep NEEDED`; `nm f \| head` | med (the organizers clearly have a "one more language" list) |
| 25 | MSVC PE (vs MinGW) | gap (MinGW seen D2) | `Rich`/`DanS` header, `.text$mn`, debug dir RSDS + `.pdb` path, `VCRUNTIME140.dll` | [I] `objdump -x f.exe`; python `pefile` (`RICH_HEADER`, `DIRECTORY_ENTRY_DEBUG`) | low-med |
| 26 | musl / static linking | seen D4, D5, D8, D12 (static); musl gap | no `.interp`, no `.dynamic`; musl: no `GLIBC_2.` version strings, `__libc_start_main` absent | [I] `readelf -lW f \| grep -c INTERP`; `strings -a f \| grep -c GLIBC_` | med (cheap twist "Static") |
| 27 | Mach-O thin / fat universal | gap (`lib.binary.macho_facts`) | `cffaedfe`/`cefaedfe` (thin), `cafebabe` + nfat_arch<20 (fat: collides with Java class magic), `__TEXT`/`__DATA_CONST`, `LC_MAIN` | [I] `/usr/lib/llvm-18/bin/llvm-otool -hlv f`; `llvm-lipo -info f`; `rz-bin -I f`; python `lief` | med-high (Swift/ObjC days were ELF, but `macho` already sits in the playbook format law; label presumed `macho`) |
| 28 | WebAssembly module | gap | `\0asm\x01\0\0\0`, sections type/import/func/data; HCFG in a data segment | [M] `wasm-objdump -x f.wasm; wasm2wat f.wasm` (apt wabt); [I] rizin `rz-bin -I f.wasm`, Ghidra (no wasm loader by default) | med (popular "new compiled target"; format label unknown: `wasm`?) |
| 29 | Relocatable object (ELF ET_REL / COFF .o) | gap | ELF e_type 1, `.rela.text`, no program headers, entry 0; COFF: no MZ, Machine u16 at 0 | [I] `readelf -hrW f.o; objdump -r f.o`; `llvm-readobj-18 --file-headers f.obj` | low-med (`elf_type` asked since D8: `ET_REL` would be new value) |
| 30 | Shared library (.so ET_DYN / .dll) | gap | `ET_DYN` with no `.interp`, SONAME, exported dynsyms; PE `IMAGE_FILE_DLL`, export dir | [I] `readelf -dW f.so; nm -D --defined-only f.so`; `objdump -p f.dll` | med (config in an exported symbol; entry_point may be 0) |
| 31 | Raw firmware / Intel HEX / S-record | gap | no magic; ARM vector table (SP then odd reset addr); `:10xxxx00` lines (IHEX) / `S0`,`S1`-`S3` (SREC) | [I] `objcopy -I ihex -O binary f.hex f.bin` / `-I srec`; `binwalk -A f.bin`; `rizin -a arm -b 16 -m 0x08000000 f.bin`; [M] srec_cat | low |
| 32 | x86 32-bit (ELF32 i386 / PE32 native) | gap (ELF); PE32 i386 seen D3 (.NET) | ELFCLASS32 + e_machine 3; PE Machine 0x14c, OptionalHeader 0x10b | [I] `readelf -h f`; labels: ELF `x86` / `ELF32` / int `3`; PE `i386` (knowledge.PE_MACHINE) | med-high (cheapest arch twist; GM already took `x86`/`i386`) |
| 33 | AArch64 | gap (label known, never seen) | e_machine 183 (0xb7); PE 0xaa64; Mach-O cputype 0x0100000c | [I] `aarch64-linux-gnu-objdump -d f`; `rizin -a arm -b 64`; capstone `CS_ARCH_ARM64`; [M] `qemu-aarch64-static f` | med-high ("Cross-arch" twist; label `AArch64` in ELF_MACHINE) |
| 34 | ARM32 / Thumb | gap (label `ARM` in map) | e_machine 40, EF_ARM_EABI flags, odd entry = Thumb, `.ARM.attributes`/`.ARM.exidx` | [I] `readelf -A f; llvm-objdump-18 -d --triple=thumbv7 f`; [M] qemu-arm-static | med |
| 35 | MIPS / MIPSel, PowerPC, SPARC (incl. big-endian) | gap (no labels in ELF_MACHINE) | e_machine 8 MIPS (readelf "MIPS R3000"), 20/21 PPC/PPC64, 2/43 SPARC/SPARCV9; EI_DATA=2 => BE | [I] `readelf -h f`; Ghidra headless (processors present); `rizin -a mips -b 32 -e cfg.bigendian=1`; [M] binutils-multiarch, qemu-user | low-med (BE flips HCFG u16/u32 if the generator writes native order) |
| 36 | RISC-V | gap | e_machine 243, `.riscv.attributes`, `rv64imafdc` arch string | [I] `readelf -A f`; `llvm-objdump-18 -d f`; `rizin -a riscv` | med (trendy; clang-18 targets it) |
| 37 | UPX packed | gap (`lib.binary.packer_info`/`unpack_upx`) | `UPX!` in first 4 KB, sections `UPX0`/`UPX1`, entropy > 7.2, tiny section table | [I] `upx -t f && cp f /tmp/u && upx -d /tmp/u`; `lib.binary.packer_info(data)` | high (most natural sequel to "Stripped"; packed bytes hide HCFG from every scan) |
| 38 | Scrubbed UPX / other packers (MPRESS, ASPack, Themida, custom XOR stub) | gap | UPX section names renamed, `UPX!` zeroed (upx -d: "not packed"), `.MPRESS1`, tiny import table + high entropy | [I] restore `UPX!` at l_info/p_info then `upx -d`; `binwalk -E f`; gdb dump after OEP; [M] diec | med |
| 39 | Stripped (no `.symtab`) | seen D15 (+ D8/D15 Mastery d01) | `readelf -S` lacks `.symtab`/`.strtab`; `file` says "stripped" | [I] `readelf -SW f \| grep -c symtab`; absence answers `[]`/`none`/`false` | high (keeps re-rolling into old groups) |
| 40 | PIE / RELRO / NX / canary (checksec fields) | gap | PIE = ET_DYN + INTERP; `GNU_RELRO` + `BIND_NOW` = full; `GNU_STACK` RW = NX; `__stack_chk_fail` import | [I] `rz-bin -I f` (prints pic/relro/nx/canary/static/stripped/lang); `readelf -lW -dW f`; [M] checksec | med (cheap new boolean field family) |
| 41 | Anti-debug (ptrace TRACEME, IsDebuggerPresent, timing, /proc/self/status) | gap | `ptrace` import, `TracerPid` string, `IsDebuggerPresent`/`NtQueryInformationProcess` | [I] `objdump -d f \| grep -B3 'call.*ptrace'`; static only (never execute) | low-med (lane is static-answer; only bites if config is decoded at runtime) |
| 42 | Control-flow obfuscation: OLLVM (CFF/BCF/sub), VM-based (VMProtect-style, custom bytecode VM) | gap | giant dispatcher switch over a state var, opaque predicates `x*(x+1)%2`, `.vmp0` sections, interpreter loop + bytecode blob | [I] Ghidra headless + `lib.binary.ghidra_decompile`; unicorn emulation of the decode fn; angr | low-med (expensive for organizers to build for 5 lanes x variants) |
| 43 | Managed obfuscation: ConfuserEx/.NET, ProGuard/ZKM Java | gap | .NET `ConfusedByAttribute`, garbage-named types, `<Module>.cctor` string decryptor; Java `a.a.b` names | [I] `ilspycmd`; `jadx --deobf`; [M] de4dot (github de4dot-cex, needs mono) | low-med |
| 44 | HCFG raw + 1-byte header xor, crc-gated | seen D2-D15 | `HCFG` magic, ver byte, xor key byte, u16 len LE, u32 crc | [I] `grep -abo HCFG f`; `lib.binary.hcfg_find(data)` | high (carry-over) |
| 45 | HCFG in a custom section / .NET FieldRVA / FPC `.data` | seen D2, D3, D10, D12, D14, D15 | section named `.hcfg` (`has_hcfg_section`), FieldRVA `<PrivateImplementationDetails>` | [I] `readelf -x .hcfg f`; `objdump -h f.exe`; `dnfile` | high |
| 46 | HCFG base64 literal (const pool / rodata String) | seen D6-D9, D11, D13 | `SENGR[A-Za-z0-9+/_-]*=*`, offset = the `S` | [I] `grep -abo 'SENGR[A-Za-z0-9+/=]*' f` | high |
| 47 | Text/wide/compressed codecs (hex, base32/85/a85, UTF-16, reversed, xor, zlib/gzip/deflate) | prebuilt hcfg_scan (tests/data/hcfg_fixtures) | `48434647`, `\x48\x43`, `JBBUMRY`, `<~`, `H\0C\0F\0G\0`, `x\x9c` | [I] `lib.binary.hcfg_scan(data)` | med |
| 48 | Multibyte xor / byte maps (nibble-swap, NOT, add/sub, rol) | prebuilt multibyte-xor, nibble-swap-bitnot | no magic; high-ish entropy region of len ~12+json; known plaintext `HCFG` recovers key | [I] `hcfg_scan`; fixtures `mxor_*`, `bytemap_*` | med-high ("Encrypted config" twist is the obvious D16+ HCFG move) |
| 49 | Custom base64 alphabet / ROT13-base64 / case-swap | prebuilt custom-base64-alphabet, rot13-base64 | 64-char unique-char string near a b64-looking blob; `FRATE` (rot13 of `SENGR`) | [I] `hcfg_scan`; fixtures `b64c_*`, `rotb64_*` | med |
| 50 | Split literals / int arrays / strided | prebuilt split-literals, int-array, strided | pointer table to short chunks; `48 00 00 00 43 00 00 00`; `72,67,70,71` | [I] `hcfg_scan`; fixtures `split_*`, `int_*`, `stride_*` | med |
| 51 | RC4 | prebuilt rc4 | 256-byte KSA loop (`i<256`, swap), printable key near blob | [I] `hcfg_scan`; fixtures `rc4_*`; `openssl enc -rc4` | med |
| 52 | Base-N of compressed (zlib/gzip/lzma/bz2/xz) | prebuilt base64-of-compressed | `eJ` (b64 zlib), `H4sI` (b64 gzip), `/Td6WFo` (b64 xz), `QlpoOTFBWSZT` (b64 bz2) | [I] `hcfg_scan`; fixtures `zpack_*` | med |
| 53 | Block/stream ciphers: AES (ECB/CBC/CTR/GCM), XTEA/TEA, ChaCha20/Salsa20 | gap | AES S-box `63 7c 77 7b`, Te tables, `AESENC`/`aesenc` insns, OpenSSL `EVP_` imports; TEA delta `0x9e3779b9`; `expand 32-byte k` | [I] `yara` crypto rules, `strings`, `rz-find -x 637c777b f`; python `Crypto.Cipher` | med-high (cumulative "harder config" ramp; key/IV must be in the binary) |
| 54 | Rolling / index xor (`k+i`, `k^prev`, xor with `crc`/len) | gap | short decode loop `xor byte [rdi+rax], cl; add cl, 1`; no constant key | [I] capstone on the decode fn; brute 256x few modes on known plaintext `HCFG` | med |
| 55 | Stack-built / code-built blob (mov imm to stack, per-char pushes) | gap | runs of `mov dword [rbp-0x..], imm32` / `movabs rax, imm64; mov [rsp+..], rax`; no blob bytes contiguous in rodata | [I] unicorn/angr emulate the builder fn; capstone imm collection; [M] FLOSS (`floss --only stack tight f`) | med-high (classic CTF "no strings" follow-up to "Stripped") |
| 56 | Resources: PE RT_RCDATA, .NET manifest resource, jar non-class file, Mach-O section | gap | `.rsrc` RCDATA named `HCFG`/`CONFIG`; .NET `ManifestResource` table; jar `config.bin` | [I] python `pefile` `DIRECTORY_ENTRY_RESOURCE`; `dnfile` resources; `unzip -p f.jar config.bin`; `llvm-otool -s __DATA __hcfg f` | med (a resource is the PE twin of `.hcfg`; offset convention unconfirmed) |
| 57 | Overlay (bytes after last section / appended) | gap | file size > max(section end); `binwalk` hit past EOF of image | [I] python `pefile` `get_overlay_data_start_offset()`; ELF: max(sh_offset+sh_size) vs size | med (raw scan already finds a raw/b64 overlay; a `has_overlay`/`overlay_offset` field would be new) |
| 58 | Init-time decoding: TLS callbacks, `.init_array` / constructors, `DllMain` | gap | PE TLS dir `AddressOfCallBacks`; ELF `.init_array` entries beyond frame_dummy | [I] `readelf -x .init_array f`; `objdump -p f.exe \| grep -A5 TLS` | low-med |
| 59 | Exotic encodings: base58/62/91, z85, lz4/zstd/brotli | gap | b58 alphabet (no 0OIl), `<~` vs z85, lz4 frame `04 22 4d 18`, zstd `28 b5 2f fd` | [I] `tools/pybase62`, `tools/pybase91`, python `lz4`; [M] python `zstandard`, `brotli` | low-med |
| 60 | Entry point + function constant (`disassembly`, recover_code) | seen D1 (entry), D1/D8/D15 (disassembly) | `e_entry` / `AddressOfEntryPoint`+ImageBase; leaf `b8 imm32 c3` | [I] `readelf -h f \| grep Entry`; `objdump -d -M intel --no-show-raw-insn f`; `lib.binary.recover_return_constants` | high (carry-over fields) |
| 61 | Imports / NEEDED libs / interpreter | gap (D15 symbolized had getenv/strcmp/printf, unasked) | `.dynsym` UND, `DT_NEEDED`, `.interp`; PE import dir | [I] `readelf -dW f \| grep NEEDED; nm -D --undefined-only f; readelf -p .interp f`; `objdump -p f.exe` | med (cheap new field family; list order/spelling unknown) |
| 62 | Sections / segments / symbols lists | seen D1, D8 | pyelftools order incl. leading `""`; `.symtab` names, dupes kept | [I] pyelftools; `readelf -SW f; readelf -sW f` | high |
| 63 | Build provenance: GNU build-id, `.comment` compiler banner, Go buildinfo, rustc commit, PE timestamp/Rich/PDB | gap (Go buildinfo used internally) | `.note.gnu.build-id` (20-byte SHA1), `GCC: (Debian 15...)`, `go1.NN`, `/rustc/<sha>`, `TimeDateStamp`, RSDS | [I] `readelf -nW f`; `readelf -p .comment f`; `go version -m f`; `pefile` `FILE_HEADER.TimeDateStamp` | med (natural "compiler/language" id; label spelling unknown) |
| 64 | Demangling + C++ vtable/typeinfo | seen D2, D8 (has_cpp_*) | `_Z`, `_ZTV`, `$s` Swift, `_D` D, Nim `__mod_u`, Rust `_R`/`17h..E` | [I] `c++filt`, `rustfilt`, `swift-demangle`, `nim-demangle`, `llvm-cxxfilt-18`; GM wants MANGLED form | high (carry-over) |
| 65 | File hashes beyond sha256 (imphash, ssdeep, TLSH, md5) | gap | id names like `imphash`/`ssdeep`; only sha256 asked so far | [I] python `pefile` `get_imphash()`, `md5sum`; [M] ssdeep/tlsh python | low |

## Recognition cues (worker quick-reference)
```
STEP 1  file -b F ; xxd -l 64 F            -> container + arch + stripped/static/PIE in one line
  7f454c46 ELF: byte4 1=ELF32 2=ELF64; byte5 1=LE 2=BE (BE => read e_machine/HCFG ints big-endian)
  4d5a MZ->PE: Machine 0x14c i386 | 0x8664 x86-64 | 0xaa64 AArch64 | 0x1c0/0x1c4 ARM; "Mono/.Net" => pe_cli
  cffaedfe/cefaedfe Mach-O thin; cafebabe + small u32 nfat => Mach-O FAT (NOT a Java class) ; format word presumed `macho`
  504b0304 zip/jar/apk (keep nested jars whole) ; 00617373 \0asm => WASM ; 1b4c7561 Lua ; 1b4c4a LuaJIT ; FOR1..BEAM Erlang
  ':10' text lines => Intel HEX ; 'S0'/'S1' => S-record ; no magic + ARM vector table => raw firmware (rizin -m base)
STEP 2  rz-bin -I F   (or readelf -hlSW F)  -> lang, machine, bits, endian, static, stripped, pic, relro, nx, canary
  e_machine: 3 x86 | 62 x86-64 | 40 ARM | 183 AArch64 | 8 MIPS | 20 PPC | 21 PPC64 | 243 RISC-V | 2/43 SPARC
  labels: GM-confirmed x86-64/x86/AArch64/ARM (ELF), i386/x86-64 (PE); others = readelf spelling first, then EM_ name minus
  prefix; kind:integer => decimal e_machine. Dispatch on answer_format.kind, never on field name.
  no .symtab => stripped (answer [] / none / false); no INTERP => static; ET_DYN+INTERP => PIE; ET_REL => object file
  UPX0/UPX1 sections or "UPX!" or entropy>7.2 => PACKED: upx -t F; cp F /tmp/x; upx -d /tmp/x (fix zeroed UPX! first)
STEP 3  strings -a -n6 F | grep -m8 -E 'GCC:|clang|rustc|go1\.|GHC |OCaml|caml_|FPC |Crystal|zig|GNAT|gfortran|DMD|Nim|
        swift|_kDart|kfun:|__svm|MEI|nuitka|AU3!|Borland|MSVBVM|libcob|UPX|HCFG|SENGR'   -> toolchain + blob form
  toolchain -> tool: Go GoReSym -t -d -p | Rust rustfilt | .NET ilspycmd | jar javap -v -p / jadx | Swift swift-demangle
  Nim nim-demangle | PyInstaller pyinstxtractor+pycdc | AutoIt autoit-ripper | anything else: rizin -q -c 'aaa;afl' /
  analyzeHeadless (lib.binary.ghidra_decompile) | foreign arch: rizin -a <arch> / llvm-objdump-18 / Ghidra (no exec, qemu absent)
HCFG (every new member since D2)
  python: from lib.binary import hcfg_find, hcfg_scan; hcfg_find(open(F,'rb').read())  -> config, offset, encoding, key, crc_ok
  raw magic 'HCFG' | b64 'SENGR' | hex '48434647' | rot13 'FRATE' | b64-zlib 'eJ' | b64-gzip 'H4sI' -> covered by hcfg_scan
  accept only crc32(plain)==header crc AND JSON parses; keep scanning past decoys (D9 had two raw-magic decoys)
  NOT FOUND => blob is hidden: (1) packed? unpack; (2) AES S-box 637c777b / TEA 9e3779b9 / 'expand 32-byte k' => find key+IV
  near the call, decrypt with pycryptodome; (3) runs of mov [rbp-x], imm => stack-built: collect imms with capstone or
  emulate the builder with unicorn; (4) PE .rsrc / .NET resource / jar non-class entry / overlay past last section;
  (5) .init_array / TLS callback decoder => emulate it. Offsets: raw=the H, base64=the S (GM-confirmed); else first stored byte.
FIELDS: format = container only (elf/pe/macho?/jar; .NET pe_cli) | machine/architecture = container machine word |
  qualifier ids dNN_analysis_<tag>_<field> -> member whose file name has <tag> | config_* verbatim from HCFG JSON |
  has_<x>_section = literal section name | hex fields lowercase 0x | never chase the prompt's theme: answer only asked ids.
```

## Readiness gaps
```json
[
  {"id": "upx-packed-hcfg", "concept": "UPX-packed ELF/PE (plain and with scrubbed UPX! magic / renamed sections)", "priority": 1, "action": "prebuild",
   "detail": "Fixture: `upx -9` a C ELF + MinGW PE carrying an HCFG `.hcfg` section; variant with `UPX!` zeroed and UPX0/1 renamed. Target: solver detects (packer_info), restores magic, `upx -d` on a copy, then hcfg_find + header fields of the UNPACKED image; record which bytes (packed vs unpacked) sha256/format/has_hcfg_section are answered from. upx 4.2.4 installed."},
  {"id": "aes-tea-chacha-hcfg", "concept": "HCFG encrypted with AES-128/256 (ECB/CBC/CTR), XTEA, ChaCha20", "priority": 1, "action": "prebuild",
   "detail": "Fixture style of TARGETS.json: key/IV as adjacent 16/32-byte raw or printable strings, or derived (sha256 of campaign-like string). Extractor: locate cipher by constants (S-box 637c777b, 0x9e3779b9, 'expand 32-byte k'), try candidate keys within +-4 KB, accept when plaintext starts 'HCFG' and crc-gates. pycryptodome installed."},
  {"id": "stack-built-hcfg", "concept": "HCFG assembled at runtime from mov-immediate stores / per-char pushes", "priority": 1, "action": "prebuild",
   "detail": "Fixture: gcc -O0/-O2 C that writes the blob via volatile stack stores (x86-64 and AArch64). Extractor: capstone imm collection per function in store order, fallback unicorn emulation of the builder (no syscalls), then hcfg_find on the buffer. Offset convention unknown: record the first mov instruction's file offset as a speculative guess."},
  {"id": "multiarch-machine-labels", "concept": "ELF/PE/Mach-O machine words for i386, ARM, AArch64, MIPS(el), PPC/PPC64, RISC-V, SPARC + big-endian HCFG ints", "priority": 1, "action": "prebuild",
   "detail": "lib/knowledge.py ELF_MACHINE has only 4 entries. Fixtures: aarch64-linux-gnu-gcc (linkable) and clang-18 --target=<arch> -c (ET_REL .o; no lld installed) each with a `.hcfg` section, LE and BE. Expected labels = readelf spelling (x86, ARM, AArch64, MIPS R3000, PowerPC, PowerPC64, RISC-V, Sparc v9) with decimal e_machine for kind:integer; check hcfg_scan handles BE u16/u32 header fields."},
  {"id": "macho-hcfg-section", "concept": "Mach-O thin + fat universal binary with HCFG in a `__DATA,__hcfg` section", "priority": 1, "action": "prebuild",
   "detail": "clang-18 --target=x86_64-apple-macos -c and arm64-apple-macos -c produce MH_OBJECT files (no ld64); hand-pack a FAT header with python for the universal case. Targets: format label (`macho` presumed), machine from cputype (0x01000007 -> x86-64, 0x0100000c -> AArch64), has_hcfg_section on segment,section names, fat-vs-Java cafebabe disambiguation, lib.binary.macho_facts over both slices."},
  {"id": "floss", "concept": "Stack/tight/decoded string recovery", "priority": 1, "action": "tool",
   "detail": "github release mandiant/flare-floss (floss-vX-linux.zip, static binary) -> tools/bin/floss + bin/ link in setup/install_tools.sh; `floss --only stack tight decoded -- F`. Backs stack-built-hcfg without a hand-built emulator."},
  {"id": "qemu-user-static", "concept": "Run/observe foreign-arch ELF decoders (ARM/AArch64/MIPS/PPC/RISC-V)", "priority": 2, "action": "tool",
   "detail": "apt install qemu-user-static binfmt-support (only qemu-system-* are installed now). Use only inside the bwrap sandbox, never on the host; static analysis remains the default."},
  {"id": "wabt", "concept": "WebAssembly modules", "priority": 2, "action": "tool",
   "detail": "apt install wabt (wasm-objdump -x, wasm2wat, wasm-decompile). Pair with prebuild wasm-hcfg-data-segment."},
  {"id": "wasm-hcfg-data-segment", "concept": "WASM module with HCFG in an active data segment", "priority": 2, "action": "prebuild",
   "detail": "Hand-assemble with wat2wasm (after wabt install) or python bytes. Targets: format label (`wasm` presumed), architecture/machine for WASM (`wasm32`?), hcfg_offset = file offset of the segment bytes vs the segment's memory offset (record both)."},
  {"id": "diec", "concept": "Compiler/packer/language fingerprint for unknown toolchains", "priority": 2, "action": "tool",
   "detail": "github release horsicq/DIE-engine (die_lin64_portable tar) -> `diec -j F`. Complements `rz-bin -I` lang= and the STEP 3 strings regex when a new language lands."},
  {"id": "resource-overlay-hcfg", "concept": "HCFG in PE RT_RCDATA, .NET manifest resource, jar non-class entry, or file overlay", "priority": 2, "action": "prebuild",
   "detail": "Fixtures: MinGW-free path = patch a resource dir with pefile into a small PE; dnfile resource in a dotnet-built dll; jar with config.bin; ELF/PE with blob appended past the last section. Confirm hcfg_scan finds each and record offset convention (resource data start vs magic) plus a speculative has_overlay/overlay_offset."},
  {"id": "rolling-xor-hcfg", "concept": "Index-dependent xor (key+i, key^prev, xor with len/crc)", "priority": 2, "action": "prebuild",
   "detail": "Extend the bytemap/mxor fixture family: known-plaintext 'HCFG' recovers the start key and step; brute 256 x {add,sub,xor-prev} modes, crc-gate. Not covered by current single-byte or repeating-key xor."},
  {"id": "init-time-decoder", "concept": "Config decoded in .init_array constructor / TLS callback / DllMain", "priority": 3, "action": "prebuild",
   "detail": "Fixture with __attribute__((constructor)) decoding a stored blob; extractor finds .init_array targets and emulates them with unicorn (stdlib-free). Low until a day theme hints at runtime behaviour."},
  {"id": "checksec-fields", "concept": "PIE/RELRO/NX/canary/static as answer fields", "priority": 2, "action": "note",
   "detail": "`rz-bin -I` already prints pic/relro/nx/canary/static/stripped. GM spelling unknown: relro full/partial/none, booleans true/false like has_symtab. Add to playbook naming law before first sighting; no checksec install needed."},
  {"id": "imports-buildid-fields", "concept": "imports / needed / interpreter / build_id / compiler banner fields", "priority": 2, "action": "note",
   "detail": "Commands: `nm -D --undefined-only`, `readelf -dW|grep NEEDED`, `readelf -p .interp`, `readelf -nW` (build-id lowercase hex, no 0x), `readelf -p .comment`. Decide list order (dynsym table order like symbols) and submit new ids ALONE (all-or-nothing POST)."},
  {"id": "shared-object-relocatable", "concept": "ET_DYN .so / ET_REL .o / DLL members", "priority": 2, "action": "prebuild",
   "detail": "gcc -shared and gcc -c fixtures with .hcfg; expected elf_type ET_DYN/ET_REL, entry_point 0x0 for .o, exported-symbol config. PE DLL via objdump -p export table."},
  {"id": "new-language-fingerprints", "concept": "Haskell, OCaml, Fortran, Ada, V, Odin, COBOL, Kotlin/Native, Dart AOT, Nuitka", "priority": 2, "action": "note",
   "detail": "Cue strings are in the Recognition cues STEP 3 regex. All still answer format=elf/architecture=x86-64 per the D8-D15 law; risk is only where the HCFG literal lives (compressed Dart snapshot, Nuitka constants blob, GHC closures) -> hcfg_scan then Ghidra. gfortran/gnat/ocaml/ghc are NOT installed for fixture builds (apt gfortran gnat ocaml-nox ghc if prebuilds are wanted)."},
  {"id": "de4dot", "concept": "ConfuserEx / .NET string encryption", "priority": 3, "action": "tool",
   "detail": "github de4dot-cex (ViRb3) release; needs apt mono-runtime. `de4dot F -o clean.dll` then ilspycmd."},
  {"id": "erlang-lua-decompilers", "concept": "BEAM, Lua, LuaJIT bytecode", "priority": 3, "action": "tool",
   "detail": "apt erlang-base (beam_lib/beam_disasm), apt lua5.4 (`luac -l -l`), unluac jar (sourceforge), luajit-decompiler-v2 (github marsinator358) -- only if a bytecode container appears."},
  {"id": "binutils-multiarch", "concept": "objdump/readelf for MIPS/PPC/SPARC/RISC-V", "priority": 3, "action": "tool",
   "detail": "apt install binutils-multiarch; rizin, llvm-objdump-18 and Ghidra already cover disassembly, so this is a convenience only."},
  {"id": "exotic-codecs", "concept": "base58/base62/base91/z85 and lz4/zstd/brotli HCFG", "priority": 3, "action": "prebuild",
   "detail": "tools/pybase62 + tools/pybase91 + python lz4 exist; pip install zstandard brotli into the venv. Add hcfg_fixtures entries with speculative offset = first stored byte."},
  {"id": "ihex-srec-firmware", "concept": "Intel HEX / S-record / raw firmware members", "priority": 3, "action": "note",
   "detail": "objcopy -I ihex|srec -O binary already converts (srecord not needed). For raw blobs: rizin -a arm -b 16 -m <base>; format label unknown (`ihex`/`srec`/`raw`?) -> submit alone."}
]
```
