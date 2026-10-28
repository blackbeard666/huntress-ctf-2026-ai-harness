@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:split_fragments|rotate_left

rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesjKxt7Iyr7G3tzM0s7q5MLo0t7cWOTK6Ork3L7G3tzM0s7q5MLo0t7c+MLIwuDoyuR6xsLY2Pjm6MLOyr7G3urc6Hpi+M7kwuDQesjSwtre3Mj43Mrw6L7YwtzO6sLOynrc3tzK+MbC2uDC0s7cvtLIesbC2uDC0s7cWspyZmzIcsjIbsT40N7m6L7SyHrQ3uboWspyZmzIcsjIbsQ=

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "FrAg0=v=1|steps=decode_configuration,return_conf"& rem HUNTRESS quote compound
set "FrAg1=iguration|adapter=call|stage_count=1|graph"& rem HUNTRESS quote compound
set "FrAg2==diamond|next_language=none|campaign_id=ca"& rem HUNTRESS quote compound
set "FrAg3=mpaign-e936d9dd7b|host_id=host-e936d9dd7b"& rem HUNTRESS quote compound

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

rem no neutral statements

ver >nul
if errorlevel 1 exit /b 1
set "ReCoVeReD=%FrAg0%%FrAg1%%FrAg2%%FrAg3%"

echo(!ReCoVeReD!

exit /b 0

:HUNTRESS_PLAN

echo set HUNTRESS_HOST=host-e936d9dd7b

exit /b 0

