# Triage: script-analysis-day-01-native-signals/mastery

**Prompt:** Three PowerShell specimens are on the table, and none of them will ever run. That's fine, because you only need to read them. Classify each script's intent, map its primary ATT&CK technique, and pull out the exact indicators sitting in plain sight.

**30 answer(s) expected.** Formats:
- `set1.resource-scenario`: What scenario best describes resource-sample.ps1?  _(fmt: one of ['resource_hijacking', 'synthetic_collection', 'synthetic_impact']; norm: trim)_
- `set1.resource-attack`: What is its primary MITRE ATT&CK technique ID?  _(fmt: T#### or T####.###; use the literal none only when the question permits it; norm: trim)_
- `set1.resource-url`: What exact URL is embedded in the resource sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set1.resource-wallet`: What exact wallet indicator is embedded in the resource sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set1.resource-mutex`: What exact mutex indicator is embedded in the resource sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set1.collection-scenario`: What scenario best describes collection-sample.ps1?  _(fmt: one of ['resource_hijacking', 'synthetic_collection', 'synthetic_impact']; norm: trim)_
- `set1.collection-attack`: What is its primary MITRE ATT&CK technique ID?  _(fmt: T#### or T####.###; use the literal none only when the question permits it; norm: trim)_
- `set1.collection-url`: What exact URL is embedded in the collection sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set1.collection-file`: What is the first exact filename indicator in the collection sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set1.collection-user-agent`: What exact user-agent indicator is embedded in the collection sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set1.impact-scenario`: What scenario best describes impact-sample.ps1?  _(fmt: one of ['resource_hijacking', 'synthetic_collection', 'synthetic_impact']; norm: trim)_
- `set1.impact-attack`: What is its primary MITRE ATT&CK technique ID?  _(fmt: T#### or T####.###; use the literal none only when the question permits it; norm: trim)_
- `set1.impact-extension`: What exact extension indicator is embedded in the impact sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set1.impact-note`: What exact recovery-note filename is embedded in the impact sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set1.impact-url`: What exact URL is embedded in the impact sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set2.resource-scenario`: What scenario best describes resource-sample.ps1?  _(fmt: one of ['resource_hijacking', 'synthetic_collection', 'synthetic_impact']; norm: trim)_
- `set2.resource-attack`: What is its primary MITRE ATT&CK technique ID?  _(fmt: T#### or T####.###; use the literal none only when the question permits it; norm: trim)_
- `set2.resource-url`: What exact URL is embedded in the resource sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set2.resource-wallet`: What exact wallet indicator is embedded in the resource sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set2.resource-mutex`: What exact mutex indicator is embedded in the resource sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set2.collection-scenario`: What scenario best describes collection-sample.ps1?  _(fmt: one of ['resource_hijacking', 'synthetic_collection', 'synthetic_impact']; norm: trim)_
- `set2.collection-attack`: What is its primary MITRE ATT&CK technique ID?  _(fmt: T#### or T####.###; use the literal none only when the question permits it; norm: trim)_
- `set2.collection-url`: What exact URL is embedded in the collection sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set2.collection-file`: What is the first exact filename indicator in the collection sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set2.collection-user-agent`: What exact user-agent indicator is embedded in the collection sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set2.impact-scenario`: What scenario best describes impact-sample.ps1?  _(fmt: one of ['resource_hijacking', 'synthetic_collection', 'synthetic_impact']; norm: trim)_
- `set2.impact-attack`: What is its primary MITRE ATT&CK technique ID?  _(fmt: T#### or T####.###; use the literal none only when the question permits it; norm: trim)_
- `set2.impact-extension`: What exact extension indicator is embedded in the impact sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set2.impact-note`: What exact recovery-note filename is embedded in the impact sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_
- `set2.impact-url`: What exact URL is embedded in the impact sample?  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_

## Artifacts

- **evidence-01.zip** (2464 bytes) sha256 `de8e0528c99ca6e2…`
  - file: Zip archive data, made by v0.0 UNIX, extract using at least v5.1, last modified Jan 01 2026 00:00:00, uncompressed size 1034, method=AES Encrypted
  - signature: ZIP/APK/JAR/OOXML container
  - archive with 3 entries: ['resource-sample.ps1', 'collection-sample.ps1', 'impact-sample.ps1']
- **evidence-02.zip** (2463 bytes) sha256 `d3b09e91db82fba3…`
  - file: Zip archive data, made by v0.0 UNIX, extract using at least v5.1, last modified Jan 01 2026 00:00:00, uncompressed size 1038, method=AES Encrypted
  - signature: ZIP/APK/JAR/OOXML container
  - archive with 3 entries: ['resource-sample.ps1', 'collection-sample.ps1', 'impact-sample.ps1']

_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._