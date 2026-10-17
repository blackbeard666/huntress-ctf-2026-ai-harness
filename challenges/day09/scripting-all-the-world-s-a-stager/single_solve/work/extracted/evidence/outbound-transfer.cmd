@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|identity
rem HUNTRESS-MATERIAL:118.61.49.124.115.116.101.112.115.61.108.111.99.97.116.101.95.108.111.99.97.108.44.112.114.101.112.97.114.101.95.116.114.97.110.115.102.101.114.44.117.112.108.111.97.100.95.114.101.109.111.116.101.124.97.100.97.112.116.101.114.61.109.97.107.101.99.97.98.46.101.120.101.124.115.116.97.103.101.95.99.111.117.110.116.61.49.124.103.114.97.112.104.61.115.105.110.103.108.101.124.110.101.120.116.95.108.97.110.103.117.97.103.101.61.110.111.110.101.124.99.97.109.112.97.105.103.110.95.105.100.61.99.97.109.112.97.105.103.110.45.57.100.48.57.97.56.99.101.55.51.124.115.111.117.114.99.101.95.112.97.116.104.61.67.58.92.85.115.101.114.115.92.80.117.98.108.105.99.92.72.117.110.116.114.101.115.115.76.97.98.92.99.111.108.108.101.99.116.45.57.100.48.57.97.56.99.101.55.51.46.99.97.98.124.117.112.108.111.97.100.95.117.114.108.61.104.116.116.112.115.58.47.47.57.100.48.57.97.56.99.101.55.51.46.101.120.97.109.112.108.101.46.105.110.118.97.108.105.100.47.117.112.108.111.97.100
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=makec"& rem HUNTRESS quote compound
set "FrAg1=ab.exe|stage_count=1|graph=single|next_language=none|campaign_id=ca"& rem HUNTRESS quote compound
set "FrAg2=mpaign-9d09a8ce73|source_path=C:\Users\Public\HuntressLab\collect-9"& rem HUNTRESS quote compound
set "FrAg3=d09a8ce73.cab|upload_url=https://9d09a8ce73.example.invalid/upload"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=cb06806b"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "ReCoVeReD="
for %%G in (0 1 2 3) do call set "ReCoVeReD=%%ReCoVeReD%%%%FrAg%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo makecab.exe upload C:\Users\Public\HuntressLab\collect-9d09a8ce73.cab to https://9d09a8ce73.example.invalid/upload
exit /b 0
