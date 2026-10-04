@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:base64_literal|add_7

rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RHN2amh7bGZzdmpoczNrcHp3aHtqb2Z3eXZqbHp6g2hraHd7bHlEanRrNWx/bIN6e2hubGZqdnx1e0Q4g255aHdvRGp5dnp6ZnNodW58aG5sg3Vsf3tmc2h1bnxobmxEdXZ1bINqaHR3aHBudWZwa0RqaHR3aHBudTQ7Pmo7OzhtbGw3g21wc2xmd2h7b0RKQWNcemx5emNXfGlzcGpjT3x1e3lsenpTaGljentobmw0Oz5qOzs4bWxsNzVraHs=

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "fragment0=v=1|steps=locate_local,dispatch_process|adapter=cm"& rem HUNTRESS quote compound
set "fragment1=d.exe|stage_count=1|graph=cross_language|next_lang"& rem HUNTRESS quote compound
set "fragment2=uage=none|campaign_id=campaign-47c441fee0|file_pat"& rem HUNTRESS quote compound
set "fragment3=h=C:\Users\Public\HuntressLab\stage-47c441fee0.dat"& rem HUNTRESS quote compound

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=1ba6d7d0"

set "recovered_configuration=!fragment0!!fragment1!!fragment2!!fragment3!"

echo(!recovered_configuration!

exit /b 0

:HUNTRESS_PLAN

echo cmd.exe dispatch C:\Users\Public\HuntressLab\stage-47c441fee0.dat

exit /b 0

