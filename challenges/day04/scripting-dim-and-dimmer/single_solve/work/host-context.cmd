@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|reverse
rem HUNTRESS-MATERIAL:MzZkNzEzYTRlMC10c29oPWRpX3Rzb2h8MzZkNzEzYTRlMC1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xlbm9uPWVnYXVnbmFsX3R4ZW58ZG5vbWFpZD1ocGFyZ3wxPXRudW9jX2VnYXRzfHRlcz1yZXRwYWRhfG5vaXRhcnVnaWZub2NfbnJ1dGVyLG5vaXRhcnVnaWZub2NfZWRvY2VkPXNwZXRzfDE9dg==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=decode_configuration,return_conf"& rem HUNTRESS quote compound
set "fragment1=iguration|adapter=set|stage_count=1|graph="& rem HUNTRESS quote compound
set "fragment2=diamond|next_language=none|campaign_id=cam"& rem HUNTRESS quote compound
set "fragment3=paign-0e4a317d63|host_id=host-0e4a317d63"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=f25e750a"
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-0e4a317d63
exit /b 0
