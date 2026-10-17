@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:dGFkLmU5MzBlZTVhM2EtZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnxlOTMwZWU1YTNhLW5naWFwbWFjPWRpX25naWFwbWFjfGVub249ZWdhdWduYWxfdHhlbnx0dW9fbmFmPWhwYXJnfDE9dG51b2NfZWdhdHN8bGxhYz1yZXRwYWRhfHNzZWNvcnBfaGN0YXBzaWQsbGFjb2xfZXRhY29sPXNwZXRzfDE9dg==
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "fragment0=v=1|steps=locate_local,dispatch_process|adapter="
SeT "fragment1=call|stage_count=1|graph=fan_out|next_language=n"
SeT "fragment2=one|campaign_id=campaign-a3a5ee039e|file_path=C:"
SeT "fragment3=\Users\Public\HuntressLab\stage-a3a5ee039e.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=0fb763ac"
ver >nul
if errorlevel 1 exit /b 1
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo call dispatch C:\Users\Public\HuntressLab\stage-a3a5ee039e.dat
exit /b 0
