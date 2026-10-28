@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:hex_pairs|xor_5a

rem HUNTRESS-MATERIAL:2c676b26292e3f2a29673635393b2e3f053635393b36763e33292a3b2e3932052a2835393f2929263b3e3b2a2e3f2867393b363626292e3b3d3f0539352f342e676b263d283b2a32673633343f3b2826343f222e05363b343d2f3b3d3f673435343f26393b372a3b333d3405333e67393b372a3b333d347769383f3b3f62683b693f263c33363f052a3b2e32671960060f293f2829060a2f3836333906122f342e283f2929163b3806292e3b3d3f7769383f3b3f62683b693f743e3b2e

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "item0=v=1|steps=locate_local,dispatch_process|adapter="
set "item1=call|stage_count=1|graph=linear|next_language=no"
set "item2=ne|campaign_id=campaign-3beae82a3e|file_path=C:\"
set "item3=Users\Public\HuntressLab\stage-3beae82a3e.dat"

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

set "neutral_dead_label=60f19312"

call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"
exit /b 0
:HUNTRESS_EMIT

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo call dispatch C:\Users\Public\HuntressLab\stage-3beae82a3e.dat

exit /b 0

