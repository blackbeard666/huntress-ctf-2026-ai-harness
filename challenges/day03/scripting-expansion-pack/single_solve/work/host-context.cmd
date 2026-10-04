@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|identity
rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWRlY29kZV9jb25maWd1cmF0aW9uLHJldHVybl9jb25maWd1cmF0aW9ufGFkYXB0ZXI9Y2FsbHxzdGFnZV9jb3VudD0xfGdyYXBoPXNhbWVfbGFuZ3VhZ2V8bmV4dF9sYW5ndWFnZT1ub25lfGNhbXBhaWduX2lkPWNhbXBhaWduLWI2YmVkYmY5MmZ8aG9zdF9pZD1ob3N0LWI2YmVkYmY5MmY=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "fragment0=v=1|steps=decode_configuration,return_config"
SeT "fragment1=uration|adapter=call|stage_count=1|graph=sam"
SeT "fragment2=e_language|next_language=none|campaign_id=ca"
SeT "fragment3=mpaign-b6bedbf92f|host_id=host-b6bedbf92f"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=0f5e5826"
ver >nul
if errorlevel 1 exit /b 1
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-b6bedbf92f
exit /b 0
