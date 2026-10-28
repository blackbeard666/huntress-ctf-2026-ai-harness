## Binary lane: what to extend
Your target's `kind` says which of the two jobs it is.

### Kind 1 (no `kind`, the default): an HCFG storage encoding
Binary challenges hide an `HCFG` config blob in a compiled program under a per-day encoding; `lib/binary.py`
`hcfg_scan` tries the known encodings over the program bytes. Your target names an encoding not yet scanned (e.g.
zlib/gzip, xor-then-base64, UTF-16LE, reversed base64, base32/base85, uppercase hex): add ONE small branch to
`hcfg_scan` (pure Python, bounded work: the scan runs inside the Mastery clock on 30-70 MB binaries) plus 2+
synthesized-blob fixtures in `tests/data/binary_fixtures/<name>.{bin,json}` = {"encoding", "expected_offset",
"expected_config", "generator_cmd", "oracle_cmd"} built by an INDEPENDENT encoder (shell tool / other library), and a
decoy blob that must NOT match. Never change how an existing encoding is reported.

### Kind 2 (`"kind": "generic_field"`): a generic field family
The binary contract is CUMULATIVE: every earlier day's family comes back under `dNN_` fields, and most new fields are
new QUESTIONS on old families (D28: 24 of 31 empties -- counts, `has_<lang>_runtime`, sha256 of ordered sets,
`cli_runtime`, overlay size). The day's lane solver fills only what it knows; a field it leaves EMPTY goes to
`lib.binary.generic_field(data, field, question, member, group=, answer_format=)`, which reads the GM's own spec
sentence ("Count the nonempty ELF symbol names matching /re/", "true exactly when the final bytes contain X or Y",
"sort ..., join with one LF byte and no trailing LF, then SHA-256") over whatever container the member really is
(ELF / PE / .NET / Mach-O / JAR / class / wasm), then the field-name families. It never overrides a lane answer.
Read the block comment above `GENERIC_FIELDS` in `lib/binary.py` first: it lists the per-format rules that are
GM-confirmed (ELF e_shnum incl. index 0 vs PE NumberOfSections; .symtab only, stripped -> []; sorted LF-joined name
sets; ':'-joined member digests in central-directory order). Do not change those.

Your job: make ONE more field family answerable, as ONE rule added with
`register_generic("<target id>", r"<field-suffix regex>", fn, formats=(...))` at the end of `lib/binary.py`
(`fn(ctx, match) -> str | None`; `ctx` is a `GenericCtx`: `ctx.data`, `ctx.q` (question), `ctx.fmt`, `ctx.group`,
`ctx.symbols(kind)`, `ctx.sections()`, `ctx.section_bytes(name)`, `ctx.jar()`, `ctx.jvm()`, `ctx.dotnet()`,
`ctx.magic()`, `ctx.memo(key, make)`). Or extend the spec grammar (`_gf_predicate` / `_gf_count` / `_gf_sha`) when
the target is a grammar gap. Reuse the existing readers (`elf_symbol_names`, `coff_symbol_names`, `macho_symbol_names`,
`cli_header`, `elf_header_facts`, `pe_header_facts`, `macho_layout`, `wasm_layout`, `jar_jvm_facts`,
`dotnet_meta_facts`, `overlay_info`, `overlay_header_facts`). Do not write new container parsers. Return None when
unsure: a wrong value in a timed mode fails the attempt, while a None leaves the field to the day's LLM worker.
Bounded work: well under 50 ms per call on a 70 MB member.

Fixtures go in `tests/data/binary_fixtures/generic/<member>.<field>.json` = {"kind": "generic_field", "member":
"<file in that dir>", "field", "question" (GM-style wording), "answer_format", "expected" (null = must stay None),
"generator_cmd", "oracle_cmd"}. Build the member with a real toolchain (gcc / strip / mingw-gcc / zig cc / dotnet /
javac+jar; see `gen_generic.sh`) and take `expected` from an INDEPENDENT reader (readelf / objdump / otool / llvm-readobj
/ pefile / pyelftools / dnfile / unzip -l one-liners). Never use lib.binary for `expected`. You need at least 2 fixtures
per format you claim and one decoy (wrong format or field absent). Add your generator lines to `gen_generic.sh`.

## Gate commands
- `python3 tests/test_d28_binary_breadth.py`: replays every generic fixture, the 24 GM-confirmed D28 residual
  fields, the never-override check and the family x format matrix against independent parsers (~30 s). Run it ONCE
  before you stop.
- Every binary regression case of every day (the harness runs them).
