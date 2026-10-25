# mobile-android — technique log (days 1-25; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Every APK so far was the same ~12.7 KB fixture: `AndroidManifest.xml`, `assets/huntress_puzzle.json`, `classes.dex`,
  `META-INF/FIXTURE-.{SF,RSA}`, `MANIFEST.MF` (6 entries). Extras: d10 `res/xml/network_security_config.xml` +
  `resources.arsc` (8 entries); d15-d16 `lib/x86_64/libarena.so` (7 entries); d20 `assets/payload.dex` (508 B plain dex).
  d21 the only manifest with `android:debuggable="true"`. One question, `answer` = `ANS-` + 16 uppercase hex.
- Each day has a new Android IPC/security THEME, written in the manifest `<meta-data android:name="huntress.mechanic">`
  and in dex constants (`DAY-NN:<theme_id>:<mechanic>` tag or `CONTROL`/`STRUCTURAL` fields): exported Activity, deep
  link, nested Intent, mutable PendingIntent, allowBackup, ContentProvider, JS interface, cleartext, X509 trust manager,
  NSC, SharedPreferences, SQLite authz, Keystore, predictable nonce d14, `jni_secret` d15, `jni_length` d16,
  `identifier_obfuscation` d17, `string_decryption` d18, `reflective_dispatch` d19, `dynamic_dex` d20, `anti_debug` d21,
  `root_detection` d22, `hook_detection` "hook and instrumentation detection" d23, `emulator_detection` "emulator
  environment detection" d24, `integrity_signal` "challenge-owned integrity statement" d25. Through d22 the theme was flavour only (stub classes never needed). **Since d23 TT/Mastery
  COMPUTE the answer in dex code**; the theme is now one pure-arithmetic gate fn inside that chain (no Android API yet).
- Puzzle JSON v1 (`schema: huntress.mobile.puzzle.v1`, d1-d24 single, d1-d22 TT/Mastery): the answer sits behind a
  rotating `codec` (plain, reverse, base64, xor+key, split, hex, caesar+key, native, indexed, reflection, dynamic =
  pointer to `assets/payload.dex`; old codecs recur: d21 reverse, d22 base64, d23 xor, d24 split, d25 hex). Keys re-roll.
- **Puzzle JSON v2 (d23-d25 TT and every Mastery set):** `{"schema":"huntress.mobile.puzzle.v2","day":N,"codec":
  "analysis","build":"<12 hex>"}` -- NO `data`. The answer is `Release.code(Context)` evaluated statically (see Day 23).
  Older days' Mastery sets were REGENERATED in v2 (d02/d06/d10/d14/d15/d22 all `analysis`), not replayed from v1.
- **Since d15 Mastery is a MIXED-DAY bundle** (d15-d21 5 sets, d22 6, d23 7, d24 8, d25 NINE: +1 set per day since d22),
  all under today's prompt. Solve each set from its own APK; never assume the set count or the schema.
- **Old days regenerated as v2 now carry their REAL mechanic as code** (d25): d19 set = genuine `Class.forName` /
  `getDeclaredMethod` / `Method.invoke` dispatch; d16 set = the u16 length-narrowing gate inside the native export; d14 set
  LCG table; d15 set JNI hop. Unseen as v2 so far: d05, d08, d11, d12, d13, d18, d20, d21 -- expect each with its mechanic.
- In every APK `.ChallengeActivity` builds a device-loopback URL `http://127.0.0.1:19090/mobile/attempt/<id>/evidence?
  case_id=..&client_secret=SECRET-..&proof=<answer>`. NOT reachable (it is the phone's loopback). The GM accepted the
  statically recovered value on all 25 days.
- Pattern d16-d22: the SINGLE variant carries flavour, the TT build carries the mechanic as dex strings (`decryptByte`,
  `dispatch`, `moduleContract`, `debuggerGate`, `rootSignals` + `STRUCTURAL`). d23 broke it for real: the TT build carried
  executable mechanics; d24 repeated the split (single v1 `split`, timed v2). Always open the TT/Mastery APK fresh.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Puzzle schema (d23-d25)** -- v1 in the single, v2 `analysis` (no `data`, field `build`) in TT and in ALL Mastery
  sets incl. old days (d23 7/7, d24 8/8, d25 9/9). Rule: branch on the JSON, not on the day: `data` present -> codec chain below; `codec ==
  "analysis"` / no `data` / schema v2 -> evaluate the `Release.code` chain in dex; neither -> code scanners.
- **Puzzle codec (v1)** -- single + TT shared the day's codec through d22. `key` (xor byte d4/d11/d18/d23: 81, 104, 109,
  205, 99, ... full 0-255; caesar shift d7/d14) and split/offset params re-roll per variant: read them every time. Keyless
  codecs (`reverse`, `base64`, `native`, `reflection`) differ only in `data`. d17 `indexed`: same `order[i] = (3+7i) mod
  20` every variant. `split` (d5/d10/d24): `data:""`, 3 `parts` (lens 9/5/6, the `ANS-X` piece is not first) + `order
  [2,0,1]` every time seen; `order[i]` = output slot of `parts[i]`. `hex` (d6/d12/d25) = ASCII hex of the answer. d20 `dynamic`: `data` = `assets/payload.dex` everywhere. Rule: decode by declared codec,
  fullmatch `^ANS-[0-9A-F]{16}$`; entry path -> read the entry; unknown name -> `ANS-` known-plaintext; int list ->
  scatter and gather.
- **Computed-chain shape (d23-d25, v2)** -- per build: class names (`Core`, `Guard`, `Mix`, `Util`, `Probe`, `Tab`,
  theme-named `HookScan`/`TrampolineMap`/`SignalBank`/`TrustAnchor`, d24 `BoardCheck`/`SensorMap`, d25 `SealCheck`/
  `VerdictMap`), method names `<verb><ThemeWord><2 hex>` (`mixPatcheb`, `scanAlibi87`, `finIntegrity9a`), seed
  `const-wide`, mixer constants, probe kinds/args/COUNT (`s1: ((i*a+b)^c)&4095==d`, `s2: ((i^c)*a+b)&4095==d`, `s3`; 3
  calls d23-d24, 2 calls d25; `Probe` defines only the kinds it uses), the theme gate fn and its SIGNATURE
  (`(III)I`: `instrumentationSignals = (a^b^c)&7` d23, `emulatorScore = (a+b+c)%4` d24, `gateStreamac = ((a*3)^b^c)&255`
  d14, `gateDomain87 = ((a^b)+c)&255` d10, `gateNativefa = ((a+b)^c)&255` d16, `gateRelay*` d03, `gateVerify*` d09;
  `(JI)J`: d25 `integrityStatement(long a, int b) = a ^ (long)b`, result `long-to-int` before folding), extras (d14
  `Tab.build` LCG `long[16]` walked 6 rounds; d15 `native long nativeShare(long)`; d16 `native long nativeShare(long, int
  len)` = returns 0 unless `len > 0xffff && (u16)len == K` (dex passes a const that passes, e.g. 104414 -> 0x97DE), then
  xor/shr/rol/add/imul; d19 `routeMaze*` = `"m" + ReflectionMaze.dispatch(k)` (packed-switch) -> `Class.forName(<pkg>.Maze)
  .getDeclaredMethod(name, long.class).invoke(null, Long)` over 8 look-alike `Maze.m0..m7`). Fixed: `Release.code` = `"ANS-"` + 16 nibbles via
  `"0123456789ABCDEF".charAt((v >>> i) & 15)` of `fin(Mix.f1(token())) ^ K`; `proof` = `Long.toHexString(token())`.
  Rule: INTERPRET from the entry (`Release.code`, the value reaching `proof=`); never key on names; unreferenced
  look-alike mixers/`K*` consts are the "generated false positives".
- **Answer location** -- puzzle JSON d1-d19 and d21-d23 single (d15-d16 also `.so` `.rodata`); d20 nested asset dex;
  d23 TT/Mastery = computed by dex (+ JNI for the d15 set). Fallback chain: v2 eval, `raw_entry_scan`, `dex_strings`,
  `strings -a lib/*/*.so | grep ANS-`, `extract_answer`.
- **Mastery set mix (d15+)** -- fixtures of DIFFERENT days (codec/schema, theme, package `dNN`, extra entries); JSON `day`
  and dex `DAY` name the source day; picks re-roll per attempt; last set = today's (d24: d03 d06 d09 d10+NSC d15+.so d17
  d23 d24; d25: d01 d04 d07 d10+NSC d14 d16+.so d19 d22 d25 -- one old day per 3-day stride). d16 the question's case ref did NOT
  match the APK (d23 they matched). Rule: per-set, schema-agnostic decoding -- never branch on the day or case ref.
- **Mastery packaging** -- `delivery N: <name>_mastery_0N.apk` per set: pair by sha256. 3, 5, 6, 7 (d23), 8 (d24), 9 (d25) sets,
  ids `setN.answer`. Loop over the contract's answer_ids.
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
char, sign from `data[:4]`); `xor` (d4, d11, d18, d23 single: base64 + int key 0-255); `split` (d5, d10: `parts[]` +
`order[]`); `indexed` (d17). v2: `analysis` (d23-d25). `lib.android.decode_payload` / `puzzle_candidates` / `decode_any`
cover v1; v2 = lib's deep Dalvik evaluator (`_DxeDeepVM`, via `puzzle_candidates`) + solve.py `_native_eval`
(unicorn JNI hop). Code-side: `bytecode_vm_scan` (`_DxVM`, bigger budget) reproduced the d23 TT value but resolved only 2 of
8 v2 APKs; also `renamed_chain_scan`, `proof_flow_scan`, `dex_eval_scan`, `reflection_scan`, `ans_compose_scan`
(on v2 it returns ANS-shaped DECOYS from the dead mixers -- never submit its first hit).

## Day by day

**Days 1-6** (all first try): d1 Exported Trust `plain` (~5.4 min, ~4 min lost on the loopback); d2 Deep Link Drift
`reverse`; d3 Intent Injection `base64`; d4 Pending Intent Relay `xor`; d5 Backup Spill `split` (`order[i]` = output
slot); d6 Provider Paths `hex` (2.3 min lost on the loopback).

**Days 7-15** (0 wrong, TT/Mastery 0.8-3.5 s): d7 WebView Bridge NEW `caesar`; d8 Cleartext `reverse`; d9 Trust
Everyone `base64`; d10 Network Config Split `split` (8-entry + NSC); d11 Local Secrets `xor`; d12 SQLite `hex`; d13
Keystore `base64`; d14 Predictable Crypto `caesar` (json-load escapes). d15 Native Library Secrets: first `libarena.so`
(literal in `.rodata`), codec `native`; first MIXED-DAY Mastery.

**Days 16-22** (asset held the answer; 0 wrong; carried-over solver CORRECT in ~2-25 s): d16 JNI Boundary `native`, TT
`.so` gate (65536). d17 Name Collapse NEW `indexed`, TT hint `follow b -> a and ignore field c`. d18 Encrypted Strings
`xor`, TT `decryptByte`. d19 Reflection Maze NEW `reflection` = plaintext. d20 Loaded Later NEW `dynamic`: `data` =
entry path, answer a const in `assets/payload.dex` class `...payload.Module`. d21 Debug Me If You Can `reverse`,
`debuggable=true`, no probe code. d22 Root of Trust `base64`, no probe code; first 6-set Mastery; title pun = key
attestation ASN.1 `RootOfTrust`.

**Day 23 — Hook Line and Signal** (`hook_detection`; "Separate real instrumentation signals from generated false
positives"). Single v1 `xor` (key 81), race probe CORRECT 22.4 s. TT + all 7 Mastery sets: FIRST v2 `analysis` (dex
5.7 KB, no `ANS-` literal): `Release.code` = hex of `fin(Mix.f1(token())) ^ K`, `token()` = 3 nested static long fns
folding `Probe.s*` results and `instrumentationSignals(a,b,c)`; ChallengeActivity calls `code` only if the `answer` extra
equalsIgnoreCase `Release.proof`. Unreferenced `seal*`/`K*` look-alikes = the "generated false positives". The
carried-over solver was silent on v2; live workers hand-solved (jadx -> python port, TT 94.5 s; Mastery javac with a
1-line `android.content.Context` stub, ~2.0 min; d15 set via `ctypes.CDLL` = sandbox violation). v2 evaluator built overnight.

**Day 24 — Emulator Alibi** (`emulator_detection`; "Defeat app-owned environment checks on the same pinned emulator used
by the solve oracle"), all first try. Single v1 `split` (`order [2,0,1]`), race probe CORRECT 16.3 s. TT v2: gate
`EmulatorAlibi.emulatorScore = (a+b+c) % 4`; classes `BoardCheck`/`SensorMap`; decoys `sealEmu*`/`KQemu*`. NO emulator
probe (`Build.*`, goldfish, qemu props, sensors) in any dex. TT 2.5 s, FIRST 8-set Mastery (all v2, d15 set via the
unicorn JNI hop) 3.1 s.

**Day 25 — Integrity Signals** (`CONTROL="integrity_signal"`, `STRUCTURAL="challenge-owned integrity statement"`; prompt
"Forge or replay a bounded challenge-owned integrity statement and explain the missing binding." -- Play Integrity pun:
the "missing binding" is the nonce/requestHash binding of a verdict). All three modes first try, 0 wrong, 0 time lost.
- Single: plain v1 6-entry fixture (12704 B, dex 2608 B), `{"codec":"hex","data":"414e532d..."}` = ASCII hex of the
  answer (3rd `hex` day after d6/d12). Prebuilt race probe: CORRECT ~5 s after start (submit RTT 1.58 s).
- TT: v2 `analysis` (dex 5660 B). `token() = VerdictMap.mixVerdict*(scanIntegrity*(mixIntegrity*(<seed>)))`; `scan*`
  calls only TWO probes (`Probe.s2`, `Probe.s3`) and the gate `IntegritySignals.integrityStatement(long a, int b) =
  a ^ (long)b` -- first gate fn with a `(JI)J` signature; its result is `long-to-int` truncated, then `* K` into the fold.
  `Release.code` = `"ANS-"` + nibbles of `SealCheck.finIntegrity*(Mix.f1(token())) ^ K`. Decoys `seal*`, `KSeal*`,
  `KStatement*`, `KCert*`. Despite the prompt: NO PackageManager/signature/IntegrityManager/token/JSON/nonce code in any
  dex -- nothing to forge or replay. Solver CORRECT 2.19 s total (solve 0.76 s).
- Mastery: FIRST 9-set bundle (d01, d04, d07, d10 +NSC, d14, d16 +`libarena.so`, d19, d22, d25), all v2. New: the d19
  set does REAL reflection (`"m"+dispatch(1)` -> `Class.forName(..Maze).getDeclaredMethod("m7", long.class).invoke(null,
  Long)`), and the d16 set's `nativeShare(long, int)` re-implements the d16 u16 length-narrowing gate in native code
  (`len > 0xffff && (u16)len == K` else 0; dex passes a passing const). Solver CORRECT 3.68 s (solve 1.89 s, double
  d24's 0.94 s for one extra set -- watch the scaling).
- GM spelling unchanged (`answer` / `setN.answer`, `exact`, `ANS-` + 16 uppercase hex). Mastery submit body lists the ids
  out of order (`set6` last): match by id, never by position.

## GM answer conventions learned
- One field, `answer`. Single solve and TT use id `answer`; Mastery uses `setN.answer` (3, 5, 6, 7, 8 or 9 sets).
- Format `ANS-` + exactly 16 UPPERCASE hex, normalization `exact`. v2 code already emits uppercase via the hex table.
- No worker-derived mobile answer has ever been rejected (d1-d25). Only harness placeholders from a silent solver were.
- Mastery feedback per set: `{"result":"accepted","remaining":N,"accepted_ids":[..]}`, then `CORRECT` on the last.
- Prompt boilerplate: "For case MOB-NN-<10 hex> in package com.huntress.mobile.dNN.v<12 hex>". Never needed.

## Pitfalls that cost time
- **Single shape != timed shape** (d23): single was v1 `xor`, TT/Mastery v2 computed. A solver tested only on the single
  (and on old v1 auto cases) emitted nothing in TT and all 7 Mastery sets. Treat a schema bump as a new construct family.
- **Generalize cut off at CORRECT** (d23): the live worker hand-solved; the generalize workers died before writing the
  v2 path. The overnight prebuild closed it, and d24 went 3/3 on the solver alone -- the lib path is what carries a day.
- **Regex-compose decoys** (d23): the hex table `"0123456789ABCDEF"` and `"ANS-"` both sit in `Release`; dead mixers make
  more ANS-shaped values (`ans_compose_scan`). Only the value of `Release.code` reached from ChallengeActivity counts.
- **Running artifact native code** (d23 `ctypes.CDLL(libarena.so)`): violates the sandbox rule. The export was ~10
  instructions of arithmetic: read it (`objdump -d`) and port, or unicorn.
- **Chasing the loopback backend**: ~4 min (d1), ~2.3 min (d6). `127.0.0.1:19090` is the phone's own loopback.
- **Taking `data` at face value** (d20): an entry path, not a value. Always fullmatch the ANS regex on the final value.
- **Assuming "today's codec/schema" in Mastery** (d15+): sets come from older days, and since d23 even old days are v2.
- **Reaching for Ghidra on a ~14 KB unstripped `.so`**: `strings`/`nm`/`objdump -d` of the one `Java_*` export first.
- **New codec, generic solver silent** (d17 `indexed`): write the 5-line decoder straight away, anchored on `ANS-`.
- **Trusting dex `CODEC`/`DAY-NN` strings or the question's case ref** (d16, d17-d22 TT): key on the JSON and the code.
- **split/indexed order semantics:** two readings exist; validate against the regex. **caesar:** raw codepoints.
- **Mastery filenames** carry a literal `delivery N: ` prefix. A naive path lookup fails.
- **Timed windows** are start + download + submit; solve must be <1 s pure python (no jadx/javac subprocess in solve.py).
- **Prompt wording escalated for 22 days while the artifact did not -- then d23 delivered** (d8 "replay", d15 "split",
  d19 "call graphs", d20 "signed module", d21 "state machine", d22 "multiple root signals", d23 "real signals vs generated
  false positives" = probe results + dead look-alike mixers; d24 "pinned emulator used by the solve oracle" and d25
  "forge or replay an integrity statement ... missing binding" = still one pure gate fn, nothing to emulate, forge or
  replay). Judge by the APK (schema, dex size jump 2.6 -> 5.7 KB, `Release`/`Probe` classes, `native` methods, real
  API refs like `forName`/`loadLibrary`), never by the verb.
- **Escalation is not monotonic** (d21 back to `reverse` after d20's pointer; d23-d25 singles still v1). Keep every decoder.
- **Escalation moved into the OLD-DAY Mastery sets** (d25): the TT chain stayed a pure gate fn, but the regenerated d19
  set used real reflection and the d16 set put a narrowing gate in native code. Every never-yet-v2 old day (d05 backup,
  d08 cleartext, d11 prefs, d12 SQLite, d13 Keystore, d18 `decryptByte`, d20 `DexClassLoader` payload, d21 debugger
  state machine) may arrive with its mechanic as executable code. If the solver goes silent on ONE set, open that set's
  dex for the source day's API (`strings -a classes.dex | grep -E 'DexClassLoader|forName|decrypt|getShared|SQLite|
  KeyStore|isDebugger'`) and hand-eval just that link; submit the other sets' answers in the same batch.
- **Escalation watch:** v2 `analysis` is the timed baseline (d23-d25 unchanged in shape; only the gate fn, its signature
  and the class words follow the theme). If a chain ever reads the environment, note the d24 wording: the oracle runs on
  a PINNED EMULATOR, so evaluate both a clean-Pixel and a stock-AVD profile and report both. Next cheap steps: chain
  reads Android state (assets JSON `build`, PackageManager signature, Resources, SharedPreferences, `Build.*`) -- stub
  with the APK's own bytes and a clean retail device; flattened or VM-dispatched mixers; cross-dex calls into
  `assets/payload.dex`; JNI in more sets; the `proof` gate demanding a derived input. Mastery solve time doubled d24->d25
  (0.94 -> 1.89 s for 8 -> 9 sets): a slow new set kind can eat the window as the bundle grows.
