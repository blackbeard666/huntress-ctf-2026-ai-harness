# Triage: metadata-forensics-day-03-bom-voyage

**Prompt:** A text export pipeline produced files that look identical in an editor but behave differently in scripts. Find the encoding landmines before they break the investigation.

**1 answer(s) expected.** Formats:
- `evidence-note-text-utf8-bom-present`: Determine text.utf8_bom_present for evidence-note.txt.  _(fmt: one of ['true', 'false']; norm: trim)_

## Artifacts

- **metadata-day-03-evidence.zip** (205 bytes) sha256 `207c74a175c574a3…`
  - file: Zip archive data, made by v2.0 UNIX, extract using at least v2.0, last modified Jan 01 2026 00:00:00, uncompressed size 33, method=deflate
  - signature: ZIP/APK/JAR/OOXML container
  - archive with 1 entries: ['evidence-note.txt']
  - **evidence-note.txt** (33 bytes) sha256 `1bfd9131619f82ce…`
    - file: ASCII text
    - preview: `Case 3DF9200ADB1A evidence note.`

_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._