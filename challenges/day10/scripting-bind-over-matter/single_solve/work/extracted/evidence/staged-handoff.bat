@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|identity
rem HUNTRESS-MATERIAL:118.61.49.124.115.116.101.112.115.61.97.99.113.117.105.114.101.95.114.101.109.111.116.101.44.119.114.105.116.101.95.102.105.108.101.44.100.105.115.112.97.116.99.104.95.112.114.111.99.101.115.115.44.104.97.110.100.111.102.102.95.115.99.114.105.112.116.124.97.100.97.112.116.101.114.61.99.115.99.114.105.112.116.46.101.120.101.124.115.116.97.103.101.95.99.111.117.110.116.61.52.124.103.114.97.112.104.61.115.97.109.101.95.108.97.110.103.117.97.103.101.124.110.101.120.116.95.108.97.110.103.117.97.103.101.61.98.97.116.99.104.124.99.97.109.112.97.105.103.110.95.105.100.61.99.97.109.112.97.105.103.110.45.99.50.99.49.56.48.57.49.102.97.124.117.114.108.61.104.116.116.112.115.58.47.47.99.50.99.49.56.48.57.49.102.97.46.101.120.97.109.112.108.101.46.105.110.118.97.108.105.100.47.52.57.101.50.57.56.50.48.46.100.97.116.124.102.105.108.101.95.112.97.116.104.61.67.58.92.85.115.101.114.115.92.80.117.98.108.105.99.92.72.117.110.116.114.101.115.115.76.97.98.92.115.116.97.103.101.45.99.50.99.49.56.48.57.49.102.97.46.100.97.116.124.110.101.120.116.95.115.116.97.103.101.61.115.116.97.103.101.45.99.50.99.49.56.48.57.49.102.97.46.99.109.100
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set fragment0=v=1^|steps=acquire_remote,write_file,dispatch_process,handoff_script^|adapter=csc
set fragment1=ript.exe^|stage_count=4^|graph=same_language^|next_language=batch^|campaign_id=camp
set fragment2=aign-c2c18091fa^|url=https://c2c18091fa.example.invalid/49e29820.dat^|file_path=C
set fragment3=:\Users\Public\HuntressLab\stage-c2c18091fa.dat^|next_stage=stage-c2c18091fa.cmd
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=005c2294"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration=!fragment0!!fragment1!!fragment2!!fragment3!"
exit /b 0
:HUNTRESS_EMIT
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo cscript.exe acquire, write, dispatch, and hand off stage-c2c18091fa.cmd
exit /b 0
