@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:reversed_text|reverse

rem HUNTRESS-MATERIAL:21TM8NHdlB3c9E2YxVXayV2XyVWbvRXZscncpRXZfZWasVGfhRWYwRXZy1jYpR3chRWbp5mLlhXZ8NHdhdWZfN2b15Gd9EDfnJXYwhWPzlmbnxWZ85WZ4R3XsFmbnVXYnVWPu9mblx3Yh1Gchl2Zu9Vak1zYh1Gchl2Zu1iYwYGMykjYkJzY8Vncs1Da0RHczpzLvIGMmBjM5IGZyMmLlhXYtBHbl5SauZXYslGZvUzM2QWY5ATMuQWY0xnZpxWZfBXY0hWPDpDXVNXZyNHXQVnYsl2YchUduRnclN3cMFmYcNHdhdWZtIGMmBjM5IGZyMmLkFGd

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set v_a0=v=1^|steps=acquire_remote,write_file^|adapter=bitsadmin.exe^|stag
set v_a1=e_count=1^|graph=single^|next_language=none^|campaign_id=campaign
set v_a2=-b0f029bd2c^|url=https://b0f029bd2c.example.invalid/536da901.da
set v_a3=t^|file_path=C:\Users\Public\HuntressLab\stage-b0f029bd2c.dat

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=58ebfa8c"

ver >nul
if errorlevel 1 exit /b 1
set "cfg=%v_a0%%v_a1%%v_a2%%v_a3%"

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo bitsadmin.exe acquire https://b0f029bd2c.example.invalid/536da901.dat to C:\Users\Public\HuntressLab\stage-b0f029bd2c.dat

exit /b 0

