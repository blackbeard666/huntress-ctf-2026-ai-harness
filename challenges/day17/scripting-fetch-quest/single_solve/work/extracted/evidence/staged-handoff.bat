@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|xor_5a
rem HUNTRESS-MATERIAL:44.103.107.38.41.46.63.42.41.103.59.57.43.47.51.40.63.5.40.63.55.53.46.63.118.45.40.51.46.63.5.60.51.54.63.118.62.51.41.42.59.46.57.50.5.42.40.53.57.63.41.41.118.50.59.52.62.53.60.60.5.41.57.40.51.42.46.38.59.62.59.42.46.63.40.103.42.53.45.63.40.41.50.63.54.54.116.63.34.63.38.41.46.59.61.63.5.57.53.47.52.46.103.110.38.61.40.59.42.50.103.62.51.59.55.53.52.62.38.52.63.34.46.5.54.59.52.61.47.59.61.63.103.42.53.45.63.40.41.50.63.54.54.38.57.59.55.42.59.51.61.52.5.51.62.103.57.59.55.42.59.51.61.52.119.59.105.56.57.110.98.56.104.110.99.38.47.40.54.103.50.46.46.42.41.96.117.117.59.105.56.57.110.98.56.104.110.99.116.63.34.59.55.42.54.63.116.51.52.44.59.54.51.62.117.106.98.63.59.99.60.63.104.116.62.59.46.38.60.51.54.63.5.42.59.46.50.103.25.96.6.15.41.63.40.41.6.10.47.56.54.51.57.6.18.47.52.46.40.63.41.41.22.59.56.6.41.46.59.61.63.119.59.105.56.57.110.98.56.104.110.99.116.62.59.46.38.52.63.34.46.5.41.46.59.61.63.103.41.46.59.61.63.119.59.105.56.57.110.98.56.104.110.99.116.42.41.107
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set fragment0=v=1^|steps=acquire_remote,write_file,dispatch_process,handoff_script^|adapter=powe
set fragment1=rshell.exe^|stage_count=4^|graph=diamond^|next_language=powershell^|campaign_id=camp
set fragment2=aign-a3bc48b249^|url=https://a3bc48b249.example.invalid/08ea9fe2.dat^|file_path=C:
set fragment3=\Users\Public\HuntressLab\stage-a3bc48b249.dat^|next_stage=stage-a3bc48b249.ps1
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=75f6df3d"
ver >nul
if errorlevel 1 exit /b 1
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo powershell.exe acquire, write, dispatch, and hand off stage-a3bc48b249.ps1
exit /b 0
