@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|add_7
rem HUNTRESS-MATERIAL:7d4438837a7b6c777a44686a787c70796c66796c74767b6c337e79707b6c666d70736c336b707a77687b6a6f667779766a6c7a7a336f68756b766d6d667a6a7970777b83686b68777b6c7944797c756b73733a39356c7f6c837a7b686e6c666a767c757b443b836e7968776f446d68737369686a7266796c7b798083756c7f7b667368756e7c686e6c4477767e6c797a6f6c7373836a68747768706e7566706b446a68747768706e75343f6a40376b3938373c6b837c7973446f7b7b777a4136363f6a40376b3938373c6b356c7f687477736c3570757d6873706b363b6b6d3e6d6b393e356b687b836d70736c6677687b6f444a41635c7a6c797a63577c6973706a634f7c757b796c7a7a536869637a7b686e6c343f6a40376b3938373c6b356b687b83756c7f7b667a7b686e6c447a7b686e6c343f6a40376b3938373c6b35777a38
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=rundl"
set "item1=l32.exe|stage_count=4|graph=fallback_retry|next_language=powershell|campaign_id=c"
set "item2=ampaign-8c90d2105d|url=https://8c90d2105d.example.invalid/4df7fd27.dat|file_path="
set "item3=C:\Users\Public\HuntressLab\stage-8c90d2105d.dat|next_stage=stage-8c90d2105d.ps1"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=5dd2d099"
ver >nul
if errorlevel 1 exit /b 1
call set "item9=%%item0%%%%item1%%%%item2%%%%item3%%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo rundll32.exe acquire, write, dispatch, and hand off stage-8c90d2105d.ps1
exit /b 0
