@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:plain_fragments|rotate_left

rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesjKxt7Iyr7G3tzM0s7q5MLo0t7cWOTK6Ork3L7G3tzM0s7q5MLo0t7c+MLIwuDoyuR6zN7k+Obows7Kvsbe6tzoemL4zuTC4NB6zMLY2MTCxta+5Mro5PL43Mrw6L7YwtzO6sLOynrc3tzK+MbC2uDC0s7cvtLIesbC2uDC0s7cWnDGcmxuYGDExmL40N7m6L7SyHrQ3uboWnDGcmxuYGDExmI=

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set fragment0=v=1^|steps=decode_configuration,return_config
set fragment1=uration^|adapter=for^|stage_count=1^|graph=fall
set fragment2=back_retry^|next_language=none^|campaign_id=ca
set fragment3=mpaign-8c96700bc1^|host_id=host-8c96700bc1

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_dead_label=6cf46a71"

ver >nul
if errorlevel 1 exit /b 1
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"

echo(!recovered_configuration!

exit /b 0

:HUNTRESS_PLAN

echo set HUNTRESS_HOST=host-8c96700bc1

exit /b 0

