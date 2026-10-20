@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:base64_literal|rotate_left

rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesLG4urS5Mq+5Mra3ujKWO7k0ujKvszS2MpYyNLm4MLoxtC+4OTexsrm5ljQwtzI3szMvubG5NLg6PjCyMLg6MrkeuTq3MjY2GZkXMrwyvjm6MLOyr7G3urc6Hpo+M7kwuDQesbk3ubmvtjC3M7qws7K+NzK8Oi+2MLczurCzsp61ObG5NLg6PjGwtrgwtLO3L7SyHrGwtrgwtLO3FpmZHJmYMTGYsRw+Ork2HrQ6Ojg5nReXmZkcmZgxMZixHBcyvDC2uDYylzS3OzC2NLIXmhiymbIyMbMXMjC6PjM0tjKvuDC6NB6hnS4qubK5Oa4oOrE2NLGuJDq3OjkyubmmMLEuObows7KWmZkcmZgxMZixHBcyMLo+NzK8Oi+5ujCzsp65ujCzspaZmRyZmDExmLEcFzU5g==

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "fragment0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=rund"& rem HUNTRESS quote compound
set "fragment1=ll32.exe|stage_count=4|graph=cross_language|next_language=jscript|campaign_id=ca"& rem HUNTRESS quote compound
set "fragment2=mpaign-32930bc1b8|url=https://32930bc1b8.example.invalid/41e3ddcf.dat|file_path="& rem HUNTRESS quote compound
set "fragment3=C:\Users\Public\HuntressLab\stage-32930bc1b8.dat|next_stage=stage-32930bc1b8.js"& rem HUNTRESS quote compound

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_string_join=afac1ffc"

goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
call set "recovered_configuration=%%fragment0%%%%fragment1%%%%fragment2%%%%fragment3%%"

echo(!recovered_configuration!

exit /b 0

:HUNTRESS_PLAN

echo rundll32.exe acquire, write, dispatch, and hand off stage-32930bc1b8.js

exit /b 0

