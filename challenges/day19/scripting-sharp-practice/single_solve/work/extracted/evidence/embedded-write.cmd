@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGtsanZrbGZsdGlsa2tsazN+eXB7bGZtcHNsg2hraHd7bHlEbH97eWhqOjk1bH9sg3p7aG5sZmp2fHV7RDiDbnlod29EbWhzc2loanJmeWx7eYCDdWx/e2ZzaHVufGhubER1dnVsg2podHdocG51ZnBrRGpodHdocG51NGltPzxtPWhrPmuDbXBzbGZ3aHtvREpBY1x6bHl6Y1d8aXNwamNPfHV7eWx6elNoaWN6e2hubDRpbT88bT1oaz5rNWtoew==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "h0=v=1|steps=decode_embedded,write_file|adapter=extrac"
SeT "h1=32.exe|stage_count=1|graph=fallback_retry|next_lang"
SeT "h2=uage=none|campaign_id=campaign-bf85f6ad7d|file_path"
SeT "h3==C:\Users\Public\HuntressLab\stage-bf85f6ad7d.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=62440bb4"
call set "cfg=%%h0%%%%h1%%%%h2%%%%h3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo extrac32.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-bf85f6ad7d.dat
exit /b 0
