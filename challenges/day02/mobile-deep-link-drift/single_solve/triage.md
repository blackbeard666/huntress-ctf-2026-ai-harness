# Triage: mobile-android-day-02-deep-link-drift

**Prompt:** Day 1 taught you the roads. Now learn which ones are actually guarded — tell verified routing apart from a scheme and host that wave everybody through.

## Artifacts

- **deep_link_drift.apk** (12704 bytes) sha256 `9211e52f1844b86e…`
  - file: Android package (APK), with AndroidManifest.xml, with APK Signing Block
  - signature: ZIP/APK/JAR/OOXML container
  - signature: AndroidManifest -> $mobile-android
  - archive with 6 entries: ['AndroidManifest.xml', 'assets/huntress_puzzle.json', 'classes.dex', 'META-INF/FIXTURE-.SF', 'META-INF/FIXTURE-.RSA', 'META-INF/MANIFEST.MF']
  - **APK** -> $mobile-android (droidasc getmanifest / findrefs / getclass)

_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._