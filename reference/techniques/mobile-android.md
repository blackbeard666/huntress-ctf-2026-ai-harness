# mobile-android — technique log (days 1-26; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Every APK so far was the same ~12.7 KB fixture: `AndroidManifest.xml`, `assets/huntress_puzzle.json`, `classes.dex`,
  `META-INF/FIXTURE-.{SF,RSA}`, `MANIFEST.MF` (6 entries). Extras: d10 `res/xml/network_security_config.xml` +
  `resources.arsc` (8 entries); d15-d16 `lib/x86_64/libarena.so` (7 entries); d20 `assets/payload.dex` (508 B plain dex).
  d21 the only manifest with `android:debuggable="true"`. One question, `answer` = `ANS-` + 16 uppercase hex.
  **d26 first non-APK container**: `*.apks` = stored zip of `base.apk` (the usual fixture) + `feature.apk` (8.5 KB,
  manifest `split="arena_feature"`, `hasCode=false`, one asset) in ALL three modes (Mastery: today's set only).
- Each day has a new Android IPC/security THEME, written in the manifest `<meta-data android:name="huntress.mechanic">`
  and in dex constants (`DAY-NN:<theme_id>:<mechanic>` tag or `CONTROL`/`STRUCTURAL` fields): exported Activity, deep
  link, nested Intent, PendingIntent, allowBackup, ContentProvider, JS bridge, cleartext, trust manager, NSC, prefs,
  SQLite, Keystore, nonce d14, `jni_secret` d15, `jni_length` d16, `identifier_obfuscation` d17, `string_decryption` d18,
  `reflective_dispatch` d19, `dynamic_dex` d20, `anti_debug` d21, `root_detection` d22, `hook_detection` d23,
  `emulator_detection` d24, `integrity_signal` d25, `split_apk` "base and feature split correlation" d26. Through d22 the theme was flavour only (stub classes never needed). **Since d23 TT/Mastery
  COMPUTE the answer in dex code**; the theme is one pure-arithmetic gate fn inside that chain. **d26 = first chain that
  READS ARTIFACT BYTES at runtime** (16 B from the feature split via `splitSourceDirs` + `ZipFile`).
- Puzzle JSON v1 (`schema: huntress.mobile.puzzle.v1`, d1-d24 single, d1-d22 TT/Mastery): the answer sits behind a
  rotating `codec` (plain, reverse, base64, xor+key, split, hex, caesar+key, native, indexed, reflection, dynamic =
  pointer to `assets/payload.dex`; old codecs recur: d21 reverse, d22 base64, d23 xor, d24 split, d25 hex, d26 split
  with a fragment in the feature split). Keys re-roll.
- **Puzzle JSON v2 (d23-d26 TT and every Mastery set):** `{"schema":"huntress.mobile.puzzle.v2","day":N,"codec":
  "analysis","build":"<12 hex>"}` -- NO `data`. The answer is `Release.code(Context)` evaluated statically (see Day 23).
  Older days' Mastery sets were REGENERATED in v2 (d02/d06/d10/d14/d15/d22 all `analysis`), not replayed from v1.
- **Since d15 Mastery is a MIXED-DAY bundle** (d15-d21 5 sets, d22 6, d23 7, d24 8, d25 9, d26 TEN: +1/day since d22),
  all under today's prompt. Solve each set from its own APK; never assume the set count or the schema.
- **Old days regenerated as v2 now carry their REAL mechanic as code** (d25): d19 set = genuine `Class.forName` /
  `getDeclaredMethod` / `Method.invoke` dispatch; d16 set = the u16 length-narrowing gate inside the native export; d14 set
  LCG table; d15 set JNI hop. d26: d11, d13, d21 arrived as v2 with NO real API (pure chain; solver handled). Unseen as v2
  so far: d05, d08, d12, d18, d20 -- may carry their mechanic.
- In every APK `.ChallengeActivity` builds a device-loopback URL `http://127.0.0.1:19090/mobile/attempt/<id>/evidence?
  case_id=..&client_secret=SECRET-..&proof=<answer>`. NOT reachable (it is the phone's loopback). The GM accepted the
  statically recovered value on all 26 days (d26 TT+Mastery live workers again curled it via `hb exec`: unreachable).
- Single = flavour, timed = mechanic (d16-d22 as dex strings; d23+ as executable code). Open the TT/Mastery APK fresh.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Puzzle schema (d23-d26)** -- v1 in the single, v2 `analysis` (no `data`, field `build`) in TT and in ALL Mastery
  sets incl. old days (d23 7/7 ... d26 10/10; in a split bundle the v2 JSON sits in `base.apk`). Rule: branch on the JSON, not on the day: `data` present -> codec chain below; `codec ==
  "analysis"` / no `data` / schema v2 -> evaluate the `Release.code` chain in dex; neither -> code scanners.
- **Puzzle codec (v1)** -- single + TT shared the day's codec through d22. `key` (xor byte d4/d11/d18/d23: 81, 104, 109,
  205, 99, ... full 0-255; caesar shift d7/d14) and split/offset params re-roll per variant: read them every time. Keyless
  codecs (`reverse`, `base64`, `native`, `reflection`) differ only in `data`. d17 `indexed`: same `order[i] = (3+7i) mod
  20` every variant. `split` (d5/d10/d24): `data:""`, 3 `parts` (lens 9/5/6, the `ANS-X` piece is not first) + `order
  [2,0,1]` every time seen; `order[i]` = output slot of `parts[i]`. d26 single: base `parts`
  has an EMPTY slot (`["","ANS-7","E37D13"]`) and the feature split's `assets/huntress_feature.json` `{"codec":"split",
  "feature":"arena_feature","part":"<9 hex>","part_index":0}` fills `parts[part_index]` BEFORE the scatter. `hex` (d6/d12/d25) = ASCII hex of the answer. d20 `dynamic`: `data` = `assets/payload.dex` everywhere. Rule: decode by declared codec,
  fullmatch `^ANS-[0-9A-F]{16}$`; entry path -> read the entry; unknown name -> `ANS-` known-plaintext; int list ->
  scatter and gather.
- **Split-bundle container (d26)** -- artifact `*.apks` (stored zip, 2 inner APKs `base.apk` + `feature.apk`; names may
  become `split_config.<abi|density|lang>.apk`) in single, TT and today's Mastery set (`delivery 10: ..._mastery_10.apks`);
  old-day sets stay plain `.apk`. Feature payload by schema: v1 = `huntress_feature.json` fragment (above); v2 =
  `assets/huntress_feature.bin`, 16 raw bytes, read by `Assets.readSplit(name)`: loop `ctx.getApplicationInfo()
  .splitSourceDirs` -> `new ZipFile(p).getEntry("assets/"+name)` -> `read` into `new byte[16]` -> `Util.mergeFeature*`
  folds them as TWO BIG-ENDIAN u64 (`j=(j<<8)|(b[i]&255)` over b[0:8] and b[8:16]) into the token (xor, rotr 9, `*K`,
  `+hi`, swap32, `*K`). Rule: outer zip with inner `PK` members -> unpack all; base = member holding
  `huntress_puzzle.json`; evaluate base's dex with `splitSourceDirs`/`ZipFile`/`AssetManager.open` served from the OTHER
  members' entries (never from the base); v1 -> fill empty `parts` from fragments by `part_index`, then scatter.
- **Computed-chain shape (d23-d26, v2)** -- per build: class names (`Core`, `Guard`, `Mix`, `Util`, `Probe`, `Tab`,
  theme-named `HookScan`/`TrampolineMap`/`SignalBank`/`TrustAnchor`, d24 `BoardCheck`/`SensorMap`, d25 `SealCheck`/
  `VerdictMap`), method names `<verb><ThemeWord><2 hex>` (`mixPatcheb`, `scanAlibi87`, `finIntegrity9a`), seed
  `const-wide`, mixer constants, probe kinds/args/COUNT (`s1: ((i*a+b)^c)&4095==d`, `s2: ((i^c)*a+b)&4095==d`, `s3`; 3
  calls d23-d24, 2 calls d25; `Probe` defines only the kinds it uses), the theme gate fn and its SIGNATURE
  (`(III)I`: `instrumentationSignals = (a^b^c)&7` d23, `emulatorScore = (a+b+c)%4` d24, `gateStreamac = ((a*3)^b^c)&255`
  d14, `gateDomain87 = ((a^b)+c)&255` d10, `gateNativefa = ((a+b)^c)&255` d16, `gateRelay*` d03, `gateVerify*` d09;
  `(JI)J`: d25 `integrityStatement(long a, int b) = a ^ (long)b`, result `long-to-int` before folding; `(II)I`: d26
  `SplitDecision.splitIndex(a,b) = (a<<4)|b`, 2 probes, `* K` into the fold), extras (d14
  `Tab.build` LCG `long[16]` walked 6 rounds; d15 `native long nativeShare(long)`; d16 `native long nativeShare(long, int
  len)` = returns 0 unless `len > 0xffff && (u16)len == K` (dex passes a const that passes, e.g. 104414 -> 0x97DE), then
  xor/shr/rol/add/imul; d19 `routeMaze*` = `"m" + ReflectionMaze.dispatch(k)` (packed-switch) -> `Class.forName(<pkg>.Maze)
  .getDeclaredMethod(name, long.class).invoke(null, Long)` over 8 look-alike `Maze.m0..m7`). Fixed: `Release.code` = `"ANS-"` + 16 nibbles via
  `"0123456789ABCDEF".charAt((v >>> i) & 15)` of `fin(Mix.f1(token())) ^ K`; `proof` = `Long.toHexString(token())`.
  Rule: INTERPRET from the entry (`Release.code`, the value reaching `proof=`); never key on names; unreferenced
  look-alike mixers/`K*` consts are the "generated false positives".
- **Answer location** -- puzzle JSON d1-d19 and d21-d23 single (d15-d16 also `.so` `.rodata`); d20 nested asset dex;
  d23+ TT/Mastery = computed by dex (+ JNI for the d15/d16 sets; + feature-split bytes d26); d26 single = base JSON +
  feature JSON fragment. Fallback chain: v2 eval, `raw_entry_scan`, `dex_strings`,
  `strings -a lib/*/*.so | grep ANS-`, `extract_answer`.
- **Mastery set mix (d15+)** -- fixtures of DIFFERENT days (codec/schema, theme, package `dNN`, extra entries); JSON `day`
  and dex `DAY` name the source day; picks re-roll per attempt; last set = today's (d24: d03 d06 d09 d10+NSC d15+.so d17
  d23 d24; d25: d01 d04 d07 d10+NSC d14 d16+.so d19 d22 d25; d26: d02 d03 d06 d11 d13 d16+.so d19 d21 d25 d26.apks). d16 the question's case ref did NOT
  match the APK (d23 they matched). Rule: per-set, schema-agnostic decoding -- never branch on the day or case ref.
- **Mastery packaging** -- `delivery N: <name>_mastery_NN.apk|.apks` per set (2-digit `NN`, `10` on d26): pair by sha256,
  never by extension. 3, 5, 6, 7 (d23), 8 (d24), 9 (d25), 10 (d26) sets, ids `setN.answer`. Loop over answer_ids.
- **Per-variant identity** -- case ref `MOB-NN-<10 hex>`, package suffix `v<12 hex>`, `client_secret`, attempt slug, v2
  `build`. None fed the answer so far (watch `build`: a natural future seed).
- **Dex hint strings** -- v1 single dex: `CODEC`, `CONTROL`, `DAY-NN:<theme>:<mechanic>`, `describe`; d17-d22 TT dropped
  the tag and added the mechanic word. v2 dex (5.3-6.2 KB vs ~2.6 KB): `CODEC="analysis"`, `CONTROL`, int `DAY`, old
  days keep `describe()`. Rule: never require `CODEC`/`DAY-NN` to find or decode anything.
- **Manifest flags (d21)** -- `debuggable="true"` only on d21 APKs; changed nothing. Record as facts; branch only if code
  reads `ApplicationInfo.flags`/`BuildConfig.DEBUG`.
- **Native lib shape (d15-d16, d23-d25 v2 sets)** -- d15 literal lib; d16 TT gate `nativeEvidence(int)`; v2 d15 set: 13512 B
  lib exporting only `Java_<pkg>_NativeLibrarySecrets_nativeShare` + `huntress_arena_day`; v2 d16 set (d25): 13648 B,
  `nativeShare(JI)J` + `nativeEvidence` + `huntress_arena_length_accepts`, gate on the int arg. No `ANS-` literal in v2
  libs. Never key on export names, arity or lib size: mangle the JNI name from the dex `native` method, emulate it.

## Recognition cues -> first move

| You see | First move |
|---|---|
| `*.apk`, answer `ANS- + 16 uppercase hex` | `unzip -p x.apk assets/huntress_puzzle.json` (triage.md pre-extracts + prints it) |
| **`*.apks` / `.xapk` / zip of `base.apk` + `feature.apk` / `split_config.*.apk`** (d26) | unzip, `unzip -l` EVERY member; base = the one with `huntress_puzzle.json`. v1: fill empty `parts[part_index]` from the feature JSON, then scatter. v2: grep the base dex for `splitSourceDirs`/`ZipFile`/`getEntry`/`readSplit`; the chain reads `assets/<name>` from the OTHER split (d26: 16 B = 2 big-endian u64). Port the chain or javac it with a `Context` stub whose `readSplit` returns the feature bytes |
| puzzle v1 `{"codec":..,"data":..}` | decode per codec (list below); fullmatch `^ANS-[0-9A-F]{16}$` before submitting |
| **puzzle v2 `"codec":"analysis"`, no `data`** (d23-d25) | answer = `Release.code(ctx)`. First: `lib.android.puzzle_candidates` (deep Dalvik eval; d25 TT 0.76 s, 9-set Mastery 1.9 s). Manual fallback: `jadx -q -d j x.apk`; copy non-Activity sources; stub `package android.content; public class Context {}`; `Main` prints `Release.code(null)`; `javac` + `java`. Or port the ~6 static long fns to python (mask 2^64, `>>>` = logical) |
| v2 chain calls a `native` method (d15 set `nativeShare(long)`; d25 d16 set `nativeShare(long,int)` with a u16 gate) | `objdump -d -M intel lib/*/libarena.so` the export (~10-20 insns of cmp/movzx + movabs/add/xor/imul/rol), feed the dex's own int arg, port to python or unicorn-emulate. Do NOT `ctypes.CDLL` the artifact on the host |
| `Probe.s1/s2/s3(a,b,c,d)` loops | 12-bit inverse search: smallest i<4096 with f(i)==d, else -1. Pure, cheap: just evaluate |
| `data` is a path (`assets/payload.dex`, d20) | `unzip -p x.apk assets/payload.dex \| strings -a \| grep ANS-`; no dex magic -> known-plaintext unwrap |
| int list next to `data` (d17 `indexed`, d5 `split`) | `order[i]` = OUTPUT slot of `data[i]`: `r[order[i]] = data[i]` |
| Unknown v1 codec name | `data` already `ANS-`? An entry name? Else `data[:4]` vs `ANS-`: constant diff = shift, constant XOR = key |
| `lib/<abi>/*.so` | `strings -a \| grep ANS-`, `nm -D --defined-only`; d16 gate `nativeEvidence(int)`: `objdump -d` the checker (65536) |
| Nothing decodes | `lib.android.extract_answer`, then `strings -a classes*.dex assets/* lib/*/*.so \| grep ANS-` |
| Theme stubs (d17-d22: `a`/decoy, `decryptByte`, `dispatch`, `debuggerGate`, `rootSignals`) | asset first. Code-side: `dex_eval_scan`/`reflection_scan`/`clean_device_scan`, then `proof_flow_scan` to keep the value reaching `proof=` |
| Hook/instrumentation theme (d23 `hook_detection`, prompt "real signals vs generated false positives") | v2 chain; the gate fn is pure arithmetic over probe results; look-alike `seal*`/`K*` members nobody calls are the decoys |
| Emulator / integrity themes (d24 "pinned emulator used by the solve oracle"; d25 "forge or replay a bounded challenge-owned integrity statement and explain the missing binding") | same v2 chain; gate = 1 pure fn (`emulatorScore=(a+b+c)%4`; d25 `integrityStatement(long,int)=a^b`); `KQemu*`/`sealEmu*`/`KSeal*`/`KStatement*`/`KCert*` = decoys; no Build/PackageManager/token API. Just run the solver |
| v2 chain with `Class.forName` + `getDeclaredMethod` + `Method.invoke` (d25 Mastery d19 set) | method name = `"m" + dispatch(k)` (packed-switch); invoke the named `Maze.mN(long)` only; the other 7 `mN` are decoys. Solver handles it |
| Loopback `127.0.0.1:19090` | do NOT chase it: device-local. The answer is static |
| Prompt demands a live action (d8 "replay", d9 "exploit CA", d20 "signed") | still static: `unzip -l` for extra entries first |
| Mastery `delivery N: foo_mastery_0N.apk` | strip the prefix (`lib.common.find_artifact`); ids `setN.answer`; each set may be another day AND another schema |

Puzzle codecs seen (v1): `plain`, `native` (d15-d16), `reflection` (d19) = plaintext; `dynamic` (d20) = entry path;
`reverse` (d2, d8, d21); `base64` (d3, d9, d13, d22); `hex` (d6, d12, d25); `caesar` (d7, d14: `chr(ord(c)-key)` over EVERY
char, sign from `data[:4]`); `xor` (d4, d11, d18, d23 single: base64 + int key 0-255); `split` (d5, d10, d24, d26 with a
feature-split fragment: `parts[]` + `order[]`); `indexed` (d17). v2: `analysis` (d23-d26). `lib.android.decode_payload` / `puzzle_candidates` / `decode_any`
cover v1; v2 = lib's deep Dalvik evaluator (`_DxeDeepVM`, via `puzzle_candidates`) + solve.py `_native_eval`
(unicorn JNI hop). Code-side: `bytecode_vm_scan` (`_DxVM`, bigger budget) reproduced the d23 TT value but resolved only 2 of
8 v2 APKs; also `renamed_chain_scan`, `proof_flow_scan`, `dex_eval_scan`, `reflection_scan`, `ans_compose_scan`
(on v2 it returns ANS-shaped DECOYS from the dead mixers -- never submit its first hit).

## Day by day

**Days 1-15** (0 wrong): d1 Exported Trust `plain` (~4 min lost on the loopback); d2 Deep Link Drift `reverse`; d3 Intent
Injection `base64`; d4 Pending Intent Relay `xor`; d5 Backup Spill `split`; d6 Provider Paths `hex`; d7 WebView Bridge
NEW `caesar`; d8 Cleartext `reverse`; d9 Trust Everyone `base64`; d10 Network Config Split `split` (+NSC); d11 Local
Secrets `xor`; d12 SQLite `hex`; d13 Keystore `base64`; d14 Predictable Crypto `caesar`; d15 Native Library Secrets:
first `libarena.so` (`.rodata` literal), codec `native`, first MIXED-DAY Mastery.

**Days 16-22** (asset held the answer; 0 wrong; carried-over solver CORRECT in ~2-25 s): d16 JNI Boundary `native`, TT
`.so` gate (65536). d17 Name Collapse NEW `indexed`, TT hint `follow b -> a and ignore field c`. d18 Encrypted Strings
`xor`, TT `decryptByte`. d19 Reflection Maze NEW `reflection` = plaintext. d20 Loaded Later NEW `dynamic`: `data` =
entry path, answer a const in `assets/payload.dex` class `...payload.Module`. d21 Debug Me If You Can `reverse`,
`debuggable=true`, no probe code. d22 Root of Trust `base64`, no probe code; first 6-set Mastery; title pun = key
attestation ASN.1 `RootOfTrust`.

**Days 23-25** (0 wrong): d23 Hook Line and Signal: single v1 `xor`; TT + 7 Mastery sets = FIRST v2 `analysis`
(`Release.code` = hex of `fin(Mix.f1(token())) ^ K`; gate `instrumentationSignals=(a^b^c)&7`; unreferenced `seal*`/`K*`
= the "generated false positives"); solver silent on v2, live workers hand-solved (jadx -> python port TT 94.5 s; javac +
`Context` stub Mastery ~2 min; d15 set via `ctypes.CDLL` = sandbox violation); v2 evaluator built overnight. d24 Emulator
Alibi: single v1 `split`; gate `emulatorScore=(a+b+c)%4`, no emulator probe API; solver 3/3 (TT 2.5 s, 8-set Mastery
3.1 s). d25 Integrity Signals: single v1 `hex`; first `(JI)J` gate `integrityStatement=a^(long)b`, 2 probes, no
PackageManager/IntegrityManager code; 9-set Mastery where old days RUN their mechanic (d19 real `forName`/
`getDeclaredMethod("m"+dispatch(k)).invoke`, d16 native u16 length gate); solver 3/3 (Mastery 3.7 s, solve 1.89 s).

**Day 26 — Split Decision** (`CONTROL="split_apk"`, `STRUCTURAL="base and feature split correlation"`; prompt
"Reassemble evidence distributed across base and configuration splits"; MainActivity: "cross the base and feature split
correlation boundary"). 0 wrong; single CORRECT 49 s, TT 83 s, Mastery 88 s -- the solver was SILENT on the v2 split
shape in both timed modes and live workers hand-solved.
- Artifact: `split_decision.apks` (21.5 KB stored zip) = `base.apk` (normal 6-entry fixture) + `feature.apk` (manifest
  `split="arena_feature"`, `hasCode=false`, 1 asset, no dex). First non-`.apk` container of the lane.
- Single (v1): base `{"codec":"split","parts":["","ANS-7","E37D13"],"order":[2,0,1]}` + feature `huntress_feature.json`
  `{"part":"4754DEA01","part_index":0}`. Fill `parts[0]`, then `r[order[i]] = parts[i]` -> `ANS-7` `E37D13` `4754DEA01`.
  The day26 solve.py `_split_bundle` handles it.
- TT + Mastery set10 (v2, base dex 6.4 KB): `token() = Util.mergeFeature*(Guard.scanBase*(Core.mixBase*(seed)))`;
  `scanBase*` = 2 probes + gate `SplitDecision.splitIndex(a,b) = (a<<4)|b`; `mergeFeature*` calls
  `Assets.readSplit("huntress_feature.bin")` (loop `ctx.getApplicationInfo().splitSourceDirs`, `java.util.zip.ZipFile`
  `getEntry("assets/"+name)`, read 16 B) and folds hi/lo big-endian u64s. `Release.code` = `"ANS-"` + nibbles of
  `Core.finFeature*(Mix.f1(token())) ^ K`. Decoys `sealBase*`/`sealFeature*`/`sealMerge*`, `KFeature*`/`KSplit*`/`KMerge*`.
  The lib deep evaluator aborts on `ApplicationInfo`/`ZipFile` (no split bytes) -> nothing. Hand-solve: jadx base dex ->
  python port with the 16 bytes from `unzip -p feature.apk assets/huntress_feature.bin` (~60 s).
- Mastery: 10 sets; 9 old-day v2 sets solver-verified in 1.13 s solve (incl. first-time-v2 d11, d13, d21: pure chains,
  NO SharedPreferences/KeyStore/Debug API; the d06 set's dex references `ContentValues`/`Cursor`). Only set10 (today's
  `.apks`) needed the live worker. The mastery generalize worker wrote a split-aware eval (serve `(String)[B` readers
  from the split members) but it did not persist in solve.py -> overnight prebuild `v2-split-asset-read`.
- GM spelling unchanged (`answer` / `setN.answer`, `exact`, `ANS-` + 16 uppercase hex).

## GM answer conventions learned
- One field, `answer`. Single solve and TT use id `answer`; Mastery uses `setN.answer` (3, 5-10 sets; 10 on d26).
- Format `ANS-` + exactly 16 UPPERCASE hex, normalization `exact`. v2 code already emits uppercase via the hex table.
- No worker-derived mobile answer has ever been rejected (d1-d26). Only harness placeholders from a silent solver were.
- Mastery feedback per set: `{"result":"accepted","remaining":N,"accepted_ids":[..]}`, then `CORRECT` on the last.
- Prompt boilerplate: "For case MOB-NN-<10 hex> in package com.huntress.mobile.dNN.v<12 hex>: ... Submit only the exact
  backend answer code returned for this case." The "backend" is the device loopback: the static value IS that code.

## Pitfalls that cost time
- **Single shape != timed shape** (d23 v1 `xor` vs v2; d26 v1 JSON fragment vs v2 split-bytes read): a solver tested only
  on the single is silent in TT/Mastery. Treat a schema or container bump as a new construct family.
- **Generalize cut off / not persisted** (d23, d26): live workers hand-solved; the generalize edit never landed in the
  solver. Overnight prebuilds close it (d24 went 3/3 on the solver alone) -- the lib path is what carries a day.
- **Container-only checks** (d26): every member of an `.apks` must be listed; the evidence for the base's chain lives in
  the feature split. Never read `huntress_feature.*` from the base, never assume the inner names stay `base`/`feature`.
- **Regex-compose decoys** (d23+): `"0123456789ABCDEF"` and `"ANS-"` sit in `Release`; dead `seal*` mixers make more
  ANS-shaped values (`ans_compose_scan`). Only the value of `Release.code` reached from ChallengeActivity counts.
- **Running artifact native code** (d23 `ctypes.CDLL(libarena.so)`): sandbox violation. Read (`objdump -d`) and port, or unicorn.
- **Chasing the loopback backend**: ~4 min (d1), ~2.3 min (d6), again d26 TT + Mastery (`hb exec curl 127.0.0.1:19090`)
  lured by "the exact backend answer code returned". It is the phone's own loopback: submit the static value.
- **Taking `data` at face value** (d20): an entry path, not a value. Always fullmatch the ANS regex on the final value.
- **Assuming "today's codec/schema/container" in Mastery** (d15+): sets come from older days, even old days are v2, and
  only today's set was an `.apks` (d26).
- **Ghidra on a ~14 KB unstripped `.so`**: `strings`/`nm`/`objdump -d` of the one `Java_*` export first.
- **New codec, generic solver silent** (d17 `indexed`): write the 5-line decoder straight away, anchored on `ANS-`.
- **Trusting dex `CODEC`/`DAY-NN` strings or the question's case ref** (d16, d17-d22 TT): key on the JSON and the code.
- **split/indexed order semantics:** `r[order[i]] = parts[i]` (validated d5, d10, d24, d26); fill empty `parts` slots
  from split fragments FIRST. **caesar:** raw codepoints. **Mastery filenames** carry a literal `delivery N: ` prefix.
- **Timed windows** are start + download + submit; solve must be <1 s pure python (no jadx/javac subprocess in solve.py).
- **Prompt verbs escalate faster than the artifact** (d8 "replay", d15 "split", d19 "call graphs", d20 "signed module",
  d21 "state machine", d22 "multiple root signals", d24 "pinned emulator", d25 "forge or replay an integrity statement"
  = one pure gate fn). BUT the NOUN can be literal: d23 "generated false positives" = dead mixers; d26 "distributed
  across base and configuration splits" = a real 2-APK bundle with the chain reading the split. Judge by the artifact
  (container, schema, dex size 2.6 -> 5.7-6.4 KB, real API refs `forName`/`loadLibrary`/`ZipFile`/`splitSourceDirs`).
- **Escalation is not monotonic** (d21 `reverse` after d20's pointer; d23-d26 singles still v1). Keep every decoder.
- **Escalation lives in Mastery old-day sets AND in the timed chain's I/O** (d25 d19 real reflection + d16 native gate;
  d26 chain reads artifact bytes). If the solver goes silent on ONE set, `strings -a classes.dex | grep -E 'ZipFile|
  splitSource|getAssets|DexClassLoader|forName|decrypt|getShared|SQLite|KeyStore|isDebugger'`, hand-eval that link, and
  batch-submit every set's answer in one request.
- **Escalation watch:** next cheap steps after d26 -- code IN the feature split (split dex, `createContextForSplit`,
  split ClassLoader), several config splits (`split_config.x86_64`/`arm64_v8a`/`xxhdpi`/`en`) where only the device-
  matching one counts (oracle = pinned x86_64 emulator), `.so` in a config split, split resources.arsc overrides, split
  signature/digest binding, AAB/protobuf manifests. Mastery solve 1.13 s for 9 sets (d26): fine, keep per-set cost flat.
