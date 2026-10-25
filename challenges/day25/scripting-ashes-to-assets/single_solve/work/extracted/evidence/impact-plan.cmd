@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|reverse
rem HUNTRESS-MATERIAL:dHh0Ljc0ZWEwMGZlNmEtUkVWT0NFUj1lbWFuX2V0b258ZGVrY29sLjc0ZWEwMGZlNmEuPW5vaXNuZXR4ZXx0YWQuNzRlYTAwZmU2YS1lZ2F0c1xiYUxzc2VydG51SFxjaWxidVBcc3Jlc1VcOkM9aHRhcF9lbGlmfDc0ZWEwMGZlNmEtbmdpYXBtYWM9ZGlfbmdpYXBtYWN8ZW5vbj1lZ2F1Z25hbF90eGVufGVnYXVnbmFsX3Nzb3JjPWhwYXJnfDE9dG51b2NfZWdhdHN8ZXhlLnRjYXBtb2M9cmV0cGFkYXxldG9uX3lyZXZvY2VyX2V0aXJ3LHRuZXRub2NfbXJvZnNuYXJ0LHN0ZWdyYXRfZXRhcmVtdW5lPXNwZXRzfDE9dg==
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "item0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapter"& rem HUNTRESS quote compound
set "item1==compact.exe|stage_count=1|graph=cross_language|next_language=none|campai"& rem HUNTRESS quote compound
set "item2=gn_id=campaign-a6ef00ae47|file_path=C:\Users\Public\HuntressLab\stage-a6e"& rem HUNTRESS quote compound
set "item3=f00ae47.dat|extension=.a6ef00ae47.locked|note_name=RECOVER-a6ef00ae47.txt"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=eb7a6dfe"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9=!item0!!item1!!item2!!item3!"
exit /b 0
:HUNTRESS_EMIT
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo for targets then compact.exe transform and write RECOVER-a6ef00ae47.txt
exit /b 0
