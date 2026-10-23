@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGhqeHxweWxmeWx0dntsM355cHtsZm1wc2wza3B6d2h7am9md3l2amx6ejNvaHVrdm1tZnpqeXB3e4Noa2h3e2x5RHd2fmx5em9sc3M1bH9sg3p7aG5sZmp2fHV7RDuDbnlod29EbWh1ZnZ8e4N1bH97ZnNodW58aG5sRHd2fmx5em9sc3ODamh0d2hwbnVmcGtEamh0d2hwbnU0Pj5sPDxtO2g9O4N8eXNEb3t7d3pBNjY+Pmw8PG07aD07NWx/aHR3c2w1cHV9aHNwazY/amlAQEBrajVraHuDbXBzbGZ3aHtvREpBY1x6bHl6Y1d8aXNwamNPfHV7eWx6elNoaWN6e2hubDQ+Pmw8PG07aD07NWtoe4N1bH97Znp7aG5sRHp7aG5sND4+bDw8bTtoPTs1d3o4
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=powe"& rem HUNTRESS quote compound
set "h1=rshell.exe|stage_count=4|graph=fan_out|next_language=powershell|campaign_id=camp"& rem HUNTRESS quote compound
set "h2=aign-77e55f4a64|url=https://77e55f4a64.example.invalid/8cb999dc.dat|file_path=C:"& rem HUNTRESS quote compound
set "h3=\Users\Public\HuntressLab\stage-77e55f4a64.dat|next_stage=stage-77e55f4a64.ps1"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=e6febee3"
ver >nul
if errorlevel 1 exit /b 1
set "cfg=!h0!!h1!!h2!!h3!"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo powershell.exe acquire, write, dispatch, and hand off stage-77e55f4a64.ps1
exit /b 0
