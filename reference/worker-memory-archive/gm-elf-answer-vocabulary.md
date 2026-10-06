---
name: gm-elf-answer-vocabulary
description: "Huntress GM's accepted/rejected spellings for binary-lane answers (ELF header fields, format elf/pe/pe_cli/jar, PE i386, pyelftools-raw section/symbol lists), plus batch-submit caveat"
metadata:
  node_type: memory
  type: project
  originSessionId: ee21cdd6-58cd-4a3b-98a6-a94c77db33ef
  modified: 2026-10-04T04:54:54.754Z
---

Huntress GM binary-lane vocabulary (the source of truth is `lib/knowledge.py`; this is the summary):
- ELF (Day 01): elf_class `ELF64` (not `ELFCLASS64`), elf_type `ET_EXEC` (not `EXEC`), machine `x86-64` (not `EM_X86_64`), endianness `little` (not `little endian`).
- Format (Day 02): ELF -> `elf`, native PE -> `pe`, both confirmed per-field. An older note said every PE spelling was rejected. That was wrong: a per-set POST is all-or-nothing, and the real failures in those sets were other fields.
- Day 03 "Table Manners": PE i386 machine -> `i386` (`x86` rejected). section_names = pyelftools `iter_sections()` names INCLUDING the "" NULL section. symbols = non-empty `.symtab` names in order. .NET metadata_version `v4.0.30319`. .NET `format`: pe, dotnet, pe32, .net, cil all REJECTED. d01 disassembly: hex-immediate capstone of recover_code, main and whole .text REJECTED (decimal-immediate form accepted, see below).

- Day 04 "Go Fish": Go ELF `architecture` -> `x86-64` (machine vocab); the buildinfo GOARCH `amd64` was REJECTED. Day 3 d01 disassembly later CONFIRMED as capstone intel recover_code with DECIMAL immediates; .NET format CONFIRMED `pe_cli`.
- Day 06 "Pool Party": Java .jar `format` -> `jar` CONFIRMED; the compound `jar_jvm` was REJECTED, so the container_runtime (pe_cli) pattern does not carry over to Java. The config was a base64 HCFG blob in a constant-pool String.

**Why:** the harness allows only a few wrong tries per non-flag field (6), and a multi-field submit with one wrong value comes back plain `incorrect`, which counts against every field in it.
**How to apply:** reuse confirmed spellings; probe unsure fields one id per submit; build JSON payloads with json.dumps, not shell quoting (backslashes).
