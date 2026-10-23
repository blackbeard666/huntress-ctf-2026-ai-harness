@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:base64_literal|identity

rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWRlY29kZV9lbWJlZGRlZCx3cml0ZV9maWxlfGFkYXB0ZXI9ZXh0cmFjMzIuZXhlfHN0YWdlX2NvdW50PTF8Z3JhcGg9ZmFuX291dHxuZXh0X2xhbmd1YWdlPW5vbmV8Y2FtcGFpZ25faWQ9Y2FtcGFpZ24tMGIzYjhhZTg3NHxmaWxlX3BhdGg9QzpcVXNlcnNcUHVibGljXEh1bnRyZXNzTGFiXHN0YWdlLTBiM2I4YWU4NzQuZGF0

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set h0=v=1^|steps=decode_embedded,write_file^|adapter=extr
set h1=ac32.exe^|stage_count=1^|graph=fan_out^|next_languag
set h2=e=none^|campaign_id=campaign-0b3b8ae874^|file_path=
set h3=C:\Users\Public\HuntressLab\stage-0b3b8ae874.dat

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=6afc05aa"

set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo extrac32.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-0b3b8ae874.dat

exit /b 0

