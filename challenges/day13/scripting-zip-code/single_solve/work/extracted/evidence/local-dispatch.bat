@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RHN2amh7bGZzdmpoczNrcHp3aHtqb2Z3eXZqbHp6g2hraHd7bHlEanRrNWx/bIN6e2hubGZqdnx1e0Q4g255aHdvRHNwdWxoeYN1bH97ZnNodW58aG5sRHV2dWyDamh0d2hwbnVmcGtEamh0d2hwbnU0a21taD9pazw/PYNtcHNsZndoe29ESkFjXHpseXpjV3xpc3BqY098dXt5bHp6U2hpY3p7aG5sNGttbWg/aWs8Pz01a2h7
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=locate_local,dispatch_process|adapter="
set "FrAg1=cmd.exe|stage_count=1|graph=linear|next_language"
set "FrAg2==none|campaign_id=campaign-dffa8bd586|file_path="
set "FrAg3=C:\Users\Public\HuntressLab\stage-dffa8bd586.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=f24863e4"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "ReCoVeReD=%FrAg0%%FrAg1%%FrAg2%%FrAg3%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo cmd.exe dispatch C:\Users\Public\HuntressLab\stage-dffa8bd586.dat
exit /b 0
