@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:hex_pairs|identity

rem HUNTRESS-MATERIAL:763d317c73746570733d6465636f64655f656d6265646465642c77726974655f66696c657c616461707465723d657870616e642e6578657c73746167655f636f756e743d317c67726170683d66616e5f6f75747c6e6578745f6c616e67756167653d6e6f6e657c63616d706169676e5f69643d63616d706169676e2d663962356661383635367c66696c655f706174683d433a5c55736572735c5075626c69635c48756e74726573734c61625c73746167652d663962356661383635362e646174

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "h0=v=1|steps=decode_embedded,write_file|adapter=expa"& rem HUNTRESS quote compound
set "h1=nd.exe|stage_count=1|graph=fan_out|next_language="& rem HUNTRESS quote compound
set "h2=none|campaign_id=campaign-f9b5fa8656|file_path=C:"& rem HUNTRESS quote compound
set "h3=\Users\Public\HuntressLab\stage-f9b5fa8656.dat"& rem HUNTRESS quote compound

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

rem no neutral statements

call set "cfg=%%h0%%%%h1%%%%h2%%%%h3%%"

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo expand.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-f9b5fa8656.dat

exit /b 0

