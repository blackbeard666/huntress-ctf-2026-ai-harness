@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|reverse
rem HUNTRESS-MATERIAL:7478742e353062363238396339382d5245564f4345523d656d616e5f65746f6e7c64656b636f6c2e353062363238396339382e3d6e6f69736e657478657c7461642e353062363238396339382d65676174735c62614c73736572746e75485c63696c6275505c73726573555c3a433d687461705f656c69667c353062363238396339382d6e676961706d61633d64695f6e676961706d61637c656e6f6e3d65676175676e616c5f7478656e7c65676175676e616c5f73736f72633d68706172677c313d746e756f635f65676174737c726f663d726574706164617c65746f6e5f797265766f6365725f65746972772c746e65746e6f635f6d726f66736e6172742c737465677261745f65746172656d756e653d73706574737c313d76
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapt"
set "h1=er=for|stage_count=1|graph=cross_language|next_language=none|campaign_i"
set "h2=d=campaign-89c9826b05|file_path=C:\Users\Public\HuntressLab\stage-89c98"
set "h3=26b05.dat|extension=.89c9826b05.locked|note_name=RECOVER-89c9826b05.txt"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=19292da2"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "cfg=%h0%%h1%%h2%%h3%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo for targets then for transform and write RECOVER-89c9826b05.txt
exit /b 0
