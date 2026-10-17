@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:MXNwLmY3ZmI1NGYwOTItZWdhdHM9ZWdhdHNfdHhlbnx0YWQuZjdmYjU0ZjA5Mi1lZ2F0c1xiYUxzc2VydG51SFxjaWxidVBcc3Jlc1VcOkM9aHRhcF9lbGlmfHRhZC40ODQ1NmMwMS9kaWxhdm5pLmVscG1heGUuZjdmYjU0ZjA5Mi8vOnNwdHRoPWxydXxmN2ZiNTRmMDkyLW5naWFwbWFjPWRpX25naWFwbWFjfGxsZWhzcmV3b3A9ZWdhdWduYWxfdHhlbnxlbGduaXM9aHBhcmd8ND10bnVvY19lZ2F0c3xleGUuMjNydnNnZXI9cmV0cGFkYXx0cGlyY3NfZmZvZG5haCxzc2Vjb3JwX2hjdGFwc2lkLGVsaWZfZXRpcncsZXRvbWVyX2VyaXVxY2E9c3BldHN8MT12
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "h0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=reg"
SeT "h1=svr32.exe|stage_count=4|graph=single|next_language=powershell|campaign_id=campa"
SeT "h2=ign-290f45bf7f|url=https://290f45bf7f.example.invalid/10c65484.dat|file_path=C:"
SeT "h3=\Users\Public\HuntressLab\stage-290f45bf7f.dat|next_stage=stage-290f45bf7f.ps1"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=9cb6efbc"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "cfg=!h0!!h1!!h2!!h3!"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo regsvr32.exe acquire, write, dispatch, and hand off stage-290f45bf7f.ps1
exit /b 0
