@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|reverse
rem HUNTRESS-MATERIAL:646d632e636663396666613264642d65676174733d65676174735f7478656e7c7461642e636663396666613264642d65676174735c62614c73736572746e75485c63696c6275505c73726573555c3a433d687461705f656c69667c7461642e64383739386635642f64696c61766e692e656c706d6178652e636663396666613264642f2f3a73707474683d6c72757c636663396666613264642d6e676961706d61633d64695f6e676961706d61637c68637461623d65676175676e616c5f7478656e7c65676175676e616c5f656d61733d68706172677c343d746e756f635f65676174737c6578652e32337276736765723d726574706164617c7470697263735f66666f646e61682c737365636f72705f68637461707369642c656c69665f65746972772c65746f6d65725f657269757163613d73706574737c313d76
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "item0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=regs"
SeT "item1=vr32.exe|stage_count=4|graph=same_language|next_language=batch|campaign_id=campa"
SeT "item2=ign-dd2aff9cfc|url=https://dd2aff9cfc.example.invalid/d5f8978d.dat|file_path=C:\"
SeT "item3=Users\Public\HuntressLab\stage-dd2aff9cfc.dat|next_stage=stage-dd2aff9cfc.cmd"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=0c34e9eb"
ver >nul
if errorlevel 1 exit /b 1
set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo regsvr32.exe acquire, write, dispatch, and hand off stage-dd2aff9cfc.cmd
exit /b 0
