@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:hex_pairs|xor_5a

rem HUNTRESS-MATERIAL:2c676b26292e3f2a29673635393b2e3f053635393b36763e33292a3b2e3932052a2835393f2929263b3e3b2a2e3f286739373e743f223f26292e3b3d3f0539352f342e676b263d283b2a32673c3b3636383b393105283f2e282326343f222e05363b343d2f3b3d3f673435343f26393b372a3b333d3405333e67393b372a3b333d3477696e39633c6e3f636a3e263c33363f052a3b2e32671960060f293f2829060a2f3836333906122f342e283f2929163b3806292e3b3d3f77696e39633c6e3f636a3e743e3b2e

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

SeT "item0=v=1|steps=locate_local,dispatch_process|adapter=cm"
SeT "item1=d.exe|stage_count=1|graph=fallback_retry|next_lang"
SeT "item2=uage=none|campaign_id=campaign-34c9f4e90d|file_pat"
SeT "item3=h=C:\Users\Public\HuntressLab\stage-34c9f4e90d.dat"

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_dead_label=f079d154"

ver >nul
if errorlevel 1 exit /b 1
set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo cmd.exe dispatch C:\Users\Public\HuntressLab\stage-34c9f4e90d.dat

exit /b 0

