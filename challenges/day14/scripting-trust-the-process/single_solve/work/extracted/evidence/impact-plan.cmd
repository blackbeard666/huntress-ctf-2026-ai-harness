@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|identity
rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWVudW1lcmF0ZV90YXJnZXRzLHRyYW5zZm9ybV9jb250ZW50LHdyaXRlX3JlY292ZXJ5X25vdGV8YWRhcHRlcj1mb3J8c3RhZ2VfY291bnQ9MXxncmFwaD1mYWxsYmFja19yZXRyeXxuZXh0X2xhbmd1YWdlPW5vbmV8Y2FtcGFpZ25faWQ9Y2FtcGFpZ24tMGZmZDFhYTA2ZnxmaWxlX3BhdGg9QzpcVXNlcnNcUHVibGljXEh1bnRyZXNzTGFiXHN0YWdlLTBmZmQxYWEwNmYuZGF0fGV4dGVuc2lvbj0uMGZmZDFhYTA2Zi5sb2NrZWR8bm90ZV9uYW1lPVJFQ09WRVItMGZmZDFhYTA2Zi50eHQ=
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "v_a0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapt"
SeT "v_a1=er=for|stage_count=1|graph=fallback_retry|next_language=none|campaign_i"
SeT "v_a2=d=campaign-0ffd1aa06f|file_path=C:\Users\Public\HuntressLab\stage-0ffd1"
SeT "v_a3=aa06f.dat|extension=.0ffd1aa06f.locked|note_name=RECOVER-0ffd1aa06f.txt"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=1d6dad6a"
ver >nul
if errorlevel 1 exit /b 1
set "cfg=%v_a0%%v_a1%%v_a2%%v_a3%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo for targets then for transform and write RECOVER-0ffd1aa06f.txt
exit /b 0
