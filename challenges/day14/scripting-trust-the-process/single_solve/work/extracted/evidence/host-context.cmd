@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:plain_fragments|rotate_left
rem HUNTRESS-MATERIAL:7Hpi+OboyuDmesjKxt7Iyr7G3tzM0s7q5MLo0t7cWOTK6Ork3L7G3tzM0s7q5MLo0t7c+MLIwuDoyuR6zN7k+Obows7Kvsbe6tzoemL4zuTC4NB65tLcztjK+NzK8Oi+2MLczurCzsp63N7cyvjGwtrgwtLO3L7SyHrGwtrgwtLO3FpkZMhwympizMZy+NDe5ui+0sh60N7m6FpkZMhwympizMZy
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
set "h0=v=1|steps=decode_configuration,return_conf"& rem HUNTRESS quote compound
set "h1=iguration|adapter=for|stage_count=1|graph="& rem HUNTRESS quote compound
set "h2=single|next_language=none|campaign_id=camp"& rem HUNTRESS quote compound
set "h3=aign-22d8e51fc9|host_id=host-22d8e51fc9"& rem HUNTRESS quote compound
goto :HUNTRESS_SEPARATOR_DONE
(ver >nul) || (rem HUNTRESS separator double pipe)
:HUNTRESS_SEPARATOR_DONE
set "neutral_arithmetic=218b5a83"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-22d8e51fc9
exit /b 0
