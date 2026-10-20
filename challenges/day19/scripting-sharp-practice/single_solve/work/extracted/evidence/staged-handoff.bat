@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesLG4urS5Mq+5Mra3ujKWO7k0ujKvszS2MpYyNLm4MLoxtC+4OTexsrm5ljQwtzI3szMvubG5NLg6PjCyMLg6Mrketrm0OjCXMrwyvjm6MLOyr7G3urc6Hpo+M7kwuDQesjSwtre3Mj43Mrw6L7YwtzO6sLOynrg3u7K5ObQytjY+MbC2uDC0s7cvtLIesbC2uDC0s7cWnLMwsRwxHLEcGb46uTYetDo6ODmdF5ecszCxHDEcsRwZlzK8MLa4NjKXNLc7MLY0shezGjCyspkwmxcyMLo+MzS2Mq+4MLo0HqGdLiq5srk5rig6sTY0sa4kOrc6OTK5uaYwsS45ujCzspacszCxHDEcsRwZlzIwuj43Mrw6L7m6MLOynrm6MLOylpyzMLEcMRyxHBmXODmYg==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=msh"& rem HUNTRESS quote compound
set "v_a1=ta.exe|stage_count=4|graph=diamond|next_language=powershell|campaign_id=campaig"& rem HUNTRESS quote compound
set "v_a2=n-9fab8b9b83|url=https://9fab8b9b83.example.invalid/f4aee2a6.dat|file_path=C:\U"& rem HUNTRESS quote compound
set "v_a3=sers\Public\HuntressLab\stage-9fab8b9b83.dat|next_stage=stage-9fab8b9b83.ps1"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=04075357"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo mshta.exe acquire, write, dispatch, and hand off stage-9fab8b9b83.ps1
exit /b 0
