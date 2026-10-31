@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|xor_5a
rem HUNTRESS-MATERIAL:2c676b26292e3f2a29673f342f373f283b2e3f052e3b283d3f2e29762e283b34293c352837053935342e3f342e762d28332e3f05283f39352c3f28230534352e3f263b3e3b2a2e3f28673935372a3b392e743f223f26292e3b3d3f0539352f342e676b263d283b2a32673e333b3735343e26343f222e05363b343d2f3b3d3f673435343f26393b372a3b333d3405333e67393b372a3b333d34776d686d6f683c62623e3c263c33363f052a3b2e32671960060f293f2829060a2f3836333906122f342e283f2929163b3806292e3b3d3f776d686d6f683c62623e3c743e3b2e263f222e3f342933353467746d686d6f683c62623e3c74363539313f3e2634352e3f05343b373f67081f19150c1f08776d686d6f683c62623e3c742e222e
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set h0=v=1^|steps=enumerate_targets,transform_content,write_recovery_note^|adapte
set h1=r=compact.exe^|stage_count=1^|graph=diamond^|next_language=none^|campaign_id
set h2==campaign-72752f88df^|file_path=C:\Users\Public\HuntressLab\stage-72752f8
set h3=8df.dat^|extension=.72752f88df.locked^|note_name=RECOVER-72752f88df.txt
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=bbabd163"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo for targets then compact.exe transform and write RECOVER-72752f88df.txt
exit /b 0
