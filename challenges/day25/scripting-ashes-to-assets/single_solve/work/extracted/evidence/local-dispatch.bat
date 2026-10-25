@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|reverse
rem HUNTRESS-MATERIAL:116.97.100.46.102.55.50.52.54.54.49.99.51.55.45.101.103.97.116.115.92.98.97.76.115.115.101.114.116.110.117.72.92.99.105.108.98.117.80.92.115.114.101.115.85.92.58.67.61.104.116.97.112.95.101.108.105.102.124.102.55.50.52.54.54.49.99.51.55.45.110.103.105.97.112.109.97.99.61.100.105.95.110.103.105.97.112.109.97.99.124.101.110.111.110.61.101.103.97.117.103.110.97.108.95.116.120.101.110.124.121.114.116.101.114.95.107.99.97.98.108.108.97.102.61.104.112.97.114.103.124.49.61.116.110.117.111.99.95.101.103.97.116.115.124.116.114.97.116.115.61.114.101.116.112.97.100.97.124.115.115.101.99.111.114.112.95.104.99.116.97.112.115.105.100.44.108.97.99.111.108.95.101.116.97.99.111.108.61.115.112.101.116.115.124.49.61.118
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=locate_local,dispatch_process|adapter=st"
set "fragment1=art|stage_count=1|graph=fallback_retry|next_langua"
set "fragment2=ge=none|campaign_id=campaign-73c166427f|file_path="
set "fragment3=C:\Users\Public\HuntressLab\stage-73c166427f.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=756d1ed1"
ver >nul
if errorlevel 1 exit /b 1
set "recovered_configuration=!fragment0!!fragment1!!fragment2!!fragment3!"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo start dispatch C:\Users\Public\HuntressLab\stage-73c166427f.dat
exit /b 0
