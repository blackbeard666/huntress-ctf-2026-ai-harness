@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesrc6trK5MLoyr7owuTOyujmWOjkwtzmzN7k2r7G3tzoytzoWO7k0ujKvuTKxt7syuTyvtze6Mr4wsjC4OjK5HrG3trgwsboXMrwyvjm6MLOyr7G3urc6Hpi+M7kwuDQeszC2NjEwsbWvuTK6OTy+NzK8Oi+2MLczurCzsp63N7cyvjGwtrgwtLO3L7SyHrGwtrgwtLO3FpsaspkcmJiasJw+MzS2Mq+4MLo0HqGdLiq5srk5rig6sTY0sa4kOrc6OTK5uaYwsS45ujCzspabGrKZHJiYmrCcFzIwuj4yvDoytzm0t7celxsaspkcmJiasJwXNjextbKyPjc3ujKvtzC2sp6pIqGnqyKpFpsaspkcmJiasJwXOjw6A==
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapter"
set "v_a1==compact.exe|stage_count=1|graph=fallback_retry|next_language=none|campai"
set "v_a2=gn_id=campaign-65e29115a8|file_path=C:\Users\Public\HuntressLab\stage-65e"
set "v_a3=29115a8.dat|extension=.65e29115a8.locked|note_name=RECOVER-65e29115a8.txt"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=ceea29a0"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo for targets then compact.exe transform and write RECOVER-65e29115a8.txt
exit /b 0
