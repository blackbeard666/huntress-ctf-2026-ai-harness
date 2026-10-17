@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:plain_fragments|reverse

rem HUNTRESS-MATERIAL:dGFkLmJjYTJjMGU5ZWItZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnxiY2EyYzBlOWViLW5naWFwbWFjPWRpX25naWFwbWFjfGVub249ZWdhdWduYWxfdHhlbnxlbGduaXM9aHBhcmd8MT10bnVvY19lZ2F0c3xleGUuMjNjYXJ0eGU9cmV0cGFkYXxlbGlmX2V0aXJ3LGRlZGRlYm1lX2Vkb2NlZD1zcGV0c3wxPXY=

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "fragment0=v=1|steps=decode_embedded,write_file|adapter=extr"
set "fragment1=ac32.exe|stage_count=1|graph=single|next_language"
set "fragment2==none|campaign_id=campaign-be9e0c2acb|file_path=C"
set "fragment3=:\Users\Public\HuntressLab\stage-be9e0c2acb.dat"

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_dead_label=42c1770e"

set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"

echo(!recovered_configuration!

exit /b 0

:HUNTRESS_PLAN

echo extrac32.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-be9e0c2acb.dat

exit /b 0

