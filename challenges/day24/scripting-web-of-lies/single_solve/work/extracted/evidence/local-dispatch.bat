@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|reverse_xor
rem HUNTRESS-MATERIAL:4752571d075006005055010a06071e56545247406f51527f40405641475d467b6f505a5f5146636f40415640666f09700e5b4752436c565f5a554f075006005055010a06071e5d545a52435e52500e575a6c5d545a52435e52504f565d5c5d0e56545246545d525f6c474b565d4f56545246545d525f6c40405c41500e5b435241544f020e475d465c506c56545247404f47415247400e415647435257524f404056505c41436c5b50475243405a571f5f52505c5f6c564752505c5f0e40435647404f020e45
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=locate_local,dispatch_process|adapter=st"& rem HUNTRESS quote compound
set "item1=art|stage_count=1|graph=cross_language|next_langua"& rem HUNTRESS quote compound
set "item2=ge=none|campaign_id=campaign-4592fc35c4|file_path="& rem HUNTRESS quote compound
set "item3=C:\Users\Public\HuntressLab\stage-4592fc35c4.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
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
echo start dispatch C:\Users\Public\HuntressLab\stage-4592fc35c4.dat
exit /b 0
