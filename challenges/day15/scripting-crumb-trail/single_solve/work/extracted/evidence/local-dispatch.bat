@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|xor_5a
rem HUNTRESS-MATERIAL:2c676b26292e3f2a29673635393b2e3f053635393b36763e33292a3b2e3932052a2835393f2929263b3e3b2a2e3f286739373e743f223f26292e3b3d3f0539352f342e676b263d283b2a32673e333b3735343e26343f222e05363b343d2f3b3d3f673435343f26393b372a3b333d3405333e67393b372a3b333d3477393e3c683b6a6d6a6e6e263c33363f052a3b2e32671960060f293f2829060a2f3836333906122f342e283f2929163b3806292e3b3d3f77393e3c683b6a6d6a6e6e743e3b2e
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=locate_local,dispatch_process|adapter=c"
set "fragment1=md.exe|stage_count=1|graph=diamond|next_language="
set "fragment2=none|campaign_id=campaign-cdf2a07044|file_path=C:"
set "fragment3=\Users\Public\HuntressLab\stage-cdf2a07044.dat"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=2cc4e209"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
call set "recovered_configuration=%%fragment0%%%%fragment1%%%%fragment2%%%%fragment3%%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo cmd.exe dispatch C:\Users\Public\HuntressLab\stage-cdf2a07044.dat
exit /b 0
