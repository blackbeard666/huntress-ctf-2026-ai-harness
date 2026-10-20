@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmetjexsLoyr7Y3sbC2FjI0ubgwujG0L7g5N7Gyubm+MLIwuDoyuR6xsLY2Pjm6MLOyr7G3urc6Hpi+M7kwuDQeszC3L7e6uj43Mrw6L7YwtzO6sLOynrc3tzK+MbC2uDC0s7cvtLIesbC2uDC0s7cWsZoxsZqyMLIYsL4zNLYyr7gwujQeoZ0uKrmyuTmuKDqxNjSxriQ6tzo5Mrm5pjCxLjm6MLOylrGaMbGasjCyGLCXMjC6A==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=locate_local,dispatch_process|adapter="& rem HUNTRESS quote compound
set "item1=call|stage_count=1|graph=fan_out|next_language=n"& rem HUNTRESS quote compound
set "item2=one|campaign_id=campaign-c4cc5dad1a|file_path=C:"& rem HUNTRESS quote compound
set "item3=\Users\Public\HuntressLab\stage-c4cc5dad1a.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=5f391ef2"
set "item9=!item0!!item1!!item2!!item3!"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo call dispatch C:\Users\Public\HuntressLab\stage-c4cc5dad1a.dat
exit /b 0
