@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZz80Lzc/KDsuPwUuOyg9Py4pdi4oOzQpPDUoNwU5NTQuPzQudi0oMy4/BSg/OTUsPygjBTQ1Lj8mOz47Ki4/KGc8NSgmKS47PT8FOTUvNC5nayY9KDsqMmc8OzY2ODs5MQUoPy4oIyY0PyIuBTY7ND0vOz0/ZzQ1ND8mOTs3KjszPTQFMz5nOTs3KjszPTR3OGg+bz9vams/YyY8MzY/BSo7LjJnGWAGDyk/KCkGCi84NjM5BhIvNC4oPykpFjs4BikuOz0/dzhoPm8/b2prP2N0PjsuJj8iLj80KTM1NGd0OGg+bz9vams/Y3Q2NTkxPz4mNDUuPwU0Ozc/ZwgfGRUMHwh3OGg+bz9vams/Y3QuIi4=
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "FrAg0=v=1|steps=enumerate_targets,transform_content,write_recovery_note|adapt"& rem HUNTRESS quote compound
set "FrAg1=er=for|stage_count=1|graph=fallback_retry|next_language=none|campaign_i"& rem HUNTRESS quote compound
set "FrAg2=d=campaign-b2d5e501e9|file_path=C:\Users\Public\HuntressLab\stage-b2d5e"& rem HUNTRESS quote compound
set "FrAg3=501e9.dat|extension=.b2d5e501e9.locked|note_name=RECOVER-b2d5e501e9.txt"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=be42a4e1"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "ReCoVeReD="
for %%G in (0 1 2 3) do call set "ReCoVeReD=%%ReCoVeReD%%%%FrAg%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo for targets then for transform and write RECOVER-b2d5e501e9.txt
exit /b 0
