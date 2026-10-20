# mobile-android: coverage atlas (D1-D19 seen, D20+ forecast)

Scope: common Android/mobile CTF concepts mapped against what this lane has shipped and what the harness can handle.
Ground truth (see `reference/techniques/mobile-android.md`): all 19 days shipped the same ~12.7 KB fixture. The day's
THEME was flavour only (manifest `huntress.mechanic` + dex `DAY-NN:<theme>:<mechanic>`). The answer `ANS-<16 HEX>` was
always in `assets/huntress_puzzle.json` behind a rotating codec (plain/reverse/base64/xor/split/hex/caesar/native/indexed/
reflection). D15
added the first real extra payload (`lib/x86_64/libarena.so` with the answer as a `.rodata` literal) and mixed-day
Mastery. D16 (JNI Boundary) TT/Mastery builds added the first REAL gate in code: `Java_<pkg>_JNIBoundary_nativeEvidence(int
len)` returns `arena_value` only if `len > 0xffff && (u16)len == 0` -- still with the literal in the asset and `.rodata`.
D17 (Name Collapse, R8-style identifier collapse) left the native track: 6-entry fixture, new per-char permutation codec
`indexed`, one renamed class `a`; the TT dex carried the real hint `follow b -> a and ignore field c` + `decoy` strings.
D18 (Encrypted Strings, `string_decryption` "runtime string decryption"): 6-entry fixture, codec `xor` again (b64 + 1-byte
key); single dex had no cipher code, the TT/Mastery dex added class `EncryptedStrings` method `decryptByte` + `STRUCTURAL`.
D19 (Reflection Maze, `reflective_dispatch` "reflective secret dispatch"; prompt "Reconstruct reflective dispatch across
generated equivalent call graphs"): 6-entry fixture, NEW codec name `reflection` whose `data` is the plaintext answer;
class `ReflectionMaze`, but NO reflection API in any dex; TT/Mastery dex only added `dispatch` + `STRUCTURAL` strings.
So "seen Dn" below means the THEME was named that day. It does NOT mean an exploit was ever needed.
The risk for D20+ is the **answer leaving the puzzle JSON** (computed by the native export / dex, nested dex, encrypted)
more than the theme. D15-D19 read as a MASVS-RESILIENCE / obfuscation arc (native secret -> JNI gate -> name obfuscation +
decoys -> string encryption -> reflection): next expect control-flow flattening / switch dispatchers / opaque predicates,
dynamic proxies / MethodHandles / invoke-custom, dynamic code loading, a tiny custom bytecode VM, anti-tamper (signature,
checksum), root/emulator/debugger/Frida detection, and SEVERAL `ANS-` candidates where only the one reaching `proof=`
counts. New codecs keep arriving (d7 caesar, d15 native, d17 indexed, d19 reflection) and old ones recur (d18 xor): any
unknown codec must be decodable from `ANS-` alone -- and first check whether `data` already IS the answer (d15, d19).

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

| # | concept | status | where the answer likely hides | recognition cues | standard tool + exact command | D19+ likelihood |
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
| 35 | String encryption helper (XOR arrays in `<clinit>`) | seen D18 (theme only: answer = asset `xor`; TT dex `EncryptedStrings.decryptByte`) | byte/char arrays + key in dex | `fill-array-data`, one `a(String)`/`decrypt` called everywhere | `jadx` (prints arrays); `tools/dex2jar/d2j-decrypt-string.sh` [i]; androguard | high |
| 36 | Puzzle codec escalation (compound, zlib, rot47, vigenere, permutation) | partly seen D1-D19 (D17 `indexed`; D18 reused `xor`; D19 `reflection` = plaintext) | puzzle `data` with a new codec name | codec name not in `decode_payload` table; int list (`order`) beside `data` | `indexed`: `r[order[i]] = data[i]` (`permutation_candidates`); `lib.android.decode_any` (depth 3; no zlib/rot47/atbash/vigenere); `lib.decode.peel` | high: new codecs D7, D15, D17 |
| 37 | JNI `Java_*` / exported native secret | seen D15, D16 | `.rodata` literal (D15) or computed in export | `lib/<abi>/*.so`, `System.loadLibrary`, `native` methods | `strings -a lib/*/*.so \| grep ANS-`; `nm -D --defined-only f.so`; `rz-bin -zz f.so` [i] | high |
| 38 | Answer split across dex + .so (real split) | gap (D15 prompt said split; it was not) | fragments: dex const-strings + `.so` rodata/xor | `ANS-` prefix alone, 8-hex fragments, two exports (`*_secret`, `*_day`) | `strings -a classes.dex lib/*/*.so \| grep -E '^[0-9A-F]{4,16}$'`; `jadx` concat order | high: D15 prompt foreshadows it |
| 39 | RegisterNatives / `JNI_OnLoad` dynamic registration | gap | fn pointer table in `.data.rel.ro` | no `Java_*` exports, `JNI_OnLoad` export, `RegisterNatives` | `rizin -A -qc 'afl; pdf @ sym.JNI_OnLoad' f.so` [i]; `analyzeHeadless` [i] | high: natural next step after D16's static `Java_*` export |
| 40 | Obfuscated / stripped .so (xor strings, OLLVM), multi-ABI divergence | gap | runtime-decoded stack buffer | stripped, xor loops, many `lib/<abi>/` dirs | `rizin -A`; py unicorn emulate [i]; compare `strings` per ABI | med |
| 41 | Anti-debug (ptrace, TracerPid) | gap | flag behind the check | `ptrace`, `TracerPid`, `/proc/self/status` | `strings`; static bypass by reading the gated branch | med |
| 42 | DexClassLoader / InMemoryDexClassLoader / asset dex | gap | `assets/*.dex\|*.jar\|*.apk\|*.bin` (maybe xor/zip) | `DexClassLoader`, `InMemoryDexClassLoader`, `dex\n03` magic inside an asset | `unzip -o -d a x.apk 'assets/*'`; `jadx -d out a/assets/payload.dex` [i] | high: classic, fits the progression |
| 43 | Reflection / `Class.forName` obfuscation | seen D19 (theme only: codec `reflection` = plaintext; no reflection API in dex; TT strings `dispatch`/`STRUCTURAL`) | class/method names as encoded strings; target picked by a dispatch key | `Class.forName`, `getDeclaredMethod`, `Method.invoke`, `Field.get`, `setAccessible` | `lib.android.reflection_scan(apk)` [i]; `jadx` | high (mixed Mastery); code-side version still unseen |
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
| 63 | Mixed-day Mastery bundle | seen D15-D19 | per-set puzzle (different codec per set) | `day` field / `DAY-NN` tag differ per set; D16: question case ref != APK case ref | `puzzle_candidates` per APK, never branch on today or the case ref | high |
| 64 | iOS IPA (if the lane ever goes iOS) | gap | `Info.plist`, Mach-O `__cstring`, embedded plist/json | `Payload/*.app/`, Mach-O `cffaedfe`, `CFBundleIdentifier` | py `plistlib` [i]; `rz-bin -zz Payload/X.app/X` [i]; lief [i]; ipsw/class-dump [M] | low |
| 65 | JNI type/length mismatch (int -> u16/jshort narrowing, signed/unsigned, jsize vs strlen, jbyteArray NUL) | seen D16 | `.rodata` value returned by the gated `Java_*` export (D16, also in the asset) | `Java_*_native*` + a `*_accepts`/`check` helper, `cmp $0xffff`, `movzwl`/`cwtl`, 16-bit `cmp %ax`; dex `native` method with `I`/`[B` arg | `nm -D --defined-only f.so`; `objdump -d --no-show-raw-insn f.so` [i]; bypass input = smallest int passing the check (D16: 65536) | high (mixed Mastery repeats it) |
| 67 | Decoy insertion (several plausible values; code picks one) | seen D17 (TT hint `ignore field c`, strings `decoy`/`telemetry`) | the field/const that flows into `proof=` in ChallengeActivity; decoys in other renamed fields | >1 `ANS-` hit across asset/dex/.so, words `decoy`/`telemetry`/`ignore`, hint strings naming fields | `jadx --deobf`, trace `StringBuilder.append` before `proof=`; androguard xrefs to the field | high: prompt said "decoy insertion" yet one value shipped |
| 66 | Native anti-debug / root / emulator gate inside the `.so` | gap | value behind `ptrace`/`/proc/self/status`/`su` checks in a native export | imports `ptrace`, `fopen`, `access`, strings `TracerPid`, `/system/bin/su`, `frida` | `rz-bin -i f.so`; `objdump -d`; read the passing branch statically | med-high: native track continues |
| 68 | Identifier collision (names differing only by case / homoglyph / zero-width char; overloaded R8 names) | gap (D17 "Name Collapse" pun) | the class/field the real call targets, not its look-alike | classes `a` and `A`, `\u0430` Cyrillic, `\u200b` in names, same name with different descriptors | androguard: list classes/fields whose `casefold()`/NFKC/strip-zero-width forms collide; jadx --deobf renames them | med |
| 69 | Answer composed in code, not stored (`"ANS-"` + `String.format("%016X", long)`, `Long.toHexString`, digest prefix) | gap | const-wide / int pair / MessageDigest output appended after an `"ANS-"` const | `ANS-` or `ANS` const-string with no 16-hex neighbour; `toHexString`/`format`/`MessageDigest` in the same method | `lib.android.dex_eval_scan` [i]; else read the method and compute in python | med-high |
| 70 | Rolling / position-keyed XOR string decryptor (`b ^ k ^ i`, `k + i`, key array cycled, previous-byte chaining, LCG keystream) | gap (D18 TT `decryptByte`) | puzzle `data` or dex byte arrays under a per-index key | method taking `(B, I)`/`(I)` returning `B`/`C`, `xor-int`, `add-int/lit8` on the loop index, `rem-int` by key length | `jadx` the helper; py: solve the params from `ANS-` known plaintext, then decrypt | high: next step after D18's single-byte xor |
| 71 | Known open-source string obfuscators (StringFog, Paranoid, obfuscapk EncryptStrings, Allatori-style) | gap | encrypted literal + library decrypt call | `com/github/megatronking/stringfog`, `StringFog.decrypt`, `io/michaelrocks/paranoid`, `Deobfuscator$`, obfuscapk `DecryptString`, AES-ECB with a fixed key | `jadx`; py re-implementation of the known algorithm | med-high |
| 72 | Opaque predicates / dead-branch decoys | gap | the `ANS-` value on the reachable branch only | `if` on `x*(x+1) % 2`, constant-folded comparisons, unreachable `const-string ANS-` | `jadx` + reason about the predicate; `dex_eval_scan` executes the real path | med-high: pairs with D17 decoys |
| 73 | Java serialized object / Parcel blob in assets | gap | `TC_STRING` fields inside `AC ED 00 05` stream | asset magic `aced0005`, `ObjectInputStream`, `readObject`, `Parcel.unmarshall` | py: minimal serialization stream parser; `strings -a` | med (MASVS-CODE) |
| 74 | JWT / session token in app (alg none, HS256 with dex key) | gap | token claim, or the HMAC key | `eyJ` strings, `Authorization: Bearer`, `HS256` | py: b64url-decode header/payload; verify HMAC with dex-string keys | med (MASVS-AUTH unseen) |
| 75 | Protobuf / gRPC asset without schema | gap | LEN-field strings in a `.pb`/`.bin` asset | `com/google/protobuf`, `GeneratedMessageLite`, asset with varint-tag bytes | py generic wire decoder (lib has the AAB one) | med-low |
| 76 | SQLCipher / encrypted asset DB | gap | rows of an encrypted `assets/*.db` | `net/sqlcipher`, `libsqlcipher.so`, db without `SQLite format 3` header, password string | py: PBKDF2-HMAC-SHA512 + AES-256-CBC per page (pycryptodome), then sqlite3 | low-med |
| 77 | Reflective dispatch table (string-keyed `Map<String,Method>`, string `switch` -> `hashCode()` lookupswitch, key from deep link/extra/asset) | gap (D19 title/prompt; TT string `dispatch`) | the handler selected by the key the app actually passes (deep-link path/query, manifest meta-data, asset field) | `HashMap.put` of `Method`/`Class` objects, `sparse-switch` on `String.hashCode()` + `equals`, `getQueryParameter` feeding `forName` | `reflection_scan` [i] for the names; then the key -> handler map by hand / `dispatch-key-resolve` prebuild | high: D19 TT hint |
| 78 | Generated equivalent call graphs (many look-alike generated classes/methods, one wired) | gap (D19 prompt "generated equivalent call graphs") | the value from the chain reachable from `ChallengeActivity`/`proof=`; siblings are decoys with valid-looking `ANS-` | N near-identical classes `Route01..NN`/`Node*`/`a..z` with the same signatures, each returning an `ANS-`-shaped value | call graph from the entry point incl. reflective edges; `proof_flow_scan` [i] | high |
| 79 | Control-flow flattening / switch dispatcher state machine | gap | value assembled across `while(true){switch(state)}` cases | one huge method with `packed-switch` in a loop, a state int reassigned in every case | `jadx` (shows the loop); emulate with `dex_eval_scan` [i] if it supports switch + loops | high: next RESILIENCE step |
| 80 | Dynamic proxy / MethodHandle / invoke-custom / lambdas | gap | target method behind `Proxy.newProxyInstance` InvocationHandler or `MethodHandles.Lookup.findStatic` | `java/lang/reflect/Proxy`, `InvocationHandler`, `MethodHandles$Lookup`, `invoke-polymorphic`/`invoke-custom` (dex 038+), `LambdaMetafactory` | `jadx`; androguard opcodes 0xfa-0xfd | med-high: "dispatch" without `forName` |
| 81 | Custom bytecode VM (virtualised method) | gap | byte-array program run by an in-dex interpreter; output = answer | `[B` program const + loop with `packed-switch` on `program[pc]`, `pc` increments | `jadx`; reimplement the opcode table in py / run it in `dex_eval_scan` | med |
| 82 | JNI reflection callback (native `FindClass`/`GetStaticMethodID`/`CallStaticObjectMethod` into Java) | gap | Java method named by `.rodata` strings in the `.so`, called from native | `.so` strings like `com/huntress/...`, `(Ljava/lang/String;)Ljava/lang/String;`; imports via JNIEnv vtable offsets | `strings -a f.so`; `rizin -A`; resolve the named Java method in the dex | med: merges native + reflection tracks |

## Recognition cues (worker quick-reference)

```
0. Always first: python3 -c "from lib.android import extract_answer as e;print(e('x.apk'))"   # puzzle->zip->dex->apktool/jadx
   If it prints ANS-... and the prompt is the usual "backend answer code": submit. Do NOT chase 127.0.0.1:19090.
1. unzip -l x.apk   -> map the entries:
   assets/huntress_puzzle.json      puzzle codec; data already ANS-? done (D15 native, D19 reflection); new name -> data[:4] vs "ANS-"
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
   Class.forName/getDeclaredMethod -> reflection_scan     BuildConfig / R$string -> arsc / BuildConfig.java
   Proxy/InvocationHandler/MethodHandles/invoke-custom -> resolve the real target; packed-switch in a loop -> flattened CFG
   KeyStore.getInstance("BKS"|"PKCS12") -> res/raw keystore + password string
5. Read code only after 1-4: droidasc findrefs x.apk string <hit>; droidasc getclass x.apk <cls>; jadx -d w/jadx x.apk
   (add --deobf for 1-2 letter class names). Strings split across constants: rebuild order from the method body.
   String decryptors (D18 TT `EncryptedStrings.decryptByte`): dex_eval_scan, else jadx the helper, take the ARGS from
   each call site, re-implement in py; unknown key/rolling scheme -> solve it from the ANS- known plaintext.
   R8/decoys (D17): hint strings like "follow b -> a and ignore field c" name the chain; >1 ANS- candidate -> keep
   the one appended before `proof=` in ChallengeActivity, never the first regex hit. Reflection/dispatch (D19 theme):
   names may be encoded or picked by a key from the deep link/asset; evaluate only the invoked target, not its twins.
   lib scanners for code-side answers (not in extract_answer): renamed_chain_scan, proof_flow_scan, dex_eval_scan,
   reflection_scan, mapping_restore_scan, signing_block_scan, zip_structure_scan  (all lib.android, take apk path)
6. Native, if no literal: rizin -A -qc 'iE; izz~ANS; afl' f.so ; pdf @ sym.Java_... ; xor loops -> py capstone/unicorn.
7. Validate: candidate must fullmatch ^ANS-[0-9A-F]{16}$ (uppercase). Two sources (asset + .so) agreeing = submit.
8. Mastery: each set can be a different day's fixture; decode every APK on its own; loop over all answer_ids (3 or 5).
```

## Readiness gaps

Priority 1 = plausible within ~3 days. "prebuild" = pure-python extractor in `lib/android.py` style that races in
`solve.py`. "tool" = install. "note" = doc/prompt change. Already built (prebuild-state ok, dropped from the list):
utf16-string-pool-scan, nested-container-recurse, dex-native-split-assembly, static-key-cipher-decode,
decode-any-chain-peel, native-so-emulate-export, dex-string-decrypt-arrays, asset-db-prefs-backup,
identity-derived-key, hermes-hbc-string-table, cert-and-signing-facts, il2cpp-metadata-literals,
jni-export-return-trace, jni-gate-bypass-input, registernatives-table, native-stack-string, multi-abi-arm-native,
dex-native-call-args, native-gated-branch-read, dex-gated-branch-consts, webview-asset-js-scan,
cert-pin-and-nsc-facts, puzzle-indexed-and-perm-fields, proof-flow-candidate-ranking, r8-renamed-chain-follow,
dalvik-mini-interpreter, permutation-transposition-family, reflection-name-resolve, proguard-mapping-restore,
apk-signing-block-payload, zip-structure-anomaly-scan, integrity-derived-key, ans-prefix-numeric-compose,
custom-alphabet-decode, asset-cipher-dex-loader, native-init-array-decrypt, resource-id-const-resolve,
messagedigest-derived-answer, v1-manifest-digest-verify, dex-slack-and-header-anomaly, aab-proto-manifest-parse,
rolling-xor-keystream-family, decrypt-call-site-args-eval, known-string-obfuscator-signatures,
identifier-collision-resolve, opaque-predicate-dead-branch, java-serialized-object-parse, jwt-token-decode-verify,
protobuf-asset-wire-decode, sqlcipher-asset-decrypt.

```json
[
  {"id": "dispatch-key-resolve", "concept": "reflective dispatch tables keyed by a runtime string (row 77; D19 TT `dispatch`)", "priority": 1, "action": "prebuild", "detail": "D19's TT dex added `dispatch` with no reflection code yet; the code-side version picks a handler by key. Pure python over the dex (androguard or the mini interpreter): recover key -> target maps from (a) `HashMap.put(const-string, Method|Class|lambda|const-string class name)` in <clinit>/<init>, (b) Java string-switch (`String.hashCode()` -> sparse-switch -> `equals(const)` -> case block), (c) arrays of class-name strings indexed by an int. Resolve the KEY the app actually supplies: deep-link path segment / `getQueryParameter` name from the manifest intent-filter (scheme/host/pathPrefix), manifest meta-data, puzzle JSON fields (`route`, `key`, `entry`, `dispatch`), const-strings passed at the call site. Run only the selected target via dex_eval_scan/reflection_scan and return its ANS- value first, other targets as demoted candidates."},
  {"id": "entry-reachable-callgraph-rank", "concept": "generated equivalent call graphs: N look-alike classes, one wired (row 78)", "priority": 1, "action": "prebuild", "detail": "D19 prompt: 'reconstruct reflective dispatch across generated equivalent call graphs'. Build a dex call graph from ChallengeActivity/MainActivity onCreate (and the manifest's launch/deep-link activities) including reflective edges (forName/getDeclaredMethod names resolved by reflection_scan, const-class, Proxy targets) and virtual dispatch to concrete subclasses. Group structurally equivalent methods (same opcode sequence modulo constants/names) and report, per group, which member is reachable from the entry and which value reaches `proof=`. Feed as a strong rank signal to proof_flow_scan; unreachable twins with ANS- literals are decoys."},
  {"id": "flattened-cfg-switch-eval", "concept": "control-flow flattening / while(true)-switch(state) dispatchers (row 79)", "priority": 1, "action": "prebuild", "detail": "Next RESILIENCE step after reflection. Ensure the dex mini interpreter executes packed-switch/sparse-switch, backward gotos and int state updates with a step budget (~200k insns), so a flattened method that appends answer chars across cases (StringBuilder / char[] writes) runs to completion; when the state seed comes from a param, try the const at each call site. Also a static unflattener fallback: from the dispatcher's state transitions (each case ends with const state; goto head) recover the case order from the initial state and concatenate the const-strings/chars in that order. Regex the output for ANS-."},
  {"id": "proxy-methodhandle-invokecustom", "concept": "dynamic proxies, MethodHandles, invoke-polymorphic/invoke-custom, lambdas (row 80)", "priority": 1, "action": "prebuild", "detail": "'Dispatch' without Class.forName: extend reflection resolution to java.lang.reflect.Proxy.newProxyInstance(handler) -> route interface calls into InvocationHandler.invoke with the Method name const; MethodHandles.Lookup.findStatic/findVirtual/findGetter(Class, name, MethodType) -> resolve target by name + descriptor; dex 038+ invoke-custom call sites (call_site_ids -> bootstrap LambdaMetafactory -> implementation method handle) and invoke-polymorphic MethodHandle.invoke/invokeExact; Kotlin/D8 desugared lambdas (`-$$Lambda$`/`$ExternalSyntheticLambda` classes) -> their single target method. Pure python dex parsing (call_site_ids/method_handles sections) + dex_eval_scan."},
  {"id": "clean-device-env-stubs", "concept": "root/emulator/debugger/Frida checks gating the answer, evaluated as a clean device (rows 41, 47, 48, 66)", "priority": 2, "action": "prebuild", "detail": "MASVS-RESILIENCE detection days are the obvious remainder of the arc. Give dex_eval_scan a 'clean physical device' environment model: File.exists/canRead on su/magisk/busybox/frida paths -> false, Build.TAGS -> 'release-keys', Build.FINGERPRINT/MODEL/HARDWARE/PRODUCT -> a Pixel profile (not goldfish/ranchu/sdk/generic), Debug.isDebuggerConnected/waitingForDebugger -> false, ApplicationInfo.flags FLAG_DEBUGGABLE clear, System.getProperty('ro.kernel.qemu') -> null, /proc/self/status TracerPid 0, /proc/self/maps without frida/xposed, Socket connect 27042 -> refused, PackageManager.getPackageInfo(magisk/xposed pkgs) -> NameNotFound. Run each method whose body references those APIs/strings and report the ANS- value on the clean path."},
  {"id": "tiny-bytecode-vm-interpret", "concept": "virtualised method: custom bytecode program + in-dex interpreter (row 81)", "priority": 2, "action": "prebuild", "detail": "Detect a method with a [B/[I program (fill-array-data or base64/hex const) and a loop dispatching on program[pc] via packed-switch. First try running it in dex_eval_scan with the step budget; else lift: map each case to an op (push const, xor, add, sub, rot, load/store reg, emit char, jump) by pattern-matching its Dalvik ops, then interpret the program in python. Output candidates to the ANS regex."},
  {"id": "jni-reflection-callback", "concept": "native code calling back into Java by name (FindClass/GetStaticMethodID) (row 82)", "priority": 2, "action": "prebuild", "detail": "Merges the D15-D16 native track with D19 reflection. In each .so: collect .rodata strings shaped like JNI class paths (`com/huntress/...`, `java/lang/...`) and method descriptors `(...)L...;`, pair them by proximity/xref (capstone over the Java_* / JNI_OnLoad bodies: lea of string -> call via JNIEnv vtable offsets FindClass 0x30, GetStaticMethodID 0x388, CallStaticObjectMethod 0x390, GetMethodID 0x108, NewStringUTF 0x538), resolve the named Java method in the dex and run it with dex_eval_scan; also return NewStringUTF literal args. x86_64 + arm64."},
  {"id": "kotlin-metadata-names-and-coroutines", "concept": "Kotlin @Metadata original names + coroutine state machines", "priority": 2, "action": "prebuild", "detail": "If the fixture moves to Kotlin: decode `kotlin/Metadata` annotations (d1 = protobuf-encoded strings with the JvmProtoBuf string table, d2 = original names) to restore class/function names after R8; and evaluate `invokeSuspend` state machines (switch on `label` field, values carried in `L$0`/`I$0` spill fields) by running the cases in label order. Strings to the ANS regex; names to renamed_chain/reflection resolution."},
  {"id": "dex-bytecode-integrity-gate", "concept": "anti-tamper: answer keyed by dex checksum/signature of classes.dex or a method's own bytes", "priority": 3, "action": "prebuild", "detail": "integrity-derived-key covers APK/cert digests; add the in-dex variants: app reads its own classes.dex (getPackageCodePath + ZipFile) and computes Adler32/CRC32/SHA-1/MD5 over the whole dex, the header checksum field, or a code_item byte range, then xors/hashes it into the answer. Compute every such digest from the shipped bytes (dex header adler32 @0x08, sha1 @0x0c, zip CRC of classes.dex) and try them as keys against puzzle data / dex arrays with the ANS- known plaintext."},
  {"id": "worker-cue-inline", "concept": "unseen-theme routing", "priority": 1, "action": "note", "detail": "Inline the 'Recognition cues' block above into the mobile worker prompt (skills/huntress-ctf mobile skill) so an unseen container (Flutter/RN/Xamarin/asset dex) is routed in 1-2 turns; add step 2's UTF-16 scan to triage.md pre-extraction."},
  {"id": "pyxamstore", "concept": "Xamarin assemblies.blob / XALZ (row 55)", "priority": 2, "action": "tool", "detail": "pip: `uv pip install --python .venv/bin/python pyxamstore` (or github jakev/pyxamstore). Then `pyxamstore unpack -d assemblies/` and ilspycmd. Also small prebuild: XALZ header (magic, index, size) + lz4.block decompress (lz4 in venv)."},
  {"id": "apkid", "concept": "packer / obfuscator / anti-VM identification (rows 44-48)", "priority": 2, "action": "tool", "detail": "pip: `uv pip install --python .venv/bin/python apkid` (needs yara-python, already OK). `apkid -j x.apk` names packers, obfuscators and anti-debug in one call: a fast routing cue for an unseen theme."},
  {"id": "bundletool", "concept": "AAB / APKS packaging (row 58)", "priority": 2, "action": "tool", "detail": "github release jar google/bundletool (bundletool-all-1.17.x.jar) into tools/bundletool + bin shim. `bundletool dump manifest --bundle x.aab`, `bundletool build-apks --mode=universal`. AAB manifests are protobuf, so aapt dump xmltree fails on them."},
  {"id": "il2cppdumper", "concept": "Unity IL2CPP (row 56)", "priority": 3, "action": "tool", "detail": "github release Perfare/Il2CppDumper (or SamboyCoding/Cpp2IL) into tools/; run with bin/dotnet. Only if a Unity fixture ever ships."},
  {"id": "blutter", "concept": "Flutter Dart AOT (row 52)", "priority": 3, "action": "tool", "detail": "github worawit/blutter (python3 blutter.py <lib dir> <out>; builds per Dart version with cmake/ninja + fetches the Dart SDK, slow first run; arm64 only). Alt: pip reflutter (needs repack + device: low value). Plain strings on libapp.so cover literal answers."},
  {"id": "abe", "concept": "encrypted Android backup (row 16)", "priority": 3, "action": "tool", "detail": "github release nelenkov/android-backup-extractor (abe.jar): `java -jar abe.jar unpack b.ab b.tar [pw]`. Needed only for encrypted .ab (PBKDF2+AES); unencrypted is zlib-flate."},
  {"id": "frida-tools", "concept": "dynamic instrumentation / root and frida checks (rows 47, 48)", "priority": 3, "action": "tool", "detail": "pip frida-tools / objection. Low value: no Android device or emulator here (adb present, no target), and every answer so far was static. Keep the rule: read the gated branch statically."},
  {"id": "standalone-baksmali", "concept": "smali-level reading / patching (row 51)", "priority": 3, "action": "tool", "detail": "Link tools/dex2jar/d2j-baksmali.sh + d2j-smali.sh into bin/ (already on disk), or github google/smali release. apktool d already emits smali, so cosmetic."},
  {"id": "ios-ipa-readiness", "concept": "iOS IPA (row 64)", "priority": 3, "action": "note", "detail": "Lane is named mobile-android; if an .ipa ever ships: unzip Payload/, plistlib for Info.plist and binary plists, rz-bin -zz / lief for Mach-O strings, ipsw (github blacktop/ipsw release) for class-dump. Nothing to prebuild now."}
]
```
