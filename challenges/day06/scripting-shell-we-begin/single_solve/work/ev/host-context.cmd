@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|identity
rem HUNTRESS-MATERIAL:763d317c73746570733d6465636f64655f636f6e66696775726174696f6e2c72657475726e5f636f6e66696775726174696f6e7c616461707465723d63616c6c7c73746167655f636f756e743d317c67726170683d6c696e6561727c6e6578745f6c616e67756167653d6e6f6e657c63616d706169676e5f69643d63616d706169676e2d616130633032373262617c686f73745f69643d686f73742d61613063303237326261
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "item0=v=1|steps=decode_configuration,return_conf"
SeT "item1=iguration|adapter=call|stage_count=1|graph"
SeT "item2==linear|next_language=none|campaign_id=cam"
SeT "item3=paign-aa0c0272ba|host_id=host-aa0c0272ba"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=f5a588f5"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!item9!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-aa0c0272ba
exit /b 0
