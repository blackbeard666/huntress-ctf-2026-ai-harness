# mobile-android — technique log (days 1-16; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Every APK so far was the same ~12.7 KB fixture: `AndroidManifest.xml`, `assets/huntress_puzzle.json`, `classes.dex`,
  `META-INF/FIXTURE-.{SF,RSA}`, `MANIFEST.MF` (6 entries). Extras: d10 `res/xml/network_security_config.xml` +
  `resources.arsc` (8 entries); d15-d16 `lib/x86_64/libarena.so` (7 entries, ~12.8 KB). One question, `answer` = `ANS-` +
  16 uppercase hex.
- Each day has a new Android IPC/security THEME, written in the manifest `<meta-data android:name="huntress.mechanic">`
  and in a dex string `DAY-NN:<theme_id>:<mechanic>` (exported Activity, permissive deep link, nested Intent, mutable
  PendingIntent, allowBackup, exported ContentProvider, JS-interface origin trust, cleartext session, permissive X509
  trust manager, NSC exception, SharedPreferences credential, client-side SQLite authz, app-controlled Keystore key,
  predictable nonce d14, `jni_secret` "challenge-owned JNI shared library" d15, `jni_length` "Java-to-native validation
  mismatch" d16). The theme was flavour only: no day required exploiting it, even with a matching stub class
  (`WebViewBridge`, `TrustEveryone`, `PredictableCrypto`, `NativeLibrarySecrets`, `JNIBoundary`) or a prompt demanding a
  live action. d16 is the first day whose TT/Mastery build had a REAL gate in code (a JNI export guarding the answer),
  yet the answer was still a literal in the asset and in `.rodata`.
- What varied day to day was the `codec` of `huntress_puzzle.json` (plain, reverse, base64, xor+key, split, hex,
  caesar+key, then repeats; d15-d16 `native`, whose `data` is already the plaintext answer). The dex also holds
  the codec name next to a `CODEC` string constant. Keys re-roll per variant. A new codec name is possible any day:
  decode it from the first 4 chars, which must become `ANS-`.
- **Since d15 Mastery is a MIXED-DAY bundle.** The 5 sets are APKs from earlier days plus one of today's (d15: d01 plain,
  d07 caesar, d10 split, d14 caesar, d15 native; d16: d01 plain, d04 xor, d11 xor, d13 base64, d16 native), all under
  today's prompt text. Solve each set from its own puzzle JSON, never from "today's codec".
- In every APK, `.ChallengeActivity` builds a device-loopback URL `http://127.0.0.1:19090/mobile/attempt/<id>/evidence?
  case_id=..&client_secret=SECRET-..&proof=<answer>`. That backend is NOT reachable (it lives on the phone). The GM
  accepted the decoded puzzle value as the "backend evidence code" on all 16 days.
- Escalation watch: d15 shipped the first native lib and d16 the first native GATE (`Java_<pkg>_JNIBoundary_nativeEvidence
  (env, cls, int len)` returns `arena_value` only if `huntress_arena_length_accepts(len, 0)`: `len > 0xffff &&
  (uint16)len == 0`, i.e. 65536). The answer was STILL in the asset and in `.rodata`. If a later day drops it from the
  asset, read the gate statically and take the value it returns (`lib.android.extract_answer` has the fallback chain).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Puzzle codec** -- single + TT always shared the day's codec. `key` (xor byte d4, d11: 81/109/205,29,44, d16 Mastery
  d04-set 21, d11-set 232; caesar shift d7: 10/18/9/3/4, d14: 9/10/17,4,7, d15 Mastery d07-set 15, d14-set 4) and split/offset parameters re-roll per variant:
  read them from `huntress_puzzle.json` every time. Keyless codecs (`reverse`, `base64`, `native`) differ only in `data`.
  Rule: decode by declared codec, regex-check `^ANS-[0-9A-F]{16}$`, else `decode_any`; unknown name -> known-plaintext
  `ANS-` trick.
- **Mastery set mix (NEW d15)** -- sets can be fixtures of DIFFERENT days (codec, theme, package `dNN`, extra entries
  like `res/xml/...` or `lib/x86_64/*.so` all differ per set; the puzzle JSON `day` field and dex `DAY-NN:` tag name the
  source day). The day picks re-roll per attempt (d15: 01/07/10/14/15 vs 03/07/09/13/15; d16: 01/04/11/13/16); the last
  set was today's. d16: the QUESTION's case ref/package (`MOB-06-..`, `d08`, `d14`) did NOT match the APK's own
  (`MOB-04`, `d11`, `d13`), so the contract text does not predict the codec either.
  Rule: per-set, codec-agnostic decoding (`puzzle_candidates` over each APK) -- never branch on the day or case ref.
- **Per-variant identity** -- case ref `MOB-NN-<10 hex>`, package suffix `v<12 hex>`, `client_secret` and the loopback
  attempt slug change per variant. None of these feed the answer.
- **Mastery packaging** -- `delivery N: <name>_mastery_0N.apk` per set: pair by sha256. Set count varies: 3 sets
  (d1-d7, d10-d14), 5 sets (d8, d9, d15, d16). Loop over the contract's answer_ids, never assume 3.
- **Answer location** -- so far always the puzzle JSON (d15-d16: also duplicated in the `.so` `.rodata`); if it decodes
  to nothing, fall back to dex/resources/native (`raw_entry_scan`, `dex_strings`, `strings -a lib/*/*.so | grep ANS-`).
- **Native lib shape (NEW d16)** -- same day, different `.so` builds: the single variant shipped the d15-style 13648 B lib
  (exports `huntress_arena_secret`/`huntress_arena_day` only, dex 2584 B, no `loadLibrary`); TT and the Mastery d16 set
  shipped a 14128 B lib adding `huntress_arena_length_accepts` + `Java_<pkg>_JNIBoundary_nativeEvidence` (dex 2760 B with
  `System.loadLibrary("arena")`, `nativeEvidence`, and a description string "Java int length narrows to an unsigned
  native 16-bit boundary before authorization"). Rule: never key on export names or lib size; take the asset value,
  cross-check `ANS-` literals in the `.so`; if none, follow the `Java_*` export to the pointer it returns.

## Recognition cues -> first move

| You see | First move |
|---|---|
| `*.apk` artifact, answer_format `ANS- + 16 uppercase hex` | `unzip -l x.apk`, then `unzip -p x.apk assets/huntress_puzzle.json` (held the answer all 15 days). triage.md pre-extracts it to `work/extracted/` and prints the JSON |
| puzzle JSON `{"codec":..,"data":..}` | decode per codec (table below). Check the result fullmatches `^ANS-[0-9A-F]{16}$` before you submit |
| Codec name not in the table (d7 `caesar`, d15 `native`) | first check whether `data` already matches `ANS-` (d15). Else compare `data[:4]` with `ANS-`: constant ord diff = shift, constant XOR = xor key |
| `lib/<abi>/*.so` in the APK (d15-d16 `lib/x86_64/libarena.so`, 13.6-14.1 KB, not stripped) | `strings -a lib/*/*.so \| grep ANS-` and `nm -D --defined-only` first (d15: exports `huntress_arena_secret`/`huntress_arena_day`, 0x20-byte `.text`, answer as a literal in `.rodata`). Only if the answer is not a literal, route to binary-re (rizin / pyelftools + capstone, or the JNI `Java_*` export) |
| Native GATE (d16: `Java_*_nativeEvidence(int)` -> `*_length_accepts`; "type or length assumption") | the gate only decides whether the export returns `arena_value`; that pointer is the `.rodata` `ANS-` literal. If a question ever asks for the bypass input: `objdump -d --no-show-raw-insn f.so` the checker (d16: `len > 0xffff && (u16)len == 0` -> 65536) |
| "Recover split configuration from DEX and a native library" (d15) | the "split" was narrative: the asset `data` and the `.so` string were the SAME full answer, and the dex held only `CODEC`/`native`/`CONTROL`. Cross-check the two, submit |
| No puzzle JSON, or it decodes to no `ANS-` | `lib.android.extract_answer` (zip scan, then dex strings incl. multidex, then apktool/jadx scan), then `strings -a classes*.dex lib/*/*.so \| grep ANS-` |
| Need the theme, component, scheme or exported flags | `droidasc getmanifest x.apk` (fast). `aapt dump xmltree x.apk AndroidManifest.xml`. Also `lib.android.manifest_facts(apk)` |
| Need handler logic (URL built, extras read, constants) | `droidasc findrefs x.apk string <scheme or URL>`, then `droidasc getclass x.apk <pkg>.ChallengeActivity`; whole app: `jadx -d work/jadx x.apk` |
| Need resources or strings.xml / smali | `apktool d -f -o work/apktool x.apk` |
| Loopback `127.0.0.1:19090` in the code | do NOT chase it. It is device-local (refused on Homebase, times out elsewhere). The answer is static |
| Prompt demands a live action ("replay the session against the backend" d8, "exploit a challenge CA" d9) | still static: check `unzip -l` for pcap/HAR/cert/network config first; none shipped. Decode the asset, submit |
| Backup theme with a real `.ab` file (not seen yet) | Android backup = 24-byte header + zlib stream: `dd bs=24 skip=1 \| zlib-flate -uncompress \| tar x` (or abe.jar) |
| Mastery artifact names like `delivery N: foo_mastery_0N.apk` | strip the `delivery N: ` prefix (`lib.common.find_artifact` does this). Ids are `setN.answer`; each set may be a different day's fixture (d15) |

Puzzle codecs seen (`schema: huntress.mobile.puzzle.v1`):
- `plain`: data is the answer. `native` (d15): same -- data is the answer, duplicated in `lib/x86_64/libarena.so`.
- `reverse`: reverse the string (`...-SNA` -> `ANS-...`).
- `base64` (d3, d9, d13): `base64 -d` (`QU5TLTNEM0I4MDM5NTI0MEI4RUU=` -> `ANS-3D3B80395240B8EE`).
- `hex` (d6, d12): `xxd -r -p`.
- `caesar` (d7, d14): `{data, key:int}`. Plain ASCII codepoint shift: `chr(ord(c) - key)` for EVERY char (digits and `-`
  shift too, e.g. `KX]7` key 10 -> `ANS-`). A letters-only mod-26 ROT is wrong. Derive the sign from `data[:4]` vs `ANS-`.
- `xor` (d4, d11): data is base64. b64-decode, then XOR every byte with the int `key` (0-255, changes per variant).
- `split` (d5, d10): `parts[]` + `order[]`, where `order[i]` is the OUTPUT SLOT of `parts[i]` (not `parts[order[i]]`).
  Try both readings and keep the one that fullmatches `ANS-`.
- `lib.android.decode_payload` covers every codec above, `puzzle_candidates(apk)` also does split (both order readings),
  and `decode_any` is the name-agnostic fallback (base32, rot13, `lib.decode.peel`). Call them instead of re-typing a
  table. Unknown codec + int key: `key_or_shift = f(data[:4], "ANS-")` (xor: byte ^; shift: ord diff).

## Day by day

**Days 1-6** (same 6-entry fixture, one codec per day, all first try): d1 Exported Trust `plain` (CORRECT ~5.4 min,
~4 min lost probing `127.0.0.1:19090` via `hctf hb exec curl`); d2 Deep Link Drift `reverse` (33 s; Mastery expired 8x
in a 6 s window until Homebase prewarm); d3 Intent Injection `base64` (18 s); d4 Pending Intent Relay `xor` key per
variant 103/189/31/81 (77 s); d5 Backup Spill `split` -- `order[i]` = output slot of `parts[i]` (27 s; TT/Mastery 7 s
window, solve 0.08 s of 5.3 s); d6 Provider Paths `hex` (exported provider with a null `query()` stub; ~3 min, 2.3 min
lost on the loopback).

**Days 7-13** (same fixture; theme stubs never needed): d7 WebView Bridge, new `caesar` key 10, spotted by eye
(`K`-10=`A`), 52 s; d8 Cleartext Session `reverse`, no traffic shipped, 22 s; d9 Trust Everyone `base64`, no TLS code,
~25 s; d10 Network Config Split `split` (first 8-entry fixture with `network_security_config.xml`, still static); d11
Local Secrets `xor` key 81, dex `client_secret` a decoy, ~28 s; d12 SQLite Assumptions `hex`, no `.db` shipped, ~4.5 s
by the carried-over solver; d13 Keystore Misuse `base64`, no `KeyStore`/`Cipher` in the dex, ~4 s. All 0 wrong;
TT/Mastery 0.8-3.5 s in-window.

**Days 14-15** (carried-over solver via the race probe, ~3 s each, 0 wrong): d14 Predictable Crypto `caesar` key 9
(`JW\6L><BL=A;OL>NN:=?`; raw JSON escapes `\\` and `<` -- json-load it), no `Random`/`Cipher` in the dex. d15 Native
Library Secrets (`jni_secret`, "split configuration from DEX and a native library"): first `lib/x86_64/libarena.so`
(13648 B, exports `huntress_arena_secret`/`_day`, `.text` 0x20 B, answer literal in `.rodata`); codec `native` = the
plaintext answer, identical to the `.so` string -- the "split" was narrative. First MIXED-DAY Mastery (d01/07/10/14/15).

**Day 16 — JNI Boundary** (manifest `huntress.mechanic`=`jni-boundary`, dex `DAY-16:jni_length:Java-to-native validation
mismatch`; prompt "Identify a Java-to-native type or length assumption that changes backend authorization.")
- Artifact: the d15 7-entry fixture (APK 12772 B), stub class `JNIBoundary`, codec `native`, `data` = plaintext answer,
  same literal in `libarena.so` `.rodata`. Single variant's `.so` was byte-for-byte the d15 shape (no gate code).
- TT/Mastery builds carried the real mechanic: `nativeEvidence(env, cls, int len)` calls
  `huntress_arena_length_accepts(len, 0)` (`cmpl $0xffff` then a 16-bit `cmp %ax`), returning `arena_value` only for
  a Java int > 65535 whose low 16 bits are 0. Reading it took ~1 min with `nm -D --defined-only` + `objdump -d`; it was
  not needed for the answer.
- Commands: `cat work/extracted/*/assets/huntress_puzzle.json` (triage.md prints it); cross-check `strings -a
  lib/x86_64/libarena.so | grep ANS-`.
- Solved by the generic carried-over solver (`puzzle_candidates` + `ANS-` regex, fallback `raw_entry_scan`/`dex_strings`)
  via the harness race probe: start 13:00:15Z -> CORRECT 13:00:22Z (~7 s). TT in_window 5.3 s (solve 0.85 s), Mastery 5
  sets mixed days (d01 plain, d04 xor 21, d11 xor 232, d13 base64, d16 native) in_window 5.5 s (solve 0.21 s). 0 wrong.

## GM answer conventions learned
- One field, `answer`. Single solve and TT use id `answer`; Mastery uses `setN.answer` (3 or 5 sets), one APK per set.
- Format is `ANS-` + exactly 16 UPPERCASE hex, normalization `exact`. Uppercase the hex after decoding, no whitespace.
- No mobile answer has ever been rejected (zero wrong submissions on days 1-16). The GM accepts the decoded
  `huntress_puzzle.json` value as the "backend evidence code" even though the prompt says "Submit only the exact backend
  answer code returned for this case".
- Mastery feedback is per set: `{"result":"accepted","remaining":N}` after each set, then `CORRECT` on the last. An
  empty submit after the deadline returns `expired`.
- Prompt boilerplate repeats daily: "For case MOB-NN-<10 hex> in package com.huntress.mobile.dNN.v<12 hex>". In a mixed
  Mastery bundle the prompt text is today's; on d15 each set's `NN` named its source day, but on d16 the question's case
  ref/package did not match the APK's own (MOB-06 question -> a d04 APK). Neither was ever needed for the answer.

## Pitfalls that cost time
- **Chasing the loopback backend** was the only recurring time sink: about 4 min (d1), about 30 s (d4) and about 2.3 min
  (d6). `127.0.0.1:19090` is the phone's own loopback. If the decoded asset already matches the answer_format, submit it.
- **Assuming "today's codec" in Mastery** (d15): sets can come from older days with different codecs and extra entries.
  A solver that branched on the day's codec name would have failed 4/5 sets. Decode each APK on its own.
- **Reaching for Ghidra on a native-lib theme** (d15-d16): the `.so` is ~14 KB, unstripped, the answer a literal. Use
  `strings`/`nm` first, then `objdump -d` of the one `Java_*` export (d16 gate = 0x30 bytes). Ghidra is overkill.
- **Trusting the question's case ref in Mastery** (d16): it can name a different day/case than the APK it points at.
- **split codec order semantics:** two plausible readings exist. Validate the candidates against the answer regex
  instead of guessing.
- **xor codec:** `data` is base64 first, and `key` may vary per variant (int; the solvers also accept a numeric string
  or a repeating string key).
- **caesar codec:** the shift is over raw codepoints, not the alphabet (`data` contains `]`, `` ` ``, `<`, `>` --
  JSON-escaped as `<`/`>`, so json-load it, never regex the raw text). Keep only the candidate that
  fullmatches `^ANS-[0-9A-F]{16}$`.
- **Mastery filenames** carry a literal `delivery N: ` prefix. A naive path lookup fails.
- **6-11 s timed windows** (d2-d9) are dominated by start + download + submit. Solve time is about 0.1 s, so do no
  decompiling in-window: read the zip entry directly (the solver runs stdlib + lib.* only, no jadx subprocess).
- **Prompt wording escalates, the artifact did not** (d8 "replay the session", d9 "exploit a challenge CA", d12 "prove
  server-side impact", d13 "app-controlled wrapping key", d14 "seeded nonces", d15 "split configuration from DEX and a
  native library", d16 "type or length assumption that changes backend authorization"): judge by what the APK contains (pcap/HAR, token file, `.db`, cert, network config, native lib,
  `Random`/`Cipher`/KDF refs in `strings -a classes.dex`), not by the verb.
- **Hand-typed codec tables:** use `lib.android.puzzle_candidates`/`decode_payload` so a missed branch can't cost a
  timed run.
- **Harness, not GM:** a re-start can clobber `single_solve/start.json` (no attempt_id), which makes a solved lane look
  incomplete. Check `hctf status` before re-solving.
- Watch for the cheap escalation (not yet seen): answer only in the dex, `strings.xml`, BuildConfig or the `.so`
  (possibly XORed/split across `huntress_arena_secret` + a dex constant), or computed by a decrypt routine. Then trace
  `ChallengeActivity`, run `lib.android.extract_answer`, and disassemble the exported native function. The d16 TT build
  already returns the answer only through a gated `Java_*` export: the next step is the literal leaving the asset, or
  the export computing it (xor/stack string) instead of returning a `.rodata` pointer.
