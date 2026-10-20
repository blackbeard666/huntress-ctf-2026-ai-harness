@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:reversed_text|identity

rem HUNTRESS-MATERIAL:==AdhRmLmdzN5kjM4YzMl1SZnFGdzxlYhx0czVmc05WdIx1YpxmY1BFXzJXZzVFX6MUPoRXYw9VZslmZ8Z2N3kTOygjNzUWLudWahBXbhNWPkl2XudWahBXbhNGfl52bu1TZnFWdn5WYs9Fd4Vmb8VGbn5Waz1DawFmcnxXM9Qnb192YfV2ZhR3c8RnchR3c9IXZ0BXYkFGfzNXZj9mcw9FajRXYwNXakxCbhN2bs9VZ0F2YvxWPzBXZ0NHfx0jd

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

SeT "item0=v=1|steps=locate_local,dispatch_process|adapter="
SeT "item1=start|stage_count=1|graph=single|next_language=n"
SeT "item2=one|campaign_id=campaign-e36829977f|file_path=C:"
SeT "item3=\Users\Public\HuntressLab\stage-e36829977f.dat"

goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=22435e0e"

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"
exit /b 0
:HUNTRESS_EMIT

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo start dispatch C:\Users\Public\HuntressLab\stage-e36829977f.dat

exit /b 0

