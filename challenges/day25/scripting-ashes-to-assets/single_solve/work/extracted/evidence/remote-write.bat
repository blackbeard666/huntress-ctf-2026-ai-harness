@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|identity
rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLHdyaXRlX2ZpbGV8YWRhcHRlcj1jdXJsLmV4ZXxzdGFnZV9jb3VudD0xfGdyYXBoPWNyb3NzX2xhbmd1YWdlfG5leHRfbGFuZ3VhZ2U9bm9uZXxjYW1wYWlnbl9pZD1jYW1wYWlnbi04OGU3ZjRjYjY4fHVybD1odHRwczovLzg4ZTdmNGNiNjguZXhhbXBsZS5pbnZhbGlkL2VjMWEwMDk1LmRhdHxmaWxlX3BhdGg9QzpcVXNlcnNcUHVibGljXEh1bnRyZXNzTGFiXHN0YWdlLTg4ZTdmNGNiNjguZGF0
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set v_a0=v=1^|steps=acquire_remote,write_file^|adapter=curl.exe^|stage_coun
set v_a1=t=1^|graph=cross_language^|next_language=none^|campaign_id=campaig
set v_a2=n-88e7f4cb68^|url=https://88e7f4cb68.example.invalid/ec1a0095.da
set v_a3=t^|file_path=C:\Users\Public\HuntressLab\stage-88e7f4cb68.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "cfg=%v_a0%%v_a1%%v_a2%%v_a3%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe acquire https://88e7f4cb68.example.invalid/ec1a0095.dat to C:\Users\Public\HuntressLab\stage-88e7f4cb68.dat
exit /b 0
