@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGtsanZrbGZqdnVtcG58eWh7cHZ1M3lse3x5dWZqdnVtcG58eWh7cHZ1g2hraHd7bHlEbXZ5g3p7aG5sZmp2fHV7RDiDbnlod29EenB1bnNsg3Vsf3tmc2h1bnxobmxEdXZ1bINqaHR3aHBudWZwa0RqaHR3aHBudTRtPDpsbTg3aTg+g292entmcGtEb3Z6ezRtPDpsbTg3aTg+
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set FrAg0=v=1^|steps=decode_configuration,return_conf
set FrAg1=iguration^|adapter=for^|stage_count=1^|graph=
set FrAg2=single^|next_language=none^|campaign_id=camp
set FrAg3=aign-f53ef10b17^|host_id=host-f53ef10b17
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=aa343068"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "ReCoVeReD=!FrAg0!!FrAg1!!FrAg2!!FrAg3!"
exit /b 0
:HUNTRESS_EMIT
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-f53ef10b17
exit /b 0
