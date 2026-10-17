@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|identity
rem HUNTRESS-MATERIAL:763d317c73746570733d656e756d65726174655f746172676574732c7472616e73666f726d5f636f6e74656e742c77726974655f7265636f766572795f6e6f74657c616461707465723d636f6d706163742e6578657c73746167655f636f756e743d317c67726170683d6c696e6561727c6e6578745f6c616e67756167653d6e6f6e657c63616d706169676e5f69643d63616d706169676e2d333364343466353566367c66696c655f706174683d433a5c55736572735c5075626c69635c48756e74726573734c61625c73746167652d333364343466353566362e6461747c657874656e73696f6e3d2e333364343466353566362e6c6f636b65647c6e6f74655f6e616d653d5245434f5645522d333364343466353566362e747874
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapt"
set "item1=er=compact.exe|stage_count=1|graph=linear|next_language=none|campaign_i"
set "item2=d=campaign-33d44f55f6|file_path=C:\Users\Public\HuntressLab\stage-33d44"
set "item3=f55f6.dat|extension=.33d44f55f6.locked|note_name=RECOVER-33d44f55f6.txt"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=f3e556ff"
set "item9=%item0%%item1%%item2%%item3%"
echo(!item9!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo for targets then compact.exe transform and write RECOVER-33d44f55f6.txt
exit /b 0
