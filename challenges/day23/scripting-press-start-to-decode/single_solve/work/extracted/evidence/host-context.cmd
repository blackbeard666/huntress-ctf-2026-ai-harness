@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:reversed_text|add_7

rem HUNTRESS-MATERIAL:==Ab3o2N9kWb+kGb0sne29GRrBnZ7pndvNIb3o2N9kWb+kGb0Unbwh2d0hmaEtGcmVnbwh2d0hmaDyWd2VHRs5Ga85WdoNnZ79Hb1NIbuhGfuVHazZGb0hmeE92dolnbDiDR7VHf2pmZs5Ga7p3g5ZXbElHb7dHarh2g1ZHc7hWe85GctVndqZWd5x3esl3M1ZHc7hWe85GctVndqZGbrZnastGR6dHb7p3g4QUf

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "item0=v=1|steps=decode_configuration,return_confi"
set "item1=guration|adapter=for|stage_count=1|graph=sa"
set "item2=me_language|next_language=none|campaign_id="
set "item3=campaign-eb7fb60c0e|host_id=host-eb7fb60c0e"

goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE

rem no neutral statements

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9=!item0!!item1!!item2!!item3!"
exit /b 0
:HUNTRESS_EMIT

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo set HUNTRESS_HOST=host-eb7fb60c0e

exit /b 0

