@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|identity
rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWRlY29kZV9lbWJlZGRlZCx3cml0ZV9maWxlfGFkYXB0ZXI9ZXhwYW5kLmV4ZXxzdGFnZV9jb3VudD0xfGdyYXBoPXNpbmdsZXxuZXh0X2xhbmd1YWdlPW5vbmV8Y2FtcGFpZ25faWQ9Y2FtcGFpZ24tMDJlNDNmMGM1N3xmaWxlX3BhdGg9QzpcVXNlcnNcUHVibGljXEh1bnRyZXNzTGFiXHN0YWdlLTAyZTQzZjBjNTcuZGF0
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=decode_embedded,write_file|adapter=exp"& rem HUNTRESS quote compound
set "v_a1=and.exe|stage_count=1|graph=single|next_language"& rem HUNTRESS quote compound
set "v_a2==none|campaign_id=campaign-02e43f0c57|file_path="& rem HUNTRESS quote compound
set "v_a3=C:\Users\Public\HuntressLab\stage-02e43f0c57.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=175c2e84"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "cfg=%v_a0%%v_a1%%v_a2%%v_a3%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo expand.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-02e43f0c57.dat
exit /b 0
