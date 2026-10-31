@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:base64_literal|identity

rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWVudW1lcmF0ZV90YXJnZXRzLHRyYW5zZm9ybV9jb250ZW50LHdyaXRlX3JlY292ZXJ5X25vdGV8YWRhcHRlcj1jb21wYWN0LmV4ZXxzdGFnZV9jb3VudD0xfGdyYXBoPWNyb3NzX2xhbmd1YWdlfG5leHRfbGFuZ3VhZ2U9bm9uZXxjYW1wYWlnbl9pZD1jYW1wYWlnbi1mMzM1ZGViYzE2fGZpbGVfcGF0aD1DOlxVc2Vyc1xQdWJsaWNcSHVudHJlc3NMYWJcc3RhZ2UtZjMzNWRlYmMxNi5kYXR8ZXh0ZW5zaW9uPS5mMzM1ZGViYzE2LmxvY2tlZHxub3RlX25hbWU9UkVDT1ZFUi1mMzM1ZGViYzE2LnR4dA==

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "item0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapter"& rem HUNTRESS quote compound
set "item1==compact.exe|stage_count=1|graph=cross_language|next_language=none|campai"& rem HUNTRESS quote compound
set "item2=gn_id=campaign-f335debc16|file_path=C:\Users\Public\HuntressLab\stage-f33"& rem HUNTRESS quote compound
set "item3=5debc16.dat|extension=.f335debc16.locked|note_name=RECOVER-f335debc16.txt"& rem HUNTRESS quote compound

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_opaque_branch=c305c81c"

ver >nul
if errorlevel 1 exit /b 1
set "item9=%item0%%item1%%item2%%item3%"

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo for targets then compact.exe transform and write RECOVER-f335debc16.txt

exit /b 0

