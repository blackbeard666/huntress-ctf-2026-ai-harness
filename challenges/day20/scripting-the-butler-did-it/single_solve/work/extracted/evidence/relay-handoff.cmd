@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|reverse
rem HUNTRESS-MATERIAL:49.115.112.46.101.55.97.57.101.48.102.97.54.50.45.101.103.97.116.115.61.101.103.97.116.115.95.116.120.101.110.124.116.97.100.46.101.55.97.57.101.48.102.97.54.50.45.101.103.97.116.115.92.98.97.76.115.115.101.114.116.110.117.72.92.99.105.108.98.117.80.92.115.114.101.115.85.92.58.67.61.104.116.97.112.95.101.108.105.102.124.116.97.100.46.100.51.52.54.57.55.51.99.47.100.105.108.97.118.110.105.46.101.108.112.109.97.120.101.46.101.55.97.57.101.48.102.97.54.50.47.47.58.115.112.116.116.104.61.108.114.117.124.101.55.97.57.101.48.102.97.54.50.45.110.103.105.97.112.109.97.99.61.100.105.95.110.103.105.97.112.109.97.99.124.108.108.101.104.115.114.101.119.111.112.61.101.103.97.117.103.110.97.108.95.116.120.101.110.124.100.110.111.109.97.105.100.61.104.112.97.114.103.124.52.61.116.110.117.111.99.95.101.103.97.116.115.124.101.120.101.46.100.109.99.61.114.101.116.112.97.100.97.124.116.112.105.114.99.115.95.102.102.111.100.110.97.104.44.115.115.101.99.111.114.112.95.104.99.116.97.112.115.105.100.44.101.108.105.102.95.101.116.105.114.119.44.101.116.111.109.101.114.95.101.114.105.117.113.99.97.61.115.112.101.116.115.124.49.61.118
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=cm"& rem HUNTRESS quote compound
set "item1=d.exe|stage_count=4|graph=diamond|next_language=powershell|campaign_id=campaig"& rem HUNTRESS quote compound
set "item2=n-26af0e9a7e|url=https://26af0e9a7e.example.invalid/c379643d.dat|file_path=C:\"& rem HUNTRESS quote compound
set "item3=Users\Public\HuntressLab\stage-26af0e9a7e.dat|next_stage=stage-26af0e9a7e.ps1"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=bc1270e7"
ver >nul
if errorlevel 1 exit /b 1
set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo cmd.exe acquire, write, dispatch, and hand off stage-26af0e9a7e.ps1
exit /b 0
