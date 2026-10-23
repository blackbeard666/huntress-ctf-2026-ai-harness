@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:reversed_text|identity

rem HUNTRESS-MATERIAL:==AdhRmLjFmMzEDN3UWM50SZnFGdzxlYhx0czVmc05WdIx1YpxmY1BFXzJXZzVFX6MUPoRXYw9VZslmZ8NWYyMTM0cTZxkTLudWahBXbhNWPkl2XudWahBXbhNGfl52bu1TZnFWdn5WYs9Fd4Vmb8JXYl5Was1DawFmcnxXM9Qnb192YfV2ZhR3c8RnchR3c9IXZ0BXYkFGfzNXZj9mcw9FajRXYwNXakxCbhN2bs9VZ0F2YvxWPzBXZ0NHfx0jd

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set fragment0=v=1^|steps=locate_local,dispatch_process^|adapter=
set fragment1=start^|stage_count=1^|graph=linear^|next_language=n
set fragment2=one^|campaign_id=campaign-91e74132ac^|file_path=C:
set fragment3=\Users\Public\HuntressLab\stage-91e74132ac.dat

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=f2501bdb"

goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"

echo(!recovered_configuration!

exit /b 0

:HUNTRESS_PLAN

echo start dispatch C:\Users\Public\HuntressLab\stage-91e74132ac.dat

exit /b 0

