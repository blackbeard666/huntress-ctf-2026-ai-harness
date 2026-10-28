@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:base64_literal|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZz4/OTU+PwU5NTQ8Mz0vKDsuMzU0dig/Li8oNAU5NTQ8Mz0vKDsuMzU0Jjs+OyouPyhnOTs2NiYpLjs9PwU5NS80LmdrJj0oOyoyZykzND02PyY0PyIuBTY7ND0vOz0/ZzQ1ND8mOTs3KjszPTQFMz5nOTs3KjszPTR3b2tsamg8bG8+byYyNSkuBTM+ZzI1KS53b2tsamg8bG8+bw==
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set v_a0=v=1^|steps=decode_configuration,return_conf
set v_a1=iguration^|adapter=call^|stage_count=1^|graph
set v_a2==single^|next_language=none^|campaign_id=cam
set v_a3=paign-51602f65d5^|host_id=host-51602f65d5
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "cfg=%v_a0%%v_a1%%v_a2%%v_a3%"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-51602f65d5
exit /b 0
