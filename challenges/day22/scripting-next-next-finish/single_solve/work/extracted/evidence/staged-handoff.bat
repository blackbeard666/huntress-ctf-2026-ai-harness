@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|reverse
rem HUNTRESS-MATERIAL:MXNwLmIzMjc0YmQ5MGEtZWdhdHM9ZWdhdHNfdHhlbnx0YWQuYjMyNzRiZDkwYS1lZ2F0c1xiYUxzc2VydG51SFxjaWxidVBcc3Jlc1VcOkM9aHRhcF9lbGlmfHRhZC4zYmM0ZWRiZi9kaWxhdm5pLmVscG1heGUuYjMyNzRiZDkwYS8vOnNwdHRoPWxydXxiMzI3NGJkOTBhLW5naWFwbWFjPWRpX25naWFwbWFjfGxsZWhzcmV3b3A9ZWdhdWduYWxfdHhlbnx0dW9fbmFmPWhwYXJnfDQ9dG51b2NfZWdhdHN8ZXhlLmxsZWhzcmV3b3A9cmV0cGFkYXx0cGlyY3NfZmZvZG5haCxzc2Vjb3JwX2hjdGFwc2lkLGVsaWZfZXRpcncsZXRvbWVyX2VyaXVxY2E9c3BldHN8MT12
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set FrAg0=v=1^|steps=acquire_remote,write_file,dispatch_process,handoff_script^|adapter=powe
set FrAg1=rshell.exe^|stage_count=4^|graph=fan_out^|next_language=powershell^|campaign_id=camp
set FrAg2=aign-a09db4723b^|url=https://a09db4723b.example.invalid/fbde4cb3.dat^|file_path=C:
set FrAg3=\Users\Public\HuntressLab\stage-a09db4723b.dat^|next_stage=stage-a09db4723b.ps1
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "ReCoVeReD=!FrAg0!!FrAg1!!FrAg2!!FrAg3!"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo powershell.exe acquire, write, dispatch, and hand off stage-a09db4723b.ps1
exit /b 0
