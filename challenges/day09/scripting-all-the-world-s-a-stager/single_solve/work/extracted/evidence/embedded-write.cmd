@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZz4/OTU+PwU/Nzg/Pj4/PnYtKDMuPwU8MzY/Jjs+OyouPyhnPyIqOzQ+dD8iPyYpLjs9PwU5NS80LmdrJj0oOyoyZzYzND87KCY0PyIuBTY7ND0vOz0/ZzQ1ND8mOTs3KjszPTQFMz5nOTs3KjszPTR3bm0/O21jOWpibCY8MzY/BSo7LjJnGWAGDyk/KCkGCi84NjM5BhIvNC4oPykpFjs4BikuOz0/d25tPzttYzlqYmx0Pjsu
rem HUNTRESS-EXTENSION:cmd
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set FrAg0=v=1^|steps=decode_embedded,write_file^|adapter=exp
set FrAg1=and.exe^|stage_count=1^|graph=linear^|next_language
set FrAg2==none^|campaign_id=campaign-47ea79c086^|file_path=
set FrAg3=C:\Users\Public\HuntressLab\stage-47ea79c086.dat
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=9a9d7c89"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "ReCoVeReD=%FrAg0%%FrAg1%%FrAg2%%FrAg3%"
exit /b 0
:HUNTRESS_EMIT
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo expand.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-47ea79c086.dat
exit /b 0
