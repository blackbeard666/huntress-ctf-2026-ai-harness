@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|reverse
rem HUNTRESS-MATERIAL:116.97.100.46.57.99.99.57.98.53.56.100.99.50.45.101.103.97.116.115.92.98.97.76.115.115.101.114.116.110.117.72.92.99.105.108.98.117.80.92.115.114.101.115.85.92.58.67.61.104.116.97.112.95.101.108.105.102.124.57.99.99.57.98.53.56.100.99.50.45.110.103.105.97.112.109.97.99.61.100.105.95.110.103.105.97.112.109.97.99.124.101.110.111.110.61.101.103.97.117.103.110.97.108.95.116.120.101.110.124.101.103.97.117.103.110.97.108.95.101.109.97.115.61.104.112.97.114.103.124.49.61.116.110.117.111.99.95.101.103.97.116.115.124.108.108.97.99.61.114.101.116.112.97.100.97.124.115.115.101.99.111.114.112.95.104.99.116.97.112.115.105.100.44.108.97.99.111.108.95.101.116.97.99.111.108.61.115.112.101.116.115.124.49.61.118
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "h0=v=1|steps=locate_local,dispatch_process|adapter=c"
SeT "h1=all|stage_count=1|graph=same_language|next_langua"
SeT "h2=ge=none|campaign_id=campaign-2cd85b9cc9|file_path"
SeT "h3==C:\Users\Public\HuntressLab\stage-2cd85b9cc9.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=a52f3808"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo call dispatch C:\Users\Public\HuntressLab\stage-2cd85b9cc9.dat
exit /b 0
