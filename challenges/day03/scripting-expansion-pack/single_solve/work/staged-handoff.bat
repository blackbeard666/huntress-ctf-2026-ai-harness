@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|identity
rem HUNTRESS-MATERIAL:zpmL2YjYyMzMzM2Y40SZnFGdz1TZnFGdz9Fd4Vmb8RXYk5iN2ImMzMzMjNGOtU2ZhR3ccJWYMN3clJHduVHScNWasJWdQx1cyV2cVxlOD1Da0FGcfVGbpZGf0FGZuIGOzYTMmhzNvQWasFmdulmLlxGctFGel5iN2ImMzMzMjNGOv8iOzBHd0hWPsJXd8ZjNiJzMzMzYjhTLudWahBXbhNWPkl2XudWahBXbhNGf0BXayN2cq1TZnFWdn5WYs9Fd4Vmb8V2ZhV3ZuFGbfN3cvJ3Y9gGchJ3Z8RTP05WdvN2XldWY0NHflhXZuQHcpJ3YzNWPyVGdwFGZhxHdwlmcjN3XmZ2bk5WYoxyczV2YvJHcfh2Y0FGczlGZsUGbpZ2XlRXaydHLlR3btVmcfVmcpVXcjFWPzBXZ0NHfx0jd
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=cscr"
set "fragment1=ipt.exe|stage_count=4|graph=cross_language|next_language=jscript|campaign_id=cam"
set "fragment2=paign-8cc3332b66|url=https://8cc3332b66.example.invalid/78f1638b.dat|file_path=C"
set "fragment3=:\Users\Public\HuntressLab\stage-8cc3332b66.dat|next_stage=stage-8cc3332b66.js"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=02b5548b"
ver >nul
if errorlevel 1 exit /b 1
call set "recovered_configuration=%%fragment0%%%%fragment1%%%%fragment2%%%%fragment3%%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo cscript.exe acquire, write, dispatch, and hand off stage-8cc3332b66.js
exit /b 0
