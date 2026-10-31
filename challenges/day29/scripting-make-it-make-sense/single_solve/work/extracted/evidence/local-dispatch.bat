@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|reverse_xor
rem HUNTRESS-MATERIAL:==QROIwTAdkVDBkDfxFUSdkVs9FXQJ1XfclWANkUHB1WsNUQcBlVAB0TSdlUDdkVB5AUedVHWtkVPB0RSRlVsBFXG11ROIwTUFkUDtlDAJlXWx2XS1FVGJFVW9UXWt0Rs9lUdRlRSRlVO0FXdZ1TQJlXDJlWU1FbadlDQJlXDJlWU1lHCAVURZQUKAVVG8UVa9lVsNkUHtlDwlwbmBkVBB0bjZUUfpFUvtnRddUQWBEQ/JVUvB0RSRlVeIAURFlBRpAUVZQHXJ1R
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=locate_local,dispatch_process|adapter=cm"& rem HUNTRESS quote compound
set "v_a1=d.exe|stage_count=1|graph=same_language|next_langu"& rem HUNTRESS quote compound
set "v_a2=age=none|campaign_id=campaign-1cbb5b9cf5|file_path"& rem HUNTRESS quote compound
set "v_a3==C:\Users\Public\HuntressLab\stage-1cbb5b9cf5.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=2700fa84"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo cmd.exe dispatch C:\Users\Public\HuntressLab\stage-1cbb5b9cf5.dat
exit /b 0
