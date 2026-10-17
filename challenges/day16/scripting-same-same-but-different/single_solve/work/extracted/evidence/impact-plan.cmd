@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|add_7
rem HUNTRESS-MATERIAL:fUQ4g3p7bHd6RGx1fHRseWh7bGZ7aHlubHt6M3t5aHV6bXZ5dGZqdnV7bHV7M355cHtsZnlsanZ9bHmAZnV2e2yDaGtod3tseURqcHdvbHk1bH9sg3p7aG5sZmp2fHV7RDiDbnlod29Ec3B1bGh5g3Vsf3tmc2h1bnxobmxEdXZ1bINqaHR3aHBudWZwa0RqaHR3aHBudTQ/aD47aj9Aazdsg21wc2xmd2h7b0RKQWNcemx5emNXfGlzcGpjT3x1e3lsenpTaGljentobmw0P2g+O2o/QGs3bDVraHuDbH97bHV6cHZ1RDU/aD47aj9AazdsNXN2anJsa4N1dntsZnVodGxEWUxKVl1MWTQ/aD47aj9AazdsNXt/ew==
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapt"
set "fragment1=er=cipher.exe|stage_count=1|graph=linear|next_language=none|campaign_id"
set "fragment2==campaign-8a74c89d0e|file_path=C:\Users\Public\HuntressLab\stage-8a74c8"
set "fragment3=9d0e.dat|extension=.8a74c89d0e.locked|note_name=RECOVER-8a74c89d0e.txt"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=8d237fa2"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "recovered_configuration=%%fragment0%%%%fragment1%%%%fragment2%%%%fragment3%%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo for targets then cipher.exe transform and write RECOVER-8a74c89d0e.txt
exit /b 0
