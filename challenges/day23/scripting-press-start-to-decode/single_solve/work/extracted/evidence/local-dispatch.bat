@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RHN2amh7bGZzdmpoczNrcHp3aHtqb2Z3eXZqbHp6g2hraHd7bHlEamhzc4N6e2hubGZqdnx1e0Q4g255aHdvRHpodGxmc2h1bnxobmyDdWx/e2ZzaHVufGhubER1dnVsg2podHdocG51ZnBrRGpodHdocG51NGlrOj1rO2tsPjeDbXBzbGZ3aHtvREpBY1x6bHl6Y1d8aXNwamNPfHV7eWx6elNoaWN6e2hubDRpazo9aztrbD43NWtoew==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "fragment0=v=1|steps=locate_local,dispatch_process|adapter=c"
SeT "fragment1=all|stage_count=1|graph=same_language|next_langua"
SeT "fragment2=ge=none|campaign_id=campaign-bd36d4de70|file_path"
SeT "fragment3==C:\Users\Public\HuntressLab\stage-bd36d4de70.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=e101deb4"
ver >nul
if errorlevel 1 exit /b 1
set "recovered_configuration=!fragment0!!fragment1!!fragment2!!fragment3!"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo call dispatch C:\Users\Public\HuntressLab\stage-bd36d4de70.dat
exit /b 0
