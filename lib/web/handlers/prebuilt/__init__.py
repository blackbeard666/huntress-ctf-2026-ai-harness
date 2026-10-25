"""Generic web class handlers written OFF-PEAK by `hctf prebuild --lane web` (D25 D5), one module per coverage-atlas gap:
`prebuilt_<id>.py` with KEY_MAP / HANDLERS (handler names `prebuilt_<id>[_*]`, keyed on concept clue keys only) and
optional KEY_COMPANIONS -- the same contract as the per-day plugins one directory up, auto-loaded by
lib.web.handlers._load_plugins. Each is gated offline on recorded-kit fixtures (tests/data/web_fixtures/, replayed by
a 127.0.0.1 mock in tests/test_web_fixtures.py); network I/O only through lib.websolve.fetch.
"""
