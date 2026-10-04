@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:MXNwLmIyNzBlMmU3OWQtZWdhdHM9ZWdhdHNfdHhlbnx0YWQuYjI3MGUyZTc5ZC1lZ2F0c1xiYUxzc2VydG51SFxjaWxidVBcc3Jlc1VcOkM9aHRhcF9lbGlmfHRhZC5lYTQ4NjI4Ny9kaWxhdm5pLmVscG1heGUuYjI3MGUyZTc5ZC8vOnNwdHRoPWxydXxiMjcwZTJlNzlkLW5naWFwbWFjPWRpX25naWFwbWFjfGxsZWhzcmV3b3A9ZWdhdWduYWxfdHhlbnxyYWVuaWw9aHBhcmd8ND10bnVvY19lZ2F0c3xleGUuMjNsbGRudXI9cmV0cGFkYXx0cGlyY3NfZmZvZG5haCxzc2Vjb3JwX2hjdGFwc2lkLGVsaWZfZXRpcncsZXRvbWVyX2VyaXVxY2E9c3BldHN8MT12
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "h0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=run"
SeT "h1=dll32.exe|stage_count=4|graph=linear|next_language=powershell|campaign_id=campa"
SeT "h2=ign-d97e2e072b|url=https://d97e2e072b.example.invalid/782684ae.dat|file_path=C:"
SeT "h3=\Users\Public\HuntressLab\stage-d97e2e072b.dat|next_stage=stage-d97e2e072b.ps1"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=856d5446"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "cfg=!h0!!h1!!h2!!h3!"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo rundll32.exe acquire, write, dispatch, and hand off stage-d97e2e072b.ps1
exit /b 0
