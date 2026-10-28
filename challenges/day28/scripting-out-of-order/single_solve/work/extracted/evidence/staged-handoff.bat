@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|add_7
rem HUNTRESS-MATERIAL:125.68.56.131.122.123.108.119.122.68.104.106.120.124.112.121.108.102.121.108.116.118.123.108.51.126.121.112.123.108.102.109.112.115.108.51.107.112.122.119.104.123.106.111.102.119.121.118.106.108.122.122.51.111.104.117.107.118.109.109.102.122.106.121.112.119.123.131.104.107.104.119.123.108.121.68.119.118.126.108.121.122.111.108.115.115.53.108.127.108.131.122.123.104.110.108.102.106.118.124.117.123.68.59.131.110.121.104.119.111.68.107.112.104.116.118.117.107.131.117.108.127.123.102.115.104.117.110.124.104.110.108.68.119.118.126.108.121.122.111.108.115.115.131.106.104.116.119.104.112.110.117.102.112.107.68.106.104.116.119.104.112.110.117.52.61.58.109.58.109.109.106.105.63.108.131.124.121.115.68.111.123.123.119.122.65.54.54.61.58.109.58.109.109.106.105.63.108.53.108.127.104.116.119.115.108.53.112.117.125.104.115.112.107.54.108.63.108.107.63.55.104.62.53.107.104.123.131.109.112.115.108.102.119.104.123.111.68.74.65.99.92.122.108.121.122.99.87.124.105.115.112.106.99.79.124.117.123.121.108.122.122.83.104.105.99.122.123.104.110.108.52.61.58.109.58.109.109.106.105.63.108.53.107.104.123.131.117.108.127.123.102.122.123.104.110.108.68.122.123.104.110.108.52.61.58.109.58.109.109.106.105.63.108.53.119.122.56
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "item0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=powe"
SeT "item1=rshell.exe|stage_count=4|graph=diamond|next_language=powershell|campaign_id=camp"
SeT "item2=aign-63f3ffcb8e|url=https://63f3ffcb8e.example.invalid/e8ed80a7.dat|file_path=C:"
SeT "item3=\Users\Public\HuntressLab\stage-63f3ffcb8e.dat|next_stage=stage-63f3ffcb8e.ps1"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=254d5500"
set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo powershell.exe acquire, write, dispatch, and hand off stage-63f3ffcb8e.ps1
exit /b 0
