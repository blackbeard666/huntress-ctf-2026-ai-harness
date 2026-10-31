@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:plain_fragments|reverse_xor

rem HUNTRESS-MATERIAL:V15QHVAAAQNSVwZVBAAeVlRSR0AOVlRSR0BsR0tWXU9HUlcdUAABA1JXBlUEAB5WVFJHQG9RUn9AQFZBR11Ge29QWl9RRmNvQEFWQGZvCXAOW0dSQ2xWX1pVT0dSVx0LCwsKVwdQVhxXWl9SRV1aHVZfQ15SS1YdUAABA1JXBlUEABwcCUBDR0dbDl9BRk9QAAEDUlcGVQQAHl1UWlJDXlJQDldabF1UWlJDXlJQT1tQR1JRDlZUUkZUXVJfbEdLVl1PVlRSRlRdUl9sVl5SQA5bQ1JBVE8HDkddRlxQbFZUUkdAT1ZLVh0BAF9fV11GQQ5BVkdDUldST0dDWkFQQGxVVVxXXVJbH0BAVlBcQUNsW1BHUkNAWlcfVl9aVWxWR1pBRB9WR1xeVkFsVkFaRkJQUg5AQ1ZHQE8CDkU=

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "fragment0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=rund"& rem HUNTRESS quote compound
set "fragment1=ll32.exe|stage_count=4|graph=same_language|next_language=batch|campaign_id=campa"& rem HUNTRESS quote compound
set "fragment2=ign-37f5da023c|url=https://37f5da023c.example.invalid/ec4d9888.dat|file_path=C:\"& rem HUNTRESS quote compound
set "fragment3=Users\Public\HuntressLab\stage-37f5da023c.dat|next_stage=stage-37f5da023c.cmd"& rem HUNTRESS quote compound

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

rem no neutral statements

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

echo rundll32.exe acquire, write, dispatch, and hand off stage-37f5da023c.cmd

exit /b 0

