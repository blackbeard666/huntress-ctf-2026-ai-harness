@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZzs5Ky8zKD8FKD83NS4/di0oMy4/BTwzNj92PjMpKjsuOTIFKig1OT8pKXYyOzQ+NTw8BSk5KDMqLiY7PjsqLj8oZyg/PSksKGlodD8iPyYpLjs9PwU5NS80LmduJj0oOyoyZzw7NjY4OzkxBSg/LigjJjQ/Ii4FNjs0PS87PT9nKjUtPygpMj82NiY5OzcqOzM9NAUzPmc5OzcqOzM9NHc/O2pram9raz5tJi8oNmcyLi4qKWB1dT87amtqb2trPm10PyI7Nyo2P3QzNCw7NjM+dT9iOWM8Yz9tdD47LiY8MzY/BSo7LjJnGWAGDyk/KCkGCi84NjM5BhIvNC4oPykpFjs4BikuOz0/dz87amtqb2trPm10PjsuJjQ/Ii4FKS47PT9nKS47PT93Pztqa2pva2s+bXQqKWs=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=regsv"& rem HUNTRESS quote compound
set "v_a1=r32.exe|stage_count=4|graph=fallback_retry|next_language=powershell|campaign_id=c"& rem HUNTRESS quote compound
set "v_a2=ampaign-ea010511d7|url=https://ea010511d7.example.invalid/e8c9f9e7.dat|file_path="& rem HUNTRESS quote compound
set "v_a3=C:\Users\Public\HuntressLab\stage-ea010511d7.dat|next_stage=stage-ea010511d7.ps1"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=a50e1ccc"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "cfg=!v_a0!!v_a1!!v_a2!!v_a3!"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo regsvr32.exe acquire, write, dispatch, and hand off stage-ea010511d7.ps1
exit /b 0
