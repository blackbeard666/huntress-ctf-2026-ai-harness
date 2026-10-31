@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesrc6trK5MLoyr7owuTOyujmWOjkwtzmzN7k2r7G3tzoytzoWO7k0ujKvuTKxt7syuTyvtze6Mr4wsjC4OjK5HrM3uT45ujCzsq+xt7q3Oh6YvjO5MLg0HrMwty+3uro+NzK8Oi+2MLczurCzsp63N7cyvjGwtrgwtLO3L7SyHrGwtrgwtLO3FpixGrCanBgbMjC+MzS2Mq+4MLo0HqGdLiq5srk5rig6sTY0sa4kOrc6OTK5uaYwsS45ujCzspaYsRqwmpwYGzIwlzIwuj4yvDoytzm0t7celxixGrCanBgbMjCXNjextbKyPjc3ujKvtzC2sp6pIqGnqyKpFpixGrCanBgbMjCXOjw6A==
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adap"& rem HUNTRESS quote compound
set "item1=ter=for|stage_count=1|graph=fan_out|next_language=none|campaign_id=cam"& rem HUNTRESS quote compound
set "item2=paign-1b5a5806da|file_path=C:\Users\Public\HuntressLab\stage-1b5a5806d"& rem HUNTRESS quote compound
set "item3=a.dat|extension=.1b5a5806da.locked|note_name=RECOVER-1b5a5806da.txt"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=eb75ffba"
ver >nul
if errorlevel 1 exit /b 1
set "item9=!item0!!item1!!item2!!item3!"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo for targets then for transform and write RECOVER-1b5a5806da.txt
exit /b 0
