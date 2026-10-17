@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:MjQ3NDY5ZWIyYi10c29oPWRpX3Rzb2h8MjQ3NDY5ZWIyYi1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xlbm9uPWVnYXVnbmFsX3R4ZW58dHVvX25hZj1ocGFyZ3wxPXRudW9jX2VnYXRzfHJvZj1yZXRwYWRhfG5vaXRhcnVnaWZub2NfbnJ1dGVyLG5vaXRhcnVnaWZub2NfZWRvY2VkPXNwZXRzfDE9dg==
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=decode_configuration,return_conf"& rem HUNTRESS quote compound
set "item1=iguration|adapter=for|stage_count=1|graph="& rem HUNTRESS quote compound
set "item2=fan_out|next_language=none|campaign_id=cam"& rem HUNTRESS quote compound
set "item3=paign-b2be964742|host_id=host-b2be964742"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=169f9e4b"
call set "item9=%%item0%%%%item1%%%%item2%%%%item3%%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-b2be964742
exit /b 0
