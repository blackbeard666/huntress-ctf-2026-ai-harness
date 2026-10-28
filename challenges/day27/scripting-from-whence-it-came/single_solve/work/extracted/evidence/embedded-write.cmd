@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:base64_literal|reverse

rem HUNTRESS-MATERIAL:dGFkLmViZTM0NGVmZjUtZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnxlYmUzNDRlZmY1LW5naWFwbWFjPWRpX25naWFwbWFjfGVub249ZWdhdWduYWxfdHhlbnxlZ2F1Z25hbF9lbWFzPWhwYXJnfDE9dG51b2NfZWdhdHN8ZXhlLjIzY2FydHhlPXJldHBhZGF8ZWxpZl9ldGlydyxkZWRkZWJtZV9lZG9jZWQ9c3BldHN8MT12

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

SeT "h0=v=1|steps=decode_embedded,write_file|adapter=extrac"
SeT "h1=32.exe|stage_count=1|graph=same_language|next_langu"
SeT "h2=age=none|campaign_id=campaign-5ffe443ebe|file_path="
SeT "h3=C:\Users\Public\HuntressLab\stage-5ffe443ebe.dat"

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_arithmetic=8a6d0289"

set "cfg=%h0%%h1%%h2%%h3%"

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo extrac32.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-5ffe443ebe.dat

exit /b 0

