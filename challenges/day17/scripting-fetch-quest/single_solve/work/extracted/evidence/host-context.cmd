@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:decimal_bytes|rotate_left

rem HUNTRESS-MATERIAL:236.122.98.248.230.232.202.224.230.122.200.202.198.222.200.202.190.198.222.220.204.210.206.234.228.194.232.210.222.220.88.228.202.232.234.228.220.190.198.222.220.204.210.206.234.228.194.232.210.222.220.248.194.200.194.224.232.202.228.122.204.222.228.248.230.232.194.206.202.190.198.222.234.220.232.122.98.248.206.228.194.224.208.122.198.228.222.230.230.190.216.194.220.206.234.194.206.202.248.220.202.240.232.190.216.194.220.206.234.194.206.202.122.220.222.220.202.248.198.194.218.224.194.210.206.220.190.210.200.122.198.194.218.224.194.210.206.220.90.102.98.114.202.106.194.102.202.98.98.248.208.222.230.232.190.210.200.122.208.222.230.232.90.102.98.114.202.106.194.102.202.98.98

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set "v_a0=v=1|steps=decode_configuration,return_config"
set "v_a1=uration|adapter=for|stage_count=1|graph=cros"
set "v_a2=s_language|next_language=none|campaign_id=ca"
set "v_a3=mpaign-319e5a3e11|host_id=host-319e5a3e11"

goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE

set "neutral_arithmetic=89e51950"

call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "cfg=%%v_a0%%%%v_a1%%%%v_a2%%%%v_a3%%"
exit /b 0
:HUNTRESS_EMIT

echo(!cfg!

exit /b 0

:HUNTRESS_PLAN

echo set HUNTRESS_HOST=host-319e5a3e11

exit /b 0

