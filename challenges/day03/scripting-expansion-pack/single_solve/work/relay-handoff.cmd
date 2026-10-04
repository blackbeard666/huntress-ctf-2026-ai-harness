@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZzs5Ky8zKD8FKD83NS4/di0oMy4/BTwzNj92PjMpKjsuOTIFKig1OT8pKXYyOzQ+NTw8BSk5KDMqLiY7PjsqLj8oZyo1LT8oKTI/NjZ0PyI/JikuOz0/BTk1LzQuZ24mPSg7KjJnOSg1KSkFNjs0PS87PT8mND8iLgU2OzQ9Lzs9P2cwKTkoMyouJjk7Nyo7Mz00BTM+Zzk7Nyo7Mz00d287OW88PGI/YmImLyg2ZzIuLiopYHV1bzs5bzw8Yj9iYnQ/Ijs3KjY/dDM0LDs2Mz51Oz9jaGM4bjx0PjsuJjwzNj8FKjsuMmcZYAYPKT8oKQYKLzg2MzkGEi80Lig/KSkWOzgGKS47PT93bzs5bzw8Yj9iYnQ+Oy4mND8iLgUpLjs9P2cpLjs9P3dvOzlvPDxiP2JidDAp
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set item0=v=1^|steps=acquire_remote,write_file,dispatch_process,handoff_script^|adapter=power
set item1=shell.exe^|stage_count=4^|graph=cross_language^|next_language=jscript^|campaign_id=ca
set item2=mpaign-5ac5ff8e88^|url=https://5ac5ff8e88.example.invalid/ae929b4f.dat^|file_path=C
set item3=:\Users\Public\HuntressLab\stage-5ac5ff8e88.dat^|next_stage=stage-5ac5ff8e88.js
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=4da4d62c"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "item9=!item0!!item1!!item2!!item3!"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo powershell.exe acquire, write, dispatch, and hand off stage-5ac5ff8e88.js
exit /b 0
