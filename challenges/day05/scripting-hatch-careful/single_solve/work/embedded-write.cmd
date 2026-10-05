@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|reverse_xor
rem HUNTRESS-MATERIAL:R1JXHQcEAwEAVVBWUlAeVlRSR0BvUVJ/QEBWQUddRntvUFpfUUZjb0BBVkBmbwlwDltHUkNsVl9aVU8HBAMBAFVQVlJQHl1UWlJDXlJQDldabF1UWlJDXlJQT1ZdXF0OVlRSRlRdUl9sR0tWXU9WVFJGVF1SX2xWXlJADltDUkFUTwIOR11GXFBsVlRSR0BPVktWHVddUkNLVg5BVkdDUldST1ZfWlVsVkdaQUQfV1ZXV1ZRXlZsVldcUFZXDkBDVkdATwIORQ==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=decode_embedded,write_file|adapter=expan"& rem HUNTRESS quote compound
set "FrAg1=d.exe|stage_count=1|graph=same_language|next_langu"& rem HUNTRESS quote compound
set "FrAg2=age=none|campaign_id=campaign-caecf32074|file_path"& rem HUNTRESS quote compound
set "FrAg3==C:\Users\Public\HuntressLab\stage-caecf32074.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=5f908d00"
ver >nul
if errorlevel 1 exit /b 1
call set "ReCoVeReD=%%FrAg0%%%%FrAg1%%%%FrAg2%%%%FrAg3%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo expand.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-caecf32074.dat
exit /b 0
