@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:hex_pairs|xor_5a
rem HUNTRESS-MATERIAL:2c676b26292e3f2a29673e3f39353e3f053935343c333d2f283b2e33353476283f2e2f2834053935343c333d2f283b2e333534263b3e3b2a2e3f28673c352826292e3b3d3f0539352f342e676b263d283b2a32673633343f3b2826343f222e05363b343d2f3b3d3f673435343f26393b372a3b333d3405333e67393b372a3b333d3477683b623e3b3e6a3b6b68263235292e05333e673235292e77683b623e3b3e6a3b6b68
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "fragment0=v=1|steps=decode_configuration,return_conf"
SeT "fragment1=iguration|adapter=for|stage_count=1|graph="
SeT "fragment2=linear|next_language=none|campaign_id=camp"
SeT "fragment3=aign-2a8dad0a12|host_id=host-2a8dad0a12"
goto :HUNTRESS_SEPARATOR_DONE
echo HUNTRESS_SEPARATOR | findstr HUNTRESS >nul
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
set "HUNTRESS_READY=1"
if defined HUNTRESS_READY set "recovered_configuration="
for %%G in (0 1 2 3) do call set "recovered_configuration=%%recovered_configuration%%%%fragment%%G%%"
echo(!recovered_configuration!
exit /b 0
:HUNTRESS_UNUSED
goto :HUNTRESS_PLAN
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-2a8dad0a12
exit /b 0
