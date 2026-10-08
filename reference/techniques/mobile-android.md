# mobile-android — technique log (days 1-7; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Every APK so far was the same ~12.7 KB fixture with 6 zip entries: `AndroidManifest.xml`, `assets/huntress_puzzle.json`,
  `classes.dex`, `META-INF/FIXTURE-.{SF,RSA}`, `MANIFEST.MF`. One question, `answer` = `ANS-` + 16 uppercase hex.
- Each day has a new Android IPC/security THEME, written in the manifest `<meta-data android:name="huntress.mechanic">`
  (exported Activity, permissive deep link, nested Intent, mutable PendingIntent, allowBackup, exported ContentProvider,
  JavaScript-interface origin trust). The theme was flavour only: no day required exploiting it, even when the
  dex carried a matching stub class (d7 `WebViewBridge`).
- What actually varied day to day was the `codec` of `huntress_puzzle.json` (plain, reverse, base64, xor+key, split,
  hex, caesar+key). Within one day every variant (single, TT, all Mastery sets) used the same codec. Keys re-roll per
  variant. Expect a not-yet-seen codec name most days: decode it from the first 4 chars, which must become `ANS-`.
- In every APK, `.ChallengeActivity` builds a device-loopback URL `http://127.0.0.1:19090/mobile/attempt/<id>/evidence?
  case_id=..&client_secret=SECRET-..&proof=<answer>`. That backend is NOT reachable (it lives on the phone). The GM
  accepted the decoded puzzle value as the "backend evidence code" on all 7 days.
- Expect escalation (inference, see reference/HARDENING.md): the answer may move into the dex, resources or a decrypt
  routine. `lib.android.extract_answer` has the fallback chain for that case.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Puzzle codec** -- the same within one day, but `key` (xor byte d4, caesar shift d7: 10/18/9/3/4) and any
  split/offset parameters re-roll per variant: read them from `huntress_puzzle.json` every time.
- **Per-variant identity** -- case ref, package suffix `v<12 hex>`, `client_secret` and the loopback attempt slug
  change per variant (all Mastery sets shared one slug on d7). APK size stays 12704 B. None of these feed the answer.
- **Mastery packaging** -- `delivery N: <name>.apk` per set, often identically named: pair by sha256.
- **Answer location** -- so far always the puzzle JSON; if it decodes to nothing, fall back to dex/resources
  (`lib.android.extract_answer` chain) rather than assuming the sample's location.

## Recognition cues -> first move

| You see | First move |
|---|---|
| `*.apk` artifact, answer_format `ANS- + 16 uppercase hex` | `unzip -l x.apk`, then `unzip -p x.apk assets/huntress_puzzle.json` (takes seconds; it held the answer all 7 days). triage.md pre-extracts it to `work/extracted/` |
| puzzle JSON `{"codec":..,"data":..}` | decode per codec (table below). Check the result fullmatches `^ANS-[0-9A-F]{16}$` before you submit |
| Codec name not in the table below (d7 `caesar`) | compare `data[:4]` with `ANS-`: constant ord diff = shift, constant XOR = xor key. Implement, regex-check, submit |
| No puzzle JSON, or it decodes to no `ANS-` | `python -c 'from lib.android import extract_answer'` (zip scan, then dex strings incl. multidex, then apktool/jadx scan), then `strings -a classes*.dex \| grep ANS-` |
| Need the theme, component, scheme or exported flags | `droidasc getmanifest x.apk` (fast). `aapt dump badging x.apk` / `aapt dump xmltree x.apk AndroidManifest.xml` (installed). Also `lib.android.manifest_facts(apk)` |
| Need handler logic (URL built, extras read, constants) | `droidasc findrefs x.apk string <scheme or URL>`, then `droidasc getclass x.apk <pkg>.ChallengeActivity`; whole app: `jadx -d work/jadx x.apk` |
| Need resources or strings.xml / smali | `apktool d -f -o work/apktool x.apk` |
| Loopback `127.0.0.1:19090` in the code | do NOT chase it. It is device-local (refused on Homebase, times out elsewhere). The answer is static |
| Native `lib/*.so` inside the APK (not seen yet) | route to the binary-re skill (rizin / Ghidra headless) |
| Backup theme with a real `.ab` file (not seen yet) | Android backup = 24-byte header + zlib stream: `dd bs=24 skip=1 \| zlib-flate -uncompress \| tar x` (or abe.jar) |
| Mastery artifact names like `delivery N: foo_mastery_0N.apk` | strip the `delivery N: ` prefix to find the file (`lib.common.find_artifact` does this). Ids are `setN.answer` |

Puzzle codecs seen (`schema: huntress.mobile.puzzle.v1`):
- `plain`: data is the answer.
- `reverse`: reverse the string (`...-SNA` -> `ANS-...`).
- `base64`: `base64 -d`.
- `hex`: `xxd -r -p`.
- `caesar` (d7): `{data, key:int}`. Plain ASCII codepoint shift: `chr(ord(c) - key)` for EVERY char (digits and `-`
  shift too, e.g. `KX]7` key 10 -> `ANS-`). A letters-only mod-26 ROT is wrong. Derive the sign from `data[:4]` vs `ANS-`.
- `xor`: data is base64. b64-decode, then XOR every byte with the int `key` (0-255, changes per variant).
- `split`: `parts[]` + `order[]`, where `order[i]` is the OUTPUT SLOT of `parts[i]` (not `parts[order[i]]`). Try both
  readings and keep the one that fullmatches `ANS-`.
- The solvers also handle base32, rot13 and a `lib.decode.peel` fallback, ready for new codecs. `lib.android.decode_payload`
  has NO caesar branch yet (d7 solver did it inline).
- Unknown codec + int key: try the known-plaintext trick. `key_or_shift = f(data[:4], "ANS-")` (xor: byte ^; shift:
  ord diff). A constant diff across the 4 chars names the transform at once.

## Day by day

**Day 1 — Exported Trust** (mechanic "exported Activity and caller trust")
- The APK had an exported `.ChallengeActivity` with intent-filter VIEW+BROWSABLE `huntress01://exported-trust/unlock`.
  `onCreate` reads the `answer`/`case_id` extras and attaches an embedded `client_secret` constant plus `proof=<answer>`
  to the loopback evidence URL.
- Codec `plain`.
- Tools that worked: `droidasc getmanifest`, apktool, jadx, reading the asset straight from the zip.
- Dead end: about 4 min (first run 62s -> 300s) spent trying to reach `127.0.0.1:19090` via `hctf hb exec curl`:
  Homebase `ss -tln`, the GM proxy, `hctf openapi`, 10.0.0.219:19090. All refused or timed out.
- Submitted at about 5.4 min. CORRECT first try.
- The second worker log was a deliberate from-scratch replay (workspace reset). It re-derived the answer in about 74s
  and still hit the loopback for about 12s.
- TT and Mastery windows were 30s on day 1 (6-7s from day 2 on).

**Day 2 — Deep Link Drift** (mechanic "permissive scheme, host, and path validation")
- Same shape as day 1. The handler did no host or path checks.
- Codec `reverse`. Submitted at 33s, CORRECT first try.
- The second worker log was not a re-solve. A harness re-start had overwritten `single_solve/start.json` with a body
  lacking `attempt_id`/`answer_ids`, so the completion gate could not match the CORRECT submission. The fix was to
  restore the original start from `log.jsonl`.
- Mastery: 8 expired attempts. This was a clock problem, not a solver problem: 6s window, with 3 APK downloads and the
  submit inside it. Homebase prewarm fixed it later.

**Day 3 — Intent Injection** (mechanic "attacker-controlled nested Intent")
- Same shape. The nested-Intent extras (`answer`, `case_id`) relay to the loopback evidence URL.
- Codec `base64`. Submitted at 18s, CORRECT first try. The worker skipped the backend because it trusted the day 1-2
  pattern.

**Day 4 — Pending Intent Relay** (mechanic "mutable PendingIntent relay")
- Same shape.
- Codec `xor`: `{data:<base64>, key:<int>}`. b64-decode, then single-byte XOR. The key differed across TT and each
  Mastery set (e.g. 103, 189, 31, 81), so derive it from the JSON and never hard-code it.
- About 30s lost re-checking the loopback with `hb exec curl`. Submitted at 77s, CORRECT first try.

**Day 5 — Backup Spill** (mechanic "backup-admitted SharedPreferences", manifest `allowBackup="true"`)
- No backup file was shipped. Same deep-link shape (the WebView loads the evidence URL).
- Codec `split`: `parts` (3 fragments) + `order`. The `parts[order[i]]` reading gave a string with no `ANS-` prefix (dead
  end). Treating `order[i]` as the slot of `parts[i]` was correct.
- Submitted at 27s, CORRECT first try. TT/Mastery window 7s (elapsed 5.3s: start 1.8, download 2.3, solve 0.08,
  submit 1.2).

**Day 6 — Provider Paths** (mechanic "exported ContentProvider path")
- New component: `<provider .ProviderPathsProvider exported=true authorities=<pkg>.evidence grantUriPermissions=true>`
  with no path-permission. Its `query()` is a stub that returns null/0, so there were no records to dump.
- Codec `hex`. Same deep-link relay.
- About 2.3 min lost (42s -> 184s) on the loopback curl and on grepping hctf/gm.py and reference/ for a backend route,
  before falling back to the day 1-5 pattern.
- Submitted at about 3 min, CORRECT first try.

**Day 7 — WebView Bridge** (mechanic "JavaScript interface origin trust"; prompt "Cross a challenge-owned WebView
bridge through an untrusted origin ... Submit only the exact backend answer code")
- Same fixture (12704 B, 6 entries). Deep link `huntress07://webview-bridge` pathPrefix `/unlock` on exported
  `.ChallengeActivity`; dex adds a `WebViewBridge` class (`describe`/`encode`/`getData`) that was a stub. Same loopback
  evidence URL. All static, no backend.
- New codec `caesar`, key 10: ASCII shift of every char by `-key`. Spotted by eye in one step (`K`-10=`A`,
  `]`-10=`S`, `7`-10=`-`).
- Worker flow: read triage.md + pre-extracted `assets/huntress_puzzle.json`, wrote the caesar branch into solve.py,
  `hctf submit --from-solver`. No loopback chase, no decompile. 5 tool calls.
- Start 13:00:10Z -> CORRECT 13:01:02Z = 52s, first try. TT (9s window) correct in 3.5s, key 18. Mastery (10s
  window) correct in 2.3s, keys 9/3/4. Zero wrong submissions.

## GM answer conventions learned
- One field, `answer`. Single solve and TT use id `answer`; Mastery uses `set1.answer`..`set3.answer`, one APK per set.
- Format is `ANS-` + exactly 16 UPPERCASE hex, normalization `exact`. Uppercase the hex after decoding and add no
  whitespace.
- No mobile answer has ever been rejected (zero wrong submissions on days 1-7). The GM accepts the decoded
  `huntress_puzzle.json` value as the "backend evidence code" even though the prompt says "invoke ... return the backend
  evidence code".
- Mastery feedback is per set: `{"result":"accepted","remaining":N}` after each set, then `CORRECT` on the last. An
  empty submit after the deadline returns `expired`.
- Prompt boilerplate repeats daily: "For case MOB-NN-<10 hex> in package com.huntress.mobile.dNN.v<12 hex>". The case
  ref and package suffix change per variant and were never needed for the answer.

## Pitfalls that cost time
- **Chasing the loopback backend** was the only recurring time sink: about 4 min (d1), about 30s (d4) and about 2.3 min
  (d6). `127.0.0.1:19090` is the phone's own loopback. If the decoded asset already matches the answer_format, submit it.
- **split codec order semantics:** two plausible readings exist. Validate the candidates against the answer regex
  instead of guessing.
- **xor codec:** `data` is base64 first, and `key` may vary per variant (int; the solvers also accept a numeric string
  or a repeating string key).
- **caesar codec:** the shift is over raw codepoints, not the alphabet (`data` contains `]`, `` ` ``, `<`, `>` --
  JSON-escaped as `\u003c`/`\u003e`, so json-load it, never regex the raw text). Keep only the candidate that
  fullmatches `^ANS-[0-9A-F]{16}$`.
- **Mastery filenames** carry a literal `delivery N: ` prefix. A naive path lookup fails.
- **6-10s timed windows** (day 2+; d7 TT 9s, Mastery 10s) are dominated by start + download + submit. Solve time is about 0.1s, so do no
  decompiling in-window: read the zip entry directly. Day 2 Mastery expired 8 times before Homebase routing.
- **Don't decompile when you don't need to.** Every solve so far (d1-d7) needed only the asset; the manifest was context only.
  Keep jadx/apktool for the day the asset is missing or lacks `ANS-`.
- **Harness, not GM:** a re-start can clobber `single_solve/start.json` (no attempt_id), which makes a solved lane look
  incomplete. Check `hctf status` before re-solving.
- Watch for the cheap escalation (hypothesis in reference/HARDENING.md, not yet seen): answer moved into the dex,
  `strings.xml`, BuildConfig or a native lib, or computed by a decrypt routine. Then trace `ChallengeActivity` and run
  `lib.android.extract_answer`.
