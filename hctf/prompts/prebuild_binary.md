## Binary lane: what to extend
Binary challenges hide an `HCFG` config blob in a compiled program under a per-day encoding; `lib/binary.py`
`hcfg_scan` tries the known encodings over the program bytes. Your target names an encoding not yet scanned (e.g.
zlib/gzip, xor-then-base64, UTF-16LE, reversed base64, base32/base85, uppercase hex): add ONE small branch to
`hcfg_scan` (pure Python, bounded work: the scan runs inside the Mastery clock on 30-70 MB binaries) plus 2+
synthesized-blob fixtures in `tests/data/binary_fixtures/<name>.{bin,json}` = {"encoding", "expected_offset",
"expected_config", "generator_cmd", "oracle_cmd"} built by an INDEPENDENT encoder (shell tool / other library), and a
decoy blob that must NOT match. Never change how an existing encoding is reported.

## Gate commands
Every binary regression case of every day (the harness runs them).
