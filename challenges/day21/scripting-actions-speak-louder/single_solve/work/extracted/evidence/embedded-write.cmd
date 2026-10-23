@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGtsanZrbGZsdGlsa2tsazN+eXB7bGZtcHNsg2hraHd7bHlEbH93aHVrNWx/bIN6e2hubGZqdnx1e0Q4g255aHdvRG1odWZ2fHuDdWx/e2ZzaHVufGhubER1dnVsg2podHdocG51ZnBrRGpodHdocG51ND0/N0BqbWw/aj6DbXBzbGZ3aHtvREpBY1x6bHl6Y1d8aXNwamNPfHV7eWx6elNoaWN6e2hubDQ9PzdAam1sP2o+NWtoew==
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set item0=v=1^|steps=decode_embedded,write_file^|adapter=expa
set item1=nd.exe^|stage_count=1^|graph=fan_out^|next_language=
set item2=none^|campaign_id=campaign-6809cfe8c7^|file_path=C:
set item3=\Users\Public\HuntressLab\stage-6809cfe8c7.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=6e25223c"
set "item9=!item0!!item1!!item2!!item3!"
echo(!item9!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo expand.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-6809cfe8c7.dat
exit /b 0
