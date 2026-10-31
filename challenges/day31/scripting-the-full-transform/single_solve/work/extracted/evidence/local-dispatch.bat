@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmetjexsLoyr7Y3sbC2FjI0ubgwujG0L7g5N7Gyubm+MLIwuDoyuR6xtrIXMrwyvjm6MLOyr7G3urc6Hpi+M7kwuDQetjS3MrC5PjcyvDovtjC3M7qws7Ketze3Mr4xsLa4MLSzty+0sh6xsLa4MLSztxaZG7EzGZgbmpqyvjM0tjKvuDC6NB6hnS4qubK5Oa4oOrE2NLGuJDq3OjkyubmmMLEuObows7KWmRuxMxmYG5qaspcyMLo
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=locate_local,dispatch_process|adapter="& rem HUNTRESS quote compound
set "item1=cmd.exe|stage_count=1|graph=linear|next_language"& rem HUNTRESS quote compound
set "item2==none|campaign_id=campaign-27bf30755e|file_path="& rem HUNTRESS quote compound
set "item3=C:\Users\Public\HuntressLab\stage-27bf30755e.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=bd2ae550"
call set "item9=%%item0%%%%item1%%%%item2%%%%item3%%"
echo(!item9!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo cmd.exe dispatch C:\Users\Public\HuntressLab\stage-27bf30755e.dat
exit /b 0
