# mobile-android — technique log (days 1-15; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Every APK so far was the same ~12.7 KB fixture: `AndroidManifest.xml`, `assets/huntress_puzzle.json`, `classes.dex`,
  `META-INF/FIXTURE-.{SF,RSA}`, `MANIFEST.MF` (6 entries). Extras: d10 `res/xml/network_security_config.xml` +
  `resources.arsc` (8 entries); d15 `lib/x86_64/libarena.so` (7 entries, 12772 B). One question, `answer` = `ANS-` + 16
  uppercase hex.
- Each day has a new Android IPC/security THEME, written in the manifest `<meta-data android:name="huntress.mechanic">`
  and in a dex string `DAY-NN:<theme_id>:<mechanic>` (exported Activity, permissive deep link, nested Intent, mutable
  PendingIntent, allowBackup, exported ContentProvider, JS-interface origin trust, cleartext session, permissive X509
  trust manager, NSC exception, SharedPreferences credential, client-side SQLite authz, app-controlled Keystore key,
  predictable nonce d14, `jni_secret` "challenge-owned JNI shared library" d15). The theme was flavour only: no day
  required exploiting it, even with a matching stub class (`WebViewBridge`, `CleartextSession`, `TrustEveryone`,
  `PredictableCrypto`, `NativeLibrarySecrets`) or a prompt demanding a live action.
- What varied day to day was the `codec` of `huntress_puzzle.json` (plain, reverse, base64, xor+key, split, hex,
  caesar+key, then repeats; d15 a NEW name `native` whose `data` is already the plaintext answer). The dex also holds
  the codec name next to a `CODEC` string constant. Keys re-roll per variant. A new codec name is possible any day:
  decode it from the first 4 chars, which must become `ANS-`.
- **d15: Mastery became a MIXED-DAY bundle.** The 5 sets were APKs from earlier days (d01 plain, d07 caesar, d10 split,
  d14 caesar, d15 native in one attempt; MOB-03/07/09/13/15 in another contract), all under today's prompt text. Up to
  d14 every set used the day's codec. Solve each set from its own puzzle JSON, never from "today's codec".
- In every APK, `.ChallengeActivity` builds a device-loopback URL `http://127.0.0.1:19090/mobile/attempt/<id>/evidence?
  case_id=..&client_secret=SECRET-..&proof=<answer>`. That backend is NOT reachable (it lives on the phone). The GM
  accepted the decoded puzzle value as the "backend evidence code" on all 15 days.
- Escalation watch: d15 shipped the first native lib, but the answer was STILL in the asset as well (and as a plain
  `.rodata` string in the `.so`). If a later day drops it from the asset, the `.so`/dex are the next places
  (`lib.android.extract_answer` has the zip/dex/apktool fallback chain).

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Puzzle codec** -- single + TT always shared the day's codec. `key` (xor byte d4, d11: 81/109/205,29,44; caesar shift
  d7: 10/18/9/3/4, d14: 9/10/17,4,7, d15 Mastery d07-set 15, d14-set 4) and split/offset parameters re-roll per variant:
  read them from `huntress_puzzle.json` every time. Keyless codecs (`reverse`, `base64`, `native`) differ only in `data`.
  Rule: decode by declared codec, regex-check `^ANS-[0-9A-F]{16}$`, else `decode_any`; unknown name -> known-plaintext
  `ANS-` trick.
- **Mastery set mix (NEW d15)** -- sets can be fixtures of DIFFERENT days (codec, theme, package `dNN`, extra entries
  like `res/xml/...` or `lib/x86_64/*.so` all differ per set; the puzzle JSON `day` field and dex `DAY-NN:` tag name the
  source day). The day picks re-roll per attempt (01/07/10/14/15 vs 03/07/09/13/15); the last set was today's.
  Rule: per-set, codec-agnostic decoding (`puzzle_candidates` over each APK) -- never branch on the challenge's day.
- **Per-variant identity** -- case ref `MOB-NN-<10 hex>`, package suffix `v<12 hex>`, `client_secret` and the loopback
  attempt slug change per variant. None of these feed the answer.
- **Mastery packaging** -- `delivery N: <name>_mastery_0N.apk` per set: pair by sha256. Set count varies: 3 sets
  (d1-d7, d10-d14), 5 sets (d8, d9, d15). Loop over the contract's answer_ids, never assume 3.
- **Answer location** -- so far always the puzzle JSON (d15: also duplicated in the `.so`); if it decodes to nothing,
  fall back to dex/resources/native (`raw_entry_scan`, `dex_strings`, `strings -a lib/*/*.so | grep ANS-`).

## Recognition cues -> first move

| You see | First move |
|---|---|
| `*.apk` artifact, answer_format `ANS- + 16 uppercase hex` | `unzip -l x.apk`, then `unzip -p x.apk assets/huntress_puzzle.json` (held the answer all 15 days). triage.md pre-extracts it to `work/extracted/` and prints the JSON |
| puzzle JSON `{"codec":..,"data":..}` | decode per codec (table below). Check the result fullmatches `^ANS-[0-9A-F]{16}$` before you submit |
| Codec name not in the table (d7 `caesar`, d15 `native`) | first check whether `data` already matches `ANS-` (d15). Else compare `data[:4]` with `ANS-`: constant ord diff = shift, constant XOR = xor key |
| `lib/<abi>/*.so` in the APK (d15 `lib/x86_64/libarena.so`, 13.6 KB, not stripped) | `strings -a lib/*/*.so \| grep ANS-` and `nm -D --defined-only` first (d15: exports `huntress_arena_secret`/`huntress_arena_day`, 0x20-byte `.text`, answer as a literal in `.rodata`). Only if the answer is not a literal, route to binary-re (rizin / pyelftools + capstone, or the JNI `Java_*` export) |
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

**Day 14 — Predictable Crypto** (`DAY-14:predictable_rng:predictable nonce and derivation`; prompt "Exploit seeded
nonces or weak derivation without bypassing earlier storage gates."): same 6-entry fixture, stub `PredictableCrypto`,
no `Random`/seed/`Cipher`/KDF strings in the dex. Codec `caesar` key 9: `JW\6L><BL=A;OL>NN:=?` ->
`ANS-C539C482FC5EE146` (raw JSON has `\\` and `<` -- json-load it). Carried-over solver via the race probe: ~3 s.
TT key 10, Mastery keys 17/4/7, ~1.3 s in-window each. 0 wrong.

**Day 15 — Native Library Secrets** (`DAY-15:jni_secret:challenge-owned JNI shared library`; prompt "Recover split
configuration from DEX and a challenge-owned native library.")
- Artifact: the usual fixture plus `lib/x86_64/libarena.so` (13648 B ELF x86-64 shared object, not stripped, 7 zip
  entries, APK 12772 B). The `.so` exports `huntress_arena_secret` (0x1000) and `huntress_arena_day` (0x1011); `.text` is
  0x20 bytes, `.rodata` 0x15 bytes = the answer literal. Dex: stub class `NativeLibrarySecrets`, strings `CODEC`,
  `native`, `CONTROL`, `encode`, `describe`; no `System.loadLibrary` logic was needed.
- Key insight: the "split" between DEX and native was narrative. Puzzle JSON `{"codec":"native","data":"ANS-..."}` held
  the full plaintext answer, identical to the `.so` `.rodata` string (checked on single and TT).
- Commands: `cat work/extracted/*/assets/huntress_puzzle.json`; cross-check `strings -a lib/x86_64/libarena.so | grep
  ANS-`; `nm -D --defined-only libarena.so`.
- Solved by the carried-over solver (`puzzle_candidates` + `ANS-` regex) via the harness race probe, no worker tool
  call: start 13:00:15.3Z -> CORRECT 13:00:18.5Z (~3 s). TT in_window 1.84 s. Mastery 5 sets, MIXED days (d01 plain,
  d07 caesar key 15, d10 split, d14 caesar key 4, d15 native), in_window 2.55 s -- passed only because the solver is
  codec-agnostic per set. 0 wrong, all first try.

## GM answer conventions learned
- One field, `answer`. Single solve and TT use id `answer`; Mastery uses `setN.answer` (3 or 5 sets), one APK per set.
- Format is `ANS-` + exactly 16 UPPERCASE hex, normalization `exact`. Uppercase the hex after decoding, no whitespace.
- No mobile answer has ever been rejected (zero wrong submissions on days 1-15). The GM accepts the decoded
  `huntress_puzzle.json` value as the "backend evidence code" even though the prompt says "Submit only the exact backend
  answer code returned for this case".
- Mastery feedback is per set: `{"result":"accepted","remaining":N}` after each set, then `CORRECT` on the last. An
  empty submit after the deadline returns `expired`.
- Prompt boilerplate repeats daily: "For case MOB-NN-<10 hex> in package com.huntress.mobile.dNN.v<12 hex>". In a mixed
  Mastery bundle (d15) the `NN` in each set's case ref/package names that set's SOURCE day, while the prompt text is
  today's. Neither the case ref nor the package suffix was ever needed for the answer.

## Pitfalls that cost time
- **Chasing the loopback backend** was the only recurring time sink: about 4 min (d1), about 30 s (d4) and about 2.3 min
  (d6). `127.0.0.1:19090` is the phone's own loopback. If the decoded asset already matches the answer_format, submit it.
- **Assuming "today's codec" in Mastery** (d15): sets can come from older days with different codecs and extra entries.
  A solver that branched on the day's codec name would have failed 4/5 sets. Decode each APK on its own.
- **Reaching for Ghidra on a native-lib theme** (d15): the `.so` was tiny and the answer was a literal. Use `strings`/`nm`
  first; disassemble only if no `ANS-` literal exists.
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
  native library"): judge by what the APK contains (pcap/HAR, token file, `.db`, cert, network config, native lib,
  `Random`/`Cipher`/KDF refs in `strings -a classes.dex`), not by the verb.
- **Hand-typed codec tables:** use `lib.android.puzzle_candidates`/`decode_payload` so a missed branch can't cost a
  timed run.
- **Harness, not GM:** a re-start can clobber `single_solve/start.json` (no attempt_id), which makes a solved lane look
  incomplete. Check `hctf status` before re-solving.
- Watch for the cheap escalation (not yet seen): answer only in the dex, `strings.xml`, BuildConfig or the `.so`
  (possibly XORed/split across `huntress_arena_secret` + a dex constant), or computed by a decrypt routine. Then trace
  `ChallengeActivity`, run `lib.android.extract_answer`, and disassemble the exported native function.
