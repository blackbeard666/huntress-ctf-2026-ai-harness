# mobile-android — technique log (days 1-30; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations"): solvers derive structure and degrade
  per field. One question, `answer` = `ANS-` + 16 uppercase hex.
- Fixture: ~12.7 KB, 6 entries (`AndroidManifest.xml`, `assets/huntress_puzzle.json`, `classes.dex`, `META-INF/FIXTURE-.
  {SF,RSA}`, `MANIFEST.MF`). Extras: d10 NSC xml + `resources.arsc`; d15-d16 `lib/x86_64/libarena.so`; d20
  `assets/payload.dex`; d21 `debuggable="true"`. **d26 `*.apks`** = stored zip of `base.apk` + `feature.apk`
  (`split="arena_feature"`, `hasCode=false`) in all modes; the d26 Mastery set keeps the `.apks` (v1 d27, v2 d28).
- Daily THEME in manifest `<meta-data huntress.mechanic>` + dex (`DAY-NN:<theme>:<mechanic>` / `CONTROL` / `STRUCTURAL`):
  d1-d14 IPC/storage/network/crypto classics; `jni_secret` d15, `jni_length` d16, `identifier_obfuscation` d17,
  `string_decryption` d18, `reflective_dispatch` d19, `dynamic_dex` d20, `anti_debug` d21, `root_detection` d22,
  `hook_detection` d23, `emulator_detection` d24, `integrity_signal` d25, `split_apk` d26, `legacy_dependency` d27,
  `binary_protocol` "binary protocol framing" d28, `white_box_table` "clean-room table transformation" d29,
  `layered_protections` "composed clean-room protections" d30. Through d22 flavour only. **Since d23 TT/Mastery COMPUTE the answer in
  dex**; the theme is one pure gate fn (or a small loop) inside that chain; d26 chain READ ARTIFACT BYTES (feature split).
- Puzzle v1 (`huntress.mobile.puzzle.v1`; every single, d1-d22 + d27 TT/Mastery): answer behind a rotating `codec`
  (list below); keys re-roll; old codecs recur; NEW codecs every day d28-d30 (`packet`, `table`, `layered`), each one a
  small COMPOSITION of known steps (hex/base64 wrapper + position-keyed keystream + reverse/framing).
- **Puzzle v2** `{"schema":"huntress.mobile.puzzle.v2","day":N,"codec":"analysis","build":"<12 hex>"}`, NO `data`: answer
  = `Release.code(Context)` evaluated statically. TT + every Mastery set d23-d26 and d28-d30; ABSENT everywhere d27.
- **Mastery = MIXED-DAY bundle since d15** (5 sets d15-d21, then +1/day: 6 d22 ... 12 d28, 13 d29, 14 d30), all under today's
  prompt; old days are REGENERATED in the day's schema and since d25 RUN their real mechanic as code (d19 reflection,
  d16 native u16 gate, d14 LCG table, d15 JNI hop, d18 decrypt loop, d17 R8 `b->a`). Never yet v2: d12, d20, d27.
- `.ChallengeActivity` builds `http://127.0.0.1:19090/mobile/attempt/<id>/evidence?case_id=..&client_secret=..&proof=..`
  = the PHONE's loopback, unreachable; the static value was accepted on all 30 days.
- Single = flavour, timed = mechanic. Open every TT/Mastery APK fresh: the schema goes back and forth (d27 v1, d28 v2).
- The single's NEW v1 codec and the TT's v2 theme fn are the SAME idea in two encodings (d30: `layered` = xor `key+i` +
  reverse over bytes; TT `peelStack` = xor `4+i` + byte-reverse inside a u64). Solving the single explains the TT chain.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Puzzle schema** -- single always v1. TT + Mastery: v1 d1-d22, v2 d23-d26, v1 d27 (all 11 sets, original codecs +
  keys), v2 d28-d30 (TT + 12/12, 13/13, 14/14 sets). In a split bundle the JSON sits in `base.apk`. Rule: branch on the JSON, never on the
  day: `data` present -> codec chain; `codec=="analysis"` / no `data` / schema v2 -> evaluate `Release.code`; neither ->
  code scanners.
- **Puzzle codec (v1)** -- params re-roll per variant: xor `key` 0-255 (d4/d11/d18/d23), caesar shift (d7/d14). Keyless
  (`reverse`, `base64`, `native`, `reflection`) differ only in `data`. `indexed` (d17): `order[i]=(3+7i) mod 20` always.
  `split` (d5/d10/d24): `data:""`, 3 `parts` (lens 9/5/6) + `order [2,0,1]`, `r[order[i]]=parts[i]`; d26: an EMPTY
  `parts` slot filled first from the feature split's `huntress_feature.json {part, part_index}`. `hex` (d6/d12/d25) =
  ASCII hex. `dynamic` (d20): `data` = `assets/payload.dex`. **`packet` (d28 single)**: `data` = hex of ONE frame
  `48 41`("HA") | len u8 (20) | payload = ASCII answer | XOR checksum of all preceding bytes. Rule: decode by declared
  codec, fullmatch `^ANS-[0-9A-F]{16}$` on the PAYLOAD; entry path -> read the entry; unknown name -> `ANS-`
  known-plaintext; int list -> scatter; framed hex -> magic/len/checksum (may grow seq/nonce/multi-frame/u16/CRC).
  **Position-keyed keystream codecs** (one `key` int + index i): d29 `table` = hex -> `(b - (key + 3i)) & 255`; d30
  `layered` = base64 -> `b ^ ((key + i) & 255)` -> REVERSE the whole string. Both were decided by `data[:4]`/tail vs
  `ANS-` (reverse puts `ANS-` at the END). Rule: wrapper {hex, base64} x op {xor, sub, add} x step {0..7} x reverse
  {before, after, none}, `key` from the JSON, accept only a `^ANS-[0-9A-F]{16}$` fullmatch (unique in practice).
- **Split-bundle container (d26; Mastery d26 set on d27 v1 and d28 v2)** -- `*.apks` stored zip of `base.apk` +
  `feature.apk` (names may become `split_config.<abi|dpi|lang>.apk`). v1: JSON fragment (above). v2: base
  `Assets.readSplit("huntress_feature.bin")` walks `getApplicationInfo().splitSourceDirs` -> `ZipFile.getEntry("assets/"
  +name)` -> 16 B folded as TWO big-endian u64 (`j=(j<<8)|(b[i]&255)`). Rule: unpack all inner `PK` members; base =
  member with `huntress_puzzle.json`; serve split reads from the OTHER members. The container travels with its day.
- **Computed-chain shape (v2)** -- per build: class names (`Core`/`Guard`/`Mix`/`Util`/`Probe`/`Tab` + theme classes:
  `HookScan`, `BoardCheck`, `SealCheck`, d28 `FrameKit`/`WireState`, d29 `TableKit`/`RoundBox`/`Tab`, d30
  `LayerKit`/`PeelStack`), method names `<verb><ThemeWord><2 hex>`, seed
  `const-wide`, mixer constants, probe kinds/args/count (`s1: ((i*a+b)^c)&4095==d`, `s2: ((i^c)*a+b)&4095==d`; 3 calls
  d23-d24, 2 d25-d26, NONE d28 TT), and the theme gate + its SIGNATURE:
  `(III)I` `(a^b^c)&7` d23, `(a+b+c)%4` d24, `((a*3)^b^c)&255` d14, `((a^b)+c)&255` d10 and d08, `((a+b)^c)&255` d16,
  d28 `frame(a,b,c)=(a<<16)|(b<<8)|c`, d30 `layeredGate(a,b,c)=((a^b)+c)%31` (first non-power-of-2 modulus);
  `(II)I` d29 `tableTransform(a,b)=((a*257)^b)&255`; `(JI)J` d25 `a^(long)b` (then `long-to-int`); `(II)I` d26 `(a<<4)|b`, d18 set
  `decryptByte(b,k)=(b^k)&255`; `(I)I` d17 set `a.b(i)->a.a(i)=(7i+3)%23`; `(ZI)I` d27 stub `z ? i+1 : -1` (never called).
  Loops/extras: d14 `Tab.build` LCG `long[16]` x6 rounds; d15 `native nativeShare(long)`; d16 `native nativeShare(long,
  int len)` = 0 unless `len>0xffff && (u16)len==K` (dex passes a passing const); d19 `Class.forName(<pkg>.Maze)
  .getDeclaredMethod("m"+dispatch(k), long.class).invoke` (1 of 8 look-alikes); d18 decrypt loop over `byte[14]`, key
  `(50i+1)&255`, FNV-64 prime fold; **d28 TT `Util.session*` = 7-round STATE-MACHINE WALK** over two `int[8]` tables:
  `h ^= frame(21, val[s], round+1)*K; h=rotl(h,34); h ^= h>>>14; s = next[(s+(h&3))&7]` (order depends on the hash);
  **d29 `walkBox*`** = 8 rounds over `Tab.build` LCG `long[16]`, index = `h & 15`, `h ^= tab[idx]`, gate byte shifted into
  lane `(round&7)*8`; **d30 `peelStack*`** = per-byte `xor (4+i)` over the u64's 8 bytes, byte-REVERSE, `+ gate*K`.
  Fixed: `Release.code` = `"ANS-"` + 16 nibbles via `"0123456789ABCDEF".charAt((v>>>i)&15)` of `fin(Mix.f1(token()))^K`;
  `proof` = `Long.toHexString(token())`. Rule: INTERPRET from `Release.code` / the value reaching `proof=`; never key on
  names; unreferenced look-alike mixers / `K*` consts are decoys.
- **Answer location** -- puzzle JSON (singles; d15-d16 also `.so` `.rodata`); d20 nested asset dex; d23+ timed = dex
  computation (+ JNI d15/d16 sets, + feature-split bytes d26); d26 single = base JSON + feature fragment; d28 single =
  framed packet payload; d29/d30 singles = keystream-decoded JSON `data`. Fallbacks: v2 eval, `raw_entry_scan`, `dex_strings`, `.so` strings, `extract_answer`.
- **Mastery set mix (d15+)** -- other days' fixtures (JSON `day` / dex `DAY` / package `dNN` name the source); picks
  re-roll per attempt; last set = today's. d26: d02 d03 d06 d11 d13 d16+.so d19 d21 d25 d26.apks; d27 (all v1): d01 d04
  d07 d10+NSC d11 d14 d18 d20+payload.dex d21 d26.apks d27; d28 (all v2): d01 d04 d07 d08 d11 d14 d17 d18 d22 d24
  d26.apks d28; d29 (all v2): d01 d03 d07 d09 d10 d13 d15+.so d18 d19 d23 d24 d26.apks d29; d30 (all v2): d02 d04 d05
  d07 d09 d13 d15+.so d17 d19 d21 d23 d26.apks d29 d30 (d05 first time v2; yesterday's day already a set). d16 case ref
  did NOT match the APK. Rule: per-set, schema-agnostic; never branch on day or case ref.
- **Mastery packaging** -- `delivery N: <name>_mastery_NN.apk|.apks` (2-digit, up to `14` d30): pair by sha256, never by
  extension; ids `setN.answer` (submission dict order != set order). Loop over answer_ids.
- **Per-variant identity** -- case ref `MOB-NN-<10 hex>`, package suffix `v<12 hex>`, `client_secret`, attempt slug, v2
  `build`. None fed the answer so far (watch `build`).
- **Dex hint strings** -- v1 single: `CODEC`, `CONTROL`, `DAY-NN:<theme>:<mechanic>`, `describe`; v1 TT d17-d22/d27
  (2.68 KB): tag dropped, `STRUCTURAL` + an uncalled stub; v2 (5.1-6.5 KB): `CODEC="analysis"`, `CONTROL`, old days keep
  `describe()` (d17 v2 set has no `CONTROL`). Rule: never require `CODEC`/`DAY-NN` to decode anything.
- **Manifest flags / native libs** -- `debuggable="true"` only d21 (changed nothing). v2 `.so` (d15/d16 sets, 13.5 KB):
  `nativeShare` exports, no `ANS-` literal; mangle the JNI name from the dex `native` method and emulate it.

## Recognition cues -> first move

| You see | First move |
|---|---|
| `*.apk`, answer `ANS- + 16 uppercase hex` | `unzip -p x.apk assets/huntress_puzzle.json` (triage.md pre-extracts + prints it) |
| **`*.apks` / `.xapk` / zip of `base.apk` + `feature.apk` / `split_config.*.apk`** (d26) | unzip, `unzip -l` EVERY member; base = the one with `huntress_puzzle.json`. v1: fill empty `parts[part_index]` from the feature JSON, then scatter. v2: grep the base dex for `splitSourceDirs`/`ZipFile`/`getEntry`/`readSplit`; the chain reads `assets/<name>` from the OTHER split (d26: 16 B = 2 big-endian u64). Port the chain or javac it with a `Context` stub whose `readSplit` returns the feature bytes |
| puzzle v1 `{"codec":..,"data":..}` | decode per codec (list below); fullmatch `^ANS-[0-9A-F]{16}$` before submitting |
| **puzzle v2 `"codec":"analysis"`, no `data`** (d23-d25) | answer = `Release.code(ctx)`. First: `lib.android.puzzle_candidates` (deep Dalvik eval; d25 TT 0.76 s, 9-set Mastery 1.9 s). Manual fallback: `jadx -q -d j x.apk`; copy non-Activity sources; stub `package android.content; public class Context {}`; `Main` prints `Release.code(null)`; `javac` + `java`. Or port the ~6 static long fns to python (mask 2^64, `>>>` = logical) |
| v2 chain calls a `native` method (d15 set `nativeShare(long)`; d25 d16 set `nativeShare(long,int)` with a u16 gate) | `objdump -d -M intel lib/*/libarena.so` the export (~10-20 insns of cmp/movzx + movabs/add/xor/imul/rol), feed the dex's own int arg, port to python or unicorn-emulate. Do NOT `ctypes.CDLL` the artifact on the host |
| **puzzle v1 `"codec":"packet"`** (d28 "Protocol Reconstruction") | `bytes.fromhex(data)`: magic `48 41`, `len` byte, payload, XOR checksum of everything before it; payload = answer. Several frames / seq / nonce fields -> order by seq, drop duplicate + bad-checksum frames, then join |
| v2 chain with two `int[8]` tables + a round loop (d28 TT `session*`, gate `frame(a,b,c)=(a<<16)\|(b<<8)\|c`) | state-machine walk: next state depends on the hash (`next[(s+(h&3))&7]`) -- evaluate in order, never reorder/batch rounds. Solver handles it (TT solve 0.55 s) |
| `Probe.s1/s2/s3(a,b,c,d)` loops | 12-bit inverse search: smallest i<4096 with f(i)==d, else -1. Pure, cheap: just evaluate |
| `data` is a path (`assets/payload.dex`, d20) | `unzip -p x.apk assets/payload.dex \| strings -a \| grep ANS-`; no dex magic -> known-plaintext unwrap |
| int list next to `data` (d17 `indexed`, d5 `split`) | `order[i]` = OUTPUT slot of `data[i]`: `r[order[i]] = data[i]` |
| Unknown v1 codec name | `data` already `ANS-`? An entry name? Else `data[:4]` vs `ANS-`: constant diff = shift, constant XOR = key |
| **Unknown v1 codec + an int `key`** (d29 `table`, d30 `layered`; prompt "layered"/"composed"/"table") | unwrap hex/base64, then compare the first AND last 4 bytes with `ANS-` / `-SNA`: per-position diff growing by 1 or 3 = keystream `key + c*i` (sub or xor); match at the END = reversed. Write the 3-line decoder, fullmatch, submit (d30 by hand ~40 s) |
| `lib/<abi>/*.so` | `strings -a \| grep ANS-`, `nm -D --defined-only`; d16 gate `nativeEvidence(int)`: `objdump -d` the checker (65536) |
| Nothing decodes | `lib.android.extract_answer`, then `strings -a classes*.dex assets/* lib/*/*.so \| grep ANS-` |
| Theme stubs (d17-d22: `a`/decoy, `decryptByte`, `dispatch`, `debuggerGate`, `rootSignals`) | asset first. Code-side: `dex_eval_scan`/`reflection_scan`/`clean_device_scan`, then `proof_flow_scan` to keep the value reaching `proof=` |
| Hook/instrumentation theme (d23 `hook_detection`, prompt "real signals vs generated false positives") | v2 chain; the gate fn is pure arithmetic over probe results; look-alike `seal*`/`K*` members nobody calls are the decoys |
| Emulator / integrity themes (d24 "pinned emulator used by the solve oracle"; d25 "forge or replay a bounded challenge-owned integrity statement and explain the missing binding") | same v2 chain; gate = 1 pure fn (`emulatorScore=(a+b+c)%4`; d25 `integrityStatement(long,int)=a^b`); `KQemu*`/`sealEmu*`/`KSeal*`/`KStatement*`/`KCert*` = decoys; no Build/PackageManager/token API. Just run the solver |
| v2 chain with `Class.forName` + `getDeclaredMethod` + `Method.invoke` (d25 Mastery d19 set) | method name = `"m" + dispatch(k)` (packed-switch); invoke the named `Maze.mN(long)` only; the other 7 `mN` are decoys. Solver handles it |
| Supply-chain / reachability prompt (d27 "which generated dependency flaw is reachable from an exported mobile surface"; `legacy_dependency`) | puzzle JSON first (d27: v1 `base64` in every mode). If a real one ships: list bundled lib packages/`META-INF/*.version`/`pom.properties`/extra `classes2.dex`/`assets/*.jar`, walk from manifest-exported components (`exported=true` / intent-filter) to the lib call; only the REACHED flaw's value counts |
| Loopback `127.0.0.1:19090` | do NOT chase it: device-local. The answer is static |
| Prompt demands a live action (d8 "replay", d9 "exploit CA", d20 "signed") | still static: `unzip -l` for extra entries first |
| Mastery `delivery N: foo_mastery_0N.apk` | strip the prefix (`lib.common.find_artifact`); ids `setN.answer`; each set may be another day AND another schema |

Puzzle codecs seen (v1): `plain`, `native` (d15-d16), `reflection` (d19) = plaintext; `dynamic` (d20) = entry path;
`packet` (d28: framed hex, see Variant axes); `table` (d29: hex, `b-(key+3i)`); `layered` (d30: base64, `b^(key+i)`,
reverse); `reverse` (d2, d8, d21); `base64` (d3, d9, d13, d22, d27); `hex` (d6, d12, d25); `caesar` (d7, d14: `chr(ord(c)-key)` over EVERY
char, sign from `data[:4]`); `xor` (d4, d11, d18, d23 single: base64 + int key 0-255); `split` (d5, d10, d24, d26 with a
feature-split fragment: `parts[]` + `order[]`); `indexed` (d17). v2: `analysis` (d23-d26, d28). `lib.android.decode_payload` / `puzzle_candidates` / `decode_any`
cover v1; v2 = lib's deep Dalvik evaluator (`_DxeDeepVM`, via `puzzle_candidates`) + solve.py `_native_eval`
(unicorn JNI hop). Never submit `ans_compose_scan`'s first hit on v2 (ANS-shaped DECOYS from the dead mixers).

## Day by day

**Days 1-22** (asset held the answer; 0 wrong): d1 `plain` (~4 min lost on the loopback), d2 `reverse`, d3 `base64`,
d4 `xor`, d5 `split`, d6 `hex`, d7 NEW `caesar`, d8 `reverse`, d9 `base64`, d10 `split`+NSC, d11 `xor`, d12 `hex`, d13
`base64`, d14 `caesar`, d15 `native` (`.so` `.rodata` literal; first mixed-day Mastery), d16 `native` + TT `.so` gate
(65536), d17 NEW `indexed` (TT hint `follow b -> a and ignore field c`), d18 `xor` (TT `decryptByte`), d19 NEW
`reflection` = plaintext, d20 NEW `dynamic` (entry path -> const in `assets/payload.dex`), d21 `reverse` + debuggable,
d22 `base64` (title pun = attestation `RootOfTrust`).

**Days 23-25** (0 wrong): d23 Hook Line and Signal: TT + 7 sets = FIRST v2 (`Release.code` = hex of `fin(Mix.f1(token()))
^ K`; gate `(a^b^c)&7`; unreferenced `seal*`/`K*` = "generated false positives"); live workers hand-solved (jadx ->
python port 94.5 s; javac + `Context` stub ~2 min; `ctypes.CDLL` = sandbox violation); evaluator built overnight. d24
Emulator Alibi: gate `(a+b+c)%4`; solver 3/3. d25 Integrity Signals: first `(JI)J` gate `a^(long)b`; old days RUN their
mechanic (d19 reflection, d16 native gate); 3/3.

**Days 26-28** (0 wrong): d26 Split Decision (`split_apk`): single 49 s, TT 83 s, Mastery 88 s -- solver SILENT on the
v2 split shape (live hand-solve); `.apks` = `base.apk` + `feature.apk`; single v1 empty `parts` slot + feature JSON;
TT/set v2 gate `splitIndex(a,b)=(a<<4)|b` + `readSplit` 16 B (2 BE u64); prebuild closed it overnight. d27 Dependency
Surface: full de-escalation, v1 `base64` single + TT, all 11 sets v1, stub `exportedReachability(z,i)` never called;
3/3 on the solver; "dependency flaw" = words. d28 Protocol Reconstruction (`binary_protocol`): single v1 NEW `packet`
(hex of `HA` | u8 len | payload | XOR8; solved by hex + `ANS-` SEARCH, no frame parser), TT/12 sets v2 BACK, gate
`frame(a,b,c)` in a 7-round `int[8]` state-machine walk; "nonce" = method names only; first-time v2 d08, d17 (R8
`a.b->a.a`), d18 (real decrypt loop, FNV-64 fold); 3/3 on the solver (single 3.2 s probe, TT 3.4 s, Mastery 2.9 s).

**Day 29 — White Box Key Recovery** (`white_box_table`, "clean-room table transformation"; prompt "Recover an
equivalent key operation from challenge-owned table transformations, not a third-party protected binary"). 0 wrong, all
first try, no LLM work: single 13 s race probe (worker printed READY), TT 3.2 s (solve 0.2 s), 13-set Mastery 5.7 s
(solve 2.8 s, slowest yet). Single v1 NEW codec `table` = hex, `(b - (key + 3i)) & 255` (no real lookup table). TT/sets
v2: gate `tableTransform(a,b)=((a*257)^b)&255` in an 8-round `walkBox` over the d14-style LCG `Tab.build` `long[16]`;
decoys `sealSbox*`/`sealTable*`/`KLookup*`. "White box" = words + one table walk; no AES T-box, no asset tables.

**Day 30 — Layered Protections** (`CONTROL="layered_protections"`, STRUCTURAL "composed clean-room protections";
prompt "Unwind obfuscation, native indirection, runtime decryption, and integrity checks while proving the same backend
effect"). 0 wrong, all first try. Single CORRECT ~40 s from start by the LLM worker: the race probe was SILENT on the
new codec. TT 2.3 s (solve 0.63 s), 14-set Mastery 3.5 s (solve 1.09 s) on the solver.
- Artifact: plain 12.7 KB 6-entry fixture in all modes (Mastery set7 = d15 + `libarena.so`, set12 = d26 `.apks`).
  Single puzzle `{"codec":"layered","data":"<base64 20 B>","key":12}`: base64 -> `b ^ ((key+i)&255)` -> reverse = answer.
  Method that found it: after base64, `ANS-` appeared at neither end under a constant key; xor with `key+i` gave
  `-SNA` at the tail.
- TT (dex 5372 B): `token()=PeelStack.mixStack(LayerKit.peelStack(Util.mixLayer(seed)))`; `peelStack` = the SAME codec
  on a u64 (byte i ^= 4+i, then byte-reverse) + `layeredGate((int)j&255, (j>>>8)&255, (j>>>16)&255) * K` with gate
  `((a^b)+c)%31`; decoys `sealLayer*`/`sealPeel*`/`sealStack*`/`KPeel*`/`KLayer*`. The prompt's "native indirection,
  runtime decryption, integrity checks" were NOT in today's chain (no `native`, no cipher, no digest): words again.
- Mastery 14 sets all v2 (list under Variant axes); d05 first time v2 (pure chain). The d29 set appeared the next day.
- GM spelling unchanged (`answer` / `setN.answer`, `exact`, `ANS-` + 16 uppercase hex). No `solver/NOTES.md`, no
  `VARIANT AXIS:` lines; axes come from the cases and the APKs.

## GM answer conventions learned
- One field, `answer`. Single solve and TT use id `answer`; Mastery uses `setN.answer` (3, 5-14 sets; 14 on d30).
- Format `ANS-` + exactly 16 UPPERCASE hex, normalization `exact`. v2 code already emits uppercase via the hex table.
- No worker-derived mobile answer has ever been rejected (d1-d30). Only harness placeholders from a silent solver were.
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
- **Assuming "today's codec/schema/container" in Mastery** (d15+): sets come from older days in either schema; the
  `.apks` container follows its day.
- **New codec, generic solver silent** (d17 `indexed`, d30 `layered`): write the 5-line decoder straight away, anchored
  on `ANS-` at BOTH ends; fit `key + c*i` per position (d30 lost ~35 s vs a probe hit).
- **Trusting dex `CODEC`/`DAY-NN` strings or the question's case ref** (d16, d17-d22 TT): key on the JSON and the code.
- **split/indexed order semantics:** `r[order[i]] = parts[i]` (validated d5, d10, d24, d26); fill empty `parts` slots
  from split fragments FIRST. **caesar:** raw codepoints. **Mastery filenames** carry a literal `delivery N: ` prefix.
- **Timed windows** are start + download + submit; solve must be <1 s pure python (no jadx/javac subprocess in solve.py).
- **Prompt verbs escalate faster than the artifact** (d8 "replay", d20 "signed module", d24 "pinned emulator", d25
  "forge or replay", d27 "prove reachable", d29 "white box", d30 "native indirection, runtime decryption, integrity
  checks" = one pure fn / a codec). The NOUN can be literal (d23 "generated false positives" = dead mixers; d26 "splits" =
  a real bundle). Judge by the artifact: container, schema, dex size, real API refs (`forName`/`loadLibrary`/`ZipFile`).
- **Escalation is not monotonic** (d21 `reverse` after d20's pointer; d23-d26 singles still v1; **d27 dropped v2 from
  TT and from all 11 Mastery sets** after 4 days of v2; **d28 brought it straight back**). Keep every v1 decoder first in
  the race and the v2 evaluator always armed; never gate on "v2 now" or "v1 now".
- **`mastery/contract.json` can be a stale `start_required` body** (d30: different case refs/days than the dealt sets):
  read the attempt's own contract (case dir / start response), never the leftover file.
- **Substring luck is not a parser** (d28 `packet`): `ANS-` search over the hex-decoded frame worked only because the
  payload was plaintext. For a framed codec, parse header/length/checksum and fullmatch the PAYLOAD.
- **Escalation lives in Mastery old-day sets AND in the timed chain's I/O** (d25 d19 real reflection + d16 native gate;
  d26 chain reads artifact bytes). If the solver goes silent on ONE set, `strings -a classes.dex | grep -E 'ZipFile|
  splitSource|getAssets|DexClassLoader|forName|decrypt|getShared|SQLite|KeyStore|isDebugger'`, hand-eval that link, and
  batch-submit every set's answer in one request.
- **Escalation watch (d31 = last day):** d30's prompt listed 4 layers but the chain shipped 1 (peel) -- the
  likeliest finale is a v2 chain that REALLY composes old mechanics in one build (JNI hop + decrypt loop + reflection +
  split/asset read + integrity digest) and a v1 codec with 3+ stacked steps or a declared `layers` list. Still words
  only: d28 multi-frame seq/nonce/CRC, d27 bundled-lib reachability, d29 real white-box AES T-boxes. Mastery solve 0.4-2.8 s
  for 11-14 sets; expect 15 sets tomorrow.
