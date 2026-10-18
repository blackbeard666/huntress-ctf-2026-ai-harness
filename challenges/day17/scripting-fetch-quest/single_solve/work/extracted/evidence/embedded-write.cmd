@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:split_fragments|xor_5a

rem HUNTRESS-MATERIAL:LGdrJikuPyopZz4/OTU+PwU/Nzg/Pj4/PnYtKDMuPwU8MzY/Jjs+OyouPyhnOT8oLi8uMzZ0PyI/JikuOz0/BTk1LzQuZ2smPSg7KjJnKTs3PwU2OzQ9Lzs9PyY0PyIuBTY7ND0vOz0/ZzQ1ND8mOTs3KjszPTQFMz5nOTs3KjszPTR3bTtqaWg+ODhvaCY8MzY/BSo7LjJnGWAGDyk/KCkGCi84NjM5BhIvNC4oPykpFjs4BikuOz0/d207amloPjg4b2h0Pjsu

rem HUNTRESS-EXTENSION:bat

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "v_a0=v=1|steps=decode_embedded,write_file|adapter=certut"& rem HUNTRESS quote compound
set "v_a1=il.exe|stage_count=1|graph=same_language|next_langu"& rem HUNTRESS quote compound
set "v_a2=age=none|campaign_id=campaign-7a032dbb52|file_path="& rem HUNTRESS quote compound
set "v_a3=C:\Users\Public\HuntressLab\stage-7a032dbb52.dat"& rem HUNTRESS quote compound

goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE

set "neutral_arithmetic=4eae396e"

goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%v_a%%G%%"

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo certutil.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-7a032dbb52.dat

exit /b 0

