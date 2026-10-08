@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|identity
rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLHdyaXRlX2ZpbGV8YWRhcHRlcj1jdXJsLmV4ZXxzdGFnZV9jb3VudD0xfGdyYXBoPXNhbWVfbGFuZ3VhZ2V8bmV4dF9sYW5ndWFnZT1ub25lfGNhbXBhaWduX2lkPWNhbXBhaWduLTY0OTI4NmIwNmN8dXJsPWh0dHBzOi8vNjQ5Mjg2YjA2Yy5leGFtcGxlLmludmFsaWQvNDg5MGMzZjcuZGF0fGZpbGVfcGF0aD1DOlxVc2Vyc1xQdWJsaWNcSHVudHJlc3NMYWJcc3RhZ2UtNjQ5Mjg2YjA2Yy5kYXQ=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=acquire_remote,write_file|adapter=curl.exe|stage_cou"& rem HUNTRESS quote compound
set "v_a1=nt=1|graph=same_language|next_language=none|campaign_id=campai"& rem HUNTRESS quote compound
set "v_a2=gn-649286b06c|url=https://649286b06c.example.invalid/4890c3f7."& rem HUNTRESS quote compound
set "v_a3=dat|file_path=C:\Users\Public\HuntressLab\stage-649286b06c.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=9ce5a69c"
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo curl.exe acquire https://649286b06c.example.invalid/4890c3f7.dat to C:\Users\Public\HuntressLab\stage-649286b06c.dat
exit /b 0
