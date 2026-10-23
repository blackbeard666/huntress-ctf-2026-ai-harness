@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:base64_literal|reverse

rem HUNTRESS-MATERIAL:dGFkLmMzMDYzNTJjOTgtZWdhdHNcYmFMc3NlcnRudUhcY2lsYnVQXHNyZXNVXDpDPWh0YXBfZWxpZnxjMzA2MzUyYzk4LW5naWFwbWFjPWRpX25naWFwbWFjfGVub249ZWdhdWduYWxfdHhlbnxkbm9tYWlkPWhwYXJnfDE9dG51b2NfZWdhdHN8ZXhlLjIzY2FydHhlPXJldHBhZGF8ZWxpZl9ldGlydyxkZWRkZWJtZV9lZG9jZWQ9c3BldHN8MT12

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

SeT "h0=v=1|steps=decode_embedded,write_file|adapter=extr"
SeT "h1=ac32.exe|stage_count=1|graph=diamond|next_languag"
SeT "h2=e=none|campaign_id=campaign-89c253603c|file_path="
SeT "h3=C:\Users\Public\HuntressLab\stage-89c253603c.dat"

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_opaque_branch=e3faac89"

for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg=%h0%%h1%%h2%%h3%"
exit /b 0
:HUNTRESS_EMIT

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo extrac32.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-89c253603c.dat

exit /b 0

