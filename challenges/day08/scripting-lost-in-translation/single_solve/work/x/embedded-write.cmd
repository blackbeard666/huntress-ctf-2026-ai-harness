@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:reversed_text|rotate_left

rem HUNTRESS-MATERIAL:=guwIzFxKDGyspGYoxmYapszCju54SswYau5KTO6crOk4as0YTs6gir5krs5qiLdGqH0oLM4+qM2SzM+ErMYIzmaghGbipF3OLtwgrtwGrHyS7L3OLtwgrtwGjvyc7N36pszCruzcLM2+iO8KzN+K7swq7M3Cjtvmbu3kbseQDuwk7M+ipH6cru3G7ryOLM6mjvywrMXIztwgDvy6RuyoDuwILM+Kjt0M7ryoLN5ujFyKjMyKTs2K7ryI7txKjsemDuyobO+ipH7

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

SeT "v_a0=v=1|steps=decode_embedded,write_file|adapter=expan"
SeT "v_a1=d.exe|stage_count=1|graph=cross_language|next_lang"
SeT "v_a2=uage=none|campaign_id=campaign-164056d0eb|file_pat"
SeT "v_a3=h=C:\Users\Public\HuntressLab\stage-164056d0eb.dat"

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_environment_probe=3dd697ec"

call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
exit /b 0
:HUNTRESS_EMIT

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo expand.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-164056d0eb.dat

exit /b 0

