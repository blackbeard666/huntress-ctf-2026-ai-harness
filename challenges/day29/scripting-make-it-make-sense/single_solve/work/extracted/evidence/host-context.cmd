@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|xor_5a
rem HUNTRESS-MATERIAL:LGdrJikuPyopZz4/OTU+PwU5NTQ8Mz0vKDsuMzU0dig/Li8oNAU5NTQ8Mz0vKDsuMzU0Jjs+OyouPyhnKT8uJikuOz0/BTk1LzQuZ2smPSg7KjJnKTs3PwU2OzQ9Lzs9PyY0PyIuBTY7ND0vOz0/ZzQ1ND8mOTs3KjszPTQFMz5nOTs3KjszPTR3Pm47ams5aG5sPiYyNSkuBTM+ZzI1KS53Pm47ams5aG5sPg==
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "item0=v=1|steps=decode_configuration,return_confi"
SeT "item1=guration|adapter=set|stage_count=1|graph=sa"
SeT "item2=me_language|next_language=none|campaign_id="
SeT "item3=campaign-d4a01c246d|host_id=host-d4a01c246d"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=74c7d057"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-d4a01c246d
exit /b 0
