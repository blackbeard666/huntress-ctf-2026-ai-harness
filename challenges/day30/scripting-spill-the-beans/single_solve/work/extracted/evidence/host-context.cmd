@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|xor_5a
rem HUNTRESS-MATERIAL:=o2a4Mma8gzOix2dukSNycmPzUgLpUjMmo2a4Mma8gzOix2d00zM7oyN7kzZ+MTB00zM7oyN7kjJ/QTN0c2P9szL9QzO2UgLi8DNmMCKu8DKFETO7gjN2sDPnJjK7gSPms2ZuQzL1kTB/0zOukiJoUDPnhyPuoyO+sjJ0UzMusDKv0zM8QTN5UANo8iL/gid0UzMusDKv0zM8QTN5UwP+UTO/4zZpoyPukiJrdGL
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "FrAg0=v=1|steps=decode_configuration,return_config"
SeT "FrAg1=uration|adapter=for|stage_count=1|graph=fall"
SeT "FrAg2=back_retry|next_language=none|campaign_id=ca"
SeT "FrAg3=mpaign-68abf09b10|host_id=host-68abf09b10"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=d8202cfe"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "ReCoVeReD=%%FrAg0%%%%FrAg1%%%%FrAg2%%%%FrAg3%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-68abf09b10
exit /b 0
