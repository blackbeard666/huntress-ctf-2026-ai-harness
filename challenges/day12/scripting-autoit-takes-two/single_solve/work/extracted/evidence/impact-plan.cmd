@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZz80Lzc/KDsuPwUuOyg9Py4pdi4oOzQpPDUoNwU5NTQuPzQudi0oMy4/BSg/OTUsPygjBTQ1Lj8mOz47Ki4/KGc5MyoyPyh0PyI/JikuOz0/BTk1LzQuZ2smPSg7KjJnNjM0PzsoJjQ/Ii4FNjs0PS87PT9nNDU0PyY5OzcqOzM9NAUzPmc5OzcqOzM9NHdra2xoPzliaDs+JjwzNj8FKjsuMmcZYAYPKT8oKQYKLzg2MzkGEi80Lig/KSkWOzgGKS47PT93a2tsaD85Ymg7PnQ+Oy4mPyIuPzQpMzU0Z3Rra2xoPzliaDs+dDY1OTE/PiY0NS4/BTQ7Nz9nCB8ZFQwfCHdra2xoPzliaDs+dC4iLg==
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapt"
set "h1=er=cipher.exe|stage_count=1|graph=linear|next_language=none|campaign_id"
set "h2==campaign-1162ec82ad|file_path=C:\Users\Public\HuntressLab\stage-1162ec"
set "h3=82ad.dat|extension=.1162ec82ad.locked|note_name=RECOVER-1162ec82ad.txt"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_opaque_branch=842ce438"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "cfg=%h0%%h1%%h2%%h3%"
echo(!cfg!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo for targets then cipher.exe transform and write RECOVER-1162ec82ad.txt
exit /b 0
