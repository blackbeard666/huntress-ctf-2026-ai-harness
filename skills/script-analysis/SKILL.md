---
name: script-analysis
description: Huntress script-analysis lane - static and sandboxed analysis of PowerShell, JScript/JavaScript, VBScript, batch, HTA and Python specimens. Classify intent (enum scenarios such as resource_hijacking/collection/impact), map the primary MITRE ATT&CK technique (T####[.###]), and extract exact indicators (URLs, wallets, mutexes, file names, user agents, extensions, ransom-note names, registry keys). Covers deobfuscation (-EncodedCommand, FromBase64String, char-code arrays, string reversal, -f format, Invoke-Expression/IEX layers, eval). Use for script-analysis-day-NN challenges.
---

**Installed: box-js, js-beautify, webcrack, node, pwsh, olevba, decompyle3 / uncompyle6 / xdis (venv), ilspycmd (.NET), base64/xxd/7z.**

# Never run specimens as-is
Read them statically first. To peel a layer dynamically, **replace the sink** and run with a timeout and no network:
- PowerShell: replace `Invoke-Expression`/`IEX`/`iex`/`.Invoke()`/`& (` with `Write-Output`, then
  `timeout 20 pwsh -NoProfile -NonInteractive -Command -` < patched.ps1. `-EncodedCommand X` = UTF-16LE base64:
  `base64 -d | iconv -f utf-16le`.
- JavaScript: `webcrack in.js -o outdir`, `js-beautify`; replace `eval`/`Function(` with `console.log`; `box-js --no-kill`
  (sandboxed emulator) for WSH JScript.
- VBScript: replace `Execute`/`ExecuteGlobal`/`Eval` with `WScript.Echo` and decode by reading; there is no cscript here, so
  re-implement the decoder in Python.
- Batch: expand `set` variables and `%var:~x,y%` substrings in Python.
- Compiled/frozen Python -> `lib.pyc`: `recover_python(path)` (PyInstaller extract via pyinstxtractor-ng, then
  decompyle3; `dis` disassembly fallback that always works, so even modern bytecode's consts/strings surface).
  `decompile_pyc(pyc)` for a bare .pyc. NOTE: real pyarmor bytecode-encryption needs dynamic unpack (residual
  gap); .NET payloads: `ilspycmd` (installed, dotnet 10); de4dot is not installed — see reference/HARDENING.md.

# Indicator extraction (exact, from the bytes)
- Regexes over the *deobfuscated* text: URLs `https?://[^\s'"<>]+`, wallets (BTC `bc1[a-z0-9]{25,60}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}`,
  XMR `4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}`, ETH `0x[a-fA-F0-9]{40}`), mutex names (`New-Object System.Threading.Mutex(...,'NAME')`,
  `CreateMutex`), user agents (`User-Agent`, `-UserAgent`), file and extension literals, ransom-note filenames.
- "first exact filename indicator" = the first occurrence in source order unless the question says otherwise.
- Keep quotes out of the answer unless the format says otherwise; respect `trim`.

# Scenario and ATT&CK mapping (pick from `accepted_values` only)
| Behaviour | Typical technique |
|---|---|
| crypto-miner, xmrig, pool URL, wallet | T1496 Resource Hijacking |
| gathers files/clipboard/screenshots, zips and stages | GM-confirmed for the D1 `synthetic_collection` scenario: **T1555.003** (browser credentials). T1005/T1119/T1560/T1074 were REJECTED -- see reference/techniques/script-analysis.md |
| exfil to web service / C2 over HTTP | T1041 / T1567 |
| encrypts files, renames extension, drops ransom note | T1486 Data Encrypted for Impact |
| deletes shadow copies / backups | T1490 Inhibit System Recovery |
| scheduled task / Run key persistence | T1053.005 / T1547.001 |
| PowerShell execution itself | T1059.001 (only when execution is the "primary" behaviour) |
Choose the technique for the script's *primary* purpose; only use `none` when the question allows it.

# Solver tips
Map every sample by its behaviour (keyword families), not its file name. Extract indicators with regexes after a generic
deobfuscation pass (base64 or UTF-16 detection, char-code joins, `-f` formatting, reversal) so new obfuscation layers in
the variants still decode.
