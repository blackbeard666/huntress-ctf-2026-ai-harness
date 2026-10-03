# Triage: mobile-android-day-01-exported-trust

**Prompt:** Identify an exported deep-link Activity that attaches an embedded client credential, invoke it with the correct case reference, and return the backend evidence code.

## Artifacts

- **exported_trust.apk** (12704 bytes) sha256 `64169ad2f314746e…`
  - file: Android package (APK), with AndroidManifest.xml, with APK Signing Block
  - signature: ZIP/APK/JAR/OOXML container
  - signature: AndroidManifest -> $mobile-android
  - archive with 6 entries: ['AndroidManifest.xml', 'assets/huntress_puzzle.json', 'classes.dex', 'META-INF/FIXTURE-.SF', 'META-INF/FIXTURE-.RSA', 'META-INF/MANIFEST.MF']
  - **APK** -> $mobile-android (droidasc getmanifest / findrefs / getclass)

_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._