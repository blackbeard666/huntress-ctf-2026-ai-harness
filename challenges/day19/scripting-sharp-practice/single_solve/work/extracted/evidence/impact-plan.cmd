@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:plain_fragments|reverse

rem HUNTRESS-MATERIAL:dHh0LjYyYTEwZWNkZWUtUkVWT0NFUj1lbWFuX2V0b258ZGVrY29sLjYyYTEwZWNkZWUuPW5vaXNuZXR4ZXx0YWQuNjJhMTBlY2RlZS1lZ2F0c1xiYUxzc2VydG51SFxjaWxidVBcc3Jlc1VcOkM9aHRhcF9lbGlmfDYyYTEwZWNkZWUtbmdpYXBtYWM9ZGlfbmdpYXBtYWN8ZW5vbj1lZ2F1Z25hbF90eGVufHlydGVyX2tjYWJsbGFmPWhwYXJnfDE9dG51b2NfZWdhdHN8ZXhlLnRjYXBtb2M9cmV0cGFkYXxldG9uX3lyZXZvY2VyX2V0aXJ3LHRuZXRub2NfbXJvZnNuYXJ0LHN0ZWdyYXRfZXRhcmVtdW5lPXNwZXRzfDE9dg==

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set item0=v=1^|steps=enumerate_targets,transform_content,write_recovery_note^|adapter
set item1==compact.exe^|stage_count=1^|graph=fallback_retry^|next_language=none^|campai
set item2=gn_id=campaign-eedce01a26^|file_path=C:\Users\Public\HuntressLab\stage-eed
set item3=ce01a26.dat^|extension=.eedce01a26.locked^|note_name=RECOVER-eedce01a26.txt

goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE

rem no neutral statements

goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "item9=!item0!!item1!!item2!!item3!"

echo(!item9!

exit /b 0

:HUNTRESS_PLAN

echo for targets then compact.exe transform and write RECOVER-eedce01a26.txt

exit /b 0

