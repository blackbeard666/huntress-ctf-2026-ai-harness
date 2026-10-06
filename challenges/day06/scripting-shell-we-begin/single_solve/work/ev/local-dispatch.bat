@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|reverse_xor
rem HUNTRESS-MATERIAL:71.82.87.29.3.5.11.5.11.1.1.85.85.81.30.86.84.82.71.64.111.81.82.127.64.64.86.65.71.93.70.123.111.80.90.95.81.70.99.111.64.65.86.64.102.111.9.112.14.91.71.82.67.108.86.95.90.85.79.3.5.11.5.11.1.1.85.85.81.30.93.84.90.82.67.94.82.80.14.87.90.108.93.84.90.82.67.94.82.80.79.86.93.92.93.14.86.84.82.70.84.93.82.95.108.71.75.86.93.79.74.65.71.86.65.108.88.80.82.81.95.95.82.85.14.91.67.82.65.84.79.2.14.71.93.70.92.80.108.86.84.82.71.64.79.95.95.82.80.14.65.86.71.67.82.87.82.79.64.64.86.80.92.65.67.108.91.80.71.82.67.64.90.87.31.95.82.80.92.95.108.86.71.82.80.92.95.14.64.67.86.71.64.79.2.14.69
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=locate_local,dispatch_process|adapter=ca"
set "item1=ll|stage_count=1|graph=fallback_retry|next_languag"
set "item2=e=none|campaign_id=campaign-bff2286860|file_path=C"
set "item3=:\Users\Public\HuntressLab\stage-bff2286860.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=e091192e"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo call dispatch C:\Users\Public\HuntressLab\stage-bff2286860.dat
exit /b 0
