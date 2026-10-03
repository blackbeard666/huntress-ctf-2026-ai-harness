# Triage: script-analysis-day-02-encoded-intent

**Prompt:** Windows Script Host has JScript plans for execution, download, upload, and impact. Carry your PowerShell findings forward, tell a function call from an invocation or a property access, and work out which script hands off to which.

## Artifacts

- **evidence.zip** (12628 bytes) sha256 `7743a1af7c51d095…`
  - file: Zip archive data, made by v0.0 UNIX, extract using at least v5.1, last modified Jan 01 2026 00:00:00, uncompressed size 1038, method=AES Encrypted
  - signature: ZIP/APK/JAR/OOXML container
  - archive with 12 entries: ['resource-sample.ps1', 'collection-sample.ps1', 'impact-sample.ps1', 'host-context.js', 'memory-stage.js', 'embedded-write.js', 'remote-write.js', 'local-dispatch.js', 'staged-handoff.js', 'outbound-transfer.js', 'impact-plan.js', 'relay-handoff.js']

_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._