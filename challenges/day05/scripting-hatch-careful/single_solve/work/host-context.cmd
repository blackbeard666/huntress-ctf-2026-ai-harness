@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGtsanZrbGZqdnVtcG58eWh7cHZ1M3lse3x5dWZqdnVtcG58eWh7cHZ1g2hraHd7bHlEbXZ5g3p7aG5sZmp2fHV7RDiDbnlod29EenB1bnNsg3Vsf3tmc2h1bnxobmxEdXZ1bINqaHR3aHBudWZwa0RqaHR3aHBudTQ3Om1AaWxpOWlqg292entmcGtEb3Z6ezQ3Om1AaWxpOWlq
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=decode_configuration,return_conf"
set "item1=iguration|adapter=for|stage_count=1|graph="
set "item2=single|next_language=none|campaign_id=camp"
set "item3=aign-03f9beb2bc|host_id=host-03f9beb2bc"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=750df499"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9=%item0%%item1%%item2%%item3%"
exit /b 0
:HUNTRESS_EMIT
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-03f9beb2bc
exit /b 0
