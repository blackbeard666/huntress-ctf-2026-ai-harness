@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:split_fragments|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZzY1OTsuPwU2NTk7NnY+MykqOy45MgUqKDU5PykpJjs+OyouPyhnOTc+dD8iPyYpLjs9PwU5NS80LmdrJj0oOyoyZzw7NjY4OzkxBSg/LigjJjQ/Ii4FNjs0PS87PT9nNDU0PyY5OzcqOzM9NAUzPmc5OzcqOzM9NHc/aTg5PmI/Y2hjJjwzNj8FKjsuMmcZYAYPKT8oKQYKLzg2MzkGEi80Lig/KSkWOzgGKS47PT93P2k4OT5iP2NoY3Q+Oy4=
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=locate_local,dispatch_process|adapter=cm"& rem HUNTRESS quote compound
set "h1=d.exe|stage_count=1|graph=fallback_retry|next_lang"& rem HUNTRESS quote compound
set "h2=uage=none|campaign_id=campaign-e3bcd8e929|file_pat"& rem HUNTRESS quote compound
set "h3=h=C:\Users\Public\HuntressLab\stage-e3bcd8e929.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo cmd.exe dispatch C:\Users\Public\HuntressLab\stage-e3bcd8e929.dat
exit /b 0
