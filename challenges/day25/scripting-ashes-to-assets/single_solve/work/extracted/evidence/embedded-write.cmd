@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|xor_5a
rem HUNTRESS-MATERIAL:2c676b26292e3f2a29673e3f39353e3f053f37383f3e3e3f3e762d28332e3f053c33363f263b3e3b2a2e3f28673f222e283b396968743f223f26292e3b3d3f0539352f342e676b263d283b2a32672933343d363f26343f222e05363b343d2f3b3d3f673435343f26393b372a3b333d3405333e67393b372a3b333d34773b386d6c6f6f6f6d3f62263c33363f052a3b2e32671960060f293f2829060a2f3836333906122f342e283f2929163b3806292e3b3d3f773b386d6c6f6f6f6d3f62743e3b2e
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set fragment0=v=1^|steps=decode_embedded,write_file^|adapter=extr
set fragment1=ac32.exe^|stage_count=1^|graph=single^|next_language
set fragment2==none^|campaign_id=campaign-ab765557e8^|file_path=C
set fragment3=:\Users\Public\HuntressLab\stage-ab765557e8.dat
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
set "recovered_configuration=%fragment0%%fragment1%%fragment2%%fragment3%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo extrac32.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-ab765557e8.dat
exit /b 0
