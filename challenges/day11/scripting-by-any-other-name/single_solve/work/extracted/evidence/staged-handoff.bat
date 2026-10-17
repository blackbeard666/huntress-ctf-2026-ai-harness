@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:MXNwLmM4YjNiMjhjNDEtZWdhdHM9ZWdhdHNfdHhlbnx0YWQuYzhiM2IyOGM0MS1lZ2F0c1xiYUxzc2VydG51SFxjaWxidVBcc3Jlc1VcOkM9aHRhcF9lbGlmfHRhZC5mYTUzMTdhMy9kaWxhdm5pLmVscG1heGUuYzhiM2IyOGM0MS8vOnNwdHRoPWxydXxjOGIzYjI4YzQxLW5naWFwbWFjPWRpX25naWFwbWFjfGxsZWhzcmV3b3A9ZWdhdWduYWxfdHhlbnx5cnRlcl9rY2FibGxhZj1ocGFyZ3w0PXRudW9jX2VnYXRzfGV4ZS4yM2xsZG51cj1yZXRwYWRhfHRwaXJjc19mZm9kbmFoLHNzZWNvcnBfaGN0YXBzaWQsZWxpZl9ldGlydyxldG9tZXJfZXJpdXFjYT1zcGV0c3wxPXY=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=rundl"
set "fragment1=l32.exe|stage_count=4|graph=fallback_retry|next_language=powershell|campaign_id=c"
set "fragment2=ampaign-14c82b3b8c|url=https://14c82b3b8c.example.invalid/3a7135af.dat|file_path="
set "fragment3=C:\Users\Public\HuntressLab\stage-14c82b3b8c.dat|next_stage=stage-14c82b3b8c.ps1"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=398d52f7"
set "recovered_configuration=!fragment0!!fragment1!!fragment2!!fragment3!"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo rundll32.exe acquire, write, dispatch, and hand off stage-14c82b3b8c.ps1
exit /b 0
