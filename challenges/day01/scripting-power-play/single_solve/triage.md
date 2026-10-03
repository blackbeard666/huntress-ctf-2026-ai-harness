# Triage: script-analysis-day-01-native-signals

**Prompt:** Three PowerShell specimens are on the table, and none of them will ever run. That's fine, because you only need to read them. Classify each script's intent, map its primary ATT&CK technique, and pull out the exact indicators sitting in plain sight.

## Artifacts

- **evidence.zip -> resource-sample.ps1** (2465 bytes) sha256 `07e61f33b72ae646…`
  - file: Zip archive data, made by v0.0 UNIX, extract using at least v5.1, last modified Jan 01 2026 00:00:00, uncompressed size 1038, method=AES Encrypted
  - signature: ZIP/APK/JAR/OOXML container
  - archive with 3 entries: ['resource-sample.ps1', 'collection-sample.ps1', 'impact-sample.ps1']

_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._