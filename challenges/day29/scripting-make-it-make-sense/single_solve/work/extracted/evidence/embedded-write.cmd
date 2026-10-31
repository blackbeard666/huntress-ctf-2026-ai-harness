@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZz4/OTU+PwU/Nzg/Pj4/PnYtKDMuPwU8MzY/Jjs+OyouPyhnOT8oLi8uMzZ0PyI/JikuOz0/BTk1LzQuZ2smPSg7KjJnNjM0PzsoJjQ/Ii4FNjs0PS87PT9nNDU0PyY5OzcqOzM9NAUzPmc5OzcqOzM9NHdrO2prP247P2JvJjwzNj8FKjsuMmcZYAYPKT8oKQYKLzg2MzkGEi80Lig/KSkWOzgGKS47PT93aztqaz9uOz9ib3Q+Oy4=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=decode_embedded,write_file|adapter=cert"
set "fragment1=util.exe|stage_count=1|graph=linear|next_language"
set "fragment2==none|campaign_id=campaign-1a01e4ae85|file_path=C"
set "fragment3=:\Users\Public\HuntressLab\stage-1a01e4ae85.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=1e33ec33"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo certutil.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-1a01e4ae85.dat
exit /b 0
