# mobile-android — technique log (days 1-23; updated after every day)

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
  `root_detection` d22, `hook_detection` "hook and instrumentation detection" d23. Through d22 the theme was flavour
  only (stub classes never needed). **d23 TT/Mastery is the first build where the answer is COMPUTED by dex code.**
- Puzzle JSON v1 (`schema: huntress.mobile.puzzle.v1`, d1-d23 single, d1-d22 TT/Mastery): the answer sits behind a
  rotating `codec` (plain, reverse, base64, xor+key, split, hex, caesar+key, native, indexed, reflection, dynamic =
  pointer to `assets/payload.dex`; old codecs recur: d21 reverse, d22 base64, d23 xor). Keys re-roll per variant.
- **Puzzle JSON v2 (NEW d23 TT + every d23 Mastery set):** `{"schema":"huntress.mobile.puzzle.v2","day":N,"codec":
  "analysis","build":"<12 hex>"}` -- NO `data`. The answer is `Release.code(Context)` evaluated statically (see Day 23).
  Older days' Mastery sets were REGENERATED in v2 (d02/d06/d10/d14/d15/d22 all `analysis`), not replayed from v1.
- **Since d15 Mastery is a MIXED-DAY bundle** (d15-d21 5 sets, d22 6, d23 SEVEN: d02, d06, d10, d14, d15, d22, d23), all
  under today's prompt. Solve each set from its own APK; never assume the set count or the schema.
- In every APK `.ChallengeActivity` builds a device-loopback URL `http://127.0.0.1:19090/mobile/attempt/<id>/evidence?
  case_id=..&client_secret=SECRET-..&proof=<answer>`. NOT reachable (it is the phone's loopback). The GM accepted the
  statically recovered value on all 23 days.
- Pattern d16-d22: the SINGLE variant carries flavour, the TT build carries the mechanic as dex strings (`decryptByte`,
  `dispatch`, `moduleContract`, `debuggerGate`, `rootSignals` + `STRUCTURAL`). d23 broke it for real: the TT build carried
  executable mechanics. Always open the TT/Mastery APK fresh -- the single's shape is not the timed shape.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Puzzle schema (NEW d23)** -- v1 in the single, v2 `analysis` (no `data`, field `build`) in TT and in ALL 7 Mastery
  sets incl. old days. Rule: branch on the JSON, not on the day: `data` present -> codec chain below; `codec ==
  "analysis"` / no `data` / schema v2 -> evaluate the `Release.code` chain in dex; neither -> code scanners.
- **Puzzle codec (v1)** -- single + TT shared the day's codec through d22. `key` (xor byte d4/d11/d18/d23: 81, 104, 109,
  205, 99, ... full 0-255; caesar shift d7/d14) and split/offset params re-roll per variant: read them every time. Keyless
  codecs (`reverse`, `base64`, `native`, `reflection`) differ only in `data`. d17 `indexed`: same `order[i] = (3+7i) mod
  20` every variant. d20 `dynamic`: `data` = `assets/payload.dex` everywhere. Rule: decode by declared codec,
  fullmatch `^ANS-[0-9A-F]{16}$`; entry path -> read the entry; unknown name -> `ANS-` known-plaintext; int list ->
  scatter and gather.
- **Computed-chain shape (NEW d23, v2)** -- per build: class names (`Core`, `Guard`, `Mix`, `Util`, `Probe`, `Tab`,
  theme-named `HookScan`/`TrampolineMap`/`SignalBank`/`TrustAnchor`), method names `<verb><ThemeWord><2 hex>` (`mixPatcheb`,
  `scanSignal61`, `finTrampoline2d`), seed `const-wide`, mixer constants, probe kinds/args (`Probe.s1/s2/s3`), the theme
  gate fn (`instrumentationSignals = (a^b^c)&7` d23, `gateStreamac = ((a*3)^b^c)&255` d14, `gateDomain87 = ((a^b)+c)&255`
  d10), extras (d14 `Tab.build` LCG `long[16]` table walked 6 rounds; d15 `native long nativeShare(long)` in
  `libarena.so`, pure add/xor/imul/rol arithmetic). Fixed: `Release.code` = `"ANS-"` + 16 nibbles via
  `"0123456789ABCDEF".charAt((v >>> i) & 15)` of `fin(Mix.f1(token())) ^ K`; `proof` = `Long.toHexString(token())`.
  Rule: INTERPRET from the entry (`Release.code`, the value reaching `proof=`); never key on names; unreferenced
  look-alike mixers/`K*` consts are the "generated false positives".
- **Answer location** -- puzzle JSON d1-d19 and d21-d23 single (d15-d16 also `.so` `.rodata`); d20 nested asset dex;
  d23 TT/Mastery = computed by dex (+ JNI for the d15 set). Fallback chain: v2 eval, `raw_entry_scan`, `dex_strings`,
  `strings -a lib/*/*.so | grep ANS-`, `extract_answer`.
- **Mastery set mix (d15+)** -- fixtures of DIFFERENT days (codec/schema, theme, package `dNN`, extra entries); JSON `day`
  and dex `DAY` name the source day; picks re-roll per attempt; last set = today's. d16 the question's case ref did NOT
  match the APK (d23 they matched). Rule: per-set, schema-agnostic decoding -- never branch on the day or case ref.
- **Mastery packaging** -- `delivery N: <name>_mastery_0N.apk` per set: pair by sha256. 3, 5, 6 (d22) or 7 (d23) sets,
  ids `setN.answer`. Loop over the contract's answer_ids.
- **Per-variant identity** -- case ref `MOB-NN-<10 hex>`, package suffix `v<12 hex>`, `client_secret`, attempt slug, v2
  `build`. None fed the answer so far (watch `build`: a natural future seed).
- **Dex hint strings** -- v1 single dex: `CODEC`, `CONTROL`, `DAY-NN:<theme>:<mechanic>`, `describe`; d17-d22 TT dropped
  the tag and added the mechanic word. v2 dex (5.3-6.2 KB vs ~2.6 KB): `CODEC="analysis"`, `CONTROL`, int `DAY`, old
  days keep `describe()`. Rule: never require `CODEC`/`DAY-NN` to find or decode anything.
- **Manifest flags (d21)** -- `debuggable="true"` only on d21 APKs; changed nothing. Record as facts; branch only if code
  reads `ApplicationInfo.flags`/`BuildConfig.DEBUG`.
- **Native lib shape (d15-d16, d23-d15set)** -- d15 literal lib; d16 TT gate `nativeEvidence(int)`; d23 v2 d15 set: 13512 B
  lib exporting only `Java_<pkg>_NativeLibrarySecrets_nativeShare` + `huntress_arena_day`, no `ANS-` literal. Never key on
  export names or lib size.

## Recognition cues -> first move

| You see | First move |
|---|---|
| `*.apk`, answer `ANS- + 16 uppercase hex` | `unzip -p x.apk assets/huntress_puzzle.json` (triage.md pre-extracts + prints it) |
| puzzle v1 `{"codec":..,"data":..}` | decode per codec (list below); fullmatch `^ANS-[0-9A-F]{16}$` before submitting |
| **puzzle v2 `"codec":"analysis"`, no `data`** (d23) | answer = `Release.code(ctx)`. Fast manual path: `jadx -q -d j x.apk`; copy non-Activity sources; stub `package android.content; public class Context {}`; `Main` prints `Release.code(null)`; `javac` + `java`. Or port the ~6 static long fns to python (mask 2^64, `>>>` = logical) |
| v2 chain calls a `native` method (d23 d15 set `nativeShare(long)`) | `objdump -d -M intel lib/*/libarena.so` the export (~10 insns of movabs/add/xor/imul/rol) and port to python, or unicorn-emulate it. Do NOT `ctypes.CDLL` the artifact on the host |
| `Probe.s1/s2/s3(a,b,c,d)` loops | 12-bit inverse search: smallest i<4096 with f(i)==d, else -1. Pure, cheap: just evaluate |
| `data` is a path (`assets/payload.dex`, d20) | `unzip -p x.apk assets/payload.dex \| strings -a \| grep ANS-`; no dex magic -> known-plaintext unwrap |
| int list next to `data` (d17 `indexed`, d5 `split`) | `order[i]` = OUTPUT slot of `data[i]`: `r[order[i]] = data[i]` |
| Unknown v1 codec name | `data` already `ANS-`? An entry name? Else `data[:4]` vs `ANS-`: constant diff = shift, constant XOR = key |
| `lib/<abi>/*.so` | `strings -a \| grep ANS-`, `nm -D --defined-only`; d16 gate `nativeEvidence(int)`: `objdump -d` the checker (65536) |
| Nothing decodes | `lib.android.extract_answer`, then `strings -a classes*.dex assets/* lib/*/*.so \| grep ANS-` |
| Theme stubs (d17-d22: `a`/decoy, `decryptByte`, `dispatch`, `debuggerGate`, `rootSignals`) | asset first. Code-side: `dex_eval_scan`/`reflection_scan`/`clean_device_scan`, then `proof_flow_scan` to keep the value reaching `proof=` |
| Hook/instrumentation theme (d23 `hook_detection`, prompt "real signals vs generated false positives") | v2 chain; the gate fn is pure arithmetic over probe results; look-alike `seal*`/`K*` members nobody calls are the decoys |
| Loopback `127.0.0.1:19090` | do NOT chase it: device-local. The answer is static |
| Prompt demands a live action (d8 "replay", d9 "exploit CA", d20 "signed") | still static: `unzip -l` for extra entries first |
| Mastery `delivery N: foo_mastery_0N.apk` | strip the prefix (`lib.common.find_artifact`); ids `setN.answer`; each set may be another day AND another schema |

Puzzle codecs seen (v1): `plain`, `native` (d15-d16), `reflection` (d19) = plaintext; `dynamic` (d20) = entry path;
`reverse` (d2, d8, d21); `base64` (d3, d9, d13, d22); `hex` (d6, d12); `caesar` (d7, d14: `chr(ord(c)-key)` over EVERY
char, sign from `data[:4]`); `xor` (d4, d11, d18, d23 single: base64 + int key 0-255); `split` (d5, d10: `parts[]` +
`order[]`); `indexed` (d17). v2: `analysis` (d23). `lib.android.decode_payload` / `puzzle_candidates` / `decode_any`
cover v1. Code-side: `bytecode_vm_scan` (`_DxVM`, bigger budget) reproduced the d23 TT value but resolved only 2 of
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

**Day 23 — Hook Line and Signal** (`CONTROL="hook_detection"`, `STRUCTURAL="hook and instrumentation detection"`; prompt
"Separate real instrumentation signals from generated false positives.")
- Single: plain v1 6-entry fixture (12704 B, dex 2604 B), `{"codec":"xor","data":"<b64>","key":81}`. Race probe
  CORRECT 22.4 s after start (13:00:14.9Z -> 13:00:37.3Z).
- TT: SAME 12704 B size but puzzle **v2 `analysis`**, dex 5684 B, no `ANS-` literal anywhere. jadx shows:
  `Release.token() = HookScan.mixPatcheb(Util.scanSignal61(Util.mixTrampoline79(<const long>)))`; `scanSignal61` xors
  in three `Probe.s3/s3/s2(...)` results times constants plus `HookLineAndSignal.instrumentationSignals(a,b,c)*K`;
  `Release.code` = `"ANS-%016X"` of `Util.finTrampoline2d(Mix.f1(token())) ^ K`. ChallengeActivity only calls `code`
  if the `answer` extra equalsIgnoreCase `Release.proof` (= `Long.toHexString(token())`), then puts `code` in `proof=`.
  Unreferenced look-alikes (`TrampolineMap.sealTrampolinec7`, `Util.sealHook30`, `HookScan.sealHook1e`, `KHook59`,
  `KPatchea`) are the "generated false positives". Live worker: jadx -> python port of 6 fns -> CORRECT 94.5 s after
  start (no clock).
- Mastery: 7 sets (d02, d06, d10, d14, d15, d22, d23), ALL v2. Live worker: jadx all 7, `javac` the non-Activity
  sources against a 1-line `android.content.Context` stub, one `Main` per set printing `Release.proof(null)` +
  `Release.code(null)` -> 6 accepted at ~97 s; d15 set: `nativeShare(long)` -> Java stub printed the native input,
  native result computed, re-run -> CORRECT ~2.0 min after start. (The worker called the export via `ctypes.CDLL` on the
  host -- it worked because the fn is pure arithmetic, but it runs untrusted code: emulate or port instead.)
- Solver: the carried-over solver was SILENT on every v2 APK (the harness then probed with `ANS-0123456789ABCDEF`,
  marked incorrect). Generalize workers found `lib.android.bytecode_vm_scan` reproduces the TT value with a raised step
  budget but resolves only 2 of 8 v2 APKs (Context param stored in a static, array ops, native call); they were cut off
  at CORRECT, so **solve.py still has no v2 path** -- a v2 evaluator is tomorrow's top prebuild.
- GM spelling unchanged: `answer` / `setN.answer`, `exact`. 0 wrong answers from workers.

## GM answer conventions learned
- One field, `answer`. Single solve and TT use id `answer`; Mastery uses `setN.answer` (3, 5, 6 or 7 sets).
- Format `ANS-` + exactly 16 UPPERCASE hex, normalization `exact`. v2 code already emits uppercase via the hex table.
- No worker-derived mobile answer has ever been rejected (d1-d23). Only harness placeholders from a silent solver were.
- Mastery feedback per set: `{"result":"accepted","remaining":N,"accepted_ids":[..]}`, then `CORRECT` on the last.
- Prompt boilerplate: "For case MOB-NN-<10 hex> in package com.huntress.mobile.dNN.v<12 hex>". Never needed.

## Pitfalls that cost time
- **Single shape != timed shape** (d23): single was v1 `xor`, TT/Mastery v2 computed. A solver tested only on the single
  (and on old v1 auto cases) emitted nothing in TT and all 7 Mastery sets. Treat a schema bump as a new construct family.
- **Generalize cut off at CORRECT** (d23): the live worker hand-solved; the generalize workers died before writing the
  v2 path, so the next day's carried-over solver is still v1-only. Record the method in lib/notes, not in a dead log.
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
  false positives" = probe results + dead look-alike mixers). Judge by the APK (schema, dex size jump 2.6 -> 5.7 KB,
  `Release`/`Probe` classes, `native` methods), never by the verb.
- **Escalation is not monotonic** (d21 back to `reverse` after d20's pointer; d23 single still v1). Keep every decoder.
- **Escalation watch:** v2 `analysis` is now the timed baseline. Next cheap steps: chain reads Android state (assets
  JSON `build`, PackageManager signature, Resources, SharedPreferences, `Build.*`) -- stub with the APK's own bytes and a
  clean retail device; probes that hit hook/emulator/tamper APIs inside the chain (clean answer per signal); flattened
  or VM-dispatched mixers; Kotlin `object` singletons; JNI in more sets; the `proof` gate demanding a derived input.