@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|reverse
rem HUNTRESS-MATERIAL:115.106.46.55.101.54.102.54.57.48.48.55.48.45.101.103.97.116.115.61.101.103.97.116.115.95.116.120.101.110.124.116.97.100.46.55.101.54.102.54.57.48.48.55.48.45.101.103.97.116.115.92.98.97.76.115.115.101.114.116.110.117.72.92.99.105.108.98.117.80.92.115.114.101.115.85.92.58.67.61.104.116.97.112.95.101.108.105.102.124.116.97.100.46.52.97.53.53.99.51.50.51.47.100.105.108.97.118.110.105.46.101.108.112.109.97.120.101.46.55.101.54.102.54.57.48.48.55.48.47.47.58.115.112.116.116.104.61.108.114.117.124.55.101.54.102.54.57.48.48.55.48.45.110.103.105.97.112.109.97.99.61.100.105.95.110.103.105.97.112.109.97.99.124.116.112.105.114.99.115.106.61.101.103.97.117.103.110.97.108.95.116.120.101.110.124.101.103.97.117.103.110.97.108.95.115.115.111.114.99.61.104.112.97.114.103.124.52.61.116.110.117.111.99.95.101.103.97.116.115.124.101.120.101.46.108.108.101.104.115.114.101.119.111.112.61.114.101.116.112.97.100.97.124.116.112.105.114.99.115.95.102.102.111.100.110.97.104.44.115.115.101.99.111.114.112.95.104.99.116.97.112.115.105.100.44.101.108.105.102.95.101.116.105.114.119.44.101.116.111.109.101.114.95.101.114.105.117.113.99.97.61.115.112.101.116.115.124.49.61.118
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=power"& rem HUNTRESS quote compound
set "v_a1=shell.exe|stage_count=4|graph=cross_language|next_language=jscript|campaign_id=ca"& rem HUNTRESS quote compound
set "v_a2=mpaign-070096f6e7|url=https://070096f6e7.example.invalid/323c55a4.dat|file_path=C"& rem HUNTRESS quote compound
set "v_a3=:\Users\Public\HuntressLab\stage-070096f6e7.dat|next_stage=stage-070096f6e7.js"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=227f81ba"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo powershell.exe acquire, write, dispatch, and hand off stage-070096f6e7.js
exit /b 0
