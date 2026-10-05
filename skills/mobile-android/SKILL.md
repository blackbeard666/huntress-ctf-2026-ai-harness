---
name: mobile-android
description: Huntress mobile-android lane - static analysis of the handed-out APK (AndroidManifest components and intent-filters/deep-link schemes, decompiled Java/Kotlin, resources and strings), then reproducing the app's own request to its challenge backend via hctf hb exec. Use for mobile-android-day-NN challenges.
---

# Scope
Only the Game Master's APK and the challenge backend it names are in scope. That backend is usually reachable only inside
the CTF network, so send its requests through `hctf hb exec -- curl ...` (runs on Homebase). Don't probe anything else.

# Tools (source bin/env.sh)
- **`lib.android` — use this in solvers.** `extract_answer(apk)` recovers `ANS-<16 hex>` through a robust
  fallback chain (puzzle-json decode -> raw zip-entry scan -> dex strings (multidex) -> apktool/jadx
  decompiled scan), so it keeps working when the answer MOVES out of `assets/huntress_puzzle.json` into the
  dex/resources/code. `manifest_facts(apk)` returns package/permissions/allowBackup/debuggable + per-component
  exported/intent-filter/deep-link data. Never write a bare `huntress_puzzle.json`-only reader again.
- **`droidasc` (ASC).** On-demand APK decompiler, fast and low-RAM (good for big APKs and Homebase):
  - `droidasc getmanifest app.apk` - decoded AndroidManifest (exported flags, intent-filters, schemes).
  - `droidasc findrefs app.apk string|type|method|field <needle>` - cross-refs across all DEX (e.g. a scheme, a URL, a const).
  - `droidasc listclass app.apk --prefix com.foo` then `droidasc getclass app.apk <class> -o out.java` - decompile just the class you need.
- `jadx -d <work>/jadx app.apk` (`--deobf`) - whole-app Java, fallback when you need the full picture.
- `apktool d -f -o <work>/apktool app.apk` - smali + `res/values/*.xml` when you need resources/strings.
- androguard in `.venv` for solvers: `from androguard.core.apk import APK; a=APK("app.apk"); a.get_package(); a.get_activities()`.
- native `.so` -> `binary-re` skill.

# Reading the challenge
1. `droidasc getmanifest`: which component is `android:exported="true"`, and its `<intent-filter>` (`VIEW`+`BROWSABLE`+`<data scheme/host/path>`).
2. `droidasc findrefs` the scheme/host to locate the handler, then `getclass` it: how it reads the incoming URI/extras, what request it
   builds (URL, headers, any id/credential from `strings.xml`/`BuildConfig`/a constant), and how it reads the reply.
3. The answer is the value the backend returns (e.g. `ANS-` + 16 hex). Build the same request the app would and run it on Homebase
   via `hctf hb exec -- curl ...` (the backend is only reachable inside the CTF network).

# Solver tips
Derive the package, component, URI and any embedded value from the APK with androguard rather than hard-coding them; variants
change the case reference, package suffix and embedded id. Keep the request-building logic in `solve.py` so each variant's
answer is fetched, not stored.
