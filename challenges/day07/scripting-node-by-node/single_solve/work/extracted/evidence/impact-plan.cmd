@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:reversed_text|xor_5a

rem HUNTRESS-MATERIAL:=4iIuQnYrtTav9jP5sma3hwHMURGfgwZ/czO0UwPuUDNm4zPxkTN2QnYrtTav9jP5sma0dGN1MTK08jLi8jJusjP0J2a7k2b/4TOrp2d/0zOukiB4sjFpkyPo4CNvIhB5MjN48iCGkCK/kyDGAWGnJjL7oSB/YzM8YiYrtTav9jP5sma3RTPzsjK3sTOn5zMFQTPzsjK3sTOm8DN1QzZ/0zOv0DN7YTBuIyP0YyP9szL9QzO2UQKpUDK5cmMqsDK9Yyan5CNvUTOF8TP74SKmgSN8cGK/4iK74zOm8jL1QTBjgyPsUTO/gSB/4yMo0iduQzPuQTN5UwNoUDPpQzOo4idp4yP9gyOuUwPusDK/czL08zZpoyPukiJrdGL

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "fragment0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapt"
set "fragment1=er=for|stage_count=1|graph=cross_language|next_language=none|campaign_i"
set "fragment2=d=campaign-01cde53a18|file_path=C:\Users\Public\HuntressLab\stage-01cde"
set "fragment3=53a18.dat|extension=.01cde53a18.locked|note_name=RECOVER-01cde53a18.txt"

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=f210b7c4"

ver >nul
if errorlevel 1 exit /b 1
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"

echo(!recovered_configuration!

exit /b 0

:HUNTRESS_PLAN

echo for targets then for transform and write RECOVER-01cde53a18.txt

exit /b 0

