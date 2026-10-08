@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|reverse_xor
rem HUNTRESS-MATERIAL:R1JXHVYAVQsKAwsBBQseVlRSR0BvUVJ/QEBWQUddRntvUFpfUUZjb0BBVkBmbwlwDltHUkNsVl9aVU9WAFULCgMLAQULHl1UWlJDXlJQDldabF1UWlJDXlJQT1ZdXF0OVlRSRlRdUl9sR0tWXU9KQUdWQWxYUFJRX19SVQ5bQ1JBVE8CDkddRlxQbFZUUkdAT1ZLVh1XXlAOQVZHQ1JXUk9AQFZQXEFDbFtQR1JDQFpXH19SUFxfbFZHUlBcXw5AQ1ZHQE8CDkU=
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=locate_local,dispatch_process|adapter=cm"& rem HUNTRESS quote compound
set "item1=d.exe|stage_count=1|graph=fallback_retry|next_lang"& rem HUNTRESS quote compound
set "item2=uage=none|campaign_id=campaign-8628098f3e|file_pat"& rem HUNTRESS quote compound
set "item3=h=C:\Users\Public\HuntressLab\stage-8628098f3e.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=7bd4a1df"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!item9!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo cmd.exe dispatch C:\Users\Public\HuntressLab\stage-8628098f3e.dat
exit /b 0
