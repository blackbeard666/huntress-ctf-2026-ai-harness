@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|identity
rem HUNTRESS-MATERIAL:118.61.49.124.115.116.101.112.115.61.97.99.113.117.105.114.101.95.114.101.109.111.116.101.44.119.114.105.116.101.95.102.105.108.101.44.100.105.115.112.97.116.99.104.95.112.114.111.99.101.115.115.44.104.97.110.100.111.102.102.95.115.99.114.105.112.116.124.97.100.97.112.116.101.114.61.114.101.103.115.118.114.51.50.46.101.120.101.124.115.116.97.103.101.95.99.111.117.110.116.61.52.124.103.114.97.112.104.61.100.105.97.109.111.110.100.124.110.101.120.116.95.108.97.110.103.117.97.103.101.61.112.111.119.101.114.115.104.101.108.108.124.99.97.109.112.97.105.103.110.95.105.100.61.99.97.109.112.97.105.103.110.45.48.54.52.50.51.97.53.97.52.50.124.117.114.108.61.104.116.116.112.115.58.47.47.48.54.52.50.51.97.53.97.52.50.46.101.120.97.109.112.108.101.46.105.110.118.97.108.105.100.47.48.97.54.56.52.100.49.97.46.100.97.116.124.102.105.108.101.95.112.97.116.104.61.67.58.92.85.115.101.114.115.92.80.117.98.108.105.99.92.72.117.110.116.114.101.115.115.76.97.98.92.115.116.97.103.101.45.48.54.52.50.51.97.53.97.52.50.46.100.97.116.124.110.101.120.116.95.115.116.97.103.101.61.115.116.97.103.101.45.48.54.52.50.51.97.53.97.52.50.46.112.115.49
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=reg"& rem HUNTRESS quote compound
set "item1=svr32.exe|stage_count=4|graph=diamond|next_language=powershell|campaign_id=camp"& rem HUNTRESS quote compound
set "item2=aign-06423a5a42|url=https://06423a5a42.example.invalid/0a684d1a.dat|file_path=C"& rem HUNTRESS quote compound
set "item3=:\Users\Public\HuntressLab\stage-06423a5a42.dat|next_stage=stage-06423a5a42.ps1"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=c2ce20c2"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "item9=%%item0%%%%item1%%%%item2%%%%item3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo regsvr32.exe acquire, write, dispatch, and hand off stage-06423a5a42.ps1
exit /b 0
