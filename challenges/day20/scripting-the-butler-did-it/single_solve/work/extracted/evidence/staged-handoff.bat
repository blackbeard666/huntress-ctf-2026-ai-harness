@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesLG4urS5Mq+5Mra3ujKWO7k0ujKvszS2MpYyNLm4MLoxtC+4OTexsrm5ljQwtzI3szMvubG5NLg6PjCyMLg6MrkesbmxuTS4OhcyvDK+Obows7Kvsbe6tzoemj4zuTC4NB6zMLY2MTCxta+5Mro5PL43Mrw6L7YwtzO6sLOynrg3u7K5ObQytjY+MbC2uDC0s7cvtLIesbC2uDC0s7cWmrGbGpiYsjGbsL46uTYetDo6ODmdF5easZsamJiyMZuwlzK8MLa4NjKXNLc7MLY0shexG7EYMpoYGZcyMLo+MzS2Mq+4MLo0HqGdLiq5srk5rig6sTY0sa4kOrc6OTK5uaYwsS45ujCzspaasZsamJiyMZuwlzIwuj43Mrw6L7m6MLOynrm6MLOylpqxmxqYmLIxm7CXODmYg==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=cscri"& rem HUNTRESS quote compound
set "fragment1=pt.exe|stage_count=4|graph=fallback_retry|next_language=powershell|campaign_id=ca"& rem HUNTRESS quote compound
set "fragment2=mpaign-5c6511dc7a|url=https://5c6511dc7a.example.invalid/b7b0e403.dat|file_path=C"& rem HUNTRESS quote compound
set "fragment3=:\Users\Public\HuntressLab\stage-5c6511dc7a.dat|next_stage=stage-5c6511dc7a.ps1"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=28db022d"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo cscript.exe acquire, write, dispatch, and hand off stage-5c6511dc7a.ps1
exit /b 0
