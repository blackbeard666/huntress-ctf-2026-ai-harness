@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|reverse
rem HUNTRESS-MATERIAL:7478742e376161336632313161372d5245564f4345523d656d616e5f65746f6e7c64656b636f6c2e376161336632313161372e3d6e6f69736e657478657c7461642e376161336632313161372d65676174735c62614c73736572746e75485c63696c6275505c73726573555c3a433d687461705f656c69667c376161336632313161372d6e676961706d61633d64695f6e676961706d61637c656e6f6e3d65676175676e616c5f7478656e7c79727465725f6b6361626c6c61663d68706172677c313d746e756f635f65676174737c6578652e746361706d6f633d726574706164617c65746f6e5f797265766f6365725f65746972772c746e65746e6f635f6d726f66736e6172742c737465677261745f65746172656d756e653d73706574737c313d76
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set v_a0=v=1^|steps=enumerate_targets,transform_content,write_recovery_note^|adapter
set v_a1==compact.exe^|stage_count=1^|graph=fallback_retry^|next_language=none^|campai
set v_a2=gn_id=campaign-7a112f3aa7^|file_path=C:\Users\Public\HuntressLab\stage-7a1
set v_a3=12f3aa7.dat^|extension=.7a112f3aa7.locked^|note_name=RECOVER-7a112f3aa7.txt
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=4acfa4aa"
set "cfg=!v_a0!!v_a1!!v_a2!!v_a3!"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo for targets then compact.exe transform and write RECOVER-7a112f3aa7.txt
exit /b 0
