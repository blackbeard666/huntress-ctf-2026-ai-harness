## Warmups lane: what to extend
Each warmups Single is one sentence under ONE classical codec that changes daily; Mastery mixes every earlier day's
codec line by line. `lib/warmups_codecs.py` holds `DAYS` (every GM-confirmed codec as an exact encoder + decoder) and
`CANDIDATES` (a broad try-list of classical encoders for identifying an unknown day's codec); `lib/decode.py`
`register_free(...)` registers speculative keyless free-text decoders. Your target names a codec family not yet in
`CANDIDATES`: add its encoder + decoder there (speculative, tagged with no day), plus 2+ fixtures in
`tests/data/warmups_fixtures/<name>.json` = {"plain", "encoded", "generator_cmd", "oracle_cmd"} where `encoded` was
produced by an INDEPENDENT implementation (a standard tool or a different library), plus one decoy line your decoder
must reject. Never edit a `DAYS` entry: those are GM-confirmed.

## Gate commands
`python3 tests/test_codec.py` + every warmups regression case of every day (the harness runs them).
