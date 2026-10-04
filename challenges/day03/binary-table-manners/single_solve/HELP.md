# HELP: Table Manners single solve — 23/24 confirmed; 1 field (d03_analysis_format) genuinely blocked

Status after operator probing 2026-10-04:

## RESOLVED — d01_analysis_disassembly  ✅
GM accepted `["mov eax, 8100","ret"]` for the recover_code leaf.
Rule: capstone intel `"{mnemonic} {op_str}"` with the DEFAULT `, ` separator, immediates in **DECIMAL**
(8100 == 0x1fa4). Solver `disassembly()` now emits this (regex-converts `0x..` -> decimal); verified it reproduces
the accepted value, and generalizes to timed/mastery variants. Recorded in `lib/knowledge.py`.

## BLOCKED — d03_analysis_format  ❌ (concept known, exact GM label not derivable)
The artifact is a .NET 8 (net8.0) IL PE32, machine i386 (confirmed), CLI metadata root v4.0.30319 (confirmed).
`file`: "PE32 executable ... Intel i386 Mono/.Net assembly". `objdump -f`: "pei-i386".
**50 candidate spellings submitted, all `incorrect`** (full list in `lib/knowledge.py:DOTNET_FORMAT_REJECTED`),
covering every form emitted by file/objdump/pefile/LIEF plus every .NET/IL/CLR token in lower/upper/dotted case,
BFD targets, modern-.NET monikers, multi-word labels, and the literal `none`.

Conclusion: the generator stores a **synthetic** label for this field (confirmed pattern — it also renders
disassembly immediates in non-standard decimal). It is not reproducible from the bytes with any standard tool.
Resolving it needs the generator source or an organizer hint, NOT more blind probing (would just burn GM attempts).
Every other binary field across single/time_trial/mastery is solved; only this one sub-field (present in every set)
keeps the binary timed modes from scoring.
