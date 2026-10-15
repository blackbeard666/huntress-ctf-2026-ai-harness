# script-analysis — coverage atlas (D1-D15 seen vs. D16+ candidates)

Built 2026-10-15 after D15 (1026 ids, 116 members). Read with `reference/techniques/script-analysis.md` (what the GM
actually asked) — this file is the BREADTH map: which common script/malware-script CTF concepts we have met, which we
have not, how to fingerprint and statically decode each, and what to prebuild/install before they drop.

Context that drives the likelihood column:
- Since D8 every new language is a **v=3 polyglot**: 4 fixtures `polyglot-<lang>-{benign-utility,downloader,launcher,
  staged-chain}` (44 ids: role/attack/adapter/campaign/steps/stage-count/host-profile/obfuscation/stage-profile/
  next-language + url) plus sometimes one `host-<profile>-<lang>` file. All answers are plan-verbatim; the plan sits
  behind `HUNTRESS_ANALYSIS_V1:<B64|HEX|HB64|FRAG>-..` in the host's comment syntax + a `descriptor_<id>` literal.
  The D15 solver (`challenges/day15/scripting-crumb-trail/solver/solve.py`, `V3_MARK` / `_v3_peel` / `analyse_v3`)
  is language-agnostic **as long as** the marker is ASCII/UTF-8 in raw bytes, on one line, peelable by hex/base64/
  reverse within 3 layers. The real D16+ risk is not a new language — it is a new **carrier/encoding/container** or a
  new **synthetic-label family** (the D2-D7 style/control/expansion era).
- Family names may contain `_` (D14 `polyglot-msbuild_xml`); host profiles seen: standalone, wsf_jscript, wsf_mixed,
  hta_jscript, php_webshell, sct_scriptlet, lua_openresty, perl_cgi. D14 picked a Windows LOLBin (MSBuild), D10 a WMI
  host (MOF), D13 a macOS host: the organizers alternate "language" days and "trusted-host abuse" days.
- ~16 drops left (D16-D31). Paths below: `$R=/home/testpwn/huntress-2026`; `source bin/env.sh` puts `bin/` on PATH
  (pwsh 7.6.6, box-js, js-beautify, webcrack, pycdc/pycdas, 7z, autoit-ripper, ilspycmd). `R/.venv/bin` holds oletools,
  msoffcrypto-tool, decompyle3/uncompyle6/xdis, pyinstxtractor-ng, LnkParse3, chepy, lxml, and **binary refinery 0.11.1**
  (AST deobfuscators `ps1` `js` `vba`, batch emulator `bat`, `wshenc`, `xlmdeobf`, `xtone`, `xtchm`, `lnk`, `xtpyi`,
  `pyc`, `a3x`, `xtnode`, `decompress`, `b64`, `xor`, `rot`...). Usage: `.venv/bin/<unit> < file`.

## 1. Concept table

Legend: INSTALLED = verified with `which`/`.venv/bin` on 2026-10-15; MISSING = not on the box. Never execute a
fixture's behaviour: run only decoders / AST deobfuscators / emulators on extracted literals.

| # | concept | status | recognition cues | standard tool / approach + exact command | D16+ likelihood |
|---|---|---|---|---|---|
| 1 | PowerShell `.ps1` (v=1 JSON descriptor, `$nativeTypes`) | seen D1 | `$encodedMaterial=[Convert]::FromBase64String(..)`, `function artifact_<hex>`, `[pscustomobject]@{..}` | `base64 -d`; `.venv/bin/ps1 < f.ps1` (INSTALLED, AST deob); `pwsh -NoProfile -NonInteractive -c '<decode expr only>'` (INSTALLED) | carried daily |
| 2 | JScript WSH `.js` | seen D2 | `ActiveXObject`, `WScript.`, `decode_*/recover_*/inspect_*`, `"52:90:.."` | `node $R/hctf/js_sandbox.js f.js`; `box-js --no-kill f.js` (INSTALLED); `.venv/bin/js < f.js` | carried daily |
| 3 | Batch `.bat/.cmd` + expansion (%/!/call/for) | seen D3 | `rem HUNTRESS-CODEC:`, `setlocal EnableDelayedExpansion`, `call set %%..%%` | Python cmd-expansion emulation (solver `batchplan.py`); `.venv/bin/bat < f.bat` (INSTALLED, refinery emulator prints command lines) | carried daily |
| 4 | VBScript `.vbs` | seen D4 | `Const Codec_<id>`, `Chr(`, `On Error Resume Next`, `Select Case` | lib.codec from the Codec const; `.venv/bin/vba < f.vbs` (INSTALLED) | carried daily |
| 5 | Python carriers (pyinstaller/pyarmor/py2exe/cx_Freeze/zipapp/wheel/pyc38) | seen D5 (recovered `.py`), D6 TT real cx_Freeze binary | `*-recovered.py`, `MATERIAL_<id>`, `CODEC_<id>`; binary: `MEI\x0c\x0b\x0a\x0b\x0e`, `PYZ`, `library.zip` | `lib.pyc.recover_python(path)`; `pyinstxtractor-ng x.exe`; `pycdc f.pyc` / `decompyle3 f.pyc` (all INSTALLED); `.venv/bin/xtpyi -l < x.exe` | med: a real frozen binary variant |
| 6 | Bash `.sh` + bash-advanced (`Feature_<id>`) | seen D6/D7-D14 | `readonly Material_`, `${!ptr}`, `local -A`, `trap`, here-strings | lib.codec; never run bash; `bash -n f.sh` (syntax only) | carried; +2 fixtures some days |
| 7 | Node ESM `.mjs` | seen D7 | `import`, top-level `await`, `process.env.HUNTRESS_INSPECT_ONLY`, `Buffer.from` | lib.codec static; `webcrack f.mjs -o out/` (INSTALLED) | carried daily |
| 8 | PHP polyglot + webshell host | seen D8 | `<?php`, `$descriptor_<id>`, `eval(`/`assert(`, `$_POST`/`$_REQUEST` | V3_MARK peel; `php` MISSING (`apt install php-cli` for `php -l`/token dump only) | carried daily |
| 9 | WSF / HTA hosts | seen D8 | `<job><script language=..>`, `<hta:application>`, mixed JScript+VBS | extract each `<script>` body (lxml/bs4 INSTALLED) and route by language | carried |
| 10 | Lua + OpenResty host | seen D9 | `local descriptor_`, `--` comments, `ngx.`, `inert_handler_<id>` | V3_MARK; `lua`/`luac` MISSING (`apt install lua5.4`) | carried |
| 11 | SCT scriptlet (regsvr32 /i:url scrobj.dll, Squiblydoo) | seen D9 (host) | `<?xml?><scriptlet><registration progid=..>`, `<![CDATA[` | strip CDATA -> JScript/VBS route | carried |
| 12 | WMI MOF | seen D10 | `#pragma namespace`, `instance of __EventFilter`, `ActiveScriptEventConsumer`, `ScriptText =` | V3_MARK; ScriptText is a C-escaped JS/VBS string -> unescape then route | carried |
| 13 | TypeScript | seen D11 | type annotations, `interface`, `as const`, `.ts` | V3_MARK; no tsc needed (strip types or read literals) | carried |
| 14 | AutoIt `.au3` | seen D12 | `Global Const $descriptor_`, `;` comments, `#include <..>`, `Execute(`, `BinaryToString` | V3_MARK; compiled: `autoit-ripper x.exe out/` / `.venv/bin/a3x < x.a3x` (INSTALLED) | carried; compiled a3x = med |
| 15 | AppleScript (source) | seen D13 | `property descriptor_<id> :`, `--` comments, `do shell script`, `osascript -e` | V3_MARK; compiled `.scpt` (`FasdUAS` magic) = no decompiler (MISSING: applescript-disassembler) | carried; `.scpt` = low/med |
| 16 | MSBuild `.proj` inline task | seen D14 | `<Project xmlns=..msbuild..>`, `<UsingTask TaskFactory="CodeTaskFactory">`, `<Code Type="Fragment">` C# CDATA, `<HuntressDescriptor>` | V3_MARK in `<!-- -->`; lxml for the property element | carried |
| 17 | Perl `.pl` + perl_cgi host | seen D15 | `#!/usr/bin/env perl`, `use strict;`, `my $descriptor_`, `print "Content-Type:` | V3_MARK; `perl -MO=Deparse f.pl` (INSTALLED, parse-only, BEGIN blocks still run - strip them) | carried |
| 18 | Ruby `.rb` (+ ERB/Rack/Rails host) | gap | `require`, `def ..end`, `puts`, `#{}` interpolation, `=begin/=end`, `.unpack1('m0')`, `Base64.decode64`, `eval`/`instance_eval`, `<%= %>` | `ruby -c f.rb` (INSTALLED /usr/bin/ruby, syntax only); `ruby -e 'print ARGV[0].unpack1("m")' <b64>`; Ruby CONSTANTS are uppercase -> descriptor may be `DESCRIPTOR_X =` | **high**: last major mainstream script language; ruby already installed |
| 19 | PowerShell module / `.psm1` `.psd1` `.ps1xml` (v=3 polyglot-powershell) | gap (PS only v=1) | `Export-ModuleMember`, `FunctionsToExport`, `<Types><Type><ScriptMethod><Script>`, `<#  #>` block comments (marker may sit inside `<# #>`) | `.venv/bin/ps1 < f.psm1`; lxml for ps1xml `<Script>` nodes | **high**: PS is the canonical malware language and has no v=3 fixture |
| 20 | Tcl / Expect | gap | `#!/usr/bin/tclsh`, `set descriptor_x "..."` (no `=`!), `proc`, `puts`, `binary decode base64`, `{braces}` strings | `tclsh` MISSING (`apt install tcl`); static: regex `set\s+descriptor_\w+\s+["{]` | med |
| 21 | R script | gap | `<-` assignment, `library(`, `base64enc::`, `rawToChar(`, `system(`, `#` comments | `Rscript` MISSING (`apt install r-base-core`, big); static `<-` descriptor regex | low/med |
| 22 | Groovy / Jenkinsfile | gap | `pipeline { agent .. stages`, `sh '''..'''`, `def x = ".."`, `"cmd".execute()`, `.decodeBase64()` | `groovy` MISSING (java INSTALLED; jar from apache); static read | med: CI-abuse host fits "trusted toolchain" theme |
| 23 | Kotlin script `.kts` / Gradle `build.gradle.kts` | gap | `val descriptor_x = ".."`, `plugins {`, `tasks.register`, `Runtime.getRuntime().exec`, `Base64.getDecoder()` | `kotlinc` MISSING; static | med (Gradle build abuse) |
| 24 | Go (`go run`, `//go:generate`) | gap | `package main`, `descriptor_x := ".."` (`:=` breaks current regex), `exec.Command`, raw `` `..` `` strings | `go vet f.go` (INSTALLED /usr/bin/go; never `go run`) | med |
| 25 | Rust script / `build.rs` | gap | `fn main()`, `const DESCRIPTOR_X: &str = ".."`, `std::process::Command`, `r#".."#` raw strings, `\u{..}` | `rustc` INSTALLED (don't build); static | low/med (`build.rs` = build-time abuse) |
| 26 | AWK program | gap | `BEGIN {`, `system(`, `"cmd" \| getline`, `#!/usr/bin/awk -f` | `gawk --lint -f f.awk /dev/null` is NOT safe (BEGIN runs) -> static only | med (LOLBin `awk`, GTFOBins) |
| 27 | sed script | gap | `#!/bin/sed -f`, `s/../../e` (GNU exec flag), `w /path` | static | low |
| 28 | Makefile | gap | `target: deps` + TAB recipes, `$(shell ..)`, `DESCRIPTOR := ..` (`:=`), `.PHONY` | `make -n -f Makefile` (INSTALLED; dry run still evaluates `$(shell)` -> static only) | med (build-system abuse theme) |
| 29 | Dockerfile | gap | `FROM`, `RUN curl .. \| sh`, `ENV`, `ARG`, `# HUNTRESS..` comments, `COPY --chmod` | static; `docker` INSTALLED (never build) | med |
| 30 | CI YAML (GitHub Actions / GitLab CI) | gap | `on: [push]`, `jobs:`, `runs-on:`, `steps: - run:` + block scalar, `stages:`, `script:`; block scalars span lines | `.venv/bin/python -c 'import yaml,sys;print(yaml.safe_load(open(sys.argv[1])))' f.yml` (INSTALLED); `yq` MISSING | med/high: supply-chain host, family would be `polyglot-github_actions`-style |
| 31 | Ansible playbook | gap | `- hosts:`, `tasks:`, `ansible.builtin.shell:`, `become: true`, `vars:` | yaml.safe_load (INSTALLED); ansible MISSING (not needed) | low/med |
| 32 | Terraform HCL | gap | `resource "null_resource"`, `provisioner "local-exec" { command = ..}`, `data "external"`, `locals {` | `terraform fmt -check` (INSTALLED; never init/plan); python-hcl2 MISSING | low/med |
| 33 | XSL/XSLT via `msxsl.exe` / `wmic /format:` (Squiblytwo) | gap | `<xsl:stylesheet`, `xmlns:msxsl="urn:schemas-microsoft-com:xslt"`, `<msxsl:script language="JScript" implements-prefix=..>` CDATA | lxml parse (INSTALLED), pull `msxsl:script` text -> JS/VBS route; NEVER apply the transform; `xsltproc` MISSING | **high**: Windows trusted-host abuse, sibling of D9 SCT / D14 MSBuild |
| 34 | InstallUtil (.NET `[RunInstaller(true)]` C#) | gap | `System.Configuration.Install.Installer`, `Uninstall(IDictionary)` override, `/U` | read C#; compiled: `ilspycmd x.dll` (INSTALLED) | med (LOLBin family with MSBuild) |
| 35 | C# script `.csx` (csi / dotnet-script) | gap | `#r "nuget:..`, top-level statements, `#load` | static; `dotnet` INSTALLED, `csi`/`dotnet-script` MISSING | med |
| 36 | F# script `.fsx` | gap | `#r`, `let descriptor_x = ".."`, `printfn`, `\|>` | static (`dotnet fsi` would execute) | low |
| 37 | rundll32 `javascript:` / mshtml RunHTMLApplication one-liner | gap | `rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";..` | treat tail as JScript -> `node $R/hctf/js_sandbox.js` | med (inside a .lnk/.bat host) |
| 38 | CHM (compiled HTML help) | gap | `ITSF` magic, `.chm`, `hh.exe`, HTML with `<OBJECT classid=..ADB880A6..>` shortcut command | `.venv/bin/xtchm -l < f.chm` (INSTALLED); `7z x f.chm -oout` (INSTALLED) | med (container carrier) |
| 39 | LNK with embedded command line | gap | `4C 00 00 00 01 14 02 00` magic, args `/c powershell -enc ..`, padded whitespace args | `.venv/bin/lnk < f.lnk` / `lnkparse f.lnk` (INSTALLED) | med |
| 40 | VBA macros (`.bas`, `.docm/.xlsm`, OLE `.doc`) | gap | `Sub AutoOpen()`, `Document_Open`, `Attribute VB_Name`, `Shell`, `CreateObject("WScript.Shell")`, `vbaProject.bin` | `.venv/bin/olevba --decode --deobf f.docm`; `.venv/bin/vba < module.bas`; `pcodedmp`/`vbapc` for VBA stomping (all INSTALLED); `msoffcrypto-tool -p VelvetSweatshop` | **high**: classic, and the 4th WSH-family language not yet polyglotted |
| 41 | Excel 4.0 / XLM macros | gap | `Macro1` sheet, `=EXEC(`, `=CALL(`, `=FORMULA(`, `CHAR(` chains, hidden/very-hidden sheets, BOUNDSHEET | `.venv/bin/xlmdeobf < f.xls` (INSTALLED, refinery port); standalone `xlmdeobfuscator` MISSING (`pip install XLMMacroDeobfuscator`) | med |
| 42 | OneNote `.one` embedded scripts | gap | GUID `E4525C7B-8CD8-A74D-AEB1-5378D02996D3`, embedded `.hta/.bat/.wsf` | `.venv/bin/xtone -l < f.one`, `.venv/bin/xtone <name> < f.one` (INSTALLED) | low/med |
| 43 | `.reg` registry import | gap | `Windows Registry Editor Version 5.00` in **UTF-16LE with BOM**, `hex(2):` REG_EXPAND_SZ byte lists, `Run`/`RunOnce` keys | `iconv -f UTF-16LE -t UTF-8 f.reg`; `hex(2):` = comma hex of UTF-16LE text | med: persistence-host day; breaks the raw-bytes V3_MARK regex |
| 44 | `.inf` (cmstp / setupapi, `RegisterOCXs`, `UnRegisterOCXSection` -> SCT URL) | gap | `[Version]`, `Signature="$CHICAGO$"`, `RunPreSetupCommands`, `[Strings]` `%var%` | static; resolve `%strings%` substitutions | med (Windows LOLBin host) |
| 45 | `.url` / `.scf` / `.library-ms` / `.desktop` | gap | `[InternetShortcut] URL=`, `IconFile=\\host\`, `[Shell] Command=2`, `[Desktop Entry] Exec=` | static INI parse (`configparser`) | low |
| 46 | Deno / Bun scripts | gap | `Deno.run`, `Deno.Command`, `Bun.spawn`, `import .. from "jsr:`/`npm:` specifiers | webcrack / static; `deno`/`bun` MISSING (not needed) | low/med (TS+Node already seen) |
| 47 | JScript.Encode / VBScript.Encode (`.jse` `.vbe`) | gap | `#@~^` .. `^#~@`, `language="JScript.Encode"` | `.venv/bin/wshenc < f.vbe` (INSTALLED) | med: cheap mutation of seen hosts |
| 48 | Codec `rep\|transform\|key` (hex/dec/b64/escapes x xor/rolling/add/sub/reverse) | seen D3-D8 | `Codec_<id>`/`CODEC_<id>`/`HUNTRESS-CODEC:` const | `lib.codec.find_codecs(src)`, `lib.codec.decode(..)` | carried |
| 49 | v=3 marker tags B64 / HEX / HB64 / FRAG | seen D8-D15 | `HUNTRESS_ANALYSIS_V1:<TAG>-` | solve.py `_v3_peel` (hex/b64/reverse, 3 layers) | carried; NEW tag (B32/Z64/XOR/ROT) = **high** risk, peel too narrow |
| 50 | Char-code arrays (`String.fromCharCode`, `Chr()`, `[char]`, `chr()`) | seen D2/D4/D5 | integer lists + a map/join | lib.codec int_array; `.venv/bin/js < f.js` folds constants | carried |
| 51 | XOR / rolling XOR / add-sub mod 256 | seen D3-D8 | key consts, `^` / `Xor` / `bxor` | lib.codec transforms; `.venv/bin/xor -h` (refinery) | carried |
| 52 | String / list reversal | seen D4-D7 | `StrReverse`, `[::-1]`, `.split('').reverse().join('')`, `-join ($s[-1..-($s.Length)])` | try both text- and list-level reversal | carried |
| 53 | PowerShell `-EncodedCommand` (UTF-16LE base64) | gap | `-enc`/`-e`/`-ec`/`-EncodedC`, b64 with every 2nd byte `A` (`JABz`, `SQBFAFgA`) | `echo <b64> \| base64 -d \| iconv -f UTF-16LE -t UTF-8` | high (if a PS polyglot comes) |
| 54 | Invoke-Obfuscation tokens: `-f` reorder, backticks, concat, `-join`, `-replace`, `.Invoke()` | gap | `("{2}{0}{1}" -f 'b','c','a')`, ``I`E`X``, `&('i'+'ex')`, `${`e`nv:..}` | `.venv/bin/ps1 < f.ps1` (INSTALLED, folds -f/concat/char); PowerDecode/PSDecode MISSING | high (paired with #19) |
| 55 | DOSfuscation: `%VAR:~n,m%` substrings, `^` carets, `%COMSPEC:~-16,1%`, FOR /F reassembly | gap (only %/!/call/for joins seen) | `:~`, `^`, `set x=%y:a=b%` substitution, `cmd /V:ON /C` | `.venv/bin/bat < f.bat` (INSTALLED emulator); extend solver expansion emulator with substring+substitution | med/high: batch is still the lane's synthetic-label heavy lang |
| 56 | Env-var substring tricks (PS `$env:comspec[4,15,25]-join''`, `$PSHome[21]+$PSHome[30]+'x'`, `$ShellId[1]`) | gap | indexing into `$env:`/`$PSHome`/`$ShellId`/`$VerbosePreference` | resolve with known Windows values (`C:\WINDOWS\system32\cmd.exe`, `C:\Windows\System32\WindowsPowerShell\v1.0`) — static table | med |
| 57 | gzip / deflate + base64 layers | gap | `H4sI` (gzip b64), `eJ`/`eN`/`eF` (zlib), `IO.Compression.DeflateStream`/`GzipStream`, `gzinflate`, `zlib.decompress`, `Zlib::Inflate` | `.venv/bin/b64 < x \| .venv/bin/decompress` (INSTALLED); raw deflate `zlib.decompress(d,-15)` | high: most common real-world layer, absent from lib.codec REPS |
| 58 | SecureString / `ConvertTo-SecureString -Key` | gap | `76492d1116743f0423413b16050a5345` header, `-Key (1..16)`, `PtrToStringAuto(SecureStringToBSTR` | `pwsh -NoProfile -c '$s=ConvertTo-SecureString "<blob>" -Key (<key>); [Net.NetworkCredential]::new("",$s).Password'` (decoder only, INSTALLED) | low/med |
| 59 | AMSI / ETW bypass patterns | gap | `AmsiUtils`, `amsiInitFailed`, `AmsiScanBuffer` patch bytes `B8 57 00 07 80 C3`, `EtwEventWrite`, split strings `'Am'+'si'` | recognition only -> ATT&CK T1562.001; never run | low/med (a "defense evasion" role/enum value) |
| 60 | JSFuck / JJencode / AAencode | gap | only `[]()!+` chars; `$=~[];$={___:++$`; `ﾟωﾟﾉ= /｀ｍ´）ﾉ` | replace final `()` call with capture in `node $R/hctf/js_sandbox.js`; `.venv/bin/js < f.js` | low/med |
| 61 | obfuscator.io (`_0x` string array + rotate IIFE + decoder, control-flow flattening) | gap | `var _0x1a2b=['..']`, `(function(_0x..,_0x..){..push(..shift())`, `while(!![])`, `'\x68\x65'` | `webcrack f.js -o out/` (INSTALLED); `synchrony` MISSING (`npm i -g deobfuscator`) | med |
| 62 | Python exec layers (pyobfuscate, marshal/zlib/base64, `_ = lambda __ : __import__('zlib')..`, BlankOBF, Hyperion) | gap | `exec(marshal.loads(`, `exec((_)(b'..'))`, `__import__('base64').b64decode`, `[::-1]` on bytes | replace `exec`/`eval` with print under `python3 -I`; `marshal.loads` -> `pycdc`/`xdis` (INSTALLED; Python version must match) | med |
| 63 | Lua obfuscators (luac bytecode, `\ddd` decimal escapes, `loadstring`/`load` layers, IronBrew/Prometheus VMs) | gap | `\27Lua` magic, `string.char(`, `loadstring(`, huge `\104\101` strings | decode `\ddd` statically; `unluac.jar` MISSING (`java -jar unluac.jar f.luac`, java INSTALLED); `luadec` MISSING | low/med |
| 64 | PHP layered eval (`eval(gzinflate(base64_decode(str_rot13(..))))`, `chr()` concat, `preg_replace /e`, `create_function`) | gap (D8 PHP was plain hex/b64) | the nested call chain, `?>` + base64 blob | Python reimplementation of each named PHP fn in chain order (`.venv/bin/rot`, `b64`, `decompress`); php MISSING | med |
| 65 | Source-file encoding / container wrapping (UTF-16LE/BE, gzip'd file, nested zip, base64'd member) | gap | `FF FE`/`FE FF` BOM, NUL-interleaved ASCII, `1F 8B`, `PK\x03\x04` inside a leaf | `file f`; `iconv -f UTF-16LE -t UTF-8 f`; `.venv/bin/decompress < f` | **high**: cheapest variant mutation; silently defeats raw-bytes regexes |

Counts: 65 rows; seen 22 (rows 1-17, 48-52), gap 43.

## Recognition cues (worker quick-reference)
```
FINGERPRINT (first 512 bytes + `file`), never by extension:
 FF FE / FE FF / NUL every 2nd byte -> UTF-16: iconv -f UTF-16LE -t UTF-8 first (.reg, PS "Unicode" saves, .inf)
 1F 8B gzip | PK\x03\x04 zip/ooxml(.docm .xlsm) | D0 CF 11 E0 OLE(.doc .xls .msi) | ITSF chm | 4C 00 00 00 01 14 02 00 lnk
 E4 52 5C 7B onenote | \x1bLua luac | FasdUAS compiled AppleScript | MEI\x0c / PYZ pyinstaller | 0x0d0d0a.. pyc magic
 #@~^ ..^#~@ = Script-Encoder (.vbe/.jse) -> .venv/bin/wshenc < f
SHEBANG/HEADER -> language:
 #!..perl / use strict;  -> perl      #!..ruby / require / def..end / =begin -> ruby
 #!..tclsh / set x "v" / proc -> tcl  x <- v / library( -> R          package main / := -> go
 fn main / let mut / r#".."# -> rust  val/fun + plugins{ -> kotlin(.kts)   pipeline{ stages{ / def x= -> groovy/Jenkinsfile
 BEGIN{ / getline -> awk              target:\n\tcmd / $(shell -> make     FROM / RUN -> Dockerfile
 on:/jobs:/runs-on: -> GH Actions     stages:/script: -> GitLab CI          - hosts:/tasks: -> ansible
 resource "x" / provisioner "local-exec" -> terraform    Windows Registry Editor 5.00 -> .reg
 [Version] Signature="$CHICAGO$" -> .inf   [InternetShortcut] -> .url   [Shell] Command= -> .scf
 <xsl:stylesheet + msxsl:script -> XSLT (msxsl/wmic)   <scriptlet> -> SCT   <job> -> WSF   <hta:application> -> HTA
 <Project ..msbuild> + UsingTask -> MSBuild    Installer + [RunInstaller(true)] -> InstallUtil C#
 Sub AutoOpen/Document_Open/Attribute VB_Name -> VBA   =EXEC(/=FORMULA( in a sheet -> XLM
 instance of __EventFilter -> MOF        #r "nuget: -> csx   let/printfn/|> -> fsx   Deno./Bun. -> deno/bun
PLAN FIRST (the lane's contract since D2):
 grep raw AND utf-16-decoded text for HUNTRESS_ANALYSIS_V\d+ / Codec_ / CODEC_ / HUNTRESS-CODEC / MATERIAL_ / descriptor
 descriptor syntaxes to accept: `x = ".."` `x := ".."` `set x ".."`/`set x {..}` `x <- ".."` `X: &str = ".."`
   `DESCRIPTOR_X = ".."` (Ruby const) `descriptor_x: ".."` (YAML) `<HuntressDescriptor>..</..>` (XML) heredoc/block scalar
 material may wrap across lines (`|` YAML block, `=begin`, `<# #>`, `"""`, `\` continuation, `.`/`+`/`&`/`..` concat):
   join the literal pieces, strip whitespace/separators, THEN peel
 peel by SHAPE, max 4 layers, accept only output starting `v=` (or `{` JSON): hex (any separators) | base64 std/urlsafe
   (also reversed text) | base32 [A-Z2-7=] | base85/ascii85 <~~> | gzip H4sI / zlib eJ eN eF | rot13 | %xx | \xNN \NNN \ddd
   \uXXXX \u{..} | int lists (READ the radix from code) | UTF-16LE inside b64 (PS -enc: every 2nd byte 00)
 copy plan values verbatim (role, attack, adapter, steps, profiles, next_language); never derive them from code
LAYERED OBFUSCATION -> standard tool (static, no network, no exec of behaviour):
 PowerShell   .venv/bin/ps1 < f  (folds -f reorder, `ticks, 'a'+'b', [char]N, -join, -replace, .Invoke)
 JS           webcrack f.js -o out/  (obfuscator.io arrays) | .venv/bin/js < f | node hctf/js_sandbox.js f (eval->capture)
 VBA/VBS      .venv/bin/olevba --decode --deobf f | .venv/bin/vba < f.bas | pcodedmp f.doc (stomped p-code)
 Batch        .venv/bin/bat < f  (emulates set/%x:~a,b%/%x:a=b%/^/delayed !x!; prints commands, runs nothing)
 XLM          .venv/bin/xlmdeobf < f.xls      OneNote .venv/bin/xtone -l < f.one     CHM .venv/bin/xtchm -l < f.chm
 LNK          .venv/bin/lnk < f.lnk           AutoIt  autoit-ripper x.exe out/ | .venv/bin/a3x < f
 Python       swap exec/eval->print, run with python3 -I in an empty dir; marshal blob -> pycdc / xdis (match version)
 compressed   .venv/bin/b64 < blob | .venv/bin/decompress   (gzip/zlib/raw deflate/lzma/bz2 auto)
 PHP chains   apply the named functions innermost-first in Python (base64_decode, gzinflate=raw deflate, str_rot13, strrev)
NEVER: run the fixture's interpreter on the file (ruby/perl/php/tclsh/Rscript/make/go run/msbuild/pwsh -File);
 `perl -MO=Deparse` and `make -n` still execute BEGIN/$(shell) -> strip first; apply XSLT; open URLs from the plan.
SYNTHETIC LABELS (if a new language brings code-shape questions): read accepted_values; compose `<keyword>_guard`,
 `<keyword>_once`, `<keyword>_<action>`; branch label tables on contract run_for_time:false (D15 regime flip).
ATT&CK when no attack= in plan: role table in lib.scripts.role_attack; host-language sub-ids T1059.001 PS .002 AppleScript
 .003 cmd .004 unix shell .005 VB .006 python .007 JS .010 AutoHotKey/AutoIt .011 Lua; v=3 plans so far used parent T1059.
```

## Readiness gaps
```json
[
  {"id": "v3-peel-widen", "concept": "v=3 marker/descriptor peel beyond hex/base64/reverse", "priority": 1, "action": "prebuild",
   "detail": "solve.py _v3_peel only tries hex, base64 and reversal (3 layers). A new tag (B32, Z64/GZ, XOR, ROT, A85, URL, UTF-16 b64) silently yields no plan for 44 ids. Fall back to lib.decode.peel (already does b32/b85/a85/zlib/gzip/bz2/lzma/rot/url) with accept=looks_like_plan, depth 4; carry over to the D16 solver template."},
  {"id": "source-encoding-normalize", "concept": "UTF-16LE/BE, BOM, gzip'd or base64'd leaf before marker scan", "priority": 1, "action": "prebuild",
   "detail": "V3_MARK, Codec_ regexes and descriptor scans run on raw bytes / utf-8 decode. Add normalize(data)->text: BOM sniff, NUL-interleave heuristic, utf-16 decode, gunzip, then scan both raw and normalized. .reg files and PS 'Unicode' saves are UTF-16LE by default."},
  {"id": "descriptor-syntax-generic", "concept": "descriptor literal in non-`=` languages and multi-line materials", "priority": 1, "action": "prebuild",
   "detail": "analyse_v3 regex is `descriptor_\\w*\\s*=` (case-sensitive): misses Tcl `set descriptor_x {..}`, R `<-`, Go/Make `:=`, Rust `const X: &str =`, Ruby `DESCRIPTOR_X =`, YAML `descriptor_x: |`, XML elements (D14 relied on the comment marker alone). Also the marker material can wrap across lines (YAML block scalar, =begin, <# #>, triple quotes): join continuation lines before peeling."},
  {"id": "container-carrier-extract", "concept": "script inside OLE/OOXML/XLM/OneNote/CHM/LNK/pyc/a3x/luac", "priority": 1, "action": "prebuild",
   "detail": "Pure-python (gate forbids subprocess) member walker: zipfile for OOXML + vbaProject.bin via olefile, LNK string data (LnkParse3), CHM via 7z-style ITSF directory, OneNote FileDataStoreObject GUID scan, gzip; emit every text stream to the plan scanner. Oracles for fixtures: olevba, .venv/bin/xtone, xtchm, lnk, xtpyi (all installed)."},
  {"id": "prebuild-lane-config-script", "concept": "hctf prebuild has no script-analysis lane", "priority": 1, "action": "note",
   "detail": "hctf/prebuild.py LANES lists metadata-forensics, warmups, binary only. Add a script-analysis entry (writable lib/scripts_prebuilt/ + tests/data/script_fixtures/, gate = codec tests + regress_lane script-analysis) so the 4 prebuild targets above can race at drop time."},
  {"id": "ps-layer-peel", "concept": "PowerShell -EncodedCommand / FromBase64String+Deflate/Gzip / -f / -join [char] / env-substring", "priority": 2, "action": "prebuild",
   "detail": "Static peeler for the Invoke-Obfuscation family: UTF-16LE b64, DeflateStream/GzipStream b64, format-operator reorder, [char] joins, `+` concat, backtick strip, $env:comspec/$PSHome index table. Oracle: .venv/bin/ps1 (refinery AST deob) + pwsh decode-only expressions. High value only if a polyglot-powershell / psm1 day comes."},
  {"id": "batch-substring-emulation", "concept": "DOSfuscation %VAR:~n,m%, %VAR:a=b%, ^ carets, cmd /V:ON", "priority": 2, "action": "prebuild",
   "detail": "solver batch emulator handles %/!/call/for joins only. Add substring/substitution/caret handling; oracle .venv/bin/bat (refinery emulator). Batch is the lane's synthetic-label language, so a 'batch advanced' fixture set is plausible."},
  {"id": "xslt-msxsl-route", "concept": "XSLT with msxsl:script (wmic /format, msxsl.exe)", "priority": 2, "action": "prebuild",
   "detail": "lxml: collect <msxsl:script> and <ms:script> CDATA, route by language= attr to the JS/VBS paths; marker likely in <!-- -->. Same shape as D9 SCT and D14 MSBuild hosts."},
  {"id": "gzip-zlib-codec-rep", "concept": "compressed reps in Codec_ consts", "priority": 2, "action": "prebuild",
   "detail": "lib.codec REPS/TRANSFORMS lack gzip/zlib/deflate/base32/base85/rot13/atbash/rc4. Add as generic readings in _fallback (shape: H4sI, eJ, [A-Z2-7]=) and transform candidates (rot13, rc4 with stated key)."},
  {"id": "php-eval-chain", "concept": "eval(gzinflate(base64_decode(str_rot13(..)))) chains", "priority": 2, "action": "prebuild",
   "detail": "Parse the nested call chain and apply each named function innermost-first (base64_decode, gzinflate=raw deflate, gzuncompress=zlib, gzdecode=gzip, str_rot13, strrev, hex2bin, urldecode, convert_uudecode). Same pattern for Ruby/Python/Perl decode chains (unpack('m'), pack('H*'), zlib.decompress)."},
  {"id": "python-exec-layers", "concept": "marshal/zlib/base64 exec onion (pyobfuscate, BlankOBF)", "priority": 2, "action": "note",
   "detail": "Worker recipe, not a module: replace exec/eval with a capture and run under python3 -I in an empty dir; marshal blobs -> pycdc/xdis with matching magic. lib.pyc.recover_python already covers real pyinstaller/pyc carriers."},
  {"id": "php-cli", "concept": "PHP CLI for lint/tokenize", "priority": 2, "action": "tool",
   "detail": "sudo apt-get install -y php-cli  (php -l, token_get_all; never run fixtures). PHP is a carried language since D8."},
  {"id": "lua-unluac", "concept": "Lua interpreter + bytecode decompiler", "priority": 2, "action": "tool",
   "detail": "sudo apt-get install -y lua5.4 luajit ; unluac.jar from https://sourceforge.net/projects/unluac/ into tools/unluac (java 25 installed) with bin/unluac wrapper. Needed if a luac-compiled carrier variant of the D9 Lua fixtures appears."},
  {"id": "xsltproc-cabextract-yq", "concept": "XML/CAB/YAML helpers", "priority": 2, "action": "tool",
   "detail": "sudo apt-get install -y xsltproc cabextract ; yq: pip install yq into .venv (jq wrapper; jq installed). xsltproc only for --noout lint, never to apply a stylesheet."},
  {"id": "tcl-r-interpreters", "concept": "tclsh / Rscript for syntax checks", "priority": 3, "action": "tool",
   "detail": "sudo apt-get install -y tcl (small); r-base-core is ~100 MB, install only on an R day. Static reading is enough for v=3 plans."},
  {"id": "applescript-scpt", "concept": "compiled AppleScript (.scpt FasdUAS) disassembly", "priority": 3, "action": "tool",
   "detail": "git clone https://github.com/Jinmo/applescript-disassembler into tools/ (pure python). D13 shipped source .applescript only; a compiled variant would hide the marker in UTF-16/MacRoman strings."},
  {"id": "js-deob-extras", "concept": "synchrony / JSFuck decoding", "priority": 3, "action": "tool",
   "detail": "npm i deobfuscator (synchrony CLI) into tools/npm; webcrack (installed) already handles obfuscator.io; JSFuck/JJencode via js_sandbox capture of the final call."},
  {"id": "ps-deob-modules", "concept": "PowerDecode / PSDecode for pwsh", "priority": 3, "action": "tool",
   "detail": "git clone https://github.com/Malandrone/PowerDecode and https://github.com/R3MRUM/PSDecode into tools/ (pwsh 7.6.6 installed). refinery ps1 covers most; these add layer-by-layer IEX override tracing."},
  {"id": "xlm-standalone", "concept": "XLMMacroDeobfuscator CLI", "priority": 3, "action": "tool",
   "detail": "uv pip install --python .venv/bin/python XLMMacroDeobfuscator  (refinery xlmdeobf is an inlined port and already works; standalone gives --sort-formulas/--extract-only)."},
  {"id": "dotnet-script", "concept": "csx inspection", "priority": 3, "action": "tool",
   "detail": "dotnet tool install --tool-path tools/dotnet-tools dotnet-script  (only to parse; ilspycmd covers compiled InstallUtil/MSBuild payloads)."},
  {"id": "leaf-ext-list", "concept": "nested-zip sniff skips unknown leaf extensions", "priority": 3, "action": "note",
   "detail": "_LEAF_EXT in solve.py still lacks .lua .mof .ts .au3 .applescript .proj .pl (and future .rb .tcl .r .groovy .kts .go .rs .awk .yml .tf .xsl .reg .inf). Speed only (~1 s); prefer sniffing PK magic over an extension list."},
  {"id": "new-synthetic-label-family", "concept": "code-shape labels for a new language (D2-D7 style)", "priority": 3, "action": "note",
   "detail": "Polyglot days have been plan-verbatim since D8, but an 'advanced <lang>' set (like bash-advanced) would bring feature/primitive or control/style labels. Apply playbook NAMING LAWS; probe one field per submit; check run_for_time regime first."},
  {"id": "family-name-underscore", "concept": "host-type families like polyglot-github_actions / host-<profile>-<lang>", "priority": 3, "action": "note",
   "detail": "Keep the longest-known-suffix field parse; derive the family prefix from the contract ids, never from the file stem (D14 msbuild_xml)."}
]
```
