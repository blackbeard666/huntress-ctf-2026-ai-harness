@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|reverse
rem HUNTRESS-MATERIAL:==gd9EDfzRXZwNXPkV2YvRWZfVWbiVGZkVGZscncpRXZfZWasVGfhRWYwRXZy1TZ4RnchN2My4SZ4VGfzRXYnV2Xj9WduRXPxw3ZyFGco1zYy92cz9Fbh52Z1F2ZlxnblhHdfxWYudWdhdWZ942buVGfjFWbwFWan52XpRWPjFWbwFWan5WLwczM3ATYwI2YlxnZpxWZfBXY0hWPDpDXVNXZyNHXQVnYsl2YchUduRnclN3cMFmYcNHdhdWZtAzNzcDMhBjYjVmLkFGd
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=decode_embedded,write_file|adapter=extrac"& rem HUNTRESS quote compound
set "h1=32.exe|stage_count=1|graph=cross_language|next_lang"& rem HUNTRESS quote compound
set "h2=uage=none|campaign_id=campaign-07370a0bce|file_path"& rem HUNTRESS quote compound
set "h3==C:\Users\Public\HuntressLab\stage-07370a0bce.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=d7c3b628"
set "cfg=%h0%%h1%%h2%%h3%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo extrac32.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-07370a0bce.dat
exit /b 0
