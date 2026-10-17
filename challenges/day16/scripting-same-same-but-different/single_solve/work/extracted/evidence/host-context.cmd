@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesjKxt7Iyr7G3tzM0s7q5MLo0t7cWOTK6Ork3L7G3tzM0s7q5MLo0t7c+MLIwuDoyuR6zN7k+Obows7Kvsbe6tzoemL4zuTC4NB65tLcztjK+NzK8Oi+2MLczurCzsp63N7cyvjGwtrgwtLO3L7SyHrGwtrgwtLO3FrEZGDMxMrEyshy+NDe5ui+0sh60N7m6FrEZGDMxMrEyshy
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "FrAg0=v=1|steps=decode_configuration,return_conf"
SeT "FrAg1=iguration|adapter=for|stage_count=1|graph="
SeT "FrAg2=single|next_language=none|campaign_id=camp"
SeT "FrAg3=aign-b20fbebed9|host_id=host-b20fbebed9"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=1e7d8363"
call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "ReCoVeReD="
for %%G in (0 1 2 3) do call set "ReCoVeReD=%%ReCoVeReD%%%%FrAg%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-b20fbebed9
exit /b 0
