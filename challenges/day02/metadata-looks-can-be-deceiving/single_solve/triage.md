# Triage: metadata-forensics-day-02-looks-can-be-deceiving

**Prompt:** The extensions claim one story; the first sixteen bytes tell another. Identify what each artifact actually is and isolate the deliberate disguise.

## Artifacts

- **metadata-day-02-evidence.zip** (287 bytes) sha256 `c356020d0dafda86…`
  - file: Zip archive data, made by v2.0 UNIX, extract using at least v2.0, last modified Jan 01 2026 00:00:00, uncompressed size 126, method=deflate
  - signature: ZIP/APK/JAR/OOXML container
  - archive with 1 entries: ['evidence-note.txt']
  - **evidence-note.txt** (126 bytes) sha256 `672840e4d6e79fdb…`
    - file: ASCII text
    - preview: `Huntress Metadata Forensics evidence note
Case marker: CASE-52F88184C9D3
Endpoint: WS-8ADC1123
Collected sequence: 5558590970`

_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._