@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:plain_fragments|reverse

rem HUNTRESS-MATERIAL:dGFkLmZjZmM1ODU4ZWUtZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnxmY2ZjNTg1OGVlLW5naWFwbWFjPWRpX25naWFwbWFjfGVub249ZWdhdWduYWxfdHhlbnxlZ2F1Z25hbF9zc29yYz1ocGFyZ3wxPXRudW9jX2VnYXRzfGV4ZS4yM2NhcnR4ZT1yZXRwYWRhfGVsaWZfZXRpcncsZGVkZGVibWVfZWRvY2VkPXNwZXRzfDE9dg==

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "FrAg0=v=1|steps=decode_embedded,write_file|adapter=extrac"
set "FrAg1=32.exe|stage_count=1|graph=cross_language|next_lang"
set "FrAg2=uage=none|campaign_id=campaign-ee8585cfcf|file_path"
set "FrAg3==C:\Users\Public\HuntressLab\stage-ee8585cfcf.dat"

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_dead_label=2bddd519"

call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "ReCoVeReD=%FrAg0%%FrAg1%%FrAg2%%FrAg3%"
exit /b 0
:HUNTRESS_EMIT

echo(!ReCoVeReD!

exit /b 0

:HUNTRESS_PLAN

echo extrac32.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-ee8585cfcf.dat

exit /b 0

