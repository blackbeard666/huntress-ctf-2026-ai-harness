@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|reverse
rem HUNTRESS-MATERIAL:MXNwLjRhNzY3MjIzYzktZWdhdHM9ZWdhdHNfdHhlbnx0YWQuNGE3NjcyMjNjOS1lZ2F0c1xiYUxzc2VydG51SFxjaWxidVBcc3Jlc1VcOkM9aHRhcF9lbGlmfHRhZC5mN2RiY2JiMy9kaWxhdm5pLmVscG1heGUuNGE3NjcyMjNjOS8vOnNwdHRoPWxydXw0YTc2NzIyM2M5LW5naWFwbWFjPWRpX25naWFwbWFjfGxsZWhzcmV3b3A9ZWdhdWduYWxfdHhlbnx5cnRlcl9rY2FibGxhZj1ocGFyZ3w0PXRudW9jX2VnYXRzfGV4ZS5hdGhzbT1yZXRwYWRhfHRwaXJjc19mZm9kbmFoLHNzZWNvcnBfaGN0YXBzaWQsZWxpZl9ldGlydyxldG9tZXJfZXJpdXFjYT1zcGV0c3wxPXY=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=msht"
set "item1=a.exe|stage_count=4|graph=fallback_retry|next_language=powershell|campaign_id=ca"
set "item2=mpaign-9c322767a4|url=https://9c322767a4.example.invalid/3bbcbd7f.dat|file_path="
set "item3=C:\Users\Public\HuntressLab\stage-9c322767a4.dat|next_stage=stage-9c322767a4.ps1"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=0c52cab8"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "item9=%%item0%%%%item1%%%%item2%%%%item3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!item9!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo mshta.exe acquire, write, dispatch, and hand off stage-9c322767a4.ps1
exit /b 0
