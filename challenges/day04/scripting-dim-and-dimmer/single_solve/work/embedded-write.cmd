@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|rotate_left
rem HUNTRESS-MATERIAL:=guwIzlxIbMZCjmYmBnZapszCju54SswYau5KTO6crOk4as0YTs6gir5krs5qiLdGqH0oLM4+qM2SzM+GjsxkJMaiZGcmpF3OLtwgrtwGrHyS7L3OLtwgrtwGjvyc7N36pszCruzcLM2+iO8KzN+kLsycLN26BN4CTuz4Lmeozt6ebsvK7swobO+KDvycht0orO6krsx6RuyoDuwILM+Kjt0M7ryoLN5ujFyKjMyKTs2K7ryI7txKjsemDuyobO+ipH7
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=decode_embedded,write_file|adapter=cert"& rem HUNTRESS quote compound
set "h1=util.exe|stage_count=1|graph=linear|next_language"& rem HUNTRESS quote compound
set "h2==none|campaign_id=campaign-38314a2cdc|file_path=C"& rem HUNTRESS quote compound
set "h3=:\Users\Public\HuntressLab\stage-38314a2cdc.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=9cc43330"
set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo certutil.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-38314a2cdc.dat
exit /b 0
