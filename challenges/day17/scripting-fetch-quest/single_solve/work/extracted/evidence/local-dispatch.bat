@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|reverse_xor
rem HUNTRESS-MATERIAL:4752571d0607025606020a5002001e56545247406f51527f40405641475d467b6f505a5f5146636f40415640666f09700e5b4752436c565f5a554f0607025606020a5002001e5d545a52435e52500e575a6c5d545a52435e52504f565d5c5d0e56545246545d525f6c474b565d4f4a414756416c585052515f5f52550e5b435241544f020e475d465c506c56545247404f5f5f52500e415647435257524f404056505c41436c5b50475243405a571f5f52505c5f6c564752505c5f0e40435647404f020e45
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=locate_local,dispatch_process|adapter=ca"& rem HUNTRESS quote compound
set "FrAg1=ll|stage_count=1|graph=fallback_retry|next_languag"& rem HUNTRESS quote compound
set "FrAg2=e=none|campaign_id=campaign-31c915e145|file_path=C"& rem HUNTRESS quote compound
set "FrAg3=:\Users\Public\HuntressLab\stage-31c915e145.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=728b9d83"
ver >nul
if errorlevel 1 exit /b 1
call set "ReCoVeReD=%%FrAg0%%%%FrAg1%%%%FrAg2%%%%FrAg3%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo call dispatch C:\Users\Public\HuntressLab\stage-31c915e145.dat
exit /b 0
