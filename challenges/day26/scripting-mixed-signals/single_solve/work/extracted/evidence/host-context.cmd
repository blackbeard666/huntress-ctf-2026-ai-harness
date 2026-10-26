@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesjKxt7Iyr7G3tzM0s7q5MLo0t7cWOTK6Ork3L7G3tzM0s7q5MLo0t7c+MLIwuDoyuR6xsLY2Pjm6MLOyr7G3urc6Hpi+M7kwuDQeubC2sq+2MLczurCzsr43Mrw6L7YwtzO6sLOynrc3tzK+MbC2uDC0s7cvtLIesbC2uDC0s7cWmbMyMjEcm5qYGD40N7m6L7SyHrQ3uboWmbMyMjEcm5qYGA=
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=decode_configuration,return_config"
set "h1=uration|adapter=call|stage_count=1|graph=sam"
set "h2=e_language|next_language=none|campaign_id=ca"
set "h3=mpaign-3fddb97500|host_id=host-3fddb97500"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=7d36d406"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg=!h0!!h1!!h2!!h3!"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-3fddb97500
exit /b 0
