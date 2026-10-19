@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:hex_pairs|identity

rem HUNTRESS-MATERIAL:763d317c73746570733d6c6f636174655f6c6f63616c2c64697370617463685f70726f636573737c616461707465723d73746172747c73746167655f636f756e743d317c67726170683d73696e676c657c6e6578745f6c616e67756167653d6e6f6e657c63616d706169676e5f69643d63616d706169676e2d643630303133313330637c66696c655f706174683d433a5c55736572735c5075626c69635c48756e74726573734c61625c73746167652d643630303133313330632e646174

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "v_a0=v=1|steps=locate_local,dispatch_process|adapter="
set "v_a1=start|stage_count=1|graph=single|next_language=n"
set "v_a2=one|campaign_id=campaign-d60013130c|file_path=C:"
set "v_a3=\Users\Public\HuntressLab\stage-d60013130c.dat"

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_opaque_branch=36a87cfe"

set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "cfg=%v_a0%%v_a1%%v_a2%%v_a3%"

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo start dispatch C:\Users\Public\HuntressLab\stage-d60013130c.dat

exit /b 0

