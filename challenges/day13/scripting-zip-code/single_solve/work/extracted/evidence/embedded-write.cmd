@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:split_fragments|add_7

rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGtsanZrbGZsdGlsa2tsazN+eXB7bGZtcHNsg2hraHd7bHlEbH97eWhqOjk1bH9sg3p7aG5sZmp2fHV7RDiDbnlod29Ec3B1bGh5g3Vsf3tmc2h1bnxobmxEdXZ1bINqaHR3aHBudWZwa0RqaHR3aHBudTQ7bWo5OGk9PUBrg21wc2xmd2h7b0RKQWNcemx5emNXfGlzcGpjT3x1e3lsenpTaGljentobmw0O21qOThpPT1AazVraHs=

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set FrAg0=v=1^|steps=decode_embedded,write_file^|adapter=extr
set FrAg1=ac32.exe^|stage_count=1^|graph=linear^|next_language
set FrAg2==none^|campaign_id=campaign-4fc21b669d^|file_path=C
set FrAg3=:\Users\Public\HuntressLab\stage-4fc21b669d.dat

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_string_join=a33615d9"

set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "ReCoVeReD=%%FrAg0%%%%FrAg1%%%%FrAg2%%%%FrAg3%%"

echo(!ReCoVeReD!

exit /b 0

:HUNTRESS_PLAN

echo extrac32.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-4fc21b669d.dat

exit /b 0

