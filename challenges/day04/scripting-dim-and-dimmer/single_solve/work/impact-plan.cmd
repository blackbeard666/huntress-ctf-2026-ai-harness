@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|reverse_xor
rem HUNTRESS-MATERIAL:R0tHHVZRClYAAVYGUVIeYXZlfHB2YQ5WXlJdbFZHXF1PV1ZYUFxfHVZRClYAAVYGUVIdDl1cWkBdVkdLVk9HUlcdVlEKVgABVgZRUh5WVFJHQG9RUn9AQFZBR11Ge29QWl9RRmNvQEFWQGZvCXAOW0dSQ2xWX1pVT1ZRClYAAVYGUVIeXVRaUkNeUlAOV1psXVRaUkNeUlBPVl1cXQ5WVFJGVF1SX2xHS1ZdT0FSVl1aXw5bQ1JBVE8CDkddRlxQbFZUUkdAT1ZLVh1HUFJDXlxQDkFWR0NSV1JPVkdcXWxKQVZFXFBWQWxWR1pBRB9HXVZHXVxQbF5BXFVAXVJBRx9AR1ZUQVJHbFZHUkFWXkZdVg5AQ1ZHQE8CDkU=
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set fragment0=v=1^|steps=enumerate_targets,transform_content,write_recovery_note^|adapt
set fragment1=er=compact.exe^|stage_count=1^|graph=linear^|next_language=none^|campaign_i
set fragment2=d=campaign-ab5e23e9be^|file_path=C:\Users\Public\HuntressLab\stage-ab5e2
set fragment3=3e9be.dat^|extension=.ab5e23e9be.locked^|note_name=RECOVER-ab5e23e9be.txt
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=36b5863a"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo for targets then compact.exe transform and write RECOVER-ab5e23e9be.txt
exit /b 0
