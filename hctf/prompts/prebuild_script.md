## Script lane: what to extend
Script challenges ship a cumulative zip of malicious-ish scripts (PowerShell, JScript, batch, VBS, Python carriers,
bash, Node, PHP/Lua/Perl polyglots, MOF, TypeScript, AutoIt, AppleScript, MSBuild ...; one new language per day). Each
script hides an operation "plan" (`v=3` marker lines / `k=v` fields / JSON) behind declared codecs: a literal
(`material`) under a representation (`rep`: hex, base64, char-code arrays, escapes, ...) and a `transform` (xor, add,
rolling, reverse, ...). The day's solver calls `lib/codec.py` `find_codecs(text)` -> `decode(material, rep, transform,
key)`; unknown names fall through to `_fallback` / `_generic_readings` (name-agnostic readings of the literal itself).
Your target names a layer, carrier or syntax the codec does not read yet (e.g. gzip/zlib/base32/base85 layers, UTF-16LE
or BOM'd sources, a new descriptor syntax `set x`, `x <- "..."`, `X := "..."`, `const X: &str`): extend the matching
reading in lib/codec.py (pure Python, bounded, no subprocess, < 2 s per file; return None when it cannot read it).
Never change what an existing reading returns for an already GM-verified case.

Fixtures: 2+ per target in `tests/data/script_fixtures/<name>.json` (+ optional `<name>.<ext>` source file):
either {"text" or sibling source, "expected_plain": "<the decoded plan text>"} (checked through `find_codecs`) or
{"material", "rep", "transform", "key", "expected"} (checked through `decode`), each with "generator_cmd" (how you
ENCODED it with an independent tool: `gzip | base64`, `iconv -t UTF-16LE`, `python3 -c ...` with stdlib only, `pwsh`,
`node`, `perl`) and "oracle_cmd" (an independent DECODER one-liner proving `expected`), plus one DECOY
({"decoy": true, "expected_plain": null}) that must not decode to a plan.

## Gate commands
`python3 tests/test_lane_fixtures.py`, `python3 tests/test_codec.py` + every script regression case of every day (the
harness runs them).
