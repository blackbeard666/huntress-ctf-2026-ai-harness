@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:decimal_bytes|identity
rem HUNTRESS-MATERIAL:118.61.49.124.115.116.101.112.115.61.100.101.99.111.100.101.95.99.111.110.102.105.103.117.114.97.116.105.111.110.44.114.101.116.117.114.110.95.99.111.110.102.105.103.117.114.97.116.105.111.110.124.97.100.97.112.116.101.114.61.99.97.108.108.124.115.116.97.103.101.95.99.111.117.110.116.61.49.124.103.114.97.112.104.61.115.105.110.103.108.101.124.110.101.120.116.95.108.97.110.103.117.97.103.101.61.110.111.110.101.124.99.97.109.112.97.105.103.110.95.105.100.61.99.97.109.112.97.105.103.110.45.101.54.101.54.56.99.98.55.57.100.124.104.111.115.116.95.105.100.61.104.111.115.116.45.101.54.101.54.56.99.98.55.57.100
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "item0=v=1|steps=decode_configuration,return_conf"
SeT "item1=iguration|adapter=call|stage_count=1|graph"
SeT "item2==single|next_language=none|campaign_id=cam"
SeT "item3=paign-e6e68cb79d|host_id=host-e6e68cb79d"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "item9="
for %%G in (0 1 2 3) do call set "item9=%%item9%%%%item%%G%%"
echo(!item9!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-e6e68cb79d
exit /b 0
