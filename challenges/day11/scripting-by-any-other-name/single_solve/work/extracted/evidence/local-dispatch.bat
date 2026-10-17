@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|reverse
rem HUNTRESS-MATERIAL:7461642e663963616664653133392d65676174735c62614c73736572746e75485c63696c6275505c73726573555c3a433d687461705f656c69667c663963616664653133392d6e676961706d61633d64695f6e676961706d61637c656e6f6e3d65676175676e616c5f7478656e7c656c676e69733d68706172677c313d746e756f635f65676174737c74726174733d726574706164617c737365636f72705f68637461707369642c6c61636f6c5f657461636f6c3d73706574737c313d76
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=locate_local,dispatch_process|adapter="
set "v_a1=start|stage_count=1|graph=single|next_language=n"
set "v_a2=one|campaign_id=campaign-931edfac9f|file_path=C:"
set "v_a3=\Users\Public\HuntressLab\stage-931edfac9f.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=0817a45d"
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
echo start dispatch C:\Users\Public\HuntressLab\stage-931edfac9f.dat
exit /b 0
