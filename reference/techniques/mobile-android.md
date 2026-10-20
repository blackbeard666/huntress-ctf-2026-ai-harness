# mobile-android — technique log (days 1-20; updated after every day)

How the lane has looked so far (observations, not guarantees):
- **Timed variants MUTATE** (organizer, Day 8: "new, dynamic variations/mutations ... new unseen effects"): nothing below is a
  guarantee for Time Trial / Mastery -- solvers derive structure and degrade per field.
- Every APK so far was the same ~12.7 KB fixture: `AndroidManifest.xml`, `assets/huntress_puzzle.json`, `classes.dex`,
  `META-INF/FIXTURE-.{SF,RSA}`, `MANIFEST.MF` (6 entries). Extras: d10 `res/xml/network_security_config.xml` +
  `resources.arsc` (8 entries); d15-d16 `lib/x86_64/libarena.so` (7 entries, ~12.8 KB); d20 `assets/payload.dex` (508 B
  plain `dex\n035`, 7 entries, APK 12768 B). One question, `answer` = `ANS-` + 16 uppercase hex.
- Each day has a new Android IPC/security THEME, written in the manifest `<meta-data android:name="huntress.mechanic">`
  and in a dex string `DAY-NN:<theme_id>:<mechanic>` (exported Activity, permissive deep link, nested Intent, mutable
  PendingIntent, allowBackup, exported ContentProvider, JS-interface origin trust, cleartext session, permissive X509
  trust manager, NSC exception, SharedPreferences credential, client-side SQLite authz, app-controlled Keystore key,
  predictable nonce d14, `jni_secret` d15, `jni_length` d16, `identifier_obfuscation` d17, `string_decryption` d18,
  `reflective_dispatch` d19, `dynamic_dex` "secondary DEX loading" d20). The theme was mostly flavour: theme stub classes
  (`WebViewBridge`, `TrustEveryone`, `NativeLibrarySecrets`, `JNIBoundary`, `EncryptedStrings`, `ReflectionMaze`,
  `LoadedLater`) were never needed, and prompts demanding a live action were still static. d16 had the first REAL gate in
  code (TT JNI export). **d20 was the first day the answer was NOT in the puzzle JSON**: `data` pointed at a second dex.
- What varied day to day was the `codec` of `huntress_puzzle.json` (plain, reverse, base64, xor+key, split, hex,
  caesar+key, then repeats; d15-d16 `native` and d19 `reflection` = theme-named, `data` already the plaintext; d17
  `indexed` = permutation; d18 back to `xor`; d20 `dynamic` = `data` is a ZIP ENTRY PATH (`assets/payload.dex`) and the
  answer is a const-string inside that entry). Keys re-roll per variant. A new codec name is possible any day: check
  `data` for `ANS-`, then for an entry name in the APK, then decode from the first 4 chars, which must become `ANS-`.
- **Since d15 Mastery is a MIXED-DAY bundle.** The 5 sets are APKs from earlier days plus one of today's (d15: 01/07/10/
  14/15; d16: 01/04/11/13/16; d17: 04/08/12/14/17; d18: 03/07/12/13/18; d19: 03/05/11/18/19; d20: d02 reverse, d09
  base64, d11 xor, d18 xor, d20 dynamic), all under today's prompt text. Solve each set from its own APK.
- In every APK, `.ChallengeActivity` builds a device-loopback URL `http://127.0.0.1:19090/mobile/attempt/<id>/evidence?
  case_id=..&client_secret=SECRET-..&proof=<answer>`. That backend is NOT reachable (it lives on the phone). The GM
  accepted the statically recovered value as the "backend evidence code" on all 20 days.
- Pattern d16-d20: the SINGLE variant carries only flavour; the TT build carries the real mechanic as dex strings (d16 JNI
  gate, d17 `follow b -> a and ignore field c` + `decoy`, d18 `decryptByte` + `STRUCTURAL`, d19 `dispatch` +
  `STRUCTURAL`, d20 `moduleContract` + `assets/payload.dex:com.huntress.arena.payload.Module` + `STRUCTURAL` -- an
  `entry:class` pointer, still no `DexClassLoader` API anywhere). Read the TT/Mastery APK's dex strings, not just the single's.

## Variant axes (what differs between the single, Time Trial and Mastery variants -- parse every value listed)
- **Puzzle codec** -- single + TT always shared the day's codec. `key` (xor byte d4, d11: 81/109/205,29,44,41,232, d16
  Mastery d04-set 21, d17 d04-set 104, d18: 20/99/233/100, d19 d18-set 44 -- full 0-255 range, never assume printable;
  caesar shift d7: 10/18/9/3/4/5/15, d14: 9/10/17,4,7,14) and split/offset parameters re-roll per variant: read them from
  `huntress_puzzle.json` every time. Keyless codecs (`reverse`, `base64`, `native`, `reflection`) differ only in `data`.
  d17 `indexed`: `order[]` was the SAME list in every variant (`order[i] = (3 + 7*i) mod 20`), only `data` changed.
  d20 `dynamic`: `data` = `assets/payload.dex` in single, TT and the Mastery d20 set (same 508 B payload layout, only the
  `ANS-` literal changed). Rule: decode by declared codec, regex-check `^ANS-[0-9A-F]{16}$`; if `data` names a zip
  entry, read that entry and run the whole candidate chain on its bytes; else `decode_any`; unknown name -> known-
  plaintext `ANS-` trick; any int-list field of len(data) -> try scatter and gather, keep the regex match.
- **Answer indirection (NEW d20)** -- the JSON value stopped being the answer: it named the entry that holds it. Inside
  `payload.dex` (class `com.huntress.arena.payload.Module`, strings `ANSWER`, `CONTRACT`, `DAY20-SIGNED-MODULE:<mechanic>`)
  the only `ANS-` literal was the answer. TT/Mastery host dex also named the class (`<entry>:<dotted class>`) and a method
  `moduleContract`. Rule: follow the pointer; if the payload ever holds >1 candidate, take the value of the field/method
  the host names (`ANSWER`, `moduleContract`), not the first regex hit; if the entry is not a valid dex/zip, unwrap it by
  magic known plaintext (`dex\n0`, `PK\x03\x04`, `\x7fELF`) before giving up.
- **Mastery set mix (d15+)** -- sets are fixtures of DIFFERENT days (codec, theme, package `dNN`, extra entries like
  `res/xml/...`, `lib/x86_64/*.so` or `assets/payload.dex`); the puzzle JSON `day` field and dex `DAY-NN:` tag name the
  source day. The day picks re-roll per attempt (the pre-start `status` preview lists different MOB-NN than the dealt
  sets); the last set was always today's, with its own manifest label (cosmetic). d16: the QUESTION's case ref/package did
  NOT match the APK's own. Rule: per-set, codec-agnostic decoding -- never branch on the day or case ref.
- **Per-variant identity** -- case ref `MOB-NN-<10 hex>`, package suffix `v<12 hex>`, `client_secret` and the loopback
  attempt slug change per variant. None of these feed the answer.
- **Mastery packaging** -- `delivery N: <name>_mastery_0N.apk` per set: pair by sha256. 3 sets (d1-d7, d10-d14) or 5
  (d8, d9, d15-d20). Loop over the contract's answer_ids, never assume a count.
- **Dex decoy/hint strings (d17-d20)** -- single dex: `CODEC`, `CONTROL`, `DAY-NN:<theme>:<mechanic>` tag, `describe`; TT
  and today's Mastery set: NO `DAY-NN` tag and no `describe`, instead the mechanic as strings (sizes single -> TT: d17
  2588 -> 2672 B, d18 2588 -> 2628, d19 2596 -> 2656, d20 2564 -> 2636). Rule: never require `CODEC`/`DAY-NN` to find or
  decode the puzzle; a TT-only string (`decryptByte`, `dispatch`, `moduleContract`) is the cue to the next escalation.
- **Answer location** -- the puzzle JSON d1-d19 (d15-d16 also in `.so` `.rodata`); d20 a nested asset dex named by the
  JSON. Fallback chain: `raw_entry_scan`, `dex_strings`, `strings -a lib/*/*.so | grep ANS-`, `extract_answer`.
- **Native lib shape (d16)** -- single shipped the 13648 B d15-style lib (no `loadLibrary`); TT/Mastery a 14128 B lib with
  `huntress_arena_length_accepts` + `Java_<pkg>_JNIBoundary_nativeEvidence`. Rule: never key on export names or lib size.

## Recognition cues -> first move

| You see | First move |
|---|---|
| `*.apk` artifact, answer_format `ANS- + 16 uppercase hex` | `unzip -l x.apk`, then `unzip -p x.apk assets/huntress_puzzle.json`. triage.md pre-extracts it to `work/extracted/` and prints the JSON |
| puzzle JSON `{"codec":..,"data":..}` | decode per codec (table below). Check the result fullmatches `^ANS-[0-9A-F]{16}$` before you submit |
| `data` is a path (`assets/payload.dex`, codec `dynamic`, d20) | `unzip -p x.apk assets/payload.dex \| strings -a \| grep ANS-` (d20: plain const in class `...payload.Module`). Not a dex magic -> known-plaintext unwrap, then recurse |
| extra `assets/*.dex\|*.jar\|*.zip\|*.bin` (d20) | secondary-code-loading theme: inspect it like `classes.dex`; host strings `<entry>:<class>` + `moduleContract` name the target |
| int list next to `data` (d17 `indexed`, d5 `split`) | `order[i]` is the OUTPUT slot of `data[i]`: `r[order[i]] = data[i]`. Tell: `A`,`N`,`S`,`-` sit where `order` has 0..3 |
| Codec name not in the table (d7 `caesar`, d15 `native`, d17 `indexed`, d19 `reflection`, d20 `dynamic`) | `data` already `ANS-`? (d15, d19). An entry name? (d20). Else `data[:4]` vs `ANS-`: constant ord diff = shift, constant XOR = xor key |
| `lib/<abi>/*.so` (d15-d16 `libarena.so`, ~14 KB, not stripped) | `strings -a lib/*/*.so \| grep ANS-`, `nm -D --defined-only`; only if no literal, route to binary-re (the `Java_*` export) |
| Native GATE (d16 `Java_*_nativeEvidence(int)` -> `*_length_accepts`) | the gate only decides whether the `.rodata` literal is returned. Bypass input if ever asked: `objdump -d` the checker (d16: 65536) |
| No puzzle JSON, or nothing decodes to `ANS-` | `lib.android.extract_answer` (zip scan, dex strings incl. multidex, apktool/jadx), then `strings -a classes*.dex assets/* lib/*/*.so \| grep ANS-` |
| Need theme, component, scheme, exported flags | `droidasc getmanifest x.apk`; `aapt dump xmltree x.apk AndroidManifest.xml`; `lib.android.manifest_facts(apk)` |
| 1-letter classes, hint "follow b -> a and ignore field c", `decoy` (d17) | asset first. If the answer leaves it: `jadx --deobf`, follow the chain the hint names; prefer the value that flows into `proof=` |
| `EncryptedStrings`/`decryptByte` (d18), `ReflectionMaze`/`dispatch` (d19) | asset first. Code-side: `dex_eval_scan` / `reflection_scan`, then `proof_flow_scan` to pick the value that reaches `proof=` |
| Handler logic (URL, extras, constants) | `droidasc findrefs x.apk string <scheme or URL>`, `droidasc getclass x.apk <pkg>.ChallengeActivity`; `jadx -d work/jadx x.apk` |
| Loopback `127.0.0.1:19090` in the code | do NOT chase it: device-local. The answer is static |
| Prompt demands a live action ("replay the session" d8, "exploit a CA" d9, "challenge-signed" d20) | still static: `unzip -l` for pcap/HAR/cert/extra dex first. d20's "signed" module had no verify code; the v1 `MANIFEST.MF` merely lists its digest |
| Backup theme with a real `.ab` file (not seen) | 24-byte header + zlib: `dd bs=24 skip=1 \| zlib-flate -uncompress \| tar x` |
| Mastery `delivery N: foo_mastery_0N.apk` | strip the prefix (`lib.common.find_artifact`). Ids `setN.answer`; each set may be another day's fixture |

Puzzle codecs seen (`schema: huntress.mobile.puzzle.v1`):
- `plain`, `native` (d15-d16, duplicated in the `.so`), `reflection` (d19): `data` is the answer.
- `dynamic` (d20): `data` = zip entry path; read the entry, `ANS-` literal inside the dex (`puzzle_candidates` yields the
  path string itself, so the solver's `raw_entry_scan` fallback found it -- follow the pointer explicitly).
- `reverse`; `base64` (d3, d9, d13); `hex` (d6, d12).
- `caesar` (d7, d14): `{data, key:int}`, `chr(ord(c) - key)` over EVERY char (digits and `-` too, `KX]7` key 10 -> `ANS-`);
  a letters-only ROT is wrong. Derive the sign from `data[:4]` vs `ANS-`.
- `xor` (d4, d11, d18): base64 data, XOR every byte with int `key` (0-255).
- `split` (d5, d10): `parts[]` + `order[]`, `order[i]` = OUTPUT SLOT of `parts[i]`. Try both readings, keep the `ANS-` one.
- `indexed` (d17): 20 chars + `order[20]`, `r[order[i]] = data[i]` (`permutation_candidates` tries scatter + gather).
- `lib.android.decode_payload` / `puzzle_candidates(apk)` / `decode_any` (base32, rot13, `lib.decode.peel`) cover these.
  Code-side scanners (call yourself; not in `extract_answer`): `renamed_chain_scan`, `proof_flow_scan`, `dex_eval_scan`,
  `reflection_scan`, `mapping_restore_scan`, `signing_block_scan`, `zip_structure_scan`, `integrity_key_scan`.

## Day by day

**Days 1-6** (same 6-entry fixture, all first try): d1 Exported Trust `plain` (~5.4 min, ~4 min lost probing
`127.0.0.1:19090`); d2 Deep Link Drift `reverse` (33 s); d3 Intent Injection `base64` (18 s); d4 Pending Intent Relay
`xor` (77 s); d5 Backup Spill `split` -- `order[i]` = output slot (27 s); d6 Provider Paths `hex` (~3 min, 2.3 min lost on
the loopback).

**Days 7-15** (theme stubs never needed; 0 wrong, TT/Mastery 0.8-3.5 s in-window): d7 WebView Bridge new `caesar`; d8
Cleartext Session `reverse`; d9 Trust Everyone `base64`; d10 Network Config Split `split` (8-entry + NSC); d11 Local
Secrets `xor`; d12 SQLite Assumptions `hex`; d13 Keystore Misuse `base64`; d14 Predictable Crypto `caesar` (json-load the
`\\`/`<` escapes). d15 Native Library Secrets: first `libarena.so` (answer literal in `.rodata`), codec `native` =
plaintext; first MIXED-DAY Mastery.

**Days 16-19** (asset held the answer; 0 wrong; carried-over solver CORRECT in ~2-25 s): d16 JNI Boundary, `native`; TT
`.so` added the `nativeEvidence(int)` gate (65536). d17 Name Collapse, NEW `indexed` (race probe silent, duel worker added
the decoder -> ~24.5 s); TT hint `follow b -> a and ignore field c`. d18 Encrypted Strings, `xor` (3rd time); TT
`decryptByte`. d19 Reflection Maze, NEW `reflection` = plaintext; no reflection API in any dex; TT `dispatch`.

**Day 20 — Loaded Later** (manifest `huntress.mechanic`=`secondary DEX loading`, dex `DAY-20:dynamic_dex:secondary DEX
loading`, class `LoadedLater`, deep link `huntress20://loaded-later/unlock`; prompt "Analyze a challenge-signed secondary
DEX and recover the module contract.")
- Artifact: 7-entry APK (12768 B): the usual fixture + `assets/payload.dex` (508 B, plain `dex\n035`, listed with a
  SHA-256 in the v1 `MANIFEST.MF` like every entry). Puzzle `{"codec":"dynamic","data":"assets/payload.dex"}` -- a
  POINTER. The payload dex = one class `com.huntress.arena.payload.Module` with strings `ANSWER`, `CONTRACT`,
  `DAY20-SIGNED-MODULE:secondary DEX loading` and the `ANS-` literal. Host dex had no `DexClassLoader`/`loadClass`/
  signature/digest code in any variant: "challenge-signed" and "module contract" were narrative.
- TT + today's Mastery set: host dex 2636 B, `DAY-20` tag dropped, adds `STRUCTURAL`, `moduleContract` and
  `assets/payload.dex:com.huntress.arena.payload.Module` (entry:class pointer). Payload unchanged in shape.
- Key insight: first day the answer LEFT the JSON value; it sat one hop away, still as a plain literal. `strings -a` on
  the extracted payload (triage pre-extracts `assets/`) showed it in one command. The carried-over solver's `answer()`
  returned nothing (`puzzle_candidates` yields the path string), the `raw_entry_scan` fallback found the literal.
- Time: race probe CORRECT (probe 1.74 s, ~8.4 s after server start 13:00:09.98Z -> 13:00:18.34Z), no LLM turn needed.
  TT in-window 3.06 s (solve 0.99 s); Mastery 5 sets (d02 reverse, d09 base64, d11 xor key 41, d18 xor key 100, d20
  dynamic) in-window 5.19 s (solve 0.53 s). Timed runs reported `no_clock: true` (window null, as on d19). All first
  try, 0 wrong. GM spelling: same `answer` / `setN.answer`, `exact`.

## GM answer conventions learned
- One field, `answer`. Single solve and TT use id `answer`; Mastery uses `setN.answer` (3 or 5 sets), one APK per set.
- Format is `ANS-` + exactly 16 UPPERCASE hex, normalization `exact`. Uppercase the hex after decoding, no whitespace.
- No mobile answer has ever been rejected (zero wrong submissions on days 1-20). The GM accepts the statically recovered
  value as the "backend evidence code" even though the prompt says "Submit only the exact backend answer code".
- Mastery feedback is per set: `{"result":"accepted","remaining":N}` after each set, then `CORRECT` on the last. An
  empty submit after the deadline returns `expired`.
- Prompt boilerplate: "For case MOB-NN-<10 hex> in package com.huntress.mobile.dNN.v<12 hex>". In Mastery the text is
  today's and the case ref may not match the APK (d16). Neither was ever needed for the answer.

## Pitfalls that cost time
- **Chasing the loopback backend** was the only recurring time sink: ~4 min (d1), ~30 s (d4), ~2.3 min (d6).
  `127.0.0.1:19090` is the phone's own loopback. If a static value matches the answer_format, submit it.
- **Taking `data` at face value** (d20): `data` was an entry path, not a value. Never submit or "decode" a string that
  names a zip entry; open the entry. Always fullmatch the ANS regex on the final value.
- **Assuming "today's codec" in Mastery** (d15+): sets come from older days with different codecs and extra entries.
- **Reaching for Ghidra on a native-lib theme** (d15-d16): the `.so` is ~14 KB, unstripped, the answer a literal. Use
  `strings`/`nm`, then `objdump -d` of the one `Java_*` export. Same for d20's payload: `strings` before `jadx`.
- **Trusting the question's case ref in Mastery** (d16): it can name a different day/case than the APK it points at.
- **New codec, generic solver silent** (d17 `indexed`, ~20 s lost): when the JSON has an unknown codec, write the
  5-line decoder straight away (anchor on `ANS-`); do not wait on lib or decompile anything.
- **Trusting dex `CODEC`/`DAY-NN` strings** (d17-d20 TT): the TT dex drops the tag. Key the decoder on the JSON's fields.
- **split/indexed order semantics:** two plausible readings exist. Validate against the answer regex instead of guessing.
- **caesar codec:** shift over raw codepoints, not the alphabet; json-load (escapes `<`/`>`), never regex the raw text.
- **Mastery filenames** carry a literal `delivery N: ` prefix. A naive path lookup fails.
- **Short timed windows** are dominated by start + download + submit; solve is <1 s. No decompiling in-window: the
  solver runs stdlib + lib.* only, no jadx subprocess.
- **Prompt wording escalates, the artifact did not** (d8 "replay the session", d9 "exploit a challenge CA", d12 "prove
  server-side impact", d15 "split configuration", d16 "type or length assumption", d18 "strings that reach
  security-sensitive APIs", d19 "reflective dispatch across generated equivalent call graphs", d20 "challenge-signed
  secondary DEX ... module contract"): judge by what the APK contains (extra entries, `Random`/`Cipher`/`forName`/
  `DexClassLoader`/`MessageDigest` refs in `strings -a classes.dex`), not by the verb.
- **Harness, not GM:** a re-start can clobber `single_solve/start.json`; check `hctf status` before re-solving.
- **Escalation watch:** d20 moved the answer one hop (JSON -> nested dex). Next cheap steps: the payload encrypted /
  XOR'd / zipped (unwrap by magic known plaintext, key from host dex), several payloads where only the one whose digest
  matches a pinned hash ("challenge-signed") is loaded, >1 `ANS-` in the payload with the host naming the real field/
  method (`moduleContract`), class shadowing between host and payload, or a stage-2 loader. If several candidates
  appear, take the one the code actually returns into `proof=` (`proof_flow_scan`), never the first regex hit.
