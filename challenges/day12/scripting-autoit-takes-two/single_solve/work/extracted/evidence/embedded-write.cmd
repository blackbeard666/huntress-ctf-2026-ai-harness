@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|reverse
rem HUNTRESS-MATERIAL:dGFkLmZlY2E2NTEwMWYtZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnxmZWNhNjUxMDFmLW5naWFwbWFjPWRpX25naWFwbWFjfGVub249ZWdhdWduYWxfdHhlbnxyYWVuaWw9aHBhcmd8MT10bnVvY19lZ2F0c3xleGUubGl0dXRyZWM9cmV0cGFkYXxlbGlmX2V0aXJ3LGRlZGRlYm1lX2Vkb2NlZD1zcGV0c3wxPXY=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set v_a0=v=1^|steps=decode_embedded,write_file^|adapter=cert
set v_a1=util.exe^|stage_count=1^|graph=linear^|next_language
set v_a2==none^|campaign_id=campaign-f10156acef^|file_path=C
set v_a3=:\Users\Public\HuntressLab\stage-f10156acef.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=ff381729"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo certutil.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-f10156acef.dat
exit /b 0
