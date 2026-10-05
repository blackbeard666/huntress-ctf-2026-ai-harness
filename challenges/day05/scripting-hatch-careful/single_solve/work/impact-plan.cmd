@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:base64_literal|identity

rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWVudW1lcmF0ZV90YXJnZXRzLHRyYW5zZm9ybV9jb250ZW50LHdyaXRlX3JlY292ZXJ5X25vdGV8YWRhcHRlcj1jaXBoZXIuZXhlfHN0YWdlX2NvdW50PTF8Z3JhcGg9Y3Jvc3NfbGFuZ3VhZ2V8bmV4dF9sYW5ndWFnZT1ub25lfGNhbXBhaWduX2lkPWNhbXBhaWduLTJkNzFiNjg2MjV8ZmlsZV9wYXRoPUM6XFVzZXJzXFB1YmxpY1xIdW50cmVzc0xhYlxzdGFnZS0yZDcxYjY4NjI1LmRhdHxleHRlbnNpb249LjJkNzFiNjg2MjUubG9ja2VkfG5vdGVfbmFtZT1SRUNPVkVSLTJkNzFiNjg2MjUudHh0

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

SeT "FrAg0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapter"
SeT "FrAg1==cipher.exe|stage_count=1|graph=cross_language|next_language=none|campaig"
SeT "FrAg2=n_id=campaign-2d71b68625|file_path=C:\Users\Public\HuntressLab\stage-2d71"
SeT "FrAg3=b68625.dat|extension=.2d71b68625.locked|note_name=RECOVER-2d71b68625.txt"

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=cc6b8f5c"

ver >nul
if errorlevel 1 exit /b 1
set "ReCoVeReD="
for %%G in (0 1 2 3) do call set "ReCoVeReD=%%ReCoVeReD%%%%FrAg%%G%%"

echo(!ReCoVeReD!

exit /b 0

:HUNTRESS_PLAN

echo for targets then cipher.exe transform and write RECOVER-2d71b68625.txt

exit /b 0

