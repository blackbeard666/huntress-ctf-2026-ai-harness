@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZzs5Ky8zKD8FKD83NS4/di0oMy4/BTwzNj92PjMpKjsuOTIFKig1OT8pKXYyOzQ+NTw8BSk5KDMqLiY7PjsqLj8oZzcpMi47dD8iPyYpLjs9PwU5NS80LmduJj0oOyoyZzkoNSkpBTY7ND0vOz0/JjQ/Ii4FNjs0PS87PT9nMCk5KDMqLiY5OzcqOzM9NAUzPmc5OzcqOzM9NHc/aWw7YztsP21uJi8oNmcyLi4qKWB1dT9pbDtjO2w/bW50PyI7Nyo2P3QzNCw7NjM+dWw/O29uajhudD47LiY8MzY/BSo7LjJnGWAGDyk/KCkGCi84NjM5BhIvNC4oPykpFjs4BikuOz0/dz9pbDtjO2w/bW50PjsuJjQ/Ii4FKS47PT9nKS47PT93P2lsO2M7bD9tbnQwKQ==
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=msh"& rem HUNTRESS quote compound
set "h1=ta.exe|stage_count=4|graph=cross_language|next_language=jscript|campaign_id=cam"& rem HUNTRESS quote compound
set "h2=paign-e36a9a6e74|url=https://e36a9a6e74.example.invalid/6ea540b4.dat|file_path="& rem HUNTRESS quote compound
set "h3=C:\Users\Public\HuntressLab\stage-e36a9a6e74.dat|next_stage=stage-e36a9a6e74.js"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
ver >nul
if errorlevel 1 exit /b 1
call set "cfg=%%h0%%%%h1%%%%h2%%%%h3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo mshta.exe acquire, write, dispatch, and hand off stage-e36a9a6e74.js
exit /b 0
