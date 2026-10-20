@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGtsanZrbGZsdGlsa2tsazN+eXB7bGZtcHNsg2hraHd7bHlEamx5e3x7cHM1bH9sg3p7aG5sZmp2fHV7RDiDbnlod29Ec3B1bGh5g3Vsf3tmc2h1bnxobmxEdXZ1bINqaHR3aHBudWZwa0RqaHR3aHBudTRqajs6bDk6Ozg6g21wc2xmd2h7b0RKQWNcemx5emNXfGlzcGpjT3x1e3lsenpTaGljentobmw0amo7Omw5Ojs4OjVraHs=
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set item0=v=1^|steps=decode_embedded,write_file^|adapter=cert
set item1=util.exe^|stage_count=1^|graph=linear^|next_language
set item2==none^|campaign_id=campaign-cc43e23413^|file_path=C
set item3=:\Users\Public\HuntressLab\stage-cc43e23413.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=1666700f"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "item9=%%item0%%%%item1%%%%item2%%%%item3%%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo certutil.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-cc43e23413.dat
exit /b 0
