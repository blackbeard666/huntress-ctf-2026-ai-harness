@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|add_7
rem HUNTRESS-MATERIAL:==weotWN/4DO+AkO+gzOrRDbuh2e6NWaoNle6xWe7VHfPNmawNXa8d1Y6lHb6x1YBpERvtHa3ZGbzBXbD+jP44DQ64DO7sGN15GcodHdopGRrBnZ15GcodHdop2gsVnd1REbuhGfuVHazZ2e/xWdDuHf2ZWdo1GRvdHa552g4Q0e1xndqZGbuh2e6NIb/xWNrVHa39HbElHb7dHarh2gsNHctZGb7BXe+Nzast2aslGdsZGbrZnastGR6dHb7p3g4QUf
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=decode_embedded,write_file|adapter=expa"& rem HUNTRESS quote compound
set "fragment1=nd.exe|stage_count=1|graph=fan_out|next_language="& rem HUNTRESS quote compound
set "fragment2=none|campaign_id=campaign-d417397178|file_path=C:"& rem HUNTRESS quote compound
set "fragment3=\Users\Public\HuntressLab\stage-d417397178.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=e0f8c976"
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo expand.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-d417397178.dat
exit /b 0
