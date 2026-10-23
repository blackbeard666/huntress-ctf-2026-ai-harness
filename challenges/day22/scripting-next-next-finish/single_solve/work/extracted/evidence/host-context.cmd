@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|reverse_xor
rem HUNTRESS-MATERIAL:BwVQBwFSAVEGAx5HQFxbDldabEdAXFtPBwVQBwFSAVEGAx5dVFpSQ15SUA5XWmxdVFpSQ15SUE9WXVxdDlZUUkZUXVJfbEdLVl1PV11cXlJaVw5bQ1JBVE8CDkddRlxQbFZUUkdAT0dWQA5BVkdDUldST11cWkdSQUZUWlVdXFBsXUFGR1ZBH11cWkdSQUZUWlVdXFBsVldcUFZXDkBDVkdATwIORQ==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=decode_configuration,return_conf"& rem HUNTRESS quote compound
set "v_a1=iguration|adapter=set|stage_count=1|graph="& rem HUNTRESS quote compound
set "v_a2=diamond|next_language=none|campaign_id=cam"& rem HUNTRESS quote compound
set "v_a3=paign-05b2a24c64|host_id=host-05b2a24c64"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=217e7831"
ver >nul
if errorlevel 1 exit /b 1
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-05b2a24c64
exit /b 0
