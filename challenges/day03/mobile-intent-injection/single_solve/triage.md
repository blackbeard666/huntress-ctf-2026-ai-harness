# Triage: mobile-android-day-03-intent-injection

**Prompt:** Trace attacker-controlled extras through an internal navigation boundary.

**1 answer(s) expected.** Formats:
- `answer`: For case MOB-03-8006859B52 in package com.huntress.mobile.d03.v8006859b5257: Trace attacker-controlled extras   _(fmt: ANS- followed by exactly 16 uppercase hexadecimal characters; no spaces or expla; norm: exact)_

## Artifacts

- **intent_injection.apk** (12704 bytes) sha256 `3127e3a93000b594…`
  - file: Android package (APK), with AndroidManifest.xml, with APK Signing Block
  - signature: ZIP/APK/JAR/OOXML container
  - signature: AndroidManifest -> $mobile-android
  - archive with 6 entries: ['AndroidManifest.xml', 'assets/huntress_puzzle.json', 'classes.dex', 'META-INF/FIXTURE-.SF', 'META-INF/FIXTURE-.RSA', 'META-INF/MANIFEST.MF']
  - **APK** -> $mobile-android (droidasc getmanifest / findrefs / getclass)

_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._