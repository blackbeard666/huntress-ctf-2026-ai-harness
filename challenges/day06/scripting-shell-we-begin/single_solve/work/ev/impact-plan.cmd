@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|xor_5a
rem HUNTRESS-MATERIAL:2c676b26292e3f2a29673f342f373f283b2e3f052e3b283d3f2e29762e283b34293c352837053935342e3f342e762d28332e3f05283f39352c3f28230534352e3f263b3e3b2a2e3f28673c352826292e3b3d3f0539352f342e676b263d283b2a32673c3b3636383b393105283f2e282326343f222e05363b343d2f3b3d3f673435343f26393b372a3b333d3405333e67393b372a3b333d34776a3f3c6a3b6c68383963263c33363f052a3b2e32671960060f293f2829060a2f3836333906122f342e283f2929163b3806292e3b3d3f776a3f3c6a3b6c68383963743e3b2e263f222e3f342933353467746a3f3c6a3b6c6838396374363539313f3e2634352e3f05343b373f67081f19150c1f08776a3f3c6a3b6c68383963742e222e
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapt"& rem HUNTRESS quote compound
set "FrAg1=er=for|stage_count=1|graph=fallback_retry|next_language=none|campaign_i"& rem HUNTRESS quote compound
set "FrAg2=d=campaign-0ef0a62bc9|file_path=C:\Users\Public\HuntressLab\stage-0ef0a"& rem HUNTRESS quote compound
set "FrAg3=62bc9.dat|extension=.0ef0a62bc9.locked|note_name=RECOVER-0ef0a62bc9.txt"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=d8a2d32f"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY call set "ReCoVeReD=%%FrAg0%%%%FrAg1%%%%FrAg2%%%%FrAg3%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo for targets then for transform and write RECOVER-0ef0a62bc9.txt
exit /b 0
