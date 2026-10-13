# mobile-android — technique log (days 1-13; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Every APK so far was the same ~12.7 KB fixture with 6 zip entries (d10 added `res/xml/network_security_config.xml` +
  `resources.arsc` = 8 entries, 12845 B; d11 back to 6): `AndroidManifest.xml`, `assets/huntress_puzzle.json`,
  `classes.dex`, `META-INF/FIXTURE-.{SF,RSA}`, `MANIFEST.MF`. One question, `answer` = `ANS-` + 16 uppercase hex.
- Each day has a new Android IPC/security THEME, written in the manifest `<meta-data android:name="huntress.mechanic">`
  (exported Activity, permissive deep link, nested Intent, mutable PendingIntent, allowBackup, exported ContentProvider,
  JavaScript-interface origin trust, cleartext session transport, permissive X509 trust manager, Network Security Config
  exception, locally stored credential in SharedPreferences, client-side SQLite authorization state, app-controlled
  Keystore wrapping key). The theme was
  flavour only: no day required exploiting it, even when the dex carried a matching stub class (d7 `WebViewBridge`,
  d8 `CleartextSession`, d9 `TrustEveryone`) or the prompt demanded a live action ("replay it against the backend"
  d8, "exploit a challenge CA" d9 -- no CA/cert/network_security_config/TrustManager code was shipped).
- What actually varied day to day was the `codec` of `huntress_puzzle.json` (plain, reverse, base64, xor+key, split,
  hex, caesar+key, reverse again on d8, base64 again on d9, split again on d10, xor+key again on d11, hex again on d12, base64 again on d13 -- codecs CAN repeat). Within one day every variant (single, TT, all Mastery
  sets) used the same codec. Keys re-roll per variant. A new codec name is possible any day: decode it from the first
  4 chars, which must become `ANS-`. The dex also holds the codec name as a `CODEC` string constant (d8, d9) and a
  `DAY-NN:<theme_id>:<mechanic>` string.
- In every APK, `.ChallengeActivity` builds a device-loopback URL `http://127.0.0.1:19090/mobile/attempt/<id>/evidence?
  case_id=..&client_secret=SECRET-..&proof=<answer>`. That backend is NOT reachable (it lives on the phone). The GM
  accepted the decoded puzzle value as the "backend evidence code" on all 13 days.
- Expect escalation (inference, see reference/HARDENING.md): the answer may move into the dex, resources or a decrypt
  routine. `lib.android.extract_answer` has the fallback chain for that case.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Puzzle codec** -- the same within one day, but `key` (xor byte d4, d11: 81 single/109 TT/205,29,44 Mastery; caesar shift d7: 10/18/9/3/4) and any
  split/offset parameters re-roll per variant: read them from `huntress_puzzle.json` every time. Keyless codecs
  (d8 `reverse`, d9/d13 `base64`) differed only in `data`. Rule: decode by declared codec, regex-check, else `decode_any`.
- **Per-variant identity** -- case ref, package suffix `v<12 hex>`, `client_secret` and the loopback attempt slug
  change per variant (all Mastery sets shared one slug on d7-d9, e.g. `d09-92be5cd6e8a5594f`; single and TT each
  had their own). APK size stays 12704 B, 6 entries. None of these feed the answer.
- **Mastery packaging** -- `delivery N: <name>.apk` per set, often identically named: pair by sha256. Set count
  varies: 3 sets (d1-d7, d10-d13), 5 sets on d8 and d9 (`set1..set5.answer`). Loop over the contract's answer_ids, never assume 3.
- **Answer location** -- so far always the puzzle JSON; if it decodes to nothing, fall back to dex/resources
  (`lib.android.extract_answer` chain) rather than assuming the sample's location.

## Recognition cues -> first move

| You see | First move |
|---|---|
| `*.apk` artifact, answer_format `ANS- + 16 uppercase hex` | `unzip -l x.apk`, then `unzip -p x.apk assets/huntress_puzzle.json` (takes seconds; it held the answer all 12 days). triage.md pre-extracts it to `work/extracted/` |
| puzzle JSON `{"codec":..,"data":..}` | decode per codec (table below). Check the result fullmatches `^ANS-[0-9A-F]{16}$` before you submit |
| Codec name not in the table below (d7 `caesar`) | compare `data[:4]` with `ANS-`: constant ord diff = shift, constant XOR = xor key. Implement, regex-check, submit |
| No puzzle JSON, or it decodes to no `ANS-` | `python -c 'from lib.android import extract_answer'` (zip scan, then dex strings incl. multidex, then apktool/jadx scan), then `strings -a classes*.dex \| grep ANS-` |
| Need the theme, component, scheme or exported flags | `droidasc getmanifest x.apk` (fast). `aapt dump badging x.apk` / `aapt dump xmltree x.apk AndroidManifest.xml` (installed). Also `lib.android.manifest_facts(apk)` |
| Need handler logic (URL built, extras read, constants) | `droidasc findrefs x.apk string <scheme or URL>`, then `droidasc getclass x.apk <pkg>.ChallengeActivity`; whole app: `jadx -d work/jadx x.apk` |
| Need resources or strings.xml / smali | `apktool d -f -o work/apktool x.apk` |
| Loopback `127.0.0.1:19090` in the code | do NOT chase it. It is device-local (refused on Homebase, times out elsewhere). The answer is static |
| Prompt says "recover the session from cleartext traffic and replay it against the backend" (d8) | still static: no pcap/HAR/network_security_config in the APK; the "traffic" is the `http://` loopback URL and `usesCleartextTraffic=true`. Decode the asset, submit |
| Prompt says "exploit a challenge CA accepted by a permissive trust implementation" (d9) | still static: no `.pem`/`.crt`/`res/raw`, no `network_security_config`, dex has no `X509TrustManager`/`SSLContext` refs, only a stub `TrustEveryone` class. Decode the asset, submit. A real TLS task would ship a cert or MITM target -- check `unzip -l` first |
| Native `lib/*.so` inside the APK (not seen yet) | route to the binary-re skill (rizin / Ghidra headless) |
| Backup theme with a real `.ab` file (not seen yet) | Android backup = 24-byte header + zlib stream: `dd bs=24 skip=1 \| zlib-flate -uncompress \| tar x` (or abe.jar) |
| Mastery artifact names like `delivery N: foo_mastery_0N.apk` | strip the `delivery N: ` prefix to find the file (`lib.common.find_artifact` does this). Ids are `setN.answer` |

Puzzle codecs seen (`schema: huntress.mobile.puzzle.v1`):
- `plain`: data is the answer.
- `reverse`: reverse the string (`...-SNA` -> `ANS-...`).
- `base64` (d3, d9): `base64 -d` (`QU5TLTNEM0I4MDM5NTI0MEI4RUU=` -> `ANS-3D3B80395240B8EE`).
- `hex`: `xxd -r -p`.
- `caesar` (d7): `{data, key:int}`. Plain ASCII codepoint shift: `chr(ord(c) - key)` for EVERY char (digits and `-`
  shift too, e.g. `KX]7` key 10 -> `ANS-`). A letters-only mod-26 ROT is wrong. Derive the sign from `data[:4]` vs `ANS-`.
- `xor`: data is base64. b64-decode, then XOR every byte with the int `key` (0-255, changes per variant).
- `split`: `parts[]` + `order[]`, where `order[i]` is the OUTPUT SLOT of `parts[i]` (not `parts[order[i]]`). Try both
  readings and keep the one that fullmatches `ANS-`.
- The solvers also handle base32, rot13 and a `lib.decode.peel` fallback, ready for new codecs.
  `lib.android.decode_payload` now covers every codec above incl. caesar/reverse, `puzzle_candidates(apk)` also does
  split (both order readings), and `decode_any` is the name-agnostic fallback. Call them instead of re-typing a table.
- Unknown codec + int key: try the known-plaintext trick. `key_or_shift = f(data[:4], "ANS-")` (xor: byte ^; shift:
  ord diff). A constant diff across the 4 chars names the transform at once.

## Day by day

**Day 1 — Exported Trust** ("exported Activity and caller trust"): exported `.ChallengeActivity`, deep link
`huntress01://exported-trust/unlock`; `onCreate` reads `answer`/`case_id` extras and builds the loopback evidence URL.
Codec `plain`. Tools: `droidasc getmanifest`, apktool, jadx, reading the asset from the zip. About 4 min lost trying to
reach `127.0.0.1:19090` via `hctf hb exec curl` (Homebase `ss -tln`, GM proxy, 10.0.0.219:19090 -- all refused/timed
out). CORRECT at about 5.4 min, first try. TT/Mastery windows were 30s on d1 (6-11s from d2 on).

**Day 2 — Deep Link Drift** ("permissive scheme, host, and path validation"): same shape, no host/path checks. Codec
`reverse`. CORRECT at 33s. A harness re-start overwrote `single_solve/start.json` without `attempt_id` (restore from
`log.jsonl`). Mastery expired 8 times: 6s window with 3 downloads + submit inside it (fixed by Homebase prewarm).

**Day 3 — Intent Injection** ("attacker-controlled nested Intent"): same shape. Codec `base64`. CORRECT at 18s.

**Day 4 — Pending Intent Relay** ("mutable PendingIntent relay"): same shape. Codec `xor` `{data:<b64>, key:<int>}`;
key re-rolled per variant (103, 189, 31, 81). About 30s lost on the loopback. CORRECT at 77s.

**Day 5 — Backup Spill** (`allowBackup="true"`, no backup file shipped): codec `split` (`parts` + `order`); the
`parts[order[i]]` reading was a dead end, `order[i]` = output slot of `parts[i]` was right. CORRECT at 27s. TT/Mastery
7s window (elapsed 5.3s: start 1.8, download 2.3, solve 0.08, submit 1.2).

**Day 6 — Provider Paths** (exported `<provider ... authorities=<pkg>.evidence grantUriPermissions=true>`, `query()`
a stub returning null): codec `hex`. About 2.3 min lost on the loopback and grepping hctf/ for a backend route.
CORRECT at about 3 min.

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

**Day 8 — Cleartext Session** (mechanic "cleartext session transport"; prompt "Recover a synthetic session from allowed
cleartext traffic and replay it against the backend ... Submit only the exact backend answer code")
- Same fixture (12704 B, 6 entries). Manifest: `usesCleartextTraffic=true`, `allowBackup=false`, INTERNET permission,
  deep link `huntress08://cleartext-session` pathPrefix `/unlock` on exported `.ChallengeActivity`. Dex: stub class
  `CleartextSession` (`describe`/`encode`/`getData`), `CODEC`="reverse", the usual `http://127.0.0.1:19090/mobile/
  attempt/d08-<16 hex>/evidence?case_id=..&client_secret=SECRET-..&proof=` URL. No captured traffic, no session token
  file, no network config: the "cleartext session" is that URL. Nothing was replayed.
- Codec `reverse` (repeat of d2): `"6667D24E8BC6DE39-SNA"` -> `ANS-93ED6CB8E42D7666`.
- Worker flow: read triage.md (pre-extracted puzzle JSON), pasted the d7 codec table into solve.py,
  `hctf submit --from-solver`. 2 tool calls, no decompile, no loopback chase.
- Start 15:43:54Z -> CORRECT 15:44:16Z = 22s, first try. TT (8s window) correct in 1.5s.
  Mastery (8s window, 5 sets) correct in 2.27s. Zero wrong submissions.

**Day 9 — Trust Everyone** (mechanic "permissive X509 trust manager"; prompt "Exploit a challenge CA ..."): same 6-entry
fixture, stub `TrustEveryone`, no TLS code -- the "CA"/"backend" were narrative. Codec `base64` (repeat of d3) ->
`ANS-3D3B80395240B8EE`. 2 tool calls, ~25 s, first try; TT 3.16 s (cold imports), Mastery 5 sets 1.7 s.

**Day 10 — Network Config Split** (mechanic "Network Security Config exception"): first fixture with extra entries --
`res/xml/network_security_config.xml` (cleartextTrafficPermitted=true for domain 127.0.0.1) + `resources.arsc`. Still
static: codec `split` (repeat of d5), `parts ["56C4B5B0D","ANS-4","9D8953"]`, `order [2,0,1]` = output slot of each part.
All 3 modes CORRECT first try (TT 13 s / Mastery 10 s windows, 3 sets).

**Day 11 — Local Secrets** (mechanic `DAY-11:shared_preferences:locally stored synthetic credential`; prompt "Separate
active credentials from decoys across generated local stores.")
- Same 6-entry fixture (12704 B). No SharedPreferences XML, sqlite or other "local store" file shipped; the only
  credential-looking string besides the asset is the dex's loopback `client_secret=SECRET-<22 hex>` (a decoy, never
  the answer). Codec `xor` (repeat of d4): `{"data":"EB8CfGkXY2NkZmVmYBUXZWkVYGU=","key":81}` -> b64-decode, XOR 81 ->
  `ANS-8F2257471DF48D14`.
- Worker (warm launch): one command decoded the triage-extracted JSON by hand (`base64 -d | xor 81`), a second filled
  `answer()` with `lib.android.puzzle_candidates` + `ANS-` regex (fallback `raw_entry_scan`/`dex_strings`) and
  submitted. Launch 01:55:40Z -> CORRECT 01:56:08Z = ~28 s, first try. TT (7 s window) 0.93 s in-window; Mastery (8 s, 3
  sets) 0.82 s. Zero wrong submissions.

**Day 12 — SQLite Assumptions** (mechanic `DAY-12:sqlite_cache:client-side SQLite authorization state`; prompt
"Reconstruct authorization from a synthetic SQLite cache and prove server-side impact.")
- Same 6-entry fixture (12704 B), deep link `huntress12://sqlite-assumptions`, stub class `SQLiteAssumptions`. NO `.db`/sqlite
  file, no `SQLiteOpenHelper` code: the "cache" was narrative again. Codec `hex` (repeat of d6):
  `414e532d30333946304439303731313131303530` -> `ANS-039F0D9071111050`.
- Solved by the carried-over solver (`lib.android.puzzle_candidates` + `ANS-` regex) with no worker tool call: start
  23:10:48Z -> CORRECT 23:10:52.8Z (~4.5 s). TT 30 s window, in_window 1.49 s; Mastery 3 sets, in_window 0.95 s. 0 wrong.

**Day 13 — Keystore Misuse** (mechanic `DAY-13:keystore_wrapper:app-controlled wrapping key`; prompt "Recover data
protected by an app-controlled wrapping key despite nominal Keystore use.")
- Same 6-entry fixture. The dex has NO `KeyStore`/`Cipher`/AES strings -- no wrapping key, no ciphertext; "keystore" was
  narrative. Codec `base64` (repeat of d3/d9): `QU5TLTc3Mzc2MkU4NTc5NzA2NEM=` -> `ANS-773762E85797064C`.
- Solved by the carried-over solver (`puzzle_candidates` + `ANS-` regex) via the harness probe, no worker tool call:
  start -> CORRECT ~4 s. TT (50 s window) 1.86 s elapsed; Mastery 3 sets (110 s) 1.63 s. 0 wrong.

## GM answer conventions learned
- One field, `answer`. Single solve and TT use id `answer`; Mastery uses `setN.answer` (3 sets d1-d7, 5 on d8-d9), one
  APK per set.
- Format is `ANS-` + exactly 16 UPPERCASE hex, normalization `exact`. Uppercase the hex after decoding and add no
  whitespace.
- No mobile answer has ever been rejected (zero wrong submissions on days 1-13). `ANS-<16 uppercase hex>` confirmed
  again on d8 and d9 (7/7 variants each). The GM accepts the decoded
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
- **6-11s timed windows** (day 2+; d7 TT 9s/Mastery 10s, d8 both 8s, d9 TT 8s/Mastery 11s) are dominated by start + download + submit. Solve time is about 0.1s, so do no
  decompiling in-window: read the zip entry directly. Day 2 Mastery expired 8 times before Homebase routing.
- **Don't decompile when you don't need to.** Every solve so far (d1-d13) needed only the asset; the manifest was context only.
  Keep jadx/apktool for the day the asset is missing or lacks `ANS-`.
- **Prompt wording escalates, the artifact did not** (d7 "cross a bridge", d8 "replay the session against the backend",
  d9 "exploit a challenge CA", d11 "separate active credentials from decoys", d12 "reconstruct authorization from a SQLite cache and prove server-side impact", d13 "recover data protected by an
  app-controlled wrapping key" with no crypto in the dex): judge by what the APK contains (pcap/HAR, token file, `.db`/sqlite, cert, network_security_config,
  native lib), not by the verb.
- **Hand-typed codec tables:** each day's solver re-pasted the decode table; it worked, but `lib.android` already
  covers it -- use `puzzle_candidates`/`decode_payload` so a missed branch can't cost a timed run.
- **Harness, not GM:** a re-start can clobber `single_solve/start.json` (no attempt_id), which makes a solved lane look
  incomplete. Check `hctf status` before re-solving.
- Watch for the cheap escalation (hypothesis in reference/HARDENING.md, not yet seen): answer moved into the dex,
  `strings.xml`, BuildConfig or a native lib, or computed by a decrypt routine. Then trace `ChallengeActivity` and run
  `lib.android.extract_answer`.
