@echo off

setlocal EnableExtensions EnableDelayedExpansion

rem HUNTRESS-CODEC:decimal_bytes|add_7

rem HUNTRESS-MATERIAL:125.68.56.131.122.123.108.119.122.68.107.108.106.118.107.108.102.106.118.117.109.112.110.124.121.104.123.112.118.117.51.121.108.123.124.121.117.102.106.118.117.109.112.110.124.121.104.123.112.118.117.131.104.107.104.119.123.108.121.68.122.108.123.131.122.123.104.110.108.102.106.118.124.117.123.68.56.131.110.121.104.119.111.68.106.121.118.122.122.102.115.104.117.110.124.104.110.108.131.117.108.127.123.102.115.104.117.110.124.104.110.108.68.117.118.117.108.131.106.104.116.119.104.112.110.117.102.112.107.68.106.104.116.119.104.112.110.117.52.57.105.59.106.60.57.105.61.109.59.131.111.118.122.123.102.112.107.68.111.118.122.123.52.57.105.59.106.60.57.105.61.109.59

rem HUNTRESS-EXTENSION:cmd

if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT

if /i "%~1"=="--plan" goto :HUNTRESS_PLAN

exit /b 0

:HUNTRESS_INSPECT

set FrAg0=v=1^|steps=decode_configuration,return_config
set FrAg1=uration^|adapter=set^|stage_count=1^|graph=cros
set FrAg2=s_language^|next_language=none^|campaign_id=ca
set FrAg3=mpaign-2b4c52b6f4^|host_id=host-2b4c52b6f4

goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE

rem no neutral statements

goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "ReCoVeReD=!FrAg0!!FrAg1!!FrAg2!!FrAg3!"

echo(!ReCoVeReD!

exit /b 0

:HUNTRESS_PLAN

echo set HUNTRESS_HOST=host-2b4c52b6f4

exit /b 0

