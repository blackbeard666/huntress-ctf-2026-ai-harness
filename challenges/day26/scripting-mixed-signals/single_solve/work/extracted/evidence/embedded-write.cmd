@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|reverse
rem HUNTRESS-MATERIAL:7461642e393536623163323337322d65676174735c62614c73736572746e75485c63696c6275505c73726573555c3a433d687461705f656c69667c393536623163323337322d6e676961706d61633d64695f6e676961706d61637c656e6f6e3d65676175676e616c5f7478656e7c65676175676e616c5f73736f72633d68706172677c313d746e756f635f65676174737c6578652e6c697475747265633d726574706164617c656c69665f65746972772c6465646465626d655f65646f6365643d73706574737c313d76
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "fragment0=v=1|steps=decode_embedded,write_file|adapter=certut"& rem HUNTRESS quote compound
set "fragment1=il.exe|stage_count=1|graph=cross_language|next_lang"& rem HUNTRESS quote compound
set "fragment2=uage=none|campaign_id=campaign-2732c1b659|file_path"& rem HUNTRESS quote compound
set "fragment3==C:\Users\Public\HuntressLab\stage-2732c1b659.dat"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=78d2e07b"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_PLAN
echo certutil.exe decode embedded bytes to C:\Users\Public\HuntressLab\stage-2732c1b659.dat
exit /b 0
