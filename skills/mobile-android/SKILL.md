---
name: mobile-android
description: Huntress mobile-android lane - static analysis of the handed-out APK (AndroidManifest components and intent-filters/deep-link schemes, decompiled Java/Kotlin, resources and strings), then reproducing the app's own request to its challenge backend via hctf hb exec. Use for mobile-android-day-NN challenges.
---

# Scope
Only the Game Master's APK and the challenge backend it names are in scope. That backend is usually reachable only inside
the CTF network, so send its requests through `hctf hb exec -- curl ...` (runs on Homebase). Don't probe anything else.

# Tools (source bin/env.sh)
- `apktool d -f -o <work>/apktool app.apk` - decoded `AndroidManifest.xml`, `res/values/*.xml`, smali.
- `jadx -d <work>/jadx app.apk` (`--deobf` for obfuscated names) - readable Java/Kotlin.
- androguard in `.venv` for solvers:
  `from androguard.core.apk import APK; a=APK("app.apk"); a.get_package(); a.get_activities()` (+ `get_element` for exported flags/filters).
- `unzip -l`, `strings`, `exiftool` for embedded assets; native `.so` -> `binary-re` skill.

# Reading the challenge
1. Manifest: which component is `android:exported="true"`, and its `<intent-filter>` (`VIEW`+`BROWSABLE`+`<data scheme/host/path>`).
2. In jadx, follow that component: how it reads the incoming URI/extras, what request it builds (URL, headers, any id/credential
   from `strings.xml`/`BuildConfig`/a constant), and how it reads the reply.
3. The answer is the value the backend returns (e.g. `ANS-` + 16 hex). Build the same request the app would and run it on Homebase.

# Solver tips
Derive the package, component, URI and any embedded value from the APK with androguard rather than hard-coding them; variants
change the case reference, package suffix and embedded id. Keep the request-building logic in `solve.py` so each variant's
answer is fetched, not stored.
