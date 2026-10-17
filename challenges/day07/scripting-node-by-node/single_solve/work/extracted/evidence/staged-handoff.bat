@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:MXNwLjdjZmJjNTRmOGUtZWdhdHM9ZWdhdHNfdHhlbnx0YWQuN2NmYmM1NGY4ZS1lZ2F0c1xiYUxzc2VydG51SFxjaWxidVBcc3Jlc1VcOkM9aHRhcF9lbGlmfHRhZC41YmZhMjBmYS9kaWxhdm5pLmVscG1heGUuN2NmYmM1NGY4ZS8vOnNwdHRoPWxydXw3Y2ZiYzU0ZjhlLW5naWFwbWFjPWRpX25naWFwbWFjfGxsZWhzcmV3b3A9ZWdhdWduYWxfdHhlbnx5cnRlcl9rY2FibGxhZj1ocGFyZ3w0PXRudW9jX2VnYXRzfGV4ZS4yM2xsZG51cj1yZXRwYWRhfHRwaXJjc19mZm9kbmFoLHNzZWNvcnBfaGN0YXBzaWQsZWxpZl9ldGlydyxldG9tZXJfZXJpdXFjYT1zcGV0c3wxPXY=
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=rundl"& rem HUNTRESS quote compound
set "fragment1=l32.exe|stage_count=4|graph=fallback_retry|next_language=powershell|campaign_id=c"& rem HUNTRESS quote compound
set "fragment2=ampaign-e8f45cbfc7|url=https://e8f45cbfc7.example.invalid/af02afb5.dat|file_path="& rem HUNTRESS quote compound
set "fragment3=C:\Users\Public\HuntressLab\stage-e8f45cbfc7.dat|next_stage=stage-e8f45cbfc7.ps1"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=8d283679"
set "recovered_configuration=!fragment0!!fragment1!!fragment2!!fragment3!"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo rundll32.exe acquire, write, dispatch, and hand off stage-e8f45cbfc7.ps1
exit /b 0
