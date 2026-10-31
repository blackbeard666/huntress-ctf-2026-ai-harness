@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RHN2amh7bGZzdmpoczNrcHp3aHtqb2Z3eXZqbHp6g2hraHd7bHlEentoeXuDentobmxmanZ8dXtEOINueWh3b0RrcGh0dnVrg3Vsf3tmc2h1bnxobmxEdXZ1bINqaHR3aHBudWZwa0RqaHR3aHBudTRpPGw6aDk4aTtAg21wc2xmd2h7b0RKQWNcemx5emNXfGlzcGpjT3x1e3lsenpTaGljentobmw0aTxsOmg5OGk7QDVraHs=
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=locate_local,dispatch_process|adapter="
set "v_a1=start|stage_count=1|graph=diamond|next_language="
set "v_a2=none|campaign_id=campaign-b5e3a21b49|file_path=C"
set "v_a3=:\Users\Public\HuntressLab\stage-b5e3a21b49.dat"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
set "cfg=!v_a0!!v_a1!!v_a2!!v_a3!"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo start dispatch C:\Users\Public\HuntressLab\stage-b5e3a21b49.dat
exit /b 0
