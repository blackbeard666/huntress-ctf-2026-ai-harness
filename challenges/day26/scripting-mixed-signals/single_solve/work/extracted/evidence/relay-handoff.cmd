@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:plain_fragments|reverse

rem HUNTRESS-MATERIAL:MXNwLmJlNDk5OGEwY2YtZWdhdHM9ZWdhdHNfdHhlbnx0YWQuYmU0OTk4YTBjZi1lZ2F0c1xiYUxzc2VydG51SFxjaWxidVBcc3Jlc1VcOkM9aHRhcF9lbGlmfHRhZC5lNDdmZGIwZi9kaWxhdm5pLmVscG1heGUuYmU0OTk4YTBjZi8vOnNwdHRoPWxydXxiZTQ5OThhMGNmLW5naWFwbWFjPWRpX25naWFwbWFjfGxsZWhzcmV3b3A9ZWdhdWduYWxfdHhlbnxkbm9tYWlkPWhwYXJnfDQ9dG51b2NfZWdhdHN8ZXhlLjIzcnZzZ2VyPXJldHBhZGF8dHBpcmNzX2Zmb2RuYWgsc3NlY29ycF9oY3RhcHNpZCxlbGlmX2V0aXJ3LGV0b21lcl9lcml1cWNhPXNwZXRzfDE9dg==

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

SeT "fragment0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=reg"
SeT "fragment1=svr32.exe|stage_count=4|graph=diamond|next_language=powershell|campaign_id=camp"
SeT "fragment2=aign-fc0a8994eb|url=https://fc0a8994eb.example.invalid/f0bdf74e.dat|file_path=C"
SeT "fragment3=:\Users\Public\HuntressLab\stage-fc0a8994eb.dat|next_stage=stage-fc0a8994eb.ps1"

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

set "neutral_dead_label=1dd82a3a"

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration=!fragment0!!fragment1!!fragment2!!fragment3!"
exit /b 0
:HUNTRESS_EMIT

echo(!recovered_configuration!

exit /b 0

:HUNTRESS_PLAN

echo regsvr32.exe acquire, write, dispatch, and hand off stage-fc0a8994eb.ps1

exit /b 0

