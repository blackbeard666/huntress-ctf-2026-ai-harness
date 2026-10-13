"""LLM-prebuilt SPECULATIVE metadata extractors (`hctf prebuild --lane metadata-forensics`).

One module per format: `<fmt>.py` with a literal `FIELDS = {("<fmt>", "<field>"): "<func>", ...}` and the functions
`func(data: bytes | None, ctx: dict) -> raw value | "none" | None` (spelled by lib.meta.spell). Every module ships
>= 2 fixtures in tests/data/meta_fixtures/<fmt>/ (incl. a decoy). Never imported eagerly: lib.meta reads FIELDS with
ast and imports a module only when a contract asks one of its fields. Never `verified` here -- the post-run ratchet
promotes a GM-confirmed field by adding a verified entry to lib.meta._BUILTIN (and removing it from FIELDS).
"""
