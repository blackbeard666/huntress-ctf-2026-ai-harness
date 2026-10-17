@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|identity
rem HUNTRESS-MATERIAL:763d317c73746570733d656e756d65726174655f746172676574732c7472616e73666f726d5f636f6e74656e742c77726974655f7265636f766572795f6e6f74657c616461707465723d666f727c73746167655f636f756e743d317c67726170683d66616e5f6f75747c6e6578745f6c616e67756167653d6e6f6e657c63616d706169676e5f69643d63616d706169676e2d626333646638623664637c66696c655f706174683d433a5c55736572735c5075626c69635c48756e74726573734c61625c73746167652d626333646638623664632e6461747c657874656e73696f6e3d2e626333646638623664632e6c6f636b65647c6e6f74655f6e616d653d5245434f5645522d626333646638623664632e747874
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "v_a0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adap"
SeT "v_a1=ter=for|stage_count=1|graph=fan_out|next_language=none|campaign_id=cam"
SeT "v_a2=paign-bc3df8b6dc|file_path=C:\Users\Public\HuntressLab\stage-bc3df8b6d"
SeT "v_a3=c.dat|extension=.bc3df8b6dc.locked|note_name=RECOVER-bc3df8b6dc.txt"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=c298e2d6"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg=!v_a0!!v_a1!!v_a2!!v_a3!"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo for targets then for transform and write RECOVER-bc3df8b6dc.txt
exit /b 0
