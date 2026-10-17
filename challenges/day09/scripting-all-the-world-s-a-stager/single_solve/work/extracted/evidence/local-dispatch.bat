@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|add_7
rem HUNTRESS-MATERIAL:7d4438837a7b6c777a4473766a687b6c6673766a6873336b707a77687b6a6f667779766a6c7a7a83686b68777b6c79446a687373837a7b686e6c666a767c757b4438836e7968776f446d68737369686a7266796c7b798083756c7f7b667368756e7c686e6c447576756c836a68747768706e7566706b446a68747768706e75343f6b6b3f6a37683c6c6a836d70736c6677687b6f444a41635c7a6c797a63577c6973706a634f7c757b796c7a7a536869637a7b686e6c343f6b6b3f6a37683c6c6a356b687b
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=locate_local,dispatch_process|adapter=ca"
set "item1=ll|stage_count=1|graph=fallback_retry|next_languag"
set "item2=e=none|campaign_id=campaign-8dd8c0a5ec|file_path=C"
set "item3=:\Users\Public\HuntressLab\stage-8dd8c0a5ec.dat"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=268bf7e4"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "item9=%%item0%%%%item1%%%%item2%%%%item3%%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo call dispatch C:\Users\Public\HuntressLab\stage-8dd8c0a5ec.dat
exit /b 0
