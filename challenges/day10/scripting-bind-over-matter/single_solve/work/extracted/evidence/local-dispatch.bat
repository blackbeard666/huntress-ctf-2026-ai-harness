@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|add_7
rem HUNTRESS-MATERIAL:7d4438837a7b6c777a4473766a687b6c6673766a6873336b707a77687b6a6f667779766a6c7a7a83686b68777b6c79447a7b68797b837a7b686e6c666a767c757b4438836e7968776f446d68737369686a7266796c7b798083756c7f7b667368756e7c686e6c447576756c836a68747768706e7566706b446a68747768706e7534373f6d693b3e3f696a6d836d70736c6677687b6f444a41635c7a6c797a63577c6973706a634f7c757b796c7a7a536869637a7b686e6c34373f6d693b3e3f696a6d356b687b
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set FrAg0=v=1^|steps=locate_local,dispatch_process^|adapter=st
set FrAg1=art^|stage_count=1^|graph=fallback_retry^|next_langua
set FrAg2=ge=none^|campaign_id=campaign-08fb478bcf^|file_path=
set FrAg3=C:\Users\Public\HuntressLab\stage-08fb478bcf.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=674f106d"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "ReCoVeReD=!FrAg0!!FrAg1!!FrAg2!!FrAg3!"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo start dispatch C:\Users\Public\HuntressLab\stage-08fb478bcf.dat
exit /b 0
