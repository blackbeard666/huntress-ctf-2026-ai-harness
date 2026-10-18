@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|reverse_xor
rem HUNTRESS-MATERIAL:R0tHHQQECgtRUVYAVwoeYXZlfHB2YQ5WXlJdbFZHXF1PV1ZYUFxfHQQECgtRUVYAVwodDl1cWkBdVkdLVk9HUlcdBAQKC1FRVgBXCh5WVFJHQG9RUn9AQFZBR11Ge29QWl9RRmNvQEFWQGZvCXAOW0dSQ2xWX1pVTwQECgtRUVYAVwoeXVRaUkNeUlAOV1psXVRaUkNeUlBPVl1cXQ5WVFJGVF1SX2xHS1ZdT1ZUUkZUXVJfbEBAXEFQDltDUkFUTwIOR11GXFBsVlRSR0BPVktWHUdQUkNeXFAOQVZHQ1JXUk9WR1xdbEpBVkVcUFZBbFZHWkFEH0ddVkddXFBsXkFcVUBdUkFHH0BHVlRBUkdsVkdSQVZeRl1WDkBDVkdATwIORQ==
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapter"
set "item1==compact.exe|stage_count=1|graph=cross_language|next_language=none|campai"
set "item2=gn_id=campaign-9d3ebb8977|file_path=C:\Users\Public\HuntressLab\stage-9d3"
set "item3=ebb8977.dat|extension=.9d3ebb8977.locked|note_name=RECOVER-9d3ebb8977.txt"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9=%item0%%item1%%item2%%item3%"
exit /b 0
:HUNTRESS_EMIT
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo for targets then compact.exe transform and write RECOVER-9d3ebb8977.txt
exit /b 0
