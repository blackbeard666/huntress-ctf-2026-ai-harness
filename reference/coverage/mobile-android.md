# mobile-android: coverage atlas (D1-D17 seen, D18+ forecast)

Scope: common Android/mobile CTF concepts mapped against what this lane has shipped and what the harness can handle.
Ground truth (see `reference/techniques/mobile-android.md`): all 17 days shipped the same ~12.7 KB fixture. The day's
THEME was flavour only (manifest `huntress.mechanic` + dex `DAY-NN:<theme>:<mechanic>`). The answer `ANS-<16 HEX>` was
always in `assets/huntress_puzzle.json` behind a rotating codec (plain/reverse/base64/xor/split/hex/caesar/native/indexed). D15
added the first real extra payload (`lib/x86_64/libarena.so` with the answer as a `.rodata` literal) and mixed-day
Mastery. D16 (JNI Boundary) TT/Mastery builds added the first REAL gate in code: `Java_<pkg>_JNIBoundary_nativeEvidence(int
len)` returns `arena_value` only if `len > 0xffff && (u16)len == 0` -- still with the literal in the asset and `.rodata`.
D17 (Name Collapse, R8-style identifier collapse) left the native track: 6-entry fixture, new per-char permutation codec
`indexed`, one renamed class `a`; the TT dex carried the real hint `follow b -> a and ignore field c` + `decoy` strings.
So "seen Dn" below means the THEME was named that day. It does NOT mean an exploit was ever needed.
The risk for D18+ is the **answer leaving the puzzle JSON** (computed by the native export / dex, nested dex, encrypted)
more than the theme. D15-D17 read as a MASVS-RESILIENCE arc (native secret -> JNI gate -> name obfuscation + decoys):
expect string encryption / reflection / control-flow obfuscation, anti-tamper (signature, checksum), root/emulator/
debugger detection, dynamic code loading, and SEVERAL `ANS-` candidates where only the one reaching `proof=` counts.
New codecs keep arriving (d7 caesar, d15 native, d17 indexed): any unknown codec must be decodable from `ANS-` alone.

Tool status (after `source bin/env.sh`; checked 2026-10-15). INSTALLED: jadx 1.5.6, apktool 3.0.3, aapt, aapt2,
apksigner, keytool, jarsigner, d2j-dex2jar (+ `tools/dex2jar/d2j-*.sh`: baksmali, decrypt-string, ...), droidasc,
androguard (CLI + py), apkInspector, rizin/rz-bin, r2/rabin2, Ghidra `analyzeHeadless`, readelf/nm/strings, hbc-decompiler/
hbc-disassembler/hbc-file-parser (hermes-dec), ilspycmd + dotnet, webcrack, js-beautify, sqlite3, 7z, binwalk, yara,
tshark, zlib-flate, openssl, adb (no device). py: lief, pyelftools, capstone, unicorn, pycryptodome, lz4, plistlib.
MISSING: blutter, reFlutter, pyxamstore, Il2CppDumper/Cpp2IL, frida/frida-tools/objection, apkid, apkleaks, bundletool,
abe (android-backup-extractor), standalone baksmali/smali, dexdump, zipalign, de4dot, ipsw/plistutil/class-dump.
Timed constraint: `solve.py` may use only stdlib + lib.* + pyzipper/pyelftools/pefile/capstone/pycryptodome/androguard,
no subprocess, <1 s per set. Prebuilt extractors must be pure python.

## Concept table

Legend: tool `[i]` = installed here, `[M]` = missing. "puzzle" = `assets/huntress_puzzle.json` (`lib.android.puzzle_candidates`).

| # | concept | status | where the answer likely hides | recognition cues | standard tool + exact command | D18+ likelihood |
|---|---|---|---|---|---|---|
| 1 | Exported Activity / implicit-export default | seen D1 | puzzle; real CTFs: `onCreate` reveals the flag when started with a magic extra | `android:exported="true"`, intent-filter w/o `exported` + targetSdk<31 | `aapt dump xmltree x.apk AndroidManifest.xml` [i]; `droidasc getmanifest x.apk` [i]; `lib.android.manifest_facts` | high: Mastery mixes old days |
| 2 | Exported Service / AIDL / Messenger | gap | `onBind`/`onStartCommand`/`handleMessage` compares + returns secret | `<service exported>`, `extends Binder`, `$Stub`, `IInterface`, `Messenger` | `jadx -d out x.apk` [i]; `droidasc findrefs x.apk type Landroid/os/Binder;` | med: next IPC theme |
| 3 | Broadcast receiver (exported, dynamic, ordered/sticky) | gap | `onReceive` action/extra check; action strings in dex | `<receiver exported>`, `registerReceiver`, `sendOrderedBroadcast`, custom `ACTION_*` | `aapt dump xmltree ...`; `jadx` grep `onReceive` | med-high: classic unused IPC theme |
| 4 | Content provider (SQLi, path traversal, FileProvider paths) | seen D6 | puzzle; real: `query()` / `openFile()`, `res/xml/*paths*.xml` | `<provider exported grantUriPermissions>`, `UriMatcher`, `<root-path>`, `../` | `apktool d -f -o out x.apk` [i]; `aapt dump xmltree x.apk res/xml/file_paths.xml` | med (mixed Mastery) |
| 5 | Custom permission weakness (normal level, typo, missing) | gap | manifest | `<permission protectionLevel="normal">`, `android:permission` on comp vs `uses-permission` | `aapt dump permissions x.apk` [i] | med |
| 6 | Task hijacking / StrandHogg | gap | manifest attrs (answer = static) | `taskAffinity`, `allowTaskReparenting="true"`, `launchMode="singleTask"` | `aapt dump xmltree ... \| grep -E 'taskAffinity\|launchMode\|Reparent'` | med |
| 7 | Tapjacking / overlay | gap | layout XML or manifest | `filterTouchesWhenObscured`, `FLAG_WINDOW_IS_OBSCURED`, `SYSTEM_ALERT_WINDOW` | `apktool d` then `grep -r filterTouches out/res` | med |
| 8 | Deep link (custom scheme, param parsing) | seen D2 | puzzle; real: `getQueryParameter` branch | `<data android:scheme=..>`, `getData()`, `getQueryParameter` | `droidasc findrefs x.apk string <scheme>` [i]; `jadx` | high (mixed) |
| 9 | App Links / autoVerify / assetlinks | gap | host + cert SHA-256 (assetlinks needs the signing fp) | `android:autoVerify="true"`, `https` scheme+host | `apksigner verify --print-certs x.apk` [i]; `keytool -printcert -jarfile x.apk` [i] | med |
| 10 | Intent redirection / nested Intent / `Intent.parseUri` | seen D3 | puzzle; real: forwarded Intent reaches a private comp | `getParcelableExtra(..Intent)`, `startActivity(`, `parseUri`, `intent://` | `jadx`; `droidasc findrefs x.apk method parseUri` | high (mixed) |
| 11 | PendingIntent (mutable / implicit base) | seen D4 | puzzle | `FLAG_MUTABLE`, `PendingIntent.getActivity` with empty Intent | `strings -a classes.dex \| grep -i pendingintent` | high (mixed) |
| 12 | Fragment injection (PreferenceActivity) | gap | `isValidFragment` returns true | `PreferenceActivity`, `:android:show_fragment` | `jadx` | low |
| 13 | WebView JS interface | seen D7 | puzzle; real: `@JavascriptInterface` getter returns secret | `addJavascriptInterface`, `@JavascriptInterface` | `jadx`; `droidasc findrefs x.apk method addJavascriptInterface` | high (mixed) |
| 14 | WebView file access / UXSS / loadUrl from extra | gap | `assets/*.html`/`*.js` holding the secret, or the URL itself | `setAllowUniversalAccessFromFileURLs(true)`, `file:///android_asset/`, `loadUrl(getIntent()` | `unzip -l x.apk 'assets/*'`; `unzip -p x.apk 'assets/*.html'` | med-high |
| 15 | WebView URL-allowlist bypass (`shouldOverrideUrlLoading`) | gap | allowlist check strings | `startsWith("https://`, `endsWith(`, `getHost()`, `loadDataWithBaseURL` | `jadx` | med |
| 16 | allowBackup / adb backup `.ab` | seen D5 | puzzle; real: `*.ab` -> tar -> `sp/*.xml`/`db/*.db` | `allowBackup="true"`, `fullBackupContent`, `dataExtractionRules`, header `ANDROID BACKUP` | `dd if=b.ab bs=24 skip=1 \| zlib-flate -uncompress \| tar x` [i]; abe [M] | med |
| 17 | SharedPreferences secrets | seen D11 | puzzle; real: `shared_prefs/*.xml` or dex default value | `getSharedPreferences`, `MODE_WORLD_READABLE`, `EncryptedSharedPreferences` | `unzip -l`; `jadx` | high (mixed) |
| 18 | SQLite / Room / Realm | seen D12 | puzzle; real: `assets/*.db` row, `rawQuery` | `SQLiteOpenHelper`, `rawQuery`, magic `SQLite format 3\0`, `.realm` | `sqlite3 f.db .dump` [i] | med |
| 19 | External storage / world-readable files | gap | path constant + file in assets | `getExternalStorageDirectory`, `requestLegacyExternalStorage`, `MODE_WORLD_*` | `jadx` grep | med |
| 20 | Logcat leakage | gap | `Log.d(tag, secret)` constant in dex | `Landroid/util/Log;`, tag strings near secret | `strings -a classes*.dex`; `jadx` grep `Log\.` | med |
| 21 | Clipboard / screenshot / keyboard cache | gap | n/a (fact question) | `ClipboardManager`, `FLAG_SECURE`, `textNoSuggestions` | `jadx`, `apktool d` | low-med |
| 22 | Hardcoded secret in strings.xml / BuildConfig | gap | `resources.arsc` string, `BuildConfig` static field | `resources.arsc` present, `BuildConfig` class, `api_key`/`secret` res names | `aapt dump --values resources x.apk \| grep -B2 ANS-` [i]; `apktool d` + `grep -r ANS- out/res`; `jadx` `BuildConfig.java` | high: cheapest escalation |
| 23 | Firebase / google-services misconfig | gap | `firebase_database_url`, `google_api_key` res or `google-services.json` | `firebaseio.com`, `AIza[0-9A-Za-z_-]{35}`, `google_app_id` | `apktool d` + grep; offline (answer = the key/URL or a JSON in assets) | med |
| 24 | Cloud/API keys (AWS, Stripe, JWT, OAuth) | gap | dex/arsc constants | `AKIA[0-9A-Z]{16}`, `sk_live_`, `eyJ` | `strings -a` + regex; apkleaks [M] | med |
| 25 | Cleartext traffic | seen D8 | puzzle | `usesCleartextTraffic="true"`, `http://` URLs | `aapt dump xmltree` | high (mixed) |
| 26 | Permissive TrustManager / HostnameVerifier | seen D9 | puzzle | `X509TrustManager`, empty `checkServerTrusted`, `ALLOW_ALL_HOSTNAME_VERIFIER` | `jadx` | high (mixed) |
| 27 | Network Security Config | seen D10 | puzzle; NSC itself (domain/pin values) | `networkSecurityConfig`, `cleartextTrafficPermitted`, `<certificates src="user">` | `aapt dump xmltree x.apk res/xml/network_security_config.xml` [i] | high (mixed) |
| 28 | Certificate pinning (OkHttp / NSC pin-set) | gap | pin `sha256/<b64>` constants; pinned host | `CertificatePinner`, `<pin-set>`, `sha256/` | `jadx`; frida [M] (no device: static only) | med-high: follows D8-D10 |
| 29 | Bundled keystore / cert with hardcoded password | gap | `res/raw/*.bks\|*.p12\|*.pem`, password in dex | `KeyStore.getInstance("BKS"\|"PKCS12")`, `.load(..,"pw".toCharArray())` | `keytool -list -v -keystore f.p12 -storepass PW` [i]; `openssl pkcs12 -in f.p12 -nodes -passin pass:PW` [i] | med |
| 30 | Shipped traffic capture (pcap/HAR) | gap (d8 prompt hinted, none shipped) | HTTP body/header | `*.pcap`, `*.har` entries | `tshark -r f.pcap -Y http -T fields -e http.file_data` [i] | low |
| 31 | Keystore misuse | seen D13 | puzzle | `AndroidKeyStore`, `KeyGenParameterSpec`, no `setUserAuthenticationRequired` | `jadx` | med (mixed) |
| 32 | Predictable RNG / nonce / seed | seen D14 | puzzle; real: `new Random(seed)` -> regenerate in py | `java/util/Random`, `setSeed`, `currentTimeMillis` | `jadx`; reimplement LCG `(x*0x5DEECE66D+0xB) mod 2^48` | med (mixed) |
| 33 | Static AES key/IV, ECB, `SecretKeySpec` | gap | ciphertext in asset/JSON + key/IV dex strings | `SecretKeySpec`, `AES/ECB/PKCS5Padding`, `IvParameterSpec`, 16/24/32-char constants | `jadx`; py `Crypto.Cipher.AES` [i] | high: the obvious "real crypto" codec |
| 34 | Weak hash / KDF / short PIN | gap | hash constant -> brute force | `MessageDigest.getInstance("MD5"\|"SHA-1")`, `PBKDF2WithHmacSHA1`, low iteration count | `jadx`; py `hashlib` brute | med |
| 35 | String encryption helper (XOR arrays in `<clinit>`) | gap (codec xor D4/D11 is a cousin) | byte/char arrays + key in dex | `fill-array-data`, one `a(String)`/`decrypt` called everywhere | `jadx` (prints arrays); `tools/dex2jar/d2j-decrypt-string.sh` [i]; androguard | high |
| 36 | Puzzle codec escalation (compound, zlib, rot47, vigenere, permutation) | partly seen D1-D17 (D17 `indexed`) | puzzle `data` with a new codec name | codec name not in `decode_payload` table; int list (`order`) beside `data` | `indexed`: `r[order[i]] = data[i]` (not in lib yet); `lib.android.decode_any` (depth 3; no zlib/rot47/atbash/vigenere); `lib.decode.peel` | high: new codecs D7, D15, D17 |
| 37 | JNI `Java_*` / exported native secret | seen D15, D16 | `.rodata` literal (D15) or computed in export | `lib/<abi>/*.so`, `System.loadLibrary`, `native` methods | `strings -a lib/*/*.so \| grep ANS-`; `nm -D --defined-only f.so`; `rz-bin -zz f.so` [i] | high |
| 38 | Answer split across dex + .so (real split) | gap (D15 prompt said split; it was not) | fragments: dex const-strings + `.so` rodata/xor | `ANS-` prefix alone, 8-hex fragments, two exports (`*_secret`, `*_day`) | `strings -a classes.dex lib/*/*.so \| grep -E '^[0-9A-F]{4,16}$'`; `jadx` concat order | high: D15 prompt foreshadows it |
| 39 | RegisterNatives / `JNI_OnLoad` dynamic registration | gap | fn pointer table in `.data.rel.ro` | no `Java_*` exports, `JNI_OnLoad` export, `RegisterNatives` | `rizin -A -qc 'afl; pdf @ sym.JNI_OnLoad' f.so` [i]; `analyzeHeadless` [i] | high: natural next step after D16's static `Java_*` export |
| 40 | Obfuscated / stripped .so (xor strings, OLLVM), multi-ABI divergence | gap | runtime-decoded stack buffer | stripped, xor loops, many `lib/<abi>/` dirs | `rizin -A`; py unicorn emulate [i]; compare `strings` per ABI | med |
| 41 | Anti-debug (ptrace, TracerPid) | gap | flag behind the check | `ptrace`, `TracerPid`, `/proc/self/status` | `strings`; static bypass by reading the gated branch | med |
| 42 | DexClassLoader / InMemoryDexClassLoader / asset dex | gap | `assets/*.dex\|*.jar\|*.apk\|*.bin` (maybe xor/zip) | `DexClassLoader`, `InMemoryDexClassLoader`, `dex\n03` magic inside an asset | `unzip -o -d a x.apk 'assets/*'`; `jadx -d out a/assets/payload.dex` [i] | high: classic, fits the progression |
| 43 | Reflection / `Class.forName` obfuscation | gap | class/method names as encoded strings | `Class.forName`, `getDeclaredMethod`, `invoke` | `jadx` | med |
| 44 | Packers (Jiagu, Bangcle, SecNeo, DexProtector) | gap | encrypted dex in assets, stub app | `libjiagu*.so`, `libsecexe.so`, `libDexHelper.so`, `StubApplication` | apkid [M]; `unzip -l` + `rz-bin -zz` | low: too heavy for a 12 KB fixture |
| 45 | R8/ProGuard renaming | seen D17 (one class `<pkg>/a`; answer still in the asset) | renamed `a`/`b` static fields or getters; `mapping.txt` if shipped | 1-letter class names, dex hint `follow b -> a`, `identifier_obfuscation` tag | `jadx --deobf -d out x.apk` [i]; `droidasc getclass x.apk <pkg>.a` [i] | high (mixed Mastery; TT may need the chain) |
| 46 | DexGuard/Allatori commercial string encryption | gap | encrypted strings + decrypt stub | `o.`/`ʼ` unicode class names, huge static arrays | `jadx`; emulate the decrypt method in py | low-med |
| 47 | Root detection (su, Magisk, RootBeer, test-keys) | gap | flag gated by `isRooted()` | `/system/xbin/su`, `RootBeer`, `test-keys`, `magisk` | `jadx`; read gated branch statically | med-high: standard MASVS-RESILIENCE theme |
| 48 | Emulator / Frida / Xposed detection | gap | same, gated | `goldfish`, `ranchu`, `ro.kernel.qemu`, `frida`, `27042`, `XposedBridge`, `/proc/self/maps` | `strings -a`; frida [M] | med-high |
| 49 | Signature / integrity / installer check | gap | expected cert digest constant | `GET_SIGNATURES`, `signingInfo`, `getInstallerPackageName`, `IntegrityManager` | `apksigner verify --print-certs -v x.apk` [i]; `keytool -printcert -jarfile x.apk` [i] | med |
| 50 | Debuggable / testOnly / debug paths | gap | debug-only branch constant | `android:debuggable="true"`, `testOnly`, `BuildConfig.DEBUG` | `aapt dump badging x.apk` [i] | med |
| 51 | Smali patching / repackaging | gap | value computed at runtime (derive statically instead) | patch hint in prompt | `apktool d`, edit smali, `apktool b -o p.apk out`, `apksigner sign --ks k.jks p.apk` [i]; zipalign [M] | low: no device |
| 52 | Flutter (Dart AOT `libapp.so`) | gap | Dart object pool strings in `libapp.so`; debug build: `flutter_assets/kernel_blob.bin` | `libflutter.so`, `libapp.so`, `assets/flutter_assets/` | `strings -a lib/*/libapp.so \| grep ANS-`; blutter [M]; reFlutter [M] | med-low |
| 53 | React Native plain JS bundle | gap | `assets/index.android.bundle` | `libreactnativejni.so`, `__BUNDLE_START_TIME__`, `__d(function` | `webcrack` [i]; `js-beautify` [i] | med |
| 54 | React Native Hermes bytecode | gap | HBC string table / function bodies | bundle magic `c6 1f bc 03 c1 03 19 1f`, `libhermes.so` | `hbc-decompiler b.hbc out.js` [i]; `hbc-disassembler` [i] | med |
| 55 | Xamarin / .NET MAUI | gap | `assemblies/*.dll`, `assemblies.blob` (XALZ lz4), .NET8 `libassemblies.*.blob.so` | `libmonodroid.so`, `libxamarin-app.so`, `XALZ` / `XABA` magic | pyxamstore [M] -> `ilspycmd f.dll` [i] | low-med |
| 56 | Unity IL2CPP / Mono | gap | `global-metadata.dat` string literals; Mono `Assembly-CSharp.dll` | `libil2cpp.so`, `libunity.so`, metadata magic `AF 1B B1 FA` | Il2CppDumper [M]; Mono: `ilspycmd` [i]; `strings` on metadata | low |
| 57 | Cordova / Ionic / Capacitor / Kotlin MP | gap | `assets/www/*.js`, `assets/public/`, plain dex (KMP) | `cordova.js`, `capacitor.config.json`, `kotlin/` | `unzip -p` + `webcrack` [i]; `jadx` (KMP) | med (Cordova), low (KMP) |
| 58 | Split APK / XAPK / APKS / AAB | gap | inside `base.apk` or a config split; AAB manifest is protobuf | `manifest.json` (XAPK), `toc.pb` (APKS), `BundleConfig.pb`, `base/dex/` (AAB) | `unzip -l`; bundletool [M] (`bundletool dump manifest --bundle x.aab`) | med |
| 59 | Signature schemes v1-v4 / cert fields | gap (v1 `META-INF/FIXTURE.RSA` every day) | signer DN fields, v2 block | `META-INF/*.RSA`, `APK Sig Block 42` | `apksigner verify -v --print-certs x.apk` [i]; `openssl pkcs7 -inform DER -in CERT.RSA -print_certs` [i] | med |
| 60 | Manifest tricks (malformed AXML, anti-apktool, odd meta-data) | partly seen (meta-data `huntress.mechanic` daily) | `<meta-data android:value>` | apktool/jadx fail but aapt works | `aapt dump xmltree`; `apkInspector` [i]; androguard | med-high: meta-data is a natural hiding spot |
| 61 | resources.arsc tricks (UTF-16 pools, renamed res) | gap (d10 shipped an arsc) | string resource value | arsc present; `raw_entry_scan` misses UTF-16 | `aapt dump --values resources x.apk`; `aapt2 dump resources x.apk` [i] | high |
| 62 | ZIP-level tricks (dup entries, fake encryption bit, data after EOCD, stored polyglot) | gap | hidden entry/trailer | `unzip -l` vs `7z l` mismatch, warnings | `7z l x.apk` [i]; `apkInspector` [i]; `binwalk x.apk` [i] | med |
| 63 | Mixed-day Mastery bundle | seen D15-D17 | per-set puzzle (different codec per set) | `day` field / `DAY-NN` tag differ per set; D16: question case ref != APK case ref | `puzzle_candidates` per APK, never branch on today or the case ref | high |
| 64 | iOS IPA (if the lane ever goes iOS) | gap | `Info.plist`, Mach-O `__cstring`, embedded plist/json | `Payload/*.app/`, Mach-O `cffaedfe`, `CFBundleIdentifier` | py `plistlib` [i]; `rz-bin -zz Payload/X.app/X` [i]; lief [i]; ipsw/class-dump [M] | low |
| 65 | JNI type/length mismatch (int -> u16/jshort narrowing, signed/unsigned, jsize vs strlen, jbyteArray NUL) | seen D16 | `.rodata` value returned by the gated `Java_*` export (D16, also in the asset) | `Java_*_native*` + a `*_accepts`/`check` helper, `cmp $0xffff`, `movzwl`/`cwtl`, 16-bit `cmp %ax`; dex `native` method with `I`/`[B` arg | `nm -D --defined-only f.so`; `objdump -d --no-show-raw-insn f.so` [i]; bypass input = smallest int passing the check (D16: 65536) | high (mixed Mastery repeats it) |
| 67 | Decoy insertion (several plausible values; code picks one) | seen D17 (TT hint `ignore field c`, strings `decoy`/`telemetry`) | the field/const that flows into `proof=` in ChallengeActivity; decoys in other renamed fields | >1 `ANS-` hit across asset/dex/.so, words `decoy`/`telemetry`/`ignore`, hint strings naming fields | `jadx --deobf`, trace `StringBuilder.append` before `proof=`; androguard xrefs to the field | high: prompt said "decoy insertion" yet one value shipped |
| 66 | Native anti-debug / root / emulator gate inside the `.so` | gap | value behind `ptrace`/`/proc/self/status`/`su` checks in a native export | imports `ptrace`, `fopen`, `access`, strings `TracerPid`, `/system/bin/su`, `frida` | `rz-bin -i f.so`; `objdump -d`; read the passing branch statically | med-high: native track continues |
| 68 | Identifier collision (names differing only by case / homoglyph / zero-width char; overloaded R8 names) | gap (D17 "Name Collapse" pun) | the class/field the real call targets, not its look-alike | classes `a` and `A`, `\u0430` Cyrillic, `\u200b` in names, same name with different descriptors | androguard: list classes/fields whose `casefold()`/NFKC/strip-zero-width forms collide; jadx --deobf renames them | med |
| 69 | Answer composed in code, not stored (`"ANS-"` + `String.format("%016X", long)`, `Long.toHexString`, digest prefix) | gap | const-wide / int pair / MessageDigest output appended after an `"ANS-"` const | `ANS-` or `ANS` const-string with no 16-hex neighbour; `toHexString`/`format`/`MessageDigest` in the same method | `lib.android.dex_eval_scan` [i]; else read the method and compute in python | med-high |

## Recognition cues (worker quick-reference)

```
0. Always first: python3 -c "from lib.android import extract_answer as e;print(e('x.apk'))"   # puzzle->zip->dex->apktool/jadx
   If it prints ANS-... and the prompt is the usual "backend answer code": submit. Do NOT chase 127.0.0.1:19090.
1. unzip -l x.apk   -> map the entries:
   assets/huntress_puzzle.json      puzzle codec; lib.android.puzzle_candidates / decode_any; new name -> data[:4] vs "ANS-"
                                    int list beside data (D17 `indexed`, D5 `split`): r[order[i]] = data[i]; else gather
   lib/<abi>/*.so                   strings -a | grep ANS- ; nm -D --defined-only ; no Java_* -> JNI_OnLoad/RegisterNatives
                                    Java_*_native*(int) + *_accepts helper (D16 gate): objdump -d it; the value it returns
                                    is the answer (D16: &arena_value = the .rodata ANS- literal; bypass len 65536)
   lib/*/libapp.so + libflutter.so  Flutter: strings libapp.so; flutter_assets/kernel_blob.bin (debug = source text)
   assets/index.android.bundle      RN: head -c8 | xxd; c61fbc03 = Hermes -> hbc-decompiler; else webcrack/js-beautify
   assemblies/*.dll|*.blob, libmonodroid.so   Xamarin: XALZ = lz4 per-dll; then ilspycmd f.dll
   libil2cpp.so + global-metadata.dat         Unity IL2CPP: strings global-metadata.dat | grep ANS- ; Managed/*.dll -> ilspycmd
   assets/www/, cordova.js, capacitor.config  hybrid JS: grep -r in assets/www
   assets/*.dex|*.jar|*.apk|*.zip|*.bin       dynamic code loading: unzip it, jadx it, re-run extract_answer on it
   libjiagu/libsecexe/libDexHelper.so          packer: payload is the encrypted asset; static decrypt or give up early
   res/xml/network_security_config.xml        NSC: aapt dump xmltree x.apk res/xml/network_security_config.xml
   resources.arsc                   aapt dump --values resources x.apk | grep -iE 'ans-|secret|key|flag|token'
   *.db / shared_prefs/*.xml / *.ab sqlite3 f.db .dump ; .ab: dd bs=24 skip=1 | zlib-flate -uncompress | tar x
   res/raw/*.bks|*.p12|*.pem        keystore: password is a dex string; keytool -list -v -storepass PW
   google-services.json / firebase  key/URL itself may be the answer
   base.apk + split_config.*.apk / manifest.json / toc.pb / BundleConfig.pb   split/XAPK/APKS/AAB: unzip inner, recurse
   Payload/*.app/                   iOS: plistlib Info.plist; rz-bin -zz the Mach-O
2. Plain-anywhere scan (incl. UTF-16 the zip scan misses):
   for f in $(unzip -Z1 x.apk); do unzip -p x.apk "$f" | strings -a -el | grep -H --label="$f" ANS-; done
   7z l x.apk vs unzip -l x.apk differ -> zip tricks (dup entry / trailing data): binwalk x.apk
3. Manifest (fast): aapt dump xmltree x.apk AndroidManifest.xml | grep -E \
   'exported|scheme|host|autoVerify|permission|debuggable|allowBackup|usesCleartext|networkSecurity|taskAffinity|launchMode|meta-data'
   meta-data value= is a hiding spot (huntress.mechanic lives there). droidasc getmanifest x.apk prints the XML.
4. Dex triage: strings -a classes*.dex | grep -E 'DAY-|CODEC|ANS-|^[0-9A-F]{8,16}$' then map API hits to themes:
   DexClassLoader/InMemoryDexClassLoader -> asset dex     SecretKeySpec/AES/Cipher/IvParameterSpec -> static key decrypt
   loadLibrary/RegisterNatives -> .so                     java/util/Random/setSeed/currentTimeMillis -> regenerate RNG
   MessageDigest/PBKDF2 -> hash brute                     addJavascriptInterface/loadUrl/file:///android_asset -> assets html/js
   Binder/$Stub/Messenger/onReceive -> IPC handler        CertificatePinner/sha256/ -> pins in code or NSC
   su/magisk/RootBeer/goldfish/frida/TracerPid -> flag sits in the gated branch: read it, never run it
   Class.forName/getDeclaredMethod -> decode names        BuildConfig / R$string -> arsc / BuildConfig.java
   KeyStore.getInstance("BKS"|"PKCS12") -> res/raw keystore + password string
5. Read code only after 1-4: droidasc findrefs x.apk string <hit>; droidasc getclass x.apk <cls>; jadx -d w/jadx x.apk
   (add --deobf for 1-2 letter class names). Strings split across constants: rebuild order from the method body.
   R8/decoys (D17): hint strings like "follow b -> a and ignore field c" name the chain; >1 ANS- candidate -> keep
   the one appended before `proof=` in ChallengeActivity, never the first regex hit.
   lib scanners for code-side answers (not in extract_answer): renamed_chain_scan, proof_flow_scan, dex_eval_scan,
   reflection_scan, mapping_restore_scan, signing_block_scan, zip_structure_scan  (all lib.android, take apk path)
6. Native, if no literal: rizin -A -qc 'iE; izz~ANS; afl' f.so ; pdf @ sym.Java_... ; xor loops -> py capstone/unicorn.
7. Validate: candidate must fullmatch ^ANS-[0-9A-F]{16}$ (uppercase). Two sources (asset + .so) agreeing = submit.
8. Mastery: each set can be a different day's fixture; decode every APK on its own; loop over all answer_ids (3 or 5).
```

## Readiness gaps

Priority 1 = plausible within days. "prebuild" = pure-python extractor in `lib/android.py` style that races in
`solve.py`. "tool" = install. "note" = doc/prompt change. Already built (prebuild-state ok, dropped from the list):
utf16-string-pool-scan, nested-container-recurse, dex-native-split-assembly, static-key-cipher-decode,
decode-any-chain-peel, native-so-emulate-export, dex-string-decrypt-arrays, asset-db-prefs-backup,
identity-derived-key, hermes-hbc-string-table, cert-and-signing-facts, il2cpp-metadata-literals,
jni-export-return-trace, jni-gate-bypass-input, registernatives-table, native-stack-string, multi-abi-arm-native,
dex-native-call-args, native-gated-branch-read, dex-gated-branch-consts, webview-asset-js-scan,
cert-pin-and-nsc-facts, puzzle-indexed-and-perm-fields, proof-flow-candidate-ranking, r8-renamed-chain-follow,
dalvik-mini-interpreter, permutation-transposition-family, reflection-name-resolve, proguard-mapping-restore,
apk-signing-block-payload, zip-structure-anomaly-scan, integrity-derived-key.

```json
[
  {"id": "ans-prefix-numeric-compose", "concept": "answer composed in code from an `ANS-` prefix + numeric constants (row 69)", "priority": 1, "action": "prebuild", "detail": "Pure python over androguard: for every method holding const-string `ANS-`/`ANS`, collect const-wide/const ints, fill-array-data longs and int pairs in the same method and emit `ANS-` + format(v & 0xFFFFFFFFFFFFFFFF, '016X'), hi/lo int pairs (`%08X%08X`), and Long.toHexString forms (lowercase -> upper, zero-pad). Also cover `\"ANS-\" + Integer.toHexString(a) + Integer.toHexString(b)`. Return regex-valid candidates for proof_flow ranking; never submit the first one blind."},
  {"id": "custom-alphabet-decode", "concept": "puzzle/dex data in a custom base64/base32/base58 alphabet carried in the dex (rows 35, 36)", "priority": 1, "action": "prebuild", "detail": "Obfuscation days favour shuffled alphabets. Pure python: take every dex/asset string of length 32, 58, 64 or 65 with all-unique printable chars as a candidate alphabet; translate the puzzle `data` (and other base-n-shaped strings) to the standard alphabet and decode; also reversed alphabet and alphabet as a key-schedule for a substitution cipher (map data chars through alphabet<->sorted). Keep only `^ANS-[0-9A-F]{16}$` hits. Wire into puzzle_candidates' unknown-codec branch."},
  {"id": "asset-cipher-dex-loader", "concept": "dynamic code loading of an ENCRYPTED asset dex (rows 42, 44; MASVS-RESILIENCE arc D15-D17)", "priority": 1, "action": "prebuild", "detail": "nested_scan handles plain or single-byte-xor dex/zip only. Extend: when the dex references DexClassLoader/InMemoryDexClassLoader/PathClassLoader or an asset is high-entropy, try repeating-key XOR, RC4, AES-ECB/CBC/GCM (pycryptodome) with keys/IVs from dex strings, byte arrays and the package name / signing-cert digest (integrity_facts), plus zlib/gzip after decrypt; accept output starting `dex\\n0` / `PK\\x03\\x04`, then recurse extract_answer + renamed_chain_scan + dex_eval_scan on it."},
  {"id": "native-init-array-decrypt", "concept": "native strings decrypted at load time by .init_array constructors (OLLVM `.datadiv_decode*`) (rows 46, 66)", "priority": 1, "action": "prebuild", "detail": "native_so_emulate covers exported functions only. Pure python: parse DT_INIT_ARRAY / .init_array with pyelftools, map the .so in unicorn (x86_64 + arm64), run each constructor with stubbed imports (return 0) and a step cap, then scan the writable .data/.bss for ANS- tokens and the strings referenced by the Java_* export. Also handle `datadiv_decode<N>` symbols by name and JNI_OnLoad run before RegisterNatives."},
  {"id": "worker-cue-inline", "concept": "unseen-theme routing", "priority": 1, "action": "note", "detail": "Inline the 'Recognition cues' block above into the mobile worker prompt (skills/huntress-ctf mobile skill) so an unseen container (Flutter/RN/Xamarin/asset dex) is routed in 1-2 turns; add step 2's UTF-16 scan to triage.md pre-extraction."},
  {"id": "identifier-collision-resolve", "concept": "names differing only by case / homoglyph / zero-width char, and overloaded R8 names (row 68)", "priority": 2, "action": "prebuild", "detail": "'Name Collapse' pun points at name collisions next. androguard: report class/field/method names whose casefold / NFKC / zero-width-stripped / confusable-skeleton forms collide, and same-name members distinguished only by descriptor. Resolve every invoke/sget by FULL descriptor (never by simple name) when following the proof= flow; feed the true target into renamed_chain_candidates. On disk (jadx/apktool on case-insensitive FS) collisions overwrite files: read classes from the dex, not the decompiled tree."},
  {"id": "resource-id-const-resolve", "concept": "answer in resources.arsc reached via R.string id constants in code (rows 22, 61)", "priority": 2, "action": "prebuild", "detail": "string_pool_scan finds literal pool strings but not WHICH one the code uses. Pure python: parse resources.arsc package/type/entry tables to map 0x7fXXYYYY -> (type, name, value incl. per-config variants), then find const 0x7f... in ChallengeActivity / the proof= method (getString/getText/getStringArray, getIdentifier(name,'string',pkg)) and return the resolved values -- the decoy-aware way to pick among several arsc ANS- strings."},
  {"id": "messagedigest-derived-answer", "concept": "answer = hex prefix of a digest/HMAC over app-visible inputs (rows 33, 69)", "priority": 2, "action": "prebuild", "detail": "When a method calls MessageDigest.getInstance/Mac.getInstance and appends hex to `ANS-`: collect its const-string inputs plus package name, case id from the manifest/dex, signing-cert digest; compute MD5/SHA-1/SHA-256/SHA-512 and HMAC with dex-string keys over each input and simple concatenations (cap ~2k combos, <0.3 s); emit `ANS-` + first/last 16 hex upper. Only candidates, ranked by proof_flow; no brute force beyond values present in the APK."},
  {"id": "v1-manifest-digest-verify", "concept": "anti-tamper: which entry was modified (MANIFEST.MF / .SF digests vs actual bytes) (rows 49, 59)", "priority": 2, "action": "prebuild", "detail": "Pure python: parse META-INF/MANIFEST.MF (Name:/SHA-256-Digest:/SHA1-Digest: blocks, 72-byte continuation lines), recompute every entry digest, and check .SF digest-manifest and per-section digests; report mismatching / unlisted entries. A tampered entry is where the anti-tamper story hides the real answer (scan it first) and answers 'which file was modified' questions. Also surface v2/v3 signer cert digest vs v1 cert (signing_certs)."},
  {"id": "dex-slack-and-header-anomaly", "concept": "data hidden inside the dex outside its declared structure (rows 51, 62)", "priority": 2, "action": "prebuild", "detail": "Pure python dex parser: header file_size vs real length (appended payload), adler32/sha1 header checks, bytes between map items not covered by map_list, string_ids not referenced by any code (orphan strings incl. decoys), unused/duplicate class_defs, and multiple dex magic versions (035/039/041). Return orphan/appended bytes to decode_any and nested_scan; flag strings referenced only from never-invoked methods as decoy-likely for proof_flow ranking."},
  {"id": "pyxamstore", "concept": "Xamarin assemblies.blob / XALZ (row 55)", "priority": 2, "action": "tool", "detail": "pip: `uv pip install --python .venv/bin/python pyxamstore` (or github jakev/pyxamstore). Then `pyxamstore unpack -d assemblies/` and ilspycmd. Also small prebuild: XALZ header (magic, index, size) + lz4.block decompress (lz4 in venv)."},
  {"id": "apkid", "concept": "packer / obfuscator / anti-VM identification (rows 44-48)", "priority": 2, "action": "tool", "detail": "pip: `uv pip install --python .venv/bin/python apkid` (needs yara-python, already OK). `apkid -j x.apk` names packers, obfuscators and anti-debug in one call: a fast routing cue for an unseen theme."},
  {"id": "bundletool", "concept": "AAB / APKS packaging (row 58)", "priority": 2, "action": "tool", "detail": "github release jar google/bundletool (bundletool-all-1.17.x.jar) into tools/bundletool + bin shim. `bundletool dump manifest --bundle x.aab`, `bundletool build-apks --mode=universal`. AAB manifests are protobuf, so aapt dump xmltree fails on them."},
  {"id": "aab-proto-manifest-parse", "concept": "AAB / APKS with protobuf manifests (row 58)", "priority": 3, "action": "prebuild", "detail": "bundletool is missing and aapt cannot read proto XML. Pure python minimal protobuf decoder for base/manifest/AndroidManifest.xml (XmlNode/XmlElement/XmlAttribute from aapt2 Resources.proto: field numbers only, no generated code) to extract package, components, meta-data values; recurse extract_answer over base/dex/*.dex and base/assets/."},
  {"id": "il2cppdumper", "concept": "Unity IL2CPP (row 56)", "priority": 3, "action": "tool", "detail": "github release Perfare/Il2CppDumper (or SamboyCoding/Cpp2IL) into tools/; run with bin/dotnet. Only if a Unity fixture ever ships."},
  {"id": "blutter", "concept": "Flutter Dart AOT (row 52)", "priority": 3, "action": "tool", "detail": "github worawit/blutter (python3 blutter.py <lib dir> <out>; builds per Dart version with cmake/ninja + fetches the Dart SDK, slow first run; arm64 only). Alt: pip reflutter (needs repack + device: low value). Plain strings on libapp.so cover literal answers."},
  {"id": "abe", "concept": "encrypted Android backup (row 16)", "priority": 3, "action": "tool", "detail": "github release nelenkov/android-backup-extractor (abe.jar): `java -jar abe.jar unpack b.ab b.tar [pw]`. Needed only for encrypted .ab (PBKDF2+AES); unencrypted is zlib-flate."},
  {"id": "frida-tools", "concept": "dynamic instrumentation / root and frida checks (rows 47, 48)", "priority": 3, "action": "tool", "detail": "pip frida-tools / objection. Low value: no Android device or emulator here (adb present, no target), and every answer so far was static. Keep the rule: read the gated branch statically."},
  {"id": "standalone-baksmali", "concept": "smali-level reading / patching (row 51)", "priority": 3, "action": "tool", "detail": "Link tools/dex2jar/d2j-baksmali.sh + d2j-smali.sh into bin/ (already on disk), or github google/smali release. apktool d already emits smali, so cosmetic."},
  {"id": "ios-ipa-readiness", "concept": "iOS IPA (row 64)", "priority": 3, "action": "note", "detail": "Lane is named mobile-android; if an .ipa ever ships: unzip Payload/, plistlib for Info.plist and binary plists, rz-bin -zz / lief for Mach-O strings, ipsw (github blacktop/ipsw release) for class-dump. Nothing to prebuild now."}
]
```
