@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGtsanZrbGZqdnVtcG58eWh7cHZ1M3lse3x5dWZqdnVtcG58eWh7cHZ1g2hraHd7bHlEamhzc4N6e2hubGZqdnx1e0Q4g255aHdvRHpodGxmc2h1bnxobmyDdWx/e2ZzaHVufGhubER1dnVsg2podHdocG51ZnBrRGpodHdocG51NGk8O2g9PWk6PTiDb3Z6e2Zwa0Rvdnp7NGk8O2g9PWk6PTg=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=decode_configuration,return_config"& rem HUNTRESS quote compound
set "FrAg1=uration|adapter=call|stage_count=1|graph=sam"& rem HUNTRESS quote compound
set "FrAg2=e_language|next_language=none|campaign_id=ca"& rem HUNTRESS quote compound
set "FrAg3=mpaign-b54a66b361|host_id=host-b54a66b361"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=57a00e63"
ver >nul
if errorlevel 1 exit /b 1
call set "ReCoVeReD=%%FrAg0%%%%FrAg1%%%%FrAg2%%%%FrAg3%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-b54a66b361
exit /b 0
