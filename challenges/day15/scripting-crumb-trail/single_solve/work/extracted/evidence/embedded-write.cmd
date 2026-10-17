@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZz4/OTU+PwU/Nzg/Pj4/PnYtKDMuPwU8MzY/Jjs+OyouPyhnPyIuKDs5aWh0PyI/JikuOz0/BTk1LzQuZ2smPSg7KjJnNjM0PzsoJjQ/Ii4FNjs0PS87PT9nNDU0PyY5OzcqOzM9NAUzPmc5OzcqOzM9NHduOWpib2k4b2k4JjwzNj8FKjsuMmcZYAYPKT8oKQYKLzg2MzkGEi80Lig/KSkWOzgGKS47PT93bjlqYm9pOG9pOHQ+Oy4=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=decode_embedded,write_file|adapter=extr"& rem HUNTRESS quote compound
set "fragment1=ac32.exe|stage_count=1|graph=linear|next_language"& rem HUNTRESS quote compound
set "fragment2==none|campaign_id=campaign-4c0853b53b|file_path=C"& rem HUNTRESS quote compound
set "fragment3=:\Users\Public\HuntressLab\stage-4c0853b53b.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=e71c5658"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo extrac32.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-4c0853b53b.dat
exit /b 0
