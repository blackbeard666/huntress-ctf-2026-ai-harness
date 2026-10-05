@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|rotate_left
rem HUNTRESS-MATERIAL:ec7a62f8e6e8cae0e67ac2c6e2ead2e4cabee4cadadee8ca58eee4d2e8cabeccd2d8ca58c8d2e6e0c2e8c6d0bee0e4dec6cae6e658d0c2dcc8deccccbee6c6e4d2e0e8f8c2c8c2e0e8cae47adae6d0e8c25ccaf0caf8e6e8c2cecabec6deeadce87a68f8cee4c2e0d07ac8d2c2dadedcc8f8dccaf0e8bed8c2dcceeac2ceca7ae0deeecae4e6d0cad8d8f8c6c2dae0c2d2cedcbed2c87ac6c2dae0c2d2cedc5aca68606a6c68686060c2f8eae4d87ad0e8e8e0e6745e5eca68606a6c68686060c25ccaf0c2dae0d8ca5cd2dcecc2d8d2c85ec2607272666c6c625cc8c2e8f8ccd2d8cabee0c2e8d07a8674b8aae6cae4e6b8a0eac4d8d2c6b890eadce8e4cae6e698c2c4b8e6e8c2ceca5aca68606a6c68686060c25cc8c2e8f8dccaf0e8bee6e8c2ceca7ae6e8c2ceca5aca68606a6c68686060c25ce0e662
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "item0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=msh"
SeT "item1=ta.exe|stage_count=4|graph=diamond|next_language=powershell|campaign_id=campaig"
SeT "item2=n-e40564400a|url=https://e40564400a.example.invalid/a0993661.dat|file_path=C:\U"
SeT "item3=sers\Public\HuntressLab\stage-e40564400a.dat|next_stage=stage-e40564400a.ps1"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=487e6c91"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo mshta.exe acquire, write, dispatch, and hand off stage-e40564400a.ps1
exit /b 0
