@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|reverse
rem HUNTRESS-MATERIAL:=YXPxw3c0VGcz1DbvNWY0V2Xs92YhxGLkl2cwFGdjh2XwJ3bjV2czxXYkFGc0Vmc9MWbk5SZ4VGfzRXYnV2Xj9WduRXPxw3ZyFGco1zYy92cz9Fbh52Z1F2ZlxnblhHdfxWYudWdhdWZ942buVGfjFWbwFWan52XpRWPjFWbwFWan5WL1MTOkhDNkZmYlxnZpxWZfBXY0hWPDpDXVNXZyNHXQVnYsl2YchUduRnclN3cMFmYcNHdhdWZtUzM5QGO0QmZiVmLkFGd
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=locate_local,dispatch_process|adapter=cm"& rem HUNTRESS quote compound
set "v_a1=d.exe|stage_count=1|graph=cross_language|next_lang"& rem HUNTRESS quote compound
set "v_a2=uage=none|campaign_id=campaign-539d84dfbe|file_pat"& rem HUNTRESS quote compound
set "v_a3=h=C:\Users\Public\HuntressLab\stage-539d84dfbe.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo cmd.exe dispatch C:\Users\Public\HuntressLab\stage-539d84dfbe.dat
exit /b 0
