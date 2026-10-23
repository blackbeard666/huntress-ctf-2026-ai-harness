@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|add_7
rem HUNTRESS-MATERIAL:125.68.56.131.122.123.108.119.122.68.115.118.106.104.123.108.102.115.118.106.104.115.51.107.112.122.119.104.123.106.111.102.119.121.118.106.108.122.122.131.104.107.104.119.123.108.121.68.106.104.115.115.131.122.123.104.110.108.102.106.118.124.117.123.68.56.131.110.121.104.119.111.68.122.104.116.108.102.115.104.117.110.124.104.110.108.131.117.108.127.123.102.115.104.117.110.124.104.110.108.68.117.118.117.108.131.106.104.116.119.104.112.110.117.102.112.107.68.106.104.116.119.104.112.110.117.52.59.61.106.104.59.64.62.64.107.58.131.109.112.115.108.102.119.104.123.111.68.74.65.99.92.122.108.121.122.99.87.124.105.115.112.106.99.79.124.117.123.121.108.122.122.83.104.105.99.122.123.104.110.108.52.59.61.106.104.59.64.62.64.107.58.53.107.104.123
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "fragment0=v=1|steps=locate_local,dispatch_process|adapter=c"
SeT "fragment1=all|stage_count=1|graph=same_language|next_langua"
SeT "fragment2=ge=none|campaign_id=campaign-46ca4979d3|file_path"
SeT "fragment3==C:\Users\Public\HuntressLab\stage-46ca4979d3.dat"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=e4c45228"
ver >nul
if errorlevel 1 exit /b 1
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo call dispatch C:\Users\Public\HuntressLab\stage-46ca4979d3.dat
exit /b 0
