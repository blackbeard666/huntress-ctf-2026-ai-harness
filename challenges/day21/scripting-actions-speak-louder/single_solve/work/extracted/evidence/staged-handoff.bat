@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGhqeHxweWxmeWx0dntsM355cHtsZm1wc2wza3B6d2h7am9md3l2amx6ejNvaHVrdm1tZnpqeXB3e4Noa2h3e2x5RGp0azVsf2yDentobmxmanZ8dXtEO4NueWh3b0R6cHVuc2yDdWx/e2ZzaHVufGhubER3dn5seXpvbHNzg2podHdocG51ZnBrRGpodHdocG51NEA3PUBrOjtsaGmDfHlzRG97e3d6QTY2QDc9QGs6O2xoaTVsf2h0d3NsNXB1fWhzcGs2O21AaDo/PDw1a2h7g21wc2xmd2h7b0RKQWNcemx5emNXfGlzcGpjT3x1e3lsenpTaGljentobmw0QDc9QGs6O2xoaTVraHuDdWx/e2Z6e2hubER6e2hubDRANz1Aazo7bGhpNXd6OA==
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "v_a0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=cm"
SeT "v_a1=d.exe|stage_count=4|graph=single|next_language=powershell|campaign_id=campaign"
SeT "v_a2=-9069d34eab|url=https://9069d34eab.example.invalid/4f9a3855.dat|file_path=C:\U"
SeT "v_a3=sers\Public\HuntressLab\stage-9069d34eab.dat|next_stage=stage-9069d34eab.ps1"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=31de6f60"
set "cfg=!v_a0!!v_a1!!v_a2!!v_a3!"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo cmd.exe acquire, write, dispatch, and hand off stage-9069d34eab.ps1
exit /b 0
