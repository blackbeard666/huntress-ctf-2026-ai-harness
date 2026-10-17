@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:hex_pairs|xor_5a

rem HUNTRESS-MATERIAL:2c676b26292e3f2a29673b392b2f33283f05283f37352e3f762d28332e3f053c33363f263b3e3b2a2e3f286738332e293b3e373334743f223f26292e3b3d3f0539352f342e676b263d283b2a3267293b373f05363b343d2f3b3d3f26343f222e05363b343d2f3b3d3f673435343f26393b372a3b333d3405333e67393b372a3b333d34776e6a69693c696d6e6a6e262f283667322e2e2a296075756e6a69693c696d6e6a6e743f223b372a363f7433342c3b36333e756d63386a6b6b683f743e3b2e263c33363f052a3b2e32671960060f293f2829060a2f3836333906122f342e283f2929163b3806292e3b3d3f776e6a69693c696d6e6a6e743e3b2e

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set item0=v=1^|steps=acquire_remote,write_file^|adapter=bitsadmin.exe^|stage_
set item1=count=1^|graph=same_language^|next_language=none^|campaign_id=campa
set item2=ign-4033f37404^|url=https://4033f37404.example.invalid/79b0112e.d
set item3=at^|file_path=C:\Users\Public\HuntressLab\stage-4033f37404.dat

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

set "neutral_opaque_branch=dbc6f1fd"

set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "item9=%item0%%item1%%item2%%item3%"

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo bitsadmin.exe acquire https://4033f37404.example.invalid/79b0112e.dat to C:\Users\Public\HuntressLab\stage-4033f37404.dat

exit /b 0

