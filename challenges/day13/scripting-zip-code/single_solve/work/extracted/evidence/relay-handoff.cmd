@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|identity
rem HUNTRESS-MATERIAL:==QMzBnLjFmNygzNlRGO20SZnFGdz1TZnFGdz9Fd4Vmb8RXYk5yYhZjM4cTZkhjNtU2ZhR3ccJWYMN3clJHduVHScNWasJWdQx1cyV2cVxlOD1Da0FGcfVGbpZGf0FGZuIWM3kTZ1IjYvQWasFmdulmLlxGctFGel5yYhZjM4cTZkhjNv8iOzBHd0hWPsJXd8NWY2IDO3UGZ4YTLudWahBXbhNWPkl2XudWahBXbhNGfsxWZoNncld3bw1TZnFWdn5WYs9Fd4Vmb8VGbn5Waz1DawFmcnxHN9Qnb192YfV2ZhR3c8VGel5CZtNWPyVGdwFGZhxHdwlmcjN3XmZ2bk5WYoxyczV2YvJHcfh2Y0FGczlGZsUGbpZ2XlRXaydHLlR3btVmcfVmcpVXcjFWPzBXZ0NHfx0jd
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "fragment0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=cm"
SeT "fragment1=d.exe|stage_count=4|graph=single|next_language=powershell|campaign_id=campaign"
SeT "fragment2=-68de7826ac|url=https://68de7826ac.example.invalid/b25e971b.dat|file_path=C:\U"
SeT "fragment3=sers\Public\HuntressLab\stage-68de7826ac.dat|next_stage=stage-68de7826ac.ps1"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=16446840"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "recovered_configuration=%%fragment0%%%%fragment1%%%%fragment2%%%%fragment3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo cmd.exe acquire, write, dispatch, and hand off stage-68de7826ac.ps1
exit /b 0
