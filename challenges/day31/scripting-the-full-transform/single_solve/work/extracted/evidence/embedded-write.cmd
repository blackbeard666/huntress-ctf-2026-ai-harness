@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:split_fragments|identity

rem HUNTRESS-MATERIAL:dj0xfHN0ZXBzPWRlY29kZV9lbWJlZGRlZCx3cml0ZV9maWxlfGFkYXB0ZXI9ZXhwYW5kLmV4ZXxzdGFnZV9jb3VudD0xfGdyYXBoPXNhbWVfbGFuZ3VhZ2V8bmV4dF9sYW5ndWFnZT1ub25lfGNhbXBhaWduX2lkPWNhbXBhaWduLWVjNjQwMzVjMzh8ZmlsZV9wYXRoPUM6XFVzZXJzXFB1YmxpY1xIdW50cmVzc0xhYlxzdGFnZS1lYzY0MDM1YzM4LmRhdA==

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set v_a0=v=1^|steps=decode_embedded,write_file^|adapter=expan
set v_a1=d.exe^|stage_count=1^|graph=same_language^|next_langu
set v_a2=age=none^|campaign_id=campaign-ec64035c38^|file_path
set v_a3==C:\Users\Public\HuntressLab\stage-ec64035c38.dat

goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=6812051e"

ver >nul
if errorlevel 1 exit /b 1
set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%v_a%%G%%"

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo expand.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-ec64035c38.dat

exit /b 0

